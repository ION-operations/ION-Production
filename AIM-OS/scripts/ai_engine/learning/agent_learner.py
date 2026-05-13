"""
AIM-OS AI Engine — Agent Learner

Wave 4: Connects DaemonRAG's PatternLearner + AdaptiveLearner
to the AI Engine's self-improvement loop.

The Agent Learner analyses execution traces to:
    1. Learn which models work best for which task types
    2. Identify prompt patterns that lead to success/failure
    3. Adapt tool selection strategies based on outcomes
    4. Update agent parameters for future tasks
    5. Generate actionable improvement recommendations

This is the intelligence behind the self-improving agents.
"""

import os
import sys
import time
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from collections import defaultdict

from ai_engine.traces.execution_trace import ExecutionTrace, TraceOutcome

logger = logging.getLogger('ai_engine.agent_learner')


@dataclass
class LearningInsight:
    """An insight discovered from execution trace analysis."""
    insight_type: str        # model_preference, prompt_pattern, tool_selection, failure_pattern
    description: str
    confidence: float = 0.0
    evidence_count: int = 0
    recommendation: str = ''
    created_at: float = field(default_factory=time.time)


@dataclass
class ModelPerformance:
    """Tracks performance of a model across tasks."""
    model_name: str
    total_uses: int = 0
    successes: int = 0
    failures: int = 0
    avg_confidence: float = 0.0
    avg_time_ms: float = 0.0
    best_for: List[str] = field(default_factory=list)   # task types
    worst_for: List[str] = field(default_factory=list)


