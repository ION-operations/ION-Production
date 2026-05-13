# LLM API Implementation Plan - Gemini + Cerebras (MVP)

**Created:** 2025-01-28  
**Status:** 🟡 **READY FOR IMPLEMENTATION**  
**Priority:** P0 - Critical for chat/IDE MVP  
**Scope:** Phase 1: Gemini + Cerebras (perfect system), Phase 2: Full expansion (Anthropic, OpenAI, DeepInfra, Replicate)

---

## 🎯 **SCOPE**

**Phase 1: MVP (Start Here) - Perfect the System:**
- ✅ **Gemini API** (using `google-generativeai` SDK)
- ✅ **Cerebras API** (using REST API)
- **Goal:** Perfect the architecture, key rotation, and integration patterns

**Phase 2: Expansion - Full Provider Support:**
- ✅ **Anthropic API** (Claude - REST API)
- ✅ **OpenAI API** (GPT-4, GPT-3.5 - REST API)
- ✅ **DeepInfra API** (Various models - REST API)
- ✅ **Replicate API** (Open source models - REST API)
- **Goal:** Complete provider ecosystem with all major LLMs

**Rationale:**
- **Start with Gemini + Cerebras:** Perfect the system architecture first
- **Then expand:** Add all providers using the same proven patterns
- **Strategic complementarity:** Each provider has strengths
  - **Gemini:** Context-heavy tasks (1M tokens, research, planning, synthesis)
  - **Cerebras:** Speed-critical tasks (10-20x faster, classification, simple chat)
  - **Anthropic:** High-quality reasoning (Claude, validation, complex analysis)
  - **OpenAI:** Industry standard (GPT-4, function calling, wide compatibility)
  - **DeepInfra:** Fast inference (alternative to Cerebras, cost-effective)
  - **Replicate:** Open source models (flexibility, self-hosted options)

**Strategic Model-to-Agent Mapping:**
- **Orchestrator/Task Classifier:** Cerebras (speed, low-context)
- **ConciseReplyAgent:** Cerebras (speed, low-cost, high-volume)
- **DeepResearchAgent:** Gemini Pro/Flash (1M context for documents/code)
- **APOEAgent/SDFAgent:** Gemini Flash (large context for file reading)
- **RelationAgent:** Gemini Pro (complex reasoning, synthesis)
- **DocAgent:** Gemini Pro (reasoning + context for merging docs)
- **VerifierAgent:** Gemini Pro (high-level reasoning, sanity checks)

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Core API Registry (Day 1-2)**

#### **1.1 Create `api_service_registry` Module**

**Location:** `packages/api_service_registry/api_service_registry.py`

