"""Loopback-only UI adapter. The core has no dependency on this server."""

import logging
import secrets
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .canonical import load_json
from .engine import audit
from .fixtures import generate, run_demo
from .importing import MAX_FILE_BYTES, ImportMapping, import_data
from .models import Agreement, Dataset, Decision
from .reporting import bundle_bytes, html_report, workbook_bytes
from .storage import Store

logger = logging.getLogger("freight_audit")


def create_app(db_path: Path) -> FastAPI:
    app = FastAPI(title="Freight Audit local", docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"])
    store = Store(db_path)
    token = secrets.token_urlsafe(32)
    static = Path(__file__).parent / "static"

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

    @app.get("/api/runs")
    def runs():
        return store.list_runs()

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str):
        return store.load(run_id)

    @app.get("/api/configs")
    def configs():
        return store.configs()

    @app.post("/api/configs/{kind}")
    async def save_config(kind: str, request: Request):
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
    async def preview(file: Annotated[UploadFile, File()], mapping: Annotated[str, Form()]):
        data = await file.read(MAX_FILE_BYTES + 1)
        config = ImportMapping.model_validate(load_json(mapping))
        result = import_data(data, file.filename or "archivo", config)
        store.put_source(data)
        store.save_config("mapping", f"{config.id}@{config.version}", config.model_dump(mode="json"))
        return result

    @app.post("/api/evidence-file")
    async def evidence_file(file: Annotated[UploadFile, File()]):
        data = await file.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("El adjunto supera 25 MB; aportar un archivo más pequeño.")
        return {"document_hash": store.put_source(data), "filename": Path(file.filename or "adjunto").name}

    @app.post("/api/audit")
    async def run_audit(request: Request):
        dataset = Dataset.model_validate(load_json(await request.body()))
        result = audit(dataset)
        return {"run_id": store.save(dataset, result)}

    @app.post("/api/demo")
    def demo():
        fixture_path = Path(__file__).resolve().parents[2] / "fixtures"
        if fixture_path.exists():
            return run_demo(store, fixture_path)
        with tempfile.TemporaryDirectory() as directory:
            generate(Path(directory))
            return run_demo(store, Path(directory))

    @app.post("/api/runs/{run_id}/replay")
    def replay(run_id: str):
        return store.replay(run_id)

    @app.post("/api/runs/{run_id}/decisions")
    async def decision(run_id: str, request: Request):
        return store.add_decision(run_id, Decision.model_validate(load_json(await request.body())))

    @app.get("/api/runs/{run_id}/export/{format}")
    def export(run_id: str, format: str):
        run = store.load(run_id)
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

    app.mount("/static", StaticFiles(directory=static), name="static")
    return app
