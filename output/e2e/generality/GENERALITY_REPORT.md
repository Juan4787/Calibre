# INFORME DE VERIFICACIÓN: FASE 4 — GENERALIDAD DEL MOTOR SIN CÓDIGO ESPECÍFICO

**Fecha**: 2026-09-17  
**Commit base bajo prueba**: `8e308cfebd5eda2c63a61a8a69ca0a5a4be80ce1`  
**Artefacto instalado y ejecutado**: `dist/freight_audit-0.1.0-py3-none-any.whl`  
**SHA-256 del Wheel**: `9a1984547c6020029a6937f4a2479fda935d085948e092f9654f1f65bfb7562b`  
**Hash del Artefacto del Motor**: `133731f29cdf72588915f14fc5f8ab0ad0dd0945cfcdf8377cd26b1368a68638`  
**Entorno clean-room aislado**: `/tmp/calibre-e2e-generality/` (Python 3.12 venv, sin `PYTHONPATH` a `src/`)  
**Navegador automatizado**: Chromium headless vía Playwright  
**Base de datos operacional**: `/tmp/calibre-e2e-generality/db/generality_audit.db`  
**Resultado final**: **APROBADO — GATE DE FASE 4 CUMPLIDO AL 100% (6/6 ARQUETIPOS NATURALES)**  

---

## 1. Declaración Formal del Gate de Salida

> **"G1–G5 reproducen exactamente sus oráculos independientes; G6 demuestra composición; todos atraviesan la cadena productiva (archivo $\to$ mapping $\to$ importer $\to$ snapshot $\to$ engine $\to$ SQLite $\to$ API $\to$ UI $\to$ export); no se modifica producción (`0` cambios en `src/freight_audit/`); y ninguna estructura requiere lógica específica por supuesto cliente. Cada caso queda además clasificado honestamente como NATURAL, AWKWARD o UNREPRESENTABLE."**

- **Divergencias entre Oráculo Independiente y Calibre**: **0**
- **Casos que requirieron lógica o parches en `src/freight_audit/`**: **0**
- **Preprocesamiento o normalización ad-hoc en scripts de prueba**: **0**
- **Casos clasificados como `AWKWARD` o `UNREPRESENTABLE`**: **0**
- **Arquetipos clasificados como `NATURAL`**: **6 / 6 (100%)**

---

## 2. Resumen Ejecutivo de Arquetipos Evaluados

```mermaid
flowchart TD
    subgraph FASE_4["FASE 4 — Evaluación de Generalidad y Composicionalidad"]
        G1["G1: Peso + Mínimo + % Combustible<br/>✅ PASS (Oráculo 100% | NATURAL)"]
        G2["G2: OD + Vehículo + Semestre<br/>✅ PASS (Lookup + Vigencias | NATURAL)"]
        G3["G3: Pallets + Evidencia Condicional<br/>✅ PASS (Excel XLSX + Hash Doc | NATURAL)"]
        G4["G4: Bandas / Tramos USD<br/>✅ PASS ([lower, upper) Fronteras | NATURAL)"]
        G5["G5: Consolidación N:1 y 1:N<br/>✅ PASS (Group Cardinality | NATURAL)"]
        G6["G6: Composición Integrada<br/>✅ PASS (Ortogonalidad Total | NATURAL)"]
    end
```

| Caso | Estructura Contractual | Oráculo Independiente | Resultado Calibre | Modificaciones en Core | Clasificación Naturalidad |
|---|---|:---:|:---:|:---:|:---:|
| **G1** | Peso $\times$ Tarifa + Mínimo + % Combustible | **PASS** | **PASS** | `0` | **NATURAL** |
| **G2** | Origen/Destino + Tipo de Vehículo + Vigencia | **PASS** | **PASS** | `0` | **NATURAL** |
| **G3** | Pallets + Adicional Condicionado por Evidencia | **PASS** | **PASS** | `0` | **NATURAL** |
| **G4** | Tarifación por Bandas / Tramos Semiabiertos (USD) | **PASS** | **PASS** | `0` | **NATURAL** |
| **G5** | Consolidación Real de Cardinalidad (N:1 y 1:N) | **PASS** | **PASS** | `0` | **NATURAL** |
| **G6** | Composición Integrada (El Sexto Contrato) | **PASS** | **PASS** | `0` | **NATURAL** |

