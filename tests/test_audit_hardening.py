"""Causal regressions from the independent audit; all sources are synthetic."""

from copy import deepcopy
from decimal import localcontext
from io import BytesIO

import pytest
import xlwt
from fastapi.testclient import TestClient
from pydantic import ValidationError
from test_importing import csv_data, mapping

from freight_audit.engine import audit, matching_preflight
from freight_audit.fixtures import attr, const, op
from freight_audit.importing import ImportErrorDetail, import_data
from freight_audit.models import Dataset
from freight_audit.reporting import bundle_bytes, verify_bundle
from freight_audit.server import create_app
from freight_audit.storage import Store
from qa.external_control import compare_external_control


@pytest.mark.parametrize("fmt", ["%d/%m/%Y %H:%M:%S%z", "%Y-%m-%dT%H:%M", "%Y/%m/%d %Z", "%Y/%m/%d/%Y"])
def test_mapping_rejects_non_civil_or_repeated_date_directives(fmt):
    with pytest.raises(ValidationError):
        mapping(date_formats=[fmt])


@pytest.mark.parametrize("reference", ["99999", ""])
@pytest.mark.parametrize("amount", ["100", "130", "-100"])
def test_uncorroborated_explicit_never_confirms(raw_dataset, reference, amount):
    raw_dataset["charges"][0].update(reference=reference, amount=amount)
    raw_dataset["agreements"][0]["matching"]["explicit"] = {"C1": ["S1"]}
    ds = Dataset.model_validate(raw_dataset)
    f = audit(ds).findings[0]
    assert (f.status, f.actual, f.expected, f.confirmed_difference) == ("REVIEW", amount, None, "0")
    preflight = matching_preflight(ds)
    assert preflight["total_issues"] == 1
    assert preflight["counts"]["uncorroborated"] == 1


def test_uncorroborated_adjustment_protects_related_obligation(raw_dataset):
    raw_dataset["charges"][0].update(reference="99999", amount="-100")
    raw_dataset["charges"].append(
        {**raw_dataset["charges"][0], "id": "C2", "reference": "00001", "amount": "150"}
    )
    raw_dataset["agreements"][0]["matching"].update(explicit={"C1": ["S1"]}, duplicate_fields=[])
    result = audit(Dataset.model_validate(raw_dataset))
    assert {f.status for f in result.findings} == {"REVIEW"}
    assert result.summary["currencies"]["ARS"]["actual"] == "50"
    assert result.summary["currencies"]["ARS"]["confirmed_net_difference"] == "0"


def test_date_text_comparison_is_not_a_typed_match(raw_dataset):
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["when"] = op(
        "eq", attr("service_date"), const("2026-05-01", kind="text")
    )
    f = audit(Dataset.model_validate(raw_dataset)).findings[0]
    assert f.status == "UNDETERMINABLE" and f.confirmed_difference == "0"


@pytest.mark.parametrize("mode", ["row", "column", "sheet"])
def test_xls_hidden_data_obeys_same_policy_as_xlsx(mode):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Data")
    if mode == "sheet":
        workbook.add_sheet("Visible")
        sheet.visibility = 1
    for r, values in enumerate([["id", "ref", "weight", "date"], ["S1", "00001", "10", "01/05/2026"]]):
        for c, value in enumerate(values):
            sheet.write(r, c, value)
    if mode == "row":
        sheet.row(1).hidden = True
    if mode == "column":
        sheet.col(2).hidden = True
    data = BytesIO()
    workbook.save(data)
    with pytest.raises(ImportErrorDetail, match="ocult"):
        import_data(data.getvalue(), "hidden.xls", mapping(sheet="Data", allow_xls_cached_values=True))


