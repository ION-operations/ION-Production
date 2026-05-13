# Codex: Board Restructure Directive
**Date:** 2025-01-27  
**From:** Braden  
**Priority:** P0 (CRITICAL)  
**Status:** Codex Lead, Aether Support Only

---

## Ã°Å¸Å½Â¯ **DIRECTIVE**

**Codex:** You are now leading the board restructure and team organization fix. Aether will observe and support, but you make the decisions.

**Aether:** Step back. Support Codex. Do not interfere. Let Codex design the solution.

---

## Ã°Å¸Å¡Â¨ **CURRENT PROBLEMS**

1. Board is a mess (16,574 lines, overwrites, confusion)
2. Agents confused about where to post
3. No clear structure
4. Response tracking unclear
5. File size unmanageable

---

## Ã¢Å“â€¦ **WHAT CODEX NEEDS TO DO**

**Design a new structure that:**
- Prevents overwrites
- Makes it clear where agents post
- Tracks responses easily
- Manages file size
- Doesn't confuse agents
- Supports their consolidation work

**Then:**
- Implement the new structure
- Get team up to speed
- Ensure agents can continue work without disruption

---

## Ã°Å¸â€œâ€¹ **CURRENT STATE**

- v2 board: 16,574 lines (archived)
- v3 board: Created but may need restructuring
- 7/8 consolidation responses confirmed
- Nova needs to post response

---

## Ã°Å¸Å½Â¯ **SUCCESS CRITERIA**

- Clean, clear structure
- No more overwrites
- Easy for agents to use
- Supports consolidation work
- Team understands new system

---

**Codex: You have full authority. Design the solution. Aether will support but not interfere.**

**Aether: Step back. Let Codex work. Support when asked.**

---

**Status:** Codex Lead Active  
**Next:** Codex designs and implements new structure

---

## Codex Restructure Plan (Draft for Aether + Braden Sign-Off)

### Architecture Overview
- **Per-agent boards:** Each agent owns a lightweight `COORDINATION_BOARD.md` inside their folder (`ide_orchestration/prototypes/dac/docs/agents/<agent>/`). Boards are append-only, chronological, and link back to the agentÃ¢â‚¬â„¢s detailed notebooks for full context.
- **Router board:** A single `AGENT_COORDINATION_ROUTER.md` at `ide_orchestration/prototypes/dac/docs/` that holds compact routing cards (who needs what, when it was posted, current status, link to agent board entry). This replaces the monolithic shared board.
- **Index & status dashboard:** A concise `AGENT_COORDINATION_INDEX.md` that lists every agent, key boards, last activity timestamp, outstanding requests, and completion snapshots for Braden. Target size <200 lines.
- **Shared design surfaces:** Cross-agent collaboration (e.g., hierarchy mapping) lives in purpose-built shared docs such as `ide_orchestration/prototypes/dac/docs/SUBSYSTEM_HIERARCHY_MAPPING.md`, each referencing the agent board anchors that supplied the source material.

### Per-Agent Board Protocol
1. **File location:** `ide_orchestration/prototypes/dac/docs/agents/<agent>/COORDINATION_BOARD.md` (create if missing).
2. **Entry template:**  
   `## [YYYY-MM-DD | Agent | Topic]`  
   `- Summary:` short intent / request  
   `- Links:` pointer(s) to rich-doc context  
   `- Needed by:` date or ASAP tag  
   `- Ack:` responding agent initials + timestamp  
   `- Status:` `OPEN / IN_PROGRESS / DONE`
3. **Rules:**  
   - Append-only; strike-through superseded entries instead of deleting.  
   - Full analysis stays in the agentÃ¢â‚¬â„¢s dedicated docs; boards only hold summaries and links.  
   - Each entry references its router card ID (e.g., `Route R-012`).  
   - Agents acknowledge directives on their own board and only post brief updates to shared boards.

4. **Board layout template:**  
   ```
   # [AGENT] Coordination Board

   ## Posting Protocol
   - Append at bottom only; no deletions.
   - Include router card ID + timestamp.

   ## Incoming Messages
   - `[DATE | Route R-XXX] FROM -> TO : summary (link)`
   - For directives/questions from other agents/Codex/Aether.

   ## Agent Broadcasts
   - `[DATE | Route R-XXX] AGENT -> Audience : summary (link)`
   - Outbound updates, including consolidation or hierarchy notes.

   ## Consolidation Snapshot
   - Short log of this agentÃ¢â‚¬â„¢s consolidation/hierarchy deliverables.
   - Houses migrated responses from legacy board plus pointers to detailed notebooks.
   ```
   Multi-agent discussions live as separate entries inside each participantÃ¢â‚¬â„¢s board; the shared router card ties them together so we retain a linear audit trail without introducing overwrite risk.

### Router Board Design
- **File:** `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_ROUTER.md`
- **Sections:** `Open Routes`, `In Progress`, `Waiting on External`, `Closed`.
- **Card template:**
  ```
  ### Route R-XXX (Owner -> Target)
  - Posted: <timestamp> by <owner>
  - Summary: <one line goal>
  - Agent link: <agents/<name>/COORDINATION_BOARD.md#anchor>
  - Dependencies / blockers
  - Next review: <date>
  ```
- Router cards must stay Ã¢â€°Â¤8 lines; anything larger belongs in the linked agent doc.
- **Rotation:** When the router nears ~120 entries or two weeks of activity, spin a new versioned file (`AGENT_COORDINATION_ROUTER_v{n}.md`) and archive closed cards so the active router stays lightweight. The index dashboard surfaces whichever router version is live plus archive pointers.

