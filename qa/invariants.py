"""Independent checks over serialized snapshots/results. Never imports audit/summarize."""

import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from .reference import rational

STATUSES = ("PASS", "FAIL", "REVIEW", "UNDETERMINABLE")
BUCKET_KEYS = (
    "actual",
    "determinable",
    "pass",
    "review",
    "undeterminable",
    "confirmed_net_difference",
    "confirmed_overcharge",
    "confirmed_undercharge",
)


def json_load(value: str | bytes):
    def pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = item
        return result

    def nonfinite(value):
        raise ValueError(f"Non-finite JSON constant: {value}")

    return json.loads(value, object_pairs_hook=pairs, parse_constant=nonfinite)


def read_json(path: Path):
    return json_load(path.read_bytes())


def stable_hash(value) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def integrity_errors(run: dict) -> list[str]:
    errors = []
    for key, payload in (("input_hash", "snapshot"), ("result_hash", "result")):
        if stable_hash(run[payload]) != run[key]:
            errors.append(f"INV-28 {key}: content differs from recorded hash")
    expected_id = stable_hash([run["input_hash"], run["result_hash"], run["artifact_hash"]])
    if run["id"] != expected_id:
        errors.append("INV-28 run id mismatch")
    previous = run["id"]
    last_seq = -1
    for decision in run.get("decisions", []):
        if (
            decision["previous_hash"] != previous
            or stable_hash([previous, decision["payload"], decision["created_at"]]) != decision["hash"]
            or decision["seq"] <= last_seq
        ):
            errors.append("INV-24 decision chain mismatch")
        previous, last_seq = decision["hash"], decision["seq"]
    return errors


def economic_projection(result: dict) -> dict:
    fields = (
        "id",
        "agreement",
        "version",
        "rule",
        "concept",
        "currency",
        "actual",
        "expected",
        "difference",
        "confirmed_difference",
        "status",
    )
    rows = [
        {
            **{field: row.get(field) for field in fields},
            "charge_ids": sorted(row["charge_ids"]),
            "shipment_ids": sorted(row["shipment_ids"]),
        }
        for row in result["findings"]
    ]
    summary = {k: v for k, v in result["summary"].items() if k != "economic_definition"}
    return {"findings": sorted(rows, key=lambda x: x["id"]), "summary": summary}


