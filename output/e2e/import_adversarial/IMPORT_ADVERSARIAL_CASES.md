# Corpus Prerregistrado de Casos Adversariales de Importación (Fase 5A)

**Documento Normativo Previo a la Ejecución**  
**Fecha de Prerregistro**: 2026-09-17  
**Commit de Referencia**: `8e308cfebd5eda2c63a61a8a69ca0a5a4be80ce1`  
**Regla de Oro**: Ningún caso se ejecuta sin haber sido prerregistrado en este documento con su causa única, su resultado esperado y su impacto documental. Prohibido modificar el código de producción (`src/freight_audit/importing.py`) durante la primera pasada.

---

## 1. Resumen de Bloques y Cantidad de Casos

| Bloque | Descripción | Cantidad | Casos |
|---|---|---|---|
| **5B** | CSV y Texto Estructurado | 20 | `CSV-01` a `CSV-20` |
| **5C** | XLSX y XML Adversarial | 18 | `XLSX-01` a `XLSX-18` |
| **5D** | Identidad y Provenance Celda a Celda | 6 | `PROV-01` a `PROV-06` |
| **5E** | Política de Rechazo Seguro | 10 | `REJ-01` a `REJ-10` |
| **5F** | Corpus Diferencial y Metamórfico | 8 | `MET-01` a `MET-08` |
| **TOTAL** | | **62** | |

---

## 2. Definición del Contrato Base de Prueba

Para garantizar aislamiento causal, todos los casos utilizan como base una de dos entidades estándar:
1. **Shipment Base**: Columnas mínimas `id`, `reference`, `carrier` (o constante), `attributes.weight` (decimal), `attributes.service_date` (date).
2. **Charge Base**: Columnas mínimas `id`, `settlement`, `carrier`, `agreement`, `reference`, `concept`, `amount` (decimal), `currency`.

---

## 3. Bloque 5B: CSV y Texto Estructurado (20 Vectores Causales)

