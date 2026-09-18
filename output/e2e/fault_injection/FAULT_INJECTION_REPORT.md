# FASE 6 — INFORME DE FAULT INJECTION Y EFECTIVIDAD REAL DE DEFENSAS

**Estado**: **CERRADA EXITOSAMENTE (GATE P0 100% CUMPLIDO)**  
**Fecha de Ejecución**: 2026-09-17 / 2026-09-18  
**Commit Baseline**: `ace3425aa4c73f6a4a104971323e4bd207ecbd5c`  
**Paquete Auditado**: `freight-audit 0.1.0` (Wheel SHA-256: `0d1b3c2ce3b8510e0ecd5d88e8a23ad4d0346de02e69059dd15c843f3c18419a`)  
**Integridad de Producción**: `git diff --exit-code src/freight_audit/` -> **0 modificaciones (100% LIMPIO)**

---

## 1. Resumen Ejecutivo y Decisión de Gate

El objetivo central de la **Fase 6** fue demostrar experimentalmente que los errores económicamente peligrosos, las mentiras entre capas arquitectónicas y las corrupciones de estado o historia **no sólo son improbables, sino intrínsecamente detectables por defensas independientes antes de que el usuario o el sistema puedan confiar en el resultado**.

A diferencia de las fases anteriores —donde se evaluó si Calibre producía resultados correctos ante datos reales, adversariales y generales—, en la Fase 6 se forzó deliberadamente a que componentes individuales **mintieran o computaran erróneamente**, para verificar si otra frontera defensiva desacoplada desenmascaraba la anomalía.

### Criterio de Gate Prerregistrado

> *Fase 6 sólo puede cerrarse si todos los faults P0 no equivalentes son PREVENTED o DETECTED por al menos una defensa independiente antes de que su resultado pueda considerarse confiable; ningún P0 puede quedar SURVIVED. Los controles sanos no pueden ser marcados sistemáticamente como corruptos. Toda conclusión debe estar respaldada por evidencia reproducible.*

### Métricas Consolidadas de Gate

| Métrica | Requisito de Cierre | Resultado Obtenido | Estado |
| :--- | :---: | :---: | :---: |
| **P0 Detection Rate** | **100.0%** (0 supervivientes) | **100.0% (33 / 33)** | **PASS** |
| **P1 Detection Rate** | 100% evaluado/atrapado | **100.0% (8 / 8)** | **PASS** |
| **P2 Total** | 0 no clasificados | **0** | **PASS** |
| **Healthy False-Positive Rate** | **0.0%** (12 controles sanos) | **0.0% (0 / 12 falsos positivos)** | **PASS** |
| **Metadata-Blind Detection Rate (6G)** | Alta efectividad agnóstica | **100.0% (10 / 10 ciegos detectados)** | **PASS** |
| **Integridad de Producción** | 0 mutaciones en `src/` | **0 mutaciones permanentes** | **PASS** |

**Decisión**: **FASE 6 CONCLUIDA Y SELLADA**. No se registró ningún defecto P0 ni P1 que lograra engañar a las defensas (`SURVIVED = 0`).

---

## 2. Arquitectura de Defensas Independientes

Para evitar defensas circulares (donde el test sabe qué línea se cambió), la evaluación se ejecutó mediante un evaluador agnóstico (`detector_runner.py`) que inspecciona artefactos, bundles y respuestas a través de 5 propiedades ontológicas independientes:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                 CALIBRE CORE                                      │
│   Sources (Raw Files) ──> Importer ──> Snapshot ──> Engine ──> SQLite / Replay    │
└─────────────────────────────────────┬─────────────────────────────────────────────┘
                                      │
               Export Channels:       ├──────> audit.json & snapshot.json
                                      ├──────> auditoria.xlsx (8 hojas)
                                      ├──────> reporte.html (tablas & badges)
                                      ├──────> API HTTP / OpenAPI
                                      └──────> UI DOM / Web Application
                                      │
┌─────────────────────────────────────▼─────────────────────────────────────────────┐
│                      DEFENSAS SISTÉMICAS INDEPENDIENTES                           │
├──────────────────────────┬────────────────────────────────────────────────────────┤
│ Invariant Engine         │ Valida INV-01..INV-29 sobre JSON, sin ejecutar motor   │
│ Deterministic Replay     │ Re-deriva resultado desde snapshot y compara hallazgo  │
│ Multi-Channel Reconciler │ Cruza XLSX, HTML, JSON, API y DOM (cero tolerancia)    │
│ Provenance Verifier      │ Rastrea celdas/filas a documentos fuente inmutables    │
│ Bundle Manifest Verifier │ Comprueba SHA-256 byte a byte y presencia de archivos  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

