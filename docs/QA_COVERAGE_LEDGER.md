# Cobertura de QA: obligaciones y evidencia

**No hay certificación global ni porcentaje de cobertura causal derivable del número de tests. El Gate S de infraestructura QA se evalúa según RELEASE_CRITERIA.md y no exige ni acredita cobertura total de producto.**

Este registro sustituye el cierre automático de 51/51 familias. El anterior acortaba obligaciones del catálogo, citaba selectores inexistentes y usaba hashes fijos.

Fuente única: `qa/catalog.py`. Un selector existente acredita infraestructura disponible; una ejecución acredita sus casos, no toda la familia.

Las campañas históricas Windows, escala, importación y E2E conservan su alcance original. No certifican este checkout. Ver `RIGOR_REVIEW.md`.

Commit base: `0a73fc30a6efe5e450ae919261046a0cd3ed8848`; huella del código y pruebas: `c66f6d360bb58ea5535024bee24c31655126494569dd4adf354be36e4e36a763`.

## Ejecuciones adjuntas

| Recibo | Código y log verificables | Salida | Comando |
|---|---|---|---|
| docs/qa-evidence/2026-09-23/qa-20260923-delivery-final.json | Sí | 0 | `.venv/bin/python scripts/verify_delivery.py --output output/delivery-verification-20260923.json` |
| docs/qa-evidence/2026-09-23/qa-20260923-final-verify.json | Sí | 0 | `scripts/verify.sh` |
| docs/qa-evidence/2026-09-23/qa-20260923-final-mutations.json | Sí | 0 | `.venv/bin/python scripts/qa.py mutate --execute` |
| docs/qa-evidence/2026-09-23/qa-20260923-final-browser.json | Sí | 0 | `.venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/qa40-final-20260923` |
| docs/qa-evidence/2026-09-23/qa-20260923-final-scale-1000.json | Sí | 0 | `.venv/bin/python output/e2e/platform_scale/benchmark_runner.py --sizes 1000 --reps 1 --skip-curve --all-exports --output-dir output/qa48-final-20260923` |
| docs/qa-evidence/2026-09-23/qa-20260923-final-external-control.json | Sí | 0 | `.venv/bin/python scripts/qa.py external-control output/control-final-20260923/audit.json fixtures/external-control.json` |

## Familias

| Familia | Prioridad | Estado conservador | Selectores existentes |
|---|---|---|---|
| QA-01 — Certeza y diferencia confirmada | P0 | PARTIAL | 2 |
| QA-02 — Tolerancia, signo y fronteras | P0 | PARTIAL | 2 |
| QA-03 — Referencia de precio independiente | P0 | PARTIAL | 2 |
| QA-04 — Dominio numérico y tipos estrictos | P0 | PARTIAL | 4 |
| QA-05 — Redondeo, escala y orden | P0 | PARTIAL | 2 |
| QA-06 — División y contexto ambiental | P0 | PARTIAL | 3 |
| QA-07 — Unidades y monedas separadas | P0 | PARTIAL | 3 |
| QA-08 — Números desde originales | P0 | PARTIAL | 4 |
| QA-09 — Identidad y normalización declarada | P0 | PARTIAL | 3 |
| QA-10 — Estructura CSV y conservación de filas | P0 | PARTIAL | 4 |
| QA-11 — Semántica de libro Excel | P0 | PARTIAL | 5 |
| QA-12 — XLS legacy y cache explícito | P1 | PARTIAL | 1 |
| QA-13 — Límites de importación y corrupción | P1 | PARTIAL | 1 |
| QA-14 — Importación incompleta y alcance documental | P0 | PARTIAL | 4 |
| QA-15 — Procedencia verificable | P0 | PARTIAL | 2 |
| QA-16 — Selección única de vigencia | P0 | PARTIAL | 3 |
| QA-17 — Fecha civil y seriales de Excel | P0 | PARTIAL | 4 |
| QA-18 — Reglas/condiciones y AST acotado | P0 | PARTIAL | 4 |
| QA-19 — Lookup/bandas sin desempate arbitrario | P0 | PARTIAL | 2 |
| QA-20 — Claves, aliases y vínculos explícitos | P0 | PARTIAL | 3 |
| QA-21 — Ambigüedad propagada a grupos parciales | P0 | PARTIAL | 2 |
| QA-22 — Consolidado y cargos por componentes | P0 | PARTIAL | 2 |
| QA-23 — Asignaciones superpuestas y servicios parciales | P0 | PARTIAL | 1 |
| QA-24 — Duplicados candidatos y remito legítimo | P0 | PARTIAL | 2 |
| QA-25 — Evidencia por ámbito y adición selectiva | P0 | PARTIAL | 2 |
| QA-26 — Cobertura explícita de cargos ausentes | P0 | PARTIAL | 3 |
| QA-27 — Conservación total por ID y moneda | P0 | PARTIAL | 1 |
| QA-28 — Determinismo y transformaciones | P0 | PARTIAL | 3 |
| QA-29 — Aislamiento entre clientes y catálogos | P0 | PARTIAL | 1 |
| QA-30 — Decisiones humanas y cadena | P0 | PARTIAL | 3 |
| QA-31 — Integridad histórica y mutación | P0 | PARTIAL | 3 |
| QA-32 — Replay y cambio de artefacto | P0 | PARTIAL | 3 |
| QA-33 — Proveniencia de ejecutables y alcance | P0 | PARTIAL | 1 |
| QA-34 — Backup, restore y reapertura | P0 | PARTIAL | 1 |
| QA-35 — Crash, rollback y concurrencia | P0 | PARTIAL | 1 |
| QA-36 — Schema y migración recuperable | P0 | PARTIAL | 2 |
| QA-37 — Reconciliación entre representaciones | P0 | PARTIAL | 1 |
| QA-38 — Límites de reportes y contenido activo | P0 | PARTIAL | 4 |
| QA-39 — UI conserva semántica visible y estado actual | P0 | PARTIAL | 0 |
| QA-40 — Barrera de red local | P0 | PARTIAL | 1 |
| QA-41 — Rutas, archivos y sobrescritura | P0 | PARTIAL | 5 |
| QA-42 — XML/ZIP malicioso acotado | P0 | PARTIAL | 3 |
| QA-43 — Errores de API y consistencia de operación | P1 | PARTIAL | 3 |
| QA-44 — Auditoría sin servicios externos | P1 | PARTIAL | 1 |
| QA-45 — Representación contractual y mapping aprobados | P0 | REQUIRES_REAL_CLIENT | 0 |
| QA-46 — Generalidad de cinco arquetipos | P1 | PARTIAL | 1 |
| QA-47 — Paquete y plataforma real | P1 | PARTIAL | 0 |
| QA-48 — Escala, memoria y tiempos de todas las etapas | P2 | PARTIAL | 0 |
| QA-49 — Los verificadores detectan corrupción | P0 | PARTIAL | 2 |
| QA-50 — Mutantes críticos dirigidos | P0 | PARTIAL | 1 |
| QA-51 — Validación ciega con cliente | P0 | REQUIRES_REAL_CLIENT | 0 |
| QA-52 — Gate de pago sin nuestra supervisión | P0 | REQUIRES_REAL_CLIENT | 0 |
| QA-53 — IDs y JSON inequívocos | P0 | PARTIAL | 2 |
| QA-54 — Bundle portable y ancla externa | P0 | PARTIAL | 1 |
| QA-55 — Entrega reproducible y dependencias | P1 | PARTIAL | 0 |
| QA-56 — Separación de liquidaciones y alcance de obligación | P0 | PARTIAL | 2 |
| QA-57 — Diagnóstico no muta evidencia | P0 | PARTIAL | 1 |
| QA-58 — Píxel exacto y matrices visuales exhaustivas | P3 | DEFERRED_NON_BLOCKING | 0 |

