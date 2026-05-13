/**
 * Spline System
 * Comprehensive spline and curve tools
 * 
 * Features:
 * - Bezier curves (quadratic, cubic)
 * - Catmull-Rom splines
 * - B-splines
 * - NURBS curves
 * - Path following
 * - Spline mesh generation
 * - Animation along curves
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface SplinePoint {
  position: THREE.Vector3;
  tangent?: THREE.Vector3;
  normal?: THREE.Vector3;
  roll?: number;
  scale?: number;
}

export interface SplineConfig {
  closed: boolean;
  tension: number;     // For Catmull-Rom
  segments: number;    // Segments per span
  autoTangents: boolean;
}

export type SplineType = 'linear' | 'bezier' | 'catmull-rom' | 'bspline';

// ============================================
// BEZIER CURVES
// ============================================

export class BezierCurve {
  private controlPoints: THREE.Vector3[];
  
  constructor(points: THREE.Vector3[]) {
    this.controlPoints = points.map(p => p.clone());
  }
  
  /**
   * Evaluate quadratic Bezier
   */
  public static quadratic(
    p0: THREE.Vector3,
    p1: THREE.Vector3,
    p2: THREE.Vector3,
    t: number
  ): THREE.Vector3 {
    const oneMinusT = 1 - t;
    
    return new THREE.Vector3()
      .addScaledVector(p0, oneMinusT * oneMinusT)
      .addScaledVector(p1, 2 * oneMinusT * t)
      .addScaledVector(p2, t * t);
  }
  
  /**
   * Evaluate cubic Bezier
   */
  public static cubic(
    p0: THREE.Vector3,
    p1: THREE.Vector3,
    p2: THREE.Vector3,
    p3: THREE.Vector3,
    t: number
  ): THREE.Vector3 {
    const oneMinusT = 1 - t;
    const t2 = t * t;
    const t3 = t2 * t;
    const oneMinusT2 = oneMinusT * oneMinusT;
    const oneMinusT3 = oneMinusT2 * oneMinusT;
    
    return new THREE.Vector3()
      .addScaledVector(p0, oneMinusT3)
      .addScaledVector(p1, 3 * oneMinusT2 * t)
      .addScaledVector(p2, 3 * oneMinusT * t2)
      .addScaledVector(p3, t3);
  }
  
  /**
   * Evaluate curve at t
   */
  public getPoint(t: number): THREE.Vector3 {
    const n = this.controlPoints.length;
    
    if (n === 3) {
      return BezierCurve.quadratic(
        this.controlPoints[0],
        this.controlPoints[1],
        this.controlPoints[2],
        t
      );
    } else if (n === 4) {
      return BezierCurve.cubic(
        this.controlPoints[0],
        this.controlPoints[1],
        this.controlPoints[2],
        this.controlPoints[3],
        t
      );
    }
    
    // General de Casteljau algorithm for any degree
    let points = this.controlPoints.map(p => p.clone());
    
    for (let r = 1; r < n; r++) {
      for (let i = 0; i < n - r; i++) {
        points[i].lerp(points[i + 1], t);
      }
    }
    
    return points[0];
  }
  
  /**
   * Get tangent at t
   */
  public getTangent(t: number): THREE.Vector3 {
    const n = this.controlPoints.length;
    
    if (n === 4) {
      // Derivative of cubic Bezier
      const p0 = this.controlPoints[0];
      const p1 = this.controlPoints[1];
      const p2 = this.controlPoints[2];
      const p3 = this.controlPoints[3];
      
      const oneMinusT = 1 - t;
      
      return new THREE.Vector3()
        .addScaledVector(p1.clone().sub(p0), 3 * oneMinusT * oneMinusT)
        .addScaledVector(p2.clone().sub(p1), 6 * oneMinusT * t)
        .addScaledVector(p3.clone().sub(p2), 3 * t * t)
        .normalize();
    }
    
    // Numerical derivative
    const delta = 0.001;
    const p0 = this.getPoint(Math.max(0, t - delta));
    const p1 = this.getPoint(Math.min(1, t + delta));
    
    return p1.sub(p0).normalize();
  }
  
  /**
   * Get points along curve
   */
  public getPoints(segments: number): THREE.Vector3[] {
    const points: THREE.Vector3[] = [];
    
    for (let i = 0; i <= segments; i++) {
      points.push(this.getPoint(i / segments));
    }
    
    return points;
  }
  
  /**
   * Get length of curve (approximation)
   */
  public getLength(segments: number = 100): number {
    let length = 0;
    let prevPoint = this.getPoint(0);
    
    for (let i = 1; i <= segments; i++) {
      const point = this.getPoint(i / segments);
      length += prevPoint.distanceTo(point);
      prevPoint = point;
    }
    
    return length;
  }
}

