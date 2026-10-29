# Bitácora obligatoria de continuidad

Leer completa después de cada compactación junto con `AGENTS.md`. Última actualización: 29/10/2026, implementación de etapa 2; etapa 1 entregada.

## Objetivo y autorizaciones

Implementar el plan completo de auditoría por etapas, con verificación profunda en cada etapa, publicación en GitHub, instalación local y auditoría final. El usuario confirmó GitHub + instalación; al pedir identificar una instalación existente aclaró **"no la hay"**. Se prepara una primera instalación con base vacía, sin promover las cinco bases de demo/QA a producción.

El usuario exige documentación completa y directrices que se relean después de cada compactación. Éstas están en `AGENTS.md`.

## Estado exacto

### Corrección posterior de la verificación remota

El workflow del tag v0.2.0, run 40830562663, terminó con fallo en el smoke instalado: pip heredó PYTHONPATH del checkout, reconoció los metadatos de la misma versión como instalada y omitió copiar el wheel al entorno aislado. El smoke fuera del checkout detectó correctamente la ausencia del módulo. Los smoke/E2E instalados locales y los hashes descargados del release habían pasado; no son evidencia de aprobación de ese workflow. Se corrige el aislamiento quitando PYTHONPATH también durante pip y forzando la instalación del wheel. Requiere CI y workflow manual sobre el commit corregido, sin mover el tag histórico ni reemplazar sus artefactos. Rama de esta corrección: engineering/release-install-isolation.

- Cwd: `/home/usuario/CascadeProjects/CALIBRE`.
- Rama de trabajo actual: `engineering/operations-0.3.0`, creada desde main al terminar etapa 1. La rama anterior queda como historia del PR #1.
- HEAD inicial publicado: `fd62f05392f819896589c2a3b271ad49cdcfafbd`, versión 0.1.0.
- Commit de preservación: `e5a404e`, conserva los cambios anteriores 0.1.2 (ONR-001..005, pruebas y evidencia). Publicado en la rama de trabajo.
- Commit de etapa 1: `a237fd136c9fb759504852ac365dfc2e77bc360b`, publicado en esa rama. PR: https://github.com/Juan4787/Calibre/pull/1. CI final de PR #1 aprobado: https://github.com/Juan4787/Calibre/actions/runs/40829412107.
- Documentación de etapas: `docs/STAGED_HARDENING_2026_10_29.md`. Publicado en main con la etapa 1.
- Etapa 1: completada; los apartados de trabajo de esa etapa que siguen son historia cronológica, no pendientes actuales.
- **Etapa 1 publicada e instalada.** PR #1 MERGED, main `30d774cc5695103e4396cc78d2b5db5daa63e6a9`. Su árbol coincide con el de 4b83186, que pasó CI; CI de main también aprobada (40829873255).
- Release: https://github.com/Juan4787/Calibre/releases/tag/v0.2.0. Incluye wheel, sdist, SHA256SUMS y recibo de distribución. Descarga remota repetida: hashes de los tres archivos comprobados OK.
- Instalación activa: `/home/usuario/.local/share/calibre/current` → `releases/0.2.0`; DB `/home/usuario/.local/share/calibre/workspaces/default/audit.db`. Al activar tenía **0 corridas**; volver a verificar antes de migrar porque el usuario puede abrirla.
- Servicio de usuario **activo y habilitado**: `calibre-freight.service`, puerto **127.0.0.1:8765**, PID inicial 3744918 (no asumir PID vigente). Launcher `/home/usuario/.local/bin/calibre-freight`; unit `/home/usuario/.config/systemd/user/calibre-freight.service`. Root de instalación modo 700; DB 600. Readback HTTP 200, JS igual al wheel instalado. Los ensayos usaron bases temporales, no esta DB.
- Etapa activa: **2, operación**, versión de trabajo 0.3.0 sin publicar. Cambios locales todavía sin commit; producción sigue en 0.2.0 / schema 1.
- No hay herramientas Browser activas; está disponible Playwright Python con Chromium. Usar el fallback documentado y pruebas secuenciales.
- CLI `gh` autenticada con cuenta activa `Juan4787`; git HTTPS tiene acceso de lectura. No se imprimieron secretos. Comprobar escritura al publicar la rama autorizada.
- No hay agentes secundarios en ejecución. No delegar salvo instrucción explícita aplicable.

