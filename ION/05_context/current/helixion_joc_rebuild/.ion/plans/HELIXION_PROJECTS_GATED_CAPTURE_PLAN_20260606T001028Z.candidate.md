# Helixion Projects Gated Capture Plan

Status: candidate draft only
Generated: 2026-06-06T00:10:28Z
Domain: helixion_projects_app_preview

## Purpose

Define the future approval path for screenshot, DOM, console, and network
observation against PreviewSession targets. This packet does not execute
capture, add a route, start a browser, probe loopback, mutate previews, or claim
accepted state.

## Authority

- Production authority: false
- Live execution authority: false
- Accepted-state authority: false
- Secrets authority: false
- Browser automation authority: false
- Capture authority: false
- Loopback probe authority: false
- Loopback mutation authority: false

## Target Source

Capture eligibility must start from:

- `preview_sessions.ai_observe_preview.targets`
- `preview_sessions.comparisons[].baseline_surface`
- `preview_sessions.comparisons[].candidate_surface`

Eligible routes must be same-origin relative paths already scrubbed by
`ion_project_preview_sessions._same_origin_path`.

Blocked targets remain blocked when:

- runtime state is `detached`, `stale`, or `orphaned`
- route is empty, protocol-relative, external, tokenized, or direct loopback
- target requires secrets, cookies, local file access, or raw process identity
- target would require service restart, deployment, VM launch, remote launch, or
  viewer-local helper mutation

## Proposed Gates

1. Preview gate: build a capture preview object from existing metadata only.
   The preview includes target id, route, route basis, planned capture lanes,
   redaction policy, artifact lane, and authority flags.

2. Operator approval gate: require an explicit future confirmation token before
   any browser/capture execution. Draft token:
   `ION_PROJECT_PREVIEW_CAPTURE_CONFIRMED`.

3. Execution gate: only after approval, run a bounded capture worker against the
   same-origin route. No direct local loopback URL, raw app token, cookie, or
   local filesystem path may be used as target input.

4. Redaction gate: redact or omit cookies, authorization headers, query tokens,
   storage values, request bodies, response bodies, local paths, and secret-like
   strings before writing artifacts.

5. Receipt gate: write a run receipt with target id, route basis, redaction
   result, artifacts written, non-claims, and validation outcome. No artifact is
   accepted state by itself.

## Candidate Artifact Lanes

- `ION/05_context/current/project_launcher/app_diagnostics/capture_previews/`
- `ION/05_context/current/project_launcher/app_diagnostics/capture_runs/`
- `ION/05_context/current/project_launcher/app_diagnostics/snapshots/`
- `ION/05_context/current/project_launcher/app_diagnostics/receipts/`

## Capture Lanes

Allowed only after approval:

- screenshot bitmap and viewport metadata
- DOM outline with text redaction and no full HTML dump
- console error/warning summary with value redaction
- network request summary with URL scrubbing and no headers/bodies
- accessibility tree summary with text redaction

Forbidden:

- raw cookies, local storage, session storage, auth headers, request bodies,
  response bodies, secret-shaped values, direct loopback URLs, raw stop tokens,
  raw local paths, deployment mutation, service restart, app patching, and
  accepted-state claims

## Model Extension Shape

Future preview object:

```json
{
  "schema_id": "ion.project_preview_capture_plan_preview.v0_1",
  "status": "preview_only_not_executed",
  "target_id": "observe:comparison:example",
  "route": "/cockpit/projects/launch/proxy/example/",
  "route_basis": "comparison.route",
  "capture_lanes": ["screenshot", "dom_outline", "console_summary", "network_summary", "accessibility_summary"],
  "authority": {
    "capture_authority": false,
    "browser_automation_authority": false,
    "preview_mutation": false,
    "accepted_state_authority": false,
    "production_authority": false,
    "live_execution_authority": false,
    "secrets_authority": false
  }
}
```

## Validation Required Before Future Execution

- Tests prove tokenized, protocol-relative, external, and direct loopback routes
  are rejected.
- Tests prove detached, stale, and orphaned targets are blocked.
- Tests prove capture preview emits no cookies, auth headers, query tokens, raw
  local paths, direct loopback URLs, stop tokens, or accepted-state verdicts.
- UI displays capture preview as a gated plan, not an action, unless approval is
  present.

## Non-Claims

- No screenshot, DOM, console, network, accessibility, or visual capture occurred.
- No browser automation occurred.
- No route handler, service, tunnel, or live runner changed.
- No production, live execution, secrets, or accepted-state authority is granted.
