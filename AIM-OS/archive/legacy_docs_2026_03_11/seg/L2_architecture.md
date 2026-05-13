---
id: seg_T2_architecture
level: L2
system: SEG
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# SEG – T2 Architecture (≈2000 words)

## System Overview

**SEG (Shared Evidence Graph)** transforms scattered evidence into a unified, temporal, contradiction-aware knowledge graph. Instead of facts living in isolated documents, SEG treats evidence as a graph where every claim, source, derivation, and agent becomes a node, and every relationship (supports, contradicts, derives, witnesses) becomes an edge.

**Core Architectural Principles:**
1. **Graph-First Design:** Evidence as nodes/edges, not documents or tables
2. **Bitemporal Foundation:** Transaction time (when recorded) + Valid time (when true) enable time-travel queries
3. **Provenance Discipline:** Every claim must have source, every derivation must have inputs
4. **Automatic Contradiction Detection:** Semantic similarity + stance analysis finds conflicts automatically
5. **Standards Compliance:** JSON-LD export, RDF serialization, SHACL validation for interoperability

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              SHARED EVIDENCE GRAPH (SEG)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              GRAPH SCHEMA LAYER                       │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Node Types: Claim, Source, Derivation, Agent        │    │
│  │  Edge Types: supports, contradicts, derives,         │    │
│  │             witnesses, cites                         │    │
│  │  Bitemporal Fields: created_at (TT), valid_from/to   │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              GRAPH STORE                              │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Backend: NetworkX (dev) / Neo4j (prod)              │    │
│  │  Indexes: Node ID, Edge Type, Temporal Range         │    │
│  │  Operations: Add/Update/Query/Delete                 │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           BITEMPORAL STORAGE ENGINE                   │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Transaction Time: When recorded in SEG              │    │
│  │  Valid Time: When true in reality                    │    │
│  │  Temporal Indexes: Valid time ranges, TT snapshots  │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        CONTRADICTION DETECTION ENGINE                  │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Semantic Similarity: Embedding-based (cosine)       │    │
│  │  Stance Detection: Positive/Negative/Neutral          │    │
│  │  Conflict Analysis: Contradiction score calculation  │    │
│  │  Auto-Edge Creation: "contradicts" edges            │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            QUERY ENGINE                               │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Lineage Tracing: Backward/Forward traversal         │    │
│  │  Temporal Queries: As-of-time snapshots              │    │
│  │  Provenance Chains: Source-to-claim paths           │    │
│  │  Contradiction Queries: Find conflicts               │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           EXPORT SYSTEM                              │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  JSON-LD: W3C standard linked data                   │    │
│  │  RDF: Triple store compatibility                    │    │
│  │  SHACL: Shape validation                            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Graph Schema Layer

**Purpose:** Define node and edge types with bitemporal support

**Node Types (4):**

**ClaimNode:**
```python
@dataclass
class ClaimNode:
    """Factual assertion (evidence)"""
    id: str                           # "claim:auth_jwt_001"
    type: str = "claim"
    content: str                      # "OAuth2 uses JWT tokens"
    embedding: Optional[np.ndarray]   # For semantic similarity
    confidence: float = 1.0           # How confident (0-1)
    stance: str = "positive"          # "positive" | "negative" | "neutral"
    
    # Bitemporal
    created_at: datetime              # Transaction time (TT)
    valid_from: datetime              # Valid time start (VT)
    valid_to: Optional[datetime]      # Valid time end (VT, None = still valid)
    
    # Provenance
    source_ids: List[str]             # Where it came from
    vif_witness_id: Optional[str]     # VIF witness that recorded it
    tags: List[str] = []              # Categories/topics
    metadata: Dict[str, Any] = {}      # Additional data
```

**SourceNode:**
```python
@dataclass
class SourceNode:
    """Origin of evidence"""
    id: str                           # "source:vif_abc123"
    type: str = "source"
    source_type: str                  # "vif_witness" | "document" | "user_input" | "external_api"
    reference: str                    # VIF ID, document path, user ID, API endpoint
    authority_score: float = 0.5      # How trustworthy (0-1)
    verified: bool = False            # Has this been verified?
    
    # Bitemporal
    created_at: datetime              # TT
    valid_from: datetime              # VT start
    valid_to: Optional[datetime] = None  # VT end
```

