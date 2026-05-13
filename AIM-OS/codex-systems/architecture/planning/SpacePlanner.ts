/**
 * Space Planning Engine
 * Generates optimal room layouts from building programs
 * 
 * Algorithms:
 * - Treemap-based allocation (squarified)
 * - Binary Space Partition (BSP)
 * - Force-directed optimization
 * - Simulated annealing refinement
 */

import {
  Vector2D,
  Rectangle,
  Polygon,
  SpaceRequirement,
  BuildingProgram,
  LayoutResult,
  RoomType
} from '../types';

// ============================================
// CONFIGURATION
// ============================================

export interface SpacePlannerConfig {
  algorithm: 'treemap' | 'bsp' | 'force' | 'hybrid';
  minRoomArea: number;
  maxIterations: number;
  adjacencyWeight: number;
  aspectWeight: number;
  circulationWidth: number;
  gridSnap: number;
}

export const DEFAULT_PLANNER_CONFIG: SpacePlannerConfig = {
  algorithm: 'hybrid',
  minRoomArea: 4,          // m²
  maxIterations: 1000,
  adjacencyWeight: 0.4,
  aspectWeight: 0.3,
  circulationWidth: 1.2,   // meters
  gridSnap: 0.1            // 10cm grid
};

// ============================================
// ADJACENCY MATRIX
// ============================================

export class AdjacencyMatrix {
  private matrix: Map<string, Map<string, number>>;
  
  constructor() {
    this.matrix = new Map();
  }
  
  public setAdjacency(id1: string, id2: string, weight: number): void {
    if (!this.matrix.has(id1)) this.matrix.set(id1, new Map());
    if (!this.matrix.has(id2)) this.matrix.set(id2, new Map());
    
    this.matrix.get(id1)!.set(id2, weight);
    this.matrix.get(id2)!.set(id1, weight);
  }
  
  public getAdjacency(id1: string, id2: string): number {
    return this.matrix.get(id1)?.get(id2) ?? 0;
  }
  
  public getNeighbors(id: string): Map<string, number> {
    return this.matrix.get(id) ?? new Map();
  }
  
  public static fromRequirements(spaces: SpaceRequirement[]): AdjacencyMatrix {
    const matrix = new AdjacencyMatrix();
    
    for (const space of spaces) {
      if (space.adjacentTo) {
        for (const adjacent of space.adjacentTo) {
          matrix.setAdjacency(space.id, adjacent, 1.0);
        }
      }
      if (space.awayFrom) {
        for (const away of space.awayFrom) {
          matrix.setAdjacency(space.id, away, -1.0);
        }
      }
    }
    
    // Add common adjacency patterns
    const kitchens = spaces.filter(s => s.type === 'kitchen');
    const dinings = spaces.filter(s => s.type === 'dining');
    const livings = spaces.filter(s => s.type === 'living');
    const bedrooms = spaces.filter(s => s.type === 'bedroom');
    const bathrooms = spaces.filter(s => s.type === 'bathroom');
    
    // Kitchen-Dining adjacency
    for (const k of kitchens) {
      for (const d of dinings) {
        if (matrix.getAdjacency(k.id, d.id) === 0) {
          matrix.setAdjacency(k.id, d.id, 0.8);
        }
      }
    }
    
    // Living-Dining adjacency
    for (const l of livings) {
      for (const d of dinings) {
        if (matrix.getAdjacency(l.id, d.id) === 0) {
          matrix.setAdjacency(l.id, d.id, 0.6);
        }
      }
    }
    
    // Bedroom-Bathroom adjacency
    for (const b of bedrooms) {
      for (const bath of bathrooms) {
        if (matrix.getAdjacency(b.id, bath.id) === 0) {
          matrix.setAdjacency(b.id, bath.id, 0.5);
        }
      }
    }
    
    return matrix;
  }
}

// ============================================
// TREEMAP ALLOCATOR
// ============================================

export class TreemapAllocator {
  private minRoomArea: number;
  
  constructor(minRoomArea: number = 4) {
    this.minRoomArea = minRoomArea;
  }
  
  /**
   * Squarified Treemap algorithm
   * Produces space-filling rectangular layouts
   */
  public allocate(
    spaces: SpaceRequirement[],
    bounds: Rectangle
  ): Map<string, Rectangle> {
    const allocations = new Map<string, Rectangle>();
    
    // Sort by area (largest first) and priority
    const sorted = [...spaces].sort((a, b) => {
      const priorityDiff = b.priority - a.priority;
      if (priorityDiff !== 0) return priorityDiff;
      return b.area - a.area;
    });
    
    const totalArea = sorted.reduce((sum, s) => sum + s.area, 0);
    
    this.squarify(sorted, bounds, totalArea, allocations);
    
    return allocations;
  }
  
