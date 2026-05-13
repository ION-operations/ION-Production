/**
 * Multi-Signal Detection Engine
 * Detects Cursor AI response completion using multiple signals with confidence routing
 * 
 * Implemented from Chat Automation T3 Detailed documentation
 */

import * as vscode from 'vscode';

export interface DetectionSignal {
    name: string;
    value: boolean | number | string;
    confidence: number;  // 0.0 to 1.0
    timestamp: number;
    error?: string;
}

export interface DetectionResult {
    isComplete: boolean;
    confidence: number;  // Combined confidence (0.0 to 1.0)
    signals: DetectionSignal[];
    recommendation: string;
    timestamp: number;
}

export class ResponseDetectionEngine {
    private lastTaskCount: number = 0;
    private mcpServerUrl: string;
    
    constructor(mcpServerUrl: string = 'http://localhost:5001') {
        this.mcpServerUrl = mcpServerUrl;
    }
    
    /**
     * Detect if Cursor AI response is complete
     * 
     * Uses 3 detection signals with confidence routing:
     * 1. Chat input ready state (0.70 confidence)
     * 2. Should continue autonomous (0.85 confidence)
     * 3. Task completion status (0.80 confidence)
     * 
     * Combined confidence ≥0.70 → Response complete
     * 
     * Returns: DetectionResult with decision and all signal data
     */
    async detectResponseComplete(): Promise<DetectionResult> {
        const signals: DetectionSignal[] = [];
        
        // === SIGNAL 1: Chat Input Ready State ===
        try {
            const chatReady = await this.checkChatInputReady();
            signals.push({
                name: 'chat_input_ready',
                value: chatReady,
                confidence: 0.70,  // Heuristic (may need refinement)
                timestamp: Date.now()
            });
        } catch (error) {
            signals.push({
                name: 'chat_input_ready',
                value: false,
                confidence: 0.0,
                timestamp: Date.now(),
                error: error instanceof Error ? error.message : String(error)
            });
        }
        
        // === SIGNAL 2: Should Continue Autonomous ===
        try {
            const shouldContinueResult = await this.callMCPTool(
                'should_continue_autonomous',
                {}
            );
            
            signals.push({
                name: 'should_continue_autonomous',
                value: shouldContinueResult.should_continue,
                confidence: 0.85,  // Proven MCP tool
                timestamp: Date.now()
            });
        } catch (error) {
            signals.push({
                name: 'should_continue_autonomous',
                value: false,
                confidence: 0.0,
                timestamp: Date.now(),
                error: error instanceof Error ? error.message : String(error)
            });
        }
        
        // === SIGNAL 3: Task Completion Status ===
        try {
            const status = await this.callMCPTool(
                'get_autonomous_status',
                {}
            );
            
            const taskCompleted = status.tasks_completed > this.lastTaskCount;
            
            signals.push({
                name: 'task_completed',
                value: taskCompleted,
                confidence: 0.80,  // Proven tool, heuristic comparison
                timestamp: Date.now()
            });
            
            // Update task count for next iteration
            if (taskCompleted) {
                this.lastTaskCount = status.tasks_completed;
            }
        } catch (error) {
            signals.push({
                name: 'task_completed',
                value: false,
                confidence: 0.0,
                timestamp: Date.now(),
                error: error instanceof Error ? error.message : String(error)
            });
        }
        
        // === CONFIDENCE ROUTING (VIF Pattern) ===
        // Calculate weighted average (only from signals without errors)
        const validSignals = signals.filter(s => !s.error && s.confidence > 0);
        const combinedConfidence = validSignals.length > 0
            ? validSignals.reduce((sum, s) => sum + s.confidence, 0) / validSignals.length
            : 0.0;
        
        // Decision: ≥0.70 = complete
        const isComplete = combinedConfidence >= 0.70;
        
        return {
            isComplete,
            confidence: combinedConfidence,
            signals,
            recommendation: isComplete 
                ? 'Send "proceed" now - response complete with high confidence'
                : `Wait - confidence ${combinedConfidence.toFixed(2)} below threshold 0.70`,
            timestamp: Date.now()
        };
    }
    
    /**
     * Check if chat input is ready for new message
     * 
     * Heuristic approach: Try to focus chat input, if succeeds, assume ready
     * 
     * Confidence: 0.70 (heuristic, may need refinement based on testing)
     */
    private async checkChatInputReady(): Promise<boolean> {
        try {
            // Try to focus chat input
            await vscode.commands.executeCommand('workbench.action.focusChatInput');
            
            // Small delay to ensure command processed
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // If command succeeded, assume chat ready
            return true;
        } catch (error) {
            // If command failed, chat not ready
            return false;
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
}

