# Auditoría independiente de CALIBRE / Freight Audit

Fecha: 29 de octubre de 2026. Revisión sin cambios al código ni a bases de la aplicación.

**Dictamen.** El proyecto tiene buenas defensas para un prototipo local: cálculo decimal, incertidumbre explícita, historia conservada y reportes reconciliables. Hay defectos reproducidos y decisiones de certeza que conviene resolver antes de ampliar el uso. La ejecución satisfactoria de las pruebas existentes no cierra estos hallazgos. No hay evidencia en esta revisión para habilitar decisiones autónomas de pago.

## Base y alcance

- GitHub `main`: `fd62f05392f819896589c2a3b271ad49cdcfafbd`, código publicado 0.1.0. Confirmado mediante la API de GitHub.
- Carpeta local: el mismo HEAD con cambios anteriores a esta revisión y versión declarada 0.1.2. Incluye ONR-001..005 y nuevas pruebas, con archivos modificados y sin seguimiento.
- La comparación del estado Git al principio y al final no cambió. Las reproducciones, bases descartables, capturas y resultados están exclusivamente en esta carpeta temporal.
- Se leyó la auditoría aportada, el núcleo, modelos, reglas, importación, proyecto/CLI, persistencia, reportes, API, UI, verificadores y workflows. Se usaron datos completamente ficticios.
- Se ejecutó la suite completa **del árbol local**. Para el commit publicado se extrajo su código a una carpeta temporal y se reprodujo el conflicto explícito. No se ejecutó una segunda suite completa del código publicado.
- No se modificó ni publicó ninguna versión. No se ensayaron datos reales, Windows/Excel de escritorio, 50.000/100.000 cargos ni todos los navegadores.

Metadatos y estado: [audit_metadata.json](./audit_metadata.json), [git-status.txt](./git-status.txt). El hash del núcleo local auditado es `a90bebb6296256569bf2f01babb7ab1cb4e82addeb5e44c3c1c2db9268d59ea3`.

## Evidencia ejecutada

| Comprobación | Resultado | Alcance |
|---|---|---|
| Pytest del árbol local | 276 passed, 2 warnings; 21,51 s | Suite existente; no implica cobertura universal |
| Ruff lint y formato | Sin errores; 51 archivos formateados | src, tests, scripts y qa |
| Mypy | Sin errores en src y en qa/scripts seleccionados | No demuestra corrección económica |
| Matriz QA y sintaxis JS | Sin errores | Consistencia de catálogo y sintaxis |
| pip check | Sin dependencias rotas | Compatibilidad declarada del entorno instalado |
| Corpus adversarial de importación | 61/62; falla XLSX-11 | Reproduce el oráculo incompatible |
| E2E del repositorio en Chromium real | passed | Importación, matching, decisiones, evidencia nueva, historia, exportaciones, replay, carreras y paginación |
| Inspección adicional de teclado y responsive | Defecto de carga por teclado confirmado | 1280×720 y 390×844; sin desborde general en esas vistas |
| Benchmark completo de 1.000 cargos | 3 repeticiones medidas tras warm-up; referencias del runner coincidentes | No extrapolado a otros tamaños |
| Pruebas dirigidas independientes | Casos detallados a continuación | Oráculos simples escritos para esta revisión |

Dos advertencias de la suite pertenecen a deprecaciones de TestClient/httpx/anyio; no se observaron fallos asociados. En el E2E, los errores HTTP esperados de las pruebas de recuperación no se confundieron con excepciones JS. No hubo excepciones JS ni rechazos CSP en sus recorridos.

Navegador: Playwright local, Chromium 153.0.8010.12, porque la sesión no expone herramientas de control de Browser. [Recibo E2E](./browser/result.json), [recibo adicional](./ui_probe_results.json), [traza](./browser/trace.zip).

## Contraste con los doce puntos de la auditoría aportada

