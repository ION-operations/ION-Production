/**
 * Matrix tests
 */

import { DefaultCompatibilityMatrix, DefaultConflictMatrix, DefaultConstitutionalLinkMatrix } from '../matrices';
import { IGODNNode } from '../types';

const create_test_node = (
  id: string,
  type: IGODNNode['type'],
  cluster: IGODNNode['cluster'] = 'DEFAULT',
  metadata: Partial<IGODNNode['metadata']> = {}
): IGODNNode => ({
  id,
  type,
  cluster,
  position: {
    rotation: { w: 1, x: 0, y: 0, z: 0 },
    translation: { x: 0, y: 0, z: 0 },
    dual: { w: 0, x: 0, y: 0, z: 0 }
  },
  velocity: { x: 0, y: 0, z: 0 },
  mass: 1.0,
  perimeter_radius: 0.5,
  metadata: {
    timestamp: new Date().toISOString(),
    ...metadata
  }
});

describe('Compatibility Matrix', () => {
  const matrix = new DefaultCompatibilityMatrix();
  
  test('should identify anchors as compatible with everything', () => {
    const anchor = create_test_node('anchor', 'ANCHOR', 'SAFETY');
    const intent = create_test_node('intent', 'INTENT', 'EXPERIMENTAL');
    
    expect(matrix.are_compatible(anchor, intent)).toBe(true);
    expect(matrix.get_compatibility_score(anchor, intent)).toBeGreaterThan(0);
  });
  
  test('should identify same cluster nodes as compatible', () => {
    const node1 = create_test_node('node1', 'CONTRACT', 'SAFETY');
    const node2 = create_test_node('node2', 'CONTRACT', 'SAFETY');
    
    expect(matrix.are_compatible(node1, node2)).toBe(true);
  });
  
  test('should identify contracts with overlapping scopes as compatible', () => {
    const node1 = create_test_node('node1', 'CONTRACT', 'SAFETY', {
      contract_scope: {
        systems: ['system1', 'system2'],
        components: []
      }
    });
    const node2 = create_test_node('node2', 'CONTRACT', 'SAFETY', {
      contract_scope: {
        systems: ['system2', 'system3'],
        components: []
      }
    });
    
    expect(matrix.are_compatible(node1, node2)).toBe(true);
  });
});

describe('Conflict Matrix', () => {
  const matrix = new DefaultConflictMatrix();
  
  test('should not conflict anchors with each other', () => {
    const anchor1 = create_test_node('anchor1', 'ANCHOR', 'SAFETY');
    const anchor2 = create_test_node('anchor2', 'ANCHOR', 'SAFETY');
    
    expect(matrix.are_conflicting(anchor1, anchor2)).toBe(false);
  });
  
  test('should identify low-authority intents conflicting with safety', () => {
    const intent = create_test_node('intent', 'INTENT', 'EXPERIMENTAL', {
      intent_authority: 0.3
    });
    const safety_contract = create_test_node('safety', 'CONTRACT', 'SAFETY');
    safety_contract.mass = 10.0;
    
    expect(matrix.are_conflicting(intent, safety_contract)).toBe(true);
  });
});

describe('Constitutional Link Matrix', () => {
  const matrix = new DefaultConstitutionalLinkMatrix();
  
  test('should link anchors to safety contracts', () => {
    const anchor = create_test_node('anchor', 'ANCHOR', 'SAFETY');
    const contract = create_test_node('contract', 'CONTRACT', 'SAFETY');
    
    expect(matrix.are_linked(anchor, contract)).toBe(true);
    expect(matrix.get_link_strength(anchor, contract)).toBeGreaterThan(0.5);
  });
  
  test('should link contracts with parent-child scope relationships', () => {
    const parent = create_test_node('parent', 'CONTRACT', 'SAFETY', {
      contract_scope: {
        systems: ['system1', 'system2', 'system3'],
        components: []
      }
    });
    const child = create_test_node('child', 'CONTRACT', 'SAFETY', {
      contract_scope: {
        systems: ['system1', 'system2'],
        components: []
      }
    });
    
    expect(matrix.are_linked(parent, child)).toBe(true);
  });
});

