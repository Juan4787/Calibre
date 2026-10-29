# ONR-001 — Resolución del conflicto entre vínculos explícitos y claves

**Actualización 27/09/2026: la revisión posterior reabrió la protección de vínculos inválidos y cobertura. La corrección ampliada es el motor 0.1.2, documentado en [ONR_HARDENING_0_1_2.md](ONR_HARDENING_0_1_2.md).** El control de contradicciones de 0.1.1 funcionaba para el caso original, pero no acreditaba propagación ante destinos inexistentes/repetidos/vacíos/ajenos. El ajuste negativo mostró una diferencia parcial confirmada de signo incorrecto. No se sostiene un cierre global con la evidencia anterior.

**Registro histórico: ONR-001 corregido para la contradicción original en el motor 0.1.1.** Implementación y suite/navegador: 23/09/2026. Comprobación de paquetes y cierre documental: 27/09/2026. Base: `fd62f05392f819896589c2a3b271ad49cdcfafbd`. Los resultados, política `v1`, comandos y límites siguientes describen esa entrega; para la política vigente usar el documento 0.1.2. Cambios sin commit ni publicación en GitHub.

La contradicción reproducida ya no genera PASS ni una diferencia confirmada: el cargo queda en REVIEW, se protegen ambos destinos posibles y la interfaz explica qué revisar. Esto cierra ese hallazgo bajo la política explícita de este documento; no certifica todo el matching, todas las familias QA ni el uso comercial.

El usuario autorizó expresamente resolver ONR-001 con autonomía de diseño y documentar la elección. Esa autorización reemplaza, para este hallazgo, la restricción de no modificar producción de la auditoría nocturna. Los otros ONR no forman parte de esta corrección.

## Problema y evidencia previa

El motor tomaba el vínculo explícito antes de resolver las claves. Validaba existencia, duplicación y transportista, pero no comparaba las dos asociaciones. Después podía agregar el cargo a otros cargos de la operación elegida.

La reproducción de Chromium conservada en `output/overnight-review/` modifica únicamente `C-001 → S-002`. Pasa de C-001 PASS y C-002 FAIL +50 a un grupo C-001+C-002 con FAIL +428; el neto ficticio cambia de −25 a +353 ARS. Un importe igual también puede ocultar el problema bajo PASS. No hay evidencia de pérdida real ni de frecuencia comercial.

## Decisión: política `explicit-consistency-v1`

Se adopta una política única, determinista y sin opción de omitir el control. El endpoint de verificación previa y el motor usan el mismo detector; ejecutar por CLI/API sin pasar por el navegador también aplica la protección.

| Condición                                                    | Comportamiento elegido                                                                                                                                                                                                           |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Destino inexistente, repetido, vacío o de otro transportista | Se conserva UNDETERMINABLE sin fallback.                                                                                                                                                                                         |
| Claves completas o incompletas sin candidatos                | Se permite el vínculo explícito válido. La traza dice `no_key_candidates`: ausencia de contradicción observable, no corroboración independiente.                                                                                 |
| `one`, uno o varios candidatos por claves                    | El explicit puede seleccionar uno o varios de esos candidatos; cualquier destino fuera del conjunto es conflicto. Conserva desambiguación y consolidación explícita entre candidatos compatibles.                                |
| `group`                                                      | El explicit debe coincidir con todo el grupo encontrado por claves. Agregar o quitar miembros es conflicto: `group` declara el alcance completo.                                                                                 |
| Contradicción                                                | Hallazgo individual REVIEW, facturado conservado, esperado y diferencia ausentes, diferencia confirmada cero. Los IDs de operaciones representan candidatos, no una asignación aceptada.                                         |
| Otros cargos en cualquiera de los destinos posibles          | Quedan sin confirmación para el mismo acuerdo, concepto y moneda, incluso en otra liquidación. Si pueden calcularse, REVIEW con cálculo no confirmado; si falta regla/dato, UNDETERMINABLE conservando el motivo de vinculación. |
| Cobertura de un concepto afectado                            | No se inventa un cargo faltante: existe una línea cuya asignación está pendiente. Otros conceptos y operaciones independientes mantienen su comportamiento.                                                                      |
| Decisión humana o evidencia agregada                         | No desbloquea por sí sola el vínculo ni reescribe el hallazgo. Corregir asociación/datos/mapping y crear una corrida nueva.                                                                                                      |

