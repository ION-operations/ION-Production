"""
AIM-OS AI Engine — API Cost Tracker

Real-time tracking of API spend across all providers.
Supports per-request logging, session/daily aggregation, budget alerts.

Usage:
    from providers.cost_tracker import CostTracker, get_tracker

    tracker = get_tracker()
    tracker.record_request('gpt-4o', input_tokens=1500, output_tokens=800)
    print(tracker.session_summary())
    print(tracker.total_cost)
"""

import os
import json
import time
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger('ai_engine.cost_tracker')


@dataclass
class RequestLog:
    """Single API request cost record."""
    timestamp: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: float = 0.0
    task_type: str = ''
    session_id: str = ''


class CostTracker:
    """
    Tracks API costs in real time across all providers.

    Features:
        - Per-request cost logging
        - Session / daily / total aggregation
        - Budget alerts (warn + hard limit)
        - Persist to JSON file
        - Cost breakdown by model and provider
    """

    def __init__(
        self,
        budget_warn: float = 1.0,
        budget_limit: float = 5.0,
        persist_path: Optional[str] = None,
    ):
        self.budget_warn = budget_warn
        self.budget_limit = budget_limit
        self._requests: List[RequestLog] = []
        self._session_start = time.time()
        self._session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Persistence
        if persist_path:
            self._persist_path = persist_path
        else:
            default_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'mcp_memory',
            )
            self._persist_path = os.path.join(default_dir, 'api_costs.json')

        self._load_history()

    def _load_history(self):
        """Load previous cost history from disk."""
        if os.path.exists(self._persist_path):
            try:
                with open(self._persist_path, 'r') as f:
                    data = json.load(f)
                self._requests = [
                    RequestLog(**entry) for entry in data.get('requests', [])
                ]
                logger.debug(f'Loaded {len(self._requests)} historical requests')
            except Exception as e:
                logger.warning(f'Failed to load cost history: {e}')

    def _save_history(self):
        """Persist cost history to disk."""
        try:
            os.makedirs(os.path.dirname(self._persist_path), exist_ok=True)
            # Keep last 1000 requests to avoid unbounded growth
            recent = self._requests[-1000:]
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_requests': len(self._requests),
                'total_cost': self.total_cost,
                'requests': [asdict(r) for r in recent],
            }
            with open(self._persist_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f'Failed to save cost history: {e}')

    # ── Recording ─────────────────────────────────────────

    def record_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider: str = '',
        latency_ms: float = 0.0,
        task_type: str = '',
        cost_override: Optional[float] = None,
    ) -> dict:
        """
        Record a completed API request.

        Returns dict with cost info and any budget alerts.
        """
        # Calculate cost
        if cost_override is not None:
            cost = cost_override
        else:
            from providers.model_catalog import get_catalog
            catalog = get_catalog()
            estimated = catalog.estimate_cost(model, input_tokens, output_tokens)
            cost = estimated if estimated is not None else 0.0
            if not provider:
                model_info = catalog.get(model)
                provider = model_info.provider.value if model_info else 'unknown'

        entry = RequestLog(
            timestamp=datetime.now().isoformat(),
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency_ms=latency_ms,
            task_type=task_type,
            session_id=self._session_id,
        )
        self._requests.append(entry)
        self._save_history()

        # Check budget
        alerts = []
        total = self.total_cost
        session = self.session_cost

        if total >= self.budget_limit:
            alerts.append({
                'level': 'BLOCK',
                'message': f'Budget limit reached: ${total:.4f} >= ${self.budget_limit:.2f}',
            })
        elif total >= self.budget_warn:
            alerts.append({
                'level': 'WARN',
                'message': f'Budget warning: ${total:.4f} >= ${self.budget_warn:.2f}',
            })

        result = {
            'cost': cost,
            'total_cost': total,
            'session_cost': session,
            'alerts': alerts,
            'budget_ok': total < self.budget_limit,
        }

        if alerts:
            for a in alerts:
                logger.warning(f'[CostTracker] {a["level"]}: {a["message"]}')

        return result

    def check_budget(self, estimated_cost: float = 0.0) -> dict:
        """Check if a request is within budget before sending."""
        projected = self.total_cost + estimated_cost
        return {
            'current_total': self.total_cost,
            'projected_total': projected,
            'budget_warn': self.budget_warn,
            'budget_limit': self.budget_limit,
            'within_budget': projected < self.budget_limit,
            'near_limit': projected >= self.budget_warn,
        }

    # ── Aggregation ───────────────────────────────────────

    @property
    def total_cost(self) -> float:
        """Total cost across all time."""
        return sum(r.cost for r in self._requests)

    @property
    def session_cost(self) -> float:
        """Cost for the current session only."""
        return sum(
            r.cost for r in self._requests
            if r.session_id == self._session_id
        )

    @property
    def today_cost(self) -> float:
        """Cost for today only."""
        today = datetime.now().strftime('%Y-%m-%d')
        return sum(
            r.cost for r in self._requests
            if r.timestamp.startswith(today)
        )

    def cost_by_model(self) -> Dict[str, float]:
        """Cost breakdown by model."""
        by_model: Dict[str, float] = {}
        for r in self._requests:
            by_model[r.model] = by_model.get(r.model, 0.0) + r.cost
        return dict(sorted(by_model.items(), key=lambda x: x[1], reverse=True))

    def cost_by_provider(self) -> Dict[str, float]:
        """Cost breakdown by provider."""
        by_provider: Dict[str, float] = {}
        for r in self._requests:
            by_provider[r.provider] = by_provider.get(r.provider, 0.0) + r.cost
        return dict(sorted(by_provider.items(), key=lambda x: x[1], reverse=True))

    # ── Reporting ─────────────────────────────────────────

    def session_summary(self) -> dict:
        """Summary for the current session."""
        session_reqs = [
            r for r in self._requests
            if r.session_id == self._session_id
        ]
        total_in = sum(r.input_tokens for r in session_reqs)
        total_out = sum(r.output_tokens for r in session_reqs)

        return {
            'session_id': self._session_id,
            'requests': len(session_reqs),
            'total_input_tokens': total_in,
            'total_output_tokens': total_out,
            'session_cost': self.session_cost,
            'all_time_cost': self.total_cost,
            'today_cost': self.today_cost,
            'budget': {
                'warn': self.budget_warn,
                'limit': self.budget_limit,
                'remaining': max(0, self.budget_limit - self.total_cost),
            },
        }

    def status(self) -> dict:
        """Full tracker status."""
        return {
            'total_requests': len(self._requests),
            'total_cost': round(self.total_cost, 6),
            'session_cost': round(self.session_cost, 6),
            'today_cost': round(self.today_cost, 6),
            'by_model': self.cost_by_model(),
            'by_provider': self.cost_by_provider(),
            'budget': {
                'warn': self.budget_warn,
                'limit': self.budget_limit,
                'within_budget': self.total_cost < self.budget_limit,
                'remaining': round(max(0, self.budget_limit - self.total_cost), 6),
            },
            'persist_path': self._persist_path,
        }

    def reset_session(self):
        """Start a new session."""
        self._session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._session_start = time.time()


