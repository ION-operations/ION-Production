# AIMOS Restore-Mode Selection Surface Profile Matrix - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_31_2026-03-14`

This matrix compares visible restore-mode selection families only.
It records evidence, not restore-canon decisions.

| Surface family | Representative local sample | Primary selection role | What kind of restore-depth question it appears to answer | Update pattern visible locally | Strongest interaction with sibling selection surfaces | Strongest visible local ambiguity, contradiction, or drift risk |
| --- | --- | --- | --- | --- | --- | --- |
| Startup-checklist or fail-closed-law surfaces | `.agent/STARTUP.md` and `.agent/workflows/startup.md` | Select whether a fresh host must do the deepest safe restore before any normal action | "Do I need full identity, doctrine, MCP, inbox, and status startup before acting at all?" | Relatively stable doctrine with occasional edits; not event-driven like bus or chat surfaces | Gives every sibling selector a safety floor by saying when acting without deeper restore is forbidden | Strong on safety law but broad and generic, so it can imply more restore depth than the exact live lane may need if read without fresher selectors |
| Live bus current-assignment surfaces | `ai_msg_237_20260314_175703` opening WP31<br>`ai_msg_234_20260314_175310` completing WP30 on thread `consolidation_wp30_2026_03_14` | Select whether a fresh or returning agent can act from the exact current assignment state already visible on the bus | "Is the live current task precise and fresh enough that I can restore only to the active assignment layer?" | Refreshes immediately on each dispatch or completion event | Gives startup law a current target and gives packet, capsule, and chat surfaces the freshest task anchor | Extremely fresh but narrow; a precise current assignment does not by itself answer whether richer rationale or synthesized history is needed before safe action |
| Capsule `NOW`, `BLOCKER`, and `NEXT` surfaces | SEV capsule `2026-03-14T17:56 | PRE`<br>SEV capsule `2026-03-14T17:57 | POST` | Select whether bounded handoff state is sufficient rather than deeper narrative or multi-packet restore | "Is a concise bounded snapshot of current task, blocker state, and next action enough for safe re-entry?" | Refreshed around each packet in PRE/POST cadence | Gives live bus and packet state a bounded anti-drift frame and gives chat/findings readers a concise control-state checkpoint | Strong on boundedness, but compressed wording can hide why a deeper restore is needed if the reader does not inspect sibling rationale or findings surfaces |
| Chat rationale or immediate-reason surfaces | SEV chat `Entry 028` in `.agent/comms/chat/sev/2026-03-14.md` | Select whether richer packet rationale is needed before acting | "Why is this next packet open, and what unresolved ambiguity makes deeper restore necessary?" | Appended as packet openings and syntheses happen | Gives capsule and bus signals the explanatory bridge that turns state into reasoned restore depth | Highly readable, but prose can blur exact proof boundaries and may still depend on sibling files for the sharpest current-state or evidence limits |
| Findings-board current-best-reading or next-priority surfaces | `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_28_2026-03-14.md`<br>`.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_29_2026-03-14.md` | Select whether synthesized multi-packet reading is required before acting | "Do I need the lane's current best reading and next unresolved layer before I can safely proceed?" | Refreshed after completed packets and then preserved as descriptive synthesis | Gives startup, bus, capsule, and chat selectors the broadest evidence-backed reading of what restore depth is now warranted | Strong at lane-level interpretation, but less fresh than the newest live event and therefore capable of lagging one packet edge if read alone |

## Evidence Base

- Work package: `.agent/sev/CONSOLIDATION_WORK_PACKAGE_31_2026-03-14.md`
- Findings boards: `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_28_2026-03-14.md`, `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_29_2026-03-14.md`
- Startup doctrine: `.agent/STARTUP.md`, `.agent/workflows/startup.md`
- Live bus reads: `get_ai_messages(to_ai="codex", limit=12)`, `get_ai_messages(to_ai="sev", limit=8)`
- Chat log: `.agent/comms/chat/sev/2026-03-14.md`
- Capsule log: `.agent/comms/capsules/sev/2026-03-14.md`
