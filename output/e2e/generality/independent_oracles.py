#!/usr/bin/env python3
"""Oráculo Matemático Independiente para Fase 4 (Generalidad del Motor).

REGLA ESTRICTA DE INDEPENDENCIA:
- Este script NO importa NADA de freight_audit.engine, freight_audit.rules,
  ni ningún helper económico de producción.
- Utiliza aritmética pura con decimal.Decimal y fractions.Fraction.
- Las tablas y tarifas de referencia son estáticas e independientes.
- Calcula y congela los resultados esperados (expected, actual, difference, status)
  en frozen_expected.json ANTES de ejecutar Calibre.
"""

import json
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path


def quantize(val: Decimal, scale: int = 2) -> Decimal:
    """Redondeo bancario estándar independiente."""
    unit = Decimal("10") ** (-scale)
    return val.quantize(unit, rounding=ROUND_HALF_EVEN)


def run_g1_oracle():
    """G1: Peso + Mínimo + Porcentaje."""
    rate = Decimal("15.00")
    min_charge = Decimal("500.00")
    fuel_pct = Decimal("0.085")  # 8.5%

    cases = [
        {"id": "OP-G1-01", "weight": Decimal("120.00"), "actual": Decimal("1953.00")},
        {"id": "OP-G1-02", "weight": Decimal("20.00"), "actual": Decimal("570.00")},
        {"id": "OP-G1-03", "weight": Decimal("50.00"), "actual": Decimal("813.75")},
    ]

    results = []
    for c in cases:
        base = max(min_charge, c["weight"] * rate)
        fuel = base * fuel_pct
        expected = quantize(base + fuel, 2)
        diff = c["actual"] - expected
        status = "PASS" if abs(diff) <= Decimal("0.05") else "FAIL"
        results.append({
            "charge_id": f"CH-{c['id']}",
            "shipment_id": c["id"],
            "concept": "FLETE_TOTAL",
            "currency": "ARS",
            "expected": str(expected),
            "actual": str(c["actual"]),
            "difference": str(diff),
            "status": status,
            "formula": "quantize(max(500, kg * 15) * 1.085, 2)"
        })
    return results


def run_g2_oracle():
    """G2: Origen/Destino + Tipo de Vehículo + Vigencia."""
    lookup_v1 = {
        ("BUE", "ROS", "SEMIRREMOLQUE"): Decimal("450000.00"),
        ("BUE", "ROS", "CHASIS"): Decimal("280000.00"),
        ("BUE", "COR", "SEMIRREMOLQUE"): Decimal("680000.00"),
        ("BUE", "COR", "CHASIS"): Decimal("420000.00"),
    }
    lookup_v2 = {
        ("BUE", "ROS", "SEMIRREMOLQUE"): Decimal("540000.00"),
        ("BUE", "ROS", "CHASIS"): Decimal("336000.00"),
        ("BUE", "COR", "SEMIRREMOLQUE"): Decimal("816000.00"),
        ("BUE", "COR", "CHASIS"): Decimal("504000.00"),
    }

    cases = [
        {"id": "OP-G2-01", "date": "2026-03-15", "route": ("BUE", "ROS", "SEMIRREMOLQUE"), "actual": Decimal("450000.00")},
        {"id": "OP-G2-02", "date": "2026-08-20", "route": ("BUE", "ROS", "SEMIRREMOLQUE"), "actual": Decimal("450000.00")},
        {"id": "OP-G2-03", "date": "2026-09-10", "route": ("BUE", "COR", "CHASIS"), "actual": Decimal("504000.00")},
        {"id": "OP-G2-04", "date": "2026-04-10", "route": ("BUE", "MZA", "FURGON"), "actual": Decimal("350000.00")},
    ]

    results = []
    for c in cases:
        table = lookup_v1 if c["date"] <= "2026-06-30" else lookup_v2
        if c["route"] not in table:
            results.append({
                "charge_id": f"CH-{c['id']}",
                "shipment_id": c["id"],
                "concept": "FLETE_VIAJE",
                "currency": "ARS",
                "expected": None,
                "actual": str(c["actual"]),
                "difference": None,
                "status": "UNDETERMINABLE",
                "reason": "Ruta/vehículo no encontrado en tabla de búsqueda"
            })
            continue

        expected = quantize(table[c["route"]], 2)
        diff = c["actual"] - expected
        status = "PASS" if abs(diff) <= Decimal("0.05") else "FAIL"
        results.append({
            "charge_id": f"CH-{c['id']}",
            "shipment_id": c["id"],
            "concept": "FLETE_VIAJE",
            "currency": "ARS",
            "expected": str(expected),
            "actual": str(c["actual"]),
            "difference": str(diff),
            "status": status,
            "version_used": "V1" if c["date"] <= "2026-06-30" else "V2"
        })
    return results


