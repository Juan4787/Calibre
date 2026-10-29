"""Cotejo de registros conservados contra sus originales y mappings congelados.

This guards the caller-to-storage boundary. It reuses the bounded tabular reader;
handwritten/independent regression oracles test conversions separately. A repeated
import is not claimed to be an independent implementation of the import semantics.
"""

from collections.abc import Callable

from .canonical import digest
from .importing import ImportMapping, import_data
from .models import Dataset


def check_provenance(dataset: Dataset, source: Callable[[str], bytes]) -> dict:
    configurations: dict[tuple[str, str, str], ImportMapping] = {}
    for payload in dataset.mappings:
        mapping = ImportMapping.model_validate(payload)
        key = (mapping.entity, mapping.id, mapping.version)
        if key in configurations and configurations[key] != mapping:
            raise ValueError(
                "La procedencia contiene dos formatos distintos con la misma versión; corregir el origen."
            )
        configurations[key] = mapping
    cache: dict[tuple, dict] = {}
    checked = declared = 0
    for role in ("shipments", "charges"):
        available = [m for key, m in configurations.items() if key[0] == role]
        for record in getattr(dataset, role):
            if not record.provenance or not available:
                declared += 1
                continue
            matches = [
                m
                for m in available
                if all(ref.transform.startswith(f"{m.id}@{m.version}:") for ref in record.provenance.values())
            ]
            documents = {ref.document for ref in record.provenance.values()}
            if len(matches) != 1 or len(documents) != 1:
                raise ValueError(
                    "La procedencia no identifica un original y formato únicos; revisar el origen del registro."
                )
            mapping = matches[0]
            document = next(iter(documents))
            filename = next(iter(record.provenance.values())).filename
            citation_key = (role, document, digest(mapping), filename)
            if citation_key not in cache:
                imported = import_data(source(document), filename, mapping)
                cache[citation_key] = {item["id"]: item for item in imported["records"]}
            expected = cache[citation_key].get(record.id)
            if expected is None:
                raise ValueError(
                    "Un registro no existe en el original indicado por su procedencia; revisar el origen."
                )
            actual = record.model_dump(mode="json")
            # Declared enrichment may add attributes, but cannot replace imported fields
            # or delete their citations. Every imported value/citation is compared.
            if (
                actual["provenance"] != expected["provenance"]
                or any(
                    actual.get(field) != value
                    for field, value in expected.items()
                    if field not in {"attributes", "provenance"}
                )
                or any(
                    actual["attributes"].get(field) != value
                    for field, value in expected["attributes"].items()
                )
            ):
                raise ValueError(
                    "Los datos o su procedencia no coinciden con el original y formato conservados; corregir el origen."
                )
            if actual["attributes"].keys() == expected["attributes"].keys():
                checked += 1
            else:
                declared += 1  # Enrichment is preserved, but the whole record is not fully corroborated.
    return {
        "checked_records": checked,
        "declared_records": declared,
        "method": "originals-and-frozen-mappings/v1",
        "scope": "Cotejo contra originales; usa el lector tabular del programa. No certifica contrato, autenticidad ni completitud documental.",
    }
