# ESPECIFICACIÓN FORMAL DE CONTRATOS (PRERREGISTRO): FASE 4

**Fecha de congelamiento**: 2026-09-17  
**Fase**: 4A — Prerregistro Previo de Contratos y Oráculos Independientes  
**Commit base**: `8e308cfebd5eda2c63a61a8a69ca0a5a4be80ce1`  
**Regla estricta**: Los oráculos matemáticos independientes y los resultados esperados aquí declarados fueron congelados **antes** de construir las configuraciones, mappings o datasets en Calibre. Prohibido adaptar retroactivamente las reglas a lo que el motor resuelva de forma simple.

---

## 1. G1 — Peso + Mínimo Garantizado + Porcentaje Adicional

### 1.1. Estructura Contractual
- **Transportista**: `EXPRESS-CARGO`
- **Moneda**: `ARS` (escala: 2, redondeo: `ROUND_HALF_EVEN`)
- **Tolerancia**: Absoluta `0.05 ARS`, Relativa `0.001`
- **Vigencia**: `2026-01-01` a `2026-12-31`
- **Regla económica**:
  * Tarifa por kilogramo: $15.00\text{ ARS/kg}$
  * Mínimo contractual garantizado: $500.00\text{ ARS}$
  * Base imponible: $\text{Base} = \max(500.00, \text{peso\_kg} \times 15.00)$
  * Adicional de combustible: $+8.5\%$ sobre la base imponible
  * Total a facturar: $\text{Total} = \text{round}(\text{Base} \times 1.085, 2)$

### 1.2. Datos de Entrada y Fórmulas del Oráculo Independiente

| Operación | Fecha | Peso (kg) | Fórmula del Oráculo Independiente | Expected Exacto | Facturado | Estado Esperado | Causa del Resultado |
|---|:---:|:---:|---|:---:|:---:|:---:|---|
| `OP-G1-01` | `2026-02-10` | 120.00 | $\max(500, 120 \times 15) \times 1.085 = 1800 \times 1.085 = 1953.00$ | **1953.00 ARS** | 1953.00 ARS | **PASS** | Cálculo exacto coincide |
| `OP-G1-02` | `2026-02-15` | 20.00 | $\max(500, 20 \times 15) \times 1.085 = 500 \times 1.085 = 542.50$ | **542.50 ARS** | 570.00 ARS | **FAIL** | Sobrecargo de $+27.50$ ARS |
| `OP-G1-03` | `2026-03-01` | 50.00 | $\max(500, 50 \times 15) \times 1.085 = 750 \times 1.085 = 813.75$ | **813.75 ARS** | 813.75 ARS | **PASS** | Cálculo exacto coincide |

### 1.3. Representación Documental y Primitivas Previstas
- **Formato documental**: CSV delimitado por `;`, decimal con coma (`,`), miles con punto (`.`), nombres de columnas en español (`Remito_Nro`, `Fecha_Despacho`, `Peso_Facturado_Kg`).
- **Matching**: `cardinality: "one"`, clave `reference` $\leftrightarrow$ `reference`.
- **Primitivas de Calibre**: `mul`, `max`, `add` o `mul(..., 1.085)`, dimensionalidad de unidades ($kg \times ARS/kg \to ARS$).

---

## 2. G2 — Origen/Destino + Tipo de Vehículo + Vigencia Temporal

### 2.1. Estructura Contractual
- **Transportista**: `LOGISTICA-TRUCK`
- **Moneda**: `ARS` (escala: 2, redondeo: `ROUND_HALF_EVEN`)
- **Vigencia Semestral**:
  * Versión 1 (`V1-SEM1`): `2026-01-01` a `2026-06-30`
  * Versión 2 (`V2-SEM2`): `2026-07-01` a `2026-12-31` (incremento paritario del $+20\%$)
