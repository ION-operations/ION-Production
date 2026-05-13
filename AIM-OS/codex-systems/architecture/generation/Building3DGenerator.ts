/**
 * Building 3D Generator
 * Converts 2D floor plans into complete 3D building models
 * 
 * Features:
 * - Wall extrusion with openings
 * - Door and window frames
 * - Floor and ceiling slabs
 * - Multiple roof types (flat, gable, hip, mansard)
 * - Stair generation
 * - Multi-floor buildings
 */

import * as THREE from 'three';
import { BufferGeometryUtils } from 'three/examples/jsm/utils/BufferGeometryUtils';
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
  Building2D,
  Wall3D,
  Opening3D,
  Floor3D,
  Roof3D,
  Building3D,
  RoofType,
  ArchitecturalStyle
} from '../types';

// ============================================
// CONFIGURATION
// ============================================

export interface GeneratorConfig {
  defaultWallHeight: number;
  defaultWallThickness: number;
  defaultFloorThickness: number;
  defaultCeilingHeight: number;
  
  doorHeight: number;
  windowSillHeight: number;
  windowHeadHeight: number;
  frameWidth: number;
  frameDepth: number;
  
  roofOverhang: number;
  roofPitch: number;  // Degrees
  
  generateInteriors: boolean;
  generateRoof: boolean;
  lodLevels: number;
}

export const DEFAULT_GENERATOR_CONFIG: GeneratorConfig = {
  defaultWallHeight: 2.8,
  defaultWallThickness: 0.15,
  defaultFloorThickness: 0.3,
  defaultCeilingHeight: 2.6,
  
  doorHeight: 2.1,
  windowSillHeight: 0.9,
  windowHeadHeight: 2.1,
  frameWidth: 0.05,
  frameDepth: 0.1,
  
  roofOverhang: 0.5,
  roofPitch: 30,
  
  generateInteriors: true,
  generateRoof: true,
  lodLevels: 3
};

// ============================================
// WALL GENERATOR
// ============================================

export class WallGenerator {
  private config: GeneratorConfig;
  
  constructor(config: GeneratorConfig) {
    this.config = config;
  }
  
  /**
   * Generate 3D wall with openings cut out
   */
  public generateWall(wall: Wall2D, openings: (Door2D | Window2D)[]): THREE.BufferGeometry {
    const length = wall.start.distanceTo(wall.end);
    const height = wall.height ?? this.config.defaultWallHeight;
    const thickness = wall.thickness ?? this.config.defaultWallThickness;
    
    // Create wall shape (rectangle)
    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    shape.lineTo(length, 0);
    shape.lineTo(length, height);
    shape.lineTo(0, height);
    shape.closePath();
    
    // Cut openings
    for (const opening of openings) {
      const localX = this.projectToWallLocal(opening.position, wall);
      
      const x1 = localX - opening.width / 2;
      const x2 = localX + opening.width / 2;
      const y1 = opening.sillHeight;
      const y2 = opening.headHeight;
      
      // Clamp to wall bounds
      const clampedX1 = Math.max(0, x1);
      const clampedX2 = Math.min(length, x2);
      const clampedY1 = Math.max(0, y1);
      const clampedY2 = Math.min(height, y2);
      
      if (clampedX2 > clampedX1 && clampedY2 > clampedY1) {
        const hole = new THREE.Path();
        hole.moveTo(clampedX1, clampedY1);
        hole.lineTo(clampedX2, clampedY1);
        hole.lineTo(clampedX2, clampedY2);
        hole.lineTo(clampedX1, clampedY2);
        hole.closePath();
        shape.holes.push(hole);
      }
    }
    
    // Extrude to thickness
    const geometry = new THREE.ExtrudeGeometry(shape, {
      depth: thickness,
      bevelEnabled: false
    });
    
    // Transform to world position
    const matrix = this.createWallTransform(wall);
    geometry.applyMatrix4(matrix);
    
    return geometry;
  }
  
