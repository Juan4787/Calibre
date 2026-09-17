"""Exact-value workbooks and self-contained printable HTML, derived from traces."""

import html
import io
import zipfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .canonical import bytes_hash, canonical, digest, load_json
from .models import Dataset
from .storage import IntegrityError, Store

STATUS_LABELS = {
    "PASS": "Coincide",
    "FAIL": "Discrepancia",
    "REVIEW": "Revisión humana",
    "UNDETERMINABLE": "Indeterminado",
}


MAX_XLSX_ROWS = 1_048_576
MAX_XLSX_CELL_CHARS = 32_767


class ReportLimitError(ValueError):
    """Excel must not silently truncate authoritative data."""


def describe_trace(trace: dict) -> str:
    """Presentation comes exclusively from executed operands, never recomputed pricing."""
    operation = trace["op"]
    details = trace.get("details", {})
    output = trace.get("output")
    operands = [str(child.get("output", "?")) for child in trace.get("children", [])]
    symbols = {"add": " + ", "sub": " - ", "mul": " × ", "div": " ÷ "}
    if operation in symbols:
        return symbols[operation].join(operands) + " = " + str(output)
    if operation == "attr":
        return f"{details.get('field')}: {output}"
    if operation == "sum":
        return f"Suma de {details.get('field')} en {len(details.get('sources', []))} operaciones = {output}"
    if operation in {"lookup", "band"}:
        return f"Tabla {details.get('table')}, selección {canonical(details.get('selected', {}))}: {output}"
    if operation == "comparison":
        return f"Facturado {details.get('actual')} - esperado {details.get('expected')} = {output}; tolerancia {details.get('tolerance')}"
    if operation in {"round", "currency_round"}:
        return f"Redondeo a {details.get('scale')} decimales, {details.get('rounding')}: {output}"
    if operation == "version":
        return f"Versión {output}; fecha relevante: {details.get('date_field')}"
    if operation == "evidence":
        return f"Respaldos encontrados: {', '.join(details.get('found', [])) or 'ninguno'}; faltantes: {', '.join(details.get('missing', [])) or 'ninguno'}"
    if details.get("reason"):
        return str(details["reason"])
    return f"{operation}: {output if output is not None else canonical(details)}"


def trace_rows(trace, path=""):
    path = f"{path}/{trace['op']}"
    yield [path, describe_trace(trace), trace.get("output"), canonical(trace.get("details", {}))]
    for child in trace.get("children", []):
        yield from trace_rows(child, path)


