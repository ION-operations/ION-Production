/**
 * NavMesh Pathfinding System
 * Navigation mesh generation and A* pathfinding
 * 
 * Features:
 * - NavMesh generation from geometry
 * - A* pathfinding
 * - Path smoothing
 * - Dynamic obstacle avoidance
 * - Area costs
 * - Off-mesh links (jumps, teleports)
 * - Agent navigation
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface NavMeshConfig {
  cellSize: number;           // XZ cell size
  cellHeight: number;         // Y cell height
  agentRadius: number;        // Agent collision radius
  agentHeight: number;        // Agent height
  maxClimb: number;           // Max step height
  maxSlope: number;           // Max walkable slope (degrees)
  minRegionArea: number;      // Min area for region
}

export interface NavMeshPolygon {
  id: number;
  vertices: THREE.Vector3[];
  center: THREE.Vector3;
  neighbors: number[];
  area: number;
  cost: number;
  flags: number;
}

export interface NavMeshNode {
  polygonId: number;
  g: number;  // Cost from start
  h: number;  // Heuristic to goal
  f: number;  // Total cost
  parent: NavMeshNode | null;
  position: THREE.Vector3;
}

export interface OffMeshLink {
  id: string;
  start: THREE.Vector3;
  end: THREE.Vector3;
  startPolygon: number;
  endPolygon: number;
  bidirectional: boolean;
  cost: number;
  type: 'walk' | 'jump' | 'climb' | 'teleport';
}

export interface NavPath {
  points: THREE.Vector3[];
  polygons: number[];
  totalCost: number;
  valid: boolean;
}

export interface NavAgent {
  id: string;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  radius: number;
  speed: number;
  currentPath: NavPath | null;
  targetPosition: THREE.Vector3 | null;
  currentPolygon: number;
  state: 'idle' | 'moving' | 'stuck';
}

// ============================================
// NAVMESH BUILDER
// ============================================

export class NavMeshBuilder {
  private config: NavMeshConfig;
  
  constructor(config: Partial<NavMeshConfig> = {}) {
    this.config = {
      cellSize: 0.3,
      cellHeight: 0.2,
      agentRadius: 0.5,
      agentHeight: 2.0,
      maxClimb: 0.4,
      maxSlope: 45,
      minRegionArea: 1,
      ...config
    };
  }
  
  /**
   * Build NavMesh from geometry
   */
  public buildFromGeometry(geometry: THREE.BufferGeometry): NavMeshPolygon[] {
    const polygons: NavMeshPolygon[] = [];
    
    const positions = geometry.getAttribute('position');
    const indices = geometry.getIndex();
    
    if (!positions) return polygons;
    
    const triangleCount = indices 
      ? indices.count / 3 
      : positions.count / 3;
    
    // Extract triangles and filter by slope
    for (let i = 0; i < triangleCount; i++) {
      let i0: number, i1: number, i2: number;
      
      if (indices) {
        i0 = indices.getX(i * 3);
        i1 = indices.getX(i * 3 + 1);
        i2 = indices.getX(i * 3 + 2);
      } else {
        i0 = i * 3;
        i1 = i * 3 + 1;
        i2 = i * 3 + 2;
      }
      
      const v0 = new THREE.Vector3(
        positions.getX(i0), positions.getY(i0), positions.getZ(i0)
      );
      const v1 = new THREE.Vector3(
        positions.getX(i1), positions.getY(i1), positions.getZ(i1)
      );
      const v2 = new THREE.Vector3(
        positions.getX(i2), positions.getY(i2), positions.getZ(i2)
      );
      
      // Calculate normal and slope
      const normal = new THREE.Vector3()
        .crossVectors(
          v1.clone().sub(v0),
          v2.clone().sub(v0)
        )
        .normalize();
      
      const slope = Math.acos(normal.dot(new THREE.Vector3(0, 1, 0))) * 180 / Math.PI;
      
      // Only include walkable triangles
      if (slope <= this.config.maxSlope) {
        const center = new THREE.Vector3()
          .add(v0).add(v1).add(v2)
          .divideScalar(3);
        
        const area = this.calculateTriangleArea(v0, v1, v2);
        
        if (area >= this.config.minRegionArea) {
          polygons.push({
            id: polygons.length,
            vertices: [v0, v1, v2],
            center,
            neighbors: [],
            area,
            cost: 1,
            flags: 1 // Walkable
          });
        }
      }
    }
    
    // Find neighbors
    this.findNeighbors(polygons);
    
    return polygons;
  }
  
  private calculateTriangleArea(v0: THREE.Vector3, v1: THREE.Vector3, v2: THREE.Vector3): number {
    const a = v1.clone().sub(v0);
    const b = v2.clone().sub(v0);
    return a.cross(b).length() / 2;
  }
  
  private findNeighbors(polygons: NavMeshPolygon[]): void {
    // Build edge map
    const edgeMap = new Map<string, number[]>();
    
    for (const poly of polygons) {
      for (let i = 0; i < poly.vertices.length; i++) {
        const v0 = poly.vertices[i];
        const v1 = poly.vertices[(i + 1) % poly.vertices.length];
        
        const key = this.edgeKey(v0, v1);
        
        if (!edgeMap.has(key)) {
          edgeMap.set(key, []);
        }
        edgeMap.get(key)!.push(poly.id);
      }
    }
    
    // Find shared edges
    for (const [_, polyIds] of edgeMap) {
      if (polyIds.length === 2) {
        const poly0 = polygons[polyIds[0]];
        const poly1 = polygons[polyIds[1]];
        
        if (!poly0.neighbors.includes(poly1.id)) {
          poly0.neighbors.push(poly1.id);
        }
        if (!poly1.neighbors.includes(poly0.id)) {
          poly1.neighbors.push(poly0.id);
        }
      }
    }
  }
  
  private edgeKey(v0: THREE.Vector3, v1: THREE.Vector3): string {
    // Order vertices for consistent key
    const key0 = `${v0.x.toFixed(3)},${v0.y.toFixed(3)},${v0.z.toFixed(3)}`;
    const key1 = `${v1.x.toFixed(3)},${v1.y.toFixed(3)},${v1.z.toFixed(3)}`;
    return key0 < key1 ? `${key0}-${key1}` : `${key1}-${key0}`;
  }
}

