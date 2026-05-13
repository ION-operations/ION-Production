# CMC Integration Tagging Guide for Chat/IDE Events
**Date:** 2025-01-28  
**Route:** R-CHAT-IDE-TAGGING-001  
**Status:** ✅ **READY FOR IMPLEMENTATION**  
**Author:** Atlas (CMC)

---

## 🎯 **OVERVIEW**

This guide provides complete details on how to apply standardized integration tags to chat/IDE events when creating CMC atoms. This enables consistent HHNI indexing, SDF-CVF quartet parity tracking, and integration discovery across all AIM-OS systems.

---

## 📋 **STANDARDIZED TAG FORMAT**

### **Format Specification:**

**List Format (Human-Readable):**
```
["system:<name>:<priority>", "integration_type:<type>", "connection:<direction>", "modality:<modality>"]
```

**CMC Weighted Dict Format (Implementation):**
```python
{
    "system:<name>:<priority>": 1.0,
    "integration_type:<type>": 1.0,
    "connection:<direction>": 0.9,
    "modality:<modality>": 1.0,
    # Additional context tags
    "chat_ide": 1.0,
    "action:<action_type>": 1.0,
    "mode:<thinking_mode>": 0.9,
}
```

### **Tag Components:**

1. **`system:<name>:<priority>`**
   - **Purpose:** Identifies which AIM-OS system is involved
   - **Format:** `system:<system_name>:<priority>`
   - **Examples:**
     - `system:vif:critical` - VIF witness creation (critical priority)
     - `system:apoe:p0` - APOE plan execution (P0 priority)
     - `system:hhni:routine` - HHNI retrieval (routine priority)
     - `system:cmc:p0` - CMC atom storage (P0 priority)

2. **`integration_type:<type>`**
   - **Purpose:** Identifies the type of integration operation
   - **Format:** `integration_type:<type>`
   - **Examples:**
     - `integration_type:witness` - VIF witness creation
     - `integration_type:plan_execution` - APOE plan execution
     - `integration_type:memory_operation` - CMC/HHNI memory operation
     - `integration_type:timeline_event` - TCS timeline entry
     - `integration_type:evidence` - SEG evidence creation/linking
     - `integration_type:cognitive_event` - CAS cognitive event

3. **`connection:<direction>`**
   - **Purpose:** Identifies the data flow direction
   - **Format:** `connection:<direction>`
   - **Examples:**
     - `connection:chat->apoe` - Chat/IDE → APOE
     - `connection:apoe->cmc` - APOE → CMC
     - `connection:cmc->hhni` - CMC → HHNI (polling)
     - `connection:vif->cmc` - VIF → CMC (witness storage)
     - `connection:chat->vif` - Chat/IDE → VIF (witness creation)

4. **`modality:<modality>`**
   - **Purpose:** Identifies the content modality
   - **Format:** `modality:<modality>`
   - **Examples:**
     - `modality:text` - Text content
     - `modality:code` - Code content
     - `modality:text+code` - Mixed text and code
     - `modality:plan_execution` - APOE plan execution
     - `modality:witness` - VIF witness envelope
     - `modality:tcs_timeline` - TCS timeline entry

---

## 🔧 **CMC ATOM CREATION WITH TAGS**

### **Basic Pattern:**

```python
from cmc_service.models import AtomCreate, AtomContent
from cmc_service.memory_store import MemoryStore

# Initialize CMC store
cmc_store = MemoryStore("./data")

# Create atom with standardized tags
atom_payload = AtomCreate(
    modality="chat_ide_action",
    content=AtomContent(
        inline=json.dumps({
            "action_type": "code_generation",
            "user_intent": "Create a new React component",
            "mode": "execution",
            "agent": "coding",
        }),
        media_type="application/json"
    ),
    tags={
        # Standardized integration tags
        "system:cmc:p0": 1.0,
        "system:vif:critical": 1.0,
        "integration_type:witness": 1.0,
        "connection:chat->vif": 1.0,
        "modality:text+code": 1.0,
        # Context tags
        "chat_ide": 1.0,
        "action:code_generation": 1.0,
        "mode:execution": 0.9,
        "agent:coding": 0.9,
    },
    metadata={
        "action_type": "code_generation",
        "user_intent": "Create a new React component",
        "mode": "execution",
        "agent": "coding",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)

# Create atom (witness stub created automatically)
atom = cmc_store.create_atom(atom_payload, correlation_id="chat_action_123")
```

### **Tag Conversion Helper:**

