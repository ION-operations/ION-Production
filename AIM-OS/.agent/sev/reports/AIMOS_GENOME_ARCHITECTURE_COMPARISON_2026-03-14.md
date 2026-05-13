# AIMOS Genome Architecture Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_08_2026-03-14`
Status: evidence-only comparative analysis

## Comparative Table

| Comparison axis | Flat single-file genomes | Per-agent directory genome surfaces | Layered `core + adapter + affinity` architecture |
| --- | --- | --- | --- |
| Portability | Strongest at literal copy-and-load portability because one file can carry the whole identity package | Moderate portability because useful behavior depends on multiple colocated files | Strongest at designed portability across environments because identity, platform, and model tuning are intentionally separable |
| Agent-specific richness | Moderate to high within one document, but constrained by file size and mixed concerns | Strongest because the family can carry genome, north star, context, instructions, dynamics, and maps together | Moderate by default because the core is intentionally compressed and platform/model detail is split outward |
| Cross-platform reuse | Weakest, because platform reality is often embedded directly in the same file as identity | Moderate, because shared patterns exist but the directory structures are agent-specific and uneven | Strongest, because adapters and affinities are explicitly shared across agents |
| Drift resistance | Moderate at best; single-file simplicity helps, but mixed concerns make synchronized updates harder | Moderate; directories can isolate concerns, but uneven shape across agents creates room for divergence | Strongest in principle because identity, platform, and model tuning are separated by rule in `GENOME_PROTOCOL.md` |
| Onboarding / startup clarity | Strongest for immediate human loading: open one file and go | Strongest for continuity-rich onboarding once the README load order is followed | Clean conceptually, but weaker for instant startup because the loader must assemble three separate pieces correctly |
| Compatibility with current continuity surfaces | Moderate; flat files carry identity, but not the richest live context links | Strongest, because current context, instructions, user rules, drift logs, and north stars already live in these directories | Partial, because the layered family is present and specified, but most live continuity surfaces still sit outside the three-layer directories |

## Direct Comparative Reading

### Flat single-file genomes vs per-agent directories

- Flat genomes are simpler to load quickly.
- Per-agent directories are richer once continuity, context, and task modes matter.

### Flat single-file genomes vs layered architecture

- Flat genomes are easier for immediate deployment.
- The layered architecture is stronger for clean reuse across platforms and model families.

### Per-agent directories vs layered architecture

- Per-agent directories are stronger for present-day continuity because they already contain live context and instructions.
- The layered architecture is stronger for deliberate separation of identity, platform mechanics, and model tuning.

## Current Best Reading

1. The flat family optimizes for directness.
2. The per-agent directory family optimizes for continuity-rich local operation.
3. The layered family optimizes for systematic reuse and porting discipline.

These are different strengths, not a silent winner ladder.