def check_run(run: dict, *, require_provenance=False, verify_hashes=True) -> list[str]:
    """Input format errors raise ValueError/KeyError; contradictions return diagnostic strings."""
    errors = integrity_errors(run) if verify_hashes else []
    snapshot, result = run["snapshot"], run["result"]

    def require(condition, code, message):
        if not condition:
            errors.append(f"{code} {message}")

    entities = {}
    for name in ("shipments", "charges", "agreements", "evidence"):
        records = snapshot.get(name, [])
        entities[name] = {row["id"]: row for row in records}
        require(len(entities[name]) == len(records), "INV-04", f"duplicate {name} id")
    charges, shipments, agreements, evidence = (
        entities[n] for n in ("charges", "shipments", "agreements", "evidence")
    )
    incomplete = any(i["category"] in {"row", "file", "mapping"} for i in snapshot.get("issues", []))
    require(result["issues"] == snapshot.get("issues", []), "INV-29", "issues differ from snapshot")
    seen: Counter[str] = Counter()
    ids = set()
    counts = dict.fromkeys(STATUSES, 0)
    charge_counts: Counter[str] = Counter()
    buckets: dict[str, dict[str, Fraction]] = defaultdict(lambda: dict.fromkeys(BUCKET_KEYS, Fraction(0)))
    for finding in result["findings"]:
        fid, status = finding["id"], finding["status"]
        require(fid not in ids, "INV-04", f"duplicate finding {fid}")
        ids.add(fid)
        if status not in STATUSES:
            raise ValueError(f"Unknown finding status: {status}")
        counts[status] += 1
        cids, sids = finding["charge_ids"], finding["shipment_ids"]
        seen.update(cids)
        charge_counts[status] += len(cids)
        actual, confirmed = rational(finding["actual"]), rational(finding["confirmed_difference"])
        expected = None if finding["expected"] is None else rational(finding["expected"])
        delta = None if finding["difference"] is None else rational(finding["difference"])
        scope_charges = [charges[cid] for cid in cids if cid in charges]
        require(all(cid in charges for cid in cids), "INV-04", f"{fid}: unknown charge")
        require(all(sid in shipments for sid in sids), "INV-09", f"{fid}: unknown shipment")
        require(len(sids) == len(set(sids)), "INV-09", f"{fid}: repeated shipment")
        require(
            actual == sum((rational(c["amount"]) for c in scope_charges), Fraction(0)),
            "INV-05",
            f"{fid}: actual differs from charges",
        )
        require(
            all(c["currency"] == finding["currency"] for c in scope_charges), "INV-06", f"{fid}: currency mix"
        )
        require(
            all(
                c["concept"] == finding["concept"] and c["agreement"] == finding["agreement"]
                for c in scope_charges
            ),
            "INV-09",
            f"{fid}: mixed concept/agreement",
        )
        if expected is None:
            require(delta is None, "INV-03", f"{fid}: difference without expectation")
        else:
            require(delta == actual - expected, "INV-03", f"{fid}: wrong difference sign/value")
        if status != "FAIL":
            require(confirmed == 0, "INV-01", f"{fid}: uncertain/PASS money confirmed")
        else:
            require(
                delta is not None and confirmed == delta,
                "INV-03",
                f"{fid}: confirmed differs from difference",
            )
        if status == "UNDETERMINABLE":
            require(expected is None and delta is None, "INV-13", f"{fid}: arbitrary expectation")
        if not cids:
            require(
                status in {"REVIEW", "UNDETERMINABLE"} and actual == 0,
                "INV-18",
                f"{fid}: empty charge scope confirmed",
            )
        determinate = status in {"PASS", "FAIL"}
        if determinate:
            require(not incomplete, "INV-11", f"{fid}: incomplete import certified")
            require(bool(sids) and bool(cids), "INV-09", f"{fid}: empty determinate scope")
            require(
                expected is not None and delta is not None, "INV-02", f"{fid}: missing expected/difference"
            )
            require(not finding.get("missing_evidence"), "INV-10", f"{fid}: missing evidence certified")
            agreement = agreements.get(finding["agreement"])
            if agreement is None:
                errors.append(f"INV-07 {fid}: missing agreement")
            else:
                require(
                    agreement["currency"] == finding["currency"], "INV-06", f"{fid}: wrong agreement currency"
                )
                require(
                    all(c["carrier"] == agreement["carrier"] for c in scope_charges),
                    "INV-09",
                    f"{fid}: wrong carrier",
                )
                if expected is not None and delta is not None:
                    tolerance = max(
                        rational(agreement["tolerance_absolute"]),
                        abs(expected) * rational(agreement["tolerance_relative"]),
                    )
                    require(
                        (abs(delta) <= tolerance) == (status == "PASS"),
                        "INV-02",
                        f"{fid}: status outside tolerance",
                    )
                versions = [v for v in agreement["versions"] if v["id"] == finding.get("version")]
                require(len(versions) == 1, "INV-07", f"{fid}: unknown selected version")
                for sid in sids:
                    shipment = shipments.get(sid, {})
                    value = shipment.get("attributes", {}).get(
                        agreement["date_field"].removeprefix("attributes."), {}
                    )
                    date = value.get("value") if value.get("type") == "date" else None
                    applicable = [
                        v
                        for v in agreement["versions"]
                        if date
                        and v["valid_from"] <= date
                        and (v.get("valid_to") is None or date <= v["valid_to"])
                    ]
                    require(
                        len(applicable) == 1 and applicable[0]["id"] == finding.get("version"),
                        "INV-08",
                        f"{fid}: wrong/ambiguous date version",
                    )
                    require(
                        shipment.get("carrier") == agreement["carrier"],
                        "INV-09",
                        f"{fid}: shipment carrier mismatch",
                    )
                if versions:
                    rules = [
                        r
                        for r in versions[0]["rules"]
                        if r["id"] == finding.get("rule") and r["concept"] == finding["concept"]
                    ]
                    require(len(rules) == 1, "INV-07", f"{fid}: unknown selected rule")
                    if rules:
                        _check_evidence(rules[0], finding, evidence, require)
            comparison = [t for t in finding.get("trace", []) if t["op"] == "comparison"]
            require(len(comparison) == 1, "INV-23", f"{fid}: missing comparison trace")
            if comparison:
                trace = comparison[0]
                require(
                    rational(trace["output"]) == delta
                    and rational(trace["details"]["actual"]) == actual
                    and rational(trace["details"]["expected"]) == expected,
                    "INV-23",
                    f"{fid}: comparison trace mismatch",
                )
        bucket = buckets[finding["currency"]]
        bucket["actual"] += actual
        if determinate:
            bucket["determinable"] += actual
        if status in {"PASS", "REVIEW", "UNDETERMINABLE"}:
            bucket[status.lower()] += actual
        # Independently derive this from state and difference, never trust confirmed_difference.
        contribution = delta if status == "FAIL" and delta is not None else Fraction(0)
        bucket["confirmed_net_difference"] += contribution
        bucket["confirmed_overcharge"] += max(contribution, Fraction(0))
        bucket["confirmed_undercharge"] += min(contribution, Fraction(0))
    require(
        seen == Counter({cid: 1 for cid in charges}),
        "INV-04",
        "accepted charges are not a partition of findings",
    )
    summary = result["summary"]
    for key, expected_count in (
        ("counts", counts),
        ("total_findings", len(result["findings"])),
        ("determinable_findings", counts["PASS"] + counts["FAIL"]),
        ("charge_counts", dict(charge_counts)),
        ("import_complete", not incomplete),
    ):
        require(summary.get(key) == expected_count, "INV-03", f"summary.{key} mismatch")
    require(set(summary["currencies"]) == set(buckets), "INV-06", "summary currency set mismatch")
    for currency, bucket in buckets.items():
        observed = summary["currencies"].get(currency, {})
        require(set(observed) == set(BUCKET_KEYS), "INV-03", f"{currency}: missing/extra metrics")
        for key, value in bucket.items():
            require(
                key in observed and rational(observed[key]) == value,
                "INV-03",
                f"{currency}.{key}: summary differs",
            )
        source_total = sum(
            (rational(c["amount"]) for c in charges.values() if c["currency"] == currency), Fraction(0)
        )
        require(bucket["actual"] == source_total, "INV-05", f"{currency}: source total mismatch")
    for decision in run.get("decisions", []):
        require(decision["payload"]["finding_id"] in ids, "INV-24", "decision references unknown finding")
        require(
            set(decision["payload"].get("evidence_ids", [])) <= set(evidence),
            "INV-24",
            "decision evidence missing",
        )
    if require_provenance:
        for entity, records in (("charges", charges), ("shipments", shipments)):
            fields = {"id", "reference", "carrier"} | (
                {"amount", "currency", "concept", "agreement", "settlement"} if entity == "charges" else set()
            )
            for record in records.values():
                needed = fields | {f"attributes.{key}" for key in record.get("attributes", {})}
                provenance = record.get("provenance", {})
                require(needed <= set(provenance), "INV-22", f"{record['id']}: missing provenance fields")
                for ref in provenance.values():
                    require(
                        ref["document"] in snapshot.get("documents", {})
                        and ref["row"] >= 1
                        and bool(ref["column"])
                        and bool(ref["transform"]),
                        "INV-22",
                        f"{record['id']}: incomplete source reference",
                    )
    return errors


def _check_evidence(rule, finding, evidence, require):
    cited = set(finding.get("evidence_ids", []))
    require(cited <= set(evidence), "INV-10", f"{finding['id']}: evidence id absent")
    for requirement in rule.get("evidence", []):
        candidates = [
            e
            for eid, e in evidence.items()
            if eid in cited
            and e["kind"] in requirement["any_of"]
            and (not requirement.get("document_required", False) or e.get("document_hash"))
        ]
        scope = requirement.get("scope", "group")
        if scope == "each_shipment":
            sufficient = all(
                any(sid in e.get("shipment_ids", []) for e in candidates) for sid in finding["shipment_ids"]
            )
        elif scope == "each_charge":
            sufficient = all(
                any(cid in e.get("charge_ids", []) for e in candidates) for cid in finding["charge_ids"]
            )
        else:
            sufficient = any(
                set(e.get("shipment_ids", [])) & set(finding["shipment_ids"])
                or set(e.get("charge_ids", [])) & set(finding["charge_ids"])
                for e in candidates
            )
        require(sufficient, "INV-10", f"{finding['id']}: insufficient cited evidence ({scope})")
