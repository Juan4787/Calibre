#!/usr/bin/env python3
"""Compare complete, nonempty platform evidence; missing proof blocks the gate."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from qa.gates import fingerprint_errors, platform_passed


def compare_runs(linux_runs, windows_runs):
    errors = []
    indexed = []
    for name, runs in (("Linux", linux_runs), ("Windows", windows_runs)):
        labels = [r.get("dataset_label") for r in runs]
        if not runs or any(not label for label in labels) or len(set(labels)) != len(labels):
            errors.append(f"{name}: empty runs or missing/duplicate labels")
        for run in runs:
            ids = [f.get("id") for f in run.get("findings", [])]
            if not ids or any(not identifier for identifier in ids) or len(set(ids)) != len(ids):
                errors.append(f"{name}: empty findings or missing/duplicate identities")
        indexed.append({r.get("dataset_label"): r for r in runs})
    left, right = indexed
    for label in sorted(set(left) | set(right)):
        # Compare all identities, traces and source/engine hashes, not a monetary subset.
        if left.get(label) != right.get(label):
            errors.append(f"Dataset {label}: full semantic fingerprint differs")
    return not errors, errors, {
        "parity": not errors,
        "total_datasets_compared": len(set(left) & set(right)),
        "total_divergences": len(errors),
        "divergences": errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    base = ROOT / "output/e2e/platform_scale/windows"
    parser.add_argument("--linux", type=Path, default=base / "linux-semantic-fingerprint.json")
    parser.add_argument("--windows", type=Path, default=base / "windows-semantic-fingerprint.json")
    parser.add_argument("--output", type=Path, default=base / "reconciliation.json")
    args = parser.parse_args()
    fingerprints = []
    errors = []
    for name, path in (("linux", args.linux), ("windows", args.windows)):
        fp = json.loads(path.read_text(encoding="utf-8"))
        errors.extend(fingerprint_errors(fp))
        report = json.loads((path.parent / f"{name}-result.json").read_text(encoding="utf-8"))
        if not platform_passed(report) or report.get("platform", {}).get("system", "").lower() != name:
            errors.append(f"{name}: incomplete/failed cases or wrong actual operating system")
        fingerprints.append(fp)
    _, differences, result = compare_runs(*(fp.get("runs", []) for fp in fingerprints))
    errors.extend(differences)
    result.update(parity=not errors, total_divergences=len(errors), divergences=errors)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["parity"] else 1


if __name__ == "__main__":
    sys.exit(main())