| Punto | Veredicto después del contraste |
|---|---|
| 1. Explicit contradice claves | Confirmado por ejecución contra el commit publicado: C1→S2 termina PASS. El caso exacto ya está corregido en el árbol local: REVIEW, sin esperado ni diferencia confirmada. No confundir esa corrección local con una versión publicada. Existe otra política residual, N01. |
| 2. XLSX-11 / nightly | Confirmado localmente y en el log remoto del 28/10: 61/62. El test pide aceptar una fila oculta y la política vigente exige rechazarla. Corregir el test y conservar el control del importador. |
| 3. Fechas textuales con hora/zona | Confirmado a través del importador real CSV y XLSX, y del motor. El mapping personalizado acepta la entrada, descarta hora/zona y permite PASS. Con el formato predeterminado, esa entrada no se acepta. |
| 4. Fidelidad de procedencia | Confirmado mediante dataset alterado después de importar: original peso 9, normalizado 10. Save, replay y verificación del ZIP aceptan la corrida. No se demostró que el importador genere por sí solo esa alteración. |
| 5. Materialización y duplicación de XLSX | Materialización y costo confirmados. Matiz: `export_run()` genera un solo XLSX y extrae los archivos del ZIP. La doble generación ocurre si se pide/mide XLSX y luego ZIP como operaciones separadas. El runner y los recibos existentes ya registran RSS. |
| 6. Gates de CI/protección | Confirmado que main no está protegida y no exige checks. El CI sí contiene lint/tipos/build/E2E y una segunda etapa semántica: no está desprovisto de controles. El corpus adversarial adicional vive en nightly. |
| 7. Oráculos independientes | La referencia racional cubre una familia de precios, no todo el intérprete. También existen tests manuales y propiedades para otras funciones; no afirmar que carecen totalmente de pruebas. Falta ampliar referencias independientes por semántica y combinaciones. |
| 8. Lecturas CLI antes de límites | Confirmado en código. Tablas, adjuntos y JSON pueden leerse completos antes de un control suficiente. Las rutas externas son una decisión de confianza del proyecto local; restringirlas cuando se admita un proyecto ajeno. No se ejecutó un agotamiento de memoria. |
| 9. Reportes sin verificar originales | Confirmado mediante corrupción en base descartable: load/canonical/HTML/XLSX devuelven 200; replay y ZIP rechazan con 422. No se concluye que el importe histórico haya cambiado: cambió la disponibilidad verificable de su respaldo. |
| 10. Contador de reglas | Confirmado estáticamente en main. Corregido en el árbol local mediante suma por versions[].rules[] y verificado en el E2E: 3 acuerdos, 5 versiones, 10 reglas. |
| 11. Reproducibilidad binaria | Los recibos históricos muestran contenido equivalente y bytes distintos. El verificador actual registra `byte_identical=false` sin rechazarlo. No reconstruí paquetes para convertir ese recibo histórico en una prueba nueva. El lock fija versiones, sin hashes obligatorios. |
| 12. Complejidad de _audit | Observación de mantenibilidad fundada. Extraer fases puras y tipos intermedios sería útil; la longitud no constituye por sí sola un defecto económico ni justifica reescribir el stack. |

La auditoría aportada es útil y, en su mayor parte, está bien fundada. Sus prioridades necesitan condiciones explícitas de activación: un timestamp requiere un formato personalizado admitido; corrupción documental, una fuente ya dañada; rendimiento depende del tamaño/equipo; una falla del oráculo es distinta de una regresión del importador.

