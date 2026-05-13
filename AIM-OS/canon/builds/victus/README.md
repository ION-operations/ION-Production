# Operation Victus — Build Documentation

> **Source:** `/home/sev/operation-victus/` (17 dirs, 7,929 files, 19MB)
> **Branch:** `victus` (separate from AIM-OS-GIT)
> **Status:** Primary ION runtime implementation — partially functional

## What Victus Is
The standalone ION/Aether runtime implementation. Contains the actual Python code for the cognitive operating system: 103 Python modules in `victus/ion/`, plus the ION-UI system map visualization.

## Directory Structure

```
operation-victus/
├── victus/
│   └── ion/           ← 103 Python modules (THE runtime)
├── ion-ui/            ← System map visualization (HTML/JS)
├── data/              ← Runtime data (should contain ions)
├── tests/             ← Test suite
├── scripts/           ← Utility scripts
├── config/            ← Configuration
├── docs/              ← Documentation
└── server/            ← Server (AetherEngine)
```

## Key Findings from Audits
- **63 modules KEEP** — core runtime (63% of ion modules)
- **36 modules CUT** — legacy/dead code
- **Bootstrap hang** — singleton bridge import chain in bootstrap.py
- **Missing data/ions/** — no seed ions bootstrapped
- **20 legacy enum refs** — pre-V5 naming
- **Server not wired** — AetherEngine exists but LLM adapter missing

## Relationship to AIM-OS-GIT
Victus is the **runtime implementation** of what AIM-OS-GIT **documents and designs**. The `packages/` in AIM-OS-GIT contain the AIM-OS packages (CMC, HHNI, etc.) that ION should integrate with. Production ION/Aether will need these two repos to converge.
