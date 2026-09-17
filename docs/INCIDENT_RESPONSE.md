# Respuesta a incidentes

Un incidente es un posible fallo de datos, semántica, cálculo, representación, seguridad o conservación. No hace falta confirmar daño para contener. Estos procedimientos no envían comunicaciones automáticamente ni ejecutan pagos/rechazos.

## IR-COMMON: obligatorio para cada clase

**Detectar:** cliente, checker, test, diferencia ciega, replay o reporte. Registrar síntoma y resultado esperado sin editar originales. **Primera acción:** suspender la confianza en la conclusión afectada y abrir carpeta privada `incidente-AAAA-MM-DD-NN`; asignar responsable de triage. **No hacer:** sobrescribir corridas, borrar evidencia, regenerar golden, ampliar tolerancia, reimportar encima de DB original o declarar que “pasa replay” descarta el bug.

**Preservar (ART-01):** originales y SHA256; DB con backup consistente si abre de forma segura, o copia forense de DB/WAL/SHM con aplicación detenida si hay corrupción; archivos de configuración completos; snapshot y audit.json; decisiones y último hash conocido externo; logs locales; wheel/sdist/código y dependencias realmente utilizados; manifest/reportes entregados; captura/UI y navegador cuando aplique. Guardar command line, hora UTC y zona local, SO, Python, permisos, seed/ejemplo reducido ficticio. No subir datos del cliente a GitHub/CI público. Si un archivo no se puede verificar, conservarlo igualmente como sospechoso.

**Histórico:** “invalidar” significa marcar **no apto para decisiones** en un registro externo append-only del incidente. No modificar `Finding.status`, `runs.result` ni hashes. Estados operativos: `sospechoso`, `confirmado_afectado`, `descartado_con_evidencia`, `sustituido_por_nueva_corrida`. No existe un endpoint nativo de invalidación o supersesión en 0.1.0. Registrar cada relación old_run→new_run con motivo y responsable. No atribuir afectación sólo porque comparte versión; tampoco excluir porque no fue posible reproducir.

**Alcance (BR-01):** consultar todas las DB del registro de clientes, filtro por artefacto/versiones y features configuradas/ejecutadas, acuerdos/reglas/monedas/tipos de fuente/fechas. Campo desconocido o run ilegible → candidato desconocido, nunca “no afectado”. Empezar amplio y reducir con evidencia. Fecha de creación no autentica nada; filtrar por período comercial exige examinar fechas de snapshot. Un inventario completo de clientes y DB no se puede inferir del programa.

**Diagnóstico base:** 1) anclar hashes; 2) comparar resultado conservado y salida observada; 3) localizar primera frontera donde diverge de OR independiente; 4) reproducir en copia con artefacto original; 5) reducir conservando una sola causa; 6) escribir expected antes de corregir; 7) clasificar alcance/contención. Una falla del entorno/oráculo se registra separada y no cuenta como producto correcto.

**Corrección base:** causa demostrada, cambio mínimo general, regresión que fallaba antes, tests de consumidores afectados y mutante relevante detectado. **Replay base:** reproducir original con motor original para diagnóstico; recalcular con corrección como nueva auditoría, conservando ambas. No prometer el mismo hash entre versiones distintas.

**Comunicación base:** avisar al responsable del cliente cuando recibió una salida posiblemente incorrecta, hubo pérdida/exposición o debe suspender decisiones; incluir run/período, campo afectado, certeza conocida/desconocida y acción segura. No esperar RCA perfecta para advertir una falsa certeza probable. No comunicar montos de recupero ni decisiones de pago automáticas.

**Cierre base:** alcance clasificado sin desconocidos omitidos; causa y corrección revisadas; evidencia antes/después; regresión y gate pertinente; historial intacto y nueva corrida vinculada; salidas corregidas entregadas a quienes recibieron las anteriores; backup/restore comprobado si hubo persistencia. **Postmortem base:** cronología, primera frontera defectuosa, por qué escapó el oráculo, reglas/artefactos/clientes/run_ids, daño confirmado/desconocido, decisiones de contención, evidencia de cierre y actualización de matriz/backlog. “No volvió a pasar” no cierra un incidente económico.

## Runbooks específicos

### IR-01 — FALSE FAIL