```python
def create_integration_tags(
    system_name: str,
    priority: str,  # "p0", "critical", "important", "routine", "low_stakes"
    integration_type: str,
    connection: str,  # "chat->apoe", "apoe->cmc", etc.
    modality: str,
    context_tags: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Create standardized integration tags for CMC atom creation.
    
    Args:
        system_name: AIM-OS system name (e.g., "vif", "apoe", "cmc")
        priority: Priority level (e.g., "p0", "critical", "routine")
        integration_type: Type of integration (e.g., "witness", "plan_execution")
        connection: Connection direction (e.g., "chat->apoe")
        modality: Content modality (e.g., "text", "code", "text+code")
        context_tags: Additional context tags (e.g., {"chat_ide": 1.0, "mode:execution": 0.9})
    
    Returns:
        Weighted tag dictionary for CMC AtomCreate
    """
    tags = {
        f"system:{system_name}:{priority}": 1.0,
        f"integration_type:{integration_type}": 1.0,
        f"connection:{connection}": 0.9,
        f"modality:{modality}": 1.0,
    }
    
    if context_tags:
        tags.update(context_tags)
    
    return tags
```

---

## 📝 **CHAT/IDE EVENT TAG EXAMPLES**

### **1. Code Generation Action (Chat/IDE → VIF → CMC)**

```python
# User action: "Create a new React component"
tags = create_integration_tags(
    system_name="vif",
    priority="critical",
    integration_type="witness",
    connection="chat->vif",
    modality="text+code",
    context_tags={
        "chat_ide": 1.0,
        "action:code_generation": 1.0,
        "mode:execution": 0.9,
        "agent:coding": 0.9,
    }
)

atom_payload = AtomCreate(
    modality="chat_ide_action",
    content=AtomContent(
        inline=json.dumps({
            "action_type": "code_generation",
            "user_intent": "Create a new React component",
            "mode": "execution",
            "agent": "coding",
            "witness_id": "witness_abc123",  # VIF witness ID
        }),
        media_type="application/json"
    ),
    tags=tags,
    metadata={
        "action_type": "code_generation",
        "user_intent": "Create a new React component",
        "mode": "execution",
        "agent": "coding",
        "witness_id": "witness_abc123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)
```

### **2. Plan Execution (Chat/IDE → APOE → CMC)**

```python
# User action: "Plan and execute feature implementation"
tags = create_integration_tags(
    system_name="apoe",
    priority="p0",
    integration_type="plan_execution",
    connection="chat->apoe",
    modality="plan_execution",
    context_tags={
        "chat_ide": 1.0,
        "action:plan_execution": 1.0,
        "mode:execution": 0.9,
        "agent:planning": 0.9,
    }
)

atom_payload = AtomCreate(
    modality="plan_execution",
    content=AtomContent(
        inline=json.dumps({
            "plan_name": "feature_implementation",
            "execution_id": "exec_xyz789",
            "status": "in_progress",
            "steps_completed": 2,
            "total_steps": 5,
        }),
        media_type="application/json"
    ),
    tags=tags,
    metadata={
        "plan_name": "feature_implementation",
        "execution_id": "exec_xyz789",
        "status": "in_progress",
        "steps_completed": 2,
        "total_steps": 5,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)
```

### **3. Memory Retrieval (Chat/IDE → HHNI → CMC)**

```python
# User action: "Search for previous work on authentication"
tags = create_integration_tags(
    system_name="hhni",
    priority="routine",
    integration_type="memory_operation",
    connection="chat->hhni",
    modality="text",
    context_tags={
        "chat_ide": 1.0,
        "action:memory_retrieval": 1.0,
        "mode:research": 0.9,
        "agent:planning": 0.9,
    }
)

atom_payload = AtomCreate(
    modality="memory_retrieval",
    content=AtomContent(
        inline=json.dumps({
            "query": "authentication implementation",
            "results_count": 5,
            "retrieval_mode": "semantic_search",
        }),
        media_type="application/json"
    ),
    tags=tags,
    metadata={
        "query": "authentication implementation",
        "results_count": 5,
        "retrieval_mode": "semantic_search",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)
```

### **4. Timeline Event (Chat/IDE → TCS → CMC)**

```python
# User action: "Log decision to use React hooks"
tags = create_integration_tags(
    system_name="tcs",
    priority="routine",
    integration_type="timeline_event",
    connection="chat->tcs",
    modality="text",
    context_tags={
        "chat_ide": 1.0,
        "action:timeline_log": 1.0,
        "mode:synthesis": 0.9,
        "agent:planning": 0.9,
    }
)

atom_payload = AtomCreate(
    modality="tcs_timeline",
    content=AtomContent(
        inline=json.dumps({
            "prompt_id": "prompt_456",
            "summary": "Decision to use React hooks for state management",
            "event_type": "decision",
            "confidence": 0.85,
        }),
        media_type="application/json"
    ),
    tags=tags,
    metadata={
        "prompt_id": "prompt_456",
        "summary": "Decision to use React hooks for state management",
        "event_type": "decision",
        "confidence": 0.85,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)
```

