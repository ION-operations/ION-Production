# Computer Action Platform Runtime Plan

> **Classification:** `runtime` + `cockpit`
> **Purpose:** Turn the operator blueprint for a window-aware self-healing injector into the formal implementation plan for a local Windows computer-action platform that JOC can drive as a runtime.
> **Status:** Phase A scaffold started

## 1. Decision

Build this as a new local runtime package, not as an extension of `packages/browser-automation-service/`.

Reason:

- `packages/browser-automation-service/` is the current browser automation lane for JOC, but ChatGPT via BAS is explicitly blocked by Finding #19 and the CODEX genome stop order.
- The runtime must own real Windows surfaces, including restore, foreground activation, UIA, keyboard fallback, motion execution, and window-scoped visual matching.
- Executive scope lock says AIM-OS should treat API/CLI execution as runtime and JOC as cockpit. This feature fits that split exactly.
- Models advise, repair, classify, and generate plans. Execution remains inside the controlled local action engine.

## 2. Platform Layers

Treat this as a Computer Action Platform with five permanent layers:

1. Operator runtime on Windows.
2. Perception stack for DOM, UIA, screenshots, and visual templates.
3. Action engine for windowing, keyboard, mouse, browser, and app controls.
4. Memory system for locators, templates, motions, workflows, fingerprints, and episode logs.
5. Agent layer where Codex CLI, Gemini CLI, and Gemini API act as bounded planner/repair/code-engineering roles over the runtime tool surface.

## 3. Repo Placement

Create a new Python package:

```text
packages/jarvis_injector/
  pyproject.toml
  README.md
  src/jarvis_injector/
    app.py
    config.py
    api/
      server.py
      routes_health.py
      routes_targets.py
      routes_dispatch.py
      routes_artifacts.py
    core/
      models.py
      enums.py
      errors.py
      policy.py
      state_machine.py
      dispatcher.py
      queue.py
      telemetry.py
    memory/
      vaults.py
    agents/
      roles.py
    registry/
      target_registry.py
      locator_store.py
      template_store.py
      fingerprint_store.py
    windows/
      window_controller.py
      hotkeys.py
      input_driver.py
      capture.py
      process_probe.py
      geometry.py
    adapters/
      base.py
      manager.py
      cdp_adapter.py
      uia_adapter.py
      keyboard_adapter.py
      visual_adapter.py
    vision/
      matcher.py
      templates.py
      regions.py
      preprocess.py
    verification/
      engine.py
      dom.py
      uia.py
      visual.py
    repair/
      models.py
      planner.py
      validator.py
      executor.py
    workflows/
      graph.py
    runtime/
      tray_app.py
      cli.py
      service.py
  tests/
    unit/
    integration/
    fixtures/
```

JOC integration points:

```text
packages/joc/src/services/windowInjectorClient.ts
packages/joc/src/types/windowInjector.ts
packages/joc/src/pages/DispatchPage.tsx          # extend existing dispatch surface
packages/joc/src/store/sessionStore.ts           # execution status / queue wiring
scripts/launchers/START_WINDOW_INJECTOR.ps1
```

Persistent data:

```text
config/window_targets/*.json
state/window_injector/locators/*.json
state/window_injector/templates/<target>/*.png
logs/window_injector/executions/*.jsonl
logs/window_injector/screenshots/*.png
```

Current scaffold landed:

- `packages/jarvis_injector/pyproject.toml`
- `packages/jarvis_injector/src/jarvis_injector/`
- `config/window_targets/*.json`
- `scripts/launchers/START_WINDOW_INJECTOR.ps1`
- `packages/joc/src/services/windowInjectorClient.ts`
- `packages/joc/src/types/windowInjector.ts`
- `packages/jarvis_injector/src/jarvis_injector/capture/`
- `packages/joc/src/types/windowCapture.ts`

## 4. Runtime Boundaries

### In Scope

- Restore/select a known window
- Inject a fixed or operator-supplied command
- Use ordered adapters: CDP -> UIA -> keyboard -> visual
- Verify success before reporting completion
- Persist improved locators and winning templates
- Expose a local API and CLI that JOC and other local agents can call

