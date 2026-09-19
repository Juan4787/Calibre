"""Comprehensive test suite for freight-audit-bundle/v1 and v2 contracts.

Validates the 13 required scenarios:
1. Bundle v1 histórico congelado sigue verificando.
2. v1 snapshot alterado -> FAIL.
3. v1 snapshot ausente -> FAIL.
4. v2 estándar -> PASS.
5. v2 audit.snapshot alterado -> FAIL.
6. v2 source alterado/faltante -> FAIL.
7. v2 cadena de decisiones alterada -> FAIL.
8. Versión v3 -> FAIL.
9. Tamaño apenas debajo de límite -> producer PASS + verifier PASS.
10. Tamaño apenas encima -> producer rechaza ANTES de emitir bundle con ReportLimitError.
11. qa/reconcile funciona con v1.
12. qa/reconcile funciona con v2.
13. XLSX omitido por ReportLimitError + advertencia -> v2 sigue PASS.
"""

import io
import zipfile

import pytest

from freight_audit.canonical import canonical, load_json
from freight_audit.engine import audit
from freight_audit.models import Decision
from freight_audit.reporting import (
    ReportLimitError,
    bundle_bytes,
    verify_bundle,
)
from freight_audit.storage import IntegrityError, Store
from qa.reconcile import reconcile


def create_test_run(tmp_path, make_dataset):
    store = Store(tmp_path / "test.db")
    doc_content = b"sample original document content"
    doc_hash = store.put_source(doc_content)
    dataset = make_dataset(lambda raw: raw.update({"documents": {doc_hash: "doc.txt"}}))
    run_id = store.save(dataset, audit(dataset))
    return store, run_id