**Structure:**
```python
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict
from abc import ABC, abstractmethod
import httpx
import google.generativeai as genai

# ============================================================================
# LLMClient Abstraction (Phase 4 Pattern)
# ============================================================================

class LLMClient(ABC):
    """Abstract base class for all LLM API clients."""
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generates a simple text completion."""
        pass
    
    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> dict:
        """Generates a chat-based completion."""
        pass
    
    @abstractmethod
    def get_provider(self) -> str:
        """Returns provider name (e.g., 'gemini', 'cerebras')."""
        pass
    
    @abstractmethod
    def get_model(self) -> str:
        """Returns default model name."""
        pass

# ============================================================================
# Key Pool Manager (22-Key Strategy)
# ============================================================================

class APIKeyManager:
    """Manages multiple API keys per provider with rotation and quota tracking"""
    
    def __init__(self):
        self.keys: Dict[str, List[str]] = {}  # provider -> [key1, key2, ...]
        self.current_index: Dict[str, int] = defaultdict(int)  # provider -> current key index
        self.usage: Dict[str, Dict[str, Any]] = {}  # key -> {requests, tokens, errors, last_used}
        self.quota_limits: Dict[str, Dict[str, int]] = {}  # key -> {requests_per_minute, tokens_per_day, etc.}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment variables (supports multiple keys)"""
        # Support multiple keys: GEMINI_API_KEY_1, GEMINI_API_KEY_2, ..., GEMINI_API_KEY_22
        # Also support single key: GEMINI_API_KEY or GOOGLE_API_KEY
        self.keys["gemini"] = []
        self.keys["cerebras"] = []
        
        # Load Gemini keys
        single_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if single_key:
            self.keys["gemini"].append(single_key)
        
        # Load multiple Gemini keys
        for i in range(1, 23):  # Support up to 22 keys
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and key not in self.keys["gemini"]:
                self.keys["gemini"].append(key)
        
        # Load Cerebras keys
        single_key = os.getenv("CEREBRAS_API_KEY")
        if single_key:
            self.keys["cerebras"].append(single_key)
        
        # Load multiple Cerebras keys
        for i in range(1, 23):  # Support up to 22 keys
            key = os.getenv(f"CEREBRAS_API_KEY_{i}")
            if key and key not in self.keys["cerebras"]:
                self.keys["cerebras"].append(key)
        
        # Phase 2: Load other provider keys (when implemented)
        # Anthropic keys
        self.keys["anthropic"] = []
        single_key = os.getenv("ANTHROPIC_API_KEY")
        if single_key:
            self.keys["anthropic"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"ANTHROPIC_API_KEY_{i}")
            if key and key not in self.keys["anthropic"]:
                self.keys["anthropic"].append(key)
        
        # OpenAI keys
        self.keys["openai"] = []
        single_key = os.getenv("OPENAI_API_KEY")
        if single_key:
            self.keys["openai"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"OPENAI_API_KEY_{i}")
            if key and key not in self.keys["openai"]:
                self.keys["openai"].append(key)
        
        # DeepInfra keys
        self.keys["deepinfra"] = []
        single_key = os.getenv("DEEPINFRA_API_KEY")
        if single_key:
            self.keys["deepinfra"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"DEEPINFRA_API_KEY_{i}")
            if key and key not in self.keys["deepinfra"]:
                self.keys["deepinfra"].append(key)
        
        # Replicate keys
        self.keys["replicate"] = []
        single_key = os.getenv("REPLICATE_API_KEY")
        if single_key:
            self.keys["replicate"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"REPLICATE_API_KEY_{i}")
            if key and key not in self.keys["replicate"]:
                self.keys["replicate"].append(key)
        
        # Initialize usage tracking
        for provider, keys in self.keys.items():
            for key in keys:
                self.usage[key] = {
                    "requests": 0,
                    "tokens": 0,
                    "errors": 0,
                    "last_used": None,
                    "quota_exhausted": False,
                    "rate_limited": False
                }
    
    def get_key(self, provider: str, rotate_on_error: bool = True) -> Optional[str]:
        """Get current API key for provider, with rotation support"""
        if provider not in self.keys or not self.keys[provider]:
            return None
        
        # Try current key
        current_index = self.current_index[provider]
        current_key = self.keys[provider][current_index]
        
        # Check if current key is exhausted
        if self.usage[current_key].get("quota_exhausted") and rotate_on_error:
            # Rotate to next key
            return self.rotate_key(provider)
        
        return current_key
    
    def rotate_key(self, provider: str) -> Optional[str]:
        """Rotate to next API key for provider"""
        if provider not in self.keys or not self.keys[provider]:
            return None
        
        # Mark current key as exhausted
        current_index = self.current_index[provider]
        current_key = self.keys[provider][current_index]
        self.usage[current_key]["quota_exhausted"] = True
        
        # Find next available key
        total_keys = len(self.keys[provider])
        for _ in range(total_keys):
            self.current_index[provider] = (self.current_index[provider] + 1) % total_keys
            next_key = self.keys[provider][self.current_index[provider]]
            
            # If key is not exhausted, use it
            if not self.usage[next_key].get("quota_exhausted"):
                return next_key
        
        # All keys exhausted
        return None
    
    def record_usage(self, key: str, tokens: int = 0, error: bool = False):
        """Record API usage for a key"""
        if key not in self.usage:
            return
        
        self.usage[key]["requests"] += 1
        self.usage[key]["tokens"] += tokens
        if error:
            self.usage[key]["errors"] += 1
        self.usage[key]["last_used"] = datetime.now()
    
    def mark_quota_exhausted(self, key: str):
        """Mark a key as quota exhausted"""
        if key in self.usage:
            self.usage[key]["quota_exhausted"] = True
    
    def mark_rate_limited(self, key: str, limited: bool = True):
        """Mark a key as rate limited"""
        if key in self.usage:
            self.usage[key]["rate_limited"] = limited

# ============================================================================
# Gemini Client Implementation
# ============================================================================

class GeminiClient(LLMClient):
    """
    Implementation for Google Gemini API.
    Uses a key pool to manage the 22+ free-tier keys.
    Optimized for: Context-heavy tasks (research, planning, synthesis)
    """
    
    def __init__(self, key_manager: APIKeyManager):
        self.key_manager = key_manager
        self._initialize_sdk()
    
    def _initialize_sdk(self):
        """Initialize Gemini SDK with first available key"""
        gemini_key = self.key_manager.get_key("gemini", rotate_on_error=False)
        if gemini_key:
            genai.configure(api_key=gemini_key)
    
    def get_provider(self) -> str:
        return "gemini"
    
    def get_model(self) -> str:
        return "gemini-1.5-flash"  # Free tier compatible
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Simple text completion"""
        model_name = kwargs.get("model", self.get_model())
        key = self.key_manager.get_key("gemini")
        
        if not key:
            raise RuntimeError("No available Gemini API keys")
        
        # Reconfigure SDK with current key
        genai.configure(api_key=key)
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_output_tokens": kwargs.get("max_tokens", 4096),
                }
            )
            
            # Record usage
            tokens = self._estimate_tokens(response.text)
            self.key_manager.record_usage(key, tokens=tokens, error=False)
            
            return response.text
        except Exception as e:
            # Handle quota/rate limit errors
            if self._is_quota_error(e):
                self.key_manager.mark_quota_exhausted(key)
                # Retry with next key
                return await self.complete(prompt, **kwargs)
            raise
    
    async def chat(self, messages: list[dict], **kwargs) -> dict:
        """Chat-based completion"""
        # Convert messages to prompt format
        prompt = self._messages_to_prompt(messages)
        text = await self.complete(prompt, **kwargs)
        return {"role": "model", "content": text}
    
    def _is_quota_error(self, error: Exception) -> bool:
        """Check if error is quota/rate limit related"""
        error_str = str(error).lower()
        return "quota" in error_str or "429" in error_str or "rate limit" in error_str
    
    def _messages_to_prompt(self, messages: list) -> str:
        """Convert messages list to Gemini prompt format"""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n".join(prompt_parts)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text) // 4

# ============================================================================
# Cerebras Client Implementation
# ============================================================================

class CerebrasClient(LLMClient):
    """
    Implementation for Cerebras Inference API.
    Optimized for speed and high TPD (Tokens Per Day).
    Optimized for: Speed-critical tasks (classification, simple chat, tool formatting)
    """
    
    def __init__(self, key_manager: APIKeyManager):
        self.key_manager = key_manager
    
    def get_provider(self) -> str:
        return "cerebras"
    
    def get_model(self) -> str:
        return "llama3.1-8b"
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Simple text completion"""
        model_name = kwargs.get("model", self.get_model())
        key = self.key_manager.get_key("cerebras")
        
        if not key:
            raise RuntimeError("No available Cerebras API keys")
        
        try:
            response = httpx.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 4096)
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Record usage
            tokens = result["usage"]["total_tokens"]
            self.key_manager.record_usage(key, tokens=tokens, error=False)
            
            return result["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit - rotate key and retry
                self.key_manager.mark_quota_exhausted(key)
                return await self.complete(prompt, **kwargs)
            raise
        except Exception as e:
            self.key_manager.record_usage(key, error=True)
            raise
    
    async def chat(self, messages: list[dict], **kwargs) -> dict:
        """Chat-based completion"""
        model_name = kwargs.get("model", self.get_model())
        key = self.key_manager.get_key("cerebras")
        
        if not key:
            raise RuntimeError("No available Cerebras API keys")
        
        try:
            response = httpx.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 4096)
                },
                timeout=60.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Record usage
            tokens = result["usage"]["total_tokens"]
            self.key_manager.record_usage(key, tokens=tokens, error=False)
            
            return result["choices"][0]["message"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit - rotate key and retry
                self.key_manager.mark_quota_exhausted(key)
                return await self.chat(messages, **kwargs)
            raise
        except Exception as e:
            self.key_manager.record_usage(key, error=True)
            raise

# ============================================================================
# API Service Registry (MCP Tool Integration)
# ============================================================================

class APIServiceRegistry:
    """
    Registry for LLM clients and MCP tool integration.
    Provides both LLMClient instances (for agent use) and MCP tool interface.
    
    Phase 1: Gemini + Cerebras
    Phase 2: Anthropic, OpenAI, DeepInfra, Replicate
    """
    
    def __init__(self):
        self.key_manager = APIKeyManager()
        
        # Phase 1: Core providers
        self.gemini_client = GeminiClient(self.key_manager)
        self.cerebras_client = CerebrasClient(self.key_manager)
        
        # Phase 2: Expanded providers (implemented later)
        # self.anthropic_client = AnthropicClient(self.key_manager)
        # self.openai_client = OpenAIClient(self.key_manager)
        # self.deepinfra_client = DeepInfraClient(self.key_manager)
        # self.replicate_client = ReplicateClient(self.key_manager)
        
        self._client_registry = {
            "gemini": self.gemini_client,
            "cerebras": self.cerebras_client,
            # Phase 2: Add other providers
            # "anthropic": self.anthropic_client,
            # "openai": self.openai_client,
            # "deepinfra": self.deepinfra_client,
            # "replicate": self.replicate_client,
        }
    
    def get_client(self, provider: str) -> Optional[LLMClient]:
        """Get LLMClient instance for provider (for agent use)"""
        return self._client_registry.get(provider)
    
    def call_api(
        self,
        provider: str,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        integrate_aimos: bool = True
    ) -> Dict[str, Any]:
        """Call external API and return standardized response (MCP tool interface)"""
        if provider == "gemini" and endpoint == "chat-completion":
            return self._call_gemini_chat(data)
        elif provider == "cerebras" and endpoint == "chat-completion":
            return self._call_cerebras_chat(data)
        else:
            return {
                "success": False,
                "error": f"Unsupported provider/endpoint: {provider}/{endpoint}"
            }
    
    def _call_gemini_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Gemini chat completion API using SDK with key rotation"""
        start_time = datetime.now()
        max_retries = len(self.key_manager.keys.get("gemini", [])) or 1
        
        for attempt in range(max_retries):
            # Get current key (rotates if previous key exhausted)
            api_key = self.key_manager.get_key("gemini", rotate_on_error=(attempt > 0))
            if not api_key:
                return {
                    "success": False,
                    "error": "No available Gemini API keys",
                    "metadata": {
                        "provider": "gemini",
                        "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
                    }
                }
            
            try:
                # Reconfigure SDK with current key
                genai.configure(api_key=api_key)
                
                # Use free-tier compatible model (may not have full 1M context)
                model_name = data.get("model", "gemini-1.5-flash")  # Default to Flash for free tier
                
                # Check if requested model is available (free tier may not have Pro)
                requested_model = data.get("model", "gemini-2.0-flash-exp")
                if "pro" in requested_model.lower() and "flash" not in requested_model.lower():
                    # Free tier may not have Pro - fallback to Flash
                    model_name = "gemini-1.5-flash"
                
                model = genai.GenerativeModel(model_name)
                
                # Convert messages to Gemini format
                messages = data.get("messages", [])
                prompt = self._messages_to_prompt(messages)
                
                # Generate content
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": data.get("temperature", 0.7),
                        "max_output_tokens": data.get("max_tokens", 4096),
                    }
                )
                
                latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                tokens_used = self._estimate_tokens(response.text)
                
                # Record successful usage
                self.key_manager.record_usage(api_key, tokens=tokens_used, error=False)
                
                return {
                    "success": True,
                    "data": {
                        "text": response.text,
                        "model": model_name,
                        "tokens_used": tokens_used,
                        "latency_ms": latency_ms,
                        "confidence": 0.9,
                        "api_key_index": self.key_manager.current_index["gemini"]
                    },
                    "metadata": {
                        "provider": "gemini",
                        "latency_ms": latency_ms,
                        "cached": False,
                        "key_rotated": attempt > 0
                    }
                }
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for quota/rate limit errors
                if "quota" in error_str or "429" in error_str or "rate limit" in error_str:
                    # Mark key as exhausted and try next key
                    self.key_manager.mark_quota_exhausted(api_key)
                    self.key_manager.mark_rate_limited(api_key, limited=True)
                    self.key_manager.record_usage(api_key, error=True)
                    
                    # Try next key if available
                    if attempt < max_retries - 1:
                        continue
                
                # Other errors - record and return
                self.key_manager.record_usage(api_key, error=True)
                return {
                    "success": False,
                    "error": str(e),
                    "metadata": {
                        "provider": "gemini",
                        "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                        "api_key_index": self.key_manager.current_index["gemini"]
                    }
                }
        
        # All keys exhausted
        return {
            "success": False,
            "error": "All Gemini API keys exhausted",
            "metadata": {
                "provider": "gemini",
                "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
        }
    
    def _call_cerebras_chat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Cerebras chat completion API using REST with key rotation"""
        start_time = datetime.now()
        max_retries = len(self.key_manager.keys.get("cerebras", [])) or 1
        
        for attempt in range(max_retries):
            # Get current key (rotates if previous key exhausted)
            api_key = self.key_manager.get_key("cerebras", rotate_on_error=(attempt > 0))
            if not api_key:
                return {
                    "success": False,
                    "error": "No available Cerebras API keys",
                    "metadata": {
                        "provider": "cerebras",
                        "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
                    }
                }
            
            try:
                response = httpx.post(
                    "https://api.cerebras.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": data.get("model", "llama3.1-8b"),
                        "messages": data.get("messages", []),
                        "temperature": data.get("temperature", 0.7),
                        "max_tokens": data.get("max_tokens", 4096)
                    },
                    timeout=60.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                tokens_used = result["usage"]["total_tokens"]
                
                # Record successful usage
                self.key_manager.record_usage(api_key, tokens=tokens_used, error=False)
                
                return {
                    "success": True,
                    "data": {
                        "text": result["choices"][0]["message"]["content"],
                        "model": result["model"],
                        "tokens_used": tokens_used,
                        "latency_ms": latency_ms,
                        "confidence": 0.9,
                        "api_key_index": self.key_manager.current_index["cerebras"]
                    },
                    "metadata": {
                        "provider": "cerebras",
                        "latency_ms": latency_ms,
                        "cached": False,
                        "key_rotated": attempt > 0
                    }
                }
            except httpx.HTTPStatusError as e:
                error_str = str(e).lower()
                status_code = e.response.status_code
                
                # Check for quota/rate limit errors (429)
                if status_code == 429 or "quota" in error_str or "rate limit" in error_str:
                    # Mark key as exhausted and try next key
                    self.key_manager.mark_quota_exhausted(api_key)
                    self.key_manager.mark_rate_limited(api_key, limited=True)
                    self.key_manager.record_usage(api_key, error=True)
                    
                    # Try next key if available
                    if attempt < max_retries - 1:
                        continue
                
                # Other HTTP errors - record and return
                self.key_manager.record_usage(api_key, error=True)
                return {
                    "success": False,
                    "error": f"HTTP {status_code}: {str(e)}",
                    "metadata": {
                        "provider": "cerebras",
                        "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                        "api_key_index": self.key_manager.current_index["cerebras"]
                    }
                }
            except Exception as e:
                # Other errors - record and return
                self.key_manager.record_usage(api_key, error=True)
                return {
                    "success": False,
                    "error": str(e),
                    "metadata": {
                        "provider": "cerebras",
                        "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                        "api_key_index": self.key_manager.current_index["cerebras"]
                    }
                }
        
        # All keys exhausted
        return {
            "success": False,
            "error": "All Cerebras API keys exhausted",
            "metadata": {
                "provider": "cerebras",
                "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
        }
    
    def _messages_to_prompt(self, messages: list) -> str:
        """Convert messages list to Gemini prompt format"""
        # Simple conversion - can be enhanced later
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n".join(prompt_parts)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # ~4 characters per token for English text
        return len(text) // 4

def get_api_registry() -> APIServiceRegistry:
    """Get or create API service registry singleton"""
    global _api_registry
    if _api_registry is None:
        _api_registry = APIServiceRegistry()
    return _api_registry

_api_registry: Optional[APIServiceRegistry] = None
```

