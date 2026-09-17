# Oráculos independientes y comparaciones

## Fuente de verdad y grados de confianza

El acuerdo y los hechos confirmados por el cliente son la verdad de negocio. El **run original verificado**, con snapshot+resultado+hash y su cadena de decisiones, es la fuente canónica técnica para representar esa corrida. La base actual, una captura y el último cálculo en memoria no reemplazan una copia confiable del run. Un resultado conservado puede ser incorrecto: conciliar salidas prueba fidelidad, no corrección contractual.

| Oráculo | Familias | Independencia / límite |
|---|---|---|
| OR-01 cálculo manual firmado | Fórmulas/precios/temporales/generalidad | Hoja de respuestas creada antes de correr el motor, autor/revisor/contrato; no copiar trace como expected |
| OR-02 referencia racional | Fijo, cantidad×tarifa, mínimo, porcentaje, redondeo final | `qa/reference.py`, Fraction/enteros, sin imports de freight_audit, sin AST ni selección de fechas; no prueba lookup/matching/evidencia/división general |
| OR-03 conservación independiente | Cargos, agregación, monedas, métricas | `qa/invariants.py` recompone desde cargos y compara partición/buckets; no prueba que los cargos estén completos respecto de factura |
| OR-04 pares de celdas | Importación/provenance | Corpus conocido y original inspeccionado fuera del parser, bytes/hash/hoja/fila; abrir otra vez con openpyxl no es independiente de openpyxl |
| OR-05 grafo y calendario manual | Matching/versiones/evidencia | Enumeración corta de candidatos e intervalos, precio distinto por versión; ningún `select_version` o matcher de producción para expected |
| OR-06 ancla externa | Hashes/snapshots/decisiones/restore | Hash/artefacto conservado fuera de DB y alcance del incidente; no sirve un hash recalculado tras corrupción como supuesto original |
| OR-07 contrato de representación | JSON/SQLite/API/XLSX/HTML/UI | Lectura independiente de campos del reporte, tabla de etiquetas propia; no importar `STATUS_LABELS`, `html_report` ni `summarize` como expected |
| OR-08 relación metamórfica | Transformaciones de significado preservado | Proyección definida abajo; dos resultados igualmente erróneos pueden satisfacerla |
| OR-09 barrera de seguridad | Archivos hostiles/endpoints/paths | Canary externo a destino, bytes/hash, captura de red, proceso limitado; un 422 no basta si hubo escritura antes |
| OR-10 baseline operacional | Capacidad/crash/concurrencia | Proceso aislado, timeout/RSS/cantidad conciliada y backup comprobado; no comparar tiempos de máquinas distintas como regresión |

Casos manuales mínimos para OR-02: fijo100→100; 10×2 con mínimo30 y +5%→31,5; 20×2 con mínimo30 y +5%→42; −1,005 HALF_UP escala2→−1,01; 2,345 HALF_EVEN→2,34. Revisar estos anclajes antes de usar diferencial. La referencia devuelve resultado y no reproduce semántica de certeza: evidencias/versiones/matching requieren otros oráculos.

## Circularidad concreta encontrada

- `Store.save` vuelve a llamar a `audit`: protege contra resultado editado, no detecta un bug común del motor.
- Replay llama a `audit` sobre el mismo snapshot: no identifica dato importado mal ni contrato configurado mal.
- Golden generado desde el motor congela un comportamiento, incluso erróneo. Cambios requieren contraste con OR-01/02/05, diff campo por campo y motivo; nunca regenerar masivamente ante un fallo.
- Helpers `freight_audit.fixtures` se usan tanto en demo como tests. Un default común erróneo puede alinear ambos. Los nuevos builders no los importan.
- El test existente de división usa Decimal de precisión100 como referencia. Es independiente del algoritmo racional de producción, pero comparte reglas de Decimal y cubre numeradores enteros pequeños. No extender su garantía a exponentes extremos sin casos manuales/racionales.
- Una prueba de exportar y verificar con `verify_bundle` comparte canonical y contratos internos. El verificador QA usa SHA256/JSON propio y reconciliación de campos, y se prueba con salidas manipuladas deliberadamente.
- No recalcular expected a partir del texto de la traza: si el motor aplicó la tarifa equivocada, explicación y resultado pueden coincidir perfectamente.

## Niveles de igualdad

**Bytes**: originales, backup copiado, snapshot congelado. **Run**: input_hash/result_hash/artifact_hash y decisiones bajo ancla confiable. **Resultado completo**: mismas estructuras, trazas, IDs e issues. **Economía**: multiconjunto de asociaciones, concepto/moneda/versión/regla, A/E/Δ/confirmada/estado + métricas. `qa.invariants.economic_projection` implementa esta última, excluyendo hashes, motivos, traza e issues textuales; conserva bandera de importación incompleta. No usarla para afirmar reproducibilidad exacta.

