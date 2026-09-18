# Especificación de Escala y Rendimiento: Subfase 9S

Este documento establece el diseño experimental para determinar los límites de escala, las características de complejidad y el perfil de recursos del motor Calibre.

---

## 1. Diseño del Generador Sintético Determinista

El generador `generate_scale_dataset.py` operará con una semilla pseudoaleatoria fija (`seed=42`) para garantizar la total reproducibilidad del benchmark.
El dataset no consistirá en filas idénticas clonadas, sino en una distribución equilibrada y precalculable matemáticamente de operaciones logísticas:

### Composición del Dataset de Escala
1. **PASS (~40%):** Envíos con tarifa plana o por peso/bulto coincidente con el acuerdo contractual.
2. **FAIL por Exceso (~20%):** Cargos facturados por encima de la tarifa de referencia calculada.
3. **FAIL por Defecto (~10%):** Cargos facturados por debajo de la tarifa calculada.
4. **REVIEW (~15%):**
   * Evidencia faltante (remitos sin remito firmado o código de entrega).
   * Matching ambiguo (múltiples envíos plausibles para un remito).
   * Desvío por fuera de tolerancia admitida.
5. **UNDETERMINABLE (~15%):**
   * Fechas fuera de ventana de vigencia contractual.
   * Moneda no cubierta por el acuerdo.
   * Reglas en conflicto.
6. **Segregación de Moneda:** Distribución de ~70% ARS y ~30% USD. Prohibición estricta de mezcla o conversión en summaries.
7. **Relaciones de Agrupación:**
   * 1:1 estándar (~80%).
   * N:1 consolidación de remitos (~10%).
   * 1:N desglose de cargos por remito (flete base + seguro + peaje) (~10%).
8. **Múltiples Liquidaciones:** Particionado en al menos 2 códigos de liquidación para validar el aislamiento por `settlement` (QA-56).

### Oráculo Agregado Independiente
Para cada tamaño $N$, el generador emitirá un archivo canónico `expected-scale-{N}.json` que incluirá:
* Total de envíos (`total_shipments`) y cargos (`total_charges`).
* Conteo exacto por status (`PASS`, `FAIL`, `REVIEW`, `UNDETERMINABLE`).
* Totales facturados y esperados por moneda (`ARS`, `USD`).
* Discrepancias confirmadas por exceso y por defecto calculadas por fórmula sin pasar por `audit()`.
* Checksums de control de IDs para verificar conservación estricta.

---

## 2. Campañas de Volumen Principal

Se ejecutarán tres niveles de escala obligatorios y uno opcional:

| Nivel | Filas Totales ($N$) | Cargos Aprox. | Objetivo de Validación |
|---|---|---|---|
| **SCALE-10K** | 10.000 | ~10.000 | Línea de base de rendimiento medio. |
| **SCALE-50K** | 50.000 | ~50.000 | Volumen representativo de operación mensual estándar. |
| **SCALE-100K** | 100.000 | ~100.000 | **Gate de escala principal.** Validación de robustez de memoria y persistencia. |
| **SCALE-250K** | 250.000 | ~250.000 | *Opcional.* Exploración de límites si 100K completa holgadamente. |

### Protocolo de Medición
* **Iteraciones:** 1 ejecución de calentamiento (warm-up) descartada + 5 ejecuciones cronometradas.
* **Estadísticas calculadas:** Mediana (métrica principal), Mínimo, Máximo, Media, Desviación Estándar, P95 observado.
* **Etapas medidas por separado:**
  1. `input_generation_or_read`: Tiempo de lectura del dataset.
  2. `import_normalization`: Parseo e ingesta de modelos Pydantic.
  3. `engine_audit`: Ejecución de reglas económicas en memoria.
  4. `store_save`: Escritura transaccional en SQLite WAL.
  5. `store_load`: Carga e hidratación desde SQLite.
  6. `transactional_replay`: Replay y confirmación de hash.
  7. `export_json`: Serialización JSON canónica.
  8. `export_xlsx`: Generación del libro Excel (`openpyxl`).
  9. `export_html`: Render del informe HTML autocontenido.
  10. `bundle_zip`: Creación del archivo ZIP.
  11. `bundle_verify`: Verificación criptográfica del bundle.
  12. `api_retrieval`: Consulta del run via cliente HTTP local.

---

## 3. Curva de Crecimiento y Complejidad Algorítmica

Para detectar indicios de comportamiento cuadrático $O(n^2)$ o superlineal severo:
* Se ejecutarán 4 puntos de escala con el mismo perfil generador: **10k, 20k, 40k, 80k**.
* Se calcularán los ratios de duplicación de tamaño:
  $$R_{audit} = \frac{T(2N)}{T(N)}, \quad R_{rss} = \frac{RSS(2N)}{RSS(N)}$$
* **Criterio de Alarma:** Si $R_{audit} \approx 4$ de forma sostenida entre duplicaciones, se clasifica como comportamiento cuadrático y se aísla la función responsable mediante profiling.

---

## 4. Baterías de Estrés Contractual (Complexity Stress)

Para evitar algoritmos que funcionen bien solo con datos planos:
* **COMPLEX-01 (Matching Denso):** Dataset donde cada cargo coincide parcialmente con múltiples candidatos de envío por fecha y zona, obligando al motor a evaluar desempates y marcar ambigüedades.
* **COMPLEX-02 (Complejidad de Reglas y Lookups):** Acuerdo con múltiples versiones históricas (5+), decenas de bandas de peso y tablas de tarifas densas.
* **COMPLEX-03 (Consolidación N:1 y 1:N Intensa):** 50% de las operaciones consolidadas en grupos de 5 a 10 envíos por remito y múltiples conceptos de cargo por envío.
