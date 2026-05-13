"""
AIM-OS AI Engine — Self-Improvement Loop

Layer 4: Agents audit themselves and evolve.

After every task completion, this system:
    1. Stores the outcome in CMC memory (via MCP store_memory)
    2. Tracks confidence on the result (via MCP track_confidence)
    3. Analyses thought patterns (via MCP analyze_thought_patterns)
    4. Retrieves similar past tasks (via MCP retrieve_memory)
    5. Adjusts model selection and prompts based on patterns

This is what makes AIM-OS agents self-improving:
they learn which models work best for which tasks,
which prompts produce better plans, and which patterns
lead to failures — then they adapt.
"""

import time
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger('ai_engine.self_improve')


# ── MCP Tool Wrapper ──────────────────────────────────────

class MCPBridge:
    """
    Bridge to AIM-OS MCP tools for self-improvement.
    Wraps the MCP tool calls so the engine can use them
    without depending on the MCP server being loaded.
    
    In production, these proxy to the actual MCP functions.
    In standalone mode, they write to local files.
    """

    def __init__(self):
        self._mcp_available = None
        self._local_memory: List[Dict] = []
        self._local_confidence: List[Dict] = []

    @property
    def mcp_available(self) -> bool:
        if self._mcp_available is None:
            try:
                # Try to import MCP functions
                from mcp_lucid_mcp import store_memory
                self._mcp_available = True
            except ImportError:
                self._mcp_available = False
        return self._mcp_available

    def store_memory(self, content: str, tags: Optional[Dict] = None) -> dict:
        """Store a memory via MCP or locally."""
        entry = {
            'content': content,
            'tags': tags or {},
            'timestamp': time.time(),
        }

        if self.mcp_available:
            try:
                from mcp_lucid_mcp import store_memory
                return store_memory(content=content, tags=tags or {})
            except Exception as e:
                logger.debug(f'MCP store_memory failed, using local: {e}')

        self._local_memory.append(entry)
        return {'stored': True, 'local': True, 'id': len(self._local_memory)}

    def track_confidence(
        self, task: str, confidence: float,
        reasoning: str = '', evidence: Optional[List[str]] = None,
    ) -> dict:
        """Track confidence via MCP or locally."""
        entry = {
            'task': task,
            'confidence': confidence,
            'reasoning': reasoning,
            'evidence': evidence or [],
            'timestamp': time.time(),
        }

        if self.mcp_available:
            try:
                from mcp_lucid_mcp import track_confidence
                return track_confidence(
                    task=task, confidence=confidence,
                    reasoning=reasoning, evidence=evidence or [],
                )
            except Exception as e:
                logger.debug(f'MCP track_confidence failed: {e}')

        self._local_confidence.append(entry)
        return {'tracked': True, 'local': True}

    def retrieve_memory(self, query: str, limit: int = 5) -> dict:
        """Retrieve memories via MCP or from local store."""
        if self.mcp_available:
            try:
                from mcp_lucid_mcp import retrieve_memory
                return retrieve_memory(query=query, limit=limit)
            except Exception as e:
                logger.debug(f'MCP retrieve_memory failed: {e}')

        # Local search
        results = []
        query_lower = query.lower()
        for entry in reversed(self._local_memory):
            if query_lower in entry['content'].lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return {'memories': results, 'local': True}

    def analyze_patterns(self, context: str, errors: Optional[List[str]] = None) -> dict:
        """Analyse thought patterns via MCP or return basic analysis."""
        if self.mcp_available:
            try:
                from mcp_lucid_mcp import analyze_thought_patterns
                return analyze_thought_patterns(
                    context=context,
                    recent_errors=errors or [],
                )
            except Exception as e:
                logger.debug(f'MCP analyze_thought_patterns failed: {e}')

        return {
            'analysis': 'Local analysis (MCP unavailable)',
            'patterns': [],
            'recommendations': [],
        }


# ── Self-Improver ────────────────────────────────────────

