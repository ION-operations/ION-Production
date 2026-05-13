# Progress Dashboard

This dashboard collects outputs from `progress_tracker.py` so coordinators can
see phase/workstream completion, predicted ETAs, and recently generated dynamic
tasks.

## How to Refresh

1. Update completion lists (e.g., `--completed-tasks task_cursor_landscape ...`).
2. Run:

```bash
python -m ide_orchestration.orchestrator.run \
  --progress-report \
  --completed-tasks task_cursor_landscape task_codex_capabilities \
  > tmp_progress.json
```

3. Copy the `predictive_metrics` section into `predictive_metrics.json`.
4. Update this dashboard with any callouts (blocked workstreams, ETA slips).

## Fields

- **Phases Table:** Percent complete vs. total tasks.
- **Workstream Status:** Completed vs. total tasks per workstream.
- **Predictive Metrics:** Velocity-based ETA estimates (tasks/day).
- **Dynamic Task Feed:** Use `--generate-dynamic --gate-context context.json` to list
  newly proposed tasks and track remediation progress.
