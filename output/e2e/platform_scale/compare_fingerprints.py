#!/usr/bin/env python3
"""Cross-Platform Semantic Fingerprint Comparison Tool.

Compares semantic fingerprints produced by Linux and Windows runs.
Verifies economic parity, finding identity, status, differences,
currencies, counts, and reasons.
Excludes platform-specific environmental metadata.
Outputs reconciliation.json and exits 0 on parity, 1 on divergence.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path


def load_fingerprint(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Fingerprint file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def compare_runs(linux_runs: list[dict], windows_runs: list[dict]) -> tuple[bool, list[str], dict]:
    divergences = []
    details = []

    linux_by_label = {r["dataset_label"]: r for r in linux_runs}
    windows_by_label = {r["dataset_label"]: r for r in windows_runs}

    all_labels = sorted(set(linux_by_label.keys()) | set(windows_by_label.keys()))

    for label in all_labels:
        run_record = {
            "dataset_label": label,
            "status": "PARITY",
            "divergences": [],
        }

        if label not in linux_by_label:
            err = f"Dataset '{label}' missing in Linux fingerprint"
            divergences.append(err)
            run_record["status"] = "DIVERGENCE"
            run_record["divergences"].append(err)
            details.append(run_record)
            continue

        if label not in windows_by_label:
            err = f"Dataset '{label}' missing in Windows fingerprint"
            divergences.append(err)
            run_record["status"] = "DIVERGENCE"
            run_record["divergences"].append(err)
            details.append(run_record)
            continue

        l_run = linux_by_label[label]
        w_run = windows_by_label[label]

        # Compare counts
        l_counts = l_run.get("counts", {})
        w_counts = w_run.get("counts", {})
        if l_counts != w_counts:
            err = f"Counts mismatch in '{label}': Linux={l_counts} vs Windows={w_counts}"
            divergences.append(err)
            run_record["divergences"].append(err)

        # Compare currencies summary
        l_curr = l_run.get("currencies", {})
        w_curr = w_run.get("currencies", {})
        if l_curr != w_curr:
            err = f"Currency summaries mismatch in '{label}': Linux={l_curr} vs Windows={w_curr}"
            divergences.append(err)
            run_record["divergences"].append(err)

        # Compare findings
        l_findings = l_run.get("findings", [])
        w_findings = w_run.get("findings", [])

        if len(l_findings) != len(w_findings):
            err = f"Finding count mismatch in '{label}': Linux has {len(l_findings)} findings, Windows has {len(w_findings)}"
            divergences.append(err)
            run_record["divergences"].append(err)

        # Index findings by a canonical key: (currency, rule, sorted charge_ids, sorted shipment_ids)
        def fkey(f: dict) -> tuple:
            return (
                f.get("currency") or "",
                f.get("rule") or "",
                tuple(f.get("charge_ids", [])),
                tuple(f.get("shipment_ids", [])),
            )

        l_fdict = {fkey(f): f for f in l_findings}
        w_fdict = {fkey(f): f for f in w_findings}

        all_fkeys = sorted(set(l_fdict.keys()) | set(w_fdict.keys()))
        for k in all_fkeys:
            if k not in l_fdict:
                err = f"Finding {k} present in Windows but missing in Linux for '{label}'"
                divergences.append(err)
                run_record["divergences"].append(err)
                continue
            if k not in w_fdict:
                err = f"Finding {k} present in Linux but missing in Windows for '{label}'"
                divergences.append(err)
                run_record["divergences"].append(err)
                continue

            lf = l_fdict[k]
            wf = w_fdict[k]

            fields_to_check = [
                "status",
                "actual",
                "expected",
                "difference",
                "confirmed_difference",
                "reasons",
                "missing_evidence",
                "issues",
            ]

            for field in fields_to_check:
                if lf.get(field) != wf.get(field):
                    err = (
                        f"Field '{field}' mismatch for finding {k} in '{label}': "
                        f"Linux={lf.get(field)} vs Windows={wf.get(field)}"
                    )
                    divergences.append(err)
                    run_record["divergences"].append(err)

        if run_record["divergences"]:
            run_record["status"] = "DIVERGENCE"

        details.append(run_record)

    is_parity = len(divergences) == 0
    reconciliation = {
        "parity": is_parity,
        "total_datasets_compared": len(all_labels),
        "total_divergences": len(divergences),
        "divergences": divergences,
        "datasets": details,
    }
    return is_parity, divergences, reconciliation


def main():
    parser = argparse.ArgumentParser(description="Cross-Platform Semantic Fingerprint Comparison")
    parser.add_argument(
        "--linux",
        type=Path,
        default=Path("output/e2e/platform_scale/windows/linux-semantic-fingerprint.json"),
        help="Path to Linux semantic fingerprint JSON",
    )
    parser.add_argument(
        "--windows",
        type=Path,
        default=Path("output/e2e/platform_scale/windows/windows-semantic-fingerprint.json"),
        help="Path to Windows semantic fingerprint JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/e2e/platform_scale/windows/reconciliation.json"),
        help="Path to output reconciliation JSON",
    )
    args = parser.parse_args()

    print(f"Loading Linux fingerprint from: {args.linux}")
    linux_fp = load_fingerprint(args.linux)
    print(f"Loading Windows fingerprint from: {args.windows}")
    windows_fp = load_fingerprint(args.windows)

    is_parity, divergences, reconciliation = compare_runs(
        linux_fp.get("runs", []), windows_fp.get("runs", [])
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(reconciliation, indent=2), encoding="utf-8")
    print(f"Reconciliation written to: {args.output}")

    if is_parity:
        print("================================================================")
        print("SEMANTIC PARITY CONFIRMED: Linux and Windows match exactly.")
        print(f"Datasets compared: {reconciliation['total_datasets_compared']}")
        print("================================================================")
        sys.exit(0)
    else:
        print("================================================================")
        print(f"SEMANTIC DIVERGENCE DETECTED! Total issues: {len(divergences)}")
        for d in divergences[:10]:
            print(f"  - {d}")
        if len(divergences) > 10:
            print(f"  ... and {len(divergences) - 10} more.")
        print("================================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
