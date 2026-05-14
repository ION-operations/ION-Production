#!/usr/bin/env python3
"""Dogfood v4.7 by building a context mesh, context package, and remountable zip."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import importlib.util
import yaml
import shutil
import zipfile
import hashlib


def _load_sibling(name: str):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


mesh_builder = _load_sibling("ion_context_mesh_builder")
pkg_builder = _load_sibling("ion_context_package_builder")
transfer_export = _load_sibling("ion_context_transfer_export")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_dogfood_package(root: Path, out_dir: Path) -> Dict[str, Any]:
    root = root.resolve()
    carrier = root / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"
    out_dir.mkdir(parents=True, exist_ok=True)

    mesh = mesh_builder.build_context_mesh(root, changed_paths=[
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_V4_7_PROJECT_CONTEXT_PACKAGE_DOGFOOD.md",
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/context_packages/ION_CONTEXT_PACKAGE_CUSTOM_GPT_CARRIER_V4_7.yaml",
    ])
    (out_dir / "ion_context_mesh_manifest.yaml").write_text(yaml.safe_dump(mesh, sort_keys=False), encoding="utf-8")

    signals = [
        {
            "signal_id": "domain_context_capsule_readme_click",
            "status": "candidate_foundational_architecture",
            "product_version_target": "v4.5/v4.7",
            "continuity_export_required": True,
            "accepted_state_claim": False,
        },
        {
            "signal_id": "ion_transfer_ignore_export_profiles",
            "status": "candidate_foundational_architecture",
            "product_version_target": "v4.6/v4.7",
            "continuity_export_required": True,
            "accepted_state_claim": False,
        },
    ]
    package = pkg_builder.build_context_package(
        "ion.context_package.custom_gpt_carrier.v4_7.dogfood",
        mesh,
        architecture_signals=signals,
    )
    pkg_builder.write_context_package(package, out_dir / "ion_context_package.yaml")
    pkg_builder.write_next_chat_prompt(out_dir / "NEXT_CHAT_PROMPT.txt")

    transfer_manifest = transfer_export.build_transfer_manifest(root, profile_name="minimal_continuity")
    (out_dir / "ION_TRANSFER_MANIFEST.yaml").write_text(yaml.safe_dump(transfer_manifest, sort_keys=False), encoding="utf-8")

    readme = (
        "# ION v4.7 Dogfood Context Package\n\n"
        "This package was built from the Custom GPT carrier's own context mesh. "
        "Mount it before substantive answer in a new chat. It is candidate context, "
        "not accepted state.\n"
    )
    (out_dir / "README_START_HERE.md").write_text(readme, encoding="utf-8")

    zip_path = out_dir.with_suffix(".zip")
    hashes = pkg_builder.build_package_zip(out_dir, zip_path)

    # Remount simulation: verify package files alone contain required state.
    loaded_package = yaml.safe_load((out_dir / "ion_context_package.yaml").read_text(encoding="utf-8"))
    loaded_mesh = yaml.safe_load((out_dir / "ion_context_mesh_manifest.yaml").read_text(encoding="utf-8"))
    remount_pass = (
        loaded_package["workflow_state"]["active_route"] == "DOGFOOD_CONTEXT_PACKAGE_BUILD_ROUTE"
        and loaded_package["authority"]["accepted_state_claim"] is False
        and len(loaded_mesh.get("capsules", [])) >= 2
        and (out_dir / "NEXT_CHAT_PROMPT.txt").exists()
    )

    report = {
        "schema_id": "ion.custom_gpt.dogfood_build_report.v1",
        "build_id": "ion_custom_gpt_v4_7_dogfood_build",
        "posture": "sandbox-candidate",
        "results": {
            "context_mesh_capsules": len(mesh.get("capsules", [])),
            "relevant_capsules": len(mesh.get("relevant_capsule_paths", [])),
            "transfer_manifest_includes": transfer_manifest["include_count"],
            "transfer_manifest_omits": transfer_manifest["omit_count"],
            "zip_path": zip_path.as_posix(),
            "zip_sha256": sha256_file(zip_path),
            "remount_simulation": "pass" if remount_pass else "fail",
        },
        "authority": {
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
        "hashes": hashes,
    }
    (out_dir / "ion_dogfood_build_report.yaml").write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--out", default="ION_V4_7_DOGFOOD_CONTEXT_PACKAGE")
    args = parser.parse_args()
    report = build_dogfood_package(Path(args.root), Path(args.out))
    print(yaml.safe_dump(report, sort_keys=False))
