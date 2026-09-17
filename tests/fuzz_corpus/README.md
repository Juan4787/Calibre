# Corpus mínimo, fuente y expected separados

Tres archivos sintéticos pequeños validan el cableado del corpus: número argentino exacto, agrupador inválido rechazado y CSV multilínea con procedencia física. `manifest.json` declara el SHA de bytes LF, accepted/rejected y expected independientes. No se genera expected llamando al importador.

Para añadir caso: escribir bytes mínimos; anotar manualmente celdas/filas; calcular SHA256 con `sha256sum`; agregar manifest y ejecutar sólo `test_small_fuzz_corpus`. Conservar fuente original del incidente en almacenamiento privado, no aquí. Anonimizar preservando mecanismo de fallo. Nunca copiar datos reales a CI público.

Corpus XLSX/XLS más profundo queda especificado en QA_CASES.md/QA-11..17/QA-42: no está implementado por estos tres archivos. El test antiguo de bytes arbitrarios complementa corrupción básica, no reemplaza libros estructuralmente válidos.
