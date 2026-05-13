# AI-Powered Prompt Chain Creation via MCP - Bidirectional Integration
**Date:** 2025-01-27  
**Status:** Design Document - Comprehensive Architecture  
**Purpose:** Enable AIs to create complex prompt chains via MCP, visualize them in UI, and allow manual editing with bidirectional sync

---

## 🎯 Executive Summary

**Goal:** Create a seamless bidirectional system where:
1. **AIs create prompt chains via MCP tools** → Chains appear in visual diagram
2. **Users manually edit chains in UI** → Changes sync back to CMC/APOE
3. **Real-time synchronization** between MCP-created chains and UI edits
4. **Version control** with bitemporal tracking in CMC

**Vision:** AIs can orchestrate complex workflows visually, and humans can refine/optimize them manually.

---

## 🔄 Bidirectional Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Cursor)                          │
│                                                               │
│  Uses MCP Tools:                                              │
│  - create_prompt_chain                                        │
│  - update_prompt_chain                                        │
│  - add_chain_node                                             │
│  - connect_chain_nodes                                        │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Server (lucid_mcp_server.py)                │
│                                                               │
│  - Validates chain structure                                  │
│  - Stores in CMC (bitemporal)                                │
│  - Notifies Electron app via WebSocket                        │
│  - Returns chain_id for reference                            │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              CMC (Context Memory Core)                       │
│                                                               │
│  - Chain definitions stored as atoms                          │
│  - Bitemporal versioning                                     │
│  - Change history tracking                                   │
│  - Tags: {"type": "prompt_chain", "chain_id": "..."}         │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│           Electron App (Prompt Chains Tab)                   │
│                                                               │
│  - Polls CMC for chains (or WebSocket push)                  │
│  - Renders visual diagram (ReactFlow)                         │
│  - Allows manual editing                                      │
│  - Saves changes via MCP tools                                │
└───────────────────┬───────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Tools (update_prompt_chain)                  │
│                                                               │
│  - Receives updated chain from UI                             │
│  - Validates changes                                          │
│  - Stores new version in CMC                                 │
│  - Notifies other agents if needed                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ New MCP Tools Design

### 1. `create_prompt_chain`

**Purpose:** AI creates a new prompt chain with nodes and connections

**Parameters:**
```typescript
{
  name: string                    // Chain name
  description?: string            // Optional description
  nodes: Node[]                   // Array of node definitions
  edges: Edge[]                   // Array of edge definitions
  executionType?: 'sequential' | 'parallel' | 'dynamic'
  entryPoint?: string             // Node ID for entry point
  metadata?: {
    tags?: string[]
    category?: string
    isTemplate?: boolean
  }
}
```

**Node Definition:**
```typescript
interface Node {
  id: string                      // Unique node ID
  type: NodeType                  // 'prompt' | 'conditional' | 'loop' | 'parallel' | 'merge' | 'agent' | 'system'
  position: { x: number, y: number }  // Visual position
  label: string                   // Display label
  prompt?: string                 // Prompt content (if type='prompt')
  agentId?: string               // Agent ID (if type='agent')
  systemId?: string              // System ID (if type='system')
  condition?: string              // Condition expression (if type='conditional')
  config?: {
    timeout?: number
    retryCount?: number
    confidenceThreshold?: number
  }
}
```

**Edge Definition:**
```typescript
interface Edge {
  id: string                      // Unique edge ID
  source: string                  // Source node ID
  target: string                  // Target node ID
  type: EdgeType                  // 'sequential' | 'conditional_true' | 'conditional_false' | 'parallel' | 'error'
  condition?: string              // Condition expression (if type='conditional_*')
  dataMapping?: DataMapping       // Data flow mapping
}
```

**Response:**
```typescript
{
  success: boolean
  chain_id: string               // CMC atom ID
  chain: ChainDefinition          // Full chain definition
  message?: string
}
```

**Example Usage:**
```python
# AI creates a code review chain
result = await mcp_client.call_tool("create_prompt_chain", {
  "name": "Code Review & Optimization",
  "description": "Review code for performance issues",
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "position": {"x": 100, "y": 100},
      "label": "Start"
    },
    {
      "id": "analyze",
      "type": "agent",
      "position": {"x": 300, "y": 100},
      "label": "Code Analysis",
      "agentId": "lexicon",
      "prompt": "Analyze this code for performance issues: {{code}}"
    },
    {
      "id": "optimize",
      "type": "agent",
      "position": {"x": 500, "y": 100},
      "label": "Optimize",
      "agentId": "lexicon",
      "prompt": "Suggest optimizations based on: {{analyze.output}}"
    }
  ],
  "edges": [
    {"id": "e1", "source": "start", "target": "analyze", "type": "sequential"},
    {"id": "e2", "source": "analyze", "target": "optimize", "type": "sequential"}
  ],
  "entryPoint": "start"
})
```

