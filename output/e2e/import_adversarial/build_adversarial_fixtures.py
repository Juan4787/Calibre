#!/usr/bin/env python3
"""Build all 62 adversarial import fixtures and mappings for Phase 5 (5A-5F)."""

import io
import json
import os
import zipfile
from datetime import date, datetime
from pathlib import Path
from openpyxl import Workbook
from freight_audit.importing import ImportMapping

BASE_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = BASE_DIR / "fixtures"
MAPPINGS_DIR = BASE_DIR / "mappings"

FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
MAPPINGS_DIR.mkdir(parents=True, exist_ok=True)


def save_mapping(name: str, mapping_dict: dict) -> Path:
    path = MAPPINGS_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping_dict, f, indent=2, ensure_ascii=False)
    return path


def base_shipments_mapping(**kwargs) -> dict:
    base = {
        "schema_version": 1,
        "id": "map_shipments_std",
        "version": "1",
        "entity": "shipments",
        "delimiter": ";",
        "encoding": "utf-8-sig",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "date_formats": ["%d/%m/%Y"],
        "columns": [
            {"source": "id", "target": "id", "type": "text"},
            {"source": "ref", "target": "reference", "type": "text"},
            {"source": None, "target": "carrier", "type": "text", "constant": "CAMIONERA_CENTRAL"},
            {"source": "weight", "target": "attributes.weight", "type": "decimal", "unit": "kg"},
            {"source": "date", "target": "attributes.service_date", "type": "date"},
        ],
    }
    base.update(kwargs)
    return base


def base_charges_mapping(**kwargs) -> dict:
    base = {
        "schema_version": 1,
        "id": "map_charges_std",
        "version": "1",
        "entity": "charges",
        "delimiter": ";",
        "encoding": "utf-8-sig",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "date_formats": ["%d/%m/%Y"],
        "columns": [
            {"source": "id", "target": "id", "type": "text"},
            {"source": "ref", "target": "reference", "type": "text"},
            {"source": None, "target": "carrier", "type": "text", "constant": "CAMIONERA_CENTRAL"},
            {"source": None, "target": "agreement", "type": "text", "constant": "AGR-2026"},
            {"source": None, "target": "settlement", "type": "text", "constant": "LIQ-001"},
            {"source": "concept", "target": "concept", "type": "text"},
            {"source": "amount", "target": "amount", "type": "decimal"},
            {"source": None, "target": "currency", "type": "text", "constant": "ARS"},
        ],
        "concept_map": {"FLETE_BASE": "base", "SEGURO": "insurance"},
    }
    base.update(kwargs)
    return base


def create_xlsx_bytes(rows, formats=None, sheet_name="Data") -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    for r in rows:
        ws.append(r)
    if formats:
        for coord, fmt in formats.items():
            ws[coord].number_format = fmt
    buf = io.BytesIO()
    wb.save(buf)
    wb.close()
    return buf.getvalue()


def inject_xml_literal(xlsx_bytes: bytes, cell_coord: str, xml_val: str, cell_type: str = "n") -> bytes:
    """Inject exact XML tokens into sheet1.xml without openpyxl float degradation."""
    import re
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as zin, zipfile.ZipFile(buf, "w") as zout:
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename == "xl/worksheets/sheet1.xml":
                text = content.decode("utf-8")
                # pattern for cell
                pattern = rf'(<c r="{cell_coord}"[^>]*>)(.*?)(</c>)'
                match = re.search(pattern, text)
                if match:
                    prefix = f'<c r="{cell_coord}"'
                    if cell_type != "n":
                        prefix += f' t="{cell_type}"'
                    new_cell = f'{prefix}><v>{xml_val}</v></c>'
                    text = re.sub(pattern, new_cell, text)
                else:
                    # fallback replace first v tag
                    text = re.sub(r'<v>[^<]+</v>', f'<v>{xml_val}</v>', text, count=1)
                content = text.encode("utf-8")
            zout.writestr(item, content)
    return buf.getvalue()


