"""
Gemini Client Implementation

Google Gemini API client with 22-key rotation support.
Optimized for: Context-heavy tasks (research, planning, synthesis)
"""

import os
from typing import Dict, Any, List, Optional
import google.generativeai as genai

from .llm_client import LLMClient
from .key_manager import APIKeyManager


class GeminiClient(LLMClient):
    """
    Implementation for Google Gemini API.
    Uses a key pool to manage the 22+ free-tier keys.
    Optimized for: Context-heavy tasks (research, planning, synthesis)
    """
    
    def __init__(self, key_manager: APIKeyManager):
        """
        Initialize Gemini client with key manager.
        
        Args:
            key_manager: APIKeyManager instance for key rotation
        """
        self.key_manager = key_manager
        self._initialize_sdk()
    
    def _initialize_sdk(self):
        """Initialize Gemini SDK with first available key."""
        gemini_key = self.key_manager.get_key("gemini", rotate_on_error=False)
        if gemini_key:
            genai.configure(api_key=gemini_key)
    
    def get_provider(self) -> str:
        """Returns provider name."""
        return "gemini"
    
    def get_model(self) -> str:
        """Returns default model name (Gemini 2.5 Flash for free tier)."""
        return "gemini-2.5-flash"
    
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
        key = self.key_manager.get_key("gemini")
        
        if not key:
            raise RuntimeError("No available Gemini API keys")
        
        # Reconfigure SDK with current key
        genai.configure(api_key=key)
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 8192),
                )
            )
            
            # Extract text from response
            text = response.text if hasattr(response, 'text') else str(response)
            
            # Record usage (estimate tokens)
            tokens = self._estimate_tokens(prompt, text)
            self.key_manager.record_usage(key, tokens=tokens, error=False)
            
            return text
        except Exception as e:
            # Handle quota/rate limit errors
            if self._is_quota_error(e):
                self.key_manager.mark_quota_exhausted(key)
                # Retry with next key
                return await self.complete(prompt, **kwargs)
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
            # For now, append context to system message or first user message
            context_text = "\n\n".join(item.get("content", "") for item in context_items)
            if messages and messages[0].get("role") == "user":
                messages[0]["content"] = f"{context_text}\n\n{messages[0]['content']}"
            elif messages:
                # Insert context as system message
                messages.insert(0, {"role": "system", "content": context_text})
        model_name = kwargs.get("model", self.get_model())
        key = self.key_manager.get_key("gemini")
        
        if not key:
            raise RuntimeError("No available Gemini API keys")
        
        # Reconfigure SDK with current key
        genai.configure(api_key=key)
        
        try:
            # Convert messages to Gemini format
            # Gemini uses parts format, but we can use the chat interface
            model = genai.GenerativeModel(model_name)
            
            # Extract system message if present
            system_instruction = None
            chat_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    system_instruction = content
                elif role in ["user", "assistant"]:
                    chat_messages.append({"role": role, "parts": [content]})
            
            # Start chat session
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name,
                    system_instruction=system_instruction
                )
            
            chat = model.start_chat(history=chat_messages[:-1] if len(chat_messages) > 1 else [])
            last_message = chat_messages[-1] if chat_messages else {"role": "user", "parts": [""]}
            
            response = chat.send_message(last_message["parts"][0])
            
            # Extract text
            text = response.text if hasattr(response, 'text') else str(response)
            
            # Estimate tokens (input + output)
            input_tokens = sum(self._estimate_tokens(msg.get("content", ""), "") for msg in messages)
            output_tokens = self._estimate_tokens("", text)
            total_tokens = input_tokens + output_tokens
            
            # Record usage
            self.key_manager.record_usage(key, tokens=total_tokens, error=False)
            
            return {
                "content": text,
                "model": model_name,
                "tokens_used": total_tokens,
                "provider": "gemini",
                "key_index": self.key_manager.current_index.get("gemini", 0)
            }
        except Exception as e:
            # Handle quota/rate limit errors
            if self._is_quota_error(e):
                self.key_manager.mark_quota_exhausted(key)
                # Retry with next key
                return await self.chat(messages, **kwargs)
            # Record error
            self.key_manager.record_usage(key, error=True)
            raise
    
    def _is_quota_error(self, error: Exception) -> bool:
        """
        Check if error is quota/rate limit related.
        
        Args:
            error: Exception to check
        
        Returns:
            True if error is quota/rate limit related
        """
        error_str = str(error).lower()
        return (
            "quota" in error_str or
            "429" in error_str or
            "rate limit" in error_str or
            "resource exhausted" in error_str
        )
    
    def _estimate_tokens(self, input_text: str = "", output_text: str = "") -> int:
        """
        Estimate token count (rough approximation).
        
        Args:
            input_text: Input text
            output_text: Output text
        
        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 characters per token
        total_chars = len(input_text) + len(output_text)
        return total_chars // 4

