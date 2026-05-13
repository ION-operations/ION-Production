# Aether Chat - Unified Implementation Pipeline

**Date:** 2025-11-19  
**Status:** ✅ **IMPLEMENTATION READY**  
**Source:** External AI (ChatGPT) analysis of `AETHER_CHAT_COMPLETE_REFERENCE.md`  
**Purpose:** Single canonical pipeline for Aether Chat implementation

---

## 🎯 **EXECUTIVE SUMMARY**

This document defines the **unified chat turn pipeline (S0-S8)** that collapses all research findings into one canonical lifecycle. This is the **engine schematic** that Cursor will code against.

**Key Innovation:** Single, explicit chat turn pipeline that maps cleanly from the comprehensive reference document to concrete TypeScript implementation.

---

## 📋 **THE UNIFIED PIPELINE: S0-S8**

### **S0 – Ingest & Session Routing**

**Purpose:** Handle incoming user message and route to appropriate session

**Input:**
- Raw user message
- Session context
- Source metadata (Cursor panel, IDE, web, etc.)
- Editor context (if available)

**Processing:**
- Thread/session management (MCP threads, TCS timelines, CMC atoms)
- Source metadata extraction
- Session routing

**Output:**
```typescript
RawUserTurn {
  sessionId: string
  userId?: string
  source: 'cursor' | 'web' | 'standalone'
  message: string
  timestamp: string
  editorContext?: EditorContext
}
```

---

### **S1 – Pre-Processing Pipeline**

**Purpose:** Analyze intent, enrich context, plan response

**Substeps:**
1. **Intent Analysis** – what is this really: debug, write, design, meta, etc.
2. **Context Enrichment** – HHNI + CMC → relevant snippets, prior turns, docs
3. **Personality Injection** – which agent, tone, role
4. **Safety Filtering** – CAS + SCOR
5. **Preliminary Confidence Assessment** – rough VIF pass on *task* risk
6. **Response Planning** – APOE task decomposition
7. **Tool Selection** – which MCP tools, model providers, etc.

**Output:**
```typescript
PreProcessingResult {
  intent: ChatIntent
  mode: ChatMode
  enrichedContext: EnrichedContext   // Context Web subset
  safety: SafetyResult
  initialConfidence: ConfidenceScore // task-level, not answer-level
  responsePlan: ResponsePlan         // APOE DAG for this turn
  tools: ToolSelection
}
```

**AIM-OS Integration:**
- HHNI: Semantic search for context
- CMC: Retrieve conversation history
- CAS: Safety checks
- SCOR: Safety rules
- VIF: Confidence assessment
- APOE: Response planning

---

### **S2 – Evidence & Context Web Construction**

**Purpose:** Build graph of relevant context and evidence pack

**Processing:**
- Build a **graph** of:
  - relevant messages
  - files/docs
  - MIGE nodes
  - past decisions
- Build the **Evidence Pack**:
  - file snippets
  - doc excerpts
  - previous answers
  - test results

**Output:**
```typescript
ContextWeb {
  nodes: ContextNode[]
  edges: ContextEdge[]
}

EvidencePack {
  items: EvidenceItem[]
}
```

**AIM-OS Integration:**
- HHNI: Semantic search for related contexts
- CMC: Retrieve relevant atoms
- SEG: Map relationships between contexts
- MIGE: Track idea evolution

**This is the concrete bridge between the doc's "Context Web Visualization" and the actual reasoning step.**

---

### **S3 – Thinking Mode (Reasoning Core)**

**Purpose:** Execute reasoning with meta-reflection

**Substeps:**
1. **Thought Articulation** – LUCID prompts: domains, assumptions, plan
2. **Execution of ResponsePlan** – APOE orchestrates:
   - tools
   - models
   - micro-agents / swarm
3. **Meta-Reasoning** – reflect on reasoning, compare with prior traces (CMC)
4. **Generate DraftResponse**:
   - user-facing text (raw)
   - reasoning trace
   - citations → EvidenceItem IDs
   - self-estimated confidence

**Output:**
```typescript
ThinkingResult {
  draft: DraftResponse        // answer + actions + citations
  reasoningTrace: ReasoningTrace
  alternatives?: Alternative[]
}
```

**AIM-OS Integration:**
- LUCID Empire: Thought articulation prompts
- APOE: Plan execution
- CMC: Store reasoning traces
- SEG: Map reasoning relationships

**This is what your "ThinkingModeSystem" interface intends, just wrapped in a single stage.**

---

### **S4 – VIF / CAS Gating (κ-Gating, Safety)**

**Purpose:** Never confidently wrong - gate responses by confidence and safety