### Out of Scope for MVP

- Unbounded agent-generated code execution
- Full-screen blind clicking
- BAS-based ChatGPT automation resurrection
- OCR-heavy flows as a primary strategy
- Cross-machine orchestration
- Direct model control of mouse/keyboard/window APIs outside the runtime

## 5. Architecture

```text
JOC (cockpit) -> windowInjectorClient.ts -> Jarvis Injector API (:5013 default)
                                            |
                                            v
                                     DispatchService
                                            |
                     +----------------------+----------------------+
                     |                                             |
                     v                                             v
               TargetRegistry                                 ExecutionQueue
                     |                                             |
                     v                                             v
               WindowController ----------------------------> AdapterManager
                                                                    |
                             +------------------+--------------------+------------------+
                             |                  |                    |                  |
                             v                  v                    v                  v
                        CdpAdapter          UiaAdapter        KeyboardAdapter      VisualAdapter
                             \                  |                    |                  /
                              \                 |                    |                 /
                               +----------------+--------------------+----------------+
                                                |
                                                v
                                         VerificationEngine
                                                |
                                                v
                                           RepairPlanner
                                                |
                                                v
                                    LocatorStore / TemplateStore
```

## 6. Memory Vaults

The memory system is first-class. Split it into six persistent stores:

- Locator Vault: DOM selectors, alternate selectors, UIA queries, role/name/path patterns.
- Template Vault: cropped button images, theme variants, DPI variants, confidence history.
- Motion Vault: saved mouse trajectories, drag gestures, scroll patterns, cursor approach strategies.
- Workflow Vault: task graphs, preconditions, postconditions, and repair branches.
- Fingerprint Vault: version hints, window signatures, structure hashes, layout drift markers.
- Episode Log: every execution, adapter chosen, timings, screenshots, repair outputs, and latency/confidence.

## 7. Internal Agent Roles

Do not use one giant AI inside the platform. Use bounded roles:

- Planner agent: convert intent into a task graph.
- Navigator agent: choose CDP, UIA, keyboard, visual, or motion path.
- Vision repair agent: inspect screenshots and crops when locators drift.
- Artifact curator agent: decide what new templates, locators, or motions should persist.
- Code engineer agent: use Codex CLI to extend adapters, tests, and parsers.
- Auditor agent: confirm the action path was safe, reproducible, and verified.

## 8. Core Class Map

### Runtime Entry

```python
class InjectorApplication:
    def build_runtime(self) -> "RuntimeServices": ...


@dataclass
class RuntimeServices:
    config: "InjectorConfig"
    queue: "ExecutionQueue"
    dispatcher: "DispatchService"
    tray: "TrayController | None"
    hotkeys: "GlobalHotkeyLoop | None"
```

### Dispatch Core

```python
class DispatchService:
    def submit(self, request: "DispatchRequest") -> "DispatchAccepted": ...
    def run_now(self, request: "DispatchRequest") -> "DispatchResult": ...
    def get_execution(self, execution_id: str) -> "ExecutionRecord | None": ...


class DispatchExecutor:
    def execute(self, request: "DispatchRequest") -> "DispatchResult": ...


class DispatchStateMachine:
    def run(self, ctx: "DispatchContext") -> "DispatchContext": ...
```

### Windowing

```python
class Win32WindowController:
    def find_window(self, target: "TargetProfile") -> "ResolvedWindow | None": ...
    def restore_if_minimized(self, window: "ResolvedWindow") -> None: ...
    def activate(self, window: "ResolvedWindow") -> None: ...
    def wait_until_ready(self, window: "ResolvedWindow", timeout_ms: int) -> None: ...
    def standardize_geometry(self, window: "ResolvedWindow") -> None: ...
```

### Adapter Layer

