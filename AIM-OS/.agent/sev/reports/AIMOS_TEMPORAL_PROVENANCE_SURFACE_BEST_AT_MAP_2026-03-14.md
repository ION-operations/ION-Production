# AIMOS Temporal-Provenance Surface Best-At Map - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_20_2026-03-14`
Status: evidence-only temporal-provenance best-at map

## Best-At Answers

| Temporal-provenance family | What it appears best at locally | Where it seems narrower than siblings | What unique temporal-provenance value it preserves | Direct local reading |
| --- | --- | --- | --- | --- |
| VIF witness, calibration, and replay surfaces | Best at carrying operation-level provenance, confidence metadata, κ-gating state, and deterministic replay mechanics together | Narrower than bitemporal queries in explicit valid-time/transaction-time semantics, narrower than live signals in present-tense freshness, and narrower than timeline-context surfaces in broad multi-entry evolution modeling | Preserves the richest one-operation provenance envelope in the sampled family | VIF is the strongest answer to "how can one operation be witnessed, confidence-scored, and replayed?" |
| Temporal-graph or timeline-context surfaces | Best at carrying how context and operations evolve over time across timelines, graphs, and related history | Narrower than VIF in per-operation confidence detail, narrower than bitemporal queries in dual-time precision, and narrower than live signals in freshness | Preserves the strongest history-and-evolution view in the sampled family | Timeline-context surfaces are the strongest answer to "how did this work evolve across time and related entries?" |
| Bitemporal memory-query surfaces | Best at carrying exact "when was this true?" versus "when was this recorded?" semantics | Narrower than VIF in witness richness, narrower than trails in lightweight trace simplicity, and narrower than live signals in current-state freshness | Preserves the only explicit dual-time query model in the sampled set | Bitemporal queries are the strongest answer to "what was valid when, and what was merely recorded when?" |
| Agent trail surfaces | Best at preserving simple append-only operational traces with timestamp, agent, tool, and session context | Narrower than VIF in confidence and replay, narrower than timeline-context in modeled evolution, and narrower than live signals in freshness | Preserves the lightest-weight durable trace format in the family | Agent trails are the strongest answer to "what did this agent or tool call do in sequence?" |
| Live memory or timeline signal surfaces | Best at exposing the current host's temporal/provenance state immediately | Narrower than every file-based sibling in narrative interpretation, deterministic replay logic, and broad historical framing | Preserves the only direct now-state layer across memory and timeline in the sampled family | Live signals are the strongest answer to "what do the memory and timeline systems report right now?" |

## Net Local Answer

1. VIF surfaces are best at witnessed operation provenance.
2. Timeline-context surfaces are best at evolution history.
3. Bitemporal query surfaces are best at dual-time semantics.
4. Agent trails are best at lightweight sequential trace.
5. Live memory and timeline signals are best at freshness.
