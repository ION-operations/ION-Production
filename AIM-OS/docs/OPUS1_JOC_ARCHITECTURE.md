# Joint Operations Center — Technical Architecture

**Author:** Claude Opus 4.6  
**Date:** 2026-03-02  
**Status:** 🏗️ ARCHITECTURE DOCUMENT — System design, data flows, and component structure  
**Companion to:** [JOC Master Vision](./OPUS1_JOC_MASTER_VISION.md)  

---

## System Overview

The JOC is a **three-tier system** built on existing AIM-OS infrastructure:

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION TIER                           │
│                                                                 │
│  JOC Panel (React/TSX)                                         │
│  ├── MissionDashboard.tsx        — Central ops view             │
│  ├── SessionManager.tsx          — AI fleet session cards        │
│  ├── DispatchEngine.tsx          — Multi-AI prompt composer      │
│  ├── ResultsSynthesizer.tsx      — Response aggregation          │
│  ├── ProjectCatalog.tsx          — Living project index          │
│  ├── AgentCommsPanel.tsx         — MCP message bus viewer        │
│  └── components/                                                │
│      ├── AIStatusCard.tsx        — Individual AI session card    │
│      ├── MissionCard.tsx         — Mission progress display     │
│      ├── DispatchTargetPicker.tsx — AI selection instrument     │
│      ├── ContextCompiler.tsx     — Auto file packager            │
│      ├── SynthesisView.tsx       — Multi-response comparison    │
│      └── HealthBar.tsx           — Visual health indicator       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     ORCHESTRATION TIER                           │
│                                                                 │
│  JOC Service (TypeScript, Express)                              │
│  ├── services/                                                  │
│  │   ├── dispatchService.ts      — Mission lifecycle manager    │
│  │   ├── sessionOrchestrator.ts  — AI session health monitor    │
│  │   ├── contextPackager.ts      — File compiler for AI context │
│  │   ├── synthesisEngine.ts      — Response comparison/merge    │
│  │   └── projectIndexer.ts       — Filesystem project scanner   │
│  ├── drivers/                                                   │
│  │   ├── BaseAIDriver.ts         — Abstract driver interface    │
│  │   ├── ChatGPTDriver.ts        — ChatGPT DOM interaction      │
│  │   ├── GeminiDriver.ts         — Gemini DOM interaction       │
│  │   ├── PerplexityDriver.ts     — Perplexity DOM interaction   │
│  │   ├── ClaudeAPIDriver.ts      — Claude API (direct)          │
│  │   └── GenericBrowserDriver.ts — Fallback for unknown AIs     │
│  └── api/                                                       │
│      ├── missions.ts             — CRUD + dispatch endpoints    │
│      ├── sessions.ts             — Session health + control     │
│      ├── drivers.ts              — Driver status + management   │
│      └── projects.ts             — Project catalog endpoints    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     INFRASTRUCTURE TIER                          │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │ Browser Service  │  │ MCP Server       │  │ Connection     │ │
│  │ (Puppeteer)     │  │ (lucid-mcp)      │  │ Manager        │ │
│  │ ● Launch        │  │ ● AI messages    │  │ ● Credentials  │ │
│  │ ● Navigate      │  │ ● Agent comms    │  │ ● Sessions     │ │
│  │ ● Execute JS    │  │ ● Memory (CMC)   │  │ ● Cookies      │ │
│  │ ● Screenshot    │  │ ● Timeline       │  │ ● Encryption   │ │
│  │ ● CDP viewport  │  │ ● HHNI search    │  │ ● AES-256-GCM  │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
│                ALREADY BUILT (Phase 0-3 deliverables)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## AI Driver System

The driver system is the critical innovation. Each AI subscription gets a **driver** — a module that knows how to interact with that specific AI's web interface.

### Driver Interface (BaseAIDriver)

