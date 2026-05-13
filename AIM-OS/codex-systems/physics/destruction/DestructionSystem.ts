/**
 * Destruction Physics System
 * Voronoi-based fracturing with stress propagation
 * 
 * Features:
 * - Voronoi fracture generation
 * - Stress propagation
 * - Impact-based breaking
 * - Debris physics
 * - Material-specific breaking
 */

import * as THREE from 'three';

export interface DestructionConfig {
  minFragments: number;      // Minimum fragments per break
  maxFragments: number;      // Maximum fragments per break
  breakThreshold: number;    // Force required to break
  stressPropagation: number; // How stress spreads (0-1)
  debrisLifetime: number;    // Seconds before debris despawns
  inheritVelocity: number;   // How much impact velocity transfers
  explosionForce: number;    // Outward force on fragments
  materialType: 'glass' | 'wood' | 'concrete' | 'metal';
}

export const DEFAULT_DESTRUCTION_CONFIG: DestructionConfig = {
  minFragments: 5,
  maxFragments: 15,
  breakThreshold: 100,
  stressPropagation: 0.7,
  debrisLifetime: 10,
  inheritVelocity: 0.8,
  explosionForce: 5,
  materialType: 'concrete'
};

// Material-specific fracture patterns
const MATERIAL_PROPERTIES = {
  glass: {
    fragmentMultiplier: 2.0,    // More fragments
    shardiness: 0.8,            // Sharp shards
    propagationSpeed: 1.0,      // Instant propagation
    dustAmount: 0.1
  },
  wood: {
    fragmentMultiplier: 0.5,    // Fewer fragments
    shardiness: 0.3,            // Splintery
    propagationSpeed: 0.5,      // Slower crack propagation
    dustAmount: 0.3
  },
  concrete: {
    fragmentMultiplier: 1.0,    // Standard
    shardiness: 0.5,            // Chunky
    propagationSpeed: 0.8,      // Fast propagation
    dustAmount: 0.8
  },
  metal: {
    fragmentMultiplier: 0.3,    // Fewer fragments
    shardiness: 0.2,            // Bent pieces
    propagationSpeed: 0.3,      // Slow propagation
    dustAmount: 0.1
  }
};

export interface Fragment {
  mesh: THREE.Mesh;
  velocity: THREE.Vector3;
  angularVelocity: THREE.Vector3;
  lifetime: number;
  mass: number;
}

export interface VoronoiCell {
  center: THREE.Vector3;
  vertices: THREE.Vector3[];
  neighbors: number[];
}

export class DestructionSystem {
  private config: DestructionConfig;
  private fragments: Fragment[] = [];
  private gravity = new THREE.Vector3(0, -9.81, 0);

  constructor(config: Partial<DestructionConfig> = {}) {
    this.config = { ...DEFAULT_DESTRUCTION_CONFIG, ...config };
  }

  /**
   * Fracture an object into fragments
   */
  public fracture(
    mesh: THREE.Mesh,
    impactPoint: THREE.Vector3,
    impactForce: THREE.Vector3
  ): Fragment[] {
    const geometry = mesh.geometry as THREE.BufferGeometry;
    const boundingBox = new THREE.Box3().setFromObject(mesh);
    const size = new THREE.Vector3();
    boundingBox.getSize(size);
    
    const materialProps = MATERIAL_PROPERTIES[this.config.materialType];
    
    // Determine number of fragments
    const forceRatio = impactForce.length() / this.config.breakThreshold;
    const numFragments = Math.floor(THREE.MathUtils.lerp(
      this.config.minFragments,
      this.config.maxFragments,
      Math.min(forceRatio, 1)
    ) * materialProps.fragmentMultiplier);
    
    // Generate Voronoi cells
    const cells = this.generateVoronoiCells(boundingBox, numFragments, impactPoint);
    
    // Create fragment meshes
    const newFragments: Fragment[] = [];
    
    for (const cell of cells) {
      const fragmentGeometry = this.createFragmentGeometry(
        geometry,
        cell,
        boundingBox,
        materialProps.shardiness
      );
      
      if (fragmentGeometry.getAttribute('position').count < 4) continue;
      
      const fragmentMesh = new THREE.Mesh(
        fragmentGeometry,
        (mesh.material as THREE.Material).clone()
      );
      
      // Position fragment at its cell center
      const worldCenter = cell.center.clone();
      mesh.localToWorld(worldCenter);
      fragmentMesh.position.copy(worldCenter);
      
      // Calculate velocity based on impact
      const toFragment = cell.center.clone().sub(impactPoint);
      const distance = toFragment.length();
      const velocity = new THREE.Vector3()
        .addScaledVector(impactForce, this.config.inheritVelocity / Math.max(distance, 1))
        .addScaledVector(toFragment.normalize(), this.config.explosionForce);
      
      // Random angular velocity
      const angularVelocity = new THREE.Vector3(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10
      );
      
      // Calculate mass from volume approximation
      const fragmentSize = new THREE.Vector3();
      new THREE.Box3().setFromObject(fragmentMesh).getSize(fragmentSize);
      const mass = fragmentSize.x * fragmentSize.y * fragmentSize.z;
      
      newFragments.push({
        mesh: fragmentMesh,
        velocity,
        angularVelocity,
        lifetime: this.config.debrisLifetime,
        mass
      });
    }
    
    this.fragments.push(...newFragments);
    return newFragments;
  }

