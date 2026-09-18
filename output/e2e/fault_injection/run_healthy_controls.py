#!/usr/bin/env python3
"""Runner for 12 healthy negative controls.

Verifies that legitimate operations, normal variations, restarts, and re-exports
are correctly evaluated as TRUSTED with 0 false positives.
"""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/usuario/CascadeProjects/CALIBRE")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from output.e2e.fault_injection.detector_runner import DetectorRunner
from output.e2e.fault_injection.fault_generator import generate_healthy_control

CONTROLS = [
    ("CTRL-01", "Standard clean baseline run (PASS, FAIL, REVIEW, UNDETERMINABLE)"),
    ("CTRL-02", "Legitimate PASS finding verified"),
    ("CTRL-03", "Legitimate FAIL finding verified"),
    ("CTRL-04", "Legitimate REVIEW finding verified"),
    ("CTRL-05", "Legitimate UNDETERMINABLE finding verified"),
    ("CTRL-06", "Legitimate added evidence and subsequent audit"),
    ("CTRL-07", "Valid contractual version validity window"),
    ("CTRL-08", "Document filename variation with identical content"),
    ("CTRL-09", "Valid reordered columns during import"),
    ("CTRL-10", "Process restart and reload from SQLite DB"),
    ("CTRL-11", "Repeated idempotent export of identical run"),
    ("CTRL-12", "Human decision recorded legitimately and preserved in chain"),
]


def run_all_controls():
    print(f"{'CONTROL ID':<10} | {'STATUS':<10} | {'VERDICT':<10} | {'VIOLATIONS':<10} | {'DESCRIPTION'}")
    print("-" * 90)
    
    results = {}
    false_positives = 0
    
    for cid, desc in CONTROLS:
        with tempfile.TemporaryDirectory(prefix=f"calibre-ctrl-{cid}-") as td:
            target_dir = Path(td)
            try:
                payload = generate_healthy_control(cid, target_dir)
                bundle_dir = payload["bundle_dir"]
                api_run = payload.get("api_run")
                observed_ui = payload.get("observed_ui")
                
                runner = DetectorRunner()
                det_res = runner.evaluate_bundle(bundle_dir, api_run=api_run, observed_ui=observed_ui)
                
                verdict = det_res.get("verdict", "UNKNOWN")
                violations = det_res.get("violations", [])
                
                if verdict == "TRUSTED" and len(violations) == 0:
                    status = "PASS"
                else:
                    status = "FALSE_POSITIVE"
                    false_positives += 1
                    
                results[cid] = {
                    "description": desc,
                    "status": status,
                    "verdict": verdict,
                    "violations": violations,
                    "passed_checks": det_res.get("passed_checks", []),
                }
                
            except Exception as e:
                status = "ERROR"
                false_positives += 1
                results[cid] = {
                    "description": desc,
                    "status": status,
                    "error": str(e),
                }
                verdict = "ERROR"
                violations = [str(e)]
                
            print(f"{cid:<10} | {status:<10} | {verdict:<10} | {len(violations):<10} | {desc[:40]}")
            
    fp_rate = (false_positives / len(CONTROLS)) * 100
    print("\n" + "=" * 90)
    print(f"Total Controls: {len(CONTROLS)} | Passed: {len(CONTROLS) - false_positives} | False Positives: {false_positives} | FP Rate: {fp_rate:.1f}%")
    
    out_path = ROOT / "output/e2e/fault_injection/false_positive_results.json"
    out_path.write_text(json.dumps({
        "total_controls": len(CONTROLS),
        "passed": len(CONTROLS) - false_positives,
        "false_positives": false_positives,
        "false_positive_rate": fp_rate,
        "details": results
    }, indent=2), encoding="utf-8")
    print(f"Results written to {out_path}")
    return false_positives == 0


if __name__ == "__main__":
    success = run_all_controls()
    sys.exit(0 if success else 1)
