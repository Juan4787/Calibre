# Evidencia portátil de QA — 23/09/2026

Este directorio conserva seis recibos aprobados, sus logs íntegros y tres reportes de salida acotados. Todos los recibos aprobados registran la misma huella de código/pruebas `c66f6d360bb58ea5535024bee24c31655126494569dd4adf354be36e4e36a763` y salida 0. `QA_COVERAGE_LEDGER.json` registra el SHA-256 de cada recibo y vuelve a comprobar el hash de su log. La referencia de código probada es `40232ac72da2f96c826721b9c8eb060de88e9ec7`; los commits posteriores de documentación no cambian esa huella.

Los recibos originales se generaron en `output/`, ruta ignorada por Git. Para hacerlos inspeccionables se copiaron recibo y log aquí. En cada copia sólo se cambió `log` a esta ruta y se añadieron `original_log` y `original_receipt_sha256`; comando, estado, plataforma, tiempo, huellas de fuente y `log_sha256` se preservaron. Los logs son bytes idénticos a los originales según su SHA-256. El valor `original_receipt_sha256` permite cotejar con el recibo local si se conserva, pero por sí mismo no constituye una firma externa.

Los tres recibos `qa-20260923-verify`, `qa-20260923-delivery` y `qa-20260923-delivery-rerun` documentan fallos **corregidos** de la campaña. No forman parte de las seis ejecuciones aceptadas del ledger. `delivery-verification.json`, `browser-result.json` y `scale-benchmark-summary.json` conservan el detalle resumido de las salidas; los archivos grandes del navegador y del benchmark sintético permanecen fuera de Git.

Para volver a verificar sin modificar el árbol, desde la raíz del repositorio con Python 3.12 o superior:

```bash
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

from qa.evidence import receipt_is_current, source_digest

root = Path.cwd()
ledger = json.loads((root / 'docs/QA_COVERAGE_LEDGER.json').read_text())
fingerprint = source_digest(root)
assert ledger['source_digest'] == fingerprint
for entry in ledger['executions']:
    path = root / entry['path']
    data = path.read_bytes()
    receipt = json.loads(data)
    log = root / receipt['log']
    assert hashlib.sha256(data).hexdigest() == entry['receipt_sha256']
    assert hashlib.sha256(log.read_bytes()).hexdigest() == receipt['log_sha256']
    assert receipt_is_current(receipt, fingerprint)
    assert entry['accepted']
print(len(ledger['executions']), 'recibos vigentes con logs verificables')
PY
```

Esta validación constata integridad relativa al checkout y a los hashes comprometidos en Git. No demuestra que la máquina, la cuenta GitHub, el control externo o los datos de un cliente real sean confiables. La cobertura causal permanece parcial según el ledger.
