# Evidencia portátil de QA — 23/09/2026

El commit de código vigente es `4f368d4586438333a1c1658ec1cb09fe34a20dec`; su huella de código, pruebas y reglas de checkout es `bf5b45d760d225038f2bc0e1e01dca4075e64c089c6590b61480c640f5482371`. Los **nueve recibos `v2`** son los aceptados por `QA_COVERAGE_LEDGER.json`: entrega limpia, suite, mutaciones, navegador, 1.000 cargos, los tres pasos del control documental ficticio y cotejo local de los artefactos Linux/Windows descargados. Cada recibo tiene salida 0 y log íntegro con SHA-256 comprobable.

Los recibos originales se generaron en `output/`, ruta ignorada por Git. Para publicarlos se copiaron recibo y log aquí. En cada copia sólo se cambió `log` a esta ruta y se añadieron `original_log` y `original_receipt_sha256`; comando, estado, plataforma, tiempo, huellas de fuente y `log_sha256` se preservaron. Los logs son idénticos a los originales según su SHA-256. `original_receipt_sha256` permite cotejar con el recibo local si todavía existe; no es una firma externa.

Los seis recibos anteriores (`qa-20260923-final-*` y `qa-20260923-delivery-final`) corresponden al commit `40232ac` y ahora son **históricos**, porque `.gitattributes` pasó a formar parte de la huella. Los tres recibos `qa-20260923-verify`, `qa-20260923-delivery` y `qa-20260923-delivery-rerun` conservan fallos corregidos del verificador local; nunca se cuentan como verdes. Los reportes `*-v2.json` resumen instalación, navegador y escala. Los archivos grandes del navegador y de la corrida sintética siguen fuera de Git.

El primer [workflow de plataformas](https://github.com/Juan4787/Calibre/actions/runs/35822778429) (`f3d3ab5`) aprobó 24/24 casos en Linux y 24/24 en Windows, pero **falló correctamente** al cotejar un snapshot. Los archivos completos están en `platform-initial/`. `root-cause.json` demuestra que convertir únicamente `fixtures/authorization.txt` de LF a CRLF reproduce exactamente el `snapshot_hash` y el `run_id` observados en Windows; los otros campos de esa huella, incluidos los 46 hallazgos, coincidían. `.gitattributes` fijó LF para ese original y el workflow nuevo compara los bytes de todos los fixtures con el commit antes de ejecutar.

El segundo [workflow de plataformas](https://github.com/Juan4787/Calibre/actions/runs/35823451264) (`4f368d4`) terminó verde: 17 fixtures con bytes exactos en ambos sistemas, 24/24 casos en cada uno, nueve pruebas adicionales de rutas/XLSX desde wheel instalado en Windows y tres datasets con huella idéntica entre Linux y Windows. `platform-final/` conserva los dos reportes, ambas huellas completas y `reconciliation.json` (`parity=true`, cero divergencias). En ambas carpetas `platform-*`, `github-artifacts-raw.zip` preserva los bytes descargados y `raw-artifacts-manifest.json` sus SHA-256. Los JSON separados sirven para inspección y el cotejo local; Git puede normalizar sus saltos de línea, pero su contenido JSON se comprobó igual al del ZIP crudo. El wheel se instaló y probó fuera del checkout; esto **no** prueba Excel de escritorio, un instalador firmado, otros Windows/sistemas de archivos ni datos de clientes reales.

Para volver a verificar los nueve recibos sin modificar el árbol, desde la raíz del repositorio con Python 3.12 o superior:

```bash
python3 - <<'PY'
import hashlib
import json
import zipfile
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
for folder in ('platform-initial', 'platform-final'):
    directory = root / 'docs/qa-evidence/2026-09-23' / folder
    manifest = json.loads((directory / 'raw-artifacts-manifest.json').read_text())
    raw = directory / 'github-artifacts-raw.zip'
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == manifest['raw_zip_sha256']
    with zipfile.ZipFile(raw) as archive:
        for name, expected in manifest['raw_file_sha256'].items():
            contents = archive.read(name)
            assert hashlib.sha256(contents).hexdigest() == expected
            assert json.loads(contents) == json.loads((directory / name).read_bytes())
print(len(ledger['executions']), 'recibos vigentes con logs verificables')
PY
```

Esta validación constata integridad relativa al checkout y a los hashes comprometidos en Git. No demuestra que la máquina, la cuenta GitHub, el control externo o los datos de un cliente real sean confiables. La cobertura causal permanece parcial según el ledger.
