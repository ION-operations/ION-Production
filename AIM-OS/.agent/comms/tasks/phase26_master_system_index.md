# Phase 26: Master System Index — Task Briefing

> **Assigned to:** Any available agent (Sev, Codex, Gemini)  
> **Priority:** CRITICAL  
> **Objective:** Build the authoritative hierarchical index of ALL AIM-OS systems

## What to Build

### 1. `scripts/ai_engine/system_registry.py`

```python
@dataclass
class SystemEntry:
    name: str           # e.g., "CMC", "ChainDirector", "ContextMapper"
    category: str       # Layer name
    purpose: str        # One-line description
    key_files: List[str]
    status: str         # active, building, planned
    exports: List[str]  # Key classes/functions
    lines: int
    dependencies: List[str]

class SystemRegistry:
    def crawl() -> List[SystemEntry]
    def categorize(entries) -> Dict[str, List[SystemEntry]]
    def generate_registry() -> str  # writes .agent/SYSTEM_REGISTRY.md
    def query(topic: str) -> List[SystemEntry]
    def diff_since(timestamp: float) -> List[str]
```

### 2. MCP Tools (add to `ai_engine_mcp_server.py`)
- `ai_engine_systems` — query registry by topic/layer
- `ai_engine_systems_crawl` — trigger full re-crawl

### 3. Output: `.agent/SYSTEM_REGISTRY.md`
Hierarchical index organized by layer with tables.

## Key Files to Leverage

| File | What It Does | How to Use |
|------|-------------|-----------|
| `atlas_agent.py` | Discovers 9 module groups | `Atlas.index()` → module list with files |
| `context_mapper.py` | Auto-indexes any file | `ContextMapper.build_index(path)` → sections, exports, concepts |
| `large_file_reader.py` | Handles >20K char files | `LargeFileReader.read_large(path)` → chunked index |

## Layer Categories

1. **Core Infrastructure** — CMC, HHNI, VIF, APOE, SEG, IIS, CAS, TCS, NL Tags
2. **AI Engine** — engine.py, chain_director, topologies, atlas, registry, sessions, router
3. **Context System** — context_mapper, context_concierge, context_engine, large_file_reader
4. **Agent System** — genome_loader, runtime, spawner, health, mesh, roundtable, enhanced_worker
5. **Documentation** — docs_engine, mission_self_audit, self_improve
6. **UI/JOC** — packages/joc/*
7. **MCP Servers** — ai_engine_mcp_server.py, lucid-mcp
8. **Agent Workforce** — 21 genomes in .agent/genomes/

## Coordination

Opus is building **Phase 25 (Agent Context Trail)** in parallel. The trail system will record the crawl operations, so both phases benefit from parallel development.

**Workspace:** `c:\Users\bombe\OneDrive\Desktop\AIM-OS`
