"""
AIM-OS AI Engine — Agent Registry

Wave 5a: Central registry of all agent types and their capabilities.

The registry is the single source of truth for what agents exist,
their roles, allowed tools, model preferences, and genome linkage.
The Orchestrator queries the registry to find the best agent/worker
for any given JobPacket.

PersistentAgentRegistry (SCOUT improvement): saves performance metrics
to a JSON file so they survive process restarts.
"""

import os
import json
import time
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger('ai_engine.registry')


class AgentStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DEGRADED = 'degraded'
    RETIRED = 'retired'


@dataclass
class AgentCapability:
    """A capability an agent can perform."""
    name: str
    proficiency: float = 0.7   # 0.0 to 1.0
    tool_subset: List[str] = field(default_factory=list)


@dataclass
class AgentDefinition:
    """
    Complete definition of an agent type in the registry.
    """
    # Identity
    agent_id: str
    name: str
    role: str                     # coder, architect, auditor, researcher, tester
    description: str = ''

    # Capabilities
    capabilities: List[AgentCapability] = field(default_factory=list)
    task_types: List[str] = field(default_factory=list)   # which task types this agent handles

    # Model preference
    model_preference: str = 'auto'
    model_fallbacks: List[str] = field(default_factory=list)

    # Permissions (capability tokens)
    allowed_actions: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=list)
    max_file_edits: int = 20
    can_run_commands: bool = True

    # Genome linkage
    genome_file: str = ''          # path in .agent/genomes/
    genome_role_overlay: str = ''  # built-in role overlay name

    # Performance tracking
    total_tasks: int = 0
    success_rate: float = 0.0
    avg_confidence: float = 0.0

    # State
    status: str = AgentStatus.ACTIVE
    registered_at: float = field(default_factory=time.time)


class AgentRegistry:
    """
    Central registry of all agent types.
    
    Usage:
        registry = AgentRegistry()
        best_agent = registry.find_best_for(task_type='debugging')
        agent_def = registry.get('coder_v1')
    """

    def __init__(self):
        self._agents: Dict[str, AgentDefinition] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register all built-in agent types."""
        self.register(AgentDefinition(
            agent_id='coder_v1',
            name='Coder',
            role='coder',
            description='Primary code-generation agent. Writes production-quality code with strict typing.',
            capabilities=[
                AgentCapability('code_generation', 0.9),
                AgentCapability('bug_fixing', 0.8),
                AgentCapability('refactoring', 0.7),
                AgentCapability('test_writing', 0.6),
            ],
            task_types=['coding', 'debugging', 'refactoring'],
            model_preference='code-edit',
            model_fallbacks=['gemini-2.0-flash', 'gemini-2.5-pro'],
            allowed_actions=['file:read', 'file:write', 'file:create', 'command:run'],
            forbidden_actions=['file:delete', 'mcp:mutate_orchestration'],
            genome_role_overlay='coder',
        ))

        self.register(AgentDefinition(
            agent_id='architect_v1',
            name='Architect',
            role='architect',
            description='Systems architect for analysis, decomposition, and strategic planning.',
            capabilities=[
                AgentCapability('system_analysis', 0.9),
                AgentCapability('task_decomposition', 0.9),
                AgentCapability('design_review', 0.8),
                AgentCapability('tradeoff_analysis', 0.85),
            ],
            task_types=['planning', 'research', 'analysis'],
            model_preference='deep-think',
            model_fallbacks=['gemini-2.5-pro', 'gemini-2.0-flash-thinking'],
            allowed_actions=['file:read', 'command:run'],
            forbidden_actions=['file:write', 'file:create', 'file:delete'],
            genome_role_overlay='architect',
        ))

        self.register(AgentDefinition(
            agent_id='auditor_v1',
            name='Auditor',
            role='auditor',
            description='Code reviewer and quality engineer. Reviews, does not edit.',
            capabilities=[
                AgentCapability('code_review', 0.9),
                AgentCapability('security_analysis', 0.8),
                AgentCapability('performance_review', 0.7),
                AgentCapability('style_check', 0.6),
            ],
            task_types=['review', 'audit', 'self_improvement'],
            model_preference='deep-think',
            model_fallbacks=['gemini-2.5-pro'],
            allowed_actions=['file:read', 'command:run'],
            forbidden_actions=['file:write', 'file:create', 'file:delete'],
            genome_role_overlay='auditor',
        ))

        self.register(AgentDefinition(
            agent_id='researcher_v1',
            name='Researcher',
            role='researcher',
            description='Deep research specialist for comprehensive information gathering.',
            capabilities=[
                AgentCapability('information_gathering', 0.9),
                AgentCapability('synthesis', 0.8),
                AgentCapability('citation', 0.7),
            ],
            task_types=['research', 'analysis'],
            model_preference='deep-think',
            model_fallbacks=['gemini-2.5-pro', 'gemini-2.0-flash-thinking'],
            allowed_actions=['file:read'],
            forbidden_actions=['file:write', 'file:create', 'file:delete', 'command:run'],
            genome_role_overlay='researcher',
        ))

        self.register(AgentDefinition(
            agent_id='tester_v1',
            name='Tester',
            role='tester',
            description='QA engineer for writing and running tests.',
            capabilities=[
                AgentCapability('test_writing', 0.9),
                AgentCapability('test_execution', 0.85),
                AgentCapability('coverage_analysis', 0.7),
            ],
            task_types=['testing', 'verification'],
            model_preference='code-edit',
            model_fallbacks=['gemini-2.0-flash'],
            allowed_actions=['file:read', 'file:write', 'file:create', 'command:run'],
            forbidden_actions=['file:delete'],
            genome_role_overlay='tester',
        ))

        self.register(AgentDefinition(
            agent_id='fast_v1',
            name='Fast Worker',
            role='coder',
            description='Quick tasks under 1 min: small fixes, file reads, simple queries.',
            capabilities=[
                AgentCapability('quick_fix', 0.8),
                AgentCapability('file_search', 0.7),
            ],
            task_types=['fast', 'query'],
            model_preference='fast',
            model_fallbacks=['gemini-2.0-flash'],
            allowed_actions=['file:read', 'file:write', 'command:run'],
            forbidden_actions=['file:delete', 'mcp:mutate_orchestration'],
            genome_role_overlay='coder',
            max_file_edits=5,
        ))

    def register(self, agent: AgentDefinition) -> None:
        """Register an agent in the registry."""
        self._agents[agent.agent_id] = agent
        logger.info(f'[Registry] Registered agent {agent.agent_id} ({agent.role})')

    def get(self, agent_id: str) -> Optional[AgentDefinition]:
        """Get an agent definition by ID."""
        return self._agents.get(agent_id)

    def find_best_for(
        self,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
    ) -> Optional[AgentDefinition]:
        """
        Find the best agent for a given task type.
        Uses capability proficiency + success rate.
        """
        candidates = [
            a for a in self._agents.values()
            if task_type in a.task_types and a.status == AgentStatus.ACTIVE
        ]

        if not candidates:
            # Fallback to coder
            return self._agents.get('coder_v1')

        if required_capabilities:
            # Filter by required capabilities
            filtered = []
            for agent in candidates:
                agent_caps = {c.name for c in agent.capabilities}
                if all(req in agent_caps for req in required_capabilities):
                    filtered.append(agent)
            if filtered:
                candidates = filtered

        # Score: capability proficiency + success rate
        def score(a: AgentDefinition) -> float:
            cap_score = max((c.proficiency for c in a.capabilities), default=0.5)
            perf_score = a.success_rate if a.total_tasks > 0 else 0.5
            return cap_score * 0.6 + perf_score * 0.4

        return max(candidates, key=score)

    def list_all(self) -> List[AgentDefinition]:
        """List all registered agents."""
        return list(self._agents.values())

    def list_by_role(self, role: str) -> List[AgentDefinition]:
        """List agents by role."""
        return [a for a in self._agents.values() if a.role == role]

    def update_performance(
        self,
        agent_id: str,
        success: bool,
        confidence: float,
    ) -> None:
        """Update an agent's performance metrics after task completion."""
        agent = self._agents.get(agent_id)
        if not agent:
            return

        agent.total_tasks += 1
        if success:
            agent.success_rate = (
                (agent.success_rate * (agent.total_tasks - 1) + 1.0)
                / agent.total_tasks
            )
        else:
            agent.success_rate = (
                (agent.success_rate * (agent.total_tasks - 1))
                / agent.total_tasks
            )

        agent.avg_confidence = (
            (agent.avg_confidence * (agent.total_tasks - 1) + confidence)
            / agent.total_tasks
        )

    def status(self) -> dict:
        return {
            'total_agents': len(self._agents),
            'active': sum(1 for a in self._agents.values() if a.status == AgentStatus.ACTIVE),
            'agents': {
                aid: {
                    'role': a.role,
                    'tasks': a.total_tasks,
                    'success_rate': round(a.success_rate, 3),
                    'status': a.status,
                }
                for aid, a in self._agents.items()
            },
        }


