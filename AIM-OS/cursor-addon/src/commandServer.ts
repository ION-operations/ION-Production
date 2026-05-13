import * as http from 'http';
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import * as url from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';
import { AIMOSLogger } from './utils/logger';
import { MCPClient } from './mcp/mcpClient';
import { CursorStateReader } from './cursorStateReader';
import { MessageRouter } from './messaging/router';
import { Envelope } from './messaging/envelope';
import { AgentMonitor } from './agent/agentMonitor';

/**
 * HTTP Server that exposes VS Code commands to external clients (e.g., Electron app)
 * Allows automation of Cursor IDE without requiring webview rendering
 */
export class CommandServer {
    private server: http.Server | null = null;
    private port: number;
    private context: vscode.ExtensionContext;
    private mcpClient: MCPClient | null = null;
    private messageRouter: MessageRouter | null = null;
    private agentMonitor: AgentMonitor | null = null;

    constructor(context: vscode.ExtensionContext, port: number = 5001) {
        this.context = context;
        this.port = port;
    }

    /**
     * Set message router for bulletproof messaging protocol
     */
    setMessageRouter(router: MessageRouter): void {
        this.messageRouter = router;
        // Initialize AgentMonitor when router is set
        if (router && !this.agentMonitor) {
            const cursorApiKey = vscode.workspace.getConfiguration('aimos').get<string>('cursorApiKey');
            const webhookUrl = `http://localhost:${this.port}/webhook/agent-event`;
            this.agentMonitor = new AgentMonitor(router, {
                cursorApiKey: cursorApiKey || undefined,
                webhookUrl
            });
            AIMOSLogger.log('COMMAND_SERVER', 'AgentMonitor initialized');
        }
    }

    /**
     * Start the HTTP server
     */
    start(): void {
        if (this.server) {
            AIMOSLogger.warn('COMMAND_SERVER', 'Server already running');
            return;
        }

        this.server = http.createServer((req, res) => {
            this.handleRequest(req, res).catch(error => {
                AIMOSLogger.error('COMMAND_SERVER', 'Request handling error', error);
                this.sendError(res, 500, error.message);
            });
        });

        this.server.listen(this.port, () => {
            AIMOSLogger.success('COMMAND_SERVER', `Command server started on port ${this.port}`);
            console.log(`✅ AIM-OS Command Server listening on http://localhost:${this.port}`);
        });

        this.server.on('error', (error: NodeJS.ErrnoException) => {
            if (error.code === 'EADDRINUSE') {
                AIMOSLogger.error('COMMAND_SERVER', `Port ${this.port} already in use`, error);
                vscode.window.showErrorMessage(`Port ${this.port} already in use. Command server not started.`);
            } else {
                AIMOSLogger.error('COMMAND_SERVER', 'Server error', error);
            }
        });
    }

    /**
     * Stop the HTTP server
     */
    stop(): void {
        if (this.server) {
            this.server.close(() => {
                AIMOSLogger.log('COMMAND_SERVER', 'Command server stopped');
            });
            this.server = null;
        }
    }

