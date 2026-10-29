# Implementación por etapas — 29/10/2026

Autorización: implementar los hallazgos de la auditoría independiente, publicar por etapas en GitHub e instalar localmente. El usuario aclaró que no existe una instalación en uso: se crea una instalación nueva y una base vacía. No se usan bases de demostración como datos operativos.

## Etapas

1. **Certeza e integridad (0.2.0).** Fechas civiles; explicit sin corroboración en revisión; tipos semánticos; procedencia cotejada; originales obligatorios al exportar; límites CLI; XLS oculto; exactitud del control externo; exportación de texto no representable; corpus adversarial y gates causales.
2. **Operación (0.3.0).** Importaciones conservadas en servidor; solicitudes por referencias; carga por teclado; control documental integrado; resumen contractual y respaldo estructurado; relación entre corridas; identificación de espacio de trabajo y backup/restauración.
3. **Rendimiento y distribución (0.3.1).** XLSX progresivo y presupuestos de recursos; builds y dependencias reproducibles; instalación aislada y actualización reversible; CI y protección de rama con checks comprobados.
4. **Auditoría final.** Regresiones causales, referencia independiente, mutaciones aplicables, multicanal, navegador, integridad/historia/restauración, distribución instalada y readback remoto.

Cada entrega requiere: commit identificado, pruebas del caso que fallaba, regresión relacionada, artefacto construido e instalado fuera del checkout, evidencia preservada y comprobación del destino publicado. No se declara una fase aprobada por cantidad de pruebas. Las etapas pueden agrupar correcciones necesarias para mantener sus invariantes.

## Límites que requieren hechos externos

- El piloto con un cliente real exige sus originales, contrato, alcance y control independiente; no se fabrican datos ni aprobaciones.
- Windows/Excel en el equipo del operador exige ese entorno; el runner Windows sólo acredita lo ejecutado en CI.
- No se agregan fórmulas comerciales, impuestos, prorrateos ni excepciones sin un contrato que los defina.
- Las corridas históricas conservan su resultado y necesitan su artefacto original para replay.

## Estado

- Preservación inicial: código y archivos sin seguimiento guardados fuera del repo; copias SQLite verificadas de las cinco bases locales existentes. Ninguna se declara base de producción.
- Implementación y recibos por etapa: se incorporan al completar sus verificaciones.

- Etapa 1: entregada 0.2.0, release y primera instalación local verificadas.
- Etapa 2: entregada 0.3.0, PR #3/main 7724b5a, CI PR/main/release aprobadas, assets exactos descargados y servicio activo con schema2. Recibo stage2/receipt.json.
- Etapa activa: 3, rendimiento/distribución; recibo stage3/receipt.json (pendiente de implementación). Auditoría final pendiente.
