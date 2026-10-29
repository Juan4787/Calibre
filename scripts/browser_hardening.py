"""Adversarial browser journeys for association uncertainty and asynchronous file inputs."""

import json
from copy import deepcopy

from playwright.sync_api import expect


def upload(page, role, data, mapping):
    page.locator(f"#file-{role}").set_input_files(data)
    page.locator(f"#toggle-advanced-{role}").click()
    page.locator(f"#mapping-file-{role}").set_input_files(mapping)
    expect(page.locator(f"#format-title-{role}")).to_contain_text("Mapping manual:")
    page.locator(f"#validate-{role}").click()
    expect(page.locator(f"#result-{role}")).to_contain_text("filas aceptadas")


def exercise_uncertainty(page, client, destination, observe):
    from freight_audit.fixtures import agreement, const, rule, version
    from freight_audit.reporting import verify_bundle

    case = destination / "uncertainty"
    case.mkdir()
    (case / "shipments.csv").write_text(
        "id;reference;carrier;date\nS1;00001;C;2026-05-01\nS2;00002;C;2026-05-01\n"
    )
    (case / "charges.csv").write_text(
        "id;settlement;reference;carrier;agreement;concept;amount;currency\n"
        "C1;L;00001;C;A;base;-100;ARS\nC2;L;00001;C;A;base;150;ARS\n"
    )
    fields = {
        "shipments": ["id", "reference", "carrier", "date"],
        "charges": ["id", "settlement", "reference", "carrier", "agreement", "concept", "amount", "currency"],
    }
    for role, columns in fields.items():
        mapping = {
            "id": "hardening-" + role,
            "version": "1",
            "entity": role,
            "date_formats": ["%Y-%m-%d"],
            "columns": [
                {
                    "source": field,
                    "target": "attributes.service_date" if field == "date" else field,
                    "type": "date" if field == "date" else "decimal" if field == "amount" else "text",
                }
                for field in columns
            ],
        }
        (case / f"{role}.json").write_text(json.dumps(mapping))
    contract = agreement(
        "A", "C", [version("V", [rule("R", "base", const("100", "ARS"), expected=True)])], detect_missing=True
    )
    contract["matching"]["explicit"] = {"C1": ["S2", "MISSING"]}
    contract["matching"]["duplicate_fields"] = []
    (case / "invalid.json").write_text(json.dumps(contract))
    corrected = deepcopy(contract)
    corrected["matching"]["explicit"] = {"C1": ["S1"]}
    (case / "corrected.json").write_text(json.dumps(corrected))

    def prepare(config, label):
        page.locator('[data-view="new"]').click()
        expect(page.locator("#file-shipments")).to_be_attached()
        for role in fields:
            upload(page, role, case / f"{role}.csv", case / f"{role}.json")
        page.locator("#audit-label").fill(label)
        page.locator("#goto-step-2").click()
        page.locator("#agreement-file").set_input_files(case / config)
        expect(page.locator("#agreements")).to_have_value(
            json.dumps([json.loads((case / config).read_text())], indent=2, ensure_ascii=False)
        )
        expect(page.locator("#agreement-load-status")).to_contain_text("Revisá")
        page.locator("#toggle-agreements").click()
        page.locator("#coverage").fill('{"A":["S1","S2"]}')
        page.locator("#goto-step-3").click()
        expect(page.locator("#step-panel-3")).to_be_visible()

    prepare("invalid.json", "ONR revisión adversarial negativa")
    warning = page.locator("#matching-check-step3")
    expect(warning).to_contain_text("1 inválida(s)")
    expect(warning).to_contain_text("MISSING (no existe en el lote)")
    expect(warning).to_contain_text("S1")
    expect(warning).to_contain_text("S2")
    page.screenshot(path=str(case / "invalid-preflight.png"), full_page=True)
    page.locator("#goto-step-4").click()
    expect(page.locator("#step-panel-4")).to_be_visible()
    page.locator("#execute").click()
    expect(page.locator("#findings tr[data-finding-id]").first).to_be_visible()
    saved = next(
        r for r in client.get("/api/runs").json() if r["label"] == "ONR revisión adversarial negativa"
    )
    run = client.get("/api/runs/" + saved["id"]).json()
    findings = {cid: f for f in run["result"]["findings"] for cid in f["charge_ids"]}
    assert len(run["result"]["findings"]) == 2  # no false missing charges for either candidate
    assert (findings["C1"]["status"], findings["C1"]["actual"]) == ("UNDETERMINABLE", "-100")
    assert (
        findings["C2"]["status"],
        findings["C2"]["difference"],
        findings["C2"]["confirmed_difference"],
    ) == ("REVIEW", "50", "0")
    assert run["result"]["summary"]["currencies"]["ARS"]["confirmed_net_difference"] == "0"
    assert observe(page, run)
    page.locator(f'[data-finding="{findings["C1"]["id"]}"]').click()
    expect(page.locator("#detail-content")).to_contain_text("Pendiente por vinculación")
    expect(page.locator("#detail-content .matching-conflicts")).to_contain_text("MISSING")
    page.screenshot(path=str(case / "invalid-detail.png"), full_page=True)
    page.locator("#close-detail").click()
    page.locator(f'[data-finding="{findings["C2"]["id"]}"]').click()
    expect(page.locator("#detail-content")).to_contain_text("sin confirmar")
    expect(page.locator("#detail-content")).to_contain_text("C1")
    page.locator("#actor").fill("Auditor sintético")
    page.locator("#action").select_option("EXCEPTION_ACCEPTED")
    page.locator("#decision-note").fill("La decisión no resuelve el vínculo ni confirma la diferencia")
    page.locator('#decision-form button[type="submit"]').click()
    expect(page.locator(".history").last).to_contain_text("Excepción aceptada")
    page.locator("#close-detail").click()
    for fmt, filename in (("zip", "invalid.zip"), ("xlsx", "invalid.xlsx"), ("html", "invalid.html")):
        with page.expect_download() as download:
            page.locator(f'a[href$="/export/{fmt}"]').click()
        download.value.save_as(case / filename)
    verified = verify_bundle((case / "invalid.zip").read_bytes())
    assert verified["result"] == run["result"]
    assert client.post(f"/api/runs/{run['id']}/replay").json()["identical"]
    prepare("corrected.json", "ONR ajuste asignado correctamente")
    expect(page.locator("#matching-check-step3")).to_contain_text("no se encontraron incidencias")
    page.locator("#goto-step-4").click()
    expect(page.locator("#step-panel-4")).to_be_visible()
    page.locator("#execute").click()
    expect(page.locator("#findings tr[data-finding-id]").first).to_be_visible()
    fixed = next(
        r for r in client.get("/api/runs").json() if r["label"] == "ONR ajuste asignado correctamente"
    )
    fixed = client.get("/api/runs/" + fixed["id"]).json()
    assert fixed["result"]["summary"]["currencies"]["ARS"]["confirmed_net_difference"] == "-50"
    assert client.get("/api/runs/" + run["id"]).json()["result"] == run["result"]
    assert observe(page, fixed)
    page.screenshot(path=str(case / "corrected-result.png"), full_page=True)
    return {"invalid_net": "0", "corrected_net": "-50", "false_missing": 0, "history_preserved": True}


