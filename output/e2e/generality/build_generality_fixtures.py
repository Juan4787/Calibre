#!/usr/bin/env python3
"""Generador de fixtures y configuraciones para Fase 4 (Generalidad del Motor).

Crea las estructuras documentales heterogéneas para G1 a G6:
- G1: CSV con ';', decimal ',', miles '.', columnas en español.
- G2: CSV con ',', decimal '.', fechas ISO, columnas en inglés.
- G3: Libro XLSX nativo con openpyxl, columnas con espacios.
- G4: CSV con '|', decimal '.', moneda USD.
- G5: CSV con ';', decimal ',', consolidación multiremito.
- G6: CSV con ',', composición integrada.
"""

import csv
import json
import shutil
from decimal import Decimal
from pathlib import Path

import openpyxl

BASE_DIR = Path(__file__).parent


def setup_g1():
    out = BASE_DIR / "G1"
    out.mkdir(parents=True, exist_ok=True)

    # operaciones.csv
    # Remito_Nro;Fecha_Despacho;Peso_Facturado_Kg;Origen;Destino
    s_csv = (
        "Remito_Nro;Fecha_Despacho;Peso_Facturado_Kg;Origen;Destino\n"
        "OP-G1-01;2026-02-10;120,00;Buenos Aires;Cordoba\n"
        "OP-G1-02;2026-02-15;20,00;Buenos Aires;Rosario\n"
        "OP-G1-03;2026-03-01;50,00;Buenos Aires;Mendoza\n"
    )
    (out / "operaciones.csv").write_text(s_csv, encoding="utf-8-sig")

    # cargos.csv
    # Liquidacion_Nro;Remito_Ref;Concepto_Cobro;Importe_ARS;Moneda;Carrier_Id
    c_csv = (
        "Liquidacion_Nro;Remito_Ref;Concepto_Cobro;Importe_ARS;Moneda;Carrier_Id\n"
        "CH-OP-G1-01;OP-G1-01;FLETE_TOTAL;1.953,00;ARS;EXPRESS-CARGO\n"
        "CH-OP-G1-02;OP-G1-02;FLETE_TOTAL;570,00;ARS;EXPRESS-CARGO\n"
        "CH-OP-G1-03;OP-G1-03;FLETE_TOTAL;813,75;ARS;EXPRESS-CARGO\n"
    )
    (out / "cargos.csv").write_text(c_csv, encoding="utf-8-sig")

    # Mappings
    ms = {
        "schema_version": 1,
        "id": "MAP-S-G1",
        "version": "1.0",
        "entity": "shipments",
        "delimiter": ";",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "date_formats": ["%Y-%m-%d"],
        "columns": [
            {"source": "Remito_Nro", "target": "id", "type": "text"},
            {"source": "Remito_Nro", "target": "reference", "type": "text"},
            {"constant": "EXPRESS-CARGO", "target": "carrier", "type": "text"},
            {"source": "Fecha_Despacho", "target": "attributes.fecha", "type": "date"},
            {"source": "Peso_Facturado_Kg", "target": "attributes.peso_kg", "type": "decimal", "unit": "kg"},
        ],
    }
    (out / "mapping-shipments.json").write_text(json.dumps(ms, indent=2, ensure_ascii=False))

    mc = {
        "schema_version": 1,
        "id": "MAP-C-G1",
        "version": "1.0",
        "entity": "charges",
        "delimiter": ";",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "columns": [
            {"source": "Liquidacion_Nro", "target": "id", "type": "text"},
            {"source": "Remito_Ref", "target": "reference", "type": "text"},
            {"source": "Carrier_Id", "target": "carrier", "type": "text"},
            {"constant": "AGR-G1", "target": "agreement", "type": "text"},
            {"constant": "LIQ-2026-G1", "target": "settlement", "type": "text"},
            {"source": "Concepto_Cobro", "target": "concept", "type": "text"},
            {"source": "Importe_ARS", "target": "amount", "type": "decimal"},
            {"source": "Moneda", "target": "currency", "type": "text"},
        ],
    }
    (out / "mapping-charges.json").write_text(json.dumps(mc, indent=2, ensure_ascii=False))

    # Agreement
    agr = {
        "id": "AGR-G1",
        "name": "Acuerdo G1: Peso + Mínimo + Combustible",
        "carrier": "EXPRESS-CARGO",
        "currency": "ARS",
        "date_field": "attributes.fecha",
        "scale": 2,
        "rounding": "ROUND_HALF_EVEN",
        "tolerance_absolute": "0.05",
        "tolerance_relative": "0.001",
        "matching": {
            "keys": [{"charge": "reference", "shipment": "reference"}],
            "cardinality": "one",
        },
        "versions": [
            {
                "id": "V1",
                "valid_from": "2026-01-01",
                "valid_to": "2026-12-31",
                "source_note": "Tarifario Anual G1",
                "rules": [
                    {
                        "id": "R-G1-FLETE",
                        "concept": "FLETE_TOTAL",
                        "description": "Max(500, kg * 15) * 1.085 (recargo combustible 8.5%)",
                        "expression": {
                            "op": "mul",
                            "args": [
                                {
                                    "op": "max",
                                    "args": [
                                        {
                                            "op": "const",
                                            "value": {"type": "decimal", "value": "500.00", "unit": "ARS"},
                                        },
                                        {
                                            "op": "mul",
                                            "args": [
                                                {"op": "attr", "field": "attributes.peso_kg", "unit": "kg"},
                                                {
                                                    "op": "const",
                                                    "value": {"type": "decimal", "value": "15.00", "unit": "ARS/kg"},
                                                },
                                            ],
                                        },
                                    ],
                                },
                                {
                                    "op": "const",
                                    "value": {"type": "decimal", "value": "1.085"},
                                },
                            ],
                        },
                    }
                ],
                "tables": {},
            }
        ],
    }
    (out / "agreement-g1.json").write_text(json.dumps(agr, indent=2, ensure_ascii=False))


