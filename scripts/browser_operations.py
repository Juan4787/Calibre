"""Operational browser regression with fictional inputs and hand-written totals."""

import hashlib
import json


def exercise_operations(page, client, destination, root):
    from playwright.sync_api import expect

    source = root / "fixtures/second-client"
    page.locator('[data-view="workspace"]').click()
    page.locator("#workspace-name").fill("Cliente ficticio Operaciones")
    page.locator("#workspace-create button").click()
    expect(page.locator("#workspace-select option:checked")).to_have_text("Cliente ficticio Operaciones")
    first_workspace = page.locator("#workspace-select").input_value()
    page.locator('[data-view="new"]').click()
    expect(page.locator("#choose-file-shipments")).to_be_visible()
    page.locator("#choose-file-shipments").focus()
    with page.expect_file_chooser() as choosing:
        page.keyboard.press("Enter")
    choosing.value.set_files(source / "movements.csv")
    for role, filename in (("shipments", "movements.csv"), ("charges", "invoice.xlsx")):
        if role == "charges":
            page.locator(f"#file-{role}").set_input_files(source / filename)
        page.locator(f"#mapping-file-{role}").set_input_files(source / f"mapping-{role}.json")
        expect(page.locator(f"#mapping-{role}")).not_to_have_value("")
        page.locator(f"#validate-{role}").click()
        expect(page.locator(f"#result-{role}")).to_contain_text("0 rechazadas")
        expect(page.locator(f"#result-{role}")).to_contain_text("Transformaciones y valores interpretados")
    page.locator("#audit-label").fill("Período ficticio con control independiente")
    page.locator("#goto-step-2").click()
    page.locator("#agreement-file").set_input_files(source / "agreements.json")
    expect(page.locator("#contract-target option")).to_have_count(2)
    page.locator("#contract-target").locator("..").locator("summary").click()
    page.locator("#contract-target").select_option(index=1)
    contract = b"Synthetic QA contract reference. Not a real contract."
    page.locator("#contract-file").set_input_files(
        {"name": "contrato-ficticio.txt", "mimeType": "text/plain", "buffer": contract}
    )
    page.locator("#contract-page").fill("1")
    page.locator("#contract-actor").fill("Responsable ficticio de QA")
    page.locator("#contract-date").fill("2026-10-29")
    page.locator("#add-contract").click()
    expect(page.locator("#contract-status")).to_contain_text("1 respaldo(s) conservado(s)")
    page.locator("#goto-step-3").click()
    expect(page.locator("#matching-check-step3")).to_contain_text("Control documental pendiente")
    shipments_hash = hashlib.sha256((source / "movements.csv").read_bytes()).hexdigest()
    charges_hash = hashlib.sha256((source / "invoice.xlsx").read_bytes()).hexdigest()
    control = {
        "schema": "freight-audit-external-control/v1",
        "source_hashes": [shipments_hash, charges_hash, hashlib.sha256(contract).hexdigest()],
        "shipments_by_source": {shipments_hash: 6},
        "charges_by_source": {charges_hash: 2},
        "charge_totals_by_source": {charges_hash: {"USD": "398.5"}},
        "shipment_count": 6,
        "charge_count": 3,
        "actual_by_currency": {"USD": "398.5"},
    }

    def upload_control():
        page.locator("#external-control").set_input_files(
            {
                "name": "control-independiente-ficticio.json",
                "mimeType": "application/json",
                "buffer": json.dumps(control).encode(),
            }
        )

    upload_control()
    expect(page.locator("#notice")).to_contain_text("El control documental no coincide")
    page.locator("#goto-step-4").click()
    expect(page.locator("#step-panel-4")).not_to_be_visible()
    control["charge_count"] = 2
    upload_control()
    expect(page.locator("#matching-check-step3")).to_contain_text("Control documental cotejado")
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator("#external-control-status").scroll_into_view_if_needed()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=str(destination / "operations-control-mobile.png"))
    page.set_viewport_size({"width": 1280, "height": 720})
    page.locator("#goto-step-4").click()
    page.locator("#execute").click()
    expect(page.locator("#findings tr[data-finding-id]")).to_have_count(2)
    expect(page.locator(".banner.info")).to_contain_text("Control documental cotejado")
    original = client.get("/api/runs", params={"workspace": first_workspace}).json()[0]
    saved = client.get("/api/runs/" + original["id"], params={"workspace": first_workspace}).json()
    assert saved["metadata"]["document_control"]["status"] == "matched"
    assert saved["result"]["summary"]["currencies"]["USD"]["actual"] == "398.5"
    page.locator("summary", has_text="1 respaldo(s) contractual(es)").click()
    with page.expect_download() as downloading:
        page.get_by_role("link", name="contrato-ficticio.txt").click()
    assert downloading.value.suggested_filename == "contrato-ficticio.txt"
    contract_path = destination / "contract-readback.txt"
    downloading.value.save_as(contract_path)
    assert contract_path.read_bytes() == contract
    page.screenshot(path=str(destination / "operations-audit.png"), full_page=True)

    page.locator("#new-correction").click()
    expect(page.locator("#revision-note")).to_be_visible()
    page.locator("#revision-note").fill("Corrección sintética para cotejar relaciones históricas")
    page.locator("#audit-label").fill("Corrección ficticia relacionada")
    for role, filename in (("shipments", "movements.csv"), ("charges", "invoice.xlsx")):
        page.locator(f"#file-{role}").set_input_files(source / filename)
        page.locator(f"#mapping-file-{role}").set_input_files(source / f"mapping-{role}.json")
        expect(page.locator(f"#mapping-{role}")).not_to_have_value("")
        page.locator(f"#validate-{role}").click()
        expect(page.locator(f"#result-{role}")).to_contain_text("0 rechazadas")
    page.locator("#goto-step-2").click()
    page.locator("#agreement-file").set_input_files(source / "agreements.json")
    expect(page.locator("#agreements")).not_to_have_value("[]")
    page.locator("#goto-step-3").click()
    page.locator("#goto-step-4").click()
    page.locator("#execute").click()
    expect(page.locator("[data-related-run]")).to_contain_text("Ver auditoría anterior")
    page.locator("#compare-revision").click()
    expect(page.locator("#revision-comparison")).to_contain_text("Comparación con la corrida anterior")
    page.locator("[data-related-run]").click()
    expect(page.locator("h1")).to_have_text(saved["snapshot"]["label"])
    expect(page.locator("[data-related-run]")).to_contain_text("Corrección ficticia relacionada")
    page.locator('[data-view="workspace"]').click()
    with page.expect_download() as downloading:
        page.get_by_role("link", name="Descargar respaldo verificado").click()
    backup_path = destination / "operations-backup.db"
    downloading.value.save_as(backup_path)
    page.locator("#workspace-name").fill("Otro cliente ficticio vacío")
    page.locator("#workspace-create button").click()
    expect(page.locator("#workspace-select option:checked")).to_have_text("Otro cliente ficticio vacío")
    expect(page.locator("[data-run]")).to_have_count(0)
    page.locator('[data-view="workspace"]').click()
    page.locator("#restore-name").fill("Copia recuperada ficticia")
    page.locator("#restore-file").set_input_files(backup_path)
    page.locator("#workspace-restore button").click()
    expect(page.locator("#workspace-select option:checked")).to_have_text("Copia recuperada ficticia")
    restored_workspace = page.locator("#workspace-select").input_value()
    assert restored_workspace != first_workspace
    page.locator(f'[data-run="{original["id"]}"]').click()
    page.locator("#replay").click()
    expect(page.locator("#notice")).to_contain_text("Reproducción idéntica")
    restored = client.get("/api/runs/" + original["id"], params={"workspace": restored_workspace}).json()
    assert restored["snapshot"] == saved["snapshot"] and restored["result_hash"] == saved["result_hash"]
    assert (
        client.get("/api/runs/" + original["id"], params={"workspace": first_workspace}).json()["snapshot"]
        == saved["snapshot"]
    )
    page.locator("#workspace-select").select_option("main")
    expect(page.locator("#workspace-select option:checked")).to_have_text("Sin cliente asignado")
    expect(page.locator("#runs-items")).to_be_visible()
    # Keep the temporary SQLite copy outside the published evidence inventory.
    backup_path.unlink()
    disconnected = page.context.new_page()
    runtime_errors = []
    disconnected.on("pageerror", lambda error: runtime_errors.append(str(error)))
    try:
        disconnected.goto(page.url)
        expect(disconnected.locator("#new-run")).to_be_visible()
        disconnected.route("**/api/runs", lambda route: route.abort("connectionfailed"))
        disconnected.locator('[data-view="audits"]').click()
        expect(disconnected.locator("#retry-runs")).to_be_visible()
        expect(disconnected.locator("#runs")).to_contain_text("No se pudo conectar con Calibre")
        disconnected.screenshot(path=str(destination / "operations-connection-recovery.png"))
        disconnected.unroute("**/api/runs")
        disconnected.locator("#retry-runs").click()
        expect(disconnected.locator("#retry-runs")).to_have_count(0)
        expect(disconnected.locator("#runs-items")).to_be_visible()
        assert not runtime_errors, runtime_errors
    finally:
        disconnected.close()
    return {
        "keyboard_file_chooser": True,
        "conversion_preview": True,
        "document_control_positive_and_negative": True,
        "contract_original_download_identical": True,
        "immutable_revision_links": True,
        "workspace_isolation": True,
        "backup_restore_replay": True,
        "network_failure_recovery": True,
        "scope": "Fictional client only; independent totals 194.25 + 204.25 = 398.5 USD",
    }


