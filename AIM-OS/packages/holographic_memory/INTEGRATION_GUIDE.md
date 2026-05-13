# CMC Holographic Memory Integration Guide

**Status:** Experimental/Additive Enhancement  
**Version:** 0.1.0

## Overview

This guide explains how to use the experimental holographic memory integration with CMC. This is an **optional, additive enhancement** that works alongside (not replacing) primary CMC storage.

## Configuration

### Enable Holographic Memory

Set environment variable:
```bash
export ENABLE_HOLOGRAPHIC_MEMORY=true
```

Or in Python:
```python
import os
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"
```

**Default:** Disabled (`false`) - core CMC works unchanged

## Usage

### Basic Integration

```python
from holographic_memory.cmc_integration import CMC_HoloIntegration

# Initialize integration
integration = CMC_HoloIntegration()

# Check if enabled
if integration.is_enabled():
    # Store atom (called AFTER primary CMC storage)
    atom = {
        "id": "atom_123",
        "modality": "text",
        "content": {"inline": "Example memory"},
        "tags": [{"key": "topic", "value": "example"}]
    }
    memory_id = integration.store_atom(atom, "semantic_123")
    
    # Retrieve exact (additional retrieval path)
    result = integration.retrieve_exact("semantic_123")
    if result:
        reconstructed, fidelity = result
        print(f"Reconstruction fidelity: {fidelity:.3f}")
    
    # Retrieve associatively (fuzzy matching)
    suggestions = integration.retrieve_associative("memory about example", top_k=5)
    for semantic_id, correlation, fidelity in suggestions:
        print(f"Found: {semantic_id} (correlation: {correlation:.3f}, fidelity: {fidelity:.3f})")
```

### Integration with CMC MemoryStore

```python
from cmc_service.memory_store import MemoryStore
from holographic_memory.cmc_integration import CMC_HoloIntegration

# Initialize CMC (primary storage)
cmc = MemoryStore(base_path="./cmc_data")

# Initialize holographic integration (experimental)
holo_integration = CMC_HoloIntegration()

# Create atom in CMC (primary)
atom_create = AtomCreate(
    modality="text",
    content=AtomContent(inline="Example memory"),
    tags=[{"key": "topic", "value": "example"}]
)
atom = cmc.create_atom(atom_create)

# Additionally store in holographic memory (if enabled)
if holo_integration.is_enabled():
    atom_dict = atom.model_dump()
    holo_integration.store_atom(atom_dict, atom.id)
```

### Retrieval Pattern

```python
# Primary retrieval from CMC
atom = cmc.get_atom("semantic_123")

# Additional associative retrieval (if enabled)
if holo_integration.is_enabled():
    # Exact retrieval (additional path)
    holo_result = holo_integration.retrieve_exact("semantic_123")
    
    # Fuzzy/associative retrieval (suggestions)
    suggestions = holo_integration.retrieve_associative("partial query", top_k=10)
    
    # Combine results
    results = {
        "primary": atom,  # From CMC
        "holographic_suggestions": suggestions,  # From holographic memory
        "source": "cmc+holo" if suggestions else "cmc"
    }
```

## Key Points

1. **Non-Breaking:** Primary CMC operations unchanged
2. **Opt-In:** Must be explicitly enabled
3. **Additive:** Provides additional capabilities, not replacements
4. **Graceful Degradation:** Errors don't affect primary CMC
5. **Experimental:** Can be disabled/removed without impact

## Statistics

```python
stats = holo_integration.get_stats()
print(stats)
# {
#     "enabled": True,
#     "semantic_id_count": 42,
#     "holo_memory": {
#         "dimension": 10000,
#         "memory_count": 42,
#         ...
#     }
# }
```

## Error Handling

All holographic operations are wrapped in try/except:
- Errors are logged but don't affect primary CMC
- Failed holographic storage → CMC storage still succeeds
- Failed holographic retrieval → CMC retrieval still works

## Future Enhancements

- Semantic embeddings for query vectorization (currently hash-based)
- Better correlation scoring
- Integration with HHNI for improved retrieval
- Performance optimizations

---

**Remember:** This is experimental. Core CMC continues working normally when disabled.

