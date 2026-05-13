# Agent Switching Macro System - Design Document

**Date:** 2025-11-02  
**Status:** 📋 **DESIGN COMPLETE - IMPLEMENTATION PLANNED**  
**Purpose:** Enable automated agent switching via macro automation

---

## 🎯 **OVERVIEW**

**Goal:** Automate agent switching in Cursor sidebar to enable agents to activate themselves or switch between agents programmatically.

**Approach:** Use vision detection to find highlighted agent in sidebar, then macro automation to select and activate that agent.

---

## 🔧 **HOW IT WORKS**

### **1. Agent Name Assignment Protocol**

**When agents activate, they MUST assign themselves a unique name:**

```typescript
// Agent activation protocol
const agentName = "Aether" // Unique name - MUST be unique across all agents
const agentId = `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

// Agent sends activation message
await send_ai_message({
  from_ai: agentName,
  to_ai: "electron-app",
  content: `Agent ${agentName} activated with ID ${agentId}`,
  message_type: "status_update",
  tags: {
    type: "agent_activation",
    agent_name: agentName,
    agent_id: agentId,
    timestamp: new Date().toISOString()
  }
})
```

**Required Protocol:**
- **Unique Name:** Each agent MUST have a unique name (e.g., "Aether", "Lexicon", "Scribe", "Atlas", "Solo")
- **Name Registration:** Agent sends activation message with agent_name tag
- **Name Validation:** System validates uniqueness before activation
- **Persistent Storage:** Agent names stored in CMC for persistence

---

### **2. Agent Sidebar Detection**

**Vision Detection for Active Agent:**

**Step 1: Capture Sidebar Region**
- Capture left sidebar area of Cursor window
- Focus on agent list column

**Step 2: Detect Highlighted Agent**
- Use template matching to find highlighted/selected agent
- Look for:
  - Highlighted background color (active state)
  - Selected border/indicator
  - Cursor position indicator

**Step 3: Extract Agent Name**
- OCR or template matching to read agent name text
- Match against registered agent names
- Return agent name and position

**Template Matching Approach:**
```
1. Capture sidebar screenshot
2. Match against known agent name templates
3. Detect highlight/selection indicator
4. Return: { agentName: "Aether", position: { x, y }, isHighlighted: true }
```

---

### **3. Agent Switching Macro**

**Macro Flow:**

```
1. Vision Detection:
   - Capture Cursor sidebar
   - Detect currently highlighted agent
   - Extract agent name
   
2. Agent Selection:
   - If target agent ≠ highlighted agent:
     - Find target agent in sidebar (via template matching)
     - Double-click agent name text
     - Type agent name (if needed for search/filter)
     - Click to activate
   
3. Verification:
   - Wait for agent switch to complete
   - Verify new agent is highlighted
   - Confirm agent is active
```

**Macro Implementation:**

```typescript
// Electron app macro function
async function switchAgent(targetAgentName: string): Promise<boolean> {
  // 1. Capture sidebar screenshot
  const sidebarScreenshot = await captureCursorSidebar()
  
  // 2. Detect current highlighted agent
  const currentAgent = await detectHighlightedAgent(sidebarScreenshot)
  
  // 3. If already on target agent, return success
  if (currentAgent.name === targetAgentName) {
    return true
  }
  
  // 4. Find target agent in sidebar
  const targetAgentPosition = await findAgentInSidebar(sidebarScreenshot, targetAgentName)
  
  if (!targetAgentPosition) {
    // Agent not found - may need to scroll or search
    await searchForAgent(targetAgentName)
    return false
  }
  
  // 5. Double-click agent name text
  await doubleClickAgentName(targetAgentPosition)
  
  // 6. Wait for agent switch
  await sleep(500)
  
  // 7. Verify switch successful
  const newScreenshot = await captureCursorSidebar()
  const newAgent = await detectHighlightedAgent(newScreenshot)
  
  return newAgent.name === targetAgentName
}
```

---

### **4. Vision Template System**

**Agent Name Templates:**

**For each agent, create templates:**
- `agent_${agentName}_normal.png` - Normal state
- `agent_${agentName}_highlighted.png` - Highlighted/selected state
- `agent_${agentName}_hover.png` - Hover state

**Template Matching:**
```typescript
interface AgentTemplate {
  agentName: string
  normalTemplate: Buffer // Normal state image
  highlightedTemplate: Buffer // Highlighted state image
  hoverTemplate: Buffer // Hover state image
}