- **Severidad inicial / señales:** CRITICAL; FAIL contra cargo que contrato+hechos independientes respaldan, signo o precio objetado por cliente.
- **Primera acción / contención:** suspender uso de discrepancias del cliente afectado; no sugerir rechazo del cargo. Congelar nuevas conclusiones determinantes de esa feature; si causa desconocida, congelar todas las auditorías económicas hasta acotar.
- **Histórico / alcance:** marcar sospechosos FAIL, PASS y REVIEW que usan la misma operación matemática/versión/matching: el defecto puede actuar en ambos sentidos. BR-01, sin filtrar sólo signo positivo.
- **Diagnóstico exacto:** OR-01 confirma importe; OR-04 coteja A y atributos; OR-05 dibuja matching y fecha; OR-02 recalcula fórmula/tolerancia; comparar trace y fuente de cada término.
- **Corrección / regresión:** preservar el caso correcto como PASS o REVIEW/UNDETERMINABLE si en realidad faltaba respaldo. Añadir contraparte con discrepancia real y prueba a ambos lados de T; matar mutación de signo/límite.
- **Replay / comunicación / cierre:** artefacto original en copia; nuevas corridas de todos los candidatos confirmados. Aviso inmediato si el FAIL se entregó; cierre con explicación rectificada y ninguna auditoría sospechosa usada como verdad. ART-01 y postmortem base obligatorios.

### IR-02 — FALSE PASS

- **Severidad / señales:** CRITICAL; cargo objetivamente fuera de regla/tolerancia clasificado PASS o discrepancia perdida en resumen.
- **Primera acción / detención:** congelar aprobación basada en el producto del cliente/feature; si no se acota, todas las nuevas auditorías. No convertir el cargo en FAIL sin reconstruir respaldo; PASS no era autorización de pago.
- **Histórico / alcance:** incluir PASS y todos los casos donde el defecto podría ocultar exceso/defecto, archivos incompletos y monedas; OR-03 revela líneas desaparecidas.
- **Diagnóstico:** reconstruir filas aceptadas/rechazadas→partición→matching→versión→E/Δ/T. Comparar total externo: un cargo omitido nunca llega al core.
- **Corrección / regresión:** caso exacto con FAIL y vecindad PASS dentro de T, signo negativo, importación incompleta→REVIEW; no reducir indiscriminadamente tolerancias.
- **Replay / comunicación / cierre:** nuevas corridas y reconciliación de todas las salidas afectadas; informar al responsable cuando utilizó/recibió el resultado. Cierre con lista de PASS afectados revisada y documentación de decisiones que ya hubieran ocurrido; ART-01/postmortem base.

### IR-03 — Incertidumbre convertida en certeza

- **Severidad / síntomas:** CRITICAL; evidencia faltante, matching ambiguo o regla ausente acaba en PASS/FAIL o sumada como diferencia confirmada.
- **Primera acción / contención:** congelar conclusiones de la feature y métricas derivadas; si existe contador compartido, detener reportes económicos globales.
- **Histórico / alcance:** todos los estados y consumidores con missing_evidence, error de importación, overlap o razón de revisión; si metadata no conserva motivo, incluir candidatos amplios.
- **Diagnóstico:** comprobar requirements y asociaciones contra snapshot, seguido de status y resumen/UI. Distinguir core errado de etiqueta errada (IR-08).
- **Corrección / regresión:** misma A/E con y sin respaldo; sólo el caso completo puede confirmar Δ. Checker debe rechazar confirmed≠0 en REVIEW/UNDETERMINABLE/PASS.
- **Replay / comunicación / cierre:** recalcular grupos relacionados y preservar anterior; aviso a receptores de cifras presentadas como objetivas; cierre tras probar métrica0 para incertidumbre en todas las salidas. ART-01/postmortem base.

### IR-04 — WRONG MATCH

- **Severidad / síntomas:** CRITICAL; cargo asociado a remito, carrier, lote o período ajeno.
- **Primera acción:** congelar cliente o esquema de claves afectado, preservar lista completa de candidatos. No arreglar cambiando sólo el importe esperado.
- **Histórico / alcance:** configuración de keys/aliases/explicit/cardinality, fuentes y carriers; incluir grupos adyacentes que puedan compartir una línea ambigua.
- **Diagnóstico:** dibujar grafo C→S con OR-05, verificar cada clave original/resuelta y link explícito; comprobar si settlement/período se perdió.
- **Corrección / regresión:** claves confirmadas, tratamiento explícito del conflicto, prueba 40+60 parcial y controles de no match/2 candidatos/grupos solapados. Ambigüedad residual→REVIEW.
- **Histórico/replay:** marcar sospechosas asociaciones y totales; generar nueva corrida, no editar explicit del snapshot conservado. Comunicar si se usó conclusión; cierre con partición de cargos y grafo correcto, ART-01/postmortem base.