| ID | Archivo Base | Mutación Causal Única | Resultado Esperado | Valores Normalizados Esperados | Issues Esperados | Provenance Esperado |
|---|---|---|---|---|---|---|
| **CSV-01** | `base_shipments.csv` | Terminador CRLF (`\r\n`) en UTF-8 estándar. | Aceptado (1 reg) | `id="S1"`, `ref="R1"`, `weight="100.5"`, `date="2026-09-01"` | Ninguno | `row=2`, `raw="100,5"` |
| **CSV-02** | `base_shipments.csv` | Byte Order Mark UTF-8 (`\xef\xbb\xbf`) inicial (`utf-8-sig`). | Aceptado (1 reg) | Header `id` reconocido limpiamente sin `\ufeffid`. `id="S1"` | Ninguno | `row=2`, `col="id"` |
| **CSV-03** | `base_shipments.csv` | Terminador Unix LF puro (`\n`). | Aceptado (1 reg) | `id="S1"`, `weight="100.5"` | Ninguno | `row=2`, `raw="100,5"` |
| **CSV-04** | `base_shipments.csv` | Delimitador Pipe (`\|`) con `delimiter="\|"`. | Aceptado (1 reg) | `id="S1"`, `ref="R1"` | Ninguno | `row=2` |
| **CSV-05** | `base_shipments.csv` | Campo entrecomillado con delimitador interno: `"Buenos Aires, CABA"`. | Aceptado (1 reg) | `reference="Buenos Aires, CABA"` | Ninguno | `raw='"Buenos Aires, CABA"'` (o contenido strip) |
| **CSV-06** | `base_shipments.csv` | Comillas dobles escapadas: `"Transporte ""El Rápido"" SA"`. | Aceptado (1 reg) | `reference='Transporte "El Rápido" SA'` | Ninguno | `raw` contiene comillas escapadas |
| **CSV-07** | `base_shipments.csv` | Celda multilínea entrecomillada: `"Línea 1\nLínea 2"`. | Aceptado (1 reg) | `reference="Línea 1\nLínea 2"` | Ninguno | `row=2` (conserva índice físico inicial) |
| **CSV-08** | `base_shipments.csv` | Espacios en blanco alrededor de delimitadores (` S1 ; 0001 ; 100,5 `). | Aceptado (1 reg) | `id="S1"`, `ref="0001"`, `weight="100.5"` | Ninguno | Valores limpios con `strip()` |
| **CSV-09** | `base_shipments.csv` | Encabezado duplicado (`id;ref;weight;date;weight`). | Error Fatal (`ImportErrorDetail`) | Ninguno (aborta archivo) | Mensaje: `"La columna 'weight' aparece 2 veces"` | N/A |
| **CSV-10** | `base_shipments.csv` | Falta columna requerida en encabezado (`ref` omitida). | Error Fatal (`ImportErrorDetail`) | Ninguno (aborta archivo) | Mensaje: `"La columna 'ref' aparece 0 veces"` | N/A |
| **CSV-11** | `base_shipments.csv` | Fila con columna extra no declarada (`S1;R1;100,5;01/09/2026;EXTRA`). | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue categoría `row`: `"hay valores fuera de las columnas declaradas"` | N/A |
| **CSV-12** | `base_shipments.csv` | Fila corta (omite valor obligatorio `weight`: `S1;R1;;01/09/2026`). | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue categoría `row`: `"Falta un valor obligatorio"` | `raw=""` |
| **CSV-13** | `base_shipments.csv` | Formato argentino de miles y decimal (`1.234.567,89`). | Aceptado (1 reg) | `weight="1234567.89"` | Ninguno | `raw="1.234.567,89"` |
| **CSV-14** | `base_shipments.csv` | Formato anglosajón (`1,234,567.89` con `.` decimal y `,` miles). | Aceptado (1 reg) | `weight="1234567.89"` | Ninguno | `raw="1,234,567.89"` |
| **CSV-15** | `base_charges.csv` | Importe negativo válido (`-150,00`). | Aceptado (1 reg) | `amount="-150"` | Ninguno | `raw="-150,00"` |
| **CSV-16** | `base_charges.csv` | Importe con signo positivo explícito (`+150,00`). | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"Número inválido para los separadores configurados"` (el regex `sign="-?"` rechaza `+`) | `raw="+150,00"` |
| **CSV-17** | `base_shipments.csv` | Identificador con ceros a la izquierda (`0000456`). | Aceptado (1 reg) | `reference="0000456"` (exacto, sin truncar a 456) | Ninguno | `raw="0000456"` |
| **CSV-18** | `base_shipments.csv` | Caracteres Unicode extendidos y tildes (`Cañuelas`, `Transporte Güemes`). | Aceptado (1 reg) | `reference="Cañuelas - Güemes"` | Ninguno | Caracteres intactos |
| **CSV-19** | `base_shipments.csv` | Espacio de no separación invisible (`\u00a0`) dentro del número (`1\u00a0234,56`). | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"Número inválido para los separadores configurados"` | `raw="1\u00a0234,56"` |
| **CSV-20** | `base_shipments.csv` | Archivo CSV truncado abruptamente dentro de comillas (`S1;"incompleto`). | Error Fatal (`ImportErrorDetail`) | Ninguno (aborta archivo) | Mensaje: `"No se pudo leer el archivo"` | N/A |

---

## 4. Bloque 5C: XLSX y XML Adversarial (18 Vectores de Frontera Crítica)

