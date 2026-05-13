"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PureHtmlDashboardProvider = void 0;
const vscode = __importStar(require("vscode"));
const logger_1 = require("./utils/logger");
/**
 * Pure HTML Dashboard Provider
 *
 * Completely isolated version - no React, no external assets, pure HTML/CSS/JS
 * Purpose: Test if webview mechanism works independently of React/asset loading
 *
 * This is a diagnostic tool to isolate webview vs React issues.
 */
class PureHtmlDashboardProvider {
    constructor(context) {
        this._context = context;
    }
    resolveWebviewView(webviewView, context, _token) {
        logger_1.AIMOSLogger.log('PURE_HTML', '═══════════════════════════════════════════');
        logger_1.AIMOSLogger.log('PURE_HTML', '🎯 Pure HTML Dashboard resolveWebviewView TRIGGERED!!!');
        logger_1.AIMOSLogger.log('PURE_HTML', '═══════════════════════════════════════════');
        logger_1.AIMOSLogger.log('PURE_HTML', `View ID: ${webviewView.viewId}`);
        PureHtmlDashboardProvider._view = webviewView;
        // Set options FIRST (critical!)
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: []
        };
        logger_1.AIMOSLogger.log('PURE_HTML', '✅ Webview options set');
        // Get pure HTML content (completely self-contained)
        const htmlContent = this.getPureHtmlContent(webviewView.webview);
        // Set HTML content
        webviewView.webview.html = htmlContent;
        logger_1.AIMOSLogger.log('PURE_HTML', `✅ Pure HTML content set (${htmlContent.length} chars)`);
        // Set up message handlers
        webviewView.webview.onDidReceiveMessage(message => {
            logger_1.AIMOSLogger.log('PURE_HTML', `Message received: ${message.command}`);
            switch (message.command) {
                case 'alert':
                    vscode.window.showInformationMessage(message.text);
                    break;
                case 'test':
                    webviewView.webview.postMessage({
                        command: 'testResponse',
                        data: 'Test successful!'
                    });
                    break;
            }
        }, null, []);
        logger_1.AIMOSLogger.log('PURE_HTML', '✅ Pure HTML Dashboard initialized');
    }
    getPureHtmlContent(webview) {
        const cspSource = webview.cspSource;
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="
        default-src ${cspSource} 'unsafe-inline' 'unsafe-eval';
        script-src ${cspSource} 'unsafe-inline' 'unsafe-eval';
        style-src ${cspSource} 'unsafe-inline';
        img-src ${cspSource} https: data:;
        font-src ${cspSource} https: data:;
        connect-src ${cspSource} https: ws: wss:;
    ">
    <title>AIM-OS Dashboard - Pure HTML</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #1e1e1e;
            color: #cccccc;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #252526;
            border-bottom: 1px solid #3e3e42;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }

        .header h1 {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            margin: 0;
        }

        .status-badge {
            background: #0e639c;
            color: #ffffff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .status-badge.success {
            background: #107c10;
        }

        .status-badge.warning {
            background: #ffaa00;
        }

        .tabs {
            background: #252526;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            padding: 0 8px;
            overflow-x: auto;
            flex-shrink: 0;
        }

        .tab {
            padding: 10px 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            color: #cccccc;
            font-size: 13px;
            white-space: nowrap;
            transition: all 0.2s;
            user-select: none;
        }

        .tab:hover {
            background: #2a2d2e;
            color: #ffffff;
        }

        .tab.active {
            color: #ffffff;
            border-bottom-color: #007acc;
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

        .card {
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 16px;
        }

        .card-title {
            font-size: 14px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 12px;
        }

        .card-content {
            color: #cccccc;
            font-size: 13px;
            line-height: 1.6;
        }

        .button {
            background: #0e639c;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: background 0.2s;
        }

        .button:hover {
            background: #1177bb;
        }

        .button:active {
            background: #0a4d73;
        }

        .button.secondary {
            background: #3e3e42;
        }

        .button.secondary:hover {
            background: #454545;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-top: 12px;
        }

        .info-item {
            display: flex;
            flex-direction: column;
        }

        .info-label {
            font-size: 11px;
            color: #858585;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-value {
            font-size: 14px;
            color: #ffffff;
            font-weight: 500;
        }

        .test-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #3e3e42;
        }

        .test-result {
            margin-top: 12px;
            padding: 12px;
            background: #2d2d30;
            border-radius: 4px;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        }

        .test-result.success {
            background: #0d3e0d;
            color: #4ec9b0;
        }

        .test-result.error {
            background: #3e0d0d;
            color: #f48771;
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-indicator.online {
            background: #107c10;
        }

        .status-indicator.offline {
            background: #f48771;
        }

        .status-indicator.unknown {
            background: #858585;
        }

        .log-output {
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            max-height: 200px;
            overflow-y: auto;
            color: #cccccc;
        }

        .log-entry {
            margin-bottom: 4px;
            padding: 2px 0;
        }

        .log-entry.info {
            color: #4ec9b0;
        }

        .log-entry.success {
            color: #107c10;
        }

        .log-entry.error {
            color: #f48771;
        }

        .log-entry.warning {
            color: #ffaa00;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>✨ AIM-OS Dashboard</h1>
        <span class="status-badge success">Pure HTML - Isolated</span>
    </div>

    <div class="tabs">
        <div class="tab active" data-tab="agents">Agents</div>
        <div class="tab" data-tab="chat">Chat</div>
        <div class="tab" data-tab="chains">Chains</div>
        <div class="tab" data-tab="tools">Tools</div>
        <div class="tab" data-tab="timeline">Timeline</div>
        <div class="tab" data-tab="nl-tags">NL Tags</div>
    </div>

    <div class="content">
        <!-- Agents Tab -->
        <div class="tab-content active" id="agents">
            <div class="card">
                <div class="card-title">Agent Management</div>
                <div class="card-content">
                    <p>This is the Agents tab - Pure HTML version.</p>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Status</div>
                            <div class="info-value">
                                <span class="status-indicator online"></span>
                                Online
                            </div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Version</div>
                            <div class="info-value">Pure HTML v1.0</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Mode</div>
                            <div class="info-value">Isolated</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">System Status</div>
                <div class="card-content">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Extension</div>
                            <div class="info-value">
                                <span class="status-indicator online"></span>
                                Active
                            </div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Webview</div>
                            <div class="info-value">
                                <span class="status-indicator online"></span>
                                Connected
                            </div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">React</div>
                            <div class="info-value">
                                <span class="status-indicator unknown"></span>
                                Not Used
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="test-section">
                <div class="card-title">Diagnostic Tests</div>
                <button class="button" onclick="runTests()">Run Tests</button>
                <div id="test-results"></div>
            </div>
        </div>

        <!-- Chat Tab -->
        <div class="tab-content" id="chat">
            <div class="card">
                <div class="card-title">Chat Interface</div>
                <div class="card-content">
                    <p>This is the Chat tab - Pure HTML version.</p>
                    <p>If you can see this, the webview mechanism works correctly!</p>
                </div>
            </div>
        </div>

        <!-- Chains Tab -->
        <div class="tab-content" id="chains">
            <div class="card">
                <div class="card-title">Prompt Chains</div>
                <div class="card-content">
                    <p>This is the Chains tab - Pure HTML version.</p>
                </div>
            </div>
        </div>

        <!-- Tools Tab -->
        <div class="tab-content" id="tools">
            <div class="card">
                <div class="card-title">MCP Tools</div>
                <div class="card-content">
                    <p>This is the Tools tab - Pure HTML version.</p>
                    <p>If this tab works, webview tabs functionality is working.</p>
                </div>
            </div>
        </div>

        <!-- Timeline Tab -->
        <div class="tab-content" id="timeline">
            <div class="card">
                <div class="card-title">Timeline</div>
                <div class="card-content">
                    <p>This is the Timeline tab - Pure HTML version.</p>
                </div>
            </div>
        </div>

        <!-- NL Tags Tab -->
        <div class="tab-content" id="nl-tags">
            <div class="card">
                <div class="card-title">NL Tags</div>
                <div class="card-content">
                    <p>This is the NL Tags tab - Pure HTML version.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                
                // Update tabs
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update content
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');

                // Log to console
                console.log('[PURE_HTML] Tab switched to:', tabId);
            });
        });

        // Message handling
        window.addEventListener('message', event => {
            const message = event.data;
            console.log('[PURE_HTML] Message received:', message);
            
            if (message.command === 'testResponse') {
                addLog('success', 'Test response received: ' + message.data);
            }
        });

        // Test functions
        function runTests() {
            const results = document.getElementById('test-results');
            results.innerHTML = '';
            
            const tests = [
                { name: 'DOM Loaded', test: () => document.body !== null },
                { name: 'JavaScript Executing', test: () => typeof vscode !== 'undefined' },
                { name: 'Tab Switching Works', test: () => document.querySelectorAll('.tab').length > 0 },
                { name: 'Message API Available', test: () => typeof acquireVsCodeApi !== 'undefined' },
                { name: 'CSS Styles Applied', test: () => window.getComputedStyle(document.body).backgroundColor !== 'rgba(0, 0, 0, 0)' }
            ];

            tests.forEach((test, index) => {
                setTimeout(() => {
                    const passed = test.test();
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'test-result ' + (passed ? 'success' : 'error');
                    resultDiv.textContent = (passed ? '✅' : '❌') + ' ' + test.name;
                    results.appendChild(resultDiv);
                    
                    addLog(passed ? 'success' : 'error', test.name + ': ' + (passed ? 'PASSED' : 'FAILED'));
                }, index * 100);
            });

            // Send test message to extension
            vscode.postMessage({ command: 'test', data: 'Running tests' });
        }

        function addLog(type, message) {
            console.log('[PURE_HTML][' + type.toUpperCase() + ']', message);
        }

        // Initialize
        console.log('[PURE_HTML] Dashboard initialized');
        console.log('[PURE_HTML] VS Code API:', typeof vscode !== 'undefined' ? 'Available' : 'Not Available');
        console.log('[PURE_HTML] Tabs:', document.querySelectorAll('.tab').length);
        console.log('[PURE_HTML] Content panels:', document.querySelectorAll('.tab-content').length);

        // Send initialization message
        vscode.postMessage({ command: 'alert', text: 'Pure HTML Dashboard loaded successfully!' });
    </script>
</body>
</html>`;
    }
    static reveal() {
        if (PureHtmlDashboardProvider._view) {
            PureHtmlDashboardProvider._view.show(true);
        }
    }
    static getView() {
        return PureHtmlDashboardProvider._view;
    }
}
exports.PureHtmlDashboardProvider = PureHtmlDashboardProvider;
//# sourceMappingURL=pureHtmlDashboardProvider.js.map