  private squarify(
    spaces: SpaceRequirement[],
    bounds: Rectangle,
    totalArea: number,
    allocations: Map<string, Rectangle>
  ): void {
    if (spaces.length === 0) return;
    
    if (spaces.length === 1) {
      allocations.set(spaces[0].id, bounds);
      return;
    }
    
    // Determine split direction (along shorter side for better aspect ratios)
    const isHorizontal = bounds.width >= bounds.height;
    const sideLength = isHorizontal ? bounds.height : bounds.width;
    
    // Find optimal row
    let row: SpaceRequirement[] = [];
    let rowArea = 0;
    let bestRatio = Infinity;
    let bestRow: SpaceRequirement[] = [];
    let bestRowArea = 0;
    
    for (const space of spaces) {
      const testRow = [...row, space];
      const testRowArea = rowArea + space.area;
      
      const worstRatio = this.worstAspectRatio(testRow, testRowArea, sideLength, bounds, totalArea);
      
      if (worstRatio <= bestRatio) {
        bestRatio = worstRatio;
        bestRow = testRow;
        bestRowArea = testRowArea;
        row = testRow;
        rowArea = testRowArea;
      } else {
        break;  // Adding more spaces makes it worse
      }
    }
    
    // Calculate row length proportional to area ratio
    const areaRatio = bestRowArea / totalArea;
    const rowLength = isHorizontal 
      ? bounds.width * areaRatio 
      : bounds.height * areaRatio;
    
    // Layout row
    let offset = 0;
    for (const space of bestRow) {
      const spaceRatio = space.area / bestRowArea;
      const spaceLength = sideLength * spaceRatio;
      
      const spaceRect = isHorizontal
        ? new Rectangle(bounds.x, bounds.y + offset, rowLength, spaceLength)
        : new Rectangle(bounds.x + offset, bounds.y, spaceLength, rowLength);
      
      allocations.set(space.id, spaceRect);
      offset += spaceLength;
    }
    
    // Recurse with remaining spaces
    const remaining = spaces.filter(s => !bestRow.includes(s));
    const remainingArea = totalArea - bestRowArea;
    
    if (remaining.length > 0 && remainingArea > this.minRoomArea) {
      const newBounds = isHorizontal
        ? new Rectangle(bounds.x + rowLength, bounds.y, bounds.width - rowLength, bounds.height)
        : new Rectangle(bounds.x, bounds.y + rowLength, bounds.width, bounds.height - rowLength);
      
      this.squarify(remaining, newBounds, remainingArea, allocations);
    }
  }
  
  private worstAspectRatio(
    row: SpaceRequirement[],
    rowArea: number,
    sideLength: number,
    bounds: Rectangle,
    totalArea: number
  ): number {
    if (row.length === 0) return Infinity;
    
    const areaRatio = rowArea / totalArea;
    const rowLength = (bounds.width >= bounds.height)
      ? bounds.width * areaRatio
      : bounds.height * areaRatio;
    
    let worst = 0;
    
    for (const space of row) {
      const spaceRatio = space.area / rowArea;
      const spaceLength = sideLength * spaceRatio;
      
      const aspectRatio = Math.max(spaceLength / rowLength, rowLength / spaceLength);
      
      // Penalize if outside desired range
      if (space.aspectRatio) {
        if (aspectRatio < space.aspectRatio.min || aspectRatio > space.aspectRatio.max) {
          worst = Math.max(worst, aspectRatio * 2);
        }
      }
      
      worst = Math.max(worst, aspectRatio);
    }
    
    return worst;
  }
}

// ============================================
// BSP ALLOCATOR
// ============================================

export class BSPAllocator {
  private minRoomArea: number;
  private random: () => number;
  
  constructor(minRoomArea: number = 4, seed?: number) {
    this.minRoomArea = minRoomArea;
    this.random = seed !== undefined ? this.seededRandom(seed) : Math.random;
  }
  
  private seededRandom(seed: number): () => number {
    return () => {
      seed = (seed * 1103515245 + 12345) & 0x7fffffff;
      return seed / 0x7fffffff;
    };
  }
  
