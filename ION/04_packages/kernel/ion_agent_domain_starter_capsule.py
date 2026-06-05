"""Compatibility wrapper for the old agent/domain starter name.

The canonical starter is now `ion_context_starter_capsule`: a clean
single-session context capsule with no invented agent or role-rehearsal surfaces.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .ion_context_starter_capsule import (
    build_context_starter_capsule_projection,
    create_context_starter_capsule,
    main,
    materialize_context_starter_capsule,
)


def materialize_agent_domain_starter_capsule(root: str | Path | None = None) -> dict[str, Any]:
    return materialize_context_starter_capsule(root)


def build_agent_domain_starter_capsule_projection(root: str | Path | None = None) -> dict[str, Any]:
    return build_context_starter_capsule_projection(root)


__all__ = [
    "build_agent_domain_starter_capsule_projection",
    "create_context_starter_capsule",
    "materialize_agent_domain_starter_capsule",
]


if __name__ == "__main__":
    raise SystemExit(main())
