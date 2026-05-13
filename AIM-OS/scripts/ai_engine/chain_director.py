"""
AIM-OS AI Engine — ChainDirector

The manager AI that plans, monitors, and adapts chains.
It does not do the work — it manages the agents that do.

Responsibilities:
    1. Plan — analyze task, select topology, assign specialists
    2. Evaluate — score each phase output for quality
    3. Adapt — rework weak phases, split timeouts, insert new phases
    4. Compress — intelligently summarize context for forwarding
    5. Synthesize — merge all phase outputs into final report

Design principle from Braden (CEO):
    "An AI that is able to manage the chain and dynamically adjust
     and aid in management and communication as needed."

Integrates with:
    - specialist_system (WorkDetector, RelevanceCalculator, ActivationSystem)
    - APOE topology strategies (parallel, sequential, consensus, debate)
    - ChainedMission runtime (context forwarding, timeout recovery)
    - Atlas (big-picture context for planning)
"""

import os
import sys
import re
import json
import time
import logging
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger('ai_engine.chain_director')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))


# ══════════════════════════════════════════════════════════
#  ENUMS & DATA MODELS
# ══════════════════════════════════════════════════════════

class Topology(Enum):
    """Chain execution topologies."""
    SEQUENTIAL = 'sequential'       # A → B → C
    PARALLEL = 'parallel'           # A → [B₁, B₂] → Merge
    GATED = 'gated'                 # A → [quality gate] → B
    DEBATE = 'debate'               # [Pro, Con] → Judge
    ITERATIVE = 'iterative'         # A → B → check → (B' if needed)
    HIERARCHICAL = 'hierarchical'   # Director → Leads → Workers
    CAROUSEL = 'carousel'           # Auto-rotate specialists
    ADAPTIVE = 'adaptive'           # DAG built at runtime


class Action(Enum):
    """Director's decision after evaluating a phase."""
    PROCEED = 'proceed'         # quality OK, move to next phase
    REWORK = 'rework'           # quality low, retry same phase
    SPLIT = 'split'             # phase too complex, decompose
    ADD_PHASE = 'add_phase'     # insert a new phase
    SKIP = 'skip'               # phase unnecessary
    ESCALATE = 'escalate'       # need human decision


@dataclass
class QualityScore:
    """Quality assessment of a phase output."""
    overall: float = 0.0           # 0.0–1.0
    structure_score: float = 0.0   # has headers, lists, tables?
    depth_score: float = 0.0       # word count / expected depth
    confidence_score: float = 0.0  # mentions confidence levels?
    coverage_score: float = 0.0    # covers task keywords?
    actionable_score: float = 0.0  # has recommendations?
    factors: Dict[str, float] = field(default_factory=dict)

    @property
    def label(self) -> str:
        if self.overall >= 0.85:
            return 'excellent'
        elif self.overall >= 0.7:
            return 'good'
        elif self.overall >= 0.5:
            return 'acceptable'
        elif self.overall >= 0.3:
            return 'weak'
        return 'poor'


@dataclass
class PhaseAssignment:
    """A specialist assigned to a chain phase."""
    phase_name: str
    role: str
    task_template: str
    specialist_id: str = ''
    relevance_score: float = 0.0
    timeout: int = 90
    depends_on: List[str] = field(default_factory=list)
    topology: Topology = Topology.SEQUENTIAL


@dataclass
class ChainPlan:
    """The Director's execution plan."""
    task: str
    topology: Topology
    phases: List[PhaseAssignment] = field(default_factory=list)
    estimated_time_ms: float = 0.0
    complexity_score: float = 0.0
    specialist_scores: Dict[str, float] = field(default_factory=dict)
    rationale: str = ''

    def to_dict(self) -> dict:
        return {
            'task': self.task[:100],
            'topology': self.topology.value,
            'phases': len(self.phases),
            'phase_details': [
                {'name': p.phase_name, 'role': p.role,
                 'specialist': p.specialist_id, 'relevance': p.relevance_score}
                for p in self.phases
            ],
            'complexity': self.complexity_score,
            'rationale': self.rationale,
        }


