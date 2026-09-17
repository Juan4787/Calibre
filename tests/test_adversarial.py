from copy import deepcopy

import pytest
from pydantic import ValidationError
from test_importing import csv_data, mapping

from freight_audit.canonical import load_json
from freight_audit.engine import audit
from freight_audit.fixtures import attr, const, op
from freight_audit.importing import import_data
from freight_audit.models import Dataset, Value


def result(raw):
    return audit(Dataset.model_validate(raw))


def test_ambiguous_allocation_also_blocks_related_partial_group(raw_dataset):
    raw_dataset["shipments"].append({**deepcopy(raw_dataset["shipments"][0]), "id": "S2"})
    raw_dataset["charges"][0]["amount"] = "40"
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2", "amount": "60"})
    raw_dataset["agreements"][0]["matching"].update(explicit={"C1": ["S1"]}, duplicate_fields=[])
    # The unresolved 60 could be the remainder of S1; 40 vs 100 is not a confirmed shortfall.
    assert {f.status for f in result(raw_dataset).findings} == {"REVIEW"}


def test_aggregate_amount_can_exceed_individual_input_digit_bound(raw_dataset):
    amount = "9" * 36
    raw_dataset["charges"][0]["amount"] = amount
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2", "amount": "1"})
    raw_dataset["agreements"][0]["matching"]["duplicate_fields"] = []
    computed = result(raw_dataset)
    assert computed.summary["currencies"]["ARS"]["actual"] == "1" + "0" * 36


def test_inexact_comparison_becomes_undeterminable(raw_dataset):
    a = raw_dataset["agreements"][0]
    a["tolerance_relative"] = "0." + "123456789012"
    a["versions"][0]["rules"][0]["expression"] = op("mul", const("9" * 36, "ARS"), const("9" * 36))
    finding = result(raw_dataset).findings[0]
    assert finding.status == "UNDETERMINABLE"
    assert finding.confirmed_difference == "0"


def test_no_boolean_coercion():
    with pytest.raises(ValidationError):
        Value(type="boolean", value=1)


def test_csv_multiline_provenance_uses_actual_line():
    data = csv_data('S1;"first\nreference";10;01/01/2026\nS2;0002;20;01/01/2026\n')
    imported = import_data(data, "multi.csv", mapping())
    assert imported["records"][1]["provenance"]["reference"]["row"] == 4


def test_missing_coverage_must_not_duplicate_existing_undetermined_charge(raw_dataset):
    raw_dataset["shipments"][0]["attributes"]["service_date"]["value"] = "2025-01-01"
    raw_dataset["coverage"] = {"A": ["S1"]}
    raw_dataset["agreements"][0]["detect_missing"] = True
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["expected"] = True
    assert len(result(raw_dataset).findings) == 1


def test_coverage_cannot_silently_drop_wrong_carrier(raw_dataset):
    raw_dataset["shipments"][0]["carrier"] = "OTHER"
    raw_dataset["coverage"] = {"A": ["S1"]}
    with pytest.raises(ValidationError):
        Dataset.model_validate(raw_dataset)


def test_oversized_unmapped_cells_not_silently_shifted():
    imported = import_data(csv_data("S1;0001;10;01/01/2026;unexpected\n"), "extra.csv", mapping())
    assert imported["rejected"] == [2]


def test_duplicate_json_keys_are_rejected():
    with pytest.raises(ValueError, match="repetida"):
        load_json('{"amount":"1","amount":"100"}')


def test_band_overlap_and_gap_never_select_arbitrarily(raw_dataset):
    version = raw_dataset["agreements"][0]["versions"][0]
    version["rules"][0]["expression"] = op("band", attr("weight", "kg"), table="ranges")
    version["tables"] = {
        "ranges": {
            "kind": "band",
            "unit": "kg",
            "bands": [
                {"lower": "0", "upper": "20", "value": {"type": "decimal", "value": "100", "unit": "ARS"}},
                {"lower": "5", "upper": "30", "value": {"type": "decimal", "value": "200", "unit": "ARS"}},
            ],
        }
    }
    assert result(raw_dataset).findings[0].status == "UNDETERMINABLE"
    raw_dataset["shipments"][0]["attributes"]["weight"]["value"] = "30"
    assert result(raw_dataset).findings[0].status == "UNDETERMINABLE"
    raw_dataset["shipments"][0]["attributes"]["weight"]["value"] = "0"
    assert result(raw_dataset).findings[0].status == "PASS"