Los aliases direccionales se aplican antes de comparar, mediante las mismas claves usadas por el matching normal. No hay comparación aproximada ni elección basada en el importe. Una clave de explicit que no corresponde a un cargo de este lote conserva el comportamiento anterior; su política de reutilización es otra decisión y no se presenta como resuelta aquí.

## Justificación técnica y operativa

1. **Evita falsa certeza en ambos sentidos.** Se protege tanto el destino explícito como el candidato por claves; proteger sólo el cargo conflictivo dejaría posibles FAIL parciales en cargos relacionados.
2. **Conserva trabajo independiente.** El conflicto no rechaza todo el lote ni contamina otras operaciones, conceptos, acuerdos o monedas. Cada cargo aceptado se conserva una vez, con su importe original.
3. **No confunde conservación con confirmación.** Es posible guardar/exportar la auditoría con REVIEW y continuar revisando otros casos. Un operador puede conservar evidencia sin tener que resolver todo antes.
4. **Mantiene utilidad del vínculo explícito.** Prohibir cualquier explicit rompería la desambiguación y el enlace cuando no existe candidato automático. Se limita la restricción a evidencia contradictoria y a grupos incompletos.
5. **Explica una acción concreta.** La verificación y el detalle muestran las dos asociaciones. El operador puede corregir el enlace, revisar un alias/mapping o los datos de origen y generar una nueva corrida con trazabilidad.
6. **Historia verificable.** No hay migración ni recálculo de corridas antiguas. El cambio usa motor/paquete 0.1.1; el hash del artefacto ya protege replay frente a código distinto. Reproducir una corrida 0.1.0 requiere su artefacto original.

La valoración comercial es una decisión de diseño, no un dato validado: preferimos una revisión visible a afirmar una diferencia que el operador no puede defender. El costo es fricción adicional para quienes usaban explicit como override de referencias contradictorias. Para una excepción legítima deben aportar una configuración o representación coherente y versionada. No se afirma que este costo haya sido medido con clientes.

## Alternativas evaluadas

| Alternativa                                             | Razón para descartarla en esta corrección                                                                                                                      |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mantener explicit como autoridad silenciosa             | Reproduce el riesgo observado y permite PASS o FAIL sin control del conflicto.                                                                                 |
| Mostrar sólo un warning pero mantener dinero confirmado | Mejora la visibilidad pero conserva el riesgo económico en API, CLI, reportes y agregados.                                                                     |
| Usar siempre las claves e ignorar explicit              | Cambia silenciosamente una instrucción configurada y rompe desambiguación legítima.                                                                            |
| Rechazar todo el lote                                   | Impide conservar y revisar casos independientes; genera trabajo repetido sin aumentar la precisión de esos casos.                                              |
| Botón/flag de “aceptar igualmente”                      | No existe un contrato de aprobación por vínculo ni identidad fuerte. Reutilizar decisiones humanas para modificar certeza contradiría su separación del motor. |
| Revisar sólo el cargo contradictorio                    | Deja confirmaciones parciales en cualquiera de sus dos destinos posibles.                                                                                      |

## Interfaz y contrato del preflight

`POST /api/audit/preflight` valida el Dataset y devuelve conflictos de vínculos, sin guardar fuentes, configuraciones, corridas ni decisiones. No es una certificación del lote ni calcula tarifas. Conserva la barrera local de sesión/Origin/Host y los límites existentes. Devuelve el total y hasta 50 detalles para presentación; el motor conserva todos los hallazgos y trazas.

