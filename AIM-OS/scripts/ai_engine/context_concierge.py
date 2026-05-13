"""
AIM-OS AI Engine — Context Concierge

Universal context discovery service. Any agent from anywhere can call
this with a natural language query and receive structured context
without knowing file paths.

Pipeline:
    1. Query → Atlas module search (scored matching)
    2. Top modules → File discovery (key files per module)
    3. Files → ContextMapper envelope building (parallel, cached)
    4. Envelopes → Budget packing (relevance-ranked merge)
    5. Response → Structured JSON with contracts, summaries, paths

Usage via MCP:
    ai_engine_context_find(query="genome loading", budget=32000)
    → Returns: modules, file envelopes, contracts, key classes

Usage direct:
    concierge = ContextConcierge('/path/to/AIM-OS')
    result = concierge.find("genome loading")
    print(result.to_string())
"""

import os
import re
import sys
import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

logger = logging.getLogger('ai_engine.context_concierge')

# Ensure imports work from various entry points
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))


# ══════════════════════════════════════════════════════════
#  DATA MODELS
# ══════════════════════════════════════════════════════════

@dataclass
class DiscoveredFile:
    """A file discovered as relevant to the query."""
    path: str
    relevance: float = 0.0
    module: str = ''
    reason: str = ''
    export_count: int = 0
    import_count: int = 0


