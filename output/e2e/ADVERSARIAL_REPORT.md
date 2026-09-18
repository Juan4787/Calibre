# INFORME DE VERIFICACIÓN: FASE 2 — E2E ADVERSARIAL DE INCERTIDUMBRE Y METAMORFISMOS

**Fecha**: 2026-09-17  
**Commit base bajo prueba**: `8e308cfebd5eda2c63a61a8a69ca0a5a4be80ce1`  
**Artefacto instalado y ejecutado**: `dist/freight_audit-0.1.0-py3-none-any.whl`  
**SHA-256 del Wheel**: `9a1984547c6020029a6937f4a2479fda935d085948e092f9654f1f65bfb7562b`  
**Entorno de ejecución aislado**: `/tmp/calibre-e2e-adversarial/` (clean-room estricto, Python 3.12 venv, sin `PYTHONPATH` al checkout)  
**Navegador automatizado**: Chromium headless vía Playwright  
**Base de datos operacional**: `/tmp/calibre-e2e-adversarial/db/adversarial_audit.db` (puerto `8770`)  
**Resultado final**: **APROBADO — GATE CUMPLIDO AL 100%**  

---

## 1. Declaración Formal del Gate de Salida

> **"Todos los escenarios de incertidumbre conservan causalidad, estado, importes y provenance a través de toda la cadena productiva (`archivo → importer → snapshot → engine → SQLite → API → UI → XLSX → HTML`). La incertidumbre jamás se transforma silenciosamente en certeza al atravesar capas, y un FAIL real jamás se pierde o se enmascara."**

- **Divergencias económicas y de estado entre representaciones**: **0**
- **Divergencias de provenance y trazabilidad entre representaciones**: **0**
- **Promociones indebidas de incertidumbre (`REVIEW`/`UNDETERMINABLE` $\to$ `PASS`/`FAIL`)**: **0**
- **Degradaciones o pérdidas de fallas reales (`FAIL` $\to$ `PASS`/`REVIEW`)**: **0**
- **Violaciones de invariancia metamórfica (Meta-1 .. Meta-6)**: **0**
- **Modificaciones al código fuente de producción (`src/freight_audit/`)**: **0**

---

## 2. Los 10 Escenarios Adversariales de Incertidumbre y 2 Casos de Control

Cada caso inició con una expectativa técnica formalmente predefinida y fue rastreado de extremo a extremo a través de las 6 capas:

| Código | Descripción del Caso Adversarial | Entrada / Condición Provocada | Estado Esperado | Causalidad / Razón Semántica | Estado Observado (6 Canales) |
|---|---|---|:---:|---|:---:|
| **CTRL-PASS** | Control Determinista Coincidente | 10 kg × 10 ARS/kg = 100 ARS. Facturado: 100 ARS. | `PASS` | Coincidencia unívoca y liquidación exacta sin discrepancias. | `PASS` / `Coincide` |
| **CTRL-FAIL** | Control Determinista Discrepante | 10 kg × 10 ARS/kg = 100 ARS. Facturado: 120 ARS. | `FAIL` | Sobreprecio comprobado de +20 ARS con regla y tarifa unívoca. | `FAIL` / `Discrepancia` |
| **ADV-01** | Matching con dos candidatos | Cargo C1 (REM-001) coincide con remitos S1A y S1B. | `REVIEW` | Ambigüedad de enlace operacional: 2 candidatas detectadas. | `REVIEW` / `Revisión humana` |
| **ADV-02** | Moneda incompatible | Cargo C2 liquidado en USD vs acuerdo en ARS sin tasa. | `UNDETERMINABLE` | Barrera estricta de divisa: no hay conversión configurada. | `UNDETERMINABLE` / `Indeterminado` |
| **ADV-03** | Evidencia obligatoria ausente | Cargo C3 (concepto ESPECIAL) exige `auth_doc` ausente. | `REVIEW` | Falta evidencia requerida en snapshot documental. | `REVIEW` / `Revisión humana` |
| **ADV-04** | Vigencias superpuestas | Fecha `15/08/2026` (S4) cae en `V-OVERLAP-1` (01/07 a 31/08) y `V-OVERLAP-2` (01/08 a 30/09). | `UNDETERMINABLE` | Ambigüedad contractual: múltiples versiones vigentes en agosto. | `UNDETERMINABLE` / `Indeterminado` |
| **ADV-05** | Fecha contractual ausente | Remito S5 sin fecha de servicio (`service_date` vacío). | `UNDETERMINABLE` | Falta fecha para determinar versión contractual aplicable. | `UNDETERMINABLE` / `Indeterminado` |
| **ADV-06** | Regla tarifaria ambigua | V-AMBIGUOUS contiene dos reglas para concepto FLETE. | `UNDETERMINABLE` | Ambigüedad en tarifario: múltiples reglas aplicables. | `UNDETERMINABLE` / `Indeterminado` |
| **ADV-07** | Cargo sin match | Cargo C7 con remito REM-UNKNOWN inexistente en viajes. | `REVIEW` | Cargo huérfano: sin coincidencia unívoca con operaciones. | `REVIEW` / `Revisión humana` |
| **ADV-08** | Posible duplicado | Cargos C8A ($200) y C8B ($200) sobre el mismo remito S8. | `REVIEW` | Colisión de firma: múltiples cargos para mismo remito/concepto. | `REVIEW` / `Revisión humana` |
| **ADV-09** | Importación con fila rechazada | Fila con datos corruptos en remitos (`operaciones_with_error`). | `REVIEW` (Estructural) | Corrupción de ingesta: bloquea certeza y fuerza revisión preventiva. | Banner en UI + 8 REVIEW / 4 UNDET |
| **ADV-10** | Cargos parcialmente asignables | Cargos C10A y C10B se superponen en concepto FLETE sobre S10. | `REVIEW` | Asignación parcial/superpuesta de conceptos en liquidación. | `REVIEW` / `Revisión humana` |

