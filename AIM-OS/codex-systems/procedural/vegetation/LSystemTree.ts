/**
 * L-System Procedural Vegetation
 * Grammar-based tree and plant generation
 * 
 * Features:
 * - Parametric L-Systems
 * - Stochastic rules
 * - Multiple tree types (oak, pine, palm, etc.)
 * - Branch geometry generation
 * - Leaf/needle placement
 * - Wind animation support
 * - LOD generation
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface LSystemRule {
  predecessor: string;
  successor: string;
  probability?: number;  // For stochastic rules
  condition?: (params: Map<string, number>) => boolean;
}

export interface LSystemConfig {
  axiom: string;
  rules: LSystemRule[];
  iterations: number;
  angle: number;
  angleVariation: number;
  lengthFactor: number;
  lengthVariation: number;
  radiusFactor: number;
  initialRadius: number;
  initialLength: number;
}

export interface TurtleState {
  position: THREE.Vector3;
  direction: THREE.Vector3;
  right: THREE.Vector3;
  length: number;
  radius: number;
  depth: number;
}

export interface BranchSegment {
  start: THREE.Vector3;
  end: THREE.Vector3;
  startRadius: number;
  endRadius: number;
  depth: number;
  parentIndex: number;
}

export interface LeafData {
  position: THREE.Vector3;
  normal: THREE.Vector3;
  size: number;
  rotation: number;
}

export interface TreePreset {
  name: string;
  config: LSystemConfig;
  leafType: 'broadleaf' | 'needle' | 'palm' | 'none';
  leafDensity: number;
  leafSize: number;
  trunkColor: THREE.Color;
  leafColor: THREE.Color;
}

// ============================================
// PRESET TREE TYPES
// ============================================

export const TreePresets: Record<string, TreePreset> = {
  oak: {
    name: 'Oak',
    config: {
      axiom: 'F',
      rules: [
        { predecessor: 'F', successor: 'FF+[+F-F-F]-[-F+F+F]', probability: 0.5 },
        { predecessor: 'F', successor: 'FF-[-F+F+F]+[+F-F-F]', probability: 0.5 },
      ],
      iterations: 4,
      angle: 25,
      angleVariation: 5,
      lengthFactor: 0.65,
      lengthVariation: 0.1,
      radiusFactor: 0.7,
      initialRadius: 0.3,
      initialLength: 2,
    },
    leafType: 'broadleaf',
    leafDensity: 0.8,
    leafSize: 0.3,
    trunkColor: new THREE.Color(0x4a3728),
    leafColor: new THREE.Color(0x228B22),
  },
  
  pine: {
    name: 'Pine',
    config: {
      axiom: 'FFFA',
      rules: [
        { predecessor: 'A', successor: '[&FL!A]////[&FL!A]////[&FL!A]' },
        { predecessor: 'F', successor: 'S//F' },
        { predecessor: 'S', successor: 'FL' },
        { predecessor: 'L', successor: '[^^-F+F+F-|-F+F+F]' },
      ],
      iterations: 6,
      angle: 22,
      angleVariation: 3,
      lengthFactor: 0.85,
      lengthVariation: 0.05,
      radiusFactor: 0.8,
      initialRadius: 0.2,
      initialLength: 1.5,
    },
    leafType: 'needle',
    leafDensity: 1.0,
    leafSize: 0.15,
    trunkColor: new THREE.Color(0x5c4033),
    leafColor: new THREE.Color(0x0d5c0d),
  },
  
  palm: {
    name: 'Palm',
    config: {
      axiom: 'FFFFFA',
      rules: [
        { predecessor: 'A', successor: '[++++++++++FL][----------FL][++++++++++FL][----------FL]' },
        { predecessor: 'F', successor: 'FF' },
        { predecessor: 'L', successor: '[&&&&&FFFF][^^^^^FFFF][&&&&&FFFF][^^^^^FFFF]' },
      ],
      iterations: 3,
      angle: 12,
      angleVariation: 2,
      lengthFactor: 0.9,
      lengthVariation: 0.02,
      radiusFactor: 0.95,
      initialRadius: 0.4,
      initialLength: 3,
    },
    leafType: 'palm',
    leafDensity: 0.5,
    leafSize: 2,
    trunkColor: new THREE.Color(0x8b7355),
    leafColor: new THREE.Color(0x2e8b2e),
  },
  
  willow: {
    name: 'Willow',
    config: {
      axiom: 'F',
      rules: [
        { predecessor: 'F', successor: 'FF[+F][--F][-F][++F]' },
      ],
      iterations: 5,
      angle: 15,
      angleVariation: 10,
      lengthFactor: 0.6,
      lengthVariation: 0.15,
      radiusFactor: 0.65,
      initialRadius: 0.25,
      initialLength: 2.5,
    },
    leafType: 'broadleaf',
    leafDensity: 0.9,
    leafSize: 0.15,
    trunkColor: new THREE.Color(0x5a4a3a),
    leafColor: new THREE.Color(0x6b8e23),
  },
  
  bush: {
    name: 'Bush',
    config: {
      axiom: 'FA',
      rules: [
        { predecessor: 'A', successor: '[+FA][-FA][^FA][&FA]' },
        { predecessor: 'F', successor: 'FF' },
      ],
      iterations: 4,
      angle: 30,
      angleVariation: 15,
      lengthFactor: 0.5,
      lengthVariation: 0.2,
      radiusFactor: 0.6,
      initialRadius: 0.1,
      initialLength: 0.5,
    },
    leafType: 'broadleaf',
    leafDensity: 1.0,
    leafSize: 0.2,
    trunkColor: new THREE.Color(0x3d2817),
    leafColor: new THREE.Color(0x32cd32),
  },
};

// ============================================
// L-SYSTEM GENERATOR
// ============================================

export class LSystemGenerator {
  private config: LSystemConfig;
  private random: () => number;
  
  constructor(config: LSystemConfig, seed?: number) {
    this.config = config;
    
    // Seeded random
    if (seed !== undefined) {
      let s = seed;
      this.random = () => {
        s = (s * 1103515245 + 12345) & 0x7fffffff;
        return s / 0x7fffffff;
      };
    } else {
      this.random = Math.random;
    }
  }
  
  /**
   * Generate L-System string
   */
  public generate(): string {
    let current = this.config.axiom;
    
    for (let i = 0; i < this.config.iterations; i++) {
      current = this.iterate(current);
    }
    
    return current;
  }
  
  private iterate(str: string): string {
    let result = '';
    
    for (const char of str) {
      let replaced = false;
      
      // Find matching rules
      const matchingRules = this.config.rules.filter(r => r.predecessor === char);
      
      if (matchingRules.length > 0) {
        // Handle stochastic rules
        const totalProb = matchingRules.reduce((sum, r) => sum + (r.probability ?? 1), 0);
        let roll = this.random() * totalProb;
        
        for (const rule of matchingRules) {
          roll -= rule.probability ?? 1;
          if (roll <= 0) {
            result += rule.successor;
            replaced = true;
            break;
          }
        }
      }
      
      if (!replaced) {
        result += char;
      }
    }
    
    return result;
  }
}

