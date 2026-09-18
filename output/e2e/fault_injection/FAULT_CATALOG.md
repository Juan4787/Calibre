# Catálogo Prerregistrado de Fallos Inyectados (Fase 6A)

**Documento Normativo Previo a la Ejecución de Fault Injection**  
**Fecha de Prerregistro**: 2026-09-17  
**Commit Baseline**: `ace3425aa4c73f6a4a104971323e4bd207ecbd5c`  
**Regla de Oro**: Ningún fallo se inyecta sin estar congelado en este catálogo. La defensa debe actuar por una propiedad intrínseca e independiente, no porque el test conozca la línea mutada.

---

## 1. Resumen de Familias de Defectos (41 Vectores)

| Grupo | Capa / Dominio | Cantidad | Códigos |
|---|---|:---:|---|
| **FI-I** | Importación y normalización de datos | 6 | `FI-I01` a `FI-I06` |
| **FI-E** | Motor económico y cálculo de reglas | 12 | `FI-E01` a `FI-E12` |
| **FI-P** | Persistencia, historia y encadenamiento | 5 | `FI-P01` a `FI-P05` |
| **FI-R** | Reporting y exportaciones (XLSX, HTML) | 6 | `FI-R01` a `FI-R06` |
| **FI-A** | Capa de API HTTP / JSON | 4 | `FI-A01` a `FI-A04` |
| **FI-U** | Interfaz de usuario (DOM Chromium) | 4 | `FI-U01` a `FI-U04` |
| **FI-X** | Cross-layer y multi-capa | 4 | `FI-X01` a `FI-X04` |
| **TOTAL** | | **41** | |

---

## 2. Catálogo Detallado de Vectores Causalmente Aislados

### 2.1. Grupo FI-I: Importer Faults (6 Vectores)

#### FI-I01: Importe Mutado en +0.01
* **Severidad**: P0 (Económica material).
* **Capa atacada**: Ingestión / Snapshot (`snapshot.charges[0].amount`).
* **Mutación exacta**: Modificar el importe del cargo de `100.00` a `100.01` tras la lectura pero antes de auditar, manteniendo el raw en provenance como `"100.00"`.
* **Efecto económico esperado**: Discrepancia no justificada entre el cargo normalizado y el comprobante documental original.
* **Primera defensa esperada**: Verificador de fidelidad de provenance (`INV-22` / comprobación de `raw` vs `amount` contra hash de fuente).
* **Defensas secundarias**: Reconciliador de representaciones documentales (`qa.reconcile`).
* **Resultado seguro esperado**: El lote/corrida se declara `UNTRUSTED` por alteración silenciosa de datos respecto al archivo original.
* **Blast radius potencial**: Liquidación incorrecta por un centavo aceptada como verídica.
* **Método de inyección**: Mutación controlada del snapshot en memoria previo al cálculo.

#### FI-I02: Cambio de Signo en Importe
* **Severidad**: P0.
* **Capa atacada**: Ingestión / Normalización (`snapshot.charges[0].amount`).
* **Mutación exacta**: Invertir signo del cargo de `100.00` a `-100.00`.
* **Efecto económico esperado**: Transformación de un débito/cargo a cobrar en un crédito a favor.
* **Primera defensa esperada**: Reconciliador documental contra archivo fuente (`INV-22`).
* **Defensas secundarias**: Invariante de balance contable de liquidación (`INV-05`).
* **Resultado seguro esperado**: Rechazo del lote o marcación de inconsistencia documental grave.
* **Blast radius potencial**: Pérdida total del importe auditado y sentido económico invertido.
* **Método de inyección**: Mutación de snapshot previo al cálculo.

#### FI-I03: Moneda Mutada Post-Lectura
* **Severidad**: P0.
* **Capa atacada**: Ingestión (`snapshot.charges[0].currency`).
* **Mutación exacta**: Sustituir moneda `ARS` por `USD` en el cargo normalizado.
* **Efecto económico esperado**: Matching contra tarifa en moneda incompatible o colapso multimoneda.
* **Primera defensa esperada**: Barrera temprana de moneda en matching (`matching_rule` bloquea o envía a `UNDETERMINABLE`).
* **Defensas secundarias**: Invariante de segregación monetaria (`INV-06`).
* **Resultado seguro esperado**: Detección inmediata de incompatibilidad monetaria o inconsistencia de divisas.
* **Blast radius potencial**: Conversión implícita no autorizada o auditoría bajo tipo de cambio inexistente.
* **Método de inyección**: Alteración de divisa en snapshot.

