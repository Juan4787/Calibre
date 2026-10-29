"""Exact comparison with independently supplied documentary inventory and totals.

No imports from the pricing interpreter or summary: expected values are supplied
by the operator. This cannot establish truth/completeness of that external source.
"""

import re
from collections import Counter, defaultdict
from fractions import Fraction

from .models import Charge, Dataset


def documentary_control(dataset: Dataset) -> dict:
    control = dataset.external_control
    scope = (
        "Control externo aportado por el responsable; no certifica autenticidad ni fidelidad del contrato."
    )
    if control is None:
        return {"status": "not_supplied", "problems": [], "scope": scope}
    required = {
        "schema",
        "source_hashes",
        "shipments_by_source",
        "charges_by_source",
        "charge_totals_by_source",
        "shipment_count",
        "charge_count",
        "actual_by_currency",
    }
    if set(control) != required or control["schema"] != "freight-audit-external-control/v1":
        raise ValueError(
            "El control documental no tiene el formato requerido; revisar inventario, cantidades e importes."
        )

    def count(value):
        if type(value) is not int or value < 0:
            raise ValueError("Las cantidades del control deben ser enteros no negativos.")
        return value

    def counts(value):
        if not isinstance(value, dict) or any(
            not isinstance(k, str) or not re.fullmatch(r"[0-9a-f]{64}", k) for k in value
        ):
            raise ValueError("Las cantidades por archivo requieren identificadores de documentos válidos.")
        return {k: count(v) for k, v in value.items()}

    def totals(value):
        if not isinstance(value, dict):
            raise ValueError("Los totales del control deben estar separados por moneda.")
        result = {}
        for currency, amount in value.items():
            if (
                not isinstance(currency, str)
                or not re.fullmatch(r"[A-Z]{3}", currency)
                or not isinstance(amount, str)
                or len(amount) > 250
                or not re.fullmatch(r"-?\d+(?:\.\d+)?", amount)
            ):
                raise ValueError("El control requiere monedas y montos decimales exactos como texto.")
            result[currency] = Fraction(amount)
        return result

    inventory = control["source_hashes"]
    if (
        not isinstance(inventory, list)
        or any(not isinstance(h, str) or not re.fullmatch(r"[0-9a-f]{64}", h) for h in inventory)
        or len(set(inventory)) != len(inventory)
    ):
        raise ValueError("El inventario del control debe contener documentos válidos sin repetir.")
    expected_s = counts(control["shipments_by_source"])
    expected_c = counts(control["charges_by_source"])
    if not isinstance(control["charge_totals_by_source"], dict):
        raise ValueError("Indicar totales por archivo y moneda en el control documental.")
    expected_by_source = {h: totals(v) for h, v in control["charge_totals_by_source"].items()}
    expected_total = totals(control["actual_by_currency"])
    expected_shipments = count(control["shipment_count"])
    expected_charges = count(control["charge_count"])
    originals = set(dataset.documents)
    originals.update(
        r.document
        for records in (dataset.shipments, dataset.charges)
        for record in records
        for r in record.provenance.values()
    )
    originals.update(e.document_hash for e in dataset.evidence if e.document_hash)
    originals.update(c.document_hash for c in dataset.contract_sources)
    shipments: Counter = Counter()
    charges: Counter = Counter()
    by_source: dict = defaultdict(lambda: defaultdict(Fraction))
    actual_total: dict = defaultdict(Fraction)
    problems = []
    for records, field, counter in (
        (dataset.shipments, "id", shipments),
        (dataset.charges, "amount", charges),
    ):
        for record in records:
            citation = record.provenance.get(field)
            if citation is None:
                problems.append("Hay registros sin origen suficiente para contrastar el control documental.")
                continue
            counter[citation.document] += 1
            if isinstance(record, Charge):
                by_source[citation.document][record.currency] += Fraction(record.amount)
                actual_total[record.currency] += Fraction(record.amount)
    if originals != set(inventory):
        problems.append("El inventario de originales difiere del control independiente.")
    if dict(shipments) != expected_s or len(dataset.shipments) != expected_shipments:
        problems.append("La cantidad de operaciones difiere del control independiente.")
    if dict(charges) != expected_c or len(dataset.charges) != expected_charges:
        problems.append("La cantidad de cargos difiere del control independiente.")
    if {h: dict(v) for h, v in by_source.items()} != expected_by_source:
        problems.append("Los importes por archivo difieren del control independiente.")
    if dict(actual_total) != expected_total:
        problems.append("Los importes por moneda difieren del control independiente.")
    if any(i.category in {"file", "mapping", "row"} for i in dataset.issues):
        problems.append("Hay filas rechazadas o errores de importación pendientes.")
    return {
        "status": "matched" if not problems else "mismatch",
        "problems": sorted(set(problems)),
        "scope": scope,
    }
