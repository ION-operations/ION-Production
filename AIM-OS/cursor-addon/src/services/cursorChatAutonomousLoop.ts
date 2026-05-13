/**
 * Cursor Chat Autonomous Loop Service
 * Manages autonomous loop for hands-free Cursor chat operation
 * 
 * Implemented from Chat Automation T3 Detailed documentation
 */

import { ResponseDetectionEngine, DetectionResult } from './responseDetectionEngine';
import * as vscode from 'vscode';

export interface LoopConfig {
    initialMessage: string;           // First message to send
    proceedMessage: string;           // Message to send after each response (default: "proceed")
    confidenceThreshold: number;      // Minimum confidence to send (default: 0.70)
    pollIntervalSeconds: number;      // How often to check (default: 3)
    maxIterations?: number;           // Safety limit (optional)
    timeoutMinutes?: number;          // Max session duration (optional)
}

export interface LoopStatus {
    active: boolean;
    paused: boolean;
    iterationsCompleted: number;
    lastDetection: DetectionResult | null;
    startedAt: number;
    pausedAt?: number;
    stoppedAt?: number;
    error?: string;
}

export class CursorChatAutonomousLoop {
    private config: LoopConfig;
    private status: LoopStatus;
    private detectionEngine: ResponseDetectionEngine;
    private intervalId: NodeJS.Timeout | null = null;
    private mcpServerUrl: string;
    private commandServerUrl: string;
    
    constructor(config: LoopConfig, mcpServerUrl: string = 'http://localhost:5001', commandServerUrl: string = 'http://localhost:5001') {
        this.config = {
            proceedMessage: 'proceed',
            confidenceThreshold: 0.70,
            pollIntervalSeconds: 3,
            ...config  // Override defaults
        };
        
        this.status = {
            active: false,
            paused: false,
            iterationsCompleted: 0,
            lastDetection: null,
            startedAt: 0
        };
        
        this.mcpServerUrl = mcpServerUrl;
        this.commandServerUrl = commandServerUrl;
        this.detectionEngine = new ResponseDetectionEngine(mcpServerUrl);
    }
    
    /**
     * Start autonomous loop
     * 
     * Flow:
     * 1. Start autonomous operation (MCP tool)
     * 2. Send initial message to Cursor chat
     * 3. Begin monitoring loop (poll every N seconds)
     */
    async start(): Promise<void> {
        if (this.status.active) {
            throw new Error('Loop already active');
        }
        
        try {
            // Start autonomous operation via MCP
            await this.callMCPTool('start_autonomous_operation', {
                operation_type: 'cursor_chat_autonomous',
                initial_task: this.config.initialMessage
            });
            
            // Send initial message to Cursor chat
            await this.sendChatMessage(this.config.initialMessage);
            
            // Update status
            this.status.active = true;
            this.status.paused = false;
            this.status.startedAt = Date.now();
            
            // Start monitoring loop
            this.intervalId = setInterval(
                () => this.monitorAndSendProceed(),
                this.config.pollIntervalSeconds * 1000
            );
            
            console.log('Autonomous loop started:', this.config);
        } catch (error) {
            this.status.error = error instanceof Error ? error.message : String(error);
            throw error;
        }
    }
    
    /**
     * Stop autonomous loop
     * 
     * Flow:
     * 1. Stop monitoring interval
     * 2. Stop autonomous operation (MCP tool)
     * 3. Store final audit trail in CMC
     */
    async stop(): Promise<void> {
        // Stop monitoring interval
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        // Stop autonomous operation via MCP
        try {
            await this.callMCPTool('stop_autonomous_operation', {});
        } catch (error) {
            console.error('Error stopping autonomous operation:', error);
        }
        
        // Update status
        this.status.active = false;
        this.status.stoppedAt = Date.now();
        
        // Store final audit trail in CMC
        try {
            await this.callMCPTool('store_memory', {
                mpd_id: `chat-automation-session-${this.status.startedAt}`,
                data: {
                    config: this.config,
                    status: this.status,
                    duration_minutes: (this.status.stoppedAt - this.status.startedAt) / 60000,
                    iterations: this.status.iterationsCompleted
                },
                category: 'chat_automation_session'
            });
        } catch (error) {
            console.error('Error storing audit trail:', error);
        }
        
        console.log('Autonomous loop stopped:', this.status);
    }
    
    /**
     * Pause autonomous loop
     * Stops monitoring but preserves state for resumption
     */
    async pause(): Promise<void> {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        try {
            await this.callMCPTool('pause_autonomous_operation', {});
        } catch (error) {
            console.error('Error pausing autonomous operation:', error);
        }
        
        this.status.paused = true;
        this.status.pausedAt = Date.now();
        
        console.log('Autonomous loop paused');
    }
    
