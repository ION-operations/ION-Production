# Quality Bar

**Status:** DOCUMENTED

A package is **merge-eligible** when all mandatory gates pass.

## Mandatory gates

1. **Structure:** All required files exist; validators pass.  
2. **Identity clarity:** `00_identity.md` states what the package is and is not (especially for AI/cloud).  
3. **Evidence ledger coverage:** Every section in `02_architecture.md`–`10_observability.md` that contains factual claims has matching ledger rows or explicit UNKNOWN blocks.  
4. **Split file:** `14_documented_vs_inferred.md` contains no empty shell; open questions listed.  
5. **Relations:** `relations.json` includes at least one typed edge where a non-trivial relationship exists, or explicit note “no grounded cross-links yet”.  
6. **Sources:** `sources.yaml` lists every DOCUMENTED claim’s primary locator or states gap.  
7. **No fabrication:** No detailed internal topology for closed proprietary runtimes unless DOCUMENTED by operator primary sources.

## Grades (informational)

| Grade | Meaning |
|-------|---------|
| **A** | Broad DOCUMENTED coverage; graphs sync’d; comparative cross-links. |
| **B** | Core DOCUMENTED; clear UNKNOWN boundaries; minor ledger gaps tracked. |
| **C** | Scaffold with honest UNKNOWN; sources queued. |
| **D** | Incomplete structure or tier misuse — not merge-eligible. |

## Review checklist (curator)

- [ ] Marketing language scrubbed from architecture sections.  
- [ ] HISTORICAL vs current behavior separated.  
- [ ] Security claims avoid absolutes without citations.  
- [ ] AI sections distinguish product behavior vs API docs vs inference.
