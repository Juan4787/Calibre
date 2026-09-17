# Sistema de verificación de Freight Audit

Base revisada: `3ec4fa667ece36e58d9898f015efb95d41e19603`, versión 0.1.0. Este plan distingue **comportamiento observado en código**, **prueba existente**, **control nuevo** y **trabajo pendiente**. Tener un test asociado no certifica toda una familia. No se modifica una conclusión comercial para hacer pasar un test.

## Modelo causal de fallos

La pérdida económica puede nacer antes del cálculo y sobrevivir a un replay perfecto. Ejemplo: una columna de importe se mapea a otra columna numérica; motor, JSON, Excel y replay coinciden, pero todos parten del dato equivocado. Hay cuatro afirmaciones diferentes que comprobar:

1. Los originales representan el período y alcance acordados. Requiere confirmación del cliente y controles totales externos.
2. La normalización conserva su significado y los términos configurados representan el acuerdo. Requiere pares original→normalizado y aprobación contractual.
3. El motor aplica correctamente esa configuración. Requiere referencia independiente, límites, propiedades y semántica de incertidumbre.
4. Persistencia y representaciones conservan exactamente esa conclusión y sus intervenciones posteriores. Requiere reconciliación, integridad, restauración y prueba visual.

| Frontera causal | Fallo y propagación | Detector independiente | Respuesta |
|---|---|---|---|
| Alcance de documentos → lote | Archivo omitido, período mezclado, factura sin detalle: total parcial parece completo | Inventario y total/control de cantidad firmado fuera del motor | IR-07 / IR-15; no concluir sobre el documento completo |
| Bytes → celdas | Float, fecha serial, fórmula cacheada, encoding o filas ocultas cambian hechos | Corpus con celdas y bytes esperados, lectura manual del original | IR-07 |
| Celdas → campos | Mapping equivocado pero válido; ceros iniciales y conceptos colisionan | Pares fuente/destino revisados, conservación de filas e importes | IR-07 / IR-11 |
| Configuración → obligación | Unidad, fecha, mínimo, tolerancia o evidencia mal interpretados | Contrato confirmado + ejemplos calculados fuera del AST | IR-15 / IR-05 |
| Cargos → operaciones | Primer candidato, clave incompleta, alias global, asignación parcial o mezcla de períodos | Grafo explícito de asignaciones y partición de IDs | IR-04 / IR-13 |
| Obligación → importe | Límites, signo, redondeo temprano, moneda o contexto erróneos | Referencia racional + casos manuales de frontera | IR-06 |
| Importe → certeza | Dato o evidencia ausente produce PASS/FAIL; una revisión suma diferencia | Invariantes que condicionan certeza y métricas | IR-03 |
| Hallazgos → agregado | Cargo perdido/duplicado, compensación de signos o monedas | Conservación por moneda y por ID, totales brutos separados | IR-01 / IR-02 |
| Memoria → historia | Escritura parcial, snapshot mutable, decisión que modifica el hallazgo | Copia externa confiable + transacciones + hashes + restauración | IR-10 / IR-12 |
| Historia → replay | Motor distinto, dependencia distinta o importación omitida se confunden con reproducción | Artefacto preservado; distinguir replay normalizado de reimportación | IR-09 |
| Historia → reporte/UI | Datos viejos, formato engañoso, fila omitida, etiqueta incorrecta o truncamiento | Conciliar campos visibles y filas contra resultado conservado | IR-08 |
| Archivo/página → equipo | Lectura/escritura arbitraria, ejecución activa, agotamiento de recursos, acceso desde red | Archivos trampa pequeños, límites, OS y pruebas de navegador | IR-14 |
| Cliente A → cliente B | Catálogo global selecciona acuerdo ajeno compatible; IDs locales colisionan | Bases separadas por cliente, registro externo de identidad y matriz de generalidad | IR-13 |

El modelo de adversario incluye errores honestos, archivos empresariales irregulares, archivos hostiles y otra página web intentando acceder al servicio local. Un administrador con control total del disco puede reemplazar base, código y hashes: los hashes locales no autentican al autor ni resuelven esa amenaza sin una copia externa confiable.

## Severidad, prioridad y costo

- **CRITICAL:** puede afirmar certeza económica falsa, alterar historia/evidencia, cruzar clientes o permitir acceso arbitrario a datos. No exige que alguien ya haya pagado.
- **HIGH:** resultado materialmente incorrecto o pérdida operativa con aviso visible, recuperable mediante controles secundarios. Escalar a CRITICAL si se vuelve silencioso.
- **MEDIUM:** bloqueo, demora o confusión sin falsa certeza; existe recuperación comprobada.
- **LOW:** ergonomía sin cambio de datos, alcance o significado económico.

La matriz usa impacto I=1..5, probabilidad L=1..5 y dificultad de detección D=1..5 (5=es muy fácil que escape). `riesgo=I×L×D`; `valor_por_costo=riesgo/C`, con C trivial=1, bajo=2, medio=4, alto=8. Son estimaciones de ingeniería, no frecuencias medidas del mercado. **Un riesgo CRITICAL no baja de P0 sólo por ser raro.** Costos separan ejecución de esfuerzo de implementación.

