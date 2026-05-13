# AIMOS Status-Classification Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_24_2026-03-14`

This comparison stays inside evidence only.
It does not choose a final status canon or treat one surface vocabulary as authoritative without sibling comparison.

| Surface family | State-vocabulary breadth | Class specificity | Machine-parseability | Degraded-state nuance | Bounded-proof linkage | Freshness of state | Operator readability | Semantic drift or ambiguity tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Broad verdict-map surfaces | Highest; they carry the widest explicit status language across systems and transports | Medium; verdicts are broad rather than field-level | Medium; tables are structured, but many verdicts are prose composites | Medium to high; `BROKEN`, `DEGRADED`, and `FUNCTIONAL but UNUSED` carry nuance beyond binary states | Medium; linked to probe columns but still mostly summary-level | Low to medium; packet-dated and visibly older than current host signals | High; easiest family for executive scanning | Highest; broad verdict phrases can drift against later live fields or bounded cards |
| Bounded verification-result surfaces | Medium; tight vocabulary by design | High; `live`, `degraded`, and `unavailable` are explicitly defined with method framing | Medium; tables are structured, but class semantics still rely on human boundary notes | Medium; captures degraded state cleanly, but with fewer shades than degraded registers | Highest; this family is built directly around explicit bounded verification methods | Medium to low; stronger than old verdict maps conceptually, but still dated | High; concise and disciplined | Medium; tight vocabulary reduces ambiguity, but dated bounded results can still be over-read |
| Degraded-register surfaces | Medium; narrower than verdict maps but richer than pure booleans | Medium to high; weak-state descriptions are specific, but not uniformly enumerated | Medium; table structure is machine-readable, observation prose is less so | Highest; this family is the most expressive about weak, partial, noisy, empty, or unavailable states | Medium; entries often cite sibling surfaces rather than carrying full proof context themselves | Medium to low; dated register evidence | High; the weakness framing is easy to scan | Medium; less drift-prone than broad verdict maps, but still selective and dated |
| Live machine status-field surfaces | Low to medium; vocabulary is narrower but much more exact | Highest; booleans, counters, modes, and error fields are the sharpest classes in the current host | Highest; this family is the most directly machine-readable | Medium; degraded meaning must be inferred from combinations of fields rather than named richly | Low to medium; direct fields are current, but bounded-proof context lives elsewhere | Highest; current-run evidence | Medium; dense JSON or status output is readable but less narrative | Lowest for literal field truth, but highest for interpretation ambiguity if read without sibling context |
| Package-test or assertion-outcome surfaces | Medium; the language is narrower but still varied across asserts, booleans, and named statuses like `pending` or `resolved` | High for package-local outcomes, low for system-wide state | High; assertion outcomes are structurally crisp | Low; this family mostly expresses expected outcome rather than runtime degradation nuance | Low; tests imply proof conditions, but do not carry bounded-live host context by themselves | Low unless rerun; in this pass they were read, not executed | Medium; readable to engineers, slower for operators | High; package pass/fail semantics can be mistakenly promoted into runtime-health language |

## Direct Comparative Reading

- Verdict maps are strongest at broad named verdict language, but weakest at holding that vocabulary steady against later live details.
- Verification cards are strongest at disciplined result classes because they define what `live`, `degraded`, and `unavailable` mean in a bounded method frame.
- Degraded registers are strongest at weak-state nuance because they preserve more shades of runtime weakness than the verification cards or live booleans do.
- Live status fields are strongest at literal current-state precision, but they often need sibling interpretation before they become a human verdict.
- Package assertions are strongest at crisp local pass/fail expectation language, but weakest at expressing full host-runtime status.

## Visible Status-Language Contradictions

1. The broad verdict map says CMC is `ALIVE`, HHNI is `BROKEN`, VIF is `FUNCTIONAL but UNUSED`, APOE and SEG `EXIST, need verification`, CAS is `DEGRADED`, and transport states include `WORKING`, `SLOW/INTERMITTENT`, `UNKNOWN`, and `PARTIAL`.
2. The bounded verification card uses the tighter result set `live`, `degraded`, and `unavailable`, which reclassifies APOE and SEG from earlier "exists, needs verification" into `live` once bounded checks were actually run.
3. The degraded register does not try to verdict everything; instead it keeps weakness-shaped language like `runtime retrieval/index not initialized`, `live but still low-evidence operationally`, `empty runtime graph`, and `package entrypoint unavailable`.
4. Current live fields say `Health: OK`, `Tool Surface: READY`, `status: operational`, `ready: true`, and `integrity.overall_ok: true`, while simultaneously reporting `write_errors_total: 8`, `hhni.index_available: false`, `retriever_available: false`, and no VIF predictions.
5. Package assertions say things like `result.passed is True`, `result.passed is False`, `state.is_hot(...)`, `state.is_cold(...)`, and `status == "pending"`, but these are package-local outcome words rather than host-runtime verdicts.

## Evidence Boundaries

- Broad verdict maps were treated as high-level state language, not current literal truth.
- Verification cards were treated as bounded status classes tied to explicit methods.
- Degraded registers were treated as preserved weakness vocabulary, not exhaustive health taxonomy.
- Live machine fields were treated as current machine-state facts, not self-sufficient human verdicts.
- Package assertions were treated as package-outcome language only, not as direct runtime-health labels.