| ID | Archivo Base | Mutación Causal Única | Resultado Esperado | Valores Normalizados Esperados | Issues Esperados | Provenance Esperado |
|---|---|---|---|---|---|---|
| **XLSX-01** | `base_shipments.xlsx` | Celdas numéricas enteras y decimales estándar (`100`, `45.67`). | Aceptado (1 reg) | `weight="45.67"` | Ninguno | `row=2`, `raw="45.67"` |
| **XLSX-02** | `base_shipments.xlsx` | Número almacenado como texto (`t="s"` en XML, valor `"00123"`). | Aceptado (1 reg) | `reference="00123"` | Ninguno | `row=2`, `raw="00123"` |
| **XLSX-03** | `base_shipments.xlsx` | Token numérico XML de 16 dígitos y 2 decimales (`1000000000000000.01`). | Aceptado (1 reg) | `weight="1000000000000000.01"` (sin pérdida de precisión float) | Ninguno | `raw="1000000000000000.01"` |
| **XLSX-04** | `base_shipments.xlsx` | Token en notación científica (`1.25E+04`). | Aceptado (1 reg) | `weight="12500"` | Ninguno | `raw="1.25E+04"` |
| **XLSX-05** | `base_shipments.xlsx` | Celda con fórmula y valor en caché (`=10*2` con `<v>20</v>`). | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"La celda contiene una fórmula o un error de Excel"` | Formula no auditada |
| **XLSX-06** | `base_shipments.xlsx` | Celda con fórmula sin valor en caché (`=SUM(A2:A3)` sin `<v>`). | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"La celda contiene una fórmula o un error de Excel"` | Rechazo seguro |
| **XLSX-07** | `base_shipments.xlsx` | Token de error nativo de Excel (`#DIV/0!`, `#N/A`, `#VALUE!`). | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"La celda contiene una fórmula o un error de Excel"` | Rechazo seguro |
| **XLSX-08** | `base_shipments.xlsx` | Fecha serial nativa de Excel (`46000` con formato de fecha). | Aceptado (1 reg) | `date="2025-12-09"` (fecha contractual exacta) | Ninguno | ISO `2025-12-09` |
| **XLSX-09** | `base_multisheet.xlsx`| Libro con 2 hojas (`Data`, `Resumen`) sin `sheet` en mapping. | Error Fatal (`ImportErrorDetail`) | Ninguno (aborta archivo) | Mensaje: `"El libro tiene varias hojas. Seleccionar una hoja explícitamente"` | N/A |
| **XLSX-10** | `base_shipments.xlsx` | Mapping solicita hoja inexistente `sheet="Facturacion"`. | Error Fatal (`ImportErrorDetail`) | Ninguno (aborta archivo) | Mensaje: `"No existe la hoja 'Facturacion'"` | N/A |
| **XLSX-11** | `base_shipments.xlsx` | Filas ocultas (`hidden="1"`) en el XML de la hoja. | Aceptado (1 reg) | Datos leídos correctamente sin desfasar numeración de fila. | Ninguno | `row` coincide con coordenada física |
| **XLSX-12** | `base_shipments.xlsx` | Celdas combinadas (`mergedCells` A2:B2; A2 con valor, B2 vacío). | Fila Rechazada si B2 es obligatorio | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"Falta un valor obligatorio"` en la celda vacía secundaria | Rechazo explícito |
| **XLSX-13** | `base_shipments.xlsx` | Filas dispersas (*sparse rows*: fila 2 con datos, fila 3 ausente, fila 4 con datos). | Aceptado (2 reg) | Registro 1 en fila 2, Registro 2 en fila 4 | Ninguno | Registro 2 tiene `row=4` exacto |
| **XLSX-14** | `base_shipments.xlsx` | Filas tras bloque vacío (5 filas en blanco intercaladas). | Aceptado (2 reg) | Filas vacías ignoradas silenciosamente; registros válidos importados | Ninguno | `row` de cada registro refleja su fila real |
| **XLSX-15** | `base_shipments.xlsx` | Valores en columna E cuando encabezados son A:D. | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"hay valores fuera de las columnas declaradas"` | Detección de columnas extra |
| **XLSX-16** | `base_shipments.xlsx` | Archivo ZIP/XLSX binariamente truncado o dañado. | Error Fatal (`ImportErrorDetail`) | Ninguno (aborta archivo) | Mensaje: `"No se pudo leer el archivo"` | N/A |
| **XLSX-17** | `base_shipments.xlsx` | ID numérico con política por defecto `numeric_text="reject"`. | Fila Rechazada | 0 aceptados, 1 rechazado (`[2]`) | Issue: `"El identificador está guardado como número y puede haber perdido ceros iniciales"` | Previene pérdida silenciosa |
| **XLSX-18** | `base_shipments.xlsx` | ID numérico `123` con formato de celda `000000` y `numeric_text="formatted"`. | Aceptado (1 reg) | `reference="000123"` (formateado con ceros a la izquierda exactos) | Ninguno | Formateo explícito |

---

## 5. Bloque 5D: Identidad y Provenance Celda a Celda (6 Casos)

| ID | Archivo Base | Operación / Transformación | Resultado Esperado | Provenance Esperado (`SourceRef`) | Invarianza Económica |
|---|---|---|---|---|---|
| **PROV-01** | `base_shipments.csv` | Importación estándar y verificación exhaustiva de los 7 atributos. | Aceptado (1 reg) | `document=SHA256`, `filename="origen.csv"`, `sheet="CSV"`, `row=2`, `column="weight"`, `raw="100,5"`, `transform="test@1:decimal"` | Paridad total |
| **PROV-02** | `base_shipments.csv` | Renombrar archivo a `factura_revisada_2026.csv`. | Aceptado (1 reg) | `filename="factura_revisada_2026.csv"`; campos económicos y `digest` idénticos. | Economía intacta |
| **PROV-03** | `base_shipments.csv` | Desplazamiento vertical: insertar 3 filas vacías antes del encabezado (`header_row=4`). | Aceptado (1 reg) | `row=5` (desplazado exactamente a la nueva fila física). | Economía intacta |
| **PROV-04** | `base_shipments.csv` | Desplazamiento horizontal: reordenar columnas físicas a `weight;date;ref;id`. | Aceptado (1 reg) | `column="weight"` apunta a la nueva posición de columna. | Registros normalizados idénticos |
| **PROV-05** | `base_shipments.csv` | Atributos adicionales dinámicos (`attributes.weight`, `attributes.volume`). | Aceptado (1 reg) | Cada atributo conserva su propio `SourceRef` independiente con su celda de origen. | Sin colapso |
| **PROV-06** | `base_shipments.csv` | Columna con valor constante en mapping (`constant("carrier", "CAMIONERA")`). | Aceptado (1 reg) | `column="(constante del mapping)"`, `raw="CAMIONERA"`, `row=2`. | Marcación explícita |

---

## 6. Bloque 5E: Política de Rechazo Seguro (10 Casos)

| ID | Archivo Base | Escenario de Ambigüedad / Inválido | Resultado Esperado | Issue / Mensaje Esperado | Regla Semántica de Rechazo |
|---|---|---|---|---|---|
| **REJ-01** | `base_shipments.csv` | Separador numérico inválido: `1.23` con miles `.` y decimal `,` (no tiene 3 dígitos tras el punto). | Fila Rechazada (`[2]`) | Issue: `"Número inválido para los separadores configurados"` | Prohibido adivinar si el punto era decimal |
| **REJ-02** | `base_shipments.csv` | Fecha ambigua: `05/06/2026` con formatos `["%d/%m/%Y", "%m/%d/%Y"]`. | Fila Rechazada (`[2]`) | Issue: `"La fecha es inválida o ambigua para los formatos configurados"` | Prohibido asumir día primero o mes primero |
| **REJ-03** | `base_shipments.xlsx`| Fecha con componente horario no nulo: `2026-06-01 14:30:00`. | Fila Rechazada (`[2]`) | Issue: `"La fecha incluye hora o zona horaria; definir primero la fecha contractual"` | Prohibido truncar la hora silenciosamente |
| **REJ-04** | `base_shipments.csv` | Identificador duplicado en el mismo archivo (`S1` repetido en filas 2 y 3). | Fila 2 Aceptada, Fila 3 Rechazada | Issue: `"Identificador 'S1' repetido; corregirlo en el archivo"` | Prohibido sobreescribir o fusionar filas |
| **REJ-05** | `base_shipments.csv` | Valor booleano ambiguo: `"quizas"` no coincide con `true_values`/`false_values`. | Fila Rechazada (`[2]`) | Issue: `"El valor no identifica un booleano único según el mapping"` | Prohibido convertir a False por omisión |
| **REJ-06** | `base_shipments.csv` | Importe obligatorio vacío (`amount=""` en cargos). | Fila Rechazada (`[2]`) | Issue: `"Falta un valor obligatorio"` | Prohibido asumir importe 0 |
| **REJ-07** | `base_charges.csv` | Concepto no mapeado (`CONCEPTO_DESCONOCIDO`). | Fila Aceptada con Warning | Issue categoría `warning`: `"concepto 'CONCEPTO_DESCONOCIDO' sin equivalencia"` | Prefijo `external:CONCEPTO_DESCONOCIDO` |
| **REJ-08** | `base_empty.csv` | Archivo de longitud 0 bytes. | Error Fatal (`ImportErrorDetail`) | Mensaje: `"No existe la fila de encabezados seleccionada"` | Prohibido generar lote vacío sin aviso |
| **REJ-09** | `base_headers.csv` | Archivo con encabezados pero sin filas de datos. | Aceptado con 0 registros | `accepted=0`, `rejected=[]`, `issues=[]` | Estado consistente sin error fatal |
| **REJ-10** | `base_shipments.csv` | Fila completamente vacía (`;;;`) entre dos filas de datos válidas. | 2 Filas Aceptadas | Fila vacía se omite silenciosamente sin rechazo ni registro corrupto. | Ignorado seguro de líneas en blanco |

---

## 7. Bloque 5F: Corpus Diferencial y Metamórfico (8 Casos)

| ID | Transformación A | Transformación B | Invarianza / Sensibilidad Verificada | Criterio de Aceptación |
|---|---|---|---|---|
| **MET-01** | Lote de 3 envíos en formato CSV estándar. | El mismo lote de 3 envíos en XLSX. | Invarianza Semántica de Formato | Los diccionarios de `records` (excluyendo filename/sheet de provenance) son estrictamente idénticos. |
| **MET-02** | Formato argentino (`1.250,75`) con mapping `,` decimal y `.` miles. | Formato anglosajón (`1,250.75`) con mapping `.` decimal y `,` miles. | Invarianza de Separador Numérico | Ambos normalizan exactamente al valor `"1250.75"`. |
| **MET-03** | Orden de columnas original `id;ref;weight;date`. | Columnas permutadas `date;weight;ref;id`. | Invarianza ante Permutación de Columnas | Ambos generan registros idénticos con provenance apuntando a la columna correcta. |
| **MET-04** | Filas en orden S1, S2, S3. | Filas en orden inverso S3, S2, S1. | Invarianza de Agregación de Lote | El conjunto de IDs `{S1, S2, S3}` y la sumatoria de pesos son estrictamente idénticos. |
| **MET-05** | CSV compacto sin espacios `S1;0001;12.5;01/01/2026`. | CSV con espacios alrededor de delimitadores ` S1 ; 0001 ; 12.5 ; 01/01/2026 `. | Invarianza ante Espacios Adicionales | Ambos normalizan a los mismos tokens limpios. |
| **MET-06** | Importe de cargo `1250.75`. | Importe de cargo `1250.76` (diferencia material de 1 centavo). | **Sensibilidad Numérica Material** | Genera un `digest` diferente y un finding de auditoría discrepante. |
| **MET-07** | Fecha contractual `2026-06-30` (Vigencia 1). | Fecha contractual `2026-07-01` (Vigencia 2). | **Sensibilidad de Fecha Frontera** | Activa versiones de acuerdo distintas y produce tarifas diferentes. |
| **MET-08** | Identificador de envío `S-100`. | Identificador de envío `S-101`. | **Sensibilidad de Identificador** | Impide el matching con el cargo que referencia `S-100` (produce cargo huérfano). |

---

## 8. Gate de Aceptación de Fase 5

El bloque de Fase 5 se considerará **APROBADO** si y sólo si:
1. Los 62 casos prerregistrados se ejecutan contra el wheel productivo en clean-room (`/tmp/calibre-e2e-generality/venv`).
2. Todo caso produce exactamente el resultado esperado (aceptación, rechazo de fila, advertencia o aborto con `ImportErrorDetail`).
3. El árbol de código de producción `src/freight_audit/` permanece 100% inalterado (`git diff --exit-code src/freight_audit/`).
4. Cualquier fallo imprevisto se aísla, documenta y clasifica por severidad y blast radius, sin parches no autorizados.
