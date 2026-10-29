# Auditoría final — Calibre / Freight Audit 0.3.1

Fecha: 29 de octubre de 2026. Estado: tres etapas publicadas, instalación 0.3.1 activa y auditoría de ingeniería final completada, con los límites explícitos de este informe. El [recibo final](qa-evidence/2026-10-29/final/receipt.json) identifica el alcance y la evidencia del destino efectivo.

**Dictamen de ingeniería.** Se corrigieron los defectos reproducidos del alcance original y se entregaron tres etapas operativas: 0.2.0, 0.3.0 y 0.3.1. Las comprobaciones ejecutadas sostienen el uso local supervisado dentro de los límites descritos. No se detectó un defecto económico P0/P1 abierto en los mecanismos y entradas habilitados que se probaron. Esto no certifica contratos, documentos de un cliente, identidad del operador ni todos los archivos/combinaciones posibles. Una aprobación económica exige la verdad independiente y la revisión del responsable.

## Qué se entregó y qué se verificó realmente

| Entrega | Resultado comprobado |
|---|---|
| 0.2.0 — certeza e integridad | Fechas civiles, explicit sin corroboración en revisión, procedencia cotejada, fuentes obligatorias para reportes, tipos semánticos, XLS oculto, límites CLI, oráculos ampliados, gates causales y protección de main. Publicada, instalada y auditada antes de 0.3.0. |
| 0.3.0 — operación | Importaciones conservadas en servidor y requests por referencia; control documental integrado; respaldo contractual estructurado; corridas relacionadas sin sobrescribir; espacios de cliente y backup/restauración como otra base. Publicada, instalada y auditada antes de 0.3.1. |
| 0.3.1 — recursos y distribución | Reportes progresivos a archivo, presupuestos, integridad del historial, cotejo racional de totales, fase pura tipada de matching, paquetes reproducibles, locks con hashes y actualización/reversión de todos los clientes. Publicada y activa. |