---

### 2. `update_prompt_chain`

**Purpose:** Update existing chain (from AI or UI)

**Parameters:**
```typescript
{
  chain_id: string                // CMC atom ID
  updates: {
    name?: string
    description?: string
    nodes?: Node[]                // Full node array (replaces all)
    edges?: Edge[]                // Full edge array (replaces all)
    executionType?: string
    entryPoint?: string
    metadata?: object
  }
  reason?: string                 // Why this update (for history)
}
```

**Response:**
```typescript
{
  success: boolean
  chain_id: string
  chain: ChainDefinition          // Updated chain
  version: number                 // New version number
  message?: string
}
```

**Use Cases:**
- AI modifies chain based on results
- User manually edits in UI
- Chain adapts dynamically

---

### 3. `add_chain_node`

**Purpose:** Add a single node to existing chain

**Parameters:**
```typescript
{
  chain_id: string
  node: Node                       // New node definition
  connectTo?: string[]             // Array of node IDs to connect to
  connectFrom?: string[]           // Array of node IDs to connect from
}
```

**Response:**
```typescript
{
  success: boolean
  chain_id: string
  node_id: string                  // New node ID
  chain: ChainDefinition          // Updated chain
}
```

---

### 4. `connect_chain_nodes`

**Purpose:** Create connection between nodes

**Parameters:**
```typescript
{
  chain_id: string
  source: string                   // Source node ID
  target: string                   // Target node ID
  type?: EdgeType                  // Default: 'sequential'
  condition?: string               // For conditional edges
  dataMapping?: DataMapping
}
```

**Response:**
```typescript
{
  success: boolean
  chain_id: string
  edge_id: string                  // New edge ID
  chain: ChainDefinition          // Updated chain
}
```

---

### 5. `get_prompt_chain`

**Purpose:** Retrieve chain definition

**Parameters:**
```typescript
{
  chain_id: string
  version?: number                 // Optional: get specific version
}
```

**Response:**
```typescript
{
  success: boolean
  chain: ChainDefinition
  version: number
  history?: ChainVersion[]        // Version history if requested
}
```

---

### 6. `list_prompt_chains`

**Purpose:** List all chains (with filtering)

**Parameters:**
```typescript
{
  filters?: {
    tags?: string[]
    category?: string
    isTemplate?: boolean
    createdBy?: string             // Agent name
  }
  limit?: number
}
```

**Response:**
```typescript
{
  success: boolean
  chains: ChainDefinition[]
  total: number
}
```

---

### 7. `execute_prompt_chain`

**Purpose:** Execute a chain (delegates to APOE)

**Parameters:**
```typescript
{
  chain_id: string
  inputs?: Record<string, any>    // Input parameters
  context?: Record<string, any>    // Execution context
}
```

**Response:**
```typescript
{
  success: boolean
  execution_id: string
  status: 'running' | 'completed' | 'failed'
  results?: Record<string, any>
}
```

---

## 🎨 Electron App Integration

### Real-Time Synchronization

**Option 1: Polling (Simple)**
```typescript
// Poll CMC every 5 seconds for chain updates
useEffect(() => {
  const interval = setInterval(async () => {
    const chains = await aimosService.getPromptChains()
    setChains(chains)
  }, 5000)
  return () => clearInterval(interval)
}, [])
```

**Option 2: WebSocket (Preferred)**
```typescript
// Subscribe to chain updates via WebSocket
useEffect(() => {
  const ws = new WebSocket('ws://localhost:5001/chains')
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data)
    if (update.type === 'chain_created' || update.type === 'chain_updated') {
      // Refresh chains
      fetchChains()
    }
  }
  return () => ws.close()
}, [])
```

### Visual Rendering

**ReactFlow Integration:**
```typescript
// Convert CMC chain to ReactFlow format
const convertChainToReactFlow = (chain: ChainDefinition) => {
  const nodes = chain.nodes.map(node => ({
    id: node.id,
    type: node.type,
    position: node.position,
    data: {
      label: node.label,
      prompt: node.prompt,
      agentId: node.agentId,
      systemId: node.systemId,
      ...node.config
    }
  }))
  
  const edges = chain.edges.map(edge => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: edge.type,
    label: edge.condition || '',
    animated: isExecuting(edge)
  }))
  
  return { nodes, edges }
}
```

### Manual Editing Flow

