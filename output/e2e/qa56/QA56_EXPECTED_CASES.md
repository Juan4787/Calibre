# FASE 7.5 — PRERREGISTRO DE CASOS CANÓNICOS QA-56

**Familia:** QA-56 (*Separación de liquidaciones y alcance de obligación*)  
**Principio de diseño:** `settlement` constituye una frontera explícita de agrupación y asignación contable en el motor de auditoría.
- Mismo remito + mismo concepto + misma liquidación -> se agrupa según las reglas vigentes (coalescencia de cargos en la liquidación).
- Mismo remito + mismo concepto + **distinta liquidación** -> **no se fusiona silenciosamente**; produce findings independientes que evalúan la obligación correspondiente a cada liquidación.

---

## 1. Catálogo de los 6 Casos Canónicos Prerregistrados

### Caso 1: Dos cargos idénticos en el mismo settlement
* **Descripción:** Un transportista factura dos veces el mismo concepto para una misma operación dentro de la misma liquidación (`LIQ-01`).
* **Fixture / Input:**
  * Operación: `REM-C1` (peso: 50 kg, fecha: 2026-03-10). Tarifa esperada según acuerdo: $100.00 ARS.
  * Cargos:
    * `CH-C1-A`: remito `REM-C1`, concepto `FLETE`, importe `100.00`, moneda `ARS`, settlement `LIQ-01`.
    * `CH-C1-B`: remito `REM-C1`, concepto `FLETE`, importe `100.00`, moneda `ARS`, settlement `LIQ-01`.
* **Comportamiento Esperado:**
  * Ambos cargos comparten `(agreement, ('REM-C1',), 'FLETE', 'ARS', 'LIQ-01')`.
  * **Se agrupan en 1 único finding**:
    * `charge_ids`: `["CH-C1-A", "CH-C1-B"]`
    * `actual`: `200.00`
    * `expected`: `100.00`
    * `difference`: `100.00`
    * `reasons`: Si `duplicate_fields` está configurado (`reference`, `concept`, `amount`), incluye advertencia de duplicación y estado `REVIEW`. Si no estuviera configurado, `difference > tolerance` deriva en `FAIL`.

---

### Caso 2: Mismos cargos en settlements distintos
* **Descripción:** Aparecen dos cargos idénticos para la misma operación y concepto, pero presentados en dos liquidaciones o facturas diferentes (`LIQ-01` y `LIQ-02`).
* **Fixture / Input:**
  * Operación: `REM-C2` (peso: 50 kg). Tarifa esperada: $100.00 ARS.
  * Cargos:
    * `CH-C2-A`: remito `REM-C2`, concepto `FLETE`, importe `100.00`, moneda `ARS`, settlement `LIQ-01`.
    * `CH-C2-B`: remito `REM-C2`, concepto `FLETE`, importe `100.00`, moneda `ARS`, settlement `LIQ-02`.
* **Comportamiento Esperado:**
  * Se particionan por settlement:
    * Clave A: `(agreement, ('REM-C2',), 'FLETE', 'ARS', 'LIQ-01')`
    * Clave B: `(agreement, ('REM-C2',), 'FLETE', 'ARS', 'LIQ-02')`
  * **Se generan 2 findings completamente independientes**:
    * Finding A (`LIQ-01`): `charge_ids = ["CH-C2-A"]`, `actual = 100.00`, `expected = 100.00`, `difference = 0.00`, `status = PASS` (o `REVIEW` si duplicate detector alerta sobre duplicación inter-liquidación, pero con importe propio $100).
    * Finding B (`LIQ-02`): `charge_ids = ["CH-C2-B"]`, `actual = 100.00`, `expected = 100.00`, `difference = 0.00`, `status = PASS`.
  * **Invariante crítica:** En ningún caso se fusionan en un finding con `actual = 200.00`.

---

### Caso 3: Consolidación N:1 dentro de una misma liquidación
* **Descripción:** Un viaje consolidado ampara dos remitos con un único cargo global facturado en `LIQ-01`.
* **Fixture / Input:**
  * Operaciones: `REM-C3-1` (peso 10 kg) y `REM-C3-2` (peso 15 kg).
  * Regla de acuerdo: `FLETE_CONSOLIDADO` = suma de pesos × $10/kg = 25 kg × $10 = $250.00 ARS.
  * Cargo:
    * `CH-C3`: remito `VIAJE-C3`, concepto `FLETE_CONSOLIDADO`, importe `250.00`, moneda `ARS`, settlement `LIQ-01`.
