---
id: "router-sentinels-implementation-plan"
system: "router-sentinels-unified"
component: "implementation-planning"
level: "L2"
type: "implementation-plan"
title: "Router + Log-Sentinels Implementation Plan"
description: "Comprehensive implementation plan for Router and Log-Sentinels integration with AIM-OS"
audience: "developers, architects, project-managers"
confidence_threshold: 0.75
token_cost: 8000
word_count: 8000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["router", "log-sentinels", "implementation", "planning"]
dependencies: []
related_docs: []
version: "v1.0.0"
---

# Router + Log-Sentinels Implementation Plan

**Purpose:** Comprehensive implementation plan for integrating Router (APOE-MCP Router) and Log-Sentinels (Hybrid) systems with AIM-OS.

**Status:** Complete implementation plan with phased approach, dependencies, and timelines.

---

## 🎯 **IMPLEMENTATION OVERVIEW**

### **Goals**

1. **Router System:** Intelligent tool selection layer enhancing APOE with learned policy
2. **Log-Sentinels System:** Comprehensive log analysis with hybrid cloud/local processing
3. **Unified Integration:** Closed-loop learning system with complete observability

### **Success Criteria**

- ✅ Router successfully selects tools based on context
- ✅ Log-Sentinels analyzes logs and suggests tools
- ✅ Unified evidence chains in SEG
- ✅ Complete integration with AIM-OS systems
- ✅ IDE panels functional
- ✅ Performance meets targets (<200ms Router, <700ms Scout)

---

## 📅 **IMPLEMENTATION TIMELINE**

### **Phase 1: Foundation (Weeks 1-2)**
- Router core implementation
- Log-Sentinels core implementation
- Basic AIM-OS integration

### **Phase 2: Integration (Weeks 3-4)**
- Unified Router-Log-Sentinels integration
- SEG evidence chains
- VIF validation gates

### **Phase 3: Advanced Features (Weeks 5-6)**
- Learned policy (Bandit layer)
- IDE integration panels
- Telemetry dashboards

### **Phase 4: Optimization (Weeks 7-8)**
- Performance optimization
- Advanced learning
- Production hardening

**Total Duration:** 8 weeks

---

## 🏗️ **PHASE 1: FOUNDATION (Weeks 1-2)**

### **Week 1: Router Core**

#### **Day 1-2: Router Infrastructure**

**Tasks:**
1. Create Router project structure
   ```bash
   packages/router/
   ├── __init__.py
   ├── core/
   │   ├── router.py          # Main Router class
   │   ├── scout.py            # Scout LLM adapter
   │   ├── bandit.py           # Bandit scoring layer
   │   ├── rules.py            # Rules engine
   │   └── manifest.py         # Tool manifest system
   ├── integrations/
   │   ├── apoe.py             # APOE integration
   │   ├── vif.py              # VIF integration
   │   ├── seg.py              # SEG integration
   │   ├── cmc.py              # CMC integration
   │   ├── hhni.py             # HHNI integration
   │   └── tcs.py              # TCS integration
   ├── types/
   │   ├── router_context.py   # Router context types
   │   ├── tool_proposal.py    # Tool proposal types
   │   ├── tool_plan.py        # Tool call plan types
   │   └── snapshot.py         # Snapshot types
   └── tests/
       ├── test_router.py
       ├── test_scout.py
       ├── test_bandit.py
       └── test_integrations.py
   ```

2. Implement Router core types
   ```python
   # packages/router/types/router_context.py
   from dataclasses import dataclass
   from typing import Dict, List, Any, Optional
   
   @dataclass
   class RouterContext:
       goal: str
       task: str
       confidence: float
       files: List[str]
       errors: List[str]
       agent_intent: str
       budget: Dict[str, float]
   ```

