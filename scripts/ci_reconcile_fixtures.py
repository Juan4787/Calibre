#!/usr/bin/env python3
"""Validates invariants (INV-01..INV-29) and cross-channel bundle reconciliation on official fixtures.

Used in Tier 2 (Full CI) to ensure no release or pull request can pass without proving
deterministic audit integrity, invariant satisfaction, and lossless XLSX/JSON/HTML export.
"""

import io
import sys
import tempfile
import zipfile
from pathlib import Path

from freight_audit.engine import audit
from freight_audit.project import load_project
from freight_audit.reporting import bundle_bytes
from freight_audit.storage import Store

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_FIXTURES = [
    ROOT / "fixtures/project.json",
    ROOT / "fixtures/second-client/project.json",
]


def run_check() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from qa.invariants import check_run
    from qa.reconcile import reconcile

    all_ok = True
    for proj_path in OFFICIAL_FIXTURES:
        print(f"[*] Validating official project fixture: {proj_path.relative_to(ROOT)}")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            store = Store(p / "audit.sqlite")
            dataset, _ = load_project(proj_path, store)
            result = audit(dataset)
            run_id = store.save(dataset, result)
            run = store.load(run_id)

            # 1. Check invariants INV-01 .. INV-29
            inv_errors = check_run(run, require_provenance=True, verify_hashes=True)
            if inv_errors:
                print(f"[-] FAILED invariants for {proj_path.name}: {inv_errors}")
                all_ok = False
            else:
                print("    [✓] Invariants INV-01..INV-29 satisfied (0 violations).")

            # 2. Export portable bundle and test cross-channel reconciliation
            data = bundle_bytes(store, run_id)
            bundle_dir = p / "bundle"
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(bundle_dir)

            rec_result = reconcile(bundle_dir)
            if rec_result.get("errors"):
                print(f"[-] FAILED reconciliation for {proj_path.name}: {rec_result['errors']}")
                all_ok = False
            else:
                print("    [✓] Multichannel reconciliation clean (JSON, XLSX, HTML match exact).")

    if all_ok:
        print("\n[✓] Tier 2 Fixtures Check: All official fixtures passed invariants and reconciliation.")
        return 0
    else:
        print("\n[X] Tier 2 Fixtures Check: One or more fixtures failed invariants or reconciliation.")
        return 1


if __name__ == "__main__":
    sys.exit(run_check())
