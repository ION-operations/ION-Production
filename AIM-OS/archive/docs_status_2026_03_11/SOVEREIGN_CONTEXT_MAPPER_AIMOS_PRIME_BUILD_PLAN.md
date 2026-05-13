# Sovereign Context Mapper & AIM-OS Prime — Full Build Plan

**Status:** Architecture locked enough to build.  
**Execution order:** **Strike 2 → Strike 1 → Strike 3** (Wire first, Mapper second, Router third).  
**Canonical reference:** Use this document as the single source of truth for the Sovereign Context Mapper and AIM-OS Prime integration.  
**Canon tier alignment (2026-03-05):** Tier A live seam reference per `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`.  
**Last updated:** 2026-02-28  

---

## 1. Executive Decision

This system is split into **deterministic context construction**, **semantic/tool orchestration**, and **transport/injection**. Those responsibilities must remain separated.

### Canonical decisions

- **LLMs do reasoning, planning, mutation, and synthesis.**
- **LLMs do not perform deterministic parsing or contract extraction.**
- **Rust owns the Sovereign Context Mapper.**
- **The existing Python MCP daemon (`lucid_mcp_server.py`) remains the semantic/tool/memory plane.**
- **Tauri owns the local kernel role:** process supervision, command routing, webviews, local actuators, and injection.
- **The system is built inside-out:** prove the wire, then build the mapper, then route traffic, then integrate with the web UIs.

### Non-negotiable law

**Context must be shaped, not shoveled.**

The target file receives full implementation visibility. Dependencies receive only the minimum structural contracts required for correct reasoning and compilation.

---

## 2. Core Philosophy

### 2.1 Law of Asymmetric Visibility

When an AI agent modifies a file, the file being edited and the files it imports do **not** deserve the same visibility budget.

**Target file** — The agent requires:

- full implementation
- local logic
- comments
- private helpers
- local control flow
- exact code to mutate

**Dependencies** — The agent usually requires only:

- public structs and layouts
- public enums
- public traits
- public function signatures
- relevant type aliases / constants when they constrain usage
- semantically relevant attributes when they alter layout or callable surface

The system therefore supplies:

```text
Envelope = Full(Target File)
         + Contracts(Used Local Dependencies)
         + Optional(Callers of Exported Target Symbols)
         + Transitive Types(Only when exposed by used contracts)
         + Edit Guardrails
```

This is the **Active Context Envelope**.

### 2.2 Design goal

Reduce:

- context starvation
- attention dilution
- irrelevant token mass
- hallucinated dependency logic
- mutation drift

The objective is not merely token savings. The objective is **higher correctness density per token**.

---

## 3. Final System Architecture

### 3.1 Tier layout

**Tier 1 — Webview Reasoners**

- Web UIs inside Tauri (ChatGPT, Gemini, etc.).
- Responsibilities: planning, reasoning, code synthesis, emitting `[SYS: ...]` commands, consuming envelopes.
- They are **not** the source of parsing truth.

**Tier 2 — Tauri HAL / Local Kernel**

- Responsibilities: spawn and supervise local services, own webviews, intercept commands, route requests, run local actuators, inject context back into the DOM, provide local file/process/screenshot control.

**Tier 3A — Rust Sovereign Context Mapper**

- Responsibilities: read target source, resolve imports, track used symbols, extract public contracts, chase selective re-exports, build bounded envelopes, expose parse confidence.
- This is the **deterministic source-analysis plane**.

**Tier 3B — Python AIM-OS MCP Daemon**

- Existing `lucid_mcp_server.py`.
- Responsibilities: memory operations, RAG retrieval, timeline / semantic logging, existing MCP tools, higher-order orchestration support.
- This is the **semantic/tool plane**, not the parsing truth plane.

**Tier 4 — Policy / Routing Layer**

- May live inside Rust kernel logic and/or AIM-OS policies.
- Responsibilities: decide whether a request goes to local Rust actuator, Rust Context Mapper, or Python MCP daemon; apply safety and timeout policies; surface failures back to the agent cleanly.

---

## 4. Responsibility Boundaries

### 4.1 What Rust Context Mapper owns

- deterministic extraction
- import resolution
- used-symbol slicing
- contract generation
- parse confidence modes
- envelope packing and truncation policies
- direct serialization into the injection payload format

### 4.2 What the Python daemon owns

- existing tool calls
- memory storage / retrieval
- orchestration / semantic services
- future federated tool ecosystem via MCP

### 4.3 What Tauri owns

- process lifecycle
- state management
- routing of `[SYS: ...]` commands
- webview handling
- injection path
- local OS actions

### 4.4 What LLMs do **not** own

- AST parsing
- contract slicing
- dependency truth generation
- exact interface extraction
- transport integrity

---

## 5. Command Routing Model

