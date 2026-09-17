from copy import deepcopy
from decimal import Decimal, getcontext, localcontext

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from freight_audit.canonical import canonical, digest
from freight_audit.engine import audit
from freight_audit.fixtures import attr, const, op, rule, version
from freight_audit.models import Dataset, Expr, Value
from freight_audit.rules import divide_quantized


def compute(raw):
    return audit(Dataset.model_validate(raw))


def first(raw):
    return compute(raw).findings[0]


def test_exact_match_and_trace(raw_dataset):
    finding = first(raw_dataset)
    assert finding.status == "PASS"
    assert finding.expected == "100"
    assert [step.op for step in finding.trace] == [
        "matching",
        "version",
        "const",
        "currency_round",
        "comparison",
        "evidence",
    ]
    assert finding.trace[-2].output == "0"


@pytest.mark.parametrize(
    ("actual", "status", "diff"),
    [
        ("100.01", "PASS", "0"),
        ("100.02", "FAIL", "0.02"),
        ("90", "FAIL", "-10"),
        ("110", "FAIL", "10"),
        ("-10", "FAIL", "-110"),
    ],
)
def test_tolerance_and_signed_differences(raw_dataset, actual, status, diff):
    raw_dataset["charges"][0]["amount"] = actual
    f = first(raw_dataset)
    assert (f.status, f.confirmed_difference) == (status, diff)


def test_missing_evidence_does_not_confirm_even_numeric_difference(raw_dataset):
    raw_dataset["charges"][0]["amount"] = "200"
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["evidence"] = [{"any_of": ["approval"]}]
    result = compute(raw_dataset)
    f = result.findings[0]
    assert (f.status, f.expected, f.difference, f.confirmed_difference) == ("REVIEW", "100", "100", "0")
    assert result.summary["currencies"]["ARS"]["confirmed_overcharge"] == "0"
    assert f.missing_evidence


def test_evidence_any_of_and_per_operation(raw_dataset):
    rule_data = raw_dataset["agreements"][0]["versions"][0]["rules"][0]
    rule_data["evidence"] = [{"any_of": ["approval", "signed_event"], "scope": "each_shipment"}]
    raw_dataset["evidence"] = [
        {"id": "E1", "kind": "signed_event", "shipment_ids": ["S1"], "note": "Declaración explícita"}
    ]
    assert first(raw_dataset).status == "PASS"
    rule_data["evidence"][0]["document_required"] = True
    assert first(raw_dataset).status == "REVIEW"


def test_unrelated_evidence_cannot_support_charge(raw_dataset):
    raw_dataset["shipments"].append(
        {**deepcopy(raw_dataset["shipments"][0]), "id": "S2", "reference": "00002"}
    )
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["evidence"] = [{"any_of": ["approval"]}]
    raw_dataset["evidence"] = [
        {"id": "E1", "kind": "approval", "shipment_ids": ["S2"], "note": "Para otra operación"}
    ]
    assert first(raw_dataset).status == "REVIEW"


@pytest.mark.parametrize(
    "date,status,version_id",
    [("2025-12-31", "UNDETERMINABLE", None), ("2026-06-30", "PASS", "V1"), ("2026-07-01", "PASS", "V2")],
)
def test_version_boundaries(raw_dataset, date, status, version_id):
    a = raw_dataset["agreements"][0]
    a["versions"][0]["valid_to"] = "2026-06-30"
    a["versions"].append(version("V2", [rule("R2", "base", const("100", "ARS"))], start="2026-07-01"))
    raw_dataset["shipments"][0]["attributes"]["service_date"]["value"] = date
    f = first(raw_dataset)
    assert (f.status, f.version) == (status, version_id)


def test_overlapping_versions_never_pick_first(raw_dataset):
    raw_dataset["agreements"][0]["versions"].append(version("V2", [rule("R2", "base", const("100", "ARS"))]))
    assert first(raw_dataset).status == "UNDETERMINABLE"
    raw_dataset["agreements"][0]["versions"].reverse()
    assert first(raw_dataset).status == "UNDETERMINABLE"


