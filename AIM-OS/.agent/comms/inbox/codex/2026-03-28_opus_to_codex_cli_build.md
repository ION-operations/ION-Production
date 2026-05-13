---
type: handoff
template: templates/actions/HANDOFF.md
created: 2026-03-28T16:42:47-04:00
from: OPUS
to: CODEX
priority: P0
status: PENDING
thread: phase-8-product-build
---

# [OPUS] → [CODEX] HANDOFF — Phase 8B: ION CLI Tool

**Date:** 2026-03-28T16:42:47-04:00
**Priority:** P0 — Director-approved build order #1
**Thread:** phase-8-product-build

---

## TASK: Build the `ion` CLI Tool

The Director (Braden) has approved the product build order. **CLI is first.** This is your primary mission — it unblocks automation for all agents and surfaces.

### What to Build

A Node.js CLI tool that wraps existing ION tools into a unified command interface:

```bash
ion init <CALLSIGN> <IDE>        # Bootstrap agent workspace (wraps ion-init.sh)
ion boot <CALLSIGN>              # Run /mini boot sequence for an agent
ion compile [--incremental]      # Run D38 compiler (wraps capsule-compiler.js)
ion status [<CALLSIGN>]          # Show agent state(s) from MINI.md/CAPSULE.md
ion signal <FROM> <TO> <TYPE>    # Send inter-agent signal (uses SIGNAL template)
ion handoff <FROM> <TO> "desc"   # Create handoff file (uses HANDOFF template)
ion audit <CALLSIGN>             # Run compliance audit (uses COMPLIANCE_AUDIT template)
ion serve [--port 5001]          # Start API server (Phase 8C, stub for now)
ion ls templates                 # List registered templates from _MASTER.md
ion ls agents                    # List agents from agents.md
```

### Architecture

```
tools/ion-cli/
├── package.json
├── bin/
│   └── ion.js                   # Entry point (#!/usr/bin/env node)
├── src/
│   ├── commands/
│   │   ├── init.js              # Wraps ion-init.sh
│   │   ├── boot.js              # Reads MINI, follows ROUTE, generates PRE
│   │   ├── compile.js           # Wraps capsule-compiler.js
│   │   ├── status.js            # Parses MINI/CAPSULE, displays state
│   │   ├── signal.js            # Creates .signal.md files per SIGNAL template
│   │   ├── handoff.js           # Creates handoff files per HANDOFF template
│   │   ├── audit.js             # Creates compliance audit files
│   │   ├── serve.js             # API server stub (Phase 8C)
│   │   └── ls.js                # List templates/agents
│   ├── config.js                # ION-BUILD root detection, agent discovery
│   └── utils.js                 # YAML parser, MINI parser, template loader
└── README.md
```

### Existing Code to Wrap
- `/home/sev/ION-BUILD/tools/ion-init.sh` — bootstrap script (working)
- `/home/sev/ION-BUILD/tools/capsule-compiler.js` — D38 compiler (working)
- `/home/sev/ION-BUILD/context/templates/` — all templates (for format generation)
- `/home/sev/ION-BUILD/agents/` — agent workspaces (for discovery)

### Key Design Decisions
1. **Node.js** — matches the existing compiler, no new runtime dependency
2. **commander.js** — standard CLI framework (`npx -y commander` or inline)
3. **ION-BUILD root detection** — walk up from CWD looking for `context/ION_MANIFEST.md`
4. **YAML frontmatter parsing** — reuse the compiler's YAML parser
5. **Template-governed output** — every `ion signal`, `ion handoff`, `ion audit` generates files that conform to the corresponding template

### Template Router
- **Action type:** CREATE
- **Depth class:** 2 — Multi-step/cross-artifact
- **Template:** CODE (infrastructure build)
- **Kernel gate:** §18 Bounded Execution — building within approved product plan

### Priority Note
Your previous HANDOFF (Phase 3 comms infrastructure) is still valid but now P2. Build the CLI first — the CLI itself will implement the signal/handoff/audit commands, which IS comms infrastructure. The two missions converge.

### Success Criteria
1. `ion compile` works and produces same output as direct `node tools/capsule-compiler.js`
2. `ion status` shows all agent states from their MINI files
3. `ion signal` creates properly formatted .signal.md files
4. `ion init` works (wrapping existing script)
5. `npm link` or `npx` installation works for global `ion` command

### FILES TO READ
- `/home/sev/ION-BUILD/tools/ion-init.sh` (existing bootstrap)
- `/home/sev/ION-BUILD/tools/capsule-compiler.js` (existing compiler)
- `/home/sev/ION-BUILD/context/templates/actions/SIGNAL.md` (signal format)
- `/home/sev/ION-BUILD/context/templates/actions/HANDOFF.md` (handoff format)
- `/home/sev/ION-BUILD/context/templates/actions/COMPLIANCE_AUDIT.md` (audit format)
- `/home/sev/ION-BUILD/context/13_cognitive/2026-03-28_product_roadmap.md` (full roadmap)
