# Motor y aplicación 0.2.0 — certeza e integridad

La versión cambia la política de certeza y amplía el artefacto del motor. No recalcula ni sobrescribe auditorías anteriores. Es necesario conservar la versión que produjo cada corrida para reproducirla; la lectura/verificación del paquete histórico se conserva.

## Cambios de contrato

- Fecha civil: los formatos declaran exactamente un día, mes numérico y año de cuatro dígitos. Se rechazan hora, zona y directivas repetidas. No se elige una zona contractual implícita.
- `explicit-consistency-v3`: sin candidatos por claves, un explicit válido queda REVIEW, conserva el importe original y no calcula esperado ni confirma diferencia. Su destino también protege grupos relacionados y cobertura. Corregir referencia o alias contra el original y crear una corrida nueva. La decisión humana no convierte esa asociación en un cálculo confirmado.
- El intérprete conserva el tipo semántico: fecha y texto de igual contenido no son una comparación tipada válida.
- XLS aplica la protección de hoja/fila/columna poblada oculta además del consentimiento requerido para valores guardados.
- La persistencia coteja los registros importados contra original y mapping conservado; modificar valor/cita/constante causa rechazo. El cotejo reutiliza el lector tabular y no constituye un segundo intérprete independiente. Registros sin mapping suficiente quedan identificados como aportados sin cotejo. El nivel se ve en UI, HTML y XLSX.
- Toda carga de corrida comprueba originales; fuentes faltantes/corruptas bloquean lectura/exportación con una acción de recuperación. No se ofrece como respaldado un reporte cuando falta el documento.
- Texto que Excel no representa produce una advertencia clasificada; el ZIP conserva JSON y originales sin eliminar caracteres ni incluir una planilla parcial.
- Lecturas reales acotadas: tablas y adjuntos 25 MiB; configuraciones/proyecto 8 MiB; dataset normalizado CLI 150 MiB; decisión 1 MiB; paquete comprimido 500 MiB. Se rechazan dispositivos/FIFO. El proyecto restringe fuentes a su carpeta, incluidos destinos de symlinks; `run --allow-external-paths` permite expresamente fuentes externas de confianza. Estos límites no son una garantía de RSS máxima del pipeline.
- El control externo usa Fraction, independiente de la precisión Decimal ambiental. El gate de PR incluye el corpus adversarial completo.

## Reproducciones y controles

Las 25 regresiones iniciales fallaron antes del cambio y pasaron después. Se agregaron 14 anclas contractuales calculadas a mano: precios, mínimos, recargo, condiciones, divisiones negativas, redondeo por componente/final, fronteras de bandas y consolidación con lookup. Se verifican también pertenencia, versión y regla. Los golden oficiales difieren solamente en engine_version; cantidades, estados, trazas e importes permanecen iguales.

La campaña de validación y publicación de esta etapa se registra por separado en `docs/qa-evidence/2026-10-29/stage1/`. No considerar este documento un recibo de publicación; consultar `docs/CONTINUATION.md` para el estado efectivo.

## Límites restantes

El cotejo técnico no prueba autenticidad documental, completitud del período ni fidelidad del contrato configurado. Se requiere control externo y validación real. El payload del wizard y accesibilidad de carga se resuelven en la etapa 2; reportes progresivos y distribución reproducible en la 3. No se habilitan decisiones autónomas de pago por el número de pruebas.