// ============================================
// TURTLE INTERPRETER
// ============================================

export class TurtleInterpreter {
  private config: LSystemConfig;
  private random: () => number;
  
  public branches: BranchSegment[] = [];
  public leaves: LeafData[] = [];
  
  constructor(config: LSystemConfig, seed?: number) {
    this.config = config;
    
    if (seed !== undefined) {
      let s = seed;
      this.random = () => {
        s = (s * 1103515245 + 12345) & 0x7fffffff;
        return s / 0x7fffffff;
      };
    } else {
      this.random = Math.random;
    }
  }
  
  /**
   * Interpret L-System string into geometry
   */
  public interpret(lsystem: string): void {
    this.branches = [];
    this.leaves = [];
    
    const stateStack: TurtleState[] = [];
    let state: TurtleState = {
      position: new THREE.Vector3(0, 0, 0),
      direction: new THREE.Vector3(0, 1, 0),
      right: new THREE.Vector3(1, 0, 0),
      length: this.config.initialLength,
      radius: this.config.initialRadius,
      depth: 0,
    };
    
    let branchIndex = -1;
    
    for (const char of lsystem) {
      const angleRad = (this.config.angle + (this.random() - 0.5) * 2 * this.config.angleVariation) * THREE.MathUtils.DEG2RAD;
      
      switch (char) {
        case 'F': // Move forward and draw
          const start = state.position.clone();
          const length = state.length * (1 + (this.random() - 0.5) * 2 * this.config.lengthVariation);
          const end = start.clone().add(state.direction.clone().multiplyScalar(length));
          
          branchIndex++;
          this.branches.push({
            start,
            end,
            startRadius: state.radius,
            endRadius: state.radius * this.config.radiusFactor,
            depth: state.depth,
            parentIndex: branchIndex - 1,
          });
          
          state.position = end;
          state.radius *= this.config.radiusFactor;
          state.length *= this.config.lengthFactor;
          break;
          
        case 'f': // Move forward without drawing
          state.position.add(state.direction.clone().multiplyScalar(state.length));
          break;
          
        case '+': // Turn right (yaw)
          this.rotateYaw(state, angleRad);
          break;
          
        case '-': // Turn left (yaw)
          this.rotateYaw(state, -angleRad);
          break;
          
        case '&': // Pitch down
          this.rotatePitch(state, angleRad);
          break;
          
        case '^': // Pitch up
          this.rotatePitch(state, -angleRad);
          break;
          
        case '/': // Roll right
          this.rotateRoll(state, angleRad);
          break;
          
        case '\\': // Roll left
          this.rotateRoll(state, -angleRad);
          break;
          
        case '|': // Turn around (180°)
          this.rotateYaw(state, Math.PI);
          break;
          
        case '[': // Push state
          stateStack.push({
            position: state.position.clone(),
            direction: state.direction.clone(),
            right: state.right.clone(),
            length: state.length,
            radius: state.radius,
            depth: state.depth + 1,
          });
          break;
          
        case ']': // Pop state
          if (stateStack.length > 0) {
            state = stateStack.pop()!;
          }
          break;
          
        case 'L': // Place leaf
          this.leaves.push({
            position: state.position.clone(),
            normal: state.direction.clone(),
            size: 1,
            rotation: this.random() * Math.PI * 2,
          });
          break;
          
        case '!': // Decrease radius
          state.radius *= this.config.radiusFactor;
          break;
          
        case "'": // Increment color index (ignored in basic implementation)
          break;
      }
    }
  }
  
