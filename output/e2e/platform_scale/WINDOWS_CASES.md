# Catálogo de Casos: Subfase 9W — Windows Real / Portabilidad

Este documento especifica los 24 casos de prueba diseñados para evaluar el comportamiento del artefacto empaquetado de Calibre en entornos Windows nativos (`windows-latest`) y comprobar su paridad con Linux.

---

## Matriz de Casos WIN-01 a WIN-24

| ID | Nombre | Descripción | Entrada / Acción | Resultado Esperado | Severidad |
|---|---|---|---|---|---|
| **WIN-01** | Clean-room Wheel Install | Instalación del `.whl` en venv aislado fuera del checkout. | `pip install freight_audit-*.whl` en `/tmp` o `%TEMP%`. | Módulo importable desde `site-packages`, `__file__` fuera del checkout de Git. | P0 |
| **WIN-02** | CLI Functionality | Ejecución de comandos del CLI productivo. | `freight-audit --help` y `freight-audit demo`. | Salida de ayuda y ejecución sin error de import o codificación de consola. | P1 |
| **WIN-03** | SQLite Database Creation | Creación y apertura de archivo SQLite. | `Store(Path("test.db"))`. | Base de datos creada con WAL, schema inicializado e `integrity_check` limpio. | P0 |
| **WIN-04** | DB Reopen Post-Process Exit | Cierre del proceso y reapertura de la DB. | Proceso 1 crea/guarda corrida, termina; Proceso 2 reabre. | `Store.load(run_id)` recupera el run exacto e intacto. | P0 |
| **WIN-05** | Transactional Replay | Replay determinista de corrida persistida. | `store.replay(run_id)`. | `identical == True`, 0 discrepancias de finding o metadata semántica. | P0 |
| **WIN-06** | Official Store Backup & Restore | Backup vía API oficial de `Store` y restauración. | `store.backup(dest_path)`, abrir nueva instancia en `dest_path`. | DB restaurada íntegra, `quick_check` OK, corridas idénticas. | P0 |
| **WIN-07** | Export JSON | Exportación multicanal JSON. | `export_run(run, "json")`. | Archivo JSON canónico válido, idéntico en contenido a la API. | P1 |
| **WIN-08** | Export XLSX | Exportación multicanal Excel XLSX. | `export_run(run, "xlsx")`. | Archivo ZIP válido, workbook sin fórmulas maliciosas, importes exactos. | P1 |
| **WIN-09** | Export HTML | Exportación multicanal HTML. | `export_run(run, "html")`. | HTML semántico seguro con UTF-8, CSS embebido y tablas exactas. | P1 |
| **WIN-10** | Bundle ZIP Integrity | Empaquetado en ZIP y verificación de bundle. | `bundle_bytes(run)` y `verify_bundle(bytes)`. | Extracción correcta de los 3 canales, hash coincidente con `run.id`. | P0 |
| **WIN-11** | Whitespace Paths | Operación en directorios con espacios. | Carpeta `Calibre QA\Auditoria de Fletes\`. | Ingesta, persistencia, export y SQLite operan sin truncamiento de ruta. | P0 |
| **WIN-12** | Unicode Directory Paths | Operación en directorios con caracteres Unicode. | Carpeta `Calibre QA\Auditoría Ñandú\`. | Manejo correcto de codificación UTF-8 / Windows MBCS, sin `UnicodeEncodeError`. | P0 |
| **WIN-13** | Unicode Filenames | Archivos de entrada y export con Unicode. | `operaciones_ñandú.xlsx`, `acuerdo_café.json`. | Apertura, lectura y generación de bundle sin fallas de filesystem. | P0 |
| **WIN-14** | CRLF Line Endings | Ingesta de CSV y JSON con saltos `\r\n`. | Archivos con terminadores Windows estándar. | Normalización correcta; economía idéntica a versión LF. | P0 |
| **WIN-15** | LF Line Endings | Ingesta de CSV y JSON con saltos `\n` en Windows. | Archivos con terminadores Unix en entorno Windows. | Ingesta limpia sin artefactos de fin de línea. | P0 |
| **WIN-16** | Concurrent SQLite Readers | Múltiples conexiones de lectura concurrentes. | Lecturas simultáneas mientras WAL está activo. | 0 bloqueos espurios, lecturas consistentes. | P1 |
| **WIN-17** | Controlled SQLite Writer Lock | Bloqueo transaccional entre 2 procesos reales. | Proceso A abre transacción inmediata, Proceso B intenta escribir. | Proceso B maneja `sqlite3.OperationalError: database is locked`, DB permanece íntegra sin escrituras parciales. | P0 |
| **WIN-18** | Backup Under Active Connection | Ejecución de backup tras operaciones previas. | Conexión con consultas previas ejecuta `backup()`. | Backup completa sin error de bloqueo ni estado pendiente. | P1 |
| **WIN-19** | Source File Locked by Another Process | Archivo de origen bloqueado para escritura por otro proceso. | Abrir archivo CSV en modo compartido de lectura. | Calibre lee el archivo para importar sin requerir acceso exclusivo de escritura. | P1 |
| **WIN-20** | Temporary Directory Cleanup | Creación y destrucción de directorios temporales. | Uso de `tempfile.TemporaryDirectory`. | Limpieza completa de archivos temporales sin handles huérfanos que bloqueen `rmdir`. | P1 |
| **WIN-21** | Long Path Handling | Rutas con profundidad jerárquica razonable. | Directorio anidado (>150 caracteres). | Resolución y acceso sin desbordamiento de buffer o `FileNotFoundError`. | P1 |
| **WIN-22** | Server Process Restart | Ciclo de vida del servidor web FastAPI. | Inicialización de app, consulta de health, terminación y reinicio. | Puerto liberado limpiamente, SQLite accesible tras reinicio. | P1 |
| **WIN-23** | Productive Local API | Flujo de auditoría interactivo vía HTTP. | Endpoints `/api/session`, `/api/demo`, `/api/runs/{id}/export/zip`. | Respuestas JSON idénticas, cookies/tokens locales válidos. | P0 |
| **WIN-24** | Playwright Chromium Headless | Verificación visual y de interacción en Windows. | Lanzamiento de navegador Chromium headless contra servidor local. | Render de tabla de findings, modal de detalle, importes visibles. | P2 |

---

## Protocolo de Paridad Linux ↔ Windows

Para evaluar la equivalencia económica:
1. Ambos sistemas ejecutarán la misma suite canónica con casos: PASS, FAIL por exceso (+), FAIL por defecto (-), REVIEW, UNDETERMINABLE, evidencia faltante, matching ambiguo, 2 liquidaciones (QA-56), vigencias distintas, ARS, USD, N:1 y 1:N.
2. Cada sistema generará su `semantic_fingerprint.json` normalizado.
3. El comparador `compare_fingerprints.py` verificará que:
   * Cada finding coincida en `status`, `currency`, `actual`, `expected`, `difference`, `confirmed_difference`.
   * Los identificadores de cargos agrupados y envíos sean equivalentes.
   * Las razones de auditoría y banderas de issue coincidan.
   * Los resúmenes por moneda sean idénticos en importes y conteos.
