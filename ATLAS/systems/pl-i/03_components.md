---
atlas_package: system
system_slug: pl-i
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Components (language facilities)

Summarized from **encyclopedic overview** + standard summaries (`DOCUMENTED`, `src-wiki-pl-i-summary`). **Not** a substitute for the full ANSI/ISO text.

## Structural

| Facility | Role |
|----------|------|
| `PROCEDURE` / `BEGIN` blocks | Procedure and block nesting |
| `DO` / `END` | Iteration and grouping |
| `ENTRY` | Alternate entry points (where supported) |

## Declarative

| Facility | Role |
|----------|------|
| `DECLARE` (`DCL`) | Names, attributes, type aggregation |
| `DEFAULT` | Default attributes for declarations |

## Control flow

| Facility | Role |
|----------|------|
| `IF` / `SELECT` / `GO TO` / `RETURN` | Branching and procedure exit |
| `CALL` | Procedure invocation |

## Storage management

| Facility | Role |
|----------|------|
| `ALLOCATE` / `FREE` | Heap-like controlled storage (model varies) |

## I/O

| Family | Role |
|--------|------|
| Stream | `GET`, `PUT` |
| Record | `READ`, `WRITE`, `REWRITE`, `LOCATE`, `DELETE` |

## Interrupt handling (standard summaries)

| Facility | Role |
|----------|------|
| `ON` / `SIGNAL` / `REVERT` | Exception / interrupt discipline |

## Preprocessor / multitasking

Preprocessing and multitasking features appear in **some** implementations but are **not** treated as universal in short standard summaries (`UNKNOWN` without edition-specific standard).
