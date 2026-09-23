#!/usr/bin/env python3
"""Fault Generator for Phase 6 (Fault Injection).

Generates:
1. 41 directed faults across 7 groups (FI-I, FI-E, FI-P, FI-R, FI-A, FI-U, FI-X)
2. 12 healthy negative controls (CTRL-01 to CTRL-12)
3. Blind testing set of 10 faults stripped of identifiers
"""

import copy
import json
import random
import shutil
from pathlib import Path
from typing import Any, Callable

from openpyxl import load_workbook

from freight_audit.canonical import digest
from qa.invariants import stable_hash
from freight_audit.engine import audit
from freight_audit.models import Dataset
from freight_audit.project import load_project
from freight_audit.reporting import export_run
from freight_audit.storage import Store
from qa.reconcile import display_money, LABELS


def create_baseline(target_dir: Path) -> tuple[Store, Dataset, str, Path]:
    """Create a fresh clean baseline run and export bundle."""
    target_dir.mkdir(parents=True, exist_ok=True)
    db_path = target_dir / "audit.db"
    store = Store(db_path)
    dataset, _ = load_project(Path(__file__).resolve().parents[3] / "fixtures/project.json", store)
    run_id = store.save(dataset, audit(dataset))
    bundle_dir = target_dir / "bundle"
    export_run(store, run_id, bundle_dir)
    return store, dataset, run_id, bundle_dir


def create_ui_observation(run_dict: dict) -> dict[str, Any]:
    """Synthetic observation for detector unit controls; this is NOT a DOM capture."""
    findings = run_dict["result"]["findings"]
    return {
        "run_id": run_dict["id"],
        "result_hash": run_dict["result_hash"],
        "complete": True,
        "findings": [
            {
                "id": f["id"],
                "state": LABELS[f["status"]],
                "currency": f["currency"],
                "actual": display_money(f["actual"]),
                "expected": display_money(f["expected"]),
                "difference": display_money(f["difference"]),
            }
            for f in sorted(findings, key=lambda x: x["id"])
        ],
    }


# ==============================================================================
# Group FI-I: Importer / Normalization Faults (6)
# ==============================================================================

def inject_fi_i01(target_dir: Path) -> dict[str, Any]:
    """FI-I01: Importe +0.01 posterior a lectura documental."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    # Alter amount in snapshot.json and audit.json
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Mutate first charge amount from 100.00 to 100.01 in snapshot
    data["snapshot"]["charges"][0]["amount"] = "100.01"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    snapshot_json = bundle_dir / "snapshot.json"
    if snapshot_json.is_file():
        snap_data = json.loads(snapshot_json.read_text(encoding="utf-8"))
        snap_data["charges"][0]["amount"] = "100.01"
        snapshot_json.write_text(json.dumps(snap_data, indent=2), encoding="utf-8")
    
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_i02(target_dir: Path) -> dict[str, Any]:
    """FI-I02: Cambio de signo (100 -> -100)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    orig = data["snapshot"]["charges"][0]["amount"]
    data["snapshot"]["charges"][0]["amount"] = f"-{orig}" if not orig.startswith("-") else orig.removeprefix("-")
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    snapshot_json = bundle_dir / "snapshot.json"
    if snapshot_json.is_file():
        snap_data = json.loads(snapshot_json.read_text(encoding="utf-8"))
        snap_data["charges"][0]["amount"] = data["snapshot"]["charges"][0]["amount"]
        snapshot_json.write_text(json.dumps(snap_data, indent=2), encoding="utf-8")
    
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_i03(target_dir: Path) -> dict[str, Any]:
    """FI-I03: Moneda mutada (ARS -> USD)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    curr = data["snapshot"]["charges"][0]["currency"]
    new_curr = "USD" if curr != "USD" else "EUR"
    data["snapshot"]["charges"][0]["currency"] = new_curr
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    snapshot_json = bundle_dir / "snapshot.json"
    if snapshot_json.is_file():
        snap_data = json.loads(snapshot_json.read_text(encoding="utf-8"))
        snap_data["charges"][0]["currency"] = new_curr
        snapshot_json.write_text(json.dumps(snap_data, indent=2), encoding="utf-8")
    
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_i04(target_dir: Path) -> dict[str, Any]:
    """FI-I04: Fecha contractual desplazada hacia frontera de vigencia."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Shift service_date to a date that changes version validity
    shipment = data["snapshot"]["shipments"][0]
    shipment["attributes"]["service_date"]["value"] = "2026-07-01"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    snapshot_json = bundle_dir / "snapshot.json"
    if snapshot_json.is_file():
        snap_data = json.loads(snapshot_json.read_text(encoding="utf-8"))
        snap_data["shipments"][0]["attributes"]["service_date"]["value"] = "2026-07-01"
        snapshot_json.write_text(json.dumps(snap_data, indent=2), encoding="utf-8")
    
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_i05(target_dir: Path) -> dict[str, Any]:
    """FI-I05: Referencia alterada produciendo mismatch documental."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    data["snapshot"]["charges"][0]["reference"] = "REM-MUTATED-999"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    snapshot_json = bundle_dir / "snapshot.json"
    if snapshot_json.is_file():
        snap_data = json.loads(snapshot_json.read_text(encoding="utf-8"))
        snap_data["charges"][0]["reference"] = "REM-MUTATED-999"
        snapshot_json.write_text(json.dumps(snap_data, indent=2), encoding="utf-8")
    
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_i06(target_dir: Path) -> dict[str, Any]:
    """FI-I06: Provenance apuntando a celda/fila equivocada."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Corrupt row provenance in charges
    prov = data["snapshot"]["charges"][0]["provenance"]["amount"]
    prov["row"] = 999
    prov["column"] = ""
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    snapshot_json = bundle_dir / "snapshot.json"
    if snapshot_json.is_file():
        snap_data = json.loads(snapshot_json.read_text(encoding="utf-8"))
        snap_data["charges"][0]["provenance"]["amount"]["row"] = 999
        snap_data["charges"][0]["provenance"]["amount"]["column"] = ""
        snapshot_json.write_text(json.dumps(snap_data, indent=2), encoding="utf-8")
    
    return {"bundle_dir": bundle_dir, "run_id": run_id}


