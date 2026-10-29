# Directrices obligatorias de continuidad y documentación

## Al comenzar o después de cada compactación

1. Leer este archivo completo.
2. Leer `docs/CONTINUATION.md` completo antes de editar, ejecutar una publicación o declarar un resultado.
3. Leer `docs/STAGED_HARDENING_2026_10_29.md` y el recibo de la etapa activa indicado en la bitácora.
4. Contrastar la bitácora con `git status --short`, rama/HEAD y estado real del destino. No inferir publicación o instalación de una intención documentada.
5. Retomar la tarea exacta indicada; no reiniciar la investigación ni repetir pruebas aprobadas sin cambios o una preocupación nueva que lo justifique.

## Autorización y alcance persistentes

El usuario autorizó implementar todo el plan de la auditoría independiente por etapas, auditar cada etapa, publicar en GitHub y entregar una instalación local. Aclaró que no existe una instalación en uso: crear una base nueva, conservar las bases anteriores y no presentar fixtures como información de un cliente.

El usuario pidió documentar todo con claridad para que quien retome no tenga vacíos. Las publicaciones dentro del alcance ya están autorizadas: preparar y verificar el resultado concreto y continuar sin pedir otra confirmación rutinaria. Los hechos de negocio, documentos y validaciones de un cliente real deben ser aportados; no inventarlos.

## Actualización obligatoria de la bitácora

Actualizar `docs/CONTINUATION.md`:

- al cambiar de etapa o de estrategia;
- después de cada commit, publicación, instalación o reversión;
- cuando aparezca un fallo material o cambie su diagnóstico;
- antes de una compactación si se advierte que es inminente y siempre antes de una entrega al usuario.

Debe registrar: objetivo activo, decisiones y motivos, archivos/contratos afectados, versiones y hashes, comandos y resultados con ubicación de evidencia, tareas en curso y sus identificadores, estado real de GitHub/instalación, backups/reversión y siguiente acción exacta. Marcar explícitamente cualquier dato todavía desconocido o comprobación pendiente.

No escribir tokens, credenciales ni datos privados en documentación, commits o artefactos públicos. No volcar logs completos con originales de clientes. Mantener la evidencia pública ficticia y acotada.

## Rigor técnico

- Respetar originales e historia; nuevas reglas no recalculan ni sobrescriben corridas antiguas.
- Probar causalmente cada fallo, con regresión proporcionada al riesgo, y revisar sus efectos en motor, API, UI, exportación, persistencia y replay.
- Distinguir siempre implementación, prueba sintética, validación local, CI remota, artefacto publicado e instalación efectiva. Un test verde no es prueba de uso real.
- Ejecutar builds, suites, navegador y benchmarks pesados secuencialmente en este host. Acotar memoria, procesos y tamaño de campañas.
- No desplegar una etapa con un bloqueo económico o de integridad dentro de su alcance habilitado. Las restricciones deben ser efectivas y visibles.
- Mensajes operativos: problema y siguiente acción; sin stack traces ni errores técnicos crudos para el usuario final.
- No declarar una auditoría global cerrada porque terminó el presupuesto o pasó una muestra.

## Comandos y entregas

La verificación canónica es `scripts/verify.sh`; los niveles de CI están en `scripts/run_ci_tier.sh`. Revisar sus cambios y ejecutar los controles aplicables. El proceso de entrega debe comprobar el artefacto instalado fuera del checkout y conservar el código necesario para las corridas históricas.

Cada etapa debe tener un recibo en `docs/qa-evidence/` con alcance, versiones, pruebas, resultados, límites y enlaces al commit/CI/release. La bitácora enlaza esos recibos y conserva el punto de continuación.
