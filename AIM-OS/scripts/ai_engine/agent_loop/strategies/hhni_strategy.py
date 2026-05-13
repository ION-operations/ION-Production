"""
Strategy: HHNI Direct (Semantic Retrieval)

Uses HHNI (Hierarchical Holographic Network Index) for semantic
retrieval and CMC (Cognitive Memory Core) atoms for context.

This is a lightweight, fast strategy that leverages AIM-OS's
semantic search infrastructure directly without LLM overhead.
"""

import time
import json
import logging
from typing import Optional, List

from . import ContextStrategy, register_strategy

import os
import sys

_AGENT_LOOP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AI_ENGINE_DIR = os.path.dirname(_AGENT_LOOP_DIR)
_SCRIPTS_DIR = os.path.dirname(_AI_ENGINE_DIR)
_AIMOS_ROOT = os.path.dirname(_SCRIPTS_DIR)

for p in [_AIMOS_ROOT, _AI_ENGINE_DIR, _AGENT_LOOP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from ..models import ContextPack, Handoff
except ImportError:
    from models import ContextPack, Handoff

logger = logging.getLogger('ai_engine.agent_loop.strategies.hhni')


@register_strategy
class HHNIStrategy(ContextStrategy):
    """HHNI semantic retrieval + CMC atom-based context strategy.

    Fast, deterministic context building using AIM-OS's semantic
    index. No LLM overhead for context research — just retrieval + ranking.
    """

    name = 'hhni_direct'
    description = 'HHNI semantic retrieval + CMC atoms (fast, no LLM overhead)'

    def __init__(self, workspace_root: str = '', **kwargs):
        super().__init__(workspace_root, **kwargs)
        self._hhni_index_path = kwargs.get(
            'hhni_index_path',
            os.path.join(_AIMOS_ROOT, 'mcp_memory', 'index', 'tags', 'hhni_index.json'),
        )
        self._cmc_db_path = kwargs.get(
            'cmc_db_path',
            os.path.join(_AIMOS_ROOT, 'mcp_memory', 'cmc_store.db'),
        )
        self._max_results = kwargs.get('max_results', 10)

    def _search_hhni(self, query: str) -> List[dict]:
        """Search HHNI index for semantically related items."""
        results = []
        try:
            if os.path.exists(self._hhni_index_path):
                with open(self._hhni_index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)

                # Simple keyword matching against HHNI tags
                # (In production, this would use proper semantic similarity)
                query_terms = set(query.lower().split())

                for entry in index if isinstance(index, list) else index.get('entries', []):
                    if isinstance(entry, dict):
                        tags = entry.get('tags', [])
                        content = entry.get('content', '')
                        source = entry.get('source', entry.get('id', 'unknown'))

                        # Score by tag overlap
                        tag_set = set(t.lower() for t in tags) if tags else set()
                        content_terms = set(content.lower().split()[:50])
                        overlap = len(query_terms & (tag_set | content_terms))

                        if overlap > 0:
                            results.append({
                                'source': source,
                                'content': content[:2000],
                                'tags': tags,
                                'score': overlap / max(len(query_terms), 1),
                            })

                # Sort by score
                results.sort(key=lambda x: x['score'], reverse=True)
                results = results[:self._max_results]
                logger.info(f'[HHNI] Found {len(results)} results for query')

        except Exception as e:
            logger.debug(f'HHNI search failed: {e}')

        return results

    def _search_cmc(self, query: str) -> List[dict]:
        """Search CMC atoms for relevant memories."""
        results = []
        try:
            import sqlite3
            if os.path.exists(self._cmc_db_path):
                conn = sqlite3.connect(self._cmc_db_path)
                cursor = conn.cursor()

                # Search atoms by content (simple LIKE query)
                query_terms = query.split()[:5]
                for term in query_terms:
                    try:
                        cursor.execute(
                            "SELECT id, content, tags FROM atoms WHERE content LIKE ? LIMIT 5",
                            (f'%{term}%',),
                        )
                        for row in cursor.fetchall():
                            results.append({
                                'id': row[0],
                                'content': row[1][:2000] if row[1] else '',
                                'tags': row[2] if row[2] else '',
                                'source': 'cmc',
                            })
                    except sqlite3.OperationalError:
                        # Table might not exist or different schema
                        break

                conn.close()
                logger.info(f'[CMC] Found {len(results)} atoms')

        except Exception as e:
            logger.debug(f'CMC search failed: {e}')

        return results

    def build_context(
        self,
        task: str,
        handoff: Optional[Handoff] = None,
        **kwargs,
    ) -> ContextPack:
        """Build context using HHNI retrieval + CMC atoms."""
        start = time.time()

        # Search both systems
        hhni_results = self._search_hhni(task)
        cmc_results = self._search_cmc(task)

        # Assemble into ContextPack
        research_parts = []
        files = []

        for r in hhni_results:
            research_parts.append(f"[HHNI:{r.get('source', '?')}] {r['content'][:500]}")
            if r.get('source', '').endswith('.py') or r.get('source', '').endswith('.ts'):
                files.append(r['source'])

        for r in cmc_results:
            research_parts.append(f"[CMC:{r.get('id', '?')}] {r['content'][:500]}")

        # Build instructions from task analysis
        instructions = f"Execute: {task}"
        if handoff and handoff.next_priorities:
            instructions += f"\nPriorities: {', '.join(handoff.next_priorities)}"

        relevant_history = ''
        if handoff:
            relevant_history = handoff.to_prompt()

        elapsed = (time.time() - start) * 1000
        total_chars = sum(len(r['content']) for r in hhni_results + cmc_results)

        self._metrics = {
            'build_time_ms': elapsed,
            'hhni_results': len(hhni_results),
            'cmc_results': len(cmc_results),
            'tokens_used': int(total_chars / 3.5),
            'method': 'hhni_direct',
        }

        logger.info(
            f'[HHNIStrategy] Built context: {len(hhni_results)} HHNI + '
            f'{len(cmc_results)} CMC, {elapsed:.0f}ms'
        )

        return ContextPack(
            task_summary=task,
            relevant_history=relevant_history,
            project_state='\n\n'.join(research_parts[:5]) if research_parts else '',
            instructions=instructions,
            files_to_examine=files[:10],
            research_notes='\n'.join(research_parts) if research_parts else 'No results found in HHNI/CMC',
            tokens_used=int(total_chars / 3.5),
            build_time_ms=elapsed,
        )
