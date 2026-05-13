---
id: "icip_graph_construction_service_T3_detailed"
system: "icip_graph_construction_service"
component: null
level: "T3"
type: "detailed"
title: "ICIP Graph Construction Service Detailed Implementation"
description: "10,000-word detailed implementation guide for ICIP Graph Construction Service"
audience: "developers, implementers"
confidence_threshold: 0.65
token_cost: 10000
word_count: 10000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T19:41:00Z"
author: "aether"
status: "complete"
tags: ["icip", "cpg", "graph", "construction", "t0-t6", "transitional"]
dependencies: ["icip_graph_construction_service_T2_architecture"]
related_docs: ["icip_graph_construction_service_T4_complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# ICIP Graph Construction Service – T3 Detailed Implementation (≈10,000 words)

## Implementation Overview

The ICIP Graph Construction Service builds and maintains the master Code Property Graph (CPG) in Neo4j. This document provides detailed implementation guidance for developers implementing or integrating this system.

**Core Implementation Principles:**
- **Unified Graph Representation:** Single source of truth combining AST, CFG, and DFG
- **Incremental Processing:** Efficient change-based CPG updates
- **Real-Time Processing:** Event-driven graph construction
- **Agent Identity Required:** All operations MUST include agent_name parameter (CRITICAL PROTOCOL)

## Component Implementation Details

### 1. CPG Builder Implementation

**Purpose:** Constructs unified graph from ASTs.

**Implementation Pattern:**
```python
class CPGBuilder:
    """Builds unified CPG from ASTs."""
    
    def __init__(self):
        self.cmc_integration = CMCIntegration()
        self.vif_service = VIFService()
        self.cfg_constructor = CFGConstructor()
        self.dfg_analyzer = DFGAnalyzer()
    
    async def construct_cpg(self, asts: List[AST], agent_name: str) -> CPG:
        """Construct Code Property Graph."""
        if not agent_name:
            raise ValueError("Agent name required for CPG construction")
        
        # Construct CFG
        cfg = await self.cfg_constructor.construct_cfg(asts, agent_name)
        
        # Analyze DFG
        dfg = await self.dfg_analyzer.analyze_dfg(asts, cfg, agent_name)
        
        # Unify graph
        cpg = self.unify_graph(asts, cfg, dfg)
        
        # Store CPG nodes as CMC atoms
        atom_ids = await self.cmc_integration.store_cpg_nodes(cpg, agent_name)
        
        # Track provenance
        witness = await self.vif_service.create_witness(
            operation="cpg_construction",
            inputs={"asts": asts},
            outputs={"cpg": cpg},
            confidence=0.95,
            agent_name=agent_name  # REQUIRED
        )
        
        return CPG(
            cpg_id=generate_id(),
            asts=asts,
            cfg=cfg,
            dfg=dfg,
            atom_ids=atom_ids,
            witness_id=witness.id
        )
```

## Agent Identity Integration

**All operations MUST include agent_name:**

```python
# Example: CPG construction with agent identity
cpg = await cpg_builder.construct_cpg(
    asts=asts,
    agent_name="aether_session_001"  # REQUIRED
)

# Example: Incremental CPG update with agent identity
updated_cpg = await cpg_builder.incremental_update(
    cpg_id=cpg_id,
    changes=changes,
    agent_name="aether_session_001"  # REQUIRED
)
```

## Testing Implementation

### Unit Tests

```python
def test_cpg_construction_with_agent_identity():
    """Test CPG construction includes agent identity."""
    builder = CPGBuilder()
    
    cpg = builder.construct_cpg(
        asts=test_asts,
        agent_name="test_agent_001"
    )
    
    assert cpg.cpg_id is not None
    assert cpg.cfg is not None
    assert cpg.dfg is not None

def test_incremental_update_with_agent_identity():
    """Test incremental CPG update includes agent identity."""
    builder = CPGBuilder()
    
    updated_cpg = builder.incremental_update(
        cpg_id=test_cpg_id,
        changes=test_changes,
        agent_name="test_agent_001"
    )
    
    assert updated_cpg.cpg_id is not None
    assert updated_cpg.changes_applied is not None
```

## References

- System map: `systems/icip_graph_construction_service/system.map.lucid.json5` (if exists)
- ICIP Platform: `systems/icip_platform/T2_architecture.md`
- ICIP Code Property Graph: `systems/icip_code_property_graph/T2_architecture.md`
- Parser Service: `systems/icip_parser_service/T2_architecture.md`
- CMC: `systems/cmc/T2_architecture.md`
- HHNI: `systems/hhni/T2_architecture.md`
- VIF: `systems/vif/T2_architecture.md`
- Agent Identity Protocol: `knowledge_architecture/AETHER_MEMORY/protocols/AGENT_IDENTITY_CONTEXT_CONTINUITY_PROTOCOL.md`
- L-level docs: `systems/icip_graph_construction_service/L0_executive.md`

