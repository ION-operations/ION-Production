# Holographic Memory - Quick Start Guide

**Status:** Experimental/Additive Enhancement  
**Version:** 0.1.0

## Installation

```bash
# Install dependencies
pip install numpy

# No additional installation needed - package is part of AIM-OS
```

## Enable Holographic Memory

```bash
# Set environment variable
export ENABLE_HOLOGRAPHIC_MEMORY=true
```

Or in Python:
```python
import os
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"
```

## Basic Usage

### 1. Core Holographic Memory

```python
from holographic_memory import AIMO_HoloMemory
import numpy as np

# Initialize
memory = AIMO_HoloMemory(dimension=10000)

# Create test data
data_vector = np.random.randn(10000)
label_vector = np.random.randn(10000)
data_vector = data_vector / np.linalg.norm(data_vector)
label_vector = label_vector / np.linalg.norm(label_vector)

# Encode and store
composite = memory.encode(data_vector, label_vector)
memory_id = memory.store(composite, label_vector)

# Retrieve
reconstructed, fidelity = memory.decode(label_vector)
print(f"Reconstruction fidelity: {fidelity:.3f}")

# Find similar
similar = memory.correlate(data_vector, top_k=5)
print(f"Found {len(similar)} similar memories")
```

### 2. CMC Integration

```python
from holographic_memory import CMC_HoloIntegration
from cmc_service.memory_store import MemoryStore, AtomCreate, AtomContent

# Initialize CMC (primary)
cmc = MemoryStore(base_path="./cmc_data")

# Initialize holographic integration (experimental)
holo = CMC_HoloIntegration()

# Create atom in CMC (primary - always happens)
atom = cmc.create_atom(AtomCreate(
    modality="text",
    content=AtomContent(inline="Example memory"),
    tags={"topic": 0.9}
))

# Additionally store in holographic memory (if enabled)
if holo.is_enabled():
    atom_dict = atom.model_dump()
    holo.store_atom(atom_dict, atom.id)
    
    # Associative retrieval (fuzzy matching)
    suggestions = holo.retrieve_associative("memory about example", top_k=5)
    for semantic_id, correlation, fidelity in suggestions:
        print(f"Found: {semantic_id} (correlation: {correlation:.3f})")
```

### 3. SEG Integration

```python
from holographic_memory import SEG_HoloIntegration
from seg import SEGraph, Entity, Relation, RelationType

# Initialize SEG (primary)
seg = SEGraph()

# Initialize holographic integration (experimental)
holo = SEG_HoloIntegration()

# Create entity in SEG (primary)
entity = Entity(
    type="concept",
    name="Machine Learning",
    attributes={"field": "ai"}
)
entity = seg.add_entity(entity)

# Additionally store in holographic memory (if enabled)
if holo.is_enabled():
    entity_dict = entity.model_dump()
    holo.store_entity(entity_dict, entity.id)
    
    # Create relationship
    relation = Relation(
        source_id=entity.id,
        target_id=target_entity.id,
        relation_type=RelationType.RELATES_TO
    )
    relation = seg.add_relation(relation)
    
    # Store relationship holographically
    relation_dict = relation.model_dump()
    holo.store_relationship(relation_dict, relation.source_id, relation.target_id)
    
    # Infer relationships (find targets from source + type)
    targets = holo.infer_relationship(entity.id, "relates_to")
    for target_id, correlation, fidelity in targets:
        print(f"Inferred target: {target_id} (correlation: {correlation:.3f})")
```

### 4. Cognitive Component Integration

