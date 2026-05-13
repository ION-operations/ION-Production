# Victus Evidence Graph Seed
## The Complete System Relationship Map

> **What this is**: The manually constructed seed of the AIM-OS evidence graph — every system-to-system dependency, data flow, and integration point we've discovered across all 4 codebases.
>
> **How to use it**: This is a living document. Every new discovery adds a node or edge. As we build Victus, this becomes the data backing the KnowledgeGraphPanel.

---

## 1. Node Registry (178 Nodes, 8 Categories)

### Category A: Core Intelligence Layer (26 nodes)

| ID | Node | Codebase | Lines | Description |
|----|------|----------|-------|-------------|
| A01 | CMC | AIM-OS-GIT + EF | 273+3000 | Bitemporal memory atoms with provenance (TT+VT) |
| A02 | CMC.Atoms | AIM-OS-GIT | — | Fundamental memory units: text/code/event/tool modalities |
| A03 | CMC.Molecules | AIM-OS-GIT | — | Composite structures, semantic grouping |
| A04 | CMC.Snapshots | AIM-OS-GIT | — | Immutable bundles, content addressing, rollback |
| A05 | CMC.WritePipeline | AIM-OS-GIT | — | Ingest→Atomize→Enrich→Index→Gate→Persist→Snapshot |
| A06 | CMC.ReadPipeline | AIM-OS-GIT | — | Query→HHNI Lookup→DVNS Optimize→Deduplicate→Budget Fit |
| A07 | HHNI | AIM-OS-GIT + EF | 405+5742 | 5-level fractal index: System→Section→Paragraph→Sentence→Subword |
| A08 | HHNI.DVNS | AIM-OS-GIT | 353 | Dynamic Vector Navigation: gravity/elastic/repulse/damping forces |
| A09 | HHNI.Retrieval | AIM-OS-GIT | — | Two-stage: coarse KNN → physics refinement, RS = QS·IDS·(1-DD) |
| A10 | HHNI.ConflictResolver | AIM-OS-GIT | — | Contradiction detection, stance clustering, suppression |
| A11 | VIF | AIM-OS-GIT + EF | 313+7392 | Witness envelopes, κ-gating, ECE calibration |
| A12 | VIF.WitnessEnvelope | both | — | Model ID, weights hash, prompt recording, tool tracking |
| A13 | VIF.KappaGate | both | — | Threshold, adaptive κ, HITL escalation |
| A14 | VIF.Replay | AIM-OS-GIT | — | Deterministic seeds, snapshot restore, verification |
| A15 | VIF.ProvenanceChain | AIM-OS-GIT | — | Lineage tracking, source attribution, derivation |
| A16 | SEG | AIM-OS-GIT + EF | 356+2602 | Shared evidence graph: nodes=claims, edges=supports/contradicts |
| A17 | SEG.Contradiction | both | — | Semantic analysis, logical conflicts, temporal conflicts |
| A18 | SEG.BiTemporal | AIM-OS-GIT | — | TT+VT, as-of queries, time-slicing |
| A19 | CAS | AIM-OS-GIT + EF | 206+3289 | Cognitive analysis: drift, attention, failure modes |
| A20 | CAS.Introspection | AIM-OS-GIT | — | Self-analysis, MCP integration |
| A21 | CAS.FailureModes | AIM-OS-GIT | — | Known failure patterns and detection |
| A22 | SDF-CVF | AIM-OS-GIT + EF | 185+5121 | Quartet parity (code/doc/test/trace), DORA metrics |
| A23 | SDF-CVF.QuartetParity | both | — | P ≥ 0.90 enforcement across all four artifacts |
| A24 | SDF-CVF.DORA | both | — | Deployment freq, lead time, change failure rate, MTTR |
| A25 | HolographicMemory | AIM-OS-GIT | 1594 | 10kD vector space: PLIx/Entity/Relationship/MemoryAtom vectorizers |
| A26 | ConsciousnessAnalyzer | AIM-OS-GIT | 2143 | MetricsCollector + PerformanceAnalyzer + HealthMonitor + OptimizationAdvisor |

### Category B: Execution Layer (18 nodes)

| ID | Node | Codebase | Lines | Description |
|----|------|----------|-------|-------------|
| B01 | APOE | AIM-OS-GIT | 12551 | Plan→Execute→Verify→Gate with 8 role agents |
| B02 | APOE.Roles | AIM-OS-GIT | — | Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness |
| B03 | APOE.DEPP | AIM-OS-GIT | — | Dynamic Emergent Prompt Pipeline: master chain as graph, self-rewrite |
| B04 | APOE.Executor | AIM-OS-GIT | 828 | PlanExecutor: VIF/HHNI/SEG/TCS integration, κ-gate, human escalation |
| B05 | AIKernel | EchoForge | 372 | AI inference: startRun→step→executeWithAI→reflect |
| B06 | OrchKernel | EchoForge | 459 | Base orchestration: plan→execute→verify, checkpointing |
| B07 | AIService | EchoForge | 167 | 4 Supabase edge functions: step/verify/journal/testgen |
| B08 | AIAgentSystem | EchoForge | 327 | 4 agent types: auditor/monitor/improver/stagnation |
| B09 | ContextManager | EchoForge | 334 | 3-tier: pinned→working→longTerm, token budgets, artifact registry |
| B10 | EventStore | EchoForge | 194 | Hash-chained append-only log, snapshot/replay |
| B11 | TaskQueue | EchoForge | — | Priority queue with dependencies |
| B12 | AutonomyGovernor | EchoForge | 309 | Budget (tokens/time/tools), risk policies, STOP, secrets redaction |
| B13 | DeepResearch | EchoForge | 114 | Streaming: decompose→research→cross-ref→synthesize |
| B14 | Journal | EchoForge | — | Structured execution journal |
| B15 | Verifier | EchoForge | — | Output verification engine |
| B16 | SafetyOrchestrator | AIM-OS-GIT | 566 | ManagerAI + LineRemovalDetector + ProtocolEducator |
| B17 | APOERunner | AIM-OS-GIT | 338 | CLI executor: loader, helpers, APOE plan runner |
| B18 | ContextBridge | Victus | 459 | 5-system aggregator: profiler→classifier→mapper→tracker→builder |

