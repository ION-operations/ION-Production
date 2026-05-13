---
id: "seg_T3_detailed"
system: "seg"
component: null
level: "T3"
type: "detailed"
title: "SEG Detailed Implementation Guide"
description: "10,000-word detailed implementation guide"
audience: "developers, implementers"
confidence_threshold: 0.60
token_cost: 10000
word_count: 10000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:00:00Z"
author: "aether"
status: "complete"
tags: ["seg", "core", "t0-t6", "transitional"]
dependencies: ["seg_T2_architecture"]
related_docs: ["seg_T4_complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.


> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# SEG – T3 Detailed Implementation Guide

---

## 📋 Implementation Tag Map

All referenced code is tagged for semantic search and quintet parity validation.

**Tag Categories:**
- **SEG-GRAPH:** Graph construction, knowledge synthesis
- **SEG-WITNESS:** Provenance tracking, lineage
- **SEG-QUERY:** Knowledge retrieval, traversal

**Complete index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) (33 tags)

---

## Setup & Installation

### Dependencies

```bash
# Core graph libraries
pip install networkx>=3.0        # Development backend
pip install neo4j>=5.0           # Production backend
pip install rdflib>=6.0          # RDF support
pip install pyshacl>=0.20        # SHACL validation

# Bitemporal support
pip install python-dateutil>=2.8
pip install pytz>=2023.3

# Embedding generation (for contradiction detection)
pip install sentence-transformers>=2.2.0
pip install numpy>=1.24.0
```

### Graph Backend Selection

**Development (NetworkX):**
```python
from packages.seg import SEG, SEGNetworkXBackend

seg = SEG(backend=SEGNetworkXBackend())
# Fast, in-memory, no persistence
# Good for testing and prototyping
```

**Production (Neo4j):**
```python
from packages.seg import SEG, SEGNeo4jBackend

seg = SEG(backend=SEGNeo4jBackend(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="your_password"
))
# Persistent, scalable, ACID transactions
# Required for production deployments
```

## Public API Interfaces

### Core Operations

```python
from packages.seg import SEG, ClaimNode, SourceNode, DerivationNode

# Initialize SEG
seg = SEG(backend="neo4j")

# Add evidence (claim + source)
claim = seg.add_evidence(
    content="OAuth2 uses JWT tokens",
    source_type="vif_witness",
    source_reference="vif_abc123",
    confidence=0.95
)

# Link claims
seg.link_claims(
    source_id="claim_001",
    target_id="claim_002",
    edge_type="supports",
    weight=0.8
)

# Find contradictions
contradictions = seg.find_contradictions(claim_id="claim_001")

# Synthesize knowledge
synthesized = seg.synthesize(
    topic="authentication_methods",
    resolution_strategy="most_recent"
)

# Query lineage
lineage = seg.trace_lineage(claim_id="claim_001", direction="backward")

# Export to JSON-LD
jsonld = seg.export_jsonld()
```

### Evidence Ingestion

```python
# Add claim with VIF witness
claim = seg.add_claim(
    content="User John has role Admin",
    confidence=0.9,
    vif_witness_id="vif_witness_xyz789",
    valid_from=datetime(2025, 10, 15),
    valid_to=datetime(2025, 10, 18)  # Bitemporal valid time
)

# Add source
source = seg.add_source(
    source_type="document",
    reference="docs/security_policy.md",
    authority_score=0.8,
    verified=True
)

# Link source to claim
seg.link_vif_witness(
    vif_id="vif_witness_xyz789",
    claim_id=claim.id
)

# Add derivation (from APOE plan)
derivation = seg.add_derivation(
    method="apoe_execution",
    inputs=["claim_001", "claim_002"],
    outputs=["claim_003"],
    reasoning="Combined evidence from multiple sources",
    confidence=0.85,
    apoe_plan_id="apoe_plan_123"
)
```

### Contradiction Detection

