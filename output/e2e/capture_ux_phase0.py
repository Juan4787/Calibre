"""Script to capture dedicated screenshots for UI/UX Phase 0.1 showcase."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8765"
SCREENSHOTS_DIR = Path("/home/usuario/CascadeProjects/CALIBRE/output/e2e/screenshots")
FIXTURES_DIR = Path("/home/usuario/CascadeProjects/CALIBRE/output/e2e/fixtures")

SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto(BASE_URL)
    page.wait_for_selector(".brand")

    # 0. Audits list (compact, clean, scannable)
    page.click("button[data-view='audits']")
    page.wait_for_selector(".run-card-rich")
    page.wait_for_timeout(300)
    page.screenshot(path=str(SCREENSHOTS_DIR / "ux_00_audits_list_compact.png"))

    # 1. New Audit - Step 1 Empty Dropzone
    page.click("button[data-view='new']")
    page.wait_for_selector("#dropzone-shipments")
    page.screenshot(path=str(SCREENSHOTS_DIR / "ux_01_step1_empty.png"))

    # 2. Upload files to show custom dropzone loaded state and format recognition
    page.set_input_files("#file-shipments", str(FIXTURES_DIR / "operaciones.csv"))
    page.wait_for_selector("#format-box-shipments")
    
    page.set_input_files("#file-charges", str(FIXTURES_DIR / "cargos.csv"))
    page.wait_for_selector("#format-box-charges")
    page.wait_for_timeout(400)
    page.screenshot(path=str(SCREENSHOTS_DIR / "ux_02_step1_loaded.png"))

    # 3. Step 2 - Acuerdo (with Step 1 collapsed into 1-line summary bar)
    page.click("#goto-step-2")
    page.wait_for_selector("#step-panel-2")
    page.wait_for_selector("#step-summary-1")
    page.wait_for_timeout(300)
    page.screenshot(path=str(SCREENSHOTS_DIR / "ux_03_step2_active.png"))

    # 4. Step 3 - Verificación (with Step 1 & 2 collapsed into summary bars)
    page.click("#goto-step-3")
    page.wait_for_selector("#step-panel-3")
    page.wait_for_selector("#step-summary-2")
    page.wait_for_timeout(300)
    page.screenshot(path=str(SCREENSHOTS_DIR / "ux_04_step3_active.png"))

    # 5. Open an existing audit to capture compact table, no-dash badges, and economic summary
    page.click("button[data-view='audits']")
    page.wait_for_selector(".run-card-rich")
    page.click(".run-card-rich")
    page.wait_for_selector("#findings tr")
    page.wait_for_timeout(400)
    page.screenshot(path=str(SCREENSHOTS_DIR / "ux_05_audit_result_compact.png"))

    # 6. Open finding detail modal
    buttons = page.locator("[data-finding]").all()
    if buttons:
        buttons[0].click()
        page.wait_for_selector(".star-status-pill")
        page.wait_for_timeout(300)
        page.screenshot(path=str(SCREENSHOTS_DIR / "ux_06_modal_finding.png"))
        page.click("#close-detail")
        page.wait_for_timeout(200)

    # 7. Acuerdos y formatos page (compact cards)
    page.click("button[data-view='configs']")
    page.wait_for_selector("#import-config-btn")
    page.wait_for_timeout(300)
    page.screenshot(path=str(SCREENSHOTS_DIR / "ux_07_acuerdos_screen.png"))

    browser.close()
    print("All Phase 0.1 UX screenshots captured successfully.")