```typescript
/**
 * Base interface for all AI drivers.
 * 
 * A driver encapsulates the knowledge of HOW to interact with a specific
 * AI service's web interface (or API). It handles:
 * - Session management (login detection, cookie persistence)
 * - Prompt injection (typing into the chat input)
 * - Response extraction (reading the AI's response)
 * - Status monitoring (quota, health, rate limits)
 * 
 * Canon compliance: Drivers are the "visual editors" of AI interaction —
 * they transform abstract "send a message" into concrete DOM operations.
 */
interface AIDriver {
  /** Unique identifier for this AI service */
  readonly providerId: string;
  
  /** Human-readable name */
  readonly displayName: string;
  
  /** URL pattern for detecting this AI's pages */
  readonly urlPattern: RegExp;
  
  /** Current session state */
  getSessionState(): Promise<AISessionState>;
  
  /** Check if the user is currently logged in */
  isLoggedIn(): Promise<boolean>;
  
  /** Inject a prompt into the AI's chat input and submit it */
  injectPrompt(prompt: string, options?: InjectOptions): Promise<InjectResult>;
  
  /** Extract the latest response from the AI's chat output */
  extractResponse(options?: ExtractOptions): Promise<ExtractedResponse>;
  
  /** Wait for the AI to finish generating its response */
  waitForCompletion(timeoutMs?: number): Promise<boolean>;
  
  /** Get the AI's current quota/rate limit status (if detectable) */
  getQuotaStatus(): Promise<QuotaStatus | null>;
  
  /** Get conversation threads (if the AI supports it) */
  getConversationList(): Promise<ConversationInfo[]>;
  
  /** Create a new conversation/thread */
  newConversation(): Promise<string>;
  
  /** Get the AI's stored memories (if supported, e.g., ChatGPT) */
  getMemoryItems(): Promise<MemoryItem[]>;
  
  /** Health check — is the session alive and responsive? */
  healthCheck(): Promise<HealthCheckResult>;
}

interface AISessionState {
  providerId: string;
  isLoggedIn: boolean;
  sessionAge: number;        // ms since last cookie refresh
  lastActivity: number;      // ms since last interaction
  conversationCount: number;
  currentModel: string;      // e.g., "GPT-4o", "Gemini 1.5 Pro"
  health: 'healthy' | 'degraded' | 'dead';
}

interface InjectOptions {
  /** Which conversation to inject into (null = current) */
  conversationId?: string;
  /** Whether to create a new conversation for this prompt */
  newThread?: boolean;
  /** Whether to wait for the AI to finish responding */
  waitForResponse?: boolean;
  /** Custom timeout for waiting */
  timeoutMs?: number;
}

interface InjectResult {
  success: boolean;
  conversationId: string;
  promptLength: number;
  timestamp: number;
}

interface ExtractedResponse {
  text: string;
  html: string;
  tokenEstimate: number;
  model: string;
  conversationId: string;
  timestamp: number;
  isComplete: boolean;
  hasCodeBlocks: boolean;
  codeBlocks: { language: string; code: string }[];
}

interface QuotaStatus {
  messagesUsed: number;
  messagesLimit: number;
  resetTime: number;
  currentModel: string;
  tier: string;  // "free", "plus", "pro", etc.
}

interface HealthCheckResult {
  healthy: boolean;
  loginValid: boolean;
  pageResponsive: boolean;
  networkOk: boolean;
  latencyMs: number;
  issues: string[];
}
```

### ChatGPT Driver (Example Implementation Strategy)

The ChatGPT driver knows the specific DOM structure of chat.openai.com:

```typescript
/**
 * ChatGPT-specific AI driver.
 * 
 * Key selectors and interaction patterns for chatgpt.com:
 * - Chat input: contenteditable div inside the prompt textarea
 * - Submit button: button with data-testid="send-button"
 * - Response: div.markdown inside assistant message containers
 * - Streaming indicator: presence of the streaming cursor element
 * - Login state: absence of login/signup buttons in the page
 * - Model selector: dropdown showing current model (GPT-4o, etc.)
 * 
 * IMPORTANT: These selectors WILL change as OpenAI updates their UI.
 * The driver must be version-adaptive or easily updatable.
 */

// Core interaction flow:
// 1. Navigate to chat.openai.com (or specific conversation URL)
// 2. Detect login state via page content analysis
// 3. If logged in, find the chat input element
// 4. Clear any existing input, type the prompt
// 5. Click the send button (or press Enter)
// 6. Monitor for streaming completion (cursor element disappears)
// 7. Extract the response from the last assistant message

// Key challenges:
// - ContentEditable divs require special input handling (not simple .value = "text")
// - Streaming responses must be monitored for completion
// - Rate limiting may show a popup that needs detection
// - Session cookies rotate; need periodic health checks
// - Multiple tabs of ChatGPT can cause conflicts
```

### Gemini Driver (Example Implementation Strategy)

```typescript
/**
 * Gemini-specific AI driver (gemini.google.com)
 * 
 * Key interaction patterns:
 * - Chat input: rich text editor area
 * - Submit: send button or Enter key
 * - Response: rendered markdown in response containers
 * - Streaming: "typing" indicator visible during generation
 * - Login: Google SSO session; cookies include SID, HSID, etc.
 * - Model: Model selector dropdown (Gemini 1.5 Pro, etc.)
 * 
 * Unique Gemini features to leverage:
 * - Image upload support (drag-and-drop)
 * - Google Search integration in responses
 * - Export to Google Docs capability
 * - Canvas/artifact creation
 */
```

### Driver Registry