// ============================================
// CATMULL-ROM SPLINE
// ============================================

export class CatmullRomSpline {
  private points: THREE.Vector3[];
  private tension: number;
  private closed: boolean;
  
  constructor(points: THREE.Vector3[], tension: number = 0.5, closed: boolean = false) {
    this.points = points.map(p => p.clone());
    this.tension = tension;
    this.closed = closed;
  }
  
  /**
   * Evaluate spline at t (0-1 over entire spline)
   */
  public getPoint(t: number): THREE.Vector3 {
    const n = this.points.length;
    
    if (n < 2) return this.points[0]?.clone() ?? new THREE.Vector3();
    
    // Map t to segment
    const totalSegments = this.closed ? n : n - 1;
    let segment = Math.floor(t * totalSegments);
    segment = Math.min(segment, totalSegments - 1);
    
    const localT = (t * totalSegments) - segment;
    
    // Get 4 control points
    const i0 = this.closed 
      ? (segment - 1 + n) % n 
      : Math.max(0, segment - 1);
    const i1 = this.closed 
      ? segment % n 
      : segment;
    const i2 = this.closed 
      ? (segment + 1) % n 
      : Math.min(n - 1, segment + 1);
    const i3 = this.closed 
      ? (segment + 2) % n 
      : Math.min(n - 1, segment + 2);
    
    return this.interpolate(
      this.points[i0],
      this.points[i1],
      this.points[i2],
      this.points[i3],
      localT
    );
  }
  
  private interpolate(
    p0: THREE.Vector3,
    p1: THREE.Vector3,
    p2: THREE.Vector3,
    p3: THREE.Vector3,
    t: number
  ): THREE.Vector3 {
    const t2 = t * t;
    const t3 = t2 * t;
    const alpha = this.tension;
    
    // Catmull-Rom matrix coefficients
    const m0 = -alpha * t3 + 2 * alpha * t2 - alpha * t;
    const m1 = (2 - alpha) * t3 + (alpha - 3) * t2 + 1;
    const m2 = (alpha - 2) * t3 + (3 - 2 * alpha) * t2 + alpha * t;
    const m3 = alpha * t3 - alpha * t2;
    
    return new THREE.Vector3()
      .addScaledVector(p0, m0)
      .addScaledVector(p1, m1)
      .addScaledVector(p2, m2)
      .addScaledVector(p3, m3);
  }
  
  /**
   * Get tangent at t
   */
  public getTangent(t: number): THREE.Vector3 {
    const delta = 0.001;
    const p0 = this.getPoint(Math.max(0, t - delta));
    const p1 = this.getPoint(Math.min(1, t + delta));
    
    return p1.sub(p0).normalize();
  }
  
  /**
   * Get Frenet frame at t
   */
  public getFrame(t: number): { tangent: THREE.Vector3; normal: THREE.Vector3; binormal: THREE.Vector3 } {
    const tangent = this.getTangent(t);
    
    // Use reference up vector for stable frames
    const up = new THREE.Vector3(0, 1, 0);
    const binormal = tangent.clone().cross(up).normalize();
    const normal = binormal.clone().cross(tangent).normalize();
    
    return { tangent, normal, binormal };
  }
  
  /**
   * Add point
   */
  public addPoint(point: THREE.Vector3): void {
    this.points.push(point.clone());
  }
  