Release definitiva: [v0.3.1](https://github.com/Juan4787/Calibre/releases/tag/v0.3.1). Fuente certificada/tag/main merge: **002ca84c592481083470a701e78d66a496d50ddf**; [PR4](https://github.com/Juan4787/Calibre/pull/4). Árbol idéntico al head revisado 85a6192: **40c85f58af1a29ea66f3ce0e80d0a1f5db28a943**. La documentación posterior no reemplaza el código ni los assets de ese tag.

Instalación efectiva: **http://127.0.0.1:8765**, servicio de usuario calibre-freight.service activo/habilitado. current apunta a ~/.local/share/calibre/releases/0.3.1. Base operativa: ~/.local/share/calibre/workspaces/default/audit.db, schema 2. Activación: 2026-10-29T19:19:53.315051Z. No se cargaron fixtures en esta base. Las cinco DB anteriores del checkout permanecen separadas y con todas sus filas conservadas frente a sus backups iniciales.

## Evidencia y límites de cada comprobación

| Comprobación | Resultado | Límite de la evidencia |
|---|---|---|
| Verificación canónica | 354 pruebas; Ruff, formato, mypy de producto y QA, matriz, JS, compilación y build aprobados | Dos deprecaciones del adaptador TestClient; no son fallos económicos. No equivale a cobertura exhaustiva. |
| CI del head revisado | [40936962120](https://github.com/Juan4787/Calibre/actions/runs/40936962120), ambos checks aprobados | El merge conserva exactamente el árbol revisado. |
| CI de main | [40937886279](https://github.com/Juan4787/Calibre/actions/runs/40937886279), aprobada | SHA exacto de la entrega, no una ejecución histórica de otro código. |
| Gate completo del tag | [40938020352](https://github.com/Juan4787/Calibre/actions/runs/40938020352), aprobado | Suite, build estricto y wheel instalado/E2E en entorno aislado. |
| Mutaciones | 20/20 detectadas, baseline válido | Mutantes definidos, no todo bug posible. |
| Fallas dirigidas | 41/41 detectadas/prevenidas; 33 P0 y 8 P1 | Corpus de fallas sintéticas, no una tasa universal de detección. |
| Controles sanos | 12/12, sin falsos positivos en esa muestra | No estima falsos positivos comerciales. |
| Importación adversarial | 62/62 casos | Incluye política de ocultos; no todos los layouts empresariales. |
| Nightly intensivo | [40934858380](https://github.com/Juan4787/Calibre/actions/runs/40934858380), aprobado | Mismo producto/artifact final; posterior cambio QA sólo separó identidad física/portable y fijó dependencia condicional Windows. |
| Linux/Windows nativos | [40937026441](https://github.com/Juan4787/Calibre/actions/runs/40937026441): 24/24 por plataforma, nueve pruebas adicionales del wheel en Windows y paridad de tres datasets | Runners reales; no Excel de escritorio ni instalación del operador. |
| Navegador real | Chromium 153, 1280×720 y 390×844, fuente y wheel final instalado fuera del checkout | Importaciones, matching, decisiones, correcciones, control documental, descargas, replay, aislamiento/restauración y recuperación de conexión; no todos los navegadores. |
| Configuración grande | 20.000 filas conservadas, preview de 20 filas y editor completo; sin desborde en ambos anchos | Es tabla contractual, no 20.000 cargos ni aprobación del contrato. |
| Build local final | Dos wheels y dos sdists idénticos en bytes; contenidos/RECORD intactos | Fuente 002ca84, Python 3.12.3, zlib 1.3, herramientas fijadas y epoch 1793301115. No garantiza bytes iguales con cualquier compresor/toolchain. |
| Instalación wheel/sdist | Ambos instalados fuera del checkout, pins/pip check/recursos/demo/replay/exportación aprobados | Linux de este host; instalación Windows se prueba aparte en su runner. |
| Actualización/reversión | Servicio systemd real, tres clientes más la base principal; identidades/hashes conservados; corrida y cliente posteriores preservados; puerto ocupado provoca recuperación automática | Datos ficticios y raíz aislada. No demuestra recuperación física de un disco perdido. |
| Publicación | Cuatro archivos descargados idénticos en bytes/hashes a los certificados | No se reconstruyeron paquetes al subir. Hashes no equivalen a firma externa. |
| Activación local | Servicio, versión, artefacto, JS, DB, backup y filas históricas comprobados | Base vacía al corte; no se presenta como adopción comercial. |

La [auditoría independiente inicial](qa-evidence/2026-10-29/initial-audit/AUDITORIA.md) conserva las reproducciones originales y su clasificación. Evidencia durable: [etapa 1](qa-evidence/2026-10-29/stage1/receipt.json), [etapa 2](qa-evidence/2026-10-29/stage2/receipt.json), [etapa 3](qa-evidence/2026-10-29/stage3/receipt.json). Los archivos detallados se encuentran junto a cada recibo. Los recibos añadidos en este cierre corresponden a pruebas ficticias y acotadas; las bases, volcados y nuevas trazas de sesión quedan fuera del repositorio.

## Contraste final con los doce puntos aportados

| Punto original | Conclusión final | Mecanismo y prueba |
|---|---|---|
| 1. Explicit contradictorio | Corregido; no confirma importes por esa vinculación | Política explicit-consistency-v3, protección de candidatos y obligaciones relacionadas. tests/test_explicit_link_conflicts.py, test_matching_uncertainty.py y test_audit_hardening.py; E2E conserva el conflicto, explica el motivo, corrige creando otra corrida y verifica exports/replay. |
| 2. XLSX-11/nightly | Corregido el oráculo, conservada la defensa | Fila oculta se rechaza; copia visible controlada se acepta. Corpus 62/62 y nightly completo actuales aprobados. No se hizo que el importador aceptara ocultos para pintar verde el test. |
| 3. Fecha con hora/zona truncada | Corregido | Mapping sólo admite fecha civil, sin descartar hora/zona silenciosamente. Regresiones CSV/XLSX/constantes/directivas y frontera de versiones. No se inventó una política contractual de conversión UTC. |
| 4. Procedencia no cotejada | Corregido el defecto reproducido; independencia limitada y explícita | Reimportación coteja original+mapeo+coordenadas+transformación+valor. Importaciones inmutables del servidor y referencias impiden sustituir registros desde el navegador. Alteraciones de dato/cita se rechazan. Se reutiliza lector de producción: es cotejo, no un segundo lector independiente ni prueba de autenticidad documental. |
| 5. Materialización de reportes | Corregido el mecanismo principal y medido | XLSX write-only, generadores/estilos compartidos; ZIP/HTTP/CLI a archivos y copias acotadas; JSON por bloques; fuentes de a una. El modelo verificado/JSON parseado y HTML todavía pueden estar en memoria. Helpers de bytes siguen para llamadores explícitos pequeños. Presupuestos efectivos, no una garantía universal de RSS. |
| 6. Gates/protección | Implementado y verificado en destino | Main exige PR y dos checks strict, aplica a admins, sin force/delete. Corpus causal está en PR. CI main y tag finales aprobadas. No hay revisión humana externa obligatoria porque el repo tiene propietario único; no atribuirla a los checks automáticos. |
| 7. Oráculos independientes | Ampliados; no se declara exhaustividad | 14 anclas manuales con importes e identidades semánticas; referencia racional, propiedades, controles negativos y 20 mutaciones. Fraction verifica control externo y conservación del facturado sin repetir el motor. Quedan combinaciones del intérprete y contratos reales fuera de esas muestras. |
| 8. Lecturas CLI previas a límites | Corregido en las superficies auditadas | Lecturas acotadas y archivos regulares para tablas/JSON/adjuntos; límites por clase y proyecto; ZIP verificado desde archivo. Rutas externas requieren autorización explícita del operador. No se ensayó un OOM destructivo. |
| 9. Reportes sin originales | Corregido | Store.load verifica originales; canonical/HTML/XLSX/ZIP y replay rechazan fuentes ausentes/alteradas. El historial verifica además hashes antes de mostrar importes. tests/test_audit_hardening.py y test_resource_delivery.py. |
| 10. Conteo de reglas | Corregido y visible | Suma versions[].rules[], no reglas fuera de versiones. E2E prueba tres acuerdos/cinco versiones/diez reglas. |
| 11. Reproducibilidad | Implementada y comprobada desde tag exacto | Normalización de metadata ZIP/tar/gzip, SOURCE_DATE_EPOCH del commit; dos archives limpios deben coincidir en bytes. Locks con hashes de todas las distribuciones y marker Windows; pip real en Linux/Windows. Readback de cuatro archivos idéntico. |
| 12. Responsabilidades de _audit | Refactor acotado aplicado | prepare_matching es fase pura tipada con presupuesto previo; se conserva la separación de evaluación/resumen y el motor determinista. Golden completo idéntico salvo versión. No se reescribió todo _audit: su tamaño restante es deuda de mantenibilidad, no un defecto económico demostrado. Cualquier extracción futura debe conservar las mismas trazas y anclas. |

El punto 12 se trata como recomendación de mantenibilidad, no como justificación para cambiar semántica o rehacer el stack. El punto 7 se considera ampliación demostrada, no certificación universal. Esta distinción conserva el alcance y evita presentar cantidad de pruebas como prueba de ausencia de errores.

## Hallazgos independientes A/N

| Hallazgo | Estado y evidencia final |
|---|---|
| A01 — pérdida de hora/zona | Formatos no civiles rechazados antes de importar; fecha contractual no inventada. |
| A02 — fidelidad original→dato | Alteración posterior del normalizado/procedencia rechazada al guardar; referencias conservadas del servidor. Alcance/independencia del lector explícitos. |
| A03 — integridad desigual entre exportes | Todos los reportes requieren originales verificables; corrupción no se convierte en un reporte respaldado. |
| N01 — explicit sin corroboración | REVIEW, preflight visible, sin esperado/diferencia confirmada y protección relacionada; decisión humana no reescribe el hallazgo. |
| N02 — control XML rompe Excel/ZIP | XLSX devuelve limitación clasificada; ZIP conserva originales y JSON con advertencia, sin error interno del servidor ni truncamiento silencioso. |
| N03 — archivo admitido imposible por payload | Requests reales de UI por referencias, verificación/ejecución/replay y exportaciones con 36.000 operaciones. JSON completo de 47.272.034 bytes y solicitud máxima de 1567 bytes. Presupuesto Excel efectivo; detalle abajo. |
| N04 — carga no iniciable por teclado | Botón nativo/foco/Enter abre filechooser real; labels persistentes y carga/regreso al flujo probados. La automatización no acredita toda combinación de lector de pantalla/teclado/sistema. |
| N05 — ocultos XLS/XLSX inconsistentes | Matriz hoja/fila/columna oculta y copias visibles; XLS conserva opt-in de valores guardados y rechazo de ocultos detectables. No se afirma evaluar fórmulas Excel. |
| N06 — date/text indistinguibles | Atom conserva tipo semántico; comparación incompatible queda indeterminada. Regresiones date/text/decimal/boolean/grupos; artefactos históricos conservados. |
| N07 — control externo depende de Decimal ambiental | Fraction elimina dependencia del contexto; extremos admitidos y contextos alterados comprobados. Se corrigió un falso rechazo del verificador, no se inventó un fallo del motor sano. |

## Seguimiento de las ocho mejoras de producto propuestas

| Propuesta | Entrega y límite actual |
|---|---|
| Control documental integrado | Inventario de fuentes, cantidades e importes por moneda; estados pendiente/coincidente/discrepante, visibles y ligados a la corrida. El responsable debe aportar el control independiente real. |
| Configuración legible | Vista de celda, transformación y resultado; resumen de versiones, fórmulas, unidades, bandas, vigencias y tolerancias. Las configuraciones avanzadas siguen usando JSON; no se declara un constructor visual completo ni ejemplos comerciales aprobados. |
| Respaldo contractual | Original preservado por hash, página/cláusula y aprobación declarada vinculadas a versión/regla. No autentica identidad ni validez jurídica. |
| Relación entre corridas | Revisión relacionada con motivo y comparación, sin sustituir resultados ni decisiones de la anterior. |
| Espacio de cliente visible | Nombre, ruta y base separada; configuraciones y biblioteca por espacio; aislamiento positivo/negativo probado. No se convierte en un SaaS multiusuario. |
| Backup/restauración practicables | Copia verificada, recibo de preparación y restauración como espacio nuevo con replay. Actualización/reversión integral ensayada. Destino externo y ejercicio con operador siguen pendientes de hechos externos. |
| Volumen/tareas largas | Referencias pequeñas, trabajo pesado serializado fuera del event loop, estado ocupado, recuperación de conexión y presupuestos previos. Se midieron los recorridos indicados; no hay estimador universal de tiempo ni certificación de cualquier volumen. |
| Validación con cliente real | Protocolo y controles documentados. No ejecutada porque no se aportaron originales, contrato ni verdad independiente de un cliente. No se presenta un fixture como sustituto. |

## Pruebas de recursos y volumen

La comparación reproducible de 1.000 cargos utiliza warmup y tres procesos medidos, mismos canales y oráculos. La mediana del pipeline pasó de 21,9 s a 16,0007 s; el pico de 181,74 MiB a 168,11 MiB. El benchmark pide XLSX y después ZIP como dos operaciones independientes. No es la latencia de un único clic ni una curva de escala; no se extrapola a 50.000/100.000 cargos.

Se probó además el caso que antes superaba el request de 32 MiB desde controles reales de Chromium: 36.000 operaciones y UN cargo facturado, con control externo de cantidades/importes/originales. Facturado: 100; esperado: 100; diferencia confirmada: 0; 36.001 registros cotejados, replay y descargas reales. El request máximo fue de 1567 bytes; el JSON de 47.272.034 bytes se conservó completo e idéntico al miembro del ZIP, que pasó verificación/replay CLI instalado. Esta prueba no calcula 36.000 cargos.

La planilla excedió el presupuesto conservador de XML: el ZIP contiene advertencia, JSON y originales íntegros, sin XLSX parcial. Es una restricción operativa efectiva, no una omisión del runner presentada como aprobación de Excel. Si el trabajo necesita Excel, dividir el alcance conservando completas las operaciones/cargos/evidencia de cada obligación o revisar otra representación explícita. No separar una consolidación y asumir que el problema económico es el mismo.

El ensayo final del wheel publicado duró 110,216 s: pico del servidor de 876,03 MiB y mínimo MemAvailable del equipo de 1107,60 MiB, sin aborto del watchdog ni excepciones de JavaScript. [Recibo](qa-evidence/2026-10-29/stage3/published-ui-volume.json) y [captura](qa-evidence/2026-10-29/stage3/published-ui-volume.png). El ensayo candidato anterior permanece separado como evidencia histórica. Los presupuestos no garantizan un máximo universal de memoria de todas las aplicaciones del equipo.

Reproducción del ensayo mantenido, con una carpeta de salida nueva y al menos 1400 MiB disponibles al iniciar (el watchdog interrumpe si el servidor supera 1100 MiB o el equipo baja de 300 MiB disponibles):

```sh
.venv/bin/python scripts/audit_ui_volume.py \
  --runtime-python /home/usuario/.local/share/calibre/releases/0.3.1/bin/python \
  --wheel /ruta/descarga/freight_audit-0.3.1-py3-none-any.whl \
  --output-dir /tmp/calibre-volumen-nuevo
```

El runner exige que los archivos del producto instalado coincidan con las fuentes y comprueba el recibo de instalación si existe. Utiliza un servidor, puerto y base temporales; el Python del backend es el instalado, y Playwright pertenece al entorno separado de QA. No cargar estos datos en la base operativa.

## Hallazgos nuevos de esta etapa y cómo se cerraron

- **Historial con resumen alterado.** La lista SQL extraía importes sin verificar hashes. Una prueba modifica un importe después de quitar el trigger y demuestra el rechazo nuevo antes de mostrarlo. La lectura se hace por filas, evitando fetchall de snapshots grandes.
- **Repetir el motor no detecta un bug sistemático del resumen.** Se simuló el mismo resumen erróneo en ambas ejecuciones; la suma independiente de cargos con Fraction impide conservarlo. No valida por sí sola una tarifa contractual falsa pero consistente.
- **Descarga temporal diferida.** La extensión pathsend podía devolver un pathname cuya lectura sobreviviera al cleanup. La respuesta temporal fuerza envío por bloques y limpia en finally también ante desconexión. Pruebas de transferencia completa y corte real simulado, sin publicar un archivo a medio escribir.
- **Recurso antes del costo.** Celdas y normalizado se contabilizan durante importación; asociación/cálculo antes de expandir candidatos; XML antes de temporales enormes; bundle reserva fuentes antes del costo Excel. Un límite rechaza el trabajo completo o clasifica la representación, no confirma un subconjunto económico ocultando el resto.
- **systemd: gramática y recuperación.** Primer ensayo real detectó comillas inválidas de WorkingDirectory y stop de unidad sin PID que ocultaba el fallo. Corregidos con parser real, runtime XDG descartable y root con espacios. Se preservó el recibo interrumpido y se ejercitó --recover. El error de lifecycle de httpx del segundo runner también se conservó y corrigió sin relajar asserts. [Cronología](qa-evidence/2026-10-29/stage3/SYSTEMD_REHEARSAL.md).
- **Lock condicional Windows.** El modo de hashes detectó colorama ausente del lock original generado en Linux. Se fijó 0.4.6 con marker Windows y hashes de todas sus distribuciones, preservando el resto de versiones. Closure oficial y pip nativo posteriores aprobados.
- **Identidad física confundida con paridad semántica.** Los runners usaron Python 3.12.15/3.12.10. El antiguo fingerprint comparaba IDs que ahora incluyen metadata.python; sólo esos IDs/digest diferían. QA v3 conserva metadata e IDs físicos y verifica sus preimágenes, luego compara identidad portable, hashes completos de datos/resultado/motor, hallazgos/trazas y toda metadata salvo campo python. No se transformó evidencia fallida en aprobada: se regeneró nativamente. Alterar ID físico, metadata, pruebas o versión/regla continúa bloqueando el gate.

## Distribución y actualización verificadas

| Archivo publicado | SHA-256 |
|---|---|
| freight_audit-0.3.1-py3-none-any.whl | 9a1730d49aa1117a1114046c20483086995e0ce21a2b09d7e3380af6a6861795 |
| freight_audit-0.3.1.tar.gz | b39af9df754f8d48bbe02444fc710e820da20bfc7731e503d735beae2906cc28 |
| delivery-verification.json | 66548c9810c2fe9ac8658abd7a4ae85f0eb59919b929153f3364c63a6ac3c426 |

SHA256SUMS.txt y los otros tres archivos se descargaron y compararon byte a byte. El wheel tiene 25 miembros y el sdist 361. El candidato previo no se publicó: su sdist precedía las correcciones de instalación/locks/QA. Los assets definitivos proceden del tag/main 002ca84; no se reconstruyeron al subir.

Artefacto motor activo: **dca7228d52b7db230a57a181bd71e8b8d9842960b5b941a247bba5941a50514e**. JS activo: **de7a38081b973cdad0bb445922028d25f029918ce04994914e99dc96ceca70be**. Root modo 700, DB modo 600. El servicio escucha sólo en 127.0.0.1, con un proceso de producto y PYTHONPATH limpiado; QA no reemplazó el ejecutable por el checkout.

Backup previo a 0.3.1: **~/.local/share/calibre/backups/before-0.3.1-20261029T191951121630Z/manifest.json**, con todas las bases registradas al corte. DB principal SHA de backup: **f3ccc23c7947c018a0f755c6eded5a33fe512476b1dba79d86f2eb441f5d21c2**. Copia verificada, todas las filas históricas idénticas antes/después, quick_check y foreign_key_check aprobados. La base tenía cero corridas, fuentes, configuraciones, decisiones e importaciones; el readback operativo no creó ejemplos.

Reversión documentada y ensayada, conservando datos posteriores:

```sh
python3 scripts/install_local.py --rollback
```

Interrupción con recibo pendiente:

```sh
python3 scripts/install_local.py --recover
```

No ejecutar una reversión de prueba sobre datos en uso. Si se necesita revertir realmente, conservar primero DB posteriores/clientes nuevos/auxiliares como hace el instalador. Restaurar la copia correspondiente al schema y activar el entorno anterior conservado. Las corridas históricas requieren su artefacto original para replay; no se recalcularon ni sobrescribieron para pasar pruebas.

## Comprobación final de la instalación activa

La inspección real de sólo lectura abrió la aplicación en 1280×720 y 390×844 con Chromium 153.0.8010.12. Los doce requests fueron GET; no se pulsó la demostración ni se cargaron fixtures. No hubo excepciones JavaScript ni desborde horizontal. Se compararon todas las filas de todas las tablas antes y después: idénticas; quick_check y foreign_key_check aprobados. [Recibo](qa-evidence/2026-10-29/final/live-browser.json), [escritorio](qa-evidence/2026-10-29/final/live-desktop.png), [móvil](qa-evidence/2026-10-29/final/live-mobile.png) y [salud/permisos/backup](qa-evidence/2026-10-29/final/live-readback.json).

Esta inspección del servicio operativo acredita disponibilidad y conservación de datos. Los flujos que crean corridas se probaron por separado con el mismo wheel instalado y bases descartables, identificadas en el recibo E2E.

## Límites y riesgos que permanecen explícitos

1. **Cliente real.** Faltan originales, contrato, período/alcance, responsable y verdad independiente. Ejecutar [el protocolo de cliente real](REAL_CLIENT_VALIDATION_PROTOCOL.md) y [el control externo](EXTERNAL_CONTROL.md) antes de atribuir validez comercial. No se agregaron impuestos, prorrateos ni excepciones sin contrato que los defina.
2. **Independencia finita.** El cotejo usa el lector conservado; 14 anclas, propiedades y mutantes no cubren toda composición del AST. Hashes/replay prueban consistencia e identidad de archivos, no autenticidad, interpretación contractual ni protección contra reescritura coherente de todo por el mismo usuario del sistema.
3. **Plataforma del operador.** Windows nativo en CI sí se ejecutó. Su instalación concreta, Excel de escritorio, antivirus/permisos y procedimiento con el operador no fueron aportados ni certificados.
4. **Respaldo externo.** Se prepararon/verificaron copias y se ensayó restauración. Las copias locales no acreditan recuperación ante pérdida del disco; falta confirmar destino fuera del equipo y ensayo operativo del responsable.
5. **Volumen.** Límites visibles y efectivos pueden rechazar un lote o la representación Excel. No hay certificación de 50.000/100.000 cargos ni de todo hardware. Los intervalos medidos se identifican arriba; no se presenta una omisión de exportes como pipeline completo aprobado.
6. **Modelo local de confianza.** Un usuario del sistema, SQLite sin cifrado propio ni firma externa del operador. No es SaaS, aislamiento entre usuarios hostiles ni autenticación de una aprobación legal. La referencia contractual/aprobación conservada es declarada y ligada por hash a la corrida.
7. **Mantenibilidad/UX.** El núcleo conserva una fase extensa después del refactor acotado; el editor JSON sigue siendo necesario para configuraciones avanzadas. Extraer fases futuras o agregar asistentes requiere las mismas regresiones y ejemplos aprobados, no reinterpretar tarifas automáticamente.
8. **Dependencias.** Pins/hashes verifican identidad y compatibilidad de archivos; no constituyen una revisión universal de vulnerabilidades. El bootstrap/descarga inicial necesita red; el camino de auditoría sigue siendo local/offline. Cambiar herramientas o Python exige repetir los gates aplicables.

Estos límites tienen significado operativo y no se ocultan bajo un resultado verde. No se demuestra que exista un defecto económico residual por el solo hecho de conservarlos.

## Cómo continuar sin perder información

- Leer AGENTS.md, CONTINUATION.md y STAGED_HARDENING_2026_10_29.md al iniciar o tras compactación. WORKLOG_2026_10_29.md conserva cronología, fallos y decisiones.
- Consultar ENGINE_0_3_0.md para operación/espacios/control/contratos y ENGINE_0_3_1.md para presupuestos, distribución, actualización/reversión y evidencia de plataforma.
- Verificar estado real de servicio/DB/HEAD y no inferir publicación de un plan. Los hashes/CI/tag de esta entrega están arriba; la bitácora registra el commit posterior de documentación.
- Reproducir la verificación con scripts/verify.sh y los tiers de scripts/run_ci_tier.sh. Ejecutar cargas pesadas de a una. Los scripts de auditoría usan raíces nuevas y datos ficticios; nunca apuntarlos a una DB operativa para generar fixtures.
- Mantener los assets de releases existentes intactos, las versiones anteriores, manifests/backups y recibos. Cambios económicos o de integridad posteriores requieren nueva versión y su propia evidencia.
