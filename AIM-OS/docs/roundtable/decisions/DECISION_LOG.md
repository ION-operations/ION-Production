# Roundtable Decision Log

**Purpose:** Record decisions made during roundtable discussions (no MCP).  
**Format:** See `../templates/DECISION_ENTRY.md`

---

## Decisions

## DEC-001 | Code freeze and communications-only mode | 2026-03-04

- **Decision ID:** DEC-001
- **Owner:** Braden (COMMAND)
- **Chosen option:** Immediate stand-down from source-code mutations; communications/documentation only.
- **Rationale:** Active identity confusion and runtime instability created unacceptable risk of cross-agent overwrite and further degradation.
- **Impacted surfaces:** All source/runtime mutation lanes; roundtable and docs lanes remain active.
- **Validation proof:** Roundtable thread entry `offline_msg_20260304_180542_Claude_Opus_4.6` in `docs/communications_mcp_down/threads/THREAD_aimos_roundtable_operational_convergence_2026-03-04.md`.
- **Rollback condition:** Explicit reauthorization from Braden (COMMAND) after team alignment.
- **Thread:** `aimos_roundtable_operational_convergence_2026-03-04`

## DEC-002 | Roundtable is canonical fallback coordination path | 2026-03-04

- **Decision ID:** DEC-002
- **Owner:** Braden (COMMAND)
- **Chosen option:** Use roundtable protocol and script-posted thread messages as the required coordination path.
- **Rationale:** MCP instability requires deterministic, shared, file-based communication to prevent silent divergence.
- **Impacted surfaces:** `docs/roundtable/*`, `docs/communications_mcp_down/threads/*`, `scripts/offline_comms/post_roundtable_message.py`.
- **Validation proof:** User bootstrap directive posted in current session; roundtable check-ins logged in active thread.
- **Rollback condition:** Stable MCP restored and explicit policy update from Braden (COMMAND).
- **Thread:** `aimos_roundtable_operational_convergence_2026-03-04`

## DEC-003 | Incident Damage Report Published | 2026-03-04

- **Decision ID:** DEC-003
- **Owner:** Codex Agent (documentation owner)
- **Chosen option:** Publish evidence-first incident damage report before any further runtime mutation.
- **Rationale:** Team confidence and coordination require one canonical snapshot of runtime state, file impact, and containment status.
- **Impacted surfaces:** `docs/roundtable/INCIDENT_DAMAGE_REPORT_2026-03-04.md`, roundtable thread communication.
- **Validation proof:** Incident report file created and referenced in roundtable check-in message.
- **Rollback condition:** If report contains factual errors, correct by append-only amendment and timestamped revision note.
- **Thread:** `aimos_roundtable_operational_convergence_2026-03-04`

## DEC-004 | Runtime Repair Window for :5001 Requires Explicit COMMAND Authorization | 2026-03-04

- **Decision ID:** DEC-004
- **Owner:** COMMAND/Agent Aether adjudication (execution candidate: Codex Agent)
- **Chosen option:** Proposed and held pending approval; no execution yet.
- **Rationale:** Current evidence shows `:5001` listener present but `/health` unstable; repair is risky under identity crisis unless explicitly authorized.
- **Impacted surfaces:** MCP fallback runtime process, lock protocol usage, recovery documentation.
- **Validation proof:** Health evidence captured in incident report.
- **Rollback condition:** If denied, remain in communications/documentation-only mode.
- **Thread:** `aimos_roundtable_operational_convergence_2026-03-04`

---

## DEC-005 | Deep Research Synthesis Packet Published with P0-P2 Ladder | 2026-03-05

