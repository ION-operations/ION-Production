"""
AIM-OS Agent Neural Mesh — Intelligent Agent Communication Graph

Transforms the flat roundtable into a neural mesh where agents
communicate with their most related peers, forming a web of
overlapping context within their comfort zones.

Three core components:

    AffinityGraph    — Weighted edges between agents based on actual
                       vocabulary overlap in their domain contexts.
                       Replaces hardcoded SYSTEM_ADJACENCY with
                       empirically computed affinity scores.

    ComfortZone      — Each agent's confidence radius. Inside = speak
                       with authority. Edge = flag uncertainty, defer
                       to neighbor. Outside = stay silent.

    CascadeProtocol  — When an agent detects a question crosses their
                       domain boundary, they page the right neighbor
                       through comms. Questions cascade through the
                       mesh along the strongest affinity edges.

Usage:
    from roundtable import Roundtable
    from agent_mesh import AffinityGraph, MeshDiscussion

    rt = Roundtable()
    rt.convene("Architecture Review")

    # Build the affinity graph from loaded contexts
    graph = AffinityGraph.from_seats(rt.seats)
    print(graph.strongest_neighbors('cmc', top_k=3))
    # => [('hhni', 0.47), ('seg', 0.31), ('vif', 0.22)]

    # Run a mesh discussion (cascade mode)
    result = mesh_discuss(rt, graph, "How does memory flow?")
    print(result.cascade_trace)

Part of the AIM-OS AI Engine.
"""

import os
import re
import sys
import json
import time
import math
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Tuple

logger = logging.getLogger('ai_engine.agent_mesh')

# ===================================================================
#  HIERARCHY — Military-style rank tiers from comms doctrine
# ===================================================================
# Priority weights: higher rank = higher seed/cascade priority when
# affinity scores are close. Based on the AIM-OS comms doctrine ranks.
AGENT_HIERARCHY = {
    # Command tier — core infrastructure
    'cmc':     {'rank': 'command',    'tier': 1, 'priority': 1.0},
    'hhni':    {'rank': 'executive',  'tier': 2, 'priority': 0.9},
    'vif':     {'rank': 'executive',  'tier': 2, 'priority': 0.9},
    # Lead tier — orchestration & analysis
    'apoe':    {'rank': 'lead',       'tier': 3, 'priority': 0.8},
    'seg':     {'rank': 'lead',       'tier': 3, 'priority': 0.8},
    'cas':     {'rank': 'lead',       'tier': 3, 'priority': 0.8},
    'sdfcvf':  {'rank': 'lead',       'tier': 3, 'priority': 0.8},
    # Specialist tier — focused domains
    'tcs':     {'rank': 'specialist', 'tier': 4, 'priority': 0.7},
    'iis':     {'rank': 'specialist', 'tier': 4, 'priority': 0.7},
    'docs':    {'rank': 'specialist', 'tier': 4, 'priority': 0.7},
    'context': {'rank': 'specialist', 'tier': 4, 'priority': 0.7},
    'mcp':     {'rank': 'specialist', 'tier': 4, 'priority': 0.7},
}

def get_rank_priority(agent_id: str) -> float:
    """Get hierarchy priority for an agent (1.0 = highest)."""
    entry = AGENT_HIERARCHY.get(agent_id, {'priority': 0.5})
    return entry['priority']

def get_rank_label(agent_id: str) -> str:
    """Get the rank label for an agent."""
    entry = AGENT_HIERARCHY.get(agent_id, {'rank': 'worker'})
    return entry['rank']

# ═══════════════════════════════════════════════════════════
#  VOCABULARY EXTRACTION
# ═══════════════════════════════════════════════════════════

# Common words to ignore when computing domain overlap
STOP_WORDS = frozenset({
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'need', 'must', 'ought',
    'and', 'but', 'or', 'nor', 'not', 'so', 'yet', 'both', 'either',
    'neither', 'each', 'every', 'all', 'any', 'few', 'more', 'most',
    'other', 'some', 'such', 'than', 'too', 'very', 'just', 'also',
    'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'about',
    'as', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'between', 'under', 'over', 'out', 'up', 'down',
    'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
    'their', 'we', 'us', 'our', 'you', 'your', 'he', 'she', 'him', 'her',
    'if', 'then', 'else', 'when', 'where', 'how', 'what', 'which', 'who',
    'whom', 'why', 'while', 'there', 'here', 'only', 'now',
    'true', 'false', 'none', 'null', 'def', 'class', 'return', 'import',
    'self', 'str', 'int', 'list', 'dict', 'type', 'line', 'lines',
    'file', 'path', 'name', 'value', 'data', 'status', 'using',
    'based', 'used', 'uses', 'system', 'systems', 'see', 'new',
})