| Relación | Transformación y precondición | Igualdad esperada y automatización |
|---|---|---|
| MT-01 | Permutar shipments/cargos/acuerdos/evidencia, IDs estables | Resultado completo igual; generar permutación independiente por colección |
| MT-02 | Renombrar archivo sin cambiar bytes/mapping | Economía igual; snapshot/provenance filename/input_hash pueden cambiar |
| MT-03 | Reordenar columnas y adaptar mapping por encabezado | Economía igual; bytes, posición y hashes del origen diferentes |
| MT-04 | Añadir columna irrelevante con nombre único y valores inocuos dentro de límites | Economía igual; no aplicar a filas con exceso de columnas sin encabezado |
| MT-05 | CRLF↔LF y BOM configurado correcto | Economía igual; SHA del archivo diferente. Las huellas de originales deben seguir siendo diferentes |
| MT-06 | Aportar evidencia suficiente al único REVIEW documental | Grupo pasa a PASS o FAIL según Δ/T; resto de proyección sin cambios; corrida original intacta |
| MT-07 | Agregar evidencia de otro grupo | No resuelve el REVIEW objetivo; registrar diferencias de metadata sin atribuir efecto económico |
| MT-08 | Guardar mismos bytes de fuente dos veces | Una fuente por hash, no dos cargos. Importar deliberadamente cargos con IDs nuevos sí altera el lote o dispara revisión; no prometer deduplicación mágica |
| MT-09 | Agregar versión futura no solapada | Economía de operaciones previas igual; semantic_hash puede cambiar por incluir todo el acuerdo; replay del snapshot original idéntico |
| MT-10 | Aumentar sólo actual en ε con regla/evidencia/asignación fijas | E constante; Δ aumenta ε; cruzar T cambia PASS→FAIL. No aplicar a reglas basadas en importe del cargo, hoy no soportadas |
| MT-11 | Dividir línea100 en40+60, IDs distintos, mismo alcance y duplicate_fields vacío | A/E/Δ/estado por grupo igual; charge_ids/ID del finding/cantidad de cargos cambian: comparar por alcance, no hash |
| MT-12 | Reunir dos operaciones N→1 con `sum`, sin mínimo ni redondeo intermedio | E combinado=E1+E2; con mínimo/porcentaje por envío no afirmar aditividad |
| MT-13 | Cambiar Decimal global prec/redondeo y restaurarlo | Resultado completo igual dentro del dominio exacto del motor |
| MT-14 | Intercalar cliente B entre dos auditorías A, con IDs/tablas iguales y precios diferentes | A completo igual en ejecuciones; catálogo/archivos/DB separados |
| MT-15 | Aplicar decisión APPROVED/REJECTED | Resultado y hash iguales, cadena de decisiones crece; UI distingue ambas columnas |
| MT-16 | Agregar cargo en otra moneda con acuerdo compatible independiente | Bucket previo intacto; se agrega bucket nuevo sin total convertido |
| MT-17 | Convertir clave mediante alias direccional explícito y equivalente | Economía igual sólo si grafo final de asociaciones es el mismo; traza y config hash cambian |
| MT-18 | Cambiar fila de tabla nunca utilizada | Economía igual; snapshot y semantic_hash cambian; no exigir hash completo igual |
| MT-19 | Cambiar nombre/etiqueta del lote | Resultado completo igual; input_hash y run_id pueden cambiar |
| MT-20 | Mover una operación al otro lado de frontera temporal | Caso de **cambio esperado**, no invariancia: debe cambiar versión/precio o volverse indeterminado |

## Generadores con significado

`qa/generators.py` produce casos válidos de tarifa por unidad+mínimo+porcentaje con racionales terminantes, importes reales iguales al esperado y tolerancia cero. Después permite invalidar una sola precondición: evidencia, matching, versión, fecha o integridad de importación. Los bordes de tolerancia están en tests manuales existentes; su generador específico sigue pendiente. Este orden permite atribuir causalidad y hacer shrinking hacia un caso mínimo, sin `assume` que descarte casi todos los ejemplos.

Backlog: calendario con pares de intervalos adyacentes/gap/overlap; tablas con una clave única y luego segunda coincidencia; bandas con límites repetidos; bipartitos de matching 1→N/N→1/solapados; mappings de permutaciones/bijecciones de conceptos; cobertura y evidencia con cada ámbito. Invalidar una dimensión por caso. Valores negativos se prueban como aritmética firmada, sin asumir que un contrato los autoriza.

Perfil nuevo: `QA_PROFILE=smoke` 25 ejemplos, `ci` 100, `nightly` 1000, un proceso. No se alteran los budgets explícitos de las pruebas antiguas. Conservar versión Hypothesis, seed, ejemplo mínimo y raw JSON ficticio; una seed sola no garantiza reproducción entre versiones. No desactivar health checks globalmente. Fuentes primarias: [estrategias](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html) y [configuración/reproducción](https://hypothesis.readthedocs.io/en/latest/reference/api.html).
