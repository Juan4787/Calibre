# Primer cliente real: experimento controlado

El objetivo es comprobar si podemos representar el acuerdo y aportar una verificación incremental con esfuerzo sostenible. Los datasets ficticios del repositorio no validan tarifas, usos del sector, ahorro, disposición a pagar ni product-market fit.

## Información exacta a solicitar

1. Un período cerrado que el cliente ya haya controlado, con archivos **originales** de operación y detalle de cargos. Pedir formato nativo XLSX/XLS/CSV, no sólo PDF de factura.
2. Qué representa cada fila, columna y archivo; si una fila es viaje, despacho, remito, servicio, concepto, subtotal, ajuste o nota de crédito. Identificadores únicos reales y sus ceros iniciales.
3. Relación entre factura, liquidación y detalle. Alcance completo del período, documentos excluidos, líneas de resumen y reconciliación de totales. Importes netos o brutos, impuestos incluidos o separados y moneda exacta.
4. Contrato, anexos y todas las versiones aplicables, con sus documentos de origen. Fecha de inicio y fin, fecha operativa que determina vigencia y tratamiento de servicios que cruzan versiones.
5. Qué unidad genera cada cargo: operación, remito, lote, consolidado, vehículo, período u otra. Cuándo varias líneas son legítimas, cuándo se agrupan y cómo se evita contar dos veces una operación.
6. Catálogo **propio de esa fuente** de conceptos y aliases. No asumir que “demora” equivale a “estadía” ni que dos nombres parecidos significan el mismo servicio.
7. Fórmulas, tarifas, lookup de zonas/rutas/vehículos, unidades, mínimos, máximos, tramos y límites inclusivos/exclusivos. Factores volumétricos o indexadores sólo si el acuerdo los define, con valor y respaldo documental.
8. Política de redondeo: dónde se redondea (línea, componente o total), cantidad de decimales y modo. Tolerancias absolutas y relativas expresamente aceptadas.
9. Evidencia requerida para cada concepto, alternativas válidas, quién la valida, qué demuestra, relación con operaciones y cargos, tratamiento de faltantes y excepciones.
10. Quién toma la decisión final, qué acciones existen, qué documentación necesita el responsable y cómo conserva su resolución.
11. Volumen por cierre, computadora/Windows disponible, restricciones de instalación, tratamiento de archivos sensibles y responsable de backups.
12. Resultado de su control previo en un archivo separado: diferencias encontradas, casos aceptados, excepciones y tiempo invertido. **No leerlo hasta terminar la primera auditoría ciega.**

No completar un dato contractual faltante con una práctica supuestamente “normal”. Registrarlo como punto abierto y dejar el caso indeterminado.

## Procedimiento

1. Guardar una copia intacta de los originales en una carpeta del caso. No editar el original para hacerlo encajar.
2. Describir qué constituye una operación y un cargo y qué período/transportista cubre cada fuente. Separar encabezados, subtotales y líneas documentales de líneas auditables de manera explícita.
3. Copiar un proyecto de ejemplo en una carpeta nueva. Crear mappings que conserven IDs y procedencia. Ejecutar `preview` y revisar todas las conversiones, rechazos y conceptos desconocidos.
4. Representar el acuerdo en JSON. Agregar ejemplos unitarios del contrato: valores por debajo/en/encima de límites, cambio de vigencia, redondeo y evidencia faltante. Usar expectativas calculadas independientemente, no extraídas del propio motor.
5. Pedir al cliente que confirme por escrito que la representación refleja su acuerdo. Esa confirmación es evidencia del experimento, no una afirmación automática del software.
6. Definir el alcance de comparación y, si corresponde, de conceptos ausentes. No activar `detect_missing` sobre un conjunto operativo sin confirmar que la liquidación lo cubre.
7. Ejecutar la auditoría ciega y conservar el paquete y el programa usados. Usar `replay` para confirmar reproducción.
8. Comparar con el control previo. Revisar cada diferencia con el responsable. Registrar decisiones sin cambiar la conclusión original del motor. Nueva evidencia o correcciones se auditan en una nueva corrida.
9. Medir en `PILOT_SCORECARD.csv`: volumen, montos por moneda, cobertura, diferencias confirmadas conocidas/nuevas, falsos positivos, casos indeterminados, preparación, auditoría y revisión humana de ambos lados.
10. Analizar si hay valor incremental y si preparar/mantener reglas cuesta menos que ese valor. Un motor correcto con cero beneficio incremental también es un resultado válido del experimento.

## Regla para ampliar el producto

Antes de cambiar el core, escribir un ejemplo mínimo del contrato que las primitivas actuales no representan. Clasificarlo:

- **Configuración**: nombres de columnas, claves, tarifas, tablas, vigencias, condiciones, evidencia y redondeos. No requiere código nuevo.
- **Abstracción general justificada**: por ejemplo, asignación explícita entre varios servicios o redondeo por componente no expresable hoy. Incorporar una primitiva acotada con tests de incertidumbre y otro ejemplo independiente.
- **Excepción de cliente**: un `if cliente == ...`, una fórmula oculta en un importador o un alias global. Rechazar esa implementación y representar la decisión como configuración o intervención humana.

El costo principal aún no demostrado es interpretar, confirmar y mantener el acuerdo. Aunque el código sea reusable, un onboarding que demanda días de trabajo exclusivo por cliente puede seguir siendo consultoría. Registrar esas horas y el número de cambios de core por cliente.

## Lo que probablemente cambie

Layouts tabulares reales, servicios consolidados, identidad de operaciones, reglas de facturación parcial, evidencia, subtotales y notas de crédito, necesidad de distribuir esperados, UX de configuración y packaging Windows. Ninguno de esos comportamientos se presume definido por este prototipo.

## Lo que debería sobrevivir

Separación entre datos y configuración; decimales con redondeo explícito; AST acotado con trazas; certeza conservadora; procedencia; snapshots; decisión humana separada; pruebas de propiedades; importadores con mapping; CLI independiente de UI; exportación y reproducción.

## Qué no construir todavía

Auth SaaS, organizaciones, permisos complejos, billing, pagos, cobros automáticos, reclamos automáticos, emails, WhatsApp, ARCA, bancos, ERP/TMS automáticos, GPS, tracking, routing, driver app, OCR general o LLM que determine cargos. Primero medir la auditoría con archivos y acuerdos reales confirmados.
