# Update Prompt (Curator / LLM)

You are performing a **revision** of an existing ATLAS package.

## Preconditions

- Read current `13_evidence_ledger.md`, `14_documented_vs_inferred.md`, and `sources.yaml`.  
- Do not silently downgrade tiers (DOCUMENTED → INFERRED) without a migration note in the ledger.

## Procedure

1. List incoming deltas (new docs, new releases, deprecated APIs).  
2. Map deltas to sections `00`–`10`.  
3. Insert ledger rows; bump `last_reviewed` in frontmatter.  
4. If scope changes, update `01_scope.md` **and** `00_identity.md` boundary bullets.  
5. Refresh `12_relation_map.md` narrative to match `relations.json`.  
6. Run mental checklist from `_meta/quality_bar.md`.

## Output

- **Change log** (bullet)  
- **Tier movements** (if any)  
- **Index/graph follow-ups**
