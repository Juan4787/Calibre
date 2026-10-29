# Motor 0.3.1 — recursos y entrega reproducible

Este documento describe la implementación. El estado efectivamente publicado/instalado se consulta en [CONTINUATION.md](CONTINUATION.md) y en [el recibo de etapa 3](qa-evidence/2026-10-29/stage3/receipt.json). No sustituye la auditoría final ni la aprobación contractual del cliente.

## Contratos conservados

La moneda, las fórmulas, los redondeos, las trazas, los cuatro estados de certeza y la separación entre resultado y decisión humana conservan la semántica 0.3.0. La comparación profunda de ambos golden sólo cambió engine_version: [evidencia](qa-evidence/2026-10-29/stage3/golden-review.json). El nuevo artefacto exige una nueva versión: para reproducir corridas históricas se conserva su entorno original. SQLite continúa en schema 2.

prepare_matching es una fase pura con un resultado tipado (acuerdos, operaciones e índices). Calcula un presupuesto estructural antes de copiar candidatos y construir resultados. El límite de 2.000.000 de unidades contempla indexación, ancho de asociaciones, expresiones, escaneo de tramos y expansión de evidencia. Es conservador: una configuración puede requerir dividir el lote aunque el equipo disponga de memoria. No altera reglas ni produce resultados parciales. Dividir conservando completas las operaciones, cargos y evidencia de cada obligación; separar una consolidación puede cambiar el problema económico y exige revisar el alcance.

Al persistir se coteja, con Fraction, la suma de cargos contra el facturado del resumen por moneda, además de repetir el motor. Así se detecta un bug sistemático del resumen que la repetición sola compartiría. No valida por sí mismo precios ni interpretación contractual. El listado de historial comprueba hashes de snapshot, resultado, metadata e identidad antes de mostrar importes; una alteración provoca rechazo. La apertura/migración clasifica errores de SQLite y mantiene su causa para diagnóstico; la regresión comprueba que una migración fallida no cambia schema ni deja tablas nuevas.

## Presupuestos explícitos

| Superficie | Límite/comportamiento |
|---|---|
| Archivo tabular | 25 MiB de entrada; se mantienen límites de filas/columnas existentes |
| Celdas expandidas | 1.000.000, control previo de dimensiones y durante CSV/XLSX; XLS antes de materializar Cell |
| Importación normalizada | 128 MiB, contabilización incremental de registros, incidencias y preview; aborto del archivo completo |
| Trabajo de asociación/cálculo | 2.000.000 unidades conservadoras, previo a pricing/trazas |
| Planilla | Límites nativos de Excel; presupuesto conservador de XML temporal de 256 MiB |
| Paquete portable | 500 MiB de miembros sin comprimir; se reservan originales antes del costo Excel |
| Vista contractual | Hasta 10 versiones, 20 reglas por versión, 10 tablas y 20 filas por tabla, con aviso explícito; configuración completa conservada |

Los presupuestos limitan representaciones/trabajo; no constituyen un máximo universal de RSS, tiempo o espacio libre del equipo. Cargas y algoritmos tienen expansiones diferentes. Los límites de entrada HTTP y de restauración del formulario siguen vigentes; restauración CLI admite una copia mayor dentro de su límite documentado.

## Reportes sin buffers completos de archivo

write_workbook usa Workbook(write_only=True), generadores de filas y estilos compartidos. Conserva ocho hojas, texto exacto, filtros, encabezados, ajuste y paneles inmovilizados. Limpia el XML temporal también al fallar. No trunca datos para satisfacer Excel: si sólo la planilla es irrepresentable o excede su presupuesto, el ZIP incluye una advertencia, audit.json completo y los originales. Un error de integridad, disco o paquete completo no se convierte en éxito.

write_bundle escribe a un stream, calcula hashes mientras escribe y procesa un original por vez. Primero produce un XLSX temporal completo y luego lo incorpora: no publica uno parcial. canonical_chunks produce exactamente los bytes UTF-8 del serializador canónico, agrupados en bloques. verify_bundle admite Path/stream y comprueba miembros por bloques; sólo materializa el JSON que debe devolver. La CLI verifica el ZIP desde archivo y extrae/exporta por copias acotadas, manteniendo el marcador de incompleto ante fallos.

HTTP prepara un archivo privado completo y lo sirve por bloques. TemporaryArtifactResponse elimina el temporal en finally, incluida desconexión. Desactiva la transferencia diferida de un pathname porque podría sobrevivir al cleanup. La descarga de backup aplica el mismo mecanismo. JSON de corrida evita la copia profunda del codificador de respuestas y conserva el documento exacto. Los helpers de bytes siguen disponibles para llamadores pequeños y explícitos. El run verificado, el JSON parseado y HTML aún residen en memoria; no se declara streaming integral del modelo.

