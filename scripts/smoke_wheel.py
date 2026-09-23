"""Run from /tmp with PYTHONPATH pointing at an installed wheel, not the source tree."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

import freight_audit
from freight_audit.canonical import load_json
from freight_audit.importing import ImportMapping, import_data
from freight_audit.reporting import verify_bundle
from freight_audit.server import create_app

parser = argparse.ArgumentParser()
parser.add_argument("--installed-root", type=Path, required=True)
parser.add_argument("--fixtures-root", type=Path)
args = parser.parse_args()
assert Path(freight_audit.__file__).resolve().is_relative_to(args.installed_root.resolve())
with TemporaryDirectory() as directory:
    with TestClient(create_app(Path(directory) / "installed.db")) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert client.get("/static/app.js").status_code == 200
        assert client.get("/static/favicon.svg").status_code == 200
        client.headers["X-Freight-Local"] = client.get("/api/session").json()["token"]
        response = client.post("/api/demo")
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["summary"]["counts"] == {"PASS": 34, "FAIL": 2, "REVIEW": 6, "UNDETERMINABLE": 4}
        run_id = result["run_id"]
        assert client.post(f"/api/runs/{run_id}/replay").json()["identical"]
        export = client.get(f"/api/runs/{run_id}/export/zip")
        assert export.status_code == 200
        assert verify_bundle(export.content)["id"] == run_id
if args.fixtures_root:
    mapping = ImportMapping.model_validate(
        load_json((args.fixtures_root / "mapping-charges.json").read_bytes())
    )
    original = (args.fixtures_root / "liquidacion.csv").read_bytes()
    lf = original.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    left = import_data(lf, "liquidacion.csv", mapping)
    right = import_data(crlf, "liquidacion.csv", mapping)

    def without_provenance(records):
        return [{key: value for key, value in record.items() if key != "provenance"} for record in records]

    assert left["accepted"] == right["accepted"] == 46
    assert without_provenance(left["records"]) == without_provenance(right["records"])
    assert left["document"] != right["document"]
print("Installed wheel: static UI, generated fixtures, audit, persistence, replay and export passed.")
