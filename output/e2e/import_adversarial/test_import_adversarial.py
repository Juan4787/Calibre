#!/usr/bin/env python3
"""Automated runner for Phase 5: Adversarial Import and Document Fidelity (5A-5F).

Executes 62 pre-registered cases against the package of the selected Python interpreter.
Records observed data, issues, provenance, and verifies adherence to the preregistered contract.
DOES NOT MODIFY PRODUCTION SOURCE CODE.
"""

import argparse
import io
import json
import os
import re
import sys
import traceback
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import freight_audit
from freight_audit.canonical import bytes_hash, decimal_text, number
from freight_audit.importing import (
    Cell,
    ColumnMapping,
    ImportErrorDetail,
    ImportMapping,
    convert,
    excel_number,
    import_data,
    parse_decimal,
)
from freight_audit.models import Charge, Shipment
from freight_audit.storage import engine_artifact_hash

BASE_DIR = Path(__file__).resolve().parent
ROOT = BASE_DIR.parents[2]
sys.path.insert(0, str(ROOT))
from qa.evidence import source_digest
from qa.gates import import_cases_passed

FIXTURES_DIR = BASE_DIR / "fixtures"
MAPPINGS_DIR = BASE_DIR / "mappings"
OBSERVED_DIR = BASE_DIR / "observed"

def load_mapping(name: str) -> ImportMapping:
    raw = json.loads((MAPPINGS_DIR / f"{name}.json").read_text(encoding="utf-8"))
    return ImportMapping.model_validate(raw)


def load_fixture(filename: str) -> bytes:
    return (FIXTURES_DIR / filename).read_bytes()


class TestCollector:
    def __init__(self):
        self.results = []

    def record(self, test_id: str, block: str, description: str, passed: bool, expected: dict, observed: dict, notes: str = ""):
        entry = {
            "test_id": test_id,
            "block": block,
            "description": description,
            "passed": passed,
            "status": "PASS" if passed else "FAIL",
            "expected": expected,
            "observed": observed,
            "notes": notes,
        }
        self.results.append(entry)
        symbol = "✓ PASS" if passed else "✗ FAIL"
        print(f"[{symbol}] {test_id} ({block}): {description}")
        if not passed:
            print(f"     Expected: {expected}")
            print(f"     Observed: {observed}")
            if notes:
                print(f"     Notes: {notes}")


collector = TestCollector()


