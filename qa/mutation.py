"""Small auditable semantic mutation runner. Product worktree is never mutated."""

import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .invariants import read_json

ROOT = Path(__file__).resolve().parents[1]


def causal_assertion_failure(xml, selectors, signal):
    """A killed mutant needs a selected test's expected assertion, not any red run."""
    if xml is None or not signal:
        return False, []
    selected_names = {selector.split("::")[-1].split("[")[0] for selector in selectors}
    cases = [case for case in xml.findall(".//testcase") if case.find("failure") is not None]
    names = [case.get("name", "").split("[")[0] for case in cases]
    bodies = [
        (failure.text or "") + failure.get("message", "")
        for case in cases
        for failure in case.findall("failure")
    ]
    return (
        bool(cases)
        and all(name in selected_names for name in names)
        and all("assert" in body.lower() for body in bodies)
        and any(signal in body for body in bodies)
        and not xml.findall(".//error"),
        names,
    )


def _run_isolated_pytest(report, selectors, isolated, environment, timeout):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *selectors, f"--junitxml={report}"],
        cwd=isolated,
        env=environment,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_mutants(ids, *, execute=False, timeout=60):
    mutants = read_json(ROOT / "qa/mutants.json")
    selected = [m for m in mutants if not ids or m["id"] in ids]
    if ids and set(ids) != {m["id"] for m in selected}:
        raise ValueError("Unknown mutant id")
    outcomes = []
    for mutant in selected:
        original = (ROOT / mutant["path"]).read_text(encoding="utf-8")
        if original.count(mutant["before"]) != 1:
            outcomes.append({"id": mutant["id"], "outcome": "obsolete anchor; not executed"})
            continue
        if not execute:
            outcomes.append(
                {
                    "id": mutant["id"],
                    "outcome": "planned",
                    "selectors": mutant["selectors"],
                    "reason": mutant["reason"],
                }
            )
            continue
        with tempfile.TemporaryDirectory(prefix="freight-qa-mutant-") as name:
            isolated = Path(name)
            for folder in ("src", "tests", "fixtures", "qa"):
                shutil.copytree(
                    ROOT / folder,
                    isolated / folder,
                    ignore=shutil.ignore_patterns("__pycache__", "*.egg-info", "*.pyc"),
                )
            shutil.copy2(ROOT / "pyproject.toml", isolated / "pyproject.toml")
            environment = {
                **os.environ,
                "PYTHONPATH": os.pathsep.join([str(isolated / "src"), str(isolated)]),
                "PYTHONDONTWRITEBYTECODE": "1",
                "QA_PROFILE": "smoke",
            }
            try:
                baseline = _run_isolated_pytest(
                    isolated / "baseline.xml", mutant["selectors"], isolated, environment, timeout
                )
                if baseline.returncode != 0:
                    outcomes.append(
                        {
                            "id": mutant["id"],
                            "outcome": "baseline failed; inconclusive",
                            "output": baseline.stdout[-5000:] + baseline.stderr[-1000:],
                        }
                    )
                    continue
                (isolated / mutant["path"]).write_text(
                    original.replace(mutant["before"], mutant["after"], 1), encoding="utf-8"
                )
                report = isolated / "mutant.xml"
                changed = _run_isolated_pytest(report, mutant["selectors"], isolated, environment, timeout)
                xml = ET.parse(report).getroot() if report.exists() else None
                causal, failed_cases = causal_assertion_failure(
                    xml, mutant["selectors"], mutant["failure_signal"]
                )
                outcome = (
                    "survived"
                    if changed.returncode == 0
                    else "killed"
                    if changed.returncode == 1 and causal
                    else "inconclusive (no expected causal assertion)"
                )
                outcomes.append(
                    {
                        "id": mutant["id"],
                        "outcome": outcome,
                        "selectors": mutant["selectors"],
                        "failure_signal": mutant["failure_signal"],
                        "failed_cases": failed_cases,
                        "output": changed.stdout[-5000:] + changed.stderr[-1000:],
                    }
                )
            except subprocess.TimeoutExpired:
                outcomes.append({"id": mutant["id"], "outcome": "timeout; inconclusive"})
    return outcomes
