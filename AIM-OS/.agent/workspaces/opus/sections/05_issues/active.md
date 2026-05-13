# Active Issues

## ISS-001: Bootstrap Hang
- **Severity:** HIGH
- **Description:** `victus/ion/bootstrap.py` hangs on import due to singleton bridge import chain (`bridge.py`)
- **Impact:** Cannot run ION runtime programmatically
- **Status:** Known since Phase 0 audit, not yet fixed (Phase G4+)

## ISS-002: Missing data/ions/ Directory
- **Severity:** HIGH
- **Description:** `data/ions/` directory does not exist on disk. ION needs seed ions to boot.
- **Impact:** No ions available for index/graph/navigator to work with
- **Status:** Known since early audits, blocked until organization complete

## ISS-003: Legacy Enum References
- **Severity:** MEDIUM
- **Description:** ~20 files reference old enum values (pre-V5 naming)
- **Impact:** Import errors in affected modules
- **Status:** Catalogued in ION audit, fix planned for Phase 1

## ISS-004: MCP Monolith
- **Severity:** MEDIUM
- **Description:** `lucid_mcp_server.py` is 570KB — needs modularization
- **Impact:** Hard to maintain, slow to understand
- **Status:** Known, deferred past organization phase

## ISS-005: Project Fragmentation
- **Severity:** HIGH
- **Description:** 3 repos, 67+ top-level dirs, 27 redundant indexes, 14 partial audits
- **Impact:** No agent can orient quickly; context loss between sessions
- **Status:** THIS IS THE MISSION — being addressed by Grand Organization
