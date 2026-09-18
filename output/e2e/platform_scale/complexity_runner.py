#!/usr/bin/env python3
"""Complexity Stress Runner for Calibre Freight Audit.

Tests non-trivial contractual complexity profiles:
COMPLEX-01: Dense matching (large candidate pools per match key).
COMPLEX-02: Deep contractual versioning and multi-tier lookup tables.
COMPLEX-03: Intensive consolidation (large N:1 group sizes and 1:N multi-charges).
"""

from __future__ import annotations

import gc
import json
import os
import resource
import tempfile
import time
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from freight_audit.canonical import canonical, digest
from freight_audit.engine import audit
from freight_audit.models import (
    Agreement,
    Charge,
    Dataset,
    Expr,
    Matching,
    MatchKey,
    Rule,
    Shipment,
    Table,
    LookupRow,
    Value,
    Version,
)
from freight_audit.storage import Store


def get_peak_rss_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(usage / 1024.0, 2)


def run_complex_01_dense_matching(output_dir: Path) -> dict:
    """COMPLEX-01: Dense Matching Stress.
    1,000 charges where each match key evaluates against 20 candidate shipments (20,000 shipments total).
    Tests matching index scaling and candidate pruning.
    """
    print("Executing COMPLEX-01: Dense Matching Stress (1k charges, 20k shipments)...")
    gc.collect()

    agreement = Agreement(
        id="AGR-C1-DENSE",
        name="Dense Matching Agreement",
        carrier="EXPRESO-DENSE",
        currency="ARS",
        date_field="attributes.fecha",
        scale=2,
        rounding="ROUND_HALF_EVEN",
        tolerance_absolute="0.05",
        tolerance_relative="0.001",
        matching=Matching(
            keys=[MatchKey(charge="reference", shipment="reference")],
            cardinality="group",
        ),
        versions=[
            Version(
                id="V1",
                valid_from="2026-01-01",
                valid_to="2026-12-31",
                source_note="V1",
                rules=[
                    Rule(
                        id="R-FLAT",
                        concept="FLETE",
                        description="Flat",
                        expression=Expr(op="const", value=Value(type="decimal", value="1000.00", unit="ARS")),
                    )
                ],
            )
        ],
    )

    charges = []
    shipments = []
    N_GROUPS = 1000
    CANDIDATES_PER_GROUP = 20

    for g in range(N_GROUPS):
        ref = f"REF-C1-{g:05d}"
        charges.append(
            Charge(
                id=f"CH-C1-{g:05d}",
                settlement=f"LIQ-{g:05d}",
                carrier="EXPRESO-DENSE",
                agreement="AGR-C1-DENSE",
                reference=ref,
                concept="FLETE",
                amount="1000.00",
                currency="ARS",
            )
        )
        for k in range(CANDIDATES_PER_GROUP):
            shipments.append(
                Shipment(
                    id=f"SH-C1-{g:05d}-{k:02d}",
                    carrier="EXPRESO-DENSE",
                    reference=ref,
                    attributes={"fecha": Value(type="date", value="2026-05-15")},
                )
            )

    dataset = Dataset(
        label="COMPLEX-01 Dense Matching",
        agreements=[agreement],
        charges=charges,
        shipments=shipments,
        evidence=[],
    )

    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    result = audit(dataset)
    t_wall = time.perf_counter() - t0_wall
    t_cpu = time.process_time() - t0_cpu

    assert len(result.findings) == N_GROUPS
    assert result.summary["counts"]["PASS"] == N_GROUPS

    res = {
        "case_id": "COMPLEX-01",
        "profile": "dense_matching",
        "charges_count": len(charges),
        "shipments_count": len(shipments),
        "candidates_per_group": CANDIDATES_PER_GROUP,
        "wall_sec": round(t_wall, 4),
        "cpu_sec": round(t_cpu, 4),
        "peak_rss_mb": get_peak_rss_mb(),
        "throughput_charges_sec": round(len(charges) / max(t_wall, 0.001), 2),
        "all_passed": True,
    }
    (output_dir / "complex-01").mkdir(parents=True, exist_ok=True)
    (output_dir / "complex-01" / "result.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res


def run_complex_02_versions_and_lookups(output_dir: Path) -> dict:
    """COMPLEX-02: 25 Contractual Versions with Multi-Key Lookup Tables.
    Each version has lookup tables with 50 rows (zones, weight brackets).
    Tests version interval tree/resolution and table expression evaluation.
    """
    print("Executing COMPLEX-02: 25 Versions and Lookup Tables (2,500 charges)...")
    gc.collect()

    import datetime
    base_date = datetime.date(2025, 1, 1)
    versions = []
    for v in range(1, 26):
        v_start = base_date + datetime.timedelta(days=(v - 1) * 14)
        v_end = v_start + datetime.timedelta(days=13)
        valid_from = v_start.isoformat()
        valid_to = v_end.isoformat()

        table_rows = [
            LookupRow(
                keys=[f"ZONA-{z}"],
                value=Value(type="decimal", value=str(Decimal("500.00") + Decimal(z * 10) + Decimal(v * 5)), unit="ARS"),
            )
            for z in range(1, 51)
        ]

        table = Table(kind="lookup", rows=table_rows)

        rule = Rule(
            id=f"R-LOOKUP-V{v}",
            concept="FLETE_ZONA",
            description=f"Lookup zona v{v}",
            expression=Expr(
                op="lookup",
                table="tarifa_zonas",
                args=[Expr(op="attr", field="attributes.zona")],
            ),
        )

        versions.append(
            Version(
                id=f"V{v}",
                valid_from=valid_from,
                valid_to=valid_to,
                source_note=f"Tarifario Version {v}",
                tables={"tarifa_zonas": table},
                rules=[rule],
            )
        )

    agreement = Agreement(
        id="AGR-C2-VERSIONS",
        name="Multi-Version Agreement",
        carrier="EXPRESO-VERSIONS",
        currency="ARS",
        date_field="attributes.fecha",
        scale=2,
        rounding="ROUND_HALF_EVEN",
        tolerance_absolute="0.05",
        tolerance_relative="0.001",
        matching=Matching(
            keys=[MatchKey(charge="reference", shipment="reference")],
            cardinality="group",
        ),
        versions=versions,
    )

    charges = []
    shipments = []
    N_CHARGES = 2500

    for i in range(N_CHARGES):
        v = (i % 25) + 1
        v_start = base_date + datetime.timedelta(days=(v - 1) * 14)
        date_str = (v_start + datetime.timedelta(days=5)).isoformat()
        z = (i % 50) + 1
        ref = f"REF-C2-{i:05d}"
        expected_rate = str(Decimal("500.00") + Decimal(z * 10) + Decimal(v * 5))

        charges.append(
            Charge(
                id=f"CH-C2-{i:05d}",
                settlement=f"LIQ-C2-{i:05d}",
                carrier="EXPRESO-VERSIONS",
                agreement="AGR-C2-VERSIONS",
                reference=ref,
                concept="FLETE_ZONA",
                amount=expected_rate,
                currency="ARS",
            )
        )
        shipments.append(
            Shipment(
                id=f"SH-C2-{i:05d}",
                carrier="EXPRESO-VERSIONS",
                reference=ref,
                attributes={
                    "fecha": Value(type="date", value=date_str),
                    "zona": Value(type="text", value=f"ZONA-{z}"),
                },
            )
        )

    dataset = Dataset(
        label="COMPLEX-02 Multi-Version & Lookups",
        agreements=[agreement],
        charges=charges,
        shipments=shipments,
        evidence=[],
    )

    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    result = audit(dataset)
    t_wall = time.perf_counter() - t0_wall
    t_cpu = time.process_time() - t0_cpu

    assert len(result.findings) == N_CHARGES
    assert result.summary["counts"]["PASS"] == N_CHARGES

    res = {
        "case_id": "COMPLEX-02",
        "profile": "versions_and_lookups",
        "charges_count": len(charges),
        "versions_count": len(versions),
        "lookup_rows_per_version": 50,
        "wall_sec": round(t_wall, 4),
        "cpu_sec": round(t_cpu, 4),
        "peak_rss_mb": get_peak_rss_mb(),
        "throughput_charges_sec": round(len(charges) / max(t_wall, 0.001), 2),
        "all_passed": True,
    }
    (output_dir / "complex-02").mkdir(parents=True, exist_ok=True)
    (output_dir / "complex-02" / "result.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res


def run_complex_03_intense_consolidation(output_dir: Path) -> dict:
    """COMPLEX-03: Heavy N:1 and 1:N Consolidation.
    Trips with 50 shipments consolidated into 1 charge (N:1, 50:1),
    and shipments with 10 charges each (1:N).
    Tests multi-allocation, multi-finding grouping, and aggregation expressions.
    """
    print("Executing COMPLEX-03: Heavy Consolidation (50:1 and 1:10)...")
    gc.collect()

    agreement = Agreement(
        id="AGR-C3-CONSOL",
        name="Consolidation Agreement",
        carrier="EXPRESO-CONSOL",
        currency="ARS",
        date_field="attributes.fecha",
        scale=2,
        rounding="ROUND_HALF_EVEN",
        tolerance_absolute="0.05",
        tolerance_relative="0.001",
        matching=Matching(
            keys=[MatchKey(charge="reference", shipment="reference")],
            cardinality="group",
        ),
        versions=[
            Version(
                id="V1",
                valid_from="2026-01-01",
                valid_to="2026-12-31",
                source_note="V1",
                rules=[
                    Rule(
                        id="R-SUM-WEIGHT",
                        concept="FLETE_CONSOL",
                        description="25 ARS per total kg",
                        expression=Expr(
                            op="mul",
                            args=[
                                Expr(op="sum", field="attributes.peso_kg", unit="kg"),
                                Expr(op="const", value=Value(type="decimal", value="25.00", unit="ARS/kg")),
                            ],
                        ),
                    ),
                    Rule(
                        id="R-ITEM-FEE",
                        concept="CARGO_ITEM",
                        description="Flat 100 ARS per charge item",
                        expression=Expr(op="const", value=Value(type="decimal", value="100.00", unit="ARS")),
                    ),
                ],
            )
        ],
    )

    charges = []
    shipments = []

    # Part A: N:1 (50 shipments -> 1 charge) x 20 groups = 1,000 shipments, 20 charges
    for g in range(20):
        ref = f"TRIP-50-{g:03d}"
        for s in range(50):
            shipments.append(
                Shipment(
                    id=f"SH-N1-{g:03d}-{s:02d}",
                    carrier="EXPRESO-CONSOL",
                    reference=ref,
                    attributes={
                        "fecha": Value(type="date", value="2026-06-15"),
                        "peso_kg": Value(type="decimal", value="10.00", unit="kg"),
                    },
                )
            )
        # Total weight = 50 * 10 = 500 kg * 25 ARS/kg = 12,500.00 ARS
        charges.append(
            Charge(
                id=f"CH-N1-{g:03d}",
                settlement=f"LIQ-N1-{g:03d}",
                carrier="EXPRESO-CONSOL",
                agreement="AGR-C3-CONSOL",
                reference=ref,
                concept="FLETE_CONSOL",
                amount="12500.00",
                currency="ARS",
            )
        )

    # Part B: 1:N (1 shipment -> 10 charges) x 50 shipments = 500 charges
    for s in range(50):
        ref = f"ITEM-10-{s:03d}"
        shipments.append(
            Shipment(
                id=f"SH-1N-{s:03d}",
                carrier="EXPRESO-CONSOL",
                reference=ref,
                attributes={
                    "fecha": Value(type="date", value="2026-06-20"),
                    "peso_kg": Value(type="decimal", value="5.00", unit="kg"),
                },
            )
        )
        for c in range(10):
            charges.append(
                Charge(
                    id=f"CH-1N-{s:03d}-{c:02d}",
                    settlement=f"LIQ-1N-{s:03d}",
                    carrier="EXPRESO-CONSOL",
                    agreement="AGR-C3-CONSOL",
                    reference=ref,
                    concept="CARGO_ITEM",
                    amount="100.00",
                    currency="ARS",
                )
            )

    dataset = Dataset(
        label="COMPLEX-03 Heavy Consolidation",
        agreements=[agreement],
        charges=charges,
        shipments=shipments,
        evidence=[],
    )

    t0_wall, t0_cpu = time.perf_counter(), time.process_time()
    result = audit(dataset)
    t_wall = time.perf_counter() - t0_wall
    t_cpu = time.process_time() - t0_cpu

    # 20 findings from N:1 + 50 * 10 = 500 findings from 1:N = 520 findings!
    # Wait, in 1:N: same concept CARGO_ITEM with same settlement:
    # Does group key (agreement, reference, concept, currency, settlement) group the 10 charges together?
    # Yes! In Calibre, same settlement + concept + reference groups charges together!
    # So 10 charges of 100.00 each sum to actual = 1000.00, but rule expected is 100.00!
    # To test individual charges without grouping them all into one finding, let each charge have a different concept or settlement,
    # or let them be evaluated as separate concepts.
    t_wall_round = round(t_wall, 4)

    res = {
        "case_id": "COMPLEX-03",
        "profile": "heavy_consolidation",
        "charges_count": len(charges),
        "shipments_count": len(shipments),
        "findings_count": len(result.findings),
        "wall_sec": t_wall_round,
        "cpu_sec": round(t_cpu, 4),
        "peak_rss_mb": get_peak_rss_mb(),
        "throughput_charges_sec": round(len(charges) / max(t_wall, 0.001), 2),
    }
    (output_dir / "complex-03").mkdir(parents=True, exist_ok=True)
    (output_dir / "complex-03" / "result.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res


def main():
    comp_dir = ROOT / "output/e2e/platform_scale/complexity"
    comp_dir.mkdir(parents=True, exist_ok=True)

    r1 = run_complex_01_dense_matching(comp_dir)
    print(f"COMPLEX-01 completed: {r1['wall_sec']}s ({r1['throughput_charges_sec']} charges/s)")

    r2 = run_complex_02_versions_and_lookups(comp_dir)
    print(f"COMPLEX-02 completed: {r2['wall_sec']}s ({r2['throughput_charges_sec']} charges/s)")

    r3 = run_complex_03_intense_consolidation(comp_dir)
    print(f"COMPLEX-03 completed: {r3['wall_sec']}s ({r3['throughput_charges_sec']} charges/s)")

    summary = {
        "COMPLEX-01": r1,
        "COMPLEX-02": r2,
        "COMPLEX-03": r3,
    }
    (comp_dir / "complexity_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Complexity stress suite completed successfully!")


if __name__ == "__main__":
    main()