## Evidencia y preservación

Auditoría anterior: `/tmp/calibre-audit-20261029-UYK9GN/AUDITORIA.md`, con scripts, JSON y capturas en la misma carpeta. Es evidencia sintética del árbol anterior, no de los cambios futuros. Pruebas anteriores: 276 passed; adversarial 61/62; E2E Chromium passed; benchmark 1.000 cargos/3 repeticiones. No reutilizar esos recibos para certificar cambios nuevos.

Preservación de esta implementación: `/tmp/calibre-implementation-20261029-CvSz5k/`.

- `initial.patch`: cambios iniciales.
- `initial-status.txt`: estado inicial.
- `untracked-before.tar.gz`: archivos inicialmente sin seguimiento.
- `db-backups/`: backups SQLite verificados por quick_check de las cinco bases `.local/*.db` (audit, control-final-20260923, control-v2-20260923, delivery, demo-final).

Las bases originales no se modificaron. No copiar backups de bases a GitHub. El archivo `docs/INSTRUCCIONES A SEGUIR PARA LA AUDITORIA ADVERSARIAL` existía sin seguimiento: preservado en el tar, no agregado en el commit de preservación; es una referencia histórica, no reemplaza el encargo actual de implementar.

## Decisiones técnicas ya establecidas

1. **Fechas:** admitir fecha civil; rechazar directivas de hora/zona en mappings. No elegir UTC como política contractual inventada.
2. **Explicit sin candidatos:** dejar en revisión sin diferencia confirmada y mostrarlo en preflight. La política 0.1.2 lo permitía; documentar cambio de semántica y nueva versión. Proteger también grupos relacionados, cobertura e importes originales.
3. **Procedencia:** cotejar datos normalizados contra originales/mappings cuando existan; para JSON aportado sin soporte, declarar nivel de procedencia en vez de afirmar cotejo inexistente. Mantener el motor puro y las corridas históricas.
4. **Exportación:** verificar originales para todos los formatos; nunca ofrecer un reporte como documentalmente íntegro si no se comprobó. Conservar JSON/originales ante límites de representación XLSX.
5. **Tipos:** preservar el tipo semántico date/text/decimal/boolean durante evaluación, sin conversiones implícitas.
6. **Recursos:** límites de lectura antes/durante read, presupuestos separados; importaciones conservadas en servidor para evitar enviar decenas de MB de procedencia en el wizard.
7. **Distribución:** crear releases verificadas y una instalación aislada con actualización reversible. Resolver primero los bloqueos del alcance; proteger main con checks concretamente observados.

## Plan restante

1. Crear pruebas permanentes que fallen en el código actual para fecha textual, vínculo sin candidatos, procedencia alterada, fuentes corruptas/exportación, caracteres XML, XLS oculto, tipos semánticos y precisión del control externo.
2. Implementar etapa 1; corregir XLSX-11 sin relajar importador, agregar controles causales al gate de PR. Actualizar golden sólo después de revisar diferencias semánticas esperadas. Auditar motor/API/exportación/historia, construir artefacto e instalar fuera del checkout.
3. Publicar la etapa 1 sólo cuando sus controles pasen; registrar commit/CI/tag/release/instalación y rollback.
4. Implementar operación/UI según etapa 2: referencias de importación, teclado, control externo integrado, respaldo contractual, relación entre corridas, espacio de trabajo y restauración.
5. Etapa 3: reportes progresivos, recursos, build/dependencias reproducibles, distribución y verificación remota.
6. Auditoría final independiente, con límites de validación real explícitos.