3. Implement Snapshot builder
   ```python
   # packages/router/core/snapshot.py
   class SnapshotBuilder:
       async def build(self, ctx: RouterContext) -> Snapshot:
           # Pull from CMC, HHNI, VIF, SEG, TCS
           cmc = await self.cmc.getRecentDecisions()
           hhni = await self.hhni.retrieve(ctx.goal)
           vif = await self.vif.getStatus()
           seg = await self.seg.getEvidenceChains()
           tcs = await self.tcs.getCursor()
           return Snapshot(cmc, hhni, vif, seg, tcs)
   ```

**Deliverables:**
- ✅ Router project structure
- ✅ Core type definitions
- ✅ Snapshot builder implementation

**Dependencies:**
- AIM-OS systems (CMC, HHNI, VIF, SEG, TCS) must be accessible

---

#### **Day 3-4: Scout LLM Adapter**

**Tasks:**
1. Implement Cerebras Scout adapter
   ```python
   # packages/router/core/scout.py
   class ScoutLLM:
       def __init__(self, api_key: str):
           self.client = CerebrasClient(api_key)
       
       async def propose(
           self, 
           snapshot: Snapshot, 
           tool_manifest: ToolManifest
       ) -> List[ToolProposal]:
           prompt = self.buildPrompt(snapshot, tool_manifest)
           response = await self.client.generate(
               prompt=prompt,
               max_tokens=384,
               timeout_ms=700
           )
           return self.parseProposals(response)
   ```

2. Create prompt template
   ```python
   def buildPrompt(self, snapshot: Snapshot, manifest: ToolManifest) -> str:
       return f"""
       Goal: {snapshot.goal}
       Context: {snapshot.summary}
       Available Tools: {manifest.listTools()}
       
       Suggest top 5 tools with rationale.
       """
   ```

3. Implement proposal parser
   ```python
   def parseProposals(self, response: str) -> List[ToolProposal]:
       # Parse JSON response
       # Extract tool names, rationale, draft arguments
       return proposals
   ```

**Deliverables:**
- ✅ Scout LLM adapter
- ✅ Prompt template
- ✅ Proposal parser

**Dependencies:**
- Cerebras API access
- Tool manifest system

---

#### **Day 5: Bandit Scoring Layer**

**Tasks:**
1. Implement Bandit scorer
   ```python
   # packages/router/core/bandit.py
   class BanditScorer:
       def __init__(self, cmc_client, hhni_client):
           self.cmc = cmc_client
           self.hhni = hhni_client
           self.weights = {
               'context_fit': 0.3,
               'success_rate': 0.25,
               'precondition': 0.2,
               'info_gain': 0.15,
               'parallelizability': 0.1
           }
       
       async def score(
           self, 
           proposals: List[ToolProposal], 
           snapshot: Snapshot
       ) -> List[RankedTool]:
           scored = []
           for proposal in proposals:
               score = await self.computeScore(proposal, snapshot)
               scored.append(RankedTool(proposal, score))
           return sorted(scored, key=lambda x: x.score, reverse=True)
       
       async def computeScore(
           self, 
           proposal: ToolProposal, 
           snapshot: Snapshot
       ) -> float:
           fit = await self.contextFit(proposal, snapshot)
           success = await self.successRate(proposal.tool)
           precond = await self.preconditionSatisfaction(proposal)
           gain = await self.expectedInfoGain(proposal, snapshot)
           parallel = self.parallelizability(proposal.tool)
           
           return (
               self.weights['context_fit'] * fit +
               self.weights['success_rate'] * success +
               self.weights['precondition'] * precond +
               self.weights['info_gain'] * gain +
               self.weights['parallelizability'] * parallel
           )
   ```

2. Implement scoring components
   - ContextFit: Embedding similarity (HHNI)
   - SuccessRate: Historical success (CMC)
   - PreconditionSatisfaction: VIF checks
   - ExpectedInfoGain: Entropy reduction estimate
   - Parallelizability: Tool capability check

**Deliverables:**
- ✅ Bandit scorer implementation
- ✅ Scoring components

**Dependencies:**
- HHNI embeddings
- CMC history
- VIF validation

---

#### **Day 6-7: Rules Engine & Tool Manifest**

