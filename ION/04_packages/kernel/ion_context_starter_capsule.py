"""Clean context starter capsule for new folders.

This is the canonical "start a new thing" capsule. It is not an agent export,
not a role rehearsal, and not a multi-agent runtime.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_ID = "ion.context_starter_capsule.v1"
READY_VERDICT = "ION_CONTEXT_STARTER_CAPSULE_READY"
STARTER_ROOT = Path("ION/05_context/current/context_starter_capsule")
OPERATOR_FINAL = STARTER_ROOT / "OPERATOR_FINAL"
INTERNAL_REFERENCE = Path("ION/05_context/current/context_starter_capsule_internal_reference")

REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    ".codex/config.toml",
    ".ion/ION_CONTEXT_CAPSULE.yaml",
    ".ion/ACTIVE_CONTEXT_PACKAGE.md",
    ".ion/ROUTE.json",
    ".ion/LONG_HORIZON.json",
    ".ion/HOT_CONTEXT.md",
    ".ion/CONTEXT_PACKAGES.json",
    ".ion/LOADED_REFS.json",
    ".ion/IDENTITY_CARD.md",
    ".ion/MINI.md",
    ".ion/CAPSULE.md",
    ".ion/STATUS.json",
    ".ion/ion_bootstrap.py",
)

EMPTY_CONTEXT_DIRS = (
    ".ion/inbox/.gitkeep",
    ".ion/outbox/.gitkeep",
    ".ion/runs/.gitkeep",
    ".ion/receipts/.gitkeep",
    ".ion/history/.gitkeep",
    ".ion/machine_receipts/.gitkeep",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _status_json(folder: Path | None = None) -> str:
    launch = "codex -C <this-folder>" if folder is None else f"codex -C {folder.resolve()}"
    return json.dumps(
        {
            "schema_id": "ion.context_starter_status.v1",
            "ready": True,
            "missing": [],
            "capsule_kind": "context_starter",
            "launch_command": launch,
            "runtime_claims": {
                "multi_agent_runtime": False,
                "live_agent_dispatch_proven": False,
                "invented_agent_outputs": False,
            },
            "authority": {
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
        },
        indent=2,
        sort_keys=True,
    )


def _readme() -> str:
    return """# ION Context Starter Capsule

This is the clean starter for a new ION-aware folder.

## What This Is

- A single-session context capsule for Codex.
- A local `.ion/` folder with Mini, Capsule, route, active context, status, inbox, outbox, runs, and receipts.
- A way to start fresh without losing the ION boundary rules.

## What This Is Not

- This is not a multi-agent runtime.
- Not an invented agent workflow.
- Not a role rehearsal.
- Not accepted ION state.
- Not production, live execution, secrets, deploy, push, or destructive authority.

## Start

Run Codex from this folder:

```bash
codex -C /path/to/this/folder
```

Codex should read `AGENTS.md`, then `.ion/ION_CONTEXT_CAPSULE.yaml`, then `.ion/ACTIVE_CONTEXT_PACKAGE.md`.
"""


def _agents_md() -> str:
    return """# ION Context Starter Capsule

You are in a clean ION context starter capsule.

## Read First

- `.ion/ION_CONTEXT_CAPSULE.yaml`
- `.ion/ACTIVE_CONTEXT_PACKAGE.md`
- `.ion/ROUTE.json`
- `.ion/HOT_CONTEXT.md`
- `.ion/CONTEXT_PACKAGES.json`
- `.ion/MINI.md`
- `.ion/CAPSULE.md`
- `.ion/STATUS.json`

## Job

1. Inspect this folder.
2. Record observed facts in `.ion/ACTIVE_CONTEXT_PACKAGE.md`.
3. Keep unknowns explicit.
4. Write receipts under `.ion/receipts/` for material work.

## Hard Boundary

This is single-session context only.
Do not create invented agents, role briefs, specialist messages, or multi-agent output logs.
Do not claim accepted ION state, production authority, live execution authority, or secrets authority.
"""


def _config_toml() -> str:
    return '''# Generated ION context starter capsule config. Do not store secrets here.
sandbox_mode = "workspace-write"
approval_policy = "on-request"
developer_instructions = """
ION context starter guidance:
- This folder is a single-session context capsule, not a multi-agent runtime.
- Read AGENTS.md and .ion/ION_CONTEXT_CAPSULE.yaml before material work.
- Record observed local facts, unknowns, and receipts.
- Do not create invented agents, role briefs, specialist messages, or multi-agent output logs.
- No production, live execution, accepted-state, secrets, deploy, push, or destructive authority is granted by this starter.
"""

[features]
hooks = false

[sandbox_workspace_write]
network_access = false
writable_roots = ["."]
'''


def _context_capsule_yaml() -> str:
    return """schema_id: "ion.context_starter_capsule.v1"