def workbook_bytes(run: dict) -> bytes:
    workbook = Workbook()
    workbook.remove(workbook.active)
    summary = run["result"]["summary"]

    def sheet(name, headings, rows):
        ws = workbook.create_sheet(name)
        ws.append(headings)
        for row in rows:
            values = [
                "" if value is None else ("Sí" if value else "No") if isinstance(value, bool) else str(value)
                for value in row
            ]
            if ws.max_row >= MAX_XLSX_ROWS or any(len(value) > MAX_XLSX_CELL_CHARS for value in values):
                workbook.close()
                raise ReportLimitError(
                    "El detalle supera los límites de filas o de texto por celda de Excel. Exportar el paquete completo: audit.json conserva todos los datos sin truncar."
                )
            ws.append(values)
        # All imported text and exact decimal money are explicit strings, never formulas.
        for row in ws:
            for cell in row:
                if cell.value is not None:
                    cell.data_type = "s"
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        for cell in ws[1]:
            cell.fill = PatternFill("solid", fgColor="183E39")
            cell.font = Font(color="FFFFFF", bold=True)
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for col in range(1, len(headings) + 1):
            ws.column_dimensions[get_column_letter(col)].width = min(58, max(18, len(headings[col - 1]) + 5))
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        return ws

    sheet(
        "Resumen",
        ["Moneda", "Métrica", "Valor exacto"],
        [
            [currency, key, value]
            for currency, bucket in summary["currencies"].items()
            for key, value in bucket.items()
        ]
        + [["", key, value] for key, value in summary["counts"].items()]
        + [
            ["", "Importación completa", summary["import_complete"]],
            ["", "Definición", summary["economic_definition"]],
            [
                "",
                "Nota",
                "Importes guardados como texto decimal exacto para evitar pérdida de precisión en Excel.",
            ],
        ],
    )
    findings = run["result"]["findings"]
    sheet(
        "Hallazgos",
        [
            "Hallazgo",
            "Operaciones",
            "Cargos",
            "Concepto",
            "Moneda",
            "Facturado",
            "Esperado",
            "Diferencia calculada",
            "Diferencia confirmada",
            "Estado",
            "Acuerdo",
            "Versión",
            "Regla",
            "Motivos",
            "Evidencia",
            "Faltante",
        ],
        [
            [
                f["id"],
                ", ".join(f["shipment_ids"]),
                ", ".join(f["charge_ids"]),
                f["concept"],
                f["currency"],
                f["actual"],
                f["expected"],
                f["difference"],
                f["confirmed_difference"],
                STATUS_LABELS[f["status"]],
                f["agreement"],
                f["version"],
                f["rule"],
                "\n".join(f["reasons"]),
                ", ".join(f["evidence_ids"]),
                ", ".join(f["missing_evidence"]),
            ]
            for f in findings
        ],
    )
    sheet(
        "Cálculos",
        ["Hallazgo", "Paso", "Explicación del cálculo", "Resultado", "Datos de ejecución"],
        [[f["id"], *row] for f in findings for trace in f["trace"] for row in trace_rows(trace)],
    )
    sheet(
        "Problemas de datos",
        ["Tipo", "Documento", "Fila", "Campo", "Valor original", "Problema"],
        [
            [i["category"], i["document"], i["row"], i["field"], i["raw"], i["message"]]
            for i in run["result"]["issues"]
        ],
    )
    sheet(
        "Evidencia",
        ["Referencia", "Tipo", "Operaciones", "Cargos", "Documento conservado", "Descripción"],
        [
            [
                e["id"],
                e["kind"],
                ", ".join(e["shipment_ids"]),
                ", ".join(e["charge_ids"]),
                e["document_hash"],
                e["note"],
            ]
            for e in run["snapshot"]["evidence"]
        ],
    )
    sheet(
        "Decisiones",
        [
            "Secuencia",
            "Hallazgo",
            "Decisión",
            "Persona",
            "Motivo",
            "Fecha",
            "Evidencia",
            "Ya conocida",
            "Minutos",
            "Hash",
        ],
        [
            [
                d["seq"],
                d["payload"]["finding_id"],
                d["payload"]["action"],
                d["payload"]["actor"],
                d["payload"]["note"],
                d["created_at"],
                ", ".join(d["payload"]["evidence_ids"]),
                d["payload"]["known_to_client"],
                d["payload"]["review_minutes"],
                d["hash"],
            ]
            for d in run["decisions"]
        ],
    )
    sheet(
        "Origen de datos",
        [
            "Registro",
            "Campo",
            "Archivo",
            "Hoja",
            "Fila",
            "Columna",
            "Valor original",
            "Transformación",
            "Hash del archivo",
        ],
        [
            [
                record["id"],
                field,
                ref["filename"],
                ref["sheet"],
                ref["row"],
                ref["column"],
                ref["raw"],
                ref["transform"],
                ref["document"],
            ]
            for entity in ("shipments", "charges")
            for record in run["snapshot"][entity]
            for field, ref in record["provenance"].items()
        ],
    )
    sheet(
        "Metadata",
        ["Dato", "Valor"],
        [[key, value] for key, value in run.items() if key not in {"result", "snapshot", "decisions"}]
        + [
            ["Motor", run["result"]["engine_version"]],
            ["Datos normalizados", run["result"]["semantic_hash"]],
        ],
    )
    data = io.BytesIO()
    workbook.save(data)
    workbook.close()
    return data.getvalue()


def html_report(run: dict) -> str:
    def escape(value):
        return html.escape(str(value if value is not None else "—"))

    summary = run["result"]["summary"]
    totals = "".join(
        f"<tr><td>{escape(currency)}</td><td>{escape(bucket['actual'])}</td><td>{escape(bucket['determinable'])}</td><td>{escape(bucket['confirmed_overcharge'])}</td><td>{escape(bucket['confirmed_undercharge'])}</td><td>{escape(bucket['review'])}</td><td>{escape(bucket['undeterminable'])}</td></tr>"
        for currency, bucket in summary["currencies"].items()
    )
    rows = "".join(
        f"<tr><td>{escape(', '.join(f['shipment_ids']))}</td><td>{escape(f['concept'])}</td><td>{escape(STATUS_LABELS[f['status']])}</td><td>{escape(f['currency'])} {escape(f['actual'])}</td><td>{escape(f['expected'])}</td><td>{escape(f['confirmed_difference'])}</td><td>{escape(' '.join(f['reasons']))}</td></tr>"
        for f in run["result"]["findings"]
    )
    warnings = (
        "<p class='warning'>IMPORTACIÓN INCOMPLETA: hay filas rechazadas. Los totales sólo incluyen cargos aceptados. Corregir los datos antes de concluir.</p>"
        if not summary["import_complete"]
        else ""
    )
    return f"""<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Freight Audit · Informe</title><style>body{{font:14px system-ui;color:#18312e;margin:40px;line-height:1.5}}h1{{font-size:32px}}table{{border-collapse:collapse;width:100%;margin:24px 0;font-size:12px}}th,td{{border-bottom:1px solid #cdd9d4;padding:10px;text-align:left;vertical-align:top}}th{{background:#edf3ef}}.warning{{padding:16px;background:#fff0d5}}small{{overflow-wrap:anywhere}}@media print{{body{{margin:12mm}}thead{{display:table-header-group}}tr{{break-inside:avoid}}}}</style><body><p>FREIGHT AUDIT / INFORME LOCAL</p><h1>{escape(run["snapshot"]["label"])}</h1><p>{summary["determinable_findings"]} de {summary["total_findings"]} hallazgos determinables. Estado técnico y decisión humana se conservan por separado.</p>{warnings}<table><thead><tr><th>Moneda</th><th>Facturado aceptado</th><th>Determinable</th><th>Exceso determinado</th><th>Defecto determinado</th><th>En revisión</th><th>Indeterminado</th></tr></thead><tbody>{totals}</tbody></table><p>{escape(summary["economic_definition"])}</p><table><thead><tr><th>Operaciones</th><th>Concepto</th><th>Estado</th><th>Facturado</th><th>Esperado</th><th>Diferencia confirmada</th><th>Motivo</th></tr></thead><tbody>{rows}</tbody></table><p>Decisiones humanas registradas: {len(run["decisions"])}. El detalle, las fuentes y los cálculos están en el XLSX y en audit.json.</p><small>Auditoría {escape(run["id"])}<br>Resultado {escape(run["result_hash"])}<br>Motor {escape(run["artifact_hash"])}</small></body></html>"""


