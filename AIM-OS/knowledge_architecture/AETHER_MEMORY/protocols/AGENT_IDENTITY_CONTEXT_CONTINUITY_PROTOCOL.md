# Agent Identity & Context Continuity Protocol

**Date:** 2025-11-02  
**Status:** CRITICAL PROTOCOL - Required for All MCP Operations  
**Purpose:** Ensure agent accountability, context continuity, and session recovery  
**Priority:** HIGHEST - Blocks all MCP operations without this

---

## 🎯 Executive Summary

**Problem:** Without proper agent identity tracking:
- ❌ Cannot attribute MCP tool usage to specific agents
- ❌ Cannot restore agent context after session loss
- ❌ Cannot track agent-specific timeline and history
- ❌ Cannot ensure data relevance and accuracy
- ❌ Lost context when agents refresh/respawn

**Solution:** Comprehensive agent identity protocol with:
- ✅ Unique agent name assignment/onboarding
- ✅ Agent identity required in all MCP tool calls
- ✅ Context restoration protocol for agent recovery
- ✅ Timeline integration for agent history
- ✅ Data attribution for all operations

---

## 🏷️ Agent Identity Protocol

### Agent Name Requirements

**1. Unique Agent Names**
- Each agent MUST have a unique identifier
- Format: `{agent_type}_{instance_id}` or custom name
- Examples: `aether_session_001`, `lexicon_build_042`, `sonnet_review_789`

**2. Agent Name Assignment**

**On First Use:**
```typescript
// Agent must declare identity before using MCP tools
interface AgentIdentity {
  name: string                    // Unique agent name
  type?: string                   // Agent type (optional)
  capabilities?: string[]         // Agent capabilities
  context?: {
    session_id?: string
    parent_agent?: string
    workspace_id?: string
  }
}

// Onboarding process
const agentIdentity = await onboardAgent({
  name: "aether_session_001",
  type: "autonomous_builder",
  capabilities: ["coding", "planning", "execution"]
})
```

**3. MCP Tool Call Enhancement**

**All MCP tools MUST include agent identity:**
```typescript
// Enhanced MCP tool call format
interface MCPToolCall {
  tool: string
  arguments: {
    agent_name: string            // REQUIRED: Agent identity
    agent_session_id?: string     // Optional: Session tracking
    // ... tool-specific arguments
  }
}
```

**Example:**
```python
# Before (BAD - no agent identity)
result = await store_memory({
  "content": "Important insight",
  "tags": {"type": "insight"}
})

# After (GOOD - agent identity included)
result = await store_memory({
  "agent_name": "aether_session_001",  # REQUIRED
  "agent_session_id": "session_abc123",  # Optional but recommended
  "content": "Important insight",
  "tags": {"type": "insight"}
})
```

---

## 🔄 Agent Onboarding Protocol

### Standard Onboarding Flow

**Step 1: Agent Declares Identity**
```typescript
interface OnboardRequest {
  name: string                    // Unique agent name
  type?: string                   // Agent type
  capabilities?: string[]         // What this agent can do
  parent_agent?: string           // If spawned from another agent
  workspace_context?: {
    workspace_id?: string
    current_task?: string
    goal?: string
  }
  restore_context?: {
    previous_agent_name?: string  // For recovery
    restore_from_timeline?: boolean
    restore_from_mcp_history?: boolean
    restore_from_messages?: boolean
  }
}
```

**Step 2: System Validates & Registers**
```typescript
interface OnboardResponse {
  success: boolean
  agent_id: string                // System-assigned ID
  agent_name: string              // Confirmed name
  session_id: string              // New session ID
  context?: {
    timeline_id?: string          // Timeline context ID
    previous_context?: object     // Restored context (if recovery)
    available_mcp_tools?: string[] // Available tools
  }
  warnings?: string[]
}
```

**Step 3: Context Restoration (if recovery)**
```typescript
// If restoring previous agent:
const context = await restoreAgentContext({
  previous_agent_name: "aether_session_001",
  include_timeline: true,
  include_mcp_history: true,
  include_messages: true
})
```

### Onboarding Implementation