**Inputs:**
- `DraftResponse`
- `EvidencePack`
- `ReasoningTrace`
- SEG contradiction checks
- CAS quality checks

**Processing:**
- VIF κ-gating (confidence threshold check)
- CAS quality validation
- SCOR safety checks
- SEG contradiction detection

**Outputs:**
- Adjusted confidence
- Possibly downgraded or rejected answer
- Decision to:
  - answer,
  - answer with strong caveats,
  - or ask a clarification

```typescript
GatingResult {
  approved: boolean
  gatedConfidence: ConfidenceScore
  gateReason?: string
  requiredClarification?: string
}
```

**If `approved = false`, the "final answer" is actually a clarification question.**

**AIM-OS Integration:**
- VIF: κ-gating, confidence tracking
- CAS: Quality checks
- SCOR: Safety rules
- SEG: Contradiction detection

---

### **S5 – Post-Processing Pipeline**

**Purpose:** Polish response for user consumption

**Substeps:**
1. **Response Refinement** – clean up text, tighten
2. **Formatting** – markdown, code blocks, lists, tables
3. **Citations** – attach explicit provenance from EvidencePack/SEG
4. **Confidence Indicators** – embed visual-level metadata
5. **Action Suggestions** – next steps if relevant
6. **Follow-up Questions** – candidate follow-ups
7. **Error Correction** – CAS pass for obvious mistakes
8. **Tone Adjustment** – personality + empathy pass

**Output:**
```typescript
PostProcessingResult {
  finalText: string
  uiFormatting: UiFormatting
  citations: EvidenceItem[]
  confidence: ConfidenceScore
  suggestedActions?: SuggestedAction[]
  suggestedFollowUps?: string[]
}
```

**AIM-OS Integration:**
- HHNI: Source retrieval for citations
- CMC: Evidence atoms
- VIF: Confidence indicators
- SEG: Action suggestions
- CAS: Error correction

---

### **S6 – UX/UI Polish & Panels**

**Purpose:** Package everything for frontend consumption

**Processing:**
- Package everything into one payload for the frontend
- Decide which panels to light up, which indicators to show
- Context Web panel
- Evidence panel
- MIGE Tree panel
- Confidence visualization
- Thinking Mode view

**Output:**
```typescript
FinalChatTurn {
  messageId: string
  sessionId: string
  userText: string
  assistantText: string
  confidence: ConfidenceScore
  contextWeb: ContextWeb
  evidence: EvidenceItem[]
  reasoningSummary?: string
  migeUpdates?: MigeUpdate[]
  uiHints: UiHints
  timestamp: string
}
```

**This is what `AetherChat.tsx` and the Cursor panel will actually consume.**

---

### **S7 – Memory, Timeline, & Evolution**

**Purpose:** Persist results to AIM-OS systems

**Processing:**
- **CMC**: store:
  - raw messages
  - reasoning trace
  - evidence links
- **HHNI**: index new atoms for retrieval
- **SEG**: update graph with relations
- **TCS**: write timeline entry
- **MIGE**: update idea evolution tree if this was part of a tracked idea

**No user-facing result; this is side-effect.**

**AIM-OS Integration:**
- CMC: Store all data as atoms
- HHNI: Index for semantic retrieval
- SEG: Update relationship graph
- TCS: Timeline entry
- MIGE: Idea evolution tracking

---

### **S8 – Optional Autonomous Follow-ups**

**Purpose:** Schedule background tasks if needed

**Processing:**
- `cursorChatAutonomousLoop.ts` hooks here
- APOE spawns background tasks:
  - tests
  - refactors
  - further research
- Those feed back as new messages in later turns

**AIM-OS Integration:**
- APOE: Autonomous task orchestration
- Cursor autonomous loop integration

---

## 🔧 **CORE TYPESCRIPT TYPES**

### **File Location:**
`ide_orchestration/prototypes/dac/src/types/aetherChatTypes.ts`

### **Core Types:**