# Domain-specific high-value terms (boost their weight)
DOMAIN_TERMS = frozenset({
    'atom', 'atoms', 'memory', 'memories', 'store', 'storage', 'persist',
    'retrieve', 'retrieval', 'index', 'indexed', 'hierarchy', 'fractal',
    'confidence', 'kappa', 'witness', 'envelope', 'provenance',
    'evidence', 'graph', 'node', 'synthesis', 'contradiction',
    'orchestration', 'workflow', 'pipeline', 'execution', 'plan',
    'convergence', 'parity', 'quartet', 'blast', 'radius',
    'cognitive', 'analysis', 'drift', 'attention', 'narrowing',
    'timeline', 'context', 'temporal', 'bitemporal', 'checkpoint',
    'intuition', 'pattern', 'meta', 'evolution', 'predictor',
    'dvns', 'force', 'gravity', 'repulsion', 'elastic', 'damping',
    'compressor', 'token', 'tokens', 'budget', 'compress',
    'documentation', 'docs', 'coverage', 'parity', 'enrich',
    'mcp', 'tool', 'tools', 'health', 'diagnostic', 'protocol',
})


def extract_vocabulary(text: str) -> Counter:
    """Extract weighted vocabulary from text.
    
    Returns a Counter of significant words with weights:
    - Regular words: weight 1
    - Domain terms: weight 3 (boosted)
    - Words appearing in headers: weight 2
    """
    vocab = Counter()
    
    # Extract words
    words = re.findall(r'[a-z][a-z_]+', text.lower())
    
    for word in words:
        if word in STOP_WORDS or len(word) < 3:
            continue
        weight = 3 if word in DOMAIN_TERMS else 1
        vocab[word] += weight
    
    # Boost header words
    headers = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
    for header in headers:
        header_words = re.findall(r'[a-z][a-z_]+', header.lower())
        for w in header_words:
            if w not in STOP_WORDS and len(w) >= 3:
                vocab[w] += 2
    
    return vocab


def jaccard_weighted(vocab_a: Counter, vocab_b: Counter) -> float:
    """Compute weighted Jaccard similarity between two vocabularies.
    
    Uses min/max formulation for weighted sets:
    J(A,B) = Σmin(wA[i], wB[i]) / Σmax(wA[i], wB[i])
    """
    all_words = set(vocab_a.keys()) | set(vocab_b.keys())
    if not all_words:
        return 0.0
    
    numerator = sum(min(vocab_a.get(w, 0), vocab_b.get(w, 0)) for w in all_words)
    denominator = sum(max(vocab_a.get(w, 0), vocab_b.get(w, 0)) for w in all_words)
    
    return numerator / denominator if denominator > 0 else 0.0


# ═══════════════════════════════════════════════════════════
#  AFFINITY GRAPH
# ═══════════════════════════════════════════════════════════

@dataclass
class AffinityEdge:
    """A weighted edge between two agents."""
    agent_a: str
    agent_b: str
    weight: float          # 0.0 to 1.0 (Jaccard similarity)
    shared_terms: int      # number of shared vocabulary terms
    top_shared: List[str]  # most important shared terms


@dataclass
class AgentNode:
    """An agent in the affinity graph."""
    system_id: str
    agent_name: str
    vocab: Counter = field(default_factory=Counter)
    vocab_size: int = 0
    # Comfort zone metrics
    domain_keywords: Set[str] = field(default_factory=set)
    comfort_radius: float = 0.0  # how broad their expertise is