def test_alternate_date_field(raw_dataset):
    a = raw_dataset["agreements"][0]
    a["date_field"] = "pickup"
    assert first(raw_dataset).status == "UNDETERMINABLE"
    raw_dataset["shipments"][0]["attributes"]["pickup"] = {"type": "date", "value": "2026-09-01"}
    assert first(raw_dataset).status == "PASS"


def test_unknown_concept_is_undeterminable(raw_dataset):
    raw_dataset["charges"][0]["concept"] = "never-configured"
    f = first(raw_dataset)
    assert f.status == "UNDETERMINABLE" and f.expected is None and f.confirmed_difference == "0"


def test_matching_ambiguity_is_review(raw_dataset):
    raw_dataset["shipments"].append({**deepcopy(raw_dataset["shipments"][0]), "id": "S2"})
    f = first(raw_dataset)
    assert f.status == "REVIEW" and f.shipment_ids == ["S1", "S2"]


def test_explicit_mapping_resolves_ambiguity(raw_dataset):
    raw_dataset["shipments"].append({**deepcopy(raw_dataset["shipments"][0]), "id": "S2"})
    raw_dataset["agreements"][0]["matching"]["explicit"] = {"C1": ["S2"]}
    f = first(raw_dataset)
    assert f.status == "PASS" and f.shipment_ids == ["S2"]


@pytest.mark.parametrize("ids", [["missing"], ["S1", "S1"], []])
def test_invalid_explicit_link_never_falls_back(raw_dataset, ids):
    raw_dataset["agreements"][0]["matching"]["explicit"] = {"C1": ids}
    assert first(raw_dataset).status == "UNDETERMINABLE"


def test_composite_keys_and_directional_alias(raw_dataset):
    raw_dataset["charges"][0]["reference"] = "external-1"
    a = raw_dataset["agreements"][0]
    a["matching"]["keys"] = [
        {"charge": "reference", "shipment": "reference", "aliases": {"external-1": "00001"}},
        {"charge": "carrier", "shipment": "carrier"},
    ]
    assert first(raw_dataset).status == "PASS"


def test_multiple_lines_aggregate_without_inventing_duplicates(raw_dataset):
    raw_dataset["charges"][0]["amount"] = "30"
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2", "amount": "70"})
    result = compute(raw_dataset)
    assert len(result.findings) == 1
    assert result.findings[0].status == "PASS"
    assert result.findings[0].charge_ids == ["C1", "C2"]
    assert result.summary["currencies"]["ARS"]["actual"] == "100"


def test_configured_duplicate_is_candidate_only(raw_dataset):
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2"})
    result = compute(raw_dataset)
    assert result.findings[0].status == "REVIEW"
    assert result.summary["currencies"]["ARS"]["confirmed_overcharge"] == "0"


def test_same_remittance_different_concepts_is_not_duplicate(raw_dataset):
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2", "concept": "extra"})
    raw_dataset["agreements"][0]["versions"][0]["rules"].append(rule("R2", "extra", const("100", "ARS")))
    assert [f.status for f in compute(raw_dataset).findings] == ["PASS", "PASS"]


def test_group_sum_and_one_expected_charge(raw_dataset):
    raw_dataset["shipments"].append({**deepcopy(raw_dataset["shipments"][0]), "id": "S2"})
    a = raw_dataset["agreements"][0]
    a["matching"]["cardinality"] = "group"
    a["versions"][0]["rules"][0]["expression"] = op(
        "mul", {"op": "sum", "field": "weight", "unit": "kg"}, const("5", "ARS/kg")
    )
    f = first(raw_dataset)
    assert f.status == "PASS" and f.expected == "100"
    assert f.shipment_ids == ["S1", "S2"]


def test_group_mixed_version_is_undeterminable(raw_dataset):
    raw_dataset["shipments"].append({**deepcopy(raw_dataset["shipments"][0]), "id": "S2"})
    raw_dataset["shipments"][1]["attributes"]["service_date"]["value"] = "2026-09-01"
    a = raw_dataset["agreements"][0]
    a["matching"]["cardinality"] = "group"
    a["versions"][0]["valid_to"] = "2026-06-30"
    a["versions"].append(version("V2", [rule("R2", "base", const("100", "ARS"))], start="2026-07-01"))
    assert first(raw_dataset).status == "UNDETERMINABLE"


