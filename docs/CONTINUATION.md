# Continuidad obligatoria — estado actual

Leer después de cada compactación, junto con AGENTS.md, STAGED_HARDENING_2026_10_29.md y el recibo de la etapa activa. Historial completo, incluidos fallos/correcciones y decisiones: [WORKLOG_2026_10_29.md](WORKLOG_2026_10_29.md). No confundir sus entradas cronológicas antiguas con pendientes actuales.

## Encargo y autorización

Implementar todo el plan auditado por etapas, auditar cada una, publicar en GitHub + instalación local y terminar con auditoría final. El usuario confirmó que NO existe una instalación en uso: se creó una nueva con DB vacía. No promover las cinco bases demo/QA. El usuario pide documentación sin huecos y directrices que se relean tras cada compactación. Publicar/mergear/instalar ya está autorizado; no repetir preguntas de permiso rutinarias. Último mensaje: «segui».

No hay originales/contratos/verdad de un cliente real ni Windows/Excel del operador. No inventar esos datos ni declarar aprobadas esas validaciones. No usar agentes secundarios sin instrucción explícita aplicable. Validaciones pesadas secuenciales en este host.

## Estado de GitHub y código

- Repo: Juan4787/Calibre; cwd /home/usuario/CascadeProjects/CALIBRE.
- Rama local recién creada: **engineering/performance-0.3.1**, desde main **7724b5ad19247df16e9a2e017b16c6e8498d12ac**. Se inicia etapa 3; versión fuente en desarrollo **0.3.1** (sin commit de producto); instalación efectiva 0.3.0 inalterada. La bitácora histórica íntegra está conservada en WORKLOG.
- Etapa 1, 0.2.0: entregada. PR #1 main 30d774c; release https://github.com/Juan4787/Calibre/releases/tag/v0.2.0. Corrección de aislamiento CI, PR #2/main 7dbc16d: release manual 40833070930 y nightly 40851752374 aprobados. Evidencia stage1/.
- Etapa 2, 0.3.0: **PR #3 MERGED**, main 7724b5a. Head revisado **7fc3f39**: CI **40924686583**, ambos checks passed. Árbol de main y del head iguales: 2e009bbee7a9d4815b6eb6809963a24ae8a40c6d.
- Tag **v0.3.0** creado y publicado sobre main 7724b5a. Release **PUBLICADO**, id **428211062**, https://github.com/Juan4787/Calibre/releases/tag/v0.3.0, con cuatro assets certificados.
- CI de main **40925405676** y gate completo de release del tag **40925586805**: **ambos PASSED** antes de publicar y activar. Las protecciones de main siguen strict + 2 checks, aplica admins, PR obligatorio, sin force push/deletion.
- Conector GitHub no tiene permisos de escritura suficientes (403 previo); se usa gh autenticado Juan4787 ADMIN. gh pr edit falla por projectCards deprecado: body actualizado por **gh api PATCH /repos/Juan4787/Calibre/pulls/3** con JSON de archivo. Merge REST con sha exacto evita cambiar head accidentalmente. No imprimir tokens.
- Netlify es una integración externa no configurada por nosotros; raíz y /api/session devolvían 404. Check verde de deploy NO acredita backend ni app SaaS. Destinos autorizados son GitHub/local.

## Etapa 2 comprobada

