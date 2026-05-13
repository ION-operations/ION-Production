# AIMOS Restore-Bundle Family Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_30_2026-03-14`

This comparison stays inside evidence only.
It does not choose a startup or restore canon, rewrite restore surfaces, or
assume that one restore bundle alone is universally sufficient without sibling
evidence.

| Restore-bundle family | Restore sufficiency | Freshness | Boundedness | Lane specificity | Proof discipline | Operator readability | Machine-parseability | Drift or restore-risk tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Startup-doctrine plus live-bus bundles | High for cold-start safety; strongest at getting a fresh host onto the right rails before deeper lane restore | High when paired with live bus, but doctrine itself is slower-moving | Medium; startup doctrine is broad even when the bus is current | Medium to high; the bus is lane-specific, the doctrine is more general | Medium to high; protocol law is explicit, but proof anchors are lighter than report bundles | High; startup steps are readable | Medium to high; checklist structure is strong, prose still matters | Medium; startup bundles can still mislead if generic doctrine is read without the current packet or current chat/capsule state |
| Live-bus plus active-work-package bundles | Very high for exact current-task restore | Highest; no sibling family is fresher on current assignment state | High; active packet law sharply bounds the task | Highest; thread plus packet scope is tightly lane-specific | High; packet constraints and acceptance are explicit | High; compact and direct | High; message fields and packet structure are regular | Low to medium; strong if both bus and packet are present, weaker if one side is missing |
| Capsule plus active-work-package bundles | High for safe handoff restore, especially under decision-freeze constraints | High; capsule timestamps are fresh around packet movement | Highest; must-not, evidence, blocker, next, and packet scope create the cleanest bounded bundle | High; packet-scoped and lane-bounded | High; constraints and evidence are explicit and disciplined | High; concise and scannable | High; capsule field schema is regular | Low to medium; strongest anti-drift bundle, but compressed context can require sibling chat for fuller understanding |
| Chat-entry plus cited-artifact bundles | Very high for human restore of what happened and what to read next | Medium to high; entries are prompt, but not as immediate as the live bus | Medium; richer narrative makes them broader than capsules or packets | High; entries stay inside packet and lane context | Medium to high; citations are strong, though proof discipline is looser than report bundles | Highest; strongest for human comprehension | Medium; headings and bullets help, but prose dominates | Medium; date-path divergence and narrative compression are the main restore risks |
| Findings-board plus proof-report bundles | High for evidence-backed current-reading restore across completed work | Medium; usually one step behind the newest live event by design | Medium to high; more bounded than chat, broader than packet or capsule law | High; the bundle stays inside the current lane and report lineage | Highest; findings plus proof reports preserve the strongest evidence discipline in one bundle | High; boards are concise and the attached reports are explicit | Medium to high; boards are prose-heavy, reports are structured | Medium; the bundle can over-compress live-state shifts if read without the latest bus or packet surface |

## Direct Comparative Reading

- Startup-doctrine plus live-bus bundles are strongest when the question is "how do I re-enter safely from a cold start and get pointed at the live lane?"
- Live-bus plus active-work-package bundles are strongest when the question is "what exactly is active now, with the freshest exact task law?"
- Capsule plus active-work-package bundles are strongest when the question is "what is the safest bounded handoff state for this active packet?"
- Chat-entry plus cited-artifact bundles are strongest when the question is "what happened, what landed, and which files do I read next to understand it?"
- Findings-board plus proof-report bundles are strongest when the question is "what is the current evidence-backed reading across the finished packets?"

## Visible Restore Gaps And Overclaim Risks

1. Startup doctrine plus the live bus can safely orient a fresh host, but it still does not by itself supply the fullest bounded packet context or the richest narrative explanation of what just happened.
2. Live bus plus active work package is the freshest exact bundle, but it is narrow; it restores the active contract better than the broader lane meaning or synthesized multi-packet state.
3. Capsule plus active work package is the tightest anti-drift bundle, but the compression that makes it safe also means a reader can miss nuance without sibling chat or findings-board support.
4. Chat-entry plus cited-artifact bundles restore human understanding well, but the same narrative breadth that helps readability can blur exact proof boundaries or expose filename-date drift across sibling logs.
5. Findings-board plus proof-report bundles are the strongest evidence-backed synthesized restore, but they inherit some delay relative to the newest live bus state and can therefore understate the freshest packet opening if read alone.

## Evidence Boundaries

- Startup-doctrine plus live-bus bundles were treated as safe entry bundles, not as complete current-lane proof by themselves.
- Live-bus plus active-work-package bundles were treated as exact current-task bundles, not as full lane-history restore.
- Capsule plus active-work-package bundles were treated as bounded handoff bundles, not as exhaustive narrative restore.
- Chat-entry plus cited-artifact bundles were treated as readable packet restores, not as strict proof-boundary or cold-start law surfaces.
- Findings-board plus proof-report bundles were treated as evidence-backed synthesized restores, not as live activation proof.
