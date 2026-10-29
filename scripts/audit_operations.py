#!/usr/bin/env python3
"""Reproduce the old 32 MiB wizard barrier with references and exact anchors.

Fictional CSV inputs; no production DB, external services or expected values read
from the audit result. Run sequentially with the other resource-heavy checks.
"""

import argparse
import json
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from freight_audit.canonical import bytes_hash, canonical
from freight_audit.fixtures import agreement, column, const, constant, rule, version
from freight_audit.server import create_app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=36000)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.rows <= 100000:
        parser.error("Use between 1 and 100000 fictional operations")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    shipments = (
        "id;ref;weight;date\n" + "".join(f"S{i};{i:05};10;01/05/2026\n" for i in range(1, args.rows + 1))
    ).encode()
    charges = (
        b"id;settlement;reference;carrier;agreement;concept;amount;currency\nC1;L1;00001;C;A;base;100;ARS\n"
    )
    mappings = {
        "shipments": {
            "id": "operations-volume-fictional",
            "version": "1",
            "entity": "shipments",
            "columns": [
                column("id", "id"),
                column("ref", "reference"),
                constant("carrier", "C"),
                column("weight", "attributes.weight", "decimal", unit="kg"),
                column("date", "attributes.service_date", "date"),
            ],
        },
        "charges": {
            "id": "charges-volume-fictional",
            "version": "1",
            "entity": "charges",
            "columns": [
                column(field, field, "decimal" if field == "amount" else "text")
                for field in (
                    "id",
                    "settlement",
                    "reference",
                    "carrier",
                    "agreement",
                    "concept",
                    "amount",
                    "currency",
                )
            ],
        },
    }
    control = {
        "schema": "freight-audit-external-control/v1",
        "source_hashes": [bytes_hash(shipments), bytes_hash(charges)],
        "shipments_by_source": {bytes_hash(shipments): args.rows},
        "charges_by_source": {bytes_hash(charges): 1},
        "charge_totals_by_source": {bytes_hash(charges): {"ARS": "100"}},
        "shipment_count": args.rows,
        "charge_count": 1,
        "actual_by_currency": {"ARS": "100"},
    }
    started = time.perf_counter()
    receipt = {
        "scope": "Synthetic volume and API lifecycle; one billed operation, not 36000 priced charges or a real client",
        "rows": args.rows,
        "sources_bytes": {"shipments": len(shipments), "charges": len(charges)},
        "compact_response_bytes": {},
    }
    with (
        tempfile.TemporaryDirectory(prefix="calibre-operations-audit-") as directory,
        TestClient(create_app(Path(directory) / "audit.db")) as client,
    ):
        client.headers["X-Freight-Local"] = client.get("/api/session").json()["token"]
        references = {}
        for role, data in (("shipments", shipments), ("charges", charges)):
            response = client.post(
                "/api/import",
                files={"file": (role + ".csv", data)},
                data={"mapping": canonical(mappings[role]), "compact": "true"},
            )
            assert response.status_code == 200, response.text[:500]
            imported = response.json()
            assert (
                imported["accepted"] == (args.rows if role == "shipments" else 1)
                and imported["rejected_count"] == 0
            )
            assert "records" not in imported
            references[role] = imported["import_id"]
            receipt["compact_response_bytes"][role] = len(response.content)
        body = {
            "label": "Fictional volume anchor",
            "imports": references,
            "agreements": [agreement("A", "C", [version("V1", [rule("R1", "base", const("100", "ARS"))])])],
            "external_control": control,
        }
        receipt["audit_request_bytes"] = len(canonical(body).encode())
        assert receipt["audit_request_bytes"] < 10000
        response = client.post("/api/audit/preflight", json=body)
        assert response.status_code == 200 and response.json()["document_control"]["status"] == "matched", (
            response.text[:500]
        )
        response = client.post("/api/audit", json=body)
        assert response.status_code == 200, response.text[:500]
        run_id = response.json()["run_id"]
        run = client.get("/api/runs/" + run_id).json()
        assert len(run["snapshot"]["shipments"]) == args.rows and len(run["snapshot"]["charges"]) == 1
        assert run["metadata"]["provenance"]["checked_records"] == args.rows + 1
        summary = run["result"]["summary"]
        assert (
            summary["currencies"]["ARS"]["actual"] == "100"
            and summary["currencies"]["ARS"]["confirmed_net_difference"] == "0"
        )
        assert run["result"]["findings"][0]["expected"] == "100"
        assert client.post(f"/api/runs/{run_id}/replay").json()["identical"]
        legacy_payload = canonical(
            {
                k: v
                for k, v in run["snapshot"].items()
                if k
                not in {
                    "external_control",
                    "contract_sources",
                    "parent_run_id",
                    "revision_kind",
                    "revision_note",
                }
            }
        ).encode()
        receipt.update(
            old_style_request_bytes=len(legacy_payload),
            original_barrier_exceeded=len(legacy_payload) > 32 * 1024 * 1024,
            run_id=run_id,
            result_hash=run["result_hash"],
            engine_artifact_hash=run["artifact_hash"],
            checked_records=args.rows + 1,
            replay_identical=True,
            actual="100",
            expected="100",
            confirmed_net_difference="0",
            elapsed_seconds=round(time.perf_counter() - started, 3),
            passed=True,
        )
    (args.output_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