def test_missing_attribute_and_unit_mismatch(raw_dataset):
    a = raw_dataset["agreements"][0]
    a["versions"][0]["rules"][0]["expression"] = op("mul", attr("weight", "kg"), const("10", "ARS/kg"))
    assert first(raw_dataset).status == "PASS"
    raw_dataset["shipments"][0]["attributes"]["weight"]["unit"] = "lb"
    assert first(raw_dataset).status == "UNDETERMINABLE"
    del raw_dataset["shipments"][0]["attributes"]["weight"]
    assert first(raw_dataset).status == "UNDETERMINABLE"


def test_rules_need_currency_units(raw_dataset):
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["expression"] = const("100")
    assert first(raw_dataset).status == "UNDETERMINABLE"


def test_currencies_never_summed_or_converted(raw_dataset):
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2", "currency": "USD", "amount": "3"})
    result = compute(raw_dataset)
    assert result.summary["currencies"]["ARS"]["actual"] == "100"
    assert result.summary["currencies"]["USD"]["actual"] == "3"
    assert next(f for f in result.findings if f.currency == "USD").status == "UNDETERMINABLE"


def test_missing_expected_charge_requires_explicit_scope_and_is_review(raw_dataset):
    raw_dataset["charges"] = []
    a = raw_dataset["agreements"][0]
    a["detect_missing"] = True
    a["versions"][0]["rules"][0]["expected"] = True
    assert not compute(raw_dataset).findings
    raw_dataset["coverage"] = {"A": ["S1"]}
    f = first(raw_dataset)
    assert (f.status, f.actual, f.expected, f.confirmed_difference) == ("REVIEW", "0", "100", "0")


def test_condition_false_does_not_invent_missing_charge(raw_dataset):
    raw_dataset["charges"] = []
    raw_dataset["coverage"] = {"A": ["S1"]}
    a = raw_dataset["agreements"][0]
    a["detect_missing"] = True
    a["versions"][0]["rules"][0].update(expected=True, when=const(False, kind="boolean"))
    assert not compute(raw_dataset).findings


def test_condition_missing_is_not_false(raw_dataset):
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["when"] = op("gt", attr("unknown"), const("0"))
    assert first(raw_dataset).status == "UNDETERMINABLE"


def test_condition_branch_is_lazy(raw_dataset):
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["expression"] = op(
        "if", const(True, kind="boolean"), const("100", "ARS"), attr("absent")
    )
    assert first(raw_dataset).status == "PASS"


def test_overlapping_rules_are_undeterminable(raw_dataset):
    raw_dataset["agreements"][0]["versions"][0]["rules"].append(rule("R2", "base", const("100", "ARS")))
    assert first(raw_dataset).status == "UNDETERMINABLE"


def test_import_rejects_block_economic_confirmation(raw_dataset):
    raw_dataset["charges"][0]["amount"] = "200"
    raw_dataset["issues"] = [{"category": "row", "message": "Fila rechazada"}]
    result = compute(raw_dataset)
    assert result.findings[0].status == "REVIEW"
    assert not result.summary["import_complete"]
    assert result.summary["currencies"]["ARS"]["confirmed_net_difference"] == "0"


def test_overlap_allocations_are_review(raw_dataset):
    raw_dataset["shipments"].append(
        {**deepcopy(raw_dataset["shipments"][0]), "id": "S2", "reference": "00002"}
    )
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2"})
    raw_dataset["agreements"][0]["matching"].update(
        explicit={"C1": ["S1", "S2"], "C2": ["S1"]}, duplicate_fields=[]
    )
    assert {f.status for f in compute(raw_dataset).findings} == {"REVIEW"}


def test_normalized_roundtrip_and_reordering(raw_dataset):
    raw_dataset["charges"].append({**raw_dataset["charges"][0], "id": "C2", "concept": "extra"})
    dataset = Dataset.model_validate(raw_dataset)
    result = audit(dataset)
    assert canonical(result) == canonical(audit(Dataset.model_validate_json(dataset.model_dump_json())))
    raw_dataset["charges"].reverse()
    assert canonical(result) == canonical(compute(raw_dataset))


def test_global_decimal_context_does_not_affect_results(raw_dataset):
    expected = canonical(compute(raw_dataset))
    with localcontext() as context:
        context.prec = 2
        context.rounding = "ROUND_DOWN"
        assert canonical(compute(raw_dataset)) == expected
    assert getcontext().prec != 2


