# Arquitectura de CI / Regresión Automatizada (Fase 8)

> **Principio Rector:**  
> Convertir el baseline verificado y certificado manualmente a lo largo de las Fases 1 a 7.5 en un sistema de ejecución automática e implacable que impida que futuros commits degraden silenciosamente las propiedades algebraicas, económicas y documentales demostradas.

---

## 1. Niveles de Ejecución (Tiers)

Para garantizar un ciclo de desarrollo ágil sin comprometer la exhaustividad de las defensas, el pipeline de CI se estructura en **cuatro niveles progresivos** con criterios de corte y tiempos de respuesta bien definidos:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 1: PR & Fast Gate (< 90s)                                          │
│ Lints, Format, Types, Sync Matrix, JS Syntax, Pytest Suite, Build       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 2: Full CI Semantic Gate (< 3 min)                                 │
│ Hypothesis Profile CI (100 ex), INV-01..INV-29, Multichannel Reconcile   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 3: Nightly Defense Sweep (< 8 min)                                 │
│ Hypothesis Nightly (1000 ex), Mutants M01..M10, Faults (33 P0 + 8 P1), │
│ Adversarial Import Corpus (62 casos)                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │ (On Release Tag 'v*')
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 4: Release Gate & Clean-Room Wheel Certification (< 4 min)         │
│ Clean Git Tree, Build .whl/.tar.gz, SHA-256 Baseline, Clean-Room Venv,  │
│ Zero-Source Smoke Test (Installed Package in Isolated /tmp)            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detalle de los Niveles

### Tier 1: PR / Cada Push (`pr`)
* **Disparador:** Cada pull request hacia `main` y cada commit pusheado a ramas activas.
* **Objetivo:** Detectar errores funcionales, de sintaxis, tipeo o formato en menos de 90 segundos antes de mezclar código.
* **Controles ejecutados:**
  1. `ruff check src tests scripts qa`: Control de estilo y linter estricto.
  2. `ruff format --check src tests scripts qa`: Consistencia tipográfica y de formato.
  3. `mypy src` & `mypy --explicit-package-bases qa scripts/qa.py`: Verificación estricta de tipos.
  4. `python scripts/qa.py matrix --check`: Sincronización exacta de `docs/TEST_MATRIX.md` con los tests del repositorio.
  5. `node --check src/freight_audit/static/app.js`: Validez sintáctica del frontend vanilla.
  6. `pytest -q tests/`: Batería completa unitaria y de integración (174 tests).
  7. `python -m compileall -q src` & `python -m build`: Compilación de bytecode y verificación de empaquetado.

### Tier 2: CI Completa (`ci`)
* **Disparador:** Pull requests hacia `main` y merge a `main`.
* **Objetivo:** Garantizar que ningún cambio afecte los invariantes estructurales ni la reconciliación exacta multicanal sobre fixtures contractuales oficiales.
* **Controles ejecutados:**
  1. Todos los pasos de **Tier 1**.
  2. `QA_PROFILE=ci pytest -q tests/`: Batería property-based con Hypothesis configurada a 100 ejemplos por invariante/propiedad.
  3. `python scripts/ci_reconcile_fixtures.py`:
     - Auditoría completa de `fixtures/project.json` y `fixtures/second-client/project.json`.
     - Verificación estricta de los 29 invariantes (`INV-01` a `INV-29`) con hashes y provenance.
     - Exportación de bundle ZIP portátil y reconciliación cruzada exacta (`reconcile`) entre JSON, XLSX y HTML.

### Tier 3: Nightly Sweep (`nightly`)
* **Disparador:** Ejecución cron diaria (03:00 UTC) o manual (`workflow_dispatch`).
* **Objetivo:** Prospección exhaustiva, fuzzing estocástico profundo y verificación de resiliencia ante mutaciones y fallas inyectadas sin ralentizar el flujo diario de PRs.
* **Controles ejecutados:**
  1. `QA_PROFILE=nightly pytest -q tests/test_qa_infrastructure.py`: Fuzzing intensivo con Hypothesis a 1000 ejemplos por invariante.
  2. `python scripts/qa.py mutate --execute`: Inyección y ejecución activa de mutaciones semánticas (`M01` a `M10`), exigiendo 100% de aniquilación (`killed`).
  3. `python output/e2e/fault_injection/run_directed_faults.py`: Suite dirigida de 41 fallas (33 P0 y 8 P1) a través de detectores agnósticos independientes (`invariants`, `reconcile`, `manifest_verifier`), exigiendo 100% de detección.
  4. `python output/e2e/import_adversarial/test_import_adversarial.py`: Batería de 62 vectores adversariales de importación (CSV, XLSX, fórmulas, XML, desplazamientos y límites).
  5. `python output/e2e/test_e2e_productive.py`: Ciclo de vida completo E2E en Chromium headless con Playwright, auditoría real, decisiones humanas, inmutabilidad de runs, replay y reconciliación exacta de 6 canales (SQLite = API = JSON = XLSX = HTML = UI).

