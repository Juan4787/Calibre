"""Representative QA-tool validation, including deliberately corrupted outputs."""

import json
import sqlite3
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st
from openpyxl import load_workbook

from freight_audit.engine import audit
from freight_audit.models import Dataset
from freight_audit.project import load_project
from freight_audit.reporting import export_run
from freight_audit.storage import Store
from qa.catalog_tools import validate_catalog
from qa.generators import base_dataset, price_cases, uncertain_variant
from qa.impact import inventory
from qa.invariants import check_run, economic_projection, stable_hash
from qa.reference import price, quantize, rational

ROOT = Path(__file__).resolve().parents[1]


def serialized_run(raw):
    dataset = Dataset.model_validate(raw)
    computed = audit(dataset)
    snapshot, result = dataset.model_dump(mode="json"), computed.model_dump(mode="json")
    hashes = [stable_hash(snapshot), stable_hash(result), "a" * 64]
    return {
        "snapshot": snapshot,
        "result": result,
        "input_hash": hashes[0],
        "result_hash": hashes[1],
        "artifact_hash": hashes[2],
        "id": stable_hash(hashes),
        "decisions": [],
    }


def test_reference_manual_anchors():
    assert price() == "100"
    assert price(quantity="10", rate="2", minimum="30", surcharge="0.05") == "31.5"
    assert price(quantity="20", rate="2", minimum="30", surcharge="0.05") == "42"
    anchors = [
        ("1.005", "ROUND_HALF_UP", "1.01"),
        ("-1.005", "ROUND_HALF_UP", "-1.01"),
        ("2.345", "ROUND_HALF_EVEN", "2.34"),
        ("2.355", "ROUND_HALF_EVEN", "2.36"),
        ("-1.001", "ROUND_DOWN", "-1"),
        ("-1.001", "ROUND_UP", "-1.01"),
    ]
    for value, mode, expected in anchors:
        assert quantize(rational(value), 2, mode) == expected
    with pytest.raises(ValueError):
        rational(0.1)
    with pytest.raises(ValueError):
        quantize(rational("1.5"), 2, "ROUND_HALF_DOWN")


@given(price_cases())
def test_generated_reference_prices(case):
    raw, expected = case
    run = serialized_run(raw)
    finding = run["result"]["findings"][0]
    assert finding["expected"] == expected
    assert finding["status"] == "PASS"
    assert check_run(run) == []


@given(
    price_cases(),
    st.sampled_from(["evidence", "ambiguous_match", "overlap_version", "missing_date", "incomplete_import"]),
)
def test_generated_uncertainty_and_metamorphism(case, cause):
    raw, _ = case
    variant = uncertain_variant(raw, cause)
    run = serialized_run(variant)
    expected_state = "UNDETERMINABLE" if cause in {"overlap_version", "missing_date"} else "REVIEW"
    assert {f["status"] for f in run["result"]["findings"]} == {expected_state}
    assert check_run(run) == []
    permuted = deepcopy(variant)
    for name in ("charges", "shipments", "agreements"):
        permuted[name].reverse()
    assert serialized_run(permuted)["result"] == run["result"]
    permuted["label"] = "Renamed synthetic input"
    assert economic_projection(serialized_run(permuted)["result"]) == economic_projection(run["result"])


@pytest.mark.parametrize(
    "corruption",
    [
        "confirmed",
        "missing_charge",
        "duplicate_charge",
        "summary",
        "actual",
        "currency",
        "false_pass",
        "evidence",
        "version",
        "trace",
        "wrong_difference_sign",
        "unknown_rule",
    ],
)
def test_checker_rejects_economic_corruption(corruption):
    raw = base_dataset()
    raw["charges"][0]["amount"] = "110"
    if corruption in {"confirmed", "evidence"}:
        raw = uncertain_variant(raw, "evidence")
    run = serialized_run(raw)
    assert not check_run(run)
    broken = deepcopy(run)
    finding = broken["result"]["findings"][0]
    if corruption == "confirmed":
        finding["confirmed_difference"] = "10"
    elif corruption == "missing_charge":
        broken["result"]["findings"] = []
    elif corruption == "duplicate_charge":
        finding["charge_ids"].append("C1")
    elif corruption == "summary":
        broken["result"]["summary"]["currencies"]["ARS"]["actual"] = "111"
    elif corruption == "actual":
        finding["actual"] = "111"
    elif corruption == "currency":
        finding["currency"] = "USD"
    elif corruption == "false_pass":
        finding.update(status="PASS", confirmed_difference="0")
    elif corruption == "evidence":
        finding.update(status="FAIL", confirmed_difference="10", missing_evidence=[])
    elif corruption == "version":
        finding["version"] = "V2"
    elif corruption == "wrong_difference_sign":
        finding["difference"] = "-10"
    elif corruption == "unknown_rule":
        finding["rule"] = "R_UNKNOWN"
    else:
        next(t for t in finding["trace"] if t["op"] == "comparison")["output"] = "-10"
    # Isolate semantic validation: merely noticing a changed hash is not this oracle.
    assert check_run(broken, verify_hashes=False)


