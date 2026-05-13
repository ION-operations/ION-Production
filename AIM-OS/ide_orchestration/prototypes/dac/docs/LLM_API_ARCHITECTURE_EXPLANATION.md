# LLM API Architecture Explanation

**Date:** 2025-11-18
**Purpose:** Clarify how the LLM API integration works and what each component does

---

## 🎯 **THE BIG PICTURE**

You're absolutely right - this IS meant to work with Gemini, Cerebras, and other LLM APIs! Let me explain the architecture:

---

## 📊 **ARCHITECTURE LAYERS**

### **Layer 1: Actual LLM APIs (External Services)**
These are the REAL LLM providers you call:
- **Gemini API** (Google) - `https://generativeai.google.com/api`
- **Cerebras API** - `https://api.cerebras.ai/v1`
- **Anthropic API** (Claude)
- **OpenAI API** (GPT-4)
- etc.

**These are external services** - you call them with API keys over HTTP.

---

### **Layer 2: API Service Registry (Python Package)**
**Location:** `packages/api_service_registry/llm/`

**What it does:**
- Wraps the external LLM APIs
- Handles API key rotation (your 22 keys per provider)
- Manages usage tracking
- Provides a unified interface: `GeminiClient`, `CerebrasClient`, etc.

**Example:**
```python
from packages.api_service_registry.llm import get_api_registry

registry = get_api_registry()
result = registry.call_api(
    provider="gemini",
    endpoint="chat-completion",
    data={
        "messages": [{"role": "user", "content": "Hello!"}],
        "model": "gemini-2.5-flash"
    }
)
# This ACTUALLY calls Google's Gemini API!
```

**This is a Python library** - you can use it directly in any Python script, not just Cursor.

---

### **Layer 3: MCP Server (Interface Layer)**
**Location:** `lucid_mcp_server.py`

**What it does:**
- Provides an interface for clients to call AIM-OS tools
- **Can be used by:**
  - ✅ Cursor IDE (via MCP protocol)
  - ✅ Standalone Python scripts
  - ✅ Electron app
  - ✅ Any other client that speaks JSON-RPC

**The MCP server has a tool called `call_api`** that:
1. Receives a request (e.g., "call Gemini with this prompt")
2. Uses the `api_service_registry` to actually call Gemini
3. Returns the response

**Example MCP tool call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "call_api",
    "arguments": {
      "provider": "gemini",
      "endpoint": "chat-completion",
      "data": {
        "messages": [{"role": "user", "content": "Hello!"}]
      }
    }
  }
}
```

This goes through the MCP server → `api_service_registry` → **Actual Gemini API**.

---

## 🔄 **THE COMPLETE FLOW**

### **Scenario 1: Direct Python Script (No Cursor)**
```python
# You can use this directly in any Python script!
from packages.api_service_registry.llm import get_api_registry

registry = get_api_registry()
result = registry.call_api(
    provider="gemini",
    endpoint="chat-completion",
    data={"messages": [{"role": "user", "content": "What is AIM-OS?"}]}
)

print(result["data"]["content"])  # Gemini's response!
```

**Flow:**
```
Your Python Script
  ↓
api_service_registry (handles key rotation)
  ↓
Actual Gemini API (Google's servers)
  ↓
Response comes back
```

---

### **Scenario 2: Via MCP Server (Any Client)**
```python
# Client calls MCP server
mcp_client.call_tool("call_api", {
    "provider": "gemini",
    "endpoint": "chat-completion",
    "data": {"messages": [...]}
})
```

**Flow:**
```
Client (Cursor/Electron/Your Script)
  ↓
MCP Server (lucid_mcp_server.py)
  ↓
api_service_registry
  ↓
Actual Gemini API
  ↓
Response comes back through all layers
```

---

## ✅ **KEY POINTS**

1. **The LLM APIs are REAL** - Gemini, Cerebras, etc. are external services you call with API keys
2. **`api_service_registry` is a Python library** - You can use it directly, no Cursor needed
3. **MCP server is just an interface** - It makes the APIs accessible via tools, but you don't NEED it
4. **Cursor is optional** - The MCP server can be used by ANY client, or you can skip it entirely and use `api_service_registry` directly

---

## 🎯 **WHAT WE BUILT**

1. ✅ **`api_service_registry` package** - Python library that calls Gemini/Cerebras APIs
2. ✅ **Key rotation system** - Handles your 22 keys per provider
3. ✅ **HHNI context integration** - Retrieves relevant AIM-OS docs before calling LLM
4. ✅ **MCP server integration** - Makes it accessible via MCP tools (optional)

---

## 💡 **HOW TO USE IT**

### **Option 1: Direct Python (Simplest)**
```python
from packages.api_service_registry.llm import get_api_registry

registry = get_api_registry()
result = registry.call_api("gemini", "chat-completion", data={...})
```

### **Option 2: Via MCP Server**
- Start MCP server: `python lucid_mcp_server.py`
- Call tool: `call_api` with provider="gemini"
- (Cursor can do this, but so can any other client)

---

## 🤔 **YOUR CONFUSION**

You thought this was ONLY for Cursor, but actually:
- ✅ It DOES call Gemini/Cerebras APIs (the real LLM services)
- ✅ The MCP server is just ONE way to access it
- ✅ You can use `api_service_registry` directly in Python scripts
- ✅ Cursor is optional - it's just one possible client

**The actual LLM calls go to Google's Gemini API and Cerebras's API** - those are real external services! 🚀