**Tasks:**
1. Implement Rules engine
   ```python
   # packages/router/core/rules.py
   class RulesEngine:
       def __init__(self, vif_client):
           self.vif = vif_client
       
       def validate(self, plan: ToolCallPlan) -> ValidationResult:
           # VIF gates
           # Budget checks
           # Rate limits
           # Depth limits
           # Risk gates
           return ValidationResult(passed=True, reasons=[])
   ```

2. Implement Tool Manifest system
   ```python
   # packages/router/core/manifest.py
   class ToolManifest:
       def __init__(self):
           self.tools: Dict[str, Tool] = {}
       
       def register(self, tool: Tool):
           self.tools[tool.name] = tool
       
       def getTool(self, name: str) -> Optional[Tool]:
           return self.tools.get(name)
       
       def listTools(self) -> List[Tool]:
           return list(self.tools.values())
   ```

3. Create Tool type definition
   ```python
   @dataclass
   class Tool:
       name: str
       version: str
       capability: List[str]
       inputs: Schema
       outputs: Schema
       preconditions: List[str]
       sideEffects: List[str]
       avgLatencyMs: float
       avgCost: float
       risk: str
       successRate: float
       examples: Optional[List[Dict]] = None
   ```

**Deliverables:**
- ✅ Rules engine
- ✅ Tool manifest system
- ✅ Tool type definitions

**Dependencies:**
- VIF client
- Tool registry

---

### **Week 2: Log-Sentinels Core**

#### **Day 8-9: Log-Sentinels Infrastructure**

**Tasks:**
1. Create Log-Sentinels project structure
   ```bash
   packages/log_sentinels/
   ├── __init__.py
   ├── core/
   │   ├── pipeline.py         # Main pipeline
   │   ├── collectors.py        # Log collectors
   │   ├── normalizer.py         # PII redaction
   │   ├── template_miner.py    # Drain3 miner
   │   ├── windower.py          # Rolling windows
   │   ├── scout.py             # Scout adapter
   │   ├── forensics.py         # Forensics adapter
   │   └── router_policy.py     # Escalation policy
   ├── integrations/
   │   ├── seg.py               # SEG integration
   │   ├── vif.py               # VIF integration
   │   ├── cmc.py               # CMC integration
   │   ├── tcs.py               # TCS integration
   │   └── router.py            # Router integration
   ├── types/
   │   ├── log_record.py        # Log record types
   │   ├── window.py            # Window types
   │   ├── scout_report.py      # Scout report types
   │   └── forensics_report.py # Forensics report types
   └── tests/
       ├── test_pipeline.py
       ├── test_collectors.py
       ├── test_normalizer.py
       └── test_integrations.py
   ```

2. Implement Log Record types
   ```python
   # packages/log_sentinels/types/log_record.py
   from dataclasses import dataclass
   from typing import Dict, Union
   
   @dataclass
   class LogRecord:
       ts: str
       source: str
       level: str  # debug, info, warn, error
       template: str
       vars: Dict[str, Union[str, int]]
       rawHash: str
   ```

3. Implement Window types
   ```python
   # packages/log_sentinels/types/window.py
   @dataclass
   class Window:
       id: str
       source: str
       from_time: int
       to_time: int
       size: int
       templates: Dict[str, int]
       sample: List[str]
   ```

**Deliverables:**
- ✅ Log-Sentinels project structure
- ✅ Core type definitions

**Dependencies:**
- None (new system)

---

#### **Day 10-11: Collectors & Normalizer**

**Tasks:**
1. Implement Log Collectors
   ```python
   # packages/log_sentinels/core/collectors.py
   class LogCollector:
       async def collect(self) -> List[LogRecord]:
           # Collect from browser console, terminal, backend API
           pass
   
   class BrowserConsoleCollector(LogCollector):
       async def collect(self) -> List[LogRecord]:
           # WebSocket connection to browser console
           pass
   
   class TerminalCollector(LogCollector):
       async def collect(self) -> List[LogRecord]:
           # File tail or process output
           pass
   
   class BackendAPICollector(LogCollector):
       async def collect(self) -> List[LogRecord]:
           # OpenTelemetry endpoint
           pass
   ```