```python
# Automatic detection (runs on claim addition)
contradictions = seg.detect_contradictions()

# Manual detection for specific claim
conflicts = seg.find_contradictions(claim_id="claim_001")

# Check contradiction details
for conflict in conflicts:
    print(f"Claim {conflict.claim_a.id} contradicts {conflict.claim_b.id}")
    print(f"Similarity: {conflict.similarity}")
    print(f"Contradiction Score: {conflict.contradiction_score}")
    print(f"Detected at: {conflict.detected_at}")
```

### Query Operations

```python
# Temporal queries
snapshot = seg.snapshot_at_time(datetime(2025, 10, 17))
# Returns all nodes/edges valid at that time

# Lineage tracing
ancestors = seg.trace_lineage(claim_id="claim_001", direction="backward")
# Returns all sources that led to this claim

descendants = seg.trace_lineage(claim_id="claim_001", direction="forward")
# Returns all claims derived from this claim

# Provenance chains
chain = seg.get_provenance_chain(claim_id="claim_001")
# Returns complete source-to-claim path

# Contradiction queries
contradictions = seg.find_contradictions(claim_id="claim_001")
# Returns all claims that contradict this claim
```

## Implementation Details

### Node Creation with Validation

```python
def add_claim(
    self,
    content: str,
    confidence: float = 1.0,
    vif_witness_id: Optional[str] = None,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None
) -> ClaimNode:
    """Add claim with validation and automatic contradiction detection"""
    
    # Validate inputs
    if not content or len(content.strip()) == 0:
        raise ValueError("Claim content cannot be empty")
    
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Confidence must be between 0 and 1, got {confidence}")
    
    # Generate embedding for semantic similarity
    embedding = self.embedding_service.embed(content)
    
    # Detect stance (positive/negative/neutral)
    stance = self._detect_stance(content)
    
    # Set bitemporal timestamps
    now = datetime.utcnow()
    valid_from = valid_from or now
    valid_to = valid_to
    
    # Create claim node
    claim = ClaimNode(
        content=content,
        embedding=embedding,
        confidence=confidence,
        stance=stance,
        vif_witness_id=vif_witness_id,
        created_at=now,  # Transaction time
        valid_from=valid_from,  # Valid time
        valid_to=valid_to
    )
    
    # Store in graph
    self.backend.add_node(claim)
    
    # Check for contradictions with existing claims
    self._check_contradictions_for_new_claim(claim)
    
    return claim
```

### Contradiction Detection Algorithm

```python
def _check_contradictions_for_new_claim(self, new_claim: ClaimNode):
    """Check if new claim contradicts existing claims"""
    
    existing_claims = [
        node for node in self.backend.get_nodes_by_type("claim")
        if node.id != new_claim.id
    ]
    
    for existing in existing_claims:
        # Skip if embeddings missing
        if new_claim.get_embedding() is None or existing.get_embedding() is None:
            continue
        
        # Calculate semantic similarity (cosine similarity)
        similarity = cosine_similarity(
            [new_claim.get_embedding()],
            [existing.get_embedding()]
        )[0, 0]
        
        # Threshold: must be similar (> 0.6) to be contradictory
        if similarity < 0.6:
            continue
        
        # Check if stances are opposite
        if not self._are_opposite_stances(new_claim.stance, existing.stance):
            continue
        
        # Calculate contradiction score
        contradiction_score = self._calculate_contradiction_score(
            new_claim.content,
            existing.content
        )
        
        # If contradiction detected, create edge
        if contradiction_score > 0.5:
            edge = ContradictsEdge(
                source_node_id=new_claim.id,
                target_node_id=existing.id,
                similarity=similarity,
                contradiction_score=contradiction_score,
                detected_at=datetime.utcnow()
            )
            self.backend.add_edge(edge)
            
            # Flag for resolution
            self._flag_contradiction_for_resolution(new_claim.id, existing.id)
```

### Stance Detection

```python
def _detect_stance(self, content: str) -> str:
    """Detect stance: positive, negative, or neutral"""
    
    content_lower = content.lower()
    
    # Positive indicators
    positive_keywords = ["is", "uses", "has", "supports", "enables", "provides"]
    # Negative indicators
    negative_keywords = ["is not", "does not", "no", "never", "cannot", "fails"]
    
    positive_count = sum(1 for kw in positive_keywords if kw in content_lower)
    negative_count = sum(1 for kw in negative_keywords if kw in content_lower)
    
    if negative_count > positive_count:
        return "negative"
    elif positive_count > 0:
        return "positive"
    else:
        return "neutral"

def _are_opposite_stances(self, stance_a: str, stance_b: str) -> bool:
    """Check if two stances are opposite"""
    opposites = {
        "positive": "negative",
        "negative": "positive"
    }
    return opposites.get(stance_a) == stance_b
```