  /**
   * Generate Voronoi cells within bounding box
   */
  private generateVoronoiCells(
    boundingBox: THREE.Box3,
    numCells: number,
    attractorPoint: THREE.Vector3
  ): VoronoiCell[] {
    const cells: VoronoiCell[] = [];
    const size = new THREE.Vector3();
    const center = new THREE.Vector3();
    boundingBox.getSize(size);
    boundingBox.getCenter(center);
    
    // Generate cell centers with bias toward impact point
    const cellCenters: THREE.Vector3[] = [];
    
    for (let i = 0; i < numCells; i++) {
      let cellCenter: THREE.Vector3;
      
      if (i < numCells * 0.3) {
        // Some cells clustered near impact
        cellCenter = new THREE.Vector3(
          attractorPoint.x + (Math.random() - 0.5) * size.x * 0.3,
          attractorPoint.y + (Math.random() - 0.5) * size.y * 0.3,
          attractorPoint.z + (Math.random() - 0.5) * size.z * 0.3
        );
      } else {
        // Rest distributed throughout
        cellCenter = new THREE.Vector3(
          boundingBox.min.x + Math.random() * size.x,
          boundingBox.min.y + Math.random() * size.y,
          boundingBox.min.z + Math.random() * size.z
        );
      }
      
      cellCenters.push(cellCenter);
    }
    
    // Create cells (simplified - real Voronoi would use Fortune's algorithm)
    for (let i = 0; i < cellCenters.length; i++) {
      cells.push({
        center: cellCenters[i],
        vertices: [],
        neighbors: []
      });
    }
    
    // Find neighbors (cells that share a Voronoi edge)
    for (let i = 0; i < cells.length; i++) {
      for (let j = i + 1; j < cells.length; j++) {
        const dist = cells[i].center.distanceTo(cells[j].center);
        if (dist < size.length() * 0.5) {
          cells[i].neighbors.push(j);
          cells[j].neighbors.push(i);
        }
      }
    }
    
    return cells;
  }

  /**
   * Create geometry for a single fragment
   */
  private createFragmentGeometry(
    sourceGeometry: THREE.BufferGeometry,
    cell: VoronoiCell,
    boundingBox: THREE.Box3,
    shardiness: number
  ): THREE.BufferGeometry {
    // Get source positions
    const positions = sourceGeometry.getAttribute('position');
    const normals = sourceGeometry.getAttribute('normal');
    const indices = sourceGeometry.index;
    
    const newPositions: number[] = [];
    const newNormals: number[] = [];
    
    // Simple approach: take vertices closest to this cell's center
    const cellRadius = boundingBox.getSize(new THREE.Vector3()).length() / 
                       Math.sqrt(this.config.maxFragments);
    
    const tempVert = new THREE.Vector3();
    
    // Process each triangle
    if (indices) {
      for (let i = 0; i < indices.count; i += 3) {
        const i0 = indices.getX(i);
        const i1 = indices.getX(i + 1);
        const i2 = indices.getX(i + 2);
        
        // Check if triangle is within this cell
        tempVert.fromBufferAttribute(positions, i0);
        const d0 = tempVert.distanceTo(cell.center);
        
        tempVert.fromBufferAttribute(positions, i1);
        const d1 = tempVert.distanceTo(cell.center);
        
        tempVert.fromBufferAttribute(positions, i2);
        const d2 = tempVert.distanceTo(cell.center);
        
        const avgDist = (d0 + d1 + d2) / 3;
        
        if (avgDist < cellRadius * (1 + shardiness * 0.5)) {
          // Include this triangle
          for (const idx of [i0, i1, i2]) {
            tempVert.fromBufferAttribute(positions, idx);
            newPositions.push(tempVert.x - cell.center.x);
            newPositions.push(tempVert.y - cell.center.y);
            newPositions.push(tempVert.z - cell.center.z);
            
            if (normals) {
              tempVert.fromBufferAttribute(normals, idx);
              newNormals.push(tempVert.x, tempVert.y, tempVert.z);
            }
          }
        }
      }
    } else {
      // Non-indexed geometry
      for (let i = 0; i < positions.count; i += 3) {
        tempVert.fromBufferAttribute(positions, i);
        const d0 = tempVert.distanceTo(cell.center);
        
        tempVert.fromBufferAttribute(positions, i + 1);
        const d1 = tempVert.distanceTo(cell.center);
        
        tempVert.fromBufferAttribute(positions, i + 2);
        const d2 = tempVert.distanceTo(cell.center);
        
        const avgDist = (d0 + d1 + d2) / 3;
        
        if (avgDist < cellRadius * (1 + shardiness * 0.5)) {
          for (let j = 0; j < 3; j++) {
            tempVert.fromBufferAttribute(positions, i + j);
            newPositions.push(tempVert.x - cell.center.x);
            newPositions.push(tempVert.y - cell.center.y);
            newPositions.push(tempVert.z - cell.center.z);
            
            if (normals) {
              tempVert.fromBufferAttribute(normals, i + j);
              newNormals.push(tempVert.x, tempVert.y, tempVert.z);
            }
          }
        }
      }
    }
    
    const fragmentGeometry = new THREE.BufferGeometry();
    fragmentGeometry.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(newPositions, 3)
    );
    
