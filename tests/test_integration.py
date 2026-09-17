import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from freight_audit.canonical import canonical, load_json
from freight_audit.engine import audit
from freight_audit.importing import ImportMapping, import_data
from freight_audit.models import Dataset
from freight_audit.project import load_project
from freight_audit.reporting import bundle_bytes, verify_bundle
from freight_audit.server import create_app
from freight_audit.storage import Store

ROOT = Path(__file__).resolve().parents[1]


def test_real_files_three_agreements_golden_and_second_client(tmp_path):
    store = Store(tmp_path / "data.db")
    dataset, imports = load_project(ROOT / "fixtures/project.json", store)
    result = audit(dataset)
    assert imports == {
        "shipments": {"accepted": 32, "rejected": []},
        "charges": {"accepted": 46, "rejected": []},
    }
    assert set(result.summary["counts"]) == {"PASS", "FAIL", "REVIEW", "UNDETERMINABLE"}
    assert all(count > 0 for count in result.summary["counts"].values())
    assert result.summary["currencies"]["ARS"] == {
        "actual": "43719.4",
        "determinable": "36706.4",
        "pass": "34485.4",
        "review": "3431",
        "undeterminable": "3582",
        "confirmed_net_difference": "-25",
        "confirmed_overcharge": "50",
        "confirmed_undercharge": "-75",
    }
    r1 = store.save(dataset, result)
    assert store.replay(r1)["identical"]
    second, _ = load_project(ROOT / "fixtures/second-client/project.json", store)
    second_result = audit(second)
    assert second_result.summary["counts"] == {"PASS": 1, "FAIL": 1, "REVIEW": 0, "UNDETERMINABLE": 0}
    assert [f.expected for f in second_result.findings] == ["194.25", "194.25"]
    assert second_result.summary["currencies"]["USD"]["confirmed_overcharge"] == "10"
    assert all(len(f.shipment_ids) == 3 for f in second_result.findings)
    assert second.agreements[0].date_field == "pickup"
    r2 = store.save(second, second_result)
    assert store.replay(r2)["identical"]
    bundle = verify_bundle(bundle_bytes(store, r2))
    assert len(bundle["snapshot"]["documents"]) == 2


def test_economic_result_unchanged_by_input_row_order(tmp_path):
    store = Store(tmp_path / "data.db")
    dataset, _ = load_project(ROOT / "fixtures/project.json", store)
    raw = dataset.model_dump()
    original = audit(dataset)
    for name in ("shipments", "charges", "agreements", "evidence"):
        raw[name].reverse()
    reordered = audit(Dataset.model_validate(raw))
    assert canonical(original) == canonical(reordered)


def test_invalid_fixture_rejects_visible_rows():
    config = ImportMapping.model_validate(load_json((ROOT / "fixtures/mapping-invalid.json").read_bytes()))
    result = import_data(
        (ROOT / "fixtures/operaciones-invalidas.csv").read_bytes(), "operaciones-invalidas.csv", config
    )
    assert result["accepted"] == 0 and result["rejected"] == [2]
    assert len(result["issues"]) == 2


def test_cli_full_run_exports_and_bundle_replay(tmp_path):
    out = tmp_path / "reports"
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "freight_audit.cli",
            "--db",
            str(tmp_path / "data.db"),
            "run",
            str(ROOT / "fixtures/second-client/project.json"),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    result = json.loads(process.stdout)
    assert result["summary"]["counts"]["FAIL"] == 1
    assert (out / "auditoria.xlsx").exists()
    verify = subprocess.run(
        [sys.executable, "-m", "freight_audit.cli", "verify-bundle", str(out / "auditoria.zip"), "--replay"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(verify.stdout)["identical"]


def client_with_token(tmp_path):
    client = TestClient(create_app(tmp_path / "web.db"))
    token = client.get("/api/session").json()["token"]
    client.headers["X-Freight-Local"] = token
    return client


def test_local_api_security_boundary(tmp_path):
    with TestClient(create_app(tmp_path / "data.db")) as client:
        assert client.post("/api/demo").status_code == 403
        token = client.get("/api/session").json()["token"]
        assert (
            client.post(
                "/api/demo", headers={"X-Freight-Local": token, "Origin": "https://other-site.example"}
            ).status_code
            == 403
        )
        assert client.get("/api/runs", headers={"Host": "external.example"}).status_code == 400
        page = client.get("/")
        assert page.status_code == 200
        assert "connect-src 'self'" in page.headers["content-security-policy"]
        assert "no-store" == page.headers["cache-control"]
        assert "https://" not in page.text


def test_api_runs_decisions_export_replay(tmp_path, raw_dataset):
    client = client_with_token(tmp_path)
    response = client.post("/api/audit", json=raw_dataset)
    assert response.status_code == 200, response.text
    run_id = response.json()["run_id"]
    run = client.get("/api/runs/" + run_id).json()
    f = run["result"]["findings"][0]
    decision = client.post(
        f"/api/runs/{run_id}/decisions",
        json={
            "finding_id": f["id"],
            "actor": "Operador",
            "action": "INFORMATION_REQUESTED",
            "note": "Solicitar respaldo al responsable",
        },
    )
    assert decision.status_code == 200, decision.text
    updated = client.get("/api/runs/" + run_id).json()
    assert updated["result"] == run["result"]
    assert len(updated["decisions"]) == 1
    assert client.post(f"/api/runs/{run_id}/replay").json()["identical"]
    export = client.get(f"/api/runs/{run_id}/export/zip")
    assert export.status_code == 200
    assert verify_bundle(export.content)["id"] == run_id


def test_api_import_with_mapping_and_provenance(tmp_path):
    client = client_with_token(tmp_path)
    mapping = (ROOT / "fixtures/mapping-charges.json").read_text()
    result = client.post(
        "/api/import",
        files={"file": ("liquidacion.csv", (ROOT / "fixtures/liquidacion.csv").read_bytes(), "text/csv")},
        data={"mapping": mapping},
    )
    assert result.status_code == 200, result.text
    assert result.json()["accepted"] == 46
    assert result.json()["records"][0]["provenance"]["amount"]["raw"]
    assert client.get("/api/configs").json()[0]["kind"] == "mapping"


def test_api_configuration_errors_use_recoverable_messages(tmp_path):
    client = client_with_token(tmp_path)
    result = client.post("/api/audit", json={"bad": "data"})
    assert result.status_code == 422
    assert "Corregir" in result.json()["error"]
    assert "Traceback" not in result.text
    assert "pydantic" not in result.text
    result = client.post("/api/configs/mapping", content='{"id":1,"id":2}')
    assert result.status_code == 422 and "repetida" in result.json()["error"]


def test_fully_offline_core(tmp_path, monkeypatch):
    import socket

    def forbidden(*args, **kwargs):
        raise AssertionError("Auditing must not contact any network")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    store = Store(tmp_path / "data.db")
    dataset, _ = load_project(ROOT / "fixtures/project.json", store)
    result = audit(dataset)
    run = store.save(dataset, result)
    assert store.replay(run)["identical"]
    assert verify_bundle(bundle_bytes(store, run))["id"] == run


def test_full_golden_results_include_trace_and_uncertainty(tmp_path):
    store = Store(tmp_path / "golden.db")
    for name, project in [
        ("demo", "fixtures/project.json"),
        ("second-client", "fixtures/second-client/project.json"),
    ]:
        dataset, _ = load_project(ROOT / project, store)
        expected = (ROOT / "tests/golden" / (name + ".json")).read_text(encoding="utf-8").strip()
        assert canonical(audit(dataset)) == expected
