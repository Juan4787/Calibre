# Revisión adversarial de ONR-001 a ONR-005 — motor 0.1.2

Fecha local: 27/09/2026. Base Git: `fd62f05392f819896589c2a3b271ad49cdcfafbd`. Trabajo local sobre las soluciones anteriores, todavía sin commit ni publicación. Esta intervención fue autorizada expresamente después de la auditoría de sólo lectura. No reescribe las evidencias históricas ni convierte el ledger en una certificación global.

## Qué faltaba y qué se corrigió

| Brecha comprobada | Consecuencia anterior | Corrección |
|---|---|---|
| P0: un vínculo explícito inválido terminaba antes de registrar sus candidatos | El cargo inválido quedaba indeterminado, pero otro cargo de la misma obligación podía confirmar una diferencia parcial e incluso de signo equivocado. | Clasificación compartida para todos los problemas de vinculación; protección de la unión de destinos explícitos válidos y candidatos por claves. |
| El preflight sólo contaba contradicciones de vínculos válidos | Un vínculo con un ID inexistente podía llegar a Verificación sin una advertencia de vinculación. | Conteos separados de vínculos inválidos, contradictorios, ambiguos y sin operación; también se informa cuántos cargos no pueden verificarse por acuerdo, transportista o moneda. |
| Cobertura protegía el conflicto, pero no todos los vínculos inválidos/ambiguos | Un cargo presente con asignación pendiente podía aparecer además como cargo faltante en sus candidatos. | La cobertura consulta la misma incertidumbre que la agregación; sólo mantiene los faltantes independientes. |
| Cobertura reconocía la tupla exacta de una consolidación explícita | Al facturar S1+S2 aparecían faltantes individuales de S1 y S2; también ocurría si no había versión aplicable. | Se reconoce cada operación cubierta, tanto en el camino con regla como en el diagnóstico sin versión. |
| Al abrir Nueva auditoría, el formulario viejo seguía disponible durante la carga de configuraciones | Un archivo seleccionado en ese intervalo desaparecía al dibujarse el nuevo formulario. | El formulario viejo se retira inmediatamente; espera visible, error recuperable y descarte de respuestas de otra vista. |
| Lecturas de mapping/acuerdo sin estado pendiente completo | Se podía validar con el mapping anterior mientras se leía el nuevo, o recibir una respuesta vieja después de cambiar la selección. | Revisiones independientes para archivo, importación, acuerdo y vista; contenido anterior invalidado al iniciar la lectura; espera explícita y resultados/errores obsoletos descartados. |
| ONR-004 insertaba todas las advertencias en el DOM dos veces | La lista conservaba información, pero su costo de presentación crecía con todas las filas, incluso cerrada. | Lista vacía mientras está cerrada; 50 incidencias por página, navegación y salto de página en Datos y Verificación. |
| Encabezado de configuraciones desbordado a 390 px | Ancho de documento de 442 px y controles desplazados horizontalmente. | Encabezado apilado y botones ajustables en móvil; documento verificado a 390 px sin desborde. |

La primera regresión de vínculos se comprobó con 19 casos que fallaban antes de la corrección. Se añadieron después los casos de consolidación y aislamiento; las dos variantes de cobertura de consolidación tuvieron también reproducciones rojas separadas. No se dedujo que el producto fuese correcto a partir de un E2E sencillo que pasara.

## Política elegida y justificación

`explicit-consistency-v2` amplía la protección de 0.1.1. `inspect_matching` es el clasificador común del motor y de la verificación previa. La UI explica su resultado; no decide la certeza económica. CLI y API aplican el mismo control aunque no se use el wizard.

