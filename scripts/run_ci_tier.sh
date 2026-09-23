#!/usr/bin/env bash
# ==============================================================================
# CALIBRE CI TIER RUNNER
# ==============================================================================
# Executes progressive verification tiers locally or in CI pipelines:
#   pr      - Tier 1: Fast linter, typing, syntax, unit/integration, build (<90s)
#   ci      - Tier 2: Tier 1 + QA_PROFILE=ci (100 ex) + invariants + reconcile (<3m)
#   nightly - Tier 3: QA_PROFILE=nightly (1000 ex) + mutation + fault injection + import adversarial (<8m)
#   release - Tier 4: Clean tree + build + SHA-256 + clean-room wheel install & smoke test (<4m)
# ==============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}:${ROOT_DIR}/src${PYTHONPATH:+:$PYTHONPATH}"

if [ -x "${ROOT_DIR}/.venv/bin/python" ]; then
    PYTHON="${ROOT_DIR}/.venv/bin/python"
    PYTEST="${ROOT_DIR}/.venv/bin/pytest"
    RUFF="${ROOT_DIR}/.venv/bin/ruff"
    MYPY="${ROOT_DIR}/.venv/bin/mypy"
else
    PYTHON="$(command -v python3 || command -v python || true)"
    PYTEST="$(command -v pytest || true)"
    RUFF="$(command -v ruff || true)"
    MYPY="$(command -v mypy || true)"
fi

tier="${1:-pr}"

run_tier_pr() {
    echo "================================================================"
    echo "== TIER 1: PR / PUSH (Fast-checks & Functional Gate)          =="
    echo "================================================================"

    echo "[1/8] Ruff lint check..."
    "$RUFF" check src tests scripts qa

    echo "[2/8] Ruff format check..."
    "$RUFF" format --check src tests scripts qa

    echo "[3/8] Mypy type checking (src)..."
    "$MYPY" src

    echo "[4/8] Mypy type checking (qa & scripts)..."
    "$MYPY" --explicit-package-bases qa scripts/qa.py

    echo "[5/8] Verification matrix sync check..."
    "$PYTHON" scripts/qa.py matrix --check

    echo "[6/8] JavaScript syntax check..."
    node --check src/freight_audit/static/app.js

    echo "[7/8] Pytest full regression suite..."
    "$PYTEST" -q tests/

    echo "[8/8] Python compilation and distribution build..."
    "$PYTHON" -m compileall -q -x '/(isolated_env|__pycache__)/' src output/e2e
    "$PYTHON" -m build

    "$PYTHON" scripts/browser_e2e.py --output-dir "output/playwright/pr-$(date +%s)"

    echo "[✓] TIER 1 PASSED: All fast-checks and functional tests clean."
}

run_tier_ci() {
    echo ""
    echo "================================================================"
    echo "== TIER 2: FULL CI (Deep Semantic & Invariant Verification)   =="
    echo "================================================================"

    echo "[1/2] Hypothesis Property-based testing (QA_PROFILE=ci, 100 ex)..."
    QA_PROFILE=ci "$PYTEST" -q tests/

    echo "[2/2] Official fixtures invariants and multichannel reconciliation..."
    "$PYTHON" scripts/ci_reconcile_fixtures.py

    echo "[✓] TIER 2 PASSED: Invariants and multichannel reconciliation verified."
}

run_tier_nightly() {
    echo "================================================================"
    echo "== TIER 3: NIGHTLY (Exhaustive & Adversarial Defense Sweep)   =="
    echo "================================================================"

    echo "[1/5] Hypothesis intensive fuzzing (QA_PROFILE=nightly, 1000 ex)..."
    QA_PROFILE=nightly "$PYTEST" -q tests/test_qa_infrastructure.py

    echo "[2/5] Semantic mutation suite execution (M01..M10)..."
    "$PYTHON" scripts/qa.py mutate --execute

    echo "[3/5] Directed fault injection detection (33 P0 + 8 P1)..."
    "$PYTHON" output/e2e/fault_injection/run_healthy_controls.py --output-dir output/ci/faults
    "$PYTHON" output/e2e/fault_injection/run_directed_faults.py --output-dir output/ci/faults

    echo "[4/5] Adversarial import edge cases (62 cases)..."
    "$PYTHON" output/e2e/import_adversarial/test_import_adversarial.py --output-dir "output/ci/imports-$(date +%s)"

    echo "[5/5] E2E Chromium Playwright UI & multichannel lifecycle..."
    "$PYTHON" scripts/browser_e2e.py --output-dir "output/playwright/nightly-$(date +%s)"

    echo "[✓] TIER 3 PASSED: All heavy adversarial and defense sweeps clean."
}

run_tier_release() {
    echo "================================================================"
    echo "== TIER 4: RELEASE GATE (Packaged Artifact Certification)     =="
    echo "================================================================"

    echo "[1/5] Verifying clean git working tree..."
    if [ -n "$(git status --porcelain)" ]; then
        echo "[-] ERROR: Working tree is dirty. Release gate requires clean committed HEAD."
        git status --short
        exit 1
    fi
    COMMIT="$(git rev-parse HEAD)"
    echo "    Commit HEAD: $COMMIT"

    # Require checks of this release source, not another workflow's historical result.
    run_tier_pr
    "$PYTHON" scripts/ci_reconcile_fixtures.py

    echo "[2/5] Building distribution artifacts from clean HEAD..."
    rm -rf dist/
    "$PYTHON" -m build

    echo "[3/5] Computing and logging SHA-256 hashes..."
    sha256sum dist/*

    echo "[4/5] Creating isolated clean-room virtualenv in /tmp..."
    TEMP_VENV="/tmp/calibre-release-verify-$$"
    rm -rf "$TEMP_VENV"
    "$PYTHON" -m venv "$TEMP_VENV"
    
    WHEEL_FILE="$(ls "${ROOT_DIR}"/dist/freight_audit-*.whl | head -n 1)"
    echo "    Installing wheel: $WHEEL_FILE into isolated clean-room..."
    "$TEMP_VENV/bin/pip" install -r requirements.lock -r requirements-browser.lock
    "$TEMP_VENV/bin/pip" install --no-deps "$WHEEL_FILE"

    echo "[5/5] Executing smoke test against installed wheel without checkout access..."
    SITE_PACKAGES="$("$TEMP_VENV/bin/python" -c "import site; print(site.getsitepackages()[0])")"
    (
        cd /tmp
        env -u PYTHONPATH "$TEMP_VENV/bin/python" "$ROOT_DIR/scripts/smoke_wheel.py" --installed-root "$SITE_PACKAGES"
    )

    env -u PYTHONPATH "$TEMP_VENV/bin/python" "$ROOT_DIR/scripts/browser_e2e.py" --installed-root "$SITE_PACKAGES" --output-dir "output/playwright/release-$(date +%s)"
    rm -rf "$TEMP_VENV"
    echo "[✓] TIER 4 PASSED: Current wheel smoke and browser regression checks passed in isolated clean-room."
}

case "$tier" in
    pr)
        run_tier_pr
        ;;
    ci)
        run_tier_ci
        ;;
    nightly)
        run_tier_nightly
        ;;
    release)
        run_tier_release
        ;;
    *)
        echo "Usage: $0 {pr|ci|nightly|release}"
        exit 1
        ;;
esac
