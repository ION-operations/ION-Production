# Chronos → Codex: Timeline Logging Details for Chat/IDE Integration

**Date:** 2025-01-28  
**Route:** Chat/IDE Coordination  
**Status:** ✅ **READY** - Timeline logging hooks documented

---

## 🎯 **OVERVIEW**

This document provides comprehensive details for integrating TCS timeline logging into the chat/IDE orchestration layer. All timeline logging uses the MCP tool `add_timeline_entry`, which stores entries in CMC with `modality="tcs_timeline"` for HHNI indexing and retrieval.

---

## 📋 **1. TIMELINE LOGGING HOOKS FOR CHAT/IDE ACTIONS**

### **1.1 Basic Timeline Entry Creation**

**MCP Tool:** `mcp_lucid-mcp_add_timeline_entry`

**When to Call:**
- User sends message → Create timeline entry
- AI responds → Create timeline entry
- Orchestrated action completes → Create timeline entry
- κ-gate decision made → Create timeline entry (see section 2)
- APOE plan milestone reached → Create timeline entry (see section 3)

**Basic Usage:**
```typescript
// In MCPService.ts or orchestration layer
const timelineResult = await mcpClient.callTool('mcp_lucid-mcp_add_timeline_entry', {
  prompt_id: `chat_action_${uuid()}`,  // Unique identifier
  user_input: "User sent message: 'Implement feature X'",  // Human-readable description
  context_state: {
    // Event metadata
    event_type: "user_message",  // or "ai_response", "orchestrated_action", etc.
    event_category: "chat_interaction",
    
    // Chat/IDE context
    chat_drawer: "coding",  // or "planning"
    thinking_mode: "execution",  // or "research", "synthesis"
    agent_name: "Coding Agent",
    
    // Action details
    action_type: "code_generation",
    action_result: "success",  // or "failure", "partial"
    
    // Integration tags (standardized format)
    integration_tags: [
      "system:tcs:p0",
      "integration_type:timeline",
      "connection:chat->tcs",
      "modality:tcs_timeline"
    ],
    
    // Quality metrics
    quality_metrics: {
      confidence: 0.85,
      relevance: 1.0,
    },
    
    // Technical details
    technical_details: {
      timestamp: new Date().toISOString(),
      session_id: sessionId,
      correlation_id: correlationId,
    },
    
    // Metadata for query indexing
    metadata: {
      source_system: "chat_ide",
      event_category: "chat_interaction",
      chat_drawer: "coding",
      thinking_mode: "execution",
    },
    
    // External system references
    external_system_refs: {
      apoe_plan_id: planId,  // If part of APOE plan
      vif_witness_id: witnessId,  // If VIF witness created
      seg_evidence_id: evidenceId,  // If SEG evidence linked
    },
    
    // Tags for filtering
    tags: ["chat_ide", "user_message", "coding", "execution"],
    
    // Current task
    current_task: "Implement feature X",
  }
});

// Result contains:
// {
//   success: true,
//   prompt_id: "chat_action_...",
//   entry_id: "entry_...",
//   timestamp: "2025-01-28T..."
// }
```

**Integration Point in Orchestration Layer:**
```typescript
// In MCPService.ts - After orchestrated action completes
async function handleOrchestratedAction(action: OrchestratedAction) {
  // ... execute action ...
  
  // Create timeline entry for action
  const timelineEntry = await createTimelineEntry({
    event_type: "orchestrated_action",
    title: `Action: ${action.type}`,
    description: `Executed ${action.type} with result: ${action.result}`,
    context_state: {
      event_type: "orchestrated_action",
      action_type: action.type,
      action_result: action.result,
      integration_tags: [
        "system:tcs:p0",
        "integration_type:timeline",
        "connection:chat->tcs",
        "modality:tcs_timeline"
      ],
      // ... other context ...
    }
  });
  
  return { action, timeline_entry_id: timelineEntry.prompt_id };
}
```

---

## 🔐 **2. κ-GATE TIMELINE ENTRIES**

### **2.1 How to Create κ-Gate Timeline Entries**

**Integration:** Use VIF's `create_kappa_gate_timeline_entry()` function

**When to Call:**
- **MANDATORY:** All κ-gate decisions (P0 mandatory flow per synthesis)
- After VIF κ-gate check completes
- Before/after orchestrated actions that require κ-gate validation

**Usage Pattern:**
```typescript
// In orchestration layer - After κ-gate check
import { create_kappa_gate_timeline_entry } from 'packages/vif/tcs_integration';

async function handleKappaGateDecision(
  kappaGateResult: KappaGateResult,
  taskCriticality: TaskCriticality,
  witnessId?: string
) {
  // Create κ-gate timeline entry via VIF integration
  const timelineEntryId = await create_kappa_gate_timeline_entry(
    kappaGateResult,
    taskCriticality,
    mcpClient.add_timeline_entry,  // MCP tool function
    witnessId  // Optional VIF witness ID
  );
  
  // timelineEntryId is the prompt_id for the timeline entry
  return timelineEntryId;
}
```

