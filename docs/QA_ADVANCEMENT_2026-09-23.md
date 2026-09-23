# Avance técnico de QA — 23/09/2026

Este documento registra qué faltaba, qué se cambió y qué **sigue sin probarse**. La referencia exhaustiva de las 58 familias, sus procedimientos y selectores es `QA_COVERAGE_LEDGER.md`; el estado se ata a la huella de código y pruebas allí indicada. Los archivos del piloto son ficticios. Ninguna de las pruebas siguientes valida un contrato o una liquidación real.

## Punto de partida y criterio

La revisión previa tenía 49 familias `PARTIAL`, seis sin runner registrado (QA-41, 47, 48, 50, 55 y 58) y tres que requieren datos/usuarios reales (QA-45, 51 y 52). Un selector verde no era cierre causal. Las seis se trataron de manera distinta: se implementaron pruebas o runners concretos para las cinco primeras; QA-58 queda `DEFERRED_NON_BLOCKING` porque sólo exige igualdad cosmética de píxeles. Si una etiqueta, moneda o importe se oculta, corresponde a QA-39/P0 y no a QA-58.

Después de esta campaña el ledger debe mostrar 54 `PARTIAL`, tres `REQUIRES_REAL_CLIENT` y una `DEFERRED_NON_BLOCKING`. **No hay familias marcadas completas ni certificación global.** P0 sigue siendo blocker para un piloto hasta ejecutar y revisar todas las obligaciones aplicables, no sólo los selectores.

## Hallazgos concretos y correcciones

| Familia | Faltaba / riesgo observado | Cambio verificable | Límite residual |
|---|---|---|---|
| QA-11 | XLSX con fila o columna poblada oculta se incorporaba sin explicar que el operador no la veía; una hoja oculta podía seleccionarse. | El importador rechaza esa hoja y nombra las primeras filas/columnas afectadas. Tras hacerlas visibles, el fixture conserva importe y celda de procedencia. | No cubre todos los productores, estilos, merges, fórmulas cacheadas o rangos extraños. XLS legacy conserva su política propia. |
| QA-14 | `import_complete=true` no demuestra que se aportaron todos los documentos; faltaba comparar contra una fuente externa. | `qa.py external-control` exige inventario SHA-256, cantidades por archivo, totales por archivo/moneda y totales globales independientes. El ejemplo sintético y cuatro alteraciones adversariales demuestran que bloquea diferencias y devuelve 0/1/2. | El control debe prepararlo un responsable externo; la herramienta no puede probar su verdad o completitud. No sustituye la conciliación ciega por ID ni la validación del contrato. |
| QA-40 | `TestClient` no observaba el socket ni la política CORS desde un navegador ajeno. | Chromium navega una página de otro puerto, intenta leer `/api/session` y ejecutar `/api/demo` incluso con token conocido; se comprueba que no puede leer y que la base queda sin nuevas corridas. Se prueba POST con Origin ajeno, preflight y escucha real IPv4 en `/proc/net/tcp`. | Linux/Chromium; no prueba firewall, otro usuario del sistema ni red Windows. |
| QA-41 | `export_run` aceptaba una carpeta vacía alcanzada por enlace simbólico; el backup verificaba existencia antes de abrir el destino y podía dejar una copia parcial. | La exportación exige carpeta nueva, rechaza `..`, rutas Windows impropias y componentes simbólicos; valida nombres internos, crea archivos sin reemplazo y deja marcador si se interrumpe. El backup se completa en un temporal, pasa `PRAGMA quick_check` y se publica por enlace duro exclusivo; conserva destino existente. Nombres de upload se reducen a etiqueta basename en ambos estilos de separador. | Otro proceso con el mismo usuario puede cambiar directorios durante la escritura. La semántica de enlaces duros debe probarse en el sistema de archivos Windows de uso; no hay garantía de corte eléctrico. |
| QA-42 | Un XLSX con nombres ZIP repetidos o rutas hostiles no se rechazaba antes del lector; el corpus no ejercitaba DTD externo. | El importador rechaza miembros duplicados, `..`, ruta absoluta, barra invertida y `:`; un DTD con entidad externa sintética no produce registro. | Faltan campaña con límites de proceso, expansión real y corpus de productores diversos. |
| QA-47/55 | Wheel/sdist y dependencias de build no tenían runner único desde un árbol Git limpio; una instalación editable podía ocultar recursos faltantes. | `verify_delivery.py` compara todos los archivos versionados con dos checkouts `git archive`, reconstruye wheel/sdist con backend fijado, compara contenido de ambos builds, instala wheel y sdist fuera del repo y comprueba UI estática, demo, persistencia, replay, ZIP y paridad económica LF/CRLF. Se fijaron `setuptools==80.9.0` y `wheel==0.45.1` para el build. | Sólo acredita el sistema operativo donde se ejecutó; faltan Windows nativo y Excel de escritorio. El lock fija versiones, no hashes criptográficos de todas las dependencias. No existe distribución firmada. |
| QA-48 | El ledger carecía de runner por fase y podía leerse el benchmark de core como prueba de todo el cierre. | Se registró el pipeline sintético de 1.000 cargos con 13 etapas, importación, dos monedas, motor, SQLite, replay, JSON/XLSX/HTML/ZIP, verificador y API. El workflow de 100.000 exige 16 GiB realmente disponibles antes de generar datos y admite etiqueta de runner con capacidad adecuada. | La campaña de 1.000 no extrapola 50.000/100.000 ni mide Chromium a esa escala. 100.000 requiere un runner capaz y un presupuesto operativo declarado. |
| QA-50 | `killed` podía significar una aserción cualquiera del selector; un fallo global de hash parecía causal. | Cada mutante tiene una señal de fallo esperada, nombre de prueba permitida y baseline limpio. Fallos de colección, errores, timeouts o aserciones ajenas son inconclusos. Prueba negativa del veredicto y ejecución de diez mutantes. | Sólo esas diez defensas y esos selectores; una señal de Pytest puede requerir mantenimiento ante cambios legítimos de mensajes. |

