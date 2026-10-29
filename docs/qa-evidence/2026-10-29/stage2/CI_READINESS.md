# Carrera detectada por CI en el oráculo de preparación

El run 40922533991 del head 61109c4 falló al intentar pulsar Continuar a Verificación, oculto porque la UI seguía en Datos. Lint/tipos, 330 pruebas, corpus 62/62 y build habían pasado. El E2E del head 29cd2bc pasó y las ejecuciones locales también; no se usaron para tapar el fallo remoto.

La condición del test era `to_contain_text("filas aceptadas")`, que también coincidía con el texto inicial `Validar para ver filas aceptadas, rechazos y origen de los datos.` En el runner rápido la prueba intentó avanzar antes de recibir la importación de cargos. El guard de la app mantuvo Datos; luego llegó la respuesta y mostró 46 aceptados. `ci-readiness-failure.jpeg` conserva la pantalla final. Seleccionar un archivo mediante un input oculto no comprueba que su paso esté abierto, por lo que ese paso de la prueba pudo continuar hasta el click que falló.

Corrección del oráculo: exigir exactamente 32 operaciones/46 cargos aceptados y botón de validación habilitado; comprobar que Acuerdo esté visible antes de cargar su archivo. Nueva comprobación causal: mantener pendiente deliberadamente la respuesta de cargos, intentar avanzar, exigir que Datos siga abierto y el mensaje pida validar; liberar respuesta y recién entonces continuar. No se aumentaron timeouts ni se relajó el guard de producto.

No cambió ningún archivo del producto ni los assets certificados. Se reejecuta el E2E del wheel instalado y la CI del commit corregido. Consultar CONTINUATION.md para su resultado efectivo y publicación; este documento no sustituye el recibo final.