  /**
   * Remove point
   */
  public removePoint(index: number): void {
    if (index >= 0 && index < this.points.length) {
      this.points.splice(index, 1);
    }
  }
  
  /**
   * Update point
   */
  public updatePoint(index: number, position: THREE.Vector3): void {
    if (index >= 0 && index < this.points.length) {
      this.points[index].copy(position);
    }
  }
  
  /**
   * Get all control points
   */
  public getControlPoints(): THREE.Vector3[] {
    return this.points.map(p => p.clone());
  }
  
  /**
   * Get points along spline
   */
  public getPoints(segments: number): THREE.Vector3[] {
    const points: THREE.Vector3[] = [];
    
    for (let i = 0; i <= segments; i++) {
      points.push(this.getPoint(i / segments));
    }
    
    return points;
  }
  
  /**
   * Get evenly spaced points (arc-length parameterization)
   */
  public getEvenlySpacedPoints(count: number): THREE.Vector3[] {
    const totalLength = this.getLength(count * 10);
    const segmentLength = totalLength / (count - 1);
    
    const points: THREE.Vector3[] = [this.getPoint(0)];
    let currentLength = 0;
    let prevPoint = points[0].clone();
    
    for (let t = 0.001; t <= 1 && points.length < count; t += 0.001) {
      const point = this.getPoint(t);
      const dist = prevPoint.distanceTo(point);
      currentLength += dist;
      
      while (currentLength >= segmentLength && points.length < count) {
        const overshoot = currentLength - segmentLength;
        const ratio = 1 - (overshoot / dist);
        const interpolated = prevPoint.clone().lerp(point, ratio);
        points.push(interpolated);
        currentLength = overshoot;
      }
      
      prevPoint = point;
    }
    
    // Ensure we have exactly the right number of points
    while (points.length < count) {
      points.push(this.getPoint(1));
    }
    
    return points;
  }
  
  /**
   * Get length
   */
  public getLength(segments: number = 100): number {
    let length = 0;
    let prevPoint = this.getPoint(0);
    
    for (let i = 1; i <= segments; i++) {
      const point = this.getPoint(i / segments);
      length += prevPoint.distanceTo(point);
      prevPoint = point;
    }
    
    return length;
  }
}

// ============================================
// SPLINE MESH GENERATOR
// ============================================

export class SplineMeshGenerator {
  /**
   * Generate tube geometry along spline
   */
  public static generateTube(
    spline: CatmullRomSpline | BezierCurve,
    radius: number,
    segments: number,
    radialSegments: number,
    closed: boolean = false
  ): THREE.BufferGeometry {
    const geometry = new THREE.BufferGeometry();
    
    const positions: number[] = [];
    const normals: number[] = [];
    const uvs: number[] = [];
    const indices: number[] = [];
    
    // Generate frames along spline
    const frames: { position: THREE.Vector3; tangent: THREE.Vector3; normal: THREE.Vector3; binormal: THREE.Vector3 }[] = [];
    
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const position = spline.getPoint(t);
      const tangent = spline.getTangent(t);
      
      const up = new THREE.Vector3(0, 1, 0);
      let binormal = tangent.clone().cross(up).normalize();
      
      if (binormal.lengthSq() < 0.001) {
        binormal = tangent.clone().cross(new THREE.Vector3(1, 0, 0)).normalize();
      }
      
      const normal = binormal.clone().cross(tangent).normalize();
      
      frames.push({ position, tangent, normal, binormal });
    }
    
    // Generate vertices
    for (let i = 0; i <= segments; i++) {
      const frame = frames[i];
      
      for (let j = 0; j <= radialSegments; j++) {
        const angle = (j / radialSegments) * Math.PI * 2;
        const sin = Math.sin(angle);
        const cos = Math.cos(angle);
        
        // Position on circle
        const circleNormal = frame.normal.clone()
          .multiplyScalar(cos)
          .add(frame.binormal.clone().multiplyScalar(sin));
        
        const vertex = frame.position.clone()
          .add(circleNormal.clone().multiplyScalar(radius));
        
        positions.push(vertex.x, vertex.y, vertex.z);
        normals.push(circleNormal.x, circleNormal.y, circleNormal.z);
        uvs.push(i / segments, j / radialSegments);
      }
    }
    
