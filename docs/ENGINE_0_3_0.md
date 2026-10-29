# Aplicación 0.3.0 — operación local e historia documental

Estado de entrega y evidencia: consultar `CONTINUATION.md` y el recibo de etapa 2. Este documento describe el contrato; su existencia no acredita una publicación. Los datos y controles de las pruebas son ficticios.

## Importaciones conservadas y volumen

El asistente envía `compact=true` a `POST /api/import`. La base conserva el resultado completo e inmutable y el original. La respuesta incluye `import_id`, cantidades aceptadas/rechazadas, conteos de incidencias/advertencias, muestra de origen y de transformaciones. No contiene los registros autoritativos. La muestra está limitada a 10 registros, 20 campos y 500 caracteres por valor; no sustituye la revisión completa del original. Las incidencias se consultan con `GET /api/imports/{id}/issues?page=0`, páginas de 50, desde cero. Todas permanecen en el snapshot final.

`POST /api/audit/preflight` y `POST /api/audit` reciben:

```json
{
  "label": "Nombre del período aportado por el operador",
  "imports": {"shipments": "ID_DEVUELTO_AL_VALIDAR_OPERACIONES", "charges": "ID_DEVUELTO_AL_VALIDAR_CARGOS"},
  "agreements": [],
  "evidence": [],
  "coverage": {},
  "documents": {},
  "contract_sources": [],
  "external_control": null
}
```

Los acuerdos deben ser configuraciones válidas y no una lista vacía en el flujo operativo. El ejemplo muestra la forma, no un lote listo para auditar. El servidor resuelve ambas referencias **en el espacio seleccionado**, comprueba hash del resultado, original y huella del lector/modelos/canonical, y comprueba su rol. Rechaza mezclarlas con `shipments`, `charges`, `mappings` o `issues` aportados por el navegador. Si cambió el importador, exige revalidar el original. Importaciones completas antiguas y datasets normalizados siguen admitidos por la API explícita; se cotejan/declararan según el contrato 0.2.0 de procedencia.

Las solicitudes siguen limitadas a 32 MiB; originales a 25 MiB y cada import normalizado conservado a 128 MiB. El tamaño normalizado se comprueba al serializar; todavía no constituye un límite de RSS de todo el pipeline. Los trabajos costosos usan una cola de exclusión local en threadpool; la consulta de salud no espera al cálculo. Las referencias eliminan la expansión del request en cada paso, sin prometer capacidad ilimitada de memoria o tiempo. El preflight acota cada lista diagnóstica y conserva el total de candidatos.

## Control del período y contrato

El archivo independiente sigue [EXTERNAL_CONTROL.md](EXTERNAL_CONTROL.md), esquema `freight-audit-external-control/v1`. Se prepara fuera de la app con originales, cantidades e importes por fuente y moneda; no se genera copiando los resultados. El asistente admite cargarlo en Verificación. Backend y CLI contrastan mediante aritmética racional exacta. El inventario incluye también evidencia y documentos contractuales. Un control contradictorio impide guardar la corrida; uno ausente queda claramente pendiente. Coincidencia no autentica documentos ni demuestra que el responsable incluyó todo el período. No modifica PASS/FAIL/REVIEW/UNDETERMINABLE ni confirma ahorro.

`external_control` forma parte del snapshot: agregarlo genera otra identidad de corrida y no pisa la declaración del resultado anterior. En CLI `project.json` puede indicar `"external_control": "control-independiente.json"`, ruta limitada a la carpeta del proyecto según la política de fuentes.

`contract_sources` vincula un original conservado con `agreement`, `version`, `rule` opcional, `page` entero positivo y/o `clause`. `approved_by` y `approved_on` (AAAA-MM-DD) se aportan juntos o quedan pendientes. La app no inventa responsables, fechas, autenticidad o aprobación. Backend valida que acuerdo/versión/regla existan y que el original esté conservado. El resultado permite descargar el documento por su hash verificado. La UI permite adjuntar una versión completa; referencias a reglas específicas también pueden declararse en JSON avanzado.

En un proyecto CLI se usa, por ejemplo:

```json
{"contract_sources": [{"file": "contrato-aportado.pdf", "agreement": "ID_REAL_DEL_ACUERDO", "version": "ID_REAL_DE_VERSION", "page": 1}]}
```

El loader conserva el archivo y reemplaza `file` por `document_hash`. Este fragmento se agrega a un proyecto completo; los identificadores deben corresponder al acuerdo aportado. El resumen de acuerdos muestra fórmulas, condiciones, tablas, unidades, fecha que rige la vigencia, redondeos y tolerancias. Es una explicación de la configuración: el responsable debe contrastarla con el contrato y con ejemplos calculados independientemente.

## Corridas relacionadas

