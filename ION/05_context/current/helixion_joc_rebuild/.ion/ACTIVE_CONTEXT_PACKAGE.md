# Helixion PreviewSession Slice 1 Context

Status: active candidate folder-local package
Created: 2026-06-05T19:38:21Z

## Objective

Implement the first bounded slice from the Helixion Projects multi-origin preview architecture: a read-only `PreviewSession` projection that gives the cockpit one model for local, workbench, Application Dev, static/catalog, future VM, and future viewer-local preview surfaces.

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

Create a kernel projection, expose a local cockpit JSON route, and hydrate the cockpit Projects/App Preview surfaces from that read-only projection. Existing local launch mutations keep their current confirmation gates.

## Next Safe Step

Add `ion_project_preview_sessions.py`, route `/cockpit/previews/model.json`, focused tests, and minimal UI hydration that shows provider/session state without starting any app or VM.