**DerivationNode:**
```python
@dataclass
class DerivationNode:
    """How claim was derived"""
    id: str                           # "derivation:apoe_plan_xyz"
    type: str = "derivation"
    method: str                       # "apoe_execution" | "inference_chain" | "computation"
    inputs: List[str]                 # Input claim/source IDs
    outputs: List[str]                # Output claim IDs
    reasoning: str                     # Human-readable explanation
    confidence: float                 # How confident in derivation (0-1)
    
    # APOE-specific
    apoe_plan_id: Optional[str]       # Reference to APOE execution
    vif_trace: List[str]              # VIF witnesses for each step
    
    # Bitemporal
    created_at: datetime              # TT
```

**AgentNode:**
```python
@dataclass
class AgentNode:
    """Who/what created evidence"""
    id: str                           # "agent:user_john" | "agent:gpt4_turbo"
    type: str = "agent"
    agent_type: str                   # "human" | "ai_model" | "system"
    model_id: Optional[str]           # If AI: "gpt-4-turbo"
    user_id: Optional[str]            # If human: "john@example.com"
    authority_score: float = 0.5      # Trustworthiness (0-1)
    
    created_at: datetime              # TT
```

**Edge Types (5):**

**supports:**
```python
@dataclass
class SupportsEdge:
    """Evidence backs up claim"""
    id: str
    type: str = "supports"
    source_node_id: str               # Source or claim that supports
    target_node_id: str               # Claim being supported
    weight: float = 1.0               # Strength of support (0-1)
    created_at: datetime
```

**contradicts:**
```python
@dataclass
class ContradictsEdge:
    """Evidence conflicts with claim"""
    id: str
    type: str = "contradicts"
    source_node_id: str               # Claim A
    target_node_id: str               # Claim B (conflicts with A)
    similarity: float                 # How semantically similar (0-1)
    contradiction_score: float        # How contradictory (0-1)
    detected_at: datetime             # When contradiction found
```

**derives:**
```python
@dataclass
class DerivesEdge:
    """Claim produced from others"""
    id: str
    type: str = "derives"
    source_node_id: str               # Derivation node
    target_node_id: str               # Resulting claim
    confidence: float                 # Confidence in derivation (0-1)
    created_at: datetime
```

**witnesses:**
```python
@dataclass
class WitnessesEdge:
    """VIF records claim"""
    id: str
    type: str = "witnesses"
    source_node_id: str               # Source (VIF witness)
    target_node_id: str               # Claim being witnessed
    vif_id: str                       # Reference to full VIF witness
    created_at: datetime
```

**cites:**
```python
@dataclass
class CitesEdge:
    """Reference to source"""
    id: str
    type: str = "cites"
    source_node_id: str               # Claim
    target_node_id: str               # Source
    created_at: datetime
```

### 2. Graph Store

**Purpose:** Persistent storage for nodes and edges with multiple backend options

**Backend Options:**

**NetworkX (Development):**
- In-memory graph storage
- Fast for small graphs (<100K nodes)
- No persistence (data lost on restart)
- Good for testing and prototyping

**Neo4j (Production):**
- Production graph database
- Handles millions of nodes/edges
- ACID transactions, persistence
- Cypher query language
- Required for production deployments

**Graph Store Operations:**
```python
class GraphStore:
    """Interface for graph storage backends"""
    
    def add_node(self, node: SEGNode) -> None:
        """Add node to graph"""
        pass
    
    def add_edge(self, edge: SEGEdge) -> None:
        """Add edge to graph"""
        pass
    
    def get_node(self, node_id: str) -> Optional[SEGNode]:
        """Retrieve node by ID"""
        pass
    
    def get_nodes_by_type(self, node_type: str) -> List[SEGNode]:
        """Get all nodes of specified type"""
        pass
    
    def get_incoming_edges(self, node_id: str) -> List[SEGEdge]:
        """Get edges pointing to node"""
        pass
    
    def get_outgoing_edges(self, node_id: str) -> List[SEGEdge]:
        """Get edges from node"""
        pass
    
    def query_cypher(self, cypher: str, params: Dict = None) -> List[Dict]:
        """Run Cypher query (Neo4j only)"""
        pass
```

**Indexing Strategy:**
- **Node ID Index:** Fast lookup by ID (hash map)
- **Type Index:** Fast lookup by node/edge type (hash map)
- **Temporal Index:** B-tree for valid time ranges (enables as-of queries)
- **Embedding Index:** Vector similarity search (for contradiction detection)

### 3. Bitemporal Storage Engine

**Purpose:** Enable time-travel queries with transaction time and valid time

**Two Independent Timelines:**

**Transaction Time (TT):** When fact was recorded in SEG  
**Valid Time (VT):** When fact was true in reality

