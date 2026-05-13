/**
 * Floor Plan Parser
 * Converts 2D architectural drawings (images, vectors) to structured data
 * 
 * Capabilities:
 * - Line detection and vectorization
 * - Wall recognition
 * - Opening detection (doors, windows)
 * - Room segmentation
 * - Symbol recognition
 * - Dimension extraction
 */

import {
  Vector2D,
  Rectangle,
  Polygon,
  LineSegment,
  Wall2D,
  Door2D,
  Window2D,
  Room2D,
  Floor2D,
  RoomType,
  WallType
} from '../types';

// ============================================
// IMAGE PROCESSING TYPES
// ============================================

export interface ImageData {
  width: number;
  height: number;
  data: Uint8ClampedArray;  // RGBA
}

export interface GrayscaleImage {
  width: number;
  height: number;
  data: Float32Array;
}

export interface BinaryImage {
  width: number;
  height: number;
  data: Uint8Array;
}

// ============================================
// DETECTED ELEMENTS
// ============================================

export interface DetectedLine {
  start: Vector2D;
  end: Vector2D;
  strength: number;
  thickness: number;
}

export interface DetectedSymbol {
  type: 'door' | 'window' | 'stair' | 'fixture' | 'furniture' | 'unknown';
  subtype?: string;
  position: Vector2D;
  bounds: Rectangle;
  rotation: number;
  confidence: number;
}

export interface DetectedDimension {
  value: number;
  unit: 'mm' | 'cm' | 'm' | 'ft' | 'in';
  start: Vector2D;
  end: Vector2D;
  confidence: number;
}

export interface DetectedText {
  text: string;
  position: Vector2D;
  bounds: Rectangle;
  confidence: number;
}

export interface ParsedFloorPlan {
  walls: Wall2D[];
  doors: Door2D[];
  windows: Window2D[];
  rooms: Room2D[];
  dimensions: DetectedDimension[];
  texts: DetectedText[];
  scale: number;  // Pixels per meter
  confidence: number;
}

// ============================================
// IMAGE PREPROCESSING
// ============================================

export class ImagePreprocessor {
  /**
   * Convert RGBA to grayscale
   */
  public toGrayscale(image: ImageData): GrayscaleImage {
    const gray = new Float32Array(image.width * image.height);
    
    for (let i = 0; i < image.width * image.height; i++) {
      const r = image.data[i * 4];
      const g = image.data[i * 4 + 1];
      const b = image.data[i * 4 + 2];
      // Luminance formula
      gray[i] = 0.299 * r + 0.587 * g + 0.114 * b;
    }
    
    return { width: image.width, height: image.height, data: gray };
  }
  
  /**
   * Adaptive thresholding (Sauvola's method)
   */
  public adaptiveThreshold(
    gray: GrayscaleImage,
    windowSize: number = 15,
    k: number = 0.2,
    r: number = 128
  ): BinaryImage {
    const binary = new Uint8Array(gray.width * gray.height);
    const halfWindow = Math.floor(windowSize / 2);
    
    // Compute integral image and integral of squares
    const integral = this.computeIntegralImage(gray);
    const integralSq = this.computeIntegralSquareImage(gray);
    
    for (let y = 0; y < gray.height; y++) {
      for (let x = 0; x < gray.width; x++) {
        const x1 = Math.max(0, x - halfWindow);
        const y1 = Math.max(0, y - halfWindow);
        const x2 = Math.min(gray.width - 1, x + halfWindow);
        const y2 = Math.min(gray.height - 1, y + halfWindow);
        
        const count = (x2 - x1 + 1) * (y2 - y1 + 1);
        
        const sum = this.getIntegralSum(integral, x1, y1, x2, y2, gray.width);
        const sumSq = this.getIntegralSum(integralSq, x1, y1, x2, y2, gray.width);
        
        const mean = sum / count;
        const variance = sumSq / count - mean * mean;
        const stddev = Math.sqrt(Math.max(0, variance));
        
        // Sauvola threshold
        const threshold = mean * (1 + k * (stddev / r - 1));
        
        const idx = y * gray.width + x;
        binary[idx] = gray.data[idx] > threshold ? 255 : 0;
      }
    }
    
    return { width: gray.width, height: gray.height, data: binary };
  }
  
