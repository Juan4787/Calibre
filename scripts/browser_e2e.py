#!/usr/bin/env python3
"""Current UI regression gate: real Chromium, fresh DB, exact cells, actual navigation."""

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import zipfile
from copy import deepcopy
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qa.reconcile import LABELS, display_money, reconcile  # noqa: E402


def observe(page, run):
    """Read all pages from the actual DOM; do not synthesize observations from API data."""
    from playwright.sync_api import expect

    page.locator("#filter-status").select_option("")
    page.locator("#search").fill("")
    observations = {}
    while True:
        for row in page.locator("#findings tr[data-finding-id]").all():
            identifier = row.get_attribute("data-finding-id")
            assert identifier not in observations, "Duplicate row across pagination"
            observations[identifier] = [cell.inner_text().strip() for cell in row.locator("td").all()]
        if page.locator("#next").is_disabled():
            break
        page.locator("#next").click()
    assert set(observations) == {f["id"] for f in run["result"]["findings"]}
    for finding in run["result"]["findings"]:
        cells = observations[finding["id"]]
        assert cells[1] == LABELS[finding["status"]]
        assert cells[2] == finding["currency"] + " " + display_money(finding["actual"])
        empty = "Requiere revisión" if finding["status"] == "REVIEW" else "No determinable"
        assert cells[3] == (empty if finding["expected"] is None else display_money(finding["expected"]))
        difference = empty if finding["difference"] is None else display_money(finding["difference"])
        if finding["status"] == "REVIEW":
            difference += "\nRequiere revisión"
        assert cells[4] == difference
    while not page.locator("#prev").is_disabled():
        page.locator("#prev").click()
    expect(page.locator("#findings tr[data-finding-id]").first).to_be_visible()
    return observations


