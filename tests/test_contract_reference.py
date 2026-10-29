"""Hand-calculated semantic anchors, independent of production calculation code.

Expectations are literals with the calculation written alongside them. Matching,
version, rule and membership are asserted too: an equal accidental price is insufficient.
"""

from copy import deepcopy

import pytest

from freight_audit.engine import audit
from freight_audit.fixtures import attr, const, op
from freight_audit.models import Dataset


@pytest.mark.parametrize(
    ("expression", "expected", "calculation"),
    [
        (op("mul", attr("weight", "kg"), const("12", "ARS/kg")), "120", "10 kg * 12 = 120"),
        (
            op("max", op("mul", attr("weight", "kg"), const("7", "ARS/kg")), const("90", "ARS")),
            "90",
            "max(10*7,90)=90",
        ),
        (op("mul", const("90", "ARS"), const("1.05")), "94.5", "90 + 5% = 94.5"),
        (
            op(
                "if",
                op("gte", attr("weight", "kg"), const("10", "kg")),
                const("120", "ARS"),
                const("80", "ARS"),
            ),
            "120",
            "10 >= 10 selects 120",
        ),
        (
            op("div", const("-5", "ARS"), const("2"), scale=0, rounding="ROUND_HALF_EVEN"),
            "-2",
            "-2.5 to even integer = -2",
        ),
        (
            op("div", const("-5", "ARS"), const("2"), scale=0, rounding="ROUND_HALF_UP"),
            "-3",
            "-2.5 away at tie = -3",
        ),
        (
            op(
                "add",
                op("round", const("0.005", "ARS"), scale=2, rounding="ROUND_HALF_UP"),
                op("round", const("0.005", "ARS"), scale=2, rounding="ROUND_HALF_UP"),
            ),
            "0.02",
            "0.01 + 0.01 = 0.02",
        ),
        (
            op("add", const("0.005", "ARS"), const("0.005", "ARS")),
            "0.01",
            "0.005 + 0.005 then currency round = 0.01",
        ),
    ],
)
def test_handwritten_price_and_semantic_identity(raw_dataset, expression, expected, calculation):
    raw_dataset["charges"][0]["amount"] = expected
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["expression"] = expression
    f = audit(Dataset.model_validate(raw_dataset)).findings[0]
    assert (f.status, f.expected, f.confirmed_difference) == ("PASS", expected, "0"), calculation
    assert (f.shipment_ids, f.charge_ids, f.version, f.rule) == (["S1"], ["C1"], "V1", "R1")


@pytest.mark.parametrize(
    ("weight", "expected"), [("0", "100"), ("9.999", "100"), ("10", "200"), ("19.999", "200"), ("20", None)]
)
def test_band_reference_boundaries(raw_dataset, weight, expected):
    raw_dataset["shipments"][0]["attributes"]["weight"]["value"] = weight
    v = raw_dataset["agreements"][0]["versions"][0]
    v["rules"][0]["expression"] = op("band", attr("weight", "kg"), table="bands")
    v["tables"] = {
        "bands": {
            "kind": "band",
            "unit": "kg",
            "bands": [
                {"lower": "0", "upper": "10", "value": {"type": "decimal", "value": "100", "unit": "ARS"}},
                {"lower": "10", "upper": "20", "value": {"type": "decimal", "value": "200", "unit": "ARS"}},
            ],
        }
    }
    raw_dataset["charges"][0]["amount"] = expected or "100"
    f = audit(Dataset.model_validate(raw_dataset)).findings[0]
    assert f.expected == expected
    assert f.status == ("PASS" if expected else "UNDETERMINABLE")


def test_lookup_and_consolidation_reference(raw_dataset):
    raw_dataset["shipments"].append(deepcopy(raw_dataset["shipments"][0]))
    raw_dataset["shipments"][1]["id"] = "S2"
    raw_dataset["shipments"][1]["attributes"]["weight"]["value"] = "20"
    raw_dataset["agreements"][0]["matching"]["cardinality"] = "group"
    v = raw_dataset["agreements"][0]["versions"][0]
    v["rules"][0]["expression"] = op(
        "mul", {"op": "sum", "field": "weight", "unit": "kg"}, op("lookup", attr("reference"), table="rates")
    )
    v["tables"] = {
        "rates": {
            "kind": "lookup",
            "rows": [{"keys": ["00001"], "value": {"type": "decimal", "value": "11", "unit": "ARS/kg"}}],
        }
    }
    raw_dataset["charges"][0]["amount"] = "330"  # (10+20)*11, one obligation.
    f = audit(Dataset.model_validate(raw_dataset)).findings[0]
    assert (f.status, f.expected, f.shipment_ids) == ("PASS", "330", ["S1", "S2"])
    v["tables"]["rates"]["rows"].append(deepcopy(v["tables"]["rates"]["rows"][0]))
    f = audit(Dataset.model_validate(raw_dataset)).findings[0]
    assert f.status == "UNDETERMINABLE" and f.expected is None