    /**
     * Resume autonomous loop after pause
     */
    async resume(): Promise<void> {
        if (!this.status.paused) {
            throw new Error('Loop not paused');
        }
        
        try {
            await this.callMCPTool('resume_autonomous_operation', {});
        } catch (error) {
            console.error('Error resuming autonomous operation:', error);
        }
        
        this.status.paused = false;
        this.status.pausedAt = undefined;
        
        // Restart monitoring loop
        this.intervalId = setInterval(
            () => this.monitorAndSendProceed(),
            this.config.pollIntervalSeconds * 1000
        );
        
        console.log('Autonomous loop resumed');
    }
    
    /**
     * Monitor and send "proceed" if response complete
     * 
     * Core loop logic:
     * 1. Check should_continue_autonomous (safety validation)
     * 2. Detect if response complete (multi-signal)
     * 3. If complete with sufficient confidence → Send "proceed"
     * 4. Store audit trail
     * 5. Check safety limits (max iterations, timeout)
     */
    private async monitorAndSendProceed(): Promise<void> {
        try {
            // === SAFETY CHECK: Should Continue? ===
            const shouldContinueResult = await this.callMCPTool(
                'should_continue_autonomous',
                {}
            );
            
            if (!shouldContinueResult.should_continue) {
                // Stop condition met
                console.log('Stop condition met:', shouldContinueResult.stop_reason);
                await this.stop();
                return;
            }
            
            // === SAFETY CHECK: Max Iterations ===
            if (this.config.maxIterations && this.status.iterationsCompleted >= this.config.maxIterations) {
                console.log('Max iterations reached:', this.config.maxIterations);
                await this.stop();
                return;
            }
            
            // === SAFETY CHECK: Timeout ===
            if (this.config.timeoutMinutes) {
                const elapsed = (Date.now() - this.status.startedAt) / 60000;
                if (elapsed >= this.config.timeoutMinutes) {
                    console.log('Timeout reached:', this.config.timeoutMinutes, 'minutes');
                    await this.stop();
                    return;
                }
            }
            
            // === DETECTION: Response Complete? ===
            const detection = await this.detectionEngine.detectResponseComplete();
            this.status.lastDetection = detection;
            
            // === DECISION: Send "Proceed"? ===
            if (detection.isComplete && detection.confidence >= this.config.confidenceThreshold) {
                // Response complete with sufficient confidence → Send "proceed"
                await this.sendChatMessage(this.config.proceedMessage);
                
                this.status.iterationsCompleted++;
                
                // Store audit trail in CMC
                try {
                    await this.callMCPTool('store_memory', {
                        mpd_id: `chat-automation-proceed-${Date.now()}`,
                        data: {
                            iteration: this.status.iterationsCompleted,
                            detection: detection,
                            message: this.config.proceedMessage,
                            timestamp: Date.now()
                        },
                        category: 'chat_automation_proceed'
                    });
                } catch (error) {
                    console.error('Error storing proceed event:', error);
                }
                
                console.log(`Proceed sent (iteration ${this.status.iterationsCompleted}):`, detection);
            } else {
                // Not complete or confidence too low → Wait
                console.log('Waiting:', detection.recommendation);
            }
        } catch (error) {
            console.error('Error in monitor loop:', error);
            // Don't stop on error - continue monitoring (resilient)
        }
    }
    
    /**
     * Send message to Cursor chat
     * Uses workbench.action.chat.newChat or similar command
     */
    private async sendChatMessage(message: string): Promise<void> {
        try {
            // Send via Command Server HTTP endpoint (if available)
            const response = await fetch(`${this.commandServerUrl}/cursor/chat/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to send chat message: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error sending chat message:', error);
            // Fallback: Try VS Code command
            // (This may not work - Cursor-specific)
            // await vscode.commands.executeCommand('workbench.action.chat.send', message);
        }
    }
    
    /**
     * Call MCP tool via HTTP endpoint
     */
    private async callMCPTool(toolName: string, args: any): Promise<any> {
        const response = await fetch(`${this.mcpServerUrl}/mcp/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool: toolName,
                arguments: args
            })
        });
        
        if (!response.ok) {
            throw new Error(`MCP tool ${toolName} failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data.result || data;
    }
    
    /**
     * Get current loop status
     */
    getStatus(): LoopStatus {
        return { ...this.status };  // Return copy
    }
}

