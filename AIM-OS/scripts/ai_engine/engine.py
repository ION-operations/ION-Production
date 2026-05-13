"""
AIM-OS AI Engine — Unified Engine Facade v2.0

The master entry point for the entire AI Engine.
Composes all subsystems into a single interface:

    engine = AIEngine(workspace_root='...')
    result = engine.execute("Fix the auth bug", active_file="auth.py")
    print(engine.status())

Architecture layers (v2.0):
    L1  LLM Providers       — Gemini CLI (headless), LLM Client (Gemini/Cerebras/Anthropic API)
    L2  Intelligent Router   — packages/router (Scout→Bandit→Rules ML pipeline)
    L3  Context Engine       — context_pack, tool_advisor (DaemonRAG integration)
    L4  Agent Runtime        — agent_registry, genome_loader, specialist_system
    L5  Self-Improvement     — agent_learner, execution_trace
    L6  Swarm                — orchestrator, worker_manager, contracts
    L7  Safety               — vif_gates, safety_systems
    L8  Session              — session_manager
    L9  Chains               — prompt_chain_executor (quality gates, system steps)
"""

import os
import time
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
import json

logger = logging.getLogger('ai_engine')


@dataclass
class EngineConfig:
    """Configuration for the AI Engine."""
    workspace_root: str = ''
    genome_dir: str = ''
    use_daemon_rag: bool = True
    max_workers: int = 5
    default_model: str = 'auto'
    enable_learning: bool = True
    enable_traces: bool = True
    enable_vif: bool = True
    enable_router: bool = True
    log_level: str = 'INFO'


@dataclass
class EngineResult:
    """Result of an engine execution."""
    success: bool
    output: str = ''
    confidence: float = 0.0
    model_used: str = ''
    agent_used: str = ''
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    trace_id: str = ''
    session_id: str = ''
    time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)
    tool_plan: Optional[Dict[str, Any]] = None


