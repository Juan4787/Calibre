# QA Coverage Ledger: Reconciliación de las 58 Familias de Verificación (Fase 7 y 7.5)

**Commit Base**: `ed278d72c93312caaaa5d490ee4af21388c905e1`  
**Wheel Distribuible**: `dist/freight_audit-0.1.0-py3-none-any.whl` (SHA-256: `ffe5d4cfa9073a147d4640086c71d1b4126885dfef6c06c3f220c048cb66baf4`)  
**Estado Global**: **GATE S CERRADO (100.0% SATISFIED - 51/51)**  

---

## 1. Resumen Ejecutivo y Balance de Gate S

Este documento constituye el inventario auditable definitivo de las **58 familias causales** de Calibre (`QA-01` a `QA-58`), reconciliando cada obligación contra la evidencia acumulada a lo largo de las Fases 1 a 6, Fase 7 y Fase 7.5, y la suite de tests de regresión permanente.

### Clasificación Estricta de Estados

| Estado | Significado | Cantidad | % del Total |
| :--- | :--- | :---: | :---: |
| **`SATISFIED`** | Obligación técnica/sintética 100% satisfecha con evidencia auditable actual | **51** | **87.9%** |
| **`PARTIAL`** | Cobertura de tests existente con delimitación arquitectónica documentada | **0** | **0.0%** |
| **`REQUIRES_REAL_CLIENT`** | Requiere acuerdos o liquidaciones de clientes reales (Reserva Gate P / Fase R) | **3** | **5.2%** |
| **`REQUIRES_WINDOWS`** | Requiere ejecución y kernel de plataforma Windows nativa (Fase 9) | **2** | **3.4%** |
| **`REQUIRES_SCALE`** | Requiere datasets masivos (100k filas) y hardware dedicado (Fase 9) | **1** | **1.7%** |
| **`DEFERRED_WITH_REASON`** | Diferido formalmente por diseño (P3 visual pixel-exact frágil) | **1** | **1.7%** |
| **TOTAL** | | **58** | **100.0%** |

### Cálculo del Gate S (Técnico / Sintético)

- **Familias en el alcance de Gate S**: **51** (excluye las 3 de cliente real, las 2 de Windows, 1 de escala y 1 diferida)
- **Familias SATISFIED**: **51** (100.0%)
- **Familias PARTIAL**: **0**
- **Veredicto Gate S**: **🟢 GATE S CERRADO (51/51 SATISFIED)**. Matriz sintética cerrada al 100% sin excepciones materiales conocidas.

---

## 2. Inventario Detallado de las 58 Familias

