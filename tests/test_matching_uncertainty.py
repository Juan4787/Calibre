"""Association failures must never certify a partial financial obligation."""

from collections import Counter
from copy import deepcopy
from decimal import Decimal
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from freight_audit.canonical import canonical
from freight_audit.engine import audit, matching_preflight
from freight_audit.models import Dataset
from freight_audit.reporting import html_report, workbook_bytes
from freight_audit.server import create_app


@pytest.fixture
def lot(raw_dataset):
    raw_dataset["shipments"] += [
        {**deepcopy(raw_dataset["shipments"][0]), "id": "S2", "reference": "00002"},
        {**deepcopy(raw_dataset["shipments"][0]), "id": "S3", "reference": "00003"},
        {**deepcopy(raw_dataset["shipments"][0]), "id": "FOREIGN", "carrier": "OTHER"},
    ]
    raw_dataset["charges"][0]["amount"] = "-100"
    raw_dataset["charges"] += [
        {**raw_dataset["charges"][0], "id": "C2", "amount": "150"},
        {**raw_dataset["charges"][0], "id": "C3", "reference": "00002", "amount": "120"},
        {**raw_dataset["charges"][0], "id": "INDEPENDENT", "reference": "00003", "amount": "130"},
    ]
    raw_dataset["agreements"][0]["matching"]["duplicate_fields"] = []
    return raw_dataset


def calculate(raw):
    return audit(Dataset.model_validate(raw))


def by_charge(result):
    return {cid: f for f in result.findings for cid in f.charge_ids}


@pytest.mark.parametrize(
    ("targets", "affected"),
    [
        (["S2", "MISSING"], {"S1", "S2"}),
        (["S2", "S2"], {"S1", "S2"}),
        (["S2", "FOREIGN"], {"S1", "S2"}),
        (["MISSING"], {"S1"}),
        ([], {"S1"}),
    ],
)
@pytest.mark.parametrize("settlement", ["L1", "OTHER-INVOICE"])
def test_invalid_link_protects_each_plausible_scope(lot, targets, affected, settlement):
    lot["agreements"][0]["matching"]["explicit"] = {"C1": targets}
    lot["charges"][1]["settlement"] = settlement
    result = calculate(lot)
    findings = by_charge(result)
    assert findings["C1"].status == "UNDETERMINABLE"
    assert set(findings["C1"].shipment_ids) == affected
    assert findings["C1"].actual == "-100"
    assert findings["C1"].expected is None and findings["C1"].difference is None
    for cid, sid in (("C2", "S1"), ("C3", "S2")):
        assert findings[cid].status == ("REVIEW" if sid in affected else "FAIL")
        assert findings[cid].confirmed_difference == ("0" if sid in affected else "20")
        if sid in affected:
            assert any(t.op == "matching_uncertainty" for t in findings[cid].trace)
    assert findings["INDEPENDENT"].confirmed_difference == "30"
    assert Counter(cid for f in result.findings for cid in f.charge_ids) == Counter(
        c["id"] for c in lot["charges"]
    )
    assert sum(Decimal(f.actual) for f in result.findings) == Decimal("300")
    permuted = deepcopy(lot)
    permuted["charges"].reverse()
    permuted["shipments"].reverse()
    assert canonical(calculate(permuted)) == canonical(result)


def test_negative_adjustment_cannot_reverse_a_confirmed_sign(lot):
    lot["charges"] = lot["charges"][:2]
    lot["agreements"][0]["matching"]["explicit"] = {"C1": ["S2", "MISSING"]}
    assert calculate(lot).summary["currencies"]["ARS"]["confirmed_net_difference"] == "0"
    lot["agreements"][0]["matching"]["explicit"] = {"C1": ["S1"]}
    corrected = calculate(lot)
    assert len(corrected.findings) == 1
    assert corrected.findings[0].actual == "50"
    assert corrected.summary["currencies"]["ARS"]["confirmed_net_difference"] == "-50"


@pytest.mark.parametrize("failure", ["invalid", "ambiguous"])
@pytest.mark.parametrize("valid_date", [True, False])
def test_uncertain_charge_is_not_also_reported_as_missing(lot, failure, valid_date):
    lot["charges"] = lot["charges"][:1]
    agreement = lot["agreements"][0]
    agreement["detect_missing"] = True
    agreement["versions"][0]["rules"][0]["expected"] = True
    lot["coverage"] = {"A": ["S1", "S2", "S3"]}
    if failure == "invalid":
        agreement["matching"]["explicit"] = {"C1": ["S2", "MISSING"]}
    else:
        lot["shipments"][1]["reference"] = "00001"
    if not valid_date:
        for s in lot["shipments"]:
            s["attributes"]["service_date"]["value"] = "2025-01-01"
    result = calculate(lot)
    assert len(result.findings) == 2
    missing = next(f for f in result.findings if not f.charge_ids)
    assert missing.shipment_ids == ["S3"]  # independent coverage remains observable
    assert result.summary["currencies"]["ARS"]["confirmed_net_difference"] == "0"