2. Implement Normalizer (PII Redaction)
   ```python
   # packages/log_sentinels/core/normalizer.py
   class LogNormalizer:
       def __init__(self, config: RedactionConfig):
           self.patterns = config.patterns
       
       def normalize(self, record: LogRecord) -> LogRecord:
           # Redact PII/secrets before cloud calls
           redacted = record.raw
           for pattern in self.patterns:
               redacted = pattern.apply(redacted)
           return LogRecord(
               ts=record.ts,
               source=record.source,
               level=record.level,
               template=record.template,
               vars=record.vars,
               rawHash=hash(record.raw),  # Keep hash of raw
               raw=redacted  # Redacted version
           )
   ```

**Deliverables:**
- ✅ Log collectors
- ✅ PII redaction normalizer

**Dependencies:**
- WebSocket support (browser console)
- File system access (terminal)
- OpenTelemetry (backend API)

---

#### **Day 12-13: Template Miner & Windower**

**Tasks:**
1. Implement Template Miner (Drain3)
   ```python
   # packages/log_sentinels/core/template_miner.py
   from drain3 import TemplateMiner
   
   class LogTemplateMiner:
       def __init__(self, cache_size: int = 5000):
           self.miner = TemplateMiner()
           self.cache_size = cache_size
       
       def mine(self, records: List[LogRecord]) -> Dict[str, int]:
           templates = {}
           for record in records:
               template = self.miner.add_log_message(record.raw)
               templates[template] = templates.get(template, 0) + 1
           return templates
       
       def noveltyScore(self, window: Window) -> float:
           # Compare templates vs historical
           # Return novelty score (0-1)
           pass
   ```

2. Implement Windower
   ```python
   # packages/log_sentinels/core/windower.py
   class Windower:
       def __init__(self, roll_seconds: int = 60, min_records: int = 12):
           self.roll_seconds = roll_seconds
           self.min_records = min_records
       
       async def createWindow(
           self, 
           records: List[LogRecord]
       ) -> Optional[Window]:
           if len(records) < self.min_records:
               return None
           
           now = time.time()
           window_start = now - self.roll_seconds
           
           window_records = [
               r for r in records
               if window_start <= r.ts <= now
           ]
           
           if len(window_records) < self.min_records:
               return None
           
           return Window(
               id=str(uuid.uuid4()),
               source=window_records[0].source,
               from_time=window_start,
               to_time=now,
               size=len(window_records),
               templates={},  # Will be filled by miner
               sample=window_records[:10]  # Sample for Scout
           )
   ```

**Deliverables:**
- ✅ Template miner (Drain3)
- ✅ Windower implementation

**Dependencies:**
- Drain3 library
- Time utilities

---

#### **Day 14: Scout & Forensics Adapters**

**Tasks:**
1. Implement Scout adapter (Cerebras)
   ```python
   # packages/log_sentinels/core/scout.py
   class ScoutAdapter:
       def __init__(self, api_key: str):
           self.client = CerebrasClient(api_key)
       
       async def analyze(self, window: Window) -> ScoutReport:
           prompt = self.buildPrompt(window)
           response = await self.client.generate(
               prompt=prompt,
               max_tokens=384,
               timeout_ms=700
           )
           return self.parseReport(response, window.id)
   ```

2. Implement Forensics adapter (Local Ollama)
   ```python
   # packages/log_sentinels/core/forensics.py
   class ForensicsAdapter:
       def __init__(self, model: str = "llama3:8b-instruct-q4"):
           self.model = model
           self.ollama = OllamaClient()
       
       async def analyze(
           self, 
           window: Window, 
           context: Dict
       ) -> ForensicsReport:
           prompt = self.buildPrompt(window, context)
           response = await self.ollama.generate(
               model=self.model,
               prompt=prompt,
               max_tokens=2048,
               timeout_ms=8000
           )
           return self.parseReport(response, window.id)
   ```

