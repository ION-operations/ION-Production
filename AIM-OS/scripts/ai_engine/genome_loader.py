"""
AIM-OS AI Engine — Genome Loader

Reads agent genome definitions from .agent/genomes/ and builds
the genome layers for worker processes.

Design by Sev:
    "genome = Base + RoleOverlay + TaskOverlay"
    
    - Base: shared identity, principles, tool awareness
    - RoleOverlay: role-specific expertise (coder, architect, auditor)
    - TaskOverlay: task-specific scope, constraints, focus

Workers inherit parent base genome + role overlay + task overlay.
This ensures all workers share AIM-OS identity while being
specialised for their specific job.
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, field

logger = logging.getLogger('ai_engine.genome_loader')


# ── Genome Data ──────────────────────────────────────────

@dataclass
class GenomeLayer:
    """A single layer of a genome definition."""
    name: str
    content: str
    source: str = ''       # file path or 'synthesized'
    layer_type: str = ''   # base, role, task

    @property
    def token_estimate(self) -> int:
        return int(len(self.content) / 3.5)


@dataclass
class AgentGenome:
    """
    Complete genome for an agent/worker.
    Assembled from base + role overlay + task overlay.
    """
    base: GenomeLayer
    role_overlay: Optional[GenomeLayer] = None
    task_overlay: Optional[GenomeLayer] = None
    trail_overlay: Optional[GenomeLayer] = None  # 4th layer: temporal context
    instance_id: str = ''
    holder_id: str = ''

    def to_system_prompt(self, max_tokens: int = 4000) -> str:
        """Assemble the full system prompt from genome layers."""
        parts = []

        # Base identity
        if self.base.content:
            parts.append(self.base.content)

        # Role specialisation
        if self.role_overlay and self.role_overlay.content:
            parts.append(f"\n\n## Role: {self.role_overlay.name}\n{self.role_overlay.content}")

        # Task scope
        if self.task_overlay and self.task_overlay.content:
            parts.append(f"\n\n## Current Task Scope\n{self.task_overlay.content}")

        # Temporal context trail (4th layer)
        if self.trail_overlay and self.trail_overlay.content:
            parts.append(f"\n\n## Temporal Context\n{self.trail_overlay.content}")

        # Identity metadata
        if self.instance_id:
            parts.append(f"\n\n## Instance\nInstance ID: `{self.instance_id}`")

        full = '\n'.join(parts)

        # Budget: truncate if exceeds max tokens
        max_chars = int(max_tokens * 3.5)
        if len(full) > max_chars:
            full = full[:max_chars] + '\n\n[GENOME TRUNCATED — token budget exceeded]'

        return full

    @property
    def total_tokens(self) -> int:
        return sum(
            layer.token_estimate for layer in [self.base, self.role_overlay, self.task_overlay, self.trail_overlay]
            if layer
        )


# ── Genome Loader ────────────────────────────────────────

class GenomeLoader:
    """
    Loads agent genomes from .agent/genomes/ directory.
    
    Genome files are markdown with YAML frontmatter and sections.
    The loader parses these into structured GenomeLayers.
    
    Usage:
        loader = GenomeLoader('/path/to/AIM-OS')
        genome = loader.build_genome(role='coder', task='Fix the auth module')
    """

    # Role overlay templates (used when no genome file exists for a role)
    ROLE_OVERLAYS = {
        'coder': GenomeLayer(
            name='Coder',
            content=(
                "You are a senior software engineer. You write production-quality code.\n"
                "- TypeScript: strict mode, zero `any` types\n"
                "- Python: type hints, Google-style docstrings\n"
                "- Every function has a clear single responsibility\n"
                "- Error handling is explicit — no silent catches\n"
                "- You provide COMPLETE file contents for every edit"
            ),
            layer_type='role',
        ),
        'architect': GenomeLayer(
            name='Architect',
            content=(
                "You are a systems architect who thinks in layers and dependencies.\n"
                "- Always consider full system impact of changes\n"
                "- Present tradeoffs explicitly\n"
                "- Use structured output: diagrams, tables, numbered lists\n"
                "- Reference existing patterns when available\n"
                "- You advise and plan — you do NOT edit files directly"
            ),
            layer_type='role',
        ),
        'auditor': GenomeLayer(
            name='Auditor',
            content=(
                "You are a code reviewer and quality engineer.\n"
                "- Prioritise: security > correctness > performance > style\n"
                "- Provide specific, actionable feedback with line references\n"
                "- Check for: SQL injection, XSS, race conditions, memory leaks\n"
                "- You review and recommend — you do NOT edit files"
            ),
            layer_type='role',
        ),
        'researcher': GenomeLayer(
            name='Researcher',
            content=(
                "You are a deep research specialist.\n"
                "- Gather comprehensive information before drawing conclusions\n"
                "- Cite sources and evidence for all claims\n"
                "- Identify gaps in knowledge and flag uncertainties\n"
                "- Provide structured summaries with key findings"
            ),
            layer_type='role',
        ),
        'tester': GenomeLayer(
            name='Tester',
            content=(
                "You are a QA engineer and test specialist.\n"
                "- Write comprehensive tests: unit, integration, edge cases\n"
                "- Focus on: correctness, boundary conditions, error paths\n"
                "- Run tests and report results with clear pass/fail status\n"
                "- Suggest test improvements and coverage gaps"
            ),
            layer_type='role',
        ),
    }

    def __init__(self, workspace_root: str = ''):
        self.workspace_root = workspace_root or os.getcwd()
        self._genome_dir = os.path.join(self.workspace_root, '.agent', 'genomes')
        self._cached_base: Optional[GenomeLayer] = None
        self._cached_genomes: Dict[str, str] = {}

    def build_genome(
        self,
        role: str = 'coder',
        task: str = '',
        task_constraints: str = '',
        instance_id: str = '',
        holder_id: str = '',
        agent_name: str = '',
        include_trail: bool = True,
        max_base_tokens: int = 2000,
    ) -> AgentGenome:
        """
        Build a complete genome for a worker.
        
        Args:
            role: Worker role (coder, architect, auditor, researcher, tester)
            task: Task description for task overlay
            task_constraints: Additional constraints for the task
            instance_id: Unique instance identifier
            holder_id: Identity lock for MCP comms
            max_base_tokens: Token budget for base genome
        """
        # Load base genome
        base = self._load_base_genome(max_tokens=max_base_tokens)

        # Load role overlay
        role_overlay = self._load_role_overlay(role)

        # Build task overlay
        task_overlay = None
        if task:
            task_content = f"**Task:** {task}"
            if task_constraints:
                task_content += f"\n\n**Constraints:**\n{task_constraints}"
            task_overlay = GenomeLayer(
                name=f'Task: {task[:50]}',
                content=task_content,
                source='synthesized',
                layer_type='task',
            )

        # Build trail overlay (temporal context)
        trail_overlay = None
        if include_trail and agent_name:
            trail_overlay = self._build_trail_layer(agent_name)

        return AgentGenome(
            base=base,
            role_overlay=role_overlay,
            task_overlay=task_overlay,
            trail_overlay=trail_overlay,
            instance_id=instance_id,
            holder_id=holder_id,
        )

    def _build_trail_layer(self, agent_name: str) -> Optional[GenomeLayer]:
        """Build temporal context trail layer from recorded history."""
        try:
            try:
                from context_trail import ContextTrailRecorder
            except ImportError:
                try:
                    from ai_engine.context_trail import ContextTrailRecorder
                except ImportError:
                    return None

            recorder = ContextTrailRecorder(self.workspace_root)
            briefing = recorder.build_temporal_context(agent_name, recent_limit=10)
            xml = briefing.to_xml()

            if not xml or len(xml) < 50:
                return None

            return GenomeLayer(
                name=f'Temporal Context ({agent_name})',
                content=xml,
                source='context_trail',
                layer_type='trail',
            )
        except Exception as e:
            logger.warning(f'Failed to build trail layer: {e}')
            return None

    def _load_base_genome(self, max_tokens: int = 2000) -> GenomeLayer:
        """Load the base genome shared by all workers."""
        if self._cached_base:
            return self._cached_base

        # Try loading from .agent/genomes/
        genome_files = [
            'base.genome.md',
            'antigravity.genome.md',
            'shared.genome.md',
        ]

        for gfile in genome_files:
            gpath = os.path.join(self._genome_dir, gfile)
            if os.path.exists(gpath):
                content = self._read_genome_file(gpath, max_tokens)
                self._cached_base = GenomeLayer(
                    name='AIM-OS Base',
                    content=content,
                    source=gpath,
                    layer_type='base',
                )
                logger.info(f'[GenomeLoader] Loaded base genome from {gfile}')
                return self._cached_base

        # Fallback: synthesize minimal base
        self._cached_base = GenomeLayer(
            name='AIM-OS Base (Synthesized)',
            content=(
                "# AIM-OS Agent\n\n"
                "You are a worker agent in the AIM-OS (AI Mind Operating System) project.\n\n"
                "## Core Principles\n"
                "1. Production quality code — no shortcuts\n"
                "2. Explicit error handling and type safety\n"
                "3. Evidence-based decisions with confidence tracking\n"
                "4. Clear communication via structured output\n"
                "5. Never guess — ask or flag uncertainty\n\n"
                "## Output Format\n"
                "Always respond with structured JSON as specified in your task."
            ),
            source='synthesized',
            layer_type='base',
        )
        return self._cached_base

    def _load_role_overlay(self, role: str) -> GenomeLayer:
        """Load role-specific genome overlay."""
        role_lower = role.lower()

        # Try loading from file
        role_files = [
            f'{role_lower}.genome.md',
            f'{role_lower}_overlay.md',
            f'role_{role_lower}.md',
        ]

        for rfile in role_files:
            rpath = os.path.join(self._genome_dir, rfile)
            if os.path.exists(rpath):
                content = self._read_genome_file(rpath, max_tokens=1000)
                return GenomeLayer(
                    name=role.title(),
                    content=content,
                    source=rpath,
                    layer_type='role',
                )

        # Fallback: use built-in overlay
        return self.ROLE_OVERLAYS.get(role_lower, self.ROLE_OVERLAYS['coder'])

    def _read_genome_file(self, path: str, max_tokens: int = 2000) -> str:
        """Read a genome file, stripping YAML frontmatter."""
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Strip YAML frontmatter
            if content.startswith('---'):
                end = content.find('---', 3)
                if end > 0:
                    content = content[end + 3:].strip()

            # Budget: truncate to max tokens
            max_chars = int(max_tokens * 3.5)
            if len(content) > max_chars:
                content = content[:max_chars]

            return content

        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f'Failed to read genome file {path}: {e}')
            return ''

    def list_genomes(self) -> List[Dict]:
        """List all available genome files."""
        genomes = []
        if os.path.isdir(self._genome_dir):
            for f in os.listdir(self._genome_dir):
                if f.endswith('.md'):
                    fpath = os.path.join(self._genome_dir, f)
                    genomes.append({
                        'name': f,
                        'path': fpath,
                        'size': os.path.getsize(fpath),
                    })
        return genomes

    def status(self) -> dict:
        return {
            'genome_dir': self._genome_dir,
            'genome_dir_exists': os.path.isdir(self._genome_dir),
            'available_genomes': self.list_genomes(),
            'builtin_roles': list(self.ROLE_OVERLAYS.keys()),
            'cached_base': self._cached_base is not None,
        }