  /**
   * Binary Space Partition allocation
   * Produces orthogonal grid-like layouts
   */
  public allocate(
    spaces: SpaceRequirement[],
    bounds: Rectangle
  ): Map<string, Rectangle> {
    const allocations = new Map<string, Rectangle>();
    
    // Sort by priority
    const sorted = [...spaces].sort((a, b) => b.priority - a.priority);
    
    this.bspAllocate(sorted, bounds, allocations, 0);
    
    return allocations;
  }
  
  private bspAllocate(
    spaces: SpaceRequirement[],
    bounds: Rectangle,
    allocations: Map<string, Rectangle>,
    depth: number
  ): void {
    if (spaces.length === 0) return;
    
    if (spaces.length === 1 || bounds.area() < this.minRoomArea * 2 || depth > 10) {
      // Base case: assign all remaining spaces to current bounds
      if (spaces.length === 1) {
        allocations.set(spaces[0].id, bounds);
      } else {
        // Stack remaining spaces (shouldn't happen often)
        for (const space of spaces) {
          allocations.set(space.id, bounds.clone());
        }
      }
      return;
    }
    
    // Find best split
    const split = this.findBestSplit(spaces, bounds);
    
    // Partition spaces
    const [leftSpaces, rightSpaces] = this.partitionSpaces(spaces, split, bounds);
    const [leftBounds, rightBounds] = this.splitBounds(bounds, split);
    
    // Recurse
    this.bspAllocate(leftSpaces, leftBounds, allocations, depth + 1);
    this.bspAllocate(rightSpaces, rightBounds, allocations, depth + 1);
  }
  
  private findBestSplit(
    spaces: SpaceRequirement[],
    bounds: Rectangle
  ): { direction: 'horizontal' | 'vertical'; ratio: number } {
    let bestSplit: { direction: 'horizontal' | 'vertical'; ratio: number } = {
      direction: bounds.width >= bounds.height ? 'vertical' : 'horizontal',
      ratio: 0.5
    };
    let bestScore = -Infinity;
    
    // Try different split ratios
    for (const direction of ['horizontal', 'vertical'] as const) {
      for (let ratio = 0.3; ratio <= 0.7; ratio += 0.05) {
        const score = this.evaluateSplit(spaces, bounds, { direction, ratio });
        if (score > bestScore) {
          bestScore = score;
          bestSplit = { direction, ratio };
        }
      }
    }
    
    return bestSplit;
  }
  
  private evaluateSplit(
    spaces: SpaceRequirement[],
    bounds: Rectangle,
    split: { direction: 'horizontal' | 'vertical'; ratio: number }
  ): number {
    const [left, right] = this.splitBounds(bounds, split);
    const [leftSpaces, rightSpaces] = this.partitionSpaces(spaces, split, bounds);
    
    // Area match score
    const leftRequired = leftSpaces.reduce((s, sp) => s + sp.area, 0);
    const rightRequired = rightSpaces.reduce((s, sp) => s + sp.area, 0);
    const leftActual = left.area();
    const rightActual = right.area();
    
    let score = 0;
    
    if (leftRequired > 0 && leftActual > 0) {
      score -= Math.abs(leftRequired - leftActual) / leftRequired * 0.5;
    }
    if (rightRequired > 0 && rightActual > 0) {
      score -= Math.abs(rightRequired - rightActual) / rightRequired * 0.5;
    }
    
    // Aspect ratio score
    score -= Math.abs(1 - left.aspectRatio()) * 0.3;
    score -= Math.abs(1 - right.aspectRatio()) * 0.3;
    
    // Balance score (prefer even splits)
    score -= Math.abs(leftSpaces.length - rightSpaces.length) * 0.1;
    
    return score;
  }
  
  private splitBounds(
    bounds: Rectangle,
    split: { direction: 'horizontal' | 'vertical'; ratio: number }
  ): [Rectangle, Rectangle] {
    if (split.direction === 'vertical') {
      const splitX = bounds.x + bounds.width * split.ratio;
      return [
        new Rectangle(bounds.x, bounds.y, splitX - bounds.x, bounds.height),
        new Rectangle(splitX, bounds.y, bounds.x + bounds.width - splitX, bounds.height)
      ];
    } else {
      const splitY = bounds.y + bounds.height * split.ratio;
      return [
        new Rectangle(bounds.x, bounds.y, bounds.width, splitY - bounds.y),
        new Rectangle(bounds.x, splitY, bounds.width, bounds.y + bounds.height - splitY)
      ];
    }
  }
  
