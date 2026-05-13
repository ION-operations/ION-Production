/**
 * Simulation tests
 */

import { create_igodn_field, create_default_anchors, add_node_to_field } from '../core/field';
import { simulate_igodn } from '../core/simulation';
import { IGODNNode } from '../types';
import { DefaultCompatibilityMatrix, DefaultConflictMatrix, DefaultConstitutionalLinkMatrix } from '../matrices';

describe('IGODN Simulation', () => {
  test('should run simulation with anchors', async () => {
    const anchors = create_default_anchors();
    const field = create_igodn_field(anchors);
    
    const compatibility = new DefaultCompatibilityMatrix();
    const conflict = new DefaultConflictMatrix();
    const constitutional = new DefaultConstitutionalLinkMatrix();
    
    await simulate_igodn(field, compatibility, conflict, constitutional, {
      max_iterations: 10,
      dt: 0.01
    });
    
    expect(field.state.iteration).toBeGreaterThan(0);
    expect(field.state.total_energy).toBeDefined();
  });
  
  test('should handle intent node orbiting anchor', async () => {
    const anchors = create_default_anchors();
    const field = create_igodn_field(anchors);
    
    // Add an intent node
    const intent: IGODNNode = {
      id: 'intent-1',
      type: 'INTENT',
      cluster: 'EXPERIMENTAL',
      position: {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: { x: 2, y: 0, z: 0 },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      },
      velocity: { x: 0, y: 0, z: 0 },
      mass: 1.0,
      perimeter_radius: 0.5,
      metadata: {
        timestamp: new Date().toISOString(),
        intent_authority: 0.7,
        intent_priority: 0.8
      }
    };
    
    add_node_to_field(field, intent);
    
    const compatibility = new DefaultCompatibilityMatrix();
    const conflict = new DefaultConflictMatrix();
    const constitutional = new DefaultConstitutionalLinkMatrix();
    
    await simulate_igodn(field, compatibility, conflict, constitutional, {
      max_iterations: 50,
      dt: 0.01
    });
    
    // Intent should have moved (attracted to anchor)
    const final_intent = field.nodes.get('intent-1');
    expect(final_intent).toBeDefined();
    expect(final_intent!.position.translation.x).not.toBe(2.0); // Should have moved
  });
  
  test('should support incremental mode', async () => {
    const anchors = create_default_anchors();
    const field = create_igodn_field(anchors);
    
    // Run initial simulation
    const compatibility = new DefaultCompatibilityMatrix();
    const conflict = new DefaultConflictMatrix();
    const constitutional = new DefaultConstitutionalLinkMatrix();
    
    await simulate_igodn(field, compatibility, conflict, constitutional, {
      max_iterations: 10
    });
    
    const initial_iteration = field.state.iteration;
    
    // Add new node and run incremental
    const new_intent: IGODNNode = {
      id: 'intent-2',
      type: 'INTENT',
      cluster: 'EXPERIMENTAL',
      position: {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: { x: 3, y: 0, z: 0 },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      },
      velocity: { x: 0, y: 0, z: 0 },
      mass: 1.0,
      perimeter_radius: 0.5,
      metadata: {
        timestamp: new Date().toISOString()
      }
    };
    
    add_node_to_field(field, new_intent);
    
    await simulate_igodn(field, compatibility, conflict, constitutional, {
      max_iterations: 20,
      incremental: true
    });
    
    // Should have more iterations
    expect(field.state.iteration).toBeGreaterThan(initial_iteration);
  });
});