### **5. Evidence Creation (Chat/IDE → SEG → CMC)**

```python
# User action: "Link evidence to previous decision"
tags = create_integration_tags(
    system_name="seg",
    priority="important",
    integration_type="evidence",
    connection="chat->seg",
    modality="text",
    context_tags={
        "chat_ide": 1.0,
        "action:evidence_creation": 1.0,
        "mode:synthesis": 0.9,
        "agent:planning": 0.9,
    }
)

atom_payload = AtomCreate(
    modality="evidence",
    content=AtomContent(
        inline=json.dumps({
            "evidence_id": "evidence_789",
            "evidence_type": "decision_rationale",
            "linked_atom_ids": ["atom_123", "atom_456"],
        }),
        media_type="application/json"
    ),
    tags=tags,
    metadata={
        "evidence_id": "evidence_789",
        "evidence_type": "decision_rationale",
        "linked_atom_ids": ["atom_123", "atom_456"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)
```

---

## 🔗 **TAG FLOW THROUGH ORCHESTRATION LAYER**

### **Flow Diagram:**

```
Chat/IDE Event
    ↓
MCPService.ts (attach integration_tags)
    ↓
APOE Executor (stamp tags in DAG nodes)
    ↓
CMC create_atom() (store tags + witness)
    ↓
HHNI Indexer (filter by tags)
    ↓
SEG Evidence (link via atom_id)
```

### **Implementation in MCPService.ts:**

```typescript
// In MCPService.ts
interface ChatEvent {
  mode: "research" | "execution" | "synthesis";
  intent: string;
  selection?: string;
  constraints?: string[];
  integration_tags?: string[];  // Standardized format
}

// Convert list format to weighted dict for CMC
function convertTagsToCMCFormat(tags: string[]): Record<string, number> {
  const tagDict: Record<string, number> = {};
  
  tags.forEach(tag => {
    // Parse tag components
    if (tag.startsWith("system:")) {
      tagDict[tag] = 1.0;
    } else if (tag.startsWith("integration_type:")) {
      tagDict[tag] = 1.0;
    } else if (tag.startsWith("connection:")) {
      tagDict[tag] = 0.9;
    } else if (tag.startsWith("modality:")) {
      tagDict[tag] = 1.0;
    } else {
      // Context tags
      tagDict[tag] = 0.9;
    }
  });
  
  return tagDict;
}

// Create CMC atom with tags
async function createCMCAtom(event: ChatEvent, content: any) {
  const tags = convertTagsToCMCFormat(event.integration_tags || []);
  
  // Add context tags
  tags["chat_ide"] = 1.0;
  tags[`mode:${event.mode}`] = 0.9;
  
  const atomPayload = {
    modality: "chat_ide_action",
    content: {
      inline: JSON.stringify(content),
      media_type: "application/json"
    },
    tags: tags,
    metadata: {
      mode: event.mode,
      intent: event.intent,
      timestamp: new Date().toISOString(),
    }
  };
  
  // Call CMC create_atom via MCP
  return await mcpClient.call("mcp_lucid-mcp_store_memory", {
    payload: atomPayload
  });
}
```

---

## 🛡️ **WITNESS STORAGE WITH TAGS**

### **VIF Witness + Tags Pattern:**

```python
from cmc_service.models import AtomCreate, AtomContent, WitnessStub
from cmc_service.memory_store import MemoryStore

# Create atom with witness stub
witness_stub = WitnessStub(
    model_id="gpt-4",
    tool_ids=["mcp_lucid-mcp_store_memory", "mcp_lucid-mcp_retrieve_memory"],
    correlation_id="chat_action_123",
    uncertainty_band="green",
    uncertainty_ece=0.05,
)

atom_payload = AtomCreate(
    modality="chat_ide_action",
    content=AtomContent(
        inline=json.dumps({
            "action_type": "code_generation",
            "user_intent": "Create a new React component",
            "witness_id": "witness_abc123",
        }),
        media_type="application/json"
    ),
    tags={
        # Standardized integration tags
        "system:vif:critical": 1.0,
        "system:cmc:p0": 1.0,
        "integration_type:witness": 1.0,
        "connection:chat->vif": 1.0,
        "modality:text+code": 1.0,
        # Context tags
        "chat_ide": 1.0,
        "action:code_generation": 1.0,
        "mode:execution": 0.9,
    },
    metadata={
        "action_type": "code_generation",
        "user_intent": "Create a new React component",
        "witness_id": "witness_abc123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)

# Create atom (witness stub attached automatically)
atom = cmc_store.create_atom(atom_payload, correlation_id="chat_action_123")

# Witness is stored in atom.witness
assert atom.witness.model_id == "gpt-4"
assert atom.witness.correlation_id == "chat_action_123"
```

