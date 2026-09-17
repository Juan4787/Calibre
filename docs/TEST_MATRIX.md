# Matriz maestra de verificación

Generada desde `qa/catalog.py` con `.venv/bin/python scripts/qa.py matrix --generate`. Editar el catálogo, no esta vista. `parcial` significa que los selectores cubren sólo parte de los casos descritos; `nuevo` tampoco significa certificación completa. Pasos base en QA_CASES.md, oráculos en TEST_ORACLES.md y respuesta común obligatoria en INCIDENT_RESPONSE.md.

Seleccionar: `.venv/bin/python scripts/qa.py matrix --priority P0 P1`. Ejecutar sólo cobertura existente: añadir `--run-existing`; salida3 indica familias pendientes aunque sus selectores pasen. No tomarla como gate aprobado.

| ID | Familia | Severidad | Prioridad / grupo | Cobertura | Riesgo / costo |
|---|---|---|---|---|---|
| [QA-01](#qa-01) | Certeza y diferencia confirmada | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-02](#qa-02) | Tolerancia, signo y fronteras | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-03](#qa-03) | Referencia de precio independiente | CRITICAL | P0 / A | nuevo | 60 / 30 |
| [QA-04](#qa-04) | Dominio numérico y tipos estrictos | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-05](#qa-05) | Redondeo, escala y orden | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-06](#qa-06) | División y contexto ambiental | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-07](#qa-07) | Unidades y monedas separadas | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-08](#qa-08) | Números desde originales | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-09](#qa-09) | Identidad y normalización declarada | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-10](#qa-10) | Estructura CSV y conservación de filas | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-11](#qa-11) | Semántica de libro Excel | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-12](#qa-12) | XLS legacy y cache explícito | HIGH | P1 / A | parcial | 48 / 12 |
| [QA-13](#qa-13) | Límites de importación y corrupción | HIGH | P1 / B | parcial | 48 / 6 |
| [QA-14](#qa-14) | Importación incompleta y alcance documental | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-15](#qa-15) | Procedencia verificable | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-16](#qa-16) | Selección única de vigencia | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-17](#qa-17) | Fecha civil y seriales de Excel | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-18](#qa-18) | Reglas/condiciones y AST acotado | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-19](#qa-19) | Lookup/bandas sin desempate arbitrario | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-20](#qa-20) | Claves, aliases y vínculos explícitos | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-21](#qa-21) | Ambigüedad propagada a grupos parciales | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-22](#qa-22) | Consolidado y cargos por componentes | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-23](#qa-23) | Asignaciones superpuestas y servicios parciales | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-24](#qa-24) | Duplicados candidatos y remito legítimo | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-25](#qa-25) | Evidencia por ámbito y adición selectiva | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-26](#qa-26) | Cobertura explícita de cargos ausentes | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-27](#qa-27) | Conservación total por ID y moneda | CRITICAL | P0 / A | nuevo | 60 / 30 |
| [QA-28](#qa-28) | Determinismo y transformaciones | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-29](#qa-29) | Aislamiento entre clientes y catálogos | CRITICAL | P0 / A | diseñado | 60 / 15 |
| [QA-30](#qa-30) | Decisiones humanas y cadena | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-31](#qa-31) | Integridad histórica y mutación | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-32](#qa-32) | Replay y cambio de artefacto | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-33](#qa-33) | Proveniencia de ejecutables y alcance | CRITICAL | P0 / A | nuevo | 60 / 30 |
| [QA-34](#qa-34) | Backup, restore y reapertura | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-35](#qa-35) | Crash, rollback y concurrencia | CRITICAL | P0 / B | parcial | 60 / 7.5 |
| [QA-36](#qa-36) | Schema y migración recuperable | CRITICAL | P0 / B | parcial | 60 / 7.5 |
| [QA-37](#qa-37) | Reconciliación entre representaciones | CRITICAL | P0 / A | nuevo | 60 / 15 |
| [QA-38](#qa-38) | Límites de reportes y contenido activo | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-39](#qa-39) | UI conserva semántica visible y estado actual | CRITICAL | P0 / A | diseñado | 60 / 15 |
| [QA-40](#qa-40) | Barrera de red local | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-41](#qa-41) | Rutas, archivos y sobrescritura | CRITICAL | P0 / A | diseñado | 60 / 15 |
| [QA-42](#qa-42) | XML/ZIP malicioso acotado | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-43](#qa-43) | Errores de API y consistencia de operación | HIGH | P1 / A | parcial | 48 / 24 |
| [QA-44](#qa-44) | Auditoría sin servicios externos | HIGH | P1 / A | parcial | 48 / 24 |
| [QA-45](#qa-45) | Representación contractual y mapping aprobados | CRITICAL | P0 / A | diseñado | 60 / 15 |
| [QA-46](#qa-46) | Generalidad de cinco arquetipos | HIGH | P1 / A | parcial | 48 / 12 |
| [QA-47](#qa-47) | Paquete y plataforma real | HIGH | P1 / B | diseñado | 48 / 6 |
| [QA-48](#qa-48) | Escala, memoria y tiempos de todas las etapas | HIGH | P2 / B | diseñado | 48 / 6 |
| [QA-49](#qa-49) | Los verificadores detectan corrupción | CRITICAL | P0 / A | nuevo | 60 / 30 |
| [QA-50](#qa-50) | Mutantes críticos dirigidos | CRITICAL | P0 / A | nuevo | 60 / 15 |
| [QA-51](#qa-51) | Validación ciega con cliente | CRITICAL | P0 / B | diseñado | 60 / 7.5 |
| [QA-52](#qa-52) | Gate de pago sin nuestra supervisión | CRITICAL | P0 / B | diseñado | 60 / 7.5 |
| [QA-53](#qa-53) | IDs y JSON inequívocos | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-54](#qa-54) | Bundle portable y ancla externa | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-55](#qa-55) | Entrega reproducible y dependencias | HIGH | P1 / B | diseñado | 48 / 12 |
| [QA-56](#qa-56) | Separación de liquidaciones y alcance de obligación | CRITICAL | P0 / A | diseñado | 60 / 15 |
| [QA-57](#qa-57) | Diagnóstico no muta evidencia | CRITICAL | P0 / A | nuevo | 60 / 30 |
| [QA-58](#qa-58) | Píxel exacto y matrices visuales exhaustivas | LOW | P3 / C | diferido | 2 / 0.25 |

## QA-01

- **TEST_ID:** QA-01
- **NOMBRE:** Certeza y diferencia confirmada
- **COMPONENTE:** engine/summary
- **RIESGO:** Falta de respaldo se convierte en discrepancia objetiva
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-01 INV-10 INV-11
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** B; A=200,E=100; requisito approval ausente; repetir con issue row y con versión ausente
- **PASOS_EXACTOS:** 1. Auditar cada variante por separado. 2. Inspeccionar finding y todos los buckets. 3. Pasar run al checker independiente.
- **RESULTADO_ESPERADO:** Sin evidencia: REVIEW,E100,Δ100,confirmada0; issue row impide PASS/FAIL; sin versión UNDETERMINABLE/E null. Ningún bucket confirma100.
- **ORACULO:** OR-03 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Una decisión APPROVED posterior no cambia status del motor.
- **FALSOS_NEGATIVOS:** Comprobar sólo finding y no summary/reportes deja escapar dinero confirmado.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-03 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_missing_evidence_does_not_confirm_even_numeric_difference; tests/test_engine.py::test_import_rejects_block_economic_confirmation
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_missing_evidence_does_not_confirm_even_numeric_difference tests/test_engine.py::test_import_rejects_block_economic_confirmation
```

## QA-02

- **TEST_ID:** QA-02
- **NOMBRE:** Tolerancia, signo y fronteras
- **COMPONENTE:** comparison
- **RIESGO:** PASS fuera de tolerancia o FAIL en el límite
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-02 INV-03
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** B y N05,N06,N07; E=100/200; límites positivos y negativos
- **PASOS_EXACTOS:** 1. Ejecutar A=T exacta y T±0.01 respecto de E. 2. Recalcular T y Δ con Fraction. 3. Revisar PASS/FAIL y neto/brutos.
- **RESULTADO_ESPERADO:** E100,T0.01,A100.01 PASS;100.02 FAIL+0.02;99.98 FAIL−0.02. E200,rel0.05,A210 PASS;210.01 FAIL10.01.
- **ORACULO:** OR-01 OR-02
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Confundir Δ calculada de un PASS con confirmada0.
- **FALSOS_NEGATIVOS:** Tolerancia relativa, negativo o igualdad exacta no ejercitados.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; mutation
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-01 IR-02 IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_tolerance_and_signed_differences; tests/test_qa_infrastructure.py::test_generated_reference_prices
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_tolerance_and_signed_differences tests/test_qa_infrastructure.py::test_generated_reference_prices
```

## QA-03

- **TEST_ID:** QA-03
- **NOMBRE:** Referencia de precio independiente
- **COMPONENTE:** rules
- **RIESGO:** Fórmula incorrecta coincide con golden generado por el mismo motor
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-03 INV-14 INV-15
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** N08,N09; casos generados unit/min/percent; anclas31.5 y42
- **PASOS_EXACTOS:** 1. Comprobar anclas de referencia. 2. Generar q/tarifa/mínimo/factor. 3. Comparar E con referencia racional sin importar helpers productivos.
- **RESULTADO_ESPERADO:** q10×2,min30,+5%→31.5; q20→42. Igual E y A no produce FAIL; cambiar A no cambia E.
- **ORACULO:** OR-01 OR-02
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Referencia fuera de su subconjunto no es fallo del motor.
- **FALSOS_NEGATIVOS:** Ambos calculan bien pero contrato mal representado; validar OR-01.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; differential
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** tests/test_qa_infrastructure.py::test_reference_manual_anchors; tests/test_qa_infrastructure.py::test_generated_reference_prices
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_reference_manual_anchors tests/test_qa_infrastructure.py::test_generated_reference_prices
```

## QA-04

- **TEST_ID:** QA-04
- **NOMBRE:** Dominio numérico y tipos estrictos
- **COMPONENTE:** models/canonical
- **RIESGO:** Coerción, no finito o desborde se acepta como dinero
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-14 INV-27
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** N17..N20; float0.1,bool1,NaN,37 dígitos,13 decimales; agregar dos inputs36dígitos
- **PASOS_EXACTOS:** 1. Validar cada input. 2. Auditar suma de inputs válidos grandes. 3. Verificar rechazo antes de conclusión o suma exacta.
- **RESULTADO_ESPERADO:** Inputs inválidos rechazados; 36nueves+1 suma37 dígitos permitida. No coerción bool→decimal ni 1→boolean.
- **ORACULO:** OR-01 OR-03
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Aplicar límites de input a agregados internos legítimos.
- **FALSOS_NEGATIVOS:** Sólo validar Value y omitir Charge/importer.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** unit; property-based
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_float_prohibited; tests/test_engine.py::test_invalid_money; tests/test_adversarial.py::test_aggregate_amount_can_exceed_individual_input_digit_bound; tests/test_adversarial.py::test_no_boolean_coercion
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_float_prohibited tests/test_engine.py::test_invalid_money tests/test_adversarial.py::test_aggregate_amount_can_exceed_individual_input_digit_bound tests/test_adversarial.py::test_no_boolean_coercion
```

## QA-05

- **TEST_ID:** QA-05
- **NOMBRE:** Redondeo, escala y orden
- **COMPONENTE:** rules/currency_round
- **RIESGO:** Cambio de centavos por modo u orden implícito
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-15 INV-27
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** N11..N16; 0.005+0.005; valores negativos; escalas0,2,3,8
- **PASOS_EXACTOS:** 1. Ejecutar cada fila manual. 2. Diferenciar round final de dos round explícitos. 3. Comprobar escala/modo/input en trace.
- **RESULTADO_ESPERADO:** Final0.01; por componente0.02; HALF_EVEN2.345→2.34,2.355→2.36. HALF_DOWN rechazado por configuración.
- **ORACULO:** OR-01 OR-02
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Cambiar expresión contractual es cambio esperado, no invariancia.
- **FALSOS_NEGATIVOS:** Sólo positivos/escala2 no detecta truncamiento de créditos.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; mutation
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_qa_infrastructure.py::test_reference_manual_anchors; tests/test_qa_infrastructure.py::test_generated_reference_prices
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_reference_manual_anchors tests/test_qa_infrastructure.py::test_generated_reference_prices
```

## QA-06

- **TEST_ID:** QA-06
- **NOMBRE:** División y contexto ambiental
- **COMPONENTE:** rules/Decimal
- **RIESGO:** Contexto global o precisión cambia resultado sin permiso
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-14 INV-19
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** N21..N23; prec global6; numeradores/denominadores negativos; divisor0
- **PASOS_EXACTOS:** 1. Comparar división con Decimal alta precisión y casos manuales. 2. Cambiar/restaurar contexto externo. 3. Probar precisión insuficiente.
- **RESULTADO_ESPERADO:** 1/3→0.33;−1/8 HALF_EVEN→−0.12; divisor0/desborde→UNDETERMINABLE/0confirmado. Contexto ajeno no altera audit.
- **ORACULO:** OR-01 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Referencia Decimal con precisión insuficiente introduce doble redondeo.
- **FALSOS_NEGATIVOS:** Rango actual de enteros pequeños no cubre todo exponente válido.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_property_division_matches_high_precision; tests/test_engine.py::test_global_decimal_context_does_not_affect_results; tests/test_adversarial.py::test_inexact_comparison_becomes_undeterminable
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_property_division_matches_high_precision tests/test_engine.py::test_global_decimal_context_does_not_affect_results tests/test_adversarial.py::test_inexact_comparison_becomes_undeterminable
```

## QA-07

- **TEST_ID:** QA-07
- **NOMBRE:** Unidades y monedas separadas
- **COMPONENTE:** models/rules/summary
- **RIESGO:** Kg, gramos o monedas se suman como equivalentes
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-06 INV-13
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** B+segundo cargoUSD; N24,N25; unidad final vacía o kg
- **PASOS_EXACTOS:** 1. Auditar moneda discordante. 2. Introducir g frente a kg sin factor. 3. Añadir factor explícito y acuerdoUSD independiente.
- **RESULTADO_ESPERADO:** Discordancia→UNDETERMINABLE; sin factor no conversión; 1000g×0.001kg/g×2ARS/kg=2ARS; buckets separados.
- **ORACULO:** OR-01 OR-03
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** No imponer dos decimales por código ISO.
- **FALSOS_NEGATIVOS:** Revisar core pero permitir suma multimoneda en UI.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** unit; metamorphic
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_currencies_never_summed_or_converted; tests/test_engine.py::test_missing_attribute_and_unit_mismatch; tests/test_engine.py::test_rules_need_currency_units
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_currencies_never_summed_or_converted tests/test_engine.py::test_missing_attribute_and_unit_mismatch tests/test_engine.py::test_rules_need_currency_units
```

## QA-08

- **TEST_ID:** QA-08
- **NOMBRE:** Números desde originales
- **COMPONENTE:** CSV/XLSX importer
- **RIESGO:** Cambio silencioso de magnitud o precisión antes del motor
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-14 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** XLSX literal1000000000000000.01 y1e999999; CSV1.234,56 y1.23,45; corpus exacto
- **PASOS_EXACTOS:** 1. Preservar bytes. 2. Importar con mapping confirmado. 3. Comparar value y provenance.raw con literal independiente.
- **RESULTADO_ESPERADO:** XLSX preserva fracción; exponente extremo rechaza fila; CSV argentino1234.56; agrupador inválido rechaza, no corrige silenciosamente.
- **ORACULO:** OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Un string XLSX respeta locale; no tratarlo igual que celda numérica.
- **FALSOS_NEGATIVOS:** Leer expected mediante openpyxl repite el float defectuoso.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** fuzz; property-based
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_xlsx_preserves_original_decimal_literal_without_binary_float_loss; tests/test_importing.py::test_xlsx_unbounded_exponent_is_rejected_before_decimal_expansion; tests/test_importing.py::test_argentine_decimal; tests/test_importing.py::test_unsafe_numeric_strings_rejected
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_xlsx_preserves_original_decimal_literal_without_binary_float_loss tests/test_importing.py::test_xlsx_unbounded_exponent_is_rejected_before_decimal_expansion tests/test_importing.py::test_argentine_decimal tests/test_importing.py::test_unsafe_numeric_strings_rejected
```

## QA-09

- **TEST_ID:** QA-09
- **NOMBRE:** Identidad y normalización declarada
- **COMPONENTE:** mapping/models
- **RIESGO:** Ceros o caracteres alterados unen entidades distintas
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-09 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** ref texto00001; numérico1 con máscara00000; fraccional99999999999999.001; Unicode y espacios
- **PASOS_EXACTOS:** 1. Importar referencia textual. 2. Repetir numeric_text reject/formatted. 3. Verificar reglas de strip y concepto desconocido.
- **RESULTADO_ESPERADO:** 00001 se conserva; numérico requiere política; fraccional rechaza aunque float parezca entero; concepto desconocido queda external:valor.
- **ORACULO:** OR-04 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Strip externo está declarado en modelos; no prometer byte equality del valor normalizado.
- **FALSOS_NEGATIVOS:** Alias/Unicode normalizado fuera del mapping puede colisionar en un cliente.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-04 IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_xlsx_numeric_id_requires_explicit_policy; tests/test_importing.py::test_original_fractional_numeric_identifier_cannot_become_integer_after_float_rounding; tests/test_importing.py::test_unknown_concept_not_canonicalized_by_accident
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_xlsx_numeric_id_requires_explicit_policy tests/test_importing.py::test_original_fractional_numeric_identifier_cannot_become_integer_after_float_rounding tests/test_importing.py::test_unknown_concept_not_canonicalized_by_accident
```

## QA-10

- **TEST_ID:** QA-10
- **NOMBRE:** Estructura CSV y conservación de filas
- **COMPONENTE:** CSV importer
- **RIESGO:** Fila o columna se desplaza u omite sin rastro
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-12 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Quotes multilínea, BOM, cp1252, header duplicado/vacío, fila con columna extra, reordered columns
- **PASOS_EXACTOS:** 1. Importar corpus con líneas físicas anotadas. 2. Comparar aceptadas/rechazadas y raw. 3. Permutar columnas/mapping.
- **RESULTADO_ESPERADO:** Referencia multilínea mantiene siguiente registro en línea4; mapeada repetida/ausente error; valor extra rechaza; economía invariante al reordenar.
- **ORACULO:** OR-04 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Blank lines/headers no son cargos; definir población relevante.
- **FALSOS_NEGATIVOS:** Control sólo de cantidad deja desplazamiento con misma cantidad.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** fuzz; metamorphic
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 IR-11 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_adversarial.py::test_csv_multiline_provenance_uses_actual_line; tests/test_importing.py::test_ambiguous_or_missing_headers_fail_file; tests/test_importing.py::test_reordered_columns_same_normalized_records; tests/test_adversarial.py::test_oversized_unmapped_cells_not_silently_shifted
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_csv_multiline_provenance_uses_actual_line tests/test_importing.py::test_ambiguous_or_missing_headers_fail_file tests/test_importing.py::test_reordered_columns_same_normalized_records tests/test_adversarial.py::test_oversized_unmapped_cells_not_silently_shifted
```

## QA-11

- **TEST_ID:** QA-11
- **NOMBRE:** Semántica de libro Excel
- **COMPONENTE:** XLSX importer
- **RIESGO:** Fórmula, ocultamiento o merge cambia alcance percibido
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-12 INV-14 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Libro2hojas/hiddenrows/merged/date styles/formula con cache; ver corpus en QA_CASES
- **PASOS_EXACTOS:** 1. Especificar sheet. 2. Importar con columnas requeridas vacías/merged. 3. Añadir fórmula cacheada y fila oculta. 4. Cotejar alcance declarado.
- **RESULTADO_ESPERADO:** Varias hojas sin selección error; fórmula mapeada rechazada; sin fill-forward. Ocultas requieren alcance visible: falta automatizar warning en producto.
- **ORACULO:** OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Fila oculta puede ser legítima; no descartarla por defecto.
- **FALSOS_NEGATIVOS:** Happy path XLSX no cubre estilos/hidden/cache; deuda explícita.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** fuzz; manual
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 IR-15 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_multisheet_requires_selection; tests/test_importing.py::test_xlsx_formula_never_evaluated_or_taken_as_cache; tests/test_importing.py::test_original_numeric_tokens_follow_sparse_sheet_coordinates
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_multisheet_requires_selection tests/test_importing.py::test_xlsx_formula_never_evaluated_or_taken_as_cache tests/test_importing.py::test_original_numeric_tokens_follow_sparse_sheet_coordinates
```

## QA-12

- **TEST_ID:** QA-12
- **NOMBRE:** XLS legacy y cache explícito
- **COMPONENTE:** xlrd/importer
- **RIESGO:** Fórmula guardada o binario impreciso parece hecho verificado
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-14 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** XLS BIFF con valores/fórmulas guardadas, codepage, epochs; montos alta precisión
- **PASOS_EXACTOS:** 1. Importar sin allow_xls_cached_values. 2. Habilitar y revisar warning. 3. Cotejar pares de celdas fuera de xlrd.
- **RESULTADO_ESPERADO:** Sin aceptación error; con aceptación warning persistente. No declarar recuperación de precisión perdida ni garantía de recalculado.
- **ORACULO:** OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Warning esperado no es fallo; su ausencia sí.
- **FALSOS_NEGATIVOS:** XLS generado por xlwt no cubre todos los productores reales.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** fuzz; manual
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_xls_requires_explicit_cached_value_acceptance
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 12.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_xls_requires_explicit_cached_value_acceptance
```

## QA-13

- **TEST_ID:** QA-13
- **NOMBRE:** Límites de importación y corrupción
- **COMPONENTE:** file parser/API
- **RIESGO:** Archivo agota recursos o produce un lote parcial silencioso
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-12 INV-25
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Archivo25MiB+, ZIP declarado150MiB+,250columnas+,200001filas+,bytes truncados
- **PASOS_EXACTOS:** 1. Crear cabeceras/payloads pequeños que activen límites. 2. Ejecutar en subprocess con timeout/RSS. 3. Comprobar clasificación y ausencia de corrida parcial.
- **RESULTADO_ESPERADO:** ImportErrorDetail/422 útil antes de agotar recursos; ningún resultado económico confirmado para importación abortada.
- **ORACULO:** OR-09 OR-10
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Timeout del equipo saturado requiere repetir aislado una vez.
- **FALSOS_NEGATIVOS:** Bytes aleatorios cortos no atraviesan parser profundo; tamaño declarado no prueba expansión real.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** fuzz; security
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** B
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 6.0
- **ESFUERZO_IMPLEMENTACION:** 1–2 días
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified
```

## QA-14

- **TEST_ID:** QA-14
- **NOMBRE:** Importación incompleta y alcance documental
- **COMPONENTE:** import/core/operator
- **RIESGO:** Total aceptado se confunde con total factura
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-11 INV-12 INV-29
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** B con fila importe inválida; documento externo total200 mientras aceptado100; archivo faltante
- **PASOS_EXACTOS:** 1. Contar filas de negocio. 2. Conciliar accepted/rejected/omitted. 3. Auditar issue row. 4. Comparar contra total externo y etiqueta UI.
- **RESULTADO_ESPERADO:** Rechazo impide certeza del lote. Archivo nunca aportado no se detecta por core: control externo obligatorio y déficit visible.
- **ORACULO:** OR-03 OR-04 OR-01
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Subtotal/cabecera no es fila económica duplicada.
- **FALSOS_NEGATIVOS:** Import_complete=true no demuestra documentos completos.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-02 IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_import_rejects_block_economic_confirmation; tests/test_integration.py::test_invalid_fixture_rejects_visible_rows
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_import_rejects_block_economic_confirmation tests/test_integration.py::test_invalid_fixture_rejects_visible_rows
```

## QA-15

- **TEST_ID:** QA-15
- **NOMBRE:** Procedencia verificable
- **COMPONENTE:** import/trace/storage
- **RIESGO:** Dato usado no puede reconstruirse desde original
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** CSVmultilínea, XLSXfila3, constante mapping; original con un byte cambiado
- **PASOS_EXACTOS:** 1. Del finding seguir trace.field→registro→SourceRef. 2. Verificar SHA y localizar celda. 3. Contrastar raw→transform→value, incluidas constantes.
- **RESULTADO_ESPERADO:** Documento/hoja/fila/columna/raw correctos y mapping congelado; archivo alterado se rechaza; constante respaldada por configuración.
- **ORACULO:** OR-04 OR-06
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Dataset manual puede carecer de provenance por contrato actual; exigirla en importados.
- **FALSOS_NEGATIVOS:** Hash correcto de archivo no demuestra referencia a la celda correcta.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-11 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_csv_argentine_numbers_zeroes_and_provenance; tests/test_storage_reporting.py::test_tampered_source_detected
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_csv_argentine_numbers_zeroes_and_provenance tests/test_storage_reporting.py::test_tampered_source_detected
```

## QA-16

- **TEST_ID:** QA-16
- **NOMBRE:** Selección única de vigencia
- **COMPONENTE:** engine.select_version
- **RIESGO:** Tarifa equivocada por frontera/gap/overlap
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-07 INV-08 INV-16
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** QA_CASES calendario V1=100/V2=120, fin06-30/inicio07-01; versiones invertidas
- **PASOS_EXACTOS:** 1. Evaluar comienzo/fin/día siguiente. 2. Crear overlap/gap. 3. Invertir orden de versiones. 4. Consolidar fechas de ambos lados.
- **RESULTADO_ESPERADO:** Extremos inclusivos; cero/dos versiones o grupo mixto→UNDETERMINABLE; no elegir primera ni prorratear.
- **ORACULO:** OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Día dentro de versión puede ser FAIL por importe, no por fecha.
- **FALSOS_NEGATIVOS:** Dos versiones con mismo precio ocultan selector equivocado.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; mutation
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-05 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_version_boundaries; tests/test_engine.py::test_overlapping_versions_never_pick_first; tests/test_engine.py::test_group_mixed_version_is_undeterminable
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_version_boundaries tests/test_engine.py::test_overlapping_versions_never_pick_first tests/test_engine.py::test_group_mixed_version_is_undeterminable
```

## QA-17

- **TEST_ID:** QA-17
- **NOMBRE:** Fecha civil y seriales de Excel
- **COMPONENTE:** import/date types
- **RIESGO:** Fecha cambia por locale/época/hora y selecciona otra tarifa
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-08 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Matriz temporal completa:03/04 ambiguo, leap2024/2026, serial60, epochs1900/1904, midnight/offset
- **PASOS_EXACTOS:** 1. Importar cada par fuente→fecha esperada. 2. Repetir con TZs distintas. 3. Comparar versión seleccionada con calendario manual.
- **RESULTADO_ESPERADO:** Ambigua/invalid/hora/zona→rechazo; medianoche ingenua admitida. Serial ficticio60 debe bloquearse/advertirse: pendiente comprobar y corregir si normaliza.
- **ORACULO:** OR-04 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Cambiar date_field contractual legítimamente cambia tarifa.
- **FALSOS_NEGATIVOS:** Comparar sólo date final pierde serial/epoch original.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** fuzz; property-based
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-05 IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_ambiguous_date_is_rejected; tests/test_importing.py::test_timestamps_are_not_silently_truncated; tests/test_engine.py::test_alternate_date_field
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_ambiguous_date_is_rejected tests/test_importing.py::test_timestamps_are_not_silently_truncated tests/test_engine.py::test_alternate_date_field
```

## QA-18

- **TEST_ID:** QA-18
- **NOMBRE:** Reglas/condiciones y AST acotado
- **COMPONENTE:** models/rules
- **RIESGO:** Default inventado o condición desconocida se trata falsa
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-07 INV-13
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** B con0/2reglas aplicables, condición ausente, if lazy, op desconocida, profundidad31
- **PASOS_EXACTOS:** 1. Validar AST inválidos. 2. Evaluar datos faltantes. 3. Probar rama no elegida con división0. 4. Repetir reglas reordenadas.
- **RESULTADO_ESPERADO:** AST inválido rechaza;0/2reglas→UNDETERMINABLE; if no evalúa rama no elegida; condición faltante no es false.
- **ORACULO:** OR-01 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** and/or actualmente evalúan todos los operandos; sólo if promete lazy.
- **FALSOS_NEGATIVOS:** Test AST parseado no prueba aridad/semántica de cada operador.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-03 IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_condition_missing_is_not_false; tests/test_engine.py::test_condition_branch_is_lazy; tests/test_engine.py::test_overlapping_rules_are_undeterminable; tests/test_adversarial.py::test_bounded_expression_depth_rejects_nested_attack
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_condition_missing_is_not_false tests/test_engine.py::test_condition_branch_is_lazy tests/test_engine.py::test_overlapping_rules_are_undeterminable tests/test_adversarial.py::test_bounded_expression_depth_rejects_nested_attack
```

## QA-19

- **TEST_ID:** QA-19
- **NOMBRE:** Lookup/bandas sin desempate arbitrario
- **COMPONENTE:** rules/tables
- **RIESGO:** Primer precio coincidente reemplaza ambigüedad real
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-07 INV-13 INV-16
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** N10, tabla con clave repetida/mismo precio, gap/overlap, unidadesdiscordantes
- **PASOS_EXACTOS:** 1. Evaluar ambos lados y límite exacto. 2. Repetir filas. 3. Invertir tabla. 4. Intercalar versión con tabla homónima diferente.
- **RESULTADO_ESPERADO:** Bandas[lower,upper); exactamente1coincidencia. Cero/dos incluso mismo importe→UNDETERMINABLE; caché separada por versión/acuerdo.
- **ORACULO:** OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Orden textual de tabla puede cambiar hash, economía no.
- **FALSOS_NEGATIVOS:** Mismo valor en tablas distintas oculta contaminación de caché.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; mutation
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-05 IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_adversarial.py::test_band_overlap_and_gap_never_select_arbitrarily; tests/test_adversarial.py::test_duplicate_lookup_rows_even_same_price_are_ambiguous
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_band_overlap_and_gap_never_select_arbitrarily tests/test_adversarial.py::test_duplicate_lookup_rows_even_same_price_are_ambiguous
```

## QA-20

- **TEST_ID:** QA-20
- **NOMBRE:** Claves, aliases y vínculos explícitos
- **COMPONENTE:** matching
- **RIESGO:** Entidad equivocada por resolución implícita
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-09 INV-26
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Taxonomía matching1→1/compuesto/alias; clave vacía; explícito inválido/contradictorio
- **PASOS_EXACTOS:** 1. Dibujar grafo manual. 2. Aplicar alias sólo al cargo. 3. Vaciar clave. 4. Añadir link inválido y verificar sin fallback.
- **RESULTADO_ESPERADO:** Match exacto declarado; vacíos no empatan; link ausente/repetido/carrier ajeno→UNDETERMINABLE. Contradicción link/claves requiere control adicional pendiente.
- **ORACULO:** OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Precedencia explicit sobre keys es contrato actual; no confundirla con detección de intención errónea.
- **FALSOS_NEGATIVOS:** Explicito válido estructuralmente puede apuntar a operación equivocada.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-04 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_composite_keys_and_directional_alias; tests/test_engine.py::test_invalid_explicit_link_never_falls_back; tests/test_adversarial.py::test_empty_keys_never_join_to_empty_keys
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_composite_keys_and_directional_alias tests/test_engine.py::test_invalid_explicit_link_never_falls_back tests/test_adversarial.py::test_empty_keys_never_join_to_empty_keys
```

## QA-21

- **TEST_ID:** QA-21
- **NOMBRE:** Ambigüedad propagada a grupos parciales
- **COMPONENTE:** matching/aggregation
- **RIESGO:** FAIL falso por comparar sólo fracción asignada
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-09 INV-04
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** S1/S2 misma referencia; C1=40 explícitoS1,C2=60 ambiguo; E100
- **PASOS_EXACTOS:** 1. Auditar en ambos órdenes. 2. Inspeccionar los dos findings. 3. Resolver C2 explícitamente y volver a auditar nueva copia.
- **RESULTADO_ESPERADO:** Antes: ambos REVIEW/confirmada0; después, si C1+C2→S1, grupoA100,E100 PASS. Ningún cargo se pierde.
- **ORACULO:** OR-03 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** No exigir un único finding antes/después; cambia agrupación.
- **FALSOS_NEGATIVOS:** Revisar sólo cargo ambiguo deja FAIL parcial en el otro.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-04 IR-03 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_adversarial.py::test_ambiguous_allocation_also_blocks_related_partial_group; tests/test_engine.py::test_matching_ambiguity_is_review
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_ambiguous_allocation_also_blocks_related_partial_group tests/test_engine.py::test_matching_ambiguity_is_review
```

## QA-22

- **TEST_ID:** QA-22
- **NOMBRE:** Consolidado y cargos por componentes
- **COMPONENTE:** matching/rules
- **RIESGO:** Expected repetido en1→N o N→1 incompleto
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-04 INV-05 INV-09
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** S1peso10,S2peso20;group lote;tarifa2; C40+C20; duplicate_fields vacío
- **PASOS_EXACTOS:** 1. Auditar sum×2. 2. Dividir/reunir líneas actual. 3. Cambiar sum por attr sobre pesos distintos. 4. Comparar scopes, no IDs hash.
- **RESULTADO_ESPERADO:** UnE60,A60 PASS; split no repiteE. attr de pesos distintos→UNDETERMINABLE; no prorrateo automático.
- **ORACULO:** OR-02 OR-03 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Mínimo por envío no es aditivo; no aplicar MT12 fuera de sus precondiciones.
- **FALSOS_NEGATIVOS:** N→M solapado no se cubre con N→1.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; metamorphic
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-04 IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_group_sum_and_one_expected_charge; tests/test_engine.py::test_multiple_lines_aggregate_without_inventing_duplicates
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_group_sum_and_one_expected_charge tests/test_engine.py::test_multiple_lines_aggregate_without_inventing_duplicates
```

## QA-23

- **TEST_ID:** QA-23
- **NOMBRE:** Asignaciones superpuestas y servicios parciales
- **COMPONENTE:** allocation
- **RIESGO:** Misma obligación se confirma dos veces
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-09 INV-05
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** C1→S1,S2;C2→S2,S3 mismo concepto; servicio tramo parcial sin política
- **PASOS_EXACTOS:** 1. Construir grafo con intersecciónS2. 2. Auditar. 3. Verificar grupo relacionado no confirma ni reparte. 4. Confirmar límite contractual con operador.
- **RESULTADO_ESPERADO:** Grupos superpuestos REVIEW; no multiplicar expected confirmado. Servicio parcial no representado se bloquea hasta definir regla.
- **ORACULO:** OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Conceptos independientes sobre mismo S no son el mismo scope económico.
- **FALSOS_NEGATIVOS:** Solapamiento a través de acuerdos distintos requiere revisión contractual.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-04 IR-15 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_overlap_allocations_are_review
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_overlap_allocations_are_review
```

## QA-24

- **TEST_ID:** QA-24
- **NOMBRE:** Duplicados candidatos y remito legítimo
- **COMPONENTE:** matching
- **RIESGO:** Deduplicar importe válido o confirmar sospecha
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-17 INV-04
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Dos cargos refigual/conceptigual/importeigual; clavesduplicado activas/inactivas; conceptos distintos
- **PASOS_EXACTOS:** 1. Auditar con duplicate_fields. 2. Desactivar sólo esa política. 3. Separar conceptos y verificar conservación.
- **RESULTADO_ESPERADO:** Candidatos→REVIEW, no eliminación ni ahorro; sin política líneas agregadas; distinto concepto no es duplicado por referencia sola.
- **ORACULO:** OR-03 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Mismo remito legítimo puede requerir claves más específicas.
- **FALSOS_NEGATIVOS:** No configurar duplicate_fields no demuestra ausencia de duplicados reales.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-03 IR-04 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_configured_duplicate_is_candidate_only; tests/test_engine.py::test_same_remittance_different_concepts_is_not_duplicate
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_configured_duplicate_is_candidate_only tests/test_engine.py::test_same_remittance_different_concepts_is_not_duplicate
```

## QA-25

- **TEST_ID:** QA-25
- **NOMBRE:** Evidencia por ámbito y adición selectiva
- **COMPONENTE:** evidence
- **RIESGO:** Respaldo ajeno o insuficiente certifica cargo
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-10 INV-20
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DosS,each_shipment/each_charge/group,any_of approval/POD,document_required; evidencia ajena
- **PASOS_EXACTOS:** 1. Retirar un respaldo por ámbito. 2. Agregar sólo el faltante. 3. Comparar grupos no relacionados y run original. 4. Retirar documento obligatorio.
- **RESULTADO_ESPERADO:** Faltante→REVIEW; evidencia suficiente sólo resuelve scope pertinente; nueva corrida puede PASS o FAIL según Δ, historia intacta.
- **ORACULO:** OR-05 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Añadir respaldo puede convertir REVIEW en FAIL legítimo; no exigir PASS.
- **FALSOS_NEGATIVOS:** Sólo kind sin revisar asociaciones/document_hash es falso respaldo.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; metamorphic
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-03 IR-11 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_evidence_any_of_and_per_operation; tests/test_engine.py::test_unrelated_evidence_cannot_support_charge
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_evidence_any_of_and_per_operation tests/test_engine.py::test_unrelated_evidence_cannot_support_charge
```

## QA-26

- **TEST_ID:** QA-26
- **NOMBRE:** Cobertura explícita de cargos ausentes
- **COMPONENTE:** coverage
- **RIESGO:** Inventar deuda o duplicar hallazgo de cobertura
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-18 INV-04
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** B sin cargos;rule.expected true; coverage vacío/explícito; versión ausente; carrier incorrecto
- **PASOS_EXACTOS:** 1. Comparar sin/con coverage. 2. Probar when=false. 3. Agregar cargo ya indeterminado. 4. Validar scope inválido.
- **RESULTADO_ESPERADO:** Sin scope no inventar; scope correcto→REVIEW A0 sin confirmada; whenfalse omite expectativa; no duplica cargo sin versión; scope inválido rechaza.
- **ORACULO:** OR-03 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Hallazgo sin cargo aumenta findings pero no charge_counts.
- **FALSOS_NEGATIVOS:** Creer que cobertura detecta documento faltante no aportado.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-03 IR-04 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_missing_expected_charge_requires_explicit_scope_and_is_review; tests/test_adversarial.py::test_missing_coverage_must_not_duplicate_existing_undetermined_charge; tests/test_adversarial.py::test_coverage_cannot_silently_drop_wrong_carrier
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_missing_expected_charge_requires_explicit_scope_and_is_review tests/test_adversarial.py::test_missing_coverage_must_not_duplicate_existing_undetermined_charge tests/test_adversarial.py::test_coverage_cannot_silently_drop_wrong_carrier
```

## QA-27

- **TEST_ID:** QA-27
- **NOMBRE:** Conservación total por ID y moneda
- **COMPONENTE:** aggregate/all states
- **RIESGO:** Omisión o doble conteo queda oculto por neto
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-03 INV-04 INV-05 INV-06
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** B extendido PASS/FAIL±/REVIEW/UNDETERMINABLE; cargo unmatched;0/negativos; dosmonedas
- **PASOS_EXACTOS:** 1. Checker recompone Counter de charge_ids y sumas desde C. 2. Comparar todos los buckets/counts. 3. Mutar salida duplicando/quitando cargo.
- **RESULTADO_ESPERADO:** Cada C exactamente1vez; bruto por moneda preservado; +50 y−75 separados y neto−25. Checker rechaza salida manipulada.
- **ORACULO:** OR-03
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Créditos invalidan desigualdad determinable≤actual; usar identidades firmadas.
- **FALSOS_NEGATIVOS:** Totales coincidentes pueden ocultar omisión y duplicación compensadas: contar IDs.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** property-based; mutation
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-01 IR-02 IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption
```

## QA-28

- **TEST_ID:** QA-28
- **NOMBRE:** Determinismo y transformaciones
- **COMPONENTE:** core/canonical/import
- **RIESGO:** Orden/nombre/ambiente modifica dinero
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-19 INV-21
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** MT01..MT20 con nivel de igualdad declarado; A/B/A; cambio future/filename/columns
- **PASOS_EXACTOS:** 1. Guardar baseline completo. 2. Aplicar una transformación. 3. Comparar resultado o economic_projection según tabla. 4. Comprobar fuente hash cambia cuando bytes cambian.
- **RESULTADO_ESPERADO:** Reordenamiento normalizado completo igual; renombre/columna economía igual aunque snapshot hash cambie; cambio futuro no muta run guardado.
- **ORACULO:** OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Exigir semantic_hash igual al agregar versión futura produce falso fallo.
- **FALSOS_NEGATIVOS:** Dos errores idénticos satisfacen relación; combinar OR02/03.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** metamorphic; property-based
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-09 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_property_arbitrary_row_permutation; tests/test_engine.py::test_semantic_hash_ignores_incidental_label; tests/test_qa_infrastructure.py::test_generated_uncertainty_and_metamorphism
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_engine.py::test_property_arbitrary_row_permutation tests/test_engine.py::test_semantic_hash_ignores_incidental_label tests/test_qa_infrastructure.py::test_generated_uncertainty_and_metamorphism
```

## QA-29

- **TEST_ID:** QA-29
- **NOMBRE:** Aislamiento entre clientes y catálogos
- **COMPONENTE:** configuration/storage/cache
- **RIESGO:** Acuerdo o datoB influyeA sin alarma
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-26
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DosDB, mismosS/C/A/tableIDs; Aprecio100,B900; import originales distintos
- **PASOS_EXACTOS:** 1. EjecutarA/B/A en proceso. 2. Reabrir DBs y comparar A. 3. Intentar selección de config ajena en UI y revisar operación.
- **RESULTADO_ESPERADO:** A idéntico, fuentes/configs separadas por DB. Catálogo global dentro mismaDB no es aislamiento multiempresa; no habilitarlo como tal.
- **ORACULO:** OR-05 OR-06 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Diferencia de label/input_hash no prueba contaminación económica.
- **FALSOS_NEGATIVOS:** DatosconIDsdistintos nunca ejercitan colisión/caché compartida.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-13 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-30

- **TEST_ID:** QA-30
- **NOMBRE:** Decisiones humanas y cadena
- **COMPONENTE:** storage/UI
- **RIESGO:** Resolución borra finding o decisión previa
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-20 INV-24
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** RunB;APPROVED→REJECTED; dos escritores; finding/evidence ajenos
- **PASOS_EXACTOS:** 1. Guardar hash de resultado. 2. Añadir decisiones en orden/concurrentes. 3. Verificar chain/resultado. 4. Intentar referencias ajenas.
- **RESULTADO_ESPERADO:** Resultado original idéntico; decisiones append-only ordenadas/hash enlazado; referencias inexistentes rechazadas.
- **ORACULO:** OR-06
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Hash de paquete cambia al añadir decisión legítima.
- **FALSOS_NEGATIVOS:** Cadena local no detecta truncamiento de sufijo sin ancla externa.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-10 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_human_decision_never_rewrites_finding; tests/test_storage_reporting.py::test_decision_chain_serializes_concurrent_writers; tests/test_storage_reporting.py::test_no_unknown_decision_or_evidence
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_human_decision_never_rewrites_finding tests/test_storage_reporting.py::test_decision_chain_serializes_concurrent_writers tests/test_storage_reporting.py::test_no_unknown_decision_or_evidence
```

## QA-31

- **TEST_ID:** QA-31
- **NOMBRE:** Integridad histórica y mutación
- **COMPONENTE:** SQLite/snapshot
- **RIESGO:** Corrida alterada sigue pareciendo confiable
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-20 INV-28
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** CopiaDB; UPDATE/DELETE normales y bypass de trigger controlado en copia; cambio deV2
- **PASOS_EXACTOS:** 1. Guardar ancla externa. 2. Intentar mutación. 3. Comparar load y list_runs ante byte alterado. 4. Abrir original intacto.
- **RESULTADO_ESPERADO:** Writes históricos bloqueados; load detecta hashes; configuración futura no cambia run. list_runs no verifica integridad: deuda visible, no oráculo.
- **ORACULO:** OR-06
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Metadata/created_at fuera del hash actual no está autenticada.
- **FALSOS_NEGATIVOS:** Rehash malicioso total o truncamiento puede pasar sin copia externa.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-10 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_db_update_delete_blocked; tests/test_storage_reporting.py::test_tampered_result_detected_after_trigger_bypass; tests/test_storage_reporting.py::test_changed_agreement_preserves_history
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_db_update_delete_blocked tests/test_storage_reporting.py::test_tampered_result_detected_after_trigger_bypass tests/test_storage_reporting.py::test_changed_agreement_preserves_history
```

## QA-32

- **TEST_ID:** QA-32
- **NOMBRE:** Replay y cambio de artefacto
- **COMPONENTE:** storage/replay
- **RIESGO:** Resultado nuevo se presenta como reproducción histórica
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-21 INV-19
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** RunB; snapshot/ancla; fuente altered; artifact distinto; proceso abierto con código cambiado
- **PASOS_EXACTOS:** 1. Replay original. 2. Alterar fuente/snapshot en copia. 3. Cambiar artifact o código cargado. 4. Confirmar que no reescribe resultado.
- **RESULTADO_ESPERADO:** Mismoartefacto coincide exactamente; integridad fallida/artefacto nuevo/proceso desactualizado rechaza. Reimportación es operación diferente.
- **ORACULO:** OR-06 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Otroartifact rechazado no es nondeterminismo probado.
- **FALSOS_NEGATIVOS:** Replay perfecto perpetúa error de importer previo.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-09 IR-10 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_save_replay_and_idempotency; tests/test_storage_reporting.py::test_engine_artifact_change_blocks_replay; tests/test_storage_reporting.py::test_source_update_requires_process_restart
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_save_replay_and_idempotency tests/test_storage_reporting.py::test_engine_artifact_change_blocks_replay tests/test_storage_reporting.py::test_source_update_requires_process_restart
```

## QA-33

- **TEST_ID:** QA-33
- **NOMBRE:** Proveniencia de ejecutables y alcance
- **COMPONENTE:** metadata/incident tooling
- **RIESGO:** No localizar históricos afectados por importer/reportero
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-21 INV-28 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DBhistórica sinimporterhash/client_id; feature configurada no ejecutada; run dañado
- **PASOS_EXACTOS:** 1. Ejecutar impact mode=ro con filtrosfeature/importer. 2. Mantener desconocidos en candidatos. 3. Contrastar inventario manual y hashDB antes/después.
- **RESULTADO_ESPERADO:** Unknown no se excluye; config y trace consultadas; cliente declarado externamente; no escribir schema/triggers ni inventar huellas pasadas.
- **ORACULO:** OR-05 OR-06
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Candidato configurado puede no haber ejecutado feature: conservador, no afirmación de daño.
- **FALSOS_NEGATIVOS:** Filtrar sólo trace pierde errores previos a calcular.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-09 IR-13 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** tests/test_qa_infrastructure.py::test_impact_is_read_only_and_retains_unknowns
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_impact_is_read_only_and_retains_unknowns
```

## QA-34

- **TEST_ID:** QA-34
- **NOMBRE:** Backup, restore y reapertura
- **COMPONENTE:** SQLite/operations
- **RIESGO:** Backup existe pero no recupera historia/fuentes
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-25 INV-28
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DB2runs/decisiones/fuentes; copia backup a ruta nueva; archivo destino existente
- **PASOS_EXACTOS:** 1. Crearbackup conAPI. 2. Restaurar en otra ruta. 3. Verificar inventario/hashes/decisiones/fuentes y replay conartefacto original. 4. Intentar overwrite.
- **RESULTADO_ESPERADO:** Copia consistente y mismas corridas; overwrite rechazado; original intacto. Copia fuera del equipo exige operación real.
- **ORACULO:** OR-06 OR-10
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Ese test se llama migration pero sólo prueba inicialización/reapertura.
- **FALSOS_NEGATIVOS:** Backup sobre mismo disco no cubre pérdida del equipo.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-12 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_migration_reopening_and_consistent_backup
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_migration_reopening_and_consistent_backup
```

## QA-35

- **TEST_ID:** QA-35
- **NOMBRE:** Crash, rollback y concurrencia
- **COMPONENTE:** SQLite/exports
- **RIESGO:** Transacción parcial o dos procesos duplican/perdieron historia
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-25 INV-04
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Subproceso copiaDB, fallo antes/despuésINSERT/commit; dosruns simultáneos; disco lleno simulado
- **PASOS_EXACTOS:** 1. Inyectar fallo en frontera transaccional. 2. Reabrir copia. 3. Inventariar completos/ausentes y fuentes huérfanas. 4. Validar no corrida parcial visible.
- **RESULTADO_ESPERADO:** Run completo o ausente, cadena íntegra; busy error recuperable. Fuentes huérfanas pueden existir y no son pérdida histórica; export incompleto no se presenta como completo.
- **ORACULO:** OR-06 OR-10
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Proceso terminado no prueba que un commit previo deba desaparecer.
- **FALSOS_NEGATIVOS:** Thread test de decisiones no cubre kill de proceso o full disk.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration; fault injection
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** B
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-12 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_decision_chain_serializes_concurrent_writers
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 7.5
- **ESFUERZO_IMPLEMENTACION:** 1–3 días
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_decision_chain_serializes_concurrent_writers
```

## QA-36

- **TEST_ID:** QA-36
- **NOMBRE:** Schema y migración recuperable
- **COMPONENTE:** SQLite/version upgrade
- **RIESGO:** Migración interpreta datos previos con semántica nueva
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-20 INV-25
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DBvacía/v1/futurav2; v0no vacía; schema incompleto; futura migración parcial
- **PASOS_EXACTOS:** 1. Abrir copias de cadaestado. 2. Futuramigración: backup anclado, ejecutar, fallar enmedio, restore/retry. 3. Comparar históricos y originales.
- **RESULTADO_ESPERADO:** Vacía inicializa1; futura rechaza; v1reabre sin cambio. v0no vacía/incompleta requiere validación adicional pendiente; ninguna migración real certificada.
- **ORACULO:** OR-06
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** No inventar downgrade de schema futuro.
- **FALSOS_NEGATIVOS:** Una prueba de reopen no cubre atomicidad del DDL.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** B
- **CUANDO:** migración; release con cambio de schema
- **RESPUESTA_SI_FALLA:** IR-10 IR-12 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_newer_database_schema_is_not_opened; tests/test_storage_reporting.py::test_migration_reopening_and_consistent_backup
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 7.5
- **ESFUERZO_IMPLEMENTACION:** 1–3 días
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_newer_database_schema_is_not_opened tests/test_storage_reporting.py::test_migration_reopening_and_consistent_backup
```

## QA-37

- **TEST_ID:** QA-37
- **NOMBRE:** Reconciliación entre representaciones
- **COMPONENTE:** JSON/SQLite/API/XLSX/HTML/UI
- **RIESGO:** Salida cambia estado, importe o identidad
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-23 INV-03
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Run ficticio4estados+monedas;8hojas; exportJSON/HTML; APIrun; observación DOM opcional
- **PASOS_EXACTOS:** 1. Verificar run e invariantes. 2. Leer salidas con lectoresindependientes. 3. Comparar filas/monedas/estado/importes y resúmenes. 4. Mutar cada salida y exigir detección.
- **RESULTADO_ESPERADO:** Camposmateriales exactos; filas completas, sin fórmulas; API/DOM sólo cubiertos si se aportan. Ausencia de canal no es aprobación de ese canal.
- **ORACULO:** OR-03 OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** HTML es resumen: no exigir columna inexistente, sí su contenido declarado.
- **FALSOS_NEGATIVOS:** Conciliar salidas iguales no prueba que el core aplicó contrato correcto.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-08 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** tests/test_qa_infrastructure.py::test_cross_report_reconciliation_and_tamper_detection
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_cross_report_reconciliation_and_tamper_detection
```

## QA-38

- **TEST_ID:** QA-38
- **NOMBRE:** Límites de reportes y contenido activo
- **COMPONENTE:** reporting
- **RIESGO:** Truncamiento silencioso o fórmula/HTML se ejecuta
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-23 INV-25
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Texto32768chars, límitefilas reducido en test, nota=HYPERLINK/script, importes36dígitos
- **PASOS_EXACTOS:** 1. Exportar. 2. Abrir tiposdecelda/cantidad. 3. Forzar límiteyverificar ZIPsinXLSX+warning+JSONentero. 4. Inspeccionar HTML escapado.
- **RESULTADO_ESPERADO:** Nunca XLSXparcial; texto explícito sinfórmulas; JSONoriginal íntegro; alerta de omisión conservada.
- **ORACULO:** OR-07 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Texto exacto en Excel no es celda numérica sumable automáticamente.
- **FALSOS_NEGATIVOS:** Probar límite reducido no mide memoria real de100kfilas.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration; security
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-08 IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_workbook_is_real_and_has_exact_money_and_no_formulas; tests/test_storage_reporting.py::test_report_escapes_untrusted_html_and_excel_formula; tests/test_storage_reporting.py::test_excel_long_cell_is_not_silently_truncated; tests/test_storage_reporting.py::test_excel_row_limit_preserves_full_bundle_json
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_workbook_is_real_and_has_exact_money_and_no_formulas tests/test_storage_reporting.py::test_report_escapes_untrusted_html_and_excel_formula tests/test_storage_reporting.py::test_excel_long_cell_is_not_silently_truncated tests/test_storage_reporting.py::test_excel_row_limit_preserves_full_bundle_json
```

## QA-39

- **TEST_ID:** QA-39
- **NOMBRE:** UI conserva semántica visible y estado actual
- **COMPONENTE:** browser/UI
- **RIESGO:** Filtro/cache/formato muestra otra auditoría o dinero alterado
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-23 INV-24 INV-29
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Dosruns parecidos; cantidades1e15+.01como strings;150findings;4estados;decisión distinta
- **PASOS_EXACTOS:** 1. Capturar DOM de todaslaspáginas/filtros. 2. Cambiar run rápido, abrir detalle/decidir. 3. Comparar valores visibles y etiquetas conrun exacto. 4. Probar moneda0/3decimales.
- **RESULTADO_ESPERADO:** No Number/float en dinero; página/filtro no cambia métricasglobales; motor y decisión separados; ningún request fuera de loopback.
- **ORACULO:** OR-07 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Captura de una página no equivale al lote entero; registrar filtro.
- **FALSOS_NEGATIVOS:** API200 no prueba lo que el operador leyó.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** E2E
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-08 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 1–2 días
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-40

- **TEST_ID:** QA-40
- **NOMBRE:** Barrera de red local
- **COMPONENTE:** server/CLI
- **RIESGO:** Página ajena opera sobre datos locales
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-26 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Hostmalicioso,originajeno,tokenfaltante/erróneo,CORSpreflight; socketdelservicio
- **PASOS_EXACTOS:** 1. RequestsPOSTsin/contokenyorigin. 2. Verificarbind127.0.0.1enprocesoCLI. 3. Probarlectura cross-origin desde navegador. 4. Inspeccionar efectosDB.
- **RESULTADO_ESPERADO:** Host/origin/token incorrectos rechazan; sin CORSpermisivo; sólo loopback. 403conefectosprevios es fallo.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Token local no autentica usuarios del mismo equipo.
- **FALSOS_NEGATIVOS:** TestClient no verifica socketreal/bind ni comportamiento navegador.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** security; E2E
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_integration.py::test_local_api_security_boundary
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_local_api_security_boundary
```

## QA-41

- **TEST_ID:** QA-41
- **NOMBRE:** Rutas, archivos y sobrescritura
- **COMPONENTE:** upload/export/backup
- **RIESGO:** Lectura/escritura fuera del destino permitido
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-25 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Canaryoutside;../../name,rutaabsoluta,C:\name,symlink,destinoexistente
- **PASOS_EXACTOS:** 1. Subirfilenamehostil. 2. Exportar/backup a destinos temporales existentes/symlink. 3. Comprobar canary y archivos modificados. 4. Nunca usar archivos reales.
- **RESULTADO_ESPERADO:** Uploads porhash;no arbitraryread/write; overwrite rechaza. Política efectiva de symlinks queda pendiente antes de confiar rutas compartidas.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** CLI acepta ruta elegida por operador; no confundirla con ruta controlada por upload.
- **FALSOS_NEGATIVOS:** Carpeta vacía symlink puede redirigir export sin romper chequeo de nooverwrite.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** security
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 1–2 días
- **DATOS_REALES:** no
- **WINDOWS:** sí
- **INTERVENCION_HUMANA:** no

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-42

- **TEST_ID:** QA-42
- **NOMBRE:** XML/ZIP malicioso acotado
- **COMPONENTE:** XLSX/bundle
- **RIESGO:** Entidades externas, bomb o entrada ambigua supera defensa
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-25 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DTDpequeña,entitycanary,ZIPentryduplicate/traversal,archive sizes; process budget
- **PASOS_EXACTOS:** 1. Generar archivo pequeño sintético. 2. Ejecutar en subprocess sinredyconlímite. 3. Registrar rechazo/salidas/red/canary. 4. Verificar expansión ademásdeheader.
- **RESULTADO_ESPERADO:** Sin ejecución/red/lecturaexterna; excepción útilyrecuperable; ninguna corridaeconómica parcial. No instalar archivos activos para la prueba.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Rechazo genérico de corrupción es aceptable si no hay efecto y orienta recuperación.
- **FALSOS_NEGATIVOS:** Fuzzerdebytes500 no alcanza DTD/zipválido ni expansión.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** fuzz; security
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified
```

## QA-43

- **TEST_ID:** QA-43
- **NOMBRE:** Errores de API y consistencia de operación
- **COMPONENTE:** FastAPI
- **RIESGO:** 422/500 oculta escritura parcial o resultado diferente a CLI
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-25 INV-29
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Mappinginválido,campoextra,idajeno,upload32MiB+,mismaentradaCLI/API
- **PASOS_EXACTOS:** 1. Registrar inventarioDB. 2. Enviar request inválido. 3. Comparar cambios permitidos de fuentes/configs versus runs. 4. Repetir válido y contrastar resultadoCLI.
- **RESULTADO_ESPERADO:** Errorrecuperable sinstack al usuario; norunparcial; resultadoeconómicoCLI/APIidéntico; no datos sensibles enrespuesta técnica.
- **ORACULO:** OR-03 OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Preview conserva fuente/config legítimamente aunque no se ejecuteaudit.
- **FALSOS_NEGATIVOS:** Sóloassertstatuscode ignora cuerpo y efectos.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 IR-08 IR-12 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_integration.py::test_api_configuration_errors_use_recoverable_messages; tests/test_integration.py::test_api_runs_decisions_export_replay; tests/test_integration.py::test_api_import_with_mapping_and_provenance
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 24.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_api_configuration_errors_use_recoverable_messages tests/test_integration.py::test_api_runs_decisions_export_replay tests/test_integration.py::test_api_import_with_mapping_and_provenance
```

## QA-44

- **TEST_ID:** QA-44
- **NOMBRE:** Auditoría sin servicios externos
- **COMPONENTE:** core/CLI/UI
- **RIESGO:** Dependencia remota exfiltra o impide auditar
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-19 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Fixturesinstalados; socket externo bloqueado; navegador request monitor
- **PASOS_EXACTOS:** 1. Bloquear network en core/CLI. 2. Importar,auditar,exportar,replay. 3. NavegarUI conmonitor y comparar destinos.
- **RESULTADO_ESPERADO:** Audit/exports íntegros offline;UI sólo loopback; instalación inicial de dependencias no se confunde con operaciónoffline.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Instalaciónrequierepaquetes ya disponibles; no es unallamadaoculta de auditoría.
- **FALSOS_NEGATIVOS:** Monkeypatchsocket no detecta subprocesos o navegador externo.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration; E2E
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_integration.py::test_fully_offline_core
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 24.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_fully_offline_core
```

## QA-45

- **TEST_ID:** QA-45
- **NOMBRE:** Representación contractual y mapping aprobados
- **COMPONENTE:** configuration/operator
- **RIESGO:** Regla válida matemáticamente representa mal el acuerdo
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-07 INV-08 INV-13
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Contrato y ejemplos verdaderos; mínimo porservicio/remito; temporalporcomponente; columnaimporteambigua
- **PASOS_EXACTOS:** 1. Aplicarprotocolo pasos1..10. 2. Crear hoja manualantesdelmotor. 3. Confirmar representaciónconcliente. 4. Congelarhashes y dudas.
- **RESULTADO_ESPERADO:** Toda regla material tiene responsable y ejemplo independiente; desconocido bloquea certeza, no default de industria.
- **ORACULO:** OR-01 OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Práctica nueva legítima no es bug hasta compararconcontratoconfirmado.
- **FALSOS_NEGATIVOS:** Tests sintéticos pueden pasar con contrato equivocado.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** manual
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** antes de cliente real; cambio contractual
- **RESPUESTA_SI_FALLA:** IR-15 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** según contrato; medir horas
- **DATOS_REALES:** sí
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-46

- **TEST_ID:** QA-46
- **NOMBRE:** Generalidad de cinco arquetipos
- **COMPONENTE:** configuration/core
- **RIESGO:** Cliente nuevo requiere excepciones exclusivas
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-26 INV-13
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** ArquetiposA..EdeQA_CASES; mismosIDs/preciosdiferentes;Ebasepickup+extradelivery
- **PASOS_EXACTOS:** 1. Configurarsincambiarcore. 2. Calcularmanual. 3. Ejecutaryregistrararchivostocados. 4. SiEnocabe fielmente,documentarabstracciónfaltante.
- **RESULTADO_ESPERADO:** A31.5,B900,Cbandas/pallet/evidencia,D194.25USD, E100+12 separado sólo si fiel al contrato. Sinif cliente/sector/carrier encore.
- **ORACULO:** OR-01 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Cambio reutilizable justificado delcore no equivale a custom.
- **FALSOS_NEGATIVOS:** QuintoarquetipoE no está ejercitadoporeltest existente.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-15 IR-13 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_integration.py::test_real_files_three_agreements_golden_and_second_client
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 12.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_integration.py::test_real_files_three_agreements_golden_and_second_client
```

## QA-47

- **TEST_ID:** QA-47
- **NOMBRE:** Paquete y plataforma real
- **COMPONENTE:** packaging/OS
- **RIESGO:** Checkoutfunciona pero instalación pierde archivos o cambia importación
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-21 INV-23
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Wheel/sdist recién construidos; directorioajenoalrepo; Linux y Windows de uso
- **PASOS_EXACTOS:** 1. Instalarpaqueteaislado. 2. SmokeconUIstatic/demo/replay/export. 3. Compararcontenidos/hash. 4. Windows: rutasUnicode,longitudes,lineendings,Excel real.
- **RESULTADO_ESPERADO:** Importdesdepaqueteinstalado,noeditable; recursoscompletos; equivalenciaeconómica. Windowsnoaprobadosinmáquinareal.
- **ORACULO:** OR-04 OR-06 OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** FechasZIPybuildhashpuedencambiar sin cambioeconómico; comparararchivos materialmente.
- **FALSOS_NEGATIVOS:** LinuxCI no valida Windows ni aplicaciónExcel.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** B
- **CUANDO:** release; antes de cliente real
- **RESPUESTA_SI_FALLA:** IR-07 IR-08 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 6.0
- **ESFUERZO_IMPLEMENTACION:** 1–2 días
- **DATOS_REALES:** no
- **WINDOWS:** sí
- **INTERVENCION_HUMANA:** no

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-48

- **TEST_ID:** QA-48
- **NOMBRE:** Escala, memoria y tiempos de todas las etapas
- **COMPONENTE:** performance
- **RIESGO:** Cierre real excedeRAM o timeout y salida parece completa
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-25
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** 10kS/50kC y100kC; trazascompletas;tabla10ktarifas;mediciónporfase
- **PASOS_EXACTOS:** 1. Unproceso/tamañoconRSSbaseline. 2. Medirimport/audit/hash/save/export/UIporseparado. 3. Conciliarcantidadesysumasalterminar.
- **RESULTADO_ESPERADO:** Sinpérdida/resultadoequivocado;presupuestooperativoacordado. Baselinescore15.953s/945.9MiB y31.577s/1821.2MiB no sonSLAend-to-end.
- **ORACULO:** OR-03 OR-10
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Ruido de carga/maquinadistinta no es regresión causal.
- **FALSOS_NEGATIVOS:** Benchmarksinpersistencia/reportes oculta pico real delcierre.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** benchmark
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P2
- **GRUPO:** B
- **CUANDO:** cambio algorítmico; volumen nuevo; release relevante
- **RESPUESTA_SI_FALLA:** IR-12 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 6.0
- **ESFUERZO_IMPLEMENTACION:** 1–3 días
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-49

- **TEST_ID:** QA-49
- **NOMBRE:** Los verificadores detectan corrupción
- **COMPONENTE:** QA/oracles
- **RIESGO:** Checker pasa todo o importa lógica defectuosa del motor
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-01 INV-04 INV-23
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Runválido y copias conconfirmedfake,IDduplicado,sumamutada,labelFAILenXLSX,missingrow
- **PASOS_EXACTOS:** 1. Esperarchecklimpiodebaseline. 2. Modificarunacausa por copia. 3. Exigirmensajeidentificableyexit1. 4. Inputmalformadoexit2.
- **RESULTADO_ESPERADO:** Cada manipulaciónobjetivorechazada;nocoreimportsenqa/referenceorinvariants;pendientesclaros,noformatoPythonassertcomoúnicobarreraCLI.
- **ORACULO:** OR-01 OR-03 OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Corregircapturaincompletaantesdeatribuirfallaalproducto.
- **FALSOS_NEGATIVOS:** Sólo probarqueunbuenrunpasa no pruebaqueelchecker sirva.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** mutation; unit
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-08 IR-06 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption; tests/test_qa_infrastructure.py::test_cross_report_reconciliation_and_tamper_detection
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption tests/test_qa_infrastructure.py::test_cross_report_reconciliation_and_tamper_detection
```

## QA-50

- **TEST_ID:** QA-50
- **NOMBRE:** Mutantes críticos dirigidos
- **COMPONENTE:** mutation infrastructure
- **RIESGO:** Tests verdes no detectan eliminación de defensas
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-01 INV-02 INV-06 INV-07 INV-09
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** qa/mutants.json, copias temporales src/tests/fixtures; baseline sano
- **PASOS_EXACTOS:** 1. Validaranclaúnica. 2. Ejecutarbaselineenlacopia. 3. Aplicarunmutante. 4. Ejecutarsusselectores. 5. Requerirfailuredeassert,no collectionerror/timeout.
- **RESULTADO_ESPERADO:** Mutacionesdesigno,tolerancia,moneda,versiónyevidencia mueren porassert causal; sobreviviente bloqueafeature;incompetente/inconclusivo no cuenta muerto.
- **ORACULO:** OR-01 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** CambiosdeAPIoanclahacenmutanteobsoleto,noequivalente.
- **FALSOS_NEGATIVOS:** Fallodehashglobalmata mutante sin ejercitar invariante; revisar causalidad.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** mutation
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio de defensa; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-06 IR-03 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–4 h por mutante nuevo
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-51

- **TEST_ID:** QA-51
- **NOMBRE:** Validación ciega con cliente
- **COMPONENTE:** field validation
- **RIESGO:** Confundir coincidencia sintética con seguridad económica real
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-12 INV-13 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Períodoverdaderoycontrolhistóricoconcustodioseparado;REAL_CLIENT_VALIDATION_PROTOCOL
- **PASOS_EXACTOS:** 1. Congelarrepresentaciónycorridaantesdevercontrol. 2. Compararporcargo/moneda. 3. RevisarfalsosPASS/FAILyconocidas/nuevas/desconocidas. 4. Registrarhoras.
- **RESULTADO_ESPERADO:** Verdadcontrasteexterna; nueva correctanoequivalearecupero; no ajustarprimera corrida trasverrespuestas sin conservarla.
- **ORACULO:** OR-01 OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Diferentealcance/períodonopermitecompararmontosdirectamente.
- **FALSOS_NEGATIVOS:** Controlhistórico también puedeestar equivocado; requerir resoluciónindependiente.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** manual
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** B
- **CUANDO:** antes de cliente real; nuevo arquetipo
- **RESPUESTA_SI_FALLA:** IR-15 IR-01 IR-02 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 7.5
- **ESFUERZO_IMPLEMENTACION:** según período; medir
- **DATOS_REALES:** sí
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-52

- **TEST_ID:** QA-52
- **NOMBRE:** Gate de pago sin nuestra supervisión
- **COMPONENTE:** release/use policy
- **RIESGO:** Habilitaruso sensible por cantidad de tests verdes
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-01 INV-21 INV-25 INV-26
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** GateUdeRELEASE_CRITERIA; evidencias reales/operativas/Windows según alcance
- **PASOS_EXACTOS:** 1. EvaluarcadaobligaciónGateU. 2. Anotarpendientes/incidentes/desconocidos. 3. Exigirrestriccionesefectivas/restore/identidad/totaldocumental.
- **RESULTADO_ESPERADO:** GateUcerradoen0.1.0; ninguna estadística sintética lo abre; no sustituiraprobacióncontractualconpytest.
- **ORACULO:** OR-01 OR-06 OR-10
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Noexigirestegateparadesarrolloofflineconficticios.
- **FALSOS_NEGATIVOS:** Confundirpilotoconsupervisión con aprobaciónautónoma.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** manual
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** B
- **CUANDO:** antes de habilitar decisiones sin supervisión
- **RESPUESTA_SI_FALLA:** IR-15 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 7.5
- **ESFUERZO_IMPLEMENTACION:** no estimable sin piloto
- **DATOS_REALES:** sí
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-53

- **TEST_ID:** QA-53
- **NOMBRE:** IDs y JSON inequívocos
- **COMPONENTE:** serialization/models
- **RIESGO:** Clave duplicada o IDcolisionado cambia interpretación
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-04 INV-26
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** JSONconamount1 y100repetidos;S/C/A/EIDsduplicados;datosmalformados/unknownfield
- **PASOS_EXACTOS:** 1. LeerJSONconparserproducto. 2. Validarduplicadosporentidad. 3. Verificarrechazosimportvisibles. 4. ProbarcheckerJSONestricto.
- **RESULTADO_ESPERADO:** Clavesrepetidas/nonfinite/extra fields rechazados; ninguna filaúltimagana silenciosamente;duplicados deimportsevisibilizan.
- **ORACULO:** OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** MismoIDentreentidades diferentes puede ser válido; espacio deIDs es porentidad.
- **FALSOS_NEGATIVOS:** ParserdeherramientaQA permisivopuedeaceptarloqueproductorechaza.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** fuzz; unit
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 IR-13 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_adversarial.py::test_duplicate_json_keys_are_rejected; tests/test_importing.py::test_duplicate_business_ids_visible_not_silently_deduplicated
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_adversarial.py::test_duplicate_json_keys_are_rejected tests/test_importing.py::test_duplicate_business_ids_visible_not_silently_deduplicated
```

## QA-54

- **TEST_ID:** QA-54
- **NOMBRE:** Bundle portable y ancla externa
- **COMPONENTE:** archive/integrity
- **RIESGO:** Paquete alterado parece evidencia confiable
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-21 INV-22 INV-28
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** ZIPdemo;mutararchivo/manifest/snapshot/decisión;duplicateentries/fuentefaltante/pathhostil
- **PASOS_EXACTOS:** 1. Verificarmanifestmásrunmáschainmásfuentes. 2. CompararhashZIPconanclaexterna. 3. Mutaruncomponente. 4. NoextraerZIPajeno para verificar.
- **RESULTADO_ESPERADO:** Cadaalteración detectadarelativaancla;manifestautoconsistente no pruebaautenticidad;metadatafueradehash se informa.
- **ORACULO:** OR-06 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** ZIPlegítimoreexportado puedecambiartimestamps/hash decontenedor.
- **FALSOS_NEGATIVOS:** Atacantepuederehacertodosloshashes;sinanclano hay autenticación.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** security; integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-10 IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_storage_reporting.py::test_portable_bundle_integrity
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_storage_reporting.py::test_portable_bundle_integrity
```

## QA-55

- **TEST_ID:** QA-55
- **NOMBRE:** Entrega reproducible y dependencias
- **COMPONENTE:** Git/build/environment
- **RIESGO:** Tests locales prueban archivos distintos de los entregados
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-21 INV-19
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Commitlimpio;checkoutaislado;lock;originalesconCRLFySHA;wheel/sdist
- **PASOS_EXACTOS:** 1. Compararárbolversionado/materiales. 2. Instalaryprobarencheckoutlimpio. 3. Registrarhuellasdelpaquete/deps. 4. VerificarsemánticaconLFsinexigirSHAdeloriginalCRLF.
- **RESULTADO_ESPERADO:** Códigoentregado coincideconverificado;datosoriginales mantienenhashpropiodesusbytes;sinsecrets/DB/outputenGit. No asumir buildsbit-identicalsinsello reproducible.
- **ORACULO:** OR-06 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Normalizarnewline cambiabytes/provenance pero noeconomía si parsingesigual.
- **FALSOS_NEGATIVOS:** Editableinstall puedeocultar recurso faltante enwheel.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** B
- **CUANDO:** release; cambio de dependencias
- **RESPUESTA_SI_FALLA:** IR-09 IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 12.0
- **ESFUERZO_IMPLEMENTACION:** 4–8 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-56

- **TEST_ID:** QA-56
- **NOMBRE:** Separación de liquidaciones y alcance de obligación
- **COMPONENTE:** grouping/domain
- **RIESGO:** Sumar cargos de servicios/períodos distintos por clave incompleta
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-05 INV-09 INV-13
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** SrefR;C100L1yC100L2;base100;clientedefine2serviciosindependientes
- **PASOS_EXACTOS:** 1. Revisargroup_keyycontrato. 2. Ejecutarsinperiodoenclave. 3. Configurarperíodo/servicioexplícito conoperacionescorrectas. 4. Comparargrafoobligaciones.
- **RESULTADO_ESPERADO:** Dosobligacionesindependientesno se comparancontrau nE100. Elcoreactualnoincluyesettlementenagrupación: mapping/scope confirmadosodeclararcaso no soportado.
- **ORACULO:** OR-01 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Doslíneasdefacturaspuedencompletarunservicio;noasumirsiempreindependientes.
- **FALSOS_NEGATIVOS:** Fixturesdeunúnicoperíodonoejercitanesteerrorcausal.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** nuevo formato; cambio de matching; antes de cliente real
- **RESPUESTA_SI_FALLA:** IR-04 IR-15 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diseñado
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 4–8 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.

## QA-57

- **TEST_ID:** QA-57
- **NOMBRE:** Diagnóstico no muta evidencia
- **COMPONENTE:** QA/forensics
- **RIESGO:** Herramienta deincidente inicializa/migraDB original
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-30 INV-28
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DBreadonly, schemafuturo/incompleto, filaJSONcorrupta; hashesprevios
- **PASOS_EXACTOS:** 1. Ejecutarimpactenmode=ro. 2. Intentarinputinexistente. 3. Compararbytes/schema/triggersantesdespués. 4. Corruptoapareceunknown o errorglobal explícito.
- **RESULTADO_ESPERADO:** NoStoreconstructor,nocreaciónDB/nuevostriggers; ninguna selección vacía falsa por corrupción.
- **ORACULO:** OR-06 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** UnDBactivo puede cambiar porprocesoproductivo;congelarcopia para compararhash.
- **FALSOS_NEGATIVOS:** Chequearsolomtime no demuestraausenciademutación.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-12 IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** tests/test_qa_infrastructure.py::test_impact_is_read_only_and_retains_unknowns
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 30.0
- **ESFUERZO_IMPLEMENTACION:** 2–6 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_qa_infrastructure.py::test_impact_is_read_only_and_retains_unknowns
```

## QA-58

- **TEST_ID:** QA-58
- **NOMBRE:** Píxel exacto y matrices visuales exhaustivas
- **COMPONENTE:** cosmetic UI
- **RIESGO:** Desviación estética sin impacto enlectura
- **SEVERIDAD:** LOW
- **INVARIANTE:** INV-23 (sólo si cambia significado)
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** TodaslascombinacionesdeSO/fuentes/anchos, sin defectoseconómicos conocidos
- **PASOS_EXACTOS:** 1. Diferirpixelperfect. 2. Conservar sólo prueba de texto/contraste/overflow material enQA39. 3. Reconsiderar ante fallo real de lectura.
- **RESULTADO_ESPERADO:** No gastarbudgetenmatrizestéticaexhaustiva; cualquierimporte/labeloculto escala aQA39/P0.
- **ORACULO:** OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Antialiasing/fuenteproduce diffsinerroroperativo.
- **FALSOS_NEGATIVOS:** Descartardiseñovisualnoautorizaocultar moneda/estado.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** E2E
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** bajo
- **PRIORIDAD:** P3
- **GRUPO:** C
- **CUANDO:** sólo si aparece necesidad material
- **RESPUESTA_SI_FALLA:** IR-08 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** diferido
- **SELECTORES:** Pendiente: sin selector automatizado
- **IMPACTO:** 1
- **PROBABILIDAD:** 2
- **DIFICULTAD_DETECCION:** 1
- **RIESGO_SCORE:** 2
- **VALOR_POR_COSTO:** 0.25
- **ESFUERZO_IMPLEMENTACION:** diferido
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

No hay automatización completa registrada. Implementar/ejecutar los pasos y preservar evidencia antes de cerrar esta familia.
