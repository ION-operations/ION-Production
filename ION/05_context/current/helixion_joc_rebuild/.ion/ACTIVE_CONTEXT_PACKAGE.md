# Helixion Project Launcher Slice 2 Context

Status: active candidate folder-local package
Created: 2026-06-05T20:53:57Z

## Objective

Implement the second bounded slice from the Helixion Projects multi-origin preview architecture: durable local launcher reconciliation that survives cockpit process restarts without claiming process ownership, plus public same-origin protection for app-preview POST proxy/event routes.

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

Persist managed launcher state under `ION/05_context/current/project_launcher/state/launches`, recover prior active launches as detached records, expose honest control fields in launcher status, and keep raw stop tokens out of status/receipt `open_href` payloads. Add focused tests for empty reconciliation, launch persistence, detached restart recovery, and protected public POST proxy behavior.

## Next Safe Step

Validate the launcher/public proxy slice, write a folder-local receipt, and commit only the bounded source/test/context changes.