### Category C: Client Engines (26 nodes)

| ID | Node | Codebase | Description |
|----|------|----------|-------------|
| C01 | VictusIDE | EchoForge | Main IDE shell: Monaco + panels + drawers + activity bar |
| C02 | DeepResearchPanel | EchoForge | Streaming research UI (✅ integrated) |
| C03 | OrchestrationPanel | EchoForge | APOE plan viewer (✅ integrated) |
| C04 | TrustPanel | EchoForge | VIF κ-gate + witness display (✅ integrated) |
| C05 | KnowledgeGraphPanel | EchoForge | SEG evidence visualization (✅ integrated) |
| C06 | ConsciousnessPanel | EchoForge | CAS health monitor (✅ integrated) |
| C07 | SwarmPanel | EchoForge | Multi-agent swarm view |
| C08 | BudgetPanel | EchoForge | AutonomyGovernor dashboard |
| C09 | CognitionPanel | EchoForge | CAS detailed analysis |
| C10 | EvolutionPanel | EchoForge | Self-evolution tracking |
| C11 | PersonaControlPanel | EchoForge | AI behavior switching |
| C12 | RegressionDashboard | EchoForge | Test regression tracking |
| C13 | TestHarnessPanel | EchoForge | AI test execution |
| C14 | WarRoomPanel | EchoForge | Strategic command center |
| C15 | MissionBoardPanel | EchoForge | Mission kanban |
| C16 | MissionTimelinePanel | EchoForge | Live MCP event timeline |
| C17 | GenomeLabPanel | EchoForge | Agent genome editor |
| C18 | CrucibleSwarmPanel | EchoForge | Crucible execution view |
| C19 | ChatDrawer | EchoForge | AI chat (right drawer) |
| C20 | LiveFeedDrawer | EchoForge | Live event feed |
| C21 | RunHistoryDrawer | EchoForge | Execution history |
| C22 | VisualInspectorDrawer | EchoForge | Visual analysis |
| C23 | SurfaceEngine | JOC | WebGPU rendering: 8 materials, 4 shapes, CSS fallback |
| C24 | CommandPalette | JOC | Enhanced command palette |
| C25 | SystemAtlas | JOC | System topology visualization |
| C26 | GitSubwayMap | JOC | Subway-style git graph |

### Category D: Operations UI (26 nodes)

| ID | Node | Codebase | Lines | Description |
|----|------|----------|-------|-------------|
| D01 | DispatchPage | JOC | 652 | 5 strategies: single/scatter/cascade/consensus/debate |
| D02 | AgentBuilderPage | JOC | 777 | 6 sub-panels: BehavioralDNA/KnowledgeDNA/Metrics/Context/Lineage |
| D03 | ContextLabPage | JOC | 313 | Context capsule browser: fork/merge/generations |
| D04 | MCPDiagnosticsPage | JOC | — | MCP server health + tool testing |
| D05 | SessionPage | JOC | — | AI session management |
| D06 | SessionHealthPage | JOC | — | Session health monitoring |
| D07 | AgentCommsPage | JOC | — | Inter-agent communication |
| D08 | AgentWorkforcePage | JOC | — | Agent fleet overview |
| D09 | MissionBuilderPage | JOC | — | Mission planning + dispatch |
| D10 | CredentialVaultPage | JOC | — | API key / secrets management |
| D11 | InfraConsolePage | JOC | — | Infrastructure monitoring |
| D12 | CliTerminalPage | JOC | — | Terminal interface |
| D13 | OraclePage | JOC | — | Predictive analytics |
| D14 | StorageBrowserPage | JOC | — | File/storage explorer |
| D15 | AgentGenomeStore | JOC | 983 | V3 spec: BehavioralDNA, KnowledgeDNA, fission, tournaments |
| D16 | JocStore | JOC | 325 | Layout: drawers, tabs, sessions, missions |
| D17 | SessionStore | JOC | — | AI session lifecycle |
| D18 | VaultStore | JOC | — | Credential storage |
| D19 | PanelRegistry | JOC | — | Dynamic panel registration |
| D20 | NotificationStore | JOC | — | Toast/notification state |
| D21 | OracleStore | JOC | — | Predictive state |
| D22 | CalendarStore | JOC | — | Calendar state |
| D23 | ComputePage | JOC | — | GPU/compute resources |
| D24 | GpuMonitorPage | JOC | — | GPU utilization |
| D25 | DashboardPage | JOC | — | JOC overview |
| D26 | ActivityLogPage | JOC | — | Activity feed |

### Category E: Evolution Layer (14 nodes)

