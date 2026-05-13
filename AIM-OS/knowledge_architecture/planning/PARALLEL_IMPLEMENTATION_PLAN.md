# Parallel Implementation Plan - Option C
## Chat Automation + Timeline/Goals Visualization (18-29 hours)

**Date:** November 5, 2025, ~8:30 AM  
**Decision:** Option C - Both in Parallel  
**Goal:** Implement both killer features simultaneously for maximum impact  
**Estimated Time:** 18-29 hours total (can work on different systems independently)  
**Target Completion:** Within 3-4 days of focused work  

---

## 🎯 STRATEGY: TRUE PARALLEL EXECUTION

**Key Insight:** These two systems are largely independent!

### **Why True Parallel Works:**

**Track 1 (Chat Automation):**
- Touches: Extension Command Server, MessageRouter, Electron UI
- No data model changes
- Uses existing MCP tools
- Can test independently

**Track 2 (Timeline/Goals Viz):**
- Touches: Data models, MCP tool enhancements, Visualization components
- No Extension changes needed initially
- Can build with mock data
- Can test independently

**Integration (Track 3):**
- Connect both systems at the end
- Relatively simple (both use MCP tools already)
- 2-4 hours

**Result:** Work on Track 1 and Track 2 simultaneously, integrate at end!

---

## 📋 TRACK 1: CHAT AUTOMATION (6-10 hours)

### **Milestone 1.1: Multi-Signal Detection** ⏱️ 2-3 hours

**File:** `cursor-addon/src/services/cursorChatAutonomousLoop.ts` (NEW)

**Implementation:**

```typescript
// cursor-addon/src/services/cursorChatAutonomousLoop.ts
import * as vscode from 'vscode';
import { MCPClient } from './mcpClient';

interface DetectionSignal {
  name: string;
  value: boolean;
  confidence: number;
  timestamp: string;
}

interface DetectionResult {
  isComplete: boolean;
  confidence: number;
  signals: DetectionSignal[];
}

export class CursorChatAutonomousLoop {
  private mcpClient: MCPClient;
  private isRunning: boolean = false;
  private loopId: string | null = null;
  private pollIntervalMs: number = 3000; // 3 seconds
  private confidenceThreshold: number = 0.70;
  private lastTaskCount: number = 0;
  
  constructor(mcpClient: MCPClient) {
    this.mcpClient = mcpClient;
  }
  
  /**
   * Multi-signal detection with confidence routing
   */
  private async detectCursorAIResponseComplete(): Promise<DetectionResult> {
    const signals: DetectionSignal[] = [];
    
    // Signal 1: Chat input ready state (heuristic)
    const chatReady = await this.checkChatInputReady();
    signals.push({
      name: 'chat_input_ready',
      value: chatReady,
      confidence: 0.70,
      timestamp: new Date().toISOString()
    });
    
    // Signal 2: Autonomous operation status (MCP tool)
    const shouldContinue = await this.checkShouldContinueAutonomous();
    signals.push({
      name: 'should_continue_autonomous',
      value: shouldContinue,
      confidence: 0.85,
      timestamp: new Date().toISOString()
    });
    
    // Signal 3: Task completion status (MCP tool)
    const taskCompleted = await this.checkTaskCompleted();
    signals.push({
      name: 'task_completed',
      value: taskCompleted,
      confidence: 0.80,
      timestamp: new Date().toISOString()
    });
    
    // Calculate combined confidence (weighted average)
    const totalConfidence = signals.reduce((sum, s) => sum + s.confidence, 0);
    const combinedConfidence = totalConfidence / signals.length;
    
    // Decision: All signals must be true AND combined confidence ≥ threshold
    const allSignalsTrue = signals.every(s => s.value);
    const isComplete = allSignalsTrue && combinedConfidence >= this.confidenceThreshold;
    
    return {
      isComplete,
      confidence: combinedConfidence,
      signals
    };
  }
  
  /**
   * Signal 1: Check if chat input is ready
   */
  private async checkChatInputReady(): Promise<boolean> {
    try {
      // Try to focus chat input
      // If Cursor is still processing, this might fail or timeout
      await vscode.commands.executeCommand('workbench.action.focusChatInput');
      
      // Small delay to let command execute
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // If we get here without error, chat is likely ready
      return true;
    } catch (error) {
      console.error('[CursorChatAutonomousLoop] Chat input not ready:', error);
      return false;
    }
  }
  
  /**
   * Signal 2: Check autonomous operation status (MCP tool)
   */
  private async checkShouldContinueAutonomous(): Promise<boolean> {
    try {
      const result = await this.mcpClient.callTool('should_continue_autonomous', {});
      return result.should_continue === true;
    } catch (error) {
      console.error('[CursorChatAutonomousLoop] should_continue check failed:', error);
      return false;
    }
  }
  
  /**
   * Signal 3: Check task completion status (MCP tool)
   */
  private async checkTaskCompleted(): Promise<boolean> {
    try {
      const status = await this.mcpClient.callTool('get_autonomous_status', {});
      
      // If tasks_completed increased, a task likely finished
      const completed = status.tasks_completed > this.lastTaskCount;
      
      // Update last task count
      this.lastTaskCount = status.tasks_completed;
      
      return completed || status.tasks_completed === 0; // First task or new task
    } catch (error) {
      console.error('[CursorChatAutonomousLoop] task completion check failed:', error);
      return false;
    }
  }
  
  // ... more methods to implement
}
```