def test_1_bundle_v1_historic_verifies(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v1_bundle = bundle_bytes(store, run_id, format="freight-audit-bundle/v1")
    with zipfile.ZipFile(io.BytesIO(v1_bundle)) as archive:
        manifest = load_json(archive.read("manifest.json"))
        assert manifest["format"] == "freight-audit-bundle/v1"
        assert "snapshot.json" in archive.namelist()
    verified = verify_bundle(v1_bundle)
    assert verified["id"] == run_id


def test_2_bundle_v1_snapshot_tampered_fails(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v1_bundle = bundle_bytes(store, run_id, format="freight-audit-bundle/v1")
    original = zipfile.ZipFile(io.BytesIO(v1_bundle))
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as modified:
        for name in original.namelist():
            modified.writestr(name, b'{"tampered": true}' if name == "snapshot.json" else original.read(name))
    with pytest.raises(IntegrityError):
        verify_bundle(output.getvalue())


def test_3_bundle_v1_snapshot_missing_fails(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v1_bundle = bundle_bytes(store, run_id, format="freight-audit-bundle/v1")
    original = zipfile.ZipFile(io.BytesIO(v1_bundle))
    manifest = load_json(original.read("manifest.json"))
    del manifest["files"]["snapshot.json"]
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as modified:
        for name in original.namelist():
            if name == "snapshot.json":
                continue
            elif name == "manifest.json":
                modified.writestr(name, canonical(manifest).encode())
            else:
                modified.writestr(name, original.read(name))
    with pytest.raises(IntegrityError, match="snapshot.json"):
        verify_bundle(output.getvalue())


def test_4_bundle_v2_standard_passes(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v2_bundle = bundle_bytes(store, run_id)  # Default format is v2
    with zipfile.ZipFile(io.BytesIO(v2_bundle)) as archive:
        manifest = load_json(archive.read("manifest.json"))
        assert manifest["format"] == "freight-audit-bundle/v2"
        assert "snapshot.json" not in archive.namelist()
        assert "audit.json" in archive.namelist()
        assert "manifest.json" in archive.namelist()
    verified = verify_bundle(v2_bundle)
    assert verified["id"] == run_id


def test_5_bundle_v2_audit_snapshot_tampered_fails(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v2_bundle = bundle_bytes(store, run_id)
    original = zipfile.ZipFile(io.BytesIO(v2_bundle))
    audit_data = load_json(original.read("audit.json"))
    audit_data["snapshot"]["label"] = "Tampered Label"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as modified:
        for name in original.namelist():
            if name == "audit.json":
                modified.writestr(name, canonical(audit_data).encode())
            else:
                modified.writestr(name, original.read(name))
    with pytest.raises(IntegrityError):
        verify_bundle(output.getvalue())


def test_6_bundle_v2_source_tampered_or_missing_fails(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v2_bundle = bundle_bytes(store, run_id)
    original = zipfile.ZipFile(io.BytesIO(v2_bundle))
    source_names = [n for n in original.namelist() if n.startswith("sources/")]
    assert source_names, "Bundle must contain sources"
    src_target = source_names[0]

    # Tampered source
    out_tampered = io.BytesIO()
    with zipfile.ZipFile(out_tampered, "w") as modified:
        for name in original.namelist():
            modified.writestr(name, b"tampered content" if name == src_target else original.read(name))
    with pytest.raises(IntegrityError):
        verify_bundle(out_tampered.getvalue())

    # Missing source
    out_missing = io.BytesIO()
    with zipfile.ZipFile(out_missing, "w") as modified:
        for name in original.namelist():
            if name != src_target:
                modified.writestr(name, original.read(name))
    with pytest.raises(IntegrityError):
        verify_bundle(out_missing.getvalue())


def test_7_bundle_v2_decision_tampered_fails(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    run_loaded = store.load(run_id)
    finding_id = run_loaded["result"]["findings"][0]["id"]
    store.add_decision(
        run_id,
        Decision(
            finding_id=finding_id,
            action="APPROVED",
            actor="Auditor QA",
            note="Conforme",
            known_to_client=True,
            review_minutes=5,
        ),
    )
    v2_bundle = bundle_bytes(store, run_id)
    original = zipfile.ZipFile(io.BytesIO(v2_bundle))
    audit_data = load_json(original.read("audit.json"))
    # Tamper decision action
    audit_data["decisions"][0]["payload"]["action"] = "REJECTED"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as modified:
        for name in original.namelist():
            if name == "audit.json":
                modified.writestr(name, canonical(audit_data).encode())
            else:
                modified.writestr(name, original.read(name))
    with pytest.raises(IntegrityError):
        verify_bundle(output.getvalue())


def test_8_bundle_v3_unknown_version_fails(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v2_bundle = bundle_bytes(store, run_id)
    original = zipfile.ZipFile(io.BytesIO(v2_bundle))
    manifest = load_json(original.read("manifest.json"))
    manifest["format"] = "freight-audit-bundle/v3"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as modified:
        for name in original.namelist():
            if name == "manifest.json":
                modified.writestr(name, canonical(manifest).encode())
            else:
                modified.writestr(name, original.read(name))
    with pytest.raises(IntegrityError, match="no admitido"):
        verify_bundle(output.getvalue())


def test_9_size_just_under_limit_passes(tmp_path, make_dataset, monkeypatch):
    store, run_id = create_test_run(tmp_path, make_dataset)
    # First get natural size
    natural_bundle = bundle_bytes(store, run_id)
    with zipfile.ZipFile(io.BytesIO(natural_bundle)) as z:
        uncompressed_sum = sum(i.file_size for i in z.infolist())

    # Set limit slightly above uncompressed_sum
    monkeypatch.setattr("freight_audit.reporting.MAX_BUNDLE_UNCOMPRESSED_BYTES", uncompressed_sum + 100)
    bundle = bundle_bytes(store, run_id)
    verified = verify_bundle(bundle)
    assert verified["id"] == run_id


def test_10_size_just_over_limit_producer_refuses(tmp_path, make_dataset, monkeypatch):
    store, run_id = create_test_run(tmp_path, make_dataset)
    natural_bundle = bundle_bytes(store, run_id)
    with zipfile.ZipFile(io.BytesIO(natural_bundle)) as z:
        uncompressed_sum = sum(i.file_size for i in z.infolist())

    # Set limit slightly below uncompressed_sum
    monkeypatch.setattr("freight_audit.reporting.MAX_BUNDLE_UNCOMPRESSED_BYTES", uncompressed_sum - 100)
    with pytest.raises(ReportLimitError, match="supera el límite"):
        bundle_bytes(store, run_id)


def test_11_qa_reconcile_with_v1(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v1_bundle = bundle_bytes(store, run_id, format="freight-audit-bundle/v1")
    bundle_dir = tmp_path / "v1_extracted"
    bundle_dir.mkdir()
    with zipfile.ZipFile(io.BytesIO(v1_bundle)) as z:
        z.extractall(bundle_dir)
    res = reconcile(bundle_dir)
    assert res["errors"] == [], f"Reconcile v1 failed with errors: {res['errors']}"


def test_12_qa_reconcile_with_v2(tmp_path, make_dataset):
    store, run_id = create_test_run(tmp_path, make_dataset)
    v2_bundle = bundle_bytes(store, run_id, format="freight-audit-bundle/v2")
    bundle_dir = tmp_path / "v2_extracted"
    bundle_dir.mkdir()
    with zipfile.ZipFile(io.BytesIO(v2_bundle)) as z:
        z.extractall(bundle_dir)
    res = reconcile(bundle_dir)
    assert res["errors"] == [], f"Reconcile v2 failed with errors: {res['errors']}"


def test_13_xlsx_omitted_by_report_limit_v2_passes(tmp_path, make_dataset, monkeypatch):
    store, run_id = create_test_run(tmp_path, make_dataset)
    monkeypatch.setattr("freight_audit.reporting.MAX_XLSX_ROWS", 2)
    bundle = bundle_bytes(store, run_id)
    with zipfile.ZipFile(io.BytesIO(bundle)) as z:
        assert "auditoria.xlsx" not in z.namelist()
        assert "ADVERTENCIA_EXPORTACION.txt" in z.namelist()
    verified = verify_bundle(bundle)
    assert verified["id"] == run_id