**Bitemporal Schema:**
```python
# Every node has:
created_at: datetime      # TT: when added to SEG
valid_from: datetime      # VT: when became true
valid_to: Optional[datetime]  # VT: when ceased to be true (None = still valid)
```

**Temporal Query Operations:**
```python
def query_valid_time(claim_type: str, at_time: datetime) -> List[ClaimNode]:
    """What was true at specific time?"""
    return [
        claim for claim in seg.get_claims(claim_type)
        if claim.valid_from <= at_time and (
            claim.valid_to is None or claim.valid_to > at_time
        )
    ]

def query_transaction_time(at_time: datetime) -> List[Node]:
    """What did we know at specific time?"""
    return [
        node for node in seg.get_all_nodes()
        if node.created_at <= at_time
    ]

def snapshot_at_time(at_time: datetime) -> SEGSnapshot:
    """Create snapshot of graph state at specific time"""
    pass
```

**Benefits:**
- **Corrections without deletion:** Update VT, preserve TT
- **Audit trails:** Know when we learned things (TT)
- **Historical reasoning:** Reason about past states (VT)
- **Time travel:** Query as-of any point in time

### 4. Contradiction Detection Engine

**Purpose:** Automatically detect conflicting claims using semantic similarity and stance analysis

**Algorithm Flow:**
```python
def detect_contradictions(seg: SEG) -> List[ContradictionRecord]:
    """Find conflicting claims in graph"""
    conflicts = []
    claims = seg.get_nodes_by_type("claim")
    
    # Step 1: Check all pairs for semantic similarity
    for i, claim_a in enumerate(claims):
        for claim_b in claims[i+1:]:
            # Skip if embeddings missing
            if claim_a.embedding is None or claim_b.embedding is None:
                continue
            
            # Calculate semantic similarity
            similarity = cosine_similarity(
                [claim_a.embedding],
                [claim_b.embedding]
            )[0, 0]
            
            # Skip if different topics (< 0.6 similarity)
            if similarity < 0.6:
                continue
            
            # Step 2: Check stances (opposite?)
            if are_opposite_stances(claim_a.stance, claim_b.stance):
                # Step 3: Verify contradiction (not just different stances)
                contradiction_score = analyze_contradiction(
                    claim_a.content,
                    claim_b.content
                )
                
                if contradiction_score > 0.5:
                    # Contradiction detected!
                    conflicts.append(ContradictionRecord(
                        claim_a=claim_a,
                        claim_b=claim_b,
                        similarity=similarity,
                        contradiction_score=contradiction_score,
                        detected_at=datetime.utcnow()
                    ))
                    
                    # Add "contradicts" edge to graph
                    seg.add_edge(ContradictsEdge(
                        id=f"contradicts_{claim_a.id}_{claim_b.id}",
                        source_node_id=claim_a.id,
                        target_node_id=claim_b.id,
                        similarity=similarity,
                        contradiction_score=contradiction_score,
                        detected_at=datetime.utcnow()
                    ))
    
    return conflicts
```

**Stance Detection:**
- **Positive:** Assertions, affirmations ("X is true", "X uses Y")
- **Negative:** Negations, denials ("X is false", "X does not use Y")
- **Neutral:** Questions, observations ("What is X?", "X was observed")

**Contradiction Scoring:**
- Semantic similarity threshold: 0.6 (same topic)
- Stance opposition: Required (positive vs negative)
- Contradiction score threshold: 0.5 (sufficient conflict)

### 5. Query Engine

**Purpose:** Efficient graph traversal for lineage, temporal, provenance, and contradiction queries

**Query Types:**

**Lineage Tracing:**
```python
def trace_lineage(node_id: str, direction: str = "backward") -> List[SEGNode]:
    """Trace lineage backward (sources) or forward (derivations)"""
    if direction == "backward":
        # Find all sources → claim paths
        ancestors = []
        visited = set()
        queue = [node_id]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Get incoming edges
            for edge in seg.get_incoming_edges(current):
                if edge.type in ["witnesses", "cites", "supports"]:
                    source = seg.get_node(edge.source_node_id)
                    if source:
                        ancestors.append(source)
                        queue.append(source.id)
        
        return ancestors
    else:
        # Forward: find derivations
        descendants = []
        # Similar traversal but forward
        return descendants
```