def exercise_loading_and_paging(page, client, destination, root):
    held = []

    def hold(route):
        held.append((route, route.fetch()))

    page.locator('[data-view="new"]').click()
    expect(page.locator("#file-shipments")).to_be_attached()
    page.locator("#file-shipments").set_input_files(root / "fixtures/operaciones.xlsx")
    page.route("**/api/configs", hold)
    page.locator('[data-view="new"]').click()
    expect(page.locator("#file-shipments")).to_have_count(0)
    expect(page.locator("#main")).to_contain_text("Preparando el asistente")
    for _ in range(100):
        if held:
            break
        page.wait_for_timeout(20)
    assert held
    held[0][0].fulfill(response=held[0][1])
    page.unroute("**/api/configs", hold)
    expect(page.locator("#file-shipments")).to_be_attached()
    page.route("**/api/configs", lambda r: r.fulfill(status=503, json={"error": "Reintentar carga local"}))
    page.locator('[data-view="new"]').click()
    expect(page.locator("#retry-new")).to_be_visible()
    page.unroute("**/api/configs")
    page.locator("#retry-new").click()
    expect(page.locator("#file-shipments")).to_be_attached()

    page.evaluate("""() => {
      const original = File.prototype.text;
      window.restoreFileRead = () => { File.prototype.text = original; };
      File.prototype.text = function() {
        const content = original.call(this);
        if (!this.name.startsWith('slow-')) return content;
        return new Promise((resolve, reject) => {
          window.releaseFileRead = () => content.then(resolve, reject);
          window.rejectFileRead = () => reject(new Error('simulated file read failure'));
        });
      };
    }""")
    try:
        manual = (root / "fixtures/mapping-invalid.json").read_bytes()
        page.locator("#toggle-advanced-shipments").click()
        page.locator("#mapping-file-shipments").set_input_files(
            {"name": "slow-mapping.json", "mimeType": "application/json", "buffer": manual}
        )
        expect(page.locator("#validate-shipments")).to_be_disabled()
        expect(page.locator("#format-title-shipments")).to_have_text("Leyendo mapping manual…")
        page.locator("#file-shipments").set_input_files(root / "fixtures/operaciones-invalidas.csv")
        expect(page.locator("#validate-shipments")).to_be_disabled()
        page.evaluate("window.releaseFileRead()")
        expect(page.locator("#format-title-shipments")).to_have_text("Mapping manual: errores-demo@1")
        expect(page.locator("#validate-shipments")).to_be_enabled()
        page.locator("#mapping-file-shipments").set_input_files(
            {"name": "slow-obsolete.json", "mimeType": "application/json", "buffer": manual}
        )
        page.locator("#toggle-mapping-shipments").click()
        saved = (
            page.locator("#saved-shipments option")
            .filter(has_text="operaciones-demo@1")
            .get_attribute("value")
        )
        page.locator("#saved-shipments").select_option(saved)
        page.evaluate("window.releaseFileRead()")
        expect(page.locator("#format-title-shipments")).to_have_text(
            "Formato seleccionado: operaciones-demo@1"
        )
        page.locator("#mapping-file-shipments").set_input_files(
            {"name": "slow-failed.json", "mimeType": "application/json", "buffer": manual}
        )
        page.evaluate("window.rejectFileRead()")
        expect(page.locator("#notice")).to_contain_text("No se pudo leer el mapping")
        expect(page.locator("#validate-shipments")).to_be_enabled()
        expect(page.locator("#mapping-shipments")).to_have_value("")
        page.locator("#mapping-file-shipments").set_input_files(
            {"name": "slow-stale-failed.json", "mimeType": "application/json", "buffer": manual}
        )
        page.locator("#toggle-mapping-shipments").click()
        page.locator("#saved-shipments").select_option(saved)
        page.locator("#mapping-shipments").fill('{"id":"newer-choice"}')
        previous_notice = page.locator("#notice").text_content()
        page.evaluate("window.rejectFileRead()")
        expect(page.locator("#format-title-shipments")).to_have_text("Mapping manual: newer-choice")
        expect(page.locator("#notice")).to_have_text(previous_notice)

        # Actual imports before exercising a pending agreement read.
        page.locator('[data-view="new"]').click()
        expect(page.locator("#file-shipments")).to_be_attached()
        for role, filename in (("shipments", "operaciones.xlsx"), ("charges", "liquidacion.csv")):
            upload(page, role, root / "fixtures" / filename, root / "fixtures" / f"mapping-{role}.json")
        page.locator("#goto-step-2").click()
        page.locator("#agreement-file").set_input_files(
            {
                "name": "slow-agreements.json",
                "mimeType": "application/json",
                "buffer": (root / "fixtures/agreements.json").read_bytes(),
            }
        )
        page.locator("#goto-step-3").click()
        expect(page.locator("#step-panel-2")).to_be_visible()
        expect(page.locator("#notice")).to_contain_text("Esperá")
        b_config = next(
            c
            for c in client.get("/api/configs").json()
            if c["kind"] == "agreement" and c["payload"]["id"] == "B"
        )
        page.locator("#agreement-select").select_option(b_config["hash"])
        page.evaluate("window.releaseFileRead()")
        expect(page.locator("#agreements")).to_have_value(
            json.dumps([b_config["payload"]], indent=2, ensure_ascii=False)
        )
        page.locator("#agreement-file").set_input_files(
            {"name": "slow-failed-agreement.json", "mimeType": "application/json", "buffer": b"[]"}
        )
        page.evaluate("window.rejectFileRead()")
        expect(page.locator("#notice")).to_contain_text("No se pudo leer el acuerdo")
        expect(page.locator("#agreements")).to_have_value("[]")
        page.locator("#goto-step-3").click()
        expect(page.locator("#notice")).to_contain_text("Seleccioná un acuerdo válido")
        page.locator("#agreement-file").set_input_files(
            {"name": "slow-stale-agreement.json", "mimeType": "application/json", "buffer": b"[]"}
        )
        page.locator("#agreement-select").select_option(b_config["hash"])
        previous_notice = page.locator("#notice").text_content()
        page.evaluate("window.rejectFileRead()")
        expect(page.locator("#notice")).to_have_text(previous_notice)
        expect(page.locator("#agreements")).to_have_value(
            json.dumps([b_config["payload"]], indent=2, ensure_ascii=False)
        )
    finally:
        page.evaluate("window.restoreFileRead()")

    # Real import with enough warnings for three pages; payload remains entirely available.
    case = destination / "uncertainty"
    mapping = json.loads((case / "charges.json").read_text())
    mapping["concept_map"] = {"known": "base"}
    payload = "id;settlement;reference;carrier;agreement;concept;amount;currency\n" + "".join(
        f"W{i};L;00001;C;A;unknown-{i};1;ARS\n" for i in range(121)
    )
    (case / "warnings.csv").write_text(payload)
    (case / "warning-map.json").write_text(json.dumps(mapping))
    page.locator('[data-view="new"]').click()
    expect(page.locator("#file-shipments")).to_be_attached()
    upload(page, "shipments", case / "shipments.csv", case / "shipments.json")
    upload(page, "charges", case / "warnings.csv", case / "warning-map.json")
    expect(page.locator("#result-charges .import-issues summary")).to_contain_text("121 advertencia(s)")
    details = page.locator("#result-charges .import-issues")
    assert details.locator("li").count() == 0
    details.locator("summary").click()
    expect(details.locator("li")).to_have_count(50)
    details.locator(".issue-page-number").fill("3")
    details.locator(".issue-page-number").press("Tab")
    expect(details.locator("li")).to_have_count(21)
    expect(details).to_contain_text("unknown-120")
    page.locator("#goto-step-2").click()
    page.locator("#agreement-file").set_input_files(case / "corrected.json")
    expect(page.locator("#agreement-load-status")).to_contain_text("Revisá")
    page.locator("#goto-step-3").click()
    expect(page.locator("#step-panel-3")).to_be_visible()
    details = page.locator("#verify-charges-summary .import-issues")
    details.locator("summary").click()
    expect(details.locator("li")).to_have_count(50)
    details.locator(".issue-next").click()
    expect(details.locator("li").first).to_contain_text("unknown-50")
    details.locator("summary").click()
    expect(details.locator("li")).to_have_count(0)
    page.screenshot(path=str(destination / "warning-pages.png"), full_page=True)
    page.locator('[data-view="configs"]').click()
    expect(page.locator("#toggle-create-config")).to_be_visible()
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    expect(page.locator("#toggle-create-config")).to_be_in_viewport()
    page.screenshot(path=str(destination / "configs-mobile.png"), full_page=True)
    page.set_viewport_size({"width": 1280, "height": 720})
    return {
        "config_fetch_race": "protected",
        "file_read_races": "protected",
        "warning_count": 121,
        "max_list_rows": 50,
        "mobile_width": 390,
    }