| ID | Node | Codebase | Description |
|----|------|----------|-------------|
| E01 | Forge | Victus | 11 AST mutation patterns + LLMForge |
| E02 | Arena | Victus | 5-dimension competition (CodeAnalyzer + Welch-t) |
| E03 | Swarm | Victus | 5-agent parallel orchestration |
| E04 | KGate | Victus | LLM-graded code quality gate |
| E05 | Pipeline | Victus | Full: forge→arena→promote cycle |
| E06 | ResourceBuilder | Victus | Codebase profiler + smell clusters |
| E07 | Auditor | Victus | Code health scoring |
| E08 | GenomeManager | Victus | Code genome tracking |
| E09 | CommsBus | Victus | Inter-module communications |
| E10 | OSLayer | Victus | OS abstraction |
| E11 | Server | Victus | FastAPI on port 5099 |
| E12 | DeepSearch | AIM-OS-GIT | Web crawler + trust scorer + master index |
| E13 | SCOR | AIM-OS-GIT | Red cell probes, adversarial testing |
| E14 | SafetySystems | AIM-OS-GIT | Safety orchestrator + line removal detection |

---

## 2. Edge Registry (85+ Directed Relationships)

### Legend
- `→feeds→` = data flows from source to target
- `→uses→` = source depends on target for functionality
- `→gates→` = source can block/approve target's actions
- `→monitors→` = source observes target's state
- `→bridges→` = source translates between two different systems
- `→evolves→` = source improves target over time
- `→witnesses→` = source creates trust records for target

### Core Intelligence Edges

```
A01 (CMC) →feeds→ A07 (HHNI)          # Memory atoms get fractal-indexed
A01 (CMC) →feeds→ A16 (SEG)           # Atoms stored as evidence nodes
A01 (CMC) →feeds→ A11 (VIF)           # Snapshots referenced in witnesses
A01 (CMC) →feeds→ A25 (HolographicMemory)  # Atoms vectorized to 10kD
A07 (HHNI) →uses→ A01 (CMC)           # Retrieval queries CMC for atoms
A07 (HHNI) →feeds→ A09 (HHNI.Retrieval)    # Index powers retrieval
A08 (HHNI.DVNS) →uses→ A07 (HHNI)    # Physics refines index positions
A11 (VIF) →gates→ B01 (APOE)          # κ-gate blocks low-confidence steps
A11 (VIF) →witnesses→ B05 (AIKernel)  # Every AI call gets a witness
A11 (VIF) →witnesses→ B07 (AIService) # Edge function calls get witnesses
A16 (SEG) →monitors→ A11 (VIF)        # Evidence graph tracks trust data
A16 (SEG) →feeds→ A10 (HHNI.ConflictResolver)  # Contradictions resolve via HHNI
A19 (CAS) →monitors→ B05 (AIKernel)   # Cognitive state of AI operations
A19 (CAS) →monitors→ B06 (OrchKernel) # Drift detection during orchestration
A22 (SDF-CVF) →gates→ E05 (Pipeline)  # Parity P≥0.90 blocks promotion
A22 (SDF-CVF) →monitors→ A01 (CMC)    # Tracks code/doc/test/trace evolution
A25 (HolographicMemory) →uses→ A01 (CMC)  # Vectorizes CMC atoms
A25 (HolographicMemory) →uses→ A16 (SEG)  # Vectorizes SEG entities
A26 (ConsciousnessAnalyzer) →monitors→ A19 (CAS)  # System-level health
```

### Execution Layer Edges

```
B01 (APOE) →uses→ A07 (HHNI)          # Retriever role queries HHNI
B01 (APOE) →uses→ A11 (VIF)           # Creates witnesses per step
B01 (APOE) →uses→ A16 (SEG)           # Records execution as evidence
B01 (APOE) →uses→ A01 (CMC)           # Context snapshots via CMC
B04 (APOE.Executor) →gates→ B02 (APOE.Roles)  # κ-gate per step execution
B05 (AIKernel) →uses→ B09 (ContextManager)     # Gets context for AI calls
B05 (AIKernel) →uses→ B10 (EventStore)         # Logs all events
B05 (AIKernel) →uses→ B12 (AutonomyGovernor)   # Budget enforcement
B06 (OrchKernel) →uses→ B05 (AIKernel)         # Delegates AI tasks
B06 (OrchKernel) →uses→ B11 (TaskQueue)        # Manages task priority
B07 (AIService) →bridges→ B05 (AIKernel)       # Edge function adapter
B08 (AIAgentSystem) →uses→ B05 (AIKernel)      # Agents call AI for work
B08 (AIAgentSystem) →monitors→ B10 (EventStore) # Monitors health via events
B09 (ContextManager) →uses→ A07 (HHNI)          # HHNI-powered retrieval
B09 (ContextManager) →feeds→ B05 (AIKernel)     # Provides context to AI
B10 (EventStore) →feeds→ A11 (VIF)              # Events verifiable via hash chain
B12 (AutonomyGovernor) →gates→ B05 (AIKernel)   # Can STOP any operation
B12 (AutonomyGovernor) →gates→ B08 (AIAgentSystem)  # Budget enforcement per agent
B13 (DeepResearch) →uses→ B07 (AIService)       # Research via edge functions
B15 (Verifier) →gates→ B05 (AIKernel)           # Output quality enforcement
B16 (SafetyOrchestrator) →gates→ E01 (Forge)    # Safe file modifications
B18 (ContextBridge) →uses→ A07 (HHNI)           # Context from HHNI
B18 (ContextBridge) →bridges→ E01 (Forge)       # Provides context to Forge
```

### Client ↔ Engine Edges

