[CODEX -> OPUS] HANDOFF
- TASK: Phase A scaffold for the Computer Action Platform runtime
- PRIORITY: P1
- FILES: `packages/jarvis_injector/`, `config/window_targets/`, `scripts/launchers/START_WINDOW_INJECTOR.ps1`, `packages/joc/src/services/windowInjectorClient.ts`, `packages/joc/src/types/windowInjector.ts`
- STATE: Landed and syntax-checked. Runtime currently supports target registry, execution queue, telemetry, Win32 window resolve/restore/activate, and keyboard adapter scaffolding.
- NEEDS: Decide whether you want next lane to be JOC UI wiring, richer verification, or UIA/CDP implementation.
