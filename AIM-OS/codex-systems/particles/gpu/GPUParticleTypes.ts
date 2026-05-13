/**
 * GPU Particle System Types
 * Transform feedback or compute shader based
 */

import * as THREE from 'three';

export interface GPUParticleConfig {
  maxParticles: number;       // Maximum particle count (65536 - 1M+)
  emissionRate: number;       // Particles per second
  lifetime: [number, number]; // Min/max lifetime in seconds
  
  // Initial conditions
  initialPosition: THREE.Vector3;
  positionSpread: THREE.Vector3;
  initialVelocity: THREE.Vector3;
  velocitySpread: THREE.Vector3;
  
  // Appearance
  startSize: [number, number];  // Min/max start size
  endSize: [number, number];    // Min/max end size
  startColor: THREE.Color;
  endColor: THREE.Color;
  startOpacity: number;
  endOpacity: number;
  
  // Physics
  gravity: THREE.Vector3;
  drag: number;               // Air resistance
  turbulence: number;         // Curl noise strength
  turbulenceFrequency: number;
  
  // Rendering
  blendMode: 'additive' | 'normal' | 'multiply';
  sortParticles: boolean;     // Sort by depth (expensive)
  softParticles: boolean;     // Depth-based fading
  softParticleScale: number;
  
  // Texture
  textureAtlas?: THREE.Texture;
  atlasFrames: number;        // Frames in atlas
  animateTexture: boolean;
  
  // Collision
  enableCollision: boolean;
  collisionBounce: number;
  collisionFriction: number;
}

export const DEFAULT_GPU_PARTICLE_CONFIG: GPUParticleConfig = {
  maxParticles: 100000,
  emissionRate: 1000,
  lifetime: [1.0, 3.0],
  
  initialPosition: new THREE.Vector3(0, 0, 0),
  positionSpread: new THREE.Vector3(0.5, 0.5, 0.5),
  initialVelocity: new THREE.Vector3(0, 2, 0),
  velocitySpread: new THREE.Vector3(1, 1, 1),
  
  startSize: [0.1, 0.2],
  endSize: [0.02, 0.05],
  startColor: new THREE.Color(1, 0.5, 0),
  endColor: new THREE.Color(1, 0, 0),
  startOpacity: 1.0,
  endOpacity: 0.0,
  
  gravity: new THREE.Vector3(0, -9.81, 0),
  drag: 0.1,
  turbulence: 0.5,
  turbulenceFrequency: 1.0,
  
  blendMode: 'additive',
  sortParticles: false,
  softParticles: true,
  softParticleScale: 1.0,
  
  atlasFrames: 1,
  animateTexture: false,
  
  enableCollision: false,
  collisionBounce: 0.5,
  collisionFriction: 0.2
};

export interface ParticleData {
  // Per-particle attributes (in GPU buffers)
  positions: Float32Array;      // xyz
  velocities: Float32Array;     // xyz
  lifetimes: Float32Array;      // current, max
  sizes: Float32Array;          // start, end
  colors: Float32Array;         // rgba start, rgba end
  seeds: Float32Array;          // random seed per particle
}

export interface EmitterShape {
  type: 'point' | 'sphere' | 'box' | 'cone' | 'ring';
  radius?: number;
  angle?: number;
  size?: THREE.Vector3;
  innerRadius?: number;
}

export interface ParticleForce {
  type: 'gravity' | 'wind' | 'vortex' | 'attract' | 'repel' | 'turbulence';
  strength: number;
  position?: THREE.Vector3;
  direction?: THREE.Vector3;
  radius?: number;
  falloff?: 'linear' | 'quadratic' | 'none';
}

export interface ParticleCollider {
  type: 'plane' | 'sphere' | 'box';
  position: THREE.Vector3;
  normal?: THREE.Vector3;   // For plane
  radius?: number;          // For sphere
  size?: THREE.Vector3;     // For box
  bounce: number;
  friction: number;
}

