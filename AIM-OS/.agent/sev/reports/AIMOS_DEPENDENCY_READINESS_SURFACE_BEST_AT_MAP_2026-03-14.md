# AIMOS Dependency-Readiness Surface Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_23_2026-03-14`

This map answers what each dependency-readiness family appears best at locally.
It does not select a final health canon.

| Surface family | Best at locally | Narrower than siblings where | Unique dependency-readiness value preserved |
| --- | --- | --- | --- |
| Bridge-level readiness probe surfaces | Best at proving that the active bridge and top-level tool surface are reachable right now | They are weaker than subsystem tools, verification cards, and degraded registers at proving anything about deeper subsystem health | They preserve the freshest answer to whether AIM-OS is bridge-ready at all |
| Subsystem status-tool surfaces | Best at proving current subsystem initialization, counters, and internal readiness flags | They are weaker than package-side tests at local capability breadth and weaker than verification cards at bounded cross-surface method framing | They preserve the sharpest current distinction between bridge-ready and subsystem-ready |
| Bounded verification-card surfaces | Best at preserving disciplined bounded-live checks that tie package-side and tool-path evidence together | They are weaker than live status tools for freshness and weaker than degraded registers for long-lived failure-shape emphasis | They preserve the clearest dated record of what was actually exercised and classified in one verification pass |
| Degraded-feature register surfaces | Best at preserving what is weak, partial, degraded, empty, noisy, or unavailable | They are weaker than bridge probes at top-level readiness and weaker than tests at package capability breadth | They preserve the failure-shaped continuity that other readiness surfaces can underemphasize |
| Package-native smoke or test surfaces | Best at showing what a package can do locally apart from live runtime initialization | They are weaker than live probes and status tools at proving present host readiness | They preserve the package-capable side of readiness truth when runtime health is still partial or absent |

## Best-At Answer

- Bridge-level readiness probes are best at proving bridge-ready state.
- Subsystem status tools are best at proving subsystem-initialized or subsystem-uninitialized state.
- Bounded verification cards are best at proving bounded-live state.
- Degraded-feature registers are best at proving degraded or weak-runtime state.
- Package-native smoke or test surfaces are best at proving package-capable state.

## Local Constraint

No single dependency-readiness family stands alone as total truth on this host:

- bridge probes can be healthy while subsystem tools still fail,
- subsystem tools are narrow and do not expose every component,
- bounded cards are strong but dated,
- degraded registers preserve weakness but not total breadth,
- and package tests can prove local capability without proving live runtime health.