  private computeIntegralImage(gray: GrayscaleImage): Float64Array {
    const integral = new Float64Array((gray.width + 1) * (gray.height + 1));
    const w = gray.width + 1;
    
    for (let y = 1; y <= gray.height; y++) {
      let rowSum = 0;
      for (let x = 1; x <= gray.width; x++) {
        rowSum += gray.data[(y - 1) * gray.width + (x - 1)];
        integral[y * w + x] = integral[(y - 1) * w + x] + rowSum;
      }
    }
    
    return integral;
  }
  
  private computeIntegralSquareImage(gray: GrayscaleImage): Float64Array {
    const integral = new Float64Array((gray.width + 1) * (gray.height + 1));
    const w = gray.width + 1;
    
    for (let y = 1; y <= gray.height; y++) {
      let rowSum = 0;
      for (let x = 1; x <= gray.width; x++) {
        const val = gray.data[(y - 1) * gray.width + (x - 1)];
        rowSum += val * val;
        integral[y * w + x] = integral[(y - 1) * w + x] + rowSum;
      }
    }
    
    return integral;
  }
  
  private getIntegralSum(
    integral: Float64Array,
    x1: number, y1: number,
    x2: number, y2: number,
    originalWidth: number
  ): number {
    const w = originalWidth + 1;
    return integral[(y2 + 1) * w + (x2 + 1)]
         - integral[y1 * w + (x2 + 1)]
         - integral[(y2 + 1) * w + x1]
         + integral[y1 * w + x1];
  }
  
  /**
   * Morphological operations
   */
  public dilate(binary: BinaryImage, kernelSize: number = 3): BinaryImage {
    const result = new Uint8Array(binary.width * binary.height);
    const half = Math.floor(kernelSize / 2);
    
    for (let y = 0; y < binary.height; y++) {
      for (let x = 0; x < binary.width; x++) {
        let maxVal = 0;
        
        for (let ky = -half; ky <= half; ky++) {
          for (let kx = -half; kx <= half; kx++) {
            const ny = y + ky;
            const nx = x + kx;
            
            if (ny >= 0 && ny < binary.height && nx >= 0 && nx < binary.width) {
              maxVal = Math.max(maxVal, binary.data[ny * binary.width + nx]);
            }
          }
        }
        
        result[y * binary.width + x] = maxVal;
      }
    }
    
    return { width: binary.width, height: binary.height, data: result };
  }
  
  public erode(binary: BinaryImage, kernelSize: number = 3): BinaryImage {
    const result = new Uint8Array(binary.width * binary.height);
    const half = Math.floor(kernelSize / 2);
    
    for (let y = 0; y < binary.height; y++) {
      for (let x = 0; x < binary.width; x++) {
        let minVal = 255;
        
        for (let ky = -half; ky <= half; ky++) {
          for (let kx = -half; kx <= half; kx++) {
            const ny = y + ky;
            const nx = x + kx;
            
            if (ny >= 0 && ny < binary.height && nx >= 0 && nx < binary.width) {
              minVal = Math.min(minVal, binary.data[ny * binary.width + nx]);
            }
          }
        }
        
        result[y * binary.width + x] = minVal;
      }
    }
    
    return { width: binary.width, height: binary.height, data: result };
  }
  
  /**
   * Zhang-Suen thinning (skeletonization)
   */
  public thin(binary: BinaryImage): BinaryImage {
    const result = new Uint8Array(binary.data);
    const width = binary.width;
    const height = binary.height;
    
    let changed = true;
    
    while (changed) {
      changed = false;
      
      // First sub-iteration
      const toRemove1: number[] = [];
      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          if (result[y * width + x] === 0) continue;
          
          const p = this.getNeighbors(result, x, y, width);
          const a = this.countTransitions(p);
          const b = this.countNonzero(p);
          
          if (b >= 2 && b <= 6 && a === 1) {
            if (p[0] * p[2] * p[4] === 0 && p[2] * p[4] * p[6] === 0) {
              toRemove1.push(y * width + x);
            }
          }
        }
      }
      
      for (const idx of toRemove1) {
        result[idx] = 0;
        changed = true;
      }
      
      // Second sub-iteration
      const toRemove2: number[] = [];
      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          if (result[y * width + x] === 0) continue;
          
