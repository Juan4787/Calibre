"""Compare a saved audit with independently supplied document and total controls."""

import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation

from .invariants import integrity_errors


def _amount(value):
    if not isinstance(value, str):
        raise ValueError("External amounts must be decimal strings")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("External amount is not a decimal string") from exc
    if not number.is_finite():
        raise ValueError("External amount is not finite")
    return number


def _count(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("External counts must be non-negative integers")
    return value


def _counts(value):
    if not isinstance(value, dict):
        raise ValueError("External counts must be an object")
    return {key: _count(count) for key, count in value.items()}


def _totals(value):
    if not isinstance(value, dict):
        raise ValueError("External totals must be an object")
    return {currency: _amount(amount) for currency, amount in value.items()}


def compare_external_control(run: dict, control: dict) -> dict:
    """This cannot prove that the independently prepared control is complete or true."""
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
    if not isinstance(control, dict) or set(control) != required:
        raise ValueError("External control has missing or unexpected fields")
    if control["schema"] != "freight-audit-external-control/v1":
        raise ValueError("Unsupported external control schema")
    sources = control["source_hashes"]
    if (
        not isinstance(sources, list)
        or any(not isinstance(item, str) or not re.fullmatch(r"[0-9a-f]{64}", item) for item in sources)
        or len(sources) != len(set(sources))
    ):
        raise ValueError("External source inventory must contain distinct SHA-256 identifiers")
    expected_shipments = _counts(control["shipments_by_source"])
    expected_charges = _counts(control["charges_by_source"])
    if not isinstance(control["charge_totals_by_source"], dict):
        raise ValueError("External per-source totals must be an object")
    expected_source_totals = {
        source: _totals(totals) for source, totals in control["charge_totals_by_source"].items()
    }
    expected_currency_totals = _totals(control["actual_by_currency"])
    shipment_count = _count(control["shipment_count"])
    charge_count = _count(control["charge_count"])
    errors = integrity_errors(run)
    snapshot = run["snapshot"]
    recorded_sources = set(snapshot["documents"])
    if recorded_sources != set(sources):
        errors.append("External source inventory differs from the saved audit")
    actual_shipments: Counter[str] = Counter()
    actual_charges: Counter[str] = Counter()
    actual_source_totals: defaultdict[str, defaultdict[str, Decimal]] = defaultdict(
        lambda: defaultdict(Decimal)
    )
    actual_currency_totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for role, records, field, counter in (
        ("shipment", snapshot["shipments"], "id", actual_shipments),
        ("charge", snapshot["charges"], "amount", actual_charges),
    ):
        for record in records:
            ref = record.get("provenance", {}).get(field)
            if not isinstance(ref, dict) or ref.get("document") not in recorded_sources:
                errors.append(f"{role} {record.get('id', '?')} lacks source provenance")
                continue
            source = ref["document"]
            counter[source] += 1
            if role == "charge":
                amount = _amount(record["amount"])
                currency = record["currency"]
                actual_source_totals[source][currency] += amount
                actual_currency_totals[currency] += amount
    if dict(actual_shipments) != expected_shipments or len(snapshot["shipments"]) != shipment_count:
        errors.append("External shipment counts differ from the saved audit")
    if dict(actual_charges) != expected_charges or len(snapshot["charges"]) != charge_count:
        errors.append("External charge counts differ from the saved audit")
    if {source: dict(totals) for source, totals in actual_source_totals.items()} != expected_source_totals:
        errors.append("External per-source charge totals differ from the saved audit")
    if dict(actual_currency_totals) != expected_currency_totals:
        errors.append("External currency totals differ from the saved audit")
    summary = run["result"]["summary"]
    if not summary.get("import_complete", False):
        errors.append("Saved audit contains rejected or incomplete import rows")
    summarized = {currency: _amount(bucket["actual"]) for currency, bucket in summary["currencies"].items()}
    if summarized != expected_currency_totals:
        errors.append("Saved summary differs from external currency totals")
    return {
        "passed": not errors,
        "errors": errors,
        "observed": {
            "source_hashes": sorted(recorded_sources),
            "shipment_count": len(snapshot["shipments"]),
            "charge_count": len(snapshot["charges"]),
            "actual_by_currency": {key: str(value) for key, value in sorted(actual_currency_totals.items())},
        },
        "scope": "Independent input required; comparison cannot establish that external documents or controls are complete",
    }
