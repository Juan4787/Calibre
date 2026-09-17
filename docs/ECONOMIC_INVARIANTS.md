# Invariantes económicos y de conservación

Sea C el conjunto de cargos aceptados, F los hallazgos, A(f) facturado, E(f) esperado, Δ(f)=A−E y T(f)=max(tolerancia absoluta, |E|×tolerancia relativa). Todos son racionales/decimales exactos por moneda; las cantidades pueden ser negativas. `PASS` expresa coincidencia técnica, no autorización de pago. `FAIL` puede representar exceso o defecto. REVIEW puede contener un cálculo tentativo, pero `confirmed_difference=0`. UNDETERMINABLE no selecciona un esperado arbitrario.

La tabla define las obligaciones. “Defensas” identifica capas requeridas, no asegura que todas ya estén implementadas. `qa/invariants.py` comprueba un subconjunto explícito sobre snapshot+resultado; no demuestra la veracidad del contrato ni recalcula todas las expresiones.

| ID / severidad | Invariante y por qué importa | Mecanismo de rotura | Prueba / defensa |
|---|---|---|---|
| INV-01 CRITICAL | Sólo FAIL aporta Δ confirmada; los otros tres estados aportan cero | Sumar difference tentativo; UI llama ahorro a REVIEW | Caso A=200,E=100 sin evidencia → REVIEW/0; checker, resumen, API, reportes, UI |
| INV-02 CRITICAL | PASS exige |Δ|≤T y FAIL exige |Δ|>T con precondiciones suficientes | Cambiar ≤ a <, ignorar tolerancia o evidencia | ±0,01 y ±0,02 sobre E=100,T=0,01; referencia independiente, core/checker |
| INV-03 CRITICAL | Δ=A−E; exceso≥0, defecto≤0; neto=exceso+defecto | Invertir signo, usar absoluto o compensar antes de separar | +50 y −75 → exceso50/defecto−75/neto−25; referencia racional, resumen/reportes |
| INV-04 CRITICAL | Cada cargo aceptado aparece exactamente una vez en `charge_ids` de F | Unmatched perdido, agrupación duplicada, cargo de otra corrida | Counter de IDs de C igual a Counter de F, sin IDs desconocidos; core/checker |
| INV-05 CRITICAL | A(f)=Σ importes de sus cargos; por moneda ΣA(f)=ΣC | Sumar monto esperado, saltar crédito, duplicar línea | Partición + sumas independientes, incluyendo cero/negativos; core/checker |
| INV-06 CRITICAL | Nunca sumar monedas distintas ni convertir implícitamente | Agrupar sin currency, mostrar único total de ARS/USD | ARS100+USD10 → dos buckets; moneda ajena → UNDETERMINABLE; contratos/core/reportes |
| INV-07 CRITICAL | Una única versión y regla aplicable respaldan certeza | Elegir primer overlap; fecha faltante tratada como hoy | Dos versiones vigentes → UNDETERMINABLE aunque cobren igual; selector/core/checker |
| INV-08 CRITICAL | La fecha contractual configurada gobierna cada operación del grupo | Usar fecha factura/importación; N→1 cruza versiones | pickup≠service_date y grupo a ambos lados del corte; tipos/selección/traza |
| INV-09 CRITICAL | Matching ambiguo y grupos superpuestos no producen certeza | Primer candidato; 40 asignados y 60 ambiguos versus 100 esperado | Dos REVIEW y confirmada0; grafo de asignaciones independiente/core |
| INV-10 CRITICAL | Evidencia debe cumplir tipo, ámbito y documento requerido | Reutilizar respaldo ajeno o una nota como archivo | each_shipment con dos operaciones y un respaldo → REVIEW; core/persistencia/checker |
| INV-11 CRITICAL | Importación incompleta impide certeza económica del lote | Filas rechazadas desaparecen o se filtran issues | Añadir issue row a lote válido → ningún PASS/FAIL; importador/core/resumen/checker |
| INV-12 CRITICAL | Cantidad física relevante=aceptadas+rechazadas+exclusiones explícitas | Ignorar fila con ID inválido, fila oculta o pie de factura | Inventario manual por fila, sin contar blancos/encabezados como negocio; importador/protocolo |
| INV-13 CRITICAL | Falta de regla/dato/conversión → UNDETERMINABLE, nunca tarifa inventada | Default0, factor aforo global, unidad confundida | Atributo ausente, lookup sin fila, kg+ARS → indeterminado/0confirmado; modelos/intérprete |
| INV-14 CRITICAL | Sin float económico; toda pérdida de precisión exige redondeo declarado o rechazo | float XLSX, contexto global, escala por moneda inferida | Literal1000000000000000.01 preservado; prec externa6 no cambia audit; importador/core/UI |
| INV-15 CRITICAL | Orden del redondeo pertenece a la regla y queda en la traza | Redondear cada componente antes de sumar o al revés | 0,005+0,005 a escala2: final0,01; componentes explícitos0,02; referencia/core/traza |
| INV-16 HIGH | Límites de tramos [inferior,superior), vigencias [inicio,fin] | Frontera compartida duplicada, hueco resuelto con vecino | 99,99/100/100,01 y fin/inicio contractual; tabla de casos/intérprete |
| INV-17 CRITICAL | Duplicado es candidato configurable, no cargo inválido por compartir remito | Deduplicar por referencia o confirmar diferencia del grupo | Mismo remito/conceptos distintos conserva ambos; flag duplicado → REVIEW; matching/core |
| INV-18 HIGH | Cargo ausente se investiga sólo en cobertura explícita; nunca ahorro | Cruzar todas las operaciones con todos los acuerdos | Sin cobertura no inventar faltantes; coverage correcto → REVIEW A=0; core/validación |
| INV-19 CRITICAL | Misma semántica produce economía idéntica sin red/reloj/locale/orden | Estado global, caché entre versiones, desempate incidental | MT-01..MT-18 con proyección apropiada; core/canonical/generadores |
| INV-20 CRITICAL | Snapshot e historial guardados no se reescriben por nueva configuración/decisión | UPDATE histórico, referencia mutable al catálogo | Guardar V2/APPROVED y comparar bytes/hash de V1; storage/backup |
| INV-21 CRITICAL | Replay bajo artefacto original coincide; otro artefacto se rechaza como replay | Recalcular con código nuevo y sobreescribir resultado | Alterar artifact_hash/code → rechazo; versión corregida crea nueva corrida vinculada externamente |
| INV-22 CRITICAL | Originales y procedencia permiten localizar cada hecho utilizado | Hash de otro archivo, fila lógica incorrecta, constante sin mapping | Celda fuente, hoja, fila, columna, raw y transformación; bytes SHA independiente + muestreo semántico |
| INV-23 CRITICAL | Representaciones mantienen identidad, moneda, estado e importes exactos | Etiquetas cruzadas, caché UI, filas truncadas | JSON/SQLite/API/XLSX/HTML/DOM reconciliados contra run conservado; reporte/checker/navegador |
| INV-24 CRITICAL | Decisión humana no implica que el motor se retractó; cadena preservada | Reemplazar status por APPROVED, quitar primera decisión | Campos separados, secuencia/hash y copia externa de cabecera; storage/UI |
| INV-25 CRITICAL | No pérdida silenciosa por fallo de escritura/exportación | Transacción parcial, disco lleno, export incompleto presentado como completo | Fault injection sobre copia; ninguna corrida parcial válida; advertencia XLSX y JSON íntegro |
| INV-26 CRITICAL | Configuración/evidencia de cliente B no afecta A | Catálogo global, IDs iguales, caché por nombre de tabla | Ejecutar A/B/A con mismos IDs/diferentes precios en bases separadas; comparación A intacta |
| INV-27 HIGH | Cero/negativos y precision configurada conservan significado | Clampear créditos, ocultar cero, imponer dos decimales | −10, 0, escala0/3/8; no inferir legitimidad del crédito ni moneda ISO en core |
| INV-28 CRITICAL | Hash es integridad relativa a ancla confiable, no autenticidad | Rehacer todos los hashes o eliminar sufijo de decisiones | Ancla/backup externos; señalar limitación; no afirmar detección local universal |
| INV-29 HIGH | Advertencias y rechazos son visibles en todas las salidas pertinentes | API omite issues, UI permite interpretar total parcial como factura | Rechazo fila2 → bandera incompleto, issues y explicación conservados |
| INV-30 CRITICAL | Cualquier fallo de QA no puede editar datos del incidente | Diagnóstico abre Store que crea triggers/migra, replay sobre DB original | Consulta SQLite mode=ro, copia para experimentos, hashes antes/después |

