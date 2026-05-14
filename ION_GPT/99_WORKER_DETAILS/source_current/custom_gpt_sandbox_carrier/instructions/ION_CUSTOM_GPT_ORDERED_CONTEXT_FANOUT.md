# ION Custom GPT Ordered Context Fan-Out v4.4

## Purpose

Parallel fan-out must not destroy sequential meaning. Large sequential sources
split across branches require dense upstream batons and source-ordered fan-in.

## Core rule

Agent B working on section 2 must receive Agent A's baton from section 1 before
finalizing. Agent C must receive A and B batons before finalizing. Soft overlap
helps but is never sufficient.

## Baton content

Each `ion_context_baton` includes:

- dense section summary
- source anchors
- tags
- definitions
- entities
- claims
- dependency edges
- downstream alerts
- unresolved questions
- upstream reopen alerts
- confidence and limitations

## Fan-in

Fan-in settles by source order, not completion order. Later branches can reopen
earlier interpretation through `upstream_reopen_alerts`.
