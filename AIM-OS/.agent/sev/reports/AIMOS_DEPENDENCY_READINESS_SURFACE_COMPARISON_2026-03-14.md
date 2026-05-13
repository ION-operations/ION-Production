# AIMOS Dependency-Readiness Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_23_2026-03-14`

This comparison stays inside evidence only.
It does not choose a health canon or turn bridge readiness or package-side success into proof of full subsystem health without sibling evidence.

| Surface family | Bridge-readiness clarity | Subsystem-health specificity | Bounded-live proof strength | Degraded-state clarity | Package-capability visibility | Freshness of evidence | Operator readability | Drift or over-readiness tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bridge-level readiness probe surfaces | Highest; they say most directly whether the bridge is up and a top-level tool call answers | Low to medium; they do not reveal much about deeper subsystem internals by themselves | Medium; they are live but broad and transport-oriented | Low; they can miss degraded subsystem states entirely | Low; they say almost nothing about package-local capability | Highest; each probe is current-run evidence | High; the outputs are short and direct | Highest risk of over-readiness if mistaken for total subsystem health |
| Subsystem status-tool surfaces | Medium; they assume the bridge is already reachable | Highest; they expose current counters, initialization flags, and subsystem-specific failures | High for current subsystem state in the slices they cover | High; they are the strongest current source for explicit partial initialization or empty-runtime signals | Low to medium; they report runtime state, not package breadth | Highest; current-run evidence | Medium to high; structured JSON is readable but more technical than status lines | Medium; they are narrow but usually less likely than bridge probes to overstate health |
| Bounded verification-card surfaces | Medium; they can mention tool-path success, but bridge readiness is not their sole focus | High; they classify live, degraded, and unavailable states with method notes | Highest for bounded live proof because they explicitly record what was executed and how | Medium to high; degraded classifications are present, but only within the earlier packet scope | Medium; package-native probes are visible through their verification notes | Medium to low; dated packet evidence can drift against current runtime | High; this family is built for operator review | Medium; strong framing reduces drift, but older results can still be over-read as current truth |
| Degraded-feature register surfaces | Low to medium; it depends on other surfaces for bridge facts | Medium to high; it is selective but explicit about weak or degraded runtime features | Medium; it preserves observed degradation rather than fresh proof | Highest; this is the clearest family for carrying forward weak, partial, noisy, or empty-state evidence | Medium; it often explains package/runtime splits directly | Medium to low; dated register evidence | High; concise degraded-state table | Low to medium; it tends to understate healthy breadth more than overstate readiness |
| Package-native smoke or test surfaces | Low; they do not tell you whether the bridge is up | Low to medium; they show local component behavior, not live subsystem initialization | Medium for package-local behavioral proof, low for host-runtime proof | Low by themselves; failures matter when run, but file inspection mostly shows what is intended to be testable | Highest; this family most clearly shows what the package can do locally | Low unless rerun; in this pass they were read, not executed | Medium; readable but code-oriented | Highest risk of over-reading package capability into live runtime health |

## Direct Comparative Reading

- Bridge-level readiness probes are strongest at answering "is the bridge up right now?" but weakest at answering "are the dependent subsystems healthy?"
- Subsystem status tools are strongest at current subsystem state and are the sharpest evidence that bridge readiness and subsystem readiness are not the same thing.
- Bounded verification cards are strongest at preserving disciplined, dated live-check evidence that touched both package-side and tool-path surfaces in a controlled way.
- Degraded-feature registers are strongest at preserving the failure-shaped side of readiness truth across sessions.
- Package-native smoke or test surfaces are strongest at showing that the package can do something locally even when the live runtime is still uninitialized, degraded, or unused.

## Visible Dependency-Readiness Contradictions

1. Bridge-level readiness is healthy right now: `scripts\mcp.cmd status` showed `ready=True`, `mode=fallback-http-bridge`, `tools=103`, and `total_atoms=710`, and `get_ai_messages(...)` succeeded.
2. Subsystem status still shows deeper weakness: `get_memory_stats(...)` reported `hhni.index_available=false`, `retriever_available=false`, `write_errors_total=8`, and zero VIF predictions, while `get_hhni_status(...)` returned `hhni_index_initialized=false`, `index_nodes=0`, and `cmc_error="tuple index out of range"`.
3. The bounded verification card already captured the same shape on 2026-03-13: HHNI package-native indexing and querying succeeded locally while the live runtime remained uninitialized, and VIF package-native and tool-path checks succeeded while operational evidence remained thin.
4. The degraded-feature register preserves the weak-runtime interpretation explicitly: HHNI runtime bridge uninitialized, VIF operational evidence weak, SEG runtime content empty, and SIS import surface unavailable.
5. Package-side tests still show meaningful local capability: HHNI tests cover document indexing and paragraph query behavior, VIF tests cover many kappa-gate and escalation scenarios, and CAS tests cover activation-state capture and warning logic, but none of that proves the live runtime is fully initialized today.

## Evidence Boundaries

- Bridge-level readiness probes were treated as top-level transport readiness only.
- Subsystem status tools were treated as current subsystem-state evidence only for the subsystems they expose.
- Verification cards were treated as bounded dated proof, not automatic current-host truth.
- Degraded registers were treated as preserved weakness evidence, not exhaustive system truth.
- Package-native tests were treated as package-capability evidence, not as proof of live subsystem health in this session.