```python
class AdapterManager:
    def choose(self, ctx: "DispatchContext") -> "AdapterSelection": ...


class BaseAdapter(Protocol):
    name: str

    def probe(self, ctx: "DispatchContext") -> "AdapterProbe": ...
    def locate_input(self, ctx: "DispatchContext") -> "LocateResult": ...
    def set_text(self, ctx: "DispatchContext", located: "LocateResult") -> "ActionResult": ...
    def submit(self, ctx: "DispatchContext", located: "LocateResult") -> "ActionResult": ...
```

### Verification and Repair

```python
class VerificationEngine:
    def verify(self, ctx: "DispatchContext") -> "VerificationResult": ...


class RepairPlanner:
    def build_plan(self, ctx: "DispatchContext") -> "RepairPlan | None": ...


class RepairPlanValidator:
    def validate(self, plan: "RepairPlan") -> "ValidatedRepairPlan": ...


class RepairExecutor:
    def execute(self, ctx: "DispatchContext", plan: "ValidatedRepairPlan") -> "DispatchResult": ...
```

### Persistence

```python
class TargetRegistry:
    def list_targets(self) -> list["TargetProfile"]: ...
    def get(self, target_id: str) -> "TargetProfile": ...


class LocatorStore:
    def load(self, target_id: str, fingerprint: "WindowFingerprint") -> "LocatorBundle | None": ...
    def save(self, target_id: str, locator: "LocatorBundle") -> None: ...


class TemplateStore:
    def list_family(self, target_id: str, family: str) -> list["TemplateVariant"]: ...
    def save_match_winner(self, target_id: str, winner: "TemplateMatch") -> None: ...
```

## 9. Data Contracts

Use Pydantic models in `core/models.py`.

```python
class TargetProfile(BaseModel):
    id: str
    display_name: str
    process_hints: list[str] = []
    title_regex: str | None = None
    class_hints: list[str] = []
    preferred_adapters: list[Literal["cdp", "uia", "keyboard", "visual"]]
    regions: dict[str, "SearchRegion"]
    submit_policy: list[str]
    verification_policy: list[str]
    cdp: "CdpProfile | None" = None
    uia: "UiaProfile | None" = None


class DispatchRequest(BaseModel):
    target_id: str
    command_text: str
    correlation_id: str | None = None
    preferred_adapter: str | None = None
    allow_repair: bool = True
    wait_for_completion: bool = False
    initiated_by: Literal["cli", "hotkey", "joc", "tray"] = "cli"


class DispatchAccepted(BaseModel):
    execution_id: str
    state: Literal["queued", "running"]


class DispatchResult(BaseModel):
    execution_id: str
    target_id: str
    state: Literal["success", "repaired", "failed", "timeout"]
    adapter_used: str | None = None
    verification: "VerificationResult"
    timings_ms: dict[str, int]
    artifacts: "ExecutionArtifacts"
    repair_applied: bool = False
    error: str | None = None


class ResolvedWindow(BaseModel):
    hwnd: int
    title: str
    process_name: str
    pid: int
    class_name: str
    is_minimized: bool
    is_visible: bool
    bounds: "Rect"


class WindowFingerprint(BaseModel):
    target_id: str
    process_name: str
    class_name: str
    dpi_scale: int
    title_hash: str
    uia_signature_hash: str | None = None


class LocatorBundle(BaseModel):
    fingerprint: WindowFingerprint
    dom: "DomLocatorSet | None" = None
    uia: "UiaLocatorSet | None" = None
    visual: "VisualLocatorSet | None" = None
    winning_submit_method: str | None = None
    updated_at: datetime
```

Repair plan contract:

```python
class RepairStep(BaseModel):
    op: Literal[
        "find_visual",
        "find_input_region",
        "focus_input",
        "type_text",
        "press_key",
        "click_match",
        "verify",
    ]
    template_family: str | None = None
    method: str | None = None
    key: str | None = None
    value: str | None = None
    expect: str | None = None


class RepairPlan(BaseModel):
    target: str
    strategy: Literal["visual_then_keyboard", "uia_then_keyboard", "cdp_then_visual"]
    steps: list[RepairStep]
    persist: dict[str, str] = {}
```

Validation rules:

- reject any op outside the allow-list
- reject filesystem, shell, script, eval, JS, or arbitrary code fields
- reject more than 8 steps
- reject cross-window coordinates
- require `verify` as final step

## 10. Adapter Specifications

### `CdpAdapter`

Use only for Chromium targets with an explicit remote-debug launch profile.

```python
class CdpAdapter:
    name = "cdp"

    def probe(self, ctx: DispatchContext) -> AdapterProbe: ...
    def attach(self, profile: CdpProfile) -> CdpSession: ...
    def locate_input(self, ctx: DispatchContext) -> LocateResult: ...
    def set_text(self, ctx: DispatchContext, located: LocateResult) -> ActionResult: ...
    def submit(self, ctx: DispatchContext, located: LocateResult) -> ActionResult: ...
```

Rules:

- require non-default `user-data-dir`
- never auto-launch against operator default Chrome profile
- attach only after the target window is already resolved
- map intent to DOM actions, not raw stored JS blobs

### `UiaAdapter`

```python
class UiaAdapter:
    name = "uia"

    def inspect(self, window: ResolvedWindow) -> UiaTreeSnapshot: ...
    def find_editable_candidates(self, snapshot: UiaTreeSnapshot) -> list[UiaElement]: ...
    def find_submit_candidates(self, snapshot: UiaTreeSnapshot) -> list[UiaElement]: ...
```

Rules:

- search under the target window subtree only
- prefer value-like and invoke-like patterns
- if value pattern is absent, switch to focus + keyboard instead of faking success

### `KeyboardAdapter`

```python
class KeyboardAdapter:
    name = "keyboard"

    def focus_input(self, ctx: DispatchContext, located: LocateResult) -> ActionResult: ...
    def type_text(self, text: str) -> ActionResult: ...
    def press_submit(self, submit_policy: list[str]) -> ActionResult: ...
```

Rules:

- fail fast if integrity mismatch blocks `SendInput`
- type into already-focused target only
- never run if the window cannot be foregrounded deterministically

### `VisualAdapter`

```python
class VisualAdapter:
    name = "visual"

    def capture_region(self, window: ResolvedWindow, region: SearchRegion) -> WindowImage: ...
    def match_family(self, image: WindowImage, family: str) -> list[TemplateMatch]: ...
    def click_match(self, match: TemplateMatch) -> ActionResult: ...
```

Rules:

- capture the target window, then crop; never search the full desktop
- support DPI variants and dark/light variants
- require confidence threshold plus sanity check before clicking

## 11. Execution Policy

Default phase timeouts:

| Phase | Timeout |
|-------|---------|
| find window | 2000 ms |
| restore + activate | 2000 ms |
| locate input | 3000 ms |
| submit + verify | 5000 ms |
| repair pass | 8000 ms |

State machine:

```text
IDLE
  -> RESOLVE_TARGET
  -> FIND_WINDOW
  -> RESTORE_IF_MINIMIZED
  -> ACTIVATE_WINDOW
  -> WAIT_FOR_READY
  -> CHOOSE_ADAPTER
  -> LOCATE_INPUT
  -> SET_TEXT
  -> SUBMIT
  -> VERIFY
  -> SUCCESS | REPAIR | FAIL
```

Hard rules:

- no adapter may return success without verification
- visual fallback never searches outside resolved window bounds
- repair may run once per execution in MVP
- persist only validated locator/template improvements

## 12. Local API Contract

Expose the runtime on `http://127.0.0.1:5013` by default. Make the port configurable with `JARVIS_INJECTOR_PORT`.

### Health

```http
GET /health
```

```json
{
  "status": "ok",
  "service": "jarvis-injector",
  "version": "0.1.0",
  "queueDepth": 0,
  "adapters": {
    "cdp": true,
    "uia": true,
    "keyboard": true,
    "visual": true
  }
}
```

### Targets

```http
GET /api/targets
POST /api/targets/{targetId}/probe
```

### Dispatch

```http
POST /api/dispatch
POST /api/dispatch/batch
GET /api/executions/{executionId}
GET /api/executions?limit=25
```

