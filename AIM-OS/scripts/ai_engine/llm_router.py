"""
AIM-OS AI Engine — LLM Router

The unified interface for all LLM access in AIM-OS.
Routes prompts to the optimal provider based on:
  - Cost:  Gemini CLI first (free), API providers as fallback
  - Task:  deep think for architecture, fast for autocomplete, vision for UI
  - Model: explicit model requests bypass routing logic

This is Layer 1 of the AI Engine. All higher layers (Context Engine,
Agent Runtime, Self-Improvement) call through this router.

Usage:
    router = LLMRouter()
    
    # Simple completion
    response = router.complete("Explain this error")
    
    # With system prompt and model selection
    response = router.complete(
        prompt="Refactor this function",
        system="You are a senior TypeScript engineer.",
        model='deep-think',
    )
    
    # Streaming
    async for chunk in router.stream("Write a REST API"):
        print(chunk.text, end='')
    
    # Vision
    response = router.vision("/path/to/screenshot.png", "What UI elements are visible?")
"""

import time
import logging
import asyncio
from typing import Optional, Dict, List, Any, AsyncIterator
from dataclasses import dataclass, field

from ai_engine.providers.gemini_cli_provider import (
    GeminiCLIProvider, GeminiModel, OutputFormat,
    ProviderResponse, StreamChunk,
)
from ai_engine.providers.api_provider import APIProvider, VaultKeyManager

logger = logging.getLogger('ai_engine.llm_router')


# ── Task-to-Model Mapping ────────────────────────────────

class TaskType:
    """Task classification for model selection."""
    FAST = 'fast'              # Autocomplete, quick answers
    STANDARD = 'standard'      # General coding, explanations
    DEEP_THINK = 'deep-think'  # Architecture, complex reasoning
    VISION = 'vision'          # Image analysis
    IMAGE_GEN = 'image-gen'    # Nano Banana
    CODE_EDIT = 'code-edit'    # File editing, refactoring
    PLANNING = 'planning'      # Task decomposition
    AUDIT = 'audit'            # Code review, self-check


MODEL_ROUTING = {
    TaskType.FAST:       {'model': GeminiModel.FLASH,      'timeout': 30},
    TaskType.STANDARD:   {'model': GeminiModel.PRO,        'timeout': 60},
    TaskType.DEEP_THINK: {'model': GeminiModel.DEEP_THINK, 'timeout': 300},
    TaskType.VISION:     {'model': GeminiModel.VISION,     'timeout': 120},
    TaskType.IMAGE_GEN:  {'model': GeminiModel.AUTO,       'timeout': 180},
    TaskType.CODE_EDIT:  {'model': GeminiModel.PRO,        'timeout': 120},
    TaskType.PLANNING:   {'model': GeminiModel.DEEP_THINK, 'timeout': 180},
    TaskType.AUDIT:      {'model': GeminiModel.PRO,        'timeout': 120},
}


# ── Router Configuration ─────────────────────────────────

@dataclass
class RouterConfig:
    """Configuration for the LLM Router."""
    # Provider preference order
    provider_priority: List[str] = field(
        default_factory=lambda: ['gemini-cli', 'openai', 'anthropic', 'deepseek']
    )
    # Default task type when not specified
    default_task: str = TaskType.STANDARD
    # Whether to auto-fallback to API when CLI fails
    auto_fallback: bool = True
    # Maximum retries per request
    max_retries: int = 2
    # Working directory for Gemini CLI context
    working_directory: str = ''
    # Include directories for workspace context
    include_dirs: List[str] = field(default_factory=list)


# ── LLM Router ──────────────────────────────────────────

