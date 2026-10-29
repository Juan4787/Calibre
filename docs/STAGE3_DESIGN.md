# Etapa 3 — decisiones y orden de implementación

Estado: en desarrollo, no es evidencia de que lo pendiente esté implementado. Instalación efectiva 0.3.0 conservada; rama `engineering/performance-0.3.1`. Contrastar siempre con CONTINUATION.md.

## Base medida y primeras regresiones

Benchmark de código idéntico a 0.3.0, 1.000 cargos, tres repeticiones medidas y warm-up del runner, todos los canales, watchdog y oráculo independiente. Mediana pipeline 21,9 s; motor 0,2466 s; pico máximo 181,74 MiB. Valores por etapa en stage3/baseline-0.3.0.json. No extrapolar a 100.000 cargos. El benchmark pide XLSX y después ZIP como dos operaciones: el export CLI normal ya generaba una sola planilla dentro del paquete.

Siete comprobaciones nuevas fallaron antes de modificar código (stage3-red.log, copia durable al cerrar etapa): escritura directa XLSX, presupuesto antes de construir una planilla imposible, ZIP a archivo verificable, listado de historial con importe alterado, control independiente de totales al persistir, presupuesto de normalización y de celdas expandidas. El caso de totales simula un bug sistemático del resumen: no demuestra que el motor sano produzca ese importe.

Primer cambio: write_workbook a stream, Workbook(write_only=True), filas generadas, estilos reutilizados y limpieza de XML temporales también al fallar. 20 pruebas dirigidas aprobadas (nueva fidelidad de celdas/filtros/estilos + almacenamiento/reportes anteriores). Todavía no tiene benchmark posterior, distribución ni publicación.

## Reportes y recursos

Mantener APIs de bytes por compatibilidad, pero implementar primitivas write_workbook/write_bundle hacia streams y usarlas en HTTP/CLI. JSON canónico incremental debe producir exactamente los mismos bytes que canonical; ZIP calcula hashes al escribir, procesa un original por vez y comprueba presupuesto durante la escritura. Reservar tamaños de fuentes antes del costo XLSX. Crear XLSX en archivo temporal completo antes de agregarlo al ZIP: ante límite Excel/XML, incluir advertencia + JSON/originales, nunca una planilla parcial. Mantener ocho hojas y todos los valores exactos/estados/trazas.

verify_bundle debe admitir bytes, Path o stream, comprobar manifest/entradas por lectura acotada y sólo materializar JSON necesario para devolver el run. La validación de fuentes no debe duplicar buffers ya comprobados contra el manifiesto. export_run debe producir ZIP temporal, extraer con copias acotadas y preservar marcador incompleto en fallos; los tests de rutas hostiles cambian el punto de inyección del helper de bytes al writer, sin eliminar su caso ni sus asserts.

HTTP debe servir archivos temporales con limpieza en finally incluso ante desconexión, sin cargar ZIP/XLSX enteros en Response. Mantener protección de loopback/Origin/token/CSP y errores humanos. Originales/JSON no se truncan para cumplir un límite de representación.

Limitar celdas expandidas antes de crear objetos tabulares y contabilizar registros/incidencias/preview durante normalización, con aborto del lote completo ante presupuesto. Usar constantes separadas y compartidas con Store.save_import; declarar que no constituyen una garantía universal de RSS. Considerar presupuesto de asociaciones/expresiones antes de construir trazas o listas cuadráticas, con error explícito del lote y sin resultados económicos parciales. Medir con las mismas tres repeticiones, no aprobar por rapidez aislada.

## Integridad y mantenibilidad

El listado actual calcula resumen/label con JSON de SQLite sin cotejar hashes: la prueba nueva reproduce el importe alterado mostrado. Verificar filas en forma secuencial (evitar fetchall de snapshots/resultados grandes), usando hashes de las serializaciones canónicas almacenadas y metadata/identidad; conservar lectura de formatos históricos. No atribuir autenticidad al operador por hashes.

Agregar a persistencia un cotejo racional independiente de suma de cargos frente al actual por moneda del resumen. Repetir audit no detecta por sí solo un bug sistemático. No sumar monedas ni inventar tarifas. Clasificar fallos de migración SQLite con recuperación humana, preservando rollback de DDL. El test antiguo de v1 inválida debe comprobar la nueva excepción clasificada y conservar los asserts de schema/imports intactos.

Refactorizar fases/estructuras de matching con tipos prudentes y funciones puras sólo con igualdad de valores/trazas/golden revisada; conservar el artefacto histórico 0.3.0. Una mejora de longitud no justifica reescribir el stack.

## Build, dependencias e instalación

Build normalizado a partir de SOURCE_DATE_EPOCH del commit concreto, wheel/RECORD sin modificar contenido, tar/gzip con metadata determinista. Dos builds de archives limpios deben coincidir también en bytes: el verificador tiene que fallar si no coinciden. Conservar exactamente los assets certificados, no reconstruir al subir. Para garantía desde tag, construir assets definitivos sobre el merge/tag concreto, registrar epoch/Python/zlib/toolchain y comprobar descarga remota.

Locks con hashes de todos los archivos admitidos de las versiones ya fijadas; no actualizar versiones sin necesidad ni generar un lock sólo Linux que rompa Windows. Fuente primaria para hashes: metadata oficial PyPI y verificación real de pip. Build sin aislamiento usa herramientas del entorno bloqueado; documentar bootstrap de pip y alcance de reproducibilidad, sin inventar ausencia de vulnerabilidades.

Actualizar instalador para administrar servicio/launcher y preservar TODAS las DBs de cliente registradas antes de migrar. No modificar bases demo ajenas. Ensayar instalación, upgrade, fallos y rollback en raíz aislada; en rollback conservar DB posterior y auxiliares, restaurar copias correctas y pointer anterior, no borrar corridas posteriores. Launcher debe limpiar PYTHONPATH (ya aplicado en instalación real 0.3). Verificar salud/versión/origen de código/historia tras reiniciar; no crear fixtures en DB operativa. Reconsultar uso real antes de actualizar: puede dejar de estar vacía.

## Cierre

PR protegido, CI exacta, artefacto instalado fuera del checkout, E2E real, readback remoto/local y recibo de etapa. Después auditoría final de todos los hallazgos originales y nuevos, incluyendo negativos, mutaciones, restauración e históricos. Cliente real y Windows/Excel del operador siguen requiriendo evidencia externa; no suplirlos con fixtures o un runner.