def test_float_prohibited(raw_dataset):
    raw_dataset["charges"][0]["amount"] = 0.1
    with pytest.raises(ValidationError):
        Dataset.model_validate(raw_dataset)


@pytest.mark.parametrize(
    "value", ["NaN", "Infinity", "-Infinity", "1e10", "1,2", "01", "1.", "0.0000000000001"]
)
def test_invalid_money(value):
    with pytest.raises(ValidationError):
        Value(type="decimal", value=value)


@pytest.mark.parametrize(
    "expression",
    [
        {"op": "eval", "value": "x"},
        {"op": "div", "args": [const("1"), const("3")]},
        {"op": "const", "value": {"type": "decimal", "value": "1"}, "table": "ignored"},
        {"op": "add", "args": [const("1")]},
    ],
)
def test_malformed_ast(expression):
    with pytest.raises(ValidationError):
        Expr.model_validate(expression)


@given(a=st.integers(-100000000, 100000000), b=st.integers(-100000000, 100000000))
@settings(max_examples=100)
def test_property_decimal_addition(a, b):
    from freight_audit.canonical import decimal_text, exact_context
    from freight_audit.models import Shipment, Version
    from freight_audit.rules import Evaluator

    expr = Expr.model_validate(
        op("add", const(str(Decimal(a) / 100), "ARS"), const(str(Decimal(b) / 100), "ARS"))
    )
    evaluator = Evaluator(
        [Shipment(id="S", reference="R", carrier="C")],
        Version.model_validate(version("V", [rule("R", "base", const("0", "ARS"))])),
    )
    with exact_context():
        result, trace = evaluator.evaluate(expr)
    assert result.value == Decimal(a + b) / 100
    assert trace.output == decimal_text(result.value)


@given(
    n=st.integers(-(10**20), 10**20),
    d=st.integers(1, 10**12),
    scale=st.integers(0, 8),
    mode=st.sampled_from(["ROUND_HALF_UP", "ROUND_HALF_EVEN", "ROUND_DOWN", "ROUND_UP"]),
)
@settings(max_examples=150)
def test_property_division_matches_high_precision(n, d, scale, mode):
    with localcontext() as context:
        context.prec = 100
        expected = (Decimal(n) / Decimal(d)).quantize(Decimal(1).scaleb(-scale), rounding=mode)
        assert divide_quantized(Decimal(n), Decimal(d), scale, mode) == expected


def test_point_one_plus_point_two(raw_dataset):
    raw_dataset["agreements"][0]["versions"][0]["rules"][0]["expression"] = op(
        "add", const("0.1", "ARS"), const("0.2", "ARS")
    )
    raw_dataset["charges"][0]["amount"] = "0.3"
    assert first(raw_dataset).status == "PASS"
    assert first(raw_dataset).expected == "0.3"


def test_semantic_hash_ignores_incidental_label(raw_dataset):
    original = compute(raw_dataset)
    raw_dataset["label"] = "Otro nombre"
    assert digest(original) == digest(compute(raw_dataset))


@given(order=st.permutations([0, 1, 2, 3]))
@settings(max_examples=24)
def test_property_arbitrary_row_permutation(order):
    from freight_audit.fixtures import agreement

    template = {
        "label": "Permutation property",
        "shipments": [
            {
                "id": f"S{i}",
                "reference": f"{i:05d}",
                "carrier": "C",
                "attributes": {"service_date": {"type": "date", "value": "2026-01-01"}},
            }
            for i in range(4)
        ],
        "charges": [
            {
                "id": f"C{i}",
                "settlement": "L",
                "reference": f"{i:05d}",
                "carrier": "C",
                "agreement": "A",
                "concept": "base",
                "amount": str(100 + i),
                "currency": "ARS",
            }
            for i in range(4)
        ],
        "agreements": [agreement("A", "C", [version("V1", [rule("R1", "base", const("100", "ARS"))])])],
    }
    baseline = canonical(compute(template))
    template["shipments"] = [template["shipments"][i] for i in order]
    template["charges"] = [template["charges"][i] for i in reversed(order)]
    assert canonical(compute(template)) == baseline
