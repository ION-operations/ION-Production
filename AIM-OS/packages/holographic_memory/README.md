# AIMO_HoloMemory - Holographic Memory Integration

**Status:** Experimental implementation complete  
**Version:** 0.1.0  
**Purpose:** **Experimental** distributed associative memory substrate for AIM-OS (additive enhancement, not replacement)

**⚠️ EXPERIMENTAL:** This is an experimental feature. Core CMC and SEG systems continue working unchanged when disabled.

## Overview

`AIMO_HoloMemory` integrates Unified-Holographic-Neural-Network (UHNN) principles into AIM-OS, providing distributed associative memory capabilities that enhance CMC and SEG operations.

## Key Features

- **Distributed Storage:** Memories encoded across entire holographic array
- **Associative Recall:** Retrieve complete patterns from partial queries
- **Fuzzy Matching:** Find memories with noisy or incomplete cues
- **Pattern Completion:** Reconstruct full memories from fragments
- **Emergent Associations:** Discover implicit relationships through holographic similarity

## Installation

```bash
# Install dependencies
pip install numpy

# No additional installation needed - package is part of AIM-OS
```

## Quick Start

```python
import os
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"

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

## Configuration

### Enable Holographic Memory

Set environment variable:
```bash
export ENABLE_HOLOGRAPHIC_MEMORY=true
```

**Default:** Disabled (`false`) - core systems work unchanged

## Core Components

### AIMO_HoloMemory

Main holographic memory class providing:
- `encode()` - Bind data with semantic ID
- `decode()` - Reconstruct data from label/query
- `store()` - Add to distributed memory array
- `update()` - Modify existing memories
- `correlate()` - Find similar memories

### Vectorizers

Convert AIM-OS data to high-dimensional vectors:
- `PLIxVectorizer` - PLIx intents
- `EntityVectorizer` - SEG entities
- `RelationshipVectorizer` - SEG relationships
- `MemoryAtomVectorizer` - CMC memory atoms

## Integration Points (Experimental/Additive)

- **CMC:** **Optional** parallel holographic storage alongside primary CMC operations
- **SEG:** **Optional** parallel holographic encoding alongside primary SEG operations
- **VIF:** **Optional** additional confidence signals from reconstruction fidelity
- **APOE:** **Optional** associative plan suggestions alongside primary plan generation
- **SIS:** **Optional** association reinforcement/weakening
- **CAS:** **Optional** meta-cognition insights from holographic state

**All integrations are opt-in and non-breaking. Core systems work unchanged when disabled.**

## Examples

See `examples/` directory:
- `basic_usage.py` - Core holographic memory operations
- `cmc_integration_example.py` - CMC integration
- `seg_integration_example.py` - SEG integration
- `cognitive_integration_example.py` - Cognitive component integration

## Documentation

- `QUICK_START.md` - Quick start guide
- `INTEGRATION_GUIDE.md` - CMC integration guide
- `SEG_INTEGRATION_GUIDE.md` - SEG integration guide
- `knowledge_architecture/systems/holographic_memory/` - Complete design documentation

## Status

**Current:** All integrations complete (90% overall)  
**Next:** Performance optimization (optional)  
**Tests:** 33 test cases passing

## Design Philosophy

✅ **Experimental:** Opt-in, can be disabled  
✅ **Additive:** Parallel storage, not replacement  
✅ **Non-Breaking:** Core systems unchanged  
✅ **Graceful:** Errors don't affect primary operations  

---

**Remember:** This is experimental. Core CMC and SEG continue working normally when disabled.
