---
atlas_package: system
system_slug: pl-i
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Process, memory, and namespace (semantic model)

## Activation and scope

**Block structure** implies nested **scopes** for identifiers; procedure activation frames support **recursion** in standard design summaries (`DOCUMENTED`, `src-wiki-pl-i-goals`).

## Storage classes (overview)

Summaries list **automatic**, **static**, **controlled**, **based** storage concepts — exact mapping to hardware stack/heap is **implementation-defined** (`DOCUMENTED` overview; **UNKNOWN** per platform without manual).

## “Namespace”

PL/I uses **identifier** resolution in nested blocks; **external** names link compilation units (`DOCUMENTED`, `src-wiki-pl-i-goals`). No URL-path style namespace — **not** analogous to OS mount namespaces.