## QA-01 — Certeza y diferencia confirmada

**Obligación:** Sin evidencia: REVIEW,E100,Δ100,confirmada0; issue row impide PASS/FAIL; sin versión UNDETERMINABLE/E null. Ningún bucket confirma100.

**Procedimiento:** 1. Auditar cada variante por separado. 2. Inspeccionar finding y todos los buckets. 3. Pasar run al checker independiente.

**Oráculo:** OR-03 OR-05. **Lo que puede escapar:** Comprobar sólo finding y no summary/reportes deja escapar dinero confirmado.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_missing_evidence_does_not_confirm_even_numeric_difference tests/test_engine.py::test_import_rejects_block_economic_confirmation
```

## QA-02 — Tolerancia, signo y fronteras

**Obligación:** E100,T0.01,A100.01 PASS;100.02 FAIL+0.02;99.98 FAIL−0.02. E200,rel0.05,A210 PASS;210.01 FAIL10.01.

**Procedimiento:** 1. Ejecutar A=T exacta y T±0.01 respecto de E. 2. Recalcular T y Δ con Fraction. 3. Revisar PASS/FAIL y neto/brutos.

**Oráculo:** OR-01 OR-02. **Lo que puede escapar:** Tolerancia relativa, negativo o igualdad exacta no ejercitados.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_tolerance_and_signed_differences tests/test_qa_infrastructure.py::test_generated_reference_prices
```

## QA-03 — Referencia de precio independiente

**Obligación:** q10×2,min30,+5%→31.5; q20→42. Igual E y A no produce FAIL; cambiar A no cambia E.

**Procedimiento:** 1. Comprobar anclas de referencia. 2. Generar q/tarifa/mínimo/factor. 3. Comparar E con referencia racional sin importar helpers productivos.

**Oráculo:** OR-01 OR-02. **Lo que puede escapar:** Ambos calculan bien pero contrato mal representado; validar OR-01.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_reference_manual_anchors tests/test_qa_infrastructure.py::test_generated_reference_prices
```

## QA-04 — Dominio numérico y tipos estrictos

**Obligación:** Inputs inválidos rechazados; 36nueves+1 suma37 dígitos permitida. No coerción bool→decimal ni 1→boolean.

**Procedimiento:** 1. Validar cada input. 2. Auditar suma de inputs válidos grandes. 3. Verificar rechazo antes de conclusión o suma exacta.

**Oráculo:** OR-01 OR-03. **Lo que puede escapar:** Sólo validar Value y omitir Charge/importer.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_float_prohibited tests/test_engine.py::test_invalid_money tests/test_adversarial.py::test_aggregate_amount_can_exceed_individual_input_digit_bound tests/test_adversarial.py::test_no_boolean_coercion
```

## QA-05 — Redondeo, escala y orden

**Obligación:** Final0.01; por componente0.02; HALF_EVEN2.345→2.34,2.355→2.36. HALF_DOWN rechazado por configuración.

**Procedimiento:** 1. Ejecutar cada fila manual. 2. Diferenciar round final de dos round explícitos. 3. Comprobar escala/modo/input en trace.

**Oráculo:** OR-01 OR-02. **Lo que puede escapar:** Sólo positivos/escala2 no detecta truncamiento de créditos.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_reference_manual_anchors tests/test_qa_infrastructure.py::test_generated_reference_prices
```

## QA-06 — División y contexto ambiental

**Obligación:** 1/3→0.33;−1/8 HALF_EVEN→−0.12; divisor0/desborde→UNDETERMINABLE/0confirmado. Contexto ajeno no altera audit.

**Procedimiento:** 1. Comparar división con Decimal alta precisión y casos manuales. 2. Cambiar/restaurar contexto externo. 3. Probar precisión insuficiente.

**Oráculo:** OR-01 OR-08. **Lo que puede escapar:** Rango actual de enteros pequeños no cubre todo exponente válido.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_property_division_matches_high_precision tests/test_engine.py::test_global_decimal_context_does_not_affect_results tests/test_adversarial.py::test_inexact_comparison_becomes_undeterminable
```

## QA-07 — Unidades y monedas separadas

**Obligación:** Discordancia→UNDETERMINABLE; sin factor no conversión; 1000g×0.001kg/g×2ARS/kg=2ARS; buckets separados.

**Procedimiento:** 1. Auditar moneda discordante. 2. Introducir g frente a kg sin factor. 3. Añadir factor explícito y acuerdoUSD independiente.

