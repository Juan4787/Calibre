"""Meaningful bounded Hypothesis inputs, independent of production fixture builders."""

import os
from copy import deepcopy

from hypothesis import settings
from hypothesis import strategies as st

from .reference import price

for name, examples in (("smoke", 25), ("ci", 100), ("nightly", 1000)):
    settings.register_profile("qa-" + name, max_examples=examples, deadline=None)
settings.load_profile("qa-" + os.environ.get("QA_PROFILE", "smoke"))


def decimal_from_integer(value, scale=2):
    sign = "-" if value < 0 else ""
    digits = str(abs(value)).zfill(scale + 1)
    return sign + (digits if scale == 0 else digits[:-scale] + "." + digits[-scale:])


def constant(value, unit=None):
    return {"op": "const", "value": {"type": "decimal", "value": value, "unit": unit}}


def base_dataset():
    return {
        "label": "QA synthetic baseline",
        "shipments": [
            {
                "id": "S1",
                "reference": "00001",
                "carrier": "C",
                "attributes": {
                    "service_date": {"type": "date", "value": "2026-05-01"},
                    "weight": {"type": "decimal", "value": "10", "unit": "kg"},
                },
            }
        ],
        "charges": [
            {
                "id": "C1",
                "settlement": "L1",
                "carrier": "C",
                "agreement": "A",
                "reference": "00001",
                "concept": "base",
                "amount": "100",
                "currency": "ARS",
            }
        ],
        "agreements": [
            {
                "id": "A",
                "name": "QA fictional contract",
                "carrier": "C",
                "currency": "ARS",
                "date_field": "service_date",
                "scale": 2,
                "rounding": "ROUND_HALF_UP",
                "tolerance_absolute": "0.01",
                "tolerance_relative": "0",
                "matching": {
                    "keys": [{"charge": "reference", "shipment": "reference"}],
                    "cardinality": "one",
                    "duplicate_fields": [],
                },
                "versions": [
                    {
                        "id": "V1",
                        "valid_from": "2026-01-01",
                        "source_note": "Fictional QA only",
                        "rules": [
                            {
                                "id": "R1",
                                "concept": "base",
                                "description": "Fixed price",
                                "expression": constant("100", "ARS"),
                            }
                        ],
                    }
                ],
            }
        ],
    }


@st.composite
def price_cases(draw):
    quantity = decimal_from_integer(draw(st.integers(0, 100000)))
    rate = decimal_from_integer(draw(st.integers(-10000, 10000)))
    minimum = draw(st.one_of(st.none(), st.integers(-10000, 10000).map(decimal_from_integer)))
    percent_units = draw(st.integers(0, 40))
    surcharge = decimal_from_integer(percent_units)
    factor = decimal_from_integer(100 + percent_units)
    scale = draw(st.sampled_from([0, 2, 3, 8]))
    mode = draw(st.sampled_from(["ROUND_HALF_UP", "ROUND_HALF_EVEN", "ROUND_DOWN", "ROUND_UP"]))
    expected = price(
        quantity=quantity, rate=rate, minimum=minimum, surcharge=surcharge, scale=scale, mode=mode
    )
    raw = base_dataset()
    raw["shipments"][0]["attributes"]["weight"]["value"] = quantity
    expression = {
        "op": "mul",
        "args": [{"op": "attr", "field": "weight", "unit": "kg"}, constant(rate, "ARS/kg")],
    }
    if minimum is not None:
        expression = {"op": "max", "args": [expression, constant(minimum, "ARS")]}
    expression = {"op": "mul", "args": [expression, constant(factor)]}
    agreement = raw["agreements"][0]
    agreement.update(scale=scale, rounding=mode, tolerance_absolute="0")
    agreement["versions"][0]["rules"][0]["expression"] = expression
    raw["charges"][0]["amount"] = expected
    return raw, expected


def uncertain_variant(raw, cause):
    value = deepcopy(raw)
    if cause == "evidence":
        value["agreements"][0]["versions"][0]["rules"][0]["evidence"] = [
            {"any_of": ["approval"], "scope": "each_shipment", "document_required": True}
        ]
    elif cause == "ambiguous_match":
        value["shipments"].append({**deepcopy(value["shipments"][0]), "id": "S2"})
    elif cause == "overlap_version":
        value["agreements"][0]["versions"].append(
            {**deepcopy(value["agreements"][0]["versions"][0]), "id": "V2"}
        )
    elif cause == "missing_date":
        del value["shipments"][0]["attributes"]["service_date"]
    elif cause == "incomplete_import":
        value["issues"] = [{"category": "row", "message": "Synthetic rejected row", "row": 2}]
    else:
        raise ValueError("Unknown one-cause invalidation")
    return value