def setup_g2():
    out = BASE_DIR / "G2"
    out.mkdir(parents=True, exist_ok=True)

    s_csv = (
        "shipment_code,dispatch_date,origin_code,destination_code,truck_type\n"
        "OP-G2-01,2026-03-15,BUE,ROS,SEMIRREMOLQUE\n"
        "OP-G2-02,2026-08-20,BUE,ROS,SEMIRREMOLQUE\n"
        "OP-G2-03,2026-09-10,BUE,COR,CHASIS\n"
        "OP-G2-04,2026-04-10,BUE,MZA,FURGON\n"
    )
    (out / "shipments.csv").write_text(s_csv, encoding="utf-8")

    c_csv = (
        "charge_id,shipment_ref,concept_name,invoiced_amount,currency_code,carrier_code\n"
        "CH-OP-G2-01,OP-G2-01,FLETE_VIAJE,450000.00,ARS,LOGISTICA-TRUCK\n"
        "CH-OP-G2-02,OP-G2-02,FLETE_VIAJE,450000.00,ARS,LOGISTICA-TRUCK\n"
        "CH-OP-G2-03,OP-G2-03,FLETE_VIAJE,504000.00,ARS,LOGISTICA-TRUCK\n"
        "CH-OP-G2-04,OP-G2-04,FLETE_VIAJE,350000.00,ARS,LOGISTICA-TRUCK\n"
    )
    (out / "charges.csv").write_text(c_csv, encoding="utf-8")

    ms = {
        "schema_version": 1,
        "id": "MAP-S-G2",
        "version": "1.0",
        "entity": "shipments",
        "delimiter": ",",
        "decimal_separator": ".",
        "thousands_separator": "",
        "date_formats": ["%Y-%m-%d"],
        "columns": [
            {"source": "shipment_code", "target": "id", "type": "text"},
            {"source": "shipment_code", "target": "reference", "type": "text"},
            {"constant": "LOGISTICA-TRUCK", "target": "carrier", "type": "text"},
            {"source": "dispatch_date", "target": "attributes.dispatch_date", "type": "date"},
            {"source": "origin_code", "target": "attributes.origin", "type": "text"},
            {"source": "destination_code", "target": "attributes.destination", "type": "text"},
            {"source": "truck_type", "target": "attributes.truck_type", "type": "text"},
        ],
    }
    (out / "mapping-shipments.json").write_text(json.dumps(ms, indent=2, ensure_ascii=False))

    mc = {
        "schema_version": 1,
        "id": "MAP-C-G2",
        "version": "1.0",
        "entity": "charges",
        "delimiter": ",",
        "decimal_separator": ".",
        "thousands_separator": "",
        "columns": [
            {"source": "charge_id", "target": "id", "type": "text"},
            {"source": "shipment_ref", "target": "reference", "type": "text"},
            {"source": "carrier_code", "target": "carrier", "type": "text"},
            {"constant": "AGR-G2", "target": "agreement", "type": "text"},
            {"constant": "LIQ-2026-G2", "target": "settlement", "type": "text"},
            {"source": "concept_name", "target": "concept", "type": "text"},
            {"source": "invoiced_amount", "target": "amount", "type": "decimal"},
            {"source": "currency_code", "target": "currency", "type": "text"},
        ],
    }
    (out / "mapping-charges.json").write_text(json.dumps(mc, indent=2, ensure_ascii=False))

    v1_rows = [
        {"keys": ["BUE", "ROS", "SEMIRREMOLQUE"], "value": {"type": "decimal", "value": "450000.00", "unit": "ARS"}},
        {"keys": ["BUE", "ROS", "CHASIS"], "value": {"type": "decimal", "value": "280000.00", "unit": "ARS"}},
        {"keys": ["BUE", "COR", "SEMIRREMOLQUE"], "value": {"type": "decimal", "value": "680000.00", "unit": "ARS"}},
        {"keys": ["BUE", "COR", "CHASIS"], "value": {"type": "decimal", "value": "420000.00", "unit": "ARS"}},
    ]
    v2_rows = [
        {"keys": ["BUE", "ROS", "SEMIRREMOLQUE"], "value": {"type": "decimal", "value": "540000.00", "unit": "ARS"}},
        {"keys": ["BUE", "ROS", "CHASIS"], "value": {"type": "decimal", "value": "336000.00", "unit": "ARS"}},
        {"keys": ["BUE", "COR", "SEMIRREMOLQUE"], "value": {"type": "decimal", "value": "816000.00", "unit": "ARS"}},
        {"keys": ["BUE", "COR", "CHASIS"], "value": {"type": "decimal", "value": "504000.00", "unit": "ARS"}},
    ]

    rule_expr = {
        "op": "lookup",
        "table": "tarifas_rutas",
        "args": [
            {"op": "attr", "field": "attributes.origin"},
            {"op": "attr", "field": "attributes.destination"},
            {"op": "attr", "field": "attributes.truck_type"},
        ],
    }

    agr = {
        "id": "AGR-G2",
        "name": "Acuerdo G2: Origen/Destino + Vehículo + Semestre",
        "carrier": "LOGISTICA-TRUCK",
        "currency": "ARS",
        "date_field": "attributes.dispatch_date",
        "scale": 2,
        "rounding": "ROUND_HALF_EVEN",
        "tolerance_absolute": "0.05",
        "tolerance_relative": "0.001",
        "matching": {
            "keys": [{"charge": "reference", "shipment": "reference"}],
            "cardinality": "one",
        },
        "versions": [
            {
                "id": "V1-SEM1",
                "valid_from": "2026-01-01",
                "valid_to": "2026-06-30",
                "source_note": "Tarifas Semestre 1",
                "rules": [
                    {
                        "id": "R-G2-RUTA-V1",
                        "concept": "FLETE_VIAJE",
                        "description": "Lookup por ruta y vehículo Semestre 1",
                        "expression": rule_expr,
                    }
                ],
                "tables": {
                    "tarifas_rutas": {
                        "kind": "lookup",
                        "rows": v1_rows,
                    }
                },
            },
            {
                "id": "V2-SEM2",
                "valid_from": "2026-07-01",
                "valid_to": "2026-12-31",
                "source_note": "Tarifas Semestre 2 (+20%)",
                "rules": [
                    {
                        "id": "R-G2-RUTA-V2",
                        "concept": "FLETE_VIAJE",
                        "description": "Lookup por ruta y vehículo Semestre 2",
                        "expression": rule_expr,
                    }
                ],
                "tables": {
                    "tarifas_rutas": {
                        "kind": "lookup",
                        "rows": v2_rows,
                    }
                },
            },
        ],
    }
    (out / "agreement-g2.json").write_text(json.dumps(agr, indent=2, ensure_ascii=False))