**Deliverables:**
- ✅ Scout adapter (Cerebras)
- ✅ Forensics adapter (Ollama)

**Dependencies:**
- Cerebras API access
- Ollama local installation

---

## 🔗 **PHASE 2: INTEGRATION (Weeks 3-4)**

### **Week 3: AIM-OS Integration**

#### **Day 15-16: Router-AIM-OS Integration**

**Tasks:**
1. Implement Router-APOE integration
   ```python
   # packages/router/integrations/apoe.py
   class APOEIntegration:
       async def generatePlan(
           self, 
           toolPlan: ToolCallPlan
       ) -> ExecutionPlan:
           # Convert ToolCallPlan to APOE ExecutionPlan
           steps = []
           for step in toolPlan.steps:
               apoe_step = Step(
                   name=step.tool,
                   description=f"Execute {step.tool}",
                   role_name="Operator",
                   inputs=step.args
               )
               steps.append(apoe_step)
           return ExecutionPlan(steps=steps)
   ```

2. Implement Router-VIF integration
   ```python
   # packages/router/integrations/vif.py
   class VIFIntegration:
       async def preflight(
           self, 
           plan: ToolCallPlan
       ) -> VIFGate:
           # Run VIF checks before execution
           for step in plan.steps:
               if step.preflight:
                   result = await self.vif.validate(step)
                   if not result.passed:
                       return VIFGate(passed=False, reasons=result.reasons)
           return VIFGate(passed=True)
   ```

3. Implement Router-SEG integration
   ```python
   # packages/router/integrations/seg.py
   class SEGIntegration:
       async def recordDecision(
           self, 
           plan: ToolCallPlan
       ):
           # Record tool selection in SEG
           node = await self.seg.addNode({
               type: "tool_selection",
               source: plan,
               timestamp: now()
           })
           return node
   ```

**Deliverables:**
- ✅ Router-APOE integration
- ✅ Router-VIF integration
- ✅ Router-SEG integration

**Dependencies:**
- APOE system
- VIF system
- SEG system

---

#### **Day 17-18: Log-Sentinels-AIM-OS Integration**

**Tasks:**
1. Implement Log-Sentinels-SEG integration
   ```python
   # packages/log_sentinels/integrations/seg.py
   class SEGIntegration:
       async def recordReport(
           self, 
           report: Union[ScoutReport, ForensicsReport]
       ):
           # Record log analysis in SEG
           node = await self.seg.addNode({
               type: "log_analysis",
               source: report,
               timestamp: now()
           })
           return node
   ```

2. Implement Log-Sentinels-VIF integration
   ```python
   # packages/log_sentinels/integrations/vif.py
   class VIFIntegration:
       async def validateFix(
           self, 
           report: ForensicsReport
       ) -> VIFGate:
           # Validate fix suggestions
           if report.fixSuggestion:
               gate = await self.vif.validate(report.fixSuggestion)
               return gate
           return VIFGate(passed=True)
   ```

3. Implement Log-Sentinels-Router integration
   ```python
   # packages/log_sentinels/integrations/router.py
   class RouterIntegration:
       async def suggestTools(
           self, 
           report: Union[ScoutReport, ForensicsReport]
       ):
           # Feed tool suggestions to Router
           if report.suggestedTools:
               await self.router.receiveSuggestions(
                   report.suggestedTools,
                   context=report.summary
               )
   ```

**Deliverables:**
- ✅ Log-Sentinels-SEG integration
- ✅ Log-Sentinels-VIF integration
- ✅ Log-Sentinels-Router integration

**Dependencies:**
- SEG system
- VIF system
- Router system

---

### **Week 4: Unified Integration**

#### **Day 19-20: Unified Router-Log-Sentinels Service**