### IR-05 — WRONG AGREEMENT VERSION

- **Severidad / señales:** CRITICAL; precio corresponde a otra fecha, versión o evento contractual.
- **Contención:** congelar acuerdo/intervalo afectado, ampliando a todos los grupos consolidados que cruzan la frontera; no tomar “última tarifa” como fallback.
- **Diagnóstico:** original del contrato→date_field→fecha de cada S→intervalos inclusivos→regla. Precios distintos por versión para distinguir selección de coincidencia accidental.
- **Alcance / histórico:** acuerdos/versiones/fechas comerciales e importadores de fechas; metadata created_at no sustituye fecha de servicio. Marcar candidatos, no mutar V1.
- **Corrección / regresión:** inicio/fin/gap/overlap/open-ended, pickup distinto de service_date y N→1 mixto. Sin regla única→UNDETERMINABLE.
- **Replay / comunicación / cierre:** nuevas corridas con representación confirmada; aviso si se entregaron resultados; cierre con calendario manual y ejemplo contractual. ART-01/postmortem base.

### IR-06 — Dinero, precisión, unidad o redondeo

- **Severidad / señales:** CRITICAL; centavos distintos, pérdida de dígitos, moneda mezclada, signo invertido o dependencia de contexto.
- **Primera acción:** detener feature numérica; si operación común o moneda desconocida, uso económico total. Conservar números como texto, nunca pasarlos por float al diagnosticar.
- **Alcance:** artefacto+operador AST+escala+modo+moneda+importer, con desconocidos incluidos. No filtrar únicamente montos altos: ties pequeños también fallan.
- **Diagnóstico:** OR-02/01 y N01..N25; separar parseo, operación exacta, redondeo declarado y presentación.
- **Corrección / regresión:** positivo/negativo/zero/tie y vecinos, extremos y contexto ajeno. Si cálculo no cabe, UNDETERMINABLE explicado, nunca truncamiento.
- **Replay / cierre:** conservar original y recalcular bajo versión corregida; conciliar bruto/neto y salidas; comunicar diferencias técnicas sin llamar ahorro. ART-01/postmortem base.

### IR-07 — IMPORT CORRUPTION

- **Severidad / síntomas:** CRITICAL si altera significado silenciosamente; HIGH si rechaza y conserva el archivo con aviso. Raw/celda difiere del normalizado o faltan filas.
- **Primera acción / contención:** congelar importaciones del formato/mapping/version afectado y conclusiones de esos lotes. No intentar arreglar con replay normalizado.
- **Alcance / histórico:** todos los runs que usaron ese formato/mapping o importer desconocido; mismos bytes pueden generar resultados incorrectos consistentes. Revisar originales existentes.
- **Diagnóstico:** extraer celda sin el parser sospechoso, cotejar tipo/estilo/época/locale/hoja/linea física; controlar filas y total documental; reducir a archivo mínimo conservando mecanismo.
- **Corrección / regresión:** original→expected normalizado literal; pruebas de rechazo y controles válidos vecinos. Reimportar con importador corregido y comparar **snapshots**, luego nuevas auditorías.
- **Comunicación / cierre:** avisar sobre lotes parciales o cifras ya entregadas; cierre sólo con originales conciliados y nuevas salidas. No “arreglar” snapshot anterior. ART-01/postmortem base.

### IR-08 — REPORTING DIVERGENCE

- **Severidad:** CRITICAL si altera dinero/certeza/identidad; MEDIUM para aspecto sin significado. Señal: API/XLSX/HTML/DOM contradice run verificado.
- **Contención:** detener la salida afectada y su uso, sin congelar core si se demostró correcto; avisar a receptores. Preservar bytes/screenshots y filtros/página activa.
- **Diagnóstico:** ejecutar reconcile contra run anclado, verificar filas por identidad, moneda/escala, labels y generación/revisión de decisiones. JSON no es correcto sólo por ser JSON: primero invariantes/integridad.
- **Histórico / alcance:** versión del reportero/UI y exports entregados; no se conservan huellas de reportero en metadata antigua, ampliar ámbito hasta evidencia independiente.
- **Corrección / regresión:** generar nuevas representaciones del **mismo run** si core no cambió; probar texto exacto grande, labels y filas omitidas. No recalcular cargos por un error de CSS.
- **Cierre:** todos los consumidores reconciliados, reportes anteriores retirados de uso, decisiones posteriores preservadas; ART-01/postmortem base.