Referencias remotas comprobadas: [main](https://github.com/Juan4787/Calibre/tree/main), [nightly 28/10](https://github.com/Juan4787/Calibre/actions/runs/40664568845). Las ocho últimas ejecuciones consultadas, del 21 al 28/10, terminaron en failure sobre el mismo SHA. La información de protección se obtuvo de [la API de la rama](https://api.github.com/repos/Juan4787/Calibre/branches/main).

## Hallazgos activos de mayor impacto ya señalados por la auditoría

### A01 — Fecha textual pierde hora y zona — prioridad P0 en esa entrada habilitada

**Reproducción:** mapping `%d/%m/%Y %H:%M:%S%z`; celda `01/05/2026 23:30:00-0300`. CSV y XLSX aceptan una fila y guardan `2026-05-01`. Con V1 hasta el 01/05 y V2 desde el 02/05, se selecciona V1 y se permite PASS de 100.

**Causa:** el validador admite directivas de tiempo; la rama textual de `convert()` hace `strptime(...).date()`. La protección de los datetime nativos no interviene. Referencia: `src/freight_audit/importing.py:95` y `:434`.

**Límite del dictamen:** no hay base para declarar que UTC sea la fecha contractual correcta; falta la política. El defecto demostrado es descartar información admitida sin esa política, en contradicción con la documentación.

**Corrección propuesta:** admitir sólo formatos de fecha civil o exigir una conversión explícita, versionada y visible. Validar el formato al guardar el mapping. **Cierre:** regresiones CSV/XLSX y constantes, medianoche, zona y frontera de versiones; conservar el dato original y evitar confirmación silenciosa.

### A02 — Procedencia conservada no equivale a procedencia cotejada — P1

**Reproducción:** importar original con peso 9; cambiar el valor normalizado y SourceRef.raw a 10; regla 10 ARS/kg y cargo 100. Save, replay y verify_bundle pasan, con PASS de 100 aunque el archivo contiene 9.

**Causa:** se cotejan hashes y consistencia entre motor/snapshot/resultado, pero no celda→transformación→valor. `Store.save()` acepta datasets normalizados aportados por el llamador. Referencia: `storage.py:110`.

**Corrección propuesta:** conservar importaciones verificadas en servidor y auditar sus identidades; validar los valores contra originales/mappings o distinguir procedencia aportada y cotejada. **Cierre:** cambiar celda, fila, columna, transformación, constante y valor normalizado, de a uno, debe producir un rechazo o nivel de confianza menor verificable. Reimportar con el mismo código, por sí solo, no constituye un oráculo completamente independiente.

### A03 — Exportaciones expresan niveles de integridad diferentes — P1

**Reproducción:** después de guardar una corrida válida, alterar únicamente los bytes originales en una base descartable. Se obtienen load=200, canonical=200, HTML=200, XLSX=200, ZIP=422 y replay=422.

**Causa:** `load()` verifica snapshot/resultado, mientras los originales se verifican en replay y bundle. Referencias: `storage.py:175`, `server.py:196`.

**Corrección propuesta:** estado explícito y separado para integridad interna, disponibilidad de fuentes y cotejo de procedencia; exigir la verificación aplicable para reportes presentados como respaldados. **Cierre:** matriz de fuentes ausentes/corruptas frente a todos los endpoints, con información comprensible para el operador.

## Hallazgos y decisiones residuales encontrados en esta revisión

### N01 — Explicit sin candidatos puede confirmar sin corroboración — P1, decisión de producto

**Reproducción:** cargo referencia 99999, explicit→S2 referencia 00002, ninguna operación con 99999. Con cargo 100: PASS, esperado 100. Con cargo 130: FAIL y diferencia confirmada de 30. En ambas ejecuciones preflight informa 0 conflictos y 0 incidencias. [Resultado adicional ejecutado](./uncorroborated_fail.json).

**Causa:** `inspect_explicit_link()` clasifica `no_key_candidates` como válido; preflight no lo cuenta como incidencia. La UI puede decir que las vinculaciones fueron comprobadas con las claves disponibles. Referencias: `engine.py:118`, `engine.py:173`, `static/app.js:1442`.

**Clasificación rigurosa:** la política y un test permiten expresamente este comportamiento. No es una regresión respecto de esa política. Sí es una capacidad de confirmar sin respaldo automático de las claves, que necesita una decisión explícita antes de ampliar uso. Tener valores distintos sigue siendo distinto de tener una clave ausente.

**Propuesta:** distinguir corroborado, desambiguado y aportado sin corroboración; mostrar el último caso en preflight y reportes. Si se admite confirmación, exigir una excepción contractual identificada y respaldada. De lo contrario, REVIEW. **Cierre:** casos sin clave, con clave contradictoria sin candidatos y con candidatos alternativos, más exportaciones y revisión humana sin reescribir el hallazgo.

### N02 — Un carácter de control aceptado rompe XLSX y ZIP — P1

**Reproducción:** CSV con atributo textual mapeado que contiene U+0001. El importador acepta la fila, el motor da PASS y se conserva la corrida. Canonical y HTML responden 200; XLSX y ZIP responden 500. Error de biblioteca: IllegalCharacterError.

**Causa:** el texto puede entrar en SourceRef/raw; openpyxl no admite ese carácter XML. `bundle_bytes()` sólo trata ReportLimitError como ausencia controlada de la planilla. Referencias: `importing.py:530`, `reporting.py:82`, `reporting.py:305`.

**Propuesta:** representar el carácter de forma reversible en la planilla o rechazar de forma explícita el campo si el contrato lo exige; conservar siempre el original y el JSON. Permitir un ZIP completo con advertencia si sólo el XLSX no es representable. No eliminar caracteres silenciosamente ni capturar cualquier excepción como éxito. **Cierre:** CSV, SourceRef, evidencia y decisiones, con controles XML, fórmulas, longitudes y descargas de todos los formatos.

### N03 — Un archivo admitido puede volverse imposible de ejecutar por la UI — P1

**Reproducción real del límite:** CSV de 877.792 bytes, 36.000 operaciones y 0 rechazos. Tras normalizar con procedencia, el request del dataset ocupa 34.364.329 bytes. Límite HTTP: 33.554.432. POST /api/audit/preflight devuelve 413. Las filas están por debajo del máximo del importador; el archivo ocupa menos de 1 MB. La reproducción usa una tabla de operaciones y ningún cargo para aislar el límite; agregar la segunda tabla aumenta el payload.

**Causa:** la UI conserva y vuelve a enviar todos los registros y SourceRef en cada verificación/ejecución. La procedencia puede multiplicar mucho el tamaño de una fuente pequeña. Referencias: `server.py:52`, `static/app.js:1335`.

**Propuesta:** importaciones y borradores conservados en servidor, con referencias pequeñas en las solicitudes; estimación de recursos antes de aceptar el trabajo y límite operativo visible. Subir el máximo HTTP por sí solo desplaza el problema de memoria. **Cierre:** ejecutar desde controles reales un lote cuya representación normalizada supera el antiguo límite, con resultado, reportes y presupuestos de memoria comprobados.

### N04 — No se puede iniciar una carga usando sólo teclado — P1

**Observación en Chromium:** dropzone es DIV, tabIndex=-1, sin role; el input tiene display:none y no tiene label. No hay inputs de archivo en la secuencia de Tab. La secuencia recorre navegación, pasos, nombre, opciones avanzadas y Validar, pero nunca un selector inicial. Con mouse sí se abre filechooser.

**Causa:** sólo existe `dropzone.onclick = () => fileInput.click()` para esa superficie, sin control nativo accesible ni manejo equivalente de teclado. Referencias: `static/app.js:1600`, `:1690`; `static/app.css:790`.

**Propuesta:** botón o label/input con nombre, foco y activación nativos; estado seleccionado anunciado. **Cierre:** completar operaciones→cargos→verificación usando sólo teclado, incluida selección de archivos y retorno de foco. Las pruebas con set_input_files sobre un input oculto no acreditan esa accesibilidad. El buscador de resultados también necesita label persistente; hoy sólo tiene placeholder.

### N05 — La política de datos ocultos cambia al usar XLS — P1 cuando se habilita XLS

**Reproducción:** con el opt-in obligatorio allow_xls_cached_values=true, tres archivos XLS con fila, columna u hoja seleccionada oculta aceptan la fila. La única advertencia es sobre valores guardados/fórmulas; no identifica contenido oculto.

**Causa:** la rama XLS no revisa los indicadores de visibilidad que sí se revisan en XLSX. Referencia: `importing.py:307`.

**Clasificación:** la documentación describe el bloqueo de ocultos específicamente para XLSX; no inventar una garantía contractual universal para XLS. El riesgo operativo es que convertir entre formatos modifica la protección sin explicarlo.

**Propuesta:** aplicar una política equivalente cuando xlrd permite conocer la visibilidad, o exigir conversión/revisión con una advertencia explícita de esa limitación. **Cierre:** matriz XLS/XLSX para hoja/fila/columna oculta y su copia visible, manteniendo coordenadas y valores.

### N06 — El intérprete pierde la diferencia entre fecha y texto — P2

**Reproducción:** condición eq(attr(service_date de tipo date), const("2026-05-01" de tipo text)). Devuelve true y permite PASS. El contrato documenta condiciones tipadas.

**Causa:** Atom conserva el valor Python y unidades, pero descarta Value.type; fecha y texto pasan a ser str y la comparación de tipos Python no los distingue. Referencias: `rules.py:39`, `rules.py:179`.

**Propuesta:** preservar el tipo semántico del operando y definir comparaciones/conversiones admitidas. **Cierre:** matriz date/text/decimal/boolean y grupos heterogéneos; no cambiar semántica histórica sin nueva versión. Este hallazgo no demuestra un error en la aritmética Decimal.

### N07 — El control documental externo depende del contexto Decimal ambiental — P2

**Reproducción:** una corrida con importe permitido de 36 nueves y un control independiente exacto. Con precisión 28, el verificador rechaza por totales y observa 1.000000000000000000000000000E+36. Con precisión 80, los mismos datos pasan. El resultado del motor es idéntico y exacto.

**Causa:** qa/external_control.py suma Decimal fuera de un contexto propio. Referencia: `qa/external_control.py:98`.

**Propuesta:** usar Fraction o un contexto explícito acorde con el dominio y detectar inexactitud. **Cierre:** extremos admitidos, agregados de muchos cargos y contextos ambientales cambiados. El caso prueba un falso rechazo del verificador, no una falsa discrepancia del motor; su frecuencia comercial no está medida.

Evidencia de A01..A03 y N01..N07: [probes.py](./probes.py), [probe_results.json](./probe_results.json), [extra_probes.py](./extra_probes.py), [extra_results.json](./extra_results.json), [payload_probe.py](./payload_probe.py), [payload_results.json](./payload_results.json), [ui_probe.py](./ui_probe.py), [ui_probe_results.json](./ui_probe_results.json).

## Rendimiento medido y recomendaciones de ingeniería

Benchmark sintético de 1.000 cargos, warm-up más tres procesos medidos independientes:

| Etapa | Mediana |
|---|---:|
| Motor | 0,2505 s |
| XLSX individual | 7,9508 s |
| ZIP completo | 10,0802 s |
| Pipeline del runner, que mide ambas exportaciones | 21,4616 s |
| RSS pico registrado | 184,81 MB |

El total del runner no equivale a la latencia de un único clic de exportación: incluye importación, auditoría, guardado, lectura, replay, exportaciones, verificación y API. Las medianas de etapas no deben sumarse como si fueran una misma repetición. Estos números no prueban una regresión respecto del recibo antiguo, ni una curva para otros tamaños. El benchmark sí confirmó los resultados sintéticos de su propio oráculo.

[Resumen](./benchmark/benchmark_summary.json), [entorno](./benchmark/environment.json), [log](./benchmark.log).

Propuestas concretas: Workbook write_only si conserva tipos/estilos/límites, filas generadas progresivamente, evitar listas completas de trazas antes de escribir, ZIP a archivo temporal/stream con presupuesto previo de recursos y reutilización del XLSX únicamente donde se solicitan ambas salidas. Mantener la validación de consistencia de Store.save hasta que otra solución preserve su garantía. Separar tareas de CPU del event loop y mostrar progreso si el volumen real lo justifica.

CLI: lectura acotada de tablas/JSON/adjuntos/ZIP, con presupuestos distintos por clase y total del proyecto. stat previo ayuda, pero no reemplaza una lectura acotada frente a cambios concurrentes o fuentes especiales. No se ensayaron OOM deliberados.

Distribución: resolver primero el estado de versión, publicar sólo un artefacto concretamente verificado cuando se autorice, conservar el motor de corridas antiguas, activar checks requeridos y hacer que la prueba causal mínima acompañe a los PR. Después, normalizar el build y verificar hashes completos si ésa es la garantía deseada. El recibo histórico de contenido equivalente no acredita bytes idénticos de 0.1.2.

Refactor: resultados tipados para matching y asignación; fases puras para obligaciones, cobertura, conflictos, evaluación y resumen. Comparar JSON/trazas antes/después y mantener las regresiones económicas. No hace falta cambiar Python, SQLite, FastAPI ni incorporar un framework frontend para abordar estos hallazgos.

## Qué conviene agregar al producto

Estas son propuestas, no capacidades ya comprobadas ni requisitos comerciales inventados:

1. **Control documental integrado al cierre.** Inventario externo de originales, cantidades e importes por archivo y moneda, con alcance confirmado por responsable. Distinguir "sin filas rechazadas" de "documentación del período completa". El verificador externo ya existe; falta convertirlo en un paso operativo visible y resolver N07.
2. **Configuración legible y verificable.** Asistente de columnas que muestre celda original, transformación y resultado; resumen contractual de fórmulas, tramos, unidades, vigencias y tolerancias; ejemplos independientes aprobados antes de usar una configuración. El editor JSON puede seguir disponible.
3. **Respaldo contractual estructurado.** Enlaces desde versión/regla al hash del documento, página/cláusula y aprobación del responsable. source_note textual no sustituye ese vínculo.
4. **Relación entre corridas.** Indicar cuál agrega evidencia, corrige datos o reemplaza una corrida anterior, sin reescribir sus hallazgos. Mostrar diferencias y motivo. La fecha y una etiqueta con "evidencia adicional" son débiles para identificar supersesión.
5. **Espacio de trabajo por cliente visible.** Nombre del cliente, ubicación de DB y alcance persistentes; biblioteca de acuerdos/mappings apropiada para ese cliente. Mantener DB separada según el procedimiento actual; no hace falta construir un SaaS multiusuario para explicitar ese aislamiento.
6. **Backup y restauración practicables.** Estado de última copia, verificación, destino fuera del equipo y ensayo de apertura/replay con el operador. El backup técnico existente es una base, no una prueba de que el procedimiento de cada cliente funciona.
7. **Volumen y tareas largas.** Estimar el tamaño normalizado, límites de filas/detalles, tiempo y espacio; progreso y recuperación de errores sin perder configuración. Priorizar el flujo real que hoy queda bloqueado por N03.
8. **Validación con un cliente real.** Ejecutar el protocolo ya escrito con originales, contrato y verdad independiente; medir falsos positivos, desconocidos y horas de configuración/revisión. Sólo incorporar prorrateos, impuestos, facturación parcial u otras primitivas si un contrato concreto los exige. La configuración actual no valida por sí sola esas reglas de negocio.

Conservar las fortalezas ya comprobadas: dinero decimal y monedas separadas; REVIEW/UNDETERMINABLE sin diferencia confirmada en los recorridos probados; historia inmutable; decisiones humanas separadas; rechazo de fórmulas no verificadas; defensa de loopback/Origin/CSP; exportaciones cotejadas y límites de Excel explícitos.

## Orden de trabajo recomendado

1. Fecha textual, política de vínculos sin corroboración y niveles de procedencia/integridad; ensayar downstream económico y todos los canales.
2. Accesibilidad de carga, exportación con caracteres no representables y límite de payload; tienen reproducciones concretas que impiden completar trabajo.
3. Reparar XLSX-11 y hacer pasar el nightly completo; incorporar las regresiones nuevas al gate de PR; establecer una versión/artefacto revisable que incluya las correcciones locales.
4. Consistencia XLS, tipos semánticos, exactitud del verificador externo y límites CLI.
5. Control documental y validación contractual integrados; piloto supervisado sobre el alcance efectivamente comprobado.
6. Optimizar reportes, refactorizar fases y mejorar distribución según volumen y entorno medidos.

No se cierra el producto por cantidad de tests, ni se declara que esta revisión cubra todos los contratos, archivos, navegadores o ataques. Las pruebas proporcionan evidencia concreta sobre los mecanismos descritos.

## Capturas conservadas

- [Carga en escritorio](./upload-1280.png)
- [Carga en móvil emulado](./upload-390.png)
- [Verificación y advertencias en móvil](./browser/onr002-004-mobile.png)
- [Resultados del recorrido E2E](./browser/current-ui.png)

El detector mecánico de interfaz también se ejecutó. Sus avisos sobre bordes/sombras son heurísticas estéticas y no se elevaron a defectos funcionales. El texto de 10,5 px de la etiqueta de prototipo es pulido menor. No se declaró conformidad WCAG ni se penalizó que la aplicación elija una sola apariencia clara. Para recorridos futuros con navegación y evidencia integradas en el chat, se puede instalar el plugin Browser; esta revisión utilizó el Playwright ya disponible.