1. **`Invariant Engine` (`qa.invariants`)**: Reglas matemáticas e invariantes de conservación económica (`INV-01` a `INV-29`). Verifica que la suma de cargos coincida con el total, que no se confirme dinero en `REVIEW` o `UNDETERMINABLE`, que no se mezclen monedas, que los estados respeten tolerancias y que la cadena de decisiones hash esté intacta.
2. **`Deterministic Replay` (`Store.replay` / `freight_audit.engine.audit`)**: Re-computa de forma pura el resultado desde el snapshot inmutable y contrasta cada hallazgo contra el resultado persistido.
3. **`Multi-Channel Reconciler` (`qa.reconcile`)**: Lee de manera cruzada las representaciones físicas (XLSX con 8 hojas, HTML con tablas parseadas, JSON, API y DOM) asegurando que ninguna capa suavice o altere un número o estado.
4. **`Provenance Verifier`**: Valida que cada referencia documental en charges/shipments apunte a un archivo existente en `sources/` con hash SHA-256 verificado y coordenadas válidas.
5. **`Bundle Manifest Verifier`**: Valida que todos los archivos del bundle correspondan a sus digests SHA-256 declarados en `manifest.json`.

---

## 3. Catálogo y Matriz Completa de Inyección (41 Faults)

Todos los defectos fueron prerregistrados en `FAULT_CATALOG.md` y `expected_detectors.json` antes de su ejecución. A continuación se detalla la matriz de resultados observada:

### Grupo FI-I: Importación y Normalización (6 Defectos)

| Fault ID | Capa Atacada | Mutación Inyectada | Severidad | Defensas Disparadas | Estado |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **FI-I01** | Importer | Importe alterado `+0.01` tras lectura documental | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-I02** | Importer | Cambio de signo (`100.00` -> `-100.00`) | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-I03** | Importer | Moneda mutada (`ARS` -> `USD`) en un cargo | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-I04** | Importer | Fecha contractual (`service_date`) desplazada a nueva vigencia | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-I05** | Importer | Referencia alterada (`REM-001` -> `REM-MUTATED-999`) | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-I06** | Importer | Provenance apuntando a fila/columna corrupta (`row: 999`) | P1 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |

*Análisis causal FI-I*: Cualquier alteración previa al motor o en el snapshot rompe la conservación de importes (`INV-05`), la partición de cargos (`INV-04`), el matching contractual por vigencias (`INV-08`), o la integridad de provenance (`INV-22`). Además, el replay determinista reproduce el cálculo legítimo y detecta la divergencia.

---

### Grupo FI-E: Engine Económico (12 Defectos)

| Fault ID | Capa Atacada | Mutación Inyectada | Severidad | Defensas Disparadas | Estado |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **FI-E01** | Engine | Invertir fórmula de diferencia (`actual - expected` -> `expected - actual`) | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E02** | Engine | Tolerancia inclusiva convertida en exclusiva (`<= tol` -> `< tol`) | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E03** | Engine | Confirmar diferencia monetaria estando en `REVIEW` | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E04** | Engine | Confirmar diferencia monetaria y expectativa en `UNDETERMINABLE` | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E05** | Engine | Certificar como `PASS` ignorando evidencia requerida ausente | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E06** | Engine | Seleccionar primera versión arbitraria ante solapamiento de vigencias | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E07** | Engine | Seleccionar primera regla arbitraria ante ambigüedad en vez de `UNDETERMINABLE` | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E08** | Engine | Seleccionar primer shipment ante matching ambiguo de múltiples candidatos | P0 | `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E09** | Engine | Mezclar o adulterar totales por moneda en resumen económico | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E10** | Engine | Pérdida silenciosa de un cargo en findings ($N \to N-1$) | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E11** | Engine | Duplicación indebida de un cargo en findings ($N \to N+1$) | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-E12** | Engine | Redondeo prematuro que altera los centavos de la expectativa | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |

*Análisis causal FI-E*: El motor está cercado por dos defensas complementarias: el verificador formal de invariantes (`INV-01`, `INV-02`, `INV-03`, `INV-04`, `INV-06`, `INV-07`, `INV-08`, `INV-10`, `INV-13`) y el replay determinista de recomputación completa. Ningún error aritmético o de asignación pudo pasar inadvertido.

---

### Grupo FI-P: Persistencia e Historia (5 Defectos)

| Fault ID | Capa Atacada | Mutación Inyectada | Severidad | Defensas Disparadas | Estado |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **FI-P01** | Persistence | Snapshot legítimo con `result` sustituido por el de otra corrida | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-P02** | Persistence | Decisión humana vinculada a finding inexistente | P1 | `invariants`, `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-P03** | Persistence | Orden alterado en la cadena de decisiones o hash previo corrupto | P1 | `invariants`, `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-P04** | Persistence | `artifact_hash` falsificado en el registro de auditoría | P1 | `invariants`, `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-P05** | Persistence | Fuentes válidas pero incompletas (archivo eliminado de `sources/`) | P1 | `manifest_verifier`, `provenance_verifier`, `reconcile` | **DETECTED** |

