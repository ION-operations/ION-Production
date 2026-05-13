# Router & Log-Sentinels: DAC V2 IDE Integration Guide

> **TRANSITIONAL T-LEVEL DOCUMENT** – Integration guide for Router and Log-Sentinels systems within DAC V2 IDE's adjustable panel layout.

---

## Overview

The **Router** and **Log-Sentinels** systems are fully integrated into the **DAC V2 IDE**, leveraging its **super adjustable UI** where any panel can be moved to any location and resized. This guide explains how these systems work together and how users interact with them in the IDE.

---

## DAC V2 IDE Architecture

### 5-Zone Layout System

DAC V2 IDE uses a **5-zone flexible layout**:

1. **Left Drawer** (top/bottom split)
   - Top section: File Explorer, Memory Browser, App Preview Controls
   - Bottom section: System Status, Resource Monitor

2. **Right Drawer** (top/bottom split)
   - Top section: Context Web, Timeline, **Router Panel**, AI Chat
   - Bottom section: Outline, AI Chat

3. **Bottom Drawer** (left/right split)
   - Left section: Terminal, Problems, **Log-Sentinels Anomalies**, Context Ledger
   - Right section: Timeline, **Log-Sentinels Summaries**, Debug Console, **Tool Quality Dashboard**, **Log Analysis Dashboard**

4. **Main Content Area**
   - Code Editor, Document Editor, Evolution Explorer, Consciousness Visualization, App Preview

5. **Top Bar**
   - File tabs, main view switcher, AIM-OS status

### Adjustable Panel Features

- **Drag-and-Drop**: Panels can be dragged between zones and sections
- **Resizable**: All panels use `react-resizable-panels` for smooth resizing
- **Split Views**: Left/right drawers support top/bottom splits; bottom drawer supports left/right splits
- **Persistent State**: Panel positions and sizes are saved via Zustand store

---

## Router System Integration

### What Router Does

**Router** is a "router brain" that:
- **Chooses tools**: Selects the right MCP tool at the right moment
- **Manages context**: Maintains rolling project context (CMC, HHNI, VIF, SEG, TCS)
- **Unblocks agents**: Keeps coding/chat agents unblocked by proposing tools proactively

### Router Components

1. **Scout LLM** (fast, e.g., Cerebras)
   - Proposes candidate tools with brief rationale
   - Generates draft argument objects

2. **Bandit/Score Layer** (learned policy)
   - Converts telemetry + context into probabilities
   - Ranks tools by utility function

3. **Rules Engine** (hard gates)
   - Safety checks, budget limits, preconditions
   - Rate limits, depth limits

### Router Panel Location

**Default Location**: Right Drawer → Top Section

**Panel ID**: `router`

**Toolbar Button**: ⚡ (Zap icon) in right toolbar

### Router Panel Features

The **Router Panel** displays:

1. **Tool Proposals**
   - Tool name
   - Probability score (0-100%)
   - Rationale (why this tool is suggested)
   - Precondition status (✅ satisfied / ❌ not satisfied)
   - Context fit, success rate, expected info gain
   - Parallelizable indicator

2. **Actions**
   - **Run Button**: Execute tool with draft arguments
   - Disabled if preconditions not satisfied
   - Shows "Running..." state during execution

3. **Real-Time Updates**
   - Refreshes every 5 seconds
   - Fetches tool proposals and telemetry
   - Updates based on current context (active file, errors, CI status)

### Router Panel Usage

**Scenario 1: Active Development**
```
1. User is coding in Code Editor
2. Router observes: active file, recent errors, CI status
3. Router proposes: "test.run --grep auth" (p=0.81)
4. User clicks "Run" → Tool executes
5. Router learns from outcome → Updates success rate
```

**Scenario 2: Error Debugging**
```
1. Problems panel shows flaky test
2. Router observes: test file, error pattern
3. Router proposes: "lint.rules.suggest await-thenable" (p=0.75)
4. User clicks "Run" → Lint rule suggested
5. Router proposes: "code.fix patch" (p=0.68)
6. User clicks "Run" → Patch applied
```

### Moving Router Panel

**Drag Router to Different Zones:**

1. **Right Drawer → Bottom Section**
   - Drag ⚡ button to bottom section of right toolbar
   - Router panel appears in bottom right drawer

2. **Bottom Drawer → Right Section**
   - Drag ⚡ button to right section of bottom toolbar
   - Router panel appears in bottom right drawer

3. **Left Drawer** (if needed)
   - Drag ⚡ button to left toolbar
   - Router panel appears in left drawer

