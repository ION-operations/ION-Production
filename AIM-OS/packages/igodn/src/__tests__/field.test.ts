/**
 * Basic field tests
 */

import { 
  create_igodn_field, 
  add_node_to_field, 
  create_default_anchors,
  infer_cluster
} from '../core/field';
import { IGODNNode } from '../types';

describe('IGODN Field', () => {
  test('should create empty field', () => {
    const field = create_igodn_field();
    expect(field.nodes.size).toBe(0);
    expect(field.state.iteration).toBe(0);
    expect(field.state.converged).toBe(false);
  });
  
  test('should create field with nodes', () => {
    const nodes: IGODNNode[] = [
      {
        id: 'test-node-1',
        type: 'INTENT',
        cluster: 'EXPERIMENTAL',
        position: {
          rotation: { w: 1, x: 0, y: 0, z: 0 },
          translation: { x: 0, y: 0, z: 0 },
          dual: { w: 0, x: 0, y: 0, z: 0 }
        },
        velocity: { x: 0, y: 0, z: 0 },
        mass: 1.0,
        perimeter_radius: 0.5,
        metadata: {
          timestamp: new Date().toISOString()
        }
      }
    ];
    
    const field = create_igodn_field(nodes);
    expect(field.nodes.size).toBe(1);
    expect(field.nodes.get('test-node-1')).toBeDefined();
  });
  
  test('should add node to field', () => {
    const field = create_igodn_field();
    
    const node: IGODNNode = {
      id: 'test-node-2',
      type: 'CONTRACT',
      cluster: 'DEFAULT',
      position: {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: { x: 1, y: 0, z: 0 },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      },
      velocity: { x: 0, y: 0, z: 0 },
      mass: 1.5,
      perimeter_radius: 0.5,
      metadata: {
        timestamp: new Date().toISOString(),
        contract_kind: 'Constraint'
      }
    };
    
    add_node_to_field(field, node);
    expect(field.nodes.size).toBe(1);
    expect(field.nodes.get('test-node-2')).toBeDefined();
    expect(field.nodes.get('test-node-2')?.cluster).toBe('SAFETY'); // Auto-assigned
  });
  
  test('should create default anchors', () => {
    const anchors = create_default_anchors();
    expect(anchors.length).toBe(4);
    expect(anchors.every(a => a.type === 'ANCHOR')).toBe(true);
    expect(anchors.every(a => a.cluster === 'SAFETY')).toBe(true);
  });
});

describe('Cluster Inference', () => {
  test('should infer SAFETY cluster for anchors', () => {
    const node: IGODNNode = {
      id: 'anchor',
      type: 'ANCHOR',
      cluster: 'DEFAULT', // Will be inferred
      position: {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: { x: 0, y: 0, z: 0 },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      },
      velocity: { x: 0, y: 0, z: 0 },
      mass: 10.0,
      perimeter_radius: 1.0,
      metadata: {
        timestamp: new Date().toISOString()
      }
    };
    
    const cluster = infer_cluster(node);
    expect(cluster).toBe('SAFETY');
  });
  
  test('should infer EXPERIMENTAL cluster for intents', () => {
    const node: IGODNNode = {
      id: 'intent',
      type: 'INTENT',
      cluster: 'DEFAULT',
      position: {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: { x: 0, y: 0, z: 0 },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      },
      velocity: { x: 0, y: 0, z: 0 },
      mass: 1.0,
      perimeter_radius: 0.5,
      metadata: {
        timestamp: new Date().toISOString()
      }
    };
    
    const cluster = infer_cluster(node);
    expect(cluster).toBe('EXPERIMENTAL');
  });
  
  test('should infer PERFORMANCE cluster for metrics', () => {
    const node: IGODNNode = {
      id: 'metric',
      type: 'METRIC',
      cluster: 'DEFAULT',
      position: {
        rotation: { w: 1, x: 0, y: 0, z: 0 },
        translation: { x: 0, y: 0, z: 0 },
        dual: { w: 0, x: 0, y: 0, z: 0 }
      },
      velocity: { x: 0, y: 0, z: 0 },
      mass: 1.0,
      perimeter_radius: 0.5,
      metadata: {
        timestamp: new Date().toISOString()
      }
    };
    
    const cluster = infer_cluster(node);
    expect(cluster).toBe('PERFORMANCE');
  });
});