# ── SCOUT Improvement: Persistent Registry ─────────────────

class PersistentAgentRegistry(AgentRegistry):
    """
    Improved AgentRegistry with JSON persistence.
    
    Based on SCOUT's AbilityAudit finding:
        'The AgentRegistry initializes with hardcoded defaults. Any
        performance metrics updated during a session are lost when
        the process terminates.'
    
    This subclass auto-saves performance metrics to a JSON file
    after every update, so they survive restarts.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), 'agent_metrics.json'
        )
        super().__init__()
        self._load_metrics()

    def _save_metrics(self) -> None:
        """Save only performance metrics (not full definitions) to JSON."""
        try:
            metrics = {}
            for aid, agent in self._agents.items():
                metrics[aid] = {
                    'total_tasks': agent.total_tasks,
                    'success_rate': agent.success_rate,
                    'avg_confidence': agent.avg_confidence,
                    'status': agent.status,
                }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2)
            logger.debug(f'[PersistentRegistry] Saved metrics for {len(metrics)} agents')
        except Exception as e:
            logger.error(f'[PersistentRegistry] Failed to save: {e}')

    def _load_metrics(self) -> None:
        """Load performance metrics from JSON and apply to registered agents."""
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            for aid, data in metrics.items():
                agent = self._agents.get(aid)
                if agent:
                    agent.total_tasks = data.get('total_tasks', 0)
                    agent.success_rate = data.get('success_rate', 0.0)
                    agent.avg_confidence = data.get('avg_confidence', 0.0)
                    if 'status' in data:
                        agent.status = data['status']
            logger.info(f'[PersistentRegistry] Loaded metrics for {len(metrics)} agents')
        except Exception as e:
            logger.error(f'[PersistentRegistry] Failed to load: {e}')

    def update_performance(
        self,
        agent_id: str,
        success: bool,
        confidence: float,
    ) -> None:
        """Update metrics and auto-save to disk."""
        super().update_performance(agent_id, success, confidence)
        self._save_metrics()

    def status(self) -> dict:
        """Extended status with persistence info."""
        base = super().status()
        base['persistence'] = {
            'enabled': True,
            'storage_path': self.storage_path,
            'file_exists': os.path.exists(self.storage_path),
        }
        return base
