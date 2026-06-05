"""ION AI Git Branch Containment helper surfaces.

This module is intentionally small and non-authorizing. It provides deterministic
branch naming, posture classification, and receipt construction for agents that
must keep AI-authored edits outside protected branches until approval.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import re
from typing import Iterable, Mapping, Any

SCHEMA_ID = "ion.ai_git_branch_receipt.v0_1"
DEFAULT_PROTECTED_BRANCHES = ("main", "master", "trunk", "production", "release", "stable")
_SAFE_SLUG_RE = re.compile(r"[^a-z0-9]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_slug(value: str, *, limit: int = 48) -> str:
    """Return a git-branch-safe lowercase slug."""
    slug = _SAFE_SLUG_RE.sub("-", value.lower()).strip("-")
    return (slug[:limit].strip("-") or "work")


def build_ai_branch_name(agent: str, branch_node: str, objective: str, stamp: str) -> str:
    """Build the canonical ION AI work branch name."""
    return "ion/{}/{}/{}/{}".format(
        safe_slug(agent, limit=24),
        safe_slug(branch_node, limit=32),
        safe_slug(objective, limit=48),
        stamp,
    )


def is_protected_branch(branch: str | None, protected: Iterable[str] = DEFAULT_PROTECTED_BRANCHES) -> bool:
    if not branch:
        return True
    protected_set = {item.lower() for item in protected}
    return branch.lower() in protected_set


@dataclass(frozen=True)
class GitEditPosture:
    branch: str | None
    dirty: bool | None
    isolated_worktree: bool | None
    protected_branch: bool
    start_receipt_present: bool
    verdict: str
    reasons: tuple[str, ...]


def classify_git_edit_posture(
    *,
    branch: str | None,
    dirty: bool | None = None,
    isolated_worktree: bool | None = None,
    start_receipt_present: bool = False,
    protected_branches: Iterable[str] = DEFAULT_PROTECTED_BRANCHES,
) -> GitEditPosture:
    """Classify whether an agent may make material edits in the current checkout."""
    protected = is_protected_branch(branch, protected_branches)
    reasons: list[str] = []

    if protected:
        reasons.append("protected_branch")
    if dirty and protected:
        reasons.append("dirty_protected_checkout")
    if not start_receipt_present:
        reasons.append("missing_start_receipt")
    if isolated_worktree is False:
        reasons.append("not_isolated_worktree")
    if branch is None:
        reasons.append("unknown_branch")

    if dirty and protected:
        verdict = "blocked"
    elif protected or branch is None:
        verdict = "read_only"
    elif not start_receipt_present:
        verdict = "patch_only"
    elif isolated_worktree is False:
        verdict = "patch_only"
    else:
        verdict = "allow_edit"

    return GitEditPosture(
        branch=branch,
        dirty=dirty,
        isolated_worktree=isolated_worktree,
        protected_branch=protected,
        start_receipt_present=start_receipt_present,
        verdict=verdict,
        reasons=tuple(reasons),
    )


def build_start_receipt(
    *,
    receipt_id: str,
    agent: str,
    objective: str,
    branch_name: str,
    base_ref: str,
    base_commit: str,
    worktree_path: str,
    branch_node_path: str,
    authority: Mapping[str, Any] | None = None,
    context_surfaces: Mapping[str, Any] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a branch start receipt without mutating Git."""
    protected = is_protected_branch(branch_name)
    receipt_authority = {
        "production_authority": False,
        "live_execution_authority": False,
        "protected_branch_write": False,
        "operator_approval": False,
    }
    if authority:
        receipt_authority.update(dict(authority))

    return {
        "schema_id": SCHEMA_ID,
        "receipt_id": receipt_id,
        "receipt_type": "start",
        "created_at": created_at or utc_now(),
        "agent": agent,
        "objective": objective,
        "branch": {
            "name": branch_name,
            "base_ref": base_ref,
            "base_commit": base_commit,
            "worktree_path": worktree_path,
            "branch_node_path": branch_node_path,
            "protected_branch": protected,
            "isolated_worktree": True,
        },
        "context_surfaces": dict(context_surfaces or {}),
        "checks": [
            {
                "name": "protected_branch_guard",
                "passed": not protected,
                "details": {"branch": branch_name},
            }
        ],
        "authority": receipt_authority,
        "verdict": "allow_edit" if not protected else "read_only",
        "missing_proof": [] if not protected else ["non_protected_branch"],
    }


def build_recovery_receipt(
    *,
    receipt_id: str,
    agent: str,
    objective: str,
    recovery_branch: str,
    damaged_branch: str,
    last_known_good_ref: str,
    recovered_from: Iterable[str],
    excluded: Iterable[str] = (),
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a receipt that preserves mistake context while starting clean recovery."""
    return {
        "schema_id": SCHEMA_ID,
        "receipt_id": receipt_id,
        "receipt_type": "recovery",
        "created_at": created_at or utc_now(),
        "agent": agent,
        "objective": objective,
        "branch": {
            "name": recovery_branch,
            "base_ref": last_known_good_ref,
            "protected_branch": is_protected_branch(recovery_branch),
            "isolated_worktree": True,
        },
        "recovery_source": {
            "damaged_branch": damaged_branch,
            "last_known_good_ref": last_known_good_ref,
            "recovered_from": sorted(set(recovered_from)),
            "excluded": sorted(set(excluded)),
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "protected_branch_write": False,
            "operator_approval": False,
        },
        "verdict": "allow_edit" if not is_protected_branch(recovery_branch) else "read_only",
        "missing_proof": [] if not is_protected_branch(recovery_branch) else ["non_protected_recovery_branch"],
    }


def as_receipt_fragment(posture: GitEditPosture) -> dict[str, Any]:
    """Expose posture as a small chat/receipt fragment."""
    return {
        "schema_id": "ion.git_edit_posture.v0_1",
        "branch": posture.branch,
        "protected_branch": posture.protected_branch,
        "dirty": posture.dirty,
        "isolated_worktree": posture.isolated_worktree,
        "start_receipt_present": posture.start_receipt_present,
        "verdict": posture.verdict,
        "reasons": list(posture.reasons),
    }


def to_dict(posture: GitEditPosture) -> dict[str, Any]:
    return asdict(posture)
