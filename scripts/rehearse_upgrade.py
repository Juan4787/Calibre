#!/usr/bin/env python3
"""Real Linux/systemd upgrade rehearsal with fictional data in a NEW isolated root.

Never point this script at an existing installation. Services use a unique name
and a free loopback port. Keep private logs; publish only the compact receipt.
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-wheel", type=Path, required=True)
    parser.add_argument("--new-wheel", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists():
        parser.error("Use a NEW root; never operate on an existing installation")
    name = "calibre-rehearsal-" + str(os.getpid()) + ".service"
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]
    base = [
        sys.executable,
        str(ROOT / "scripts/install_local.py"),
        "--root",
        str(root),
        "--service-name",
        name,
    ]
    events = []

    def install(*arguments, expected=0):
        result = subprocess.run([*base, *map(str, arguments)], capture_output=True, text=True)
        (root.parent / (name + f"-{len(events)}.log")).write_text(result.stdout + result.stderr)
        events.append({"action": str(arguments[0]), "exit": result.returncode})
        assert (result.returncode == 0) == (expected == 0), (result.stdout + result.stderr)[-3000:]

    def client():
        connection = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60)
        connection.headers["X-Freight-Local"] = connection.get("/api/session").json()["token"]
        return connection

    def recorded(connection, workspace):
        listed = connection.get("/api/runs", headers={"X-Freight-Workspace": workspace})
        listed.raise_for_status()
        return [{key: row[key] for key in ("id", "input_hash", "result_hash")} for row in listed.json()]

    try:
        install("--wheel", args.old_wheel.resolve(), "--activate", "--port", port)
        with client() as connection:
            old_health = connection.get("/api/health").json()
            spaces = ["main"]
            for i in range(3):
                response = connection.post("/api/workspaces", json={"name": f"Ficticio {i}"})
                response.raise_for_status()
                spaces.append(response.json()["id"])
            for workspace in spaces:
                response = connection.post("/api/demo", headers={"X-Freight-Workspace": workspace})
                response.raise_for_status()
            before = {space: recorded(connection, space) for space in spaces}
        install("--wheel", args.new_wheel.resolve(), "--activate", "--port", port)
        with client() as connection:
            new_health = connection.get("/api/health").json()
            assert old_health["engine_version"] != new_health["engine_version"]
            assert before == {space: recorded(connection, space) for space in spaces}
            response = connection.post("/api/demo")
            response.raise_for_status()
            later_id = response.json()["run_id"]
            assert later_id not in {r["id"] for r in before["main"]}
            added = connection.post("/api/workspaces", json={"name": "Ficticio posterior"}).json()
        install("--rollback")
        with client() as connection:
            assert connection.get("/api/health").json() == old_health
            assert before == {space: recorded(connection, space) for space in spaces}
        rollback = json.loads((root / "rollback.json").read_text())
        preserved = Path(rollback["preserved_after_upgrade"])
        # Read with the candidate runtime that created the newer data, outside checkout.
        code = "from freight_audit.storage import Store; import sys; assert Store(sys.argv[1]).load(sys.argv[2])['id']==sys.argv[2]"
        subprocess.run(
            [
                str(root / "releases" / new_health["engine_version"] / "bin/python"),
                "-c",
                code,
                str(preserved / "workspaces/default/audit.db"),
                later_id,
            ],
            cwd=root,
            env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
            check=True,
        )
        assert (preserved / Path(added["database"]).relative_to(root)).exists()

        class WrongHealth(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"engine_version":"wrong-listener"}')

            def log_message(self, *_args):
                pass

        # Occupied candidate port: real startup fails; old port/config must return.
        occupied = ThreadingHTTPServer(("127.0.0.1", 0), WrongHealth)
        thread = threading.Thread(target=occupied.serve_forever, daemon=True)
        thread.start()
        try:
            install(
                "--wheel", args.new_wheel.resolve(), "--activate", "--port", occupied.server_port, expected=1
            )
        finally:
            occupied.shutdown()
            occupied.server_close()
            thread.join()
        with client() as connection:
            assert connection.get("/api/health").json() == old_health
            assert before == {space: recorded(connection, space) for space in spaces}
        failed = json.loads((root / "activation-failed.json").read_text())
        assert Path(failed["preserved"]).is_dir()
        assert not (root / "activation-pending.json").exists()
        receipt = {
            "passed": True,
            "old_health": old_health,
            "candidate_health": new_health,
            "databases_before_upgrade": 4,
            "historical_run_identities_unchanged": True,
            "post_upgrade_run_preserved": later_id,
            "post_upgrade_client_preserved": True,
            "explicit_rollback_health": True,
            "occupied_port_automatic_rollback": True,
            "previous_port_restored": True,
            "real_systemd_service": name,
            "events": events,
            "scope": "Fictional data, actual installed wheels and user systemd; not production data or Windows",
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2))
    finally:
        subprocess.run(["systemctl", "--user", "disable", "--now", name], capture_output=True)
        (Path.home() / ".config/systemd/user" / name).unlink(missing_ok=True)
        (Path.home() / ".local/bin" / name.removesuffix(".service")).unlink(missing_ok=True)
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)


if __name__ == "__main__":
    main()
