# IDE Orchestration Engine

Scaffolding for the epic orchestration system (graph manager, scheduler, gate runner, telemetry).

## Modules
- `graph_manager.py` – loads ChainSpec, builds dependency graph, computes ready queues.
- `scheduler.py` – capability-based assignment against `agents/registry.json`.
- `gate_runner.py` – evaluates task/phase/epic gates from `policy/gates.json`.
- `dynamic_task_generator.py` – emits follow-up tasks using `tasks/dynamic_rules.yaml`.
- `progress_tracker.py` – aggregates phase/workstream completion + predictive metrics.
- `run.py` – CLI/entrypoint for status, scheduling, and gate evaluation.
- `utils/telemetry.py` – helpers for logging to CMC/HHNI.
- `api/adapter_chatgpt.py`, etc. (future) – adapters for external APIs.

## CLI usage
```bash
# list ready tasks
python -m ide_orchestration.orchestrator.run --list-ready

# compute suggested assignments (requires agents/registry.json)
python -m ide_orchestration.orchestrator.run --schedule

# run dynamic task generator tests
python -m unittest ide_orchestration.orchestrator.tests.test_dynamic_tasks

# evaluate gates for a specific task using context payload
python -m ide_orchestration.orchestrator.run \
  --gate-task task_dynamic_task_generator \
  --gate-context /tmp/gate_context.json

# emit progress report (phases/workstreams/predictive metrics)
python -m ide_orchestration.orchestrator.run \
  --progress-report \
  --completed-tasks task_cursor_landscape task_codex_capabilities

# save / load checkpoints
python -m ide_orchestration.orchestrator.run \
  --save-checkpoint before_big_change \
  --completed-tasks task_cursor_landscape task_codex_capabilities

python -m ide_orchestration.orchestrator.run \
  --load-checkpoint before_big_change \
  --completed-tasks task_cursor_landscape
```
