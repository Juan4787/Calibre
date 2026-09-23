#!/usr/bin/env python3
"""Generate coverage from the causal catalog and source-bound execution receipts."""

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qa.catalog import FAMILIES  # noqa: E402
from qa.catalog_tools import validate_catalog  # noqa: E402
from qa.evidence import receipt_is_current, source_digest  # noqa: E402


def build_ledger(receipt_paths=()):
    errors = validate_catalog()
    if errors:
        raise ValueError("\n".join(errors))
    fingerprint = source_digest(ROOT)
    receipts = []
    for path in receipt_paths:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        log = Path(receipt.get("log", ""))
        log_matches = log.is_file() and hashlib.sha256(log.read_bytes()).hexdigest() == receipt.get(
            "log_sha256"
        )
        receipts.append(
            {
                "path": str(path),
                "command": receipt.get("command"),
                "exit_code": receipt.get("exit_code"),
                "accepted": receipt_is_current(receipt, fingerprint) and log_matches,
                "receipt_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    families = []
    for item in FAMILIES:
        # A passing selector cannot establish complete coverage of a causal family.
        status = (
            "REQUIRES_REAL_CLIENT"
            if item["DATOS_REALES"]
            else "DEFERRED_NON_BLOCKING"
            if item["PRIORIDAD"] == "P3" and item["ESTADO_COBERTURA"] == "diferido"
            else "PARTIAL"
            if item["SELECTORES"] or item["RUNNERS"]
            else "NO_REGISTERED_RUNNER"
        )
        families.append(
            {
                "id": item["TEST_ID"],
                "name": item["NOMBRE"],
                "priority": item["PRIORIDAD"],
                "severity": item["SEVERIDAD"],
                "status": status,
                "requirement": item["RESULTADO_ESPERADO"],
                "steps": item["PASOS_EXACTOS"],
                "oracle": item["ORACULO"],
                "false_negatives": item["FALSOS_NEGATIVOS"],
                "requires_windows": item["WINDOWS"],
                "requires_human": item["INTERVENCION_HUMANA"],
                "selectors": item["SELECTORES"],
                "runners": item["RUNNERS"],
                "command": shlex.join([".venv/bin/python", "-m", "pytest", "-q", *item["SELECTORES"]])
                if item["SELECTORES"]
                else None,
            }
        )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    result = {
        "schema": "calibre-coverage/v2",
        "commit": commit,
        "source_digest": fingerprint,
        "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)),
        "certification": False,
        "total_families": len(families),
        "full_product_coverage": "PENDING_OBLIGATION_REVIEW",
        "gate_s": "QA_INFRASTRUCTURE_ONLY_SEE_RELEASE_CRITERIA",
        "distribution_files_observed": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "dist").glob("*"))
            if p.is_file()
        },
        "distribution_note": "Hashes observed on disk; acceptance also requires a current build/install receipt.",
        "executions": receipts,
        "families": families,
    }
    docs = ROOT / "docs"
    (docs / "QA_COVERAGE_LEDGER.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Cobertura de QA: obligaciones y evidencia",
        "",
        "**No hay certificación global ni porcentaje de cobertura causal derivable del número de tests. El Gate S de infraestructura QA se evalúa según RELEASE_CRITERIA.md y no exige ni acredita cobertura total de producto.**",
        "",
        "Este registro sustituye el cierre automático de 51/51 familias. El anterior acortaba obligaciones del catálogo, citaba selectores inexistentes y usaba hashes fijos.",
        "",
        "Fuente única: `qa/catalog.py`. Un selector existente acredita infraestructura disponible; una ejecución acredita sus casos, no toda la familia.",
        "",
        "Las campañas históricas Windows, escala, importación y E2E conservan su alcance original. No certifican este checkout. Ver `RIGOR_REVIEW.md`.",
        "",
        f"Commit base: `{commit}`; huella del código y pruebas: `{fingerprint}`.",
        "",
        "## Ejecuciones adjuntas",
        "",
        "| Recibo | Código y log verificables | Salida | Comando |",
        "|---|---|---|---|",
    ]
    for receipt in receipts:
        lines.append(
            f"| {receipt['path']} | {'Sí' if receipt['accepted'] else 'No: pendiente/incompatible'} | {receipt['exit_code']} | `{shlex.join(receipt['command'] or [])}` |"
        )
    if not receipts:
        lines.append("| Ninguna adjunta | No | — | — |")
    lines += [
        "",
        "## Familias",
        "",
        "| Familia | Prioridad | Estado conservador | Selectores existentes |",
        "|---|---|---|---|",
    ]
    for item in families:
        lines.append(
            f"| {item['id']} — {item['name']} | {item['priority']} | {item['status']} | {len(item['selectors'])} |"
        )
    for item in families:
        lines += [
            "",
            f"## {item['id']} — {item['name']}",
            "",
            f"**Obligación:** {item['requirement']}",
            "",
            f"**Procedimiento:** {item['steps']}",
            "",
            f"**Oráculo:** {item['oracle']}. **Lo que puede escapar:** {item['false_negatives']}",
            "",
        ]
        if item["command"]:
            lines += ["Comando del subconjunto automatizado:", "", "```bash", item["command"], "```"]
        for runner in item["runners"]:
            lines += [
                "",
                "Runner adicional; usar un directorio de evidencia nuevo:",
                "",
                "```bash",
                runner,
                "```",
            ]
        if not item["command"] and not item["runners"]:
            lines += [
                "Sin selector automatizado: ejecutar el procedimiento y conservar evidencia antes de cerrar."
            ]
    (docs / "QA_COVERAGE_LEDGER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"Generated {len(families)} families; {sum(r['accepted'] for r in receipts)} current receipts; certification=false"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, action="append", default=[])
    build_ledger(parser.parse_args().evidence)
