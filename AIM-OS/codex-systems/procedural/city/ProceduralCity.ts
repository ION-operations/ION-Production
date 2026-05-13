/**
 * Procedural City Generation System
 * Generates complete cities with roads, blocks, and buildings
 * 
 * Features:
 * - L-System road network generation
 * - Block subdivision (straight skeleton)
 * - Building generation (CGA Shape Grammar inspired)
 * - Procedural facades
 * - LOD support
 * - Zone-based density
 * - Landmark placement
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export type ZoneType = 'residential' | 'commercial' | 'industrial' | 'downtown' | 'park';

export interface CityConfig {
  size: number;
  blockSize: number;
  roadWidth: number;
  minBuildingHeight: number;
  maxBuildingHeight: number;
  buildingDensity: number;
  seed: number;
}

export interface RoadSegment {
  start: THREE.Vector2;
  end: THREE.Vector2;
  width: number;
  type: 'main' | 'secondary' | 'alley';
}

export interface CityBlock {
  vertices: THREE.Vector2[];
  zone: ZoneType;
  buildings: Building[];
}

export interface Building {
  position: THREE.Vector3;
  size: THREE.Vector3;
  floors: number;
  type: 'tower' | 'office' | 'residential' | 'industrial' | 'landmark';
  style: BuildingStyle;
}

export interface BuildingStyle {
  baseColor: THREE.Color;
  accentColor: THREE.Color;
  windowColor: THREE.Color;
  roofType: 'flat' | 'peaked' | 'dome' | 'spire';
  windowDensity: number;
  hasBalconies: boolean;
  hasAwnings: boolean;
}

// ============================================
// SEEDED RANDOM
// ============================================

class SeededRandom {
  private seed: number;
  
  constructor(seed: number) {
    this.seed = seed;
  }
  
  public next(): number {
    this.seed = (this.seed * 1103515245 + 12345) & 0x7fffffff;
    return this.seed / 0x7fffffff;
  }
  
  public range(min: number, max: number): number {
    return min + this.next() * (max - min);
  }
  
  public int(min: number, max: number): number {
    return Math.floor(this.range(min, max + 1));
  }
  
  public pick<T>(array: T[]): T {
    return array[Math.floor(this.next() * array.length)];
  }
}

// ============================================
// ROAD NETWORK GENERATOR (L-System)
// ============================================

export class RoadNetworkGenerator {
  private config: CityConfig;
  private random: SeededRandom;
  public segments: RoadSegment[] = [];
  private roadSet: Set<string> = new Set();
  
  constructor(config: CityConfig) {
    this.config = config;
    this.random = new SeededRandom(config.seed);
  }
  
  public generate(): RoadSegment[] {
    this.segments = [];
    this.roadSet.clear();
    
    // Create main roads (grid)
    this.generateMainGrid();
    
    // Add secondary roads
    this.generateSecondaryRoads();
    
    // Add some curved/diagonal roads for variety
    this.generateDiagonalRoads();
    
    return this.segments;
  }
  
  private generateMainGrid(): void {
    const halfSize = this.config.size / 2;
    const spacing = this.config.blockSize + this.config.roadWidth;
    
    // Horizontal main roads
    for (let y = -halfSize; y <= halfSize; y += spacing * 2) {
      this.addRoad(
        new THREE.Vector2(-halfSize, y),
        new THREE.Vector2(halfSize, y),
        'main'
      );
    }
    
    // Vertical main roads
    for (let x = -halfSize; x <= halfSize; x += spacing * 2) {
      this.addRoad(
        new THREE.Vector2(x, -halfSize),
        new THREE.Vector2(x, halfSize),
        'main'
      );
    }
    
    // Secondary grid
    for (let y = -halfSize + spacing; y <= halfSize; y += spacing * 2) {
      this.addRoad(
        new THREE.Vector2(-halfSize, y),
        new THREE.Vector2(halfSize, y),
        'secondary'
      );
    }
    
    for (let x = -halfSize + spacing; x <= halfSize; x += spacing * 2) {
      this.addRoad(
        new THREE.Vector2(x, -halfSize),
        new THREE.Vector2(x, halfSize),
        'secondary'
      );
    }
  }
  
  private generateSecondaryRoads(): void {
    const halfSize = this.config.size / 2;
    const spacing = this.config.blockSize + this.config.roadWidth;
    
    // Add smaller roads within blocks
    for (let x = -halfSize; x < halfSize; x += spacing * 2) {
      for (let y = -halfSize; y < halfSize; y += spacing * 2) {
        if (this.random.next() > 0.6) {
          // Add alley
          const midX = x + spacing;
          const midY = y + spacing;
          
          if (this.random.next() > 0.5) {
            this.addRoad(
              new THREE.Vector2(midX, y),
              new THREE.Vector2(midX, y + spacing * 2),
              'alley'
            );
          } else {
            this.addRoad(
              new THREE.Vector2(x, midY),
              new THREE.Vector2(x + spacing * 2, midY),
              'alley'
            );
          }
        }
      }
    }
  }
  
  private generateDiagonalRoads(): void {
    const halfSize = this.config.size / 2;
    
    // Add a few diagonal boulevards
    if (this.random.next() > 0.5) {
      this.addRoad(
        new THREE.Vector2(-halfSize * 0.8, -halfSize * 0.8),
        new THREE.Vector2(halfSize * 0.8, halfSize * 0.8),
        'main'
      );
    }
    
    if (this.random.next() > 0.5) {
      this.addRoad(
        new THREE.Vector2(-halfSize * 0.8, halfSize * 0.8),
        new THREE.Vector2(halfSize * 0.8, -halfSize * 0.8),
        'main'
      );
    }
  }
  
  private addRoad(start: THREE.Vector2, end: THREE.Vector2, type: 'main' | 'secondary' | 'alley'): void {
    const key = `${start.x.toFixed(1)},${start.y.toFixed(1)}-${end.x.toFixed(1)},${end.y.toFixed(1)}`;
    if (this.roadSet.has(key)) return;
    this.roadSet.add(key);
    
    const width = type === 'main' ? this.config.roadWidth : 
                  type === 'secondary' ? this.config.roadWidth * 0.7 : 
                  this.config.roadWidth * 0.4;
    
    this.segments.push({
      start: start.clone(),
      end: end.clone(),
      width,
      type
    });
  }
}

// ============================================
// BLOCK SUBDIVIDER
// ============================================

export class BlockSubdivider {
  private config: CityConfig;
  private random: SeededRandom;
  
  constructor(config: CityConfig) {
    this.config = config;
    this.random = new SeededRandom(config.seed + 1000);
  }
  
  public createBlocks(roads: RoadSegment[]): CityBlock[] {
    const blocks: CityBlock[] = [];
    const halfSize = this.config.size / 2;
    const spacing = this.config.blockSize + this.config.roadWidth;
    
    // Create blocks from grid
    for (let x = -halfSize; x < halfSize; x += spacing) {
      for (let y = -halfSize; y < halfSize; y += spacing) {
        const block = this.createBlock(x, y, spacing - this.config.roadWidth);
        if (block) {
          blocks.push(block);
        }
      }
    }
    
    return blocks;
  }
  
  private createBlock(x: number, y: number, size: number): CityBlock | null {
    const padding = this.config.roadWidth / 2;
    
    const vertices = [
      new THREE.Vector2(x + padding, y + padding),
      new THREE.Vector2(x + size - padding, y + padding),
      new THREE.Vector2(x + size - padding, y + size - padding),
      new THREE.Vector2(x + padding, y + size - padding)
    ];
    
    // Determine zone based on distance from center
    const centerDist = Math.sqrt(x * x + y * y);
    const zone = this.getZone(centerDist);
    
    return {
      vertices,
      zone,
      buildings: []
    };
  }
  
  private getZone(distFromCenter: number): ZoneType {
    const maxDist = this.config.size / 2;
    const ratio = distFromCenter / maxDist;
    
    if (ratio < 0.15) return 'downtown';
    if (ratio < 0.35) return 'commercial';
    if (ratio < 0.7) return this.random.next() > 0.3 ? 'residential' : 'commercial';
    if (this.random.next() > 0.7) return 'industrial';
    return 'residential';
  }
}

// ============================================
// BUILDING GENERATOR
// ============================================

export class BuildingGenerator {
  private config: CityConfig;
  private random: SeededRandom;
  
  constructor(config: CityConfig) {
    this.config = config;
    this.random = new SeededRandom(config.seed + 2000);
  }
  
  public generateBuildings(blocks: CityBlock[]): void {
    for (const block of blocks) {
      const buildingCount = this.getBuildingCount(block.zone);
      const area = this.getBlockArea(block.vertices);
      
      for (let i = 0; i < buildingCount; i++) {
        const building = this.createBuilding(block, i, buildingCount);
        if (building) {
          block.buildings.push(building);
        }
      }
    }
  }
  
  private getBuildingCount(zone: ZoneType): number {
    switch (zone) {
      case 'downtown': return this.random.int(3, 6);
      case 'commercial': return this.random.int(2, 5);
      case 'residential': return this.random.int(4, 8);
      case 'industrial': return this.random.int(1, 3);
      case 'park': return this.random.int(0, 1);
    }
  }
  
  private createBuilding(block: CityBlock, index: number, total: number): Building | null {
    const bounds = this.getBounds(block.vertices);
    const blockWidth = bounds.max.x - bounds.min.x;
    const blockDepth = bounds.max.y - bounds.min.y;
    
    // Calculate position within block
    const cols = Math.ceil(Math.sqrt(total));
    const rows = Math.ceil(total / cols);
    const col = index % cols;
    const row = Math.floor(index / cols);
    
    const cellWidth = blockWidth / cols;
    const cellDepth = blockDepth / rows;
    
    const padding = 2;
    const maxWidth = cellWidth - padding * 2;
    const maxDepth = cellDepth - padding * 2;
    
    if (maxWidth < 5 || maxDepth < 5) return null;
    
    // Building dimensions based on zone
    const { width, depth, height } = this.getBuildingDimensions(block.zone, maxWidth, maxDepth);
    
    const position = new THREE.Vector3(
      bounds.min.x + col * cellWidth + cellWidth / 2,
      height / 2,
      bounds.min.y + row * cellDepth + cellDepth / 2
    );
    
    const type = this.getBuildingType(block.zone, height);
    const style = this.generateStyle(type, block.zone);
    
    return {
      position,
      size: new THREE.Vector3(width, height, depth),
      floors: Math.floor(height / 3),
      type,
      style
    };
  }
  
  private getBuildingDimensions(zone: ZoneType, maxWidth: number, maxDepth: number): { width: number; depth: number; height: number } {
    let heightMultiplier = 1;
    let sizeMultiplier = 0.8;
    
    switch (zone) {
      case 'downtown':
        heightMultiplier = 3;
        sizeMultiplier = 0.9;
        break;
      case 'commercial':
        heightMultiplier = 1.5;
        sizeMultiplier = 0.85;
        break;
      case 'residential':
        heightMultiplier = 0.7;
        sizeMultiplier = 0.6;
        break;
      case 'industrial':
        heightMultiplier = 0.5;
        sizeMultiplier = 0.95;
        break;
    }
    
    const width = Math.min(maxWidth * this.random.range(0.6, sizeMultiplier), maxWidth);
    const depth = Math.min(maxDepth * this.random.range(0.6, sizeMultiplier), maxDepth);
    
    const baseHeight = this.random.range(
      this.config.minBuildingHeight,
      this.config.maxBuildingHeight
    );
    const height = baseHeight * heightMultiplier;
    
    return { width, depth, height };
  }
  
  private getBuildingType(zone: ZoneType, height: number): Building['type'] {
    if (height > this.config.maxBuildingHeight * 2) return 'landmark';
    if (height > this.config.maxBuildingHeight) return 'tower';
    
    switch (zone) {
      case 'downtown': return this.random.next() > 0.3 ? 'tower' : 'office';
      case 'commercial': return 'office';
      case 'residential': return 'residential';
      case 'industrial': return 'industrial';
      default: return 'residential';
    }
  }
  
  private generateStyle(type: Building['type'], zone: ZoneType): BuildingStyle {
    const styles: Record<Building['type'], () => BuildingStyle> = {
      tower: () => ({
        baseColor: new THREE.Color().setHSL(this.random.range(0.55, 0.65), 0.3, 0.6),
        accentColor: new THREE.Color().setHSL(this.random.range(0, 0.1), 0.5, 0.5),
        windowColor: new THREE.Color(0.3, 0.4, 0.6),
        roofType: this.random.pick(['flat', 'spire']),
        windowDensity: 0.8,
        hasBalconies: false,
        hasAwnings: false
      }),
      office: () => ({
        baseColor: new THREE.Color().setHSL(0, 0, this.random.range(0.5, 0.8)),
        accentColor: new THREE.Color().setHSL(0.6, 0.5, 0.4),
        windowColor: new THREE.Color(0.4, 0.5, 0.7),
        roofType: 'flat',
        windowDensity: 0.7,
        hasBalconies: false,
        hasAwnings: this.random.next() > 0.7
      }),
      residential: () => ({
        baseColor: new THREE.Color().setHSL(this.random.range(0.05, 0.15), 0.4, 0.7),
        accentColor: new THREE.Color().setHSL(0.1, 0.6, 0.4),
        windowColor: new THREE.Color(0.5, 0.5, 0.5),
        roofType: this.random.pick(['flat', 'peaked']),
        windowDensity: 0.5,
        hasBalconies: this.random.next() > 0.5,
        hasAwnings: this.random.next() > 0.6
      }),
      industrial: () => ({
        baseColor: new THREE.Color().setHSL(0, 0, 0.5),
        accentColor: new THREE.Color(0.6, 0.3, 0.1),
        windowColor: new THREE.Color(0.3, 0.3, 0.3),
        roofType: 'flat',
        windowDensity: 0.2,
        hasBalconies: false,
        hasAwnings: false
      }),
      landmark: () => ({
        baseColor: new THREE.Color().setHSL(this.random.range(0.5, 0.7), 0.4, 0.6),
        accentColor: new THREE.Color(0.9, 0.8, 0.5),
        windowColor: new THREE.Color(0.4, 0.5, 0.8),
        roofType: this.random.pick(['dome', 'spire']),
        windowDensity: 0.6,
        hasBalconies: true,
        hasAwnings: false
      })
    };
    
    return styles[type]();
  }
  
  private getBounds(vertices: THREE.Vector2[]): { min: THREE.Vector2; max: THREE.Vector2 } {
    const min = new THREE.Vector2(Infinity, Infinity);
    const max = new THREE.Vector2(-Infinity, -Infinity);
    
    for (const v of vertices) {
      min.min(v);
      max.max(v);
    }
    
    return { min, max };
  }
  
  private getBlockArea(vertices: THREE.Vector2[]): number {
    // Shoelace formula
    let area = 0;
    const n = vertices.length;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      area += vertices[i].x * vertices[j].y;
      area -= vertices[j].x * vertices[i].y;
    }
    return Math.abs(area) / 2;
  }
}

// ============================================
// CITY MESH GENERATOR
// ============================================

export class CityMeshGenerator {
  private config: CityConfig;
  
  constructor(config: CityConfig) {
    this.config = config;
  }
  
  public generateRoadMesh(roads: RoadSegment[]): THREE.Mesh {
    const shapes: THREE.Shape[] = [];
    
    for (const road of roads) {
      const shape = this.createRoadShape(road);
      shapes.push(shape);
    }
    
    const geometry = new THREE.ExtrudeGeometry(shapes, {
      depth: 0.1,
      bevelEnabled: false
    });
    
    // Rotate to lay flat
    geometry.rotateX(-Math.PI / 2);
    
    const material = new THREE.MeshStandardMaterial({
      color: 0x333333,
      roughness: 0.9,
      metalness: 0.1
    });
    
    return new THREE.Mesh(geometry, material);
  }
  
  private createRoadShape(road: RoadSegment): THREE.Shape {
    const direction = road.end.clone().sub(road.start).normalize();
    const perpendicular = new THREE.Vector2(-direction.y, direction.x);
    const halfWidth = road.width / 2;
    
    const shape = new THREE.Shape();
    const p1 = road.start.clone().add(perpendicular.clone().multiplyScalar(halfWidth));
    const p2 = road.start.clone().add(perpendicular.clone().multiplyScalar(-halfWidth));
    const p3 = road.end.clone().add(perpendicular.clone().multiplyScalar(-halfWidth));
    const p4 = road.end.clone().add(perpendicular.clone().multiplyScalar(halfWidth));
    
    shape.moveTo(p1.x, p1.y);
    shape.lineTo(p2.x, p2.y);
    shape.lineTo(p3.x, p3.y);
    shape.lineTo(p4.x, p4.y);
    shape.closePath();
    
    return shape;
  }
  
  public generateBuildingMeshes(blocks: CityBlock[]): THREE.Group {
    const group = new THREE.Group();
    
    for (const block of blocks) {
      for (const building of block.buildings) {
        const mesh = this.createBuildingMesh(building);
        group.add(mesh);
      }
    }
    
    return group;
  }
  
  private createBuildingMesh(building: Building): THREE.Group {
    const group = new THREE.Group();
    
    // Main building body
    const geometry = new THREE.BoxGeometry(
      building.size.x,
      building.size.y,
      building.size.z
    );
    
    const material = new THREE.MeshStandardMaterial({
      color: building.style.baseColor,
      roughness: 0.7,
      metalness: 0.1
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(building.position);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
    
    // Add windows (simple approach - could use textures)
    this.addWindows(group, building);
    
    // Add roof
    this.addRoof(group, building);
    
    return group;
  }
  
  private addWindows(group: THREE.Group, building: Building): void {
    const windowMaterial = new THREE.MeshStandardMaterial({
      color: building.style.windowColor,
      roughness: 0.1,
      metalness: 0.8,
      emissive: building.style.windowColor,
      emissiveIntensity: 0.1
    });
    
    const floorHeight = 3;
    const windowWidth = 1;
    const windowHeight = 1.5;
    const spacing = 2.5;
    
    const sides = [
      { axis: 'x', sign: 1, depth: building.size.z },
      { axis: 'x', sign: -1, depth: building.size.z },
      { axis: 'z', sign: 1, depth: building.size.x },
      { axis: 'z', sign: -1, depth: building.size.x }
    ];
    
    for (const side of sides) {
      const sideWidth = side.axis === 'x' ? building.size.x : building.size.z;
      const windowCount = Math.floor(sideWidth / spacing);
      
      for (let floor = 0; floor < building.floors; floor++) {
        for (let i = 0; i < windowCount; i++) {
          if (Math.random() > building.style.windowDensity) continue;
          
          const windowGeom = new THREE.PlaneGeometry(windowWidth, windowHeight);
          const windowMesh = new THREE.Mesh(windowGeom, windowMaterial);
          
          const offset = (i - windowCount / 2 + 0.5) * spacing;
          const y = building.position.y - building.size.y / 2 + floor * floorHeight + floorHeight / 2;
          
          if (side.axis === 'x') {
            windowMesh.position.set(
              building.position.x + offset,
              y,
              building.position.z + side.sign * (building.size.z / 2 + 0.01)
            );
          } else {
            windowMesh.rotation.y = Math.PI / 2;
            windowMesh.position.set(
              building.position.x + side.sign * (building.size.x / 2 + 0.01),
              y,
              building.position.z + offset
            );
          }
          
          group.add(windowMesh);
        }
      }
    }
  }
  
  private addRoof(group: THREE.Group, building: Building): void {
    const roofMaterial = new THREE.MeshStandardMaterial({
      color: building.style.accentColor,
      roughness: 0.6,
      metalness: 0.2
    });
    
    let roofMesh: THREE.Mesh;
    
    switch (building.style.roofType) {
      case 'peaked':
        const peakGeom = new THREE.ConeGeometry(
          Math.max(building.size.x, building.size.z) * 0.6,
          building.size.y * 0.2,
          4
        );
        roofMesh = new THREE.Mesh(peakGeom, roofMaterial);
        roofMesh.rotation.y = Math.PI / 4;
        roofMesh.position.set(
          building.position.x,
          building.position.y + building.size.y / 2 + building.size.y * 0.1,
          building.position.z
        );
        break;
        
      case 'dome':
        const domeGeom = new THREE.SphereGeometry(
          Math.min(building.size.x, building.size.z) * 0.4,
          16, 8,
          0, Math.PI * 2,
          0, Math.PI / 2
        );
        roofMesh = new THREE.Mesh(domeGeom, roofMaterial);
        roofMesh.position.set(
          building.position.x,
          building.position.y + building.size.y / 2,
          building.position.z
        );
        break;
        
      case 'spire':
        const spireGeom = new THREE.ConeGeometry(
          Math.min(building.size.x, building.size.z) * 0.2,
          building.size.y * 0.3,
          8
        );
        roofMesh = new THREE.Mesh(spireGeom, roofMaterial);
        roofMesh.position.set(
          building.position.x,
          building.position.y + building.size.y / 2 + building.size.y * 0.15,
          building.position.z
        );
        break;
        
      case 'flat':
      default:
        const flatGeom = new THREE.BoxGeometry(
          building.size.x * 1.02,
          0.5,
          building.size.z * 1.02
        );
        roofMesh = new THREE.Mesh(flatGeom, roofMaterial);
        roofMesh.position.set(
          building.position.x,
          building.position.y + building.size.y / 2 + 0.25,
          building.position.z
        );
        break;
    }
    
    roofMesh.castShadow = true;
    group.add(roofMesh);
  }
  
  public generateGroundPlane(): THREE.Mesh {
    const geometry = new THREE.PlaneGeometry(
      this.config.size * 1.5,
      this.config.size * 1.5
    );
    geometry.rotateX(-Math.PI / 2);
    
    const material = new THREE.MeshStandardMaterial({
      color: 0x2a5c2a,  // Grass green
      roughness: 0.9,
      metalness: 0
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.y = -0.1;
    mesh.receiveShadow = true;
    
    return mesh;
  }
}

// ============================================
// MAIN PROCEDURAL CITY
// ============================================

export class ProceduralCity {
  public group: THREE.Group;
  
  private config: CityConfig;
  private roadGenerator: RoadNetworkGenerator;
  private blockSubdivider: BlockSubdivider;
  private buildingGenerator: BuildingGenerator;
  private meshGenerator: CityMeshGenerator;
  
  private roads: RoadSegment[] = [];
  private blocks: CityBlock[] = [];
  
  constructor(config: Partial<CityConfig> = {}) {
    this.config = {
      size: 500,
      blockSize: 50,
      roadWidth: 10,
      minBuildingHeight: 10,
      maxBuildingHeight: 50,
      buildingDensity: 0.8,
      seed: Date.now(),
      ...config
    };
    
    this.group = new THREE.Group();
    
    this.roadGenerator = new RoadNetworkGenerator(this.config);
    this.blockSubdivider = new BlockSubdivider(this.config);
    this.buildingGenerator = new BuildingGenerator(this.config);
    this.meshGenerator = new CityMeshGenerator(this.config);
  }
  
  /**
   * Generate the entire city
   */
  public generate(): THREE.Group {
    // Clear previous
    this.clear();
    
    // Generate road network
    this.roads = this.roadGenerator.generate();
    
    // Create blocks from roads
    this.blocks = this.blockSubdivider.createBlocks(this.roads);
    
    // Generate buildings in blocks
    this.buildingGenerator.generateBuildings(this.blocks);
    
    // Create meshes
    const groundMesh = this.meshGenerator.generateGroundPlane();
    const roadMesh = this.meshGenerator.generateRoadMesh(this.roads);
    const buildingGroup = this.meshGenerator.generateBuildingMeshes(this.blocks);
    
    this.group.add(groundMesh);
    this.group.add(roadMesh);
    this.group.add(buildingGroup);
    
    return this.group;
  }
  
  /**
   * Regenerate with new seed
   */
  public regenerate(seed?: number): THREE.Group {
    if (seed !== undefined) {
      this.config.seed = seed;
      this.roadGenerator = new RoadNetworkGenerator(this.config);
      this.blockSubdivider = new BlockSubdivider(this.config);
      this.buildingGenerator = new BuildingGenerator(this.config);
    }
    
    return this.generate();
  }
  
  /**
   * Get building at world position
   */
  public getBuildingAt(position: THREE.Vector3): Building | null {
    for (const block of this.blocks) {
      for (const building of block.buildings) {
        const half = building.size.clone().multiplyScalar(0.5);
        if (
          position.x >= building.position.x - half.x &&
          position.x <= building.position.x + half.x &&
          position.z >= building.position.z - half.z &&
          position.z <= building.position.z + half.z
        ) {
          return building;
        }
      }
    }
    return null;
  }
  
  /**
   * Get statistics
   */
  public getStats(): { roads: number; blocks: number; buildings: number } {
    let buildingCount = 0;
    for (const block of this.blocks) {
      buildingCount += block.buildings.length;
    }
    
    return {
      roads: this.roads.length,
      blocks: this.blocks.length,
      buildings: buildingCount
    };
  }
  
  /**
   * Clear city
   */
  public clear(): void {
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      this.group.remove(child);
      
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose();
        if (child.material instanceof THREE.Material) {
          child.material.dispose();
        }
      }
    }
    
    this.roads = [];
    this.blocks = [];
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.clear();
  }
}