def setup_g3():
    out = BASE_DIR / "G3"
    out.mkdir(parents=True, exist_ok=True)

    # Excel XLSX
    wb = openpyxl.Workbook()
    ws_s = wb.active
    ws_s.title = "Operaciones"
    ws_s.append(["Nro Operacion", "Fecha Servicio", "Cant Pallets", "Cliente Destino"])
    ws_s.append(["OP-G3-01", "2026-04-05", 24, "Sucursal Norte"])
    ws_s.append(["OP-G3-02", "2026-04-12", 10, "Sucursal Oeste"])
    ws_s.append(["OP-G3-03", "2026-04-18", 15, "Sucursal Sur"])

    ws_c = wb.create_sheet(title="Liquidacion")
    ws_c.append(["ID Factura", "Ref Operacion", "Concepto Servicio", "Importe Liquidado", "Moneda Fact", "Empresa"])
    ws_c.append(["CH-OP-G3-01", "OP-G3-01", "FLETE_PALLET", 2040.00, "ARS", "PALLET-DISTRIB"])
    ws_c.append(["CH-OP-G3-02", "OP-G3-02", "FLETE_PALLET", 850.00, "ARS", "PALLET-DISTRIB"])
    ws_c.append(["CH-OP-G3-03", "OP-G3-03", "FLETE_PALLET", 1500.00, "ARS", "PALLET-DISTRIB"])

    wb.save(out / "datos_distribucion.xlsx")

    # Archivo dummy de evidencia digital
    ev_file = out / "remito_firmado_g3_01.pdf"
    ev_file.write_bytes(b"%PDF-1.4 REMITO DIGITALIZADO CONFORME OP-G3-01 FIRMA RECEPCION CLIENTE OK")
    ev_file_03 = out / "remito_firmado_g3_03.pdf"
    ev_file_03.write_bytes(b"%PDF-1.4 REMITO DIGITALIZADO CONFORME OP-G3-03 FIRMA RECEPCION CLIENTE OK")

    ms = {
        "schema_version": 1,
        "id": "MAP-S-G3",
        "version": "1.0",
        "entity": "shipments",
        "sheet": "Operaciones",
        "date_formats": ["%Y-%m-%d"],
        "columns": [
            {"source": "Nro Operacion", "target": "id", "type": "text"},
            {"source": "Nro Operacion", "target": "reference", "type": "text"},
            {"constant": "PALLET-DISTRIB", "target": "carrier", "type": "text"},
            {"source": "Fecha Servicio", "target": "attributes.fecha", "type": "date"},
            {"source": "Cant Pallets", "target": "attributes.pallets", "type": "decimal", "unit": "pallet"},
        ],
    }
    (out / "mapping-shipments.json").write_text(json.dumps(ms, indent=2, ensure_ascii=False))

    mc = {
        "schema_version": 1,
        "id": "MAP-C-G3",
        "version": "1.0",
        "entity": "charges",
        "sheet": "Liquidacion",
        "columns": [
            {"source": "ID Factura", "target": "id", "type": "text"},
            {"source": "Ref Operacion", "target": "reference", "type": "text"},
            {"source": "Empresa", "target": "carrier", "type": "text"},
            {"constant": "AGR-G3", "target": "agreement", "type": "text"},
            {"constant": "LIQ-2026-G3", "target": "settlement", "type": "text"},
            {"source": "Concepto Servicio", "target": "concept", "type": "text"},
            {"source": "Importe Liquidado", "target": "amount", "type": "decimal"},
            {"source": "Moneda Fact", "target": "currency", "type": "text"},
        ],
    }
    (out / "mapping-charges.json").write_text(json.dumps(mc, indent=2, ensure_ascii=False))

    agr = {
        "id": "AGR-G3",
        "name": "Acuerdo G3: Pallets + Evidencia Obligatoria",
        "carrier": "PALLET-DISTRIB",
        "currency": "ARS",
        "date_field": "attributes.fecha",
        "scale": 2,
        "rounding": "ROUND_HALF_EVEN",
        "tolerance_absolute": "0.05",
        "tolerance_relative": "0.001",
        "matching": {
            "keys": [{"charge": "reference", "shipment": "reference"}],
            "cardinality": "one",
        },
        "versions": [
            {
                "id": "V1",
                "valid_from": "2026-01-01",
                "valid_to": "2026-12-31",
                "source_note": "Tarifas Pallets con Evidencia",
                "rules": [
                    {
                        "id": "R-G3-PALLET",
                        "concept": "FLETE_PALLET",
                        "description": "Tarifa por pallet con remito conformado obligatorio",
                        "expression": {
                            "op": "mul",
                            "args": [
                                {"op": "attr", "field": "attributes.pallets", "unit": "pallet"},
                                {"op": "const", "value": {"type": "decimal", "value": "85.00", "unit": "ARS/pallet"}},
                            ],
                        },
                        "evidence": [
                            {
                                "any_of": ["REMITO_FIRMA_RECEPCION"],
                                "scope": "each_shipment",
                                "document_required": True,
                            }
                        ],
                    }
                ],
                "tables": {},
            }
        ],
    }
    (out / "agreement-g3.json").write_text(json.dumps(agr, indent=2, ensure_ascii=False))