---

## 3. Comportamiento Estructural ante Ingesta Corrupta (ADV-09)

En la ejecución preliminar de ADV-09:
- Se cargó `operaciones_with_error.csv` con una fila rechazada deliberadamente.
- **Detección inmediata en UI**: El formulario de importación reportó `1 fila rechazada`.
- **Efecto de propagación en la auditoría**:
  - Banner en la UI: *"1 fila de remitos fue rechazada durante la importación. La liquidación contiene incertidumbre estructural: los hallazgos determinables pasan a revisión preventiva y no deben liquidarse automáticamente."*
  - **Bloqueo estricto de liquidación automática**:
    - `PASS`: **0** (CTRL-PASS fue preventivamente degradado a `REVIEW`).
    - `FAIL`: **0** (CTRL-FAIL fue preventivamente degradado a `REVIEW`).
    - `REVIEW`: **8**
    - `UNDETERMINABLE`: **4**
- **Conclusión**: Un error en la capa de ingesta jamás permite liquidar a ciegas; la incertidumbre estructural contamina la certeza aguas abajo de forma segura y transparente.

---

## 4. Auditoría Adversarial Baseline (Corrida Limpia)

Con el dataset adversarial limpio (`operaciones_adv.csv`, `cargos_adv.csv`, `agreements_adv.json`):
- **ID de Corrida**: `9605b5d0734142ac7f25c69519ba53ebdb4f45dc07620ef6391edd39a992ee77`
- **Resultados Consolidados**:
  - `PASS`: 1 (`CTRL-PASS`)
  - `FAIL`: 1 (`CTRL-FAIL`)
  - `REVIEW`: 6 (`ADV-01`, `ADV-03`, `ADV-07`, `ADV-08`, `ADV-10A`, `ADV-10B`)
  - `UNDETERMINABLE`: 4 (`ADV-02`, `ADV-04`, `ADV-05`, `ADV-06`)
  - **Total de hallazgos**: 12
  - **Cobertura determinable**: 17% (2 de 12 hallazgos)
  - **Métricas económicas en ARS**:
    - Facturado Aceptado: **$1.220 ARS**
    - Exceso Determinado: **$20 ARS**
    - Importe en Revisión: **$700 ARS**
    - Importe Indeterminado: **$300 ARS**
  - **Métricas económicas en USD**:
    - Facturado Aceptado: **$50 USD**
    - Exceso Determinado: **$0 USD**
    - Importe en Revisión: **$0 USD**
    - Importe Indeterminado: **$50 USD**
- **Interacción y Decisión Humana**:
  - Se inspeccionó el modal del hallazgo C_FAIL (`CTRL-FAIL`) en Chromium.
  - Se registró la decisión humana: Acción `REJECTED`, Comentario `"Sobreprecio adversarial rechazado formalmente"`, Actor `"Auditor Adversarial"`.
  - Reflejo inmediato en el DOM y persistencia en la tabla SQLite `decisions`.

---

## 5. Metamorfismos E2E (Invariancia Semántica y Operacional)