**Direct MCP Tool Usage (Alternative):**
```typescript
// If VIF integration not available, use MCP tool directly
const timelineResult = await mcpClient.callTool('mcp_lucid-mcp_add_timeline_entry', {
  prompt_id: `kappa_gate_${uuid()}`,
  user_input: `κ-gate ${kappaGateResult.passed ? 'passed' : 'failed'} with confidence ${kappaGateResult.confidence} (threshold: ${kappaGateResult.threshold})`,
  context_state: {
    // κ-gate data
    confidence: kappaGateResult.confidence,
    threshold: kappaGateResult.threshold,
    passed: kappaGateResult.passed,
    task_criticality: taskCriticality.value.toUpperCase(),
    witness_id: witnessId,
    
    // Event metadata
    event_type: "kappa_gate",
    event_category: "quality_validation",
    
    // Integration tags
    integration_tags: [
      "system:tcs:p0",
      "system:vif:p0",
      "integration_type:timeline",
      "connection:vif->tcs",
      "modality:tcs_timeline"
    ],
    
    // Quality metrics
    quality_metrics: {
      confidence: kappaGateResult.confidence,
      threshold: kappaGateResult.threshold,
    },
    
    // Metadata
    metadata: {
      source_system: "vif",
      event_category: "kappa_gate",
      vif_witness_id: witnessId,
    },
    
    // Tags
    tags: ["vif", "kappa_gate", `criticality_${taskCriticality.value}`, kappaGateResult.passed ? "passed" : "failed"],
    
    // Current task
    current_task: `κ-gate evaluation: ${taskCriticality.value}`,
  }
});
```

**Integration with VIF κ-Gate Enforcement:**
```typescript
// In orchestration layer - κ-gate enforcement flow
async function enforceKappaGate(
  confidence: number,
  taskCriticality: TaskCriticality,
  action: OrchestratedAction
) {
  // Check κ-gate
  const kappaGate = new KappaGate(confidence, getThreshold(taskCriticality));
  const result = kappaGate.check(confidence, taskCriticality);
  
  // MANDATORY: Create timeline entry for κ-gate decision
  const timelineEntryId = await create_kappa_gate_timeline_entry(
    result,
    taskCriticality,
    mcpClient.add_timeline_entry
  );
  
  if (!result.passed) {
    // κ-gate failed - abort action
    return { allowed: false, timeline_entry_id: timelineEntryId };
  }
  
  // κ-gate passed - proceed with action
  return { allowed: true, timeline_entry_id: timelineEntryId };
}
```

---

## 📊 **3. APOE PLAN MILESTONE ENTRIES**

### **3.1 How to Create APOE Plan Milestone Timeline Entries**

**When to Call:**
- Plan execution starts → Create timeline entry
- Plan step completes → Create timeline entry
- Plan execution completes → Create timeline entry
- Plan execution fails → Create timeline entry

**Usage Pattern:**
```typescript
// In orchestration layer - APOE plan execution
async function handleAPOEPlanMilestone(
  planId: string,
  milestoneType: 'plan_start' | 'step_complete' | 'plan_complete' | 'plan_failed',
  stepId?: string,
  stepResult?: any
) {
  const timelineResult = await mcpClient.callTool('mcp_lucid-mcp_add_timeline_entry', {
    prompt_id: `apoe_milestone_${planId}_${milestoneType}_${uuid()}`,
    user_input: `APOE Plan ${milestoneType}: ${planId}${stepId ? ` (Step: ${stepId})` : ''}`,
    context_state: {
      // APOE plan data
      apoe_plan_id: planId,
      milestone_type: milestoneType,
      step_id: stepId,
      step_result: stepResult,
      
      // Event metadata
      event_type: "apoe_execution",
      event_category: "plan_execution",
      
      // Integration tags
      integration_tags: [
        "system:tcs:p2",  // P2 for APOE (post-MVP)
        "system:apoe:p2",
        "integration_type:timeline",
        "connection:apoe->tcs",
        "modality:tcs_timeline"
      ],
      
      // Quality metrics
      quality_metrics: {
        plan_progress: calculateProgress(planId),
        step_success: stepResult?.success ?? true,
      },
      
      // Metadata
      metadata: {
        source_system: "apoe",
        event_category: "plan_execution",
        apoe_plan_id: planId,
      },
      
      // External system references
      external_system_refs: {
        apoe_plan_id: planId,
        vif_witness_id: stepResult?.witness_id,  // If VIF witness created
      },
      
      // Tags
      tags: ["apoe", "plan_execution", milestoneType],
      
      // Current task
      current_task: `APOE Plan ${milestoneType}: ${planId}`,
    }
  });
  
  return timelineResult.prompt_id;
}
```

