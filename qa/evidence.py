"""Bind execution receipts to the code actually checked, including a dirty checkout."""

import hashlib
import json
from pathlib import Path


def source_digest(root: Path) -> str:
    paths = []
    for directory in ("src", "tests", "qa", "scripts", "fixtures", ".github", "output/e2e"):
        for path in (root / directory).rglob("*"):
            if any(
                part in {"__pycache__", "isolated_env"} or part.endswith(".egg-info") for part in path.parts
            ):
                continue
            if (
                path.is_file()
                and (
                    directory != "output/e2e"
                    or path.suffix == ".py"
                    or path.name == "expected_detectors.json"
                    or bool({"fixtures", "mappings"} & set(path.parent.parts))
                )
                and path.suffix not in {".pyc"}
            ):
                paths.append(path)
    paths.extend(
        root / name
        for name in (
            ".gitattributes",
            ".gitignore",
            "pyproject.toml",
            "requirements.lock",
            "requirements-browser.lock",
            "MANIFEST.in",
        )
        if (root / name).exists()
    )
    entries = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths)
    }
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


def receipt_is_current(receipt: dict, fingerprint: str) -> bool:
    return (
        receipt.get("exit_code") == 0
        and receipt.get("source_before") == fingerprint
        and receipt.get("source_after") == fingerprint
        and bool(receipt.get("command"))
    )
