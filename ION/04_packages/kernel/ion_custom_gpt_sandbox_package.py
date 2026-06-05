"""Build the ION Custom GPT sandbox-carrier upload package.

This builder intentionally packages curated carrier instructions and indexes, not
secrets, runtime vaults, or raw workspace history.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile

from .ion_artifact_purpose import PURPOSE_CUSTOM_GPT_SANDBOX_PACKAGE, require_artifact_path

DEFAULT_OUTPUT = Path("ION_EXPORTS_LOCAL/custom_gpt_sandbox_carrier")
PACKAGE_ROOT = Path("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier")
CANONICAL_OPENAPI = Path("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway/openapi.yaml")
GPT_BUILDER_ACTION_SCHEMA_TARGETS = [
    Path("ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml"),
    Path("ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml"),
]
BOOT_EVIDENCE_ROOT = Path("Needs_Routed/custom_gpt_mount")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_file(src_root: Path, dst_root: Path, rel: Path, records: list[dict]) -> None:
    src = src_root / rel
    if not src.exists() or not src.is_file():
        return
    dst = dst_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    records.append({"path": str(rel), "sha256": _sha256(dst), "bytes": dst.stat().st_size})


def _copy_tree(src_root: Path, dst_root: Path, rel_root: Path, records: list[dict]) -> None:
    root = src_root / rel_root
    if not root.exists():
        return
    for src in sorted(root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_root)
        if src.suffix.lower() == ".zip" or "UPLOAD_THESE_ZIPS" in rel.parts:
            continue
        _copy_file(src_root, dst_root, rel, records)


def build_package(workspace_root: Path, output_root: Path | None = None) -> dict:
    workspace_root = workspace_root.resolve()
    output_root = require_artifact_path(
        output_root or DEFAULT_OUTPUT,
        purpose=PURPOSE_CUSTOM_GPT_SANDBOX_PACKAGE,
        active_root=workspace_root,
        base_root="workspace",
    )
    timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    package_id = f"ION_CUSTOM_GPT_SANDBOX_CARRIER_PACKAGE_{timestamp}"
    staging = output_root / f".{package_id}_staging"
    zip_path = output_root / f"{package_id}.zip"

    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []

    _copy_tree(workspace_root, staging, PACKAGE_ROOT, records)
    _copy_tree(workspace_root, staging, Path("ION_GPT/01_GPT_BUILDER_INPUTS"), records)
    _copy_tree(workspace_root, staging, Path("ION_GPT/02_PACKAGES_TO_UPLOAD"), records)
    _copy_tree(workspace_root, staging, Path("ION_GPT/03_ACTIONS"), records)
    _copy_file(workspace_root, staging, CANONICAL_OPENAPI, records)
    _copy_tree(workspace_root, staging, BOOT_EVIDENCE_ROOT, records)

    for rel in [Path("README.md"), Path("AGENTS.md")]:
        _copy_file(workspace_root, staging, rel, records)

    start_here = staging / "START_HERE_FOR_CUSTOM_GPT.md"
    start_here.write_text(
        "# Start Here for ION Custom GPT Sandbox Carrier\n\n"
        "Use `ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md` "
        "as the current GPT Builder instruction source.\n\n"
        "The matching carrier-source instruction file is "
        "`ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/"
        "instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md`.\n\n"
        "Use this package as context and evidence, not accepted state. The Custom GPT is a sandbox carrier, not total ION.\n\n"
        "Do not install Action fragments into GPT Builder. GPT Builder Action install targets are "
        "`ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml` and "
        "`ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml`.\n\n"
        "The worker/source OpenAPI evidence path is "
        "`ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_action_gateway/openapi.yaml`. "
        "It is not the GPT Builder install target. GPT Builder changes require a release bundle.\n",
        encoding="utf-8",
    )
    records.append({"path": "START_HERE_FOR_CUSTOM_GPT.md", "sha256": _sha256(start_here), "bytes": start_here.stat().st_size})

    manifest = {
        "schema_id": "ion.custom_gpt_sandbox_package_manifest.v0_1",
        "package_id": package_id,
        "created_at_utc": timestamp,
        "workspace_root": "redacted_local_workspace_root",
        "workspace_root_redacted": True,
        "source_posture": "candidate_context_package",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "canonical_action_schema_reference": str(CANONICAL_OPENAPI),
        "gpt_builder_action_schema_targets": [str(path) for path in GPT_BUILDER_ACTION_SCHEMA_TARGETS],
        "records": records,
        "excludes": [".git", ".env*", "ION_VAULT_LOCAL", "quarantine raw evidence", "venv/caches/node_modules/tmp/logs"],
    }
    manifest_path = staging / "PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    records.append({"path": "PACKAGE_MANIFEST.json", "sha256": _sha256(manifest_path), "bytes": manifest_path.stat().st_size})

    sums_path = staging / "SHA256SUMS.json"
    sums_path.write_text(json.dumps({r["path"]: r["sha256"] for r in records}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    records.append({"path": "SHA256SUMS.json", "sha256": _sha256(sums_path), "bytes": sums_path.stat().st_size})

    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(staging.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(staging))

    shutil.rmtree(staging)

    return {
        "ok": True,
        "package_id": package_id,
        "zip_path": str(zip_path),
        "zip_sha256": _sha256(zip_path),
        "file_count": len(records),
        "bytes": zip_path.stat().st_size,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build ION Custom GPT sandbox-carrier package")
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = build_package(Path(args.workspace_root), Path(args.output_root) if args.output_root else None)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["zip_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
