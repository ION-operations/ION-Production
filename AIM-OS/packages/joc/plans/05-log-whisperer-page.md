# 05 — Log Whisperer Page (Deep Plan)

> **AI-powered log analysis, port monitoring, and process visibility.**  
> "Need to easily see ports and what apps are running or stuck."

---

## What This Page Does

A live operations dashboard that combines:
1. **AI-powered log analysis** — semantic search, anomaly detection, pattern recognition
2. **Port monitor** — which ports are in use, by what process
3. **Process supervisor** — running apps, health status, restart controls
4. **Log Sentinels** — DAC's concept of intelligent log watchers that detect issues proactively

---

## Architecture

### Primary View: Log Stream

Real-time scrolling log feed with filters:

| Control | Function |
|---------|----------|
| Source filter | Select which apps/services to show |
| Level filter | ERROR / WARN / INFO / DEBUG / TRACE |
| Semantic search | HHNI-powered natural language search across log entries |
| Time range | Show last 5m / 15m / 1h / custom |
| AI Whisper | Trigger local LLM or Cerebras to analyze visible logs and summarize |

Log entries show:
- Timestamp (relative + absolute on hover)
- Source (service name + PID)
- Level badge (color-coded)
- Message (with syntax highlighting for JSON/stack traces)
- AIM-OS metadata (if the log came from an AIM-OS service)

### Secondary View: Port Monitor

Table of active ports with process information:

| Port | Process | PID | Status | CPU% | Mem | Uptime | Actions |
|------|---------|-----|--------|------|-----|--------|---------|
| 3000 | joc-dev | 1234 | ✅ Running | 2.1% | 180MB | 2h 14m | [Restart] [Stop] [Logs] |
| 5001 | mcp-core | 2345 | ✅ Running | 0.5% | 95MB | 2h 14m | [Restart] [Stop] [Logs] |
| 5002 | mcp-browser | 3456 | ⚠️ High CPU | 45% | 312MB | 1h 03m | [Restart] [Stop] [Logs] |
| 8080 | -- | -- | 🔴 Available | -- | -- | -- | -- |

- Click a row → shows process details and recent logs filtered to that process
- Actions: restart, stop, view logs, open in terminal
- Status indicators: Running (green), High CPU (yellow), Crashed (red), Available (gray)
- Auto-refresh every 5 seconds

### Tertiary View: AI Analysis

"Whisper" mode — feed current log buffer to local LLM or Cerebras API:

| AI Feature | Source | Description |
|------------|--------|-------------|
| Anomaly Detection | CAS cognitive analysis | Detect unusual patterns, frequency spikes, new error types |
| Root Cause Analysis | HHNI semantic linkage | Given an error, trace back to likely root cause in log history |
| Trend Analysis | TCS timeline data | Show error frequency trends, predict issues |
| Summary | Cerebras or local LLM | Natural language summary of recent activity |

### Quaternary View: Log Sentinels (from DAC)

Configurable "watcher" rules:

```typescript
interface LogSentinel {
  id: string;
  name: string;           // "Memory Pressure Warning"
  pattern: string;        // regex or semantic query
  level: 'error' | 'warn' | 'info';
  source?: string;        // filter to specific service
  cooldown: number;       // seconds between re-fires
  action: SentinelAction; // notification, sound, auto-restart, escalate
  enabled: boolean;
}
```

Users can create sentinels like:
- "Alert me if MCP core stops responding for >30s"
- "Notify if any process exceeds 90% CPU"
- "Highlight all logs containing 'ECONNREFUSED'"
- "Summarize errors every 15 minutes"

---

## Left Drawer Contents (Page-Specific)

| Icon | Drawer | Content |
|------|--------|---------|
| 📡 | Sources | Log source list with toggles |
| 🔍 | Search | Semantic log search (HHNI) |
| 🤖 | AI Whisper | AI analysis controls and summary |
| 🏥 | Sentinels | Log sentinel manager |
| 📊 | Stats | Log volume, error rate, uptime charts |
| ⚙️ | Config | Log retention, AI model selection |

---

## Data Sources

| Feature | Source | Method |
|---------|--------|--------|
| Log streams | File watchers or stdout capture | WebSocket or polling |
| Port info | `netstat -tlnp` / `Get-NetTCPConnection` | Periodic polling (5s) |
| Process info | `ps aux` / `Get-Process` | Periodic polling (5s) |
| AI analysis | Cerebras API or local LLM | On-demand or scheduled |
| HHNI search | MCP `deepsearch` or `icip_search` | On-demand |

---

## Implementation Phases

### Phase 1: Log Stream View
- Scrolling log display with virtual scrolling (for performance with 10k+ entries)
- Level/source filters
- Time range selection
- JSON syntax highlighting

### Phase 2: Port + Process Monitor
- Port scan and display table
- Process health indicators
- Action buttons (restart, stop, inspect)
- Auto-refresh

### Phase 3: AI Whisper Integration
- "Analyze" button that sends visible logs to Cerebras
- Summary panel showing AI analysis
- Anomaly highlight overlay on log entries
- Root cause trace links

### Phase 4: Log Sentinels
- Sentinel creation UI
- Pattern (regex) and semantic (HHNI query) matching
- Sentinel status indicators
- Notification system integration
