"""
AIM-OS AI Engine — Tool Advisor

Wave 2: Wraps DaemonRAG's ToolFilter → RelevanceScorer → PerformanceOptimizer
to provide intelligent tool recommendations for swarm workers.

Each worker gets told which MCP tools are relevant for their task,
based on context analysis and historical performance — not just a
flat list of all 92+ tools.
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger('ai_engine.tool_advisor')


@dataclass
class ToolRecommendation:
    """A recommended tool with relevance score."""
    tool_id: str
    score: float = 0.0
    reason: str = ''
    category: str = ''


@dataclass
class ToolAdvice:
    """Tool advice for a worker or task."""
    recommended_tools: List[ToolRecommendation] = field(default_factory=list)
    required_servers: List[str] = field(default_factory=list)
    total_tools: int = 0
    selection_time_ms: float = 0.0
    strategy: str = 'balanced'
    source: str = 'heuristic'  # 'daemon_rag' or 'heuristic'


class ToolAdvisor:
    """
    Advises workers on which MCP tools to use.
    
    Integrates DaemonRAG's tool selection pipeline:
        ToolFilter → RelevanceScorer → PerformanceOptimizer
    
    Falls back to heuristic-based recommendations
    when DaemonRAG is unavailable.
    """

    # Heuristic tool recommendations by task type
    TASK_TOOLS = {
        'coding': [
            'store_memory', 'retrieve_memory', 'track_confidence',
            'get_file_problems', 'get_problem_summary',
        ],
        'debugging': [
            'get_file_problems', 'get_problem_summary', 'get_problems',
            'retrieve_memory', 'track_confidence', 'get_unified_diagnostics',
        ],
        'planning': [
            'create_plan', 'retrieve_memory', 'store_memory',
            'synthesize_knowledge', 'track_confidence',
        ],
        'review': [
            'get_file_problems', 'get_problems', 'track_confidence',
            'store_memory', 'run_cognitive_audit',
        ],
        'research': [
            'retrieve_memory', 'deepsearch', 'icip_search',
            'synthesize_knowledge', 'store_memory',
        ],
        'self_improvement': [
            'store_memory', 'retrieve_memory', 'track_confidence',
            'analyze_thought_patterns', 'run_cognitive_audit',
        ],
        'collaboration': [
            'send_ai_message', 'get_ai_messages', 'handoff_task_to_ai',
            'get_ai_collaboration_summary',
        ],
    }

    def __init__(self, workspace_root: str = ''):
        self.workspace_root = workspace_root or os.getcwd()
        self._daemon_rag = None
        self._daemon_available = None

    def _load_daemon_rag(self):
        """Lazy-load DaemonRAG tool selection engine."""
        if self._daemon_available is not None:
            return self._daemon_rag

        try:
            dag_path = os.path.join(self.workspace_root, 'daemon_rag_system')
            if dag_path not in sys.path:
                sys.path.insert(0, dag_path)

            from tool_registry.tool_registry import ToolRegistry
            from tool_selection_engine.tool_selector import ToolSelectionEngine

            registry = ToolRegistry()
            self._daemon_rag = ToolSelectionEngine(registry)
            self._daemon_available = True
            logger.info('[ToolAdvisor] DaemonRAG ToolSelectionEngine loaded')
        except Exception as e:
            logger.debug(f'DaemonRAG tool selection not available: {e}')
            self._daemon_available = False
        return self._daemon_rag

    def advise(
        self,
        task_type: str = 'general',
        context_profile: Optional[Dict] = None,
        max_tools: int = 15,
    ) -> ToolAdvice:
        """
        Get tool recommendations for a task.
        
        Args:
            task_type: Type of task (coding, debugging, planning, etc.)
            context_profile: Optional context analysis result
            max_tools: Maximum tools to recommend
        """
        start = time.time()

        dag = self._load_daemon_rag()
        if dag and context_profile:
            try:
                from tool_selection_engine.tool_selector import SelectionStrategy
                result = dag.select_tools(
                    context_profile=context_profile,
                    strategy=SelectionStrategy.BALANCED,
                )
                recs = [
                    ToolRecommendation(
                        tool_id=t,
                        score=getattr(result, 'total_score', 0.5),
                        reason='DaemonRAG selection',
                    )
                    for t in result.selected_tools[:max_tools]
                ]
                return ToolAdvice(
                    recommended_tools=recs,
                    total_tools=len(recs),
                    selection_time_ms=(time.time() - start) * 1000,
                    strategy='balanced',
                    source='daemon_rag',
                )
            except Exception as e:
                logger.debug(f'DaemonRAG selection failed: {e}')

        # Heuristic fallback
        tool_ids = self.TASK_TOOLS.get(task_type, self.TASK_TOOLS.get('coding', []))
        recs = [
            ToolRecommendation(tool_id=t, score=0.5, reason=f'Heuristic: {task_type}')
            for t in tool_ids[:max_tools]
        ]

        return ToolAdvice(
            recommended_tools=recs,
            total_tools=len(recs),
            selection_time_ms=(time.time() - start) * 1000,
            strategy='heuristic',
            source='heuristic',
        )
