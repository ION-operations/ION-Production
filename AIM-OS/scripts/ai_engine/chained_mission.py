"""
AIM-OS AI Engine — ChainedMission

Dynamic prompt chaining for agent missions. When a task is too
complex for a single agent, ChainedMission:

    1. Estimates complexity (token budget, scope analysis)
    2. Director plans the chain (topology, specialist assignment)
    3. Chains agents sequentially — each phase gets previous outputs
    4. Director evaluates quality after each phase (proceed/rework/split)
    5. Intelligent context compression for forwarding
    6. Synthesizes all phase outputs into a unified report

The key insight: a 3-phase chain of focused 60s agents beats
a single 180s agent that times out on an overloaded prompt.

The ChainDirector manages the chain — it does not do the work.
It plans, evaluates, adapts, and synthesizes.

Design by Braden (CEO):
    "An AI that is able to manage the chain and dynamically adjust
     and aid in management and communication as needed."
"""

import os
import sys
import json
import time
import uuid
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger('ai_engine.chained_mission')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))


# ── Data Models ──────────────────────────────────────────

@dataclass
class Phase:
    """A single phase in a chained mission."""
    id: str
    name: str
    task: str
    role: str = 'researcher'
    depends_on: List[str] = field(default_factory=list)    # phase IDs
    timeout: int = 90
    status: str = 'pending'      # pending, running, done, failed, split
    output: str = ''
    latency_ms: float = 0.0
    context_tokens: int = 0
    error: str = ''
    retry_count: int = 0


@dataclass
class ChainResult:
    """Result of an entire chained mission."""
    mission_id: str
    task: str
    phases: List[Phase] = field(default_factory=list)
    synthesized_output: str = ''
    total_time_ms: float = 0.0
    phases_succeeded: int = 0
    phases_failed: int = 0
    phases_total: int = 0
    context_forwarded: int = 0  # how many times output was passed forward

    def to_dict(self) -> dict:
        return {
            'mission_id': self.mission_id,
            'task': self.task[:100],
            'total_time_ms': self.total_time_ms,
            'phases_succeeded': self.phases_succeeded,
            'phases_failed': self.phases_failed,
            'phases_total': self.phases_total,
            'context_forwarded': self.context_forwarded,
            'phases': [
                {
                    'id': p.id,
                    'name': p.name,
                    'role': p.role,
                    'status': p.status,
                    'latency_ms': p.latency_ms,
                    'output_len': len(p.output),
                }
                for p in self.phases
            ],
        }


# ── Complexity Estimator ─────────────────────────────────

class ComplexityEstimator:
    """
    Estimates whether a task needs chaining and how to split it.
    
    Signals that suggest chaining:
    - Long task descriptions (>200 words)
    - Multiple distinct objectives ("analyze X and Y and Z")
    - Broad scope keywords (audit, comprehensive, thorough)
    - Previous timeout on this task
    """

    # Keywords that suggest high complexity
    COMPLEXITY_SIGNALS = [
        'audit', 'comprehensive', 'thorough', 'complete', 'all',
        'every', 'entire', 'deep dive', 'full analysis', 'end-to-end',
        'map', 'inventory', 'catalog', 'assess', 'evaluate',
    ]

    # Keywords that suggest multiple objectives
    MULTI_OBJECTIVE_SIGNALS = [
        ' and ', ' also ', ' additionally ', ' furthermore ',
        ' plus ', ' as well as ', '\n1.', '\n2.', '\n-',
    ]

    @classmethod
    def estimate(cls, task: str, previous_timeout: bool = False) -> dict:
        """
        Estimate task complexity.
        
        Returns:
            dict with 'score' (0-1), 'should_chain' (bool),
            'reason' (str), 'suggested_phases' (int)
        """
        score = 0.0
        reasons = []

        # Word count
        word_count = len(task.split())
        if word_count > 200:
            score += 0.3
            reasons.append(f'Long task ({word_count} words)')
        elif word_count > 100:
            score += 0.15
            reasons.append(f'Medium task ({word_count} words)')

        # Complexity signals
        task_lower = task.lower()
        complexity_hits = sum(
            1 for s in cls.COMPLEXITY_SIGNALS if s in task_lower
        )
        if complexity_hits >= 3:
            score += 0.3
            reasons.append(f'{complexity_hits} complexity signals')
        elif complexity_hits >= 1:
            score += 0.15
            reasons.append(f'{complexity_hits} complexity signals')

        # Multi-objective signals
        multi_hits = sum(
            1 for s in cls.MULTI_OBJECTIVE_SIGNALS if s in task
        )
        if multi_hits >= 3:
            score += 0.3
            reasons.append(f'{multi_hits} multi-objective signals')
        elif multi_hits >= 1:
            score += 0.1

        # Previous timeout is a strong signal
        if previous_timeout:
            score += 0.4
            reasons.append('Previous timeout (guaranteed chain)')

        # Numbered list items suggest phases
        import re
        numbered_items = len(re.findall(r'\d+\.', task))
        if numbered_items >= 3:
            score += 0.2
            reasons.append(f'{numbered_items} numbered items')

        score = min(score, 1.0)
        should_chain = score >= 0.5

        # Estimate phases needed
        if score >= 0.8:
            suggested_phases = min(numbered_items + 1, 5) if numbered_items >= 2 else 4
        elif score >= 0.5:
            suggested_phases = min(numbered_items + 1, 4) if numbered_items >= 2 else 3
        else:
            suggested_phases = 1

        return {
            'score': round(score, 2),
            'should_chain': should_chain,
            'reason': '; '.join(reasons) if reasons else 'Low complexity',
            'suggested_phases': suggested_phases,
        }