  private partitionSpaces(
    spaces: SpaceRequirement[],
    split: { direction: 'horizontal' | 'vertical'; ratio: number },
    bounds: Rectangle
  ): [SpaceRequirement[], SpaceRequirement[]] {
    // Greedily assign spaces to minimize area difference
    const totalArea = spaces.reduce((s, sp) => s + sp.area, 0);
    const targetLeft = totalArea * split.ratio;
    
    let leftArea = 0;
    const leftSpaces: SpaceRequirement[] = [];
    const rightSpaces: SpaceRequirement[] = [];
    
    for (const space of spaces) {
      if (leftArea + space.area <= targetLeft * 1.2 || leftSpaces.length === 0) {
        leftSpaces.push(space);
        leftArea += space.area;
      } else {
        rightSpaces.push(space);
      }
    }
    
    return [leftSpaces, rightSpaces];
  }
}

// ============================================
// FORCE-DIRECTED OPTIMIZER
// ============================================

interface LayoutNode {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  area: number;
  width: number;
  height: number;
  fixed?: boolean;
}

export class ForceDirectedOptimizer {
  private nodes: Map<string, LayoutNode>;
  private adjacency: AdjacencyMatrix;
  private bounds: Rectangle;
  private config: SpacePlannerConfig;
  
  constructor(
    initialLayout: Map<string, Rectangle>,
    adjacency: AdjacencyMatrix,
    bounds: Rectangle,
    config: SpacePlannerConfig
  ) {
    this.nodes = new Map();
    this.adjacency = adjacency;
    this.bounds = bounds;
    this.config = config;
    
    // Convert rectangles to nodes
    for (const [id, rect] of initialLayout) {
      this.nodes.set(id, {
        id,
        x: rect.center().x,
        y: rect.center().y,
        vx: 0,
        vy: 0,
        area: rect.area(),
        width: rect.width,
        height: rect.height
      });
    }
  }
  
  /**
   * Optimize layout using force-directed simulation
   */
  public optimize(iterations: number = 500): Map<string, Rectangle> {
    for (let i = 0; i < iterations; i++) {
      const alpha = 1 - i / iterations;  // Cooling
      this.step(alpha);
    }
    
    return this.toRectangles();
  }
  
  private step(alpha: number): void {
    const nodes = Array.from(this.nodes.values());
    
    // Reset velocities
    for (const node of nodes) {
      node.vx = 0;
      node.vy = 0;
    }
    
    // Repulsion between all nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        this.applyRepulsion(nodes[i], nodes[j], alpha);
      }
    }
    
    // Attraction for adjacent nodes
    for (const node of nodes) {
      const neighbors = this.adjacency.getNeighbors(node.id);
      for (const [neighborId, weight] of neighbors) {
        const neighbor = this.nodes.get(neighborId);
        if (neighbor && weight > 0) {
          this.applyAttraction(node, neighbor, weight, alpha);
        } else if (neighbor && weight < 0) {
          this.applyRepulsion(node, neighbor, alpha, Math.abs(weight) * 2);
        }
      }
    }
    
    // Center gravity
    const centerX = this.bounds.center().x;
    const centerY = this.bounds.center().y;
    
    for (const node of nodes) {
      const dx = centerX - node.x;
      const dy = centerY - node.y;
      node.vx += dx * 0.01 * alpha;
      node.vy += dy * 0.01 * alpha;
    }
    
    // Apply velocities and constrain to bounds
    for (const node of nodes) {
      if (node.fixed) continue;
      
      node.x += node.vx;
      node.y += node.vy;
      
      // Constrain to bounds
      const halfW = node.width / 2;
      const halfH = node.height / 2;
      
      node.x = Math.max(this.bounds.minX + halfW, Math.min(this.bounds.maxX - halfW, node.x));
      node.y = Math.max(this.bounds.minY + halfH, Math.min(this.bounds.maxY - halfH, node.y));
    }
  }
  
  private applyRepulsion(a: LayoutNode, b: LayoutNode, alpha: number, strength: number = 1): void {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dist = Math.sqrt(dx * dx + dy * dy) + 0.01;
    
    // Target distance based on sizes
    const targetDist = (a.width + b.width) / 2 + (a.height + b.height) / 2;
    
    if (dist < targetDist) {
      const force = (targetDist - dist) / dist * 0.5 * alpha * strength;
      
      a.vx -= dx * force;
      a.vy -= dy * force;
      b.vx += dx * force;
      b.vy += dy * force;
    }
  }
  
  private applyAttraction(a: LayoutNode, b: LayoutNode, weight: number, alpha: number): void {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    
    // Target distance for adjacent rooms (touching)
    const targetDist = (a.width + b.width) / 4 + (a.height + b.height) / 4;
    
    const force = (dist - targetDist) * 0.05 * weight * alpha;
    
    const fx = dx / dist * force;
    const fy = dy / dist * force;
    
    a.vx += fx;
    a.vy += fy;
    b.vx -= fx;
    b.vy -= fy;
  }
  
  private toRectangles(): Map<string, Rectangle> {
    const result = new Map<string, Rectangle>();
    
    for (const [id, node] of this.nodes) {
      result.set(id, new Rectangle(
        node.x - node.width / 2,
        node.y - node.height / 2,
        node.width,
        node.height
      ));
    }
    
    return result;
  }
}