// ============================================
// A* PATHFINDER
// ============================================

export class AStarPathfinder {
  private polygons: NavMeshPolygon[];
  private offMeshLinks: OffMeshLink[] = [];
  
  constructor(polygons: NavMeshPolygon[]) {
    this.polygons = polygons;
  }
  
  /**
   * Add off-mesh link
   */
  public addOffMeshLink(link: OffMeshLink): void {
    this.offMeshLinks.push(link);
  }
  
  /**
   * Find path between two points
   */
  public findPath(start: THREE.Vector3, end: THREE.Vector3): NavPath {
    const startPoly = this.findClosestPolygon(start);
    const endPoly = this.findClosestPolygon(end);
    
    if (startPoly === -1 || endPoly === -1) {
      return { points: [], polygons: [], totalCost: Infinity, valid: false };
    }
    
    // A* search
    const openSet: NavMeshNode[] = [];
    const closedSet = new Set<number>();
    
    const startNode: NavMeshNode = {
      polygonId: startPoly,
      g: 0,
      h: this.heuristic(startPoly, endPoly),
      f: 0,
      parent: null,
      position: start.clone()
    };
    startNode.f = startNode.g + startNode.h;
    
    openSet.push(startNode);
    
    while (openSet.length > 0) {
      // Get node with lowest f
      openSet.sort((a, b) => a.f - b.f);
      const current = openSet.shift()!;
      
      // Check if reached goal
      if (current.polygonId === endPoly) {
        return this.reconstructPath(current, start, end);
      }
      
      closedSet.add(current.polygonId);
      
      // Get neighbors
      const polygon = this.polygons[current.polygonId];
      
      for (const neighborId of polygon.neighbors) {
        if (closedSet.has(neighborId)) continue;
        
        const neighborPoly = this.polygons[neighborId];
        const g = current.g + this.movementCost(current.polygonId, neighborId);
        
        // Check if already in open set
        const existingNode = openSet.find(n => n.polygonId === neighborId);
        
        if (!existingNode || g < existingNode.g) {
          const node: NavMeshNode = {
            polygonId: neighborId,
            g,
            h: this.heuristic(neighborId, endPoly),
            f: 0,
            parent: current,
            position: neighborPoly.center.clone()
          };
          node.f = node.g + node.h;
          
          if (existingNode) {
            existingNode.g = g;
            existingNode.f = node.f;
            existingNode.parent = current;
          } else {
            openSet.push(node);
          }
        }
      }
      
      // Check off-mesh links
      for (const link of this.offMeshLinks) {
        if (link.startPolygon === current.polygonId && !closedSet.has(link.endPolygon)) {
          const g = current.g + link.cost;
          const existingNode = openSet.find(n => n.polygonId === link.endPolygon);
          
          if (!existingNode || g < existingNode.g) {
            const node: NavMeshNode = {
              polygonId: link.endPolygon,
              g,
              h: this.heuristic(link.endPolygon, endPoly),
              f: 0,
              parent: current,
              position: link.end.clone()
            };
            node.f = node.g + node.h;
            
            if (existingNode) {
              existingNode.g = g;
              existingNode.f = node.f;
              existingNode.parent = current;
            } else {
              openSet.push(node);
            }
          }
        }
      }
    }
    
    // No path found
    return { points: [], polygons: [], totalCost: Infinity, valid: false };
  }
  