- **Tabla de Búsqueda Multidimensional (`lookup`)**:
  * Claves: `(origen, destino, tipo_vehiculo)`
  * Valores V1:
    - `(BUE, ROS, SEMIRREMOLQUE)` $\to 450000.00\text{ ARS}$
    - `(BUE, ROS, CHASIS)` $\to 280000.00\text{ ARS}$
    - `(BUE, COR, SEMIRREMOLQUE)` $\to 680000.00\text{ ARS}$
    - `(BUE, COR, CHASIS)` $\to 420000.00\text{ ARS}$
  * Valores V2 (+20%):
    - `(BUE, ROS, SEMIRREMOLQUE)` $\to 540000.00\text{ ARS}$
    - `(BUE, ROS, CHASIS)` $\to 336000.00\text{ ARS}$
    - `(BUE, COR, SEMIRREMOLQUE)` $\to 816000.00\text{ ARS}$
    - `(BUE, COR, CHASIS)` $\to 504000.00\text{ ARS}$

### 2.2. Datos de Entrada y Fórmulas del Oráculo Independiente

| Operación | Fecha | Ruta y Vehículo | Versión | Expected Exacto | Facturado | Estado Esperado | Causa del Resultado |
|---|:---:|---|:---:|:---:|:---:|:---:|---|
| `OP-G2-01` | `2026-03-15` | `BUE` $\to$ `ROS`, Semirremolque | V1 | **450000.00 ARS** | 450000.00 ARS | **PASS** | Lookup exacto en V1 |
| `OP-G2-02` | `2026-08-20` | `BUE` $\to$ `ROS`, Semirremolque | V2 | **540000.00 ARS** | 450000.00 ARS | **FAIL** | Facturó tarifa vieja V1 (defecto $-90000.00$) |
| `OP-G2-03` | `2026-09-10` | `BUE` $\to$ `COR`, Chasis | V2 | **504000.00 ARS** | 504000.00 ARS | **PASS** | Lookup exacto en V2 |
| `OP-G2-04` | `2026-04-10` | `BUE` $\to$ `MZA`, Furgón | V1 | *No existe en tabla* | 350000.00 ARS | **UNDETERMINABLE** | Sin coincidencia en tabla de búsqueda |

### 2.3. Representación Documental y Primitivas Previstas
- **Formato documental**: CSV delimitado por coma (`,`), decimal con punto (`.`), fecha `%Y-%m-%d`, encabezados en inglés (`shipment_code,dispatch_date,origin_code,destination_code,truck_type`).
- **Primitivas de Calibre**: `lookup` multidimensional sobre tabla de filas, selección automática de versión gobernada por `agreement.date_field`.

---

## 3. G3 — Pallets + Adicional Condicionado por Evidencia

### 3.1. Estructura Contractual
- **Transportista**: `PALLET-DISTRIB`
- **Moneda**: `ARS` (escala: 2, redondeo: `ROUND_HALF_EVEN`)
- **Vigencia**: `2026-01-01` a `2026-12-31`
- **Regla económica y de respaldo**:
  * Tarifa unitaria por pallet: $85.00\text{ ARS/pallet}$
  * Fórmula base: $\text{Total} = \text{pallets} \times 85.00\text{ ARS}$
  * Requisito de evidencia documental obligatoria: Constancia de entrega firmada (`REMITO_FIRMA_RECEPCION`) con documento original registrado y verificado (`document_required=True`).

### 3.2. Datos de Entrada y Fórmulas del Oráculo Independiente

| Operación | Fecha | Pallets | Evidencia Aportada | Expected Numérico | Facturado | Estado Esperado | Causa del Resultado |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `OP-G3-01` | `2026-04-05` | 24 | Remito firmado presente con hash | **2040.00 ARS** | 2040.00 ARS | **PASS** | Cálculo y evidencia conformes |
| `OP-G3-02` | `2026-04-12` | 10 | **Ninguna (ausente)** | **850.00 ARS** | 850.00 ARS | **REVIEW** | Falta evidencia obligatoria |
| `OP-G3-03` | `2026-04-18` | 15 | Remito firmado presente con hash | **1275.00 ARS** | 1500.00 ARS | **FAIL** | Sobrecargo de $+225.00$ ARS |