Commands must be separated cleanly.

### 5.1 Rust local file/workspace commands

- `READ_FILE`, `LIST_DIR`, `RUN_COMMAND`, `SCREENSHOT`, `MOUSE_*`, `KEY_*`

### 5.2 Context Mapper commands

- `READ_ENVELOPE`, `READ_TARGET_WITH_CONTRACTS`, `LIST_LOCAL_IMPORTS`, `READ_SYMBOL_CONTEXT`

### 5.3 Python daemon commands

- `CALL_TOOL`, `STORE_MEMORY`, `RETRIEVE_MEMORY`, `RAG_QUERY`, timeline / semantic tool calls, any existing MCP tool in `lucid_mcp_server.py`

### 5.4 Principle

Do **not** blur raw file access with context-shaped access.

- `READ_FILE` → raw local file content
- `READ_ENVELOPE` → bounded, structured context artifact
- `CALL_TOOL` → semantic/tool plane request

---

## 6. Strike Sequence

### 6.1 Final order

**Strike 2 → Strike 1 → Strike 3 → UI integration / prompting**

Why:

- The wire is the highest-risk integration unknown.
- The Context Mapper is easier to build once process and IPC assumptions are proven.
- A router before both endpoints exist is abstraction tax.
- Prompt tuning comes last because the machine must exist before the prompts matter.

---

## 7. Strike 2 — The Wire (First)

Build a **standalone Rust CLI smoke test** before full Tauri integration.

### 7.1 Goal

Prove that Rust can maintain a stable JSON-RPC stdio conversation with `lucid_mcp_server.py`.

### 7.2 Required pass criteria

**Phase A (mandatory)**

- Spawn Python daemon successfully
- Send `initialize`
- Send `notifications/initialized`
- Send `tools/list`
- Receive and parse valid tool response

**Phase B (secondary)**

- Choose **one verified, safe, fast tool** from the actual returned list
- Execute `tools/call`
- Parse and print the result

Do **not** make an arbitrary `tools/call` part of the required green state unless the tool is confirmed real and safe.

### 7.3 Bridge requirements

The real bridge must support:

- persistent subprocess
- monotonic request IDs
- pending request map
- `oneshot` response routing
- timeout handling
- stdout protocol purity
- stderr logging only
- daemon death monitoring
- fail-all-pending-on-exit behavior
- configurable Python path
- explicit shutdown and restart policy

### 7.4 Standalone smoke-test scope

**Acceptable for smoke test:** child owned by watcher task; no restart policy yet; terminal logs only; no frontend state integration yet.

**Not acceptable for production:** losing child ownership permanently; no shutdown path; no restart supervision.

### 7.5 Likely failure modes to inspect first

- wrong `workspace_root`
- wrong `python_path`
- invalid `PYTHONPATH`
- daemon printing logs to stdout
- JSON-RPC shape mismatch
- wrong tool name or args
- startup timing longer than timeout

### 7.6 Deliverables

**Deliverable A1 — Standalone CLI bridge test**

A small Rust crate that: boots daemon, handshakes, lists tools, optionally calls one safe tool, exits cleanly.

**Deliverable A2 — Production bridge module**

`mcp_daemon_bridge.rs` for Tauri, with: retained child handle, watcher task, supervisor-friendly state, shutdown/restart hooks.

---

## 8. Strike 1 — Deterministic Context Mapper (Second)

Once the wire is proven, build the Rust Context Mapper as a separate subsystem.

### 8.1 Architectural rule

Do **not** replace "FSM religion" with "Tree-sitter religion."

Tree-sitter is an excellent **primary syntax extraction backend for v1**, but it is not a magical oracle. It does not automatically solve: `pub use` semantic resolution, cfg gates, macro expansion truth, transitive symbol provenance, external crate semantics, path aliasing.

Therefore the mapper must live behind an abstraction.

### 8.2 Parser abstraction

The mapper should expose a parser backend interface and explicit confidence modes.

**Suggested shape:**

```rust
pub enum ParseConfidence {
    High,
    Degraded,
    Fallback,
}

pub struct ExtractedFile {
    pub path: std::path::PathBuf,
    pub imports: Vec<String>,
    pub contracts: String,
    pub confidence: ParseConfidence,
}

pub trait ContractExtractor {
    fn extract_file(&self, path: &std::path::Path, source: &str) -> Result<ExtractedFile, String>;
}
```

Possible implementations: `TreeSitterExtractor`, `FastLexerExtractor`, `RegexSalvageExtractor`.

### 8.3 v1 backend recommendation

Use **Tree-sitter** as the primary backend for v1, behind the abstraction. Rationale: robust syntax structure, practical speed, incremental upgrade path, less brittle than a pure hand-rolled lexer/FSM for Rust source structure. But the system must **surface degradation honestly**.

