import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { MCPClient } from './mcp/mcpClient';
import { MessageRouter } from './messaging/router';
import { HeartbeatMonitor } from './messaging/heartbeatMonitor';
import { Envelope, createEnvelope } from './messaging/envelope';

/**
 * Webview Provider for AIM-OS UI
 * Creates and manages the React-based webview panel with bulletproof messaging
 */
export class AIMOSWebviewProvider {
    public static currentPanel: vscode.WebviewPanel | undefined = undefined;
    private static context: vscode.ExtensionContext;
    private static mcpClient: MCPClient | null = null;
    private static messageRouter: MessageRouter | null = null;
    private static heartbeatMonitor: HeartbeatMonitor | null = null;
    private static uiSequenceNumber: number = 0; // Sequence number for UI messages

    public static initialize(context: vscode.ExtensionContext) {
        this.context = context;
        // Initialize MCP client for tool calls from React UI
        // Note: This connects to the same MCP server that Cursor uses (via mcp.json)
        this.mcpClient = new MCPClient();
        
        // Initialize message router with bulletproof messaging
        this.messageRouter = new MessageRouter(context, {
            maxRetries: 3,
            retryDelay: 500,
            ackTimeout: 500,
        });
        
        // Initialize heartbeat monitor
        this.heartbeatMonitor = new HeartbeatMonitor(10000);
        
        // Register handlers for common topics
        this.messageRouter.registerHandler('mcp.callTool', async (env) => {
            return await this.handleMCPCallEnvelope(env);
        });
        
        // Cleanup on deactivate
        context.subscriptions.push({
            dispose: () => {
                if (this.heartbeatMonitor) {
                    this.heartbeatMonitor.stop();
                }
                if (this.messageRouter) {
                    // Router will checkpoint on dispose
                }
            }
        });
    }

    /**
     * Get message router instance (for Command Server integration)
     */
    public static getRouter(): MessageRouter | null {
        return this.messageRouter;
    }