# ── Phase Decomposer ─────────────────────────────────────

class PhaseDecomposer:
    """
    Decomposes a complex task into focused, sequential phases.
    
    Each phase:
    - Has a single, clear objective
    - Gets previous phases' outputs as context
    - Stays within timeout bounds
    """

    # Standard decomposition templates
    AUDIT_PHASES = [
        {
            'name': 'Survey',
            'role': 'researcher',
            'template': (
                'PHASE 1 — SURVEY: List and briefly describe all files and '
                'modules in the target area. Count lines of code per module. '
                'Identify key classes and functions. Do NOT analyze deeply — '
                'just map what exists.\n\nTarget: {target}'
            ),
        },
        {
            'name': 'Deep Analysis',
            'role': 'auditor',
            'template': (
                'PHASE 2 — DEEP ANALYSIS: Using the survey from Phase 1 below, '
                'conduct a thorough analysis of the code quality, architecture '
                'patterns, error handling, and edge cases.\n\n'
                '## Phase 1 Survey Results\n{prev_output}\n\n'
                'Target: {target}'
            ),
        },
        {
            'name': 'Recommendations',
            'role': 'architect',
            'template': (
                'PHASE 3 — RECOMMENDATIONS: Given the survey and analysis below, '
                'provide specific, actionable recommendations for improvement. '
                'Rate confidence 0-1 for each recommendation.\n\n'
                '## Phase 1 Survey\n{phase_1_output}\n\n'
                '## Phase 2 Analysis\n{prev_output}\n\n'
                'Target: {target}'
            ),
        },
    ]

    RESEARCH_PHASES = [
        {
            'name': 'Discovery',
            'role': 'researcher',
            'template': (
                'PHASE 1 — DISCOVERY: Explore and map the target area. '
                'List all relevant files, their sizes, and key contents. '
                'Identify the main patterns and structures.\n\nTarget: {target}'
            ),
        },
        {
            'name': 'Deep Dive',
            'role': 'researcher',
            'template': (
                'PHASE 2 — DEEP DIVE: Using the discovery from Phase 1, '
                'read and analyze the most important files identified. '
                'Document how the subsystems connect and interact.\n\n'
                '## Phase 1 Discovery\n{prev_output}\n\nTarget: {target}'
            ),
        },
        {
            'name': 'Synthesis',
            'role': 'architect',
            'template': (
                'PHASE 3 — SYNTHESIS: Synthesize all findings into a '
                'comprehensive technical report with architecture diagrams '
                'and confidence levels.\n\n'
                '## Phase 1 Discovery\n{phase_1_output}\n\n'
                '## Phase 2 Deep Dive\n{prev_output}\n\nTarget: {target}'
            ),
        },
    ]

    @classmethod
    def decompose(
        cls,
        task: str,
        num_phases: int = 3,
        task_type: str = 'auto',
    ) -> List[Phase]:
        """
        Decompose a task into sequential phases.
        
        Args:
            task: The full task description
            num_phases: Target number of phases
            task_type: 'audit', 'research', or 'auto' (detected)
        
        Returns:
            List of Phase objects
        """
        # Auto-detect task type
        if task_type == 'auto':
            task_lower = task.lower()
            if any(w in task_lower for w in ['audit', 'review', 'quality', 'security']):
                task_type = 'audit'
            else:
                task_type = 'research'

        # Select template
        templates = (
            cls.AUDIT_PHASES if task_type == 'audit'
            else cls.RESEARCH_PHASES
        )

        # Extract target from task (first sentence or line)
        target = task.split('\n')[0][:200]

        phases = []
        for i, tmpl in enumerate(templates[:num_phases]):
            phase_id = f'phase_{i+1}'
            phase_task = tmpl['template'].format(
                target=target,
                prev_output='{prev_output}',  # placeholder for runtime
                phase_1_output='{phase_1_output}',
            )

            phases.append(Phase(
                id=phase_id,
                name=tmpl['name'],
                task=phase_task,
                role=tmpl['role'],
                depends_on=[f'phase_{i}'] if i > 0 else [],
                timeout=90,
            ))

        return phases