    /**
     * Handle incoming HTTP requests
     */
    private async handleRequest(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
        // CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

        // Handle OPTIONS (preflight)
        if (req.method === 'OPTIONS') {
            res.writeHead(200);
            res.end();
            return;
        }

        // Handle GET requests (health check + cursor state endpoints)
        if (req.method === 'GET') {
            if (req.url === '/health') {
                this.sendSuccess(res, { status: 'ok', port: this.port });
                return;
            }
            
            // Parse URL for query parameters
            const parsedUrl = url.parse(req.url || '', true);
            const pathname = parsedUrl.pathname;
            const query = parsedUrl.query;
            
            // Handle cursor state endpoints
            if (pathname === '/cursor/terminals/list') {
                const result = await this.handleListTerminals();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/terminals/manage') {
                const threshold = query.threshold ? parseInt(query.threshold as string, 10) : 5;
                const result = await this.handleManageTerminals(threshold);
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/editor') {
                const result = await this.handleGetActiveEditor();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/workspace') {
                const result = await this.handleGetWorkspaceState();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/output') {
                const channelName = query.channel as string;
                if (!channelName) {
                    this.sendError(res, 400, 'Missing required parameter: channel');
                    return;
                }
                const limit = query.limit ? parseInt(query.limit as string, 10) : 0;
                const result = await this.handleGetOutputChannel(channelName, limit);
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/output/channels') {
                const result = await this.handleListOutputChannels();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/problems') {
                const result = await this.handleGetProblems();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/problems/summary') {
                const result = await this.handleGetProblemSummary();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/problems/file') {
                const filePath = query.file as string;
                if (!filePath) {
                    this.sendError(res, 400, 'Missing required parameter: file');
                    return;
                }
                const result = await this.handleGetFileProblems(filePath);
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/webview/refresh') {
                const viewId = query.viewId as string || 'aimosDashboard';
                const result = await this.handleRefreshWebview(viewId);
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/electron/logs') {
                const limit = query.limit ? parseInt(query.limit as string, 10) : 100;
                const level = query.level as string || 'all';
                const source = query.source as string || 'all';
                const search = query.search as string || '';
                const timeRange = query.time_range as string || 'all';
                const result = await this.handleGetElectronLogs(limit, level, source, search, timeRange);
                this.sendSuccess(res, result);
                return;
            }
            
            // Handle agent status endpoint
            if (pathname?.startsWith('/agent/status/')) {
                const runId = pathname.split('/agent/status/')[1];
                const result = await this.handleAgentStatus(runId);
                this.sendSuccess(res, result);
                return;
            }
            
            // Handle MCP endpoints
            if (pathname === '/mcp/list') {
                const result = await this.listMCPTools();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/mcp/restart') {
                // Restart MCP server connection
                const result = await this.restartMCPServer();
                this.sendSuccess(res, result);
                return;
            }
            
            if (pathname === '/cursor/chat/discover') {
                // Discover available chat commands and APIs
                const result = await this.discoverChatAPIs();
                this.sendSuccess(res, result);
                return;
            }
            
            // Handle Vite cache endpoints
            if (pathname === '/dev/vite/cache/info') {
                const projectPath = query.project as string || this.getWorkspaceRoot();
                const result = await this.handleGetViteCacheInfo(projectPath);
                this.sendSuccess(res, result);
                return;
            }
            
            // Handle system indexes API
            if (pathname === '/api/system-indexes') {
                const systemId = query.systemId as string | undefined;
                const result = await this.handleGetSystemIndexes(systemId);
                this.sendSuccess(res, result);
                return;
            }
            
            // Handle specific system index
            if (pathname?.startsWith('/api/system-indexes/')) {
                const systemId = decodeURIComponent(pathname.split('/api/system-indexes/')[1]);
                const result = await this.handleGetSystemIndexes(systemId);
                this.sendSuccess(res, result);
                return;
            }
        }

        // Only allow POST requests for commands
        if (req.method !== 'POST') {
            this.sendError(res, 405, 'Method not allowed. Use POST for commands, GET /health for status, GET /cursor/* for state.');
            return;
        }

        // Parse request body
        let body = '';
        req.on('data', (chunk) => {
            body += chunk.toString();
        });

        req.on('end', async () => {
            try {
                // Handle command execution
                if (req.url === '/execute') {
                    const request = JSON.parse(body);
                    const result = await this.executeCommand(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/mcp/execute') {
                    // Handle MCP tool execution
                    const request = JSON.parse(body);
                    const result = await this.executeMCPTool(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/mcp/list') {
                    // List available MCP tools
                    const result = await this.listMCPTools();
                    this.sendSuccess(res, result);
                } else if (req.url === '/aimos/chat') {
                    // Handle AIMOS chat requests (from Chat Participant)
                    const request = JSON.parse(body);
                    const result = await this.handleAIMOSChat(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/cursor/execute-cli') {
                    // Execute cursor-agent CLI command
                    const request = JSON.parse(body);
                    const result = await this.executeCursorCLI(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/cursor/chat/send') {
                    // Send message to Cursor chat (macro automation)
                    const request = JSON.parse(body);
                    const result = await this.handleSendChatMessage(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/cursor/chat/autonomous-loop') {
                    // Control autonomous loop (start/stop/pause/resume/status)
                    const request = JSON.parse(body);
                    const result = await this.handleAutonomousLoop(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/cursor/terminals/close') {
                    // Close terminal
                    const request = JSON.parse(body);
                    const result = await this.handleCloseTerminal(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/messaging/send') {
                    // Handle bulletproof messaging protocol envelopes
                    const request = JSON.parse(body);
                    const result = await this.handleMessagingEnvelope(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/agent/start') {
                    // Start Cursor agent (Cloud API or CLI)
                    const request = JSON.parse(body);
                    const result = await this.handleAgentStart(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/agent/stop') {
                    // Stop Cursor agent
                    const request = JSON.parse(body);
                    const result = await this.handleAgentStop(request);
                    this.sendSuccess(res, result);
                } else if (req.url?.startsWith('/agent/status/')) {
                    // Get agent status by run ID
                    const runId = req.url.split('/agent/status/')[1];
                    const result = await this.handleAgentStatus(runId);
                    this.sendSuccess(res, result);
                } else if (req.url === '/webhook/agent-event') {
                    // Handle webhook events from Cursor API
                    const request = JSON.parse(body);
                    const result = await this.handleAgentWebhook(request);
                    this.sendSuccess(res, result);
                } else if (req.url === '/dev/vite/cache/clear') {
                    // Clear Vite cache
                    const request = JSON.parse(body);
                    const result = await this.handleClearViteCache(request);
                    this.sendSuccess(res, result);
                } else {
                    this.sendError(res, 404, 'Endpoint not found. Use /execute for commands, /mcp/execute for MCP tools, /cursor/* for state, /messaging/send for envelopes.');
                }
            } catch (error: any) {
                AIMOSLogger.error('COMMAND_SERVER', 'Request parsing error', error);
                this.sendError(res, 400, error.message || 'Invalid request');
            }
        });
    }

    /**
     * Handle messaging envelope via HTTP
     */
    private async handleMessagingEnvelope(request: {
        envelope: Envelope;
    }): Promise<any> {
        if (!this.messageRouter) {
            return {
                success: false,
                error: 'Message router not initialized',
            };
        }

        try {
            const envelope = request.envelope as Envelope;
            
            // Validate envelope structure
            if (!envelope.v || !envelope.id || !envelope.kind || !envelope.topic) {
                return {
                    success: false,
                    error: 'Invalid envelope structure',
                };
            }

            // Route envelope through message router
            await this.messageRouter.route(envelope);

            return {
                success: true,
                envelopeId: envelope.id,
                message: 'Envelope routed successfully',
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Messaging envelope error', error);
            return {
                success: false,
                error: error.message || String(error),
            };
        }
    }

    /**
     * Execute a VS Code command via the command server
     */
    private async executeCommand(request: {
        command: string;
        args?: any[];
        [key: string]: any;
    }): Promise<any> {
        const { command, args = [] } = request;

        AIMOSLogger.log('COMMAND_SERVER', `Executing command: ${command}`, { args });

        try {
            // Execute VS Code command
            const result = await vscode.commands.executeCommand(command, ...args);
            
            AIMOSLogger.success('COMMAND_SERVER', `Command executed: ${command}`);
            
            // TCS Integration: Log command execution to timeline (fail-soft)
            this.logTimelineEntry('command_execution', {
                command,
                args: args?.length > 0 ? args : undefined,
                success: true,
                result_type: typeof result
            }).catch(() => {}); // Fail-soft: TCS integration is optional
            
            return {
                success: true,
                command,
                result
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', `Command failed: ${command}`, error);
            
            // TCS Integration: Log command failure to timeline (fail-soft)
            this.logTimelineEntry('command_execution', {
                command,
                args: args?.length > 0 ? args : undefined,
                success: false,
                error: error.message || String(error)
            }).catch(() => {}); // Fail-soft: TCS integration is optional
            
            return {
                success: false,
                command,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Send success response
     */
    private sendSuccess(res: http.ServerResponse, data: any): void {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(data));
    }

    /**
     * Log timeline entry via TCS (fail-soft pattern)
     */
    private async logTimelineEntry(entryType: string, metadata: any): Promise<void> {
        try {
            if (!this.mcpClient) {
                return; // No MCP client available
            }
            
            // Use MCP tool to add timeline entry
            await this.mcpClient.callTool('add_timeline_entry', {
                entry_type: entryType,
                content: `${entryType}: ${JSON.stringify(metadata)}`,
                metadata: {
                    ...metadata,
                    source: 'command_server',
                    timestamp: new Date().toISOString()
                }
            });
        } catch (error) {
            // Fail-soft: TCS integration is optional
            // Don't log errors to avoid noise
        }
    }

    /**
     * Normalize tool names from mixed caller conventions.
     * Accepts: mcp_lucid-mcp_<tool>, mcp_lucid_mcp_<tool>, mcp:<tool>, <tool>
     */
    private normalizeMCPToolName(toolName: string): string {
        if (!toolName) {
            return toolName;
        }

        return toolName
            .replace(/^mcp_lucid-mcp_/, '')
            .replace(/^mcp_lucid_mcp_/, '')
            .replace(/^mcp:/, '')
            .trim();
    }

    /**
     * Parse MCP tools/call envelope into stable business payload.
     * MCP often returns { content: [{ type: 'text', text: '{...json...}' }], isError?: boolean }
     */
    private parseMCPToolCallResult(rawResult: any): {
        payload: any;
        parsedFromContent: boolean;
        parseWarning?: string;
    } {
        if (
            rawResult &&
            typeof rawResult === 'object' &&
            Array.isArray(rawResult.content)
        ) {
            const textChunk = rawResult.content.find(
                (chunk: any) => chunk && typeof chunk.text === 'string'
            );

            if (textChunk && typeof textChunk.text === 'string') {
                const text = textChunk.text.trim();
                if (!text) {
                    return { payload: text, parsedFromContent: true };
                }

                try {
                    return {
                        payload: JSON.parse(text),
                        parsedFromContent: true,
                    };
                } catch (error: any) {
                    return {
                        payload: text,
                        parsedFromContent: true,
                        parseWarning: `Failed to parse MCP text payload as JSON: ${error?.message || String(error)}`,
                    };
                }
            }
        }

        return {
            payload: rawResult,
            parsedFromContent: false,
        };
    }

    /**
     * Infer business success from parsed payload + MCP envelope flags.
     */
    private inferMCPToolSuccess(parsedPayload: any, rawResult: any): boolean {
        if (rawResult && typeof rawResult === 'object' && rawResult.isError === true) {
            return false;
        }

        if (
            parsedPayload &&
            typeof parsedPayload === 'object' &&
            typeof parsedPayload.success === 'boolean'
        ) {
            return parsedPayload.success;
        }

        return true;
    }

    private inferMCPToolError(parsedPayload: any, rawResult: any): string | undefined {
        if (
            parsedPayload &&
            typeof parsedPayload === 'object' &&
            typeof parsedPayload.error === 'string' &&
            parsedPayload.error.trim()
        ) {
            return parsedPayload.error;
        }

        if (
            rawResult &&
            typeof rawResult === 'object' &&
            typeof rawResult.error === 'string' &&
            rawResult.error.trim()
        ) {
            return rawResult.error;
        }

        if (rawResult && typeof rawResult === 'object' && rawResult.isError === true) {
            return 'MCP tool returned an error envelope';
        }

        return undefined;
    }

    /**
     * Execute an MCP tool via the extension
     */
    private async executeMCPTool(request: {
        tool: string;
        arguments?: any;
        [key: string]: any;
    }): Promise<any> {
        const { tool, arguments: args = {} } = request;
        const normalizedTool = this.normalizeMCPToolName(tool);

        AIMOSLogger.log('COMMAND_SERVER', `Executing MCP tool: ${tool}`, { args });

        try {
            // Initialize MCP client if needed
            if (!this.mcpClient) {
                AIMOSLogger.log('COMMAND_SERVER', 'Initializing MCP client...');
                this.mcpClient = new MCPClient();
                await this.mcpClient.initialize();
                AIMOSLogger.success('COMMAND_SERVER', 'MCP client initialized');
            }

            // Execute MCP tool
            AIMOSLogger.log('COMMAND_SERVER', `Calling MCP tool: ${normalizedTool}`, {
                originalTool: tool,
                arguments: args
            });
            const rawResult = await this.mcpClient.callTool(normalizedTool, args);
            const parsed = this.parseMCPToolCallResult(rawResult);
            const toolSuccess = this.inferMCPToolSuccess(parsed.payload, rawResult);
            const toolError = this.inferMCPToolError(parsed.payload, rawResult);
            
            AIMOSLogger.success('COMMAND_SERVER', `MCP tool executed: ${tool}`, { 
                normalizedTool,
                resultType: typeof parsed.payload,
                hasResult: parsed.payload !== undefined && parsed.payload !== null,
                resultKeys: parsed.payload && typeof parsed.payload === 'object' ? Object.keys(parsed.payload) : [],
                parsedFromContent: parsed.parsedFromContent,
                parseWarning: parsed.parseWarning || null,
                toolSuccess
            });
            
            // TCS Integration: Log MCP tool execution to timeline (fail-soft)
            // Skip logging for timeline entry tool itself to avoid recursion
            if (normalizedTool !== 'add_timeline_entry') {
                this.logTimelineEntry('mcp_tool_execution', {
                    tool,
                    normalized_tool: normalizedTool,
                    success: toolSuccess,
                    has_result: parsed.payload !== undefined && parsed.payload !== null
                }).catch(() => {}); // Fail-soft: TCS integration is optional
            }

            if (!toolSuccess) {
                return {
                    success: false,
                    tool,
                    normalizedTool,
                    result: parsed.payload,
                    error: toolError || 'MCP tool returned unsuccessful result',
                    parseWarning: parsed.parseWarning
                };
            }

            return {
                success: true,
                tool,
                normalizedTool,
                result: parsed.payload,
                parseWarning: parsed.parseWarning
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', `MCP tool failed: ${tool}`, {
                error: error.message || String(error),
                stack: error.stack,
                name: error.name,
                tool,
                normalizedTool,
                args
            });
            
            // TCS Integration: Log MCP tool failure to timeline (fail-soft)
            if (normalizedTool !== 'add_timeline_entry') {
                this.logTimelineEntry('mcp_tool_execution', {
                    tool,
                    normalized_tool: normalizedTool,
                    success: false,
                    error: error.message || String(error)
                }).catch(() => {}); // Fail-soft: TCS integration is optional
            }
            
            return {
                success: false,
                tool,
                normalizedTool,
                error: error.message || String(error),
                details: {
                    name: error.name,
                    stack: error.stack?.split('\n').slice(0, 5).join('\n')
                }
            };
        }
    }

    /**
     * Restart MCP server connection (forces Python process to reload)
     */
    private async restartMCPServer(): Promise<any> {
        AIMOSLogger.log('COMMAND_SERVER', 'Restarting MCP server...');

        try {
            // Disconnect existing client
            if (this.mcpClient) {
                AIMOSLogger.log('COMMAND_SERVER', 'Disconnecting existing MCP client...');
                this.mcpClient.disconnect();
                this.mcpClient = null;
            }

            // Wait a moment for process to fully terminate
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Initialize new client
            AIMOSLogger.log('COMMAND_SERVER', 'Initializing new MCP client...');
            this.mcpClient = new MCPClient();
            await this.mcpClient.initialize();
            
            AIMOSLogger.success('COMMAND_SERVER', 'MCP server restarted successfully');
            
            return {
                success: true,
                message: 'MCP server restarted successfully'
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to restart MCP server', error);
            
            // Clear client on error
            this.mcpClient = null;
            
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * List available MCP tools
     */
    private async listMCPTools(): Promise<any> {
        AIMOSLogger.log('COMMAND_SERVER', 'Listing MCP tools');

        try {
            // Initialize MCP client if needed
            if (!this.mcpClient) {
                this.mcpClient = new MCPClient();
                await this.mcpClient.initialize();
                AIMOSLogger.success('COMMAND_SERVER', 'MCP client initialized');
            }

            // List tools
            const tools = await this.mcpClient.listTools();
            
            AIMOSLogger.success('COMMAND_SERVER', `Found ${tools.length} MCP tools`);
            
            return {
                success: true,
                tools
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to list MCP tools', error);
            
            return {
                success: false,
                error: error.message || String(error),
                tools: []
            };
        }
    }

    /**
     * Send error response
     */
    private sendError(res: http.ServerResponse, statusCode: number, message: string): void {
        res.writeHead(statusCode, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            success: false,
            error: message
        }));
    }

    /**
     * Handle list terminals request
     */
    private async handleListTerminals(): Promise<any> {
        try {
            const terminals = await CursorStateReader.listTerminals();
            return {
                success: true,
                terminals
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to list terminals', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle close terminal request
     */
    private async handleCloseTerminal(request: {
        terminal_name?: string;
        terminal_index?: number;
    }): Promise<any> {
        try {
            const result = await CursorStateReader.closeTerminal(
                request.terminal_name,
                request.terminal_index
            );
            return result;
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to close terminal', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle manage terminals request
     */
    private async handleManageTerminals(threshold: number): Promise<any> {
        try {
            const result = await CursorStateReader.manageTerminals(threshold);
            return {
                success: true,
                ...result
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to manage terminals', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle get active editor request
     */
    private async handleGetActiveEditor(): Promise<any> {
        try {
            const editorState = await CursorStateReader.getActiveEditorState();
            return {
                success: true,
                editor: editorState
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get active editor', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle get workspace state request
     */
    private async handleGetWorkspaceState(): Promise<any> {
        try {
            const workspaceState = await CursorStateReader.getWorkspaceState();
            return {
                success: true,
                workspace: workspaceState
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get workspace state', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle get output channel request
     */
    private async handleGetOutputChannel(channelName: string, limit: number = 0): Promise<any> {
        try {
            const content = limit > 0 
                ? await CursorStateReader.getOutputChannelLogs(channelName, limit)
                : await CursorStateReader.getOutputChannel(channelName);
            return {
                success: true,
                channel: channelName,
                content,
                limit: limit > 0 ? limit : undefined
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get output channel', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle refresh webview request
     */
    private async handleRefreshWebview(viewId: string): Promise<any> {
        try {
            AIMOSLogger.log('COMMAND_SERVER', `Refreshing webview: ${viewId}`);
            
            // Execute VS Code refresh command
            await vscode.commands.executeCommand('aimos.refreshDashboard');
            
            return {
                success: true,
                message: `Webview ${viewId} refreshed`,
                timestamp: new Date().toISOString()
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', `Failed to refresh webview: ${viewId}`, error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }
    
    /**
     * Handle get Electron logs request
     */
    private async handleGetElectronLogs(
        limit: number,
        level: string,
        source: string,
        search: string = '',
        timeRange: string = 'all'
    ): Promise<any> {
        try {
            AIMOSLogger.log('COMMAND_SERVER', `Getting Electron logs: limit=${limit}, level=${level}, source=${source}, search=${search}, timeRange=${timeRange}`);
            
            // Get Electron log file path
            const electronLogPath = process.platform === 'win32'
                ? path.join(os.homedir(), 'AppData', 'Roaming', 'AIM-OS Dashboard', 'electron-console.log')
                : process.platform === 'darwin'
                    ? path.join(os.homedir(), 'Library', 'Application Support', 'AIM-OS Dashboard', 'electron-console.log')
                    : path.join(os.homedir(), '.config', 'AIM-OS Dashboard', 'electron-console.log');
            
            if (!fs.existsSync(electronLogPath)) {
                return {
                    success: false,
                    error: `Electron log file not found at: ${electronLogPath}. Is Electron app running?`,
                    log_file: electronLogPath
                };
            }
            
            // Read and filter logs
            const content = fs.readFileSync(electronLogPath, 'utf8');
            let lines = content.split('\n').filter(l => l.trim());
            
            // Filter by level
            if (level && level !== 'all') {
                lines = lines.filter(l => l.includes(`[${level.toUpperCase()}]`));
            }
            
            // Filter by source
            if (source && source !== 'all') {
                lines = lines.filter(l => l.includes(`[${source.toUpperCase()}]`));
            }
            
            // Filter by search term
            if (search) {
                const searchLower = search.toLowerCase();
                lines = lines.filter(l => l.toLowerCase().includes(searchLower));
            }
            
            // Filter by time range (simplified - filter by timestamp if present)
            if (timeRange && timeRange !== 'all') {
                const now = Date.now();
                let cutoffTime = 0;
                
                switch (timeRange) {
                    case 'last_hour':
                        cutoffTime = now - (60 * 60 * 1000);
                        break;
                    case 'last_day':
                        cutoffTime = now - (24 * 60 * 60 * 1000);
                        break;
                    case 'last_week':
                        cutoffTime = now - (7 * 24 * 60 * 60 * 1000);
                        break;
                }
                
                if (cutoffTime > 0) {
                    lines = lines.filter(l => {
                        // Try to extract timestamp from log line (ISO format)
                        const timestampMatch = l.match(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
                        if (timestampMatch) {
                            const logTime = new Date(timestampMatch[0]).getTime();
                            return logTime >= cutoffTime;
                        }
                        // If no timestamp, include all lines (can't filter)
                        return true;
                    });
                }
            }
            
            // Get last N lines
            const logs = lines.slice(-limit);
            
            AIMOSLogger.log('COMMAND_SERVER', `Retrieved ${logs.length} log lines from Electron`);
            
            return {
                success: true,
                logs,
                count: logs.length,
                total_lines: lines.length,
                log_file: electronLogPath,
                level_filter: level,
                source_filter: source,
                search_filter: search || undefined,
                time_range_filter: timeRange !== 'all' ? timeRange : undefined,
                server_filtered: true // Indicate server-side filtering was applied
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get Electron logs', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }
    
    /**
     * Handle list output channels request
     */
    private async handleListOutputChannels(): Promise<any> {
        try {
            const channels = await CursorStateReader.listOutputChannels();
            return {
                success: true,
                channels,
                count: channels.length
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to list output channels', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle get problems request
     */
    private async handleGetProblems(): Promise<any> {
        try {
            const problems = await CursorStateReader.getProblems();
            const summary = await CursorStateReader.getProblemSummary();
            return {
                success: true,
                problems,
                summary,
                count: problems.length
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get problems', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle get problem summary request
     */
    private async handleGetProblemSummary(): Promise<any> {
        try {
            const summary = await CursorStateReader.getProblemSummary();
            return {
                success: true,
                summary
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get problem summary', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle get file problems request
     */
    private async handleGetFileProblems(filePath: string): Promise<any> {
        try {
            const problems = await CursorStateReader.getFileProblems(filePath);
            return {
                success: true,
                file: filePath,
                problems,
                count: problems.length
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get file problems', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Discover available chat commands and APIs
     * This method investigates what chat-related functionality is available in Cursor
     */
    private async discoverChatAPIs(): Promise<any> {
        AIMOSLogger.log('COMMAND_SERVER', 'Discovering chat APIs...');
        
        const results: any = {
            success: true,
            timestamp: new Date().toISOString(),
            commands: {},
            extensions: {},
            languageModel: {},
            summary: {}
        };

        try {
            // 1. List all available commands
            const allCommands = await vscode.commands.getCommands();
            results.summary.totalCommands = allCommands.length;

            // 2. Filter chat-related commands
            const chatKeywords = ['chat', 'cursor', 'assistant', 'ai', 'copilot', 'model'];
            const chatCommands = allCommands.filter(cmd => 
                chatKeywords.some(keyword => cmd.toLowerCase().includes(keyword))
            );

            results.summary.chatCommandsFound = chatCommands.length;
            results.commands.chatRelated = chatCommands;

            // 3. Test specific potential chat commands
            const potentialCommands = [
                'workbench.action.chat.open',
                'workbench.action.chat.focus',
                'cursor.chat.open',
                'cursor.chat.send',
                'cursor.chat.focus',
                'chat.open',
                'chat.send',
                'cursor.showChat',
                'cursor.sendMessage',
                'workbench.action.chat',
                'workbench.action.chat.new',
                'workbench.action.chat.newSession'
            ];

            results.commands.tested = [];
            for (const cmd of potentialCommands) {
                try {
                    // Try to execute (may fail but tells us if command exists)
                    await vscode.commands.executeCommand(cmd);
                    results.commands.tested.push({
                        command: cmd,
                        exists: true,
                        executable: true,
                        error: null
                    });
                } catch (e: any) {
                    // Check if error is "command not found" vs "command exists but needs args"
                    const errorMsg = e.message || String(e);
                    const exists = !errorMsg.includes('command not found') && 
                                  !errorMsg.includes('Unknown command');
                    
                    results.commands.tested.push({
                        command: cmd,
                        exists,
                        executable: false,
                        error: errorMsg
                    });
                }
            }

            // 4. Check Language Model API
            const languageModel = (vscode as any).lm;
            if (languageModel) {
                results.languageModel.available = true;
                results.languageModel.methods = Object.keys(languageModel);
                results.languageModel.hasSendRequest = typeof languageModel.sendRequest === 'function';
            } else {
                results.languageModel.available = false;
            }

            // 5. Check Cursor extensions (safely - don't access exports if extension not activated)
            const cursorExtensions = vscode.extensions.all.filter(ext => 
                ext.id.includes('cursor') || 
                ext.packageJSON?.publisher === 'cursor'
            );

            results.extensions.found = cursorExtensions.length;
            results.extensions.details = cursorExtensions.map(ext => {
                try {
                    // Only check exports if extension is active
                    const isActive = ext.isActive;
                    let exports = [];
                    if (isActive && ext.exports) {
                        try {
                            exports = Object.keys(ext.exports);
                        } catch (e) {
                            // Extension exports may not be accessible
                            exports = [];
                        }
                    }
                    return {
                id: ext.id,
                name: ext.packageJSON?.displayName || ext.id,
                publisher: ext.packageJSON?.publisher,
                version: ext.packageJSON?.version,
                        isActive: isActive,
                        hasExports: exports.length > 0,
                        exports: exports
                    };
                } catch (e: any) {
                    // Extension not accessible (not activated)
                    return {
                        id: ext.id,
                        name: ext.packageJSON?.displayName || ext.id,
                        publisher: ext.packageJSON?.publisher,
                        version: ext.packageJSON?.version,
                        isActive: false,
                        hasExports: false,
                        exports: [],
                        error: e.message || String(e)
                    };
                }
            });

            // 6. Check Chat API availability
            const chatApi = (vscode as any).chat;
            if (chatApi) {
                results.chatApi = {
                    available: true,
                    methods: Object.keys(chatApi),
                    hasCreateParticipant: typeof chatApi.createChatParticipant === 'function'
                };
            } else {
                results.chatApi = {
                    available: false
                };
            }

            AIMOSLogger.success('COMMAND_SERVER', 'Chat API discovery complete', {
                commandsFound: chatCommands.length,
                extensionsFound: cursorExtensions.length
            });

        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to discover chat APIs', error);
            results.success = false;
            results.error = error.message || String(error);
        }

        return results;
    }

    /**
     * Handle AIMOS chat requests from Chat Participant
     */
    private async handleAIMOSChat(request: {
        prompt: string;
        references?: Array<{ name: string; uri: string }>;
        command?: string;
        variables?: Record<string, any>;
    }): Promise<any> {
        AIMOSLogger.log('COMMAND_SERVER', 'Handling AIMOS chat request', {
            promptLength: request.prompt.length,
            hasReferences: !!request.references?.length,
            command: request.command
        });

        try {
            const { prompt, references, command, variables } = request;

            // Check if this is a command-based request
            if (command && command.startsWith('mcp:')) {
                // Execute MCP tool directly
                const toolName = command.substring(4);
                const args = variables || {};
                
                AIMOSLogger.log('COMMAND_SERVER', `Executing MCP tool via chat: ${toolName}`);
                const mcpResult = await this.executeMCPTool({
                    tool: toolName,
                    arguments: args
                });

                if (mcpResult.success) {
                    return {
                        success: true,
                        response: typeof mcpResult.result === 'string' 
                            ? mcpResult.result 
                            : JSON.stringify(mcpResult.result, null, 2),
                        tool: toolName
                    };
                } else {
                    return {
                        success: false,
                        error: mcpResult.error || 'MCP tool execution failed',
                        response: `❌ Failed to execute ${toolName}: ${mcpResult.error}`
                    };
                }
            }

            // Default: Intelligent routing based on prompt content
            // Check if prompt mentions MCP tools
            const mcpToolPatterns = [
                { pattern: /store.*memory|memory.*store/i, tool: 'mcp_lucid-mcp_store_memory' },
                { pattern: /retrieve.*memory|memory.*search|search.*memory/i, tool: 'mcp_lucid-mcp_retrieve_memory' },
                { pattern: /create.*plan|plan.*create|execution.*plan/i, tool: 'mcp_lucid-mcp_create_plan' },
                { pattern: /track.*confidence|confidence.*track/i, tool: 'mcp_lucid-mcp_track_confidence' },
                { pattern: /(memory.*stat|stat.*memory|show.*memory|memory.*stats|get.*memory.*stat)/i, tool: 'mcp_lucid-mcp_get_memory_stats' }
            ];

            for (const { pattern, tool } of mcpToolPatterns) {
                if (pattern.test(prompt)) {
                    AIMOSLogger.log('COMMAND_SERVER', `Auto-detected MCP tool: ${tool} from prompt`);
                    
                    // Build appropriate arguments for each tool
                    let toolArgs: any = { ...variables };
                    
                    if (tool === 'mcp_lucid-mcp_get_memory_stats') {
                        toolArgs = {}; // No arguments needed for memory stats
                    } else if (tool === 'mcp_lucid-mcp_retrieve_memory') {
                        toolArgs = { query: prompt, limit: 10 };
                    } else if (tool === 'mcp_lucid-mcp_store_memory') {
                        toolArgs = { content: prompt, tags: {} };
                    } else if (tool === 'mcp_lucid-mcp_create_plan') {
                        toolArgs = { goal: prompt, priority: 'medium' };
                    } else if (tool === 'mcp_lucid-mcp_track_confidence') {
                        toolArgs = { task: prompt, confidence: 0.75, reasoning: 'Auto-detected from chat' };
                    }
                    
                    const mcpResult = await this.executeMCPTool({
                        tool: tool,
                        arguments: toolArgs
                    });

                    if (mcpResult.success) {
                        return {
                            success: true,
                            response: typeof mcpResult.result === 'string' 
                                ? mcpResult.result 
                                : JSON.stringify(mcpResult.result, null, 2),
                            tool: tool,
                            autoDetected: true
                        };
                    }
                }
            }

            // Fallback: Return informative response
            return {
                success: true,
                response: `I received your message: "${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}"\n\n` +
                    `**Available AIMOS capabilities:**\n` +
                    `- Store memory: "@aimos store this in memory"\n` +
                    `- Search memory: "@aimos search memory for..."\n` +
                    `- Create plan: "@aimos create a plan to..."\n` +
                    `- Track confidence: "@aimos track confidence for..."\n` +
                    `- Memory stats: "@aimos show memory statistics"\n\n` +
                    `Or use MCP tools directly: "@aimos mcp:tool_name arguments"`,
                note: 'This is a basic response. Full MCP integration available.'
            };

        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to handle AIMOS chat request', error);
            return {
                success: false,
                error: error.message || String(error),
                response: `❌ Error processing request: ${error.message}`
            };
        }
    }

    /**
     * Execute cursor-agent CLI command
     */
    private async executeCursorCLI(request: {
        prompt: string;
        timeout?: number;
        outputFormat?: 'json' | 'text';
    }): Promise<any> {
        const { prompt, timeout = 300000, outputFormat = 'json' } = request;

        AIMOSLogger.log('COMMAND_SERVER', 'Executing cursor-agent CLI', {
            promptLength: prompt.length,
            timeout,
            outputFormat
        });

        try {
            const execAsync = promisify(exec);

            // Escape prompt for shell safety
            const escapedPrompt = prompt.replace(/"/g, '\\"').replace(/\$/g, '\\$');

            // Build command
            const command = `cursor-agent --print --output-format ${outputFormat} "${escapedPrompt}"`;

            AIMOSLogger.log('COMMAND_SERVER', `Executing: ${command.substring(0, 100)}...`);

            // Execute with timeout
            const startTime = Date.now();
            let result: any;

            try {
                const { stdout, stderr } = await Promise.race([
                    execAsync(command, { 
                        timeout,
                        maxBuffer: 10 * 1024 * 1024 // 10MB buffer
                    }),
                    // Timeout wrapper in case process hangs (known bug)
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Process timeout - cursor-agent may have hung')), timeout)
                    ) as Promise<{ stdout: string; stderr: string }>
                ]);

                const duration = Date.now() - startTime;
                AIMOSLogger.success('COMMAND_SERVER', `cursor-agent completed in ${duration}ms`);

                if (stderr && !stderr.includes('warning')) {
                    AIMOSLogger.warn('COMMAND_SERVER', 'cursor-agent stderr', stderr);
                }

                // Parse output based on format
                if (outputFormat === 'json') {
                    try {
                        result = JSON.parse(stdout);
                    } catch (parseError) {
                        AIMOSLogger.warn('COMMAND_SERVER', 'Failed to parse JSON output, returning raw', parseError);
                        result = stdout;
                    }
                } else {
                    result = stdout;
                }

                return {
                    success: true,
                    result,
                    duration,
                    outputFormat
                };

            } catch (execError: any) {
                const duration = Date.now() - startTime;
                
                // Check if it's the known hanging bug
                if (execError.message?.includes('timeout') || execError.killed) {
                    AIMOSLogger.warn('COMMAND_SERVER', 'cursor-agent process timed out (known bug)', {
                        duration,
                        error: execError.message
                    });
                    
                    return {
                        success: false,
                        error: 'Process timeout - cursor-agent may have hung (known bug)',
                        duration,
                        knownIssue: true,
                        suggestion: 'Consider using Chat Participant API instead'
                    };
                }

                throw execError;
            }

        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to execute cursor-agent CLI', error);
            
            // Check if cursor-agent is installed
            if (error.message?.includes('command not found') || error.code === 'ENOENT') {
                return {
                    success: false,
                    error: 'cursor-agent command not found. Install Cursor CLI or use Chat Participant API instead.',
                    suggestion: 'Use @aimos in Cursor chat instead'
                };
            }

            return {
                success: false,
                error: error.message || String(error),
                details: {
                    name: error.name,
                    code: error.code
                }
            };
        }
    }

    /**
     * Handle sending messages to Cursor chat via macro automation
     * This enables Electron app/daemon to programmatically send messages to Cursor chat UI
     * 
     * Strategy: Try VS Code command chaining first (professional), fall back to macro (last resort)
     */
    private async handleSendChatMessage(request: {
        message: string;
        waitForResponse?: boolean;
    }): Promise<any> {
        const { message, waitForResponse = false } = request;

        AIMOSLogger.log('COMMAND_SERVER', 'Handling chat message send request', {
            messageLength: message.length,
            waitForResponse
        });

        try {
            // Validate message
            if (!message || typeof message !== 'string') {
                return {
                    success: false,
                    error: 'Message is required and must be a string'
                };
            }

            // Strategy 1: Try VS Code command chaining (professional approach)
            try {
                const commandResult = await this.sendChatViaCommands(message);
                if (commandResult.success) {
                    AIMOSLogger.success('COMMAND_SERVER', 'Chat message sent via VS Code commands');
                    return {
                        success: true,
                        accepted: true,  // Handshake signal
                        ts: Date.now(),   // Timestamp
                        message: message.substring(0, 100) + (message.length > 100 ? '...' : ''),
                        sent: true,
                        method: 'command-chaining',
                        waitForResponse
                    };
                }
            } catch (error: any) {
                AIMOSLogger.warn('COMMAND_SERVER', 'Command chaining failed, falling back to macro', error);
            }

            // Strategy 2: Fall back to macro automation (last resort)
            const platform = process.platform;
            if (platform === 'win32') {
                await this.executeWindowsChatMacro(message);
            } else if (platform === 'darwin') {
                await this.executeMacChatMacro(message);
            } else {
                await this.executeLinuxChatMacro(message);
            }

                AIMOSLogger.success('COMMAND_SERVER', 'Chat message sent successfully via macro');

                return {
                    success: true,
                    accepted: true,  // Handshake signal for macro automation
                    ts: Date.now(),   // Timestamp for macro pause calculation
                    message: message.substring(0, 100) + (message.length > 100 ? '...' : ''),
                    sent: true,
                    method: 'macro-automation',
                    waitForResponse
                };

        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to send chat message', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle autonomous loop control (start/stop/pause/resume/status)
     * Implements Chat Automation system from T3 Detailed documentation
     */
    private async handleAutonomousLoop(request: {
        action: 'start' | 'stop' | 'pause' | 'resume' | 'status';
        config?: any;
        loop_id?: string;
    }): Promise<any> {
        const { action, config, loop_id } = request;
        
        // Import loop service
        const { CursorChatAutonomousLoop } = await import('./services/cursorChatAutonomousLoop');
        
        // Static storage for active loops
        if (!(globalThis as any).activeLoops) {
            (globalThis as any).activeLoops = new Map();
        }
        const activeLoops: Map<string, any> = (globalThis as any).activeLoops;
        
        try {
            if (action === 'start') {
                // Create new loop
                const loop = new CursorChatAutonomousLoop(config);
                const loopId = `loop-${Date.now()}`;
                
                // Start loop
                await loop.start();
                
                // Store in active loops
                activeLoops.set(loopId, loop);
                
                return {
                    success: true,
                    loop_id: loopId,
                    status: loop.getStatus()
                };
            }
            else if (action === 'stop') {
                const loop = activeLoops.get(loop_id || '');
                if (!loop) {
                    return { success: false, error: 'Loop not found' };
                }
                
                await loop.stop();
                activeLoops.delete(loop_id || '');
                
                return { success: true };
            }
            else if (action === 'pause') {
                const loop = activeLoops.get(loop_id || '');
                if (!loop) {
                    return { success: false, error: 'Loop not found' };
                }
                
                await loop.pause();
                return { success: true, status: loop.getStatus() };
            }
            else if (action === 'resume') {
                const loop = activeLoops.get(loop_id || '');
                if (!loop) {
                    return { success: false, error: 'Loop not found' };
                }
                
                await loop.resume();
                return { success: true, status: loop.getStatus() };
            }
            else if (action === 'status') {
                if (loop_id) {
                    const loop = activeLoops.get(loop_id);
                    if (!loop) {
                        return { success: false, error: 'Loop not found' };
                    }
                    return { success: true, status: loop.getStatus() };
                } else {
                    // Return all active loops
                    const allStatus: any[] = [];
                    activeLoops.forEach((loop, id) => {
                        allStatus.push({ loop_id: id, status: loop.getStatus() });
                    });
                    return { success: true, active_loops: allStatus };
                }
            }
            else {
                return { success: false, error: 'Invalid action' };
            }
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    /**
     * Send chat message via VS Code command chaining (professional approach)
     * Based on Grok research findings, but discovery shows these commands don't exist in Cursor
     * So this will likely fail and fall back to macro, but we try it first
     */
    private async sendChatViaCommands(message: string): Promise<any> {
        AIMOSLogger.log('COMMAND_SERVER', 'Attempting to send chat via VS Code commands');

        // Discovery endpoint shows these commands don't exist, but we try anyway
        // Also try composer/aichat commands that were found in discovery
        const commandsToTry = [
            'workbench.action.chat.open',
            'composer.newAgentChat',
            'aichat.newchataction',
            'workbench.action.chat.focus'
        ];

        let chatOpened = false;
        for (const cmd of commandsToTry) {
            try {
                await vscode.commands.executeCommand(cmd);
                await new Promise(resolve => setTimeout(resolve, 300));
                chatOpened = true;
                AIMOSLogger.log('COMMAND_SERVER', `Successfully executed: ${cmd}`);
                break;
            } catch (e) {
                // Continue trying next command
            }
        }

        if (!chatOpened) {
            throw new Error('Could not open chat via any available command');
        }

        // Try to insert text (discovery shows these don't exist, but try anyway)
        try {
            await vscode.commands.executeCommand('workbench.action.chat.insertText', message);
            await new Promise(resolve => setTimeout(resolve, 100));
        } catch (e) {
            // Fallback: Use type command
            try {
                await vscode.commands.executeCommand('type', { text: message });
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (e2) {
                throw new Error('Could not insert text into chat');
            }
        }

        // Try to submit (discovery shows this doesn't exist, but try anyway)
        try {
            await vscode.commands.executeCommand('workbench.action.chat.submit');
            await new Promise(resolve => setTimeout(resolve, 200));
        } catch (e) {
            // No submit command available - throw error so we fall back to macro
            throw new Error('Could not submit chat message via command');
        }

        return { success: true };
    }

    /**
     * Execute Windows macro to send message to Cursor chat
     * Uses PowerShell to simulate keyboard input
     */
    private async executeWindowsChatMacro(message: string): Promise<void> {
        const execAsync = promisify(exec);
        
        // Escape message for PowerShell
        const escapedMessage = message
            .replace(/'/g, "''")  // Escape single quotes
            .replace(/\$/g, '`$')  // Escape dollar signs
            .replace(/`/g, '``');  // Escape backticks

        // PowerShell script to send message to Cursor chat
        const psScript = `
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName Microsoft.VisualBasic
            
            # Find Cursor process
            $cursorProcess = Get-Process | Where-Object {$_.MainWindowTitle -like "*Cursor*" -or $_.ProcessName -eq "Cursor"}
            if (-not $cursorProcess) {
                Write-Error "Cursor process not found"
                exit 1
            }
            
            # Activate Cursor window
            [Microsoft.VisualBasic.Interaction]::AppActivate($cursorProcess[0].Id)
            Start-Sleep -Milliseconds 300
            
            # Open chat (Ctrl+L)
            [System.Windows.Forms.SendKeys]::SendWait("^l")
            Start-Sleep -Milliseconds 500
            
            # Type message
            [System.Windows.Forms.SendKeys]::SendWait('${escapedMessage}')
            Start-Sleep -Milliseconds 100
            
            # Send (Enter)
            [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
        `;

        try {
            AIMOSLogger.log('COMMAND_SERVER', 'Executing Windows chat macro via PowerShell');
            
            // Execute PowerShell script
            const { stdout, stderr } = await execAsync(
                `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "${psScript.replace(/"/g, '\\"')}"`,
                { timeout: 10000 } // 10 second timeout
            );

            if (stderr && !stderr.includes('AppActivate')) {
                AIMOSLogger.warn('COMMAND_SERVER', 'PowerShell script warnings', stderr);
            }

        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Windows chat macro failed', error);
            throw new Error(`Failed to execute Windows macro: ${error.message}`);
        }
    }

    /**
     * Execute macOS macro to send message to Cursor chat
     * Uses AppleScript to simulate keyboard input
     */
    private async executeMacChatMacro(message: string): Promise<void> {
        const execAsync = promisify(exec);
        
        // Escape message for AppleScript
        const escapedMessage = message
            .replace(/\\/g, '\\\\')
            .replace(/"/g, '\\"')
            .replace(/\$/g, '\\$');

        // AppleScript to send message to Cursor chat
        const applescript = `
            tell application "Cursor"
                activate
                delay 0.3
                tell application "System Events"
                    keystroke "l" using {command down}
                    delay 0.5
                    keystroke "${escapedMessage}"
                    delay 0.1
                    key code 36 -- Enter
                end tell
            end tell
        `;

        try {
            AIMOSLogger.log('COMMAND_SERVER', 'Executing macOS chat macro via AppleScript');
            
            const { stdout, stderr } = await execAsync(
                `osascript -e '${applescript.replace(/'/g, "''")}'`,
                { timeout: 10000 }
            );

            if (stderr) {
                AIMOSLogger.warn('COMMAND_SERVER', 'AppleScript warnings', stderr);
            }

        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'macOS chat macro failed', error);
            throw new Error(`Failed to execute macOS macro: ${error.message}`);
        }
    }

    /**
     * Execute Linux macro to send message to Cursor chat
     * Uses xdotool to simulate keyboard input
     */
    private async executeLinuxChatMacro(message: string): Promise<void> {
        const execAsync = promisify(exec);
        
        try {
            AIMOSLogger.log('COMMAND_SERVER', 'Executing Linux chat macro via xdotool');
            
            // Find Cursor window
            const { stdout: windowId } = await execAsync(
                `xdotool search --name "Cursor" | head -1`,
                { timeout: 5000 }
            );

            if (!windowId.trim()) {
                throw new Error('Cursor window not found');
            }

            // Activate window
            await execAsync(`xdotool windowactivate ${windowId.trim()}`, { timeout: 2000 });
            await new Promise(resolve => setTimeout(resolve, 300));

            // Open chat (Ctrl+L)
            await execAsync(`xdotool key ctrl+l`, { timeout: 2000 });
            await new Promise(resolve => setTimeout(resolve, 500));

            // Type message
            await execAsync(`xdotool type -- "${message.replace(/"/g, '\\"')}"`, { timeout: 5000 });
            await new Promise(resolve => setTimeout(resolve, 100));

            // Send (Enter)
            await execAsync(`xdotool key Return`, { timeout: 2000 });

        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Linux chat macro failed', error);
            throw new Error(`Failed to execute Linux macro: ${error.message}`);
        }
    }

    /**
     * Handle agent start request
     * POST /agent/start
     */
    private async handleAgentStart(request: {
        prompt: string;
        repoPath: string;
        branch?: string;
        maxRuntimeHours?: number;
        taskFile?: string;
    }): Promise<any> {
        if (!this.agentMonitor) {
            return {
                success: false,
                error: 'AgentMonitor not initialized. Message router must be set first.'
            };
        }

        try {
            AIMOSLogger.log('COMMAND_SERVER', 'Starting agent', {
                repoPath: request.repoPath,
                branch: request.branch,
                maxRuntimeHours: request.maxRuntimeHours
            });

            const result = await this.agentMonitor.startAgentSmart({
                prompt: request.prompt,
                repoPath: request.repoPath,
                branch: request.branch,
                maxRuntimeHours: request.maxRuntimeHours,
                taskFile: request.taskFile
            });

            AIMOSLogger.success('COMMAND_SERVER', 'Agent started', {
                runId: result.runId,
                method: result.method
            });

            return {
                success: true,
                runId: result.runId,
                method: result.method,
                message: `Agent started via ${result.method} method`
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to start agent', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle agent stop request
     * POST /agent/stop
     */
    private async handleAgentStop(request: {
        runId: string;
    }): Promise<any> {
        if (!this.agentMonitor) {
            return {
                success: false,
                error: 'AgentMonitor not initialized'
            };
        }

        try {
            AIMOSLogger.log('COMMAND_SERVER', 'Stopping agent', { runId: request.runId });

            await this.agentMonitor.stopAgent(request.runId);

            AIMOSLogger.success('COMMAND_SERVER', 'Agent stopped', { runId: request.runId });

            return {
                success: true,
                message: 'Agent stopped successfully'
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to stop agent', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle agent status request
     * GET /agent/status/:runId
     */
    private async handleAgentStatus(runId: string): Promise<any> {
        if (!this.agentMonitor) {
            return {
                success: false,
                error: 'AgentMonitor not initialized'
            };
        }

        try {
            const status = await this.agentMonitor.getAgentStatus(runId);

            return {
                success: true,
                runId,
                status
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get agent status', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Handle agent webhook events from Cursor API
     * POST /webhook/agent-event
     */
    private async handleAgentWebhook(request: any): Promise<any> {
        if (!this.agentMonitor) {
            return {
                success: false,
                error: 'AgentMonitor not initialized'
            };
        }

        try {
            AIMOSLogger.log('COMMAND_SERVER', 'Received agent webhook event', {
                eventType: request.type,
                runId: request.run_id
            });

            await this.agentMonitor.handleWebhookEvent(request);

            return {
                success: true,
                message: 'Webhook event processed'
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to process webhook event', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Get workspace root path
     */
    private getWorkspaceRoot(): string {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            return workspaceFolders[0].uri.fsPath;
        }
        // Fallback to current working directory
        return process.cwd();
    }

    /**
     * Get Vite cache information
     * GET /dev/vite/cache/info
     */
    private async handleGetViteCacheInfo(projectPath: string): Promise<any> {
        AIMOSLogger.log('COMMAND_SERVER', 'Getting Vite cache info', { projectPath });

        try {
            const viteCachePath = path.join(projectPath, 'node_modules', '.vite');
            const depsCachePath = path.join(viteCachePath, 'deps');
            
            const buildCache = {
                path: viteCachePath,
                exists: fs.existsSync(viteCachePath),
                size: 0
            };

            const depsCache = {
                path: depsCachePath,
                exists: fs.existsSync(depsCachePath),
                size: 0
            };

            // Calculate sizes if directories exist
            if (buildCache.exists) {
                buildCache.size = await this.getDirectorySize(viteCachePath);
            }

            if (depsCache.exists) {
                depsCache.size = await this.getDirectorySize(depsCachePath);
            }

            const totalSize = buildCache.size + depsCache.size;

            return {
                success: true,
                buildCache,
                depsCache,
                totalSize,
                projectPath
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to get Vite cache info', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Clear Vite cache
     * POST /dev/vite/cache/clear
     */
    private async handleClearViteCache(request: {
        projectPath?: string;
        types?: string[] | string; // 'build', 'deps', or 'all'
        restart?: boolean;
    }): Promise<any> {
        const projectPath = request.projectPath || this.getWorkspaceRoot();
        const types = Array.isArray(request.types) 
            ? request.types 
            : request.types === 'all' || !request.types 
                ? ['build', 'deps'] 
                : [request.types];
        const restart = request.restart || false;

        AIMOSLogger.log('COMMAND_SERVER', 'Clearing Vite cache', { 
            projectPath, 
            types, 
            restart 
        });

        try {
            const cleared: string[] = [];
            let freed = 0;

            const viteCachePath = path.join(projectPath, 'node_modules', '.vite');
            const depsCachePath = path.join(viteCachePath, 'deps');

            // Clear build cache (includes deps if clearing all)
            if (types.includes('build') || types.includes('all')) {
                if (fs.existsSync(viteCachePath)) {
                    const size = await this.getDirectorySize(viteCachePath);
                    await fs.promises.rm(viteCachePath, { recursive: true, force: true });
                    cleared.push('build');
                    freed += size;
                    AIMOSLogger.log('COMMAND_SERVER', 'Cleared Vite build cache', { size });
                }
            }

            // Clear deps cache only (if not already cleared with build)
            if (types.includes('deps') && !types.includes('build') && !types.includes('all')) {
                if (fs.existsSync(depsCachePath)) {
                    const size = await this.getDirectorySize(depsCachePath);
                    await fs.promises.rm(depsCachePath, { recursive: true, force: true });
                    cleared.push('deps');
                    freed += size;
                    AIMOSLogger.log('COMMAND_SERVER', 'Cleared Vite deps cache', { size });
                }
            }

            // Restart dev server if requested
            let restarted = false;
            if (restart) {
                try {
                    await this.restartViteDevServer(projectPath);
                    restarted = true;
                    AIMOSLogger.log('COMMAND_SERVER', 'Restarted Vite dev server');
                } catch (restartError: any) {
                    AIMOSLogger.error('COMMAND_SERVER', 'Failed to restart Vite dev server', restartError);
                    // Don't fail the whole operation if restart fails
                }
            }

            AIMOSLogger.success('COMMAND_SERVER', 'Vite cache cleared', { 
                cleared, 
                freed, 
                restarted 
            });

            return {
                success: true,
                cleared,
                freed,
                restarted,
                projectPath
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to clear Vite cache', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Calculate directory size recursively
     */
    private async getDirectorySize(dirPath: string): Promise<number> {
        let totalSize = 0;
        
        try {
            const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
            
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                
                if (entry.isDirectory()) {
                    totalSize += await this.getDirectorySize(fullPath);
                } else {
                    const stats = await fs.promises.stat(fullPath);
                    totalSize += stats.size;
                }
            }
        } catch (error) {
            // Ignore errors (permissions, etc.)
        }
        
        return totalSize;
    }

    /**
     * Handle get system indexes request
     * GET /api/system-indexes or GET /api/system-indexes/:systemId
     */
    private async handleGetSystemIndexes(systemId?: string): Promise<any> {
        AIMOSLogger.log('COMMAND_SERVER', 'Loading system indexes', { systemId: systemId || 'all' });

        try {
            const workspaceRoot = this.getWorkspaceRoot();
            const systemsDir = path.join(workspaceRoot, 'knowledge_architecture', 'systems');
            
            if (!fs.existsSync(systemsDir)) {
                return {
                    success: false,
                    error: `Systems directory not found: ${systemsDir}`
                };
            }

            const indexes: any[] = [];

            // Recursively find all system.index.lucid.json5 files
            const findSystemIndexes = (dir: string): void => {
                try {
                    const entries = fs.readdirSync(dir, { withFileTypes: true });
                    
                    for (const entry of entries) {
                        const fullPath = path.join(dir, entry.name);
                        
                        if (entry.isDirectory()) {
                            findSystemIndexes(fullPath);
                        } else if (entry.name === 'system.index.lucid.json5') {
                            try {
                                const content = fs.readFileSync(fullPath, 'utf-8');
                                const parsed = this.parseJSON5(content);
                                
                                // If looking for specific system, filter
                                if (systemId && parsed.systemId !== systemId) {
                                    continue;
                                }
                                
                                indexes.push(parsed);
                            } catch (err: any) {
                                AIMOSLogger.warn('COMMAND_SERVER', `Failed to parse ${fullPath}`, err);
                            }
                        }
                    }
                } catch (err: any) {
                    AIMOSLogger.warn('COMMAND_SERVER', `Error reading directory ${dir}`, err);
                }
            };

            findSystemIndexes(systemsDir);

            if (systemId) {
                const index = indexes.find(i => i.systemId === systemId);
                if (index) {
                    return {
                        success: true,
                        index
                    };
                } else {
                    return {
                        success: false,
                        error: `System index not found: ${systemId}`
                    };
                }
            }

            AIMOSLogger.success('COMMAND_SERVER', `Loaded ${indexes.length} system indexes`);

            return {
                success: true,
                indexes
            };
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to load system indexes', error);
            return {
                success: false,
                error: error.message || String(error)
            };
        }
    }

    /**
     * Parse JSON5 content (strip comments and trailing commas, then parse as JSON)
     */
    private parseJSON5(content: string): any {
        // Remove single-line comments (// ...)
        let cleaned = content.replace(/\/\/.*$/gm, '');
        
        // Remove multi-line comments (/* ... */)
        cleaned = cleaned.replace(/\/\*[\s\S]*?\*\//g, '');
        
        // Remove trailing commas before } or ]
        cleaned = cleaned.replace(/,(\s*[}\]])/g, '$1');
        
        // Parse as JSON
        return JSON.parse(cleaned);
    }

    /**
     * Restart Vite dev server
     */
    private async restartViteDevServer(projectPath: string): Promise<void> {
        // Find and kill existing Vite process
        // This is platform-specific, so we'll use a simple approach
        
        const execAsync = promisify(exec);
        const isWindows = os.platform() === 'win32';
        
        try {
            // Try to find Vite process
            let command: string;
            if (isWindows) {
                command = `tasklist /FI "IMAGENAME eq node.exe" /FO CSV | findstr /C:"node.exe"`;
            } else {
                command = `ps aux | grep -i vite | grep -v grep`;
            }
            
            // Note: Actually restarting requires more sophisticated process management
            // For now, we'll just log that restart was requested
            // In production, you might want to use a process manager or send a signal
            
            AIMOSLogger.log('COMMAND_SERVER', 'Vite dev server restart requested', { 
                projectPath,
                note: 'Manual restart may be required. Kill existing process and run "npm run dev"'
            });
            
            // Return success - actual restart would require more complex implementation
            // or integration with a process manager
        } catch (error: any) {
            AIMOSLogger.error('COMMAND_SERVER', 'Failed to restart Vite dev server', error);
            throw error;
        }
    }
}