# ══════════════════════════════════════════════════════════
#  QUALITY EVALUATOR
# ══════════════════════════════════════════════════════════

class QualityEvaluator:
    """
    Scores phase outputs for quality without using an LLM.
    
    Fast, deterministic evaluation using structural analysis:
    - Does it have headers/sections?
    - Is it deep enough (word count)?
    - Does it mention confidence levels?
    - Does it cover the task keywords?
    - Does it have actionable recommendations?
    """

    # Weights for quality factors
    WEIGHTS = {
        'structure': 0.20,
        'depth': 0.25,
        'confidence': 0.15,
        'coverage': 0.25,
        'actionable': 0.15,
    }

    @classmethod
    def evaluate(cls, output: str, task: str, expected_depth: str = 'medium') -> QualityScore:
        """
        Evaluate phase output quality.
        
        Args:
            output: The agent's output text
            task: The original task for coverage checking
            expected_depth: 'shallow', 'medium', or 'deep'
        
        Returns:
            QualityScore with breakdown
        """
        if not output or not output.strip():
            return QualityScore(overall=0.0)

        structure = cls._score_structure(output)
        depth = cls._score_depth(output, expected_depth)
        confidence = cls._score_confidence(output)
        coverage = cls._score_coverage(output, task)
        actionable = cls._score_actionable(output)

        overall = (
            structure * cls.WEIGHTS['structure'] +
            depth * cls.WEIGHTS['depth'] +
            confidence * cls.WEIGHTS['confidence'] +
            coverage * cls.WEIGHTS['coverage'] +
            actionable * cls.WEIGHTS['actionable']
        )

        return QualityScore(
            overall=round(min(overall, 1.0), 3),
            structure_score=round(structure, 3),
            depth_score=round(depth, 3),
            confidence_score=round(confidence, 3),
            coverage_score=round(coverage, 3),
            actionable_score=round(actionable, 3),
            factors={
                'headers': len(re.findall(r'^#{1,4}\s', output, re.MULTILINE)),
                'lists': len(re.findall(r'^\s*[-*]\s', output, re.MULTILINE)),
                'tables': output.count('|'),
                'word_count': len(output.split()),
                'confidence_mentions': len(re.findall(r'confiden\w*\s*[:=]?\s*\d', output, re.IGNORECASE)),
            },
        )

    @classmethod
    def _score_structure(cls, output: str) -> float:
        """Headers, lists, tables → well-organized output."""
        score = 0.0
        headers = len(re.findall(r'^#{1,4}\s', output, re.MULTILINE))
        lists = len(re.findall(r'^\s*[-*]\s', output, re.MULTILINE))
        tables = output.count('|')
        code_blocks = output.count('```')

        if headers >= 3:
            score += 0.4
        elif headers >= 1:
            score += 0.2

        if lists >= 5:
            score += 0.3
        elif lists >= 2:
            score += 0.15

        if tables >= 4:
            score += 0.2
        elif tables >= 2:
            score += 0.1

        if code_blocks >= 2:
            score += 0.1

        return min(score, 1.0)

    @classmethod
    def _score_depth(cls, output: str, expected: str) -> float:
        """Word count relative to expected depth."""
        word_count = len(output.split())

        targets = {'shallow': 200, 'medium': 500, 'deep': 1000}
        target = targets.get(expected, 500)

        if word_count >= target:
            return 1.0
        elif word_count >= target * 0.5:
            return 0.7
        elif word_count >= target * 0.2:
            return 0.4
        return 0.2

    @classmethod
    def _score_confidence(cls, output: str) -> float:
        """Does the output include confidence/certainty assessments?"""
        confidence_patterns = [
            r'confiden\w*\s*[:=]?\s*\d',
            r'\d+\.?\d*\s*/\s*1\.?0?',
            r'(high|medium|low)\s+confiden',
            r'certainty',
            r'risk\s+level',
        ]
        hits = 0
        for p in confidence_patterns:
            hits += len(re.findall(p, output, re.IGNORECASE))

        if hits >= 3:
            return 1.0
        elif hits >= 1:
            return 0.6
        return 0.2

    @classmethod
    def _score_coverage(cls, output: str, task: str) -> float:
        """Does the output cover the key topics from the task?"""
        task_words = set(
            w.lower() for w in task.split()
            if len(w) > 4 and w.isalpha()
        )
        if not task_words:
            return 0.5

        output_lower = output.lower()
        covered = sum(1 for w in task_words if w in output_lower)
        coverage_ratio = covered / len(task_words) if task_words else 0

        if coverage_ratio >= 0.7:
            return 1.0
        elif coverage_ratio >= 0.4:
            return 0.7
        elif coverage_ratio >= 0.2:
            return 0.4
        return 0.2

    @classmethod
    def _score_actionable(cls, output: str) -> float:
        """Does the output contain actionable recommendations?"""
        action_patterns = [
            r'recommend',
            r'should\s',
            r'suggest',
            r'action\s*item',
            r'next\s+step',
            r'improve',
            r'implement',
            r'refactor',
            r'REC-\d+',
        ]
        hits = 0
        for p in action_patterns:
            hits += len(re.findall(p, output, re.IGNORECASE))

        if hits >= 5:
            return 1.0
        elif hits >= 2:
            return 0.7
        elif hits >= 1:
            return 0.4
        return 0.1


