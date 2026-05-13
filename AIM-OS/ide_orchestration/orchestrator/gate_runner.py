"""Gate evaluation helpers for the IDE orchestration program.

GateRunner loads ``ide_orchestration/policy/gates.json`` and provides light
weight evaluators for task / phase / epic gates.  The goal is not to replace
the full AIM-OS infrastructure but to offer fast feedback when working on the
ChainSpec or running local drills.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .graph_manager import GraphManager, TaskNode


@dataclass
class GateResult:
    gate_id: str
    level: str
    status: str  # passed | failed | pending
    blocking: bool
    details: str


class GateRunner:
    """Evaluates gate definitions against lightweight context data."""

    def __init__(
        self,
        graph_manager: GraphManager,
        gate_policy: str | Path = "ide_orchestration/policy/gates.json",
    ) -> None:
        self.graph_manager = graph_manager
        self.policy_path = Path(gate_policy)
        self.policy = self._load_policy()
        self.gates = self.policy.get("gates", {})

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def evaluate_task(
        self, task_id: str, context: Optional[Dict[str, Any]] = None
    ) -> List[GateResult]:
        task = self.graph_manager.get_task(task_id)
        gate_ids = task.gate_refs or []
        return self._evaluate_gate_list(
            gate_ids=gate_ids, level="task", context=context or {}, task_node=task
        )

    def evaluate_phase(
        self, phase_id: str, gate_ids: Optional[Iterable[str]] = None, context=None
    ) -> List[GateResult]:
        ids = list(gate_ids) if gate_ids else list(self.gates.get("phase", {}).keys())
        return self._evaluate_gate_list(
            gate_ids=ids, level="phase", context=context or {}, phase_id=phase_id
        )

    def evaluate_epic(
        self, gate_ids: Optional[Iterable[str]] = None, context=None
    ) -> List[GateResult]:
        ids = list(gate_ids) if gate_ids else list(self.gates.get("epic", {}).keys())
        return self._evaluate_gate_list(
            gate_ids=ids, level="epic", context=context or {}
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _load_policy(self) -> Dict[str, Any]:
        if not self.policy_path.exists():
            raise FileNotFoundError(f"Gate policy not found: {self.policy_path}")
        with self.policy_path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def _evaluate_gate_list(
        self,
        gate_ids: Iterable[str],
        level: str,
        context: Dict[str, Any],
        task_node: Optional[TaskNode] = None,
        phase_id: Optional[str] = None,
    ) -> List[GateResult]:
        definitions = self.gates.get(level, {})
        results: List[GateResult] = []
        for gate_id in gate_ids:
            definition = definitions.get(self._normalize_gate_key(gate_id))
            if not definition:
                results.append(
                    GateResult(
                        gate_id=gate_id,
                        level=level,
                        status="failed",
                        blocking=True,
                        details="Gate definition missing from policy",
                    )
                )
                continue

            status, details = self._dispatch_gate(
                gate_id=gate_id,
                definition=definition,
                level=level,
                context=context,
                task_node=task_node,
                phase_id=phase_id,
            )
            results.append(
                GateResult(
                    gate_id=gate_id,
                    level=level,
                    status=status,
                    blocking=bool(definition.get("blocking", False)),
                    details=details,
                )
            )
        return results

    def _dispatch_gate(
        self,
        gate_id: str,
        definition: Dict[str, Any],
        level: str,
        context: Dict[str, Any],
        task_node: Optional[TaskNode],
        phase_id: Optional[str],
    ) -> tuple[str, str]:
        method = definition.get("method")
        evaluator_name = self._EVALUATORS.get(method)
        evaluator = getattr(self, evaluator_name, self._default_pending)
        return evaluator(
            gate_id=gate_id,
            definition=definition,
            level=level,
            context=context,
            task_node=task_node,
            phase_id=phase_id,
        )

    # ------------------------------------------------------------------ #
    # Gate evaluators
    # ------------------------------------------------------------------ #
    def _default_pending(self, **_) -> tuple[str, str]:
        return ("pending", "No evaluator registered for gate method")

    def _check_seg_validate(self, **kwargs) -> tuple[str, str]:
        evidence = kwargs["context"].get("evidence", {})
        tier_a = evidence.get("tier_a_citations", 0)
        if tier_a >= 1:
            return ("passed", f"{tier_a} Tier A citations logged")
        return ("pending", "Awaiting Tier A citation evidence")

    def _check_spec_schema(self, **kwargs) -> tuple[str, str]:
        spec = kwargs["context"].get("spec_validation", {})
        if spec.get("errors"):
            return ("failed", f"Spec schema errors: {spec['errors']}")
        if spec.get("validated"):
            return ("passed", "Spec schema validation succeeded")
        return ("pending", "No schema validation results supplied")

    def _check_policy_alignment(self, **kwargs) -> tuple[str, str]:
        policy_state = kwargs["context"].get("policy_state", {})
        if policy_state.get("in_sync"):
            return ("passed", "Policy diffs reconciled with AIM-OS thresholds")
        return (
            "pending",
            "Alignment not confirmed; provide policy_state.in_sync flag",
        )

    def _check_api_contract(self, **kwargs) -> tuple[str, str]:
        adapters = kwargs["context"].get("adapter_tests", {})
        if adapters.get("contract_passed"):
            return ("passed", "Adapter contract tests passed")
        return ("pending", "Adapter contract results missing")

    def _check_unit_tests(self, **kwargs) -> tuple[str, str]:
        tests = kwargs["context"].get("tests", {})
        coverage = float(tests.get("coverage", 0))
        threshold = float(kwargs["definition"].get("threshold", 0))
        if tests.get("passed") and coverage >= threshold:
            return ("passed", f"Coverage {coverage:.2f} >= {threshold:.2f}")
        if tests.get("passed"):
            return ("pending", f"Coverage {coverage:.2f} < threshold {threshold:.2f}")
        return ("pending", "Tests not executed yet")

    def _check_sdf_cvf(self, **kwargs) -> tuple[str, str]:
        qa = kwargs["context"].get("qa_suite", {})
        if qa.get("blocking_defects", 0) == 0 and qa.get("executed"):
            return ("passed", "SDF-CVF suite executed with zero blocking defects")
        if qa.get("executed"):
            return ("failed", f"{qa.get('blocking_defects')} blocking defects found")
        return ("pending", "QA suite not executed")

    def _check_evidence(self, **kwargs) -> tuple[str, str]:
        evidence = kwargs["context"].get("evidence", {})
        if evidence.get("cmc_atoms") and evidence.get("hhni_vectors"):
            return ("passed", "Evidence logged to CMC + HHNI")
        return ("pending", "Evidence atoms missing")

    def _check_phase_coverage(self, **kwargs) -> tuple[str, str]:
        coverage = kwargs["context"].get("coverage", {})
        complete = coverage.get("workstreams_complete", 0)
        total = coverage.get("workstreams_total", 0)
        if total and complete == total:
            return ("passed", "All workstreams reported complete")
        return ("pending", "Coverage data incomplete")

    def _check_vif_threshold(self, **kwargs) -> tuple[str, str]:
        scores = kwargs["context"].get("vif_scores", {})
        phase_id = kwargs.get("phase_id")
        threshold = kwargs["definition"].get("thresholds", {}).get(phase_id)
        score = scores.get(phase_id or "default")
        if threshold is None or score is None:
            return ("pending", "VIF scores not supplied")
        if score >= threshold:
            return ("passed", f"VIF {score:.2f} >= threshold {threshold:.2f}")
        return ("failed", f"VIF {score:.2f} below threshold {threshold:.2f}")

    def _check_launch(self, **kwargs) -> tuple[str, str]:
        launch = kwargs["context"].get("launch", {})
        if all(
            [
                launch.get("checklist_complete"),
                launch.get("dashboards_live"),
                launch.get("board_updated"),
            ]
        ):
            return ("passed", "Launch checklist complete")
        return ("pending", "Launch readiness signals incomplete")

    def _normalize_gate_key(self, gate_id: str) -> str:
        if "." in gate_id:
            prefix, suffix = gate_id.split(".", 1)
            if prefix in {"task", "phase", "epic"}:
                return suffix
        return gate_id

    _EVALUATORS = {
        "seg_validate": "_check_seg_validate",
        "spec_schema_check": "_check_spec_schema",
        "policy_diff_check": "_check_policy_alignment",
        "api_contract_audit": "_check_api_contract",
        "test_runner": "_check_unit_tests",
        "sdf_cvf_suite": "_check_sdf_cvf",
        "cmc_evidence_check": "_check_evidence",
        "coverage_check": "_check_phase_coverage",
        "vif_aggregate": "_check_vif_threshold",
        "launch_checklist": "_check_launch",
    }


__all__ = ["GateRunner", "GateResult"]
