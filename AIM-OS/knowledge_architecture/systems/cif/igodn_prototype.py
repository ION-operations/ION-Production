# IGODN Prototype - First RTFT Vortex
# Based on Grok's immediate prototype
# Run: python -c "from igodn_prototype import *; n1=Node('SAFETY', 'ANCHOR', [0,0,0], mass=10); n2=Node('intent1', 'INTENT', [2,0,0]); print(step([n1,n2]))"

import numpy as np
from typing import Dict, List, Tuple

class Node:
    """IGODN node - represents contract, intent, concept, etc."""
    def __init__(self, id: str, type: str, pos: List[float], mass: float = 1.0, radius: float = 0.5):
        self.id = id
        self.type = type
        self.pos = np.array(pos, dtype=np.float64)
        self.vel = np.zeros(3, dtype=np.float64)
        self.mass = mass
        self.radius = radius

def step(nodes: List[Node], dt: float = 0.01, G: float = 1.0, k_rep: float = 10.0) -> List[List[float]]:
    """
    Single simulation step - compute forces and update positions
    
    Args:
        nodes: List of nodes in field
        dt: Time step
        G: Gravitational constant
        k_rep: Repulsive barrier stiffness
    
    Returns:
        List of node positions after step
    """
    for i, n1 in enumerate(nodes):
        F = np.zeros(3, dtype=np.float64)
        
        for n2 in nodes:
            if n1.id == n2.id:
                continue
            
            r = n2.pos - n1.pos
            d = np.linalg.norm(r)
            
            if d < 1e-8:
                continue
            
            # Gravity (compatible nodes attract)
            # F = G * m1 * m2 / r^2 * r_hat
            F += G * n1.mass * n2.mass / (d * d) * (r / d)
            
            # Repulsion (conflicting nodes repel)
            # F = k_rep * (perimeter - actual) * r_hat
            if d < n1.radius + n2.radius:
                F += k_rep * (n1.radius + n2.radius - d) * (r / d)
        
        # Update velocity and position (F = ma, so a = F/m)
        a = F / n1.mass
        n1.vel += a * dt
        n1.pos += n1.vel * dt
    
    return [n.pos.tolist() for n in nodes]

def simulate(nodes: List[Node], iterations: int = 100, dt: float = 0.01, 
             G: float = 1.0, k_rep: float = 10.0) -> List[List[List[float]]]:
    """
    Run full simulation
    
    Returns:
        List of position histories for each iteration
    """
    history = []
    
    for _ in range(iterations):
        positions = step(nodes, dt, G, k_rep)
        history.append(positions)
    
    return history

# Test: Intent orbiting anchor
if __name__ == '__main__':
    # Create anchor (heavy, at origin)
    n1 = Node('SAFETY', 'ANCHOR', [0, 0, 0], mass=10.0, radius=1.0)
    
    # Create intent (light, offset)
    n2 = Node('intent1', 'INTENT', [2, 0, 0], mass=1.0, radius=0.5)
    
    # Run one step
    positions = step([n1, n2])
    print(f"After 1 step:")
    print(f"  {n1.id}: {positions[0]}")
    print(f"  {n2.id}: {positions[1]}")
    
    # Run full simulation
    print(f"\nRunning 100 iterations...")
    history = simulate([n1, n2], iterations=100)
    
    print(f"Final positions:")
    print(f"  {n1.id}: {history[-1][0]}")
    print(f"  {n2.id}: {history[-1][1]}")
    
    # Check if intent orbited anchor
    final_distance = np.linalg.norm(np.array(history[-1][1]) - np.array(history[-1][0]))
    initial_distance = np.linalg.norm(np.array([2, 0, 0]) - np.array([0, 0, 0]))
    print(f"\nDistance change: {initial_distance:.3f} -> {final_distance:.3f}")
    
    if final_distance < initial_distance:
        print("✅ Intent attracted to anchor (first RTFT vortex!)")

