"""Anthropic Claude API client implementation.

Provides unified interface to Claude models through anthropic SDK.
"""

from __future__ import annotations

import os
import time
from typing import Optional, List, Dict, Any

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import (
    LLMClient,
    LLMResponse,
    ModelInfo,
    LLMError,
    AuthenticationError,
    RateLimitError
)


class AnthropicClient(LLMClient):
    """Anthropic Claude API client.
    
    Supports Claude models including:
    - claude-3-5-sonnet-20241022 (fast, high quality)
    - claude-3-opus-20240229 (highest quality)
    - claude-3-haiku-20240307 (fastest, cost-effective)
    
    Example:
        >>> import os
        >>> client = AnthropicClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
        >>> response = client.generate("Explain bitemporal databases")
        >>> print(response.text)
        >>> print(f"Tokens: {response.tokens_used}, Latency: {response.latency_ms}ms")
    
    Args:
        api_key: Anthropic API key
        model: Model name (default: claude-3-5-sonnet-20241022)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic SDK not installed. "
                "Install with: pip install anthropic"
            )
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key parameter."
            )
        
        try:
            self.client = Anthropic(api_key=self.api_key)
            self.model_name = model
        except Exception as e:
            raise AuthenticationError(
                message=f"Failed to initialize Anthropic: {str(e)}",
                provider="anthropic",
                original_error=e
            )
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Claude.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (default: 4096)
            temperature: Sampling temperature (0-1, default: 1.0)
            **kwargs: Additional Anthropic-specific parameters
                - system: System message
                - messages: List of messages (for chat)
        
        Returns:
            LLMResponse with generated text and metadata
        
        Raises:
            LLMError: If generation fails
            RateLimitError: If rate limit exceeded
            AuthenticationError: If authentication fails
        """
        # Build messages - support both simple prompt and chat format
        if "messages" in kwargs:
            messages = kwargs["messages"]
        else:
            # Simple prompt format
            messages = [{"role": "user", "content": prompt}]
        
        # Extract system message if provided
        system = kwargs.get("system")
        
        # Build generation parameters
        params: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens or 4096,
        }
        
        if temperature is not None:
            params["temperature"] = temperature
        else:
            params["temperature"] = 1.0  # Anthropic default
        
        if system:
            params["system"] = system
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["messages", "system"]:
                params[key] = value
        
        try:
            start_time = time.time()
            
            response = self.client.messages.create(**params)
            
            latency = (time.time() - start_time) * 1000
            
            # Extract text from response
            # Claude returns content as a list of content blocks
            text_parts = []
            for content_block in response.content:
                if content_block.type == "text":
                    text_parts.append(content_block.text)
            
            text = "".join(text_parts)
            
            # Extract token counts
            usage = response.usage
            prompt_tokens = usage.input_tokens
            completion_tokens = usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            # Extract stop reason
            stop_reason = response.stop_reason
            
            # Estimate confidence based on stop reason
            # stop = normal completion (high confidence)
            # max_tokens = truncated (medium confidence)
            # stop_sequence = hit stop sequence (high confidence)
            if stop_reason == "stop":
                confidence = 0.90
            elif stop_reason == "max_tokens":
                confidence = 0.75
            elif stop_reason == "stop_sequence":
                confidence = 0.85
            else:
                confidence = 0.70
            
            return LLMResponse(
                text=text,
                model=self.model_name,
                provider="anthropic",
                tokens_used=total_tokens,
                latency_ms=latency,
                confidence=confidence,
                raw_response=response,
                metadata={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "stop_reason": stop_reason,
                    "stop_sequence": response.stop_sequence,
                }
            )
        
        except Exception as e:
            error_str = str(e).lower()
            
            # Detect specific error types
            if "rate" in error_str or "quota" in error_str or "429" in error_str:
                raise RateLimitError(
                    message=f"Anthropic rate limit exceeded: {str(e)}",
                    provider="anthropic",
                    error_code="RATE_LIMIT",
                    original_error=e
                )
            elif "auth" in error_str or "key" in error_str or "401" in error_str:
                raise AuthenticationError(
                    message=f"Anthropic authentication failed: {str(e)}",
                    provider="anthropic",
                    error_code="AUTH_FAILED",
                    original_error=e
                )
            else:
                raise LLMError(
                    message=f"Anthropic generation failed: {str(e)}",
                    provider="anthropic",
                    original_error=e
                )
    
    def get_model_info(self) -> ModelInfo:
        """Get information about current Claude model.
        
        Returns:
            ModelInfo with model capabilities
        """
        # Model-specific information
        model_specs = {
            "claude-3-5-sonnet-20241022": {
                "context_window": 200_000,
                "max_output": 8192,
                "streaming": True,
                "functions": True
            },
            "claude-3-opus-20240229": {
                "context_window": 200_000,
                "max_output": 4096,
                "streaming": True,
                "functions": True
            },
            "claude-3-sonnet-20240229": {
                "context_window": 200_000,
                "max_output": 4096,
                "streaming": True,
                "functions": True
            },
            "claude-3-haiku-20240307": {
                "context_window": 200_000,
                "max_output": 4096,
                "streaming": True,
                "functions": True
            }
        }
        
        spec = model_specs.get(self.model_name, {
            "context_window": 200_000,
            "max_output": 4096,
            "streaming": True,
            "functions": True
        })
        
        return ModelInfo(
            name=self.model_name,
            provider="anthropic",
            context_window=spec["context_window"],
            max_output_tokens=spec["max_output"],
            supports_streaming=spec["streaming"],
            supports_function_calling=spec["functions"],
            metadata={
                "sdk": "anthropic",
                "docs": "https://docs.anthropic.com"
            }
        )

