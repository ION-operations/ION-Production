#!/usr/bin/env python3
"""
Example: TCS Timeline Entry → SEG Evidence Node Integration

Demonstrates Priority 1 gate unlocking workflow:
1. TCS creates timeline entry
2. TCS stores in CMC (gets atom_id)
3. SEG ingests timeline entry (creates evidence node)
4. Capture gate evidence tuple (timeline_prompt_id, atom_id, evidence_id)

This example can be used by Nexus + Atlas to test the integration
and capture gate evidence for gate_system_map_integrity and gate_dual_system.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from seg.seg_graph import SEGraph
from seg.tcs_integration import ingest_timeline_entry


def example_tcs_seg_integration():
    """
    Example workflow for TCS → SEG integration.
    
    This demonstrates the Priority 1 gate unlocking workflow.
    """
    # Initialize SEG graph
    graph = SEGraph()
    
    # Step 1: Simulate TCS timeline entry creation
    # (In real workflow, this comes from PromptContextTracker)
    timeline_entry = {
        "prompt_id": "prompt_example_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Example timeline entry for TCS→SEG integration test",
        "context_index": {
            "active_tasks": ["TCS→SEG integration"],
            "files_read": [
                "packages/seg/models.py",
                "packages/timeline_context_system/prompt_context_tracker.py",
            ],
            "insights_gained": [
                "Timeline entries can be transformed into SEG evidence nodes",
                "CMC atom_id provides the link between TCS and SEG",
            ],
            "decisions_made": [
                {
                    "decision": "Implement TCS→SEG integration function",
                    "impact": "Unlock gate_system_map_integrity and gate_dual_system",
                }
            ],
        },
        "confidence_metrics": {
            "average_confidence": 0.92,
            "high_confidence_areas": ["integration", "mapping"],
        },
        "relevance_score": 0.90,
    }
    
    # Step 2: Simulate CMC atom storage
    # (In real workflow, this comes from TimelineMemoryStore.create_atom())
    atom_id = "atom_example_001"  # Would be returned from CMC
    
    # Step 3: Optional VIF witness (if VIF observes timeline)
    witness_id = None  # Optional - would be provided if VIF observes
    
    # Step 4: Ingest timeline entry into SEG
    gate_evidence = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        witness_id=witness_id,
        graph=graph,
    )
    
    # Step 5: Verify gate evidence tuple
    print("✅ Gate Evidence Tuple Captured:")
    print(f"   timeline_prompt_id: {gate_evidence['timeline_prompt_id']}")
    print(f"   atom_id: {gate_evidence['atom_id']}")
    print(f"   evidence_id: {gate_evidence['evidence_id']}")
    
    # Step 6: Verify evidence node in graph
    evidence = graph.get_evidence(gate_evidence["evidence_id"])
    if evidence:
        print("\n✅ Evidence Node Created:")
        print(f"   Content: {evidence.content[:60]}...")
        print(f"   Source: {evidence.source}")
        print(f"   Confidence: {evidence.confidence}")
        print(f"   Atom ID: {evidence.atom_id}")
        print(f"   Metadata keys: {list(evidence.metadata.keys())}")
    
    return gate_evidence


if __name__ == "__main__":
    print("TCS → SEG Integration Example")
    print("=" * 50)
    gate_evidence = example_tcs_seg_integration()
    print("\n" + "=" * 50)
    print("✅ Integration example complete!")
    print(f"\nGate Evidence Tuple: {gate_evidence}")