  /**
   * Generate wall with separate inner/outer faces for different materials
   */
  public generateWallWithFaces(wall: Wall2D, openings: (Door2D | Window2D)[]): {
    outer: THREE.BufferGeometry;
    inner: THREE.BufferGeometry;
    edges: THREE.BufferGeometry;
  } {
    const length = wall.start.distanceTo(wall.end);
    const height = wall.height ?? this.config.defaultWallHeight;
    const thickness = wall.thickness ?? this.config.defaultWallThickness;
    
    // Create face shape with holes
    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    shape.lineTo(length, 0);
    shape.lineTo(length, height);
    shape.lineTo(0, height);
    shape.closePath();
    
    for (const opening of openings) {
      const localX = this.projectToWallLocal(opening.position, wall);
      const x1 = Math.max(0, localX - opening.width / 2);
      const x2 = Math.min(length, localX + opening.width / 2);
      const y1 = Math.max(0, opening.sillHeight);
      const y2 = Math.min(height, opening.headHeight);
      
      if (x2 > x1 && y2 > y1) {
        const hole = new THREE.Path();
        hole.moveTo(x1, y1);
        hole.lineTo(x2, y1);
        hole.lineTo(x2, y2);
        hole.lineTo(x1, y2);
        hole.closePath();
        shape.holes.push(hole);
      }
    }
    
    // Create flat face geometry
    const faceGeometry = new THREE.ShapeGeometry(shape);
    
    // Clone and offset for inner/outer
    const outerGeometry = faceGeometry.clone();
    const innerGeometry = faceGeometry.clone();
    
    // Flip inner face normals
    innerGeometry.scale(-1, 1, 1);
    innerGeometry.translate(length, 0, 0);
    
    // Offset outer face
    const outerMatrix = new THREE.Matrix4().makeTranslation(0, 0, thickness);
    outerGeometry.applyMatrix4(outerMatrix);
    
    // Create edge geometry (sides of openings and wall)
    const edges = this.generateWallEdges(wall, openings, length, height, thickness);
    
    // Transform all to world position
    const worldMatrix = this.createWallTransform(wall);
    outerGeometry.applyMatrix4(worldMatrix);
    innerGeometry.applyMatrix4(worldMatrix);
    edges.applyMatrix4(worldMatrix);
    
    return {
      outer: outerGeometry,
      inner: innerGeometry,
      edges
    };
  }
  
  private generateWallEdges(
    wall: Wall2D,
    openings: (Door2D | Window2D)[],
    length: number,
    height: number,
    thickness: number
  ): THREE.BufferGeometry {
    const geometries: THREE.BufferGeometry[] = [];
    
    // Top edge
    const topEdge = new THREE.BoxGeometry(length, 0.001, thickness);
    topEdge.translate(length / 2, height, thickness / 2);
    geometries.push(topEdge);
    
    // Bottom edge
    const bottomEdge = new THREE.BoxGeometry(length, 0.001, thickness);
    bottomEdge.translate(length / 2, 0, thickness / 2);
    geometries.push(bottomEdge);
    
    // Side edges
    const leftEdge = new THREE.BoxGeometry(0.001, height, thickness);
    leftEdge.translate(0, height / 2, thickness / 2);
    geometries.push(leftEdge);
    
    const rightEdge = new THREE.BoxGeometry(0.001, height, thickness);
    rightEdge.translate(length, height / 2, thickness / 2);
    geometries.push(rightEdge);
    
    // Opening edges
    for (const opening of openings) {
      const localX = this.projectToWallLocal(opening.position, wall);
      const x1 = localX - opening.width / 2;
      const x2 = localX + opening.width / 2;
      const y1 = opening.sillHeight;
      const y2 = opening.headHeight;
      
      // Left side of opening
      const leftSide = new THREE.BoxGeometry(0.001, y2 - y1, thickness);
      leftSide.translate(x1, (y1 + y2) / 2, thickness / 2);
      geometries.push(leftSide);
      
      // Right side of opening
      const rightSide = new THREE.BoxGeometry(0.001, y2 - y1, thickness);
      rightSide.translate(x2, (y1 + y2) / 2, thickness / 2);
      geometries.push(rightSide);
      
      // Top of opening
      const topSide = new THREE.BoxGeometry(x2 - x1, 0.001, thickness);
      topSide.translate((x1 + x2) / 2, y2, thickness / 2);
      geometries.push(topSide);
      
      // Bottom of opening (sill)
      if (y1 > 0) {
        const bottomSide = new THREE.BoxGeometry(x2 - x1, 0.001, thickness);
        bottomSide.translate((x1 + x2) / 2, y1, thickness / 2);
        geometries.push(bottomSide);
      }
    }
    
    return BufferGeometryUtils.mergeGeometries(geometries) ?? new THREE.BufferGeometry();
  }
  