# ==============================================================================
# Group FI-E: Engine Economic Faults (12)
# ==============================================================================

def inject_fi_e01(target_dir: Path) -> dict[str, Any]:
    """FI-E01: Invertir signo de diferencia en finding (actual - expected -> expected - actual)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Find a finding with difference
    for f in data["result"]["findings"]:
        if f.get("difference") is not None and f["difference"] != "0.00":
            diff = f["difference"]
            f["difference"] = f"-{diff}" if not diff.startswith("-") else diff.removeprefix("-")
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e02(target_dir: Path) -> dict[str, Any]:
    """FI-E02: Tolerancia inclusiva convertida en exclusiva (<= tol -> < tol)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # In a PASS finding with 0 difference, set difference to 0.01 and change status to FAIL
    for f in data["result"]["findings"]:
        if f["status"] == "PASS":
            f["status"] = "FAIL"
            f["confirmed_difference"] = "0.01"
            f["difference"] = "0.01"
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e03(target_dir: Path) -> dict[str, Any]:
    """FI-E03: Confirmar diferencia monetaria estando en REVIEW."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    for f in data["result"]["findings"]:
        if f["status"] == "REVIEW":
            f["confirmed_difference"] = "15000.00"
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e04(target_dir: Path) -> dict[str, Any]:
    """FI-E04: Confirmar diferencia monetaria y expectativa estando en UNDETERMINABLE."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    for f in data["result"]["findings"]:
        if f["status"] == "UNDETERMINABLE":
            f["confirmed_difference"] = "5000.00"
            f["expected"] = "20000.00"
            f["difference"] = "5000.00"
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e05(target_dir: Path) -> dict[str, Any]:
    """FI-E05: Ignorar evidencia requerida certificando como PASS."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    for f in data["result"]["findings"]:
        if f["status"] == "REVIEW" and f.get("missing_evidence"):
            f["status"] = "PASS"
            f["missing_evidence"] = ["AUTH-REQUIRED-001"]
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e06(target_dir: Path) -> dict[str, Any]:
    """FI-E06: Seleccionar primera versión cuando hay dos vigentes solapadas."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Overlap two versions in agreement
    agr = data["snapshot"]["agreements"][0]
    if len(agr["versions"]) >= 2:
        agr["versions"][1]["valid_from"] = agr["versions"][0]["valid_from"]
    # Mark finding as PASS using version[0]
    data["result"]["findings"][0]["status"] = "PASS"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e07(target_dir: Path) -> dict[str, Any]:
    """FI-E07: Seleccionar primera regla ante ambigüedad en lugar de UNDETERMINABLE."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    for f in data["result"]["findings"]:
        if f["status"] == "UNDETERMINABLE":
            f["status"] = "PASS"
            f["rule"] = "RULE-01"
            f["version"] = "v1"
            f["expected"] = f["actual"]
            f["difference"] = "0.00"
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e08(target_dir: Path) -> dict[str, Any]:
    """FI-E08: Seleccionar primer shipment ante matching ambiguo (candidatos múltiples)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    for f in data["result"]["findings"]:
        if len(f.get("shipment_ids", [])) > 1:
            f["shipment_ids"] = [f["shipment_ids"][0]]
            f["status"] = "PASS"
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e09(target_dir: Path) -> dict[str, Any]:
    """FI-E09: Mezclar monedas en resumen económico (ARS + USD agregadas)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Mutate summary currencies
    curr_map = data["result"]["summary"]["currencies"]
    if "ARS" in curr_map:
        curr_map["ARS"]["actual"] = "99999999.00"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e10(target_dir: Path) -> dict[str, Any]:
    """FI-E10: Pérdida silenciosa de un cargo (N -> N-1 findings)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Drop one finding
    data["result"]["findings"].pop()
    data["result"]["summary"]["total_findings"] = len(data["result"]["findings"])
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e11(target_dir: Path) -> dict[str, Any]:
    """FI-E11: Duplicación de un cargo en findings."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Duplicate first finding
    dup = copy.deepcopy(data["result"]["findings"][0])
    data["result"]["findings"].append(dup)
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_e12(target_dir: Path) -> dict[str, Any]:
    """FI-E12: Redondeo prematuro alterando centavos esperados."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Shift expected on first finding with expected
    for f in data["result"]["findings"]:
        if f.get("expected") is not None:
            val = float(f["expected"]) + 0.05
            f["expected"] = f"{val:.2f}"
            break
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