**Oráculo:** OR-01 OR-03. **Lo que puede escapar:** Revisar core pero permitir suma multimoneda en UI.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_currencies_never_summed_or_converted tests/test_engine.py::test_missing_attribute_and_unit_mismatch tests/test_engine.py::test_rules_need_currency_units
```

## QA-08 — Números desde originales

**Obligación:** XLSX preserva fracción; exponente extremo rechaza fila; CSV argentino1234.56; agrupador inválido rechaza, no corrige silenciosamente.

**Procedimiento:** 1. Preservar bytes. 2. Importar con mapping confirmado. 3. Comparar value y provenance.raw con literal independiente.

**Oráculo:** OR-04. **Lo que puede escapar:** Leer expected mediante openpyxl repite el float defectuoso.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_xlsx_preserves_original_decimal_literal_without_binary_float_loss tests/test_importing.py::test_xlsx_unbounded_exponent_is_rejected_before_decimal_expansion tests/test_importing.py::test_argentine_decimal tests/test_importing.py::test_unsafe_numeric_strings_rejected
```

## QA-09 — Identidad y normalización declarada

**Obligación:** 00001 se conserva; numérico requiere política; fraccional rechaza aunque float parezca entero; concepto desconocido queda external:valor.

**Procedimiento:** 1. Importar referencia textual. 2. Repetir numeric_text reject/formatted. 3. Verificar reglas de strip y concepto desconocido.

**Oráculo:** OR-04 OR-05. **Lo que puede escapar:** Alias/Unicode normalizado fuera del mapping puede colisionar en un cliente.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_xlsx_numeric_id_requires_explicit_policy tests/test_importing.py::test_original_fractional_numeric_identifier_cannot_become_integer_after_float_rounding tests/test_importing.py::test_unknown_concept_not_canonicalized_by_accident
```

## QA-10 — Estructura CSV y conservación de filas

**Obligación:** Referencia multilínea mantiene siguiente registro en línea4; mapeada repetida/ausente error; valor extra rechaza; economía invariante al reordenar.

**Procedimiento:** 1. Importar corpus con líneas físicas anotadas. 2. Comparar aceptadas/rechazadas y raw. 3. Permutar columnas/mapping.

**Oráculo:** OR-04 OR-08. **Lo que puede escapar:** Control sólo de cantidad deja desplazamiento con misma cantidad.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_csv_multiline_provenance_uses_actual_line tests/test_importing.py::test_ambiguous_or_missing_headers_fail_file tests/test_importing.py::test_reordered_columns_same_normalized_records tests/test_adversarial.py::test_oversized_unmapped_cells_not_silently_shifted
```

## QA-11 — Semántica de libro Excel

**Obligación:** Varias hojas sin selección error; fórmula mapeada rechazada; sin fill-forward. Hoja o datos ocultos bloquean la importación hasta hacerlos visibles y revisar el alcance.

**Procedimiento:** 1. Especificar sheet. 2. Importar con columnas requeridas vacías/merged. 3. Añadir fórmula cacheada y fila oculta. 4. Cotejar alcance declarado.

**Oráculo:** OR-04. **Lo que puede escapar:** Los casos de ocultamiento probados no cubren todos los productores, estilos, merges ni caches reales.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_multisheet_requires_selection tests/test_importing.py::test_xlsx_formula_never_evaluated_or_taken_as_cache tests/test_importing.py::test_original_numeric_tokens_follow_sparse_sheet_coordinates tests/test_importing.py::test_xlsx_hidden_business_data_blocks_import_until_made_visible tests/test_importing.py::test_xlsx_hidden_selected_sheet_blocks_import
```

## QA-12 — XLS legacy y cache explícito

**Obligación:** Sin aceptación error; con aceptación warning persistente. No declarar recuperación de precisión perdida ni garantía de recalculado.

**Procedimiento:** 1. Importar sin allow_xls_cached_values. 2. Habilitar y revisar warning. 3. Cotejar pares de celdas fuera de xlrd.

**Oráculo:** OR-04. **Lo que puede escapar:** XLS generado por xlwt no cubre todos los productores reales.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_xls_requires_explicit_cached_value_acceptance
```

## QA-13 — Límites de importación y corrupción

**Obligación:** ImportErrorDetail/422 útil antes de agotar recursos; ningún resultado económico confirmado para importación abortada.

**Procedimiento:** 1. Crear cabeceras/payloads pequeños que activen límites. 2. Ejecutar en subprocess con timeout/RSS. 3. Comprobar clasificación y ausencia de corrida parcial.

**Oráculo:** OR-09 OR-10. **Lo que puede escapar:** Bytes aleatorios cortos no atraviesan parser profundo; tamaño declarado no prueba expansión real.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified
```

## QA-14 — Importación incompleta y alcance documental

**Obligación:** Rechazo impide certeza del lote. Archivo nunca aportado no se detecta por core: control externo obligatorio y déficit visible.

**Procedimiento:** 1. Contar filas de negocio. 2. Conciliar accepted/rejected/omitted. 3. Auditar issue row. 4. Comparar contra total externo y etiqueta UI.

**Oráculo:** OR-03 OR-04 OR-01. **Lo que puede escapar:** El comparador sólo detecta omisiones incluidas en un inventario externo independiente; no puede demostrar que ese inventario sea verdadero/completo ni reemplaza la validación humana.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_import_rejects_block_economic_confirmation tests/test_integration.py::test_invalid_fixture_rejects_visible_rows tests/test_external_control.py::test_external_inventory_count_and_total_are_independent_blockers tests/test_external_control.py::test_external_control_cli_exit_codes_and_hash_integrity
```

Runner adicional; usar un directorio de evidencia nuevo:

```bash
.venv/bin/python scripts/qa.py external-control ARCHIVO_AUDIT_JSON CONTROL_EXTERNO_JSON
```

## QA-15 — Procedencia verificable

**Obligación:** Documento/hoja/fila/columna/raw correctos y mapping congelado; archivo alterado se rechaza; constante respaldada por configuración.

**Procedimiento:** 1. Del finding seguir trace.field→registro→SourceRef. 2. Verificar SHA y localizar celda. 3. Contrastar raw→transform→value, incluidas constantes.

