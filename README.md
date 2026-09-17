# FREIGHT AUDIT

Prototipo B2B local para reconstruir cargos esperados a partir de operaciones, acuerdos versionados y evidencia, compararlos con cargos reales y conservar una explicación reproducible. Todos los fixtures son **completamente ficticios**.

El programa separa PASS, FAIL, REVIEW y UNDETERMINABLE. Sólo una discrepancia objetiva integra las diferencias confirmadas. Ningún importe se presenta como ahorro. Las decisiones humanas no modifican el hallazgo original.

## Inicio rápido — Linux/macOS, Python 3.12+

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/freight-audit serve --port 8765
```

Abrir **http://127.0.0.1:8765**. Seleccionar **Explorar demostración ficticia**. La aplicación no necesita red después de instalarse. Para detenerla, Ctrl+C en su terminal.

En este workspace también quedó una demo preparada con dos clientes ficticios. Para abrir esa base conservada: `.venv/bin/freight-audit --db .local/delivery.db serve --port 8765`. Sus informes están en `output/delivery/`.

## Windows — instalación desde fuentes

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\freight-audit.exe serve --port 8765
```

El código es portable; esta sesión verificó Linux, **no una instalación Windows real**. No se entrega todavía un instalador firmado ni un ejecutable autocontenido.

## Auditoría sin UI

```bash
.venv/bin/freight-audit run fixtures/project.json --out output/mi-auditoria
.venv/bin/freight-audit run fixtures/second-client/project.json --out output/segundo-cliente
.venv/bin/freight-audit preview fixtures/liquidacion.csv --mapping fixtures/mapping-charges.json
.venv/bin/freight-audit verify-bundle output/mi-auditoria/auditoria.zip --replay
```

La carpeta `--out` debe estar vacía: no se sustituyen informes anteriores. El comando devuelve el identificador de corrida. Para auditar un dataset ya normalizado: `freight-audit audit-json archivo.json`. Una fuente documental referenciada debe estar conservada en la base.

```bash
.venv/bin/freight-audit replay IDENTIFICADOR_DE_CORRIDA
.venv/bin/freight-audit export IDENTIFICADOR_DE_CORRIDA --out output/otra-copia
.venv/bin/freight-audit backup output/respaldo-nuevo.db
```

La opción global `--db RUTA` se coloca antes del comando. El default es `.local/audit.db`. El backup debe guardarse también fuera del equipo según el procedimiento acordado con el cliente.

## Qué contiene una exportación

- `audit.json`: resultado, snapshot, metadata e historial de decisiones.
- `snapshot.json`: datos, acuerdos, mappings, evidencia y procedencia originales de esa corrida.
- `auditoria.xlsx`: ocho hojas operativas, importes decimales exactos como texto, filtros y encabezados fijos.
- `reporte.html`: resumen autocontenido, imprimible a PDF desde el navegador.
- `sources/`: documentos originales por su hash de contenido.
- `manifest.json`: hashes de los archivos exportados.
- `auditoria.zip`: paquete portable verificable, generado desde los mismos contenidos.

Conservar el paquete **y la versión del programa**. `replay` no usa un motor nuevo para reescribir la historia. Las decisiones forman una cadena de hashes; esto no es una firma digital ni autentica al operador.

## Acuerdos, formatos y otro cliente

Desde la UI, **Acuerdos y formatos** permite editar y guardar configuraciones JSON sin tocar el código. **Nueva auditoría** permite cargar operaciones y cargos con mappings guardados o archivos JSON, revisar filas, seleccionar acuerdos, declarar evidencia y ejecutar. Un hallazgo muestra cálculo, reglas, origen de datos, decisiones y permite aportar evidencia para una nueva corrida.

Para un cliente nuevo, copiar `fixtures/second-client/` a una carpeta nueva y reemplazar sus archivos, mappings y acuerdo. Los cuatro acuerdos ficticios existentes cambian tarifas, unidades, moneda, vigencia, columnas y consolidación sólo mediante configuración. La configuración contractual debe confirmarla el cliente.

Leer [guía del primer cliente real](docs/FIRST_REAL_CLIENT.md), [reglas e importación](docs/RULES_AND_IMPORTS.md) y [arquitectura](docs/ARCHITECTURE.md). Los schemas están en `docs/schemas/` y se regeneran con `freight-audit schemas`.

## Verificación de desarrollo

Ejecutar secuencialmente:

```bash
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/mypy src
node --check src/freight_audit/static/app.js
.venv/bin/pytest -q
.venv/bin/python -m compileall -q src
.venv/bin/python -m build
.venv/bin/python scripts/benchmark.py --charges 50000 --out output/benchmark-50000.json
.venv/bin/python scripts/benchmark.py --charges 100000 --out output/benchmark-100000.json
```

Node sólo se usa para la comprobación de sintaxis de la UI, no para ejecutar el producto. `scripts/benchmark.py` mide tiempo y RSS en Linux; no mide importación, persistencia o reportes. Sus tablas de 10.000 tarifas permiten verificar que las búsquedas no recorren una tabla completa por cargo.

[Revisión adversarial](docs/ADVERSARIAL_REVIEW.md), [verificación y benchmarks](docs/VERIFICATION.md) y [entrega técnica](docs/DELIVERY.md) documentan evidencia, resultados y límites.

## Límites deliberados

Editor JSON, sin constructor visual de reglas; servicio de un solo usuario en loopback; sin autenticación ni cifrado de base; identidad del operador declarada; XLS con aceptación explícita de valores guardados; sin OCR, IA, impuestos genéricos, conciliación de totales de documentos, prorrateo automático ni integración ERP. La UI no fue diseñada ni certificada todavía para navegación interactiva de 100.000 hallazgos. El JSON conserva el resultado autoritativo.

El costo de interpretar acuerdos, onboarding, frecuencia real de errores, beneficio incremental y disposición a pagar siguen sin validarse. No construir SaaS, billing o integraciones externas antes de medir el primer caso real.