```typescript
/**
 * DriverRegistry manages available AI drivers and 
 * matches them to browser sessions.
 */
interface DriverRegistry {
  /** Register a new driver */
  register(driver: AIDriver): void;
  
  /** Find the driver for a given URL */
  findDriverForUrl(url: string): AIDriver | null;
  
  /** Get all registered drivers */
  getAll(): AIDriver[];
  
  /** Get driver by provider ID */
  get(providerId: string): AIDriver | null;
  
  /** Check health of all registered drivers */
  healthCheckAll(): Promise<Map<string, HealthCheckResult>>;
}
```

---

## Mission Lifecycle

A "mission" is the core orchestration unit — a prompt dispatched to one or more AIs.

```
┌─────────┐   ┌───────────┐   ┌───────────┐   ┌──────────────┐   ┌──────────┐
│ COMPOSE  │──▶│ DISPATCH  │──▶│ MONITOR   │──▶│ SYNTHESIZE   │──▶│ ROUTE    │
│          │   │           │   │           │   │              │   │          │
│ Write    │   │ Send to   │   │ Track     │   │ Compare      │   │ Send to  │
│ prompt   │   │ selected  │   │ progress  │   │ responses    │   │ agents   │
│ Select   │   │ AIs via   │   │ per AI    │   │ Find         │   │ Save to  │
│ targets  │   │ drivers   │   │ Detect    │   │ consensus    │   │ memory   │
│ Attach   │   │           │   │ completion│   │ Highlight    │   │ Export   │
│ context  │   │           │   │ Extract   │   │ disagreement │   │          │
│          │   │           │   │ responses │   │              │   │          │
└─────────┘   └───────────┘   └───────────┘   └──────────────┘   └──────────┘

State Machine:
DRAFT → DISPATCHING → IN_PROGRESS → EXTRACTING → SYNTHESIZING → COMPLETE → ROUTED
                └───────────────── FAILED (retry available) ──────────────────┘
```

### Mission Data Model

```typescript
interface Mission {
  id: string;                    // M-001, M-002, etc.
  title: string;
  prompt: string;
  
  // Dispatch config
  targets: DispatchTarget[];     // Which AIs to send to
  strategy: 'parallel' | 'sequential' | 'consensus' | 'debate';
  
  // Context
  contextFiles: ContextFile[];   // Auto-compiled or manually added
  totalTokenEstimate: number;
  
  // State
  status: MissionStatus;
  createdAt: number;
  completedAt: number | null;
  
  // Results
  responses: Map<string, ExtractedResponse>;  // providerId → response
  synthesis: SynthesisResult | null;
  
  // Post-processing
  routedTo: string[];           // Agent IDs that received the results
  savedToMemory: boolean;
  savedToDocs: string | null;   // File path if saved
}

interface DispatchTarget {
  providerId: string;
  driverId: string;
  status: 'pending' | 'sending' | 'waiting' | 'extracting' | 'done' | 'failed';
  progress: number;             // 0-1
  error: string | null;
}

interface ContextFile {
  path: string;
  name: string;
  sizeBytes: number;
  tokenEstimate: number;
  included: boolean;            // Toggle on/off
}

interface SynthesisResult {
  agreements: string[];         // Points all AIs agree on
  disagreements: DisagreementItem[];
  confidence: number;           // 0-1
  uniqueSources: number;
  summary: string;
}
```

---

## Context Packaging Service

This automates the 20% of time spent compiling context. When dispatching a mission, the Context Packager can:

1. **Auto-detect relevant files** from the active project workspace
2. **Compile them** into a format suitable for each AI (respecting their token limits)
3. **Estimate tokens** so you know how much context budget remains
4. **Prioritize** files by relevance (most-recently-edited first, then by import graph proximity)

```typescript
interface ContextPackager {
  /** Scan a project directory and find relevant files */
  scanProject(projectPath: string): Promise<ContextFile[]>;
  
  /** Compile selected files into a context bundle */
  compile(files: ContextFile[], options: CompileOptions): Promise<ContextBundle>;
  
  /** Estimate token count for a text block */
  estimateTokens(text: string): number;
  
  /** Auto-select the most relevant files for a given prompt */
  autoSelect(prompt: string, projectPath: string, maxTokens: number): Promise<ContextFile[]>;
}

interface CompileOptions {
  maxTokens: number;           // Budget per AI
  format: 'concatenated' | 'structured' | 'xml-tagged';
  includeFilePaths: boolean;
  includeLineNumbers: boolean;
  stripComments: boolean;
}

interface ContextBundle {
  text: string;
  tokenCount: number;
  filesIncluded: string[];
  filesExcluded: string[];     // What didn't fit
  truncated: boolean;
}
```

---

## Session Health Monitoring