```
C01 (VictusIDE) →uses→ B05 (AIKernel)       # IDE drives AI operations
C02 (DeepResearchPanel) →uses→ B13 (DeepResearch)  # Panel → engine
C03 (OrchestrationPanel) →uses→ B01 (APOE)         # Displays APOE plans
C04 (TrustPanel) →uses→ A11 (VIF)                  # Displays κ-gate results
C05 (KnowledgeGraphPanel) →uses→ A16 (SEG)         # Displays evidence graph
C06 (ConsciousnessPanel) →uses→ A19 (CAS)          # Displays cognitive state
C07 (SwarmPanel) →uses→ E03 (Swarm)                # Displays swarm activity
C08 (BudgetPanel) →uses→ B12 (AutonomyGovernor)    # Displays budget state
C14 (WarRoomPanel) →uses→ D01 (DispatchPage)       # Strategic dispatch
C15 (MissionBoardPanel) →uses→ D16 (JocStore)      # Mission tracking
C17 (GenomeLabPanel) →uses→ D15 (AgentGenomeStore) # Genome editing
C23 (SurfaceEngine) →feeds→ C01 (VictusIDE)        # Visual identity layer
```

### Operations ↔ Execution Edges

```
D01 (DispatchPage) →uses→ B07 (AIService)          # Dispatch calls AI
D01 (DispatchPage) →uses→ D17 (SessionStore)        # Targets from sessions
D02 (AgentBuilderPage) →uses→ D15 (AgentGenomeStore)  # Creates genomes
D03 (ContextLabPage) →uses→ B09 (ContextManager)   # Manages capsules
D04 (MCPDiagnosticsPage) →monitors→ B07 (AIService)  # MCP health
D05 (SessionPage) →uses→ D17 (SessionStore)         # Session management
D10 (CredentialVaultPage) →uses→ D18 (VaultStore)   # API key management
D15 (AgentGenomeStore) →feeds→ B08 (AIAgentSystem)  # Genome → agent config
D19 (PanelRegistry) →feeds→ C01 (VictusIDE)         # Dynamic panel loading
```

### Evolution Layer Edges

```
E01 (Forge) →evolves→ any target code               # 11 AST mutation patterns
E02 (Arena) →gates→ E01 (Forge)                      # 5D competition selects winners
E03 (Swarm) →uses→ E01 (Forge)                       # 5 parallel agents forge solutions
E04 (KGate) →gates→ E05 (Pipeline)                   # Quality gate for promotion
E05 (Pipeline) →uses→ E01→E02→E04                    # Forge→Arena→Gate→Promote
E06 (ResourceBuilder) →feeds→ E01 (Forge)            # Smell clusters → mutation targets
E07 (Auditor) →feeds→ E06 (ResourceBuilder)          # Health scores → profiler
E08 (GenomeManager) →monitors→ E05 (Pipeline)        # Tracks evolution lineage
E11 (Server) →bridges→ C01 (VictusIDE)               # REST API: frontend↔backend
E12 (DeepSearch) →feeds→ B13 (DeepResearch)          # Backend for research
E13 (SCOR) →monitors→ B16 (SafetyOrchestrator)       # Red cell testing
```

---

## 3. Cold Principles (The Invariants)

These are the unbreakable laws governing the system:

| ID | Principle | System | Rule |
|----|-----------|--------|------|
| C-1 | Single Writer | CMC | Each atom has exactly one writer |
| C-2 | Immutability | CMC | Atoms never mutate — supersede only |
| C-7 | Time Ordering | CMC | Transaction time always moves forward |
| C-3 | Quartet Parity | SDF-CVF | P ≥ 0.90 across code/doc/test/trace |
| C-4 | Compile Don't Improvise | APOE | Intent→Plan→DAG, no ad-hoc execution |
| C-5 | Witness Everything | VIF | Every AI output gets a WitnessEnvelope |
| C-6 | κ Before Action | VIF | No execution below confidence threshold |
| C-8 | Bitemporal Truth | CMC+SEG | Both TT and VT preserved for all data |
| C-9 | Budget Before Autonomy | AutonomyGovernor | No operation without budget clearance |
| C-10 | Evidence Before Belief | SEG | Claims require evidence nodes |

---

## 4. Cross-Codebase Bridge Points

These are where systems from different codebases MUST connect:

| Bridge | From | To | Current Status | Integration Method |
|--------|------|-----|---------------|-------------------|
| **AI Inference** | EF `ai-service.ts` | Supabase edge functions | 🟡 Works via Supabase | Make backend-agnostic |
| **HHNI Retrieval** | Victus `context_bridge.py` | AIM-OS `hhni/` | 🔲 Not connected | REST API via Victus server |
| **VIF Trust** | EF `vif.ts` (client) | AIM-OS `vif/` (backend) | 🔲 Separate implementations | Sync via shared types |
| **CAS Cognition** | EF `cas.ts` (client) | AIM-OS `cas/` (backend) | 🔲 Separate implementations | Sync via shared types |
| **SEG Evidence** | EF `seg.ts` (client) | AIM-OS `seg/` (backend) | 🔲 Separate implementations | Sync via shared types |
| **CMC Memory** | EF `cmc.ts` (client) | AIM-OS CMC DB | 🔲 Not connected | REST API + DB sync |
| **Agent Genomes** | JOC `agentGenomeStore.ts` | Victus `genome_manager.py` | 🔲 Not connected | Shared genome schema |
| **Context Capsules** | JOC `ContextLabPage` | EF `context-manager.ts` | 🔲 Not connected | Shared capsule format |
| **Event Chain** | EF `event-store.ts` | AIM-OS CMC atoms | 🔲 Not connected | Events → CMC atoms pipeline |
| **Dispatch → BAS** | JOC `DispatchPage` | Browser Automation Service | 🟢 Working | Via BAS API |

