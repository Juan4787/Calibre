#!/usr/bin/env python3
"""Runner for Subphase 6G (Blind Faults).

Generates 10 blind faults stripped of identifiers and evaluates them agnostically.
Only reveals the secret key AFTER evaluation to assess blind detection efficacy.
"""

import json
import sys
from pathlib import Path

ROOT = Path("/home/usuario/CascadeProjects/CALIBRE")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from output.e2e.fault_injection.detector_runner import DetectorRunner
from output.e2e.fault_injection.fault_generator import generate_blind_faults


def run_blind_suite():
    blind_dir = ROOT / "output/e2e/fault_injection/blind"
    print("1. Generating 10 blind faults (metadata stripped)...")
    secret_key = generate_blind_faults(blind_dir)
    print(f"   Generated {len(secret_key)} blind cases. Secret key secured.")
    
    print("\n2. Executing Agnostic Detection Evaluation (Zero metadata knowledge)...")
    print(f"{'BLIND ID':<10} | {'VERDICT':<12} | {'FAILED CHECKS':<30} | {'VIOLATIONS':<10} | {'EST. SEVERITY'}")
    print("-" * 80)
    
    eval_results = {}
    runner = DetectorRunner()
    
    for idx in range(1, 11):
        blind_id = f"BLIND-{idx:02d}"
        case_dir = blind_dir / blind_id
        bundle_dir = case_dir / "bundle"
        
        api_run = None
        api_path = case_dir / "api_run.json"
        if api_path.exists():
            api_run = json.loads(api_path.read_text(encoding="utf-8"))
            
        observed_ui = None
        ui_path = case_dir / "observed_ui.json"
        if ui_path.exists():
            observed_ui = json.loads(ui_path.read_text(encoding="utf-8"))
            
        # Agnostic evaluation
        res = runner.evaluate_bundle(bundle_dir, api_run=api_run, observed_ui=observed_ui)
        
        verdict = res["verdict"]
        failed = res["failed_checks"]
        violations = res["violations"]
        
        # Estimate severity
        est_sev = "P0" if any(v.get("severity") == "P0" for v in violations) else ("P1" if violations else "NONE")
        
        eval_results[blind_id] = {
            "verdict": verdict,
            "failed_checks": failed,
            "violations_count": len(violations),
            "estimated_severity": est_sev,
            "sample_violation": violations[0]["message"] if violations else "None",
            "full_violations": violations,
        }
        
        failed_str = ", ".join(failed) if failed else "NONE"
        print(f"{blind_id:<10} | {verdict:<12} | {failed_str[:28]:<30} | {len(violations):<10} | {est_sev}")
        
    print("\n3. Unveiling Secret Key and Cross-Verifying Blind Detection...")
    print(f"{'BLIND ID':<10} | {'ACTUAL FAULT':<12} | {'VERDICT':<10} | {'DETECTED?':<10} | {'MATCHING DEFENSE'}")
    print("-" * 80)
    
    blind_detected = 0
    final_blind_report = {}
    
    for blind_id, actual_fault in secret_key.items():
        eval_info = eval_results[blind_id]
        is_detected = eval_info["verdict"] == "UNTRUSTED"
        if is_detected:
            blind_detected += 1
            
        matched_defense = ", ".join(eval_info["failed_checks"]) if eval_info["failed_checks"] else "NONE"
        
        final_blind_report[blind_id] = {
            "actual_fault": actual_fault,
            "verdict": eval_info["verdict"],
            "detected": is_detected,
            "matching_defense": eval_info["failed_checks"],
            "estimated_severity": eval_info["estimated_severity"],
            "sample_violation": eval_info["sample_violation"],
        }
        
        detected_str = "YES" if is_detected else "NO (SURVIVED)"
        print(f"{blind_id:<10} | {actual_fault:<12} | {eval_info['verdict']:<10} | {detected_str:<10} | {matched_defense}")
        
    blind_rate = (blind_detected / len(secret_key)) * 100
    print("\n" + "=" * 80)
    print(f"Total Blind Cases: {len(secret_key)} | Detected: {blind_detected} | Blind Detection Rate: {blind_rate:.1f}%")
    
    out_path = blind_dir / "blind_evaluation_results.json"
    out_path.write_text(json.dumps({
        "total_cases": len(secret_key),
        "detected": blind_detected,
        "blind_detection_rate": blind_rate,
        "cases": final_blind_report
    }, indent=2), encoding="utf-8")
    print(f"Blind results saved to {out_path}")
    return blind_detected == len(secret_key)


if __name__ == "__main__":
    success = run_blind_suite()
    sys.exit(0 if success else 1)
