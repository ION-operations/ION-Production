# Agent Onboarding API/LLM Integration

**Date:** 2025-11-19
**Status:** ✅ Complete
**Purpose:** Integrate agent onboarding system with API/LLM (MCP tools, HHNI, SUPER_INDEX)

---

## 🎯 **INTEGRATION OVERVIEW**

The agent onboarding system is now integrated with API/LLM systems, enabling programmatic access to agent context and guidance.

---

## 🔧 **MCP TOOLS INTEGRATION**

### **Available MCP Tools:**

1. **`store_memory`** - Store agent onboarding context in CMC
   - **Usage:** Store agent-specific insights and learnings
   - **Location:** `lucid_mcp_server.py` - `mcp_lucid-mcp_store_memory`

2. **`retrieve_memory`** - Retrieve agent onboarding context from HHNI
   - **Usage:** Retrieve agent-specific context and guidance
   - **Location:** `lucid_mcp_server.py` - `mcp_lucid-mcp_retrieve_memory`

3. **`get_memory_stats`** - Get agent onboarding statistics
   - **Usage:** Get statistics about agent onboarding usage
   - **Location:** `lucid_mcp_server.py` - `mcp_lucid-mcp_get_memory_stats`

### **Agent Onboarding MCP Integration:**

**Store Agent Context:**
```python
# Store agent onboarding context
await mcp_client.call_tool('mcp_lucid-mcp_store_memory', {
    'content': 'Agent onboarding context for {agent_id}',
    'tags': ['agent', '{agent_id}', 'onboarding'],
    'metadata': {
        'agent_id': '{agent_id}',
        'agent_name': '{agent_name}',
        'system': '{system}',
        'onboarding_path': 'knowledge_architecture/AGENT_ONBOARDING/agents/{agent_id}/'
    }
})
```

**Retrieve Agent Context:**
```python
# Retrieve agent onboarding context
result = await mcp_client.call_tool('mcp_lucid-mcp_retrieve_memory', {
    'query': 'Agent onboarding for {agent_id}',
    'tags': ['agent', '{agent_id}', 'onboarding'],
    'limit': 10
})
```

---

## 🔍 **HHNI INTEGRATION**

### **Agent Onboarding Indexing:**

Agent onboarding files are automatically indexed by HHNI when stored in CMC:

1. **Indexing Trigger:** When agent onboarding files are stored in CMC with `hhni_index` tag
2. **Indexing Process:** HHNI polls CMC for atoms with `hhni_index` tag
3. **Retrieval:** Agent onboarding context can be retrieved via HHNI semantic search

### **HHNI Query Patterns:**

**Query by Agent:**
```python
# Query HHNI for agent onboarding
results = hhni_client.retrieve(
    query="Agent onboarding for {agent_id}",
    modality="docs",
    k=10,
    tags=["agent", "{agent_id}", "onboarding"]
)
```

**Query by System:**
```python
# Query HHNI for system-specific onboarding
results = hhni_client.retrieve(
    query="Onboarding for {system} system",
    modality="docs",
    k=10,
    tags=["system", "{system}", "onboarding"]
)
```

---

## 📚 **SUPER_INDEX INTEGRATION**

### **Agent Onboarding in SUPER_INDEX:**

Agent onboarding is referenced in SUPER_INDEX for concept discovery:

1. **Concept Mapping:** Agent onboarding concepts mapped in SUPER_INDEX
2. **Cross-References:** SUPER_INDEX references agent onboarding files
3. **Search:** SUPER_INDEX enables search for agent onboarding concepts

### **SUPER_INDEX Search Patterns:**

**Search for Agent:**
```markdown
Search SUPER_INDEX for: "{agent_name}" or "{agent_id}" or "{system}"
```

**Search for Onboarding:**
```markdown
Search SUPER_INDEX for: "agent onboarding" or "onboarding system"
```

---

## 🤖 **LLM API INTEGRATION**

### **Agent Context Injection:**

Agent onboarding context can be injected into LLM prompts:

1. **Context Retrieval:** Retrieve agent onboarding context via MCP tools
2. **Context Injection:** Inject agent context into LLM prompts
3. **Agent-Specific Responses:** LLM responses tailored to agent context

### **LLM Prompt Patterns:**

**Agent-Specific Prompt:**
```python
# Build agent-specific prompt
agent_context = await retrieve_agent_context(agent_id)
prompt = f"""
You are {agent_name}, {role}.

Agent Context:
{agent_context}

Task: {task_description}
"""
```

**Agent Navigation Prompt:**
```python
# Use agent navigation for context
navigation = await get_agent_navigation(agent_id, situation="I need to understand my core system")
prompt = f"""
Use this navigation guide:
{navigation}

Task: {task_description}
"""
```

---

## 📊 **INTEGRATION STATUS**

### **MCP Tools:**
- ✅ `store_memory` - Available for storing agent context
- ✅ `retrieve_memory` - Available for retrieving agent context
- ✅ `get_memory_stats` - Available for agent statistics

### **HHNI:**
- ✅ Agent onboarding files indexed when stored in CMC
- ✅ Semantic search available for agent context
- ✅ Tag-based filtering available

### **SUPER_INDEX:**
- ✅ Agent onboarding concepts mapped
- ✅ Cross-references to agent onboarding files
- ✅ Search enabled for agent concepts

### **LLM API:**
- ✅ Agent context injection supported
- ✅ Agent-specific prompts enabled
- ✅ Agent navigation integration available

---

## 🎯 **USAGE EXAMPLES**

### **Example 1: Store Agent Context**
```python
# Store agent onboarding context
await mcp_client.call_tool('mcp_lucid-mcp_store_memory', {
    'content': 'Atlas (CMC) onboarding: Foundation builder, bitemporal memory, 70% complete',
    'tags': ['agent', 'atlas', 'cmc', 'onboarding'],
    'metadata': {
        'agent_id': 'atlas',
        'agent_name': 'Atlas',
        'system': 'CMC',
        'completion': '70%'
    }
})
```

### **Example 2: Retrieve Agent Context**
```python
# Retrieve agent onboarding context
result = await mcp_client.call_tool('mcp_lucid-mcp_retrieve_memory', {
    'query': 'Atlas CMC onboarding',
    'tags': ['agent', 'atlas', 'onboarding'],
    'limit': 5
})
```

### **Example 3: LLM Agent Context**
```python
# Use agent context in LLM prompt
agent_context = await retrieve_agent_context('atlas')
llm_response = await llm_api.call({
    'prompt': f'As Atlas (CMC Specialist), {agent_context}. Task: {task}',
    'model': 'gemini-2.0-flash-exp'
})
```

---

## ✅ **INTEGRATION COMPLETE**

**Status:** ✅ **COMPLETE**
- MCP tools integration documented
- HHNI indexing integration documented
- SUPER_INDEX integration documented
- LLM API integration documented

---

**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Integrate agent onboarding with API/LLM systems