#### FI-I04: Fecha Contractual Desplazada a Través de Frontera
* **Severidad**: P0.
* **Capa atacada**: Ingestión (`attributes.service_date`).
* **Mutación exacta**: Modificar fecha de `2026-06-30` (Vigencia 1) a `2026-07-01` (Vigencia 2).
* **Efecto económico esperado**: Selección de una tarifa y versión de acuerdo contractual errónea.
* **Primera defensa esperada**: Reconciliación documental contra hash de remito y raw de provenance (`INV-22`).
* **Defensas secundarias**: Replay verificado contra archivo origen.
* **Resultado seguro esperado**: Declaración de `UNTRUSTED` por divergencia entre fecha normalizada y documento físico.
* **Blast radius potencial**: Aplicación de tarifas desactualizadas o sobreprecios.
* **Método de inyección**: Alteración de fecha en snapshot.

#### FI-I05: Identificador de Referencia Alterado
* **Severidad**: P0.
* **Capa atacada**: Ingestión (`snapshot.charges[0].reference`).
* **Mutación exacta**: Modificar referencia de `REM-001` a `REM-002` (operación existente).
* **Efecto económico esperado**: Cargo asociado indebidamente a otra operación física.
* **Primera defensa esperada**: Reconciliación contra `raw` de provenance del archivo cargado.
* **Defensas secundarias**: Replay verificado de fuentes.
* **Resultado seguro esperado**: `UNTRUSTED` por falseamiento de identidad documental.
* **Blast radius potencial**: Asociación fraudulenta o errónea de fletes a viajes ajenos.
* **Método de inyección**: Mutación de `reference` en snapshot.

#### FI-I06: Provenance Apuntando a Coordenada Física Falsa
* **Severidad**: P1 (Auditabilidad).
* **Capa atacada**: Ingestión (`provenance.row`).
* **Mutación exacta**: Mantener valor económico correcto pero mutar `row: 2` a `row: 15`.
* **Efecto económico esperado**: Cálculo numérico idéntico pero trazabilidad judicial/auditable inválida.
* **Primera defensa esperada**: Verificador de trazabilidad física contra tabla cruda.
* **Defensas secundarias**: Auditor de provenance.
* **Resultado seguro esperado**: Alerta de procedencia espuria.
* **Blast radius potencial**: Imposibilidad de fundamentar el hallazgo ante reclamo legal al transportista.
* **Método de inyección**: Alteración de coordenada en `SourceRef`.

---

### 2.2. Grupo FI-E: Engine Faults (12 Vectores)

#### FI-E01: Invertir Signo de la Diferencia
* **Severidad**: P0.
* **Capa atacada**: Motor (`rules.py` / `audit_finding`).
* **Mutación exacta**: Calcular diferencia como `expected - actual` en lugar de `actual - expected`.
* **Efecto económico esperado**: Un sobrecobro (+20) aparece como defecto (-20).
* **Primera defensa esperada**: Invariante de signo de auditoría (`INV-07`).
* **Defensas secundarias**: Replay con oráculo independiente en Decimal.
* **Resultado seguro esperado**: Detección de incoherencia de signo entre `actual`, `expected` y `difference`.
* **Blast radius potencial**: Reclamar créditos inexistentes o perdonar sobrecobros reales.
* **Método de inyección**: Monkeypatching en copia de ejecución del motor.

#### FI-E02: Tolerancia Inclusiva Convertida en Exclusiva
* **Severidad**: P0.
* **Capa atacada**: Motor (`rules.py` / evaluación de tolerancia).
* **Mutación exacta**: Evaluar `abs(diff) < tolerance` en vez de `<= tolerance`.
* **Efecto económico esperado**: Una diferencia de exactamente $0.01$ con tolerancia $0.01$ pasa de `PASS` a `FAIL`.
* **Primera defensa esperada**: Invariante de tolerancia de frontera (`INV-07`).
* **Defensas secundarias**: Replay y mutation test M01.
* **Resultado seguro esperado**: Inconsistencia detectada entre tolerancia contratada y estado asignado.
* **Blast radius potencial**: Falsa alarma masiva en operaciones limítrofes.
* **Método de inyección**: Mutación de operador en función de tolerancia.

#### FI-E03: Confirmar Diferencia Estando en REVIEW
* **Severidad**: P0.
* **Capa atacada**: Motor / Resumen (`engine.py`).
* **Mutación exacta**: Asignar `confirmed_difference = difference` cuando `status == "REVIEW"`.
* **Efecto económico esperado**: Una diferencia tentativa no auditada se suma al neto recuperable.
* **Primera defensa esperada**: Invariante estricto `INV-08` (`require(status in ("PASS", "FAIL") or confirmed == 0)`).
* **Defensas secundarias**: Replay determinista.
* **Resultado seguro esperado**: Falla inmediata de invariante contable.
* **Blast radius potencial**: Contabilización indebida de diferencias inciertas como recupero financiero firme.
* **Método de inyección**: Mutación de resultado en memoria post-cálculo.

