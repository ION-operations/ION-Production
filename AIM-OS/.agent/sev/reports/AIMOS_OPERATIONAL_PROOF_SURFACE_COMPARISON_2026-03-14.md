# AIMOS Operational-Proof Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_21_2026-03-14`

This comparison stays inside evidence only.
It does not choose a proof canon or turn README or test claims into live proof.

| Surface family | Claim breadth | Behavioral proof strength | Runtime specificity | Freshness of proof | Failure visibility | Operator readability | Machine-query value | Drift or overclaim tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| README or declarative-claim surfaces | Highest; they make the broadest package and system claims | Weak by themselves; they describe intent more than observed behavior | Low; they rarely bind claims to the current host state | Low to medium; files persist, but nothing in them proves they match current runtime | Weak; failures are usually omitted or softened | Highest; fastest way to understand intended role and promise | Medium; readable but not structured around runtime state | Highest; package claims can outrun usage, wiring, or current host health |
| Implementation or code surfaces | High; code reveals broader capability than tests or probes alone | Medium; code proves mechanisms exist but not that the current host is exercising them | Medium; entrypoints and data shapes are explicit, but activation and wiring remain separate questions | Medium; fresher than dated reports if actively edited, but still not per-run proof | Medium; missing imports or dead code are visible, but quiet non-use is not | Medium to low; exact but slower for operators to scan | Highest; code is the deepest structured source for exact mechanics | Medium to high; rich implementation can look operational even when runtime adoption is absent |
| Automated test surfaces | Medium; narrower than README claims and broader than single live probes | High for controlled slices; they are the strongest falsifiable proof that selected behaviors work under test conditions | Low to medium; they bind to fixtures, mocks, and local object state more than the active host | Low unless rerun; this packet read test surfaces but did not execute them | High when a test is run, but only medium from file inspection alone | Medium; clearer than raw code but denser than reports | Medium to high; assertions are structured, but tied to test harnesses rather than live state | Medium; tests can overstate readiness if they mostly cover isolated or mocked flows |
| Synthesized verification or report surfaces | Medium to high; they aggregate multiple checks into one narrative | Medium; stronger than README because they cite bounded checks, weaker than rerun probes because they are interpreted summaries | Medium to high; they usually name exact systems, tools, and methods | Medium to low; dated packets can drift from the host quickly | High; degradation, unknowns, and method boundaries are usually made explicit | High; they are built for operator review | Medium; structured enough for scanning, but less machine-native than raw code or probe JSON | Medium; summaries can remain accurate in role but drift in current numbers or transport state |
| Live probe surfaces | Narrowest; each probe proves a smaller slice | Highest for current host behavior in the exact slice exercised | Highest; they bind directly to this machine, this bridge, and this runtime state | Highest; each result is current-run evidence | Highest; errors and unhealthy counters surface immediately | Medium; outputs are factual but often terse or tool-shaped | High; JSON or command output is directly consumable | Lowest for current host truth, but narrowness itself can mislead if treated as total-system proof |

## Direct Comparative Reading

- README surfaces are strongest at saying what AIM-OS claims to be able to do, but they are the weakest proof family when current host state diverges.
- Implementation surfaces are strongest at showing what AIM-OS is concretely built to do, but they still stop short of proving that the current host is wired, populated, or actively using those paths.
- Automated tests are strongest at proving controlled behaviors repeatably, but the sampled suites visibly depend on mocks and local object instantiation, so they cannot stand in for live-runtime proof.
- Synthesized reports are strongest at packaging bounded checks into one operator-readable layer, but their dated numbers and transport assumptions can drift as the host changes.
- Live probes are strongest at proving what is true right now on this machine, but they only prove the slices they actually touch.

## Visible Proof-Strength Contradictions

1. `packages/vif/README.md` presents VIF as production-ready with `153 passing tests` and `95% coverage`, while current live stats still show `total_predictions=0` and `current_ece=0.0`.
2. `packages/temporal_consciousness/README.md` and `packages/timeline_context_system/timeline_api.py` describe rich temporal graph and timeline capability, while current `get_timeline_summary(limit=5)` reports `total_prompts=0`.
3. `.agent/sev/reports/RUNTIME_TRUTH_MAP_2026-03-13.md` reports `427` atoms, `0` write errors, and stdio-native MCP as working, while current live probes show fallback HTTP bridge readiness, `692` atoms, and `7` write errors.
4. Current live `retrieve_memory("session state")` failed with `tuple index out of range` even though `scripts\mcp.cmd status` still reported `ready=True` and `tools=103`.

## Evidence Boundaries

- README claims were treated as declarative surfaces only.
- Test files were treated as proof of controlled assertions, not proof that those assertions passed in this session.
- Dated reports were treated as bounded historical verification, not as automatic current-host truth.
- Live probes were treated as the freshest evidence, but only for the exact slices they exercised.
