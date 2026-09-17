"""Render/validate the operational matrix without collecting or running product tests."""

import ast
import csv
import io
import re
from collections import Counter
from pathlib import Path

from .catalog import FAMILIES

ROOT = Path(__file__).resolve().parents[1]


def value_text(value):
    if isinstance(value, list):
        return "; ".join(value) or "Pendiente: sin selector automatizado"
    if isinstance(value, bool):
        return "sí" if value else "no"
    return str(value)


def rendered():
    matrix = [
        "# Matriz maestra de verificación",
        "",
        "Generada desde `qa/catalog.py` con `.venv/bin/python scripts/qa.py matrix --generate`. Editar el catálogo, no esta vista. `parcial` significa que los selectores cubren sólo parte de los casos descritos; `nuevo` tampoco significa certificación completa. Pasos base en QA_CASES.md, oráculos en TEST_ORACLES.md y respuesta común obligatoria en INCIDENT_RESPONSE.md.",
        "",
        "Seleccionar: `.venv/bin/python scripts/qa.py matrix --priority P0 P1`. Ejecutar sólo cobertura existente: añadir `--run-existing`; salida3 indica familias pendientes aunque sus selectores pasen. No tomarla como gate aprobado.",
        "",
        "| ID | Familia | Severidad | Prioridad / grupo | Cobertura | Riesgo / costo |",
        "|---|---|---|---|---|---|",
    ]
    for row in FAMILIES:
        matrix.append(
            f"| [{row['TEST_ID']}](#{row['TEST_ID'].lower()}) | {row['NOMBRE']} | {row['SEVERIDAD']} | {row['PRIORIDAD']} / {row['GRUPO']} | {row['ESTADO_COBERTURA']} | {row['RIESGO_SCORE']} / {row['VALOR_POR_COSTO']:g} |"
        )
    for row in FAMILIES:
        matrix += ["", f"## {row['TEST_ID']}", ""]
        for key, value in row.items():
            matrix.append(f"- **{key}:** {value_text(value)}")
        if row["SELECTORES"]:
            matrix += ["", "```bash", ".venv/bin/python -m pytest -q " + " ".join(row["SELECTORES"]), "```"]
        else:
            matrix += [
                "",
                "No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.",
            ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(FAMILIES[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows({key: value_text(value) for key, value in row.items()} for row in FAMILIES)
    backlog = [
        "# Backlog de automatización",
        "",
        "Generado desde `qa/catalog.py`. Estimaciones de implementación orientativas para alguien familiarizado con el repositorio; no SLA. Grupo A se ejecuta/automatiza primero; B queda diseñado y la feature correspondiente no se habilita sin su gate; C se difiere. Prioridad económica prevalece sobre score/costo.",
        "",
        "## Orden recomendado",
        "",
        "1. Usar referencia/checker y sus pruebas negativas (QA-01..08, QA-27, QA-49).",
        "2. Completar fronteras temporales, matching y evidencia (QA-16..26).",
        "3. Completar corpus estructurado/importación y salidas/DOM (QA-08..17, QA-37..43).",
        "4. Metadatos de cadena completa, scope y aislamiento (QA-29, QA-33, QA-56..57).",
        "5. Antes de entorno/feature nueva: crash/migraciones, Windows, fuzz pesado y performance completa.",
        "6. Cliente real: protocolo ciego y aprobación contractual; no delegar esa verdad a un generador.",
        "",
        "Cada entrada enlaza datos, pasos, expected y runbook. Para entregar una tarea: citar TEST_ID, exigir reproducer mínimo, prueba del oráculo y resultado de sólo los checks afectados; no pedir un barrido repetitivo de toda la suite.",
        "",
        "| Familia | P / grupo | Riesgo | Dificultad / esfuerzo | Automatización / herramienta | Ejecución / costo | Datos reales | Windows | Humano | Estado |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in sorted(
        FAMILIES, key=lambda r: (r["PRIORIDAD"], r["GRUPO"], -r["VALOR_POR_COSTO"], r["TEST_ID"])
    ):
        kind = row["TIPO_IDEAL"]
        tool = (
            "Hypothesis + pytest"
            if "property" in kind or "fuzz" in kind
            else "runner dirigido + pytest"
            if "mutation" in kind
            else "Playwright + reconciliador"
            if "E2E" in kind
            else "procedimiento con evidencia"
            if kind == "manual"
            else "pytest / CLI QA"
        )
        difficulty = (
            "alta"
            if row["COSTO_EJECUCION"] == "alto" or row["DATOS_REALES"]
            else "media"
            if row["COSTO_EJECUCION"] == "medio"
            else "baja/media"
        )
        backlog.append(
            f"| [{row['TEST_ID']}](TEST_MATRIX.md#{row['TEST_ID'].lower()}) {row['NOMBRE']} | {row['PRIORIDAD']} / {row['GRUPO']} | {row['RIESGO']} | {difficulty}; {row['ESFUERZO_IMPLEMENTACION']} | {kind}; {tool} | {row['CUANDO']}; {row['COSTO_EJECUCION']} | {value_text(row['DATOS_REALES'])} | {value_text(row['WINDOWS'])} | {value_text(row['INTERVENCION_HUMANA'])} | {row['ESTADO_COBERTURA']} |"
        )
    return {
        "docs/TEST_MATRIX.md": "\n".join(matrix) + "\n",
        "docs/TEST_MATRIX.csv": output.getvalue(),
        "docs/TEST_AUTOMATION_BACKLOG.md": "\n".join(backlog) + "\n",
    }


def validate_catalog():
    errors: list[str] = []
    counts = Counter(row["TEST_ID"] for row in FAMILIES)
    errors.extend(f"Duplicate TEST_ID {key}" for key, count in counts.items() if count != 1)
    invariants = (ROOT / "docs/ECONOMIC_INVARIANTS.md").read_text(encoding="utf-8")
    incidents = (ROOT / "docs/INCIDENT_RESPONSE.md").read_text(encoding="utf-8")
    for row in FAMILIES:
        for token in re.findall(r"INV-\d{2}", row["INVARIANTE"]):
            if token not in invariants:
                errors.append(f"{row['TEST_ID']}: unknown {token}")
        for token in re.findall(r"IR-\d{2}", row["RESPUESTA_SI_FALLA"]):
            if token not in incidents:
                errors.append(f"{row['TEST_ID']}: unknown {token}")
        for selector in row["SELECTORES"]:
            path, function = selector.split("::", 1)
            full_path = ROOT / path
            if not full_path.is_file():
                errors.append(f"{row['TEST_ID']}: missing selector {selector}")
                continue
            names = {
                n.name
                for n in ast.walk(ast.parse(full_path.read_text(encoding="utf-8")))
                if isinstance(n, ast.FunctionDef)
            }
            if function not in names:
                errors.append(f"{row['TEST_ID']}: unknown function {selector}")
        if row["GRUPO"] not in {"A", "B", "C"} or row["PRIORIDAD"] not in {"P0", "P1", "P2", "P3"}:
            errors.append(f"{row['TEST_ID']}: invalid priority/group")
        if any(value == "" for value in row.values()):
            errors.append(f"{row['TEST_ID']}: empty field")
    return errors