---

## 3. Metodología de Validación y Prerregistro (4A a 4C)

1. **Prerregistro Previo (4A)**:
   - Todas las estructuras, fórmulas matemáticas, datos de prueba y resultados esperados fueron formalizados y congelados en [GENERALITY_CASES.md](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/GENERALITY_CASES.md) antes de construir las configuraciones o mappings en Calibre.
2. **Oráculo Independiente (4B)**:
   - Implementado en [independent_oracles.py](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/independent_oracles.py).
   - **Cero importaciones del core**: No utiliza `freight_audit.engine`, `rules.py` ni helpers de producción.
   - Basado en `decimal.Decimal` y `fractions.Fraction` puros.
   - Congeló de forma autónoma los resultados en [frozen_expected.json](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/frozen_expected.json).
3. **Diversidad de Formatos Documentales de Entrada (4C)**:
   - **G1**: CSV delimitado por punto y coma (`;`), coma decimal (`,`), punto de miles (`.`), encabezados en español (`Remito_Nro`, `Peso_Facturado_Kg`), moneda `ARS`.
   - **G2**: CSV delimitado por coma (`,`), punto decimal (`.`), fechas `%Y-%m-%d`, encabezados en inglés (`shipment_code`, `truck_type`), moneda `ARS`.
   - **G3**: Hoja de cálculo binaria **Excel nativa (.XLSX)** con hojas separadas `Operaciones` y `Liquidacion`, columnas con espacios (`Nro Operacion`, `Cant Pallets`).
   - **G4**: CSV delimitado por pipe (`|`), punto decimal (`.`), moneda extranjera `USD`.
   - **G5**: CSV con estructura de consolidación de remitos bajo `Viaje_ID`, moneda `ARS`.
   - **G6**: CSV con atributos combinados y archivos de evidencia documental.

---

## 4. Detalle de Ejecución y Reconciliación por Arquetipo

### 4.1. G1 — Peso + Mínimo + Porcentaje Adicional
- **Mecanismo**: $\text{Total} = \text{round}(\max(500.00, \text{peso\_kg} \times 15.00) \times 1.085, 2)$.
- **Primitivas**: `mul`, `max`, dimensionalidad de unidades ($kg \times ARS/kg \to ARS$) y scaling porcentual.
- **Reconciliación**:
  * `CH-OP-G1-01` (120 kg): Facturado $1953.00$ | Oráculo $1953.00$ | Calibre $1953.00$ $\to$ **PASS** (Paridad 100%).
  * `CH-OP-G1-02` (20 kg, Mínimo): Facturado $570.00$ | Oráculo $542.50$ | Calibre $542.50$ (Dif: $+27.50$) $\to$ **FAIL** detectado (Paridad 100%).
  * `CH-OP-G1-03` (50 kg): Facturado $813.75$ | Oráculo $813.75$ | Calibre $813.75$ $\to$ **PASS** (Paridad 100%).

---

### 4.2. G2 — Origen/Destino + Tipo de Vehículo + Vigencia Temporal
- **Mecanismo**: Lookup multidimensional con tupla `[origen, destino, vehiculo]` y dos versiones disjuntas (Semestre 1 y Semestre 2 con $+20\%$).
- **Primitivas**: `lookup` sobre tabla de filas y selección automática de versión mediante `agreement.date_field`.
- **Reconciliación**:
  * `CH-OP-G2-01` (V1, BUE-ROS Semirremolque): Facturado $450000.00$ | Expected $450000.00$ $\to$ **PASS** (Paridad 100%).
  * `CH-OP-G2-02` (V2, BUE-ROS Semirremolque): Facturado $450000.00$ (tarifa vieja) | Expected $540000.00$ $\to$ **FAIL** (Dif: $-90000.00$) (Paridad 100%).
  * `CH-OP-G2-03` (V2, BUE-COR Chasis): Facturado $504000.00$ | Expected $504000.00$ $\to$ **PASS** (Paridad 100%).
  * `CH-OP-G2-04` (V1, BUE-MZA Furgón ausente): Expected `None` $\to$ **UNDETERMINABLE** ("La tabla 'tarifas_rutas' devolvió 0 coincidencias") (Paridad 100%).

---