El wizard verifica antes de entrar a Verificación/Ejecutar. Bloquea avance mientras espera, muestra un estado de progreso y descarta respuestas de otra revisión/vista. Al ejecutar coteja que el contenido siga siendo el verificado; un cambio exige otra revisión. El servidor vuelve a comprobar el Dataset, sin confiar en la UI.

## Verificación y evidencia

La evidencia conservada está en [qa-evidence/2026-09-27/onr001/](qa-evidence/2026-09-27/onr001/README.md), con recibo, hashes, logs, capturas y paquetes sintéticos anterior/nuevo. Los archivos locales completos, incluida la traza de Playwright, están en `output/onr-001-fix/`. El recibo fecha cada ejecución; la fecha de recopilación no se presenta como una nueva ejecución.

La reproducción previa está en `before.txt`; el test nuevo falló antes del cambio porque el motor confirmaba −100 donde la nueva política exige REVIEW/0 (`red-tests.txt`). Esa falla es de una aserción económica, no de importación o del entorno.

Los tests usan tablas de casos y conjuntos escritos independientemente del detector, verifican conservación de cargos/importes, protección de ambos destinos, aislamiento, alias, grupos, ausencia de candidatos, cobertura, fallo de cálculo, API sin preflight, decisiones, historia y representaciones. El orden de una lista explicit puede cambiar el hash de su configuración original; se exige invariancia del resultado económico y de la comparación ejecutada, no identidad de ese hash literal.

| Comprobación | Resultado y alcance |
|---|---|
| `scripts/verify.sh` | 254 passed, 2 advertencias preexistentes de TestClient, salida 0. Incluye Ruff/formato, mypy del producto y QA, matriz, sintaxis JS, pytest, compilación y build. 24 casos pytest adicionales respecto de la base de 230; este conteo no expresa cobertura total. |
| Casos dirigidos de matching y consumidores | 98 passed antes del cierre general. Importes 0, 50, 100, 200 y −50; precio coincidente incluido. Conservación exacta por cargo y moneda; ambos destinos; distintas liquidaciones; acuerdos/conceptos/monedas independientes; aliases compuestos; cobertura y fallos de cálculo. |
| Límite de la verificación previa | 60 conflictos: devuelve total 60 y 50 detalles. El motor conserva 60 REVIEW, facturado 6000 y confirmado 0. El límite de presentación no limita la protección. |
| Propiedad de conjuntos | `one`: subconjunto; `group`: igualdad. Oráculo finito separado del detector; permutaciones de candidatos y destinos conservan semántica y comparación ejecutada. |
| Mutaciones M11/M12/M13 | 3/3 detectadas por aserciones causales, con baseline válido. No se interpreta un error del runner como mutante detectado. |
| Chromium real 153.0.8010.12 | Recorrido completo con archivos, configuración, retroceso, respuesta tardía, fallo/reintento, detalle, decisión, replay, descargas, corrección y reapertura. 44 filas reales del caso ONR-001 cotejadas celda por celda; también pasa el recorrido previo de 46 filas. |
| Canales de resultado | JSON, XLSX, HTML, API y DOM conciliados. La decisión EXCEPTION_ACCEPTED no cambia el resultado ni la certeza. ZIP nuevo: integridad y replay idéntico. |
| Historia 0.1.0 | ZIP anterior íntegro, SHA sin cambios; verificación devuelve 0. Replay con 0.1.1 devuelve 2 por artefacto diferente, como exige el contrato. No se reescribió ese resultado. |
| Wheel y sdist 0.1.1 instalados | Ambos instalados en directorios temporales y ejecutados fuera del checkout. 17 archivos de producto iguales byte a byte; UI estática, auditoría, persistencia, replay/export y caso ONR-001 comprobados. Dependencias reutilizadas de `.venv`: no es una instalación limpia de dependencias ni una certificación Windows. |