**Oráculo:** OR-04 OR-06. **Lo que puede escapar:** Hash correcto de archivo no demuestra referencia a la celda correcta.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_csv_argentine_numbers_zeroes_and_provenance tests/test_storage_reporting.py::test_tampered_source_detected
```

## QA-16 — Selección única de vigencia

**Obligación:** Extremos inclusivos; cero/dos versiones o grupo mixto→UNDETERMINABLE; no elegir primera ni prorratear.

**Procedimiento:** 1. Evaluar comienzo/fin/día siguiente. 2. Crear overlap/gap. 3. Invertir orden de versiones. 4. Consolidar fechas de ambos lados.

**Oráculo:** OR-05. **Lo que puede escapar:** Dos versiones con mismo precio ocultan selector equivocado.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_version_boundaries tests/test_engine.py::test_overlapping_versions_never_pick_first tests/test_engine.py::test_group_mixed_version_is_undeterminable
```

## QA-17 — Fecha civil y seriales de Excel

**Obligación:** Ambigua/invalid/hora/zona→rechazo; medianoche ingenua admitida. Serial ficticio60 del calendario1900 se rechaza; serial60 de1904 es01/03/1904.

**Procedimiento:** 1. Importar cada par fuente→fecha esperada. 2. Repetir con TZs distintas. 3. Comparar versión seleccionada con calendario manual.

**Oráculo:** OR-04 OR-05. **Lo que puede escapar:** Comparar sólo date final pierde serial/epoch original.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_ambiguous_date_is_rejected tests/test_importing.py::test_excel_fictitious_leap_day_never_aliases_real_date tests/test_importing.py::test_timestamps_are_not_silently_truncated tests/test_engine.py::test_alternate_date_field
```

## QA-18 — Reglas/condiciones y AST acotado

**Obligación:** AST inválido rechaza;0/2reglas→UNDETERMINABLE; if no evalúa rama no elegida; condición faltante no es false.

**Procedimiento:** 1. Validar AST inválidos. 2. Evaluar datos faltantes. 3. Probar rama no elegida con división0. 4. Repetir reglas reordenadas.

**Oráculo:** OR-01 OR-05. **Lo que puede escapar:** Test AST parseado no prueba aridad/semántica de cada operador.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_condition_missing_is_not_false tests/test_engine.py::test_condition_branch_is_lazy tests/test_engine.py::test_overlapping_rules_are_undeterminable tests/test_adversarial.py::test_bounded_expression_depth_rejects_nested_attack
```

## QA-19 — Lookup/bandas sin desempate arbitrario

**Obligación:** Bandas[lower,upper); exactamente1coincidencia. Cero/dos incluso mismo importe→UNDETERMINABLE; caché separada por versión/acuerdo.

**Procedimiento:** 1. Evaluar ambos lados y límite exacto. 2. Repetir filas. 3. Invertir tabla. 4. Intercalar versión con tabla homónima diferente.

**Oráculo:** OR-05. **Lo que puede escapar:** Mismo valor en tablas distintas oculta contaminación de caché.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_band_overlap_and_gap_never_select_arbitrarily tests/test_adversarial.py::test_duplicate_lookup_rows_even_same_price_are_ambiguous
```

## QA-20 — Claves, aliases y vínculos explícitos

**Obligación:** Match exacto declarado; vacíos no empatan; link ausente/repetido/carrier ajeno→UNDETERMINABLE. Contradicción link/claves requiere control adicional pendiente.

**Procedimiento:** 1. Dibujar grafo manual. 2. Aplicar alias sólo al cargo. 3. Vaciar clave. 4. Añadir link inválido y verificar sin fallback.

**Oráculo:** OR-05. **Lo que puede escapar:** Explicito válido estructuralmente puede apuntar a operación equivocada.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_composite_keys_and_directional_alias tests/test_engine.py::test_invalid_explicit_link_never_falls_back tests/test_adversarial.py::test_empty_keys_never_join_to_empty_keys
```

## QA-21 — Ambigüedad propagada a grupos parciales

**Obligación:** Antes: ambos REVIEW/confirmada0; después, si C1+C2→S1, grupoA100,E100 PASS. Ningún cargo se pierde.

**Procedimiento:** 1. Auditar en ambos órdenes. 2. Inspeccionar los dos findings. 3. Resolver C2 explícitamente y volver a auditar nueva copia.

**Oráculo:** OR-03 OR-05. **Lo que puede escapar:** Revisar sólo cargo ambiguo deja FAIL parcial en el otro.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_ambiguous_allocation_also_blocks_related_partial_group tests/test_engine.py::test_matching_ambiguity_is_review
```

## QA-22 — Consolidado y cargos por componentes

**Obligación:** UnE60,A60 PASS; split no repiteE. attr de pesos distintos→UNDETERMINABLE; no prorrateo automático.

**Procedimiento:** 1. Auditar sum×2. 2. Dividir/reunir líneas actual. 3. Cambiar sum por attr sobre pesos distintos. 4. Comparar scopes, no IDs hash.

**Oráculo:** OR-02 OR-03 OR-08. **Lo que puede escapar:** N→M solapado no se cubre con N→1.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_group_sum_and_one_expected_charge tests/test_engine.py::test_multiple_lines_aggregate_without_inventing_duplicates
```

## QA-23 — Asignaciones superpuestas y servicios parciales

**Obligación:** Grupos superpuestos REVIEW; no multiplicar expected confirmado. Servicio parcial no representado se bloquea hasta definir regla.

**Procedimiento:** 1. Construir grafo con intersecciónS2. 2. Auditar. 3. Verificar grupo relacionado no confirma ni reparte. 4. Confirmar límite contractual con operador.

**Oráculo:** OR-05. **Lo que puede escapar:** Solapamiento a través de acuerdos distintos requiere revisión contractual.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_overlap_allocations_are_review
```

## QA-24 — Duplicados candidatos y remito legítimo

**Obligación:** Candidatos→REVIEW, no eliminación ni ahorro; sin política líneas agregadas; distinto concepto no es duplicado por referencia sola.

**Procedimiento:** 1. Auditar con duplicate_fields. 2. Desactivar sólo esa política. 3. Separar conceptos y verificar conservación.

**Oráculo:** OR-03 OR-05. **Lo que puede escapar:** No configurar duplicate_fields no demuestra ausencia de duplicados reales.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_configured_duplicate_is_candidate_only tests/test_engine.py::test_same_remittance_different_concepts_is_not_duplicate
```

