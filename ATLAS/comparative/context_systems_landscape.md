# Comparative: Context systems landscape

**Atlas scope:** A **cross-lineage** map of how **context** is **selected**, **compiled**, **packaged**, **transported**, and **governed** for AI systems — spanning **public platforms**, **protocols**, and **AIM-OS-era** implementations. This is **not** ION doctrine; it is **field + lineage** vocabulary for roundtable and consolidation work.

**Evidence discipline:** Public specs (e.g. MCP) are **DOCUMENTED** at their normative URLs. AIM-OS paths and internal names are **OBSERVED** / **HISTORICAL** from the external AIM-OS tree unless you pin a specific commit. ION’s private/projection split is **ION doctrine** — see `ION/02_architecture/CONTINUITY_ARCHITECTURE.md` and agent `MINI.md` / projection `CAPSULE.md` (not repeated here as authority).

**AIM-OS evidence pin (2026-04-03):** Remote `https://github.com/sev-32/AIM-OS.git`, branch **`aimos-march-2026-update`**, commit **`a3b2ba14b8175a8d2bed2eda2fefd77ef96949d8`** (`git rev-parse HEAD` on the pinned checkout). For byte-identical audit of a path, use `git show a3b2ba14b8175a8d2bed2eda2fefd77ef96949d8:<path-in-repo>`. **Caveat:** The local tree at capture had **uncommitted changes** relative to that commit; the **References** paths below are normative **repo-relative** locations at the pin, not a guarantee the working copy on disk matched `HEAD` byte-for-byte.

---

## 1. Dimensions (how to compare “context systems”)

| Dimension | Question it answers | Examples of mechanisms |
|-----------|---------------------|-------------------------|
| **Selection** | What subset of the world enters the model? | Rules, globs, RAG top‑k, “relevant files”, memory retrieval |
| **Compilation** | How are raw artifacts turned into a **bounded package**? | Tiered context builds, summarization, capsule compilers |
| **Structure** | What **shape** does the bundle have? | Envelopes, JSON packets, markdown capsules, tool schemas |
| **Transport** | How does context cross a boundary? | IDE APIs, MCP, HTTP, zip handoffs, sync folders |
| **Persistence** | What survives a session? | Stores, journals, vectors, witness/evidence graphs |
| **Governance** | Who may write what, and under what proof? | Authority classes, audit ledgers, canon tiers, promotion gates |
| **Time** | How is drift handled? | Versioning, snapshots, “current truth” packs, rollback |

**Forbidden merge:** Treating **“big RAG pile”** as equivalent to a **governed context package** — retrieval without authority and envelope discipline is a different system class.

---

## 2. Public and industry-familiar systems

| Class | Representative surfaces | Role in the stack |
|-------|-------------------------|-------------------|
| **IDE rules + commands** | Cursor rules (`.mdc`), VS Code–family configs | Selection + policy injection at edit time |
| **Chat / agent products** | ChatGPT projects, Claude projects, Gemini Gems | Scoped instructions + attachments as **lightweight** context bundles |
| **Tool protocols** | `model-context-protocol` (ATLAS package) | **Transport + tool/schema** context, not full workspace doctrine |
| **IDE language + debug protocols** | `language-server-protocol`, `debug-adapter-protocol` | **LSP** = language intelligence; **DAP** = debug sessions — both JSON-RPC host↔server splits, **not** agent tool envelopes |
| **RAG stacks** | Vector DB + chunkers + rerankers | **Selection** from corpora; quality depends on indexing and eval |
| **Orchestration frameworks** | LangGraph-style DAGs, workflow engines | **Control flow** over multiple LLM/tool steps; context is often **implicit** in graph state |
| **Observability of prompts** | OpenTelemetry for AI (emerging), vendor logs | **Witness** for what was sent — not a context compiler by itself |

Use ATLAS packages where they exist (`grpc`, `opentelemetry`, `model-context-protocol`, `language-server-protocol`, `debug-adapter-protocol`, …) for **wire** and **platform** depth; this doc stays **conceptual**.

---

## 3. AIM-OS lineage: A–H protocol (workflow, not a wire format)

**OBSERVED** documentation in AIM-OS describes the **A–H protocol** as a **staged investigation / implementation methodology** applied to real work (e.g. Cursor rules & commands). Published letter-artifacts under `knowledge_architecture/ah_protocol/cursor_rules_commands_investigation/` include:

