# Joint Operations Center — Compute Fabric & IDE Layout

**Author:** Claude Opus 4.6  
**Date:** 2026-03-02  
**Status:** 🏗️ DESIGN DOCUMENT — Compute orchestration, hardware integration, and IDE UI philosophy  
**Companion to:** [JOC Master Vision](./OPUS1_JOC_MASTER_VISION.md) | [JOC Architecture](./OPUS1_JOC_ARCHITECTURE.md)

---

## The Expanded Vision

The original JOC vision focused on browser-based AI sessions. But the real operational surface is **much wider** than browser tabs. Braden's actual compute fabric includes:

| Resource | Type | Capacity | Access Method |
|----------|------|----------|---------------|
| **ChatGPT Pro** | Browser AI | High token limits | DOM driver (browser session) |
| **Gemini Ultra** | Browser AI + CLI + API | Near-unlimited with Ultra | DOM driver + CLI subprocess + REST API |
| **Claude** | Browser AI + API | API-tier limits | DOM driver + Anthropic API |
| **Perplexity Pro** | Browser AI | Research + web-sourced | DOM driver |
| **Gemini CLI** | Local CLI tool | Near-unlimited (Ultra account) | Subprocess pipe (stdin/stdout) |
| **Gemini API** | Direct REST API | Configurable rate limits | HTTP client |
| **Local GPU (3050 Ti)** | Local inference | 4GB VRAM, low-end inference | Ollama / llama.cpp / vLLM |
| **Google Drive** | Cloud storage | **30TB** | Google Drive API / rclone |
| **Google Vertex AI** | Cloud compute | On-demand VMs + AI endpoints | Vertex SDK / REST |
| **NVIDIA Cloud** | Cloud GPU | High-end sims + inference | NVIDIA NGC / DGX Cloud API |
| **Custom Models** | Trained models | Project-specific | Deployed on Vertex/NVIDIA |

This means the JOC isn't just a "browser automation hub" — it's a **unified compute orchestration center** that dispatches work to the right resource based on the task's needs.

---

## Compute Tier Design

### The Three Compute Rings

Think of available compute as three concentric rings, from fastest/cheapest to slowest/most powerful:

```
                    ┌─────────────────────────────────┐
                    │     RING 3: CLOUD COMPUTE       │
                    │                                  │
                    │  ● Vertex AI VMs (GPU instances) │
                    │  ● NVIDIA DGX Cloud              │
                    │  ● Custom model hosting           │
                    │  ● High-end simulations           │
                    │  ● Long-running training jobs     │
                    │                                  │
                    │  Latency: minutes-hours           │
                    │  Cost: $$$                        │
                    │  Power: ████████████████████      │
                    │                                  │
                ┌───┴───────────────────────────┐      │
                │    RING 2: API / CLI DIRECT    │      │
                │                               │      │
                │  ● Gemini CLI (Ultra)         │      │
                │  ● Gemini API                  │      │
                │  ● Anthropic API (Claude)     │      │
                │  ● OpenAI API                  │      │
                │  ● Local GPU inference (3050Ti)│      │
                │                               │      │
                │  Latency: seconds              │      │
                │  Cost: $ (API) / free (local)  │      │
                │  Power: ██████████████         │      │
                │                               │      │
            ┌───┴───────────────────────┐       │      │
            │   RING 1: BROWSER SESSION  │       │      │
            │                           │       │      │
            │  ● ChatGPT (web)          │       │      │
            │  ● Gemini (web)           │       │      │
            │  ● Claude (web)           │       │      │
            │  ● Perplexity (web)       │       │      │
            │                           │       │      │
            │  Latency: 10-60s          │       │      │
            │  Cost: subscription       │       │      │
            │  Power: ██████████        │       │      │
            └───────────────────────────┘       │      │
                └───────────────────────────────┘      │
                    └─────────────────────────────────┘

    Work flows outward: Try Ring 1 first (cheapest, already paid),
    escalate to Ring 2 for speed/programmatic access,
    escalate to Ring 3 for heavy compute.
```

### Smart Dispatch Router

When a mission is created, the Dispatch Router decides **which ring and which resource** to use:

