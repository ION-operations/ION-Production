"""
API Service Registry

Central registry for LLM clients and MCP tool integration.
Provides both LLMClient instances (for agent use) and MCP tool interface.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from .llm_client import LLMClient
from .key_manager import APIKeyManager
from .gemini_client import GeminiClient
from .cerebras_client import CerebrasClient


class APIServiceRegistry:
    """
    Registry for LLM clients and MCP tool integration.
    Provides both LLMClient instances (for agent use) and MCP tool interface.
    
    Phase 1: Gemini + Cerebras
    Phase 2: Anthropic, OpenAI, DeepInfra, Replicate
    """
    
    def __init__(self):
        """Initialize the API service registry."""
        self.key_manager = APIKeyManager()
        
        # Phase 1: Core providers
        self.gemini_client = GeminiClient(self.key_manager)
        self.cerebras_client = CerebrasClient(self.key_manager)
        
        # Phase 2: Expanded providers (implemented later)
        # self.anthropic_client = AnthropicClient(self.key_manager)
        # self.openai_client = OpenAIClient(self.key_manager)
        # self.deepinfra_client = DeepInfraClient(self.key_manager)
        # self.replicate_client = ReplicateClient(self.key_manager)
        
        self._client_registry: Dict[str, LLMClient] = {
            "gemini": self.gemini_client,
            "cerebras": self.cerebras_client,
            # Phase 2: Add other providers
            # "anthropic": self.anthropic_client,
            # "openai": self.openai_client,
            # "deepinfra": self.deepinfra_client,
            # "replicate": self.replicate_client,
        }
    
    def get_client(self, provider: str) -> Optional[LLMClient]:
        """
        Get LLMClient instance for provider (for agent use).
        
        Args:
            provider: Provider name (e.g., 'gemini', 'cerebras')
        
        Returns:
            LLMClient instance, or None if provider not found
        """
        return self._client_registry.get(provider)
    
    def call_api(
        self,
        provider: str,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        hhni_query: Optional[str] = None,
        integrate_aimos: bool = True
    ) -> Dict[str, Any]:
        """
        Call external API and return standardized response (MCP tool interface).
        
        This is the main entry point for MCP tool calls. It handles:
        - Provider routing
        - HHNI context retrieval (if hhni_query provided)
        - Context window validation
        - Key rotation
        - Error handling
        - AIM-OS integration (if enabled)
        
        Args:
            provider: Provider name (e.g., 'gemini', 'cerebras')
            endpoint: Endpoint name (e.g., 'chat-completion')
            method: HTTP method (default: 'POST')
            data: Request data (messages, model, temperature, etc.)
            hhni_query: Optional HHNI retrieval query for context (Sev P0 requirement)
            integrate_aimos: Whether to integrate with AIM-OS systems
        
        Returns:
            Standardized response dict with success, data, error, metadata, aimos
        """
        start_time = time.time()
        data = data or {}
        
        try:
            # HHNI context retrieval (Sev P0 requirement)
            # MCP server handles HHNI retrieval and passes context_items in data
            context_items = data.get("context_items") if data else None
            
            # Context window validation (Sev P0 requirement)
            if context_items:
                # Get provider context window limit
                context_window_limits = {
                    "gemini": 1_000_000,  # Gemini 2.5 Pro supports 1M context
                    "cerebras": 32_768,   # Cerebras models typically have smaller limits
                }
                limit = context_window_limits.get(provider, 32_768)
                
                # Calculate total tokens (context + prompt)
                context_tokens = sum(item.get("tokens", 0) for item in context_items)
                prompt_tokens = sum(len(msg.get("content", "")) // 4 for msg in data.get("messages", []))
                total_tokens = context_tokens + prompt_tokens
                
                # Validate and truncate if needed
                if total_tokens > limit:
                    # TODO: Implement context truncation/prioritization (Phase 2)
                    # For now, log warning
                    pass
            
            # Route to appropriate provider
            if provider == "gemini" and endpoint == "chat-completion":
                result = self._call_gemini_chat(data, context_items=context_items)
            elif provider == "cerebras" and endpoint == "chat-completion":
                result = self._call_cerebras_chat(data, context_items=context_items)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported provider/endpoint: {provider}/{endpoint}",
                    "metadata": {
                        "provider": provider,
                        "endpoint": endpoint,
                        "latency_ms": int((time.time() - start_time) * 1000)
                    }
                }
            
            # Add metadata
            latency_ms = int((time.time() - start_time) * 1000)
            result["metadata"] = result.get("metadata", {})
            result["metadata"].update({
                "provider": provider,
                "endpoint": endpoint,
                "method": method,
                "latency_ms": latency_ms,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # AIM-OS integration will be handled by MCP server
            # (we return the result, MCP server calls integration hooks)
            
            return result
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "provider": provider,
                    "endpoint": endpoint,
                    "method": method,
                    "latency_ms": latency_ms,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
    
    def _call_gemini_chat(
        self, 
        data: Dict[str, Any], 
        context_items: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Call Gemini chat completion API using SDK with key rotation."""
        start_time = time.time()
        messages = data.get("messages", [])
        model = data.get("model", "gemini-2.5-flash")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 8192)
        token_budget = data.get("token_budget")  # For context window validation
        
        # Run async chat method
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            self.gemini_client.chat(
                messages,
                context_items=context_items,
                token_budget=token_budget,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "data": {
                "content": result.get("content", ""),
                "model": result.get("model", model),
                "tokens_used": result.get("tokens_used", 0),
                "provider": "gemini",
                "key_index": result.get("key_index", 0)
            },
            "metadata": {
                "provider": "gemini",
                "latency_ms": latency_ms,
                "cached": False
            }
        }
    
    def _call_cerebras_chat(
        self, 
        data: Dict[str, Any], 
        context_items: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Call Cerebras chat completion API using REST with key rotation."""
        start_time = time.time()
        messages = data.get("messages", [])
        model = data.get("model", "llama3.1-8b")  # Correct Cerebras model name
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 4096)
        token_budget = data.get("token_budget")  # For context window validation
        
        # Run async chat method
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            self.cerebras_client.chat(
                messages,
                context_items=context_items,
                token_budget=token_budget,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "data": {
                "content": result.get("content", ""),
                "model": result.get("model", model),
                "tokens_used": result.get("tokens_used", 0),
                "provider": "cerebras",
                "key_index": result.get("key_index", 0)
            },
            "metadata": {
                "provider": "cerebras",
                "latency_ms": latency_ms,
                "cached": False
            }
        }


# Singleton instance
_api_registry: Optional[APIServiceRegistry] = None


def get_api_registry() -> APIServiceRegistry:
    """
    Get singleton API registry instance.
    
    Returns:
        APIServiceRegistry instance
    """
    global _api_registry
    if _api_registry is None:
        _api_registry = APIServiceRegistry()
    return _api_registry