# ── ChainedMission ────────────────────────────────────────

class ChainedMission:
    """
    Dynamic prompt chaining for complex agent missions.
    
    Now managed by ChainDirector — the manager AI that plans
    the chain, evaluates quality, and adapts in real-time.
    
    Usage:
        mission = ChainedMission()
        result = mission.execute(
            task='Audit scripts/ai_engine/ comprehensively',
        )
        print(result.synthesized_output)
    """

    def __init__(
        self,
        workspace_root: str = '',
        max_phases: int = 5,
        phase_timeout: int = 90,
        enable_atlas: bool = True,
        enable_context: bool = True,
        max_retries: int = 2,
        quality_threshold: float = 0.6,
        context_budget: int = 2000,
        enable_director: bool = True,
    ):
        self.workspace_root = workspace_root or WORKSPACE
        self.max_phases = max_phases
        self.phase_timeout = phase_timeout
        self.enable_atlas = enable_atlas
        self.enable_context = enable_context
        self.max_retries = max_retries
        self._mission_id = f'cm_{uuid.uuid4().hex[:8]}'

        # Director integration
        self.director = None
        self.topology_dispatcher = None
        if enable_director:
            try:
                from chain_director import ChainDirector, Topology
                self.director = ChainDirector(
                    workspace_root=self.workspace_root,
                    quality_threshold=quality_threshold,
                    context_budget=context_budget,
                )
                # Topology dispatcher routes to specialized executors
                try:
                    from chain_topologies import TopologyDispatcher
                    self.topology_dispatcher = TopologyDispatcher(
                        workspace_root=self.workspace_root,
                        director=self.director,
                        default_timeout=phase_timeout,
                    )
                    logger.info(f'[{self._mission_id}] TopologyDispatcher enabled')
                except Exception as e:
                    logger.debug(f'[{self._mission_id}] TopologyDispatcher unavailable: {e}')
                logger.info(f'[{self._mission_id}] ChainDirector enabled')
            except Exception as e:
                logger.warning(f'[{self._mission_id}] ChainDirector unavailable: {e}')

    def execute(
        self,
        task: str,
        task_type: str = 'auto',
        force_chain: bool = False,
        phases: Optional[List[Phase]] = None,
        active_file: str = '',
    ) -> ChainResult:
        """
        Execute a mission with dynamic prompt chaining.
        
        Pipeline:
            1. Estimate complexity
            2. Decompose into phases (or use provided)
            3. Execute phases sequentially, forwarding context
            4. Handle timeouts with retry/split
            5. Synthesize all outputs
        
        Args:
            task: The task description
            task_type: 'audit', 'research', or 'auto'
            force_chain: Always chain, skip complexity check
            phases: Pre-defined phases (skip decomposition)
            active_file: Active file for context
        
        Returns:
            ChainResult with all phase outputs and synthesis
        """
        start_time = time.monotonic()

        logger.info(f'[{self._mission_id}] Starting chained mission: {task[:80]}...')

        # Step 1: Estimate complexity
        estimate = ComplexityEstimator.estimate(task)
        logger.info(
            f'[{self._mission_id}] Complexity: {estimate["score"]} '
            f'(chain={estimate["should_chain"]}, phases={estimate["suggested_phases"]})'
        )

        # Step 2: Plan the chain (Director-managed or legacy decomposition)
        if phases:
            mission_phases = phases
            topology_name = 'custom'
        elif self.director and (force_chain or estimate['should_chain']):
            # Director plans: topology selection + specialist scoring
            plan = self.director.plan_chain(
                task=task,
                complexity=estimate['score'],
            )
            topology_name = plan.topology.value
            # Convert Director's PhaseAssignments to our Phase objects
            mission_phases = []
            for pa in plan.phases:
                mission_phases.append(Phase(
                    id=f'phase_{len(mission_phases)+1}',
                    name=pa.phase_name,
                    task=pa.task_template,
                    role=pa.role,
                    depends_on=[f'phase_{len(mission_phases)}'] if mission_phases else [],
                    timeout=pa.timeout or self.phase_timeout,
                ))
            logger.info(
                f'[{self._mission_id}] Director plan: {topology_name}, '
                f'{len(mission_phases)} phases, '
                f'specialists={plan.specialist_scores}'
            )
        elif force_chain or estimate['should_chain']:
            # Legacy fallback if Director unavailable
            mission_phases = PhaseDecomposer.decompose(
                task=task,
                num_phases=min(estimate['suggested_phases'], self.max_phases),
                task_type=task_type,
            )
            topology_name = 'sequential'
        else:
            # Simple task — single phase
            mission_phases = [Phase(
                id='phase_1',
                name='Direct',
                task=task,
                role='researcher',
                timeout=self.phase_timeout,
            )]
            topology_name = 'direct'

        result = ChainResult(
            mission_id=self._mission_id,
            task=task,
            phases=mission_phases,
            phases_total=len(mission_phases),
        )

        logger.info(
            f'[{self._mission_id}] Decomposed into {len(mission_phases)} phases '
            f'(topology: {topology_name})'
        )

        # ── Dispatch to topology executor if available ──
        # Gated, debate, and parallel topologies use specialized executors
        # that handle parallelism, quality gates, etc. natively.
        if (
            self.topology_dispatcher
            and self.director
            and topology_name in ('gated', 'debate', 'parallel')
            and not phases  # don't override custom phases
        ):
            try:
                from chain_director import Topology
                logger.info(
                    f'[{self._mission_id}] Dispatching to {topology_name} executor'
                )
                topo_result = self.topology_dispatcher.dispatch(
                    plan=plan,
                    task=task,
                    active_file=active_file,
                )

                # Convert TopologyResult → ChainResult
                result = ChainResult(
                    mission_id=self._mission_id,
                    task=task,
                    phases=[],
                    phases_total=len(topo_result.phases),
                    phases_succeeded=topo_result.phases_succeeded,
                    phases_failed=topo_result.phases_failed,
                    synthesized_output=topo_result.synthesized_output,
                    total_time_ms=topo_result.total_time_ms,
                )
                # Convert topology PhaseResults to our Phase objects
                for tr in topo_result.phases:
                    result.phases.append(Phase(
                        id=tr.phase_id,
                        name=tr.phase_name,
                        task='(executed by topology dispatcher)',
                        role=tr.role,
                        status='done' if tr.success else 'failed',
                        output=tr.output,
                        latency_ms=tr.latency_ms,
                        error=tr.error,
                        retry_count=tr.retry_count,
                    ))

                # Append Director's decision log
                if self.director and self.director.decision_history:
                    result.synthesized_output += '\n\n---\n\n'
                    result.synthesized_output += self.director.summary()

                result.total_time_ms = (time.monotonic() - start_time) * 1000
                logger.info(
                    f'[{self._mission_id}] Topology executor complete: '
                    f'{result.phases_succeeded}/{result.phases_total}, '
                    f'{result.total_time_ms:.0f}ms'
                )
                return result

            except Exception as e:
                logger.warning(
                    f'[{self._mission_id}] Topology executor failed, '
                    f'falling back to sequential: {e}'
                )

        # Step 3: Execute phases sequentially with Director management
        from enhanced_worker import EnhancedWorker

        phase_outputs: Dict[str, str] = {}
        context_forwards = 0

        for i, phase in enumerate(mission_phases):
            phase.status = 'running'
            logger.info(
                f'[{self._mission_id}] Phase {i+1}/{len(mission_phases)}: '
                f'{phase.name} ({phase.role})'
            )

            # Inject previous phase outputs into this phase's task
            phase_task = phase.task
            if i > 0 and phase_outputs:
                prev_key = f'phase_{i}'  # previous phase
                prev_output = phase_outputs.get(prev_key, '')
                if prev_output:
                    # Use Director's intelligent compression if available
                    if self.director:
                        forwarded = self.director.compress_for_next(prev_output)
                    else:
                        max_forward = 2000
                        forwarded = prev_output[:max_forward]
                        if len(prev_output) > max_forward:
                            forwarded += f'\n...(truncated, {len(prev_output)} total chars)'

                    phase_task = phase_task.replace('{prev_output}', forwarded)
                    context_forwards += 1

                # Also inject phase 1 output if referenced
                phase_1_output = phase_outputs.get('phase_1', '')
                if phase_1_output and '{phase_1_output}' in phase_task:
                    if self.director:
                        p1_forwarded = self.director.compress_for_next(
                            phase_1_output, budget=1500
                        )
                    else:
                        max_p1 = 1500
                        p1_forwarded = phase_1_output[:max_p1]
                        if len(phase_1_output) > max_p1:
                            p1_forwarded += f'\n...(truncated, {len(phase_1_output)} total chars)'
                    phase_task = phase_task.replace('{phase_1_output}', p1_forwarded)
                    context_forwards += 1

            # Also handle {phase_1} placeholder from Director templates
            if '{phase_1}' in phase_task:
                phase_1_output = phase_outputs.get('phase_1', '')
                if phase_1_output:
                    if self.director:
                        p1_forwarded = self.director.compress_for_next(
                            phase_1_output, budget=1500
                        )
                    else:
                        p1_forwarded = phase_1_output[:1500]
                    phase_task = phase_task.replace('{phase_1}', p1_forwarded)
                    context_forwards += 1

            # Clean any unreplaced placeholders
            phase_task = phase_task.replace('{prev_output}', '(no prior output)')
            phase_task = phase_task.replace('{phase_1_output}', '(no prior output)')
            phase_task = phase_task.replace('{phase_1}', '(no prior output)')

            # Execute phase with EnhancedWorker
            worker = EnhancedWorker(
                workspace_root=self.workspace_root,
                role=phase.role,
                timeout=phase.timeout,
                enable_atlas=self.enable_atlas,
                enable_context=self.enable_context,
                enable_memory=True,
                enable_scoring=False,
                enable_comms=False,
                enable_evolution=False,
            )

            phase_result = worker.execute(
                task=phase_task,
                active_file=active_file,
            )

            phase.latency_ms = phase_result.latency_ms
            phase.context_tokens = phase_result.context_tokens

            if phase_result.success:
                phase.status = 'done'
                phase.output = phase_result.content
                phase_outputs[phase.id] = phase_result.content
                result.phases_succeeded += 1

                # Director evaluates quality and decides
                if self.director:
                    quality = self.director.evaluate_output(
                        phase.output, task,
                        expected_depth='medium' if i < len(mission_phases) - 1 else 'deep',
                    )
                    action = self.director.decide(
                        quality, i, len(mission_phases),
                        retry_count=phase.retry_count,
                    )
                    logger.info(
                        f'[{self._mission_id}] Director: phase {i+1} quality={quality.overall:.2f} '
                        f'({quality.label}) → {action.value}'
                    )

                    # Handle Director's rework decision
                    from chain_director import Action
                    if action == Action.REWORK and phase.retry_count < self.max_retries:
                        logger.info(f'[{self._mission_id}] Director ordered REWORK for phase {i+1}')
                        phase.retry_count += 1
                        rework_task = (
                            f"REWORK — Your previous output scored {quality.overall:.2f}/1.0. "
                            f"The Director says: improve structure (headers/tables), "
                            f"add confidence levels, cover more task keywords, "
                            f"and include actionable recommendations.\n\n"
                            f"Original task:\n{phase_task[:1200]}"
                        )
                        rework_worker = EnhancedWorker(
                            workspace_root=self.workspace_root,
                            role=phase.role,
                            timeout=phase.timeout + 30,
                            enable_atlas=False,
                            enable_context=True,
                            enable_memory=False,
                            enable_scoring=False,
                            enable_comms=False,
                            enable_evolution=False,
                        )
                        rework_result = rework_worker.execute(
                            task=rework_task,
                            active_file=active_file,
                        )
                        if rework_result.success and len(rework_result.content) > len(phase.output):
                            phase.output = rework_result.content
                            phase_outputs[phase.id] = rework_result.content
                            phase.latency_ms += rework_result.latency_ms
                            logger.info(
                                f'[{self._mission_id}] Rework improved phase {i+1}: '
                                f'{len(phase.output)} chars'
                            )
                else:
                    logger.info(
                        f'[{self._mission_id}] Phase {i+1} complete: '
                        f'{len(phase.output)} chars, {phase.latency_ms:.0f}ms'
                    )
            else:
                # Handle timeout/failure — Director or legacy retry
                timed_out = 'timed out' in (phase_result.error or '').lower()

                if self.director:
                    from chain_director import Action
                    quality = self.director.evaluate_output('', task)
                    action = self.director.decide(
                        quality, i, len(mission_phases),
                        retry_count=phase.retry_count,
                        timed_out=timed_out,
                    )
                else:
                    action = None

                if phase.retry_count < self.max_retries:
                    phase.retry_count += 1
                    logger.warning(
                        f'[{self._mission_id}] Phase {i+1} failed, retrying '
                        f'({phase.retry_count}/{self.max_retries}): {phase_result.error}'
                    )

                    # Simplify the task for retry
                    simplified = (
                        f"SIMPLIFIED RETRY — be concise, max 500 words.\n\n"
                        f"{phase_task[:1000]}"
                    )

                    retry_worker = EnhancedWorker(
                        workspace_root=self.workspace_root,
                        role=phase.role,
                        timeout=phase.timeout + 60,  # extra time
                        enable_atlas=False,  # skip atlas for speed
                        enable_context=True,
                        enable_memory=False,
                        enable_scoring=False,
                        enable_comms=False,
                        enable_evolution=False,
                    )

                    retry_result = retry_worker.execute(
                        task=simplified,
                        active_file=active_file,
                    )

                    if retry_result.success:
                        phase.status = 'done'
                        phase.output = retry_result.content
                        phase_outputs[phase.id] = retry_result.content
                        phase.latency_ms += retry_result.latency_ms
                        result.phases_succeeded += 1
                        logger.info(
                            f'[{self._mission_id}] Phase {i+1} retry succeeded: '
                            f'{len(phase.output)} chars'
                        )
                    else:
                        phase.status = 'failed'
                        phase.error = retry_result.error
                        result.phases_failed += 1
                else:
                    phase.status = 'failed'
                    phase.error = phase_result.error
                    result.phases_failed += 1

        # Step 4: Synthesize all outputs
        result.context_forwarded = context_forwards
        successful_outputs = [
            p for p in mission_phases if p.status == 'done'
        ]

        if successful_outputs:
            synth_parts = []
            for p in successful_outputs:
                synth_parts.append(
                    f"## {p.name} ({p.role})\n{p.output}"
                )
            result.synthesized_output = '\n\n---\n\n'.join(synth_parts)

            # Append Director's decision log if available
            if self.director and self.director.decision_history:
                result.synthesized_output += '\n\n---\n\n'
                result.synthesized_output += self.director.summary()
        else:
            result.synthesized_output = 'All phases failed.'

        result.total_time_ms = (time.monotonic() - start_time) * 1000

        logger.info(
            f'[{self._mission_id}] Mission complete: '
            f'{result.phases_succeeded}/{result.phases_total} phases, '
            f'{result.total_time_ms:.0f}ms total, '
            f'{context_forwards} context forwards'
        )

        return result