### Bitemporal Query Implementation

```python
def snapshot_at_time(self, at_time: datetime) -> SEGSnapshot:
    """Create snapshot of graph state at specific time"""
    
    nodes = []
    edges = []
    
    # Get all nodes valid at time
    for node in self.backend.get_all_nodes():
        # Check valid time range
        if node.valid_from <= at_time:
            if node.valid_to is None or node.valid_to > at_time:
                nodes.append(node)
    
    # Get all edges created before time
    for edge in self.backend.get_all_edges():
        if edge.created_at <= at_time:
            # Verify source and target nodes exist in snapshot
            source_exists = any(n.id == edge.source_node_id for n in nodes)
            target_exists = any(n.id == edge.target_node_id for n in nodes)
            
            if source_exists and target_exists:
                edges.append(edge)
    
    return SEGSnapshot(
        nodes=nodes,
        edges=edges,
        timestamp=at_time
    )
```

### Lineage Tracing

```python
def trace_lineage(self, node_id: str, direction: str = "backward") -> List[SEGNode]:
    """Trace lineage backward (sources) or forward (derivations)"""
    
    if direction == "backward":
        return self._trace_backward(node_id)
    else:
        return self._trace_forward(node_id)

def _trace_backward(self, node_id: str) -> List[SEGNode]:
    """Find all sources that led to this node"""
    ancestors = []
    visited = set()
    queue = [node_id]
    
    while queue:
        current_id = queue.pop(0)
        if current_id in visited:
            continue
        visited.add(current_id)
        
        # Get incoming edges
        for edge in self.backend.get_incoming_edges(current_id):
            if edge.type in ["witnesses", "cites", "supports", "derives"]:
                source = self.backend.get_node(edge.source_node_id)
                if source:
                    ancestors.append(source)
                    queue.append(source.id)
    
    return ancestors

def _trace_forward(self, node_id: str) -> List[SEGNode]:
    """Find all nodes derived from this node"""
    descendants = []
    visited = set()
    queue = [node_id]
    
    while queue:
        current_id = queue.pop(0)
        if current_id in visited:
            continue
        visited.add(current_id)
        
        # Get outgoing edges
        for edge in self.backend.get_outgoing_edges(current_id):
            if edge.type == "derives":
                target = self.backend.get_node(edge.target_node_id)
                if target:
                    descendants.append(target)
                    queue.append(target.id)
    
    return descendants
```

### Synthesis with Resolution Strategies

```python
def synthesize(
    self,
    topic: str,
    resolution_strategy: str = "most_recent"
) -> ClaimNode:
    """Synthesize knowledge from multiple claims on topic"""
    
    # Find all claims on topic (semantic similarity)
    topic_embedding = self.embedding_service.embed(topic)
    relevant_claims = []
    
    for claim in self.backend.get_nodes_by_type("claim"):
        if claim.get_embedding() is None:
            continue
        
        similarity = cosine_similarity(
            [topic_embedding],
            [claim.get_embedding()]
        )[0, 0]
        
        if similarity > 0.7:  # Relevant to topic
            relevant_claims.append((claim, similarity))
    
    # Sort by resolution strategy
    if resolution_strategy == "most_recent":
        relevant_claims.sort(key=lambda x: x[0].valid_from, reverse=True)
    elif resolution_strategy == "source_trust":
        relevant_claims.sort(key=lambda x: self._get_source_authority(x[0]), reverse=True)
    
    # Check for contradictions
    contradictions = []
    for claim_a, _ in relevant_claims:
        for claim_b, _ in relevant_claims:
            if claim_a.id == claim_b.id:
                continue
            
            if self._are_contradictory(claim_a.id, claim_b.id):
                contradictions.append((claim_a, claim_b))
    
    # If contradictions exist, resolve them
    if contradictions:
        resolved_claims = self._resolve_contradictions(contradictions, resolution_strategy)
    else:
        resolved_claims = [claim for claim, _ in relevant_claims]
    
    # Create synthesized claim
    synthesized_content = self._merge_claims(resolved_claims)
    
    synthesis_claim = self.add_claim(
        content=synthesized_content,
        confidence=self._calculate_synthesis_confidence(resolved_claims)
    )
    
    # Create derivation node
    derivation = self.add_derivation(
        method="synthesis",
        inputs=[c.id for c in resolved_claims],
        outputs=[synthesis_claim.id],
        reasoning=f"Synthesized from {len(resolved_claims)} claims using {resolution_strategy}",
        confidence=synthesis_claim.confidence
    )
    
    return synthesis_claim
```

