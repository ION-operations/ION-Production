# Helixion Projects App Preview Context

Status: active candidate folder-local package
Created: 2026-06-05T20:53:57Z
Updated: 2026-06-06T01:09:29Z

## Objective

Continue the Helixion Projects multi-origin preview architecture from the folder-local context lane.

Committed candidate slices now cover:

- PreviewSession projection over project, portfolio, launcher, local, same-origin, VM, remote, viewer-local, and static provider classes.
- Durable local launcher state reconciliation and protected public app-preview POST proxy/event routing.
- Runtime ownership classification for attached, detached, stale, and orphaned preview records.
- Read-only preview comparison registration and Project Cockpit summary counts.
- Local and protected public route-surface tests proving `comparisons` and `surface_matrix` survive `/cockpit/previews/model.json`.
- Metadata-only AI observe-preview substrate with capture, browser automation, loopback mutation, live execution, secrets, and accepted-state authority all false.
- No-CSS Preview Pairing Map in the Helixion app preview detail panel.
- Sanitized comparison peer surfaces for baseline/candidate labels, providers, runner locations, and safe same-origin routes.
- Read-only observe target and blocked-target detail rows in the app preview detail panel.
- Draft-only gated capture plan for future screenshot, DOM, console, network, and accessibility observation.
- Metadata-only app-cast preview projection for future multi-user app-only host/viewer sharing, derived from sanitized observe targets with no stream, capture, desktop share, viewer control, live, production, accepted-state, or secrets authority.
- Read-only app-cast share-grant contract projection for host/viewer membership requirements, public-vs-object-grant viewer rules, expiry/revocation/audit placeholders, route-auth evidence, and passive UI wording.

## Authority

- No production deployment.
- No live execution authority.
- No accepted-state claim.
- No secrets access.
- No service restart.
- No push.

## Source Packet

- `ION/05_context/current/helixion_joc_rebuild/diagnostics_research/HELIXION_PROJECTS_MULTI_ORIGIN_PREVIEW_ARCHITECTURE_20260605T192746Z.candidate.md`
- `ION/05_context/current/helixion_joc_rebuild/diagnostics_research/HELIXION_PROJECTS_MULTI_ORIGIN_PREVIEW_ARCHITECTURE_20260605T192746Z.candidate.json`

## Slice Scope

Current active source/test/UI scope:

- `ION/04_packages/kernel/ion_project_preview_sessions.py`
- `ION/04_packages/kernel/ion_project_launcher.py`
- `ION/04_packages/kernel/ion_project_cockpit.py`
- `ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py`
- `ION/04_packages/kernel/ion_local_cockpit_app.py`
- `ION/08_ui/joc_cockpit_shell/HelixionAppsPreviewPanel.tsx`
- `ION/08_ui/joc_cockpit_shell/ionRuntimeCockpitTypes.ts`
- `ION/tests/test_kernel_ion_project_preview_sessions.py`
- `ION/tests/test_kernel_ion_project_launcher.py`
- `ION/tests/test_kernel_ion_local_cockpit_app.py`
- `ION/tests/test_kernel_ion_chatgpt_browser_mcp_http_preview.py`
- `ION/tests/test_kernel_ion_cockpit_view_model.py`

Current receipts:

- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_PREVIEW_SESSION_SLICE1_20260605T195601Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_LAUNCH_RECONCILIATION_SLICE2_20260605T205438Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_RUNTIME_IDENTITY_SLICE3_20260605T212912Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_PREVIEW_COMPARISON_SLICE4_20260605T231416Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_PREVIEW_SUMMARY_SLICE5_20260605T231649Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_PREVIEW_ROUTE_SURFACE_SLICE6_20260605T232114Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_AI_OBSERVE_SUBSTRATE_SLICE7_20260605T232851Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_PREVIEW_PAIRING_MAP_SLICE8_20260605T233010Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_PREVIEW_PEER_SURFACES_SLICE10_20260606T000738Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_OBSERVE_DETAIL_UI_SLICE11_20260606T000923Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_GATED_CAPTURE_PLAN_SLICE13_20260606T001028Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_APP_CAST_PREVIEW_SLICE15_20260606T002520Z.receipt.json`
- `ION/05_context/current/helixion_joc_rebuild/.ion/receipts/HELIXION_PROJECTS_APP_CAST_SHARE_GRANT_CONTRACT_SLICE17_20260606T010857Z.receipt.json`

## Next Safe Step

Next bounded slice:

- Add protected route / real-model tests for `/cockpit/previews/model.json` and `/cockpit/projects/previews/model.json`, then reconcile app-cast route-auth evidence with the parallel collaboration route registry once that lane is committed. This may verify bearer auth, query-token rejection, app-cast share-grant fields in the served model, and route-registry vocabulary alignment, but it must not open WebRTC, websocket, media, screenshot, browser automation, loopback, viewer-control, or mutation channels.

Do not start live VM, remote, viewer-local, app-cast stream, browser automation, screenshot, or loopback probe work without a new explicit gated packet.
