# Protocolo de primer cliente real

Objetivo: contrastar determinismo y corrección de representación contra hechos reales, y medir beneficio incremental por separado. Un piloto supervisado no habilita decisiones autónomas de pago.

## Antes de importar

1. Asignar client_id operativo y carpeta/DB exclusivos; registrar responsable, acceso autorizado y período. Confirmar máquina/SO, respaldo fuera del equipo y método de intercambio autorizado. No usar el catálogo de la demo para datos reales.
2. Pedir originales de operaciones, detalle de cargos, factura/liquidación y totales de control externos; contrato/anexos/versiones; catálogo de conceptos y evidencia; definición de fila, IDs y relación entre remito/viaje/servicio. Recibir un período ya controlado y acordar custodio de sus conclusiones históricas.
3. Inventariar archivos con SHA256, bytes, nombre, fecha de recepción y período declarado. Guardar copia read-only; nunca editar el único Excel. Conservar etiquetas de hojas ocultas, filtros, fórmulas/cache, moneda/unidad/decimales, formatos1900/1904 y significado de créditos/anulaciones. Archivo protegido o no entendido→detener esa importación.
4. Congelar contrato y reglas vigentes, evento contractual, intervalos, unidad de obligación, mínimos, tramos, factores, orden de redondeos, tolerancias y evidence requirements. Desconocido queda desconocido. No extraer una regla normativa de un ejemplo de cobro.
5. Separar control histórico del equipo que representa/calcula. Congelar respuestas contractuales que son necesarias antes de la corrida; ocultar sólo conclusiones anteriores, no términos del acuerdo.

## Configuración y aprobación de representación

6. Crear mappings en copia; revisar pares original→normalizado de cada columna material y **todos** los bordes detectados: crédito, ceros iniciales, cambio de versión, consolidado, recargo, rechazo, archivo con formato distinto. No fijar un porcentaje arbitrario como prueba suficiente.
7. Reconciliar filas y totales por documento/moneda con control externo; explicar toda diferencia por rechazo, encabezado, subtotal o alcance. `import_complete=true` sólo significa que no hubo errores detectados por el parser; no prueba completitud de factura.
8. Dibujar grafo de asignaciones, declarar qué forma cada obligación, y ejecutar manualmente al menos un caso ordinario, cada fórmula distinta, cada frontera y cada excepción. Registrar precio independiente antes de correr audit.
9. Entregar al responsable una representación legible de fórmulas/fechas/unidades/evidencia/tolerancias y ejemplos con esperado. Obtener confirmación identificada y fechada. Esta aprobación no reescribe el contrato ni convierte evidencia ausente en inexistencia de servicio.
10. Congelar mapping/acuerdo/evidencia/alcance, hashes y artefacto completo (incluido importador y reportero) en un manifest externo. Esas huellas complementan las que hoy conserva Store.

## Primera corrida supervisada

11. Ejecutar CLI o UI con DB exclusiva, exportar paquete, conservar resultado y versiones antes de mirar control histórico. Verificar integridad, invariantes, reconciliación y un restore en otra ruta.
12. Revisar manualmente **todos** los FAIL, REVIEW y UNDETERMINABLE, cada mecanismo de regla y una selección dirigida de PASS con riesgo de falso negativo: frontera, máximo/minimo, crédito, versión, consolidación, evidencia, mismo remito. Si el volumen impide esa revisión, reducir el alcance del piloto.
13. Detener ante cualquier falsa certeza, cargo perdido/duplicado, moneda mezclada, importación silenciosamente alterada, origen no reconstruible, representación no confirmada o reporte divergente. Seguir IR, preservar corrida; no “limpiar” resultados antes de registrarlos.
14. Registrar por moneda montos aceptados/determinables/revisión/indeterminados; cantidades de cargos/hallazgos; rechazos; diferencias firmadas; horas de preparación/configuración/QA/revisión, excepciones y desconocidos. No sumar monedas ni usar revisión como ahorro.

## Comparación ciega

15. Congelar la primera corrida. El custodio abre el control histórico. Conciliar mismo período, cargos, moneda y concepto usando IDs/filas, no sólo totales.
16. Clasificar cada discrepancia con resolución independiente: conocida por cliente, nueva correcta, falso positivo, falso negativo, diferencia de alcance, sin resolución. Registrar también errores que el cliente detectó y el sistema no.
17. “Nueva correcta” exige ausencia en control histórico congelado y respaldo confirmado. No cuenta como beneficio incremental: REVIEW sin resolver, indeterminado, duplicado sospechoso, diferencia ya conocida, importe bruto sin materialidad acordada, discrepancia causada por mapping, ni cargo cuyo recupero no existe. Diferencia correcta tampoco equivale a dinero recuperado.
18. Si cambia una regla tras ver resultados, guardar otra corrida y describir la intervención; no reemplazar la corrida ciega ni atribuirle el rendimiento de la corregida.

## Postmortem y criterio de continuación

19. Revisar todos los falsos resultados/desconocidos y tareas manuales; actualizar TEST_MATRIX/IR/backlog con mecanismos, no nombres de clientes. Conservar resultados originales y corregidos.
20. Decidir con el responsable qué períodos/features pueden seguir en modo supervisado, basándose en gates técnicos, cobertura real y carga humana. Evidencia de un cliente no demuestra práctica de mercado ni generalidad de todas las tarifas.
21. Medir voluntad de pago, beneficio incremental y costo de sostener reglas mediante conversación/operación real. Los tests técnicos no los validan. Usar `PILOT_SCORECARD.csv` como registro, ampliado por IDs de corrida/incidente si hace falta.

El gate de uso para decisiones de pago sin nuestra revisión está en RELEASE_CRITERIA y permanece cerrado hasta aportar evidencia real suficiente y controles operativos. Este protocolo no lo abre por completar una lista de tests sintéticos.