---

## 5. Growth Zones (Where New Nodes Will Emerge)

These are areas where the graph will naturally expand as we build:

### Zone 1: Plugin System
```
New nodes: PluginRegistry, PluginSandbox, PluginAPI, ThemeEngine
New edges: PluginRegistry →feeds→ PanelRegistry
           PluginSandbox →gates→ PluginAPI (security)
```

### Zone 2: Collaboration
```
New nodes: WebSocketServer, CRDTEngine, PresenceService, CursorSync
New edges: CRDTEngine →feeds→ VictusIDE (multi-cursor)
           PresenceService →monitors→ all active users
```

### Zone 3: Deployment
```
New nodes: DeployService, VercelAdapter, DockerBuilder, CDNPush
New edges: Pipeline →evolves→ target code →triggers→ DeployService
           KGate →gates→ DeployService (quality before deploy)
```

### Zone 4: Data Capsule Sync (from other PC team)
```
New nodes: CapsuleSync, CapsuleFormat, CapsuleEncoder, CapsuleDecoder
New edges: CapsuleSync →bridges→ ContextManager (memory consistency)
           CapsuleFormat →uses→ CMC.Atoms (shared format)
```

---

## 6. MCP Memory Integration

### Stored Memories (Active)
- Session audit summary: 231 items, 4 codebases
- Architecture insight: triad architecture (EF/JOC/AIM-OS)
- 5 evolutionary branches mapped
- Prior session: 97 systems, 451K lines mapped
- Retrieval guide: 4 documentation locations
- Cold principles decoded
- aimos_systems dataset: 20 records in DB

### Memory Tools Available (106 total)
- `store_memory` / `retrieve_memory` — persistent knowledge
- `create_plan` — APOE plan creation
- `get_memory_stats` — memory system health

---

## 7. How This Graph Grows

1. **Every conversation** → new nodes discovered → add to registry
2. **Every integration** → new edges confirmed → add to edge registry
3. **Every test** → validates an edge → mark as `✅ CONFIRMED`
4. **Every contradiction** → SEG-style conflict node → track resolution
5. **Every new feature** → predict new growth zone → add to Zone section

> [!TIP]
> This document IS the evidence graph, stored as a human-readable artifact. When we build the SEG UI panel in Victus, this data becomes the initial seed — importable as SEG nodes and edges.

---

## 8. Category F: Adaptive Nervous System (18 nodes, from ops/relay)

| ID | Node | Lines | Description |
|----|------|-------|-------------|
| F01 | AdaptiveCore | ~300 | Universal pattern: Sensor→Tracker→Analyzer→Generator→Gatekeeper |
| F02 | AdaptiveDaemon | ~400 | Autonomous Sense-Decide-Act loop: schedule/event/incremental/dry-run |
| F03 | AdaptiveExecutor | ~350 | Proposal lifecycle: PENDING→APPROVED→EXECUTING→COMPLETED/FAILED/REJECTED |
| F04 | AdaptiveLearner | ~270 | Weight adjustment from proposal outcomes (effective/noise/false_positive) |
| F05 | AdaptiveRelay | 391 | Cross-machine MCP SSE relay: push/pull/sync/status |
| F06 | AdaptiveScanner | 415 | Codebase scanning engine for all sensors |
| F07 | AdaptiveCLI | ~200 | CLI interface: scan/assess/propose/execute/status/relay |
| F08 | Hooks | 246 | Git hooks integration for event-driven sensing |
| F09 | Sensor.ArchDrift | 310 | Architecture drift detection |
| F10 | Sensor.ContextDepth | 296 | Context coherence: KI staleness, capsule drift, memory bloat |
| F11 | Sensor.DocDepth | 257 | Documentation quality and completeness |
| F12 | Sensor.KnowledgeDecay | 268 | Knowledge staleness detection |
| F13 | Sensor.ResearchDepth | 234 | Research coverage and freshness |
| F14 | Sensor.SecurityPosture | 291 | Security posture monitoring |
| F15 | Sensor.TestCoverage | 288 | Test coverage gap detection |
| F16 | SensorsV5.Performance | 381 | File size, module lines, import depth regression |
| F17 | SensorsV5.Dependency | — | Dependency health (outdated, vulnerable, unused) |
| F18 | SensorsV5.Agent | — | Agent effectiveness (success rate, latency, drift) |

### Adaptive System Edges

```
F01 (AdaptiveCore) →feeds→ F02 (Daemon)           # Core pattern used by all
F02 (Daemon) →uses→ F06 (Scanner)                  # Scans codebase each cycle
F02 (Daemon) →uses→ F09–F18 (all sensors)          # Runs all sensors
F02 (Daemon) →feeds→ F03 (Executor)                # Proposals from analysis
F03 (Executor) →uses→ G04 (GenomeAssembler)        # Spawns agents to execute
F04 (Learner) →monitors→ F03 (Executor)            # Learns from outcomes
F05 (Relay) →bridges→ F02 (Daemon)                 # Cross-machine sync
F05 (Relay) →uses→ MCP SSE (port 5001)             # Communication transport
F08 (Hooks) →feeds→ F02 (Daemon)                   # Event-driven triggers
F09 (ArchDrift) →monitors→ A22 (SDF-CVF)           # Parity drift detection
F10 (ContextDepth) →monitors→ B09 (ContextManager) # Context coherence audit
F10 (ContextDepth) →monitors→ A01 (CMC)            # Memory bloat detection
F12 (KnowledgeDecay) →monitors→ A07 (HHNI)         # Knowledge freshness
F14 (SecurityPosture) →monitors→ B16 (SafetyOrch)  # Security posture
F15 (TestCoverage) →monitors→ A22 (SDF-CVF)        # Quartet parity test arm
F18 (SensorsV5.Agent) →monitors→ B08 (AIAgentSystem) # Agent health tracking
```

