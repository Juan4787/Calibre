"""Negative controls for the verification system itself."""

from copy import deepcopy

import pytest

from qa.gates import PIPELINE_STAGES, endurance_passed, fingerprint_errors, pipeline_passed, platform_passed


def test_platform_requires_every_case_and_rejects_infrastructure_errors():
    report = {"cases": {f"WIN-{n:02d}": {"status": "PASSED"} for n in range(1, 25)}}
    assert platform_passed(report)
    for status in ("FAILED", "FAILED_INFRA", "SKIPPED_INFRA", "UNKNOWN"):
        report["cases"]["WIN-24"]["status"] = status
        assert not platform_passed(report)
    assert not platform_passed({"cases": {}})


def test_pipeline_does_not_certify_core_only_or_unverified_bundle():
    report = {
        "correctness_verified": True,
        "stages": {name: {"status": "PASS"} for name in PIPELINE_STAGES},
    }
    report["stages"]["12_verify_bundle"] = {"verified": True, "status": "PASS"}
    assert pipeline_passed(report)
    for status in ("BOUNDED_AT_SCALE", "INTEGRITY_ERROR", "SKIPPED_PRODUCER_LIMIT"):
        broken = deepcopy(report)
        broken["stages"]["12_verify_bundle"] = {"verified": False, "status": status}
        assert not pipeline_passed(broken)
    assert not pipeline_passed({})


@pytest.mark.parametrize("evaluation", ["LEAK-LIKE", "SUSPICIOUS", "INCONCLUSIVE"])
def test_endurance_requires_stability_and_restart(evaluation):
    report = {
        "iterations": 10,
        "evaluation": "STABLE",
        "fd_leak_detected": False,
        "restart_verification": {"passed": True, "exit_code": 0},
    }
    assert endurance_passed(report)
    report["evaluation"] = evaluation
    assert not endurance_passed(report)
    report["evaluation"] = "STABLE"
    report["restart_verification"]["exit_code"] = 1
    assert not endurance_passed(report)


def test_empty_or_historical_fingerprints_are_not_parity_evidence():
    assert fingerprint_errors({})
    assert fingerprint_errors({"runs": [], "digest": "anything"})


def test_comparer_rejects_empty_duplicate_and_changed_identity():
    from output.e2e.platform_scale.compare_fingerprints import compare_runs

    assert not compare_runs([], [])[0]
    runs = [{"dataset_label": "demo", "findings": [{"id": "one", "version": "v1"}]}]
    assert compare_runs(runs, deepcopy(runs))[0]
    assert not compare_runs(runs * 2, runs * 2)[0]
    changed = deepcopy(runs)
    changed[0]["findings"][0]["version"] = "v2"
    assert not compare_runs(runs, changed)[0]
    changed = deepcopy(runs)
    changed[0]["findings"] *= 2
    assert not compare_runs(changed, changed)[0]


def test_directed_runner_does_not_credit_broken_fixture(monkeypatch, tmp_path):
    import json

    from output.e2e.fault_injection import run_directed_faults as directed

    def broken(_):
        raise FileNotFoundError("required fixture missing")

    monkeypatch.setattr(directed, "INJECTORS", {"FI-BROKEN": broken})
    assert directed.run_all_faults(tmp_path) is False
    row = json.loads((tmp_path / "detector_matrix.json").read_text())["results"]["FI-BROKEN"]
    assert row["status"] == "INCONCLUSIVE"
    assert row["independent_detection"] is False
    assert (tmp_path / "incidents/FI-BROKEN/reproducer").is_dir()


def test_benchmark_aggregation_rejects_later_failure():
    from output.e2e.platform_scale.benchmark_runner import aggregate_runs

    # A good first repetition must never conceal an incomplete later repetition.
    result = aggregate_runs([{"correctness_verified": True}, {"correctness_verified": False}])
    assert result["correctness_verified"] is False


def test_surviving_fault_blocks_and_preserves_actual_reproducer(monkeypatch, tmp_path):
    import json

    from output.e2e.fault_injection import run_directed_faults as directed

    monkeypatch.setattr(
        directed, "INJECTORS", {"FI-I01": lambda path: directed.generate_healthy_control("CTRL-01", path)}
    )
    assert not directed.run_all_faults(tmp_path)
    row = json.loads((tmp_path / "detector_matrix.json").read_text())["results"]["FI-I01"]
    assert row["status"] == "SURVIVED"
    assert (tmp_path / "incidents/FI-I01/reproducer/bundle/audit.json").is_file()


def test_receipt_rejects_failed_stale_and_changed_during_execution():
    from qa.evidence import receipt_is_current

    receipt = {"exit_code": 0, "source_before": "A", "source_after": "A", "command": ["pytest"]}
    assert receipt_is_current(receipt, "A")
    assert not receipt_is_current(receipt, "B")
    assert not receipt_is_current({**receipt, "exit_code": 1}, "A")
    assert not receipt_is_current({**receipt, "source_after": "B"}, "B")


def test_receipt_fingerprint_ignores_generated_metadata_but_not_product_code(tmp_path):
    from qa.evidence import source_digest

    source = tmp_path / "src/module.py"
    source.parent.mkdir()
    source.write_text("value = 1")
    before = source_digest(tmp_path)
    metadata = tmp_path / "src/product.egg-info/SOURCES.txt"
    metadata.parent.mkdir()
    metadata.write_text("generated during build")
    assert source_digest(tmp_path) == before
    source.write_text("value = 2")
    assert source_digest(tmp_path) != before
    fixture = tmp_path / "output/e2e/import_adversarial/fixtures/input.csv"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("id,amount\nS1,100\n")
    with_fixture = source_digest(tmp_path)
    fixture.write_text("id,amount\nS1,200\n")
    assert source_digest(tmp_path) != with_fixture


def test_import_gate_rejects_empty_missing_duplicated_and_failed_cases():
    from qa.gates import import_cases_passed

    cases = [
        {"test_id": f"{prefix}-{n:02d}", "passed": True, "status": "PASS"}
        for prefix, count in (("CSV", 20), ("XLSX", 18), ("PROV", 6), ("REJ", 10), ("MET", 8))
        for n in range(1, count + 1)
    ]
    assert import_cases_passed(cases)
    assert not import_cases_passed([])
    assert not import_cases_passed(cases[:-1])
    assert not import_cases_passed(cases[:-1] + [cases[0]])
    cases[-1]["passed"] = False
    assert not import_cases_passed(cases)


def test_import_runner_rejects_no_executed_cases(monkeypatch, tmp_path):
    import json
    import sys

    from output.e2e.import_adversarial import test_import_adversarial as runner

    destination = tmp_path / "evidence"
    monkeypatch.setattr(sys, "argv", ["import-runner", "--output-dir", str(destination)])
    for name in (
        "run_5b_csv_tests",
        "run_5c_xlsx_tests",
        "run_5d_provenance_tests",
        "run_5e_safe_rejection_tests",
        "run_5f_metamorphic_tests",
    ):
        monkeypatch.setattr(runner, name, lambda: None)
    assert runner.main() == 2
    report = json.loads((destination / "adversarial_import_results.json").read_text())
    assert report["gate_passed"] is False and report["total_cases"] == 0
