"""
AIM-OS Context Lab — Strategy Evolution Engine

Evolutionary testing for context strategies. Allows:
    - Forking strategies into variants with parameter mutations
    - Running tournaments across variant lineages
    - Tracking performance genealogy (parent → child)
    - Auto-selecting best performers
    - Persisting leaderboard history to JSON

Usage:
    evo = EvolutionManager()
    evo.fork('hhni_direct', 'hhni_deep', mutations={'max_results': 20})
    result = evo.tournament(['Audit registry', 'Review safety'])
    print(evo.leaderboard())
"""

import json
import os
import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger('ai_engine.agent_loop.evolution')


# ── Variant — a strategy with mutations applied ─────────

@dataclass
class StrategyVariant:
    """A named variant of a strategy with optional parameter mutations."""
    name: str                           # Unique variant name
    base_strategy: str                  # Registry name of parent strategy
    parent_variant: str = ''            # Parent variant ('' = original)
    mutations: Dict[str, Any] = field(default_factory=dict)
    generation: int = 0                 # 0 = original, 1 = first fork, etc.
    created_at: float = field(default_factory=time.time)
    variant_id: str = ''

    def __post_init__(self):
        if not self.variant_id:
            self.variant_id = f'v_{uuid.uuid4().hex[:8]}'

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VariantScore:
    """Performance record for a variant across tournament runs."""
    variant_name: str = ''
    runs: int = 0
    avg_quality: float = 0.0
    avg_time_ms: float = 0.0
    best_quality: float = 0.0
    worst_quality: float = 0.0
    total_quality_sum: float = 0.0
    total_time_sum: float = 0.0
    last_run: float = 0.0

    def record(self, quality: float, time_ms: float):
        """Add a new run to the score."""
        self.runs += 1
        self.total_quality_sum += quality
        self.total_time_sum += time_ms
        self.avg_quality = self.total_quality_sum / self.runs
        self.avg_time_ms = self.total_time_sum / self.runs
        self.best_quality = max(self.best_quality, quality)
        if self.worst_quality == 0.0 or quality < self.worst_quality:
            self.worst_quality = quality
        self.last_run = time.time()

    def to_dict(self) -> dict:
        return {
            'variant': self.variant_name,
            'runs': self.runs,
            'avg_quality': round(self.avg_quality, 4),
            'avg_time_ms': round(self.avg_time_ms, 1),
            'best': round(self.best_quality, 4),
            'worst': round(self.worst_quality, 4),
        }


# ── Evolution Manager ───────────────────────────────────

