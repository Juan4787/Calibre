# Carrera detectada por CI en el oráculo de preparación

El run 40922533991 del head 61109c4 falló al intentar pulsar Continuar a Verificación, oculto porque la UI seguía en Datos. Lint/tipos, 330 pruebas, corpus 62/62 y build habían pasado. El E2E del head 29cd2bc pasó y las ejecuciones locales también; no se usaron para tapar el fallo remoto.

La condición del test era `to_contain_text("filas aceptadas")`, que también coincidía con el texto inicial `Validar para ver filas aceptadas, rechazos y origen de los datos.` En el runner rápido la prueba intentó avanzar antes de recibir la importación de cargos. El guard de la app mantuvo Datos; luego llegó la respuesta y mostró 46 aceptados. `ci-readiness-failure.jpeg` conserva la pantalla final. Seleccionar un archivo mediante un input oculto no comprueba que su paso esté abierto, por lo que ese paso de la prueba pudo continuar hasta el click que falló.

Corrección del oráculo: exigir exactamente 32 operaciones/46 cargos aceptados y botón de validación habilitado; comprobar que Acuerdo esté visible antes de cargar su archivo. Nueva comprobación causal: mantener pendiente deliberadamente la respuesta de cargos, intentar avanzar, exigir que Datos siga abierto y el mensaje pida validar; liberar respuesta y recién entonces continuar. No se aumentaron timeouts ni se relajó el guard de producto.

No cambió ningún archivo del producto ni los assets certificados. Se reejecuta el E2E del wheel instalado y la CI del commit corregido. Consultar CONTINUATION.md para su resultado efectivo y publicación; este documento no sustituye el recibo final.


## Segunda comprobación: preservar el archivo en la intercepción

La retención mediante route.fetch/fulfill reenviaba el multipart con un archivo de cero bytes en este entorno. Parsear los cuerpos capturados como MIME demuestra partes file de tamaño 0, cuerpos de 1242 y 977 bytes y respuestas 422; ver route-fetch-file-omission.json. El control reforzado de 46 filas detectó esa omisión. Antes, la respuesta inválida de la prueba de origen obsoleto se descartaba y no exigía que el original válido hubiera llegado intacto.

Se sustituyó ese reenviado por retener la ruta y liberarla con route.continue_(), que deja enviar la solicitud original del navegador. La prueba exige respuesta 200 tanto para la operación obsoleta como para los cargos pendientes, además de verificar que una respuesta obsoleta no restaure datos descartados. El E2E completo sobre Python real del wheel 0.3.0 vuelve a pasar. Falta CI remota del commit con esa corrección antes de publicar; no se aumentan timeouts ni se eliminan asserts.