#### FI-E04: Confirmar Diferencia Estando en UNDETERMINABLE
* **Severidad**: P0.
* **Capa atacada**: Motor / Resumen (`engine.py`).
* **Mutación exacta**: Asignar `confirmed_difference = 100` cuando `status == "UNDETERMINABLE"`.
* **Efecto económico esperado**: Invención de recupero monetario sin tarifa determinable.
* **Primera defensa esperada**: Invariante `INV-08`.
* **Defensas secundarias**: Invariante de resumen.
* **Resultado seguro esperado**: Violación grave de invariante.
* **Blast radius potencial**: Reclamo comercial carente de sustento contractual.
* **Método de inyección**: Mutación de resultado.

#### FI-E05: Ignorar Evidencia Obligatoria
* **Severidad**: P0.
* **Capa atacada**: Motor (`rules.py`).
* **Mutación exacta**: Promover un hallazgo a `PASS` o `FAIL` cuando falta evidencia requerida en la regla.
* **Efecto económico esperado**: Aprobar un cobro de concepto condicional sin respaldo probatorio.
* **Primera defensa esperada**: Invariante de justificación documental (`INV-08` / `missing_evidence`).
* **Defensas secundarias**: Replay independiente con motor canónico.
* **Resultado seguro esperado**: Descalificación del resultado por falta de evidencia.
* **Blast radius potencial**: Pago de adicionales fraudulentos sin comprobante.
* **Método de inyección**: Bypass de chequeo de evidencia en copia de regla.

#### FI-E06: Seleccionar Primera Versión ante Superposición de Vigencias
* **Severidad**: P0.
* **Capa atacada**: Motor (`engine.py`).
* **Mutación exacta**: Si dos versiones contractuales se superponen, elegir `applicable[0]` en vez de `UNDETERMINABLE`.
* **Efecto económico esperado**: Cálculo determinista arbitrario bajo un contrato ambiguo.
* **Primera defensa esperada**: Invariante de unicidad de versión y Replay independiente.
* **Defensas secundarias**: Mutation test M04.
* **Resultado seguro esperado**: Detección de ambigüedad contractual no resuelta.
* **Blast radius potencial**: Auditoría ejecutada con tarifa no pactada.
* **Método de inyección**: Reemplazo de lógica de conflicto de versiones.

#### FI-E07: Seleccionar Primera Regla ante Conflicto de Reglas
* **Severidad**: P0.
* **Capa atacada**: Motor (`engine.py`).
* **Mutación exacta**: Elegir primera regla ante reglas múltiples aplicables para el mismo concepto.
* **Efecto económico esperado**: Regla arbitraria aplicada sin base de precedencia.
* **Primera defensa esperada**: Replay y chequeo de ambigüedad de reglas.
* **Defensas secundarias**: Invariante de completitud.
* **Resultado seguro esperado**: Detección de resolución espuria de ambigüedad.
* **Blast radius potencial**: Fallo de consistencia y litigiosidad con transportistas.
* **Método de inyección**: Mutación de matching de reglas.

#### FI-E08: Asignar Primer Candidato ante Matching Ambiguo
* **Severidad**: P0.
* **Capa atacada**: Motor (`engine.py`).
* **Mutación exacta**: Asignar el primer remito si hay 2 candidatos en lugar de marcar `REVIEW`.
* **Efecto económico esperado**: Certeza artificial en asociación de fletes.
* **Primera defensa esperada**: Invariante de matching y Replay.
* **Defensas secundarias**: Reconciliación cruzada.
* **Resultado seguro esperado**: Detección de colapso de incertidumbre.
* **Blast radius potencial**: Flete asignado a operación equivocada.
* **Método de inyección**: Mutación de rama de candidatos múltiples.

#### FI-E09: Mezclar Monedas en el Resumen
* **Severidad**: P0.
* **Capa atacada**: Motor (`engine.py` / `summarize`).
* **Mutación exacta**: Sumar $100\text{ ARS} + 50\text{ USD} = 150$ en el resumen consolidado.
* **Efecto económico esperado**: Suma adimensional inválida de divisas.
* **Primera defensa esperada**: Invariante de segregación por divisa (`INV-06`).
* **Defensas secundarias**: Reconciliador de resumen (`qa.reconcile`).
* **Resultado seguro esperado**: Error fatal por suma multimoneda.
* **Blast radius potencial**: Destrucción total de la contabilidad de la auditoría.
* **Método de inyección**: Mutación del acumulador de resumen.

