# Informe de Auditoría E2E: FASE 5 — Importación Adversarial y Fidelidad Documental

**Fecha de Cierre de Release**: 2026-09-17  
**Commit de Producción Sellado**: `ace3425aa4c73f6a4a104971323e4bd207ecbd5c`  
**Mensaje de Commit**: `fix(import): reject populated XLSX cells under blank headers`  
**Nuevo Baseline Criptográfico del Wheel**:
- Wheel: `dist/freight_audit-0.1.0-py3-none-any.whl`  
  SHA-256: `0d1b3c2ce3b8510e0ecd5d88e8a23ad4d0346de02e69059dd15c843f3c18419a`
- Tarball: `dist/freight_audit-0.1.0.tar.gz`  
  SHA-256: `b16045982de1c58dd1709b899fae77273ac555f6cd39e91a615404c6a8faa35b`

**Veredicto Final**: **FASE 5 CERRADA AL 100% — REVALIDACIÓN MULTI-FASE EXITOSA (62/62 F5 + G1-G6 F4 + SMOKE E2E F1)**

---

## 1. Resumen Ejecutivo y Ciclo de Release

Fase 5 evaluó la frontera de ingestión documental de Calibre (`src/freight_audit/importing.py`), demostrando fidelidad numérica y de provenance en 62 vectores causales prerregistrados.

El ciclo de resolución y release se completó con la máxima disciplina metodológica:
1. **Primera Pasada Observacional (Commit `8e308cf`)**:
   - Ejecución sin tocar producción (`git diff --exit-code src/freight_audit/` $\to$ 0).
   - Detección fiel del fallo `XLSX-15` (61/62 PASS), donde openpyxl rellenaba con `None` la fila de encabezados evadiendo la defensa de columnas huérfanas.