def test_invalid_link_without_keys_protects_valid_explicit_targets(lot):
    lot["charges"][0]["reference"] = "no-candidate"
    lot["agreements"][0]["matching"]["explicit"] = {"C1": ["S2", "MISSING"]}
    f = by_charge(calculate(lot))
    assert f["C1"].shipment_ids == ["S2"]
    assert f["C2"].status == "FAIL" and f["C3"].status == "REVIEW"


def test_unrelated_dimensions_and_failed_calculation_remain_distinct(lot):
    lot["agreements"][0]["matching"]["explicit"] = {"C1": ["S2", "MISSING"]}
    other = deepcopy(lot["agreements"][0])
    other.update(id="B", currency="USD")
    other["matching"]["explicit"] = {}
    other["versions"][0]["rules"][0]["expression"]["value"]["unit"] = "USD"
    lot["agreements"].append(other)
    lot["charges"].append({**lot["charges"][1], "id": "USD", "agreement": "B", "currency": "USD"})
    del lot["shipments"][1]["attributes"]["service_date"]
    f = by_charge(calculate(lot))
    assert f["USD"].confirmed_difference == "50"
    assert f["C3"].status == "UNDETERMINABLE" and f["C3"].confirmed_difference == "0"
    assert any(t.op == "matching_uncertainty" for t in f["C3"].trace)


def test_preflight_reports_invalid_ambiguous_and_unmatched_without_persisting(tmp_path, lot):
    lot["agreements"][0]["matching"]["explicit"] = {"C1": ["S2", "MISSING"]}
    lot["shipments"].append({**deepcopy(lot["shipments"][2]), "id": "S4"})
    lot["charges"].append({**lot["charges"][1], "id": "UNMATCHED", "reference": "unknown"})
    with TestClient(create_app(tmp_path / "preflight.db")) as client:
        client.headers["X-Freight-Local"] = client.get("/api/session").json()["token"]
        preview = client.post("/api/audit/preflight", json=lot).json()
        assert preview["total_issues"] == 3
        assert preview["counts"] == {"invalid": 1, "conflict": 0, "ambiguous": 1, "unmatched": 1}
        assert {e["charge_id"] for e in preview["issues"]} == {"C1", "INDEPENDENT", "UNMATCHED"}
        assert client.get("/api/runs").json() == []
        assert client.get("/api/configs").json() == []
        run_id = client.post("/api/audit", json=lot).json()["run_id"]
        run = client.get("/api/runs/" + run_id).json()
        assert run["result"]["summary"]["currencies"]["ARS"]["confirmed_net_difference"] == "0"
        assert client.post(f"/api/runs/{run_id}/replay").status_code == 200
        wb = load_workbook(BytesIO(workbook_bytes(run)))
        rows = list(wb["Hallazgos"].values)
        c2 = next(row for row in rows[1:] if row[2] == "C2")
        assert c2[8] == "0" and c2[9] == "Revisión humana"
        assert "Otra línea" in html_report(run)


def test_preflight_detail_limit_does_not_limit_uncertainty(lot):
    lot["charges"] = [{**lot["charges"][0], "id": f"C{i:03}"} for i in range(60)] + [lot["charges"][1]]
    lot["agreements"][0]["matching"]["explicit"] = {f"C{i:03}": ["S2", "MISSING"] for i in range(60)}
    ds = Dataset.model_validate(lot)
    preview = matching_preflight(ds)
    assert preview["total_issues"] == 60 and len(preview["issues"]) == 50
    result = audit(ds)
    assert len(result.findings) == 61
    assert by_charge(result)["C2"].confirmed_difference == "0"


@pytest.mark.parametrize("valid_date", [True, False])
def test_coverage_does_not_duplicate_an_explicit_consolidation(lot, valid_date):
    lot["charges"] = lot["charges"][:1]
    lot["charges"][0]["reference"] = "explicit-only"
    agreement = lot["agreements"][0]
    agreement["matching"]["explicit"] = {"C1": ["S1", "S2"]}
    agreement["detect_missing"] = True
    agreement["versions"][0]["rules"][0]["expected"] = True
    lot["coverage"] = {"A": ["S1", "S2", "S3"]}
    if not valid_date:
        for shipment in lot["shipments"]:
            shipment["attributes"]["service_date"]["value"] = "2025-01-01"
    result = calculate(lot)
    assert len(result.findings) == 2
    assert [f.shipment_ids for f in result.findings if not f.charge_ids] == [["S3"]]


def test_invalid_alias_candidates_and_other_concept_are_isolated(lot):
    agreement = lot["agreements"][0]
    agreement["matching"]["explicit"] = {"C1": ["MISSING"]}
    agreement["matching"]["keys"][0]["aliases"] = {"external": "00002"}
    lot["charges"][0]["reference"] = "external"
    other_rule = deepcopy(agreement["versions"][0]["rules"][0])
    other_rule.update(id="OTHER-RULE", concept="other")
    agreement["versions"][0]["rules"].append(other_rule)
    lot["charges"].append({**lot["charges"][2], "id": "OTHER-CONCEPT", "concept": "other"})
    f = by_charge(calculate(lot))
    assert f["C1"].shipment_ids == ["S2"]
    assert f["C2"].confirmed_difference == "50"
    assert f["C3"].confirmed_difference == "0"
    assert f["OTHER-CONCEPT"].confirmed_difference == "20"
