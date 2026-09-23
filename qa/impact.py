"""Conservative impact inventory; reads SQLite without creating schema or triggers."""

import sqlite3
from collections import defaultdict
from pathlib import Path

from .invariants import integrity_errors, json_load


def operators(value):
    found = set()
    if isinstance(value, dict):
        if isinstance(value.get("op"), str):
            found.add(value["op"])
        for child in value.values():
            found.update(operators(child))
    elif isinstance(value, list):
        for child in value:
            found.update(operators(child))
    return found


def inventory(db: Path, filters: dict[str, str] | None = None) -> dict:
    if not db.is_file():
        raise ValueError("Database must already exist; inventory never creates it")
    filters = filters or {}
    allowed = {
        "engine_artifact",
        "engine_version",
        "feature",
        "currency",
        "agreement",
        "rule",
        "source_type",
        "importer_hash",
    }
    if not set(filters) <= allowed:
        raise ValueError("Unsupported impact filter")
    conn = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA query_only=ON")
        columns = {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
        required = {
            "id",
            "input_hash",
            "result_hash",
            "artifact_hash",
            "snapshot",
            "result",
            "metadata",
            "created_at",
        }
        if not required <= columns:
            raise ValueError("Unknown/incomplete runs schema: impact is unknown, not empty")
        entries = []
        for row in conn.execute(
            "SELECT id,input_hash,result_hash,artifact_hash,snapshot,result,metadata,created_at FROM runs ORDER BY id"
        ):
            entry = {
                "run_id": row["id"],
                "created_at_observed": row["created_at"],
                "client_id": None,
                "classification": "unknown",
                "reasons": [],
                "evidence": {},
            }
            try:
                snapshot, result, metadata = (
                    json_load(row[key]) for key in ("snapshot", "result", "metadata")
                )
                run = {**dict(row), "snapshot": snapshot, "result": result, "decisions": []}
                failures = integrity_errors(run)
                if failures:
                    entry["reasons"] = [
                        "Stored content failed integrity: include until investigated",
                        *failures,
                    ]
                    entries.append(entry)
                    continue
                features = operators(snapshot.get("agreements", [])) | operators(result.get("findings", []))
                charge_settlements = {c["id"]: c["settlement"] for c in snapshot["charges"]}
                obligation_settlements: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
                for finding in result["findings"]:
                    for shipment_id in finding["shipment_ids"]:
                        key = (finding["agreement"], shipment_id, finding["concept"], finding["currency"])
                        obligation_settlements[key].update(
                            charge_settlements[cid] for cid in finding["charge_ids"]
                        )
                if any(len(settlements) > 1 for settlements in obligation_settlements.values()):
                    features.add("cross_settlement")
                for agreement in snapshot["agreements"]:
                    matching = agreement["matching"]
                    if matching.get("cardinality") == "group":
                        features.add("group")
                    if matching.get("explicit"):
                        features.add("explicit")
                    if any(k.get("aliases") for k in matching["keys"]):
                        features.add("aliases")
                    if any(r.get("evidence") for v in agreement["versions"] for r in v["rules"]):
                        features.add("evidence")
                document_names = list(snapshot.get("documents", {}).values())
                source_types = {Path(name).suffix.lower().removeprefix(".") for name in document_names}
                source_unknown = not source_types or "" in source_types
                values = {
                    "engine_artifact": {row["artifact_hash"]},
                    "engine_version": {result["engine_version"]},
                    "feature": features,
                    "currency": {c["currency"] for c in snapshot["charges"]}
                    | {a["currency"] for a in snapshot["agreements"]},
                    "agreement": {a["id"] for a in snapshot["agreements"]},
                    "rule": {
                        r["id"] for a in snapshot["agreements"] for v in a["versions"] for r in v["rules"]
                    },
                    "source_type": source_types,
                    "importer_hash": {metadata["importer_hash"]} if metadata.get("importer_hash") else None,
                }
                decisions = []
                for name, wanted in filters.items():
                    actual = values[name]
                    if actual is None or (name == "source_type" and wanted not in actual and source_unknown):
                        decisions.append("unknown")
                        entry["reasons"].append(f"{name}: unavailable; cannot exclude")
                    elif wanted in actual:
                        decisions.append("match")
                        entry["reasons"].append(f"{name}: observed candidate")
                    else:
                        decisions.append("excluded")
                        entry["reasons"].append(f"{name}: observed value does not match")
                entry["classification"] = (
                    "excluded"
                    if "excluded" in decisions
                    else "unknown"
                    if "unknown" in decisions
                    else "match"
                )
                entry["evidence"] = {
                    key: sorted(value) if value is not None else None for key, value in values.items()
                }
                entry["label_observed"] = snapshot.get("label")
                entry["limitations"] = (
                    "Metadata/created_at not authenticated by run hash. Source type inferred from recorded filename; verify importer manifest. Match is candidate, not confirmed affected."
                )
            except (KeyError, ValueError, TypeError, AttributeError, RecursionError) as exc:
                entry["classification"] = "unknown"
                entry["reasons"] = [
                    f"Unreadable/incomplete run: {type(exc).__name__}; include until investigated"
                ]
            entries.append(entry)
    finally:
        conn.close()
    candidates = [e for e in entries if e["classification"] != "excluded"]
    return {
        "database": str(db),
        "filters": filters,
        "candidates": candidates,
        "excluded": [e for e in entries if e["classification"] == "excluded"],
        "scanned": len(entries),
        "client_identity": "not available; use external client-to-database registry",
        "scope": "Configured OR executed features; conservative candidate superset. No original blob or decision-chain verification in this inventory. No writes.",
    }