#### **1.2 Install Dependencies**

**Add to `requirements.txt` or `pyproject.toml`:**
```
httpx>=0.25.0  # For Cerebras REST API
google-generativeai>=0.3.0  # For Gemini SDK
```

#### **1.3 Configure API Keys (Multiple Keys Supported)**

**Environment Variables (Single Key):**
```bash
export GEMINI_API_KEY="AIzaSy..."  # Or GOOGLE_API_KEY
export CEREBRAS_API_KEY="csk-..."
```

**Environment Variables (Multiple Keys - Up to 22 per provider):**
```bash
# Gemini keys (up to 22)
export GEMINI_API_KEY_1="AIzaSy..."
export GEMINI_API_KEY_2="AIzaSy..."
# ... up to GEMINI_API_KEY_22

# Cerebras keys (up to 22)
export CEREBRAS_API_KEY_1="csk-..."
export CEREBRAS_API_KEY_2="csk-..."
# ... up to CEREBRAS_API_KEY_22

# Phase 2: Other providers (up to 22 keys each)
# Anthropic keys
export ANTHROPIC_API_KEY_1="sk-ant-..."
export ANTHROPIC_API_KEY_2="sk-ant-..."
# ... up to ANTHROPIC_API_KEY_22

# OpenAI keys
export OPENAI_API_KEY_1="sk-..."
export OPENAI_API_KEY_2="sk-..."
# ... up to OPENAI_API_KEY_22

# DeepInfra keys
export DEEPINFRA_API_KEY_1="..."
export DEEPINFRA_API_KEY_2="..."
# ... up to DEEPINFRA_API_KEY_22

# Replicate keys
export REPLICATE_API_KEY_1="r8_..."
export REPLICATE_API_KEY_2="r8_..."
# ... up to REPLICATE_API_KEY_22
```

