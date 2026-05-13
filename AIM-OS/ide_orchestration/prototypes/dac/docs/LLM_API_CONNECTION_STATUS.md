# LLM API Connection Status

**Created:** 2025-01-28  
**Purpose:** Clarify how AIM-OS connects to LLM APIs (OpenAI, Anthropic, Gemini, etc.) and identify missing components

---

## ✅ **ARCHITECTURE IS CORRECT**

The connection flow is properly designed:

```
UI (AdvancedChatPanel)
  ↓
LLMService.chatCompletion()
  ↓
Command Server: POST /mcp/execute
  {
    tool: "call_api",
    arguments: {
      provider: "openai" | "anthropic" | "gemini" | etc.,
      endpoint: "chat-completion",
      method: "POST",
      data: { model, messages, temperature, ... }
    }
  }
  ↓
MCPClient.callTool("call_api", args)
  ↓
MCP Server (lucid_mcp_server.py): call_api()
  ↓
api_service_registry.call_api()  ⚠️ MISSING MODULE
  ↓
Actual LLM API (OpenAI/Anthropic/Gemini/etc.)
```

---

## ❌ **MISSING COMPONENT: `api_service_registry`**

### **The Problem**

The MCP server's `call_api()` function (line 9054 in `lucid_mcp_server.py`) tries to import:

```python
from api_service_registry import get_api_registry
api_registry = get_api_registry()
```

**But this module doesn't exist!**

### **What This Module Should Do**

The `api_service_registry` module should:

1. **Manage API Keys:**
   - Read API keys from environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc.)
   - Provide secure key storage/retrieval
   - Validate keys before use

2. **Call LLM APIs:**
   - **OpenAI:** `POST https://api.openai.com/v1/chat/completions`
   - **Anthropic:** `POST https://api.anthropic.com/v1/messages`
   - **Gemini:** Use Google's Gemini SDK (`google-generativeai`)
   - **Cerebras:** `POST https://api.cerebras.ai/v1/chat/completions`
   - **Minimax:** `POST https://api.minimax.chat/v1/chat/completions`

3. **Handle Responses:**
   - Parse LLM responses
   - Extract text, tokens, latency
   - Return standardized format:
     ```python
     {
       "success": True,
       "data": {
         "text": "...",
         "model": "gpt-4",
         "tokens_used": 150,
         "latency_ms": 1200,
         "confidence": 0.95
       },
       "metadata": {
         "provider": "openai",
         "latency_ms": 1200,
         "cached": False
       }
     }
     ```

4. **Integrate with AIM-OS:**
   - Store API calls in CMC (via `store_memory`)
   - Track confidence with VIF (via `track_confidence`)
   - Index responses in HHNI (if enabled)
   - Link to SEG knowledge graph (if enabled)

---

## 🔧 **IMPLEMENTATION PLAN**

### **Step 1: Create `api_service_registry.py`**

Location: `packages/api_service_registry/api_service_registry.py`

**Core Structure:**
```python
import os
import json
from typing import Dict, Any, Optional
import httpx  # or requests
from datetime import datetime

class APIServiceRegistry:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.clients = self._initialize_clients()
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables"""
        return {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            "cerebras": os.getenv("CEREBRAS_API_KEY"),
            "minimax": os.getenv("MINIMAX_API_KEY"),
            # ... etc
        }
    
    def call_api(
        self,
        provider: str,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        integrate_aimos: bool = True
    ) -> Dict[str, Any]:
        """Call external API and return standardized response"""
        # Route to provider-specific handler
        if provider == "openai" and endpoint == "chat-completion":
            return self._call_openai_chat(data)
        elif provider == "anthropic" and endpoint == "chat-completion":
            return self._call_anthropic_chat(data)
        elif provider == "gemini" and endpoint == "chat-completion":
            return self._call_gemini_chat(data)
        # ... etc
    
    def _call_openai_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call OpenAI chat completion API"""
        import httpx
        
        api_key = self.api_keys.get("openai")
        if not api_key:
            return {"success": False, "error": "OpenAI API key not configured"}
        
        start_time = datetime.now()
        
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": data.get("model", "gpt-4"),
                    "messages": data.get("messages", []),
                    "temperature": data.get("temperature", 0.7),
                    "max_tokens": data.get("max_tokens", 4096)
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return {
                "success": True,
                "data": {
                    "text": result["choices"][0]["message"]["content"],
                    "model": result["model"],
                    "tokens_used": result["usage"]["total_tokens"],
                    "latency_ms": latency_ms,
                    "confidence": 0.9  # Default confidence
                },
                "metadata": {
                    "provider": "openai",
                    "latency_ms": latency_ms,
                    "cached": False
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "provider": "openai",
                    "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
                }
            }
    
    # Similar methods for Anthropic, Gemini, etc.

def get_api_registry() -> APIServiceRegistry:
    """Get or create API service registry singleton"""
    global _api_registry
    if _api_registry is None:
        _api_registry = APIServiceRegistry()
    return _api_registry

_api_registry: Optional[APIServiceRegistry] = None
```

### **Step 2: Install Dependencies**

Add to `requirements.txt` or `pyproject.toml`:
```
httpx>=0.25.0  # For HTTP requests
google-generativeai>=0.3.0  # For Gemini API
anthropic>=0.18.0  # For Anthropic API
```

### **Step 3: Configure API Keys**

Users need to set environment variables:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIzaSy..."
export CEREBRAS_API_KEY="csk-..."
```

Or create a `.env` file (if using `python-dotenv`):
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
```

---

## ✅ **WHAT'S ALREADY WORKING**

1. **UI → Command Server:** ✅ Working
   - `AdvancedChatPanel` calls `LLMService.chatCompletion()`
   - `LLMService` calls `POST /mcp/execute` on Command Server

2. **Command Server → MCP Server:** ✅ Working
   - Command Server routes `/mcp/execute` to `executeMCPTool()`
   - `MCPClient.callTool()` connects to MCP server
   - MCP server receives `call_api` tool call

3. **MCP Server → API Registry:** ❌ **BROKEN**
   - `call_api()` tries to import `api_service_registry`
   - Import fails → returns error: "API service registry not available"

4. **API Registry → LLM APIs:** ❌ **NOT IMPLEMENTED**
   - Module doesn't exist yet

---

## 🎯 **BOTTOM LINE**

**The architecture is correct, but the `api_service_registry` module is missing.**

**Current Status:**
- ✅ UI can send chat requests
- ✅ Command Server can route requests
- ✅ MCP Server can receive requests
- ❌ **LLM API calls fail because `api_service_registry` doesn't exist**

**To Fix:**
1. Create `packages/api_service_registry/api_service_registry.py`
2. Implement provider-specific API callers (OpenAI, Anthropic, Gemini, etc.)
3. Load API keys from environment variables
4. Return standardized response format
5. Test with real API keys

**Once this module exists, the full flow will work:**
```
UI → Command Server → MCP Server → API Registry → LLM API → Response → UI
```

---

## 📚 **REFERENCES**

- **MCP Server `call_api` implementation:** `lucid_mcp_server.py:9054`
- **LLMService implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/llm/LLMService.ts:223`
- **Command Server MCP execution:** `cursor-addon/src/commandServer.ts:439`
- **API Key Status:** `Testing/artifacts/API_KEY_STATUS.md` (shows which keys are working)

---

**Status:** Architecture is correct, but `api_service_registry` module needs to be implemented for LLM API calls to work.

