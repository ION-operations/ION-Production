"""CLI entrypoint for the IDE orchestration engine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .dynamic_task_generator import DynamicTaskGenerator, GeneratedTask
from .gate_runner import GateRunner, GateResult
from .scheduler import Scheduler, TaskAssignment
from .graph_manager import GraphManager
from .progress_tracker import ProgressTracker
from .recovery import RecoveryEngine, Checkpoint


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="IDE Orchestration Runner (status + ready queues)"
    )
    parser.add_argument(
        "--spec",
        default="ide_orchestration/chains/ChainSpec.yaml",
        help="Path to ChainSpec.yaml",
    )
    parser.add_argument(
        "--completed-tasks",
        nargs="*",
        default=[],
        help="Task IDs considered completed",
    )
    parser.add_argument(
        "--completed-phases",
        nargs="*",
        default=[],
        help="Phase IDs considered complete/unlocked",
    )
    parser.add_argument(
        "--blocked-tasks",
        nargs="*",
        default=[],
        help="Task IDs temporarily blocked",
    )
    parser.add_argument(
        "--list-ready",
        action="store_true",
        help="List tasks ready for execution",
    )
    parser.add_argument(
        "--phase-status",
        action="store_true",
        help="Print phase completion status",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Compute agent assignments for ready tasks",
    )
    parser.add_argument(
        "--agent-registry",
        default="ide_orchestration/agents/registry.json",
        help="Path to agent registry JSON",
    )
    parser.add_argument(
        "--gate-policy",
        default="ide_orchestration/policy/gates.json",
        help="Path to gate policy JSON",
    )
    parser.add_argument(
        "--gate-task",
        help="Evaluate task-level gates for the provided task ID",
    )
    parser.add_argument(
        "--gate-phase",
        help="Evaluate phase-level gates for the provided phase ID",
    )
    parser.add_argument(
        "--gate-epic",
        action="store_true",
        help="Evaluate epic-level gates",
    )
    parser.add_argument(
        "--gate-context",
        help="Optional path to JSON payload with gate context data",
    )
    parser.add_argument(
        "--generate-dynamic",
        action="store_true",
        help="Run dynamic task generator against the provided context payload",
    )
    parser.add_argument(
        "--dynamic-rules",
        default="ide_orchestration/orchestrator/tasks/dynamic_rules.yaml",
        help="Path to dynamic task rules YAML",
    )
    parser.add_argument(
        "--progress-report",
        action="store_true",
        help="Emit progress tracker summary (phases/workstreams/predictions)",
    )
    parser.add_argument(
        "--save-checkpoint",
        help="Save completed task set to a named checkpoint",
    )
    parser.add_argument(
        "--load-checkpoint",
        help="Load a checkpoint and return restored task list",
    )
    parser.add_argument(
        "--list-checkpoints",
        action="store_true",
        help="List available checkpoints",
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="ide_orchestration/orchestrator/state/checkpoints",
        help="Directory used for checkpoint storage",
    )
    parser.add_argument(
        "--recovery-telemetry",
        default="ide_orchestration/telemetry/recovery_log.jsonl",
        help="Telemetry log path for recovery events",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manager = GraphManager(args.spec)

    output = {
        "spec_path": str(Path(args.spec).resolve()),
        "completed_tasks": args.completed_tasks,
        "completed_phases": args.completed_phases,
    }

    gate_context = _load_gate_context(args.gate_context)

    if args.list_ready:
        ready = manager.compute_ready_tasks(
            completed_tasks=set(args.completed_tasks),
            completed_phases=set(args.completed_phases),
            blocked_tasks=set(args.blocked_tasks),
        )
        output["ready_tasks"] = [
            {
                "id": task.id,
                "description": task.description,
                "phase": task.phase_id,
                "workstream": task.workstream_id,
                "dependencies": task.dependencies,
            }
            for task in ready
        ]

    if args.phase_status:
        status = manager.compute_phase_status(set(args.completed_tasks))
        output["phase_status"] = {
            phase_id: {"completed": done, "total": total}
            for phase_id, (done, total) in status.items()
        }

    if args.schedule:
        scheduler = Scheduler(manager, agent_registry=args.agent_registry)
        assignments = scheduler.build_schedule(
            completed_tasks=set(args.completed_tasks),
            completed_phases=set(args.completed_phases),
            blocked_tasks=set(args.blocked_tasks),
        )
        output["schedule"] = [_assignment_dict(a) for a in assignments]

    if args.gate_task or args.gate_phase or args.gate_epic:
        runner = GateRunner(manager, gate_policy=args.gate_policy)
        gate_results: Dict[str, List[Dict[str, str]]] = {}
        if args.gate_task:
            gate_results["task"] = [
                _gate_result_dict(result)
                for result in runner.evaluate_task(
                    task_id=args.gate_task, context=gate_context
                )
            ]
        if args.gate_phase:
            gate_results.setdefault("phase", [])
            gate_results["phase"] = [
                _gate_result_dict(result)
                for result in runner.evaluate_phase(
                    phase_id=args.gate_phase, context=gate_context
                )
            ]
        if args.gate_epic:
            gate_results.setdefault("epic", [])
            gate_results["epic"] = [
                _gate_result_dict(result)
                for result in runner.evaluate_epic(context=gate_context)
        ]
        output["gate_results"] = gate_results

    if args.generate_dynamic:
        generator = DynamicTaskGenerator(rules_path=args.dynamic_rules)
        dynamic_tasks = generator.generate_tasks(
            gate_context, exclude_tasks=args.completed_tasks
        )
        output["dynamic_tasks"] = [_dynamic_task_dict(task) for task in dynamic_tasks]

    if args.progress_report:
        tracker = ProgressTracker(manager)
        output["progress_report"] = tracker.summarize(
            completed_tasks=set(args.completed_tasks)
        )

    if args.list_checkpoints or args.save_checkpoint or args.load_checkpoint:
        recovery_engine = RecoveryEngine(
            checkpoint_dir=args.checkpoint_dir,
            telemetry_log=args.recovery_telemetry,
        )
        if args.list_checkpoints:
            output["checkpoints"] = [
                _checkpoint_dict(cp) for cp in recovery_engine.available_checkpoints()
            ]
        if args.save_checkpoint:
            saved = recovery_engine.checkpoint(
                args.save_checkpoint, set(args.completed_tasks)
            )
            output["checkpoint_saved"] = _checkpoint_dict(saved)
        if args.load_checkpoint:
            restored = recovery_engine.rollback(
                args.load_checkpoint, set(args.completed_tasks)
            )
            if restored:
                output["checkpoint_restored"] = _checkpoint_dict(restored)
            else:
                output["checkpoint_restored"] = None

    print(json.dumps(output, indent=2))


def _load_gate_context(path: Optional[str]) -> Dict:
    if not path:
        return {}
    ctx_path = Path(path)
    if not ctx_path.exists():
        raise FileNotFoundError(f"Gate context file not found: {ctx_path}")
    with ctx_path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _assignment_dict(assignment: TaskAssignment) -> Dict[str, Any]:
    return {
        "task_id": assignment.task_id,
        "agent_id": assignment.agent_id,
        "score": assignment.score,
        "rationale": assignment.rationale,
        "metadata": assignment.metadata,
    }


def _gate_result_dict(result: GateResult) -> Dict[str, str]:
    return {
        "gate_id": result.gate_id,
        "level": result.level,
        "status": result.status,
        "blocking": result.blocking,
        "details": result.details,
    }


def _dynamic_task_dict(task: GeneratedTask) -> Dict[str, Any]:
    return {
        "id": task.id,
        "description": task.description,
        "phase": task.phase_id,
        "workstream": task.workstream_id,
        "gate_refs": task.gate_refs,
        "ai_modes": task.ai_modes,
        "dependencies": task.dependencies,
        "metadata": task.metadata,
    }


def _checkpoint_dict(cp: Checkpoint) -> Dict[str, Any]:
    return {
        "name": cp.name,
        "completed_tasks": sorted(cp.completed_tasks),
        "notes": cp.notes,
        "path": str(cp.path),
    }


if __name__ == "__main__":
    main()
