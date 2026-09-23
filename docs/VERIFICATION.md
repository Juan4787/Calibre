# Verificación — 17 de septiembre de 2026

Acta histórica. La revisión posterior del código, los E2E y sus verificadores está en [RIGOR_REVIEW.md](RIGOR_REVIEW.md); los recuentos siguientes no describen automáticamente la versión actual.

Entorno verificado: Linux x86_64, Python 3.12.3, un proceso por check. Dependencias exactas: `requirements.lock`. Los datos y acuerdos utilizados son ficticios. La suite final aprobó 148 tests.

## Checks

- `ruff check src tests scripts`: aprobado.
- `ruff format --check src tests scripts`: aprobado al cerrar el formato.
- `mypy src`: sin problemas en 12 módulos.
- `node --check src/freight_audit/static/app.js`: aprobado.
- `pytest -q`: **148 passed**, dos avisos de deprecación de TestClient. Suite secuencial, 6,59 segundos en este equipo.
- `python -m compileall -q src`: aprobado.
- Build de wheel y sdist ejecutado; artefactos en `dist/` y hashes en `output/delivery/artifacts.json`.
- Wheel instalado con `pip --no-deps --target output/wheel-install`; desde `/tmp`, `scripts/smoke_wheel.py` confirmó que se importaba ese paquete instalado y verificó UI estática, fixtures generados sin depender del checkout, auditoría, guardado, replay y exportación.
- Ambos proyectos se ejecutaron mediante CLI y generaron JSON, XLSX, HTML, originales y ZIP en `output/delivery/demo/` y `output/delivery/second-client/`. `verify-bundle --replay` confirmó integridad y resultado idéntico en ambos. Backup SQLite en `output/delivery/delivery-backup.db`.

La suite incluye tests unitarios/integración, propiedades Hypothesis (350 ejemplos numéricos de suma/división/fuzz de números, más permutaciones y archivos corruptos), golden completos, CLI real, API local, originales/snapshots/decisiones alterados, schema SQLite, reapertura, backup/restauración, XLSX verdadero, HTML escapado, ZIP verificable y reproducción offline. El generador conserva ejemplos mínimos de Hypothesis en su caché local ignorada por Git; esos archivos no forman parte del producto.

## Datasets y resultados esperados

| Dataset | Operaciones | Cargos | Hallazgos | PASS | FAIL | REVIEW | UNDETERMINABLE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tres acuerdos | 32 | 46 | 46 | 34 | 2 | 6 | 4 |
| Segundo cliente consolidado | 6 | 2 | 2 | 1 | 1 | 0 | 0 |

Primer ejemplo: facturado aceptado 43.719,40 ARS; exceso determinado 50; defecto determinado −75; revisión 3.431; indeterminado 3.582. Segundo: 398,50 USD facturados, exceso determinado 10. No son métricas comerciales.

La demo preparada para esta entrega usa `.local/delivery.db`, con las dos auditorías y sus configuraciones. Reiniciar con `.venv/bin/freight-audit --db .local/delivery.db serve --port 8765`. Las bases de desarrollo anteriores se conservaron por separado, sin modificar sus corridas.

## Navegador Chromium real

Verificado con Playwright CLI, con el servicio en loopback:

- Abrir la lista, entrar a una auditoría y filtrar discrepancias/revisión.
- Abrir cálculo y procedencia de un hallazgo.
- Guardar una decisión ficticia y verificar que la huella del resultado original no cambió.
- Ejecutar replay desde la UI y obtener coincidencia exacta.
- Crear una auditoría desde CSV + XLSX del segundo cliente, reutilizando mappings y acuerdo guardados; seis filas operativas y dos cargos aceptados; resultado 1 PASS / 1 FAIL / 10 USD de diferencia.
- Agregar evidencia ficticia a un REVIEW: nueva corrida, caso respaldado pasa a PASS, la corrida anterior se conserva.
- Vista 1440×1000 y 390×844; sin desbordamiento horizontal de la página. Las tablas usan su propio scroll horizontal.
- Diálogo con foco nativo y cierre por Escape; modo de movimiento reducido.
- Recarga final sin errores de JavaScript ni solicitudes a destinos externos. Se corrigió un favicon ausente detectado inicialmente.

Capturas en `output/playwright/`: `audit-desktop.png`, `audit-desktop-final.png`, `audit-mobile.png`, `finding-explanation.png`, `import-preview.png`. Esto es una verificación focalizada, no una certificación exhaustiva de accesibilidad ni un test de UI a 100.000 hallazgos.

## Benchmarks

| Operaciones | Cargos / hallazgos | Cálculo (s) | Hash del resultado (s) | RSS pico (MiB) |
|---:|---:|---:|---:|---:|
| 10,000 | 50,000 | 15.953 | 4.089 | 945.9 |
| 10,000 | 100,000 | 31.577 | 8.163 | 1821.2 |

Artefacto del núcleo medido: `133731f29cdf72588915f14fc5f8ab0ad0dd0945cfcdf8377cd26b1368a68638`. RSS se obtiene de `ru_maxrss / 1024` en Linux, en MiB. Preparación de datos: 1.097 s y 1.977 s respectivamente.

Resultados brutos: `output/benchmark-50000-delivery.json` y `output/benchmark-100000-delivery.json`.
 Cada tamaño corre en un proceso independiente y secuencial; incluye matching, reglas, evidencia, agregación, trazas y huella semántica. El hashing del resultado se mide por separado. No incluye archivo de entrada, persistencia, exportación XLSX ni navegador.

Una primera medición de 50.000 cargos mostró 1.723,9 MB de RSS pico y 17,231 s de hashing. El recorrido canónico superficial eliminó copias profundas repetidas: en la siguiente medición hubo 919,4 MB y 3,617 s, con **el mismo hash del resultado**. Las tablas de 10.000 tarifas se indexan por versión para evitar búsquedas lineales por cargo.

Un perfil separado de 5.000 cargos y 1.000 operaciones registró 2,595 s bajo cProfile: 1,093 s acumulados en evaluación de reglas y 0,551 s en construcción de modelos Pydantic. `output/benchmark-profile.txt` conserva el detalle. Estos tiempos instrumentados sirven para localizar costo, no para sustituir las mediciones de la tabla.

El principal límite observado es conservar todas las trazas y serializar el resultado completo en memoria. El almacenamiento vuelve a verificar la corrida antes de conservarla; ese costo no está incluido en los benchmarks del core. Una futura exportación por streaming debe preservar los mismos contratos y controles de integridad.

## Límites y siguientes verificaciones necesarias

Sin cliente real, sin instalación Windows real, sin evaluación de reglas contractuales externas, sin certificación de seguridad/producción. Los hashes detectan alteración respecto de una copia confiable; no son firmas digitales. Los datos y la base requieren backups fuera del equipo. La auditoría trabaja sobre las líneas importadas: verificar totales y alcance del documento sigue siendo una tarea explícita del operador.
