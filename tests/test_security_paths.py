"""Adversarial local paths use synthetic witnesses outside the requested output."""

import io
import os
import zipfile
from pathlib import Path

import pytest

from freight_audit.engine import audit
from freight_audit.local_paths import checked_output_path
from freight_audit.reporting import export_run
from freight_audit.storage import IntegrityError, Store


def test_export_rejects_existing_and_redirected_directories(tmp_path, make_dataset):
    store = Store(tmp_path / "data.db")
    dataset = make_dataset()
    run_id = store.save(dataset, audit(dataset))
    outside = tmp_path / "outside"
    outside.mkdir()
    witness = outside / "witness.txt"
    witness.write_bytes(b"unchanged")
    link = tmp_path / "redirect"
    link.symlink_to(outside, target_is_directory=True)

    for destination in (outside, link, link / "new", tmp_path / "reports" / ".." / "other"):
        with pytest.raises(ValueError):
            export_run(store, run_id, destination)
    assert witness.read_bytes() == b"unchanged"
    assert sorted(item.name for item in outside.iterdir()) == ["witness.txt"]

    result = export_run(store, run_id, tmp_path / "reports")
    assert result["run_id"] == run_id
    assert (tmp_path / "reports" / "auditoria.zip").is_file()
    assert not (tmp_path / "reports" / "EXPORTACION_INCOMPLETA.txt").exists()
    with pytest.raises(ValueError):
        export_run(store, run_id, tmp_path / "reports")


def test_foreign_platform_drive_syntax_is_not_a_local_relative_output():
    path = Path(r"C:\audit\outside.db")
    if os.name == "nt":
        assert checked_output_path(path) == path
    else:
        with pytest.raises(ValueError, match="ambigua"):
            checked_output_path(path)


def test_backup_publishes_only_completed_copy_without_overwrite(tmp_path, make_dataset):
    store = Store(tmp_path / "data.db")
    dataset = make_dataset()
    run_id = store.save(dataset, audit(dataset))
    outside = tmp_path / "outside"
    outside.mkdir()
    witness = outside / "witness.db"
    witness.write_bytes(b"unchanged")
    directory_link = tmp_path / "redirect"
    directory_link.symlink_to(outside, target_is_directory=True)
    file_link = tmp_path / "file-link.db"
    file_link.symlink_to(witness)

    for destination in (directory_link / "backup.db", file_link, witness, tmp_path / "x" / ".." / "y.db"):
        with pytest.raises(ValueError):
            store.backup(destination)
    assert witness.read_bytes() == b"unchanged"
    assert not list(tmp_path.glob(".freight-backup-*"))
    assert not list(outside.glob(".freight-backup-*"))

    backup = tmp_path / "backup.db"
    store.backup(backup)
    assert Store(backup).replay(run_id)["identical"]
    original = backup.read_bytes()
    with pytest.raises(ValueError):
        store.backup(backup)
    assert backup.read_bytes() == original
    assert not list(tmp_path.glob(".freight-backup-*"))


def test_export_marks_interrupted_or_invalid_package(tmp_path, make_dataset, monkeypatch):
    store = Store(tmp_path / "data.db")
    dataset = make_dataset()
    run_id = store.save(dataset, audit(dataset))
    witness = tmp_path / "witness.txt"
    witness.write_bytes(b"unchanged")
    package = io.BytesIO()
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("audit.json", b"partial")
        archive.writestr("../witness.txt", b"changed")
    monkeypatch.setattr("freight_audit.reporting.bundle_bytes", lambda *_: package.getvalue())

    output = tmp_path / "partial"
    with pytest.raises(IntegrityError, match="ruta"):
        export_run(store, run_id, output)
    assert witness.read_bytes() == b"unchanged"
    assert (output / "EXPORTACION_INCOMPLETA.txt").is_file()
    assert not (output / "auditoria.zip").exists()
