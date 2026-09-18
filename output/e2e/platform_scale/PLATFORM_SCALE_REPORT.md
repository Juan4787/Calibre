# INFORME DE FASE 9: PLATAFORMA, ESCALA Y ESTABILIDAD

**Proyecto:** CALIBRE / Freight Audit Engine  
**Entornos de Referencia:**
- *Host Local de Desarrollo:* Linux 6.8.0-136-generic | Intel Core i3-4170 (4 hilos @ 3.70GHz) | 11.9 GB RAM (~5.8 GB libres en reposo)
- *Runner CI Windows Nativo:* Windows Server 2025 Datacenter (`windows-latest`) | 4 vCPU | 16 GB RAM
- *Runner CI Escala 100k:* Ubuntu 24.04 LTS (`ubuntu-latest`) | 4 vCPU | 16 GB RAM (15.6 GB total, 14.6 GB libre en reposo)  
**Fecha:** 18 de Septiembre de 2026  
**Estado General de la Fase:** 🟡 **OPEN (Motor/persistencia 100k validado; exportación portable a escala en resolución)**

---

## 1. Resumen Ejecutivo de Gates

| Gate | Subcomponente | Requisito Pre-registrado | Resultado Medido | Veredicto |
|---|---|---|---|---|
| **9A** | Pre-registro y Oráculos | Planes de prueba, oráculos matemáticos independientes y datasets fijados a priori. | Oráculos deterministas fijados antes de ejecutar cualquier suite de prueba (`output/e2e/platform_scale/`). | ✅ **CLOSED** |
| **9W** | Portabilidad Windows Real | 24 casos en Windows Server 2025 nativo (GitHub Actions); huella semántica cruzada vs. Linux. | 24/24 PASS en Windows; 0 divergencias en ARS/USD/findings/provenance (`parity: true`). | ✅ **CLOSED** |
| **9R** | Estabilidad / Resistencia | 50 ejecuciones consecutivas en un proceso único; 0 fugas de FDs, RSS estable, 0 degradación de latencia. | 50 ciclos revalidados con el nuevo `Store.save`: 85 $\rightarrow$ 85 FDs, RSS meseta en 237–238 MB, ratio 1.00x, replay verificado. | ✅ **CLOSED** |
| **9S** | **Cómputo / Persistencia 100k** | Normalización, motor `audit()`, SQLite `Store.save`, `Store.load`, `replay` y API a 100k. | **100.000 cargos completados** en runner de 16 GB (`run 35406238596`). Oráculo matemático 100% exacto, SQLite 474.9 MB, replay idéntico. | ✅ **CLOSED** |
| **9S** | **Exportación XLSX 100k** | Generación de planilla XLSX completa a 100k. | Provenance (~1,3M filas) excede el límite de Excel (1.048.576 filas). `ReportLimitError` evita truncamiento. `audit.json` conserva el 100% sin truncar. | 🟡 **LIMITACIÓN DOCUMENTADA** |
| **9S** | **Portable Bundle 100k** | Generación y verificación del paquete ZIP portable a 100k. | `bundle_bytes` genera ZIP con ~756 MB descomprimidos. `verify_bundle` rechaza por límite de 500 MB. Incidente `SCALE-EXPORT-01`. | 🔴 **OPEN** |
| **Fase 9** | **Global** | Cierre de plataforma, portabilidad, resistencia y escala. | Abierta hasta resolver la inconsistencia del formato de paquete portable a 100k. | 🟡 **OPEN** |

---

## 2. Gate 9W: Portabilidad Windows Real y Huella Semántica

El test de portabilidad se ejecutó en GitHub Actions sobre un runner limpio `windows-latest` (Windows Server 2025 Datacenter) mediante la construcción previa de un wheel (`.whl`) e instalación aislada fuera del árbol de código.

### Resultados de la Suite de Plataforma (WIN-01 a WIN-24):
* **24/24 casos superados** en Windows nativo sin adaptaciones artificiales.
* **Aspectos Críticos Validados:**
  1. *Separadores y Rutas:* Normalización estricta de barras diagonales e inversas, prevención de fallos en rutas absolutas con letra de unidad (`C:\...`).
  2. *Bloqueo de Archivos (Mandatory File Locking):* Cierre explícito y determinista de conexiones SQLite y manejadores de procesos en Windows para evitar errores `WinError 32`.
  3. *Replay Criptográfico Transaccional:* Idéntico en Windows y Linux.
  4. *Unicode y CLI:* Manejo de acentos, caracteres especiales y salidas UTF-8 en consolas Windows.
  5. *UI Headless Playwright:* Servidor FastAPI y pruebas de navegador Chromium superadas sin cuelgues de sockets ni puertos huérfanos.

### Reconciliación Semántica Cruzada (Linux vs. Windows):
* **Divergencias encontradas:** **0**
* **Paridad Semántica:** `true`

---

## 3. Gate 9R: Resistencia y Estabilidad de Recursos

Tras la optimización de `Store.save`, se ejecutó una revalidación limpia de 50 iteraciones continuas en un proceso único sobre el dataset de resistencia (`ENDURANCE_CASES.md`):