class SelfImprover:
    """
    The self-improvement engine for AIM-OS agents.
    
    After each task, analyses the outcome and stores learnings.
    Over time, builds a knowledge base of:
        - Which models work best for which task types
        - Which system prompts produce better results
        - Common failure patterns and their fixes
        - Codebase-specific conventions and patterns
    """

    def __init__(self):
        self.mcp = MCPBridge()
        self._improvement_log: List[Dict] = []
        self._model_scores: Dict[str, List[float]] = {}
        self._task_patterns: Dict[str, Dict] = {}

    def learn_from_task(
        self,
        task: str,
        agent_name: str,
        result: Any,  # TaskResult from agent_runtime
    ) -> bool:
        """
        Learn from a completed task execution.
        Called automatically by the Agent Runtime after every task.
        """
        try:
            success = result.status == 'completed' and result.steps_failed == 0
            confidence = 1.0 if success and result.verification_passed else (
                0.6 if success else 0.2
            )

            # 1. Store memory of the outcome
            memory_content = (
                f"[AI Engine Learning] Agent: {agent_name}\n"
                f"Task: {task[:200]}\n"
                f"Status: {result.status}\n"
                f"Steps: {result.steps_completed}/{result.steps_completed + result.steps_failed}\n"
                f"Verification: {'PASSED' if result.verification_passed else 'FAILED'}\n"
                f"Model: {result.model_used}\n"
                f"Time: {result.total_time_ms:.0f}ms\n"
                f"Files modified: {', '.join(result.files_modified[:5])}\n"
                f"Files created: {', '.join(result.files_created[:5])}"
            )

            if result.error:
                memory_content += f"\nError: {result.error}"

            self.mcp.store_memory(
                content=memory_content,
                tags={
                    'type': 'ai_engine_learning',
                    'agent': agent_name,
                    'success': success,
                    'model': result.model_used,
                },
            )

            # 2. Track confidence
            evidence = []
            if result.verification_passed:
                evidence.append('Verification passed')
            if result.steps_failed == 0:
                evidence.append(f'All {result.steps_completed} steps completed')
            if result.error:
                evidence.append(f'Error: {result.error}')

            self.mcp.track_confidence(
                task=f'[{agent_name}] {task[:100]}',
                confidence=confidence,
                reasoning=f'{result.steps_completed} steps completed, '
                          f'{result.steps_failed} failed, '
                          f'verification {"passed" if result.verification_passed else "failed"}',
                evidence=evidence,
            )

            # 3. Update model scores
            model = result.model_used or 'unknown'
            self._model_scores.setdefault(model, []).append(confidence)

            # Keep last 100 scores per model
            if len(self._model_scores[model]) > 100:
                self._model_scores[model] = self._model_scores[model][-100:]

            # 4. Analyse failure patterns
            if not success and result.error:
                self.mcp.analyze_patterns(
                    context=f'Agent {agent_name} failed on: {task[:100]}',
                    errors=[result.error],
                )

            # 5. Log improvement entry
            self._improvement_log.append({
                'timestamp': time.time(),
                'agent': agent_name,
                'task': task[:100],
                'success': success,
                'confidence': confidence,
                'model': model,
                'time_ms': result.total_time_ms,
            })

            # Keep last 200 entries
            if len(self._improvement_log) > 200:
                self._improvement_log = self._improvement_log[-200:]

            return True

        except Exception as e:
            logger.error(f'Self-improvement failed: {e}')
            return False

    def get_model_recommendation(self, task_type: str) -> str:
        """
        Recommend the best model for a task type
        based on historical performance data.
        """
        if not self._model_scores:
            return 'auto'

        best_model = 'auto'
        best_score = 0.0

        for model, scores in self._model_scores.items():
            avg = sum(scores) / len(scores)
            if avg > best_score:
                best_score = avg
                best_model = model

        return best_model

    def get_improvement_summary(self) -> dict:
        """Summary of self-improvement metrics."""
        total = len(self._improvement_log)
        successes = sum(1 for e in self._improvement_log if e['success'])

        model_stats = {}
        for model, scores in self._model_scores.items():
            model_stats[model] = {
                'avg_confidence': sum(scores) / len(scores) if scores else 0,
                'total_uses': len(scores),
            }

        return {
            'total_tasks_learned': total,
            'success_rate': successes / total if total > 0 else 0,
            'model_performance': model_stats,
            'mcp_available': self.mcp.mcp_available,
            'local_memories': len(self.mcp._local_memory),
            'local_confidence_entries': len(self.mcp._local_confidence),
            'recent_entries': self._improvement_log[-5:],
        }
