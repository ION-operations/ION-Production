# System Package Template (Curator Copy)

Copy the directory `/systems/_template/` to `/systems/<system-slug>/` and replace placeholders.  
Do not delete sections; mark **UNKNOWN** or **N/A** with rationale in `01_scope.md`.

## Frontmatter (every `00`–`14` markdown file)

```yaml
---
atlas_package: system
system_slug: <system-slug>
schema_version: "1.0"
last_reviewed: <YYYY-MM-DD>
evidence_grade: <A|B|C|D>
---
```

## Section prompts

### Why this system matters

Place in `00_identity.md` after the identity block: 3–6 bullets, DOCUMENTED/HISTORICAL only unless marked INFERRED.

### What this system teaches the atlas

Place at end of `00_identity.md`: pattern bullets useful for comparative modeling (may include INFERRED if labeled).

### Documented vs inferred

`14_documented_vs_inferred.md` must contain:

1. **DOCUMENTED claims** — bullet list with source IDs from `sources.yaml`.  
2. **INFERRED claims** — each with “why inferred” and confidence note.  
3. **OBSERVED** — protocol of observation.  
4. **Open questions** — explicit list.  
5. **Forbidden until sourced** — list of tempting but banned assertions.

### Placeholders (remove in real packages)

- `{{SYSTEM_NAME}}`  
- `{{PRIMARY_LOCATOR}}`  
- `{{CLAIM_ID_PREFIX}}`
