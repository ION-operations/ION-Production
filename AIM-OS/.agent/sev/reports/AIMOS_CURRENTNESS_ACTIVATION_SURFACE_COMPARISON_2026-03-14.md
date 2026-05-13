# AIMOS Currentness-Activation Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_27_2026-03-14`

This comparison stays inside evidence only.
It does not choose a final current-state canon, rewrite continuity surfaces, or assume that the freshest-looking surface is authoritative without sibling comparison.

| Surface family | Currentness explicitness | Activation strength | Lane specificity | Freshness | Continuity value | Operator readability | Machine-parseability | Drift or staleness tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Live bus directive or message surfaces | Highest; message IDs and timestamps state what just activated or completed | Highest; this is the strongest family for proving that WP27 is live now | High; messages are thread- and recipient-specific | Highest; live read at request time | Medium; message history is strong, but less synthesized than chat docs | Medium to high; clear when short, denser across long queues | Highest; JSON-like structured fields are direct | Lowest for immediate activation, but dependent on transport availability and queue reading discipline |
| Active work-package law surfaces | High; packets clearly state purpose, authorized outputs, and non-goals | High for authorization, medium for activation because the bus still has to make a packet current | Highest; no sibling family is narrower about exact task scope | Medium; the current packet is fresh, but older active-looking packets persist unchanged | High; packet trail preserves lane progression clearly | High; packet sections are easy to scan | High; repeatable markdown structure makes them relatively machine-friendly | Medium to high; many packet files remain "active when picked up" on disk after activation has moved on |
| Capsule current-state surfaces | High; `NOW`, `NEXT`, and `HANDOFF` state current lane position directly | Medium to high; strong for bounded current state, weaker than the bus for proving lane activation | High; capsule entries are agent- and turn-specific | High when latest capsule is read | High; this family is optimized for handoff continuity | High; compact format makes current state quick to spot | Medium to high; stable labeled fields help | Medium; capsules are strong anti-drift surfaces, but dated filenames and missed writes can still mislead |
| Chat-doc entry surfaces | Medium to high; entries usually state what just happened and what lane follows | Medium; chat records activation and completion well, but usually after the live event is already known on the bus | High; lane and artifact references are explicit | Medium to high; fresh if the latest entry has landed, weaker if logging lags | Highest; richest recent-history continuity of any family here | High; readable narrative with artifacts, atoms, and message IDs | Medium; semi-structured prose is less parseable than packets or bus messages | Medium to high; long logs, out-of-order numbering, and dated filenames can slow "what is current now?" reading |
| Status-file surfaces | Medium; `Current Work` and `State` speak plainly when updated | Lowest; they declare currentness, but do not activate the lane | Medium to high; agent identity is explicit, but task scope is often broad | Lowest in the visible local sample set | Medium; quick snapshot value exists, but not rich continuity | Highest; easiest one-glance scan | Medium; headings are simple, but content is freeform | Highest; the sampled files lag the 2026-03-14 consolidation lane by one to ten days |

## Direct Comparative Reading

- Live bus surfaces are strongest when the question is "what became active most recently?"
- Active work-package law surfaces are strongest when the question is "what exactly is authorized right now if this packet is the live one?"
- Capsule surfaces are strongest when the question is "what does the agent currently say it is doing, avoiding, and doing next in bounded form?"
- Chat-doc surfaces are strongest when the question is "what just happened across the lane, with enough context to reconstruct the sequence?"
- Status files are strongest when the question is "what does this agent declaratively claim at a glance?" rather than "what is truly current now?"

## Visible Freshness And Activation Contradictions

1. Live bus message `ai_msg_214_20260314_143021` says WP27 is open now, while `.agent/sev/CONSOLIDATION_WORK_PACKAGE_25_2026-03-14.md`, `.agent/sev/CONSOLIDATION_WORK_PACKAGE_26_2026-03-14.md`, and `.agent/sev/CONSOLIDATION_WORK_PACKAGE_27_2026-03-14.md` all remain present and all use `Active when picked up`.
2. `ai_msg_210_20260314_141754` proves WP26 completion on the bus at 14:17 on 2026-03-14, but the status files still describe much older realities: `sev.status.md` from 2026-03-13 15:50 UTC still centers Aether OS migration law, `codex.status.md` from 2026-03-12 21:17 ET still centers JARVIS and MCP root work, and `antigravity.status.md` from 2026-03-04 12:30 predates the current consolidation campaign.
3. `.agent/comms/chat/codex/2026-03-13.md` and `.agent/comms/capsules/codex/2026-03-13.md` contain March 14 work-package entries even though their filenames still point to 2026-03-13, which preserves continuity but weakens filename-level freshness cues.
4. SEV capsule entries at 14:28 and 14:30 on 2026-03-14 show WP27 opening in bounded pre/post form, while the richer SEV chat log narrates the same move in more detail; both are fresher than any visible status file but still lag the instant of live bus activation.
5. Chat and capsule surfaces preserve currentness better than status files, but neither by itself proves that a packet is live unless the bus or equivalent live dispatch also confirms activation.

## Evidence Boundaries

- Live bus surfaces were treated as strongest evidence of live activation, not as complete continuity history.
- Active work-package law surfaces were treated as authorization surfaces, not as self-proving live activation.
- Capsule current-state surfaces were treated as bounded agent-declared current state, not as whole-organism truth.
- Chat-doc entry surfaces were treated as rich recent-history evidence, not as the instant activation source.
- Status-file surfaces were treated as declared snapshot surfaces only, not as reliable live-current proof on this host.
