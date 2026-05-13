# Builds — Build & Deployment Documentation

> **Sources:** Root files (pyproject.toml, requirements.txt, Makefile, PACKAGE_MANIFEST.md)

## Current Build State

### What Runs
| Component | Status | Command |
|-----------|--------|---------|
| MCP Server | ✅ Works | `python lucid_mcp_server.py` (stdio) or port 5001 (HTTP) |
| JOC App | ✅ Works | `packages/joc/` — React/TypeScript on port 5011 |
| Echo-Forge | ⚠️ Unknown | `echo-forge-loop/` — currently empty |

### What Doesn't Run
| Component | Issue | Blocked By |
|-----------|-------|-----------|
| ION Runtime | ❌ Bootstrap hangs | Singleton bridge import chain |
| ION Tests | ❌ Collection errors | Legacy enum references |
| Full System | ❌ Not wired | AetherEngine → LLM adapter missing |

## Build Files
- [pyproject.toml](pyproject.toml) — Python project config
- [requirements.txt](requirements.txt) — Python dependencies
- [Makefile](Makefile) — Build commands
- [PACKAGE_MANIFEST.md](PACKAGE_MANIFEST.md) — Package manifest

## Provenance
Build files copied from project root on 2026-03-24.
