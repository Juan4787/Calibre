"""Pure deterministic audit. Findings never incorporate mutable human resolutions."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal

from . import ENGINE_VERSION
from .canonical import decimal_text, digest, exact_context, number, rounded
from .models import Agreement, AuditResult, Charge, Dataset, Evidence, Finding, Shipment, Trace
from .rules import EvaluationError, Evaluator, dimensions, shipment_value


def field_value(record: Shipment | Charge, field: str) -> str | bool | None:
    if field.startswith("attributes."):
        value = record.attributes.get(field[11:])
        return value.value if value else None
    if field in {"id", "reference", "carrier", "concept", "currency", "amount", "settlement", "agreement"}:
        return getattr(record, field, None)
    value = record.attributes.get(field)
    return value.value if value else None


def semantic_input(dataset: Dataset) -> dict:
    data = dataset.model_dump(
        mode="json",
        exclude={
            "documents",
            "mappings",
            "label",
            "issues",
            "contract_sources",
            "external_control",
            "parent_run_id",
            "revision_kind",
            "revision_note",
        },
    )
    for key in ("shipments", "charges", "agreements", "evidence"):
        for record in data[key]:
            record.pop("provenance", None)
            if key == "evidence":
                record["shipment_ids"] = sorted(record["shipment_ids"])
                record["charge_ids"] = sorted(record["charge_ids"])
        data[key].sort(key=lambda record: record["id"])
    data["coverage"] = {key: sorted(value) for key, value in data["coverage"].items()}
    data["incomplete_import"] = any(issue.category in {"file", "mapping", "row"} for issue in dataset.issues)
    return data


def key_for(record, agreement, side, trace=None):
    values = []
    for pair in agreement.matching.keys:
        value = field_value(record, getattr(pair, side))
        if value is None or value == "":
            return None
        # Aliases are directional and apply only to charge keys, never global fuzzy guesses.
        resolved = pair.aliases.get(str(value), value) if side == "charge" else value
        if trace is not None:
            trace.append({"field": getattr(pair, side), "original": value, "resolved": resolved})
        values.append(resolved)
    return tuple(values)


EXPLICIT_CONFLICT_REASON = (
    "La vinculación explícita contradice las claves del cargo. Revisar las operaciones indicadas, "
    "corregir la vinculación o el formato y crear una nueva auditoría. "
    "No se confirma ningún importe de este cargo."
)
RELATED_UNCERTAINTY_REASON = (
    "Otra línea tiene una vinculación pendiente, inválida o contradictoria que podría afectar a estas operaciones. "
    "Resolver esa vinculación y crear una nueva auditoría antes de confirmar importes."
)
MATCHING_PROBLEMS = {
    "invalid": (
        "UNDETERMINABLE",
        "La vinculación explícita está vacía o contiene operaciones ausentes, repetidas o de otro transportista. "
        "Revisar los destinos indicados y corregir la vinculación; no se asigna el cargo automáticamente.",
    ),
    "conflict": ("REVIEW", EXPLICIT_CONFLICT_REASON),
    "uncorroborated": (
        "REVIEW",
        "La vinculación explícita no pudo corroborarse con las claves disponibles. "
        "Revisar el original y corregir la referencia o su equivalencia antes de confirmar importes.",
    ),
    "ambiguous": ("REVIEW", "Hay varias operaciones candidatas; se necesita una vinculación explícita."),
    "unmatched": (
        "REVIEW",
        "No se encontró la operación con las claves configuradas; confirmar la referencia o aportar el registro.",
    ),
}


def matching_indexes(dataset: Dataset) -> dict:
    indexes = {}
    for agreement in dataset.agreements:
        index = defaultdict(list)
        for shipment in dataset.shipments:
            if shipment.carrier == agreement.carrier:
                key = key_for(shipment, agreement, "shipment")
                if key is not None:
                    index[key].append(shipment)
        indexes[agreement.id] = index
    return indexes


MAX_AUDIT_WORK = 2_000_000


class AuditLimitError(ValueError):
    """The whole batch is refused before pricing or candidate trace expansion."""


@dataclass(frozen=True)
class MatchingPreparation:
    agreements: dict[str, Agreement]
    shipments: dict[str, Shipment]
    indexes: dict[str, dict[tuple, list[Shipment]]]


def prepare_matching(dataset: Dataset) -> MatchingPreparation:
    """Pure phase: bound index, association, expression and evidence expansion.

    Work units are a conservative structural budget, not a guarantee of RSS or
    elapsed time. No prices or partial findings are emitted when it is exceeded.
    """
    work = 0

    def consume(amount: int) -> None:
        nonlocal work
        work += amount
        if work > MAX_AUDIT_WORK:
            raise AuditLimitError(
                "El lote supera el presupuesto de asociaciones y cálculo. Dividirlo por períodos o "
                "acuerdos conservando completas las operaciones de cada cargo; no se guardó un resultado parcial."
            )

    costs = {}
    degrees = Counter(
        (kind, identifier)
        for e in dataset.evidence
        for kind, identifiers in (("shipment", e.shipment_ids), ("charge", e.charge_ids))
        for identifier in identifiers
    )
    consume(sum(degrees.values()))
    max_degree = max(degrees.values(), default=0)
    for agreement in dataset.agreements:
        consume(len(dataset.shipments) * len(agreement.matching.keys))
        expression_cost = 1
        evidence_cost = 0
        for version in agreement.versions:
            consume(sum(len(table.rows) for table in version.tables.values()))
            for rule in version.rules:
                evidence_cost += sum(len(r.any_of) + 1 for r in rule.evidence)
                pending = [rule.expression, *([rule.when] if rule.when else [])]
                while pending:
                    expression = pending.pop()
                    expression_cost += 1
                    if expression.op == "band" and expression.table in version.tables:
                        expression_cost += len(version.tables[expression.table].bands)
                    pending.extend(expression.args)
        costs[agreement.id] = expression_cost, evidence_cost
        if agreement.detect_missing:
            consume(len(dataset.coverage.get(agreement.id, [])) * expression_cost)
    indexes = matching_indexes(dataset)
    agreements = {a.id: a for a in dataset.agreements}
    for charge in dataset.charges:
        selected = agreements.get(charge.agreement)
        if selected is None or charge.carrier != selected.carrier or charge.currency != selected.currency:
            consume(1)
            continue
        candidates = len(indexes[selected.id].get(key_for(charge, selected, "charge"), ()))
        explicit = len(selected.matching.explicit.get(charge.id, ()))
        expression_cost, evidence_cost = costs[selected.id]
        # Count candidates before inspect_matching sorts/copies their IDs.
        width = 1 + candidates + explicit
        consume(width * (expression_cost + 4) + evidence_cost * width * width * max_degree)
    return MatchingPreparation(agreements, {s.id: s for s in dataset.shipments}, indexes)


def inspect_explicit_link(charge: Charge, agreement: Agreement, shipments: dict, index: dict):
    """One policy for preflight and audit; explicit disambiguation is not a silent override."""
    ids = sorted(agreement.matching.explicit[charge.id])
    matched = [
        shipments[sid]
        for sid in sorted(set(ids))
        if sid in shipments and shipments[sid].carrier == agreement.carrier
    ]
    key_details: list[dict] = []
    key = key_for(charge, agreement, "charge", key_details)
    candidate_ids = sorted(s.id for s in index.get(key, []))
    execution: dict = {
        "charge_id": charge.id,
        "method": "explicit",
        "shipment_ids": ids,
        "policy": "explicit-consistency-v3",
        "keys": key_details,
        "key_candidate_ids": candidate_ids,
    }
    if not ids or len(matched) != len(ids):
        execution["comparison"] = "invalid"
        execution["invalid_targets"] = {
            "empty": not ids,
            "missing": sorted(set(ids) - shipments.keys()),
            "repeated": sorted(sid for sid, count in Counter(ids).items() if count > 1),
            "other_carrier": sorted(
                sid for sid in set(ids) if sid in shipments and shipments[sid].carrier != agreement.carrier
            ),
        }
        execution["affected_shipment_ids"] = sorted({s.id for s in matched} | set(candidate_ids))
        return matched, execution
    if not candidate_ids:
        comparison = "uncorroborated"
    else:
        # `one` permits explicit selection among ambiguous candidates. `group`
        # declares the whole matching group, so dropping a member is a conflict too.
        compatible = (
            set(ids) == set(candidate_ids)
            if agreement.matching.cardinality == "group"
            else set(ids) <= set(candidate_ids)
        )
        comparison = "compatible" if compatible else "conflict"
    execution["comparison"] = comparison
    if comparison in {"conflict", "uncorroborated"}:
        execution["affected_shipment_ids"] = sorted(set(ids) | set(candidate_ids))
    return matched, execution


def inspect_matching(charge: Charge, agreement: Agreement, shipments: dict, index: dict):
    """Classify the association once; candidates describe uncertainty, never an allocation."""
    if charge.id in agreement.matching.explicit:
        return inspect_explicit_link(charge, agreement, shipments, index)
    key_details: list[dict] = []
    key = key_for(charge, agreement, "charge", key_details)
    matched = sorted(index.get(key, []), key=lambda s: s.id)
    execution: dict = {"charge_id": charge.id, "method": "keys", "keys": key_details}
    comparison = None
    if not matched:
        comparison = "unmatched"
    elif len(matched) > 1 and agreement.matching.cardinality != "group":
        comparison = "ambiguous"
    if comparison:
        execution.update(
            comparison=comparison,
            key_candidate_ids=[s.id for s in matched],
            affected_shipment_ids=[s.id for s in matched],
        )
    return matched, execution


def matching_preflight(dataset: Dataset) -> dict:
    """Read-only, bounded matching diagnostics; audit always checks again."""
    prepared = prepare_matching(dataset)
    indexes, shipments, agreements = prepared.indexes, prepared.shipments, prepared.agreements
    conflicts: list[dict] = []
    issues: list[dict] = []
    counts = dict.fromkeys(MATCHING_PROBLEMS, 0)
    skipped = 0
    for charge in sorted(dataset.charges, key=lambda c: c.id):
        agreement = agreements.get(charge.agreement)
        if agreement is None or charge.carrier != agreement.carrier or charge.currency != agreement.currency:
            skipped += 1
            continue
        _, execution = inspect_matching(charge, agreement, shipments, indexes[agreement.id])
        comparison = execution.get("comparison")
        if comparison in counts:
            counts[comparison] += 1
            if len(issues) < 50:
                issues.append(execution)
        if comparison == "conflict":
            if len(conflicts) < 50:
                conflicts.append(execution)
    return {
        "total_conflicts": counts["conflict"],
        "conflicts": conflicts,
        "total_issues": sum(counts.values()),
        "counts": counts,
        "issues": issues,
        "skipped_charges": skipped,
    }


def select_version(agreement: Agreement, shipments: list[Shipment]):
    chosen = set()
    dates = []
    for shipment in shipments:
        value = shipment_value(shipment, agreement.date_field)
        if value.type != "date":
            raise EvaluationError(
                f"La fecha que gobierna la vigencia '{agreement.date_field}' no tiene tipo fecha."
            )
        service_date = str(value.value)
        matches = [
            v
            for v in agreement.versions
            if v.valid_from <= service_date and (v.valid_to is None or service_date <= v.valid_to)
        ]
        if len(matches) != 1:
            raise EvaluationError(
                f"La fecha {service_date} tiene {len(matches)} versiones aplicables; se requiere una sola."
            )
        chosen.add(matches[0].id)
        dates.append({"shipment_id": shipment.id, "date": service_date})
    if len(chosen) != 1:
        raise EvaluationError(
            "El cargo consolidado abarca varias versiones; falta una regla explícita de asignación."
        )
    version = next(v for v in agreement.versions if v.id in chosen)
    return version, Trace(
        op="version",
        output=version.id,
        details={
            "date_field": agreement.date_field,
            "dates": dates,
            "valid_from": version.valid_from,
            "valid_to": version.valid_to,
            "source_note": version.source_note,
        },
    )


def evidence_check(rule, evidence: list[Evidence], shipments, charges):
    found: set[str] = set()
    missing = []
    shipment_ids = {s.id for s in shipments}
    charge_ids = {c.id for c in charges}
    for requirement in rule.evidence:
        candidates = [
            e
            for e in evidence
            if e.kind in requirement.any_of and (not requirement.document_required or e.document_hash)
        ]
        if requirement.scope == "each_shipment":
            targets = [
                (sid, [e for e in candidates if sid in e.shipment_ids]) for sid in sorted(shipment_ids)
            ]
        elif requirement.scope == "each_charge":
            targets = [(cid, [e for e in candidates if cid in e.charge_ids]) for cid in sorted(charge_ids)]
        else:
            targets = [
                (
                    "grupo",
                    [
                        e
                        for e in candidates
                        if set(e.shipment_ids) & shipment_ids or set(e.charge_ids) & charge_ids
                    ],
                )
            ]
        for target, matches in targets:
            if not matches:
                alternatives = " o ".join(requirement.any_of[:3])
                if len(requirement.any_of) > 3:
                    alternatives += f" u otras {len(requirement.any_of) - 3} alternativas (ver requisitos completos en la traza)"
                missing.append(
                    f"{target}: {alternatives}"
                    + (" con documento conservado" if requirement.document_required else "")
                )
            found.update(e.id for e in matches)
    return sorted(found), sorted(missing)


def unresolved(charges, agreement, shipments, status, message, concept=None, currency=None):
    actual = sum((number(c.amount) for c in charges), Decimal(0))
    charge_ids = sorted(c.id for c in charges)
    shipment_ids = sorted(s.id for s in shipments)
    return Finding(
        id=digest([agreement, shipment_ids, charge_ids, concept or charges[0].concept]),
        status=status,
        agreement=agreement,
        concept=concept or charges[0].concept,
        currency=currency or charges[0].currency,
        shipment_ids=shipment_ids,
        charge_ids=charge_ids,
        actual=decimal_text(actual),
        reasons=[message],
    )


def audit(dataset: Dataset) -> AuditResult:
    with exact_context():
        return _audit(dataset)


def _audit(dataset: Dataset) -> AuditResult:
    prepared = prepare_matching(dataset)
    agreements, shipments, indexes = prepared.agreements, prepared.shipments, prepared.indexes
    findings = []
    version_lookup_indexes: dict = {}
    match_execution: dict = {}
    matching_strategies = {
        a.id: {
            "configuration_hash": digest(a.matching),
            "keys": [{"charge": k.charge, "shipment": k.shipment} for k in a.matching.keys],
            "cardinality": a.matching.cardinality,
            "duplicate_fields": a.matching.duplicate_fields,
        }
        for a in dataset.agreements
    }
    groups: dict = defaultdict(list)
    group_shipments = {}
    seen_duplicates: dict = defaultdict(list)
    duplicate_ids: set = set()
    uncertain_allocations: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    uncertain_scopes: set[tuple[str, str]] = set()
    evidence_by_shipment: dict = defaultdict(list)
    evidence_by_charge: dict = defaultdict(list)
    for evidence in dataset.evidence:
        for sid in evidence.shipment_ids:
            evidence_by_shipment[sid].append(evidence)
        for cid in evidence.charge_ids:
            evidence_by_charge[cid].append(evidence)
    for charge in sorted(dataset.charges, key=lambda c: c.id):
        candidate_agreement = agreements.get(charge.agreement)
        if candidate_agreement is None or charge.carrier != candidate_agreement.carrier:
            findings.append(
                unresolved(
                    [charge],
                    charge.agreement,
                    [],
                    "UNDETERMINABLE",
                    "No hay un acuerdo compatible con el transportista del cargo.",
                )
            )
            continue
        agreement = candidate_agreement
        if charge.currency != agreement.currency:
            findings.append(
                unresolved(
                    [charge],
                    agreement.id,
                    [],
                    "UNDETERMINABLE",
                    "La moneda del cargo difiere de la del acuerdo; no hay conversión configurada.",
                )
            )
            continue
        matched, execution = inspect_matching(charge, agreement, shipments, indexes[agreement.id])
        comparison = execution.get("comparison")
        if comparison in MATCHING_PROBLEMS:
            status, reason = MATCHING_PROBLEMS[comparison]
            candidates = execution["affected_shipment_ids"]
            for sid in candidates:
                scope = (agreement.id, sid, charge.concept, charge.currency)
                uncertain_allocations[scope].add(charge.id)
                uncertain_scopes.add((agreement.id, sid))
            finding = unresolved(
                [charge], agreement.id, [shipments[sid] for sid in candidates], status, reason
            )
            findings.append(
                finding.model_copy(
                    update={
                        "trace": [
                            Trace(
                                op="matching",
                                details={
                                    "shipment_ids": candidates,
                                    "charge_ids": [charge.id],
                                    "strategy": matching_strategies[agreement.id],
                                    "execution": [execution],
                                    "allocation": "unresolved_candidates",
                                    "reason": reason,
                                },
                            )
                        ]
                    }
                )
            )
            # Uncertainty protects every plausible scope without assigning this charge to one.
            continue
        match_execution[charge.id] = execution
        if agreement.matching.duplicate_fields:
            signature = tuple(field_value(charge, field) for field in agreement.matching.duplicate_fields)
            if all(value is not None and value != "" for value in signature):
                seen_duplicates[(agreement.id, *signature)].append(charge.id)
        group_key = (
            agreement.id,
            tuple(s.id for s in matched),
            charge.concept,
            charge.currency,
            charge.settlement,
        )
        groups[group_key].append(charge)
        group_shipments[group_key] = matched
    for ids in seen_duplicates.values():
        if len(ids) > 1:
            duplicate_ids.update(ids)
    incomplete = any(issue.category in {"file", "mapping", "row"} for issue in dataset.issues)
    observed_scopes = {(key[0], sid) for key in groups for sid in key[1]}
    billed_scopes = {
        (key[0], sid, key[2], key[3]) for key, charges in groups.items() if charges for sid in key[1]
    }
    # Optional coverage is explicit. Never infer a missing payable from an unrelated shipment.
    for agreement in dataset.agreements:
        if not agreement.detect_missing or incomplete:
            continue
        scopes = defaultdict(list)
        for sid in sorted(set(dataset.coverage.get(agreement.id, []))):
            shipment = shipments[sid]
            if shipment.carrier != agreement.carrier:
                continue
            key = (
                key_for(shipment, agreement, "shipment")
                if agreement.matching.cardinality == "group"
                else (shipment.id,)
            )
            if key is not None:
                scopes[key].append(shipment)
        for matched in scopes.values():
            matched.sort(key=lambda s: s.id)
            try:
                version, _ = select_version(agreement, matched)
                for rule in sorted(version.rules, key=lambda r: r.id):
                    if rule.expected:
                        if any(
                            (agreement.id, s.id, rule.concept, agreement.currency) in uncertain_allocations
                            for s in matched
                        ):
                            # A disputed charge is present: absence is not established.
                            continue
                        # An explicit consolidation still covers each member. If any member
                        # is billed, absence of the whole obligation has not been established.
                        already_billed = any(
                            (agreement.id, s.id, rule.concept, agreement.currency) in billed_scopes
                            for s in matched
                        )
                        if not already_billed:
                            group_key = (
                                agreement.id,
                                tuple(s.id for s in matched),
                                rule.concept,
                                agreement.currency,
                                "",
                            )
                            groups.setdefault(group_key, [])
                            group_shipments[group_key] = matched
            except EvaluationError:
                if any((agreement.id, s.id) in uncertain_scopes for s in matched):
                    continue
                if any((agreement.id, s.id) in observed_scopes for s in matched):
                    continue
                group_key = (
                    agreement.id,
                    tuple(s.id for s in matched),
                    "(cobertura sin versión)",
                    agreement.currency,
                    "",
                )
                groups.setdefault(group_key, [])
                group_shipments[group_key] = matched
    # Overlapping allocations of a single concept cannot independently assert full expected totals.
    allocations = defaultdict(set)
    for group_key in groups:
        aid, sids, concept, currency, settlement = group_key
        for sid in sids:
            # A different invoice preserves document identity, not a new service.
            # Reuse of the same obligation needs an explicit allocation before certainty.
            allocations[(aid, sid, concept, currency)].add(group_key)
    overlapping = {
        group_key
        for allocation_key, group_set in allocations.items()
        if len(group_set) > 1
        for group_key in group_set
    }
    for group_key in sorted(groups):
        agreement_id, _, concept, currency, settlement = group_key
        agreement = agreements[agreement_id]
        charges = groups[group_key]
        matched = group_shipments[group_key]
        base = unresolved(
            charges, agreement.id, matched, "UNDETERMINABLE", "Sin cálculo suficiente.", concept, currency
        )
        traces = [
            Trace(
                op="matching",
                details={
                    "shipment_ids": base.shipment_ids,
                    "charge_ids": base.charge_ids,
                    "strategy": matching_strategies[agreement.id],
                    "execution": [match_execution[c.id] for c in charges],
                },
            )
        ]
        related_uncertainty = sorted(
            {
                cid
                for shipment in matched
                for cid in uncertain_allocations.get((agreement.id, shipment.id, concept, currency), ())
            }
        )
        matching_reasons = [RELATED_UNCERTAINTY_REASON] if related_uncertainty else []
        if related_uncertainty:
            traces.append(
                Trace(
                    op="matching_uncertainty",
                    details={
                        "unresolved_charge_ids": related_uncertainty,
                        "reason": RELATED_UNCERTAINTY_REASON,
                    },
                )
            )
        version_id = None
        rule_id = None
        try:
            version, trace = select_version(agreement, matched)
            version_id = version.id
            traces.append(trace)
            evaluator = Evaluator(
                matched, version, version_lookup_indexes.setdefault((agreement.id, version.id), {})
            )
            applicable = []
            for rule in sorted(version.rules, key=lambda r: r.id):
                if rule.concept != concept:
                    continue
                if rule.when:
                    condition, trace = evaluator.evaluate(rule.when)
                    traces.append(
                        Trace(
                            op="condition",
                            output=condition.text(),
                            details={"rule": rule.id},
                            children=[trace],
                        )
                    )
                    if not condition.boolean():
                        continue
                applicable.append(rule)
            if len(applicable) == 0 and not charges:
                # An expected rule with a false condition creates no expectation.
                continue
            if len(applicable) != 1:
                raise EvaluationError(
                    f"El concepto tiene {len(applicable)} reglas aplicables; no se puede determinar un único importe."
                )
            rule = applicable[0]
            rule_id = rule.id
            result, trace = evaluator.evaluate(rule.expression)
            traces.append(trace)
            if result.units != dimensions(currency):
                raise EvaluationError("El resultado de la regla no tiene la unidad monetaria del acuerdo.")
            expected = rounded(result.decimal(), agreement.scale, agreement.rounding)
            traces.append(
                Trace(
                    op="currency_round",
                    output=decimal_text(expected),
                    details={
                        "scale": agreement.scale,
                        "rounding": agreement.rounding,
                        "currency": currency,
                        "input": result.text(),
                    },
                )
            )
            actual = Decimal(base.actual)
            difference = actual - expected
            tolerance = max(
                number(agreement.tolerance_absolute), abs(expected) * number(agreement.tolerance_relative)
            )
            traces.append(
                Trace(
                    op="comparison",
                    output=decimal_text(difference),
                    details={
                        "actual": base.actual,
                        "expected": decimal_text(expected),
                        "tolerance": decimal_text(tolerance),
                        "formula": "actual - expected",
                    },
                )
            )
            evidence_items = {}
            for shipment in matched:
                evidence_items.update({e.id: e for e in evidence_by_shipment[shipment.id]})
            for charge in charges:
                evidence_items.update({e.id: e for e in evidence_by_charge[charge.id]})
            evidence_ids, missing = evidence_check(rule, list(evidence_items.values()), matched, charges)
            reasons = list(matching_reasons)
            if missing:
                reasons.append(
                    "Falta evidencia requerida: "
                    + "; ".join(missing[:3])
                    + (
                        f"; y {len(missing) - 3} comprobaciones adicionales (ver detalle completo de evidencia)"
                        if len(missing) > 3
                        else ""
                    )
                    + ". Solicitar el respaldo antes de resolver."
                )
            if any(c.id in duplicate_ids for c in charges):
                reasons.append(
                    "Hay líneas que coinciden con la clave de posible duplicación configurada; confirmar si corresponden a servicios distintos."
                )
            if group_key in overlapping and not related_uncertainty:
                reasons.append(
                    "Hay asignaciones superpuestas del mismo concepto; definir qué operaciones cubre cada cargo."
                )
            if incomplete:
                reasons.append(
                    "La importación tiene filas rechazadas o errores; corregirlos para confirmar el resultado del lote."
                )
            if not charges:
                reasons.append(
                    "El acuerdo espera este concepto y no se encontraron cargos en el alcance declarado; confirmar que la liquidación esté completa."
                )
            status = "REVIEW" if reasons else "PASS" if abs(difference) <= tolerance else "FAIL"
            if not reasons:
                reasons = [
                    "El importe coincide dentro de la tolerancia configurada."
                    if status == "PASS"
                    else "El importe difiere del cálculo respaldado por el acuerdo y los datos disponibles."
                ]
            traces.append(
                Trace(
                    op="evidence",
                    details={
                        "found": evidence_ids,
                        "missing": missing,
                        "requirements": [r.model_dump(mode="json") for r in rule.evidence],
                    },
                )
            )
            findings.append(
                base.model_copy(
                    update={
                        "status": status,
                        "version": version.id,
                        "rule": rule.id,
                        "expected": decimal_text(expected),
                        "difference": decimal_text(difference),
                        "confirmed_difference": decimal_text(difference) if status == "FAIL" else "0",
                        "reasons": reasons,
                        "trace": traces,
                        "evidence_ids": evidence_ids,
                        "missing_evidence": missing,
                    }
                )
            )
        except (EvaluationError, ArithmeticError) as error:
            exc = (
                error
                if isinstance(error, EvaluationError)
                else EvaluationError(
                    "El cálculo de comparación excede la precisión exacta admitida; revisar la magnitud y la regla de tolerancia."
                )
            )
            findings.append(
                base.model_copy(
                    update={
                        "version": version_id,
                        "rule": rule_id,
                        "reasons": [*matching_reasons, str(exc)],
                        "trace": [*traces, exc.trace],
                    }
                )
            )
    findings.sort(key=lambda finding: finding.id)
    return AuditResult(
        engine_version=ENGINE_VERSION,
        semantic_hash=digest(semantic_input(dataset)),
        findings=findings,
        summary=summarize(findings, incomplete),
        issues=dataset.issues,
    )


def summarize(findings: list[Finding], incomplete: bool) -> dict:
    currencies: dict = {}
    counts = {status: 0 for status in ("PASS", "FAIL", "REVIEW", "UNDETERMINABLE")}
    for finding in findings:
        counts[finding.status] += 1
        bucket = currencies.setdefault(
            finding.currency,
            {
                key: Decimal(0)
                for key in (
                    "actual",
                    "determinable",
                    "pass",
                    "review",
                    "undeterminable",
                    "confirmed_net_difference",
                    "confirmed_overcharge",
                    "confirmed_undercharge",
                )
            },
        )
        actual = Decimal(finding.actual)
        bucket["actual"] += actual
        if finding.status in {"PASS", "FAIL"}:
            bucket["determinable"] += actual
        if finding.status in {"PASS", "REVIEW", "UNDETERMINABLE"}:
            bucket[finding.status.lower()] += actual
        diff = Decimal(finding.confirmed_difference)
        bucket["confirmed_net_difference"] += diff
        bucket["confirmed_overcharge"] += max(diff, Decimal(0))
        bucket["confirmed_undercharge"] += min(diff, Decimal(0))
    total = len(findings)
    determinable = counts["PASS"] + counts["FAIL"]
    charge_status: Counter[str] = Counter()
    for finding in findings:
        charge_status[finding.status] += len(finding.charge_ids)
    return {
        "counts": counts,
        "total_findings": total,
        "determinable_findings": determinable,
        "charge_counts": dict(charge_status),
        "import_complete": not incomplete,
        "currencies": {
            currency: {key: decimal_text(value) for key, value in bucket.items()}
            for currency, bucket in sorted(currencies.items())
        },
        "economic_definition": "Diferencia = facturado menos esperado. Sólo FAIL integra la diferencia confirmada. No representa ahorro, recupero ni decisión de pago. Monedas separadas.",
    }
