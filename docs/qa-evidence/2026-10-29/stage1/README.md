# Recibo de etapa 1: 0.2.0

Datos completamente ficticios. Los archivos distinguen prueba causal antes/después, suite, mutaciones, corpus, multicanal y navegador. `receipt.json` contiene la huella del producto; no constituye por sí solo una publicación ni validación de un cliente real. El estado operativo actual está en `docs/CONTINUATION.md`.

La primera campaña de mutaciones dejó M16 vivo porque su fixture dejó de representar una consolidación corroborada bajo la nueva política. Se conservó el diagnóstico en la bitácora, se corrigió la precondición del fixture y se repitió **toda** la campaña: 20/20 detectados mediante sus assertions causales. No se contó ese primer resultado como aprobado.

El primer E2E encontró que la nueva fila de procedencia del XLSX no estaba incluida en el verificador. Se amplió el cotejo explícito conservando compatibilidad histórica y se repitió el recorrido completo, con resultado satisfactorio. No se silenciaron diferencias económicas ni se excluyó la fila nueva.

Comandos principales:

```bash
.venv/bin/pytest -q tests/test_audit_hardening.py
.venv/bin/pytest -q
.venv/bin/python scripts/qa.py mutate --execute
.venv/bin/python output/e2e/import_adversarial/test_import_adversarial.py --output-dir DIRECTORIO_NUEVO
.venv/bin/python scripts/browser_e2e.py --output-dir DIRECTORIO_NUEVO
bash scripts/verify.sh
```

Los golden de demo y segundo cliente se compararon antes de actualizar: sólo cambia `engine_version` de 0.1.2 a 0.2.0. Se conserva la evidencia histórica de versiones anteriores sin reescribirla.
