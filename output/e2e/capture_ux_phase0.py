"""Script to capture dedicated screenshots for UI/UX Phase 0 showcase."""
import os
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8765"
SCREENSHOTS_DIR = "/home/usuario/CascadeProjects/CALIBRE/output/e2e/screenshots"
FIXTURES_DIR = "/home/usuario/CascadeProjects/CALIBRE/output/e2e/fixtures"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto(BASE_URL)
    page.wait_for_selector(".brand")

    # 1. New Audit - Step 1 Empty Dropzone
    page.click("button[data-view='new']")
    page.wait_for_selector("#dropzone-shipments")
    page.screenshot(path=f"{SCREENSHOTS_DIR}/ux_01_step1_empty_dropzone.png")

    # 2. Upload files to show custom dropzone loaded state and format recognition
    page.set_input_files("#file-shipments", f"{FIXTURES_DIR}/operaciones.csv")
    page.wait_for_selector("#format-box-shipments")
    
    page.set_input_files("#file-charges", f"{FIXTURES_DIR}/cargos.csv")
    page.wait_for_selector("#format-box-charges")
    page.wait_for_timeout(400)
    page.screenshot(path=f"{SCREENSHOTS_DIR}/ux_02_step1_loaded_files_recognized.png")

    # 3. Step 2 - Acuerdo
    page.click("#goto-step-2")
    page.wait_for_selector("#step-panel-2")
    page.wait_for_timeout(300)
    page.screenshot(path=f"{SCREENSHOTS_DIR}/ux_03_step2_acuerdo.png")

    # 4. Step 3 - Verificación
    page.click("#goto-step-3")
    page.wait_for_selector("#step-panel-3")
    page.wait_for_timeout(300)
    page.screenshot(path=f"{SCREENSHOTS_DIR}/ux_04_step3_verificacion.png")

    # 5. Acuerdos y formatos page
    page.click("button[data-view='configs']")
    page.wait_for_selector("#import-config-btn")
    page.wait_for_timeout(300)
    page.screenshot(path=f"{SCREENSHOTS_DIR}/ux_05_acuerdos_screen.png")

    # 6. Guía de trabajo page
    page.click("button[data-view='guide']")
    page.wait_for_selector(".panel.guide")
    page.wait_for_timeout(300)
    page.screenshot(path=f"{SCREENSHOTS_DIR}/ux_06_guia_trabajo_screen.png")

    browser.close()
    print("Dedicated UX screenshots captured successfully.")
