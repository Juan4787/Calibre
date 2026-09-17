# Triage operativo

Abrir un registro privado con caso observado, esperado independiente, run_id, DB/cliente declarados, artefacto, original y salida. No exigir un reproducer antes de contener dinero o incertidumbre. Seguir estas decisiones en orden:

1. **¿Puede afectar importe, moneda, cargo incluido, destinatario o decisión?** Sí/desconocido: CRITICAL provisional; congelar conclusiones del alcance. No: evaluar HIGH/MEDIUM/LOW.
2. **¿Puede convertir falta de información en certeza?** Sí: IR-03 y gate bloqueado aunque Δ=0. El daño no se limita a sobrecobros.
3. **¿Es reproducible?** Conservar artefacto y ejecutar una vez en copia. Si no reproduce: comparar entorno/origen y mantener sospecha; “no reproduce” no equivale a descartado.
4. **¿Core o representación?** Comparar run verificado con salida observada. Run incorrecto→IR-01/02/03/04/05/06/07; run correcto y salida distinta→IR-08. Si run no verifica→IR-09/10/12 primero.
5. **¿Input particular o mecanismo general?** Cambiar una sola dimensión en copia. Un archivo particular puede activar un parser compartido; no reducir blast radius al único cliente que reportó.
6. **¿Qué versiones?** Comparar artefacto exacto, importer/reportero/dependencias cuando existan. Etiqueta0.1.0 no identifica bytes. Datos faltantes→unknown.
7. **¿Qué clientes/runs?** BR-01: recorrer inventario externo de DB, ejecutar consulta conservadora, preservar candidatos y motivos de exclusión. Sin inventario completo no declarar alcance completo.
8. **¿Detener?** Causa común desconocida, historia alterada, mezcla de clientes o seguridad→uso económico total. Causa aislada demostrada→cliente/feature/salida. Falla estética→continuar con nota.
9. **Minimal reproducer:** copiar bytes/config; eliminar filas irrelevantes una a una manteniendo fallo y expected; anonimizar preservando claves/tipos/fechas/límites. No alterar el único original. Registrar hash de ambos.
10. **Regresión y cierre:** test falla antes/pasa después, contraparte sana pasa, mutante causal muere, consumidores reconciliados, candidatos históricos resueltos y comunicación si hubo entregas. Sólo entonces cerrar IR.

Una tarea delegada debe devolver `causa confirmada` o `hipótesis pendiente`, nunca mezclar ambas. Escalar al responsable del producto: semántica contractual nueva, cambio de invariante, mutante presuntamente equivalente, pérdida de ancla confiable o necesidad de aceptar deuda P0. Los agentes no están autorizados por este documento a contactar clientes, eliminar historia o aprobar pagos.
