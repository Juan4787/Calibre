"""Full-client backup/rollback faults on disposable SQLite databases only."""

import json
import sqlite3
from pathlib import Path

import pytest

from freight_audit.engine import audit
from freight_audit.storage import Store
from freight_audit.workspaces import Workspaces
from scripts import local_release as release


class Service:
    def __init__(self, root, *, fail=False):
        self.files = [root / "unit.txt", root / "launcher.txt"]
        self.events = []
        self.fail = fail
        for path in self.files:
            path.write_text("previous configuration")

    def stop(self):
        self.events.append("stop")

    def configure(self):
        self.events.append("configure")
        for path in self.files:
            path.write_text("next configuration")

    def reload(self):
        self.events.append("reload")

    def start(self):
        self.events.append("start")

    def probe(self, path):
        self.events.append("probe:" + path.name)
        if self.fail and path.name == "0.3.1":
            raise ValueError("simulated health failure")
        return {"engine_version": path.name}


def installation(tmp_path, make_dataset, monkeypatch):
    root = tmp_path / "installation"
    main = Store(root / "workspaces/default/audit.db")
    workspaces = Workspaces(main)
    clients = [workspaces.create("Cliente ficticio " + str(i)) for i in range(3)]
    stores = [main, *(Store(c["database"]) for c in clients)]
    ids = []
    for store in stores:
        dataset = make_dataset()
        ids.append(store.save(dataset, audit(dataset)))
    old, new = [root / "releases" / v for v in ("0.3.0", "0.3.1")]
    for environment in (old, new):
        (environment / "bin").mkdir(parents=True)
        (environment / "bin/python").write_text("disposable runtime stand-in")
    release.switch(root, old)

    def migrate(_python, paths, _root):
        for path in paths:
            with sqlite3.connect(path) as connection:
                connection.execute("CREATE TABLE new_version_marker (value TEXT)")

    monkeypatch.setattr(release, "migrate", migrate)
    return root, old, new, stores, ids


def test_all_registered_clients_backed_up_and_post_upgrade_runs_preserved(
    tmp_path, make_dataset, monkeypatch
):
    root, old, new, stores, ids = installation(tmp_path, make_dataset, monkeypatch)
    service = Service(root)
    receipt = release.activate(root, new, "fictional-wheel-sha", service=service)
    manifest = json.loads(Path(receipt["backup_manifest"]).read_text())
    assert len(manifest["databases"]) == 4
    assert root.joinpath("current").resolve() == new
    assert service.events == ["stop", "configure", "start", "probe:0.3.1"]
    # Actual new result and new workspace created after upgrade must survive rollback.
    dataset = make_dataset(lambda raw: raw.update(label="Posterior a la actualización"))
    later = stores[1].save(dataset, audit(dataset))
    extra = Workspaces(stores[0]).create("Cliente agregado después")
    result = release.rollback(root, service=service)
    preserved = Path(result["preserved_after_upgrade"])
    assert (root / "current").resolve() == old
    for store, identifier in zip(stores, ids, strict=True):
        assert [r["id"] for r in store.list_runs()] == [identifier]
        with sqlite3.connect(store.path) as connection:
            assert "new_version_marker" not in release.fingerprint(connection)
    later_copy = preserved / stores[1].path.relative_to(root)
    assert Store(later_copy).load(later)["snapshot"]["label"] == dataset.label
    assert (preserved / Path(extra["database"]).relative_to(root)).exists()
    assert Path(extra["database"]).exists()
    assert all(path.read_text() == "previous configuration" for path in service.files)
    assert not (root / "activation-pending.json").exists()


def test_health_failure_restores_every_database_and_service_configuration(
    tmp_path, make_dataset, monkeypatch
):
    root, old, new, stores, ids = installation(tmp_path, make_dataset, monkeypatch)
    service = Service(root, fail=True)
    with pytest.raises(ValueError, match="simulated health"):
        release.activate(root, new, "fictional", service=service)
    assert (root / "current").resolve() == old
    failed = json.loads((root / "activation-failed.json").read_text())
    for store, identifier in zip(stores, ids, strict=True):
        assert store.load(identifier)["id"] == identifier
        with sqlite3.connect(store.path) as connection:
            assert "new_version_marker" not in release.fingerprint(connection)
        with sqlite3.connect(Path(failed["preserved"]) / store.path.relative_to(root)) as connection:
            assert "new_version_marker" in release.fingerprint(connection)
    assert all(path.read_text() == "previous configuration" for path in service.files)
    assert service.events[-1] == "probe:0.3.0"


