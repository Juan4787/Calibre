import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from freight_audit.engine import audit
from freight_audit.project import load_project
from freight_audit.storage import Store
from qa.external_control import compare_external_control
from qa.invariants import read_json

ROOT = Path(__file__).resolve().parents[1]


def example(tmp_path):
    store = Store(tmp_path / "audit.db")
    dataset, _ = load_project(ROOT / "fixtures/project.json", store)
    run_id = store.save(dataset, audit(dataset))
    control = read_json(ROOT / "fixtures/external-control.json")
    return store.load(run_id), control


def test_external_inventory_count_and_total_are_independent_blockers(tmp_path):
    run, control = example(tmp_path)
    assert compare_external_control(run, control)["passed"]
    variants = []
    missing_source = deepcopy(control)
    missing_source["source_hashes"].append("f" * 64)
    variants.append((missing_source, "source inventory"))
    missing_charge = deepcopy(control)
    missing_charge["charge_count"] -= 1
    variants.append((missing_charge, "charge counts"))
    changed_source_total = deepcopy(control)
    source = next(iter(changed_source_total["charge_totals_by_source"]))
    changed_source_total["charge_totals_by_source"][source]["ARS"] = "43719.41"
    variants.append((changed_source_total, "per-source charge totals"))
    changed_currency_total = deepcopy(control)
    changed_currency_total["actual_by_currency"]["ARS"] = "43719.41"
    variants.append((changed_currency_total, "currency totals"))
    for altered, signal in variants:
        result = compare_external_control(run, altered)
        assert not result["passed"] and any(signal in error for error in result["errors"])


def test_external_control_cli_exit_codes_and_hash_integrity(tmp_path):
    run, control = example(tmp_path)
    run_path = tmp_path / "run.json"
    control_path = tmp_path / "control.json"
    run_path.write_text(json.dumps(run), encoding="utf-8")
    control_path.write_text(json.dumps(control), encoding="utf-8")

    def execute():
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/qa.py"),
                "external-control",
                str(run_path),
                str(control_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    assert execute().returncode == 0
    run["result"]["summary"]["currencies"]["ARS"]["actual"] = "1"
    run_path.write_text(json.dumps(run), encoding="utf-8")
    failed = execute()
    assert failed.returncode == 1
    assert any("result_hash" in error for error in json.loads(failed.stdout)["errors"])
    control_path.write_text('{"schema":1,"schema":2}', encoding="utf-8")
    invalid = execute()
    assert invalid.returncode == 2
    assert "Duplicate JSON key" in invalid.stdout