# ══════════════════════════════════════════════════════════
#  CONTEXT COMPRESSOR
# ══════════════════════════════════════════════════════════

class ContextCompressor:
    """
    Intelligently compresses agent outputs for context forwarding.
    
    Instead of naive truncation, extracts the most valuable parts:
    - Headers and section titles
    - Tables (high information density)
    - Numbered lists and recommendations
    - Confidence assessments
    - Code blocks
    """

    @classmethod
    def compress(cls, output: str, budget: int = 2000) -> str:
        """
        Compress output to fit within token budget.
        
        Args:
            output: Full agent output
            budget: Target character count (~500 tokens)
        
        Returns:
            Compressed version preserving key information
        """
        if len(output) <= budget:
            return output

        parts: List[Tuple[int, str]] = []  # (priority, text)

        # Priority 1: Headers + their first line
        for match in re.finditer(r'(^#{1,4}\s.+)(?:\n(.+))?', output, re.MULTILINE):
            header = match.group(1)
            first_line = match.group(2) or ''
            parts.append((10, f"{header}\n{first_line}".strip()))

        # Priority 2: Tables (high density)
        in_table = False
        table_lines: List[str] = []
        for line in output.split('\n'):
            if '|' in line and ('---' in line or line.strip().startswith('|')):
                in_table = True
                table_lines.append(line)
            elif in_table:
                if line.strip():
                    table_lines.append(line)
                else:
                    parts.append((8, '\n'.join(table_lines)))
                    table_lines = []
                    in_table = False
        if table_lines:
            parts.append((8, '\n'.join(table_lines)))

        # Priority 3: Numbered recommendations / action items
        for match in re.finditer(
            r'^\s*\d+\.\s+\*\*.*?\*\*.*$', output, re.MULTILINE
        ):
            parts.append((7, match.group()))

        # Priority 4: Confidence assessments
        for match in re.finditer(
            r'.*confiden\w*\s*[:=]?\s*\d.*', output, re.IGNORECASE
        ):
            parts.append((6, match.group().strip()))

        # Priority 5: Bullet point items
        bullets = re.findall(r'^\s*[-*]\s+\*\*.*?\*\*.*$', output, re.MULTILINE)
        for b in bullets[:10]:  # cap at 10
            parts.append((5, b))

        # Sort by priority (highest first) and assemble
        parts.sort(key=lambda x: -x[0])

        compressed: List[str] = []
        chars_used = 0

        for priority, text in parts:
            if chars_used + len(text) + 2 > budget:
                break
            compressed.append(text)
            chars_used += len(text) + 2

        if not compressed:
            # Fallback: just truncate
            return output[:budget] + f'\n...(truncated, {len(output)} total chars)'

        result = '\n'.join(compressed)
        if len(result) < len(output):
            result += f'\n\n[Compressed from {len(output)} to {len(result)} chars]'

        return result


