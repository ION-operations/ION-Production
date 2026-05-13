[CODEX] | ACTIVE | Window injector Phase A scaffold landed

- `packages/jarvis_injector/` now exists with config, queue, telemetry, target registry, FastAPI server, Win32 window controller, and keyboard adapter scaffold
- Root target configs added under `config/window_targets/`
- Launcher added at `scripts/launchers/START_WINDOW_INJECTOR.ps1`
- JOC typed client seam added at `packages/joc/src/services/windowInjectorClient.ts`
- Python syntax check passed: `python -m compileall packages/jarvis_injector/src/jarvis_injector`
- `packages/joc` build still fails on unrelated pre-existing `AssistantRail.tsx` errors

This lane is now past planning and into bounded implementation.
