/**
 * Orthogonal View Generator Service
 * 
 * Generates orthogonal reference views (front, back, left, right, top, bottom)
 * from 3D objects for use as reference images in AI texture generation
 */

import * as THREE from 'three';

export interface OrthogonalViews {
  front: ImageData;
  back: ImageData;
  left: ImageData;
  right: ImageData;
  top: ImageData;
  bottom: ImageData;
}

export interface ImageData {
  url: string;
  dataUrl: string;
  width: number;
  height: number;
}

export interface ObjectBounds {
  min: THREE.Vector3;
  max: THREE.Vector3;
  center: THREE.Vector3;
  size: THREE.Vector3;
}

export class OrthogonalViewGenerator {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.OrthographicCamera;
  private resolution: number = 2048;

  constructor(renderer?: THREE.WebGLRenderer) {
    // Create renderer if not provided
    this.renderer = renderer || new THREE.WebGLRenderer({
      antialias: true,
      preserveDrawingBuffer: true,
      alpha: true
    });
    this.renderer.setSize(this.resolution, this.resolution);
    this.renderer.setPixelRatio(1);

    // Create scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xffffff);

    // Create orthographic camera
    const aspect = 1;
    const size = 10;
    this.camera = new THREE.OrthographicCamera(
      -size * aspect,
      size * aspect,
      size,
      -size,
      0.1,
      1000
    );
  }

  /**
   * Generate all 6 orthogonal views for an object
   */
  async generateViews(
    object: THREE.Object3D,
    options?: {
      resolution?: number;
      includeGrid?: boolean;
      includeAxes?: boolean;
      backgroundColor?: number;
    }
  ): Promise<OrthogonalViews> {
    const resolution = options?.resolution || this.resolution;
    this.renderer.setSize(resolution, resolution);

    // Calculate object bounds
    const bounds = this.calculateBounds(object);

    // Set up lighting
    this.setupLighting();

    // Add grid and axes if requested
    if (options?.includeGrid) {
      this.addGrid(bounds);
    }
    if (options?.includeAxes) {
      this.addAxes(bounds);
    }

    // Set background color
    if (options?.backgroundColor !== undefined) {
      this.scene.background = new THREE.Color(options.backgroundColor);
    }

    // Generate each view
    const views: Partial<OrthogonalViews> = {};

    // Front view (looking along -Z axis)
    views.front = await this.renderView(object, bounds, {
      position: new THREE.Vector3(bounds.center.x, bounds.center.y, bounds.max.z + bounds.size.z),
      target: bounds.center,
      up: new THREE.Vector3(0, 1, 0)
    }, resolution);

    // Back view (looking along +Z axis)
    views.back = await this.renderView(object, bounds, {
      position: new THREE.Vector3(bounds.center.x, bounds.center.y, bounds.min.z - bounds.size.z),
      target: bounds.center,
      up: new THREE.Vector3(0, 1, 0)
    }, resolution);

    // Left view (looking along +X axis)
    views.left = await this.renderView(object, bounds, {
      position: new THREE.Vector3(bounds.min.x - bounds.size.x, bounds.center.y, bounds.center.z),
      target: bounds.center,
      up: new THREE.Vector3(0, 1, 0)
    }, resolution);

    // Right view (looking along -X axis)
    views.right = await this.renderView(object, bounds, {
      position: new THREE.Vector3(bounds.max.x + bounds.size.x, bounds.center.y, bounds.center.z),
      target: bounds.center,
      up: new THREE.Vector3(0, 1, 0)
    }, resolution);

    // Top view (looking along -Y axis)
    views.top = await this.renderView(object, bounds, {
      position: new THREE.Vector3(bounds.center.x, bounds.max.y + bounds.size.y, bounds.center.z),
      target: bounds.center,
      up: new THREE.Vector3(0, 0, -1)
    }, resolution);

    // Bottom view (looking along +Y axis)
    views.bottom = await this.renderView(object, bounds, {
      position: new THREE.Vector3(bounds.center.x, bounds.min.y - bounds.size.y, bounds.center.z),
      target: bounds.center,
      up: new THREE.Vector3(0, 0, 1)
    }, resolution);

    // Clean up
    this.scene.clear();

    return views as OrthogonalViews;
  }

  /**
   * Render a single view
   */
  private async renderView(
    object: THREE.Object3D,
    bounds: ObjectBounds,
    cameraSetup: {
      position: THREE.Vector3;
      target: THREE.Vector3;
      up: THREE.Vector3;
    },
    resolution: number
  ): Promise<ImageData> {
    // Clone object for rendering (to avoid modifying original)
    const clonedObject = object.clone();
    this.scene.add(clonedObject);

    // Set up camera
    this.camera.position.copy(cameraSetup.position);
    this.camera.lookAt(cameraSetup.target);
    this.camera.up.copy(cameraSetup.up);

    // Fit camera to bounds
    this.fitCameraToBounds(bounds);

    // Render
    this.renderer.render(this.scene, this.camera);

    // Get image data
    const dataUrl = this.renderer.domElement.toDataURL('image/png');

    // Remove cloned object
    this.scene.remove(clonedObject);

    // Create blob URL
    const blob = await this.dataURLToBlob(dataUrl);
    const url = URL.createObjectURL(blob);

    return {
      url,
      dataUrl,
      width: resolution,
      height: resolution
    };
  }

  /**
   * Calculate object bounds
   */
  private calculateBounds(object: THREE.Object3D): ObjectBounds {
    const box = new THREE.Box3().setFromObject(object);
    const min = box.min.clone();
    const max = box.max.clone();
    const center = new THREE.Vector3().addVectors(min, max).multiplyScalar(0.5);
    const size = new THREE.Vector3().subVectors(max, min);

    // Add padding
    const padding = size.length() * 0.2;
    min.subScalar(padding);
    max.addScalar(padding);
    size.addScalar(padding * 2);

    return { min, max, center, size };
  }

  /**
   * Fit camera to bounds
   */
  private fitCameraToBounds(bounds: ObjectBounds): void {
    const size = bounds.size;
    const maxDim = Math.max(size.x, size.y, size.z);
    const aspect = 1;

    this.camera.left = -maxDim * aspect;
    this.camera.right = maxDim * aspect;
    this.camera.top = maxDim;
    this.camera.bottom = -maxDim;
    this.camera.near = 0.1;
    this.camera.far = maxDim * 10;
    this.camera.updateProjectionMatrix();
  }

  /**
   * Set up lighting for rendering
   */
  private setupLighting(): void {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    // Main directional light
    const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
    mainLight.position.set(5, 10, 5);
    this.scene.add(mainLight);

    // Fill light
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-5, 5, -5);
    this.scene.add(fillLight);
  }

  /**
   * Add grid helper
   */
  private addGrid(bounds: ObjectBounds): void {
    const gridHelper = new THREE.GridHelper(
      Math.max(bounds.size.x, bounds.size.z) * 2,
      10,
      0x888888,
      0xcccccc
    );
    this.scene.add(gridHelper);
  }

  /**
   * Add axes helper
   */
  private addAxes(bounds: ObjectBounds): void {
    const axesHelper = new THREE.AxesHelper(
      Math.max(bounds.size.x, bounds.size.y, bounds.size.z)
    );
    this.scene.add(axesHelper);
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
    this.renderer.dispose();
    this.scene.clear();
  }
}

export default OrthogonalViewGenerator;