**Or create `.env` file:**
```
# Single keys (fallback)
GEMINI_API_KEY=AIzaSy...
CEREBRAS_API_KEY=csk-...

# Multiple keys (up to 22 per provider)
GEMINI_API_KEY_1=AIzaSy...
GEMINI_API_KEY_2=AIzaSy...
GEMINI_API_KEY_3=AIzaSy...
# ... etc

CEREBRAS_API_KEY_1=csk-...
CEREBRAS_API_KEY_2=csk-...
CEREBRAS_API_KEY_3=csk-...
# ... etc

# Phase 2: Other providers (up to 22 keys each)
ANTHROPIC_API_KEY_1=sk-ant-...
ANTHROPIC_API_KEY_2=sk-ant-...
# ... etc

OPENAI_API_KEY_1=sk-...
OPENAI_API_KEY_2=sk-...
# ... etc

DEEPINFRA_API_KEY_1=...
DEEPINFRA_API_KEY_2=...
# ... etc

REPLICATE_API_KEY_1=r8_...
REPLICATE_API_KEY_2=r8_...
# ... etc
```

**Key Rotation Behavior:**
- Automatically rotates to next key when quota/rate limit hit
- Tracks usage per key (requests, tokens, errors)
- Marks keys as exhausted when limits reached
- Falls back to next available key
- Supports up to 22 keys per provider
- **Phase 1:** 44 total keys (22 Gemini + 22 Cerebras)
- **Phase 2:** 132 total keys (22 × 6 providers)