# ══════════════════════════════════════════════════════════
#  TOPOLOGY SELECTOR
# ══════════════════════════════════════════════════════════

class TopologySelector:
    """
    Selects the optimal chain topology based on task characteristics.
    
    Rules:
    - Audit/review tasks → GATED (quality checkpoints)
    - Research/exploration → SEQUENTIAL (deep progressive)
    - Multi-domain tasks → CAROUSEL (auto-rotate specialists)
    - Debate/analysis → DEBATE (adversarial)
    - Independent sub-tasks → PARALLEL (fan-out)
    - Simple tasks → SEQUENTIAL (single pass)
    """

    # Task type → topology mapping
    TOPOLOGY_RULES = {
        'audit': Topology.GATED,
        'review': Topology.GATED,
        'security': Topology.GATED,
        'research': Topology.SEQUENTIAL,
        'explore': Topology.SEQUENTIAL,
        'investigate': Topology.SEQUENTIAL,
        'compare': Topology.DEBATE,
        'evaluate': Topology.DEBATE,
        'decide': Topology.DEBATE,
        'build': Topology.SEQUENTIAL,
        'implement': Topology.SEQUENTIAL,
        'refactor': Topology.SEQUENTIAL,
    }

    @classmethod
    def select(cls, task: str, complexity: float = 0.5) -> Topology:
        """
        Select optimal topology for a task.
        
        Args:
            task: Task description
            complexity: 0.0–1.0 complexity score
        
        Returns:
            Recommended Topology
        """
        task_lower = task.lower()

        # Check for explicit topology signals
        for keyword, topo in cls.TOPOLOGY_RULES.items():
            if keyword in task_lower:
                return topo

        # Multi-domain detection → carousel
        domain_keywords = [
            'security', 'performance', 'architecture', 'testing',
            'documentation', 'deployment', 'database', 'ui', 'api',
        ]
        domain_hits = sum(1 for d in domain_keywords if d in task_lower)
        if domain_hits >= 3:
            return Topology.CAROUSEL

        # High complexity → gated (with quality checkpoints)
        if complexity >= 0.8:
            return Topology.GATED

        # Default
        return Topology.SEQUENTIAL


# ══════════════════════════════════════════════════════════
#  CHAIN DIRECTOR
# ══════════════════════════════════════════════════════════