#### FI-E10: Pérdida Silenciosa de un Cargo en Findings
* **Severidad**: P0.
* **Capa atacada**: Motor (`engine.py`).
* **Mutación exacta**: Omitir un cargo en la lista de findings de salida ($N \to N-1$).
* **Efecto económico esperado**: Cargo flete facturado no auditado ni reportado.
* **Primera defensa esperada**: Invariante de conservación de cargos (`INV-04` / `charge_counts`).
* **Defensas secundarias**: Reconciliador de filas en exportaciones.
* **Resultado seguro esperado**: Detección inmediata de cargo huérfano omitido.
* **Blast radius potencial**: Cargos sin auditar pagados ciegamente.
* **Método de inyección**: Eliminación de finding en resultado.

#### FI-E11: Duplicación de un Cargo en Findings
* **Severidad**: P0.
* **Capa atacada**: Motor (`engine.py`).
* **Mutación exacta**: Generar 2 findings para el mismo cargo ID.
* **Efecto económico esperado**: Doble auditoría y doble cómputo de diferencias.
* **Primera defensa esperada**: Invariante de unicidad de cargos en findings (`INV-04`).
* **Defensas secundarias**: Verificador de clave primaria en SQLite.
* **Resultado seguro esperado**: Rechazo por clave o ID repetido.
* **Blast radius potencial**: Duplicación artificial de recuperos calculados.
* **Método de inyección**: Inserción de finding duplicado.

#### FI-E12: Redondeo Prematuro de Sumandos
* **Severidad**: P0.
* **Capa atacada**: Motor (`rules.py`).
* **Mutación exacta**: Redondear cada componente antes de sumar en vez de redondear la suma final.
* **Efecto económico esperado**: Desvío de centavos en liquidaciones complejas ($0.005 + 0.005 \to 0.01 + 0.01 = 0.02$).
* **Primera defensa esperada**: Replay con oráculo en números racionales (`Fraction`) y Decimal de alta precisión.
* **Defensas secundarias**: Invariante `INV-07`.
* **Resultado seguro esperado**: Discrepancia detectada en precisión de centavos.
* **Blast radius potencial**: Fuga acumulada de centavos en grandes volúmenes.
* **Método de inyección**: Alteración de orden de redondeo en regla.

---

### 2.3. Grupo FI-P: Persistence Faults (5 Vectores)

#### FI-P01: Sustituir Result por el de Otra Corrida
* **Severidad**: P0.
* **Capa atacada**: Persistencia / Almacenamiento (`storage.py` / `audit.json`).
* **Mutación exacta**: Guardar el `result` de la Corrida B bajo el `snapshot` de la Corrida A.
* **Efecto económico esperado**: Corrida aparentemente válida que responde a datos de otro lote.
* **Primera defensa esperada**: `verify_run` / `integrity_errors` (`INV-28`: `result_hash` no coincide con el contenido).
* **Defensas secundarias**: Replay determinista recalcula sobre snapshot y detecta discordancia.
* **Resultado seguro esperado**: Rechazo de integridad criptográfica.
* **Blast radius potencial**: Presentación de resultados cruzados a clientes distintos.
* **Método de inyección**: Modificación de archivo `audit.json` en disco.

#### FI-P02: Decisión Humana Vinculada a Finding Incorrecto
* **Severidad**: P1 (Auditabilidad / Integridad de gobierno).
* **Justificación de Severidad**: El cálculo numérico de la corrida permanece correcto pero la decisión humana queda huérfana al referenciar un finding inexistente.
* **Capa atacada**: Persistencia (`decisions` en `run`).
* **Mutación exacta**: Vincular decisión de `C2` al finding `C1`.
* **Efecto económico esperado**: Aprobación o rechazo aplicado al flete equivocado en el historial.
* **Primera defensa esperada**: Validador de consistencia de finding en decisiones humanas (`INV-24`).
* **Defensas secundarias**: Reconciliación cruzada de decisiones (`qa.reconcile`).
* **Resultado seguro esperado**: Inconsistencia detectada en ID de finding objetivo.
* **Blast radius potencial**: Impacto contable erróneo en transportista.
* **Método de inyección**: Mutación de payload de decisión en SQLite / JSON.

#### FI-P03: Orden Alterado en Cadena de Decisiones
* **Severidad**: P1 (Integridad histórica secuencial).
* **Justificación de Severidad**: No altera los saldos numéricos directos pero destruye la verificabilidad criptográfica secuencial de la cadena de decisiones.
* **Capa atacada**: Persistencia (`decisions` chain).
* **Mutación exacta**: Intercambiar el orden de dos decisiones en la lista o alterar `seq`.
* **Efecto económico esperado**: Alteración de la línea temporal auditable.
* **Primera defensa esperada**: Invariante de cadena criptográfica `INV-24` (`previous_hash`).
* **Defensas secundarias**: `storage.verify_run`.
* **Resultado seguro esperado**: Quiebre de cadena de custodia detectado.
* **Blast radius potencial**: Manipulación retroactiva de resoluciones de auditoría.
* **Método de inyección**: Permutación de registros de decisiones.