## QA-25 — Evidencia por ámbito y adición selectiva

**Obligación:** Faltante→REVIEW; evidencia suficiente sólo resuelve scope pertinente; nueva corrida puede PASS o FAIL según Δ, historia intacta.

**Procedimiento:** 1. Retirar un respaldo por ámbito. 2. Agregar sólo el faltante. 3. Comparar grupos no relacionados y run original. 4. Retirar documento obligatorio.

**Oráculo:** OR-05 OR-08. **Lo que puede escapar:** Sólo kind sin revisar asociaciones/document_hash es falso respaldo.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_evidence_any_of_and_per_operation tests/test_engine.py::test_unrelated_evidence_cannot_support_charge
```

## QA-26 — Cobertura explícita de cargos ausentes

**Obligación:** Sin scope no inventar; scope correcto→REVIEW A0 sin confirmada; whenfalse omite expectativa; no duplica cargo sin versión; scope inválido rechaza.

**Procedimiento:** 1. Comparar sin/con coverage. 2. Probar when=false. 3. Agregar cargo ya indeterminado. 4. Validar scope inválido.

**Oráculo:** OR-03 OR-05. **Lo que puede escapar:** Creer que cobertura detecta documento faltante no aportado.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_missing_expected_charge_requires_explicit_scope_and_is_review tests/test_adversarial.py::test_missing_coverage_must_not_duplicate_existing_undetermined_charge tests/test_adversarial.py::test_coverage_cannot_silently_drop_wrong_carrier
```

## QA-27 — Conservación total por ID y moneda

**Obligación:** Cada C exactamente1vez; bruto por moneda preservado; +50 y−75 separados y neto−25. Checker rechaza salida manipulada.

**Procedimiento:** 1. Checker recompone Counter de charge_ids y sumas desde C. 2. Comparar todos los buckets/counts. 3. Mutar salida duplicando/quitando cargo.

**Oráculo:** OR-03. **Lo que puede escapar:** Totales coincidentes pueden ocultar omisión y duplicación compensadas: contar IDs.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption
```

## QA-28 — Determinismo y transformaciones

**Obligación:** Reordenamiento normalizado completo igual; renombre/columna economía igual aunque snapshot hash cambie; cambio futuro no muta run guardado.

**Procedimiento:** 1. Guardar baseline completo. 2. Aplicar una transformación. 3. Comparar resultado o economic_projection según tabla. 4. Comprobar fuente hash cambia cuando bytes cambian.

**Oráculo:** OR-08. **Lo que puede escapar:** Dos errores idénticos satisfacen relación; combinar OR02/03.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_property_arbitrary_row_permutation tests/test_engine.py::test_semantic_hash_ignores_incidental_label tests/test_qa_infrastructure.py::test_generated_uncertainty_and_metamorphism
```

## QA-29 — Aislamiento entre clientes y catálogos

**Obligación:** A idéntico, fuentes/configs separadas por DB. Catálogo global dentro mismaDB no es aislamiento multiempresa; no habilitarlo como tal.

**Procedimiento:** 1. EjecutarA/B/A en proceso. 2. Reabrir DBs y comparar A. 3. Intentar selección de config ajena en UI y revisar operación.

**Oráculo:** OR-05 OR-06 OR-08. **Lo que puede escapar:** DatosconIDsdistintos nunca ejercitan colisión/caché compartida.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_backlog_p0_p1.py::test_qa29_client_catalog_and_storage_isolation
```

## QA-30 — Decisiones humanas y cadena

**Obligación:** Resultado original idéntico; decisiones append-only ordenadas/hash enlazado; referencias inexistentes rechazadas.

**Procedimiento:** 1. Guardar hash de resultado. 2. Añadir decisiones en orden/concurrentes. 3. Verificar chain/resultado. 4. Intentar referencias ajenas.

**Oráculo:** OR-06. **Lo que puede escapar:** Cadena local no detecta truncamiento de sufijo sin ancla externa.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_human_decision_never_rewrites_finding tests/test_storage_reporting.py::test_decision_chain_serializes_concurrent_writers tests/test_storage_reporting.py::test_no_unknown_decision_or_evidence
```

## QA-31 — Integridad histórica y mutación

**Obligación:** Writes históricos bloqueados; load detecta hashes; configuración futura no cambia run. list_runs no verifica integridad: deuda visible, no oráculo.

**Procedimiento:** 1. Guardar ancla externa. 2. Intentar mutación. 3. Comparar load y list_runs ante byte alterado. 4. Abrir original intacto.

**Oráculo:** OR-06. **Lo que puede escapar:** Rehash malicioso total o truncamiento puede pasar sin copia externa.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_db_update_delete_blocked tests/test_storage_reporting.py::test_tampered_result_detected_after_trigger_bypass tests/test_storage_reporting.py::test_changed_agreement_preserves_history
```

## QA-32 — Replay y cambio de artefacto

**Obligación:** Mismo artefacto: resultado exacto. Integridad fallida, artefacto distinto o proceso desactualizado bloquean replay. Reimportar es otra operación.

**Procedimiento:** 1. Replay original. 2. Alterar fuente/snapshot en copia. 3. Cambiar artifact o código cargado. 4. Confirmar que no reescribe resultado.

**Oráculo:** OR-06 OR-08. **Lo que puede escapar:** Replay perfecto perpetúa error de importer previo.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_save_replay_and_idempotency tests/test_storage_reporting.py::test_engine_artifact_change_blocks_replay tests/test_storage_reporting.py::test_source_update_requires_process_restart
```

## QA-33 — Proveniencia de ejecutables y alcance

**Obligación:** Unknown no se excluye; config y trace consultadas; cliente declarado externamente; no escribir schema/triggers ni inventar huellas pasadas.

**Procedimiento:** 1. Ejecutar impact con --feature const y --importer-hash distinto. 2. Conservar desconocidos como candidatos. 3. Contrastar inventario manual. 4. Comparar bytes de la base antes/después.