capsule_kind: "context_starter"
folder_role: "candidate_new_context_folder"
status: "candidate_local_context"
runtime_claims:
  multi_agent_runtime: false
  live_agent_dispatch_proven: false
  invented_agent_outputs: false
authority:
  candidate_local_context_only: true
  production_authority: false
  live_execution_authority: false
  accepted_state_authority: false
  secrets_authority: false
read_first:
  - "AGENTS.md"
  - ".ion/ION_CONTEXT_CAPSULE.yaml"
  - ".ion/ACTIVE_CONTEXT_PACKAGE.md"
  - ".ion/ROUTE.json"
  - ".ion/HOT_CONTEXT.md"
  - ".ion/CONTEXT_PACKAGES.json"
  - ".ion/MINI.md"
  - ".ion/CAPSULE.md"
  - ".ion/STATUS.json"
write_surfaces:
  active_context: ".ion/ACTIVE_CONTEXT_PACKAGE.md"
  hot_context: ".ion/HOT_CONTEXT.md"
  context_packages: ".ion/CONTEXT_PACKAGES.json"
  loaded_refs: ".ion/LOADED_REFS.json"
  inbox: ".ion/inbox"
  outbox: ".ion/outbox"
  runs: ".ion/runs"
  receipts: ".ion/receipts"
  history: ".ion/history"
  machine_receipts: ".ion/machine_receipts"
forbidden_defaults:
  - "invented_agents"
  - "invented_role_briefs"
  - "specialist_message_drill"
  - "multi_agent_runtime_claim"
"""


def _active_context_package_md() -> str:
    return """# Active Context Package

This is the local working context for this folder.

## Observed Facts

- folder: current working folder
- capsule: clean ION context starter
- runtime: single Codex session

## Unknowns

- folder purpose: unknown until inspected
- accepted ION registry state: none claimed
- production/live authority: none

## Boundary

This is not a multi-agent runtime and does not contain generated agent messages.
"""


def _route_json() -> str:
    return json.dumps(
        {
            "schema_id": "ion.context_starter_route.v1",
            "local_required_refs": [{"path": path, "required": True} for path in REQUIRED_FILES],
            "route_policy": "Load local refs first. Keep claims local and candidate until accepted by explicit ION receipt.",
            "forbidden_default_outputs": [
                "invented_agents",
                "invented_role_briefs",
                "generated_specialist_messages",
                "multi_agent_runtime_claims",
            ],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        indent=2,
        sort_keys=True,
    )


def _long_horizon_json() -> str:
    return json.dumps(
        {
            "schema_id": "ion.context_starter_long_horizon.v1",
            "epochs": [
                {
                    "epoch_id": "starter_initial_epoch",
                    "summary": "Clean context starter created. Fill only from observed folder evidence.",
                }
            ],
            "policy": "Local continuity witness only until explicit ION acceptance.",
            "runtime_policy": "Single-session context only. Registry/domain-backed evidence is required for agent claims.",
        },
        indent=2,
        sort_keys=True,
    )


def _hot_context_md() -> str:
    return """# ION Context Starter Hot Context

generated_at: starter_materialization
witness_policy: Capsule is the minimum working context. Mini is lookup only.
production_authority: false
live_execution_authority: false

## CURRENT FOLDER CONTEXT

- Capsule: `.ion/ION_CONTEXT_CAPSULE.yaml`
- Active context package: `.ion/ACTIVE_CONTEXT_PACKAGE.md`
- Route: `.ion/ROUTE.json`
- Mini: `.ion/MINI.md`
- Long horizon: `.ion/LONG_HORIZON.json`

## NEXT

Inspect the folder, record observed facts, keep unknowns explicit, and write receipts for material work.
"""


def _context_packages_json() -> str:
    return json.dumps(
        {
            "schema_id": "ion.context_starter_context_packages.v1",
            "package_count": 5,
            "selected_by_default": [
                "minimum_working_capsule",
                "active_context_package",
                "hot_context",
            ],
            "packages": [
                {
                    "package_id": "minimum_working_capsule",
                    "context_type": "active_short_horizon",
                    "load_policy": "always_inline_first",
                    "path_refs": [".ion/CAPSULE.md", ".ion/ION_CONTEXT_CAPSULE.yaml"],
                },
                {
                    "package_id": "active_context_package",
                    "context_type": "local_working_context",
                    "load_policy": "always_inline_first",
                    "path_refs": [".ion/ACTIVE_CONTEXT_PACKAGE.md"],
                },
                {
                    "package_id": "hot_context",
                    "context_type": "compiled_hot_context",
                    "load_policy": "always_inline_first",
                    "path_refs": [".ion/HOT_CONTEXT.md"],
                },
                {
                    "package_id": "mini_lookup_index",
                    "context_type": "receipt_lookup",
                    "load_policy": "index_only_not_primary_prompt",
                    "path_refs": [".ion/MINI.md"],
                },
                {
                    "package_id": "long_horizon_index",
                    "context_type": "compressed_long_horizon",
                    "load_policy": "load_when_older_continuity_or_prior_decisions_matter",
                    "path_refs": [".ion/LONG_HORIZON.json"],
                },
            ],
            "production_authority": False,
            "live_execution_authority": False,
        },
        indent=2,
        sort_keys=True,
    )


def _loaded_refs_json() -> str:
    return json.dumps(
        {
            "schema_id": "ion.context_starter_loaded_refs.v1",
            "loaded_refs": [{"path": path, "required": True} for path in REQUIRED_FILES],
            "production_authority": False,
            "live_execution_authority": False,
        },
        indent=2,
        sort_keys=True,
    )


def _identity_card_md() -> str:
    return """# ION Context Starter Identity Card