class AffinityGraph:
    """Weighted graph of agent-to-agent affinity based on content overlap.
    
    Replaces the hardcoded SYSTEM_ADJACENCY with empirically computed
    affinity scores. Each edge weight represents how much vocabulary
    two agents share — their "comfort zone overlap."
    
    Usage:
        graph = AffinityGraph.from_seats(roundtable.seats)
        
        # Who knows the most about what CMC knows?
        neighbors = graph.strongest_neighbors('cmc', top_k=3)
        # => [('hhni', 0.47), ('seg', 0.31), ('vif', 0.22)]
        
        # How connected are these two agents?
        score = graph.affinity('cmc', 'hhni')
        # => 0.47
        
        # Which agents should handle this question?
        cluster = graph.route_question("How does memory retrieval work?")
        # => ['cmc', 'hhni', 'seg'] (ordered by relevance)
    """
    
    def __init__(self):
        self.nodes: Dict[str, AgentNode] = {}
        self.edges: Dict[Tuple[str, str], AffinityEdge] = {}
        self._adjacency: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    
    @classmethod
    def from_seats(cls, seats: list) -> 'AffinityGraph':
        """Build affinity graph from roundtable seats.
        
        Computes weighted Jaccard similarity between every pair
        of agents based on their domain context vocabulary.
        """
        graph = cls()
        
        # 1. Build vocabulary for each agent
        for seat in seats:
            text = seat.domain_context + "\n" + seat.overlap_context
            vocab = extract_vocabulary(text)
            
            # Identify domain-specific keywords (top 50 by weight)
            top_words = {w for w, _ in vocab.most_common(50)}
            
            node = AgentNode(
                system_id=seat.system_id,
                agent_name=seat.agent_name,
                vocab=vocab,
                vocab_size=len(vocab),
                domain_keywords=top_words,
                comfort_radius=len(vocab) / 500.0,  # normalized
            )
            graph.nodes[seat.system_id] = node
        
        # 2. Compute pairwise affinity
        system_ids = list(graph.nodes.keys())
        for i, id_a in enumerate(system_ids):
            for id_b in system_ids[i+1:]:
                node_a = graph.nodes[id_a]
                node_b = graph.nodes[id_b]
                
                weight = jaccard_weighted(node_a.vocab, node_b.vocab)
                
                # Find shared high-value terms
                shared = set(node_a.vocab.keys()) & set(node_b.vocab.keys())
                shared_domain = shared & DOMAIN_TERMS
                top_shared = sorted(shared_domain,
                                   key=lambda w: node_a.vocab[w] + node_b.vocab[w],
                                   reverse=True)[:10]
                
                edge = AffinityEdge(
                    agent_a=id_a,
                    agent_b=id_b,
                    weight=weight,
                    shared_terms=len(shared),
                    top_shared=top_shared,
                )
                
                graph.edges[(id_a, id_b)] = edge
                graph.edges[(id_b, id_a)] = edge
                graph._adjacency[id_a].append((id_b, weight))
                graph._adjacency[id_b].append((id_a, weight))
        
        # 3. Sort adjacency lists by weight (strongest first)
        for agent_id in graph._adjacency:
            graph._adjacency[agent_id].sort(key=lambda x: -x[1])
        
        return graph
    
    def affinity(self, agent_a: str, agent_b: str) -> float:
        """Get affinity score between two agents."""
        if agent_a == agent_b:
            return 1.0
        key = (agent_a, agent_b)
        if key in self.edges:
            return self.edges[key].weight
        return 0.0
    
    def strongest_neighbors(self, agent_id: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Get the top-k strongest neighbors for an agent."""
        return self._adjacency.get(agent_id, [])[:top_k]
    
    def shared_terms(self, agent_a: str, agent_b: str) -> List[str]:
        """Get the top shared domain terms between two agents."""
        key = (agent_a, agent_b)
        if key in self.edges:
            return self.edges[key].top_shared
        return []
    
    def route_question(self, question: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Route a question to the most relevant agents.
        
        Uses vocabulary overlap between the question and each
        agent's domain to find the best cluster. Higher-ranked
        agents get a small tiebreaker boost (hierarchy-aware).
        """
        q_vocab = extract_vocabulary(question)
        
        scores = []
        for agent_id, node in self.nodes.items():
            # Compute question-to-agent affinity
            score = jaccard_weighted(q_vocab, node.vocab)
            
            # Boost if question mentions the system directly
            q_lower = question.lower()
            if agent_id in q_lower or node.agent_name.lower() in q_lower:
                score += 0.3
            
            # Hierarchy tiebreaker: up to 10% boost for higher ranks
            rank_priority = get_rank_priority(agent_id)
            score += score * 0.1 * rank_priority
            
            scores.append((agent_id, min(score, 1.0)))
        
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]
    
    def cluster_around(self, seed_agents: List[str], depth: int = 1,
                        min_affinity: float = 0.15) -> List[Tuple[str, float]]:
        """Expand from seed agents along affinity edges.
        
        Returns the cluster of agents reachable within `depth` hops
        with affinity above `min_affinity`.
        """
        visited = {}
        frontier = [(a, 1.0) for a in seed_agents]
        
        for _ in range(depth + 1):
            next_frontier = []
            for agent_id, score in frontier:
                if agent_id in visited:
                    visited[agent_id] = max(visited[agent_id], score)
                    continue
                visited[agent_id] = score
                
                # Expand neighbors
                for neighbor_id, edge_weight in self._adjacency.get(agent_id, []):
                    if neighbor_id not in visited and edge_weight >= min_affinity:
                        propagated = score * edge_weight
                        next_frontier.append((neighbor_id, propagated))
            
            frontier = next_frontier
        
        result = sorted(visited.items(), key=lambda x: -x[1])
        return result
    
    def print_matrix(self):
        """Print the affinity matrix."""
        ids = sorted(self.nodes.keys())
        
        # Header
        header = f"{'':>10s}"
        for sid in ids:
            header += f"  {sid:>6s}"
        print(header)
        print("-" * len(header))
        
        for id_a in ids:
            row = f"  {id_a:>8s}"
            for id_b in ids:
                score = self.affinity(id_a, id_b)
                if id_a == id_b:
                    row += f"  {'-':>6s}"
                elif score >= 0.3:
                    row += f"  \033[92m{score:>5.2f}\033[0m "
                elif score >= 0.15:
                    row += f"  \033[93m{score:>5.2f}\033[0m "
                else:
                    row += f"  {score:>5.2f} "
            print(row)
    
    def stats(self) -> dict:
        """Return graph statistics."""
        # Edges are stored bidirectionally — deduplicate by sorted key
        seen = set()
        weights = []
        for (a, b), edge in self.edges.items():
            key = tuple(sorted((a, b)))
            if key not in seen:
                seen.add(key)
                weights.append(edge.weight)
        return {
            'agents': len(self.nodes),
            'edges': len(weights),
            'avg_affinity': sum(weights) / len(weights) if weights else 0,
            'max_affinity': max(weights) if weights else 0,
            'min_affinity': min(weights) if weights else 0,
            'strong_edges': sum(1 for w in weights if w >= 0.3),
            'medium_edges': sum(1 for w in weights if 0.15 <= w < 0.3),
            'weak_edges': sum(1 for w in weights if w < 0.15),
        }