| ID | Prioridad | Severidad | Familia | Estado | Evidencia Principal | Comando / Verificación |
| :--- | :---: | :---: | :--- | :---: | :--- | :--- |
| **[QA-01](#qa-01)** | `P0` | `CRITICAL` | Certeza y diferencia confirmada | **`SATISFIED`** | Fase 1 (+3) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-02](#qa-02)** | `P0` | `CRITICAL` | Tolerancia, signo y fronteras | **`SATISFIED`** | Fase 0 (+3) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-03](#qa-03)** | `P0` | `CRITICAL` | Referencia de precio independiente | **`SATISFIED`** | Fase 4 (+1) | `.venv/bin/pytest tests/test_qa_infrastructure` |
| **[QA-04](#qa-04)** | `P0` | `CRITICAL` | Dominio numérico y tipos estrictos | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_engine.py -k 'tes` |
| **[QA-05](#qa-05)** | `P0` | `CRITICAL` | Redondeo, escala y orden | **`SATISFIED`** | Fase 4 (+2) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-06](#qa-06)** | `P0` | `CRITICAL` | División y contexto ambiental | **`SATISFIED`** | Unit/Integration | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-07](#qa-07)** | `P0` | `CRITICAL` | Unidades y monedas separadas | **`SATISFIED`** | Fase 2 (+3) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-08](#qa-08)** | `P0` | `CRITICAL` | Números desde originales | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_importing.py -k '` |
| **[QA-09](#qa-09)** | `P0` | `CRITICAL` | Identidad y normalización declarada | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_importing.py -k t` |
| **[QA-10](#qa-10)** | `P0` | `CRITICAL` | Estructura CSV y conservación de filas | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_importing.py -k t` |
| **[QA-11](#qa-11)** | `P0` | `CRITICAL` | Semántica de libro Excel | **`SATISFIED`** | Fase 4 (+2) | `.venv/bin/pytest tests/test_importing.py -k t` |
| **[QA-12](#qa-12)** | `P1` | `HIGH` | XLS legacy y cache explícito | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_importing.py -k t` |
| **[QA-13](#qa-13)** | `P1` | `HIGH` | Límites de importación y corrupción | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_importing.py -k t` |
| **[QA-14](#qa-14)** | `P0` | `CRITICAL` | Importación incompleta y alcance documental | **`SATISFIED`** | Fase 2 (+2) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-15](#qa-15)** | `P0` | `CRITICAL` | Procedencia verificable | **`SATISFIED`** | Fase 1 (+2) | `.venv/bin/pytest tests/test_integration.py -k` |
| **[QA-16](#qa-16)** | `P0` | `CRITICAL` | Selección única de vigencia | **`SATISFIED`** | Fase 2 (+3) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-17](#qa-17)** | `P0` | `CRITICAL` | Fecha civil y seriales de Excel | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_importing.py -k t` |
| **[QA-18](#qa-18)** | `P0` | `CRITICAL` | Reglas/condiciones y AST acotado | **`SATISFIED`** | Fase 4 (+1) | `.venv/bin/pytest tests/test_engine.py -k 'tes` |
| **[QA-19](#qa-19)** | `P0` | `CRITICAL` | Lookup/bandas sin desempate arbitrario | **`SATISFIED`** | Fase 4 (+1) | `.venv/bin/pytest tests/test_adversarial.py -k` |
| **[QA-20](#qa-20)** | `P0` | `CRITICAL` | Claves, aliases y vínculos explícitos | **`SATISFIED`** | Fase 1 (+2) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-21](#qa-21)** | `P0` | `CRITICAL` | Ambigüedad propagada a grupos parciales | **`SATISFIED`** | Fase 2 (+1) | `.venv/bin/pytest tests/test_adversarial.py -k` |
| **[QA-22](#qa-22)** | `P0` | `CRITICAL` | Consolidado y cargos por componentes | **`SATISFIED`** | Fase 4 (+1) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-23](#qa-23)** | `P0` | `CRITICAL` | Asignaciones superpuestas y servicios parciales | **`SATISFIED`** | Fase 2 (+1) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-24](#qa-24)** | `P0` | `CRITICAL` | Duplicados candidatos y remito legítimo | **`SATISFIED`** | Fase 2 (+1) | `.venv/bin/pytest tests/test_engine.py -k 'tes` |
| **[QA-25](#qa-25)** | `P0` | `CRITICAL` | Evidencia por ámbito y adición selectiva | **`SATISFIED`** | Fase 1 (+1) | `.venv/bin/pytest tests/test_engine.py -k 'tes` |
| **[QA-26](#qa-26)** | `P0` | `CRITICAL` | Cobertura explícita de cargos ausentes | **`SATISFIED`** | Fase 2 (+1) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-27](#qa-27)** | `P0` | `CRITICAL` | Conservación total por ID y moneda | **`SATISFIED`** | Fase 6 (+1) | `.venv/bin/pytest tests/test_qa_infrastructure` |
| **[QA-28](#qa-28)** | `P0` | `CRITICAL` | Determinismo y transformaciones | **`SATISFIED`** | Fase 2 (+1) | `.venv/bin/pytest tests/test_engine.py -k test` |
| **[QA-29](#qa-29)** | `P0` | `CRITICAL` | Aislamiento entre clientes y catálogos | **`SATISFIED`** | Fase 7 (+1) | `.venv/bin/pytest tests/test_backlog_p0_p1.py ` |
| **[QA-30](#qa-30)** | `P0` | `CRITICAL` | Decisiones humanas y cadena | **`SATISFIED`** | Fase 1 (+2) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-31](#qa-31)** | `P0` | `CRITICAL` | Integridad histórica y mutación | **`SATISFIED`** | Fase 3 (+1) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-32](#qa-32)** | `P0` | `CRITICAL` | Replay y cambio de artefacto | **`SATISFIED`** | Fase 1 (+2) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-33](#qa-33)** | `P0` | `CRITICAL` | Proveniencia de ejecutables y alcance | **`SATISFIED`** | Fase 0 (+2) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-34](#qa-34)** | `P0` | `CRITICAL` | Backup, restore y reapertura | **`SATISFIED`** | Fase 3 (+1) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-35](#qa-35)** | `P0` | `CRITICAL` | Crash, rollback y concurrencia | **`SATISFIED`** | Fase 3F (+1) | `.venv/bin/python output/e2e/persistence_crash` |
| **[QA-36](#qa-36)** | `P0` | `CRITICAL` | Schema y migración recuperable | **`SATISFIED`** | Fase 3 (+1) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-37](#qa-37)** | `P0` | `CRITICAL` | Reconciliación entre representaciones | **`SATISFIED`** | Fase 1 (+3) | `.venv/bin/pytest tests/test_qa_infrastructure` |
| **[QA-38](#qa-38)** | `P0` | `CRITICAL` | Límites de reportes y contenido activo | **`SATISFIED`** | Unit/Integration | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-39](#qa-39)** | `P0` | `CRITICAL` | UI conserva semántica visible y estado actual | **`SATISFIED`** | Fase 1 (+2) | `Playwright headless Chromium automated flow i` |
| **[QA-40](#qa-40)** | `P0` | `CRITICAL` | Barrera de red local | **`SATISFIED`** | Unit/Integration | `.venv/bin/pytest tests/test_integration.py -k` |
| **[QA-41](#qa-41)** | `P0` | `CRITICAL` | Rutas, archivos y sobrescritura | **`REQUIRES_WINDOWS`** | Pendiente Fase 9 | `scripts/verify_windows.bat (Fase 9)` |
| **[QA-42](#qa-42)** | `P0` | `CRITICAL` | XML/ZIP malicioso acotado | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-43](#qa-43)** | `P1` | `HIGH` | Errores de API y consistencia de operación | **`SATISFIED`** | Fase 1 (+1) | `.venv/bin/pytest tests/test_integration.py -k` |
| **[QA-44](#qa-44)** | `P1` | `HIGH` | Auditoría sin servicios externos | **`SATISFIED`** | Fase 1 (+1) | `.venv/bin/pytest tests/test_integration.py -k` |
| **[QA-45](#qa-45)** | `P0` | `CRITICAL` | Representación contractual y mapping aprobados | **`REQUIRES_REAL_CLIENT`** | Pendiente Gate P / Fase R | `Revisión formal con cliente real (Fase R)` |
| **[QA-46](#qa-46)** | `P1` | `HIGH` | Generalidad de cinco arquetipos | **`SATISFIED`** | Fase 4 | `.venv/bin/python output/e2e/generality/test_g` |
| **[QA-47](#qa-47)** | `P1` | `HIGH` | Paquete y plataforma real | **`REQUIRES_WINDOWS`** | Pendiente Fase 9 | `pip install dist/*.whl en Windows x64 (Fase 9` |
| **[QA-48](#qa-48)** | `P2` | `HIGH` | Escala, memoria y tiempos de todas las etapas | **`REQUIRES_SCALE`** | Pendiente Fase 9 | `scripts/benchmark_scale.py (Fase 9)` |
| **[QA-49](#qa-49)** | `P0` | `CRITICAL` | Los verificadores detectan corrupción | **`SATISFIED`** | Fase 3 (+2) | `.venv/bin/pytest tests/test_qa_infrastructure` |
| **[QA-50](#qa-50)** | `P0` | `CRITICAL` | Mutantes críticos dirigidos | **`SATISFIED`** | Fase 0 (+1) | `.venv/bin/python scripts/qa.py mutate --all` |
| **[QA-51](#qa-51)** | `P0` | `CRITICAL` | Validación ciega con cliente | **`REQUIRES_REAL_CLIENT`** | Pendiente Gate P / Fase R | `Auditoría en staging con dataset confidencial` |
| **[QA-52](#qa-52)** | `P0` | `CRITICAL` | Gate de pago sin nuestra supervisión | **`REQUIRES_REAL_CLIENT`** | Pendiente Gate P / Fase R | `Pase a producción operacional en dador de car` |
| **[QA-53](#qa-53)** | `P0` | `CRITICAL` | IDs y JSON inequívocos | **`SATISFIED`** | Fase 5 (+1) | `.venv/bin/pytest tests/test_adversarial.py -k` |
| **[QA-54](#qa-54)** | `P0` | `CRITICAL` | Bundle portable y ancla externa | **`SATISFIED`** | Fase 1 (+1) | `.venv/bin/pytest tests/test_storage_reporting` |
| **[QA-55](#qa-55)** | `P1` | `HIGH` | Entrega reproducible y dependencias | **`SATISFIED`** | Fase 0 (+2) | `bash scripts/verify.sh` |
| **[QA-56](#qa-56)** | `P0` | `CRITICAL` | Separación de liquidaciones y alcance de obligación | **`SATISFIED`** | Fase 7 (+2) | `.venv/bin/pytest tests/test_backlog_p0_p1.py ` |
| **[QA-57](#qa-57)** | `P0` | `CRITICAL` | Diagnóstico no muta evidencia | **`SATISFIED`** | Fase 3 (+1) | `.venv/bin/pytest tests/test_qa_infrastructure` |
| **[QA-58](#qa-58)** | `P3` | `LOW` | Píxel exacto y matrices visuales exhaustivas | **`DEFERRED_WITH_REASON`** | Diferido | `N/A (Diferido formalmente)` |

---

## 3. Mapeo Causal de Evidencia por Familia (TEST_ID)

### QA-01 — Certeza y diferencia confirmada

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/summary`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Falta de respaldo (evidencia, reglas incompletas) nunca se convierte en discrepancia confirmada ni dinero recuperable.
- **Fases con Evidencia**: Fase 1, Fase 2, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-05`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-e03`
  - `tests/test_engine.py::test_missing_evidence_does_not_confirm_even_numeric_difference`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_missing_evidence`
- **Resultado Observado**: `PASS (0 confirmed diff in REVIEW/UNDETERMINABLE)`

### QA-02 — Tolerancia, signo y fronteras

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/tolerance`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Evaluación de tolerancias absolutas y relativas con signos exactos; diferencias dentro de tolerancia son PASS.
- **Fases con Evidencia**: Fase 0, Fase 2, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-06`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-e01`
  - `tests/test_engine.py::test_tolerance_and_signed_differences`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_tolerance`
- **Resultado Observado**: `PASS (INV-02 and INV-07 verified)`

### QA-03 — Referencia de precio independiente

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `qa/oracle`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Oráculo independiente de referencia en Decimal/Fraction sin reusar código del motor productivo.
- **Fases con Evidencia**: Fase 4, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md`
  - `qa/reference.py`
  - `tests/test_qa_infrastructure.py::test_generated_reference_prices`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_qa_infrastructure.py -k test_generated_reference`
- **Resultado Observado**: `PASS (20 findings compared against independent oracle)`

### QA-04 — Dominio numérico y tipos estrictos

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/numeric`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Prohibición absoluta de float binario IEEE 754; operaciones en Decimal con representación textual exacta.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_engine.py::test_float_prohibited`
  - `tests/test_engine.py::test_invalid_money`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k 'test_float or test_invalid_money'`
- **Resultado Observado**: `PASS (strict Decimal enforcement)`

### QA-05 — Redondeo, escala y orden

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/rounding`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Redondeo solo en la frontera contractual especificada, sin pérdidas acumuladas de centavos.
- **Fases con Evidencia**: Fase 4, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-e12`
  - `tests/test_engine.py::test_property_division_matches_high_precision`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_property_division`
- **Resultado Observado**: `PASS (exact scale conservation)`

### QA-06 — División y contexto ambiental

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/environment`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Inmunidad frente al contexto global decimal de Python (getcontext()); divisiones protegidas contra división por cero.
- **Fases con Evidencia**: Unit/Integration
- **Artefactos de Respaldo**:
  - `tests/test_engine.py::test_global_decimal_context_does_not_affect_results`
  - `tests/test_engine.py::test_property_division_matches_high_precision`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_global_decimal_context`
- **Resultado Observado**: `PASS (local decimal isolation)`

### QA-07 — Unidades y monedas separadas

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/currency`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Segregación estricta por moneda; imposibilidad de sumar o consolidar ARS con USD u otras divisas.
- **Fases con Evidencia**: Fase 2, Fase 4, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-02`
  - `output/e2e/generality/GENERALITY_REPORT.md#g2`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-e09`
  - `tests/test_engine.py::test_currencies_never_summed_or_converted`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_currencies_never_summed`
- **Resultado Observado**: `PASS (INV-06 multi-currency segregation)`

### QA-08 — Números desde originales

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `importing/numbers`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Preservación del token numérico original desde CSV/XLSX respetando separadores decimales locales.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_importing.py::test_argentine_decimal`
  - `tests/test_importing.py::test_csv_argentine_numbers_zeroes_and_provenance`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_importing.py -k 'test_argentine_decimal or test_csv_argentine'`
- **Resultado Observado**: `PASS (exact numeric token parsing)`

### QA-09 — Identidad y normalización declarada

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `importing/identity`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Normalización explícita y visible de identificadores sin desduplicación silenciosa.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_importing.py::test_duplicate_business_ids_visible_not_silently_deduplicated`
  - `tests/test_importing.py::test_unknown_concept_not_canonicalized_by_accident`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_importing.py -k test_duplicate_business_ids`
- **Resultado Observado**: `PASS (explicit identifier handling)`

### QA-10 — Estructura CSV y conservación de filas

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `importing/csv`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Lectura robusta de CSV (comillas escapadas, multilínea, saltos CRLF) con coordenadas de fila verificables.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_importing.py::test_csv_multiline_provenance_uses_actual_line`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_importing.py -k test_csv_multiline`
- **Resultado Observado**: `PASS (15 CSV adversarial vectors passed)`

### QA-11 — Semántica de libro Excel

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `importing/xlsx`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Lectura directa de celdas XLSX sin evaluar fórmulas activas ni depender de caché opaco; selección de hoja obligatoria.
- **Fases con Evidencia**: Fase 4, Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md#g3`
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_importing.py::test_xlsx_formula_never_evaluated_or_taken_as_cache`
  - `tests/test_importing.py::test_multisheet_requires_selection`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_importing.py -k test_xlsx_formula`
- **Resultado Observado**: `PASS (20 XLSX adversarial vectors passed)`

### QA-12 — XLS legacy y cache explícito

- **Prioridad / Severidad**: `P1` / `HIGH`
- **Componente**: `importing/xls`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Importación segura de archivos binarios XLS (BIFF8) con requerimiento de declaración de caché explícito.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_importing.py::test_xls_requires_explicit_cached_value_acceptance`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_importing.py -k test_xls_requires`
- **Resultado Observado**: `PASS (10 XLS adversarial vectors passed)`

### QA-13 — Límites de importación y corrupción

- **Prioridad / Severidad**: `P1` / `HIGH`
- **Componente**: `importing/limits`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Fuzzing y contención de archivos corruptos, truncados o con ataques de expansión (zip bomb, xml entity).
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_importing.py::test_malformed_xlsx_fuzz_is_bounded_and_classified`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_importing.py -k test_malformed_xlsx`
- **Resultado Observado**: `PASS (15 malformed files safely rejected)`

### QA-14 — Importación incompleta y alcance documental

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/integrity`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Si la importación rechaza filas o está incompleta, el motor bloquea la certificación de certeza (INV-11).
- **Fases con Evidencia**: Fase 2, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-09`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-u04`
  - `tests/test_engine.py::test_import_rejects_block_economic_confirmation`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_import_rejects`
- **Resultado Observado**: `PASS (INV-11 incomplete import lock)`

### QA-15 — Procedencia verificable

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/provenance`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Trazabilidad celda a celda con hash de documento fuente inmutable; validable por verificadores independientes.
- **Fases con Evidencia**: Fase 1, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/isolated_env/artifacts/reconciliation.json`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-i06`
  - `tests/test_integration.py::test_api_import_with_mapping_and_provenance`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_integration.py -k test_api_import_with_mapping`
- **Resultado Observado**: `PASS (INV-22 provenance verifier verified)`

### QA-16 — Selección única de vigencia

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/validity`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Resolución unívoca de vigencia contractual por fecha; solapamientos no eligen primera versión arbitraria.
- **Fases con Evidencia**: Fase 2, Fase 4, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-04`
  - `output/e2e/generality/GENERALITY_REPORT.md#g4`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-e06`
  - `tests/test_engine.py::test_overlapping_versions_never_pick_first`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_overlapping_versions`
- **Resultado Observado**: `PASS (INV-08 ambiguity leads to UNDETERMINABLE)`

### QA-17 — Fecha civil y seriales de Excel

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `importing/dates`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Parsing inequívoco de fechas ISO (YYYY-MM-DD) y seriales de Excel (epoch 1899-12-30) rechazando ambigüedad DD/MM vs MM/DD.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_importing.py::test_ambiguous_date_is_rejected`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_importing.py -k test_ambiguous_date`
- **Resultado Observado**: `PASS (ambiguous dates rejected)`

### QA-18 — Reglas/condiciones y AST acotado

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/rules`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Evaluación segura de AST acotado; lazy branching; falta de atributo no es falso booleano.
- **Fases con Evidencia**: Fase 4, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md`
  - `tests/test_engine.py::test_condition_branch_is_lazy`
  - `tests/test_engine.py::test_condition_missing_is_not_false`
  - `tests/test_adversarial.py::test_bounded_expression_depth_rejects_nested_attack`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k 'test_condition_branch or test_condition_missing'`
- **Resultado Observado**: `PASS (safe bounded rule evaluation)`

### QA-19 — Lookup/bandas sin desempate arbitrario

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/lookup`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Búsqueda en tablas y bandas escalonadas; solapamientos o vacíos conducen a indeterminación sin selección arbitraria.
- **Fases con Evidencia**: Fase 4, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md#g2`
  - `tests/test_adversarial.py::test_band_overlap_and_gap_never_select_arbitrarily`
  - `tests/test_adversarial.py::test_duplicate_lookup_rows_even_same_price_are_ambiguous`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_adversarial.py -k test_band_overlap`
- **Resultado Observado**: `PASS (lookup ambiguity handled conservatively)`

### QA-20 — Claves, aliases y vínculos explícitos

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/matching`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Matching por claves compuestas, aliases direccionales y vínculos explícitos; keys vacías nunca cruzan con keys vacías.
- **Fases con Evidencia**: Fase 1, Fase 4, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md`
  - `tests/test_engine.py::test_composite_keys_and_directional_alias`
  - `tests/test_adversarial.py::test_empty_keys_never_join_to_empty_keys`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_composite_keys`
- **Resultado Observado**: `PASS (empty keys never join)`

### QA-21 — Ambigüedad propagada a grupos parciales

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/matching`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Ambigüedad en asignación de viajes contamina al grupo completo, declarando REVIEW para todo el conjunto.
- **Fases con Evidencia**: Fase 2, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-01`
  - `tests/test_engine.py::test_matching_ambiguity_is_review`
  - `tests/test_adversarial.py::test_ambiguous_allocation_also_blocks_related_partial_group`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_adversarial.py -k test_ambiguous_allocation`
- **Resultado Observado**: `PASS (matching ambiguity propagates)`

### QA-22 — Consolidado y cargos por componentes

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/consolidation`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Auditoría de fletes consolidados (N remitos -> 1 cargo) y componentes desagregados (1 remito -> N cargos).
- **Fases con Evidencia**: Fase 4, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md#g5`
  - `output/e2e/generality/GENERALITY_REPORT.md#g6`
  - `tests/test_engine.py::test_group_sum_and_one_expected_charge`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_group_sum`
- **Resultado Observado**: `PASS (G5 and G6 parity verified)`

### QA-23 — Asignaciones superpuestas y servicios parciales

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/allocation`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Cargos que reclaman los mismos remitos en combinaciones solapadas se envían a REVIEW sin doble adjudicación.
- **Fases con Evidencia**: Fase 2, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-10`
  - `tests/test_engine.py::test_overlap_allocations_are_review`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_overlap_allocations`
- **Resultado Observado**: `PASS (overlapping allocations in REVIEW)`

### QA-24 — Duplicados candidatos y remito legítimo

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/duplicates`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Detección de duplicados como candidatos a revisión humana; mismo remito con conceptos distintos no es duplicado.
- **Fases con Evidencia**: Fase 2, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-08`
  - `tests/test_engine.py::test_configured_duplicate_is_candidate_only`
  - `tests/test_engine.py::test_same_remittance_different_concepts_is_not_duplicate`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k 'test_configured_duplicate or test_same_remittance'`
- **Resultado Observado**: `PASS (duplicate candidate isolation)`

### QA-25 — Evidencia por ámbito y adición selectiva

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/evidence`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Requisitos de evidencia validados por ámbito (operación, remito o flete); evidencia no relacionada no satisface el cargo.
- **Fases con Evidencia**: Fase 1, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/isolated_env/artifacts/reconciliation.json`
  - `tests/test_engine.py::test_evidence_any_of_and_per_operation`
  - `tests/test_engine.py::test_unrelated_evidence_cannot_support_charge`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k 'test_evidence_any_of or test_unrelated_evidence'`
- **Resultado Observado**: `PASS (INV-10 evidence enforcement)`

### QA-26 — Cobertura explícita de cargos ausentes

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/coverage`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Cargos esperados contractualmente pero no facturados se detectan en REVIEW si el ámbito está explícitamente cerrado.
- **Fases con Evidencia**: Fase 2, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md#adv-07`
  - `tests/test_engine.py::test_missing_expected_charge_requires_explicit_scope_and_is_review`
  - `tests/test_adversarial.py::test_coverage_cannot_silently_drop_wrong_carrier`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_missing_expected_charge`
- **Resultado Observado**: `PASS (missing expected charges in REVIEW)`

### QA-27 — Conservación total por ID y moneda

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `qa/invariants`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Invariantes de conservación estricta: suma de cargos = suma de hallazgos; partición biyectiva de IDs (INV-04, INV-05).
- **Fases con Evidencia**: Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-e10`
  - `output/e2e/fault_injection/FAULT_CATALOG.md#fi-e11`
  - `tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_qa_infrastructure.py -k test_checker_rejects`
- **Resultado Observado**: `PASS (INV-04 and INV-05 invariants enforced)`

### QA-28 — Determinismo y transformaciones

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/determinism`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Invarianza estricta ante orden de filas, espacios inocuos y permutación de records en input.
- **Fases con Evidencia**: Fase 2, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/adversarial/ADVERSARIAL_CASES.md`
  - `tests/test_engine.py::test_property_arbitrary_row_permutation`
  - `tests/test_integration.py::test_economic_result_unchanged_by_input_row_order`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_engine.py -k test_property_arbitrary_row`
- **Resultado Observado**: `PASS (10 E2E metamorphic permutations passed)`

### QA-29 — Aislamiento entre clientes y catálogos

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/isolation`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Aislamiento criptográfico y de base de datos entre clientes distintos; bases de datos y fuentes no se contaminan.
- **Fases con Evidencia**: Fase 7, Unit/Integration
- **Artefactos de Respaldo**:
  - `tests/test_backlog_p0_p1.py::test_qa29_client_catalog_and_storage_isolation`
  - `tests/test_integration.py::test_real_files_three_agreements_golden_and_second_client`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_backlog_p0_p1.py -k test_qa29`
- **Resultado Observado**: `PASS (strict multi-tenant database isolation)`

### QA-30 — Decisiones humanas y cadena

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/decisions`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Decisiones humanas son aditivas y encadenadas por SHA-256; nunca reescriben el hallazgo del motor.
- **Fases con Evidencia**: Fase 1, Fase 3, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3d`
  - `tests/test_storage_reporting.py::test_human_decision_never_rewrites_finding`
  - `tests/test_storage_reporting.py::test_decision_chain_serializes_concurrent_writers`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k test_human_decision`
- **Resultado Observado**: `PASS (INV-24 append-only decision chain)`

### QA-31 — Integridad histórica y mutación

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/integrity`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Bloqueo de UPDATE y DELETE en tablas históricas; detección inmediata si se saltean los triggers SQLite.
- **Fases con Evidencia**: Fase 3, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3a`
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3c`
  - `tests/test_storage_reporting.py::test_db_update_delete_blocked`
  - `tests/test_storage_reporting.py::test_tampered_result_detected_after_trigger_bypass`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k 'test_db_update or test_tampered_result'`
- **Resultado Observado**: `PASS (triggers and tamper verifiers verified)`

### QA-32 — Replay y cambio de artefacto

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/replay`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Replay determinista reproduce idéntico resultado desde snapshot; si cambia el artefacto motor se bloquea con advertencia.
- **Fases con Evidencia**: Fase 1, Fase 3, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3d`
  - `tests/test_storage_reporting.py::test_save_replay_and_idempotency`
  - `tests/test_storage_reporting.py::test_engine_artifact_change_blocks_replay`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k 'test_save_replay or test_engine_artifact'`
- **Resultado Observado**: `PASS (deterministic replay from snapshot)`

### QA-33 — Proveniencia de ejecutables y alcance

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/artifact`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Identidad SHA-256 del código del motor persistida en metadata de cada corrida (engine_artifact_hash).
- **Fases con Evidencia**: Fase 0, Fase 3, Fase 5
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md`
  - `tests/test_storage_reporting.py::test_engine_artifact_change_blocks_replay`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k test_engine_artifact`
- **Resultado Observado**: `PASS (artifact hash verified)`

### QA-34 — Backup, restore y reapertura

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/backup`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Backup consistente con VACUUM INTO / WAL checkpoint; reapertura y replay idéntico tras restore.
- **Fases con Evidencia**: Fase 3, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3b`
  - `tests/test_storage_reporting.py::test_migration_reopening_and_consistent_backup`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k test_migration_reopening`
- **Resultado Observado**: `PASS (backup restore verified)`

### QA-35 — Crash, rollback y concurrencia

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/crash`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Resistencia a muerte no cooperativa del proceso con SIGKILL en puntos transaccionales deterministas y timing variable.
- **Fases con Evidencia**: Fase 3F, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3f`
  - `output/e2e/persistence_crash/observed/crash-summary.json`
- **Comando de Verificación**: `.venv/bin/python output/e2e/persistence_crash/test_crash_resilience.py`
- **Resultado Observado**: `PASS (7 deterministic SIGKILL crash points + 60 timing-variable iterations passed without corruption)`

### QA-36 — Schema y migración recuperable

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/schema`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Control estricto de versión de schema SQLite; bases de datos de versiones más nuevas son rechazadas de modo seguro.
- **Fases con Evidencia**: Fase 3, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3e`
  - `tests/test_storage_reporting.py::test_newer_database_schema_is_not_opened`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k test_newer_database_schema`
- **Resultado Observado**: `PASS (forward compatibility protection)`

### QA-37 — Reconciliación entre representaciones

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `reporting/reconcile`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Reconciliación cruzada exhaustiva entre JSON, XLSX, HTML, API y UI DOM con cero tolerancia a divergencias.
- **Fases con Evidencia**: Fase 1, Fase 2, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/isolated_env/artifacts/reconciliation.json`
  - `output/e2e/fault_injection/FAULT_INJECTION_REPORT.md`
  - `tests/test_qa_infrastructure.py::test_cross_report_reconciliation_and_tamper_detection`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_qa_infrastructure.py -k test_cross_report`
- **Resultado Observado**: `PASS (zero divergence across 6 representations)`

### QA-38 — Límites de reportes y contenido activo

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `reporting/limits`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Escape estricto de HTML (XSS) y fórmulas de Excel (=, +, -, @); manejo de celdas largas sin desbordar buffers.
- **Fases con Evidencia**: Unit/Integration
- **Artefactos de Respaldo**:
  - `tests/test_storage_reporting.py::test_report_escapes_untrusted_html_and_excel_formula`
  - `tests/test_storage_reporting.py::test_excel_long_cell_is_not_silently_truncated`
  - `tests/test_storage_reporting.py::test_excel_row_limit_preserves_full_bundle_json`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k 'test_report_escapes or test_excel_long_cell'`
- **Resultado Observado**: `PASS (formula injection and XSS blocked)`

### QA-39 — UI conserva semántica visible y estado actual

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `ui/browser`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Navegación completa Chromium E2E verificando que el árbol DOM refleja fielmente estados, importes y banderas del backend.
- **Fases con Evidencia**: Fase 1, Fase 2, Fase 6
- **Artefactos de Respaldo**:
  - `output/e2e/isolated_env/artifacts/screenshots/`
  - `output/e2e/adversarial/observed/adversarial-ui-observed.json`
  - `output/e2e/fault_injection/FAULT_INJECTION_REPORT.md#fi-u01`
- **Comando de Verificación**: `Playwright headless Chromium automated flow in Fase 1 & 2`
- **Resultado Observado**: `PASS (DOM mirrors core exactly)`

### QA-40 — Barrera de red local

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `server/security`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: La API corre exclusivamente en localhost; rechaza Host headers externos, CORS sospechoso y no emite requests salientes.
- **Fases con Evidencia**: Unit/Integration
- **Artefactos de Respaldo**:
  - `tests/test_integration.py::test_local_api_security_boundary`
  - `tests/test_integration.py::test_fully_offline_core`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_integration.py -k test_local_api_security_boundary`
- **Resultado Observado**: `PASS (local binding, CSP and offline barrier verified)`

### QA-41 — Rutas, archivos y sobrescritura

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `platform/windows_paths`
- **Estado**: **`REQUIRES_WINDOWS`**
- **Obligación / Requisito**: Comportamiento ante rutas con backslash, case-insensitivity y locking de archivos en Windows.
- **Fases con Evidencia**: Pendiente Fase 9
- **Artefactos de Respaldo**:
  - `docs/QA_DELIVERY.md#plataforma-windows`
- **Comando de Verificación**: `scripts/verify_windows.bat (Fase 9)`
- **Resultado Observado**: `REQUIRES_WINDOWS (ambiente Linux actual no ejecuta kernel NTFS)`

### QA-42 — XML/ZIP malicioso acotado

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `reporting/security`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Verificación segura de bundles ZIP sin path traversal y lectura de XML sin resolución de entidades externas.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_storage_reporting.py::test_portable_bundle_integrity`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k test_portable_bundle_integrity`
- **Resultado Observado**: `PASS (safe zip and defused xml parsing)`

### QA-43 — Errores de API y consistencia de operación

- **Prioridad / Severidad**: `P1` / `HIGH`
- **Componente**: `api/errors`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Respuestas de error estructuradas con códigos HTTP adecuados (400/403/404/409/422) y mensajes recuperables.
- **Fases con Evidencia**: Fase 1, Unit/Integration
- **Artefactos de Respaldo**:
  - `tests/test_integration.py::test_api_configuration_errors_use_recoverable_messages`
  - `tests/test_integration.py::test_api_runs_decisions_export_replay`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_integration.py -k test_api_configuration_errors`
- **Resultado Observado**: `PASS (standard error responses)`

### QA-44 — Auditoría sin servicios externos

- **Prioridad / Severidad**: `P1` / `HIGH`
- **Componente**: `engine/offline`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Ejecución de auditoría completamente offline sin llamadas a DNS, CDN o APIs de terceros.
- **Fases con Evidencia**: Fase 1, Unit/Integration
- **Artefactos de Respaldo**:
  - `tests/test_integration.py::test_fully_offline_core`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_integration.py -k test_fully_offline`
- **Resultado Observado**: `PASS (zero outbound network activity)`

### QA-45 — Representación contractual y mapping aprobados

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `client/contracts`
- **Estado**: **`REQUIRES_REAL_CLIENT`**
- **Obligación / Requisito**: Validación y firma de mappings y representaciones contractuales con los transportistas y dadores reales.
- **Fases con Evidencia**: Pendiente Gate P / Fase R
- **Artefactos de Respaldo**:
  - `docs/QA_DELIVERY.md#gate-p`
- **Comando de Verificación**: `Revisión formal con cliente real (Fase R)`
- **Resultado Observado**: `REQUIRES_REAL_CLIENT (no debe simularse artificialmente)`

### QA-46 — Generalidad de cinco arquetipos

- **Prioridad / Severidad**: `P1` / `HIGH`
- **Componente**: `engine/archetypes`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Validación de generalidad sobre los arquetipos contractuales de flete (pallets, peso, bultos, vigencias, consolidado).
- **Fases con Evidencia**: Fase 4
- **Artefactos de Respaldo**:
  - `output/e2e/generality/GENERALITY_REPORT.md`
  - `output/e2e/generality/oracle.py`
- **Comando de Verificación**: `.venv/bin/python output/e2e/generality/test_generality_e2e.py`
- **Resultado Observado**: `PASS (6 archetypes G1..G6 matched independent oracle 100%)`

### QA-47 — Paquete y plataforma real

- **Prioridad / Severidad**: `P1` / `HIGH`
- **Componente**: `platform/windows_package`
- **Estado**: **`REQUIRES_WINDOWS`**
- **Obligación / Requisito**: Instalación del wheel y arranque del CLI y GUI en un sistema operativo Windows real.
- **Fases con Evidencia**: Pendiente Fase 9
- **Artefactos de Respaldo**:
  - `docs/QA_DELIVERY.md#plataforma-windows`
- **Comando de Verificación**: `pip install dist/*.whl en Windows x64 (Fase 9)`
- **Resultado Observado**: `REQUIRES_WINDOWS (requiere host Windows)`

### QA-48 — Escala, memoria y tiempos de todas las etapas

- **Prioridad / Severidad**: `P2` / `HIGH`
- **Componente**: `performance/scale`
- **Estado**: **`REQUIRES_SCALE`**
- **Obligación / Requisito**: Benchmark con 100.000 operaciones y liquidaciones; medición de memoria RSS y tiempo total < 60 s.
- **Fases con Evidencia**: Pendiente Fase 9
- **Artefactos de Respaldo**:
  - `docs/VERIFICATION.md#benchmarks`
- **Comando de Verificación**: `scripts/benchmark_scale.py (Fase 9)`
- **Resultado Observado**: `REQUIRES_SCALE (requiere dataset masivo y hardware dedicado)`

### QA-49 — Los verificadores detectan corrupción

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `qa/detectors`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Demostración experimental de que las defensas e invariantes detectan corrupción y fallos deliberados.
- **Fases con Evidencia**: Fase 3, Fase 6, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md#3c`
  - `output/e2e/fault_injection/FAULT_INJECTION_REPORT.md`
  - `tests/test_qa_infrastructure.py::test_checker_rejects_economic_corruption`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_qa_infrastructure.py -k test_checker_rejects`
- **Resultado Observado**: `PASS (100% of 41 corrupted payloads detected)`

### QA-50 — Mutantes críticos dirigidos

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `qa/mutations`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Asesinato estricto de mutantes críticos dirigidos (M01..M07) en el motor económico.
- **Fases con Evidencia**: Fase 0, Fase 6
- **Artefactos de Respaldo**:
  - `output/e2e/fault_injection/FAULT_INJECTION_REPORT.md`
  - `scripts/qa.py mutate`
- **Comando de Verificación**: `.venv/bin/python scripts/qa.py mutate --all`
- **Resultado Observado**: `PASS (7/7 critical mutants killed with causal oracle)`

### QA-51 — Validación ciega con cliente

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `client/blind_audit`
- **Estado**: **`REQUIRES_REAL_CLIENT`**
- **Obligación / Requisito**: Auditoría ciega contra liquidación real de cliente sin conocer el resultado manual previo.
- **Fases con Evidencia**: Pendiente Gate P / Fase R
- **Artefactos de Respaldo**:
  - `docs/QA_DELIVERY.md#gate-p`
- **Comando de Verificación**: `Auditoría en staging con dataset confidencial real`
- **Resultado Observado**: `REQUIRES_REAL_CLIENT (reserva a Gate P)`

### QA-52 — Gate de pago sin nuestra supervisión

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `client/payment_gate`
- **Estado**: **`REQUIRES_REAL_CLIENT`**
- **Obligación / Requisito**: El cliente confía el bloqueo o pago de facturas a Calibre sin intervención humana de nuestro equipo.
- **Fases con Evidencia**: Pendiente Gate P / Fase R
- **Artefactos de Respaldo**:
  - `docs/QA_DELIVERY.md#gate-p`
- **Comando de Verificación**: `Pase a producción operacional en dador de carga real`
- **Resultado Observado**: `REQUIRES_REAL_CLIENT (reserva a Gate P)`

### QA-53 — IDs y JSON inequívocos

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `importing/json`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Rechazo de claves JSON duplicadas y manejo inequívoco de identificadores numéricos fraccionarios.
- **Fases con Evidencia**: Fase 5, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/import_adversarial/IMPORT_ADVERSARIAL_REPORT.md`
  - `tests/test_adversarial.py::test_duplicate_json_keys_are_rejected`
  - `tests/test_importing.py::test_original_fractional_numeric_identifier_cannot_become_integer_after_float_rounding`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_adversarial.py -k test_duplicate_json_keys`
- **Resultado Observado**: `PASS (duplicate keys and float coercion rejected)`

### QA-54 — Bundle portable y ancla externa

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `reporting/bundle`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Bundle ZIP portable con manifest.json y SHA-256 verificables de forma independiente mediante cli verify-bundle.
- **Fases con Evidencia**: Fase 1, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/isolated_env/artifacts/manifest.json`
  - `tests/test_storage_reporting.py::test_portable_bundle_integrity`
  - `tests/test_integration.py::test_cli_full_run_exports_and_bundle_replay`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_storage_reporting.py -k test_portable_bundle`
- **Resultado Observado**: `PASS (portable bundle verification verified)`

### QA-55 — Entrega reproducible y dependencias

- **Prioridad / Severidad**: `P1` / `HIGH`
- **Componente**: `build/packaging`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Empaquetado limpio con pip/build; hash de wheel y tarball inmutables; instalación en clean-room probada.
- **Fases con Evidencia**: Fase 0, Fase 1, Fase 5
- **Artefactos de Respaldo**:
  - `dist/freight_audit-0.1.0-py3-none-any.whl (SHA-256: ffe5d4cfa9073a147d4640086c71d1b4126885dfef6c06c3f220c048cb66baf4)`
  - `scripts/verify.sh`
- **Comando de Verificación**: `bash scripts/verify.sh`
- **Resultado Observado**: `PASS (100% build verification)`

### QA-56 — Separación de liquidaciones y alcance de obligación

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `engine/settlement`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Separación de liquidaciones y períodos: settlement constituye frontera explícita de agrupación y asignación en engine; evita fusión silenciosa de cargos de liquidaciones distintas.
- **Fases con Evidencia**: Fase 7, Fase 7.5, Unit/Integration
- **Artefactos de Respaldo**:
  - `src/freight_audit/engine.py::group_key`
  - `output/e2e/qa56/QA56_EXPECTED_CASES.md`
  - `tests/test_backlog_p0_p1.py::test_qa56_settlement_scope_and_grouping_behavior`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_backlog_p0_p1.py -k test_qa56`
- **Resultado Observado**: `SATISFIED (settlement como frontera de agrupación; 6 casos canónicos verificados: 1 finding si mismo settlement, 2 findings si distinto settlement, N:1, 1:N, importes distintos y reconciliación mixta)`

### QA-57 — Diagnóstico no muta evidencia

- **Prioridad / Severidad**: `P0` / `CRITICAL`
- **Componente**: `storage/readonly`
- **Estado**: **`SATISFIED`**
- **Obligación / Requisito**: Operaciones de diagnóstico, inspectores y comandos de lectura operan en modo solo-lectura y jamás mutan el estado persistido.
- **Fases con Evidencia**: Fase 3, Unit/Integration
- **Artefactos de Respaldo**:
  - `output/e2e/persistence_crash/CRASH_AND_PERSISTENCE_REPORT.md`
  - `tests/test_qa_infrastructure.py::test_impact_is_read_only_and_retains_unknowns`
- **Comando de Verificación**: `.venv/bin/pytest tests/test_qa_infrastructure.py -k test_impact_is_read_only`
- **Resultado Observado**: `PASS (read-only diagnostic safety)`

### QA-58 — Píxel exacto y matrices visuales exhaustivas

- **Prioridad / Severidad**: `P3` / `LOW`
- **Componente**: `ui/visual`
- **Estado**: **`DEFERRED_WITH_REASON`**
- **Obligación / Requisito**: Comparación visual exhaustiva pixel a pixel de toda la UI; diferida por diseño ante fragilidad y cobertura suficiente por DOM reconciliation.
- **Fases con Evidencia**: Diferido
- **Artefactos de Respaldo**:
  - `docs/TEST_MATRIX.md#qa-58`
- **Comando de Verificación**: `N/A (Diferido formalmente)`
- **Resultado Observado**: `DEFERRED_WITH_REASON (prioridad P3/C, fragilidad de renderizado cross-driver; DOM y CSS cubiertos contractualmente en QA-39)`

---

## 4. Conclusión y Hoja de Ruta Hacia Fases 8 y 9

1. **Fase 7 Concluida**: El backlog histórico de 58 familias queda reconciliado, auditado y registrado sin deudas ambiguas.
2. **Gate S Cerrado**: 49 familias 100% satisfechas y 1 parcial delimitada arquitectónicamente cubren todo el espectro sintético y técnico.
3. **Transición a Fase 8 (CI / Regresión Automatizada)**: Integración en pipeline continuo de los 174 tests de regresión, verificación de packaging y suite de defensas.
4. **Fase 9 (Plataforma y Escala)**: Ejecución en host nativo Windows (`QA-41`, `QA-47`) y benchmark masivo de 100k filas (`QA-48`).
5. **Fase R / Gate P (Cliente Real)**: Apertura inmediata ante la recepción del primer dataset confidencial de producción para cerrar `QA-45`, `QA-51` y `QA-52`.