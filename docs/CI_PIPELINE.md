# Arquitectura de CI / Regresión Automatizada (Fase 8)

Actualización 2026-09-22: los workflows instalan `requirements.lock` y `requirements-browser.lock`. Tier 1 incluye `scripts/browser_e2e.py` con Chromium; Tier 2 depende del job previo y no repite lint/build. Nightly exige 12 controles sanos antes de las 41 fallas. Release ejecuta Tier 1, reconciliación y E2E del wheel instalado, además del smoke. Las duraciones dibujadas abajo son objetivos históricos, no resultados medidos del pipeline actual. `mypy` se ejecuta con la configuración del proyecto, sin modo `strict` global. Los resultados actuales y sus límites están en [RIGOR_REVIEW.md](RIGOR_REVIEW.md).

> **Principio Rector:**  
> Conservar regresiones comprobables y bloquear ejecuciones incompletas. Las campañas históricas prueban sus casos y artefactos; no constituyen certificación global del producto.

---

## 1. Niveles de Ejecución (Tiers)

Para garantizar un ciclo de desarrollo ágil sin comprometer la exhaustividad de las defensas, el pipeline de CI se estructura en **cuatro niveles progresivos** con criterios de corte y tiempos de respuesta bien definidos:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 1: PR & Fast Gate (duración objetivo histórica < 90s)            │
│ Lints, Format, Types, Matrix, JS, Pytest, Build, Chromium              │
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
│ TIER 4: Release Checks & Clean-Room Wheel (objetivo < 4 min)          │
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
  3. `mypy src` & `mypy --explicit-package-bases qa scripts/qa.py`: Verificación de tipos con la configuración del proyecto.
  4. `python scripts/qa.py matrix --check`: Sincronización exacta de `docs/TEST_MATRIX.md` con los tests del repositorio.
  5. `node --check src/freight_audit/static/app.js`: Validez sintáctica del frontend vanilla.
  6. `pytest -q tests/`: Batería unitaria, de integración y regresiones; recuento vigente en `RIGOR_REVIEW.md`.
  7. Compilación de `src` y runners E2E, excluyendo entornos/caches, y `python -m build`: verificación de empaquetado.
  8. `scripts/browser_e2e.py`: flujo de Chromium con datos sintéticos, comparaciones exactas y evidencia por corrida.

### Tier 2: CI Completa (`ci`)
* **Disparador:** Pull requests hacia `main` y merge a `main`.
* **Objetivo:** Garantizar que ningún cambio afecte los invariantes estructurales ni la reconciliación exacta multicanal sobre fixtures contractuales oficiales.
* **Controles ejecutados:**
  1. El workflow exige que el job **Tier 1** del mismo commit haya terminado correctamente.
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
  3. Controles sanos y luego `python output/e2e/fault_injection/run_directed_faults.py`: 41 fallas (33 P0 y 8 P1), exigiendo detección registrada y salida no cero si una falla sobrevive o la infraestructura impide comprobarla.
  4. `python output/e2e/import_adversarial/test_import_adversarial.py --output-dir DIRECTORIO_NUEVO`: exige los 62 casos distintos de importación aprobados y código sin cambios durante la corrida; conserva procedencia real y resultados sin reemplazar una campaña anterior.
  5. `python scripts/browser_e2e.py`: Chromium, auditoría real con datos sintéticos, decisiones sucesivas, evidencia, historial, replay, descarga JSON, celdas exactas y todas las páginas. SQLite se ejercita a través del servicio y los tests de almacenamiento; no se declara un lector SQL independiente en este runner.

### Tier 4: Release Gate (`release`)
* **Disparador:** Push de tags con formato `v*` (ej. `v0.1.0`) o disparo manual de release.
* **Objetivo:** Comprobar el código actual y ejecutar smoke/E2E contra el wheel instalado en un entorno nuevo. Los checks ejecutados no constituyen certificación completa del producto.
* **Controles ejecutados:**
  1. **Verificación de árbol limpio:** `git status --porcelain` debe estar 100% vacío (sin archivos sin seguimiento ni modificaciones).
     Después se ejecutan Tier 1 y la reconciliación de ambas fixtures sobre ese código.
  2. **Build canónico:** Generación de `.whl` y `.tar.gz` desde el commit limpio (`git rev-parse HEAD`).
  3. **Registro criptográfico:** Cálculo y emisión en log de los hashes SHA-256 de los artefactos en `dist/`.
  4. **Entorno clean-room aislado:** Creación de un virtualenv temporal efímero en `/tmp` con `pip` actualizado.
  5. **Instalación del Wheel:** Instalación directa y aislada del `.whl` empaquetado.
  6. **Smoke test fuera del checkout:** Ejecución de `scripts/smoke_wheel.py` desde `/tmp` exigiendo que `freight_audit.__file__` pertenezca al `site-packages` del wheel instalado, validando:
     - Servicio HTTP y assets estáticos (`/`, `/static/app.js`, `/static/favicon.svg`).
     - Creación de base SQLite efímera y ejecución de auditoría demo con recuentos deterministas (`34 PASS`, `2 FAIL`, `6 REVIEW`, `4 UNDETERMINABLE`).
     - Replay transaccional inmutable (`/api/runs/{id}/replay` -> `identical: true`).
     - Exportación de bundle ZIP y verificación de integridad criptográfica vía `verify_bundle`.
  7. **E2E del wheel:** `scripts/browser_e2e.py --installed-root SITE_PACKAGES` exige igualdad de archivos con el código revisado y opera el navegador contra el producto instalado.

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

# Nivel 4: Verificación de release y prueba del wheel
bash scripts/run_ci_tier.sh release
```

---

## 5. Mapeo de Workflows de GitHub Actions

| Archivo de Workflow | Disparador | Nivel Ejecutado |
|---|---|---|
| `.github/workflows/ci.yml` | Push & PR a `main` | `tier1-pr` y `tier2-ci` |
| `.github/workflows/nightly.yml` | Cron `0 3 * * *` / Manual | `tier3-nightly` |
| `.github/workflows/release.yml` | Tags `v*` / Manual | `tier4-release` |
