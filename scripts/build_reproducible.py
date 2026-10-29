#!/usr/bin/env python3
"""Build with locked local tools and normalize archive metadata without changing members."""

import argparse
import gzip
import os
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path


def normalize(path: Path, epoch: int) -> None:
    if not 315532800 <= epoch <= 4354819198:
        raise ValueError("SOURCE_DATE_EPOCH must fit the ZIP timestamp range (1980..2107)")
    with tempfile.TemporaryDirectory(prefix="calibre-build-metadata-", dir=path.parent) as directory:
        target = Path(directory) / path.name
        if path.suffix == ".whl":
            with (
                zipfile.ZipFile(path) as source,
                zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output,
            ):
                for name in sorted(source.namelist()):
                    member = zipfile.ZipInfo(name, time.gmtime(epoch)[:6])
                    member.create_system = 3
                    member.external_attr = (0o40755 if name.endswith("/") else 0o100644) << 16
                    member.compress_type = zipfile.ZIP_DEFLATED
                    output.writestr(member, source.read(name), compresslevel=9)
        else:
            with (
                tarfile.open(path, "r:gz") as source,
                target.open("wb") as raw,
                gzip.GzipFile(
                    filename="", mode="wb", fileobj=raw, mtime=epoch, compresslevel=9
                ) as compressed,
                tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as output,
            ):
                for member in sorted(source.getmembers(), key=lambda item: item.name):
                    member.uid = member.gid = 0
                    member.uname = member.gname = ""
                    member.mtime = epoch
                    member.pax_headers = {}
                    member.mode = 0o755 if member.isdir() else 0o644
                    if member.isfile():
                        with source.extractfile(member) as contents:
                            output.addfile(member, contents)
                    else:
                        output.addfile(member)
        target.replace(path)


def build(epoch: int, out: Path) -> None:
    environment = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    environment["SOURCE_DATE_EPOCH"] = str(epoch)
    subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(out)], env=environment, check=True
    )
    artifacts = list(out.glob("freight_audit-*.whl")) + list(out.glob("freight_audit-*.tar.gz"))
    if len(artifacts) != 2:
        raise ValueError("Build into a new directory; exactly one wheel and one sdist are required")
    for artifact in artifacts:
        normalize(artifact, epoch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--out", type=Path, default=Path("dist"))
    args = parser.parse_args()
    build(args.epoch, args.out)