---

## 9. Category G: Comms & Capsule Infrastructure (8 nodes, from ops/relay)

| ID | Node | Description |
|----|------|-------------|
| G01 | CommsDoctrineProtocol | 7 agent inboxes, broadcast system, status files |
| G02 | CapsuleProtocolV1 | PRE/POST capsules: MISSION, NOW, MUST-NOT, EVIDENCE, BLOCKER, NEXT, HANDOFF |
| G03 | BroadcastSystem | 42+ broadcast files, agent-to-all messaging |
| G04 | GenomeAssembler | 3-layer: Universal Core + Platform Adapter + Model Affinity |
| G05 | AntigravityConsole | VS Code extension: MCP poller, Ghost bridge monitor, dashboard |
| G06 | GhostBridge | HTTP bridge at 192.168.2.25:9090 for cross-machine messaging |
| G07 | AgentIdentitySystem | Platform→agent mapping in AGENTS.md, callsign enforcement |
| G08 | ConsolidationFreeze | Decision freeze: no platform/arch/migration decisions until lifted |

### Comms & Capsule Edges

```
G01 (CommsProtocol) →feeds→ all agents             # Message routing
G02 (CapsuleV1) →feeds→ G01 (CommsProtocol)        # Capsules are comms
G02 (CapsuleV1) →monitors→ all agent sessions      # Drift detection
G04 (GenomeAssembler) →feeds→ D15 (AgentGenomeStore) # Generates genomes
G04 (GenomeAssembler) →feeds→ F03 (Executor)         # Spawns agents for proposals
G05 (AntigravityConsole) →monitors→ MCP (port 5001)  # Health polling
G05 (AntigravityConsole) →monitors→ G06 (GhostBridge) # Cross-machine health
G06 (GhostBridge) →bridges→ F05 (AdaptiveRelay)     # Network transport
G07 (AgentIdentitySystem) →gates→ all agents        # Identity enforcement
G08 (ConsolidationFreeze) →gates→ all decisions     # No decisions until lifted
```

---

## 10. Category H: AI Engine MCP (12 nodes, from scripts/ai_engine/)

| ID | Node | Lines | Description |
|----|------|-------|-------------|
| H01 | AIEngineMCP | 1520 | Slim zero-dep MCP server v2.3.0, 29 tools, lazy loading, stdio transport |
| H02 | AIEngine.Execute | — | Flagship: context→agent→genome→VIF gate→LLM→trace pipeline |
| H03 | AIEngine.Agents | — | 6 agents: coder_v1, architect_v1, auditor_v1, researcher_v1, tester_v1, fast_v1 |
| H04 | AIEngine.Loop | — | 3-phase loop with strategies: standard, deep_research, minimal, full_mcp |
| H05 | AIEngine.MetaAgent | — | Agent-to-agent via Gemini CLI subprocess |
| H06 | AIEngine.ContextLab | — | Tournament, evolve, compare strategies with leaderboard |
| H07 | AIEngine.ContextMapper | — | Sovereign Context Envelope: AST contracts, dependency sigs, edit guardrails |
| H08 | AIEngine.ContextConcierge | — | Natural language context discovery for any agent |
| H09 | AIEngine.LargeFileReader | — | MapReduce: chunking→summarization→hierarchical index |
| H10 | AIEngine.SystemRegistry | — | System registry query + crawl, writes SYSTEM_REGISTRY.md |
| H11 | AIEngine.Learning | — | Record outcomes, get insights, model performance tracking |
| H12 | AIEngine.SystemInfo | — | Task manager: CPU, RAM, GPU, disk, Python processes |

### AI Engine Edges

```
H01 (AIEngineMCP) →bridges→ Gemini CLI agents       # Dedicated MCP for Gemini
H02 (Execute) →uses→ A11 (VIF)                       # VIF gate in pipeline
H02 (Execute) →uses→ D15 (AgentGenomeStore)           # Genome loading
H02 (Execute) →uses→ B09 (ContextManager)             # Context packing
H03 (Agents) →uses→ H02 (Execute)                     # All agents route through pipeline
H04 (Loop) →uses→ H03 (Agents)                        # Loop runs agents
H05 (MetaAgent) →bridges→ Gemini CLI                  # Subprocess spawning
H06 (ContextLab) →evolves→ H04 (Loop)                 # Strategy evolution
H07 (ContextMapper) →feeds→ H02 (Execute)             # Structural context in
H08 (ContextConcierge) →uses→ H07 (ContextMapper)     # Discovery layer
H09 (LargeFileReader) →feeds→ H07 (ContextMapper)     # Large file processing
H10 (SystemRegistry) →monitors→ all systems           # System health
H11 (Learning) →monitors→ H03 (Agents)                # Agent performance
```

---

### Additional AIEngine Subsystems (from packages/)