class AIEngine:
    """
    Unified AI Engine v2.0 — the master orchestrator.

    Integrates all AIM-OS layers:
        - LLM routing via Gemini CLI headless (primary) + LLM Client API (fallback)
        - Intelligent Router (packages/router) with Scout→Bandit→Rules ML pipeline
        - Context pipeline (DaemonRAG integration)
        - Agent registry + genome loading
        - Swarm orchestration
        - VIF safety gates
        - Structured execution traces
        - Self-improvement learning loop

    Usage:
        engine = AIEngine(workspace_root='/path/to/AIM-OS')
        result = engine.execute("Fix the auth module", active_file="auth.py")

        # Swarm execution
        result = engine.swarm_execute("Refactor the entire auth system", workers=3)

        # Status
        print(engine.status())
    """

    VERSION = '2.0.0'

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        if not self.config.workspace_root:
            self.config.workspace_root = os.getcwd()

        # ── Lazy-loaded subsystems ──
        self._registry = None
        self._genome_loader = None
        self._context_builder = None
        self._tool_advisor = None
        self._session_manager = None
        self._trace_store = None
        self._agent_learner = None
        self._vif_gate = None
        self._llm_router = None
        self._orchestrator = None
        # v2.0: New integrated subsystems
        self._cli_provider = None
        self._smart_router = None
        self._llm_client = None
        self._intent_classifier = None
        self._work_detector = None
        self._chain_executor = None
        self._safety_orchestrator = None
        self._thought_articulator = None

        logger.info(f'[AIEngine] Initialised v{self.VERSION} at {self.config.workspace_root}')

    # ── Lazy loaders ─────────────────────────────────────

    @property
    def registry(self):
        if self._registry is None:
            from ai_engine.registry import AgentRegistry
            self._registry = AgentRegistry()
        return self._registry

    @property
    def genome_loader(self):
        if self._genome_loader is None:
            from ai_engine.genome_loader import GenomeLoader
            self._genome_loader = GenomeLoader(self.config.workspace_root)
        return self._genome_loader

    @property
    def context_builder(self):
        if self._context_builder is None:
            from ai_engine.context.context_pack import ContextPackBuilder
            self._context_builder = ContextPackBuilder(
                workspace_root=self.config.workspace_root,
                use_daemon_rag=self.config.use_daemon_rag,
            )
        return self._context_builder

    @property
    def tool_advisor(self):
        if self._tool_advisor is None:
            from ai_engine.context.tool_advisor import ToolAdvisor
            self._tool_advisor = ToolAdvisor(self.config.workspace_root)
        return self._tool_advisor

    @property
    def sessions(self):
        if self._session_manager is None:
            from ai_engine.session_manager import SessionManager
            self._session_manager = SessionManager()
        return self._session_manager

    @property
    def traces(self):
        if self._trace_store is None:
            from ai_engine.traces.execution_trace import TraceStore
            self._trace_store = TraceStore()
        return self._trace_store

    @property
    def learner(self):
        if self._agent_learner is None:
            from ai_engine.learning.agent_learner import AgentLearner
            self._agent_learner = AgentLearner(self.config.workspace_root)
        return self._agent_learner

    @property
    def vif(self):
        if self._vif_gate is None:
            from ai_engine.safety.vif_gates import VIFGate
            self._vif_gate = VIFGate()
        return self._vif_gate

    @property
    def router(self):
        """Legacy router — kept for backwards compatibility."""
        if self._llm_router is None:
            from ai_engine.llm_router import LLMRouter
            self._llm_router = LLMRouter()
        return self._llm_router

    @property
    def orchestrator(self):
        if self._orchestrator is None:
            from ai_engine.swarm.orchestrator import SwarmOrchestrator
            self._orchestrator = SwarmOrchestrator(
                workspace_root=self.config.workspace_root,
                max_workers=self.config.max_workers,
            )
        return self._orchestrator

    # ── v2.0 New Subsystems ──────────────────────────────

    @property
    def cli_provider(self):
        """Gemini CLI headless provider — primary LLM pathway."""
        if self._cli_provider is None:
            from ai_engine.providers.gemini_cli_provider import GeminiCLIProvider
            self._cli_provider = GeminiCLIProvider(
                working_directory=self.config.workspace_root,
                allowed_mcp_servers=['none'],  # Bypass lucid-mcp 400
            )
        return self._cli_provider

    @property
    def smart_router(self):
        """Intelligent Router (packages/router) — Scout→Bandit→Rules ML pipeline."""
        if self._smart_router is None:
            try:
                from packages.router.core.router import Router
                from packages.router.core.scout import ScoutLLM
                from packages.router.core.bandit import BanditScorer
                from packages.router.core.rules import RulesEngine
                from packages.router.core.manifest import ToolManifest
                from packages.router.core.snapshot import SnapshotBuilder

                self._smart_router = Router(
                    scout=ScoutLLM(),
                    bandit=BanditScorer(),
                    rules=RulesEngine(),
                    manifest=ToolManifest(),
                    snapshot_builder=SnapshotBuilder(),
                )
                logger.info('[AIEngine] Smart Router (packages/router) loaded')
            except ImportError as e:
                logger.warning(f'[AIEngine] Smart Router not available: {e}')
                self._smart_router = None
        return self._smart_router

    @property
    def llm_client(self):
        """Unified LLM Client (packages/llm_client) — API fallback."""
        if self._llm_client is None:
            try:
                from packages.llm_client import GeminiClient
                api_key = os.environ.get('GEMINI_API_KEY', '')
                if api_key:
                    self._llm_client = GeminiClient(api_key=api_key)
                    logger.info('[AIEngine] LLM Client (Gemini API) loaded')
                else:
                    logger.info('[AIEngine] No GEMINI_API_KEY — CLI-only mode')
                    self._llm_client = None
            except ImportError as e:
                logger.warning(f'[AIEngine] LLM Client not available: {e}')
                self._llm_client = None
        return self._llm_client

    @property
    def intent_classifier(self):
        """Intent Classification Engine (packages/intent_classification)."""
        if self._intent_classifier is None:
            try:
                from packages.intent_classification.classification_engine import ClassificationEngine
                self._intent_classifier = ClassificationEngine()
                logger.info('[AIEngine] Intent Classifier loaded')
            except ImportError as e:
                logger.warning(f'[AIEngine] Intent Classifier not available: {e}')
                self._intent_classifier = None
        return self._intent_classifier

    @property
    def work_detector(self):
        """Work Detector (packages/specialist_system) — chat-to-work conversion."""
        if self._work_detector is None:
            try:
                from packages.specialist_system.work_detector import WorkDetector
                self._work_detector = WorkDetector()
                logger.info('[AIEngine] Work Detector loaded')
            except ImportError as e:
                logger.warning(f'[AIEngine] Work Detector not available: {e}')
                self._work_detector = None
        return self._work_detector

    @property
    def chain_executor(self):
        """Chain Executor (packages/prompt_chain_executor) — multi-step workflows."""
        if self._chain_executor is None:
            try:
                from packages.prompt_chain_executor.executor import ChainExecutor
                self._chain_executor = ChainExecutor(
                    vif_validator=self._get_vif_validator(),
                )
                logger.info('[AIEngine] Chain Executor loaded')
            except ImportError as e:
                logger.warning(f'[AIEngine] Chain Executor not available: {e}')
                self._chain_executor = None
        return self._chain_executor

    @property
    def safety(self):
        """Safety Orchestrator (packages/safety_systems) — file operation protection."""
        if self._safety_orchestrator is None:
            try:
                from packages.safety_systems.safety_orchestrator import SafetyOrchestrator
                self._safety_orchestrator = SafetyOrchestrator()
                logger.info('[AIEngine] Safety Orchestrator loaded')
            except ImportError as e:
                logger.warning(f'[AIEngine] Safety Orchestrator not available: {e}')
                self._safety_orchestrator = None
        return self._safety_orchestrator

    @property
    def thought_articulator(self):
        """Thought Articulator (packages/meta_reasoning) — meta-cognitive traces."""
        if self._thought_articulator is None:
            try:
                from packages.meta_reasoning.thought_articulator import ThoughtArticulator
                self._thought_articulator = ThoughtArticulator(
                    llm_client=self.llm_client,
                )
                logger.info('[AIEngine] Thought Articulator loaded')
            except ImportError as e:
                logger.warning(f'[AIEngine] Thought Articulator not available: {e}')
                self._thought_articulator = None
        return self._thought_articulator

    def _get_vif_validator(self):
        """Create VIF validator callback for ChainExecutor."""
        def validate(confidence: float) -> bool:
            try:
                result = self.vif.check(action='chain:step', confidence=confidence)
                return result.passed
            except Exception:
                return confidence >= 0.70
        return validate

    # ── Core Execution ───────────────────────────────────

    def execute(
        self,
        task: str,
        active_file: str = '',
        include_files: Optional[List[str]] = None,
        agent_id: str = '',
        model: str = 'auto',
        max_tokens: int = 0,
    ) -> EngineResult:
        """
        Execute a single task through the full engine pipeline.

        Pipeline v2.0:
            1. Intent classification (multi-axis ML)
            2. Context analysis (DaemonRAG) → ContextPack
            3. Agent selection (Registry + Intent-driven)
            4. Genome loading (Base + RoleOverlay + TaskOverlay)
            5. VIF gate check (with intent risk/complexity)
            6. LLM execution (Gemini CLI headless primary, API fallback)
            7. Trace recording
            8. Learning update
        """
        start = time.time()
        intent_result = None
        work = None

        # 1. Classify intent (if available)
        if self.intent_classifier:
            try:
                intent_result = self.intent_classifier.classify_intent(task)
                logger.info(f'[AIEngine] Intent: {intent_result.mission_intent.primary_category.value} '
                           f'(confidence={intent_result.classification_confidence:.2f})')
            except Exception as e:
                logger.warning(f'[AIEngine] Intent classification failed: {e}')

        # 1b. Detect work for specialist routing (if available)
        if self.work_detector:
            try:
                intent_analysis = None
                if intent_result:
                    from packages.specialist_system.work_detector import IntentAnalysis
                    intent_analysis = IntentAnalysis(
                        intent=intent_result.mission_intent.primary_category.value,
                        mode=intent_result.mission_intent.lifecycle_stage.value,
                        domains=intent_result.mission_intent.facets.get('domains', []) if intent_result.mission_intent.facets else [],
                        systems=intent_result.mission_intent.facets.get('systems', []) if intent_result.mission_intent.facets else [],
                        complexity=intent_result.mission_intent.complexity_score,
                    )
                work = self.work_detector.detect_work(task, intent_analysis)
                logger.info(f'[AIEngine] Work detected: domains={work.domain}, systems={work.systems}')
            except Exception as e:
                logger.warning(f'[AIEngine] Work detection failed: {e}')

        # 2. Build context pack
        pack = self.context_builder.build_for_task(
            task=task,
            active_file=active_file,
            include_files=include_files or [],
            max_tokens=max_tokens,
        )

        # 3. Select agent (intent-driven if available, else fallback)
        if not agent_id:
            if intent_result and intent_result.mission_intent:
                # Use classified intent for smarter agent selection
                task_type = intent_result.mission_intent.primary_category.value
            else:
                task_type = pack.profile.task_type if pack.profile else 'coding'
            agent_def = self.registry.find_best_for(task_type)
            agent_id = agent_def.agent_id if agent_def else 'coder_v1'
        else:
            agent_def = self.registry.get(agent_id)

        # 4. Build genome
        role = agent_def.genome_role_overlay if agent_def else 'coder'
        genome = self.genome_loader.build_genome(
            role=role,
            task=task,
        )

        # 5. VIF gate (uses intent risk if available)
        if self.config.enable_vif:
            confidence = pack.profile.confidence if pack.profile else 0.5
            if intent_result and intent_result.mission_intent:
                # Use classified complexity to adjust confidence threshold
                complexity = intent_result.mission_intent.complexity_score
                if complexity and complexity > 0.8:
                    confidence = min(confidence, 0.4)  # High-complexity = stricter gate
            gate_result = self.vif.check(
                action='file:write',
                confidence=confidence,
            )
            if not gate_result.passed:
                return EngineResult(
                    success=False,
                    output=f'VIF gate blocked: {gate_result.reason}',
                    confidence=gate_result.confidence,
                    agent_used=agent_id,
                    time_ms=(time.time() - start) * 1000,
                    errors=[gate_result.reason],
                )

        # 6. LLM execution — Gemini CLI headless (primary)
        system_prompt = genome.to_system_prompt()
        context = pack.get_content()
        # Enrich prompt with intent classification if available
        intent_context = ''
        if intent_result and intent_result.mission_intent:
            mi = intent_result.mission_intent
            intent_context = (f"\n[Intent: {mi.primary_category.value} | "
                            f"Lifecycle: {mi.lifecycle_stage.value} | "
                            f"Scope: {mi.scope_level.value} | "
                            f"Complexity: {mi.complexity_score:.2f}]")
        full_prompt = f"{context}{intent_context}\n\n---\n\nTask: {task}"

        result_text = ''
        model_used = model
        try:
            # Primary: Gemini CLI headless (unlimited via Ultra)
            provider = self.cli_provider
            if provider and provider.is_available:
                response = provider.run_headless(
                    prompt=full_prompt,
                    system=system_prompt,
                    model=model if model != 'auto' else '',
                )
                if response.success:
                    result_text = response.content
                    model_used = response.model or 'gemini-cli'
                else:
                    # Fallback: LLM Client API
                    logger.warning(f'[AIEngine] CLI failed: {response.error}, trying API')
                    if self.llm_client:
                        api_response = self.llm_client.generate(
                            prompt=f"{system_prompt}\n\n{full_prompt}",
                        )
                        result_text = api_response.text
                        model_used = api_response.model
                    else:
                        result_text = f'CLI error: {response.error}'
            else:
                # CLI not available — try API
                if self.llm_client:
                    api_response = self.llm_client.generate(
                        prompt=f"{system_prompt}\n\n{full_prompt}",
                    )
                    result_text = api_response.text
                    model_used = api_response.model
                else:
                    result_text = 'No LLM provider available (CLI not installed, no API key)'
        except Exception as e:
            result_text = f'LLM execution error: {e}'
            logger.error(f'[AIEngine] LLM error: {e}')

        # 7. Create trace
        from ai_engine.traces.execution_trace import ExecutionTrace
        trace = ExecutionTrace(
            task_description=task,
            task_type=intent_result.mission_intent.primary_category.value if intent_result else (pack.profile.task_type if pack.profile else ''),
            agent_name=agent_id,
            agent_role=role,
            model_used=model_used,
            outcome='success' if result_text and 'error' not in result_text.lower() else 'partial',
            confidence=pack.profile.confidence if pack.profile else 0.5,
            context_tokens=pack.total_tokens,
            total_time_ms=(time.time() - start) * 1000,
        )

        if self.config.enable_traces:
            self.traces.save(trace)

        # 8. Learn
        if self.config.enable_learning:
            insights = self.learner.learn_from_trace(trace)
            learnings = [i.description for i in insights]
        else:
            learnings = []

        return EngineResult(
            success=True,
            output=result_text,
            confidence=trace.confidence,
            model_used=model_used,
            agent_used=agent_id,
            trace_id=trace.trace_id,
            time_ms=trace.total_time_ms,
            learnings=learnings,
        )

    # ── Chain Execution ──────────────────────────────────

    def execute_chain(
        self,
        chain_definition: Dict[str, Any],
        inputs: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        agent_name: str = 'primary',
    ) -> EngineResult:
        """
        Execute a multi-step prompt chain with quality gates.

        Uses ChainExecutor from packages/prompt_chain_executor for:
        - Dynamic conditional branching
        - Quality gates with configurable thresholds
        - State persistence in CMC
        - Confidence routing
        - System steps (CMC, VIF, APOE, HHNI, SEG)
        """
        start = time.time()

        executor = self.chain_executor
        if not executor:
            return EngineResult(
                success=False,
                output='ChainExecutor not available',
                errors=['packages/prompt_chain_executor not installed'],
                time_ms=(time.time() - start) * 1000,
            )

        try:
            result = executor.execute_chain(
                chain_definition=chain_definition,
                inputs=inputs,
                context=context,
                agent_name=agent_name,
            )

            return EngineResult(
                success=result.get('success', False),
                output=json.dumps(result, indent=2),
                confidence=result.get('metrics', {}).get('avg_confidence', 0.0),
                time_ms=(time.time() - start) * 1000,
                tool_plan=result,
            )
        except Exception as e:
            return EngineResult(
                success=False,
                output='',
                errors=[str(e)],
                time_ms=(time.time() - start) * 1000,
            )

    # ── Swarm Execution ──────────────────────────────────

    def swarm_execute(
        self,
        task: str,
        workers: int = 3,
        active_file: str = '',
    ) -> EngineResult:
        """
        Execute a complex task using the swarm orchestrator.
        Decomposes → assigns → gates → merges.
        """
        start = time.time()

        try:
            result = self.orchestrator.execute(task)

            return EngineResult(
                success=result.get('success', False),
                output=json.dumps(result, indent=2) if isinstance(result, dict) else str(result),
                time_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return EngineResult(
                success=False,
                output='',
                errors=[str(e)],
                time_ms=(time.time() - start) * 1000,
            )

    # ── Status ───────────────────────────────────────────

    def status(self) -> dict:
        """Get full engine status."""
        status: Dict[str, Any] = {
            'version': self.VERSION,
            'workspace': self.config.workspace_root,
            'subsystems': {},
        }

        # Core subsystems
        subsystem_checks = {
            'registry': lambda: self.registry.status(),
            'genome_loader': lambda: self.genome_loader.status(),
            'sessions': lambda: self.sessions.status(),
            'traces': lambda: self.traces.stats(),
            'learner': lambda: self.learner.status(),
            'vif': lambda: self.vif.status(),
        }

        for name, check in subsystem_checks.items():
            try:
                status['subsystems'][name] = check()
            except Exception:
                status['subsystems'][name] = 'not loaded'

        # v2.0 subsystems
        v2_checks = {
            'cli_provider': lambda: 'available' if self._cli_provider else 'lazy',
            'smart_router': lambda: 'loaded' if self._smart_router else 'lazy',
            'llm_client': lambda: 'loaded' if self._llm_client else ('no API key' if not os.environ.get('GEMINI_API_KEY') else 'lazy'),
            'intent_classifier': lambda: 'loaded' if self._intent_classifier else 'lazy',
            'work_detector': lambda: 'loaded' if self._work_detector else 'lazy',
            'chain_executor': lambda: 'loaded' if self._chain_executor else 'lazy',
            'safety': lambda: 'loaded' if self._safety_orchestrator else 'lazy',
            'thought_articulator': lambda: 'loaded' if self._thought_articulator else 'lazy',
        }

        for name, check in v2_checks.items():
            try:
                status['subsystems'][name] = check()
            except Exception:
                status['subsystems'][name] = 'not loaded'

        return status