* **Ciclos completados:** 50 / 50.
* **Descriptores de Archivo (FDs):** 85 al inicio $\rightarrow$ 85 al final (0 fugas).
* **Consumo de Memoria (RSS):** Meseta estricta en 237–238 MB (0 fugas acumulativas).
* **Latencia de Auditoría:** Ratio exacto de degradación: **1.00x** (sin degradación temporal).
* **Persistencia y Replay en frío:** Determinismo y persistencia SQLite verificados al 100%.

---

## 4. Gate 9S: Cómputo y Persistencia a Escala 100k

El cómputo de 100.000 cargos fue validado experimentalmente en GitHub Actions (`run 35406238596`) sobre un runner `ubuntu-latest` con ~16 GB de RAM total y ~15 GB disponibles al inicio, alcanzando un **peak RSS de 11.355,38 MB (~11,1 GB)** y manteniendo $>4\text{ GB}$ de memoria disponible en todo momento.

### 4.1. Telemetría de Cómputo y Persistencia:
* **Lectura e Ingestión:** 13,67 s | 100.000 cargos y 50.000 remitos procesados.
* **Normalización:** 11,33 s | Modelos Pydantic validados.
* **Motor `audit()`:** **17,65 s** | **5.665,5 cargos/s** (100.000 hallazgos determinados).
* **Store.save (SQLite):** **52,50 s** | Base de datos SQLite íntegra de **474,9 MB**.
* **Store.load:** **18,09 s** | Deserialización canónica íntegra.
* **Replay Determinista:** **42,07 s** | Paridad bit a bit (`identical: true`).
* **Exportación JSON (`audit.json`):** **4,23 s** | **459,3 MB** de JSON canónico.
* **API Retrieval:** **56,10 s** | Endpoint `/api/runs/{id}` respondiendo HTTP 200 con el run íntegro.
* **Oráculo Matemático:** Coincidencia exacta al 100% en todos los hallazgos y totales de ARS y USD.

---

## 5. Caracterización de Límites de Exportación a Escala 100k

### 5.1. Exportación XLSX (Límite Físico de Formato)
* **Comportamiento:** Al generar la hoja `Origen de datos` con 100.000 cargos y 50.000 remitos, el detalle de *provenance* genera $\approx 1.300.000$ filas.
* **Límite de Excel:** El estándar OpenXML (`.xlsx`) no admite más de $1.048.576$ filas por hoja.
* **Contrato de Calibre:** Se activa la salvaguarda `ReportLimitError`. Calibre **no trunca silenciosamente** datos contables o de procedencia.
* **Disponibilidad de Datos:** La totalidad de los datos (cálculos, trazas completas, hallazgos y procedencia registro a registro) se conserva íntegramente y sin truncar en `audit.json` (459 MB).

---

### 5.2. Paquete Portable: Incidente `SCALE-EXPORT-01`
* **Inconsistencia Detectada:**
  - `bundle_bytes()` empaqueta exitosamente `audit.json` (459 MB) y `snapshot.json` (287 MB), produciendo un ZIP comprimido de 28,3 MB con **756 MB descomprimidos**.
  - `verify_bundle()` aplica una defensa estricta contra bombas ZIP de **500 MB** (`sum(file_size) > 500 MB`), rechazando el paquete recién generado con `IntegrityError`.
* **Causa Raíz:** `snapshot.json` es **100% redundante** con `run["snapshot"]`, que ya está contenido íntegramente dentro de `audit.json`.
* **Hecho Demostrado:** Sin la duplicación innecesaria de `snapshot.json`, el paquete portable a 100k sumaría **469,30 MB descomprimidos**, entrando de forma natural bajo el límite de seguridad de 500 MB sin relajar las defensas anti DoS.
* **Estado:** Incidente registrado en `output/e2e/platform_scale/incidents/SCALE-EXPORT-01-BUNDLE-PRODUCER-VERIFIER-MISMATCH/`. Propuesta de solución en evaluación antes de modificar producción.

---

## 6. Caracterización de Hardware Comprobada

* **100.000 cargos fue validado experimentalmente en un runner con ~16 GB de RAM total y ~15 GB disponibles al inicio, alcanzando ~11,35 GB de peak RSS.**
* **Estaciones de trabajo de 8 a 12 GB RAM:** Límite operativo seguro certificado en **50.000 cargos** (consumo pico de ~3,6 GB RSS).

---

## 7. Dictamen y Próximos Pasos

1. **Gate 9A:** ✅ **CLOSED**
2. **Gate 9W:** ✅ **CLOSED**
3. **Gate 9R:** ✅ **CLOSED**
4. **Gate 9S (Motor / Persistencia 100k):** ✅ **CLOSED**
5. **Gate 9S (XLSX 100k):** 🟡 **LIMITACIÓN DOCUMENTADA** (Fallo seguro por límite físico de Excel; `audit.json` es la representación autoritativa completa).
6. **Gate 9S (Portable Bundle 100k):** 🔴 **OPEN** (Incidente `SCALE-EXPORT-01`).
7. **Fase 9 Global:** 🟡 **OPEN** (Pendiente de resolución del paquete portable).
