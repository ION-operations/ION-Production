"""
Strategy: Atlas (Big-Picture Architecture Context)

Leverages the Atlas agent's knowledge graph to provide architectural
context for tasks. When given a task, this strategy:

1. Loads the Atlas store (atlas_store.json) with subsystem relationships
2. Matches task keywords against subsystem nodes
3. Builds a ContextPack enriched with architecture-level context

This pairs with other strategies:
    - hhni_direct: finds semantic matches
    - pack_builder: gathers file context
    - atlas: provides the "big picture" — subsystem relationships
"""

import time
import json
import logging
import os
import sys
from typing import Optional, List, Dict, Any

from . import ContextStrategy, register_strategy

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

logger = logging.getLogger('ai_engine.agent_loop.strategies.atlas')


# ── Atlas Knowledge Graph ────────────────────────────────

# Hardcoded system map for when atlas_store.json is missing or empty.
# This provides the essential AIM-OS architecture relationships.
_BUILTIN_SYSTEMS = {
    'cmc': {
        'name': 'CMC — Cognitive Memory Core',
        'description': 'Bitemporal persistent memory. Atoms with tags, provenance, and snapshots.',
        'connects_to': ['hhni', 'seg', 'vif'],
        'keywords': ['memory', 'atom', 'store', 'persist', 'recall', 'history', 'snapshot'],
    },
    'hhni': {
        'name': 'HHNI — Hierarchical Holographic Network Index',
        'description': 'Two-stage semantic retrieval with DVNS physics. Indexes CMC atoms for fast search.',
        'connects_to': ['cmc'],
        'keywords': ['search', 'retrieval', 'index', 'semantic', 'embedding', 'query', 'find'],
    },
    'vif': {
        'name': 'VIF — Verifiable Intelligence Framework',
        'description': 'Confidence tracking with κ-gating. Blocks low-confidence destructive actions.',
        'connects_to': ['cmc', 'apoe'],
        'keywords': ['confidence', 'verify', 'trust', 'gate', 'safety', 'block', 'approve'],
    },
    'apoe': {
        'name': 'APOE — AI-Powered Orchestration Engine',
        'description': 'Goal-to-plan compilation and multi-agent DAG orchestration.',
        'connects_to': ['vif', 'seg'],
        'keywords': ['plan', 'orchestrate', 'goal', 'workflow', 'pipeline', 'dag', 'task'],
    },
    'seg': {
        'name': 'SEG — Shared Evidence Graph',
        'description': 'Knowledge synthesis and relationship mapping across evidence.',
        'connects_to': ['cmc', 'apoe'],
        'keywords': ['knowledge', 'evidence', 'graph', 'synthesize', 'relationship', 'link'],
    },
    'cas': {
        'name': 'CAS — Cognitive Analysis System',
        'description': 'Self-monitoring, failure mode detection, cognitive drift analysis.',
        'connects_to': ['vif', 'seg'],
        'keywords': ['introspect', 'monitor', 'drift', 'failure', 'cognitive', 'audit'],
    },
    'ai_engine': {
        'name': 'AI Engine — 9-Layer Facade',
        'description': 'Unified orchestrator. Composes LLM routing, context, intelligence, safety.',
        'connects_to': ['cmc', 'hhni', 'vif', 'apoe', 'seg', 'cas'],
        'keywords': ['engine', 'facade', 'execute', 'worker', 'swarm', 'agent', 'mission'],
    },
    'genome': {
        'name': 'Agent Genome System',
        'description': 'Bitemporal agent identity bundles. Delta cloning, tournament evolution.',
        'connects_to': ['ai_engine', 'cmc'],
        'keywords': ['genome', 'identity', 'role', 'agent', 'clone', 'evolve', 'tournament'],
    },
    'chain_director': {
        'name': 'ChainDirector — Manager AI',
        'description': 'Topology dispatching, dynamic specialist assignment, quality gates.',
        'connects_to': ['ai_engine', 'apoe'],
        'keywords': ['chain', 'director', 'topology', 'specialist', 'quality', 'rework'],
    },
    'mcp': {
        'name': 'MCP — Model Context Protocol Server',
        'description': '92+ tools via lucid-mcp. 14 via ai-engine MCP. stdio + SSE transport.',
        'connects_to': ['ai_engine', 'cmc', 'hhni'],
        'keywords': ['mcp', 'tool', 'protocol', 'server', 'bridge', 'sse', 'transport'],
    },
}


