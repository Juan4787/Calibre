#!/usr/bin/env python3
"""Characterization harness for Incident PERF-01 (XLSX Quadratic Complexity).

Measures workbook_bytes() across N = [1000, 2000, 5000, 10000] findings
using the unmodified production reporting.py to capture the current performance cliff.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from freight_audit.canonical import load_json
from freight_audit.engine import audit
from freight_audit.importing import ImportMapping, import_data
from freight_audit.models import Agreement, Dataset
from freight_audit.reporting import workbook_bytes
from freight_audit.storage import Store
from output.e2e.platform_scale.generate_scale_dataset import generate_scale_data


def measure_xlsx_for_size(n: int, tmp_dir: Path) -> dict:
    data_dir = tmp_dir / f"bench_{n}"
    data_dir.mkdir(parents=True, exist_ok=True)
    generate_scale_data(n, data_dir)

    charges_bytes = (data_dir / "cargos.csv").read_bytes()
    shipments_bytes = (data_dir / "remitos.csv").read_bytes()
    map_c = ImportMapping.model_validate(load_json((data_dir / "mapping-charges.json").read_bytes()))
    map_s = ImportMapping.model_validate(load_json((data_dir / "mapping-shipments.json").read_bytes()))
    imp_c = import_data(charges_bytes, "cargos.csv", map_c)
    imp_s = import_data(shipments_bytes, "remitos.csv", map_s)

    dataset = Dataset(
        label=f"XLSX Bench {n}",
        agreements=[Agreement.model_validate(a) for a in load_json((data_dir / "agreements.json").read_bytes())],
        charges=imp_c["records"],
        shipments=imp_s["records"],
        evidence=load_json((data_dir / "evidence.json").read_bytes()),
        documents={imp_c["document"]: "cargos.csv", imp_s["document"]: "remitos.csv"},
    )

    audit_res = audit(dataset)
    db_path = tmp_dir / f"store_{n}.db"
    store = Store(db_path)
    store.put_source(charges_bytes)
    store.put_source(shipments_bytes)
    run_id = store.save(dataset, audit_res)
    run = store.load(run_id)

    print(f"Measuring workbook_bytes() for N={n} findings...", flush=True)
    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    wb_data = workbook_bytes(run)
    t_wall = time.perf_counter() - t0_wall
    t_cpu = time.process_time() - t0_cpu
    sz = len(wb_data)
    print(f"  N={n}: {t_wall:.3f}s (CPU: {t_cpu:.3f}s, size: {sz} bytes)", flush=True)

    return {
        "n_findings": n,
        "wall_sec": round(t_wall, 4),
        "cpu_sec": round(t_cpu, 4),
        "size_bytes": sz,
    }


def main():
    sizes = [1000, 2000, 5000, 10000]
    results = {}
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        for s in sizes:
            results[str(s)] = measure_xlsx_for_size(s, tdp)

    out_file = ROOT / "output/e2e/platform_scale/incidents/PERF-01-XLSX-QUADRATIC/characterization_curve.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nCharacterization curve saved to: {out_file}")


if __name__ == "__main__":
    main()