| Situación | Cargo original | Efecto sobre otras obligaciones |
|---|---|---|
| Explicit vacío, repetido, inexistente o de otro transportista | UNDETERMINABLE; importe original conservado; esperado/diferencia ausentes; confirmada 0. Sin fallback automático. | Protege los destinos explícitos existentes del transportista correcto y los candidatos por claves, incluidos aliases. |
| Explicit válido incompatible con claves | REVIEW individual, sin cálculo confirmado. | Protege ambos conjuntos de candidatos. |
| Claves automáticas con varios candidatos y cardinalidad `one` | REVIEW individual, sin asignación arbitraria. | Protege todos sus candidatos y la cobertura relacionada. |
| Sin candidato por claves y sin explicit | REVIEW individual; referencia visible para corrección. | No se inventa una operación candidata ni se bloquean operaciones independientes sin evidencia de relación. |
| Explicit válido sin candidatos por claves | Sigue permitido y deja constancia de la falta de corroboración. | No se interpreta ausencia de contradicción observable como confirmación de la intención del configurador. |
| Explicit compatible con claves | `one`: puede seleccionar entre los candidatos; `group`: exige el conjunto completo. | Continúan los controles existentes de reglas, evidencia, superposición y precisión. |

La protección se identifica por **acuerdo + operación + concepto + moneda**, sin limitarse a una liquidación. Un documento distinto no prueba que se trate de otra obligación. Los grupos relacionados quedan REVIEW si el cálculo es posible, o UNDETERMINABLE si además falta fecha/regla/dato; ambos conservan el motivo y `matching_uncertainty.unresolved_charge_ids`. No confirman diferencias. Un concepto, acuerdo, moneda u operación independiente conserva su evaluación.

Los IDs del hallazgo no resuelto representan candidatos, no una asignación aceptada. `allocation: unresolved_candidates` y las trazas conservan esa distinción; la UI los muestra como candidatos y dice “Pendiente por vinculación”. Los IDs ausentes se muestran como tales, los repetidos se identifican y los de otro transportista no pasan a ser operaciones asignadas.

**Decisión sobre cobertura:** si existe un cargo asignado a un miembro de un grupo, no está demostrada la ausencia de la obligación completa. Si existe una asignación pendiente del concepto, tampoco. Por eso no se agrega un faltante especulativo sobre ese alcance. Se mantiene la detección de operaciones independientes sin cargos. La rama sin versión reconoce los miembros ya observados y conserva el problema de fecha en el hallazgo original; no lo multiplica artificialmente. Esta decisión no introduce reparto proporcional de servicios ni certifica que un cargo parcial complete un contrato real.

Se descartaron estas alternativas:

- **Corregir sólo el aviso de UI:** deja el dinero confirmado incorrectamente en CLI/API/reportes.
- **Proteger sólo el cargo inválido o sólo el primer destino:** deja grupos parciales confirmables; el ajuste negativo reproduce el cambio de signo.
- **Volver automáticamente a las claves:** convierte silenciosamente una configuración inválida en otra asociación.
- **Bloquear todo el lote:** impide conservar y revisar resultados independientes; no es necesario para impedir la falsa confirmación.
- **Aceptar el vínculo mediante una decisión humana:** confunde la decisión operativa con la conclusión del motor y reescribe su significado.
- **Sostener motores separados para preflight y auditoría:** permite volver a mostrar un resumen tranquilizador frente a una corrida incierta. Compartir clasificación mantiene una sola política.

La decisión comercial es explícita: se prefiere una revisión defendible a una diferencia aparentemente cobrable que depende de una asociación pendiente. Se conserva el trabajo del operador y se exige corregir los datos/configuración para producir una nueva corrida. El costo de esa fricción no fue medido con clientes; no se inventa una excepción contractual para reducirla.

## Caso económico que detectó el defecto

Datos ficticios: S1 tiene referencia `00001`, S2 `00002`; la tarifa es 100 ARS. C1 es un ajuste de −100, C2 factura 150 y ambos llevan `00001`. C1 configura destinos `[S2, MISSING]`.

| Variante | C1 | C2 / grupo | Neto confirmado |
|---|---|---|---|
| Antes | UNDETERMINABLE | FAIL, diferencia parcial +50 | +50 ARS |
| Motor 0.1.2, vínculo todavía inválido | UNDETERMINABLE, candidatos S1/S2 | REVIEW, +50 calculado **sin confirmar** | 0 ARS |
| Nueva corrida, C1 corregido a S1 | Integrado con C2 | Facturado −100 + 150 = 50; esperado 100; diferencia −50 | −50 ARS |