---

### **Phase 2: MCP Server Integration (Day 2)**

#### **2.1 Update MCP Server**

**File:** `lucid_mcp_server.py`

**Current Status:**
- `call_api()` function exists (line 9054)
- Tries to import `api_service_registry` (fails)
- Returns error: "API service registry not available"

**Update:**
- Ensure `api_service_registry` module is in Python path
- Verify import works
- Test `call_api` tool with Gemini and Cerebras

---

### **Phase 3: Testing (Day 2-3)**

#### **3.1 Unit Tests**

**File:** `packages/api_service_registry/tests/test_api_registry.py`

**Test Cases:**
- Gemini API call (success)
- Cerebras API call (success)
- Missing API key (error)
- Invalid API key (error)
- Network failure (error)
- Timeout handling

#### **3.2 Integration Tests**

**Test Flow:**
1. UI → LLMService → Command Server → MCP Server → `call_api` → Gemini/Cerebras
2. Verify response flows back correctly
3. Verify AIM-OS integration (CMC, VIF, TCS)

---

### **Phase 4: Provider Selection Logic (Day 3)**

#### **4.1 Auto-Selection Strategy**

**Strategic Model Routing (Based on Gemini Analysis):**
- **Speed-Critical Tasks:** Cerebras (classification, simple chat, tool formatting)
- **Context-Heavy Tasks:** Gemini (research, planning, synthesis, reasoning)
- **Agent-Based Routing:** Each agent gets preferred client based on task type
- **User Override:** Allow user to select in UI if needed