  private heuristic(fromId: number, toId: number): number {
    const from = this.polygons[fromId].center;
    const to = this.polygons[toId].center;
    return from.distanceTo(to);
  }
  
  private movementCost(fromId: number, toId: number): number {
    const from = this.polygons[fromId];
    const to = this.polygons[toId];
    
    const distance = from.center.distanceTo(to.center);
    return distance * to.cost;
  }
  
  private reconstructPath(node: NavMeshNode, start: THREE.Vector3, end: THREE.Vector3): NavPath {
    const points: THREE.Vector3[] = [end.clone()];
    const polygons: number[] = [];
    let totalCost = node.g;
    
    let current: NavMeshNode | null = node;
    
    while (current) {
      polygons.unshift(current.polygonId);
      if (current.parent) {
        points.unshift(current.position.clone());
      }
      current = current.parent;
    }
    
    points.unshift(start.clone());
    
    // Smooth path using string-pulling
    const smoothedPoints = this.smoothPath(points, polygons);
    
    return {
      points: smoothedPoints,
      polygons,
      totalCost,
      valid: true
    };
  }
  
  /**
   * String-pulling path smoothing
   */
  private smoothPath(points: THREE.Vector3[], polygons: number[]): THREE.Vector3[] {
    if (points.length <= 2) return points;
    
    const smoothed: THREE.Vector3[] = [points[0]];
    let apex = 0;
    let leftIdx = 1;
    let rightIdx = 1;
    
    let portalLeft = points[1].clone();
    let portalRight = points[1].clone();
    
    for (let i = 2; i < points.length; i++) {
      const left = points[i].clone();
      const right = points[i].clone();
      
      // Update portal
      if (this.triArea2D(points[apex], portalRight, right) <= 0) {
        if (points[apex].equals(portalRight) || 
            this.triArea2D(points[apex], portalLeft, right) > 0) {
          portalRight.copy(right);
          rightIdx = i;
        } else {
          smoothed.push(portalLeft.clone());
          apex = leftIdx;
          portalLeft.copy(points[apex]);
          portalRight.copy(points[apex]);
          leftIdx = apex;
          rightIdx = apex;
          i = apex;
          continue;
        }
      }
      
      if (this.triArea2D(points[apex], portalLeft, left) >= 0) {
        if (points[apex].equals(portalLeft) ||
            this.triArea2D(points[apex], portalRight, left) < 0) {
          portalLeft.copy(left);
          leftIdx = i;
        } else {
          smoothed.push(portalRight.clone());
          apex = rightIdx;
          portalLeft.copy(points[apex]);
          portalRight.copy(points[apex]);
          leftIdx = apex;
          rightIdx = apex;
          i = apex;
          continue;
        }
      }
    }
    
    smoothed.push(points[points.length - 1].clone());
    
    return smoothed;
  }
  
