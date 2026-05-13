"""
Cerebras Client Implementation

Cerebras Inference API client with 22-key rotation support.
Optimized for: Speed-critical tasks (classification, simple chat, tool formatting)
"""

import httpx
from typing import Dict, Any, List, Optional

from .llm_client import LLMClient
from .key_manager import APIKeyManager


class CerebrasClient(LLMClient):
    """
    Implementation for Cerebras Inference API.
    Optimized for speed and high TPD (Tokens Per Day).
    Optimized for: Speed-critical tasks (classification, simple chat, tool formatting)
    """
    
    def __init__(self, key_manager: APIKeyManager):
        """
        Initialize Cerebras client with key manager.
        
        Args:
            key_manager: APIKeyManager instance for key rotation
        """
        self.key_manager = key_manager
        self.base_url = "https://api.cerebras.ai/v1"
    
    def get_provider(self) -> str:
        """Returns provider name."""
        return "cerebras"
    
    def get_model(self) -> str:
        """Returns default model name."""
        return "llama3.1-8b"  # Correct model name from Cerebras API
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Simple text completion.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)
        
        Returns:
            Generated text response
        """
        model_name = kwargs.get("model", self.get_model())
        key = self.key_manager.get_key("cerebras")
        
        if not key:
            raise RuntimeError("No available Cerebras API keys")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 4096)
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract response text
                text = result["choices"][0]["message"]["content"]
                
                # Record usage
                tokens = result.get("usage", {}).get("total_tokens", 0)
                self.key_manager.record_usage(key, tokens=tokens, error=False)
                
                return text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit - rotate key and retry
                self.key_manager.mark_quota_exhausted(key)
                self.key_manager.mark_rate_limited(key, limited=True)
                # Retry with next key
                return await self.complete(prompt, **kwargs)
            # Record error
            self.key_manager.record_usage(key, error=True)
            raise
        except Exception as e:
            # Record error
            self.key_manager.record_usage(key, error=True)
            raise
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        context_items: Optional[List[Dict[str, Any]]] = None,
        token_budget: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat-based completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            context_items: Optional HHNI retrieval context items (Sev P0 requirement)
            token_budget: Optional token budget for context window validation (Sev P0 requirement)
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)
        
        Returns:
            Response dict with 'content', 'model', 'tokens_used', etc.
        """
        # Format context items into prompt if provided (Sev P0 requirement)
        if context_items:
            # TODO: Implement provider-specific context formatting (Sev P1)
            # For now, append context to first user message
            context_text = "\n\n".join(item.get("content", "") for item in context_items)
            if messages and messages[0].get("role") == "user":
                messages[0]["content"] = f"{context_text}\n\n{messages[0]['content']}"
            elif messages:
                # Insert context as system message
                messages.insert(0, {"role": "system", "content": context_text})
        model_name = kwargs.get("model", self.get_model())
        key = self.key_manager.get_key("cerebras")
        
        if not key:
            raise RuntimeError("No available Cerebras API keys")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 4096)
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract response
                message = result["choices"][0]["message"]
                
                # Record usage
                tokens = result.get("usage", {}).get("total_tokens", 0)
                self.key_manager.record_usage(key, tokens=tokens, error=False)
                
                return {
                    "content": message.get("content", ""),
                    "model": model_name,
                    "tokens_used": tokens,
                    "provider": "cerebras",
                    "key_index": self.key_manager.current_index.get("cerebras", 0)
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit - rotate key and retry
                self.key_manager.mark_quota_exhausted(key)
                self.key_manager.mark_rate_limited(key, limited=True)
                # Retry with next key
                return await self.chat(messages, **kwargs)
            # Record error
            self.key_manager.record_usage(key, error=True)
            raise
        except Exception as e:
            # Record error
            self.key_manager.record_usage(key, error=True)
            raise

