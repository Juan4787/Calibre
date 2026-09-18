# Ejecución delegable y límites de las herramientas

Leer primero [estrategia](TEST_STRATEGY.md), [matriz](TEST_MATRIX.md) y [respuesta a incidentes](INCIDENT_RESPONSE.md). Ejecutar desde la raíz, con dependencias del lock instaladas. Un proceso pesado por vez. Estas herramientas no certifican contratos ni autorizan pagos.

## Comandos y resultados

```bash
# Selección y documentación; no ejecutan tests del producto
.venv/bin/python scripts/qa.py matrix --priority P0 P1
.venv/bin/python scripts/qa.py matrix --check

# Sólo después de editar qa/catalog.py
.venv/bin/python scripts/qa.py matrix --generate

# Muestra que valida la infraestructura nueva
QA_PROFILE=smoke .venv/bin/python -m pytest -q tests/test_qa_infrastructure.py

# Trabajo futuro: ejecutar cobertura ya implementada de las familias elegidas
.venv/bin/python scripts/qa.py matrix --ids QA-01 QA-21 --run-existing

# Archivos ya exportados: lectura sin recalcular la auditoría
.venv/bin/python scripts/qa.py invariants output/delivery/demo/audit.json --require-provenance
.venv/bin/python scripts/qa.py reconcile output/delivery/demo

# Inventario conservador sobre una copia consistente de la base
.venv/bin/python scripts/qa.py impact --db .local/delivery.db --feature band

# Inspección de anclas; luego ejecución opt-in de una muestra
.venv/bin/python scripts/qa.py mutate
.venv/bin/python scripts/qa.py mutate --ids M01 M05 M06 --execute
```

En Windows sustituir `.venv/bin/python` por `.venv\Scripts\python.exe` y declarar `$env:QA_PROFILE='smoke'`. La portabilidad de estos comandos está diseñada; no se verificó una máquina Windows en esta entrega.

| Salida | Interpretación                                                                                                             |
| ------ | -------------------------------------------------------------------------------------------------------------------------- |
| 0      | El control solicitado pasó dentro de su alcance; selección/generación de matriz no ejecuta pruebas                         |
| 1      | Contradicción, catálogo desactualizado/inválido, test fallido o mutante no detectado/inconcluso                            |
| 2      | Argumentos o entrada malformados, archivo/base inaccesible o formato incompatible; diagnóstico no concluido                |
| 3      | `impact`: hay candidatos desconocidos; `matrix --run-existing`: siguen obligaciones pendientes aunque los selectores pasen |

`nuevo` significa infraestructura añadida, no familia completa. Actualmente todas las familias conservan obligaciones pendientes. La selección no omite esos casos. `matrix --run-existing` hereda salida de pytest y termina con informe JSON; si se necesita JSON puro, usar selección sin ejecución. `certification=false` es deliberado.

Archivar comando, salida, código de retorno, fecha, versión de Python/dependencias, commit y cambios locales. Los ejemplos reducidos ficticios pueden convertirse en fixtures; datos privados quedan fuera del repositorio. `QA_PROFILE` admite `smoke` (25 ejemplos por propiedad nueva), `ci` (100) y `nightly` (1000). No modifica budgets explícitos de propiedades antiguas. Hypothesis reduce fallos; conservar el ejemplo final, seed/reproduce_failure cuando exista y versión exacta. No usar `assume` para descartar los casos difíciles hasta hacer pasar el test.

## Referencia, invariantes y conciliación

`qa/reference.py` usa Fraction, división entera y reglas de empate explícitas. Cubre fijo, cantidad×tarifa, mínimo, porcentaje y redondeo final; no interpreta AST, lookup ni bandas. Anclas manuales verifican la propia referencia. Nuevas reglas requieren ejemplos contractuales y una extensión independiente, no llamar al intérprete productivo desde el oráculo.

`qa/invariants.py` comprueba hashes registrados, cadena de decisiones, partición de cargos, sumas firmadas por moneda, signo, estados, tolerancia, versión por fecha, respaldo citado, traza de comparación y métricas. `--require-provenance` exige referencias para campos importados. No recorre cada AST ni detecta toda ambigüedad de matching; no prueba que una celda fuente tenga el significado declarado. La proyección económica permite comparar transformaciones que legítimamente cambian hashes.

`qa/reconcile.py` lee ocho hojas XLSX y HTML, verifica manifest, originales y snapshot, y compara campos materiales contra `audit.json`. Los importes XLSX deben seguir siendo texto exacto. Texto explicativo libre y significado contractual requieren revisión. openpyxl se comparte con el escritor: las expectativas son independientes, pero no es un lector binario independiente; probar Excel real sigue pendiente.

SQLite se compara leyendo la corrida preservada en una base temporal en el test de integración. Para una API real, capturar `/api/runs/{id}` de la misma revisión de decisiones en un archivo y aportar `--api-run ARCHIVO.json`. No pasar `audit.json` como si fuera una observación independiente de API. Para UI, el argumento `--observed-ui` acepta esta estructura:

