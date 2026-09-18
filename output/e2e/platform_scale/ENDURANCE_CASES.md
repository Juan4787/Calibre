# Protocolo de Endurance y Estabilidad: Subfase 9R

Este documento define la metodología de evaluación de fatiga y estabilidad de recursos a largo plazo en Calibre.

---

## 1. Objetivo y Escenario

El objetivo es descartar fugas de memoria (memory leaks), descriptores de archivo huérfanos (unclosed file descriptors/handles) y degradación progresiva de tiempos tras ejecuciones sucesivas continuadas dentro de un único proceso de larga duración.

### Condiciones del Ensayo
* **Ciclos:** 50 auditorías completas consecutivas.
* **Proceso:** Proceso Python único persistente (sin reinicios entre iteraciones).
* **Flujo por ciclo:**
  1. Carga de dataset sintético moderado (ej. 2.500 operaciones representativas con mezcla de PASS, FAIL, REVIEW y monedas ARS/USD).
  2. Ejecución del motor `audit()`.
  3. Guardado en SQLite `Store.save()`.
  4. Carga e hidratación `Store.load()`.
  5. Replay transaccional `Store.replay()`.
  6. Exportación completa a JSON, XLSX y HTML.
  7. Creación de bundle ZIP y verificación de integridad.

---

## 2. Métricas Capturadas por Ciclo

En cada una de las 50 iteraciones se registrarán:
* `iteration`: Número de ciclo (1 a 50).
* `wall_time_s`: Tiempo total de ejecución del ciclo en segundos.
* `rss_kib`: Memoria residente física del proceso (obtenida via `/proc/self/status` `VmRSS` y `resource.getrusage`).
* `open_fds`: Cantidad de descriptores de archivos abiertos (inspección de `/proc/self/fd`).
* `db_size_bytes`: Tamaño del archivo SQLite y archivos WAL/SHM.
* `temp_files_count`: Conteo de archivos residuales en el directorio temporal asignado.

---

## 3. Protocolo de Reinicio y Verificación Final

Tras completar los 50 ciclos:
1. Se finaliza el proceso de auditoría.
2. Un nuevo proceso independiente abre la base de datos acumulada.
3. Se ejecuta `PRAGMA integrity_check` y `PRAGMA foreign_key_check`.
4. Se ejecuta el replay de la primera corrida (#1), la corrida intermedia (#25) y la última corrida (#50).
5. Se verifica que los hashes de resultado y la identidad semántica sean 100% idénticos.

---

## 4. Criterios de Clasificación de Estabilidad

* **STABLE:** El uso de RSS se estabiliza tras las primeras 5 a 10 iteraciones (efecto de warm-up y pools de asignación de Python/SQLite) y no muestra una pendiente positiva monótona y sostenida. Los FDs se mantienen constantes entre ciclos.
* **SUSPICIOUS:** El uso de RSS o FDs muestra aumentos esporádicos o mesetas ascendentes que requieren análisis de referencias cíclicas o buffers de exportación.
* **LEAK-LIKE:** El RSS o el conteo de FDs crece de forma continua y lineal en cada ciclo sin estabilizarse, evidenciando retención indebida de objetos en memoria o conexiones SQLite no cerradas.
* **INCONCLUSIVE:** Dispersión extrema atribuible a interferencias de hardware o SO que impiden una conclusión causal.