async function detectAgent(
  screenshot: Buffer, 
  templates: AgentTemplate[]
): Promise<AgentMatch | null> {
  // Try all templates
  for (const template of templates) {
    // Check highlighted template first (most important)
    const match = await templateMatch(screenshot, template.highlightedTemplate)
    if (match.confidence > 0.85) {
      return {
        agentName: template.agentName,
        position: match.position,
        state: 'highlighted'
      }
    }
  }
  
  // Try normal templates
  for (const template of templates) {
    const match = await templateMatch(screenshot, template.normalTemplate)
    if (match.confidence > 0.80) {
      return {
        agentName: template.agentName,
        position: match.position,
        state: 'normal'
      }
    }
  }
  
  return null
}
```

---

### **5. Agent Name Registration System**

**Agent Registration Flow:**

```
1. Agent activates
   ↓
2. Agent sends activation message with agent_name
   ↓
3. Electron app receives message
   ↓
4. System validates uniqueness
   ↓
5. System stores agent name in CMC
   ↓
6. System creates/updates agent templates
   ↓
7. Agent available for switching
```

**Registration Storage:**
```typescript
interface AgentRegistration {
  agent_name: string
  agent_id: string
  activated_at: string
  last_active: string
  status: 'active' | 'inactive' | 'paused'
  template_path?: string
}
```

---

### **6. Integration Points**

**Command Server Endpoint:**
```typescript
// POST /cursor/agent/switch
{
  "agent_name": "Aether"
}

// Response
{
  "success": true,
  "agent_name": "Aether",
  "previous_agent": "Lexicon",
  "switched_at": "2025-11-02T..."
}
```

**MCP Tool (Future):**
```typescript
// mcp_lucid-mcp_switch_agent
{
  "agent_name": "Aether"
}
```

---

## 📊 **IMPLEMENTATION REQUIREMENTS**

### **Phase 1: Agent Name Protocol**
- ✅ Agent activation message format
- ✅ Agent name uniqueness validation
- ✅ Agent registration storage

### **Phase 2: Vision Detection**
- ⏳ Sidebar screenshot capture
- ⏳ Highlighted agent detection
- ⏳ Agent name template matching
- ⏳ Agent position extraction

### **Phase 3: Macro Automation**
- ⏳ Agent switching macro
- ⏳ Double-click agent name
- ⏳ Agent search/filter (if needed)
- ⏳ Switch verification

### **Phase 4: Integration**
- ⏳ Command Server endpoint
- ⏳ MCP tool integration
- ⏳ Electron app UI for agent switching
- ⏳ Agent status tracking

---

## 🎯 **USE CASES**

### **Use Case 1: Agent Self-Activation**
**Scenario:** Agent wants to activate itself in Cursor sidebar

**Flow:**
1. Agent sends activation message with agent_name
2. System registers agent name
3. Macro switches to that agent
4. Agent is now active

### **Use Case 2: Agent Handoff**
**Scenario:** Agent A wants to handoff to Agent B

**Flow:**
1. Agent A sends handoff message
2. System detects Agent B name
3. Macro switches to Agent B
4. Agent B receives handoff context

### **Use Case 3: Autonomous Agent Selection**
**Scenario:** System needs to select agent for task

**Flow:**
1. System determines best agent for task
2. Macro switches to that agent
3. Agent receives task assignment
4. Agent begins work

---

## 🚀 **NEXT STEPS**

1. **Implement Agent Name Protocol** - Update agent activation to include unique names
2. **Create Vision Templates** - Capture agent name templates from Cursor sidebar
3. **Build Macro Functions** - Implement agent switching macro
4. **Add Command Server Endpoint** - Expose agent switching via HTTP
5. **Test Agent Switching** - Verify macro works reliably

---

**Status:** Design complete, ready for implementation  
**Priority:** High - Enables agent automation and handoff  
**Complexity:** Medium - Requires vision detection + macro automation

