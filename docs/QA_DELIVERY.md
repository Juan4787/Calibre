# Respuestas de cierre — 22 decisiones para operar QA

Mapa ejecutable: [matriz](TEST_MATRIX.md), [backlog](TEST_AUTOMATION_BACKLOG.md) y [comandos](QA_EXECUTION.md). Evidencia y límites de esta sesión: [QA_IMPLEMENTATION](QA_IMPLEMENTATION.md).

1. **Diez fallas más peligrosas:** falso PASS; falso FAIL; incertidumbre sumada como diferencia confirmada; importe/fecha/ID alterados silenciosamente al importar; matching equivocado o parcial; versión contractual incorrecta; error de signo/redondeo/unidad/moneda; historia alterada o replay divergente; reporte/procedencia que respalda otra conclusión; contaminación entre clientes o acceso a archivos fuera del alcance. Cada una puede cambiar decisiones aunque otros componentes sean consistentes.

2. **Diez familias de mayor valor:** QA-01 certeza; QA-02 tolerancia y signo; QA-03 referencia independiente; QA-08 importación numérica; QA-16 vigencia; QA-21 ambigüedad parcial; QA-25 evidencia por ámbito; QA-27 conservación por ID y moneda; QA-31 integridad histórica; QA-37 reconciliación de representaciones. Sus familias vecinas cubren redondeo, procedencia, replay y límites que no deben inferirse como incluidos automáticamente.

3. **Invariantes críticos:** sólo FAIL confirma Δ; Δ=A−E; todo cargo exactamente una vez; sumas firmadas separadas por moneda; versión/regla/asignación únicas; evidencia suficiente; importación incompleta impide certeza; originales e historia preservados; todas las salidas mantienen significado. Son obligaciones, no sólo asserts.

4. **Oráculos circulares:** golden generado por el motor, Store.save que reaudita con el mismo motor, replay del mismo snapshot, helpers compartidos, verificador de bundle que comparte canonical y lector XLSX común. Contrarrestar con Fraction/manual, pares de celdas, grafo/calendario externo, conservación y ancla independiente. Dos salidas iguales pueden estar igualmente equivocadas.

5. **Automatizar primero:** controles económicos baratos y pruebas negativas de los verificadores; fronteras de vigencia, matching/evidencia; corpus válido alterado por una causa; reconciliación de reportes. Completar mutantes de las defensas que se habiliten. Seleccionar por causa del cambio, no por cantidad de tests.

6. **Después:** corpus XLS/XLSX estructurado más amplio, A/B/A entre clientes, captura DOM completa, crash/restore/migración, Windows real y medición de importación/persistencia/export/UI. “Después” sólo habilita diferir si la feature o entorno permanece fuera del alcance operativo.

7. **No probar ahora:** igualdad exhaustiva de píxeles, miles de seeds sin hipótesis, motores contractuales no implementados, SaaS/multitenancy futuro ni todas las combinaciones de plataformas. No usar tests para inferir voluntad de pago, frecuencia de errores o product-market fit.

8. **Herramientas:** pytest e Hypothesis ya instalados; Fraction e enteros como referencia; JSON/SHA256/SQLite de biblioteca estándar; openpyxl y HTMLParser como lectores de reportes; runner de mutaciones semánticas acotado. Playwright queda para QA-39; mutmut es opción posterior, no dependencia añadida.

9. **Infraestructura reusable:** catálogo generador de matriz CSV/Markdown/backlog, CLI de selección, referencia racional, generadores válidos y de incertidumbre, checker independiente con pruebas negativas, reconciliador, inventario de impacto de sólo lectura, ocho mutantes dirigidos y corpus inicial con hashes/expected. Cada herramienta declara lo que no demuestra.

10. **Investigar un bug económico:** contener la conclusión, preservar ART-01, reconstruir verdad independiente, localizar primera frontera divergente, reproducir en copia, reducir sin cambiar causa, escribir regresión antes de corregir, consultar BR-01, corregir y reconciliar consumidores. No actualizar un golden para silenciar la discrepancia.