**Agent-Specific Routing:**
- **Orchestrator/Task Classifier:** Cerebras (speed)
- **ConciseReplyAgent:** Cerebras (speed, low-cost)
- **DeepResearchAgent:** Gemini Pro/Flash (1M context)
- **APOEAgent/SDFAgent:** Gemini Flash (large context for files)
- **RelationAgent:** Gemini Pro (complex reasoning)
- **DocAgent:** Gemini Pro (reasoning + context)
- **VerifierAgent:** Gemini Pro (high-level reasoning)

**Future Enhancement:**
- Dynamic routing based on task complexity
- Cost-based selection
- Performance-based selection
- Load balancing across keys

---

## 📊 **API KEY STATUS & MULTI-KEY SUPPORT**

**From `Testing/artifacts/API_KEY_STATUS.md`:**

### **Gemini** ✅
- **Model:** `gemini-2.0-flash-exp` (free tier - limited 1M context access)
- **API Keys:** Up to 22 keys from different accounts
- **Status:** Fully functional
- **Free Tier Limits:** 
  - Limited access to 1M context models
  - Rate limits per key
  - Quota limits per account
- **Speed:** ~100-200 tokens/sec
- **Use Case:** Complex reasoning, high-quality outputs
- **Key Rotation:** Required to overcome per-key/account limits