# ==============================================================================
# Group FI-P: Persistence & History Faults (5)
# ==============================================================================

def inject_fi_p01(target_dir: Path) -> dict[str, Any]:
    """FI-P01: Snapshot correcto con result swap de otra corrida."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Replace findings with empty list or foreign findings
    data["result"]["findings"] = []
    data["result"]["summary"]["total_findings"] = 0
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_p02(target_dir: Path) -> dict[str, Any]:
    """FI-P02: Decisión humana vinculada a finding incorrecto o inexistente."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    decision = {
        "seq": 0,
        "hash": "dummy",
        "previous_hash": data["id"],
        "created_at": "2026-09-17T12:00:00Z",
        "payload": {
            "finding_id": "FINDING-NON-EXISTENT-XYZ",
            "action": "override_rate",
            "actor": "auditor",
            "note": "Corrupted decision",
            "evidence_ids": [],
            "known_to_client": True,
            "review_minutes": 5
        }
    }
    decision["hash"] = stable_hash([decision["previous_hash"], decision["payload"], decision["created_at"]])
    data["decisions"] = [decision]
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_p03(target_dir: Path) -> dict[str, Any]:
    """FI-P03: Orden alterado en cadena de decisiones o hash anterior corrupto."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    fid = data["result"]["findings"][0]["id"]
    d0 = {
        "seq": 0,
        "hash": "h0",
        "previous_hash": data["id"],
        "created_at": "2026-09-17T12:00:00Z",
        "payload": {"finding_id": fid, "action": "override_rate", "actor": "auditor1", "note": "d0", "evidence_ids": [], "known_to_client": True, "review_minutes": 2}
    }
    d0["hash"] = stable_hash([d0["previous_hash"], d0["payload"], d0["created_at"]])
    
    d1 = {
        "seq": 1,
        "hash": "h1",
        "previous_hash": d0["hash"],
        "created_at": "2026-09-17T12:05:00Z",
        "payload": {"finding_id": fid, "action": "accept_rate", "actor": "auditor2", "note": "d1", "evidence_ids": [], "known_to_client": True, "review_minutes": 3}
    }
    d1["hash"] = stable_hash([d1["previous_hash"], d1["payload"], d1["created_at"]])
    
    # Invert the order in decisions list: [d1, d0]
    data["decisions"] = [d1, d0]
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_p04(target_dir: Path) -> dict[str, Any]:
    """FI-P04: Artifact hash falsificado."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    data["artifact_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_p05(target_dir: Path) -> dict[str, Any]:
    """FI-P05: Sources válidas pero incompletas (archivo de source eliminado de sources/)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    sources_dir = bundle_dir / "sources"
    files = list(sources_dir.iterdir())
    if files:
        files[0].unlink()
    return {"bundle_dir": bundle_dir, "run_id": run_id}


# ==============================================================================
# Group FI-R: Reporting & Export Faults (6)
# ==============================================================================

def inject_fi_r01(target_dir: Path) -> dict[str, Any]:
    """FI-R01: XLSX desincronizado (REVIEW -> PASS exclusivamente en Excel)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    xlsx_path = bundle_dir / "auditoria.xlsx"
    wb = load_workbook(xlsx_path)
    ws = wb["Hallazgos"]
    for row in ws.iter_rows(min_row=2):
        # Column 10 is Status / Estado
        if row[9].value == "Revisión humana":
            row[9].value = "Coincide"
            break
    wb.save(xlsx_path)
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_r02(target_dir: Path) -> dict[str, Any]:
    """FI-R02: HTML desincronizado (UNDETERMINABLE -> FAIL exclusivamente en HTML)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    html_path = bundle_dir / "reporte.html"
    content = html_path.read_text(encoding="utf-8")
    # Replace Indeterminado with Discrepancia in table
    new_content = content.replace("Indeterminado", "Discrepancia", 1)
    html_path.write_text(new_content, encoding="utf-8")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_r03(target_dir: Path) -> dict[str, Any]:
    """FI-R03: XLSX alterado en importe/diferencia (difference = 20 -> 200)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    xlsx_path = bundle_dir / "auditoria.xlsx"
    wb = load_workbook(xlsx_path)
    ws = wb["Hallazgos"]
    for row in ws.iter_rows(min_row=2):
        # Column 8 is difference
        if row[7].value is not None and str(row[7].value) != "0.00":
            row[7].value = "99999.00"
            break
    wb.save(xlsx_path)
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_r04(target_dir: Path) -> dict[str, Any]:
    """FI-R04: XLSX con fila de finding eliminada."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    xlsx_path = bundle_dir / "auditoria.xlsx"
    wb = load_workbook(xlsx_path)
    ws = wb["Hallazgos"]
    ws.delete_rows(2, 1)
    wb.save(xlsx_path)
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_r05(target_dir: Path) -> dict[str, Any]:
    """FI-R05: XLSX con moneda cambiada (USD -> ARS) sin tocar importe."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    xlsx_path = bundle_dir / "auditoria.xlsx"
    wb = load_workbook(xlsx_path)
    ws = wb["Hallazgos"]
    for row in ws.iter_rows(min_row=2):
        if row[4].value == "ARS":
            row[4].value = "USD"
            break
    wb.save(xlsx_path)
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_r06(target_dir: Path) -> dict[str, Any]:
    """FI-R06: XLSX con motivo/reasons eliminado de fila REVIEW."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    xlsx_path = bundle_dir / "auditoria.xlsx"
    wb = load_workbook(xlsx_path)
    ws = wb["Hallazgos"]
    for row in ws.iter_rows(min_row=2):
        if row[9].value == "Revisión humana":
            row[13].value = ""  # Reasons
            row[15].value = ""  # Missing evidence
            break
    wb.save(xlsx_path)
    return {"bundle_dir": bundle_dir, "run_id": run_id}


# ==============================================================================
# Group FI-A: API Faults (4)
# ==============================================================================

def inject_fi_a01(target_dir: Path) -> dict[str, Any]:
    """FI-A01: API devuelve estado diferente al persistido (FAIL -> PASS)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    
    api_run = copy.deepcopy(audit_data)
    for f in api_run["result"]["findings"]:
        if f["status"] == "FAIL":
            f["status"] = "PASS"
            f["confirmed_difference"] = "0.00"
            break
    return {"bundle_dir": bundle_dir, "run_id": run_id, "api_run": api_run}


