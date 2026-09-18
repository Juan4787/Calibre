#!/usr/bin/env python3
"""Stage-by-stage memory isolation harness for Incident PERF-02.

Profiles exact RSS (before, peak, after) across pipeline stages for
N = [10000, 20000, 30000] to determine the exact components causing
memory amplification in Store.save without executing 100k.
"""

from __future__ import annotations

import gc
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


def get_current_vm_rss_mb() -> float:
    if Path("/proc/self/status").exists():
        for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return round(int(line.split()[1]) / 1024.0, 2)
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 2)


def get_peak_rss_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(usage / 1024.0, 2)


def profile_single_size_worker(n: int, tmp_dir_str: str) -> dict:
    """Runs in an isolated child process to ensure clean initial RSS."""
    from freight_audit.canonical import canonical, digest, load_json
    from freight_audit.engine import audit
    from freight_audit.importing import ImportMapping, import_data
    from freight_audit.models import Agreement, Dataset
    from freight_audit.storage import Store
    from output.e2e.platform_scale.generate_scale_dataset import generate_scale_data

    tmp_dir = Path(tmp_dir_str)
    data_dir = tmp_dir / f"bench_{n}"
    data_dir.mkdir(parents=True, exist_ok=True)
    generate_scale_data(n, data_dir)

    stages = {}

    def record_stage(name: str, fn):
        gc.collect()
        rss_before = get_current_vm_rss_mb()
        t0_wall, t0_cpu = time.perf_counter(), time.process_time()
        res = fn()
        t_wall = time.perf_counter() - t0_wall
        t_cpu = time.process_time() - t0_cpu
        rss_after = get_current_vm_rss_mb()
        peak_rss = get_peak_rss_mb()
        stages[name] = {
            "wall_sec": round(t_wall, 4),
            "cpu_sec": round(t_cpu, 4),
            "rss_before_mb": rss_before,
            "rss_after_mb": rss_after,
            "rss_delta_mb": round(rss_after - rss_before, 2),
            "peak_rss_mb": peak_rss,
        }
        return res

    # 1. Dataset Construction
    def step_dataset():
        charges_bytes = (data_dir / "cargos.csv").read_bytes()
        shipments_bytes = (data_dir / "remitos.csv").read_bytes()
        map_c = ImportMapping.model_validate(load_json((data_dir / "mapping-charges.json").read_bytes()))
        map_s = ImportMapping.model_validate(load_json((data_dir / "mapping-shipments.json").read_bytes()))
        imp_c = import_data(charges_bytes, "cargos.csv", map_c)
        imp_s = import_data(shipments_bytes, "remitos.csv", map_s)
        ds = Dataset(
            label=f"Mem Bench {n}",
            agreements=[Agreement.model_validate(a) for a in load_json((data_dir / "agreements.json").read_bytes())],
            charges=imp_c["records"],
            shipments=imp_s["records"],
            evidence=load_json((data_dir / "evidence.json").read_bytes()),
            documents={imp_c["document"]: "cargos.csv", imp_s["document"]: "remitos.csv"},
        )
        return ds, charges_bytes, shipments_bytes

    dataset, charges_bytes, shipments_bytes = record_stage("1_dataset_built", step_dataset)

    # 2. First Audit
    audit_res1 = record_stage("2_first_audit", lambda: audit(dataset))

    # 3. Canonical Dataset Serialization
    canon_ds = record_stage("3_canonical_dataset", lambda: canonical(dataset))
    stages["3_canonical_dataset"]["string_bytes"] = len(canon_ds.encode("utf-8"))

    # 4. Canonical Result Serialization
    canon_res1 = record_stage("4_canonical_result", lambda: canonical(audit_res1))
    stages["4_canonical_result"]["string_bytes"] = len(canon_res1.encode("utf-8"))

    # 5. Second Audit (Simulating Store.save re-audit)
    audit_res2 = record_stage("5_second_audit_in_memory", lambda: audit(dataset))

    # 6. Canonical Second Audit Serialization
    canon_res2 = record_stage("6_canonical_second_audit", lambda: canonical(audit_res2))
    stages["6_canonical_second_audit"]["string_bytes"] = len(canon_res2.encode("utf-8"))

    # 7. Comparison
    comp_ok = record_stage("7_canonical_comparison", lambda: canon_res1 == canon_res2)
    assert comp_ok

    # 8. SQLite Write
    def step_sqlite_write():
        db_p = tmp_dir / f"profile_{n}.db"
        store = Store(db_p)
        store.put_source(charges_bytes)
        store.put_source(shipments_bytes)
        # Directly insert to measure write step
        run_id = digest([digest(dataset), digest(audit_res1), "test_artifact_hash"])
        with store.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO runs VALUES (?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    digest(dataset),
                    digest(audit_res1),
                    "test_artifact_hash",
                    canon_ds,
                    canon_res1,
                    canonical({}),
                    "2026-09-18T00:00:00Z",
                ),
            )
        return db_p.stat().st_size

    db_size = record_stage("8_sqlite_write", step_sqlite_write)
    stages["8_sqlite_write"]["db_size_bytes"] = db_size

    return {
        "n": n,
        "stages": stages,
        "final_peak_rss_mb": get_peak_rss_mb(),
    }


def main():
    sizes = [10000, 20000, 30000]
    results = {}

    for s in sizes:
        print(f"\n==================================================")
        print(f"Profiling Memory Stages for N = {s} charges...")
        print(f"==================================================")
        with tempfile.TemporaryDirectory() as td:
            # Run in child process for clean glibc malloc arena state
            script = f"""
import json, sys
from pathlib import Path
sys.path.insert(0, '{ROOT}')
sys.path.insert(0, '{ROOT / "src"}')
from output.e2e.platform_scale.profile_perf02_memory import profile_single_size_worker
res = profile_single_size_worker({s}, r'{td}')
print('__RESULT_START__')
print(json.dumps(res))
"""
            proc = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                check=True,
            )
            raw = proc.stdout.split("__RESULT_START__\n")[1].strip()
            data = json.loads(raw)
            results[str(s)] = data

            # Print summary table for this size
            print(f"{'Stage':<30} | {'RSS Before':>10} | {'RSS After':>10} | {'Delta':>8} | {'Peak':>10} | {'Wall (s)':>8}")
            print("-" * 88)
            for st_name, st in data["stages"].items():
                print(f"{st_name:<30} | {st['rss_before_mb']:>9.1f}M | {st['rss_after_mb']:>9.1f}M | {st['rss_delta_mb']:>7.1f}M | {st['peak_rss_mb']:>9.1f}M | {st['wall_sec']:>7.2f}s")
            print(f"\nFinal Peak RSS for N={s}: {data['final_peak_rss_mb']} MB")

    out_file = ROOT / "output/e2e/platform_scale/incidents/PERF-02-STORE-MEMORY-AMPLIFICATION/stage_rss_profile.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nAll stage profiling complete! Saved to: {out_file}")


if __name__ == "__main__":
    main()