Se ejecutaron 6 transformaciones metamórficas que no deben alterar la semántica económica del lote auditado:

1. **Meta-1 (Renombrado de Archivos)**:
   - Entradas: `viajes_adversariales_marzo.csv` y `liquidacion_proveedor_exp.csv`.
   - Resultado: Conteos (1 PASS, 1 FAIL, 6 REVIEW, 4 UNDETERMINABLE) y monedas idénticos al baseline.
2. **Meta-2 (Reordenamiento Inverso de Filas)**:
   - Entradas: Inversión estricta del orden de las filas en ambos CSVs.
   - Resultado: Invariante 100%. El orden de lectura no influye en las reglas de matching ni en el motor.
3. **Meta-3 (Permutación de Columnas)**:
   - Entradas: Columnas de remitos barajadas (`service_date, origin, ...`).
   - Resultado: Invariante 100%. La resolución basada en nombres lógicos de mapping funciona independientemente de la posición ordinal.
4. **Meta-4 (Adición de Columnas Irrelevantes)**:
   - Entradas: Se agregaron columnas no mapeadas (`comentarios_chofer, metadata_gps`).
   - Resultado: Invariante 100%. Las columnas desconocidas son ignoradas sin generar efectos colaterales.
5. **Meta-5 (Reinicio en Frío de la Aplicación)**:
   - Se envió señal `SIGTERM` al servidor en el puerto 8770.
   - Se levantó un proceso de servidor completamente nuevo contra la base de datos persistida.
   - Playwright navegó a la UI: la corrida `9605b5d0...` fue recuperada intacta, con su statusline original y la decisión humana registrada.
   - Se ejecutó el botón de Replay en el navegador: confirmación `"Reproducción idéntica"`.
6. **Meta-6 (Doble Exportación Idempotente)**:
   - Se descargó el reporte HTML por segunda vez tras el reinicio en frío.
   - Comparación de checksums SHA-256:
     - Exportación 1: `b21e489615ecd192f369dc357d3720499ceb8bc34b8e7579c3a513328133164f`
     - Exportación 2: `b21e489615ecd192f369dc357d3720499ceb8bc34b8e7579c3a513328133164f`
     - **Identidad byte por byte demostrada**.

---

## 6. Matriz de Reconciliación de Estados e Importes (6 Canales)

Rastreo exhaustivo de la información a través de:
$$\text{SQLite} \equiv \text{API} \equiv \text{JSON} \equiv \text{XLSX} \equiv \text{HTML} \equiv \text{UI}$$

| ID Cargo | Caso | Concepto | Moneda | Facturado | Esperado | Dif. | SQLite | API | JSON | XLSX | HTML | UI | Divergencia |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `C_PASS` | **CTRL-PASS** | FLETE | ARS | 100 | 100 | 0 | PASS | PASS | PASS | Coincide | Coincide | Coincide | **ZERO** |
| `C_FAIL` | **CTRL-FAIL** | FLETE | ARS | 120 | 100 | +20 | FAIL | FAIL | FAIL | Discrepancia | Discrepancia | Discrepancia | **ZERO** |
| `C1` | **ADV-01** | FLETE | ARS | 100 | — | — | REVIEW | REVIEW | REVIEW | Revisión humana | Revisión humana | Revisión humana | **ZERO** |
| `C2` | **ADV-02** | FLETE | USD | 50 | — | — | UNDETERMINABLE | UNDETERMINABLE | UNDETERMINABLE | Indeterminado | Indeterminado | Indeterminado | **ZERO** |
| `C3` | **ADV-03** | ESPECIAL | ARS | 100 | 100 | 0* | REVIEW | REVIEW | REVIEW | Revisión humana | Revisión humana | Revisión humana | **ZERO** |
| `C4` | **ADV-04** | FLETE | ARS | 100 | — | — | UNDETERMINABLE | UNDETERMINABLE | UNDETERMINABLE | Indeterminado | Indeterminado | Indeterminado | **ZERO** |
| `C5` | **ADV-05** | FLETE | ARS | 100 | — | — | UNDETERMINABLE | UNDETERMINABLE | UNDETERMINABLE | Indeterminado | Indeterminado | Indeterminado | **ZERO** |
| `C6` | **ADV-06** | FLETE | ARS | 100 | — | — | UNDETERMINABLE | UNDETERMINABLE | UNDETERMINABLE | Indeterminado | Indeterminado | Indeterminado | **ZERO** |
| `C7` | **ADV-07** | FLETE | ARS | 100 | — | — | REVIEW | REVIEW | REVIEW | Revisión humana | Revisión humana | Revisión humana | **ZERO** |
| `C8A` | **ADV-08** | FLETE | ARS | 200 | 100 | +100* | REVIEW | REVIEW | REVIEW | Revisión humana | Revisión humana | Revisión humana | **ZERO** |
| `C10A` | **ADV-10A** | FLETE | ARS | 100 | 100 | 0* | REVIEW | REVIEW | REVIEW | Revisión humana | Revisión humana | Revisión humana | **ZERO** |
| `C10B` | **ADV-10B** | FLETE | ARS | 100 | 100 | 0* | REVIEW | REVIEW | REVIEW | Revisión humana | Revisión humana | Revisión humana | **ZERO** |