2. **Test de Regresión Permanente**:
   - Se añadió `test_xlsx_populated_cell_under_blank_header_is_rejected` a [tests/test_importing.py](file:///home/usuario/CascadeProjects/CALIBRE/tests/test_importing.py#L301-L306) para garantizar que el comportamiento quede protegido para siempre en la suite core.
3. **Commit Atómico**:
   - `fix(import): reject populated XLSX cells under blank headers` (Commit `ace3425`).
4. **Verificación Integral (`scripts/verify.sh`)**:
   - Ruff linting: PASS
   - Ruff format check: PASS
   - Mypy type-checking (`src` y `qa`): PASS
   - QA matrix check: PASS
   - Node JS syntax check: PASS
   - Pytest suite: **172 passed, 2 warnings** (100% PASS)
   - Python compileall: PASS
   - Python build (sdist + wheel): PASS
5. **Revalidación Multi-Fase en Clean-Room**:
   - **Fase 5 (Importación Adversarial)**: **62/62 PASS**.
   - **Fase 4 (Generalidad Contractual)**: Re-ejecución de G1 a G6, incluyendo **G3 en XLSX nativo con evidencia**: **100% paridad contra oráculo independiente**.
   - **Fase 1 (Smoke E2E Productivo)**: Re-ejecución completa en Chromium headless vía Playwright con exportación y servidor persistente: **Reconciliación 6 canales con 0 divergencias (SQLite = API = JSON = XLSX = HTML = UI)**.

---

## 2. Matriz de Resultados Finales por Subbloque

| Bloque | Descripción | Casos Totales | Iteración 1 (Observacional) | Iteración 2 (Cierre) | Tasa de Éxito Final |
|---|---|:---:|:---:|:---:|:---:|
| **5A** | Corpus Causal Prerregistrado | 62 | 62 / 62 | 62 / 62 | 100.0% |
| **5B** | CSV y Texto Estructurado | 20 | 20 / 20 | 20 / 20 | 100.0% |
| **5C** | XLSX y XML Adversarial | 18 | 17 / 18 | 18 / 18 | 100.0% |
| **5D** | Identidad y Provenance Celda a Celda | 6 | 6 / 6 | 6 / 6 | 100.0% |
| **5E** | Política de Rechazo Seguro | 10 | 10 / 10 | 10 / 10 | 100.0% |
| **5F** | Corpus Diferencial y Metamórfico | 8 | 8 / 8 | 8 / 8 | 100.0% |
| **TOTAL** | | **62** | **61 / 62 (98.4%)** | **62 / 62 (100%)** | **100.0%** |

---

## 3. Detalle Técnico de la Corrección y Regresión de `XLSX-15`

### 3.1. Causa Raíz
En archivos XLSX con columnas huérfanas sin encabezado, `openpyxl.load_workbook(read_only=True)` determina `max_column` por la fila más ancha y rellena la fila de encabezados con `None`, de modo que `headers` contiene `""` al final.
La condición anterior `if len(row) > len(headers)` no detectaba el exceso porque ambas listas medían 5 elementos, descartando silenciosamente la columna no rotulada.

### 3.2. Corrección en Producción ([importing.py:407](file:///home/usuario/CascadeProjects/CALIBRE/src/freight_audit/importing.py#L407-L413))
```python
has_extra_columns = (
    len(row) > len(headers) and any(cell.value not in (None, "") for cell in row[len(headers) :])
) or any(
    i < len(headers) and not headers[i] and cell.value not in (None, "") for i, cell in enumerate(row)
)
```

### 3.3. Test de Regresión Permanente ([test_importing.py:301](file:///home/usuario/CascadeProjects/CALIBRE/tests/test_importing.py#L301-L306))
```python
def test_xlsx_populated_cell_under_blank_header_is_rejected():
    data = xlsx_data([["id", "ref", "weight", "date"], ["S1", "0001", 12.5, "01/09/2026", "EXTRA"]])
    result = import_data(data, "extra.xlsx", mapping())
    assert result["accepted"] == 0
    assert result["rejected"] == [2]
    assert any("fuera de las columnas declaradas" in issue["message"] for issue in result["issues"])
```

---

## 4. Revalidación Cruzada contra Fases Previas

1. **Revalidación Fase 4 (Generalidad Contractual)**:
   - Archivo de prueba: `output/e2e/generality/test_cleanroom_generality.py`
   - G1 (Aritmética y combustibles): **100% paridad (3 findings)**
   - G2 (Ruta, vehículo y vigencia): **100% paridad (4 findings)**
   - G3 (**Lectura binaria XLSX nativo con evidencia**): **100% paridad (3 findings)**
   - G4 (Bandas continuas en USD): **100% paridad (4 findings)**
   - G5 (Consolidación N:1 y 1:N): **100% paridad (3 findings)**
   - G6 (Composición total de primitivas): **100% paridad (3 findings)**
   - Total findings reconciliados: **20 / 20 PASS**.

2. **Revalidación Smoke E2E Fase 1**:
   - Archivo de prueba: `output/e2e/test_e2e_productive.py`
   - Servidor real levantado sobre `e2e_audit.db` en puerto 8770.
   - Navegación Playwright Chromium: Carga de auditoría, ingestión de envíos y cargos, evaluación de reglas, registro de decisión humana, creación de Run 2 con evidencia, verificación de inmutabilidad de Run 1 y replay idéntico.
   - Reinicio de proceso: servidor recuperado contra SQLite persistente.
   - **Reconciliación material**: 6 canales sin divergencias:
     $$\text{SQLite} = \text{API} = \text{JSON} = \text{XLSX} = \text{HTML} = \text{UI}$$

---

## 5. Conclusión Formal

Con el nuevo commit `ace3425aa4c73f6a4a104971323e4bd207ecbd5c`, el nuevo wheel generado y la revalidación exitosa de las tres fases (F5, F4 y F1), **FASE 5 QUEDA FORMALMENTE SELLADA Y CERRADA AL 100%**.
El proyecto queda en posición óptima para abrir la **FASE 6 — Fault Injection y efectividad de defensas**.
