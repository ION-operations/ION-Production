"""
AIM-OS AI Engine — Context Pack Pipeline

Sev's unified context strategy: Evidence → Retrieval → Budgeting → Pack.

This is the DEEP integration layer. It wraps:
    - DaemonRAG ContextParser (parse user input for clues)
    - DaemonRAG TaskClassifier (classify task type + complexity)
    - DaemonRAG IntentInferencer (infer user goals)
    - CMC retrieval (past memories, execution traces)
    - HHNI semantic search (when DGraph is available)
    - Workspace file search (from v0.1 context_engine)
    - Recent git diffs (for change context)
    - Canonical docs index

The output is a ContextPack — an immutable, budget-constrained
bundle of context that gets attached to every JobPacket.

Workers NEVER freestyle file crawling — they get a ContextPack
and work within it.
"""

import os
import time
import json
import logging
import subprocess
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger('ai_engine.context_pack')


# ── Enums ─────────────────────────────────────────────────

class EvidenceType(str, Enum):
    FILE_CONTENT = 'file_content'
    FILE_SUMMARY = 'file_summary'
    SYMBOL_INDEX = 'symbol_index'
    GIT_DIFF = 'git_diff'
    CMC_MEMORY = 'cmc_memory'
    HHNI_RESULT = 'hhni_result'
    DAEMON_RAG_CONTEXT = 'daemon_rag_context'
    CONVERSATION_HISTORY = 'conversation_history'
    GENOME_EXCERPT = 'genome_excerpt'
    EDITOR_STATE = 'editor_state'
    SEARCH_RESULT = 'search_result'
    CANONICAL_DOC = 'canonical_doc'


# ── Data Models ──────────────────────────────────────────

@dataclass
class EvidenceItem:
    """A single piece of evidence for context assembly."""
    type: str
    source: str               # file path, memory id, search query
    content: str              # the actual content
    relevance: float = 0.5    # 0.0 to 1.0
    token_estimate: int = 0   # estimated tokens
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.token_estimate == 0:
            self.token_estimate = int(len(self.content) / 3.5)


@dataclass
class ContextProfile:
    """
    Analysis of the task context.
    Built from DaemonRAG ContextParser + TaskClassifier + IntentInferencer.
    """
    task_type: str = 'general'       # coding, planning, debugging, etc.
    complexity: str = 'medium'       # trivial, low, medium, high, critical
    intent: str = ''                 # inferred user intent
    keywords: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    confidence: float = 0.5
    classification_source: str = ''  # 'daemon_rag' or 'heuristic'


@dataclass
class ContextPack:
    """
    Immutable, budget-constrained context bundle.
    
    Attached to every JobPacket. Workers operate within this
    context — they don't freestyle file crawling.
    
    Usage:
        pack = builder.build_for_task("Fix the auth bug", active_file="auth.py")
        pack_for_job = pack.for_job("job_abc123")
    """
    pack_id: str = ''
    task_description: str = ''
    profile: Optional[ContextProfile] = None

    # Evidence layers (ordered by priority)
    evidence: List[EvidenceItem] = field(default_factory=list)

    # Budget tracking
    total_tokens: int = 0
    max_tokens: int = 32000
    token_utilization: float = 0.0

    # Metadata
    created_at: float = field(default_factory=time.time)
    build_time_ms: float = 0.0

    def get_content(self) -> str:
        """Get the assembled context content."""
        parts = []
        for item in self.evidence:
            header = f"[{item.type.upper()}] {item.source}"
            parts.append(f"--- {header} ---\n{item.content}")
        return '\n\n'.join(parts)

    def for_job(self, job_id: str, max_tokens: int = 0) -> 'ContextPack':
        """Create a job-specific slice of this pack."""
        budget = max_tokens or self.max_tokens
        sliced_evidence = []
        used_tokens = 0

        for item in self.evidence:
            if used_tokens + item.token_estimate <= budget:
                sliced_evidence.append(item)
                used_tokens += item.token_estimate

        return ContextPack(
            pack_id=f"{self.pack_id}__{job_id}",
            task_description=self.task_description,
            profile=self.profile,
            evidence=sliced_evidence,
            total_tokens=used_tokens,
            max_tokens=budget,
            token_utilization=used_tokens / budget if budget > 0 else 0,
        )

    def to_dict(self) -> dict:
        return {
            'pack_id': self.pack_id,
            'task': self.task_description[:100],
            'total_tokens': self.total_tokens,
            'max_tokens': self.max_tokens,
            'utilization': f"{self.token_utilization:.1%}",
            'evidence_count': len(self.evidence),
            'evidence_types': list(set(e.type for e in self.evidence)),
            'build_time_ms': self.build_time_ms,
        }


