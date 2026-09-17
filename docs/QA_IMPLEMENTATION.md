# Acta de entrega de infraestructura QA

Fecha: 2026-09-17. Producto examinado: Freight Audit 0.1.0, base `3ec4fa667ece36e58d9898f015efb95d41e19603`. Durante el cierre se observó HEAD `d4654e1` con la incorporación inicial de QA; esta acta describe también las correcciones locales posteriores. No representa un release publicado ni un commit final reproducible. Se comparó `src/` y `fixtures/` contra la base: sin cambios de producto.

## Entregado

- Threat model causal; 30 invariantes con defensas y límites; 10 clases de oráculo y 20 relaciones metamórficas.
- 58 familias operativas con datos, pasos, expected, oráculo, severidad, prioridad, costo, errores de interpretación, cobertura y respuesta. Catálogo único `qa/catalog.py` → Markdown, CSV y backlog; validación de selectores contra AST de tests sin ejecutarlos.
- Matrices numérica, temporal, de matching, archivos y seguridad; cinco arquetipos; diferencias entre soporte actual y abstracciones pendientes.
- IR-COMMON y 15 runbooks; triage, preservación, contención, impacto conservador e invalidación externa sin reescritura histórica.
- Protocolo de cliente real con contraste ciego; gates separados para infraestructura, piloto supervisado y uso de conclusiones para pago sin nuestra revisión.
- CLI `scripts/qa.py`: matriz, invariantes, reconciliación, impacto de sólo lectura y mutación dirigida. Referencia racional independiente, generadores Hypothesis y tres CSV con expectativas/hash manuales.
- Integración en `scripts/verify.sh`, paths de pytest y manifest del sdist. QA permanece fuera del wheel de producto. No se añadieron dependencias de ejecución al producto.

## Evidencia ejecutada

| Control | Resultado observado | Alcance exacto |
|---|---|---|
| `.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py --hypothesis-show-statistics` | **21 passed in 6.19s** | Sólo infraestructura nueva; log `output/qa/tests-infrastructure.txt` |
| Diferencial de precio | 25 ejemplos válidos; cero fallidos/inválidos | Cantidad, tarifa, mínimo opcional, porcentaje, escala 0/2/3/8 y cuatro modos; no AST general |
| Incertidumbre y metamorfismo | 25 ejemplos válidos; cero fallidos/inválidos | Una precondición retirada, inversión de listas y renombre; no todas las MT implementadas |
| Checker negativo | Diez manipulaciones rechazadas | Confirmada falsa, cargo omitido/duplicado, suma, actual, moneda, falso PASS, evidencia, versión y traza; hashes desactivados para aislar comprobación semántica |
| Export temporal desde Store | JSON/XLSX/HTML consistentes; etiqueta XLSX y HTML alteradas detectadas | Archivos de demo reales, DB temporal; API es objeto suministrado para probar comparador, no llamada HTTP; navegador no ejecutado |
| Impacto | Base sin cambios de bytes; desconocidos conservados, filtro excluyente válido, corrupción incluida, ruta inexistente no creada | Prueba sobre base temporal, sin Store en el lector |
| CLI con Python `-O` | Tres entradas inválidas clasificadas con salida 2, sin traceback; familia nueva permanece pendiente | Valida recuperación y evita interpretar selección como certificación |
| `mutate` sin `--execute` | Ocho anclas únicas válidas | Valida aplicabilidad de M01–M08; no cuenta como ejecutar ocho mutantes |
| `mutate --ids M01 M05 M06 --execute` | **3/3 detectados** con baseline sano | Tolerancia, evidencia y ambigüedad parcial; aserciones causales en copias temporales; log `output/qa/mutants-sample.json` |
| `invariants output/delivery/demo/audit.json --require-provenance` | Sin contradicciones | Lectura de export histórico; no regenerado ni recalculado |
| `reconcile output/delivery/second-client` | JSON/XLSX/HTML sin divergencias | API y UI explícitamente `not supplied`; no prueba contrato verdadero |
| `impact --db .local/delivery.db --importer-hash unavailable` | Dos candidatos `unknown`, salida 3 | Ambas corridas carecen de esa huella; ninguna se declara no afectada |
| Ruff lint y formato | Correctos en 11 archivos Python de QA, script y tests | No modificó código productivo |
| `mypy --explicit-package-bases qa scripts/qa.py` | Sin problemas, 10 archivos fuente | Base explícita evita colisión entre paquete qa y script qa.py |
| `matrix --check` | 58 familias, cero errores | Vistas generadas y referencias actuales; las 58 familias conservan obligaciones pendientes |
| Compilación Python, `bash -n`, `git diff --check` | Correctos | Sintaxis y formato del cambio |
| Build aislado de muestra y contenido de paquetes | Wheel y sdist construidos | sdist incluye QA, matriz CSV y corpus; wheel conserva recursos UI y excluye qa; `output/qa/package-check.json` |

La primera muestra tenía 17 casos y pasó. Se incorporaron cuatro comprobaciones de CLI y se repitió **sólo ese archivo** para validar el cambio: resultado final 21. No sumar los dos intentos como cobertura distinta ni presentar 21+148 como una nueva ejecución integral.

Los mutantes fallaron por el mecanismo buscado: M01 convirtió PASS en FAIL en 100.01; M05 convirtió REVIEW/confirmada0 en FAIL/confirmada100 sin evidencia; M06 produjo FAIL en un grupo parcial relacionado con un cargo ambiguo. No se contaron hashes cambiados, fallos de importación ni timeouts como detecciones.

## Incidencias de la propia infraestructura

Se corrigieron tipado de colecciones y nombres del CLI detectados por mypy, se conservaron familias nuevas como pendientes y se clasificaron entradas malformadas. No hubo necesidad de cambiar el motor para que los verificadores aceptaran los fixtures.

El intento de build con `--no-isolation` falló porque el entorno de trabajo no contiene `setuptools`. El build normal, con backend aislado, pasó. El paquete de `output/qa/dist/` fue una comprobación intermedia de inclusión; posteriores ajustes de CLI y documentación no se presentan como incluidos en ese artefacto ni como una distribución final. Para publicar se debe construir y verificar el árbol final conforme a QA-55.

## Pendientes y conclusión permitida

Esta sesión valida la utilidad de las herramientas y la viabilidad del procedimiento, **no completa las 58 familias**. No se ejecutó otra vez la suite previa de 148 casos, ni un barrido P0/P1, benchmark masivo, navegador, Windows, fuzz pesado, migración real, fallo de disco ni piloto con datos reales. M02/M03/M04/M07/M08 están definidos pero no ejecutados en esta muestra.

No hay aislamiento multiempresa nativo, conciliación automática contra total documental, manifest completo de aplicación por corrida ni ledger nativo de invalidaciones. El alcance desconocido se conserva para revisión; no se resuelve inventando metadata histórica. El contrato debe confirmar fecha, unidad de obligación, redondeos y evidencia.

Gate S: controles de esta entrega satisfechos en el entorno local y alcance descrito. Gate P: **no acreditado**, requiere ejecutar controles aplicables y protocolo real. Gate U: **cerrado**. La próxima tarea se delega por TEST_ID y causa; no consiste en repetir todos los comandos para acumular resultados verdes.
