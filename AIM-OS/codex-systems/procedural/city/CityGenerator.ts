/**
 * Procedural City Generator
 * Complete city generation: roads, blocks, buildings
 * 
 * Based on research from:
 * - Parish & Müller (2001) - L-system roads
 * - Chen et al. (2008) - Tensor fields
 * - CGA Shape grammar
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export type RoadType = 'highway' | 'major' | 'minor' | 'local';
export type ZoningType = 'residential' | 'commercial' | 'industrial' | 'park' | 'civic';
export type BuildingStyle = 'modern' | 'classical' | 'industrial' | 'residential';

export interface RoadSegment {
  id: string;
  start: THREE.Vector2;
  end: THREE.Vector2;
  type: RoadType;
  width: number;
}

export interface CityBlock {
  id: string;
  polygon: THREE.Vector2[];
  area: number;
  zoning: ZoningType;
}

export interface Parcel {
  id: string;
  polygon: THREE.Vector2[];
  area: number;
  zoning: ZoningType;
  frontage: number;  // Length of road-facing edge
  depth: number;
}

export interface Building {
  id: string;
  parcel: Parcel;
  footprint: THREE.Vector2[];
  height: number;
  floors: number;
  style: BuildingStyle;
  geometry?: THREE.BufferGeometry;
}

export interface CityConfig {
  size: number;              // City diameter in meters
  seed: number;
  density: number;           // 0-1, affects building heights
  gridiness: number;         // 0-1, how grid-like vs organic
  
  // Roads
  highwaySpacing: number;
  majorRoadSpacing: number;
  minorRoadSpacing: number;
  
  // Blocks
  minBlockArea: number;
  maxBlockArea: number;
  
  // Buildings
  minBuildingHeight: number;
  maxBuildingHeight: number;
  buildingCoverage: number;  // 0-1, lot coverage ratio
}

export const DEFAULT_CITY_CONFIG: CityConfig = {
  size: 2000,
  seed: 12345,
  density: 0.6,
  gridiness: 0.7,
  highwaySpacing: 500,
  majorRoadSpacing: 200,
  minorRoadSpacing: 80,
  minBlockArea: 2000,
  maxBlockArea: 20000,
  minBuildingHeight: 3,
  maxBuildingHeight: 100,
  buildingCoverage: 0.6
};

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
  
  public pick<T>(array: T[]): T {
    return array[Math.floor(this.next() * array.length)];
  }
}

// ============================================
// ROAD GENERATOR
// ============================================

export class RoadGenerator {
  private config: CityConfig;
  private random: SeededRandom;
  private segments: RoadSegment[] = [];
  private nextId: number = 0;

  constructor(config: CityConfig) {
    this.config = config;
    this.random = new SeededRandom(config.seed);
  }

  public generate(): RoadSegment[] {
    this.segments = [];
    
    // Generate highway grid
    this.generateHighways();
    
    // Generate major roads
    this.generateMajorRoads();
    
    // Generate minor roads (fills blocks)
    this.generateMinorRoads();
    
    return this.segments;
  }

  private generateHighways(): void {
    const halfSize = this.config.size / 2;
    const spacing = this.config.highwaySpacing;
    
    // Horizontal highways
    for (let y = -halfSize; y <= halfSize; y += spacing) {
      const offset = (this.random.next() - 0.5) * spacing * 0.2;
      this.addSegment(
        new THREE.Vector2(-halfSize, y + offset),
        new THREE.Vector2(halfSize, y + offset),
        'highway'
      );
    }
    
    // Vertical highways
    for (let x = -halfSize; x <= halfSize; x += spacing) {
      const offset = (this.random.next() - 0.5) * spacing * 0.2;
      this.addSegment(
        new THREE.Vector2(x + offset, -halfSize),
        new THREE.Vector2(x + offset, halfSize),
        'highway'
      );
    }
  }

  private generateMajorRoads(): void {
    const halfSize = this.config.size / 2;
    const spacing = this.config.majorRoadSpacing;
    
    // Grid with some randomness based on gridiness
    const jitter = (1 - this.config.gridiness) * spacing * 0.3;
    
    // Horizontal
    for (let y = -halfSize; y <= halfSize; y += spacing) {
      const segments = this.subdivideLine(
        new THREE.Vector2(-halfSize, y),
        new THREE.Vector2(halfSize, y),
        jitter
      );
      
      for (const seg of segments) {
        this.addSegment(seg.start, seg.end, 'major');
      }
    }
    
    // Vertical
    for (let x = -halfSize; x <= halfSize; x += spacing) {
      const segments = this.subdivideLine(
        new THREE.Vector2(x, -halfSize),
        new THREE.Vector2(x, halfSize),
        jitter
      );
      
      for (const seg of segments) {
        this.addSegment(seg.start, seg.end, 'major');
      }
    }
  }

  private generateMinorRoads(): void {
    const halfSize = this.config.size / 2;
    const spacing = this.config.minorRoadSpacing;
    
    const jitter = (1 - this.config.gridiness) * spacing * 0.4;
    
    // Fill between major roads
    for (let y = -halfSize; y <= halfSize; y += spacing) {
      if (Math.abs(y % this.config.majorRoadSpacing) < spacing * 0.5) continue;
      
      const yOffset = (this.random.next() - 0.5) * jitter;
      this.addSegment(
        new THREE.Vector2(-halfSize, y + yOffset),
        new THREE.Vector2(halfSize, y + yOffset),
        'minor'
      );
    }
    
    for (let x = -halfSize; x <= halfSize; x += spacing) {
      if (Math.abs(x % this.config.majorRoadSpacing) < spacing * 0.5) continue;
      
      const xOffset = (this.random.next() - 0.5) * jitter;
      this.addSegment(
        new THREE.Vector2(x + xOffset, -halfSize),
        new THREE.Vector2(x + xOffset, halfSize),
        'minor'
      );
    }
  }

  private subdivideLine(
    start: THREE.Vector2,
    end: THREE.Vector2,
    jitter: number
  ): { start: THREE.Vector2; end: THREE.Vector2 }[] {
    const length = start.distanceTo(end);
    const segments = Math.ceil(length / 100);
    const result: { start: THREE.Vector2; end: THREE.Vector2 }[] = [];
    
    let prevPoint = start.clone();
    
    for (let i = 1; i <= segments; i++) {
      const t = i / segments;
      const point = new THREE.Vector2().lerpVectors(start, end, t);
      
      if (i < segments) {
        const perpendicular = new THREE.Vector2(
          -(end.y - start.y),
          end.x - start.x
        ).normalize();
        
        point.addScaledVector(perpendicular, (this.random.next() - 0.5) * jitter);
      }
      
      result.push({ start: prevPoint.clone(), end: point.clone() });
      prevPoint = point;
    }
    
    return result;
  }

  private addSegment(start: THREE.Vector2, end: THREE.Vector2, type: RoadType): void {
    const widths: Record<RoadType, number> = {
      highway: 20,
      major: 12,
      minor: 8,
      local: 6
    };
    
    this.segments.push({
      id: `road_${this.nextId++}`,
      start: start.clone(),
      end: end.clone(),
      type,
      width: widths[type]
    });
  }
}

// ============================================
// BLOCK GENERATOR
// ============================================

export class BlockGenerator {
  private config: CityConfig;
  private random: SeededRandom;

  constructor(config: CityConfig) {
    this.config = config;
    this.random = new SeededRandom(config.seed + 1);
  }

  public generateBlocks(roads: RoadSegment[]): CityBlock[] {
    // Simplified: create rectangular blocks from road grid
    const blocks: CityBlock[] = [];
    const halfSize = this.config.size / 2;
    
    // Find unique Y coordinates (horizontal roads)
    const yCoords = new Set<number>();
    const xCoords = new Set<number>();
    
    for (const road of roads) {
      if (Math.abs(road.start.y - road.end.y) < 1) {
        // Horizontal road
        yCoords.add(Math.round(road.start.y));
      }
      if (Math.abs(road.start.x - road.end.x) < 1) {
        // Vertical road
        xCoords.add(Math.round(road.start.x));
      }
    }
    
    const sortedY = Array.from(yCoords).sort((a, b) => a - b);
    const sortedX = Array.from(xCoords).sort((a, b) => a - b);
    
    // Create blocks between roads
    for (let i = 0; i < sortedY.length - 1; i++) {
      for (let j = 0; j < sortedX.length - 1; j++) {
        const minY = sortedY[i];
        const maxY = sortedY[i + 1];
        const minX = sortedX[j];
        const maxX = sortedX[j + 1];
        
        // Inset by road width
        const inset = 6;
        const polygon = [
          new THREE.Vector2(minX + inset, minY + inset),
          new THREE.Vector2(maxX - inset, minY + inset),
          new THREE.Vector2(maxX - inset, maxY - inset),
          new THREE.Vector2(minX + inset, maxY - inset)
        ];
        
        const area = (maxX - minX - inset * 2) * (maxY - minY - inset * 2);
        
        if (area > this.config.minBlockArea && area < this.config.maxBlockArea) {
          blocks.push({
            id: `block_${blocks.length}`,
            polygon,
            area,
            zoning: this.assignZoning(minX, minY)
          });
        }
      }
    }
    
    return blocks;
  }

  private assignZoning(x: number, y: number): ZoningType {
    const distFromCenter = Math.sqrt(x * x + y * y);
    const normalizedDist = distFromCenter / (this.config.size / 2);
    
    // Center is commercial
    if (normalizedDist < 0.2) {
      return this.random.next() > 0.3 ? 'commercial' : 'civic';
    }
    
    // Middle ring is mixed
    if (normalizedDist < 0.5) {
      const r = this.random.next();
      if (r < 0.4) return 'commercial';
      if (r < 0.7) return 'residential';
      if (r < 0.85) return 'park';
      return 'industrial';
    }
    
    // Outer ring is mostly residential
    const r = this.random.next();
    if (r < 0.6) return 'residential';
    if (r < 0.8) return 'industrial';
    if (r < 0.95) return 'park';
    return 'commercial';
  }
}

// ============================================
// PARCEL GENERATOR
// ============================================

export class ParcelGenerator {
  private config: CityConfig;
  private random: SeededRandom;

  constructor(config: CityConfig) {
    this.config = config;
    this.random = new SeededRandom(config.seed + 2);
  }

  public subdivideBlock(block: CityBlock): Parcel[] {
    const parcels: Parcel[] = [];
    
    // Determine target parcel size based on zoning
    const targetSizes: Record<ZoningType, number> = {
      residential: 400,
      commercial: 800,
      industrial: 1500,
      park: block.area, // Don't subdivide parks
      civic: 2000
    };
    
    const targetSize = targetSizes[block.zoning];
    
    if (block.area <= targetSize * 1.5) {
      // Block is small enough, use as single parcel
      parcels.push(this.createParcel(block.polygon, block.zoning));
    } else {
      // Subdivide
      const subdivided = this.recursiveSubdivide(block.polygon, targetSize, block.zoning);
      parcels.push(...subdivided);
    }
    
    return parcels;
  }

  private recursiveSubdivide(
    polygon: THREE.Vector2[],
    targetSize: number,
    zoning: ZoningType,
    depth: number = 0
  ): Parcel[] {
    const area = this.computeArea(polygon);
    
    if (area <= targetSize * 1.5 || depth > 5) {
      return [this.createParcel(polygon, zoning)];
    }
    
    // Find longest edge for splitting
    const [left, right] = this.splitPolygon(polygon);
    
    return [
      ...this.recursiveSubdivide(left, targetSize, zoning, depth + 1),
      ...this.recursiveSubdivide(right, targetSize, zoning, depth + 1)
    ];
  }

  private splitPolygon(polygon: THREE.Vector2[]): [THREE.Vector2[], THREE.Vector2[]] {
    // Simplified: split along the middle of the bounding box
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    
    for (const p of polygon) {
      minX = Math.min(minX, p.x);
      maxX = Math.max(maxX, p.x);
      minY = Math.min(minY, p.y);
      maxY = Math.max(maxY, p.y);
    }
    
    const width = maxX - minX;
    const height = maxY - minY;
    
    // Split along longer axis
    if (width > height) {
      const splitX = minX + width * (0.4 + this.random.next() * 0.2);
      return this.splitVertically(polygon, splitX);
    } else {
      const splitY = minY + height * (0.4 + this.random.next() * 0.2);
      return this.splitHorizontally(polygon, splitY);
    }
  }

  private splitVertically(polygon: THREE.Vector2[], x: number): [THREE.Vector2[], THREE.Vector2[]] {
    // Simplified for rectangular polygons
    const left: THREE.Vector2[] = [];
    const right: THREE.Vector2[] = [];
    
    let minY = Infinity, maxY = -Infinity;
    let leftX = -Infinity, rightX = Infinity;
    
    for (const p of polygon) {
      minY = Math.min(minY, p.y);
      maxY = Math.max(maxY, p.y);
      if (p.x < x) leftX = Math.max(leftX, p.x);
      if (p.x > x) rightX = Math.min(rightX, p.x);
    }
    
    // Handle case where split is inside polygon
    leftX = polygon.find(p => p.x < x)?.x ?? polygon[0].x;
    rightX = polygon.find(p => p.x > x)?.x ?? polygon[1].x;
    
    left.push(
      new THREE.Vector2(leftX, minY),
      new THREE.Vector2(x, minY),
      new THREE.Vector2(x, maxY),
      new THREE.Vector2(leftX, maxY)
    );
    
    right.push(
      new THREE.Vector2(x, minY),
      new THREE.Vector2(rightX, minY),
      new THREE.Vector2(rightX, maxY),
      new THREE.Vector2(x, maxY)
    );
    
    return [left, right];
  }

  private splitHorizontally(polygon: THREE.Vector2[], y: number): [THREE.Vector2[], THREE.Vector2[]] {
    const bottom: THREE.Vector2[] = [];
    const top: THREE.Vector2[] = [];
    
    let minX = Infinity, maxX = -Infinity;
    let bottomY = -Infinity, topY = Infinity;
    
    for (const p of polygon) {
      minX = Math.min(minX, p.x);
      maxX = Math.max(maxX, p.x);
      if (p.y < y) bottomY = Math.max(bottomY, p.y);
      if (p.y > y) topY = Math.min(topY, p.y);
    }
    
    bottomY = polygon.find(p => p.y < y)?.y ?? polygon[0].y;
    topY = polygon.find(p => p.y > y)?.y ?? polygon[2].y;
    
    bottom.push(
      new THREE.Vector2(minX, bottomY),
      new THREE.Vector2(maxX, bottomY),
      new THREE.Vector2(maxX, y),
      new THREE.Vector2(minX, y)
    );
    
    top.push(
      new THREE.Vector2(minX, y),
      new THREE.Vector2(maxX, y),
      new THREE.Vector2(maxX, topY),
      new THREE.Vector2(minX, topY)
    );
    
    return [bottom, top];
  }

  private createParcel(polygon: THREE.Vector2[], zoning: ZoningType): Parcel {
    return {
      id: `parcel_${Math.random().toString(36).substr(2, 9)}`,
      polygon,
      area: this.computeArea(polygon),
      zoning,
      frontage: this.computeFrontage(polygon),
      depth: this.computeDepth(polygon)
    };
  }

  private computeArea(polygon: THREE.Vector2[]): number {
    let area = 0;
    for (let i = 0; i < polygon.length; i++) {
      const j = (i + 1) % polygon.length;
      area += polygon[i].x * polygon[j].y;
      area -= polygon[j].x * polygon[i].y;
    }
    return Math.abs(area) / 2;
  }

  private computeFrontage(polygon: THREE.Vector2[]): number {
    // Assume bottom edge is frontage
    let maxLength = 0;
    for (let i = 0; i < polygon.length; i++) {
      const j = (i + 1) % polygon.length;
      const length = polygon[i].distanceTo(polygon[j]);
      maxLength = Math.max(maxLength, length);
    }
    return maxLength;
  }

  private computeDepth(polygon: THREE.Vector2[]): number {
    let minY = Infinity, maxY = -Infinity;
    for (const p of polygon) {
      minY = Math.min(minY, p.y);
      maxY = Math.max(maxY, p.y);
    }
    return maxY - minY;
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
    this.random = new SeededRandom(config.seed + 3);
  }

  public generateBuilding(parcel: Parcel): Building | null {
    if (parcel.zoning === 'park') return null;
    
    // Calculate building footprint (inset from parcel)
    const footprint = this.calculateFootprint(parcel);
    if (!footprint) return null;
    
    // Calculate height based on zoning and location
    const height = this.calculateHeight(parcel);
    const floors = Math.floor(height / 3.5);
    
    // Determine style
    const style = this.determineStyle(parcel);
    
    const building: Building = {
      id: `building_${Math.random().toString(36).substr(2, 9)}`,
      parcel,
      footprint,
      height,
      floors,
      style
    };
    
    // Generate geometry
    building.geometry = this.createGeometry(building);
    
    return building;
  }

  private calculateFootprint(parcel: Parcel): THREE.Vector2[] | null {
    const coverage = this.config.buildingCoverage;
    const inset = Math.sqrt(parcel.area * (1 - coverage)) / 4;
    
    // Inset polygon
    const footprint: THREE.Vector2[] = [];
    const center = new THREE.Vector2();
    
    for (const p of parcel.polygon) {
      center.add(p);
    }
    center.divideScalar(parcel.polygon.length);
    
    for (const p of parcel.polygon) {
      const toCenter = center.clone().sub(p).normalize();
      footprint.push(p.clone().addScaledVector(toCenter, inset));
    }
    
    // Validate area
    const area = this.computeArea(footprint);
    if (area < 50) return null;
    
    return footprint;
  }

  private calculateHeight(parcel: Parcel): number {
    // Get center distance from city center
    let cx = 0, cy = 0;
    for (const p of parcel.polygon) {
      cx += p.x;
      cy += p.y;
    }
    cx /= parcel.polygon.length;
    cy /= parcel.polygon.length;
    
    const distFromCenter = Math.sqrt(cx * cx + cy * cy);
    const normalizedDist = distFromCenter / (this.config.size / 2);
    
    // Height decreases toward edge
    const heightFactor = 1 - normalizedDist * 0.8;
    
    // Zoning affects height
    const zoningFactors: Record<ZoningType, number> = {
      commercial: 1.5,
      civic: 1.2,
      residential: 0.6,
      industrial: 0.4,
      park: 0
    };
    
    const baseHeight = THREE.MathUtils.lerp(
      this.config.minBuildingHeight,
      this.config.maxBuildingHeight,
      heightFactor * this.config.density
    );
    
    return baseHeight * zoningFactors[parcel.zoning] * (0.7 + this.random.next() * 0.6);
  }

  private determineStyle(parcel: Parcel): BuildingStyle {
    const stylesByZoning: Record<ZoningType, BuildingStyle[]> = {
      commercial: ['modern', 'classical'],
      civic: ['classical', 'modern'],
      residential: ['residential', 'modern'],
      industrial: ['industrial'],
      park: ['residential']
    };
    
    return this.random.pick(stylesByZoning[parcel.zoning]);
  }

  private createGeometry(building: Building): THREE.BufferGeometry {
    // Create extruded geometry from footprint
    const shape = new THREE.Shape();
    
    shape.moveTo(building.footprint[0].x, building.footprint[0].y);
    for (let i = 1; i < building.footprint.length; i++) {
      shape.lineTo(building.footprint[i].x, building.footprint[i].y);
    }
    shape.closePath();
    
    const extrudeSettings = {
      depth: building.height,
      bevelEnabled: false
    };
    
    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    
    // Rotate to Y-up
    geometry.rotateX(-Math.PI / 2);
    
    return geometry;
  }

  private computeArea(polygon: THREE.Vector2[]): number {
    let area = 0;
    for (let i = 0; i < polygon.length; i++) {
      const j = (i + 1) % polygon.length;
      area += polygon[i].x * polygon[j].y;
      area -= polygon[j].x * polygon[i].y;
    }
    return Math.abs(area) / 2;
  }
}

// ============================================
// MAIN CITY GENERATOR
// ============================================

export class CityGenerator {
  private config: CityConfig;
  private roadGenerator: RoadGenerator;
  private blockGenerator: BlockGenerator;
  private parcelGenerator: ParcelGenerator;
  private buildingGenerator: BuildingGenerator;

  constructor(config: Partial<CityConfig> = {}) {
    this.config = { ...DEFAULT_CITY_CONFIG, ...config };
    this.roadGenerator = new RoadGenerator(this.config);
    this.blockGenerator = new BlockGenerator(this.config);
    this.parcelGenerator = new ParcelGenerator(this.config);
    this.buildingGenerator = new BuildingGenerator(this.config);
  }

  public generate(): {
    roads: RoadSegment[];
    blocks: CityBlock[];
    parcels: Parcel[];
    buildings: Building[];
    mesh: THREE.Group;
  } {
    console.log('Generating roads...');
    const roads = this.roadGenerator.generate();
    
    console.log('Generating blocks...');
    const blocks = this.blockGenerator.generateBlocks(roads);
    
    console.log('Generating parcels...');
    const parcels: Parcel[] = [];
    for (const block of blocks) {
      parcels.push(...this.parcelGenerator.subdivideBlock(block));
    }
    
    console.log('Generating buildings...');
    const buildings: Building[] = [];
    for (const parcel of parcels) {
      const building = this.buildingGenerator.generateBuilding(parcel);
      if (building) {
        buildings.push(building);
      }
    }
    
    console.log('Creating mesh...');
    const mesh = this.createCityMesh(roads, buildings);
    
    console.log(`Generated: ${roads.length} roads, ${blocks.length} blocks, ${parcels.length} parcels, ${buildings.length} buildings`);
    
    return { roads, blocks, parcels, buildings, mesh };
  }

  private createCityMesh(roads: RoadSegment[], buildings: Building[]): THREE.Group {
    const group = new THREE.Group();
    
    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(this.config.size, this.config.size);
    groundGeometry.rotateX(-Math.PI / 2);
    const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x3a5f0b });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    group.add(ground);
    
    // Roads
    const roadMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
    for (const road of roads) {
      const length = road.start.distanceTo(road.end);
      const roadGeometry = new THREE.PlaneGeometry(length, road.width);
      roadGeometry.rotateX(-Math.PI / 2);
      
      const roadMesh = new THREE.Mesh(roadGeometry, roadMaterial);
      roadMesh.position.set(
        (road.start.x + road.end.x) / 2,
        0.01,
        (road.start.y + road.end.y) / 2
      );
      
      const angle = Math.atan2(road.end.y - road.start.y, road.end.x - road.start.x);
      roadMesh.rotation.y = -angle;
      
      group.add(roadMesh);
    }
    
    // Buildings with colors by zoning
    const zoningColors: Record<ZoningType, number> = {
      commercial: 0x4488cc,
      civic: 0xcccc88,
      residential: 0xcc8866,
      industrial: 0x888888,
      park: 0x44aa44
    };
    
    for (const building of buildings) {
      if (!building.geometry) continue;
      
      const material = new THREE.MeshStandardMaterial({
        color: zoningColors[building.parcel.zoning],
        flatShading: true
      });
      
      const mesh = new THREE.Mesh(building.geometry, material);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      
      group.add(mesh);
    }
    
    return group;
  }
}

