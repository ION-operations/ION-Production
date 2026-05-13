# AIMOS Corroboration-Traceability Surface Comparison - 2026-03-14

Work package: `CONSOLIDATION_WORK_PACKAGE_28_2026-03-14`

This comparison stays inside evidence only.
It does not choose a final continuity canon, rewrite trace surfaces, or assume that one corroboration cue alone proves total truth without sibling evidence.

| Surface family | Cross-surface binding strength | Temporal precision | Lane specificity | Continuity value | Operator readability | Machine-parseability | Collision or ambiguity tendency | Drift or trace-break tendency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Timestamp or date-stamp surfaces | Medium to high; they bind surfaces by time rather than by object identity | Highest; no sibling family is better at saying exactly when a cue appeared | Medium; timestamps alone rarely say which lane object they belong to | High; chronology is essential for reconstruction | High; dates and times are easy to scan | High when structured on the bus, medium in prose headers or filenames | High; one move often carries different valid date cues across files, headers, and messages | Medium; timestamps remain useful, but file-date and header-date drift can confuse "current" if read alone |
| Message and thread ID surfaces | Highest; they are the strongest direct bind between bus events and lane threads | High; message IDs embed time and the bus also supplies timestamps | Highest; thread names like `consolidation_wp27_2026_03_14` are tightly lane-specific | High; thread continuity links many related events | Medium; IDs are readable but not human-friendly | Highest; ID fields are structured and stable | Medium; one milestone can yield multiple message IDs across recipients, but thread ID keeps the family coherent | Low to medium; message/thread IDs stay strong as long as the bus and citations remain accessible |
| Artifact path citation surfaces | High; they bind claims to concrete files on disk | Low to medium; paths say where, not when | High; cited files usually encode the lane and packet family clearly | Highest; they are the strongest family for tracing narrative claims back to artifacts | High; paths are easy to inspect and open | High; path strings are parseable and exact | Medium; repeated long path lists can blur which citation matters most | Medium; a trace weakens if a path is omitted, renamed, or cited without date or ID support |
| Packet and entry numbering surfaces | Medium to high; they bind sequence position better than object identity | Medium; numbering implies order, not clock time | High; packet numbers, findings-board numbers, and entry numbers all sit inside the lane | High; sequence numbering is valuable for reconstruction | High; numbers are quick to scan | Medium to high; patterns are regular, but cross-family mapping is human work | Highest; several numbering systems coexist at once, so "current number" depends on which family is being read | Medium to high; numbering remains useful, but out-of-order insertion or parallel counters can complicate trace restoration |
| Atom and checkpoint ID surfaces | Highest; they are the strongest evidence that a durable write actually happened | Medium; IDs do not expose time as intuitively as timestamps or message IDs | High; atoms and checkpoint IDs are tied to specific lane writes | Medium to high; they preserve durability more than readable narrative continuity | Lowest; opaque identifiers are hard to scan mentally | Highest; ID fields are exact and structured | Medium; many atoms can accumulate around one move, and their role must be inferred from sibling text | Low to medium; if cited correctly they are strong, but if not carried forward the trace becomes opaque quickly |

## Direct Comparative Reading

- Timestamp or date-stamp surfaces are strongest when the question is "when did this happen relative to the other cues?"
- Message and thread ID surfaces are strongest when the question is "which live bus event and lane thread does this belong to?"
- Artifact path citation surfaces are strongest when the question is "which concrete file does this summary or claim point to?"
- Packet and entry numbering surfaces are strongest when the question is "where in the lane sequence does this move sit?"
- Atom and checkpoint ID surfaces are strongest when the question is "which durable write or checkpoint proves this step was persisted?"

## Visible Trace And Corroboration Contradictions

1. `.agent/comms/chat/codex/2026-03-13.md` and `.agent/comms/capsules/codex/2026-03-13.md` carry March 14 packet activity even though the filenames still point to 2026-03-13, so file-path dates and content dates diverge.
2. Status `Updated:` headers show 2026-03-13 15:50 UTC for `sev.status.md`, 2026-03-12 21:17 ET for `codex.status.md`, and 2026-03-04 12:30 for `antigravity.status.md`, while live bus messages `ai_msg_217_20260314_144349` and `ai_msg_218_20260314_144743` prove much fresher lane activity on 2026-03-14.
3. One lane step accumulates multiple corroboration cues at once: WP27 ties to message `ai_msg_214_20260314_143021`, thread `consolidation_wp27_2026_03_14`, checkpoint atom `b266d619-cbf1-4679-a999-8ea0963c81c9`, completion atom `bdd50001-8b39-4c8f-a071-0f00c0e984c1`, and message `atom_id` `b4704dc8-2fed-485e-8e22-5cc9979b14f9`.
4. Packet and entry numbering do not share one counter: WP28 follows WP27, Findings Board 26 synthesizes WP27, SEV chat opens WP28 in `Entry 025`, and CODEX chat closes WP27 in `Entry 036`.
5. Artifact path citations strongly prove which files are meant, but they do not by themselves prove whether the cited file is the freshest, current, or already superseded step in the lane.

## Evidence Boundaries

- Timestamp or date-stamp surfaces were treated as chronology anchors, not as sufficient object identity.
- Message and thread ID surfaces were treated as bus-event binders, not as complete artifact or memory proof by themselves.
- Artifact path citation surfaces were treated as filesystem grounding, not as freshness proof.
- Packet and entry numbering surfaces were treated as sequence cues, not as universal counters across all surface families.
- Atom and checkpoint ID surfaces were treated as durable-write receipts, not as human-complete explanations of the move they represent.