# ═══════════════════════════════════════════════════════════
#  COMFORT ZONES
# ═══════════════════════════════════════════════════════════

@dataclass
class ComfortAssessment:
    """Assessment of how comfortable an agent is with a question."""
    agent_id: str
    agent_name: str
    zone: str              # 'core', 'edge', 'outside'
    coverage: float        # 0-1: what fraction of question falls in their domain
    confidence: float      # 0-1: how confidently they can answer
    missing_terms: List[str]  # question terms outside their domain
    defer_to: List[str]    # agents better suited for the missing terms


class ComfortZone:
    """Defines each agent's area of expertise and confidence boundaries.
    
    Three zones:
        core    (coverage > 0.6) — Agent speaks with full authority
        edge    (0.2 < coverage ≤ 0.6) — Agent contributes but flags gaps
        outside (coverage ≤ 0.2) — Agent defers to better-suited peer
    
    Usage:
        zone = ComfortZone(graph)
        assessment = zone.assess('cmc', "How does memory storage work?")
        # => ComfortAssessment(zone='core', coverage=0.85, ...)
        
        assessment = zone.assess('cmc', "How does HHNI compress tokens?")
        # => ComfortAssessment(zone='edge', coverage=0.35, defer_to=['hhni'])
    """
    
    CORE_THRESHOLD = 0.6
    EDGE_THRESHOLD = 0.2
    
    def __init__(self, graph: AffinityGraph):
        self.graph = graph
    
    def assess(self, agent_id: str, question: str) -> ComfortAssessment:
        """Assess how comfortable an agent is with a question."""
        node = self.graph.nodes.get(agent_id)
        if not node:
            return ComfortAssessment(
                agent_id=agent_id, agent_name=f"AGENT-{agent_id.upper()}",
                zone='outside', coverage=0.0, confidence=0.0,
                missing_terms=[], defer_to=[],
            )
        
        q_vocab = extract_vocabulary(question)
        q_significant = {w for w in q_vocab if q_vocab[w] >= 1}
        
        if not q_significant:
            return ComfortAssessment(
                agent_id=agent_id, agent_name=node.agent_name,
                zone='outside', coverage=0.0, confidence=0.0,
                missing_terms=[], defer_to=[],
            )
        
        # Compute coverage: what fraction of question terms are in domain
        covered = q_significant & set(node.vocab.keys())
        missing = q_significant - covered
        coverage = len(covered) / len(q_significant)
        
        # Determine zone
        if coverage > self.CORE_THRESHOLD:
            zone = 'core'
            confidence = min(coverage * 1.2, 1.0)
        elif coverage > self.EDGE_THRESHOLD:
            zone = 'edge'
            confidence = coverage * 0.8
        else:
            zone = 'outside'
            confidence = coverage * 0.3
        
        # Find who to defer to for missing terms
        defer_to = []
        if missing and zone != 'core':
            # Find agents whose domain covers the missing terms
            for other_id, other_node in self.graph.nodes.items():
                if other_id == agent_id:
                    continue
                other_covered = missing & set(other_node.vocab.keys())
                if len(other_covered) > len(missing) * 0.3:
                    defer_to.append(other_id)
            
            # Sort by affinity (prefer stronger neighbors)
            defer_to.sort(
                key=lambda x: self.graph.affinity(agent_id, x),
                reverse=True
            )
        
        return ComfortAssessment(
            agent_id=agent_id,
            agent_name=node.agent_name,
            zone=zone,
            coverage=coverage,
            confidence=confidence,
            missing_terms=sorted(missing)[:10],
            defer_to=defer_to[:3],
        )
    
    def assess_all(self, question: str) -> List[ComfortAssessment]:
        """Assess all agents for a question, sorted by confidence."""
        assessments = []
        for agent_id in self.graph.nodes:
            assessments.append(self.assess(agent_id, question))
        assessments.sort(key=lambda a: -a.confidence)
        return assessments