Dispatch request:

```json
{
  "targetId": "chatgpt_edge_main",
  "commandText": "check mcp and proceed",
  "preferredAdapter": null,
  "allowRepair": true,
  "waitForCompletion": false,
  "initiatedBy": "joc"
}
```

Dispatch accepted:

```json
{
  "executionId": "inj_20260309_140501_a1b2c3",
  "state": "queued"
}
```

Execution result:

```json
{
  "executionId": "inj_20260309_140501_a1b2c3",
  "targetId": "chatgpt_edge_main",
  "state": "success",
  "adapterUsed": "keyboard",
  "verification": {
    "passed": true,
    "signals": ["composer_cleared", "new_message_visible"]
  },
  "timingsMs": {
    "findWindow": 181,
    "activate": 420,
    "locateInput": 944,
    "submitVerify": 1810
  },
  "repairApplied": false
}
```

## 13. JOC Client Contract

Add `packages/joc/src/types/windowInjector.ts`:

```ts
export interface InjectorHealth {
  status: string;
  service: string;
  version: string;
  queueDepth: number;
  adapters: Record<string, boolean>;
}

export interface InjectorTarget {
  id: string;
  displayName: string;
  preferredAdapters: string[];
  lastSeenWindow?: {
    title: string;
    processName: string;
    hwnd: number;
  };
}

export interface InjectorDispatchRequest {
  targetId: string;
  commandText: string;
  preferredAdapter?: string | null;
  allowRepair?: boolean;
  waitForCompletion?: boolean;
  initiatedBy: "joc";
}

export interface InjectorDispatchAccepted {
  executionId: string;
  state: "queued" | "running";
}
```

Add `packages/joc/src/services/windowInjectorClient.ts`:

```ts
export async function checkInjectorHealth(): Promise<InjectorHealth> {}
export async function listInjectorTargets(): Promise<InjectorTarget[]> {}
export async function dispatchInjectorCommand(
  request: InjectorDispatchRequest
): Promise<InjectorDispatchAccepted> {}
export async function getInjectorExecution(executionId: string): Promise<InjectorExecution> {}
export async function probeInjectorTarget(targetId: string): Promise<InjectorProbeResult> {}
```

JOC UI scope:

- extend `DispatchPage.tsx` to add a `Window Targets` lane
- show adapter chosen, verification state, screenshots on failure
- keep BAS targets and window-injector targets visually distinct

## 14. Launcher Plan

Add `scripts/launchers/START_WINDOW_INJECTOR.ps1`:

- ensure Python environment is available
- install package extras if missing
- start Flask server on `:5013`
- start tray app if `-WithTray`
- verify `/health`

Phase 2 change to `scripts/launchers/LAUNCH_JARVIS.ps1`:

- add `-WithInjector`
- keep BAS optional and independent
- do not auto-start BAS when only window injection is needed

## 15. Dependency Plan

Python dependencies for `packages/jarvis_injector/pyproject.toml`:

- `flask`
- `pydantic`
- `playwright`
- `pywin32`
- `comtypes`
- `opencv-python`
- `numpy`
- `pillow`
- `pystray`

Optional later:

- `rapidfuzz` for fuzzy title matching
- `pytesseract` or Windows OCR bridge for text anchors

## 16. Reuse vs Isolation

There is already Windows-native actuator and injector code in `IDE/src-tauri/src/actuator/` and `IDE/src-tauri/src/injection/`.

Decision:

- treat that Rust code as reference material, not as a hard dependency for MVP
- keep the new runtime standalone in Python so JOC can call it directly over localhost
- if the Python MVP hits latency or reliability limits, add a phase-2 bridge to reuse Rust input/UIA primitives behind a stable Python interface

This avoids coupling the new runtime to the IDE/Tauri lane.

## 17. Ticket Breakdown

### P0 - Runtime Skeleton

1. `WININJ-001` Create `packages/jarvis_injector/` with Python package layout, config loader, and local Flask service.
2. `WININJ-002` Add `GET /health`, `GET /api/targets`, and execution log writer.
3. `WININJ-003` Add `scripts/launchers/START_WINDOW_INJECTOR.ps1`.

