#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/ruff check src tests scripts
.venv/bin/ruff format --check src tests scripts
.venv/bin/mypy src
node --check src/freight_audit/static/app.js
.venv/bin/pytest -q
.venv/bin/python -m compileall -q src
.venv/bin/python -m build