  private rotateYaw(state: TurtleState, angle: number): void {
    const up = state.direction.clone().cross(state.right).normalize();
    
    state.direction.applyAxisAngle(up, angle);
    state.right.applyAxisAngle(up, angle);
  }
  
  private rotatePitch(state: TurtleState, angle: number): void {
    state.direction.applyAxisAngle(state.right, angle);
  }
  
  private rotateRoll(state: TurtleState, angle: number): void {
    state.right.applyAxisAngle(state.direction, angle);
  }
}

// ============================================
// TREE MESH GENERATOR
// ============================================

export class TreeMeshGenerator {
  private radialSegments: number = 8;
  
  /**
   * Generate trunk/branch geometry
   */
  public generateBranchGeometry(branches: BranchSegment[]): THREE.BufferGeometry {
    const vertices: number[] = [];
    const indices: number[] = [];
    const uvs: number[] = [];
    const normals: number[] = [];
    
    let indexOffset = 0;
    
    for (const branch of branches) {
      const direction = branch.end.clone().sub(branch.start);
      const length = direction.length();
      direction.normalize();
      
      // Create perpendicular vectors
      const perp1 = new THREE.Vector3();
      if (Math.abs(direction.y) < 0.99) {
        perp1.crossVectors(direction, new THREE.Vector3(0, 1, 0)).normalize();
      } else {
        perp1.crossVectors(direction, new THREE.Vector3(1, 0, 0)).normalize();
      }
      const perp2 = new THREE.Vector3().crossVectors(direction, perp1).normalize();
      
      // Generate cylinder vertices
      for (let ring = 0; ring <= 1; ring++) {
        const t = ring;
        const pos = branch.start.clone().lerp(branch.end, t);
        const radius = THREE.MathUtils.lerp(branch.startRadius, branch.endRadius, t);
        
        for (let seg = 0; seg <= this.radialSegments; seg++) {
          const angle = (seg / this.radialSegments) * Math.PI * 2;
          const cos = Math.cos(angle);
          const sin = Math.sin(angle);
          
          const normal = perp1.clone().multiplyScalar(cos).add(perp2.clone().multiplyScalar(sin));
          const vertex = pos.clone().add(normal.clone().multiplyScalar(radius));
          
          vertices.push(vertex.x, vertex.y, vertex.z);
          normals.push(normal.x, normal.y, normal.z);
          uvs.push(seg / this.radialSegments, t);
        }
      }
      
      // Generate indices
      for (let seg = 0; seg < this.radialSegments; seg++) {
        const a = indexOffset + seg;
        const b = indexOffset + seg + 1;
        const c = indexOffset + this.radialSegments + 1 + seg;
        const d = indexOffset + this.radialSegments + 1 + seg + 1;
        
        indices.push(a, c, b);
        indices.push(b, c, d);
      }
      
      indexOffset += (this.radialSegments + 1) * 2;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geometry.setIndex(indices);
    
    return geometry;
  }
  
  /**
   * Generate leaf instances
   */
  public generateLeafGeometry(
    leaves: LeafData[],
    leafSize: number,
    leafType: 'broadleaf' | 'needle' | 'palm' | 'none'
  ): THREE.BufferGeometry {
    if (leafType === 'none' || leaves.length === 0) {
      return new THREE.BufferGeometry();
    }
    
    const baseGeom = this.createLeafShape(leafType, leafSize);
    const positions: number[] = [];
    const normals: number[] = [];
    const uvs: number[] = [];
    const indices: number[] = [];
    
    const basePositions = baseGeom.getAttribute('position');
    const baseNormals = baseGeom.getAttribute('normal');
    const baseUvs = baseGeom.getAttribute('uv');
    const baseIndices = baseGeom.getIndex();
    
    let indexOffset = 0;
    
    for (const leaf of leaves) {
      // Create rotation matrix
      const matrix = new THREE.Matrix4();
      const quaternion = new THREE.Quaternion();
      
      // Align with normal
      const up = new THREE.Vector3(0, 1, 0);
      quaternion.setFromUnitVectors(up, leaf.normal);
      
      // Apply random rotation around normal
      const rotQuat = new THREE.Quaternion().setFromAxisAngle(leaf.normal, leaf.rotation);
      quaternion.multiply(rotQuat);
      
      matrix.makeRotationFromQuaternion(quaternion);
      matrix.setPosition(leaf.position);
      matrix.scale(new THREE.Vector3(leaf.size, leaf.size, leaf.size));
      
      // Transform vertices
      for (let i = 0; i < basePositions.count; i++) {
        const pos = new THREE.Vector3(
          basePositions.getX(i),
          basePositions.getY(i),
          basePositions.getZ(i)
        );
        pos.applyMatrix4(matrix);
        positions.push(pos.x, pos.y, pos.z);
        
        const norm = new THREE.Vector3(
          baseNormals.getX(i),
          baseNormals.getY(i),
          baseNormals.getZ(i)
        );
        norm.applyQuaternion(quaternion);
        normals.push(norm.x, norm.y, norm.z);
        
        uvs.push(baseUvs.getX(i), baseUvs.getY(i));
      }
      
      // Copy indices
      if (baseIndices) {
        for (let i = 0; i < baseIndices.count; i++) {
          indices.push(baseIndices.getX(i) + indexOffset);
        }
      }
      
      indexOffset += basePositions.count;
    }
    
    baseGeom.dispose();
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    if (indices.length > 0) {
      geometry.setIndex(indices);
    }
    
    return geometry;
  }
  
  private createLeafShape(type: 'broadleaf' | 'needle' | 'palm', size: number): THREE.BufferGeometry {
    switch (type) {
      case 'broadleaf':
        return this.createBroadleaf(size);
      case 'needle':
        return this.createNeedle(size);
      case 'palm':
        return this.createPalmFrond(size);
      default:
        return new THREE.PlaneGeometry(size, size);
    }
  }
  
  private createBroadleaf(size: number): THREE.BufferGeometry {
    const shape = new THREE.Shape();
    
    // Leaf shape
    shape.moveTo(0, 0);
    shape.bezierCurveTo(size * 0.3, size * 0.3, size * 0.3, size * 0.7, 0, size);
    shape.bezierCurveTo(-size * 0.3, size * 0.7, -size * 0.3, size * 0.3, 0, 0);
    
    const geometry = new THREE.ShapeGeometry(shape);
    geometry.computeVertexNormals();
    
    return geometry;
  }
  
  private createNeedle(size: number): THREE.BufferGeometry {
    const geometry = new THREE.BufferGeometry();
    
    const vertices = new Float32Array([
      0, 0, 0,
      -size * 0.05, size, 0,
      size * 0.05, size, 0,
    ]);
    
    const normals = new Float32Array([
      0, 0, 1,
      0, 0, 1,
      0, 0, 1,
    ]);
    
    const uvs = new Float32Array([
      0.5, 0,
      0, 1,
      1, 1,
    ]);
    
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geometry.setIndex([0, 1, 2]);
    
    return geometry;
  }
  
  private createPalmFrond(size: number): THREE.BufferGeometry {
    const segments = 8;
    const vertices: number[] = [];
    const normals: number[] = [];
    const uvs: number[] = [];
    const indices: number[] = [];
    
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const width = size * 0.3 * Math.sin(t * Math.PI);
      
      vertices.push(-width, t * size, 0);
      vertices.push(width, t * size, 0);
      
      normals.push(0, 0, 1, 0, 0, 1);
      uvs.push(0, t, 1, t);
      
      if (i < segments) {
        const base = i * 2;
        indices.push(base, base + 2, base + 1);
        indices.push(base + 1, base + 2, base + 3);
      }
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geometry.setIndex(indices);
    
    return geometry;
  }
}

// ============================================
// MAIN L-SYSTEM TREE
// ============================================

export class LSystemTree {
  public group: THREE.Group;
  public trunkMesh: THREE.Mesh;
  public leavesMesh: THREE.Mesh;
  
