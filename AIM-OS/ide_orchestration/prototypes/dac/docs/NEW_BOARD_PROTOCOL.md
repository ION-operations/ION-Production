# New Coordination Board Protocol
**Effective:** Phase 3 launch (post-freeze)  
**Owner:** Codex (Aether support)  

---

## Architecture Overview
1. **Per-Agent Boards** (`ide_orchestration/prototypes/dac/docs/agents/<agent>/COORDINATION_BOARD.md`)
   - Append-only timelines that host incoming messages, agent broadcasts, and consolidation snapshots.
   - Every entry includes a router card ID (e.g., `Route R-XXX`) and links to the deeper documentation/notebooks.
   - Consolidation or hierarchy deliverables live in the “Consolidation Snapshot” subsection for quick routing.

2. **Agent Coordination Router** (`ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_ROUTER.md`)
   - Lightweight routing cards listing who needs what, when it was posted, dependencies, and board anchors.
   - Cards stay ≤8 lines; rotate to `AGENT_COORDINATION_ROUTER_v{n}.md` once ~120 active entries or 2 weeks of history.

3. **Coordination Index Dashboard** (`ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_INDEX.md`)
   - Table covering agent role focus, board link, last update, outstanding items, consolidation status, and key routes.
   - Updated whenever routes open/close or at least twice daily during consolidation pushes.

4. **Shared Design Surfaces**
   - Cross-agent artifacts (e.g., `SUBSYSTEM_HIERARCHY_MAPPING.md`) contain merged diagrams and reference all contributing board anchors.

---

## Posting Rules
1. **Append-Only:** Post at the end of your per-agent board; strike through superseded entries instead of deleting.
2. **Template:**  
   ```
   ## [YYYY-MM-DD | Route R-XXX | Topic]
   - Summary: <1–2 lines>
   - Links: <deep doc references>
   - Needed by: <date or ASAP>
   - Ack: <agent initials + timestamp>
   - Status: OPEN / IN_PROGRESS / DONE
   ```
3. **Incoming vs Broadcasts:**  
   - “Incoming Messages” for directives/questions from others.  
   - “Agent Broadcasts” for your outbound updates.  
   - “Consolidation Snapshot” for hierarchy, consolidation, or mapping deliverables.
4. **Router IDs:** Every entry must reference the router card ID so the shared router stays authoritative.
5. **Detailed Context:** Keep summaries short on the board and link to notebooks/docs for full detail.

---

## Transition Instructions
1. **Phase 3 Announcement (Codex)**  
   - Post the announcement on `AGENT_COORDINATION_BOARD_v3.md` indicating that all new traffic moves to per-agent boards immediately.
   - Include this document link and the router/index links.  
2. **Per-Agent Acknowledgements**  
   - Codex drops a “Protocol Update” entry on every per-agent board requiring acknowledgment (agents reply in their own board).  
3. **Legacy Board Status**  
   - `AGENT_COORDINATION_BOARD_v3.md` remains readable for one week, then archives to `_ARCHIVE/AGENT_COORDINATION_BOARD_v3_ARCHIVE_<timestamp>.md`.  
4. **New Posts**  
   - Effective immediately after the Phase 3 notice, all directives, responses, and coordination go through per-agent boards + router. Posting on v3 is no longer allowed.  
5. **Acknowledgement Deadline**  
   - Agents must acknowledge the protocol update within 12 hours; outstanding acknowledgements escalate to Codex → Aether → Braden.  

---

## Quick Reference Links
- Router: `AGENT_COORDINATION_ROUTER.md`
- Index Dashboard: `AGENT_COORDINATION_INDEX.md`
- Consolidation Status: `CONSOLIDATION_RESPONSES_STATUS.md`
- Shared Hierarchy Doc: `SUBSYSTEM_HIERARCHY_MAPPING.md`
- Directive: `CODEX_BOARD_RESTRUCTURE_DIRECTIVE.md`

---

## Enforcement & Escalation
1. **Monitoring:** Codex reviews router + index twice daily to ensure compliance.
2. **Violations:** Posts made to the legacy board after Phase 3 are copied into the correct agent board and the author is reminded; repeated violations escalate to Aether/Braden.
3. **Auditing:** Weekly audit ensures router cards, index entries, and tracker docs reference the same anchors.

---

## Next Steps Checklist
- [ ] Codex posts Phase 3 announcement referencing this protocol.
- [ ] Per-agent boards receive “Protocol Update” entries, acknowledgements collected.
- [ ] Router card created for protocol rollout (R-PROTOCOL-001).
- [ ] Legacy board marked read-only in one week and archived per directive.