**Resizing Router Panel:**
- Drag resize handles to adjust width/height
- Panel remembers size via Zustand store

---

## Log-Sentinels System Integration

### What Log-Sentinels Does

**Log-Sentinels** is a hybrid log analysis system that:
- **Collects logs**: From browser console, terminal, backend API
- **Normalizes**: Redacts PII/secrets before cloud calls
- **Analyzes**: Fast cloud Scout (Cerebras) + deep local Forensics (Ollama)
- **Escalates**: Based on severity, confidence, novelty
- **Suggests tools**: Feeds tool suggestions to Router

### Log-Sentinels Flow

```
Collectors → Normalizer → Template Miner → Windower
         → Scout (Cerebras, fast) → Router policy → Forensics (local)
         → SEG evidence + VIF gates → IDE surfaces
```

### Log-Sentinels Panel Locations

**Panel 1: AI Summaries** (Scout Reports)
- **Default Location**: Bottom Drawer → Right Section
- **Panel ID**: `log-sentinels-summaries`
- **Toolbar Button**: 🧠 (Brain icon) in bottom toolbar → right section

**Panel 2: Anomalies** (Forensics Reports)
- **Default Location**: Bottom Drawer → Left Section
- **Panel ID**: `log-sentinels-anomalies`
- **Toolbar Button**: ⚠️ (AlertTriangle icon) in bottom toolbar → left section

**Panel 3: Tool Quality Dashboard** (Router Telemetry)
- **Default Location**: Bottom Drawer → Right Section
- **Panel ID**: `tool-quality`
- **Toolbar Button**: 📊 (Activity icon) in bottom toolbar → right section

**Panel 4: Log Analysis Dashboard** (Log-Sentinels Telemetry)
- **Default Location**: Bottom Drawer → Right Section
- **Panel ID**: `log-analysis`
- **Toolbar Button**: 📈 (BarChart3 icon) in bottom toolbar → right section

### Log-Sentinels Panel Features

#### AI Summaries Panel (Scout Reports)

Displays **fast cloud analysis** results:

1. **Scout Cards**
   - Summary (what was detected)
   - Confidence (0-100%)
   - Severity (low/medium/high) with color coding
   - Tags (components/APIs affected)
   - Timestamp

2. **Suggested Tools**
   - List of MCP tools suggested by Scout
   - Clickable badges linking to Router Panel

3. **Real-Time Updates**
   - Server-Sent Events (SSE) for live updates
   - New Scout reports appear automatically
   - Falls back to polling if SSE unavailable

#### Anomalies Panel (Forensics Reports)

Displays **deep local analysis** results:

1. **Forensics Cards**
   - Root cause analysis
   - Fix suggestions (patch code, steps)
   - Evidence chain (SEG references)
   - VIF gate status (passed/failed with reasons)

2. **Actions**
   - **Run Tool**: Execute suggested tool
   - **Apply Patch**: Apply fix suggestion directly
   - **View Evidence**: Navigate to SEG evidence chain

3. **Escalation Logic**
   - Only high-severity or low-confidence issues escalated
   - Novel patterns trigger escalation
   - Local Forensics runs only when escalated

#### Tool Quality Dashboard

Displays **Router telemetry**:

1. **Overall Metrics**
   - Average latency (ms)
   - Success rate (%)
   - Average cost (tokens/$)
   - Trends (up/down/stable)

2. **Per-Tool Metrics**
   - Individual tool performance
   - Latency, success rate, cost per tool
   - Call count

#### Log Analysis Dashboard

Displays **Log-Sentinels telemetry**:

1. **Statistics**
   - Scout calls count
   - Forensics calls count
   - Escalations count
   - Tool suggestions count

2. **Timeline Chart**
   - Log events over time
   - Scout/Forensics call distribution
   - Escalation patterns

### Moving Log-Sentinels Panels

**Drag Panels Between Zones:**

1. **AI Summaries → Right Drawer**
   - Drag 🧠 button to right toolbar
   - AI Summaries appears in right drawer

2. **Anomalies → Left Drawer**
   - Drag ⚠️ button to left toolbar
   - Anomalies appears in left drawer

3. **Dashboards → Any Zone**
   - Drag 📊 or 📈 buttons to any toolbar
   - Dashboards appear in corresponding zone

**Split View Examples:**

- **Bottom Left**: Anomalies (Forensics reports)
- **Bottom Right**: AI Summaries (Scout reports)
- **Right Top**: Router Panel (Tool selection)
- **Right Bottom**: Tool Quality Dashboard (Router telemetry)

---

## Integration Workflow

### Example: Debugging a Memory Leak