#### FI-P04: Falsificación de Artifact Hash en DB
* **Severidad**: P1 (Integridad de proveniencia del ejecutable).
* **Justificación de Severidad**: No modifica importes pero falsifica el digest SHA-256 de identidad del motor que produjo el cálculo.
* **Capa atacada**: Persistencia (`runs.artifact_hash` en SQLite).
* **Mutación exacta**: Cambiar el `artifact_hash` por un hash inventado sin alterar el archivo físico.
* **Efecto económico esperado**: Desconexión entre base de datos y archivo exportado.
* **Primera defensa esperada**: `integrity_errors` (`INV-28`) y verificación de run ID.
* **Defensas secundarias**: Verificador de bundle `manifest.json`.
* **Resultado seguro esperado**: Alerta de alteración de base de datos.
* **Blast radius potencial**: Pérdida de reproducibilidad forense.
* **Método de inyección**: UPDATE directo en tabla SQLite.

#### FI-P05: Eliminación de Documento Original en Sources
* **Severidad**: P1 (Integridad de repositorio de fuentes).
* **Justificación de Severidad**: Los resultados económicos persisten intactos pero la evidencia documental original es eliminada del bundle.
* **Capa atacada**: Almacenamiento documental (`sources/` directory).
* **Mutación exacta**: Borrar uno de los archivos fuente referenciados en snapshot.
* **Efecto económico esperado**: Snapshot afirma auditar fuentes que ya no existen.
* **Primera defensa esperada**: Invariante `INV-22` (`original source missing or altered`).
* **Defensas secundarias**: Reconciliador de bundles (`reconcile`).
* **Resultado seguro esperado**: Error `INV-22` antes de aceptar el paquete.
* **Blast radius potencial**: Imposibilidad de re-auditoría o exhibición de prueba.
* **Método de inyección**: Eliminación de archivo en directorio `sources/`.

---

### 2.4. Grupo FI-R: Reporting y Export Faults (6 Vectores)

#### FI-R01: REVIEW Convertido en PASS Exclusivamente en XLSX
* **Severidad**: P0.
* **Capa atacada**: Exportación (`auditoria.xlsx`).
* **Mutación exacta**: Cambiar texto de estado a "Coincide" en la celda de la hoja `Hallazgos` del XLSX.
* **Efecto económico esperado**: El usuario ve un cobro aprobado que el motor dejó pendiente de revisión.
* **Primera defensa esperada**: Reconciliador de representaciones (`qa.reconcile`: `INV-23 XLSX Hallazgos: material rows differ`).
* **Defensas secundarias**: Manifest checksum check.
* **Resultado seguro esperado**: Discrepancia detectada entre XLSX y `audit.json`.
* **Blast radius potencial**: Pago de conceptos no autorizados por confiar en el Excel exportado.
* **Método de inyección**: Modificación directa de celdas en el archivo XLSX exportado.

#### FI-R02: UNDETERMINABLE Convertido en FAIL en Reporte HTML
* **Severidad**: P0.
* **Capa atacada**: Exportación (`reporte.html`).
* **Mutación exacta**: Modificar el badge HTML a "Discrepancia" con importe inventado.
* **Efecto económico esperado**: Un flete indeterminado se muestra como reclamo monetario en el reporte HTML.
* **Primera defensa esperada**: Reconciliador HTML (`qa.reconcile`: Tables parser detecta divergencia material).
* **Defensas secundarias**: Manifest checksum mismatch.
* **Resultado seguro esperado**: Descalificación del reporte HTML.
* **Blast radius potencial**: Emisión de reportes falsos a clientes.
* **Método de inyección**: Reemplazo de texto en HTML exportado.

#### FI-R03: Importe de Diferencia Alterado en XLSX
* **Severidad**: P0.
* **Capa atacada**: Exportación (`auditoria.xlsx`).
* **Mutación exacta**: Cambiar valor numérico de diferencia de `20.00` a `200.00` en columna de diferencia.
* **Efecto económico esperado**: El export muestra un monto de reclamo 10 veces mayor.
* **Primera defensa esperada**: Reconciliador XLSX (`INV-23: material rows differ`).
* **Defensas secundarias**: Manifest check.
* **Resultado seguro esperado**: Detección de corrupción en fila material.
* **Blast radius potencial**: Débito indebido al transportista por reporte corrupto.
* **Método de inyección**: Modificación de celda en XLSX.