## Dependencias y builds

requirements.lock y requirements-browser.lock mantienen las versiones anteriores y agregan hashes SHA-256 de todos los archivos de cada release obtenidos de su metadata oficial PyPI. No es un lock sólo Linux; pip selecciona el archivo compatible y comprueba su hash. La instalación con hashes se activa automáticamente al contenerlos y el instalador además exige --require-hashes. No confundir identidad de archivos con ausencia de vulnerabilidades. El bootstrap de Python/pip y la descarga del navegador requieren red; la auditoría de producto funciona localmente.

Regeneración deliberada, revisando el diff:

```sh
python3 scripts/lock_hashes.py requirements.lock requirements-browser.lock
```

scripts/build_reproducible.py ejecuta build --no-isolation con las herramientas fijadas; SOURCE_DATE_EPOCH procede del timestamp del commit concreto. Normaliza timestamps, orden, permisos/propietarios y cabeceras ZIP/tar/gzip sin modificar el contenido de miembros ni RECORD. verify_delivery construye dos git archive limpios y falla si difieren contenido O bytes; instala wheel y sdist fuera del checkout, comprueba pins/pip check/recursos/ejecución y conserva exactamente esos archivos. La garantía medida corresponde a ese commit, Python, zlib y toolchain registrados, no a cualquier plataforma/versión de compresor.

```sh
.venv/bin/python scripts/verify_delivery.py --output /tmp/entrega-0.3.1.json --artifacts-out /tmp/assets-0.3.1
```

Ambos destinos deben ser nuevos. No reconstruir al subir: publicar los archivos certificados y comprobar readback remoto. Para una release definitiva se usa el SHA concreto de main/tag. El gate Tier 4 ahora incluye la comprobación estricta de dos builds, además de smoke y navegador del wheel instalado. Los tags/paquetes anteriores conservan sus propias garantías históricas.

## Instalación Linux, actualización y reversión

El script de instalación pertenece al repositorio/sdist; no se ejecuta desde el wheel. Preparar/activar un wheel certificado conserva datos fuera del checkout:

```sh
python3 scripts/install_local.py --wheel /ruta/freight_audit-0.3.1-py3-none-any.whl --activate
systemctl --user status calibre-freight.service
```

Por defecto usa ~/.local/share/calibre, launcher ~/.local/bin/calibre-freight, unit de usuario calibre-freight.service y http://127.0.0.1:8765. --root, --service-name y --port permiten una instalación independiente. --no-service es sólo para un ensayo offline con todos los procesos que usen esas bases detenidos manualmente. No apuntarlo al servicio activo. Sin --activate prepara y prueba el entorno, sin cambiar datos/puntero/servicio.

La activación bloquea otra instalación concurrente, detiene el servicio, enumera la base principal y TODOS los clientes registrados, comprueba el registro y exige que sus DBs existan. Respalda cada base con SQLite backup, quick_check, foreign_key_check y huellas de filas; conserva un manifest privado con hashes y schema. Guarda configuración previa del launcher/unit y un recibo pendiente antes de migrar. Cada DB se abre/verifica con el Python nuevo y se cotejan sus filas históricas. Sólo entonces cambia current, configura/reinicia/habilita servicio y comprueba versión, artefacto y estado activo. El launcher limpia PYTHONPATH y el unit trabaja fuera del checkout con permisos privados.

Si falla la migración o la salud, conserva primero TODOS los archivos posteriores (incluidos clientes nuevos y auxiliares SQLite), restaura copias anteriores, configuración y puntero, reinicia/verifica la versión anterior y conserva un recibo de fallo. Una falla de recuperación deja el recibo pendiente y requiere investigación; no se simula una recuperación exitosa. La primera instalación no tiene versión anterior a la cual volver.

Reversión explícita de la última activación exitosa:

```sh
python3 scripts/install_local.py --rollback
```

Rechaza un puntero que ya no coincide con el recibo o un entorno anterior ausente. Conserva datos posteriores en backups/after-preserved-FECHA/ antes de restaurar. Los clientes nuevos conservan sus archivos, pero el registro anterior no los incluye: para recuperarlos, abrir/verificar una COPIA con el motor que la creó y usar restore-workspace como otro espacio, conservando la copia posterior. No fusionar bases ni descartar corridas nuevas. La reversión de schema exige la copia previa, nunca abrir una DB nueva con código antiguo a la fuerza.

Si se interrumpió el proceso y existe activation-pending.json, el siguiente intento exige recuperación explícita:

```sh
python3 scripts/install_local.py --recover
```

Mantener releases anteriores, backups, manifest y recibos privados. Respaldar fuera de este equipo es un paso del operador: una copia local no acredita recuperación ante pérdida del disco. El ensayo automático usa datos ficticios; no equivale al piloto de un cliente ni a Windows/Excel de escritorio.
