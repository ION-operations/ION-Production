import * as vscode from 'vscode';
import { McpPoller } from '../services/mcpPoller';
import { BridgeMonitor } from '../services/bridgeMonitor';
import { DashboardState, WebviewToExtMessage } from '../types';

/**
 * Provides the Antigravity Console sidebar webview.
 * Orchestrates MCP polling, bridge monitoring, and message display.
 */
export class ConsoleViewProvider implements vscode.WebviewViewProvider {
    private view?: vscode.WebviewView;
    private readonly extensionUri: vscode.Uri;
    private readonly mcpPoller: McpPoller;
    private readonly bridgeMonitor: BridgeMonitor;

    constructor(extensionUri: vscode.Uri, _context: vscode.ExtensionContext) {
        this.extensionUri = extensionUri;
        this.mcpPoller = new McpPoller();

        const config = vscode.workspace.getConfiguration('antigravity');
        const bridgeUrl = config.get<string>('ghostBridgeUrl', 'http://192.168.2.25:9090');
        this.bridgeMonitor = new BridgeMonitor(bridgeUrl);
    }

    resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ): void {
        this.view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(this.extensionUri, 'media'),
                vscode.Uri.joinPath(this.extensionUri, 'resources')
            ]
        };

        webviewView.webview.html = this.getHtml(webviewView.webview);

        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(async (msg: WebviewToExtMessage) => {
            switch (msg.type) {
                case 'ready':
                    await this.refresh();
                    break;
                case 'refresh':
                    await this.refresh();
                    break;
                case 'sendMessage':
                    await this.sendAgentMessage(msg.to, msg.content);
                    break;
                case 'storeMemory':
                    await this.storeMemoryAtom(msg.content);
                    break;
                case 'checkGhost':
                    await this.checkGhost();
                    break;
            }
        });
    }

    /**
     * Refresh all dashboard data and push to webview.
     */
    async refresh(): Promise<void> {
        try {
            const [system, ghost, memory, messages] = await Promise.all([
                this.mcpPoller.pollSystemHealth(),
                this.bridgeMonitor.checkHealth(),
                this.mcpPoller.getMemoryPulse(),
                this.mcpPoller.getRecentMessages(8)
            ]);

            const state: DashboardState = {
                system, ghost, memory, messages,
                lastRefresh: new Date().toISOString()
            };

            this.postMessage({ type: 'updateDashboard', data: state });
        } catch (err) {
            this.postMessage({ type: 'showError', message: `Refresh failed: ${err}` });
        }
    }

    /**
     * Check ghost bridge status and update.
     */
    async checkGhost(): Promise<void> {
        const status = await this.bridgeMonitor.checkHealth();
        this.postMessage({ type: 'updateGhost', data: status });
        const emoji = status.bridgeHealthy ? '🟢' : '🔴';
        const latency = status.latencyMs ? `${status.latencyMs}ms` : 'n/a';
        vscode.window.showInformationMessage(`Victus Bridge: ${emoji} ${latency}`);
    }

    /**
     * Prompt user for a message to send to ghost/team.
     */
    async promptSendMessage(): Promise<void> {
        const to = await vscode.window.showInputBox({ prompt: 'Send to (e.g., ghost, sev, codex)', value: 'ghost' });
        if (!to) { return; }
        const content = await vscode.window.showInputBox({ prompt: 'Message content', placeHolder: 'Status update...' });
        if (!content) { return; }
        await this.sendAgentMessage(to, content);
    }

    /**
     * Prompt user for memory content to store.
     */
    async promptStoreMemory(): Promise<void> {
        const content = await vscode.window.showInputBox({ prompt: 'Memory to store', placeHolder: 'Key insight or milestone...' });
        if (!content) { return; }
        await this.storeMemoryAtom(content);
    }

    // --- Private helpers ---

    private async sendAgentMessage(to: string, content: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('antigravity');
        const from = config.get<string>('agentIdentity', 'opus-windows');

        // Try bridge first for ghost
        if (to.toLowerCase() === 'ghost' || to.toLowerCase().includes('linux')) {
            const ok = await this.bridgeMonitor.sendMessage(from, content);
            if (ok) {
                this.postMessage({ type: 'showInfo', message: `✓ Sent to Victus via bridge` });
                return;
            }
        }

        // Fallback: write to local message file
        try {
            const fs = await import('fs');
            const path = await import('path');
            const homeDir = process.env.USERPROFILE || process.env.HOME || '';
            const msgFile = path.join(homeDir, 'mcp_ai_messages.json');

            let data: { messages: Array<Record<string, unknown>> } = { messages: [] };
            if (fs.existsSync(msgFile)) {
                data = JSON.parse(fs.readFileSync(msgFile, 'utf-8'));
            }

            data.messages.push({
                from_ai: from, to_ai: to, content,
                message_type: 'discussion', priority: 'medium',
                timestamp: new Date().toISOString()
            });

            fs.writeFileSync(msgFile, JSON.stringify(data, null, 2));
            this.postMessage({ type: 'showInfo', message: `✓ Message stored for ${to}` });
        } catch (err) {
            this.postMessage({ type: 'showError', message: `Failed to send: ${err}` });
        }
    }

    private async storeMemoryAtom(content: string): Promise<void> {
        try {
            const fs = await import('fs');
            const path = await import('path');
            const crypto = await import('crypto');
            const homeDir = process.env.USERPROFILE || process.env.HOME || '';
            const memDir = path.join(homeDir, 'mcp_memory', 'atoms');

            if (!fs.existsSync(memDir)) { fs.mkdirSync(memDir, { recursive: true }); }

            const atomId = crypto.randomUUID();
            const atom = {
                id: atomId,
                content,
                modality: 'text',
                created_at: new Date().toISOString(),
                tags: { source: 'antigravity-extension', agent: 'opus' }
            };

            fs.writeFileSync(path.join(memDir, `${atomId}.json`), JSON.stringify(atom, null, 2));
            this.mcpPoller.recordMemoryStore();
            this.postMessage({ type: 'showInfo', message: `✓ Memory stored: ${atomId.substring(0, 8)}...` });
        } catch (err) {
            this.postMessage({ type: 'showError', message: `Store failed: ${err}` });
        }
    }

    private postMessage(msg: Record<string, unknown>): void {
        this.view?.webview.postMessage(msg);
    }

    /**
     * Generate the webview HTML. All styles and scripts inline for reliability.
     */
    private getHtml(_webview: vscode.Webview): string {
        return /*html*/`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';">
<title>Antigravity Console</title>
<style>
:root {
    --bg-primary: #0d1117;
    --bg-card: #161b22;
    --bg-card-hover: #1c2333;
    --border: #30363d;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-dim: #484f58;
    --accent-green: #3fb950;
    --accent-red: #f85149;
    --accent-amber: #d29922;
    --accent-blue: #58a6ff;
    --accent-purple: #bc8cff;
    --accent-cyan: #39d2c0;
    --radius: 6px;
    --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 12px;
    line-height: 1.5;
    padding: 8px;
}

/* Header */
.header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 10px;
}
.header .logo {
    width: 20px; height: 20px;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
    border-radius: 50%;
    flex-shrink: 0;
    animation: pulse 3s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.8; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}
.header h1 {
    font-size: 13px;
    font-weight: 600;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.header .last-refresh {
    margin-left: auto;
    font-size: 10px;
    color: var(--text-dim);
    font-family: var(--font-mono);
}

/* Cards */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 10px;
    margin-bottom: 8px;
    transition: border-color 0.2s, background 0.2s;
}
.card:hover { border-color: var(--accent-blue); background: var(--bg-card-hover); }
.card-title {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.card-title .icon { font-size: 12px; }

/* Status indicators */
.status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 3px 0;
    font-size: 11px;
}
.status-row .label { color: var(--text-secondary); }
.status-row .value { font-family: var(--font-mono); font-size: 11px; }
.dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 4px;
    vertical-align: middle;
}
.dot.green { background: var(--accent-green); box-shadow: 0 0 6px var(--accent-green); }
.dot.red { background: var(--accent-red); box-shadow: 0 0 6px var(--accent-red); }
.dot.amber { background: var(--accent-amber); box-shadow: 0 0 6px var(--accent-amber); }
.dot.blue { background: var(--accent-blue); }

/* Message list */
.msg-item {
    padding: 6px 8px;
    border-left: 2px solid var(--border);
    margin-bottom: 4px;
    font-size: 11px;
    transition: border-color 0.2s;
}
.msg-item:hover { border-left-color: var(--accent-cyan); }
.msg-from {
    font-weight: 600;
    color: var(--accent-cyan);
    font-family: var(--font-mono);
    font-size: 10px;
}
.msg-time {
    float: right;
    font-size: 9px;
    color: var(--text-dim);
    font-family: var(--font-mono);
}
.msg-content {
    color: var(--text-secondary);
    margin-top: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Actions */
.actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-top: 8px;
}
.btn {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    padding: 6px 10px;
    font-size: 11px;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s;
    font-family: inherit;
}
.btn:hover {
    border-color: var(--accent-blue);
    background: var(--bg-card-hover);
}
.btn.primary {
    background: linear-gradient(135deg, rgba(57,210,192,0.15), rgba(188,140,255,0.15));
    border-color: var(--accent-cyan);
}
.btn.primary:hover {
    background: linear-gradient(135deg, rgba(57,210,192,0.25), rgba(188,140,255,0.25));
}

/* Toast */
.toast {
    position: fixed;
    bottom: 8px;
    left: 8px;
    right: 8px;
    padding: 8px 12px;
    border-radius: var(--radius);
    font-size: 11px;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s;
    pointer-events: none;
    z-index: 100;
}
.toast.show { opacity: 1; transform: translateY(0); }
.toast.info { background: rgba(88,166,255,0.15); border: 1px solid var(--accent-blue); color: var(--accent-blue); }
.toast.error { background: rgba(248,81,73,0.15); border: 1px solid var(--accent-red); color: var(--accent-red); }

/* Loading */
.loading {
    text-align: center;
    padding: 30px;
    color: var(--text-dim);
}
.loading .spinner {
    display: inline-block;
    width: 20px; height: 20px;
    border: 2px solid var(--border);
    border-top-color: var(--accent-cyan);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
    <div class="header">
        <div class="logo"></div>
        <h1>Antigravity</h1>
        <span class="last-refresh" id="lastRefresh">--:--</span>
    </div>

    <div id="loading" class="loading">
        <div class="spinner"></div>
        <div style="margin-top:8px;">Connecting to MCP...</div>
    </div>

    <div id="dashboard" style="display:none;">
        <!-- System Health -->
        <div class="card" id="systemCard">
            <div class="card-title"><span class="icon">⚡</span> System Health</div>
            <div class="status-row">
                <span class="label">MCP</span>
                <span class="value" id="mcpStatus"><span class="dot green"></span>92 tools</span>
            </div>
            <div class="status-row">
                <span class="label">CMC</span>
                <span class="value" id="cmcStatus"><span class="dot green"></span>-- atoms</span>
            </div>
            <div class="status-row">
                <span class="label">HHNI</span>
                <span class="value" id="hhniStatus"><span class="dot amber"></span>index down</span>
            </div>
            <div class="status-row">
                <span class="label">VIF</span>
                <span class="value" id="vifStatus"><span class="dot green"></span>kappa active</span>
            </div>
        </div>

        <!-- Ghost Status -->
        <div class="card" id="ghostCard">
            <div class="card-title"><span class="icon">👻</span> Victus (Ghost)</div>
            <div class="status-row">
                <span class="label">Bridge</span>
                <span class="value" id="bridgeStatus"><span class="dot red"></span>checking...</span>
            </div>
            <div class="status-row">
                <span class="label">Latency</span>
                <span class="value" id="bridgeLatency">--</span>
            </div>
            <div class="status-row">
                <span class="label">Last msg</span>
                <span class="value" id="lastMsg">--</span>
            </div>
            <div class="status-row">
                <span class="label">Unread</span>
                <span class="value" id="unreadCount">0</span>
            </div>
        </div>

        <!-- Memory Pulse -->
        <div class="card" id="memoryCard">
            <div class="card-title"><span class="icon">🧠</span> Memory Pulse</div>
            <div class="status-row">
                <span class="label">Total atoms</span>
                <span class="value" id="totalAtoms">--</span>
            </div>
            <div class="status-row">
                <span class="label">Session</span>
                <span class="value" id="sessionAtoms">0 new</span>
            </div>
            <div class="status-row">
                <span class="label">Last store</span>
                <span class="value" id="lastStore">--</span>
            </div>
            <div class="status-row">
                <span class="label">Confidence</span>
                <span class="value" id="lastConfidence">--</span>
            </div>
        </div>

        <!-- Messages -->
        <div class="card" id="messagesCard">
            <div class="card-title"><span class="icon">💬</span> Recent Messages</div>
            <div id="messageList">
                <div style="color:var(--text-dim);font-size:11px;">No messages yet</div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="actions">
            <button class="btn primary" onclick="doRefresh()">↻ Refresh</button>
            <button class="btn" onclick="doCheckGhost()">📡 Ghost</button>
            <button class="btn" onclick="doSendMessage()">✉ Message</button>
            <button class="btn" onclick="doStoreMemory()">💾 Memory</button>
        </div>
    </div>

    <div class="toast" id="toast"></div>

<script>
const vscode = acquireVsCodeApi();

// Signal ready
vscode.postMessage({ type: 'ready' });

// Handle messages from extension host
window.addEventListener('message', (event) => {
    const msg = event.data;
    switch (msg.type) {
        case 'updateDashboard': renderDashboard(msg.data); break;
        case 'updateGhost': renderGhost(msg.data); break;
        case 'updateMessages': renderMessages(msg.data); break;
        case 'showError': showToast(msg.message, 'error'); break;
        case 'showInfo': showToast(msg.message, 'info'); break;
    }
});

function renderDashboard(state) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';

    // Last refresh
    const t = new Date(state.lastRefresh);
    document.getElementById('lastRefresh').textContent =
        t.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

    // System health
    const sys = state.system;
    setStatus('mcpStatus', sys.mcp.status === 'online' ? 'green' : 'red',
        sys.mcp.status === 'online' ? sys.mcp.toolCount + ' tools' : 'offline');
    setStatus('cmcStatus', sys.cmc.status === 'online' ? 'green' : 'red',
        sys.cmc.atomCount + ' atoms');
    setStatus('hhniStatus', sys.hhni.indexAvailable ? 'green' : 'amber',
        sys.hhni.indexAvailable ? 'index active' : 'index down');
    setStatus('vifStatus', sys.vif.kappaGateAvailable ? 'green' : 'red',
        sys.vif.kappaGateAvailable ? 'kappa active' : 'offline');

    // Ghost
    renderGhost(state.ghost);

    // Memory
    const mem = state.memory;
    document.getElementById('totalAtoms').textContent = mem.totalAtoms.toString();
    document.getElementById('sessionAtoms').textContent = mem.sessionAtoms + ' new';
    document.getElementById('lastStore').textContent = mem.lastStoreTime ?
        timeAgo(new Date(mem.lastStoreTime)) : '--';
    document.getElementById('lastConfidence').textContent = mem.lastConfidence !== null ?
        mem.lastConfidence.toFixed(2) : '--';

    // Messages
    renderMessages(state.messages);
}

function renderGhost(ghost) {
    setStatus('bridgeStatus', ghost.bridgeHealthy ? 'green' : 'red',
        ghost.bridgeHealthy ? 'healthy' : 'unreachable');
    document.getElementById('bridgeLatency').textContent =
        ghost.latencyMs !== null ? ghost.latencyMs + 'ms' : '--';
    document.getElementById('lastMsg').textContent =
        ghost.lastMessageTimestamp ? timeAgo(new Date(ghost.lastMessageTimestamp)) : '--';
    document.getElementById('unreadCount').textContent = ghost.unreadCount.toString();
}

function renderMessages(messages) {
    const list = document.getElementById('messageList');
    if (!messages || messages.length === 0) {
        list.innerHTML = '<div style="color:var(--text-dim);font-size:11px;">No messages</div>';
        return;
    }
    list.innerHTML = messages.map(m => {
        const time = m.timestamp ? timeAgo(new Date(m.timestamp)) : '';
        const preview = m.content.length > 80 ? m.content.substring(0, 80) + '…' : m.content;
        return '<div class="msg-item">' +
            '<span class="msg-from">' + escHtml(m.from) + '</span>' +
            '<span class="msg-time">' + time + '</span>' +
            '<div class="msg-content">' + escHtml(preview) + '</div>' +
            '</div>';
    }).join('');
}

function setStatus(id, color, text) {
    document.getElementById(id).innerHTML =
        '<span class="dot ' + color + '"></span>' + escHtml(text);
}

function timeAgo(date) {
    const sec = Math.floor((Date.now() - date.getTime()) / 1000);
    if (sec < 60) return sec + 's ago';
    if (sec < 3600) return Math.floor(sec / 60) + 'm ago';
    if (sec < 86400) return Math.floor(sec / 3600) + 'h ago';
    return Math.floor(sec / 86400) + 'd ago';
}

function escHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showToast(msg, type) {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = 'toast ' + type + ' show';
    setTimeout(() => { el.className = 'toast'; }, 3000);
}

// Quick actions
function doRefresh() { vscode.postMessage({ type: 'refresh' }); }
function doCheckGhost() { vscode.postMessage({ type: 'checkGhost' }); }

function doSendMessage() {
    const to = prompt('Send to (ghost, sev, codex):');
    if (!to) return;
    const content = prompt('Message:');
    if (!content) return;
    vscode.postMessage({ type: 'sendMessage', to, content });
}

function doStoreMemory() {
    const content = prompt('Memory to store:');
    if (!content) return;
    vscode.postMessage({ type: 'storeMemory', content });
}
</script>
</body>
</html>`;
    }
}
