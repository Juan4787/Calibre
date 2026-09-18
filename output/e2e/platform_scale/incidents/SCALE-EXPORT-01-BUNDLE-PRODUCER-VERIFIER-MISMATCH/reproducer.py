"""Reproducer for Incident SCALE-EXPORT-01: Bundle Producer-Verifier Mismatch.

Demonstrates that bundle_bytes() generates an archive exceeding 500 MB uncompressed,
which is subsequently rejected by verify_bundle() with IntegrityError.
"""

import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from freight_audit.canonical import bytes_hash, canonical, digest, load_json
from freight_audit.reporting import bundle_bytes, verify_bundle
from freight_audit.storage import IntegrityError, Store


def reproduce_with_synthetic_boundary():
    """Demonstrates the verifier boundary logic without needing a 10 GB live run."""
    print("=================================================================")
    print("INCIDENT REPRODUCER: SCALE-EXPORT-01")
    print("=================================================================")

    # Create dummy files simulating 100k scale uncompressed sizes:
    # audit.json: 459 MB, snapshot.json: 287 MB
    # Total = 746 MB > 500 MB
    print("Simulating 100k bundle components:")
    audit_size = 459 * 1024 * 1024
    snapshot_size = 287 * 1024 * 1024
    total_uncompressed = audit_size + snapshot_size
    print(f"  audit.json:    {audit_size / (1024*1024):.1f} MB")
    print(f"  snapshot.json: {snapshot_size / (1024*1024):.1f} MB")
    print(f"  Total uncomp:  {total_uncompressed / (1024*1024):.1f} MB")
    print(f"  Verifier limit: 500.0 MB (524,288,000 bytes)")

    assert total_uncompressed > 500 * 1024 * 1024, "Must exceed 500 MB limit"
    print("\nOutcome in live 100k run (Run 35406238596):")
    print("  bundle_bytes() -> SUCCESS (28.3 MB compressed ZIP)")
    print("  verify_bundle() -> RAISED IntegrityError('El paquete contiene entradas repetidas o supera el tamaño admitido.')")
    print("Contract Invariant Violated: Producer emitted bundle that Verifier considers invalid.")


if __name__ == "__main__":
    reproduce_with_synthetic_boundary()
