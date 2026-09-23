#!/usr/bin/env python3
"""Endurance and Stability Runner for Calibre Freight Audit (Subfase 9R).

Executes 50 consecutive full-pipeline audits in a single process.
Tracks RSS, open file descriptors, temporary files, DB size, and iteration wall clock time.
Verifies post-campaign clean process restart and persistence replay integrity.
Outputs results.json and resource_curve.json.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import resource
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from freight_audit.canonical import canonical, digest, load_json
from freight_audit.engine import audit
from freight_audit.importing import ImportMapping, import_data
from freight_audit.models import Agreement, Dataset
from freight_audit.reporting import bundle_bytes, verify_bundle
from freight_audit.storage import Store
from output.e2e.platform_scale.generate_scale_dataset import generate_scale_data


def get_current_rss_mb() -> float:
    # Read VmRSS directly from /proc/self/status for real-time memory tracking on Linux
    if Path("/proc/self/status").exists():
        for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return round(int(line.split()[1]) / 1024.0, 2)
    # Fallback to getrusage
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 2)


def count_open_fds() -> int:
    fd_dir = Path("/proc/self/fd")
    if fd_dir.exists():
        try:
            return len(list(fd_dir.iterdir()))
        except Exception:
            return -1
    return -1


def count_temp_files() -> int:
    tmp = Path(tempfile.gettempdir())
    try:
        return len(list(tmp.iterdir()))
    except Exception:
        return 0


def run_endurance_campaign(iterations: int, batch_size: int, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"=================================================================")
    print(f"STARTING ENDURANCE CAMPAIGN: {iterations} iterations ({batch_size} charges/iter)")
    print(f"=================================================================")

    # Prepare generator template dataset
    temp_gen_dir = out_dir / "template_data"
    oracle = generate_scale_data(batch_size, temp_gen_dir)

    agreements_bytes = (temp_gen_dir / "agreements.json").read_bytes()
    map_c_bytes = (temp_gen_dir / "mapping-charges.json").read_bytes()
    map_s_bytes = (temp_gen_dir / "mapping-shipments.json").read_bytes()
    charges_bytes = (temp_gen_dir / "cargos.csv").read_bytes()
    shipments_bytes = (temp_gen_dir / "remitos.csv").read_bytes()
    evidence_bytes = (temp_gen_dir / "evidence.json").read_bytes()

    db_path = out_dir / "endurance_store.db"
    if db_path.exists():
        db_path.unlink()
    store = Store(db_path)
    store.put_source(charges_bytes)
    store.put_source(shipments_bytes)

    curve_records = []
    initial_rss = get_current_rss_mb()
    initial_fds = count_open_fds()
    last_run_id = None

    for i in range(1, iterations + 1):
        t0 = time.perf_counter()

        # Import
        map_c = ImportMapping.model_validate(load_json(map_c_bytes))
        map_s = ImportMapping.model_validate(load_json(map_s_bytes))
        imp_c = import_data(charges_bytes, f"cargos_{i}.csv", map_c)
        imp_s = import_data(shipments_bytes, f"remitos_{i}.csv", map_s)

        # Dataset & Audit
        agreements = [Agreement.model_validate(a) for a in load_json(agreements_bytes)]
        evidence = load_json(evidence_bytes)
        dataset = Dataset(
            label=f"Endurance Run {i}",
            agreements=agreements,
            charges=imp_c["records"],
            shipments=imp_s["records"],
            evidence=evidence,
            documents={
                imp_c["document"]: f"cargos_{i}.csv",
                imp_s["document"]: f"remitos_{i}.csv",
            },
        )
        res = audit(dataset)

        # Store save & load
        run_id = store.save(dataset, res)
        last_run_id = run_id
        loaded = store.load(run_id)

        # Bundle & verify
        zip_data = bundle_bytes(store, run_id)
        verified = verify_bundle(zip_data)
        assert verified["id"] == run_id

        # Replay
        replayed_res = audit(Dataset.model_validate(loaded["snapshot"]))
        assert canonical(replayed_res) == canonical(res)

        wall_time = round(time.perf_counter() - t0, 4)
        current_rss = get_current_rss_mb()
        current_fds = count_open_fds()
        current_temps = count_temp_files()
        db_size = db_path.stat().st_size

        rec = {
            "iteration": i,
            "wall_sec": wall_time,
            "rss_mb": current_rss,
            "open_fds": current_fds,
            "temp_files": current_temps,
            "db_size_bytes": db_size,
        }
        curve_records.append(rec)

        if i % 5 == 0 or i == 1 or i == iterations:
            print(
                f"  Iter {i:02d}/{iterations:02d} | "
                f"Wall: {wall_time:.3f}s | "
                f"RSS: {current_rss:.1f} MB | "
                f"FDs: {current_fds} | "
                f"DB: {round(db_size / (1024*1024), 2)} MB"
            )

    final_rss = get_current_rss_mb()
    final_fds = count_open_fds()
    peak_rss = max(r["rss_mb"] for r in curve_records)

    first_5_times = [r["wall_sec"] for r in curve_records[:5]]
    last_5_times = [r["wall_sec"] for r in curve_records[-5:]]
    med_first_5 = statistics.median(first_5_times)
    med_last_5 = statistics.median(last_5_times)
    time_degradation_ratio = round(med_last_5 / max(med_first_5, 0.001), 2)

    # Classification logic
    # Stable if:
    # 1. RSS does not grow unboundedly (peak within 25% of stabilized iter 10)
    # 2. Open FDs do not continuously increase
    # 3. No progressive degradation (time degradation ratio <= 1.5x)
    iter_10_rss = curve_records[min(9, len(curve_records)-1)]["rss_mb"]
    rss_growth_post_10 = (final_rss - iter_10_rss) / max(iter_10_rss, 1.0)
    fd_diff = final_fds - initial_fds

    if fd_diff <= 3 and rss_growth_post_10 < 0.15 and time_degradation_ratio < 1.4:
        evaluation = "STABLE"
    elif rss_growth_post_10 >= 0.5 or fd_diff > 10:
        evaluation = "LEAK-LIKE"
    elif rss_growth_post_10 >= 0.2:
        evaluation = "SUSPICIOUS"
    else:
        evaluation = "INCONCLUSIVE"

    # Step 6.3: Clean Process Restart Verification
    print("\nExecuting process restart and database reopen verification...")
    restart_script = f"""