Una revisión declara conjuntamente `parent_run_id`, `revision_kind` (`correction` o `evidence`) y `revision_note` (mínimo tres caracteres). El padre debe existir en esa base. Son campos del snapshot, excluidos de la semántica económica. Los resultados anteriores no se reescriben ni se marcan como pagados/reclamados automáticamente.

Aportar evidencia fija como padre la corrida abierta y deja pendiente el control independiente previo, porque un nuevo adjunto cambia el inventario. «Crear corrección» inicia una carga nueva con motivo y vínculo: el operador selecciona deliberadamente los datos y acuerdos corregidos. La UI muestra padres/hijos y permite comparar registros agregados/retirados/modificados (incluye procedencia) e importes antes/después por moneda. La comparación no resta números con coma flotante ni agrega corridas como si fueran liquidaciones distintas.

## Espacios locales y respaldos

El selector de cliente/espacio permanece visible. El espacio principal se identifica como **Sin cliente asignado**; no se inventa un cliente a partir de fixtures o nombres de bases anteriores. Crear un cliente crea una DB vacía con biblioteca propia e identidad conservada. No hay renombrado silencioso de una base con historia. Son bases locales separadas, no un sistema de usuarios ni un SaaS.

`GET/POST /api/workspaces` lista/crea espacios; en APIs se selecciona mediante `X-Freight-Workspace` y para descargas mediante `?workspace=...`. Un identificador desconocido se rechaza, sin caer en la base principal. Las rutas se generan en `{stem_DB_principal}-workspaces/{identificador_aleatorio}/audit.db`, nunca a partir del nombre aportado. El registro de espacios vive en la DB principal. No mover esos archivos con el servicio activo. Si se mueve la instalación completa, conservar su estructura y hacer un readback por cada base.

**Un backup incluye sólo la DB del espacio seleccionado.** Respaldar todos los clientes requiere descargar/verificar una copia por cada uno. El registro de espacios de la DB principal no contiene las otras bases. No presentar esa copia como un respaldo completo de todas ellas.

«Descargar respaldo verificado» usa SQLite Backup API, `quick_check`, `foreign_key_check`, hashes de originales/configuraciones/imports, identidades de auditorías y cadenas de decisiones. Publica el archivo sólo cuando pasa. Registra la última copia **preparada para descargar**, sin afirmar que llegó al disco ni que está fuera del equipo. Guardarla fuera del equipo, comprobar su hash y ensayar restauración forman parte del procedimiento del operador.

Restaurar verifica el formato de la DB antes de migrar una copia, rechaza fuentes/historia alteradas y registra el nuevo espacio sólo al terminar. Siempre crea otra DB; no reemplaza ninguna existente. La identidad histórica del cliente en cada corrida sigue siendo la original; el nombre del nuevo espacio identifica la copia. La restauración web admite 25 MiB. Para una copia mayor (hasta 500 MiB):

```bash
/home/usuario/.local/bin/calibre-freight restore-workspace /ruta/al/respaldo.db --name "Nombre para identificar la copia"
```

El launcher fija la DB principal de esta instalación. En otra instalación usar `freight-audit --db RUTA_DB_PRINCIPAL restore-workspace ...`. Conservar versiones del motor para replay: la verificación de integridad histórica no exige recalcular con una versión nueva. Los respaldos también contienen originales; tratarlos con la misma privacidad que los documentos de trabajo.

## Identidad, migración y reversión

SQLite schema 2 agrega la tabla de importaciones y el índice de revisiones en una migración aditiva transaccional. No altera snapshots/resultados/decisiones existentes. Una versión que sólo conoce schema 1 debe usar su backup anterior; no abrir la DB migrada con ella.

Las corridas nuevas usan `metadata.run_identity_version=2`: identidad = SHA-256 canónico de `[input_hash,result_hash,artifact_hash,SHA-256(metadata)]`. Incluye procedencia, control documental, entorno e identidad del espacio. La identidad v1 de las corridas antiguas conserva su fórmula de tres componentes. El lector y el verificador de paquetes aceptan ambos; no atribuyen protección retroactiva de metadata a v1. Los hashes detectan cambios inconsistentes; no son firma digital ni autenticación del operador.

Al actualizar la instalación: detener `calibre-freight.service`, verificar y respaldar **todas** las bases, ensayar migración en copias, instalar el wheel fuera del checkout, activar el pointer, reiniciar y comprobar versión/schema/puerto y lectura de historia. Si se vuelve a 0.2, preservar primero la DB posterior y restaurar la copia schema 1; conservar todos los archivos para reconciliar corridas posteriores. No borrar cambios del usuario para hacer pasar una reversión.

## Validación externa pendiente

Los recibos sintéticos no sustituyen originales y verdad independiente de un cliente ni la prueba en Windows/Excel del operador. Seguir el protocolo de primer cliente, sin habilitar decisiones autónomas de pago por cantidad de tests.
