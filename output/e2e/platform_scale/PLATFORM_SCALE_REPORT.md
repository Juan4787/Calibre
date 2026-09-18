# INFORME DE FASE 9: PLATAFORMA, ESCALA Y ESTABILIDAD

**Proyecto:** CALIBRE / Freight Audit Engine  
**Entorno de Referencia:** Linux 6.8.0-136-generic | Intel Core i3-4170 (4 hilos @ 3.70GHz) | 11.9 GB RAM  
**Fecha:** 18 de Septiembre de 2026  
**Estado General de la Fase:** 🟡 **OPEN (En proceso de revalidación y certificación remota)**

---

## 1. Resumen Ejecutivo de Gates

| Gate | Descripción | Requisito Pre-registrado | Resultado Medido | Veredicto |
|---|---|---|---|---|
| **9A** | Pre-registro y Oráculos | Planes de prueba, oráculos matemáticos independientes y datasets generados a priori. | Oráculos deterministas fijados antes de ejecutar cualquier suite de prueba. | ✅ **CLOSED** |
| **9W** | Portabilidad Windows Real | 24 casos en Windows Server 2025 nativo (GitHub Actions); huella semántica cruzada vs. Linux. | 24/24 PASS en Windows; 0 divergencias en ARS/USD/findings/provenance (`parity: true`). | ✅ **CLOSED** |
| **9R** | Estabilidad / Resistencia | 50 ejecuciones consecutivas en un proceso único; 0 fugas de FDs, RSS estable, 0 degradación de latencia. | 50 ciclos originales pasados (88 FDs, 124,9 MB RSS). Revalidación requerida tras cambios en `Store.save`. | 🟡 **REVALIDATION REQUIRED** |
| **9S** | Escala y Complejidad | Comportamiento asintótico $O(N)$, caracterización de límites y validación completa hasta 100k. | PERF-01 resuelto $O(N)$. PERF-02 optimizado. 50k PASS; 80k/100k abortan por watchdog (`MemAvailable` $\le 2\text{ GB}$). | 🟡 **PARTIAL / RESOURCE-LIMITED** |

---

## 2. Gate 9W: Portabilidad Windows Real y Huella Semántica

El test de portabilidad se ejecutó en GitHub Actions sobre un runner limpio `windows-latest` (Windows Server 2025 Datacenter) mediante la construcción previa de un wheel (`.whl`) e instalación aislada fuera del árbol de código.

### Resultados de la Suite de Plataforma (WIN-01 a WIN-24):
* **24/24 casos superados** en Windows nativo sin adaptaciones artificiales.
* **Aspectos Críticos Validados:**
  1. *Separadores y Rutas:* Normalización estricta de barras diagonales e inversas, prevención de fallos en rutas absolutas con letra de unidad (`C:\...`).
  2. *Bloqueo de Archivos (Mandatory File Locking):* Cierre explícito y determinista de conexiones SQLite y manejadores de archivos en Windows para evitar errores `WinError 32` ("The process cannot access the file because it is being used by another process").
  3. *Replay Criptográfico Transaccional:* Idéntico en Windows y Linux.
  4. *Unicode y CLI:* Manejo de acentos, caracteres especiales y salidas UTF-8 en consolas Windows.
  5. *UI Headless Playwright:* Servidor FastAPI y pruebas de navegador Chromium superadas sin cuelgues de sockets ni puertos huérfanos.

### Reconciliación Semántica Cruzada (Linux vs. Windows):
Se extrajeron los fingerprints semánticos de tres datasets (Demo, Cliente Real 2 y Estrés de Plataforma) en ambos sistemas operativos:
* **Divergencias encontradas:** **0**
* **Paridad Semántica:** `true`
* Los resúmenes contables, las determinaciones contractuales en ARS y USD, los hallazgos y los hashes de origen coincidieron al 100% bit por bit.

---

## 3. Gate 9R: Resistencia y Estabilidad de Recursos

La ejecución previa de 50 ciclos completos en un único proceso demostró:
* **Descriptores de Archivo (FDs):** 88 $\rightarrow$ 88 FDs (0 fugas).
* **Consumo de Memoria (RSS):** Estable en 124,9 MB (0 fugas acumulativas).
* **Latencia:** 11,54 s $\rightarrow$ 10,32 s (sin degradación).