**Oráculo:** OR-05 OR-06. **Lo que puede escapar:** Filtrar sólo trace pierde errores previos a calcular.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_impact_is_read_only_and_retains_unknowns
```

## QA-34 — Backup, restore y reapertura

**Obligación:** Copia consistente y mismas corridas; overwrite rechazado; original intacto. Copia fuera del equipo exige operación real.

**Procedimiento:** 1. Crear backup con la API. 2. Restaurar en otra ruta. 3. Verificar inventario, hashes, decisiones, fuentes y replay con el artefacto original. 4. Intentar sobrescribir el destino existente.

**Oráculo:** OR-06 OR-10. **Lo que puede escapar:** Backup sobre mismo disco no cubre pérdida del equipo.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_migration_reopening_and_consistent_backup
```

## QA-35 — Crash, rollback y concurrencia

**Obligación:** Run completo o ausente, cadena íntegra; busy error recuperable. Fuentes huérfanas pueden existir y no son pérdida histórica; export incompleto no se presenta como completo.

**Procedimiento:** 1. Inyectar fallo en frontera transaccional. 2. Reabrir copia. 3. Inventariar completos/ausentes y fuentes huérfanas. 4. Validar no corrida parcial visible.

**Oráculo:** OR-06 OR-10. **Lo que puede escapar:** Thread test de decisiones no cubre kill de proceso o full disk.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_decision_chain_serializes_concurrent_writers
```

## QA-36 — Schema y migración recuperable

**Obligación:** Vacía inicializa schema 1; versión futura se rechaza; v1 reabre sin cambios. v0 no vacío o incompleto requiere validación pendiente. No se certifica una migración real.

**Procedimiento:** 1. Abrir copias de cada estado. 2. Para una futura migración: preservar backup con hash externo, interrumpir antes/después de cada DDL y restaurar/reintentar. 3. Comparar corridas históricas y originales.

**Oráculo:** OR-06. **Lo que puede escapar:** Una prueba de reopen no cubre atomicidad del DDL.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_newer_database_schema_is_not_opened tests/test_storage_reporting.py::test_migration_reopening_and_consistent_backup
```

## QA-37 — Reconciliación entre representaciones

**Obligación:** Campos materiales exactos; filas completas y sin fórmulas. API y DOM sólo se cubren al aportar capturas independientes. Un canal ausente queda pendiente.

**Procedimiento:** 1. Verificar integridad e invariantes. 2. Leer salidas con lectores independientes. 3. Comparar filas, monedas, estados, importes y resúmenes. 4. Alterar cada salida por separado y exigir detección.

**Oráculo:** OR-03 OR-07. **Lo que puede escapar:** Conciliar salidas iguales no prueba que el core aplicó contrato correcto.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_cross_report_reconciliation_and_tamper_detection
```

## QA-38 — Límites de reportes y contenido activo

**Obligación:** No se entrega un XLSX parcial; texto explícito sin fórmulas; JSON íntegro y advertencia de omisión conservada.

**Procedimiento:** 1. Exportar. 2. Revisar tipos y cantidad de celdas. 3. Forzar límite y verificar ZIP sin XLSX, advertencia explícita y JSON completo. 4. Inspeccionar escape del HTML.

**Oráculo:** OR-07 OR-09. **Lo que puede escapar:** Probar un límite reducido no mide la memoria real para 100000 filas.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_workbook_is_real_and_has_exact_money_and_no_formulas tests/test_storage_reporting.py::test_report_escapes_untrusted_html_and_excel_formula tests/test_storage_reporting.py::test_excel_long_cell_is_not_silently_truncated tests/test_storage_reporting.py::test_excel_row_limit_preserves_full_bundle_json
```

## QA-39 — UI conserva semántica visible y estado actual

**Obligación:** Dinero sin conversión a Number/float; paginación y filtros no cambian métricas globales. Estado del motor y decisión separados; solicitudes sólo a loopback.

**Procedimiento:** 1. Capturar DOM de todas las páginas y filtros. 2. Cambiar rápidamente de corrida, abrir detalle y registrar decisión. 3. Comparar valores y etiquetas con la corrida exacta. 4. Probar importes con cero y tres decimales.

**Oráculo:** OR-07 OR-09. **Lo que puede escapar:** Una respuesta exitosa de API no prueba qué leyó el operador.


Runner adicional; usar un directorio de evidencia nuevo:

```bash
.venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/qa39-new
```

## QA-40 — Barrera de red local

**Obligación:** Host, Origin o token incorrectos se rechazan; CORS sin orígenes ajenos; servicio sólo en loopback. Un rechazo con efectos previos en la base es un fallo.

**Procedimiento:** 1. Enviar POST con y sin token y Origin válidos. 2. Verificar bind a 127.0.0.1 en el proceso CLI. 3. Probar lectura desde otro origen en navegador. 4. Inspeccionar efectos en la base.

**Oráculo:** OR-09. **Lo que puede escapar:** El E2E de Chromium/Linux no prueba firewall ni aislamiento frente a otros usuarios del equipo; falta matriz Windows.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_local_api_security_boundary
```

Runner adicional; usar un directorio de evidencia nuevo:

```bash
.venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/qa40-new
```

## QA-41 — Rutas, archivos y sobrescritura

**Obligación:** Uploads identificados por hash; sin lectura ni escritura arbitrarias; sobrescritura rechazada. Verificar política de enlaces simbólicos antes de usar rutas compartidas.

**Procedimiento:** 1. Subir un archivo con nombre hostil. 2. Exportar y crear backup en destinos temporales existentes y enlaces simbólicos. 3. Verificar el testigo y archivos modificados. 4. Usar sólo datos sintéticos.

**Oráculo:** OR-09. **Lo que puede escapar:** La comprobación de enlaces no detiene a otro proceso del mismo usuario que cambie directorios durante la escritura; falta ejecutar la matriz nativa Windows.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_security_paths.py::test_export_rejects_existing_and_redirected_directories tests/test_security_paths.py::test_foreign_platform_drive_syntax_is_not_a_local_relative_output tests/test_security_paths.py::test_backup_publishes_only_completed_copy_without_overwrite tests/test_security_paths.py::test_export_marks_interrupted_or_invalid_package tests/test_integration.py::test_upload_filename_is_only_a_label_and_never_an_output_path
```

## QA-42 — XML/ZIP malicioso acotado

