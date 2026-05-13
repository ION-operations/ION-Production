# AIMOS Restore-Mode Selection Surface Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_31_2026-03-14`

This map answers what each visible restore-mode selection family appears best at
locally. It does not choose a restore canon.

| Surface family | What it appears best at locally | Where it seems narrower than siblings | What unique restore-selection value it preserves |
| --- | --- | --- | --- |
| Startup-checklist or fail-closed-law surfaces | Best at deciding when the deepest safe startup restore is mandatory before any action | Narrower than bus, capsule, chat, and findings-board surfaces in exact live lane specificity | Preserves the only sampled selector family that can explicitly say "do not proceed normally yet" |
| Live bus current-assignment surfaces | Best at deciding when exact current-task restore may already be enough | Narrower than chat and findings boards in rationale and lane-wide reading, and narrower than capsules in bounded anti-drift framing | Preserves the sharpest local answer to "what is active right now?" |
| Capsule `NOW/BLOCKER/NEXT` surfaces | Best at deciding when bounded handoff restore is sufficient | Narrower than chat in richer explanation and narrower than findings boards in synthesized multi-packet reading | Preserves the clearest structured answer to "what is the bounded state, what is blocked, and what happens next?" |
| Chat rationale or immediate-reason surfaces | Best at deciding when richer contextual restore is needed before acting | Narrower than startup law in hard safety gating and narrower than live bus or capsules in strict state compactness | Preserves the clearest human-readable answer to "why is this restore depth needed?" |
| Findings-board current-best-reading or next-priority surfaces | Best at deciding when synthesized multi-packet restore depth is required | Narrower than live bus in freshness and narrower than capsules in bounded handoff precision | Preserves the strongest local answer to "what broader current reading and next unresolved layer must be understood before proceeding?" |

## Local Answer

No single restore-mode selection family is universally sufficient locally.
The visible stack separates cleanly by selection role:

- startup law selects deepest safe startup restore
- live bus selects exact current-task restore
- capsules select bounded handoff restore
- chat rationale selects richer contextual restore
- findings boards select synthesized multi-packet restore

The local restore-selection answer is therefore compositional, not singular.