> [!IMPORTANT]
> **Revalidación Pendiente:** Debido a que `Store.save` fue modificado posteriormente para optimizar la serialización y la gestión de memoria en el ciclo de persistencia, se requiere ejecutar nuevamente la suite de 50 iteraciones para certificar que el nuevo código mantiene exactamente la misma estabilidad.

---

## 4. Gate 9S: Hallazgos de Rendimiento y Correcciones

### 4.1. Incidente PERF-01: Cuello Cuadrático en Exportación XLSX
* **Causa Raíz:** En `src/freight_audit/reporting.py`, dentro del bucle de escritura de filas, se evaluaba `ws.max_row >= MAX_XLSX_ROWS`. En `openpyxl`, cada llamada a `ws.max_row` recorre internamente todas las celdas ya creadas para calcular `max(coordinate)`, convirtiendo la adición de $R$ filas en un algoritmo de complejidad cuadrática $O(R^2)$.
* **Solución:** Se sustituyó `ws.max_row` por un contador local `row_count = 1` incrementado en cada fila.
* **Preservación Estricta de Semántica:** Se mantuvo intacto el bucle de formato posterior:
  ```python
  for row in ws:
      for cell in row:
          cell.data_type = "s"
          cell.alignment = Alignment(vertical="top", wrap_text=True)
  ```
* **Verificación:**
  - Equivalencia XML demostrada para el caso de regresión bajo prueba controlada.
  - Pruebas de límites de Excel (`MAX_XLSX_ROWS` y `MAX_XLSX_CELL_CHARS`) pasando al 100%.
* **Curva de Escala Medida:**
  * 1.000 cargos: **6,44 s** (antes 33,91 s — mejora de 5,3x)
  * 2.000 cargos: **13,50 s** (antes 119,48 s — ratio de 2,09x, estrictamente lineal)
  * 5.000 cargos: **34,83 s** (antes proyectado ~745 s)
  * 10.000 cargos: **70,54 s** (antes proyectado ~3.400 s)

---

### 4.2. Incidente PERF-02: Amplificación de Memoria en Persistencia
* **Aislamiento Causal:**
  1. *Harness de Pruebas (QA):* Acumulación de arenas entre warm-up y 5 repeticiones pesadas en el mismo proceso. Corregido aislando cada repetición en un subproceso hijo independiente.
  2. *Watchdog Activo en el Harness:* Monitoreo continuo de RSS ($\ge 8.000\text{ MB}$) y `MemAvailable` ($\le 2.000\text{ MB}$) para abortar limpiamente antes de provocar swap thrashing o congelamientos del host.
  3. *Optimización en Producto (`Store.save`):*
     - Reducción de serializaciones canónicas redundantes (de 3 a 1 en `result`, de 2 a 1 en `dataset`).
     - Cálculo directo de SHA-256 desde los bytes serializados una sola vez.
     - Destrucción inmediata del árbol temporal de re-auditoría pasando `audit(dataset)` como argumento anónimo a `digest()`.
     - Invariante crítico preservado: `Store.save(dataset, tampered_result)` sigue fallando incondicionalmente con `IntegrityError`.

---

## 5. Resultados de Escala y Curva de Crecimiento Asintótico

### 5.1. Telemetría de Campaña de Volumen

| Volumen ($N$) | Estado | Tiempo de Auditoría | Tiempo Total | Peak RSS | Tasa del Motor |
|---|---|---|---|---|---|
| **10.000** | ✅ PASS | 2,40 s | 157,02 s* | 1.434,41 MB | 4.167 cargos/s |
| **20.000** | ✅ PASS | 4,57 s | 51,29 s | 1.586,00 MB | 4.376 cargos/s |
| **40.000** | ✅ PASS | 9,21 s | 101,28 s | 2.910,78 MB | 4.343 cargos/s |
| **50.000** | ✅ PASS | 10,70 s | 138,06 s | 3.613,72 MB | 4.672 cargos/s |
| **80.000** | 🛑 RESOURCE_LIMIT | — | — | > 3.650 MB | Interceptado limpiamente por watchdog (`MemAvailable` $\le 2\text{ GB}$) |
| **100.000** | 🛑 RESOURCE_LIMIT | — | — | > 3.680 MB | Interceptado limpiamente por watchdog (`MemAvailable` $\le 2\text{ GB}$) |

