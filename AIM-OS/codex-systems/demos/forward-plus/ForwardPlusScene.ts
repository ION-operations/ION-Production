import * as THREE from 'three';
import { ForwardPlusDemo } from '../../rendering/lighting/ForwardPlusDemo';
import { LightData } from '../../rendering/lighting/ForwardPlusLighting';

/**
 * Minimal Forward+ demo scene wiring:
 * - Creates a few spheres and assigns Forward+ material.
 * - Builds tile lists and tile texture.
 */
export function createForwardPlusScene(
  renderer: THREE.WebGLRenderer,
  camera: THREE.PerspectiveCamera,
  scene: THREE.Scene
): void {
  // Geometry
  const geo = new THREE.SphereGeometry(1, 16, 16);
  const meshes: THREE.Mesh[] = [];
  for (let i = 0; i < 8; i++) {
    const m = new THREE.Mesh(geo);
    m.position.set((i - 4) * 2, Math.random() * 2, -5 - i * 1.5);
    scene.add(m);
    meshes.push(m);
  }

  // Lights
  const lights: LightData[] = [];
  for (let i = 0; i < 32; i++) {
    lights.push({
      position: new THREE.Vector3(
        THREE.MathUtils.randFloatSpread(8),
        THREE.MathUtils.randFloatSpread(4) + 2,
        -THREE.MathUtils.randFloat(4, 20)
      ),
      color: new THREE.Color().setHSL(Math.random(), 0.8, 0.6),
      range: THREE.MathUtils.randFloat(4, 8),
      intensity: THREE.MathUtils.randFloat(1, 2),
    });
  }

  const demo = new ForwardPlusDemo(renderer, camera);
  demo.setLights(lights);
  demo.build();
  const { material } = demo.buildMaterial();

  meshes.forEach(m => (m.material = material));
}

