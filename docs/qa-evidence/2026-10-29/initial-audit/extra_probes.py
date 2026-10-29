import io
import json
from copy import deepcopy
from decimal import localcontext
from pathlib import Path

from fastapi.testclient import TestClient

from freight_audit.canonical import canonical
from freight_audit.engine import audit
from freight_audit.fixtures import agreement, const, op, rule, version
from freight_audit.models import Dataset
from freight_audit.importing import import_data, ImportMapping
from freight_audit.reporting import export_run
import freight_audit.reporting as reporting
from freight_audit.server import create_app
from freight_audit.storage import Store
from qa.external_control import compare_external_control

ROOT = Path(__file__).parent
raw = {
    'label': 'Synthetic exactness check',
    'shipments': [{'id': 'S1', 'reference': '1', 'carrier': 'C', 'attributes': {
        'service_date': {'type': 'date', 'value': '2026-05-01'},
    }}],
    'charges': [{'id': 'C1', 'settlement': 'L1', 'reference': '1', 'carrier': 'C',
                 'agreement': 'A', 'concept': 'base', 'amount': '100', 'currency': 'ARS'}],
    'agreements': [agreement('A', 'C', [version('V1', [rule('R1', 'base', const('100', 'ARS'))])])],
}
out = {}
store = Store(ROOT / 'extra.sqlite')
ds = Dataset.model_validate(raw)
rid = store.save(ds, audit(ds))
calls = []
original = reporting.workbook_bytes
def counted(run):
    calls.append(True)
    return original(run)
reporting.workbook_bytes = counted
export_run(store, rid, ROOT / 'counted-export')
out['workbook_generations_in_export_run'] = len(calls)
reporting.workbook_bytes = original

# Declared date type is erased by the runtime Atom, so date == text is accepted.
bad_types = deepcopy(raw)
bad_types['agreements'][0]['versions'][0]['rules'][0]['when'] = op('eq',
    {'op': 'attr', 'field': 'service_date'},
    {'op': 'const', 'value': {'type': 'text', 'value': '2026-05-01'}})
f = audit(Dataset.model_validate(bad_types)).findings[0]
out['date_compared_to_text'] = {'status': f.status, 'expected': f.expected,
    'condition_output': [t.output for t in f.trace if t.op == 'condition']}

# Independent control should not depend on ambient decimal precision.
big = deepcopy(raw)
amount = '999999999999999999999999999999999999'
source = store.put_source(b'original synthetic charge fixture')
big['documents'] = {source: 'source.csv'}
big['charges'][0]['amount'] = amount
ref = {'document': source, 'filename': 'source.csv', 'sheet': 'CSV', 'row': 2,
       'column': 'id', 'raw': 'S1', 'transform': 'synthetic'}
big['shipments'][0]['provenance'] = {'id': ref}
big['charges'][0]['provenance'] = {'amount': {**ref, 'column': 'amount', 'raw': amount}}
ds = Dataset.model_validate(big)
rid = store.save(ds, audit(ds))
run = store.load(rid)
control = {
    'schema': 'freight-audit-external-control/v1', 'source_hashes': [source],
    'shipments_by_source': {source: 1}, 'charges_by_source': {source: 1},
    'charge_totals_by_source': {source: {'ARS': amount}},
    'shipment_count': 1, 'charge_count': 1, 'actual_by_currency': {'ARS': amount}
}
for precision in (28, 80):
    with localcontext() as ctx:
        ctx.prec = precision
        result = compare_external_control(run, control)
    out['external_control_precision_' + str(precision)] = result

store = Store(ROOT / 'controlcsv.sqlite')
rid = store.list_runs()[0]['id']
with TestClient(create_app(store.path), raise_server_exceptions=False) as client:
    out['control_csv_export_statuses'] = {fmt: client.get(f'/api/runs/{rid}/export/{fmt}').status_code for fmt in ('canonical', 'html', 'xlsx', 'zip')}

print(json.dumps(out, ensure_ascii=False, indent=2))
(ROOT / 'extra_results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
