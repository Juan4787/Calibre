"""Run from /tmp with PYTHONPATH pointing at an installed wheel, not the source tree."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

import freight_audit
from freight_audit.reporting import verify_bundle
from freight_audit.server import create_app

parser = argparse.ArgumentParser()
parser.add_argument("--installed-root", type=Path, required=True)
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
print("Installed wheel: static UI, generated fixtures, audit, persistence, replay and export passed.")
