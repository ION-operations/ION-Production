"""Cognitive component integration example.

Demonstrates using holographic memory with VIF, APOE, SIS, and CAS.
"""

import os
import tempfile
from pathlib import Path

# Enable holographic memory
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


def main():
    """Demonstrate cognitive component holographic integration."""
    
    print("=== Cognitive Component Holographic Integration ===\n")
    
    # Create temporary directory for CMC
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize base integrations
        print("1. Initializing base integrations...")
        cmc = MemoryStore(base_path=Path(tmpdir))
        cmc_holo = CMC_HoloIntegration(dimension=1000)
        seg_holo = SEG_HoloIntegration(dimension=1000)
        print(f"   CMC holographic enabled: {cmc_holo.is_enabled()}")
        print(f"   SEG holographic enabled: {seg_holo.is_enabled()}\n")
        
        if not cmc_holo.is_enabled():
            print("   ⚠️  Holographic memory is disabled. Set ENABLE_HOLOGRAPHIC_MEMORY=true")
            return
        
        # Store some atoms for testing
        print("2. Storing test atoms...")
        for i in range(3):
            atom = cmc.create_atom(AtomCreate(
                modality="text",
                content=AtomContent(inline=f"Test memory {i}"),
                tags={"test": 0.9}
            ))
            if cmc_holo.is_enabled():
                cmc_holo.store_atom(atom.model_dump(), atom.id)
        print("   Stored 3 test atoms\n")
        
        # VIF Integration
        print("3. VIF Integration - Confidence from reconstruction...")
        vif_holo = VIF_HoloIntegration(cmc_integration=cmc_holo, dimension=1000)
        if vif_holo.is_enabled():
            plix_intent = {
                "goal": "Test goal",
                "process": "Test process",
                "constraint": "Test constraint"
            }
            confidence = vif_holo.compute_confidence_from_reconstruction(
                plix_intent, semantic_id="atom_123"
            )
            if confidence:
                print(f"   Holographic confidence: {confidence:.3f}")
            else:
                print("   No confidence signal available")
        print()
        
        # APOE Integration
        print("4. APOE Integration - Associative plan retrieval...")
        apoe_holo = APOE_HoloIntegration(cmc_integration=cmc_holo, dimension=1000)
        if apoe_holo.is_enabled():
            plix_intent = {"goal": "Complete task", "process": "Step by step"}
            plans = apoe_holo.retrieve_associative_plans(plix_intent, top_k=3)
            print(f"   Found {len(plans)} plan suggestions:")
            for plan_id, correlation, fidelity in plans:
                print(f"     {plan_id[:12]}... (correlation: {correlation:.3f})")
        print()
        
        # SIS Integration
        print("5. SIS Integration - Association reinforcement...")
        sis_holo = SIS_HoloIntegration(cmc_integration=cmc_holo, dimension=1000)
        if sis_holo.is_enabled():
            # Reinforce successful pattern
            success = sis_holo.reinforce_association("pattern_123", success=True, strength=0.1)
            print(f"   Reinforcement result: {success}")
            
            # Weaken failed pattern
            success = sis_holo.reinforce_association("pattern_456", success=False, strength=0.1)
            print(f"   Weakening result: {success}")
        print()
        
        # CAS Integration
        print("6. CAS Integration - Meta-cognition...")
        cas_holo = CAS_HoloIntegration(
            cmc_integration=cmc_holo,
            seg_integration=seg_holo,
            dimension=1000
        )
        if cas_holo.is_enabled():
            # Analyze holographic state
            insights = cas_holo.analyze_holographic_state()
            print(f"   Memory density: {insights.get('memory_density', 0):.3f}")
            print(f"   Coherence score: {insights.get('coherence_score', 0):.3f}")
            if 'memory_count' in insights:
                print(f"   Memory count: {insights['memory_count']}")
            
            # Detect ambiguity
            ambiguity = cas_holo.detect_ambiguity("test query", threshold=0.5)
            print(f"   Ambiguity detected: {ambiguity.get('ambiguous', False)}")
            print(f"   Strong matches: {ambiguity.get('strong_matches', 0)}")
        
        print("\n=== Demo Complete ===")
        print("\nNote: All cognitive components work normally when holographic memory is disabled.")


if __name__ == "__main__":
    main()