| ID | Node | Package | Description |
|----|------|---------|-------------|
| H13 | SmartRouter | packages/router | Scout→Bandit→Rules ML pipeline for LLM routing |
| H14 | IntentClassifier | packages/intent_classification | Multi-axis ML intent classification |
| H15 | WorkDetector | packages/specialist_system | Chat-to-work conversion engine |
| H16 | ChainExecutor | packages/prompt_chain_executor | Multi-step workflows with quality gates |
| H17 | ThoughtArticulator | packages/meta_reasoning | Meta-cognitive reasoning traces |
| H18 | ContextEngine | scripts/ai_engine/context_engine.py | 640L: FileIndex + ContextWindow assembly, token budgets (4K-64K) |
| H19 | FileIndex | context_engine.py | Symbol extraction, content search, workspace scanning |
| H20 | DocsEngine | scripts/ai_engine/docs_engine.py | Documentation context support |

### Surface Engine Subsystem Details (from JOC)

| ID | Node | Lines | Description |
|----|------|-------|-------------|
| C27 | SurfaceEngineMaterials | 222 | 6 presets, MaterialCompiler enforcing 5 Laws, specular+cavity+cast |
| C28 | SurfaceEngineMotion | 323 | Spring physics, useSurfaceInteraction hook (hover/press/tilt/caustic) |
| C29 | SurfaceEngineWebGPU | 370 | WGSL SDF shaders, per-pixel lighting, Fresnel, cavity AO |
| C30 | SurfaceEngineCSS | 146 | CSS custom prop uniforms, progressive WebGPU→Paint→CSS fallback |

> **Updated Total: 178 nodes, 135+ edges across 8 categories**

---

## 11. Category I: AIM-OS Packages — Deep Systems (30 nodes)

### Consciousness Cluster

| ID | Node | Lines | Description |
|----|------|-------|-------------|
| I01 | ConsciousnessCreativityEngine | 1,112 | Creative reasoning, novel solution generation |
| I02 | ConsciousnessErrorLearning | 389 | Error pattern learning, failure-to-knowledge pipeline |
| I03 | ConsciousnessLearningEngine | 749 | Generalized learning from AI execution outcomes |
| I04 | ConsciousnessOptimizationDetector | 760 | Detects optimization opportunities in code/process |
| I05 | TemporalConsciousness | 959 | Time-aware cognition, temporal pattern recognition |

### Intelligence Cluster

| ID | Node | Lines | Description |
|----|------|-------|-------------|
| I06 | IntuitiveIntelligenceSystem | 5,448 | Emotional salience, intuitive reasoning engine |
| I07 | PLIx | 21,770 | Core intelligence indexing (largest single package) |
| I08 | IGODN | 2,480 | Intelligence graph and network system |
| I09 | QuaternionMath | 723 | Quaternion operations for multi-dimensional reasoning |
| I10 | QuaternionKernel | — | Kernel operations on quaternion space |
| I11 | NLTags | 3,652 | Natural language tag extraction and classification |
| I12 | ICIPSearch | 1,379 | Integrated contextual-intelligent pattern search |

### Context & Memory Cluster

| ID | Node | Lines | Description |
|----|------|-------|-------------|
| I13 | TimelineContextSystem | 44,506 | Timeline-based context system (largest by far) |
| I14 | ContextBootloader | 1,617 | Bootstrap context on session start |
| I15 | MCPDataIntegration | 7,929 | Cross-reference system, MCP data bridge |
| I16 | MCPDebuggingSystem | 1,155 | MCP diagnostic framework |
| I17 | MCPRagProxy | 3,562 | Consciousness-integrated RAG over MCP |

### Platform & Tools Cluster

| ID | Node | Lines | Description |
|----|------|-------|-------------|
| I18 | AdvancedMonacoEditor | 15,756 | Full Monaco editor package with extensions |
| I19 | BrowserAutomationService | 6,662 | BAS: browser automation for agent tasks |
| I20 | LucidOrchestrator | 15,057 | Lucid orchestration engine with user guide |
| I21 | LucidDocumentEditor | 5,842 | Document editing engine with launcher |
| I22 | LucidCoreConsole | 1,873 | Core console interface |
| I23 | IDEChatApp | 15,835 | IDE-integrated chat application |
| I24 | JarvisInjector | 3,421 | Window injection for JOC overlay |
| I25 | LuminSnapSystem | 1,952 | Screenshot/capture system |
| I26 | AIMOSMobileApp | 432 | Mobile companion app |
| I27 | AIMOSSDK | 1,091 | SDK for external integrations |
| I28 | LogSentinels | 1,833 | Log monitoring and anomaly detection |
| I29 | APIServiceRegistry | 2,133 | Service discovery and registration |
| I30 | OrchestrationBuilder | 1,420 | Orchestration plan builder |

### Category I Edges

```
I01 (Creativity) →feeds→ A19 (CAS)                   # Creative insights to cognition
I02 (ErrorLearning) →monitors→ B05 (AIKernel)         # Learns from AI errors
I03 (LearningEngine) →feeds→ H11 (AIEngine.Learning)  # Generalized learning
I04 (OptDetector) →feeds→ F16 (SensorsV5.Performance)  # Optimization signals
I05 (Temporal) →uses→ A01 (CMC)                        # Time-aware memory
I06 (Intuitive) →feeds→ A19 (CAS)                     # Emotional salience to CAS
I07 (PLIx) →feeds→ A07 (HHNI)                         # Core indexing to HHNI
I08 (IGODN) →uses→ A16 (SEG)                          # Graph operations on SEG
I13 (Timeline) →uses→ A01 (CMC)                        # Timeline context from CMC
I14 (Bootloader) →feeds→ B09 (ContextManager)         # Bootstrap context
I15 (MCPDataInteg) →bridges→ H01 (AIEngineMCP)        # Cross-reference bridge
I16 (MCPDebug) →monitors→ H01 (AIEngineMCP)           # MCP diagnostics
I17 (MCPRag) →uses→ A07 (HHNI)                        # RAG retrieval
I18 (MonacoEditor) →feeds→ C01 (VictusIDE)            # Editor integration
I19 (BAS) →uses→ B07 (AIService)                      # Browser automation
I20 (LucidOrch) →uses→ B01 (APOE)                     # Orchestration
I23 (IDEChat) →uses→ H02 (AIEngine.Execute)           # Chat pipeline
I24 (JarvisInject) →feeds→ D01 (DispatchPage)         # Window overlay
I28 (LogSentinels) →monitors→ all services            # Log anomalies
I29 (APIRegistry) →feeds→ H01 (AIEngineMCP)           # Service discovery
```