  private triArea2D(a: THREE.Vector3, b: THREE.Vector3, c: THREE.Vector3): number {
    return (c.x - a.x) * (b.z - a.z) - (b.x - a.x) * (c.z - a.z);
  }
  
  /**
   * Find closest polygon to point
   */
  public findClosestPolygon(point: THREE.Vector3): number {
    let closestId = -1;
    let closestDist = Infinity;
    
    for (const poly of this.polygons) {
      const dist = point.distanceTo(poly.center);
      
      if (dist < closestDist) {
        // Check if point is within polygon (simplified)
        if (this.isPointInPolygon(point, poly)) {
          return poly.id;
        }
        
        closestDist = dist;
        closestId = poly.id;
      }
    }
    
    return closestId;
  }
  
  private isPointInPolygon(point: THREE.Vector3, polygon: NavMeshPolygon): boolean {
    // Project to 2D (XZ plane) and check
    const verts = polygon.vertices;
    let inside = false;
    
    for (let i = 0, j = verts.length - 1; i < verts.length; j = i++) {
      if ((verts[i].z > point.z) !== (verts[j].z > point.z) &&
          point.x < (verts[j].x - verts[i].x) * (point.z - verts[i].z) / (verts[j].z - verts[i].z) + verts[i].x) {
        inside = !inside;
      }
    }
    
    return inside;
  }
}

// ============================================
// NAV AGENT CONTROLLER
// ============================================

export class NavAgentController {
  private pathfinder: AStarPathfinder;
  private agents: Map<string, NavAgent> = new Map();
  
  constructor(pathfinder: AStarPathfinder) {
    this.pathfinder = pathfinder;
  }
  
  /**
   * Create agent
   */
  public createAgent(id: string, position: THREE.Vector3, config: Partial<NavAgent> = {}): NavAgent {
    const agent: NavAgent = {
      id,
      position: position.clone(),
      velocity: new THREE.Vector3(),
      radius: 0.5,
      speed: 3,
      currentPath: null,
      targetPosition: null,
      currentPolygon: this.pathfinder.findClosestPolygon(position),
      state: 'idle',
      ...config
    };
    
    this.agents.set(id, agent);
    return agent;
  }
  
  /**
   * Set agent destination
   */
  public setDestination(agentId: string, target: THREE.Vector3): boolean {
    const agent = this.agents.get(agentId);
    if (!agent) return false;
    
    const path = this.pathfinder.findPath(agent.position, target);
    
    if (path.valid) {
      agent.currentPath = path;
      agent.targetPosition = target.clone();
      agent.state = 'moving';
      return true;
    }
    
    return false;
  }
  
  /**
   * Stop agent
   */
  public stopAgent(agentId: string): void {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.currentPath = null;
      agent.targetPosition = null;
      agent.state = 'idle';
      agent.velocity.set(0, 0, 0);
    }
  }
  
  /**
   * Update all agents
   */
  public update(deltaTime: number): void {
    for (const agent of this.agents.values()) {
      this.updateAgent(agent, deltaTime);
    }
  }
  
  private updateAgent(agent: NavAgent, dt: number): void {
    if (agent.state !== 'moving' || !agent.currentPath) return;
    
    const path = agent.currentPath;
    
    if (path.points.length === 0) {
      agent.state = 'idle';
      return;
    }
    
    // Get next waypoint
    const nextPoint = path.points[0];
    const toNext = nextPoint.clone().sub(agent.position);
    toNext.y = 0; // Ignore vertical
    
    const distance = toNext.length();
    
    if (distance < 0.3) {
      // Reached waypoint
      path.points.shift();
      
      if (path.points.length === 0) {
        // Reached destination
        agent.state = 'idle';
        agent.currentPath = null;
        agent.velocity.set(0, 0, 0);
        return;
      }
    }
    
    // Move towards waypoint
    const direction = toNext.normalize();
    agent.velocity.copy(direction.multiplyScalar(agent.speed));
    
    agent.position.add(agent.velocity.clone().multiplyScalar(dt));
    
    // Update current polygon
    agent.currentPolygon = this.pathfinder.findClosestPolygon(agent.position);
  }
  
  /**
   * Get agent
   */
  public getAgent(id: string): NavAgent | undefined {
    return this.agents.get(id);
  }
  
  /**
   * Get all agents
   */
  public getAgents(): NavAgent[] {
    return Array.from(this.agents.values());
  }
  
  /**
   * Remove agent
   */
  public removeAgent(id: string): void {
    this.agents.delete(id);
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.agents.clear();
  }
}

