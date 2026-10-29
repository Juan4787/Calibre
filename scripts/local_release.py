"""Linux release activation with complete DB backups and loss-preserving rollback.

No product imports: inspect/backup the old databases BEFORE the new runtime can
migrate them. Every backup is verified and every restore retains the later data.
"""

import hashlib
import json
import os
import re
import shlex
import shutil
import sqlite3
import subprocess
import time
import urllib.request
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path


def stamp():
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")


def checksum(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path, value):
    temporary = path.with_name(path.name + ".pending")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)


def controlled(root, path):
    path = Path(path)
    path.resolve().relative_to(root.resolve())
    if any(p.is_symlink() for p in (path, *path.parents) if p != root and root in p.parents):
        raise ValueError(
            "Una base atraviesa un enlace; conservarla y revisar la ubicación antes de actualizar."
        )
    return path


def fingerprint(connection):
    tables = sorted(
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    )
    result = {}
    for table in tables:
        # Hash each row then sort small digests: independent of SQLite page layout.
        rows = []
        for row in connection.execute('SELECT * FROM "' + table.replace('"', '""') + '"'):
            values = [
                {
                    "type": type(value).__name__,
                    "sha256": hashlib.sha256(
                        value if isinstance(value, bytes) else value.encode()
                    ).hexdigest(),
                }
                if isinstance(value, (bytes, str))
                else value
                for value in row
            ]
            rows.append(
                hashlib.sha256(
                    json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode()
                ).digest()
            )
        result[table] = {"rows": len(rows), "sha256": hashlib.sha256(b"".join(sorted(rows))).hexdigest()}
    return result


def copy_database(source, target):
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (
        closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as origin,
        closing(sqlite3.connect(target)) as destination,
    ):
        origin.backup(destination)
        if (
            destination.execute("PRAGMA quick_check").fetchone()[0] != "ok"
            or destination.execute("PRAGMA foreign_key_check").fetchall()
        ):
            raise ValueError(
                "El respaldo no supera el control de integridad; conservar el original y detener la actualización."
            )
        before = fingerprint(origin)
        if before != fingerprint(destination):
            raise ValueError("El respaldo difiere del original; no se activó la actualización.")
        version = destination.execute("PRAGMA user_version").fetchone()[0]
    target.chmod(0o600)
    return {"sha256": checksum(target), "schema": version, "tables": before}