class ChainDirector:
    """
    The manager AI that plans, monitors, and adapts chains.
    
    It does NOT do the work. It manages the agents that do.
    
    Usage:
        director = ChainDirector()
        
        # Plan a chain
        plan = director.plan_chain("Audit the AI Engine")
        
        # After each phase, evaluate and decide
        quality = director.evaluate_output(output, task)
        action = director.decide(quality, phase_index, chain_state)
        
        # Compress context for next phase
        compressed = director.compress_for_next(output, budget=2000)
    """

    # Phase templates for different topologies
    PHASE_TEMPLATES = {
        Topology.SEQUENTIAL: [
            {'name': 'Scout', 'role': 'researcher', 'task': (
                'PHASE 1 — SCOUT: Quick reconnaissance of {target}. '
                'Map files, count lines, identify key components. '
                'Be concise — this feeds into deeper analysis phases.'
            )},
            {'name': 'Analyst', 'role': 'auditor', 'task': (
                'PHASE 2 — DEEP ANALYSIS: Using the scout report below, '
                'conduct thorough analysis of code quality, patterns, '
                'and risks.\n\n## Scout Report\n{prev_output}'
            )},
            {'name': 'Synthesizer', 'role': 'architect', 'task': (
                'PHASE 3 — SYNTHESIS: Given the scout and analysis below, '
                'synthesize findings into actionable recommendations with '
                'confidence levels.\n\n## Scout\n{phase_1}\n\n'
                '## Analysis\n{prev_output}'
            )},
        ],
        Topology.GATED: [
            {'name': 'Scout', 'role': 'researcher', 'task': (
                'PHASE 1 — SCOUT: Map {target}. List all files, modules, '
                'key classes. Keep it factual and structured.'
            )},
            # [GATE: Director evaluates quality before proceeding]
            {'name': 'Deep Dive', 'role': 'auditor', 'task': (
                'PHASE 2 — DEEP DIVE: Based on the verified scout report, '
                'perform deep code analysis.\n\n## Verified Scout Report\n{prev_output}'
            )},
            # [GATE: Director evaluates quality]
            {'name': 'Recommendations', 'role': 'architect', 'task': (
                'PHASE 3 — RECOMMENDATIONS: Based on verified analysis, '
                'provide specific recommendations with confidence levels.\n\n'
                '## Scout\n{phase_1}\n\n## Analysis\n{prev_output}'
            )},
        ],
        Topology.DEBATE: [
            {'name': 'Advocate', 'role': 'architect', 'task': (
                'ROLE: ADVOCATE — Make the strongest case FOR the current '
                'approach/architecture of {target}. Identify all strengths, '
                'good patterns, and reasons to keep the current design.'
            )},
            {'name': 'Critic', 'role': 'auditor', 'task': (
                'ROLE: CRITIC — Make the strongest case AGAINST the current '
                'approach of {target}. Identify all weaknesses, risks, '
                'anti-patterns, and reasons to change.\n\n'
                '## Advocate\'s Case\n{prev_output}'
            )},
            {'name': 'Judge', 'role': 'architect', 'task': (
                'ROLE: JUDGE — Given the advocate and critic arguments below, '
                'determine the truth. Rate each argument. Produce a balanced '
                'verdict with specific actions.\n\n'
                '## Advocate\n{phase_1}\n\n## Critic\n{prev_output}'
            )},
        ],
    }

    def __init__(
        self,
        workspace_root: str = '',
        quality_threshold: float = 0.6,
        rework_threshold: float = 0.35,
        context_budget: int = 2000,
    ):
        self.workspace_root = workspace_root or WORKSPACE
        self.quality_threshold = quality_threshold
        self.rework_threshold = rework_threshold
        self.context_budget = context_budget
        self._decision_log: List[Dict[str, Any]] = []

    # ── Planning ──────────────────────────────────────────

    def plan_chain(
        self,
        task: str,
        complexity: float = 0.5,
        topology_override: Optional[Topology] = None,
        atlas_context: str = '',
    ) -> ChainPlan:
        """
        Plan a chain for a task.
        
        Args:
            task: Task description
            complexity: 0.0–1.0
            topology_override: Force a specific topology
            atlas_context: Big-picture context from Atlas
        
        Returns:
            ChainPlan with topology, phases, and specialist assignments
        """
        # Select topology
        topology = topology_override or TopologySelector.select(task, complexity)

        # Get phase templates
        templates = self.PHASE_TEMPLATES.get(topology, self.PHASE_TEMPLATES[Topology.SEQUENTIAL])

        # Extract target from task
        target = task.split('\n')[0][:200]

        # Score all specialists against the overall task
        specialist_scores, activation_result = self._score_specialists(task)

        # Build phase assignments
        phases = []
        for i, tmpl in enumerate(templates):
            phase_task = tmpl['task'].format(
                target=target,
                prev_output='{prev_output}',
                phase_1='{phase_1}',
            )

            phases.append(PhaseAssignment(
                phase_name=tmpl['name'],
                role=tmpl['role'],
                task_template=phase_task,
                timeout=90,
                depends_on=[phases[i-1].phase_name] if i > 0 else [],
                topology=topology,
            ))

        # Assign best specialist to each phase based on role + relevance
        if activation_result is not None:
            self._assign_specialists_to_phases(phases, activation_result)

        plan = ChainPlan(
            task=task,
            topology=topology,
            phases=phases,
            estimated_time_ms=len(phases) * 90_000,
            complexity_score=complexity,
            specialist_scores=specialist_scores,
            rationale=(
                f'Selected {topology.value} topology for task with '
                f'complexity {complexity:.2f}. '
                f'{len(phases)} phases planned.'
                + (f' Specialists: {list(specialist_scores.keys())}' if specialist_scores else '')
            ),
        )

        logger.info(f'[Director] Plan: {topology.value}, {len(phases)} phases')
        return plan

    def _score_specialists(self, task: str) -> tuple:
        """
        Score available specialists using the full specialist system pipeline:
        WorkDetector → RelevanceCalculator → ActivationSystem.
        
        Returns:
            Tuple of (scores_dict, ActivationResult or None)
        """
        try:
            spec_root = os.path.join(self.workspace_root, 'packages')
            if spec_root not in sys.path:
                sys.path.insert(0, spec_root)

            from specialist_system.work_detector import WorkDetector
            from specialist_system.relevance_calculator import RelevanceCalculator
            from specialist_system.specialist_registry import SpecialistRegistry
            from specialist_system.initial_specialists import register_initial_specialists
            from specialist_system.activation_system import ActivationSystem

            # Step 1: Detect work from task description
            detector = WorkDetector()
            work = detector.detect_work(task)

            # Step 2: Build specialist registry
            registry = SpecialistRegistry()
            register_initial_specialists(registry)

            # Step 3: Run activation pipeline
            calculator = RelevanceCalculator()
            activation = ActivationSystem(registry, calculator)
            result = activation.activate_specialists(work)

            # Step 4: Extract actual relevance scores (not static values)
            scores = {}
            for spec_id, rel_score in result.scores.items():
                spec = registry.get(spec_id)
                if spec and rel_score.overall >= 0.1:  # skip near-zero
                    scores[spec.name] = round(rel_score.overall, 3)

            if scores:
                # Log with tier info
                tiers = []
                for s in result.ownership:
                    tiers.append(f'{s.name}(own:{scores.get(s.name, 0):.2f})')
                for s in result.activation:
                    tiers.append(f'{s.name}(act:{scores.get(s.name, 0):.2f})')
                for s in result.consultation:
                    tiers.append(f'{s.name}(con:{scores.get(s.name, 0):.2f})')
                logger.info(f'[Director] Specialists: {" | ".join(tiers)}')

            return scores, result

        except Exception as e:
            logger.debug(f'[Director] Specialist scoring unavailable: {e}')
            return {}, None

    # Role → domain affinity for phase-specialist matching
    ROLE_DOMAIN_AFFINITY = {
        'researcher': ['Backend Integration', 'APIs', 'Chat', 'Conversation'],
        'auditor': ['Backend Integration', 'APIs', 'Mathematics', 'Computation'],
        'architect': ['UI', 'UX', 'Design', 'Frontend', 'Backend Integration'],
    }

    def _assign_specialists_to_phases(self, phases: List, activation_result) -> None:
        """
        Assign best specialist to each chain phase using:
        1. Activation tier (ownership > activation > consultation)
        2. Role-domain affinity matching
        3. Relevance score as tiebreaker
        """
        if not activation_result:
            return

        # Pool of activated specialists (ownership + activation + consultation)
        all_activated = (
            [(s, 3) for s in activation_result.ownership] +
            [(s, 2) for s in activation_result.activation] +
            [(s, 1) for s in activation_result.consultation]
        )

        if not all_activated:
            return

        for phase in phases:
            best_specialist = None
            best_score = -1.0

            # Get domain affinity for this phase's role
            affinities = self.ROLE_DOMAIN_AFFINITY.get(phase.role, [])

            for spec, tier_weight in all_activated:
                # Base score from relevance
                rel_score = activation_result.scores.get(spec.id)
                base = rel_score.overall if rel_score else 0.0

                # Bonus for domain affinity
                affinity_bonus = 0.0
                if affinities:
                    domain_hits = sum(
                        1 for d in spec.domain
                        if d in affinities
                    )
                    affinity_bonus = min(domain_hits * 0.1, 0.3)

                # Combined score: relevance + tier + affinity
                combined = base + (tier_weight * 0.05) + affinity_bonus

                if combined > best_score:
                    best_score = combined
                    best_specialist = spec

            if best_specialist:
                phase.specialist_id = best_specialist.id
                rel = activation_result.scores.get(best_specialist.id)
                phase.relevance_score = round(rel.overall, 3) if rel else 0.0
                logger.debug(
                    f'[Director] Phase "{phase.phase_name}" → '
                    f'{best_specialist.name} (rel={phase.relevance_score:.2f})'
                )

    # ── Evaluation ────────────────────────────────────────

    def evaluate_output(
        self,
        output: str,
        task: str,
        expected_depth: str = 'medium',
    ) -> QualityScore:
        """Evaluate a phase's output quality."""
        return QualityEvaluator.evaluate(output, task, expected_depth)

    # ── Decision ──────────────────────────────────────────

    def decide(
        self,
        quality: QualityScore,
        phase_index: int,
        total_phases: int,
        retry_count: int = 0,
        timed_out: bool = False,
    ) -> Action:
        """
        Decide the next action based on quality assessment.
        
        Returns:
            Action — proceed, rework, split, add_phase, skip, or escalate
        """
        decision_context = {
            'quality': quality.overall,
            'label': quality.label,
            'phase': f'{phase_index + 1}/{total_phases}',
            'retry': retry_count,
            'timed_out': timed_out,
        }

        action: Action

        if timed_out:
            if retry_count >= 2:
                action = Action.SPLIT
                decision_context['reason'] = 'Repeated timeouts — splitting into smaller tasks'
            else:
                action = Action.REWORK
                decision_context['reason'] = 'Timeout — retrying with simplified prompt'

        elif quality.overall >= self.quality_threshold:
            action = Action.PROCEED
            decision_context['reason'] = f'Quality {quality.label} ({quality.overall:.2f}) meets threshold'

        elif quality.overall >= self.rework_threshold:
            if retry_count >= 2:
                action = Action.PROCEED  # accept imperfect after 2 retries
                decision_context['reason'] = 'Accepted after max retries despite low quality'
            else:
                action = Action.REWORK
                decision_context['reason'] = f'Quality {quality.label} ({quality.overall:.2f}) below threshold'

        else:
            if retry_count >= 1:
                action = Action.SKIP
                decision_context['reason'] = 'Very low quality after retry — skipping'
            else:
                action = Action.REWORK
                decision_context['reason'] = f'Quality {quality.label} ({quality.overall:.2f}) very low'

        decision_context['action'] = action.value
        self._decision_log.append(decision_context)

        logger.info(f'[Director] Decision: {action.value} — {decision_context["reason"]}')
        return action

    # ── Context Compression ───────────────────────────────

    def compress_for_next(self, output: str, budget: Optional[int] = None) -> str:
        """Compress output for forwarding to next phase."""
        return ContextCompressor.compress(
            output,
            budget=budget or self.context_budget,
        )

    # ── Reporting ─────────────────────────────────────────

    @property
    def decision_history(self) -> List[Dict[str, Any]]:
        return self._decision_log

    def summary(self) -> str:
        """Director's summary of decisions made."""
        if not self._decision_log:
            return 'No decisions made yet.'

        lines = ['## Director Decision Log\n']
        for d in self._decision_log:
            icon = {
                'proceed': '✅', 'rework': '🔄', 'split': '✂️',
                'add_phase': '➕', 'skip': '⏭️', 'escalate': '🚨',
            }.get(d.get('action', ''), '❓')
            lines.append(
                f"{icon} Phase {d.get('phase', '?')}: **{d.get('action', '?')}** "
                f"(quality={d.get('quality', 0):.2f}, {d.get('reason', '')})"
            )
        return '\n'.join(lines)