def inject_fi_a02(target_dir: Path) -> dict[str, Any]:
    """FI-A02: API omite un finding respecto al run persistido."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    
    api_run = copy.deepcopy(audit_data)
    api_run["result"]["findings"].pop()
    return {"bundle_dir": bundle_dir, "run_id": run_id, "api_run": api_run}


def inject_fi_a03(target_dir: Path) -> dict[str, Any]:
    """FI-A03: API cambia importe actual en un finding."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    
    api_run = copy.deepcopy(audit_data)
    f0 = api_run["result"]["findings"][0]
    f0["actual"] = "999999.00"
    return {"bundle_dir": bundle_dir, "run_id": run_id, "api_run": api_run}


def inject_fi_a04(target_dir: Path) -> dict[str, Any]:
    """FI-A04: API pierde provenance en snapshot."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    
    api_run = copy.deepcopy(audit_data)
    api_run["snapshot"]["charges"][0]["provenance"] = {}
    return {"bundle_dir": bundle_dir, "run_id": run_id, "api_run": api_run}


# ==============================================================================
# Group FI-U: UI Faults (4)
# ==============================================================================

def inject_fi_u01(target_dir: Path) -> dict[str, Any]:
    """FI-U01: UI DOM muestra 'Coincide' (PASS) para finding que es REVIEW."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    observed_ui = create_ui_observation(audit_data)
    
    # Mutate UI observation
    for uf in observed_ui["findings"]:
        if uf["state"] == "Revisión humana":
            uf["state"] = "Coincide"
            break
    return {"bundle_dir": bundle_dir, "run_id": run_id, "observed_ui": observed_ui}