## Conservaciones comprobables

Por moneda: `actual = determinable + review + undeterminable`, `determinable = actual(PASS)+actual(FAIL)` y `confirmed_net_difference = confirmed_overcharge + confirmed_undercharge`. Valores firmados: con créditos no se deduce que determinable≤actual ni que una cobertura monetaria esté entre 0% y 100%. La cobertura por cantidad de hallazgos sí usa enteros no negativos; no confundirla con porcentaje de cargos ni porcentaje del monto.

Con `F0={f: charge_ids=[]}`, A(f)=0 y f no puede confirmar diferencia. Estos hallazgos pueden ser REVIEW o UNDETERMINABLE según disponibilidad de versión; no integran el conteo de cargos. Un cargo sin operación sigue perteneciendo al total facturado aceptado.

## Límite del checker

Comprueba partición, sumas, signo, buckets, comparaciones/tolerancias, unicidad de versión seleccionada, requisitos documentales explícitos, consistencia básica de traza y referencias. La exigencia `--require-provenance` sirve para datos importados: datasets normalizados construidos manualmente pueden carecer de procedencia por contrato actual. No demuestra que la celda indicada contenga el raw, ni que el precio de cada AST sea el correcto; eso requiere import oracle y referencia/ejemplos contractuales. Un atacante que altera todos los datos de forma coherente puede pasar estas identidades.