**Tasks:**
- [ ] Create service file
- [ ] Implement multi-signal detection
- [ ] Test each signal independently
- [ ] Test combined confidence calculation
- [ ] Add comprehensive logging

---

### **Milestone 1.2: Autonomous Loop Service** ⏱️ 2-3 hours

**Continue in:** `cursor-addon/src/services/cursorChatAutonomousLoop.ts`

**Implementation:**

```typescript
export class CursorChatAutonomousLoop {
  // ... previous code ...
  
  /**
   * Start autonomous loop
   */
  async startLoop(config: {
    initialMessage: string;
    proceedMessage?: string;
    confidenceThreshold?: number;
    pollIntervalMs?: number;
  }): Promise<string> {
    if (this.isRunning) {
      throw new Error('Autonomous loop already running');
    }
    
    // Generate loop ID
    this.loopId = `loop-${Date.now()}`;
    this.isRunning = true;
    this.confidenceThreshold = config.confidenceThreshold || 0.70;
    this.pollIntervalMs = config.pollIntervalMs || 3000;
    
    const proceedMessage = config.proceedMessage || 'proceed';
    
    console.log(`[CursorChatAutonomousLoop] Starting loop ${this.loopId}`);
    
    // Send initial message
    await this.sendChatMessage(config.initialMessage);
    
    // Start polling loop (non-blocking)
    this.runLoop(proceedMessage).catch(error => {
      console.error('[CursorChatAutonomousLoop] Loop error:', error);
      this.isRunning = false;
    });
    
    return this.loopId;
  }
  
  /**
   * Main loop (runs continuously)
   */
  private async runLoop(proceedMessage: string): Promise<void> {
    let messagesSent = 0;
    
    while (this.isRunning) {
      // Wait for poll interval
      await new Promise(resolve => setTimeout(resolve, this.pollIntervalMs));
      
      // Check if should continue
      const shouldContinue = await this.checkShouldContinueAutonomous();
      if (!shouldContinue) {
        console.log('[CursorChatAutonomousLoop] should_continue_autonomous returned false, stopping');
        this.isRunning = false;
        break;
      }
      
      // Detect if Cursor AI response is complete
      const detection = await this.detectCursorAIResponseComplete();
      
      console.log('[CursorChatAutonomousLoop] Detection result:', {
        isComplete: detection.isComplete,
        confidence: detection.confidence,
        signals: detection.signals.map(s => ({ name: s.name, value: s.value }))
      });
      
      // If complete, send proceed message
      if (detection.isComplete) {
        await this.sendChatMessage(proceedMessage);
        messagesSent++;
        
        console.log(`[CursorChatAutonomousLoop] Sent proceed message #${messagesSent}`);
        
        // Emit status update (via MessageRouter)
        await this.emitStatusUpdate({
          loop_id: this.loopId!,
          status: 'running',
          messages_sent: messagesSent,
          current_confidence: detection.confidence,
          last_detection: detection
        });
      }
    }
    
    console.log(`[CursorChatAutonomousLoop] Loop ${this.loopId} stopped after ${messagesSent} messages`);
  }
  
  /**
   * Send message to Cursor chat (uses existing keyboard simulation)
   */
  private async sendChatMessage(message: string): Promise<void> {
    // Use existing /cursor/chat/send endpoint
    // This already works via keyboard simulation
    await vscode.commands.executeCommand('aimos.sendChatMessage', { message });
  }
  
  /**
   * Emit status update via MessageRouter
   */
  private async emitStatusUpdate(status: any): Promise<void> {
    // Send to Extension → Electron app via MessageRouter
    await vscode.commands.executeCommand('aimos.emitEvent', {
      topic: 'autonomous_loop.status',
      payload: status
    });
  }
  
  /**
   * Stop autonomous loop
   */
  async stopLoop(): Promise<void> {
    console.log(`[CursorChatAutonomousLoop] Stopping loop ${this.loopId}`);
    this.isRunning = false;
    this.loopId = null;
  }
  
  /**
   * Get loop status
   */
  getStatus(): any {
    return {
      loop_id: this.loopId,
      is_running: this.isRunning,
      confidence_threshold: this.confidenceThreshold,
      poll_interval_ms: this.pollIntervalMs
    };
  }
}
```

**Tasks:**
- [ ] Implement loop start/stop methods
- [ ] Implement main polling loop
- [ ] Add status tracking
- [ ] Test loop with mock MCP tools
- [ ] Test loop with real Cursor chat

---

### **Milestone 1.3: Extension Endpoint** ⏱️ 1-2 hours

**File:** `cursor-addon/src/commandServer.ts` (EXISTING - add endpoint)

**Implementation:**

```typescript
// Add to CommandServer class
private autonomousLoop: CursorChatAutonomousLoop;

