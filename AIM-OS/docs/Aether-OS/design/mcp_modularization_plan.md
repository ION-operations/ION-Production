# MCP Server Modularization Plan

## Problem
`lucid_mcp_server.py` is **11,138 lines** in one file with **93 tools** and **148 functions**. This makes it:
- Hard to maintain or debug
- Easy to break unrelated tools when editing
- Impossible for multiple agents to work on simultaneously

## Proposed Structure

```
mcp_server/
├── __init__.py         # Package init, SimpleMCPServer re-export
├── core.py             # Server class, run loop, dispatch (~700 lines)
├── tools_registry.py   # handle_tools_list — tool definitions (~1,700 lines → auto-generate)
├── tools/
│   ├── __init__.py
│   ├── memory.py       # store_memory, get_memory_stats, retrieve_memory (~650 lines)
│   ├── planning.py     # create_plan + helpers (~340 lines)
│   ├── confidence.py   # track_confidence (~180 lines)
│   ├── knowledge.py    # synthesize_knowledge (~260 lines)
│   ├── scor.py         # check_invariant, run_baseline_probe, detect_manipulation (~85 lines)
│   ├── snapshots.py    # create/restore/list/archive_snapshot (~200 lines)
│   ├── timeline.py     # add/get timeline entries (~240 lines)
│   ├── goals.py        # create/update/query goal timeline (~265 lines)
│   ├── intuition.py    # compute/update/get intuition (~210 lines)
│   ├── coagency.py     # signal_disagreement, trust_dashboard, escalation (~190 lines)
│   ├── datasets.py     # create/ingest/query/delete dataset + helpers (~400 lines)
│   ├── applications.py # create/deploy/manage application (~500 lines)
│   ├── autonomous.py   # 9 autonomous ops tools (~575 lines)
│   ├── ard.py          # conduct_recursive_analysis, dreams (~300 lines)
│   ├── cas.py          # run_cognitive_audit, analyze_thoughts, detect_drift (~400 lines)
│   ├── nltags.py       # 5 NL tag tools (~200 lines)
│   ├── cursor.py       # 5 cursor integration tools (~250 lines)
│   ├── cursor_commands.py  # 10 cursor command tools (~400 lines)
│   ├── collaboration.py    # 6 AI collaboration tools (~350 lines)
│   ├── prompt_chains.py    # 7 prompt chain tools (~400 lines)
│   ├── observability.py    # get_consciousness_metrics (~80 lines)
│   ├── api.py          # call_api, list_apis, api_status (~200 lines)
│   ├── specialist.py   # specialist system tools (~200 lines)
│   ├── math.py         # math tools (~150 lines)
│   └── deepsearch.py   # deepsearch tool (~60 lines)
└── utils.py            # Shared helpers (persistence, identity, etc.)
```

## Migration Strategy

> [!IMPORTANT]
> The `lucid_mcp_server.py` monolith stays **working** throughout. Each module is extracted one at a time, tested, then imported.

1. Create `mcp_server/` package alongside existing file
2. Extract one tool category at a time (start with smallest: `scor.py`)
3. Each extracted module exports a `register_tools(server)` function
4. `core.py` imports and calls each module's `register_tools`
5. After all modules extracted, `lucid_mcp_server.py` becomes a thin launcher

## Effort Estimate
- **Small modules** (scor, deepsearch, observability): ~30 min each
- **Medium modules** (memory, timeline, goals, confidence): ~1 hr each
- **Large modules** (applications, autonomous, cursor_commands): ~2 hrs each
- **Total estimated**: ~20 hours across sessions

## Verification
- Each module tested by running MCP server and calling its tools
- Full test: all 93 tools must still respond after modularization
