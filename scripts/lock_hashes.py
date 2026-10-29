#!/usr/bin/env python3
"""Refresh hashes for unchanged exact pins using official PyPI release metadata.

Include every released distribution to preserve the existing platform/Python
selection. pip still checks compatibility and dependency resolution at install.
This records archive identity; it is not a vulnerability assessment.
"""

import argparse
import json
import re
import urllib.request
from pathlib import Path


def refresh(path):
    pins = []
    for line in path.read_text().splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)(.*)", line)
        if match:
            tail = match[3].strip().removesuffix("\\").strip()
            marker = tail if tail.startswith(";") else ""
            pins.append((match[1], match[2], marker))
    if not pins:
        raise ValueError("No exact package pins found")
    lines = [
        "# Exact versions and SHA-256 of ALL distribution files from official PyPI release metadata.",
        "# Regenerate: python3 scripts/lock_hashes.py " + path.name,
        "# Install: python -m pip install --require-hashes -r " + path.name,
    ]
    for name, version, marker in pins:
        url = f"https://pypi.org/pypi/{name}/{version}/json"
        with urllib.request.urlopen(url, timeout=30) as response:
            metadata = json.load(response)
        if metadata["info"]["version"] != version:
            raise ValueError(f"Version mismatch from {url}")
        hashes = sorted({file["digests"]["sha256"] for file in metadata["urls"]})
        if not hashes or any(not re.fullmatch("[0-9a-f]{64}", value) for value in hashes):
            raise ValueError(f"Missing distribution hashes from {url}")
        lines += [f"# {url}", f"{name}=={version}{' ' + marker if marker else ''} \\"]
        lines += [
            f"    --hash=sha256:{value}" + (" \\" if index < len(hashes) - 1 else "")
            for index, value in enumerate(hashes)
        ]
    path.write_text("\n".join(lines) + "\n")
    print(f"Locked {len(pins)} unchanged versions in {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("locks", type=Path, nargs="+")
    for lock in parser.parse_args().locks:
        refresh(lock)
