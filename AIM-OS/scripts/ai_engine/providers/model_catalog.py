"""
AIM-OS AI Engine — Model Catalog

Centralized registry of LLM models across all providers with pricing,
capabilities, and context window metadata.

Usage:
    from providers.model_catalog import ModelCatalog, get_catalog

    catalog = get_catalog()
    model = catalog.get('gpt-4o')
    cost = catalog.estimate_cost('gpt-4o', input_tokens=1000, output_tokens=500)
    picks = catalog.recommend('coding', budget_per_request=0.05)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set
from enum import Enum


# ── Enums ─────────────────────────────────────────────────

class Provider(str, Enum):
    OPENAI = 'openai'
    GEMINI = 'gemini'
    ANTHROPIC = 'anthropic'
    DEEPSEEK = 'deepseek'


class Capability(str, Enum):
    TEXT = 'text'
    VISION = 'vision'
    TOOLS = 'tools'
    JSON_MODE = 'json_mode'
    STREAMING = 'streaming'
    REASONING = 'reasoning'
    CODE = 'code'
    THINKING = 'thinking'
    COMPUTER_USE = 'computer_use'
    IMAGE_GEN = 'image_gen'


class TaskType(str, Enum):
    CODING = 'coding'
    RESEARCH = 'research'
    ANALYSIS = 'analysis'
    CREATIVE = 'creative'
    REASONING = 'reasoning'
    FAST = 'fast'
    CHEAP = 'cheap'


# ── Model Definition ─────────────────────────────────────

@dataclass
class ModelInfo:
    """Complete model metadata."""
    id: str
    provider: Provider
    display_name: str
    input_price_per_m: float       # $ per million input tokens
    output_price_per_m: float      # $ per million output tokens
    context_window: int            # max tokens
    capabilities: Set[Capability] = field(default_factory=set)
    best_for: List[TaskType] = field(default_factory=list)
    notes: str = ''
    deprecated: bool = False

    @property
    def input_price_per_token(self) -> float:
        return self.input_price_per_m / 1_000_000

    @property
    def output_price_per_token(self) -> float:
        return self.output_price_per_m / 1_000_000

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request."""
        return (
            input_tokens * self.input_price_per_token
            + output_tokens * self.output_price_per_token
        )

    def has_capability(self, cap: Capability) -> bool:
        return cap in self.capabilities

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'provider': self.provider.value,
            'display_name': self.display_name,
            'input_price_per_m': self.input_price_per_m,
            'output_price_per_m': self.output_price_per_m,
            'context_window': self.context_window,
            'capabilities': [c.value for c in self.capabilities],
            'best_for': [t.value for t in self.best_for],
            'notes': self.notes,
        }


# ── Built-in Model Registry ──────────────────────────────

MODELS: Dict[str, ModelInfo] = {}


def _register(model: ModelInfo):
    MODELS[model.id] = model


# ── OpenAI ────────────────────────────────────────────────

_register(ModelInfo(
    id='gpt-4o',
    provider=Provider.OPENAI,
    display_name='GPT-4o',
    input_price_per_m=2.50,
    output_price_per_m=10.00,
    context_window=128_000,
    capabilities={Capability.TEXT, Capability.VISION, Capability.TOOLS,
                  Capability.JSON_MODE, Capability.STREAMING, Capability.CODE},
    best_for=[TaskType.CODING, TaskType.ANALYSIS, TaskType.RESEARCH],
    notes='Flagship multimodal. Best quality/cost for most tasks.',
))

_register(ModelInfo(
    id='gpt-4o-mini',
    provider=Provider.OPENAI,
    display_name='GPT-4o Mini',
    input_price_per_m=0.15,
    output_price_per_m=0.60,
    context_window=128_000,
    capabilities={Capability.TEXT, Capability.VISION, Capability.TOOLS,
                  Capability.JSON_MODE, Capability.STREAMING, Capability.CODE},
    best_for=[TaskType.FAST, TaskType.CHEAP],
    notes='Very cheap. Good for classification, extraction, simple tasks.',
))

_register(ModelInfo(
    id='o3-mini',
    provider=Provider.OPENAI,
    display_name='o3-mini',
    input_price_per_m=1.10,
    output_price_per_m=4.40,
    context_window=128_000,
    capabilities={Capability.TEXT, Capability.TOOLS, Capability.REASONING,
                  Capability.STREAMING, Capability.CODE},
    best_for=[TaskType.REASONING, TaskType.CODING],
    notes='Reasoning model. Chain-of-thought for complex problems.',
))

_register(ModelInfo(
    id='o1',
    provider=Provider.OPENAI,
    display_name='o1',
    input_price_per_m=15.00,
    output_price_per_m=60.00,
    context_window=200_000,
    capabilities={Capability.TEXT, Capability.VISION, Capability.TOOLS,
                  Capability.REASONING, Capability.CODE},
    best_for=[TaskType.REASONING],
    notes='Most powerful reasoning. Expensive — use for hard problems only.',
))

