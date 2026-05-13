/**
 * Core Types for Architectural Systems
 * Shared types across all architecture modules
 */

import * as THREE from 'three';

// ============================================
// GEOMETRY PRIMITIVES
// ============================================

export class Vector2D {
  constructor(public x: number = 0, public y: number = 0) {}
  
  clone(): Vector2D {
    return new Vector2D(this.x, this.y);
  }
  
  add(v: Vector2D): Vector2D {
    return new Vector2D(this.x + v.x, this.y + v.y);
  }
  
  sub(v: Vector2D): Vector2D {
    return new Vector2D(this.x - v.x, this.y - v.y);
  }
  
  scale(s: number): Vector2D {
    return new Vector2D(this.x * s, this.y * s);
  }
  
  length(): number {
    return Math.sqrt(this.x * this.x + this.y * this.y);
  }
  
  normalize(): Vector2D {
    const len = this.length();
    if (len === 0) return new Vector2D();
    return this.scale(1 / len);
  }
  
  dot(v: Vector2D): number {
    return this.x * v.x + this.y * v.y;
  }
  
  cross(v: Vector2D): number {
    return this.x * v.y - this.y * v.x;
  }
  
  distanceTo(v: Vector2D): number {
    return this.sub(v).length();
  }
  
  angle(): number {
    return Math.atan2(this.y, this.x);
  }
  
  perpendicular(): Vector2D {
    return new Vector2D(-this.y, this.x);
  }
  
  rotate(angle: number): Vector2D {
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    return new Vector2D(
      this.x * cos - this.y * sin,
      this.x * sin + this.y * cos
    );
  }
  
  lerp(v: Vector2D, t: number): Vector2D {
    return new Vector2D(
      this.x + (v.x - this.x) * t,
      this.y + (v.y - this.y) * t
    );
  }
  
  equals(v: Vector2D, epsilon: number = 0.0001): boolean {
    return Math.abs(this.x - v.x) < epsilon && Math.abs(this.y - v.y) < epsilon;
  }
  
  toArray(): [number, number] {
    return [this.x, this.y];
  }
  
  static fromArray(arr: [number, number]): Vector2D {
    return new Vector2D(arr[0], arr[1]);
  }
}

export class Rectangle {
  constructor(
    public x: number,
    public y: number,
    public width: number,
    public height: number
  ) {}
  
  get minX(): number { return this.x; }
  get maxX(): number { return this.x + this.width; }
  get minY(): number { return this.y; }
  get maxY(): number { return this.y + this.height; }
  
  center(): Vector2D {
    return new Vector2D(this.x + this.width / 2, this.y + this.height / 2);
  }
  
  area(): number {
    return this.width * this.height;
  }
  
  aspectRatio(): number {
    return this.width / this.height;
  }
  
  contains(point: Vector2D): boolean {
    return point.x >= this.minX && point.x <= this.maxX &&
           point.y >= this.minY && point.y <= this.maxY;
  }
  
  intersects(other: Rectangle): boolean {
    return !(this.maxX < other.minX || other.maxX < this.minX ||
             this.maxY < other.minY || other.maxY < this.minY);
  }
  
  expand(amount: number): Rectangle {
    return new Rectangle(
      this.x - amount,
      this.y - amount,
      this.width + amount * 2,
      this.height + amount * 2
    );
  }
  
  getCorners(): Vector2D[] {
    return [
      new Vector2D(this.minX, this.minY),
      new Vector2D(this.maxX, this.minY),
      new Vector2D(this.maxX, this.maxY),
      new Vector2D(this.minX, this.maxY)
    ];
  }
  
  getEdges(): LineSegment[] {
    const corners = this.getCorners();
    return [
      new LineSegment(corners[0], corners[1]),
      new LineSegment(corners[1], corners[2]),
      new LineSegment(corners[2], corners[3]),
      new LineSegment(corners[3], corners[0])
    ];
  }
  
  clone(): Rectangle {
    return new Rectangle(this.x, this.y, this.width, this.height);
  }
}

export class LineSegment {
  constructor(
    public start: Vector2D,
    public end: Vector2D
  ) {}
  
  length(): number {
    return this.start.distanceTo(this.end);
  }
  
  direction(): Vector2D {
    return this.end.sub(this.start).normalize();
  }
  
  midpoint(): Vector2D {
    return this.start.lerp(this.end, 0.5);
  }
  
  normal(): Vector2D {
    return this.direction().perpendicular();
  }
  
  pointAt(t: number): Vector2D {
    return this.start.lerp(this.end, t);
  }
  
  distanceToPoint(point: Vector2D): number {
    const v = this.end.sub(this.start);
    const w = point.sub(this.start);
    
    const c1 = w.dot(v);
    if (c1 <= 0) return point.distanceTo(this.start);
    
    const c2 = v.dot(v);
    if (c2 <= c1) return point.distanceTo(this.end);
    
    const t = c1 / c2;
    const projection = this.start.add(v.scale(t));
    return point.distanceTo(projection);
  }
  
