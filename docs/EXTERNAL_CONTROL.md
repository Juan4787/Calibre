# Control documental externo del lote

`scripts/qa.py external-control` compara una corrida guardada con cifras e inventario **preparados de forma independiente**. Permite detectar archivos esperados ausentes y discrepancias de cantidad o importe antes de aceptar el alcance del lote. Una salida verde sólo dice que la corrida coincide con ese control; no prueba que el control incluya todas las facturas ni que el contrato esté bien representado.

## Preparación

El responsable obtiene, por fuera de Freight Audit, la lista de originales del período, el SHA-256 de cada uno, la cantidad de filas de operaciones y cargos por archivo y los importes de cargos por moneda. Conserva ese control separado de la corrida y de los resultados previos. No lo genera copiando el JSON ni los totales calculados por Freight Audit: eso haría circular la comparación. Los anexos de evidencia también integran `source_hashes`, aunque no tengan filas de operaciones o cargos.

El formato `freight-audit-external-control/v1` exige exactamente:

- `source_hashes`: hashes SHA-256 de todos los originales esperados, sin repetidos.
- `shipments_by_source`: cantidad de operaciones por hash de archivo.
- `charges_by_source`: cantidad de cargos por hash de archivo.
- `charge_totals_by_source`: importes por hash de archivo y moneda, como strings decimales.
- `shipment_count`, `charge_count`: cantidades globales independientes.
- `actual_by_currency`: total facturado del lote por moneda, como strings decimales.

El ejemplo **ficticio** completo está en `fixtures/external-control.json`. Para comprobarlo:

```bash
.venv/bin/freight-audit --db .local/control-demo.db run fixtures/project.json --out output/control-demo
.venv/bin/freight-audit verify-bundle output/control-demo/auditoria.zip --replay
.venv/bin/python scripts/qa.py external-control output/control-demo/audit.json fixtures/external-control.json
```

Usar rutas nuevas para la base y la exportación. El verificador devuelve código 0 si todas las comparaciones pasan, 1 si los datos difieren y 2 si la entrada/control está mal formado. Comprueba hashes internos registrados en `audit.json`, pero **no** los bytes de `sources/`; por eso el paso previo `verify-bundle` es separado y obligatorio. Si el archivo de control afirma una fuente no presente, un cargo menos o un total diferente, el resultado es 1. No convierte un `REVIEW` o `UNDETERMINABLE` en ahorro confirmado.

El control externo no distingue por sí mismo dos errores de igual importe que se compensen ni valida las claves de negocio. Para el primer cliente debe añadirse el cotejo independiente por documento e identificador y la comparación ciega de `REAL_CLIENT_VALIDATION_PROTOCOL.md`. Si la fuente externa está incompleta, también puede pasar una corrida incompleta; el responsable debe firmar el alcance antes de interpretar los hallazgos. Gate P y Gate U permanecen cerrados sin esa evidencia.