# ── Google Gemini ─────────────────────────────────────────

_register(ModelInfo(
    id='gemini-2.5-pro',
    provider=Provider.GEMINI,
    display_name='Gemini 2.5 Pro',
    input_price_per_m=1.25,
    output_price_per_m=10.00,
    context_window=1_048_576,
    capabilities={Capability.TEXT, Capability.VISION, Capability.TOOLS,
                  Capability.JSON_MODE, Capability.STREAMING, Capability.CODE,
                  Capability.THINKING},
    best_for=[TaskType.CODING, TaskType.ANALYSIS, TaskType.RESEARCH],
    notes='1M context window. Thinking mode included. Best value for long-context.',
))

_register(ModelInfo(
    id='gemini-2.5-flash',
    provider=Provider.GEMINI,
    display_name='Gemini 2.5 Flash',
    input_price_per_m=0.15,
    output_price_per_m=0.60,
    context_window=1_048_576,
    capabilities={Capability.TEXT, Capability.VISION, Capability.TOOLS,
                  Capability.JSON_MODE, Capability.STREAMING, Capability.CODE},
    best_for=[TaskType.FAST, TaskType.CHEAP],
    notes='Cheap + fast + 1M context. Best for high-volume.',
))

_register(ModelInfo(
    id='gemini-2.0-flash',
    provider=Provider.GEMINI,
    display_name='Gemini 2.0 Flash',
    input_price_per_m=0.10,
    output_price_per_m=0.40,
    context_window=1_048_576,
    capabilities={Capability.TEXT, Capability.VISION, Capability.TOOLS,
                  Capability.JSON_MODE, Capability.STREAMING},
    best_for=[TaskType.FAST, TaskType.CHEAP],
    notes='Cheapest Gemini. Good for simple tasks.',
))

# ── Anthropic ─────────────────────────────────────────────

_register(ModelInfo(
    id='claude-sonnet-4-20250514',
    provider=Provider.ANTHROPIC,
    display_name='Claude Sonnet 4',
    input_price_per_m=3.00,
    output_price_per_m=15.00,
    context_window=200_000,
    capabilities={Capability.TEXT, Capability.VISION, Capability.TOOLS,
                  Capability.JSON_MODE, Capability.STREAMING, Capability.CODE,
                  Capability.COMPUTER_USE},
    best_for=[TaskType.CODING, TaskType.ANALYSIS],
    notes='Extended thinking. Computer use. Best for long complex code.',
))

_register(ModelInfo(
    id='claude-3-5-haiku-20241022',
    provider=Provider.ANTHROPIC,
    display_name='Claude 3.5 Haiku',
    input_price_per_m=0.80,
    output_price_per_m=4.00,
    context_window=200_000,
    capabilities={Capability.TEXT, Capability.TOOLS, Capability.JSON_MODE,
                  Capability.STREAMING, Capability.CODE},
    best_for=[TaskType.FAST, TaskType.CODING],
    notes='Fast Claude. Good for code review, extraction.',
))

# ── DeepSeek ──────────────────────────────────────────────

_register(ModelInfo(
    id='deepseek-chat',
    provider=Provider.DEEPSEEK,
    display_name='DeepSeek V3',
    input_price_per_m=0.14,
    output_price_per_m=0.28,
    context_window=64_000,
    capabilities={Capability.TEXT, Capability.TOOLS, Capability.JSON_MODE,
                  Capability.STREAMING, Capability.CODE},
    best_for=[TaskType.CHEAP, TaskType.CODING],
    notes='Cheapest capable model. Great for batch/bulk work.',
))

_register(ModelInfo(
    id='deepseek-reasoner',
    provider=Provider.DEEPSEEK,
    display_name='DeepSeek R1',
    input_price_per_m=0.55,
    output_price_per_m=2.19,
    context_window=64_000,
    capabilities={Capability.TEXT, Capability.REASONING, Capability.CODE},
    best_for=[TaskType.REASONING, TaskType.CODING],
    notes='Reasoning model at DeepSeek prices. R1-class thinking.',
))


# ── Model Catalog ─────────────────────────────────────────

