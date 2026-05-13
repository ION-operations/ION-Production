# Phase 28: Production Extraction & Output Protocol

**Agent:** Opus
**Date:** 2026-03-09T13:25:00-04:00
**Phase/Task:** Phase 28 — Production Extraction + IDE Output Protocol
**Confidence:** 0.92

## Reasoning

### Production Extraction
- **Problem:** AIM-OS workspace is 20+ GB with massive noise (Tauri builds, .venv, backups)
- **Considered:** Manual copy, rsync with exclude, custom Python script
- **Chose:** Custom Python script with curated include lists from Phase 27 audit
- **Because:** The include list is more reliable than an exclude list — we know exactly what matters. Also reusable and trackable via git.
- **Risks:** May miss newly created directories not in the COPY_DIRS list → mitigated by keeping the script updated.

### IDE Output Protocol
- **Problem:** IDE agents (Cursor, Antigravity) produce ephemeral chat output that's lost between sessions. Full AIM-OS tracks everything via CMC/HHNI, but IDE emulation mode doesn't.
- **Considered:** MCP-only tracking, chat export, file-based output
- **Chose:** File-based output to `.agent/comms/output/` with structured sections
- **Because:** Files persist in git, are readable by other agents, and will integrate seamlessly with full AIM-OS when it runs in production mode.
- **Braden's insight:** This is a dogfooding gap — the architecture already handles full provenance, but the IDE bridge doesn't. The protocol bridges that gap.

## Work Done

1. **extract_production.py** (280 lines) — copies only production code to clean location
   - Curated include list: 68 packages, 27 engine modules, sentinel family, genomes, configs
   - Excludes: IDE/Tauri (5,610 files), .venv, node_modules, binary artifacts, backups
   - Result: 10,630 files, 169.2 MB → `AIM-OS-Production/`
   - Includes extraction manifest (JSON)

2. **protocol_ide_output.md** — genome protocol amendment
   - All substantive agent output → `.agent/comms/output/{agent}_{date}_{topic}.md`
   - Required sections: Reasoning, Work Done, Files Changed, Open Questions
   - Chat replies become brief summaries pointing to the file
   - Integrates with Context Trail (auto), Git (auto), CMC/HHNI (when full AIM-OS runs)

## Files Changed

| File | Action | Lines |
|------|--------|------:|
| scripts/ai_engine/extract_production.py | CREATED | 280 |
| .agent/genomes/protocol_ide_output.md | CREATED | 130 |
| AIM-OS-Production/ (entire directory) | CREATED | 10,630 files |

## Open Questions

1. Should `knowledge_architecture/` (5,740 files, 122 MB) be filtered further in extraction?
2. Should `ide_orchestration/` (1,458 files, 19 MB) be filtered further?
3. How do we ensure new agents read and follow the output protocol? (Genome loader injection?)
4. Next: Cross-reference dependency mapping in the Production directory