AGENT_TAG: context_starter
CONVERSATION_TAG: local_context_starter
TASK_TAG: inspect_folder_and_record_observed_facts
CONTEXT_INSTANCE: pending_until_launched
BRANCH_ID: pending_until_launched
PARENT_CONTEXT: none
SHARED_CONTEXT_WRITE: false
SETTLEMENT_REQUIRED: true
"""


def _mini_md() -> str:
    return """# ION Context Starter Mini

ROLE: lookup index for this local context starter.

ACTIVE_CONTEXT_PACKAGE: .ion/ACTIVE_CONTEXT_PACKAGE.md
CAPSULE: .ion/CAPSULE.md
ROUTE: .ion/ROUTE.json
HOT_CONTEXT: .ion/HOT_CONTEXT.md
CONTEXT_PACKAGES: .ion/CONTEXT_PACKAGES.json

NEXT: Inspect this folder and write observed facts only.
"""


def _capsule_md() -> str:
    return """# ION Context Starter Capsule

Minimum local context for a new folder.

This capsule helps Codex start cleanly in this folder. It is not accepted ION state, not a multi-agent runtime, and not a role rehearsal.
"""


def _bootstrap_py() -> str:
    return '''#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

def find_portable_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".ion").is_dir() and (candidate / "AGENTS.md").exists():
            return candidate
    raise RuntimeError("Unable to locate portable ION root markers.")


ROOT = find_portable_root(Path(__file__).resolve())
ION = ROOT / ".ion"
REQUIRED = [
    ROOT / "AGENTS.md",
    ROOT / ".codex" / "config.toml",
    ION / "ION_CONTEXT_CAPSULE.yaml",
    ION / "ACTIVE_CONTEXT_PACKAGE.md",
    ION / "ROUTE.json",
    ION / "LONG_HORIZON.json",
    ION / "HOT_CONTEXT.md",
    ION / "CONTEXT_PACKAGES.json",
    ION / "LOADED_REFS.json",
    ION / "IDENTITY_CARD.md",
    ION / "MINI.md",
    ION / "CAPSULE.md",
]


def main() -> int:
    for rel in ("inbox", "outbox", "receipts", "runs"):
        (ION / rel).mkdir(parents=True, exist_ok=True)
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    status = {
        "schema_id": "ion.context_starter_status.v1",
        "ready": not missing,
        "missing": missing,
        "capsule_kind": "context_starter",
        "launch_command": f"codex -C {ROOT}",
        "runtime_claims": {
            "multi_agent_runtime": False,
            "live_agent_dispatch_proven": False,
            "invented_agent_outputs": False,
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    (ION / "STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0 if status["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _materialize_files(target: Path, *, status_folder: Path | None = None) -> None:
    for rel in (".codex", ".ion", ".ion/inbox", ".ion/outbox", ".ion/receipts", ".ion/runs"):
        (target / rel).mkdir(parents=True, exist_ok=True)
    for rel in EMPTY_CONTEXT_DIRS:
        _write(target / rel, "")
    _write(target / "README.md", _readme())
    _write(target / "AGENTS.md", _agents_md())
    _write(target / ".codex/config.toml", _config_toml())
    _write(target / ".ion/ION_CONTEXT_CAPSULE.yaml", _context_capsule_yaml())
    _write(target / ".ion/ACTIVE_CONTEXT_PACKAGE.md", _active_context_package_md())
    _write(target / ".ion/ROUTE.json", _route_json())
    _write(target / ".ion/LONG_HORIZON.json", _long_horizon_json())
    _write(target / ".ion/HOT_CONTEXT.md", _hot_context_md())
    _write(target / ".ion/CONTEXT_PACKAGES.json", _context_packages_json())
    _write(target / ".ion/LOADED_REFS.json", _loaded_refs_json())
    _write(target / ".ion/IDENTITY_CARD.md", _identity_card_md())
    _write(target / ".ion/MINI.md", _mini_md())
    _write(target / ".ion/CAPSULE.md", _capsule_md())
    _write(target / ".ion/STATUS.json", _status_json(status_folder))
    _write(target / ".ion/ion_bootstrap.py", _bootstrap_py())


def _clean_generated_surfaces(target: Path) -> None:
    for rel in EMPTY_CONTEXT_DIRS:
        surface = target / rel.rsplit("/", 1)[0]
        if surface.exists() and surface.is_dir():
            shutil.rmtree(surface)
    for rel in (
        *REQUIRED_FILES,
        ".ion/AGENT.yaml",
        ".ion/DOMAIN.yaml",
        ".ion/RELATIONSHIPS.yaml",
        ".ion/REMOVED_FAKE_AGENT_DRILL_20260525.md",
    ):
        path = target / rel
        if path.exists() and path.is_file():
            path.unlink()


def materialize_context_starter_capsule(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    final = shell_root / OPERATOR_FINAL
    internal = shell_root / INTERNAL_REFERENCE
    _materialize_files(final)
    internal.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "operator_final_path": OPERATOR_FINAL.as_posix(),
        "required_files": list(REQUIRED_FILES),
        "policy": "Clean context starter only; no agents, source snapshots, role drills, or multi-agent runtime are bundled.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    _write(internal / "STARTER_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True))
    return build_context_starter_capsule_projection(shell_root)


def create_context_starter_capsule(
    target: str | Path,
    root: str | Path | None = None,
    *,
    force: bool = False,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    materialize_context_starter_capsule(shell_root)
    target_path = Path(target).expanduser().resolve()
    existing = [item for item in target_path.iterdir()] if target_path.exists() else []
    if existing and not force:
        return {
            "schema_id": "ion.context_starter_create_result.v1",
            "ok": False,
            "finding": "target_not_empty",
            "target_path": target_path.as_posix(),
            "hint": "Use an empty folder or pass --force.",
        }
    target_path.mkdir(parents=True, exist_ok=True)
    if force:
        _clean_generated_surfaces(target_path)
    source = shell_root / OPERATOR_FINAL
    shutil.copytree(source, target_path, dirs_exist_ok=True)
    _write(target_path / ".ion/STATUS.json", _status_json(target_path))
    return {
        "schema_id": "ion.context_starter_create_result.v1",
        "ok": True,
        "target_path": target_path.as_posix(),
        "launch_command": f"codex -C {target_path}",
        "created_files": list(REQUIRED_FILES),
        "empty_context_dirs": [path.rsplit("/", 1)[0] for path in EMPTY_CONTEXT_DIRS],
        "runtime_policy": "single_session_context_only_registry_backed_context",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def build_context_starter_capsule_projection(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    final = shell_root / OPERATOR_FINAL
    required = []
    for rel in REQUIRED_FILES:
        path = final / rel
        required.append(
            {
                "path": (OPERATOR_FINAL / rel).as_posix(),
                "exists": path.is_file(),
                "bytes": path.stat().st_size if path.is_file() else 0,
            }
        )
    missing = [item["path"] for item in required if not item["exists"]]
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": READY_VERDICT if not missing else "ION_CONTEXT_STARTER_CAPSULE_MISSING",
        "ready": not missing,
        "starter_root": STARTER_ROOT.as_posix(),
        "operator_final_path": OPERATOR_FINAL.as_posix(),
        "internal_reference_path": INTERNAL_REFERENCE.as_posix(),
        "launch_command_template": "codex -C <new-folder>",
        "create_command_template": "python3 -m kernel.ion_context_starter_capsule --ion-root <ion-root> --create <new-folder>",
        "copy_policy": "Create a new folder from OPERATOR_FINAL; do not copy INTERNAL_REFERENCE_DO_NOT_TOUCH.",
        "source_snapshot_policy": "disabled_by_default",
        "runtime_policy": "single_session_context_only_registry_backed_context",
        "required_files": required,
        "missing_required_files": missing,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--materialize", action="store_true")
    parser.add_argument("--create")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.create:
        model = create_context_starter_capsule(args.create, args.ion_root, force=args.force)
    elif args.materialize:
        model = materialize_context_starter_capsule(args.ion_root)
    else:
        model = build_context_starter_capsule_projection(args.ion_root)
    if args.json:
        print(json.dumps(model, indent=2, sort_keys=True))
    else:
        print(model.get("verdict") or ("OK" if model.get("ok") else model.get("finding")))
        print(model.get("operator_final_path") or model.get("target_path") or "")
    return 0 if model.get("ready", model.get("ok", False)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
