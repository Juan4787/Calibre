# Criterios de release y de uso

Evaluar un gate sobre un commit/artefacto/entorno y alcance declarado; no sobre “la última versión” sin hash. Un test `diseñado`, `skipped`, `xfail`, desconocido o sin oráculo independiente no es verde. El score de cobertura no compensa un control económico faltante.

## RELEASE BLOCKER

- Cualquier P0 del alcance habilitado falla o no tiene control ejecutado (automático o manual explícito con evidencia).
- Mutante crítico válido sobrevive, timeout o fallo de infraestructura no resuelto se cuenta como “muerto”, o baseline de su suite no pasa.
- Se acepta certeza con matching/versión/evidencia/importación insuficientes; currencies mezcladas; signo/conservación equivocados.
- Importador puede alterar importe, identidad o fecha silenciosamente en el formato que se va a admitir.
- Replay diverge bajo el mismo artefacto/snapshot, historia muta o no existe copia restaurable/ancla para corridas entregadas.
- Reporte/UI/API no reconcilia con run verificado, o una salida truncada parece completa.
- Alcance de bug económico desconocido excluido de la revisión; incidente CRITICAL abierto en feature habilitada.
- Acceso arbitrario a archivos, ejecución activa, exposición en red no autorizada, mezcla de clientes o defaults contractuales no confirmados.

Bloquear la feature/entorno no soportado puede permitir publicar una herramienta para un alcance menor **sólo si la restricción es efectiva y visible**. Un párrafo que dice “no usar” mientras el flujo acepta silenciosamente una entrada peligrosa no es mitigación suficiente para pago autónomo.

## WARNING y ACCEPTABLE DEBT

Warning: deprecación de dependencia sin cambio observado, performance más lenta con resultado íntegro y volumen dentro de límites, cobertura opcional incompleta fuera de alcance. Requiere dueño, motivo, impacto y fecha de revisión. Debt aceptable: constructor visual, instalador firmado mientras se usa entorno local validado, prueba de100k UI mientras límite operativo sea pequeño/confirmado, píxeles exactos del diseño. No son debt aceptable los falsos PASS/FAIL ni la falta de provenance material.

## Gate S — entregar código/infraestructura QA

Catálogo válido, selectores existentes, enlaces/IDs consistentes, lint/tipos de herramientas nuevas, una muestra con oráculos independientes y pruebas negativas del verificador. Registrar qué no se ejecutó. Este gate no certifica producto ni habilita clientes; es el alcance de esta tarea.

## Gate P — primer piloto supervisado

1. Scope de archivos/acuerdos/monedas/períodos/volumen explícito, contrato/mapping confirmados y control total externo reconciliado.
2. Todas las familias P0 aplicables tienen evidencia; las no automatizadas requieren procedimiento manual concreto y ejecución registrada. Si no pueden ejecutarse, reducir alcance o no iniciar.
3. Todos los rechazos/desconocidos visibles; ninguna conclusión automática de pago/rechazo. Revisión humana de casos y PASS de riesgo según protocolo.
4. Referencia independiente para cada fórmula y límite, mutantes críticos de features utilizadas detectados, integridad+replay+reconciliación+restore comprobados.
5. DB/directorio por cliente, original preservado, inventario externo y artefactos completos; ningún incidente económico abierto en alcance.
6. Aplicar REAL_CLIENT_VALIDATION_PROTOCOL con comparación ciega. Plataforma Windows requiere prueba real si es el entorno de uso; Linux aprobado no la reemplaza.

No se declara que P esté aprobado con los148 tests anteriores ni con esta nueva muestra. Faltan datos/contratos reales y hay familias diseñadas pendientes.

## Gate U — cliente toma decisiones de pago sin nuestra revisión

Además de P: evidencia de períodos reales representativos de cada modalidad con verdad independiente y sin falsos resultados sin explicar; control documental automático o procedimiento externo obligatorio integrado; restricciones efectivas ante ambiguos/archivos no soportados; identidad/aislamiento adecuados al uso; distribución/actualización/versionado de toda la cadena; backups y restore practicados por operador; incidentes y supersesión visibles; monitoreo de errores y política de escalamiento; QA de reportes/UI y plataforma exacta; validación del responsable del cliente sobre quién decide y qué revisión humana conserva.

Un número arbitrario de períodos o “cero fallos en100 ejemplos” no demuestra tasa real de error cero. Registrar población, selección, mecanismos cubiertos y puntos desconocidos. Un estadístico puede estimar límites sólo con muestreo y supuestos defendibles. **Gate U cerrado en0.1.0**: las capacidades y evidencia necesarias aún no están completas.

## Ejecución eficiente

Cambio sólo docs/QA: Gate S y muestra de la herramienta, no repetir benchmark ni E2E entero. Cambio motor: familias causales afectadas + invariantes + diferencial + mutantes del mecanismo + golden revisado. Importador: corpus normalizado+reimportación y trazabilidad, además de downstream económico. Reporting: reconciliación y UI afectada. Schema: backups antes, migration/rollback/crash/restore en copia; prohibido ensayar sobre la única DB del cliente.

Conservar acta de gate: commit/tree/dirty state, huellas, dependencia exacta, comandos/salidas, familias cubiertas y pendientes, mutantes, incidentes, entorno, scope, responsable. No publicar datos reales como artefactos de CI público.

La campaña técnica del 23/09/2026 y sus obligaciones residuales están en `QA_ADVANCEMENT_2026-09-23.md`. Su evidencia acotada no sustituye Gate P ni Gate U.