#### FI-R04: Fila de Finding Omitida en Exportación XLSX
* **Severidad**: P0.
* **Capa atacada**: Exportación (`auditoria.xlsx`).
* **Mutación exacta**: Borrar una fila de hallazgo en la hoja `Hallazgos`.
* **Efecto económico esperado**: Un sobrecobro desaparece de la vista del cliente.
* **Primera defensa esperada**: Reconciliador de filas XLSX (`INV-23: material rows differ`).
* **Defensas secundarias**: Resumen del XLSX no balancea con hoja Hallazgos.
* **Resultado seguro esperado**: Detección de pérdida de fila.
* **Blast radius potencial**: Ocultamiento de irregularidades en auditoría.
* **Método de inyección**: Eliminación de fila en workbook.

#### FI-R05: Moneda Mutada en Reporte HTML
* **Severidad**: P0.
* **Capa atacada**: Exportación (`reporte.html`).
* **Mutación exacta**: Cambiar `USD` por `ARS` en tabla HTML.
* **Efecto económico esperado**: Un cargo en dólares parece estar expresado en pesos.
* **Primera defensa esperada**: Reconciliador HTML contra `audit.json`.
* **Defensas secundarias**: Manifest checksum.
* **Resultado seguro esperado**: Discrepancia de columnas en HTML detectada.
* **Blast radius potencial**: Error cambiario masivo.
* **Método de inyección**: Reemplazo en string HTML.

#### FI-R06: Eliminación de Reasons / Missing Evidence en XLSX
* **Severidad**: P1 (Explicabilidad / Metadata de auditoría).
* **Justificación de Severidad**: Conserva el estado REVIEW y los importes correctos pero elimina la justificación causal y evidencia ausente del reporte Excel.
* **Capa atacada**: Exportación (`auditoria.xlsx`).
* **Mutación exacta**: Dejar vacía la celda de motivos en un finding de `REVIEW`.
* **Efecto económico esperado**: Operador no sabe por qué el flete está en revisión.
* **Primera defensa esperada**: Reconciliador XLSX (`INV-23: material rows differ`).
* **Defensas secundarias**: Auditor de completitud.
* **Resultado seguro esperado**: Detección de pérdida de metadata explicativa.
* **Blast radius potencial**: Bloqueo operacional de resolución humana.
* **Método de inyección**: Vaciado de celda en XLSX.

---

### 2.5. Grupo FI-A: API Faults (4 Vectores)

#### FI-A01: API Devuelve Estado Divergente al de SQLite
* **Severidad**: P0.
* **Justificación de Severidad**: La API devuelve estado de conformidad (PASS) para un hallazgo que en base de datos es FAIL.
* **Capa atacada**: API HTTP (`/api/audits/{id}`).
* **Mutación exacta**: Modificar respuesta JSON interceptada para cambiar `REVIEW` por `PASS`.
* **Efecto económico esperado**: Clientes API reciben confirmación falsa de un flete incierto.
* **Primera defensa esperada**: Cross-check API vs DB snapshot (`test_qa_infrastructure` / reconciliador API).
* **Defensas secundarias**: Inconsistencia de hash de respuesta.
* **Resultado seguro esperado**: Discrepancia API vs Core detectada.
* **Blast radius potencial**: Integraciones de pago automáticas liquidan sin revisión.
* **Método de inyección**: Middleware / Mock de interceptación HTTP.

#### FI-A02: API Omite un Finding en la Colección
* **Severidad**: P0.
* **Justificación de Severidad**: La API omite un hallazgo en la respuesta JSON, entregando saldos y conteos incompletos.
* **Capa atacada**: API HTTP (`/api/audits/{id}`).
* **Mutación exacta**: Omitir un finding en el array `findings` devuelto por el endpoint.
* **Efecto económico esperado**: Front-end o sistema ERP pierde visibilidad de un cargo.
* **Primera defensa esperada**: Reconciliador de cardinalidad de respuesta API.
* **Defensas secundarias**: Hash de payload API no coincide con `result_hash`.
* **Resultado seguro esperado**: Detección de pérdida de finding en capa de transporte.
* **Blast radius potencial**: Fletes omitidos en interfases downstream.
* **Método de inyección**: Interceptación de response JSON.

