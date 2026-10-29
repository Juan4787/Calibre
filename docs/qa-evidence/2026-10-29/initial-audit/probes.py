import io
import json
import logging
import os
import sys
from copy import deepcopy
from pathlib import Path

import openpyxl
import xlwt
from fastapi.testclient import TestClient

from freight_audit.engine import audit, matching_preflight
from freight_audit.fixtures import agreement, attr, const, op, rule, version
from freight_audit.importing import ImportMapping, import_data
from freight_audit.models import Dataset
from freight_audit.reporting import bundle_bytes, verify_bundle, workbook_bytes
from freight_audit.server import create_app
from freight_audit.storage import Store

logging.disable(logging.CRITICAL)
ROOT = Path(__file__).parent
OUT = {}


def raw_dataset():
    return {
        'label': 'Independent synthetic audit',
        'shipments': [{'id': 'S1', 'reference': '00001', 'carrier': 'C', 'attributes': {
            'service_date': {'type': 'date', 'value': '2026-05-01'},
            'weight': {'type': 'decimal', 'value': '10', 'unit': 'kg'},
        }}],
        'charges': [{'id': 'C1', 'settlement': 'L1', 'reference': '00001', 'carrier': 'C',
                     'agreement': 'A', 'concept': 'base', 'amount': '100', 'currency': 'ARS'}],
        'agreements': [agreement('A', 'C', [version('V1', [rule('R1', 'base', const('100', 'ARS'))])])],
    }


def mapper(date_format='%d/%m/%Y', allow_xls=False):
    return ImportMapping.model_validate({
        'id': 'independent', 'version': '1', 'entity': 'shipments',
        'date_formats': [date_format], 'allow_xls_cached_values': allow_xls,
        'columns': [
            {'source': 'id', 'target': 'id', 'type': 'text'},
            {'source': 'reference', 'target': 'reference', 'type': 'text'},
            {'constant': 'C', 'target': 'carrier', 'type': 'text'},
            {'source': 'date', 'target': 'attributes.service_date', 'type': 'date'},
            {'source': 'weight', 'target': 'attributes.weight', 'type': 'decimal', 'unit': 'kg'},
        ],
    })


def outcome(f):
    return {k: getattr(f, k) for k in ('status', 'actual', 'expected', 'confirmed_difference', 'shipment_ids')}


raw = raw_dataset()
raw['shipments'].append({**deepcopy(raw['shipments'][0]), 'id': 'S2', 'reference': '00002'})
raw['agreements'][0]['matching']['explicit'] = {'C1': ['S2']}
OUT['explicit_with_other_key_candidate'] = outcome(audit(Dataset.model_validate(raw)).findings[0])
raw['charges'][0]['reference'] = '99999'
ds = Dataset.model_validate(raw)
OUT['explicit_without_key_candidate'] = {
    **outcome(audit(ds).findings[0]), 'preflight': matching_preflight(ds)
}

text_timestamp = '01/05/2026 23:30:00-0300'
config = mapper('%d/%m/%Y %H:%M:%S%z')
csv_bytes = ('id;reference;date;weight\nS1;00001;' + text_timestamp + ';10\n').encode()
wb = openpyxl.Workbook()
wb.active.append(['id', 'reference', 'date', 'weight'])
wb.active.append(['S1', '00001', text_timestamp, '10'])
b = io.BytesIO()
wb.save(b)
for name, data in [('timestamp.csv', csv_bytes), ('timestamp.xlsx', b.getvalue())]:
    imported = import_data(data, name, config)
    raw = raw_dataset()
    raw['shipments'] = imported['records']
    raw['agreements'][0]['versions'][0]['valid_to'] = '2026-05-01'
    raw['agreements'][0]['versions'].append(version('V2', [rule('R2', 'base', const('200', 'ARS'))], start='2026-05-02'))
    f = audit(Dataset.model_validate(raw)).findings[0]
    OUT[name] = {'accepted': imported['accepted'], 'date': imported['records'][0]['attributes']['service_date']['value'], 'version': f.version, **outcome(f)}

