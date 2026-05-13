# Standalone Dashboard Launcher - Quick Guide

## Quick Launch

**Double-click:** `LAUNCH_STANDALONE_VISIBLE.bat`

This will:
- Show a visible terminal window with all output
- Check/install dependencies
- Start the dev server
- Open your browser automatically
- Surface any errors clearly

## What You'll See

The terminal window displays:
- Setup status (dependencies, build directory)
- Server startup messages
- TypeScript/build errors
- Server URL (http://localhost:3000)
- Live reload status

## Prototype Panels to Explore

- **Lucid Orchestrator -> Telemetry tab:** Reads `ide_orchestration/telemetry/predictive_metrics.json` so you can inspect orchestrator ETA metrics without leaving the UI.
- **Lucid Orchestrator -> Confidence tab:** Mirrors `knowledge_architecture/WORKFLOW_ORCHESTRATION/confidence_routing.md`, giving you the capability tiers + git risk matrix inside the IDE.
- Use the refresh buttons on each tab after you run the orchestrator CLI to pull the latest artifacts without restarting the dev server.

### Live Telemetry Hookups

- Set `VITE_LUCID_DAEMON_URL` in `.env` (defaults to `http://localhost:5000`).
- When the Lucid daemon exposes `/api/telemetry/progress` and `/api/telemetry/confidence-routing`, the IDE panels will load real data; otherwise they fall back to the local artifacts mentioned above.
- Follow `packages/lucid_orchestrator/daemon/README.md` for daemon setup, curl health checks, and guidance on keeping `ide_orchestration/telemetry/*.json` snapshots fresh so the live payloads stay up to date.

## If You See Errors

**Common fixes:**
1. `npm install` errors -> run manually and ensure Node.js is installed (`node --version`).
2. Port already in use -> stop the process on port 3000 or change the port in `vite.config.ts`.
3. TypeScript errors -> read the terminal output for file + line, then fix or temporarily suppress.
4. Module not found -> run `npm install` again and ensure `node_modules` exists.

## Success Indicators

You'll know it's working when you see:
```
  VITE v5.x.x  ready in XXX ms

  Local:   http://localhost:3000/
  Network: use --host to expose
```
Then your browser should open automatically.

## Debugging Tips

The visible terminal shows all console output, build diagnostics, TypeScript errors, and runtime stack traces. Leave it open while iterating on the prototype IDE.