class EvolutionManager:
    """Manages strategy variants, evolution, and tournament history.

    Data is persisted to a JSON file in the agent_loop directory
    so that lineage history survives across sessions.
    """

    def __init__(self, data_dir: str = ''):
        self.data_dir = data_dir or os.path.join(_THIS_DIR, 'evolution_data')
        os.makedirs(self.data_dir, exist_ok=True)

        self.variants: Dict[str, StrategyVariant] = {}
        self.scores: Dict[str, VariantScore] = {}
        self.history: List[Dict[str, Any]] = []

        # Load existing state
        self._load()

        # Pre-register base strategies as generation-0 variants
        self._register_base_strategies()

    def _register_base_strategies(self):
        """Register original strategies as generation-0 variants."""
        import sys
        sys.path.insert(0, _THIS_DIR)
        try:
            from strategies import list_strategies
            for name, desc in list_strategies().items():
                if name not in self.variants:
                    self.variants[name] = StrategyVariant(
                        name=name,
                        base_strategy=name,
                        generation=0,
                    )
        except ImportError:
            logger.warning('Could not import strategies — base variants not registered')

    # ── Forking ──────────────────────────────────────────

    def fork(
        self,
        parent: str,
        child_name: str,
        mutations: Dict[str, Any] = None,
    ) -> StrategyVariant:
        """Fork a strategy/variant into a new variant with mutations.

        Args:
            parent: Name of parent variant (or base strategy)
            child_name: Name for the new variant
            mutations: Parameter overrides for the child

        Returns:
            The new StrategyVariant

        Example:
            evo.fork('hhni_direct', 'hhni_deep', {'max_results': 20})
        """
        if child_name in self.variants:
            raise ValueError(f"Variant '{child_name}' already exists")

        # Determine base strategy and generation
        if parent in self.variants:
            parent_var = self.variants[parent]
            base = parent_var.base_strategy
            gen = parent_var.generation + 1
            # Merge: parent mutations + new mutations
            merged = {**parent_var.mutations, **(mutations or {})}
        else:
            base = parent
            gen = 1
            merged = mutations or {}

        variant = StrategyVariant(
            name=child_name,
            base_strategy=base,
            parent_variant=parent,
            mutations=merged,
            generation=gen,
        )
        self.variants[child_name] = variant
        self._save()

        logger.info(f'Forked {parent} → {child_name} (gen {gen}, {len(merged)} mutations)')
        return variant

    # ── Tournament ───────────────────────────────────────

    def tournament(
        self,
        tasks: List[str],
        variant_names: List[str] = None,
        workspace_root: str = '',
    ) -> Dict[str, Any]:
        """Run a tournament across variants (or all variants).

        Args:
            tasks: Task descriptions to test
            variant_names: Variant names to compete (None = all)
            workspace_root: Working directory

        Returns:
            Tournament result dict with leaderboard and details
        """
        import sys
        sys.path.insert(0, _THIS_DIR)
        from strategies import get_strategy
        from quality import score_context_pack

        names = variant_names or list(self.variants.keys())
        results = []

        for task in tasks:
            for vname in names:
                variant = self.variants.get(vname)
                if not variant:
                    logger.warning(f'Unknown variant: {vname}')
                    continue

                try:
                    # Get base strategy with mutations applied as kwargs
                    strategy = get_strategy(
                        variant.base_strategy,
                        workspace_root=workspace_root,
                        **variant.mutations,
                    )

                    start = time.time()
                    pack = strategy.build_context(task)
                    elapsed_ms = (time.time() - start) * 1000

                    quality = score_context_pack(pack, task)

                    # Record in persistent scores
                    if vname not in self.scores:
                        self.scores[vname] = VariantScore(variant_name=vname)
                    self.scores[vname].record(quality.overall, elapsed_ms)

                    results.append({
                        'variant': vname,
                        'task': task,
                        'quality': quality.overall,
                        'time_ms': elapsed_ms,
                        'scores': quality.to_dict(),
                        'generation': variant.generation,
                        'success': True,
                    })

                except Exception as e:
                    logger.warning(f'Variant {vname} failed on "{task[:40]}": {e}')
                    results.append({
                        'variant': vname,
                        'task': task,
                        'quality': 0.0,
                        'time_ms': 0,
                        'error': str(e),
                        'success': False,
                    })

        # Save history
        entry = {
            'tournament_id': f'evo_{uuid.uuid4().hex[:8]}',
            'timestamp': time.time(),
            'tasks': tasks,
            'variants': names,
            'result_count': len(results),
        }
        self.history.append(entry)
        self._save()

        return {
            'tournament': entry,
            'results': results,
            'leaderboard': self.leaderboard(),
        }

    # ── Leaderboard ──────────────────────────────────────

    def leaderboard(self) -> List[Dict[str, Any]]:
        """Get ranked leaderboard from cumulative scores."""
        board = []
        for vname, score in self.scores.items():
            variant = self.variants.get(vname)
            board.append({
                **score.to_dict(),
                'generation': variant.generation if variant else 0,
                'parent': variant.parent_variant if variant else '',
                'base': variant.base_strategy if variant else vname,
            })

        board.sort(key=lambda x: x['avg_quality'], reverse=True)
        for i, entry in enumerate(board):
            entry['rank'] = i + 1
        return board

    def format_leaderboard(self) -> str:
        """Format leaderboard for display."""
        board = self.leaderboard()
        if not board:
            return 'No results yet. Run a tournament first.'

        lines = [
            '╔══════════════════════════════════════════════════════════╗',
            '║          EVOLUTION LEADERBOARD — All-Time              ║',
            '╚══════════════════════════════════════════════════════════╝',
            '',
            f"{'Rank':<6}{'Variant':<20}{'Gen':>4}{'Quality':>10}{'Time(ms)':>10}{'Runs':>6}",
            '─' * 56,
        ]

        for entry in board:
            medal = ['🥇', '🥈', '🥉'][entry['rank'] - 1] if entry['rank'] <= 3 else '  '
            gen_tag = f'G{entry["generation"]}' if entry['generation'] > 0 else 'G0'
            lines.append(
                f"{medal} {entry['rank']:<3}"
                f"{entry['variant']:<20}"
                f"{gen_tag:>4}"
                f"{entry['avg_quality']:>9.1%}"
                f"{entry['avg_time_ms']:>10.0f}"
                f"{entry['runs']:>6}"
            )

        lines.append('')
        lines.append(f'Total variants: {len(self.variants)}, Tournaments: {len(self.history)}')
        return '\n'.join(lines)

    # ── Lineage ──────────────────────────────────────────

    def lineage(self, variant_name: str) -> List[str]:
        """Get the ancestry chain for a variant (child → ... → root)."""
        chain = [variant_name]
        current = variant_name
        while current in self.variants:
            parent = self.variants[current].parent_variant
            if not parent or parent == current:
                break
            chain.append(parent)
            current = parent
        return chain

    def format_lineage_tree(self) -> str:
        """Format the full variant tree."""
        lines = ['── Strategy Lineage Tree ──', '']

        # Group by base strategy
        by_base: Dict[str, List[StrategyVariant]] = {}
        for v in self.variants.values():
            by_base.setdefault(v.base_strategy, []).append(v)

        for base, variants in sorted(by_base.items()):
            # Sort by generation
            variants.sort(key=lambda x: x.generation)
            for v in variants:
                indent = '  ' * v.generation
                score_info = ''
                if v.name in self.scores:
                    s = self.scores[v.name]
                    score_info = f'  ({s.avg_quality:.1%}, {s.runs} runs)'
                mut_info = f'  [{", ".join(f"{k}={v2}" for k, v2 in v.mutations.items())}]' if v.mutations else ''
                lines.append(f'{indent}{"└─ " if v.generation > 0 else ""}{v.name}{mut_info}{score_info}')
            lines.append('')

        return '\n'.join(lines)

    # ── Auto-Select ──────────────────────────────────────

    def best_variant(self, base_strategy: str = '') -> Optional[str]:
        """Get the best-performing variant, optionally filtered by base strategy."""
        board = self.leaderboard()
        for entry in board:
            if entry['runs'] >= 1:  # Must have at least 1 run
                if not base_strategy or entry['base'] == base_strategy:
                    return entry['variant']
        return None

    # ── Persistence ──────────────────────────────────────

    def _save(self):
        """Save evolution state to JSON."""
        state = {
            'variants': {n: v.to_dict() for n, v in self.variants.items()},
            'scores': {n: asdict(s) for n, s in self.scores.items()},
            'history': self.history[-100:],  # Keep last 100 tournaments
        }
        path = os.path.join(self.data_dir, 'evolution_state.json')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f'Failed to save evolution state: {e}')

    def _load(self):
        """Load evolution state from JSON."""
        path = os.path.join(self.data_dir, 'evolution_state.json')
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            for name, vdata in state.get('variants', {}).items():
                self.variants[name] = StrategyVariant(**{
                    k: v for k, v in vdata.items()
                    if k in StrategyVariant.__dataclass_fields__
                })

            for name, sdata in state.get('scores', {}).items():
                self.scores[name] = VariantScore(**{
                    k: v for k, v in sdata.items()
                    if k in VariantScore.__dataclass_fields__
                })

            self.history = state.get('history', [])
            logger.info(f'Loaded {len(self.variants)} variants, {len(self.scores)} scores')

        except Exception as e:
            logger.warning(f'Failed to load evolution state: {e}')