# ── Singleton ─────────────────────────────────────────────

_tracker: Optional[CostTracker] = None


def get_tracker(
    budget_warn: float = 1.0,
    budget_limit: float = 5.0,
) -> CostTracker:
    """Get the global cost tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = CostTracker(
            budget_warn=budget_warn,
            budget_limit=budget_limit,
        )
    return _tracker


# ── Quick Test ────────────────────────────────────────────

if __name__ == '__main__':
    tracker = CostTracker(budget_warn=0.50, budget_limit=2.00, persist_path='/tmp/test_costs.json')

    # Simulate some requests
    r1 = tracker.record_request('gpt-4o', input_tokens=2000, output_tokens=1000)
    r2 = tracker.record_request('gemini-2.5-flash', input_tokens=5000, output_tokens=2000)
    r3 = tracker.record_request('deepseek-chat', input_tokens=10000, output_tokens=5000)

    print('╔════════════════════════════════════════════════════════════╗')
    print('║   AIM-OS Cost Tracker — Test                             ║')
    print('╚════════════════════════════════════════════════════════════╝')
    print()
    print(f'  Request 1 (gpt-4o):           ${r1["cost"]:.6f}')
    print(f'  Request 2 (gemini-2.5-flash): ${r2["cost"]:.6f}')
    print(f'  Request 3 (deepseek-chat):    ${r3["cost"]:.6f}')
    print(f'  ─────────────────────────────────────')
    print(f'  Total:                        ${tracker.total_cost:.6f}')
    print(f'  Budget remaining:             ${max(0, tracker.budget_limit - tracker.total_cost):.6f}')
    print()

    summary = tracker.session_summary()
    print(f'  Session requests: {summary["requests"]}')
    print(f'  Total tokens:     {summary["total_input_tokens"]} in / {summary["total_output_tokens"]} out')