```json
{
  "run_id": "identificador observado",
  "result_hash": "hash observado en el detalle",
  "complete": true,
  "findings": [
    {
      "id": "hallazgo",
      "state": "Coincide",
      "currency": "ARS",
      "actual": "1.234,56",
      "expected": "1.234,56",
      "difference": "0"
    }
  ]
}
```

Recorrer todas las páginas sin filtro y obtener strings del DOM, conservando captura y versión del navegador. No fabricar este archivo desde el core/API. `complete=true` es declaración del capturador, no demostración automática. Se ordenan IDs, pero se comparan todas las filas. UI sin captura y API sin respuesta se informan como **not supplied**; no se consideran verificadas. Métricas, decisiones visibles, navegación rápida y CSS requieren QA-39 además de esta comparación de hallazgos.

## Matriz de replay y cambios históricos

Crear corrida R, preservar snapshot/result/artefacto y ancla externa. Toda alteración siguiente se realiza en copia. “Nueva corrida” nunca significa sobrescribir R. Diferenciar igualdad del resultado, de economía y de bytes del contenedor.

| Cambio aislado                                   | Operación / resultado exigido                                                            | Detector y límite                                                                        |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Ninguno; reabrir proceso/DB                      | Replay con artefacto original produce mismo resultado                                    | Resultado completo + hashes; no prueba verdad contractual                                |
| Orden de entidades sin cambio semántico          | Audit normalizado mantiene resultado según canonicalización                              | MT-01; registrar snapshot diferente si corresponde                                       |
| Un byte del original conservado                  | Verificación de fuente/bundle falla                                                      | SHA contra ancla; replay numérico no reemplaza control de originales                     |
| Archivo nuevo con mismos datos y nombre distinto | Reimportación nueva: economía igual, procedencia/input hash pueden cambiar               | Pares fuente→normalizado y proyección económica                                          |
| Mapping de importe/locale/fecha                  | Reimportación explícita, posible resultado distinto; R permanece intacta                 | Hash de mapping y oracle de celdas; replay de R no usa mapping nuevo                     |
| Tarifa o versión futura en catálogo              | R no cambia; nuevo dataset puede cambiar input/semantic hash sin cambiar economía pasada | MT-09 y control de selección por fecha                                                   |
| Tarifa retroactiva corregida                     | Nueva corrida con configuración confirmada; registrar relación R→R2                      | OR-01 y ledger de incidente; no editar snapshot de R                                     |
| Un campo de snapshot almacenado                  | `load`/verificación falla si no coincide input_hash                                      | No usar list_runs como prueba de integridad                                              |
| Importe/estado/traza en resultado guardado       | Verificación falla; checker también detecta contradicción económica cuando corresponda   | Prueba negativa sin verificar hashes aísla utilidad del checker                          |
| Motor o modelo/reglas/canonical distintos        | Replay rechaza distinto artefacto                                                        | Reejecución corregida es nueva corrida, no reproducción histórica                        |
| Archivo del motor cambia con proceso abierto     | Exigir reinicio antes de guardar/reproducir                                              | Test existente de proceso desactualizado; conservar ambos artefactos                     |
| Sólo importador/reportero/servidor/UI cambia     | Huella actual del motor puede seguir igual; no afirmar cadena completa idéntica          | Manifest externo de aplicación requerido; ampliar candidatos históricos                  |
| Dependencia/SO/Python cambia                     | Comparar con entorno original; cualquier divergencia exige IR-09                         | Metadata parcial no garantiza detección automática del cambio                            |
| Nueva decisión humana                            | Resultado de motor igual; cadena y reporte de decisiones nuevos                          | Último hash externo detecta borrado de sufijo; export viejo corresponde a revisión vieja |
| metadata/created_at editados                     | Hash actual del run puede seguir válido                                                  | Documentar límite; verificar manifest externo, no inventar autenticación                 |
| DB copiada/restaurada consistentemente           | Mismas corridas, fuentes y cadena; replay bajo artefacto original                        | Inventario + backup restaurado; copia no demuestra migración                             |
| Corrupción/DDL parcial/schema futuro             | Detener diagnóstico normal; error explícito, nunca corrida vacía “correcta”              | IR-10/12; copia forense y restauración, sin inicializar original                         |
| Export HTML/XLSX o pantalla cambia               | Resultado guardado igual, reconciliación material detecta divergencia                    | IR-08; reemitir reporte con referencia a export sustituido                               |

## Mutación semántica dirigida

Se eligió un runner pequeño y auditable: `qa/mutants.json` declara ubicación, ancla única, sustitución y selectores causales; `qa/mutation.py` copia sólo código/tests/fixtures/QA a un directorio temporal. Primero exige baseline sano, después aplica una sola mutación. No copia `.local`, no usa bases del cliente ni modifica el worktree. Límite de 60 segundos **por subproceso**. Un error de importación/colección, timeout o test inválido es inconcluso; no cuenta como detectado. El reporte conserva la aserción fallida para revisar causalidad.