@dataclass
class ConciergeResult:
    """Result from the Context Concierge."""
    query: str
    intent: str = 'code'  # code, docs, mixed
    modules_found: List[str] = field(default_factory=list)
    files_discovered: List[DiscoveredFile] = field(default_factory=list)
    envelopes: Dict[str, str] = field(default_factory=dict)  # path -> envelope string
    contracts_summary: Dict[str, List[str]] = field(default_factory=dict)  # path -> export names
    total_chars: int = 0
    budget_chars: int = 32000
    generation_ms: float = 0.0
    atlas_context: str = ''

    def to_string(self) -> str:
        """Render as structured text for LLM injection."""
        parts = [
            f"<context_discovery query=\"{self.query}\">",
            f"<intent>{self.intent}</intent>",
            f"<modules_matched>{', '.join(self.modules_found)}</modules_matched>",
            f"<files_discovered>{len(self.files_discovered)}</files_discovered>",
            f"<generation_ms>{self.generation_ms:.0f}</generation_ms>",
        ]

        # Atlas high-level context
        if self.atlas_context:
            parts.append(f"\n<atlas_context>")
            # Truncate atlas context to reasonable size
            atlas_trimmed = self.atlas_context[:4000]
            parts.append(atlas_trimmed)
            parts.append(f"</atlas_context>")

        # File-level structural envelopes
        for df in self.files_discovered:
            basename = os.path.basename(df.path)
            parts.append(f"\n<file name=\"{basename}\" relevance=\"{df.relevance:.1f}\" module=\"{df.module}\">")
            if df.path in self.contracts_summary:
                exports = self.contracts_summary[df.path]
                parts.append(f"  <exports>{', '.join(exports[:20])}</exports>")
            if df.path in self.envelopes:
                parts.append(self.envelopes[df.path])
            parts.append(f"</file>")

        parts.append("</context_discovery>")
        return '\n'.join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for MCP JSON response."""
        return {
            "query": self.query,
            "intent": self.intent,
            "modules_found": self.modules_found,
            "files_discovered": [
                {
                    "path": os.path.basename(f.path),
                    "full_path": f.path,
                    "relevance": f.relevance,
                    "module": f.module,
                    "reason": f.reason,
                    "exports": len(self.contracts_summary.get(f.path, [])),
                }
                for f in self.files_discovered
            ],
            "contracts": {
                os.path.basename(k): v[:15]
                for k, v in self.contracts_summary.items()
            },
            "total_chars": self.total_chars,
            "budget_chars": self.budget_chars,
            "generation_ms": round(self.generation_ms, 1),
        }


# ══════════════════════════════════════════════════════════
#  INTENT CLASSIFIER
# ══════════════════════════════════════════════════════════

# Keywords that signal code vs documentation intent
CODE_SIGNALS = {
    'function', 'class', 'method', 'import', 'module', 'file',
    'implement', 'code', 'refactor', 'debug', 'fix', 'api',
    'interface', 'type', 'return', 'parameter', 'call', 'invoke',
    'engine', 'builder', 'resolver', 'handler', 'provider',
    'extract', 'parse', 'create', 'build', 'generate',
}

DOC_SIGNALS = {
    'documentation', 'readme', 'guide', 'tutorial', 'explain',
    'description', 'overview', 'architecture', 'design', 'decision',
    'protocol', 'workflow', 'canon', 'spec', 'specification',
    'research', 'thesis', 'analysis', 'report',
}


def classify_intent(query: str) -> str:
    """Classify query intent: code, docs, or mixed."""
    words = set(re.findall(r'\w+', query.lower()))
    code_score = len(words & CODE_SIGNALS)
    doc_score = len(words & DOC_SIGNALS)

    if code_score > doc_score:
        return 'code'
    elif doc_score > code_score:
        return 'docs'
    return 'mixed'


# ══════════════════════════════════════════════════════════
#  CONTEXT CONCIERGE
# ══════════════════════════════════════════════════════════

class ContextConcierge:
    """
    Universal context discovery service.

    Chains Atlas (module discovery) with ContextMapper (structural extraction)
    to provide any agent with rich, structured context from a natural language query.
    """

    def __init__(self, workspace_root: str = ''):
        self.workspace_root = workspace_root or WORKSPACE
        self._atlas = None
        self._mapper = None
        logger.info(f'ContextConcierge initialized (workspace: {self.workspace_root})')

    # ── Lazy Loading ────────────────────────────────────────

    def _get_atlas(self):
        """Lazy-load Atlas agent."""
        if self._atlas is None:
            try:
                from atlas_agent import Atlas
            except ImportError:
                try:
                    from ai_engine.atlas_agent import Atlas
                except ImportError:
                    from scripts.ai_engine.atlas_agent import Atlas
            self._atlas = Atlas(self.workspace_root)
            # Load cached index or build fresh
            self._atlas.load()
            if not self._atlas._indexed:
                logger.info('Atlas indexing workspace...')
                self._atlas.index()
        return self._atlas

    def _get_mapper(self):
        """Lazy-load ContextMapper."""
        if self._mapper is None:
            try:
                from context_mapper import ContextMapper
            except ImportError:
                try:
                    from ai_engine.context_mapper import ContextMapper
                except ImportError:
                    from scripts.ai_engine.context_mapper import ContextMapper
            self._mapper = ContextMapper(self.workspace_root)
        return self._mapper

    # ── Main Discovery Pipeline ─────────────────────────────

    def find(
        self,
        query: str,
        budget_chars: int = 32000,
        max_files: int = 5,
        include_envelopes: bool = True,
    ) -> ConciergeResult:
        """
        Discover and build context for a natural language query.

        Pipeline:
            1. Classify intent (code vs docs vs mixed)
            2. Atlas module search (scored matching)
            3. File discovery (key files per module)
            4. ContextMapper envelope building (cached)
            5. Budget packing (relevance-ranked)

        Args:
            query: Natural language description of what context is needed
            budget_chars: Maximum total context size (~4 chars/token)
            max_files: Maximum files to include
            include_envelopes: Whether to build full structural envelopes

        Returns:
            ConciergeResult with modules, files, contracts, and optional envelopes
        """
        t0 = time.time()
        result = ConciergeResult(query=query, budget_chars=budget_chars)

        # Step 1: Classify intent
        result.intent = classify_intent(query)
        logger.info(f'Query: "{query}" → intent={result.intent}')

        # Step 2: Atlas module search
        atlas = self._get_atlas()
        atlas_context = atlas.get_context_for(query)
        result.atlas_context = atlas_context

        # Extract module names from Atlas results
        modules_found = self._extract_modules_from_atlas(query, atlas)
        result.modules_found = [m for m, _ in modules_found[:5]]

        # Step 3: File discovery
        discovered = self._discover_files(modules_found, query, max_files)
        result.files_discovered = discovered

        # Step 4: Build envelopes (if requested and budget allows)
        if include_envelopes and discovered:
            mapper = self._get_mapper()
            per_file_budget = budget_chars // min(len(discovered), max_files)

            chars_used = 0
            for df in discovered:
                if chars_used >= budget_chars:
                    break

                try:
                    # Extract contracts (fast, always do this)
                    extraction = mapper.extract_contracts(df.path)
                    df.export_count = len(extraction.exports)
                    df.import_count = len(extraction.imports)
                    result.contracts_summary[df.path] = [
                        exp.name for exp in extraction.exports
                    ]

                    if include_envelopes:
                        # Build envelope (heavier, structural context)
                        remaining = budget_chars - chars_used
                        file_budget = min(per_file_budget, remaining)
                        if file_budget > 2000:  # Min useful envelope
                            envelope = mapper.build_envelope(
                                df.path,
                                budget_chars=file_budget,
                            )
                            env_str = envelope.to_string()
                            result.envelopes[df.path] = env_str
                            chars_used += len(env_str)

                except Exception as e:
                    logger.warning(f'Failed to process {df.path}: {e}')
                    continue

            result.total_chars = chars_used

        result.generation_ms = (time.time() - t0) * 1000
        logger.info(
            f'Concierge: {len(result.modules_found)} modules, '
            f'{len(result.files_discovered)} files, '
            f'{result.total_chars} chars in {result.generation_ms:.0f}ms'
        )
        return result

    # ── Helper Methods ──────────────────────────────────────

    def _extract_modules_from_atlas(
        self, query: str, atlas
    ) -> List[tuple]:
        """Score and rank modules from Atlas for the query."""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        scored = []

        for name, mod in atlas.map.modules.items():
            score = 0.0

            # Module name match (strongest signal)
            name_lower = name.lower()
            for word in query_words:
                if word in name_lower:
                    score += 3.0

            # Description/purpose match
            desc_lower = (mod.description + ' ' + mod.purpose).lower()
            for word in query_words:
                if word in desc_lower:
                    score += 2.0

            # Tag match
            for tag in mod.tags:
                for word in query_words:
                    if word in tag.lower():
                        score += 1.5

            # Class/function name match
            for cls in mod.key_classes:
                for word in query_words:
                    if word in cls.lower():
                        score += 1.0
            for fn in mod.key_functions:
                for word in query_words:
                    if word in fn.lower():
                        score += 0.5

            if score > 0:
                scored.append((name, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _discover_files(
        self,
        modules: List[tuple],
        query: str,
        max_files: int,
    ) -> List[DiscoveredFile]:
        """Discover key files from matched modules."""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        files = []
        seen_paths = set()
        atlas = self._get_atlas()

        CODE_EXTS = {'.py', '.ts', '.tsx', '.js', '.jsx'}

        for mod_name, mod_score in modules[:5]:
            if mod_name not in atlas.map.modules:
                continue
            mod = atlas.map.modules[mod_name]

            # Get file list — from Atlas or fallback to filesystem scan
            file_list = mod.files
            if not file_list and mod.path:
                # Atlas cache might have empty files — scan module dir
                mod_dir = os.path.join(self.workspace_root, mod.path)
                if os.path.isdir(mod_dir):
                    file_list = []
                    ignore = {'node_modules', '__pycache__', '.next', 'dist', 'build', '.git'}
                    for root, dirs, fnames in os.walk(mod_dir):
                        dirs[:] = [d for d in dirs if d not in ignore]
                        for fname in fnames:
                            ext = os.path.splitext(fname)[1].lower()
                            if ext in CODE_EXTS:
                                rel = os.path.relpath(os.path.join(root, fname), self.workspace_root)
                                file_list.append(rel)

            for rel_path in file_list:
                # Resolve to absolute path
                abs_path = os.path.normpath(os.path.join(self.workspace_root, rel_path))
                if abs_path in seen_paths:
                    continue
                if not os.path.isfile(abs_path):
                    continue
                seen_paths.add(abs_path)

                basename = os.path.basename(abs_path).lower()
                ext = os.path.splitext(basename)[1]

                # Only code files
                if ext not in CODE_EXTS:
                    continue

                # Skip test files unless query is about testing
                if basename.startswith('test_') and 'test' not in query_lower:
                    continue

                # Skip __init__.py (usually just imports)
                if basename == '__init__.py':
                    continue

                # Score this file
                file_score = mod_score

                # Boost if filename matches query words
                for word in query_words:
                    if word in basename:
                        file_score += 5.0

                # Boost if key classes/functions match query
                for cls in mod.key_classes:
                    if any(w in cls.lower() for w in query_words):
                        file_score += 1.0
                        break

                reason = f"Module '{mod_name}' matched query"
                if any(w in basename for w in query_words):
                    reason = f"Filename matches query term"

                files.append(DiscoveredFile(
                    path=abs_path,
                    relevance=file_score,
                    module=mod_name,
                    reason=reason,
                ))

        # Sort by relevance, limit
        files.sort(key=lambda f: f.relevance, reverse=True)
        return files[:max_files]

    # ── Quick Query (No Envelopes) ──────────────────────────

    def quick_find(self, query: str, max_files: int = 10) -> ConciergeResult:
        """
        Fast lightweight discovery — modules, files, contracts only.
        No envelope building (much faster).
        """
        return self.find(
            query=query,
            budget_chars=32000,
            max_files=max_files,
            include_envelopes=False,
        )

    # ── Status ──────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Get concierge system status."""
        return {
            "workspace": self.workspace_root,
            "atlas_loaded": self._atlas is not None,
            "atlas_indexed": self._atlas._indexed if self._atlas else False,
            "atlas_modules": len(self._atlas.map.modules) if self._atlas else 0,
            "mapper_loaded": self._mapper is not None,
            "mapper_cache_size": (
                self._mapper._cache.size()
                if self._mapper and hasattr(self._mapper, '_cache')
                else 0
            ),
        }


