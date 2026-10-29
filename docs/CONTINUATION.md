# Bitácora obligatoria de continuidad

Leer completa después de cada compactación junto con `AGENTS.md`. Última actualización: 29/10/2026, inicio de implementación.

## Objetivo y autorizaciones

Implementar el plan completo de auditoría por etapas, con verificación profunda en cada etapa, publicación en GitHub, instalación local y auditoría final. El usuario confirmó GitHub + instalación; al pedir identificar una instalación existente aclaró **"no la hay"**. Se prepara una primera instalación con base vacía, sin promover las cinco bases de demo/QA a producción.

El usuario exige documentación completa y directrices que se relean después de cada compactación. Éstas están en `AGENTS.md`.

## Estado exacto

### Corrección posterior de la verificación remota

El workflow del tag v0.2.0, run 40830562663, terminó con fallo en el smoke instalado: pip heredó PYTHONPATH del checkout, reconoció los metadatos de la misma versión como instalada y omitió copiar el wheel al entorno aislado. El smoke fuera del checkout detectó correctamente la ausencia del módulo. Los smoke/E2E instalados locales y los hashes descargados del release habían pasado; no son evidencia de aprobación de ese workflow. Se corrige el aislamiento quitando PYTHONPATH también durante pip y forzando la instalación del wheel. Requiere CI y workflow manual sobre el commit corregido, sin mover el tag histórico ni reemplazar sus artefactos. Rama de esta corrección: engineering/release-install-isolation.

- Cwd: `/home/usuario/CascadeProjects/CALIBRE`.
- Rama de trabajo: `engineering/staged-hardening-20261029`.
- HEAD inicial publicado: `fd62f05392f819896589c2a3b271ad49cdcfafbd`, versión 0.1.0.
- Commit de preservación: `e5a404e`, conserva los cambios anteriores 0.1.2 (ONR-001..005, pruebas y evidencia). Publicado en la rama de trabajo.
- Commit de etapa 1: `a237fd136c9fb759504852ac365dfc2e77bc360b`, publicado en esa rama. PR: https://github.com/Juan4787/Calibre/pull/1. CI en curso: https://github.com/Juan4787/Calibre/actions/runs/40829017212.
- Documentación de etapas: `docs/STAGED_HARDENING_2026_10_29.md`. Se acaba de crear, todavía sin commit.
- Etapa activa: **1, certeza e integridad**, implementación en curso, todavía SIN entrega ni publicación. Versión de trabajo 0.2.0.
- Publicaciones realizadas: rama/PR de etapa 1; **main y releases todavía no actualizados**.
- Instalación nueva: entorno **preparado y verificado, NO activado** en `/home/usuario/.local/share/calibre/releases/0.2.0/`. Smoke y E2E completo del wheel instalado pasaron. No hay listener Calibre activo ni base operativa creada.
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

1. Comprobar CI de PR #1. Preservar/commit de los recibos instalados y esta actualización documental; se disparará CI sobre el nuevo HEAD, que debe aprobar.
2. Configurar protección de main con los nombres reales de checks exitosos; integrar PR, publicar tag/release 0.2.0 con wheel y sdist concretamente verificados. Conservar el código anterior para replay.
3. Activar el entorno local preparado con el **mismo wheel** de `dist/`, crear launcher y servicio systemd de usuario en loopback; comprobar puerto/UI/version/ruta y base vacía. Registrar todo.
4. Cambiar a etapa 2, nueva rama y versión 0.3.0. Diseñar imports conservados con referencias pequeñas (schema SQLite v2, migración sólo probada en copias), teclado y controles documentales.

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
