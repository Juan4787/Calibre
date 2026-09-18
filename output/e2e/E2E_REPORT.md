# INFORME DE VERIFICACIÓN: FASE 1 — E2E PRODUCTIVO REAL

**Fecha**: 2026-09-17  
**Commit bajo prueba**: `8e308cf27484439169623e10034633dfb01e389e`  
**Artefacto instalado y ejecutado**: `dist/freight_audit-0.1.0-py3-none-any.whl`  
**Entorno de ejecución**: `output/e2e/isolated_env` (venv limpio, Python 3.12, sin PYTHONPATH al repo)  
**Navegador automatizado**: Chromium headless vía Playwright  
**Base de datos operacional**: `output/e2e/e2e_audit.db` (puerto `8770`)  
**Resultado final**: **APROBADO (GATE CUMPLIDO)**  

---

## 1. Declaración Formal del Gate de Salida

> "Un wheel limpio e instalado fuera del repositorio completó una auditoría completa mediante la UI, atravesó servidor/API/persistencia/motor/reporting, sobrevivió reinicio y replay, y todas las representaciones materiales reconciliaron."

- **Divergencias económicas encontradas**: **0**
- **Divergencias de estado encontradas**: **0**
- **Divergencias de trazabilidad encontradas**: **0**
- **Modificaciones al código fuente de producción (`src/`)**: **0**

---

## 2. Escenario Sintético de 4 Estados

Se auditó un lote compuesto por 4 operaciones de transporte y 4 cargos liquidados con el acuerdo contractual `AGR-E2E` (versión `V1`):

1. **S1 / C1 (`PASS`)**:
   - Servicio: Flete estándar (10 kg × 10 ARS/kg = $100 ARS). Facturado: $100 ARS. Diferencia: $0 ARS.
   - Estado: **`PASS`** (Coincide).
2. **S2 / C2 (`FAIL`)**:
   - Servicio: Flete estándar (10 kg × 10 ARS/kg = $100 ARS). Facturado: $120 ARS. Diferencia: +$20 ARS.
   - Estado: **`FAIL`** (Discrepancia).
3. **S3 / C3 (`REVIEW`)**:
   - Servicio: Maniobra especial pactada a tarifa fija ($100 ARS), condicionada a presentar evidencia documental (`authorization`). Facturado: $100 ARS. En la Corrida 1 no se incluye el documento.
   - Estado: **`REVIEW`** (Revisión humana).
4. **S4 / C4 (`UNDETERMINABLE`)**:
   - Servicio: Flete liquidado en `USD` ($50 USD), cuando el acuerdo contractual pactado es en `ARS`. El motor activa la barrera estricta de no conversión automática de divisas.
   - Estado: **`UNDETERMINABLE`** (Indeterminado).

---

## 3. Resumen de Ejecución Playwright y Operaciones en la UI

1. **Creación de auditoría**: Ingesta de `operaciones.csv`, `cargos.csv`, asignación de mappings JSON y guardado del acuerdo contractual `AGR-E2E`. Validación previa de 4/4 filas aceptadas por archivo.
2. **Cálculo y DOM**: Visualización inmediata en el DOM del desglose de los 4 estados: `Coincide: 1`, `Discrepancia: 1`, `Revisión humana: 1`, `Indeterminado: 1`.
3. **Auditoría de hallazgos (Modal)**:
   - Inspección celda a celda de provenance original (`operaciones.csv`, hoja, fila, columna).
   - Inspección de traza de ejecución de reglas (`mul`, `attr`, `const`, `comparison`).
4. **Decisión humana**:
   - Registro en modal de C2: Acción `REJECTED`, Actor `"Auditor Senior QA"`, Motivo `"Exceso de 20 ARS rechazado en liquidación por no corresponder a tarifa pactada."`.
   - Verificación de reflejo instantáneo en la columna "Decisión humana" de la tabla.
5. **Aporte de evidencia (Corrida 2)**:
   - Aporte desde el modal de C3 del archivo `authorization.txt`.
   - Generación automática de **Corrida 2** (`45d68deb...`): el estado de C3 transiciona a `PASS` (totales en Corrida 2: 2 PASS, 1 FAIL, 0 REVIEW, 1 UNDETERMINABLE).
6. **Inmutabilidad de Corrida 1**:
   - Navegación hacia atrás a la lista de auditorías. Apertura de Corrida 1 (`8a2135a2...`).
   - Verificación de que conteos originales (1/1/1/1) y la resolución humana persistieron intactos.
