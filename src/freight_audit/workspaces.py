"""Local, separate SQLite workspaces; restoration always creates a new copy."""

import hashlib
import re
import shutil
import sqlite3
import tempfile
import uuid
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from .canonical import bytes_hash, digest, load_json
from .storage import IntegrityError, Store


class Workspaces:
    def __init__(self, root: Store):
        self.root = root
        self.directory = root.path.parent / (root.path.stem + "-workspaces")

    def list(self) -> list[dict]:
        entries = [{"id": "main", "name": "Sin cliente asignado", "database": str(self.root.path.resolve())}]
        entries.extend(
            {**c["payload"], "database": str(self.path(c["payload"]["id"]))}
            for c in reversed(self.root.configs())
            if c["kind"] == "workspace"
        )
        return entries

    def path(self, identifier: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{32}", identifier):
            raise KeyError("Seleccionar un espacio local existente.")
        return self.directory / identifier / "audit.db"

    def select(self, identifier: str) -> Store:
        if identifier == "main":
            return self.root
        if identifier not in {e["id"] for e in self.list()}:
            raise KeyError("Seleccionar un espacio local existente.")
        path = self.path(identifier)
        if not path.is_file():
            raise IntegrityError(
                "Falta la base de este espacio. Restaurar un respaldo sin reemplazar los archivos restantes."
            )
        return Store(path)

    def create(self, name: str, original: bytes | None = None) -> dict:
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120 or any(ord(c) < 32 for c in name):
            raise ValueError("Indicar un nombre de cliente o espacio de hasta 120 caracteres.")
        identifier = uuid.uuid4().hex
        path = self.path(identifier)
        path.parent.mkdir(mode=0o700, parents=True)
        try:
            if original is not None:
                if not original.startswith(b"SQLite format 3\x00"):
                    raise ValueError(
                        "El archivo no es un respaldo de Calibre. Seleccionar una copia de la base local."
                    )
                path.write_bytes(original)
                with closing(sqlite3.connect(f"file:{path}?mode=ro", uri=True)) as source:
                    required = {
                        "sources": {"hash", "data"},
                        "configs": {"hash", "kind", "name", "payload", "created_at"},
                        "runs": {
                            "id",
                            "input_hash",
                            "result_hash",
                            "artifact_hash",
                            "snapshot",
                            "result",
                            "metadata",
                            "created_at",
                        },
                        "decisions": {
                            "seq",
                            "run_id",
                            "finding_id",
                            "payload",
                            "previous_hash",
                            "hash",
                            "created_at",
                        },
                    }
                    tables = {
                        row[0] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    }
                    if not required.keys() <= tables or any(
                        not columns <= {row[1] for row in source.execute(f"PRAGMA table_info({table})")}
                        for table, columns in required.items()
                    ):
                        raise ValueError("El archivo no tiene el formato de un respaldo de Calibre.")
            store = Store(path)
            path.chmod(0o600)
            self.verify(store)
            entry = {"id": identifier, "name": name.strip()}
            if original is not None:
                entry["restored_from_hash"] = bytes_hash(original)
            else:
                store.save_config("workspace_identity", name.strip(), entry)
            # Register only after migration and complete integrity verification.
            self.root.save_config("workspace", name.strip(), entry)
            return {**entry, "database": str(path.resolve())}
        except (sqlite3.DatabaseError, KeyError, ValueError) as exc:
            shutil.rmtree(path.parent)
            raise ValueError(
                "No se pudo crear el espacio: el respaldo o su historial no supera el control de integridad. Conservar el original y elegir una copia verificada."
            ) from exc
        except BaseException:
            shutil.rmtree(path.parent)
            raise

    @staticmethod
    def verify(store: Store) -> None:
        with store.connect() as connection:
            if (
                connection.execute("PRAGMA quick_check").fetchone()[0] != "ok"
                or connection.execute("PRAGMA foreign_key_check").fetchall()
            ):
                raise IntegrityError("El respaldo no supera la comprobación de la base.")
            sources = [row[0] for row in connection.execute("SELECT hash FROM sources")]
            imports = connection.execute("SELECT * FROM imports").fetchall()
        for source in sources:
            store.source(source)
        for config in store.configs():
            if digest(config["payload"]) != config["hash"]:
                raise IntegrityError("Una configuración del respaldo fue alterada.")
        for imported in imports:
            if (
                digest([imported["artifact_hash"], bytes_hash(imported["payload"].encode())])
                != imported["id"]
            ):
                raise IntegrityError("Una importación del respaldo fue alterada.")
            store.source(load_json(imported["payload"])["document"])
        for run in store.list_runs():
            store.load(run["id"])

    @staticmethod
    def backup(store: Store) -> Path:
        directory = Path(tempfile.mkdtemp(prefix="calibre-backup-"))
        destination = directory / "calibre-backup.db"
        try:
            store.backup(destination)
            Workspaces.verify(Store(destination))
            checksum = hashlib.sha256()
            with destination.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    checksum.update(block)
            store.save_config(
                "backup_receipt",
                "Respaldo preparado",
                {
                    "created_at": datetime.now(UTC).isoformat(),
                    "sha256": checksum.hexdigest(),
                    "bytes": destination.stat().st_size,
                    "status": "prepared_for_download",
                    "off_device_confirmed": False,
                },
            )
            return destination
        except BaseException:
            shutil.rmtree(directory)
            raise