def test_duplicate_lookup_rows_even_same_price_are_ambiguous(raw_dataset):
    version = raw_dataset["agreements"][0]["versions"][0]
    version["rules"][0]["expression"] = op("lookup", attr("reference"), table="prices")
    row = {"keys": ["00001"], "value": {"type": "decimal", "value": "100", "unit": "ARS"}}
    version["tables"] = {"prices": {"kind": "lookup", "rows": [row, row]}}
    assert result(raw_dataset).findings[0].status == "UNDETERMINABLE"


def test_division_by_zero_is_explained(raw_dataset):
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["expression"] = op(
        "div", const("100", "ARS"), const("0"), scale=2, rounding="ROUND_HALF_UP"
    )
    finding = result(raw_dataset).findings[0]
    assert finding.status == "UNDETERMINABLE"
    assert "cero" in finding.reasons[0]
    assert finding.trace[-1].children


def test_bounded_expression_depth_rejects_nested_attack():
    expression = const("1")
    for _ in range(35):
        expression = op("add", expression, const("1"))
    from freight_audit.models import Expr

    with pytest.raises(ValidationError):
        Expr.model_validate(expression)


def test_empty_keys_never_join_to_empty_keys(raw_dataset):
    raw_dataset["charges"][0]["reference"] = ""
    # shipment reference cannot be empty; use optional attributes on both sides.
    raw_dataset["agreements"][0]["matching"]["keys"] = [
        {"charge": "attributes.blank", "shipment": "attributes.blank"}
    ]
    assert result(raw_dataset).findings[0].status == "REVIEW"


def test_many_missing_evidence_preserves_serialization_roundtrip(raw_dataset):
    from freight_audit.models import AuditResult

    template = raw_dataset["shipments"][0]
    raw_dataset["shipments"] = [{**deepcopy(template), "id": "S" * 150 + str(i)} for i in range(100)]
    raw_dataset["agreements"][0]["matching"]["cardinality"] = "group"
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["evidence"] = [
        {"any_of": ["approval"], "scope": "each_shipment"}
    ]
    computed = result(raw_dataset)
    restored = AuditResult.model_validate_json(computed.model_dump_json())
    assert len(restored.findings[0].missing_evidence) == 100
    assert restored.findings[0].status == "REVIEW"


def test_many_evidence_alternatives_remain_replayable(raw_dataset):
    from freight_audit.models import AuditResult

    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["evidence"] = [
        {"any_of": ["type-" + "x" * 190 + str(i) for i in range(100)]}
    ]
    computed = result(raw_dataset)
    restored = AuditResult.model_validate_json(computed.model_dump_json())
    assert restored.findings[0].status == "REVIEW"
    assert len(restored.findings[0].trace[-1].details["requirements"][0]["any_of"]) == 100


def test_long_invalid_rule_field_preserves_result_roundtrip(raw_dataset):
    from freight_audit.models import AuditResult

    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["expression"] = attr("x" * 10000)
    computed = result(raw_dataset)
    restored = AuditResult.model_validate_json(computed.model_dump_json())
    assert restored.findings[0].status == "UNDETERMINABLE"
    assert len(restored.findings[0].reasons[0]) < 2000


def test_matching_trace_references_configuration_without_repeating_unused_aliases(raw_dataset):
    from freight_audit.canonical import canonical

    aliases = {f"external-{i}": f"other-{i}" for i in range(1000)}
    aliases["external-actual"] = "00001"
    raw_dataset["charges"][0]["reference"] = "external-actual"
    raw_dataset["agreements"][0]["matching"]["keys"][0]["aliases"] = aliases
    finding = result(raw_dataset).findings[0]
    assert finding.status == "PASS"
    trace = finding.trace[0]
    assert len(canonical(trace)) < 2000
    assert "external-actual" in canonical(trace)
    assert "external-999" not in canonical(trace)