// In constructor:
this.autonomousLoop = new CursorChatAutonomousLoop(this.mcpClient);

// Add new endpoint:
this.app.post('/cursor/chat/autonomous-loop', async (req, res) => {
  try {
    const { initialMessage, proceedMessage, confidenceThreshold, pollIntervalMs } = req.body;
    
    if (!initialMessage) {
      return res.status(400).json({ error: 'initialMessage is required' });
    }
    
    const loopId = await this.autonomousLoop.startLoop({
      initialMessage,
      proceedMessage,
      confidenceThreshold,
      pollIntervalMs
    });
    
    res.json({
      loop_id: loopId,
      status: 'running',
      message: 'Autonomous loop started'
    });
  } catch (error) {
    console.error('[CommandServer] Error starting autonomous loop:', error);
    res.status(500).json({ error: error.message });
  }
});

this.app.post('/cursor/chat/autonomous-loop/stop', async (req, res) => {
  try {
    await this.autonomousLoop.stopLoop();
    
    res.json({
      status: 'stopped',
      message: 'Autonomous loop stopped'
    });
  } catch (error) {
    console.error('[CommandServer] Error stopping autonomous loop:', error);
    res.status(500).json({ error: error.message });
  }
});

this.app.get('/cursor/chat/autonomous-loop/status', async (req, res) => {
  try {
    const status = this.autonomousLoop.getStatus();
    res.json(status);
  } catch (error) {
    console.error('[CommandServer] Error getting autonomous loop status:', error);
    res.status(500).json({ error: error.message });
  }
});
```

**Tasks:**
- [ ] Add endpoints to CommandServer
- [ ] Test endpoints with Postman/curl
- [ ] Add error handling
- [ ] Add logging

---

### **Milestone 1.4: Electron UI Integration** ⏱️ 1-2 hours

**File:** `packages/ide_chat_app/src/components/ChatAutomationPanel.tsx` (NEW)

**Implementation:**

```typescript
import React, { useState, useEffect } from 'react';