## Información externa pendiente

No existen originales/contratos/control independiente de un cliente real. No se puede ejecutar ni declarar aprobado ese piloto sin ellos. Tampoco hay Windows/Excel del operador disponible. Implementar las herramientas y el protocolo; conservar estas validaciones como pendientes externos concretos, sin inventar resultados.

## Próxima acción exacta

1. Crear y ejecutar las regresiones de etapa 2: imports compactos/ref de servidor, protección contra sustitución, control externo, referencias contractuales y relación entre corridas; comprobar estado rojo antes de implementar.
2. Implementar schema SQLite v2 (tabla imports inmutable, migración aditiva transaccional), API por referencias y paginación de incidencias; UI por teclado, preflight y control documental. NO modificar el servicio 0.2.0 mientras se desarrolla.
3. Completar identificación de espacio local, cotejo/backup/restauración y resumen contractual legible. Ver diseño abajo.
4. Antes de instalar 0.3.0: detener servicio, backup consistente verificado, migrar una copia y ensayar rollback. Conservar entorno 0.2.0. Nunca abrir una DB v2 con el motor viejo ni sustituir la DB sin preservar sus cambios.

## Trabajo de etapa 1 ya realizado y comprobaciones

- `tests/test_audit_hardening.py`: **25 fallos antes de corregir**, recibo `stage1-red.log`; **25 aprobados después**, `stage1-directed.log`.
- Cambios: date_formats sólo Y/m/d una vez; explicit-consistency-v3 con categoría uncorroborated→REVIEW y protección relacionada; Atom.kind preserva date/text; XLS bloquea hoja/fila/columna ocultas; verificador externo usa Fraction; límites de lectura; texto no representable XLSX produce ReportLimitError para conservar ZIP+JSON; check_provenance coteja importación congelada y valores/citas; Store.load comprueba originales para todos los lectores/exportaciones.
- Nuevo `provenance.py`: **reutiliza el lector tabular**, no afirmar que sea una implementación independiente de conversiones. Regresiones con valores escritos a mano cubren ese límite. Registros sin mapping/citas suficientes se cuentan como declarados; la UI lo explica en banner.
- Primera suite completa: **297 passed, 4 failed**. Los cuatro fallos fueron golden por cambio de engine_version, nuevo contador uncorroborated y dos referencias al test renombrado en catálogo. Se corrigieron esas referencias. Los dos golden fueron comparados por estructura: **únicamente cambió engine_version 0.1.2→0.2.0**; importes/estados/trazas de fixtures oficiales intactos.
- Corpus adversarial: **62/62**, `stage1-imports/adversarial_import_results.json`; XLSX-11 ahora exige rechazo de ocultos y compara copia visible, peso 80 y fila física 2.
- Ruff y ambos mypy aprobados antes de los cambios menores finales de rutas. `qa.py matrix --generate` ejecutado sin errores.
- Nuevo `tests/test_contract_reference.py`: 14 casos con precios/fronteras/redondeos/consolidación/lookup calculados a mano y comprobación de pertenencia/regla/versión; incluidos en la suite en curso.
- UI: banner de nivel de procedencia y nueva incidencia sin corroboración; falta ejecutar E2E actual. Craft floor leído antes de editar. Estilo existente preservado.
- Gate PR ahora incluye corpus adversarial; aún no ejecutado remotamente.

### Actualización de verificación

