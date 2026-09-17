# Entrega técnica — Freight Audit 0.1.0

Implementación funcional, local y sin servicios externos en el camino de auditoría. **No constituye validación comercial ni una representación de las prácticas del mercado.**

1. **Arquitectura elegida:** monolito modular con núcleo puro, adaptadores de importación/persistencia/reporting y dos interfaces: CLI y web local.
2. **Stack:** Python 3.12+, Decimal, Pydantic 2, openpyxl, xlrd, SQLite, FastAPI/Uvicorn y HTML/CSS/JavaScript sin framework. Dependencias fijadas en `requirements.lock`.
3. **Motivo específico:** precisión y trazabilidad de archivos tabulares, contratos estrictos, pruebas de propiedades y operación offline con un solo runtime de producto. El costo es incorporar Python al mantenimiento habitual del fundador.
4. **Alternativas descartadas:** Pandas por inferencia de tipos; `eval`/scripting por ejecución arbitraria; Rust/Tauri por costo de iteración inicial; Electron y SaaS por operación adicional prematura; React/TypeScript como stack único por la combinación de decimal y lectores legacy. La UI puede reemplazarse sin cambiar el motor.
5. **Implementado:** atributos tipados extensibles, AST finito, unidades, aritmética y redondeos explícitos, versiones con fecha configurable, tablas/tramos/condiciones, matching compuesto/aliases/consolidado/explícito, candidatos a duplicado, evidencia configurable, cuatro estados de certeza, métricas por moneda, mappings reutilizables, XLSX/XLS/CSV, preview/rechazos/procedencia, snapshots/originales/hashes, decisiones separadas, replay, backup, exportación y UI.
6. **Probado:** núcleo, importadores, persistencia, integridad, reportes reales, CLI, API, navegador, invariantes económicas, roundtrip, reordenamiento, malformed inputs, propiedades numéricas, golden completos y ejecución sin red.
7. **Comandos exactos:** `scripts/start-local.sh` inicia la UI; `scripts/verify.sh` ejecuta lint, formato, tipos, sintaxis JS, tests, compilación y build secuencialmente. Instalación y equivalentes Windows en `README.md`.
8. **Demo:** abrir `http://127.0.0.1:8765` con el servicio iniciado. La entrega queda preparada con ambos ejemplos en `.local/delivery.db`; reiniciar con `.venv/bin/freight-audit --db .local/delivery.db serve --port 8765`. Filtrar estados y abrir “Ver explicación”. La base por defecto de comandos sin `--db` es `.local/audit.db`.
9. **Sin UI:** `.venv/bin/freight-audit run fixtures/project.json --out output/mi-auditoria`. Para otro cliente: sustituir el proyecto. `verify-bundle ARCHIVO.zip --replay` verifica integridad y reproducción.
10. **Nuevo acuerdo:** copiar una configuración en `fixtures/agreements.json`, definir sus términos y validarla desde “Acuerdos y formatos”; conservar una nueva versión. El cliente debe confirmar la representación. Ver `RULES_AND_IMPORTS.md` y schemas.
11. **Nuevo mapping:** declarar columnas o constantes, campos destino, tipos, hoja, encabezado, separadores, fechas y conceptos. Cargarlo en “Nueva auditoría”, validar filas y conservar la versión; no editar el core.
12. **Segundo cliente:** `fixtures/second-client/` utiliza otros encabezados, layout, punto decimal, USD, fecha `pickup`, consolidación 3→1 y fórmula de masa/volumen con factor ficticio. Se incorporó mediante configuración y archivos; ningún cambio específico de cliente en el núcleo.
13. **Tests:** 148 aprobados en la verificación final. Dos advertencias de deprecación del adaptador TestClient, sin fallos. Lint, formato, mypy y sintaxis JS comprobados. Resultados y alcance detallados en `VERIFICATION.md`.
14. **Benchmarks:** 10.000 operaciones con 50.000 y 100.000 cargos/hallazgos, trazas completas y tabla de 10.000 tarifas. Tiempos, memoria, huellas y alcance exacto en `VERIFICATION.md`; no se presentan como medición de importación, almacenamiento, exportación o UI a esa escala.
15. **Bugs adversariales:** vinculación ambigua que dejaba un FAIL parcial, límite de dígitos aplicado a agregados, precisión no clasificada en comparación, coerción de booleanos, procedencia CSV multilínea, cobertura duplicada, transportista incorrecto en alcance, celdas fuera de encabezados, mensajes extensos no recuperables, truncamiento XLSX, cambio de código durante ejecución, repetición de aliases completos en cada traza y pérdida de decimales al importar números XLSX. Registro en `ADVERSARIAL_REVIEW.md`.
16. **Correcciones:** propagación de incertidumbre, decimales internos separados de validación de inputs, resultados indeterminados ante precisión insuficiente, modelos estrictos, líneas físicas reales, validación de alcance, rechazos visibles, explicaciones acotadas con traza completa, límites explícitos de exportación, exigencia de reinicio tras cambiar el motor y lectura de tokens numéricos XLSX originales sin conversión a float. Se conservaron pruebas de regresión.
17. **Limitaciones conocidas:** configuración JSON, un usuario local, identidad declarada, base sin cifrado propio, XLS con aceptación de cache, sin asignación proporcional automática, sin motor impositivo, sin conciliación automática del total documental y sin soporte de todos los layouts empresariales. Si Excel no puede contener un detalle, el paquete entrega JSON completo y una advertencia; no una planilla truncada.
18. **Supuestos comerciales no validados:** frecuencia real de errores, utilidad incremental respecto del control existente, voluntad de pago, disponibilidad y calidad de evidencia, esfuerzo de preparar datos y mantener acuerdos, volumen económicamente viable.
19. **Pendientes técnicos:** instalación real Windows, distribución firmada, actualizaciones, backup operativo de clientes, cifrado si se requiere, manejo masivo de exportaciones y UI, prueba con formatos reales, reconciliación de controles totales y modelos de asignación que surjan de contratos verdaderos. No se declara certificación de producción.
20. **Partes que podrían cambiar:** UX de configuración, estructura de importación, relaciones entre remitos/operaciones/servicios, reglas de cargos parciales, redondeo por componentes, evidencia, documentos de ajuste y packaging.
21. **Partes probablemente reutilizables:** core sin red/reloj, contratos tipados, decimal exacto, AST seguro y trazas, semántica conservadora, versiones, procedencia, snapshots, decisiones separadas, CLI, suite de invariantes y exportaciones verificables.
22. **No construir todavía:** SaaS, auth multiempresa, billing, pagos/reclamos automáticos, ERP/TMS automático, ARCA, bancos, WhatsApp/email, OCR general, LLM decisorio, tracking/GPS/routing o app de choferes.
23. **Datos del primer cliente:** originales de un período ya auditado, significado de filas e identificadores, alcance y totales, contrato/anexos/versiones, fecha contractual, unidad de facturación, tarifas/unidades/tramos/factores, redondeos/tolerancias, catálogo de conceptos, evidencia/excepciones, responsable, entorno Windows y resultados previos separados para una comparación ciega. Checklist completo en `FIRST_REAL_CLIENT.md`.
24. **Riesgo de consultoría custom:** no hay ramas de cliente/sector/transportista en el core. Sigue existiendo riesgo comercial en interpretar y sostener reglas manualmente. Medir horas de onboarding, excepciones, cambios de core por cliente, cobertura y beneficio incremental. `PILOT_SCORECARD.csv` facilita registrar ese experimento sin inventar resultados.

## Archivos para empezar

- `README.md`: instalación, uso y comandos.
- `docs/FIRST_REAL_CLIENT.md`: ejecución del primer experimento real.
- `docs/ARCHITECTURE.md`: modelo, seguridad, decisiones y límites.
- `docs/RULES_AND_IMPORTS.md`: acuerdos, mappings y semántica.
- `docs/VERIFICATION.md`: evidencia de checks, benchmarks y navegador.
- `fixtures/project.json`: primer ejemplo, 32 operaciones y 46 cargos.
- `fixtures/second-client/project.json`: generalización a otro esquema.
- `dist/`: wheel y distribución de fuentes generados por el build.

Las auditorías de demostración contienen un exceso determinado ficticio de 50 ARS y un defecto determinado ficticio de −75 ARS; el segundo ejemplo tiene una diferencia ficticia de 10 USD. Estos números son expectativas de pruebas, no ahorro ni evidencia sectorial.