7. **Replay en navegador**:
   - Ejecución del botón "Verificar reproducción".
   - Confirmación por UI: `"Reproducción idéntica. Entradas, documentos, motor y resultado verificados."`
8. **Descargas operativas**:
   - Descarga de planilla XLSX (`8a2135a2..._auditoria.xlsx`, 16 KB).
   - Descarga de reporte HTML (`8a2135a2..._reporte.html`, 2.5 KB).
   - Descarga de paquete ZIP con originales y JSON (`8a2135a2..._paquete.zip`, 23 KB).
9. **Detención y Reinicio en Frío**:
   - Terminación de proceso (`SIGTERM`).
   - Reinicio del servidor con comando operativo sobre `output/e2e/e2e_audit.db`.
   - Recarga de página en Chromium: recuperación completa de las 2 corridas, estado inmutable de Corrida 1 y decisiones humanas.
   - Ejecución de Replay post-reinicio exitosa y comprobación de identidad de archivos reexportados.

---

## 4. Reconciliación de 6 Canales

$$\text{SQLite} = \text{API} = \text{JSON} = \text{XLSX} = \text{HTML} = \text{UI}$$

### Detalle por Cargo

- **C1 (FLETE, ARS)**:
  - SQLite: PASS, Facturado 100, Esperado 100, Dif 0
  - API: PASS, Facturado 100, Esperado 100, Dif 0
  - JSON: PASS, Facturado 100, Esperado 100, Dif 0
  - XLSX: Coincide, Facturado 100, Esperado 100, Dif 0
  - HTML: Coincide, Facturado ARS 100, Esperado 100, Dif 0
  - UI: Coincide, Facturado ARS 100, Esperado 100, Dif 0
  - **Resultado: 100% RECONCILIADO**

- **C2 (FLETE, ARS)**:
  - SQLite: FAIL, Facturado 120, Esperado 100, Dif 20 | Decisión: REJECTED por Auditor Senior QA
  - API: FAIL, Facturado 120, Esperado 100, Dif 20 | Decisión: REJECTED por Auditor Senior QA
  - JSON: FAIL, Facturado 120, Esperado 100, Dif 20 | Decisión: REJECTED por Auditor Senior QA
  - XLSX: Discrepancia, Facturado 120, Esperado 100, Dif 20
  - HTML: Discrepancia, Facturado ARS 120, Esperado 100, Dif 20
  - UI: Discrepancia, Facturado ARS 120, Esperado 100, Dif 20 | Decisión: Rechazado
  - **Resultado: 100% RECONCILIADO**

- **C3 (ESPECIAL, ARS)**:
  - SQLite: REVIEW, Facturado 100, Esperado 100, Dif 0 (no confirmada)
  - API: REVIEW, Facturado 100, Esperado 100, Dif 0
  - JSON: REVIEW, Facturado 100, Esperado 100, Dif 0
  - XLSX: Revisión humana, Facturado 100, Esperado 100, Dif 0
  - HTML: Revisión humana, Facturado ARS 100, Esperado 100, Dif —
  - UI: Revisión humana, Facturado ARS 100, Esperado 100, Dif 0 (No confirmada)
  - **Resultado: 100% RECONCILIADO**

- **C4 (FLETE, USD)**:
  - SQLite: UNDETERMINABLE, Facturado 50, Esperado None, Dif None
  - API: UNDETERMINABLE, Facturado 50, Esperado None, Dif None
  - JSON: UNDETERMINABLE, Facturado 50, Esperado None, Dif None
  - XLSX: Indeterminado, Facturado 50, Esperado None, Dif None
  - HTML: Indeterminado, Facturado USD 50, Esperado —, Dif —
  - UI: Indeterminado, Facturado USD 50, Esperado —, Dif —
  - **Resultado: 100% RECONCILIADO**

### Indicadores Globales

- **Facturado Aceptado ARS**: $320,00 en todos los canales.
- **Exceso Confirmado ARS**: $20,00 en todos los canales.
- **En Revisión ARS**: $100,00 en todos los canales.
- **Facturado Aceptado USD**: $50,00 en todos los canales.
- **Indeterminado USD**: $50,00 en todos los canales.
- **Hallazgos determinables**: 2 de 4 (50% de cobertura) en todos los canales.
- **Conteos por estado**: PASS=1, FAIL=1, REVIEW=1, UNDETERMINABLE=1 en todos los canales.
