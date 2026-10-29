# Continuidad obligatoria — entrega 0.3.1 y auditoría final

Leer completo al comenzar y después de cada compactación, junto con [AGENTS.md](../AGENTS.md), el [plan](STAGED_HARDENING_2026_10_29.md) y el [recibo de etapa 3](qa-evidence/2026-10-29/stage3/receipt.json). La cronología anterior, incluidos todos los fallos y sus correcciones, está en [WORKLOG](WORKLOG_2026_10_29.md). Este archivo contiene el estado vigente.

## Encargo y autorización

El usuario autorizó implementar las recomendaciones de la auditoría por etapas, auditar cada etapa, publicar en GitHub y entregar una instalación local, terminando con auditoría final. Aclaró que no había instalación en uso: se creó una base nueva. Exigió documentación sin huecos y directrices obligatorias después de cada compactación. Publicar, mergear e instalar dentro del alcance ya están autorizados; no pedir confirmación rutinaria otra vez.

No se aportaron originales, contrato ni verdad independiente de un cliente real. Windows/Excel del operador y backup fuera del equipo no están acreditados. No inventar aprobaciones ni confundir fixtures con datos operativos. No delegar sin instrucción explícita. Ejecutar QA pesada secuencialmente. Nunca subir bases, credenciales, tokens ni trazas con sesiones.

## Resultado y código publicado

Las tres etapas están entregadas. La [auditoría final](FINAL_AUDIT_2026_10_29.md) y su [recibo](qa-evidence/2026-10-29/final/receipt.json) contrastan los doce puntos originales, A01–A03/N01–N07 y las ocho mejoras propuestas. No se detectó un defecto económico P0/P1 reproducido abierto en el alcance habilitado probado; esto no es certificación universal ni aprobación comercial.

