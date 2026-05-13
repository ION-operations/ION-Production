# Canon — Master Index

> **Purpose:** Single source of truth for all organized AIM-OS content.
> **Rule:** Nothing is deleted from originals. Everything here is copied and properly structured.
> **Maintainer:** OPUS (COO)
> **Created:** 2026-03-24
> **Total Files:** 123

---

## Population Status

| Section | Files | Status | Key Contents |
|---------|-------|--------|-------------|
| [constitution/](constitution/) | 5 | ✅ Complete | Supreme law: Constitution (39 articles), Kernel, Interface, Atlas |
| [doctrine/](doctrine/) | 17 | ✅ Complete | Architecture, orchestration, context, PROJECT_TRUTH (8 files) |
| [north_star/](north_star/) | 14 | ✅ Populated | AIM_OS_NORTH_STAR.md + goals. Awaiting v3 (Phase G4). |
| [systems/](systems/) | 8 | ✅ Populated | ION (5 docs), MCP (2 docs), system summaries (CMC/HHNI/SEG/VIF/APOE) |
| [agents/](agents/) | 35 | ✅ Complete | 28 genomes, bootloader, AGENTS.md, README |
| [apps/](apps/) | 1 | 📋 Summary | README with JOC, Echo-Forge, ION-UI summaries |
| [audits/](audits/) | 19 | ✅ Consolidated | From 3 source dirs (audit/ + audits/ + docs/) |
| [history/](history/) | 14 | ✅ Populated | Roundtable outputs + README summarizing 4 archive sources |
| [builds/](builds/) | 6 | ✅ Complete | pyproject, requirements, Makefile, manifest, victus summary |
| [bloat_registry/](bloat_registry/) | 1 | ✅ Documented | 53K files / 3GB identified as bloat |

## Root Files

| File | Purpose |
|------|---------|
| [INDEX.md](INDEX.md) | This file — master index |
| [PROVENANCE_LOG.md](PROVENANCE_LOG.md) | What came from where (123 entries) |
| [README.md](README.md) | Project README (from root) |

## Key Metrics

| Metric | Value |
|--------|-------|
| Canon files | 123 |
| Source directories surveyed | 67 |
| Directories classified CORE | 7 |
| Directories classified REORG | 21 |
| Directories classified ARCHIVE | 11 |
| Directories classified BLOAT | 16 |
| Total bloat identified | 53,000 files / 3GB |
| Active valuable content | ~11,000 files / 100MB |

## How to Use This Canon

1. **New agent boot:** Read `constitution/` → `doctrine/` → `agents/` → your genome
2. **Understanding a system:** Read `systems/README.md` → `systems/{system}/README.md`
3. **Finding what's built:** Read `builds/README.md`
4. **Understanding the mission:** Read `north_star/README.md` → `doctrine/MASTER_ORCHESTRATION.md`
5. **Finding audits:** Read `audits/README.md`
6. **What's dead:** Read `bloat_registry/INDEX.md`

## What's Next

- **Phase G4:** Write NORTH_STAR_V3.md with production ION/Aether plan
- **Phase G5:** Template the OPUS workspace for other agents
