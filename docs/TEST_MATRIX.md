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
| [QA-29](#qa-29) | Aislamiento entre clientes y catálogos | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-30](#qa-30) | Decisiones humanas y cadena | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-31](#qa-31) | Integridad histórica y mutación | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-32](#qa-32) | Replay y cambio de artefacto | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-33](#qa-33) | Proveniencia de ejecutables y alcance | CRITICAL | P0 / A | nuevo | 60 / 30 |
| [QA-34](#qa-34) | Backup, restore y reapertura | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-35](#qa-35) | Crash, rollback y concurrencia | CRITICAL | P0 / B | parcial | 60 / 7.5 |
| [QA-36](#qa-36) | Schema y migración recuperable | CRITICAL | P0 / B | parcial | 60 / 7.5 |
| [QA-37](#qa-37) | Reconciliación entre representaciones | CRITICAL | P0 / A | nuevo | 60 / 15 |
| [QA-38](#qa-38) | Límites de reportes y contenido activo | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-39](#qa-39) | UI conserva semántica visible y estado actual | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-40](#qa-40) | Barrera de red local | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-41](#qa-41) | Rutas, archivos y sobrescritura | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-42](#qa-42) | XML/ZIP malicioso acotado | CRITICAL | P0 / A | parcial | 60 / 15 |
| [QA-43](#qa-43) | Errores de API y consistencia de operación | HIGH | P1 / A | parcial | 48 / 24 |
| [QA-44](#qa-44) | Auditoría sin servicios externos | HIGH | P1 / A | parcial | 48 / 24 |
| [QA-45](#qa-45) | Representación contractual y mapping aprobados | CRITICAL | P0 / A | diseñado | 60 / 15 |
| [QA-46](#qa-46) | Generalidad de cinco arquetipos | HIGH | P1 / A | parcial | 48 / 12 |
| [QA-47](#qa-47) | Paquete y plataforma real | HIGH | P1 / B | parcial | 48 / 6 |
| [QA-48](#qa-48) | Escala, memoria y tiempos de todas las etapas | HIGH | P2 / B | parcial | 48 / 6 |
| [QA-49](#qa-49) | Los verificadores detectan corrupción | CRITICAL | P0 / A | nuevo | 60 / 30 |
| [QA-50](#qa-50) | Mutantes críticos dirigidos | CRITICAL | P0 / A | nuevo | 60 / 15 |
| [QA-51](#qa-51) | Validación ciega con cliente | CRITICAL | P0 / B | diseñado | 60 / 7.5 |
| [QA-52](#qa-52) | Gate de pago sin nuestra supervisión | CRITICAL | P0 / B | diseñado | 60 / 7.5 |
| [QA-53](#qa-53) | IDs y JSON inequívocos | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-54](#qa-54) | Bundle portable y ancla externa | CRITICAL | P0 / A | parcial | 60 / 30 |
| [QA-55](#qa-55) | Entrega reproducible y dependencias | HIGH | P1 / B | parcial | 48 / 12 |
| [QA-56](#qa-56) | Separación de liquidaciones y alcance de obligación | CRITICAL | P0 / A | parcial | 60 / 15 |
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RESULTADO_ESPERADO:** Varias hojas sin selección error; fórmula mapeada rechazada; sin fill-forward. Hoja o datos ocultos bloquean la importación hasta hacerlos visibles y revisar el alcance.
- **ORACULO:** OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Fila oculta puede ser legítima; no descartarla por defecto.
- **FALSOS_NEGATIVOS:** Los casos de ocultamiento probados no cubren todos los productores, estilos, merges ni caches reales.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** fuzz; manual
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-07 IR-15 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_multisheet_requires_selection; tests/test_importing.py::test_xlsx_formula_never_evaluated_or_taken_as_cache; tests/test_importing.py::test_original_numeric_tokens_follow_sparse_sheet_coordinates; tests/test_importing.py::test_xlsx_hidden_business_data_blocks_import_until_made_visible; tests/test_importing.py::test_xlsx_hidden_selected_sheet_blocks_import
- **RUNNERS:** Pendiente: sin selector automatizado
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
.venv/bin/python -m pytest -q tests/test_importing.py::test_multisheet_requires_selection tests/test_importing.py::test_xlsx_formula_never_evaluated_or_taken_as_cache tests/test_importing.py::test_original_numeric_tokens_follow_sparse_sheet_coordinates tests/test_importing.py::test_xlsx_hidden_business_data_blocks_import_until_made_visible tests/test_importing.py::test_xlsx_hidden_selected_sheet_blocks_import
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FALSOS_NEGATIVOS:** El comparador sólo detecta omisiones incluidas en un inventario externo independiente; no puede demostrar que ese inventario sea verdadero/completo ni reemplaza la validación humana.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** bajo
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-02 IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_engine.py::test_import_rejects_block_economic_confirmation; tests/test_integration.py::test_invalid_fixture_rejects_visible_rows; tests/test_external_control.py::test_external_inventory_count_and_total_are_independent_blockers; tests/test_external_control.py::test_external_control_cli_exit_codes_and_hash_integrity
- **RUNNERS:** .venv/bin/python scripts/qa.py external-control ARCHIVO_AUDIT_JSON CONTROL_EXTERNO_JSON
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
.venv/bin/python -m pytest -q tests/test_engine.py::test_import_rejects_block_economic_confirmation tests/test_integration.py::test_invalid_fixture_rejects_visible_rows tests/test_external_control.py::test_external_inventory_count_and_total_are_independent_blockers tests/test_external_control.py::test_external_control_cli_exit_codes_and_hash_integrity
```

```bash
.venv/bin/python scripts/qa.py external-control ARCHIVO_AUDIT_JSON CONTROL_EXTERNO_JSON
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RESULTADO_ESPERADO:** Ambigua/invalid/hora/zona→rechazo; medianoche ingenua admitida. Serial ficticio60 del calendario1900 se rechaza; serial60 de1904 es01/03/1904.
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
- **SELECTORES:** tests/test_importing.py::test_ambiguous_date_is_rejected; tests/test_importing.py::test_excel_fictitious_leap_day_never_aliases_real_date; tests/test_importing.py::test_timestamps_are_not_silently_truncated; tests/test_engine.py::test_alternate_date_field
- **RUNNERS:** Pendiente: sin selector automatizado
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
.venv/bin/python -m pytest -q tests/test_importing.py::test_ambiguous_date_is_rejected tests/test_importing.py::test_excel_fictitious_leap_day_never_aliases_real_date tests/test_importing.py::test_timestamps_are_not_silently_truncated tests/test_engine.py::test_alternate_date_field
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_backlog_p0_p1.py::test_qa29_client_catalog_and_storage_isolation
- **RUNNERS:** Pendiente: sin selector automatizado
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
.venv/bin/python -m pytest -q tests/test_backlog_p0_p1.py::test_qa29_client_catalog_and_storage_isolation
```

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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RESULTADO_ESPERADO:** Mismo artefacto: resultado exacto. Integridad fallida, artefacto distinto o proceso desactualizado bloquean replay. Reimportar es otra operación.
- **ORACULO:** OR-06 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Rechazar otro artefacto no demuestra falta de determinismo.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Base histórica sin importer_hash ni client_id; operador configurado pero no ejecutado; corrida dañada.
- **PASOS_EXACTOS:** 1. Ejecutar impact con --feature const y --importer-hash distinto. 2. Conservar desconocidos como candidatos. 3. Contrastar inventario manual. 4. Comparar bytes de la base antes/después.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Base con dos corridas, decisiones y fuentes; destino nuevo para backup y otro ya existente.
- **PASOS_EXACTOS:** 1. Crear backup con la API. 2. Restaurar en otra ruta. 3. Verificar inventario, hashes, decisiones, fuentes y replay con el artefacto original. 4. Intentar sobrescribir el destino existente.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Subproceso sobre copia de base; fallo antes/después de INSERT y commit; dos corridas simultáneas; disco lleno simulado.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Base vacía, schema v1, schema futuro v2, v0 no vacío y schema incompleto; futura migración interrumpida.
- **PASOS_EXACTOS:** 1. Abrir copias de cada estado. 2. Para una futura migración: preservar backup con hash externo, interrumpir antes/después de cada DDL y restaurar/reintentar. 3. Comparar corridas históricas y originales.
- **RESULTADO_ESPERADO:** Vacía inicializa schema 1; versión futura se rechaza; v1 reabre sin cambios. v0 no vacío o incompleto requiere validación pendiente. No se certifica una migración real.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Corrida ficticia con cuatro estados y dos monedas; ocho hojas XLSX; JSON y HTML exportados; respuesta API y observación DOM.
- **PASOS_EXACTOS:** 1. Verificar integridad e invariantes. 2. Leer salidas con lectores independientes. 3. Comparar filas, monedas, estados, importes y resúmenes. 4. Alterar cada salida por separado y exigir detección.
- **RESULTADO_ESPERADO:** Campos materiales exactos; filas completas y sin fórmulas. API y DOM sólo se cubren al aportar capturas independientes. Un canal ausente queda pendiente.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Texto de 32768 caracteres, límite de filas reducido en test, nota con =HYPERLINK o script, importes de 36 dígitos.
- **PASOS_EXACTOS:** 1. Exportar. 2. Revisar tipos y cantidad de celdas. 3. Forzar límite y verificar ZIP sin XLSX, advertencia explícita y JSON completo. 4. Inspeccionar escape del HTML.
- **RESULTADO_ESPERADO:** No se entrega un XLSX parcial; texto explícito sin fórmulas; JSON íntegro y advertencia de omisión conservada.
- **ORACULO:** OR-07 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Texto exacto en Excel no es celda numérica sumable automáticamente.
- **FALSOS_NEGATIVOS:** Probar un límite reducido no mide la memoria real para 100000 filas.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Dos corridas similares; importe textual 1000000000000000.01; 150 hallazgos; cuatro estados y decisión humana distinta del estado del motor.
- **PASOS_EXACTOS:** 1. Capturar DOM de todas las páginas y filtros. 2. Cambiar rápidamente de corrida, abrir detalle y registrar decisión. 3. Comparar valores y etiquetas con la corrida exacta. 4. Probar importes con cero y tres decimales.
- **RESULTADO_ESPERADO:** Dinero sin conversión a Number/float; paginación y filtros no cambian métricas globales. Estado del motor y decisión separados; solicitudes sólo a loopback.
- **ORACULO:** OR-07 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Captura de una página no equivale al lote entero; registrar filtro.
- **FALSOS_NEGATIVOS:** Una respuesta exitosa de API no prueba qué leyó el operador.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** E2E
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-08 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** Pendiente: sin selector automatizado
- **RUNNERS:** .venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/qa39-new
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 1–2 días
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/qa39-new
```

## QA-40

- **TEST_ID:** QA-40
- **NOMBRE:** Barrera de red local
- **COMPONENTE:** server/CLI
- **RIESGO:** Página ajena opera sobre datos locales
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-26 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Host malicioso, Origin ajeno, token faltante o erróneo, preflight CORS y socket real del servicio.
- **PASOS_EXACTOS:** 1. Enviar POST con y sin token y Origin válidos. 2. Verificar bind a 127.0.0.1 en el proceso CLI. 3. Probar lectura desde otro origen en navegador. 4. Inspeccionar efectos en la base.
- **RESULTADO_ESPERADO:** Host, Origin o token incorrectos se rechazan; CORS sin orígenes ajenos; servicio sólo en loopback. Un rechazo con efectos previos en la base es un fallo.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Token local no autentica usuarios del mismo equipo.
- **FALSOS_NEGATIVOS:** El E2E de Chromium/Linux no prueba firewall ni aislamiento frente a otros usuarios del equipo; falta matriz Windows.
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
- **RUNNERS:** .venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/qa40-new
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

```bash
.venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/qa40-new
```

## QA-41

- **TEST_ID:** QA-41
- **NOMBRE:** Rutas, archivos y sobrescritura
- **COMPONENTE:** upload/export/backup
- **RIESGO:** Lectura/escritura fuera del destino permitido
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-25 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Archivo testigo externo; ../../name, ruta absoluta, ruta Windows, enlace simbólico y destino existente.
- **PASOS_EXACTOS:** 1. Subir un archivo con nombre hostil. 2. Exportar y crear backup en destinos temporales existentes y enlaces simbólicos. 3. Verificar el testigo y archivos modificados. 4. Usar sólo datos sintéticos.
- **RESULTADO_ESPERADO:** Uploads identificados por hash; sin lectura ni escritura arbitrarias; sobrescritura rechazada. Verificar política de enlaces simbólicos antes de usar rutas compartidas.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** CLI acepta ruta elegida por operador; no confundirla con ruta controlada por upload.
- **FALSOS_NEGATIVOS:** La comprobación de enlaces no detiene a otro proceso del mismo usuario que cambie directorios durante la escritura; falta ejecutar la matriz nativa Windows.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** security
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_security_paths.py::test_export_rejects_existing_and_redirected_directories; tests/test_security_paths.py::test_foreign_platform_drive_syntax_is_not_a_local_relative_output; tests/test_security_paths.py::test_backup_publishes_only_completed_copy_without_overwrite; tests/test_security_paths.py::test_export_marks_interrupted_or_invalid_package; tests/test_integration.py::test_upload_filename_is_only_a_label_and_never_an_output_path
- **RUNNERS:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 1–2 días
- **DATOS_REALES:** no
- **WINDOWS:** sí
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_security_paths.py::test_export_rejects_existing_and_redirected_directories tests/test_security_paths.py::test_foreign_platform_drive_syntax_is_not_a_local_relative_output tests/test_security_paths.py::test_backup_publishes_only_completed_copy_without_overwrite tests/test_security_paths.py::test_export_marks_interrupted_or_invalid_package tests/test_integration.py::test_upload_filename_is_only_a_label_and_never_an_output_path
```

## QA-42

- **TEST_ID:** QA-42
- **NOMBRE:** XML/ZIP malicioso acotado
- **COMPONENTE:** XLSX/bundle
- **RIESGO:** Entidades externas, bomb o entrada ambigua supera defensa
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-25 INV-30
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** DTD pequeña con entidad hacia archivo testigo; entradas ZIP repetidas o con ../; tamaños declarados y reales; presupuesto de proceso.
- **PASOS_EXACTOS:** 1. Generar un archivo sintético pequeño. 2. Ejecutar en subproceso sin red y con límites. 3. Registrar rechazo, salidas, red y testigo. 4. Verificar expansión efectiva y cabecera.
- **RESULTADO_ESPERADO:** Sin ejecución de contenido, red ni lectura externa; error recuperable; ninguna corrida económica parcial. Archivos sintéticos y acotados.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Rechazo genérico de corrupción es aceptable si no hay efecto y orienta recuperación.
- **FALSOS_NEGATIVOS:** DTD y ZIP ambiguo sintéticos no prueban todos los productores XML ni el pico de descompresión real bajo un límite de proceso.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** fuzz; security
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio afectado; CI; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-14 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified; tests/test_importing.py::test_xlsx_duplicate_or_traversal_entry_is_rejected; tests/test_importing.py::test_xlsx_external_entity_never_becomes_imported_value
- **RUNNERS:** Pendiente: sin selector automatizado
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
.venv/bin/python -m pytest -q tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified tests/test_importing.py::test_xlsx_duplicate_or_traversal_entry_is_rejected tests/test_importing.py::test_xlsx_external_entity_never_becomes_imported_value
```

## QA-43

- **TEST_ID:** QA-43
- **NOMBRE:** Errores de API y consistencia de operación
- **COMPONENTE:** FastAPI
- **RIESGO:** 422/500 oculta escritura parcial o resultado diferente a CLI
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-25 INV-29
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Mapping inválido, campo extra, ID ajeno, upload mayor de 32 MiB y misma entrada válida por CLI/API.
- **PASOS_EXACTOS:** 1. Registrar inventario de la base. 2. Enviar petición inválida. 3. Comparar fuentes y configuraciones conservadas con corridas creadas. 4. Enviar entrada válida y contrastar con CLI.
- **RESULTADO_ESPERADO:** Error recuperable sin traceback para el usuario; ninguna corrida parcial; mismo resultado económico por CLI/API; sin datos sensibles expuestos.
- **ORACULO:** OR-03 OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** La vista previa puede conservar una fuente o configuración sin ejecutar la auditoría.
- **FALSOS_NEGATIVOS:** Comprobar sólo el código de respuesta ignora el cuerpo y los efectos persistidos.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Fixtures instalados, conexiones externas bloqueadas y monitor de solicitudes del navegador.
- **PASOS_EXACTOS:** 1. Bloquear conexiones externas para core y CLI. 2. Importar, auditar, exportar y reproducir. 3. Navegar la UI y revisar destinos de todas las solicitudes.
- **RESULTADO_ESPERADO:** Auditoría y exportaciones íntegras sin red; UI sólo en loopback. Evaluar instalación inicial de dependencias por separado.
- **ORACULO:** OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Instalar sin red requiere paquetes previos; esto no demuestra dependencia remota durante la auditoría.
- **FALSOS_NEGATIVOS:** Interceptar sockets de Python no cubre subprocesos ni navegador.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Contrato y ejemplos reales; mínimo por servicio o remito; fecha por componente; columna de importe ambigua.
- **PASOS_EXACTOS:** 1. Aplicar pasos 1–10 del protocolo de cliente real. 2. Calcular hoja manual antes de ejecutar el motor. 3. Confirmar representación con el cliente. 4. Preservar hashes y dudas.
- **RESULTADO_ESPERADO:** Toda regla material tiene responsable y ejemplo independiente; desconocido bloquea certeza, no default de industria.
- **ORACULO:** OR-01 OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Una práctica nueva no es un bug hasta compararla con el contrato confirmado.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Arquetipos A–E de QA_CASES; mismos IDs y precios diferentes; E con base por pickup y adicional por delivery.
- **PASOS_EXACTOS:** 1. Configurar sin cambiar el core. 2. Calcular manualmente. 3. Ejecutar y registrar archivos modificados. 4. Si E no puede representarse fielmente, documentar la abstracción faltante.
- **RESULTADO_ESPERADO:** A: 31.5; B: 900; C: bandas, pallets y evidencia; D: 194.25 USD; E: 100 + 12 con acuerdos separados sólo si representan el contrato. Sin condiciones por cliente, sector o transportista en el core.
- **ORACULO:** OR-01 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Un cambio reutilizable y justificado del core no equivale a una excepción exclusiva de cliente.
- **FALSOS_NEGATIVOS:** El test existente no ejercita el quinto arquetipo E.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RIESGO:** El checkout funciona pero el paquete instalado pierde recursos o cambia la importación.
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-21 INV-23
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Wheel y sdist recién construidos; directorio fuera del repositorio; Linux y Windows del entorno de uso.
- **PASOS_EXACTOS:** 1. Instalar paquete aislado. 2. Comprobar recursos UI, demo, replay y exportación. 3. Comparar contenidos y hashes. 4. En Windows: rutas Unicode, longitudes, saltos de línea y Excel real.
- **RESULTADO_ESPERADO:** Importación desde paquete instalado sin modo editable; recursos completos y equivalencia económica. Windows pendiente hasta probarlo en una máquina real.
- **ORACULO:** OR-04 OR-06 OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Fechas ZIP y hashes del build pueden cambiar sin cambio económico; comparar contenido de archivos.
- **FALSOS_NEGATIVOS:** Instalar wheel y sdist en Linux no valida rutas ni Excel de escritorio en Windows.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** B
- **CUANDO:** release; antes de cliente real
- **RESPUESTA_SI_FALLA:** IR-07 IR-08 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** Pendiente: sin selector automatizado
- **RUNNERS:** .venv/bin/python scripts/verify_delivery.py --output output/delivery-verification.json
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 6.0
- **ESFUERZO_IMPLEMENTACION:** 1–2 días
- **DATOS_REALES:** no
- **WINDOWS:** sí
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python scripts/verify_delivery.py --output output/delivery-verification.json
```

## QA-48

- **TEST_ID:** QA-48
- **NOMBRE:** Escala, memoria y tiempos de todas las etapas
- **COMPONENTE:** performance
- **RIESGO:** Un cierre real agota memoria o tiempo y entrega una salida aparentemente completa.
- **SEVERIDAD:** HIGH
- **INVARIANTE:** INV-25
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** 10000 operaciones con 50000 y 100000 cargos; trazas completas; tabla de 10000 tarifas; medición por fase.
- **PASOS_EXACTOS:** 1. Un proceso por tamaño con memoria base registrada. 2. Medir importación, motor, hashes, persistencia, exportación y UI por separado. 3. Conciliar cantidades y sumas al terminar.
- **RESULTADO_ESPERADO:** Sin pérdida ni resultado incorrecto y dentro del presupuesto operativo acordado. Las mediciones históricas del core en VERIFICATION.md no constituyen un SLA de todo el flujo.
- **ORACULO:** OR-03 OR-10
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Carga concurrente o máquina distinta pueden cambiar tiempos sin regresión causal.
- **FALSOS_NEGATIVOS:** El pipeline de 1000 cargos no extrapola 50000/100000 ni mide un navegador con esos hallazgos.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** benchmark
- **COSTO_EJECUCION:** alto
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P2
- **GRUPO:** B
- **CUANDO:** cambio algorítmico; volumen nuevo; release relevante
- **RESPUESTA_SI_FALLA:** IR-12 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** Pendiente: sin selector automatizado
- **RUNNERS:** .venv/bin/python output/e2e/platform_scale/benchmark_runner.py --sizes 1000 --reps 1 --skip-curve --all-exports --output-dir output/qa48-small
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 6.0
- **ESFUERZO_IMPLEMENTACION:** 1–3 días
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python output/e2e/platform_scale/benchmark_runner.py --sizes 1000 --reps 1 --skip-curve --all-exports --output-dir output/qa48-small
```

## QA-49

- **TEST_ID:** QA-49
- **NOMBRE:** Los verificadores detectan corrupción
- **COMPONENTE:** QA/oracles
- **RIESGO:** Checker pasa todo o importa lógica defectuosa del motor
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-01 INV-04 INV-23
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Corrida válida y copias con confirmada inventada, ID duplicado, suma alterada, estado falso en XLSX y fila faltante.
- **PASOS_EXACTOS:** 1. Exigir resultado limpio para la base válida. 2. Alterar una causa por copia. 3. Exigir error identificable y salida 1. 4. Probar entrada malformada con salida 2.
- **RESULTADO_ESPERADO:** Cada alteración objetivo se detecta. qa/reference.py y qa/invariants.py no importan lógica productiva. El CLI conserva sus validaciones con Python optimizado.
- **ORACULO:** OR-01 OR-03 OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Descartar captura incompleta antes de atribuir el fallo al producto.
- **FALSOS_NEGATIVOS:** Aceptar una corrida correcta no demuestra que el verificador detecte una incorrecta.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **PASOS_EXACTOS:** 1. Validar ancla única. 2. Ejecutar tests base en copia temporal. 3. Aplicar un mutante. 4. Ejecutar sus selectores. 5. Exigir fallo de aserción causal; colección fallida o timeout es inconcluso.
- **RESULTADO_ESPERADO:** Mutaciones de signo, tolerancia, moneda, versión y evidencia deben fallar por aserción causal. Un sobreviviente bloquea la función afectada hasta investigar. Incompetente o inconcluso no cuenta como detectado.
- **ORACULO:** OR-01 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Un cambio de API o ancla puede volver obsoleto al mutante; no demuestra equivalencia semántica.
- **FALSOS_NEGATIVOS:** La señal causal exigida vale para estos diez mutantes; no demuestra que todas las defensas tengan un mutante dirigido.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** mutation
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** cambio de defensa; release; después de incidente
- **RESPUESTA_SI_FALLA:** IR-06 IR-03 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** nuevo
- **SELECTORES:** tests/test_mutation_verdict.py::test_mutant_verdict_requires_selected_causal_assertion
- **RUNNERS:** .venv/bin/python scripts/qa.py mutate --execute
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 2–4 h por mutante nuevo
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python -m pytest -q tests/test_mutation_verdict.py::test_mutant_verdict_requires_selected_causal_assertion
```

```bash
.venv/bin/python scripts/qa.py mutate --execute
```

## QA-51

- **TEST_ID:** QA-51
- **NOMBRE:** Validación ciega con cliente
- **COMPONENTE:** field validation
- **RIESGO:** Confundir coincidencia sintética con seguridad económica real
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-12 INV-13 INV-22
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Período real y control histórico bajo custodio separado; seguir REAL_CLIENT_VALIDATION_PROTOCOL.md.
- **PASOS_EXACTOS:** 1. Congelar representación y corrida antes de ver control histórico. 2. Comparar por cargo y moneda. 3. Resolver falsos PASS/FAIL y diferencias conocidas, nuevas o desconocidas. 4. Registrar horas de trabajo.
- **RESULTADO_ESPERADO:** Contraste externo documentado; diferencia nueva correcta no equivale a dinero recuperado. Conservar primera corrida antes de ajustar tras conocer las respuestas.
- **ORACULO:** OR-01 OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Con distinto alcance o período no se comparan montos directamente.
- **FALSOS_NEGATIVOS:** El control histórico también puede estar equivocado; resolver diferencias con evidencia independiente.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RIESGO:** Habilitar decisiones de pago sólo por cantidad de tests aprobados.
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-01 INV-21 INV-25 INV-26
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Gate U de RELEASE_CRITERIA.md; evidencia real, operativa y de Windows según alcance.
- **PASOS_EXACTOS:** 1. Evaluar cada requisito del Gate U. 2. Registrar pendientes, incidentes y desconocidos. 3. Comprobar restricciones efectivas, restauración, identidad y conciliación del total documental.
- **RESULTADO_ESPERADO:** Gate U cerrado para 0.1.0. Ninguna estadística sintética lo habilita; pytest no sustituye confirmación del contrato.
- **ORACULO:** OR-01 OR-06 OR-10
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Este gate no impide desarrollo local con datos ficticios.
- **FALSOS_NEGATIVOS:** Confundir piloto supervisado con habilitación para decidir pagos sin revisión.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RIESGO:** Una clave JSON duplicada o colisión de ID cambia la interpretación.
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-04 INV-26
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** JSON con clave amount repetida y valores 1 y 100; IDs repetidos por entidad S/C/A/E; datos malformados y campo desconocido.
- **PASOS_EXACTOS:** 1. Leer JSON con parser del producto. 2. Validar duplicados por entidad. 3. Verificar rechazos visibles de importación. 4. Probar lector JSON estricto del verificador.
- **RESULTADO_ESPERADO:** Claves repetidas, números no finitos y campos extra rechazados; ninguna política silenciosa de conservar última fila; duplicados de importación visibles.
- **ORACULO:** OR-04
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Mismo ID en entidades distintas puede ser válido; unicidad por entidad.
- **FALSOS_NEGATIVOS:** Un parser permisivo en QA puede aceptar lo que el producto rechaza.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** ZIP de demo; alterar archivo, manifest, snapshot o decisión; entradas repetidas, fuente faltante y ruta hostil.
- **PASOS_EXACTOS:** 1. Verificar manifest, corrida, cadena de decisiones y fuentes. 2. Comparar hash del ZIP con ancla externa. 3. Alterar un componente por copia. 4. Verificar sin extraer rutas controladas por el archivo.
- **RESULTADO_ESPERADO:** Alteraciones detectadas respecto del ancla; un manifest consistente consigo mismo no prueba autenticidad. Declarar metadata no cubierta por hashes.
- **ORACULO:** OR-06 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Reexportar legítimamente un ZIP puede cambiar timestamps y hash del contenedor.
- **FALSOS_NEGATIVOS:** Un atacante puede recalcular todos los hashes; sin ancla independiente no hay autenticación.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **FIXTURE_DATOS:** Commit limpio, checkout aislado, lock de dependencias, originales con CRLF y SHA, wheel y sdist.
- **PASOS_EXACTOS:** 1. Comparar árbol versionado y archivos materiales. 2. Instalar y probar en checkout limpio. 3. Registrar hashes del paquete y dependencias. 4. Verificar equivalencia de parsing con LF sin exigir SHA del original CRLF.
- **RESULTADO_ESPERADO:** Código entregado igual al verificado; cada original conserva hash de sus bytes; secretos, bases y salidas fuera de Git. No presumir builds idénticos sin comprobar reproducibilidad.
- **ORACULO:** OR-06 OR-08
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Normalizar saltos de línea cambia bytes y procedencia; sólo preserva economía si parsing es equivalente.
- **FALSOS_NEGATIVOS:** Las instalaciones aisladas en Linux no prueban Excel de escritorio, distribución firmada ni hashes de terceros en el lock.
- **AUTOMATIZABLE:** sí
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** alto
- **PRIORIDAD:** P1
- **GRUPO:** B
- **CUANDO:** release; cambio de dependencias
- **RESPUESTA_SI_FALLA:** IR-09 IR-07 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** Pendiente: sin selector automatizado
- **RUNNERS:** .venv/bin/python scripts/verify_delivery.py --output output/delivery-verification.json
- **IMPACTO:** 4
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 48
- **VALOR_POR_COSTO:** 12.0
- **ESFUERZO_IMPLEMENTACION:** 4–8 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** no

```bash
.venv/bin/python scripts/verify_delivery.py --output output/delivery-verification.json
```

## QA-56

- **TEST_ID:** QA-56
- **NOMBRE:** Separación de liquidaciones y alcance de obligación
- **COMPONENTE:** grouping/domain
- **RIESGO:** Sumar cargos de servicios/períodos distintos por clave incompleta
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-05 INV-09 INV-13
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Referencia R; cargos de 100 en liquidaciones L1 y L2; tarifa 100; cliente confirma dos servicios independientes.
- **PASOS_EXACTOS:** 1. Revisar group_key y contrato. 2. Auditar sin período en clave. 3. Representar período y servicio explícitos con operaciones correctas. 4. Comparar grafo de obligaciones manual.
- **RESULTADO_ESPERADO:** L1 y L2 conservan hallazgos separados. Si reutilizan la misma operación/concepto: REVIEW y confirmada0; otra liquidación no prueba otro servicio. Operaciones distintas correctamente vinculadas pueden ser PASS. La asignación entre facturas requiere representación contractual explícita.
- **ORACULO:** OR-01 OR-05
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Dos líneas de facturas pueden completar un servicio; no asumir independencia automáticamente.
- **FALSOS_NEGATIVOS:** Fixtures de un único período no ejercitan este error causal.
- **AUTOMATIZABLE:** parcialmente
- **TIPO_IDEAL:** integration
- **COSTO_EJECUCION:** medio
- **VALOR_ESPERADO:** crítico
- **PRIORIDAD:** P0
- **GRUPO:** A
- **CUANDO:** nuevo formato; cambio de matching; antes de cliente real
- **RESPUESTA_SI_FALLA:** IR-04 IR-15 + IR-COMMON (INCIDENT_RESPONSE.md)
- **ESTADO_COBERTURA:** parcial
- **SELECTORES:** tests/test_review_regressions.py::test_rebilling_same_operation_in_other_invoice_is_not_independent_pass; tests/test_review_regressions.py::test_separate_operations_on_separate_invoices_still_pass
- **RUNNERS:** Pendiente: sin selector automatizado
- **IMPACTO:** 5
- **PROBABILIDAD:** 3
- **DIFICULTAD_DETECCION:** 4
- **RIESGO_SCORE:** 60
- **VALOR_POR_COSTO:** 15.0
- **ESFUERZO_IMPLEMENTACION:** 4–8 h
- **DATOS_REALES:** no
- **WINDOWS:** no
- **INTERVENCION_HUMANA:** sí

```bash
.venv/bin/python -m pytest -q tests/test_review_regressions.py::test_rebilling_same_operation_in_other_invoice_is_not_independent_pass tests/test_review_regressions.py::test_separate_operations_on_separate_invoices_still_pass
```

## QA-57

- **TEST_ID:** QA-57
- **NOMBRE:** Diagnóstico no muta evidencia
- **COMPONENTE:** QA/forensics
- **RIESGO:** La herramienta de diagnóstico inicializa o migra la base original.
- **SEVERIDAD:** CRITICAL
- **INVARIANTE:** INV-30 INV-28
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Base de sólo lectura; schema futuro o incompleto; fila JSON corrupta; hashes previos.
- **PASOS_EXACTOS:** 1. Ejecutar impact en sólo lectura. 2. Intentar ruta inexistente. 3. Comparar bytes, schema y triggers antes/después. 4. Corrupción debe aparecer como unknown o error global explícito.
- **RESULTADO_ESPERADO:** No invocar Store, crear bases ni instalar triggers. La corrupción nunca produce una selección vacía que aparente ausencia de impacto.
- **ORACULO:** OR-06 OR-09
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Una base activa puede cambiar por otro proceso; preservar copia consistente para comparar hashes.
- **FALSOS_NEGATIVOS:** Comprobar sólo mtime no demuestra ausencia de modificaciones.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
- **RIESGO:** Desviación estética sin impacto en la lectura.
- **SEVERIDAD:** LOW
- **INVARIANTE:** INV-23 (sólo si cambia significado)
- **PRECONDICIONES:** Entorno aislado; originales preservados; expected independiente. Base B y matrices exactas en QA_CASES.md.
- **FIXTURE_DATOS:** Todas las combinaciones de sistemas operativos, fuentes y anchos; sin defectos económicos conocidos.
- **PASOS_EXACTOS:** 1. Diferir igualdad exacta de píxeles. 2. Cubrir texto, contraste y desbordamiento material en QA-39. 3. Reconsiderar ante fallo real de lectura.
- **RESULTADO_ESPERADO:** Diferir matriz estética exhaustiva. Cualquier importe o etiqueta ocultos se clasifican como QA-39/P0.
- **ORACULO:** OR-07
- **FALLA:** Cualquier contradicción al resultado esperado, omisión de salida requerida o excepción sin clasificar. Una prueba no ejecutada queda pendiente.
- **FALSOS_POSITIVOS:** Antialiasing o fuentes distintas producen diferencias visuales sin error operativo.
- **FALSOS_NEGATIVOS:** Diferir pruebas cosméticas no permite ocultar moneda o estado.
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
- **RUNNERS:** Pendiente: sin selector automatizado
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