def setup_g4():
    out = BASE_DIR / "G4"
    out.mkdir(parents=True, exist_ok=True)

    s_csv = (
        "tracking_id|event_date|billable_weight_kg|sender|recipient\n"
        "OP-G4-01|2026-05-02|50.00|Logistics US|Warehouse Miami\n"
        "OP-G4-02|2026-05-10|100.00|Logistics US|Warehouse Miami\n"
        "OP-G4-03|2026-05-15|500.00|Logistics US|Warehouse Miami\n"
        "OP-G4-04|2026-05-20|1500.00|Logistics US|Warehouse Miami\n"
    )
    (out / "shipments.csv").write_text(s_csv, encoding="utf-8")

    c_csv = (
        "invoice_line_id|tracking_ref|service_code|line_total_usd|curr|carrier\n"
        "CH-OP-G4-01|OP-G4-01|AIR_FREIGHT|45.00|USD|GLOBAL-CARGO-INTL\n"
        "CH-OP-G4-02|OP-G4-02|AIR_FREIGHT|110.00|USD|GLOBAL-CARGO-INTL\n"
        "CH-OP-G4-03|OP-G4-03|AIR_FREIGHT|110.00|USD|GLOBAL-CARGO-INTL\n"
        "CH-OP-G4-04|OP-G4-04|AIR_FREIGHT|420.00|USD|GLOBAL-CARGO-INTL\n"
    )
    (out / "charges.csv").write_text(c_csv, encoding="utf-8")

    ms = {
        "schema_version": 1,
        "id": "MAP-S-G4",
        "version": "1.0",
        "entity": "shipments",
        "delimiter": "|",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "date_formats": ["%Y-%m-%d"],
        "columns": [
            {"source": "tracking_id", "target": "id", "type": "text"},
            {"source": "tracking_id", "target": "reference", "type": "text"},
            {"constant": "GLOBAL-CARGO-INTL", "target": "carrier", "type": "text"},
            {"source": "event_date", "target": "attributes.date", "type": "date"},
            {"source": "billable_weight_kg", "target": "attributes.weight_kg", "type": "decimal", "unit": "kg"},
        ],
    }
    (out / "mapping-shipments.json").write_text(json.dumps(ms, indent=2, ensure_ascii=False))

    mc = {
        "schema_version": 1,
        "id": "MAP-C-G4",
        "version": "1.0",
        "entity": "charges",
        "delimiter": "|",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "columns": [
            {"source": "invoice_line_id", "target": "id", "type": "text"},
            {"source": "tracking_ref", "target": "reference", "type": "text"},
            {"source": "carrier", "target": "carrier", "type": "text"},
            {"constant": "AGR-G4", "target": "agreement", "type": "text"},
            {"constant": "LIQ-2026-G4", "target": "settlement", "type": "text"},
            {"source": "service_code", "target": "concept", "type": "text"},
            {"source": "line_total_usd", "target": "amount", "type": "decimal"},
            {"source": "curr", "target": "currency", "type": "text"},
        ],
    }
    (out / "mapping-charges.json").write_text(json.dumps(mc, indent=2, ensure_ascii=False))

    bands = [
        {"lower": "0.00", "upper": "100.00", "value": {"type": "decimal", "value": "45.00", "unit": "USD"}},
        {"lower": "100.00", "upper": "500.00", "value": {"type": "decimal", "value": "110.00", "unit": "USD"}},
        {"lower": "500.00", "upper": "1000.00", "value": {"type": "decimal", "value": "240.00", "unit": "USD"}},
        {"lower": "1000.00", "upper": None, "value": {"type": "decimal", "value": "420.00", "unit": "USD"}},
    ]

    agr = {
        "id": "AGR-G4",
        "name": "Acuerdo G4: Bandas de Peso USD",
        "carrier": "GLOBAL-CARGO-INTL",
        "currency": "USD",
        "date_field": "attributes.date",
        "scale": 2,
        "rounding": "ROUND_HALF_EVEN",
        "tolerance_absolute": "0.05",
        "tolerance_relative": "0.001",
        "matching": {
            "keys": [{"charge": "reference", "shipment": "reference"}],
            "cardinality": "one",
        },
        "versions": [
            {
                "id": "V1",
                "valid_from": "2026-01-01",
                "valid_to": "2026-12-31",
                "source_note": "Tarifas por Bandas USD",
                "rules": [
                    {
                        "id": "R-G4-BAND",
                        "concept": "AIR_FREIGHT",
                        "description": "Tarifación por bandas semiabiertas [lower, upper)",
                        "expression": {
                            "op": "band",
                            "table": "peso_bandas",
                            "args": [{"op": "attr", "field": "attributes.weight_kg", "unit": "kg"}],
                        },
                    }
                ],
                "tables": {
                    "peso_bandas": {
                        "kind": "band",
                        "unit": "kg",
                        "bands": bands,
                    }
                },
            }
        ],
    }
    (out / "agreement-g4.json").write_text(json.dumps(agr, indent=2, ensure_ascii=False))