No se confirma 0 como importe esperado: se conserva incertidumbre hasta resolver el vínculo. El caso se ejecuta también con archivos CSV y mappings cargados mediante controles reales de Chromium, detalle, decisión humana, descarga, replay y una corrida corregida. Al corregir se vuelve a consultar la corrida anterior y su resultado permanece intacto.

## Interfaz: estado efectivo y recursos

El wizard retira el formulario anterior antes de pedir configuraciones. Un error de carga ofrece Reintentar. Las respuestas se aceptan sólo si pertenecen a la vista/revisión que las solicitó.

Al seleccionar un mapping manual se vacían la selección guardada y el contenido previo, se invalida la importación y se deshabilita Validar durante la lectura. Cambiar el archivo de datos no cancela la elección manual. Elegir otro mapping guardado o escribir JSON cancela la lectura anterior. La respuesta de una importación anterior tampoco rehabilita un archivo que ya cambió.

Los acuerdos siguen la misma regla: una lectura pendiente no permite avanzar a verificación ni ejecutar usando el acuerdo anterior. Una selección posterior prevalece. Fallos de lectura actuales muestran una acción concreta; fallos de lecturas obsoletas se descartan. El E2E controla las promesas de lectura para ensayar el orden de respuestas y rechazos, sin depender de una máquina lenta ni cambiar el servidor.

Las incidencias se conservan completas en el resultado de importación. Cada desplegable genera como máximo 50 filas visibles por página y elimina sus filas al cerrarse. La prueba usa una importación real con 121 conceptos desconocidos: comprueba las tres páginas, incluido el último mensaje, en Datos y Verificación. No se bloquea la corrida únicamente por un warning. La prueba ONR-004 anterior sigue comprobando que el cargo permanece y queda indeterminado.

La paginación acota el **DOM del detalle**; no convierte el payload de importación en streaming ni acredita operación masiva. La base de importación y los resultados siguen cargados en memoria. El ajuste móvil y la migración CSS conservan la CSP; no se añadió `unsafe-inline`.

## Versión, historia y archivos modificados

Motor y paquete pasan a **0.1.2**, porque hay un cambio en certeza, trazas y cobertura. No hay migración de base ni recálculo automático de resultados. Replay requiere el artefacto exacto que generó la corrida; verificar integridad de un paquete 0.1.1 sigue siendo posible, pero reproducirlo con 0.1.2 debe rechazarse. Esto protege la historia; no demuestra que la asociación histórica fuese correcta.

| Archivo | Responsabilidad en esta revisión |
|---|---|
| `src/freight_audit/engine.py` | Clasificación común, diagnóstico de destinos inválidos, preflight completo de matching, incertidumbre compartida, cobertura por miembro y conservación de motivos. |
| `src/freight_audit/static/app.js`, `app.css` | Lecturas/revisiones/espera/reintento, advertencias de matching, detalle de candidatos, paginación de incidencias, ajuste móvil. |
| `src/freight_audit/__init__.py`, `pyproject.toml` | Versión 0.1.2. |
| `tests/test_matching_uncertainty.py` | 22 casos parametrizados de propagación, signos, cobertura, alias, aislamiento, orden, importes/cargos, API/preflight y consumidores. |
| `tests/test_explicit_link_conflicts.py` | Conserva expectativas económicas anteriores y ajusta el nombre de la traza común. |
| `tests/golden/demo.json`, `second-client.json` | Versión nueva. Demo: traza explícita para C-046 sin candidato. Todos los campos económicos y resúmenes de ambos ejemplos se mantienen iguales; el productor histórico v1 permanece intacto. |
| `scripts/browser_hardening.py`, `browser_e2e.py` | Recorridos adversariales mantenidos junto al E2E anterior. No reemplazan las aserciones de importes/estados por un simple “página cargada”. |
| `qa/catalog.py`, `qa/mutants.json`, matriz y ledger | Nuevas obligaciones/selectores; mutantes M14–M16, anclas M06/M09/M12 adaptadas al clasificador común. QA-20/QA-39 continúan PARTIAL. |