// ============================================
// LAYOUT VALIDATOR
// ============================================

export class LayoutValidator {
  /**
   * Score a layout based on multiple criteria
   */
  public static score(
    layout: Map<string, Rectangle>,
    spaces: SpaceRequirement[],
    adjacency: AdjacencyMatrix,
    bounds: Rectangle
  ): LayoutResult {
    const adjacencyScore = this.scoreAdjacency(layout, adjacency);
    const aspectScore = this.scoreAspectRatios(layout, spaces);
    const circulationScore = this.scoreCirculation(layout);
    
    const totalScore = (adjacencyScore * 0.4) + (aspectScore * 0.3) + (circulationScore * 0.3);
    
    return {
      rooms: layout,
      adjacencyScore,
      aspectScore,
      circulationScore,
      totalScore
    };
  }
  
  private static scoreAdjacency(layout: Map<string, Rectangle>, adjacency: AdjacencyMatrix): number {
    let satisfied = 0;
    let total = 0;
    
    for (const [id, rect] of layout) {
      const neighbors = adjacency.getNeighbors(id);
      
      for (const [neighborId, weight] of neighbors) {
        if (weight <= 0) continue;
        
        total++;
        const neighborRect = layout.get(neighborId);
        
        if (neighborRect && this.areAdjacent(rect, neighborRect)) {
          satisfied++;
        }
      }
    }
    
    return total > 0 ? satisfied / total : 1;
  }
  
  private static areAdjacent(a: Rectangle, b: Rectangle, tolerance: number = 0.5): boolean {
    // Check if rectangles share an edge (with tolerance)
    const xOverlap = Math.max(0, Math.min(a.maxX, b.maxX) - Math.max(a.minX, b.minX));
    const yOverlap = Math.max(0, Math.min(a.maxY, b.maxY) - Math.max(a.minY, b.minY));
    
    const xGap = Math.max(a.minX, b.minX) - Math.min(a.maxX, b.maxX);
    const yGap = Math.max(a.minY, b.minY) - Math.min(a.maxY, b.maxY);
    
    // Adjacent horizontally
    if (yOverlap > 0 && Math.abs(xGap) < tolerance) return true;
    
    // Adjacent vertically
    if (xOverlap > 0 && Math.abs(yGap) < tolerance) return true;
    
    return false;
  }
  
  private static scoreAspectRatios(layout: Map<string, Rectangle>, spaces: SpaceRequirement[]): number {
    let score = 0;
    let count = 0;
    
    for (const space of spaces) {
      const rect = layout.get(space.id);
      if (!rect) continue;
      
      const aspect = rect.aspectRatio();
      const idealRange = space.aspectRatio || { min: 0.5, max: 2.0 };
      
      if (aspect >= idealRange.min && aspect <= idealRange.max) {
        score += 1;
      } else {
        // Partial score based on how far from ideal
        const deviation = aspect < idealRange.min
          ? idealRange.min / aspect
          : aspect / idealRange.max;
        
        score += Math.max(0, 1 - (deviation - 1) * 0.5);
      }
      
      count++;
    }
    
    return count > 0 ? score / count : 1;
  }
  
  private static scoreCirculation(layout: Map<string, Rectangle>): number {
    // Simple heuristic: penalty for overlaps
    let overlaps = 0;
    const rects = Array.from(layout.values());
    
    for (let i = 0; i < rects.length; i++) {
      for (let j = i + 1; j < rects.length; j++) {
        if (rects[i].intersects(rects[j])) {
          overlaps++;
        }
      }
    }
    
    const maxOverlaps = (rects.length * (rects.length - 1)) / 2;
    return maxOverlaps > 0 ? 1 - (overlaps / maxOverlaps) : 1;
  }
}