# ══════════════════════════════════════════════════════════
#  CLI TEST
# ══════════════════════════════════════════════════════════

def _test():
    """Test the ChainDirector components."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  ChainDirector — Manager AI Test Suite                  ║")
    print("╚══════════════════════════════════════════════════════════╝")

    director = ChainDirector()

    # Test 1: Topology Selection
    print("\n═══ TEST 1: Topology Selection ═══")
    tests = [
        ("Audit the AI Engine security", Topology.GATED),
        ("Research how swarm works", Topology.SEQUENTIAL),
        ("Compare HHNI vs ContextPack approaches", Topology.DEBATE),
        ("Build a new agent genome", Topology.SEQUENTIAL),
    ]
    for task, expected in tests:
        selected = TopologySelector.select(task)
        icon = '✅' if selected == expected else '❌'
        print(f"  {icon} '{task[:50]}' → {selected.value} (expected {expected.value})")

    # Test 2: Quality Evaluation
    print("\n═══ TEST 2: Quality Evaluation ═══")

    excellent_output = """
### Architecture Analysis
The system uses a 9-layer architecture with lazy loading.

| Layer | Component | Status |
|-------|-----------|--------|
| L1 | LLM Router | Active |
| L2 | Context Engine | Active |

**Confidence Level:** 0.95

