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


def install(wheel: Path, lock: Path, root: Path, *, activate: bool, service=None):
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
            run(
                [str(python), "-m", "pip", "install", "--require-hashes", "-r", str(lock.resolve())],
                env=environment,
            )
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
    if __package__:
        from .local_release import activate as activate_release
    else:
        from local_release import activate as activate_release
    activation = activate_release(root, release, checksum, service=service)
    print(json.dumps(activation, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--wheel", type=Path)
    choice.add_argument("--rollback", action="store_true")
    choice.add_argument("--recover", action="store_true")
    parser.add_argument(
        "--lock", type=Path, default=Path(__file__).resolve().parents[1] / "requirements.lock"
    )
    parser.add_argument("--root", type=Path, default=Path.home() / ".local/share/calibre")
    parser.add_argument("--activate", action="store_true")
    parser.add_argument(
        "--no-service",
        action="store_true",
        help="Activación offline: exige detener manualmente cualquier proceso que use estas bases",
    )
    parser.add_argument("--service-name", default="calibre-freight.service")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error(
            "Este instalador administra versiones locales Linux; usar el procedimiento documentado para Windows."
        )
    import fcntl

    args.root = args.root.expanduser().resolve()
    args.root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.umask(0o077)
    from local_release import SystemdService, recover, rollback

    service = None if args.no_service else SystemdService(args.root, port=args.port, name=args.service_name)
    with (args.root / ".install.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.recover:
            print(json.dumps(recover(args.root, service=service), indent=2))
            return
        if (args.root / "activation-pending.json").exists():
            parser.error(
                "Hay una actualización interrumpida; ejecutar --recover con esta misma raíz antes de continuar."
            )
        if args.rollback:
            print(json.dumps(rollback(args.root, service=service), indent=2))
        else:
            install(args.wheel, args.lock, args.root, activate=args.activate, service=service)


if __name__ == "__main__":
    main()