| Letter | Title (investigation packet) |
|--------|------------------------------|
| **A** | Intent capture |
| **B** | Hypothesis formation |
| **C** | Context mapping |
| **D** | Deep Expansion Layer (DEL) |
| **E** | CMM (context / coherence layer in that packet) |
| **F** | Confidence |
| **H** | Audit and memory |

**Note:** This folder set is **seven** named chapters (A–F plus H). Do not assume an eighth letter file exists without locating it; other AIM-OS trees may define **G** elsewhere.

A separate **implementation summary** (`plans/ah_protocol/AH_PROTOCOL_IMPLEMENTATION_SUMMARY.md`) describes **Python modules** under a daemon/RAG path for **intent → hypothesis → context mapping** steps with tests — that is **code-level** **OBSERVED** lineage, not a universal standard.

**ION mapping:** A–H is closest to a **forensic / governance pipeline** (compare ION templates: reconnaissance, evidence, audit). It is **orthogonal** to MCP: MCP moves **tool messages**; A–H structures **how humans and agents justify and record** a slice of work.

---

## 4. AIM-OS lineage: federated **context stacks** (DEC-007 + canon registry)

**OBSERVED** decision **DEC-007** (`docs/roundtable/decisions/DEC-007_CONTEXT_SYSTEM_CONSOLIDATION_PACKET_2026-03-05.md`) chooses **federation by lane** rather than a forced single mapper merge, with **promotion criteria** (shared envelope contract, dedupe, **JOC integration proof**, rollback).

The **Context System Canon Registry** (`docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`) assigns **tiers**:

| Tier | Role (summary) |
|------|----------------|
| **A** | Live seam — IDE Rust `context_mapper` / `context_service` |
| **B** | Staging — `context_capsule_wire_and_mapper_v1/*` |
| **S** | Support — `packages/context_bootloader/*` |
| **D** | Deferred — `packages/timeline_context_system/*` |
| **E** | Evidence-only snapshots — `docs/phase2b_context_packet/*` |

**Lesson for ION:** Tiering **canon vs experiment** is a reusable pattern for any multi-chat or multi-agent root: without it, “context system” becomes an unmergeable pile of partial implementations.

---

## 5. JOC (Job Operations Console) as a **consumer surface**

**OBSERVED** planning docs (`docs/JOC_MASTER_PLAN.md`, `docs/CANON_JOC_UI_ARCHITECTURE.md`, …) treat JOC as the **operator-facing** console with pages such as **Dispatch**, **Session**, **AutoContext**, **ContextGraph**, and integration with **BAS**, **Ghost / S2DB**, and **execution graph** concepts.

**Comparative placement:** JOC is primarily **UX + orchestration** over context-shaped **state** (sessions, dispatch strategies, graphs). DEC-007 explicitly demands **JOC/Dispatch/Session** consuming a **promoted** context path without ambiguous fallbacks — so JOC is a **forcing function** for envelope unification in that lineage.

---

## 6. Echo Forge cluster (organism loop + persistence lanes)

**OBSERVED** comparative evidence (e.g. `.agent/sev/reports/AIMOS_ECHO_FORGE_CLUSTER_BEST_AT_MAP_2026-03-14.md`) splits Echo Forge into:

| Surface | Best-at (summary) |
|---------|---------------------|
| **`echo-forge-loop/`** | Richest **operator** UI — mission control, many inspection panels |
| **`echo-forge-loop/server/`** | **Local** execution and streaming service (multi-endpoint) |
| **`echo-forge-loop/supabase/`** | **Hosted** persistence and edge functions for durable run artifacts |

**Comparative placement:** Echo Forge emphasizes **longitudinal** context: traces, atoms, witnesses, plans — a **memory/event** shape rather than a single “prompt prefix.” That sits beside RAG (corpus retrieval) and beside capsule zip packaging (handoff).

---

## 7. DAGs, prompt chains, and execution graphs

Several **distinct** “graph” ideas appear in the same ecosystem; **do not conflate**:

| Idea | What the graph is |
|------|-------------------|
| **JOC master plan mermaid** | Human roadmap / dependency of **features** |
| **Ghost Engine / execution graph runtime** | **Runtime** structure for tool pipelines (per JOC vision docs) |
| **Prompt chains / meta-orchestration** | **OBSERVED** in `knowledge_architecture` — chains of prompts/workflows (including references to A–H execution in executive summaries) |
| **LangGraph-style DAGs** | Industry pattern — explicit state machine for agents |