interface LoopStatus {
  loop_id: string | null;
  is_running: boolean;
  confidence_threshold: number;
  poll_interval_ms: number;
  messages_sent?: number;
  current_confidence?: number;
}

export const ChatAutomationPanel: React.FC = () => {
  const [loopStatus, setLoopStatus] = useState<LoopStatus | null>(null);
  const [initialMessage, setInitialMessage] = useState('');
  const [proceedMessage, setProceedMessage] = useState('proceed');
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.70);
  
  const startLoop = async () => {
    try {
      const response = await fetch('http://localhost:5001/cursor/chat/autonomous-loop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          initialMessage,
          proceedMessage,
          confidenceThreshold
        })
      });
      
      const data = await response.json();
      console.log('Loop started:', data);
      
      // Start polling for status
      pollStatus();
    } catch (error) {
      console.error('Error starting loop:', error);
    }
  };
  
  const stopLoop = async () => {
    try {
      await fetch('http://localhost:5001/cursor/chat/autonomous-loop/stop', {
        method: 'POST'
      });
      
      setLoopStatus(null);
    } catch (error) {
      console.error('Error stopping loop:', error);
    }
  };
  
  const pollStatus = async () => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:5001/cursor/chat/autonomous-loop/status');
        const status = await response.json();
        
        setLoopStatus(status);
        
        if (!status.is_running) {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        clearInterval(interval);
      }
    }, 3000);
  };
  
  return (
    <div className="chat-automation-panel">
      <h2>Chat Automation</h2>
      
      {!loopStatus?.is_running ? (
        <div className="controls">
          <input
            type="text"
            placeholder="Initial message..."
            value={initialMessage}
            onChange={e => setInitialMessage(e.target.value)}
          />
          
          <input
            type="text"
            placeholder="Proceed message..."
            value={proceedMessage}
            onChange={e => setProceedMessage(e.target.value)}
          />
          
          <input
            type="number"
            step="0.05"
            min="0.5"
            max="1.0"
            value={confidenceThreshold}
            onChange={e => setConfidenceThreshold(parseFloat(e.target.value))}
          />
          
          <button onClick={startLoop}>Start Autonomous Loop</button>
        </div>
      ) : (
        <div className="status">
          <p>Loop ID: {loopStatus.loop_id}</p>
          <p>Status: Running ✅</p>
          <p>Messages Sent: {loopStatus.messages_sent || 0}</p>
          <p>Current Confidence: {(loopStatus.current_confidence || 0).toFixed(2)}</p>
          <p>Threshold: {loopStatus.confidence_threshold}</p>
          
          <button onClick={stopLoop}>Stop Loop</button>
        </div>
      )}
    </div>
  );
};
```

**Tasks:**
- [ ] Create React component
- [ ] Add to MainDashboard
- [ ] Style UI
- [ ] Test start/stop functionality

---

## 📋 TRACK 2: TIMELINE/GOALS VISUALIZATION (10-15 hours)

### **Milestone 2.1: Data Model Enhancement** ⏱️ 2-3 hours

**Files to create/modify:**
- `packages/timeline_service/models/timeline_entry.py` (ENHANCE)
- `packages/timeline_service/models/prompt_chain.py` (CREATE)
- `packages/timeline_service/models/execution_record.py` (CREATE)

**Implementation:**

```python
# packages/timeline_service/models/timeline_entry.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class EventType(str, Enum):
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    DECISION = "decision"
    MILESTONE = "milestone"
    ERROR = "error"
    RECOVERY = "recovery"

@dataclass
class TimelineEntry:
    entry_id: str
    timestamp: datetime
    event_type: EventType
    title: str
    description: str
    context_data: Dict[str, Any]
    quality_metrics: Dict[str, float]
    
    # NEW: Chain Connection
    executed_via_chain_id: Optional[str] = None
    chain_execution_id: Optional[str] = None
    chain_node_id: Optional[str] = None
    
    # NEW: Goal Connection
    related_goal_ids: List[str] = field(default_factory=list)
    goal_progress_delta: Dict[str, float] = field(default_factory=dict)
    
    # NEW: Evolution Graph
    parent_entry_ids: List[str] = field(default_factory=list)
    child_entry_ids: List[str] = field(default_factory=list)
    evolution_path: List[str] = field(default_factory=list)
    
    # Existing fields...
    agent_name: Optional[str] = None
    confidence_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