*\*En 10k se ejecutan todos los artefactos de visualización (`export_xlsx` y `bundle_zip`); a partir de >10k se aíslan la auditoría, persistencia, replay e interfaz API HTTP.*

### 5.2. Curva de Crecimiento Asintótico (Duplicación de Tamaño)

$$R_{audit} = \frac{T(2N)}{T(N)}, \quad R_{rss} = \frac{RSS(2N)}{RSS(N)}$$

* **10k $\rightarrow$ 20k (x2.0 cargos):**
  * $R_{audit} = \frac{4,57\text{ s}}{2,40\text{ s}} = \mathbf{1,90x}$
  * $R_{rss} = \frac{1.586\text{ MB}}{1.434\text{ MB}} = \mathbf{1,11x}$
  * **Evaluación:** `LINEAR_OR_SUBQUADRATIC`
* **20k $\rightarrow$ 40k (x2.0 cargos):**
  * $R_{audit} = \frac{9,21\text{ s}}{4,57\text{ s}} = \mathbf{2,01x}$
  * $R_{rss} = \frac{2.910\text{ MB}}{1.586\text{ MB}} = \mathbf{1,84x}$
  * **Evaluación:** `LINEAR_OR_SUBQUADRATIC`

**Conclusión Algorítmica:** El motor `audit()` y el ciclo de persistencia/replay presentan una complejidad estrictamente **lineal $O(N)$**. No existe complejidad cuadrática en el motor.

### 5.3. Caracterización del Límite Físico del Host de Referencia
* En este equipo con **11,9 GB de RAM** (donde el sistema operativo, entorno de escritorio y servicios en reposo consumen ~6,1 GB, dejando ~5,8 GB disponibles):
  * **50.000 cargos** se procesan de forma holgada y estable en ~138 s con 3,6 GB RSS.
  * **80.000 y 100.000 cargos** no completan en este host porque la memoria transitoria requerida supera el margen disponible antes de tocar el piso de seguridad de 2 GB.
  * El sistema ahora falla de forma controlada y segura mediante el watchdog, eliminando el riesgo de congelamiento. Sin embargo, **100k no está validado experimentalmente**.
  * Determinar los requisitos de hardware para 100k (e.g. si 16 GB de RAM es suficiente) requerirá pruebas en un entorno con mayor memoria disponible.

---

## 6. Batería de Estrés Contractual (Complexity Stress)

* **COMPLEX-01 (Matching Denso - 1k cargos vs 20k remitos):** 0,46 s (2.150 cargos/s) — **PASS**
* **COMPLEX-02 (25 versiones contractuales y lookup tables densas):** 0,51 s (4.938 cargos/s) — **PASS**
* **COMPLEX-03 (Consolidación N:1 y 1:N Intensa):** 0,03 s (16.347 cargos/s) — **PASS**

---

## 7. Dictamen y Próximos Pasos

1. **Gate 9A:** ✅ **CLOSED**
2. **Gate 9W:** ✅ **CLOSED**
3. **Gate 9R:** 🟡 **REVALIDATION REQUIRED** (ejecutar suite de 50 repeticiones con el nuevo `Store.save`).
4. **Gate 9S:** 🟡 **PARTIAL / RESOURCE-LIMITED** (50k PASS; 80k/100k limitados por hardware de referencia).
5. **Fase 9:** 🟡 **OPEN**.

### Plan Inmediato:
1. Confirmar y subir los cambios a `origin/main` (`git add`, `git commit`, `git push`).
2. Revalidar **9R (50 repeticiones)** en el entorno local con el nuevo código de persistencia.
3. Definir estrategia para 9S: ¿probar 100k en un runner/máquina con mayor memoria o certificar formalmente el límite de 50.000 cargos para v0.1.0?