def setup_g5():
    out = BASE_DIR / "G5"
    out.mkdir(parents=True, exist_ok=True)

    # N:1 shipments S-G5-01, S-G5-02, S-G5-03 on VIAJE-801
    # 1:N shipment S-G5-04 on VIAJE-902
    s_csv = (
        "Remito_ID;Fecha_Remito;Viaje_ID;Peso_Kg;Destinatario\n"
        "S-G5-01;2026-06-01;VIAJE-801;350,00;Depot Central\n"
        "S-G5-02;2026-06-01;VIAJE-801;450,00;Depot Central\n"
        "S-G5-03;2026-06-01;VIAJE-801;200,00;Depot Central\n"
        "S-G5-04;2026-06-05;VIAJE-902;500,00;Depot Sur\n"
    )
    (out / "remitos_consolidados.csv").write_text(s_csv, encoding="utf-8-sig")

    c_csv = (
        "Cargo_ID;Referencia_Matching;Concepto;Importe;Moneda;Carrier\n"
        "C-G5-01;VIAJE-801;FLETE_CONSOLIDADO;22.000,00;ARS;CONSOLIDADOS-DEL-SUR\n"
        "C-G5-02;VIAJE-902;FLETE_TRAMO;8.000,00;ARS;CONSOLIDADOS-DEL-SUR\n"
        "C-G5-03;VIAJE-902;SEGURO_CARGA;1.200,00;ARS;CONSOLIDADOS-DEL-SUR\n"
    )
    (out / "cargos_consolidados.csv").write_text(c_csv, encoding="utf-8-sig")

    ms = {
        "schema_version": 1,
        "id": "MAP-S-G5",
        "version": "1.0",
        "entity": "shipments",
        "delimiter": ";",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "date_formats": ["%Y-%m-%d"],
        "columns": [
            {"source": "Remito_ID", "target": "id", "type": "text"},
            {"source": "Viaje_ID", "target": "reference", "type": "text"},
            {"constant": "CONSOLIDADOS-DEL-SUR", "target": "carrier", "type": "text"},
            {"source": "Fecha_Remito", "target": "attributes.fecha", "type": "date"},
            {"source": "Peso_Kg", "target": "attributes.peso_kg", "type": "decimal", "unit": "kg"},
        ],
    }
    (out / "mapping-shipments.json").write_text(json.dumps(ms, indent=2, ensure_ascii=False))

    mc = {
        "schema_version": 1,
        "id": "MAP-C-G5",
        "version": "1.0",
        "entity": "charges",
        "delimiter": ";",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "columns": [
            {"source": "Cargo_ID", "target": "id", "type": "text"},
            {"source": "Referencia_Matching", "target": "reference", "type": "text"},
            {"source": "Carrier", "target": "carrier", "type": "text"},
            {"constant": "AGR-G5", "target": "agreement", "type": "text"},
            {"constant": "LIQ-2026-G5", "target": "settlement", "type": "text"},
            {"source": "Concepto", "target": "concept", "type": "text"},
            {"source": "Importe", "target": "amount", "type": "decimal"},
            {"source": "Moneda", "target": "currency", "type": "text"},
        ],
    }
    (out / "mapping-charges.json").write_text(json.dumps(mc, indent=2, ensure_ascii=False))

    agr = {
        "id": "AGR-G5",
        "name": "Acuerdo G5: Consolidación Multiremito (N:1 y 1:N)",
        "carrier": "CONSOLIDADOS-DEL-SUR",
        "currency": "ARS",
        "date_field": "attributes.fecha",
        "scale": 2,
        "rounding": "ROUND_HALF_EVEN",
        "tolerance_absolute": "0.05",
        "tolerance_relative": "0.001",
        "matching": {
            "keys": [{"charge": "reference", "shipment": "reference"}],
            "cardinality": "group",
        },
        "versions": [
            {
                "id": "V1",
                "valid_from": "2026-01-01",
                "valid_to": "2026-12-31",
                "source_note": "Tarifas Consolidadas",
                "rules": [
                    {
                        "id": "R-G5-CONSOL",
                        "concept": "FLETE_CONSOLIDADO",
                        "description": "Suma de peso de remitos en viaje * 22 ARS/kg",
                        "expression": {
                            "op": "mul",
                            "args": [
                                {"op": "sum", "field": "attributes.peso_kg", "unit": "kg"},
                                {"op": "const", "value": {"type": "decimal", "value": "22.00", "unit": "ARS/kg"}},
                            ],
                        },
                    },
                    {
                        "id": "R-G5-TRAMO",
                        "concept": "FLETE_TRAMO",
                        "description": "Tarifa fija por tramo individual",
                        "expression": {
                            "op": "const",
                            "value": {"type": "decimal", "value": "8000.00", "unit": "ARS"},
                        },
                    },
                    {
                        "id": "R-G5-SEGURO",
                        "concept": "SEGURO_CARGA",
                        "description": "Seguro de carga individual",
                        "expression": {
                            "op": "const",
                            "value": {"type": "decimal", "value": "1200.00", "unit": "ARS"},
                        },
                    },
                ],
                "tables": {},
            }
        ],
    }
    (out / "agreement-g5.json").write_text(json.dumps(agr, indent=2, ensure_ascii=False))