def exercise_large_agreement_preview(page, client, destination, root):
    """Large contractual table: bounded visible preview, full retained configuration."""
    from playwright.sync_api import expect

    agreement = json.loads((root / "fixtures/second-client/agreements.json").read_text())[0]
    agreement["name"] = "Tabla grande ficticia de QA"
    agreement["versions"][0]["tables"]["tabla_grande_qa"] = {
        "kind": "lookup",
        "rows": [
            {"keys": [f"QA-{i:06}"], "value": {"type": "decimal", "value": "1", "unit": "USD"}}
            for i in range(20000)
        ],
    }
    response = client.post("/api/configs/agreement", json=agreement)
    assert response.status_code == 200, response.text
    identifier = response.json()["hash"]
    page.locator('[data-view="configs"]').click()
    card = page.locator(".run-card-rich").filter(has=page.locator(f'[data-view-config="{identifier}"]'))
    expect(card).to_be_visible()
    card.locator("summary").click()
    expect(card).to_contain_text("primeras 20 de 20000 filas")
    expect(card).to_contain_text("QA-000019")
    expect(card).not_to_contain_text("QA-019999")
    assert len(card.inner_text()) < 10000
    page.screenshot(path=str(destination / "agreement-table-desktop.png"))
    page.set_viewport_size({"width": 390, "height": 844})
    card.scroll_into_view_if_needed()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=str(destination / "agreement-table-mobile.png"))
    card.locator(f'[data-view-config="{identifier}"]').click()
    stored = json.loads(page.locator("#config-data").input_value())
    assert len(stored["versions"][0]["tables"]["tabla_grande_qa"]["rows"]) == 20000
    assert stored["versions"][0]["tables"]["tabla_grande_qa"]["rows"][-1]["keys"] == ["QA-019999"]
    page.set_viewport_size({"width": 1280, "height": 720})
    return {
        "configured_rows": 20000,
        "visible_preview_rows": 20,
        "full_editor_unchanged": True,
        "viewports": [1280, 390],
    }