@register_strategy
class AtlasStrategy(ContextStrategy):
    """Architecture-level context from the Atlas knowledge graph.

    Provides subsystem relationship context for tasks. Helps agents
    understand where their work fits in the AIM-OS architecture.
    """

    name = 'atlas'
    description = 'Atlas knowledge graph — architecture-level context (fast, no LLM)'

    def __init__(self, workspace_root: str = '', **kwargs):
        super().__init__(workspace_root, **kwargs)
        self._atlas_store_path = kwargs.get(
            'atlas_store_path',
            os.path.join(_AIMOS_ROOT, '.agent', 'atlas_store.json'),
        )
        self._max_systems = kwargs.get('max_systems', 5)

    def _load_atlas(self) -> Dict[str, Any]:
        """Load Atlas store, falling back to builtin system map."""
        systems = dict(_BUILTIN_SYSTEMS)

        try:
            if os.path.exists(self._atlas_store_path):
                with open(self._atlas_store_path, 'r', encoding='utf-8') as f:
                    store = json.load(f)

                # Merge store entries into systems
                if isinstance(store, dict):
                    nodes = store.get('nodes', store.get('systems', {}))
                    if isinstance(nodes, dict):
                        for key, node in nodes.items():
                            if isinstance(node, dict):
                                systems[key] = {
                                    'name': node.get('name', key),
                                    'description': node.get('description', ''),
                                    'connects_to': node.get('connects_to', node.get('dependencies', [])),
                                    'keywords': node.get('keywords', node.get('tags', [])),
                                }
                    elif isinstance(nodes, list):
                        for node in nodes:
                            if isinstance(node, dict) and 'id' in node:
                                nid = node['id']
                                systems[nid] = {
                                    'name': node.get('name', nid),
                                    'description': node.get('description', ''),
                                    'connects_to': node.get('connects_to', []),
                                    'keywords': node.get('keywords', []),
                                }

                logger.info(f'[Atlas] Loaded {len(systems)} systems from atlas store')

        except Exception as e:
            logger.debug(f'Atlas store load failed, using builtins: {e}')

        return systems

    def _match_systems(self, task: str, systems: Dict[str, Any]) -> List[dict]:
        """Score each system by relevance to the task."""
        task_terms = set(task.lower().split())
        scored = []

        for sys_id, sys_data in systems.items():
            keywords = set(k.lower() for k in sys_data.get('keywords', []))
            name_terms = set(sys_data.get('name', '').lower().split())
            desc_terms = set(sys_data.get('description', '').lower().split()[:30])

            # Score by keyword overlap + name overlap + description overlap
            keyword_overlap = len(task_terms & keywords)
            name_overlap = len(task_terms & name_terms)
            desc_overlap = len(task_terms & desc_terms)

            score = (keyword_overlap * 3) + (name_overlap * 2) + desc_overlap

            if score > 0:
                scored.append({
                    'id': sys_id,
                    'name': sys_data['name'],
                    'description': sys_data['description'],
                    'connects_to': sys_data.get('connects_to', []),
                    'score': score,
                })

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:self._max_systems]

    def _build_architecture_context(
        self, matches: List[dict], all_systems: Dict[str, Any]
    ) -> str:
        """Build architecture context from matched systems."""
        if not matches:
            return 'No matching subsystems found in the Atlas knowledge graph.'

        parts = ['## Architecture Context (Atlas)\n']

        for m in matches:
            parts.append(f'### {m["name"]}')
            parts.append(f'{m["description"]}')

            # Show connections
            connections = m.get('connects_to', [])
            if connections:
                conn_names = []
                for conn_id in connections:
                    if conn_id in all_systems:
                        conn_names.append(all_systems[conn_id]['name'])
                    else:
                        conn_names.append(conn_id)
                parts.append(f'**Connects to:** {", ".join(conn_names)}')

            parts.append('')  # blank line

        return '\n'.join(parts)

    def build_context(
        self,
        task: str,
        handoff: Optional[Handoff] = None,
        **kwargs,
    ) -> ContextPack:
        """Build context using Atlas architecture knowledge graph."""
        start = time.time()

        # Load and match
        systems = self._load_atlas()
        matches = self._match_systems(task, systems)
        arch_context = self._build_architecture_context(matches, systems)

        # Build instructions
        instructions = f'Execute: {task}'
        if matches:
            primary = matches[0]
            instructions += f'\n\nPrimary system: {primary["name"]}'
            if primary.get('connects_to'):
                instructions += f'\nRelated systems: {", ".join(primary["connects_to"])}'

        if handoff and handoff.next_priorities:
            instructions += f'\nPriorities: {", ".join(handoff.next_priorities)}'

        relevant_history = ''
        if handoff:
            relevant_history = handoff.to_prompt()

        elapsed = (time.time() - start) * 1000
        total_chars = len(arch_context)

        self._metrics = {
            'build_time_ms': elapsed,
            'systems_matched': len(matches),
            'systems_total': len(systems),
            'tokens_used': int(total_chars / 3.5),
            'method': 'atlas',
        }

        logger.info(
            f'[AtlasStrategy] Built context: {len(matches)} systems matched, '
            f'{elapsed:.0f}ms'
        )

        # Collect relevant file paths from matched systems
        files = []
        file_map = {
            'cmc': 'packages/cmc_service/cmc_store.py',
            'hhni': 'packages/hhni/__init__.py',
            'vif': 'scripts/ai_engine/safety/vif_gates.py',
            'apoe': 'packages/apoe/__init__.py',
            'seg': 'packages/seg/__init__.py',
            'ai_engine': 'scripts/ai_engine/engine.py',
            'genome': 'scripts/ai_engine/genome_loader.py',
            'chain_director': 'scripts/ai_engine/chain_director.py',
            'mcp': 'lucid_mcp_server.py',
        }
        for m in matches:
            if m['id'] in file_map:
                files.append(file_map[m['id']])

        return ContextPack(
            task_summary=task,
            relevant_history=relevant_history,
            project_state=arch_context,
            instructions=instructions,
            files_to_examine=files[:10],
            research_notes=arch_context,
            tokens_used=int(total_chars / 3.5),
            build_time_ms=elapsed,
        )
