# Continuidad obligatoria — estado actual

Leer después de cada compactación, junto con AGENTS.md, STAGED_HARDENING_2026_10_29.md y el recibo de la etapa activa. Historial completo, incluidos fallos/correcciones y decisiones: [WORKLOG_2026_10_29.md](WORKLOG_2026_10_29.md). No confundir sus entradas cronológicas antiguas con pendientes actuales.

## Encargo y autorización

Implementar todo el plan auditado por etapas, auditar cada una, publicar en GitHub + instalación local y terminar con auditoría final. El usuario confirmó que NO existe una instalación en uso: se creó una nueva con DB vacía. No promover las cinco bases demo/QA. El usuario pide documentación sin huecos y directrices que se relean tras cada compactación. Publicar/mergear/instalar ya está autorizado; no repetir preguntas de permiso rutinarias. Último mensaje: «segui».

No hay originales/contratos/verdad de un cliente real ni Windows/Excel del operador. No inventar esos datos ni declarar aprobadas esas validaciones. No usar agentes secundarios sin instrucción explícita aplicable. Validaciones pesadas secuenciales en este host.

## Estado de GitHub y código

- Repo: Juan4787/Calibre; cwd /home/usuario/CascadeProjects/CALIBRE.
- Rama local recién creada: **engineering/performance-0.3.1**, desde main **7724b5ad19247df16e9a2e017b16c6e8498d12ac**. Se inicia etapa 3; producto todavía 0.3.0, sin cambios de rendimiento. La bitácora histórica íntegra está conservada en WORKLOG.
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
