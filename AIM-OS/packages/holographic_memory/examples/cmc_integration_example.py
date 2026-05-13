"""CMC integration example for holographic memory.

Demonstrates using holographic memory with CMC as an experimental enhancement.
"""

import os
import tempfile
from pathlib import Path

# Enable holographic memory
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"

from holographic_memory import CMC_HoloIntegration
from cmc_service.memory_store import MemoryStore, AtomCreate, AtomContent


def main():
    """Demonstrate CMC holographic integration."""
    
    print("=== CMC Holographic Memory Integration ===\n")
    
    # Create temporary directory for CMC
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize CMC (primary storage)
        print("1. Initializing CMC (primary storage)...")
        cmc = MemoryStore(base_path=Path(tmpdir))
        print("   CMC initialized\n")
        
        # Initialize holographic integration (experimental)
        print("2. Initializing holographic integration...")
        holo = CMC_HoloIntegration(dimension=1000)  # Smaller for demo
        print(f"   Holographic memory enabled: {holo.is_enabled()}\n")
        
        if not holo.is_enabled():
            print("   ⚠️  Holographic memory is disabled. Set ENABLE_HOLOGRAPHIC_MEMORY=true")
            return
        
        # Create atoms in CMC (primary)
        print("3. Creating memory atoms in CMC...")
        atoms = []
        for i in range(5):
            atom = cmc.create_atom(AtomCreate(
                modality="text",
                content=AtomContent(inline=f"Memory {i}: User prefers Python for data science"),
                tags={"topic": 0.9, "language": 0.8}
            ))
            atoms.append(atom)
            print(f"   Created atom {i+1}: {atom.id[:12]}...")
        
        print()
        
        # Additionally store in holographic memory (experimental)
        print("4. Storing atoms in holographic memory (experimental)...")
        for atom in atoms:
            atom_dict = atom.model_dump()
            holo_id = holo.store_atom(atom_dict, atom.id)
            if holo_id:
                print(f"   Stored {atom.id[:12]}... in holographic memory: {holo_id[:8]}...")
        
        print()
        
        # Exact retrieval (additional path)
        print("5. Exact retrieval from holographic memory...")
        result = holo.retrieve_exact(atoms[0].id)
        if result:
            reconstructed, fidelity = result
            print(f"   Retrieved {atoms[0].id[:12]}... (fidelity: {fidelity:.3f})")
        
        print()
        
        # Associative retrieval (fuzzy matching)
        print("6. Associative retrieval (fuzzy matching)...")
        suggestions = holo.retrieve_associative("user preference Python", top_k=3)
        print(f"   Found {len(suggestions)} suggestions:")
        for semantic_id, correlation, fidelity in suggestions:
            print(f"     {semantic_id[:12]}... (correlation: {correlation:.3f}, fidelity: {fidelity:.3f})")
        
        print()
        
        # Statistics
        print("7. Integration statistics...")
        stats = holo.get_stats()
        print(f"   Enabled: {stats['enabled']}")
        if stats['enabled']:
            print(f"   Semantic ID count: {stats['semantic_id_count']}")
            holo_stats = stats.get('holo_memory', {})
            print(f"   Holographic memory count: {holo_stats.get('memory_count', 0)}")
        
        print("\n=== Demo Complete ===")
        print("\nNote: Primary CMC storage succeeded regardless of holographic results.")


if __name__ == "__main__":
    main()

