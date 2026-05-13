"""
LLM API Service Registry

Provides unified interface for LLM API providers (Gemini, Cerebras, Anthropic, OpenAI, etc.)
with automatic key rotation, usage tracking, and AIM-OS integration.

Phase 1: Gemini + Cerebras (MVP)
Phase 2: Full expansion (Anthropic, OpenAI, DeepInfra, Replicate)
"""

from .llm_client import LLMClient
from .key_manager import APIKeyManager
from .gemini_client import GeminiClient
from .cerebras_client import CerebrasClient
from .api_service_registry import APIServiceRegistry, get_api_registry

__all__ = [
    "LLMClient",
    "APIKeyManager",
    "GeminiClient",
    "CerebrasClient",
    "APIServiceRegistry",
    "get_api_registry",
]

