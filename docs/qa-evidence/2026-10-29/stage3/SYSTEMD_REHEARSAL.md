# Ensayo real de actualización y reversión

Todos los datos son ficticios, en raíces NUEVAS de /tmp/calibre-implementation-20261029-CvSz5k. El servicio productivo calibre-freight.service no se detuvo ni se usó para estos ensayos. Logs de pip/servicios y DB privadas no se publican; los recibos compactos se conservan aquí.

1. **Intento inicial fallido (calibre-rehearsal-254497.service).** El journal de systemd informó `WorkingDirectory= path is not absolute` porque las comillas se conservaron como parte del valor. El intento de detener la unidad inválida retornó5 y ocultó el fallo inicial. Se corrigió la gramática de WorkingDirectory, se conservó el quoting válido de ExecStart y stop ahora distingue ausencia de PID de un proceso que no pudo detenerse. Se recarga configuración y elimina enable residual cuando una primera instalación fallida no tenía unit previa. La unit no se ordena After del mismo default.target que la incorpora.
2. **Segundo intento (calibre-rehearsal-258904.service).** Instalación inicial saludable sobre una ruta con espacios. Falló el runner: httpx.Client ya estaba abierto por consultar sesión antes de entrar en su contexto. Se corrigió el runner para inicializar el token dentro del contexto; no se modificaron asserts ni se ampliaron timeouts. La rutina finally eliminó exclusivamente su servicio y launcher.
3. **Ensayo final aprobado (calibre-rehearsal-259869.service).** Wheel0.3.0 publicado → wheel0.3.1 candidato en dos venvs reales, sin checkout. Tres clientes más base principal con originales ficticios. Actualización conserva IDs/hashes de las cuatro bases. Una corrida y un cliente nuevos se conservaron en backup posterior al revertir. Se ocupó intencionalmente OTRO puerto con una respuesta de salud incorrecta: el servicio candidato no pudo arrancar y el instalador restauró automáticamente bases, configuración, puerto y salud anteriores. [Recibo](real-upgrade-rollback.json).
4. **Recuperación del primer intento.** Tras constatar que su unidad no existía ni tenía proceso, --recover --no-service restauró su estado previo sin versión activa y conservó la DB creada durante el fallo. [Recibo](first-install-recovery.json). No es una prueba de matar el proceso en cada instrucción posible; la prueba de interrupción de migración usa además SQLite descartable y receipt pendiente.

El candidato wheel mantiene exactamente el código de producto auditado; los cambios de este ensayo afectan scripts de instalación y tests. El sdist candidato anterior contiene el instalador previo: **no publicarlo**. La distribución final requiere repetir build/certificación desde el commit concreto de main/tag.

Regresiones: tests/test_local_release.py, con parser real systemd-analyze en runtime XDG descartable, root con espacios, aislamiento de otro servicio, respaldo de todos los clientes, rollback con datos posteriores, backup alterado, cliente ausente y recuperación. Una comprobación mock no se atribuye a systemd; el recibo final anterior sí usa systemd y wheels instalados reales.

Reproducción en Linux, usando una raíz nueva:

```sh
.venv/bin/python scripts/rehearse_upgrade.py --old-wheel /ruta/0.3.0.whl --new-wheel /ruta/0.3.1.whl --root '/tmp/calibre ensayo nuevo' --output /tmp/recibo-ensayo.json
```

El script deriva nombre de servicio y puerto libres; falla si la raíz existe. Conserva logs/DB/entornos y elimina sólo su unit/launcher al terminar. No ejecutar contra una instalación en uso. Este ensayo no acredita backup fuera de disco ni datos/contrato de un cliente real, ni Windows/Excel de escritorio.