def run_g3_oracle():
    """G3: Pallets + Adicional Condicionado por Evidencia."""
    pallet_rate = Decimal("85.00")

    cases = [
        {"id": "OP-G3-01", "pallets": Decimal("24"), "evidence_valid": True, "actual": Decimal("2040.00")},
        {"id": "OP-G3-02", "pallets": Decimal("10"), "evidence_valid": False, "actual": Decimal("850.00")},
        {"id": "OP-G3-03", "pallets": Decimal("15"), "evidence_valid": True, "actual": Decimal("1500.00")},
    ]

    results = []
    for c in cases:
        expected = quantize(c["pallets"] * pallet_rate, 2)
        diff = c["actual"] - expected
        if not c["evidence_valid"]:
            status = "REVIEW"
            reason = "Falta evidencia requerida (remito firmado)"
        else:
            status = "PASS" if abs(diff) <= Decimal("0.05") else "FAIL"
            reason = None
        results.append({
            "charge_id": f"CH-{c['id']}",
            "shipment_id": c["id"],
            "concept": "FLETE_PALLET",
            "currency": "ARS",
            "expected": str(expected),
            "actual": str(c["actual"]),
            "difference": str(diff),
            "status": status,
            "evidence_valid": c["evidence_valid"],
            "reason": reason
        })
    return results


def run_g4_oracle():
    """G4: Tarifación por Bandas/Tramos (USD)."""
    # Política: [lower, upper)
    bands = [
        (Decimal("0.00"), Decimal("100.00"), Decimal("45.00")),
        (Decimal("100.00"), Decimal("500.00"), Decimal("110.00")),
        (Decimal("500.00"), Decimal("1000.00"), Decimal("240.00")),
        (Decimal("1000.00"), None, Decimal("420.00")),
    ]

    cases = [
        {"id": "OP-G4-01", "weight": Decimal("50.00"), "actual": Decimal("45.00")},
        {"id": "OP-G4-02", "weight": Decimal("100.00"), "actual": Decimal("110.00")},
        {"id": "OP-G4-03", "weight": Decimal("500.00"), "actual": Decimal("110.00")},  # Error del facturador
        {"id": "OP-G4-04", "weight": Decimal("1500.00"), "actual": Decimal("420.00")},
    ]

    results = []
    for c in cases:
        w = c["weight"]
        selected_rate = None
        for low, high, rate in bands:
            if (low is None or w >= low) and (high is None or w < high):
                selected_rate = rate
                break
        assert selected_rate is not None, f"No band found for weight {w}"
        expected = quantize(selected_rate, 2)
        diff = c["actual"] - expected
        status = "PASS" if abs(diff) <= Decimal("0.05") else "FAIL"
        results.append({
            "charge_id": f"CH-{c['id']}",
            "shipment_id": c["id"],
            "concept": "AIR_FREIGHT",
            "currency": "USD",
            "weight_kg": str(w),
            "expected": str(expected),
            "actual": str(c["actual"]),
            "difference": str(diff),
            "status": status,
        })
    return results


