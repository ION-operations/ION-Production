"""Dynamic task generator for AIM-OS orchestration.

This module reads ``tasks/dynamic_rules.yaml`` to determine when follow-up tasks
should be generated based on telemetry/context signals (HHNI gaps, gate
failures, etc.).  The goal is to provide a deterministic, local mechanism for
expanding the ChainSpec without reaching out to remote services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import operator
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class GeneratedTask:
    """Represents a dynamically produced task specification."""

    id: str
    description: str
    phase_id: str
    workstream_id: str
    ai_modes: List[str] = field(default_factory=list)
    gate_refs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DynamicTaskGenerator:
    """Evaluates rule catalog and emits tasks whose conditions match context."""

    def __init__(
        self,
        rules_path: str | Path = "ide_orchestration/orchestrator/tasks/dynamic_rules.yaml",
    ) -> None:
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Dynamic rules file missing: {self.rules_path}")
        with self.rules_path.open("r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp) or {}
        rules = data.get("rules", [])
        if not isinstance(rules, list):
            raise ValueError("dynamic_rules.yaml must contain a top-level 'rules' list")
        return data

    def list_rule_ids(self) -> List[str]:
        return [rule["id"] for rule in self.rules.get("rules", [])]

    def generate_tasks(
        self,
        context: Dict[str, Any],
        *,
        exclude_tasks: Optional[List[str]] = None,
    ) -> List[GeneratedTask]:
        """Return generated tasks that match the supplied context signals."""
        exclude = set(exclude_tasks or [])
        generated: List[GeneratedTask] = []
        for rule in self.rules.get("rules", []):
            rule_id = rule.get("id")
            if not rule_id or rule_id in exclude:
                continue
            if not self._rule_matches(rule, context):
                continue
            generated.append(self._build_task(rule, context))
        return generated

    # ------------------------------------------------------------------ #
    # Rule evaluation helpers
    # ------------------------------------------------------------------ #
    def _rule_matches(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        conditions = rule.get("conditions", [])
        if not conditions:
            return True  # unconditional rules are allowed
        for condition in conditions:
            path = condition.get("path")
            operator_name = condition.get("operator", "equals")
            expected = condition.get("value")
            actual = _extract(context, path, default=None)
            comparator = _OPERATORS.get(operator_name)
            if comparator is None:
                return False
            if operator_name == "exists":
                if actual is None:
                    return False
            else:
                try:
                    if not comparator(actual, expected):
                        return False
                except Exception:
                    return False
        return True

    def _build_task(self, rule: Dict[str, Any], context: Dict[str, Any]) -> GeneratedTask:
        # Allow templates to reference context values via dotted paths.
        metadata = {
            "source_rule": rule.get("id"),
            "context_snapshot": {
                key: _extract(context, key, default=None)
                for key in rule.get("context_snapshot", [])
            },
        }
        return GeneratedTask(
            id=rule["task"]["id"],
            description=rule["task"].get("description", rule["task"]["id"]),
            phase_id=rule["task"]["phase"],
            workstream_id=rule["task"]["workstream"],
            ai_modes=rule["task"].get("ai_modes", []),
            gate_refs=rule["task"].get("gate_refs", []),
            dependencies=rule["task"].get("dependencies", []),
            metadata=metadata,
        )


def _extract(payload: Dict[str, Any], path: Optional[str], default: Any) -> Any:
    if not path:
        return default
    parts = path.split(".")
    value: Any = payload
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return default
    return value


_OPERATORS = {
    "equals": operator.eq,
    "not_equals": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "exists": lambda actual, expected: actual is not None,
}


__all__ = ["DynamicTaskGenerator", "GeneratedTask"]