  intersects(other: LineSegment): Vector2D | null {
    const p = this.start;
    const r = this.end.sub(this.start);
    const q = other.start;
    const s = other.end.sub(other.start);
    
    const rxs = r.cross(s);
    const qp = q.sub(p);
    
    if (Math.abs(rxs) < 0.0001) return null;  // Parallel
    
    const t = qp.cross(s) / rxs;
    const u = qp.cross(r) / rxs;
    
    if (t >= 0 && t <= 1 && u >= 0 && u <= 1) {
      return p.add(r.scale(t));
    }
    
    return null;
  }
  
  clone(): LineSegment {
    return new LineSegment(this.start.clone(), this.end.clone());
  }
}

export class Polygon {
  constructor(public vertices: Vector2D[]) {}
  
  area(): number {
    let area = 0;
    const n = this.vertices.length;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      area += this.vertices[i].x * this.vertices[j].y;
      area -= this.vertices[j].x * this.vertices[i].y;
    }
    return Math.abs(area) / 2;
  }
  
  centroid(): Vector2D {
    let cx = 0, cy = 0;
    for (const v of this.vertices) {
      cx += v.x;
      cy += v.y;
    }
    return new Vector2D(cx / this.vertices.length, cy / this.vertices.length);
  }
  
  perimeter(): number {
    let p = 0;
    const n = this.vertices.length;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      p += this.vertices[i].distanceTo(this.vertices[j]);
    }
    return p;
  }
  
  isClockwise(): boolean {
    let sum = 0;
    const n = this.vertices.length;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      sum += (this.vertices[j].x - this.vertices[i].x) * 
             (this.vertices[j].y + this.vertices[i].y);
    }
    return sum > 0;
  }
  
  reverse(): Polygon {
    return new Polygon([...this.vertices].reverse());
  }
  
  contains(point: Vector2D): boolean {
    let inside = false;
    const n = this.vertices.length;
    
    for (let i = 0, j = n - 1; i < n; j = i++) {
      const xi = this.vertices[i].x, yi = this.vertices[i].y;
      const xj = this.vertices[j].x, yj = this.vertices[j].y;
      
      if (((yi > point.y) !== (yj > point.y)) &&
          (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi)) {
        inside = !inside;
      }
    }
    
    return inside;
  }
  
  boundingBox(): Rectangle {
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;
    
    for (const v of this.vertices) {
      minX = Math.min(minX, v.x);
      minY = Math.min(minY, v.y);
      maxX = Math.max(maxX, v.x);
      maxY = Math.max(maxY, v.y);
    }
    
    return new Rectangle(minX, minY, maxX - minX, maxY - minY);
  }
  
  getEdges(): LineSegment[] {
    const edges: LineSegment[] = [];
    const n = this.vertices.length;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      edges.push(new LineSegment(this.vertices[i], this.vertices[j]));
    }
    return edges;
  }
  
  offset(distance: number): Polygon {
    // Simple parallel offset (not robust for complex polygons)
    const newVertices: Vector2D[] = [];
    const n = this.vertices.length;
    
    for (let i = 0; i < n; i++) {
      const prev = this.vertices[(i - 1 + n) % n];
      const curr = this.vertices[i];
      const next = this.vertices[(i + 1) % n];
      
      const e1 = curr.sub(prev).normalize();
      const e2 = next.sub(curr).normalize();
      
      const n1 = e1.perpendicular();
      const n2 = e2.perpendicular();
      
      const bisector = n1.add(n2).normalize();
      const sin = e1.cross(bisector);
      const offset = distance / Math.abs(sin);
      
      newVertices.push(curr.add(bisector.scale(offset)));
    }
    
    return new Polygon(newVertices);
  }
  
  clone(): Polygon {
    return new Polygon(this.vertices.map(v => v.clone()));
  }
}

// ============================================
// ARCHITECTURAL ELEMENTS
// ============================================

export type WallType = 'exterior' | 'interior' | 'partition' | 'curtain';
export type DoorType = 'hinged' | 'sliding' | 'pocket' | 'bifold' | 'double' | 'revolving';
export type WindowType = 'fixed' | 'casement' | 'double-hung' | 'sliding' | 'awning' | 'picture';
export type RoomType = 
  | 'living' | 'dining' | 'kitchen' | 'bedroom' | 'bathroom'
  | 'office' | 'hallway' | 'closet' | 'garage' | 'utility'
  | 'balcony' | 'stair' | 'elevator' | 'unknown';

export type RoofType = 'flat' | 'gable' | 'hip' | 'mansard' | 'gambrel' | 'shed' | 'butterfly';

export interface Wall2D {
  id: string;
  start: Vector2D;
  end: Vector2D;
  thickness: number;
  type: WallType;
  height?: number;
  material?: string;
  openings?: Opening2D[];
}

export interface Opening2D {
  id: string;
  type: 'door' | 'window';
  position: Vector2D;  // Center position along wall
  width: number;
  sillHeight: number;  // 0 for doors
  headHeight: number;
  wallId: string;
}