# ══════════════════════════════════════════════════════════
#  CLI TEST
# ══════════════════════════════════════════════════════════

def _test():
    """Interactive test of the Context Concierge."""
    import json

    print("=" * 60)
    print("  Context Concierge — Live Test")
    print("=" * 60)

    concierge = ContextConcierge(WORKSPACE)

    # Test queries
    queries = [
        "genome loading and agent configuration",
        "context engine and token management",
        "MCP server tools and protocol",
    ]

    for query in queries:
        print(f"\n{'─' * 60}")
        print(f"  Query: \"{query}\"")
        print(f"{'─' * 60}")

        result = concierge.find(query, budget_chars=16000, max_files=3)

        print(f"  Intent: {result.intent}")
        print(f"  Modules: {result.modules_found}")
        print(f"  Files: {len(result.files_discovered)}")
        for f in result.files_discovered:
            print(f"    [{f.relevance:.1f}] {os.path.basename(f.path)} ({f.module}) — {f.reason}")
        print(f"  Contracts:")
        for path, exports in result.contracts_summary.items():
            print(f"    {os.path.basename(path)}: {exports[:5]}")
        print(f"  Envelopes: {len(result.envelopes)}")
        for path, env in result.envelopes.items():
            print(f"    {os.path.basename(path)}: {len(env)} chars")
        print(f"  Total: {result.total_chars} chars, {result.generation_ms:.0f}ms")

    # Status
    print(f"\n{'─' * 60}")
    print(f"  Status:")
    print(json.dumps(concierge.status(), indent=2))


if __name__ == '__main__':
    _test()