*\* Nota técnica: En los casos en que existe un cálculo preliminar de tarifa pero el hallazgo queda en `REVIEW` (por falta de evidencia, duplicidad o superposición), el sistema expone explícitamente en el DOM y en las exportaciones la leyenda `"No confirmada"` junto a la diferencia, impidiendo que el motor compute el valor como ahorro confirmado en `confirmed_overcharge`.*

---

## 7. Reconciliación Explícita de Provenance y Causalidad (4 Casos Representativos)

Para certificar que la procedencia y la trazabilidad celda-a-celda persisten de forma idéntica a través de toda la cadena (`Archivo → Importer → Snapshot → Engine → SQLite → API → UI → XLSX → HTML`), se detalla la reconciliación cruzada de 4 casos representativos:

### Caso A: `CTRL-PASS` (Control Determinista Coincidente)
- **Origen en Archivos**:
  - Cargo: `cargos_adv.csv`, Fila `2`, Columna `amount`, Valor raw `"100,00"`, Ref `"REM-PASS"`.
  - Operación: `operaciones_adv.csv`, Fila `2`, ID `"S_PASS"`, Columna `weight`, Valor raw `"10,00"`.
- **Contrato y Regla**: Acuerdo `AGR-ADV`, Versión `V-BASE` (2026-01-01 a 2026-06-30), Regla `R-BASE` (`weight * 10 ARS/kg`).
- **Persistencia y Canales**:
  - **SQLite / API / JSON**: `charge_ids: ["C_PASS"]`, `shipment_ids: ["S_PASS"]`, `agreement: "AGR-ADV"`, `version: "V-BASE"`, `rule: "R-BASE"`, `trace` con op `matching` (resolución unívoca de `REM-PASS`) y op `mul` ($10 \times 10 = 100$).
  - **XLSX (Hoja Hallazgos)**: Fila 2: Cargos=`C_PASS`, Operaciones=`S_PASS`, Regla=`R-BASE`, Versión=`V-BASE`, Facturado=100, Esperado=100.
  - **HTML**: Tarjeta de hallazgo vincula remito `REM-PASS`, ID cargo `C_PASS`, operación `S_PASS`, regla `R-BASE` y versión `V-BASE`.
  - **UI (Modal Chromium)**: Despliega Operación `S_PASS`, Cargo `C_PASS`, trazabilidad celda a celda con archivo `cargos_adv.csv` fila 2 y regla `R-BASE`.

### Caso B: `CTRL-FAIL` (Control Determinista Discrepante)
- **Origen en Archivos**:
  - Cargo: `cargos_adv.csv`, Fila `3`, Columna `amount`, Valor raw `"120,00"`, Ref `"REM-FAIL"`.
  - Operación: `operaciones_adv.csv`, Fila `3`, ID `"S_FAIL"`, Columna `weight`, Valor raw `"10,00"`.
- **Contrato y Regla**: Acuerdo `AGR-ADV`, Versión `V-BASE`, Regla `R-BASE` (calcula 100 ARS). Discrepancia real = +20 ARS.
- **Persistencia y Canales**:
  - **SQLite / API / JSON**: `charge_ids: ["C_FAIL"]`, `shipment_ids: ["S_FAIL"]`, `difference: "20"`, `confirmed_difference: "20"`, decisión registrada `REJECTED` vinculada con FK a la corrida.
  - **XLSX (Hoja Hallazgos)**: Cargos=`C_FAIL`, Operaciones=`S_FAIL`, Regla=`R-BASE`, Versión=`V-BASE`, Facturado=120, Esperado=100, Dif=20.
  - **HTML**: Tarjeta muestra sobreprecio de +20 ARS con regla `R-BASE` y versión `V-BASE`.
  - **UI (Modal Chromium)**: Tabla de trazabilidad de reglas muestra `mul` ($10 \times 10 = 100$), diferencia calculada de 20 ARS y decisión humana persistida como `Rechazado`.