# ═══════════════════════════════════════════════════════════
#  CASCADE PROTOCOL
# ═══════════════════════════════════════════════════════════

@dataclass
class CascadeStep:
    """One step in a cascade chain."""
    agent_id: str
    agent_name: str
    zone: str
    confidence: float
    paged_by: Optional[str] = None   # who pulled this agent in
    reason: str = ""                  # why they were paged
    contribution_preview: str = ""    # first 200 chars of what they'd say


@dataclass
class CascadeTrace:
    """Full trace of a cascade discussion."""
    question: str
    steps: List[CascadeStep] = field(default_factory=list)
    seed_agents: List[str] = field(default_factory=list)
    cascaded_agents: List[str] = field(default_factory=list)
    total_agents: int = 0
    max_depth_reached: int = 0
    
    @property
    def summary(self) -> str:
        lines = [f"Cascade: {len(self.seed_agents)} seed -> {len(self.steps)} total agents"]
        lines.append(f"Depth: {self.max_depth_reached}")
        for step in self.steps:
            prefix = "  [SEED]" if step.paged_by is None else f"  <-{step.paged_by}"
            lines.append(
                f"{prefix} {step.agent_name} "
                f"[{step.zone}] conf={step.confidence:.2f}"
                f"{(' -- ' + step.reason) if step.reason else ''}"
            )
        return "\n".join(lines)