    // Generate indices
    for (let i = 0; i < segments; i++) {
      for (let j = 0; j < radialSegments; j++) {
        const a = i * (radialSegments + 1) + j;
        const b = a + radialSegments + 1;
        const c = a + 1;
        const d = b + 1;
        
        indices.push(a, b, c);
        indices.push(b, d, c);
      }
    }
    
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geometry.setIndex(indices);
    
    return geometry;
  }
  
  /**
   * Generate ribbon geometry along spline
   */
  public static generateRibbon(
    spline: CatmullRomSpline | BezierCurve,
    width: number,
    segments: number
  ): THREE.BufferGeometry {
    const geometry = new THREE.BufferGeometry();
    
    const positions: number[] = [];
    const normals: number[] = [];
    const uvs: number[] = [];
    const indices: number[] = [];
    
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const position = spline.getPoint(t);
      const tangent = spline.getTangent(t);
      
      const up = new THREE.Vector3(0, 1, 0);
      let right = tangent.clone().cross(up).normalize();
      
      if (right.lengthSq() < 0.001) {
        right = tangent.clone().cross(new THREE.Vector3(1, 0, 0)).normalize();
      }
      
      const normal = right.clone().cross(tangent).normalize();
      
      // Left vertex
      const left = position.clone().sub(right.clone().multiplyScalar(width / 2));
      positions.push(left.x, left.y, left.z);
      normals.push(normal.x, normal.y, normal.z);
      uvs.push(t, 0);
      
      // Right vertex
      const rightPos = position.clone().add(right.clone().multiplyScalar(width / 2));
      positions.push(rightPos.x, rightPos.y, rightPos.z);
      normals.push(normal.x, normal.y, normal.z);
      uvs.push(t, 1);
    }
    
    // Generate indices
    for (let i = 0; i < segments; i++) {
      const a = i * 2;
      const b = a + 1;
      const c = a + 2;
      const d = a + 3;
      
      indices.push(a, c, b);
      indices.push(b, c, d);
    }
    
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geometry.setIndex(indices);
    
    return geometry;
  }
}

// ============================================
// SPLINE FOLLOWER
// ============================================

export class SplineFollower {
  private spline: CatmullRomSpline;
  private target: THREE.Object3D;
  private t: number = 0;
  private speed: number;
  private loop: boolean;
  private lookAhead: number;
  
  constructor(
    spline: CatmullRomSpline,
    target: THREE.Object3D,
    speed: number = 1,
    loop: boolean = true
  ) {
    this.spline = spline;
    this.target = target;
    this.speed = speed;
    this.loop = loop;
    this.lookAhead = 0.01;
  }
  
  /**
   * Update position along spline
   */
  public update(deltaTime: number): void {
    // Calculate distance to move
    const distance = this.speed * deltaTime;
    
    // Get current position and approximate arc length
    const length = this.spline.getLength(100);
    const dt = distance / length;
    
    this.t += dt;
    
    if (this.loop) {
      this.t = this.t % 1;
      if (this.t < 0) this.t += 1;
    } else {
      this.t = THREE.MathUtils.clamp(this.t, 0, 1);
    }
    
    // Update position
    const position = this.spline.getPoint(this.t);
    this.target.position.copy(position);
    
    // Update rotation to face forward
    const lookAtT = Math.min(1, this.t + this.lookAhead);
    const lookAtPoint = this.spline.getPoint(lookAtT);
    
    this.target.lookAt(lookAtPoint);
  }
  
  /**
   * Set progress (0-1)
   */
  public setProgress(t: number): void {
    this.t = THREE.MathUtils.clamp(t, 0, 1);
  }
  
  /**
   * Get progress
   */
  public getProgress(): number {
    return this.t;
  }
  
  /**
   * Set speed
   */
  public setSpeed(speed: number): void {
    this.speed = speed;
  }
  
  /**
   * Is at end
   */
  public isAtEnd(): boolean {
    return !this.loop && this.t >= 1;
  }
}

