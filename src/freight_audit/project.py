from pathlib import Path

from .canonical import load_json
from .importing import ImportMapping, import_data
from .models import Agreement, Dataset
from .storage import Store


def load_project(path: Path, store: Store) -> tuple[Dataset, dict]:
    project = load_json(path.read_bytes())
    root = path.parent
    records = {}
    mappings = []
    documents = {}
    issues = []
    imports = {}
    for role in ("shipments", "charges"):
        config = project[role]
        mapping = ImportMapping.model_validate(load_json((root / config["mapping"]).read_bytes()))
        if mapping.entity != role:
            raise ValueError(f"El mapping no corresponde a {role}.")
        data = (root / config["file"]).read_bytes()
        imported = import_data(data, Path(config["file"]).name, mapping)
        source_hash = store.put_source(data)
        documents[source_hash] = Path(config["file"]).name
        records[role] = imported["records"]
        mappings.append(mapping.model_dump(mode="json"))
        issues.extend(imported["issues"])
        imports[role] = {"accepted": imported["accepted"], "rejected": imported["rejected"]}
        store.save_config("mapping", f"{mapping.id}@{mapping.version}", mapping.model_dump(mode="json"))
    agreements = [
        Agreement.model_validate(value) for value in load_json((root / project["agreements"]).read_bytes())
    ]
    for agreement in agreements:
        store.save_config("agreement", agreement.name, agreement.model_dump(mode="json"))
    evidence = load_json((root / project["evidence"]).read_bytes()) if project.get("evidence") else []
    for attachment in project.get("attachments", []):
        data = (root / attachment["file"]).read_bytes()
        source_hash = store.put_source(data)
        documents[source_hash] = Path(attachment["file"]).name
        found = [item for item in evidence if item["id"] == attachment["evidence_id"]]
        if len(found) != 1:
            raise ValueError("Un adjunto no tiene una referencia de evidencia única.")
        found[0]["document_hash"] = source_hash
    return Dataset(
        label=project["label"],
        shipments=records["shipments"],
        charges=records["charges"],
        agreements=agreements,
        evidence=evidence,
        issues=issues,
        mappings=mappings,
        documents=documents,
        coverage=project.get("coverage", {}),
    ), imports