# The import emits a faithful record; an API caller then changes it before save.
data = b'id;reference;date;weight\nS1;00001;01/05/2026;9\n'
imported = import_data(data, 'source.csv', mapper())
raw = raw_dataset()
raw['shipments'] = deepcopy(imported['records'])
raw['shipments'][0]['attributes']['weight']['value'] = '10'
raw['shipments'][0]['provenance']['attributes.weight']['raw'] = '10'
raw['documents'] = {imported['document']: 'source.csv'}
raw['mappings'] = [mapper().model_dump(mode='json')]
raw['agreements'][0]['versions'][0]['rules'][0]['expression'] = op('mul', attr('weight', 'kg'), const('10', 'ARS/kg'))
store = Store(ROOT / 'provenance.sqlite')
store.put_source(data)
ds = Dataset.model_validate(raw)
run_id = store.save(ds, audit(ds))
OUT['forged_provenance'] = {
    'source_weight': '9', 'normalized_weight': '10',
    'finding': outcome(audit(ds).findings[0]),
    'replay_identical': store.replay(run_id)['identical'],
    'bundle_verified': verify_bundle(bundle_bytes(store, run_id))['id'] == run_id,
}

# Corrupt only an isolated fixture DB, never user data.
with store.connect() as conn:
    conn.execute('DROP TRIGGER immutable_sources_UPDATE')
    conn.execute('UPDATE sources SET data=?', (b'corrupt',))
with TestClient(create_app(store.path), raise_server_exceptions=False) as client:
    client.headers['X-Freight-Local'] = client.get('/api/session').json()['token']
    statuses = {fmt: client.get(f'/api/runs/{run_id}/export/{fmt}').status_code for fmt in ('canonical', 'html', 'xlsx', 'zip')}
    statuses['load'] = client.get(f'/api/runs/{run_id}').status_code
    statuses['replay'] = client.post(f'/api/runs/{run_id}/replay').status_code
OUT['corrupt_original_http_statuses'] = statuses

# XML-forbidden text can come from CSV, JSON, evidence, or a human decision.
data = b'id;reference;date;weight\nS1;00001;01/05/2026;10\n'
imported = import_data(data, 'valid.csv', mapper())
raw = raw_dataset()
raw['shipments'] = imported['records']
raw['label'] = 'Control\x01periodo'
store = Store(ROOT / 'controlchar.sqlite')
store.put_source(data)
ds = Dataset.model_validate(raw)
run_id = store.save(ds, audit(ds))
OUT['control_character_export'] = {'run_saved': True}
with TestClient(create_app(store.path), raise_server_exceptions=False) as client:
    OUT['control_character_export']['http'] = {fmt: client.get(f'/api/runs/{run_id}/export/{fmt}').status_code for fmt in ('canonical', 'html', 'xlsx', 'zip')}

# Same failure from a real accepted CSV field.
data = b'id;reference;date;weight;extra\nS1;00001;01/05/2026;10;bad\x01value\n'
m = mapper().model_dump(mode='json')
m['columns'].append({'source': 'extra', 'target': 'attributes.extra', 'type': 'text'})
imp = import_data(data, 'control.csv', ImportMapping.model_validate(m))
raw = raw_dataset()
raw['shipments'] = imp['records']
store = Store(ROOT / 'controlcsv.sqlite')
store.put_source(data)
ds = Dataset.model_validate(raw)
rid = store.save(ds, audit(ds))
try:
    bundle_bytes(store, rid)
except Exception as exc:
    OUT['control_character_csv'] = {'accepted': imp['accepted'], 'audit_status': audit(ds).findings[0].status, 'zip_error': type(exc).__name__}

# XLS legacy visibility handling, after the explicitly required cached-value opt-in.
for mode in ('row', 'column', 'sheet'):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Data')
    if mode == 'sheet':
        wb.add_sheet('Visible')
        ws.visibility = 1
    for r, row in enumerate([['id', 'reference', 'date', 'weight'], ['S1', '00001', '01/05/2026', '10']]):
        for col, val in enumerate(row):
            ws.write(r, col, val)
    if mode == 'row':
        ws.row(1).hidden = True
    if mode == 'column':
        ws.col(3).hidden = True
    b = io.BytesIO()
    wb.save(b)
    cfg = mapper(allow_xls=True).model_copy(update={'sheet': 'Data'})
    imported = import_data(b.getvalue(), mode + '.xls', cfg)
    OUT['xls_hidden_' + mode] = {'accepted': imported['accepted'], 'rejected': imported['rejected'], 'warnings': [x['message'] for x in imported['issues']]}

print(json.dumps(OUT, ensure_ascii=False, indent=2))
(ROOT / 'probe_results.json').write_text(json.dumps(OUT, ensure_ascii=False, indent=2))
