"""Run from the repo root after verify.sh; check installed artifacts, not clean dependencies."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path.cwd()
reports = []
for filename in ("freight_audit-0.1.1-py3-none-any.whl", "freight_audit-0.1.1.tar.gz"):
    artifact = root / "dist" / filename
    with tempfile.TemporaryDirectory(prefix="calibre-onr001-installed-") as td:
        work = Path(td)
        target = work / "installed"
        install = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--no-build-isolation",
                "--target",
                str(target),
                str(artifact),
            ],
            cwd=work,
            capture_output=True,
            text=True,
            check=True,
        )
        environment = {**os.environ, "PYTHONPATH": str(target)}
        smoke = subprocess.run(
            [
                sys.executable,
                str(root / "scripts/smoke_wheel.py"),
                "--installed-root",
                str(target),
                "--fixtures-root",
                str(root / "fixtures"),
            ],
            cwd=work,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        compared = []
        for source in sorted((root / "src/freight_audit").rglob("*")):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            relative = source.relative_to(root / "src")
            assert (target / relative).read_bytes() == source.read_bytes(), relative
            compared.append(str(relative))
        probe = subprocess.run(
            [
                sys.executable,
                "-c",
                """
import json, pathlib, sys
import freight_audit
from freight_audit.engine import audit, matching_preflight
from freight_audit.models import Dataset
assert pathlib.Path(freight_audit.__file__).is_relative_to(sys.argv[1])
assert freight_audit.ENGINE_VERSION == '0.1.1'
saved = json.loads(pathlib.Path(sys.argv[2]).read_text())
dataset = Dataset.model_validate(saved['snapshot'])
assert matching_preflight(dataset)['total_conflicts'] == 1
result = audit(dataset).model_dump(mode='json')
assert result == saved['result']
print(json.dumps({'engine_version': freight_audit.ENGINE_VERSION, 'installed_result_equal': True}))
""",
                str(target),
                str(root / "output/onr-001-fix/browser-reviewed/onr001-audit.json"),
            ],
            cwd=work,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        reports.append(
            {
                "artifact": str(artifact.relative_to(root)),
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "installed_product_files_compared": compared,
                "install_exit_code": install.returncode,
                "smoke_exit_code": smoke.returncode,
                "smoke_stdout": smoke.stdout,
                "onr001_probe": json.loads(probe.stdout),
            }
        )
print(
    json.dumps(
        {
            "scope": "wheel and sdist installed outside checkout; dependencies reused from current .venv, no clean lock/platform certification",
            "artifacts": reports,
        },
        indent=2,
    )
)