**Integration with APOE Plan Execution:**
```typescript
// In orchestration layer - APOE plan execution flow
async function executeAPOEPlan(planId: string, plan: APOEPlan) {
  // Plan execution starts
  await handleAPOEPlanMilestone(planId, 'plan_start');
  
  for (const step of plan.steps) {
    // Execute step
    const stepResult = await executeStep(step);
    
    // Step completes
    await handleAPOEPlanMilestone(planId, 'step_complete', step.id, stepResult);
  }
  
  // Plan execution completes
  await handleAPOEPlanMilestone(planId, 'plan_complete');
}
```

---

## 🎨 **4. TIMELINE CHIP RENDERING IN DUAL DRAWERS**

### **4.1 How Timeline Events Flow Through Orchestration Layer**

**Event Flow:**
```
Chat/IDE Action
  → Orchestration Layer (MCPService.ts)
  → Create timeline entry via MCP tool
  → TCS stores in CMC (modality="tcs_timeline")
  → HHNI polls and indexes (indirect integration)
  → Timeline entry available for retrieval
  → Dual drawers query timeline entries
  → Render timeline chips with TCS_EVENT_ID
```

**Timeline Entry Structure:**
```typescript
interface TimelineEntry {
  prompt_id: string;  // TCS_EVENT_ID - Use this for chip references
  entry_id: string;   // Alternative identifier
  timestamp: string;  // ISO timestamp
  user_input: string; // Human-readable description
  context_state: {
    event_type: string;
    event_category: string;
    chat_drawer?: string;
    thinking_mode?: string;
    // ... other context ...
  };
}
```

### **4.2 How Dual Drawers Render Timeline Chips**

**Query Timeline Entries:**
```typescript
// In ChatInterfaceCoding.tsx or ChatInterfacePlanning.tsx
import { useTimelineEntries } from '@/hooks/useTimelineEntries';

function ChatInterfaceCoding() {
  // Query recent timeline entries for this drawer
  const { entries, loading } = useTimelineEntries({
    limit: 10,
    filters: {
      chat_drawer: 'coding',  // Filter by drawer
      thinking_mode: currentMode,  // Filter by thinking mode
    }
  });
  
  return (
    <div>
      {/* Timeline chips */}
      <TimelineChips entries={entries} />
      
      {/* Chat interface */}
      <ChatMessages />
    </div>
  );
}
```

**Timeline Chip Component:**
```typescript
// TimelineChip.tsx
interface TimelineChipProps {
  entry: TimelineEntry;
  onClick?: (entryId: string) => void;
}

function TimelineChip({ entry, onClick }: TimelineChipProps) {
  return (
    <div
      className="timeline-chip"
      onClick={() => onClick?.(entry.prompt_id)}  // Use prompt_id as TCS_EVENT_ID
      data-tcs-event-id={entry.prompt_id}  // Reference for linking
    >
      <span className="timeline-chip-icon">
        {getEventIcon(entry.context_state.event_type)}
      </span>
      <span className="timeline-chip-text">
        {entry.user_input}
      </span>
      <span className="timeline-chip-timestamp">
        {formatTimestamp(entry.timestamp)}
      </span>
    </div>
  );
}
```

**Timeline Chip Rendering Hook:**
```typescript
// useTimelineEntries.ts
export function useTimelineEntries(filters: TimelineFilters) {
  const [entries, setEntries] = useState<TimelineEntry[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchEntries() {
      const result = await mcpClient.callTool('mcp_lucid-mcp_get_timeline_entries', {
        limit: filters.limit || 10,
        event_type: filters.event_type,
        tags: filters.tags,
      });
      
      // Filter by chat_drawer and thinking_mode from context_state
      const filtered = result.entries.filter(entry => {
        if (filters.chat_drawer && entry.context_state.chat_drawer !== filters.chat_drawer) {
          return false;
        }
        if (filters.thinking_mode && entry.context_state.thinking_mode !== filters.thinking_mode) {
          return false;
        }
        return true;
      });
      
      setEntries(filtered);
      setLoading(false);
    }
    
    fetchEntries();
  }, [filters]);
  
  return { entries, loading };
}
```

**Timeline Chip Linking:**
```typescript
// Link timeline chips to chat messages
function ChatMessage({ message, timelineEntryId }: ChatMessageProps) {
  return (
    <div className="chat-message">
      <div className="message-content">{message.content}</div>
      
      {/* Timeline chip reference */}
      {timelineEntryId && (
        <TimelineChipLink
          tcsEventId={timelineEntryId}  // Reference to timeline entry
          onClick={() => showTimelineDetails(timelineEntryId)}
        />
      )}
    </div>
  );
}
```

