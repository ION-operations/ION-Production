# Lucid Orchestrator HTTP Daemon

This directory hosts the Flask-based daemon that the prototype IDE uses for
live orchestration data. It exposes a small JSON API on port `5000` that can be
read by the Lucid dashboard (Vite app) as well as other automation surfaces.

## Quick start

```bash
# From the repository root
python -m venv .venv
.\.venv\Scripts\activate            # or source .venv/bin/activate on macOS/Linux
pip install -r packages/lucid_orchestrator/daemon/http_requirements.txt
python packages/lucid_orchestrator/daemon/http_daemon.py
```

Running from the repo root is important because the daemon reads snapshot files
via relative paths (see the Telemetry Snapshot section). Once the server is up
you can verify it with:

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/telemetry/progress
curl http://localhost:5000/api/telemetry/confidence-routing
```

## API surface

| Route | Method | Description |
| --- | --- | --- |
| `/api/health` | GET | Simple readiness check with timestamp + focused node. |
| `/api/nodes` | GET | Lists mocked orchestrator nodes that the prototype understands. |
| `/api/spec/<node_id>` | GET | Returns the SpecBlock for a node. |
| `/api/blueprint/<node_id>?depth=1` | GET | Blueprint slice with dependency context. |
| `/api/timeline/<node_id>?limit=10` | GET | Timeline summary and recent runs for a node. |
| `/api/propose-change/<node_id>` | POST | Returns a mocked change proposal payload. |
| `/api/focus/<node_id>` | POST | Persists the focused node inside the daemon. |
| `/api/telemetry/progress` | GET | Live predictive metrics snapshot. |
| `/api/telemetry/confidence-routing` | GET | Confidence routing tiers + git risk matrix. |

If a snapshot file cannot be read, each telemetry route falls back to the
built-in defaults baked into `http_daemon.py` so the IDE never hard fails.

## Telemetry snapshots

| File | Purpose | How to refresh |
| --- | --- | --- |
| `ide_orchestration/telemetry/predictive_metrics.json` | Predictive metrics rendered on the **Lucid Orchestrator -> Telemetry** tab. | Run the orchestrator progress tracker (see `ide_orchestration/telemetry/PROGRESS_DASHBOARD.md`) and copy the generated `predictive_metrics` section into this JSON. Update `last_updated`, `notes`, and any phase data that changed. |
| `ide_orchestration/telemetry/confidence_routing_snapshot.json` | Confidence tiers used by the **Lucid Orchestrator -> Confidence** tab. | `knowledge_architecture/WORKFLOW_ORCHESTRATION/confidence_routing.md` is the canonical source. When that doc changes, mirror the tiers/git risk tables here and bump the `updated` timestamp. |

Tips:

- Keep the JSON machine-friendly (double quotes, UTF-8). The daemon logs a
  warning and serves the fallback data if parsing fails, so watch the console.
- Commit refreshed snapshots alongside any docs describing the changes so RAG
  surfaces stay consistent.

## IDE integration

The Vite app under `packages/ide_chat_app` pulls telemetry from the daemon via
`progressTelemetryService` and `confidenceRoutingService`. Configure the IDE to
talk to the daemon by adding this to `packages/ide_chat_app/.env` (or your shell
env) before running `npm run dev`:

```
VITE_LUCID_DAEMON_URL=http://localhost:5000
```

If the environment variable is omitted the services default to
`http://localhost:5000`. When the daemon is unavailable the IDE logs a warning
and falls back to the static JSON artifacts listed above.

## Keeping the daemon healthy

- Restart the daemon after updating snapshot files so you immediately see the
  new payloads served over HTTP.
- Consider adding automated tests for the `/api/telemetry/*` routes by using the
  Flask test client; manual curl checks are currently the only guardrail.
- The daemon currently trusts local file paths supplied via `Path(...)`. If you
  run it from outside the repo root, pass absolute paths or set `PYTHONPATH`
  accordingly so the files resolve.