```typescript
// High-level user input
export interface RawUserTurn {
  sessionId: string;
  userId?: string;
  source: 'cursor' | 'web' | 'standalone';
  message: string;
  timestamp: string;
  editorContext?: EditorContext;
}

// Intent & mode
export type ChatIntent =
  | 'ask_explain'
  | 'code_edit'
  | 'debug_error'
  | 'design_arch'
  | 'meta_chat'
  | 'planning'
  | 'other';

export type ChatMode = 'fast' | 'deep' | 'research' | 'surgical';

// Pre-processing outputs
export interface PreProcessingResult {
  intent: ChatIntent;
  mode: ChatMode;
  enrichedContext: EnrichedContext;
  safety: SafetyResult;
  initialConfidence: ConfidenceScore;
  responsePlan: ResponsePlan;
  tools: ToolSelection;
}

// Context Web
export interface ContextNode {
  id: string;
  type: 'msg' | 'file' | 'doc' | 'mige' | 'event';
  label: string;
  importance: number;
  recency: number;
}

export interface ContextEdge {
  from: string;
  to: string;
  relation: 'refers_to' | 'explains' | 'extends' | 'contradicts' | 'depends_on';
}

export interface ContextWeb {
  nodes: ContextNode[];
  edges: ContextEdge[];
}

// Evidence
export interface EvidenceItem {
  id: string;
  kind: 'file_snippet' | 'doc_snippet' | 'prior_msg' | 'test_output' | 'other';
  sourceId: string;     // file path, message id, etc.
  excerpt: string;
  trust: number;        // 0–1
}

export interface EvidencePack {
  items: EvidenceItem[];
}

// Thinking / reasoning
export interface ReasoningTrace {
  id: string;
  rawText: string;
  domains: string[];
  assumptions: string[];
  confidenceSelfReport: number;
}

export interface DraftResponse {
  userFacingText: string;
  actions: PlannedAction[];
  rationale: string;
  citedEvidenceIds: string[];
  selfEstimatedConfidence: number;
}

export interface ThinkingResult {
  draft: DraftResponse;
  reasoningTrace: ReasoningTrace;
  alternatives?: Alternative[];
}

// Gating
export interface ConfidenceScore {
  value: number; // 0–1
  band: 'A' | 'B' | 'C';
}

export interface GatingResult {
  approved: boolean;
  gatedConfidence: ConfidenceScore;
  gateReason?: string;
  requiredClarification?: string;
}

// Post-processing
export interface UiFormatting {
  markdown: string; // for now, just final markdown
}

export interface PostProcessingResult {
  finalText: string;
  uiFormatting: UiFormatting;
  citations: EvidenceItem[];
  confidence: ConfidenceScore;
  suggestedActions?: SuggestedAction[];
  suggestedFollowUps?: string[];
}

// Final turn payload to UI
export interface UiHints {
  showContextWeb: boolean;
  showEvidencePanel: boolean;
  showThinkingMode: boolean;
}

export interface FinalChatTurn {
  messageId: string;
  sessionId: string;
  userText: string;
  assistantText: string;
  confidence: ConfidenceScore;
  contextWeb: ContextWeb;
  evidence: EvidenceItem[];
  reasoningSummary?: string;
  migeUpdates?: MigeUpdate[];
  uiHints: UiHints;
  timestamp: string;
}
```

**Auxiliary Types (stubs for now):**
- `EditorContext`
- `EnrichedContext`
- `SafetyResult`
- `ResponsePlan`
- `ToolSelection`
- `PlannedAction`
- `Alternative`
- `SuggestedAction`
- `MigeUpdate`

---

## 🏗️ **ORCHESTRATOR SKELETON**

### **File Location:**
`ide_orchestration/prototypes/dac/src/services/aetherChatOrchestrator.ts`

### **Main Orchestrator Function:**