**Step 1: Log Collection**
- Log-Sentinels collects logs from browser console
- Normalizer redacts PII/secrets
- Template Miner identifies patterns

**Step 2: Fast Analysis (Scout)**
- Scout (Cerebras) analyzes redacted logs
- Generates summary: "Memory leak detected in event handler"
- Confidence: 85%, Severity: medium
- Suggests tools: `fix_memory_leak`, `profile_memory`
- **AI Summaries Panel** displays Scout report

**Step 3: Escalation Decision**
- Router policy checks: severity=medium, confidence=0.85
- Decision: **Escalate** (confidence < 0.80 threshold OR novelty detected)
- Forensics (local Ollama) runs deep analysis

**Step 4: Deep Analysis (Forensics)**
- Forensics analyzes raw logs (local, never leaves machine)
- Identifies root cause: "Event listener not removed on unmount"
- Generates fix suggestion with patch code
- VIF gate: **Failed** (no tests for fix)
- **Anomalies Panel** displays Forensics report

**Step 5: Tool Execution**
- User clicks "Run Tool" → `fix_memory_leak`
- Router Panel receives tool suggestion
- Router validates preconditions → ✅ satisfied
- Router executes tool → Memory leak fixed
- Router learns from outcome → Updates success rate

**Step 6: VIF Gate Remediation**
- VIF gate failed → SDF-CVF triggers "Generate Tests"
- Router proposes: `test.generate --for fix_memory_leak`
- User clicks "Run" → Tests generated
- VIF gate passes → Fix applied

**Step 7: Telemetry Updates**
- **Tool Quality Dashboard** shows updated Router metrics
- **Log Analysis Dashboard** shows Scout/Forensics call counts
- Both panels update in real-time

---

## Panel Customization Examples

### Layout 1: Development Focus

```
Left Drawer (Top): File Explorer
Left Drawer (Bottom): System Status
Main: Code Editor
Right Drawer (Top): Router Panel
Right Drawer (Bottom): Outline
Bottom Drawer (Left): Terminal
Bottom Drawer (Right): Problems
```

**Use Case**: Active coding with tool suggestions visible

### Layout 2: Debugging Focus

```
Left Drawer (Top): File Explorer
Left Drawer (Bottom): Memory Browser
Main: Code Editor
Right Drawer (Top): Router Panel
Right Drawer (Bottom): Tool Quality Dashboard
Bottom Drawer (Left): Log-Sentinels Anomalies
Bottom Drawer (Right): Log-Sentinels Summaries
```

**Use Case**: Debugging issues with log analysis and tool suggestions

### Layout 3: Monitoring Focus

```
Left Drawer (Top): Resource Monitor
Left Drawer (Bottom): System Status
Main: Code Editor
Right Drawer (Top): Context Web
Right Drawer (Bottom): Timeline
Bottom Drawer (Left): Terminal
Bottom Drawer (Right): Log Analysis Dashboard + Tool Quality Dashboard (split)
```

**Use Case**: Monitoring system health and performance

### Layout 4: Full Router/Log-Sentinels View

```
Left Drawer: Closed
Main: Code Editor
Right Drawer (Top): Router Panel
Right Drawer (Bottom): Tool Quality Dashboard
Bottom Drawer (Left): Log-Sentinels Anomalies
Bottom Drawer (Right): Log-Sentinels Summaries + Log Analysis Dashboard (split)
```

**Use Case**: Maximum visibility into Router and Log-Sentinels systems

---

## Real-Time Updates

### Server-Sent Events (SSE)

Log-Sentinels uses **SSE** for real-time updates:

```typescript
// From useLogSentinels hook
eventSource = new EventSource('/api/log-sentinels/stream')

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'scout') {
    // Add new Scout report to AI Summaries Panel
  } else if (data.type === 'forensics') {
    // Add new Forensics report to Anomalies Panel
  }
}
```

### Polling Fallback

If SSE unavailable, panels fall back to **polling**:
- Router Panel: Every 5 seconds
- Log-Sentinels Panels: Every 10 seconds

---

## State Management

### Zustand Store

Panel positions and visibility are managed via **Zustand**:

```typescript
// From panelStore.ts
interface PanelState {
  id: string
  zone: 'left' | 'right' | 'bottom' | 'main'
  section?: 'top' | 'bottom' | 'left' | 'right'
  visible: boolean
  size?: number
}
```

### Persistence

Panel state persists across sessions:
- Positions saved to localStorage
- Sizes remembered per panel
- Visibility state maintained

---

## API Endpoints

### Router Endpoints