**Temporal Queries:**
```python
def snapshot_at_time(at_time: datetime) -> SEGSnapshot:
    """Create snapshot of graph state at specific time"""
    nodes = []
    edges = []
    
    # Get all nodes valid at time
    for node in seg.get_all_nodes():
        if node.valid_from <= at_time and (
            node.valid_to is None or node.valid_to > at_time
        ):
            nodes.append(node)
    
    # Get all edges valid at time
    for edge in seg.get_all_edges():
        if edge.created_at <= at_time:
            edges.append(edge)
    
    return SEGSnapshot(nodes=nodes, edges=edges, timestamp=at_time)
```

**Provenance Chains:**
```python
def get_provenance_chain(claim_id: str) -> ProvenanceChain:
    """Get complete source-to-claim path"""
    chain = []
    current = claim_id
    
    while current:
        claim = seg.get_node(current)
        if not claim:
            break
        
        chain.append(claim)
        
        # Find source (witnesses or cites edge)
        sources = [
            seg.get_node(edge.source_node_id)
            for edge in seg.get_incoming_edges(current)
            if edge.type in ["witnesses", "cites"]
        ]
        
        if sources:
            current = sources[0].id
        else:
            break
    
    return ProvenanceChain(chain=chain)
```

**Contradiction Queries:**
```python
def find_contradictions(claim_id: str) -> List[ClaimNode]:
    """Find all claims that contradict given claim"""
    claim = seg.get_node(claim_id)
    if not claim:
        return []
    
    # Find all "contradicts" edges
    contradictions = []
    for edge in seg.get_outgoing_edges(claim_id):
        if edge.type == "contradicts":
            contradictory_claim = seg.get_node(edge.target_node_id)
            if contradictory_claim:
                contradictions.append(contradictory_claim)
    
    return contradictions
```

### 6. Export System

**Purpose:** Export graph to standards-compliant formats for external tools

**JSON-LD Export:**
```python
def export_jsonld(context_url: str = "https://aimos.org/seg/context") -> Dict:
    """Export graph as JSON-LD"""
    graph = {
        "@context": context_url,
        "@graph": []
    }
    
    # Convert nodes to JSON-LD
    for node in seg.get_all_nodes():
        jsonld_node = {
            "@id": node.id,
            "@type": node.type.capitalize(),
            "content": node.content if hasattr(node, 'content') else None,
            "created": node.created_at.isoformat(),
            "validFrom": node.valid_from.isoformat(),
            "validTo": node.valid_to.isoformat() if node.valid_to else None
        }
        graph["@graph"].append(jsonld_node)
    
    # Convert edges to JSON-LD
    for edge in seg.get_all_edges():
        jsonld_edge = {
            "@id": edge.id,
            "@type": edge.type.capitalize(),
            "source": edge.source_node_id,
            "target": edge.target_node_id
        }
        graph["@graph"].append(jsonld_edge)
    
    return graph
```

**RDF Serialization:**
- Convert JSON-LD to RDF triples
- Compatible with triple stores (Apache Jena, Virtuoso)
- Enables SPARQL queries

**SHACL Validation:**
- Validate graph structure against shape schema
- Ensure required fields present
- Check edge type constraints
- Validate bitemporal ranges

## Data Models

### Complete Node Schema
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class SEGNode(BaseModel):
    """Base class for all SEG nodes"""
    id: str = Field(default_factory=lambda: f"node_{uuid.uuid4().hex[:12]}")
    type: str  # "claim" | "source" | "derivation" | "agent"
    
    # Bitemporal
    created_at: datetime = Field(default_factory=datetime.utcnow)  # TT
    valid_from: datetime = Field(default_factory=datetime.utcnow)  # VT start
    valid_to: Optional[datetime] = None                             # VT end
    
    # Common fields
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
```

### Complete Edge Schema
```python
class SEGEdge(BaseModel):
    """Base class for all SEG edges"""
    id: str = Field(default_factory=lambda: f"edge_{uuid.uuid4().hex[:12]}")
    type: str  # "supports" | "contradicts" | "derives" | "witnesses" | "cites"
    source_node_id: str
    target_node_id: str
    weight: float = 1.0                       # Edge strength (0-1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
```

## Key System Flows

### Evidence Ingestion Flow
```
1. System/agent calls seg.add_evidence(claim, source)
2. Create ClaimNode with content, embedding, stance
3. Create SourceNode with source_type, reference, authority_score
4. Create "witnesses" or "cites" edge linking source → claim
5. Store nodes/edges in graph store with bitemporal timestamps
6. Contradiction detector analyzes new claim for conflicts
7. Query engine indexes new nodes/edges for fast retrieval
```

### Contradiction Detection Flow
```
1. New claim added to graph
2. Contradiction detector runs (on-demand or batch)
3. Calculate embeddings for all claims (if missing)
4. Check semantic similarity (cosine similarity > 0.6)
5. Check stance opposition (positive vs negative)
6. Calculate contradiction score (NLP/stance analysis)
7. If contradiction_score > 0.5:
   - Create "contradicts" edge
   - Flag for resolution (human or automated)
   - Log contradiction event
