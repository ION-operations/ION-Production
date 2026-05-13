# AIMOS Restore-Mode Selection Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_31_2026-03-14`

This comparison stays inside evidence only.
It does not choose a restore canon, rewrite selector surfaces, or assume that
one restore-mode selector alone is universally sufficient without sibling
evidence.

| Surface family | Restore-depth selection power | Freshness | Boundedness | Lane specificity | Operator readability | Machine-parseability | Overread risk | Drift or selection-risk tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Startup-checklist or fail-closed-law surfaces | High for selecting deepest safe restore versus no-action states | Low to medium; doctrine is stable, not event-fresh | High; checklist and fail-closed rules are explicit | Medium; applies across lanes more than inside one packet | High; startup law is easy to follow | Medium to high; checklist form is regular | High; broad safety law can be over-applied as if it always settles exact restore depth alone | Medium; good at preventing unsafe under-restore, weaker at choosing the narrowest sufficient restore |
| Live bus current-assignment surfaces | High for selecting exact active-task restore when the lane edge is clear | Highest; no sibling family is fresher | High; the current assignment is narrow and precise | Highest; thread and packet references are lane-specific | High; compact and direct | Highest; message fields are structured | Medium to high; easy to overread freshness as total sufficiency | Medium; strongest for exact currentness, weaker for rationale or broader lane meaning |
| Capsule `NOW/BLOCKER/NEXT` surfaces | High for selecting bounded handoff restore | High; capsule timestamps track packet movement closely | Highest; these fields are explicitly bounded | High; packet-scoped and lane-bounded | High; concise and scannable | High; field schema is regular | Medium; brevity can hide when richer rationale or synthesis is still needed | Low to medium; strongest anti-drift selector, but compressed context is the main selection risk |
| Chat rationale or immediate-reason surfaces | Very high for selecting whether richer contextual restore is needed | Medium to high; prompt but not as immediate as bus or capsule state | Medium; prose is broader than packet or capsule fields | High; packet openings are lane-specific | Highest; strongest human explanation layer | Medium; structure exists but prose dominates | Medium; rationale can sound sufficient even when proof or current-state siblings still need to be checked | Medium; strong for explaining depth, weaker for strict bounded control |
| Findings-board current-best-reading or next-priority surfaces | Very high for selecting whether synthesized multi-packet restore is needed | Medium; by design they trail the newest live event | Medium to high; focused but broader than packet-level state | High; boards stay inside current lane lineage | High; concise and interpretable | Medium; section structure is regular but prose-heavy | Medium; synthesis can be overread as current enough for every situation | Medium; strongest for choosing deeper synthesized restore, weaker for live-edge exactness |

## Direct Comparative Reading

- Startup-checklist or fail-closed-law surfaces are strongest when the question is "do I need the deepest safe startup restore before doing anything?"
- Live bus current-assignment surfaces are strongest when the question is "is the active assignment clear and fresh enough that an exact current-task restore may suffice?"
- Capsule `NOW/BLOCKER/NEXT` surfaces are strongest when the question is "is a bounded handoff restore enough right now?"
- Chat rationale or immediate-reason surfaces are strongest when the question is "why is deeper contextual restore needed before acting?"
- Findings-board current-best-reading or next-priority surfaces are strongest when the question is "do I need synthesized multi-packet reading before proceeding safely?"

## Visible Restore-Selection Gaps And Overclaim Risks

1. Startup law can correctly force deep safe restore, but it does not by itself choose the narrowest sufficient restore depth once the host is already alive and the bus is healthy.
2. Live bus current-assignment surfaces can make exact current-task restore look sufficient, but they do not by themselves say whether bounded handoff, rationale, or synthesized lane reading is still required.
3. Capsule `NOW/BLOCKER/NEXT` surfaces are the cleanest bounded selectors, but their compression can under-express why a deeper restore is needed.
4. Chat rationale surfaces explain restore depth best for a human, but they can still under-carry the hard safety and currentness boundaries held by startup law, live bus state, or capsules.
5. Findings-board current-best-reading and next-priority surfaces best signal when deeper synthesized restore is needed, but they are less fresh than the newest live assignment and can therefore lag the lane edge.

## Evidence Boundaries

- Startup-checklist or fail-closed-law surfaces were treated as safety selectors, not as universally exact current-lane selectors.
- Live bus current-assignment surfaces were treated as exact currentness selectors, not as complete restore-depth selectors by themselves.
- Capsule `NOW/BLOCKER/NEXT` surfaces were treated as bounded handoff selectors, not as exhaustive rationale or synthesis layers.
- Chat rationale or immediate-reason surfaces were treated as explanatory selectors, not as the only proof or safety boundary surfaces.
- Findings-board current-best-reading or next-priority surfaces were treated as synthesized depth selectors, not as live-edge currentness proof.