export interface Door2D extends Opening2D {
  type: 'door';
  doorType: DoorType;
  swingDirection: 'left' | 'right' | 'both';
  swingAngle: number;  // In radians, typically 90°
}

export interface Window2D extends Opening2D {
  type: 'window';
  windowType: WindowType;
  paneCount: number;
}

export interface Room2D {
  id: string;
  name?: string;
  type: RoomType;
  polygon: Polygon;
  floor: number;
  height?: number;
  walls: string[];  // Wall IDs
  doors: string[];  // Door IDs
  windows: string[];  // Window IDs
}

export interface Floor2D {
  id: string;
  level: number;
  elevation: number;  // Height from ground
  height: number;     // Floor-to-floor height
  walls: Wall2D[];
  rooms: Room2D[];
  doors: Door2D[];
  windows: Window2D[];
}

export interface Building2D {
  id: string;
  name?: string;
  floors: Floor2D[];
  footprint: Polygon;
  totalArea: number;
}

// ============================================
// 3D BUILDING ELEMENTS
// ============================================

export interface Wall3D {
  id: string;
  geometry: THREE.BufferGeometry;
  position: THREE.Vector3;
  rotation: THREE.Euler;
  material: string;
  openings: Opening3D[];
}

export interface Opening3D {
  id: string;
  type: 'door' | 'window';
  geometry: THREE.BufferGeometry;
  frameGeometry: THREE.BufferGeometry;
  position: THREE.Vector3;
}

export interface Floor3D {
  id: string;
  level: number;
  elevation: number;
  walls: Wall3D[];
  floorSlab: THREE.BufferGeometry;
  ceilingSlab: THREE.BufferGeometry;
}

export interface Roof3D {
  type: RoofType;
  geometry: THREE.BufferGeometry;
  pitch: number;
  overhang: number;
  ridgeHeight: number;
}

export interface Building3D {
  id: string;
  floors: Floor3D[];
  roof: Roof3D;
  group: THREE.Group;
}

// ============================================
// STYLE & CODE TYPES
// ============================================

export type ArchitecturalStyleId = 
  | 'modern' | 'classical' | 'art_deco' | 'victorian' 
  | 'craftsman' | 'colonial' | 'mediterranean' | 'industrial';

export interface NumberRange {
  min: number;
  max: number;
}

export interface MaterialPalette {
  primary: string[];
  secondary: string[];
  accent: string[];
}

export interface ArchitecturalStyle {
  id: ArchitecturalStyleId;
  name: string;
  era: string;
  
  proportions: {
    floorToFloorHeight: NumberRange;
    windowToWallRatio: NumberRange;
    doorHeight: NumberRange;
    ceilingHeight: NumberRange;
  };
  
  roof: {
    types: RoofType[];
    pitchRange: NumberRange;
    overhangRange: NumberRange;
  };
  
  facade: {
    symmetry: 'symmetric' | 'asymmetric' | 'balanced';
    materials: MaterialPalette;
    ornamentLevel: 'minimal' | 'moderate' | 'rich';
  };
  
  windows: {
    types: WindowType[];
    proportions: NumberRange;
  };
  
  doors: {
    types: DoorType[];
  };
  
  details: {
    cornices: boolean;
    pilasters: boolean;
    quoins: boolean;
    stringCourses: boolean;
    balconies: boolean;
  };
}

export interface ValidationResult {
  status: 'pass' | 'fail' | 'warn';
  details?: string;
  location?: string;
}

export interface CodeViolation {
  ruleId: string;
  category: 'egress' | 'fire' | 'accessibility' | 'structural' | 'zoning';
  description: string;
  details: string;
  location: string;
  severity: 'critical' | 'major' | 'minor';
}

export interface ValidationReport {
  valid: boolean;
  violations: CodeViolation[];
  warnings: { ruleId: string; description: string }[];
  score: number;  // 0-100
}

// ============================================
// SPACE PLANNING TYPES
// ============================================

export interface SpaceRequirement {
  id: string;
  name: string;
  type: RoomType;
  area: number;           // Required area in m²
  minArea?: number;
  maxArea?: number;
  aspectRatio?: NumberRange;
  adjacentTo?: string[];  // IDs of spaces that should be adjacent
  awayFrom?: string[];    // IDs of spaces to avoid
  requiresExteriorWall?: boolean;
  requiresNaturalLight?: boolean;
  priority: number;       // Higher = more important
}

export interface BuildingProgram {
  name: string;
  totalArea: number;
  spaces: SpaceRequirement[];
  floors: number;
  style?: ArchitecturalStyleId;
  constraints?: ProgramConstraint[];
}

export interface ProgramConstraint {
  type: 'max_width' | 'max_depth' | 'setback' | 'height_limit' | 'coverage';
  value: number;
}

export interface LayoutResult {
  rooms: Map<string, Rectangle>;
  adjacencyScore: number;  // How well adjacencies are satisfied
  aspectScore: number;     // How good the aspect ratios are
  circulationScore: number;
  totalScore: number;
}

