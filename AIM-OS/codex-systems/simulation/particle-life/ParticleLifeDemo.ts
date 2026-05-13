/**
 * Particle Life Demo (Three.js)
 * Renders ParticleLifeSystem as instanced spheres / points.
 */

import * as THREE from 'three';
import { ParticleLifeSystem, Species, InteractionMatrix } from './ParticleLifeSystem';

export interface ParticleLifeDemoOptions {
  speciesCount?: number;
  particleCount?: number;
  boundsSize?: number;
  pointSize?: number;
}

export class ParticleLifeDemo {
  private system: ParticleLifeSystem;
  private mesh: THREE.InstancedMesh;
  private colors: THREE.Color[] = [];
  private particleCount: number;
  private pointSize: number;

  constructor(scene: THREE.Scene, options: ParticleLifeDemoOptions = {}) {
    const speciesCount = options.speciesCount ?? 6;
    this.particleCount = options.particleCount ?? 4000;
    this.pointSize = options.pointSize ?? 0.08;
    const boundsSize = options.boundsSize ?? 20;

    // Species
    const species: Species[] = [];
    for (let i = 0; i < speciesCount; i++) {
      const color = new THREE.Color().setHSL(i / speciesCount, 0.7, 0.5);
      species.push({ id: i, color, mass: 1, radius: 0.1 });
      this.colors.push(color);
    }

    // Interaction matrix (random balanced attract/repel)
    const matrix: number[][] = [];
    for (let a = 0; a < speciesCount; a++) {
      matrix[a] = [];
      for (let b = 0; b < speciesCount; b++) {
        const v = THREE.MathUtils.lerp(-1, 1, Math.random());
        matrix[a][b] = v * 3; // stronger forces
      }
    }

    const interactions: InteractionMatrix = {
      matrix,
      falloff: 2,
      maxDistance: 2.5,
    };

    this.system = new ParticleLifeSystem(species, interactions, {
      bounds: new THREE.Box3(
        new THREE.Vector3(-boundsSize, -boundsSize, -boundsSize),
        new THREE.Vector3(boundsSize, boundsSize, boundsSize)
      ),
      wrap: true,
      timeStep: 0.016,
      damping: 0.995,
      maxNeighbors: 48,
    });

    this.system.spawn(this.particleCount);

    // Instanced spheres
    const geometry = new THREE.SphereGeometry(this.pointSize, 6, 6);
    const material = new THREE.MeshBasicMaterial({ vertexColors: true });
    this.mesh = new THREE.InstancedMesh(geometry, material, this.particleCount);
    scene.add(this.mesh);
  }

  public update(): void {
    this.system.update();
    const particles = this.system.getParticles();
    const dummy = new THREE.Object3D();

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      dummy.position.copy(p.position);
      dummy.updateMatrix();
      this.mesh.setMatrixAt(i, dummy.matrix);
      const c = this.colors[p.species];
      this.mesh.setColorAt(i, c);
    }

    this.mesh.instanceMatrix.needsUpdate = true;
    if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true;
  }
}

