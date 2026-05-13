"""
AIM-OS AI Engine — Multi-Provider API Gateway

Production-grade LLM provider supporting OpenAI, Gemini, Anthropic, and DeepSeek
via their REST APIs. Includes retry logic, cost tracking, and streaming.

Keys are sourced from: ENV vars > BAS Credential Vault (port 5002).

Usage:
    from providers.api_provider import APIProvider

    api = APIProvider()
    result = api.complete("Explain recursion", model="gpt-4o")
    print(result.content, f"${result.metadata.get('cost', 0):.6f}")

    # Stream
    for chunk in api.stream("Write a poem", model="gemini-2.5-flash"):
        print(chunk.text, end='', flush=True)

    # Smart model selection
    result = api.complete("Fix this bug", provider_name="cheapest")
"""

import os
import sys
import json
import time
import logging
import random
from typing import Optional, Dict, List, Any, Iterator
from dataclasses import dataclass, field

# Add parent paths for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ENGINE_DIR = os.path.dirname(SCRIPT_DIR)
SCRIPTS_DIR = os.path.dirname(AI_ENGINE_DIR)

for p in [SCRIPTS_DIR, AI_ENGINE_DIR, SCRIPT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from providers.gemini_cli_provider import ProviderResponse, StreamChunk

logger = logging.getLogger('ai_engine.api_provider')


# ── Vault Integration ────────────────────────────────────

class VaultKeyManager:
    """
    Fetches API keys from ENV vars or BAS Credential Vault.
    Keys are cached in-process after first retrieval.
    """

    def __init__(self, vault_url: str = 'http://localhost:5002'):
        self.vault_url = vault_url
        self._cache: Dict[str, str] = {}

    def get_key(self, provider: str) -> Optional[str]:
        """
        Get an API key for a provider.
        Check order: 1) cache, 2) environment, 3) BAS vault
        """
        if provider in self._cache:
            return self._cache[provider]

        env_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'gemini': 'GEMINI_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
        }
        env_var = env_map.get(provider, f'{provider.upper()}_API_KEY')
        env_key = os.environ.get(env_var)
        if env_key:
            self._cache[provider] = env_key
            return env_key

        # Try BAS Credential Vault
        try:
            import urllib.request
            url = f'{self.vault_url}/api/vault/credentials'
            req = urllib.request.Request(url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                credentials = data if isinstance(data, list) else data.get('credentials', [])
                for cred in credentials:
                    cred_provider = cred.get('provider', '').lower()
                    if cred_provider == provider.lower():
                        key = cred.get('apiKey', cred.get('value', ''))
                        if key:
                            self._cache[provider] = key
                            return key
        except Exception as e:
            logger.debug(f'Vault lookup failed for {provider}: {e}')

        return None

    def status(self) -> dict:
        """Report which providers have keys."""
        providers = ['openai', 'anthropic', 'gemini', 'deepseek']
        return {p: bool(self.get_key(p)) for p in providers}


# ── Provider Configs ─────────────────────────────────────

PROVIDER_CONFIGS = {
    'openai': {
        'base_url': 'https://api.openai.com/v1',
        'chat_endpoint': '/chat/completions',
        'header_key': 'Authorization',
        'header_format': 'Bearer {key}',
        'api_version': None,
    },
    'gemini': {
        'base_url': 'https://generativelanguage.googleapis.com/v1beta',
        'chat_endpoint': '/models/{model}:generateContent',
        'header_key': None,  # Uses query param ?key=
        'header_format': None,
        'api_version': 'v1beta',
    },
    'anthropic': {
        'base_url': 'https://api.anthropic.com/v1',
        'chat_endpoint': '/messages',
        'header_key': 'x-api-key',
        'header_format': '{key}',
        'api_version': '2023-06-01',
    },
    'deepseek': {
        'base_url': 'https://api.deepseek.com/v1',
        'chat_endpoint': '/chat/completions',
        'header_key': 'Authorization',
        'header_format': 'Bearer {key}',
        'api_version': None,
    },
}


# ── API Provider ─────────────────────────────────────────

class APIProvider:
    """
    Multi-provider LLM gateway via REST APIs.

    Supports: OpenAI, Gemini, Anthropic, DeepSeek.
    Features: auto-retry, cost tracking, streaming, model detection.
    """

    def __init__(
        self,
        vault: Optional[VaultKeyManager] = None,
        track_costs: bool = True,
        max_retries: int = 3,
        budget_warn: float = 1.0,
        budget_limit: float = 5.0,
    ):
        self.vault = vault or VaultKeyManager()
        self.max_retries = max_retries
        self._request_count: int = 0
        self._total_latency: float = 0.0
        self._cost_tracker = None

        if track_costs:
            try:
                from providers.cost_tracker import get_tracker
                self._cost_tracker = get_tracker(budget_warn, budget_limit)
            except ImportError:
                logger.debug('Cost tracker not available')

    # ── Main API ──────────────────────────────────────────

    def complete(
        self,
        prompt: str,
        system: str = '',
        model: str = '',
        provider_name: str = 'openai',
        timeout: int = 120,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> ProviderResponse:
        """
        Send a prompt and get a complete response.

        Special provider_name values:
            'cheapest' — auto-select cheapest model
            'best'     — auto-select best model for coding
            'auto'     — detect from model name
        """
        # Handle special provider selectors
        if provider_name in ('cheapest', 'best', 'auto'):
            model, provider_name = self._smart_select(model, provider_name)

        # Auto-detect provider from model name
        if not provider_name and model:
            provider_name = self._detect_provider(model)

        if not provider_name:
            provider_name = 'openai'

        config = PROVIDER_CONFIGS.get(provider_name)
        if not config:
            return ProviderResponse(
                success=False,
                error=f'Unknown provider: {provider_name}',
            )

        # Get API key
        api_key = self.vault.get_key(provider_name)
        if not api_key:
            return ProviderResponse(
                success=False,
                error=f'No API key for {provider_name}. Set {provider_name.upper()}_API_KEY or add to BAS Vault.',
            )

        # Resolve default model
        if not model:
            try:
                from providers.model_catalog import get_catalog
                models = get_catalog().list_by_provider(
                    __import__('providers.model_catalog', fromlist=['Provider']).Provider(provider_name)
                )
                model = models[0].id if models else 'gpt-4o'
            except Exception:
                model = {'openai': 'gpt-4o', 'gemini': 'gemini-2.5-flash',
                         'anthropic': 'claude-sonnet-4-20250514', 'deepseek': 'deepseek-chat'}.get(provider_name, 'gpt-4o')

        # Budget check
        if self._cost_tracker:
            try:
                from providers.model_catalog import get_catalog
                est = get_catalog().estimate_cost(model, 2000, 2000) or 0
                check = self._cost_tracker.check_budget(est)
                if not check['within_budget']:
                    return ProviderResponse(
                        success=False,
                        error=f'Budget limit reached (${check["current_total"]:.4f} / ${check["budget_limit"]:.2f})',
                    )
            except Exception:
                pass

        # Build request body
        body = self._build_request(prompt, system, model, max_tokens, temperature, json_mode, provider_name)

        # Execute with retry
        return self._execute_with_retry(
            config=config,
            api_key=api_key,
            model=model,
            provider_name=provider_name,
            body=body,
            timeout=timeout,
        )

    def stream(
        self,
        prompt: str,
        system: str = '',
        model: str = 'gpt-4o',
        provider_name: str = '',
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Iterator[StreamChunk]:
        """
        Stream a response. Yields StreamChunk objects.

        Note: Gemini API streaming uses a different format than OpenAI.
        """
        if not provider_name:
            provider_name = self._detect_provider(model)

        config = PROVIDER_CONFIGS.get(provider_name)
        api_key = self.vault.get_key(provider_name)

        if not config or not api_key:
            yield StreamChunk(text=f'Error: No API key for {provider_name}', done=True)
            return

        body = self._build_request(prompt, system, model, max_tokens, temperature, False, provider_name)

        # Add streaming flag
        if provider_name in ('openai', 'deepseek'):
            body['stream'] = True
        elif provider_name == 'anthropic':
            body['stream'] = True

        url = self._build_url(config, model, api_key, stream=True)
        headers = self._build_headers(config, api_key, provider_name)

        try:
            import urllib.request
            req_data = json.dumps(body).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')

            with urllib.request.urlopen(req, timeout=120) as resp:
                buffer = ''
                for line_bytes in resp:
                    line = line_bytes.decode('utf-8').strip()
                    if not line:
                        continue

                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            yield StreamChunk(text='', done=True)
                            return

                        try:
                            chunk_data = json.loads(data_str)
                            text = self._extract_stream_chunk(chunk_data, provider_name)
                            if text:
                                yield StreamChunk(text=text, done=False)
                        except json.JSONDecodeError:
                            continue
                    elif provider_name == 'gemini':
                        # Gemini uses JSON array streaming
                        buffer += line
                        try:
                            chunks = json.loads(buffer)
                            if isinstance(chunks, list):
                                for c in chunks:
                                    text = self._extract_gemini_text(c)
                                    if text:
                                        yield StreamChunk(text=text, done=False)
                            buffer = ''
                        except json.JSONDecodeError:
                            continue

            yield StreamChunk(text='', done=True)

        except Exception as e:
            yield StreamChunk(text=f'\n\n[Stream error: {e}]', done=True)

    # ── Request Building ──────────────────────────────────

    def _build_request(
        self, prompt: str, system: str, model: str,
        max_tokens: int, temperature: float,
        json_mode: bool, provider_name: str,
    ) -> dict:
        """Build provider-specific request body."""
        if provider_name == 'gemini':
            return self._build_gemini_request(prompt, system, model, max_tokens, temperature)
        elif provider_name == 'anthropic':
            return self._build_anthropic_request(prompt, system, model, max_tokens, temperature)
        else:
            return self._build_openai_request(prompt, system, model, max_tokens, temperature, json_mode)

    def _build_openai_request(
        self, prompt: str, system: str, model: str,
        max_tokens: int, temperature: float, json_mode: bool,
    ) -> dict:
        messages = []
        if system:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': prompt})

        body: Dict[str, Any] = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }
        if json_mode:
            body['response_format'] = {'type': 'json_object'}
        return body

    def _build_anthropic_request(
        self, prompt: str, system: str, model: str,
        max_tokens: int, temperature: float,
    ) -> dict:
        body: Dict[str, Any] = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': max_tokens,
        }
        if system:
            body['system'] = system
        return body

    def _build_gemini_request(
        self, prompt: str, system: str, model: str,
        max_tokens: int, temperature: float,
    ) -> dict:
        body: Dict[str, Any] = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'maxOutputTokens': max_tokens,
                'temperature': temperature,
            },
        }
        if system:
            body['systemInstruction'] = {'parts': [{'text': system}]}
        return body

    def _build_url(self, config: dict, model: str, api_key: str, stream: bool = False) -> str:
        """Build the full API URL."""
        base = config['base_url']
        endpoint = config['chat_endpoint']

        if '{model}' in endpoint:
            endpoint = endpoint.replace('{model}', model)

        url = base + endpoint

        # Gemini uses query param for auth
        if config.get('header_key') is None:
            url += f'?key={api_key}'
            if stream:
                url += '&alt=sse'

        return url

    def _build_headers(self, config: dict, api_key: str, provider_name: str) -> dict:
        """Build request headers."""
        headers: Dict[str, str] = {'Content-Type': 'application/json'}

        if config.get('header_key') and config.get('header_format'):
            headers[config['header_key']] = config['header_format'].format(key=api_key)

        if provider_name == 'anthropic':
            headers['anthropic-version'] = config.get('api_version', '2023-06-01')

        return headers

    # ── Response Extraction ───────────────────────────────

    def _extract_content(self, result: dict, provider_name: str) -> str:
        """Extract text content from provider-specific response."""
        if provider_name == 'anthropic':
            blocks = result.get('content', [])
            return '\n'.join(b.get('text', '') for b in blocks if b.get('type') == 'text')
        elif provider_name == 'gemini':
            return self._extract_gemini_text(result)
        else:
            choices = result.get('choices', [])
            if choices:
                return choices[0].get('message', {}).get('content', '')
            return ''

    def _extract_gemini_text(self, result: dict) -> str:
        """Extract text from Gemini response."""
        candidates = result.get('candidates', [])
        if candidates:
            parts = candidates[0].get('content', {}).get('parts', [])
            return '\n'.join(p.get('text', '') for p in parts if 'text' in p)
        return ''

    def _extract_tokens(self, result: dict, provider_name: str) -> tuple:
        """Extract input/output token counts."""
        if provider_name == 'gemini':
            meta = result.get('usageMetadata', {})
            return meta.get('promptTokenCount', 0), meta.get('candidatesTokenCount', 0)
        elif provider_name == 'anthropic':
            usage = result.get('usage', {})
            return usage.get('input_tokens', 0), usage.get('output_tokens', 0)
        else:
            usage = result.get('usage', {})
            return usage.get('prompt_tokens', 0), usage.get('completion_tokens', 0)

    def _extract_stream_chunk(self, data: dict, provider_name: str) -> str:
        """Extract text from a streaming chunk."""
        if provider_name == 'anthropic':
            if data.get('type') == 'content_block_delta':
                return data.get('delta', {}).get('text', '')
            return ''
        else:
            # OpenAI / DeepSeek
            choices = data.get('choices', [])
            if choices:
                delta = choices[0].get('delta', {})
                return delta.get('content', '')
            return ''

    # ── Retry Logic ───────────────────────────────────────

    def _execute_with_retry(
        self,
        config: dict,
        api_key: str,
        model: str,
        provider_name: str,
        body: dict,
        timeout: int,
    ) -> ProviderResponse:
        """Execute API call with exponential backoff retry."""
        import urllib.request
        import urllib.error

        url = self._build_url(config, model, api_key)
        headers = self._build_headers(config, api_key, provider_name)

        last_error = ''
        for attempt in range(self.max_retries):
            start_time = time.monotonic()

            try:
                req_data = json.dumps(body).encode('utf-8')
                req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')

                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    result = json.loads(resp.read().decode())

                latency = (time.monotonic() - start_time) * 1000
                self._request_count += 1
                self._total_latency += latency

                # Extract content and tokens
                content = self._extract_content(result, provider_name)
                tokens_in, tokens_out = self._extract_tokens(result, provider_name)

                # Track cost
                cost = 0.0
                if self._cost_tracker:
                    cost_result = self._cost_tracker.record_request(
                        model=model,
                        input_tokens=tokens_in,
                        output_tokens=tokens_out,
                        provider=provider_name,
                        latency_ms=latency,
                    )
                    cost = cost_result.get('cost', 0.0)

                return ProviderResponse(
                    success=True,
                    content=content,
                    model=model,
                    provider=provider_name,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    latency_ms=latency,
                    metadata={
                        'cost': cost,
                        'attempt': attempt + 1,
                    },
                )

            except urllib.error.HTTPError as e:
                last_error = f'HTTP {e.code}: {e.reason}'
                # Don't retry 4xx client errors (except 429 rate limit)
                if 400 <= e.code < 500 and e.code != 429:
                    break
                logger.warning(f'[APIProvider] Attempt {attempt + 1}/{self.max_retries}: {last_error}')

            except Exception as e:
                last_error = str(e)
                logger.warning(f'[APIProvider] Attempt {attempt + 1}/{self.max_retries}: {last_error}')

            # Exponential backoff with jitter
            if attempt < self.max_retries - 1:
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        latency = (time.monotonic() - start_time) * 1000
        return ProviderResponse(
            success=False,
            error=f'All {self.max_retries} attempts failed. Last error: {last_error}',
            provider=provider_name,
            latency_ms=latency,
        )

    # ── Smart Selection ───────────────────────────────────

    def _smart_select(self, model: str, strategy: str) -> tuple:
        """Auto-select model based on strategy."""
        try:
            from providers.model_catalog import get_catalog
            catalog = get_catalog()

            if strategy == 'cheapest':
                m = catalog.cheapest_for('text')
                if m:
                    return m.id, m.provider.value
            elif strategy == 'best':
                recs = catalog.recommend('coding')
                if recs:
                    return recs[0].id, recs[0].provider.value
            elif strategy == 'auto' and model:
                return model, self._detect_provider(model)
        except Exception:
            pass

        return model or 'gpt-4o', 'openai'

    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name."""
        m = model.lower()
        if 'claude' in m:
            return 'anthropic'
        if 'gemini' in m:
            return 'gemini'
        if 'deepseek' in m:
            return 'deepseek'
        return 'openai'

    # ── Status ────────────────────────────────────────────

    def status(self) -> dict:
        """Full provider status."""
        keys = self.vault.status()

        cost_info = {}
        if self._cost_tracker:
            cost_info = self._cost_tracker.status()

        try:
            from providers.model_catalog import get_catalog
            catalog_info = get_catalog().status()
        except Exception:
            catalog_info = {}

        return {
            'provider': 'api_gateway',
            'version': '2.0',
            'available_keys': keys,
            'providers_ready': [p for p, avail in keys.items() if avail],
            'providers_missing': [p for p, avail in keys.items() if not avail],
            'catalog': catalog_info,
            'costs': cost_info,
            'metrics': {
                'total_requests': self._request_count,
                'avg_latency_ms': (
                    round(self._total_latency / self._request_count, 1)
                    if self._request_count > 0 else 0
                ),
            },
        }

    def check_available(self) -> dict:
        """Quick availability check."""
        keys = self.vault.status()
        any_available = any(keys.values())
        return {
            'available': any_available,
            'keys': keys,
        }


# ── Quick Test ────────────────────────────────────────────

if __name__ == '__main__':
    api = APIProvider()
    status = api.status()

    print('╔════════════════════════════════════════════════════════════╗')
    print('║   AIM-OS Multi-Provider API Gateway v2.0                 ║')
    print('╚════════════════════════════════════════════════════════════╝')
    print()

    print('  API Keys:')
    for provider, available in status['available_keys'].items():
        icon = '✅' if available else '❌'
        print(f'    {icon} {provider}')
    print()

    ready = status['providers_ready']
    print(f'  Ready: {len(ready)} provider(s) — {", ".join(ready) if ready else "none"}')
    print(f'  Models: {status["catalog"].get("total_models", "?")} in catalog')

    if status.get('costs'):
        c = status['costs']
        print(f'  Spend: ${c.get("total_cost", 0):.6f} total, ${c.get("session_cost", 0):.6f} session')
        budget = c.get('budget', {})
        print(f'  Budget: ${budget.get("remaining", 0):.4f} remaining of ${budget.get("limit", 0):.2f}')

    # Quick API test if requested
    if '--test' in sys.argv and ready:
        provider = ready[0]
        print(f'\n  Testing {provider} API...')
        result = api.complete(
            'Say "Hello from AIM-OS!" and nothing else.',
            provider_name=provider,
            max_tokens=50,
        )
        if result.success:
            print(f'  ✅ Response: {result.content.strip()[:80]}')
            print(f'     Model: {result.model}, Tokens: {result.tokens_in}/{result.tokens_out}')
            print(f'     Cost: ${result.metadata.get("cost", 0):.6f}, Latency: {result.latency_ms:.0f}ms')
        else:
            print(f'  ❌ Error: {result.error}')
