# AIMOS Operational-Proof Surface Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_21_2026-03-14`

This map answers what each operational-proof family appears best at locally.
It does not select a final proof canon.

| Surface family | Best at locally | Narrower than siblings where | Unique proof value preserved |
| --- | --- | --- | --- |
| README or declarative-claim surfaces | Best at stating the intended capability envelope, expected maturity, and operator-facing promise of a package or subsystem | They are weaker than implementation, tests, reports, and live probes at proving actual behavior on this host | They preserve the clearest top-level statement of what the system says it is trying to do |
| Implementation or code surfaces | Best at preserving the exact executable mechanics, schemas, endpoints, and query paths AIM-OS is built to support | They are weaker than live probes at proving current host reality and weaker than reports at quick synthesized interpretation | They are the only surfaces that show the concrete machinery behind the claims |
| Automated test surfaces | Best at proving repeatable controlled slices of behavior and regression intent | They are weaker than live probes at current host truth and weaker than README surfaces at broad package intent | They turn implementation into falsifiable assertions with explicit expected outcomes |
| Synthesized verification or report surfaces | Best at packaging bounded checks into one dated, operator-readable verification layer | They are weaker than raw code for exact mechanics and weaker than current probes for freshness | They preserve the clearest bridge between scattered evidence and human review |
| Live probe surfaces | Best at proving what the current host, bridge, and runtime return right now | They are weaker than code and tests at expressing total capability breadth and weaker than README surfaces at stating larger intent | They are the only surfaces that can immediately confirm or contradict older claims with current runtime state |

## Best-At Answer

- README surfaces are best at declaring AIM-OS capability.
- Implementation surfaces are best at encoding AIM-OS capability.
- Automated test surfaces are best at controlled proof of AIM-OS capability.
- Synthesized reports are best at summarizing bounded proof of AIM-OS capability.
- Live probes are best at current-host proof of AIM-OS capability.

## Local Constraint

The current host does not let any single family stand alone as total proof:

- README claims outrun current live counters.
- Implementation richness outruns current live activation.
- Tests prove controlled slices, not this session's runtime.
- Reports preserve bounded verification, but their numbers can drift.
- Live probes are freshest, but narrow and failure-shaped.
