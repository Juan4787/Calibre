"""ONR-001: independent association, conservation and financial safety oracles."""

from collections import Counter
from copy import deepcopy
from decimal import Decimal
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st
from openpyxl import load_workbook

from freight_audit.canonical import canonical
from freight_audit.engine import audit
from freight_audit.models import Dataset, Decision
from freight_audit.reporting import bundle_bytes, html_report, verify_bundle, workbook_bytes
from freight_audit.server import create_app
from freight_audit.storage import Store


@pytest.fixture
def conflicting(raw_dataset):
    raw = deepcopy(raw_dataset)
    raw["shipments"].append({**deepcopy(raw["shipments"][0]), "id": "S2", "reference": "00002"})
    raw["agreements"][0]["matching"].update(explicit={"C1": ["S2"]}, duplicate_fields=[])
    return raw


def compute(raw):
    return audit(Dataset.model_validate(raw))


def by_charge(result):
    return {cid: finding for finding in result.findings for cid in finding.charge_ids}


@pytest.mark.parametrize("amount", ["0", "50", "100", "200", "-50"])
def test_conflict_never_becomes_pass_or_confirms_money(conflicting, amount):
    conflicting["charges"][0]["amount"] = amount
    result = compute(conflicting)
    f = result.findings[0]
    assert (f.status, f.actual, f.expected, f.difference, f.confirmed_difference) == (
        "REVIEW",
        amount,
        None,
        None,
        "0",
    )
    assert f.shipment_ids == ["S1", "S2"]  # candidates, not an asserted allocation
    execution = f.trace[0].details["execution"][0]
    assert execution["comparison"] == "conflict"
    assert execution["shipment_ids"] == ["S2"]
    assert execution["key_candidate_ids"] == ["S1"]
    assert execution["keys"] == [{"field": "reference", "original": "00001", "resolved": "00001"}]
    assert result.summary["currencies"]["ARS"]["confirmed_net_difference"] == "0"


@pytest.mark.parametrize("settlement", ["L1", "OTHER-INVOICE"])
def test_conflict_protects_both_scopes_without_poisoning_unrelated_work(conflicting, settlement):
    raw = conflicting
    raw["shipments"].append({**deepcopy(raw["shipments"][0]), "id": "S3", "reference": "00003"})
    raw["charges"] += [
        {**raw["charges"][0], "id": "C2", "reference": "00002", "amount": "110", "settlement": settlement},
        {**raw["charges"][0], "id": "C3", "amount": "70", "settlement": settlement},
        {**raw["charges"][0], "id": "C4", "reference": "00003", "amount": "150"},
    ]
    result = compute(raw)
    charges = by_charge(result)
    assert {charges[cid].status for cid in ("C1", "C2", "C3")} == {"REVIEW"}
    assert charges["C1"].charge_ids == ["C1"]  # never aggregated into the explicit destination
    assert charges["C4"].status == "FAIL" and charges["C4"].confirmed_difference == "50"
    assert Counter(cid for f in result.findings for cid in f.charge_ids) == Counter(
        c["id"] for c in raw["charges"]
    )
    assert sum(Decimal(f.actual) for f in result.findings) == Decimal("430")
    assert result.summary["currencies"]["ARS"]["confirmed_overcharge"] == "50"
    for cid in ("C2", "C3"):
        trace = next(t for t in charges[cid].trace if t.op == "matching_uncertainty")
        assert trace.details["unresolved_charge_ids"] == ["C1"]
    raw["charges"].reverse()
    raw["shipments"].reverse()
    assert canonical(compute(raw)) == canonical(result)


@pytest.mark.parametrize(
    ("cardinality", "explicit", "expected_status"),
    [
        ("one", ["S2"], "PASS"),
        ("one", ["S1", "S2"], "PASS"),
        ("group", ["S1", "S2"], "PASS"),
        ("group", ["S2"], "REVIEW"),
        ("one", ["S2", "S3"], "REVIEW"),
        ("group", ["S1", "S2", "S3"], "REVIEW"),
    ],
)
def test_candidate_selection_and_group_completeness(raw_dataset, cardinality, explicit, expected_status):
    raw = raw_dataset
    raw["shipments"] += [
        {**deepcopy(raw["shipments"][0]), "id": "S2"},
        {**deepcopy(raw["shipments"][0]), "id": "S3", "reference": "other"},
    ]
    raw["agreements"][0]["matching"].update(cardinality=cardinality, explicit={"C1": explicit})
    f = compute(raw).findings[0]
    assert f.status == expected_status
    if expected_status == "REVIEW":
        assert f.expected is None and f.confirmed_difference == "0"