```typescript
interface DispatchRouter {
  /**
   * Given a mission, determines the optimal compute target(s).
   * 
   * Decision factors:
   * - Task type (chat, code gen, research, simulation, training)
   * - Token budget (small prompt vs. massive context)
   * - Latency requirement (interactive vs. background)
   * - Cost sensitivity (subscription-included vs. API billing)
   * - Capability match (web search? code execution? image gen?)
   * - Current load (which resources are idle?)
   */
  route(mission: Mission): Promise<RoutingPlan>;
}

interface RoutingPlan {
  primary: ComputeTarget;              // Best match
  fallbacks: ComputeTarget[];          // If primary fails
  reasoning: string;                   // Why this route was chosen
  estimatedCost: CostEstimate;
  estimatedLatency: number;            // ms
}

interface ComputeTarget {
  ring: 1 | 2 | 3;
  provider: string;                    // "chatgpt", "gemini-cli", "vertex-ai", etc.
  accessMethod: 'browser' | 'cli' | 'api' | 'vm';
  endpoint?: string;                   // API endpoint or VM address
  model?: string;                      // Specific model to use
  capabilities: string[];             // What this target can do
}
```

### Routing Heuristics

| Task Type | Preferred Route | Why |
|-----------|----------------|-----|
| Quick question, chat | Ring 1: ChatGPT/Gemini browser | Already paid, no additional cost |
| Batch processing (50+ prompts) | Ring 2: Gemini CLI | Near-unlimited with Ultra, no browser overhead |
| Code generation with execution | Ring 2: Gemini API or OpenAI API | Structured output, no DOM parsing |
| Web research with sources | Ring 1: Perplexity browser | Web search integration built-in |
| Large context (>100K tokens) | Ring 2: Gemini CLI/API | 1M+ context window |
| Image understanding | Ring 2: Gemini API (vision) | Direct image upload |
| Small model inference (summaries, classification) | Ring 2: Local 3050 Ti | Free, private, no latency |
| Heavy simulation (fluid, particles) | Ring 3: Vertex/NVIDIA cloud | GPU compute required |
| Custom model training | Ring 3: Vertex AI | Managed training infrastructure |
| Long-term storage/retrieval | Google Drive (30TB) | Persistent, sharable |

---

## Gemini CLI Integration

The Gemini CLI is a **high-throughput, near-unlimited channel** with the Ultra account. This is a major asset:

```typescript
interface GeminiCLIDriver extends AIDriver {
  readonly providerId: 'gemini-cli';
  readonly accessMethod: 'cli';
  
  /**
   * Execute a prompt via Gemini CLI subprocess.
   * 
   * Advantages over browser:
   * - No DOM parsing, no UI flakiness
   * - Programmatic stdin/stdout
   * - Near-unlimited with Ultra account
   * - Can handle massive context (1M+ tokens)
   * - Supports streaming output
   * - Can process files directly
   * 
   * Implementation:
   * - Spawns `gemini` CLI process
   * - Pipes prompt to stdin
   * - Reads response from stdout
   * - Supports --model flag for model selection
   * - Can include file attachments via CLI flags
   */
  execute(prompt: string, options?: CLIOptions): Promise<CLIResponse>;
  
  /** Stream response chunks for real-time display */
  executeStreaming(prompt: string, onChunk: (chunk: string) => void): Promise<void>;
  
  /** Execute with file context (Gemini supports large file uploads) */
  executeWithFiles(prompt: string, files: string[]): Promise<CLIResponse>;
  
  /** Batch execute multiple prompts sequentially */
  executeBatch(prompts: string[]): AsyncIterable<CLIResponse>;
}

interface CLIOptions {
  model?: string;           // "gemini-2.0-flash", "gemini-2.0-pro", etc.
  maxTokens?: number;
  temperature?: number;
  systemPrompt?: string;
  files?: string[];         // File paths to include as context
  streaming?: boolean;
  timeout?: number;
}

interface CLIResponse {
  text: string;
  model: string;
  tokenCount: {
    input: number;
    output: number;
  };
  latencyMs: number;
  exitCode: number;
}
```

### CLI → JOC Integration Pattern

