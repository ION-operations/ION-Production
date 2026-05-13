import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { AIMOSLogger } from './utils/logger';

/**
 * SUPER BASIC FUNCTIONAL UI - Minimal working dashboard
 * Purpose: Just get something working in the right sidebar
 */
export class SuperBasicDashboardProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;
    private _outputChannel: vscode.OutputChannel;
    
    constructor(private readonly _context: vscode.ExtensionContext) {
        this._outputChannel = vscode.window.createOutputChannel('AIM-OS Dashboard');
    }
    
    /**
     * ✅ REFRESH METHOD - Reload webview HTML without reloading Cursor
     */
    public refresh(): void {
        if (this._view) {
            const timestamp = new Date().toISOString();
            AIMOSLogger.log('SUPER_BASIC', '🔄 Refreshing webview...');
            this._outputChannel.appendLine(`🔄 [${timestamp}] Refreshing webview...`);
            
            // Update HTML with new content
            const newHtml = this.getWebviewContent(this._view.webview);
            this._view.webview.html = newHtml;
            
            AIMOSLogger.log('SUPER_BASIC', `✅ Webview refreshed (${newHtml.length} chars)`);
            this._outputChannel.appendLine(`✅ Webview refreshed (${newHtml.length} chars)`);
        } else {
            AIMOSLogger.log('SUPER_BASIC', '⚠️ Webview not yet initialized - cannot refresh');
            this._outputChannel.appendLine('⚠️ Webview not yet initialized - cannot refresh');
        }
    }
    
    /**
     * ✅ GET CURRENT HTML - For debugging/inspection
     */
    public getCurrentHtml(): string {
        return this._view?.webview.html || '';
    }
    
    resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        // ✅ DIAGNOSTIC: Log that resolveWebviewView was called
        const logFile = path.join(this._context.extensionPath, 'resolve-called.txt');
        const timestamp = new Date().toISOString();
        try {
            fs.writeFileSync(logFile, `✅ RESOLVE CALLED: ${timestamp}\nExtension Path: ${this._context.extensionPath}\n`, 'utf8');
        } catch (e) {
            console.error('Failed to write resolve log:', e);
        }
        
        // ✅ DIAGNOSTIC: Log to output channel
        this._outputChannel.clear();
        this._outputChannel.appendLine('═══════════════════════════════════════════');
        this._outputChannel.appendLine('✅ resolveWebviewView() CALLED!');
        this._outputChannel.appendLine('═══════════════════════════════════════════');
        this._outputChannel.appendLine(`Timestamp: ${timestamp}`);
        this._outputChannel.appendLine(`Extension Path: ${this._context.extensionPath}`);
        this._outputChannel.show();
        
        AIMOSLogger.log('SUPER_BASIC', '═══════════════════════════════════════════');
        AIMOSLogger.log('SUPER_BASIC', '✅ resolveWebviewView() CALLED!');
        AIMOSLogger.log('SUPER_BASIC', `Timestamp: ${timestamp}`);
        
        this._view = webviewView;
        
        // CRITICAL: Set options FIRST
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: []
        };
        
        // ✅ DIAGNOSTIC: Log options set
        this._outputChannel.appendLine('✅ Webview options set (enableScripts: true)');
        
        // SUPER BASIC HTML - Just works!
        const htmlContent = this.getWebviewContent(webviewView.webview);
        
        // ✅ DIAGNOSTIC: Log HTML details
        this._outputChannel.appendLine(`✅ HTML Content Length: ${htmlContent.length} chars`);
        this._outputChannel.appendLine(`✅ HTML has script tag: ${htmlContent.includes('<script>')}`);
        this._outputChannel.appendLine(`✅ HTML has body tag: ${htmlContent.includes('<body>')}`);
        
        webviewView.webview.html = htmlContent;
        
        AIMOSLogger.log('SUPER_BASIC', `✅ HTML content set (${htmlContent.length} chars)`);
        
        // ✅ DIAGNOSTIC: Handle messages from webview (console errors, logs, etc.)
        webviewView.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'consoleLog':
                        this._outputChannel.appendLine(`[CONSOLE] ${message.message}`);
                        AIMOSLogger.log('SUPER_BASIC', `[CONSOLE] ${message.message}`);
                        break;
                    case 'consoleError':
                        this._outputChannel.appendLine(`[ERROR] ${message.error}`);
                        if (message.stack) {
                            this._outputChannel.appendLine(`[STACK] ${message.stack}`);
                        }
                        AIMOSLogger.error('SUPER_BASIC', `[JS ERROR] ${message.error}`, { stack: message.stack });
                        // Also write to file
                        const errorFile = path.join(this._context.extensionPath, 'js-errors.txt');
                        fs.appendFileSync(errorFile, `[${new Date().toISOString()}] ERROR: ${message.error}\n${message.stack || ''}\n\n`, 'utf8');
                        break;
                    case 'testMCP':
                        vscode.window.showInformationMessage('MCP test - check Command Server');
                        webviewView.webview.postMessage({
                            command: 'response',
                            data: { message: 'MCP test triggered' }
                        });
                        break;
                    case 'testCommand':
                        vscode.window.showInformationMessage('VS Code command test successful!');
                        webviewView.webview.postMessage({
                            command: 'response',
                            data: { message: 'Command test successful' }
                        });
                        break;
                }
            },
            null,
            this._context.subscriptions
        );
        
        AIMOSLogger.log('SUPER_BASIC', '✅ Message handlers registered');
        this._outputChannel.appendLine('✅ Message handlers registered');
        this._outputChannel.appendLine('═══════════════════════════════════════════');
    }
    
    private getWebviewContent(webview: vscode.Webview): string {
        const cspSource = webview.cspSource;
        
        // ✅ SIMPLIFIED HTML - Using the clean version from simple-dashboard.html
        // This is the original simple HTML that worked - no complex diagnostic code
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src ${cspSource} 'unsafe-inline' 'unsafe-eval'; script-src ${cspSource} 'unsafe-inline' 'unsafe-eval'; style-src ${cspSource} 'unsafe-inline'; img-src ${cspSource} https: data:; font-src ${cspSource} https: data:; connect-src ${cspSource} https: ws: wss: http://localhost:5001;">
    <title>AIM-OS Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: #2d2d2d;
            border-bottom: 1px solid #3e3e3e;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header h1 {
            font-size: 14px;
            font-weight: 600;
            color: #4ec9b0;
        }
        
        .tabs {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid #3e3e3e;
            background: #252526;
            padding: 0 16px;
        }
        
        .tab {
            padding: 10px 16px;
            background: none;
            border: none;
            color: #cccccc;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-size: 13px;
        }
        
        .tab:hover {
            background: #2a2d2e;
        }
        
        .tab.active {
            color: #4ec9b0;
            border-bottom-color: #4ec9b0;
        }
        
        .content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .section {
            background: #2d2d2d;
            border: 1px solid #3e3e3e;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        
        .section h2 {
            font-size: 14px;
            font-weight: 600;
            color: #4ec9b0;
            margin-bottom: 12px;
        }
        
        .section p {
            font-size: 13px;
            color: #cccccc;
            line-height: 1.6;
            margin-bottom: 8px;
        }
        
        .button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }
        
        .button:hover {
            background: #1177bb;
        }
        
        .status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status.active {
            background: #51cf66;
            color: white;
        }
        
        .status.inactive {
            background: #ff6b6b;
            color: white;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AIM-OS Dashboard</h1>
        <div>
            <span class="status active">✅ Plain HTML - Working!</span>
        </div>
    </div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('agents')">Agents</button>
        <button class="tab" onclick="showTab('chat')">Chat</button>
        <button class="tab" onclick="showTab('chains')">Chains</button>
        <button class="tab" onclick="showTab('tools')">Tools</button>
        <button class="tab" onclick="showTab('timeline')">Timeline</button>
        <button class="tab" onclick="showTab('nl-tags')">NL Tags</button>
    </div>
    
    <div class="content">
        <div id="agents" class="tab-content active">
            <div class="section">
                <h2>Agent Management</h2>
                <div id="agent-controls">
                    <div style="margin-bottom: 16px;">
                        <input type="text" id="agent-prompt" placeholder="Agent prompt/task..." style="width: 100%; padding: 8px; background: #1e1e1e; border: 1px solid #3e3e3e; color: #d4d4d4; border-radius: 4px; margin-bottom: 8px;">
                        <input type="text" id="agent-repo" placeholder="Repo path (local or GitHub URL)..." style="width: 100%; padding: 8px; background: #1e1e1e; border: 1px solid #3e3e3e; color: #d4d4d4; border-radius: 4px; margin-bottom: 8px;">
                        <div style="display: flex; gap: 8px;">
                            <button class="button" id="start-agent-btn" onclick="startAgent()">Start Agent</button>
                            <button class="button" id="stop-agent-btn" onclick="stopAgent()" disabled style="background: #d32f2f;">Stop Agent</button>
                        </div>
                    </div>
                    <div id="agent-status" style="display: none;">
                        <div style="margin-bottom: 8px;">
                            <strong>Status:</strong> <span id="status-text">-</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>Run ID:</strong> <span id="run-id">-</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>Progress:</strong> <span id="progress-text">-</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>Method:</strong> <span id="method-text">-</span>
                        </div>
                    </div>
                    <div id="agent-output" style="display: none; margin-top: 16px;">
                        <h3 style="font-size: 13px; margin-bottom: 8px;">Output:</h3>
                        <pre id="output-text" style="background: #1e1e1e; padding: 12px; border-radius: 4px; overflow-x: auto; max-height: 300px; font-size: 12px; white-space: pre-wrap; word-wrap: break-word;"></pre>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="chat" class="tab-content">
            <div class="section">
                <h2>Chat Interface</h2>
                <p>Chat functionality will go here.</p>
            </div>
        </div>
        
        <div id="chains" class="tab-content">
            <div class="section">
                <h2>Prompt Chains</h2>
                <p>Chain management will go here.</p>
            </div>
        </div>
        
        <div id="tools" class="tab-content">
            <div class="section">
                <h2>MCP Tools</h2>
                <p>Tool management will go here.</p>
            </div>
        </div>
        
        <div id="timeline" class="tab-content">
            <div class="section">
                <h2>Timeline</h2>
                <p>Timeline view will go here.</p>
            </div>
        </div>
        
        <div id="nl-tags" class="tab-content">
            <div class="section">
                <h2>NL Tags</h2>
                <p>NL tag management will go here.</p>
            </div>
        </div>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function showTab(tabId) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Send ready message to extension
        if (typeof vscode !== 'undefined') {
            vscode.postMessage({ command: 'ready' });
        }
        
        // Agent monitoring state
        let currentRunId = null;
        let statusInterval = null;
        
        // Start agent
        async function startAgent() {
            const prompt = document.getElementById('agent-prompt').value;
            const repoPath = document.getElementById('agent-repo').value || '.';
            
            if (!prompt) {
                alert('Please enter an agent prompt');
                return;
            }
            
            try {
                const response = await fetch('http://localhost:5001/agent/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        repoPath: repoPath,
                        maxRuntimeHours: 6
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentRunId = result.runId;
                    document.getElementById('run-id').textContent = result.runId;
                    document.getElementById('method-text').textContent = result.method;
                    document.getElementById('agent-status').style.display = 'block';
                    document.getElementById('start-agent-btn').disabled = true;
                    document.getElementById('stop-agent-btn').disabled = false;
                    
                    // Start polling status
                    startStatusPolling(result.runId);
                } else {
                    alert('Failed to start agent: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error starting agent: ' + error.message);
                console.error('Agent start error:', error);
            }
        }
        
        // Stop agent
        async function stopAgent() {
            if (!currentRunId) return;
            
            try {
                const response = await fetch('http://localhost:5001/agent/stop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ runId: currentRunId })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    stopStatusPolling();
                    document.getElementById('agent-status').style.display = 'none';
                    document.getElementById('agent-output').style.display = 'none';
                    document.getElementById('start-agent-btn').disabled = false;
                    document.getElementById('stop-agent-btn').disabled = true;
                    currentRunId = null;
                } else {
                    alert('Failed to stop agent: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Error stopping agent: ' + error.message);
                console.error('Agent stop error:', error);
            }
        }
        
        // Poll agent status
        function startStatusPolling(runId) {
            if (statusInterval) clearInterval(statusInterval);
            
            statusInterval = setInterval(async () => {
                try {
                    const response = await fetch('http://localhost:5001/agent/status/' + runId);
                    const result = await response.json();
                    
                    if (result.success && result.status) {
                        const status = result.status;
                        document.getElementById('status-text').textContent = status.status || 'unknown';
                        
                        if (status.current_step !== undefined && status.total_steps !== undefined) {
                            document.getElementById('progress-text').textContent = status.current_step + ' / ' + status.total_steps;
                        }
                        
                        if (status.output && status.output.length > 0) {
                            document.getElementById('output-text').textContent = status.output.join('\\n');
                            document.getElementById('agent-output').style.display = 'block';
                        }
                        
                        // Stop polling if completed
                        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
                            stopStatusPolling();
                            document.getElementById('start-agent-btn').disabled = false;
                            document.getElementById('stop-agent-btn').disabled = true;
                        }
                    }
                } catch (error) {
                    console.error('Status polling error:', error);
                }
            }, 5000); // Poll every 5 seconds
        }
        
        function stopStatusPolling() {
            if (statusInterval) {
                clearInterval(statusInterval);
                statusInterval = null;
            }
        }
        
        console.log('[SIMPLE_DASHBOARD] Dashboard loaded successfully');
    </script>
</body>
</html>`;
    }
}