```typescript
import {
  RawUserTurn,
  PreProcessingResult,
  ContextWeb,
  EvidencePack,
  ThinkingResult,
  GatingResult,
  PostProcessingResult,
  FinalChatTurn,
} from '../types/aetherChatTypes';

export async function runAetherChatTurn(
  input: RawUserTurn
): Promise<FinalChatTurn> {
  // S1: Pre-Processing
  const pre = await runPreProcessing(input);

  // S2: Context Web + Evidence
  const { contextWeb, evidencePack } = await buildContextAndEvidence(input, pre);

  // S3: Thinking Mode / Reasoning
  const thinking = await runThinkingMode(input, pre, contextWeb, evidencePack);

  // S4: Gating (VIF / CAS / SCOR)
  const gating = await runGating(input, pre, contextWeb, evidencePack, thinking);

  // If gating fails, answer is a clarification question
  const thinkingForOutput =
    gating.approved ? thinking : await buildClarificationDraft(input, pre, gating, contextWeb, evidencePack);

  // S5: Post-Processing
  const post = await runPostProcessing(input, pre, contextWeb, evidencePack, thinkingForOutput, gating);

  // S6: Build FinalChatTurn (UI payload)
  const finalTurn = buildFinalChatTurn(input, pre, contextWeb, evidencePack, thinkingForOutput, gating, post);

  // S7: Persist to AIM-OS (CMC, HHNI, SEG, TCS, MIGE)
  await persistTurnToAimos(input, pre, contextWeb, evidencePack, thinkingForOutput, gating, post, finalTurn);

  // S8: Optional autonomous follow-ups (APOE, cursor loop)
  await maybeScheduleFollowUps(input, pre, finalTurn);

  return finalTurn;
}

// --- Stage functions (initially stubs with TODOs) ---

async function runPreProcessing(input: RawUserTurn): Promise<PreProcessingResult> {
  // TODO: plug into CMC, HHNI, APOE, CAS, SCOR, VIF as per spec
  throw new Error('runPreProcessing not implemented');
}

async function buildContextAndEvidence(
  input: RawUserTurn,
  pre: PreProcessingResult
): Promise<{ contextWeb: ContextWeb; evidencePack: EvidencePack }> {
  // TODO: use HHNI + CMC + SEG to build Context Web & EvidencePack
  throw new Error('buildContextAndEvidence not implemented');
}

async function runThinkingMode(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack
): Promise<ThinkingResult> {
  // TODO: LUCID Empire-style prompts, APOE plan execution, ReasoningTrace
  throw new Error('runThinkingMode not implemented');
}

async function runGating(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult
): Promise<GatingResult> {
  // TODO: VIF κ-gating + CAS/SCOR safety checks
  throw new Error('runGating not implemented');
}

async function buildClarificationDraft(
  input: RawUserTurn,
  pre: PreProcessingResult,
  gating: GatingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack
): Promise<ThinkingResult> {
  // TODO: construct a ThinkingResult where draft is a clarification question
  throw new Error('buildClarificationDraft not implemented');
}

async function runPostProcessing(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult,
  gating: GatingResult
): Promise<PostProcessingResult> {
  // TODO: refinement, formatting, citations, follow-ups, tone
  throw new Error('runPostProcessing not implemented');
}

function buildFinalChatTurn(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult,
  gating: GatingResult,
  post: PostProcessingResult
): FinalChatTurn {
  // TODO: pack objects into FinalChatTurn for UI
  throw new Error('buildFinalChatTurn not implemented');
}

async function persistTurnToAimos(
  input: RawUserTurn,
  pre: PreProcessingResult,
  contextWeb: ContextWeb,
  evidencePack: EvidencePack,
  thinking: ThinkingResult,
  gating: GatingResult,
  post: PostProcessingResult,
  finalTurn: FinalChatTurn
): Promise<void> {
  // TODO: CMC, HHNI, SEG, TCS, MIGE writes
  return;
}

async function maybeScheduleFollowUps(
  input: RawUserTurn,
  pre: PreProcessingResult,
  finalTurn: FinalChatTurn
): Promise<void> {
  // TODO: APOE autonomous loops / cursorChatAutonomousLoop integration
  return;
}
```

**This is the spine Cursor should build around. Everything in the big doc hangs off these functions.**

---

## ✅ **CONCRETE IMPLEMENTATION TASKS**

### **Task 1 – Add Types & Orchestrator Skeleton**

**Goal:** Create the foundation types and orchestrator structure

**Steps:**
1. Create `ide_orchestration/prototypes/dac/src/types/aetherChatTypes.ts` with the core types from this pipeline
2. Create `ide_orchestration/prototypes/dac/src/services/aetherChatOrchestrator.ts` with `runAetherChatTurn` and stub stage functions exactly as specified
3. Do NOT call any real AIM-OS subsystems yet; just set up signatures, imports, and TODOs
4. Keep each file small and well-documented

**Cursor Prompt:**
> You have one source of truth: `AETHER_CHAT_COMPLETE_REFERENCE.md` and the unified pipeline I'm giving you here (S0–S8 plus orchestrator skeleton).
>
> 1. Create `ide_orchestration/prototypes/dac/src/types/aetherChatTypes.ts` with the core types from this pipeline (RawUserTurn, PreProcessingResult, ContextWeb, EvidencePack, ThinkingResult, GatingResult, PostProcessingResult, FinalChatTurn, etc.).
> 2. Create `ide_orchestration/prototypes/dac/src/services/aetherChatOrchestrator.ts` with a `runAetherChatTurn` function and stub stage functions exactly as specified.
> 3. Do NOT call any real AIM-OS subsystems yet; just set up signatures, imports, and TODOs. Keep each file small and well-documented.

---

### **Task 2 – Wire AetherChat.tsx and useAIChat.ts to the Orchestrator**

**Goal:** Connect existing UI components to the new orchestrator

**Steps:**
1. In `AetherChat.tsx` and `useAIChat.ts`:
   - Replace direct model/agent calls with a call to `runAetherChatTurn`
   - Map the existing message structure into `RawUserTurn`
   - Map `FinalChatTurn` back into the UI's message state