```
Mission created
    │
    ▼
DispatchRouter says: "This is a batch task with 50 prompts, use Gemini CLI"
    │
    ▼
GeminiCLIDriver.executeBatch(prompts)
    │
    ├──► Spawns gemini process
    ├──► Pipes prompt #1 → stdout → capture response
    ├──► Pipes prompt #2 → stdout → capture response
    ├──► ... (50x, with rate limiting if needed)
    │
    ▼
Results aggregated into Mission.responses
    │
    ▼
SynthesisEngine.synthesize(responses)
    │
    ▼
Dashboard shows: "Mission complete — 50/50 processed"
```

---

## Local GPU Inference (3050 Ti)

The 3050 Ti has 4GB VRAM — enough for small quantized models (7B Q4, some 13B Q3). Useful for:

- **Classification tasks**: "Is this code Python or TypeScript?" → instant, free
- **Summarization**: Condensing long responses from other AIs
- **Embedding generation**: Creating vector embeddings for project code
- **Quick drafts**: First-pass generation that gets refined by a more powerful model
- **Privacy-sensitive tasks**: Data that shouldn't leave the local machine

```typescript
interface LocalGPUDriver extends AIDriver {
  readonly providerId: 'local-gpu';
  readonly accessMethod: 'api';  // Running via Ollama/llama.cpp HTTP server
  
  /**
   * Local inference via Ollama or llama.cpp server.
   * 
   * Available models (fitting 4GB VRAM):
   * - gemma-2b-it (fast, small tasks)
   * - phi-3-mini (3.8B, good reasoning for size)
   * - mistral-7b-q4 (general purpose)
   * - codellama-7b-q4 (code-specific)
   * - nomic-embed-text (embedding generation)
   * 
   * Running on: localhost:11434 (Ollama default)
   */
  
  /** Check which models are available locally */
  listModels(): Promise<LocalModel[]>;
  
  /** Pull a new model if not available */
  pullModel(modelName: string): Promise<void>;
  
  /** Generate embeddings for text */
  embed(text: string, model?: string): Promise<number[]>;
  
  /** Estimate if a prompt fits in the model's context */
  fitsInContext(prompt: string, model: string): boolean;
}

interface LocalModel {
  name: string;
  size: string;         // "3.8GB", "4.1GB"
  quantization: string; // "Q4_K_M", "Q8_0"
  contextLength: number;
  loaded: boolean;      // Currently in VRAM
}
```

### Local GPU Dashboard Card

```
┌─ LOCAL GPU: NVIDIA 3050 Ti ─────────────────────────────────┐
│                                                              │
│  VRAM: ████████████░░░░ 3.1/4.0 GB                          │
│  GPU:  ██████░░░░░░░░░░ 38% utilization                     │
│  Temp: 62°C  Fan: 45%                                       │
│                                                              │
│  Loaded Model: phi-3-mini (Q4_K_M)                          │
│  Status: ● READY                                             │
│                                                              │
│  Available Models:                                           │
│  ├─ phi-3-mini (3.8B)      ● loaded     [Unload]           │
│  ├─ mistral-7b (Q4)        ○ available  [Load]             │
│  ├─ codellama-7b (Q4)      ○ available  [Load]             │
│  └─ nomic-embed-text       ○ available  [Load]             │
│                                                              │
│  Tasks completed today: 142  |  Avg latency: 1.2s           │
└──────────────────────────────────────────────────────────────┘
```

---

## Cloud Compute Layer (Ring 3)

### Google Vertex AI Integration

```typescript
interface VertexAIDriver {
  readonly providerId: 'vertex-ai';
  
  /**
   * Google Vertex AI provides:
   * - Managed model endpoints (Gemini, PaLM, custom fine-tuned)
   * - Custom training pipelines
   * - GPU VMs (A100, H100) for simulations
   * - Batch prediction jobs
   * - Model Garden (pre-trained models)
   */
  
  /** List available endpoints */
  listEndpoints(): Promise<VertexEndpoint[]>;
  
  /** Launch a GPU VM for simulation work */
  launchVM(config: VMConfig): Promise<VMInstance>;
  
  /** Submit a batch prediction job */
  submitBatchJob(job: BatchJobConfig): Promise<BatchJob>;
  
  /** Deploy a custom model */
  deployModel(modelArtifact: string, config: DeployConfig): Promise<string>;
  
  /** Get status and cost tracking */
  getUsage(): Promise<VertexUsage>;
}

interface VMConfig {
  machineType: string;           // "n1-standard-8", "a2-highgpu-1g"  
  accelerator?: {
    type: 'NVIDIA_TESLA_T4' | 'NVIDIA_A100_80GB' | 'NVIDIA_H100_80GB';
    count: number;
  };
  diskSizeGB: number;
  preemptible: boolean;          // Cheaper but can be terminated
  maxRuntime: number;            // Auto-shutdown after N hours
  startupScript?: string;        // What to run on boot
}

interface VMInstance {
  id: string;
  status: 'provisioning' | 'running' | 'stopped' | 'terminated';
  externalIP: string;
  sshCommand: string;
  estimatedCostPerHour: number;
  launchedAt: number;
}
```

