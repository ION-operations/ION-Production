"""
AIM-OS AI Engine — Chain Topology Executors

Implements the execution logic for each chain topology pattern.
The ChainDirector selects the topology; these executors run it.

Topologies:
    1. SequentialExecutor  — A → B → C (baseline)
    2. ParallelExecutor    — A → [B₁, B₂, B₃] → Merge
    3. GatedExecutor       — A → [quality gate] → B → [gate] → C
    4. DebateExecutor      — [Pro, Con] → Judge
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger('ai_engine.chain_topologies')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


# ══════════════════════════════════════════════════════════
#  SHARED TYPES
# ══════════════════════════════════════════════════════════

@dataclass
class PhaseResult:
    """Result of executing a single phase."""
    phase_id: str
    phase_name: str
    role: str
    output: str = ''
    success: bool = False
    latency_ms: float = 0.0
    quality_score: float = 0.0
    error: str = ''
    retry_count: int = 0


@dataclass
class TopologyResult:
    """Result of executing an entire topology."""
    topology: str
    phases: List[PhaseResult] = field(default_factory=list)
    synthesized_output: str = ''
    total_time_ms: float = 0.0
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    phases_succeeded: int = 0
    phases_failed: int = 0


# ══════════════════════════════════════════════════════════
#  PHASE RUNNER — wraps EnhancedWorker execution
# ══════════════════════════════════════════════════════════

class PhaseRunner:
    """
    Runs a single phase using EnhancedWorker.
    
    Shared by all topology executors. Handles:
    - Worker creation with appropriate settings
    - Timeout and error handling
    - Result packaging
    """

    def __init__(
        self,
        workspace_root: str = '',
        default_timeout: int = 90,
        enable_atlas: bool = True,
        enable_context: bool = True,
    ):
        self.workspace_root = workspace_root
        self.default_timeout = default_timeout
        self.enable_atlas = enable_atlas
        self.enable_context = enable_context

    def run(
        self,
        phase_id: str,
        phase_name: str,
        task: str,
        role: str = 'researcher',
        timeout: int = 0,
        active_file: str = '',
        lightweight: bool = False,
    ) -> PhaseResult:
        """
        Execute a single phase.
        
        Args:
            phase_id: Unique phase ID
            phase_name: Human-readable name
            task: The task prompt
            role: Agent role (researcher, auditor, architect)
            timeout: Seconds before timeout (0 = default)
            active_file: File context
            lightweight: Skip atlas/memory for speed
            
        Returns:
            PhaseResult with output or error
        """
        from enhanced_worker import EnhancedWorker

        start = time.monotonic()
        try:
            worker = EnhancedWorker(
                workspace_root=self.workspace_root,
                role=role,
                timeout=timeout or self.default_timeout,
                enable_atlas=self.enable_atlas and not lightweight,
                enable_context=self.enable_context,
                enable_memory=not lightweight,
                enable_scoring=False,
                enable_comms=False,
                enable_evolution=False,
            )
            result = worker.execute(task=task, active_file=active_file)
            elapsed = (time.monotonic() - start) * 1000

            if result.success:
                return PhaseResult(
                    phase_id=phase_id,
                    phase_name=phase_name,
                    role=role,
                    output=result.content,
                    success=True,
                    latency_ms=elapsed,
                )
            else:
                return PhaseResult(
                    phase_id=phase_id,
                    phase_name=phase_name,
                    role=role,
                    success=False,
                    latency_ms=elapsed,
                    error=result.error or 'Unknown error',
                )
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return PhaseResult(
                phase_id=phase_id,
                phase_name=phase_name,
                role=role,
                success=False,
                latency_ms=elapsed,
                error=str(e),
            )


# ══════════════════════════════════════════════════════════
#  PARALLEL EXECUTOR — Fan-out / Fan-in
# ══════════════════════════════════════════════════════════

class ParallelExecutor:
    """
    Parallel fan-out / fan-in topology.
    
    Pattern:
        Scout → [Analyst₁ ∥ Analyst₂ ∥ Analyst₃] → Synthesizer
    
    Use when:
        - Multi-domain tasks (security + performance + architecture)
        - Independent sub-tasks that don't depend on each other
        - Throughput is important
    
    The scout phase runs first to establish shared context,
    then parallel phases run concurrently, and finally
    a synthesis phase merges all results.
    """

    def __init__(
        self,
        runner: PhaseRunner,
        director=None,
        max_workers: int = 3,
    ):
        self.runner = runner
        self.director = director
        self.max_workers = max_workers

    def execute(
        self,
        task: str,
        scout_task: str,
        parallel_tasks: List[Dict[str, str]],
        synthesis_task: str,
        active_file: str = '',
    ) -> TopologyResult:
        """
        Execute parallel fan-out/fan-in.
        
        Args:
            task: Overall task description
            scout_task: Task for the initial scout phase
            parallel_tasks: List of {name, task, role} dicts for parallel phases
            synthesis_task: Task for final synthesis (receives {parallel_outputs})
            active_file: File context
            
        Returns:
            TopologyResult with all phase results
        """
        start = time.monotonic()
        result = TopologyResult(topology='parallel')

        # Phase 1: Scout (sequential)
        logger.info('[Parallel] Phase 1: Scout')
        scout = self.runner.run(
            phase_id='scout',
            phase_name='Scout',
            task=scout_task,
            role='researcher',
            active_file=active_file,
        )
        result.phases.append(scout)

        if not scout.success:
            result.phases_failed += 1
            result.total_time_ms = (time.monotonic() - start) * 1000
            return result
        result.phases_succeeded += 1

        # Compress scout output for parallel phases
        scout_context = scout.output
        if self.director:
            scout_context = self.director.compress_for_next(scout.output)

        # Phase 2: Parallel fan-out
        logger.info(f'[Parallel] Phase 2: Fan-out ({len(parallel_tasks)} parallel phases)')
        parallel_results: List[PhaseResult] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for i, pt in enumerate(parallel_tasks):
                phase_task = pt.get('task', '').replace('{scout_output}', scout_context)
                future = executor.submit(
                    self.runner.run,
                    phase_id=f'parallel_{i+1}',
                    phase_name=pt.get('name', f'Parallel-{i+1}'),
                    task=phase_task,
                    role=pt.get('role', 'auditor'),
                    active_file=active_file,
                )
                futures[future] = pt.get('name', f'Parallel-{i+1}')

            for future in as_completed(futures):
                name = futures[future]
                try:
                    phase_result = future.result()
                    parallel_results.append(phase_result)
                    result.phases.append(phase_result)
                    if phase_result.success:
                        result.phases_succeeded += 1
                        logger.info(
                            f'[Parallel] {name}: {len(phase_result.output)} chars, '
                            f'{phase_result.latency_ms:.0f}ms'
                        )
                    else:
                        result.phases_failed += 1
                        logger.warning(f'[Parallel] {name} failed: {phase_result.error}')
                except Exception as e:
                    result.phases_failed += 1
                    logger.error(f'[Parallel] {name} exception: {e}')

        # Phase 3: Synthesis (fan-in)
        logger.info('[Parallel] Phase 3: Synthesis (fan-in)')

        # Merge parallel outputs
        merged_parts = []
        for pr in parallel_results:
            if pr.success and pr.output:
                compressed = pr.output
                if self.director:
                    compressed = self.director.compress_for_next(pr.output, budget=1500)
                merged_parts.append(f"### {pr.phase_name}\n{compressed}")

        parallel_merged = '\n\n---\n\n'.join(merged_parts)
        final_task = synthesis_task.replace('{parallel_outputs}', parallel_merged)
        final_task = final_task.replace('{scout_output}', scout_context)

        synthesis = self.runner.run(
            phase_id='synthesis',
            phase_name='Synthesizer',
            task=final_task,
            role='architect',
            active_file=active_file,
        )
        result.phases.append(synthesis)

        if synthesis.success:
            result.phases_succeeded += 1
            result.synthesized_output = synthesis.output
        else:
            result.phases_failed += 1
            # Fallback: just concatenate parallel outputs
            result.synthesized_output = parallel_merged

        result.total_time_ms = (time.monotonic() - start) * 1000
        logger.info(
            f'[Parallel] Complete: {result.phases_succeeded}/{len(result.phases)} phases, '
            f'{result.total_time_ms:.0f}ms'
        )
        return result


# ══════════════════════════════════════════════════════════
#  GATED EXECUTOR — Quality-Gated Pipeline
# ══════════════════════════════════════════════════════════

class GatedExecutor:
    """
    Quality-gated sequential pipeline.
    
    Pattern:
        Phase 1 → [GATE: quality ≥ threshold?]
                    → Yes: Phase 2 → [GATE] → Phase 3
                    → No:  Rework Phase 1 (max retries)
    
    Use when:
        - Each phase's output MUST be high quality before proceeding
        - Audit/review tasks where errors propagate downstream
        - Tasks where rework is cheaper than redoing everything
    
    The Director evaluates quality at each gate. Failed gates trigger:
    1. Rework (first failure) — retry with quality feedback
    2. Rework focused (second failure) — simplified, focused prompt
    3. Accept & proceed (third failure) — accept imperfect and move on
    """

    def __init__(
        self,
        runner: PhaseRunner,
        director=None,
        quality_threshold: float = 0.6,
        max_retries: int = 2,
    ):
        self.runner = runner
        self.director = director
        self.quality_threshold = quality_threshold
        self.max_retries = max_retries

    def execute(
        self,
        task: str,
        phases: List[Dict[str, str]],
        active_file: str = '',
    ) -> TopologyResult:
        """
        Execute quality-gated pipeline.
        
        Args:
            task: Overall task description
            phases: List of {name, task, role} phase definitions
            active_file: File context
            
        Returns:
            TopologyResult with gating decisions logged
        """
        start = time.monotonic()
        result = TopologyResult(topology='gated')
        phase_outputs: Dict[str, str] = {}

        for i, phase_def in enumerate(phases):
            phase_name = phase_def.get('name', f'Phase-{i+1}')
            phase_task = phase_def.get('task', '')
            phase_role = phase_def.get('role', 'researcher')

            # Inject previous outputs
            if i > 0 and phase_outputs:
                prev_output = list(phase_outputs.values())[-1]
                if self.director:
                    prev_output = self.director.compress_for_next(prev_output)
                phase_task = phase_task.replace('{prev_output}', prev_output)

                # Inject first phase output if referenced
                first_output = list(phase_outputs.values())[0] if phase_outputs else ''
                if first_output and '{phase_1}' in phase_task:
                    if self.director:
                        first_output = self.director.compress_for_next(first_output, budget=1500)
                    phase_task = phase_task.replace('{phase_1}', first_output)

            # Clean unreplaced placeholders
            phase_task = phase_task.replace('{prev_output}', '(no prior output)')
            phase_task = phase_task.replace('{phase_1}', '(no prior output)')

            # Execute with quality gating
            phase_result = self._execute_with_gate(
                phase_id=f'gated_{i+1}',
                phase_name=phase_name,
                task=phase_task,
                original_task=task,
                role=phase_role,
                phase_index=i,
                total_phases=len(phases),
                active_file=active_file,
                result=result,
            )

            result.phases.append(phase_result)
            if phase_result.success:
                phase_outputs[f'gated_{i+1}'] = phase_result.output
                result.phases_succeeded += 1
            else:
                result.phases_failed += 1

        # Synthesize
        if phase_outputs:
            parts = []
            for pr in result.phases:
                if pr.success:
                    parts.append(f"## {pr.phase_name} ({pr.role})\n{pr.output}")
            result.synthesized_output = '\n\n---\n\n'.join(parts)
        else:
            result.synthesized_output = 'All gated phases failed.'

        result.total_time_ms = (time.monotonic() - start) * 1000
        logger.info(
            f'[Gated] Complete: {result.phases_succeeded}/{len(phases)} phases, '
            f'{len(result.decisions)} gate decisions, {result.total_time_ms:.0f}ms'
        )
        return result

    def _execute_with_gate(
        self,
        phase_id: str,
        phase_name: str,
        task: str,
        original_task: str,
        role: str,
        phase_index: int,
        total_phases: int,
        active_file: str,
        result: TopologyResult,
    ) -> PhaseResult:
        """Execute a phase and apply the quality gate."""

        retry_count = 0
        current_task = task

        while retry_count <= self.max_retries:
            # Run the phase
            phase_result = self.runner.run(
                phase_id=phase_id,
                phase_name=phase_name,
                task=current_task,
                role=role,
                active_file=active_file,
                lightweight=retry_count > 0,  # speed up retries
            )

            if not phase_result.success:
                retry_count += 1
                phase_result.retry_count = retry_count
                if retry_count <= self.max_retries:
                    logger.warning(
                        f'[Gated] {phase_name} failed, retrying '
                        f'({retry_count}/{self.max_retries})'
                    )
                    current_task = (
                        f"SIMPLIFIED RETRY — be concise.\n\n{task[:1000]}"
                    )
                    continue
                return phase_result

            # QUALITY GATE
            if self.director:
                quality = self.director.evaluate_output(
                    phase_result.output, original_task,
                    expected_depth='deep' if phase_index == total_phases - 1 else 'medium',
                )
                phase_result.quality_score = quality.overall

                from chain_director import Action
                action = self.director.decide(
                    quality, phase_index, total_phases,
                    retry_count=retry_count,
                )

                decision = {
                    'phase': phase_name,
                    'quality': quality.overall,
                    'label': quality.label,
                    'action': action.value,
                    'retry': retry_count,
                }
                result.decisions.append(decision)

                if action == Action.PROCEED:
                    logger.info(
                        f'[Gated] ✅ GATE PASSED: {phase_name} '
                        f'(quality={quality.overall:.2f})'
                    )
                    return phase_result

                elif action == Action.REWORK:
                    retry_count += 1
                    phase_result.retry_count = retry_count
                    if retry_count <= self.max_retries:
                        logger.info(
                            f'[Gated] 🔄 GATE FAILED: {phase_name} '
                            f'(quality={quality.overall:.2f}), reworking'
                        )
                        current_task = (
                            f"REWORK — Your output scored {quality.overall:.2f}/1.0. "
                            f"Improve: add headers/tables for structure, "
                            f"include confidence levels, cover key topics, "
                            f"add actionable recommendations.\n\n"
                            f"Original task:\n{task[:1200]}"
                        )
                        continue
                    else:
                        # Accept after max retries
                        logger.info(
                            f'[Gated] ⚠️ GATE: {phase_name} accepted after '
                            f'{retry_count} retries (quality={quality.overall:.2f})'
                        )
                        return phase_result

                elif action == Action.SKIP:
                    logger.info(
                        f'[Gated] ⏭️ GATE SKIP: {phase_name} '
                        f'(quality={quality.overall:.2f})'
                    )
                    phase_result.success = False
                    phase_result.error = 'Skipped by Director (very low quality)'
                    return phase_result
            else:
                # No director — pass through
                return phase_result

        return phase_result


# ══════════════════════════════════════════════════════════
#  DEBATE EXECUTOR — Adversarial Debate Pattern
# ══════════════════════════════════════════════════════════

class DebateExecutor:
    """
    Adversarial debate topology.
    
    Pattern:
        [Advocate ∥ Critic] → Judge
    
    Use when:
        - Evaluating trade-offs (REST vs GraphQL, monolith vs micro)
        - Architecture decisions where bias is dangerous
        - Review tasks where multiple perspectives improve outcomes
    
    The Advocate builds the strongest case FOR the current approach,
    the Critic builds the case AGAINST, and the Judge synthesizes
    a balanced verdict with specific actions.
    """

    def __init__(
        self,
        runner: PhaseRunner,
        director=None,
    ):
        self.runner = runner
        self.director = director

    def execute(
        self,
        task: str,
        advocate_task: str,
        critic_task: str,
        judge_task: str,
        active_file: str = '',
    ) -> TopologyResult:
        """
        Execute adversarial debate.
        
        Args:
            task: Overall question/topic being debated
            advocate_task: Prompt for the Advocate (pro)
            critic_task: Prompt for the Critic (con) — receives {advocate_output}
            judge_task: Prompt for the Judge — receives {advocate_output} and {critic_output}
            active_file: File context
            
        Returns:
            TopologyResult with debate phases and verdict
        """
        start = time.monotonic()
        result = TopologyResult(topology='debate')

        # Phase 1 & 2: Advocate and Critic run in parallel
        logger.info('[Debate] Running Advocate and Critic in parallel')

        with ThreadPoolExecutor(max_workers=2) as executor:
            adv_future = executor.submit(
                self.runner.run,
                phase_id='advocate',
                phase_name='Advocate',
                task=advocate_task,
                role='architect',
                active_file=active_file,
            )
            crit_future = executor.submit(
                self.runner.run,
                phase_id='critic',
                phase_name='Critic',
                task=critic_task,
                role='auditor',
                active_file=active_file,
            )

            advocate_result = adv_future.result()
            critic_result = crit_future.result()

        result.phases.append(advocate_result)
        result.phases.append(critic_result)

        if advocate_result.success:
            result.phases_succeeded += 1
        else:
            result.phases_failed += 1
        if critic_result.success:
            result.phases_succeeded += 1
        else:
            result.phases_failed += 1

        # Compress arguments for the Judge
        adv_output = advocate_result.output if advocate_result.success else '(Advocate failed to respond)'
        crit_output = critic_result.output if critic_result.success else '(Critic failed to respond)'

        if self.director:
            adv_output = self.director.compress_for_next(adv_output, budget=2000)
            crit_output = self.director.compress_for_next(crit_output, budget=2000)

        # Phase 3: Judge synthesizes
        logger.info('[Debate] Phase 3: Judge rendering verdict')
        final_task = judge_task.replace('{advocate_output}', adv_output)
        final_task = final_task.replace('{critic_output}', crit_output)

        judge_result = self.runner.run(
            phase_id='judge',
            phase_name='Judge',
            task=final_task,
            role='architect',
            active_file=active_file,
        )
        result.phases.append(judge_result)

        if judge_result.success:
            result.phases_succeeded += 1
            result.synthesized_output = judge_result.output
        else:
            result.phases_failed += 1
            # Fallback: concatenate both sides
            result.synthesized_output = (
                f"## Advocate's Case\n{advocate_result.output}\n\n"
                f"---\n\n## Critic's Case\n{critic_result.output}\n\n"
                f"---\n\n*Judge failed to render verdict.*"
            )

        result.total_time_ms = (time.monotonic() - start) * 1000
        logger.info(
            f'[Debate] Complete: {result.phases_succeeded}/{len(result.phases)} phases, '
            f'{result.total_time_ms:.0f}ms'
        )
        return result


# ══════════════════════════════════════════════════════════
#  TOPOLOGY DISPATCHER
# ══════════════════════════════════════════════════════════

class TopologyDispatcher:
    """
    Routes a task to the appropriate topology executor based on
    the ChainDirector's plan.
    
    Usage:
        from chain_director import ChainDirector
        from chain_topologies import TopologyDispatcher
        
        director = ChainDirector()
        plan = director.plan_chain("Compare REST vs GraphQL")
        
        dispatcher = TopologyDispatcher(director=director)
        result = dispatcher.dispatch(plan, task="Compare REST vs GraphQL")
    """

    def __init__(
        self,
        workspace_root: str = '',
        director=None,
        default_timeout: int = 90,
        max_parallel: int = 3,
    ):
        self.workspace_root = workspace_root or os.path.normpath(
            os.path.join(SCRIPT_DIR, '..', '..')
        )
        self.director = director
        self.runner = PhaseRunner(
            workspace_root=self.workspace_root,
            default_timeout=default_timeout,
        )
        self.max_parallel = max_parallel

    def dispatch(
        self,
        plan,
        task: str,
        active_file: str = '',
    ) -> TopologyResult:
        """
        Dispatch a ChainPlan to the right topology executor.
        
        Args:
            plan: ChainPlan from ChainDirector.plan_chain()
            task: Full task description
            active_file: File context
            
        Returns:
            TopologyResult
        """
        from chain_director import Topology

        topology = plan.topology
        target = task.split('\n')[0][:200]

        if topology == Topology.PARALLEL:
            return self._run_parallel(plan, task, target, active_file)
        elif topology == Topology.DEBATE:
            return self._run_debate(plan, task, target, active_file)
        elif topology == Topology.GATED:
            return self._run_gated(plan, task, target, active_file)
        else:
            # Sequential default — run phases in order
            return self._run_sequential(plan, task, target, active_file)

    def _run_parallel(self, plan, task, target, active_file) -> TopologyResult:
        """Run parallel fan-out/fan-in."""
        executor = ParallelExecutor(
            runner=self.runner,
            director=self.director,
            max_workers=self.max_parallel,
        )

        # Build parallel sub-tasks from plan phases
        # First phase = scout, last = synthesis, middle = parallel
        phases = plan.phases
        if len(phases) < 3:
            # Not enough phases for parallel — fall back to sequential
            return self._run_sequential(plan, task, target, active_file)

        scout_task = phases[0].task_template.replace('{prev_output}', '')
        scout_task = scout_task.replace('{phase_1}', '')

        parallel_tasks = []
        for p in phases[1:-1]:
            parallel_tasks.append({
                'name': p.phase_name,
                'task': p.task_template.replace('{prev_output}', '{scout_output}'),
                'role': p.role,
            })

        synthesis_task = phases[-1].task_template

        return executor.execute(
            task=task,
            scout_task=scout_task,
            parallel_tasks=parallel_tasks,
            synthesis_task=synthesis_task,
            active_file=active_file,
        )

    def _run_debate(self, plan, task, target, active_file) -> TopologyResult:
        """Run adversarial debate."""
        executor = DebateExecutor(
            runner=self.runner,
            director=self.director,
        )

        phases = plan.phases
        if len(phases) < 3:
            return self._run_sequential(plan, task, target, active_file)

        # Phase 0 = Advocate, Phase 1 = Critic, Phase 2 = Judge
        advocate_task = phases[0].task_template.replace('{prev_output}', '')
        advocate_task = advocate_task.replace('{phase_1}', '')

        critic_task = phases[1].task_template.replace(
            '{prev_output}', '{advocate_output}'
        )

        judge_task = phases[2].task_template.replace(
            '{phase_1}', '{advocate_output}'
        ).replace('{prev_output}', '{critic_output}')

        return executor.execute(
            task=task,
            advocate_task=advocate_task,
            critic_task=critic_task,
            judge_task=judge_task,
            active_file=active_file,
        )

    def _run_gated(self, plan, task, target, active_file) -> TopologyResult:
        """Run quality-gated pipeline."""
        executor = GatedExecutor(
            runner=self.runner,
            director=self.director,
        )

        phase_defs = []
        for p in plan.phases:
            phase_defs.append({
                'name': p.phase_name,
                'task': p.task_template,
                'role': p.role,
            })

        return executor.execute(
            task=task,
            phases=phase_defs,
            active_file=active_file,
        )

    def _run_sequential(self, plan, task, target, active_file) -> TopologyResult:
        """Run simple sequential execution."""
        start = time.monotonic()
        result = TopologyResult(topology='sequential')
        phase_outputs: Dict[str, str] = {}

        for i, phase_def in enumerate(plan.phases):
            phase_task = phase_def.task_template

            # Inject previous outputs
            if i > 0 and phase_outputs:
                prev_output = list(phase_outputs.values())[-1]
                if self.director:
                    prev_output = self.director.compress_for_next(prev_output)
                phase_task = phase_task.replace('{prev_output}', prev_output)

                first_output = list(phase_outputs.values())[0]
                if '{phase_1}' in phase_task:
                    if self.director:
                        first_output = self.director.compress_for_next(
                            first_output, budget=1500
                        )
                    phase_task = phase_task.replace('{phase_1}', first_output)

            phase_task = phase_task.replace('{prev_output}', '(no prior output)')
            phase_task = phase_task.replace('{phase_1}', '(no prior output)')

            phase_result = self.runner.run(
                phase_id=f'seq_{i+1}',
                phase_name=phase_def.phase_name,
                task=phase_task,
                role=phase_def.role,
                active_file=active_file,
            )
            result.phases.append(phase_result)

            if phase_result.success:
                phase_outputs[f'seq_{i+1}'] = phase_result.output
                result.phases_succeeded += 1
            else:
                result.phases_failed += 1

        # Synthesize
        if phase_outputs:
            parts = [
                f"## {pr.phase_name} ({pr.role})\n{pr.output}"
                for pr in result.phases if pr.success
            ]
            result.synthesized_output = '\n\n---\n\n'.join(parts)
        else:
            result.synthesized_output = 'All phases failed.'

        result.total_time_ms = (time.monotonic() - start) * 1000
        return result


# ══════════════════════════════════════════════════════════
#  SELF-TEST
# ══════════════════════════════════════════════════════════

def _test():
    """Test topology executors (structural, no LLM)."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Chain Topologies — Test Suite                          ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Test 1: PhaseRunner creation
    print("\n═══ TEST 1: PhaseRunner ═══")
    runner = PhaseRunner(workspace_root=os.getcwd())
    print(f"  ✅ PhaseRunner created (workspace={runner.workspace_root[:40]}...)")

    # Test 2: ParallelExecutor instantiation
    print("\n═══ TEST 2: ParallelExecutor ═══")
    pe = ParallelExecutor(runner=runner, max_workers=3)
    assert pe.max_workers == 3
    print("  ✅ ParallelExecutor created (max_workers=3)")

    # Test 3: GatedExecutor instantiation
    print("\n═══ TEST 3: GatedExecutor ═══")
    ge = GatedExecutor(runner=runner, quality_threshold=0.6, max_retries=2)
    assert ge.quality_threshold == 0.6
    assert ge.max_retries == 2
    print("  ✅ GatedExecutor created (threshold=0.6, retries=2)")

    # Test 4: DebateExecutor instantiation
    print("\n═══ TEST 4: DebateExecutor ═══")
    de = DebateExecutor(runner=runner)
    print("  ✅ DebateExecutor created")

    # Test 5: TopologyDispatcher
    print("\n═══ TEST 5: TopologyDispatcher ═══")
    dispatcher = TopologyDispatcher(workspace_root=os.getcwd())
    assert dispatcher.runner is not None
    print("  ✅ TopologyDispatcher created")

    # Test 6: Dispatcher integration with ChainDirector
    print("\n═══ TEST 6: Director → Dispatcher Integration ═══")
    try:
        from chain_director import ChainDirector, Topology
        director = ChainDirector()

        # Test each topology type
        test_cases = [
            ("Audit the security of the API", Topology.GATED),
            ("Research how context engine works", Topology.SEQUENTIAL),
            ("Compare HHNI vs ContextPack", Topology.DEBATE),
        ]

        for task, expected_topo in test_cases:
            plan = director.plan_chain(task)
            assert plan.topology == expected_topo, \
                f"Expected {expected_topo.value}, got {plan.topology.value}"
            print(f"  ✅ '{task[:40]}' → {plan.topology.value} ({len(plan.phases)} phases)")

        # Verify dispatcher would route correctly
        dispatcher_with_dir = TopologyDispatcher(director=director)
        print("  ✅ TopologyDispatcher with Director ready")

    except ImportError as e:
        print(f"  ⚠️ ChainDirector not available: {e}")

    print("\n✅ All topology tests passed!")


if __name__ == '__main__':
    _test()