```

### Synthesis Flow
```
1. Query engine finds all claims on topic (semantic similarity)
2. Contradiction detector identifies conflicts
3. Resolution strategies applied:
   - Most recent (higher valid_to timestamp)
   - Source trust (higher authority_score)
   - Merge (combine non-conflicting parts)
4. Create synthesized claim with DerivationNode
5. Create "derives" edges linking inputs → synthesized claim
6. Complete provenance chain preserved
```

## System Integrations

### CMC Integration
- **Storage:** SEG nodes/edges stored as CMC atoms
- **Bitemporal:** CMC provides bitemporal storage infrastructure
- **Snapshots:** SEG snapshots use CMC snapshot system
- **Provenance:** CMC atoms link to SEG nodes via VIF witnesses

### HHNI Integration
- **Context Retrieval:** HHNI uses SEG for evidence-based context
- **Embeddings:** SEG uses HHNI for embedding generation
- **Indexing:** SEG claims indexed in HHNI for fast retrieval

### VIF Integration
- **Witness Linking:** VIF witnesses linked to SEG claims via "witnesses" edges
- **Confidence:** SEG claims inherit confidence from VIF witnesses
- **Provenance:** Complete provenance chain from VIF → SEG → Claims

### APOE Integration
- **Plan Execution:** APOE executions recorded as DerivationNodes
- **Lineage Tracking:** SEG tracks how claims were derived from APOE plans
- **Trace Linking:** APOE traces linked to SEG derivations

### SDF-CVF Integration
- **Traces:** SDF-CVF traces linked to SEG evidence nodes
- **Quality Assurance:** SEG enables quartet parity (code/docs/tests/traces)
- **Blast Radius:** SEG tracks impact of changes through evidence relationships

## Non-Functional Requirements

### Performance
- **Node Addition:** <10ms per node (NetworkX), <50ms (Neo4j)
- **Contradiction Detection:** <100ms for graph with <10K claims
- **Query Response:** <50ms for lineage queries (depth < 10)
- **Export:** <1s for JSON-LD export (graph <100K nodes)

### Scalability
- **NetworkX:** Up to 100K nodes (development/testing)
- **Neo4j:** Millions of nodes/edges (production)
- **Contradiction Detection:** Batch processing for large graphs
- **Indexing:** Efficient temporal indexes for as-of queries

### Consistency
- **ACID Transactions:** Neo4j provides ACID guarantees
- **Bitemporal Integrity:** Valid time ranges must be consistent
- **Provenance Integrity:** Every claim must have source
- **Edge Constraints:** Source/target nodes must exist

### Storage
- **NetworkX:** In-memory (no persistence)
- **Neo4j:** Persistent storage with replication
- **Export Formats:** JSON-LD, RDF for archival

## Diagrams

### Component Diagram
```
[API Layer]
    ↓
[Graph Store Interface]
    ↓
[NetworkX Backend] OR [Neo4j Backend]
    ↓
[Bitemporal Storage Engine]
    ↓
[Contradiction Detection Engine]
    ↓
[Query Engine]
    ↓
[Export System]
```

### Sequence Diagram: Evidence Ingestion
```
Client → SEG.add_evidence()
    → Create ClaimNode
    → Create SourceNode
    → Create Edges
    → Store in Graph
    → Trigger Contradiction Detection
    → Return Result
```

### Sequence Diagram: Contradiction Detection
```
SEG.add_evidence()
    → Contradiction Engine.detect()
    → Calculate Embeddings
    → Check Similarity
    → Check Stances
    → Calculate Contradiction Score
    → If > threshold: Create ContradictsEdge
    → Flag for Resolution
```

## References

- **System Map:** `knowledge_architecture/systems/seg/system.map.lucid.json5`
- **L-Level Docs:** `knowledge_architecture/systems/seg/L{0-4}_*.md`
- **Gate Validation:** `coordination/epic_standards_overhaul/artifacts/gate_checks/SEG_T0_T6_GATE_RESULTS.md`
- **Templates:** `knowledge_architecture/TEMPLATES_LIBRARY/T2_ARCHITECTURE_TEMPLATE.md`