### Caso C: `ADV-03` (Incertidumbre: Evidencia Obligatoria Ausente)
- **Origen en Archivos**:
  - Cargo: `cargos_adv.csv`, Fila `7`, Columna `concept`, Valor raw `"ESPECIAL"`, Monto `"100,00"`, Ref `"REM-003"`.
  - Operación: `operaciones_adv.csv`, Fila `7`, ID `"S3"`, Ref `"REM-003"`.
- **Contrato y Regla**: Acuerdo `AGR-ADV`, Versión `V-BASE`, Regla `R-SPECIAL` (requiere `authorization`).
- **Causalidad de Incertidumbre y Canales**:
  - **SQLite / API / JSON**: `status: "REVIEW"`, `missing_evidence: ["S3: authorization"]`, `reasons: ["Falta evidencia requerida: S3: authorization. Solicitar el respaldo antes de resolver."]`, `difference: "0"` (diferencia no confirmada).
  - **XLSX (Hoja Hallazgos)**: Cargos=`C3`, Operaciones=`S3`, Regla=`R-SPECIAL`, Motivo=`Falta evidencia requerida: S3: authorization...`.
  - **HTML**: Tarjeta de hallazgo indica `Revisión humana` con motivo textual de falta de autorización.
  - **UI (Modal Chromium)**: Despliega remito `S3`, regla `R-SPECIAL`, badge de advertencia por evidencia faltante y formulario de adjunto.

### Caso D: `ADV-04` (Incertidumbre: Vigencias Superpuestas)
- **Origen en Archivos**:
  - Cargo: `cargos_adv.csv`, Fila `8`, Columna `amount`, Valor raw `"100,00"`, Ref `"REM-004"`.
  - Operación: `operaciones_adv.csv`, Fila `8`, ID `"S4"`, Columna `service_date`, Valor raw `"15/08/2026"` (fecha ISO `2026-08-15`).
- **Conflicto Contractual**: Acuerdo `AGR-ADV` tiene `V-OVERLAP-1` (vigente `2026-07-01` a `2026-08-31`) y `V-OVERLAP-2` (vigente `2026-08-01` a `2026-09-30`). Ambas cubren el `2026-08-15`.
- **Causalidad de Incertidumbre y Canales**:
  - **SQLite / API / JSON**: `status: "UNDETERMINABLE"`, `version: null`, `rule: null`, `expected: null`, `reasons: ["Múltiples versiones del acuerdo vigentes para la fecha 2026-08-15: V-OVERLAP-1, V-OVERLAP-2"]`.
  - **XLSX (Hoja Hallazgos)**: Cargos=`C4`, Operaciones=`S4`, Regla=`—`, Versión=`—`, Motivo=`Múltiples versiones del acuerdo vigentes para la fecha 2026-08-15...`.
  - **HTML**: Tarjeta `Indeterminado` detallando el conflicto explícito de versiones temporales en agosto de 2026.
  - **UI (Modal Chromium)**: Muestra remito `S4`, fecha `15/08/2026` y trazabilidad de selección de versión interrumpida por superposición temporal.

---

## 8. Verificación de Invariantes Críticos

1. **Invariante de Preservación de la Incertidumbre**:
   - Para los 10 casos adversariales (`ADV-01` al `ADV-10`), en ninguna de las capas (`SQLite`, `API`, `JSON`, `XLSX`, `HTML`, `UI`) el estado fue promovido a `PASS` o `FAIL`.
2. **Invariante de No Enmascaramiento de Fallas Reales**:
   - El caso `CTRL-FAIL` mantuvo su estado `FAIL` / `Discrepancia` y su exceso de +20 ARS intactos a través de toda la cadena, sin ser arrastrado indebidamente por la presencia de casos indeterminados adyacentes.
3. **Invariante de Trazabilidad y Provenance**:
   - Cada hallazgo en la base de datos conserva su puntero al documento origen (`operaciones.csv`, `cargos.csv`), la fila correspondiente y la traza detallada de reglas ejecutadas.

---

## 9. Conclusión y Veredicto de Fase 2

La Fase 2 queda **CERRADA AL 100% CON ÉXITO ABSOLUTO**.  
El sistema Freight Audit / Calibre 0.1.0 demostró una rigidez semántica impecable frente a anomalías adversariales, preservando causalidad, estado, importes y provenance celda-a-celda a través de toda la cadena productiva.
