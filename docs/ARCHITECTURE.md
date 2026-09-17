# Arquitectura y decisiones

Freight Audit es un monolito modular local. No necesita internet para importar, calcular, conservar, revisar ni exportar. Las descargas iniciales de dependencias son una operación de instalación explícita. No contiene analytics, IA, OCR, CDN, fuentes externas ni llamadas a terceros durante su uso.

## Límites de módulos

| Módulo | Responsabilidad |
|---|---|
| `models.py` | Contratos Pydantic estrictos, versión de schema, atributos tipados y configuración serializable |
| `canonical.py` | Decimales exactos, serialización canónica, hashes SHA-256 y JSON sin claves repetidas |
| `rules.py` | Intérprete finito de expresiones, unidades y trazas de ejecución |
| `engine.py` | Matching, versiones, cargos esperados, comparación, evidencia, estados y agregados |
| `importing.py` | Lectura tabular, conversiones declaradas, preview, rechazos y procedencia por celda |
| `storage.py` | SQLite, originales por contenido, snapshots inmutables, decisiones anexadas, replay y backup |
| `reporting.py` | XLSX, HTML imprimible y paquete portable verificable |
| `project.py`, `cli.py` | Orquestación reproducible desde archivos |
| `server.py`, `static/` | Adaptador HTTP de loopback e interfaz local |
| `fixtures.py` | Generación de ejemplos completamente ficticios; no participa en el motor |

El núcleo de cálculo (`canonical`, `models`, `rules`, `engine`) no usa reloj, red, IDs aleatorios, archivos ni base de datos. El adaptador genera metadata incidental —fecha de creación y responsable declarado— fuera del resultado determinista.

## Stack y alternativas

**Python 3.12+, Pydantic 2, Decimal, openpyxl, xlrd, SQLite; FastAPI y HTML/CSS/JavaScript sin framework.**

Se eligió Python por la combinación de decimal exacto con control de contexto, lectores diferenciados XLS/XLSX, formatos de datos estrictos, pruebas de propiedades y SQLite integrado. Se evita Pandas: aquí interesan identificadores, celdas originales y conversiones deliberadas más que inferencia de tipos o análisis estadístico. No hay `float` en el cálculo económico.

La interfaz es un adaptador reemplazable. No agrega un bundler ni un segundo servidor a un programa que necesita instalarse localmente. Esto exige aprender Python además del stack habitual del fundador, a cambio de concentrar las reglas, importación y pruebas en un solo runtime.

Alternativas descartadas para esta versión:

- TypeScript + React: buena continuidad con el fundador, pero requería escoger un decimal adicional y resolver lectores legacy y packaging de dos lados. No se descarta migrar sólo la UI a React.
- Rust/Tauri: buen candidato de distribución futura; hoy penaliza la experimentación de contratos y formatos sin aportar valor comercial demostrado.
- Electron: empaquetado desktop conocido, con un runtime grande antes de validar la necesidad.
- Pandas: su inferencia tabular agrega riesgo sobre ceros iniciales, fechas y nulos.
- Cloud/SaaS: contradice el camino crítico offline y agrega operación que no resuelve la primera auditoría.
- Un lenguaje de scripting o `eval`: agrega ejecución arbitraria donde basta un AST finito.

## Modelo y unidad de comparación

`Shipment` representa una operación, sin afirmar que un remito equivalga a un viaje. `reference` es una referencia de negocio; `id` identifica de forma única el registro normalizado. `Charge` conserva línea, liquidación, referencia, concepto, acuerdo, transportista, importe y moneda. Los atributos extensibles son valores discriminados `decimal`, `text`, `date` o `boolean`; los decimales pueden declarar unidad.

No existe un concepto universal de flete, espera o POD. Los nombres pertenecen a la configuración del acuerdo. Cada cargo declara explícitamente su acuerdo (columna o constante del mapping). El motor no elige automáticamente un contrato a partir del precio.

La unidad de comparación es `(acuerdo, conjunto de operaciones vinculadas, concepto, moneda)`. Las líneas reales de esa unidad se **suman una sola vez** y se comparan con un esperado. Varias liquidaciones en un mismo lote también se suman si comparten esa unidad. Para servicios recurrentes separados, la identidad de la operación o sus claves de agrupación debe expresar esa separación. No existe asignación automática de costos de un consolidado a sus remitos.

Un importe esperado ausente sólo se busca con `detect_missing`, una regla `expected` y el alcance `coverage` expresamente definido. La ausencia genera REVIEW: la integridad de la liquidación necesita confirmación. Si falta versión y ya existe un cargo indeterminado para ese grupo, no se duplica el hallazgo por cobertura.

## Matching conservador

Las claves son explícitas y pueden ser compuestas. Los aliases son direccionales, por acuerdo y por campo de cargo. Nunca se hace fuzzy matching. La traza conserva el hash de la configuración y los valores originales/resueltos de las claves usadas; la tabla completa de aliases se conserva una vez en el snapshot. `one` requiere un candidato único; `group` autoriza expresamente la consolidación de todos los candidatos. `explicit` permite vincular una línea con uno o varios IDs concretos.

Una referencia sin candidato produce REVIEW. Varios candidatos con cardinalidad `one` producen REVIEW. Una vinculación explícita rota produce UNDETERMINABLE, sin fallback. Los candidatos ambiguos también bloquean la confirmación de grupos parciales relacionados. Asignaciones superpuestas del mismo concepto producen REVIEW.

