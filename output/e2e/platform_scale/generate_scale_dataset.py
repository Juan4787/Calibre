#!/usr/bin/env python3
"""Deterministic Scale Dataset Generator with Mathematical Independent Oracle.

Generates calibrated datasets of N charges with realistic patterns:
- PASS (single shipment & multi-vigencia)
- FAIL excess (overcharge)
- FAIL defect (undercharge)
- REVIEW (missing POD evidence)
- UNDETERMINABLE (unmatched reference)
- Segregated Currencies: ARS and USD
- N:1 Consolidation (multiple shipments to 1 charge)
- 1:N Multiple charges per shipment

Outputs:
- cargos.csv
- remitos.csv
- mapping-charges.json
- mapping-shipments.json
- agreements.json
- evidence.json
- expected-scale-{N}.json (independent mathematical oracle)
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from decimal import Decimal
from pathlib import Path

SEED = 42
BLOCK_SIZE = 20  # 20 charges per cycle


def build_agreements() -> list[dict]:
    return [
        {
            "id": "AGR-SCALE-ARS",
            "name": "Acuerdo Escala ARS",
            "carrier": "EXPRESO-SUR",
            "currency": "ARS",
            "date_field": "attributes.fecha",
            "scale": 2,
            "rounding": "ROUND_HALF_EVEN",
            "tolerance_absolute": "0.05",
            "tolerance_relative": "0.001",
            "matching": {
                "keys": [
                    {"charge": "reference", "shipment": "reference"}
                ],
                "cardinality": "group"
            },
            "versions": [
                {
                    "id": "V1",
                    "valid_from": "2026-01-01",
                    "valid_to": "2026-06-30",
                    "source_note": "Tarifas H1 2026",
                    "rules": [
                        {
                            "id": "R-BASE-V1",
                            "concept": "FLETE_BASE",
                            "description": "Tarifa plana H1",
                            "expression": {
                                "op": "const",
                                "value": {
                                    "type": "decimal",
                                    "value": "1000.00",
                                    "unit": "ARS"
                                }
                            }
                        },
                        {
                            "id": "R-SEGURO-V1",
                            "concept": "SEGURO",
                            "description": "Tarifa seguro con requisito de remito firmado",
                            "evidence": [
                                {
                                    "any_of": ["remito_firmado"],
                                    "scope": "group",
                                    "document_required": False
                                }
                            ],
                            "expression": {
                                "op": "const",
                                "value": {
                                    "type": "decimal",
                                    "value": "200.00",
                                    "unit": "ARS"
                                }
                            }
                        }
                    ]
                },
                {
                    "id": "V2",
                    "valid_from": "2026-07-01",
                    "valid_to": "2026-12-31",
                    "source_note": "Tarifas H2 2026",
                    "rules": [
                        {
                            "id": "R-BASE-V2",
                            "concept": "FLETE_BASE",
                            "description": "Tarifa plana H2",
                            "expression": {
                                "op": "const",
                                "value": {
                                    "type": "decimal",
                                    "value": "1200.00",
                                    "unit": "ARS"
                                }
                            }
                        },
                        {
                            "id": "R-SEGURO-V2",
                            "concept": "SEGURO",
                            "description": "Tarifa seguro con requisito de remito firmado",
                            "evidence": [
                                {
                                    "any_of": ["remito_firmado"],
                                    "scope": "group",
                                    "document_required": False
                                }
                            ],
                            "expression": {
                                "op": "const",
                                "value": {
                                    "type": "decimal",
                                    "value": "200.00",
                                    "unit": "ARS"
                                }
                            }
                        }
                    ]
                }
            ]
        },
        {
            "id": "AGR-SCALE-USD",
            "name": "Acuerdo Escala USD",
            "carrier": "GLOBAL-CARGO",
            "currency": "USD",
            "date_field": "attributes.fecha",
            "scale": 2,
            "rounding": "ROUND_HALF_EVEN",
            "tolerance_absolute": "0.05",
            "tolerance_relative": "0.001",
            "matching": {
                "keys": [
                    {"charge": "reference", "shipment": "reference"}
                ],
                "cardinality": "group"
            },
            "versions": [
                {
                    "id": "V1",
                    "valid_from": "2026-01-01",
                    "valid_to": "2026-12-31",
                    "source_note": "Tarifas Marítimas 2026",
                    "rules": [
                        {
                            "id": "R-OCEAN",
                            "concept": "FLETE_MARITIMO",
                            "description": "Tarifa marítima plana",
                            "expression": {
                                "op": "const",
                                "value": {
                                    "type": "decimal",
                                    "value": "500.00",
                                    "unit": "USD"
                                }
                            }
                        },
                        {
                            "id": "R-PORT",
                            "concept": "GASTOS_PUERTO",
                            "description": "Tarifa portuaria",
                            "expression": {
                                "op": "const",
                                "value": {
                                    "type": "decimal",
                                    "value": "150.00",
                                    "unit": "USD"
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]


def build_mappings() -> tuple[dict, dict]:
    mapping_charges = {
        "id": "MAP-SCALE-CHARGES",
        "version": "1",
        "entity": "charges",
        "header_row": 1,
        "delimiter": ",",
        "decimal_separator": ".",
        "thousands_separator": "",
        "columns": [
            {"source": "id_cargo", "target": "id", "type": "text"},
            {"source": "liquidacion", "target": "settlement", "type": "text"},
            {"source": "transportista", "target": "carrier", "type": "text"},
            {"source": "acuerdo", "target": "agreement", "type": "text"},
            {"source": "referencia", "target": "reference", "type": "text"},
            {"source": "concepto", "target": "concept", "type": "text"},
            {"source": "monto", "target": "amount", "type": "decimal"},
            {"source": "moneda", "target": "currency", "type": "text"}
        ]
    }
    mapping_shipments = {
        "id": "MAP-SCALE-SHIPMENTS",
        "version": "1",
        "entity": "shipments",
        "header_row": 1,
        "delimiter": ",",
        "date_formats": ["%Y-%m-%d"],
        "columns": [
            {"source": "id_remito", "target": "id", "type": "text"},
            {"source": "transportista", "target": "carrier", "type": "text"},
            {"source": "referencia", "target": "reference", "type": "text"},
            {"source": "fecha", "target": "attributes.fecha", "type": "date"}
        ]
    }
    return mapping_charges, mapping_shipments


def compute_mathematical_oracle(num_charges: int) -> dict:
    """Computes exact aggregated expected outcomes without running the engine."""
    assert num_charges % BLOCK_SIZE == 0, f"num_charges must be a multiple of {BLOCK_SIZE}"
    blocks = num_charges // BLOCK_SIZE

    # Per block exact figures:
    # Shipments: 19
    # Findings: 20
    # PASS: 14 (11 ARS, 3 USD)
    # FAIL: 4 (2 excess ARS, 1 defect ARS, 1 excess USD)
    # REVIEW: 1 (ARS)
    # UNDETERMINABLE: 1 (ARS)

    total_shipments = blocks * 19
    total_findings = blocks * 20
    counts = {
        "PASS": blocks * 14,
        "FAIL": blocks * 4,
        "REVIEW": blocks * 1,
        "UNDETERMINABLE": blocks * 1,
    }

    # ARS per block
    # Actual: 15250.00
    # Expected: 14000.00
    # Excess: 500.00
    # Defect: -250.00
    # Review: 200.00
    # Undeterminable: 1000.00
    ars_actual = Decimal("15250.00") * blocks
    ars_overcharge = Decimal("500.00") * blocks
    ars_undercharge = Decimal("-250.00") * blocks
    ars_net_diff = Decimal("250.00") * blocks
    ars_pass = Decimal("10800.00") * blocks
    ars_review = Decimal("200.00") * blocks
    ars_undet = Decimal("1000.00") * blocks
    ars_det = Decimal("14050.00") * blocks

    usd_actual = Decimal("1770.00") * blocks
    usd_overcharge = Decimal("120.00") * blocks
    usd_undercharge = Decimal("0.00")
    usd_net_diff = Decimal("120.00") * blocks
    usd_pass = Decimal("1150.00") * blocks
    usd_review = Decimal("0.00")
    usd_undet = Decimal("0.00")
    usd_det = Decimal("1770.00") * blocks

    return {
        "seed": SEED,
        "total_charges": num_charges,
        "total_shipments": total_shipments,
        "total_findings": total_findings,
        "counts": counts,
        "currencies": {
            "ARS": {
                "actual": str(ars_actual),
                "confirmed_overcharge": str(ars_overcharge),
                "confirmed_undercharge": str(ars_undercharge),
                "confirmed_net_difference": str(ars_net_diff),
                "pass": str(ars_pass),
                "review": str(ars_review),
                "undeterminable": str(ars_undet),
                "determinable": str(ars_det),
            },
            "USD": {
                "actual": str(usd_actual),
                "confirmed_overcharge": str(usd_overcharge),
                "confirmed_undercharge": str(usd_undercharge),
                "confirmed_net_difference": str(usd_net_diff),
                "pass": str(usd_pass),
                "review": str(usd_review),
                "undeterminable": str(usd_undet),
                "determinable": str(usd_det),
            },
        },
        "invariants": {
            "no_currency_leakage": True,
            "charges_conservation": num_charges == total_findings,
            "ars_actual_conservation": str(ars_actual) == str(ars_det + ars_undet),
            "usd_actual_conservation": str(usd_actual) == str(usd_det + usd_undet),
        },
    }


def generate_scale_data(num_charges: int, out_dir: Path) -> dict:
    assert num_charges % BLOCK_SIZE == 0
    blocks = num_charges // BLOCK_SIZE
    rng = random.Random(SEED)

    out_dir.mkdir(parents=True, exist_ok=True)

    agreements = build_agreements()
    map_c, map_s = build_mappings()

    (out_dir / "agreements.json").write_text(json.dumps(agreements, indent=2), encoding="utf-8")
    (out_dir / "mapping-charges.json").write_text(json.dumps(map_c, indent=2), encoding="utf-8")
    (out_dir / "mapping-shipments.json").write_text(json.dumps(map_s, indent=2), encoding="utf-8")

    charges_path = out_dir / "cargos.csv"
    shipments_path = out_dir / "remitos.csv"
    evidence_path = out_dir / "evidence.json"

    evidence_list = []

    with open(charges_path, "w", newline="", encoding="utf-8") as fc, \
         open(shipments_path, "w", newline="", encoding="utf-8") as fs:

        cw = csv.writer(fc)
        sw = csv.writer(fs)

        cw.writerow(["id_cargo", "liquidacion", "transportista", "acuerdo", "referencia", "concepto", "monto", "moneda"])
        sw.writerow(["id_remito", "transportista", "referencia", "fecha"])

        for b in range(blocks):
            sett_ars = f"LIQ-ARS-{b:06d}"
            sett_usd = f"LIQ-USD-{b:06d}"

            # -------------------------------------------------------------
            # Oper 0..4: PASS in ARS (Vigencia 1: 1000.00 ARS)
            # -------------------------------------------------------------
            for k in range(5):
                ref = f"REM-P1-{b:06d}-{k}"
                sw.writerow([f"SH-P1-{b:06d}-{k}", "EXPRESO-SUR", ref, "2026-03-15"])
                cw.writerow([f"CH-P1-{b:06d}-{k}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref, "FLETE_BASE", "1000.00", "ARS"])

            # -------------------------------------------------------------
            # Oper 5..7: PASS in ARS (Vigencia 2: 1200.00 ARS)
            # -------------------------------------------------------------
            for k in range(3):
                ref = f"REM-P2-{b:06d}-{k}"
                sw.writerow([f"SH-P2-{b:06d}-{k}", "EXPRESO-SUR", ref, "2026-08-10"])
                cw.writerow([f"CH-P2-{b:06d}-{k}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref, "FLETE_BASE", "1200.00", "ARS"])

            # -------------------------------------------------------------
            # Oper 8..9: FAIL excess in ARS (Vigencia 1: Expected 1000.00)
            # Oper 8: 1350.00 (+350.00)
            # Oper 9: 1150.00 (+150.00)
            # -------------------------------------------------------------
            ref8 = f"REM-FE1-{b:06d}"
            sw.writerow([f"SH-FE1-{b:06d}", "EXPRESO-SUR", ref8, "2026-03-20"])
            cw.writerow([f"CH-FE1-{b:06d}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref8, "FLETE_BASE", "1350.00", "ARS"])

            ref9 = f"REM-FE2-{b:06d}"
            sw.writerow([f"SH-FE2-{b:06d}", "EXPRESO-SUR", ref9, "2026-03-21"])
            cw.writerow([f"CH-FE2-{b:06d}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref9, "FLETE_BASE", "1150.00", "ARS"])

            # -------------------------------------------------------------
            # Oper 10: FAIL defect in ARS (Vigencia 1: Expected 1000.00, Actual 750.00, Diff -250.00)
            # -------------------------------------------------------------
            ref10 = f"REM-FD-{b:06d}"
            sw.writerow([f"SH-FD-{b:06d}", "EXPRESO-SUR", ref10, "2026-03-22"])
            cw.writerow([f"CH-FD-{b:06d}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref10, "FLETE_BASE", "750.00", "ARS"])

            # -------------------------------------------------------------
            # Oper 11: REVIEW in ARS (SEGURO requires POD, missing evidence)
            # -------------------------------------------------------------
            ref11 = f"REM-REV-{b:06d}"
            sw.writerow([f"SH-REV-{b:06d}", "EXPRESO-SUR", ref11, "2026-03-23"])
            cw.writerow([f"CH-REV-{b:06d}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref11, "SEGURO", "200.00", "ARS"])

            # -------------------------------------------------------------
            # Oper 12: UNDETERMINABLE in ARS (Incompatible carrier)
            # -------------------------------------------------------------
            ref12 = f"REM-NOEXIST-{b:06d}"
            # No shipment written!
            cw.writerow([f"CH-UND-{b:06d}", sett_ars, "TRANSPORTISTA-DESCONOCIDO", "AGR-SCALE-ARS", ref12, "FLETE_BASE", "1000.00", "ARS"])

            # -------------------------------------------------------------
            # Oper 13..15: PASS in USD
            # Oper 13, 14: FLETE_MARITIMO (500.00 USD)
            # Oper 15: GASTOS_PUERTO (150.00 USD)
            # -------------------------------------------------------------
            ref13 = f"REM-USD-OC1-{b:06d}"
            sw.writerow([f"SH-USD-OC1-{b:06d}", "GLOBAL-CARGO", ref13, "2026-04-01"])
            cw.writerow([f"CH-USD-OC1-{b:06d}", sett_usd, "GLOBAL-CARGO", "AGR-SCALE-USD", ref13, "FLETE_MARITIMO", "500.00", "USD"])

            ref14 = f"REM-USD-OC2-{b:06d}"
            sw.writerow([f"SH-USD-OC2-{b:06d}", "GLOBAL-CARGO", ref14, "2026-04-02"])
            cw.writerow([f"CH-USD-OC2-{b:06d}", sett_usd, "GLOBAL-CARGO", "AGR-SCALE-USD", ref14, "FLETE_MARITIMO", "500.00", "USD"])

            ref15 = f"REM-USD-PT-{b:06d}"
            sw.writerow([f"SH-USD-PT-{b:06d}", "GLOBAL-CARGO", ref15, "2026-04-03"])
            cw.writerow([f"CH-USD-PT-{b:06d}", sett_usd, "GLOBAL-CARGO", "AGR-SCALE-USD", ref15, "GASTOS_PUERTO", "150.00", "USD"])

            # -------------------------------------------------------------
            # Oper 16: FAIL excess in USD (Expected 500.00, Actual 620.00, Diff +120.00)
            # -------------------------------------------------------------
            ref16 = f"REM-USD-FAIL-{b:06d}"
            sw.writerow([f"SH-USD-FAIL-{b:06d}", "GLOBAL-CARGO", ref16, "2026-04-04"])
            cw.writerow([f"CH-USD-FAIL-{b:06d}", sett_usd, "GLOBAL-CARGO", "AGR-SCALE-USD", ref16, "FLETE_MARITIMO", "620.00", "USD"])

            # -------------------------------------------------------------
            # Oper 17: N:1 Consolidation in ARS (2 shipments -> 1 charge)
            # Both shipments share same reference ref17
            # -------------------------------------------------------------
            ref17 = f"REM-N1-{b:06d}"
            sw.writerow([f"SH-N1-A-{b:06d}", "EXPRESO-SUR", ref17, "2026-03-25"])
            sw.writerow([f"SH-N1-B-{b:06d}", "EXPRESO-SUR", ref17, "2026-03-25"])
            cw.writerow([f"CH-N1-{b:06d}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref17, "FLETE_BASE", "1000.00", "ARS"])

            # -------------------------------------------------------------
            # Oper 18..19: 1:N Multiple charges for 1 shipment in ARS
            # 1 shipment ref18
            # Charge 18: FLETE_BASE (1000.00 ARS)
            # Charge 19: SEGURO (200.00 ARS, with POD attached -> PASS)
            # -------------------------------------------------------------
            ref18 = f"REM-1N-{b:06d}"
            sh_id_18 = f"SH-1N-{b:06d}"
            sw.writerow([sh_id_18, "EXPRESO-SUR", ref18, "2026-03-26"])
            cw.writerow([f"CH-1N-BASE-{b:06d}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref18, "FLETE_BASE", "1000.00", "ARS"])
            cw.writerow([f"CH-1N-SEG-{b:06d}", sett_ars, "EXPRESO-SUR", "AGR-SCALE-ARS", ref18, "SEGURO", "200.00", "ARS"])

            # Attach POD evidence to sh_id_18
            ev_id = f"EV-POD-{b:06d}"
            evidence_list.append({
                "id": ev_id,
                "kind": "remito_firmado",
                "shipment_ids": [sh_id_18],
                "charge_ids": [],
                "note": "Remito firmado conforme",
            })

    evidence_path.write_text(json.dumps(evidence_list, indent=2), encoding="utf-8")

    oracle = compute_mathematical_oracle(num_charges)
    oracle_path = out_dir / f"expected-scale-{num_charges}.json"
    oracle_path.write_text(json.dumps(oracle, indent=2), encoding="utf-8")

    return oracle


def main():
    parser = argparse.ArgumentParser(description="Scale Dataset Generator")
    parser.add_argument("--size", type=int, required=True, help="Number of charges (e.g. 10000, 50000, 100000)")
    parser.add_argument("--out", type=Path, default=None, help="Output directory")
    args = parser.parse_args()

    out_dir = args.out or Path(f"output/e2e/platform_scale/scale/{args.size}")
    print(f"Generating scale dataset for N={args.size} into {out_dir}...")
    oracle = generate_scale_data(args.size, out_dir)
    print(f"Done! Oracle generated with {oracle['total_findings']} expected findings.")
    print(f"Counts: {oracle['counts']}")
    print(f"Currencies: {oracle['currencies']}")


if __name__ == "__main__":
    main()