def main():
    print("=== Building Adversarial Import Fixtures ===")

    # Standard Mappings
    save_mapping("shipments_std", base_shipments_mapping())
    save_mapping("charges_std", base_charges_mapping())

    # -------------------------------------------------------------
    # Bloque 5B: CSV y Texto Estructurado
    # -------------------------------------------------------------
    # CSV-01: CRLF line endings
    (FIXTURES_DIR / "csv_01_crlf.csv").write_bytes(
        b"id;ref;weight;date\r\nS1;R1;100,5;01/09/2026\r\n"
    )

    # CSV-02: UTF-8 BOM
    (FIXTURES_DIR / "csv_02_bom.csv").write_bytes(
        b"\xef\xbb\xbfid;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )

    # CSV-03: Pure Unix LF
    (FIXTURES_DIR / "csv_03_lf.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )

    # CSV-04: Pipe delimiter
    (FIXTURES_DIR / "csv_04_pipe.csv").write_bytes(
        b"id|ref|weight|date\nS1|R1|100,5|01/09/2026\n"
    )
    save_mapping("csv_04_pipe", base_shipments_mapping(delimiter="|"))

    # CSV-05: Quoted field with delimiter inside
    (FIXTURES_DIR / "csv_05_quoted_delim.csv").write_bytes(
        b'id,ref,weight,date\nS1,"Buenos Aires, CABA",100.5,01/09/2026\n'
    )
    save_mapping("csv_05_comma", base_shipments_mapping(
        delimiter=",", decimal_separator=".", thousands_separator=""
    ))

    # CSV-06: Escaped quotes inside quoted string
    (FIXTURES_DIR / "csv_06_escaped_quotes.csv").write_bytes(
        b'id;ref;weight;date\nS1;"Transporte ""El Rapido"" SA";100,5;01/09/2026\n'
    )

    # CSV-07: Multiline cell inside quotes
    (FIXTURES_DIR / "csv_07_multiline.csv").write_bytes(
        b'id;ref;weight;date\nS1;"Linea 1\nLinea 2";100,5;01/09/2026\n'
    )

    # CSV-08: Whitespace around delimiters and tokens
    (FIXTURES_DIR / "csv_08_whitespace.csv").write_bytes(
        b"  id  ;  ref  ;  weight  ;  date  \n  S1  ;  0001  ;  100,5  ;  01/09/2026  \n"
    )

    # CSV-09: Duplicate header
    (FIXTURES_DIR / "csv_09_duplicate_header.csv").write_bytes(
        b"id;ref;weight;date;weight\nS1;R1;100,5;01/09/2026;100,5\n"
    )

    # CSV-10: Missing required header (ref omitted)
    (FIXTURES_DIR / "csv_10_missing_header.csv").write_bytes(
        b"id;weight;date\nS1;100,5;01/09/2026\n"
    )

    # CSV-11: Extra column values beyond header
    (FIXTURES_DIR / "csv_11_extra_col.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026;COL_EXTRA_VAL\n"
    )

    # CSV-12: Short row (missing weight)
    (FIXTURES_DIR / "csv_12_short_row.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;;01/09/2026\n"
    )

    # CSV-13: Argentine numbers (dot thousands, comma decimal)
    (FIXTURES_DIR / "csv_13_arg_number.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;1.234.567,89;01/09/2026\n"
    )

    # CSV-14: Anglo numbers (comma thousands, dot decimal)
    (FIXTURES_DIR / "csv_14_anglo_number.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;1,234,567.89;01/09/2026\n"
    )
    save_mapping("csv_14_anglo", base_shipments_mapping(
        delimiter=";", decimal_separator=".", thousands_separator=","
    ))

    # CSV-15: Negative amount in charges
    (FIXTURES_DIR / "csv_15_negative_amount.csv").write_bytes(
        b"id;ref;concept;amount\nC1;R1;FLETE_BASE;-150,00\n"
    )

    # CSV-16: Explicit positive amount +150,00
    (FIXTURES_DIR / "csv_16_positive_amount.csv").write_bytes(
        b"id;ref;concept;amount\nC1;R1;FLETE_BASE;+150,00\n"
    )

    # CSV-17: Leading zeroes in ID
    (FIXTURES_DIR / "csv_17_leading_zeros.csv").write_bytes(
        b"id;ref;weight;date\nS1;0000456;100,5;01/09/2026\n"
    )

    # CSV-18: Extended Unicode / accents
    (FIXTURES_DIR / "csv_18_unicode.csv").write_bytes(
        "id;ref;weight;date\nS1;Cañuelas - Güemes;100,5;01/09/2026\n".encode("utf-8")
    )

    # CSV-19: Non-breaking space \u00a0
    (FIXTURES_DIR / "csv_19_nbsp.csv").write_bytes(
        "id;ref;weight;date\nS1;R1;1\u00a0234,56;01/09/2026\n".encode("utf-8")
    )

    # CSV-20: Truncated CSV inside quote
    (FIXTURES_DIR / "csv_20_truncated.csv").write_bytes(
        b'id;ref;weight;date\nS1;"incompleto_sin_cierre\n'
    )

    # -------------------------------------------------------------
    # Bloque 5C: XLSX y XML Adversarial
    # -------------------------------------------------------------
    # XLSX-01: Standard numeric
    (FIXTURES_DIR / "xlsx_01_standard.xlsx").write_bytes(
        create_xlsx_bytes([
            ["id", "ref", "weight", "date"],
            ["S1", "R1", 45.67, datetime(2026, 9, 1)]
        ])
    )

    # XLSX-02: Number stored as text
    # In openpyxl, a string "00123" is stored as text (t="s")
    (FIXTURES_DIR / "xlsx_02_num_as_text.xlsx").write_bytes(
        create_xlsx_bytes([
            ["id", "ref", "weight", "date"],
            ["S1", "00123", 50.0, datetime(2026, 9, 1)]
        ])
    )

    # XLSX-03: XML high-precision literal (1000000000000000.01)
    raw_xlsx = create_xlsx_bytes([
        ["id", "ref", "weight", "date"],
        ["S1", "R1", 0.1, datetime(2026, 9, 1)]
    ])
    (FIXTURES_DIR / "xlsx_03_high_precision.xlsx").write_bytes(
        inject_xml_literal(raw_xlsx, "C2", "1000000000000000.01", cell_type="n")
    )

    # XLSX-04: Scientific notation
    (FIXTURES_DIR / "xlsx_04_scientific.xlsx").write_bytes(
        inject_xml_literal(raw_xlsx, "C2", "1.25E+04", cell_type="n")
    )

    # XLSX-05: Formula with cached value
    wb_form = Workbook()
    ws_form = wb_form.active
    ws_form.title = "Data"
    ws_form.append(["id", "ref", "weight", "date"])
    ws_form.append(["S1", "R1", "=10*2", datetime(2026, 9, 1)])
    buf_form = io.BytesIO()
    wb_form.save(buf_form)
    # Inject cached value into formula cell while keeping <f> tag
    raw_f = buf_form.getvalue()
    buf_f_cached = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw_f)) as zin, zipfile.ZipFile(buf_f_cached, "w") as zout:
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename == "xl/worksheets/sheet1.xml":
                content = content.replace(b"<f>10*2</f>", b"<f>10*2</f><v>20</v>")
            zout.writestr(item, content)
    (FIXTURES_DIR / "xlsx_05_formula_cached.xlsx").write_bytes(buf_f_cached.getvalue())

    # XLSX-06: Formula without cached value
    (FIXTURES_DIR / "xlsx_06_formula_nocache.xlsx").write_bytes(buf_form.getvalue())

    # XLSX-07: Error token #DIV/0!
    wb_err = Workbook()
    ws_err = wb_err.active
    ws_err.title = "Data"
    ws_err.append(["id", "ref", "weight", "date"])
    ws_err.append(["S1", "R1", "#DIV/0!", datetime(2026, 9, 1)])
    buf_err = io.BytesIO()
    wb_err.save(buf_err)
    (FIXTURES_DIR / "xlsx_07_error_token.xlsx").write_bytes(
        inject_xml_literal(buf_err.getvalue(), "C2", "#DIV/0!", cell_type="e")
    )

    # XLSX-08: Serial date (datetime with 00:00:00)
    (FIXTURES_DIR / "xlsx_08_serial_date.xlsx").write_bytes(
        create_xlsx_bytes([
            ["id", "ref", "weight", "date"],
            ["S1", "R1", 75.0, datetime(2025, 12, 9)]
        ])
    )

    # XLSX-09: Multisheet without sheet configured
    wb_multi = Workbook()
    ws1 = wb_multi.active
    ws1.title = "Data"
    ws1.append(["id", "ref", "weight", "date"])
    ws1.append(["S1", "R1", 10.0, datetime(2026, 9, 1)])
    ws2 = wb_multi.create_sheet("Resumen")
    ws2.append(["total", 10.0])
    buf_multi = io.BytesIO()
    wb_multi.save(buf_multi)
    (FIXTURES_DIR / "xlsx_09_multisheet.xlsx").write_bytes(buf_multi.getvalue())

    # XLSX-10: Nonexistent sheet requested in mapping
    save_mapping("xlsx_10_bad_sheet", base_shipments_mapping(sheet="Facturacion"))

    # XLSX-11: Hidden row
    wb_hid = Workbook()
    ws_hid = wb_hid.active
    ws_hid.title = "Data"
    ws_hid.append(["id", "ref", "weight", "date"])
    ws_hid.append(["S1", "R1", 80.0, datetime(2026, 9, 1)])
    ws_hid.row_dimensions[2].hidden = True
    buf_hid = io.BytesIO()
    wb_hid.save(buf_hid)
    (FIXTURES_DIR / "xlsx_11_hidden_row.xlsx").write_bytes(buf_hid.getvalue())

    # XLSX-12: Merged cells
    wb_mrg = Workbook()
    ws_mrg = wb_mrg.active
    ws_mrg.title = "Data"
    ws_mrg.append(["id", "ref", "weight", "date"])
    ws_mrg.append(["S1", None, 100.0, datetime(2026, 9, 1)])
    ws_mrg.merge_cells("A2:B2")
    buf_mrg = io.BytesIO()
    wb_mrg.save(buf_mrg)
    (FIXTURES_DIR / "xlsx_12_merged_cells.xlsx").write_bytes(buf_mrg.getvalue())

    # XLSX-13: Sparse rows (row 2 then row 4)
    wb_sp = Workbook()
    ws_sp = wb_sp.active
    ws_sp.title = "Data"
    ws_sp.append(["id", "ref", "weight", "date"])
    ws_sp.append(["S1", "R1", 10.0, datetime(2026, 9, 1)])
    ws_sp.append([])  # empty row 3
    ws_sp.append(["S2", "R2", 20.0, datetime(2026, 9, 2)])
    buf_sp = io.BytesIO()
    wb_sp.save(buf_sp)
    (FIXTURES_DIR / "xlsx_13_sparse_rows.xlsx").write_bytes(buf_sp.getvalue())

    # XLSX-14: Block of 5 empty rows
    wb_blk = Workbook()
    ws_blk = wb_blk.active
    ws_blk.title = "Data"
    ws_blk.append(["id", "ref", "weight", "date"])
    ws_blk.append(["S1", "R1", 10.0, datetime(2026, 9, 1)])
    for _ in range(5):
        ws_blk.append([])
    ws_blk.append(["S2", "R2", 20.0, datetime(2026, 9, 2)])
    buf_blk = io.BytesIO()
    wb_blk.save(buf_blk)
    (FIXTURES_DIR / "xlsx_14_empty_block.xlsx").write_bytes(buf_blk.getvalue())

    # XLSX-15: Extra values outside header range
    (FIXTURES_DIR / "xlsx_15_extra_col.xlsx").write_bytes(
        create_xlsx_bytes([
            ["id", "ref", "weight", "date"],
            ["S1", "R1", 50.0, datetime(2026, 9, 1), "EXTRA_VAL"]
        ])
    )

    # XLSX-16: Corrupt ZIP
    (FIXTURES_DIR / "xlsx_16_corrupt.xlsx").write_bytes(
        b"PK\x03\x04\x14\x00\x00\x00corrupted_archive_data_stream_calibre"
    )

    # XLSX-17: Numeric ID with reject policy
    (FIXTURES_DIR / "xlsx_17_num_id_reject.xlsx").write_bytes(
        create_xlsx_bytes([
            ["id", "ref", "weight", "date"],
            ["S1", 123, 50.0, datetime(2026, 9, 1)]
        ])
    )

    # XLSX-18: Numeric ID with formatted policy
    (FIXTURES_DIR / "xlsx_18_num_id_formatted.xlsx").write_bytes(
        create_xlsx_bytes(
            [
                ["id", "ref", "weight", "date"],
                ["S1", 123, 50.0, datetime(2026, 9, 1)]
            ],
            formats={"B2": "000000"}
        )
    )
    save_mapping("xlsx_18_formatted", base_shipments_mapping(
        columns=[
            {"source": "id", "target": "id", "type": "text"},
            {"source": "ref", "target": "reference", "type": "text", "numeric_text": "formatted"},
            {"source": None, "target": "carrier", "type": "text", "constant": "CAMIONERA_CENTRAL"},
            {"source": "weight", "target": "attributes.weight", "type": "decimal", "unit": "kg"},
            {"source": "date", "target": "attributes.service_date", "type": "date"},
        ]
    ))

    # -------------------------------------------------------------
    # Bloque 5D: Identidad y Provenance
    # -------------------------------------------------------------
    # PROV-01: Full SourceRef
    (FIXTURES_DIR / "prov_01_standard.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )

    # PROV-02: Renamed file
    (FIXTURES_DIR / "factura_revisada_2026.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )

    # PROV-03: Vertical shift (3 blank rows before header)
    (FIXTURES_DIR / "prov_03_vertical_shift.csv").write_bytes(
        b"\n\n\nid;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )
    save_mapping("prov_03_header4", base_shipments_mapping(header_row=4))

    # PROV-04: Horizontal shift (columns reordered)
    (FIXTURES_DIR / "prov_04_horizontal_shift.csv").write_bytes(
        b"weight;date;ref;id\n100,5;01/09/2026;R1;S1\n"
    )

    # PROV-05: Dynamic attributes
    (FIXTURES_DIR / "prov_05_attributes.csv").write_bytes(
        b"id;ref;weight;date;vol\nS1;R1;100,5;01/09/2026;2,5\n"
    )
    save_mapping("prov_05_attrs", base_shipments_mapping(
        columns=[
            {"source": "id", "target": "id", "type": "text"},
            {"source": "ref", "target": "reference", "type": "text"},
            {"source": None, "target": "carrier", "type": "text", "constant": "CAMIONERA_CENTRAL"},
            {"source": "weight", "target": "attributes.weight", "type": "decimal", "unit": "kg"},
            {"source": "date", "target": "attributes.service_date", "type": "date"},
            {"source": "vol", "target": "attributes.volume", "type": "decimal", "unit": "m3"},
        ]
    ))

    # PROV-06: Constant mapping (carrier is constant)
    (FIXTURES_DIR / "prov_06_constant.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )

    # -------------------------------------------------------------
    # Bloque 5E: Política de Rechazo Seguro
    # -------------------------------------------------------------
    # REJ-01: Ambiguous number (1.23 with dot thousands and comma decimal)
    (FIXTURES_DIR / "rej_01_bad_separator.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;1.23;01/09/2026\n"
    )

    # REJ-02: Ambiguous date
    (FIXTURES_DIR / "rej_02_ambiguous_date.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;05/06/2026\n"
    )
    save_mapping("rej_02_ambiguous_date", base_shipments_mapping(
        date_formats=["%d/%m/%Y", "%m/%d/%Y"]
    ))

    # REJ-03: Non-zero time component
    (FIXTURES_DIR / "rej_03_date_with_time.xlsx").write_bytes(
        create_xlsx_bytes([
            ["id", "ref", "weight", "date"],
            ["S1", "R1", 100.0, datetime(2026, 6, 1, 14, 30)]
        ])
    )

    # REJ-04: Duplicate ID in same file
    (FIXTURES_DIR / "rej_04_duplicate_id.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\nS1;R2;200,5;02/09/2026\n"
    )

    # REJ-05: Ambiguous boolean
    (FIXTURES_DIR / "rej_05_ambiguous_boolean.csv").write_bytes(
        b"id;ref;flag\nS1;R1;quizas\n"
    )
    save_mapping("rej_05_boolean", ImportMapping.model_validate({
        "schema_version": 1,
        "id": "map_bool",
        "version": "1",
        "entity": "shipments",
        "delimiter": ";",
        "encoding": "utf-8-sig",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "columns": [
            {"source": "id", "target": "id", "type": "text"},
            {"source": "ref", "target": "reference", "type": "text"},
            {"source": None, "target": "carrier", "type": "text", "constant": "C"},
            {"source": "flag", "target": "attributes.urgent", "type": "boolean", "true_values": ["si"], "false_values": ["no"]}
        ]
    }).model_dump())

    # REJ-06: Missing mandatory amount in charge
    (FIXTURES_DIR / "rej_06_missing_amount.csv").write_bytes(
        b"id;ref;concept;amount\nC1;R1;FLETE_BASE;\n"
    )

    # REJ-07: Unmapped concept
    (FIXTURES_DIR / "rej_07_unmapped_concept.csv").write_bytes(
        b"id;ref;concept;amount\nC1;R1;CONCEPTO_DESCONOCIDO;500,00\n"
    )

    # REJ-08: Zero byte file
    (FIXTURES_DIR / "rej_08_empty_file.csv").write_bytes(b"")

    # REJ-09: Headers only
    (FIXTURES_DIR / "rej_09_headers_only.csv").write_bytes(
        b"id;ref;weight;date\n"
    )

    # REJ-10: Blank line between data rows
    (FIXTURES_DIR / "rej_10_blank_line.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\n;;;\nS2;R2;200,5;02/09/2026\n"
    )

    # -------------------------------------------------------------
    # Bloque 5F: Corpus Diferencial y Metamórfico
    # -------------------------------------------------------------
    # MET-01: CSV vs XLSX equivalence (3 shipments)
    (FIXTURES_DIR / "met_01_data.csv").write_bytes(
        b"id;ref;weight;date\n"
        b"S1;R1;100,5;01/09/2026\n"
        b"S2;R2;200,75;02/09/2026\n"
        b"S3;R3;300;03/09/2026\n"
    )
    (FIXTURES_DIR / "met_01_data.xlsx").write_bytes(
        create_xlsx_bytes([
            ["id", "ref", "weight", "date"],
            ["S1", "R1", 100.5, datetime(2026, 9, 1)],
            ["S2", "R2", 200.75, datetime(2026, 9, 2)],
            ["S3", "R3", 300.0, datetime(2026, 9, 3)]
        ])
    )

    # MET-02: Argentine vs Anglo numeric format
    (FIXTURES_DIR / "met_02_arg.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;1.250,75;01/09/2026\n"
    )
    (FIXTURES_DIR / "met_02_anglo.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;1,250.75;01/09/2026\n"
    )
    save_mapping("met_02_anglo_map", base_shipments_mapping(
        delimiter=";", decimal_separator=".", thousands_separator=","
    ))

    # MET-03: Column permutation
    (FIXTURES_DIR / "met_03_perm_a.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )
    (FIXTURES_DIR / "met_03_perm_b.csv").write_bytes(
        b"date;weight;ref;id\n01/09/2026;100,5;R1;S1\n"
    )

    # MET-04: Row permutation
    (FIXTURES_DIR / "met_04_order_a.csv").write_bytes(
        b"id;ref;weight;date\n"
        b"S1;R1;100,5;01/09/2026\n"
        b"S2;R2;200,5;02/09/2026\n"
        b"S3;R3;300,5;03/09/2026\n"
    )
    (FIXTURES_DIR / "met_04_order_b.csv").write_bytes(
        b"id;ref;weight;date\n"
        b"S3;R3;300,5;03/09/2026\n"
        b"S1;R1;100,5;01/09/2026\n"
        b"S2;R2;200,5;02/09/2026\n"
    )

    # MET-05: Whitespace invariance
    (FIXTURES_DIR / "met_05_compact.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/09/2026\n"
    )
    (FIXTURES_DIR / "met_05_spaced.csv").write_bytes(
        b" id ; ref ; weight ; date \n  S1  ;  R1  ;  100,5  ;  01/09/2026  \n"
    )

    # MET-06: 1 Cent difference sensitivity
    (FIXTURES_DIR / "met_06_amt_a.csv").write_bytes(
        b"id;ref;concept;amount\nC1;R1;FLETE_BASE;1250,75\n"
    )
    (FIXTURES_DIR / "met_06_amt_b.csv").write_bytes(
        b"id;ref;concept;amount\nC1;R1;FLETE_BASE;1250,76\n"
    )

    # MET-07: Boundary date sensitivity
    (FIXTURES_DIR / "met_07_date_a.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;30/06/2026\n"
    )
    (FIXTURES_DIR / "met_07_date_b.csv").write_bytes(
        b"id;ref;weight;date\nS1;R1;100,5;01/07/2026\n"
    )

    # MET-08: Identifier sensitivity
    (FIXTURES_DIR / "met_08_id_a.csv").write_bytes(
        b"id;ref;weight;date\nS-100;R1;100,5;01/09/2026\n"
    )
    (FIXTURES_DIR / "met_08_id_b.csv").write_bytes(
        b"id;ref;weight;date\nS-101;R1;100,5;01/09/2026\n"
    )

    print("All 62 fixtures and mappings built successfully!")


if __name__ == "__main__":
    main()