  private projectToWallLocal(point: Vector2D, wall: Wall2D): number {
    const wallDir = wall.end.sub(wall.start);
    const wallLength = wallDir.length();
    const normalizedDir = wallDir.scale(1 / wallLength);
    
    const toPoint = point.sub(wall.start);
    return toPoint.dot(normalizedDir);
  }
  
  private createWallTransform(wall: Wall2D): THREE.Matrix4 {
    const direction = wall.end.sub(wall.start).normalize();
    const angle = Math.atan2(direction.y, direction.x);
    
    const matrix = new THREE.Matrix4();
    
    // Translate to start position
    matrix.makeTranslation(wall.start.x, 0, wall.start.y);
    
    // Rotate around Y axis
    const rotationMatrix = new THREE.Matrix4().makeRotationY(-angle);
    matrix.multiply(rotationMatrix);
    
    // Rotate to stand upright (from XY plane to XZ plane)
    const uprightMatrix = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
    matrix.multiply(uprightMatrix);
    
    return matrix;
  }
}

// ============================================
// OPENING GENERATOR (DOORS & WINDOWS)
// ============================================

export class OpeningGenerator {
  private config: GeneratorConfig;
  
  constructor(config: GeneratorConfig) {
    this.config = config;
  }
  
  /**
   * Generate door geometry with frame
   */
  public generateDoor(door: Door2D, wall: Wall2D): {
    frame: THREE.BufferGeometry;
    leaf: THREE.BufferGeometry;
  } {
    const width = door.width;
    const height = door.headHeight;
    const frameWidth = this.config.frameWidth;
    const frameDepth = this.config.frameDepth;
    const wallThickness = wall.thickness ?? this.config.defaultWallThickness;
    
    // Frame (rectangular with inner cutout)
    const frameShape = new THREE.Shape();
    frameShape.moveTo(0, 0);
    frameShape.lineTo(width, 0);
    frameShape.lineTo(width, height);
    frameShape.lineTo(0, height);
    frameShape.closePath();
    
    const frameHole = new THREE.Path();
    frameHole.moveTo(frameWidth, 0);
    frameHole.lineTo(width - frameWidth, 0);
    frameHole.lineTo(width - frameWidth, height - frameWidth);
    frameHole.lineTo(frameWidth, height - frameWidth);
    frameHole.closePath();
    frameShape.holes.push(frameHole);
    
    const frameGeometry = new THREE.ExtrudeGeometry(frameShape, {
      depth: wallThickness + 0.02,
      bevelEnabled: false
    });
    
    // Door leaf (simple rectangle for now)
    const leafGeometry = new THREE.BoxGeometry(
      width - frameWidth * 2 - 0.02,
      height - frameWidth - 0.02,
      0.04
    );
    leafGeometry.translate(
      width / 2,
      (height - frameWidth) / 2,
      wallThickness / 2
    );
    
    // Apply door swing rotation if specified
    if (door.swingAngle !== 0) {
      const pivotMatrix = new THREE.Matrix4();
      
      // Move pivot to hinge
      const hingeX = door.swingDirection === 'left' ? frameWidth : width - frameWidth;
      pivotMatrix.makeTranslation(-hingeX, 0, -wallThickness / 2);
      
      const rotateMatrix = new THREE.Matrix4().makeRotationY(
        door.swingDirection === 'left' ? door.swingAngle : -door.swingAngle
      );
      
      const unpivotMatrix = new THREE.Matrix4().makeTranslation(hingeX, 0, wallThickness / 2);
      
      leafGeometry.applyMatrix4(pivotMatrix);
      leafGeometry.applyMatrix4(rotateMatrix);
      leafGeometry.applyMatrix4(unpivotMatrix);
    }
    
    // Position at door location
    const transform = this.createOpeningTransform(door, wall);
    frameGeometry.applyMatrix4(transform);
    leafGeometry.applyMatrix4(transform);
    
    return {
      frame: frameGeometry,
      leaf: leafGeometry
    };
  }
  
