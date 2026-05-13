/**
 * UV Map Extractor Service
 * 
 * Extracts and visualizes UV maps from 3D objects for texture reference
 */

import * as THREE from 'three';

export interface UVMapData {
  layout: ImageData;
  wireframe: ImageData;
  coordinates: UVCoordinates;
  resolution: [number, number];
  texelDensity: number;
  seams: UVSeam[];
}

export interface ImageData {
  url: string;
  dataUrl: string;
  width: number;
  height: number;
}

export interface UVCoordinates {
  vertices: UVVertex[];
  faces: UVFace[];
}

export interface UVVertex {
  index: number;
  uv: [number, number];
  position: [number, number, number];
}

export interface UVFace {
  indices: [number, number, number];
  uvIndices: [number, number, number];
}

export interface UVSeam {
  id: string;
  vertices: number[];
  polyline: [number, number][];
}

export class UVMapExtractor {
  private resolution: number = 2048;
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;

  constructor(resolution: number = 2048) {
    this.resolution = resolution;
    this.canvas = document.createElement('canvas');
    this.canvas.width = resolution;
    this.canvas.height = resolution;
    const ctx = this.canvas.getContext('2d');
    if (!ctx) {
      throw new Error('Failed to create canvas context');
    }
    this.ctx = ctx;
  }

  /**
   * Extract UV map from geometry
   */
  async extractUVMap(geometry: THREE.BufferGeometry): Promise<UVMapData> {
    // Extract UV coordinates
    const coordinates = this.extractUVCoordinates(geometry);

    // Generate UV layout visualization
    const layout = await this.generateUVLayout(coordinates);

    // Generate UV wireframe
    const wireframe = await this.generateUVWireframe(coordinates);

    // Detect seams
    const seams = this.detectSeams(coordinates);

    // Calculate texel density
    const texelDensity = this.calculateTexelDensity(coordinates, geometry);

    return {
      layout,
      wireframe,
      coordinates,
      resolution: [this.resolution, this.resolution],
      texelDensity,
      seams
    };
  }

  /**
   * Extract UV coordinates from geometry
   */
  private extractUVCoordinates(geometry: THREE.BufferGeometry): UVCoordinates {
    const positions = geometry.attributes.position;
    const uvs = geometry.attributes.uv;
    const index = geometry.index;

    if (!positions || !uvs) {
      throw new Error('Geometry must have position and UV attributes');
    }

    const vertices: UVVertex[] = [];
    const faces: UVFace[] = [];

    // Extract vertices
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const y = positions.getY(i);
      const z = positions.getZ(i);
      const u = uvs.getX(i);
      const v = uvs.getY(i);

      vertices.push({
        index: i,
        uv: [u, v],
        position: [x, y, z]
      });
    }

    // Extract faces
    if (index) {
      for (let i = 0; i < index.count; i += 3) {
        const i0 = index.getX(i);
        const i1 = index.getX(i + 1);
        const i2 = index.getX(i + 2);

        faces.push({
          indices: [i0, i1, i2],
          uvIndices: [i0, i1, i2] // Assuming 1:1 mapping
        });
      }
    } else {
      // No index, assume triangles
      for (let i = 0; i < positions.count; i += 3) {
        faces.push({
          indices: [i, i + 1, i + 2],
          uvIndices: [i, i + 1, i + 2]
        });
      }
    }