**Obligación:** Sin ejecución de contenido, red ni lectura externa; error recuperable; ninguna corrida económica parcial. Archivos sintéticos y acotados.

**Procedimiento:** 1. Generar un archivo sintético pequeño. 2. Ejecutar en subproceso sin red y con límites. 3. Registrar rechazo, salidas, red y testigo. 4. Verificar expansión efectiva y cabecera.

**Oráculo:** OR-09. **Lo que puede escapar:** DTD y ZIP ambiguo sintéticos no prueban todos los productores XML ni el pico de descompresión real bajo un límite de proceso.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified tests/test_importing.py::test_xlsx_duplicate_or_traversal_entry_is_rejected tests/test_importing.py::test_xlsx_external_entity_never_becomes_imported_value
```

## QA-43 — Errores de API y consistencia de operación

**Obligación:** Error recuperable sin traceback para el usuario; ninguna corrida parcial; mismo resultado económico por CLI/API; sin datos sensibles expuestos.

**Procedimiento:** 1. Registrar inventario de la base. 2. Enviar petición inválida. 3. Comparar fuentes y configuraciones conservadas con corridas creadas. 4. Enviar entrada válida y contrastar con CLI.

**Oráculo:** OR-03 OR-07. **Lo que puede escapar:** Comprobar sólo el código de respuesta ignora el cuerpo y los efectos persistidos.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_api_configuration_errors_use_recoverable_messages tests/test_integration.py::test_api_runs_decisions_export_replay tests/test_integration.py::test_api_import_with_mapping_and_provenance
```

## QA-44 — Auditoría sin servicios externos

**Obligación:** Auditoría y exportaciones íntegras sin red; UI sólo en loopback. Evaluar instalación inicial de dependencias por separado.

**Procedimiento:** 1. Bloquear conexiones externas para core y CLI. 2. Importar, auditar, exportar y reproducir. 3. Navegar la UI y revisar destinos de todas las solicitudes.

**Oráculo:** OR-09. **Lo que puede escapar:** Interceptar sockets de Python no cubre subprocesos ni navegador.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_fully_offline_core
```

## QA-45 — Representación contractual y mapping aprobados

**Obligación:** Toda regla material tiene responsable y ejemplo independiente; desconocido bloquea certeza, no default de industria.

**Procedimiento:** 1. Aplicar pasos 1–10 del protocolo de cliente real. 2. Calcular hoja manual antes de ejecutar el motor. 3. Confirmar representación con el cliente. 4. Preservar hashes y dudas.

**Oráculo:** OR-01 OR-04. **Lo que puede escapar:** Tests sintéticos pueden pasar con contrato equivocado.

Sin selector automatizado: ejecutar el procedimiento y conservar evidencia antes de cerrar.

## QA-46 — Generalidad de cinco arquetipos

**Obligación:** A: 31.5; B: 900; C: bandas, pallets y evidencia; D: 194.25 USD; E: 100 + 12 con acuerdos separados sólo si representan el contrato. Sin condiciones por cliente, sector o transportista en el core.

**Procedimiento:** 1. Configurar sin cambiar el core. 2. Calcular manualmente. 3. Ejecutar y registrar archivos modificados. 4. Si E no puede representarse fielmente, documentar la abstracción faltante.

**Oráculo:** OR-01 OR-05. **Lo que puede escapar:** El test existente no ejercita el quinto arquetipo E.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_real_files_three_agreements_golden_and_second_client
```

## QA-47 — Paquete y plataforma real

**Obligación:** Importación desde paquete instalado sin modo editable; recursos completos y equivalencia económica. Windows pendiente hasta probarlo en una máquina real.

**Procedimiento:** 1. Instalar paquete aislado. 2. Comprobar recursos UI, demo, replay y exportación. 3. Comparar contenidos y hashes. 4. En Windows: rutas Unicode, longitudes, saltos de línea y Excel real.

**Oráculo:** OR-04 OR-06 OR-07. **Lo que puede escapar:** Instalar wheel y sdist en Linux no valida rutas ni Excel de escritorio en Windows.


Runner adicional; usar un directorio de evidencia nuevo:

```bash
.venv/bin/python scripts/verify_delivery.py --output output/delivery-verification.json
```

## QA-48 — Escala, memoria y tiempos de todas las etapas

**Obligación:** Sin pérdida ni resultado incorrecto y dentro del presupuesto operativo acordado. Las mediciones históricas del core en VERIFICATION.md no constituyen un SLA de todo el flujo.

**Procedimiento:** 1. Un proceso por tamaño con memoria base registrada. 2. Medir importación, motor, hashes, persistencia, exportación y UI por separado. 3. Conciliar cantidades y sumas al terminar.

**Oráculo:** OR-03 OR-10. **Lo que puede escapar:** El pipeline de 1000 cargos no extrapola 50000/100000 ni mide un navegador con esos hallazgos.


Runner adicional; usar un directorio de evidencia nuevo:

```bash
.venv/bin/python output/e2e/platform_scale/benchmark_runner.py --sizes 1000 --reps 1 --skip-curve --all-exports --output-dir output/qa48-small
```

## QA-49 — Los verificadores detectan corrupción

**Obligación:** Cada alteración objetivo se detecta. qa/reference.py y qa/invariants.py no importan lógica productiva. El CLI conserva sus validaciones con Python optimizado.

**Procedimiento:** 1. Exigir resultado limpio para la base válida. 2. Alterar una causa por copia. 3. Exigir error identificable y salida 1. 4. Probar entrada malformada con salida 2.

**Oráculo:** OR-01 OR-03 OR-07. **Lo que puede escapar:** Aceptar una corrida correcta no demuestra que el verificador detecte una incorrecta.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption tests/test_qa_infrastructure.py::test_cross_report_reconciliation_and_tamper_detection
```

## QA-50 — Mutantes críticos dirigidos

**Obligación:** Mutaciones de signo, tolerancia, moneda, versión y evidencia deben fallar por aserción causal. Un sobreviviente bloquea la función afectada hasta investigar. Incompetente o inconcluso no cuenta como detectado.

**Procedimiento:** 1. Validar ancla única. 2. Ejecutar tests base en copia temporal. 3. Aplicar un mutante. 4. Ejecutar sus selectores. 5. Exigir fallo de aserción causal; colección fallida o timeout es inconcluso.

**Oráculo:** OR-01 OR-05. **Lo que puede escapar:** La señal causal exigida vale para estos diez mutantes; no demuestra que todas las defensas tengan un mutante dirigido.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_mutation_verdict.py::test_mutant_verdict_requires_selected_causal_assertion
```