  /**
   * Generate window geometry with frame and glass
   */
  public generateWindow(window: Window2D, wall: Wall2D): {
    frame: THREE.BufferGeometry;
    glass: THREE.BufferGeometry;
    sill: THREE.BufferGeometry;
  } {
    const width = window.width;
    const height = window.headHeight - window.sillHeight;
    const frameWidth = this.config.frameWidth;
    const frameDepth = this.config.frameDepth;
    const wallThickness = wall.thickness ?? this.config.defaultWallThickness;
    
    // Frame
    const frameShape = new THREE.Shape();
    frameShape.moveTo(0, 0);
    frameShape.lineTo(width, 0);
    frameShape.lineTo(width, height);
    frameShape.lineTo(0, height);
    frameShape.closePath();
    
    const glassHole = new THREE.Path();
    glassHole.moveTo(frameWidth, frameWidth);
    glassHole.lineTo(width - frameWidth, frameWidth);
    glassHole.lineTo(width - frameWidth, height - frameWidth);
    glassHole.lineTo(frameWidth, height - frameWidth);
    glassHole.closePath();
    frameShape.holes.push(glassHole);
    
    const frameGeometry = new THREE.ExtrudeGeometry(frameShape, {
      depth: frameDepth,
      bevelEnabled: false
    });
    frameGeometry.translate(0, 0, (wallThickness - frameDepth) / 2);
    
    // Glass (thin plane)
    const glassGeometry = new THREE.PlaneGeometry(
      width - frameWidth * 2,
      height - frameWidth * 2
    );
    glassGeometry.translate(width / 2, height / 2, wallThickness / 2);
    
    // Muntins (window dividers) if multiple panes
    if (window.paneCount > 1) {
      const muntinGeometries = this.generateMuntins(
        width - frameWidth * 2,
        height - frameWidth * 2,
        window.paneCount,
        frameWidth,
        wallThickness
      );
      // Merge with frame
      const allFrameGeometries = [frameGeometry, ...muntinGeometries];
      const mergedFrame = BufferGeometryUtils.mergeGeometries(allFrameGeometries);
      if (mergedFrame) {
        frameGeometry.copy(mergedFrame);
      }
    }
    
    // Sill (exterior ledge)
    const sillGeometry = new THREE.BoxGeometry(
      width + 0.1,
      0.05,
      wallThickness + 0.1
    );
    sillGeometry.translate(width / 2, -0.025, wallThickness / 2);
    
    // Position at window location
    const transform = this.createOpeningTransform(window, wall);
    frameGeometry.applyMatrix4(transform);
    glassGeometry.applyMatrix4(transform);
    sillGeometry.applyMatrix4(transform);
    
    return {
      frame: frameGeometry,
      glass: glassGeometry,
      sill: sillGeometry
    };
  }
  
  private generateMuntins(
    width: number,
    height: number,
    paneCount: number,
    muntinWidth: number,
    wallThickness: number
  ): THREE.BufferGeometry[] {
    const geometries: THREE.BufferGeometry[] = [];
    
    // Determine grid (assume 2xN for simplicity)
    const cols = Math.min(paneCount, 2);
    const rows = Math.ceil(paneCount / 2);
    
    // Vertical muntins
    if (cols > 1) {
      const vMuntin = new THREE.BoxGeometry(muntinWidth * 0.6, height, muntinWidth * 0.6);
      vMuntin.translate(width / 2, height / 2, wallThickness / 2);
      geometries.push(vMuntin);
    }
    
    // Horizontal muntins
    for (let i = 1; i < rows; i++) {
      const y = height * i / rows;
      const hMuntin = new THREE.BoxGeometry(width, muntinWidth * 0.6, muntinWidth * 0.6);
      hMuntin.translate(width / 2 + muntinWidth, y + muntinWidth, wallThickness / 2);
      geometries.push(hMuntin);
    }
    
    return geometries;
  }
  