- Implementación 3df0785; distribución desde árbol limpio **29cd2bc184262c8072cf7d26db2ed227c12d0865**; cambios siguientes sólo runner/recibos, producto idéntico. Archivos y contratos: docs/ENGINE_0_3_0.md.
- **330 pruebas**, Ruff/formato/tipos/matriz/JS/compile/build; **62/62 corpus**; **20/20 mutaciones detectadas**; E2E real escritorio + 390px. Gate canónico scripts/verify.sh.
- 36.000 operaciones / **un cargo**, 36.001 registros cotejados: request 1.480 bytes vs 48.528.135 con registros; facturado/esperado 100 y diferencia 0, replay idéntico. Repro scripts/audit_operations.py; 41,489 s en este host. No extrapolar a 36.000 cargos o exportación.
- Copia creada por wheel 0.2 instalado, migrada con 0.3: identidad/resultados/metadata/decisiones preservados; ZIP viejo verificado; wheel viejo rechaza v2 y reproduce backup v1 intacto. Nunca se migró producción durante ese ensayo.
- Corpus y fuente E2E finales pasaron. Dos fallos CI del runner (61109c4/run40922533991 y f2cbe37/run40923753720) documentados en stage2/CI_READINESS.md. El placeholder coincidía con el substring de validación; se exige 32/46 filas y paso visible. route.fetch omitía el contenido del file multipart (0 bytes, 422): ahora se retiene y libera **la solicitud original** mediante route.continue_(), con 200 obligatorio y prueba del guard mientras cargos siguen pendientes. No se relajaron asserts ni aumentaron timeouts.
- Último E2E instalado aprobado: **stage2-installed-browser-original-request/result.json**, Python real de releases/0.3.0. Recibo durable stage2/installed-browser.json. Playwright corre en entorno QA; --runtime-python selecciona Python real del backend. Sólo dos 503 intencionales de recuperación, sin excepciones JS/CSP.
- Evidencia pública durable: docs/qa-evidence/2026-10-29/stage2/. Receipt actualizado: publicado/activo, CI de PR/main/release y readback remoto preservados; mantiene el historial de fallos del runner.

## Instalación efectiva y assets

