#!/usr/bin/env python3
"""Tests covering generic P0/P1 backlog requirements (Phase 7).

Specifically covers:
- QA-29: Client catalog and storage cryptographic isolation
- QA-56: Settlement scope boundary and grouping behavior
"""

import tempfile
from pathlib import Path

import pytest

from freight_audit.engine import audit
from freight_audit.project import load_project
from freight_audit.storage import IntegrityError, Store

ROOT = Path(__file__).resolve().parents[1]


def test_qa29_client_catalog_and_storage_isolation():
    """QA-29: Aislamiento entre clientes y catálogos.

    Verifies that executing Client A -> Client B -> Client A across separate
    stores ensures strict cryptographic isolation: no cross-leakage of configurations,
    runs, or source documents between clients.
    """
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        store_a = Store(p / "client_a.sqlite")
        store_b = Store(p / "client_b.sqlite")

        # 1. Load and execute Client A
        ds_a, _ = load_project(ROOT / "fixtures/project.json", store_a)
        run_a1 = store_a.save(ds_a, audit(ds_a))

        # 2. Load and execute Client B in its own Store
        ds_b, _ = load_project(ROOT / "fixtures/second-client/project.json", store_b)
        run_b = store_b.save(ds_b, audit(ds_b))

        # 3. Re-execute Client A on a fresh Store instance connected to DB A
        store_a2 = Store(p / "client_a.sqlite")
        run_a2 = store_a2.save(ds_a, audit(ds_a))

        # Assert strict deterministic equivalence for Client A
        assert run_a1 == run_a2
        load_a1 = store_a.load(run_a1)
        load_a2 = store_a2.load(run_a2)
        assert load_a1["result_hash"] == load_a2["result_hash"]
        assert load_a1["input_hash"] == load_a2["input_hash"]

        # Assert Store A contains zero runs from Store B
        runs_a = store_a.list_runs()
        assert len(runs_a) == 1  # Idempotent save
        assert not any(r["id"] == run_b for r in runs_a)

        # Assert Store B contains zero runs from Store A
        runs_b = store_b.list_runs()
        assert len(runs_b) == 1
        assert not any(r["id"] == run_a1 for r in runs_b)

        # Assert Store B cannot access any source document belonging to Store A
        sources_a = store_a.source_hashes(ds_a)
        assert len(sources_a) > 0
        for sh in sources_a:
            with pytest.raises(IntegrityError):
                store_b.source(sh)