class CascadeProtocol:
    """Routes questions through the agent mesh via cascading pages.
    
    Instead of broadcasting to all agents, the cascade protocol:
    1. Routes the question to the top-k most relevant agents (seeds)
    2. Each seed assesses their comfort zone
    3. If they're at the EDGE, they page their strongest neighbor
       who covers the missing terms
    4. Paged agents can page further (up to max_depth)
    5. Agents OUTSIDE their comfort zone stay silent
    
    This creates natural information flow along affinity edges,
    with each agent contributing within their comfort zone.
    
    Usage:
        protocol = CascadeProtocol(graph, comfort_zone)
        trace = protocol.cascade("How does memory retrieval work?")
        print(trace.summary)
    """
    
    def __init__(self, graph: AffinityGraph, comfort: ComfortZone,
                 max_seeds: int = 3, max_depth: int = 2,
                 min_confidence: float = 0.1):
        self.graph = graph
        self.comfort = comfort
        self.max_seeds = max_seeds
        self.max_depth = max_depth
        self.min_confidence = min_confidence
    
    def cascade(self, question: str, seats_map: Optional[Dict] = None) -> CascadeTrace:
        """Run the cascade protocol for a question.
        
        Args:
            question: The discussion question
            seats_map: Optional dict of system_id -> Seat for contribution preview
        
        Returns:
            CascadeTrace with the full cascade chain
        """
        trace = CascadeTrace(question=question)
        
        # 1. Find seed agents via affinity routing
        routed = self.graph.route_question(question, top_k=self.max_seeds)
        seed_ids = [agent_id for agent_id, score in routed if score > 0]
        
        if not seed_ids:
            # Fallback: use all agents
            seed_ids = list(self.graph.nodes.keys())[:self.max_seeds]
        
        trace.seed_agents = seed_ids
        
        # 2. Process seeds and cascade
        visited = set()
        queue = [(agent_id, None, "", 0) for agent_id in seed_ids]
        # (agent_id, paged_by, reason, depth)
        
        while queue:
            agent_id, paged_by, reason, depth = queue.pop(0)
            
            if agent_id in visited:
                continue
            visited.add(agent_id)
            
            # Assess comfort
            assessment = self.comfort.assess(agent_id, question)
            
            if assessment.confidence < self.min_confidence:
                continue
            
            # Build contribution preview
            preview = ""
            if seats_map and agent_id in seats_map:
                seat = seats_map[agent_id]
                preview = f"{seat.domain_context_tokens:,} tokens of {seat.system_name} context"
            
            step = CascadeStep(
                agent_id=agent_id,
                agent_name=assessment.agent_name,
                zone=assessment.zone,
                confidence=assessment.confidence,
                paged_by=f"AGENT-{paged_by.upper()}" if paged_by else None,
                reason=reason,
                contribution_preview=preview,
            )
            trace.steps.append(step)
            trace.max_depth_reached = max(trace.max_depth_reached, depth)
            
            # 3. If at the edge, page neighbors for missing terms
            if assessment.zone == 'edge' and depth < self.max_depth:
                for defer_id in assessment.defer_to:
                    if defer_id not in visited:
                        # Build reason from missing terms
                        missing = assessment.missing_terms[:5]
                        r = f"covers [{', '.join(missing)}]"
                        queue.append((defer_id, agent_id, r, depth + 1))
                        trace.cascaded_agents.append(defer_id)
            
            # Core agents can also pull in strong neighbors for synthesis
            elif assessment.zone == 'core' and depth < self.max_depth:
                top_neighbors = self.graph.strongest_neighbors(agent_id, top_k=2)
                for neighbor_id, edge_weight in top_neighbors:
                    if neighbor_id not in visited and edge_weight >= 0.2:
                        shared = self.graph.shared_terms(agent_id, neighbor_id)[:3]
                        r = f"strong affinity ({edge_weight:.2f}), shared: [{', '.join(shared)}]"
                        queue.append((neighbor_id, agent_id, r, depth + 1))
        
        trace.total_agents = len(trace.steps)
        return trace


# ═══════════════════════════════════════════════════════════
#  MESH DISCUSSION (integrates with Roundtable)
# ═══════════════════════════════════════════════════════════

@dataclass
class MeshContribution:
    """An agent's contribution in a mesh discussion."""
    agent_id: str
    agent_name: str
    zone: str
    confidence: float
    relevance_score: float
    paged_by: Optional[str]
    content: str
    tokens_used: int