### 3.3. Representación Documental y Primitivas Previstas
- **Formato documental**: Libro **Excel binario nativo (.XLSX)** con hojas separadas `Operaciones` y `Liquidacion`. Encabezados con espacios (`Nro Operacion`, `Fecha Servicio`, `Cant Pallets`, `Cliente Destino`).
- **Primitivas de Calibre**: `mul` de atributo con unidad (`pallet` $\times$ `ARS/pallet` $\to$ `ARS`), regla con `evidence: [Requirement(any_of=["REMITO_FIRMA_RECEPCION"], document_required=True)]`.

---

## 4. G4 — Tarifación por Bandas/Tramos (USD)

### 4.1. Estructura Contractual
- **Transportista**: `GLOBAL-CARGO-INTL`
- **Moneda**: `USD` (escala: 2, redondeo: `ROUND_HALF_EVEN`)
- **Vigencia**: `2026-01-01` a `2026-12-31`
- **Tabla de Tramos / Bandas (`band`, unidad `kg`)**:
  Política contractual semiabierta $[lower, upper)$:
  * Tramo 1: $[0.00, 100.00) \to 45.00\text{ USD}$
  * Tramo 2: $[100.00, 500.00) \to 110.00\text{ USD}$
  * Tramo 3: $[500.00, 1000.00) \to 240.00\text{ USD}$
  * Tramo 4: $[1000.00, \infty) \to 420.00\text{ USD}$

### 4.2. Datos de Entrada y Fórmulas del Oráculo Independiente

| Operación | Fecha | Peso (kg) | Tramo Aplicable | Expected Exacto | Facturado | Estado Esperado | Causa del Resultado |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `OP-G4-01` | `2026-05-02` | 50.00 | $[0, 100)$ | **45.00 USD** | 45.00 USD | **PASS** | Punto interior de Tramo 1 |
| `OP-G4-02` | `2026-05-10` | 100.00 | $[100, 500)$ | **110.00 USD** | 110.00 USD | **PASS** | **Frontera exacta**: cae en Tramo 2 |
| `OP-G4-03` | `2026-05-15` | 500.00 | $[500, 1000)$ | **240.00 USD** | 110.00 USD | **FAIL** | **Frontera exacta**: facturó tramo anterior |
| `OP-G4-04` | `2026-05-20` | 1500.00 | $[1000, \infty)$ | **420.00 USD** | 420.00 USD | **PASS** | Tramo superior abierto |

### 4.3. Representación Documental y Primitivas Previstas
- **Formato documental**: CSV delimitado por barra vertical (`|`), decimal con punto (`.`), moneda `USD`, encabezados: `tracking_id|event_date|billable_weight_kg|sender|recipient`.
- **Primitivas de Calibre**: `band` sobre tabla con unit `kg` y verificación estricta de política $[lower, upper)$.

---

## 5. G5 — Consolidación Real de Cardinalidad Distinta (N:1 y 1:N)

### 5.1. Estructura Contractual
- **Transportista**: `CONSOLIDADOS-DEL-SUR`
- **Moneda**: `ARS` (escala: 2, redondeo: `ROUND_HALF_EVEN`)
- **Vigencia**: `2026-01-01` a `2026-12-31`
- **Estructura N:1 (Consolidación Multiremito en Viaje Común)**:
  * Cardinalidad: `cardinality: "group"`
  * Clave de matching: `attributes.viaje_id`
  * Tarifa del viaje: $22.00\text{ ARS/kg}$ sobre el peso sumado de los remitos que componen el viaje.
  * Tres remitos `S-G5-01` ($350\text{ kg}$), `S-G5-02` ($450\text{ kg}$) y `S-G5-03` ($200\text{ kg}$) viajan juntos en `VIAJE-801`.
  * Total consolidado: $(350 + 450 + 200) \times 22.00 = 1000 \times 22.00 = 22000.00\text{ ARS}$.