@pytest.mark.parametrize("reference", ["no-automatic-candidate", ""])
def test_explicit_without_key_candidates_requires_review(conflicting, reference):
    conflicting["charges"][0]["reference"] = reference
    f = compute(conflicting).findings[0]
    assert f.status == "REVIEW" and f.shipment_ids == ["S2"]
    assert f.expected is None and f.confirmed_difference == "0"
    assert f.trace[0].details["execution"][0]["comparison"] == "uncorroborated"


def test_aliases_are_applied_before_conflict_comparison(conflicting):
    conflicting["agreements"][0]["matching"]["keys"][0]["aliases"] = {"00001": "00002"}
    f = compute(conflicting).findings[0]
    assert f.status == "PASS" and f.shipment_ids == ["S2"]
    assert f.trace[0].details["execution"][0]["comparison"] == "compatible"


def test_composite_alias_keys_are_compared_as_a_whole(conflicting):
    raw = conflicting
    raw["charges"][0]["attributes"] = {"batch": {"type": "text", "value": "external"}}
    for shipment, batch in zip(raw["shipments"], ("A", "B"), strict=True):
        shipment["reference"] = "00001"
        shipment["attributes"]["batch"] = {"type": "text", "value": batch}
    raw["agreements"][0]["matching"]["keys"].append(
        {"charge": "attributes.batch", "shipment": "attributes.batch", "aliases": {"external": "A"}}
    )
    before = canonical(raw)
    f = compute(raw).findings[0]
    assert f.status == "REVIEW"
    assert f.trace[0].details["execution"][0]["key_candidate_ids"] == ["S1"]
    assert canonical(raw) == before


def test_conflict_does_not_cross_agreement_concept_or_currency(conflicting):
    raw = conflicting
    for aid, currency in (("B", "ARS"), ("USD-A", "USD")):
        agreement = deepcopy(raw["agreements"][0])
        agreement.update(id=aid, currency=currency)
        agreement["matching"]["explicit"] = {}
        agreement["versions"][0]["rules"][0]["expression"]["value"]["unit"] = currency
        raw["agreements"].append(agreement)
        raw["charges"].append(
            {**raw["charges"][0], "id": aid, "agreement": aid, "currency": currency, "amount": "130"}
        )
    other_rule = deepcopy(raw["agreements"][0]["versions"][0]["rules"][0])
    other_rule.update(id="OTHER-RULE", concept="other")
    raw["agreements"][0]["versions"][0]["rules"].append(other_rule)
    raw["charges"].append({**raw["charges"][0], "id": "OTHER-CONCEPT", "concept": "other", "amount": "130"})
    result = compute(raw)
    for cid in ("B", "USD-A", "OTHER-CONCEPT"):
        f = by_charge(result)[cid]
        assert (f.status, f.confirmed_difference) == ("FAIL", "30")
    assert result.summary["currencies"]["ARS"]["confirmed_net_difference"] == "60"
    assert result.summary["currencies"]["USD"]["confirmed_net_difference"] == "30"


def test_coverage_does_not_invent_missing_charges_for_conflicted_obligations(conflicting):
    a = conflicting["agreements"][0]
    a["detect_missing"] = True
    a["versions"][0]["rules"][0]["expected"] = True
    conflicting["coverage"] = {"A": ["S1", "S2"]}
    result = compute(conflicting)
    assert len(result.findings) == 1
    assert result.findings[0].charge_ids == ["C1"]
    for s in conflicting["shipments"]:
        s["attributes"]["service_date"]["value"] = "2025-01-01"
    assert len(compute(conflicting).findings) == 1


def test_related_calculation_failure_retains_conflict_explanation(conflicting):
    conflicting["charges"].append({**conflicting["charges"][0], "id": "C2", "reference": "00002"})
    conflicting["shipments"][1]["attributes"].pop("service_date")
    f = by_charge(compute(conflicting))["C2"]
    assert f.status == "UNDETERMINABLE" and f.confirmed_difference == "0"
    assert any("vinculación" in reason for reason in f.reasons)
    assert any(t.op == "matching_uncertainty" for t in f.trace)


def test_preflight_is_read_only_and_audit_cannot_bypass_conflicts(tmp_path, conflicting):
    path = tmp_path / "api.sqlite"
    with TestClient(create_app(path)) as client:
        assert client.post("/api/audit/preflight", json=conflicting).status_code == 403
        client.headers["X-Freight-Local"] = client.get("/api/session").json()["token"]
        assert client.post("/api/audit/preflight", json={}).status_code == 422
        assert (
            client.post(
                "/api/audit/preflight", json=conflicting, headers={"Origin": "https://foreign.example"}
            ).status_code
            == 403
        )
        response = client.post("/api/audit/preflight", json=conflicting)
        assert response.status_code == 200, response.text
        preview = response.json()
        assert preview["total_conflicts"] == 1
        assert preview["conflicts"][0]["key_candidate_ids"] == ["S1"]
        assert preview["conflicts"][0]["shipment_ids"] == ["S2"]
        store = Store(path)
        with store.connect() as connection:
            for table in ("runs", "sources", "configs", "decisions"):
                assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
        run_id = client.post("/api/audit", json=conflicting).json()["run_id"]
        run = client.get(f"/api/runs/{run_id}").json()
        f = run["result"]["findings"][0]
        assert (f["status"], f["confirmed_difference"]) == ("REVIEW", "0")
        assert f["trace"][0]["details"]["execution"][0] == preview["conflicts"][0]


