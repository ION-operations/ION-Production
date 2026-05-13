#!/usr/bin/env python3
"""
Copy AIM-OS essentials to a new folder — source code, docs, indexes, config only.
Excludes: dependencies (node_modules, target, etc.), build output, runtime data.

Target size: ~10–100 MB (actual source + docs, not 12GB of Rust builds).

Usage:
    python scripts/copy_aimos_essentials.py [destination_folder]
    Default destination: ../AIM-OS-essentials (sibling of AIM-OS)
"""

import os
import shutil
import sys
from pathlib import Path

# Paths relative to repo root
EXCLUDE_DIRS = {
    "node_modules",
    "target",
    "target-live",
    "out",
    "dist",
    ".next",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".git",
    "build",
    ".pytest_cache",
    "htmlcov",
    "coverage",
    ".idea",
    ".vscode",
    ".cursor",
    "backups",
    "logs",
    # Large generated / runtime
    "context_mapper_lab",  # ~300 MB, likely generated
    "wire_proof",          # ~268 MB, likely generated
}

EXCLUDE_FILE_PATTERNS = (
    ".pyc",
    ".pyo",
    ".db",
    ".db-shm",
    ".db-wal",
    ".log",
    ".map",
    ".vsix",
    ".zip",
    ".pkl",
    ".faiss",
)

# Large generated index files (HHNI, etc.) — .gitignore has **/HHNI_*.json
EXCLUDE_FILE_NAMES = (
    "HHNI_IDEA_INDEX.json",
    "HHNI_IDEA_INDEX_SUMMARY.json",
)

# Root-relative paths to skip entirely (not "what AIM-OS is")
SKIP_ENTIRE_PATHS = {
    "mcp_ai_messages.json",
    "mcp_timeline_entries.json",
    "codex_workspace",
    "mcp_memory",  # runtime index tags
    "data",        # runtime stores (analysis, memory, mcp, etc.)
    "IDE/src-tauri/target",
    "IDE/src-tauri/target-live",
    # Large app examples (not core AIM-OS)
    "apps/ProEarth",
    "apps/planet-engine",
    "apps/lucidimage",
    "apps/OPUStree",
    "apps/Procedural_trees_rocks",
    "apps/Documentation",
    "apps/earthdocs",
    "apps/MASTER_ORCHESTRATION",
    "apps/OPUS_ONBOARDING_PACK",
    "apps/TBD",
    "apps/Globe",
    "apps/HyperRealH20Monolith",
    "apps/OpusMagnusWater",
    "apps/forcing_test_quick",
    "apps/mlsmpmsplashdrafts",
    "forcing_test_flip",
    "UIeditor",
    "knowledge_architecture/applications/ide_chat_app/analysis",
    # Large legacy/consolidated docs (not core AIM-OS)
    "Documentation",
    "Documentation_Consolidated",
    "legacy_docs",
    "analysis",
}

# Paths to include (if we want explicit include-only; else we copy root and exclude)
# For now: copy from root, exclude by pattern


def should_skip_path(rel_path: str, name: str, is_dir: bool) -> bool:
    """Return True if this path should be skipped."""
    rel_norm = rel_path.replace("\\", "/")
    # Check entire path skip
    for skip in SKIP_ENTIRE_PATHS:
        s = skip.replace("\\", "/")
        if rel_norm == s or rel_norm.startswith(s + "/"):
            return True
    # Check dir name
    if is_dir and name in EXCLUDE_DIRS:
        return True
    # Check file patterns
    if not is_dir:
        if name in EXCLUDE_FILE_NAMES:
            return True
        for pat in EXCLUDE_FILE_PATTERNS:
            if name.endswith(pat):
                return True
        if "HHNI_" in name and name.endswith(".json"):
            return True
        # Skip .env (secrets) but keep .env.template
        if name == ".env" or (name.startswith(".env.") and "template" not in name.lower() and "example" not in name.lower()):
            return True
    return False


def copy_essentials(src_root: Path, dst_root: Path) -> tuple[int, int, int]:
    """Copy essential files. Returns (files_copied, dirs_created, bytes_copied)."""
    files_copied = 0
    dirs_created = 0
    bytes_copied = 0

    for root, dirs, files in os.walk(src_root, topdown=True):
        root_path = Path(root)
        rel_root = root_path.relative_to(src_root)
        rel_str = str(rel_root).replace("\\", "/")

        # Prune dirs we don't want to descend into
        dirs[:] = [d for d in dirs if not should_skip_path(str(Path(rel_root) / d), d, True)]

        # Create destination dir
        dst_dir = dst_root / rel_root
        if not dst_dir.exists():
            dst_dir.mkdir(parents=True, exist_ok=True)
            dirs_created += 1

        for f in files:
            rel_file = str(Path(rel_root) / f).replace("\\", "/")
            if should_skip_path(rel_file, f, False):
                continue
            src_file = root_path / f
            dst_file = dst_dir / f
            try:
                shutil.copy2(src_file, dst_file)
                files_copied += 1
                bytes_copied += src_file.stat().st_size
            except OSError as e:
                print(f"  Skip {rel_file}: {e}", file=sys.stderr)

    return files_copied, dirs_created, bytes_copied


def main():
    args = [a for a in sys.argv[1:] if a not in ("-y", "-f", "--force")]
    script_dir = Path(__file__).resolve().parent
    src_root = script_dir.parent
    default_dst = src_root.parent / "AIM-OS-essentials"
    dst_root = Path(args[0]) if args else default_dst

    dst_root = dst_root.resolve()
    if dst_root == src_root:
        print("Error: Destination cannot be the source.", file=sys.stderr)
        sys.exit(1)

    force = any(f in sys.argv for f in ("-y", "-f", "--force"))
    if dst_root.exists():
        if not force:
            print(f"Destination exists: {dst_root}")
            r = input("Overwrite? (y/N): ").strip().lower()
            if r != "y":
                print("Aborted.")
                sys.exit(0)
        shutil.rmtree(dst_root)

    print(f"Copying AIM-OS essentials")
    print(f"  From: {src_root}")
    print(f"  To:   {dst_root}")
    print()

    files, dirs, bytes_total = copy_essentials(src_root, dst_root)
    size_mb = bytes_total / (1024 * 1024)

    print(f"Done: {files} files, {dirs} dirs, {size_mb:.1f} MB")
    print(f"Location: {dst_root}")


if __name__ == "__main__":
    main()
