"""Run one workload per process to measure independent peak RSS; no parallel workers."""

import argparse
import cProfile
import json
import platform
import resource
import time
from pathlib import Path

from freight_audit.canonical import digest
from freight_audit.engine import audit
from freight_audit.fixtures import agreement, attr, op, rule, version
from freight_audit.models import Agreement, Charge, Dataset, Shipment, Value
from freight_audit.storage import engine_artifact_hash

parser = argparse.ArgumentParser()
parser.add_argument("--charges", type=int, default=50000)
parser.add_argument("--shipments", type=int, default=10000)
parser.add_argument("--out", type=Path, default=Path("output/benchmark.json"))
parser.add_argument("--profile", type=Path)
args = parser.parse_args()
if args.charges % args.shipments:
    parser.error("charges must be a multiple of shipments")
started = time.perf_counter()
concepts = args.charges // args.shipments
rate = op("lookup", attr("reference"), table="rates")
rules = [rule(f"R{i}", f"concept-{i}", op("mul", attr("weight", "kg"), rate)) for i in range(concepts)]
rows = [
    {"keys": [f"{i:08d}"], "value": {"type": "decimal", "value": "2.5", "unit": "ARS/kg"}}
    for i in range(args.shipments)
]
a = Agreement.model_validate(
    agreement(
        "BENCH",
        "FICTICIO",
        [version("V", rules, tables={"rates": {"kind": "lookup", "rows": rows}})],
        matching={"keys": [{"charge": "reference", "shipment": "reference"}], "cardinality": "one"},
    )
)
attributes = {
    "weight": Value(type="decimal", value="100", unit="kg"),
    "service_date": Value(type="date", value="2026-05-01"),
}
shipments = [
    Shipment(id=f"S{i}", reference=f"{i:08d}", carrier="FICTICIO", attributes=attributes)
    for i in range(args.shipments)
]
charges = [
    Charge(
        id=f"C{i}-{j}",
        settlement="BENCH",
        reference=f"{i:08d}",
        carrier="FICTICIO",
        agreement="BENCH",
        concept=f"concept-{j}",
        amount="250",
        currency="ARS",
    )
    for i in range(args.shipments)
    for j in range(concepts)
]
dataset = Dataset(label="BENCHMARK SINTÉTICO", shipments=shipments, charges=charges, agreements=[a])
generated = time.perf_counter()
baseline_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
profiler = cProfile.Profile() if args.profile else None
if profiler:
    profiler.enable()
result = audit(dataset)
if profiler:
    profiler.disable()
    profiler.dump_stats(args.profile)
audited = time.perf_counter()
result_hash = digest(result)
serialized = time.perf_counter()
peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
assert result.summary["counts"]["PASS"] == args.charges
report = {
    "shipments": args.shipments,
    "charges": args.charges,
    "findings": len(result.findings),
    "lookup_rows": args.shipments,
    "prepare_seconds": round(generated - started, 3),
    "audit_seconds": round(audited - generated, 3),
    "hash_result_seconds": round(serialized - audited, 3),
    "peak_rss_mb": round(peak_rss / 1024, 1),
    "baseline_rss_mb": round(baseline_rss / 1024, 1),
    "result_hash": result_hash,
    "artifact_hash": engine_artifact_hash(),
    "python": platform.python_version(),
    "system": platform.platform(),
    "profiled": bool(profiler),
    "scope": f"Core audit with full traces and {args.shipments}-row lookup; excludes file import, database save, XLSX export and browser.",
}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2), flush=True)