- Segunda suite completa: **315 passed, 2 warnings**, 27,63 s. Lecturas/rutas y filas de procedencia en reportes se modificaron después; requieren gate posterior.
- Mutaciones: **19/20 detectadas**, M16 sobrevivió. Causa identificada: su fixture usaba un explicit sin corroboración, que la nueva política deja REVIEW y suprime cobertura; ya no ejercitaba la consolidación válida. Se corrigió el fixture con clave compartida de lote explícita y se agregó assert de estado/importe. No se alteró el motor para matar el mutante. Reejecución sólo M16 en curso, sesión `39914`, archivo `stage1-mutation-M16.json`.
- Primer E2E actual falló al reconciliar una fila nueva `Procedencia` de XLSX. Se amplió el verificador para cotejar explícitamente la fila y conservar compatibilidad con reportes históricos sin ella. No se ignoran métricas desconocidas. Debe reejecutarse E2E.
- Auditoría inicial archivada permanentemente en `docs/qa-evidence/2026-10-29/initial-audit/` (21 archivos, sin bases); ya no depende exclusivamente de /tmp.
- Permiso GitHub ADMIN confirmado. Último CI de main original: https://github.com/Juan4787/Calibre/actions/runs/35824346370, success. Falta publicar rama, crear PR y comprobar los checks del commit nuevo antes de proteger/mergear main.

### Cierre técnico local de etapa 1 (publicación pendiente)

- Campaña completa final: **20/20 mutaciones detectadas**, `stage1-mutations-final.json`, salida 0.
- E2E completo repetido: **passed**, `stage1-browser-rerun/result.json`; sin excepciones JS ni rechazos CSP.
- Cruce de familias afectadas: **107 passed**, `stage1-cross-flow.log`.
- Gate canónico terminado: `stage1-verify.log`, build wheel/sdist correcto; comprobar el resumen de pytest al crear el recibo definitivo.
- Evidencia permanente: `docs/qa-evidence/2026-10-29/stage1/` y contrato `docs/ENGINE_0_2_0.md`.
- `scripts/install_local.py` prepara venv de versión, instala lock+wheel y corre smoke fuera del checkout; sólo activa con --activate, preservando pointer anterior y backup SQLite verificado. Usa bloqueo exclusivo. Todavía no ejercitado completamente: instalación en curso.
- Los registros enriquecidos con atributos manuales adicionales se cuentan como declarados (aunque sus campos importados sean cotejados), para no atribuir respaldo al registro completo.

### Publicación y entorno descubierto

- Conector GitHub rechazó crear PR con 403 de integración. Se usó la CLI `gh` ya autenticada con permisos ADMIN; no fue un rechazo de aprobación automática. PR #1 creado correctamente.
- Preparación instalada: log `stage1-install.log`; entorno aislado, lock completo, smoke fuera del checkout. E2E instalado: `stage1-installed-browser/result.json`, passed, ruta de paquete dentro de releases/0.2.0; recibido permanente `installed-browser.json`.
- Checks de PR revelaron una integración Netlify no documentada. **Sitio público y deploy preview devuelven 404**, igual que /api/session público. No existe backend declarado allí. No confundir check verde del deploy con app operativa. Registro `stage1/netlify-inspection.json`. Destinos elegidos por el usuario: GitHub y primera instalación local; no se configuró un SaaS ni se alteró Netlify.
- Al retomar, la presencia de esta inspección no autoriza afirmar que Netlify publica el motor ni que es el destino operativo. Mantener el estado real visible en auditoría final.

### Entrega efectiva de etapa 1

