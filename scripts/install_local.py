#!/usr/bin/env python3
"""Prepare a versioned Linux installation; activate only after an isolated smoke.

Runtime data stays outside the checkout and release directories. Activation
preserves the previous pointer and a verified SQLite backup for rollback.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import venv
import zipfile
from datetime import UTC, datetime
from email.parser import Parser
from pathlib import Path


def run(arguments, *, cwd=None, env=None):
    subprocess.run(arguments, cwd=cwd, env=env, check=True)


def install(wheel: Path, lock: Path, root: Path, *, activate: bool):
    wheel = wheel.resolve()
    root = root.expanduser().resolve()
    checksum = hashlib.sha256(wheel.read_bytes()).hexdigest()
    with zipfile.ZipFile(wheel) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = Parser().parsestr(archive.read(name).decode())
    version = metadata["Version"]
    if (
        metadata["Name"] != "freight-audit"
        or not version
        or not re.fullmatch(r"\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?", version)
    ):
        raise ValueError("Seleccionar un wheel válido de Freight Audit.")
    release = root / "releases" / version
    receipt = release / "installation.json"
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    python = release / "bin/python"
    if release.exists():
        if not receipt.is_file() or json.loads(receipt.read_text())["wheel_sha256"] != checksum:
            raise ValueError(
                "El destino de esta versión existe sin un recibo coincidente; conservarlo y revisar la instalación."
            )
    else:
        release.parent.mkdir(parents=True, exist_ok=True)
        venv.create(release, with_pip=True)
        try:
            run([str(python), "-m", "pip", "install", "-r", str(lock.resolve())], env=environment)
            run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], env=environment)
            with tempfile.TemporaryDirectory(prefix="calibre-installed-smoke-") as directory:
                purelib = subprocess.check_output(
                    [str(python), "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                    text=True,
                    cwd=directory,
                    env=environment,
                ).strip()
                run(
                    [
                        str(python),
                        str(Path(__file__).resolve().parent / "smoke_wheel.py"),
                        "--installed-root",
                        purelib,
                    ],
                    cwd=directory,
                    env=environment,
                )
            receipt.write_text(
                json.dumps(
                    {
                        "version": version,
                        "wheel_sha256": checksum,
                        "installed_smoke": True,
                        "created_at": datetime.now(UTC).isoformat(),
                    },
                    indent=2,
                )
                + "\n"
            )
        except BaseException:
            # Do not pretend a partial environment is a completed release.
            (release / "INSTALLATION_INCOMPLETE.txt").write_text(
                "No activar esta carpeta. Conservar el log y preparar una instalación nueva verificada.\n"
            )
            raise
    if not activate:
        print(json.dumps({"prepared": str(release), "activated": False, "version": version}))
        return
    database = root / "workspaces/default/audit.db"
    database.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if database.exists():
        backup_dir = root / "backups"
        backup_dir.mkdir(exist_ok=True)
        backup = backup_dir / f"before-{version}-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}.db"
        with (
            sqlite3.connect(f"file:{database}?mode=ro", uri=True) as origin,
            sqlite3.connect(backup) as target,
        ):
            origin.backup(target)
            if target.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise ValueError("La copia previa no supera la verificación; no se activó la nueva versión.")
    current = root / "current"
    if current.exists() and not current.is_symlink():
        raise ValueError(
            "El destino activo no es un enlace de versiones; conservarlo y revisar la instalación."
        )
    previous = str(current.resolve()) if current.is_symlink() else None
    run(
        [
            str(python),
            "-c",
            "from freight_audit.storage import Store; import sys; Store(sys.argv[1])",
            str(database),
        ],
        cwd=root,
        env=environment,
    )
    pending = root / (".activate-" + str(os.getpid()))
    pending.symlink_to(release)
    pending.replace(current)
    activation = {
        "version": version,
        "current": str(release),
        "previous": previous,
        "database": str(database),
        "backup": str(backup) if backup else None,
        "wheel_sha256": checksum,
        "activated_at": datetime.now(UTC).isoformat(),
    }
    (root / "activation.json").write_text(json.dumps(activation, indent=2) + "\n")
    print(json.dumps(activation, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument(
        "--lock", type=Path, default=Path(__file__).resolve().parents[1] / "requirements.lock"
    )
    parser.add_argument("--root", type=Path, default=Path.home() / ".local/share/calibre")
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error(
            "Este instalador administra versiones locales Linux; usar el procedimiento documentado para Windows."
        )
    import fcntl

    args.root = args.root.expanduser().resolve()
    args.root.mkdir(parents=True, exist_ok=True)
    with (args.root / ".install.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        install(args.wheel, args.lock, args.root, activate=args.activate)


if __name__ == "__main__":
    main()
