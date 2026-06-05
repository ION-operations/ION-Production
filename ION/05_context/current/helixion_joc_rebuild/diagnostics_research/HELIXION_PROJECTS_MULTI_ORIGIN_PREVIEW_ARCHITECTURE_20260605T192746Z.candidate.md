# Helixion Projects Multi-Origin Preview Architecture

Status: candidate research packet
Created: 2026-06-05T19:27:46Z
Scope: Helixion website app, Projects system, app preview, local/VM/remote/viewer-local preview topology
Authority: no production, no live execution, no accepted-state, no secrets, no service restart, no push

## Objective

Design the next Projects/App Preview model so Helixion can support:

- local-machine app launch and diagnostics;
- VM or remote runner app launch;
- public or remote near-real-time same-origin preview;
- viewer-local preview on the machine opening the website;
- AI-observable comparison between two or more preview surfaces;
- interactive control where allowed, without collapsing preview visibility into unsafe execution authority.

## Current ION State

Current working pieces:

- `ION/08_ui/joc_cockpit_shell/HelixionAppsPreviewPanel.tsx` provides app launch, stop, diagnostics, matrix, screenshots, and launch timeline UI.
- `ION/08_ui/joc_cockpit_shell/VNextMissionControlPanel.tsx` includes project mission-control launch/stop/diagnostics affordances.
- `ION/08_ui/joc_cockpit_shell/BuildWorkbenchPage.tsx` already has an isolated sandbox preview model for builder work.
- `ION/04_packages/kernel/ion_project_launcher.py` starts authorized local app roots on loopback ports, writes launch receipts, serves an instrumented wrapper, proxies launched apps, injects diagnostics, and captures screenshots.
- `ION/04_packages/kernel/ion_project_workbench.py` projects registered workbench status, preview status, browser captures, patch receipts, rollback candidates, and bounded project actions.
- `ION/04_packages/kernel/ion_local_cockpit_app.py` exposes `/projects`, `/cockpit/projects/model.json`, launch start/stop/status/diagnostics, proxy, screenshots, and Application Dev catalog bridge routes.
- `ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py` exposes the remote/browser-facing cockpit/project HTTP surface with auth and same-origin mutation checks.
- `ION/04_packages/kernel/ion_helixion_project_access_inventory.py` renders the public Projects canon and family detail model with redacted local refs and embedded workbench preview capability.
- `ION/03_registry/ion_chatgpt_browser_mcp_tool_policy.yaml` already lists Project Workbench tools and marks public preview allowed while requiring cockpit auth for mutation.
- `browser_extension/ion_chatops_bridge` and Browser GPT DOM calibration surfaces provide the current AI/browser-observation substrate.

Observed runtime snapshot:

- `project_cockpit.status`: `project_cockpit_ready`
- portfolio manifest mode: `cached_manifest`
- portfolio project roots: `199`
- portfolio families: `45`
- launchable projects in explorer report: `117`
- current launcher running count: `0`
- Cosmos preview probe: `not_running` at `http://127.0.0.1:5173/`
- ION development preview probe: `ready` at `http://127.0.0.1:8765/`

## Core Finding

ION already has most of the pieces, but they are not yet unified by a first-class preview session contract.

Today, preview is split across:

- local Project Launcher records;
- hardcoded Project Workbench project specs;
- public Projects family preview capability;
- Application Dev launcher/catalog bridge;
- Build Workbench sandbox iframe;
- Browser GPT DOM and screenshot capture lanes.

The next model should not add one more ad hoc route. It should introduce a shared `PreviewSession` contract consumed by `#apps`, `#projects`, `#build`, public `/projects`, Browser GPT/Action surfaces, and future VM runners.

## Recommended Product Model

### Preview Object Types

`PreviewProvider`

The adapter that knows how to start, expose, observe, and stop one class of preview.

Recommended provider IDs:

- `local_loopback_launcher`
- `local_static_file_server`
- `application_dev_launcher`
- `cockpit_internal_surface`
- `vm_runner`
- `remote_runner`
- `viewer_local_runner`
- `static_hosted_artifact`

`PreviewSession`

The durable runtime object representing one live or historical preview.

Required fields:

- `preview_id`
- `project_id`
- `version_id`
- `provider_id`
- `runner_id`
- `runner_location`: `local_host`, `vm`, `remote_host`, `viewer_local`, `static_host`
- `source_root_ref`
- `public_url`
- `same_origin_embed_url`
- `control_url`
- `status_url`
- `diagnostics_url`
- `screenshot_url`
- `ws_hmr_url` or `hmr_proxy`
- `auth_mode`
- `viewer_scope`
- `lifecycle_state`
- `created_at`
- `expires_at`
- `stop_token_ref`
- `receipt_refs`
- `authority`

`PreviewComparison`

The model for seeing two or more previews together.

Required fields:

