# Reglas e importación

Todos los ejemplos y precios del repositorio son ficticios. El software no ofrece un tarifario por defecto aplicable a un cliente real.

## Crear un acuerdo

Copiar uno de `fixtures/agreements.json` o el contrato de `fixtures/second-client/agreements.json`. También se puede pegar en **Acuerdos y formatos → Crear una versión**. Validarlo con el schema generado en `docs/schemas/agreement.schema.json` y con un período conocido antes de usarlo.

Campos obligatorios: `id`, `name`, `carrier`, `currency`, `date_field`, `scale`, `rounding`, tolerancias, `matching` y versiones. Fechas ISO, intervalos inclusivos `valid_from`–`valid_to`; final nulo significa sin final definido. El motor exige una sola versión para todas las operaciones del grupo. No usa “la última versión” como desempate.

Una regla declara `id`, `concept`, `description` y `expression`. `when` restringe su aplicabilidad; `expected` habilita su búsqueda como cargo ausente dentro de `coverage`. Dos reglas aplicables al mismo concepto son ambiguas, aunque den el mismo precio. No hay prioridad oculta.

### Expresión de ejemplo

Tarifa ficticia de 2 ARS/kg, con mínimo de 300 ARS y factor de 1,05:

```json
{
  "op": "mul",
  "args": [
    {"op": "max", "args": [
      {"op": "mul", "args": [
        {"op": "attr", "field": "weight", "unit": "kg"},
        {"op": "const", "value": {"type": "decimal", "value": "2", "unit": "ARS/kg"}}
      ]},
      {"op": "const", "value": {"type": "decimal", "value": "300", "unit": "ARS"}}
    ]},
    {"op": "const", "value": {"type": "decimal", "value": "1.05"}}
  ]
}
```

### Primitivas

| Operación | Uso y límite |
|---|---|
| `const` | Valor tipado, incluidos factores documentales explícitos |
| `attr` | Atributo único o compartido por todas las operaciones; valores distintos no se eligen arbitrariamente |
| `sum` | Suma del atributo entre operaciones, conservando unidad |
| `count` | Cantidad de operaciones del grupo, sin unidad |
| `add`, `sub`, `mul`, `div` | Aritmética; `div` exige `scale` y `rounding` |
| `min`, `max` | Límites explícitos, con operandos de unidades compatibles |
| `round` | Redondeo declarado, exige `scale` y `rounding` |
| `lookup` | Coincidencia exacta de claves contra tabla de la versión; 0 o más de 1 coincidencias = indeterminado |
| `band` | Tramos `[lower, upper)`, sin extrapolación ni elección de primera coincidencia |
| `if` | Condicional; sólo ejecuta la rama seleccionada |
| `eq`, `gt`, `gte`, `lt`, `lte` | Condiciones tipadas; las desigualdades son numéricas |
| `and`, `or`, `not` | Condiciones booleanas; no convierten datos faltantes en falso |

Los modos admitidos son `ROUND_HALF_UP`, `ROUND_HALF_EVEN`, `ROUND_DOWN` y `ROUND_UP`. Se permiten hasta 30 niveles y 1.000 nodos por expresión. Los parámetros sobrantes se rechazan. No existen scripts, ciclos, plugins de ejecución ni funciones arbitrarias.

Las tablas de lookup se indexan por versión durante una corrida. Las bandas se recorren para detectar huecos y superposiciones. Un factor de actualización documental se puede representar como parámetro o lookup versionado con `source_note`; no se descarga ni se inventa un índice.

Un recargo porcentual puede ser una fórmula compuesta. Esta versión no referencia el resultado de otra regla por ID; repetir una subexpresión declarativa es posible, pero debe revisarse el mantenimiento. Una futura biblioteca de subexpresiones debe evitar ciclos y mantener trazas.

## Crear un mapping

Un mapping contiene `id`, `version`, `entity` (`shipments` o `charges`), hoja, fila de encabezado, delimitador, codificación, separadores numéricos, formatos de fecha y columnas. Cada columna declara `source` o `constant` (exclusivos), `target`, tipo, unidad y si es obligatoria.

```json
{
  "id": "despachos-proveedor",
  "version": "1",
  "entity": "shipments",
  "sheet": "Despachos",
  "header_row": 2,
  "decimal_separator": ",",
  "thousands_separator": ".",
  "date_formats": ["%d/%m/%Y"],
  "columns": [
    {"source": "ID interno", "target": "id", "type": "text"},
    {"source": "Numero Rem.", "target": "reference", "type": "text"},
    {"constant": "transportista-configurado", "target": "carrier", "type": "text"},
    {"source": "Peso KG", "target": "attributes.weight", "type": "decimal", "unit": "kg"},
    {"source": "Fecha", "target": "attributes.service_date", "type": "date"}
  ]
}
```

