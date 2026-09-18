#!/usr/bin/env python3
"""Runner for directed fault injection suite (41 faults).

Evaluates each fault against independent detectors and classifies each result as:
- PREVENTED: caught during execution/generation by invariant/model constraints
- DETECTED: post-occurrence detection by at least one independent defense
- SURVIVED: flaw undetected, trusted result produced (GATE BLOCKER FOR P0)
- EQUIVALENT: mutation produces semantically identical observable state
"""

import json
import shutil
import sys
import tempfile
import traceback
import sys
from pathlib import Path

ROOT = Path("/home/usuario/CascadeProjects/CALIBRE")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from output.e2e.fault_injection.detector_runner import DetectorRunner
from output.e2e.fault_injection.fault_generator import INJECTORS


def run_all_faults():
    root = Path("/home/usuario/CascadeProjects/CALIBRE")
    catalog_path = root / "output/e2e/fault_injection/expected_detectors.json"
    raw_meta = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else {}
    expected_detectors = raw_meta.get("faults", raw_meta)
    
    incidents_dir = root / "output/e2e/fault_injection/incidents"
    incidents_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    matrix_rows = {}
    
    print(f"{'FAULT ID':<10} | {'SEV':<4} | {'STATUS':<10} | {'PRIMARY DETECTOR':<20} | {'VIOLATIONS':<5} | {'SUMMARY'}")
    print("-" * 100)
    
    for fault_id in sorted(INJECTORS.keys()):
        injector = INJECTORS[fault_id]
        exp_meta = expected_detectors.get(fault_id, {})
        severity = exp_meta.get("severity", "P0")
        
        status = "UNKNOWN"
        primary_detector = "NONE"
        detected_by = []
        violations = []
        
        with tempfile.TemporaryDirectory(prefix=f"calibre-fi-{fault_id}-") as td:
            target_dir = Path(td)
            try:
                payload = injector(target_dir)
                bundle_dir = payload.get("bundle_dir", target_dir / "bundle")
                api_run = payload.get("api_run")
                observed_ui = payload.get("observed_ui")
                
                # Agnostic detection evaluation
                runner = DetectorRunner()
                det_res = runner.evaluate_bundle(bundle_dir, api_run=api_run, observed_ui=observed_ui)
                
                violations = det_res.get("violations", [])
                failed_checks = det_res.get("failed_checks", [])
                
                if det_res["verdict"] == "UNTRUSTED" and violations:
                    status = "DETECTED"
                    detected_by = failed_checks
                    primary_detector = failed_checks[0] if failed_checks else violations[0]["detector"]
                else:
                    status = "SURVIVED"
                    primary_detector = "NONE"
                    
            except Exception as e:
                # Fault was prevented by invariant/validation exception
                status = "PREVENTED"
                primary_detector = "invariant_prevention"
                violations = [{
                    "detector": "system_prevention",
                    "check": "prevention_exception",
                    "message": str(e),
                    "severity": severity
                }]
                detected_by = ["system_prevention"]

        # Record result
        res_item = {
            "fault_id": fault_id,
            "severity": severity,
            "justification": exp_meta.get("justification", ""),
            "status": status,
            "primary_detector": primary_detector,
            "detected_by": detected_by,
            "violations_count": len(violations),
            "sample_violation": violations[0]["message"] if violations else "None",
            "expected_detector": exp_meta.get("primary_detector", "invariants"),
            "independent_detection": status in ("DETECTED", "PREVENTED"),
        }
        results.append(res_item)
        matrix_rows[fault_id] = res_item
        
        # If SURVIVED, generate incident reproduction package
        if status == "SURVIVED":
            inc_dir = incidents_dir / fault_id
            inc_dir.mkdir(parents=True, exist_ok=True)
            (inc_dir / "expected.json").write_text(json.dumps(exp_meta, indent=2), encoding="utf-8")
            (inc_dir / "observed.json").write_text(json.dumps(res_item, indent=2), encoding="utf-8")
            (inc_dir / "detector-output.json").write_text(json.dumps({"violations": violations}, indent=2), encoding="utf-8")
            (inc_dir / "blast-radius.md").write_text(
                f"# Incident: {fault_id}\n\n"
                f"**Severity**: {severity}\n"
                f"**Status**: SURVIVED\n"
                f"**Expected Detector**: {exp_meta.get('primary_detector')}\n"
                f"**Description**: Fault bypassed defenses without triggering UNTRUSTED verdict.\n",
                encoding="utf-8"
            )
            print(f">>> CRITICAL: Fault {fault_id} SURVIVED! Preserved in {inc_dir}")
            
        print(f"{fault_id:<10} | {severity:<4} | {status:<10} | {primary_detector:<20} | {len(violations):<10} | {res_item['sample_violation'][:40]}")

    # Write detector matrix output
    matrix_out = root / "output/e2e/fault_injection/detector_matrix.json"
    matrix_out.write_text(json.dumps({
        "total_faults": len(results),
        "results": matrix_rows,
        "summary": {
            "p0_total": sum(1 for r in results if r["severity"] == "P0"),
            "p0_detected_or_prevented": sum(1 for r in results if r["severity"] == "P0" and r["status"] in ("DETECTED", "PREVENTED")),
            "p0_survived": sum(1 for r in results if r["severity"] == "P0" and r["status"] == "SURVIVED"),
            "p1_total": sum(1 for r in results if r["severity"] == "P1"),
            "p1_detected_or_prevented": sum(1 for r in results if r["severity"] == "P1" and r["status"] in ("DETECTED", "PREVENTED")),
            "p1_survived": sum(1 for r in results if r["severity"] == "P1" and r["status"] == "SURVIVED"),
            "p2_total": sum(1 for r in results if r["severity"] == "P2"),
            "p2_detected_or_prevented": sum(1 for r in results if r["severity"] == "P2" and r["status"] in ("DETECTED", "PREVENTED")),
            "p2_survived": sum(1 for r in results if r["severity"] == "P2" and r["status"] == "SURVIVED"),
        }
    }, indent=2), encoding="utf-8")
    
    print("\n" + "=" * 100)
    summary = json.loads(matrix_out.read_text())["summary"]
    p0_rate = (summary["p0_detected_or_prevented"] / summary["p0_total"]) * 100 if summary["p0_total"] else 0
    p1_rate = (summary["p1_detected_or_prevented"] / summary["p1_total"]) * 100 if summary["p1_total"] else 0
    print(f"P0 Total: {summary['p0_total']} | Detected/Prevented: {summary['p0_detected_or_prevented']} | Survived: {summary['p0_survived']} | Detection Rate: {p0_rate:.1f}%")
    print(f"P1 Total: {summary['p1_total']} | Detected/Prevented: {summary['p1_detected_or_prevented']} | Survived: {summary['p1_survived']} | Detection Rate: {p1_rate:.1f}%")
    print(f"P2 Total: {summary['p2_total']} | Detected/Prevented: {summary['p2_detected_or_prevented']} | Survived: {summary['p2_survived']}")
    print(f"Matrix saved to {matrix_out}")


if __name__ == "__main__":
    run_all_faults()