- Protección de main aplicada y leída: checks obligatorios `Tier 1 - PR & Fast Functional Gate` y `Tier 2 - Full Semantic & Invariant Verification`, strict, aplica a admins, requiere PR (0 aprobaciones porque el dueño trabaja solo), sin force push ni borrado, conversaciones resueltas.
- Replay histórico preservado mediante tags `replay-0.1.0-fd62f05` y `replay-0.1.2-e5a404e` (no se presentan como releases recomendadas).
- Verificador de distribución de dos checkouts limpios aprobado: `/tmp/calibre-implementation-20261029-CvSz5k/stage1-delivery.json`. Byte-identical aún es deuda de etapa 3; contenido e instalaciones wheel/sdist verificados.
- Artefactos concretos inmutables de etapa 1: `/tmp/calibre-implementation-20261029-CvSz5k/stage1-assets/`; copia descargada y comprobada en `stage1-readback/`.
- Activación y readback local: `stage1-activation.json`, `stage1-live.json`. Aún falta copiarlos al recibo permanente junto con el de distribución y registrar el workflow de release que se disparó con el tag. No afirmar que ese workflow terminó hasta consultarlo.
- El unit ejecuta el launcher con `serve --port 8765`, WorkingDirectory en root de instalación, PYTHONDONTWRITEBYTECODE=1, UMask=0077, NoNewPrivileges=yes, Restart=on-failure. `systemctl --user stop/start/status calibre-freight.service` administra el proceso.

## Diseño de etapa 2 pendiente de implementación

- API `/api/import` con Form compact=true para el wizard: conservar resultado completo en SQLite y devolver ID/contadores/vista previa acotada; mantener API normal por compatibilidad. Los requests de audit/preflight llevan `{imports:{shipments:id,charges:id}, label, agreements, evidence, coverage, ...}`. Resolver en servidor, rechazar mezcla con records/overrides. La respuesta preflight incluye sólo referencias de los candidatos mostrados, para conservar avisos sin enviar todas las operaciones.
- Incidencias compactas: no volver a enviar todas; devolver conteos y primera página, con endpoint de páginas de 50. Conservar todos los mensajes backend y proteger respuestas obsoletas al cambiar vista/archivo/página.
- Huella de importador liga cada import conservado a lector/modelos/canonical; rechazar import antiguo si esos archivos cambian. Las optimizaciones de reporting no deberían invalidar un import por cambiar sólo la versión del paquete.
- Control externo: debe estar vinculado al snapshot (campo opcional excluido de hash semántico económico); así agregar control crea una corrida distinta sin sobrescribir metadata por INSERT OR IGNORE. Validar inventario, conteos por fuente y moneda mediante Fraction, con archivo independiente aportado por operador. No generar los expected copiando los resultados. Sin control, mostrar pendiente; control contradictorio bloquea conservación hasta corregir.
- Contrato: referencias opcionales a hash, acuerdo/versión/regla y página/cláusula/aprobación aportadas. Validar IDs y conservar documentos; no inventar aprobación ni autenticidad.
- Relación entre corridas: campos opcionales `parent_run_id`/motivo/tipo vinculados al snapshot, excluidos de semántica económica. Evidencia adicional fija parent a la corrida actual. UI permite volver al original y muestra revisiones posteriores sin cambiar resultados históricos.
- Workspace: hacer visibles nombre/DB y evitar fingir cliente asignado. Mantener DB separada por cliente; no construir SaaS/multiusuario. No cambiar el cliente de una base con historia de forma silenciosa. Diseñar el flujo concreto antes de extenderlo.
- Accesibilidad: selector inicial nativo o botón, nombre/foco/teclado, label persistente del buscador, errores de conexión comprensibles. Preservar estilo/CSP existente y ejecutar desktop+390px/teclado real.

## Actualización operativa de etapa 2 (estado vigente)