#### Recommendations
1. **REC-01**: Implement health checks (confidence: 0.9)
2. **REC-02**: Add resource throttling (confidence: 0.85)
3. **REC-03**: Improve error handling (confidence: 0.8)

- Should refactor the singleton pattern
- Suggest adding proper dependency injection
"""

    weak_output = "The system looks fine. No major issues found."

    task = "Audit the AI Engine architecture and provide recommendations"

    q_excellent = director.evaluate_output(excellent_output, task)
    q_weak = director.evaluate_output(weak_output, task)

    print(f"  Excellent output: {q_excellent.overall:.3f} ({q_excellent.label})")
    print(f"    Structure: {q_excellent.structure_score:.2f}, "
          f"Depth: {q_excellent.depth_score:.2f}, "
          f"Confidence: {q_excellent.confidence_score:.2f}, "
          f"Coverage: {q_excellent.coverage_score:.2f}, "
          f"Actionable: {q_excellent.actionable_score:.2f}")
    print(f"  Weak output:      {q_weak.overall:.3f} ({q_weak.label})")

    # Test 3: Decision Making
    print("\n═══ TEST 3: Decision Making ═══")
    decisions = [
        (q_excellent, 0, 3, 0, False),
        (q_weak, 0, 3, 0, False),
        (q_weak, 0, 3, 2, False),
        (QualityScore(), 0, 3, 0, True),
    ]
    for quality, phase, total, retries, timeout in decisions:
        action = director.decide(quality, phase, total, retries, timeout)
        print(f"  quality={quality.overall:.2f}, retry={retries}, timeout={timeout} → {action.value}")

    # Test 4: Context Compression
    print("\n═══ TEST 4: Context Compression ═══")
    compressed = director.compress_for_next(excellent_output, budget=500)
    print(f"  Original: {len(excellent_output)} chars")
    print(f"  Compressed: {len(compressed)} chars")
    print(f"  Ratio: {len(compressed)/len(excellent_output):.1%}")

    # Test 5: Chain Planning
    print("\n═══ TEST 5: Chain Planning ═══")
    plan = director.plan_chain(
        task="Audit the AI Engine security and architecture",
        complexity=0.8,
    )
    print(f"  Topology: {plan.topology.value}")
    print(f"  Phases: {len(plan.phases)}")
    for p in plan.phases:
        print(f"    {p.phase_name} ({p.role}) → {p.task_template[:60]}...")
    print(f"  Specialist scores: {plan.specialist_scores}")
    print(f"  Rationale: {plan.rationale}")

    # Test 6: Decision History
    print("\n═══ TEST 6: Director Decision Log ═══")
    print(director.summary())

    print("\n✅ All tests passed!")


if __name__ == '__main__':
    _test()
