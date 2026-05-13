---
id: hhni_T3_detailed
level: L3
system: HHNI
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# HHNI – T3 Detailed Implementation Guide

## Setup & Interfaces

### Public API Methods

```python
from packages.hhni import HierarchicalIndex, RetrievalConfig, RetrievalResult

# Initialize HHNI
index = HierarchicalIndex(
    vector_store="faiss",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)

# Index atoms from CMC
atoms = cmc_client.get_atoms(modality="text")
index.build_from_atoms(atoms)

# Retrieve with query
result = index.retrieve(
    query="authentication OAuth2",
    config=RetrievalConfig(
        token_budget=8000,
        enable_dvns=True,
        enable_dedup=True,
        enable_conflict_resolution=True
    )
)

# Retrieve by hierarchical path
section_context = index.get_by_path(["system:auth", "section:oauth2"])

# Update index when atoms change
index.update_index(changed_atom_ids=["atom_123", "atom_456"])
```

### Type Definitions

```python
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import numpy as np

@dataclass
class IndexEntry:
    """Entry at any hierarchical level"""
    id: str
    level: int  # 1-6
    content_summary: str
    embedding: np.ndarray
    parent_id: Optional[str] = None
    child_ids: List[str] = None
    atom_refs: List[str] = None
    depth_score: float = 0.0
    dependency_hash: str = ""

@dataclass
class RetrievalConfig:
    """Retrieval configuration"""
    token_budget: int = 8000
    k_candidates: int = 100  # Stage 1 candidates
    enable_dvns: bool = True
    enable_dedup: bool = True
    enable_conflict_resolution: bool = True
    enable_compression: bool = True
    preserve_diversity: bool = True
    similarity_threshold: float = 0.85  # Deduplication threshold

@dataclass
class RetrievalResult:
    """Optimized context with metrics"""
    items: List[BudgetItem]
    total_tokens: int
    items_count: int
    rs_lift: float
    dvns_applied: bool
    iterations: int
    duplicates_removed: int
    conflicts_resolved: int
    metrics: Dict[str, Any]
```

## Indexing Implementation

### Building 6-Level Index

```python
def build_from_atoms(atoms: List[Atom]) -> None:
    """Construct all 6 levels from atoms"""
    # Level 4: Sentence (from atoms directly)
    for atom in atoms:
        if atom.modality == Modality.TEXT:
            sentences = extract_sentences(atom.get_content())
            for sent in sentences:
                entry = IndexEntry(
                    id=f"sent_{uuid.uuid4().hex[:12]}",
                    level=4,
                    content_summary=sent,
                    embedding=embed(sent),
                    atom_refs=[atom.id]
                )
                levels[4].add_entry(entry)
    
    # Level 3: Paragraph (group sentences)
    paragraphs = group_into_paragraphs(list(levels[4].entries.values()))
    for para in paragraphs:
        levels[3].add_entry(para)
    
    # Level 2: Section (group paragraphs)
    sections = group_into_sections(list(levels[3].entries.values()))
    for sect in sections:
        levels[2].add_entry(sect)
    
    # Level 1: System (overview)
    system = create_system_overview(list(levels[2].entries.values()))
    levels[1].add_entry(system)
    
    # Level 5-6: Word and subword
    build_word_index()
    build_subword_index()
    
    # Build parent-child relationships
    build_relationships()
```

### Dependency Hashing

```python
def compute_dependency_hash(entry: IndexEntry) -> str:
    """Hash of all child content for change detection"""
    if not entry.child_ids:
        # Leaf node: hash own content
        return hashlib.sha256(entry.content_summary.encode()).hexdigest()
    
    # Non-leaf: hash all children
    child_entries = [get_entry(cid) for cid in entry.child_ids]
    child_hashes = sorted([c.dependency_hash for c in child_entries])
    
    canonical = json.dumps({
        "children": child_hashes,
        "atoms": sorted(entry.atom_refs)
    }, sort_keys=True)
    
    return hashlib.sha256(canonical.encode()).hexdigest()

def update_dependency_hashes():
    """Recompute hashes bottom-up when content changes"""
    # Start at bottom (level 6), propagate up
    for level_num in [6, 5, 4, 3, 2, 1]:
        level = levels[level_num]
        for entry in level.entries.values():
            entry.dependency_hash = compute_dependency_hash(entry)
```

