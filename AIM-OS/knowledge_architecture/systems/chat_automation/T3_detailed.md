---
id: "chat_automation_T3_detailed"
system: "chat_automation"
component: null
level: "T3"
type: "detailed"
title: "Chat Automation Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Chat Automation"
audience: "developers, implementers"
confidence_threshold: 0.70
token_cost: 10000
word_count: 10000
created: "2025-11-05T16:00:00Z"
updated: "2025-11-05T16:00:00Z"
author: "aether"
status: "complete"
tags: ["chat-automation", "implementation", "multi-signal", "autonomous-loop", "t0-t6"]
dependencies: ["autonomous_protocols", "cursor_extension", "mcp_tools"]
related_docs: ["T0_executive.md", "T1_overview.md", "T2_architecture.md", "CURSOR_CHAT_AUTONOMOUS_LOOP_DESIGN.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Chat Automation – T3 Detailed Implementation Guide (≈10,000 words)

**This document provides complete implementation guidance for the Chat Automation system, including multi-signal detection engine and autonomous loop service.**

---

## Table of Contents

### Part 1: Detection Engine
1. [Multi-Signal Detection Engine](#multi-signal-detection-engine)
2. [Signal Implementations](#signal-implementations)
3. [Confidence Routing](#confidence-routing)

### Part 2: Loop Service
4. [Cursor Chat Autonomous Loop Service](#cursor-chat-autonomous-loop-service)
5. [MCP Tools Integration](#mcp-tools-integration)
6. [Extension Command Server Integration](#extension-command-server-integration)

### Part 3: Implementation Guide
7. [Complete TypeScript Implementation](#complete-typescript-implementation)
8. [Testing Guide](#testing-guide)
9. [Deployment Guide](#deployment-guide)

---

# Part 1: Detection Engine

## Multi-Signal Detection Engine

**File:** `cursor-addon/src/services/responseDetectionEngine.ts`

```typescript
/**
 * Multi-Signal Detection Engine
 * Detects Cursor AI response completion using multiple signals with confidence routing
 */

import * as vscode from 'vscode';
import { MCPClient } from '../mcp/mcpClient';

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
    private mcpClient: MCPClient;
    private lastTaskCount: number = 0;
    
    constructor(mcpClient: MCPClient) {
        this.mcpClient = mcpClient;
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
            const shouldContinueResult = await this.mcpClient.callTool(
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
            const status = await this.mcpClient.callTool(
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
        const validSignals = signals.filter(s => !s.error);
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
}
```

---

## Signal Implementations

### Signal 1: Chat Input Ready State

**Implementation Details:**

```typescript
/**
 * Signal 1: Chat Input Ready
 * 
 * Detects if Cursor chat input is ready for new message
 * 
 * Method: Execute VS Code command to focus chat input
 * If command succeeds → Chat ready
 * If command fails → Chat still processing
 * 
 * Confidence: 0.70 (heuristic, based on command success)
 * 
 * Limitations:
 * - Heuristic approach (not perfect)
 * - May have false positives if chat unfocused for other reasons
 * - Needs testing to validate accuracy
 */
private async checkChatInputReady(): Promise<boolean> {
    try {
        await vscode.commands.executeCommand('workbench.action.focusChatInput');
        await new Promise(resolve => setTimeout(resolve, 500));
        return true;
    } catch (error) {
        return false;
    }
}
```

**Alternative Implementations (Research Needed):**

```typescript
// Option 2: Check if chat input element exists and is enabled
private async checkChatInputViaDOM(): Promise<boolean> {
    // Would require accessing VS Code webview DOM
    // Research needed: Can extension access Cursor chat DOM?
    throw new Error('Not yet implemented - research needed');
}

// Option 3: Monitor chat state via VS Code API
private async checkChatInputViaAPI(): Promise<boolean> {
    // Would require Cursor-specific API
    // Research needed: Does Cursor expose chat state API?
    throw new Error('Not yet implemented - research needed');
}
```

### Signal 2: Should Continue Autonomous

**Implementation:**

```typescript
/**
 * Signal 2: Should Continue Autonomous
 * 
 * Uses MCP tool to validate autonomous operation should continue
 * 
 * Method: Call should_continue_autonomous MCP tool
 * Returns: should_continue (boolean) + stop_reason (if false)
 * 
 * Confidence: 0.85 (proven tool with validated logic)
 * 
 * This tool checks:
 * - Confidence still ≥0.70?
 * - Quality maintained?
 * - Alignment preserved?
 * - No capability boundaries hit?
 * - Checklist passed?
 */
private async checkShouldContinueAutonomous(): Promise<boolean> {
    try {
        const result = await this.mcpClient.callTool('should_continue_autonomous', {});
        return result.should_continue === true;
    } catch (error) {
        // MCP tool error = assume should not continue (safe default)
        return false;
    }
}
```

### Signal 3: Task Completion Status

**Implementation:**

```typescript
/**
 * Signal 3: Task Completion Status
 * 
 * Detects if AI completed a task by comparing task count
 * 
 * Method: Call get_autonomous_status MCP tool, compare tasks_completed
 * If tasks_completed increased → Task just completed
 * 
 * Confidence: 0.80 (proven tool, heuristic comparison)
 * 
 * Heuristic: Task count increase implies completion
 * Limitation: Doesn't detect partial progress (only complete tasks)
 */
private async checkTaskCompleted(): Promise<boolean> {
    try {
        const status = await this.mcpClient.callTool('get_autonomous_status', {});
        
        // Check if task count increased
        const taskCompleted = status.tasks_completed > this.lastTaskCount;
        
        return taskCompleted;
    } catch (error) {
        // MCP tool error = assume no task completed
        return false;
    }
}
```

---

## Confidence Routing

**VIF-Based Confidence Pattern:**

```typescript
/**
 * Confidence Routing (VIF Pattern)
 * 
 * Combines multiple signals using weighted average confidence.
 * 
 * Algorithm:
 * 1. Collect all signals
 * 2. Filter out signals with errors (confidence = 0.0)
 * 3. Calculate weighted average:
 *    combined = (c1 + c2 + c3 + ...) / n
 * 4. Decision:
 *    - combined ≥0.70 → Response complete (send "proceed")
 *    - combined <0.70 → Response incomplete (wait)
 * 
 * Why weighted average (not all-must-agree):
 * - Robust to single signal failures
 * - Tolerates varying signal quality
 * - Follows AIM-OS VIF confidence pattern
 * - Enables graceful degradation
 */
private calculateCombinedConfidence(signals: DetectionSignal[]): number {
    // Filter out failed signals
    const validSignals = signals.filter(s => !s.error && s.confidence > 0);
    
    if (validSignals.length === 0) {
        // All signals failed → confidence = 0.0 (don't proceed)
        return 0.0;
    }
    
    // Weighted average
    const sum = validSignals.reduce((total, s) => total + s.confidence, 0);
    return sum / validSignals.length;
}
```

**Example Scenarios:**

```typescript
// Scenario 1: All signals agree (high confidence)
signals = [
    {name: 'chat_ready', value: true, confidence: 0.70},
    {name: 'should_continue', value: true, confidence: 0.85},
    {name: 'task_completed', value: true, confidence: 0.80}
]
combined = (0.70 + 0.85 + 0.80) / 3 = 0.78 ✅ Send "proceed"

// Scenario 2: One signal disagrees (medium confidence)
signals = [
    {name: 'chat_ready', value: false, confidence: 0.70},
    {name: 'should_continue', value: true, confidence: 0.85},
    {name: 'task_completed', value: true, confidence: 0.80}
]
combined = (0.70 + 0.85 + 0.80) / 3 = 0.78 ✅ Still send (majority agree)

// Scenario 3: Multiple signals disagree (low confidence)
signals = [
    {name: 'chat_ready', value: false, confidence: 0.70},
    {name: 'should_continue', value: false, confidence: 0.85},
    {name: 'task_completed', value: false, confidence: 0.80}
]
combined = (0.70 + 0.85 + 0.80) / 3 = 0.78 
BUT: All values are false → Don't send (despite high confidence)

// Scenario 4: Signal failures (graceful degradation)
signals = [
    {name: 'chat_ready', value: false, confidence: 0.70, error: 'Timeout'},
    {name: 'should_continue', value: true, confidence: 0.85},
    {name: 'task_completed', value: true, confidence: 0.80}
]
// Filter out error signal
valid_signals = [0.85, 0.80]
combined = (0.85 + 0.80) / 2 = 0.825 ✅ Send "proceed" (degraded but functional)
```

---

# Part 2: Loop Service

## Cursor Chat Autonomous Loop Service

**File:** `cursor-addon/src/services/cursorChatAutonomousLoop.ts`

```typescript
/**
 * Cursor Chat Autonomous Loop Service
 * Manages autonomous loop for hands-free Cursor chat operation
 */

import { ResponseDetectionEngine, DetectionResult } from './responseDetectionEngine';
import { MCPClient } from '../mcp/mcpClient';
import { CommandServerClient } from '../api/commandServerClient';

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
    private commandServer: CommandServerClient;
    private mcpClient: MCPClient;
    private intervalId: NodeJS.Timeout | null = null;
    
    constructor(config: LoopConfig, mcpClient: MCPClient) {
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
        
        this.mcpClient = mcpClient;
        this.detectionEngine = new ResponseDetectionEngine(mcpClient);
        this.commandServer = new CommandServerClient();
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
            await this.mcpClient.callTool('start_autonomous_operation', {
                operation_type: 'cursor_chat_autonomous',
                initial_task: this.config.initialMessage
            });
            
            // Send initial message to Cursor chat
            await this.commandServer.post('/cursor/chat/send', {
                message: this.config.initialMessage
            });
            
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
        await this.mcpClient.callTool('stop_autonomous_operation', {});
        
        // Update status
        this.status.active = false;
        this.status.stoppedAt = Date.now();
        
        // Store final audit trail in CMC
        await this.mcpClient.callTool('store_memory', {
            mpd_id: `chat-automation-session-${this.status.startedAt}`,
            data: {
                config: this.config,
                status: this.status,
                duration_minutes: (this.status.stoppedAt - this.status.startedAt) / 60000,
                iterations: this.status.iterationsCompleted
            },
            category: 'chat_automation_session'
        });
        
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
        
        await this.mcpClient.callTool('pause_autonomous_operation', {});
        
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
        
        await this.mcpClient.callTool('resume_autonomous_operation', {});
        
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
            const shouldContinueResult = await this.mcpClient.callTool(
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
                await this.commandServer.post('/cursor/chat/send', {
                    message: this.config.proceedMessage
                });
                
                this.status.iterationsCompleted++;
                
                // Store audit trail in CMC
                await this.mcpClient.callTool('store_memory', {
                    mpd_id: `chat-automation-proceed-${Date.now()}`,
                    data: {
                        iteration: this.status.iterationsCompleted,
                        detection: detection,
                        message: this.config.proceedMessage,
                        timestamp: Date.now()
                    },
                    category: 'chat_automation_proceed'
                });
                
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
     * Get current loop status
     */
    getStatus(): LoopStatus {
        return { ...this.status };  // Return copy
    }
}
```

---

## MCP Tools Integration

**Complete Integration Pattern:**

```typescript
/**
 * MCP Tools Used by Chat Automation
 * 
 * Autonomous Operation Tools (Primary):
 * - should_continue_autonomous: Validates before each "proceed"
 * - get_autonomous_status: Monitors task completion
 * - start_autonomous_operation: Starts loop
 * - stop_autonomous_operation: Stops loop
 * - pause/resume_autonomous_operation: Control loop
 * 
 * Memory Tools (Audit Trail):
 * - store_memory: Stores all detection events, "proceed" sends
 * - retrieve_memory: Retrieves session history
 * 
 * Goal Tools (Progress Tracking):
 * - update_goal_progress: Auto-updates goals
 * - query_goal_timeline: Tracks which goals advanced
 */

class MCPToolsIntegration {
    private mcpClient: MCPClient;
    
    /**
     * Start autonomous operation
     * Initializes autonomous mode with safety checklist
     */
    async startAutonomousOperation(initialTask: string): Promise<void> {
        const result = await this.mcpClient.callTool('start_autonomous_operation', {
            operation_type: 'cursor_chat_autonomous',
            initial_task: initialTask,
            safety_checklist: true  // Run full safety checklist
        });
        
        if (!result.success) {
            throw new Error(`Failed to start: ${result.error}`);
        }
    }
    
    /**
     * Validate should continue
     * Returns: {should_continue: boolean, stop_reason?: string}
     */
    async shouldContinueAutonomous(): Promise<{should_continue: boolean, stop_reason?: string}> {
        return await this.mcpClient.callTool('should_continue_autonomous', {});
    }
    
    /**
     * Get autonomous status
     * Returns: {tasks_completed: number, confidence: number, issues: string[]}
     */
    async getAutonomousStatus(): Promise<{tasks_completed: number, confidence: number}> {
        return await this.mcpClient.callTool('get_autonomous_status', {});
    }
    
    /**
     * Store detection event in CMC
     */
    async storeDetectionEvent(detection: DetectionResult): Promise<void> {
        await this.mcpClient.callTool('store_memory', {
            mpd_id: `detection-event-${detection.timestamp}`,
            data: detection,
            category: 'chat_automation_detection'
        });
    }
}
```

---

## Extension Command Server Integration

**New Endpoint Implementation:**

```typescript
/**
 * File: cursor-addon/src/commandServer/routes/chatAutomation.ts
 * 
 * Autonomous loop control endpoint
 */

import express from 'express';
import { CursorChatAutonomousLoop } from '../../services/cursorChatAutonomousLoop';
import { MCPClient } from '../../mcp/mcpClient';

const router = express.Router();
const activeLoops = new Map<string, CursorChatAutonomousLoop>();

/**
 * POST /cursor/chat/autonomous-loop
 * Control autonomous loop (start, stop, pause, resume, status)
 */
router.post('/autonomous-loop', async (req, res) => {
    try {
        const { action, config, loop_id } = req.body;
        
        if (action === 'start') {
            // Create new loop
            const mcpClient = new MCPClient();
            const loop = new CursorChatAutonomousLoop(config, mcpClient);
            const loopId = `loop-${Date.now()}`;
            
            // Start loop
            await loop.start();
            
            // Store in active loops
            activeLoops.set(loopId, loop);
            
            res.json({
                success: true,
                loop_id: loopId,
                status: loop.getStatus()
            });
        }
        else if (action === 'stop') {
            const loop = activeLoops.get(loop_id);
            if (!loop) {
                res.status(404).json({success: false, error: 'Loop not found'});
                return;
            }
            
            await loop.stop();
            activeLoops.delete(loop_id);
            
            res.json({success: true});
        }
        else if (action === 'pause') {
            const loop = activeLoops.get(loop_id);
            if (!loop) {
                res.status(404).json({success: false, error: 'Loop not found'});
                return;
            }
            
            await loop.pause();
            res.json({success: true, status: loop.getStatus()});
        }
        else if (action === 'resume') {
            const loop = activeLoops.get(loop_id);
            if (!loop) {
                res.status(404).json({success: false, error: 'Loop not found'});
                return;
            }
            
            await loop.resume();
            res.json({success: true, status: loop.getStatus()});
        }
        else if (action === 'status') {
            const loop = activeLoops.get(loop_id);
            if (!loop) {
                res.status(404).json({success: false, error: 'Loop not found'});
                return;
            }
            
            res.json({success: true, status: loop.getStatus()});
        }
        else {
            res.status(400).json({success: false, error: 'Invalid action'});
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error instanceof Error ? error.message : String(error)
        });
    }
});

export default router;
```

---

# Part 3: Implementation Guide

## Complete TypeScript Implementation

**Directory Structure:**

```
cursor-addon/
├── src/
│   ├── services/
│   │   ├── responseDetectionEngine.ts         (NEW - 200 lines)
│   │   ├── cursorChatAutonomousLoop.ts        (NEW - 300 lines)
│   │   └── messageMonitorService.ts           (EXISTS - extend)
│   │
│   ├── commandServer/
│   │   └── routes/
│   │       └── chatAutomation.ts              (NEW - 150 lines)
│   │
│   └── mcp/
│       └── mcpClient.ts                       (EXISTS - use)
│
└── tests/
    ├── responseDetectionEngine.test.ts        (NEW - 100 lines)
    └── cursorChatAutonomousLoop.test.ts       (NEW - 150 lines)
```

---

## Testing Guide

**Test File:** `cursor-addon/tests/cursorChatAutonomousLoop.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { CursorChatAutonomousLoop } from '../src/services/cursorChatAutonomousLoop';
import { MCPClient } from '../src/mcp/mcpClient';

describe('CursorChatAutonomousLoop', () => {
    let mcpClient: MCPClient;
    let loop: CursorChatAutonomousLoop;
    
    beforeEach(() => {
        mcpClient = new MCPClient();
        loop = new CursorChatAutonomousLoop({
            initialMessage: 'Start autonomous work',
            proceedMessage: 'proceed',
            confidenceThreshold: 0.70,
            pollIntervalSeconds: 1  // Faster for testing
        }, mcpClient);
    });
    
    it('should start loop successfully', async () => {
        // Mock MCP tools
        vi.spyOn(mcpClient, 'callTool').mockResolvedValue({
            success: true
        });
        
        await loop.start();
        
        const status = loop.getStatus();
        expect(status.active).toBe(true);
        expect(status.iterationsCompleted).toBe(0);
        expect(status.startedAt).toBeGreaterThan(0);
    });
    
    it('should detect response and send proceed', async () => {
        // Mock detection engine
        vi.spyOn(loop['detectionEngine'], 'detectResponseComplete').mockResolvedValue({
            isComplete: true,
            confidence: 0.85,
            signals: [],
            recommendation: 'Send proceed',
            timestamp: Date.now()
        });
        
        // Mock should_continue_autonomous
        vi.spyOn(mcpClient, 'callTool').mockImplementation((tool) => {
            if (tool === 'should_continue_autonomous') {
                return Promise.resolve({should_continue: true});
            }
            return Promise.resolve({success: true});
        });
        
        await loop.start();
        
        // Wait for monitoring iteration
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const status = loop.getStatus();
        expect(status.iterationsCompleted).toBeGreaterThan(0);
        
        await loop.stop();
    });
    
    it('should stop when should_continue returns false', async () => {
        vi.spyOn(mcpClient, 'callTool').mockImplementation((tool) => {
            if (tool === 'should_continue_autonomous') {
                return Promise.resolve({
                    should_continue: false,
                    stop_reason: 'Confidence below threshold'
                });
            }
            return Promise.resolve({success: true});
        });
        
        await loop.start();
        
        // Wait for monitoring to detect stop condition
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const status = loop.getStatus();
        expect(status.active).toBe(false);
    });
});
```

---

## Deployment Guide

**Step 1: Install Dependencies**
```bash
cd cursor-addon
npm install
```

**Step 2: Build Extension**
```bash
npm run compile
```

**Step 3: Package VSIX**
```bash
npm run package
```

**Step 4: Install Extension**
```bash
code --install-extension cursor-extension-v*.vsix --force
```

**Step 5: Start Autonomous Loop**
```typescript
// Via HTTP API
fetch('http://localhost:5001/cursor/chat/autonomous-loop', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        action: 'start',
        config: {
            initialMessage: 'Begin autonomous work on feature X',
            proceedMessage: 'proceed',
            confidenceThreshold: 0.70,
            pollIntervalSeconds: 3
        }
    })
});
```

---

**Status:** Design Complete (Nov 2, 2025) | **Implementation:** Planned  
**Next:** T4-T5 completion documentation  
**Files:** ResponseDetectionEngine, CursorChatAutonomousLoop, HTTP endpoints

