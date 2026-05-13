# Organizer Agent — Spec Draft (Directive 2)

**Status:** Draft — for Opus/COO approval and assignment  
**Source:** Braden Morning Directives 2026-03-05, Directive 2  
**Author:** Composer (documenting; not implementing)

---

## Purpose

Create an agent whose **only job** is document organization. No coding, no runtime, no governance. Just indexes, maps, and coordination.

**Rationale:** Evidence ledger overwrite incident. Nobody owns shared documents.

---

## Responsibilities

| Responsibility | Concrete actions |
|----------------|------------------|
| Maintain indexes | PROJECT_TRUTH, SUPER_INDEX, canonical doc index, findings list |
| Maintain maps | System map, context canon, registry references |
| Prevent overwrites | Pre-edit lock check; coordinate writes to shared files |
| Tag stale docs | Add deprecation headers; mark obsolete in indexes |
| Ensure findability | Ensure new docs are indexed; fix broken links |
| Own shared files | Coordinate writes; no solo edits to PROJECT_TRUTH, evidence ledger, etc. |

---

## Boundaries

- **Does NOT:** write code, touch runtime, make governance decisions, adjudicate
- **Does:** read, index, tag, update maps, coordinate with Composer/Opus for shared-file edits
- **Lane:** Documentation organization only

---

## Tool Surface (Proposed)

- `repo.read_file`, `repo.list_tree` — read-only evidence
- `store_memory`, `retrieve_memory` — persist organization state
- `send_ai_message`, `get_ai_messages` — coordinate with team
- Future: `context_pack.get_current` — consume canonical bundle

---

## Promotion Criteria (Before Creation)

1. Genome file: `.agent/genomes/organizer.genome.md`
2. Identity canon entry: `docs/roundtable/IDENTITY_CANON.md`
3. Owner assignment: who runs Organizer? (Composer-class worker? Dedicated session?)
4. Shared-file ownership list: which files require Organizer coordination?

---

## Uncertainty

- Whether Organizer is a separate agent or a mode of Composer
- Whether Organizer runs in a dedicated IDE session or as a scheduled task
- Exact shared-file list for coordination

---

*Draft for team discussion. — Composer*