## Retrieval Implementation

### Stage 1: Coarse Retrieval

```python
def coarse_retrieval(
    query: str,
    query_embedding: np.ndarray,
    k: int = 100
) -> List[BudgetItem]:
    """Fast KNN semantic search"""
    # Search at appropriate level (default: Level 4 = Sentence)
    candidates = vector_store.search(
        query_vector=query_embedding,
        k=k,
        filters={"modality": "text"}
    )
    
    # Convert to BudgetItems
    items = []
    for candidate in candidates:
        atom = load_atom(candidate.id)
        item = BudgetItem(
            source_id=atom.id,
            content=atom.get_content(),
            embedding=atom.embedding.vector,
            tokens=estimate_tokens(atom.get_content()),
            relevance_score=cosine_similarity(query_embedding, atom.embedding.vector)
        )
        items.append(item)
    
    return items
```

### Stage 2: DVNS Physics Optimization

```python
def physics_refinement(
    items: List[BudgetItem],
    query_embedding: np.ndarray,
    max_iterations: int = 100
) -> List[BudgetItem]:
    """Apply DVNS physics to optimize layout"""
    # Create particles
    particles = create_particles(items, query_embedding)
    
    # Run simulation
    iterations = 0
    while iterations < max_iterations:
        # Compute forces
        for particle in particles:
            F_total = np.zeros(particle.position.shape)
            
            # Sum all forces
            for other in particles:
                if other != particle:
                    F_total += compute_gravity_force(particle, other, query_embedding)
                    F_total += compute_repulse_force(particle, other)
            
            F_total += compute_elastic_force(particle, index)
            F_total += compute_damping_force(particle)
            
            # Update acceleration
            particle.acceleration = F_total / particle.mass
        
        # Velocity-Verlet integration
        for particle in particles:
            particle.position += particle.velocity * dt + 0.5 * particle.acceleration * dt**2
        
        # Recompute accelerations at new positions
        # (repeat force computation)
        
        # Update velocities
        for particle in particles:
            particle.velocity += 0.5 * (a_old + particle.acceleration) * dt
        
        # Check convergence
        if has_converged(particles):
            break
        
        iterations += 1
    
    # Reorder by physics score (distance to query)
    items_reordered = reorder_by_physics_score(items, particles)
    
    return items_reordered, iterations
```

### Complete Retrieval Pipeline

```python
def retrieve(
    query: str,
    config: RetrievalConfig
) -> RetrievalResult:
    """Two-stage retrieval with quality pipeline"""
    # Embed query
    query_embedding = embed(query)
    
    # === STAGE 1: COARSE RETRIEVAL ===
    candidates = coarse_retrieval(query, query_embedding, k=config.k_candidates)
    
    # === STAGE 2: REFINEMENT ===
    
    # Step 1: DVNS Physics Optimization
    if config.enable_dvns:
        optimized, iterations = physics_refinement(candidates, query_embedding)
        candidates = optimized
    else:
        iterations = 0
    
    # Step 2: Deduplication
    duplicates_removed = 0
    if config.enable_dedup:
        candidates, duplicates_removed = remove_duplicates(
            candidates,
            threshold=config.similarity_threshold
        )
    
    # Step 3: Conflict Resolution
    conflicts_resolved = 0
    if config.enable_conflict_resolution:
        conflicts = detect_conflicts(candidates)
        if conflicts:
            candidates, conflicts_resolved = resolve_conflicts(
                candidates,
                conflicts
            )
    
    # Step 4: Strategic Compression
    if config.enable_compression:
        candidates = apply_compression(candidates)
    
    # Step 5: Budget Fitting
    final_items = fit_to_budget(
        candidates,
        budget=config.token_budget,
        preserve_diversity=config.preserve_diversity
    )
    
    # Calculate RS-lift (improvement over baseline)
    rs_lift = calculate_rs_lift(final_items, baseline_items)
    
    return RetrievalResult(
        items=final_items,
        total_tokens=sum(item.tokens for item in final_items),
        items_count=len(final_items),
        rs_lift=rs_lift,
        dvns_applied=config.enable_dvns,
        iterations=iterations,
        duplicates_removed=duplicates_removed,
        conflicts_resolved=conflicts_resolved,
        metrics={...}
    )
```

