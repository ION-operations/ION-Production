# Mission Start: Sovereign Context Mapper & AIM-OS Prime

**Date:** 2026-02-28  
**Type:** Consolidation and alignment — full mission kickoff.  
**Canonical plan:** [SOVEREIGN_CONTEXT_MAPPER_AIMOS_PRIME_BUILD_PLAN.md](SOVEREIGN_CONTEXT_MAPPER_AIMOS_PRIME_BUILD_PLAN.md)  

---

## 1. Mission Summary

Today we formally start the **Sovereign Context Mapper & AIM-OS Prime** build. The architecture is locked; the execution order is **Strike 2 (Wire) → Strike 1 (Mapper) → Strike 3 (Router)**. This doc aligns the team and points to the single source of truth so everyone works from the same plan.

---

## 2. Team Roles & Responsibilities

| Role | Who | Responsibility |
|------|-----|----------------|
| **Lead visuals & hands-on** | Braden (user) | Visual design, UX, hands-on validation, sign-off, and product direction. |
| **Lead dev** | GPT 5.2 | Architecture decisions, design review, and technical direction for the Sovereign Context Mapper and AIM-OS Prime integration. |
| **Lead dev assistant** | Gemini 3.1 Pro (DeepThink) | Deep analysis, strategy, and alignment with the build plan; supports GPT 5.2 and the team. |
| **Composer agent (coding)** | Cursor Composer / Aether | Implements the plan in code: wire proof, bridge, Context Mapper, router, Tauri integration. Primary coding agent for this mission. |
| **Coding support** | Claude Opus 4.6 | Additional coding support as needed; works with Composer via the Antigravity IDE. |

**Principle:** One canonical plan, one build order. Composer codes; GPT 5.2 leads design; DeepThink supports strategy; Braden leads visuals and validation; Claude supports coding when needed.

---

## 3. Canonical Build Plan Reference

**Full build plan:** [docs/SOVEREIGN_CONTEXT_MAPPER_AIMOS_PRIME_BUILD_PLAN.md](SOVEREIGN_CONTEXT_MAPPER_AIMOS_PRIME_BUILD_PLAN.md)

Use it for:

- Executive decisions and responsibility boundaries (Rust vs Python vs Tauri vs LLMs).
- Law of Asymmetric Visibility and Active Context Envelope.
- Tier layout (Webview Reasoners, Tauri HAL, Rust Context Mapper, Python MCP daemon, Policy/Routing).
- Command routing (local Rust, Context Mapper, Python daemon).
- Strike sequence and phase plan (Wire → Mapper → Router → UI).
- Deliverables, testing strategy, risk register, and production hardening checklist.

**Build motto:** *Build the wire. Build the mapper. Route the traffic. Prompt last.*

---

## 4. Execution Order (Locked)

1. **Strike 2 — The Wire (first)**  
   Standalone Rust CLI smoke test: spawn `lucid_mcp_server.py`, handshake (`initialize`, `notifications/initialized`, `tools/list`), optionally one safe `tools/call`. Prove JSON-RPC stdio before any Tauri or mapper work.

2. **Strike 1 — Context Mapper (second)**  
   Rust Sovereign Context Mapper behind parser abstraction; Tree-sitter v1 backend; extractor, resolver, symbol_usage, envelope, cache; parse confidence (High/Degraded/Fallback); symbol-driven slicing.

3. **Strike 3 — Router & integration (third)**  
   Production `mcp_daemon_bridge.rs` in Tauri; `sys_router.rs`; command routing; then webview integration and injection.

4. **UI / prompting (fourth)**  
   After the machine exists: interception, injection, prompt tuning.

---

## 5. Immediate Next Actions (From Plan §18)

| # | Action | Owner |
|---|--------|--------|
| 1 | Create the standalone Rust CLI smoke test for the daemon bridge. | Composer (Cursor) |
| 2 | Run only `initialize` and `tools/list`; inspect real output before choosing a tool call. | Composer + Braden |
| 3 | Choose one safe tool from the actual returned tool list and run a second pass. | Composer |
| 4 | Once the wire is proven, start the Rust Context Mapper (parser abstraction, Tree-sitter, degradation modes). | Composer |
| 5 | Only then build the command router and Tauri/webview injection path. | Composer |

---

## 6. Key Documents for This Mission

| Document | Purpose |
|----------|---------|
| **SOVEREIGN_CONTEXT_MAPPER_AIMOS_PRIME_BUILD_PLAN.md** | Full build plan — canonical reference. |
| **REPLY_TO_DEEPTHINK_AIMOS_GRAND_CONVERGENCE.md** | Daemon stack answers (Python, launch, bundle options). |
| **DAEMON_STDIO_MCP_AND_CONTEXT_BUS_FINDINGS.md** | AIM-OS daemon/stdio/MCP index and context-bus mapping. |

---

## 7. Repos and Code Locations

- **AIM-OS (this repo):** Python MCP daemon (`lucid_mcp_server.py`), docs, build plan, mission alignment. Wire proof can live here as a small Rust crate or in a dedicated folder.
- **SAIOS / Tauri app (Application_Dev/IDE):** Tauri HAL, webviews, actuators, injection. Production bridge (`mcp_daemon_bridge.rs`), Context Mapper (if bundled with app), and `sys_router.rs` will live there once the wire is proven.

Where to implement the **standalone Rust CLI wire proof** (Action 1) is a team choice: e.g. `AIM-OS/tools/wire_proof/` or `Application_Dev/IDE/src-tauri/wire_proof/` or a small sibling repo. The plan only requires that it be a **standalone Rust binary** (no Tauri) that talks to `lucid_mcp_server.py` over stdio.

---

## 8. Alignment Checklist

- [ ] All agents and Braden have read or can access the **full build plan**.
- [ ] Execution order is agreed: **Strike 2 → Strike 1 → Strike 3**.
- [ ] Composer (Cursor) is designated primary coder for wire, mapper, router, and Tauri integration.
- [ ] Immediate Action 1 is clear: **standalone Rust CLI daemon bridge smoke test**.

---

*Mission start documented. Consolidate and align; then build the wire.*