### **Witness + Tags Verification:**

```python
# Retrieve atom and verify witness + tags
atom = cmc_store.get_atom("atom_123")

# Verify witness
assert atom.witness.model_id is not None
assert atom.witness.correlation_id is not None

# Verify tags
assert "system:vif:critical" in atom.tags
assert "integration_type:witness" in atom.tags
assert "connection:chat->vif" in atom.tags
assert "modality:text+code" in atom.tags
```

---

## 📊 **APOE DAG NODE TAGGING**

### **Stamping Tags in DAG Nodes:**

```python
# In APOE executor (packages/apoe/executor.py)
def create_dag_node(
    task: Task,
    integration_tags: List[str],  # From orchestration layer
) -> DAGNode:
    """
    Create DAG node with standardized integration tags.
    """
    # Convert list format to weighted dict
    tags_dict = {
        tag: 1.0 if tag.startswith(("system:", "integration_type:", "modality:")) else 0.9
        for tag in integration_tags
    }
    
    # Add APOE-specific tags
    tags_dict.update({
        "system:apoe:p0": 1.0,
        "integration_type:plan_execution": 1.0,
        "connection:chat->apoe": 1.0,
        "modality:plan_execution": 1.0,
    })
    
    node = DAGNode(
        task_id=task.id,
        task_name=task.name,
        tags=tags_dict,  # Stamped in node
        metadata={
            "integration_tags": integration_tags,  # Preserve list format
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    
    return node
```

---

## ✅ **VERIFICATION CHECKLIST**

### **Before Creating CMC Atoms:**

- [ ] **Standardized Tags:** All 4 required tags present (`system:`, `integration_type:`, `connection:`, `modality:`)
- [ ] **Priority Correct:** Priority matches action severity (critical/important/routine/low_stakes)
- [ ] **Connection Direction:** Connection direction matches data flow (e.g., `chat->apoe`)
- [ ] **Modality Accurate:** Modality matches content type (text/code/text+code)
- [ ] **Context Tags:** Additional context tags included (chat_ide, action:, mode:, agent:)
- [ ] **Metadata Complete:** Metadata includes all relevant fields (timestamp, action_type, etc.)
- [ ] **Witness Stub:** Witness stub created (if VIF witness required)

### **After Creating CMC Atoms:**

- [ ] **Atom ID Generated:** Atom ID returned successfully
- [ ] **Tags Stored:** Tags stored correctly (verify via `get_atom()`)
- [ ] **Witness Stored:** Witness stub stored correctly (if applicable)
- [ ] **Metadata Stored:** Metadata stored correctly
- [ ] **HHNI Indexing:** Tags enable HHNI filtering (verify via `retrieve_memory()`)
- [ ] **SEG Linking:** Atom ID available for SEG evidence linking

---

## 🔗 **REFERENCES**

- **CMC Models:** `packages/cmc_service/models.py`
- **CMC Memory Store:** `packages/cmc_service/memory_store.py`
- **APOE CMC Integration:** `packages/apoe/cmc_integration.py`
- **TCS CMC Integration:** `packages/cmc_service/tcs_seg_integration_helper.py`
- **Synthesis Outcomes:** `SYNTHESIS_SESSION_FINAL_OUTCOMES.md`
- **Integration Tagging Decision:** Part 3 of synthesis session

---

## 📝 **NEXT STEPS FOR CODEX**

1. **Implement Tag Conversion:** Create helper function to convert list format to weighted dict
2. **Update MCPService.ts:** Add integration tag attachment to chat events
3. **Update APOE Executor:** Stamp tags in DAG nodes
4. **Test Tag Flow:** Verify tags flow through orchestration layer
5. **Verify CMC Storage:** Confirm tags stored correctly in CMC atoms
6. **Test HHNI Filtering:** Verify HHNI can filter by tags
7. **Test SEG Linking:** Verify SEG can link evidence via atom_id

---

**Status:** ✅ **READY FOR IMPLEMENTATION**  
**Confidence:** 0.95 - All patterns documented, examples provided, ready for Codex integration  
**Timeline:** Can start immediately (Week 1, Days 1-3)

---

*Integration Tagging Guide - Created 2025-01-28*  
*Atlas (CMC) → Codex (Chat/IDE)* 💙

