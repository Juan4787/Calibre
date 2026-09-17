"""Pure deterministic audit. Findings never incorporate mutable human resolutions."""

from collections import Counter, defaultdict
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
    data = dataset.model_dump(mode="json", exclude={"documents", "mappings", "label", "issues"})
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
    agreements = {a.id: a for a in dataset.agreements}
    shipments = {s.id: s for s in dataset.shipments}
    indexes: dict = {}
    for agreement in dataset.agreements:
        index = defaultdict(list)
        for shipment in dataset.shipments:
            if shipment.carrier == agreement.carrier:
                key = key_for(shipment, agreement, "shipment")
                if key is not None:
                    index[key].append(shipment)
        indexes[agreement.id] = index
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
    uncertain_allocations: set[tuple[str, str, str, str]] = set()
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
        execution: dict = {"charge_id": charge.id}
        if charge.id in agreement.matching.explicit:
            execution["method"] = "explicit"
            ids = agreement.matching.explicit[charge.id]
            matched = [shipments[sid] for sid in sorted(set(ids)) if sid in shipments]
            execution["shipment_ids"] = ids
            if not ids or len(matched) != len(ids) or any(s.carrier != agreement.carrier for s in matched):
                findings.append(
                    unresolved(
                        [charge],
                        agreement.id,
                        [],
                        "UNDETERMINABLE",
                        "La vinculación explícita contiene operaciones ausentes, repetidas o de otro transportista.",
                    )
                )
                continue
        else:
            execution["method"] = "keys"
            key_details: list[dict] = []
            key = key_for(charge, agreement, "charge", key_details)
            execution["keys"] = key_details
            matched = sorted(indexes[agreement.id].get(key, []), key=lambda s: s.id)
            if not matched:
                findings.append(
                    unresolved(
                        [charge],
                        agreement.id,
                        [],
                        "REVIEW",
                        "No se encontró la operación con las claves configuradas; confirmar la referencia o aportar el registro.",
                    )
                )
                continue
            if len(matched) > 1 and agreement.matching.cardinality != "group":
                uncertain_allocations.update(
                    (agreement.id, item.id, charge.concept, charge.currency) for item in matched
                )
                findings.append(
                    unresolved(
                        [charge],
                        agreement.id,
                        matched,
                        "REVIEW",
                        "Hay varias operaciones candidatas; se necesita una vinculación explícita.",
                    )
                )
                continue
        match_execution[charge.id] = execution
        if agreement.matching.duplicate_fields:
            signature = tuple(field_value(charge, field) for field in agreement.matching.duplicate_fields)
            if all(value is not None and value != "" for value in signature):
                seen_duplicates[(agreement.id, *signature)].append(charge.id)
        group_key = (agreement.id, tuple(s.id for s in matched), charge.concept, charge.currency)
        groups[group_key].append(charge)
        group_shipments[group_key] = matched
    for ids in seen_duplicates.values():
        if len(ids) > 1:
            duplicate_ids.update(ids)
    incomplete = any(issue.category in {"file", "mapping", "row"} for issue in dataset.issues)
    observed_scopes = {(key[0], key[1]) for key in groups}
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
                        group_key = (
                            agreement.id,
                            tuple(s.id for s in matched),
                            rule.concept,
                            agreement.currency,
                        )
                        groups.setdefault(group_key, [])
                        group_shipments[group_key] = matched
            except EvaluationError:
                if (agreement.id, tuple(s.id for s in matched)) in observed_scopes:
                    continue
                group_key = (
                    agreement.id,
                    tuple(s.id for s in matched),
                    "(cobertura sin versión)",
                    agreement.currency,
                )
                groups.setdefault(group_key, [])
                group_shipments[group_key] = matched
    # Overlapping allocations of a single concept cannot independently assert full expected totals.
    allocations = defaultdict(set)
    for group_key in groups:
        aid, sids, concept, currency = group_key
        for sid in sids:
            allocations[(aid, sid, concept, currency)].add(group_key)
    overlapping = {
        group_key
        for allocation_key, group_set in allocations.items()
        if len(group_set) > 1 or allocation_key in uncertain_allocations
        for group_key in group_set
    }
    for group_key in sorted(groups):
        agreement_id, _, concept, currency = group_key
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
            reasons = []
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
            if group_key in overlapping:
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
                        "reasons": [str(exc)],
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