**1. User Edits Node:**
```typescript
const handleNodeChange = async (nodeId: string, updates: Partial<Node>) => {
  // Update local state immediately (optimistic update)
  setNodes(prev => prev.map(n => 
    n.id === nodeId ? { ...n, ...updates } : n
  ))
  
  // Sync to CMC via MCP
  try {
    await serviceBridge.updatePromptChain({
      chain_id: currentChain.id,
      updates: {
        nodes: getUpdatedNodes() // Full node array
      },
      reason: `User manually edited node ${nodeId}`
    })
  } catch (error) {
    // Rollback on error
    revertChanges()
  }
}
```

**2. User Adds Connection:**
```typescript
const handleConnect = async (source: string, target: string) => {
  await serviceBridge.connectChainNodes({
    chain_id: currentChain.id,
    source,
    target,
    type: 'sequential'
  })
  
  // Refresh chain from CMC
  await fetchChain(currentChain.id)
}
```

**3. User Deletes Node:**
```typescript
const handleDeleteNode = async (nodeId: string) => {
  await serviceBridge.updatePromptChain({
    chain_id: currentChain.id,
    updates: {
      nodes: nodes.filter(n => n.id !== nodeId),
      edges: edges.filter(e => e.source !== nodeId && e.target !== nodeId)
    },
    reason: `User deleted node ${nodeId}`
  })
}
```

---

## 📡 ServiceBridge Integration

**Add to ServiceBridge:**
```typescript
class ServiceBridge {
  // ... existing methods ...
  
  async createPromptChain(chain: ChainDefinition): Promise<ChainResponse> {
    if (this.isMCPAvailable) {
      return await this.mcpApi.createPromptChain(chain)
    } else {
      return await this.aimosService.createPromptChain(chain)
    }
  }
  
  async updatePromptChain(chainId: string, updates: ChainUpdates): Promise<ChainResponse> {
    if (this.isMCPAvailable) {
      return await this.mcpApi.updatePromptChain(chainId, updates)
    } else {
      return await this.aimosService.updatePromptChain(chainId, updates)
    }
  }
  
  async getPromptChains(filters?: ChainFilters): Promise<ChainDefinition[]> {
    if (this.isMCPAvailable) {
      return await this.mcpApi.listPromptChains(filters)
    } else {
      return await this.aimosService.getPromptChains(filters)
    }
  }
  
  // ... other chain methods ...
}
```

---

## 🔄 Conflict Resolution

### Scenario: AI and User Edit Simultaneously

**Strategy: Last-Write-Wins with Conflict Detection**

```typescript
interface ChainVersion {
  version: number
  timestamp: Date
  modifiedBy: string              // 'ai' | 'user' | agent name
  changes: string[]
}

// When updating, check version
const updateChain = async (chainId: string, updates: ChainUpdates) => {
  const currentChain = await getPromptChain(chainId)
  
  // Check if chain was modified since last fetch
  if (currentChain.version > lastKnownVersion) {
    // Conflict detected
    showConflictDialog({
      current: currentChain,
      local: localChanges,
      options: ['Keep Local', 'Keep Remote', 'Merge']
    })
  } else {
    // Safe to update
    await updatePromptChain(chainId, updates)
  }
}
```

### Merge Strategy

**3-Way Merge:**
1. **Base Version**: Last version both AI and user saw
2. **AI Version**: AI's changes
3. **User Version**: User's changes

**Merge Rules:**
- If both changed same node → User wins (manual override)
- If changed different nodes → Both applied
- If deleted node → User decision required

---

## 📊 Data Model in CMC

### Chain Storage Format

```yaml
# CMC Atom Structure
atom_id: "chain_abc123"
content:
  type: "prompt_chain"
  chain_id: "chain_abc123"
  name: "Code Review & Optimization"
  description: "Review code for performance issues"
  version: 3
  
  # Visual representation
  nodes:
    - id: "start"
      type: "start"
      position: {x: 100, y: 100}
      label: "Start"
    - id: "analyze"
      type: "agent"
      position: {x: 300, y: 100}
      label: "Code Analysis"
      agentId: "lexicon"
      prompt: "Analyze this code: {{code}}"
      config:
        timeout: 30000
        confidenceThreshold: 0.70
  
  edges:
    - id: "e1"
      source: "start"
      target: "analyze"
      type: "sequential"
  
  # Execution metadata
  executionType: "sequential"
  entryPoint: "start"
  
  # Template info
  isTemplate: false
  tags: ["code-review", "optimization"]
  category: "development"

metadata:
  created_at: "2025-01-27T10:00:00Z"
  created_by: "aether"
  updated_at: "2025-01-27T10:15:00Z"
  updated_by: "user"
  version: 3

tags:
  type: "prompt_chain"
  chain_id: "chain_abc123"
  category: "development"
  tags: ["code-review", "optimization"]
```