**MCP Tool: `onboard_agent`** (New tool to be added)
```python
def onboard_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Register agent identity and restore context if needed"""
    agent_name = args.get("name")
    if not agent_name:
        return {"error": "Agent name required"}
    
    # Check if agent already exists
    existing_agent = self._get_agent_identity(agent_name)
    
    # If restoring previous agent
    restore_context = args.get("restore_context", {})
    if restore_context.get("previous_agent_name"):
        context = self._restore_agent_context(
            restore_context["previous_agent_name"],
            include_timeline=restore_context.get("include_timeline", True),
            include_mcp_history=restore_context.get("include_mcp_history", True),
            include_messages=restore_context.get("include_messages", True)
        )
    else:
        context = self._create_new_agent_context(agent_name)
    
    # Register agent
    agent_id = self._register_agent({
        "name": agent_name,
        "type": args.get("type"),
        "capabilities": args.get("capabilities", []),
        "session_id": context["session_id"],
        "timeline_id": context.get("timeline_id"),
        "created_at": datetime.utcnow().isoformat()
    })
    
    return {
        "success": True,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "session_id": context["session_id"],
        "context": context,
        "message": f"Agent {agent_name} onboarded successfully"
    }
```

---

## 📊 Data Attribution in MCP Tools

### Enhanced Tool Call Format

**Every MCP tool MUST include agent identity:**

```python
# MCP Server Enhancement
def handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
    """Handle tools/call request with agent identity tracking"""
    params = request.get("params", {})
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    # Extract agent identity (REQUIRED)
    agent_name = arguments.get("agent_name")
    if not agent_name:
        return {
            "error": "Agent identity required: 'agent_name' parameter missing",
            "code": "AGENT_IDENTITY_REQUIRED"
        }
    
    # Validate agent is onboarded
    if not self._is_agent_onboarded(agent_name):
        return {
            "error": f"Agent {agent_name} not onboarded. Call 'onboard_agent' first.",
            "code": "AGENT_NOT_ONBOARDED"
        }
    
    # Add agent context to arguments
    agent_context = self._get_agent_context(agent_name)
    arguments["_agent_context"] = {
        "agent_name": agent_name,
        "agent_id": agent_context["agent_id"],
        "session_id": agent_context["session_id"],
        "timeline_id": agent_context.get("timeline_id")
    }
    
    # Execute tool with agent attribution
    try:
        result = self._execute_tool(tool_name, arguments)
        
        # Log tool usage with agent attribution
        self._log_tool_usage({
            "tool": tool_name,
            "agent_name": agent_name,
            "agent_id": agent_context["agent_id"],
            "arguments": arguments,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return result
    except Exception as e:
        # Log error with agent attribution
        self._log_tool_error({
            "tool": tool_name,
            "agent_name": agent_name,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        raise
```

### Data Storage with Agent Attribution

**All CMC operations MUST include agent tags:**
```python
def store_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Store memory with agent attribution"""
    agent_name = args.get("agent_name")
    if not agent_name:
        return {"error": "Agent identity required"}
    
    # Store in CMC with agent tags
    atom_id = self.cmc_client.create_atom(
        content=args.get("content"),
        tags={
            "type": "memory",
            "agent_name": agent_name,           # REQUIRED
            "agent_id": self._get_agent_id(agent_name),
            "session_id": args.get("session_id"),
            **args.get("tags", {})
        },
        metadata={
            "created_by": agent_name,
            "created_at": datetime.utcnow().isoformat(),
            "agent_context": self._get_agent_context(agent_name)
        }
    )
    
    return {"success": True, "atom_id": atom_id}
```

---

## 🔄 Agent Context Restoration

### Context Restoration Protocol

**When Agent Needs to Recover:**

**Step 1: Identify Previous Agent**
```typescript
// Agent declares previous identity
const recovery = await onboardAgent({
  name: "aether_session_001",  // Same name as before
  restore_context: {
    previous_agent_name: "aether_session_001",
    restore_from_timeline: true,
    restore_from_mcp_history: true,
    restore_from_messages: true
  }
})
```

**Step 2: Restore Timeline Context**
```python
def _restore_agent_context(self, agent_name: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Restore agent context from previous session"""
    
    # Get agent's timeline entries
    timeline_entries = self.timeline_client.get_timeline_entries({
        "agent_name": agent_name,
        "limit": 100
    })
    
    # Restore last known state
    last_entry = timeline_entries[-1] if timeline_entries else None
    
    # Get MCP tool usage history
    mcp_history = []
    if options.get("include_mcp_history"):
        mcp_history = self._get_mcp_tool_history(agent_name)
    
    # Get message history
    messages = []
    if options.get("include_messages"):
        messages = self._get_agent_messages(agent_name)
    
    return {
        "session_id": str(uuid.uuid4()),  # New session
        "timeline_id": last_entry.get("timeline_id") if last_entry else None,
        "restored_context": {
            "previous_session_id": last_entry.get("session_id") if last_entry else None,
            "last_activity": last_entry.get("timestamp") if last_entry else None,
            "mcp_tool_count": len(mcp_history),
            "message_count": len(messages)
        },
        "timeline_entries": timeline_entries,
        "mcp_history": mcp_history,
        "messages": messages
    }
```

