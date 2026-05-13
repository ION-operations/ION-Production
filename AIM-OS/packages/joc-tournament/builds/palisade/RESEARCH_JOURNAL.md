# Palisade Research Journal — JARVIS Tournament

**Agent:** Palisade  
**Date:** 2026-03-07  
**Phase:** Research (before design proposal)

---

## Sources Read

- RULES.md (7 laws, Phase 1 gate, deliverables)
- AESTHETIC_BRIEF.md (DXL/Hasselblad/military DNA, palette, material language)
- HERITAGE_INDEX.md, README.md (canon, backend, shell components)
- Codex Tournament Brief (championship question, 7 primary workspaces, Mission Control as Phase 1)
- DAC V2 Design Document (5-zone layout, 31 panels, hooks, state)
- Best Ideas Synthesis (Aether/Max/Lex/Codex/Dac/Rev — best panels and systems)
- panelRegistry.ts (12 panels, 12 workspaces, DataStatus, DATA_STATUS_CONFIG)
- shared/types.ts (TruthState, PRIMARY_WORKSPACES, OperatorAction)
- Existing Palisade research: PALISADE_JARVIS_RESEARCH_2026-03-07.md (law-by-law interpretation)

---

## Observations

### What Worked in Heritage

1. **5-zone layout is consensus** — TopBar, Left Drawer, Main, Right Drawer (or Rail), Bottom. Mission Control doesn’t need right drawer for round one; Assistant Rail is the right-side fixture. So: TopBar | Left | Main | Rail | Bottom.

2. **Codex’s thesis is the filter** — “Operator legibility over a real intelligence organism.” If Braden can’t see what’s live, broken, and what agents are doing in seconds, the build fails. That prioritizes: system health, agent fleet, mission/approval state, and truth labels — not panel count.

3. **Mission Control is the right Phase 1 page** — It’s the clearest proof of “cockpit”: fleet + system status + activity. Canon already gives dashboard defaultLeftPanels = agent-fleet, system-status; bottomPanels = activity-feed. I’ll use that as the drawer contract.

4. **Left drawer = workspace-local command context** — Not a generic panel list. For Mission Control specifically: Agent Fleet + System Status. Each as a real panel (recessed, truth-labeled), not a placeholder strip.

5. **Bottom bar = temporal/diagnostic** — Activity feed for Mission Control. Terminal/problems/debug can appear in other workspaces. For Phase 1, one bottom strip with Activity Feed is enough to prove the grammar.

6. **Data truth is non-negotiable** — Every surface: LIVE | CACHED | MOCK | OFFLINE | SPECULATIVE. Small, unmistakable (8px-dot scale per Aesthetic Brief). No mock masquerading as live.

7. **Aesthetic Brief is the visual law** — Matte black (#0A0A0C), surface levels, single amber (#F5A623) for primary action, recessed LCD feel, engraved typography (uppercase labels, monospace data), dense but hierarchical. SkeuPanel/SkeuCard/SkeuLCD/SkeuLED in `packages/joc/src/components/surface/` are the right primitives. Test: screenshot next to Panavision DXL — same design language.

8. **Degraded mode** — When MCP/backend is down, show OFFLINE and optionally a shell-level “connectivity” state. No blank or ambiguous states.

### What to Avoid

- **Spectacle over legibility** — Hero visuals that hide agent status or system health.
- **Panel sprawl** — More panels don’t win; coherent Mission Control with the canonical three (fleet, status, activity) does.
- **Generic dark UI** — Flat #121212, glassmorphism, neon. Use the Aesthetic Brief palette and recessed/beveled language.
- **Silent mock data** — Every data surface must declare truth state.
- **One shell, many labels** — Workspace switch must change left drawer and bottom; for Phase 1 we only implement Mission Control, but the shell must be built so that switching workspace would reconfigure it.

### Open Decisions for the Brief

- **Workspace set:** Codex’s 7 primary + 5 secondary is convincing; I’ll adopt it and state Mission Control as first of the 7.
- **Assistant Rail:** Persistent, workspace-aware; for Phase 1, one mode (e.g. context or chat) with clear width (280–420px) and collapse. Don’t overbuild; prove it’s there and that it’s the “intelligence rail.”
- **Navigation:** TopBar workspace switcher (primary), command palette (secondary), keyboard shortcuts. No deep nested nav for Phase 1.
- **Truth signals:** Per-panel badge or corner dot using DATA_STATUS_CONFIG; 8px LED-style where possible (SkeuLED). Global “MCP: Live/Offline” in TopBar or status strip.

---

## Conclusion

Mission Control, built to the Aesthetic Brief and the 7 laws, with Agent Fleet + System Status in the left drawer and Activity Feed in the bottom strip, and every surface truth-labeled, will answer the championship question: *Which build makes AIM-OS easiest to govern as a real organism?* Next step: formal DESIGN_BRIEF.md with answers to the 7 key design questions and a concrete layout sketch for Braden’s review.
