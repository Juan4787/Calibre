# Evidencia de la resolución ONR-001

Decisión y alcance: [ONR_001_RESOLUTION.md](../../../ONR_001_RESOLUTION.md). Recibo: [receipt.json](receipt.json).

Se recopila el 27/09/2026 evidencia de implementación y suite/navegador del 23/09, más la comprobación de paquetes del 27/09. No son resultados de clientes. Los originales de la revisión nocturna permanecen en `output/overnight-review/`; este directorio conserva copias de evidencia seleccionada para que su revisión no dependa sólo de archivos ignorados por Git.

| Archivo | Qué acredita |
|---|---|
| `before.txt`, `red-tests.txt` | Reproducción mínima previa y nueva regresión fallando por estado/importe confirmado en el código anterior. |
| `core-first.txt`, `core-green.txt` | Primera propiedad demasiado amplia respecto al hash literal de configuración; corrección del oráculo y 98 casos dirigidos aprobados. El motivo está explicado en el documento de resolución. |
| `verify.log` | Suite final de 254 tests, controles estáticos, matriz, compilación y build; salida 0. |
| `mutations.json` | M11–M13 detectadas por sus aserciones causales, con selecciones y fallos observados. |
| `browser.log`, `browser-result.json` | Chromium, identidad de UI, resultados, conciliación de canales, recuperación y tiempos de la ejecución final. |
| `preflight.png`, `matching.png` | Inspección visual de advertencia previa y detalle del cargo. Las capturas no reemplazan las aserciones del runner. |
| `before.zip` | Paquete sintético original 0.1.0: +428 en el grupo y neto +353 ARS. Su integridad no acredita corrección económica. |
| `after.zip` | Mismo conflicto en 0.1.1: cargos afectados sin confirmación y neto independiente −75 ARS; contiene JSON, XLSX, HTML, originales y manifiesto. |
| `history.json` | Verificación del paquete anterior y rechazo esperado de replay con otro motor; hash antes/después igual. |
| `installed-packages.json`, `probe-installed.py` | Instalación de wheel/sdist fuera del checkout, igualdad de 17 archivos de producto y reproducción exacta del caso ONR-001. Dependencias de `.venv` reutilizadas. |
| `receipt.json` | Comandos, fechas, salidas, hashes de evidencia y huella del código/pruebas recopilada después de ejecutar. No simula una captura antes/después inexistente. |

La UI probada tiene SHA-256 `fbbbc6e0d777983a2897b350530662d9ca85789f4e033591309b1523afc3cb02`. El artefacto del motor es `882ff21e6f6d8d91c5fe2e6e36ab8549a2b85c0fce5aee76919a26d758fabc48`. Motor, UI y entorno son identificaciones distintas: el hash del motor no cubre los archivos estáticos, que el runner contrasta por separado.

## Verificar las copias y el checkout

Desde la raíz del repositorio:

```bash
.venv/bin/python - <<'PY'
import hashlib, json
from pathlib import Path
base = Path('docs/qa-evidence/2026-09-27/onr001')
r = json.loads((base / 'receipt.json').read_text())
for name, evidence in r['evidence_files'].items():
    assert hashlib.sha256((base / name).read_bytes()).hexdigest() == evidence['sha256'], name
for name, expected in r['source_fingerprints']['files'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
print('Evidencia y archivos del checkout coinciden con el recibo')
PY
.venv/bin/freight-audit verify-bundle docs/qa-evidence/2026-09-27/onr001/after.zip --replay
.venv/bin/freight-audit verify-bundle docs/qa-evidence/2026-09-27/onr001/before.zip
```

Si se modifica código/pruebas después, la comparación correspondiente debe fallar. Un hash acredita identidad, no completitud de cobertura. El recibo no lleva firma ni ancla externa de autenticidad.

Replay del paquete anterior con el motor actual debe rechazar la operación con salida 2:

```bash
.venv/bin/freight-audit verify-bundle docs/qa-evidence/2026-09-27/onr001/before.zip --replay
```

Para repetir la comprobación de instalación, primero generar `dist/` con `scripts/verify.sh` y obtener el caso con el runner de navegador en `output/onr-001-fix/browser-reviewed` si no existe. Después:

```bash
.venv/bin/python docs/qa-evidence/2026-09-27/onr001/probe-installed.py
```

Ese script usa un destino temporal distinto para cada paquete, elimina ambos al terminar y reutiliza las dependencias del intérprete invocante. No exige commit, no cambia el checkout y no reemplaza `scripts/verify_delivery.py`, que verifica otra obligación: entrega desde un commit limpio y dependencias aisladas.

La traza completa de Playwright y todos los archivos auxiliares siguen en `output/onr-001-fix/browser-reviewed/`. Los paquetes conservados son los construidos antes del cierre documental; se comprobó igualdad byte a byte del producto instalado, no identidad del contenido de documentación final dentro del sdist.
