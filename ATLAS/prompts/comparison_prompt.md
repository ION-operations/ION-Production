# Comparison Prompt (Curator / LLM)

You are writing or extending a file under `/ATLAS/comparative/`.

## Rules

- Structural comparison only: allocation models, trust boundaries, naming, IPC, packaging, reconciliation loops.  
- Every row in a comparison table cites which packages were used (`system_slug`) or mark **UNKNOWN** for a cell.  
- No “winner” language; use “tradeoff”, “constraint”, “deployment class”.  
- If evidence differs in tier across systems, footnote the weakest tier.

## Suggested outputs

- Dimension headers (e.g., “address space model”, “capability mechanism”, “desired-state store”).  
- Matrix with footnote markers to `claim_id` in respective packages where possible.  
- “Atlas pattern IDs” — short codes for recurring structures (optional, register in comparative doc).

## Forbidden

- Synthesizing a unified internal diagram for closed AI clouds.  
- Collapsing historical systems with modern descendants without a lineage section reference.