Las correcciones anteriores en servidor, resumen de acuerdos y migración CSS ya estaban en el árbol: no se atribuyen enteramente a esta revisión. No se modificaron persistencia, modelos, importadores ni generadores de informes para ocultar inconsistencias. Se probaron sus consumidores.

## Verificación reproducible

Evidencia y recibo: [qa-evidence/2026-09-27/onr-hardening/README.md](qa-evidence/2026-09-27/onr-hardening/README.md). Los recibos identifican código, comandos, salidas y limitaciones. Los resultados finales se detallan allí.

- Suite completa: 276 tests aprobados, dos advertencias conocidas de deprecación de TestClient. Ruff, formato, mypy de producto/QA, matriz y sintaxis JS forman parte de `verify.sh`.
- Subconjunto económico dirigido: 120 tests aprobados; incluye los 22 casos nuevos. Los oráculos fijan estados, importes, conjuntos y signos independientemente del detector.
- Mutación: 16/16 mutantes detectados por aserciones causales con baseline válido; incluye suprimir la protección de vínculos inválidos, permitir faltantes falsos y desconocer miembros de consolidaciones. No es una tasa de cobertura de todas las mutaciones posibles.
- Navegador real: recorridos previos ONR-001 a ONR-005 conservados, además de ajuste negativo, historia, fallos/demoras, paginación y móvil. Se registran aparte los errores HTTP deliberados y los rechazos CSP.
- Dos golden comparados sin regenerar expectativas económicas desde el motor corregido. La incorporación de la traza de C-046 fue explícita y limitada.

Ejecutar secuencialmente desde la raíz, con el entorno y Chromium instalados:

```bash
scripts/verify.sh
.venv/bin/python scripts/qa.py mutate --execute
.venv/bin/python scripts/browser_e2e.py --output-dir output/playwright/onr-hardening-recheck
```

El runner no sobrescribe una carpeta de evidencia ya usada. Se ejecutó un navegador propio y servidores temporales; se cerraron al terminar. No se detuvo Proton VPN. Los tiempos/RSS del recibo describen estas ejecuciones; no suman toda la memoria de Chromium ni son un benchmark de lotes masivos.

## Límites y recuperación

1. No es posible deducir la intención correcta si no hay candidatos o si se elige un candidato equivocado dentro de un conjunto compatible. Deben revisarse originales, mapping y contrato. La estructura coherente no basta para validar una práctica comercial.
2. Los explicit para cargos que no están en el lote conservan la política de reutilización anterior. No se inventó una validación contractual de esa reutilización ni reparto proporcional N:M.
3. La verificación previa devuelve hasta 50 incidencias detalladas, pero cuenta todas y la auditoría protege todas. Sus categorías no certifican tarifas, vigencias o evidencia; los cargos incompatibles se identifican como no verificables, con motivo individual en la corrida.
4. La paginación prueba 121 incidencias y 50 filas de DOM por desplegable; importación/exportación/UI a 50.000 o 100.000 cargos necesitan una campaña de escala de esas etapas. No se adjudica a este cambio evidencia de campañas anteriores.
5. Chromium/Linux y viewport móvil no acreditan esta versión en Windows, Excel de escritorio, otros navegadores, accesibilidad exhaustiva ni todos los layouts. Los paquetes se verifican fuera del checkout reutilizando dependencias locales; no se presenta eso como instalación limpia desde el lock.
6. No hay publicación ni gate de entrega desde commit limpio. No se puede prometer ausencia total de errores por estos tests. El cierre abarca las brechas reproducidas y sus variantes, manteniendo las obligaciones parciales del ledger.

Para actualizar: conservar backup y exportaciones; instalar 0.1.2 y reiniciar el servicio. Revisar las corridas anteriores con asignaciones inválidas/ambiguas o consolidaciones explícitas y cobertura. Corregir con evidencia disponible, versionar la configuración y crear otra corrida. Conservar la anterior como registro de lo que efectivamente se obtuvo. Una decisión “Excepción aceptada” no cambia sus métricas.