          const p = this.getNeighbors(result, x, y, width);
          const a = this.countTransitions(p);
          const b = this.countNonzero(p);
          
          if (b >= 2 && b <= 6 && a === 1) {
            if (p[0] * p[2] * p[6] === 0 && p[0] * p[4] * p[6] === 0) {
              toRemove2.push(y * width + x);
            }
          }
        }
      }
      
      for (const idx of toRemove2) {
        result[idx] = 0;
        changed = true;
      }
    }
    
    return { width, height, data: result };
  }
  
  private getNeighbors(data: Uint8Array, x: number, y: number, width: number): number[] {
    // P2, P3, P4, P5, P6, P7, P8, P9 (clockwise from top)
    return [
      data[(y - 1) * width + x] > 0 ? 1 : 0,      // P2
      data[(y - 1) * width + (x + 1)] > 0 ? 1 : 0, // P3
      data[y * width + (x + 1)] > 0 ? 1 : 0,       // P4
      data[(y + 1) * width + (x + 1)] > 0 ? 1 : 0, // P5
      data[(y + 1) * width + x] > 0 ? 1 : 0,       // P6
      data[(y + 1) * width + (x - 1)] > 0 ? 1 : 0, // P7
      data[y * width + (x - 1)] > 0 ? 1 : 0,       // P8
      data[(y - 1) * width + (x - 1)] > 0 ? 1 : 0  // P9
    ];
  }
  
  private countTransitions(p: number[]): number {
    let count = 0;
    for (let i = 0; i < 8; i++) {
      if (p[i] === 0 && p[(i + 1) % 8] === 1) count++;
    }
    return count;
  }
  
  private countNonzero(p: number[]): number {
    return p.reduce((sum, val) => sum + val, 0);
  }
}

// ============================================
// LINE DETECTION (LSD - Line Segment Detector)
// ============================================

export class LineDetector {
  private gradientThreshold: number = 5;
  private minLineLength: number = 10;
  private maxLineGap: number = 3;
  
  /**
   * Detect line segments using gradient-based approach
   */
  public detectLines(gray: GrayscaleImage): DetectedLine[] {
    // Compute gradients
    const { gx, gy, magnitude, angle } = this.computeGradients(gray);
    
    // Find line support regions
    const regions = this.findLineRegions(magnitude, angle, gray.width, gray.height);
    
    // Fit lines to regions
    const lines: DetectedLine[] = [];
    
    for (const region of regions) {
      const line = this.fitLineToRegion(region, gray.width);
      if (line && line.start.distanceTo(line.end) >= this.minLineLength) {
        lines.push(line);
      }
    }
    
    // Merge collinear segments
    const merged = this.mergeCollinearLines(lines);
    
    return merged;
  }
  
  private computeGradients(gray: GrayscaleImage): {
    gx: Float32Array;
    gy: Float32Array;
    magnitude: Float32Array;
    angle: Float32Array;
  } {
    const size = gray.width * gray.height;
    const gx = new Float32Array(size);
    const gy = new Float32Array(size);
    const magnitude = new Float32Array(size);
    const angle = new Float32Array(size);
    
    for (let y = 1; y < gray.height - 1; y++) {
      for (let x = 1; x < gray.width - 1; x++) {
        const idx = y * gray.width + x;
        
        // Sobel operators
        gx[idx] = (
          -gray.data[idx - gray.width - 1] + gray.data[idx - gray.width + 1]
          - 2 * gray.data[idx - 1] + 2 * gray.data[idx + 1]
          - gray.data[idx + gray.width - 1] + gray.data[idx + gray.width + 1]
        ) / 8;
        
        gy[idx] = (
          -gray.data[idx - gray.width - 1] - 2 * gray.data[idx - gray.width] - gray.data[idx - gray.width + 1]
          + gray.data[idx + gray.width - 1] + 2 * gray.data[idx + gray.width] + gray.data[idx + gray.width + 1]
        ) / 8;
        
        magnitude[idx] = Math.sqrt(gx[idx] * gx[idx] + gy[idx] * gy[idx]);
        angle[idx] = Math.atan2(gy[idx], gx[idx]);
      }
    }
    
    return { gx, gy, magnitude, angle };
  }
  