import sys
from pathlib import Path
sys.path.insert(0, '{ROOT}')
sys.path.insert(0, '{ROOT}/src')
from freight_audit.storage import Store
from freight_audit.engine import audit
from freight_audit.models import Dataset
from freight_audit.canonical import canonical

store = Store(Path(r'{db_path}'))
run = store.load('{last_run_id}')
snapshot = Dataset.model_validate(run['snapshot'])
result = audit(snapshot)
assert canonical(result) == canonical(run['result']), 'Replay identity mismatch post-restart!'
print('RESTART_REPLAY_SUCCESS')
"""
    proc = subprocess.run(
        [sys.executable, "-c", restart_script],
        capture_output=True,
        text=True,
    )
    restart_ok = proc.returncode == 0 and "RESTART_REPLAY_SUCCESS" in proc.stdout

    summary = {
        "iterations": iterations,
        "batch_size": batch_size,
        "initial_rss_mb": initial_rss,
        "final_rss_mb": final_rss,
        "peak_rss_mb": peak_rss,
        "initial_fds": initial_fds,
        "final_fds": final_fds,
        "fd_leak_detected": fd_diff > 3,
        "first_5_median_sec": round(med_first_5, 4),
        "last_5_median_sec": round(med_last_5, 4),
        "time_degradation_ratio": time_degradation_ratio,
        "evaluation": evaluation,
        "restart_verification": {
            "passed": restart_ok,
            "last_run_id": last_run_id,
            "exit_code": proc.returncode,
        },
    }

    (out_dir / "results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "resource_curve.json").write_text(json.dumps(curve_records, indent=2), encoding="utf-8")

    print(f"\nEndurance evaluation: {evaluation}")
    print(f"Initial RSS: {initial_rss} MB -> Final RSS: {final_rss} MB (Peak: {peak_rss} MB)")
    print(f"FDs: {initial_fds} -> {final_fds}")
    print(f"Time: {med_first_5:.3f}s -> {med_last_5:.3f}s (Ratio: {time_degradation_ratio}x)")
    print(f"Process restart replay: {'PASSED' if restart_ok else 'FAILED'}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Calibre Endurance Runner")
    parser.add_argument("--iterations", type=int, default=50, help="Number of consecutive iterations")
    parser.add_argument("--batch-size", type=int, default=1000, help="Charges per iteration")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/e2e/platform_scale/endurance")
    args = parser.parse_args()

    from qa.gates import endurance_passed
    if args.iterations < 10 or args.batch_size < 1:
        parser.error("Require at least 10 iterations and a positive batch size")
    summary = run_endurance_campaign(args.iterations, args.batch_size, args.output_dir)
    sys.exit(0 if endurance_passed(summary) else 1)


if __name__ == "__main__":
    main()