- Corrección remota adicional de etapa 1: PR #2 https://github.com/Juan4787/Calibre/pull/2, commit 6ffb523, merge main **7dbc16d651472af955a8e5688075cd280f5bc372**. El workflow del tag 0.2 falló porque pip heredaba PYTHONPATH del checkout y omitía instalar el wheel al reconocer metadatos de la misma versión. Smoke fuera del checkout detectó la ausencia del módulo. Se quitó PYTHONPATH durante pip y se fuerza instalar el wheel; ambos checks del PR pasaron. **Workflow manual completo de release 40833070930 aprobado**, sin mover el tag ni reemplazar los artefactos. Recibo permanente release-recheck.json. Worktree de corrección /tmp/calibre-release-isolation-20261029, no es un agente paralelo.
- Copias de activation/live/delivery de etapa 1 ya están en evidencia permanente, aún sin commit en la rama de etapa 2. Receipt actualizado con el estado real y el fallo/remediación remotos. No ocultar el fallo histórico del tag.
- Nuevos módulos: document_control.py (comparación exacta Fraction), workspaces.py (bases separadas, backup íntegro, restore como base nueva). SQLite v2 agrega imports inmutables e índice de revisiones. Configs contienen registro de espacios en la DB principal e identidad inmutable por espacio. El backup de un espacio incluye SÓLO su DB, no las DB de los otros espacios registrados.
- API compact=true conserva registros en servidor; IDs ligados al hash del importador; paginación de incidencias de 50; muestra de transformaciones limitada; requests rechazan sustituciones de registros. Trabajos costosos se serializan en threadpool para no bloquear el event loop ni ejecutar varios cálculos grandes simultáneamente. /api/health identifica versión y schema sin crear corridas.
- Dataset añade control externo, fuentes contractuales (documento/versión/regla/página/cláusula/aprobación), parent_run_id/tipo/motivo. Se excluyen de semántica económica. Store.save rechaza control contradictorio y parent ausente. UI soporta carga de control, documento contractual y aprobación aportada; nueva evidencia deja control pendiente porque el inventario cambió.
- Las nuevas corridas ligan metadata a su identidad (run_identity_version=2), para que no pueda alterarse la declaración de cotejo sin fallar el hash. Lectura y verificación de paquetes conservan compatibilidad de identidad v1. Metadatos históricos v1 no obtienen retroactivamente esa garantía. Se actualizaron QA invariants e impact para ambos contratos.
- UI: selector visible de cliente/espacio, bases nuevas por nombre; backups preparados y restauración sin reemplazar; carga por botón nativo/teclado, labels buscadores, errores de red humanos, links y comparación entre revisiones, fórmulas/tarifas legibles. Cambio de espacio invalida respuestas pendientes. La restauración web admite 25 MiB; CLI restore-workspace admite 500 MiB y verifica antes de registrar.
- Causal rojo inicial: 7/7 fallos en stage2-red.log; luego 7/7 verdes. Dos casos de aislamiento/restore fallaron antes del backend, luego pasaron. Nuevo caso de metadata alterada falló antes de proteger identidad, luego pasa dentro del cruce de familias.
- Primera suite total: 322 passed / 2 failed: golden por versión y simulación de corrupción impedida por nuevo índice JSON. Golden comparado estructuralmente: SÓLO engine_version 0.2→0.3; importes/semántica/trazas idénticos. Para simular DB corrupta se elimina expresamente índice además del trigger antes de inyectar JSON inválido; no se elimina ninguna defensa del producto.
- Primer E2E llegó al último flujo existente y detectó selector de espacio desplazando acción principal fuera del primer viewport móvil. Se compactó la cabecera móvil; requiere repetir. No se declara E2E aprobado todavía.
- Cruce posterior detectó 15 fallos del verificador QA al asumir metadata siempre presente/parseada. Corregido: fixtures sintéticos v1 sin metadata siguen válidos y impact deserializa metadata para identidad v2. **Cruce repetido 63 passed**. Cambios UI/API posteriores requieren gate final.
- Nuevas pruebas browser_operations.py (integradas al E2E canónico): chooser por Enter, transformaciones, control independiente escrito a mano (194.25+204.25=398.5 USD), negativo de cantidad, respaldo contractual descargado idéntico, corrección relacionada/comparación, cliente B vacío, restaurar A en base nueva y replay. Todavía sin ejecutar.

### Siguiente acción exacta actualizada