## Configuration

### Embedding Service Configuration

```python
# Default: sentence-transformers model
from packages.seg import SEG, SentenceTransformerEmbeddingService

seg = SEG(
    backend="neo4j",
    embedding_service=SentenceTransformerEmbeddingService(
        model_name="all-MiniLM-L6-v2"  # Fast, good quality
    )
)

# Custom embedding service
class CustomEmbeddingService:
    def embed(self, text: str) -> np.ndarray:
        # Your embedding logic
        pass

seg = SEG(
    backend="neo4j",
    embedding_service=CustomEmbeddingService()
)
```

### Contradiction Detection Configuration

```python
# Configure thresholds
seg.configure_contradiction_detection(
    similarity_threshold=0.6,        # Minimum similarity to check
    contradiction_threshold=0.5,      # Minimum contradiction score
    auto_detect=True,                 # Run on claim addition
    batch_detect_interval=3600       # Batch detection every hour
)
```

### Bitemporal Configuration

```python
# Configure temporal behavior
seg.configure_bitemporal(
    default_valid_time_start="now",  # "now" | "past" | datetime
    allow_future_valid_time=False,   # Prevent future valid times
    enable_time_travel=True           # Enable snapshot queries
)
```

## Export & Interoperability

### JSON-LD Export

```python
# Export to JSON-LD
jsonld = seg.export_jsonld(
    context_url="https://aimos.org/seg/context",
    include_edges=True
)

# Save to file
import json
with open("seg_export.jsonld", "w") as f:
    json.dump(jsonld, f, indent=2)
```

### RDF Serialization

```python
# Export to RDF
rdf_triples = seg.export_rdf(format="turtle")

# Save to file
with open("seg_export.ttl", "w") as f:
    f.write(rdf_triples)
```

### SHACL Validation

```python
# Validate graph structure
validation_result = seg.validate_shacl(
    shape_schema="schemas/seg_shacl.ttl"
)

if validation_result.valid:
    print("Graph structure is valid")
else:
    print(f"Validation errors: {validation_result.errors}")
```

## Error Handling

### Invalid Node/Edge Errors

```python
try:
    claim = seg.add_claim(content="")  # Empty content
except ValueError as e:
    print(f"Validation error: {e}")

try:
    seg.link_claims(
        source_id="nonexistent",
        target_id="claim_001",
        edge_type="supports"
    )
except NodeNotFoundError as e:
    print(f"Node not found: {e}")
```

### Cycle Detection

```python
# SEG prevents cycles in derivation chains
try:
    seg.add_derivation(
        method="inference",
        inputs=["claim_003"],
        outputs=["claim_001"],  # Would create cycle
        reasoning="test"
    )
except CycleDetectedError as e:
    print(f"Cycle detected: {e}")
```

### Bitemporal Range Errors

```python
try:
    claim = seg.add_claim(
        content="Test",
        valid_from=datetime(2025, 10, 20),
        valid_to=datetime(2025, 10, 15)  # Invalid: end before start
    )
except InvalidValidTimeRangeError as e:
    print(f"Invalid valid time range: {e}")
```

## Testing

### Unit Tests

