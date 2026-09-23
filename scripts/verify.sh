#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/ruff check src tests scripts qa
.venv/bin/ruff format --check src tests scripts qa
.venv/bin/mypy src
.venv/bin/mypy --explicit-package-bases qa scripts/qa.py
.venv/bin/python scripts/qa.py matrix --check
node --check src/freight_audit/static/app.js
.venv/bin/pytest -q
.venv/bin/python -m compileall -q -x '/(isolated_env|__pycache__)/' src output/e2e
.venv/bin/python -m build
