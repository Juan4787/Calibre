import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).parent
project = Path('/home/usuario/CascadeProjects/CALIBRE')
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
env = {**os.environ, 'PYTHONPATH': str(project / 'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
with (root / 'ui-probe-server.log').open('w') as log:
    proc = subprocess.Popen([sys.executable, '-m', 'freight_audit.cli', '--db', str(root / 'ui-probe.sqlite'),
                             'serve', '--port', str(port)], cwd=root, env=env, stdout=log, stderr=log)
    try:
        url = f'http://127.0.0.1:{port}'
        for i in range(100):
            try:
                httpx.get(url + '/api/session', timeout=1).raise_for_status()
                break
            except httpx.HTTPError:
                time.sleep(0.1)
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 1280, 'height': 720})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(url)
            page.locator('[data-view="new"]').click()
            expect(page.locator('#file-shipments')).to_be_attached()
            out = {'url': url, 'browser': browser.version, 'viewports': {}, 'page_errors': errors}
            out['upload_dom'] = page.evaluate('''() => {
              const d=document.querySelector('#dropzone-shipments');
              const f=document.querySelector('#file-shipments');
              return {dropzone_tag:d.tagName, dropzone_tabindex:d.tabIndex, dropzone_role:d.getAttribute('role'),
                input_display:getComputedStyle(f).display,
                input_labels: Array.from(f.labels).map(x=>x.textContent),
                tabbable_file_inputs:Array.from(document.querySelectorAll('input[type=file]')).filter(e=>e.getClientRects().length && e.tabIndex>=0).length};
            }''')
            focus = []
            for i in range(22):
                page.keyboard.press('Tab')
                focus.append(page.evaluate('document.activeElement.id || document.activeElement.textContent.trim().slice(0,45)'))
            out['keyboard_tab_order'] = focus
            with page.expect_file_chooser() as chooser:
                page.locator('#dropzone-shipments').click()
            out['mouse_opens_file_chooser'] = chooser.value is not None
            for width, height in ((1280,720),(390,844)):
                page.set_viewport_size({'width':width,'height':height})
                page.evaluate('window.scrollTo(0,0)')
                out['viewports'][str(width)] = page.evaluate('''() => ({viewport:innerWidth,document:document.documentElement.scrollWidth,
                  text_min:Math.min(...Array.from(document.querySelectorAll('main button,main label,main input,main p')).filter(e=>e.getClientRects().length).map(e=>parseFloat(getComputedStyle(e).fontSize)))})''')
                page.screenshot(path=str(root / f'upload-{width}.png'))
            page.locator('[data-view="audits"]').click()
            page.locator('#demo').click()
            expect(page.locator('#findings tr[data-finding-id]').first).to_be_visible()
            out['results_search'] = page.locator('#search').evaluate('e => ({labelCount:e.labels.length,ariaLabel:e.getAttribute("aria-label"),placeholder:e.placeholder})')
            browser.close()
        (root / 'ui_probe_results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(json.dumps(out, ensure_ascii=False, indent=2))
    finally:
        proc.terminate()
        proc.wait(timeout=15)
