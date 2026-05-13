# AIMOS Continuity Surface Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_14_2026-03-14`
Status: evidence-only comparative answer map

## Best-At Answers

| Continuity family | What it appears best at locally | Where it seems narrower than siblings | Unique continuity value preserved locally | Direct evidence |
| --- | --- | --- | --- | --- |
| Dated chat docs | Best at preserving a rich human-readable audit trail of completed work, created artifacts, scope constraints, and returned MCP IDs | Narrower than capsules for compact recovery, narrower than status for one-glance snapshots, and narrower than MCP for direct queryability | Preserves the densest visible narrative ledger of what actually happened in the lane, especially for active agents like `codex` and `sev` | Chat docs show the highest local line density, and `.agent/comms/chat/codex/2026-03-13.md` records work-package entries with artifacts, atoms, and scope-hold notes |
| Dated capsules | Best at preserving bounded turn-to-turn recovery context without requiring a reader to parse a long narrative log | Narrower than chat for full audit richness, narrower than status for fastest snapshot reading, and narrower than MCP for global query/filter behavior | Preserves the clearest anti-drift handoff format in the continuity family through PRE/POST control fields | `.agent/comms/capsules/codex/2026-03-13.md` repeatedly locks `MISSION`, `MUST-NOT`, `EVIDENCE`, `NEXT`, and `HANDOFF` into compact recoverable state |
| Status files | Best at giving a single-file glance at declared current work, blockers, and availability | Narrower than chat and capsules on history, narrower than `current_priorities.md` on stable standing intent, and narrower than MCP on live cross-agent retrieval | Preserves the fastest file-based "what does this lane say it is doing?" surface when the file is actually fresh | Status files are short and snapshot-like, but `codex.status.md`, `sev.status.md`, and `antigravity.status.md` also show how quickly this family falls behind rolling continuity |
| `current_priorities.md` files | Best at preserving medium-horizon priorities and standing orders that should survive beyond a single turn | Narrower than status on immediate freshness, narrower than chat and capsules on concrete recent actions, and narrower than MCP on cross-agent live visibility | Preserves intent continuity that is more stable than a momentary status file but lighter than a full narrative log | The visible files keep standing-order structure, but still name earlier genome/onboarding/backend-audit priorities rather than today's packet stream |
| MCP-backed continuity surfaces | Best at live cross-agent continuity and machine-readable retrieval, especially for current assignments and ID-backed coordination | Narrower than chat for rich narrative explanation, narrower than capsules for bounded human handoff, and currently weakened by uneven memory and timeline retrieval quality | Preserves the only live query surface that can expose fresh tasking immediately without scanning multiple files | `get_ai_messages` returned the live WP14 assignment immediately, while `retrieve_memory` returned `0` focused continuity hits and `get_timeline_entries` returned older generic entries rather than today's consolidation lane |

## Net Comparative Answer

1. Dated chat docs appear best at rich audit-trail continuity.
2. Dated capsules appear best at bounded handoff and drift-resistant recovery continuity.
3. Status files appear best at at-a-glance declared current state.
4. `current_priorities.md` files appear best at standing-order and medium-horizon intent continuity.
5. MCP-backed continuity appears best at live cross-agent and machine-readable continuity, with messages currently much stronger than memory or timeline recall.

The map stays comparative. It does not choose a final single source of truth.