  private findLineRegions(
    magnitude: Float32Array,
    angle: Float32Array,
    width: number,
    height: number
  ): Set<number>[] {
    const regions: Set<number>[] = [];
    const visited = new Set<number>();
    const angleTolerance = Math.PI / 8;  // 22.5 degrees
    
    // Sort pixels by gradient magnitude
    const pixels: { idx: number; mag: number }[] = [];
    for (let i = 0; i < magnitude.length; i++) {
      if (magnitude[i] > this.gradientThreshold) {
        pixels.push({ idx: i, mag: magnitude[i] });
      }
    }
    pixels.sort((a, b) => b.mag - a.mag);
    
    // Region growing
    for (const pixel of pixels) {
      if (visited.has(pixel.idx)) continue;
      
      const region = new Set<number>();
      const queue = [pixel.idx];
      const refAngle = angle[pixel.idx];
      
      while (queue.length > 0) {
        const current = queue.shift()!;
        if (visited.has(current)) continue;
        
        const currentAngle = angle[current];
        const angleDiff = Math.abs(this.normalizeAngle(currentAngle - refAngle));
        
        if (angleDiff > angleTolerance && angleDiff < Math.PI - angleTolerance) {
          continue;
        }
        
        visited.add(current);
        region.add(current);
        
        // Check 8-neighbors
        const x = current % width;
        const y = Math.floor(current / width);
        
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            if (dx === 0 && dy === 0) continue;
            
            const nx = x + dx;
            const ny = y + dy;
            
            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
              const nidx = ny * width + nx;
              if (!visited.has(nidx) && magnitude[nidx] > this.gradientThreshold) {
                queue.push(nidx);
              }
            }
          }
        }
      }
      
      if (region.size >= this.minLineLength) {
        regions.push(region);
      }
    }
    
    return regions;
  }
  
  private normalizeAngle(angle: number): number {
    while (angle < -Math.PI) angle += 2 * Math.PI;
    while (angle > Math.PI) angle -= 2 * Math.PI;
    return angle;
  }
  
  private fitLineToRegion(region: Set<number>, width: number): DetectedLine | null {
    if (region.size < 2) return null;
    
    const points: Vector2D[] = [];
    for (const idx of region) {
      const x = idx % width;
      const y = Math.floor(idx / width);
      points.push(new Vector2D(x, y));
    }
    
    // PCA to find principal axis
    let sumX = 0, sumY = 0;
    for (const p of points) {
      sumX += p.x;
      sumY += p.y;
    }
    const meanX = sumX / points.length;
    const meanY = sumY / points.length;
    
    let cxx = 0, cxy = 0, cyy = 0;
    for (const p of points) {
      const dx = p.x - meanX;
      const dy = p.y - meanY;
      cxx += dx * dx;
      cxy += dx * dy;
      cyy += dy * dy;
    }
    
    // Principal eigenvector
    const trace = cxx + cyy;
    const det = cxx * cyy - cxy * cxy;
    const eigenvalue = trace / 2 + Math.sqrt(trace * trace / 4 - det);
    
    let vx = cxy;
    let vy = eigenvalue - cxx;
    const len = Math.sqrt(vx * vx + vy * vy);
    if (len > 0) {
      vx /= len;
      vy /= len;
    } else {
      vx = 1;
      vy = 0;
    }
    
    // Project points to find endpoints
    let minT = Infinity, maxT = -Infinity;
    for (const p of points) {
      const t = (p.x - meanX) * vx + (p.y - meanY) * vy;
      minT = Math.min(minT, t);
      maxT = Math.max(maxT, t);
    }
    
    return {
      start: new Vector2D(meanX + minT * vx, meanY + minT * vy),
      end: new Vector2D(meanX + maxT * vx, meanY + maxT * vy),
      strength: points.length,
      thickness: this.estimateThickness(region, width, vx, vy)
    };
  }
  
  private estimateThickness(region: Set<number>, width: number, vx: number, vy: number): number {
    // Perpendicular direction
    const px = -vy;
    const py = vx;
    
    const projections: number[] = [];
    for (const idx of region) {
      const x = idx % width;
      const y = Math.floor(idx / width);
      const proj = x * px + y * py;
      projections.push(proj);
    }
    
    projections.sort((a, b) => a - b);
    return projections[projections.length - 1] - projections[0] + 1;
  }
  
  private mergeCollinearLines(lines: DetectedLine[]): DetectedLine[] {
    const merged: DetectedLine[] = [];
    const used = new Set<number>();
    
    const collinearityThreshold = 5;  // Pixels
    const angleThreshold = Math.PI / 36;  // 5 degrees
    
    for (let i = 0; i < lines.length; i++) {
      if (used.has(i)) continue;
      
      let current = lines[i];
      used.add(i);
      
      let merged_any = true;
      while (merged_any) {
        merged_any = false;
        
        for (let j = 0; j < lines.length; j++) {
          if (used.has(j)) continue;
          
          const other = lines[j];
          
          // Check if collinear and close
          if (this.areCollinear(current, other, angleThreshold, collinearityThreshold)) {
            // Merge
            current = this.mergeLines(current, other);
            used.add(j);
            merged_any = true;
          }
        }
      }
      
      merged.push(current);
    }
    
    return merged;
  }
  
  private areCollinear(
    a: DetectedLine,
    b: DetectedLine,
    angleThreshold: number,
    distanceThreshold: number
  ): boolean {
    const angleA = Math.atan2(a.end.y - a.start.y, a.end.x - a.start.x);
    const angleB = Math.atan2(b.end.y - b.start.y, b.end.x - b.start.x);
    
    const angleDiff = Math.abs(this.normalizeAngle(angleA - angleB));
    if (angleDiff > angleThreshold && angleDiff < Math.PI - angleThreshold) {
      return false;
    }
    
    // Check distance between lines
    const segA = new LineSegment(a.start, a.end);
    const segB = new LineSegment(b.start, b.end);
    
    const distAtoB = Math.min(
      segA.distanceToPoint(b.start),
      segA.distanceToPoint(b.end)
    );
    const distBtoA = Math.min(
      segB.distanceToPoint(a.start),
      segB.distanceToPoint(a.end)
    );
    
    return Math.min(distAtoB, distBtoA) < distanceThreshold;
  }
  
  private mergeLines(a: DetectedLine, b: DetectedLine): DetectedLine {
    const points = [a.start, a.end, b.start, b.end];
    
    // Find endpoints that are farthest apart
    let maxDist = 0;
    let p1 = a.start, p2 = a.end;
    
    for (let i = 0; i < 4; i++) {
      for (let j = i + 1; j < 4; j++) {
        const dist = points[i].distanceTo(points[j]);
        if (dist > maxDist) {
          maxDist = dist;
          p1 = points[i];
          p2 = points[j];
        }
      }
    }
    
    return {
      start: p1,
      end: p2,
      strength: a.strength + b.strength,
      thickness: Math.max(a.thickness, b.thickness)
    };
  }
}