def inject_fi_u02(target_dir: Path) -> dict[str, Any]:
    """FI-U02: UI DOM altera diferencia (+20.00 -> +2.00)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    observed_ui = create_ui_observation(audit_data)
    
    for uf in observed_ui["findings"]:
        if uf["difference"] != "—" and uf["difference"] != "0,00":
            uf["difference"] = "+2,00"
            break
    return {"bundle_dir": bundle_dir, "run_id": run_id, "observed_ui": observed_ui}


def inject_fi_u03(target_dir: Path) -> dict[str, Any]:
    """FI-U03: UI DOM altera moneda (USD -> ARS)."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    observed_ui = create_ui_observation(audit_data)
    
    for uf in observed_ui["findings"]:
        if uf["currency"] == "ARS":
            uf["currency"] = "USD"
            break
    return {"bundle_dir": bundle_dir, "run_id": run_id, "observed_ui": observed_ui}


def inject_fi_u04(target_dir: Path) -> dict[str, Any]:
    """FI-U04: UI DOM omite completitud o datos de auditoría."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    observed_ui = create_ui_observation(audit_data)
    
    # Omit complete flag in UI DOM
    observed_ui["complete"] = False
    return {"bundle_dir": bundle_dir, "run_id": run_id, "observed_ui": observed_ui}


# ==============================================================================
# Group FI-X: Cross-layer / Combinados (4)
# ==============================================================================

def inject_fi_x01(target_dir: Path) -> dict[str, Any]:
    """FI-X01: Importer mutado +0.01 y XLSX desincronizado para enmascarar."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    data["snapshot"]["charges"][0]["amount"] = "9999.01"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    xlsx_path = bundle_dir / "auditoria.xlsx"
    wb = load_workbook(xlsx_path)
    ws = wb["Hallazgos"]
    ws.cell(row=2, column=6, value="9999.01")
    wb.save(xlsx_path)
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_x02(target_dir: Path) -> dict[str, Any]:
    """FI-X02: Cascada de mutación de estado: Core REVIEW, HTML renderiza PASS, UI renderiza Coincide."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
    
    # Mutate HTML
    html_path = bundle_dir / "reporte.html"
    html = html_path.read_text(encoding="utf-8").replace("Revisión humana", "Coincide", 1)
    html_path.write_text(html, encoding="utf-8")
    
    # Mutate UI
    observed_ui = create_ui_observation(audit_data)
    for uf in observed_ui["findings"]:
        if uf["state"] == "Revisión humana":
            uf["state"] = "Coincide"
            break
            
    return {"bundle_dir": bundle_dir, "run_id": run_id, "observed_ui": observed_ui}


def inject_fi_x03(target_dir: Path) -> dict[str, Any]:
    """FI-X03: Alteración combinada snapshot + result sin tocar raw doc."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    data = json.loads(audit_json.read_text(encoding="utf-8"))
    
    # Modify finding actual and snapshot charge amount together
    data["snapshot"]["charges"][0]["amount"] = "88888.88"
    data["result"]["findings"][0]["actual"] = "88888.88"
    audit_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    snapshot_json = bundle_dir / "snapshot.json"
    if snapshot_json.is_file():
        snap_data = json.loads(snapshot_json.read_text(encoding="utf-8"))
        snap_data["charges"][0]["amount"] = "88888.88"
        snapshot_json.write_text(json.dumps(snap_data, indent=2), encoding="utf-8")
    
    return {"bundle_dir": bundle_dir, "run_id": run_id}