### 8.4 Required parse modes

- **High** — Used when structured extraction succeeds and the symbol mapping confidence is strong.
- **Degraded** — Used when extraction is partial or some resolution is incomplete (e.g. unresolved re-export chain, unsupported syntax corner, partial AST query mismatch).
- **Fallback** — Used when the parser cannot provide confident structured extraction and a salvage strategy is used.

These modes must appear in the envelope so the agent knows how much to trust the extracted contracts.

### 8.5 Context Mapper modules

| Module | Responsibilities |
|--------|------------------|
| **extractor.rs** | Parse file syntax via backend; extract public declarations; preserve semantically relevant attributes; strip bodies from exported contracts. |
| **resolver.rs** | Map `use` statements to local files; follow `mod` pathing; resolve `pub use` re-exports where feasible; stop token explosion with explicit policies. |
| **symbol_usage.rs** | Identify actually used imported symbols in target; support tree-shaking of dependency contracts; optionally use efficient matcher strategies (e.g. Aho-Corasick). |
| **envelope.rs** | Own typed internal envelope structs; serialize final injection payload format; include parse warnings / confidence / rules. |
| **cache.rs** | Hold extracted artifacts; cache invalidation using more than bare `mtime` when practical; support warm repeated requests. |

### 8.6 Symbol-driven slicing

Do **not** dump a dependency's entire public API if the target uses only one or two symbols. The mapper should: inspect imported names; inspect explicit symbol usage; slice contracts to only the referenced surface; include transitive types only when required by those used contracts.

### 8.7 Re-export handling

A strict depth=1 policy is too blunt. **Final rule:** stay shallow by default; allow selective transitive expansion for symbols actually exposed by used contracts; chase simple `pub use` chains where necessary; surface warnings when resolution remains incomplete.

### 8.8 Fallback policy

Do **not** use "first 100 lines" as the canonical fallback. Preferred fallback order:

1. structured extraction
2. public declaration salvage
3. focused excerpt around public declarations
4. explicit parse warning in envelope

### 8.9 Comments and attributes policy

**Outbound contracts:** strip comments; preserve semantically relevant attributes where they matter to layout, ABI, or callable surface.

**Target file:** preserve comments and full implementation.

---

## 9. Envelope Design

### 9.1 Internal representation rule

Internally use typed Rust structs. Do **not** make XML or pseudo-XML the internal brain. The envelope string is the final serialized artifact, not the source of truth.

### 9.2 Suggested payload structure

```xml
<system_envelope version="1.0">
  <intent>Active Context Envelope for requested file.</intent>

  <edit_rules>
    - Modify only the target_file unless explicitly instructed.
    - Treat outbound_contracts as read-only.
    - Preserve public API compatibility unless the task requires otherwise.
    - If context appears incomplete, request additional envelope or directory info.
  </edit_rules>

  <parse_mode>High</parse_mode>

  <dependency_index>
    <dep path="src/webview_manager.rs" symbols="WebviewFleet,get_agent" />
  </dependency_index>

  <outbound_contracts>
    <!-- stripped comments, preserved critical attrs -->
  </outbound_contracts>

  <target_symbol_usage>
    WebviewFleet
    get_agent
  </target_symbol_usage>

  <target_file path="src/actuator/input.rs">
    <!-- full implementation -->
  </target_file>
</system_envelope>
```

### 9.3 Envelope rules

- target file remains full
- contracts are read-only surface
- contract comments are stripped unless absolutely required
- parse warnings must be explicit
- token budget truncation must be deterministic

### 9.4 Truncation priority

When envelope budget is exceeded, keep in this order:

1. full target file
2. directly used dependency contracts
3. transitive exposed types required by those contracts
4. required trait bounds or associated types
5. optional inbound callers of touched public API
6. everything else

---

## 10. Inbound Callers Policy

Do **not** always include inbound callers. Include them only when justified: editing a public API, changing exported signatures, refactoring a high fan-in symbol, behavior where caller constraints matter. Otherwise, they are just more token fog.

---

## 11. Caching Strategy

### 11.1 Bridge / daemon plane

The Python daemon is already persistent over stdio. Keep it hot.

### 11.2 Context Mapper plane

Cache extracted files and resolution results. Suggested cache identity: path, modified time, file size, lightweight content hash when practical. Do not rely purely on `mtime` if easy improvements are available.

---

## 12. Tauri Integration Plan

After the standalone bridge proof passes:

1. **Add production `mcp_daemon_bridge.rs`** — Managed state inside Tauri; retained child handle; shutdown on app close; restart policy or explicit crash propagation; structured log surfaces.
2. **Add `context_mapper` module** — Expose backend commands that the frontend/kernel can invoke for envelope generation.
3. **Add `sys_router.rs`** — Parse or route `[SYS: ...]` commands; dispatch to local Rust tools, Context Mapper, or Python daemon; normalize error payloads.
4. **Add frontend/webview bridge** — MutationObserver for streamed model output; detect system commands; forward commands to Rust; inject returned payloads back into the chat UI.

