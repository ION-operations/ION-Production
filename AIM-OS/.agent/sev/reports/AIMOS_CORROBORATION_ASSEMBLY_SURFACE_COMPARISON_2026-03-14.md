# AIMOS Corroboration-Assembly Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_29_2026-03-14`

This comparison stays inside evidence only.
It does not choose a final continuity or proof canon, rewrite assembly surfaces,
or assume that one assembled surface alone is sufficient proof without sibling
evidence.

| Surface family | Multi-cue density | Cross-surface binding completeness | Temporal specificity | Lane specificity | Continuity value | Operator readability | Machine-parseability | Contradiction visibility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Live bus completion or dispatch message surfaces | High; one message carries IDs, thread, timestamp, sender, recipient, priority, and summary text | Medium to high; strong at binding one live event, weaker at binding the whole downstream file trail | Highest; event timestamps are exact and immediate | Highest; thread IDs are tightly lane-shaped | Medium; the bus preserves event continuity more than broad narrative continuity | Medium to high; compact but terse | Highest; fielded and regular | Low to medium; contradictions usually appear only when sibling surfaces are compared |
| Chat synthesis entry surfaces | Highest; packet, artifacts, findings, IDs, atoms, scope, and next-lane cues often appear together | Highest; chat entries are the strongest local bundle for tying one packet move to artifacts, findings, and receipts in prose | Medium; entries may cite precise IDs but usually rely on sibling timestamps rather than carrying all of them inline | Highest; entries are packet- and lane-specific | Highest; strongest readable reconstruction layer across successive moves | Highest; designed for human scan and recovery | Medium; headings and bullets are structured, but prose remains dominant | High; chat can name contradictions directly while still keeping the broader packet narrative intact |
| Capsule evidence-block surfaces | High; each block gathers current task, constraints, evidence, blocker, next, and handoff in one bounded form | High; the evidence field explicitly binds IDs, files, and packet state, though with less narrative breadth than chat | High; each block has its own timestamp and often cites timed IDs | High; capsules are lane-bounded and packet-scoped | High; strongest bounded handoff continuity layer | High; terse but regular | High; the field schema is stable and parse-friendly | Medium; blockers and evidence can expose drift, but nuance is intentionally compressed |
| Findings-board synthesis surfaces | Medium to high; they gather several prior answers and unresolved ambiguities, but fewer raw receipts than chat or capsules | High; boards bind multiple completed packets into one synthesized reading | Medium; boards are date-stamped but less event-specific than the live bus or capsules | High; boards stay inside the current consolidation lane and packet lineage | High; strongest current-reading synthesis across completed work | High; concise and readable | Medium; section structure is consistent, but conclusions remain prose-heavy | Medium to high; unresolved ambiguities are explicit, but raw contradictions are summarized rather than fully replayed |
| Report evidence-base or contradiction surfaces | High; sources, contradictions, and reading limits are grouped directly inside the comparative artifact | High; they bind claims to named inputs and explicit caveat lists | Medium; report dates are clear, but event-level timing is usually inherited from cited siblings | Medium to high; report families are packet-scoped, though narrower than chat or boards in lane breadth | Medium; they preserve proof discipline more than broad continuity recovery | Medium to high; readable, but denser and more local than chat or boards | High; lists, tables, and boundary sections are structured | Highest; contradiction and evidence-boundary sections are the sharpest local place where overclaims are explicitly surfaced |

## Direct Comparative Reading

- Live bus completion or dispatch message surfaces are strongest when the question is "what is the freshest compact proof bundle for the live event itself?"
- Chat synthesis entry surfaces are strongest when the question is "what is the most readable assembled lane proof for a human trying to understand the move?"
- Capsule evidence-block surfaces are strongest when the question is "what is the cleanest bounded anti-drift proof bundle for handoff and current-state control?"
- Findings-board synthesis surfaces are strongest when the question is "what is the current synthesized reading across several finished evidence passes?"
- Report evidence-base or contradiction surfaces are strongest when the question is "what exact proof anchors and contradiction anchors justify this comparative claim?"

## Visible Proof-Assembly Gaps And Overclaim Risks

1. A live bus message proves a dispatch or completion event cleanly, but by itself it does not prove the full artifact bundle, the findings-board synthesis, or the richer lane narrative that later file surfaces provide.
2. Chat entries assemble the broadest readable proof bundle locally, but CODEX chat still sits in `.agent/comms/chat/codex/2026-03-13.md` while carrying March 14 packet activity, so filename date and content date can diverge inside the assembled bundle.
3. Capsule evidence blocks are the cleanest bounded form, but their brevity means the reader often needs sibling chat or reports to recover full contradiction context.
4. Findings boards synthesize several corroboration cues into one current reading, but they inherit raw IDs, timestamps, and contradiction detail from underlying chat, capsules, bus messages, and reports rather than replaying all of them directly.
5. Report evidence-base and contradiction sections are the sharpest local proof-discipline surfaces, but they remain packet-local and do not by themselves restore the whole lane sequence or live bus state.

## Evidence Boundaries

- Live bus completion or dispatch message surfaces were treated as compact event bundles, not as complete lane proof on their own.
- Chat synthesis entry surfaces were treated as assembled human-readable proof bundles, not as machine-perfect canonical truth.
- Capsule evidence-block surfaces were treated as bounded handoff bundles, not as exhaustive narrative history.
- Findings-board synthesis surfaces were treated as descriptive current-reading bundles, not as directive law.
- Report evidence-base or contradiction surfaces were treated as packet-local proof discipline anchors, not as whole-lane restore surfaces.