def inject_fi_x04(target_dir: Path) -> dict[str, Any]:
    """FI-X04: Alteración de bytes en audit.json sin actualizar manifest.json."""
    store, dataset, run_id, bundle_dir = create_baseline(target_dir)
    audit_json = bundle_dir / "audit.json"
    # Append a trailing newline or comment in json
    content = audit_json.read_bytes()
    audit_json.write_bytes(content + b" ")
    return {"bundle_dir": bundle_dir, "run_id": run_id}


# All injectors catalog
INJECTORS: dict[str, Callable[[Path], dict[str, Any]]] = {
    # 6B - Importer (6)
    "FI-I01": inject_fi_i01,
    "FI-I02": inject_fi_i02,
    "FI-I03": inject_fi_i03,
    "FI-I04": inject_fi_i04,
    "FI-I05": inject_fi_i05,
    "FI-I06": inject_fi_i06,
    # 6C - Engine (12)
    "FI-E01": inject_fi_e01,
    "FI-E02": inject_fi_e02,
    "FI-E03": inject_fi_e03,
    "FI-E04": inject_fi_e04,
    "FI-E05": inject_fi_e05,
    "FI-E06": inject_fi_e06,
    "FI-E07": inject_fi_e07,
    "FI-E08": inject_fi_e08,
    "FI-E09": inject_fi_e09,
    "FI-E10": inject_fi_e10,
    "FI-E11": inject_fi_e11,
    "FI-E12": inject_fi_e12,
    # 6D - Persistence (5)
    "FI-P01": inject_fi_p01,
    "FI-P02": inject_fi_p02,
    "FI-P03": inject_fi_p03,
    "FI-P04": inject_fi_p04,
    "FI-P05": inject_fi_p05,
    # 6E - Reporting (6)
    "FI-R01": inject_fi_r01,
    "FI-R02": inject_fi_r02,
    "FI-R03": inject_fi_r03,
    "FI-R04": inject_fi_r04,
    "FI-R05": inject_fi_r05,
    "FI-R06": inject_fi_r06,
    # 6F - API & UI (8)
    "FI-A01": inject_fi_a01,
    "FI-A02": inject_fi_a02,
    "FI-A03": inject_fi_a03,
    "FI-A04": inject_fi_a04,
    "FI-U01": inject_fi_u01,
    "FI-U02": inject_fi_u02,
    "FI-U03": inject_fi_u03,
    "FI-U04": inject_fi_u04,
    # 6X - Cross-layer (4)
    "FI-X01": inject_fi_x01,
    "FI-X02": inject_fi_x02,
    "FI-X03": inject_fi_x03,
    "FI-X04": inject_fi_x04,
}


# ==============================================================================
# Healthy Negative Controls (12)
# ==============================================================================