1. Terminar controles locales de etapa 2: ejecutar E2E nuevo y corregir fallos reales; probar 36.000 operaciones por referencias para cerrar el 413 original; migrar una copia v1 creada con el wheel instalado 0.2 y comprobar historia/rollback.
2. Crear docs/ENGINE_0_3_0.md, actualizar APIs/arquitectura/uso y schemas, guardar recibo etapa 2. Completar tests de controles negativos/tampering/restore y límites; suite/corpus/mutaciones pertinentes/gate canónico.
3. Commit de etapa 2, incorporar origin/main (PR #2) sin perder esta bitácora, PR protegido, CI y distribución/instalación aislada. Publicar 0.3 únicamente con evidencia aprobada. Antes de migrar instalación: parar servicio, backup verificado, ensayo copia, activar/reiniciar/readback, rollback conservando DB posterior.
4. Etapa 3 y auditoría final siguen pendientes según plan. No cerrar por cantidad de tests ni omitir piloto real/Windows del operador pendientes externos.

## Cierre local de etapa 2 antes de commit

- Gate canónico final: **330 passed, 2 warnings**; Ruff/tipos/matriz/JS/compile/build aprobados, stage2-verify.log. Últimos cambios posteriores sólo amplían catálogo/documentación y preservación de artefactos en verify_delivery.py; comprobar esos scripts al entregar.
- Nuevas familias/selectoras añadidas a QA-14/15/29/31/34/36 y matriz regenerada. Identidad de metadata v2 y schema 2 descritos sin atribuirlos a históricos.
- **20/20 mutaciones detectadas** en etapa 2; **62/62 corpus adversarial**. E2E final **passed**, stage2-browser-release/result.json. Incluye recuperación real de conexión fallida (página aislada, sin excepciones JS), contratos/controles, comparación y restore. Fallos encontrados y corregidos: scroll persistente al navegar, busy genérico eliminaba opciones del select, cantidad esperada mal escrita en control de prueba (original tiene seis operaciones, no tres). No se relajó ninguna protección para pasar.
- Ajustes finales: reportes HTML/XLSX indican control coincidente o pendiente; QA coteja exactamente ese texto. Verificador QA externo incluye originales citados aunque no estén repetidos en documents; regresión causal roja preservada y verde en suite final.
- Volumen real API por referencias: **36.000 operaciones, un cargo**; originales pequeños; request 1.480 bytes vs 48.528.135 bytes con registros normalizados; 36.001 registros cotejados; esperado/facturado 100, diferencia 0, replay idéntico; 41,489 s en este host. NO equivale a 36.000 cargos tarifados ni a benchmark de exportación. Reproducir con scripts/audit_operations.py.
- Migración real ensayada en copia: wheel instalado 0.2 fuera del checkout produjo DB/ZIP v1 de fixtures. Abrir con 0.3 migró a schema 2 y conservó id, hashes, snapshot, resultado, metadata, decisiones y fecha. El ZIP viejo pasa verificación nueva. Wheel viejo rechaza DB v2 y reproduce backup v1 intacto. Evidencia privada de trabajo stage2-migration/; recibo público migration.json, no se tocó DB operativa.
- Evidencia durable (sin DB ni trace con tokens de sesión): docs/qa-evidence/2026-10-29/stage2/. El recibo dice publicación/instalación PENDIENTES. E2E fuente y corpus corresponden al producto actual; no equivalen al wheel aún no instalado.
- verify_delivery.py ahora permite --artifacts-out RUTA_NUEVA y conserva exactamente wheel/sdist certificados para publicarlos, y limpia PYTHONPATH en subprocess. Todavía necesita ejecución después del commit limpio. La reproducibilidad binaria estricta sigue reservada a etapa 3.
- Próximo paso: commit de implementación, merge origin/main (PR #2, posible conflicto de esta bitácora: conservar ambos hechos), crear PR y esperar checks. Ejecutar verify_delivery con preservación de assets, preparar instalación 0.3 sin activarla, E2E sobre wheel fuera del checkout. Actualizar recibos; sólo entonces merge/tag/release y actualización local con servicio detenido y backups.
