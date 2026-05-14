#!/usr/bin/env python3
"""Build a candidate ION context mesh from folder capsules.

This tool is intentionally small and deterministic so Custom GPT / Codex
carriers can use it as a bounded local helper. It reads only files under the
provided root and never grants authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, Any, List
import hashlib
import yaml


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path != root else "."


def load_capsule(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"capsule is not a mapping: {path}")
    return data


def discover_capsules(root: Path) -> List[Dict[str, Any]]:
    root = root.resolve()
    results: List[Dict[str, Any]] = []
    for path in sorted(root.rglob("ION_CONTEXT_CAPSULE.yaml")):
        data = load_capsule(path)
        folder = data.get("folder") or rel(path.parent, root)
        results.append({
            "capsule_id": data.get("capsule_id", path.parent.name),
            "folder": folder,
            "path": rel(path, root),
            "sha256": sha256_file(path),
            "status": data.get("status", "unknown"),
            "domain_label": (data.get("identity") or {}).get("domain_label", path.parent.name),
            "authority": data.get("authority", {}),
            "read_first": data.get("read_first", []),
            "continuity_export": data.get("continuity_export", {}),
        })
    return results


def parent_folder(folder: str) -> str | None:
    if folder in ("", "."):
        return None
    p = Path(folder)
    parent = p.parent.as_posix()
    return "." if parent == "." else parent


def build_inheritance_edges(capsules: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    by_folder = {c["folder"].rstrip("/"): c for c in capsules}
    edges = []
    for capsule in capsules:
        folder = capsule["folder"].rstrip("/")
        parent = parent_folder(folder)
        while parent is not None:
            if parent in by_folder:
                edges.append({
                    "from_parent": by_folder[parent]["capsule_id"],
                    "to_child": capsule["capsule_id"],
                    "parent_folder": parent,
                    "child_folder": folder,
                })
                break
            parent = parent_folder(parent)
    return edges


def select_relevant_capsules(root: Path, changed_paths: Iterable[str] | None = None) -> List[str]:
    """Return capsule paths relevant to a changed file set, including parents.

    If changed_paths is empty, all discovered capsules are relevant.
    """
    capsules = discover_capsules(root)
    if not changed_paths:
        return [c["path"] for c in capsules]

    by_folder = {c["folder"].rstrip("/"): c for c in capsules}
    selected = set()
    for changed in changed_paths:
        p = Path(changed)
        cur = p.parent.as_posix() if p.parent.as_posix() != "." else "."
        while True:
            if cur in by_folder:
                selected.add(by_folder[cur]["path"])
            parent = parent_folder(cur)
            if parent is None:
                break
            cur = parent
    return sorted(selected)


def build_context_mesh(root: Path, changed_paths: Iterable[str] | None = None) -> Dict[str, Any]:
    root = root.resolve()
    capsules = discover_capsules(root)
    relevant = select_relevant_capsules(root, changed_paths)
    return {
        "schema_id": "ion.context_mesh_manifest.v1",
        "mesh_id": "ion.context_mesh.custom_gpt_carrier.v4_7",
        "root": ".",
        "capsules": capsules,
        "relevant_capsule_paths": relevant,
        "inheritance_edges": build_inheritance_edges(capsules),
        "authority": {
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "capsules_grant_authority": False,
        },
    }


def write_context_mesh(root: Path, out_path: Path, changed_paths: Iterable[str] | None = None) -> Dict[str, Any]:
    mesh = build_context_mesh(root, changed_paths)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(mesh, sort_keys=False), encoding="utf-8")
    return mesh


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--out", default="ION_CONTEXT_MESH_MANIFEST.yaml")
    parser.add_argument("--changed", nargs="*", default=None)
    args = parser.parse_args()
    write_context_mesh(Path(args.root), Path(args.out), args.changed)