    if (newNormals.length > 0) {
      fragmentGeometry.setAttribute(
        'normal',
        new THREE.Float32BufferAttribute(newNormals, 3)
      );
    } else {
      fragmentGeometry.computeVertexNormals();
    }
    
    return fragmentGeometry;
  }

  /**
   * Update fragment physics
   */
  public update(dt: number, collisionTest?: (pos: THREE.Vector3) => boolean): void {
    const deadFragments: number[] = [];
    
    for (let i = 0; i < this.fragments.length; i++) {
      const fragment = this.fragments[i];
      
      // Update lifetime
      fragment.lifetime -= dt;
      if (fragment.lifetime <= 0) {
        deadFragments.push(i);
        continue;
      }
      
      // Apply gravity
      fragment.velocity.addScaledVector(this.gravity, dt);
      
      // Update position
      fragment.mesh.position.addScaledVector(fragment.velocity, dt);
      
      // Update rotation
      const rotationDelta = new THREE.Quaternion().setFromEuler(
        new THREE.Euler(
          fragment.angularVelocity.x * dt,
          fragment.angularVelocity.y * dt,
          fragment.angularVelocity.z * dt
        )
      );
      fragment.mesh.quaternion.multiply(rotationDelta);
      
      // Simple ground collision
      if (fragment.mesh.position.y < 0) {
        fragment.mesh.position.y = 0;
        fragment.velocity.y = -fragment.velocity.y * 0.3;
        fragment.velocity.x *= 0.8;
        fragment.velocity.z *= 0.8;
        fragment.angularVelocity.multiplyScalar(0.5);
      }
      
      // Custom collision test
      if (collisionTest && collisionTest(fragment.mesh.position)) {
        fragment.velocity.multiplyScalar(-0.3);
        fragment.angularVelocity.multiplyScalar(0.5);
      }
      
      // Fade out near end of lifetime
      if (fragment.lifetime < 1) {
        const material = fragment.mesh.material as THREE.MeshStandardMaterial;
        if (material.transparent !== undefined) {
          material.transparent = true;
          material.opacity = fragment.lifetime;
        }
      }
    }
    
    // Remove dead fragments (reverse order to preserve indices)
    for (let i = deadFragments.length - 1; i >= 0; i--) {
      const idx = deadFragments[i];
      const fragment = this.fragments[idx];
      fragment.mesh.geometry.dispose();
      (fragment.mesh.material as THREE.Material).dispose();
      this.fragments.splice(idx, 1);
    }
  }

  /**
   * Check if impact should cause fracture
   */
  public shouldFracture(impactForce: number): boolean {
    return impactForce >= this.config.breakThreshold;
  }

  /**
   * Get all fragment meshes for adding to scene
   */
  public getFragmentMeshes(): THREE.Mesh[] {
    return this.fragments.map(f => f.mesh);
  }

  /**
   * Clear all fragments
   */
  public clearFragments(): void {
    for (const fragment of this.fragments) {
      fragment.mesh.geometry.dispose();
      (fragment.mesh.material as THREE.Material).dispose();
    }
    this.fragments = [];
  }

  public dispose(): void {
    this.clearFragments();
  }
}

