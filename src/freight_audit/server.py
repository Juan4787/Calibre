"""Loopback-only UI adapter. The core has no dependency on this server."""

import logging
import secrets
import shutil
import tempfile
import threading
from functools import wraps
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import ENGINE_VERSION
from .canonical import canonical, load_json
from .document_control import documentary_control
from .engine import audit, matching_preflight
from .fixtures import generate, run_demo
from .importing import MAX_FILE_BYTES, ImportMapping, import_data, source_filename
from .models import Agreement, Dataset, Decision
from .reporting import bundle_bytes, html_report, workbook_bytes
from .storage import Store, engine_artifact_hash
from .workspaces import Workspaces

logger = logging.getLogger("freight_audit")


def create_app(db_path: Path) -> FastAPI:
    app = FastAPI(title="Freight Audit local", docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"])
    store = Store(db_path)
    workspaces = Workspaces(store)
    token = secrets.token_urlsafe(32)
    static = Path(__file__).parent / "static"
    job_lock = threading.Lock()

    def limited(function):
        @wraps(function)
        def execute(*args, **kwargs):
            with job_lock:
                return function(*args, **kwargs)

        return execute

    async def heavy(function, *args):
        return await run_in_threadpool(limited(function), *args)

    def selected(request: Request) -> Store:
        return workspaces.select(
            request.headers.get("x-freight-workspace") or request.query_params.get("workspace", "main")
        )

    def resolve_dataset(value: dict, store: Store) -> Dataset:
        if not isinstance(value, dict):
            raise ValueError("Seleccionar los datos y acuerdos de esta auditoría.")
        if "imports" not in value:
            return Dataset.model_validate(value)
        allowed = set(Dataset.model_fields) - {"shipments", "charges", "mappings", "issues"}
        if set(value) - allowed - {"imports"}:
            raise ValueError(
                "El lote debe usar las importaciones conservadas; no se admiten registros sustituidos desde el navegador."
            )
        references = value["imports"]
        if not isinstance(references, dict) or set(references) != {"shipments", "charges"}:
            raise ValueError("Validar un archivo de operaciones y otro de cargos antes de continuar.")
        composed = {key: data for key, data in value.items() if key != "imports"}
        composed.update(mappings=[], issues=[], documents=dict(value.get("documents", {})))
        for role in ("shipments", "charges"):
            identifier = references[role]
            if not isinstance(identifier, str):
                raise ValueError("La referencia de importación no es válida; volver a validar el archivo.")
            imported = store.load_import(identifier)
            if imported["mapping"]["entity"] != role:
                raise ValueError(
                    "La importación corresponde a otro tipo de archivo; revisar operaciones y cargos."
                )
            composed[role] = imported["records"]
            composed["mappings"].append(imported["mapping"])
            composed["issues"].extend(imported["issues"])
            composed["documents"][imported["document"]] = imported["filename"]
        return Dataset.model_validate(composed)

    def compact_import(imported: dict, identifier: str) -> dict:
        result = {key: imported[key] for key in ("document", "filename", "sheet", "sheets", "accepted")}
        result.update(
            import_id=identifier,
            rejected=imported["rejected"][:50],
            rejected_count=len(imported["rejected"]),
            issues=imported["issues"][:50],
            issue_count=len(imported["issues"]),
            warning_count=sum(i["category"] == "warning" for i in imported["issues"]),
            mapping={key: imported["mapping"][key] for key in ("id", "version", "entity")},
            headers=[h[:500] for h in imported["headers"][:20]],
            preview=[
                {
                    "row": row["row"],
                    "values": {
                        h[:500]: str(row["values"].get(h, ""))[:500] for h in imported["headers"][:20]
                    },
                }
                for row in imported["preview"]
            ],
            preview_limited=True,
        )
        conversions = []
        for record in imported["records"][:10]:
            for field, ref in list(record.get("provenance", {}).items())[:20]:
                value = (
                    record.get("attributes", {}).get(field.removeprefix("attributes."))
                    if field.startswith("attributes.")
                    else record.get(field)
                )
                if isinstance(value, dict):
                    value = str(value.get("value", "")) + (" " + value["unit"] if value.get("unit") else "")
                conversions.append(
                    {
                        "row": ref["row"],
                        "field": field,
                        "raw": ref["raw"][:500],
                        "transform": ref["transform"][:500],
                        "value": str(value)[:500],
                    }
                )
        result["conversion_preview"] = conversions
        return result

    def perform_import(data, filename, config, store, compact):
        result = import_data(data, filename, config)
        store.put_source(data)
        store.save_config("mapping", f"{config.id}@{config.version}", config.model_dump(mode="json"))
        return compact_import(result, store.save_import(result)) if compact else result

    def perform_audit(body, store, preview=False):
        dataset = resolve_dataset(body, store)
        if preview:
            return preflight_result(dataset)
        return {"run_id": store.save(dataset, audit(dataset))}

    def preflight_result(dataset):
        result = matching_preflight(dataset)

        def bounded(detail):
            if isinstance(detail, dict):
                output = {}
                for key, value in detail.items():
                    output[key] = value[:50] if isinstance(value, list) else bounded(value)
                    if isinstance(value, list) and len(value) > 50:
                        output[key + "_count"] = len(value)
                return output
            return detail

        result["issues"] = [bounded(e) for e in result["issues"]]
        result["conflicts"] = [bounded(e) for e in result["conflicts"]]
        ids = {
            sid
            for issue in result["issues"]
            for field in ("affected_shipment_ids", "key_candidate_ids", "shipment_ids")
            for sid in issue.get(field, [])
        }
        cids = {issue["charge_id"] for issue in result["issues"]}
        result["references"] = {
            "shipments": [{"id": s.id, "reference": s.reference} for s in dataset.shipments if s.id in ids],
            "charges": [{"id": c.id, "reference": c.reference} for c in dataset.charges if c.id in cids],
        }
        result["document_control"] = documentary_control(dataset)
        return result

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            expected_origin = f"{request.url.scheme}://{request.headers.get('host', '')}"
            if (origin and origin != expected_origin) or not secrets.compare_digest(
                request.headers.get("x-freight-local", ""), token
            ):
                return JSONResponse(
                    {
                        "error": "La sesión local venció o la solicitud proviene de otra página. Recargar Freight Audit e intentar de nuevo."
                    },
                    status_code=403,
                )
            total = 0
            chunks = []
            async for chunk in request.stream():
                total += len(chunk)
                if total > 32 * 1024 * 1024:
                    return JSONResponse(
                        {
                            "error": "La solicitud supera 32 MB. Dividir el archivo o usar la herramienta de línea de comandos."
                        },
                        status_code=413,
                    )
                chunks.append(chunk)
            request._body = b"".join(chunks)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(ValueError)
    async def value_error(request: Request, exc: ValueError):
        if isinstance(exc, ValidationError):
            details = [
                {"field": ".".join(map(str, e["loc"])), "message": e["msg"].removeprefix("Value error, ")}
                for e in exc.errors(include_input=False)[:20]
            ]
            return JSONResponse(
                {
                    "error": "Hay campos inválidos en los datos o la configuración. Corregir los campos indicados y volver a validar.",
                    "details": details,
                },
                status_code=422,
            )
        return JSONResponse({"error": str(exc)}, status_code=422)

    @app.exception_handler(RequestValidationError)
    async def request_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            {"error": "Faltan archivos o campos obligatorios. Completar el formulario y volver a intentar."},
            status_code=422,
        )

    @app.exception_handler(KeyError)
    async def missing_error(request: Request, exc: KeyError):
        return JSONResponse(
            {
                "error": "No se encontró la auditoría o el dato solicitado. Volver a la lista y seleccionar un registro existente."
            },
            status_code=404,
        )

    @app.exception_handler(Exception)
    async def internal_error(request: Request, exc: Exception):
        incident = secrets.token_hex(4)
        logger.exception("Incident %s at %s", incident, request.url.path, exc_info=exc)
        return JSONResponse(
            {
                "error": "No se pudo completar la operación por un problema del programa. Los resultados guardados se conservan. Revisar el registro local antes de reintentar."
            },
            status_code=500,
        )

    @app.get("/")
    def index():
        return FileResponse(static / "index.html")

    @app.get("/api/session")
    def session():
        return {"token": token, "mode": "local", "network_required": False}

    @app.get("/api/health")
    def health():
        with store.connect() as connection:
            schema = connection.execute("PRAGMA user_version").fetchone()[0]
        return {
            "engine_version": ENGINE_VERSION,
            "artifact_hash": engine_artifact_hash(),
            "database_schema": schema,
        }

    @app.get("/api/runs")
    def runs(request: Request):
        return selected(request).list_runs()

    @app.get("/api/runs/{run_id}")
    @limited
    def get_run(run_id: str, request: Request):
        return selected(request).load(run_id)

    @app.get("/api/configs")
    def configs(request: Request):
        return selected(request).configs()

    @app.get("/api/workspaces")
    def workspace_list():
        return workspaces.list()

    @app.get("/api/workspace/status")
    def workspace_status(request: Request):
        store = selected(request)
        receipts = [c["payload"] for c in store.configs() if c["kind"] == "backup_receipt"]
        return {"identity": store.identity(), "last_backup": receipts[0] if receipts else None}

    @app.post("/api/workspaces")
    async def workspace_create(request: Request):
        body = load_json(await request.body())
        if not isinstance(body, dict) or set(body) != {"name"}:
            raise ValueError("Indicar solamente el nombre del nuevo cliente o espacio local.")
        return await run_in_threadpool(workspaces.create, body["name"])

    @app.get("/api/workspace/backup")
    @limited
    def workspace_backup(request: Request):
        backup = workspaces.backup(selected(request))
        return FileResponse(
            backup,
            media_type="application/octet-stream",
            filename="calibre-backup.db",
            background=BackgroundTask(shutil.rmtree, backup.parent),
        )

    @app.post("/api/workspaces/restore")
    async def workspace_restore(file: Annotated[UploadFile, File()], name: Annotated[str, Form()]):
        data = await file.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise ValueError(
                "El respaldo supera 25 MB. Restaurarlo con la herramienta local de línea de comandos para conservar su contenido completo."
            )
        return await heavy(workspaces.create, name, data)

    @app.post("/api/configs/{kind}")
    async def save_config(kind: str, request: Request):
        store = selected(request)
        value = load_json(await request.body())
        if kind == "mapping":
            model = ImportMapping.model_validate(value)
            name = f"{model.id}@{model.version}"
        elif kind == "agreement":
            agreement_model = Agreement.model_validate(value)
            return {
                "hash": store.save_config(kind, agreement_model.name, agreement_model.model_dump(mode="json"))
            }
        else:
            raise ValueError("Seleccionar acuerdo o mapping.")
        return {"hash": store.save_config(kind, name, model.model_dump(mode="json"))}

    @app.post("/api/import")
    async def preview(
        request: Request,
        file: Annotated[UploadFile, File()],
        mapping: Annotated[str, Form()],
        compact: Annotated[bool, Form()] = False,
    ):
        store = selected(request)
        data = await file.read(MAX_FILE_BYTES + 1)
        config = ImportMapping.model_validate(load_json(mapping))
        return await heavy(perform_import, data, file.filename or "archivo", config, store, compact)

    @app.get("/api/imports/{identifier}/issues")
    @limited
    def import_issues(identifier: str, request: Request, page: int = 0):
        store = selected(request)
        if page < 0:
            raise ValueError("Seleccionar una página de incidencias válida.")
        imported = store.load_import(identifier)
        total = len(imported["issues"])
        if page and page * 50 >= total:
            raise ValueError("La página de incidencias no existe; volver a la primera página.")
        return {"issues": imported["issues"][page * 50 : (page + 1) * 50], "page": page, "total": total}

    @app.post("/api/evidence-file")
    async def evidence_file(request: Request, file: Annotated[UploadFile, File()]):
        store = selected(request)
        data = await file.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("El adjunto supera 25 MB; aportar un archivo más pequeño.")
        return {
            "document_hash": store.put_source(data),
            "filename": source_filename(file.filename or "adjunto"),
        }

    @app.post("/api/audit/preflight")
    async def preflight(request: Request):
        return await heavy(perform_audit, load_json(await request.body()), selected(request), True)

    @app.post("/api/audit")
    async def run_audit(request: Request):
        store = selected(request)
        return await heavy(perform_audit, load_json(await request.body()), store)

    @app.post("/api/demo")
    @limited
    def demo(request: Request):
        store = selected(request)
        fixture_path = Path(__file__).resolve().parents[2] / "fixtures"
        if fixture_path.exists():
            return run_demo(store, fixture_path)
        with tempfile.TemporaryDirectory() as directory:
            generate(Path(directory))
            return run_demo(store, Path(directory))

    @app.post("/api/runs/{run_id}/replay")
    @limited
    def replay(run_id: str, request: Request):
        return selected(request).replay(run_id)

    @app.post("/api/runs/{run_id}/decisions")
    async def decision(run_id: str, request: Request):
        return selected(request).add_decision(
            run_id, Decision.model_validate(load_json(await request.body()))
        )

    @app.get("/api/runs/{run_id}/export/{format}")
    @limited
    def export(run_id: str, format: str, request: Request):
        store = selected(request)
        run = store.load(run_id)
        if format == "canonical":
            return Response(
                canonical(run),
                media_type="application/json",
                headers={"Content-Disposition": 'attachment; filename="audit.json"'},
            )
        if format == "xlsx":
            return Response(
                workbook_bytes(run),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": 'attachment; filename="auditoria.xlsx"'},
            )
        if format == "html":
            return Response(
                html_report(run),
                media_type="text/html",
                headers={"Content-Disposition": 'attachment; filename="reporte.html"'},
            )
        if format == "zip":
            return Response(
                bundle_bytes(store, run_id),
                media_type="application/zip",
                headers={"Content-Disposition": 'attachment; filename="auditoria.zip"'},
            )
        raise HTTPException(404, "Formato no disponible.")

    @app.get("/api/sources/{source_hash}")
    @limited
    def original(source_hash: str, request: Request, filename: str = "documento-original"):
        data = selected(request).source(source_hash)
        return Response(
            data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename*=UTF-8''" + quote(source_filename(filename))
            },
        )

    app.mount("/static", StaticFiles(directory=static), name="static")
    return app