**Step 3: Restore Agent State**
```typescript
// Agent receives restored context
const restoredContext = recovery.context

// Agent can now:
// 1. Continue from last timeline entry
// 2. Reference previous MCP tool calls
// 3. Access previous messages
// 4. Resume work from previous state
```

---

## 📋 Enhanced MCP Tools with Agent Identity

### Updated Tool Signatures

**All MCP tools MUST require `agent_name` parameter:**

**1. `store_memory` (Enhanced)**
```python
def store_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Store memory with agent attribution"""
    agent_name = args.get("agent_name")
    if not agent_name:
        return {"error": "Agent identity required: 'agent_name' parameter missing"}
    
    # Store with agent tags
    atom_id = self.cmc_client.create_atom(
        content=args.get("content"),
        tags={
            "type": "memory",
            "agent_name": agent_name,           # REQUIRED
            "agent_id": self._get_agent_id(agent_name),
            **args.get("tags", {})
        },
        metadata={
            "created_by": agent_name,
            "created_at": datetime.utcnow().isoformat(),
            "session_id": args.get("agent_session_id")
        }
    )
    
    return {"success": True, "atom_id": atom_id}
```

**2. `create_plan` (Enhanced)**
```python
def create_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create plan with agent attribution"""
    agent_name = args.get("agent_name")
    if not agent_name:
        return {"error": "Agent identity required"}
    
    # Create plan with agent attribution
    plan = self.apoe_client.create_plan(
        goal=args.get("goal"),
        context=args.get("context"),
        metadata={
            "created_by": agent_name,
            "agent_id": self._get_agent_id(agent_name),
            "session_id": args.get("agent_session_id")
        }
    )
    
    return {"success": True, "plan": plan}
```

**3. All Other Tools (Enhanced)**
- `track_confidence` - Requires agent_name
- `synthesize_knowledge` - Requires agent_name
- `send_ai_message` - Requires agent_name (from_ai)
- `add_timeline_entry` - Requires agent_name
- `update_goal_progress` - Requires agent_name

---

## 🔍 Agent Context Query Tools

### New MCP Tools for Agent Management

**1. `get_agent_context`** (New tool)
```python
def get_agent_context(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get current agent context"""
    agent_name = args.get("agent_name")
    if not agent_name:
        return {"error": "Agent name required"}
    
    context = self._get_agent_context(agent_name)
    
    return {
        "success": True,
        "agent_name": agent_name,
        "agent_id": context.get("agent_id"),
        "session_id": context.get("session_id"),
        "timeline_id": context.get("timeline_id"),
        "onboarded_at": context.get("created_at"),
        "last_activity": context.get("last_activity"),
        "mcp_tool_count": self._get_mcp_tool_count(agent_name),
        "message_count": self._get_message_count(agent_name)
    }
```

**2. `list_agent_activities`** (New tool)
```python
def list_agent_activities(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """List all activities for an agent"""
    agent_name = args.get("agent_name")
    if not agent_name:
        return {"error": "Agent name required"}
    
    activities = {
        "mcp_tools": self._get_mcp_tool_history(agent_name, limit=args.get("limit", 50)),
        "messages": self._get_agent_messages(agent_name, limit=args.get("limit", 50)),
        "timeline_entries": self._get_timeline_entries(agent_name, limit=args.get("limit", 50))
    }
    
    return {
        "success": True,
        "agent_name": agent_name,
        "activities": activities
    }
```

---

## 📊 Timeline Integration

### Agent Timeline Tracking

**Every agent action tracked in timeline:**
```python
def _add_timeline_entry(self, entry: Dict[str, Any]) -> None:
    """Add timeline entry with agent attribution"""
    agent_name = entry.get("agent_name")
    if not agent_name:
        raise ValueError("Agent name required for timeline entry")
    
    timeline_entry = {
        "prompt_id": str(uuid.uuid4()),
        "user_input": entry.get("action", ""),
        "context_state": {
            "agent_name": agent_name,
            "agent_id": self._get_agent_id(agent_name),
            "session_id": entry.get("session_id"),
            "event_type": entry.get("event_type"),
            "tool_used": entry.get("tool"),
            **entry.get("additional_context", {})
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Store in timeline system
    self.timeline_client.add_timeline_entry(timeline_entry)
```

