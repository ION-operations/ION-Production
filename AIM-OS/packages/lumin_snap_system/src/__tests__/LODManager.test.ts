/**
 * LODManager Tests
 * @module @lumin/snap-system/tests/LODManager
 */

import * as THREE from 'three';
import { LODManager } from '../utils/LODManager';
import { LODLevel } from '../types';

describe('LODManager', () => {
  let manager: LODManager;

  beforeEach(() => {
    // Reset singleton before each test
    LODManager.resetInstance();
    manager = LODManager.getInstance();
  });

  afterEach(() => {
    manager.clearCache();
  });

  describe('Singleton Pattern', () => {
    it('should return same instance', () => {
      const instance1 = LODManager.getInstance();
      const instance2 = LODManager.getInstance();
      expect(instance1).toBe(instance2);
    });

    it('should create new instance after reset', () => {
      const instance1 = LODManager.getInstance();
      LODManager.resetInstance();
      const instance2 = LODManager.getInstance();
      expect(instance1).not.toBe(instance2);
    });
  });

  describe('countPolygons', () => {
    it('should count polygons in simple box', () => {
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry);
      
      const count = manager.countPolygons(mesh);
      
      // Box has 6 faces * 2 triangles = 12 polygons
      expect(count).toBe(12);
    });

    it('should count polygons in group with children', () => {
      const group = new THREE.Group();
      
      const box1 = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1));
      const box2 = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1));
      
      group.add(box1);
      group.add(box2);
      
      const count = manager.countPolygons(group);
      
      // 2 boxes * 12 polygons = 24
      expect(count).toBe(24);
    });

    it('should return 0 for empty object', () => {
      const empty = new THREE.Object3D();
      const count = manager.countPolygons(empty);
      expect(count).toBe(0);
    });
  });

  describe('selectLOD', () => {
    it('should return FULL_DETAIL for simple mesh', () => {
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry);
      
      const level = manager.selectLOD(mesh);
      
      expect(level).toBe(LODLevel.FULL_DETAIL);
    });

    it('should return SIMPLIFIED_MESH for medium mesh', () => {
      // Create mesh with ~5000 polygons
      const geometry = new THREE.IcosahedronGeometry(5, 4);
      const mesh = new THREE.Mesh(geometry);
      
      const polyCount = manager.countPolygons(mesh);
      const level = manager.selectLOD(mesh);
      
      expect(polyCount).toBeGreaterThan(1000);
      expect(polyCount).toBeLessThan(10000);
      expect(level).toBe(LODLevel.SIMPLIFIED_MESH);
    });

    it('should return WIREFRAME for large mesh', () => {
      // Create mesh with ~50000 polygons
      const geometry = new THREE.IcosahedronGeometry(5, 6);
      const mesh = new THREE.Mesh(geometry);
      
      const polyCount = manager.countPolygons(mesh);
      const level = manager.selectLOD(mesh);
      
      expect(polyCount).toBeGreaterThan(10000);
      expect(polyCount).toBeLessThan(100000);
      expect(level).toBe(LODLevel.WIREFRAME);
    });

    it('should return BOUNDING_BOX for huge mesh', () => {
      // Create mesh with >100000 polygons
      const geometry = new THREE.IcosahedronGeometry(5, 8);
      const mesh = new THREE.Mesh(geometry);
      
      const polyCount = manager.countPolygons(mesh);
      const level = manager.selectLOD(mesh);
      
      expect(polyCount).toBeGreaterThan(100000);
      expect(level).toBe(LODLevel.BOUNDING_BOX);
    });
  });

  describe('createLODObject', () => {
    it('should create full detail clone', () => {
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
      const mesh = new THREE.Mesh(geometry, material);
      
      const lod = manager.createLODObject(mesh, LODLevel.FULL_DETAIL);
      
      expect(lod).toBeDefined();
      expect(lod).not.toBe(mesh); // Should be a clone
    });

    it('should create bounding box for BOUNDING_BOX level', () => {
      const geometry = new THREE.BoxGeometry(2, 3, 4);
      const mesh = new THREE.Mesh(geometry);
      
      const lod = manager.createLODObject(mesh, LODLevel.BOUNDING_BOX);
      
      expect(lod).toBeDefined();
      expect(lod instanceof THREE.Mesh).toBe(true);
    });

    it('should cache LOD objects', () => {
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry);
      
      // First call - cache miss
      manager.createLODObject(mesh, LODLevel.FULL_DETAIL);
      
      // Second call - cache hit
      manager.createLODObject(mesh, LODLevel.FULL_DETAIL);
      
      const stats = manager.getStats();
      expect(stats.cacheHits).toBe(1);
      expect(stats.cacheMisses).toBe(1);
    });
  });

  describe('Performance Tracking', () => {
    it('should record render times', () => {
      manager.recordRenderTime('test-object-1', 5);
      manager.recordRenderTime('test-object-1', 6);
      manager.recordRenderTime('test-object-1', 7);
      
      const stats = manager.getStats();
      expect(stats.averageRenderTimeMs).toBeCloseTo(6, 1);
    });

    it('should track render count', () => {
      manager.recordRenderTime('obj1', 5);
      manager.recordRenderTime('obj2', 5);
      manager.recordRenderTime('obj3', 5);
      
      const stats = manager.getStats();
      expect(stats.averageRenderTimeMs).toBe(5);
    });
  });

  describe('Cache Management', () => {
    it('should clear cache', () => {
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1));
      
      manager.createLODObject(mesh, LODLevel.FULL_DETAIL);
      manager.createLODObject(mesh, LODLevel.BOUNDING_BOX);
      
      let stats = manager.getStats();
      expect(stats.cacheEntries).toBe(2);
      
      manager.clearCache();
      
      stats = manager.getStats();
      expect(stats.cacheEntries).toBe(0);
    });

    it('should estimate memory usage', () => {
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1));
      
      manager.createLODObject(mesh, LODLevel.FULL_DETAIL);
      
      const stats = manager.getStats();
      expect(stats.memoryUsageMB).toBeGreaterThan(0);
    });
  });
});