// ============================================
// WALL DETECTOR
// ============================================

export class WallDetector {
  private minWallLength: number = 20;  // Pixels
  private wallThicknessRange: { min: number; max: number } = { min: 3, max: 30 };
  
  /**
   * Detect walls from line segments
   */
  public detectWalls(lines: DetectedLine[], scale: number): Wall2D[] {
    const walls: Wall2D[] = [];
    
    // Filter lines that could be walls (thick enough, long enough)
    const wallCandidates = lines.filter(line => {
      const length = line.start.distanceTo(line.end);
      return length >= this.minWallLength &&
             line.thickness >= this.wallThicknessRange.min &&
             line.thickness <= this.wallThicknessRange.max;
    });
    
    // Group parallel lines (wall pairs)
    const wallPairs = this.groupParallelLines(wallCandidates);
    
    let wallId = 0;
    
    for (const pair of wallPairs) {
      // Calculate wall centerline
      const centerStart = pair[0].start.lerp(pair[1].start, 0.5);
      const centerEnd = pair[0].end.lerp(pair[1].end, 0.5);
      
      // Calculate thickness
      const thickness = Math.abs(
        pair[0].start.distanceTo(pair[1].start) +
        pair[0].end.distanceTo(pair[1].end)
      ) / 2 / scale;
      
      walls.push({
        id: `wall_${wallId++}`,
        start: new Vector2D(centerStart.x / scale, centerStart.y / scale),
        end: new Vector2D(centerEnd.x / scale, centerEnd.y / scale),
        thickness,
        type: this.classifyWallType(thickness)
      });
    }
    
    // Also handle single thick lines as walls
    for (const line of wallCandidates) {
      const isPaired = wallPairs.some(pair => 
        pair[0] === line || pair[1] === line
      );
      
      if (!isPaired && line.thickness >= 5) {
        walls.push({
          id: `wall_${wallId++}`,
          start: new Vector2D(line.start.x / scale, line.start.y / scale),
          end: new Vector2D(line.end.x / scale, line.end.y / scale),
          thickness: line.thickness / scale,
          type: this.classifyWallType(line.thickness / scale)
        });
      }
    }
    
    return walls;
  }
  