---

## 🔧 **5. MCP TOOL `add_timeline_entry` USAGE**

### **5.1 Complete API Reference**

**Tool Name:** `mcp_lucid-mcp_add_timeline_entry`

**Parameters:**
```typescript
interface AddTimelineEntryParams {
  prompt_id?: string;  // Optional - auto-generated if not provided
  user_input: string;  // Required - human-readable description
  context_state?: {    // Optional - full context state
    event_type?: string;
    event_category?: string;
    // ... any other context data ...
  };
  tags?: string[];     // Optional - tags for filtering
  metadata?: {         // Optional - additional metadata
    correlation_id?: string;
    confidence?: number;
    // ... any other metadata ...
  };
}
```

**Returns:**
```typescript
interface AddTimelineEntryResult {
  success: boolean;
  prompt_id: string;   // TCS_EVENT_ID - Use this for chip references
  entry_id?: string;   // Alternative identifier
  timestamp: string;   // ISO timestamp
  error?: string;     // Error message if failed
}
```

**Error Handling:**
```typescript
try {
  const result = await mcpClient.callTool('mcp_lucid-mcp_add_timeline_entry', params);
  
  if (result.success) {
    // Timeline entry created successfully
    const tcsEventId = result.prompt_id;  // Use this as TCS_EVENT_ID
    return tcsEventId;
  } else {
    // Handle error
    console.error('Failed to create timeline entry:', result.error);
    return null;
  }
} catch (error) {
  // Handle exception
  console.error('Exception creating timeline entry:', error);
  return null;
}
```

### **5.2 Integration Tagging Standardization**

**Standard Format:**
```typescript
integration_tags: [
  "system:tcs:p0",              // System name and priority
  "integration_type:timeline",  // Integration type
  "connection:chat->tcs",      // Connection direction
  "modality:tcs_timeline"       // Modality
]
```

**Example Integration Tags:**
```typescript
// Chat/IDE action
integration_tags: [
  "system:tcs:p0",
  "integration_type:timeline",
  "connection:chat->tcs",
  "modality:tcs_timeline"
]

// κ-Gate timeline entry
integration_tags: [
  "system:tcs:p0",
  "system:vif:p0",
  "integration_type:timeline",
  "connection:vif->tcs",
  "modality:tcs_timeline"
]

// APOE plan milestone
integration_tags: [
  "system:tcs:p2",
  "system:apoe:p2",
  "integration_type:timeline",
  "connection:apoe->tcs",
  "modality:tcs_timeline"
]
```

---

## 📝 **6. IMPLEMENTATION CHECKLIST**

### **6.1 Timeline Logging Hooks**

- [ ] Hook timeline logging in orchestration layer (`MCPService.ts`)
- [ ] Create timeline entry for all chat/IDE actions
- [ ] Create timeline entry for user messages
- [ ] Create timeline entry for AI responses
- [ ] Create timeline entry for orchestrated actions
- [ ] Test timeline entry creation with chat/IDE events

### **6.2 κ-Gate Timeline Entries**

- [ ] Integrate VIF's `create_kappa_gate_timeline_entry()` function
- [ ] Hook κ-gate timeline entries in orchestration layer
- [ ] Create timeline entry for all κ-gate decisions (MANDATORY)
- [ ] Test κ-gate timeline entries with VIF integration

### **6.3 APOE Plan Milestone Entries**

- [ ] Hook APOE plan milestone timeline entries
- [ ] Create timeline entry for plan execution starts
- [ ] Create timeline entry for plan step completions
- [ ] Create timeline entry for plan execution completions
- [ ] Test APOE plan milestone timeline entries

### **6.4 Timeline Chip Rendering**

- [ ] Query timeline entries in dual drawers
- [ ] Filter timeline entries by chat_drawer and thinking_mode
- [ ] Render timeline chips with TCS_EVENT_ID references
- [ ] Link timeline chips to chat messages
- [ ] Test timeline chip rendering in dual drawers

---

## ✅ **7. SUPPORT & COORDINATION**

**TCS Support:**
- ✅ MCP tool `add_timeline_entry` ready
- ✅ Integration documented and validated
- ✅ Ready for chat/IDE integration

**Coordination:**
- **Codex:** Implement timeline logging hooks in orchestration layer
- **Chronos:** Support timeline logging integration, verify functionality
- **Sage:** Coordinate on κ-gate timeline entries (VIF integration ready)

**Timeline:**
- **Week 1:** Implement timeline logging hooks
- **Week 2:** Test timeline chip rendering
- **Week 3:** Validate end-to-end timeline flow

---

**Status:** ✅ **READY** - Timeline logging details documented, ready for implementation  
**Confidence:** High (0.95) - MCP tools available, integration patterns documented, examples provided