- **Estructura 1:N (Múltiples Conceptos sobre Misma Operación)**:
  * Un remito `S-G5-04` genera dos cargos separados:
    - Cargo `C-G5-02` (`FLETE_TRAMO`): Tarifa fija $8000.00\text{ ARS}$.
    - Cargo `C-G5-03` (`SEGURO_CARGA`): Tarifa fija $1200.00\text{ ARS}$.

### 5.2. Datos de Entrada y Fórmulas del Oráculo Independiente

| ID Cargo | Tipo | Remitos Vinculados | Fórmula del Oráculo Independiente | Expected Exacto | Facturado | Estado Esperado |
|---|:---:|---|---|:---:|:---:|:---:|
| `C-G5-01` | **N:1** | `S-G5-01`, `S-G5-02`, `S-G5-03` | $(350 + 450 + 200) \times 22.00 = 1000 \times 22.00$ | **22000.00 ARS** | 22000.00 ARS | **PASS** |
| `C-G5-02` | **1:N** | `S-G5-04` (Flete) | Tarifa directa concepto `FLETE_TRAMO` | **8000.00 ARS** | 8000.00 ARS | **PASS** |
| `C-G5-03` | **1:N** | `S-G5-04` (Seguro) | Tarifa directa concepto `SEGURO_CARGA` | **1200.00 ARS** | 1200.00 ARS | **PASS** |

### 5.3. Representación Documental y Primitivas Previstas
- **Formato documental**: CSV delimitado por `;`, decimal con coma (`,`), encabezados con identificador de viaje.
- **Primitivas de Calibre**: `cardinality: "group"`, `sum(field="attributes.peso_kg")`, evaluación multiconcepto sobre mismo ámbito.

---

## 6. G6 — Recombinación Composicional ("El Sexto Contrato")

### 6.1. Estructura Contractual
- **Transportista**: `INTEGRAL-LOGISTICS`
- **Moneda**: `ARS` (escala: 2, redondeo: `ROUND_HALF_EVEN`)
- **Estructura Combinada**:
  * Lookup tarifario por zona (`Zona_Norte` $\to$ `Zona_Sur`) y vehículo (`CHASIS`).
  * Tarifa base de lookup: $120000.00\text{ ARS}$ en V1; actualizada a $150000.00\text{ ARS}$ en V2.
  * Mínimo garantizado: $100000.00\text{ ARS}$ ($\max$).
  * Requisito de evidencia documental obligatoria: Remito digitalizado con hash (`REMITO_CONFORME`).
  * Cambio de vigencia: V1 hasta `2026-06-30`, V2 desde `2026-07-01`.

### 6.2. Datos de Entrada y Fórmulas del Oráculo Independiente

| Operación | Fecha | Ruta y Vehículo | Versión | Evidencia | Expected Exacto | Facturado | Estado Esperado | Causa del Resultado |
|---|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| `OP-G6-01` | `2026-03-20` | Norte $\to$ Sur, Chasis | V1 | Conforme | **120000.00 ARS** | 120000.00 ARS | **PASS** | Cumple lookup, max y evidencia |
| `OP-G6-02` | `2026-04-15` | Norte $\to$ Sur, Chasis | V1 | **Ausente** | **120000.00 ARS** | 120000.00 ARS | **REVIEW** | Falta evidencia documental |
| `OP-G6-03` | `2026-08-10` | Norte $\to$ Sur, Chasis | V2 | Conforme | **150000.00 ARS** | 120000.00 ARS | **FAIL** | Facturó tarifa vieja de V1 |

---

## 7. Resumen de Estados Deliberados en la Suite

La suite cubre exhaustivamente los estados operativos requeridos:
- **PASS**: 8 casos (`G1-01`, `G1-03`, `G2-01`, `G2-03`, `G3-01`, `G4-01`, `G4-02`, `G4-04`, `G5-01`, `G5-02`, `G5-03`, `G6-01`).
- **FAIL**: 4 casos (`G1-02`, `G2-02`, `G3-03`, `G4-03`, `G6-03`).
- **REVIEW**: 2 casos (`G3-02`, `G6-02`).
- **UNDETERMINABLE**: 1 caso (`G2-04`).