### **Cerebras** ✅
- **Model:** `llama3.1-8b` (also available: 70b, 405b)
- **API Keys:** Up to 22 keys from different accounts
- **Status:** Fully functional
- **Speed:** ~2000+ tokens/sec (10-20x faster than Gemini)
- **Cost:** Cheaper than most providers
- **Use Case:** Speed-critical tasks, simple classification
- **Key Rotation:** Required to overcome per-key/account limits

### **Multi-Key Strategy:**
- **Track usage per key:** Monitor requests, tokens, errors per key
- **Rotate keys:** Automatically switch to next key when limits hit
- **Load balancing:** Distribute requests across available keys
- **Quota monitoring:** Track quota usage per key/account
- **Graceful fallback:** Switch to backup key when primary exhausted

---

## 🎯 **SUCCESS CRITERIA**

- [ ] `api_service_registry` module created and working
- [ ] Gemini API calls working (via SDK)
- [ ] Cerebras API calls working (via REST)
- [ ] **Multi-key support working (up to 22 keys per provider)**
- [ ] **Key rotation working (auto-rotate on quota/rate limit)**
- [ ] **Usage tracking per key (requests, tokens, errors)**
- [ ] **Free tier model detection (fallback to Flash if Pro unavailable)**
- [ ] MCP Server `call_api` tool working
- [ ] UI → Command Server → MCP Server → LLM API flow working
- [ ] Error handling working (missing keys, network failures, quota exhaustion)
- [ ] Basic AIM-OS integration (CMC storage, VIF tracking)

