# AIMOS Genome Cluster Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_08_2026-03-14`
Status: evidence-only comparative answer map

## Best-At Answers

| Family | What it appears best at locally | What it seems weaker at than siblings | Unique value it preserves | Direct evidence |
| --- | --- | --- | --- | --- |
| Flat single-file genomes | Best at fast, self-contained identity deployment and simple bootstrap loading | Weaker than per-agent directories at continuity depth and weaker than the layered family at clean cross-platform reuse | Preserves a direct one-file operational identity format that is easy to move, inspect, and hand to a host without extra assembly | Root flat files explicitly say "Load this at conversation start"; `21` root `*.genome.md` files exist; representative files like `codex.genome.md` and `sev.genome.md` combine role, authority, correction vectors, and project map in one place |
| Per-agent directory genome surfaces | Best at continuity-rich, agent-specific operation with adjacent context, instructions, and task-mode files | Weaker than flat files at immediate one-file portability and weaker than the layered family at clean shared abstraction across platforms/models | Preserves the richest living operational context in the genome cluster: README load orders, current priorities, north stars, task instructions, dynamics, maps, and drift materials colocated by agent | `codex/README.md` and `opus/README.md` define explicit load orders; `sev/`, `opus/`, `codex/`, and `composer/` directories contain `genome.md`, `README.md`, context files, instructions, and supporting surfaces |
| Layered core / adapter / affinity architecture | Best at explicit separation of identity, platform mechanics, and model tuning for structured porting and reuse | Weaker than flat files at instant one-document startup and weaker than per-agent directories at current live continuity integration | Preserves the clearest architectural discipline in the cluster by making porting rules explicit and reusable across agents | `GENOME_PROTOCOL.md` defines the three-layer formula; `PORTING_GUIDE.md` explains adapter/affinity creation; `cores/`, `platforms/`, and `affinities/` provide `5 + 4 + 4` concrete files implementing that model |

## Net Comparative Answer

1. Flat genomes are best at direct bootstrap portability.
2. Per-agent directory genomes are best at rich continuity and operational specificity.
3. The layered architecture is best at disciplined reuse and porting.

The local evidence says each family preserves a distinct strength. The layered family is visible and substantial, but this packet does not elevate it to silent canon.