  private groupParallelLines(lines: DetectedLine[]): [DetectedLine, DetectedLine][] {
    const pairs: [DetectedLine, DetectedLine][] = [];
    const used = new Set<number>();
    
    for (let i = 0; i < lines.length; i++) {
      if (used.has(i)) continue;
      
      const line1 = lines[i];
      const angle1 = Math.atan2(line1.end.y - line1.start.y, line1.end.x - line1.start.x);
      
      let bestMatch: number | null = null;
      let bestDistance = Infinity;
      
      for (let j = i + 1; j < lines.length; j++) {
        if (used.has(j)) continue;
        
        const line2 = lines[j];
        const angle2 = Math.atan2(line2.end.y - line2.start.y, line2.end.x - line2.start.x);
        
        // Check if parallel
        const angleDiff = Math.abs(angle1 - angle2);
        if (angleDiff > 0.1 && angleDiff < Math.PI - 0.1) continue;
        
        // Check distance
        const dist = this.parallelLineDistance(line1, line2);
        if (dist >= this.wallThicknessRange.min && dist <= this.wallThicknessRange.max * 1.5) {
          if (dist < bestDistance) {
            bestDistance = dist;
            bestMatch = j;
          }
        }
      }
      
      if (bestMatch !== null) {
        pairs.push([line1, lines[bestMatch]]);
        used.add(i);
        used.add(bestMatch);
      }
    }
    
    return pairs;
  }
  
  private parallelLineDistance(a: DetectedLine, b: DetectedLine): number {
    const seg = new LineSegment(a.start, a.end);
    return (seg.distanceToPoint(b.start) + seg.distanceToPoint(b.end)) / 2;
  }
  
  private classifyWallType(thickness: number): WallType {
    if (thickness >= 0.25) return 'exterior';
    if (thickness >= 0.15) return 'interior';
    return 'partition';
  }
}

// ============================================
// ROOM DETECTOR
// ============================================

export class RoomDetector {
  private minRoomArea: number = 2;  // m²
  
  /**
   * Detect rooms as enclosed spaces
   */
  public detectRooms(walls: Wall2D[]): Room2D[] {
    // Build wall graph
    const graph = this.buildWallGraph(walls);
    
    // Find minimal cycles
    const cycles = this.findMinimalCycles(graph);
    
    // Convert to rooms
    const rooms: Room2D[] = [];
    let roomId = 0;
    
    for (const cycle of cycles) {
      const polygon = new Polygon(cycle.map(n => n.point));
      const area = polygon.area();
      
      if (area >= this.minRoomArea) {
        rooms.push({
          id: `room_${roomId++}`,
          type: 'unknown',
          polygon,
          floor: 0,
          walls: cycle.flatMap(n => n.walls),
          doors: [],
          windows: []
        });
      }
    }
    
    // Classify rooms
    for (const room of rooms) {
      room.type = this.classifyRoom(room, walls);
    }
    
    return rooms;
  }
  
