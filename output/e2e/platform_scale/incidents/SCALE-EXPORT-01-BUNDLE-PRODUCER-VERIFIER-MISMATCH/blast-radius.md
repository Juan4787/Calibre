# Blast Radius & Architectural Analysis: Incident SCALE-EXPORT-01

**Identificador:** `SCALE-EXPORT-01-BUNDLE-PRODUCER-VERIFIER-MISMATCH`  
**Título:** Portable bundle generated above verifier's own 500 MB limit  
**Componente Afectado:** `src/freight_audit/reporting.py` (`bundle_bytes` y `verify_bundle`)  
**Fecha:** 18 de Septiembre de 2026  
**Severidad:** P1 — Inconsistencia de Contrato Productor ↔ Verificador  

---

## 1. Descripción del Problema y Causa Raíz

En Calibre, el paquete portable (`bundle_bytes`) empaqueta un archivo ZIP que incluye:
- `audit.json`: Serialización canónica de `run` (que incluye metadatos, decisiones, `result` y el `snapshot` completo de entrada).
- `snapshot.json`: Serialización canónica de `run["snapshot"]`.
- `reporte.html`: Informe HTML auto-contenido.
- `auditoria.xlsx` (o `ADVERTENCIA_EXPORTACION.txt` si supera `MAX_XLSX_ROWS`).
- `sources/*`: Archivos fuente originales (CSVs, etc.).
- `manifest.json`: Formato (`freight-audit-bundle/v1`), run_id y SHA-256 de cada archivo.

### La Causa Raíz Técnica:
1. **Duplicación del 100% del Dataset de Entrada:**
   `run["snapshot"]` ya está incluido **íntegramente** dentro de `audit.json`. Generar un archivo independiente `snapshot.json` duplica el 100% del árbol de datos de entrada.
2. **Amplificación de Tamaño Uncompressed:**
   A 100.000 cargos, `audit.json` pesa **459,34 MB** y `snapshot.json` pesa **287,03 MB**. La suma de ambos archivos es de **746,37 MB**.
3. **Inconsistencia de Contrato Productor ↔ Verificador:**
   - `bundle_bytes()` no comprueba el límite antes de generar el paquete y produce exitosamente un ZIP de **28,3 MB comprimido**.
   - `verify_bundle()` aplica una regla de seguridad anti-bombas ZIP estricta:
     ```python
     if sum(i.file_size for i in infos) > 500 * 1024 * 1024:
         raise IntegrityError("El paquete contiene entradas repetidas o supera el tamaño admitido.")
     ```
   - **Resultado:** Calibre genera un archivo ZIP válido que su propia función oficial de verificación rechaza como corrupto/inválido.

---

## 2. Telemetría Exacta Medida (10k / 50k / 100k)

| Archivo / Componente | 10.000 Cargos | 50.000 Cargos | 100.000 Cargos |
|---|---|---|---|
| `audit.json` | 45,82 MB | 229,61 MB | **459,34 MB** |
| `snapshot.json` (duplicado) | 29,98 MB | 150,42 MB | **287,03 MB** |
| `reporte.html` | 1,82 MB | 9,10 MB | **18,19 MB** |
| `auditoria.xlsx` / Advertencia | 7,82 MB | ~39,00 MB | 180 B (Advertencia Excel) |
| `sources/*` | 1,45 MB | 7,21 MB | **13,89 MB** |
| `manifest.json` | < 1 KB | < 1 KB | < 1 KB |
| **Total Descomprimido Actual** | **86,89 MB** | **435,34 MB** | **756,33 MB** |
| **Límite Verificador (`verify_bundle`)** | 500,00 MB | 500,00 MB | 500,00 MB |
| **Resultado Verificación Actual** | ✅ **PASS** | ✅ **PASS** | 🔴 **FAIL (`IntegrityError`)** |
| **Total Descomprimido SIN `snapshot.json`** | **56,91 MB** | **284,92 MB** | **469,30 MB** |
| **¿Entra bajo el límite de 500 MB sin duplicación?** | ✅ SÍ (11% del límite) | ✅ SÍ (57% del límite) | ✅ **SÍ (94% del límite)** |

---

## 3. Redundancia Exacta de `snapshot.json`

En `src/freight_audit/storage.py`, `store.load(run_id)` devuelve un diccionario `run`:
```python
{
    "id": row["id"],
    "input_hash": row["input_hash"],
    "result_hash": row["result_hash"],
    "artifact_hash": row["artifact_hash"],
    "created_at": row["created_at"],
    "metadata": load_json(row["metadata"]),
    "decisions": self.decisions(run_id),
    "snapshot": load_json(row["snapshot"]),
    "result": load_json(row["result"]),
}
```
`canonical(run["snapshot"])` es **100,00% idéntico** al contenido de `snapshot.json`.
En `verify_bundle()`:
```python
if canonical(load_json(archive.read("snapshot.json"))) != canonical(run["snapshot"]):
    raise IntegrityError("El snapshot no coincide con la auditoría.")
```
El único propósito de `snapshot.json` en v1 es ser comparado contra `run["snapshot"]`. Toda la información para replay, auditoría y consulta ya reside autoritativamente en `audit.json`.

---

## 4. Revisión de Consumidores de `snapshot.json`