    public static createOrShow() {
        // Always use ViewColumn.Beside to open in editor area (next to code)
        // This ensures it opens in the CENTRAL editor area, not sidebar
        const column = vscode.ViewColumn.Beside;

        // If we already have a panel, dispose it first to ensure fresh start
        if (this.currentPanel) {
            this.currentPanel.dispose();
            this.currentPanel = undefined;
        }

        // Create a new panel in EDITOR AREA (not sidebar)
        const panel = vscode.window.createWebviewPanel(
            'aimosUI',
            'AIM-OS Dashboard',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.file(path.join(this.context.extensionPath, 'dist')),
                    vscode.Uri.file(path.join(__dirname, '..', 'dist')), // Source dist for development
                    vscode.Uri.file(path.join(this.context.extensionPath, 'resources'))
                ]
            }
        );

        // Set the webview's initial html content
        panel.webview.html = this.getWebviewContent(panel.webview);

        // Listen for when the panel is disposed
        panel.onDidDispose(
            () => {
                this.currentPanel = undefined;
            },
            null,
            this.context.subscriptions
        );

        // Set webview for router and heartbeat monitor
        if (this.messageRouter) {
            this.messageRouter.setWebview(panel.webview);
        }
        if (this.heartbeatMonitor) {
            this.heartbeatMonitor.setWebview(panel.webview);
            this.heartbeatMonitor.start();
        }

        // Handle messages from the webview
        panel.webview.onDidReceiveMessage(
            async (message) => {
                // Check if this is a new envelope protocol message
                if (message.v === 1 && message.kind) {
                    // New envelope protocol - route through router
                    if (this.messageRouter) {
                        // Set sequence number if missing
                        if (message.dir === 'ui->ext' && message.seq === undefined) {
                            message.seq = ++this.uiSequenceNumber;
                        }
                        await this.messageRouter.route(message);
                    }
                    return;
                }
                
                // Legacy command-based messages (backward compatibility)
                switch (message.command) {
                    case 'alert':
                        vscode.window.showErrorMessage(message.text);
                        return;
                    case 'info':
                        vscode.window.showInformationMessage(message.text);
                        return;
                    case 'mcpCall':
                        // Forward MCP tool calls from React UI to MCP server
                        await this.handleMCPCall(panel.webview, message);
                        return;
                    case 'ready':
                        // React UI has loaded - send initial state
                        panel.webview.postMessage({
                            command: 'initialized',
                            data: {
                                message: 'React UI loaded successfully'
                            }
                        });
                        return;
                }
            },
            null,
            this.context.subscriptions
        );

        this.currentPanel = panel;
    }
    
    /**
     * Handle MCP call via envelope protocol
     */
    private static async handleMCPCallEnvelope(env: Envelope): Promise<Envelope | null> {
        const payload = env.payload as { toolName: string; params: any; requestId?: string };
        if (!payload || !payload.toolName) {
            return createEnvelope('nack', env.topic, 'ext->ui', {
                code: 'INVALID_PAYLOAD',
                message: 'Missing toolName in payload',
            }, { replyTo: env.id });
        }
        
        try {
            // Initialize MCP client if needed
            if (!this.mcpClient) {
                this.mcpClient = new MCPClient();
            }
            
            const toolNameClean = payload.toolName.replace(/^mcp_lucid-mcp_/, '');
            
            try {
                await this.mcpClient.initialize();
            } catch (initError) {
                // Already initialized or initialization failed, continue anyway
                console.log('MCP client initialization check:', initError);
            }
            
            const result = await this.mcpClient.callTool(toolNameClean, payload.params || {});
            
            // Create response envelope
            return createEnvelope('response', env.topic, 'ext->ui', {
                success: true,
                toolName: payload.toolName,
                requestId: payload.requestId,
                result: result,
            }, {
                replyTo: env.id,
                priority: 'high',
            });
        } catch (error: any) {
            // Create error response envelope
            return createEnvelope('response', env.topic, 'ext->ui', {
                success: false,
                toolName: payload.toolName,
                requestId: payload.requestId,
                error: error instanceof Error ? error.message : String(error),
            }, {
                replyTo: env.id,
                priority: 'high',
            });
        }
    }

    public static getWebviewContentStatic(webview: vscode.Webview, context: vscode.ExtensionContext): string {
        // Use the instance method but with context passed in
        const originalContext = this.context;
        this.context = context;
        const content = this.getWebviewContent(webview);
        this.context = originalContext;
        return content;
    }

    private static getWebviewContent(webview: vscode.Webview): string {
        // Try to load the built HTML, or use a fallback
        const distHtmlPath = path.join(this.context.extensionPath, 'dist', 'index.html');
        let htmlContent = '';

        // DEBUG: Log what we're checking
        console.log(`[AIM-OS DEBUG] Extension path: ${this.context.extensionPath}`);
        console.log(`[AIM-OS DEBUG] Looking for HTML at: ${distHtmlPath}`);
        console.log(`[AIM-OS DEBUG] File exists: ${fs.existsSync(distHtmlPath)}`);
        
        // Also check if dist folder exists at all
        const distFolder = path.join(this.context.extensionPath, 'dist');
        console.log(`[AIM-OS DEBUG] dist folder exists: ${fs.existsSync(distFolder)}`);
        if (fs.existsSync(distFolder)) {
            const distFiles = fs.readdirSync(distFolder);
            console.log(`[AIM-OS DEBUG] Files in dist/: ${distFiles.join(', ')}`);
        }
        
        // Check source location too (for development)
        const sourceDistPath = path.join(__dirname, '..', 'dist', 'index.html');
        console.log(`[AIM-OS DEBUG] Source dist path: ${sourceDistPath}`);
        console.log(`[AIM-OS DEBUG] Source dist exists: ${fs.existsSync(sourceDistPath)}`);

        // Try extension path first, then source path (for development)
        let actualHtmlPath = distHtmlPath;
        if (!fs.existsSync(distHtmlPath) && fs.existsSync(sourceDistPath)) {
            console.log(`[AIM-OS DEBUG] ⚠️ Extension path not found, trying source path...`);
            actualHtmlPath = sourceDistPath;
        }
        
        if (fs.existsSync(actualHtmlPath)) {
            htmlContent = fs.readFileSync(actualHtmlPath, 'utf8');
            
            // DEBUG: Log that we found it
            console.log(`[AIM-OS DEBUG] ✅ Found React UI HTML at: ${actualHtmlPath}`);
            console.log(`[AIM-OS DEBUG] ✅ Found React UI HTML! Loading...`);
            
            // Replace all asset paths (scripts and styles) with webview URIs
            // Handle both absolute (/assets/) and relative (./assets/ or assets/) paths
            // ADD CACHE BUSTING: Add timestamp to force fresh load
            const cacheBuster = Date.now();
            htmlContent = htmlContent.replace(
                /(src|href)=["']?(\.?\/?assets\/)([^"'\s>]+)["']?/gi,
                (match, attr, prefix, asset) => {
                    // Try extension path first, then source path (for development)
                    let assetPath = path.join(this.context.extensionPath, 'dist', 'assets', asset);
                    if (!fs.existsSync(assetPath)) {
                        const sourceAssetPath = path.join(__dirname, '..', 'dist', 'assets', asset);
                        if (fs.existsSync(sourceAssetPath)) {
                            assetPath = sourceAssetPath;
                            console.log(`[AIM-OS DEBUG] ⚠️ Using source asset path: ${assetPath}`);
                        }
                    }
                    
                    if (fs.existsSync(assetPath)) {
                        const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
                        // Add cache busting query parameter
                        console.log(`[AIM-OS DEBUG] ✅ Found asset: ${asset} -> ${assetUri}`);
                        return `${attr}="${assetUri}?v=${cacheBuster}"`;
                    }
                    console.error(`[AIM-OS DEBUG] ❌ Asset not found: ${assetPath}`);
                    return match; // Keep original if file doesn't exist
                }
            );
            
            // Inject CSP meta tag to allow scripts and styles from webview
            // Use webview.cspSource for proper CSP
            const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src ${webview.cspSource} https:; script-src ${webview.cspSource} 'unsafe-inline' 'unsafe-eval' https:; style-src ${webview.cspSource} 'unsafe-inline' https:; img-src ${webview.cspSource} https: data:; font-src ${webview.cspSource} https: data:; connect-src ${webview.cspSource} https: ws: wss:;">`;
            
            // Insert CSP after <head> tag if not already present
            if (!htmlContent.includes('Content-Security-Policy')) {
                htmlContent = htmlContent.replace(/<head>/i, `<head>\n    ${cspMeta}`);
            }
            
            // Debug: Log that we're loading React UI
            console.log(`[AIM-OS DEBUG] ✅ Loading React UI from dist/index.html`);
        } else {
            // Fallback HTML if dist not built yet
            console.error(`[AIM-OS DEBUG] ❌ dist/index.html not found at: ${distHtmlPath}`);
            console.error(`[AIM-OS DEBUG] ❌ Extension path: ${this.context.extensionPath}`);
            console.error(`[AIM-OS DEBUG] ❌ Using fallback HTML`);
            htmlContent = this.getFallbackHtml(webview);
        }

        return htmlContent;
    }

    private static getFallbackHtml(webview: vscode.Webview): string {
        const scriptUri = webview.asWebviewUri(
            vscode.Uri.file(path.join(this.context.extensionPath, 'dist', 'assets', 'index.js'))
        );
        const styleUri = webview.asWebviewUri(
            vscode.Uri.file(path.join(this.context.extensionPath, 'dist', 'assets', 'index.css'))
        );
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIM-OS Dashboard</title>
    <link rel="stylesheet" href="${styleUri}">
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .status {
            background: #2d2d2d;
            border: 1px solid #3e3e3e;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .status h3 {
            margin-top: 0;
            color: #4ec9b0;
        }
        .build-status {
            background: #2d2d2d;
            border: 1px solid #3e3e3e;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .build-status code {
            background: #1e1e1e;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AIM-OS Dashboard</h1>
            <p>Building UI layout... Please wait.</p>
        </div>
        
        <div class="status">
            <h3>⚠️ UI Not Loaded</h3>
            <p><strong>Expected:</strong> MainDashboard with tabs (Agents, Chat, Chains, Tools, Timeline, NL Tags)</p>
            <p><strong>What happened:</strong> React UI files not found or failed to load</p>
        </div>

        <div class="status">
            <h3>🔧 Troubleshooting</h3>
            <ol>
                <li>Check that <code>dist/index.html</code> exists in extension directory</li>
                <li>Check that <code>dist/assets/*.js</code> files exist</li>
                <li>Check Developer Console (F12) for errors</li>
                <li>Reload the extension</li>
                <li>If still broken, rebuild: <code>cd packages/ide_chat_app && npm run build</code></li>
            </ol>
        </div>

        <div class="build-status">
            <h3>📋 Current Status</h3>
            <p><strong>This is a fallback message.</strong> The actual MainDashboard UI should load automatically if files are present.</p>
            <p style="color: #ff6b6b;">If you see this message, there's a problem with the build or file paths.</p>
        </div>
    </div>
    
    <script src="${scriptUri}"></script>
</body>
</html>`;
    }

    private static async handleMCPCall(webview: vscode.Webview, message: any) {
        const { toolName, params, requestId } = message;
        
        try {
            // Initialize MCP client if not already initialized
            if (!this.mcpClient) {
                this.mcpClient = new MCPClient();
            }

            // Remove 'mcp_lucid-mcp_' prefix if present (MCP tools may or may not have this prefix)
            const toolNameClean = toolName.replace(/^mcp_lucid-mcp_/, '');
            
            // Try to call the MCP tool
            // Note: The MCPClient will need to connect to the MCP server
            // Since Cursor manages the server, we may need to read mcp.json config
            let result;
            try {
                // First, try to initialize and call via MCP client
                // Initialize if not already initialized (check by trying to call)
                try {
                    await this.mcpClient.initialize();
                } catch (initError) {
                    // Already initialized or initialization failed, continue anyway
                    console.log('MCP client initialization check:', initError);
                }
                result = await this.mcpClient.callTool(toolNameClean, params || {});
            } catch (mcpError) {
                // If MCP client fails, try alternative approach
                // Read mcp.json to get server config and connect directly
                console.error(`MCP client call failed: ${mcpError}`);
                
                // Fallback: Try to use Cursor's MCP API if available
                // Unfortunately, VS Code extensions don't have direct access to Cursor's MCP tools
                // So we'll return an error explaining the limitation
                throw new Error(
                    `MCP tool ${toolName} call failed: ${mcpError instanceof Error ? mcpError.message : String(mcpError)}. ` +
                    `Note: Extension MCP bridge requires MCP server connection. ` +
                    `Ensure MCP server is configured in ~/.cursor/mcp.json and running.`
                );
            }
            
            // Send success response back to React UI
            webview.postMessage({
                command: 'mcpCallResponse',
                toolName: toolName,
                requestId: requestId,
                success: true,
                result: result
            });
        } catch (error) {
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

    public static postMessage(message: any) {
        if (this.currentPanel) {
            this.currentPanel.webview.postMessage(message);
        }
    }
}