  private buildWallGraph(walls: Wall2D[]): WallGraph {
    const nodes = new Map<string, GraphNode>();
    const epsilon = 0.1;  // Snap distance
    
    const getNodeKey = (p: Vector2D): string => {
      const x = Math.round(p.x / epsilon) * epsilon;
      const y = Math.round(p.y / epsilon) * epsilon;
      return `${x},${y}`;
    };
    
    const getOrCreateNode = (p: Vector2D): GraphNode => {
      const key = getNodeKey(p);
      if (!nodes.has(key)) {
        nodes.set(key, { point: p, neighbors: [], walls: [] });
      }
      return nodes.get(key)!;
    };
    
    for (const wall of walls) {
      const startNode = getOrCreateNode(wall.start);
      const endNode = getOrCreateNode(wall.end);
      
      startNode.neighbors.push(endNode);
      startNode.walls.push(wall.id);
      endNode.neighbors.push(startNode);
      endNode.walls.push(wall.id);
    }
    
    return { nodes: Array.from(nodes.values()) };
  }
  
  private findMinimalCycles(graph: WallGraph): GraphNode[][] {
    const cycles: GraphNode[][] = [];
    
    // For each node, try to find cycles
    for (const startNode of graph.nodes) {
      for (const neighbor of startNode.neighbors) {
        const cycle = this.findCycleFrom(startNode, neighbor, graph);
        if (cycle && cycle.length >= 3) {
          // Check if this cycle is unique
          const isUnique = !cycles.some(c => this.sameCycle(c, cycle));
          if (isUnique) {
            cycles.push(cycle);
          }
        }
      }
    }
    
    return cycles;
  }
  
  private findCycleFrom(start: GraphNode, second: GraphNode, graph: WallGraph): GraphNode[] | null {
    const visited = new Set<GraphNode>();
    const path = [start, second];
    visited.add(start);
    visited.add(second);
    
    let current = second;
    const maxLength = 20;
    
    while (path.length < maxLength) {
      // Find next node (prefer turning left for consistent winding)
      const next = this.findNextNode(current, path[path.length - 2], visited);
      
      if (!next) return null;
      
      if (next === start) {
        return path;  // Cycle complete
      }
      
      path.push(next);
      visited.add(next);
      current = next;
    }
    
    return null;
  }
  
  private findNextNode(current: GraphNode, previous: GraphNode, visited: Set<GraphNode>): GraphNode | null {
    const incomingAngle = Math.atan2(
      current.point.y - previous.point.y,
      current.point.x - previous.point.x
    );
    
    let bestNext: GraphNode | null = null;
    let bestAngle = -Infinity;
    
    for (const neighbor of current.neighbors) {
      if (neighbor === previous) continue;
      
      const outgoingAngle = Math.atan2(
        neighbor.point.y - current.point.y,
        neighbor.point.x - current.point.x
      );
      
      // Turn angle (positive = left turn)
      let turnAngle = outgoingAngle - incomingAngle;
      while (turnAngle > Math.PI) turnAngle -= 2 * Math.PI;
      while (turnAngle < -Math.PI) turnAngle += 2 * Math.PI;
      
      if (!visited.has(neighbor) || neighbor === current.neighbors[0]) {
        if (turnAngle > bestAngle) {
          bestAngle = turnAngle;
          bestNext = neighbor;
        }
      }
    }
    
    return bestNext;
  }
  
  private sameCycle(a: GraphNode[], b: GraphNode[]): boolean {
    if (a.length !== b.length) return false;
    
    // Check if same nodes (possibly rotated)
    const aSet = new Set(a);
    const bSet = new Set(b);
    
    if (aSet.size !== bSet.size) return false;
    
    for (const node of aSet) {
      if (!bSet.has(node)) return false;
    }
    
    return true;
  }
  
  private classifyRoom(room: Room2D, walls: Wall2D[]): RoomType {
    const area = room.polygon.area();
    const bounds = room.polygon.boundingBox();
    const aspectRatio = bounds.width / bounds.height;
    
    // Simple heuristics
    if (aspectRatio > 4 || aspectRatio < 0.25) {
      return 'hallway';
    }
    
    if (area < 4) {
      return 'closet';
    }
    
    if (area < 8) {
      return 'bathroom';  // Or could be small bedroom
    }
    
    if (area > 25) {
      return 'living';
    }
    
    return 'bedroom';  // Default
  }
}

// ============================================
// MAIN FLOOR PLAN PARSER
// ============================================

interface WallGraph {
  nodes: GraphNode[];
}

interface GraphNode {
  point: Vector2D;
  neighbors: GraphNode[];
  walls: string[];
}

export class FloorPlanParser {
  private preprocessor: ImagePreprocessor;
  private lineDetector: LineDetector;
  private wallDetector: WallDetector;
  private roomDetector: RoomDetector;
  