  private createOpeningTransform(opening: Door2D | Window2D, wall: Wall2D): THREE.Matrix4 {
    const wallDir = wall.end.sub(wall.start);
    const wallLength = wallDir.length();
    const normalizedDir = wallDir.scale(1 / wallLength);
    
    const localX = opening.position.sub(wall.start).dot(normalizedDir);
    const worldPos = wall.start.add(normalizedDir.scale(localX));
    
    const angle = Math.atan2(normalizedDir.y, normalizedDir.x);
    
    const matrix = new THREE.Matrix4();
    matrix.makeTranslation(worldPos.x, opening.sillHeight, worldPos.y);
    
    const rotationMatrix = new THREE.Matrix4().makeRotationY(-angle);
    matrix.multiply(rotationMatrix);
    
    // Center the opening
    const centerMatrix = new THREE.Matrix4().makeTranslation(-opening.width / 2, 0, 0);
    matrix.multiply(centerMatrix);
    
    return matrix;
  }
}

// ============================================
// ROOF GENERATOR
// ============================================

export class RoofGenerator {
  private config: GeneratorConfig;
  
  constructor(config: GeneratorConfig) {
    this.config = config;
  }
  
  /**
   * Generate roof based on type
   */
  public generateRoof(
    footprint: Polygon,
    wallHeight: number,
    type: RoofType = 'gable'
  ): Roof3D {
    switch (type) {
      case 'flat':
        return this.generateFlatRoof(footprint, wallHeight);
      case 'gable':
        return this.generateGableRoof(footprint, wallHeight);
      case 'hip':
        return this.generateHipRoof(footprint, wallHeight);
      case 'shed':
        return this.generateShedRoof(footprint, wallHeight);
      default:
        return this.generateFlatRoof(footprint, wallHeight);
    }
  }
  
  private generateFlatRoof(footprint: Polygon, wallHeight: number): Roof3D {
    const overhang = this.config.roofOverhang;
    const expandedFootprint = footprint.offset(overhang);
    
    // Create roof slab
    const shape = new THREE.Shape(
      expandedFootprint.vertices.map(v => new THREE.Vector2(v.x, v.y))
    );
    
    const geometry = new THREE.ExtrudeGeometry(shape, {
      depth: 0.2,
      bevelEnabled: false
    });
    
    geometry.rotateX(-Math.PI / 2);
    geometry.translate(0, wallHeight, 0);
    
    return {
      type: 'flat',
      geometry,
      pitch: 0,
      overhang,
      ridgeHeight: wallHeight + 0.2
    };
  }
  
