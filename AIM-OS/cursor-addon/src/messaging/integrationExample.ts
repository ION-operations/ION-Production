/**
 * Integration Example: Using Bulletproof Messaging in Webview Provider
 * 
 * This file shows how to integrate the bulletproof messaging protocol
 * into the existing webview provider while maintaining backward compatibility
 */

import * as vscode from 'vscode';
import { MessageRouter } from './router';
import { HeartbeatMonitor } from './heartbeatMonitor';
import { PersistentOutbox } from './persistentOutbox';
import { Envelope, createEnvelope } from './envelope';
import { MCPClient } from '../mcp/mcpClient';

/**
 * Example integration showing how to use bulletproof messaging
 */
export class BulletproofMessagingIntegration {
    private router: MessageRouter;
    private heartbeat: HeartbeatMonitor;
    private outbox: PersistentOutbox;
    private mcpClient: MCPClient;
    private webview: vscode.Webview | null = null;
    private sequenceNumber: number = 0;

    constructor(context: vscode.ExtensionContext) {
        // Initialize components
        this.router = new MessageRouter(context, {
            maxRetries: 3,
            retryDelay: 500,
            ackTimeout: 500,
        });
        
        this.heartbeat = new HeartbeatMonitor(10000);
        this.outbox = new PersistentOutbox(context);
        this.mcpClient = new MCPClient();
        
        // Register handlers
        this.registerHandlers();
        
        // Replay undelivered messages on startup
        this.replayUndelivered();
        
        // Periodic cleanup
        setInterval(() => {
            this.outbox.cleanup();
        }, 60 * 60 * 1000); // Every hour
    }

    /**
     * Set webview for communication
     */
    setWebview(webview: vscode.Webview): void {
        this.webview = webview;
        this.router.setWebview(webview);
        this.heartbeat.setWebview(webview);
        this.heartbeat.start();
        
        // Listen for messages
        webview.onDidReceiveMessage((message: any) => {
            // Handle envelope protocol messages
            if (message.v === 1 && message.kind) {
                this.handleEnvelope(message);
            }
        });
    }

    /**
     * Register message handlers
     */
    private registerHandlers(): void {
        // MCP tool calls
        this.router.registerHandler('mcp.callTool', async (env) => {
            return await this.handleMCPTool(env);
        });
        
        // Chat messages
        this.router.registerHandler('chat.message', async (env) => {
            return await this.handleChatMessage(env);
        });
        
        // State updates
        this.router.registerHandler('state.update', async (env) => {
            return await this.handleStateUpdate(env);
        });
    }

    /**
     * Handle incoming envelope
     */
    private async handleEnvelope(message: any): Promise<void> {
        // Validate envelope
        if (!message.v || !message.id || !message.kind) {
            console.error('Invalid envelope:', message);
            return;
        }
        
        // Set sequence number if missing
        if (message.dir === 'ui->ext' && message.seq === undefined) {
            message.seq = ++this.sequenceNumber;
        }
        
        // Route through router
        await this.router.route(message);
    }

    /**
     * Handle MCP tool call
     */
    private async handleMCPTool(env: Envelope): Promise<Envelope | null> {
        const payload = env.payload as { toolName: string; params: any };
        
        try {
            await this.mcpClient.initialize();
            const result = await this.mcpClient.callTool(
                payload.toolName.replace(/^mcp_lucid-mcp_/, ''),
                payload.params || {}
            );
            
            return createEnvelope('response', env.topic, 'ext->ui', {
                success: true,
                result,
            }, {
                replyTo: env.id,
                priority: 'high',
            });
        } catch (error: any) {
            return createEnvelope('response', env.topic, 'ext->ui', {
                success: false,
                error: error.message,
            }, {
                replyTo: env.id,
                priority: 'high',
            });
        }
    }

    /**
     * Handle chat message
     */
    private async handleChatMessage(env: Envelope): Promise<Envelope | null> {
        // Process chat message
        // ...
        return createEnvelope('ack', env.topic, 'ext->ui', null, {
            replyTo: env.id,
        });
    }

    /**
     * Handle state update
     */
    private async handleStateUpdate(env: Envelope): Promise<Envelope | null> {
        // Process state update
        // ...
        return createEnvelope('ack', env.topic, 'ext->ui', null, {
            replyTo: env.id,
        });
    }

    /**
     * Send message to UI
     */
    async sendMessage(envelope: Envelope): Promise<void> {
        if (!this.webview) {
            // Store in outbox for later delivery
            this.outbox.push(envelope);
            return;
        }
        
        try {
            envelope.seq = ++this.sequenceNumber;
            this.webview.postMessage(envelope);
            
            // Mark as delivered in outbox
            this.outbox.markDelivered(envelope.id);
        } catch (error) {
            // Failed to send - store in outbox
            this.outbox.push(envelope);
        }
    }

    /**
     * Replay undelivered messages
     */
    private async replayUndelivered(): Promise<void> {
        const undelivered = this.outbox.getUndelivered();
        
        for (const entry of undelivered) {
            if (this.webview) {
                try {
                    this.webview.postMessage(entry.envelope);
                    this.outbox.markDelivered(entry.id);
                } catch (error) {
                    this.outbox.markAttempted(entry.id);
                }
            }
        }
    }

    /**
     * Get statistics
     */
    getStats() {
        return {
            router: this.router.getStats(),
            heartbeat: this.heartbeat.getStats(),
            outbox: this.outbox.getStats(),
        };
    }
}