- **0.2.0:** certeza/integridad. PR #1/main 30d774c; corrección de instalación CI PR #2/main 7dbc16d. Release e instalación verificadas. Gates 40833070930 y 40851752374 aprobados. [Recibo](qa-evidence/2026-10-29/stage1/receipt.json).
- **0.3.0:** operación. PR #3/main 7724b5ad19247df16e9a2e017b16c6e8498d12ac. CI PR/main/tag 40924686583/40925405676/40925586805 aprobadas, assets idénticos e instalación efectiva antes de 0.3.1. [Recibo](qa-evidence/2026-10-29/stage2/receipt.json).
- **0.3.1 vigente:** recursos/distribución. [PR #4 merged](https://github.com/Juan4787/Calibre/pull/4), main/tag **002ca84c592481083470a701e78d66a496d50ddf**. Head revisado **85a6192a9b3b905f76785ae0f54a150886452d1e**, mismo árbol **40c85f58af1a29ea66f3ce0e80d0a1f5db28a943**. [Release pública](https://github.com/Juan4787/Calibre/releases/tag/v0.3.1) desde 2026-10-29T19:19:05Z. Cuatro archivos descargados idénticos. No reemplazar assets existentes.

Rama de cierre: `engineering/final-audit-0.3.1`, desde 002ca84. Sólo documentación, recibos y runner de QA; no cambió ningún archivo del producto. Obtener procedencia documental sin referencia recursiva:

```sh
git log -1 --format=%H -- docs/CONTINUATION.md
git status --short
gh pr list --state all --head engineering/final-audit-0.3.1
```

La documentación se publica mediante PR protegido y sus dos checks. Antes de responder al usuario se debe comprobar merge y servicio. El tag/paquetes siguen vinculados a 002ca84 aunque main avance con documentación; no reconstruir ni retaguear para incorporar recibos posteriores.

## Instalación efectiva y datos

- **http://127.0.0.1:8765**, servicio de usuario **calibre-freight.service**, enabled/active; listener sólo en loopback comprobado en el PID real.
- Root **/home/usuario/.local/share/calibre**, modo 700; `current` → `releases/0.3.1`. Python **/home/usuario/.local/share/calibre/releases/0.3.1/bin/python**, fuera del checkout.
- DB **/home/usuario/.local/share/calibre/workspaces/default/audit.db**, modo 600, schema 2. Última inspección real: cero corridas, fuentes, configuraciones, decisiones e importaciones. El usuario puede usarla desde ahora: reconsultar antes de actualizar; no generar fixtures allí.
- Launcher **/home/usuario/.local/bin/calibre-freight** limpia PYTHONPATH. Unit **/home/usuario/.config/systemd/user/calibre-freight.service**.
- Activación **2026-10-29T19:19:53.315051Z**. Backup integral previo **/home/usuario/.local/share/calibre/backups/before-0.3.1-20261029T191951121630Z/manifest.json**. DB principal SHA **f3ccc23c7947c018a0f755c6eded5a33fe512476b1dba79d86f2eb441f5d21c2**. Hashes, quick_check, foreign_key_check y filas frente al backup aprobados.
- Entornos 0.2.0/0.3.0 y backups anteriores schema 1 conservados. No borrar ni abrir una DB nueva con código anterior a la fuerza. Corridas históricas necesitan su artefacto original.
- Cinco bases originales **.local/*.db** no promovidas ni migradas; todas sus filas lógicas iguales a las copias iniciales: [recibo](qa-evidence/2026-10-29/stage3/original-databases-preserved.json).

Artefacto motor **dca7228d52b7db230a57a181bd71e8b8d9842960b5b941a247bba5941a50514e**. JS **de7a38081b973cdad0bb445922028d25f029918ce04994914e99dc96ceca70be**.

| Asset definitivo | SHA-256 |
|---|---|
| freight_audit-0.3.1-py3-none-any.whl | 9a1730d49aa1117a1114046c20483086995e0ce21a2b09d7e3380af6a6861795 |
| freight_audit-0.3.1.tar.gz | b39af9df754f8d48bbe02444fc710e820da20bfc7731e503d735beae2906cc28 |
| delivery-verification.json | 66548c9810c2fe9ac8658abd7a4ae85f0eb59919b929153f3364c63a6ac3c426 |

El cuarto asset es SHA256SUMS.txt. Dos builds de cada paquete idénticos en bytes, Python 3.12.3/zlib 1.3, herramientas fijadas, epoch 1793301115; wheel 25 miembros y sdist 361. Alcance ligado a esa toolchain. El sdist candidato anterior a correcciones systemd/locks/QA nunca se publicó y no debe reutilizarse.

## Verificación ejecutada

- `scripts/verify.sh`: **354 passed**, dos deprecaciones TestClient; lint/formato/tipos/matriz/JS/compilación/build aprobados. [Log](qa-evidence/2026-10-29/stage3/verify-354.log).
- CI exacta PR **40936962120**, main **40937886279**, tag/release **40938020352** aprobadas. El tag incluye doble build estricto, instalación aislada y E2E.
- Nightly **40934858380**, mismo producto: **20/20 mutaciones**, **41/41 fallas** (33 P0/8 P1), **12/12 controles** sin falsos positivos, **62/62 imports**, 23 tests intensivos y E2E. JSON durables `stage3/nightly-*.json`. Cambios posteriores: lock Windows y QA de identidad, sin cambiar motor/UI.
- Plataformas nativas **40937026441**: Linux 24/24, Windows 24/24 más nueve pruebas del wheel y paridad de tres datasets. `stage3/platform-v3/` conserva identidades físicas y metadata completas.
- E2E real de fuente y wheel final: 1280×720/390×844; importación, conflictos/correcciones, decisiones, control documental, contrato, descargas, replay, aislamiento/restauración y recuperación de red. Tabla de 20.000 filas conservada, preview 20, editor completo. [Recibo](qa-evidence/2026-10-29/stage3/final-installed-browser.json). Dos 503 intencionales; sin excepciones JS/rechazos CSP.
- Ensayo de actualización/reversión: systemd real, ruta con espacios, tres clientes más principal, IDs/hashes y nueva corrida/cliente posteriores preservados; puerto ocupado obliga recuperación automática a puerto/config anterior. [Recibo](qa-evidence/2026-10-29/stage3/real-upgrade-rollback.json). Unit/launcher de ensayo eliminados; DB ficticias privadas conservadas.
- Benchmark comparable, 1000 cargos/tres repeticiones tras warmup: mediana 21,9 → 16,0007 s; pico 181,74 → 168,11 MiB. XLSX/ZIP son operaciones separadas. No extrapolar.
- **Volumen UI del wheel publicado:** 36.000 operaciones y **UN cargo**, 36.001 registros cotejados; facturado/esperado 100, diferencia 0, control coincidente, replay/exportaciones reales. Request máximo 1567 bytes; JSON completo 47.272.034 bytes idéntico en ZIP, originales/manifiesto/CLI verificados. XLSX excedió presupuesto XML: advertencia y JSON/originales íntegros, sin planilla parcial. 110,216 s; pico servidor 876,03 MiB; mínimo host 1107,60 MiB; watchdog sin aborto. [Recibo](qa-evidence/2026-10-29/stage3/published-ui-volume.json). Runner `scripts/audit_ui_volume.py`; comando/guardas en informe final. No son 36.000 cargos ni un cliente real.
- **Servicio operativo, sólo lectura:** Chromium a las 22:33:04Z, ambos anchos, doce GET, sin demo/cargas; filas de todas las tablas idénticas antes/después, quick_check/FK aprobados, sin JS/desborde. [Navegador](qa-evidence/2026-10-29/final/live-browser.json), [salud/permisos/backup](qa-evidence/2026-10-29/final/live-readback.json).

No repetir suites pesadas aprobadas sin cambio aplicable o preocupación nueva. La CI del PR documental ejecutará los checks requeridos; los paquetes no se alteran.

## Contratos, límites y fallos que conservar

[ENGINE_0_3_0](ENGINE_0_3_0.md) explica operación, control, contratos, espacios y restauración; [ENGINE_0_3_1](ENGINE_0_3_1.md), recursos/distribución. Límites: 25 MiB tabular, un millón de celdas, 128 MiB normalizado, dos millones de unidades de trabajo, 256 MiB XML conservador y 500 MiB por bundle sin comprimir. Son presupuestos de trabajo/representación, no un máximo universal de RSS. Dividir conservando completa cada obligación/consolidación y su evidencia.

Fraction coteja conservación del facturado; se verifican hashes del historial antes de mostrar importes y fuentes para reportes/replay. Procedencia cotejada por reimportación comparte lector de producción: no es un segundo lector independiente. Ambos golden completos sólo cambiaron engine_version. Refactor matching puro/tipado acotado; `_audit` conserva deuda de tamaño. Modelo/JSON/HTML aún pueden estar en memoria; configuraciones avanzadas usan JSON. Catorce anclas/mutaciones no cubren todo el intérprete.

Fallos causalmente corregidos y preservados:

- systemd: comillas inválidas de WorkingDirectory y stop sin PID ocultando error; parser real/ensayo completo aprobados. Segundo intento: lifecycle de httpx del runner, corregido sin relajar asserts. [Cronología](qa-evidence/2026-10-29/stage3/SYSTEMD_REHEARSAL.md).
- Windows **40934863136**: faltaba colorama condicional en lock Linux. Se fijó 0.4.6 con marker/hashes oficiales; closure/pip Windows posteriores aprobados.
- Paridad **40935692521**: Python Linux 3.12.15/Windows 3.12.10 cambiaban IDs físicos por diseño. QA v3 verifica cada preimagen/metadata y compara todo salvo metadata.python. No modifica corridas ni omite hashes de resultado/trazas/versiones/bibliotecas. Evidencia v2 fallida conservada; v3 regenerada nativamente.

## Operación y eventual reversión

```sh
systemctl --user status calibre-freight.service
curl --fail http://127.0.0.1:8765/api/health
```

`python3 scripts/install_local.py --rollback` conserva bases posteriores, clientes nuevos y auxiliares; restaura backups/configuración/puntero y verifica salud. `--recover` atiende activación interrumpida con recibo pendiente. No ejecutar rollback de prueba sobre la instalación en uso: ya se ensayó aparte. Clientes nuevos preservados pueden requerir restauración como copia con el motor que los creó; no fusionar ni descartar datos.

Main exige PR/dos checks strict/protección de admins; no hay revisión humana externa obligatoria. Conector GitHub rechazó escrituras 403; `gh` del propietario funciona. Si `gh pr edit` falla por projectCards, usar PATCH REST/JSON de archivo. Merge con SHA exacto revisado; no imprimir credenciales. Netlify no acredita backend: destinos entregados son GitHub más instalación local.

## Próxima acción exacta

1. Revisar diff/enlaces/recibos/ausencia de datos privados. Ruff/formato/compilación del runner nuevo; su ensayo real con wheel definitivo ya pasó.
2. Commit/push de `engineering/final-audit-0.3.1`, PR a main. Esperar ambos checks del SHA exacto y mergear mediante protección vigente. Consultar Git/PR para procedencia documental, sin insertar recursivamente el SHA del propio documento.
3. Comprobar merge/árbol remoto, release pública con cuatro assets y servicio 0.3.1. La DB puede recibir uso legítimo: no exigir que siga vacía ni alterarla para coincidir con un recibo histórico.
4. Entregar respuesta final con URL, release e informe. No dejar publicación autorizada pendiente ni pedir aprobación rutinaria.

Tras merge estos pasos son historia del cierre, no motivo para abrir otro PR idéntico. Retomar sólo si GitHub demuestra un paso faltante o aparece un fallo nuevo. Hechos externos pendientes: cliente real/verdad independiente, equipo y Excel del operador, backup fuera del equipo/ejercicio operativo. Cambios económicos o de integridad futuros exigen nueva versión/evidencia.

Temporales privados: **/tmp/calibre-implementation-20261029-CvSz5k**. Evidencia durable: `docs/qa-evidence/2026-10-29/`. Worktree inmutable `stage3-final-source`, detached 002ca84; paquetes/readback `stage3-final-assets/` y `stage3-final-readback/`. No depender de /tmp para operar: scripts, hashes, comandos, protocolos y recibos están versionados; entornos/backups reales, en el root privado de instalación.
