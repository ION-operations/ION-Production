"""ION workspace path resolver.

The active workspace was reorganized so integration surfaces that used to live
under ``ION/09_integrations`` can live as first-class workspace roots. This
helper keeps older repo-relative callers working while the workspace promotion is
settled.
"""
from __future__ import annotations

import os
from pathlib import Path

WORKSPACE_REGISTRY_RELATIVE_PATH = Path("ION/03_registry/ion_workspace_path_registry.yaml")

PROMOTED_INTEGRATION_ROOTS: tuple[tuple[Path, Path], ...] = (
    (Path("ION/09_integrations/custom_gpt_action_gateway"), Path("../ION_GPT/custom_gpt_action_gateway")),
    (Path("ION/09_integrations/chatgpt_browser_mcp_action"), Path("../mcp/chatgpt_browser_mcp_action")),
    (Path("ION/09_integrations/browser_extension"), Path("../browser_extension")),
    (Path("ION/09_integrations/cursor_extension"), Path("../Cursor/cursor_extension")),
    (Path("ION/09_integrations/cursor_sdk"), Path("../Cursor/cursor_sdk")),
    (Path("ION/09_integrations/local_daemon"), Path("../local_daemon")),
    (Path("ION/09_integrations/product_packager"), Path("../product_packager")),
    (Path("ION/09_integrations/systemd/user"), Path("../systemd/user")),
    (Path("ION/09_integrations/mcp"), Path("../mcp")),
)

KNOWN_ACTIVE_REPO_NAMES = ("ION_Developement", "ION_CODEX FULL", "ION_CODEX")


def resolve_repo_root(start: str | Path | None = None) -> Path:
    """Resolve an ION repo root from a path without requiring the old name."""

    candidate = Path(start or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    for path in (candidate, *candidate.parents):
        for repo_name in KNOWN_ACTIVE_REPO_NAMES:
            repo = path / repo_name
            if (repo / "pyproject.toml").exists() and (repo / "ION/REPO_AUTHORITY.md").exists():
                return repo
    return candidate


def workspace_root_for_repo(repo_root: str | Path) -> Path:
    """Return the parent workspace root for the active ION repo."""

    root = Path(repo_root).expanduser().resolve()
    return root.parent


def _relative_to(path: Path, root: Path) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def display_path(path: Path, repo_root: str | Path) -> str:
    """Render a path relative to repo root, allowing promoted sibling roots."""

    root = Path(repo_root).expanduser().resolve()
    return _relative_to(path.expanduser().resolve(), root)


def resolve_ion_path(repo_root: str | Path, relative_path: str | Path) -> Path:
    """Resolve an ION path, falling back to promoted workspace roots.

    Resolution order:
    1. Existing path relative to repo root.
    2. Explicit relative path such as ``../ION_GPT/...``.
    3. Active-root fallback for old ``../`` workspace references now living in-repo.
    4. Promoted integration mapping for legacy ``ION/09_integrations`` paths.
    5. Original repo-relative path as a non-existing candidate.
    """

    root = Path(repo_root).expanduser().resolve()
    rel = Path(relative_path)
    repo_candidate = (root / rel).resolve()
    if repo_candidate.exists():
        return repo_candidate
    if rel.parts and rel.parts[0] == "..":
        explicit = (root / rel).resolve()
        if explicit.exists():
            return explicit
        in_repo = (root / Path(*rel.parts[1:])).resolve()
        if in_repo.exists():
            return in_repo
    rel_posix = rel.as_posix()
    for old_root, new_root in PROMOTED_INTEGRATION_ROOTS:
        old_posix = old_root.as_posix()
        if rel_posix == old_posix or rel_posix.startswith(old_posix + "/"):
            suffix = rel_posix[len(old_posix):].lstrip("/")
            promoted = (root / new_root / suffix).resolve()
            if promoted.exists():
                return promoted
    return repo_candidate


def classify_ion_path(repo_root: str | Path, relative_path: str | Path) -> dict[str, object]:
    """Return path resolution evidence for audits and release reports."""

    root = Path(repo_root).expanduser().resolve()
    rel = Path(relative_path)
    repo_candidate = (root / rel).resolve()
    resolved = resolve_ion_path(root, rel)
    return {
        "requested_path": rel.as_posix(),
        "repo_candidate": display_path(repo_candidate, root),
        "resolved_path": display_path(resolved, root),
        "exists": resolved.exists(),
        "promoted_workspace_path": resolved != repo_candidate,
        "workspace_root": str(workspace_root_for_repo(root)),
    }