#### FI-A03: API Altera un Centavo en el Importe
* **Severidad**: P0.
* **Justificación de Severidad**: La API altera el importe auditado (actual) en el payload JSON consumido por integradores.
* **Capa atacada**: API HTTP (`/api/audits/{id}`).
* **Mutación exacta**: Cambiar `amount: "100.00"` a `"100.01"` en la respuesta JSON.
* **Efecto económico esperado**: Importe no reconciliable con la base transaccional.
* **Primera defensa esperada**: Reconciliador de payload API contra hash de base de datos.
* **Defensas secundarias**: Checksum de respuesta.
* **Resultado seguro esperado**: Detección de alteración de centavos en tránsito.
* **Blast radius potencial**: Fricción de reconciliación bancaria.
* **Método de inyección**: Interceptación de payload HTTP.

#### FI-A04: API Omite Metadatos de Provenance
* **Severidad**: P1 (Trazabilidad documental).
* **Justificación de Severidad**: La API entrega importes y estados correctos pero suprime la trazabilidad documental hacia las fuentes.
* **Capa atacada**: API HTTP (`/api/audits/{id}`).
* **Mutación exacta**: Omitir diccionario `provenance` en las operaciones devueltas.
* **Efecto económico esperado**: Pérdida de vínculo celda a celda en UI.
* **Primera defensa esperada**: Validador Pydantic del esquema de respuesta de la API.
* **Defensas secundarias**: Auditor Playwright de provenance en modal.
* **Resultado seguro esperado**: Rechazo de contrato de API por campo faltante.
* **Blast radius potencial**: Degeneración del sistema a "caja negra".
* **Método de inyección**: Strip de `provenance` en response.

---

### 2.6. Grupo FI-U: UI Faults (4 Vectores)

#### FI-U01: DOM Muestra "Coincide" cuando API Reporta "Revisión humana"
* **Severidad**: P0.
* **Justificación de Severidad**: El DOM de la interfaz muestra 'Coincide' para un hallazgo en REVIEW, engañando al operador humano.
* **Capa atacada**: UI (Renderizado DOM JavaScript).
* **Mutación exacta**: Inyectar mutación en el DOM para que el badge de estado muestre `Coincide` en un finding en `REVIEW`.
* **Efecto económico esperado**: El operador humano ve el flete como aprobado en pantalla.
* **Primera defensa esperada**: Auditor E2E Playwright de reconciliación DOM vs API (`reconcile(directory, observed_ui=ui_capture)`).
* **Defensas secundarias**: Captura y contraste visual de badges.
* **Resultado seguro esperado**: `reconcile` detecta divergencia entre DOM y API.
* **Blast radius potencial**: Decisión errónea tomada por operador humano basada en pantalla falsa.
* **Método de inyección**: Mutación de elemento DOM vía Playwright `evaluate`.

#### FI-U02: DOM Muestra Importe de Diferencia Truncado (+20 a +2)
* **Severidad**: P0.
* **Justificación de Severidad**: El DOM muestra una diferencia distorsionada (+2,00 en vez de +20,00), engañando sobre el recupero.
* **Capa atacada**: UI (Formateo de moneda).
* **Mutación exacta**: Modificar texto de diferencia en tabla DOM de `20` a `2`.
* **Efecto económico esperado**: Operador ve una discrepancia diez veces menor a la real.
* **Primera defensa esperada**: Auditor Playwright DOM vs API (`observed_ui` reconciliation).
* **Defensas secundarias**: Suma de tarjetas macro de statusline no coincide con la tabla.
* **Resultado seguro esperado**: Detección de discrepancia material de interfaz.
* **Blast radius potencial**: Minimización engañosa de desvíos económicos.
* **Método de inyección**: Mutación de texto de celda en DOM.

#### FI-U03: DOM Muestra Moneda Errónea (USD a ARS)
* **Severidad**: P0.
* **Justificación de Severidad**: El DOM muestra símbolo de moneda USD en vez de ARS para importes en moneda local.
* **Capa atacada**: UI (Etiqueta de divisa).
* **Mutación exacta**: Cambiar texto `USD` a `ARS` en el modal de detalle del finding.
* **Efecto económico esperado**: Confusión de divisa en la resolución de discrepancia.
* **Primera defensa esperada**: Verificador Playwright de coherencia monetaria en modal.
* **Defensas secundarias**: Reconciliador de interfaz.
* **Resultado seguro esperado**: Detección de incoherencia de moneda en UI.
* **Blast radius potencial**: Emisión de notas de crédito en moneda equivocada.
* **Método de inyección**: Mutación de selector en modal.

