import argparse
import json
import sys
from pathlib import Path

from .canonical import canonical, digest, load_json
from .engine import audit
from .fixtures import generate, run_demo
from .importing import ImportMapping, import_data
from .models import Agreement, Dataset, Decision
from .project import load_project
from .reporting import export_run, verify_bundle
from .storage import Store, engine_artifact_hash


def main():
    parser = argparse.ArgumentParser(
        prog="freight-audit", description="Auditoría local y determinista. Ningún dato se envía a terceros."
    )
    parser.add_argument("--db", default=".local/audit.db", help="Base SQLite local")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Ejecutar archivos totalmente ficticios")
    demo.add_argument("--fixtures", type=Path, default=Path("fixtures"))
    demo.add_argument("--out", type=Path)
    create = commands.add_parser("generate-fixtures")
    create.add_argument("--out", type=Path, default=Path("fixtures"))
    run_parser = commands.add_parser("run", help="Auditar un proyecto con archivos y mappings")
    run_parser.add_argument("project", type=Path)
    run_parser.add_argument("--out", type=Path)
    normalized = commands.add_parser("audit-json")
    normalized.add_argument("dataset", type=Path)
    normalized.add_argument("--out", type=Path)
    preview = commands.add_parser("preview")
    preview.add_argument("file", type=Path)
    preview.add_argument("--mapping", required=True, type=Path)
    replay = commands.add_parser("replay")
    replay.add_argument("run_id")
    verify = commands.add_parser("verify-bundle")
    verify.add_argument("bundle", type=Path)
    verify.add_argument("--replay", action="store_true")
    export = commands.add_parser("export")
    export.add_argument("run_id")
    export.add_argument("--out", required=True, type=Path)
    decision = commands.add_parser("decide")
    decision.add_argument("run_id")
    decision.add_argument("decision", type=Path)
    backup = commands.add_parser("backup")
    backup.add_argument("destination", type=Path)
    serve = commands.add_parser("serve")
    serve.add_argument("--port", type=int, default=8765)
    schemas = commands.add_parser("schemas")
    schemas.add_argument("--out", type=Path, default=Path("docs/schemas"))
    args = parser.parse_args()
    result: dict = {}
    try:
        if args.command == "generate-fixtures":
            if (args.out / "project.json").exists():
                raise ValueError(
                    "Los fixtures ya existen. Elegir otra carpeta para preservar los originales."
                )
            generate(args.out)
            result = {"fixtures": str(args.out)}
        elif args.command == "schemas":
            args.out.mkdir(parents=True, exist_ok=True)
            schema_models: list[
                tuple[str, type[Dataset] | type[Agreement] | type[ImportMapping] | type[Decision]]
            ] = [
                ("dataset", Dataset),
                ("agreement", Agreement),
                ("mapping", ImportMapping),
                ("decision", Decision),
            ]
            for name, model in schema_models:
                (args.out / f"{name}.schema.json").write_text(
                    json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            result = {"schemas": str(args.out)}
        elif args.command == "serve":
            import uvicorn

            from .server import create_app

            uvicorn.run(create_app(Path(args.db)), host="127.0.0.1", port=args.port, workers=1)
            return
        elif args.command == "preview":
            mapping = ImportMapping.model_validate(load_json(args.mapping.read_bytes()))
            imported = import_data(args.file.read_bytes(), args.file.name, mapping)
            result = {key: value for key, value in imported.items() if key != "records"}
        elif args.command == "verify-bundle":
            run = verify_bundle(args.bundle.read_bytes())
            result = {"run_id": run["id"], "integrity": True}
            if args.replay:
                if run["artifact_hash"] != engine_artifact_hash():
                    raise ValueError(
                        "El paquete corresponde a otro artefacto del motor; usar esa versión para reproducirlo."
                    )
                replayed = audit(Dataset.model_validate(run["snapshot"]))
                if digest(replayed) != run["result_hash"]:
                    raise ValueError("La reproducción difiere del resultado original.")
                result["identical"] = True
        else:
            store = Store(args.db)
            if args.command == "demo":
                result = run_demo(store, args.fixtures)
                if args.out:
                    result["export"] = export_run(store, result["run_id"], args.out)
            elif args.command in {"run", "audit-json"}:
                if args.command == "run":
                    dataset, imports = load_project(args.project, store)
                else:
                    dataset = Dataset.model_validate(load_json(args.dataset.read_bytes()))
                    imports = {}
                computed = audit(dataset)
                run_id = store.save(dataset, computed)
                result = {"run_id": run_id, "summary": computed.summary, "imports": imports}
                if args.out:
                    result["export"] = export_run(store, run_id, args.out)
            elif args.command == "replay":
                result = store.replay(args.run_id)
            elif args.command == "export":
                result = export_run(store, args.run_id, args.out)
            elif args.command == "decide":
                result = store.add_decision(
                    args.run_id, Decision.model_validate(load_json(args.decision.read_bytes()))
                )
            elif args.command == "backup":
                store.backup(args.destination)
                result = {"backup": str(args.destination)}
            else:
                raise ValueError("Comando desconocido.")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError) as exc:
        from pydantic import ValidationError

        if isinstance(exc, ValidationError):
            details = "; ".join(
                ".".join(map(str, error["loc"])) + ": " + error["msg"]
                for error in exc.errors(include_input=False)[:10]
            )
        else:
            details = str(exc)
        print(canonical({"error": details}), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
