#!/usr/bin/env python3
"""Verify tracked-source parity, clean builds, and installed wheel/sdist behavior."""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def command(arguments, *, cwd=ROOT, environment=None):
    result = subprocess.run(
        arguments, cwd=cwd, env=environment, capture_output=True, text=True, check=False, timeout=600
    )
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(map(str, arguments))} failed ({result.returncode}): "
            + (result.stdout + result.stderr)[-4000:]
        )
    return result.stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def archive_contents(path):
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return {name: sha(archive.read(name)) for name in archive.namelist()}
    with tarfile.open(path, "r:gz") as archive:
        return {
            member.name: sha(archive.extractfile(member).read())
            for member in archive.getmembers()
            if member.isfile()
        }


def pinned_environment(venv_python, lock):
    freeze = command([venv_python, "-m", "pip", "freeze"])
    installed = {
        name.lower().replace("_", "-"): version
        for line in freeze.splitlines()
        if "==" in line
        for name, version in [line.split("==", 1)]
    }
    expected = {
        name.lower().replace("_", "-"): version
        for line in lock.splitlines()
        if line and not line.startswith("#")
        for name, version in [line.split("==", 1)]
    }
    if any(installed.get(name) != version for name, version in expected.items()):
        raise RuntimeError("The isolated environment differs from requirements.lock")
    command([venv_python, "-m", "pip", "check"])
    return {name: installed[name] for name in sorted(expected)}


def clean_source(directory, archived):
    with tarfile.open(fileobj=io.BytesIO(archived), mode="r:") as archive:
        archive.extractall(directory, filter="data")
    names = [name.decode() for name in command_bytes(["git", "ls-files", "-z"]).split(b"\0") if name]
    for name in names:
        original = ROOT / name
        copied = directory / name
        if original.is_symlink():
            if not copied.is_symlink() or os.readlink(original) != os.readlink(copied):
                raise RuntimeError(f"Tracked symlink differs: {name}")
        elif not copied.is_file() or sha(original.read_bytes()) != sha(copied.read_bytes()):
            raise RuntimeError(f"Tracked file differs: {name}")
    forbidden = [
        name
        for name in names
        if name.startswith(".local/")
        or name.startswith("output/review-")
        or name.endswith((".db", ".sqlite", ".sqlite3"))
        or Path(name).name in {".env", ".env.local"}
    ]
    if forbidden:
        raise RuntimeError("Private runtime files are tracked: " + ", ".join(forbidden))
    return len(names)


def command_bytes(arguments):
    return subprocess.check_output(arguments, cwd=ROOT, timeout=120)


def smoke(installed_python, checkout, workdir):
    purelib = command(
        [installed_python, "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"], cwd=workdir
    ).strip()
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    return command(
        [
            installed_python,
            str(checkout / "scripts/smoke_wheel.py"),
            "--installed-root",
            purelib,
            "--fixtures-root",
            str(checkout / "fixtures"),
        ],
        cwd=workdir,
        environment=environment,
    ).strip()


def verify(output):
    if command_bytes(["git", "status", "--porcelain", "--untracked-files=all"]).strip():
        raise RuntimeError("Commit or remove worktree changes before delivery verification")
    commit = command(["git", "rev-parse", "HEAD"]).strip()
    tree = command(["git", "rev-parse", "HEAD^{tree}"]).strip()
    archived = command_bytes(["git", "archive", "--format=tar", "HEAD"])
    with tempfile.TemporaryDirectory(prefix="freight-delivery-") as temporary:
        base = Path(temporary)
        checkouts = [base / "checkout-a", base / "checkout-b"]
        for checkout in checkouts:
            checkout.mkdir()
        tracked_count = clean_source(checkouts[0], archived)
        clean_source(checkouts[1], archived)
        for checkout in checkouts:
            command([sys.executable, "-m", "build", "--no-isolation"], cwd=checkout)
        artifacts = []
        for checkout in checkouts:
            files = sorted((checkout / "dist").iterdir())
            if len(files) != 2 or {path.suffix for path in files} != {".whl", ".gz"}:
                raise RuntimeError("Expected one wheel and one sdist per clean build")
            artifacts.append({path.name: path for path in files})
        if artifacts[0].keys() != artifacts[1].keys():
            raise RuntimeError("Builds produced different filenames")
        builds = {}
        for name in artifacts[0]:
            first, second = artifacts[0][name], artifacts[1][name]
            first_contents, second_contents = archive_contents(first), archive_contents(second)
            if first_contents != second_contents:
                raise RuntimeError(f"Build content differs across clean checkouts: {name}")
            builds[name] = {
                "first_sha256": sha(first.read_bytes()),
                "second_sha256": sha(second.read_bytes()),
                "byte_identical": first.read_bytes() == second.read_bytes(),
                "member_count": len(first_contents),
                "content_digest": sha(json.dumps(first_contents, sort_keys=True).encode()),
            }
        wheel = next(path for name, path in artifacts[0].items() if name.endswith(".whl"))
        sdist = next(path for name, path in artifacts[0].items() if name.endswith(".gz"))
        wheel_members = archive_contents(wheel)
        if (
            not {
                "freight_audit/static/index.html",
                "freight_audit/static/app.js",
                "freight_audit/local_paths.py",
            }
            <= wheel_members
        ):
            raise RuntimeError("The wheel lacks a required product resource")
        if any(name.endswith((".db", ".sqlite")) or "/.env" in name for name in wheel_members):
            raise RuntimeError("The wheel contains a private runtime file")
        venv = base / "venv"
        command([sys.executable, "-m", "venv", str(venv)])
        venv_python = str(venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
        lock = (checkouts[0] / "requirements.lock").read_text(encoding="utf-8")
        command(
            [venv_python, "-m", "pip", "install", "--no-input", "-r", "requirements.lock"], cwd=checkouts[0]
        )
        pinned = pinned_environment(venv_python, lock)
        command([venv_python, "-m", "pip", "install", "--no-input", "--no-deps", str(wheel)], cwd=base)
        wheel_smoke = smoke(venv_python, checkouts[0], base)
        command([venv_python, "-m", "pip", "uninstall", "-y", "freight-audit"], cwd=base)
        command(
            [
                venv_python,
                "-m",
                "pip",
                "install",
                "--no-input",
                "--no-deps",
                "--no-build-isolation",
                str(sdist),
            ],
            cwd=base,
        )
        sdist_smoke = smoke(venv_python, checkouts[0], base)
        report = {
            "commit": commit,
            "tree": tree,
            "tracked_files_compared": tracked_count,
            "requirements_lock_sha256": sha(lock.encode()),
            "pinned_environment": pinned,
            "clean_builds": builds,
            "wheel_smoke": wheel_smoke,
            "sdist_smoke": sdist_smoke,
            "scope": "Clean source, package content and installed behavior on this OS; not Windows Excel or field validation",
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    verify(parser.parse_args().output)