def inventory(root):
    main = root / "workspaces/default/audit.db"
    if not main.exists():
        return []
    paths = [controlled(root, main)]
    with closing(sqlite3.connect(main.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        for stored_hash, payload in connection.execute(
            "SELECT hash,payload FROM configs WHERE kind='workspace'"
        ):
            entry = json.loads(payload)
            canonical = json.dumps(
                entry, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
            )
            if hashlib.sha256(canonical.encode()).hexdigest() != stored_hash or not re.fullmatch(
                r"[0-9a-f]{32}", entry["id"]
            ):
                raise ValueError(
                    "El registro de espacios fue alterado; restaurar una copia verificada antes de actualizar."
                )
            path = controlled(root, main.parent / (main.stem + "-workspaces") / entry["id"] / "audit.db")
            if not path.is_file():
                raise ValueError("Falta una base de cliente registrada; recuperarla antes de actualizar.")
            paths.append(path)
    return sorted(set(paths))


def backup_set(root, version, previous):
    paths = inventory(root)
    directory = root / "backups" / ("before-" + version + "-" + stamp())
    directory.mkdir(parents=True, mode=0o700)
    manifest = {
        "version": version,
        "previous": str(previous) if previous else None,
        "directory": str(directory),
        "databases": [],
    }
    for path in paths:
        relative = path.relative_to(root)
        info = copy_database(path, directory / relative)
        manifest["databases"].append({"relative": str(relative), **info})
    atomic_json(directory / "manifest.json", manifest)
    return manifest


def preserve_and_restore(root, manifest):
    directory = Path(manifest["directory"])
    directory.resolve().relative_to((root / "backups").resolve())
    # Validate ALL backup files before changing any active database.
    for entry in manifest["databases"]:
        relative = Path(entry["relative"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("El registro de respaldo contiene una ruta inválida.")
        backup = controlled(directory, directory / relative)
        if checksum(backup) != entry["sha256"]:
            raise ValueError("El respaldo fue alterado; detener la reversión y conservar todos los archivos.")
    preserved = root / "backups" / ("after-preserved-" + stamp())
    preserved.mkdir(mode=0o700)
    later = []
    # Include new clients added since activation, even if restoring the old registry.
    for path in sorted((root / "workspaces").rglob("*.db")):
        controlled(root, path)
        relative = path.relative_to(root)
        target = preserved / relative
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(path, target)
        target.chmod(0o600)
        for suffix in ("-wal", "-shm", "-journal"):
            auxiliary = Path(str(path) + suffix)
            if auxiliary.exists():
                shutil.copyfile(auxiliary, Path(str(target) + suffix))
        later.append(str(relative))
    atomic_json(
        preserved / "preservation.json",
        {
            "files": later,
            "reason": "Data after upgrade, retained before rollback; includes unregistered/new clients",
        },
    )
    for entry in manifest["databases"]:
        path = controlled(root, root / entry["relative"])
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        for suffix in ("-wal", "-shm", "-journal"):
            Path(str(path) + suffix).unlink(missing_ok=True)
        temporary = path.with_name(path.name + ".restore-pending")
        shutil.copyfile(directory / entry["relative"], temporary)
        temporary.chmod(0o600)
        temporary.replace(path)
    return preserved


def switch(root, release):
    current = root / "current"
    if current.exists() and not current.is_symlink():
        raise ValueError(
            "El destino activo no es un enlace de versiones; conservarlo y revisar la instalación."
        )
    temporary = root / (".activate-" + str(os.getpid()))
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(release)
    temporary.replace(current)


def migrate(python, paths, root):
    environment = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    for path in paths:
        subprocess.run(
            [
                str(python),
                "-c",
                "from freight_audit.storage import Store; from freight_audit.workspaces import Workspaces; import sys; Workspaces.verify(Store(sys.argv[1]))",
                str(path),
            ],
            cwd=root,
            env=environment,
            check=True,
        )


class SystemdService:
    def __init__(self, root, *, port=8765, name="calibre-freight.service"):
        if not re.fullmatch(r"[A-Za-z0-9_.@-]+\.service", name) or not 1 <= port <= 65535:
            raise ValueError("Seleccionar un nombre de servicio y un puerto local válidos.")
        self.root, self.port, self.name = root, port, name
        self.unit = Path.home() / ".config/systemd/user" / name
        self.launcher = Path.home() / ".local/bin" / name.removesuffix(".service")
        self.files = [self.unit, self.launcher]
        if any(ord(char) < 32 for char in str(root)):
            raise ValueError("Seleccionar una ubicación sin caracteres de control.")
        if self.unit.exists():
            configured = re.search(r"^WorkingDirectory=(.+)$", self.unit.read_text(), re.M)
            if configured is None or Path(configured[1].replace("%%", "%")).resolve() != root.resolve():
                raise ValueError(
                    "Este servicio pertenece a otra instalación. Elegir su raíz correcta u otro --service-name."
                )

    def command(self, *args, check=True):
        return subprocess.run(["systemctl", "--user", *args], capture_output=True, check=check)

    def stop(self):
        if self.unit.exists() or self.command("is-active", "--quiet", self.name, check=False).returncode == 0:
            stopped = self.command("stop", self.name, check=False)
            if stopped.returncode:
                pid = self.command(
                    "show", "--property=MainPID", "--value", self.name, check=False
                ).stdout.strip()
                # An invalid/not-loaded unit has no process to stop. Never let
                # that mask the startup failure or skip preservation/rollback.
                if pid not in {b"", b"0"}:
                    stopped.check_returncode()

    def configure(self):
        self.launcher.parent.mkdir(parents=True, exist_ok=True)
        self.launcher.write_text(
            '#!/bin/sh\nset -eu\nunset PYTHONPATH\nif [ "$#" -eq 0 ]; then set -- serve --port '
            + str(self.port)
            + "; fi\nexec "
            + shlex.quote(str(self.root / "current/bin/freight-audit"))
            + " --db "
            + shlex.quote(str(self.root / "workspaces/default/audit.db"))
            + ' "$@"\n'
        )
        self.launcher.chmod(0o700)

        def quoted(path):
            return '"' + str(path).replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") + '"'

        self.unit.parent.mkdir(parents=True, exist_ok=True)
        self.unit.write_text(
            "[Unit]\nDescription=Calibre local freight audit\n\n[Service]\nType=simple\nWorkingDirectory="
            + str(self.root).replace("%", "%%")
            + "\nExecStart="
            + quoted(self.launcher)
            + "\nUMask=0077\nNoNewPrivileges=true\nRestart=on-failure\nRestartSec=3\n\n[Install]\nWantedBy=default.target\n"
        )
        self.unit.chmod(0o600)

    def reload(self):
        if not self.unit.exists():
            self.command("disable", self.name, check=False)
        self.command("daemon-reload")

    def start(self):
        self.reload()
        self.command("enable", "--now", self.name)

    def owns_listener(self, port):
        pid = self.command("show", "--property=MainPID", "--value", self.name).stdout.decode().strip()
        if not pid.isdigit() or pid == "0":
            return False
        process = Path("/proc") / pid
        if (process / "cwd").resolve() != self.root.resolve():
            return False
        expected = f"0100007F:{port:04X}"
        sockets = {path.readlink().as_posix() for path in (process / "fd").iterdir() if path.is_symlink()}
        for line in Path("/proc/net/tcp").read_text().splitlines()[1:]:
            fields = line.split()
            if fields[1] == expected and fields[3] == "0A" and f"socket:[{fields[9]}]" in sockets:
                return True
        return False

    def probe(self, release):
        # A rollback restores the previous launcher's port, which can differ
        # from the port requested for the failed candidate.
        configured = re.search(r"serve --port ([0-9]+)", self.launcher.read_text())
        port = int(configured[1]) if configured else self.port
        environment = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        expected = json.loads(
            subprocess.check_output(
                [
                    str(release / "bin/python"),
                    "-c",
                    "from freight_audit import ENGINE_VERSION; from freight_audit.storage import engine_artifact_hash; import json; print(json.dumps([ENGINE_VERSION, engine_artifact_hash()]))",
                ],
                cwd=self.root,
                env=environment,
            )
        )
        last = None
        for _ in range(40):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=2) as response:
                    health = json.load(response)
                if (
                    health["engine_version"] == expected[0]
                    and health["artifact_hash"] == expected[1]
                    and self.command("is-active", "--quiet", self.name, check=False).returncode == 0
                    and self.owns_listener(port)
                ):
                    return health
            except (OSError, ValueError, KeyError) as exc:
                last = exc
            time.sleep(0.25)
        raise ValueError(
            "La instalación no supera la comprobación de salud; se iniciará la reversión preservando datos."
        ) from last


def activate(root, release, checksum_value, *, service=None):
    root = root.resolve()
    current = root / "current"
    previous = current.resolve() if current.is_symlink() else None
    if previous:
        previous.relative_to((root / "releases").resolve())
        if not (previous / "bin/python").is_file():
            raise ValueError("Falta la versión anterior; recuperarla antes de actualizar.")
        if previous == release.resolve():
            if service:
                service.probe(release)
            return json.loads((root / "activation.json").read_text())
    # Refuse an invalid pointer before stopping service or touching data.
    if current.exists() and not current.is_symlink():
        raise ValueError(
            "El destino activo no es un enlace de versiones; conservarlo y revisar la instalación."
        )
    if service:
        service.stop()
    manifest = None
    configurations = []
    try:
        manifest = backup_set(root, release.name, previous)
        if service:
            for index, path in enumerate(service.files):
                saved = Path(manifest["directory"]) / f"service-file-{index}"
                if path.exists():
                    shutil.copyfile(path, saved)
                configurations.append({"path": str(path), "backup": str(saved) if path.exists() else None})
        manifest["service_files"] = configurations
        atomic_json(Path(manifest["directory"]) / "manifest.json", manifest)
        atomic_json(root / "activation-pending.json", manifest)
        paths = [root / entry["relative"] for entry in manifest["databases"]]
        main = root / "workspaces/default/audit.db"
        main.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        migrate(release / "bin/python", paths or [main], root)
        for entry in manifest["databases"]:
            with closing(sqlite3.connect(root / entry["relative"])) as connection:
                actual = fingerprint(connection)
                if any(actual.get(table) != info for table, info in entry["tables"].items()):
                    raise ValueError(
                        "La actualización modificó datos históricos; se conservará evidencia y se revertirá."
                    )
        switch(root, release)
        health = None
        if service:
            service.configure()
            service.start()
            health = service.probe(release)
        receipt = {
            "version": release.name,
            "current": str(release),
            "previous": str(previous) if previous else None,
            "database": str(main),
            "backup_manifest": str(Path(manifest["directory"]) / "manifest.json"),
            "wheel_sha256": checksum_value,
            "activated_at": datetime.now(UTC).isoformat(),
            "health": health,
            "service_managed": bool(service),
        }
        atomic_json(root / "activation.json", receipt)
        (root / "activation-pending.json").unlink()
        return receipt
    except BaseException:
        if service:
            service.stop()
        if manifest is not None:
            preserved = preserve_and_restore(root, manifest)
            restore_service_files(manifest)
            if service:
                service.reload()
            atomic_json(
                root / "activation-failed.json",
                {
                    "backup": manifest["directory"],
                    "preserved": str(preserved),
                    "previous": str(previous) if previous else None,
                },
            )
        if previous:
            switch(root, previous)
            if service:
                service.start()
                service.probe(previous)
        elif current.is_symlink():
            current.unlink()
        (root / "activation-pending.json").unlink(missing_ok=True)
        raise


def restore_service_files(manifest):
    for entry in manifest.get("service_files", []):
        path = Path(entry["path"])
        if entry["backup"]:
            shutil.copyfile(entry["backup"], path)
        else:
            path.unlink(missing_ok=True)


def rollback(root, *, service=None):
    receipt = json.loads((root / "activation.json").read_text())
    if not receipt.get("previous"):
        raise ValueError(
            "No hay una versión anterior para activar. Conservar la instalación y sus respaldos."
        )
    if (root / "current").resolve() != Path(receipt["current"]):
        raise ValueError(
            "La versión activa cambió desde este recibo; revisar el historial antes de revertir."
        )
    previous = Path(receipt["previous"])
    previous.relative_to((root / "releases").resolve())
    if not (previous / "bin/python").is_file():
        raise ValueError("Falta la versión anterior; recuperarla antes de modificar los datos.")
    manifest = json.loads(Path(receipt["backup_manifest"]).read_text())
    if service:
        service.stop()
    preserved = preserve_and_restore(root, manifest)
    restore_service_files(manifest)
    if service:
        service.reload()
    switch(root, previous)
    health = None
    if service:
        service.start()
        health = service.probe(previous)
    result = {
        "current": str(previous),
        "preserved_after_upgrade": str(preserved),
        "health": health,
        "rolled_back_at": datetime.now(UTC).isoformat(),
    }
    atomic_json(root / "rollback.json", result)
    return result


def recover(root, *, service=None):
    """Explicit recovery after process termination; keep all later DB files first."""
    manifest = json.loads((root / "activation-pending.json").read_text())
    previous = Path(manifest["previous"]) if manifest["previous"] else None
    if previous:
        previous.relative_to((root / "releases").resolve())
        if not (previous / "bin/python").is_file():
            raise ValueError("Recuperar primero el entorno anterior; ningún archivo se modificó.")
    if service:
        service.stop()
    preserved = preserve_and_restore(root, manifest)
    restore_service_files(manifest)
    if service:
        service.reload()
    health = None
    if previous:
        switch(root, previous)
        if service:
            service.start()
            health = service.probe(previous)
    elif (root / "current").is_symlink():
        (root / "current").unlink()
    receipt = {"previous": str(previous), "preserved_after_interruption": str(preserved), "health": health}
    atomic_json(root / "activation-recovered.json", receipt)
    (root / "activation-pending.json").unlink()
    return receipt