class ModelCatalog:
    """
    Unified interface to the model registry.

    Provides model lookup, cost estimation, and smart recommendations.
    """

    def __init__(self, models: Optional[Dict[str, ModelInfo]] = None):
        self._models = models or MODELS

    def get(self, model_id: str) -> Optional[ModelInfo]:
        """Get a model by ID."""
        return self._models.get(model_id)

    def list_all(self) -> List[ModelInfo]:
        """List all registered models."""
        return list(self._models.values())

    def list_by_provider(self, provider: Provider) -> List[ModelInfo]:
        """List models for a specific provider."""
        return [m for m in self._models.values() if m.provider == provider]

    def list_by_capability(self, capability: Capability) -> List[ModelInfo]:
        """List models with a specific capability."""
        return [m for m in self._models.values() if capability in m.capabilities]

    def estimate_cost(
        self, model_id: str, input_tokens: int, output_tokens: int
    ) -> Optional[float]:
        """Estimate cost for a specific model and token count."""
        model = self.get(model_id)
        if not model:
            return None
        return model.estimate_cost(input_tokens, output_tokens)

    def recommend(
        self,
        task_type: str = 'coding',
        budget_per_request: Optional[float] = None,
        required_capabilities: Optional[List[str]] = None,
        min_context: int = 0,
        provider: Optional[str] = None,
    ) -> List[ModelInfo]:
        """
        Recommend models for a task.

        Args:
            task_type: Type of task (coding, research, fast, cheap, etc.)
            budget_per_request: Max cost per request (assumes 2K in + 2K out)
            required_capabilities: Required capability names
            min_context: Minimum context window size
            provider: Filter to specific provider

        Returns:
            List of matching models, sorted by relevance
        """
        candidates = list(self._models.values())

        # Filter by provider
        if provider:
            try:
                prov = Provider(provider)
                candidates = [m for m in candidates if m.provider == prov]
            except ValueError:
                pass

        # Filter by minimum context
        if min_context > 0:
            candidates = [m for m in candidates if m.context_window >= min_context]

        # Filter by capabilities
        if required_capabilities:
            req_caps = set()
            for c in required_capabilities:
                try:
                    req_caps.add(Capability(c))
                except ValueError:
                    pass
            if req_caps:
                candidates = [m for m in candidates if req_caps.issubset(m.capabilities)]

        # Filter by budget (estimate at 2K input + 2K output)
        if budget_per_request is not None:
            candidates = [
                m for m in candidates
                if m.estimate_cost(2000, 2000) <= budget_per_request
            ]

        # Sort: prefer models where task_type matches best_for
        try:
            tt = TaskType(task_type)
        except ValueError:
            tt = None

        def score(m: ModelInfo) -> float:
            s = 0.0
            if tt and tt in m.best_for:
                s += 10.0
            # Prefer cheaper models marginally
            s -= m.estimate_cost(1000, 1000) * 100
            return s

        candidates.sort(key=score, reverse=True)
        return candidates

    def cheapest_for(self, capability: str = 'text') -> Optional[ModelInfo]:
        """Find the cheapest model with a given capability."""
        try:
            cap = Capability(capability)
        except ValueError:
            cap = Capability.TEXT

        models = self.list_by_capability(cap)
        if not models:
            return None
        return min(models, key=lambda m: m.estimate_cost(1000, 1000))

    def status(self) -> dict:
        """Catalog status summary."""
        by_provider = {}
        for m in self._models.values():
            p = m.provider.value
            if p not in by_provider:
                by_provider[p] = []
            by_provider[p].append(m.id)

        return {
            'total_models': len(self._models),
            'providers': list(by_provider.keys()),
            'models_by_provider': by_provider,
        }


# ── Singleton ─────────────────────────────────────────────

_catalog: Optional[ModelCatalog] = None


def get_catalog() -> ModelCatalog:
    """Get the global model catalog instance."""
    global _catalog
    if _catalog is None:
        _catalog = ModelCatalog()
    return _catalog


# ── Quick Test ────────────────────────────────────────────

if __name__ == '__main__':
    catalog = get_catalog()
    status = catalog.status()

    print('╔════════════════════════════════════════════════════════════╗')
    print('║   AIM-OS Model Catalog                                   ║')
    print('╚════════════════════════════════════════════════════════════╝')
    print(f'\n  {status["total_models"]} models across {len(status["providers"])} providers\n')

    for provider, models in status['models_by_provider'].items():
        print(f'  {provider}:')
        for m_id in models:
            m = catalog.get(m_id)
            cost = m.estimate_cost(1000, 1000)
            print(f'    {m.display_name:.<30} ${m.input_price_per_m:.2f}/${m.output_price_per_m:.2f} per M  |  {m.context_window//1000}K ctx  |  ~${cost:.5f}/1K tok')
        print()

    print('  Cheapest for code:', catalog.cheapest_for('code').display_name)
    print('  Cheapest for text:', catalog.cheapest_for('text').display_name)

    print('\n  Recommendations for "coding" (budget $0.01/req):')
    recs = catalog.recommend('coding', budget_per_request=0.01)
    for r in recs[:5]:
        print(f'    → {r.display_name} ({r.provider.value})')
