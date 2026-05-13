"""
AIM-OS AI Engine — Atlas: The Big Picture Agent

Atlas is the cartographer of the AIM-OS codebase. Its sole purpose
is to maintain a living, queryable knowledge graph of the project:

    - What files exist and what they do
    - How modules relate to each other
    - What architectural decisions have been made
    - What patterns are used and where
    - What changed recently and why

Atlas pre-builds context packages so that when Opus or any
enhanced worker starts a task, they already have a high-quality
understanding of the relevant landscape waiting for them.

Design by Braden (CEO):
    "An agent whose job is to keep all the indexes and maps
     and relationships and build its own context bank and stores
     and dynamically organize its main permanent context so it
     always has a quick retrieval and understanding of the big
     picture."

This is that agent.
"""

import os
import sys
import json
import time
import hashlib
import logging
import re
from pathlib import Path
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, field, asdict

logger = logging.getLogger('ai_engine.atlas')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))


# ── Data Models ──────────────────────────────────────────

@dataclass
class ModuleInfo:
    """A module/component in the project."""
    name: str
    path: str                                 # relative to workspace
    description: str = ''
    purpose: str = ''                         # one-line purpose
    files: List[str] = field(default_factory=list)
    file_count: int = 0
    total_lines: int = 0
    key_classes: List[str] = field(default_factory=list)
    key_functions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)   # other modules
    dependents: List[str] = field(default_factory=list)      # modules that use this
    tags: List[str] = field(default_factory=list)


@dataclass
class Relationship:
    """A relationship between two modules."""
    source: str
    target: str
    type: str = 'imports'       # imports, calls, extends, configures
    strength: float = 0.5       # 0-1, how tightly coupled
    evidence: str = ''          # file:line that proves this


@dataclass
class ArchitectureMap:
    """The living architecture map of the project."""
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)
    decisions: List[Dict[str, str]] = field(default_factory=list)
    patterns: List[Dict[str, str]] = field(default_factory=list)
    gotchas: List[str] = field(default_factory=list)
    last_indexed: float = 0.0
    workspace_root: str = ''
    total_files: int = 0
    total_lines: int = 0

    def to_summary(self) -> str:
        """Generate a human-readable architecture summary."""
        parts = [
            f"# AIM-OS Architecture Map",
            f"_Last indexed: {time.strftime('%Y-%m-%d %H:%M', time.localtime(self.last_indexed))}_",
            f"**{len(self.modules)} modules** | "
            f"**{self.total_files} files** | "
            f"**{self.total_lines:,} lines** | "
            f"**{len(self.relationships)} relationships**",
            "",
        ]

        # Module overview
        parts.append("## Modules\n")
        for name, mod in sorted(self.modules.items()):
            parts.append(
                f"### {name}\n"
                f"**Path:** `{mod.path}` | "
                f"**Files:** {mod.file_count} | "
                f"**Lines:** {mod.total_lines:,}\n"
                f"{mod.description}\n"
            )
            if mod.key_classes:
                parts.append(f"**Key classes:** {', '.join(mod.key_classes[:8])}")
            if mod.dependencies:
                parts.append(f"**Depends on:** {', '.join(mod.dependencies[:8])}")
            if mod.dependents:
                parts.append(f"**Used by:** {', '.join(mod.dependents[:8])}")
            parts.append("")

        # Architecture decisions
        if self.decisions:
            parts.append("## Key Decisions\n")
            for d in self.decisions:
                parts.append(f"- **{d.get('title', '?')}**: {d.get('description', '')}")
            parts.append("")

        # Patterns
        if self.patterns:
            parts.append("## Patterns\n")
            for p in self.patterns:
                parts.append(f"- **{p.get('name', '?')}**: {p.get('description', '')}")
            parts.append("")

        # Gotchas
        if self.gotchas:
            parts.append("## Known Gotchas\n")
            for g in self.gotchas:
                parts.append(f"- {g}")
            parts.append("")

        return '\n'.join(parts)

    def get_module_context(self, module_name: str) -> str:
        """Get focused context for a specific module."""
        mod = self.modules.get(module_name)
        if not mod:
            # Fuzzy match
            for name, m in self.modules.items():
                if module_name.lower() in name.lower():
                    mod = m
                    break
        if not mod:
            return f"Module '{module_name}' not found in atlas."

        parts = [
            f"# {mod.name}",
            f"**Path:** `{mod.path}`",
            f"**Purpose:** {mod.purpose or mod.description}",
            f"**Files:** {mod.file_count} | **Lines:** {mod.total_lines:,}",
        ]
        if mod.key_classes:
            parts.append(f"\n**Key classes:** {', '.join(mod.key_classes)}")
        if mod.key_functions:
            parts.append(f"**Key functions:** {', '.join(mod.key_functions)}")
        if mod.dependencies:
            parts.append(f"\n**Dependencies:** {', '.join(mod.dependencies)}")
        if mod.dependents:
            parts.append(f"**Dependents:** {', '.join(mod.dependents)}")

        # Related relationships
        rels = [r for r in self.relationships
                if r.source == mod.name or r.target == mod.name]
        if rels:
            parts.append("\n**Relationships:**")
            for r in rels:
                direction = '→' if r.source == mod.name else '←'
                other = r.target if r.source == mod.name else r.source
                parts.append(f"  {direction} {other} ({r.type})")

        return '\n'.join(parts)