### P0 - Deterministic Window Control

4. `WININJ-010` Implement `Win32WindowController.find_window()` with title/class/process resolution and scoring.
5. `WININJ-011` Implement restore, foreground activation, and readiness polling.
6. `WININJ-012` Add unit-tested window fingerprint generation and region normalization.

### P1 - MVP Dispatch Path

7. `WININJ-020` Implement `KeyboardAdapter` with focus, type, submit, and integrity-level failure reporting.
8. `WININJ-021` Implement `DispatchStateMachine` with mandatory verification.
9. `WININJ-022` Add initial verification signals: composer cleared, message appeared, submit control state change.
10. `WININJ-023` Ship first target profile for `chatgpt_edge_main` using keyboard-first fallback and optional CDP attach metadata.

### P1 - JOC Cockpit Wiring

11. `WININJ-030` Add `windowInjectorClient.ts` and type definitions in JOC.
12. `WININJ-031` Extend `DispatchPage.tsx` with queue, status, and per-target execution result cards.
13. `WININJ-032` Add degraded-state messaging when injector runtime is offline.

### P1 - Structured Adapters

14. `WININJ-040` Implement `CdpAdapter` for Chromium attach with dedicated profile enforcement.
15. `WININJ-041` Implement `UiaAdapter` with editable-control discovery and submit candidates.
16. `WININJ-042` Add integration fixtures for Edge ChatGPT window, Cursor, and one UIA desktop app.

### P2 - Visual Fallback

17. `WININJ-050` Implement `VisualAdapter`, `TemplateMatcher`, and constrained-region template family matching.
18. `WININJ-051` Add template capture workflow and persisted winner storage.
19. `WININJ-052` Add failure screenshots and region overlays to execution artifacts.

### P2 - Repair Layer

20. `WININJ-060` Implement `RepairPlan`, `RepairPlanValidator`, and bounded repair executor.
21. `WININJ-061` Add provider-agnostic `RepairPlanner` interface with JSON-only output contract.
22. `WININJ-062` Persist validated locator/template improvements after successful repair.

## 18. Test Plan

### Unit

- target resolution scoring
- window fingerprint generation
- adapter selection ordering
- repair plan validation
- region clamp math

### Integration

- restore minimized target, type fixed phrase, verify success
- CDP attach to dedicated Edge/Chrome profile
- UIA locate + invoke on a desktop test surface
- visual match inside bounded region only
- repair path turns failed verification into persisted locator improvement

### Proof Artifacts

- execution JSONL record
- failure screenshot
- chosen adapter and confidence
- verification signals emitted

## 19. Acceptance Gates

The build is acceptable when:

1. Global hotkey can enqueue a dispatch.
2. CLI can dispatch `check mcp and proceed` to at least three configured targets.
3. Runtime restores and activates the correct window automatically.
4. At least two adapters succeed in real runs.
5. No run is marked successful without verification signals.
6. One broken locator can be recovered by visual or repair path and persisted.
7. JOC can display runtime health, queue depth, and per-execution result state.

## 20. Build Plan

### Phase A - 2 to 3 sessions

- package skeleton
- health/targets/dispatch API
- window controller
- keyboard adapter
- execution logging

### Phase B - 2 to 4 sessions

- JOC client wiring
- CDP adapter
- UIA adapter
- target registry and locator persistence

### Phase C - 2 to 3 sessions

- visual adapter
- template capture
- screenshot artifact pipeline

### Phase D - 2 sessions

- bounded repair planner
- replayable repair execution
- persistence of improved locators/templates

## 21. Immediate Next Step

Implement Phase A only:

- scaffold `packages/jarvis_injector/`
- ship `Win32WindowController`
- ship `KeyboardAdapter`
- add `/health`, `/targets`, `/dispatch`
- wire a minimal JOC client card for runtime health and manual dispatch

That yields the first operator-usable loop without reopening the blocked BAS ChatGPT path.
