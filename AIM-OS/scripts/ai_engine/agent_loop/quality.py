"""
AIM-OS Context Lab — Context Quality Metrics

Scoring system for evaluating context quality independent of the
worker's output. Measures how GOOD the context was — not how good
the worker performed with it.

Metrics:
    coverage      — Does the context include relevant files/memories?
    specificity   — Is the context focused on the task, not bloated?
    freshness     — Are recent changes and state reflected?
    token_efficiency — How much of the budget was actually useful?
    diversity     — Does context span multiple evidence sources?
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_AGENT_LOOP_DIR = os.path.dirname(_THIS_DIR) if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'strategies' else os.path.dirname(os.path.abspath(__file__))

import importlib.util as _ilu
_mf = os.path.join(_AGENT_LOOP_DIR, 'models.py')
if os.path.exists(_mf):
    _sp = _ilu.spec_from_file_location('_loop_models', _mf)
    _m = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_m)
    ContextPack = _m.ContextPack
else:
    ContextPack = None

logger = logging.getLogger('ai_engine.agent_loop.quality')


@dataclass
class ContextQualityScore:
    """Detailed quality assessment of a context pack."""

    # Core dimensions (0.0 to 1.0)
    coverage: float = 0.0       # How much relevant info was included
    specificity: float = 0.0    # How focused vs bloated
    freshness: float = 0.0      # How current the context is
    token_efficiency: float = 0.0  # Useful tokens / total tokens
    diversity: float = 0.0      # Source variety

    # Composite
    overall: float = 0.0        # Weighted average of all dimensions

    # Metadata
    details: Dict[str, Any] = field(default_factory=dict)
    scored_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            'coverage': round(self.coverage, 3),
            'specificity': round(self.specificity, 3),
            'freshness': round(self.freshness, 3),
            'token_efficiency': round(self.token_efficiency, 3),
            'diversity': round(self.diversity, 3),
            'overall': round(self.overall, 3),
        }


# ── Weights for the composite score ──────────────────────

QUALITY_WEIGHTS = {
    'coverage': 0.30,
    'specificity': 0.25,
    'freshness': 0.15,
    'token_efficiency': 0.15,
    'diversity': 0.15,
}


def score_context_pack(
    pack: Any,
    task: str,
    max_tokens: int = 32000,
) -> ContextQualityScore:
    """Score a ContextPack on multiple quality dimensions.

    Works with either the agent loop ContextPack or the
    engine's ContextPack — both have similar fields.
    """
    score = ContextQualityScore()
    details: Dict[str, Any] = {}

    # ── Coverage ──────────────────────────────────────
    # Measure: does the pack include relevant content?
    task_words = set(task.lower().split())
    pack_text = ''

    if hasattr(pack, 'to_prompt'):
        pack_text = pack.to_prompt().lower()
    elif hasattr(pack, 'get_content'):
        pack_text = pack.get_content().lower()
    elif hasattr(pack, 'task_summary'):
        parts = [
            getattr(pack, 'task_summary', ''),
            getattr(pack, 'project_state', ''),
            getattr(pack, 'instructions', ''),
            getattr(pack, 'research_notes', ''),
        ]
        pack_text = ' '.join(str(p) for p in parts).lower()

    if task_words and pack_text:
        matched = sum(1 for w in task_words if w in pack_text and len(w) > 3)
        meaningful_words = [w for w in task_words if len(w) > 3]
        score.coverage = matched / max(len(meaningful_words), 1)
    else:
        score.coverage = 0.0

    # File presence boosts coverage
    files = getattr(pack, 'files_to_examine', [])
    if files:
        score.coverage = min(1.0, score.coverage + 0.2)

    details['task_word_matches'] = int(score.coverage * len(task_words))
    details['files_count'] = len(files) if files else 0

    # ── Specificity ──────────────────────────────────
    # Measure: is the context focused, not bloated?
    pack_length = len(pack_text)
    tokens_used = getattr(pack, 'tokens_used', 0) or getattr(pack, 'total_tokens', 0) or int(pack_length / 3.5)

    if tokens_used > 0 and pack_length > 0:
        # Penalize very short (< 500 tokens) or very bloated (> 80% budget)
        ratio = tokens_used / max_tokens
        if ratio < 0.05:
            score.specificity = 0.3  # Too little
        elif ratio > 0.9:
            score.specificity = 0.4  # Probably over-bloated
        elif 0.2 <= ratio <= 0.7:
            score.specificity = 0.9  # Sweet spot
        else:
            score.specificity = 0.7  # Reasonable
    else:
        score.specificity = 0.2

    details['tokens_used'] = tokens_used
    details['budget_ratio'] = round(tokens_used / max_tokens, 3) if max_tokens > 0 else 0

    # ── Freshness ────────────────────────────────────
    # Measure: does context include recent state?
    has_git = 'git' in pack_text or 'diff' in pack_text
    has_history = bool(getattr(pack, 'relevant_history', ''))
    has_recent = 'recent' in pack_text or 'current' in pack_text

    freshness_signals = [has_git, has_history, has_recent]
    score.freshness = sum(freshness_signals) / len(freshness_signals) if freshness_signals else 0.3
    details['has_git_context'] = has_git
    details['has_history'] = has_history

    # ── Token Efficiency ─────────────────────────────
    # Measure: useful content vs filler
    if pack_length > 0:
        # Check for repetition (simple heuristic: unique words / total words)
        words = pack_text.split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            score.token_efficiency = min(1.0, unique_ratio * 1.5)
        else:
            score.token_efficiency = 0.0
    else:
        score.token_efficiency = 0.0

    details['uniqueness_ratio'] = round(score.token_efficiency, 3)

    # ── Diversity ────────────────────────────────────
    # Measure: are multiple evidence sources represented?
    source_signals = {
        'files': bool(files),
        'memory': 'cmc' in pack_text or 'memory' in pack_text,
        'search': 'search' in pack_text or 'hhni' in pack_text,
        'history': has_history,
        'analysis': 'analysis' in pack_text or 'daemon' in pack_text,
    }
    active_sources = sum(source_signals.values())
    score.diversity = min(1.0, active_sources / 3.0)
    details['active_sources'] = {k: v for k, v in source_signals.items() if v}

    # ── Composite Score ──────────────────────────────
    score.overall = sum(
        getattr(score, dim) * weight
        for dim, weight in QUALITY_WEIGHTS.items()
    )

    score.details = details
    return score


def compare_quality_scores(
    scores: Dict[str, ContextQualityScore],
) -> str:
    """Format a comparison table of quality scores from multiple strategies."""
    if not scores:
        return 'No scores to compare'

    lines = ['═══ Context Quality Comparison ═══', '']

    # Header
    names = list(scores.keys())
    dims = ['coverage', 'specificity', 'freshness', 'token_efficiency', 'diversity', 'overall']
    header = f"{'Metric':<20}" + ''.join(f'{n:>14}' for n in names)
    lines.append(header)
    lines.append('─' * len(header))

    # Rows
    for dim in dims:
        row = f'{dim:<20}'
        values = [getattr(scores[n], dim) for n in names]
        best = max(values) if values else 0
        for val in values:
            marker = ' ★' if val == best and len(names) > 1 else '  '
            row += f'{val:>11.1%}{marker}'
        lines.append(row)

    lines.append('')

    # Winner
    overall_scores = {n: s.overall for n, s in scores.items()}
    winner = max(overall_scores, key=overall_scores.get)
    lines.append(f'🏆 Best overall: {winner} ({overall_scores[winner]:.1%})')

    return '\n'.join(lines)