### Cloud VM Dashboard Card

```
┌─ CLOUD COMPUTE ─────────────────────────────────────────────┐
│                                                              │
│  Active VMs: 1                      Budget: $45/$100 month  │
│                                                              │
│  ┌─ vertex-sim-01 ─────────────────────────────────────┐    │
│  │  Machine: a2-highgpu-1g (A100 80GB)                  │    │
│  │  Status: ● RUNNING        Uptime: 2h 34m             │    │
│  │  Cost: $3.67/hr           Running total: $9.42        │    │
│  │  Task: WGSL particle sim at 2M particles              │    │
│  │  [SSH] [Stop] [Extend 1hr] [View Logs]                │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Quick Launch:                                               │
│  [T4 ($0.35/hr)] [A100 ($3.67/hr)] [H100 ($6.98/hr)]       │
│                                                              │
│  ⚠ Auto-shutdown: All VMs stop after 4hr idle               │
└──────────────────────────────────────────────────────────────┘
```

---

## Google Drive Integration (30TB)

30TB is an enormous resource. The JOC uses it for:

1. **Project Backups** — Automated snapshots of all project directories
2. **Response Archive** — Every AI response ever received, searchable
3. **Asset Storage** — Generated images, videos, simulation outputs
4. **Model Artifacts** — Custom trained models, checkpoints, datasets
5. **Context Library** — Pre-compiled context bundles for common tasks

```typescript
interface DriveStorageDriver {
  /** Sync a local directory to Google Drive */
  syncToCloud(localPath: string, drivePath: string): Promise<SyncResult>;
  
  /** Pull files from Google Drive to local */
  syncFromCloud(drivePath: string, localPath: string): Promise<SyncResult>;
  
  /** Archive mission results */
  archiveMission(missionId: string): Promise<string>;  // Returns drive path
  
  /** Search across all stored content */
  search(query: string): Promise<DriveSearchResult[]>;
  
  /** Get storage usage breakdown */
  getUsage(): Promise<StorageUsage>;
}

interface StorageUsage {
  totalBytes: number;          // 30TB
  usedBytes: number;
  breakdown: {
    projects: number;
    responses: number;
    assets: number;
    models: number;
    other: number;
  };
}
```

### Storage Dashboard Card

```
┌─ STORAGE: Google Drive (30TB) ──────────────────────────────┐
│                                                              │
│  Used: ██░░░░░░░░░░░░░░░░░░ 4.2TB / 30TB (14%)            │
│                                                              │
│  ┌─ Breakdown ───────────────────────────────────────────┐  │
│  │  Projects    ████████████       2.1TB  (50%)          │  │
│  │  Assets      ████████           1.2TB  (29%)          │  │
│  │  Responses   ███                0.5TB  (12%)          │  │
│  │  Models      ██                 0.3TB  (7%)           │  │
│  │  Other       █                  0.1TB  (2%)           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Last backup: 15m ago  |  Next: in 45m                      │
│  [Sync Now] [Browse] [Search Archives]                      │
└──────────────────────────────────────────────────────────────┘
```

---

## The IDE-Grade UI Architecture

The JOC should feel like working inside a premium, purpose-built IDE. Not a web app. Not a dashboard. An **instrument of work** — the way VS Code or Cursor feels for coding, but for AI orchestration.

### What Makes an IDE Feel Like an IDE