### 4.3. G3 — Pallets + Adicional Condicionado por Evidencia
- **Mecanismo**: Tarifa unitaria por pallet ($pallets \times 85.00\text{ ARS}$) leída desde libro **Excel (.XLSX)** con requisito de evidencia `REMITO_FIRMA_RECEPCION` (`document_required=True`).
- **Primitivas**: Parser openpyxl con `preserve_xlsx_numbers`, `evidence_check` con hash criptográfico obligatorio.
- **Reconciliación**:
  * `CH-OP-G3-01` (24 pallets, con remito PDF firmado): Facturado $2040.00$ | Expected $2040.00$ $\to$ **PASS** (Paridad 100%).
  * `CH-OP-G3-02` (10 pallets, **sin evidencia**): Facturado $850.00$ | Expected $850.00$ $\to$ **REVIEW** ("Falta evidencia requerida: OP-G3-02: REMITO_FIRMA_RECEPCION con documento conservado") (Paridad 100%).
  * `CH-OP-G3-03` (15 pallets, con remito PDF firmado): Facturado $1500.00$ | Expected $1275.00$ $\to$ **FAIL** (Dif: $+225.00$) (Paridad 100%).

---

### 4.4. G4 — Tarifación por Bandas / Tramos (USD)
- **Mecanismo**: Tabla `band` con unidad `kg` bajo política semiabierta $[lower, upper)$ en moneda extranjera (`USD`).
- **Primitivas**: `band` con evaluación estricta de bordes superior exclusivo e inferior inclusivo.
- **Reconciliación**:
  * `CH-OP-G4-01` (50 kg, interior $[0, 100)$): Facturado $45.00$ | Expected $45.00$ $\to$ **PASS** (Paridad 100%).
  * `CH-OP-G4-02` (**Frontera exacta 100.00 kg**): Cae en Tramo 2 $[100, 500)$ $\to$ Facturado $110.00$ | Expected $110.00$ $\to$ **PASS** (Paridad 100%).
  * `CH-OP-G4-03` (**Frontera exacta 500.00 kg**): Cae en Tramo 3 $[500, 1000)$ ($240.00\text{ USD}$) pero facturó $110.00\text{ USD}$ $\to$ **FAIL** (Dif: $-130.00$) (Paridad 100%).
  * `CH-OP-G4-04` (1500 kg, tramo abierto $[1000, \infty)$): Facturado $420.00$ | Expected $420.00$ $\to$ **PASS** (Paridad 100%).

---

### 4.5. G5 — Consolidación Real de Cardinalidad Distinta (N:1 y 1:N)
- **Mecanismo**:
  * **N:1**: Tres remitos (`S-G5-01`, `S-G5-02`, `S-G5-03`) consolidados bajo `Viaje_ID = VIAJE-801` con suma agregada de peso: $(350 + 450 + 200)\text{ kg} \times 22.00\text{ ARS/kg} = 22000.00\text{ ARS}$.
  * **1:N**: Remito `S-G5-04` con dos cargos independientes facturados (`FLETE_TRAMO` por $8000.00$ y `SEGURO_CARGA` por $1200.00$).
- **Primitivas**: `cardinality: "group"`, agregación `sum(field="attributes.peso_kg")`, evaluación multiconcepto en el mismo ámbito.
- **Reconciliación**:
  * `C-G5-01` (N:1 consolidado 3 remitos): Facturado $22000.00$ | Expected $22000.00$ $\to$ **PASS** (Paridad 100%).
  * `C-G5-02` (1:N Flete): Facturado $8000.00$ | Expected $8000.00$ $\to$ **PASS** (Paridad 100%).
  * `C-G5-03` (1:N Seguro): Facturado $1200.00$ | Expected $1200.00$ $\to$ **PASS** (Paridad 100%).

---

### 4.6. G6 — Recombinación Composicional (El Sexto Contrato)
- **Mecanismo**: Contrato compuesto que combina simultáneamente:
  1. Lookup por zona y vehículo (`tarifas_zonas`).
  2. Mínimo contractual garantizado ($\max(100000.00, \text{lookup})$).
  3. Requisito de evidencia documental obligatoria (`REMITO_CONFORME`).
  4. Cambio de vigencia semestral (V1 $120000.00$, V2 $150000.00$).