- `comparison_id`
- `baseline_preview_id`
- `candidate_preview_id`
- `route`
- `viewport`
- `capture_pair_receipt_refs`
- `screenshot_refs`
- `console_delta`
- `network_delta`
- `dom_delta_ref`
- `accessibility_delta_ref`
- `visual_diff_ref`
- `verdict`: `not_compared`, `same_enough`, `changed_expected`, `changed_unexpected`, `blocked`

### Capability Classes

Do not expose a generic `launch_app` permission.

Use separate capabilities:

1. `preview_read`
   - Read session state, health, screenshots, logs, public preview URLs, and model JSON.
   - No process start.

2. `managed_local_preview_launch`
   - Start/stop authorized local apps under `ion_project_launcher.py`.
   - Requires `ION_PROJECT_LOCAL_LAUNCH_CONFIRMED`.
   - Loopback-bound by default.

3. `managed_vm_preview_launch`
   - Future runner adapter.
   - Requires VM identity, workspace/state-root binding, approved source materialization, network policy, and receipts.

4. `viewer_local_preview_launch`
   - Future browser/helper adapter.
   - Lets the machine viewing Helixion launch its own clone/worktree preview.
   - Requires local helper install, project identity proof, path confirmation, and local-only receipt.

5. `preview_interaction`
   - Reload, route navigation, viewport change, screenshot capture, diagnostics snapshot.
   - Should be allowed before mutation but still receipt-bearing.

6. `preview_mutation`
   - Patch/apply/build/start/stop/dependency repair.
   - Requires same-origin cockpit auth, confirmation tokens, idempotency, edit leases where applicable, and receipts.

7. `ai_observe_preview`
   - Browser/Playwright/extension/visual-agent capture, DOM snapshot, AX snapshot, screenshot and console/network intake.
   - No silent submit, no third-party account action, no accepted-state claim.

## Topology Options

### A. Local Host Preview

Current closest implementation.

Flow:

```text
Helixion cockpit
-> /cockpit/projects/launch/start
-> ion_project_launcher.py
-> app on 127.0.0.1:<port>
-> /cockpit/projects/launch/open/<launch_id>
-> /cockpit/projects/launch/proxy/<launch_id>/...
-> diagnostics + screenshot receipts
```

Use this for:

- operator workstation work;
- local app debugging;
- fast screenshots/diagnostics;
- source edits under Project Workbench.

Needed hardening:

- durable launch reconciliation after cockpit restart;
- HMR/WebSocket proxy support;
- auth parity review for public POST proxy paths;
- first-class preview-session records.

### B. Remote Same-Origin Preview

Flow:

```text
Remote browser
-> https://ion.helixion.net/cockpit#apps
-> same-origin /projects/<project>/preview/session/<preview_id>/...
-> local or VM runner via allowlisted proxy
```

Use this for:

- viewing a preview from another machine;
- near-real-time operator review;
- Browser GPT or external reviewer visibility.

Rule:

The remote browser should not fetch `127.0.0.1` app URLs directly. Remote preview should stay same-origin through the cockpit/preview service.

### C. VM Runner Preview

Flow:

```text
Helixion cockpit
-> PreviewProvider(vm_runner)
-> VM-local runner daemon
-> materialize approved source/worktree
-> start app inside VM
-> expose same-origin proxy/embed URL
-> return logs/screenshots/diagnostics/stop receipt
```

Use this for:

- stronger isolation;
- testing from a reproducible environment;
- cloud/remote app previews.

Needs:

- `runner_id` and VM identity;
- workspace/state-root binding;
- artifact or git ref materialization policy;
- dependency install policy;
- port/firewall/NAT policy;
- lifecycle receipts;
- teardown proof;
- no secret mount by default.

### D. Viewer-Local Preview

Flow:

```text
Remote user opens Helixion
-> user has local ION helper/browser extension
-> page offers "Run on this device"
-> helper proves project/ref and local path
-> viewer machine launches its own preview
-> viewer-local receipt syncs back as candidate evidence
```

Use this for:

- client/customer running their own local preview;
- comparing "operator machine" versus "viewer machine";
- offline/local-first demos.

Rule:

The website cannot silently start a viewer machine process. Viewer-local launch requires a local helper, explicit operator action, and local receipts.

### E. Static Hosted Artifact Preview

Flow:

```text
build artifact
-> safe static bundle
-> content-addressed preview
-> public/static iframe
-> no process lifecycle
```

Use this for:

- read-only demos;
- release candidates;
- stable public project pages.

This should be separate from dev-server launch because stop/restart/dependency repair semantics do not apply.

## Dual/Triple Preview Pattern

The target product shape should support a matrix:

```text
source A: operator-local preview
source B: VM preview
source C: viewer-local preview
source D: static artifact preview
```

For each preview, the cockpit can show:

- live iframe or screenshot fallback;
- health;
- route;
- viewport;
- console/network summary;
- latest DOM/AX snapshot if available;
- last receipt;
- allowed controls.

For comparison:

- synchronize route and viewport;
- capture both previews;
- compute screenshot/console/network/DOM deltas;
- let Visual Agent or Browser DOM Cartographer inspect differences;
- route the finding into a `PreviewComparison` receipt.

## AI Observation Model

Current AI-observation substrate:

- Project Workbench can capture Playwright screenshots and console/bad-response receipts.
- Browser GPT DOM twin observes ChatGPT/browser surfaces.
- Browser extension can capture visible tab screenshots and DOM diagnostics.
- Browser perception protocols define DOM, accessibility, visual geometry, mutation timeline, and page state cartography.
- Build Workbench already uses isolated iframe preview patterns.

Recommended next layer:

- Add `ion_project_preview_capture_pair`.
- Add project preview DOM/AX snapshot capture, not only screenshots.
- Wire preview captures into Agent Observatory.
- Add a visual-agent "compare two previews" read-only route.
- Keep all AI interaction as observe/plan/preview by default; clicks/navigation/form actions require explicit preview-interaction authority.

## Route Design

Read routes:

```text
GET /cockpit/previews/model.json
GET /cockpit/previews/session/<preview_id>.json
GET /cockpit/previews/session/<preview_id>/events
GET /cockpit/previews/session/<preview_id>/screenshot/<name>
GET /cockpit/previews/comparison/<comparison_id>.json
```

Same-origin preview routes:

```text
GET /projects/<project_id>/preview/session/<preview_id>/
GET /projects/<project_id>/preview/session/<preview_id>/<path>
```

Mutation/control routes:

```text
POST /cockpit/previews/session/start
POST /cockpit/previews/session/stop
POST /cockpit/previews/session/capture
POST /cockpit/previews/session/diagnostics/snapshot
POST /cockpit/previews/comparison/create
POST /cockpit/previews/comparison/capture
```

Auth and authority:

- read routes may be public only when the session explicitly says `public_preview_allowed: true`;
- all mutation/control routes require cockpit auth, same-origin mutation check, confirmation when state-bearing, idempotency for repeatable actions, and receipts;
- Action Gateway should call registered branch routes only, not raw preview URLs.

## Implementation Slices

### Slice 1: Preview Session Projection

Add a read-only kernel module:

```text
ION/04_packages/kernel/ion_project_preview_sessions.py
```

Responsibilities:

- project current launcher records into `PreviewSession`;
- include static/cockpit/internal providers;
- no process control;
- tests for local, static, and missing cases.

UI:

- add `/cockpit/previews/model.json`;
- add `#apps` fast model route;
- update `HelixionAppsPreviewPanel` to consume preview-session rows.

### Slice 2: Durable Launch Reconciliation

Extend `ion_project_launcher.py`:

- persist active launch registry;
- rehydrate status after cockpit restart;
- reconcile dead PIDs/ports;
- keep stop-token and log refs without reviving unsafe state.

### Slice 3: Same-Origin Preview Proxy Hardening

Review and patch:

- public POST proxy auth parity;
- HMR WebSocket support;
- origin/referrer policy;
- route allowlist by `preview_id`;
- CSP is widened only per explicit provider allowlist.

### Slice 4: Comparison Receipts

Add:

- `ion_project_preview_compare.py`;
- capture-pair receipt;
- screenshot pair refs;
- console/network delta;
- optional DOM/AX snapshot placeholders.

### Slice 5: VM Runner Protocol

Add architecture/protocol first:

- runner identity;
- workspace/state-root binding;
- materialization policy;
- dependency install policy;
- allowed egress;
- lifecycle receipts;
- teardown receipts.

Implementation waits until the protocol is green.

### Slice 6: Viewer-Local Helper

Define separately from server preview:

- browser extension or local helper handshake;
- no silent local process start;
- explicit local path/project ref confirmation;
- viewer-local receipt sync.

## Hard Boundaries

- Do not expose arbitrary loopback proxying.
- Do not make public pages fetch local `127.0.0.1` app servers directly.
- Do not put bearer tokens or cockpit permission tokens in frontend JS or URLs.
- Do not treat tunnel availability as production authority.
- Do not start VM/remote processes through the existing local launcher path.
- Do not broaden iframe/CSP globally.
- Do not let screenshots, DOM captures, or AI visual claims become accepted state without normal proof/settlement.

## Immediate Recommendation

Start with Slice 1 and Slice 3:

1. Create a read-only `PreviewSession` projection from current launcher/project/workbench state.
2. Add `/cockpit/previews/model.json` and `#apps` fast model hydration.
3. Audit and harden same-origin proxy auth parity before expanding remote preview behavior.

This gives the Helixion app a clean model for the future local/VM/viewer-local system without prematurely building VM execution or exposing unsafe remote control.

## Specialist Inputs

Five read-only GPT-5.5 xhigh specialist reports informed this packet:

- UI/projects/app preview surfaces;
- project launcher/app registry/runtime;
- remote/tunnel/gateway transport;
- Browser GPT/AI observability;
- architecture/security/governance.

All specialists reported no edits, no staging, no deletion, no push, and no service restarts.