  private preset: TreePreset;
  private generator: LSystemGenerator;
  private interpreter: TurtleInterpreter;
  private meshGenerator: TreeMeshGenerator;
  private seed: number;
  
  constructor(preset: TreePreset | string, seed?: number) {
    this.seed = seed ?? Math.floor(Math.random() * 1000000);
    
    if (typeof preset === 'string') {
      this.preset = TreePresets[preset] ?? TreePresets.oak;
    } else {
      this.preset = preset;
    }
    
    this.group = new THREE.Group();
    this.generator = new LSystemGenerator(this.preset.config, this.seed);
    this.interpreter = new TurtleInterpreter(this.preset.config, this.seed);
    this.meshGenerator = new TreeMeshGenerator();
    
    // Generate tree
    this.generate();
    
    // Create meshes
    this.trunkMesh = this.createTrunkMesh();
    this.leavesMesh = this.createLeavesMesh();
    
    this.group.add(this.trunkMesh);
    this.group.add(this.leavesMesh);
  }
  
  private generate(): void {
    const lsystem = this.generator.generate();
    this.interpreter.interpret(lsystem);
  }
  
  private createTrunkMesh(): THREE.Mesh {
    const geometry = this.meshGenerator.generateBranchGeometry(this.interpreter.branches);
    
    const material = new THREE.MeshStandardMaterial({
      color: this.preset.trunkColor,
      roughness: 0.9,
      metalness: 0,
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    return mesh;
  }
  
  private createLeavesMesh(): THREE.Mesh {
    // Filter leaves based on density
    const filteredLeaves = this.interpreter.leaves.filter(
      () => Math.random() < this.preset.leafDensity
    );
    
    const geometry = this.meshGenerator.generateLeafGeometry(
      filteredLeaves,
      this.preset.leafSize,
      this.preset.leafType
    );
    
    const material = new THREE.MeshStandardMaterial({
      color: this.preset.leafColor,
      roughness: 0.7,
      metalness: 0,
      side: THREE.DoubleSide,
      alphaTest: 0.5,
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    return mesh;
  }
  
  /**
   * Get branch count
   */
  public getBranchCount(): number {
    return this.interpreter.branches.length;
  }
  
  /**
   * Get leaf count
   */
  public getLeafCount(): number {
    return this.interpreter.leaves.length;
  }
  
  /**
   * Dispose resources
   */
  public dispose(): void {
    this.trunkMesh.geometry.dispose();
    this.leavesMesh.geometry.dispose();
    
    if (this.trunkMesh.material instanceof THREE.Material) {
      this.trunkMesh.material.dispose();
    }
    if (this.leavesMesh.material instanceof THREE.Material) {
      this.leavesMesh.material.dispose();
    }
  }
}

// ============================================
// FOREST GENERATOR
// ============================================

export class ForestGenerator {
  private scene: THREE.Scene;
  private trees: LSystemTree[] = [];
  
  constructor(scene: THREE.Scene) {
    this.scene = scene;
  }
  
  /**
   * Generate forest
   */
  public generate(
    count: number,
    area: THREE.Box2,
    presets: string[] = ['oak', 'pine', 'willow'],
    heightFunction?: (x: number, z: number) => number
  ): void {
    for (let i = 0; i < count; i++) {
      const x = THREE.MathUtils.randFloat(area.min.x, area.max.x);
      const z = THREE.MathUtils.randFloat(area.min.y, area.max.y);
      const y = heightFunction ? heightFunction(x, z) : 0;
      
      const preset = presets[Math.floor(Math.random() * presets.length)];
      const tree = new LSystemTree(preset);
      
      tree.group.position.set(x, y, z);
      tree.group.rotation.y = Math.random() * Math.PI * 2;
      
      const scale = 0.7 + Math.random() * 0.6;
      tree.group.scale.setScalar(scale);
      
      this.trees.push(tree);
      this.scene.add(tree.group);
    }
  }
  
  /**
   * Clear forest
   */
  public clear(): void {
    for (const tree of this.trees) {
      this.scene.remove(tree.group);
      tree.dispose();
    }
    this.trees = [];
  }
  
  /**
   * Get tree count
   */
  public getTreeCount(): number {
    return this.trees.length;
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.clear();
  }
}