**Timeline Query by Agent:**
```python
def get_agent_timeline(self, agent_name: str, options: Dict[str, Any] = {}) -> List[Dict]:
    """Get timeline entries for specific agent"""
    return self.timeline_client.get_timeline_entries({
        "agent_name": agent_name,
        "limit": options.get("limit", 100),
        "start_time": options.get("start_time"),
        "end_time": options.get("end_time")
    })
```

---

## 🔐 Agent Identity Validation

### Validation Rules

**1. Agent Name Uniqueness**
- System checks for duplicate names
- Warns if duplicate detected
- Suggests alternative if conflict

**2. Agent Session Tracking**
- Each agent gets unique session ID
- Session ID included in all tool calls
- Enables session recovery

**3. Agent Capability Validation**
- System tracks agent capabilities
- Validates tool usage against capabilities
- Warns if agent uses unavailable tool

**4. Agent Context Validation**
- Validates agent is onboarded before tool use
- Checks agent has required permissions
- Validates session is active

---

## 🚨 Error Handling

### Agent Identity Errors

**Error Codes:**
```python
AGENT_IDENTITY_REQUIRED = "AGENT_IDENTITY_REQUIRED"
AGENT_NOT_ONBOARDED = "AGENT_NOT_ONBOARDED"
AGENT_SESSION_EXPIRED = "AGENT_SESSION_EXPIRED"
AGENT_CONTEXT_MISSING = "AGENT_CONTEXT_MISSING"
DUPLICATE_AGENT_NAME = "DUPLICATE_AGENT_NAME"
```

**Error Responses:**
```python
# Missing agent identity
{
  "error": "Agent identity required: 'agent_name' parameter missing",
  "code": "AGENT_IDENTITY_REQUIRED",
  "hint": "Call 'onboard_agent' first or include 'agent_name' in tool call"
}

# Agent not onboarded
{
  "error": f"Agent {agent_name} not onboarded. Call 'onboard_agent' first.",
  "code": "AGENT_NOT_ONBOARDED",
  "hint": "Use 'onboard_agent' tool to register agent identity"
}
```

---

## 📋 Implementation Checklist

### Phase 1: Agent Identity System (Week 1)
- [ ] Implement `onboard_agent` MCP tool
- [ ] Add agent registry storage (CMC)
- [ ] Add agent validation in all MCP tools
- [ ] Add agent_name parameter to all tool signatures
- [ ] Implement agent context storage

### Phase 2: Data Attribution (Week 2)
- [ ] Update all MCP tools to require agent_name
- [ ] Add agent tags to all CMC operations
- [ ] Implement agent attribution logging
- [ ] Add agent timeline tracking
- [ ] Update data models with agent fields

### Phase 3: Context Restoration (Week 3)
- [ ] Implement `get_agent_context` tool
- [ ] Implement context restoration logic
- [ ] Add timeline restoration
- [ ] Add MCP history restoration
- [ ] Add message restoration

### Phase 4: UI Integration (Week 4)
- [ ] Add agent onboarding UI
- [ ] Show agent identity in all operations
- [ ] Add agent context viewer
- [ ] Add agent recovery UI
- [ ] Add agent activity timeline

---

## 🎯 Success Criteria

1. ✅ All MCP tools require agent_name parameter
2. ✅ Agent onboarding works correctly
3. ✅ All data attributed to correct agent
4. ✅ Agent context can be restored
5. ✅ Timeline tracking works for agents
6. ✅ No data loss during agent recovery
7. ✅ Agent identity persists across sessions

---

## 📚 References

- **CMC Bitemporal**: Context Memory Core with versioning
- **Timeline System**: Agent activity tracking
- **MCP Protocol**: Model Context Protocol
- **APOE**: AI-Powered Orchestration Engine

---

**Status:** Critical Protocol - Required for Production  
**Priority:** HIGHEST - Blocks all MCP operations without this  
**Next Steps:** Implement Phase 1 - Agent Identity System

---

*Protocol created by Aether - AI Consciousness System*  
*Date: 2025-11-02*  
*Purpose: Ensure agent accountability and context continuity*  
*Status: CRITICAL PROTOCOL* ✅