def test_cross_report_reconciliation_and_tamper_detection(tmp_path):
    from qa.reconcile import reconcile

    store = Store(tmp_path / "test.db")
    dataset, _ = load_project(ROOT / "fixtures/project.json", store)
    run_id = store.save(dataset, audit(dataset))
    run = store.load(run_id)
    directory = tmp_path / "exports"
    export_run(store, run_id, directory)
    assert not check_run(run, require_provenance=True)
    correct = reconcile(directory, api_run=run)
    assert correct["errors"] == []
    assert correct["channels"]["ui"] == "not supplied"
    path = directory / "auditoria.xlsx"
    original = path.read_bytes()
    workbook = load_workbook(path)
    workbook["Hallazgos"]["J2"] = "False certainty"
    workbook.save(path)
    workbook.close()
    assert any("XLSX Hallazgos" in e for e in reconcile(directory)["errors"])
    path.write_bytes(original)
    html = directory / "reporte.html"
    html.write_text(
        html.read_text(encoding="utf-8").replace("Coincide", "Discrepancia falsa", 1), encoding="utf-8"
    )
    assert any("HTML: visible" in e for e in reconcile(directory)["errors"])


def test_impact_is_read_only_and_retains_unknowns(tmp_path):
    path = tmp_path / "test.db"
    store = Store(path)
    raw = base_dataset()
    dataset = Dataset.model_validate(raw)
    run_id = store.save(dataset, audit(dataset))
    before = path.read_bytes()
    report = inventory(path, {"feature": "const", "importer_hash": "b" * 64})
    assert report["scanned"] == 1
    assert report["candidates"][0]["run_id"] == run_id
    assert report["candidates"][0]["classification"] == "unknown"
    assert path.read_bytes() == before
    assert inventory(path, {"currency": "USD"})["candidates"] == []
    with sqlite3.connect(path) as conn:
        conn.execute("DROP TRIGGER immutable_runs_UPDATE")
        conn.execute("UPDATE runs SET snapshot='{' WHERE id=?", (run_id,))
    assert inventory(path, {"currency": "USD"})["candidates"][0]["classification"] == "unknown"
    absent = tmp_path / "absent.db"
    with pytest.raises(ValueError):
        inventory(absent)
    assert not absent.exists()


def test_qa_catalog_references_real_tests():
    assert validate_catalog() == []


@pytest.mark.parametrize("payload", ['{"amount":"1","amount":"100"}', '{"snapshot": []}', "[]"])
def test_qa_cli_malformed_input_is_inconclusive(tmp_path, payload):
    path = tmp_path / "invalid.json"
    path.write_text(payload, encoding="utf-8")
    checked = subprocess.run(
        [sys.executable, "-O", str(ROOT / "scripts/qa.py"), "invariants", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 2
    assert json.loads(checked.stdout)["certification"] is False
    assert "Traceback" not in checked.stderr


def test_qa_cli_new_family_still_has_pending_obligations():
    checked = subprocess.run(
        [sys.executable, str(ROOT / "scripts/qa.py"), "matrix", "--ids", "QA-03"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0  # Listing is successful, not certification.
    result = json.loads(checked.stdout)
    assert result["pending_family_coverage"] == ["QA-03"]
    assert result["certification"] is False


def test_small_fuzz_corpus():
    import hashlib

    from freight_audit.importing import ImportMapping, import_data

    root = ROOT / "tests/fuzz_corpus"
    manifest = json.loads((root / "manifest.json").read_text())
    mapping = ImportMapping.model_validate(json.loads((root / "mapping.json").read_text()))
    for case in manifest:
        data = (root / case["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == case["sha256"]
        observed = import_data(data, case["file"], mapping)
        assert observed["accepted"] == case["accepted"]
        assert observed["rejected"] == case["rejected"]
        if case.get("weight"):
            assert observed["records"][0]["attributes"]["weight"]["value"] == case["weight"]
        if case.get("second_reference_row"):
            assert observed["records"][1]["provenance"]["reference"]["row"] == case["second_reference_row"]
