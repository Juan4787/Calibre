from pathlib import Path

from .canonical import load_json
from .importing import MAX_FILE_BYTES, ImportMapping, import_data
from .local_paths import read_bounded
from .models import Agreement, ContractSource, Dataset
from .storage import Store


def load_project(path: Path, store: Store, *, allow_external_paths: bool = False) -> tuple[Dataset, dict]:
    project = load_json(read_bounded(path, 8 * 1024 * 1024))
    root = path.parent

    def read_source(name, limit):
        candidate = root / name
        if not allow_external_paths and not candidate.resolve().is_relative_to(root.resolve()):
            raise ValueError(
                "Una fuente está fuera de la carpeta del proyecto; conservarla dentro o habilitar expresamente rutas externas de confianza."
            )
        return read_bounded(candidate, limit)

    records = {}
    mappings = []
    documents = {}
    issues = []
    imports = {}
    for role in ("shipments", "charges"):
        config = project[role]
        mapping = ImportMapping.model_validate(load_json(read_source(config["mapping"], 8 * 1024 * 1024)))
        if mapping.entity != role:
            raise ValueError(f"El mapping no corresponde a {role}.")
        data = read_source(config["file"], MAX_FILE_BYTES)
        imported = import_data(data, Path(config["file"]).name, mapping)
        source_hash = store.put_source(data)
        documents[source_hash] = Path(config["file"]).name
        records[role] = imported["records"]
        mappings.append(mapping.model_dump(mode="json"))
        issues.extend(imported["issues"])
        imports[role] = {"accepted": imported["accepted"], "rejected": imported["rejected"]}
        store.save_config("mapping", f"{mapping.id}@{mapping.version}", mapping.model_dump(mode="json"))
    agreements = [
        Agreement.model_validate(value)
        for value in load_json(read_source(project["agreements"], 8 * 1024 * 1024))
    ]
    for agreement in agreements:
        store.save_config("agreement", agreement.name, agreement.model_dump(mode="json"))
    evidence = load_json(read_source(project["evidence"], 8 * 1024 * 1024)) if project.get("evidence") else []
    for attachment in project.get("attachments", []):
        data = read_source(attachment["file"], MAX_FILE_BYTES)
        source_hash = store.put_source(data)
        documents[source_hash] = Path(attachment["file"]).name
        found = [item for item in evidence if item["id"] == attachment["evidence_id"]]
        if len(found) != 1:
            raise ValueError("Un adjunto no tiene una referencia de evidencia única.")
        found[0]["document_hash"] = source_hash
    contract_sources = []
    for citation in project.get("contract_sources", []):
        citation = dict(citation)
        filename = citation.pop("file")
        source_hash = store.put_source(read_source(filename, MAX_FILE_BYTES))
        documents[source_hash] = Path(filename).name
        contract_sources.append(ContractSource.model_validate({**citation, "document_hash": source_hash}))
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
        contract_sources=contract_sources,
        external_control=load_json(read_source(project["external_control"], 2 * 1024 * 1024))
        if project.get("external_control")
        else None,
        parent_run_id=project.get("parent_run_id"),
        revision_kind=project.get("revision_kind"),
        revision_note=project.get("revision_note"),
    ), imports