  constructor() {
    this.preprocessor = new ImagePreprocessor();
    this.lineDetector = new LineDetector();
    this.wallDetector = new WallDetector();
    this.roomDetector = new RoomDetector();
  }
  
  /**
   * Parse floor plan image to structured data
   */
  public parse(image: ImageData, options: {
    scale?: number;  // Pixels per meter (if known)
    detectScale?: boolean;
  } = {}): ParsedFloorPlan {
    // 1. Preprocess
    const gray = this.preprocessor.toGrayscale(image);
    const binary = this.preprocessor.adaptiveThreshold(gray);
    
    // 2. Detect lines
    const lines = this.lineDetector.detectLines(gray);
    
    // 3. Estimate scale if needed
    const scale = options.scale ?? (options.detectScale ? this.estimateScale(lines, image) : 100);
    
    // 4. Detect walls
    const walls = this.wallDetector.detectWalls(lines, scale);
    
    // 5. Detect rooms
    const rooms = this.roomDetector.detectRooms(walls);
    
    // 6. Detect openings (simplified)
    const { doors, windows } = this.detectOpenings(walls, lines, scale);
    
    // 7. Calculate confidence
    const confidence = this.calculateConfidence(walls, rooms);
    
    return {
      walls,
      doors,
      windows,
      rooms,
      dimensions: [],
      texts: [],
      scale,
      confidence
    };
  }
  
  private estimateScale(lines: DetectedLine[], image: ImageData): number {
    // Look for dimension lines and text to estimate scale
    // Simplified: assume typical wall lengths
    
    const horizontalLines = lines.filter(l => 
      Math.abs(l.end.y - l.start.y) < Math.abs(l.end.x - l.start.x) * 0.1
    );
    
    if (horizontalLines.length === 0) return 100;
    
    // Find median line length
    const lengths = horizontalLines.map(l => l.start.distanceTo(l.end));
    lengths.sort((a, b) => a - b);
    const medianLength = lengths[Math.floor(lengths.length / 2)];
    
    // Assume median wall is about 4 meters
    return medianLength / 4;
  }
  
  private detectOpenings(
    walls: Wall2D[],
    lines: DetectedLine[],
    scale: number
  ): { doors: Door2D[]; windows: Window2D[] } {
    const doors: Door2D[] = [];
    const windows: Window2D[] = [];
    
    // Find gaps in walls (simplified approach)
    for (const wall of walls) {
      const wallLine = new LineSegment(wall.start, wall.end);
      const wallLength = wallLine.length();
      
      // Look for arcs near wall (door swings)
      // In a real implementation, this would analyze the actual image
      
      // For now, assume gaps of certain sizes are doors/windows
      // This would need actual gap detection from the image
    }
    
    return { doors, windows };
  }
  
  private calculateConfidence(walls: Wall2D[], rooms: Room2D[]): number {
    let score = 0;
    
    // Walls detected
    if (walls.length >= 4) score += 0.3;
    else if (walls.length >= 2) score += 0.1;
    
    // Rooms detected
    if (rooms.length >= 1) score += 0.3;
    if (rooms.length >= 3) score += 0.1;
    
    // Wall connectivity (all walls should connect)
    const connected = this.checkWallConnectivity(walls);
    if (connected) score += 0.3;
    
    return Math.min(1, score);
  }
  
  private checkWallConnectivity(walls: Wall2D[]): boolean {
    if (walls.length < 2) return false;
    
    const epsilon = 0.1;
    const connected = new Set<string>();
    const queue = [walls[0].id];
    connected.add(walls[0].id);
    
    while (queue.length > 0) {
      const currentId = queue.shift()!;
      const current = walls.find(w => w.id === currentId)!;
      
      for (const other of walls) {
        if (connected.has(other.id)) continue;
        
        if (current.start.distanceTo(other.start) < epsilon ||
            current.start.distanceTo(other.end) < epsilon ||
            current.end.distanceTo(other.start) < epsilon ||
            current.end.distanceTo(other.end) < epsilon) {
          connected.add(other.id);
          queue.push(other.id);
        }
      }
    }
    
    return connected.size === walls.length;
  }
}

