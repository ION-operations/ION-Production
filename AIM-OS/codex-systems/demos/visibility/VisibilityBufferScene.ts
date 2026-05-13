import * as THREE from 'three';
import { VisibilityBufferDemo } from '../../rendering/visibility/VisibilityBufferDemo';
import { MaterialTableEntry } from '../../rendering/visibility/VisibilityBufferShading';

/**
 * Minimal Visibility Buffer demo:
 * - Renders simple meshes into visibility buffer and shades with material table.
 */
export function createVisibilityBufferScene(
  renderer: THREE.WebGLRenderer,
  camera: THREE.Camera,
  scene: THREE.Scene,
  width: number,
  height: number
): VisibilityBufferDemo {
  // Assign materialId userData
  const geo = new THREE.BoxGeometry(1, 1, 1);
  for (let i = 0; i < 6; i++) {
    const m = new THREE.Mesh(geo);
    m.position.set((i - 3) * 1.5, Math.random() * 2, -5 - i);
    m.userData.materialId = i + 1;
    scene.add(m);
  }

  const vb = new VisibilityBufferDemo(renderer, scene, camera, width, height);

  // Material table entries (0..255)
  const entries: Record<number, MaterialTableEntry> = {
    1: { baseColor: new THREE.Color(0xff5555), metallic: 0.1, roughness: 0.6, emissive: new THREE.Color(0) },
    2: { baseColor: new THREE.Color(0x55ff55), metallic: 0.3, roughness: 0.4, emissive: new THREE.Color(0) },
    3: { baseColor: new THREE.Color(0x5555ff), metallic: 0.6, roughness: 0.2, emissive: new THREE.Color(0) },
    4: { baseColor: new THREE.Color(0xffff55), metallic: 0.1, roughness: 0.7, emissive: new THREE.Color(0) },
    5: { baseColor: new THREE.Color(0xff55ff), metallic: 0.4, roughness: 0.5, emissive: new THREE.Color(0) },
    6: { baseColor: new THREE.Color(0x55ffff), metallic: 0.2, roughness: 0.8, emissive: new THREE.Color(0) },
  };
  vb.setMaterialTable(entries);

  return vb;
}