- **Reconciliación**:
  * `CH-OP-G6-01` (V1, Norte-Sur Chasis, con evidencia): Facturado $120000.00$ | Expected $120000.00$ $\to$ **PASS** (Paridad 100%).
  * `CH-OP-G6-02` (V1, Norte-Sur Chasis, **sin evidencia**): Facturado $120000.00$ | Expected $120000.00$ $\to$ **REVIEW** (Evidencia obligatoria ausente) (Paridad 100%).
  * `CH-OP-G6-03` (V2, Norte-Sur Chasis, tarifa vieja): Facturado $120000.00$ | Expected $150000.00$ $\to$ **FAIL** (Dif: $-30000.00$) (Paridad 100%).

---

## 5. Medición de Naturalidad de Configuración (4F)

Se evaluó con rigor la complejidad de configuración registrada en [configuration-complexity.json](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/configuration-complexity.json):

| Caso | Reglas | Tablas | Mappings | Pasos Manuales | Expresiones Incómodas | Clasificación | Justificación Técnica |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **G1** | 1 | 0 | 2 | 0 | Ninguna | **NATURAL** | Composición aritmética directa `max(const, mul)` con álgebra de unidades dimensional nativa. |
| **G2** | 2 | 2 | 2 | 0 | Ninguna | **NATURAL** | Lookup multidimensional directo con 3 claves y vigencias gobernadas por `date_field`. |
| **G3** | 1 | 0 | 2 | 0 | Ninguna | **NATURAL** | Importación nativa de Excel XLSX y validación declarativa de evidencia `document_required`. |
| **G4** | 1 | 1 | 2 | 0 | Ninguna | **NATURAL** | Tabla de tramos nativa `band` con evaluación de fronteras $[lower, upper)$ en moneda USD. |
| **G5** | 3 | 0 | 2 | 0 | Ninguna | **NATURAL** | Agrupamiento declarativo `cardinality: "group"` con `sum()` para N:1 y multiconcepto para 1:N. |
| **G6** | 2 | 2 | 2 | 0 | Ninguna | **NATURAL** | Ortogonalidad total: las primitivas de G1 a G5 se combinan sin fricción ni ambigüedades de tipo. |

---

## 6. Verificación de Independencia del Core (4E)

Se ejecutó la verificación formal de inalterabilidad del código fuente de producción:

```bash
git diff -- src/freight_audit/
# Salida: (vacía, 0 modificaciones)

git status --short
# Salida: M docs/QA_EXECUTION.md (sólo documentación de QA)
```

- **Líneas modificadas en `src/freight_audit/`**: **0**
- **Parches condicionales (`if cliente == X`)**: **0**
- **Normalización externa oculta en arnés de pruebas**: **0**

---

## 7. Evidencias Archivadas

Todos los artefactos de la Fase 4 han sido preservados en el repositorio:
1. **Prerregistro Contractual**: [GENERALITY_CASES.md](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/GENERALITY_CASES.md)
2. **Oráculo Independiente**: [independent_oracles.py](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/independent_oracles.py)
3. **Resultados Congelados**: [frozen_expected.json](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/frozen_expected.json)
4. **Matriz Completa de Reconciliación**: [reconciliation.json](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/reconciliation.json)
5. **Métricas de Complejidad**: [configuration-complexity.json](file:///home/usuario/CascadeProjects/CALIBRE/output/e2e/generality/configuration-complexity.json)
6. **Capturas de Pantalla UI (Chromium)**:
   - `G1_overview.png`, `G2_overview.png`, `G3_overview.png`, `G4_overview.png`, `G5_overview.png`, `G6_overview.png`
7. **Paquetes y Exportaciones de Cada Caso**: Subdirectorios `G1/`, `G2/`, `G3/`, `G4/`, `G5/`, `G6-composition/`.

---

## 8. Conclusión y Veredicto Final

La **FASE 4 queda CERRADA AL 100% CON ÉXITO ABSOLUTO**.  
Se demostró fehacientemente que Freight Audit / Calibre 0.1.0 es un **motor genérico, declarativo y configurable**, capaz de resolver cinco arquetipos contractuales sustancialmente diferentes más un sexto arquetipo composicional de forma completamente `NATURAL`, sin artificios, sin normalizaciones externas y sin haber modificado una sola línea de código en `src/freight_audit/`.