def setup_g6():
    out = BASE_DIR / "G6-composition"
    out.mkdir(parents=True, exist_ok=True)

    s_csv = (
        "shipment_id,date,origin,destination,vehicle,weight_kg\n"
        "OP-G6-01,2026-03-20,NORTE,SUR,CHASIS,350.00\n"
        "OP-G6-02,2026-04-15,NORTE,SUR,CHASIS,350.00\n"
        "OP-G6-03,2026-08-10,NORTE,SUR,CHASIS,350.00\n"
    )
    (out / "shipments.csv").write_text(s_csv, encoding="utf-8")

    c_csv = (
        "charge_id,shipment_ref,concept,amount,currency,carrier\n"
        "CH-OP-G6-01,OP-G6-01,FLETE_COMPUESTO,120000.00,ARS,INTEGRAL-LOGISTICS\n"
        "CH-OP-G6-02,OP-G6-02,FLETE_COMPUESTO,120000.00,ARS,INTEGRAL-LOGISTICS\n"
        "CH-OP-G6-03,OP-G6-03,FLETE_COMPUESTO,120000.00,ARS,INTEGRAL-LOGISTICS\n"
    )
    (out / "charges.csv").write_text(c_csv, encoding="utf-8")

    # Documento de evidencia
    (out / "remito_conforme_01.txt").write_text("CONSTANCIA DE ENTREGA FIRMADA OP-G6-01", encoding="utf-8")
    (out / "remito_conforme_03.txt").write_text("CONSTANCIA DE ENTREGA FIRMADA OP-G6-03", encoding="utf-8")

    ms = {
        "schema_version": 1,
        "id": "MAP-S-G6",
        "version": "1.0",
        "entity": "shipments",
        "delimiter": ",",
        "decimal_separator": ".",
        "thousands_separator": "",
        "date_formats": ["%Y-%m-%d"],
        "columns": [
            {"source": "shipment_id", "target": "id", "type": "text"},
            {"source": "shipment_id", "target": "reference", "type": "text"},
            {"constant": "INTEGRAL-LOGISTICS", "target": "carrier", "type": "text"},
            {"source": "date", "target": "attributes.date", "type": "date"},
            {"source": "origin", "target": "attributes.origin", "type": "text"},
            {"source": "destination", "target": "attributes.destination", "type": "text"},
            {"source": "vehicle", "target": "attributes.vehicle", "type": "text"},
            {"source": "weight_kg", "target": "attributes.weight_kg", "type": "decimal", "unit": "kg"},
        ],
    }
    (out / "mapping-shipments.json").write_text(json.dumps(ms, indent=2, ensure_ascii=False))

    mc = {
        "schema_version": 1,
        "id": "MAP-C-G6",
        "version": "1.0",
        "entity": "charges",
        "delimiter": ",",
        "decimal_separator": ".",
        "thousands_separator": "",
        "columns": [
            {"source": "charge_id", "target": "id", "type": "text"},
            {"source": "shipment_ref", "target": "reference", "type": "text"},
            {"source": "carrier", "target": "carrier", "type": "text"},
            {"constant": "AGR-G6", "target": "agreement", "type": "text"},
            {"constant": "LIQ-2026-G6", "target": "settlement", "type": "text"},
            {"source": "concept", "target": "concept", "type": "text"},
            {"source": "amount", "target": "amount", "type": "decimal"},
            {"source": "currency", "target": "currency", "type": "text"},
        ],
    }
    (out / "mapping-charges.json").write_text(json.dumps(mc, indent=2, ensure_ascii=False))

    rule_expr = {
        "op": "max",
        "args": [
            {"op": "const", "value": {"type": "decimal", "value": "100000.00", "unit": "ARS"}},
            {
                "op": "lookup",
                "table": "tarifas_zonas",
                "args": [
                    {"op": "attr", "field": "attributes.origin"},
                    {"op": "attr", "field": "attributes.destination"},
                    {"op": "attr", "field": "attributes.vehicle"},
                ],
            },
        ],
    }

    agr = {
        "id": "AGR-G6",
        "name": "Acuerdo G6: Composición (Zona + Vehículo + Mínimo + Evidencia + Vigencia)",
        "carrier": "INTEGRAL-LOGISTICS",
        "currency": "ARS",
        "date_field": "attributes.date",
        "scale": 2,
        "rounding": "ROUND_HALF_EVEN",
        "tolerance_absolute": "0.05",
        "tolerance_relative": "0.001",
        "matching": {
            "keys": [{"charge": "reference", "shipment": "reference"}],
            "cardinality": "one",
        },
        "versions": [
            {
                "id": "V1",
                "valid_from": "2026-01-01",
                "valid_to": "2026-06-30",
                "source_note": "Semestre 1",
                "rules": [
                    {
                        "id": "R-G6-COMPOSITE",
                        "concept": "FLETE_COMPUESTO",
                        "description": "Max(100k, lookup) con evidencia obligatoria V1",
                        "expression": rule_expr,
                        "evidence": [
                            {
                                "any_of": ["REMITO_CONFORME"],
                                "scope": "each_shipment",
                                "document_required": True,
                            }
                        ],
                    }
                ],
                "tables": {
                    "tarifas_zonas": {
                        "kind": "lookup",
                        "rows": [
                            {"keys": ["NORTE", "SUR", "CHASIS"], "value": {"type": "decimal", "value": "120000.00", "unit": "ARS"}}
                        ],
                    }
                },
            },
            {
                "id": "V2",
                "valid_from": "2026-07-01",
                "valid_to": "2026-12-31",
                "source_note": "Semestre 2",
                "rules": [
                    {
                        "id": "R-G6-COMPOSITE",
                        "concept": "FLETE_COMPUESTO",
                        "description": "Max(100k, lookup) con evidencia obligatoria V2",
                        "expression": rule_expr,
                        "evidence": [
                            {
                                "any_of": ["REMITO_CONFORME"],
                                "scope": "each_shipment",
                                "document_required": True,
                            }
                        ],
                    }
                ],
                "tables": {
                    "tarifas_zonas": {
                        "kind": "lookup",
                        "rows": [
                            {"keys": ["NORTE", "SUR", "CHASIS"], "value": {"type": "decimal", "value": "150000.00", "unit": "ARS"}}
                        ],
                    }
                },
            },
        ],
    }
    (out / "agreement-g6.json").write_text(json.dumps(agr, indent=2, ensure_ascii=False))


def main():
    print("Construyendo fixtures y configuraciones para G1 a G6...")
    setup_g1()
    setup_g2()
    setup_g3()
    setup_g4()
    setup_g5()
    setup_g6()
    print("[✓] Todos los fixtures generados con éxito.")


if __name__ == "__main__":
    main()