---

## 🚀 **NEXT STEPS**

1. **Create `api_service_registry` module** (Phase 1)
2. **Test with real API keys** (Phase 3)
3. **Integrate with MCP Server** (Phase 2)
4. **Test end-to-end flow** (Phase 3)
5. **Add provider selection logic** (Phase 4)

---

## 📚 **REFERENCES**

- **API Key Status:** `Testing/artifacts/API_KEY_STATUS.md`
- **MCP Server:** `lucid_mcp_server.py:9054`
- **LLMService:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/llm/LLMService.ts:223`
- **Architecture Discussion:** `AETHER_CODEX_CHAT_IDE_ARCHITECTURE_DISCUSSION.md`
- **LLM API Status:** `LLM_API_CONNECTION_STATUS.md`
- **Strategic Routing Guide:** `LLM_STRATEGIC_MODEL_ROUTING.md` ⭐ **NEW** - Model-to-agent mapping strategy

---

## 🔮 **PHASE 2: FULL PROVIDER EXPANSION**

After Phase 1 (Gemini + Cerebras) is working perfectly:

### **Phase 2.1: Anthropic (Claude) Support**

**Implementation:**
- REST API client (`POST https://api.anthropic.com/v1/messages`)
- Support for Claude 3.5 Sonnet, Opus, Haiku
- Multi-key rotation (up to 22 keys)
- Streaming support

**Use Cases:**
- High-quality reasoning
- Validation tasks
- Complex analysis
- Alternative to Gemini for quality

### **Phase 2.2: OpenAI Support**

**Implementation:**
- REST API client (`POST https://api.openai.com/v1/chat/completions`)
- Support for GPT-4, GPT-3.5 Turbo
- Multi-key rotation (up to 22 keys)
- Function calling support
- Streaming support

**Use Cases:**
- Industry standard compatibility
- Function calling tasks
- Wide ecosystem compatibility
- Alternative to Gemini for compatibility

### **Phase 2.3: DeepInfra Support**

**Implementation:**
- REST API client (`POST https://api.deepinfra.com/v1/openai/chat/completions`)
- Support for various models (Llama, Mistral, etc.)
- Multi-key rotation (up to 22 keys)
- Fast inference alternative

**Use Cases:**
- Fast inference (alternative to Cerebras)
- Cost-effective operations
- Open source model access
- Load distribution

### **Phase 2.4: Replicate Support**

**Implementation:**
- REST API client (`POST https://api.replicate.com/v1/predictions`)
- Support for open source models
- Multi-key rotation (up to 22 keys)
- Custom model deployment

**Use Cases:**
- Open source model access
- Custom model deployment
- Flexibility and control
- Self-hosted options

### **Phase 2.5: Advanced Features**

- **Advanced provider selection:** Task-based, cost-based, performance-based
- **Cost tracking:** Per key/account/provider
- **Response caching:** Reduce API calls
- **Quota monitoring dashboard:** Real-time usage tracking
- **Key health monitoring:** Automatic key status tracking
- **Automatic key rotation scheduling:** Proactive rotation
- **Load balancing:** Distribute requests across providers
- **Fallback chains:** Provider → Provider → Provider

---

**Status:** 🟡 **READY FOR IMPLEMENTATION**  
**Timeline:** 
- **Phase 1 (MVP):** 2-3 days (Gemini + Cerebras)
- **Phase 2 (Expansion):** 3-5 days (Anthropic, OpenAI, DeepInfra, Replicate)
- **Total:** ~1 week for complete provider ecosystem