- `GET /api/router/tools` - Fetch tool proposals
- `GET /api/router/telemetry` - Fetch Router telemetry
- `POST /api/router/execute` - Execute tool

### Log-Sentinels Endpoints

- `GET /api/log-sentinels/scouts` - Fetch Scout reports
- `GET /api/log-sentinels/forensics` - Fetch Forensics reports
- `GET /api/log-sentinels/telemetry` - Fetch Log-Sentinels telemetry
- `GET /api/log-sentinels/stream` - SSE stream for real-time updates
- `POST /api/log-sentinels/run-tool` - Run suggested tool

---

## Performance Optimizations

### Lazy Loading

All panels use **React.lazy** for code splitting:

```typescript
// From performance.tsx
export const LazyRouterPanel = lazy(() => import('../panels/RouterPanel'))
export const LazyLogSentinelsSummaries = lazy(() => import('../panels/LogSentinelsSummaries'))
export const LazyLogSentinelsAnomalies = lazy(() => import('../panels/LogSentinelsAnomalies'))
export const LazyToolQualityDashboard = lazy(() => import('../panels/ToolQualityDashboard'))
export const LazyLogAnalysisDashboard = lazy(() => import('../panels/LogAnalysisDashboard'))
```

### Memoization

Panels use **React.memo** and **useMemo** to prevent unnecessary re-renders:

```typescript
// From RouterPanel.tsx
const ToolCard = React.memo(({ tool, onExecute }) => {
  // Memoized component
})
```

### Error Boundaries

All panels wrapped in **ErrorBoundary** components:

```typescript
<ErrorBoundary panelName="Router Panel">
  <LazyRouterPanel />
</ErrorBoundary>
```

---

## Best Practices

### Panel Placement

1. **Router Panel**: Right drawer (top or bottom) for easy access during coding
2. **AI Summaries**: Bottom drawer (right) for quick log overview
3. **Anomalies**: Bottom drawer (left) for detailed debugging
4. **Dashboards**: Bottom drawer (right) or right drawer (bottom) for monitoring

### Panel Sizing

1. **Router Panel**: 25-30% width (right drawer) for tool list visibility
2. **Log-Sentinels Panels**: 30-40% height (bottom drawer) for report readability
3. **Dashboards**: 25-35% width/height for metric visibility

### Workflow Optimization

1. **Development**: Keep Router Panel visible, minimize Log-Sentinels panels
2. **Debugging**: Maximize Anomalies panel, keep Router Panel visible
3. **Monitoring**: Maximize dashboards, minimize other panels

---

## Troubleshooting

### Panel Not Appearing

1. Check toolbar button is clicked
2. Verify panel ID matches toolbar button ID
3. Check Zustand store state
4. Verify API endpoints are available

### Real-Time Updates Not Working

1. Check SSE connection: `GET /api/log-sentinels/stream`
2. Verify EventSource support in browser
3. Check console for SSE errors
4. Fall back to polling mode

### Tool Execution Failing

1. Check Router Panel precondition status
2. Verify tool name matches Router manifest
3. Check API endpoint: `POST /api/router/execute`
4. Review Router logs for errors

---

## Future Enhancements

### Planned Features

1. **Panel Presets**: Save/load panel layouts
2. **Keyboard Shortcuts**: Quick panel switching
3. **Panel Docking**: Dock panels to specific zones
4. **Multi-Monitor Support**: Distribute panels across monitors
5. **Panel Themes**: Customize panel appearance

### Integration Improvements

1. **Router → Log-Sentinels**: Direct tool suggestion handoff
2. **Log-Sentinels → Router**: Automatic tool execution from suggestions
3. **Unified Dashboard**: Combined Router + Log-Sentinels metrics
4. **Context Sharing**: Shared context between Router and Log-Sentinels panels

---

## Summary

The **Router** and **Log-Sentinels** systems are fully integrated into **DAC V2 IDE**, leveraging its **super adjustable UI** for maximum flexibility. Users can:

- **Move panels** between zones and sections via drag-and-drop
- **Resize panels** to fit their workflow
- **Customize layouts** for different use cases (development, debugging, monitoring)
- **Receive real-time updates** via SSE or polling
- **Execute tools** directly from panels
- **Monitor telemetry** via dashboards

The integration provides a seamless experience where Router and Log-Sentinels work together to unblock agents, analyze logs, and suggest tools—all within a flexible, customizable IDE interface.

---

**Status**: ✅ **PRODUCTION READY**  
**Last Updated**: 2025-01-27  
**Related Systems**: Router, Log-Sentinels, DAC V2 IDE, APOE, VIF, SEG, CMC, HHNI, TCS