Las salidas locales del CLI son rutas **elegidas por el operador**, no rutas arbitrarias elegidas por un upload. El usuario debe seleccionar una carpeta nueva para exportar y un nombre nuevo para backup. En una exportación interrumpida, `EXPORTACION_INCOMPLETA.txt` impide tratar los archivos parciales como entrega cerrada.

## Evidencia y ejecución

La campaña ejecutó pruebas enfocadas para rutas, XLSX, ZIP/XML, nombres hostiles, mutantes y control externo; `scripts/verify.sh` ejecutó lint, formato, tipos, matriz, sintaxis JavaScript, suite completa, compilación y build de wheel/sdist secuencialmente. También se ejecutó `scripts/browser_e2e.py` con Chromium real: 46 filas leídas desde el DOM, comparación de JSON/XLSX/HTML/API, más origen ajeno y socket IPv4. El pipeline acotado de 1.000 cargos cerró sus 13 etapas con conciliación exacta. Los comandos completos y hashes aceptados deben constar en los recibos adjuntos al ledger; una corrida anterior a la huella actual queda histórica, no vigente.

`verify_delivery.py` exige árbol Git limpio y por eso se ejecuta **después** de confirmar el código. La equivalencia de contenidos del wheel/sdist no implica que dos archivos `.tar.gz` tengan idénticos bytes; el reporte distingue hashes de contenedor y hashes del contenido. El protocolo de build usa versiones fijadas, verificadas en [PyPI setuptools 80.9.0](https://pypi.org/project/setuptools/80.9.0/) y [PyPI wheel 0.45.1](https://pypi.org/project/wheel/0.45.1/).

## Obligaciones técnicas que siguen abiertas sin datos ni usuarios reales

Cada fila señala el control adicional necesario; `PARTIAL` significa que existe alguna prueba o runner, no que el control ya pasó para todo el alcance. Los detalles operativos y falsos negativos están en `QA_COVERAGE_LEDGER.md`.

| ID | Pendiente concreto |
|---|---|
| QA-01 | Extender la prueba de certeza a todos los buckets y reportes tras cada causa de incertidumbre. |
| QA-02 | Cubrir límites relativos, signos negativos e igualdad exacta con referencia independiente más amplia. |
| QA-03 | Verificar fórmulas de un contrato aprobado; la referencia sintética no acredita interpretación contractual. |
| QA-04 | Ampliar tipos/límites numéricos a todos los adaptadores y entradas, además de modelos del core. |
| QA-05 | Probar escalas y redondeos negativos/por componentes de acuerdos concretos. |
| QA-06 | Explorar exponentes y divisiones en todo el dominio permitido con precisión independiente. |
| QA-07 | Reconciliar separación de unidades y monedas también en cada vista/exportación. |
| QA-08 | Comparar un corpus XLSX/CSV más amplio con tokens originales leídos fuera de openpyxl. |
| QA-09 | Probar colisiones de alias, Unicode, ceros y espacios con identidades externas confirmadas. |
| QA-10 | Conciliar filas e identificadores, además de cantidades, en CSV de distintos productores. |
| QA-11 | Cubrir merges, estilos, rangos y ocultamientos producidos por programas reales; el rechazo nuevo no cierra toda la semántica Excel. |
| QA-12 | Cotejar XLS legacy de distintos productores y sus valores cacheados contra una fuente independiente. |
| QA-13 | Medir CPU/RSS/timeout en subproceso para archivos grandes, truncados y ZIP realmente expandido. |
| QA-14 | Integrar el control externo confirmado al flujo del piloto y cotejar IDs/documentos, no sólo totales. |
| QA-15 | Recorrer del hallazgo a cada celda original y transformación con cotejo manual independiente. |
| QA-16 | Verificar fronteras, huecos y solapes cuando dos versiones dan el mismo importe. |
| QA-17 | Contrastar fecha civil, serial original, epoch y zonas horarias de libros diversos. |
| QA-18 | Ejercitar aridad, tipos, límites y semántica de cada operador/condición del AST. |
| QA-19 | Probar contaminación de caché y ambigüedad aunque bandas o tablas arrojen el mismo valor. |
| QA-20 | Cotejar vínculos explícitos estructuralmente válidos con la operación verdadera, imposible de inferir sólo del ID. |
| QA-21 | Cubrir más grupos parciales y cargos ambiguos con referencia de asignación independiente. |
| QA-22 | Incorporar escenarios N→M y componentes solapados, no sólo consolidación N→1. |
| QA-23 | Definir y probar alcance de servicios parciales entre acuerdos y liquidaciones. |
| QA-24 | Comparar candidatos duplicados con remitos legítimos y reglas de duplicidad confirmadas. |
| QA-25 | Validar cada asociación de evidencia y `document_hash`, no sólo el tipo de respaldo. |
| QA-26 | Conciliar cobertura explícita con un inventario externo de cargos/documentos ausentes. |
| QA-27 | Conciliar conjuntos de IDs para detectar omisiones y duplicaciones que se compensan en el total. |
| QA-28 | Combinar invariancias metamórficas con oráculos económicos independientes; dos errores iguales pueden pasar. |
| QA-29 | Ejercitar colisiones de IDs y cachés entre clientes con bases realmente aisladas. |
| QA-30 | Anclar externamente el extremo de la cadena de decisiones para detectar truncamiento completo del sufijo. |
| QA-31 | Probar rehash y truncamiento malicioso frente a copia/huella externas preservadas. |
| QA-32 | Cotejar originales reimportados y snapshot; replay solo no descubre un error previo del importador. |
| QA-33 | Ampliar análisis de impacto a importación/configuración anteriores al cálculo y artefactos históricos. |
| QA-34 | Practicar copia fuera del equipo, restauración y reapertura con un operador y entorno objetivo. |
| QA-35 | Ejecutar kill de proceso, disco lleno, rollback y concurrencia multiproceso en copias aisladas. |
| QA-36 | Probar migraciones/DDL interrumpidos y reversión sobre copias de cada versión soportada. |
| QA-37 | Conciliar API/UI/JSON/XLSX/HTML en más variantes y contra el contrato, no sólo entre salidas coincidentes. |
| QA-38 | Verificar límites de celdas/filas y memoria real de exportación masiva sin planilla parcial aparente. |
| QA-39 | Cubrir filtros, accesibilidad, textos críticos, anchos y estados de UI fuera de la demo observada. |
| QA-40 | Repetir red/origen/bind en Windows y revisar aislamiento frente a otro usuario local. |
| QA-41 | Repetir rutas/enlaces/backup en Windows y decidir defensa ante cambios concurrentes del sistema de archivos. |
| QA-42 | Añadir fuzz acotado en proceso separado con medición de expansión ZIP y consumo real. |
| QA-43 | Probar más errores API con inventario persistido antes/después y equivalencia CLI/API. |
| QA-44 | Interceptar red de subprocesos y navegador durante flujo completo sin servicio externo. |
| QA-46 | Ejecutar el quinto arquetipo de acuerdo con oráculo independiente y documentar abstracciones faltantes. |
| QA-47 | Ejecutar clean-room nativo Windows, comparar huellas y abrir XLSX en Excel real; Linux no lo sustituye. |
| QA-48 | Ejecutar 50.000 y 100.000 en host suficiente, fases completas y navegador, con SLA acordado. |
| QA-49 | Inyectar más corrupciones en verificadores y exigir detección causal, no sólo caso verde. |
| QA-50 | Extender mutaciones dirigidas a defensas aún no mutadas y revisar manualmente cada aserción. |
| QA-53 | Ampliar corpus de IDs y JSON malformado a parser de producto y oráculo QA. |
| QA-54 | Mantener ancla externa de ZIP/resultado y ensayar rehash total, truncamiento y metadata no cubierta. |
| QA-55 | Completar Windows y Excel, hashes de dependencias, firma/distribución y actualización verificable. |
| QA-56 | Repetir obligaciones entre períodos/liquidaciones múltiples y comprobar asignación contractual. |
| QA-57 | Comparar bytes/esquema/triggers antes/después del diagnóstico en más bases futuras/corruptas. |

QA-45 (contrato/mapping aprobados), QA-51 (comparación ciega) y QA-52 (uso sin supervisión) **requieren cliente, datos y responsable reales**. QA-58 permanece diferida sólo en su parte estética. Hasta resolver las familias P0 aplicables y esos tres puntos, **Gate P y Gate U no están aprobados**. Tampoco se infiere ahorro, recupero o seguridad de pago de los importes ficticios.