@pytest.mark.parametrize("alteration", ["value", "raw", "row", "column", "transform", "constant"])
def test_save_rejects_provenance_or_normalized_value_changed_after_import(tmp_path, raw_dataset, alteration):
    data = csv_data("S1;00001;9;01/05/2026\n")
    config = mapping()
    imported = import_data(data, "source.csv", config)
    raw_dataset.update(
        shipments=imported["records"],
        mappings=[config.model_dump(mode="json")],
        documents={imported["document"]: "source.csv"},
    )
    record = raw_dataset["shipments"][0]
    ref = record["provenance"]["attributes.weight"]
    if alteration == "value":
        record["attributes"]["weight"]["value"] = "10"
    elif alteration == "raw":
        ref["raw"] = "10"
    elif alteration == "row":
        ref["row"] = 3
    elif alteration == "column":
        ref["column"] = "date"
    elif alteration == "transform":
        ref["transform"] = "unrecorded@1:decimal"
    else:
        record["carrier"] = "OTHER"
    store = Store(tmp_path / "sources.db")
    store.put_source(data)
    ds = Dataset.model_validate(raw_dataset)
    rejected = False
    try:
        store.save(ds, audit(ds))
    except ValueError as error:
        assert any(word in str(error) for word in ("original", "procedencia", "origen"))
        rejected = True
    assert rejected, "Changed imported value or citation must not be conserved as original-backed"


def test_every_export_checks_originals(tmp_path, raw_dataset):
    path = tmp_path / "corruption.db"
    store = Store(path)
    source = store.put_source(b"synthetic original")
    raw_dataset["documents"] = {source: "original.txt"}
    ds = Dataset.model_validate(raw_dataset)
    rid = store.save(ds, audit(ds))
    with store.connect() as conn:
        conn.execute("DROP TRIGGER immutable_sources_UPDATE")
        conn.execute("UPDATE sources SET data=?", (b"corrupt",))
    with TestClient(create_app(path), raise_server_exceptions=False) as client:
        for fmt in ("canonical", "html", "xlsx", "zip"):
            assert client.get(f"/api/runs/{rid}/export/{fmt}").status_code == 422, fmt


def test_xml_control_character_keeps_complete_bundle(tmp_path, raw_dataset):
    data = csv_data("S1;00001;10;01/05/2026\n")
    raw_dataset["label"] = "synthetic XML boundary"
    imported = import_data(data, "source.csv", mapping())
    raw_dataset["shipments"] = imported["records"]
    raw_dataset["shipments"][0]["attributes"]["note"] = {"type": "text", "value": "bad\x01value"}
    raw_dataset["evidence"] = [{"id": "E", "kind": "note", "shipment_ids": ["S1"], "note": "bad\x01value"}]
    store = Store(tmp_path / "xml.db")
    store.put_source(data)
    ds = Dataset.model_validate(raw_dataset)
    rid = store.save(ds, audit(ds))
    run = verify_bundle(bundle_bytes(store, rid))
    assert run["snapshot"]["evidence"][0]["note"] == "bad\x01value"


def test_external_control_exact_independent_of_decimal_context(tmp_path, raw_dataset):
    store = Store(tmp_path / "external.db")
    source = store.put_source(b"synthetic source")
    amount = "9" * 36
    raw_dataset["documents"] = {source: "source.csv"}
    ref = {
        "document": source,
        "filename": "source.csv",
        "sheet": "CSV",
        "row": 2,
        "column": "id",
        "raw": "S1",
        "transform": "external",
    }
    raw_dataset["shipments"][0]["provenance"] = {"id": deepcopy(ref)}
    raw_dataset["charges"][0].update(
        amount=amount, provenance={"amount": {**ref, "column": "amount", "raw": amount}}
    )
    ds = Dataset.model_validate(raw_dataset)
    rid = store.save(ds, audit(ds))
    control = {
        "schema": "freight-audit-external-control/v1",
        "source_hashes": [source],
        "shipments_by_source": {source: 1},
        "charges_by_source": {source: 1},
        "charge_totals_by_source": {source: {"ARS": amount}},
        "shipment_count": 1,
        "charge_count": 1,
        "actual_by_currency": {"ARS": amount},
    }
    for precision in (8, 28, 80):
        with localcontext() as context:
            context.prec = precision
            assert compare_external_control(store.load(rid), control)["passed"]


def test_bounded_reader_rejects_before_materializing(tmp_path):
    from freight_audit.local_paths import read_bounded

    path = tmp_path / "oversized.csv"
    with path.open("wb") as stream:
        stream.truncate(1025)
    with pytest.raises(ValueError, match="supera"):
        read_bounded(path, 1024)
