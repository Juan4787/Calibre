#!/usr/bin/env python3
"""Agnostic and independent detector runner for Phase 6 (Fault Injection).

Evaluates artifacts, bundles, runs, and export channels WITHOUT knowledge
of what mutation was injected or which line was altered.
Returns TRUSTED if the artifact satisfies all independent invariants and cross-checks,
or UNTRUSTED with the detailed list of detected violations and estimated severity.
"""

import hashlib
import json
import traceback
from pathlib import Path
from typing import Any

from freight_audit.canonical import bytes_hash, canonical, digest, load_json
from freight_audit.engine import audit
from freight_audit.models import Dataset
from freight_audit.reporting import verify_bundle
from freight_audit.storage import IntegrityError, Store

from qa.invariants import check_run, integrity_errors
from qa.reconcile import reconcile


class DetectorRunner:
    """Agnostic defense orchestrator."""

    def __init__(self):
        pass

    def evaluate_bundle(
        self,
        directory: Path,
        *,
        api_run: dict | None = None,
        observed_ui: dict | None = None,
    ) -> dict[str, Any]:
        """Evaluate a full exported bundle directory across all independent channels."""
        passed_checks = []
        failed_checks = []
        violations = []

        # 1. Manifest & byte-level integrity check
        manifest_path = directory / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = load_json(manifest_path.read_text(encoding="utf-8"))
                for filename, expected_hash in manifest.get("files", {}).items():
                    target = directory / filename
                    if not target.is_file():
                        violations.append({
                            "detector": "manifest_verifier",
                            "check": "missing_file",
                            "message": f"Declarated file missing from bundle: {filename}",
                            "severity": "P0"
                        })
                    else:
                        actual_hash = bytes_hash(target.read_bytes())
                        if actual_hash != expected_hash:
                            violations.append({
                                "detector": "manifest_verifier",
                                "check": "byte_corruption",
                                "message": f"Byte hash differs for {filename}: expected {expected_hash}, got {actual_hash}",
                                "severity": "P0"
                            })
                if not any(v["detector"] == "manifest_verifier" for v in violations):
                    passed_checks.append("manifest_verifier")
                else:
                    failed_checks.append("manifest_verifier")
            except Exception as e:
                failed_checks.append("manifest_verifier")
                violations.append({
                    "detector": "manifest_verifier",
                    "check": "parse_error",
                    "message": f"Failed reading manifest: {e}",
                    "severity": "P0"
                })

        # 2. Invariants check on audit.json
        audit_path = directory / "audit.json"
        run_data = None
        if audit_path.exists():
            try:
                run_data = json.loads(audit_path.read_text(encoding="utf-8"))
                inv_errors = check_run(run_data, require_provenance=True, verify_hashes=True)
                if inv_errors:
                    failed_checks.append("invariants")
                    for err in inv_errors:
                        violations.append({
                            "detector": "invariants",
                            "check": "invariant_violation",
                            "message": err,
                            "severity": "P0" if any(code in err for code in ("INV-04", "INV-05", "INV-06", "INV-07", "INV-08", "INV-28")) else "P1"
                        })
                else:
                    passed_checks.append("invariants")
            except Exception as e:
                failed_checks.append("invariants")
                violations.append({
                    "detector": "invariants",
                    "check": "integrity_error",
                    "message": f"Corrupt audit.json payload: {e}",
                    "severity": "P0"
                })

        # 3. Source provenance check
        if run_data and "snapshot" in run_data:
            prov_passed = True
            sources_dir = directory / "sources"
            for entity in ("shipments", "charges"):
                for item in run_data["snapshot"].get(entity, []):
                    for field, pref in item.get("provenance", {}).items():
                        doc_hash = pref.get("document")
                        if doc_hash and sources_dir.exists():
                            src_file = sources_dir / doc_hash
                            if not src_file.exists():
                                prov_passed = False
                                violations.append({
                                    "detector": "provenance_verifier",
                                    "check": "missing_source",
                                    "message": f"Original source document {doc_hash} missing for {entity} {item.get('id')}",
                                    "severity": "P0"
                                })
            if prov_passed:
                passed_checks.append("provenance_verifier")
            else:
                failed_checks.append("provenance_verifier")

        # 4. Deterministic Replay Check (Re-derive result from snapshot)
        if run_data and "snapshot" in run_data and "result" in run_data:
            try:
                dataset = Dataset.model_validate(run_data["snapshot"])
                replayed_result = audit(dataset).model_dump(mode="json")
                
                # Compare economic findings
                orig_findings = run_data["result"].get("findings", [])
                replayed_findings = replayed_result.get("findings", [])
                
                if len(orig_findings) != len(replayed_findings):
                    failed_checks.append("replay")
                    violations.append({
                        "detector": "replay",
                        "check": "finding_count_mismatch",
                        "message": f"Replayed finding count {len(replayed_findings)} != recorded {len(orig_findings)}",
                        "severity": "P0"
                    })
                else:
                    replay_divergence = False
                    for of, rf in zip(sorted(orig_findings, key=lambda x: x["id"]), sorted(replayed_findings, key=lambda x: x["id"])):
                        if (
                            of.get("status") != rf.get("status")
                            or of.get("actual") != rf.get("actual")
                            or of.get("expected") != rf.get("expected")
                            or of.get("difference") != rf.get("difference")
                            or of.get("confirmed_difference") != rf.get("confirmed_difference")
                            or of.get("currency") != rf.get("currency")
                            or of.get("rule") != rf.get("rule")
                            or of.get("version") != rf.get("version")
                        ):
                            replay_divergence = True
                            violations.append({
                                "detector": "replay",
                                "check": "economic_divergence",
                                "message": f"Replay divergence in finding {of.get('id')}: recorded (status={of.get('status')}, diff={of.get('difference')}, exp={of.get('expected')}) vs replayed (status={rf.get('status')}, diff={rf.get('difference')}, exp={rf.get('expected')})",
                                "severity": "P0"
                            })
                            break
                    if replay_divergence:
                        failed_checks.append("replay")
                    else:
                        passed_checks.append("replay")
            except Exception as e:
                failed_checks.append("replay")
                violations.append({
                    "detector": "replay",
                    "check": "replay_execution_error",
                    "message": f"Replay engine crashed on snapshot: {e}",
                    "severity": "P0"
                })

        # 5. Cross-channel Reconcile (XLSX, HTML, JSON, API, UI)
        try:
            recon_res = reconcile(directory, api_run=api_run, observed_ui=observed_ui)
            recon_errors = recon_res.get("errors", [])
            if recon_errors:
                failed_checks.append("reconcile")
                for re_err in recon_errors:
                    # Filter out duplicates if already in invariants
                    if not any(v["message"] == re_err for v in violations):
                        violations.append({
                            "detector": "reconcile",
                            "check": "cross_channel_divergence",
                            "message": re_err,
                            "severity": "P0" if "material rows differ" in re_err or "XLSX" in re_err or "HTML" in re_err or "UI" in re_err or "API" in re_err else "P1"
                        })
            else:
                passed_checks.append("reconcile")
        except Exception as e:
            failed_checks.append("reconcile")
            violations.append({
                "detector": "reconcile",
                "check": "reconcile_exception",
                "message": f"Reconciler error: {e}",
                "severity": "P0"
            })

        # Determine overall verdict and severity
        is_trusted = len(violations) == 0
        max_severity = "NONE"
        if any(v["severity"] == "P0" for v in violations):
            max_severity = "P0"
        elif any(v["severity"] == "P1" for v in violations):
            max_severity = "P1"
        elif any(v["severity"] == "P2" for v in violations):
            max_severity = "P2"

        return {
            "verdict": "TRUSTED" if is_trusted else "UNTRUSTED",
            "passed_checks": sorted(list(set(passed_checks))),
            "failed_checks": sorted(list(set(failed_checks))),
            "violations": violations,
            "estimated_severity": max_severity,
        }

    def evaluate_run_dict(self, run_dict: dict) -> dict[str, Any]:
        """Evaluate an in-memory run dictionary directly (invariants + replay)."""
        passed_checks = []
        failed_checks = []
        violations = []

        # 1. Invariants
        try:
            inv_errors = check_run(run_dict, require_provenance=True, verify_hashes=True)
            if inv_errors:
                failed_checks.append("invariants")
                for err in inv_errors:
                    violations.append({
                        "detector": "invariants",
                        "check": "invariant_violation",
                        "message": err,
                        "severity": "P0" if any(code in err for code in ("INV-04", "INV-05", "INV-06", "INV-07", "INV-08", "INV-28")) else "P1"
                    })
            else:
                passed_checks.append("invariants")
        except Exception as e:
            failed_checks.append("invariants")
            violations.append({
                "detector": "invariants",
                "check": "integrity_error",
                "message": str(e),
                "severity": "P0"
            })

        # 2. Replay
        if "snapshot" in run_dict and "result" in run_dict:
            try:
                dataset = Dataset.model_validate(run_dict["snapshot"])
                replayed_result = audit(dataset).model_dump(mode="json")
                orig_findings = run_dict["result"].get("findings", [])
                replayed_findings = replayed_result.get("findings", [])
                
                if len(orig_findings) != len(replayed_findings):
                    failed_checks.append("replay")
                    violations.append({
                        "detector": "replay",
                        "check": "finding_count_mismatch",
                        "message": f"Count mismatch: recorded {len(orig_findings)} vs replayed {len(replayed_findings)}",
                        "severity": "P0"
                    })
                else:
                    diff_found = False
                    for of, rf in zip(sorted(orig_findings, key=lambda x: x["id"]), sorted(replayed_findings, key=lambda x: x["id"])):
                        if (
                            of.get("status") != rf.get("status")
                            or of.get("actual") != rf.get("actual")
                            or of.get("expected") != rf.get("expected")
                            or of.get("difference") != rf.get("difference")
                            or of.get("confirmed_difference") != rf.get("confirmed_difference")
                            or of.get("currency") != rf.get("currency")
                            or of.get("rule") != rf.get("rule")
                        ):
                            diff_found = True
                            violations.append({
                                "detector": "replay",
                                "check": "economic_divergence",
                                "message": f"Finding {of.get('id')} divergence: recorded status={of.get('status')} diff={of.get('difference')} vs replayed status={rf.get('status')} diff={rf.get('difference')}",
                                "severity": "P0"
                            })
                            break
                    if diff_found:
                        failed_checks.append("replay")
                    else:
                        passed_checks.append("replay")
            except Exception as e:
                failed_checks.append("replay")
                violations.append({
                    "detector": "replay",
                    "check": "replay_error",
                    "message": str(e),
                    "severity": "P0"
                })

        is_trusted = len(violations) == 0
        max_severity = "NONE"
        if any(v["severity"] == "P0" for v in violations):
            max_severity = "P0"
        elif any(v["severity"] == "P1" for v in violations):
            max_severity = "P1"

        return {
            "verdict": "TRUSTED" if is_trusted else "UNTRUSTED",
            "passed_checks": sorted(list(set(passed_checks))),
            "failed_checks": sorted(list(set(failed_checks))),
            "violations": violations,
            "estimated_severity": max_severity,
        }