11. **Detener inmediatamente:** certeza falsa probable, dinero alterado, historia no íntegra, exposición/mezcla de clientes, pérdida de evidencia o alcance de fallo económico desconocido. Detener cliente/feature/salida sólo si su independencia está demostrada; en caso contrario, detener el uso económico general.

12. **Invalidar históricos:** cuando una corrida contiene el mecanismo defectuoso confirmado o sigue siendo candidata no descartada. Marcar externamente no apta/sospechosa; preservar status, snapshot, resultado, decisiones y hashes. Registrar sustitución por nueva corrida; no borrar ni reescribir.

13. **Blast radius:** inventario externo cliente→DB; consultar artefactos, operadores configurados/ejecutados, acuerdos, reglas, monedas y fuentes; inspeccionar fechas comerciales y entregas. Incluir desconocidos y corrupción. Metadata antigua no identifica importador/reportero/cliente: ampliar alcance hasta obtener evidencia, sin atribuirles el código actual.

14. **FALSE FAIL:** IR-01. Suspender uso del FAIL y eventuales rechazos; contrastar A/celdas, grafo, contrato/fecha, E y T; preservar cargo respaldado y contraparte realmente discrepante; revisar todos los estados del mecanismo; nueva corrida y comunicación a receptores si se entregó. Cerrar con explicación y salidas rectificadas.

15. **FALSE PASS:** IR-02. Suspender aprobaciones basadas en el producto; inventariar cargos omitidos y total documental además de fórmula/tolerancia; reproducir con discrepancia independiente; incorporar vecinos válidos; revisar PASS históricos candidatos y decisiones ya tomadas. Recalcular como nueva corrida, sin reducir tolerancias arbitrariamente.

16. **Importación incorrecta:** IR-07. Congelar formato/mapping afectado; conservar bytes y normalizado; inspeccionar celda sin parser sospechoso; corregir y probar original→expected; reimportar y comparar snapshots antes de auditar nuevamente. Replay del snapshot anterior no corrige importación.

17. **Resultado distinto en replay:** IR-09. Preservar ambos resultados; confirmar igualdad real de snapshot/artefacto y comparar entorno/código cargado; proceso limpio en copia; localizar primer campo divergente. Otro artefacto rechazado es incompatibilidad esperada. No reemplazar hash ni resultado histórico para hacerlos coincidir.

18. **Falla de provenance:** IR-11. Suspender confianza del hallazgo; comprobar SHA/hoja/fila física/columna/raw/mapping y vínculo hasta la traza. Si el dato cambia, reimportar y crear corrida nueva; si sólo presentación, corregir salida del mismo run. Origen irrecuperable queda explícitamente sin respaldo; nunca inventar una celda.

19. **Datos reales imprescindibles:** fidelidad contractual, unidad de obligación, layouts y exclusiones, significados de IDs/alias, controles documentales, evidencia/excepciones, representatividad de resultados y plataforma de uso. Un período ya auditado con comparación ciega permite contraste; beneficio incremental y costos requieren observación separada.

20. **Gate mínimo del piloto:** alcance y contrato/mapping confirmados; control total externo; P0 aplicables ejecutados o manualmente comprobados con evidencia; incertidumbre visible; referencia/mutantes de fórmulas utilizadas; integridad, reconciliación y restore; bases separadas, artefactos preservados y revisión humana. Windows real si corresponde. No acreditado por esta sesión sintética.

21. **Gate de pago sin nuestra revisión:** Gate P más evidencia real representativa, restricciones efectivas, identidad/aislamiento, totales, cadena completa versionada, backups/restore operables, supersesión/incidentes visibles y QA de la plataforma exacta. Responsable del cliente confirma el flujo de decisión. **Cerrado para 0.1.0**; no hay umbral mágico de tests que lo abra.

22. **Trabajo para un agente de menor costo:** tomar TEST_ID, construir archivo mínimo con expected previo, implementar selector, ejecutar presupuesto indicado, reducir fallos, preparar ART-01 y consultar impacto. Actualizar catálogo y evidencia sin marcar pendientes como verdes. Escalar semántica contractual, contraejemplos a invariantes, cambios de abstracción o supuesta equivalencia de mutantes. No contactar clientes, publicar datos privados ni aprobar pagos por seguir este documento.
