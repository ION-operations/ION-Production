# Data, memory stores, and git

## `data/`

Copied as in AIM-OS-GIT at sync time. May include:

- `data/mcp/` — MCP-related persisted data
- `data/system_maps/` — generated or checked-in maps
- `data/databases/` — may be absent or smaller than on some FRESH snapshots

**Rule:** If a workflow depends on a large local DB that existed only on FRESH, restore it explicitly (see `06_SATELLITE_AND_FRESH.md`).

## `mcp_memory/`

Runtime memory index / tag files as in source. Copy is point-in-time.

## Root JSON

- `mcp_ai_messages.json` — collaboration messages (if present)
- `mcp_timeline_entries.json` — timeline entries (if present)

## `.git`

Full history copied from AIM-OS-GIT. **~915 MiB** typical — normal.

For exports **without** history, use `git archive` or a fresh clone with policy documented in `99_COPY_PROVENANCE.md` (future runs).