### Index / Status Dashboard
  - **File:** `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_INDEX.md`
  - **Contents:** table `[Agent | Role focus | Board link | Last update | Outstanding items | Consolidation status]` plus a `Global Metrics` block (total open routes, priorities, last sync).
  - Columns also capture the active router card IDs for consolidation + hierarchy mapping so every tracker links to the exact board anchor.
  - **Cadence:** Update whenever a route opens/closes or at least twice per day during consolidation pushes.

### Migration & Archival Steps
  1. **Phase 0 Ã¢â‚¬â€œ Freeze & Snapshot:** Pause new long-form posts on `AGENT_COORDINATION_BOARD.md`, record the timestamp, and inform agents the migration window has begun.
  2. **Phase 1 Ã¢â‚¬â€œ Parallel Setup:** Generate every per-agent board plus router/index skeletons while v3 stays live; seed each with the template + critical doc links.
  3. **Phase 2 Ã¢â‚¬â€œ Consolidation Migration:** Move all consolidation responses (including NovaÃ¢â‚¬â„¢s pending entry) and any active directives into their boards, creating router cards for each anchor and leaving acknowledgement breadcrumbs on v3.
  4. **Phase 3 Ã¢â‚¬â€œ Announcement & Dual-Read:** Publish `NEW_BOARD_PROTOCOL.md`, drop per-agent Ã¢â‚¬Å“Protocol UpdateÃ¢â‚¬Â entries, and mark v3 as read-only yet readable for one week while new traffic flows through the router/per-agent structure.
  5. **Phase 4 Ã¢â‚¬â€œ Final Archive:** After stabilization week, archive `AGENT_COORDINATION_BOARD_v3.md` into `_ARCHIVE/AGENT_COORDINATION_BOARD_v3_ARCHIVE_<timestamp>.md` and log the cutover in the index dashboard.

### Communication Rollout
  - Publish `NEW_BOARD_PROTOCOL.md` summarizing architecture, file locations, and posting rules.
  - Notify every agent via their board with a `Protocol Update` entry requiring acknowledgement.
  - Codex + Aether verify acknowledgements; escalate missing confirmations to Braden.

  ### Tracker Integration
  - Update `CONSOLIDATION_RESPONSES_STATUS.md`, `AGENT_COORDINATION_INDEX.md`, and `AGENT_SYSTEM_ASSIGNMENTS.md` to reference per-agent board anchors instead of the monolithic board.
  - Stand up `SUBSYSTEM_HIERARCHY_MAPPING.md` for the shared hierarchy design synthesis, with backlinks to each contributing agent board entry.
  - Ensure every new router card lists the tracker/doc(s) it updates so downstream automation can stay in sync.

### Risks & Mitigations
- **Agents forget to link detailed docs:** Router template enforces link; weekly spot-check by Codex.  
- **File sprawl:** Rotate monthly board snapshots (`COORDINATION_BOARD_2025-02.md`) and keep active file <300 lines.  
- **Missed approvals:** Execution checklist (below) blocks implementation until Codex + Aether + Braden sign-off is logged.

### Execution Checklist & Sign-Off Gate
1. Ã¢Å“â€¦ Codex finalizes this plan and confirms scope with Aether.  
2. Ã¢Å“â€¦ Aether review logged (see section below).  
3. Ã¢Å“â€¦ Braden approval recorded before restructuring begins.  
4. Ã¢Å“â€¦ **Phase 0:** Freeze new large posts on v3 board, capture timestamp, notify agents migration prep underway. **COMPLETE** - 2025-01-27 10:28 UTC  
5. Ã¢ËœÂ **Phase 1:** Generate all per-agent boards + router/index skeletons in parallel while v3 stays live. **COMPLETE** - 2025-01-27 11:00 UTC (boards + router/index seeded).  
6. ï¿½~? **Phase 2:** Migrate consolidation responses + active directives, create router cards, drop acknowledgement comments in v3. **COMPLETE** - 2025-01-27 11:05 UTC (entries relocated, router/index refreshed).  
7. Ã¢ËœÂ **Phase 3:** Publish `NEW_BOARD_PROTOCOL.md` + board-specific pings, mark v3 read-only.  
8. Ã¢ËœÂ **Phase 4:** Route all new traffic through router + per-agent boards, monitor for one week.  
9. Ã¢ËœÂ **Phase 5:** Archive v3 board, update index with cutover date, notify Braden of completion.

### Review & Feedback Log
- **Codex Notes:** Ã¢Å“â€¦ Complete - All 6 concern areas addressed with concrete resolutions (consolidation migration, hierarchy mapping, phased cutover, board templates, router rotation, tracker integration). Plan expanded in directive with shared design surface, detailed board layout, router rotation policy, phased migration schedule, and tracker-integration steps.  
- **Aether Feedback:** Ã¢Å“â€¦ Complete - All 6 follow-ups added confirming alignment. All concerns addressed. Consolidation Snapshot section, router card system, phased migration, board template structure, router rotation strategy, and tracker integration all align with requirements. No outstanding concerns. Ready for Braden approval.  
- **Braden Decision:** Ã¢Å“â€¦ **APPROVED** - 2025-01-27 - Full approval granted. Proceed with implementation.

### Next Immediate Actions
1. Codex shares this plan with Aether for asynchronous commentary (within this directive).  
2. Capture Aether feedback above and revise as needed.  
3. Present final plan plus checklist to Braden for approval.  
4. After sign-off, execute checklist in order and log completions in router/index files.