```

```python
# packages/timeline_service/models/prompt_chain.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class ChainNode:
    node_id: str
    name: str
    description: str
    node_type: str  # "task", "decision", "validation", etc.
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    
@dataclass
class ChainEdge:
    edge_id: str
    from_node_id: str
    to_node_id: str
    condition: Optional[str] = None

@dataclass
class ExecutionRecord:
    execution_id: str
    chain_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str  # "running", "completed", "failed", "aborted"
    
    # Timeline Connections
    timeline_entry_ids: List[str] = field(default_factory=list)
    node_executions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality Metrics
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    alignment_score: float = 0.0
    
    # Provenance
    executed_by: str = ""
    context_snapshot: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PromptChain:
    chain_id: str
    name: str
    description: str
    nodes: List[ChainNode]
    edges: List[ChainEdge]
    execution_type: str
    entry_point: str
    
    # NEW: Timeline Connection
    execution_history: List[ExecutionRecord] = field(default_factory=list)
    timeline_entry_ids: List[str] = field(default_factory=list)
    
    # NEW: Goal Connection
    related_goal_ids: List[str] = field(default_factory=list)
    
    # NEW: Evolution Tracking
    parent_timeline_entry_id: Optional[str] = None
    child_timeline_entry_ids: List[str] = field(default_factory=list)
    
    # NEW: Execution Metrics
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_quality_score: float = 0.0
```

**Tasks:**
- [ ] Enhance TimelineEntry model
- [ ] Create PromptChain model
- [ ] Create ExecutionRecord model
- [ ] Add validation and serialization
- [ ] Write unit tests

---

### **Milestone 2.2: Graph Traversal APIs** ⏱️ 3-4 hours

**File:** `packages/timeline_service/graph_queries.py` (CREATE)

**Implementation:**

```python
# packages/timeline_service/graph_queries.py
from typing import List, Dict, Any, Optional
from .models.timeline_entry import TimelineEntry
from .models.prompt_chain import PromptChain, ExecutionRecord