---

## 13. UI / Injection Layer

Build this **after** wire and mapper are proven.

### 13.1 Responsibilities

- detect `[SYS: ...]` commands emitted by the model
- send requests to Rust backend
- receive envelope or tool result payloads
- inject them into the LLM chat input

### 13.2 Injection principle

Use a synthetic interaction path that updates the framework's internal state, not just raw DOM field mutation. The injection layer is an **adapter**, not the sovereign core.

---

## 14. Testing Strategy

| Stage | Scope |
|-------|--------|
| **A — CLI wire proof** | Standalone Rust binary; no Tauri; no webviews; handshake + tools/list + one safe tool. |
| **B — Production bridge in Tauri** | Daemon lifecycle supervision; startup/shutdown behavior; timeout and error propagation. |
| **C — Context Mapper local tests** | Corpus of Rust files: normal structs/functions, multiline signatures, traits/impls, attrs, raw strings, comments with braces, `pub use` chains, cfg-gated items, macro-heavy files. |
| **D — Envelope quality tests** | Contracts pruned correctly; only used symbols included; parse mode correct; truncation order deterministic. |
| **E — Full webview integration** | Intercept streamed commands; inject payload back into target UI; verify end-to-end loop. |

---

## 15. Risk Register

### 15.1 Wire risks

- Python not installed / wrong executable; daemon crash on startup; stdout contamination; request ID mismatch; timeout under load; Windows process oddities.

### 15.2 Context Mapper risks

- unsupported Rust syntax corners; macro-generated APIs; incorrect re-export resolution; cfg-specific visibility confusion; token overexpansion from careless transitive traversal.

### 15.3 Router risks

- command namespace ambiguity; mixing raw file reads with envelope reads; retry storms on tool failure.

### 15.4 UI risks

- DOM changes in provider websites; synthetic event rejection; race conditions while models are streaming.

---

## 16. Production Hardening Checklist

**Python daemon bridge:** retain child handle; stdout protocol purity; stderr-only logs; fail-all-pending on exit; initialize + tools/list sanity probe; configurable Python path; shutdown and restart behavior; structured error types.

**Context Mapper:** parser abstraction boundary; explicit confidence modes; structured fallback chain; symbol-driven slicing; deterministic serialization; controlled transitive expansion.

**Router:** exact command ownership table; separate raw file reads from envelope generation; bounded retries; explicit error surface back to agent.

---

## 17. Phase Plan

| Phase | Goal | Deliverables |
|-------|------|--------------|
| **0 — Wire proof** | Prove JSON-RPC stdio bridge against real daemon. | Standalone Rust CLI bridge; terminal logs of initialize and tools/list; one safe tool call if convenient. |
| **1 — Production daemon bridge in Tauri** | Persistent managed service inside the app. | `mcp_daemon_bridge.rs`; supervisor behavior; managed state. |
| **2 — Context Mapper v1** | Deterministic envelope generation for local Rust files. | extractor/resolver/symbol_usage/envelope/cache; parse confidence surfaced; used-symbol slicing working. |
| **3 — Command router** | Route local, mapper, and daemon requests cleanly. | `sys_router.rs`; routing table; normalized error responses. |
| **4 — Webview integration** | End-to-end agent loop. | Command interception; payload injection; successful envelope consumption by web UI. |
| **5 — Quality expansion** | Deepen correctness and coverage. | More robust re-export resolution; better cfg awareness; multi-language adapters; richer truncation; observability. |

---

## 18. Immediate Next Actions

1. **Action 1** — Create the standalone Rust CLI smoke test for the daemon bridge.
2. **Action 2** — Run only `initialize` and `tools/list`; inspect real output before choosing a tool call.
3. **Action 3** — Choose one safe tool from the actual returned tool list and run a second pass.
4. **Action 4** — Once the wire is proven, start the Rust Context Mapper with: parser abstraction, Tree-sitter primary backend, explicit degradation modes.
5. **Action 5** — Only then build the command router and Tauri/webview injection path.

---

## 19. Final Canonical Statement

**AIM-OS Prime shall integrate the existing Python MCP daemon as a persistent stdio sidecar for semantic tools, memory, and orchestration, while a separate deterministic Rust Context Mapper serves as the authoritative source for token-aware file envelopes and local source analysis. Tauri shall supervise both transport and local actuation, route commands between them, and inject structured envelopes into web-based LLM interfaces. The build order is Wire first, Mapper second, Router third, UI integration fourth.**

---

## 20. Compact Build Motto

**Build the wire. Build the mapper. Route the traffic. Prompt last.**
