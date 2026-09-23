from copy import deepcopy

from freight_audit.engine import audit
from freight_audit.models import Dataset


def test_rebilling_same_operation_in_other_invoice_is_not_independent_pass(raw_dataset):
    # Optional duplicate heuristics cannot be the only defense of obligation scope.
    raw_dataset["agreements"][0]["matching"]["duplicate_fields"] = []
    second = deepcopy(raw_dataset["charges"][0])
    second.update(id="C2", settlement="L2")
    raw_dataset["charges"].append(second)
    result = audit(Dataset.model_validate(raw_dataset))
    assert len(result.findings) == 2
    assert {f.status for f in result.findings} == {"REVIEW"}
    assert all(f.confirmed_difference == "0" for f in result.findings)
    assert result.summary["currencies"]["ARS"]["actual"] == "200"


def test_separate_operations_on_separate_invoices_still_pass(raw_dataset):
    second_shipment = deepcopy(raw_dataset["shipments"][0])
    second_shipment.update(id="S2", reference="00002")
    raw_dataset["shipments"].append(second_shipment)
    second_charge = deepcopy(raw_dataset["charges"][0])
    second_charge.update(id="C2", settlement="L2", reference="00002")
    raw_dataset["charges"].append(second_charge)
    result = audit(Dataset.model_validate(raw_dataset))
    assert len(result.findings) == 2
    assert {f.status for f in result.findings} == {"PASS"}


def test_canonical_download_endpoint_matches_preserved_run(tmp_path, make_dataset):
    from fastapi.testclient import TestClient

    from freight_audit.server import create_app
    from freight_audit.storage import Store

    path = tmp_path / "api.db"
    store = Store(path)
    dataset = make_dataset()
    identifier = store.save(dataset, audit(dataset))
    with TestClient(create_app(path)) as client:
        response = client.get(f"/api/runs/{identifier}/export/canonical")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.json() == store.load(identifier)


def test_cross_settlement_impact_inventory_is_read_only(raw_dataset, tmp_path):
    from freight_audit.storage import Store
    from qa.impact import inventory

    path = tmp_path / "historical.db"
    second = {**raw_dataset["charges"][0], "id": "C2", "settlement": "L2"}
    raw_dataset["charges"].append(second)
    dataset = Dataset.model_validate(raw_dataset)
    store = Store(path)
    identifier = store.save(dataset, audit(dataset))
    before = path.read_bytes()
    result = inventory(path, {"feature": "cross_settlement"})
    assert identifier in {candidate["run_id"] for candidate in result["candidates"]}
    assert path.read_bytes() == before