def exercise(page, client, destination):
    from playwright.sync_api import expect

    page.goto(str(client.base_url))
    page.locator("#demo").click()
    expect(page.locator("#findings tr[data-finding-id]").first).to_be_visible()
    runs = client.get("/api/runs").json()
    assert len(runs) == 1
    run = client.get("/api/runs/" + runs[0]["id"]).json()
    original_hash = run["result_hash"]
    original_findings = run["result"]["findings"]
    observations = observe(page, run)
    # Independent handwritten anchors, in addition to channel consistency.
    by_charge = {cid: f for f in run["result"]["findings"] for cid in f["charge_ids"]}
    assert (by_charge["C-002"]["status"], by_charge["C-002"]["difference"]) == ("FAIL", "50")
    assert (by_charge["C-004"]["status"], by_charge["C-004"]["confirmed_difference"]) == ("REVIEW", "0")

    unknown = next(f for f in run["result"]["findings"] if f["version"] is None)
    page.locator("#filter-status").select_option("UNDETERMINABLE")
    page.locator(f'[data-finding="{unknown["id"]}"]').click()
    expect(page.locator("#detail-content")).to_contain_text("Sin versión aplicable")
    expect(page.locator("#detail-content")).to_contain_text("No se puede determinar la diferencia")
    expect(page.locator("#detail-content")).not_to_contain_text("R-BASE")
    expect(page.locator("#detail-content")).not_to_contain_text("Sin desviación")
    page.locator("#close-detail").click()

    page.locator("#filter-status").select_option("FAIL")
    target = by_charge["C-002"]
    page.locator(f'[data-finding="{target["id"]}"]').click()
    for action, text in (("APPROVED", "Confirmado"), ("REJECTED", "Rechazado")):
        page.locator("#actor").fill("QA sintética")
        page.locator("#action").select_option(action)
        page.locator("#decision-note").fill("Prueba de historial conservado " + action)
        page.locator('#decision-form button[type="submit"]').click()
        expect(page.locator(".history").last).to_contain_text(text)
    page.locator("#close-detail").click()
    expect(page.locator(f'tr[data-finding-id="{target["id"]}"] td').nth(5)).to_have_text("Rechazado")
    run = client.get("/api/runs/" + run["id"]).json()
    assert run["result_hash"] == original_hash and len(run["decisions"]) == 2
    assert run["result"]["findings"] == original_findings
    page.locator("#replay").click()
    expect(page.locator("#notice")).to_contain_text("Reproducción idéntica")
    with page.expect_download() as downloading:
        page.get_by_text("Exportar JSON canónico", exact=True).click()
    download = downloading.value
    download.save_as(destination / "ui-export.json")
    assert json.loads((destination / "ui-export.json").read_text()) == run

    exported = client.get(f"/api/runs/{run['id']}/export/zip")
    exported.raise_for_status()
    bundle_path = destination / "audit.zip"
    bundle_path.write_bytes(exported.content)
    bundle_dir = destination / "export"
    with zipfile.ZipFile(bundle_path) as bundle:
        bundle.extractall(bundle_dir)  # Our fresh local server is the producer, not untrusted input.
    reconciled = reconcile(bundle_dir, api_run=run)
    assert not reconciled["errors"], reconciled
    reconciled["channels"]["ui"] = "46 actual DOM rows; all pages; exact cells and statuses"

    # Evidence from the actual form must create a new audit while preserving the original.
    page.locator("#filter-status").select_option("REVIEW")
    review = by_charge["C-004"]
    page.locator(f'[data-finding="{review["id"]}"]').click()
    page.locator("#evidence-panel summary").click()
    page.locator("#ev-kind").fill("authorization")
    page.locator("#ev-note").fill("Autorización ficticia para regresión")
    page.locator('#evidence-form button[type="submit"]').click()
    expect(page.locator("#detail")).not_to_be_visible()
    updated = next(r for r in client.get("/api/runs").json() if "evidencia adicional" in r["label"])
    resolved = client.get("/api/runs/" + updated["id"]).json()
    resolved_finding = next(f for f in resolved["result"]["findings"] if "C-004" in f["charge_ids"])
    assert resolved_finding["status"] == "PASS"
    assert client.get("/api/runs/" + run["id"]).json()["result"]["findings"] == original_findings

    # New wizard, including a response arriving after its file has changed.
    page.locator('[data-view="new"]').click()
    expect(page.locator("#file-shipments")).to_be_attached()
    page.locator("#step-nav-4").click()
    expect(page.locator("#step-panel-1")).to_be_visible()
    for role, filename in (("shipments", "operaciones.xlsx"), ("charges", "liquidacion.csv")):
        page.locator(f"#file-{role}").set_input_files(ROOT / "fixtures" / filename)
        page.locator(f"#mapping-file-{role}").set_input_files(ROOT / "fixtures" / f"mapping-{role}.json")
        expect(page.locator(f"#mapping-{role}")).to_have_value(
            (ROOT / "fixtures" / f"mapping-{role}.json").read_text()
        )
        if role == "shipments":
            held = []

            def hold(route, _request, held=held):
                held.append((route, route.fetch()))

            page.route("**/api/import", hold)
            page.locator(f"#validate-{role}").click()
            for _ in range(100):
                if held:
                    break
                page.wait_for_timeout(20)
            assert held, "Import request did not reach server"
            page.locator(f"#file-{role}").set_input_files(
                {
                    "name": "operaciones-cambiadas.xlsx",
                    "mimeType": "application/octet-stream",
                    "buffer": (ROOT / "fixtures" / filename).read_bytes(),
                }
            )
            held[0][0].fulfill(response=held[0][1])
            expect(page.locator(f"#validate-{role}")).to_be_enabled()
            expect(page.locator(f"#result-{role}")).to_have_text(
                "Validar para ver filas aceptadas, rechazos y origen de los datos."
            )
            page.unroute("**/api/import", hold)
        page.locator(f"#validate-{role}").click()
        expect(page.locator(f"#result-{role}")).to_contain_text("filas aceptadas")
    page.locator("#audit-label").fill("QA interfaz actual")
    page.locator("#goto-step-2").click()
    page.locator("#agreement-file").set_input_files(ROOT / "fixtures/agreements.json")
    expect(page.locator("#agreements")).not_to_have_value("[]")
    page.locator("#goto-step-3").click()
    page.locator("#goto-step-4").click()
    page.locator("#execute").click()
    expect(page.locator("#findings tr[data-finding-id]").first).to_be_visible()
    created = next(r for r in client.get("/api/runs").json() if r["label"] == "QA interfaz actual")
    imported = client.get("/api/runs/" + created["id"]).json()
    assert "operaciones-cambiadas.xlsx" in imported["snapshot"]["documents"].values()
    observe(page, imported)
    page.screenshot(path=str(destination / "current-ui.png"), full_page=True)
    page.reload()
    page.locator(f'[data-run="{run["id"]}"]').click()
    expect(page.locator("#findings tr[data-finding-id]").first).to_be_visible()
    observe(page, run)
    # Numeric boundary values have handwritten expectations; no float conversion in the oracle.
    snapshot = deepcopy(run["snapshot"])
    base_shipment = next(s for s in snapshot["shipments"] if s["reference"] == "00001")
    base_charge = next(c for c in snapshot["charges"] if c["id"] == "C-001")
    agreement = next(a for a in snapshot["agreements"] if a["id"] == "A")
    agreement["matching"]["duplicate_fields"] = []
    agreement["detect_missing"] = False
    agreement["versions"] = [agreement["versions"][0]]
    rule = deepcopy(agreement["versions"][0]["rules"][0])
    rule.update(
        expression={"op": "const", "value": {"type": "decimal", "value": "100", "unit": "ARS"}}, evidence=[]
    )
    agreement["versions"][0]["rules"] = [rule]
    snapshot.update(
        label="QA decimales extremos",
        shipments=[],
        charges=[],
        agreements=[agreement],
        evidence=[],
        coverage={},
    )
    numbers = {"BIG": "999999999999999999999999999999999999", "NEG": "-75.12", "ZERO": "0", "TOL": "100.01"}
    for identifier, amount in numbers.items():
        shipment = deepcopy(base_shipment)
        shipment.update(id=identifier, reference=identifier, provenance={})
        snapshot["shipments"].append(shipment)
        charge = deepcopy(base_charge)
        charge.update(id=identifier, reference=identifier, amount=amount, provenance={})
        snapshot["charges"].append(charge)
        if identifier == "BIG":
            snapshot["charges"].append({**charge, "id": "BIG2"})
    response = client.post("/api/audit", json=snapshot)
    response.raise_for_status()
    numeric_id = response.json()["run_id"]
    page.locator("#back").click()
    page.locator(f'[data-run="{numeric_id}"]').click()
    expect(page.locator("#findings tr[data-finding-id]").first).to_be_visible()
    numeric_run = client.get("/api/runs/" + numeric_id).json()
    numeric_findings = {f["shipment_ids"][0]: f for f in numeric_run["result"]["findings"]}
    assert numeric_findings["BIG"]["actual"] == str(2 * int(numbers["BIG"]))
    assert numeric_findings["NEG"]["difference"] == "-175.12"
    assert numeric_findings["ZERO"]["difference"] == "-100"
    assert numeric_findings["TOL"]["status"] == "PASS"
    observe(page, numeric_run)

    # A slow response for an old run must not replace the new-audit form.
    page.locator("#back").click()
    held_run = []

    def hold_run(route):
        held_run.append((route, route.fetch()))

    page.route(f"**/api/runs/{run['id']}", hold_run)
    page.locator(f'[data-run="{run["id"]}"]').click()
    for _ in range(100):
        if held_run:
            break
        page.wait_for_timeout(20)
    assert held_run
    page.locator('[data-view="new"]').click()
    expect(page.locator("#audit-label")).to_be_visible()
    held_run[0][0].fulfill(response=held_run[0][1])
    page.wait_for_timeout(100)
    expect(page.locator("#audit-label")).to_be_visible()
    expect(page.locator("#findings")).to_have_count(0)
    (destination / "observed-ui.json").write_text(json.dumps(observations, ensure_ascii=False, indent=2))
    return {
        "run_id": run["id"],
        "result_hash": original_hash,
        "rows_observed": len(observations),
        "channels": reconciled["channels"],
    }