@dataclass 
class MeshDiscussion:
    """Result of a mesh-routed discussion."""
    question: str
    cascade_trace: CascadeTrace
    contributions: List[MeshContribution] = field(default_factory=list)
    unified_answer: str = ""
    graph_stats: dict = field(default_factory=dict)
    elapsed_ms: float = 0.0
    
    @property
    def minutes(self) -> str:
        lines = []
        lines.append("# Mesh Discussion Minutes\n")
        lines.append(f"**Question:** {self.question}")
        lines.append(f"**Routing:** {len(self.cascade_trace.seed_agents)} seeds -> "
                     f"{self.cascade_trace.total_agents} participants "
                     f"(depth {self.cascade_trace.max_depth_reached})")
        lines.append(f"**Duration:** {self.elapsed_ms:.0f}ms\n")
        
        # Cascade trace
        lines.append("## Cascade Trace\n")
        lines.append("```")
        lines.append(self.cascade_trace.summary)
        lines.append("```\n")
        
        # Contributions by zone
        core = [c for c in self.contributions if c.zone == 'core']
        edge = [c for c in self.contributions if c.zone == 'edge']
        
        if core:
            lines.append(f"## Core Contributors ({len(core)})\n")
            for c in sorted(core, key=lambda x: -x.confidence):
                lines.append(f"### {c.agent_name} (conf={c.confidence:.2f})")
                lines.append(c.content[:1500])
                lines.append("")
        
        if edge:
            lines.append(f"## Edge Contributors ({len(edge)})\n")
            for c in sorted(edge, key=lambda x: -x.confidence):
                paged = f" <- paged by {c.paged_by}" if c.paged_by else ""
                lines.append(f"### {c.agent_name} (conf={c.confidence:.2f}){paged}")
                lines.append(c.content[:1000])
                lines.append("")
        
        if self.unified_answer:
            lines.append("## Synthesized Answer\n")
            lines.append(self.unified_answer)
        
        return "\n".join(lines)


def mesh_discuss(roundtable, graph: AffinityGraph, question: str,
                 max_seeds: int = 3, max_depth: int = 2) -> MeshDiscussion:
    """Run a mesh-routed discussion through the roundtable.
    
    Instead of the flat discuss() which broadcasts to all agents,
    this routes through the affinity graph using cascade protocol.
    
    Args:
        roundtable: A convened Roundtable instance
        graph: AffinityGraph built from the roundtable seats
        question: The question to discuss
        max_seeds: How many agents to seed the cascade with
        max_depth: How deep the cascade can go
    
    Returns:
        MeshDiscussion with cascade trace and contributions
    """
    start = time.time()
    
    # Build lookup maps
    seats_map = {s.system_id: s for s in roundtable.seats}
    
    # Create comfort zone analyzer
    comfort = ComfortZone(graph)
    
    # Run cascade protocol
    protocol = CascadeProtocol(
        graph, comfort,
        max_seeds=max_seeds,
        max_depth=max_depth,
    )
    trace = protocol.cascade(question, seats_map)
    
    # Build contributions from participating agents
    discussion = MeshDiscussion(
        question=question,
        cascade_trace=trace,
        graph_stats=graph.stats(),
    )
    
    for step in trace.steps:
        seat = seats_map.get(step.agent_id)
        if not seat:
            continue
        
        # Lightweight mesh contribution (no heavy line scanning)
        content_parts = [
            f"**{seat.agent_name}** -- {seat.system_name}",
            f"Domain: {seat.domain_context_tokens:,} tokens",
            f"Confidence: {step.confidence:.2f}",
        ]
        preview = [l for l in seat.domain_context.split('\n')
                  if l.strip() and len(l.strip()) > 10][:15]
        if preview:
            content_parts.append('\n'.join(preview))
        mesh_contrib = MeshContribution(
            agent_id=step.agent_id,
            agent_name=step.agent_name,
            zone=step.zone,
            confidence=step.confidence,
            relevance_score=step.confidence,
            paged_by=step.paged_by,
            content='\n'.join(content_parts),
            tokens_used=seat.total_context_tokens,
        )
        discussion.contributions.append(mesh_contrib)
    
    # Synthesize
    if discussion.contributions:
        parts = [f"Mesh discussion via {len(trace.seed_agents)} seeds, "
                 f"{trace.total_agents} agents participated "
                 f"(cascade depth {trace.max_depth_reached}):\n"]
        
        for c in sorted(discussion.contributions, key=lambda x: -x.confidence)[:5]:
            zone_label = f"[{c.zone.upper()}]"
            paged = f" <- {c.paged_by}" if c.paged_by else " [SEED]"
            parts.append(f"**{c.agent_name}** {zone_label}{paged} "
                        f"(conf={c.confidence:.2f}):")
            # Extract key knowledge
            lines = c.content.split('\n')
            key = [l for l in lines if l.strip() and 'tokens of context' not in l 
                   and 'Relevance:' not in l and not l.startswith('**AGENT')][:8]
            parts.append("  " + "\n  ".join(key))
        
        discussion.unified_answer = "\n\n".join(parts)
    
    # Record contributions for dynamic hierarchy tracking
    try:
        from mesh_visualizer import record_contribution
        for c in discussion.contributions:
            record_contribution(c.agent_id, c.zone, c.confidence, question)
    except Exception:
        pass  # Don't fail discussion if tracking fails
    
    discussion.elapsed_ms = (time.time() - start) * 1000
    return discussion


