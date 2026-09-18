# Plan de Validación: Fase 9 — Plataforma, Escala y Estabilidad

## 1. Alcance y Objetivos

El objetivo de Fase 9 es someter a Calibre a tres pruebas de esfuerzo antes de iniciar la interacción con clientes reales:
1. **Gate 9W — Windows Real / Portabilidad:** Garantizar que el artefacto empaquetado (.whl) funcione en un entorno Windows nativo con paridad semántica exacta respecto a Linux, sin fallos por paths, separadores, codificación Unicode, saltos de línea CRLF/LF, ni concurrencia/locking en SQLite.
2. **Gate 9S — Escala / Rendimiento / Complejidad:** Medir el comportamiento del motor y del almacenamiento frente a volúmenes crecientes (10k, 50k, 100k filas) y bajo estrés contractual (matching denso, múltiples versiones/tarifas, consolidación N:1 y 1:N), evaluando tiempos, uso de memoria (RSS) y conservación estricta de invariantes.
3. **Gate 9R — Endurance / Estabilidad de Recursos:** Demostrar que el proceso puede ejecutar 50 auditorías consecutivas sin acumulación progresiva de memoria (memory leaks), sin fugas de descriptores de archivo ni acumulación de archivos temporales.

---

## 2. Hardware y Entorno Baseline

### Entorno Primario de Desarrollo, Profiling y Benchmark (Ubuntu Linux)
* **SO:** Ubuntu Linux x86_64 (Kernel 6.8.0-136-generic)
* **CPU:** Intel(R) Core(TM) i3-4170 CPU @ 3.70GHz (2 núcleos físicos, 4 hilos lógicos)
* **Memoria RAM:** 11 GiB física + 2 GiB swap
* **Python:** 3.12.3 (GCC 13.3.0)
* **SQLite:** 3.45.1
* **Filesystem:** ext4 sobre `/dev/sda3`
* **Commit Base:** `0127b9d85c90febbd9ca067d4e67ca313685240a` (Clean tree)

### Entorno Remoto Windows (GitHub Actions Hosted Runner)
* **Runner:** `windows-latest`
* **Arquitectura:** x86_64
* **Python:** 3.12 (via `actions/setup-python@v5`)
* **Aislamiento:** Entorno virtual clean-room creado en directorio temporal fuera del checkout del repositorio.

---

## 3. Protocolo Metodológico y Reglas Innegociables

1. **Sin atajos locales para Windows:** No se utilizarán Wine, WSL ni emulaciones. Toda la evidencia de Windows se obtendrá ejecutando el runner nativo de GitHub Actions.
2. **Inmutabilidad de código productivo durante primera pasada:** `src/freight_audit/` no será modificado para ocultar defectos. Todo fallo legítimo de producto se preservará en `output/e2e/platform_scale/incidents/CASE-ID/`.
3. **Determinismo:** Todos los generadores usarán seeds fijas prerregistradas y oráculos matemáticos independientes sin reutilizar `freight_audit.engine.audit`.
4. **Independencia de Gates:** 9W, 9S y 9R son evaluados por separado. No existen aprobaciones por promedio ni por compensación.
5. **Aritmética Decimal:** Cero conversión a punto flotante binario en cálculos económicos o invariantes.