def main():
    from playwright.sync_api import sync_playwright

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/playwright/rigor")
    parser.add_argument("--installed-root", type=Path)
    args = parser.parse_args()
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if (args.output_dir / "server.log").exists():
        parser.error("Output directory already used; preserve evidence and choose a new directory")
    errors = []
    with tempfile.TemporaryDirectory(prefix="calibre-browser-") as td:
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        if not args.installed_root:
            env["PYTHONPATH"] = str(ROOT / "src")
        probe = subprocess.check_output(
            [sys.executable, "-c", "import freight_audit; print(freight_audit.__file__)"],
            cwd=td,
            env=env,
            text=True,
        ).strip()
        if args.installed_root:
            assert Path(probe).resolve().is_relative_to(args.installed_root.resolve()), probe
        script_hash = hashlib.sha256((Path(probe).parent / "static/app.js").read_bytes()).hexdigest()
        assert (
            script_hash == hashlib.sha256((ROOT / "src/freight_audit/static/app.js").read_bytes()).hexdigest()
        ), "Stale UI artifact"
        for path in (ROOT / "src/freight_audit").rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                installed = Path(probe).parent / path.relative_to(ROOT / "src/freight_audit")
                assert installed.read_bytes() == path.read_bytes(), f"Stale product file: {path.name}"
        with (args.output_dir / "server.log").open("w") as log:
            server = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "freight_audit.cli",
                    "--db",
                    str(Path(td) / "audit.db"),
                    "serve",
                    "--port",
                    str(port),
                ],
                cwd=td,
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=30) as client:
                    for _ in range(100):
                        assert server.poll() is None, "Owned server exited; refusing to use another process"
                        try:
                            token = client.get("/api/session").json()["token"]
                            break
                        except httpx.ConnectError:
                            time.sleep(0.1)
                    else:
                        raise AssertionError("Server startup timed out")
                    client.headers["X-Freight-Local"] = token
                    assert client.get("/api/runs").json() == []
                    with sync_playwright() as pw:
                        browser = pw.chromium.launch()
                        context = browser.new_context()
                        context.tracing.start(screenshots=True, snapshots=True, sources=True)
                        page = context.new_page()
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        try:
                            result = exercise(page, client, args.output_dir)
                            assert not errors, errors
                            result.update(
                                product_path=probe,
                                ui_sha256=script_hash,
                                browser=browser.version,
                                passed=True,
                            )
                            (args.output_dir / "result.json").write_text(json.dumps(result, indent=2))
                            print(json.dumps(result, indent=2))
                        finally:
                            context.tracing.stop(path=str(args.output_dir / "trace.zip"))
                            browser.close()
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


if __name__ == "__main__":
    main()
