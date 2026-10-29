import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

OUT = Path('/tmp/calibre-implementation-20261029-CvSz5k/final-live-browser')
DB = Path('/home/usuario/.local/share/calibre/workspaces/default/audit.db')
OUT.mkdir(exist_ok=False)


def snapshot():
    with sqlite3.connect(DB.as_uri() + '?mode=ro', uri=True) as db:
        assert db.execute('PRAGMA quick_check').fetchone() == ('ok',)
        assert db.execute('PRAGMA foreign_key_check').fetchall() == []
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        result = {}
        for name in tables:
            quoted = '"' + name.replace('"', '""') + '"'
            rows = sorted(json.dumps(row, default=lambda x: {'bytes': x.hex()}, sort_keys=True) for row in db.execute('SELECT * FROM ' + quoted))
            result[name] = {'rows': len(rows), 'sha256': hashlib.sha256('\n'.join(rows).encode()).hexdigest()}
        return result


before = snapshot()
errors = []
requests = []
views = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    version = browser.version
    for label, width, height in [('desktop', 1280, 720), ('mobile', 390, 844)]:
        context = browser.new_context(viewport={'width': width, 'height': height})
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append({'method': request.method, 'path': request.url.split('127.0.0.1:8765')[-1]}))
        response = page.goto('http://127.0.0.1:8765', wait_until='networkidle')
        assert response.status == 200
        expect(page.locator('#new-run')).to_be_visible()
        expect(page.locator('#demo')).to_be_visible()
        expect(page.locator('#workspace-select')).to_be_visible()
        text = page.locator('#runs').inner_text()
        assert 'Leyendo auditorías' not in text
        assert 'Del cargo a la evidencia.' in text
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.screenshot(path=str(OUT / (label + '.png')), full_page=True)
        views.append({'viewport': [width, height], 'title': page.title(), 'runs_text': text, 'horizontal_overflow': False})
        context.close()
    browser.close()
after = snapshot()
assert before == after
assert not errors, errors
assert all(r['method'] in ('GET', 'HEAD') for r in requests), requests
receipt = {'passed': True, 'checked_at': datetime.now(timezone.utc).isoformat(), 'url': 'http://127.0.0.1:8765', 'read_only': True, 'browser_version': version, 'views': views, 'page_errors': errors, 'requests': requests, 'database_before': before, 'database_after': after, 'all_database_rows_unchanged': True, 'scope': 'Live installed service, empty operational database, no demo or write action'}
(OUT / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': True, 'browser_version': version, 'database_unchanged': True, 'requests': len(requests)}))
