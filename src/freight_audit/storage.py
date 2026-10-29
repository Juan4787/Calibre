"""Local immutable snapshots, content-addressed originals, append-only decisions."""

import gc
import importlib.metadata
import os
import platform
import sqlite3
import tempfile
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from . import ENGINE_VERSION
from .canonical import bytes_hash, canonical, digest, load_json
from .document_control import documentary_control
from .engine import audit
from .importing import MAX_NORMALIZED_BYTES
from .local_paths import checked_output_path
from .models import AuditResult, Charge, Dataset, Decision, Shipment
from .provenance import check_provenance


class IntegrityError(ValueError):
    pass


def engine_artifact_hash() -> str:
    root = Path(__file__).parent
    return digest(
        {
            name: bytes_hash((root / name).read_bytes())
            for name in (
                "__init__.py",
                "canonical.py",
                "models.py",
                "rules.py",
                "engine.py",
                "importing.py",
                "provenance.py",
                "document_control.py",
                "storage.py",
            )
        }
    )


RUNNING_ARTIFACT_HASH = engine_artifact_hash()


def importer_artifact_hash() -> str:
    root = Path(__file__).parent
    return digest(
        {
            name: bytes_hash((root / name).read_bytes())
            for name in ("canonical.py", "models.py", "importing.py")
        }
    )


def environment() -> dict:
    return {
        "python": platform.python_version(),
        "packages": {name: importlib.metadata.version(name) for name in ("pydantic", "openpyxl", "xlrd")},
    }


def run_identity(input_hash: str, result_hash: str, artifact_hash: str, metadata: dict) -> str:
    if not isinstance(metadata, dict):
        raise IntegrityError(
            "Los metadatos de la auditoría no tienen un formato válido; restaurar una copia verificada."
        )
    components = [input_hash, result_hash, artifact_hash]
    if metadata.get("run_identity_version") == 2:
        components.append(digest(metadata))
    return digest(components)


def _check_recorded_totals(dataset: Dataset, result: AuditResult) -> None:
    """Independent conservation check; no interpreter or Decimal aggregation."""
    expected: dict[str, Fraction] = {}
    for charge in dataset.charges:
        expected[charge.currency] = expected.get(charge.currency, Fraction()) + Fraction(charge.amount)
    try:
        observed = {}
        for currency, bucket in result.summary["currencies"].items():
            if not isinstance(bucket["actual"], str):
                raise ValueError("Non-text exact total")
            observed[currency] = Fraction(bucket["actual"])
        if any(
            expected.get(currency, Fraction()) != observed.get(currency, Fraction())
            for currency in expected.keys() | observed.keys()
        ):
            raise ValueError("Input totals differ")
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise IntegrityError(
            "Los totales del resultado no conservan los cargos originales. No se guardó la auditoría; revisar el cálculo antes de continuar."
        ) from exc


