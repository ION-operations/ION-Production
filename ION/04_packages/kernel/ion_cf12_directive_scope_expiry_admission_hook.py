"""Kernel hook surface for CF-12 directive scope/expiry findings (candidate).

Logic lives under domain.operator_sovereignty_and_directive_admission runtime module.
This file only loads that module and exposes admission-time entrypoints. Never blocks.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Mapping

_DOMAIN_RUNTIME_REL = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.operator_sovereignty_and_directive_admission/runtime/"
    "ion_cf12_directive_scope_expiry_admission_findings.candidate.py"
)

_MODULE_CACHE: Any = None


def _load_domain_module(shell: Path) -> Any | None:
    global _MODULE_CACHE
    if _MODULE_CACHE is not None:
        return _MODULE_CACHE
    script = shell / _DOMAIN_RUNTIME_REL
    if not script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ion_cf12_directive_admission_findings", script)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MODULE_CACHE = mod
    return mod


def maybe_record_prompt_spawn_cf12_findings(
    shell: Path,
    *,
    intent: Mapping[str, Any],
    spawn_admission: Mapping[str, Any] | None = None,
    write: bool = True,
) -> dict[str, Any] | None:
    mod = _load_domain_module(shell)
    if mod is None:
        return None
    return mod.record_prompt_spawn_intent_findings(
        shell, intent=intent, spawn_admission=spawn_admission, write=write
    )


def maybe_record_queue_row_cf12_findings(
    shell: Path,
    *,
    row: Mapping[str, Any],
    write: bool = True,
) -> dict[str, Any] | None:
    mod = _load_domain_module(shell)
    if mod is None:
        return None
    return mod.record_durable_queue_row_findings(shell, row=row, write=write)