### Resultado económico exacto del E2E

Los valores son ficticios. El lote manual tiene 32 operaciones, 46 cargos aceptados, 44 hallazgos y total ARS **43719.4** conservado. No se confunde ese recorrido con la demostración generada, que también prueba el runner y tiene 46 hallazgos.

| Variante | C-001 | C-002 | Neto confirmado ARS del lote |
|---|---|---|---|
| Referencia sin contradicción | PASS: 378 esperado y facturado | FAIL: 596 facturado, 546 esperado, +50 confirmado | −25, por +50 y otro caso independiente de −75 |
| Contradicción en 0.1.0 | Agrupado con C-002 en S-002 | Grupo: 974 facturado − 546 esperado = +428 confirmado | +353 |
| Misma contradicción en 0.1.1 | REVIEW individual: 378 facturado; esperado/diferencia ausentes; confirmado 0 | REVIEW: cálculo 596 − 546 = +50, **sin confirmar**, por cargo relacionado | −75, exclusivamente del caso independiente |
| Vínculo corregido a S-001 en una nueva corrida 0.1.1 | PASS: 378/378 | FAIL: +50 confirmado | −25 |

Corrida conflictiva nueva: `a8a1bc2cdae436de75c4622907f440c14746470526b160a9314be57089bc7f93`. Corrida corregida: `8d587e0f965132a99863a49a37b5a2e00bb984f61e15529c20ebed3ec3773ab2`. El test vuelve a abrir la primera y comprueba que sigue en REVIEW después de crear la segunda.

La UI no exige abrir JSON para entender el conflicto: muestra el cargo, referencia original, candidatos por claves y destinos explícitos. Marca las operaciones como candidatas y el cálculo/regla/versión como pendientes por vinculación. La diferencia calculada del grupo relacionado sigue visible como **sin confirmar**.

### Prueba de que las regresiones se detectan

| Mutante deliberado, ejecutado en copia temporal | Test que debe fallar | Fallo observado |
|---|---|---|
| M11: tratar toda contradicción como compatible | `test_conflict_never_becomes_pass_or_confirms_money` | Vuelve FAIL o PASS donde se exige REVIEW; incluye mismo precio y signos opuestos. |
| M12: retirar propagación de incertidumbre a ambos destinos | `test_conflict_protects_both_scopes_without_poisoning_unrelated_work` | Cargos relacionados vuelven a FAIL, incluso en otra liquidación. |
| M13: permitir subconjunto en `group` | `test_candidate_selection_and_group_completeness` | Grupo incompleto vuelve a PASS. |

Los mutantes se aplicaron a copias desechables. El producto conserva la implementación sin esas alteraciones. Sólo se afirma la detección de estas tres regresiones concretas.

## Cambios exactos por archivo