# ── CLI Test ──────────────────────────────────────────────

def _test():
    """Test the chained mission system."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  ChainedMission — Dynamic Prompt Chaining Test         ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Test 1: Complexity estimation
    print("\n═══ TEST 1: Complexity Estimation ═══")

    simple = "List the files in scripts/ai_engine/"
    complex_task = (
        "Conduct a thorough audit of the AIM-OS AI Engine located in scripts/ai_engine/. "
        "Analyze the architecture, identify strengths and weaknesses, map subsystem relationships, "
        "and assess production readiness. Focus on:\n"
        "1. The 7-layer execution pipeline\n"
        "2. The swarm orchestration system\n"
        "3. The context engine and context pack builder\n"
        "4. The enhanced worker and Atlas integration\n"
        "Report findings with confidence levels."
    )

    for label, task in [('Simple', simple), ('Complex', complex_task)]:
        est = ComplexityEstimator.estimate(task)
        print(f"  {label}: score={est['score']}, chain={est['should_chain']}, "
              f"phases={est['suggested_phases']}, reason={est['reason']}")

    # Test with previous timeout
    est_timeout = ComplexityEstimator.estimate(complex_task, previous_timeout=True)
    print(f"  Complex+timeout: score={est_timeout['score']}, "
          f"chain={est_timeout['should_chain']}, phases={est_timeout['suggested_phases']}")

    # Test 2: Phase decomposition
    print("\n═══ TEST 2: Phase Decomposition ═══")
    phases = PhaseDecomposer.decompose(complex_task, num_phases=3, task_type='audit')
    for p in phases:
        print(f"  Phase {p.id}: {p.name} ({p.role})")
        print(f"    Task: {p.task[:100]}...")
        print(f"    Depends on: {p.depends_on}")

    # Test 3: Full chained mission
    print("\n═══ TEST 3: Full Chained Mission ═══")
    print("  Deploying 3-phase audit chain...")

    mission = ChainedMission(
        workspace_root=WORKSPACE,
        phase_timeout=90,
        enable_atlas=True,
        enable_context=True,
    )

    result = mission.execute(
        task=complex_task,
        task_type='audit',
        force_chain=True,
        active_file='scripts/ai_engine/engine.py',
    )

    print(f"\n  ── MISSION RESULTS ──")
    print(f"  Phases:    {result.phases_succeeded}/{result.phases_total} succeeded")
    print(f"  Time:      {result.total_time_ms:.0f}ms ({result.total_time_ms/1000:.1f}s)")
    print(f"  Forwarded: {result.context_forwarded} context passes")

    for p in result.phases:
        icon = '✅' if p.status == 'done' else '❌'
        print(f"  {icon} {p.name:20s} ({p.role:12s}) — {p.latency_ms:.0f}ms, "
              f"{len(p.output)} chars")

    if result.synthesized_output:
        print(f"\n  Synthesized output: {len(result.synthesized_output)} chars")
        for line in result.synthesized_output.split('\n')[:15]:
            print(f"    {line}")
        print("    ...")

    # Save report
    report_dir = os.path.join(WORKSPACE, '.agent', 'mission_reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, 'chained_audit_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Chained Mission Report\n\n")
        f.write(f"**Mission:** {result.mission_id}\n")
        f.write(f"**Phases:** {result.phases_succeeded}/{result.phases_total}\n")
        f.write(f"**Time:** {result.total_time_ms:.0f}ms\n")
        f.write(f"**Context Forwards:** {result.context_forwarded}\n\n---\n\n")
        f.write(result.synthesized_output)
    print(f"\n  📄 Report saved: {report_path}")

    return result


if __name__ == '__main__':
    _test()