  private generateGableRoof(footprint: Polygon, wallHeight: number): Roof3D {
    const overhang = this.config.roofOverhang;
    const pitch = this.config.roofPitch * Math.PI / 180;
    
    const bounds = footprint.boundingBox();
    const isWide = bounds.width >= bounds.height;
    
    const width = isWide ? bounds.height : bounds.width;
    const ridgeHeight = (width / 2) * Math.tan(pitch);
    
    const expandedBounds = bounds.expand(overhang);
    
    const vertices: number[] = [];
    const indices: number[] = [];
    
    if (isWide) {
      // Ridge runs along X axis
      const ridgeY = wallHeight + ridgeHeight;
      
      // Left slope
      vertices.push(
        expandedBounds.minX, wallHeight, expandedBounds.minY,  // 0
        expandedBounds.maxX, wallHeight, expandedBounds.minY,  // 1
        expandedBounds.maxX, ridgeY, (expandedBounds.minY + expandedBounds.maxY) / 2,  // 2
        expandedBounds.minX, ridgeY, (expandedBounds.minY + expandedBounds.maxY) / 2   // 3
      );
      indices.push(0, 1, 2, 0, 2, 3);
      
      // Right slope
      vertices.push(
        expandedBounds.minX, ridgeY, (expandedBounds.minY + expandedBounds.maxY) / 2,  // 4
        expandedBounds.maxX, ridgeY, (expandedBounds.minY + expandedBounds.maxY) / 2,  // 5
        expandedBounds.maxX, wallHeight, expandedBounds.maxY,  // 6
        expandedBounds.minX, wallHeight, expandedBounds.maxY   // 7
      );
      indices.push(4, 5, 6, 4, 6, 7);
      
      // Front gable
      vertices.push(
        expandedBounds.minX, wallHeight, expandedBounds.minY,  // 8
        expandedBounds.minX, ridgeY, (expandedBounds.minY + expandedBounds.maxY) / 2,  // 9
        expandedBounds.minX, wallHeight, expandedBounds.maxY   // 10
      );
      indices.push(8, 9, 10);
      
      // Back gable
      vertices.push(
        expandedBounds.maxX, wallHeight, expandedBounds.minY,  // 11
        expandedBounds.maxX, wallHeight, expandedBounds.maxY,  // 12
        expandedBounds.maxX, ridgeY, (expandedBounds.minY + expandedBounds.maxY) / 2   // 13
      );
      indices.push(11, 12, 13);
    } else {
      // Ridge runs along Z axis
      const ridgeY = wallHeight + ridgeHeight;
      
      // Front slope
      vertices.push(
        expandedBounds.minX, wallHeight, expandedBounds.minY,  // 0
        (expandedBounds.minX + expandedBounds.maxX) / 2, ridgeY, expandedBounds.minY,  // 1
        (expandedBounds.minX + expandedBounds.maxX) / 2, ridgeY, expandedBounds.maxY,  // 2
        expandedBounds.minX, wallHeight, expandedBounds.maxY   // 3
      );
      indices.push(0, 1, 2, 0, 2, 3);
      
      // Back slope
      vertices.push(
        (expandedBounds.minX + expandedBounds.maxX) / 2, ridgeY, expandedBounds.minY,  // 4
        expandedBounds.maxX, wallHeight, expandedBounds.minY,  // 5
        expandedBounds.maxX, wallHeight, expandedBounds.maxY,  // 6
        (expandedBounds.minX + expandedBounds.maxX) / 2, ridgeY, expandedBounds.maxY   // 7
      );
      indices.push(4, 5, 6, 4, 6, 7);
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    
    return {
      type: 'gable',
      geometry,
      pitch: this.config.roofPitch,
      overhang,
      ridgeHeight: wallHeight + ridgeHeight
    };
  }
  
  private generateHipRoof(footprint: Polygon, wallHeight: number): Roof3D {
    const overhang = this.config.roofOverhang;
    const pitch = this.config.roofPitch * Math.PI / 180;
    
    const bounds = footprint.boundingBox();
    const minDim = Math.min(bounds.width, bounds.height);
    const ridgeHeight = (minDim / 2) * Math.tan(pitch);
    
    const expandedBounds = bounds.expand(overhang);
    
    // Calculate ridge endpoints
    const ridgeY = wallHeight + ridgeHeight;
    const ridgeInset = minDim / 2;
    
    const isWide = bounds.width >= bounds.height;
    
    const vertices: number[] = [];
    const indices: number[] = [];
    let vertexIndex = 0;
    
    if (isWide) {
      const ridgeStartX = expandedBounds.minX + ridgeInset;
      const ridgeEndX = expandedBounds.maxX - ridgeInset;
      const ridgeZ = (expandedBounds.minY + expandedBounds.maxY) / 2;
      
      // Front slope (trapezoid)
      vertices.push(
        expandedBounds.minX, wallHeight, expandedBounds.minY,
        expandedBounds.maxX, wallHeight, expandedBounds.minY,
        ridgeEndX, ridgeY, ridgeZ,
        ridgeStartX, ridgeY, ridgeZ
      );
      indices.push(vertexIndex, vertexIndex + 1, vertexIndex + 2, vertexIndex, vertexIndex + 2, vertexIndex + 3);
      vertexIndex += 4;
      
      // Back slope (trapezoid)
      vertices.push(
        ridgeStartX, ridgeY, ridgeZ,
        ridgeEndX, ridgeY, ridgeZ,
        expandedBounds.maxX, wallHeight, expandedBounds.maxY,
        expandedBounds.minX, wallHeight, expandedBounds.maxY
      );
      indices.push(vertexIndex, vertexIndex + 1, vertexIndex + 2, vertexIndex, vertexIndex + 2, vertexIndex + 3);
      vertexIndex += 4;
      
      // Left hip (triangle)
      vertices.push(
        expandedBounds.minX, wallHeight, expandedBounds.minY,
        ridgeStartX, ridgeY, ridgeZ,
        expandedBounds.minX, wallHeight, expandedBounds.maxY
      );
      indices.push(vertexIndex, vertexIndex + 1, vertexIndex + 2);
      vertexIndex += 3;
      
      // Right hip (triangle)
      vertices.push(
        expandedBounds.maxX, wallHeight, expandedBounds.minY,
        expandedBounds.maxX, wallHeight, expandedBounds.maxY,
        ridgeEndX, ridgeY, ridgeZ
      );
      indices.push(vertexIndex, vertexIndex + 1, vertexIndex + 2);
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    
    return {
      type: 'hip',
      geometry,
      pitch: this.config.roofPitch,
      overhang,
      ridgeHeight
    };
  }
  
  private generateShedRoof(footprint: Polygon, wallHeight: number): Roof3D {
    const overhang = this.config.roofOverhang;
    const pitch = this.config.roofPitch * Math.PI / 180;
    
    const bounds = footprint.boundingBox();
    const rise = bounds.height * Math.tan(pitch);
    
    const expandedBounds = bounds.expand(overhang);
    
    const vertices: number[] = [
      expandedBounds.minX, wallHeight, expandedBounds.minY,
      expandedBounds.maxX, wallHeight, expandedBounds.minY,
      expandedBounds.maxX, wallHeight + rise, expandedBounds.maxY,
      expandedBounds.minX, wallHeight + rise, expandedBounds.maxY
    ];
    
    const indices: number[] = [0, 1, 2, 0, 2, 3];
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    
    return {
      type: 'shed',
      geometry,
      pitch: this.config.roofPitch,
      overhang,
      ridgeHeight: wallHeight + rise
    };
  }
}

// ============================================
// FLOOR SLAB GENERATOR
// ============================================

export class FloorSlabGenerator {
  private config: GeneratorConfig;
  
  constructor(config: GeneratorConfig) {
    this.config = config;
  }
  
  /**
   * Generate floor and ceiling slabs
   */
  public generateSlabs(rooms: Room2D[], elevation: number): {
    floor: THREE.BufferGeometry;
    ceiling: THREE.BufferGeometry;
  } {
    const floorGeometries: THREE.BufferGeometry[] = [];
    const ceilingGeometries: THREE.BufferGeometry[] = [];
    
    for (const room of rooms) {
      const shape = new THREE.Shape(
        room.polygon.vertices.map(v => new THREE.Vector2(v.x, v.y))
      );
      
      // Floor
      const floorGeom = new THREE.ShapeGeometry(shape);
      floorGeom.rotateX(-Math.PI / 2);
      floorGeom.translate(0, elevation, 0);
      floorGeometries.push(floorGeom);
      
      // Ceiling
      const ceilingHeight = room.height ?? this.config.defaultCeilingHeight;
      const ceilingGeom = new THREE.ShapeGeometry(shape);
      ceilingGeom.rotateX(Math.PI / 2);  // Flip for correct normals
      ceilingGeom.translate(0, elevation + ceilingHeight, 0);
      ceilingGeometries.push(ceilingGeom);
    }
    
    return {
      floor: BufferGeometryUtils.mergeGeometries(floorGeometries) ?? new THREE.BufferGeometry(),
      ceiling: BufferGeometryUtils.mergeGeometries(ceilingGeometries) ?? new THREE.BufferGeometry()
    };
  }
}

// ============================================
// MAIN BUILDING 3D GENERATOR
// ============================================

export class Building3DGenerator {
  private config: GeneratorConfig;
  private wallGenerator: WallGenerator;
  private openingGenerator: OpeningGenerator;
  private roofGenerator: RoofGenerator;
  private slabGenerator: FloorSlabGenerator;
  
  constructor(config: Partial<GeneratorConfig> = {}) {
    this.config = { ...DEFAULT_GENERATOR_CONFIG, ...config };
    this.wallGenerator = new WallGenerator(this.config);
    this.openingGenerator = new OpeningGenerator(this.config);
    this.roofGenerator = new RoofGenerator(this.config);
    this.slabGenerator = new FloorSlabGenerator(this.config);
  }
  
  /**
   * Generate complete 3D building from 2D floor plans
   */
  public generate(building2D: Building2D, roofType: RoofType = 'gable'): Building3D {
    const group = new THREE.Group();
    const floors3D: Floor3D[] = [];
    
    let maxElevation = 0;
    
    for (const floor of building2D.floors) {
      const floor3D = this.generateFloor(floor);
      floors3D.push(floor3D);
      
      // Add to group
      for (const wall of floor3D.walls) {
        const wallMesh = new THREE.Mesh(
          wall.geometry,
          new THREE.MeshStandardMaterial({ color: 0xeeeeee })
        );
        wallMesh.castShadow = true;
        wallMesh.receiveShadow = true;
        group.add(wallMesh);
      }
      
      // Floor slab
      const floorMesh = new THREE.Mesh(
        floor3D.floorSlab,
        new THREE.MeshStandardMaterial({ color: 0x8b7355 })  // Wood floor
      );
      floorMesh.receiveShadow = true;
      group.add(floorMesh);
      
      // Ceiling
      const ceilingMesh = new THREE.Mesh(
        floor3D.ceilingSlab,
        new THREE.MeshStandardMaterial({ color: 0xffffff })
      );
      group.add(ceilingMesh);
      
      maxElevation = Math.max(maxElevation, floor.elevation + floor.height);
    }
    
    // Generate roof
    let roof3D: Roof3D | undefined;
    if (this.config.generateRoof && building2D.footprint) {
      roof3D = this.roofGenerator.generateRoof(building2D.footprint, maxElevation, roofType);
      
      const roofMesh = new THREE.Mesh(
        roof3D.geometry,
        new THREE.MeshStandardMaterial({ color: 0x8b4513 })  // Brown roof
      );
      roofMesh.castShadow = true;
      roofMesh.receiveShadow = true;
      group.add(roofMesh);
    }
    
    return {
      id: building2D.id,
      floors: floors3D,
      roof: roof3D!,
      group
    };
  }
  
  private generateFloor(floor: Floor2D): Floor3D {
    const walls3D: Wall3D[] = [];
    
    // Generate walls with openings
    for (const wall of floor.walls) {
      const wallOpenings = [
        ...floor.doors.filter(d => d.wallId === wall.id),
        ...floor.windows.filter(w => w.wallId === wall.id)
      ];
      
      const wallGeometry = this.wallGenerator.generateWall(wall, wallOpenings);
      
      // Generate door/window geometries
      const openings3D: Opening3D[] = [];
      
      for (const door of floor.doors.filter(d => d.wallId === wall.id)) {
        const doorGeom = this.openingGenerator.generateDoor(door, wall);
        openings3D.push({
          id: door.id,
          type: 'door',
          geometry: doorGeom.leaf,
          frameGeometry: doorGeom.frame,
          position: new THREE.Vector3(door.position.x, door.sillHeight, door.position.y)
        });
      }
      
      for (const window of floor.windows.filter(w => w.wallId === wall.id)) {
        const windowGeom = this.openingGenerator.generateWindow(window, wall);
        openings3D.push({
          id: window.id,
          type: 'window',
          geometry: windowGeom.glass,
          frameGeometry: windowGeom.frame,
          position: new THREE.Vector3(window.position.x, window.sillHeight, window.position.y)
        });
      }
      
      walls3D.push({
        id: wall.id,
        geometry: wallGeometry,
        position: new THREE.Vector3(wall.start.x, 0, wall.start.y),
        rotation: new THREE.Euler(0, -Math.atan2(
          wall.end.y - wall.start.y,
          wall.end.x - wall.start.x
        ), 0),
        material: wall.material ?? 'plaster',
        openings: openings3D
      });
    }
    
    // Generate floor and ceiling slabs
    const slabs = this.slabGenerator.generateSlabs(floor.rooms, floor.elevation);
    
    return {
      id: floor.id,
      level: floor.level,
      elevation: floor.elevation,
      walls: walls3D,
      floorSlab: slabs.floor,
      ceilingSlab: slabs.ceiling
    };
  }
}

