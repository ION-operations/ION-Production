"""Basic usage example for AIMO_HoloMemory.

Demonstrates core holographic memory operations.
"""

import os
import numpy as np

# Enable holographic memory
os.environ["ENABLE_HOLOGRAPHIC_MEMORY"] = "true"

from holographic_memory import AIMO_HoloMemory


def main():
    """Demonstrate basic holographic memory operations."""
    
    print("=== AIMO_HoloMemory Basic Usage ===\n")
    
    # Initialize
    print("1. Initializing holographic memory...")
    memory = AIMO_HoloMemory(dimension=1000)  # Smaller for demo
    print(f"   Dimension: {memory.dimension}")
    print(f"   Normalize: {memory.normalize}\n")
    
    # Create test data
    print("2. Creating test data...")
    data_vector = np.random.randn(1000)
    label_vector = np.random.randn(1000)
    data_vector = data_vector / np.linalg.norm(data_vector)
    label_vector = label_vector / np.linalg.norm(label_vector)
    print(f"   Data vector shape: {data_vector.shape}")
    print(f"   Label vector shape: {label_vector.shape}\n")
    
    # Encode
    print("3. Encoding data with label...")
    composite = memory.encode(data_vector, label_vector)
    print(f"   Composite vector shape: {composite.shape}")
    print(f"   Composite norm: {np.linalg.norm(composite):.3f}\n")
    
    # Store
    print("4. Storing in holographic memory...")
    memory_id = memory.store(composite, label_vector)
    print(f"   Memory ID: {memory_id}\n")
    
    # Decode
    print("5. Decoding from holographic memory...")
    reconstructed, fidelity = memory.decode(label_vector)
    print(f"   Reconstructed shape: {reconstructed.shape}")
    print(f"   Reconstruction fidelity: {fidelity:.3f}\n")
    
    # Store multiple memories
    print("6. Storing multiple memories...")
    for i in range(5):
        data = np.random.randn(1000)
        label = np.random.randn(1000)
        data = data / np.linalg.norm(data)
        label = label / np.linalg.norm(label)
        
        composite = memory.encode(data, label)
        memory_id = memory.store(composite, label)
        print(f"   Stored memory {i+1}: {memory_id[:8]}...")
    
    # Correlate
    print("\n7. Finding similar memories...")
    query_vector = data_vector.copy()
    similar = memory.correlate(query_vector, top_k=3)
    print(f"   Found {len(similar)} similar memories:")
    for memory_id, correlation in similar:
        print(f"     {memory_id[:8]}... (correlation: {correlation:.3f})")
    
    # Statistics
    print("\n8. Memory statistics...")
    stats = memory.get_memory_stats()
    print(f"   Memory count: {stats['memory_count']}")
    print(f"   Memory array norm: {stats['memory_array_norm']:.3f}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

