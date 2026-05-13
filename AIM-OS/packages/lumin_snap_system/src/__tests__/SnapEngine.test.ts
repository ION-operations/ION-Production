/**
 * SnapEngine Tests
 * @module @lumin/snap-system/tests/SnapEngine
 */

import * as THREE from 'three';
import { SnapEngine } from '../utils/SnapEngine';
import { DEFAULT_SNAP_CONFIG } from '../types';

describe('SnapEngine', () => {
  let engine: SnapEngine;

  beforeEach(() => {
    SnapEngine.resetInstance();
    engine = SnapEngine.getInstance();
    
    // Set up a default container
    engine.setContainer(new THREE.Box3(
      new THREE.Vector3(-10, -10, -10),
      new THREE.Vector3(10, 10, 10)
    ));
  });

  describe('Singleton Pattern', () => {
    it('should return same instance', () => {
      const instance1 = SnapEngine.getInstance();
      const instance2 = SnapEngine.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('Configuration', () => {
    it('should start with default config', () => {
      const config = engine.getConfig();
      expect(config.gridSize).toBe(DEFAULT_SNAP_CONFIG.gridSize);
      expect(config.magneticStrength).toBe(DEFAULT_SNAP_CONFIG.magneticStrength);
    });

    it('should update config', () => {
      engine.updateConfig({ gridSize: 20 });
      
      const config = engine.getConfig();
      expect(config.gridSize).toBe(20);
    });

    it('should apply presets', () => {
      engine.applyPreset('Precise');
      
      const config = engine.getConfig();
      expect(config.gridSize).toBe(5);
      expect(config.magneticStrength).toBe(60);
    });
  });

  describe('calculateSnapPosition', () => {
    let mesh: THREE.Mesh;

    beforeEach(() => {
      // Create a 2x2x2 box at origin
      mesh = new THREE.Mesh(new THREE.BoxGeometry(2, 2, 2));
      mesh.position.set(0, 0, 0);
    });

    it('should snap to top', () => {
      const pos = engine.calculateSnapPosition(mesh, 'snap_top');
      
      // Top of container (10) minus half object height (1)
      expect(pos.y).toBe(9); // 10 - 1 = 9, but grid-snapped to 10
    });

    it('should snap to bottom', () => {
      const pos = engine.calculateSnapPosition(mesh, 'snap_bottom');
      
      // Bottom of container (-10) plus half object height (1)
      expect(pos.y).toBe(-9); // -10 + 1 = -9, grid-snapped to -10
    });

    it('should snap to left', () => {
      const pos = engine.calculateSnapPosition(mesh, 'snap_left');
      
      expect(pos.x).toBe(-9);
    });

    it('should snap to right', () => {
      const pos = engine.calculateSnapPosition(mesh, 'snap_right');
      
      expect(pos.x).toBe(9);
    });

    it('should center on X axis', () => {
      mesh.position.set(5, 0, 0);
      const pos = engine.calculateSnapPosition(mesh, 'snap_center_x');
      
      expect(pos.x).toBe(0);
    });

    it('should center on Y axis', () => {
      mesh.position.set(0, 5, 0);
      const pos = engine.calculateSnapPosition(mesh, 'snap_center_y');
      
      expect(pos.y).toBe(0);
    });

    it('should center on both axes', () => {
      mesh.position.set(5, 5, 0);
      const pos = engine.calculateSnapPosition(mesh, 'snap_center_xy');
      
      expect(pos.x).toBe(0);
      expect(pos.y).toBe(0);
    });

    it('should preserve Z position', () => {
      mesh.position.set(0, 0, 5);
      const pos = engine.calculateSnapPosition(mesh, 'snap_center_xy');
      
      expect(pos.z).toBe(5);
    });
  });

  describe('Grid Snapping', () => {
    it('should snap to grid', () => {
      engine.updateConfig({ gridSize: 10 });
      
      const pos = new THREE.Vector3(13, 27, 41);
      const snapped = engine.snapToGrid(pos);
      
      expect(snapped.x).toBe(10);
      expect(snapped.y).toBe(30);
      expect(snapped.z).toBe(40);
    });

    it('should detect if position is on grid', () => {
      engine.updateConfig({ gridSize: 10 });
      
      expect(engine.isOnGrid(new THREE.Vector3(10, 20, 30))).toBe(true);
      expect(engine.isOnGrid(new THREE.Vector3(13, 27, 41))).toBe(false);
    });
  });

  describe('Magnetic Force', () => {
    it('should apply magnetic force toward targets', () => {
      engine.updateConfig({ magneticStrength: 100, magneticRadius: 50 });
      
      const position = new THREE.Vector3(0, 0, 0);
      const targets = [
        { position: new THREE.Vector3(10, 0, 0), object: new THREE.Object3D(), type: 'element' as const, priority: 1, distance: 10 }
      ];
      
      const result = engine.applyMagneticForce(position, targets);
      
      // Should move toward target (positive X)
      expect(result.x).toBeGreaterThan(0);
    });

    it('should not affect positions outside radius', () => {
      engine.updateConfig({ magneticStrength: 100, magneticRadius: 5 });
      
      const position = new THREE.Vector3(0, 0, 0);
      const targets = [
        { position: new THREE.Vector3(100, 0, 0), object: new THREE.Object3D(), type: 'element' as const, priority: 1, distance: 100 }
      ];
      
      const result = engine.applyMagneticForce(position, targets);
      
      // Should not move
      expect(result.x).toBe(0);
    });
  });

  describe('Utility Methods', () => {
    it('should get all snap options', () => {
      const options = engine.getSnapOptions();
      
      expect(options).toHaveLength(7);
      expect(options.map(o => o.option)).toContain('snap_top');
      expect(options.map(o => o.option)).toContain('snap_center_xy');
    });

    it('should calculate distance', () => {
      const from = new THREE.Vector3(0, 0, 0);
      const to = new THREE.Vector3(3, 4, 0);
      
      const distance = engine.getDistance(from, to);
      
      expect(distance).toBe(5); // 3-4-5 triangle
    });

    it('should get component distances', () => {
      const from = new THREE.Vector3(0, 0, 0);
      const to = new THREE.Vector3(3, 4, 5);
      
      const components = engine.getComponentDistances(from, to);
      
      expect(components.deltaX).toBe(3);
      expect(components.deltaY).toBe(4);
      expect(components.deltaZ).toBe(5);
    });
  });

  describe('calculateSnapToObject', () => {
    it('should snap source to target edge', () => {
      const source = new THREE.Mesh(new THREE.BoxGeometry(2, 2, 2));
      source.position.set(0, 0, 0);
      
      const target = new THREE.Mesh(new THREE.BoxGeometry(4, 4, 4));
      target.position.set(10, 0, 0);
      
      const pos = engine.calculateSnapToObject(source, target, 'left');
      
      // Target left edge is at 10 - 2 = 8
      // Source should be at 8 - 1 = 7 (minus half source width)
      expect(pos.x).toBe(7);
    });
  });
});