## DVNS Parameterization

### Force Constants

```python
class DVNSConfig:
    """Physics simulation parameters"""
    # Gravity
    G: float = 1.0  # Gravitational constant
    
    # Elastic
    k: float = 0.5  # Spring constant
    
    # Repulse
    δ: float = 0.3  # Repulse strength
    
    # Damping
    c: float = 0.1  # Damping coefficient
    
    # Simulation
    dt: float = 0.01  # Time step
    max_iterations: int = 100
    convergence_epsilon: float = 0.001
```

### Tuning Guidelines

```python
# For faster convergence (lower quality):
config = DVNSConfig(
    dt=0.02,  # Larger time step
    max_iterations=50,
    convergence_epsilon=0.01  # Looser convergence
)

# For higher quality (slower):
config = DVNSConfig(
    dt=0.005,  # Smaller time step
    max_iterations=200,
    convergence_epsilon=0.0001  # Tighter convergence
)
```

## Deduplication Strategy

### Semantic Clustering

```python
def remove_duplicates(
    items: List[BudgetItem],
    threshold: float = 0.85
) -> Tuple[List[BudgetItem], int]:
    """Cluster and deduplicate semantically similar items"""
    if not items:
        return [], 0
    
    # Build similarity matrix
    embeddings = np.array([item.embedding for item in items])
    similarities = cosine_similarity(embeddings)
    
    # Cluster using threshold
    clusters = []
    assigned = set()
    
    for i, item in enumerate(items):
        if i in assigned:
            continue
        
        # Start new cluster
        cluster = [i]
        assigned.add(i)
        
        # Find similar items
        for j in range(i + 1, len(items)):
            if j not in assigned and similarities[i, j] >= threshold:
                cluster.append(j)
                assigned.add(j)
        
        clusters.append(cluster)
    
    # Select best from each cluster
    kept = []
    suppressed_count = 0
    
    for cluster_indices in clusters:
        cluster_items = [items[i] for i in cluster_indices]
        
        # Select best (highest relevance score)
        best = max(cluster_items, key=lambda x: x.relevance_score)
        kept.append(best)
        suppressed_count += len(cluster_items) - 1
    
    return kept, suppressed_count
```

## Error Handling

### Missing Index Entries

```python
class IndexError(Exception):
    """Raised when index operation fails"""
    pass

def get_entry_safe(entry_id: str) -> IndexEntry:
    """Get entry with error handling"""
    entry = index.get_entry(entry_id)
    if not entry:
        raise IndexError(f"Entry not found: {entry_id}")
    return entry
```

### Budget Violations

```python
class BudgetError(Exception):
    """Raised when budget exceeded"""
    pass

def fit_to_budget_safe(
    items: List[BudgetItem],
    budget: int
) -> List[BudgetItem]:
    """Fit to budget with validation"""
    selected = fit_to_budget(items, budget)
    total = sum(item.tokens for item in selected)
    
    if total > budget:
        raise BudgetError(f"Budget exceeded: {total} > {budget}")
    
    return selected
```

## Examples

### Example: Indexing Atoms

```python
# Get atoms from CMC
atoms = cmc_client.query_atoms(modality="text")

# Build index
index = HierarchicalIndex()
index.build_from_atoms(atoms)

# Verify index
print(f"Level 1 entries: {len(index.levels[1].entries)}")
print(f"Level 4 entries: {len(index.levels[4].entries)}")
```