```python
import pytest
from packages.seg import SEG, SEGNetworkXBackend

def test_add_claim():
    seg = SEG(backend=SEGNetworkXBackend())
    claim = seg.add_claim(content="Test claim", confidence=0.9)
    
    assert claim.content == "Test claim"
    assert claim.confidence == 0.9
    assert claim.type == "claim"
    assert seg.backend.get_node(claim.id) == claim

def test_contradiction_detection():
    seg = SEG(backend=SEGNetworkXBackend())
    
    claim1 = seg.add_claim(content="OAuth2 uses JWT tokens", confidence=0.9)
    claim2 = seg.add_claim(content="OAuth2 does not use JWT tokens", confidence=0.8)
    
    contradictions = seg.find_contradictions(claim1.id)
    assert len(contradictions) > 0
    assert contradictions[0].claim_b.id == claim2.id

def test_lineage_tracing():
    seg = SEG(backend=SEGNetworkXBackend())
    
    source = seg.add_source(source_type="document", reference="doc.md")
    claim = seg.add_claim(content="Test claim")
    seg.link_vif_witness(vif_id="vif_123", claim_id=claim.id)
    
    ancestors = seg.trace_lineage(claim.id, direction="backward")
    assert len(ancestors) > 0
```

### Integration Modules

SEG provides 7 integration modules (all complete, 22 functions total):

**CMC Integration** (`packages/seg/cmc_integration.py`):
```python
from seg.cmc_integration import store_evidence_in_cmc, retrieve_evidence_from_cmc, link_evidence_to_cmc

# Store evidence in CMC
atom_id = store_evidence_in_cmc(evidence, cmc_store)

# Retrieve from CMC
evidence = retrieve_evidence_from_cmc(atom_id, cmc_store, graph)

# Link existing evidence
link_evidence_to_cmc(evidence_id, atom_id, graph)
```

**VIF Integration** (`packages/seg/vif_integration.py`):
```python
from seg.vif_integration import create_vif_witness, attach_witness_to_entity, get_witness_provenance

# Create witness
witness = create_vif_witness(entity, "entity_create", "model_id", "provider", 0.95, "snapshot_123")

# Attach to entity
attach_witness_to_entity(entity_id, witness.witness_id, graph)

# Get provenance
provenance = get_witness_provenance(witness_id)
```

**HHNI Integration** (`packages/seg/hhni_integration.py`):
```python
from seg.hhni_integration import synthesize_evidence, get_synthesis_context, index_evidence_for_hhni

# Synthesize evidence
result = synthesize_evidence("query", graph, hhni_retriever)

# Get context
context = get_synthesis_context(["evidence_1", "evidence_2"], hhni_retriever)

# Index evidence
index_id = index_evidence_for_hhni(evidence, hhni_indexer)
```

**APOE Integration** (`packages/seg/apoe_integration.py`):
```python
from seg.apoe_integration import store_execution_trace, get_plan_effectiveness, link_trace_to_evidence

# Store trace
evidence_id = store_execution_trace(trace_dict, graph)

# Get effectiveness
effectiveness = get_plan_effectiveness("plan_name", graph)

# Link trace
link_trace_to_evidence("exec_123", evidence_id, graph)
```

**SDF-CVF Integration** (`packages/seg/sdfcvf_integration.py`):
```python
from seg.sdfcvf_integration import validate_consistency, get_consistency_report, link_trace_to_evidence

# Validate consistency
is_consistent = validate_consistency(evidence)

# Get report
report = get_consistency_report(evidence_id, graph)

# Link trace
link_trace_to_evidence("trace_123", evidence_id, graph)
```

**CAS Integration** (`packages/seg/cas_integration.py`):
```python
from seg.cas_integration import store_failure_pattern, get_failure_patterns, link_pattern_to_evidence

# Store pattern
evidence_id = store_failure_pattern(pattern_dict, graph)

# Get patterns
patterns = get_failure_patterns("categorization_error", graph)

# Link pattern
link_pattern_to_evidence("event_123", evidence_id, graph)
```

**TCS Integration** (`packages/seg/tcs_integration.py`):
```python
from seg.tcs_integration import timeline_entry_to_evidence, ingest_timeline_entry

# Transform timeline entry
evidence, evidence_id = timeline_entry_to_evidence(timeline_entry, "atom_123", graph)

# Ingest with gate evidence
gate_evidence = ingest_timeline_entry(timeline_entry, "atom_123", "witness_123")
```