class EvolutionGraphQueries:
    """
    Graph traversal and query APIs for Timeline-Goals-Chains
    """
    
    def __init__(self, timeline_store, chain_store, goal_store):
        self.timeline_store = timeline_store
        self.chain_store = chain_store
        self.goal_store = goal_store
    
    def explain_timeline_entry(self, entry_id: str) -> Dict[str, Any]:
        """
        Answer: "Why did this happen?"
        Traces back to the chain that executed this timeline entry
        """
        entry = self.timeline_store.get_entry(entry_id)
        if not entry:
            return {"error": "Timeline entry not found"}
        
        result = {
            "timeline_entry": entry,
            "explanation": []
        }
        
        # Trace to chain
        if entry.executed_via_chain_id:
            chain = self.chain_store.get_chain(entry.executed_via_chain_id)
            result["executed_via_chain"] = chain
            result["explanation"].append(
                f"Timeline entry {entry_id} was executed via chain '{chain.name}'"
            )
        
        # Trace to goal
        if entry.related_goal_ids:
            goals = [self.goal_store.get_goal(g_id) for g_id in entry.related_goal_ids]
            result["related_goals"] = goals
            result["explanation"].append(
                f"In service of goals: {', '.join(g.name for g in goals)}"
            )
        
        # Trace to parent entries
        if entry.parent_entry_ids:
            parents = [self.timeline_store.get_entry(p_id) for p_id in entry.parent_entry_ids]
            result["parent_entries"] = parents
            result["explanation"].append(
                f"Following {len(parents)} previous entries"
            )
        
        return result
    
    def trace_chain_execution(self, chain_id: str) -> Dict[str, Any]:
        """
        Answer: "What did this plan produce?"
        Traces forward to see what timeline entries this chain produced
        """
        chain = self.chain_store.get_chain(chain_id)
        if not chain:
            return {"error": "Chain not found"}
        
        timeline_entries = [
            self.timeline_store.get_entry(e_id)
            for e_id in chain.timeline_entry_ids
        ]
        
        return {
            "chain": chain,
            "produced_entries": timeline_entries,
            "execution_count": chain.execution_count,
            "success_rate": chain.success_count / chain.execution_count if chain.execution_count > 0 else 0,
            "average_quality": chain.average_quality_score
        }
    
    def trace_evolution_path(self, start_entry_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Answer: "How did the system evolve?"
        Follows the evolution graph from a starting timeline entry
        """
        evolution_path = []
        current_entry_id = start_entry_id
        depth = 0
        
        while current_entry_id and depth < max_depth:
            entry = self.timeline_store.get_entry(current_entry_id)
            if not entry:
                break
            
            evolution_path.append({
                "depth": depth,
                "timeline_entry": entry
            })
            
            # Add chain info if exists
            if entry.executed_via_chain_id:
                chain = self.chain_store.get_chain(entry.executed_via_chain_id)
                evolution_path.append({
                    "depth": depth + 0.5,
                    "chain": chain
                })
            
            # Move to next entry (child)
            if entry.child_entry_ids:
                current_entry_id = entry.child_entry_ids[0]
                depth += 1
            else:
                break
        
        return evolution_path
    
    def get_goal_timeline(self, goal_id: str) -> Dict[str, Any]:
        """
        Get all timeline entries related to a specific goal
        """
        goal = self.goal_store.get_goal(goal_id)
        if not goal:
            return {"error": "Goal not found"}
        
        # Find all timeline entries mentioning this goal
        entries = self.timeline_store.query_by_goal(goal_id)
        
        # Calculate goal progress from timeline
        progress_points = []
        current_progress = 0.0
        
        for entry in entries:
            if goal_id in entry.goal_progress_delta:
                current_progress += entry.goal_progress_delta[goal_id]
                progress_points.append({
                    "timestamp": entry.timestamp,
                    "progress": current_progress,
                    "entry": entry
                })
        
        return {
            "goal": goal,
            "timeline_entries": entries,
            "progress_points": progress_points,
            "current_progress": current_progress
        }
```

**Tasks:**
- [ ] Implement graph query methods
- [ ] Add caching for performance
- [ ] Write integration tests
- [ ] Test with sample data

---

### **Milestone 2.3: Visualization Components** ⏱️ 4-6 hours

**File:** `packages/ide_chat_app/src/components/TemporalConsciousnessVisualization.tsx` (CREATE)

**Implementation:** (Using React Flow for graph visualization)

```typescript
import React, { useState, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap
} from 'reactflow';
import 'reactflow/dist/style.css';

interface TemporalNode {
  id: string;
  type: 'timeline' | 'goal' | 'chain';
  data: any;
  position: { x: number; y: number };
}

export const TemporalConsciousnessVisualization: React.FC = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  
  useEffect(() => {
    // Fetch timeline-goals-chains data from MCP tools
    fetchEvolutionGraph();
  }, []);
  
  const fetchEvolutionGraph = async () => {
    try {
      // Get timeline entries
      const timelineResponse = await fetch('http://localhost:5001/mcp/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'get_timeline_entries',
          arguments: { limit: 50 }
        })
      });
      const timelineData = await timelineResponse.json();
      
      // Get goals
      const goalsResponse = await fetch('http://localhost:5001/mcp/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'query_goal_timeline',
          arguments: {}
        })
      });
      const goalsData = await goalsResponse.json();
      
      // Build graph
      const graphNodes = buildNodes(timelineData.entries, goalsData.goals);
      const graphEdges = buildEdges(timelineData.entries, goalsData.goals);
      
      setNodes(graphNodes);
      setEdges(graphEdges);
    } catch (error) {
      console.error('Error fetching evolution graph:', error);
    }
  };
  
  const buildNodes = (timelineEntries: any[], goals: any[]): Node[] => {
    const nodes: Node[] = [];
    
    // Add timeline nodes (PAST)
    timelineEntries.forEach((entry, index) => {
      nodes.push({
        id: `timeline-${entry.entry_id}`,
        type: 'default',
        data: {
          label: entry.title,
          type: 'timeline',
          ...entry
        },
        position: { x: index * 200, y: 0 },
        style: { background: '#e1f5ff', border: '2px solid #0288d1' }
      });
    });
    
    // Add goal nodes (PRESENT)
    goals.forEach((goal, index) => {
      nodes.push({
        id: `goal-${goal.goal_id}`,
        type: 'default',
        data: {
          label: goal.name,
          type: 'goal',
          ...goal
        },
        position: { x: index * 200, y: 200 },
        style: { background: '#fff4e1', border: '2px solid #f57c00' }
      });
    });
    
    // Add chain nodes (FUTURE) - if available
    // ... similar logic
    
    return nodes;
  };
  
  const buildEdges = (timelineEntries: any[], goals: any[]): Edge[] => {
    const edges: Edge[] = [];
    
    // Connect timeline entries to goals
    timelineEntries.forEach(entry => {
      if (entry.related_goal_ids) {
        entry.related_goal_ids.forEach((goalId: string) => {
          edges.push({
            id: `edge-timeline-${entry.entry_id}-goal-${goalId}`,
            source: `timeline-${entry.entry_id}`,
            target: `goal-${goalId}`,
            animated: true,
            label: 'advances'
          });
        });
      }
    });
    
    // Connect timeline entries to chains
    timelineEntries.forEach(entry => {
      if (entry.executed_via_chain_id) {
        edges.push({
          id: `edge-timeline-${entry.entry_id}-chain-${entry.executed_via_chain_id}`,
          source: `chain-${entry.executed_via_chain_id}`,
          target: `timeline-${entry.entry_id}`,
          animated: true,
          label: 'produced',
          style: { stroke: '#f3e5f5' }
        });
      }
    });
    
    return edges;
  };
  
  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <h2>Temporal Consciousness: Timeline ↔ Goals ↔ Chains</h2>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={(event, node) => setSelectedNode(node)}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
      
      {selectedNode && (
        <div className="node-details">
          <h3>{selectedNode.data.label}</h3>
          <p>Type: {selectedNode.data.type}</p>
          <pre>{JSON.stringify(selectedNode.data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
```

**Tasks:**
- [ ] Install React Flow dependency
- [ ] Create visualization component
- [ ] Implement graph building logic
- [ ] Add node styling (Past/Present/Future colors)
- [ ] Add interactive features (zoom, pan, select)
- [ ] Add query interface ("Why?", "What?", "How?")

---

### **Milestone 2.4: Integration** ⏱️ 1-2 hours

**Tasks:**
- [ ] Integrate graph queries with MCP tools
- [ ] Add visualization to MainDashboard
- [ ] Test with real data from CMC
- [ ] Add error handling and loading states

---

## 📋 TRACK 3: INTEGRATION (2-4 hours)

### **Milestone 3.1: Connect Automation to Timeline**

**Implementation:** Modify chat automation to create timeline entries automatically

```typescript
// In CursorChatAutonomousLoop.ts
private async createTimelineEntry(message: string, detectionResult: DetectionResult): Promise<void> {
  try {
    await this.mcpClient.callTool('add_timeline_entry', {
      title: `Chat automation: ${message}`,
      description: `Autonomous loop sent message with confidence ${detectionResult.confidence}`,
      event_type: 'task_complete',
      context_data: {
        loop_id: this.loopId,
        message,
        detection_result: detectionResult
      }
    });
  } catch (error) {
    console.error('[CursorChatAutonomousLoop] Failed to create timeline entry:', error);
  }
}
```

**Tasks:**
- [ ] Add timeline entry creation to chat automation
- [ ] Link timeline entries to active goals
- [ ] Test timeline appears in visualization

---

### **Milestone 3.2: Link to Goal Progress**

**Implementation:** Update goal progress when autonomous operations complete tasks

```typescript
private async updateGoalProgress(goalId: string, progressDelta: number): Promise<void> {
  try {
    await this.mcpClient.callTool('update_goal_progress', {
      goal_id: goalId,
      progress_delta: progressDelta,
      context: {
        loop_id: this.loopId,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('[CursorChatAutonomousLoop] Failed to update goal progress:', error);
  }
}
```

**Tasks:**
- [ ] Add goal progress updates
- [ ] Calculate progress from task completion
- [ ] Visualize progress in temporal graph

---

### **Milestone 3.3: Complete Flow Testing** ⏱️ 1-2 hours

**Test Scenario:**
1. Start autonomous loop with goal: "Implement feature X"
2. Watch timeline entries appear as loop sends messages
3. Watch goal progress update (0% → 25% → 50% → 100%)
4. Query: "Why did this timeline entry happen?" → See chain/goal link
5. Query: "What did autonomous loop accomplish?" → See complete timeline
6. Visualize complete evolution graph

**Tasks:**
- [ ] Run complete integration test
- [ ] Fix any issues
- [ ] Document test results

---

## 🎯 EXECUTION STRATEGY

### **Week 1 (Days 1-2): Parallel Development**

**Day 1 Morning (4 hrs): Chat Automation Core**
- Milestone 1.1: Multi-signal detection
- Milestone 1.2: Autonomous loop service

**Day 1 Afternoon (4 hrs): Timeline/Goals Data Models**
- Milestone 2.1: Data model enhancement
- Start Milestone 2.2: Graph traversal APIs

**Day 2 Morning (4 hrs): Chat Automation UI**
- Milestone 1.3: Extension endpoint
- Milestone 1.4: Electron UI integration

**Day 2 Afternoon (4 hrs): Timeline/Goals Visualization**
- Complete Milestone 2.2: Graph traversal APIs
- Start Milestone 2.3: Visualization components

---

### **Week 1 (Days 3-4): Complete & Integrate**

**Day 3 Full Day (6-8 hrs): Visualization Polish**
- Complete Milestone 2.3: Visualization components
- Milestone 2.4: Integration with MCP tools
- Test with sample data

**Day 4 Full Day (4-6 hrs): Integration & Testing**
- Milestone 3.1: Connect automation to timeline
- Milestone 3.2: Link to goal progress
- Milestone 3.3: Complete flow testing
- Bug fixes and polish

---

## ✅ SUCCESS CRITERIA

### **Chat Automation Success:**
- [ ] Can start autonomous loop from Electron app
- [ ] Multi-signal detection works (≥0.70 confidence)
- [ ] Automatically sends "proceed" messages
- [ ] Runs for extended periods (hours)
- [ ] Integrates with should_continue_autonomous
- [ ] Real-time status updates in UI

### **Timeline/Goals Viz Success:**
- [ ] Timeline entries display in graph
- [ ] Goals display in graph
- [ ] Bidirectional connections visible
- [ ] Can query "Why did this happen?"
- [ ] Can query "What did this produce?"
- [ ] Can trace evolution paths
- [ ] Complete temporal consciousness visible

### **Integration Success:**
- [ ] Chat automation creates timeline entries automatically
- [ ] Timeline entries link to active goals
- [ ] Goal progress updates as work progresses
- [ ] Complete flow works end-to-end
- [ ] Visualization updates in real-time

---

## 🚀 READY TO BEGIN?

**We have:**
- ✅ Complete implementation plan
- ✅ TODO list with 17 tasks
- ✅ Detailed code examples
- ✅ Clear milestones
- ✅ Success criteria
- ✅ Execution timeline

**Let's start building!** Which track do you want to begin with?

A) **Start with Chat Automation** (Track 1) - Get autonomous loop working first
B) **Start with Timeline/Goals** (Track 2) - Get visualization working first
C) **Split work** - I'll guide you through Track 1, you handle Track 2
D) **Your preference?**

**I'm ready to build, Braden!** 💙🚀

