import json
from pathlib import Path
from fastapi.testclient import TestClient
from freight_audit.canonical import canonical
from freight_audit.importing import ImportMapping, import_data
from freight_audit.server import create_app

root = Path(__file__).parent
m = ImportMapping.model_validate({'id': 'size', 'version': '1', 'entity': 'shipments',
 'date_formats': ['%Y-%m-%d'], 'columns': [
 {'source': 'id', 'target': 'id', 'type': 'text'},
 {'source': 'ref', 'target': 'reference', 'type': 'text'},
 {'constant': 'C', 'target': 'carrier', 'type': 'text'},
 {'source': 'date', 'target': 'attributes.service_date', 'type': 'date'}]})
data = ('id;ref;date\n' + ''.join(f'S{i};R{i};2026-05-01\n' for i in range(36000))).encode()
r = import_data(data, 'small.csv', m)
ds = {'label': 'synthetic transport payload', 'shipments': r['records'], 'charges': [],
      'agreements': [], 'mappings': [r['mapping']], 'documents': {r['document']: 'small.csv'},
      'evidence': [], 'issues': r['issues'], 'coverage': {}}
body = canonical(ds).encode()
out = {'source_bytes': len(data), 'rows': r['accepted'], 'rejected': len(r['rejected']),
       'normalized_request_bytes': len(body), 'http_limit': 32 * 1024 * 1024}
with TestClient(create_app(root / 'payload.sqlite')) as c:
    c.headers['X-Freight-Local'] = c.get('/api/session').json()['token']
    response = c.post('/api/audit/preflight', content=body, headers={'Content-Type': 'application/json'})
    out['preflight_http_status'] = response.status_code
    out['preflight_message'] = response.json()
(root / 'payload_results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(json.dumps(out, ensure_ascii=False, indent=2))