def bundle_bytes(store: Store, run_id: str) -> bytes:
    run = store.load(run_id)
    files = {
        "audit.json": canonical(run).encode(),
        "snapshot.json": canonical(run["snapshot"]).encode(),
        "reporte.html": html_report(run).encode(),
    }
    try:
        files["auditoria.xlsx"] = workbook_bytes(run)
    except ReportLimitError as exc:
        files["ADVERTENCIA_EXPORTACION.txt"] = (str(exc) + "\nNo se incluyó una planilla parcial.\n").encode()
    for source_hash in store.source_hashes(Dataset.model_validate(run["snapshot"])):
        files[f"sources/{source_hash}"] = store.source(source_hash)
    manifest = {name: bytes_hash(data) for name, data in files.items()}
    files["manifest.json"] = canonical(
        {"format": "freight-audit-bundle/v1", "run_id": run_id, "files": manifest}
    ).encode()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            archive.writestr(name, data)
    return output.getvalue()


def verify_bundle(data: bytes) -> dict:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            if (
                len({i.filename for i in infos}) != len(infos)
                or sum(i.file_size for i in infos) > 500 * 1024 * 1024
            ):
                raise IntegrityError("El paquete contiene entradas repetidas o supera el tamaño admitido.")
            manifest = load_json(archive.read("manifest.json"))
            if manifest["format"] != "freight-audit-bundle/v1":
                raise IntegrityError("Formato de paquete no admitido.")
            if set(archive.namelist()) != {*manifest["files"], "manifest.json"}:
                raise IntegrityError("El paquete contiene archivos no declarados o faltantes.")
            for name, source_hash in manifest["files"].items():
                if (
                    name.startswith("/")
                    or ".." in Path(name).parts
                    or bytes_hash(archive.read(name)) != source_hash
                ):
                    raise IntegrityError("Un archivo del paquete fue alterado.")
            run = load_json(archive.read("audit.json"))
            if (
                digest(run["snapshot"]) != run["input_hash"]
                or digest(run["result"]) != run["result_hash"]
                or digest([run["input_hash"], run["result_hash"], run["artifact_hash"]]) != run["id"]
                or run["id"] != manifest["run_id"]
            ):
                raise IntegrityError("Los hashes de auditoría no coinciden.")
            if canonical(load_json(archive.read("snapshot.json"))) != canonical(run["snapshot"]):
                raise IntegrityError("El snapshot no coincide con la auditoría.")
            previous = run["id"]
            for decision in run["decisions"]:
                if (
                    decision["previous_hash"] != previous
                    or digest([previous, decision["payload"], decision["created_at"]]) != decision["hash"]
                ):
                    raise IntegrityError("La cadena de decisiones no coincide.")
                previous = decision["hash"]
            for source_hash in Store.source_hashes(Dataset.model_validate(run["snapshot"])):
                if bytes_hash(archive.read(f"sources/{source_hash}")) != source_hash:
                    raise IntegrityError("El documento original fue alterado.")
            return run
    except (KeyError, ValueError, zipfile.BadZipFile) as exc:
        if isinstance(exc, IntegrityError):
            raise
        raise IntegrityError("El paquete está incompleto o dañado; usar una copia verificada.") from exc


def export_run(store: Store, run_id: str, destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("La carpeta de salida debe estar vacía para evitar reemplazar un informe previo.")
    bundle = bundle_bytes(store, run_id)
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        archive.extractall(destination)  # Names are generated internally, never user-provided ZIP entries.
    (destination / "auditoria.zip").write_bytes(bundle)
    return {"directory": str(destination), "run_id": run_id, "bundle_hash": bytes_hash(bundle)}