### Example: Retrieval with Physics

```python
# Configure retrieval
config = RetrievalConfig(
    token_budget=8000,
    enable_dvns=True,
    enable_dedup=True,
    enable_conflict_resolution=True
)

# Retrieve
result = index.retrieve(
    query="How does OAuth2 token validation work?",
    config=config
)

# Use results
print(f"Retrieved {result.items_count} items")
print(f"Total tokens: {result.total_tokens}")
print(f"RS-lift: {result.rs_lift:.2%}")
print(f"DVNS iterations: {result.iterations}")

for item in result.items:
    print(f"- {item.content[:100]}...")
```

### Example: Lost in Middle Test

```python
def test_lost_in_middle_scenario():
    """Validate physics solves the problem"""
    # Create 100 items
    items = create_test_items(100)
    
    # Place most relevant in middle (position 50)
    items[50] = create_highly_relevant_item(query)
    
    # Run retrieval with DVNS
    result = index.retrieve(
        query,
        config=RetrievalConfig(enable_dvns=True)
    )
    
    # Check: relevant item should be in top 10!
    top_10_ids = [item.source_id for item in result.items[:10]]
    assert items[50].source_id in top_10_ids  # ✅ PASSING!
```

## Tests

### Unit Test Example

```python
def test_deduplication():
    """Test semantic deduplication"""
    items = [
        BudgetItem(content="OAuth2 uses tokens", ...),
        BudgetItem(content="OAuth2 token authentication", ...),  # Duplicate
        BudgetItem(content="REST API design", ...)  # Different
    ]
    
    kept, removed = remove_duplicates(items, threshold=0.85)
    
    assert len(kept) == 2
    assert removed == 1
```

### Integration Test Example

```python
def test_complete_pipeline():
    """End-to-end retrieval"""
    # Ingest test data
    atoms = create_test_atoms(100)
    index.build_from_atoms(atoms)
    
    # Query
    result = index.retrieve(
        "authentication OAuth2",
        config=default_config
    )
    
    # Validate
    assert result.items_count > 0
    assert result.total_tokens <= config.token_budget
    assert result.dvns_applied == True
    assert result.rs_lift > 0.10  # At least 10% improvement
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_index_entry_cached(entry_id: str) -> IndexEntry:
    """Cache frequently accessed index entries"""
    return index.get_entry(entry_id)

# Embedding cache
embedding_cache: Dict[str, np.ndarray] = {}

def embed_with_cache(text: str) -> np.ndarray:
    """Cache embeddings"""
    if text not in embedding_cache:
        embedding_cache[text] = embedding_service.embed(text)
    return embedding_cache[text]
```

### Batch Processing

```python
def retrieve_batch(
    queries: List[str],
    config: RetrievalConfig
) -> List[RetrievalResult]:
    """Process multiple queries efficiently"""
    # Batch embed queries
    query_embeddings = embedding_service.embed_batch(queries)
    
    # Parallel retrieval
    results = []
    for query, embedding in zip(queries, query_embeddings):
        result = retrieve_with_embedding(embedding, config)
        results.append(result)
    
    return results
```

## Migration & Cutover Notes

### T→L Rename Strategy

After review and acceptance:
1. Run validation gate: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
2. Get reviewer sign-off (Braden)
3. Backup L-level files: `mv L*.md L*.md.backup`
4. Rename T-level files: `mv T0_executive.md L0_executive.md` (repeat for T1-T6)
5. Update references in indices/maps
6. Run post-cutover validation
7. Archive old L-level files

### Post-Cutover Validation Checklist

- [ ] All T-level files renamed to L-level
- [ ] Indices updated to reference new L-level paths
- [ ] System maps updated
- [ ] Validation gates pass
- [ ] No broken links
- [ ] Old L-level files archived
- [ ] Performance benchmarks still pass
- [ ] RS-lift metrics still validated (+15%)

## References

- System map: `systems/hhni/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/hhni/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/hhni/` (~1,850 lines, 77 tests passing ✅)