---

## 🎯 AI Usage Patterns

### Pattern 1: AI Creates Chain from Goal

```python
# AI receives task: "Review and optimize the codebase"
goal = "Review and optimize the codebase"

# AI creates orchestration plan
plan = await create_plan({
  "goal": goal,
  "priority": "high"
})

# Convert plan to prompt chain
chain = {
  "name": f"Code Review: {goal}",
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "position": {"x": 100, "y": 100},
      "label": "Start"
    },
    {
      "id": "analyze",
      "type": "agent",
      "position": {"x": 300, "y": 100},
      "label": "Code Analysis",
      "agentId": "lexicon",
      "prompt": f"Analyze codebase for: {goal}"
    },
    # ... more nodes from plan steps
  ],
  "edges": [
    # ... connections based on plan dependencies
  ]
}

# Create chain via MCP
result = await create_prompt_chain(chain)
chain_id = result["chain_id"]

# User sees chain appear in UI automatically
# User can then manually refine/edit it
```

### Pattern 2: AI Modifies Chain Based on Results

```python
# Chain execution reveals bottleneck
execution_results = await execute_prompt_chain({
  "chain_id": "chain_abc123"
})

# AI analyzes results and optimizes chain
if execution_results["bottleneck_node"]:
  # Add parallel processing
  await add_chain_node({
    "chain_id": "chain_abc123",
    "node": {
      "id": "parallel_analyze",
      "type": "parallel",
      "position": {"x": 500, "y": 100},
      "label": "Parallel Analysis"
    },
    "connectFrom": ["analyze"],
    "connectTo": ["optimize"]
  })
  
  # User sees optimization appear in UI
```

### Pattern 3: AI Uses Template

```python
# AI finds relevant template
templates = await list_prompt_chains({
  "filters": {
    "isTemplate": True,
    "tags": ["code-review"]
  }
})

# Instantiate template
template = templates[0]
chain = await create_prompt_chain({
  "name": "Code Review - Custom",
  "nodes": template.nodes,  # Copy nodes
  "edges": template.edges,  # Copy edges
  "metadata": {
    "basedOn": template.chain_id
  }
})

# User sees instantiated chain
```

---

## 🔌 MCP Server Implementation

### New Methods in `lucid_mcp_server.py`

```python
def create_prompt_chain(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new prompt chain"""
    try:
        chain_def = args.get("chain")
        if not chain_def:
            raise ValueError("chain definition required")
        
        # Validate chain structure
        self._validate_chain(chain_def)
        
        # Generate chain_id
        chain_id = f"chain_{uuid.uuid4().hex[:8]}"
        chain_def["chain_id"] = chain_id
        chain_def["version"] = 1
        
        # Store in CMC
        atom_id = self.cmc_client.create_atom(
            content=chain_def,
            tags={
                "type": "prompt_chain",
                "chain_id": chain_id,
                "category": chain_def.get("metadata", {}).get("category", "general"),
                **chain_def.get("metadata", {}).get("tags", {})
            },
            metadata={
                "created_at": datetime.utcnow().isoformat(),
                "created_by": args.get("created_by", "ai"),
                "version": 1
            }
        )
        
        # Notify Electron app via WebSocket (if available)
        self._notify_chain_update("chain_created", chain_id)
        
        return {
            "success": True,
            "chain_id": atom_id,
            "chain": chain_def,
            "message": f"Chain created: {chain_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def update_prompt_chain(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Update existing prompt chain"""
    try:
        chain_id = args.get("chain_id")
        updates = args.get("updates", {})
        
        # Get current chain
        chain = self.cmc_client.get_atom(chain_id)
        if not chain:
            raise ValueError(f"Chain not found: {chain_id}")
        
        # Merge updates
        updated_chain = {**chain.content, **updates}
        updated_chain["version"] = chain.metadata.get("version", 1) + 1
        
        # Validate updated chain
        self._validate_chain(updated_chain)
        
        # Store new version in CMC (bitemporal)
        new_atom_id = self.cmc_client.create_atom(
            content=updated_chain,
            tags=chain.tags,
            metadata={
                **chain.metadata,
                "updated_at": datetime.utcnow().isoformat(),
                "updated_by": args.get("updated_by", "user"),
                "version": updated_chain["version"],
                "reason": args.get("reason", "Chain updated")
            }
        )
        
        # Notify Electron app
        self._notify_chain_update("chain_updated", chain_id)
        
        return {
            "success": True,
            "chain_id": new_atom_id,
            "chain": updated_chain,
            "version": updated_chain["version"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _validate_chain(self, chain: Dict[str, Any]) -> None:
    """Validate chain structure"""
    # Check required fields
    assert "name" in chain, "Chain name required"
    assert "nodes" in chain, "Chain nodes required"
    assert "edges" in chain, "Chain edges required"
    
    # Validate nodes
    node_ids = {node["id"] for node in chain["nodes"]}
    assert len(node_ids) == len(chain["nodes"]), "Duplicate node IDs"
    
    # Validate edges
    for edge in chain["edges"]:
        assert edge["source"] in node_ids, f"Invalid source node: {edge['source']}"
        assert edge["target"] in node_ids, f"Invalid target node: {edge['target']}"
    
    # Validate entry point
    if "entryPoint" in chain:
        assert chain["entryPoint"] in node_ids, "Invalid entry point"

def _notify_chain_update(self, event_type: str, chain_id: str) -> None:
    """Notify Electron app of chain update"""
    # WebSocket notification (if WebSocket server available)
    if hasattr(self, "ws_server"):
        self.ws_server.broadcast({
            "type": event_type,
            "chain_id": chain_id,
            "timestamp": datetime.utcnow().isoformat()
        })
```

