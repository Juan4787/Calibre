"""Operational contracts: compact inputs, documentary control and immutable revisions."""

import hashlib
import sqlite3
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from test_importing import csv_data, mapping

from freight_audit.canonical import canonical, digest
from freight_audit.engine import audit
from freight_audit.models import Dataset
from freight_audit.server import create_app
from freight_audit.storage import IntegrityError, Store


def inputs(rows=1):
    shipments = csv_data("".join(f"S{i};{i:05};10;01/05/2026\n" for i in range(1, rows + 1)))
    charges = (
        b"id;settlement;reference;carrier;agreement;concept;amount;currency\nC1;L1;00001;C;A;base;100;ARS\n"
    )
    charge_mapping = {
        "id": "charge-test",
        "version": "1",
        "entity": "charges",
        "columns": [
            {"source": key, "target": key, "type": "decimal" if key == "amount" else "text"}
            for key in (
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
    }
    return {"shipments": (shipments, mapping().model_dump(mode="json")), "charges": (charges, charge_mapping)}


def upload(client, rows=1):
    refs = {}
    for role, (data, config) in inputs(rows).items():
        response = client.post(
            "/api/import",
            files={"file": (role + ".csv", data)},
            data={"mapping": canonical(config), "compact": "true"},
        )
        assert response.status_code == 200, response.text
        result = response.json()
        assert "records" not in result, (
            "Compact import must not send authoritative records through the browser"
        )
        assert "import_id" in result
        refs[role] = result["import_id"]
    return refs


def body_for(raw_dataset, refs):
    return {
        "label": "Synthetic server-held imports",
        "imports": refs,
        "agreements": raw_dataset["agreements"],
    }


def authorized_client(path):
    client = TestClient(create_app(path))
    client.headers["X-Freight-Local"] = client.get("/api/session").json()["token"]
    return client


def test_compact_import_request_preserves_all_records(tmp_path, raw_dataset):
    with authorized_client(tmp_path / "refs.db") as client:
        refs = upload(client, rows=1200)
        body = body_for(raw_dataset, refs)
        assert len(canonical(body).encode()) < 5000
        preflight = client.post("/api/audit/preflight", json=body)
        assert preflight.status_code == 200, preflight.text
        response = client.post("/api/audit", json=body)
        assert response.status_code == 200, response.text
        run = client.get("/api/runs/" + response.json()["run_id"]).json()
        assert len(run["snapshot"]["shipments"]) == 1200
        assert run["result"]["summary"]["currencies"]["ARS"]["actual"] == "100"
        assert run["metadata"]["provenance"]["checked_records"] == 1201
        assert client.post(f"/api/runs/{run['id']}/replay").json()["identical"]


def test_compact_request_rejects_injected_records_and_wrong_role(tmp_path, raw_dataset):
    with authorized_client(tmp_path / "tamper.db") as client:
        refs = upload(client)
        body = body_for(raw_dataset, refs)
        body["shipments"] = []
        assert client.post("/api/audit", json=body).status_code == 422
        body.pop("shipments")
        body["imports"]["shipments"] = refs["charges"]
        assert client.post("/api/audit", json=body).status_code == 422
        assert client.get("/api/runs").json() == []


def test_compact_import_issues_are_bounded_and_all_pages_accessible(tmp_path):
    with authorized_client(tmp_path / "issues.db") as client:
        data, config = inputs()["charges"]
        config["concept_map"] = {"different": "base"}
        data = (
            data.splitlines()[0]
            + b"\n"
            + b"".join(f"C{i};L;R;C;A;unknown-{i};100;ARS\n".encode() for i in range(121))
        )
        response = client.post(
            "/api/import",
            files={"file": ("warnings.csv", data)},
            data={"mapping": canonical(config), "compact": "true"},
        )
        result = response.json()
        assert result["issue_count"] == 121 and len(result["issues"]) <= 50
        messages = []
        for page in range(3):
            chunk = client.get(f"/api/imports/{result['import_id']}/issues", params={"page": page}).json()
            assert len(chunk["issues"]) <= 50
            messages += [i["message"] for i in chunk["issues"]]
        assert len(messages) == 121 and "unknown-120" in messages[-1]


def independent_control(rows=1):
    data = inputs(rows)
    source_s = hashlib.sha256(data["shipments"][0]).hexdigest()
    source_c = hashlib.sha256(data["charges"][0]).hexdigest()
    return {
        "schema": "freight-audit-external-control/v1",
        "source_hashes": [source_s, source_c],
        "shipments_by_source": {source_s: rows},
        "charges_by_source": {source_c: 1},
        "charge_totals_by_source": {source_c: {"ARS": "100"}},
        "shipment_count": rows,
        "charge_count": 1,
        "actual_by_currency": {"ARS": "100"},
    }


def test_document_control_is_bound_to_snapshot_and_not_overwritten(tmp_path, raw_dataset):
    with authorized_client(tmp_path / "control.db") as client:
        refs = upload(client)
        body = body_for(raw_dataset, refs)
        original = client.post("/api/audit", json=body).json()["run_id"]
        body["external_control"] = independent_control()
        checked = client.post("/api/audit", json=body)
        assert checked.status_code == 200, checked.text
        new_id = checked.json()["run_id"]
        assert new_id != original
        run = client.get("/api/runs/" + new_id).json()
        assert run["metadata"]["document_control"]["status"] == "matched"
        assert run["snapshot"]["external_control"] == body["external_control"]
        assert (
            "inventario, cantidades e importes coinciden"
            in client.get(f"/api/runs/{new_id}/export/html").text
        )
        body["external_control"]["charge_count"] = 2
        assert client.post("/api/audit", json=body).status_code == 422
        assert len(client.get("/api/runs").json()) == 2


def test_revision_links_preserve_previous_result(tmp_path, raw_dataset):
    with authorized_client(tmp_path / "revision.db") as client:
        original = client.post("/api/audit", json=raw_dataset).json()["run_id"]
        before = client.get("/api/runs/" + original).json()
        revised = deepcopy(raw_dataset)
        revised.update(
            parent_run_id=original,
            revision_kind="correction",
            revision_note="Independent synthetic correction",
        )
        revised["charges"][0]["amount"] = "130"
        response = client.post("/api/audit", json=revised)
        assert response.status_code == 200, response.text
        new_id = response.json()["run_id"]
        after = client.get("/api/runs/" + original).json()
        assert after["result"] == before["result"] and after["result_hash"] == before["result_hash"]
        assert [r["id"] for r in after["revisions"]] == [new_id]
        assert client.get("/api/runs/" + new_id).json()["snapshot"]["parent_run_id"] == original


def test_contract_reference_requires_preserved_document_and_valid_target(tmp_path, raw_dataset):
    with authorized_client(tmp_path / "contract.db") as client:
        attachment = client.post(
            "/api/evidence-file", files={"file": ("contract.pdf", b"synthetic contract fixture")}
        ).json()
        raw_dataset["contract_sources"] = [
            {
                "document_hash": attachment["document_hash"],
                "agreement": "A",
                "version": "V1",
                "rule": "R1",
                "page": 1,
                "approved_by": "Synthetic QA",
                "approved_on": "2026-10-29",
            }
        ]
        response = client.post("/api/audit", json=raw_dataset)
        assert response.status_code == 200, response.text
        run_id = response.json()["run_id"]
        raw_dataset["contract_sources"][0]["version"] = "missing"
        assert client.post("/api/audit", json=raw_dataset).status_code == 422
        assert client.get("/api/runs/" + run_id).json()["snapshot"]["contract_sources"][0]["page"] == 1


def test_health_identifies_installed_engine_without_creating_runs(tmp_path):
    with authorized_client(tmp_path / "health.db") as client:
        result = client.get("/api/health")
        assert result.status_code == 200
        assert result.json()["engine_version"] == "0.3.0"
        assert result.json()["database_schema"] == 2
        assert client.get("/api/runs").json() == []


def test_workspace_isolation_and_restore_preserve_history(tmp_path, raw_dataset):
    with authorized_client(tmp_path / "local.db") as client:
        first = client.post("/api/workspaces", json={"name": "Cliente ficticio A"})
        assert first.status_code == 200, first.text
        first_id = first.json()["id"]
        client.headers["X-Freight-Workspace"] = first_id
        run_id = client.post("/api/audit", json=raw_dataset).json()["run_id"]
        before = client.get("/api/runs/" + run_id).json()
        backup = client.get("/api/workspace/backup")
        assert backup.status_code == 200 and backup.content.startswith(b"SQLite format 3")
        second = client.post("/api/workspaces", json={"name": "Cliente ficticio B"}).json()["id"]
        client.headers["X-Freight-Workspace"] = second
        assert client.get("/api/runs").json() == []
        assert client.get("/api/runs/" + run_id).status_code == 404
        restored = client.post(
            "/api/workspaces/restore",
            files={"file": ("backup.db", backup.content)},
            data={"name": "A recuperado (ficticio)"},
        )
        assert restored.status_code == 200, restored.text
        client.headers["X-Freight-Workspace"] = restored.json()["id"]
        after = client.get("/api/runs/" + run_id).json()
        assert after == before
        assert client.post(f"/api/runs/{run_id}/replay").json()["identical"]
        assert restored.json()["id"] not in {first_id, second}
        client.headers["X-Freight-Workspace"] = first_id
        assert client.get("/api/runs/" + run_id).json() == before


def test_invalid_workspace_and_corrupt_restore_never_fall_back(tmp_path):
    with authorized_client(tmp_path / "local.db") as client:
        client.headers["X-Freight-Workspace"] = "../elsewhere"
        assert client.get("/api/runs").status_code == 404
        client.headers.pop("X-Freight-Workspace")
        before = client.get("/api/workspaces").json()
        response = client.post(
            "/api/workspaces/restore", files={"file": ("bad.db", b"corrupt")}, data={"name": "Invalid"}
        )
        assert response.status_code == 422
        assert client.get("/api/workspaces").json() == before


def test_new_identity_also_protects_documentary_metadata(tmp_path, raw_dataset):
    store = Store(tmp_path / "metadata.db")
    dataset = Dataset.model_validate(raw_dataset)
    run_id = store.save(dataset, audit(dataset))
    run = store.load(run_id)
    run["metadata"]["provenance"]["checked_records"] = 999
    with store.connect() as connection:
        connection.execute("DROP TRIGGER immutable_runs_UPDATE")
        connection.execute("UPDATE runs SET metadata=? WHERE id=?", (canonical(run["metadata"]), run_id))
    with pytest.raises(IntegrityError):
        store.load(run_id)


def test_restore_rejects_foreign_sqlite_and_altered_originals(tmp_path, raw_dataset):
    from freight_audit.workspaces import Workspaces

    registry = Workspaces(Store(tmp_path / "registry.db"))
    foreign = tmp_path / "foreign.db"
    with sqlite3.connect(foreign) as connection:
        connection.execute("CREATE TABLE unrelated (data TEXT)")
    with pytest.raises(ValueError):
        registry.create("Foreign", foreign.read_bytes())
    original = Store(tmp_path / "original.db")
    source_hash = original.put_source(b"synthetic original")
    dataset = Dataset.model_validate({**raw_dataset, "documents": {source_hash: "original.txt"}})
    original.save(dataset, audit(dataset))
    with original.connect() as connection:
        connection.execute("DROP TRIGGER immutable_sources_UPDATE")
        connection.execute("UPDATE sources SET data=?", (b"altered",))
    with pytest.raises(ValueError):
        registry.create("Corrupt", original.path.read_bytes())
    assert len(registry.list()) == 1


def test_import_reference_integrity_and_cross_workspace(tmp_path, raw_dataset):
    path = tmp_path / "refs.db"
    with authorized_client(path) as client:
        refs = upload(client)
        other = client.post("/api/workspaces", json={"name": "Other fictional client"}).json()["id"]
        client.headers["X-Freight-Workspace"] = other
        assert client.post("/api/audit", json=body_for(raw_dataset, refs)).status_code == 404
        client.headers.pop("X-Freight-Workspace")
        with Store(path).connect() as connection:
            connection.execute("DROP TRIGGER immutable_imports_UPDATE")
            connection.execute("UPDATE imports SET payload='{}' WHERE id=?", (refs["shipments"],))
        assert client.post("/api/audit", json=body_for(raw_dataset, refs)).status_code == 422
        assert client.get("/api/runs").json() == []


def legacy_database(path, raw_dataset):
    """Hand-built v1 storage fixture; no current Store initialization."""
    dataset = Dataset.model_validate(raw_dataset)
    snapshot = dataset.model_dump(mode="json")
    for field in ("contract_sources", "external_control", "parent_run_id", "revision_kind", "revision_note"):
        snapshot.pop(field)
    result = audit(dataset).model_dump(mode="json")
    result["engine_version"] = "0.2.0"
    input_hash, result_hash, artifact_hash = digest(snapshot), digest(result), "f" * 64
    identifier = digest([input_hash, result_hash, artifact_hash])
    with sqlite3.connect(path) as connection:
        connection.executescript("""
            CREATE TABLE sources (hash TEXT PRIMARY KEY, data BLOB NOT NULL);
            CREATE TABLE configs (hash TEXT PRIMARY KEY, kind TEXT NOT NULL, name TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE runs (id TEXT PRIMARY KEY, input_hash TEXT NOT NULL, result_hash TEXT NOT NULL, artifact_hash TEXT NOT NULL, snapshot TEXT NOT NULL, result TEXT NOT NULL, metadata TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE decisions (seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(id), finding_id TEXT NOT NULL, payload TEXT NOT NULL, previous_hash TEXT NOT NULL, hash TEXT NOT NULL, created_at TEXT NOT NULL);
            PRAGMA user_version=1;
        """)
        connection.execute(
            "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?)",
            (
                identifier,
                input_hash,
                result_hash,
                artifact_hash,
                canonical(snapshot),
                canonical(result),
                canonical({"python": "legacy fixture"}),
                "2026-01-01T00:00:00+00:00",
            ),
        )
    return identifier, snapshot, result


def test_schema_v1_migration_preserves_old_identity_and_result(tmp_path, raw_dataset):
    path = tmp_path / "legacy.db"
    identifier, snapshot, result = legacy_database(path, raw_dataset)
    store = Store(path)
    preserved = store.load(identifier)
    assert preserved["snapshot"] == snapshot and preserved["result"] == result
    assert "run_identity_version" not in preserved["metadata"]
    with store.connect() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
    with pytest.raises(IntegrityError, match="cambió"):
        store.replay(identifier)
    assert store.load(identifier)["result"] == result


def test_failed_v2_migration_rolls_back_schema_changes(tmp_path, raw_dataset):
    path = tmp_path / "legacy-invalid.db"
    identifier, _, _ = legacy_database(path, raw_dataset)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE runs SET snapshot='{' WHERE id=?", (identifier,))
    with pytest.raises(sqlite3.DatabaseError):
        Store(path)
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("SELECT name FROM sqlite_master WHERE name='imports'").fetchall() == []
        assert connection.execute("SELECT snapshot FROM runs WHERE id=?", (identifier,)).fetchone()[0] == "{"


def test_independent_checker_includes_contract_original_not_repeated_in_registry(tmp_path, raw_dataset):
    from qa.external_control import compare_external_control

    with authorized_client(tmp_path / "contract-inventory.db") as client:
        refs = upload(client)
        attachment = client.post(
            "/api/evidence-file", files={"file": ("contract.txt", b"fictional reference")}
        ).json()
        body = body_for(raw_dataset, refs)
        body["contract_sources"] = [
            {"document_hash": attachment["document_hash"], "agreement": "A", "version": "V1", "page": 1}
        ]
        body["external_control"] = independent_control()
        body["external_control"]["source_hashes"].append(attachment["document_hash"])
        response = client.post("/api/audit", json=body)
        assert response.status_code == 200, response.text
        run = client.get("/api/runs/" + response.json()["run_id"]).json()
        assert attachment["document_hash"] not in run["snapshot"]["documents"]
        assert compare_external_control(run, body["external_control"])["passed"]