def run_5b_csv_tests():
    print("\n--- Running Bloque 5B: CSV y Texto Estructurado (20 Vectores) ---")
    map_std = load_mapping("shipments_std")
    map_charges = load_mapping("charges_std")

    # CSV-01: CRLF line endings
    try:
        data = load_fixture("csv_01_crlf.csv")
        res = import_data(data, "csv_01_crlf.csv", map_std)
        passed = (
            res["accepted"] == 1
            and not res["rejected"]
            and res["records"][0]["id"] == "S1"
            and res["records"][0]["attributes"]["weight"]["value"] == "100.5"
        )
        collector.record("CSV-01", "5B", "CRLF line endings in standard UTF-8", passed,
                         {"accepted": 1, "rejected": []},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("CSV-01", "5B", "CRLF line endings in standard UTF-8", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-02: UTF-8 BOM
    try:
        data = load_fixture("csv_02_bom.csv")
        res = import_data(data, "csv_02_bom.csv", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["id"] == "S1"
        collector.record("CSV-02", "5B", "UTF-8 with BOM stripped cleanly", passed,
                         {"accepted": 1, "id": "S1"},
                         {"accepted": res["accepted"], "id": res["records"][0]["id"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-02", "5B", "UTF-8 with BOM stripped cleanly", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-03: Pure Unix LF
    try:
        data = load_fixture("csv_03_lf.csv")
        res = import_data(data, "csv_03_lf.csv", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["attributes"]["weight"]["value"] == "100.5"
        collector.record("CSV-03", "5B", "Pure Unix LF line endings", passed,
                         {"accepted": 1, "weight": "100.5"},
                         {"accepted": res["accepted"], "weight": res["records"][0]["attributes"]["weight"]["value"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-03", "5B", "Pure Unix LF line endings", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-04: Pipe delimiter
    try:
        data = load_fixture("csv_04_pipe.csv")
        m_pipe = load_mapping("csv_04_pipe")
        res = import_data(data, "csv_04_pipe.csv", m_pipe)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == "R1"
        collector.record("CSV-04", "5B", "Pipe delimiter (|)", passed,
                         {"accepted": 1, "ref": "R1"},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-04", "5B", "Pipe delimiter (|)", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-05: Quoted field with delimiter inside
    try:
        data = load_fixture("csv_05_quoted_delim.csv")
        m_comma = load_mapping("csv_05_comma")
        res = import_data(data, "csv_05_quoted_delim.csv", m_comma)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == "Buenos Aires, CABA"
        collector.record("CSV-05", "5B", "Quoted field containing delimiter", passed,
                         {"accepted": 1, "ref": "Buenos Aires, CABA"},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-05", "5B", "Quoted field containing delimiter", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-06: Escaped quotes inside quoted string
    try:
        data = load_fixture("csv_06_escaped_quotes.csv")
        res = import_data(data, "csv_06_escaped_quotes.csv", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == 'Transporte "El Rapido" SA'
        collector.record("CSV-06", "5B", "Escaped double quotes in quoted text", passed,
                         {"accepted": 1, "ref": 'Transporte "El Rapido" SA'},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-06", "5B", "Escaped double quotes in quoted text", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-07: Multiline cell inside quotes
    try:
        data = load_fixture("csv_07_multiline.csv")
        res = import_data(data, "csv_07_multiline.csv", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == "Linea 1\nLinea 2"
        collector.record("CSV-07", "5B", "Multiline cell inside quotes with physical row tracking", passed,
                         {"accepted": 1, "ref": "Linea 1\nLinea 2"},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-07", "5B", "Multiline cell inside quotes with physical row tracking", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-08: Whitespace around delimiters
    try:
        data = load_fixture("csv_08_whitespace.csv")
        res = import_data(data, "csv_08_whitespace.csv", map_std)
        passed = (
            res["accepted"] == 1
            and res["records"][0]["id"] == "S1"
            and res["records"][0]["reference"] == "0001"
            and res["records"][0]["attributes"]["weight"]["value"] == "100.5"
        )
        collector.record("CSV-08", "5B", "Whitespace stripped cleanly around delimiters and values", passed,
                         {"accepted": 1, "id": "S1", "ref": "0001"},
                         {"accepted": res["accepted"], "id": res["records"][0]["id"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-08", "5B", "Whitespace stripped cleanly around delimiters and values", False,
                         {"accepted": 1}, {"error": str(e)})

    # CSV-09: Duplicate header
    try:
        data = load_fixture("csv_09_duplicate_header.csv")
        import_data(data, "csv_09_duplicate_header.csv", map_std)
        collector.record("CSV-09", "5B", "Duplicate header aborts file", False,
                         {"error": "ImportErrorDetail"}, {"accepted": 1})
    except ImportErrorDetail as e:
        passed = "aparece 2 veces" in str(e)
        collector.record("CSV-09", "5B", "Duplicate header aborts file", passed,
                         {"error_match": "aparece 2 veces"}, {"message": str(e)})
    except Exception as e:
        collector.record("CSV-09", "5B", "Duplicate header aborts file", False,
                         {"error": "ImportErrorDetail"}, {"error": str(e)})

    # CSV-10: Missing required header
    try:
        data = load_fixture("csv_10_missing_header.csv")
        import_data(data, "csv_10_missing_header.csv", map_std)
        collector.record("CSV-10", "5B", "Missing required header aborts file", False,
                         {"error": "ImportErrorDetail"}, {"accepted": 1})
    except ImportErrorDetail as e:
        passed = "aparece 0 veces" in str(e)
        collector.record("CSV-10", "5B", "Missing required header aborts file", passed,
                         {"error_match": "aparece 0 veces"}, {"message": str(e)})
    except Exception as e:
        collector.record("CSV-10", "5B", "Missing required header aborts file", False,
                         {"error": "ImportErrorDetail"}, {"error": str(e)})

    # CSV-11: Extra column beyond headers
    try:
        data = load_fixture("csv_11_extra_col.csv")
        res = import_data(data, "csv_11_extra_col.csv", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("fuera de las columnas declaradas" in i["message"] for i in res["issues"])
        collector.record("CSV-11", "5B", "Extra column beyond declared headers rejected at row level", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issue": res["issues"][0]["message"] if res["issues"] else ""})
    except Exception as e:
        collector.record("CSV-11", "5B", "Extra column beyond declared headers rejected at row level", False,
                         {"rejected": [2]}, {"error": str(e)})

    # CSV-12: Short row missing required value
    try:
        data = load_fixture("csv_12_short_row.csv")
        res = import_data(data, "csv_12_short_row.csv", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("Falta un valor obligatorio" in i["message"] for i in res["issues"])
        collector.record("CSV-12", "5B", "Short row with missing required value rejected safely", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("CSV-12", "5B", "Short row with missing required value rejected safely", False,
                         {"rejected": [2]}, {"error": str(e)})

    # CSV-13: Argentine number format
    try:
        data = load_fixture("csv_13_arg_number.csv")
        res = import_data(data, "csv_13_arg_number.csv", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["attributes"]["weight"]["value"] == "1234567.89"
        collector.record("CSV-13", "5B", "Argentine number format (1.234.567,89)", passed,
                         {"accepted": 1, "weight": "1234567.89"},
                         {"accepted": res["accepted"], "weight": res["records"][0]["attributes"]["weight"]["value"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-13", "5B", "Argentine number format (1.234.567,89)", False,
                         {"weight": "1234567.89"}, {"error": str(e)})

    # CSV-14: Anglo number format
    try:
        data = load_fixture("csv_14_anglo_number.csv")
        m_anglo = load_mapping("csv_14_anglo")
        res = import_data(data, "csv_14_anglo_number.csv", m_anglo)
        passed = res["accepted"] == 1 and res["records"][0]["attributes"]["weight"]["value"] == "1234567.89"
        collector.record("CSV-14", "5B", "Anglo number format (1,234,567.89)", passed,
                         {"accepted": 1, "weight": "1234567.89"},
                         {"accepted": res["accepted"], "weight": res["records"][0]["attributes"]["weight"]["value"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-14", "5B", "Anglo number format (1,234,567.89)", False,
                         {"weight": "1234567.89"}, {"error": str(e)})

    # CSV-15: Negative amount in charges
    try:
        data = load_fixture("csv_15_negative_amount.csv")
        res = import_data(data, "csv_15_negative_amount.csv", map_charges)
        passed = res["accepted"] == 1 and res["records"][0]["amount"] == "-150"
        collector.record("CSV-15", "5B", "Negative amount (-150,00) in charges", passed,
                         {"accepted": 1, "amount": "-150"},
                         {"accepted": res["accepted"], "amount": res["records"][0]["amount"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-15", "5B", "Negative amount (-150,00) in charges", False,
                         {"amount": "-150"}, {"error": str(e)})

    # CSV-16: Explicit positive amount (+150,00) -> Pre-registered expected: REJECTED because sign regex is "-?"
    try:
        data = load_fixture("csv_16_positive_amount.csv")
        res = import_data(data, "csv_16_positive_amount.csv", map_charges)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("Número inválido" in i["message"] for i in res["issues"])
        collector.record("CSV-16", "5B", "Explicit positive sign (+150,00) safely rejected by strict decimal regex", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issue": res["issues"][0]["message"] if res["issues"] else ""})
    except Exception as e:
        collector.record("CSV-16", "5B", "Explicit positive sign (+150,00) safely rejected by strict decimal regex", False,
                         {"rejected": [2]}, {"error": str(e)})

    # CSV-17: Leading zeros in ID
    try:
        data = load_fixture("csv_17_leading_zeros.csv")
        res = import_data(data, "csv_17_leading_zeros.csv", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == "0000456"
        collector.record("CSV-17", "5B", "Leading zeros preserved without truncation (0000456)", passed,
                         {"accepted": 1, "ref": "0000456"},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-17", "5B", "Leading zeros preserved without truncation (0000456)", False,
                         {"ref": "0000456"}, {"error": str(e)})

    # CSV-18: Extended Unicode / accents
    try:
        data = load_fixture("csv_18_unicode.csv")
        res = import_data(data, "csv_18_unicode.csv", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == "Cañuelas - Güemes"
        collector.record("CSV-18", "5B", "Unicode characters and tildes preserved intact", passed,
                         {"accepted": 1, "ref": "Cañuelas - Güemes"},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("CSV-18", "5B", "Unicode characters and tildes preserved intact", False,
                         {"ref": "Cañuelas - Güemes"}, {"error": str(e)})

    # CSV-19: Non-breaking space \u00a0
    try:
        data = load_fixture("csv_19_nbsp.csv")
        res = import_data(data, "csv_19_nbsp.csv", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("Número inválido" in i["message"] for i in res["issues"])
        collector.record("CSV-19", "5B", "Non-breaking space in number safely rejected without ad-hoc conversion", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("CSV-19", "5B", "Non-breaking space in number safely rejected without ad-hoc conversion", False,
                         {"rejected": [2]}, {"error": str(e)})

    # CSV-20: Truncated CSV inside quotes
    try:
        data = load_fixture("csv_20_truncated.csv")
        import_data(data, "csv_20_truncated.csv", map_std)
        collector.record("CSV-20", "5B", "Truncated CSV inside quotes aborts with ImportErrorDetail", False,
                         {"error": "ImportErrorDetail"}, {"accepted": 1})
    except ImportErrorDetail as e:
        passed = "No se pudo leer el archivo" in str(e)
        collector.record("CSV-20", "5B", "Truncated CSV inside quotes aborts with ImportErrorDetail", passed,
                         {"error_match": "No se pudo leer el archivo"}, {"message": str(e)})
    except Exception as e:
        collector.record("CSV-20", "5B", "Truncated CSV inside quotes aborts with ImportErrorDetail", False,
                         {"error": "ImportErrorDetail"}, {"error": str(e)})


def run_5c_xlsx_tests():
    print("\n--- Running Bloque 5C: XLSX y XML Adversarial (18 Vectores) ---")
    map_std = load_mapping("shipments_std")

    # XLSX-01: Standard numeric
    try:
        data = load_fixture("xlsx_01_standard.xlsx")
        res = import_data(data, "xlsx_01_standard.xlsx", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["attributes"]["weight"]["value"] == "45.67"
        collector.record("XLSX-01", "5C", "Standard numeric cell in XLSX", passed,
                         {"accepted": 1, "weight": "45.67"},
                         {"accepted": res["accepted"], "weight": res["records"][0]["attributes"]["weight"]["value"] if res["records"] else None})
    except Exception as e:
        collector.record("XLSX-01", "5C", "Standard numeric cell in XLSX", False,
                         {"accepted": 1}, {"error": str(e)})

    # XLSX-02: Number stored as text
    try:
        data = load_fixture("xlsx_02_num_as_text.xlsx")
        res = import_data(data, "xlsx_02_num_as_text.xlsx", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == "00123"
        collector.record("XLSX-02", "5C", "Number stored as text in XML (t='s')", passed,
                         {"accepted": 1, "ref": "00123"},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("XLSX-02", "5C", "Number stored as text in XML (t='s')", False,
                         {"accepted": 1}, {"error": str(e)})

    # XLSX-03: XML high-precision literal (1000000000000000.01)
    try:
        data = load_fixture("xlsx_03_high_precision.xlsx")
        res = import_data(data, "xlsx_03_high_precision.xlsx", map_std)
        passed = (
            res["accepted"] == 1
            and res["records"][0]["attributes"]["weight"]["value"] == "1000000000000000.01"
            and res["records"][0]["provenance"]["attributes.weight"]["raw"] == "1000000000000000.01"
        )
        collector.record("XLSX-03", "5C", "High-precision XML token preserves exact decimal without float loss", passed,
                         {"accepted": 1, "weight": "1000000000000000.01"},
                         {"accepted": res["accepted"], "weight": res["records"][0]["attributes"]["weight"]["value"] if res["records"] else None})
    except Exception as e:
        collector.record("XLSX-03", "5C", "High-precision XML token preserves exact decimal without float loss", False,
                         {"accepted": 1}, {"error": str(e)})

    # XLSX-04: Scientific notation
    try:
        data = load_fixture("xlsx_04_scientific.xlsx")
        res = import_data(data, "xlsx_04_scientific.xlsx", map_std)
        passed = (
            res["accepted"] == 1
            and res["records"][0]["attributes"]["weight"]["value"] == "12500"
            and res["records"][0]["provenance"]["attributes.weight"]["raw"] == "1.25E+04"
        )
        collector.record("XLSX-04", "5C", "Scientific notation (1.25E+04 -> 12500) preserved with exact raw", passed,
                         {"accepted": 1, "weight": "12500", "raw": "1.25E+04"},
                         {"accepted": res["accepted"], "weight": res["records"][0]["attributes"]["weight"]["value"] if res["records"] else None,
                          "raw": res["records"][0]["provenance"]["attributes.weight"]["raw"] if res["records"] else None})
    except Exception as e:
        collector.record("XLSX-04", "5C", "Scientific notation (1.25E+04 -> 12500) preserved with exact raw", False,
                         {"accepted": 1}, {"error": str(e)})

    # XLSX-05: Formula with cached value
    try:
        data = load_fixture("xlsx_05_formula_cached.xlsx")
        res = import_data(data, "xlsx_05_formula_cached.xlsx", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("fórmula o un error de Excel" in i["message"] for i in res["issues"])
        collector.record("XLSX-05", "5C", "Formula with cached value rejected safely by unaudited formula policy", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issue": res["issues"][0]["message"] if res["issues"] else ""})
    except Exception as e:
        collector.record("XLSX-05", "5C", "Formula with cached value rejected safely by unaudited formula policy", False,
                         {"rejected": [2]}, {"error": str(e)})

    # XLSX-06: Formula without cached value
    try:
        data = load_fixture("xlsx_06_formula_nocache.xlsx")
        res = import_data(data, "xlsx_06_formula_nocache.xlsx", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("fórmula o un error de Excel" in i["message"] for i in res["issues"])
        collector.record("XLSX-06", "5C", "Formula without cached value rejected safely", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("XLSX-06", "5C", "Formula without cached value rejected safely", False,
                         {"rejected": [2]}, {"error": str(e)})

    # XLSX-07: Error token #DIV/0!
    try:
        data = load_fixture("xlsx_07_error_token.xlsx")
        res = import_data(data, "xlsx_07_error_token.xlsx", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("fórmula o un error de Excel" in i["message"] for i in res["issues"])
        collector.record("XLSX-07", "5C", "Excel native error token (#DIV/0!) rejected safely", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("XLSX-07", "5C", "Excel native error token (#DIV/0!) rejected safely", False,
                         {"rejected": [2]}, {"error": str(e)})

    # XLSX-08: Serial date
    try:
        data = load_fixture("xlsx_08_serial_date.xlsx")
        res = import_data(data, "xlsx_08_serial_date.xlsx", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["attributes"]["service_date"]["value"] == "2025-12-09"
        collector.record("XLSX-08", "5C", "Excel serial date parsed to exact ISO YYYY-MM-DD", passed,
                         {"accepted": 1, "date": "2025-12-09"},
                         {"accepted": res["accepted"], "date": res["records"][0]["attributes"]["service_date"]["value"] if res["records"] else None})
    except Exception as e:
        collector.record("XLSX-08", "5C", "Excel serial date parsed to exact ISO YYYY-MM-DD", False,
                         {"date": "2025-12-09"}, {"error": str(e)})

    # XLSX-09: Multisheet without sheet configured
    try:
        data = load_fixture("xlsx_09_multisheet.xlsx")
        import_data(data, "xlsx_09_multisheet.xlsx", map_std)
        collector.record("XLSX-09", "5C", "Multisheet workbook without sheet selection aborts file", False,
                         {"error": "ImportErrorDetail"}, {"accepted": 1})
    except ImportErrorDetail as e:
        passed = "varias hojas" in str(e)
        collector.record("XLSX-09", "5C", "Multisheet workbook without sheet selection aborts file", passed,
                         {"error_match": "varias hojas"}, {"message": str(e)})
    except Exception as e:
        collector.record("XLSX-09", "5C", "Multisheet workbook without sheet selection aborts file", False,
                         {"error": "ImportErrorDetail"}, {"error": str(e)})

    # XLSX-10: Nonexistent sheet requested
    try:
        data = load_fixture("xlsx_01_standard.xlsx")
        m_badsheet = load_mapping("xlsx_10_bad_sheet")
        import_data(data, "xlsx_01_standard.xlsx", m_badsheet)
        collector.record("XLSX-10", "5C", "Nonexistent sheet requested aborts file", False,
                         {"error": "ImportErrorDetail"}, {"accepted": 1})
    except ImportErrorDetail as e:
        passed = "No existe la hoja 'Facturacion'" in str(e)
        collector.record("XLSX-10", "5C", "Nonexistent sheet requested aborts file", passed,
                         {"error_match": "No existe la hoja 'Facturacion'"}, {"message": str(e)})
    except Exception as e:
        collector.record("XLSX-10", "5C", "Nonexistent sheet requested aborts file", False,
                         {"error": "ImportErrorDetail"}, {"error": str(e)})

    # XLSX-11: Hidden row
    try:
        data = load_fixture("xlsx_11_hidden_row.xlsx")
        res = import_data(data, "xlsx_11_hidden_row.xlsx", map_std)
        passed = res["accepted"] == 1 and res["records"][0]["attributes"]["weight"]["value"] == "80"
        collector.record("XLSX-11", "5C", "Hidden row read faithfully without coordinate corruption", passed,
                         {"accepted": 1, "weight": "80"},
                         {"accepted": res["accepted"], "weight": res["records"][0]["attributes"]["weight"]["value"] if res["records"] else None})
    except Exception as e:
        collector.record("XLSX-11", "5C", "Hidden row read faithfully without coordinate corruption", False,
                         {"accepted": 1}, {"error": str(e)})

    # XLSX-12: Merged cells
    try:
        data = load_fixture("xlsx_12_merged_cells.xlsx")
        res = import_data(data, "xlsx_12_merged_cells.xlsx", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("Falta un valor obligatorio" in i["message"] for i in res["issues"])
        collector.record("XLSX-12", "5C", "Merged cell secondary empty target rejected safely", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issue": res["issues"][0]["message"] if res["issues"] else ""})
    except Exception as e:
        collector.record("XLSX-12", "5C", "Merged cell secondary empty target rejected safely", False,
                         {"rejected": [2]}, {"error": str(e)})

    # XLSX-13: Sparse rows
    try:
        data = load_fixture("xlsx_13_sparse_rows.xlsx")
        res = import_data(data, "xlsx_13_sparse_rows.xlsx", map_std)
        passed = (
            res["accepted"] == 2
            and res["records"][0]["provenance"]["id"]["row"] == 2
            and res["records"][1]["provenance"]["id"]["row"] == 4
        )
        collector.record("XLSX-13", "5C", "Sparse rows preserve exact physical coordinates (row 2 and row 4)", passed,
                         {"accepted": 2, "rows": [2, 4]},
                         {"accepted": res["accepted"], "rows": [r["provenance"]["id"]["row"] for r in res["records"]]})
    except Exception as e:
        collector.record("XLSX-13", "5C", "Sparse rows preserve exact physical coordinates (row 2 and row 4)", False,
                         {"accepted": 2}, {"error": str(e)})

    # XLSX-14: Block of empty rows
    try:
        data = load_fixture("xlsx_14_empty_block.xlsx")
        res = import_data(data, "xlsx_14_empty_block.xlsx", map_std)
        passed = (
            res["accepted"] == 2
            and res["records"][0]["provenance"]["id"]["row"] == 2
            and res["records"][1]["provenance"]["id"]["row"] == 8
        )
        collector.record("XLSX-14", "5C", "Empty row block skipped without shifting physical row coordinate (row 8)", passed,
                         {"accepted": 2, "rows": [2, 8]},
                         {"accepted": res["accepted"], "rows": [r["provenance"]["id"]["row"] for r in res["records"]]})
    except Exception as e:
        collector.record("XLSX-14", "5C", "Empty row block skipped without shifting physical row coordinate (row 8)", False,
                         {"accepted": 2}, {"error": str(e)})

    # XLSX-15: Extra values outside header range
    try:
        data = load_fixture("xlsx_15_extra_col.xlsx")
        res = import_data(data, "xlsx_15_extra_col.xlsx", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("fuera de las columnas declaradas" in i["message"] for i in res["issues"])
        collector.record("XLSX-15", "5C", "Values outside header range rejected at row level", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("XLSX-15", "5C", "Values outside header range rejected at row level", False,
                         {"rejected": [2]}, {"error": str(e)})

    # XLSX-16: Corrupt ZIP/XLSX
    try:
        data = load_fixture("xlsx_16_corrupt.xlsx")
        import_data(data, "xlsx_16_corrupt.xlsx", map_std)
        collector.record("XLSX-16", "5C", "Corrupt XLSX file aborts cleanly with ImportErrorDetail", False,
                         {"error": "ImportErrorDetail"}, {"accepted": 1})
    except ImportErrorDetail as e:
        passed = "No se pudo leer el archivo" in str(e)
        collector.record("XLSX-16", "5C", "Corrupt XLSX file aborts cleanly with ImportErrorDetail", passed,
                         {"error_match": "No se pudo leer el archivo"}, {"message": str(e)})
    except Exception as e:
        collector.record("XLSX-16", "5C", "Corrupt XLSX file aborts cleanly with ImportErrorDetail", False,
                         {"error": "ImportErrorDetail"}, {"error": str(e)})

    # XLSX-17: Numeric ID with reject policy
    try:
        data = load_fixture("xlsx_17_num_id_reject.xlsx")
        res = import_data(data, "xlsx_17_num_id_reject.xlsx", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("perdido ceros iniciales" in i["message"] for i in res["issues"])
        collector.record("XLSX-17", "5C", "Numeric ID with numeric_text='reject' safely warns of leading zero risk", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issue": res["issues"][0]["message"] if res["issues"] else ""})
    except Exception as e:
        collector.record("XLSX-17", "5C", "Numeric ID with numeric_text='reject' safely warns of leading zero risk", False,
                         {"rejected": [2]}, {"error": str(e)})

    # XLSX-18: Numeric ID with formatted policy
    try:
        data = load_fixture("xlsx_18_num_id_formatted.xlsx")
        m_fmt = load_mapping("xlsx_18_formatted")
        res = import_data(data, "xlsx_18_num_id_formatted.xlsx", m_fmt)
        passed = res["accepted"] == 1 and res["records"][0]["reference"] == "000123"
        collector.record("XLSX-18", "5C", "Numeric ID with numeric_text='formatted' and '000000' format gives exact '000123'", passed,
                         {"accepted": 1, "ref": "000123"},
                         {"accepted": res["accepted"], "ref": res["records"][0]["reference"] if res["records"] else None})
    except Exception as e:
        collector.record("XLSX-18", "5C", "Numeric ID with numeric_text='formatted' and '000000' format gives exact '000123'", False,
                         {"ref": "000123"}, {"error": str(e)})


def run_5d_provenance_tests():
    print("\n--- Running Bloque 5D: Identidad y Provenance Celda a Celda (6 Casos) ---")
    map_std = load_mapping("shipments_std")

    # PROV-01: Full SourceRef verification
    try:
        data = load_fixture("prov_01_standard.csv")
        res = import_data(data, "prov_01_standard.csv", map_std)
        rec = res["records"][0]
        prov = rec["provenance"]["attributes.weight"]
        expected_hash = bytes_hash(data)
        passed = (
            prov["document"] == expected_hash
            and prov["filename"] == "prov_01_standard.csv"
            and prov["sheet"] == "CSV"
            and prov["row"] == 2
            and prov["column"] == "weight"
            and prov["raw"] == "100,5"
            and prov["transform"] == "map_shipments_std@1:decimal"
        )
        collector.record("PROV-01", "5D", "Exhaustive SourceRef contract verification across all 7 fields", passed,
                         {"doc": expected_hash, "row": 2, "col": "weight", "raw": "100,5"},
                         {"doc": prov["document"], "row": prov["row"], "col": prov["column"], "raw": prov["raw"]})
    except Exception as e:
        collector.record("PROV-01", "5D", "Exhaustive SourceRef contract verification across all 7 fields", False,
                         {}, {"error": str(e)})

    # PROV-02: Renamed file
    try:
        data_orig = load_fixture("prov_01_standard.csv")
        data_renamed = load_fixture("factura_revisada_2026.csv")
        res1 = import_data(data_orig, "prov_01_standard.csv", map_std)
        res2 = import_data(data_renamed, "factura_revisada_2026.csv", map_std)
        rec1 = res1["records"][0].copy()
        rec2 = res2["records"][0].copy()
        prov1 = rec1.pop("provenance")
        prov2 = rec2.pop("provenance")
        passed = (
            rec1 == rec2
            and prov2["attributes.weight"]["filename"] == "factura_revisada_2026.csv"
            and prov1["attributes.weight"]["filename"] == "prov_01_standard.csv"
        )
        collector.record("PROV-02", "5D", "Filename rename changes provenance metadata without altering economics", passed,
                         {"records_equal": True, "renamed_fn": "factura_revisada_2026.csv"},
                         {"records_equal": rec1 == rec2, "observed_fn": prov2["attributes.weight"]["filename"]})
    except Exception as e:
        collector.record("PROV-02", "5D", "Filename rename changes provenance metadata without altering economics", False,
                         {}, {"error": str(e)})

    # PROV-03: Vertical cell offset
    try:
        data = load_fixture("prov_03_vertical_shift.csv")
        m_hdr4 = load_mapping("prov_03_header4")
        res = import_data(data, "prov_03_vertical_shift.csv", m_hdr4)
        rec = res["records"][0]
        prov = rec["provenance"]["attributes.weight"]
        passed = res["accepted"] == 1 and prov["row"] == 5
        collector.record("PROV-03", "5D", "Vertical shift of 3 blank rows updates provenance row to 5", passed,
                         {"accepted": 1, "row": 5},
                         {"accepted": res["accepted"], "row": prov["row"]})
    except Exception as e:
        collector.record("PROV-03", "5D", "Vertical shift of 3 blank rows updates provenance row to 5", False,
                         {"row": 5}, {"error": str(e)})

    # PROV-04: Horizontal column shift
    try:
        data = load_fixture("prov_04_horizontal_shift.csv")
        res = import_data(data, "prov_04_horizontal_shift.csv", map_std)
        rec = res["records"][0]
        passed = (
            res["accepted"] == 1
            and rec["provenance"]["attributes.weight"]["column"] == "weight"
            and rec["provenance"]["id"]["column"] == "id"
            and rec["attributes"]["weight"]["value"] == "100.5"
        )
        collector.record("PROV-04", "5D", "Horizontal column reordering updates provenance column accurately", passed,
                         {"accepted": 1, "weight_col": "weight", "id_col": "id"},
                         {"accepted": res["accepted"],
                          "weight_col": rec["provenance"]["attributes.weight"]["column"],
                          "id_col": rec["provenance"]["id"]["column"]})
    except Exception as e:
        collector.record("PROV-04", "5D", "Horizontal column reordering updates provenance column accurately", False,
                         {}, {"error": str(e)})

    # PROV-05: Dynamic attributes provenance
    try:
        data = load_fixture("prov_05_attributes.csv")
        m_attrs = load_mapping("prov_05_attrs")
        res = import_data(data, "prov_05_attributes.csv", m_attrs)
        rec = res["records"][0]
        prov_w = rec["provenance"]["attributes.weight"]
        prov_v = rec["provenance"]["attributes.volume"]
        passed = (
            res["accepted"] == 1
            and prov_w["raw"] == "100,5"
            and prov_w["column"] == "weight"
            and prov_v["raw"] == "2,5"
            and prov_v["column"] == "vol"
        )
        collector.record("PROV-05", "5D", "Dynamic attributes preserve individual provenance without collision", passed,
                         {"weight_raw": "100,5", "vol_raw": "2,5"},
                         {"weight_raw": prov_w["raw"], "vol_raw": prov_v["raw"]})
    except Exception as e:
        collector.record("PROV-05", "5D", "Dynamic attributes preserve individual provenance without collision", False,
                         {}, {"error": str(e)})

    # PROV-06: Constant mapping provenance
    try:
        data = load_fixture("prov_06_constant.csv")
        res = import_data(data, "prov_06_constant.csv", map_std)
        rec = res["records"][0]
        prov_carrier = rec["provenance"]["carrier"]
        passed = (
            res["accepted"] == 1
            and prov_carrier["column"] == "(constante del mapping)"
            and prov_carrier["raw"] == "CAMIONERA_CENTRAL"
            and prov_carrier["row"] == 2
        )
        collector.record("PROV-06", "5D", "Constant mapping records explicit (constante del mapping) in provenance", passed,
                         {"column": "(constante del mapping)", "raw": "CAMIONERA_CENTRAL"},
                         {"column": prov_carrier["column"], "raw": prov_carrier["raw"]})
    except Exception as e:
        collector.record("PROV-06", "5D", "Constant mapping records explicit (constante del mapping) in provenance", False,
                         {}, {"error": str(e)})


def run_5e_safe_rejection_tests():
    print("\n--- Running Bloque 5E: Política de Rechazo Seguro (10 Casos) ---")
    map_std = load_mapping("shipments_std")
    map_charges = load_mapping("charges_std")

    # REJ-01: Ambiguous number (1.23 with dot thousands and comma decimal)
    try:
        data = load_fixture("rej_01_bad_separator.csv")
        res = import_data(data, "rej_01_bad_separator.csv", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("Número inválido" in i["message"] for i in res["issues"])
        collector.record("REJ-01", "5E", "Ambiguous number format (1.23 when expecting thousands dot) safely rejected", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("REJ-01", "5E", "Ambiguous number format (1.23 when expecting thousands dot) safely rejected", False,
                         {"rejected": [2]}, {"error": str(e)})

    # REJ-02: Ambiguous date (05/06/2026 with DMY and MDY)
    try:
        data = load_fixture("rej_02_ambiguous_date.csv")
        m_ambig = load_mapping("rej_02_ambiguous_date")
        res = import_data(data, "rej_02_ambiguous_date.csv", m_ambig)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("ambigua" in i["message"] for i in res["issues"])
        collector.record("REJ-02", "5E", "Ambiguous date (05/06/2026 matching multiple formats) rejected safely", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issue": res["issues"][0]["message"] if res["issues"] else ""})
    except Exception as e:
        collector.record("REJ-02", "5E", "Ambiguous date (05/06/2026 matching multiple formats) rejected safely", False,
                         {"rejected": [2]}, {"error": str(e)})

    # REJ-03: Date with non-zero time component
    try:
        data = load_fixture("rej_03_date_with_time.xlsx")
        res = import_data(data, "rej_03_date_with_time.xlsx", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("hora o zona horaria" in i["message"] for i in res["issues"])
        collector.record("REJ-03", "5E", "Date with non-zero time component rejected without silent truncation", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issue": res["issues"][0]["message"] if res["issues"] else ""})
    except Exception as e:
        collector.record("REJ-03", "5E", "Date with non-zero time component rejected without silent truncation", False,
                         {"rejected": [2]}, {"error": str(e)})

    # REJ-04: Duplicate business ID in same batch
    try:
        data = load_fixture("rej_04_duplicate_id.csv")
        res = import_data(data, "rej_04_duplicate_id.csv", map_std)
        passed = res["accepted"] == 1 and res["rejected"] == [3] and any("repetido" in i["message"] for i in res["issues"])
        collector.record("REJ-04", "5E", "Duplicate business ID in same batch rejects duplicate row without overwrite", passed,
                         {"accepted": 1, "rejected": [3]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("REJ-04", "5E", "Duplicate business ID in same batch rejects duplicate row without overwrite", False,
                         {"rejected": [3]}, {"error": str(e)})

    # REJ-05: Ambiguous boolean
    try:
        data = load_fixture("rej_05_ambiguous_boolean.csv")
        m_bool = load_mapping("rej_05_boolean")
        res = import_data(data, "rej_05_ambiguous_boolean.csv", m_bool)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("booleano único" in i["message"] for i in res["issues"])
        collector.record("REJ-05", "5E", "Ambiguous boolean ('quizas') rejected without default fallback", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("REJ-05", "5E", "Ambiguous boolean ('quizas') rejected without default fallback", False,
                         {"rejected": [2]}, {"error": str(e)})

    # REJ-06: Missing mandatory amount in charge
    try:
        data = load_fixture("rej_06_missing_amount.csv")
        res = import_data(data, "rej_06_missing_amount.csv", map_charges)
        passed = res["accepted"] == 0 and res["rejected"] == [2] and any("Falta un valor obligatorio" in i["message"] for i in res["issues"])
        collector.record("REJ-06", "5E", "Missing mandatory amount rejected safely (never silently assumed 0)", passed,
                         {"accepted": 0, "rejected": [2]},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("REJ-06", "5E", "Missing mandatory amount rejected safely (never silently assumed 0)", False,
                         {"rejected": [2]}, {"error": str(e)})

    # REJ-07: Unmapped concept in charges
    try:
        data = load_fixture("rej_07_unmapped_concept.csv")
        res = import_data(data, "rej_07_unmapped_concept.csv", map_charges)
        rec = res["records"][0] if res["records"] else {}
        warn = res["issues"][0] if res["issues"] else {}
        passed = (
            res["accepted"] == 1
            and rec.get("concept") == "external:CONCEPTO_DESCONOCIDO"
            and warn.get("category") == "warning"
            and "sin equivalencia" in warn.get("message", "")
        )
        collector.record("REJ-07", "5E", "Unmapped concept classified as external with audit warning", passed,
                         {"accepted": 1, "concept": "external:CONCEPTO_DESCONOCIDO", "warning": True},
                         {"accepted": res["accepted"], "concept": rec.get("concept"), "warning": warn.get("category")})
    except Exception as e:
        collector.record("REJ-07", "5E", "Unmapped concept classified as external with audit warning", False,
                         {}, {"error": str(e)})

    # REJ-08: Zero byte file
    try:
        data = load_fixture("rej_08_empty_file.csv")
        import_data(data, "rej_08_empty_file.csv", map_std)
        collector.record("REJ-08", "5E", "Zero byte file aborts with ImportErrorDetail", False,
                         {"error": "ImportErrorDetail"}, {"accepted": 0})
    except ImportErrorDetail as e:
        passed = "No existe la fila de encabezados seleccionada" in str(e)
        collector.record("REJ-08", "5E", "Zero byte file aborts with ImportErrorDetail", passed,
                         {"error_match": "No existe la fila de encabezados"}, {"message": str(e)})
    except Exception as e:
        collector.record("REJ-08", "5E", "Zero byte file aborts with ImportErrorDetail", False,
                         {"error": "ImportErrorDetail"}, {"error": str(e)})

    # REJ-09: Headers only
    try:
        data = load_fixture("rej_09_headers_only.csv")
        res = import_data(data, "rej_09_headers_only.csv", map_std)
        passed = res["accepted"] == 0 and res["rejected"] == [] and res["issues"] == []
        collector.record("REJ-09", "5E", "Headers-only file yields 0 records and 0 rejects consistently without crashing", passed,
                         {"accepted": 0, "rejected": [], "issues": []},
                         {"accepted": res["accepted"], "rejected": res["rejected"], "issues": res["issues"]})
    except Exception as e:
        collector.record("REJ-09", "5E", "Headers-only file yields 0 records and 0 rejects consistently without crashing", False,
                         {"accepted": 0}, {"error": str(e)})

    # REJ-10: Blank line between data rows
    try:
        data = load_fixture("rej_10_blank_line.csv")
        res = import_data(data, "rej_10_blank_line.csv", map_std)
        passed = res["accepted"] == 2 and res["rejected"] == []
        collector.record("REJ-10", "5E", "Completely blank row between data rows safely skipped without corruption", passed,
                         {"accepted": 2, "rejected": []},
                         {"accepted": res["accepted"], "rejected": res["rejected"]})
    except Exception as e:
        collector.record("REJ-10", "5E", "Completely blank row between data rows safely skipped without corruption", False,
                         {"accepted": 2}, {"error": str(e)})


def run_5f_metamorphic_tests():
    print("\n--- Running Bloque 5F: Corpus Metamórfico y Diferencial (8 Casos) ---")
    map_std = load_mapping("shipments_std")
    map_charges = load_mapping("charges_std")

    # MET-01: CSV vs XLSX equivalence
    try:
        data_csv = load_fixture("met_01_data.csv")
        data_xlsx = load_fixture("met_01_data.xlsx")
        res_csv = import_data(data_csv, "met_01_data.csv", map_std)
        res_xlsx = import_data(data_xlsx, "met_01_data.xlsx", map_std)
        # Compare economic contents (all fields and attributes without provenance)
        recs_csv_econ = []
        for r in res_csv["records"]:
            c = json.loads(json.dumps(r))
            c.pop("provenance")
            recs_csv_econ.append(c)
        recs_xlsx_econ = []
        for r in res_xlsx["records"]:
            c = json.loads(json.dumps(r))
            c.pop("provenance")
            recs_xlsx_econ.append(c)
        economic_equal = (recs_csv_econ == recs_xlsx_econ)
        passed = (
            res_csv["accepted"] == 3
            and res_xlsx["accepted"] == 3
            and economic_equal
        )
        collector.record("MET-01", "5F", "Format Invariance: CSV vs XLSX economic equivalence across all fields", passed,
                         {"accepted": 3, "economic_equal": True},
                         {"csv_acc": res_csv["accepted"], "xlsx_acc": res_xlsx["accepted"], "economic_equal": economic_equal})
    except Exception as e:
        collector.record("MET-01", "5F", "Format Invariance: CSV vs XLSX semantic equivalence across all fields", False,
                         {}, {"error": str(e)})

    # MET-02: Separator equivalence (Argentine vs Anglo)
    try:
        data_arg = load_fixture("met_02_arg.csv")
        data_anglo = load_fixture("met_02_anglo.csv")
        m_anglo = load_mapping("met_02_anglo_map")
        res_arg = import_data(data_arg, "met_02_arg.csv", map_std)
        res_anglo = import_data(data_anglo, "met_02_anglo.csv", m_anglo)
        val_arg = res_arg["records"][0]["attributes"]["weight"]["value"]
        val_anglo = res_anglo["records"][0]["attributes"]["weight"]["value"]
        passed = val_arg == "1250.75" and val_anglo == "1250.75"
        collector.record("MET-02", "5F", "Separator Invariance: Argentine 1.250,75 == Anglo 1,250.75 -> 1250.75", passed,
                         {"val_arg": "1250.75", "val_anglo": "1250.75"},
                         {"val_arg": val_arg, "val_anglo": val_anglo})
    except Exception as e:
        collector.record("MET-02", "5F", "Separator Invariance: Argentine 1.250,75 == Anglo 1,250.75 -> 1250.75", False,
                         {}, {"error": str(e)})

    # MET-03: Column permutation invariance
    try:
        data_a = load_fixture("met_03_perm_a.csv")
        data_b = load_fixture("met_03_perm_b.csv")
        res_a = import_data(data_a, "met_03_perm_a.csv", map_std)
        res_b = import_data(data_b, "met_03_perm_b.csv", map_std)
        rec_a = res_a["records"][0].copy()
        rec_b = res_b["records"][0].copy()
        rec_a.pop("provenance")
        rec_b.pop("provenance")
        passed = rec_a == rec_b
        collector.record("MET-03", "5F", "Column Permutation Invariance: Reordering physical columns produces identical records", passed,
                         {"records_identical": True},
                         {"records_identical": passed})
    except Exception as e:
        collector.record("MET-03", "5F", "Column Permutation Invariance: Reordering physical columns produces identical records", False,
                         {}, {"error": str(e)})

    # MET-04: Row permutation invariance on multiset aggregation
    try:
        data_a = load_fixture("met_04_order_a.csv")
        data_b = load_fixture("met_04_order_b.csv")
        res_a = import_data(data_a, "met_04_order_a.csv", map_std)
        res_b = import_data(data_b, "met_04_order_b.csv", map_std)
        ids_a = sorted(r["id"] for r in res_a["records"])
        ids_b = sorted(r["id"] for r in res_b["records"])
        sum_a = sum(Decimal(r["attributes"]["weight"]["value"]) for r in res_a["records"])
        sum_b = sum(Decimal(r["attributes"]["weight"]["value"]) for r in res_b["records"])
        passed = ids_a == ids_b and sum_a == sum_b
        collector.record("MET-04", "5F", "Row Permutation Invariance: Batch multiset and aggregated sum are identical", passed,
                         {"ids_equal": True, "sum_equal": True},
                         {"ids_equal": ids_a == ids_b, "sum_equal": sum_a == sum_b})
    except Exception as e:
        collector.record("MET-04", "5F", "Row Permutation Invariance: Batch multiset and aggregated sum are identical", False,
                         {}, {"error": str(e)})

    # MET-05: Whitespace invariance
    try:
        data_c = load_fixture("met_05_compact.csv")
        data_s = load_fixture("met_05_spaced.csv")
        res_c = import_data(data_c, "met_05_compact.csv", map_std)
        res_s = import_data(data_s, "met_05_spaced.csv", map_std)
        rec_c = res_c["records"][0].copy()
        rec_s = res_s["records"][0].copy()
        rec_c.pop("provenance")
        rec_s.pop("provenance")
        passed = rec_c == rec_s
        collector.record("MET-05", "5F", "Whitespace Invariance: Spaces around delimiters stripped identically", passed,
                         {"records_identical": True},
                         {"records_identical": passed})
    except Exception as e:
        collector.record("MET-05", "5F", "Whitespace Invariance: Spaces around delimiters stripped identically", False,
                         {}, {"error": str(e)})

    # MET-06: 1 Cent difference sensitivity
    try:
        data_a = load_fixture("met_06_amt_a.csv")
        data_b = load_fixture("met_06_amt_b.csv")
        res_a = import_data(data_a, "met_06_amt_a.csv", map_charges)
        res_b = import_data(data_b, "met_06_amt_b.csv", map_charges)
        amt_a = res_a["records"][0]["amount"]
        amt_b = res_b["records"][0]["amount"]
        hash_a = bytes_hash(json.dumps(res_a["records"][0], sort_keys=True).encode())
        hash_b = bytes_hash(json.dumps(res_b["records"][0], sort_keys=True).encode())
        passed = amt_a == "1250.75" and amt_b == "1250.76" and hash_a != hash_b
        collector.record("MET-06", "5F", "Material Sensitivity: 1 cent difference (1250.75 vs 1250.76) strictly distinguishes records", passed,
                         {"amt_diff": True, "hash_diff": True},
                         {"amt_a": amt_a, "amt_b": amt_b, "hash_diff": hash_a != hash_b})
    except Exception as e:
        collector.record("MET-06", "5F", "Material Sensitivity: 1 cent difference (1250.75 vs 1250.76) strictly distinguishes records", False,
                         {}, {"error": str(e)})

    # MET-07: Boundary date sensitivity
    try:
        data_a = load_fixture("met_07_date_a.csv")
        data_b = load_fixture("met_07_date_b.csv")
        res_a = import_data(data_a, "met_07_date_a.csv", map_std)
        res_b = import_data(data_b, "met_07_date_b.csv", map_std)
        date_a = res_a["records"][0]["attributes"]["service_date"]["value"]
        date_b = res_b["records"][0]["attributes"]["service_date"]["value"]
        passed = date_a == "2026-06-30" and date_b == "2026-07-01" and date_a != date_b
        collector.record("MET-07", "5F", "Date Boundary Sensitivity: 2026-06-30 vs 2026-07-01 preserves exact distinct contractual dates", passed,
                         {"date_a": "2026-06-30", "date_b": "2026-07-01"},
                         {"date_a": date_a, "date_b": date_b})
    except Exception as e:
        collector.record("MET-07", "5F", "Date Boundary Sensitivity: 2026-06-30 vs 2026-07-01 preserves exact distinct contractual dates", False,
                         {}, {"error": str(e)})

    # MET-08: Identifier sensitivity
    try:
        data_a = load_fixture("met_08_id_a.csv")
        data_b = load_fixture("met_08_id_b.csv")
        res_a = import_data(data_a, "met_08_id_a.csv", map_std)
        res_b = import_data(data_b, "met_08_id_b.csv", map_std)
        id_a = res_a["records"][0]["id"]
        id_b = res_b["records"][0]["id"]
        passed = id_a == "S-100" and id_b == "S-101" and id_a != id_b
        collector.record("MET-08", "5F", "Identifier Sensitivity: S-100 vs S-101 never collides or truncates", passed,
                         {"id_a": "S-100", "id_b": "S-101"},
                         {"id_a": id_a, "id_b": id_b})
    except Exception as e:
        collector.record("MET-08", "5F", "Identifier Sensitivity: S-100 vs S-101 never collides or truncates", False,
                         {}, {"error": str(e)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    destination = args.output_dir or OBSERVED_DIR / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    destination.mkdir(parents=True, exist_ok=False)
    collector.results.clear()
    fingerprint = source_digest(ROOT)
    product_hash = engine_artifact_hash()
    print("=======================================================================")
    print("  FASE 5 — Importación Adversarial y Fidelidad Documental  ")
    print("=======================================================================")
    print(f"Source fingerprint: {fingerprint}")
    print(f"Freight Audit package: {freight_audit.__file__}")
    print(f"Product artifact hash: {product_hash}")

    run_5b_csv_tests()
    run_5c_xlsx_tests()
    run_5d_provenance_tests()
    run_5e_safe_rejection_tests()
    run_5f_metamorphic_tests()

    total = len(collector.results)
    passed_count = sum(1 for r in collector.results if r["passed"])
    failed_count = total - passed_count
    accepted = (
        import_cases_passed(collector.results)
        and fingerprint == source_digest(ROOT)
        and product_hash == engine_artifact_hash()
    )

    print("\n=======================================================================")
    print(f"  RESUMEN EJECUCIÓN FASE 5: {passed_count}/{total} PASSED ({failed_count} FAILED)")
    print("=======================================================================")

    out_file = destination / "adversarial_import_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "source_digest": fingerprint,
                "product_path": freight_audit.__file__,
                "artifact_hash": product_hash,
                "gate_passed": accepted,
                "total_cases": total,
                "passed": passed_count,
                "failed": failed_count,
                "results": collector.results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"Results saved to: {out_file}")

    if not accepted:
        print("\nImport gate failed: require all 62 distinct cases passed and unchanged tested code.")
        return 2
    print("\nAll 62 preregistered import cases passed; results apply to the recorded product artifact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