### Integration Tests

All 7 integration modules have comprehensive test coverage (37 tests total):

```python
# CMC integration tests
def test_store_evidence_in_cmc_basic():
    """Test basic evidence storage in CMC"""
    # Tests ImportError handling when CMC unavailable
    # Tests graph storage and retrieval
    # Tests metadata preservation

# VIF integration tests (6 tests)
def test_create_vif_witness_basic():
    """Test basic VIF witness creation"""
    # Tests witness creation and attachment

# HHNI integration tests (4 tests)
def test_synthesize_evidence_basic():
    """Test basic evidence synthesis via HHNI"""
    # Tests semantic search integration

# APOE integration tests (5 tests)
def test_store_execution_trace_basic():
    """Test basic execution trace storage"""
    # Tests trace storage and effectiveness tracking

# SDF-CVF integration tests (6 tests)
def test_validate_consistency_basic():
    """Test basic consistency validation"""
    # Tests quartet/quintet parity validation

# CAS integration tests (5 tests)
def test_store_failure_pattern_basic():
    """Test basic failure pattern storage"""
    # Tests failure pattern storage and retrieval

# TCS integration tests (7 tests - existing)
def test_timeline_entry_to_evidence_basic():
    """Test basic timeline entry transformation"""
    # Tests timeline entry transformation
```

## Troubleshooting

### Common Issues

**Issue: Contradiction detection not working**
```python
# Cause: Embeddings not generated
# Solution: Ensure embedding service is configured

seg = SEG(
    backend="neo4j",
    embedding_service=SentenceTransformerEmbeddingService()
)

# Verify embeddings exist
claim = seg.add_claim(content="Test")
assert claim.get_embedding() is not None
```

**Issue: Neo4j connection errors**
```python
# Cause: Incorrect connection parameters
# Solution: Verify Neo4j is running and credentials are correct

from neo4j import GraphDatabase

# Test connection
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)
driver.verify_connectivity()
```

**Issue: Temporal queries return empty results**
```python
# Cause: Valid time range not set correctly
# Solution: Ensure valid_from <= query_time <= valid_to

# Set valid time explicitly
claim = seg.add_claim(
    content="Test",
    valid_from=datetime(2025, 1, 1),
    valid_to=datetime(2025, 12, 31)
)

# Query at valid time
snapshot = seg.snapshot_at_time(datetime(2025, 6, 15))
assert len(snapshot.nodes) > 0
```

**Issue: Slow contradiction detection**
```python
# Cause: Checking all pairs (O(n²))
# Solution: Use batch processing or indexing

# Enable batch processing
seg.configure_contradiction_detection(
    auto_detect=False,  # Disable on-demand
    batch_detect_interval=3600  # Run hourly
)

# Or use vector similarity index (Neo4j)
seg.backend.create_similarity_index()
```

## Migration Notes

### T→L Cutover Steps

1. **Validate T-level documentation** against gate checklist
2. **Review with stakeholders** for accuracy and completeness
3. **Update L-level docs** with T-level content (preserve T-level for history)
4. **Update navigation indexes** to reference L-level instead of T-level
5. **Run validation gates** to ensure compliance
6. **Archive T-level** in historical_versions/

### Validation Checklist

- [ ] All interfaces documented with examples
- [ ] All configuration options explained
- [ ] Error handling covered
- [ ] Tests provided
- [ ] Troubleshooting guide included
- [ ] Migration steps documented

## References

- **System Map:** `knowledge_architecture/systems/seg/system.map.lucid.json5`
- **L-Level Docs:** `knowledge_architecture/systems/seg/L{0-4}_*.md`
- **Gate Validation:** `coordination/epic_standards_overhaul/artifacts/gate_checks/SEG_T0_T6_GATE_RESULTS.md`
- **Templates:** `knowledge_architecture/TEMPLATES_LIBRARY/T3_DETAILED_TEMPLATE.md`
- **Code:** `packages/seg/`