### Tier 4: Release Gate (`release`)
* **Disparador:** Push de tags con formato `v*` (ej. `v0.1.0`) o disparo manual de release.
* **Objetivo:** Certificar que el artefacto que se distribuye al usuario final es idéntico al validado y funciona de manera autónoma en un entorno clean-room sin acceso al árbol fuente (`src/`).
* **Controles ejecutados:**
  1. **Verificación de árbol limpio:** `git status --porcelain` debe estar 100% vacío (sin archivos sin seguimiento ni modificaciones).
  2. **Build canónico:** Generación de `.whl` y `.tar.gz` desde el commit limpio (`git rev-parse HEAD`).
  3. **Registro criptográfico:** Cálculo y emisión en log de los hashes SHA-256 de los artefactos en `dist/`.
  4. **Entorno clean-room aislado:** Creación de un virtualenv temporal efímero en `/tmp` con `pip` actualizado.
  5. **Instalación del Wheel:** Instalación directa y aislada del `.whl` empaquetado.
  6. **Smoke test fuera del checkout:** Ejecución de `scripts/smoke_wheel.py` desde `/tmp` exigiendo que `freight_audit.__file__` pertenezca al `site-packages` del wheel instalado, validando:
     - Servicio HTTP y assets estáticos (`/`, `/static/app.js`, `/static/favicon.svg`).
     - Creación de base SQLite efímera y ejecución de auditoría demo con recuentos deterministas (`34 PASS`, `2 FAIL`, `6 REVIEW`, `4 UNDETERMINABLE`).
     - Replay transaccional inmutable (`/api/runs/{id}/replay` -> `identical: true`).
     - Exportación de bundle ZIP y verificación de integridad criptográfica vía `verify_bundle`.

---

## 3. Restricciones y Políticas Innegociables

1. **Cero tests flaky:**  
   No se admiten fallas intermitentes ni reintentos automáticos como sustituto de corrección. Todo test inestable es tratado como defecto del test o del sistema y debe corregirse o desincorporarse justificadamente.
2. **Separación estricta de cargas:**  
   Las pruebas estocásticas largas (1000 iteraciones) y las inyecciones de mutación/fallas viven en Nightly; la validación de empaquetado vive en Release. Esto preserva un Tier 1 ágil (<90s) y evita la fatiga o desatención de la CI.
3. **Validación del artefacto real empaquetado:**  
   La prueba final de release no ejecuta código del repositorio (`src/`), sino que instala el archivo `.whl` en una ruta limpia y ejecuta las verificaciones funcionales contra el paquete compilado.

---

## 4. Ejecución Local Reproducible

Los desarrolladores y auditores pueden ejecutar exactamente los mismos pasos de CI de forma local mediante el script orquestador:

```bash
# Nivel 1: Rápido para commits y PRs
bash scripts/run_ci_tier.sh pr

# Nivel 2: Verificación completa de invariantes
bash scripts/run_ci_tier.sh ci

# Nivel 3: Batería exhaustiva nocturna
bash scripts/run_ci_tier.sh nightly

# Nivel 4: Certificación de release y prueba del wheel
bash scripts/run_ci_tier.sh release
```

---

## 5. Mapeo de Workflows de GitHub Actions

| Archivo de Workflow | Disparador | Nivel Ejecutado |
|---|---|---|
| `.github/workflows/ci.yml` | Push & PR a `main` | `tier1-pr` y `tier2-ci` |
| `.github/workflows/nightly.yml` | Cron `0 3 * * *` / Manual | `tier3-nightly` |
| `.github/workflows/release.yml` | Tags `v*` / Manual | `tier4-release` |
