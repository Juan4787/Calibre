#!/usr/bin/env python3
"""Run one check sequentially and preserve exit status, log and exact source identity."""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qa.evidence import source_digest  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("A command is required")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    before = source_digest(ROOT)
    start = time.time()
    log = args.out.with_suffix(".log")
    with log.open("wb") as output:
        proc = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, check=False)
    after = source_digest(ROOT)
    result = {
        "command": command,
        "exit_code": proc.returncode,
        "source_before": before,
        "source_after": after,
        "platform": platform.platform(),
        "python": sys.version,
        "started_at_unix": start,
        "elapsed_seconds": round(time.time() - start, 3),
        "log": str(log),
        "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return proc.returncode if before == after else 2


if __name__ == "__main__":
    sys.exit(main())