class LLMRouter:
    """
    Unified LLM access for all AIM-OS agents.
    
    Routing logic:
      1. If explicit model requested → route to matching provider
      2. If task_type specified → select model from MODEL_ROUTING
      3. Default → Gemini CLI (free, Pro model)
      4. On failure → auto-fallback to API providers
    
    All responses are standardised as ProviderResponse objects.
    """

    def __init__(self, config: Optional[RouterConfig] = None):
        self.config = config or RouterConfig()

        # Initialise providers
        self._vault = VaultKeyManager()
        self._gemini = GeminiCLIProvider(
            working_directory=self.config.working_directory or None,
        )
        self._api = APIProvider(vault=self._vault)

        # Metrics
        self._total_requests: int = 0
        self._gemini_requests: int = 0
        self._api_requests: int = 0
        self._fallback_count: int = 0
        self._total_latency: float = 0.0

    # ── Main Interface ───────────────────────────────────

    def complete(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        task_type: str = '',
        timeout: Optional[int] = None,
        provider: str = '',
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ProviderResponse:
        """
        Send a prompt and get a complete response.
        
        Args:
            prompt: The user/agent prompt
            system: System instruction (role, constraints)
            model: Explicit model name, or empty for auto
            task_type: Task classification for auto model selection
            timeout: Request timeout in seconds
            provider: Force a specific provider ('gemini-cli', 'openai', etc.)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
        
        Returns:
            ProviderResponse with content, timing, and metadata
        """
        self._total_requests += 1

        # Resolve model and timeout from task type
        resolved = self._resolve_model(model, task_type)
        model = resolved['model']
        timeout = timeout or resolved.get('timeout', 120)

        # Route to explicit provider
        if provider:
            return self._route_to_provider(
                provider, prompt, system, model, timeout, temperature, max_tokens,
            )

        # Default routing: Gemini CLI first
        if self._gemini.is_available:
            response = self._try_gemini(prompt, system, model, timeout)
            if response.success:
                self._gemini_requests += 1
                return response
            logger.warning(f'Gemini CLI failed: {response.error}')

        # Fallback to API providers
        if self.config.auto_fallback:
            self._fallback_count += 1
            return self._try_api_fallback(
                prompt, system, model, timeout, temperature, max_tokens,
            )

        return ProviderResponse(
            success=False,
            error='No LLM provider available. Check Gemini CLI installation or add API keys to Vault.',
        )

    def complete_json(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        task_type: str = '',
        timeout: Optional[int] = None,
    ) -> ProviderResponse:
        """
        Get structured JSON output.
        Uses Gemini CLI --output-format json when available.
        """
        self._total_requests += 1

        resolved = self._resolve_model(model, task_type)
        model = resolved['model']
        timeout = timeout or resolved.get('timeout', 120)

        if self._gemini.is_available:
            response = self._gemini.complete_json(
                prompt=prompt, system=system, model=model, timeout=timeout,
            )
            if response.success:
                self._gemini_requests += 1
                return response

        # API fallback with JSON instruction in prompt
        json_system = (system or '') + (
            '\n\nIMPORTANT: Respond ONLY with valid JSON. '
            'No markdown, no explanations, just the JSON object.'
        )
        return self._try_api_fallback(
            prompt, json_system, model, timeout,
        )

    # ── Streaming ────────────────────────────────────────

    async def stream(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        task_type: str = '',
        timeout: Optional[int] = None,
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream response tokens using Gemini CLI stream-json.
        Falls back to full completion if streaming unavailable.
        """
        resolved = self._resolve_model(model, task_type)
        model = resolved['model']
        timeout = timeout or resolved.get('timeout', 120)

        if self._gemini.is_available:
            async for chunk in self._gemini.stream(
                prompt=prompt, system=system, model=model, timeout=timeout,
            ):
                yield chunk
        else:
            # Fallback: get full response and yield as single chunk
            response = self.complete(prompt=prompt, system=system, model=model)
            yield StreamChunk(text=response.content, done=True)

    # ── Vision ───────────────────────────────────────────

    def vision(
        self,
        image_path: str,
        prompt: str,
        model: str = '',
        timeout: Optional[int] = None,
    ) -> ProviderResponse:
        """
        Analyse an image with a text prompt.
        Routes to Gemini CLI Vision (free via Ultra sub).
        """
        self._total_requests += 1
        timeout = timeout or 120

        if self._gemini.is_available:
            response = self._gemini.vision(
                image_path=image_path, prompt=prompt,
                model=model, timeout=timeout,
            )
            if response.success:
                self._gemini_requests += 1
                return response

        return ProviderResponse(
            success=False,
            error='Vision requires Gemini CLI. Install: npm install -g @anthropic-ai/gemini-cli',
        )

    # ── Image Generation ─────────────────────────────────

    def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        reference_image: Optional[str] = None,
    ) -> ProviderResponse:
        """
        Generate image via Nano Banana (Gemini CLI).
        Free with Ultra subscription.
        """
        self._total_requests += 1

        if self._gemini.is_available:
            return self._gemini.generate_image(
                prompt=prompt,
                output_path=output_path,
                reference_image=reference_image,
            )

        return ProviderResponse(
            success=False,
            error='Image generation requires Gemini CLI (Nano Banana).',
        )

    # ── Status & Metrics ─────────────────────────────────

    def status(self) -> dict:
        """Full router status with all provider statuses."""
        return {
            'router': {
                'version': '0.1.0',
                'total_requests': self._total_requests,
                'gemini_requests': self._gemini_requests,
                'api_requests': self._api_requests,
                'fallback_count': self._fallback_count,
                'avg_latency_ms': (
                    self._total_latency / self._total_requests
                    if self._total_requests > 0 else 0
                ),
                'config': {
                    'provider_priority': self.config.provider_priority,
                    'auto_fallback': self.config.auto_fallback,
                    'default_task': self.config.default_task,
                },
            },
            'providers': {
                'gemini_cli': self._gemini.status(),
                'api': self._api.status(),
            },
            'model_routing': {
                task: cfg['model'] for task, cfg in MODEL_ROUTING.items()
            },
        }

    # ── Internal Routing ─────────────────────────────────

    def _resolve_model(self, model: str, task_type: str) -> dict:
        """Resolve model and timeout from explicit model or task type."""
        if model and model != 'auto':
            return {'model': model, 'timeout': 120}

        task = task_type or self.config.default_task
        routing = MODEL_ROUTING.get(task, MODEL_ROUTING[TaskType.STANDARD])
        return routing

    def _try_gemini(
        self, prompt: str, system: str, model: str, timeout: int,
    ) -> ProviderResponse:
        """Try Gemini CLI provider."""
        return self._gemini.complete(
            prompt=prompt,
            system=system,
            model=model,
            timeout=timeout,
        )

    def _try_api_fallback(
        self,
        prompt: str, system: str = '', model: str = '',
        timeout: int = 120, temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ProviderResponse:
        """Try API providers in priority order."""
        api_providers = [
            p for p in self.config.provider_priority
            if p != 'gemini-cli'
        ]

        for provider_name in api_providers:
            key = self._vault.get_key(provider_name)
            if not key:
                continue

            response = self._api.complete(
                prompt=prompt,
                system=system,
                model=model if model not in [m.value for m in GeminiModel] else '',
                provider_name=provider_name,
                timeout=timeout,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if response.success:
                self._api_requests += 1
                self._total_latency += response.latency_ms
                return response

            logger.warning(f'API provider {provider_name} failed: {response.error}')

        return ProviderResponse(
            success=False,
            error='All LLM providers failed. Check Gemini CLI or add API keys to Vault.',
        )

    def _route_to_provider(
        self,
        provider: str,
        prompt: str, system: str, model: str,
        timeout: int, temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ProviderResponse:
        """Route directly to a specific provider."""
        if provider == 'gemini-cli':
            return self._try_gemini(prompt, system, model, timeout)
        else:
            return self._api.complete(
                prompt=prompt, system=system, model=model,
                provider_name=provider, timeout=timeout,
                temperature=temperature, max_tokens=max_tokens,
            )