1. **`Store.replay(run_id)`:** No consume `snapshot.json`; opera sobre `run["snapshot"]` desde la base de datos o el objeto devuelto por `store.load()`.
2. **`verify_bundle(data)`:** Devuelve el diccionario `run` (deserializado de `audit.json`). Los clientes que consumen el retorno de `verify_bundle` acceden a `run["snapshot"]`.
3. **Scripts de Test y QA (`reconcile.py`, `clean_room`, `fault_injection`):**
   - En `qa/reconcile.py:99`: `read_bundle_snapshot(directory)` lee `directory / "snapshot.json"`. Puede adaptarse para leer `directory / "snapshot.json"` si existe, o extraerlo de `directory / "audit.json"`.
   - En `fault_injection`: Altera `snapshot.json` para validar detección de manipulación.

---

## 5. Racional de Seguridad del Límite de 500 MB

El límite de 500 MB uncompressed en `verify_bundle()` es una defensa explícita de seguridad contra **bombas de descompresión (ZIP bombs)** y agotamiento no controlado de memoria o disco al importar paquetes de clientes externos.
**Conclusión de Seguridad:** Subir arbitrariamente el límite a 1 GB debilitaría la protección contra DoS y trasladaría la ineficiencia estructural al consumidor.

---

## 6. Evaluación de Opciones Técnicas

### Opción 1: Eliminar duplicación de `snapshot.json` en `freight-audit-bundle/v1`
* **Mecanismo:** Dejar de escribir `snapshot.json` en `bundle_bytes`. En `verify_bundle`, si `snapshot.json` no está en el archivo, se verifica `run["snapshot"]` contra `run["input_hash"]`. Si `snapshot.json` está presente (bundles v1 históricos), se verifica que coincida.
* **Tamaño 100k Esperado:** **469,30 MB** (entra bajo los 500 MB).
* **Compatibilidad:**
  - Hacia atrás (Calibre nuevo leyendo bundles viejos): 100% compatible.
  - Hacia adelante (Calibre viejo leyendo bundle nuevo): **INCOMPATIBLE** (un verificador v1 anterior fallará con `IntegrityError` porque exige que `snapshot.json` esté en `archive.namelist()`).
* **Propiedades de Seguridad:** Intactas. `input_hash` sigue validando criptográficamente el snapshot.
* **Blast Radius:** Medio (rompe a consumidores externos que usen la versión v1 previa).

---

### Opción 2 (Recomendada): Introducir `freight-audit-bundle/v2` con soporte bidireccional en `verify_bundle`
* **Mecanismo:**
  1. `bundle_bytes(store, run_id, format="freight-audit-bundle/v2")`:
     - Emite formato `v2`.
     - `files` incluye `audit.json`, `reporte.html`, `auditoria.xlsx` / advertencia, `sources/*` y `manifest.json`.
     - Omite el archivo redundante `snapshot.json`.
  2. `verify_bundle(data)`:
     - Si `manifest["format"] == "freight-audit-bundle/v1"`: ejecuta la verificación estricta v1 exigiendo `snapshot.json` (preserva al 100% la compatibilidad con bundles históricos).
     - Si `manifest["format"] == "freight-audit-bundle/v2"`: ejecuta la verificación v2 validando `audit.json` y que `digest(run["snapshot"]) == run["input_hash"]`.
     - Si el formato no es reconocido: lanza `IntegrityError("Formato de paquete no admitido.")`.
* **Tamaño 100k Esperado:** **469,30 MB** (descomprimido) / **27,0 MB** (comprimido).
* **Compatibilidad:**
  - Bundles históricos v1: **100% verificables y preservados**.
  - Especificación formal: Versión explícita y no ambigua en el manifiesto.
* **Propiedades de Seguridad:** Idénticas o superiores. `digest(run["snapshot"])` se valida contra `run["input_hash"]`, `run["id"]` se valida contra el manifiesto y cada documento original en `sources/` se valida contra su hash SHA-256.
* **Blast Radius:** Mínimo. Localizado en `src/freight_audit/reporting.py` (unas 15 líneas de código).
* **Tests Requeridos:**
  - Test de bundle v2 a 10k y 100k.
  - Test de bundle v1 histórico (asegurar que sigue verificando y fallando ante tampering).
  - Test de rechazo de formatos desconocidos (`v3`, etc.).

---

### Opción 3: Rechazo Preventivo en el Productor (`bundle_bytes`)
* **Mecanismo:** Si la suma de archivos a empaquetar supera 500 MB, `bundle_bytes` lanza `ReportLimitError("El tamaño del paquete supera el límite de 500 MB admitido para paquetes portables. Utilizar audit.json directamente.")`.
* **Tamaño 100k:** No se genera bundle a 100k.
* **Compatibilidad:** 100%.
* **Consecuencia de Gate 9S:** 100k quedaría sin soporte de paquete portable (el scope portable certificado quedaría fijado en $\le 50.000$ cargos).
* **Veredicto:** Es una defensa válida si no se desea optimizar el formato, pero inferior a la Opción 2, ya que la Opción 2 permite que 100k complete exitosamente dentro de los 500 MB sin agrandar el límite.

---

## 7. Invariante de Contrato a Preservar

> **INVARIANTE FUNDAMENTAL:**  
> *Todo paquete portable emitido por `bundle_bytes()` o `export_run()` DEBE ser verificado y aceptado incondicionalmente por `verify_bundle()` de la misma versión de Calibre.*  
> *Todo paquete histórico válido con formato `freight-audit-bundle/v1` DEBE continuar siendo aceptado por `verify_bundle()`.*
