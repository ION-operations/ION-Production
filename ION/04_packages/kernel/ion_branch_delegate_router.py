"""ION Branch Delegation Router v0.1.

Candidate helper for path-addressable branch delegation.

This module deliberately does not invoke external agents. It resolves folder/file
references into branch-context targets and emits a proof-aware delegation request
shape. Actual delegate calls require a separate Codex subagent, MCP, ION agent,
or browser-queue receipt.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import re
from typing import Iterable, Literal

SCHEMA_ID = "ion.branch_delegation_request.v0_1"

RESERVED_TAGS = [
    "route:branch-delegation",
    "carrier:codex-cli",
    "phase:delegate-request",
    "state:candidate",
    "proof:missing",
    "authority:read-only",
    "authority:no-production",
    "authority:no-live",
]

GUIDANCE_FILENAMES = (
    "README.md",
    "AGENTS.md",
    "ION_CONTEXT_CAPSULE.yaml",
    "BRANCH_CHILD_INDEX.yaml",
)

DelegateMode = Literal["route_only", "ask_for_context", "review_plan", "patch_plan", "run_tests"]


@dataclass(frozen=True)
class BranchTarget:
    ref: str
    kind: str
    resolved_path: str
    nearest_branch_node: str | None
    context_files: list[str]
    status: str
    blockers: list[str]


class BranchDelegationError(ValueError):
    """Raised when an unsafe target path is provided."""


def _repo_relative(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise BranchDelegationError(f"path escapes repo root: {path}") from exc


def safe_resolve_ref(repo_root: str | Path, ref: str, current_branch: str | Path = ".") -> Path:
    """Resolve a branch/file ref safely under repo_root.

    Absolute paths and path traversal outside the repo are rejected.
    """

    root = Path(repo_root).resolve()
    if not ref or ref.strip() == "":
        raise BranchDelegationError("empty branch reference")
    raw = Path(ref)
    if raw.is_absolute():
        raise BranchDelegationError("absolute external paths are not allowed by default")
    base = (root / current_branch).resolve()
    candidate = (base / raw).resolve() if not str(ref).startswith(("ION/", "README.md", "AGENTS.md")) else (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise BranchDelegationError(f"path escapes repo root: {ref}") from exc
    return candidate


def find_nearest_branch_node(repo_root: str | Path, target_path: str | Path) -> tuple[str | None, list[str]]:
    """Find the nearest ancestor containing README/AGENTS/CAPSULE guidance."""

    root = Path(repo_root).resolve()
    target = Path(target_path).resolve()
    if target.is_file():
        cursor = target.parent
    else:
        cursor = target
    context_files: list[str] = []
    nearest: str | None = None
    while True:
        present = [name for name in GUIDANCE_FILENAMES if (cursor / name).exists()]
        if present:
            nearest = _repo_relative(root, cursor) or "."
            context_files = [f"{nearest.rstrip('/')}/{name}".lstrip("./") if nearest != "." else name for name in present]
            break
        if cursor == root:
            break
        cursor = cursor.parent
    return nearest, context_files


def classify_target(repo_root: str | Path, ref: str, current_branch: str | Path = ".") -> BranchTarget:
    """Classify one target path into a candidate branch delegation target."""

    root = Path(repo_root).resolve()
    try:
        resolved = safe_resolve_ref(root, ref, current_branch=current_branch)
    except BranchDelegationError as exc:
        return BranchTarget(
            ref=ref,
            kind="invalid",
            resolved_path="",
            nearest_branch_node=None,
            context_files=[],
            status="blocked",
            blockers=[str(exc)],
        )

    if resolved.exists():
        kind = "directory" if resolved.is_dir() else "file"
        nearest, files = find_nearest_branch_node(root, resolved)
        blockers = [] if nearest else ["no_branch_context_node_found"]
        status = "candidate" if nearest else "blocked"
    else:
        kind = "missing"
        nearest, files = find_nearest_branch_node(root, resolved.parent)
        blockers = ["target_path_missing"]
        status = "blocked"

    return BranchTarget(
        ref=ref,
        kind=kind,
        resolved_path=_repo_relative(root, resolved) if resolved.exists() else str(Path(ref).as_posix()),
        nearest_branch_node=nearest,
        context_files=files,
        status=status,
        blockers=blockers,
    )


def infer_delegate_mode(text: str) -> DelegateMode:
    lowered = text.lower()
    if any(word in lowered for word in ["test", "pytest", "verify", "regression"]):
        return "run_tests"
    if any(word in lowered for word in ["patch", "implement", "fix", "change"]):
        return "patch_plan"
    if any(word in lowered for word in ["review", "audit", "critique"]):
        return "review_plan"
    if any(word in lowered for word in ["route", "which branch", "who should"]):
        return "route_only"
    return "ask_for_context"


_PATH_TOKEN = re.compile(
    r"(?:branch:|path:)?(?P<path>(?:ION|src|tests|docs|packages|apps|\.agents|README\.md|AGENTS\.md|ION_CONTEXT_CAPSULE\.yaml)[A-Za-z0-9_./\-]*)(?=$|\s|[,;:])"
)


def extract_branch_refs(text: str) -> list[str]:
    """Extract likely repo path references from operator text.

    This is intentionally conservative. It accepts explicit branch:/path: prefixes
    and common repo path roots. It does not grant authority.
    """

    refs: list[str] = []
    for match in _PATH_TOKEN.finditer(text):
        ref = match.group("path").rstrip(".,;:")
        if ref not in refs:
            refs.append(ref)
    return refs


def build_delegation_request(
    repo_root: str | Path,
    objective: str,
    targets: Iterable[str] | None = None,
    current_branch: str | Path = ".",
    mode: DelegateMode | None = None,
    allowed_surfaces: Iterable[str] | None = None,
    production_authority: bool = False,
    live_execution_authority: bool = False,
) -> dict:
    """Build a proof-aware branch delegation request.

    The request is a candidate object. It does not call an agent.
    """

    root = Path(repo_root).resolve()
    selected_targets = list(targets or extract_branch_refs(objective))
    selected_mode: DelegateMode = mode or infer_delegate_mode(objective)
    target_objects = [classify_target(root, ref, current_branch=current_branch) for ref in selected_targets]

    if allowed_surfaces is None:
        allowed_surfaces = ["local_context_compile", "manual_receipt_packet"]

    blocked = any(t.status == "blocked" for t in target_objects) or not target_objects
    return {
        "schema_id": SCHEMA_ID,
        "status": "blocked" if blocked else "candidate",
        "objective": objective,
        "current_branch": str(current_branch),
        "requested_delegate_mode": selected_mode,
        "targets": [asdict(t) for t in target_objects],
        "allowed_surfaces": list(allowed_surfaces),
        "authority": {
            "production_authority": bool(production_authority),
            "live_execution_authority": bool(live_execution_authority),
            "write_authority": "none",
        },
        "tags": list(RESERVED_TAGS),
        "proof_required": [
            "context_files_read",
            "delegate_return_or_blocker",
            "ion_receipt_fragment",
        ],
        "did_not_do": [
            "did_not_invoke_subagent",
            "did_not_call_mcp",
            "did_not_enqueue_ion_agent",
            "did_not_mutate_files",
        ],
        "missing_proof": [
            "no_delegate_invocation_receipt",
            "no_branch_delegate_return",
        ],
    }


def build_delegate_return_stub(branch: str, status: str = "blocked", blocker: str = "delegate_not_invoked") -> dict:
    """Build a safe return stub when no delegate was actually called."""

    return {
        "schema_id": "ion.branch_delegate_return.v0_1",
        "branch": branch,
        "status": status,
        "context_refs": [],
        "summary": "",
        "recommendations": [],
        "blockers": [blocker],
        "authority_boundary": {
            "production_authority": False,
            "live_execution_authority": False,
        },
        "receipt_fragment": {
            "tool_calls": [],
            "did_not_do": ["did_not_call_delegate"],
            "missing_proof": ["delegate_invocation_receipt"],
        },
    }