---

## 🎨 UI Enhancements

### Visual Indicators

**AI-Created Chains:**
- Badge: "🤖 AI Created"
- Color: Blue accent
- Tooltip: "Created by AI agent via MCP"

**User-Edited Chains:**
- Badge: "✏️ User Edited"
- Color: Green accent
- Tooltip: "Manually edited by user"

**Template Chains:**
- Badge: "📋 Template"
- Color: Purple accent
- Icon: Template icon

### Real-Time Updates

**Show Live Updates:**
```typescript
const [chainUpdates, setChainUpdates] = useState<ChainUpdate[]>([])

// Show notification when chain updated
useEffect(() => {
  if (chainUpdates.length > 0) {
    const update = chainUpdates[0]
    showNotification({
      type: 'info',
      message: `Chain "${update.chainName}" was ${update.type === 'chain_created' ? 'created' : 'updated'} by ${update.modifiedBy}`,
      action: 'View Chain',
      onClick: () => selectChain(update.chainId)
    })
  }
}, [chainUpdates])
```

### Edit Mode

**Lock/Unlock Editing:**
- AI-created chains: Editable by default
- User can lock chain to prevent AI modifications
- User can unlock to allow AI improvements

**Edit History:**
- Show version history
- Show who made each change
- Ability to revert to previous version

---

## 📋 Implementation Checklist

### Phase 1: MCP Tools (Week 1)
- [ ] Implement `create_prompt_chain` in MCP server
- [ ] Implement `update_prompt_chain` in MCP server
- [ ] Implement `get_prompt_chain` in MCP server
- [ ] Implement `list_prompt_chains` in MCP server
- [ ] Add CMC integration for chain storage
- [ ] Add validation logic
- [ ] Add WebSocket notifications (optional)

### Phase 2: Electron App Integration (Week 2)
- [ ] Add ServiceBridge methods for chain operations
- [ ] Implement real-time chain fetching
- [ ] Convert CMC chain format to ReactFlow format
- [ ] Render chains in visual diagram
- [ ] Handle manual edits
- [ ] Sync edits back to CMC via MCP

### Phase 3: Conflict Resolution (Week 3)
- [ ] Implement version checking
- [ ] Add conflict detection
- [ ] Add merge UI
- [ ] Add conflict resolution logic

### Phase 4: Polish & Testing (Week 4)
- [ ] Add visual indicators (AI/User/Template)
- [ ] Add edit history view
- [ ] Add chain locking/unlocking
- [ ] Comprehensive testing
- [ ] Documentation

---

## 🎯 Success Criteria

1. ✅ AI can create chains via MCP → Chains appear in UI
2. ✅ User can edit chains manually → Changes sync to CMC
3. ✅ Real-time updates (within 5 seconds)
4. ✅ Conflict resolution works
5. ✅ Version history preserved
6. ✅ No data loss during sync
7. ✅ Chains executable via APOE

---

## 📚 References

- **ReactFlow**: https://reactflow.dev/
- **CMC Bitemporal**: AIM-OS Context Memory Core
- **APOE**: AI-Powered Orchestration Engine
- **MCP Protocol**: Model Context Protocol

---

**Status:** Design Complete - Ready for Implementation  
**Next Steps:** Begin Phase 1 - MCP Tools Implementation

