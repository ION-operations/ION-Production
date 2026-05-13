"""
AIM-OS Context Lab — Strategy Plugin System

Swappable strategies for Phase 1 (Context Researcher) of the 3-phase loop.
Each strategy implements `build_context()` to produce a ContextPack using
different AIM-OS context systems.

Available strategies:
    llm_research     — LLM analyzes task via Gemini CLI (current default)
    pack_builder     — Uses ContextPackBuilder 4-stage pipeline
    hhni_direct      — HHNI semantic retrieval + CMC atoms
    hybrid           — Multi-source fusion with deduplication
"""

from abc import ABC, abstractmethod
import time
import logging
from typing import Optional, Dict, Any

import os
import sys

# Path setup
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_AGENT_LOOP_DIR = os.path.dirname(_THIS_DIR)
_AI_ENGINE_DIR = os.path.dirname(_AGENT_LOOP_DIR)
_SCRIPTS_DIR = os.path.dirname(_AI_ENGINE_DIR)
_AIMOS_ROOT = os.path.dirname(_SCRIPTS_DIR)

for p in [_AIMOS_ROOT, _AI_ENGINE_DIR, _AGENT_LOOP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Import models via file path (avoids resolving to heavy installed packages)
_models_file = os.path.join(_AGENT_LOOP_DIR, 'models.py')
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('agent_loop_models', _models_file)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ContextPack = _mod.ContextPack
Handoff = _mod.Handoff

logger = logging.getLogger('ai_engine.agent_loop.strategies')


class ContextStrategy(ABC):
    """Base class for all context-building strategies."""

    name: str = 'base'
    description: str = 'Abstract base strategy'

    def __init__(self, workspace_root: str = '', **kwargs):
        self.workspace_root = workspace_root or _AIMOS_ROOT
        self._metrics: Dict[str, Any] = {}

    @abstractmethod
    def build_context(
        self,
        task: str,
        handoff: Optional[Handoff] = None,
        **kwargs,
    ) -> ContextPack:
        """Build a ContextPack for the given task."""
        ...

    @property
    def metrics(self) -> Dict[str, Any]:
        return self._metrics

    def status(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'workspace': self.workspace_root,
            'last_metrics': self._metrics,
        }


# ── Strategy Registry (LAZY — no eager imports) ─────────

_REGISTRY: Dict[str, type] = {}

# Map of name → (module_name, class_name) for lazy loading
_LAZY_MAP: Dict[str, tuple] = {
    'llm_research': ('strategies.llm_strategy', 'LLMResearchStrategy'),
    'pack_builder': ('strategies.pack_builder_strategy', 'PackBuilderStrategy'),
    'hhni_direct': ('strategies.hhni_strategy', 'HHNIStrategy'),
    'hybrid': ('strategies.hybrid_strategy', 'HybridStrategy'),
    'atlas': ('strategies.atlas_strategy', 'AtlasStrategy'),
}


def register_strategy(cls):
    """Decorator to register a strategy class."""
    _REGISTRY[cls.name] = cls
    return cls


def _lazy_load(name: str):
    """Lazily load and register a strategy."""
    if name in _REGISTRY:
        return
    if name not in _LAZY_MAP:
        return

    mod_name, cls_name = _LAZY_MAP[name]
    try:
        import importlib
        mod = importlib.import_module(f'.{mod_name.split(".")[-1]}', package='strategies')
        cls = getattr(mod, cls_name)
        _REGISTRY[name] = cls
    except ImportError:
        # Direct import fallback
        mod_file = os.path.join(_THIS_DIR, mod_name.split('.')[-1] + '.py')
        if os.path.exists(mod_file):
            import importlib.util
            spec = importlib.util.spec_from_file_location(mod_name, mod_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            cls = getattr(mod, cls_name)
            _REGISTRY[name] = cls


def get_strategy(name: str, **kwargs) -> ContextStrategy:
    """Get a strategy instance by name (lazy-loaded)."""
    _lazy_load(name)
    if name not in _REGISTRY:
        available = ', '.join(list(_REGISTRY.keys()) + list(_LAZY_MAP.keys()))
        raise ValueError(f"Unknown strategy '{name}'. Available: {available}")
    return _REGISTRY[name](**kwargs)


def list_strategies() -> Dict[str, str]:
    """List all available strategies (both loaded and lazy)."""
    result = {}
    # Include already-loaded
    for name, cls in _REGISTRY.items():
        result[name] = cls.description
    # Include lazy (not yet loaded)
    descriptions = {
        'llm_research': 'LLM analyzes task + calls MCP (original default)',
        'pack_builder': 'ContextPackBuilder 4-stage pipeline',
        'hhni_direct': 'HHNI semantic retrieval + CMC atoms (fast)',
        'hybrid': 'Multi-source fusion with deduplication',
        'atlas': 'Atlas knowledge graph — architecture-level context (fast)',
    }
    for name in _LAZY_MAP:
        if name not in result:
            result[name] = descriptions.get(name, '')
    return result