def run_g5_oracle():
    """G5: Consolidación Real de Cardinalidad Distinta (N:1 y 1:N)."""
    rate_per_kg = Decimal("22.00")

    # N:1 - 3 shipments consolidate into 1 charge
    group_shipments = [
        {"id": "S-G5-01", "weight": Decimal("350.00")},
        {"id": "S-G5-02", "weight": Decimal("450.00")},
        {"id": "S-G5-03", "weight": Decimal("200.00")},
    ]
    total_weight = sum(s["weight"] for s in group_shipments)
    expected_n1 = quantize(total_weight * rate_per_kg, 2)
    actual_n1 = Decimal("22000.00")
    diff_n1 = actual_n1 - expected_n1
    status_n1 = "PASS" if abs(diff_n1) <= Decimal("0.05") else "FAIL"

    # 1:N - 1 shipment S-G5-04 has 2 charges
    expected_flete = Decimal("8000.00")
    actual_flete = Decimal("8000.00")
    expected_seguro = Decimal("1200.00")
    actual_seguro = Decimal("1200.00")

    results = [
        {
            "charge_id": "C-G5-01",
            "shipment_ids": [s["id"] for s in group_shipments],
            "cardinality": "N:1",
            "concept": "FLETE_CONSOLIDADO",
            "currency": "ARS",
            "total_weight_kg": str(total_weight),
            "expected": str(expected_n1),
            "actual": str(actual_n1),
            "difference": str(diff_n1),
            "status": status_n1,
        },
        {
            "charge_id": "C-G5-02",
            "shipment_ids": ["S-G5-04"],
            "cardinality": "1:N",
            "concept": "FLETE_TRAMO",
            "currency": "ARS",
            "expected": str(expected_flete),
            "actual": str(actual_flete),
            "difference": str(actual_flete - expected_flete),
            "status": "PASS",
        },
        {
            "charge_id": "C-G5-03",
            "shipment_ids": ["S-G5-04"],
            "cardinality": "1:N",
            "concept": "SEGURO_CARGA",
            "currency": "ARS",
            "expected": str(expected_seguro),
            "actual": str(actual_seguro),
            "difference": str(actual_seguro - expected_seguro),
            "status": "PASS",
        }
    ]
    return results


def run_g6_oracle():
    """G6: Recombinación Composicional (Zona + Vehículo + Mínimo + Evidencia + Vigencia)."""
    min_charge = Decimal("100000.00")
    lookup_v1 = {("NORTE", "SUR", "CHASIS"): Decimal("120000.00")}
    lookup_v2 = {("NORTE", "SUR", "CHASIS"): Decimal("150000.00")}

    cases = [
        {"id": "OP-G6-01", "date": "2026-03-20", "evidence": True, "actual": Decimal("120000.00")},
        {"id": "OP-G6-02", "date": "2026-04-15", "evidence": False, "actual": Decimal("120000.00")},
        {"id": "OP-G6-03", "date": "2026-08-10", "evidence": True, "actual": Decimal("120000.00")},
    ]

    results = []
    for c in cases:
        table = lookup_v1 if c["date"] <= "2026-06-30" else lookup_v2
        base = table[("NORTE", "SUR", "CHASIS")]
        expected = quantize(max(min_charge, base), 2)
        diff = c["actual"] - expected
        if not c["evidence"]:
            status = "REVIEW"
            reason = "Falta evidencia requerida (remito conforme)"
        else:
            status = "PASS" if abs(diff) <= Decimal("0.05") else "FAIL"
            reason = None
        results.append({
            "charge_id": f"CH-{c['id']}",
            "shipment_id": c["id"],
            "concept": "FLETE_COMPUESTO",
            "currency": "ARS",
            "expected": str(expected),
            "actual": str(c["actual"]),
            "difference": str(diff),
            "status": status,
            "evidence_valid": c["evidence"],
            "reason": reason
        })
    return results


def main():
    oracle_summary = {
        "status": "INDEPENDENT_ORACLES_FROZEN",
        "description": "Resultados esperados calculados de forma 100% independiente con Decimal puro.",
        "G1": run_g1_oracle(),
        "G2": run_g2_oracle(),
        "G3": run_g3_oracle(),
        "G4": run_g4_oracle(),
        "G5": run_g5_oracle(),
        "G6": run_g6_oracle(),
    }

    out_file = Path(__file__).parent / "frozen_expected.json"
    out_file.write_text(json.dumps(oracle_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Oráculo independiente ejecutado. Resultados congelados en {out_file}")


if __name__ == "__main__":
    main()