### IR-09 — NONDETERMINISTIC REPLAY

- **Severidad / señales:** CRITICAL ante mismo artefacto/snapshot con resultado distinto. Artefacto distinto y rechazo esperado es una incompatibilidad, no nondeterminismo confirmado.
- **Primera acción:** congelar nuevas conclusiones bajo artefacto sospechoso; preservar resultado original y el divergente por separado. No actualizar expected/hash.
- **Diagnóstico:** verificar bytes/input/result/artifact; dependencias/Python/contexto/orden; comprobar que proceso cargado coincide con disco; reproducir en proceso limpio sin red y comparar primer campo divergente.
- **Alcance:** versión/huella/environment/feature; si env no está registrado, candidatos desconocidos. No confiar en semantic_hash solo.
- **Corrección / regresión:** fixture mínimo y transformación responsable; prueba entre procesos/contextos/órdenes, artefacto original preservado. Si original se perdió, documentar que reproducibilidad histórica no pudo demostrarse.
- **Replay / cierre:** cerrar con repeticiones justificadas bajo condiciones distintas y evidencia de causalidad, no un loop de seeds. Nueva versión crea nuevos runs. Comunicación cuando afectó entregas; ART-01/postmortem base.

### IR-10 — HISTORICAL MUTATION

- **Severidad:** CRITICAL; snapshot/resultado cambia tras configuración o decisión, trigger eliminado o hashes no coinciden.
- **Contención:** detener escrituras de esa DB y conservar copia forense antes de abrir herramientas que creen schema/triggers. No restaurar encima de la única evidencia.
- **Alcance:** toda DB, versiones y backups desde última ancla confiable; otras DB si el defecto es de código compartido.
- **Diagnóstico:** comparar ancla externa, fuente/snapshot/result/cadena de decisiones; revisar transacciones, triggers y acceso directo. Cadena coherente no prueba que no haya truncamiento.
- **Corrección / regresión:** write-once, constraints/transacciones, tests de catálogos futuros y decisiones; restaurar a ruta nueva verificada. Historia alterada se marca sospechosa externamente.
- **Replay / cierre:** verificar copia anterior con artefacto correspondiente y nuevas auditorías sólo donde necesario; comunicar pérdida de confianza histórica; ART-01/postmortem base.

### IR-11 — PROVENANCE FAILURE

- **Severidad:** CRITICAL si impide respaldar conclusión; HIGH si referencia de presentación está mal pero originales íntegros y corregibles.
- **Primera acción:** suspender confianza del hallazgo/archivo; si transformación general afecta muchos, congelar importer. No inventar una fila aproximada.
- **Diagnóstico:** verificar documento SHA, hoja/columna/línea física/raw/mapping, constantes y relaciones trace→S/C. El documento puede existir y la celda apuntada ser incorrecta.
- **Alcance:** mapping/importer/archivo y todos sus consumidores; ledger desconoce importer→incluir.
- **Corrección / regresión:** corpus multilínea, columnas reordenadas, filas dispersas, constantes; reconstrucción exacta desde original. Si no se puede, conservar UNDETERMINABLE operativo sin editar finding histórico.
- **Replay / cierre:** reimportar/nueva corrida cuando cambia snapshot; si sólo vista, IR-08. Cerrar con navegación independiente hasta cada campo material y documento íntegro. Comunicar limitación si salida se entregó; ART-01/postmortem base.

### IR-12 — DATA LOSS / corrupción

- **Severidad:** CRITICAL para evidencia/historia; HIGH para export recreable con run intacto.
- **Contención:** detener escrituras DB/disco afectado; preservar DB/WAL/SHM/espacio/logs; no VACUUM, migrar ni copiar un archivo SQLite activo sin consistencia.
- **Diagnóstico:** en copia, SQLite quick_check, inventario de runs/fuentes/decisiones y anclas; localizar última copia completa y verificar restore a ubicación nueva.
- **Alcance:** corrida/transacción/dispositivo/período desde backup; falta de inventario implica alcance desconocido, no cero pérdidas.
- **Corrección / regresión:** crash/fault injection y rollback; backup verificable fuera del equipo; reexportar sólo si originales y run íntegros.
- **Replay / cierre:** auditorías restauradas verificadas; originales irrecuperables no se recrean ficticiamente. Avisar inmediatamente ante pérdida o detención; cierre con restore probado y pérdidas explícitas. ART-01/postmortem base.