**Tasks:**
1. Implement Unified Service
   ```python
   # packages/unified/router_sentinels_service.py
   class UnifiedRouterSentinelsService:
       def __init__(self):
           self.router = Router()
           self.log_sentinels = LogSentinelsPipeline()
           self.apoe = APOEEngine()
       
       async def processLogsAndRoute(
           self, 
           logs: List[LogRecord]
       ) -> ExecutionResult:
           # 1. Log-Sentinels analyzes logs
           scout_report = await self.log_sentinels.scout(logs)
           
           # 2. Router receives tool suggestions
           router_context = RouterContext(
               goal=scout_report.summary,
               logInsights=scout_report,
               suggestedTools=scout_report.suggestedTools
           )
           
           # 3. Router selects best tools
           tool_plan = await self.router.decide(router_context)
           
           # 4. APOE executes tools
           execution_result = await self.apoe.execute(tool_plan)
           
           # 5. Log-Sentinels validates execution
           validation = await self.log_sentinels.validate(
               execution_result.logs
           )
           
           # 6. Update success rates
           await self.router.updateSuccessRate(
               tool_plan.tools, 
               validation.success
           )
           
           # 7. Record unified evidence chain
           await self.recordUnifiedEvidence({
               logAnalysis: scout_report,
               toolSelection: tool_plan,
               toolExecution: execution_result,
               validation: validation
           })
           
           return execution_result
   ```

2. Implement Unified Evidence Recording
   ```python
   async def recordUnifiedEvidence(
       self, 
       evidence: UnifiedEvidence
   ):
       # Record in SEG
       await mcp_lucid-mcp_synthesize_knowledge({
           topics: [f"unified_evidence_{evidence.logAnalysis.windowId}"],
           format: "structured"
       })
       
       # Store in CMC
       await mcp_lucid-mcp_store_memory({
           content: JSON.stringify(evidence),
           tags: {
               unified_evidence: 1.0,
               log_analysis: 1.0,
               tool_execution: 1.0
           }
       })
       
       # Record in TCS
       await mcp_lucid-mcp_add_timeline_entry({
           prompt_id: f"unified_{evidence.logAnalysis.windowId}",
           user_input: evidence.logAnalysis.summary,
           context_state: evidence
       })
   ```

**Deliverables:**
- ✅ Unified service implementation
- ✅ Unified evidence recording

**Dependencies:**
- Router system
- Log-Sentinels system
- APOE system
- AIM-OS systems (SEG, CMC, TCS)

---

## 🎨 **PHASE 3: ADVANCED FEATURES (Weeks 5-6)**

### **Week 5: Learned Policy & IDE Integration**

#### **Day 21-22: Learned Policy (Bandit Layer)**

**Tasks:**
1. Implement Bandit learning
   ```python
   # packages/router/core/bandit.py (enhanced)
   class BanditScorer:
       async def updateSuccessRate(
           self, 
           tool: str, 
           success: bool
       ):
           # Update success rate in CMC
           await self.cmc.updateToolStats(tool, success)
       
       async def learnFromOutcome(
           self, 
           proposal: ToolProposal, 
           outcome: ExecutionResult
       ):
           # Update weights based on outcome
           if outcome.success:
               # Increase weight for successful factors
               self.adjustWeights(proposal, outcome, positive=True)
           else:
               # Decrease weight for failed factors
               self.adjustWeights(proposal, outcome, positive=False)
   ```

2. Implement weight adjustment
   ```python
   def adjustWeights(
       self, 
       proposal: ToolProposal, 
       outcome: ExecutionResult, 
       positive: bool
   ):
       # Adjust weights based on outcome
       # Use gradient descent or similar
       pass
   ```

**Deliverables:**
- ✅ Bandit learning implementation
- ✅ Weight adjustment algorithm

**Dependencies:**
- CMC storage
- Execution results

---

#### **Day 23-25: IDE Integration Panels**

**Tasks:**
1. Implement Router Panel (Right Drawer)
   ```typescript
   // ide_orchestration/prototypes/dac/src/panels/RouterPanel.tsx
   export function RouterPanel() {
     const { tools, suggestions } = useRouter();
     
     return (
       <Panel title="Tool Selection">
         {tools.map(tool => (
           <ToolCard
             key={tool.name}
             tool={tool}
             probability={tool.probability}
             reason={tool.reason}
             preconditions={tool.preconditions}
           />
         ))}
       </Panel>
     );
   }
   ```