def test_qa56_settlement_scope_and_grouping_behavior():
    """QA-56: Separación de liquidaciones y alcance de obligación.

    Verifies the 6 canonical cases for settlement as an explicit grouping boundary:
    1. Two identical charges in same settlement -> coalesce into 1 finding
    2. Same charges in different settlements -> 2 distinct findings, NOT merged
    3. N:1 consolidation within same settlement -> 1 consolidated finding
    4. 1:N multi-charge within same settlement -> distinct findings per concept
    5. Same shipment/concept across two settlements with different amounts -> 2 findings, one PASS, one FAIL
    6. Mixed dataset with two settlements -> findings and totals reconcile cleanly per settlement
    """
    with tempfile.TemporaryDirectory() as td:
        store = Store(Path(td) / "audit.sqlite")
        ds_b, _ = load_project(ROOT / "fixtures/second-client/project.json", store)
        ds_a, _ = load_project(ROOT / "fixtures/project.json", store)
        c0 = ds_b.charges[
            0
        ]  # matches movements ['M1', 'M2', 'M3'], concept 'movement', amount '194.25', settlement 'INV-EXAMPLE'

        # -------------------------------------------------------------
        # Case 1: Two identical charges in the SAME settlement -> Coalesce
        # -------------------------------------------------------------
        c_same = c0.model_copy(update={"id": "INV-1-DUP", "amount": "194.25"})
        ds1 = ds_b.model_copy(update={"charges": [c0, c_same]})
        res1 = audit(ds1)
        assert len(res1.findings) == 1
        f1 = res1.findings[0]
        assert set(f1.charge_ids) == {c0.id, "INV-1-DUP"}
        assert f1.actual == "388.5"  # Coalesced

        # -------------------------------------------------------------
        # Case 2: Same charges in DIFFERENT settlements -> 2 distinct findings
        # -------------------------------------------------------------
        c_diff = c0.model_copy(update={"id": "INV-1-DIFF", "settlement": "INV-PERIOD-2", "amount": "194.25"})
        ds2 = ds_b.model_copy(update={"charges": [c0, c_diff]})
        res2 = audit(ds2)
        assert len(res2.findings) == 2, "Must produce 2 independent findings across settlement boundary"
        f2_a = next(f for f in res2.findings if c0.id in f.charge_ids)
        f2_b = next(f for f in res2.findings if "INV-1-DIFF" in f.charge_ids)
        assert f2_a.actual == "194.25"
        assert f2_b.actual == "194.25"
        assert f2_a.id != f2_b.id

        # -------------------------------------------------------------
        # Case 3: N:1 consolidation within the SAME settlement -> 1 finding
        # -------------------------------------------------------------
        ds3 = ds_b.model_copy(update={"charges": [c0]})
        res3 = audit(ds3)
        assert len(res3.findings) == 1
        f3 = res3.findings[0]
        assert f3.shipment_ids == ["M1", "M2", "M3"]
        assert f3.charge_ids == [c0.id]
        assert f3.status == "PASS"

        # -------------------------------------------------------------
        # Case 4: 1:N multi-charge within the SAME settlement -> 2 findings
        # -------------------------------------------------------------
        c_a0 = ds_a.charges[0]  # agreement A, shipment S-001, concept 'base', settlement 'L1'
        c_a_wait = c_a0.model_copy(update={"id": "C-WAIT-01", "concept": "wait", "amount": "50"})
        ds4 = ds_a.model_copy(update={"charges": [c_a0, c_a_wait], "coverage": {}})
        res4 = audit(ds4)
        assert len(res4.findings) == 2
        concepts = {f.concept for f in res4.findings}
        assert concepts == {"base", "wait"}

        # -------------------------------------------------------------
        # Case 5: Same shipment/concept across two settlements with different amounts
        # -------------------------------------------------------------
        c_jan = c0.model_copy(update={"id": "INV-JAN", "settlement": "LIQ-JAN", "amount": "194.25"})
        c_feb = c0.model_copy(update={"id": "INV-FEB", "settlement": "LIQ-FEB", "amount": "250"})
        ds5 = ds_b.model_copy(update={"charges": [c_jan, c_feb]})
        res5 = audit(ds5)
        assert len(res5.findings) == 2
        f_jan = next(f for f in res5.findings if "INV-JAN" in f.charge_ids)
        f_feb = next(f for f in res5.findings if "INV-FEB" in f.charge_ids)
        assert f_jan.status == "PASS"
        assert f_jan.actual == "194.25"
        assert f_jan.difference == "0"
        assert f_feb.status == "FAIL"
        assert f_feb.actual == "250"
        assert f_feb.difference == "55.75"
        assert f_feb.confirmed_difference == "55.75"

        # -------------------------------------------------------------
        # Case 6: Mixed dataset with two settlements reconciled per settlement
        # -------------------------------------------------------------
        # LIQ-A: M1..M3 (194.25 PASS), M4..M6 (overcharge 250 vs expected 194.25 -> FAIL +55.75)
        # LIQ-B: M1..M3 (undercharge 150 vs expected 194.25 -> FAIL -44.25), M4..M6 (194.25 PASS)
        c_a1 = ds_b.charges[0].model_copy(update={"id": "CH-A1", "settlement": "LIQ-A", "amount": "194.25"})
        c_a2 = ds_b.charges[1].model_copy(update={"id": "CH-A2", "settlement": "LIQ-A", "amount": "250"})
        c_b1 = ds_b.charges[0].model_copy(update={"id": "CH-B1", "settlement": "LIQ-B", "amount": "150"})
        c_b2 = ds_b.charges[1].model_copy(update={"id": "CH-B2", "settlement": "LIQ-B", "amount": "194.25"})
        ds6 = ds_b.model_copy(update={"charges": [c_a1, c_a2, c_b1, c_b2]})
        res6 = audit(ds6)
        assert len(res6.findings) == 4

        f_by_cid = {f.charge_ids[0]: f for f in res6.findings}
        assert f_by_cid["CH-A1"].status == "PASS"
        assert f_by_cid["CH-A2"].status == "FAIL"
        assert f_by_cid["CH-A2"].confirmed_difference == "55.75"
        assert f_by_cid["CH-B1"].status == "FAIL"
        assert f_by_cid["CH-B1"].confirmed_difference == "-44.25"
        assert f_by_cid["CH-B2"].status == "PASS"

        # Check global currencies summary
        usd_summary = res6.summary["currencies"]["USD"]
        assert usd_summary["actual"] == "788.5"  # 194.25 + 250 + 150 + 194.25
        assert usd_summary["confirmed_net_difference"] == "11.5"  # +55.75 - 44.25
        assert usd_summary["confirmed_overcharge"] == "55.75"
        assert usd_summary["confirmed_undercharge"] == "-44.25"