```python
from holographic_memory import (
    VIF_HoloIntegration,
    APOE_HoloIntegration,
    SIS_HoloIntegration,
    CAS_HoloIntegration,
)
from holographic_memory import CMC_HoloIntegration, SEG_HoloIntegration

# Initialize base integrations
cmc_holo = CMC_HoloIntegration()
seg_holo = SEG_HoloIntegration()

# VIF: Additional confidence signal
vif_holo = VIF_HoloIntegration(cmc_integration=cmc_holo)
if vif_holo.is_enabled():
    plix_intent = {"goal": "Test goal", "process": "Test process"}
    confidence = vif_holo.compute_confidence_from_reconstruction(
        plix_intent, semantic_id="semantic_123"
    )
    if confidence:
        print(f"Holographic confidence: {confidence:.3f}")

# APOE: Plan suggestions
apoe_holo = APOE_HoloIntegration(cmc_integration=cmc_holo)
if apoe_holo.is_enabled():
    plans = apoe_holo.retrieve_associative_plans(plix_intent, top_k=5)
    for plan_id, correlation, fidelity in plans:
        print(f"Plan suggestion: {plan_id} (correlation: {correlation:.3f})")

# SIS: Association learning
sis_holo = SIS_HoloIntegration(cmc_integration=cmc_holo)
if sis_holo.is_enabled():
    # Reinforce successful pattern
    sis_holo.reinforce_association("pattern_123", success=True, strength=0.1)
    # Weaken failed pattern
    sis_holo.reinforce_association("pattern_456", success=False, strength=0.1)

# CAS: Meta-cognition
cas_holo = CAS_HoloIntegration(
    cmc_integration=cmc_holo,
    seg_integration=seg_holo
)
if cas_holo.is_enabled():
    # Analyze holographic state
    insights = cas_holo.analyze_holographic_state()
    print(f"Memory density: {insights.get('memory_density', 0):.3f}")
    print(f"Coherence score: {insights.get('coherence_score', 0):.3f}")
    
    # Detect ambiguity
    ambiguity = cas_holo.detect_ambiguity("test query", threshold=0.7)
    if ambiguity.get("ambiguous"):
        print(f"Ambiguity detected: {ambiguity['strong_matches']} strong matches")
```

## Complete Example

```python
import os
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"

from holographic_memory import (
    CMC_HoloIntegration,
    SEG_HoloIntegration,
    VIF_HoloIntegration,
    APOE_HoloIntegration,
    SIS_HoloIntegration,
    CAS_HoloIntegration,
)
from cmc_service.memory_store import MemoryStore, AtomCreate, AtomContent
from seg import SEGraph, Entity, Relation, RelationType

# Initialize primary systems
cmc = MemoryStore(base_path="./cmc_data")
seg = SEGraph()

# Initialize holographic integrations
cmc_holo = CMC_HoloIntegration()
seg_holo = SEG_HoloIntegration()
vif_holo = VIF_HoloIntegration(cmc_integration=cmc_holo)
apoe_holo = APOE_HoloIntegration(cmc_integration=cmc_holo)
sis_holo = SIS_HoloIntegration(cmc_integration=cmc_holo)
cas_holo = CAS_HoloIntegration(
    cmc_integration=cmc_holo,
    seg_integration=seg_holo
)

# Store memory atom (primary + holographic)
atom = cmc.create_atom(AtomCreate(
    modality="text",
    content=AtomContent(inline="User prefers Python over JavaScript"),
    tags={"preference": 0.9, "language": 0.8}
))

if cmc_holo.is_enabled():
    cmc_holo.store_atom(atom.model_dump(), atom.id)
    
    # Fuzzy search
    suggestions = cmc_holo.retrieve_associative("user preference", top_k=3)
    print(f"Found {len(suggestions)} related memories")

# Store entity (primary + holographic)
entity = seg.add_entity(Entity(
    type="person",
    name="User",
    attributes={"preference": "Python"}
))

if seg_holo.is_enabled():
    seg_holo.store_entity(entity.model_dump(), entity.id)
    
    # Relationship inference
    targets = seg_holo.infer_relationship(entity.id, "prefers")
    print(f"Inferred {len(targets)} relationships")

# Get statistics
if cas_holo.is_enabled():
    insights = cas_holo.analyze_holographic_state()
    print(f"System state: {insights}")
```

## Key Points

1. **Always check `is_enabled()`** before using holographic features
2. **Primary systems work unchanged** - holographic is additive
3. **Errors are logged** but don't affect primary operations
4. **Can disable anytime** - set `ENABLE_HOLOGRAPHIC_MEMORY=false` or don't set it

## Troubleshooting

**Holographic memory not working?**
- Check `ENABLE_HOLOGRAPHIC_MEMORY=true` is set
- Check `is_enabled()` returns `True`
- Check logs for errors (warnings are non-fatal)

**Performance issues?**
- Reduce dimension (default: 10000, try 1000 for testing)
- Disable if not needed (zero overhead when disabled)

**Integration not found?**
- Ensure package is in Python path
- Check imports are correct

---

**Remember:** This is experimental. Core systems continue working normally when disabled.