*Análisis causal FI-P*: La inmutabilidad criptográfica (`INV-28` input/result/artifact hash), el encadenamiento de decisiones SHA-256 (`INV-24`) y la integridad referencial de fuentes documentales (`INV-22`) impiden que el almacenamiento acepte o certifique historias falsificadas.

---

### Grupo FI-R: Reporting y Exportaciones (6 Defectos)

| Fault ID | Capa Atacada | Mutación Inyectada | Severidad | Defensas Disparadas | Estado |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **FI-R01** | Export/XLSX | `REVIEW` -> `PASS` ("Coincide") exclusivamente en XLSX | P0 | `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-R02** | Export/HTML | `UNDETERMINABLE` -> `FAIL` ("Discrepancia") exclusivamente en HTML | P0 | `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-R03** | Export/XLSX | Diferencia económica alterada (`20.00` -> `99999.00`) en Excel | P0 | `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-R04** | Export/XLSX | Fila de finding eliminada de la hoja "Hallazgos" | P0 | `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-R05** | Export/XLSX | Moneda cambiada (`ARS` -> `USD`) sin tocar importe | P0 | `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-R06** | Export/XLSX | Motivo (`reasons`) y evidencia eliminados de fila `REVIEW` | P1 | `manifest_verifier`, `reconcile` | **DETECTED** |

*Análisis causal FI-R*: Los exportadores no pueden mentirle al usuario final. El reconciliador de representaciones (`qa.reconcile`) parsea celdas de openpyxl y nodos HTML contrastándolos contra el `audit.json` y el `snapshot.json`. Ante la menor divergencia de etiquetas, importes o motivos, el reconciliador emite violaciones `INV-23`.

---

### Grupo FI-A y FI-U: API y UI (8 Defectos)

| Fault ID | Capa Atacada | Mutación Inyectada | Severidad | Defensas Disparadas | Estado |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **FI-A01** | API | API devuelve estado diferente al persistido (`FAIL` -> `PASS`) | P0 | `reconcile` | **DETECTED** |
| **FI-A02** | API | API omite un finding respecto a la corrida persistida | P0 | `reconcile` | **DETECTED** |
| **FI-A03** | API | API altera el importe actual (`actual`) en un finding | P0 | `reconcile` | **DETECTED** |
| **FI-A04** | API | API pierde el bloque de provenance en el snapshot | P1 | `reconcile` | **DETECTED** |
| **FI-U01** | UI DOM | Core tiene `REVIEW`, pero DOM muestra "Coincide" (`PASS`) | P0 | `reconcile` | **DETECTED** |
| **FI-U02** | UI DOM | Core tiene diferencia real, pero DOM muestra `+2,00` | P0 | `reconcile` | **DETECTED** |
| **FI-U03** | UI DOM | Core tiene `ARS`, pero DOM muestra `USD` | P0 | `reconcile` | **DETECTED** |
| **FI-U04** | UI DOM | DOM omite la completitud documental (`complete: False`) | P1 | `reconcile` | **DETECTED** |

*Análisis causal FI-A y FI-U*: La reconciliación multicanal valida contractualmente las respuestas serializadas de la API REST y las capturas del árbol DOM de Playwright, bloqueando cualquier suavizado cosmético o desincronización entre frontend y backend.

---

### Grupo FI-X: Cross-Layer y Combinados (4 Defectos)

| Fault ID | Capa Atacada | Mutación Inyectada | Severidad | Defensas Disparadas | Estado |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **FI-X01** | Cross-layer | Desincronización coordinada Importer + Excel para enmascarar | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-X02** | Cross-layer | Mutación en cascada: Core `REVIEW`, HTML `PASS`, UI "Coincide" | P0 | `manifest_verifier`, `reconcile` | **DETECTED** |
| **FI-X03** | Cross-layer | Falsificación coordinada snapshot + result sin tocar fuente raw | P0 | `invariants`, `manifest_verifier`, `reconcile`, `replay` | **DETECTED** |
| **FI-X04** | Cross-layer | Alteración física de bytes en `audit.json` sin tocar manifest | P0 | `manifest_verifier`, `reconcile` | **DETECTED** |

---

## 4. Subfase 6G — Evaluación Ciega (Metadata-Blind Detection)

Para evaluar la capacidad de detección sin sesgo de selectores o tests dirigidos, se implementó una modalidad **ciega a metadatos** (`run_blind_faults.py`):
1. El generador seleccionó 10 defectos del catálogo y los empaquetó como `BLIND-01` a `BLIND-10` en `output/e2e/fault_injection/blind/`.
2. Se **eliminó todo metadato, nombre de archivo, FAULT_ID o pista causal**.
3. El verificador agnóstico (`DetectorRunner`) evaluó cada corrida recibiendo únicamente los artefactos opacos.
4. Una vez emitidos los veredictos, se abrió el archivo criptográfico `secret_key.json` para corroborar el acierto causal.

> [!NOTE]
> **Matiz Metodológico sobre "Blind"**:
> El detector no conocía el `FAULT_ID` ni la línea mutada durante la ejecución, basando su veredicto exclusivamente en propiedades ontológicas (invariantes, digests y reconciliación cruzada de canales). Esta prueba demuestra **metadata-blind detection** (detección estricta sin metadatos en tiempo de ejecución dentro del espacio de familias de fallo conocidas del sistema), y no pretende representar una generalización omnisciente frente a clases de defecto ontológicamente ajenas a la arquitectura.

### Resultados de la Evaluación Ciega

| Blind ID | Veredicto Agnóstico | Violaciones | Severidad Est. | Fault Oculto Revelado | ¿Detectado? | Defensas Disparadas |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **BLIND-01** | **UNTRUSTED** | 8 | P0 | `FI-I01` (Importer +0.01) | **SÍ** | `invariants`, `manifest`, `reconcile`, `replay` |
| **BLIND-02** | **UNTRUSTED** | 8 | P0 | `FI-I02` (Sign change) | **SÍ** | `invariants`, `manifest`, `reconcile`, `replay` |
| **BLIND-03** | **UNTRUSTED** | 5 | P0 | `FI-E01` (Inverted diff) | **SÍ** | `invariants`, `manifest`, `reconcile`, `replay` |
| **BLIND-04** | **UNTRUSTED** | 7 | P0 | `FI-E03` (Diff in REVIEW) | **SÍ** | `invariants`, `manifest`, `reconcile`, `replay` |
| **BLIND-05** | **UNTRUSTED** | 12 | P0 | `FI-E10` (Dropped charge) | **SÍ** | `invariants`, `manifest`, `reconcile`, `replay` |
| **BLIND-06** | **UNTRUSTED** | 4 | P1 | `FI-P02` (Orphan decision) | **SÍ** | `invariants`, `manifest`, `reconcile` |
| **BLIND-07** | **UNTRUSTED** | 3 | P1 | `FI-P05` (Missing source) | **SÍ** | `manifest_verifier`, `reconcile` |
| **BLIND-08** | **UNTRUSTED** | 3 | P0 | `FI-R01` (XLSX status) | **SÍ** | `manifest_verifier`, `reconcile` |
| **BLIND-09** | **UNTRUSTED** | 1 | P0 | `FI-A03` (API amount) | **SÍ** | `reconcile` |
| **BLIND-10** | **UNTRUSTED** | 1 | P0 | `FI-U01` (UI DOM status) | **SÍ** | `reconcile` |

**Tasa de Detección Ciega**: **100.0% (10 de 10 detectados bajo modalidad metadata-blind)**.

---

## 5. Controles Negativos (Ausencia de Falsos Positivos)

Para garantizar que el detector agnóstico no fuera un filtro paranoico que rechace indiscriminadamente todo resultado, se evaluaron 12 escenarios de operación legítima (`run_healthy_controls.py`):

| Control ID | Escenario Operativo Probado | Veredicto | Violaciones | Estado |
| :--- | :--- | :---: | :---: | :---: |
| **CTRL-01** | Corrida base limpia con PASS, FAIL, REVIEW y UNDETERMINABLE | **TRUSTED** | 0 | **PASS** |
| **CTRL-02** | Presencia legítima de hallazgos en PASS determinista | **TRUSTED** | 0 | **PASS** |
| **CTRL-03** | Presencia legítima de hallazgos en FAIL determinista | **TRUSTED** | 0 | **PASS** |
| **CTRL-04** | Presencia legítima de hallazgos en REVIEW justificado | **TRUSTED** | 0 | **PASS** |
| **CTRL-05** | Presencia legítima de hallazgos en UNDETERMINABLE justificado | **TRUSTED** | 0 | **PASS** |
| **CTRL-06** | Incorporación válida de nueva evidencia y posterior re-auditoría | **TRUSTED** | 0 | **PASS** |
| **CTRL-07** | Ventana de vigencia contractual válida en fecha límite | **TRUSTED** | 0 | **PASS** |
| **CTRL-08** | Variación válida de nombre de archivo con contenido idéntico | **TRUSTED** | 0 | **PASS** |
| **CTRL-09** | Reordenamiento válido de columnas documentales en importación | **TRUSTED** | 0 | **PASS** |
| **CTRL-10** | Reinicio completo de proceso y recarga desde SQLite | **TRUSTED** | 0 | **PASS** |
| **CTRL-11** | Exportación repetida e idempotente del mismo bundle | **TRUSTED** | 0 | **PASS** |
| **CTRL-12** | Decisión humana registrada conforme modelo (`APPROVED`) en cadena SHA-256 | **TRUSTED** | 0 | **PASS** |

**Tasa de Falsos Positivos**: **0.0% (0 falsos positivos sobre 12 controles)**. Todos los casos sanos fueron clasificados como `TRUSTED`.

---

## 6. Registro de Incidentes y Gaps

Siguiendo el mandato estricto de la fase:
> *TU OBJETIVO NO ES CONSEGUIR 100% DE DETECCIÓN ARTIFICIAL. UN P0 SURVIVED BIEN REPRODUCIDO ES MÁS VALIOSO QUE UN INFORME TODO VERDE.*

Se monitoreó la existencia de cualquier defecto P0 no detectado. El directorio `output/e2e/fault_injection/incidents/` permaneció vacío porque **las 41 mutaciones fueron interceptadas o detectadas de manera inmediata**:
- **Defectos Prevenidos (`FAULT PREVENTED`)**: Aquellos donde los modelos Pydantic o invariantes estructurales abortaron el guardado/ejecución antes de emitir un resultado.
- **Defectos Detectados Post-Ocurrencia (`FAULT DETECTED`)**: 41 de 41 fueron atrapados por las defensas independientes (Invariants, Reconciler, Replay, Manifest Verifier, Provenance Verifier) emitiendo dictamen **`UNTRUSTED`**.
- **Defectos Sobrevivientes (`FAULT SURVIVED`)**: **0**.

---

## 7. Verificación de No-Regresión en Producción

Se verificó el árbol de trabajo completo del repositorio:
1. `git diff --exit-code src/freight_audit/` -> **Retorno 0 (Limpio)**.
2. La suite completa de tests de regresión del repositorio sigue en verde:
   ```bash
   pytest tests/
   ```
   **172 passed**.
3. Los artefactos de release generados al cierre de Fase 5 (`dist/freight_audit-0.1.0-py3-none-any.whl`) conservan su digest SHA-256 `0d1b3c2ce3b8510e0ecd5d88e8a23ad4d0346de02e69059dd15c843f3c18419a`.

---

## 8. Conclusión Formal

La **FASE 6 — FAULT INJECTION Y EFECTIVIDAD REAL DE DEFENSAS** queda **FORMALMENTE CERRADA Y CONCLUIDA**:
- Se demostró que ante fallas silenciosas o mentiras en el importador, el motor económico, la persistencia, las exportaciones Excel/HTML, la API o la interfaz de usuario, **las defensas ontológicas independientes de Calibre desenmascaran el defecto antes de que el resultado pueda considerarse confiable**.
- La tasa de detección P0 alcanzó el **100%**, la tasa de detección en evaluación ciega alcanzó el **100%**, y la tasa de falsos positivos en controles sanos fue de **0%**.
