#!/usr/bin/env python3
"""Check default dependency closure against official PyPI metadata for Python 3.12.

This read-only network check complements actual pip installs on each platform;
it cannot substitute execution of native wheels or application code.
"""

import json
import sys
import urllib.request
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

if __package__:
    from .verify_delivery import expected_pins
else:
    from verify_delivery import expected_pins


def check(root):
    locks = (root / "requirements.lock").read_text() + "\n" + (root / "requirements-browser.lock").read_text()
    platforms = {}
    for system, platform_name, os_name in (("linux", "Linux", "posix"), ("win32", "Windows", "nt")):
        environment = {
            **default_environment(),
            "sys_platform": system,
            "platform_system": platform_name,
            "os_name": os_name,
            "python_version": "3.12",
            "python_full_version": "3.12.3",
            "extra": "",
        }
        platforms[system] = environment, expected_pins(locks, environment)
    metadata = {}
    for _environment, pins in platforms.values():
        for name, version in pins.items():
            if name not in metadata:
                with urllib.request.urlopen(
                    f"https://pypi.org/pypi/{name}/{version}/json", timeout=30
                ) as response:
                    metadata[name] = json.load(response)
    report = {}
    for system, (environment, pins) in platforms.items():
        errors = []
        edges = 0
        for name in pins:
            for text in metadata[name]["info"]["requires_dist"] or []:
                requirement = Requirement(text)
                if requirement.marker and not requirement.marker.evaluate(environment):
                    continue
                edges += 1
                dependency = canonicalize_name(requirement.name)
                if dependency not in pins or not requirement.specifier.contains(
                    pins[dependency], prereleases=True
                ):
                    errors.append({"from": name, "requirement": text, "locked": pins.get(dependency)})
        report[system] = {"pins": len(pins), "active_dependency_edges": edges, "errors": errors}
    print(
        json.dumps(
            {
                "source": "Official PyPI release metadata, unchanged package versions plus conditional colorama0.4.6",
                "python": "3.12",
                "platforms": report,
            },
            indent=2,
        )
    )
    return all(not value["errors"] for value in report.values())


if __name__ == "__main__":
    sys.exit(0 if check(Path(__file__).resolve().parents[1]) else 1)
