"""
AIM-OS Agent Roundtable — Collective Context System

A roundtable where N specialist agents each hold deep domain context,
collectively commanding 360K+ tokens of knowledge — far beyond any
single agent's context window.

Architecture:
    Shared Context  (~5K tokens)  — ALL agents get the system map
    Domain Context  (~25K tokens) — UNIQUE per agent (their system's docs)
    Overlap Context (~5K tokens)  — NEIGHBORS share adjacent summaries

Two execution modes:
    Simulated — builds context packs, shows what each agent would know
    Live      — spawns agents via GeminiCLIProvider with real inference

Usage:
    from roundtable import Roundtable

    rt = Roundtable()
    rt.convene("System architecture review")
    result = rt.discuss("How does CMC interact with HHNI for memory retrieval?")
    print(result.unified_answer)
    print(result.minutes)

Part of the AIM-OS AI Engine.
"""

import json
import os
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict

# Path setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE = os.path.dirname(SCRIPTS_DIR)

for p in [WORKSPACE, SCRIPTS_DIR, SCRIPT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

logger = logging.getLogger('ai_engine.roundtable')


# ═══════════════════════════════════════════════════════════
#  DATA MODELS
# ═══════════════════════════════════════════════════════════

@dataclass
class RoundtableConfig:
    """Configuration for a roundtable session."""
    # Which systems to include (None = all 12)
    systems: Optional[List[str]] = None
    # Context budgets (characters, ~4 chars per token)
    shared_context_budget: int = 20_000     # ~5K tokens
    domain_context_budget: int = 100_000    # ~25K tokens
    overlap_context_budget: int = 20_000    # ~5K tokens
    # Execution
    mode: str = 'simulated'   # 'simulated' or 'live'
    timeout_per_agent: int = 120
    # Quality
    min_relevance_score: float = 0.2  # Agents below this skip contributing
    enable_synthesis: bool = True
    # Comms integration
    enable_comms: bool = False         # Wire into MCP + FS comms
    comms_sender: str = 'Claude Opus 4.6'  # Who posts minutes (canonical ID)
    broadcast_mcp: bool = True         # Post to MCP message bus
    write_fs_minutes: bool = True      # Write .agent/comms/ minutes
    write_jsonl_log: bool = True       # Append to messages.jsonl


@dataclass
class Seat:
    """One agent's position at the roundtable.
    
    Each Seat holds a specialist agent fully loaded with:
    - Their genome (identity + protocols)
    - Shared context (system map everyone knows)
    - Domain context (deep knowledge of their system)
    - Overlap context (adjacent system awareness)
    """
    system_id: str
    system_name: str
    layer: str
    package: str
    # Context payloads
    genome: str = ""
    shared_context: str = ""
    domain_context: str = ""
    overlap_context: str = ""
    # Metadata
    domain_context_tokens: int = 0
    total_context_tokens: int = 0
    doc_files_loaded: int = 0
    classes_known: int = 0
    functions_known: int = 0
    
    @property
    def agent_name(self) -> str:
        return f"AGENT-{self.system_id.upper()}"
    
    @property
    def full_context(self) -> str:
        """The complete context this agent would receive."""
        parts = []
        if self.genome:
            parts.append(f"# Your Identity\n\n{self.genome}")
        if self.shared_context:
            parts.append(f"# System-Wide Awareness\n\n{self.shared_context}")
        if self.domain_context:
            parts.append(f"# Your Domain Knowledge (Deep)\n\n{self.domain_context}")
        if self.overlap_context:
            parts.append(f"# Adjacent Systems Awareness\n\n{self.overlap_context}")
        return "\n\n---\n\n".join(parts)
    
    @property
    def context_stats(self) -> dict:
        return {
            "system_id": self.system_id,
            "agent_name": self.agent_name,
            "genome_chars": len(self.genome),
            "shared_chars": len(self.shared_context),
            "domain_chars": len(self.domain_context),
            "overlap_chars": len(self.overlap_context),
            "total_chars": len(self.full_context),
            "est_tokens": len(self.full_context) // 4,
            "doc_files_loaded": self.doc_files_loaded,
            "classes_known": self.classes_known,
            "functions_known": self.functions_known,
        }


@dataclass
class Contribution:
    """An agent's contribution to the discussion."""
    agent_name: str
    system_id: str
    content: str
    relevance_score: float = 0.0
    quality_score: float = 0.0
    tokens_used: int = 0
    elapsed_ms: float = 0.0


@dataclass
class Discussion:
    """Result of a roundtable discussion."""
    topic: str
    question: str
    contributions: List[Contribution] = field(default_factory=list)
    unified_answer: str = ""
    total_agents: int = 0
    contributing_agents: int = 0
    collective_tokens: int = 0
    elapsed_ms: float = 0.0
    
    @property
    def minutes(self) -> str:
        """Return formatted discussion minutes."""
        lines = []
        lines.append(f"# Roundtable Minutes")
        lines.append(f"\n**Topic:** {self.topic}")
        lines.append(f"**Question:** {self.question}")
        lines.append(f"**Agents:** {self.contributing_agents}/{self.total_agents} contributed")
        lines.append(f"**Collective Context:** ~{self.collective_tokens:,} tokens")
        lines.append(f"**Duration:** {self.elapsed_ms:.0f}ms")
        
        for c in sorted(self.contributions, key=lambda x: -x.relevance_score):
            lines.append(f"\n## {c.agent_name} (relevance: {c.relevance_score:.2f})")
            lines.append(c.content[:2000])
        
        if self.unified_answer:
            lines.append(f"\n## Synthesized Answer")
            lines.append(self.unified_answer)
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
#  CONTEXT LOADERS
# ═══════════════════════════════════════════════════════════

# System adjacency map — which systems are "neighbors"
SYSTEM_ADJACENCY = {
    'cmc': ['hhni', 'seg', 'vif'],       # Memory ↔ Retrieval ↔ Evidence ↔ Confidence
    'hhni': ['cmc', 'seg', 'sdfcvf'],    # Retrieval ↔ Memory ↔ Evidence ↔ Convergence
    'seg': ['cmc', 'hhni', 'vif'],       # Evidence ↔ Memory ↔ Retrieval ↔ Confidence
    'vif': ['seg', 'cmc', 'cas'],        # Confidence ↔ Evidence ↔ Memory ↔ Cognition
    'sdfcvf': ['hhni', 'apoe', 'cas'],   # Convergence ↔ Retrieval ↔ Orchestration ↔ Cognition
    'apoe': ['sdfcvf', 'cas', 'tcs'],    # Orchestration ↔ Convergence ↔ Cognition ↔ Timeline
    'cas': ['vif', 'apoe', 'iis'],       # Cognition ↔ Confidence ↔ Orchestration ↔ Intuition
    'tcs': ['apoe', 'cas', 'iis'],       # Timeline ↔ Orchestration ↔ Cognition ↔ Intuition
    'iis': ['cas', 'tcs', 'vif'],        # Intuition ↔ Cognition ↔ Timeline ↔ Confidence
    'docs': ['cmc', 'seg', 'hhni'],      # Docs ↔ Memory ↔ Evidence ↔ Retrieval
    'context': ['hhni', 'cmc', 'apoe'],  # Context ↔ Retrieval ↔ Memory ↔ Orchestration
    'mcp': ['apoe', 'cmc', 'vif'],       # MCP ↔ Orchestration ↔ Memory ↔ Confidence
}


def load_shared_context(workspace: str, budget: int = 20_000) -> str:
    """Build the shared context that ALL agents receive.
    
    Contains:
    - System hierarchy (layer structure)
    - Agent roster (who knows what)
    - Communication protocol
    """
    parts = []
    
    # 1. System hierarchy
    parts.append("## AIM-OS System Hierarchy\n")
    parts.append("Layer 1 (Foundation): CMC (memory), SEG (evidence), HHNI (retrieval)")
    parts.append("Layer 2 (Intelligence): VIF (confidence), SDF-CVF (convergence)")
    parts.append("Layer 3 (Orchestration): APOE (workflows)")
    parts.append("Layer 4 (Cognition): CAS (analysis), TCS (timeline)")
    parts.append("Layer 5 (Meta): IIS (intuition)")
    parts.append("Cross-cutting: DOCS (documentation), CONTEXT (maintenance), MCP (health)")
    
    # 2. Agent roster
    parts.append("\n## Agent Roster — Who Knows What\n")
    try:
        from agent_spawner import SYSTEM_REGISTRY
        for sys_id, spec in SYSTEM_REGISTRY.items():
            parts.append(f"- **AGENT-{sys_id.upper()}**: {spec.system_name} "
                        f"(Layer {spec.layer}, package: `{spec.package}`)")
    except ImportError:
        parts.append("(Registry unavailable)")
    
    # 3. Communication protocol
    parts.append("\n## Roundtable Protocol\n")
    parts.append("When contributing to a discussion:")
    parts.append("1. State what you know from YOUR domain (be specific, cite classes/functions)")
    parts.append("2. Rate your relevance 0-1 (how relevant is your domain to this question?)")
    parts.append("3. Note cross-system implications (what should other agents know?)")
    parts.append("4. Be concise — your peers are also contributing")
    
    shared = "\n".join(parts)
    return shared[:budget]


def load_domain_context(workspace: str, system_id: str, budget: int = 100_000) -> tuple:
    """Load deep domain context for a specific system.
    
    Reads:
    - T0_executive.md (with code structure appendix from enrichment)
    - L0_executive.md (if different from T0)
    - L1-L4 docs if they exist
    - README.md from the package
    - system.map.lucid.json5 if it exists
    
    Returns:
        (context_str, metadata_dict)
    """
    from agent_spawner import SYSTEM_REGISTRY
    
    spec = SYSTEM_REGISTRY.get(system_id)
    if not spec:
        return "", {"files": 0, "classes": 0, "functions": 0}
    
    sys_dir = os.path.join(workspace, "knowledge_architecture", "systems", spec.system_dir)
    pkg_dir = os.path.join(workspace, "packages", spec.package)
    
    parts = []
    files_loaded = 0
    classes_found = 0
    functions_found = 0
    
    # Priority order for docs
    doc_files = [
        "T0_executive.md",
        "L0_executive.md",
        "L1_architecture.md",
        "L2_implementation.md",
        "L3_deep_dive.md",
        "L4_all_source.md",
        "system.map.lucid.json5",
        "system.index.lucid.json5",
    ]
    
    chars_used = 0
    for doc_file in doc_files:
        doc_path = os.path.join(sys_dir, doc_file)
        if os.path.exists(doc_path):
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Respect budget
                remaining = budget - chars_used
                if remaining <= 0:
                    break
                if len(content) > remaining:
                    content = content[:remaining] + "\n...(truncated)"
                
                parts.append(f"### {doc_file}\n\n{content}")
                chars_used += len(content)
                files_loaded += 1
                
                # Count classes/functions from enriched appendix
                classes_found += content.lower().count("**") // 2  # Bold items in appendix
                functions_found += content.count("()` —")
            except (UnicodeDecodeError, OSError):
                pass
    
    # Package README
    readme_path = os.path.join(pkg_dir, "README.md")
    if os.path.exists(readme_path) and chars_used < budget:
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                readme = f.read()
            remaining = budget - chars_used
            if len(readme) > remaining:
                readme = readme[:remaining]
            parts.append(f"### Package README\n\n{readme}")
            files_loaded += 1
        except (UnicodeDecodeError, OSError):
            pass
    
    context = "\n\n".join(parts)
    metadata = {
        "files": files_loaded,
        "classes": classes_found,
        "functions": functions_found,
    }
    return context, metadata


def load_overlap_context(workspace: str, system_id: str, budget: int = 20_000) -> str:
    """Load adjacent system summaries for cross-referencing.
    
    Each agent gets brief summaries of their neighbor systems,
    so they have awareness of integration points.
    """
    neighbors = SYSTEM_ADJACENCY.get(system_id, [])
    if not neighbors:
        return ""
    
    from agent_spawner import SYSTEM_REGISTRY
    
    parts = []
    parts.append("## Adjacent Systems (brief summaries)\n")
    
    chars_used = 0
    per_neighbor = budget // max(len(neighbors), 1)
    
    for neighbor_id in neighbors:
        spec = SYSTEM_REGISTRY.get(neighbor_id)
        if not spec:
            continue
        
        # Read just the T0/L0 summary (first 500 chars)
        sys_dir = os.path.join(workspace, "knowledge_architecture", "systems", spec.system_dir)
        for doc in ["T0_executive.md", "L0_executive.md"]:
            doc_path = os.path.join(sys_dir, doc)
            if os.path.exists(doc_path):
                try:
                    with open(doc_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Take just the executive summary portion
                    summary = content[:min(per_neighbor, len(content))]
                    parts.append(f"### AGENT-{neighbor_id.upper()}: {spec.system_name}\n{summary}")
                    chars_used += len(summary)
                except (UnicodeDecodeError, OSError):
                    pass
                break
        
        if chars_used >= budget:
            break
    
    return "\n\n".join(parts)


# ═══════════════════════════════════════════════════════════
#  ROUNDTABLE
# ═══════════════════════════════════════════════════════════

class Roundtable:
    """The Agent Roundtable — collective context orchestrator.
    
    Convenes N specialist agents, each loaded with deep domain context,
    creating a collective knowledge space far larger than any single
    agent's context window.
    
    Usage:
        rt = Roundtable()
        rt.convene("Architecture review")
        
        # See what each agent knows
        for seat in rt.seats:
            print(f"{seat.agent_name}: {seat.domain_context_tokens} tokens")
        
        # Run a discussion (simulated mode)
        result = rt.discuss("How does memory flow from CMC to HHNI?")
        print(result.minutes)
    """
    
    def __init__(self, config: Optional[RoundtableConfig] = None):
        self.config = config or RoundtableConfig()
        self.seats: List[Seat] = []
        self.topic: str = ""
        self._convened = False
        self._shared_context = ""
        self._comms: Optional['CommsIntegration'] = None
    
    def convene(self, topic: str) -> 'Roundtable':
        """Load all agents with their contexts. Returns self for chaining."""
        start = time.time()
        self.topic = topic
        self.seats = []
        
        # Import registry
        try:
            from agent_spawner import SYSTEM_REGISTRY, generate_specialist_genome
        except ImportError:
            raise RuntimeError("agent_spawner.py not found on path")
        
        # Determine which systems to include
        system_ids = self.config.systems or list(SYSTEM_REGISTRY.keys())
        
        # 1. Build shared context (same for all)
        self._shared_context = load_shared_context(
            WORKSPACE, self.config.shared_context_budget
        )
        
        # 2. Create seats with domain context
        for sys_id in system_ids:
            spec = SYSTEM_REGISTRY.get(sys_id)
            if not spec:
                continue
            
            # Generate genome
            genome = generate_specialist_genome(spec)
            
            # Load domain context
            domain_ctx, meta = load_domain_context(
                WORKSPACE, sys_id, self.config.domain_context_budget
            )
            
            # Load overlap context
            overlap_ctx = load_overlap_context(
                WORKSPACE, sys_id, self.config.overlap_context_budget
            )
            
            seat = Seat(
                system_id=sys_id,
                system_name=spec.system_name,
                layer=spec.layer,
                package=spec.package,
                genome=genome,
                shared_context=self._shared_context,
                domain_context=domain_ctx,
                overlap_context=overlap_ctx,
                doc_files_loaded=meta["files"],
                classes_known=meta["classes"],
                functions_known=meta["functions"],
            )
            seat.domain_context_tokens = len(domain_ctx) // 4
            seat.total_context_tokens = len(seat.full_context) // 4
            
            self.seats.append(seat)
        
        self._convened = True
        elapsed = (time.time() - start) * 1000
        
        logger.info(
            f"[Roundtable] Convened {len(self.seats)} agents for '{topic}' "
            f"in {elapsed:.0f}ms"
        )
        
        return self
    
    def _score_relevance(self, seat: Seat, question: str) -> float:
        """Score how relevant an agent is to a specific question."""
        q_lower = question.lower()
        score = 0.0
        
        # Check if system name or ID mentioned
        if seat.system_id in q_lower or seat.system_name.lower() in q_lower:
            score += 0.5
        
        # Check if agent name mentioned
        if seat.agent_name.lower() in q_lower:
            score += 0.3
        
        # Check domain keywords
        domain_lower = seat.domain_context.lower()
        q_words = [w for w in q_lower.split() if len(w) > 3]
        matches = sum(1 for w in q_words if w in domain_lower)
        if q_words:
            score += 0.4 * (matches / len(q_words))
        
        # Package name match
        if seat.package in q_lower:
            score += 0.2
        
        return min(score, 1.0)
    
    def discuss(self, question: str) -> Discussion:
        """Run a roundtable discussion on a question.
        
        In simulated mode: returns what each agent would know/contribute
        In live mode: spawns actual Gemini CLI agents (not implemented yet)
        """
        if not self._convened:
            raise RuntimeError("Must call convene() before discuss()")
        
        start = time.time()
        
        discussion = Discussion(
            topic=self.topic,
            question=question,
            total_agents=len(self.seats),
        )
        
        for seat in self.seats:
            relevance = self._score_relevance(seat, question)
            
            if relevance < self.config.min_relevance_score:
                continue
            
            if self.config.mode == 'simulated':
                contribution = self._simulated_contribution(seat, question, relevance)
            else:
                contribution = self._live_contribution(seat, question, relevance)
            
            discussion.contributions.append(contribution)
        
        discussion.contributing_agents = len(discussion.contributions)
        discussion.collective_tokens = sum(
            s.total_context_tokens for s in self.seats
        )
        
        # Synthesize unified answer
        if self.config.enable_synthesis and discussion.contributions:
            discussion.unified_answer = self._synthesize(discussion)
        
        discussion.elapsed_ms = (time.time() - start) * 1000
        
        # Broadcast to comms infrastructure
        if self.config.enable_comms:
            if self._comms is None:
                self._comms = CommsIntegration(WORKSPACE, self.config.comms_sender)
            self._comms.broadcast_discussion(
                discussion,
                broadcast_mcp=self.config.broadcast_mcp,
                write_fs=self.config.write_fs_minutes,
                write_jsonl=self.config.write_jsonl_log,
            )
        
        return discussion
    
    def _simulated_contribution(self, seat: Seat, question: str, 
                                 relevance: float) -> Contribution:
        """Simulated contribution — shows what the agent would know."""
        # Extract the most relevant sections from domain context
        q_words = set(question.lower().split())
        lines = seat.domain_context.split('\n')
        
        relevant_lines = []
        for i, line in enumerate(lines):
            line_words = set(line.lower().split())
            overlap = len(q_words & line_words)
            if overlap >= 2 or any(w in line.lower() for w in q_words if len(w) > 4):
                # Include this line and 2 lines of context
                for j in range(max(0, i-1), min(len(lines), i+3)):
                    if lines[j] not in relevant_lines:
                        relevant_lines.append(lines[j])
        
        # Build contribution
        content_parts = []
        content_parts.append(f"**{seat.agent_name}** — {seat.system_name}")
        content_parts.append(f"Domain: {seat.domain_context_tokens:,} tokens of context loaded")
        content_parts.append(f"Relevance: {relevance:.2f}")
        
        if relevant_lines:
            content_parts.append(f"\nRelevant knowledge ({len(relevant_lines)} lines):")
            content_parts.append("\n".join(relevant_lines[:30]))  # Cap at 30 lines
        else:
            content_parts.append("\nNo directly matching content found in domain context.")
            content_parts.append(f"(But this agent has {seat.classes_known} classes "
                               f"and {seat.functions_known} functions documented)")
        
        return Contribution(
            agent_name=seat.agent_name,
            system_id=seat.system_id,
            content="\n".join(content_parts),
            relevance_score=relevance,
            tokens_used=seat.total_context_tokens,
        )
    
    def _live_contribution(self, seat: Seat, question: str,
                            relevance: float) -> Contribution:
        """Live contribution — actually invokes the LLM."""
        # Build the full prompt
        prompt = (
            f"{seat.full_context}\n\n"
            f"---\n\n"
            f"# Roundtable Discussion\n\n"
            f"**Topic:** {self.topic}\n"
            f"**Question:** {question}\n\n"
            f"Contribute your domain expertise. Be specific — cite actual "
            f"classes, functions, and code paths from your system. "
            f"Rate your relevance to this question 0-1."
        )
        
        # Try to use GeminiCLIProvider
        try:
            from gemini_cli_provider import GeminiCLIProvider
            provider = GeminiCLIProvider()
            start = time.time()
            result = provider.execute(
                prompt,
                timeout=self.config.timeout_per_agent,
                cwd=WORKSPACE,
            )
            elapsed = (time.time() - start) * 1000
            
            return Contribution(
                agent_name=seat.agent_name,
                system_id=seat.system_id,
                content=result.output if result.success else f"Error: {result.error}",
                relevance_score=relevance,
                tokens_used=seat.total_context_tokens,
                elapsed_ms=elapsed,
            )
        except ImportError:
            return self._simulated_contribution(seat, question, relevance)
    
    def _synthesize(self, discussion: Discussion) -> str:
        """Synthesize contributions into a unified answer."""
        parts = []
        parts.append(f"Based on input from {discussion.contributing_agents} "
                     f"specialist agents ({discussion.collective_tokens:,} tokens collective context):\n")
        
        # Sort by relevance and take top contributions
        top = sorted(discussion.contributions, key=lambda c: -c.relevance_score)
        
        for c in top[:5]:
            parts.append(f"**{c.agent_name}** (relevance {c.relevance_score:.2f}):")
            # Extract just the relevant knowledge section
            lines = c.content.split('\n')
            knowledge_lines = [l for l in lines if l.strip() and not l.startswith('**') 
                             and 'tokens of context' not in l and 'Relevance:' not in l]
            parts.append("  " + "\n  ".join(knowledge_lines[:10]))
        
        return "\n\n".join(parts)
    
    # ── Reporting ──────────────────────────────────────────
    
    def stats(self) -> dict:
        """Return roundtable statistics."""
        if not self._convened:
            return {"status": "not convened"}
        
        total_tokens = sum(s.total_context_tokens for s in self.seats)
        total_classes = sum(s.classes_known for s in self.seats)
        total_functions = sum(s.functions_known for s in self.seats)
        
        return {
            "topic": self.topic,
            "agents": len(self.seats),
            "collective_tokens": total_tokens,
            "collective_classes": total_classes,
            "collective_functions": total_functions,
            "mode": self.config.mode,
            "seats": [s.context_stats for s in self.seats],
        }
    
    def print_stats(self):
        """Print a formatted stats table."""
        if not self._convened:
            print("Roundtable not yet convened. Call convene() first.")
            return
        
        total_tokens = sum(s.total_context_tokens for s in self.seats)
        total_classes = sum(s.classes_known for s in self.seats)
        total_functions = sum(s.functions_known for s in self.seats)
        
        print("=" * 70)
        print(f"  AGENT ROUNDTABLE — {self.topic}")
        print("=" * 70)
        print(f"\n  Agents: {len(self.seats)}  |  "
              f"Collective Context: ~{total_tokens:,} tokens  |  "
              f"Mode: {self.config.mode}")
        print(f"  Classes known: {total_classes:,}  |  "
              f"Functions known: {total_functions:,}")
        
        print(f"\n{'Agent':20s} {'Layer':8s} {'Domain':>10s} {'Overlap':>10s} "
              f"{'Total':>10s} {'Docs':>6s}")
        print("-" * 70)
        
        for seat in self.seats:
            stats = seat.context_stats
            print(f"  {seat.agent_name:18s} {seat.layer:8s} "
                  f"{stats['domain_chars']//4:>8,}t "
                  f"{stats['overlap_chars']//4:>8,}t "
                  f"{stats['est_tokens']:>8,}t "
                  f"{stats['doc_files_loaded']:>4d}")
        
        print(f"\n{'':20s} {'':8s} {'':>10s} {'':>10s} "
              f"{total_tokens:>8,}t total")


# ═══════════════════════════════════════════════════════════
#  COMMS INTEGRATION
# ═══════════════════════════════════════════════════════════

class CommsIntegration:
    """Wires the roundtable into the existing AIM-OS comms backbone.
    
    Integrates with 4 layers:
    1. MCP Message Bus  — send_ai_message for agent broadcasts
    2. Filesystem Comms — .agent/comms/ for persistent minutes
    3. Identity Registry — canonical agent name resolution
    4. JSONL Log        — structured message log
    """
    
    def __init__(self, workspace: str, sender: str = 'Claude Opus 4.6'):
        self.workspace = workspace
        self.sender = sender
        self.comms_root = os.path.join(workspace, '.agent', 'comms')
        self._identity_module = None
    
    def resolve_identity(self, agent_name: str) -> Dict[str, str]:
        """Resolve agent name through the identity registry."""
        if self._identity_module is None:
            try:
                comms_dir = os.path.join(self.workspace, 'scripts', 'agent_comms')
                if comms_dir not in sys.path:
                    sys.path.insert(0, comms_dir)
                import identity_registry
                self._identity_module = identity_registry
            except ImportError:
                return {'canonical_id': agent_name, 'route_key': agent_name.lower(),
                        'matched': 'false'}
        return self._identity_module.resolve_identity(agent_name)
    
    def broadcast_discussion(self, discussion: 'Discussion',
                              broadcast_mcp: bool = True,
                              write_fs: bool = True,
                              write_jsonl: bool = True):
        """Broadcast a completed discussion to all comms channels.
        
        This makes the roundtable discussion visible to:
        - All agents via MCP message bus (139+ messages in history)
        - The JOC AgentCommsPage UI (380-line threaded message view)
        - Future sessions via filesystem persistence
        """
        thread_id = self._make_thread_id(discussion)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if broadcast_mcp:
            self._broadcast_mcp(discussion, thread_id, timestamp)
        
        if write_fs:
            self._write_fs_minutes(discussion, thread_id, timestamp)
        
        if write_jsonl:
            self._write_jsonl(discussion, thread_id, timestamp)
    
    def _make_thread_id(self, discussion: 'Discussion') -> str:
        """Generate a thread ID for the discussion."""
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        topic_slug = discussion.topic.lower()
        topic_slug = ''.join(c if c.isalnum() else '_' for c in topic_slug)
        topic_slug = topic_slug[:40].strip('_')
        return f"roundtable_{topic_slug}_{date}"
    
    def _broadcast_mcp(self, discussion: 'Discussion', thread_id: str,
                        timestamp: str):
        """Post discussion summary to MCP message bus via direct JSON append.
        
        Writes directly to mcp_ai_messages.json in the same format
        as all 401+ existing messages — no heavy imports needed.
        """
        try:
            # Find the messages file
            msg_file = os.path.join(self.workspace, 'mcp_ai_messages.json')
            if not os.path.exists(msg_file):
                msg_file = os.path.join(self.workspace, 'data', 'mcp', 'mcp_ai_messages.json')
            
            if not os.path.exists(msg_file):
                logger.warning("[CommsIntegration] mcp_ai_messages.json not found")
                return
            
            # Build summary content
            top_agents = sorted(discussion.contributions,
                              key=lambda c: -c.relevance_score)[:5]
            summary_parts = [
                f"[ROUNDTABLE] {discussion.topic}",
                f"Question: {discussion.question}",
                f"Contributing: {discussion.contributing_agents}/{discussion.total_agents} agents",
                f"Collective: {discussion.collective_tokens:,} tokens",
                "",
                "Top contributors:",
            ]
            for c in top_agents:
                summary_parts.append(
                    f"  {c.agent_name} (rel={c.relevance_score:.2f})"
                )
            
            # Create message in exact existing format
            msg_id = f"ai_msg_rt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            new_msg = {
                "message_id": msg_id,
                "from_ai": self.sender,
                "to_ai": "all",
                "content": "\n".join(summary_parts),
                "message_type": "status_update",
                "priority": "medium",
                "thread_id": thread_id,
                "timestamp": timestamp,
                "response_required": False,
            }
            
            # Read existing, append, write back
            with open(msg_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            messages.append(new_msg)
            
            with open(msg_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[CommsIntegration] MCP message {msg_id} appended to {msg_file}")
        except Exception as e:
            logger.warning(f"[CommsIntegration] MCP broadcast failed: {e}")
    
    def _write_fs_minutes(self, discussion: 'Discussion', thread_id: str,
                           timestamp: str):
        """Write discussion minutes to filesystem comms."""
        try:
            # Write to broadcasts/
            broadcasts_dir = os.path.join(self.comms_root, 'broadcasts')
            os.makedirs(broadcasts_dir, exist_ok=True)
            
            date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            sender_identity = self.resolve_identity(self.sender)
            route_key = sender_identity.get('route_key', 'roundtable')
            
            filename = f"{date}_{route_key}_roundtable_{discussion.topic[:30].lower().replace(' ', '_')}.md"
            filepath = os.path.join(broadcasts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(discussion.minutes)
            
            logger.info(f"[CommsIntegration] Minutes written to {filepath}")
        except Exception as e:
            logger.warning(f"[CommsIntegration] FS minutes write failed: {e}")
    
    def _write_jsonl(self, discussion: 'Discussion', thread_id: str,
                      timestamp: str):
        """Append structured message to JSONL log."""
        try:
            logs_dir = os.path.join(self.comms_root, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            jsonl_path = os.path.join(logs_dir, 'messages.jsonl')
            
            record = {
                'type': 'roundtable_discussion',
                'thread_id': thread_id,
                'timestamp': timestamp,
                'sender': self.sender,
                'topic': discussion.topic,
                'question': discussion.question,
                'total_agents': discussion.total_agents,
                'contributing_agents': discussion.contributing_agents,
                'collective_tokens': discussion.collective_tokens,
                'elapsed_ms': discussion.elapsed_ms,
                'top_contributors': [
                    {'agent': c.agent_name, 'relevance': round(c.relevance_score, 3)}
                    for c in sorted(discussion.contributions,
                                   key=lambda x: -x.relevance_score)[:5]
                ],
            }
            
            with open(jsonl_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            logger.info(f"[CommsIntegration] JSONL record appended")
        except Exception as e:
            logger.warning(f"[CommsIntegration] JSONL write failed: {e}")
    
    def get_comms_status(self) -> Dict:
        """Return status of all comms channels."""
        status = {
            'workspace': self.workspace,
            'sender': self.sender,
            'comms_root': self.comms_root,
            'comms_root_exists': os.path.isdir(self.comms_root),
        }
        
        # Check sub-directories
        for subdir in ['broadcasts', 'handoffs', 'inbox', 'status', 'logs']:
            path = os.path.join(self.comms_root, subdir)
            status[f'{subdir}_exists'] = os.path.isdir(path)
            if os.path.isdir(path):
                items = [f for f in os.listdir(path)
                         if not f.startswith('.')]
                status[f'{subdir}_count'] = len(items)
        
        # Check MCP message bus
        try:
            mcp_msgs = os.path.join(self.workspace, 'mcp_ai_messages.json')
            if os.path.exists(mcp_msgs):
                with open(mcp_msgs, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                status['mcp_message_count'] = len(data) if isinstance(data, list) else 0
            else:
                data_msgs = os.path.join(self.workspace, 'data', 'mcp', 'mcp_ai_messages.json')
                if os.path.exists(data_msgs):
                    with open(data_msgs, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    status['mcp_message_count'] = len(data) if isinstance(data, list) else 0
        except Exception:
            status['mcp_message_count'] = 'error'
        
        # Check identity registry
        identity = self.resolve_identity(self.sender)
        status['sender_identity'] = identity
        
        # Check JSONL log
        jsonl = os.path.join(self.comms_root, 'logs', 'messages.jsonl')
        if os.path.exists(jsonl):
            with open(jsonl, 'r', encoding='utf-8') as f:
                status['jsonl_entries'] = sum(1 for _ in f)
        else:
            status['jsonl_entries'] = 0
        
        return status


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AIM-OS Agent Roundtable")
    parser.add_argument("command", choices=["convene", "discuss", "stats",
                                            "comms-status", "mesh-matrix"],
                       help="Command to run")
    parser.add_argument("--topic", default="System Architecture Review",
                       help="Discussion topic")
    parser.add_argument("--question", default="",
                       help="Question to discuss")
    parser.add_argument("--mode", default="simulated",
                       choices=["simulated", "live", "mesh"],
                       help="Execution mode (mesh = cascade routing)")
    parser.add_argument("--depth", type=int, default=2,
                       help="Cascade depth for mesh mode")
    parser.add_argument("--seeds", type=int, default=3,
                       help="Number of seed agents for mesh mode")
    parser.add_argument("--systems", nargs="*", default=None,
                       help="Specific systems to include (default: all)")
    parser.add_argument("--comms", action="store_true",
                       help="Enable comms integration (MCP + FS + JSONL)")
    parser.add_argument("--sender", default="Claude Opus 4.6",
                       help="Sender identity for comms")
    args = parser.parse_args()
    
    config = RoundtableConfig(
        mode=args.mode,
        systems=args.systems,
        enable_comms=args.comms,
        comms_sender=args.sender,
    )
    rt = Roundtable(config)
    
    if args.command == "convene":
        rt.convene(args.topic)
        rt.print_stats()
    
    elif args.command == "discuss":
        if not args.question:
            print("Error: --question is required for discuss command")
            return
        rt.convene(args.topic)
        
        if args.mode == 'mesh':
            # Mesh mode: cascade routing through affinity graph
            from agent_mesh import AffinityGraph, mesh_discuss
            graph = AffinityGraph.from_seats(rt.seats)
            result = mesh_discuss(rt, graph, args.question,
                               max_seeds=args.seeds,
                               max_depth=args.depth)
            print(result.minutes)
        else:
            result = rt.discuss(args.question)
            print(result.minutes)
        
        if args.comms:
            print(f"\n  [Comms] Discussion broadcast to MCP + FS + JSONL")
    
    elif args.command == "stats":
        rt.convene(args.topic)
        rt.print_stats()
    
    elif args.command == "comms-status":
        comms = CommsIntegration(WORKSPACE, args.sender)
        status = comms.get_comms_status()
        print("=" * 60)
        print("  AGENT COMMS INFRASTRUCTURE STATUS")
        print("=" * 60)
        for key, val in status.items():
            if isinstance(val, dict):
                print(f"  {key}:")
                for k2, v2 in val.items():
                    print(f"    {k2}: {v2}")
            else:
                print(f"  {key}: {val}")
    
    elif args.command == "mesh-matrix":
        from agent_mesh import AffinityGraph
        rt.convene(args.topic)
        graph = AffinityGraph.from_seats(rt.seats)
        graph.print_matrix()
        stats = graph.stats()
        print(f"\n  {stats['agents']} agents, {stats['edges']} edges")
        print(f"  Strong (>=0.3): {stats['strong_edges']}, "
              f"Medium (0.15-0.3): {stats['medium_edges']}, "
              f"Weak (<0.15): {stats['weak_edges']}")
        print(f"  Avg affinity: {stats['avg_affinity']:.3f}, "
              f"Max: {stats['max_affinity']:.3f}")


if __name__ == "__main__":
    main()
