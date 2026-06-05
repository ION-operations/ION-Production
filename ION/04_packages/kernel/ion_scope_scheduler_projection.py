"""UI-safe scope projection for the ION kernel scheduler.

This module does not mutate scheduler state and does not become a planner. It wraps
the existing kernel scheduler projection in the language needed by the cockpit:
scope, horizon, schedule state, commitment, carrier binding, blockers, and receipts.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.scope_scheduler_projection.v1"
DEFAULT_KERNEL_STORE = Path("ION/05_context/history/kernel_store")

SCHEDULE_STATES = (
    "READY",
    "BLOCKED",
    "CLAIMED",
    "IN_FLIGHT",
    "RETRY",
    "STALE",
    "DEFERRED",
    "ENACTED_UNLANDED",
    "FUTURE_CANDIDATE",
)

COMMITMENTS = (
    "SPECULATIVE",
    "EMERGING",
    "LIKELY",
    "PRECOMMITTED",
    "COMMITTED",
    "ENACTED",
    "COMPLETED",
)

HORIZON_BUCKETS = ("immediate", "near", "far", "unlayered")


def _shell_root(root: str | Path | None = None) -> Path:
    """Return the shell root expected by ION paths.

    The uploaded package in sandbox often has `ION/05_context` as the extracted
    content root rather than `./ION/05_context` below a shell root. This helper
    accepts both shapes.
    """

    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "ION/05_context").exists():
            return path
        if (path / "05_context").exists() and (path / "REPO_AUTHORITY.md").exists():
            return path.parent
    return candidate


def _kernel_store_root(shell_root: Path) -> Path:
    return shell_root / DEFAULT_KERNEL_STORE


def _count_by(rows: list[Mapping[str, Any]], key: str, allowed: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(str(row.get(key) or "UNKNOWN") for row in rows)
    return {value.lower(): int(counts.get(value, 0)) for value in allowed}


def _horizon_rows(rows: list[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {name: [] for name in HORIZON_BUCKETS}
    for row in rows:
        layer = str(row.get("source_layer") or "").lower()
        if layer not in buckets:
            layer = "unlayered"
        buckets[layer].append(dict(row))
    return buckets


def _first_actionable(rows: list[Mapping[str, Any]]) -> dict[str, Any] | None:
    for row in rows:
        if bool(row.get("actionable")):
            return dict(row)
    return None


def _fallback_projection(
    *,
    scope_type: str | None,
    scope_ref: str | None,
    error: str | None = None,
    finding: str = "kernel_scheduler_projection_unavailable",
) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "ok": False,
        "finding": finding,
        "error": error,
        "scope_type": scope_type,
        "scope_ref": scope_ref,
        "source_policy_id": "L1_SCHEDULER_V1",
        "summary": {state.lower(): 0 for state in SCHEDULE_STATES},
        "commitment_summary": {value.lower(): 0 for value in COMMITMENTS},
        "horizon": {name: [] for name in HORIZON_BUCKETS},
        "selected_candidate": None,
        "candidates": [],
        "blocking_factors": [],
        "policy": [
            "Scheduler projection unavailable; cockpit must not infer execution authority from missing scheduler state.",
            "No mutation authority is granted by this fallback projection.",
        ],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def build_scope_scheduler_projection(
    root: str | Path | None = None,
    *,
    scope_type: str | None = None,
    scope_ref: str | None = None,
    fallback_to_global: bool = True,
) -> dict[str, Any]:
    """Build a UI-safe scheduler projection for one scope.

    If the exact scope has no scheduler candidates and `fallback_to_global` is true,
    the projection includes the global schedule as context while preserving the
    requested scope fields.
    """

    shell_root = _shell_root(root)
    store_root = _kernel_store_root(shell_root)
    try:
        from .graph import KernelGraph
        from .index import KernelIndex
        from .scheduler import KernelScheduler
        from .store import KernelStore

        store = KernelStore(store_root)
        index = KernelIndex()
        indexed = index.build_from_store(store)
        graph = KernelGraph()
        graph.build_from_index(index)
        scheduler = KernelScheduler()

        requested_scope_type = scope_type
        requested_scope_ref = scope_ref
        if scope_type and scope_ref:
            projection = scheduler.build_schedule_projection(
                index,
                graph,
                scope_type=scope_type,
                scope_ref=scope_ref,
            )
            rendered = scheduler.render_schedule_projection(projection)
            if fallback_to_global and not rendered.get("candidates"):
                global_projection = scheduler.build_schedule_projection(index, graph)
                rendered = scheduler.render_schedule_projection(global_projection)
                rendered["requested_scope_type"] = requested_scope_type
                rendered["requested_scope_ref"] = requested_scope_ref
                rendered["scope_fallback"] = "global_schedule_used_because_requested_scope_has_no_candidates"
        else:
            projection = scheduler.build_schedule_projection(index, graph)
            rendered = scheduler.render_schedule_projection(projection)

        candidates = [dict(row) for row in list(rendered.get("candidates") or []) if isinstance(row, Mapping)]
        selected = rendered.get("selected_candidate")
        if not isinstance(selected, Mapping):
            selected = _first_actionable(candidates)

        blocking_factors = []
        for candidate in candidates:
            if str(candidate.get("scheduler_state") or "") == "BLOCKED":
                blocking_factors.append(
                    {
                        "candidate_id": candidate.get("candidate_id"),
                        "candidate_title": candidate.get("candidate_title"),
                        "state": "blocked",
                        "blocking_refs": list(candidate.get("blocking_refs") or []),
                        "warnings": list(candidate.get("warnings") or []),
                    }
                )

        return {
            "schema_id": SCHEMA_ID,
            "ok": True,
            "generated_at": rendered.get("generated_at"),
            "source_policy_id": rendered.get("policy_id") or "L1_SCHEDULER_V1",
            "ranking_factors": list(rendered.get("ranking_factors") or []),
            "policy_notes": list(rendered.get("policy_notes") or []),
            "scope_type": rendered.get("scope_type") or scope_type,
            "scope_ref": rendered.get("scope_ref") or scope_ref,
            "requested_scope_type": rendered.get("requested_scope_type"),
            "requested_scope_ref": rendered.get("requested_scope_ref"),
            "scope_fallback": rendered.get("scope_fallback"),
            "kernel_store_root": DEFAULT_KERNEL_STORE.as_posix(),
            "indexed_record_count": indexed,
            "summary": _count_by(candidates, "scheduler_state", SCHEDULE_STATES),
            "commitment_summary": _count_by(candidates, "commitment", COMMITMENTS),
            "horizon": _horizon_rows(candidates),
            "selected_candidate": dict(selected) if isinstance(selected, Mapping) else None,
            "candidates": candidates,
            "candidate_count": len(candidates),
            "blocking_factors": blocking_factors,
            "blocking_factor_count": len(blocking_factors),
            "policy": [
                "This is a UI-safe scheduler projection, not scheduler mutation authority.",
                "Mission phase, scheduler state, execution state, proof state, and accepted state must remain distinct.",
                "Carrier binding is advisory unless a lawful dispatch/receipt path is executed.",
            ],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    except Exception as exc:  # pragma: no cover - defensive projection fallback
        return _fallback_projection(
            scope_type=scope_type,
            scope_ref=scope_ref,
            error=exc.__class__.__name__,
        )