Runner adicional; usar un directorio de evidencia nuevo:

```bash
.venv/bin/python scripts/qa.py mutate --execute
```

## QA-51 — Validación ciega con cliente

**Obligación:** Contraste externo documentado; diferencia nueva correcta no equivale a dinero recuperado. Conservar primera corrida antes de ajustar tras conocer las respuestas.

**Procedimiento:** 1. Congelar representación y corrida antes de ver control histórico. 2. Comparar por cargo y moneda. 3. Resolver falsos PASS/FAIL y diferencias conocidas, nuevas o desconocidas. 4. Registrar horas de trabajo.

**Oráculo:** OR-01 OR-04. **Lo que puede escapar:** El control histórico también puede estar equivocado; resolver diferencias con evidencia independiente.

Sin selector automatizado: ejecutar el procedimiento y conservar evidencia antes de cerrar.

## QA-52 — Gate de pago sin nuestra supervisión

**Obligación:** Gate U cerrado para 0.1.0. Ninguna estadística sintética lo habilita; pytest no sustituye confirmación del contrato.

**Procedimiento:** 1. Evaluar cada requisito del Gate U. 2. Registrar pendientes, incidentes y desconocidos. 3. Comprobar restricciones efectivas, restauración, identidad y conciliación del total documental.

**Oráculo:** OR-01 OR-06 OR-10. **Lo que puede escapar:** Confundir piloto supervisado con habilitación para decidir pagos sin revisión.

Sin selector automatizado: ejecutar el procedimiento y conservar evidencia antes de cerrar.

## QA-53 — IDs y JSON inequívocos

**Obligación:** Claves repetidas, números no finitos y campos extra rechazados; ninguna política silenciosa de conservar última fila; duplicados de importación visibles.

**Procedimiento:** 1. Leer JSON con parser del producto. 2. Validar duplicados por entidad. 3. Verificar rechazos visibles de importación. 4. Probar lector JSON estricto del verificador.

**Oráculo:** OR-04. **Lo que puede escapar:** Un parser permisivo en QA puede aceptar lo que el producto rechaza.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_duplicate_json_keys_are_rejected tests/test_importing.py::test_duplicate_business_ids_visible_not_silently_deduplicated
```

## QA-54 — Bundle portable y ancla externa

**Obligación:** Alteraciones detectadas respecto del ancla; un manifest consistente consigo mismo no prueba autenticidad. Declarar metadata no cubierta por hashes.

**Procedimiento:** 1. Verificar manifest, corrida, cadena de decisiones y fuentes. 2. Comparar hash del ZIP con ancla externa. 3. Alterar un componente por copia. 4. Verificar sin extraer rutas controladas por el archivo.

**Oráculo:** OR-06 OR-09. **Lo que puede escapar:** Un atacante puede recalcular todos los hashes; sin ancla independiente no hay autenticación.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_portable_bundle_integrity
```

## QA-55 — Entrega reproducible y dependencias

**Obligación:** Código entregado igual al verificado; cada original conserva hash de sus bytes; secretos, bases y salidas fuera de Git. No presumir builds idénticos sin comprobar reproducibilidad.

**Procedimiento:** 1. Comparar árbol versionado y archivos materiales. 2. Instalar y probar en checkout limpio. 3. Registrar hashes del paquete y dependencias. 4. Verificar equivalencia de parsing con LF sin exigir SHA del original CRLF.

**Oráculo:** OR-06 OR-08. **Lo que puede escapar:** Las instalaciones aisladas en Linux no prueban Excel de escritorio, distribución firmada ni hashes de terceros en el lock.


Runner adicional; usar un directorio de evidencia nuevo:

```bash
.venv/bin/python scripts/verify_delivery.py --output output/delivery-verification.json
```

## QA-56 — Separación de liquidaciones y alcance de obligación

**Obligación:** L1 y L2 conservan hallazgos separados. Si reutilizan la misma operación/concepto: REVIEW y confirmada0; otra liquidación no prueba otro servicio. Operaciones distintas correctamente vinculadas pueden ser PASS. La asignación entre facturas requiere representación contractual explícita.

**Procedimiento:** 1. Revisar group_key y contrato. 2. Auditar sin período en clave. 3. Representar período y servicio explícitos con operaciones correctas. 4. Comparar grafo de obligaciones manual.

**Oráculo:** OR-01 OR-05. **Lo que puede escapar:** Fixtures de un único período no ejercitan este error causal.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_review_regressions.py::test_rebilling_same_operation_in_other_invoice_is_not_independent_pass tests/test_review_regressions.py::test_separate_operations_on_separate_invoices_still_pass
```

## QA-57 — Diagnóstico no muta evidencia

**Obligación:** No invocar Store, crear bases ni instalar triggers. La corrupción nunca produce una selección vacía que aparente ausencia de impacto.

**Procedimiento:** 1. Ejecutar impact en sólo lectura. 2. Intentar ruta inexistente. 3. Comparar bytes, schema y triggers antes/después. 4. Corrupción debe aparecer como unknown o error global explícito.

**Oráculo:** OR-06 OR-09. **Lo que puede escapar:** Comprobar sólo mtime no demuestra ausencia de modificaciones.

Comando del subconjunto automatizado:

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_impact_is_read_only_and_retains_unknowns
```

## QA-58 — Píxel exacto y matrices visuales exhaustivas

**Obligación:** Diferir matriz estética exhaustiva. Cualquier importe o etiqueta ocultos se clasifican como QA-39/P0.

**Procedimiento:** 1. Diferir igualdad exacta de píxeles. 2. Cubrir texto, contraste y desbordamiento material en QA-39. 3. Reconsiderar ante fallo real de lectura.

**Oráculo:** OR-07. **Lo que puede escapar:** Diferir pruebas cosméticas no permite ocultar moneda o estado.

Sin selector automatizado: ejecutar el procedimiento y conservar evidencia antes de cerrar.