#### FI-U04: Ocultamiento del Banner de Importación Incompleta
* **Severidad**: P1 (Contexto de certeza operacional).
* **Justificación de Severidad**: Los datos numéricos coinciden pero el DOM omite la advertencia visual de importación incompleta.
* **Capa atacada**: UI (Alerta de certeza).
* **Mutación exacta**: Eliminar del DOM el banner que notifica filas rechazadas en la importación.
* **Efecto económico esperado**: El operador asume que el lote auditado estaba 100% completo cuando faltan operaciones.
* **Primera defensa esperada**: Verificador Playwright de presencia de advertencias de incertidumbre.
* **Defensas secundarias**: Reconciliador de conteo de filas importadas vs rechazadas.
* **Resultado seguro esperado**: Detección de omisión de advertencia crítica de contexto.
* **Blast radius potencial**: Auditoría parcial tomada erróneamente como completa.
* **Método de inyección**: Eliminación de nodo DOM de aviso de importación.

---

### 2.7. Grupo FI-X: Cross-Layer y Combinados (4 Vectores)

#### FI-X01: Falsificación Simultánea en DB y XLSX con Result Hash Recalculado
* **Severidad**: P0.
* **Capa atacada**: Multi-capa (Persistencia + Exportación).
* **Mutación exacta**: Alterar un finding en DB y XLSX, recalculando el SHA-256 de `result` para engañar a `verify_run`, pero manteniendo el `snapshot` original intacto.
* **Efecto económico esperado**: Corrupción sofisticada que burla verificadores triviales de hash.
* **Primera defensa esperada**: **Replay Determinista Independiente**: re-ejecuta el motor sobre el snapshot y descubre que el resultado almacenado no puede ser derivado de las entradas originales.
* **Defensas secundarias**: Desajuste entre `run_id` y componentes criptográficos.
* **Resultado seguro esperado**: Detección categórica por replay independiente.
* **Blast radius potencial**: Manipulación interna de bases de datos por actores maliciosos.
* **Método de inyección**: Recálculo artificial de hash sobre payload mutado.

#### FI-X02: Modificación Posterior de Regla Contractual en Base de Datos
* **Severidad**: P0.
* **Capa atacada**: Multi-capa (Acuerdo en DB vs Snapshot).
* **Mutación exacta**: Alterar la tarifa en la tabla `agreements` de SQLite después de auditada la corrida.
* **Efecto económico esperado**: Desajuste entre lo que el sistema dice haber aplicado y la regla vigente en base.
* **Primera defensa esperada**: Snapshot Inmutability Check (`snapshot.agreements` conserva la regla original sellada).
* **Defensas secundarias**: Replay detecta discrepancia si intentara leer fuera del snapshot.
* **Resultado seguro esperado**: El sistema mantiene intacta la verdad histórica del snapshot congelado.
* **Blast radius potencial**: Contratos editados retroactivamente alterando auditorías pasadas.
* **Método de inyección**: UPDATE directo en tabla `agreements`.

#### FI-X03: Alteración de Metadata de Redondeo en Runtime
* **Severidad**: P0.
* **Capa atacada**: Configuración / Engine (`agreement.rounding`).
* **Mutación exacta**: Sustituir `ROUND_HALF_EVEN` por `ROUND_HALF_UP` en el acuerdo en runtime.
* **Efecto económico esperado**: Desvío sistemático de centavos en la liquidación.
* **Primera defensa esperada**: Replay y Reconciliador con oráculo racional (`Fraction`).
* **Defensas secundarias**: Mutation test M12.
* **Resultado seguro esperado**: Detección de cambio no contractual de redondeo.
* **Blast radius potencial**: Pérdida acumulada en miles de fletes.
* **Método de inyección**: Alteración de atributo en memoria.

#### FI-X04: Desfase Temporal en created_at Rompiendo Orden Causal
* **Severidad**: P1.
* **Capa atacada**: Persistencia (`created_at` timestamp).
* **Mutación exacta**: Registrar una decisión con fecha anterior a la creación de la corrida (`decision.created_at < run.created_at`).
* **Efecto económico esperado**: Anacronismo causal en la línea de tiempo.
* **Primera defensa esperada**: Invariante de monotonicidad temporal causal.
* **Defensas secundarias**: Auditor de bitácora transaccional.
* **Resultado seguro esperado**: Rechazo por violación de flecha temporal.
* **Blast radius potencial**: Destrucción de la validez legal y pericial del informe.
* **Método de inyección**: Timestamp falsificado en payload.

---

## 3. Criterio de Evaluación y Gate de Fase 6

1. **P0 Detection Rate**: **100%**. Ningún defecto P0 puede quedar en estado `SURVIVED`.
2. **P1/P2 Tolerance**: Todo P1/P2 sobreviviente debe quedar aislado con su blast radius y ticket de incidente asociado.
3. **Control de Falsos Positivos**: Los 12 controles negativos sanos deben dar `TRUSTED` (0% de falsos positivos).
4. **Independencia Demostrada**: En la matriz final, los detectores deben haber actuado por violaciones de contratos e invariantes, no por nombres de variables ni números de línea.