- **ACTIVA 0.3.0**, servicio usuario calibre-freight.service habilitado/activo, http://127.0.0.1:8765.
- Root /home/usuario/.local/share/calibre (700); current → releases/0.3.0. DB workspaces/default/audit.db (600), schema 2. Readback de activación: **0 corridas, 0 fuentes, 0 decisiones**. Volver a verificar tras detener antes de actualizar.
- Launcher /home/usuario/.local/bin/calibre-freight fija esa DB; unit /home/usuario/.config/systemd/user/calibre-freight.service. systemctl --user stop/start/status calibre-freight.service. Conservar entorno 0.2 y backups; no tocar .local/*.db del repo.
- Instalada y activa: **releases/0.3.0**. Smoke y E2E fuera del checkout aprobados. Wheel SHA **c682f5fa639c2f36628fa2fa149486673823e387ca4ccf55f66ee3d5a4871d07**. Artifact hash de motor **fdd667513b48127a6a1c2e1475e05a6c27326e30d82841851d7777db7a8e702f**.
- Assets exactos certificados: **/tmp/calibre-implementation-20261029-CvSz5k/stage2-assets/**: wheel anterior, sdist SHA **119a3b2eff2ca5b91bb8cd8dbd26298cb137ace71e595e1644549626304e192d**, delivery-verification.json SHA **44b3ee7c915da5bfd73704cc1624d82c8789866649c6eecf6e2f34ba445987f4**, SHA256SUMS.txt. No reconstruir/reemplazar estos archivos al publicar 0.3. Dos builds de contenido igual; garantía binaria estricta pendiente etapa 3.
- Release remoto tiene assets exactos. Descarga readback terminada: hashes y bytes de los CUATRO archivos iguales a assets certificados, recibo stage2/remote-readback.json. Carpeta /tmp/calibre-implementation-20261029-CvSz5k/stage2-readback/.
- Copia de DB real para preflight, sólo temporal: stage2-production-preflight.db; migrada/verificada sin tocar original. Recibo stage2-production-preflight.json. Los backups originales son privados; no agregarlos al repo.

## Cierre efectivo de etapa 2

Activación 2026-10-29T17:59:21Z. Servicio activo, listener sólo 127.0.0.1:8765, HTTP200, health 0.3.0/schema2/artifact esperado y JS exacto. Conteos y hashes de filas históricas preservados (0 corridas/fuentes/configs/decisiones). PID inicial 204961: no asumir vigente. No se cargaron fixtures en la base operativa.

Backups schema1 intactos/verificados en root/backups/: before-0.3.0-cutover-20261029T175920403421Z.db (SHA bb16bcb524b077a0ced74d23962d7b7b6cfb47c40e8a50ced3309928f6522f84) y before-0.3.0-20261029T175920534065Z.db (del instalador). Conservar releases/0.2.0. El launcher ahora hace unset PYTHONPATH para impedir resolver código del checkout al iniciar. El primer helper manual de backup falló porque la carpeta backups aún no existía; creó carpeta privada y repitió antes de migrar. El instalador ya crea esa carpeta por sí mismo. Ningún dato se perdió ni se restauró para pasar pruebas.

Rollback: detener servicio, preservar DB posterior y sus archivos auxiliares, restaurar copia v1 verificada, cambiar current a releases/0.2.0 y reiniciar/verificar. No abrir DB v2 con motor 0.2 ni borrar cambios posteriores. Actualización/reversión automatizada de TODAS las bases de cliente pendiente etapa 3.

## Próxima acción exacta

1. Conservar este cierre de etapa2 y WORKLOG en commit de documentación sobre engineering/performance-0.3.1; no alterar el tag 0.3 ni reconstruir sus assets.
2. Leer etapa3 del plan y recibo stage3/receipt.json. Crear regresiones de recursos/reportes/reproducibilidad antes de cambiar producto, fijar baseline de benchmark1k/3reps de 0.3 instalado o código idéntico. Ejecutar trabajos pesados secuencialmente.
3. Cambiar versión a 0.3.1 al implementar, refactor prudente con referencia/golden revisada, reportes progresivos/presupuestos, locks con hashes, build normalizado e instalación/reversión integral. Conservar 0.3 y sus datos; verificar DB real nuevamente antes de cualquier actualización porque puede usarse desde ahora.
4. Publicar etapa3 por PR protegido y artefactos concretos verificados, luego auditoría final completa con recibos y límites explícitos. No declarar cierre global por tests verdes.

## Etapa 3 y auditoría final pendientes

Plan vinculante: STAGED_HARDENING_2026_10_29.md. Implementar reportes progresivos/generadores y estilos reutilizados, presupuestos medidos y límites previos; builds reproducibles y locks con hashes; actualización/reversión integral (incluye todas las bases de cliente); refactor prudente de fases/resultados tipados, conservando precios/trazas. Ejecutar benchmark1k/3reps comparable, controles semánticos/causales/mutaciones y distribución instalada/remota. No iniciar campañas enormes en este host sin verificar capacidad.

Revisiones a investigar durante etapa3/final, aún NO implementadas ni fallos actuales reproducidos: list_runs extrae resumen/label sin verificar hashes (deuda ya explícita QA-31); errores de migración SQLite crudos en CLI; presupuesto de trabajo antes de construir trazas/candidatos enormes; comparación del resumen contra control externo al conservar además del cotejo de inputs. No confundir estas ideas con evidencia de un importe incorrecto actual. API y GUI no son SaaS/multiusuario.

Final: reabrir cada hallazgo original con evidencia nueva, cruzar API/UI/CLI/reportes/historia/fuentes/restore/artefactos publicados, indicar riesgos/exclusiones reales. Cliente real/verdad independiente y Windows/Excel del operador siguen pendientes externos; no simular certificación. Actualizar docs para que quien retome tenga comandos, hashes, CI, backups y siguiente acción sin huecos.

## Inicio de implementación de etapa 3 (después de entrega efectiva)

- Cierre documental etapa2 publicado en rama engineering/performance-0.3.1, commit **620296f**; push aprobado. Main/tag0.3 no se alteraron. No hay procesos QA largos en curso.
- Baseline actual de código 0.3.0: **1k cargos / 3 reps medidas**, oráculo íntegro; mediana pipeline **21,9 s**, motor **0,2466 s**, pico **181,74 MiB**. Recibo stage3/baseline-0.3.0.json. Temporales /tmp/.../stage3-baseline/. No tocar CSVs/DB generados ni publicarlos.
- tests/test_resource_delivery.py nuevo: **7 fallos rojos** antes del cambio; causal-red.log preservado. Prueban interfaces de archivo, budget antes de Excel, listado alterado, conservación independiente de totales, límite normalizado y de celdas. Son presupuestos y fallos simulados controlados, no evidencia de OOM ni importe sano erróneo.
- Primer cambio local SIN commit: **reporting.py** contiene write_workbook(write_only=True), estilos reutilizados, generadores de filas y cleanup de XML temporales. wrapper workbook_bytes conserva compatibilidad. Nuevas y existentes dirigidas: **20 passed** en stage3-workbook-directed.log. No se ejecutó suite completa ni benchmark posterior ni paquete de estos cambios.
- Únicos cambios de producto tras 620296f hasta este punto: reporting.py. tests/test_resource_delivery.py y este diseño/recibos también sin commit. Fuente todavía 0.3.0: cambiar a 0.3.1 al continuar, revisar golden sólo versión tras comparar resultados. Backend operativo aislado en releases/0.3 no usa PYTHONPATH del checkout.
- Diseño concreto y dependencias: **docs/STAGE3_DESIGN.md**. Leerlo al retomar antes de continuar el writer.
- Próximo cambio exacto: canonical_chunks idéntico a canonical, write_bundle a stream con budget progresivo y fuentes de a una; verify_bundle admite Path/stream; export_run usa temporales/copias acotadas y conserva marcador/rutas seguras. Luego presupuesto importador, integridad de listado/totales, build/locks e instalador. Todos los 7 tests deben pasar sin debilitar existentes. Evitar editar módulos del artifact mientras un test/benchmark/E2E del checkout esté corriendo: RUNNING_ARTIFACT_HASH detecta cambios deliberadamente.


## Estado actual que sustituye las primeras entradas de implementación

- Fuente local 0.3.1 sin commit; instalación activa continúa 0.3.0. Después de 620296f se agregaron canonical_chunks, generadores XLSX, ZIP/CLI/HTTP a archivos temporales, limpieza ante desconexión, límites de celdas y normalización, cotejo independiente de suma facturada con Fraction, listado con verificación de hashes y errores de migración clasificados con causa preservada. prepare_matching es fase pura tipada, presupuesto estructural previo a expandir candidatos/cálculos (2M unidades; no garantía de RSS).
- Regresiones de recursos: siete rojas iniciales y una adicional de presupuesto de matching roja antes de corregir. Tras los cambios de motor/migración: **100 passed** dirigidas, mypy src aprobado (stage3-engine-directed.log). Tanda HTTP anterior: 57 passed y un fallo exclusivamente por versión en golden. Comparación profunda de AMBOS golden completada: todos los otros campos/trazas/importes iguales; referencias actualizadas sólo de 0.3.0 a 0.3.1, recibo stage3/golden-review.json.
- scripts/build_reproducible.py normaliza metadata ZIP/tar/gzip sin cambiar miembros. Dos pruebas independientes de normalización aprobadas; verify_delivery ahora exige bytes iguales entre dos archives limpios, registra epoch del commit/Python/zlib y admite locks con hashes. Todavía no ejecutada la doble construcción real de esta fuente: requiere commit limpio.
- requirements.lock y requirements-browser.lock: generador scripts/lock_hashes.py consulta metadata oficial PyPI para hashes de TODOS los archivos de cada versión exacta, preservando plataformas. Sin actualizar versiones. pip real en entorno nuevo con hashes todavía pendiente. Consulta de documentación web falló por servicio503; metadata PyPI sí respondió directamente. No declarar revisión de vulnerabilidades por fijar hashes.
- Tarea en curso: scripts/verify.sh, sesión de exec obtenida al retomar (ver herramientas), log /tmp/calibre-implementation-20261029-CvSz5k/stage3-verify-first.log. No editar engine/storage/importing/canonical mientras corre: artifact hash lo detecta. Luego benchmark1k/3reps comparable.
- Pendiente: instalador integral que detenga/reinicie servicio y respalde TODAS las bases registradas; ensayo de fallo/reversión preservando cambios nuevos; build real con pip hash; browser y CI/corpus/mutaciones; PR/merge/tag/assets/readback/instalación0.3.1 y auditoría final. Documentar API/operación nueva. No cerrar por la suite parcial.


## Avance posterior — integridad de recursos y actualización

- Primer verify.sh **342 passed** (stage3-verify-first.log). Primer benchmark posterior, 1k/3 reps, oráculos matched: mediana21,6489s y pico168,12MiB, frente baseline21,9s/181,74MiB. No es una campaña grande ni prueba de acelerar toda carga. Nueva agrupación de canonical_chunks64KiB resuelve muchas escrituras mínimas al ZIP: hace necesario benchmark final comparable (pendiente).
- Dos regresiones nuevas rojas → verdes: transferencia pathsend diferida impedía garantizar cleanup después de enviar; ahora se fuerza la transferencia por bloques. Presupuesto conservador XML256MiB rechaza XLSX antes de generar temporales enormes; ZIP conserva JSON completo y advertencia, no planilla parcial. Dirigidas finales recursos/install/build/integración/rutas/reportes: **53 passed** (stage3-resources-final-directed.log).
- Nuevo scripts/local_release.py integra respaldo de TODAS las bases registradas, hash/huellas, migración/verificación, stop/start/health, reversión que conserva todas las DB posteriores y auxiliares, y --recover tras interrupción. Cinco pruebas con DBs reales descartables y servicio/runtime simulados (no equivalen todavía a ensayo real del instalador/systemd). Guardan/restauran 3 clientes+principal, una corrida y cliente creados después, fallo de salud, backup alterado, cliente ausente e interrupción.
- install_local.py ahora --activate administra systemd por defecto; --no-service sólo ensayo offline, --rollback/--recover explícitos. No ejecutarlo sobre producción hasta certificar paquete. CI Tier4 usa verify_delivery estricto. Locks con hashes generados sin cambiar versiones (38+3), metadata PyPI respondió. Pip real en venv nuevo todavía pendiente.
- UI: acuerdo muestra hasta10versiones/20reglas/10tablas/20filas con avisos, sin truncar configuración. Runner navegador agrega configuración ficticia20kfilas, prueba preview20/editorcompleto/desktop390. SintaxisJS aprobada; navegador final todavía pendiente. Browser plugin no expone capacidad activa: fallback Playwright local ya documentado.
- En curso: **segundo verify.sh**, sesión93101, log stage3-verify-second.log. Luego benchmark final y navegador, commit limpio, verify_delivery real, ensayo instalado/systemd aislado, corpus/mutaciones, PR/CI/merge/tag/readback/activación/auditoría final. Plan operativo documentado en ENGINE_0_3_1.md.
- Reconsulta efectiva antes de actualizar: servicio0.3activo; DB schema2, 0runs/sources/configs/decisions/imports. No se alteró la instalación0.3 ni se cargó fixture. Verificar otra vez al cortar servicio.


## Listo para certificar distribución (estado más reciente)

- Source Chromium E2E aprobado, recibo stage3/source-browser.json; UI SHA de7a38081b973cdad0bb445922028d25f029918ce04994914e99dc96ceca70be. Capturas desktop/mobile inspeccionadas; preview20 de20k sin desborde, editor conserva20k. Sólo503intencionales del runner, ninguna excepciónJS/CSP.
- Benchmark FINAL después de agrupar64KiB: 1k/3reps +warmup, todos oráculos: mediana **16,0007s** vs21,9s baseline; pico **168,11MiB** vs181,74MiB. XLSXmediana5,8711s. stage3/benchmark-0.3.1.json; temporalstage3-final-benchmark/. No extrapolar a otra escala. No hay QA pesada en curso.
- Instalador ahora rechaza unit perteneciente a otra raíz y comprueba listener loopback del PID del servicio en /proc; probe después de rollback usa puerto del launcher RESTAURADO, que puede diferir del candidato. Fingerprints hashean campos grandes sin convertir BLOBs a hexadecimal. Scripts no forman parte del artifact del motor. Últimas dirigidas:8passed (6installer+2build), posteriores al verify349.
- Nuevo ensayo REPRODUCIBLE **scripts/rehearse_upgrade.py**: usar raíz NUEVA y wheels0.3/0.3.1. Crea servicio de nombre/puerto únicos,3clientes+principal con originales ficticios; actualiza conservandoIDs/hashes; crea corrida+cliente nuevos y revierte conservándolos; ensaya puerto ocupado y exige rollback automático al puerto/configuración anteriores; elimina sólo su unit/launcher al finalizar. Todavía NO ejecutado. Mantiene logs privados junto a root; publica recibo compacto. Nunca apuntar a producción existente.
- Próximo: commit de esta fuente/documentación, verificar árbol limpio, ejecutar verify_delivery con doblebuild estricto/hashlocks en venv nuevo; luego ensayo real instalado/systemd y E2E instalado. No modificar core durante pruebas. Si falla corregir causalmente y certificar nuevamente. Después corpus/mutaciones/PRCI/plataformas/main/tag/artefactos finales/readback/activación y auditoría final. Producción sigue0.3.0 vacía yactiva.


## Certificación de fuente comprometida

Implementación etapa3 comprometida en **ae87e18** sobre engineering/performance-0.3.1. El commit siguiente sólo registra este checkpoint/directriz de SHA documental (consultar git log -1 -- docs/CONTINUATION.md). Árbol de producto idéntico. Se inicia verify_delivery estricto con dos archives limpios; salida/artefactos temporales **stage3-candidate-delivery.json** y **stage3-candidate-assets/** bajo /tmp/calibre-implementation-20261029-CvSz5k. Mientras corre no editar ningún archivo trackeado porque compara HEAD/estado; registrar resultado al finalizar. Luego ensayo real aislado, no producción.


## Distribución candidata certificada

verify_delivery PASSED sobre **ec5566d50408b857ab23a5755be8c4e6ec61f1e1**: dos builds de cada wheel/sdist idénticos EN BYTES; pip con hashes y 38pins/pipcheck; smoke de ambos instalados fuera del checkout. Python3.12.3/zlib1.3, epoch1793299410. Wheel candidato e8d45b60170718b233b3363e5c286606fa02433d503c7cde9935d2b5a1daca01; sdist7d6fe724347921c70da3961b37627f287868da9f2d25b16bd552ad2cf6a4dbc0. Recibo stage3/candidate-delivery.json; assets en stage3-candidate-assets/. NO son assets definitivos desde main/tag, ni se instalaron en producción.

Ensayo REAL en curso: scripts/rehearse_upgrade.py, sesión80482; raíz NUEVA /tmp/calibre-implementation-20261029-CvSz5k/stage3-real-rehearsal, log stage3-real-rehearsal.log, salida prevista stage3-real-rehearsal.json. Al finalizar deshabilita/elimina exclusivamente su service/launcher de nombre único; conserva venvs/DB ficticias privadas. La producción0.3permanece activa y aislada. No ejecutar otra QA pesada local a la vez.

Se prepara PR de etapa3 como draft: CI puede ejecutarse mientras se terminan los ensayos locales; no mergear/publicar hasta revisar todos los checks y resultados. Pending: E2E del candidato instalado, corpus/mutaciones/nightly actual, plataformas Windows/Linux actuales, assets definitivos desde main, release/activación y auditoría final.


## Ensayo real y corrección causal de systemd

- PR **#4 draft**, https://github.com/Juan4787/Calibre/pull/4. Primer CI **40933933375 PASSED** amboschecks sobre **d7e4dc5a1fa5c7fa304321a23d09344e17d90b4f** (anterior a correcciones de instalador). Main/tag/producción continúan0.3.0.
- Primer ensayo real FALLÓ: systemd no elimina comillas de WorkingDirectory; interpretó `"/tmp/..."` como ruta no absoluta. Journal confirmado. stop de unidad inválida sinPID retornaba5 y ocultaba el error, evitando el cleanup automático. Corregidos: ruta absoluta sin comillas (ExecStart conserva su gramática de argumentos), stop verifica ausencia dePID, reload/disable al restaurar/eliminar una unit nueva. Nuevo parser real prueba también espacios y XDG_RUNTIME_DIR descartable para CI sin sesión; jamás controla producción. Se quitó After=default.target para evitar ordenar un servicio después del target que lo quiere.
- Segundo ensayo: primera instalación corregida y saludable en ruta CON ESPACIOS; falló el RUNNER por entrar en contexto de httpx.Client ya abierto al consultar token. Se inicializa dentro del contexto. No fue un fallo económico ni de producto. Historial de ambos intentos en stage3/SYSTEMD_REHEARSAL.md.
- Ensayo REAL final **PASSED**, recibo stage3/real-upgrade-rollback.json: servicio calibre-rehearsal-259869.service, 3clientes+principal con datos/originales ficticios, actualización0.3→0.3.1 mantuvoIDs/hashes. Nuevacorrida+cliente posteriores preservados al --rollback. Puertoocupado fuerza fallo de inicio y exige reversión automática con puerto/config anterior +salud. Unit/launcher únicos eliminados/deshabilitados al terminar. Base0.3productiva siguióactiva yvacía. Motor0.3.1 **dca7228d52b7db230a57a181bd71e8b8d9842960b5b941a247bba5941a50514e**.
- Primer ensayo interrumpido recuperado explícitamente con --recover --no-service, después de comprobar que su unit ya estaba eliminada: recibo first-install-recovery.json; conservó DB posterior ficticia. No se borraron logs/DB/evidencia de intentos.
- Cambios SINcommit actuales sólo instalador/runners/tests/docs; ningún archivo del producto/wheel cambió tras ec5566d. **El sdist candidato contiene instalador anterior a esta corrección y NO debe publicarse.** Construir/certificar assets definitivos desde main/tag, no reutilizarlo.
- En curso: **E2E instalado candidato**, sesión33574, Python real de `/tmp/calibre-implementation-20261029-CvSz5k/stage3 real rehearsal final/releases/0.3.1/bin/python`; QA Playwright en .venv. Log stage3-installed-browser.log; salida stage3-installed-browser/result.json. No editar producto mientras corre. Después verify.sh final, commitfix+docs/push, CIexacta, nightly/plataformas, merge/tag/buildfinal/instalación/auditoríafinal.


## Gates remotos, último fix de plataforma y siguientes pasos

- Corrección systemd comprometida/pushed **a03f667ef2d8efa672a22672a0f8f8f94695cbb2**. CI PR **40934859058 PASSED** amboschecks; **nightly40934858380 PASSED** (Hypothesis1000, mutaciones, controles/fallas dirigidas,62imports,E2E). Descargar sus JSONcompactos antes de que expiren los artifacts; descarga a stage3-ci-nightly-evidence/ en curso (no publicar trazas/tokens/DB).
- E2E instalado PASSED, recibo stage3/installed-browser.json, ruedaE8d45..., todos los archivos de producto iguales al checkout y backendPythonreal fuera de repo; sólo503intencionales, sin excepcionesJS/CSP. QA sesión33574terminó0. Último verify.sh local **352passed** (verify-352.log); luego11dirigidas de instalador/build/markerlock aprobadas. Ninguna QA pesada local pendiente salvo descargaartifact, no editar core todavía (no requiere cambios).
- Plataformas **40934863136**: LinuxPASS, Windows falló al instalar lock con hashes: dependencia **colorama** condicional requerida por build/click/pytest estaba ausente del lock Linuxoriginal. No es fallo de hashes incorrectos ni del motor. Se agrega **colorama==0.4.6; sys_platform==win32**, hashes oficiales de todas sus distribuciones. Generador preserva markers; verificador de pins evalúa entorno para no exigir colorama enLinux.
- Nuevo scripts/check_lock_closure.py: metadata PyPI oficial, dependencias activas Python3.12Linux/Win sin faltantes/incompatibles; 41pins incluyendoBrowserLinux/42Win. Recibo stage3/lock-closure.json. Regresión selecciona pins por plataforma; dirigida11passed. ActualWindowsCI aún pendiente de repetición tras push. Archivos SINcommit: lock/generador/verificador/regresión/checkclosure/docs/recibos. No cambió producto/motor/JS tras ae87e18.
- Próximo: commit de cierre de lock/recibos, pushPR4; repetirCIexacta+plataformas (nightly del producto ya pasó, nuevo lock no cambia versionesLinux; si se ejecuta otra, conservar). Verificardescarganoerrores y recogerresúmenesnightly. MarcarPRready, merge sólo tras requeridos y plataformaaprobados. Construir assetsdefinitivos desdeSHAde main/tag, releasegateTagcompleto, ruedasinstaladasE2E/readbackremoto, actualizarservicioreal conbackupyhashes, auditoríafinal. No reutilizar sdistcandidato viejo. Produccióncontinúa0.3.0, basevacía última consulta; reconsultar aldetener.


## Diagnóstico de paridad y protocolo QA v3 (estado más reciente)

- Lock corregido comprometido/pushed **609e625efaeb5ca0521e253f187711688e56a11c**. CI **40935679336 PASSED**, incluye353pruebas. Gateplataforma **40935692521**: Linux24/24 y Windows24/24 +9rutas/importación instaladas aprobados; comparación conjunta FALLÓ. Archivos descargados intactos a stage3-platform-divergence/.
- Cotejo campo a campo de ambos fingerprintsv2: ÚNICAMENTE rootdigest y los3run_id diferentes; todos los hashes de snapshot/motor, importes, trazas y hallazgos iguales. Reportes registran **PythonLinux3.12.15 vsWindows3.12.10**. Desde0.3 metadata.python forma parte de identidadv2: el antiguo QA confundía identidad física por entorno con identidad portable, sin error económico demostrado.
- Nuevo QA **calibre-platform/v3**, sólo archivosqa/gates.py, output/e2e/platform_scale/{run_platform_suite,compare_fingerprints}.py y regresión. Conserva identities originales con metadata COMPLETA, valida preimagen del ID físico; portable_run_id incluye input/result/motor/metadata salvo python. TODA metadata restante se compara, incluyendo bibliotecas/control/procedencia/workspace. No eliminar controles de hashes ni reescribir corridas. El fingerprintincluye result_hash completo adicional. Gate rechaza identidadalterada/metadataque no corresponde/faltaprueba/cambiodeversión/traza. V2histórico noes aprobacióndev3.
- Causal exacta con función anterior degitHEAD609 y Pythonpatches observados: paridadFalse→True con idénticodataset/resultado; physicalIDdistinto conservado. stage3/platform-causal.json. Testinicialrojo preservado; **59dirigidasPASSED**, mypyQAaprobado. NO cambia ningún archivo del producto ni el artifact dca7228.... Faltaejecutar CI y plataformasreales actualizadas.
- Nightly anterior del MISMOproducto con a03: **20/20mutaciones**, **41/41fallas detectadas/prevenidas**, **12/12controles sinfalsospositivos**, **62/62imports**,23testsQA_PROFILEnightly1000 yE2E, todosPASS. JSONcompactosdurables stage3/nightly-{mutations,faults,healthy,imports}.json. Artifacts completos privados/tmp, nunca subirtrace/DB/sessiontoken.
- Comparación de sólolectura: las **5DBoriginales .local/** mantienen TODASlas filas lógicas iguales a susbackupsiniciales, quickcheckok. Recibo original-databases-preserved.json. No fueronpromovidas ni migradas.
- Próximo: commitQAfix/docs, push, dispatchplatformsobreHEADnuevo y revisarCIexacta; sinQAheavy localactiva. Si ambosgatespasan, PR4ready+mergeprotegido, tagv0.3.1, buildfinaldosvecesdesdemain/tag+locks, releasegatefull/E2Einstaladoexacto/readback/activarservicio0.3.1 conbackup, auditoríafinal. Producciónaún0.3.0 y no se tocó enensayos. Sdistcandidatoec es viejo e INAPTOpara publicar. Mantenerhistorialfallos.