| Archivo | Cambio y propósito |
|---|---|
| `src/freight_audit/engine.py` | Extracción del índice de matching sin cambiar su criterio; detector compartido de consistencia; preflight; hallazgo individual; trazas de ambas asociaciones; propagación al mismo acuerdo/operación/concepto/moneda; cobertura conservadora; motivo retenido cuando falla el cálculo. |
| `src/freight_audit/server.py` | Endpoint local de verificación previa sin persistencia. La ruta de auditoría sigue usando el motor autoritativo. |
| `src/freight_audit/static/app.js` | Dataset común entre verificación y ejecución; control de revisión/vista/contenido; espera visible; advertencias en pasos 3 y 4 y en detalle; comparación de asociaciones; instrucciones de corrección; limpieza del aviso de error al reintentar. |
| `src/freight_audit/static/app.css` | Clases para la advertencia y lista de conflictos; ajuste de textos largos. La CSP no se relaja. |
| `src/freight_audit/__init__.py`, `pyproject.toml` | Motor y paquete 0.1.1 para identificar el cambio de comportamiento. No cambia el schema. |
| `tests/test_explicit_link_conflicts.py` | Regresiones y oráculos independientes descritos arriba; verificación de API sin preflight y de ausencia de escrituras del preflight. |
| `scripts/browser_e2e.py` | Extensión del runner mantenido con el recorrido real ONR-001, descargas, fallos/tardanzas, corrección e historia; no se sustituye el escenario anterior. |
| `tests/golden/demo.json`, `tests/golden/second-client.json` | Únicamente cambia `engine_version`: 0.1.0 → 0.1.1. No se regeneran ni ajustan resultados económicos para hacer pasar tests. El productor histórico v1 permanece intacto. |
| `qa/catalog.py`, `qa/mutants.json` | Obligación concreta de QA-20, ocho selectores adicionales y tres mutantes causales. |
| `docs/TEST_MATRIX.md`, `docs/TEST_MATRIX.csv`, `docs/QA_COVERAGE_LEDGER.md` | Matriz regenerada, obligación/evidencia actualizada y familia QA-20 todavía PARTIAL por sus obligaciones más amplias. |
| `docs/ARCHITECTURE.md`, `docs/RULES_AND_IMPORTS.md`, `README.md`, este documento y su carpeta de evidencia | Contrato de la nueva política, recuperación operativa, decisiones, resultados y límites explícitos. |

No hubo cambios en persistencia, importadores, reportes, reglas de cálculo ni modelos. Sus consumidores se verificaron usando los contratos existentes de REVIEW y diferencia confirmada.

## Ajustes surgidos durante la validación

1. Una primera propiedad exigía identidad de toda la traza al reordenar la lista de explicit. Falló porque la traza incluye el hash del JSON original de configuración, que sí cambia. Se corrigió el oráculo para exigir igualdad económica y de la comparación ejecutada, manteniendo la integridad literal del snapshot. No se alteró el producto para ocultar esa diferencia legítima.
2. Mypy requirió anotar explícitamente la lista de diagnósticos. Se añadió la anotación y el control de tipos pasó.
3. La primera inspección visual mostró que el aviso de un fallo simulado seguía visible después de una verificación exitosa. Se limpia al recuperarse; el E2E lo comprueba.
4. El resumen compacto decía “Lote verificado” aunque hubiera un conflicto. Ahora muestra la cantidad de vinculaciones en revisión.
5. La inspección del detalle mostró “Sin versión/regla aplicable” pese a no haberse intentado su evaluación. Ahora dice “Pendiente por vinculación” y explica por qué no se calcula; se agregaron aserciones de navegador y se repitió el recorrido tras ese cambio.

## Recursos y alcance de ejecución

Los checks pesados y Chromium se ejecutaron secuencialmente. No se detuvo Proton VPN. El runner cierra su navegador y servidor temporal incluso si falla; los originales del informe nocturno se conservaron.

La ejecución final de `verify.sh` tardó **28.25 s**, con máximo RSS informado por `/usr/bin/time -v` de **92532 KiB**. El navegador final tardó **46.41 s**, con **252260 KiB** informados por la misma herramienta. Estos valores no suman la memoria simultánea de todos los procesos de Chromium ni representan un benchmark de importación/exportación masiva. No se extrapolan a 50000/100000 cargos.

## Comandos para reproducir

Desde la raíz, con el entorno de desarrollo y Chromium de Playwright instalados, ejecutar secuencialmente. Usar una carpeta nueva para cada corrida de navegador; el runner se niega a sobrescribir evidencia.

```bash
scripts/verify.sh
.venv/bin/python -m pytest -q tests/test_explicit_link_conflicts.py
.venv/bin/python scripts/qa.py mutate --ids M11 M12 M13 --execute
.venv/bin/python scripts/browser_e2e.py --output-dir output/onr-001-recheck
.venv/bin/freight-audit verify-bundle docs/qa-evidence/2026-09-27/onr001/after.zip --replay
.venv/bin/freight-audit verify-bundle docs/qa-evidence/2026-09-27/onr001/before.zip
```