2. Implement Log-Sentinels Summaries Panel (Bottom Right)
   ```typescript
   // ide_orchestration/prototypes/dac/src/panels/LogSentinelsSummaries.tsx
   export function LogSentinelsSummaries() {
     const { scouts } = useLogSentinels();
     
     return (
       <Panel title="AI Summaries">
         {scouts.map(scout => (
           <ScoutCard
             key={scout.windowId}
             summary={scout.summary}
             confidence={scout.confidence}
             severity={scout.severity}
             suggestedTools={scout.suggestedTools}
           />
         ))}
       </Panel>
     );
   }
   ```

3. Implement Log-Sentinels Anomalies Panel (Bottom Left)
   ```typescript
   // ide_orchestration/prototypes/dac/src/panels/LogSentinelsAnomalies.tsx
   export function LogSentinelsAnomalies() {
     const { forensics } = useLogSentinels();
     
     return (
       <Panel title="Anomalies">
         {forensics.map(forensic => (
           <ForensicsCard
             key={forensic.windowId}
             rootCause={forensic.rootCause}
             fixSuggestion={forensic.fixSuggestion}
             evidence={forensic.evidence}
             gate={forensic.gate}
           />
         ))}
       </Panel>
     );
   }
   ```

**Deliverables:**
- ✅ Router panel
- ✅ Log-Sentinels Summaries panel
- ✅ Log-Sentinels Anomalies panel

**Dependencies:**
- IDE panel system
- React components
- Event streaming (SSE/WS)

---

### **Week 6: Telemetry & Monitoring**

#### **Day 26-28: Telemetry Dashboards**

**Tasks:**
1. Implement Tool Quality Dashboard
   ```typescript
   // ide_orchestration/prototypes/dac/src/panels/ToolQualityDashboard.tsx
   export function ToolQualityDashboard() {
     const { metrics } = useRouterTelemetry();
     
     return (
       <Panel title="Tool Quality">
         <MetricsGrid>
           <MetricCard
             label="Average Latency"
             value={metrics.avgLatency}
             trend={metrics.latencyTrend}
           />
           <MetricCard
             label="Success Rate"
             value={metrics.successRate}
             trend={metrics.successTrend}
           />
           <MetricCard
             label="Cost"
             value={metrics.avgCost}
             trend={metrics.costTrend}
           />
         </MetricsGrid>
         <ToolList tools={metrics.tools} />
       </Panel>
     );
   }
   ```

2. Implement Log Analysis Dashboard
   ```typescript
   // ide_orchestration/prototypes/dac/src/panels/LogAnalysisDashboard.tsx
   export function LogAnalysisDashboard() {
     const { stats } = useLogSentinelsTelemetry();
     
     return (
       <Panel title="Log Analysis">
         <StatsGrid>
           <StatCard label="Scout Calls" value={stats.scoutCalls} />
           <StatCard label="Forensics Calls" value={stats.forensicsCalls} />
           <StatCard label="Escalations" value={stats.escalations} />
           <StatCard label="Tool Suggestions" value={stats.toolSuggestions} />
         </StatsGrid>
         <TimelineChart data={stats.timeline} />
       </Panel>
     );
   }
   ```

**Deliverables:**
- ✅ Tool Quality Dashboard
- ✅ Log Analysis Dashboard

**Dependencies:**
- Telemetry data collection
- Chart libraries
- React components

---

## ⚡ **PHASE 4: OPTIMIZATION (Weeks 7-8)**

### **Week 7: Performance Optimization**

#### **Day 29-31: Caching & Latency Reduction**

