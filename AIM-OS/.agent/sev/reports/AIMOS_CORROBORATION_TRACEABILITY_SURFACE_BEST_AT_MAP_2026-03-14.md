# AIMOS Corroboration-Traceability Surface Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_28_2026-03-14`

This map answers what each corroboration-and-traceability family appears best at locally.
It does not select a final continuity canon.

| Surface family | Best at locally | Narrower than siblings where | Unique corroboration or traceability value preserved |
| --- | --- | --- | --- |
| Timestamp or date-stamp surfaces | Best at temporal anchoring of lane evidence | They are weaker than message/thread IDs at object identity and weaker than artifact paths at concrete file grounding | They preserve the clearest answer to when a cue appeared |
| Message and thread ID surfaces | Best at binding live bus events to a specific lane thread | They are weaker than timestamps at quick human chronology and weaker than artifact paths at pointing to disk files | They preserve the strongest live-event lineage in the lane |
| Artifact path citation surfaces | Best at grounding narrative claims in concrete files | They are weaker than timestamps at time precision and weaker than atoms at proving a write actually persisted | They preserve the clearest filesystem trace from summary to artifact |
| Packet and entry numbering surfaces | Best at placing a move inside the lane sequence | They are weaker than timestamps at exact time and weaker than message IDs at exact live-event identity | They preserve ordinal position across the packet, findings-board, and log trail |
| Atom and checkpoint ID surfaces | Best at proving that a durable checkpoint or write occurred | They are weaker than chat/path surfaces at human-readable context and weaker than numbering surfaces at intuitive sequence placement | They preserve the strongest durable-write receipt in the lane |

## Best-At Answer

- Timestamp or date-stamp surfaces are best at temporal anchoring.
- Message and thread ID surfaces are best at live-event lineage.
- Artifact path citation surfaces are best at filesystem grounding.
- Packet and entry numbering surfaces are best at ordinal lane placement.
- Atom and checkpoint ID surfaces are best at durable-write proof.

## Local Constraint

No single corroboration-and-traceability family stands alone as total lane proof on this host:

- timestamps say when but not fully what,
- message and thread IDs say which event but not the whole file trail,
- artifact paths say where but not freshness,
- numbering says sequence but not exact identity,
- and atom IDs prove persistence but not meaning without sibling context.