Ambos paquetes son ahora históricos: `before.zip` pertenece a 0.1.0 y `after.zip` a 0.1.1. Con 0.1.2 se verifica su integridad sin `--replay`; reproducir cualquiera con el motor nuevo debe terminar con código 2 por artefacto distinto. El comando anterior con `--replay` sólo acreditó el artefacto 0.1.1 de aquella ejecución. No se debe cambiar el hash del paquete para evitar el rechazo. El script de paquetes y sus argumentos están conservados en la carpeta de evidencia; usa las dependencias existentes y directorios temporales.

## Actualización y recuperación operativa

1. Conservar backup y paquete de cualquier auditoría anterior que se esté investigando. Actualizar a 0.1.1 y reiniciar el servicio; el resultado viejo no se recalcula automáticamente.
2. Si una corrida antigua usaba vínculos explícitos, revisar la asociación con los documentos originales. Integridad/replay histórico no demuestran que su asociación fuese correcta: la corrida sintética anterior sigue conteniendo +428.
3. Volver a importar los originales con sus mappings y acuerdo conservados. La verificación nueva muestra contradicciones observables. Guardar el resultado con REVIEW si todavía no se puede resolver.
4. Corregir el vínculo, dato de origen o mapping/alias según la documentación disponible y conservar la configuración revisada. No cambiar claves sólo para silenciar el control ni inventar una excepción contractual.
5. Crear y comparar una corrida nueva. La decisión humana de aceptar una excepción puede registrarse en la anterior, pero no modifica su resultado técnico ni confirma dinero.

## Qué queda fuera de este cierre

- No puede detectar una intención errónea cuando las claves no aportan candidatos o cuando un explicit elige al candidato equivocado dentro de un conjunto ambiguo compatible. La coincidencia estructural no valida el contrato ni la intención del configurador.
- Las claves de explicit que apuntan a cargos ausentes del lote mantienen la política anterior; no se introduce una nueva regla de reutilización de configuraciones.
- No se agregaron aprobaciones por vínculo, identidad fuerte, asignación proporcional, detección semántica de contratos ni edición automática de originales.
- El preflight cuenta contradicciones explícitas; no valida por sí solo todas las reglas, evidencias, coberturas o errores del lote. Sus 50 detalles y las ocho operaciones visibles por lista son límites de presentación; las trazas y el resultado conservan el detalle.
- No se certifican todas las combinaciones N:M, todos los layouts, accesibilidad formal, otros navegadores ni el comportamiento de esta versión en Windows/Excel de escritorio. La instalación de dependencias en un entorno nuevo y la entrega reproducible desde un commit limpio quedan para el gate de publicación; `verify_delivery.py` exige ese estado y no se afirmó haberlo ejecutado sobre este worktree modificado.
- ONR-002 (resumen de acuerdos), ONR-003 (nombre de mapping), ONR-004 (advertencia de importación) y ONR-005 (estilos inline/CSP) quedaron fuera de **ONR-001** y se resolvieron después en [ONR_002_005_RESOLUTION.md](ONR_002_005_RESOLUTION.md). El E2E de ONR-001 por sí solo no acreditaba cero avisos CSP.
- La frecuencia de conflictos, costo de revisión, facilidad de onboarding y aceptación comercial necesitan evidencia real. La elección protege la capacidad de defender un resultado; no demuestra una mejora comercial medida.

El criterio de cierre de ONR-001 fue observar y proteger la contradicción original en motor, API, interfaz, persistencia, decisiones y exportaciones, demostrar que los controles fallan ante regresiones deliberadas, y documentar una política inequívoca. No se cambió QA-20 a cobertura total ni se reescribió el informe nocturno histórico.
