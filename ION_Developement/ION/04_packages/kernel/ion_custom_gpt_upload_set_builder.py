"""Build ION Custom GPT knowledge upload package sets.

The builder emits curated zip packages with START_HERE, manifest, tree snapshot,
and SHA256SUMS. It excludes secrets, git history, local vaults, caches, and raw
runtime bulk by default.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

GPT_FILE_LIMIT_BYTES = 512 * 1024 * 1024
OUTPUT_ROOT = Path("ION_EXPORTS_LOCAL/custom_gpt_upload_set")

GLOBAL_EXCLUDE_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".cache",
    "ION_EXPORTS_LOCAL",
    "ION_VAULT_LOCAL",
    "quarentine",
    "dist",
    "build",
    "coverage",
    ".next",
    "target",
}
GLOBAL_EXCLUDE_PATTERNS = [
    ".env",
    ".env.*",
    "*.log",
    "*.tmp",
    "*.pyc",
    "*.pyo",
    "*.sqlite",
    "*.db",
    "*.key",
    "*.pem",
    "*.crt",
    "*.p12",
    "*.pfx",
    "*.zip",
]

PACKAGE_SPECS = {
    "ion_custom_gpt_sandbox_carrier_package": {
        "title": "ION Custom GPT Sandbox Carrier Package",
        "prefix": "ION_CUSTOM_GPT_SANDBOX_CARRIER_PACKAGE",
        "purpose": "Primary GPT boot package: current paste instructions, front-door carrier contract, persona/boot receipt laws, action setup maps, and continuity-transfer instructions.",
        "roots": [
            "ION_GPT/README.md",
            "ION_GPT/01_GPT_BUILDER_INPUTS",
            "ION_GPT/02_PACKAGES_TO_UPLOAD/README.md",
            "ION_GPT/03_ACTIONS",
            "ION_GPT/04_CURRENT_SANDBOX_CARRIER",
            "ION_GPT/05_CONTINUITY_TRANSFER",
            "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier",
        ],
        "extra_exclude_names": set(),
    },
    "full_workspace_snapshot": {
        "title": "ION Production Workspace Snapshot",
        "prefix": "ION_PRODUCTION_WORKSPACE_SNAPSHOT",
        "purpose": "Full readable workspace snapshot excluding secrets, git history, caches, build outputs, vaults, and raw quarantine evidence.",
        "roots": ["."],
        "extra_exclude_names": set(),
    },
    "ion_development_core_source": {
        "title": "ION Development Core Source",
        "prefix": "ION_DEVELOPMENT_CORE_SOURCE",
        "purpose": "Focused ION kernel/source/docs/tests/context working version.",
        "roots": ["ION_Developement"],
        "extra_exclude_names": set(),
    },
    "ion_gpt_action_release_and_builder_inputs": {
        "title": "ION GPT Action Release and Builder Inputs",
        "prefix": "ION_GPT_ACTION_RELEASE_AND_BUILDER_INPUTS",
        "purpose": "Canonical Action schema, GPT Builder input files, and Action release domain surfaces.",
        "roots": [
            "ION_GPT/01_GPT_BUILDER_INPUTS",
            "ION_GPT/03_ACTIONS",
            "ION_GPT/04_CURRENT_SANDBOX_CARRIER",
            "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway",
            "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier",
            "ION_Developement/ION/02_architecture/ION_CUSTOM_GPT_ACTION_RELEASE_DOMAIN_PROTOCOL_V0_1.md",
            "ION_Developement/ION/03_registry/ion_custom_gpt_action_release_registry.yaml",
            "ION_Developement/ION/04_packages/kernel/ion_action_schema_release.py",
            "ION_Developement/ION/tests/test_kernel_ion_action_schema_release.py",
            "ION_Developement/ION/docs/setup/ION_CUSTOM_GPT_ACTION_RELEASE_PROCESS.md",
        ],
        "extra_exclude_names": set(),
    },
    "daimon_workspace_context": {
        "title": "dAimon Workspace Context",
        "prefix": "DAIMON_WORKSPACE_CONTEXT",
        "purpose": "dAimon companion and bridge source/context without dependency/build bulk.",
        "roots": ["dAimon"],
        "extra_exclude_names": set(),
    },
    "browser_extension_context": {
        "title": "Browser Extension Context",
        "prefix": "BROWSER_EXTENSION_CONTEXT",
        "purpose": "Browser extension source/context for ChatGPT page companion, queue, docs, projects, and drop-target work.",
        "roots": ["browser_extension"],
        "extra_exclude_names": set(),
    },
    "ui_canon_and_joc_context": {
        "title": "UI Canon and JOC Context",
        "prefix": "UI_CANON_AND_JOC_CONTEXT",
        "purpose": "JOC/UI canon, Helixion cockpit workflow, and non-monolith UI context surfaces.",
        "roots": [
            "ION_Developement/ION/05_context/current/helixion_joc_rebuild",
            "ION_Developement/ION/05_context/current/ai_assistant_work",
            "ION_Developement/ION/08_ui",
        ],
        "extra_exclude_names": set(),
    },
    "aimos_atlas_wisdomnet_context": {
        "title": "AIMOS Atlas WisdomNET Context",
        "prefix": "AIMOS_ATLAS_WISDOMNET_CONTEXT",
        "purpose": "AIM-OS, ATLAS, and WisdomNET adjacent-system context.",
        "roots": ["AIM-OS", "ATLAS", "wisdomNET"],
        "extra_exclude_names": set(),
    },
    "ion_research_and_doctrine_context": {
        "title": "ION Research and Doctrine Context",
        "prefix": "ION_RESEARCH_AND_DOCTRINE_CONTEXT",
        "purpose": "ION doctrine, continuity substrate, context engineering, and research/reference material.",
        "roots": [
            "what is ION?",
            "ION_Developement/ION/02_architecture",
            "ION_Developement/ION/06_intelligence",
            "ION_Developement/ION/docs",
        ],
        "extra_exclude_names": set(),
    },
    "ion_latest_status_and_receipts": {
        "title": "ION Latest Status and Receipts",
        "prefix": "ION_LATEST_STATUS_AND_RECEIPTS",
        "purpose": "Freshness layer: current capsule, failure reports, action release recovery, status manifests, and selected receipts without raw runtime spam.",
        "roots": [
            "README.md",
            "AGENTS.md",
            "START_HERE_FOR_ANY_AGENT.md",
            "ION_WORKSPACE_MANIFEST.yaml",
            "ION_GPT/01_GPT_BUILDER_INPUTS",
            "ION_GPT/03_ACTIONS",
            "ION_GPT/04_CURRENT_SANDBOX_CARRIER",
            "ION_Developement/ION/05_context/current/codex_solo",
            "ION_Developement/ION/05_context/current/failure_reports",
            "ION_Developement/ION/05_context/current/action_release_recovery",
            "ION_Developement/ION/05_context/current/git_orchestration",
            "ION_Developement/ION/05_context/current/context_settlement",
        ],
        "extra_exclude_names": {"codex_queue_runs", "response_runs"},
    },
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _excluded(path: Path, extra_names: set[str]) -> bool:
    parts = path.parts
    for part in parts:
        if part in GLOBAL_EXCLUDE_NAMES or part in extra_names:
            return True
    name = path.name
    return any(fnmatch.fnmatch(name, pattern) for pattern in GLOBAL_EXCLUDE_PATTERNS)


def _iter_files(workspace_root: Path, roots: list[str], extra_names: set[str]):
    seen: set[Path] = set()
    for root_name in roots:
        root = workspace_root / root_name
        if not root.exists():
            continue
        if root.is_file():
            rel = root.relative_to(workspace_root)
            if not _excluded(rel, extra_names) and rel not in seen:
                seen.add(rel)
                yield rel
            continue
        for file_path in sorted(root.rglob("*")):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(workspace_root)
            if _excluded(rel, extra_names):
                continue
            if rel in seen:
                continue
            seen.add(rel)
            yield rel


def _tree_snapshot(records: list[dict]) -> str:
    lines = []
    for rec in records:
        lines.append(f'{rec["bytes"]:>10}  {rec["path"]}')
    return "\n".join(lines) + ("\n" if lines else "")


def _write_text(path: Path, text: str, records: list[dict], rel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    records.append({"path": rel, "sha256": _sha256(path), "bytes": path.stat().st_size, "generated": True})


def plan_package(workspace_root: Path, spec_key: str) -> dict:
    spec = PACKAGE_SPECS[spec_key]
    files = list(_iter_files(workspace_root, spec["roots"], spec.get("extra_exclude_names", set())))
    total_bytes = sum((workspace_root / rel).stat().st_size for rel in files)
    return {
        "package": spec_key,
        "title": spec["title"],
        "prefix": spec["prefix"],
        "file_count": len(files),
        "source_bytes": total_bytes,
        "source_mb": round(total_bytes / (1024 * 1024), 2),
        "roots": spec["roots"],
    }


def build_package(workspace_root: Path, spec_key: str, output_root: Path, timestamp: str) -> dict:
    spec = PACKAGE_SPECS[spec_key]
    package_id = f'{spec["prefix"]}_{timestamp}'
    staging = output_root / f".{package_id}_staging"
    zip_path = output_root / f"{package_id}.zip"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    for rel in _iter_files(workspace_root, spec["roots"], spec.get("extra_exclude_names", set())):
        src = workspace_root / rel
        dst = staging / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        records.append({"path": str(rel), "sha256": _sha256(dst), "bytes": dst.stat().st_size})

    start = (
        f'# {spec["title"]}\n\n'
        f'Package ID: `{package_id}`\n\n'
        f'Purpose: {spec["purpose"]}\n\n'
        'Source posture: candidate context package. This upload is not accepted ION state by itself.\n\n'
        'Start by reading `PACKAGE_MANIFEST.json`, then `TREE_SNAPSHOT.txt`, then the highest-level README/START_HERE files.\n'
    )
    _write_text(staging / "START_HERE.md", start, records, "START_HERE.md")

    source_posture = (
        '# Source Posture\n\n'
        '- accepted_state_claim: false\n'
        '- production_authority: false\n'
        '- live_execution_authority: false\n'
        '- secrets_included: false\n'
        '- git_history_included: false\n'
        '- vault_included: false\n'
        '- use_as: GPT knowledge/context, not source-of-truth mutation lane\n'
    )
    _write_text(staging / "SOURCE_POSTURE.md", source_posture, records, "SOURCE_POSTURE.md")

    _write_text(staging / "TREE_SNAPSHOT.txt", _tree_snapshot(records), records, "TREE_SNAPSHOT.txt")

    manifest = {
        "schema_id": "ion.custom_gpt_upload_package_manifest.v0_1",
        "package_key": spec_key,
        "package_id": package_id,
        "title": spec["title"],
        "purpose": spec["purpose"],
        "created_at_utc": timestamp,
        "workspace_root": str(workspace_root),
        "source_posture": "candidate_context_package",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "roots": spec["roots"],
        "records": records,
        "excludes": sorted(GLOBAL_EXCLUDE_NAMES | set(spec.get("extra_exclude_names", set()))),
    }
    manifest_path = staging / "PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    records.append({"path": "PACKAGE_MANIFEST.json", "sha256": _sha256(manifest_path), "bytes": manifest_path.stat().st_size, "generated": True})

    sums_path = staging / "SHA256SUMS.json"
    sums_path.write_text(json.dumps({r["path"]: r["sha256"] for r in records}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    records.append({"path": "SHA256SUMS.json", "sha256": _sha256(sums_path), "bytes": sums_path.stat().st_size, "generated": True})

    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(staging.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(staging))
    shutil.rmtree(staging)

    zip_size = zip_path.stat().st_size
    return {
        "package": spec_key,
        "package_id": package_id,
        "zip_path": str(zip_path),
        "zip_sha256": _sha256(zip_path),
        "file_count": len(records),
        "bytes": zip_size,
        "mb": round(zip_size / (1024 * 1024), 2),
        "within_gpt_512mb_limit": zip_size <= GPT_FILE_LIMIT_BYTES,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build ION Custom GPT upload package set")
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--output-root", default=str(OUTPUT_ROOT))
    parser.add_argument("--package", action="append", choices=["all", *PACKAGE_SPECS.keys()], default=[])
    parser.add_argument("--plan", action="store_true", help="Report package sizes without building zips")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    workspace_root = Path(args.workspace_root).resolve()
    output_root = (workspace_root / args.output_root).resolve() if not Path(args.output_root).is_absolute() else Path(args.output_root).resolve()
    selected = args.package or ["all"]
    if "all" in selected:
        keys = list(PACKAGE_SPECS.keys())
    else:
        keys = selected

    if args.plan:
        result = {"ok": True, "mode": "plan", "packages": [plan_package(workspace_root, key) for key in keys]}
    else:
        timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        packages = [build_package(workspace_root, key, output_root, timestamp) for key in keys]
        summary_path = output_root / f"UPLOAD_SET_SUMMARY_{timestamp}.json"
        result = {
            "ok": True,
            "mode": "build",
            "created_at_utc": timestamp,
            "output_root": str(output_root),
            "packages": packages,
        }
        output_root.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["summary_path"] = str(summary_path)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