class AgentLearner:
    """
    Learns from execution traces and improves agent performance.
    
    Integrates with DaemonRAG's learning subsystem when available.
    Maintains its own learning state for model performance,
    prompt effectiveness, and tool selection patterns.
    """

    def __init__(self, workspace_root: str = ''):
        self.workspace_root = workspace_root or os.getcwd()

        # Learning state
        self._model_perf: Dict[str, ModelPerformance] = {}
        self._task_model_scores: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self._failure_patterns: List[Dict] = []
        self._insights: List[LearningInsight] = []

        # DaemonRAG integration
        self._pattern_learner = None
        self._adaptive_learner = None
        self._daemon_loaded = False

    def _load_daemon_learners(self):
        """Lazy-load DaemonRAG learning subsystems."""
        if self._daemon_loaded:
            return

        try:
            dag_path = os.path.join(self.workspace_root, 'daemon_rag_system')
            if dag_path not in sys.path:
                sys.path.insert(0, dag_path)

            from learning_system.learning_system import PatternLearner, AdaptiveLearner
            from rag_system.rag_engine import RAGSystem
            from tool_registry.tool_registry import ToolRegistry

            registry = ToolRegistry()
            rag = RAGSystem(registry)
            self._pattern_learner = PatternLearner(rag)
            self._adaptive_learner = AdaptiveLearner()
            logger.info('[AgentLearner] DaemonRAG learning subsystems loaded')
        except Exception as e:
            logger.debug(f'DaemonRAG learning not available: {e}')

        self._daemon_loaded = True

    def learn_from_trace(self, trace: ExecutionTrace) -> List[LearningInsight]:
        """
        Learn from a completed execution trace.
        Returns any new insights discovered.
        """
        self._load_daemon_learners()
        new_insights = []

        # 1. Update model performance
        model = trace.model_used or 'unknown'
        if model not in self._model_perf:
            self._model_perf[model] = ModelPerformance(model_name=model)

        perf = self._model_perf[model]
        perf.total_uses += 1
        success = trace.outcome == TraceOutcome.SUCCESS

        if success:
            perf.successes += 1
        else:
            perf.failures += 1

        # Running average
        perf.avg_confidence = (
            (perf.avg_confidence * (perf.total_uses - 1) + trace.confidence)
            / perf.total_uses
        )
        perf.avg_time_ms = (
            (perf.avg_time_ms * (perf.total_uses - 1) + trace.total_time_ms)
            / perf.total_uses
        )

        # Track model scores per task type
        if trace.task_type:
            score = trace.confidence if success else (trace.confidence * 0.3)
            self._task_model_scores[trace.task_type][model].append(score)

            # Keep last 50 scores per task-model pair
            scores = self._task_model_scores[trace.task_type][model]
            if len(scores) > 50:
                self._task_model_scores[trace.task_type][model] = scores[-50:]

        # 2. Analyse failure patterns
        if not success and trace.errors:
            pattern = {
                'task_type': trace.task_type,
                'agent': trace.agent_name,
                'model': model,
                'errors': trace.errors[:3],
                'timestamp': time.time(),
            }
            self._failure_patterns.append(pattern)

            # Keep last 100 failures
            if len(self._failure_patterns) > 100:
                self._failure_patterns = self._failure_patterns[-100:]

            # Check for repeated failure patterns
            similar_failures = sum(
                1 for f in self._failure_patterns[-20:]
                if f['task_type'] == trace.task_type and f['model'] == model
            )
            if similar_failures >= 3:
                insight = LearningInsight(
                    insight_type='failure_pattern',
                    description=f'Model {model} has {similar_failures} recent failures on {trace.task_type} tasks',
                    confidence=0.7,
                    evidence_count=similar_failures,
                    recommendation=f'Consider switching from {model} for {trace.task_type} tasks',
                )
                new_insights.append(insight)

        # 3. Model preference insights
        if perf.total_uses >= 5:
            rate = perf.successes / perf.total_uses
            if rate > 0.8 and trace.task_type and trace.task_type not in perf.best_for:
                perf.best_for.append(trace.task_type)
                insight = LearningInsight(
                    insight_type='model_preference',
                    description=f'{model} excels at {trace.task_type} (success rate: {rate:.0%})',
                    confidence=min(rate, perf.total_uses / 20),
                    evidence_count=perf.total_uses,
                    recommendation=f'Prefer {model} for {trace.task_type} tasks',
                )
                new_insights.append(insight)

        # 4. Feed DaemonRAG learners
        if self._pattern_learner:
            try:
                from learning_system.learning_system import LearningData, LearningPhase
                ld = LearningData(
                    context_profile={'task_type': trace.task_type, 'complexity': trace.complexity},
                    selected_tools=[],
                    outcome={'success': success, 'confidence': trace.confidence},
                    performance_metrics={
                        'time_ms': trace.total_time_ms,
                        'confidence': trace.confidence,
                    },
                    timestamp=time.time(),
                    learning_phase=LearningPhase.EXPLOITATION if perf.total_uses > 10 else LearningPhase.EXPLORATION,
                )
                self._pattern_learner.learn_from_data(ld)
            except Exception as e:
                logger.debug(f'DaemonRAG pattern learning failed: {e}')

        if self._adaptive_learner:
            try:
                self._adaptive_learner.adapt_learning({
                    'accuracy': trace.confidence,
                    'efficiency': max(0, 1.0 - trace.total_time_ms / 60000),
                    'reliability': 1.0 if success else 0.0,
                })
            except Exception as e:
                logger.debug(f'DaemonRAG adaptive learning failed: {e}')

        # Store insights
        self._insights.extend(new_insights)
        if len(self._insights) > 200:
            self._insights = self._insights[-200:]

        return new_insights

    def recommend_model(self, task_type: str) -> str:
        """Recommend the best model for a given task type."""
        if task_type not in self._task_model_scores:
            return 'auto'

        best_model = 'auto'
        best_score = 0.0

        for model, scores in self._task_model_scores[task_type].items():
            if len(scores) >= 3:
                avg = sum(scores) / len(scores)
                if avg > best_score:
                    best_score = avg
                    best_model = model

        return best_model

    def get_insights(self, limit: int = 10) -> List[LearningInsight]:
        """Get recent learning insights."""
        return self._insights[-limit:]

    def get_model_stats(self) -> Dict[str, dict]:
        """Get performance stats for all models."""
        return {
            model: {
                'total_uses': perf.total_uses,
                'success_rate': perf.successes / max(1, perf.total_uses),
                'avg_confidence': round(perf.avg_confidence, 3),
                'avg_time_ms': round(perf.avg_time_ms, 1),
                'best_for': perf.best_for,
            }
            for model, perf in self._model_perf.items()
        }

    def status(self) -> dict:
        return {
            'models_tracked': len(self._model_perf),
            'total_insights': len(self._insights),
            'failure_patterns': len(self._failure_patterns),
            'daemon_rag_learning': self._pattern_learner is not None,
            'daemon_rag_adaptive': self._adaptive_learner is not None,
            'task_types_tracked': list(self._task_model_scores.keys()),
        }
