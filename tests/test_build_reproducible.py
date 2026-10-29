"""Reproducibility must include bytes while preserving every product member."""

import gzip
import io
import tarfile
import zipfile

from scripts.build_reproducible import normalize
from scripts.verify_delivery import archive_contents


def test_wheel_normalization_removes_timestamps_order_and_preserves_members(tmp_path):
    paths = [tmp_path / f"build-{i}.whl" for i in range(2)]
    members = {"product.py": b"exact product\n", "package.dist-info/RECORD": b"exact record\n"}
    for i, path in enumerate(paths):
        with zipfile.ZipFile(path, "w") as archive:
            for name in list(members)[:: 1 if i else -1]:
                info = zipfile.ZipInfo(name, (2020 + i, 1, 1, 0, 0, 0))
                archive.writestr(info, members[name])
    before = archive_contents(paths[0])
    assert paths[0].read_bytes() != paths[1].read_bytes()
    for path in paths:
        normalize(path, 1700000000)
        assert archive_contents(path) == before
    assert paths[0].read_bytes() == paths[1].read_bytes()


def test_sdist_normalization_removes_owners_headers_and_gzip_metadata(tmp_path):
    paths = [tmp_path / f"build-{i}.tar.gz" for i in range(2)]
    for i, path in enumerate(paths):
        with (
            path.open("wb") as raw,
            gzip.GzipFile(filename=f"host-{i}", mode="wb", fileobj=raw, mtime=1700000000 + i) as compressed,
            tarfile.open(fileobj=compressed, mode="w") as archive,
        ):
            info = tarfile.TarInfo("product/source.py")
            info.size = len(b"exact source\n")
            info.uid = i + 1
            info.mtime = 1700000000 + i
            archive.addfile(info, io.BytesIO(b"exact source\n"))
    before = archive_contents(paths[0])
    assert paths[0].read_bytes() != paths[1].read_bytes()
    for path in paths:
        normalize(path, 1700000000)
        assert archive_contents(path) == before
    assert paths[0].read_bytes() == paths[1].read_bytes()
