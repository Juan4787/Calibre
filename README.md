# FREIGHT AUDIT

Revisión técnica: [RIGOR_REVIEW](docs/RIGOR_REVIEW.md) y [avance del 23/09/2026](docs/QA_ADVANCEMENT_2026-09-23.md). Detallan los fallos encontrados, las correcciones, la evidencia ejecutada y los límites pendientes. El [ledger](docs/QA_COVERAGE_LEDGER.md) conserva las obligaciones completas; no declara cobertura total a partir del número de tests.

Prototipo B2B local para reconstruir cargos esperados a partir de operaciones, acuerdos versionados y evidencia, compararlos con cargos reales y conservar una explicación reproducible. Todos los fixtures son **completamente ficticios**.

El programa separa PASS, FAIL, REVIEW y UNDETERMINABLE. Sólo una discrepancia objetiva integra las diferencias confirmadas. Ningún importe se presenta como ahorro. Las decisiones humanas no modifican el hallazgo original.

El sistema de QA parte de [TEST_STRATEGY](docs/TEST_STRATEGY.md). La [matriz operativa](docs/TEST_MATRIX.md) y el [backlog](docs/TEST_AUTOMATION_BACKLOG.md) distinguen pruebas implementadas de obligaciones pendientes. [QA_EXECUTION](docs/QA_EXECUTION.md) contiene comandos, oráculos, mutaciones y criterios de interpretación; [QA_IMPLEMENTATION](docs/QA_IMPLEMENTATION.md) registra la muestra efectivamente verificada. Ante un resultado económico sospechoso, seguir [TRIAGE_PLAYBOOK](docs/TRIAGE_PLAYBOOK.md) e [INCIDENT_RESPONSE](docs/INCIDENT_RESPONSE.md). Los [gates de piloto y uso](docs/RELEASE_CRITERIA.md) requieren evidencia adicional y no quedan aprobados por la cantidad de tests.

[QA_DELIVERY](docs/QA_DELIVERY.md) resume las 22 decisiones de testing, incidentes, uso y delegación.

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

La carpeta `--out` **no debe existir**: la exportación crea una carpeta nueva y rechaza enlaces simbólicos en la ruta. Si se interrumpe después de crearla, deja `EXPORTACION_INCOMPLETA.txt`; esos archivos no deben usarse y la operación debe repetirse en otra carpeta. El comando devuelve el identificador de corrida. Para auditar un dataset ya normalizado: `freight-audit audit-json archivo.json`. Una fuente documental referenciada debe estar conservada en la base.

```bash
.venv/bin/freight-audit replay IDENTIFICADOR_DE_CORRIDA
.venv/bin/freight-audit export IDENTIFICADOR_DE_CORRIDA --out output/otra-copia
.venv/bin/freight-audit backup output/respaldo-nuevo.db
```

La opción global `--db RUTA` se coloca antes del comando. El default es `.local/audit.db`. El backup debe guardarse también fuera del equipo según el procedimiento acordado con el cliente.
El backup exige un nombre nuevo, rechaza enlaces simbólicos en la ruta y publica una copia íntegra sin sustituir otra. La protección no cubre un proceso concurrente del mismo usuario que cambie directorios durante la escritura ni prueba supervivencia a un corte eléctrico.

## Qué contiene una exportación

- `audit.json`: resultado, snapshot, metadata e historial de decisiones.
- El formato v2 incluye snapshot, acuerdos, mappings, evidencia y procedencia dentro de `audit.json`; `snapshot.json` sólo aparece en paquetes antiguos v1.
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

Antes de concluir que el lote está completo, contrastar originales, cantidades e importes con un control independiente: [procedimiento y formato del control externo](docs/EXTERNAL_CONTROL.md). El ejemplo del repositorio es ficticio y no acredita que un cliente real haya aportado todos sus documentos.

## Verificación de desarrollo

Ejecutar secuencialmente:

```bash
.venv/bin/ruff check src tests scripts qa
.venv/bin/ruff format --check src tests scripts qa
.venv/bin/mypy src
.venv/bin/mypy --explicit-package-bases qa scripts/qa.py
.venv/bin/python scripts/qa.py matrix --check
node --check src/freight_audit/static/app.js
.venv/bin/pytest -q
.venv/bin/python -m compileall -q src
.venv/bin/python -m build
.venv/bin/python output/e2e/platform_scale/benchmark_runner.py --sizes 1000 --reps 1 --skip-curve --all-exports --output-dir output/qa48-small
# Con el árbol Git limpio y los cambios confirmados:
.venv/bin/python scripts/verify_delivery.py --output output/delivery-verification.json
```

Node sólo se usa para la comprobación de sintaxis de la UI, no para ejecutar el producto. El runner de 1.000 cargos mide las etapas del flujo y compara los resultados sintéticos con un oráculo; no acredita 50.000/100.000 cargos ni la UI de navegador a esa escala. Las campañas grandes requieren un equipo con memoria suficiente y controles explícitos de recursos. `verify_delivery.py` reconstruye wheel y sdist en dos copias limpias, compara sus contenidos, instala cada uno fuera del checkout y comprueba recursos, demo, replay, exportación y equivalencia económica LF/CRLF; no prueba Excel de escritorio.

[Revisión adversarial](docs/ADVERSARIAL_REVIEW.md), [verificación y benchmarks](docs/VERIFICATION.md) y [entrega técnica](docs/DELIVERY.md) documentan evidencia, resultados y límites.

## Límites deliberados

Editor JSON, sin constructor visual de reglas; servicio de un solo usuario en loopback; sin autenticación ni cifrado de base; identidad del operador declarada; XLS con aceptación explícita de valores guardados; sin OCR, IA, impuestos genéricos, conciliación de totales de documentos, prorrateo automático ni integración ERP. La UI no fue diseñada ni certificada todavía para navegación interactiva de 100.000 hallazgos. El JSON conserva el resultado autoritativo.

El costo de interpretar acuerdos, onboarding, frecuencia real de errores, beneficio incremental y disposición a pagar siguen sin validarse. No construir SaaS, billing o integraciones externas antes de medir el primer caso real.