// ============================================
// MAIN SPACE PLANNER
// ============================================

export class SpacePlanner {
  private config: SpacePlannerConfig;
  
  constructor(config: Partial<SpacePlannerConfig> = {}) {
    this.config = { ...DEFAULT_PLANNER_CONFIG, ...config };
  }
  
  /**
   * Generate optimal room layout from building program
   */
  public plan(program: BuildingProgram, bounds: Rectangle): LayoutResult {
    // Build adjacency matrix
    const adjacency = AdjacencyMatrix.fromRequirements(program.spaces);
    
    // Initial allocation
    let layout: Map<string, Rectangle>;
    
    switch (this.config.algorithm) {
      case 'treemap':
        layout = new TreemapAllocator(this.config.minRoomArea).allocate(program.spaces, bounds);
        break;
        
      case 'bsp':
        layout = new BSPAllocator(this.config.minRoomArea).allocate(program.spaces, bounds);
        break;
        
      case 'force':
        // Start with treemap, then optimize
        layout = new TreemapAllocator(this.config.minRoomArea).allocate(program.spaces, bounds);
        layout = new ForceDirectedOptimizer(layout, adjacency, bounds, this.config)
          .optimize(this.config.maxIterations);
        break;
        
      case 'hybrid':
      default:
        // Try both, pick best
        const treemapLayout = new TreemapAllocator(this.config.minRoomArea).allocate(program.spaces, bounds);
        const bspLayout = new BSPAllocator(this.config.minRoomArea).allocate(program.spaces, bounds);
        
        const treemapScore = LayoutValidator.score(treemapLayout, program.spaces, adjacency, bounds);
        const bspScore = LayoutValidator.score(bspLayout, program.spaces, adjacency, bounds);
        
        const bestInitial = treemapScore.totalScore > bspScore.totalScore ? treemapLayout : bspLayout;
        
        // Optimize with force-directed
        layout = new ForceDirectedOptimizer(bestInitial, adjacency, bounds, this.config)
          .optimize(this.config.maxIterations / 2);
        break;
    }
    
    // Snap to grid
    layout = this.snapToGrid(layout, this.config.gridSnap);
    
    // Resolve overlaps
    layout = this.resolveOverlaps(layout);
    
    return LayoutValidator.score(layout, program.spaces, adjacency, bounds);
  }
  
  private snapToGrid(layout: Map<string, Rectangle>, gridSize: number): Map<string, Rectangle> {
    const snapped = new Map<string, Rectangle>();
    
    for (const [id, rect] of layout) {
      snapped.set(id, new Rectangle(
        Math.round(rect.x / gridSize) * gridSize,
        Math.round(rect.y / gridSize) * gridSize,
        Math.round(rect.width / gridSize) * gridSize,
        Math.round(rect.height / gridSize) * gridSize
      ));
    }
    
    return snapped;
  }
  
  private resolveOverlaps(layout: Map<string, Rectangle>, iterations: number = 50): Map<string, Rectangle> {
    const rects = new Map(layout);
    
    for (let iter = 0; iter < iterations; iter++) {
      let hasOverlap = false;
      
      const entries = Array.from(rects.entries());
      
      for (let i = 0; i < entries.length; i++) {
        for (let j = i + 1; j < entries.length; j++) {
          const [id1, rect1] = entries[i];
          const [id2, rect2] = entries[j];
          
          if (rect1.intersects(rect2)) {
            hasOverlap = true;
            
            // Push apart
            const c1 = rect1.center();
            const c2 = rect2.center();
            const dx = c2.x - c1.x;
            const dy = c2.y - c1.y;
            const dist = Math.sqrt(dx * dx + dy * dy) + 0.01;
            
            const overlapX = (rect1.width + rect2.width) / 2 - Math.abs(dx);
            const overlapY = (rect1.height + rect2.height) / 2 - Math.abs(dy);
            
            const pushX = (dx / dist) * Math.max(0, overlapX) / 2;
            const pushY = (dy / dist) * Math.max(0, overlapY) / 2;
            
            rects.set(id1, new Rectangle(rect1.x - pushX, rect1.y - pushY, rect1.width, rect1.height));
            rects.set(id2, new Rectangle(rect2.x + pushX, rect2.y + pushY, rect2.width, rect2.height));
          }
        }
      }
      
      if (!hasOverlap) break;
    }
    
    return rects;
  }
}

