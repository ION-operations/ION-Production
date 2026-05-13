# AIMOS Restore-Arbitration Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_32_2026-03-14`

This comparison stays inside evidence only.
It does not choose a restore canon, rewrite arbitration surfaces, or assume
that one restore-arbitration surface alone is universally sufficient without
sibling evidence.

| Surface family | Escalation force | Boundedness | Lane specificity | Operator readability | Machine-parseability | Overread resistance | Freshness | Drift or arbitration-risk tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fail-closed or no-normal-execution surfaces | Highest; nothing else in the sample set is stronger at forcing a stop | High; the command is blunt and explicit | Medium; applies across the organism more than inside one packet | High; the stop law is clear | Medium; structured sections exist, but prose carries the force | Highest; hard-stop language resists casual overread into permissive action | Low to medium; doctrine is stable rather than event-fresh | Medium; safest at preventing unsafe execution, but broadness can overconstrain if not paired with packet-local or lane-local surfaces |
| Active work-package non-goal or acceptance-boundary surfaces | High; they strongly block overreach beyond the current packet contract | Highest; non-goals and acceptance are tight | Highest; packet-local and lane-specific | High; packet sections are direct | High; headings and checklists are regular | High; explicit non-goals make overread harder | High; refreshed on each active packet | Low to medium; strongest at preventing local scope drift, weaker at organism-wide stop or deeper-restore arbitration |
| Capsule `MUST-NOT` or `BLOCKER` surfaces | High; they can force hold or refuse escalation inside the current handoff state | High; concise fielded structure keeps the hold bounded | High; packet and lane specific | High; terse and easy to scan | High; field schema is stable | Medium to high; must-not fields resist overread, though brevity can hide nuance | High; capsules track live packet movement closely | Low to medium; strongest anti-drift hold surface, but can under-carry the wider reason for escalation |
| Chat explicit risk or insufficiency framing surfaces | Medium to high; they can strongly argue for deeper restore or against premature action | Medium; prose is broader than packet or capsule boundaries | High; packet openings remain lane-specific | Highest; strongest human explanation layer | Medium; structure exists, but prose dominates | Medium; rich explanation can still be overread as sufficient authority on its own | High; updated on packet opening and synthesis | Medium; very useful for arbitration sense-making, but less strict than hard-stop or boundary surfaces |
| Findings-board unresolved-ambiguity or next-priority surfaces | High; they explicitly escalate to the next unresolved evidence layer | Medium to high; the synthesis is focused but broader than packet-local boundaries | High; boards stay inside the current lane lineage | High; concise and interpretable | Medium; structured sections with prose-heavy conclusions | High; unresolved-ambiguity framing resists shallow closure well | Medium; one synthesis step behind the live edge by design | Medium; strongest for justified deeper restore escalation, but weaker than fail-closed or packet law at immediate hard-stop control |

## Direct Comparative Reading

- Fail-closed or no-normal-execution surfaces are strongest when the question is "must all normal action stop now?"
- Active work-package non-goal or acceptance-boundary surfaces are strongest when the question is "is this action outside the current packet's authorized envelope?"
- Capsule `MUST-NOT` or `BLOCKER` surfaces are strongest when the question is "should I hold inside the current packet state rather than escalate?"
- Chat explicit risk or insufficiency framing surfaces are strongest when the question is "why is the current restore still insufficient?"
- Findings-board unresolved-ambiguity or next-priority surfaces are strongest when the question is "does the lane now require escalation to the next deeper evidence layer?"

## Visible Arbitration Gaps And Overclaim Risks

1. Fail-closed law can stop action hardest, but it does not by itself distinguish whether the right response is bounded hold, packet-local boundary respect, or deeper synthesized restore.
2. Active work-package non-goal and acceptance surfaces strongly arbitrate local overreach, but they do not by themselves settle organism-wide arbitration when broader ambiguity remains.
3. Capsule `MUST-NOT` and `BLOCKER` surfaces are the cleanest bounded hold signals, but their brevity can under-express whether the next move should be hard stop, wait, or deeper restore.
4. Chat risk framing explains insufficiency best for a human, but explanation alone is not as hard-edged as fail-closed law or packet boundaries.
5. Findings-board unresolved-ambiguity and next-priority surfaces justify deeper restore escalation best, but they are less fresh than the newest live turn and therefore not the strongest immediate stop surface.

## Evidence Boundaries

- Fail-closed or no-normal-execution surfaces were treated as hard-stop arbitration, not as the only packet-local scope boundary.
- Active work-package non-goal or acceptance-boundary surfaces were treated as packet-envelope arbitration, not as total organism-wide stop law.
- Capsule `MUST-NOT` or `BLOCKER` surfaces were treated as bounded hold arbitration, not as exhaustive rationale.
- Chat explicit risk or insufficiency framing surfaces were treated as explanatory arbitration, not as sole formal authority.
- Findings-board unresolved-ambiguity or next-priority surfaces were treated as synthesized escalation arbitration, not as live-edge hard-stop law.