    return { vertices, faces };
  }

  /**
   * Generate UV layout visualization
   */
  private async generateUVLayout(coordinates: UVCoordinates): Promise<ImageData> {
    // Clear canvas
    this.ctx.fillStyle = '#ffffff';
    this.ctx.fillRect(0, 0, this.resolution, this.resolution);

    // Draw UV space border
    this.ctx.strokeStyle = '#000000';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(0, 0, this.resolution, this.resolution);

    // Draw faces
    this.ctx.fillStyle = '#f0f0f0';
    this.ctx.strokeStyle = '#333333';
    this.ctx.lineWidth = 1;

    for (const face of coordinates.faces) {
      const v0 = coordinates.vertices[face.uvIndices[0]];
      const v1 = coordinates.vertices[face.uvIndices[1]];
      const v2 = coordinates.vertices[face.uvIndices[2]];

      // Convert UV to pixel coordinates
      const x0 = v0.uv[0] * this.resolution;
      const y0 = (1 - v0.uv[1]) * this.resolution; // Flip Y
      const x1 = v1.uv[0] * this.resolution;
      const y1 = (1 - v1.uv[1]) * this.resolution;
      const x2 = v2.uv[0] * this.resolution;
      const y2 = (1 - v2.uv[1]) * this.resolution;

      // Draw triangle
      this.ctx.beginPath();
      this.ctx.moveTo(x0, y0);
      this.ctx.lineTo(x1, y1);
      this.ctx.lineTo(x2, y2);
      this.ctx.closePath();
      this.ctx.fill();
      this.ctx.stroke();
    }

    // Convert to image
    const dataUrl = this.canvas.toDataURL('image/png');
    const blob = await this.dataURLToBlob(dataUrl);
    const url = URL.createObjectURL(blob);

    return {
      url,
      dataUrl,
      width: this.resolution,
      height: this.resolution
    };
  }

  /**
   * Generate UV wireframe visualization
   */
  private async generateUVWireframe(coordinates: UVCoordinates): Promise<ImageData> {
    // Clear canvas
    this.ctx.fillStyle = '#ffffff';
    this.ctx.fillRect(0, 0, this.resolution, this.resolution);

    // Draw wireframe
    this.ctx.strokeStyle = '#0066ff';
    this.ctx.lineWidth = 2;

    for (const face of coordinates.faces) {
      const v0 = coordinates.vertices[face.uvIndices[0]];
      const v1 = coordinates.vertices[face.uvIndices[1]];
      const v2 = coordinates.vertices[face.uvIndices[2]];

      // Convert UV to pixel coordinates
      const x0 = v0.uv[0] * this.resolution;
      const y0 = (1 - v0.uv[1]) * this.resolution;
      const x1 = v1.uv[0] * this.resolution;
      const y1 = (1 - v1.uv[1]) * this.resolution;
      const x2 = v2.uv[0] * this.resolution;
      const y2 = (1 - v2.uv[1]) * this.resolution;

      // Draw triangle edges
      this.ctx.beginPath();
      this.ctx.moveTo(x0, y0);
      this.ctx.lineTo(x1, y1);
      this.ctx.lineTo(x2, y2);
      this.ctx.closePath();
      this.ctx.stroke();
    }

    // Convert to image
    const dataUrl = this.canvas.toDataURL('image/png');
    const blob = await this.dataURLToBlob(dataUrl);
    const url = URL.createObjectURL(blob);

    return {
      url,
      dataUrl,
      width: this.resolution,
      height: this.resolution
    };
  }

  /**
   * Detect UV seams (edges that are split in UV space)
   */
  private detectSeams(coordinates: UVCoordinates): UVSeam[] {
    // This is a simplified seam detection
    // In a full implementation, you would compare 3D edges with UV edges
    // to find where they don't match (indicating a seam)

    const seams: UVSeam[] = [];
    // TODO: Implement proper seam detection algorithm
    return seams;
  }

  /**
   * Calculate texel density (pixels per unit in 3D space)
   */
  private calculateTexelDensity(
    coordinates: UVCoordinates,
    geometry: THREE.BufferGeometry
  ): number {
    // Calculate average texel density across all faces
    let totalDensity = 0;
    let faceCount = 0;

    for (const face of coordinates.faces) {
      const v0 = coordinates.vertices[face.uvIndices[0]];
      const v1 = coordinates.vertices[face.uvIndices[1]];
      const v2 = coordinates.vertices[face.uvIndices[2]];

      // Calculate 3D face area
      const p0 = new THREE.Vector3(...v0.position);
      const p1 = new THREE.Vector3(...v1.position);
      const p2 = new THREE.Vector3(...v2.position);
      const edge1 = p1.clone().sub(p0);
      const edge2 = p2.clone().sub(p0);
      const area3D = edge1.cross(edge2).length() / 2;

      // Calculate UV face area
      const uv0 = new THREE.Vector2(...v0.uv);
      const uv1 = new THREE.Vector2(...v1.uv);
      const uv2 = new THREE.Vector2(...v2.uv);
      const uvEdge1 = uv1.clone().sub(uv0);
      const uvEdge2 = uv2.clone().sub(uv0);
      const areaUV = Math.abs(uvEdge1.cross(uvEdge2)) / 2;

      // Calculate density (pixels per unit)
      if (areaUV > 0) {
        const density = (areaUV * this.resolution * this.resolution) / area3D;
        totalDensity += density;
        faceCount++;
      }
    }

    return faceCount > 0 ? totalDensity / faceCount : 0;
  }

  /**
   * Convert data URL to blob
   */
  private async dataURLToBlob(dataUrl: string): Promise<Blob> {
    const response = await fetch(dataUrl);
    return await response.blob();
  }

  /**
   * Clean up resources
   */
  dispose(): void {
    // Canvas cleanup if needed
  }
}

export default UVMapExtractor;

