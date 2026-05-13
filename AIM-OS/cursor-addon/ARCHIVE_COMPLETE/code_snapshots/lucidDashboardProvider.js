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
exports.LucidOrchestratorDashboardProvider = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const mcpClient_1 = require("./mcp/mcpClient");
const logger_1 = require("./utils/logger");
class LucidOrchestratorDashboardProvider {
    static getOutputChannel() {
        if (!LucidOrchestratorDashboardProvider._outputChannel) {
            LucidOrchestratorDashboardProvider._outputChannel = vscode.window.createOutputChannel('AIM-OS Dashboard');
        }
        return LucidOrchestratorDashboardProvider._outputChannel;
    }
    log(message, data) {
        // Use the centralized logger
        logger_1.AIMOSLogger.log('DASHBOARD', message, data);
    }
    constructor(context, config) {
        this._mcpClient = null;
        this._context = context;
        this._config = {
            position: 'panel',
            models: {
                gemini: { enabled: false },
                cerebras: { enabled: false },
                default: 'auto'
            },
            agentManagement: {
                enabled: true,
                autoManage: false
            },
            daemon: {
                url: 'http://localhost:5000',
                autoConnect: true
            },
            ...config
        };
    }
    resolveWebviewView(webviewView, context, _token) {
        logger_1.AIMOSLogger.log('WEBVIEW_RESOLVE', '═══════════════════════════════════════════');
        logger_1.AIMOSLogger.log('WEBVIEW_RESOLVE', '🎯 resolveWebviewView TRIGGERED!!!');
        logger_1.AIMOSLogger.log('WEBVIEW_RESOLVE', '═══════════════════════════════════════════');
        logger_1.AIMOSLogger.log('WEBVIEW_RESOLVE', `View ID: ${webviewView.viewId}`);
        logger_1.AIMOSLogger.log('WEBVIEW_RESOLVE', `Extension path: ${this._context.extensionPath}`);
        logger_1.AIMOSLogger.log('WEBVIEW_RESOLVE', `Context state: ${JSON.stringify(context.state)}`);
        const output = LucidOrchestratorDashboardProvider.getOutputChannel();
        output.show(); // Show output panel automatically
        output.appendLine('');
        output.appendLine('═══════════════════════════════════════════');
        output.appendLine('🎯 DASHBOARD VIEW BEING RESOLVED!!!');
        output.appendLine('═══════════════════════════════════════════');
        output.appendLine('');
        this.log('[AIM-OS] ========================================');
        this.log('[AIM-OS] ✅ resolveWebviewView CALLED');
        this.log(`[AIM-OS] Webview view ID: ${webviewView.viewId}`);
        this.log(`[AIM-OS] Extension path: ${this._context.extensionPath}`);
        LucidOrchestratorDashboardProvider._view = webviewView;
        // CRITICAL FIX: Set webview options BEFORE setting HTML
        // VS Code requires options to be set before HTML for proper initialization
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.file(path.join(this._context.extensionPath, 'dist')),
                vscode.Uri.file(path.join(this._context.extensionPath, 'resources'))
            ]
        };
        this.log('[AIM-OS] ✅ Webview options set (enableScripts, localResourceRoots)');
        // CRITICAL FIX: Load full HTML immediately (no timeout race condition)
        try {
            this.log('[AIM-OS] Loading full HTML content...');
            const htmlContent = this.getWebviewContent(webviewView.webview);
            webviewView.webview.html = htmlContent;
            this.log(`[AIM-OS] ✅ Full HTML content loaded (${htmlContent.length} chars)`);
        }
        catch (error) {
            this.log(`[AIM-OS] ❌ Error loading full HTML: ${error}`);
            // Use a proper error display instead of test HTML
            const errorHtml = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AIM-OS Dashboard - Error</title>
    <style>
        body { 
            background: #1e1e1e; 
            color: #ffffff; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 40px; 
            margin: 0;
        }
        h1 { color: #ff6b6b; }
        pre { 
            background: #2d2d2d; 
            padding: 20px; 
            border-radius: 8px;
            overflow: auto;
            color: #ffff00;
        }
        .info { color: #4ec9b0; margin-top: 20px; }
        ol { margin-top: 10px; }
        li { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>❌ Failed to Load Dashboard</h1>
    <pre>${String(error)}</pre>
    <div class="info">
        <p><strong>Troubleshooting:</strong></p>
        <ol>
            <li>Check that dist/index.html exists</li>
            <li>Check that dist/assets/*.js files exist</li>
            <li>Rebuild the extension if needed</li>
            <li>Check the Output panel (AIM-OS Dashboard) for details</li>
        </ol>
    </div>
</body>
</html>`;
            webviewView.webview.html = errorHtml;
        }
        // Set up message handler
        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'movePanel':
                    await this.handleMovePanel(message.position);
                    break;
                case 'connectDaemon':
                    await this.handleConnectDaemon(message.url);
                    break;
                case 'selectModel':
                    await this.handleSelectModel(message.model);
                    break;
                case 'manageAgent':
                    await this.handleManageAgent(message.action, message.agentId);
                    break;
                case 'executeMCPTool':
                    await this.handleExecuteMCPTool(message.toolId, message.params);
                    break;
                case 'mcpCall':
                    // Forward MCP tool calls from React UI to MCP server
                    await this.handleMCPCall(webviewView.webview, message);
                    break;
                case 'getSystemStatus':
                    await this.handleGetSystemStatus(webviewView.webview);
                    break;
            }
        }, null, this._context.subscriptions);
        // Load initial state
        this.loadInitialState(webviewView.webview);
    }
    getWebviewContent(webview) {
        // Try to load the built HTML, or use enhanced fallback
        const distHtmlPath = path.join(this._context.extensionPath, 'dist', 'index.html');
        let htmlContent = '';
        // ENHANCED DIAGNOSTIC LOGGING - Get EXACT answers
        this.log(`[DIAGNOSTIC] ========================================`);
        this.log(`[DIAGNOSTIC] UI PANEL LOADING DIAGNOSTIC START`);
        this.log(`[DIAGNOSTIC] ========================================`);
        this.log(`[DIAGNOSTIC] Extension path: ${this._context.extensionPath}`);
        this.log(`[DIAGNOSTIC] HTML path: ${distHtmlPath}`);
        this.log(`[DIAGNOSTIC] HTML exists: ${fs.existsSync(distHtmlPath)}`);
        this.log(`[DIAGNOSTIC] HTML readable: ${fs.existsSync(distHtmlPath) ? 'YES' : 'NO'}`);
        // Check asset files existence BEFORE reading HTML
        const expectedAssets = ['main-5fYGI1t7.js', 'main-DftvcEcs.css'];
        expectedAssets.forEach(file => {
            const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', file);
            const exists = fs.existsSync(assetPath);
            this.log(`[DIAGNOSTIC] Asset ${file} exists: ${exists}`);
            if (exists) {
                const stats = fs.statSync(assetPath);
                this.log(`[DIAGNOSTIC] Asset ${file} size: ${stats.size} bytes`);
            }
            else {
                this.log(`[DIAGNOSTIC] Asset ${file} path: ${assetPath}`);
            }
        });
        if (fs.existsSync(distHtmlPath)) {
            // CRITICAL FIX: Always re-read file to get latest version
            // Add cache-busting timestamp to force webview reload
            const fileStats = fs.statSync(distHtmlPath);
            const cacheBuster = fileStats.mtime.getTime();
            htmlContent = fs.readFileSync(distHtmlPath, 'utf8');
            // CRITICAL DEBUG: Log the ACTUAL script tag format we're seeing
            const rawScriptTags = htmlContent.match(/<script[^>]*>/gi);
            if (rawScriptTags) {
                rawScriptTags.forEach((tag, idx) => {
                    this.log(`[DIAGNOSTIC] Raw script tag ${idx + 1}: ${tag}`);
                });
            }
            // DIAGNOSTIC: Log HTML content details
            this.log(`[DIAGNOSTIC] ✅ HTML file read successfully`);
            this.log(`[DIAGNOSTIC] HTML length: ${htmlContent.length} chars`);
            this.log(`[DIAGNOSTIC] HTML has root element: ${htmlContent.includes('<div id="root">')}`);
            // DIAGNOSTIC: Test regex BEFORE replacement
            const testScriptMatches = htmlContent.match(/<script[^>]*src=["']([^"']*assets\/[^"']+)["'][^>]*>/gi);
            const testLinkMatches = htmlContent.match(/<link[^>]*href=["']([^"']*assets\/[^"']+)["'][^>]*>/gi);
            this.log(`[DIAGNOSTIC] Script tags found (BEFORE replacement): ${testScriptMatches ? testScriptMatches.length : 0}`);
            if (testScriptMatches) {
                testScriptMatches.forEach((match, idx) => {
                    this.log(`[DIAGNOSTIC]   Script ${idx + 1}: ${match.substring(0, 120)}`);
                });
            }
            this.log(`[DIAGNOSTIC] Link tags found (BEFORE replacement): ${testLinkMatches ? testLinkMatches.length : 0}`);
            if (testLinkMatches) {
                testLinkMatches.forEach((match, idx) => {
                    this.log(`[DIAGNOSTIC]   Link ${idx + 1}: ${match.substring(0, 120)}`);
                });
            }
            // CRITICAL FIX: Replace script tags with webview URIs (handles type="module", crossorigin, etc.)
            // Match script tags with src attribute - more flexible regex that handles any attribute order
            let scriptReplacementCount = 0;
            htmlContent = htmlContent.replace(/<script([^>]*?)(?:\s+src=["']([^"']*assets\/[^"']+)["'])([^>]*)>/gi, (match, beforeSrc, assetPathRel, afterSrc) => {
                // Extract just the filename from the path
                const assetFileName = assetPathRel.split('/').pop() || assetPathRel.split('\\').pop() || assetPathRel;
                const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', assetFileName);
                if (fs.existsSync(assetPath)) {
                    const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
                    // Reconstruct script tag with webview URI, preserving all attributes
                    this.log(`[DIAGNOSTIC] ✅ Replacing script: ${assetPathRel} -> ${assetUri.toString().substring(0, 80)}...`);
                    scriptReplacementCount++;
                    // Preserve all attributes but replace src with webview URI
                    return `<script${beforeSrc} src="${assetUri}?v=${cacheBuster}"${afterSrc}>`;
                }
                this.log(`[DIAGNOSTIC] ❌ Script asset not found: ${assetPath} (from ${assetPathRel})`);
                return match; // Keep original if file doesn't exist
            });
            this.log(`[DIAGNOSTIC] Script replacements: ${scriptReplacementCount} of ${testScriptMatches ? testScriptMatches.length : 0} replaced`);
            if (scriptReplacementCount === 0 && testScriptMatches && testScriptMatches.length > 0) {
                this.log(`[DIAGNOSTIC] ❌ CRITICAL: Script regex found ${testScriptMatches.length} matches but replaced 0!`);
                this.log(`[DIAGNOSTIC] ❌ This means regex matching but file lookup failing`);
            }
            // Replace CSS/other asset paths (href attributes)
            let assetReplacementCount = 0;
            htmlContent = htmlContent.replace(/href=["']([^"']*assets\/[^"']+)["']/gi, (match, assetPathRel) => {
                const assetFileName = assetPathRel.split('/').pop() || assetPathRel.split('\\').pop() || assetPathRel;
                const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', assetFileName);
                if (fs.existsSync(assetPath)) {
                    const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
                    this.log(`[AIM-OS DEBUG] ✅ Replacing href: ${assetPathRel} -> ${assetUri}`);
                    assetReplacementCount++;
                    return `href="${assetUri}?v=${cacheBuster}"`;
                }
                this.log(`[AIM-OS DEBUG] ❌ Asset not found: ${assetPath} (from ${assetPathRel})`);
                return match;
            });
            this.log(`[DIAGNOSTIC] Asset replacements: ${assetReplacementCount} of ${testLinkMatches ? testLinkMatches.length : 0} replaced`);
            if (assetReplacementCount === 0 && testLinkMatches && testLinkMatches.length > 0) {
                this.log(`[DIAGNOSTIC] ❌ CRITICAL: Link regex found ${testLinkMatches.length} matches but replaced 0!`);
                this.log(`[DIAGNOSTIC] ❌ This means regex matching but file lookup failing`);
            }
            // DIAGNOSTIC: Test webview URI generation
            const testAssetPath = path.join(this._context.extensionPath, 'dist', 'assets', 'main-5fYGI1t7.js');
            if (fs.existsSync(testAssetPath)) {
                const testUri = webview.asWebviewUri(vscode.Uri.file(testAssetPath));
                this.log(`[DIAGNOSTIC] Test webview URI generation:`);
                this.log(`[DIAGNOSTIC]   File path: ${testAssetPath}`);
                this.log(`[DIAGNOSTIC]   Webview URI: ${testUri}`);
                this.log(`[DIAGNOSTIC]   URI scheme: ${testUri.scheme}`);
                this.log(`[DIAGNOSTIC]   URI authority: ${testUri.authority}`);
            }
            // DIAGNOSTIC: Check final HTML after replacements
            const finalScriptMatches = htmlContent.match(/<script[^>]*src=["']([^"']+)["'][^>]*>/gi);
            const finalLinkMatches = htmlContent.match(/<link[^>]*href=["']([^"']+)["'][^>]*>/gi);
            this.log(`[DIAGNOSTIC] Final HTML script tags: ${finalScriptMatches ? finalScriptMatches.length : 0}`);
            if (finalScriptMatches) {
                finalScriptMatches.forEach((script, idx) => {
                    const srcMatch = script.match(/src=["']([^"']+)["']/);
                    const srcValue = srcMatch ? srcMatch[1] : 'NOT FOUND';
                    this.log(`[DIAGNOSTIC]   Final script ${idx + 1} src: ${srcValue.substring(0, 100)}`);
                    if (!srcValue.startsWith('vscode-webview://')) {
                        this.log(`[DIAGNOSTIC] ❌ CRITICAL: Script ${idx + 1} src NOT a webview URI! Still has original path!`);
                    }
                });
            }
            this.log(`[DIAGNOSTIC] Final HTML link tags: ${finalLinkMatches ? finalLinkMatches.length : 0}`);
            if (finalLinkMatches) {
                finalLinkMatches.forEach((link, idx) => {
                    const hrefMatch = link.match(/href=["']([^"']+)["']/);
                    const hrefValue = hrefMatch ? hrefMatch[1] : 'NOT FOUND';
                    this.log(`[DIAGNOSTIC]   Final link ${idx + 1} href: ${hrefValue.substring(0, 100)}`);
                    if (!hrefValue.startsWith('vscode-webview://')) {
                        this.log(`[DIAGNOSTIC] ❌ CRITICAL: Link ${idx + 1} href NOT a webview URI! Still has original path!`);
                    }
                });
            }
            // CRITICAL FIX: Add TrustedTypes policy BEFORE CSP to allow module scripts
            // VS Code/Cursor enforces TrustedTypes, so we need to create a policy first
            const trustedTypesScript = `<script>
if (window.trustedTypes && window.trustedTypes.createPolicy) {
    try {
        window.trustedTypes.createPolicy('default', {
            createHTML: (string) => string,
            createScript: (string) => string,
            createScriptURL: (string) => string
        });
        console.log('[AIM-OS] ✅ TrustedTypes policy created');
    } catch (e) {
        console.warn('[AIM-OS] ⚠️ TrustedTypes policy creation failed:', e);
    }
}
</script>`;
            // Inject CSP meta tag with module support
            const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src ${webview.cspSource} https:; script-src ${webview.cspSource} 'unsafe-inline' 'unsafe-eval' 'module' https:; style-src ${webview.cspSource} 'unsafe-inline' https:; img-src ${webview.cspSource} https: data:; font-src ${webview.cspSource} https: data:; connect-src ${webview.cspSource} https: ws: wss:;">`;
            // Insert TrustedTypes script and CSP after <head> tag if not already present
            if (!htmlContent.includes('Content-Security-Policy')) {
                htmlContent = htmlContent.replace(/<head>/i, `<head>\n    ${trustedTypesScript}\n    ${cspMeta}`);
            }
            // Debug: Log that we're loading React UI with cache-busting
            this.log(`[AIM-OS DEBUG] ✅ Loading React UI from dist/index.html (cache-buster: ${cacheBuster})`);
            // Additional debug: Log HTML content length and first 500 chars
            this.log(`[AIM-OS DEBUG] HTML content length: ${htmlContent.length} chars`);
            this.log(`[AIM-OS DEBUG] HTML preview: ${htmlContent.substring(0, 500)}...`);
            // Check if root element exists
            if (!htmlContent.includes('<div id="root">')) {
                this.log(`[AIM-OS DEBUG] ❌ WARNING: Root element <div id="root"> not found in HTML!`);
            }
            else {
                this.log(`[AIM-OS DEBUG] ✅ Root element <div id="root"> found in HTML`);
            }
            // CRITICAL: Verify scripts are converted to webview URIs
            const scriptMatches = htmlContent.match(/<script[^>]*src=["']([^"']+)["'][^>]*>/gi);
            if (scriptMatches && scriptMatches.length > 0) {
                this.log(`[AIM-OS DEBUG] ✅ Found ${scriptMatches.length} script tag(s)`);
                scriptMatches.forEach((script, idx) => {
                    const srcMatch = script.match(/src=["']([^"']+)["']/);
                    if (srcMatch) {
                        const src = srcMatch[1];
                        if (!src.startsWith('vscode-webview://')) {
                            this.log(`[AIM-OS DEBUG] ❌ Script ${idx + 1} NOT converted to webview URI: ${src}`);
                        }
                        else {
                            this.log(`[AIM-OS DEBUG] ✅ Script ${idx + 1} converted: ${src.substring(0, 80)}...`);
                        }
                    }
                });
            }
            else {
                this.log(`[AIM-OS DEBUG] ❌ WARNING: No script tags found in HTML!`);
            }
        }
        else {
            // Enhanced fallback HTML with full dashboard preview
            this.log(`[DIAGNOSTIC] ========================================`);
            this.log(`[DIAGNOSTIC] ❌ CRITICAL ERROR: HTML FILE NOT FOUND`);
            this.log(`[DIAGNOSTIC] ========================================`);
            this.log(`[DIAGNOSTIC] Extension path: ${this._context.extensionPath}`);
            this.log(`[DIAGNOSTIC] Expected HTML path: ${distHtmlPath}`);
            this.log(`[DIAGNOSTIC] File exists check: ${fs.existsSync(distHtmlPath)}`);
            // Try to find what files DO exist
            const distDir = path.join(this._context.extensionPath, 'dist');
            this.log(`[DIAGNOSTIC] Dist directory exists: ${fs.existsSync(distDir)}`);
            if (fs.existsSync(distDir)) {
                try {
                    const distFiles = fs.readdirSync(distDir);
                    this.log(`[DIAGNOSTIC] Files in dist/: ${distFiles.join(', ')}`);
                }
                catch (e) {
                    this.log(`[DIAGNOSTIC] Could not read dist directory: ${e}`);
                }
            }
            this.log(`[DIAGNOSTIC] ========================================`);
            this.log(`[DIAGNOSTIC] Using fallback HTML`);
            this.log(`[DIAGNOSTIC] ========================================`);
            const scriptUri = webview.asWebviewUri(vscode.Uri.file(path.join(this._context.extensionPath, 'dist', 'assets', 'index.js')));
            const styleUri = webview.asWebviewUri(vscode.Uri.file(path.join(this._context.extensionPath, 'dist', 'assets', 'index.css')));
            htmlContent = this.getEnhancedFallbackHtml(webview, scriptUri, styleUri);
        }
        return htmlContent;
    }
    getEnhancedFallbackHtml(webview, scriptUri, styleUri) {
        // Fallback HTML that matches MainDashboard structure
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lucid Orchestrator Dashboard - AIM-OS</title>
    <link rel="stylesheet" href="${styleUri}">
    <meta http-equiv="Content-Security-Policy" content="default-src ${webview.cspSource} https:; script-src ${webview.cspSource} 'unsafe-inline' 'unsafe-eval' https:; style-src ${webview.cspSource} 'unsafe-inline' https:; img-src ${webview.cspSource} https: data:; font-src ${webview.cspSource} https: data:; connect-src ${webview.cspSource} https: ws: wss:;">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
            flex-shrink: 0;
        }
        .header h1 {
            font-size: 14px;
            font-weight: 600;
            color: #4ec9b0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-bar {
            display: flex;
            gap: 16px;
            align-items: center;
            font-size: 12px;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ff6b6b;
        }
        .status-dot.connected { background: #51cf66; }
        .status-dot.connecting { background: #ffd43b; animation: pulse 1.5s infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }
        .section {
            background: #2d2d2d;
            border: 1px solid #3e3e3e;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .section h3 {
            font-size: 13px;
            font-weight: 600;
            color: #4ec9b0;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section p {
            font-size: 12px;
            color: #999;
            line-height: 1.6;
            margin-bottom: 8px;
        }
        .button-group {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 12px;
        }
        button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #1177bb;
        }
        button:disabled {
            background: #3e3e3e;
            color: #666;
            cursor: not-allowed;
        }
        .panel-controls {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }
        .panel-btn {
            padding: 4px 8px;
            font-size: 11px;
            background: #3e3e3e;
        }
        .panel-btn.active {
            background: #0e639c;
        }
        code {
            background: #1e1e1e;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #9cdcfe;
        }
        .build-status {
            background: #2d2d2d;
            border: 1px solid #3e3e3e;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
        }
        .feature-list {
            list-style: none;
            padding: 0;
        }
        .feature-list li {
            padding: 8px 0;
            border-bottom: 1px solid #3e3e3e;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .feature-list li:last-child {
            border-bottom: none;
        }
        .feature-icon {
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .loading {
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid #3e3e3e;
            border-top-color: #4ec9b0;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Lucid Orchestrator Dashboard</h1>
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot" id="daemonStatus"></div>
                <span>Daemon</span>
            </div>
            <div class="status-item">
                <div class="status-dot" id="mcpStatus"></div>
                <span>MCP</span>
            </div>
            <div class="status-item">
                <div class="status-dot" id="ragStatus"></div>
                <span>RAG</span>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="section">
            <h3>📦 Panel Position</h3>
            <p>Move this dashboard to different locations:</p>
            <div class="panel-controls">
                <button class="panel-btn" onclick="movePanel('left')">Left</button>
                <button class="panel-btn" onclick="movePanel('right')">Right</button>
                <button class="panel-btn" onclick="movePanel('bottom')">Bottom</button>
                <button class="panel-btn" onclick="movePanel('panel')">Panel</button>
                <button class="panel-btn" onclick="movePanel('floating')">Floating</button>
            </div>
        </div>

        <div class="section">
            <h3>🤖 Model Integration</h3>
            <p>Select AI models for different tasks:</p>
            <div class="button-group">
                <button onclick="selectModel('gemini')">Gemini</button>
                <button onclick="selectModel('cerebras')">Cerebras</button>
                <button onclick="selectModel('auto')">Auto Select</button>
            </div>
            <p style="margin-top: 12px; font-size: 11px; color: #666;">
                Current: <span id="currentModel">Auto</span>
            </p>
        </div>

        <div class="section">
            <h3>🔌 Daemon Connection</h3>
            <p>Connect to AIM-OS daemon for real-time updates:</p>
            <div class="button-group">
                <button onclick="connectDaemon()">Connect</button>
                <button onclick="disconnectDaemon()">Disconnect</button>
                <button onclick="refreshStatus()">Refresh Status</button>
            </div>
            <p style="margin-top: 12px; font-size: 11px; color: #666;">
                URL: <code id="daemonUrl">http://localhost:5000</code>
            </p>
        </div>

        <div class="section">
            <h3>🤖 Agent Management</h3>
            <p>Control and automate Cursor agents:</p>
            <div class="button-group">
                <button onclick="manageAgent('start', 'cursor')">Start Cursor Agent</button>
                <button onclick="manageAgent('stop', 'cursor')">Stop Agent</button>
                <button onclick="manageAgent('configure', 'cursor')">Configure</button>
            </div>
        </div>

        <div class="section">
            <h3>🛠️ MCP Tools</h3>
            <p>Execute MCP tools and manage connections:</p>
            <div class="button-group">
                <button onclick="testMCPTool('store_memory')">Test Store Memory</button>
                <button onclick="testMCPTool('retrieve_memory')">Test Retrieve</button>
                <button onclick="refreshMCPStatus()">Refresh Status</button>
            </div>
        </div>

        <div class="build-status">
            <h3>⚠️ UI Not Loaded</h3>
            <p><strong>Issue:</strong> React UI files not found or failed to load</p>
            <p><strong>Expected:</strong> MainDashboard with tabs (Agents, Chat, Chains, Tools, Timeline, NL Tags)</p>
            <p><strong>What to do:</strong></p>
            <ol style="margin-left: 20px; margin-top: 8px;">
                <li>Check that <code>dist/index.html</code> exists</li>
                <li>Check that <code>dist/assets/*.js</code> files exist</li>
                <li>Reload the extension</li>
                <li>Check Developer Console (F12) for errors</li>
            </ol>
            <p style="margin-top: 12px; color: #ff6b6b;">
                <strong>This is a fallback message. The actual UI should load automatically.</strong>
            </p>
        </div>

        <div class="section">
            <h3>✨ Features</h3>
            <ul class="feature-list">
                <li>
                    <span class="feature-icon">✅</span>
                    <span>Movable panels (left, right, bottom, floating)</span>
                </li>
                <li>
                    <span class="feature-icon">✅</span>
                    <span>Gemini/Cerebras model selection</span>
                </li>
                <li>
                    <span class="feature-icon">✅</span>
                    <span>Agent automation and management</span>
                </li>
                <li>
                    <span class="feature-icon">✅</span>
                    <span>Daemon connection and control</span>
                </li>
                <li>
                    <span class="feature-icon">✅</span>
                    <span>MCP tools integration</span>
                </li>
                <li>
                    <span class="feature-icon">⏳</span>
                    <span>Four-pane consciousness interface (Code, Blueprint, Spec, Timeline)</span>
                </li>
                <li>
                    <span class="feature-icon">⏳</span>
                    <span>Real-time consciousness visualization</span>
                </li>
            </ul>
        </div>
    </div>

    <script src="${scriptUri}"></script>
    <script>
        const vscode = acquireVsCodeApi();
        
        function movePanel(position) {
            vscode.postMessage({ command: 'movePanel', position });
            updateActiveButton(position);
        }
        
        function selectModel(model) {
            vscode.postMessage({ command: 'selectModel', model });
            document.getElementById('currentModel').textContent = model.charAt(0).toUpperCase() + model.slice(1);
        }
        
        function connectDaemon() {
            vscode.postMessage({ command: 'connectDaemon', url: 'http://localhost:5000' });
            updateStatus('daemonStatus', 'connecting');
        }
        
        function disconnectDaemon() {
            vscode.postMessage({ command: 'disconnectDaemon' });
            updateStatus('daemonStatus', 'disconnected');
        }
        
        function refreshStatus() {
            vscode.postMessage({ command: 'getSystemStatus' });
        }
        
        function manageAgent(action, agentId) {
            vscode.postMessage({ command: 'manageAgent', action, agentId });
        }
        
        function testMCPTool(toolId) {
            vscode.postMessage({ command: 'executeMCPTool', toolId, params: {} });
        }
        
        function refreshMCPStatus() {
            vscode.postMessage({ command: 'getSystemStatus' });
        }
        
        function updateActiveButton(position) {
            document.querySelectorAll('.panel-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function updateStatus(elementId, status) {
            const element = document.getElementById(elementId);
            element.className = 'status-dot ' + status;
        }
        
        // Listen for messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.command) {
                case 'statusUpdate':
                    if (message.daemon) updateStatus('daemonStatus', message.daemon);
                    if (message.mcp) updateStatus('mcpStatus', message.mcp);
                    if (message.rag) updateStatus('ragStatus', message.rag);
                    break;
                case 'modelSelected':
                    document.getElementById('currentModel').textContent = message.model;
                    break;
            }
        });
        
        // Initial status check
        refreshStatus();
    </script>
</body>
</html>`;
    }
    async loadInitialState(webview) {
        // Send initial configuration
        webview.postMessage({
            command: 'config',
            config: this._config
        });
        // Check daemon connection
        await this.checkDaemonConnection(webview);
    }
    async handleMovePanel(position) {
        this._config.position = position;
        // Show notification
        vscode.window.showInformationMessage(`Dashboard moved to ${position} panel`);
        // Post message to webview
        if (LucidOrchestratorDashboardProvider._view) {
            LucidOrchestratorDashboardProvider._view.webview.postMessage({
                command: 'panelMoved',
                position
            });
        }
    }
    async handleConnectDaemon(url) {
        this._config.daemon.url = url;
        try {
            // Test connection
            const response = await fetch(`${url}/api/health`);
            if (response.ok) {
                vscode.window.showInformationMessage('✅ Connected to AIM-OS daemon');
                if (LucidOrchestratorDashboardProvider._view) {
                    LucidOrchestratorDashboardProvider._view.webview.postMessage({
                        command: 'statusUpdate',
                        daemon: 'connected'
                    });
                }
            }
            else {
                throw new Error('Daemon not responding');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Failed to connect to daemon: ${error}`);
            if (LucidOrchestratorDashboardProvider._view) {
                LucidOrchestratorDashboardProvider._view.webview.postMessage({
                    command: 'statusUpdate',
                    daemon: 'disconnected'
                });
            }
        }
    }
    async handleSelectModel(model) {
        this._config.models.default = model;
        vscode.window.showInformationMessage(`Model selected: ${model}`);
        if (LucidOrchestratorDashboardProvider._view) {
            LucidOrchestratorDashboardProvider._view.webview.postMessage({
                command: 'modelSelected',
                model
            });
        }
    }
    async handleManageAgent(action, agentId) {
        // This would integrate with Cursor's agent system
        vscode.window.showInformationMessage(`Agent ${action}: ${agentId}`);
        // TODO: Implement actual agent management
    }
    async handleExecuteMCPTool(toolId, params) {
        // This would call the MCP server
        vscode.window.showInformationMessage(`Executing MCP tool: ${toolId}`);
        // TODO: Implement actual MCP tool execution
    }
    async handleMCPCall(webview, message) {
        const { toolName, params, requestId } = message;
        try {
            // Initialize MCP client if not already initialized
            if (!this._mcpClient) {
                this._mcpClient = new mcpClient_1.MCPClient();
            }
            // Remove 'mcp_lucid-mcp_' prefix if present
            const toolNameClean = toolName.replace(/^mcp_lucid-mcp_/, '');
            // Try to call the MCP tool
            let result;
            try {
                // First, try to initialize and call via MCP client
                if (!this._mcpClient.process) {
                    await this._mcpClient.initialize();
                }
                result = await this._mcpClient.callTool(toolNameClean, params || {});
            }
            catch (mcpError) {
                // If MCP client fails, provide helpful error message
                console.error(`MCP client call failed: ${mcpError}`);
                throw new Error(`MCP tool ${toolName} call failed: ${mcpError instanceof Error ? mcpError.message : String(mcpError)}. ` +
                    `Note: Extension MCP bridge requires MCP server connection. ` +
                    `Ensure MCP server is configured in ~/.cursor/mcp.json and running.`);
            }
            // Send success response back to React UI
            webview.postMessage({
                command: 'mcpCallResponse',
                toolName: toolName,
                requestId: requestId,
                success: true,
                result: result
            });
        }
        catch (error) {
            console.error(`Failed to call MCP tool ${toolName}:`, error);
            // Send error response back to React UI
            webview.postMessage({
                command: 'mcpCallResponse',
                toolName: toolName,
                requestId: requestId,
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            });
        }
    }
    async handleGetSystemStatus(webview) {
        // Check all system connections
        const status = {
            daemon: 'disconnected',
            mcp: 'disconnected',
            rag: 'disconnected'
        };
        try {
            const daemonResponse = await fetch(`${this._config.daemon.url}/api/health`);
            if (daemonResponse.ok) {
                status.daemon = 'connected';
            }
        }
        catch (error) {
            // Daemon not available
        }
        // TODO: Check MCP and RAG status
        webview.postMessage({
            command: 'statusUpdate',
            ...status
        });
    }
    async checkDaemonConnection(webview) {
        await this.handleGetSystemStatus(webview);
    }
    static reveal() {
        if (this._view) {
            this._view.show(true);
        }
    }
}
exports.LucidOrchestratorDashboardProvider = LucidOrchestratorDashboardProvider;
LucidOrchestratorDashboardProvider._outputChannel = null;
//# sourceMappingURL=lucidDashboardProvider.js.map