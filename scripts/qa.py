"""Read-only QA commands except explicit matrix generation and isolated tests/mutants."""

import argparse
import json
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import BadZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="Freight Audit QA: a passing check is not certification")
    commands = parser.add_subparsers(dest="command", required=True)
    matrix = commands.add_parser("matrix")
    matrix.add_argument("--priority", nargs="+", choices=["P0", "P1", "P2", "P3"])
    matrix.add_argument("--ids", nargs="+")
    action = matrix.add_mutually_exclusive_group()
    action.add_argument("--generate", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--run-existing", action="store_true")
    invariants = commands.add_parser("invariants")
    invariants.add_argument("audit_json", type=Path)
    invariants.add_argument("--require-provenance", action="store_true")
    reconcile_parser = commands.add_parser("reconcile")
    reconcile_parser.add_argument("directory", type=Path)
    reconcile_parser.add_argument("--api-run", type=Path)
    reconcile_parser.add_argument("--observed-ui", type=Path)
    impact = commands.add_parser("impact")
    impact.add_argument("--db", type=Path, required=True)
    filters = (
        "engine-artifact",
        "engine-version",
        "feature",
        "currency",
        "agreement",
        "rule",
        "source-type",
        "importer-hash",
    )
    for name in filters:
        impact.add_argument("--" + name)
    mutations = commands.add_parser("mutate")
    mutations.add_argument("--ids", nargs="+")
    mutations.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    code = 0
    from qa.invariants import check_run, read_json

    if args.command == "matrix":
        from qa.catalog import FAMILIES
        from qa.catalog_tools import rendered, validate_catalog

        errors = validate_catalog()
        if args.generate and not errors:
            for name, content in rendered().items():
                (ROOT / name).write_text(content, encoding="utf-8")
        if args.check:
            for name, content in rendered().items():
                path = ROOT / name
                if not path.is_file() or path.read_text(encoding="utf-8") != content:
                    errors.append(f"Generated view stale or missing: {name}")
        if args.ids and not set(args.ids) <= {f["TEST_ID"] for f in FAMILIES}:
            raise ValueError("Unknown TEST_ID")
        selected = [
            r
            for r in FAMILIES
            if (not args.priority or r["PRIORIDAD"] in args.priority)
            and (not args.ids or r["TEST_ID"] in args.ids)
        ]
        # New tooling validates a subset, not every obligation in its family.
        pending = [r["TEST_ID"] for r in selected if r["ESTADO_COBERTURA"] != "completa"]
        selectors = sorted({s for r in selected for s in r["SELECTORES"]})
        if args.run_existing and not errors:
            if not selectors:
                code = 3
            else:
                execution = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", *selectors], cwd=ROOT, check=False
                )
                code = 1 if execution.returncode else 3 if pending else 0
        result = {
            "families": len(selected),
            "selected": [
                {
                    "id": r["TEST_ID"],
                    "priority": r["PRIORIDAD"],
                    "group": r["GRUPO"],
                    "status": r["ESTADO_COBERTURA"],
                    "name": r["NOMBRE"],
                }
                for r in selected
            ],
            "pending_family_coverage": pending,
            "selectors": selectors,
            "errors": errors,
            "certification": False,
        }
        if errors:
            code = 1
    elif args.command == "invariants":
        errors = check_run(read_json(args.audit_json), require_provenance=args.require_provenance)
        result, code = (
            {
                "errors": errors,
                "scope": "Algebraic/structural invariants and recorded hashes; not contract truth or original cell interpretation",
            },
            int(bool(errors)),
        )
    elif args.command == "reconcile":
        from qa.reconcile import reconcile

        result = reconcile(
            args.directory,
            api_run=read_json(args.api_run) if args.api_run else None,
            observed_ui=read_json(args.observed_ui) if args.observed_ui else None,
        )
        code = int(bool(result["errors"]))
    elif args.command == "impact":
        from qa.impact import inventory

        result = inventory(
            args.db,
            {
                name.replace("-", "_"): getattr(args, name.replace("-", "_"))
                for name in filters
                if getattr(args, name.replace("-", "_")) is not None
            },
        )
        code = 3 if any(r["classification"] == "unknown" for r in result["candidates"]) else 0
    else:
        from qa.mutation import run_mutants

        result = {"mutants": run_mutants(args.ids, execute=args.execute), "certification": False}
        required = "killed" if args.execute else "planned"
        code = int(any(r["outcome"] != required for r in result["mutants"]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        IndexError,
        RecursionError,
        OSError,
        sqlite3.DatabaseError,
        BadZipFile,
        ET.ParseError,
    ) as exc:
        print(
            json.dumps(
                {"error": type(exc).__name__, "message": str(exc), "certification": False}, ensure_ascii=False
            )
        )
        sys.exit(2)