* **Comportamiento Esperado:**
  * **1 único finding consolidado**:
    * `shipment_ids`: `["REM-C3-1", "REM-C3-2"]`
    * `charge_ids`: `["CH-C3"]`
    * `actual`: `250.00`
    * `expected`: `250.00`
    * `difference`: `0.00`
    * `status`: `PASS`

---

### Caso 4: Multi-cargo 1:N dentro de una misma liquidación
* **Descripción:** Una misma operación recibe múltiples cargos de conceptos distintos bajo una misma liquidación (`LIQ-01`).
* **Fixture / Input:**
  * Operación: `REM-C4` (peso 50 kg).
  * Tarifas esperadas: `FLETE` = $100.00 ARS; `SEGURO` = $15.00 ARS.
  * Cargos:
    * `CH-C4-1`: remito `REM-C4`, concepto `FLETE`, importe `100.00`, settlement `LIQ-01`.
    * `CH-C4-2`: remito `REM-C4`, concepto `SEGURO`, importe `15.00`, settlement `LIQ-01`.
* **Comportamiento Esperado:**
  * Las claves de agrupación divergen por concepto:
    * Clave 1: `(agreement, ('REM-C4',), 'FLETE', 'ARS', 'LIQ-01')`
    * Clave 2: `(agreement, ('REM-C4',), 'SEGURO', 'ARS', 'LIQ-01')`
  * **2 findings independientes**:
    * Finding FLETE: `charge_ids = ["CH-C4-1"]`, `concept = "FLETE"`, `actual = 100.00`, `expected = 100.00`, `status = PASS`.
    * Finding SEGURO: `charge_ids = ["CH-C4-2"]`, `concept = "SEGURO"`, `actual = 15.00`, `expected = 15.00`, `status = PASS`.

---

### Caso 5: Mismo remito/concepto repetido en dos liquidaciones con importes distintos
* **Descripción:** Un remito es facturado en enero de forma correcta y re-facturado en febrero con sobrecargo.
* **Fixture / Input:**
  * Operación: `REM-C5`. Tarifa contractual esperada = $100.00 ARS.
  * Cargos:
    * `CH-C5-1`: remito `REM-C5`, concepto `FLETE`, importe `100.00`, settlement `LIQ-ENE`.
    * `CH-C5-2`: remito `REM-C5`, concepto `FLETE`, importe `130.00`, settlement `LIQ-FEB`.
* **Comportamiento Esperado:**
  * **2 findings independientes**:
    * Finding ENE: `charge_ids = ["CH-C5-1"]`, `actual = 100.00`, `expected = 100.00`, `difference = 0.00`, `status = PASS`.
    * Finding FEB: `charge_ids = ["CH-C5-2"]`, `actual = 130.00`, `expected = 100.00`, `difference = 30.00`, `confirmed_difference = 30.00`, `status = FAIL`.
  * **Invariante:** La discrepancia de febrero (+30.00) se atribuye con precisión quirúrgica a `LIQ-FEB`, sin contaminar el finding de `LIQ-ENE` ni generar un finding distorsionado de $230.00.

---

### Caso 6: Dataset mixto con dos liquidaciones donde totales y findings se reconcilian por separado
* **Descripción:** Un lote auditado contiene transacciones correspondientes a dos liquidaciones distintas (`LIQ-A` y `LIQ-B`).
* **Fixture / Input:**
  * Liquidación A:
    * `REM-06A-1`: `FLETE` facturado `100.00`, esperado `100.00`.
    * `REM-06A-2`: `FLETE` facturado `180.00`, esperado `150.00` (desvío +30.00).
    * Subtotal facturado LIQ-A = $280.00; esperado = $250.00; discrepancia confirmada = +$30.00.
  * Liquidación B:
    * `REM-06B-1`: `FLETE` facturado `200.00`, esperado `200.00`.
    * `REM-06B-2`: `FLETE` facturado `70.00`, esperado `80.00` (desvío -10.00).
    * Subtotal facturado LIQ-B = $270.00; esperado = $280.00; discrepancia confirmada = -$10.00.
* **Comportamiento Esperado:**
  * **4 findings independientes** (2 en LIQ-A, 2 en LIQ-B).
  * Reconciliación matemática exacta por liquidación:
    * LIQ-A: facturado $280.00, esperado $250.00, discrepancia confirmada $30.00 (1 PASS, 1 FAIL).
    * LIQ-B: facturado $270.00, esperado $280.00, discrepancia confirmada -$10.00 (1 PASS, 1 FAIL).
  * Total global del lote auditado:
    * Facturado = $550.00 ARS.
    * Discrepancia neta confirmada = +$20.00 ARS.
    * Discrepancia sobrecargo (+30.00), subcargo (-10.00).