# ── Context Pack Builder ─────────────────────────────────

class ContextPackBuilder:
    """
    Builds ContextPacks using the 4-stage pipeline:
        1. Evidence: gather raw context from all sources
        2. Retrieval: semantic search via HHNI + CMC
        3. Budgeting: select minimal slices within token budget
        4. Pack: assemble final ContextPack
    
    Integrates with:
        - DaemonRAG ContextParser + TaskClassifier + IntentInferencer
        - CMC memory retrieval
        - Workspace file indexing (v0.1 context_engine)
        - Git diffs
        - Genome excerpts
    """

    # Token budgets by task type
    TASK_BUDGETS = {
        'fast': 4000,
        'coding': 24000,
        'debugging': 32000,
        'planning': 16000,
        'review': 20000,
        'research': 32000,
        'general': 12000,
    }

    def __init__(
        self,
        workspace_root: str = '',
        genome_dir: str = '',
        use_daemon_rag: bool = True,
    ):
        self.workspace_root = workspace_root or os.getcwd()
        self.genome_dir = genome_dir or os.path.join(self.workspace_root, '.agent', 'genomes')
        self._use_daemon_rag = use_daemon_rag
        self._daemon_rag = None
        self._mcp_bridge = None

    def _get_daemon_rag(self):
        """Lazy-load DaemonRAG context analyzer."""
        if self._daemon_rag is None and self._use_daemon_rag:
            try:
                import sys
                # Add DaemonRAG to path
                dag_path = os.path.join(self.workspace_root, 'daemon_rag_system')
                if dag_path not in sys.path:
                    sys.path.insert(0, dag_path)
                from context_analysis_engine.context_analyzer import (
                    ContextAnalysisEngine, ContextType, ComplexityLevel,
                )
                self._daemon_rag = ContextAnalysisEngine()
                logger.info('[ContextPack] DaemonRAG ContextAnalysisEngine loaded')
            except Exception as e:
                logger.debug(f'DaemonRAG not available: {e}')
                self._use_daemon_rag = False
        return self._daemon_rag

    def _get_mcp(self):
        """Lazy-load MCP bridge."""
        if self._mcp_bridge is None:
            from ai_engine.self_improve import MCPBridge
            self._mcp_bridge = MCPBridge()
        return self._mcp_bridge

    # ── Main Build ───────────────────────────────────────

    def build_for_task(
        self,
        task: str,
        active_file: str = '',
        include_files: Optional[List[str]] = None,
        conversation_history: str = '',
        editor_state: Optional[Dict] = None,
        max_tokens: int = 0,
    ) -> ContextPack:
        """
        Build a complete ContextPack for a task.
        
        The 4-stage pipeline:
            1. Evidence: gather from all sources
            2. Retrieval: find related from memory/search
            3. Budgeting: select within token budget
            4. Pack: assemble final pack
        """
        import uuid
        start = time.time()

        pack_id = f"ctx_{uuid.uuid4().hex[:10]}"

        # Stage 0: Profile the task
        profile = self._analyze_task(task)
        budget = max_tokens or self.TASK_BUDGETS.get(profile.task_type, 12000)

        # Stage 1: Evidence gathering
        evidence: List[EvidenceItem] = []

        # Active file (highest priority)
        if active_file and os.path.exists(active_file):
            evidence.append(self._gather_file(active_file, relevance=1.0))

        # Included files
        if include_files:
            for f in include_files[:10]:
                if os.path.exists(f):
                    evidence.append(self._gather_file(f, relevance=0.8))

        # Editor state
        if editor_state:
            evidence.append(EvidenceItem(
                type=EvidenceType.EDITOR_STATE,
                source='editor',
                content=json.dumps(editor_state, indent=2),
                relevance=0.9,
            ))

        # Conversation history
        if conversation_history:
            evidence.append(EvidenceItem(
                type=EvidenceType.CONVERSATION_HISTORY,
                source='session',
                content=conversation_history[-4000:],
                relevance=0.7,
            ))

        # Git diffs (recent changes)
        diff_content = self._gather_git_diffs()
        if diff_content:
            evidence.append(EvidenceItem(
                type=EvidenceType.GIT_DIFF,
                source='git diff HEAD~3',
                content=diff_content[:3000],
                relevance=0.6,
            ))

        # Stage 2: Retrieval
        # CMC memories
        cmc_results = self._retrieve_from_cmc(task)
        evidence.extend(cmc_results)

        # Workspace search
        search_results = self._search_workspace(task, profile.keywords)
        evidence.extend(search_results)

        # DaemonRAG context profile
        if profile.classification_source == 'daemon_rag':
            evidence.append(EvidenceItem(
                type=EvidenceType.DAEMON_RAG_CONTEXT,
                source='daemon_rag_analyzer',
                content=json.dumps({
                    'task_type': profile.task_type,
                    'complexity': profile.complexity,
                    'intent': profile.intent,
                    'capabilities': profile.required_capabilities,
                }, indent=2),
                relevance=0.4,
            ))

        # Stage 3: Budgeting
        evidence = self._budget_evidence(evidence, budget)

        # Stage 4: Pack
        total_tokens = sum(e.token_estimate for e in evidence)

        pack = ContextPack(
            pack_id=pack_id,
            task_description=task,
            profile=profile,
            evidence=evidence,
            total_tokens=total_tokens,
            max_tokens=budget,
            token_utilization=total_tokens / budget if budget > 0 else 0,
            build_time_ms=(time.time() - start) * 1000,
        )

        logger.info(
            f'[ContextPack] Built {pack_id}: {len(evidence)} items, '
            f'{total_tokens}/{budget} tokens ({pack.token_utilization:.0%}), '
            f'{pack.build_time_ms:.0f}ms'
        )

        return pack

    # ── Stage 0: Task Analysis ───────────────────────────

    def _analyze_task(self, task: str) -> ContextProfile:
        """Analyse task using DaemonRAG or heuristic fallback."""
        dag = self._get_daemon_rag()

        if dag:
            try:
                context_result = dag.analyze_context(task, {})
                return ContextProfile(
                    task_type=context_result.task_classification,
                    complexity=context_result.complexity.value if hasattr(context_result.complexity, 'value') else str(context_result.complexity),
                    intent=context_result.intent_inference,
                    keywords=context_result.keywords if hasattr(context_result, 'keywords') else [],
                    required_capabilities=context_result.required_capabilities if hasattr(context_result, 'required_capabilities') else [],
                    confidence=context_result.confidence_score,
                    classification_source='daemon_rag',
                )
            except Exception as e:
                logger.debug(f'DaemonRAG analysis failed: {e}')

        # Heuristic fallback
        task_lower = task.lower()
        task_type = 'general'
        keywords = []

        type_keywords = {
            'coding': ['fix', 'implement', 'add', 'create', 'build', 'write', 'code', 'function'],
            'debugging': ['bug', 'error', 'crash', 'fix', 'broken', 'fail', 'debug', 'issue'],
            'planning': ['plan', 'design', 'architect', 'strategy', 'approach', 'how'],
            'review': ['review', 'audit', 'check', 'quality', 'test'],
            'research': ['research', 'find', 'search', 'analyze', 'understand', 'explore'],
        }

        for ttype, kws in type_keywords.items():
            matches = [k for k in kws if k in task_lower]
            if matches:
                task_type = ttype
                keywords = matches
                break

        return ContextProfile(
            task_type=task_type,
            complexity='medium',
            intent=task[:100],
            keywords=keywords,
            confidence=0.4,
            classification_source='heuristic',
        )

    # ── Stage 1: Evidence Gathering ──────────────────────

    def _gather_file(self, path: str, relevance: float = 0.5) -> EvidenceItem:
        """Gather file content as evidence."""
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            return EvidenceItem(
                type=EvidenceType.FILE_CONTENT,
                source=path,
                content=content[:10000],  # Cap at 10k chars
                relevance=relevance,
                metadata={'size': os.path.getsize(path)},
            )
        except OSError:
            return EvidenceItem(
                type=EvidenceType.FILE_CONTENT,
                source=path,
                content=f'[Error reading file: {path}]',
                relevance=0.0,
            )

    def _gather_git_diffs(self) -> str:
        """Get recent git diffs for change context."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--stat', 'HEAD~3'],
                capture_output=True, text=True,
                cwd=self.workspace_root, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return ''

    # ── Stage 2: Retrieval ───────────────────────────────

    def _retrieve_from_cmc(self, task: str) -> List[EvidenceItem]:
        """Retrieve related memories from CMC via MCP."""
        items = []
        try:
            mcp = self._get_mcp()
            result = mcp.retrieve_memory(query=task, limit=3)
            memories = result.get('memories', [])

            for mem in memories:
                content = mem.get('content', '') if isinstance(mem, dict) else str(mem)
                items.append(EvidenceItem(
                    type=EvidenceType.CMC_MEMORY,
                    source='cmc_retrieval',
                    content=content[:2000],
                    relevance=0.5,
                ))
        except Exception as e:
            logger.debug(f'CMC retrieval failed: {e}')

        return items

    def _search_workspace(self, task: str, keywords: List[str]) -> List[EvidenceItem]:
        """Search workspace files for relevant content."""
        items = []
        search_terms = keywords[:3] if keywords else task.split()[:3]

        for term in search_terms:
            try:
                result = subprocess.run(
                    ['grep', '-rl', '--include=*.py', '--include=*.ts', '--include=*.md',
                     '-m', '3', term, '.'],
                    capture_output=True, text=True,
                    cwd=self.workspace_root, timeout=5,
                )
                if result.returncode == 0:
                    for file_path in result.stdout.strip().split('\n')[:2]:
                        if file_path:
                            abs_path = os.path.join(self.workspace_root, file_path.strip())
                            items.append(EvidenceItem(
                                type=EvidenceType.SEARCH_RESULT,
                                source=f'workspace_search:{term}',
                                content=f'Found: {file_path.strip()}',
                                relevance=0.3,
                            ))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return items

    # ── Stage 3: Budgeting ───────────────────────────────

    def _budget_evidence(
        self,
        evidence: List[EvidenceItem],
        max_tokens: int,
    ) -> List[EvidenceItem]:
        """
        Select evidence within token budget.
        Priority: highest relevance first, then trim.
        """
        # Sort by relevance (highest first)
        sorted_evidence = sorted(evidence, key=lambda e: e.relevance, reverse=True)

        selected = []
        used_tokens = 0

        for item in sorted_evidence:
            if used_tokens + item.token_estimate <= max_tokens:
                selected.append(item)
                used_tokens += item.token_estimate
            else:
                # Try truncating the item
                remaining = max_tokens - used_tokens
                if remaining > 100:
                    truncated = EvidenceItem(
                        type=item.type,
                        source=item.source,
                        content=item.content[:int(remaining * 3.5)],
                        relevance=item.relevance,
                        metadata=item.metadata,
                    )
                    selected.append(truncated)
                    break

        return selected

    # ── Status ───────────────────────────────────────────

    def status(self) -> dict:
        return {
            'workspace_root': self.workspace_root,
            'daemon_rag_available': self._daemon_rag is not None,
            'mcp_available': self._mcp_bridge.mcp_available if self._mcp_bridge else None,
            'genome_dir': self.genome_dir,
            'task_budgets': self.TASK_BUDGETS,
        }