**Tasks:**
1. Implement caching strategies
   ```python
   # packages/router/core/cache.py
   class RouterCache:
       def __init__(self):
           self.context_cache = {}
           self.tool_cache = {}
       
       async def getCachedProposals(
           self, 
           snapshot: Snapshot
       ) -> Optional[List[ToolProposal]]:
           cache_key = self.hashSnapshot(snapshot)
           return self.context_cache.get(cache_key)
       
       async def cacheProposals(
           self, 
           snapshot: Snapshot, 
           proposals: List[ToolProposal]
       ):
           cache_key = self.hashSnapshot(snapshot)
           self.context_cache[cache_key] = proposals
   ```

2. Optimize Scout calls
   - Batch similar requests
   - Cache common patterns
   - Reduce token usage

3. Optimize Bandit scoring
   - Pre-compute scores
   - Cache embeddings
   - Parallel scoring

**Deliverables:**
- ✅ Caching implementation
- ✅ Latency optimizations

**Dependencies:**
- Cache storage
- Performance profiling

---

### **Week 8: Production Hardening**

#### **Day 32-35: Testing & Documentation**

**Tasks:**
1. Comprehensive testing
   - Unit tests for all components
   - Integration tests for AIM-OS systems
   - End-to-end tests for unified service
   - Performance tests

2. Documentation
   - API documentation
   - Integration guides
   - Troubleshooting guides
   - User guides

3. Production deployment
   - Configuration management
   - Monitoring setup
   - Error handling
   - Rollback procedures

**Deliverables:**
- ✅ Test suite
- ✅ Documentation
- ✅ Production deployment

**Dependencies:**
- Test frameworks
- Documentation tools
- Deployment infrastructure

---

## 📊 **SUCCESS METRICS**

### **Performance Targets**

- **Router Decision Time:** <200ms average, <400ms maximum
- **Scout Analysis Time:** <700ms average
- **Forensics Analysis Time:** <8s average
- **Tool Selection Accuracy:** >80%
- **Log Analysis Accuracy:** >85%

### **Quality Targets**

- **Test Coverage:** >90%
- **Documentation Coverage:** 100%
- **Integration Completeness:** 100%
- **Error Rate:** <1%

---

## 🔧 **DEPENDENCIES & PREREQUISITES**

### **External Dependencies**

- Cerebras API access (Router Scout, Log-Sentinels Scout)
- Ollama local installation (Log-Sentinels Forensics)
- Drain3 library (Log-Sentinels Template Miner)
- AIM-OS systems (APOE, VIF, SEG, CMC, HHNI, TCS)

### **Infrastructure Requirements**

- Python 3.10+
- Node.js 18+ (IDE panels)
- React 19+ (IDE panels)
- WebSocket support (log collection)
- File system access (log collection)

---

## 📋 **RISK MITIGATION**

### **Technical Risks**

1. **Cerebras API Availability**
   - Mitigation: Fallback to other fast LLMs
   - Contingency: Local fast model

2. **Ollama Performance**
   - Mitigation: Model optimization
   - Contingency: Cloud fallback

3. **Integration Complexity**
   - Mitigation: Phased integration
   - Contingency: Staged rollout

### **Operational Risks**

1. **Performance Degradation**
   - Mitigation: Caching, optimization
   - Contingency: Rate limiting

2. **Privacy Concerns**
   - Mitigation: PII redaction, local processing
   - Contingency: Enhanced redaction

---

## 📚 **REFERENCES**

- Router Integration Analysis: `knowledge_architecture/research/router-apoe-mcp/ROUTER_INTEGRATION_ANALYSIS.md`
- Log-Sentinels Integration Analysis: `knowledge_architecture/research/log-sentinels-hybrid/LOG_SENTINELS_INTEGRATION_ANALYSIS.md`
- Unified Integration Analysis: `knowledge_architecture/research/unified-integration/ROUTER_SENTINELS_UNIFIED_ANALYSIS.md`
- APOE System: `knowledge_architecture/systems/apoe/L3_detailed.md`
- VIF System: `knowledge_architecture/systems/vif/L3_detailed.md`
- SEG System: `knowledge_architecture/systems/seg/L3_detailed.md`

---

**Status:** Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