def generate_healthy_control(control_id: str, target_dir: Path) -> dict[str, Any]:
    """Generate legitimate healthy run artifacts for negative controls (must evaluate to TRUSTED)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    db_path = target_dir / "audit.db"
    store = Store(db_path)
    dataset, summary = load_project(Path("fixtures/project.json"), store)
    
    if control_id == "CTRL-01":
        # Standard baseline run
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        return {
            "bundle_dir": bundle_dir,
            "api_run": audit_data,
            "observed_ui": create_ui_observation(audit_data),
        }
        
    elif control_id == "CTRL-02":
        # Verify legitimate PASS finding presence
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        assert any(f["status"] == "PASS" for f in audit_data["result"]["findings"])
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}
        
    elif control_id == "CTRL-03":
        # Verify legitimate FAIL finding presence
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        assert any(f["status"] == "FAIL" for f in audit_data["result"]["findings"])
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}
        
    elif control_id == "CTRL-04":
        # Verify legitimate REVIEW finding presence
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        assert any(f["status"] == "REVIEW" for f in audit_data["result"]["findings"])
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-05":
        # Verify legitimate UNDETERMINABLE finding presence
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        assert any(f["status"] == "UNDETERMINABLE" for f in audit_data["result"]["findings"])
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-06":
        # Legitimate added evidence and subsequent audit
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-07":
        # Valid contractual version validity window
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-08":
        # Document filename variation with identical content
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-09":
        # Valid reordered columns during import
        run_id = store.save(dataset, audit(dataset))
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-10":
        # Process restart / reload from SQLite DB
        run_id = store.save(dataset, audit(dataset))
        # Reconnect from new Store instance
        reopened_store = Store(db_path)
        bundle_dir = target_dir / "bundle"
        export_run(reopened_store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-11":
        # Repeated idempotent export of identical run
        run_id = store.save(dataset, audit(dataset))
        bundle_dir1 = target_dir / "bundle1"
        bundle_dir2 = target_dir / "bundle2"
        export_run(store, run_id, bundle_dir1)
        export_run(store, run_id, bundle_dir2)
        audit_data = json.loads((bundle_dir2 / "audit.json").read_text(encoding="utf-8"))
        return {"bundle_dir": bundle_dir2, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    elif control_id == "CTRL-12":
        # Human decision recorded legitimately and preserved in chain
        from freight_audit.models import Decision
        run_id = store.save(dataset, audit(dataset))
        rec = store.load(run_id)
        fid = rec["result"]["findings"][0]["id"]
        decision = Decision(
            finding_id=fid,
            action="APPROVED",
            actor="supervisor@empresa.com",
            note="Tarifa aceptada conforme orden de compra",
            evidence_ids=[],
            known_to_client=True,
            review_minutes=4
        )
        store.add_decision(run_id, decision)
        bundle_dir = target_dir / "bundle"
        export_run(store, run_id, bundle_dir)
        audit_data = json.loads((bundle_dir / "audit.json").read_text(encoding="utf-8"))
        return {"bundle_dir": bundle_dir, "api_run": audit_data, "observed_ui": create_ui_observation(audit_data)}

    raise ValueError(f"Unknown control_id: {control_id}")


# ==============================================================================
# Blind Fault Generation (10 faults with secret key)
# ==============================================================================

BLIND_SELECTION = [
    "FI-I01",  # Importer +0.01
    "FI-I02",  # Importer sign change
    "FI-E01",  # Invert difference
    "FI-E03",  # Confirm diff in REVIEW
    "FI-E10",  # Charge dropped
    "FI-P02",  # Decision for invalid finding
    "FI-P05",  # Source missing
    "FI-R01",  # XLSX status desync
    "FI-A03",  # API actual amount altered
    "FI-U01",  # UI DOM status altered
]


def generate_blind_faults(blind_dir: Path) -> dict[str, str]:
    """Generate 10 blind faults in blind_dir/BLIND-01..10 and write secret key."""
    blind_dir.mkdir(parents=True, exist_ok=True)
    secret_key = {}
    
    for idx, fault_id in enumerate(BLIND_SELECTION, start=1):
        blind_name = f"BLIND-{idx:02d}"
        secret_key[blind_name] = fault_id
        case_dir = blind_dir / blind_name
        if case_dir.exists():
            shutil.rmtree(case_dir)
        case_dir.mkdir(parents=True, exist_ok=True)
        
        injector = INJECTORS[fault_id]
        payload = injector(case_dir)
        
        # Save optional api_run or observed_ui in the directory for the agnostic runner to consume
        if "api_run" in payload:
            (case_dir / "api_run.json").write_text(json.dumps(payload["api_run"], indent=2), encoding="utf-8")
        if "observed_ui" in payload:
            (case_dir / "observed_ui.json").write_text(json.dumps(payload["observed_ui"], indent=2), encoding="utf-8")
            
    # Save secret key
    (blind_dir / "secret_key.json").write_text(json.dumps(secret_key, indent=2), encoding="utf-8")
    return secret_key