| ID  | Defensa rota                                    | Test que debe detectarla                                         |
| --- | ----------------------------------------------- | ---------------------------------------------------------------- |
| M01 | Tolerancia inclusiva convertida en estricta     | `test_tolerance_and_signed_differences`: 100.01 debe PASS        |
| M02 | Signo A−E invertido                             | Mismo test: exceso +10 y defecto −10                             |
| M03 | Eliminación de barrera monetaria                | `test_currencies_never_summed_or_converted`                      |
| M04 | Fin de vigencia exclusivo                       | `test_version_boundaries`: fin sigue en V1                       |
| M05 | Falta de evidencia no agrega motivo de revisión | `test_missing_evidence_does_not_confirm_even_numeric_difference` |
| M06 | Se elimina propagación de asignación incierta   | `test_ambiguous_allocation_also_blocks_related_partial_group`    |
| M07 | Extremo superior de banda inclusivo             | `test_band_overlap_and_gap_never_select_arbitrarily`             |
| M08 | Diferencia tentativa se confirma fuera de FAIL  | Test de evidencia de M05                                         |

Ocho anclas implementadas no equivalen a ocho mutantes ejecutados. La muestra y resultados reales están en [QA_IMPLEMENTATION](QA_IMPLEMENTATION.md). Para cualquier sobreviviente: comprobar baseline/ancla, reducir caso, decidir si es equivalente con contraejemplo o prueba explícita, reforzar oracle y repetir sólo el mutante afectado. No cambiar producción para que una mutación pase.

Siguientes mutaciones especificadas, **pendientes de implementar**:

| Mutación                                             | Caso causal y aserción necesaria                                                 |
| ---------------------------------------------------- | -------------------------------------------------------------------------------- |
| Redondear cada sumando sin round contractual         | N15: 0.005+0.005 debe dar 0.01, no 0.02                                          |
| HALF_EVEN sustituido por HALF_UP                     | N12: 2.345 debe dar 2.34; ancla racional                                         |
| `len(candidatos)>1` elige primero                    | Dos operaciones con igual referencia y precios distintos: REVIEW, sin confirmada |
| Desactivar control de versiones/reglas superpuestas  | Dos vigentes/aplicables incluso mismo precio: UNDETERMINABLE                     |
| Omitir crédito o cargo sin match al resumir          | Counter por ID y suma firmada desde cargos; no sólo neto final                   |
| Aceptar issue de importación como lote completo      | Fila rechazada: ningún PASS/FAIL; aviso en UI/HTML/XLSX                          |
| Reusar tabla por nombre entre acuerdos               | A/B/A con mismo table_id, precios 100/900; A permanece 100                       |
| Cambiar etiqueta de UI sin cambiar JSON              | Captura DOM debe discrepar aunque API coincida                                   |
| Leer literal XLSX vía float                          | Literal 1000000000000000.01 conservado contra token XML escrito manualmente      |
| Permitir edición de snapshot o eliminar verificación | Copia alterada rechazada contra hash/ancla anterior                              |

[mutmut](https://mutmut.readthedocs.io/en/latest/) queda como opción posterior para ampliar mutaciones sintácticas: requiere controlar costo y mutantes equivalentes; su ejecución basada en fork requiere WSL en Windows. No se añadió esa dependencia ni se ejecutó un barrido genérico. La selección dirigida protege mecanismos económicos reconocibles y permite presupuesto por familia.

## Impacto y corpus

`impact` admite filtros AND por artefacto/versión del motor, operador configurado **o** ejecutado, moneda, acuerdo, regla, extensión de fuente y huella del importador. Coincidencia significa candidato, no daño probado. Una fila ilegible o sin integridad queda desconocida incluso si un filtro habría permitido excluirla. La falta histórica de importer_hash nunca se rellena con código actual. Identidad de cliente y fechas comerciales se contrastan con inventario externo y snapshot; no se filtran por created_at para inferir período económico.

Usar copia consistente preservada. La consulta no llama Store ni crea schema/triggers. No verifica blobs ni cadena de decisiones; son controles separados. SQLite puede requerir sus archivos auxiliares al leer una base activa: no usar el único original dañado como entorno de diagnóstico.

El corpus inicial contiene tres CSV con hashes y expectativas escritas manualmente: número argentino, agrupador inválido y registro multilínea. Ampliar según QA_CASES por una causa a la vez; para XLSX escribir tokens XML conocidos en libros mínimos, no calcular expected leyendo con la misma biblioteca. Para XLS conservar un par revisado externamente y registrar limitación de caché. Fuzz nocturno, libros enormes y fault injection de procesos quedan especificados y pendientes.
