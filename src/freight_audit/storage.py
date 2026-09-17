"""Local immutable snapshots, content-addressed originals, append-only decisions."""

import importlib.metadata
import json
import platform
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from . import ENGINE_VERSION
from .canonical import bytes_hash, canonical, digest, load_json
from .engine import audit
from .models import AuditResult, Charge, Dataset, Decision, Shipment


class IntegrityError(ValueError):
    pass


def engine_artifact_hash() -> str:
    root = Path(__file__).parent
    return digest(
        {
            name: bytes_hash((root / name).read_bytes())
            for name in ("__init__.py", "canonical.py", "models.py", "rules.py", "engine.py")
        }
    )


RUNNING_ARTIFACT_HASH = engine_artifact_hash()


def environment() -> dict:
    return {
        "python": platform.python_version(),
        "packages": {name: importlib.metadata.version(name) for name in ("pydantic", "openpyxl", "xlrd")},
    }


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version > 1:
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
            for table in ("sources", "configs", "runs", "decisions"):
                for operation in ("UPDATE", "DELETE"):
                    conn.execute(
                        f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{operation} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT, 'immutable history'); END"
                    )

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

    def save(self, dataset: Dataset, result: AuditResult) -> str:
        if engine_artifact_hash() != RUNNING_ARTIFACT_HASH:
            raise IntegrityError(
                "El programa cambió mientras estaba abierto. Cerrar y reiniciar el servicio local antes de guardar una nueva auditoría."
            )
        # The result must belong to exactly these inputs; callers cannot persist an edited finding.
        if result.engine_version != ENGINE_VERSION or canonical(audit(dataset)) != canonical(result):
            raise IntegrityError("El resultado no corresponde a estos datos y a esta versión del motor.")
        for source_hash in self.source_hashes(dataset):
            self.source(source_hash)
        input_hash = digest(dataset)
        result_hash = digest(result)
        artifact_hash = engine_artifact_hash()
        run_id = digest([input_hash, result_hash, artifact_hash])
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO runs VALUES (?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    input_hash,
                    result_hash,
                    artifact_hash,
                    canonical(dataset),
                    canonical(result),
                    canonical(environment()),
                    datetime.now(UTC).isoformat(),
                ),
            )
        return run_id

    @staticmethod
    def source_hashes(dataset: Dataset) -> list[str]:
        hashes = set(dataset.documents)
        records: list[Shipment | Charge] = [*dataset.shipments, *dataset.charges]
        for record in records:
            hashes.update(ref.document for ref in record.provenance.values())
        hashes.update(e.document_hash for e in dataset.evidence if e.document_hash)
        return sorted(hashes)

    def list_runs(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, created_at, input_hash, result_hash, json_extract(snapshot, '$.label') label, json_extract(result, '$.summary') summary FROM runs ORDER BY created_at DESC, id"
            ).fetchall()
        return [{**dict(row), "summary": json.loads(row["summary"])} for row in rows]

    def load(self, run_id: str) -> dict:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            raise KeyError("La auditoría no existe.")
        snapshot = load_json(row["snapshot"])
        result = load_json(row["result"])
        if (
            digest(snapshot) != row["input_hash"]
            or digest(result) != row["result_hash"]
            or digest([row["input_hash"], row["result_hash"], row["artifact_hash"]]) != run_id
        ):
            raise IntegrityError("La auditoría guardada no supera la verificación de integridad.")
        return {
            **dict(row),
            "snapshot": snapshot,
            "result": result,
            "metadata": load_json(row["metadata"]),
            "decisions": self.decisions(run_id),
        }

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
        if destination.exists():
            raise ValueError(
                "El destino ya existe; elegir un archivo nuevo para preservar la copia anterior."
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as origin, sqlite3.connect(destination) as target:
            origin.backup(target)