---

## 12. Category J: JOC Services & Additional Pages (18 nodes)

### JOC Services

| ID | Node | Description |
|----|------|-------------|
| J01 | APIGateway | Central API routing gateway for JOC |
| J02 | AutomationMacros | Macro system for repeat task automation |
| J03 | BASClient | Browser Automation Service client |
| J04 | GitHubContext | GitHub integration for repo/PR context |
| J05 | MCPClient | MCP client for JOC↔MCP communication |
| J06 | MissionOrchestrator | Mission lifecycle orchestration |
| J07 | RateLimiter | API rate limiting and throttling |
| J08 | SchedulerEngine | Task scheduling and cron-like execution |
| J09 | SessionPersist | Session persistence and recovery |
| J10 | VaultService | Credential encryption and vault operations |
| J11 | WindowInjectorClient | Window injection client for overlays |

### JOC Pages (Not Previously Cataloged)

| ID | Node | Description |
|----|------|-------------|
| J12 | AutoContextPage | Automatic context assembly UI |
| J13 | ContextGraphPage | Evidence graph visualization |
| J14 | ProjectCatalogPage | Multi-project catalog browser |
| J15 | SynthesizerPage | AI synthesis engine interface |
| J16 | WelcomePage | Onboarding and welcome flow |
| J17 | CalendarPage | Calendar and scheduling UI |
| J18 | SettingsPage | System configuration and preferences |

### Category J Edges

```
J01 (APIGateway) →bridges→ H01 (AIEngineMCP)          # Routes API calls
J01 (APIGateway) →uses→ J07 (RateLimiter)             # Rate limiting
J03 (BASClient) →uses→ I19 (BAS)                      # BAS integration
J04 (GitHubContext) →feeds→ B09 (ContextManager)      # Git context
J05 (MCPClient) →bridges→ MCP (port 5001)             # MCP transport
J06 (MissionOrchestrator) →uses→ B01 (APOE)           # Mission→APOE plans
J08 (SchedulerEngine) →uses→ F02 (AdaptiveDaemon)     # Scheduled tasks
J09 (SessionPersist) →feeds→ D17 (SessionStore)       # Session storage
J10 (VaultService) →feeds→ D18 (VaultStore)           # Credential store
J11 (WindowInjector) →uses→ I24 (JarvisInjector)      # Window overlay
J12 (AutoContext) →uses→ H18 (ContextEngine)          # Auto context
J13 (ContextGraph) →uses→ A16 (SEG)                   # Evidence graph
J14 (ProjectCatalog) →uses→ H10 (SystemRegistry)      # Project listing
J15 (Synthesizer) →uses→ H02 (AIEngine.Execute)       # AI synthesis
```

---

## 13. Remaining Package Inventory (Small/Utility)

| Package | Lines | Status | Notes |
|---------|-------|--------|-------|
| ai_collaboration | 318 | Utility | Multi-agent collaboration helpers |
| autonomous_protocol | 952 | Protocol | Autonomous execution protocol def |
| autonomous_research_dream | 2,134 | Research | Autonomous research engine |
| capability_awareness | 3,139 | Intelligence | System capability detection |
| doc_builder | 128 | Utility | Documentation generator |
| joc-tournament | 1,562 | Evolution | Agent tournament system |
| meta_optimizer | 233 | Utility | Meta-optimization helpers |
| prompt_chains | — | Execution | Pre-built prompt chain templates |
| schemas | 83 | Types | Shared type definitions |
| shared | — | Types | Shared utilities |
| sis | 832 | Intelligence | Strategic intelligence system |
| unified | 229 | Bridge | Unified interface layer |

---

> **FINAL TOTAL: 226 nodes, 170+ edges across 10 categories (A-J)**
>
> | Category | Nodes | Focus |
> |----------|-------|-------|
> | A: Core Intelligence | 26 | CMC, HHNI, VIF, SEG, CAS, SDF-CVF |
> | B: Execution | 18 | APOE, AI Kernel, Context Manager, Safety |
> | C: Client Engines | 30 | Panels, drawers, editors, surface engine |
> | D: Operations UI | 26 | Dispatch, Agent Builder, stores |
> | E: Evolution | 14 | Forge, Arena, Swarm, Pipeline |
> | F: Adaptive System | 18 | Sensors, Daemon, Executor, Relay |
> | G: Comms/Capsules | 8 | Protocol, broadcast, genome assembly |
> | H: AI Engine MCP | 20 | 29-tool server, agents, context mapper |
> | I: Deep Systems | 30 | Consciousness, intelligence, platform |
> | J: JOC Services | 18 | Services, gateway, new pages |
> | **Remaining** | **18** | Small/utility packages |
> | **TOTAL** | **226** | **170+ directed edges** |