**ION mapping:** ION’s **execution / work-unit** schemas (when adopted) should state which graph class they encode — roadmap DAG vs runtime DAG vs prompt DAG.

---

## 8. AIM-OS memory reconciliation (“perfect” vs optimal vs DAG)

People often **merge memories** of **four different surfaces**. They are related but **not the same system**.

| If you remember… | Likely artifact | OBSERVED path (AIM-OS tree) |
|------------------|-----------------|----------------------------|
| **“Perfect” context** as a **documentation standard** | **Perfect Active / Timeline** standards — rigid templates for session working memory (“Perfect” = standard naming, not formal proof) | `knowledge_architecture/PERFECT_ACTIVE_CONTEXT_STANDARD.md`, `PERFECT_TIMELINE_CONTEXT_STANDARD.md`; tracking in `plans/EPIC_STANDARDS_TRACKING.md`, gates under `knowledge_architecture/validation/` |
| **“Optimal context”** as a **pipeline / mathy optimization** | **HHNI + DVNS** retrieval story — dedup, conflict handling, compression, token budget; docs describe a chain ending in **“Optimal Context”** | `knowledge_architecture/SAM/sources/MASTER_CMC_SYSTEM_MAP.md`, `docs/AIMOS_MAJOR_SYSTEMS.md`; HHNI system docs under `knowledge_architecture/systems/hhni/` |
| **DAG / graph / staged compilation** for coded projects | **JOC Context System** vision — **S0–S8** pipeline, **Context Web** (force-directed graph), **Context Mesh Maps** (NetworkX + contracts), **Sovereign Context Mapper** (deterministic Rust **envelopes**) | `packages/joc/plans/02-context-system-page.md`, `packages/joc/plans/09-context-node-graph-visualization.md`; mapper build narrative cited there (e.g. `SOVEREIGN_CONTEXT_MAPPER_BUILD_PLAN.md` in that plan’s table) |
| **Code ↔ docs must agree** | **SDF-CVF** quartet / **quintet** parity — consistency gates, not the same as HHNI retrieval | `knowledge_architecture/systems/sdfcvf/` |

**Forbidden merge:** Calling any one of the above **the** context system without naming which layer (template vs retrieval vs UI pipeline vs parity gate).

---

## 9. Open gaps (honest)

- **Single normative envelope** for AIM-OS context packets across Tier A/B — still a **promotion** problem per DEC-007, not solved in this file.
- **G** letter definition in A–H — not located in the same investigation folder as A–F and H; treat as **UNKNOWN** until cited.
- **Cross-root** context (ION + AIM-OS + IDE) — no single ATLAS **package** can own it; consolidation is **governance**, not scraping.

---

## 10. Suggested next artifacts (if you want this to become “merge-eligible”)

1. **One diagram** in ION: *context planes* (private MINI, projection CAPSULE, tool transport, long-term memory) with **forbidden merges**.  
2. **One ATLAS system package** later for a **specific** public context protocol (if not already covered).  
3. **Evidence pin (AIM-OS):** satisfied — see **AIM-OS evidence pin** under *Evidence discipline*; refresh the SHA when the branch moves and audits need a new baseline.

---

## References (external tree paths — OBSERVED)

- `/home/sev/AIM-OS/docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`  
- `/home/sev/AIM-OS/docs/roundtable/decisions/DEC-007_CONTEXT_SYSTEM_CONSOLIDATION_PACKET_2026-03-05.md`  
- `/home/sev/AIM-OS/knowledge_architecture/ah_protocol/cursor_rules_commands_investigation/*.md`  
- `/home/sev/AIM-OS/plans/ah_protocol/AH_PROTOCOL_IMPLEMENTATION_SUMMARY.md`  
- `/home/sev/AIM-OS/docs/JOC_MASTER_PLAN.md`  
- `/home/sev/AIM-OS/.agent/sev/reports/AIMOS_ECHO_FORGE_CLUSTER_BEST_AT_MAP_2026-03-14.md`  
- `/home/sev/AIM-OS/knowledge_architecture/PERFECT_ACTIVE_CONTEXT_STANDARD.md`  
- `/home/sev/AIM-OS/knowledge_architecture/PERFECT_TIMELINE_CONTEXT_STANDARD.md`  
- `/home/sev/AIM-OS/knowledge_architecture/SAM/sources/MASTER_CMC_SYSTEM_MAP.md`  
- `/home/sev/AIM-OS/packages/joc/plans/02-context-system-page.md`  