### IR-13 — CROSS-CLIENT CONTAMINATION

- **Severidad:** CRITICAL; archivos/reglas/reportes de A aparecen o influyen en B.
- **Contención:** detener ambas DB/clientes y entrega de reportes; si origen compartido desconocido, todos. No borrar el documento ajeno antes de preservar la prueba de exposición.
- **Diagnóstico:** inventario externo cliente↔DB, fuentes/hashes, selección UI/configs y caché de tablas. IDs/carrier comunes no son identidad de cliente.
- **Alcance:** runs/reportes/destinatarios de ambas configuraciones; la metadata actual no contiene tenant autenticado.
- **Corrección / regresión:** DB y directorios separados; A/B/A con mismos IDs, tablas, distinto precio; si se necesita multitenancy real, diseñarlo explícitamente fuera de este plan mínimo.
- **Replay / cierre:** reimportar desde fuentes correctas, nuevas corridas y comunicación a afectados según exposición conocida; restaurar confianza con aislamiento demostrado y permisos. ART-01/postmortem base.

### IR-14 — SECURITY FILE INCIDENT

- **Severidad:** CRITICAL ante acceso/ejecución/exposición; HIGH para DoS acotado. Síntoma: canary modificado, proceso/red inesperados, límite omitido, archivo activo.
- **Contención:** detener servicio/procesamiento de archivos; aislar entrada y conservar bytes sin abrirlos con aplicación de escritorio. No reenviar archivo real a servicios online.
- **Alcance:** proceso, usuario local, carpetas alcanzables, DB/reportes; preservar logs OS además de ART-01.
- **Diagnóstico:** reducir con archivo sintético en proceso limitado/directorio temporal, frontera Host/Origin/token, XML/ZIP/path/symlink y permisos. Un error visible no descarta efectos previos.
- **Corrección / regresión:** allowlist/límites/escape/rutas contenidas y controles antes de efectos; canary intacto y sin red/escrituras fuera del destino.
- **Replay / cierre:** verificar integridad antes de restaurar operación; no hace falta recalcular si se demuestra que datos no cambiaron. Comunicar pérdida/exposición cuando corresponda; cierre con causa eliminada y alcance documentado. ART-01/postmortem base.

### IR-15 — UNKNOWN DOMAIN SEMANTICS

- **Severidad:** CRITICAL si ya produjo certeza falsa; HIGH si se detectó antes. Ejemplo: mínimo por remito interpretado por viaje o fecha distinta por componente.
- **Contención:** detener conclusiones del contrato/feature del cliente; no congelar otros si se demuestra independencia. No adivinar una práctica “normal”.
- **Diagnóstico:** devolver al responsable contrato/anexos y tres ejemplos: ordinario, frontera y excepción; preguntar unidad de obligación, fechas, evidencia y redondeo exactos.
- **Alcance / histórico:** configuraciones que heredaron el supuesto, no sólo código; runs previos quedan sospechosos hasta comparar con representación confirmada.
- **Corrección / regresión:** configuración nueva si cabe fielmente; abstracción general sólo si necesaria, con dos arquetipos y contraejemplo. Firma/confirmación contractual externa al test.
- **Replay / cierre:** nueva corrida con reglas confirmadas, comparación ciega; comunicar y registrar qué no se conocía. Cierre requiere confirmación humana y casos contractuales independientes, además del test. ART-01/postmortem base.

## Consulta de alcance implementable hoy

`scripts/qa.py impact --db COPIA.db --feature band --currency ARS` lee SQLite en modo de sólo lectura y produce candidatos `match`, `unknown` y excluidos con razón. Filtros combinan AND; feature busca configuración y ejecución, no sólo una traza que pudo cortarse antes del fallo. `--importer-hash` incluye históricos sin huella como unknown. `--agreement`, `--rule`, `--source-type`, `--engine-version` y `--engine-artifact` permiten estrechar. El registro de clientes debe aportar qué DB revisar; el script no adivina clientes a partir de label.

Mejora mínima propuesta para futuras corridas: manifest de ejecución externo autenticable con client_id asignado por operador, run_id, hashes de importador/reportero/app/dependencias/mappings, tipo de archivo y rango comercial, y ledger de incidentes/supersesión. No rellenar metadata histórica con el código instalado hoy. Esta entrega implementa la consulta conservadora, no una migración retroactiva de confianza.