Los cargos requieren también `settlement`, `agreement`, `concept`, `amount` y `currency`. El mapping de importes usa la convención del archivo; el JSON normalizado y las reglas siempre usan punto decimal y strings.

`concept_map` establece equivalencias sólo para esa fuente. Si hay diccionario y un concepto no figura, se conserva como `external:nombre` con advertencia: no puede coincidir accidentalmente con un concepto canónico.

El mapping se puede cargar como JSON, reutilizar desde la biblioteca local y editar desde la UI. No hay todavía un constructor visual de reglas ni un asistente gráfico de columnas; hoy el operador técnico debe aprender este schema, sin editar código del producto.

## Casos de archivo

- CSV: delimitador y codificación explícitos (`utf-8-sig` o `cp1252`); soporta campos entrecomillados y multilínea. `header_row` cuenta registros CSV, y la procedencia conserva la línea física inicial real.
- XLSX: hoja explícita si existe más de una; encabezados desplazados admitidos; se ignoran columnas no mapeadas. Una hoja seleccionada oculta o con filas/columnas pobladas ocultas **bloquea** la importación: hacer visibles los datos, revisar su alcance y volver a importar. No se descarta una fila oculta en silencio. Las fórmulas y errores en celdas mapeadas se rechazan; no se usa un valor cacheado silenciosamente. Las entradas ZIP repetidas o con rutas ambiguas también se rechazan. Los números se recuperan del XML original y pasan directamente a Decimal, sin usar el float del lector; su token original queda en la procedencia. La notación científica del archivo se admite con límites de dígitos y exponente antes de expandirla. Esto conserva lo que contiene el archivo, sin reconstruir precisión que Excel ya hubiera perdido antes de guardarlo.
- XLS: requiere aceptar explícitamente `allow_xls_cached_values` o convertir a XLSX/valores verificados. El lector legacy no ofrece aquí una garantía de distinguir fórmula de valor; se emite advertencia permanente en el lote. Los números del formato binario conservan la precisión disponible en ese archivo, sin recuperar decimales originales que no estén representados; para importes de alta precisión, aportar texto decimal verificado.
- Identificadores numéricos de Excel: rechazados por defecto. `numeric_text: "formatted"` permite un entero seguro y conserva un formato de ceros `000000`. No puede recuperar ceros que el archivo ya perdió.
- Fechas: no se infiere D/M contra M/D; varios formatos con dos interpretaciones causan rechazo. Hora o zona horaria no se trunca a fecha.
- Números: `1.234,56` se interpreta únicamente con separadores correspondientes. Agrupaciones como `1.23,45`, exponentes textuales, valores no finitos o símbolos de moneda se rechazan.
- Falta de una columna obligatoria es error del archivo/mapping. Falta de una celda requerida rechaza la fila. Campos opcionales pueden quedar ausentes; una regla que los necesite resulta indeterminada.
- IDs duplicados no se fusionan ni se sustituyen: se conserva el primer registro con rechazo visible de los repetidos y el lote queda incompleto. Corregir el origen antes de confirmar comparaciones.
- Valores fuera del ancho de encabezados rechazan la fila; no se desplazan columnas automáticamente.

## Procedencia y reportes

Cada campo importado conserva hash del documento, nombre, hoja, fila, columna, texto original y mapping/transformación. Los campos constantes apuntan al mapping conservado. Las trazas referencian registro y atributo; su origen se resuelve en el snapshot.

El XLSX incluye Resumen, Hallazgos, Cálculos, Problemas de datos, Evidencia, Decisiones, Origen de datos y Metadata. Los importes se guardan como **texto decimal exacto**, para evitar que Excel degrade cifras; esto implica que una suma manual requiere convertir deliberadamente al formato numérico apropiado. No se escriben fórmulas provenientes del input. El JSON es el formato autoritativo completo. El HTML es autocontenido e imprimible a PDF desde el navegador; no depende de un servicio PDF.

Si una exportación supera 1.048.576 filas por hoja o 32.767 caracteres por celda, se rechaza el XLSX para evitar truncamiento. El ZIP sigue incluyendo el JSON completo, las fuentes, el informe y `ADVERTENCIA_EXPORTACION.txt`; no incluye una planilla parcial. Los mensajes humanos extensos de evidencia se resumen, pero la traza conserva cada requisito y cada comprobación faltante.