# ── Atlas Agent ──────────────────────────────────────────

class Atlas:
    """
    The Big Picture Agent.
    
    Maintains a living knowledge graph of the AIM-OS project.
    Pre-builds context packages for any query domain.
    
    Usage:
        atlas = Atlas(workspace_root='/path/to/AIM-OS')
        atlas.index()  # Build initial knowledge graph
        
        # Get big picture
        summary = atlas.get_summary()
        
        # Get context for a specific area
        context = atlas.get_context_for('swarm orchestrator')
        
        # Pre-build a context package for a task
        pack = atlas.build_context_package(
            task='Audit the CMC memory system',
        )
    """

    # The key modules in AIM-OS that Atlas tracks
    MODULE_DEFINITIONS = {
        'ai_engine': {
            'path': 'scripts/ai_engine',
            'description': 'Core AI Engine — 7-layer pipeline: Context→Agent→Genome→VIF→LLM→Trace→Learn',
            'purpose': 'Orchestrates all AI operations via unified pipeline',
            'tags': ['core', 'pipeline', 'orchestration'],
        },
        'swarm': {
            'path': 'scripts/ai_engine/swarm',
            'description': 'Gemini CLI worker swarm — orchestrator, workers, contracts',
            'purpose': 'Multi-agent parallel execution with capability tokens',
            'tags': ['agents', 'parallel', 'workers'],
        },
        'context': {
            'path': 'scripts/ai_engine/context',
            'description': 'Context Pack pipeline — Evidence→Retrieval→Budgeting→Pack',
            'purpose': 'Assembles optimal context windows for LLM calls',
            'tags': ['context', 'retrieval', 'budgeting'],
        },
        'agent_loop': {
            'path': 'scripts/ai_engine/agent_loop',
            'description': 'Agent loop infrastructure — strategies, evolution, quality scoring',
            'purpose': 'Manage agent execution cycles and quality assurance',
            'tags': ['evolution', 'quality', 'strategies'],
        },
        'providers': {
            'path': 'scripts/ai_engine/providers',
            'description': 'LLM providers — GeminiCLIProvider (headless/streaming/vision)',
            'purpose': 'Interface with Gemini CLI for agent execution',
            'tags': ['llm', 'gemini', 'providers'],
        },
        'safety': {
            'path': 'scripts/ai_engine/safety',
            'description': 'Safety systems — VIF gates, capability enforcement',
            'purpose': 'Enforce safety constraints on agent operations',
            'tags': ['safety', 'vif', 'capability'],
        },
        'learning': {
            'path': 'scripts/ai_engine/learning',
            'description': 'Learning system — outcome tracking, model preferences',
            'purpose': 'Track execution outcomes and improve over time',
            'tags': ['learning', 'feedback', 'metrics'],
        },
        'genomes': {
            'path': '.agent/genomes',
            'description': 'Agent genome files — identity, role, and task overlays',
            'purpose': 'Define agent personalities, capabilities, and constraints',
            'tags': ['genome', 'identity', 'configuration'],
        },
        'joc': {
            'path': 'packages/joc',
            'description': 'JOC Dashboard — React UI for AIM-OS monitoring and control',
            'purpose': 'Visual interface for managing agents, context lab, and system health',
            'tags': ['ui', 'dashboard', 'react'],
        },
        'lucid_mcp': {
            'path': 'packages/lucid-mcp-server',
            'description': 'Lucid MCP Server — 92 tools for IDE integration',
            'purpose': 'Bridge between AIM-OS intelligence and IDE environments',
            'tags': ['mcp', 'tools', 'ide'],
        },
        'daemon_rag': {
            'path': 'packages/daemon-rag',
            'description': 'DaemonRAG — context parsing, task classification, intent inference',
            'purpose': 'Parse user input for context clues and classify task types',
            'tags': ['rag', 'context', 'classification'],
        },
    }

    # Known architectural decisions
    KNOWN_DECISIONS = [
        {
            'title': 'Ephemeral Workers',
            'description': 'Workers are stateless subprocesses with strict TTL. They get a JobPacket, return a ResultPacket. Always.',
            'by': 'Sev',
        },
        {
            'title': 'Capability Tokens',
            'description': 'Permission enforcement at the MCP layer, not just in prompts. RED ZONE capabilities require human approval.',
            'by': 'Sev',
        },
        {
            'title': 'Layered Genomes',
            'description': 'Agent identity = base genome + role overlay + task overlay. Genome files in .agent/genomes/.',
            'by': 'Team',
        },
        {
            'title': 'Context Pack Pipeline',
            'description': 'Evidence→Retrieval→Budgeting→Pack. All context goes through this pipeline.',
            'by': 'Sev',
        },
        {
            'title': 'MCP as System Interface',
            'description': 'AIM-OS systems are exposed as MCP tools. IDEs emulate AIM-OS via MCP. Agents get the real systems.',
            'by': 'Braden',
        },
    ]

    # Known patterns
    KNOWN_PATTERNS = [
        {
            'name': 'Lazy Component Loading',
            'description': 'Use @property with None-check for lazy initialization to avoid import cycles and reduce startup cost.',
        },
        {
            'name': 'Dataclass Contracts',
            'description': 'All inter-component data uses @dataclass with to_dict(). Immutable once created.',
        },
        {
            'name': 'Fallback Chains',
            'description': 'Every external dependency has a graceful fallback (e.g., DaemonRAG → heuristic, MCP → direct call).',
        },
        {
            'name': 'Logging Convention',
            'description': 'logger = logging.getLogger("ai_engine.{module}"). Prefix log messages with [ClassName].',
        },
    ]

    # Known gotchas
    KNOWN_GOTCHAS = [
        '`run_headless()` blocks MCP servers to avoid 400 errors — use it for swarm workers, not for interactive agents.',
        'Gemini CLI has ~20s cold start — plan for latency in parallel spawning.',
        'Windows subprocess needs encoding="utf-8" or you get garbled output.',
        'ContextPackBuilder tries DaemonRAG first; if not installed, falls back to keyword extraction.',
        'Quality scorer in quality.py is `score_context_pack()` (function), not a class.',
    ]

    def __init__(self, workspace_root: str = ''):
        self.workspace_root = workspace_root or WORKSPACE
        self.map = ArchitectureMap(workspace_root=self.workspace_root)
        self._store_path = os.path.join(
            self.workspace_root, '.agent', 'atlas_store.json'
        )
        self._indexed = False

    def index(self, force: bool = False) -> Dict[str, Any]:
        """
        Build the complete project knowledge graph.
        
        Scans modules, counts files/lines, extracts classes/functions,
        detects imports for relationships.
        
        Returns:
            Stats dict with module count, file count, relationship count
        """
        if self._indexed and not force:
            return {'status': 'already_indexed', 'modules': len(self.map.modules)}

        start = time.monotonic()
        logger.info('[Atlas] Indexing workspace...')

        total_files = 0
        total_lines = 0

        # Index each module
        for mod_name, mod_def in self.MODULE_DEFINITIONS.items():
            mod_path = os.path.join(self.workspace_root, mod_def['path'])
            if not os.path.exists(mod_path):
                logger.debug(f'[Atlas] Module path not found: {mod_path}')
                continue

            mod_info = ModuleInfo(
                name=mod_name,
                path=mod_def['path'],
                description=mod_def.get('description', ''),
                purpose=mod_def.get('purpose', ''),
                tags=mod_def.get('tags', []),
            )

            # Scan files
            if os.path.isdir(mod_path):
                mod_info = self._scan_directory(mod_info, mod_path)
            elif os.path.isfile(mod_path):
                mod_info.files = [mod_def['path']]
                mod_info.file_count = 1

            total_files += mod_info.file_count
            total_lines += mod_info.total_lines

            self.map.modules[mod_name] = mod_info

        # Detect relationships via import analysis
        self._detect_relationships()

        # Add known decisions, patterns, gotchas
        self.map.decisions = self.KNOWN_DECISIONS
        self.map.patterns = self.KNOWN_PATTERNS
        self.map.gotchas = self.KNOWN_GOTCHAS

        self.map.total_files = total_files
        self.map.total_lines = total_lines
        self.map.last_indexed = time.time()
        self._indexed = True

        elapsed = (time.monotonic() - start) * 1000

        # Persist to disk
        self._save()

        stats = {
            'status': 'indexed',
            'modules': len(self.map.modules),
            'files': total_files,
            'lines': total_lines,
            'relationships': len(self.map.relationships),
            'decisions': len(self.map.decisions),
            'patterns': len(self.map.patterns),
            'gotchas': len(self.map.gotchas),
            'elapsed_ms': elapsed,
        }

        logger.info(
            f'[Atlas] Indexed: {stats["modules"]} modules, '
            f'{stats["files"]} files, {stats["lines"]:,} lines, '
            f'{stats["relationships"]} relationships ({elapsed:.0f}ms)'
        )

        return stats

    def _scan_directory(self, mod: ModuleInfo, dir_path: str) -> ModuleInfo:
        """Scan a directory for code files, extracting classes and functions."""
        code_extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.md'}
        ignore_dirs = {'node_modules', '.next', '__pycache__', '.git', 'dist', 'build'}

        for root, dirs, files in os.walk(dir_path):
            # Filter ignore dirs
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext not in code_extensions:
                    continue

                fpath = os.path.join(root, f)
                rel_path = os.path.relpath(fpath, self.workspace_root)
                mod.files.append(rel_path)

                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()

                    lines = content.count('\n') + 1
                    mod.total_lines += lines

                    # Extract classes and functions (Python)
                    if ext == '.py':
                        for match in re.finditer(r'^class\s+(\w+)', content, re.MULTILINE):
                            cls_name = match.group(1)
                            if cls_name not in mod.key_classes:
                                mod.key_classes.append(cls_name)
                        for match in re.finditer(r'^def\s+(\w+)', content, re.MULTILINE):
                            fn_name = match.group(1)
                            if not fn_name.startswith('_') and fn_name not in mod.key_functions:
                                mod.key_functions.append(fn_name)

                    # Extract classes and functions (TypeScript/JS)
                    elif ext in {'.ts', '.tsx', '.js', '.jsx'}:
                        for match in re.finditer(r'(?:export\s+)?class\s+(\w+)', content):
                            cls_name = match.group(1)
                            if cls_name not in mod.key_classes:
                                mod.key_classes.append(cls_name)
                        for match in re.finditer(
                            r'(?:export\s+)?(?:function|const)\s+(\w+)',
                            content
                        ):
                            fn_name = match.group(1)
                            if fn_name not in mod.key_functions and len(fn_name) > 2:
                                mod.key_functions.append(fn_name)

                except Exception:
                    pass

        mod.file_count = len(mod.files)
        # Limit lists for readability
        mod.key_classes = mod.key_classes[:20]
        mod.key_functions = mod.key_functions[:20]
        return mod

    def _detect_relationships(self):
        """Detect import-based relationships between modules."""
        relationships = []
        module_names = set(self.map.modules.keys())

        for mod_name, mod in self.map.modules.items():
            for f in mod.files:
                fpath = os.path.join(self.workspace_root, f)
                if not f.endswith('.py'):
                    continue
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()

                    # Detect Python imports pointing to other modules
                    for other_name, other_mod in self.map.modules.items():
                        if other_name == mod_name:
                            continue
                        # Check if this file imports from the other module's path
                        other_import = other_mod.path.replace('/', '.').replace('\\', '.')
                        if other_import in content or other_name in content:
                            rel = Relationship(
                                source=mod_name,
                                target=other_name,
                                type='imports',
                                strength=0.5,
                                evidence=f,
                            )
                            relationships.append(rel)
                            # Track in module info
                            if other_name not in mod.dependencies:
                                mod.dependencies.append(other_name)
                            if mod_name not in other_mod.dependents:
                                other_mod.dependents.append(mod_name)

                except Exception:
                    pass

        # Deduplicate
        seen = set()
        unique = []
        for r in relationships:
            key = f"{r.source}->{r.target}:{r.type}"
            if key not in seen:
                seen.add(key)
                unique.append(r)

        self.map.relationships = unique

    # ── Query API ─────────────────────────────────────────

    def get_summary(self) -> str:
        """Get the full architecture summary."""
        if not self._indexed:
            self.index()
        return self.map.to_summary()

    def get_context_for(self, query: str) -> str:
        """
        Get focused context for a query topic.
        
        Searches module names, descriptions, classes, and functions
        to find the most relevant modules, then returns their context.
        """
        if not self._indexed:
            self.index()

        query_lower = query.lower()
        scored: List[tuple] = []

        for name, mod in self.map.modules.items():
            score = 0.0
            # Module name match
            if query_lower in name.lower():
                score += 3.0
            # Description match
            if query_lower in mod.description.lower():
                score += 2.0
            # Purpose match
            if query_lower in mod.purpose.lower():
                score += 2.0
            # Tag match
            for tag in mod.tags:
                if query_lower in tag.lower():
                    score += 1.5
            # Class/function match
            for cls in mod.key_classes:
                if query_lower in cls.lower():
                    score += 1.0
            for fn in mod.key_functions:
                if query_lower in fn.lower():
                    score += 0.5

            if score > 0:
                scored.append((name, score))

        if not scored:
            return f"No modules found matching '{query}'. Available: {', '.join(self.map.modules.keys())}"

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:3]

        parts = [f"# Context for: {query}\n"]
        for name, score in top:
            parts.append(self.map.get_module_context(name))
            parts.append("")

        # Add related decisions
        related_decisions = [
            d for d in self.map.decisions
            if query_lower in d.get('title', '').lower()
            or query_lower in d.get('description', '').lower()
        ]
        if related_decisions:
            parts.append("## Related Decisions")
            for d in related_decisions:
                parts.append(f"- **{d['title']}**: {d['description']}")

        # Add related gotchas
        related_gotchas = [
            g for g in self.map.gotchas
            if query_lower in g.lower()
        ]
        if related_gotchas:
            parts.append("\n## Gotchas")
            for g in related_gotchas:
                parts.append(f"- {g}")

        return '\n'.join(parts)

    def build_context_package(
        self,
        task: str,
        include_summary: bool = True,
        max_modules: int = 3,
    ) -> str:
        """
        Pre-build a context package for a task.
        
        This is what gets injected into an EnhancedWorker's
        prompt BEFORE the task description.
        
        Args:
            task: The task description to build context for
            include_summary: Whether to include full architecture overview
            max_modules: Max relevant modules to include
        
        Returns:
            Markdown-formatted context package
        """
        if not self._indexed:
            self.index()

        parts = []

        # Architecture overview (condensed)
        if include_summary:
            parts.append(
                "## Project Overview\n"
                f"AIM-OS: {len(self.map.modules)} modules, "
                f"{self.map.total_files} files, "
                f"{self.map.total_lines:,} lines\n"
            )
            # Module directory
            parts.append("### Module Directory")
            for name, mod in sorted(self.map.modules.items()):
                parts.append(
                    f"- **{name}** (`{mod.path}`) — {mod.purpose}"
                )
            parts.append("")

        # Task-relevant context
        relevant = self.get_context_for(task)
        parts.append(relevant)

        # Relevant patterns
        task_lower = task.lower()
        relevant_patterns = [
            p for p in self.map.patterns
            if any(word in p.get('description', '').lower()
                   for word in task_lower.split()[:5])
        ]
        if relevant_patterns:
            parts.append("\n## Relevant Patterns")
            for p in relevant_patterns:
                parts.append(f"- **{p['name']}**: {p['description']}")

        return '\n'.join(parts)

    # ── Persistence ───────────────────────────────────────

    def _save(self):
        """Save the atlas store to disk."""
        try:
            os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
            data = {
                'last_indexed': self.map.last_indexed,
                'total_files': self.map.total_files,
                'total_lines': self.map.total_lines,
                'modules': {
                    name: {
                        'path': mod.path,
                        'description': mod.description,
                        'purpose': mod.purpose,
                        'file_count': mod.file_count,
                        'total_lines': mod.total_lines,
                        'key_classes': mod.key_classes[:10],
                        'key_functions': mod.key_functions[:10],
                        'dependencies': mod.dependencies,
                        'dependents': mod.dependents,
                        'tags': mod.tags,
                    }
                    for name, mod in self.map.modules.items()
                },
                'relationships': [
                    {
                        'source': r.source,
                        'target': r.target,
                        'type': r.type,
                    }
                    for r in self.map.relationships
                ],
            }
            with open(self._store_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f'[Atlas] Saved to {self._store_path}')
        except Exception as e:
            logger.warning(f'[Atlas] Save failed: {e}')

    def load(self) -> bool:
        """Load atlas store from disk if available."""
        try:
            if os.path.exists(self._store_path):
                with open(self._store_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.map.last_indexed = data.get('last_indexed', 0)
                self.map.total_files = data.get('total_files', 0)
                self.map.total_lines = data.get('total_lines', 0)
                for name, mdata in data.get('modules', {}).items():
                    self.map.modules[name] = ModuleInfo(
                        name=name,
                        **{k: v for k, v in mdata.items() if k != 'name'}
                    )
                self.map.relationships = [
                    Relationship(**r) for r in data.get('relationships', [])
                ]
                self.map.decisions = self.KNOWN_DECISIONS
                self.map.patterns = self.KNOWN_PATTERNS
                self.map.gotchas = self.KNOWN_GOTCHAS
                self._indexed = True
                logger.info(
                    f'[Atlas] Loaded from disk: {len(self.map.modules)} modules'
                )
                return True
        except Exception as e:
            logger.warning(f'[Atlas] Load failed: {e}')
        return False

    def status(self) -> dict:
        return {
            'indexed': self._indexed,
            'modules': len(self.map.modules),
            'files': self.map.total_files,
            'lines': self.map.total_lines,
            'relationships': len(self.map.relationships),
            'decisions': len(self.map.decisions),
            'patterns': len(self.map.patterns),
            'gotchas': len(self.map.gotchas),
            'last_indexed': self.map.last_indexed,
            'store_path': self._store_path,
        }


# ── CLI Test ──────────────────────────────────────────────

def _test():
    """Full Atlas integration test."""
    import textwrap

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  AIM-OS Atlas — Big Picture Agent Test                  ║")
    print("╚══════════════════════════════════════════════════════════╝")

    atlas = Atlas(workspace_root=WORKSPACE)

    # Test 1: Index
    print("\n" + "=" * 60)
    print("TEST 1: Index Workspace")
    print("=" * 60)
    stats = atlas.index(force=True)
    for k, v in stats.items():
        print(f'  {k}: {v}')

    # Test 2: Architecture Summary
    print("\n" + "=" * 60)
    print("TEST 2: Architecture Summary")
    print("=" * 60)
    summary = atlas.get_summary()
    # Print first 60 lines
    for line in summary.split('\n')[:60]:
        print(f'  {line}')
    print('  ...(truncated)')

    # Test 3: Context Query
    print("\n" + "=" * 60)
    print("TEST 3: Context Query — 'swarm'")
    print("=" * 60)
    context = atlas.get_context_for('swarm')
    for line in context.split('\n')[:30]:
        print(f'  {line}')

    # Test 4: Context Package
    print("\n" + "=" * 60)
    print("TEST 4: Pre-built Context Package")
    print("=" * 60)
    package = atlas.build_context_package(
        task='Audit the CMC memory system and context engine',
    )
    print(f'  Package size: {len(package)} chars (~{len(package)//4} tokens)')
    for line in package.split('\n')[:20]:
        print(f'  {line}')
    print('  ...(truncated)')

    # Test 5: Persistence
    print("\n" + "=" * 60)
    print("TEST 5: Persistence (save + load)")
    print("=" * 60)
    atlas2 = Atlas(workspace_root=WORKSPACE)
    loaded = atlas2.load()
    print(f'  Loaded from disk: {loaded}')
    if loaded:
        print(f'  Modules: {len(atlas2.map.modules)}')
        print(f'  Relationships: {len(atlas2.map.relationships)}')

    # Summary
    print("\n" + "=" * 60)
    print("ATLAS STATUS")
    print("=" * 60)
    status = atlas.status()
    for k, v in status.items():
        print(f'  {k}: {v}')

    return atlas


if __name__ == '__main__':
    _test()