def test_bad_backup_stops_restore_before_any_active_file_is_changed(tmp_path, make_dataset, monkeypatch):
    root, old, _new, stores, _ids = installation(tmp_path, make_dataset, monkeypatch)
    manifest = release.backup_set(root, "next", old)
    hashes = [release.checksum(store.path) for store in stores]
    bad = Path(manifest["directory"]) / manifest["databases"][-1]["relative"]
    bad.write_bytes(b"altered backup")
    with pytest.raises(ValueError, match="alterado"):
        release.preserve_and_restore(root, manifest)
    assert [release.checksum(store.path) for store in stores] == hashes


def test_missing_registered_client_aborts_before_migration(tmp_path, make_dataset, monkeypatch):
    root, old, new, stores, _ids = installation(tmp_path, make_dataset, monkeypatch)
    stores[-1].path.unlink()
    with pytest.raises(ValueError, match="Falta una base"):
        release.activate(root, new, "fictional")
    assert (root / "current").resolve() == old
    assert not (root / "activation.json").exists()


def test_explicit_recovery_after_interruption_keeps_later_data(tmp_path, make_dataset, monkeypatch):
    root, old, new, stores, _ids = installation(tmp_path, make_dataset, monkeypatch)
    manifest = release.backup_set(root, "0.3.1", old)
    release.atomic_json(root / "activation-pending.json", manifest)
    release.migrate(new / "bin/python", [s.path for s in stores], root)
    release.switch(root, new)
    result = release.recover(root)
    assert (root / "current").resolve() == old
    assert Path(result["preserved_after_interruption"]).is_dir()
    assert not (root / "activation-pending.json").exists()
    for store in stores:
        with sqlite3.connect(store.path) as connection:
            assert "new_version_marker" not in release.fingerprint(connection)


def test_systemd_refuses_another_installations_service(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    unit = Path.home() / ".config/systemd/user/calibre-freight.service"
    unit.parent.mkdir(parents=True)
    unit.write_text('[Service]\nWorkingDirectory="/some/other/installation"\n')
    with pytest.raises(ValueError, match="otra instalación"):
        release.SystemdService(tmp_path / "candidate")


def test_systemd_working_directory_with_spaces_has_no_command_line_quotes(tmp_path, monkeypatch):
    import os
    import shutil
    import subprocess

    if shutil.which("systemd-analyze") is None:
        pytest.skip("systemd parser applies to the Linux installer only")
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    root = tmp_path / "installation with spaces"
    root.mkdir()
    service = release.SystemdService(root, name="calibre-test.service")
    service.configure()
    text = service.unit.read_text()
    assert f"WorkingDirectory={root}\n" in text
    assert "After=default.target" not in text
    assert f'WorkingDirectory="{root}"' not in text
    # The actual local systemd parser is the oracle for its unit grammar.
    runtime = tmp_path / "xdg-runtime"
    runtime.mkdir(mode=0o700)
    environment = {k: v for k, v in os.environ.items() if k != "DBUS_SESSION_BUS_ADDRESS"}
    environment["XDG_RUNTIME_DIR"] = str(runtime)
    verified = subprocess.run(
        ["systemd-analyze", "--user", "verify", str(service.unit)],
        capture_output=True,
        text=True,
        env=environment,
    )
    assert verified.returncode == 0, verified.stderr
    assert release.SystemdService(root, name="calibre-test.service").root == root


def test_stop_of_invalid_unit_without_pid_does_not_mask_original_failure(tmp_path, monkeypatch):
    import subprocess

    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    service = release.SystemdService(tmp_path)
    service.unit.parent.mkdir(parents=True)
    service.unit.write_text("invalid unit")

    def command(*arguments, check=True):
        return subprocess.CompletedProcess(arguments, 5, stdout=b"0\n", stderr=b"invalid unit")

    monkeypatch.setattr(service, "command", command)
    service.stop()
