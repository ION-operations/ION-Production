/**
 * Distance calculation tests
 */

import { compute_distance_decomposed } from '../core/distance';
import { IGODNNode } from '../types';

describe('Distance Decomposition', () => {
  const create_test_node = (id: string, x: number = 0, y: number = 0, z: number = 0): IGODNNode => ({
    id,
    type: 'INTENT',
    cluster: 'EXPERIMENTAL',
    position: {
      rotation: { w: 1, x: 0, y: 0, z: 0 },
      translation: { x, y, z },
      dual: { w: 0, x: 0, y: 0, z: 0 }
    },
    velocity: { x: 0, y: 0, z: 0 },
    mass: 1.0,
    perimeter_radius: 0.5,
    metadata: {
      timestamp: new Date().toISOString()
    }
  });
  
  test('should compute spatial distance correctly', () => {
    const node1 = create_test_node('node1', 0, 0, 0);
    const node2 = create_test_node('node2', 3, 4, 0);
    
    const dist = compute_distance_decomposed(node1, node2);
    
    // Spatial distance should be 5 (3-4-5 triangle)
    expect(dist.spatial).toBeCloseTo(5.0, 5);
  });
  
  test('should compute combined distance', () => {
    const node1 = create_test_node('node1', 0, 0, 0);
    const node2 = create_test_node('node2', 1, 0, 0);
    
    const dist = compute_distance_decomposed(node1, node2);
    
    // Combined should be weighted sum
    expect(dist.combined).toBeGreaterThan(0);
    expect(dist.combined).toBeLessThanOrEqual(1.0);
  });
  
  test('should handle zero distance', () => {
    const node1 = create_test_node('node1', 0, 0, 0);
    const node2 = create_test_node('node2', 0, 0, 0);
    
    const dist = compute_distance_decomposed(node1, node2);
    
    expect(dist.spatial).toBeCloseTo(0, 5);
  });
});