The Session Orchestrator runs continuous health checks on all AI sessions:

```
Every 60 seconds:
  ForEach registered AI session:
    1. Check if browser instance is alive (isConnected)
    2. Check if session cookies are fresh (age < threshold)
    3. Attempt lightweight page interaction (page responsive?)
    4. Detect login popups or session expiry screens
    5. Update health status: healthy / degraded / dead
    
  If session degraded:
    → Show amber indicator on dashboard
    → Log warning
    
  If session dead:
    → Show red indicator on dashboard  
    → Attempt automatic session refresh (reload + cookie reuse)
    → If still dead, alert user: "ChatGPT session expired — re-login needed"
```

### Health State Machine

```
                    ┌─────────────────┐
                    │    HEALTHY      │
                    │ (green, active) │
                    └────┬───────┬────┘
                         │       │
          cookie stale   │       │  page unresponsive
                         │       │
                    ┌────▼───────▼────┐
                    │   DEGRADED      │
                    │ (amber, warning)│
                    └────┬───────┬────┘
                         │       │
          auto-refresh   │       │  login expired
          succeeds       │       │
                    ┌────▼──┐  ┌─▼────────────┐
                    │HEALTHY│  │    DEAD       │
                    │       │  │ (red, alert)  │
                    └───────┘  └───────────────┘
                                     │
                               user re-logs in
                                     │
                               ┌─────▼─────┐
                               │  HEALTHY   │
                               └────────────┘
```

---

## Integration Points

### With Existing Browser Automation Service

The JOC orchestration tier builds **on top of** the browser service, not alongside it:

| Browser Service (Existing) | JOC Layer (New) |
|---------------------------|-----------------|
| `launchBrowser()` | `sessionOrchestrator.ensureSession(providerId)` |
| `navigate(url)` | `driver.navigateToChat(conversationId)` |
| `page.evaluate(script)` | `driver.injectPrompt(text)` |
| `screenshot()` | `dashboard.liveViewport(sessionId)` |
| `detectElements()` | `driver.findChatInput()`, `driver.findResponseContainer()` |
| `connectionManager.saveCookies()` | `sessionOrchestrator.persistSession()` |

### With MCP Message Bus

| MCP Tool | JOC Usage |
|----------|-----------|
| `send_ai_message` | Route mission results to Aether/Codex |
| `get_ai_messages` | Display in Agent Comms panel |
| `store_memory` | Save synthesis results to CMC |
| `retrieve_memory` | Auto-context from past missions |

### With Lucid MCP Server

The JOC will be accessible as MCP tools, allowing any agent to dispatch missions:

```typescript
// New MCP tools the JOC would expose:
'joc_dispatch_mission'      // Send a prompt to multiple AIs
'joc_get_mission_status'    // Check mission progress
'joc_get_session_health'    // Check AI fleet status
'joc_list_projects'         // Query the project catalog
```

---

## Data Persistence

| Data | Storage | Format |
|------|---------|--------|
| Missions | `data/joc/missions.json` | Mission[] |
| AI Sessions | `data/joc/sessions.json` | AISessionState[] |
| Driver Config | `data/joc/drivers.json` | DriverConfig[] |
| Project Index | `data/joc/projects.json` | ProjectEntry[] |
| Extracted Responses | `data/joc/responses/M-{id}/` | Individual .md files |
| Synthesis Results | `data/joc/synthesis/M-{id}.json` | SynthesisResult |

---

## Security Considerations

1. **Credentials**: All session cookies encrypted via ConnectionManager (AES-256-GCM) — already implemented
2. **API Keys**: If Claude/other APIs are used directly, keys stored in encrypted env
3. **Session Isolation**: Each AI gets its own browser context (incognito profile) to prevent cross-session leaks
4. **Driver Trust**: Drivers only execute within their URL pattern scope — a ChatGPT driver cannot interact with pages outside `chat.openai.com`
5. **Rate Limiting**: Drivers must respect per-provider rate limits; the dispatch engine enforces cooldowns

---

## Port Allocation

Following the launcher canon (one app, one port, no conflicts):

| Service | Port | Purpose |
|---------|------|---------|
| Browser Automation Service | 5002 | Existing Puppeteer service |
| JOC Orchestration Service | 5010 | Mission dispatch, session mgmt |
| JOC Panel Dev Server | 5011 | React panel during development |
| MCP Server (lucid-mcp) | 5001 | Agent communication backbone |

---

*Architecture by Claude Opus 4.6*  
*For the vision, see: [JOC Master Vision](./OPUS1_JOC_MASTER_VISION.md)*  
*For the driver design, see: [JOC AI Driver Design](./OPUS1_JOC_AI_DRIVER_DESIGN.md) (forthcoming)*