P0 protege dinero, certeza, integridad y límites de acceso; P1 completa fronteras, operación y aislamiento; P2 amplía entornos/capacidad; P3 es exploración de poco retorno. Grupo A: automatizar controles económicos baratos/medios y defensas necesarias. B: especificar ahora; ejecutar al habilitar la feature, entorno o volumen. C: diferir explícitamente. Grupo B puede contener un P0: la feature queda bloqueada mientras falte el control. Un score nunca levanta un bloqueo.

## Estado real de la base

La suite previa tiene 148 casos reportados, con unitarios, integración y Hypothesis. Las propiedades existentes generan suma de enteros, división comparada con Decimal de alta precisión y permutación de cuatro cargos. El fuzz actual de XLSX son bytes aleatorios de hasta 500 bytes: demuestra clasificación de corrupción básica, **no** navegación significativa de un libro válido. Los golden completos nacieron de la implementación; detectan cambios, no prueban por sí solos el contrato. Fixtures de tests usan helpers de producción, otra dependencia común a reducir.

Hallazgos de diseño que deben permanecer visibles:

- La huella de motor incluye `__init__`, `canonical`, `models`, `rules`, `engine`. No incluye importador, persistencia, CLI, servidor o reporting. Replay reejecuta el snapshot; no reimporta originales.
- Metadata conserva Python y tres paquetes, sin huella completa de aplicación/importador/reportero ni cliente inmutable. `created_at` y metadata no están en el hash del run. Son datos orientativos, no prueba forense autenticada.
- No hay identidad de cliente en Dataset. Las configuraciones comparten catálogo en una base. No llamar a esto aislamiento multiempresa. Un DB separado por cliente y un inventario externo son requisitos del piloto.
- `frozen=True` no inmoviliza recursivamente listas/diccionarios. El hash y snapshot serializado protegen lo guardado; no usar mutaciones concurrentes del mismo Dataset como API soportada.
- `Store.list_runs()` lee resúmenes sin la verificación de `load()`. No usar la lista como oráculo de integridad.
- No hay migraciones entre versiones productivas; sólo inicialización de schema 1 y rechazo de versiones futuras. La prueba de reapertura no prueba una migración ni recuperación tras fallo a mitad del DDL.
- El parser admite estilos de fecha y deja la interpretación de seriales a los lectores. La pérdida previa a un `date` normalizado exige corpus 1900/1904/serial 60, estilos engañosos y fechas fraccionarias.
- No hay conciliación contra total de factura, prorrateo ni temporales diferentes por concepto dentro del mismo acuerdo. No fabricar soporte con un test que sólo demuestre una configuración equivocada.

## Operación delegable

1. Leer la familia en [TEST_MATRIX](TEST_MATRIX.md), su oráculo y runbook. Consultar el estado: `existente`, `parcial`, `nuevo` o `diseñado`.
2. Ejecutar `.venv/bin/python scripts/qa.py matrix --check` y seleccionar con `matrix --priority P0 P1`. La lista incluye pendientes; no los transforma en aprobados.
3. `matrix --priority P0 --run-existing` ejecuta sólo selectores ya implementados, secuencialmente. El informe separa cobertura pendiente. Para validar esta entrega se usa la muestra específica descrita en `QA_IMPLEMENTATION.md`, no ese barrido.
4. Guardar resultado, comando, commit, dependencias, seed/ejemplo mínimo, entorno y decisión de triage en una carpeta de incidente fuera de Git si contiene datos reales.
5. Ante fallo: conservar evidencia antes de reducir el caso; seguir IR; no actualizar golden, ampliar tolerancia o quitar requisitos para obtener verde.
6. Un test pendiente del alcance habilitado es pendiente del gate, incluso si todos los comandos ejecutables pasan.

Cadencia: cada cambio, tests afectados + controles económicos cortos; CI, selectores relevantes y validación de matriz; nightly **opt-in**, propiedades estructuradas/fuzz presupuestados; release, gates y mutantes críticos aplicables; migración, copia/rollback/restore; cliente nuevo, protocolo ciego. Un proceso pesado a la vez; sin workers paralelos en este equipo.

## Reparto del trabajo

El trabajo de alto razonamiento queda codificado en teoría causal, invariantes, oráculos, relaciones metamórficas y runbooks. Un agente económico puede implementar una fila pendiente siguiendo sus datos/pasos/oráculo, ejecutar lotes limitados, minimizar fallos y preparar evidencia. Debe escalar semántica contractual desconocida, contraejemplos a invariantes, mutantes supuestamente equivalentes y cambios de alcance. No puede declarar correcta una regla de negocio sólo porque el código sea consistente.

Las pruebas no demuestran voluntad de pago, frecuencia real de errores, beneficio incremental, horas de onboarding ni calidad documental del mercado. Esos resultados pertenecen al protocolo de campo.