def test_preview_limit_is_visible_and_never_limits_engine_protection(tmp_path, conflicting):
    conflicting["charges"] = [{**conflicting["charges"][0], "id": f"C{i:03}"} for i in range(60)]
    conflicting["agreements"][0]["matching"]["explicit"] = {c["id"]: ["S2"] for c in conflicting["charges"]}
    with TestClient(create_app(tmp_path / "bounded.sqlite")) as client:
        client.headers["X-Freight-Local"] = client.get("/api/session").json()["token"]
        preview = client.post("/api/audit/preflight", json=conflicting).json()
        assert preview["total_conflicts"] == 60 and len(preview["conflicts"]) == 50
    result = compute(conflicting)
    assert len(result.findings) == 60
    assert {f.status for f in result.findings} == {"REVIEW"}
    assert result.summary["currencies"]["ARS"]["actual"] == "6000"
    assert result.summary["currencies"]["ARS"]["confirmed_net_difference"] == "0"


def test_decisions_correction_exports_and_replay_preserve_uncertainty(tmp_path, conflicting):
    store = Store(tmp_path / "history.sqlite")
    dataset = Dataset.model_validate(conflicting)
    run_id = store.save(dataset, audit(dataset))
    original = store.load(run_id)
    finding = original["result"]["findings"][0]
    store.add_decision(
        run_id,
        Decision(
            finding_id=finding["id"],
            action="EXCEPTION_ACCEPTED",
            actor="Prueba",
            note="No transforma incertidumbre en dinero",
        ),
    )
    after = store.load(run_id)
    assert after["result_hash"] == original["result_hash"]
    assert after["result"] == original["result"]
    workbook = load_workbook(BytesIO(workbook_bytes(after)), data_only=False)
    row = list(workbook["Hallazgos"].values)[1]
    assert row[5:10] == ("100", None, None, "0", "Revisión humana")
    assert "Revisión humana" in html_report(after)
    assert verify_bundle(bundle_bytes(store, run_id))["result"] == original["result"]
    assert store.replay(run_id)["identical"]
    conflicting["agreements"][0]["matching"]["explicit"] = {"C1": ["S1"]}
    corrected = Dataset.model_validate(conflicting)
    corrected_id = store.save(corrected, audit(corrected))
    assert corrected_id != run_id
    assert store.load(corrected_id)["result"]["findings"][0]["status"] == "PASS"
    assert store.load(run_id)["result"] == original["result"]


@settings(max_examples=40, deadline=None)
@given(
    cardinality=st.sampled_from(["one", "group"]),
    targets=st.sets(st.sampled_from(["S1", "S2", "S3"]), min_size=1),
)
def test_explicit_set_relation_oracle(cardinality, targets):
    from freight_audit.fixtures import agreement, const, rule, version

    data = {
        "label": "Synthetic independent set oracle",
        "shipments": [
            {
                "id": sid,
                "reference": "key" if sid in {"S1", "S2"} else "other",
                "carrier": "C",
                "attributes": {"service_date": {"type": "date", "value": "2026-05-01"}},
            }
            for sid in ("S1", "S2", "S3")
        ],
        "charges": [
            {
                "id": "C1",
                "reference": "key",
                "carrier": "C",
                "agreement": "A",
                "settlement": "L",
                "currency": "ARS",
                "concept": "base",
                "amount": "100",
            }
        ],
        "agreements": [agreement("A", "C", [version("V", [rule("R", "base", const("100", "ARS"))])])],
    }
    data["agreements"][0]["matching"].update(
        cardinality=cardinality, explicit={"C1": sorted(targets, reverse=True)}
    )
    # Independent finite set oracle, no call to matching/key helpers.
    compatible = targets <= {"S1", "S2"} if cardinality == "one" else targets == {"S1", "S2"}
    result = compute(data)
    assert result.findings[0].status == ("PASS" if compatible else "REVIEW")
    reordered = deepcopy(data)
    reordered["agreements"][0]["matching"]["explicit"]["C1"].reverse()
    reordered["shipments"].reverse()
    other = compute(reordered)
    # The raw configuration hash legitimately changes with the list ordering.
    # Financial semantics and the executed comparison must not change.
    assert other.summary == result.summary
    assert other.findings[0].model_dump(exclude={"trace"}) == result.findings[0].model_dump(exclude={"trace"})
    assert other.findings[0].trace[0].details["execution"] == result.findings[0].trace[0].details["execution"]