def _check_stored_json(payload: str, expected: str) -> None:
    # Normal stored payloads are canonical already: hash without building their
    # object graphs. Fallback preserves older equivalent JSON representations.
    if bytes_hash(payload.encode()) == expected:
        return
    try:
        if digest(load_json(payload)) == expected:
            return
    except ValueError:
        pass
    raise IntegrityError(
        "La auditoría guardada no supera la verificación de integridad; restaurar una copia verificada."
    )


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.connect() as conn:
                version = conn.execute("PRAGMA user_version").fetchone()[0]
                if version > 2:
                    raise IntegrityError(
                        "La base pertenece a una versión más nueva; abrir con esa versión del programa."
                    )
                if version == 0:
                    conn.executescript("""
                        CREATE TABLE IF NOT EXISTS sources (hash TEXT PRIMARY KEY, data BLOB NOT NULL);
                        CREATE TABLE IF NOT EXISTS configs (hash TEXT PRIMARY KEY, kind TEXT NOT NULL, name TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL);
                        CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, input_hash TEXT NOT NULL, result_hash TEXT NOT NULL, artifact_hash TEXT NOT NULL, snapshot TEXT NOT NULL, result TEXT NOT NULL, metadata TEXT NOT NULL, created_at TEXT NOT NULL);
                        CREATE TABLE IF NOT EXISTS decisions (seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(id), finding_id TEXT NOT NULL, payload TEXT NOT NULL, previous_hash TEXT NOT NULL, hash TEXT NOT NULL, created_at TEXT NOT NULL);
                        CREATE INDEX IF NOT EXISTS decisions_run ON decisions(run_id, seq);
                        PRAGMA user_version=1;
                    """)
                if version < 2:
                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS imports (id TEXT PRIMARY KEY, artifact_hash TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL)"
                    )
                    conn.execute(
                        "CREATE INDEX IF NOT EXISTS runs_parent ON runs(json_extract(snapshot, '$.parent_run_id'))"
                    )
                    conn.execute("PRAGMA user_version=2")
                for table in ("sources", "configs", "runs", "decisions", "imports"):
                    for operation in ("UPDATE", "DELETE"):
                        conn.execute(
                            f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{operation} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT, 'immutable history'); END"
                        )
        except sqlite3.DatabaseError as exc:
            raise IntegrityError(
                "No se pudo abrir o actualizar la base. Conservar el archivo y abrir una copia verificada; "
                "la actualización incompleta se revirtió."
            ) from exc

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def put_source(self, data: bytes) -> str:
        source_hash = bytes_hash(data)
        with self.connect() as conn:
            conn.execute("INSERT OR IGNORE INTO sources VALUES (?, ?)", (source_hash, data))
        return source_hash

    def source(self, source_hash: str) -> bytes:
        with self.connect() as conn:
            row = conn.execute("SELECT data FROM sources WHERE hash=?", (source_hash,)).fetchone()
        if row is None or bytes_hash(row["data"]) != source_hash:
            raise IntegrityError(
                "Falta un documento original o su contenido fue alterado; restaurar una copia verificada."
            )
        return row["data"]

    def save_config(self, kind: str, name: str, payload: dict) -> str:
        value_hash = digest(payload)
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO configs VALUES (?,?,?,?,?)",
                (value_hash, kind, name, canonical(payload), datetime.now(UTC).isoformat()),
            )
        return value_hash

    def configs(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM configs ORDER BY created_at DESC, hash").fetchall()
        return [{**dict(row), "payload": load_json(row["payload"])} for row in rows]

    def save_import(self, imported: dict) -> str:
        self.source(imported["document"])
        payload = canonical(imported)
        if len(payload.encode()) > MAX_NORMALIZED_BYTES:
            raise ValueError(
                "El lote normalizado supera el presupuesto de importación; dividirlo en períodos más pequeños antes de continuar."
            )
        artifact = importer_artifact_hash()
        identifier = digest([artifact, bytes_hash(payload.encode())])
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO imports VALUES (?,?,?,?)",
                (identifier, artifact, payload, datetime.now(UTC).isoformat()),
            )
        return identifier

    def load_import(self, identifier: str) -> dict:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM imports WHERE id=?", (identifier,)).fetchone()
        if row is None:
            raise KeyError("La importación no existe en este espacio; volver a validar el archivo.")
        if digest([row["artifact_hash"], bytes_hash(row["payload"].encode())]) != identifier:
            raise IntegrityError(
                "La importación conservada no supera el cotejo; volver a validar desde el original."
            )
        if row["artifact_hash"] != importer_artifact_hash():
            raise ValueError(
                "El lector cambió desde la validación. Volver a validar los originales con esta versión antes de auditar."
            )
        imported = load_json(row["payload"])
        self.source(imported["document"])
        return imported

    def save(self, dataset: Dataset, result: AuditResult) -> str:
        control = documentary_control(dataset)
        if control["status"] == "mismatch":
            raise ValueError(
                "El control documental no coincide. "
                + " ".join(control["problems"])
                + " Corregir el alcance o los archivos antes de conservar la auditoría."
            )
        if dataset.parent_run_id:
            self.load(dataset.parent_run_id)
        if engine_artifact_hash() != RUNNING_ARTIFACT_HASH:
            raise IntegrityError(
                "El programa cambió mientras estaba abierto. Cerrar y reiniciar el servicio local antes de guardar una nueva auditoría."
            )
        # The result must belong to exactly these inputs; callers cannot persist an edited finding.
        if result.engine_version != ENGINE_VERSION:
            raise IntegrityError("El resultado no corresponde a estos datos y a esta versión del motor.")
        _check_recorded_totals(dataset, result)

        # Serialize result once and compute hash directly
        result_json = canonical(result)
        result_hash = bytes_hash(result_json.encode())

        # Validate that the result belongs to exactly these inputs.
        # Passing audit(dataset) as an anonymous temporary ensures the re-audited result tree
        # is discarded immediately upon calculating its digest, avoiding concurrent trees in memory.
        expected_result_hash = digest(audit(dataset))
        if expected_result_hash != result_hash:
            raise IntegrityError("El resultado no corresponde a estos datos y a esta versión del motor.")
        del expected_result_hash
        gc.collect()

        for source_hash in self.source_hashes(dataset):
            self.source(source_hash)
        provenance = check_provenance(dataset, self.source)

        # Serialize dataset once and compute hash directly
        dataset_json = canonical(dataset)
        input_hash = bytes_hash(dataset_json.encode())

        artifact_hash = engine_artifact_hash()
        metadata = {
            **environment(),
            "provenance": provenance,
            "document_control": control,
            "workspace": self.identity(),
            "run_identity_version": 2,
        }
        run_id = run_identity(input_hash, result_hash, artifact_hash, metadata)
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO runs VALUES (?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    input_hash,
                    result_hash,
                    artifact_hash,
                    dataset_json,
                    result_json,
                    canonical(metadata),
                    datetime.now(UTC).isoformat(),
                ),
            )
        del dataset_json, result_json
        gc.collect()
        return run_id

    @staticmethod
    def source_hashes(dataset: Dataset) -> list[str]:
        hashes = set(dataset.documents)
        records: list[Shipment | Charge] = [*dataset.shipments, *dataset.charges]
        for record in records:
            hashes.update(ref.document for ref in record.provenance.values())
        hashes.update(e.document_hash for e in dataset.evidence if e.document_hash)
        hashes.update(c.document_hash for c in dataset.contract_sources)
        return sorted(hashes)

    def identity(self) -> dict:
        identities = [c["payload"] for c in self.configs() if c["kind"] == "workspace_identity"]
        return identities[-1] if identities else {"id": "main", "name": "Sin cliente asignado"}

    def list_runs(self) -> list[dict]:
        result = []
        try:
            with self.connect() as conn:
                rows = conn.execute(
                    "SELECT id,created_at,input_hash,result_hash,artifact_hash,snapshot,result,metadata,json_extract(snapshot,'$.label') label,json_extract(result,'$.summary') summary FROM runs ORDER BY created_at DESC,id"
                )
                for row in rows:
                    _check_stored_json(row["snapshot"], row["input_hash"])
                    _check_stored_json(row["result"], row["result_hash"])
                    if (
                        run_identity(
                            row["input_hash"],
                            row["result_hash"],
                            row["artifact_hash"],
                            load_json(row["metadata"]),
                        )
                        != row["id"]
                    ):
                        raise IntegrityError(
                            "El historial no supera la verificación de integridad; restaurar una copia verificada."
                        )
                    result.append(
                        {key: row[key] for key in ("id", "created_at", "input_hash", "result_hash", "label")}
                        | {"summary": load_json(row["summary"])}
                    )
        except sqlite3.DatabaseError as exc:
            raise IntegrityError(
                "No se pudo verificar el historial guardado. Conservar la base y restaurar una copia verificada."
            ) from exc
        return result

    def load(self, run_id: str) -> dict:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            raise KeyError("La auditoría no existe.")
        snapshot = load_json(row["snapshot"])
        result = load_json(row["result"])
        metadata = load_json(row["metadata"])
        if (
            digest(snapshot) != row["input_hash"]
            or digest(result) != row["result_hash"]
            or run_identity(row["input_hash"], row["result_hash"], row["artifact_hash"], metadata) != run_id
        ):
            raise IntegrityError("La auditoría guardada no supera la verificación de integridad.")
        for source_hash in self.source_hashes(Dataset.model_validate(snapshot)):
            self.source(source_hash)
        return {
            **dict(row),
            "snapshot": snapshot,
            "result": result,
            "metadata": metadata,
            "decisions": self.decisions(run_id),
            "revisions": self.revisions(run_id),
        }

    def revisions(self, run_id: str) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, created_at, json_extract(snapshot, '$.label') label, json_extract(snapshot, '$.revision_kind') kind FROM runs WHERE json_extract(snapshot, '$.parent_run_id')=? ORDER BY created_at, id",
                (run_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def replay(self, run_id: str) -> dict:
        run = self.load(run_id)
        for source_hash in self.source_hashes(Dataset.model_validate(run["snapshot"])):
            self.source(source_hash)
        if run["artifact_hash"] != engine_artifact_hash() or engine_artifact_hash() != RUNNING_ARTIFACT_HASH:
            raise IntegrityError(
                "El código del motor cambió. Conservar el resultado original y reproducir con el artefacto de su versión; no sobrescribir la auditoría."
            )
        result = audit(Dataset.model_validate(run["snapshot"]))
        if digest(result) != run["result_hash"]:
            raise IntegrityError("La reproducción no coincide con el resultado original.")
        return {
            "run_id": run_id,
            "identical": True,
            "result_hash": run["result_hash"],
            "artifact_hash": run["artifact_hash"],
        }

    def add_decision(self, run_id: str, decision: Decision) -> dict:
        run = self.load(run_id)
        if decision.finding_id not in {finding["id"] for finding in run["result"]["findings"]}:
            raise ValueError("Seleccionar un hallazgo de esta auditoría.")
        if not set(decision.evidence_ids) <= {e["id"] for e in run["snapshot"]["evidence"]}:
            raise ValueError(
                "La evidencia citada no forma parte de esta auditoría. Agregarla en una nueva corrida."
            )
        now = datetime.now(UTC).isoformat()
        payload = decision.model_dump(mode="json")
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT hash FROM decisions WHERE run_id=? ORDER BY seq DESC LIMIT 1", (run_id,)
            ).fetchone()
            previous = row[0] if row else run_id
            value_hash = digest([previous, payload, now])
            cursor = conn.execute(
                "INSERT INTO decisions(run_id,finding_id,payload,previous_hash,hash,created_at) VALUES (?,?,?,?,?,?)",
                (run_id, decision.finding_id, canonical(payload), previous, value_hash, now),
            )
            sequence = cursor.lastrowid
        return {"seq": sequence, "hash": value_hash, "created_at": now, "payload": payload}

    def decisions(self, run_id: str) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM decisions WHERE run_id=? ORDER BY seq", (run_id,)).fetchall()
        previous = run_id
        result = []
        for row in rows:
            payload = load_json(row["payload"])
            if (
                row["previous_hash"] != previous
                or digest([previous, payload, row["created_at"]]) != row["hash"]
            ):
                raise IntegrityError(
                    "El historial de decisiones fue alterado; restaurar una copia verificada."
                )
            previous = row["hash"]
            result.append({**dict(row), "payload": payload})
        return result

    def backup(self, destination: Path):
        destination = checked_output_path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        checked_output_path(destination)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".freight-backup-", suffix=".tmp", dir=destination.parent
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            with self.connect() as origin, closing(sqlite3.connect(temporary)) as target:
                origin.backup(target)
                if target.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise IntegrityError("La copia de la base no superó su control de integridad.")
            # A hard link in the same directory publishes the completed copy
            # atomically and fails if any file or symlink already has this name.
            try:
                os.link(temporary, destination)
            except FileExistsError as exc:
                raise ValueError(
                    "El destino ya existe; elegir un archivo nuevo para preservar la copia anterior."
                ) from exc
        finally:
            temporary.unlink(missing_ok=True)