- **Decision ID:** DEC-005
- **Owner:** Codex Agent (specialist execution lane)
- **Chosen option:** Publish consolidated deep research packet with current runtime evidence and prioritized execution ladder (P0-P2).
- **Rationale:** Team planning drift and document sprawl required one evidence-backed operational map that ties doctrine to immediate execution.
- **Impacted surfaces:** `docs/roundtable/CODEX1_DEEP_RESEARCH_SYNTHESIS_PACKET_2026-03-05.md`, roundtable coordination thread, MCP team messaging.
- **Validation proof:** Runtime checks completed (`:5001`, `:5002`, `:5011`), BAS API flow verified, BAS/JOC builds and BAS tests passed in this session.
- **Rollback condition:** Supersede by later packet with explicit adjudication entry and full diff of changed assumptions.
- **Thread:** `aimos_roundtable_operational_convergence_2026-03-04`

---

## DEC-006 | Composer Assigned as ChatGPT Sync and Zip Packaging Owner | 2026-03-05

- **Decision ID:** DEC-006
- **Owner:** Braden (COMMAND), acknowledged by team in roundtable/MCP
- **Chosen option:** Route ChatGPT-facing discussion packaging through Composer as primary owner.
- **Rationale:** Reduce context drift and remove manual routing burden from Braden by centralizing capsule curation and zip handoff.
- **Impacted surfaces:** `context/*`, `scripts/package_chatgpt_context.ps1`, roundtable/MCP coordination messages.
- **Validation proof:** Team thread acknowledgements posted (`Composer`, `Opus`, `Codex`) and packaging protocol file created at `context/README.md`.
- **Rollback condition:** Explicit command from Braden or COO to reassign packaging ownership.
- **Thread:** `aimos_roundtable_operational_convergence_2026-03-04`

---

## DEC-007 | Context Systems Federate-by-Lane Now, Consolidate by Promotion Gate Later | 2026-03-05

- **Decision ID:** DEC-007
- **Owner:** Codex (specialist execution lane), adjudication path: Opus
- **Chosen option:** Federate context systems by lane now; defer full consolidation until promotion criteria are met.
- **Rationale:** Evidence shows multiple viable context stacks with competing sources; forced immediate merge would increase regression risk and create false canon certainty.
- **Impacted surfaces:** `IDE/src-tauri/src/context_mapper/*`, `context_capsule_wire_and_mapper_v1/*`, `packages/context_bootloader/*`, `packages/timeline_context_system/*`, context packaging docs.
- **Validation proof:** Decision packet created at `docs/roundtable/decisions/DEC-007_CONTEXT_SYSTEM_CONSOLIDATION_PACKET_2026-03-05.md`; supporting evidence in `PROJECT_TRUTH/00_evidence_ledger.md` (context systems section).
- **Rollback condition:** If adjudication rejects lane federation, replace with explicit single-canon promotion decision and migration plan.
- **Thread:** `aimos_roundtable_operational_convergence_2026-03-04`

---

## DEC-008 | HTTP Fallback (:5001) Required for Codex — Canonize Startup | 2026-03-06

- **Decision ID:** DEC-008
- **Owner:** Braden (COMMAND), Composer (audit/canon)
- **Chosen option:** Canonize that MCP HTTP fallback on `:5001` MUST run for Codex IDE connectivity. Codex has no stdio path; only Cursor spawns `lucid_mcp_server.py` directly. Codex depends on HTTP bridge. Add to startup checklist and MCP runbook.
- **Rationale:** Codex repeatedly fails to connect when HTTP fallback is not running. Cursor works; Codex looks broken. Root cause: transport asymmetry. Canonizing prevents recurrence.
- **Impacted surfaces:** `docs/MCP_RUNBOOK.md`, agent startup checklists, `.agent/STARTUP.md`, `docs/CODEX_IDE_MCP_ONBOARDING_V1.md`.
- **Validation proof:** Team message sent via MCP; memory stored (atom `85707be7-36d0-49eb-a017-cc005004b097`). Runbook updated with Codex canon.
- **Rollback condition:** Explicit COMMAND override if Codex gains native stdio path.
- **Thread:** `aimos_roundtable_mcp_recovery_audit_2026-03-06`

---

## Next decision ID: DEC-009