// ============================================
// NAVMESH VISUALIZER
// ============================================

export class NavMeshVisualizer {
  private scene: THREE.Scene;
  private meshGroup: THREE.Group;
  private pathLines: Map<string, THREE.Line> = new Map();
  
  constructor(scene: THREE.Scene) {
    this.scene = scene;
    this.meshGroup = new THREE.Group();
    this.meshGroup.name = 'NavMeshVisualizer';
    scene.add(this.meshGroup);
  }
  
  /**
   * Show NavMesh polygons
   */
  public showPolygons(polygons: NavMeshPolygon[]): void {
    this.clearPolygons();
    
    const material = new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide,
      depthWrite: false
    });
    
    const wireframeMaterial = new THREE.LineBasicMaterial({
      color: 0x00aa00
    });
    
    for (const poly of polygons) {
      // Create mesh
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(poly.vertices.length * 3);
      
      for (let i = 0; i < poly.vertices.length; i++) {
        positions[i * 3] = poly.vertices[i].x;
        positions[i * 3 + 1] = poly.vertices[i].y + 0.01; // Slight offset
        positions[i * 3 + 2] = poly.vertices[i].z;
      }
      
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setIndex([0, 1, 2]);
      
      const mesh = new THREE.Mesh(geometry, material);
      this.meshGroup.add(mesh);
      
      // Create wireframe
      const edges = new THREE.EdgesGeometry(geometry);
      const wireframe = new THREE.LineSegments(edges, wireframeMaterial);
      this.meshGroup.add(wireframe);
    }
  }
  
  /**
   * Show path
   */
  public showPath(id: string, path: NavPath): void {
    this.hidePath(id);
    
    if (!path.valid || path.points.length < 2) return;
    
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(path.points.length * 3);
    
    for (let i = 0; i < path.points.length; i++) {
      positions[i * 3] = path.points[i].x;
      positions[i * 3 + 1] = path.points[i].y + 0.1;
      positions[i * 3 + 2] = path.points[i].z;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.LineBasicMaterial({ color: 0xff0000, linewidth: 2 });
    const line = new THREE.Line(geometry, material);
    
    this.pathLines.set(id, line);
    this.scene.add(line);
  }
  
  /**
   * Hide path
   */
  public hidePath(id: string): void {
    const line = this.pathLines.get(id);
    if (line) {
      this.scene.remove(line);
      line.geometry.dispose();
      (line.material as THREE.Material).dispose();
      this.pathLines.delete(id);
    }
  }
  
  /**
   * Clear all
   */
  public clearPolygons(): void {
    while (this.meshGroup.children.length > 0) {
      const child = this.meshGroup.children[0];
      this.meshGroup.remove(child);
      
      if ((child as THREE.Mesh).geometry) {
        (child as THREE.Mesh).geometry.dispose();
      }
      if ((child as THREE.Mesh).material) {
        ((child as THREE.Mesh).material as THREE.Material).dispose();
      }
    }
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.clearPolygons();
    this.scene.remove(this.meshGroup);
    
    for (const id of Array.from(this.pathLines.keys())) {
      this.hidePath(id);
    }
  }
}