---

## Companion

- `comparative/ai_operating_system_reference_matrices.md` — trust, transport, mesh, CDN (lower-level **platform** context).  
- `systems/model-context-protocol/` — MCP as a **tool context** transport.  
- `systems/debug-adapter-protocol/` — DAP as **debug control** transport (orthogonal to MCP/LSP for “context package” questions).  
- `systems/elf/` — **object file container** (link/load) vs **ISA** vs **DWARF** — vocabulary for not merging “binary shape” with “debug encoding” or “machine code meaning.”  
- `systems/gnu-binutils/` — **toolchain** that produces/inspects ELF; still not the same as the **ELF spec** or **DWARF spec**.  
- `systems/glibc/` — **C**/**POSIX** **userland** **runtime** + **dynamic** **linker**; not **`linux-kernel`**, not **`gnu-gcc`**, not the **ELF** spec.  
- `systems/musl/` — **musl** **libc** vs **`glibc`** — **not** **drop-in** **ABI**; common in **minimal** **OCI** **bases**.  
- `systems/gnu-libstdcxx/` — **GNU** **C++** **stdlib** vs **`gnu-gcc`** vs **`glibc`**/**`musl`** — **not** the **compiler** or **C** **libc**.
- `systems/llvm-libcxx/` — **LLVM** **C++** **stdlib** vs **`clang`**/**`llvm-lld`** — **`competes_with`** **`gnu-libstdcxx`**; **not** the **compiler** or **linker** **packages** **alone**.
- `systems/llvm-libcxxabi/` — **C++** **ABI** **runtime** (**`cxx-abi-runtime`**) vs **`llvm-libcxx`** — **not** the **full** **stdlib** **surface**.  
- `systems/llvm-lld/` — LLVM **linker** only; competes with **GNU ld**, does not replace **as**/**readelf** by itself.  
- `systems/gnu-gdb/` — **CLI debugger** (DWARF-in-ELF); **not** **DAP** wire format; IDEs often **wrap** GDB behind **`debug-adapter-protocol`**.  
- `systems/lldb/` — LLVM **debugger** (**lldb-dap** / adapters); **`competes_with`** **`gnu-gdb`**; still **not** **Clang** or **DWARF** as specs.  
- ION `CONTINUITY_ARCHITECTURE.md` — **authority** of private vs projected context on the ION side.  
- ION `02_architecture/CONTEXT_PLANES.md` — **plane diagram** and **forbidden merges** for ION (private MINI/CAPSULE vs root projection vs MCP vs ATLAS).  
- `systems/systemd-portable/` — **systemd** **portable** OS-tree bundles (**`portablectl`**) vs **OCI** containers — vocabulary for not merging with **`docker`**.  
- `systems/systemd-sysext/` — **systemd** **system** **extensions** (**`sysext`**) **/** **`/usr`** **overlay** **merge** vs **`systemd-portable`** vs **containers**.  
- `systems/systemd-confext/` — **systemd** **configuration** **extensions** (**`confext`**) **/** **`/etc`** **overlay** **merge** vs **`systemd-sysext`**.  
- `systems/alpine-linux/` — **`linux-distribution`** **(musl** **+** **`apk`)** vs **`musl`** **/** **`linux-kernel`** **/** **`docker`** **base** **images**.  
- `systems/debian/` — **`linux-distribution`** **(glibc** **+** **`apt`** **+** **`systemd`)** vs **`glibc`** **/** **`systemd`** **/** **`alpine-linux`**.  
- `systems/oci-image-spec/` — **OCI Image Spec** vs **`docker`** (Moby engine) — format **law** separate from **runtime** implementation.  
- `systems/oci-distribution-spec/` — **registry pull/push HTTP API** vs **`oci-image-spec`** (what blobs *mean*) — transport vs layout.  
- `systems/oci-runtime-spec/` — **bundle + `config.json` + lifecycle** vs **`oci-image-spec`** / **`runc`** / **`crun`** (spec vs image vs **OCI** **implementations**).