# ═══════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════

def main():
    import argparse
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    SCRIPTS_DIR = os.path.dirname(SCRIPT_DIR)
    WORKSPACE = os.path.dirname(SCRIPTS_DIR)
    for p in [WORKSPACE, SCRIPTS_DIR, SCRIPT_DIR]:
        if p not in sys.path:
            sys.path.insert(0, p)
    
    from roundtable import Roundtable, RoundtableConfig
    
    parser = argparse.ArgumentParser(description="AIM-OS Agent Neural Mesh")
    parser.add_argument("command", choices=["matrix", "neighbors", "route",
                                            "comfort", "cascade", "discuss"],
                       help="Command to run")
    parser.add_argument("--question", "-q", default="",
                       help="Question to analyze/discuss")
    parser.add_argument("--agent", "-a", default="",
                       help="Agent system ID (for neighbors/comfort)")
    parser.add_argument("--top-k", type=int, default=3,
                       help="Number of results")
    parser.add_argument("--depth", type=int, default=2,
                       help="Cascade depth")
    args = parser.parse_args()
    
    # Convene roundtable
    rt = Roundtable()
    rt.convene("Mesh Analysis")
    
    # Build affinity graph
    graph = AffinityGraph.from_seats(rt.seats)
    
    if args.command == "matrix":
        print("\n  AGENT AFFINITY MATRIX\n")
        graph.print_matrix()
        stats = graph.stats()
        print(f"\n  {stats['agents']} agents, {stats['edges']} edges")
        print(f"  Strong (≥0.3): {stats['strong_edges']}, "
              f"Medium (0.15-0.3): {stats['medium_edges']}, "
              f"Weak (<0.15): {stats['weak_edges']}")
        print(f"  Avg affinity: {stats['avg_affinity']:.3f}, "
              f"Max: {stats['max_affinity']:.3f}")
    
    elif args.command == "neighbors":
        agent = args.agent or "cmc"
        neighbors = graph.strongest_neighbors(agent, top_k=args.top_k)
        print(f"\n  Strongest neighbors of AGENT-{agent.upper()}:\n")
        for nid, weight in neighbors:
            shared = graph.shared_terms(agent, nid)
            print(f"  {weight:.3f}  AGENT-{nid.upper()}")
            if shared:
                print(f"         shared: {', '.join(shared[:5])}")
    
    elif args.command == "route":
        if not args.question:
            print("Error: --question required")
            return
        routed = graph.route_question(args.question, top_k=args.top_k)
        print(f"\n  Best agents for: \"{args.question[:60]}...\"\n")
        for aid, score in routed:
            print(f"  {score:.3f}  AGENT-{aid.upper()}")
    
    elif args.command == "comfort":
        if not args.question:
            print("Error: --question required")
            return
        comfort = ComfortZone(graph)
        assessments = comfort.assess_all(args.question)
        print(f"\n  Comfort zones for: \"{args.question[:60]}...\"\n")
        for a in assessments:
            zone_color = {'core': '\033[92m', 'edge': '\033[93m', 'outside': '\033[91m'}
            reset = '\033[0m'
            color = zone_color.get(a.zone, '')
            print(f"  {color}{a.zone:>7s}{reset}  {a.agent_name:20s} "
                  f"coverage={a.coverage:.2f}  conf={a.confidence:.2f}")
            if a.defer_to:
                print(f"           defer -> {', '.join(a.defer_to[:3])}")
    
    elif args.command == "cascade":
        if not args.question:
            print("Error: --question required")
            return
        comfort = ComfortZone(graph)
        protocol = CascadeProtocol(graph, comfort,
                                    max_seeds=args.top_k,
                                    max_depth=args.depth)
        seats_map = {s.system_id: s for s in rt.seats}
        trace = protocol.cascade(args.question, seats_map)
        print(f"\n  CASCADE TRACE\n")
        print(trace.summary)
    
    elif args.command == "discuss":
        if not args.question:
            print("Error: --question required")
            return
        result = mesh_discuss(rt, graph, args.question,
                            max_seeds=args.top_k, max_depth=args.depth)
        print(result.minutes)


if __name__ == "__main__":
    main()