2. For now, stub `runPreProcessing` etc. to return minimal dummy data so the UI can still function

**Cursor Prompt:**
> Refactor `packages/ide_chat_app/src/hooks/useAIChat.ts` and `ide_orchestration/prototypes/dac/src/components/aether-chat/AetherChat.tsx` to:
>
> * Construct a `RawUserTurn` from the current user input and editor/session context.
> * Call `runAetherChatTurn`.
> * Use the returned `FinalChatTurn` to update the chat UI, including confidence indicator stubs and room for Context Web and Evidence panels.
>
> For now, stub `runPreProcessing` etc. to return minimal dummy data so the UI can still function.

---

### **Task 3 – Expose Confidence & Evidence in UI (minimal)**

**Goal:** Show confidence and evidence in the UI

**Steps:**
1. In `AetherChat.tsx` and the Cursor `customChatPanel.ts`:
   - Display `FinalChatTurn.confidence.band` as a simple badge
   - Add a collapsible "Evidence" area listing `EvidenceItem.sourceId` and a short snippet
2. Use existing styling primitives; focus on data flow, not pixel-perfect design

**Cursor Prompt:**
> In `AetherChat.tsx` and `cursor-addon/src/customChatPanel.ts`, update the message rendering so each assistant message:
>
> * Shows a small confidence badge (A/B/C from `FinalChatTurn.confidence.band`).
> * Has a collapsible "Evidence" panel that lists `evidence` items' `sourceId` and `excerpt`.
>
> Use existing styling primitives; focus on data flow, not pixel-perfect design.

---

### **Task 4 – Gradually Implement Each Stage**

**Goal:** Implement stages incrementally

**Approach:**
- Implement **Context & Evidence (S2)** by wiring to:
  - `ChatHistoryService.ts` (CMC/HHNI)
- Implement **Pre-Processing (S1)** with basic intent classification and simple APOE plan stubs
- Implement **Thinking Mode (S3)** by wrapping existing model calls with LUCID-style thought prompts
- Then VIF gating, etc.

**Each step is bounded and testable.**

---

## 🔗 **MAPPING FROM REFERENCE DOCUMENT**

### **Reference Document Sections → Pipeline Stages:**

- **"Pre-Processing Pipeline"** → **S1**
- **"Thinking Mode System"** → **S3**
- **"Post-Processing Pipeline"** → **S5**
- **"UX/UI Polish System"** → **S6**
- **"Context Web Visualization"** → **S2**
- **"Evidence Panel"** → **S2, S6**
- **"Idea Evolution (MIGE Tree)"** → **S7**
- **"Confidence Gating (κ-gating)"** → **S4**
- **"Provenance Chain"** → **S2, S5**
- **"Memory, Timeline, & Evolution"** → **S7**

**Everything in the reference document maps cleanly into these stages.**

---

## 📊 **IMPLEMENTATION PRIORITY**

### **Phase 1: Foundation (Week 1)**
- ✅ Task 1: Types & Orchestrator Skeleton
- ✅ Task 2: Wire UI to Orchestrator
- ✅ Task 3: Confidence & Evidence UI

### **Phase 2: Core Stages (Weeks 2-3)**
- Task 4a: Implement S2 (Context & Evidence) - Wire to ChatHistoryService
- Task 4b: Implement S1 (Pre-Processing) - Basic intent + APOE stubs
- Task 4c: Implement S3 (Thinking Mode) - LUCID prompts + model calls

### **Phase 3: Quality & Safety (Week 4)**
- Task 4d: Implement S4 (Gating) - VIF κ-gating + CAS/SCOR
- Task 4e: Implement S5 (Post-Processing) - Refinement + citations

### **Phase 4: Polish & Persistence (Week 5)**
- Task 4f: Implement S6 (UX/UI Polish) - Panels + visualizations
- Task 4g: Implement S7 (Memory & Timeline) - CMC, HHNI, SEG, TCS, MIGE

### **Phase 5: Autonomous (Week 6)**
- Task 4h: Implement S8 (Autonomous Follow-ups) - APOE + cursor loop

---

## 🎯 **NEXT STEPS**

1. **Review this pipeline** - Ensure it matches the reference document
2. **Start Task 1** - Create types and orchestrator skeleton
3. **Iterate incrementally** - One stage at a time, testable and bounded

**This pipeline is the single source of truth for implementation. All code should follow this structure.**

---

**Status:** ✅ **IMPLEMENTATION READY**  
**Created:** 2025-11-19  
**Source:** External AI (ChatGPT) analysis  
**Purpose:** Unified pipeline for Aether Chat implementation

