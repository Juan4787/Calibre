from copy import deepcopy

import pytest

from freight_audit.fixtures import agreement, const, rule, version
from freight_audit.models import Dataset


@pytest.fixture
def raw_dataset():
    return {
        "label": "Prueba ficticia",
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
                "reference": "00001",
                "carrier": "C",
                "agreement": "A",
                "concept": "base",
                "amount": "100",
                "currency": "ARS",
            }
        ],
        "agreements": [agreement("A", "C", [version("V1", [rule("R1", "base", const("100", "ARS"))])])],
    }


@pytest.fixture
def make_dataset(raw_dataset):
    def factory(mutate=None):
        raw = deepcopy(raw_dataset)
        if mutate:
            mutate(raw)
        return Dataset.model_validate(raw)

    return factory
