"""Bounded real-browser 36k operations/one charge check; all data fictional."""

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from freight_audit.fixtures import agreement, column, const, constant, rule, version  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--runtime-python", type=Path, required=True)
parser.add_argument("--wheel", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=False)
# Preserve the venv path, not the system interpreter symlink target.
RUNTIME = args.runtime_python.absolute()
WHEEL_SHA = hashlib.sha256(args.wheel.read_bytes()).hexdigest()
installation = RUNTIME.parent.parent / "installation.json"
if installation.exists():
    assert json.loads(installation.read_text())["wheel_sha256"] == WHEEL_SHA

operations = (
    "id;ref;weight;date\n" + "".join(f"S{i};{i:05};10;01/05/2026\n" for i in range(1, 36001))
).encode()
charges = b"id;settlement;reference;carrier;agreement;concept;amount;currency\nC1;L1;00001;C;A;base;100;ARS\n"
mappings = {
    "shipments": {
        "id": "volume-ui-operations",
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
        "id": "volume-ui-charges",
        "version": "1",
        "entity": "charges",
        "columns": [
            column(f, f, "decimal" if f == "amount" else "text")
            for f in (
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
    "source_hashes": [hashlib.sha256(operations).hexdigest(), hashlib.sha256(charges).hexdigest()],
    "shipments_by_source": {hashlib.sha256(operations).hexdigest(): 36000},
    "charges_by_source": {hashlib.sha256(charges).hexdigest(): 1},
    "charge_totals_by_source": {hashlib.sha256(charges).hexdigest(): {"ARS": "100"}},
    "shipment_count": 36000,
    "charge_count": 1,
    "actual_by_currency": {"ARS": "100"},
}
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
telemetry = {"server_peak_rss_mib": 0, "minimum_host_available_mib": 999999, "aborted": False}
done = threading.Event()
requests = []
errors = []


def mem_available():
    return next(
        int(line.split()[1]) / 1024
        for line in Path("/proc/meminfo").read_text().splitlines()
        if line.startswith("MemAvailable:")
    )


assert mem_available() > 1400, "Insufficient available host memory for bounded browser volume check"
with tempfile.TemporaryDirectory(prefix="calibre-ui-volume-") as work:
    product = Path(
        subprocess.check_output(
            [str(RUNTIME), "-c", "import freight_audit; print(freight_audit.__file__)"],
            cwd=work,
            env=env,
            text=True,
        ).strip()
    )
    assert not product.is_relative_to(ROOT), "Backend must use an installed distribution outside the checkout"
    for source in (ROOT / "src/freight_audit").rglob("*"):
        if source.is_file() and "__pycache__" not in source.parts:
            assert (
                source.read_bytes()
                == (product.parent / source.relative_to(ROOT / "src/freight_audit")).read_bytes()
            ), source
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    with (OUT / "server.log").open("w") as log:
        server = subprocess.Popen(
            [
                str(RUNTIME),
                "-m",
                "freight_audit.cli",
                "--db",
                str(Path(work) / "audit.db"),
                "serve",
                "--port",
                str(port),
            ],
            cwd=work,
            env=env,
            stdout=log,
            stderr=log,
        )

        def watchdog():
            while not done.wait(0.25):
                available = mem_available()
                telemetry["minimum_host_available_mib"] = min(
                    telemetry["minimum_host_available_mib"], available
                )
                try:
                    rss = next(
                        int(line.split()[1]) / 1024
                        for line in Path(f"/proc/{server.pid}/status").read_text().splitlines()
                        if line.startswith("VmHWM:")
                    )
                    telemetry["server_peak_rss_mib"] = max(telemetry["server_peak_rss_mib"], rss)
                except (FileNotFoundError, StopIteration):
                    return
                if available < 300 or rss > 1100:
                    telemetry["aborted"] = True
                    server.terminate()
                    return

        monitor = threading.Thread(target=watchdog, daemon=True)
        monitor.start()
        started = time.perf_counter()
        try:
            with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=90) as client:
                for _ in range(100):
                    try:
                        token = client.get("/api/session").json()["token"]
                        break
                    except httpx.ConnectError:
                        assert server.poll() is None
                        time.sleep(0.1)
                else:
                    raise AssertionError("Server did not start")
                client.headers["X-Freight-Local"] = token
                with sync_playwright() as pw:
                    browser = pw.chromium.launch()
                    page = browser.new_page(viewport={"width": 1280, "height": 720})
                    page.set_default_timeout(90000)
                    page.on("pageerror", lambda error: errors.append(str(error)))

                    def capture(request):
                        if request.method == "POST" and "/api/audit" in request.url:
                            body = request.post_data_json
                            assert "records" not in json.dumps(body)
                            requests.append(
                                {
                                    "path": request.url.split(str(port))[-1],
                                    "bytes": len(request.post_data_buffer or b""),
                                    "import_roles": sorted(body["imports"]),
                                }
                            )

                    page.on("request", capture)
                    page.goto(f"http://127.0.0.1:{port}")
                    expect(page.locator("#new-run")).to_be_visible()
                    page.locator('[data-view="new"]').click()
                    for role, data in [("shipments", operations), ("charges", charges)]:
                        page.locator("#file-" + role).set_input_files(
                            {"name": role + ".csv", "mimeType": "text/csv", "buffer": data}
                        )
                        page.locator("#mapping-file-" + role).set_input_files(
                            {
                                "name": "mapping-" + role + ".json",
                                "mimeType": "application/json",
                                "buffer": json.dumps(mappings[role]).encode(),
                            }
                        )
                        expect(page.locator("#mapping-" + role)).not_to_have_value("")
                        page.locator("#validate-" + role).click()
                        expect(page.locator("#result-" + role)).to_contain_text(
                            f"{36000 if role == 'shipments' else 1} filas aceptadas · 0 rechazadas",
                            timeout=90000,
                        )
                    print("Browser imported 36000 operations and one charge", flush=True)
                    page.locator("#audit-label").fill("Volumen ficticio: 36000 operaciones, un cargo")
                    page.locator("#goto-step-2").click()
                    page.locator("#agreement-file").set_input_files(
                        {
                            "name": "agreements.json",
                            "mimeType": "application/json",
                            "buffer": json.dumps(
                                [
                                    agreement(
                                        "A", "C", [version("V1", [rule("R1", "base", const("100", "ARS"))])]
                                    )
                                ]
                            ).encode(),
                        }
                    )
                    page.locator("#goto-step-3").click()
                    expect(page.locator("#step-panel-3")).to_be_visible()
                    page.locator("#external-control").set_input_files(
                        {
                            "name": "control-ficticio.json",
                            "mimeType": "application/json",
                            "buffer": json.dumps(control).encode(),
                        }
                    )
                    expect(page.locator("#matching-check-step3")).to_contain_text(
                        "Control documental cotejado", timeout=90000
                    )
                    page.locator("#goto-step-4").click()
                    page.locator("#execute").click()
                    expect(page.locator("#findings tr[data-finding-id]")).to_have_count(1, timeout=90000)
                    saved = client.get("/api/runs").json()[0]
                    assert (
                        saved["summary"]["currencies"]["ARS"]["actual"] == "100"
                        and saved["summary"]["currencies"]["ARS"]["confirmed_net_difference"] == "0"
                    )
                    page.screenshot(path=str(OUT / "volume-results.png"))
                    page.locator("#replay").click()
                    expect(page.locator("#notice")).to_contain_text("Reproducción idéntica", timeout=90000)
                    print("Browser executed audit, exact totals and replay", flush=True)
                    for fmt in ["canonical", "html", "zip"]:
                        with page.expect_download(timeout=240000) as downloading:
                            page.locator(f'a[href$="/export/{fmt}"]').click()
                        downloading.value.save_as(
                            OUT / ("audit." + {"canonical": "json", "html": "html", "zip": "zip"}[fmt])
                        )
                        print("Downloaded " + fmt, flush=True)
                    browser.close()
            assert not errors and not telemetry["aborted"]
        finally:
            server.terminate()
            server.wait(timeout=20)
            done.set()
            monitor.join(timeout=2)
    # Browser/backend are closed before the authoritative archive is materialized.
    checked = subprocess.run(
        [str(RUNTIME), "-m", "freight_audit.cli", "verify-bundle", str(OUT / "audit.zip"), "--replay"],
        cwd=work,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(checked.stdout)["identical"]
    with zipfile.ZipFile(OUT / "audit.zip") as archive:
        assert archive.read("audit.json") == (OUT / "audit.json").read_bytes()
        run = json.loads(archive.read("audit.json"))
        assert len(run["snapshot"]["shipments"]) == 36000 and len(run["snapshot"]["charges"]) == 1
        assert (
            run["metadata"]["provenance"]["checked_records"] == 36001
            and run["metadata"]["document_control"]["status"] == "matched"
        )
        assert run["result"]["findings"][0]["expected"] == "100"
        spreadsheet = "auditoria.xlsx" in archive.namelist()
        warning = archive.read("ADVERTENCIA_EXPORTACION.txt").decode() if not spreadsheet else None
    assert all(r["bytes"] < 10000 for r in requests) and requests
    receipt = {
        "passed": True,
        "scope": "Real Chromium and installed wheel, fictional 36000 operations/one priced charge; not 36000 priced charges or a real client",
        "operations": 36000,
        "charges": 1,
        "checked_records": 36001,
        "actual": "100",
        "expected": "100",
        "confirmed_net_difference": "0",
        "document_control": "matched",
        "ui_requests": requests,
        "canonical_bytes": (OUT / "audit.json").stat().st_size,
        "canonical_identical_to_bundle": True,
        "complete_json_and_originals_verified": True,
        "installed_cli_bundle_replay_identical": True,
        "xlsx_in_bundle": spreadsheet,
        "xlsx_warning": warning,
        "console_page_errors": errors,
        "telemetry": telemetry,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "engine_artifact_hash": run["artifact_hash"],
        "wheel_sha256": WHEEL_SHA,
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