La detección de posibles duplicados sólo usa `duplicate_fields` configurados. Repetir remito no prueba duplicación. Un candidato nunca se convierte automáticamente en exceso confirmado.

## Estados y dinero

| Estado | Semántica | Diferencia confirmada |
|---|---|---|
| PASS | El importe concuerda dentro de la tolerancia configurada | 0 |
| FAIL | Existe un cálculo único y una discrepancia por fuera de la tolerancia; no hay bloqueos de certeza | Facturado − esperado, con signo |
| REVIEW | Matching, evidencia, duplicación, importación incompleta o alcance requieren intervención | 0 |
| UNDETERMINABLE | Falta dato esencial, regla, versión única, unidad compatible o precisión admitida | 0 |

La diferencia numérica de REVIEW puede mostrarse como **calculada y no confirmada**. No se convierte en ahorro. El exceso confirmado es la suma de diferencias positivas FAIL; el defecto es la suma de negativas FAIL, separada. No se suman monedas ni se infieren tipos de cambio. Los totales reflejan cargos aceptados, con advertencia visible si la importación rechazó filas.

Toda la aritmética usa Decimal con contexto local de 80 dígitos e interrupción ante operaciones inexactas no declaradas. Inputs: hasta 36 dígitos y 12 decimales, sin exponentes, NaN ni Infinity; los agregados pueden exceder 36 dígitos. La división exige escala y modo, y usa cocientes enteros exactos para evitar doble redondeo. Cada acuerdo declara escala monetaria, modo de redondeo y tolerancias absolutas y relativas; el límite aplicado es `max(absoluta, abs(esperado) × relativa)`. Un desborde de precisión se vuelve indeterminado.

Las unidades tienen álgebra simple de productos y cocientes (`ARS/kg`, `kg/m3`). No hay conversiones implícitas de kg a toneladas, moneda o zona horaria. Un factor contractual debe ser explícito y versionado.

## Evidencia y decisiones

Una regla puede exigir varias condiciones documentales, cada una con alternativas `any_of`. El alcance puede ser grupo, cada operación o cada cargo. `document_required` exige un documento conservado por hash. Sin él, una declaración humana vinculada puede ser suficiente sólo si así se configuró la regla.

La presencia de un documento no certifica su autenticidad ni el contenido. El motor verifica disponibilidad según la configuración. La persona responsable debe confirmar que el tipo, la vinculación y el documento representan el hecho real.

Las decisiones se agregan con responsable declarado, motivo, evidencia ya presente, conocimiento previo del cliente y minutos de revisión opcionales. No alteran findings. Aportar evidencia nueva crea otra corrida. La identidad del operador no está autenticada en esta versión local.

## Reproducibilidad y conservación

- SHA-256 de cada archivo original, incluidas evidencias adjuntas; bytes conservados en SQLite.
- Snapshot de datasets, acuerdos, mappings, problemas de datos y evidencia.
- Hash semántico que ignora etiqueta, procedencia incidental y orden de filas; sí incorpora la condición de importación incompleta.
- Hash exacto del snapshot, resultado y artefacto fuente del núcleo.
- Identidad de corrida derivada de esos hashes. Repetir exactamente una corrida es idempotente.
- Versión del motor y metadata del entorno (Python y dependencias).
- SQLite schema v1; inicialización/migración y reapertura idempotentes, rechazo de schemas futuros.
- Tablas con bloqueo de UPDATE/DELETE por triggers. Las decisiones forman una cadena de hashes.
- `replay` verifica originales y resultado; exige el mismo artefacto del motor. Conservar el wheel, lock y fuentes de cada release.

Los hashes proporcionan integridad respecto de un valor confiable. No son firma digital, sellado de tiempo ni prueba contra un administrador que reescriba la base, los triggers y todos los hashes. Una copia externa controlada es necesaria para detectar sustitución total o truncamiento del historial. La base no está cifrada; depende del disco y usuario del sistema operativo.

## Seguridad local

Servidor ligado sólo a `127.0.0.1`, validación de Host, token de sesión para operaciones, control de Origin, CSP sin código remoto, ausencia de CORS permisivo y límites de archivo/expansión. Los adjuntos se conservan como bytes, no se ejecutan ni se sirven inline. Los mensajes de usuario no contienen stack traces; los incidentes internos se registran en consola local. No exponer este servidor en una red empresarial sin diseñar autenticación y aislamiento.

Los límites de importación son 25 MB de archivo, 150 MB expandido, 200.001 filas y 250 columnas. La API acepta solicitudes de hasta 32 MB. El motor y CLI son utilizables de forma independiente de esos límites HTTP.

## Fuentes técnicas consultadas

La elección y los contratos se contrastaron con la documentación primaria de [Decimal](https://docs.python.org/3/library/decimal.html), [openpyxl](https://openpyxl.readthedocs.io/en/stable/) y [xlrd](https://xlrd.readthedocs.io/en/stable/). Las versiones realmente instaladas están fijadas en `requirements.lock`; el comportamiento relevante se verifica con los tests del repositorio.

El proceso conserva la huella del núcleo que cargó al iniciar. Si los archivos de código cambian mientras está abierto, se bloquean nuevas conservaciones y reproducciones hasta reiniciarlo: no se etiqueta una ejecución antigua con la huella de archivos nuevos.
