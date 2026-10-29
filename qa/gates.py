"""Fail-closed acceptance of QA evidence (independent of product calculations)."""

import hashlib
import json
from collections import Counter

PIPELINE_STAGES = {
    "1_input_read",
    "2_import",
    "3_normalization",
    "4_audit",
    "5_store_save",
    "6_store_load",
    "7_replay",
    "8_export_json",
    "9_export_xlsx",
    "10_export_html",
    "11_bundle_zip",
    "12_verify_bundle",
    "13_api_retrieval",
}


def platform_passed(report: dict) -> bool:
    cases = report.get("cases", {})
    return set(cases) == {f"WIN-{n:02d}" for n in range(1, 25)} and all(
        case.get("status") == "PASSED" for case in cases.values()
    )


def pipeline_passed(report: dict) -> bool:
    stages = report.get("stages", {})
    return (
        report.get("correctness_verified") is True
        and set(stages) == PIPELINE_STAGES
        and stages.get("12_verify_bundle", {}).get("verified") is True
        and all(stage.get("status", "PASS") == "PASS" for stage in stages.values())
    )


def endurance_passed(report: dict) -> bool:
    return (
        report.get("iterations", 0) >= 10
        and report.get("evaluation") == "STABLE"
        and report.get("fd_leak_detected") is False
        and report.get("restart_verification", {}).get("passed") is True
        and report.get("restart_verification", {}).get("exit_code") == 0
    )


def import_cases_passed(results: list[dict]) -> bool:
    expected = {
        f"{prefix}-{n:02d}"
        for prefix, count in (("CSV", 20), ("XLSX", 18), ("PROV", 6), ("REJ", 10), ("MET", 8))
        for n in range(1, count + 1)
    }
    return (
        len(results) == len(expected)
        and {case.get("test_id") for case in results} == expected
        and all(case.get("passed") is True and case.get("status") == "PASS" for case in results)
    )


def fingerprint_errors(fingerprint: dict) -> list[str]:
    """Reject absent, truncated or ambiguous evidence before comparing it."""
    errors = []
    runs = fingerprint.get("runs")
    if fingerprint.get("schema") != "calibre-platform/v3":
        errors.append("Fingerprint schema must be calibre-platform/v3; regenerate historical evidence")
    if not isinstance(runs, list) or not runs:
        return errors + ["Fingerprint has no runs"]
    encoded = json.dumps(runs, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if hashlib.sha256(encoded.encode()).hexdigest() != fingerprint.get("digest"):
        errors.append("Fingerprint digest mismatch")
    labels = [run.get("dataset_label") for run in runs]
    if any(not label for label in labels) or len(set(labels)) != len(labels):
        errors.append("Missing or duplicate dataset labels")
    identities = fingerprint.get("identities")
    if not isinstance(identities, list) or len(identities) != len(runs):
        return errors + ["Missing actual run identity proofs"]
    proof_labels = [entry.get("dataset_label") for entry in identities]
    if set(proof_labels) != set(labels) or len(set(proof_labels)) != len(proof_labels):
        return errors + ["Missing or duplicate actual identity labels"]
    proofs = {entry["dataset_label"]: entry for entry in identities}

    def hashed(value):
        return hashlib.sha256(
            json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    for run in runs:
        proof = proofs[run["dataset_label"]]
        metadata = proof.get("metadata")
        components = [run.get("snapshot_hash"), run.get("result_hash"), run.get("engine_artifact_hash")]
        if not isinstance(metadata, dict) or metadata.get("run_identity_version") not in {None, 2}:
            errors.append("Missing or unsupported actual identity metadata")
        else:
            actual_components = (
                [*components, hashed(metadata)] if metadata.get("run_identity_version") == 2 else components
            )
            portable_metadata = {key: value for key, value in metadata.items() if key != "python"}
            if hashed(actual_components) != proof.get("run_id"):
                errors.append("Actual metadata-bound run identity mismatch")
            if (
                not run.get("result_hash")
                or portable_metadata != run.get("portable_metadata")
                or hashed([*components, hashed(portable_metadata)]) != run.get("portable_run_id")
            ):
                errors.append("Portable identity or metadata mismatch")
        findings = run.get("findings", [])
        if not findings or not run.get("snapshot_hash") or not run.get("engine_artifact_hash"):
            errors.append("Missing findings, snapshot identity or engine identity")
        ids = [finding.get("id") for finding in findings]
        if any(not identifier for identifier in ids) or len(set(ids)) != len(ids):
            errors.append("Missing or duplicate finding identities")
        if dict(Counter(f.get("status") for f in findings)) != {
            key: value for key, value in run.get("counts", {}).items() if value
        }:
            errors.append("Finding counts do not reconcile")
        if not run.get("currencies"):
            errors.append("Missing currency summaries")
    return errors