1. **Panels that can split, stack, tab, and resize** — not fixed layout
2. **Command palette** (Ctrl+Shift+P) for instant access to any action
3. **Status bar** showing live system state
4. **Activity bar** (left sidebar icons) for major mode switching
5. **Explorer/sidebar** for browsing content hierarchies
6. **Editor area** as the central workspace — multi-tab, split-view
7. **Terminal/output panel** at the bottom for logs and output
8. **Breadcrumbs** for navigation context
9. **Keyboard-first** with discoverable shortcuts
10. **Theming** that's consistent and not fatiguing

### JOC IDE Layout

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  ◉ JOINT OPERATIONS CENTER                              ▪ ▪ ▪  ─  □  ✕         │
│  [File] [Mission] [Fleet] [Compute] [View] [Help]                               │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│  │                                                                               │
│  │  ┌─ TABS ─────────────────────────────────────────────────────────────────┐  │
│A │  │ [📊 Dashboard] [🌐 ChatGPT] [🌐 Gemini] [📋 Mission #42] [📦 Projects]│  │
│C │  └────────────────────────────────────────────────────────────────────────┘  │
│T │                                                                               │
│I │  ┌─────────────────────────────────────────┬──────────────────────────────┐  │
│V │  │                                         │                              │  │
│I │  │         MAIN EDITOR AREA                │     SIDE PANEL               │  │
│T │  │                                         │                              │  │
│Y │  │   (Dashboard / Session View /           │  (Properties / Details /     │  │
│  │  │    Mission Editor / Live Viewport /      │   Inspector / Context)       │  │
│B │  │    Project Explorer / Code View)         │                              │  │
│A │  │                                         │  ┌──────────────────────┐    │  │
│R │  │   Multi-pane with drag-to-split         │  │ INSPECTOR            │    │  │
│  │  │   Like VS Code editor groups            │  │                      │    │  │
│  │  │                                         │  │ Session: ChatGPT Pro │    │  │
│🗺 │  │                                         │  │ Health: ██████ 92%   │    │  │
│  │  │                                         │  │ Model: GPT-4o        │    │  │
│🌐 │  │                                         │  │ Quota: 150/300       │    │  │
│  │  │                                         │  │ Cookies: 23 (fresh)  │    │  │
│📋 │  │                                         │  │ Memory: 12 items     │    │  │
│  │  │                                         │  │                      │    │  │
│💬 │  │                                         │  │ [Inject] [Extract]   │    │  │
│  │  │                                         │  │ [Refresh] [Open]     │    │  │
│📦 │  │                                         │  └──────────────────────┘    │  │
│  │  │                                         │                              │  │
│🖥 │  │                                         │                              │  │
│  │  │                                         │                              │  │
│⚙ │  │                                         │                              │  │
│  │  └─────────────────────────────────────────┴──────────────────────────────┘  │
│  │                                                                               │
│  │  ┌─ BOTTOM PANEL ────────────────────────────────────────────────────────┐   │
│  │  │ [Agent Comms] [Output Log] [Mission Queue] [Resource Monitor]         │   │
│  │  │                                                                        │   │
│  │  │ 09:45 Aether → All: "Starting Phase 3 of capsule system"              │   │
│  │  │ 09:44 Codex2 → Aether: "Tests passing, 47/47"                         │   │
│  │  │ 09:42 Opus → Aether: "JOC design docs ready for review"               │   │
│  │  │ 09:40 Mission #42: ChatGPT response extracted (3.2K tokens)           │   │
│  │  │                                                                        │   │
│  │  │ [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] Message all agents...             │   │
│  │  └────────────────────────────────────────────────────────────────────────┘   │
│  │                                                                               │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│  ● 4 AIs active  │  ▲ 2 missions running  │  GPU: 38%  │  Drive: 4.2/30 TB     │
│  ● MCP: connected │  Agents: 4 online      │  Mem: 12GB │  ⌘⇧P Command Palette  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Activity Bar (Left Sidebar Icons)

| Icon | View | Purpose |
|------|------|---------|
| 🗺️ | **Dashboard** | Operations overview — fleet status, active missions, agent comms |
| 🌐 | **Sessions** | AI fleet management — session cards, health, viewport |
| 📋 | **Missions** | Mission composer, history, results |
| 💬 | **Comms** | Full agent communications hub — MCP message bus |
| 📦 | **Projects** | Project catalog — the living index of all your work |
| 🖥️ | **Compute** | Resource monitor — local GPU, cloud VMs, storage |
| ⚙️ | **Settings** | System config, driver management, API keys |

### Editor Area: Multi-Pane, Multi-Tab

Like VS Code, the central editor area supports:

- **Tabs** — multiple views open simultaneously
- **Split panes** — drag tab to side/bottom to create split view
- **Tab types** — each opens a different kind of view:

| Tab Type | Content | Interaction |
|----------|---------|-------------|
| Dashboard tab | Live ops overview | Read-only, auto-updating |
| Session tab | Full AI session with live viewport | Inject prompts, extract responses |
| Mission tab | Mission composer/results | Edit prompt, choose targets, view results |
| Viewport tab | Live browser view of an AI session | Watch AI typing in real-time |
| Project tab | Project details, file tree, status | Browse, launch, archive |
| Code tab | Syntax-highlighted file viewer | Read-only preview of project files |
| Diff tab | Multi-AI response comparison | Side-by-side with highlighting |
| Terminal tab | Direct shell/CLI access | Run commands, manage processes |

### Command Palette (Ctrl+Shift+P)

The power user's shortcut to everything:

```
┌─ Command Palette ────────────────────────────────────────────┐
│  > _                                                          │
│                                                               │
│  Recently Used:                                               │
│  ├─ Dispatch Mission to All AIs                               │
│  ├─ Check ChatGPT Session Health                              │
│  └─ Open Project: Pool Ocean                                  │
│                                                               │
│  > "dispatch"                                                 │
│  ├─ 📋 New Mission: Quick Dispatch                           │
│  ├─ 📋 New Mission: Full Composer                             │
│  ├─ 📋 Re-dispatch Last Mission                               │
│  ├─ 📋 Dispatch to Gemini CLI (batch)                         │
│  └─ 📋 Dispatch to Local GPU                                  │
│                                                               │
│  > "session"                                                  │
│  ├─ 🌐 Refresh All Sessions                                  │
│  ├─ 🌐 Open ChatGPT Session                                  │
│  ├─ 🌐 Open Gemini Session                                    │
│  ├─ 🌐 Session Health Check (all)                             │
│  └─ 🌐 Export Session Cookies                                 │
│                                                               │
│  > "compute"                                                  │
│  ├─ 🖥️ Launch Vertex VM (T4)                                 │
│  ├─ 🖥️ Launch Vertex VM (A100)                                │
│  ├─ 🖥️ Stop All VMs                                           │
│  ├─ 🖥️ Load Local Model (Ollama)                              │
│  └─ 🖥️ GPU Status                                             │
│                                                               │
│  > "project"                                                  │
│  ├─ 📦 Open Project by Name                                  │
│  ├─ 📦 List Active Projects                                   │
│  ├─ 📦 List Dormant Projects                                  │
│  ├─ 📦 Backup All to Drive                                    │
│  └─ 📦 Kill Orphan Dev Servers                                │
└───────────────────────────────────────────────────────────────┘
```

### Status Bar

The status bar is always visible at the bottom, showing **live system state at a glance**:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ● 4 AIs active │ ▲ 2 missions │ GPU: 38% 62°C │ Drive: 4.2/30TB │ MCP: ✓  │
│ Agents: Aether ● Codex1 ● Codex2 ● Opus ●  │ ⌘⇧P │ Ln 1, Col 1          │
└──────────────────────────────────────────────────────────────────────────────┘
```

Each segment is clickable:
- **4 AIs active** → Opens Sessions view
- **2 missions** → Opens Missions view
- **GPU: 38%** → Opens Compute view
- **Drive: 4.2/30TB** → Opens Storage browser
- **MCP: ✓** → Shows MCP connection status
- **Agent names** → Opens that agent's message history
- **⌘⇧P** → Opens command palette

---

## Keyboard Shortcuts

Following IDE conventions for muscle memory:

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+N` | New Mission |
| `Ctrl+Enter` | Dispatch current mission |
| `Ctrl+1/2/3/4` | Switch to editor group 1/2/3/4 |
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+J` | Toggle bottom panel |
| `Ctrl+\` | Split editor |
| `Ctrl+W` | Close current tab |
| `Ctrl+Tab` | Switch tabs |
| `Ctrl+Shift+E` | Focus Sessions view |
| `Ctrl+Shift+M` | Focus Missions view |
| `Ctrl+Shift+C` | Focus Comms panel |
| `F5` | Refresh all AI sessions |
| `F6` | Run health check on all |
| `Escape` | Close command palette / cancel dispatch |

---

## The Resource Monitor View

The Compute view brings all hardware into one coherent view:

```
┌─ COMPUTE FABRIC ────────────────────────────────────────────────────────────┐
│                                                                              │
│  ┌─ LOCAL ───────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  ┌─ CPU ──────────────┐  ┌─ GPU: 3050 Ti ────────┐  ┌─ RAM ───────┐│  │
│  │  │ ████████░░░░ 62%   │  │ ██████░░░░░░░░ 38%    │  │ ████████░░  ││  │
│  │  │ Cores: 12/12       │  │ VRAM: 3.1/4.0 GB      │  │ 12/16 GB   ││  │
│  │  │ Temp: 58°C         │  │ Temp: 62°C             │  │            ││  │
│  │  │                    │  │ Model: phi-3-mini       │  │            ││  │
│  │  └────────────────────┘  └────────────────────────┘  └────────────┘│  │
│  │                                                                       │  │
│  │  ┌─ Network ──────────────────────┐  ┌─ Active Processes ──────────┐│  │
│  │  │ ↓ 45 Mbps   ↑ 12 Mbps         │  │ 4 browser instances         ││  │
│  │  │ Latency: 23ms (to Google)      │  │ 1 ollama server             ││  │
│  │  └────────────────────────────────┘  │ 3 dev servers (ports used)  ││  │
│  │                                       │ 1 MCP server                ││  │
│  │                                       └────────────────────────────┘│  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ CLOUD ──────────────────────────────────────────────────────────────┐   │
│  │                                                                       │  │
│  │  Vertex AI                                  Month Budget: $45/$100   │  │
│  │  ├─ vertex-sim-01 (A100)  ● RUNNING   $9.42  [Stop] [SSH]           │  │
│  │  └─ No other VMs                                                      │  │
│  │                                                                       │  │
│  │  NVIDIA Cloud                                                         │  │
│  │  └─ No active instances                        [Launch H100]         │  │
│  │                                                                       │  │
│  │  Google Drive                                                         │  │
│  │  └─ ██░░░░░░░░░░░░░░░░░░ 4.2TB / 30TB         [Browse] [Sync]      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ API QUOTA ──────────────────────────────────────────────────────────┐   │
│  │  Gemini API:     ████████████████████ 0 / ∞ (Ultra)    [Test]       │  │
│  │  OpenAI API:     ████████████░░░░░░░ $8.40 / $50       [Test]       │  │
│  │  Anthropic API:  ██████████████░░░░░ $12.20 / $100     [Test]       │  │
│  └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Design Philosophy Summary

The JOC IDE follows these principles, synthesized from the Opus Canon:

1. **Visual instruments, not data entry** — Resource usage is bars and colors, not numbers in a table. Mission progress is visual, not percentual.

2. **Direct manipulation** — Drag to reorder mission priority. Click to dispatch. Drag-split to create dual pane views. Everything responds to gesture.

3. **IDE conventions** — Activity bar, editor tabs, split panes, command palette, status bar, keyboard shortcuts. If you know VS Code, you know JOC.

4. **Live, not static** — Agent comms stream in. Session health updates in real-time. GPU metrics animate. Mission progress bars fill. Nothing requires manual refresh.

5. **Three-ring compute** — Work flows to the cheapest/fastest ring first (browser subscriptions you already pay for), escalates to API/CLI for speed, and to cloud for power. No wasted resources.

6. **Canon dark theme** — `#0a0a15` deep, `#1a1a2e` surface, `#00d4ff` accent, `#e0e0e0` text. Consistent, not fatiguing, premium.

7. **Launcher canon compliance** — Every process the JOC starts has a documented way to stop. No orphan processes. One window = one context.

---

*Expanding the vision from browser hub to compute cockpit,*  
*Claude Opus 4.6 💙*
