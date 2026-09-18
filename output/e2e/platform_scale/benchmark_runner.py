#!/usr/bin/env python3
"""Platform & Scale Benchmark Runner for Calibre Freight Audit.

Executes rigorous performance benchmarks, scalability curves, and complexity stress tests.
Measures wall clock, CPU time, peak RSS, artifact sizes, and throughput per pipeline stage.
Validates 100% semantic correctness and mathematical invariants against independent oracles.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import resource
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from decimal import Decimal
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
from freight_audit.reporting import (
    bundle_bytes,
    html_report,
    verify_bundle,
    workbook_bytes,
)
from freight_audit.server import create_app
from freight_audit.storage import Store
from fastapi.testclient import TestClient

from output.e2e.platform_scale.generate_scale_dataset import generate_scale_data


def get_environment_info() -> dict:
    cpu_model = "Unknown"
    cpu_count = os.cpu_count() or 1
    mem_total_kb = 0

    if Path("/proc/cpuinfo").exists():
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break

    if Path("/proc/meminfo").exists():
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                mem_total_kb = int(line.split()[1])
                break

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        git_status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        git_commit = "unknown"
        git_status = "unknown"

    fs_type = "unknown"
    try:
        df_out = subprocess.check_output(["df", "-T", str(ROOT)], text=True).splitlines()
        if len(df_out) >= 2:
            fs_type = df_out[1].split()[1]
    except Exception:
        pass

    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "cpu_model": cpu_model,
        "cpu_count": cpu_count,
        "mem_total_mb": round(mem_total_kb / 1024.0, 2),
        "python_version": platform.python_version(),
        "sqlite_version": sqlite3.sqlite_version,
        "filesystem": fs_type,
        "git_commit": git_commit,
        "git_clean": git_status == "",
        "rss_unit": "kilobytes" if platform.system() == "Linux" else "bytes",
    }


def get_peak_rss_mb() -> float:
    # On Linux, ru_maxrss is in kilobytes
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == "Linux":
        return round(usage / 1024.0, 2)
    return round(usage / (1024.0 * 1024.0), 2)


def run_single_pipeline_benchmark(data_dir: Path, oracle: dict) -> dict:
    """Executes full pipeline and measures each stage separately."""
    gc.collect()
    start_rss = get_peak_rss_mb()
    metrics = {}

    # 1. Read Inputs
    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    agreements_bytes = (data_dir / "agreements.json").read_bytes()
    map_c_bytes = (data_dir / "mapping-charges.json").read_bytes()
    map_s_bytes = (data_dir / "mapping-shipments.json").read_bytes()
    charges_bytes = (data_dir / "cargos.csv").read_bytes()
    shipments_bytes = (data_dir / "remitos.csv").read_bytes()
    evidence_bytes = (data_dir / "evidence.json").read_bytes()
    t_read_wall = time.perf_counter() - t0_wall
    t_read_cpu = time.process_time() - t0_cpu

    metrics["1_input_read"] = {
        "wall_sec": t_read_wall,
        "cpu_sec": t_read_cpu,
        "peak_rss_mb": get_peak_rss_mb(),
    }

    # 2. Import
    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    map_c = ImportMapping.model_validate(load_json(map_c_bytes))
    map_s = ImportMapping.model_validate(load_json(map_s_bytes))
    imp_c = import_data(charges_bytes, "cargos.csv", map_c)
    imp_s = import_data(shipments_bytes, "remitos.csv", map_s)
    charges_records = imp_c["records"]
    shipments_records = imp_s["records"]
    t_import_wall = time.perf_counter() - t0_wall
    t_import_cpu = time.process_time() - t0_cpu

    metrics["2_import"] = {
        "wall_sec": t_import_wall,
        "cpu_sec": t_import_cpu,
        "peak_rss_mb": get_peak_rss_mb(),
        "charges_imported": len(charges_records),
        "shipments_imported": len(shipments_records),
    }

    # 3. Normalization (Dataset model validation)
    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    agreements = [Agreement.model_validate(a) for a in load_json(agreements_bytes)]
    evidence = load_json(evidence_bytes)
    dataset = Dataset(
        label=f"Scale Bench {len(charges_records)}",
        agreements=agreements,
        charges=charges_records,
        shipments=shipments_records,
        evidence=evidence,
        documents={
            imp_c["document"]: "cargos.csv",
            imp_s["document"]: "remitos.csv",
        },
    )
    t_norm_wall = time.perf_counter() - t0_wall
    t_norm_cpu = time.process_time() - t0_cpu

    metrics["3_normalization"] = {
        "wall_sec": t_norm_wall,
        "cpu_sec": t_norm_cpu,
        "peak_rss_mb": get_peak_rss_mb(),
    }

    # 4. Engine Audit
    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    audit_res = audit(dataset)
    t_audit_wall = time.perf_counter() - t0_wall
    t_audit_cpu = time.process_time() - t0_cpu

    metrics["4_audit"] = {
        "wall_sec": t_audit_wall,
        "cpu_sec": t_audit_cpu,
        "peak_rss_mb": get_peak_rss_mb(),
        "charges_per_sec": round(len(charges_records) / max(t_audit_wall, 0.0001), 2),
        "findings_per_sec": round(len(audit_res.findings) / max(t_audit_wall, 0.0001), 2),
    }

    # 5. Store.save
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "bench.db"
        store = Store(db_path)
        store.put_source(charges_bytes)
        store.put_source(shipments_bytes)

        t0_wall, t0_cpu = time.perf_counter(), time.process_time()
        run_id = store.save(dataset, audit_res)
        del dataset
        gc.collect()
        t_save_wall = time.perf_counter() - t0_wall
        t_save_cpu = time.process_time() - t0_cpu
        db_size = db_path.stat().st_size

        metrics["5_store_save"] = {
            "wall_sec": t_save_wall,
            "cpu_sec": t_save_cpu,
            "db_size_bytes": db_size,
            "peak_rss_mb": get_peak_rss_mb(),
        }

        # 6. Store.load
        t0_wall, t0_cpu = time.perf_counter(), time.process_time()
        run = store.load(run_id)
        t_load_wall = time.perf_counter() - t0_wall
        t_load_cpu = time.process_time() - t0_cpu

        metrics["6_store_load"] = {
            "wall_sec": t_load_wall,
            "cpu_sec": t_load_cpu,
            "peak_rss_mb": get_peak_rss_mb(),
        }

        # 7. Replay
        t0_wall, t0_cpu = time.perf_counter(), time.process_time()
        replayed_d = Dataset.model_validate(run["snapshot"])
        replayed_res = audit(replayed_d)
        replay_ok = canonical(replayed_res) == canonical(audit_res)
        t_replay_wall = time.perf_counter() - t0_wall
        t_replay_cpu = time.process_time() - t0_cpu

        assert replay_ok, "Replay divergence detected!"
        metrics["7_replay"] = {
            "wall_sec": t_replay_wall,
            "cpu_sec": t_replay_cpu,
            "identical": replay_ok,
            "peak_rss_mb": get_peak_rss_mb(),
        }
        del replayed_d, replayed_res
        gc.collect()

        # 8. Export JSON
        t0_wall, t0_cpu = time.perf_counter(), time.process_time()
        json_bytes_data = canonical(run).encode("utf-8")
        t_json_wall = time.perf_counter() - t0_wall
        t_json_cpu = time.process_time() - t0_cpu
        sz_json = len(json_bytes_data)
        del json_bytes_data
        gc.collect()

        metrics["8_export_json"] = {
            "wall_sec": t_json_wall,
            "cpu_sec": t_json_cpu,
            "size_bytes": sz_json,
            "peak_rss_mb": get_peak_rss_mb(),
        }

        # 9. Export XLSX
        if len(charges_records) <= 2000:
            t0_wall, t0_cpu = time.perf_counter(), time.process_time()
            xlsx_bytes = workbook_bytes(run)
            t_xlsx_wall = time.perf_counter() - t0_wall
            t_xlsx_cpu = time.process_time() - t0_cpu

            metrics["9_export_xlsx"] = {
                "wall_sec": t_xlsx_wall,
                "cpu_sec": t_xlsx_cpu,
                "size_bytes": len(xlsx_bytes),
                "peak_rss_mb": get_peak_rss_mb(),
            }
        else:
            metrics["9_export_xlsx"] = {
                "wall_sec": None,
                "cpu_sec": None,
                "status": "BOUNDED_BY_INCIDENT_PERF_01",
                "note": "Documented in output/e2e/platform_scale/incidents/PERF-01-XLSX-QUADRATIC",
                "peak_rss_mb": get_peak_rss_mb(),
            }

        # 10. Export HTML
        t0_wall, t0_cpu = time.perf_counter(), time.process_time()
        html_content = html_report(run).encode("utf-8")
        t_html_wall = time.perf_counter() - t0_wall
        t_html_cpu = time.process_time() - t0_cpu
        sz_html = len(html_content)
        del html_content
        gc.collect()

        metrics["10_export_html"] = {
            "wall_sec": t_html_wall,
            "cpu_sec": t_html_cpu,
            "size_bytes": sz_html,
            "peak_rss_mb": get_peak_rss_mb(),
        }

        # 11. Bundle ZIP
        if len(charges_records) <= 2000:
            t0_wall, t0_cpu = time.perf_counter(), time.process_time()
            zip_bytes = bundle_bytes(store, run_id)
            t_zip_wall = time.perf_counter() - t0_wall
            t_zip_cpu = time.process_time() - t0_cpu

            metrics["11_bundle_zip"] = {
                "wall_sec": t_zip_wall,
                "cpu_sec": t_zip_cpu,
                "size_bytes": len(zip_bytes),
                "peak_rss_mb": get_peak_rss_mb(),
            }

            # 12. Verify Bundle
            t0_wall, t0_cpu = time.perf_counter(), time.process_time()
            verified_run = verify_bundle(zip_bytes)
            verify_ok = verified_run["id"] == run_id
            t_verify_wall = time.perf_counter() - t0_wall
            t_verify_cpu = time.process_time() - t0_cpu

            assert verify_ok, "Bundle verification failed!"
            metrics["12_verify_bundle"] = {
                "wall_sec": t_verify_wall,
                "cpu_sec": t_verify_cpu,
                "verified": verify_ok,
                "peak_rss_mb": get_peak_rss_mb(),
            }
        else:
            metrics["11_bundle_zip"] = {
                "wall_sec": None,
                "cpu_sec": None,
                "status": "BOUNDED_BY_INCIDENT_PERF_01",
                "note": "Depends on workbook_bytes()",
                "peak_rss_mb": get_peak_rss_mb(),
            }
            metrics["12_verify_bundle"] = {
                "wall_sec": None,
                "cpu_sec": None,
                "status": "BOUNDED_BY_INCIDENT_PERF_01",
                "peak_rss_mb": get_peak_rss_mb(),
            }

        # 13. API retrieval
        t0_wall, t0_cpu = time.perf_counter(), time.process_time()
        app = create_app(db_path)
        with TestClient(app) as client:
            sess = client.get("/api/session").json()
            client.headers["X-Freight-Local"] = sess["token"]
            api_resp = client.get(f"/api/runs/{run_id}")
            assert api_resp.status_code == 200
        t_api_wall = time.perf_counter() - t0_wall
        t_api_cpu = time.process_time() - t0_cpu
        del app
        gc.collect()

        metrics["13_api_retrieval"] = {
            "wall_sec": t_api_wall,
            "cpu_sec": t_api_cpu,
            "peak_rss_mb": get_peak_rss_mb(),
        }

    # Verify Correctness against Mathematical Oracle
    assert len(audit_res.findings) == oracle["total_findings"], (
        f"Findings count mismatch: {len(audit_res.findings)} vs {oracle['total_findings']}"
    )
    assert audit_res.summary["counts"] == oracle["counts"], (
        f"Counts mismatch: {audit_res.summary['counts']} vs {oracle['counts']}"
    )

    for curr in ("ARS", "USD"):
        s = audit_res.summary["currencies"][curr]
        o = oracle["currencies"][curr]
        for k in (
            "actual",
            "confirmed_overcharge",
            "confirmed_undercharge",
            "confirmed_net_difference",
            "pass",
            "review",
            "undeterminable",
            "determinable",
        ):
            assert Decimal(str(s[k])) == Decimal(str(o[k])), (
                f"Mismatch in {curr} field {k}: actual={s[k]} vs oracle={o[k]}"
            )

    total_wall = sum(m["wall_sec"] for m in metrics.values() if m.get("wall_sec") is not None)
    total_cpu = sum(m["cpu_sec"] for m in metrics.values() if m.get("cpu_sec") is not None)

    return {
        "stages": metrics,
        "total_wall_sec": total_wall,
        "total_cpu_sec": total_cpu,
        "peak_rss_mb": get_peak_rss_mb(),
        "correctness_verified": True,
    }


def aggregate_runs(runs: list[dict]) -> dict:
    """Computes median, min, max, mean, stdev, p95 across repeated runs."""
    agg = {}
    stage_keys = list(runs[0]["stages"].keys())

    for stage in stage_keys:
        wall_times = [r["stages"][stage]["wall_sec"] for r in runs if r["stages"][stage].get("wall_sec") is not None]
        cpu_times = [r["stages"][stage]["cpu_sec"] for r in runs if r["stages"][stage].get("cpu_sec") is not None]
        rss_vals = [r["stages"][stage]["peak_rss_mb"] for r in runs]

        if wall_times:
            st_data = {
                "wall": {
                    "median": round(statistics.median(wall_times), 4),
                    "min": round(min(wall_times), 4),
                    "max": round(max(wall_times), 4),
                    "mean": round(statistics.mean(wall_times), 4),
                    "stdev": round(statistics.stdev(wall_times), 4) if len(wall_times) > 1 else 0.0,
                },
                "cpu": {
                    "median": round(statistics.median(cpu_times), 4),
                    "min": round(min(cpu_times), 4),
                    "max": round(max(cpu_times), 4),
                    "mean": round(statistics.mean(cpu_times), 4),
                },
                "peak_rss_mb": max(rss_vals),
            }
        else:
            st_data = {
                "wall": {"median": "BOUNDED_BY_INCIDENT_PERF_01"},
                "cpu": {"median": "BOUNDED_BY_INCIDENT_PERF_01"},
                "status": "BOUNDED_BY_INCIDENT_PERF_01",
                "note": runs[0]["stages"][stage].get("note", "Documented in PERF-01-XLSX-QUADRATIC"),
                "peak_rss_mb": max(rss_vals),
            }
        # Carry over sizes or rates if present
        for extra in ("db_size_bytes", "size_bytes", "charges_per_sec", "findings_per_sec"):
            if extra in runs[0]["stages"][stage]:
                st_data[extra] = runs[0]["stages"][stage][extra]

        agg[stage] = st_data

    total_walls = [r["total_wall_sec"] for r in runs]
    total_cpus = [r["total_cpu_sec"] for r in runs]
    total_rss = [r["peak_rss_mb"] for r in runs]

    return {
        "reps": len(runs),
        "total_wall": {
            "median": round(statistics.median(total_walls), 4),
            "min": round(min(total_walls), 4),
            "max": round(max(total_walls), 4),
            "mean": round(statistics.mean(total_walls), 4),
            "stdev": round(statistics.stdev(total_walls), 4) if len(total_walls) > 1 else 0.0,
        },
        "total_cpu": {
            "median": round(statistics.median(total_cpus), 4),
            "min": round(min(total_cpus), 4),
            "max": round(max(total_cpus), 4),
            "mean": round(statistics.mean(total_cpus), 4),
        },
        "peak_rss_mb": max(total_rss),
        "stages": agg,
    }


def execute_size_benchmark(size: int, reps: int, scale_dir: Path) -> dict:
    data_dir = scale_dir / str(size)
    print(f"\n=================================================================")
    print(f"BENCHMARK SIZE: {size} charges")
    print(f"=================================================================")

    if not (data_dir / "cargos.csv").exists():
        print(f"Generating dataset for N={size}...")
        oracle = generate_scale_data(size, data_dir)
    else:
        oracle = json.loads((data_dir / f"expected-scale-{size}.json").read_text(encoding="utf-8"))

    # Warm-up run
    print("Executing warm-up run...", flush=True)
    t0 = time.time()
    warmup = run_single_pipeline_benchmark(data_dir, oracle)
    print(f"Warm-up complete in {time.time() - t0:.2f}s.", flush=True)

    measured_runs = []
    for rep in range(1, reps + 1):
        print(f"  Run {rep}/{reps}...", end="", flush=True)
        t0 = time.time()
        run_res = run_single_pipeline_benchmark(data_dir, oracle)
        measured_runs.append(run_res)
        print(f" done in {time.time() - t0:.2f}s (Audit: {run_res['stages']['4_audit']['wall_sec']:.2f}s, Peak RSS: {run_res['peak_rss_mb']} MB)", flush=True)

    summary = aggregate_runs(measured_runs)
    (data_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_growth_curve(sizes: list[int], scale_dir: Path) -> dict:
    print("\n=================================================================")
    print(f"GROWTH CURVE CAMPAIGN: {sizes}")
    print("=================================================================")
    curve_data = {}
    for sz in sizes:
        # Run 3 reps for curve points
        summ = execute_size_benchmark(sz, reps=3, scale_dir=scale_dir)
        curve_data[sz] = {
            "audit_wall_median": summ["stages"]["4_audit"]["wall"]["median"],
            "total_wall_median": summ["total_wall"]["median"],
            "peak_rss_mb": summ["peak_rss_mb"],
        }

    # Calculate growth ratios
    ratios = []
    for i in range(len(sizes) - 1):
        sz1, sz2 = sizes[i], sizes[i + 1]
        mult = sz2 / sz1
        t_ratio = curve_data[sz2]["audit_wall_median"] / max(curve_data[sz1]["audit_wall_median"], 0.0001)
        tot_ratio = curve_data[sz2]["total_wall_median"] / max(curve_data[sz1]["total_wall_median"], 0.0001)
        rss_ratio = curve_data[sz2]["peak_rss_mb"] / max(curve_data[sz1]["peak_rss_mb"], 0.0001)

        evaluation = "LINEAR_OR_SUBQUADRATIC"
        if t_ratio >= 3.8:
            evaluation = "QUADRATIC_ALARM"
        elif t_ratio >= 2.5:
            evaluation = "SUPERLINEAR"

        ratios.append({
            "from_size": sz1,
            "to_size": sz2,
            "multiplier": mult,
            "audit_time_ratio": round(t_ratio, 2),
            "total_time_ratio": round(tot_ratio, 2),
            "rss_ratio": round(rss_ratio, 2),
            "evaluation": evaluation,
        })

    result = {
        "points": curve_data,
        "ratios": ratios,
    }
    (scale_dir / "growth_curve.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description="Calibre Scale & Complexity Benchmark Runner")
    parser.add_argument("--sizes", nargs="+", type=int, default=[10000, 50000, 100000], help="Benchmark sizes")
    parser.add_argument("--curve", nargs="+", type=int, default=[10000, 20000, 40000, 80000], help="Growth curve sizes")
    parser.add_argument("--reps", type=int, default=5, help="Number of measured repetitions")
    parser.add_argument("--skip-curve", action="store_true", help="Skip growth curve")
    args = parser.parse_args()

    scale_dir = ROOT / "output/e2e/platform_scale/scale"
    scale_dir.mkdir(parents=True, exist_ok=True)

    env = get_environment_info()
    (scale_dir / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    print(f"Host environment captured: {env['system']} {env['release']} | CPU: {env['cpu_model']} ({env['cpu_count']} cores) | RAM: {env['mem_total_mb']} MB")

    benchmark_summary = {}
    summary_path = scale_dir / "benchmark_summary.json"
    if summary_path.exists():
        try:
            benchmark_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception:
            benchmark_summary = {}

    # Run Benchmark Sizes (10k, 50k, 100k)
    for sz in args.sizes:
        summary = execute_size_benchmark(sz, reps=args.reps, scale_dir=scale_dir)
        benchmark_summary[sz] = summary

    (scale_dir / "benchmark_summary.json").write_text(json.dumps(benchmark_summary, indent=2), encoding="utf-8")

    # Run Growth Curve (10k, 20k, 40k, 80k)
    if not args.skip_curve:
        run_growth_curve(args.curve, scale_dir=scale_dir)

    print("\n=================================================================")
    print("ALL SCALE BENCHMARKS AND GROWTH CURVES COMPLETED SUCCESSFULLY!")
    print(f"Results recorded in: {scale_dir}")
    print("=================================================================")


if __name__ == "__main__":
    main()
