# AIMOS Restore-Arbitration Surface Profile Matrix - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_32_2026-03-14`

This matrix compares visible restore-arbitration families only.
It records evidence, not restore-canon decisions.

| Surface family | Representative local sample | Primary arbitration role | What kind of stop/escalate/deepen question it appears to answer | Update pattern visible locally | Strongest interaction with sibling arbitration surfaces | Strongest visible local ambiguity, contradiction, or drift risk |
| --- | --- | --- | --- | --- | --- | --- |
| Fail-closed or no-normal-execution surfaces | `.agent/STARTUP.md` lines requiring no normal execution while MCP is down and "DO NOT begin any work until you complete this checklist" | Force hard stop before normal execution when core safety conditions are not met | "Must action stop completely rather than proceed with a shallower restore?" | Stable doctrine updated only when host law changes | Gives every sibling arbitration family a hard floor that stronger contextual surfaces cannot undercut casually | Strongest at absolute stop law, but broad enough that it can over-govern more specific lane conditions if read without packet or capsule boundaries |
| Active work-package non-goal or acceptance-boundary surfaces | `Explicit Non-Goals` and `Acceptance Standard` in `.agent/sev/CONSOLIDATION_WORK_PACKAGE_31_2026-03-14.md` | Force bounded hold against overreading current authorization or claiming completion too early | "Does current packet law block me from escalating into cleanup, canon choice, or acting as if the packet solved more than it did?" | Refreshed per packet; each work package reasserts bounded scope and completion gate | Gives fail-closed law a packet-local boundary and gives chat/capsule warnings a concrete task envelope | Precise inside one packet, but narrower than findings boards or chat at telling whether deeper restore outside the packet is warranted |
| Capsule `MUST-NOT` or `BLOCKER` surfaces | SEV capsules `2026-03-14T17:56 | PRE` and `2026-03-14T17:57 | POST` | Force bounded hold, anti-drift discipline, or waiting state when the next move is not yet safely justified | "Should I hold because the current state is blocked, constrained, or explicitly not allowed to escalate?" | Refreshed in PRE/POST cadence around packet transitions | Gives packet boundaries and live lane state a compact operational stop/hold signal that can be checked quickly | Highly effective at local discipline, but concise wording can under-explain the broader reason for the hold without sibling chat or findings-board context |
| Chat explicit risk or insufficiency framing surfaces | SEV chat `Entry 029` in `.agent/comms/chat/sev/2026-03-14.md` | Force deeper restore by naming what remains unresolved or insufficient in the current reading | "Why is current restore depth not enough, and what unresolved problem makes deeper arbitration necessary?" | Refreshed when a new packet is opened or synthesized | Gives capsules and packets the readable narrative that explains why a stop, hold, or deeper restore is necessary | Rich explanatory prose is strong for humans but can blur exact hard boundaries if read without startup law, packet limits, or findings-board synthesis |
| Findings-board unresolved-ambiguity or next-priority surfaces | `F-128/F-129` in `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_29_2026-03-14.md`<br>`F-132/F-133` in `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_30_2026-03-14.md` | Force escalation to a deeper evidence layer when unresolved ambiguity remains | "Do the current unresolved ambiguities require deeper synthesized restore before safe action?" | Refreshed after completed packets land and are synthesized | Gives chat, capsule, and packet warnings a broader lane-level justification and points to the next deeper evidence family | Strong at synthesized escalation logic, but less fresh than the newest packet edge and can therefore lag one live turn behind |

## Evidence Base

- Work package: `.agent/sev/CONSOLIDATION_WORK_PACKAGE_32_2026-03-14.md`
- Findings boards: `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_29_2026-03-14.md`, `.agent/sev/reports/CONSOLIDATION_FINDINGS_BOARD_30_2026-03-14.md`
- Startup doctrine: `.agent/STARTUP.md`
- Packet boundary surface: `.agent/sev/CONSOLIDATION_WORK_PACKAGE_31_2026-03-14.md`
- Capsule log: `.agent/comms/capsules/sev/2026-03-14.md`
- Chat log: `.agent/comms/chat/sev/2026-03-14.md`
