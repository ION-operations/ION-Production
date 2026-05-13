import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { ForwardPlusDemo } from '../../rendering/lighting/ForwardPlusDemo';
import { LightData } from '../../rendering/lighting/ForwardPlusLighting';
import { createForwardPlusScene } from '../../demos/forward-plus/ForwardPlusScene';

/**
 * Full Three.js example for Forward+ lighting.
 * Usage: call initForwardPlusExample(canvas) to bootstrap.
 */
export async function initForwardPlusExample(canvas: HTMLCanvasElement) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x101018);

  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 2, 8);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1, -5);

  // Build scene geometry and lights
  createForwardPlusScene(renderer, camera, scene);

  // Extract lights from scene (or rebuild)
  const lights: LightData[] = [];
  scene.traverse(obj => {
    if ((obj as any).isPointLight) {
      const l = obj as THREE.PointLight;
      lights.push({
        position: l.position.clone(),
        color: l.color.clone(),
        range: l.distance || 8,
        intensity: l.intensity,
      });
    }
  });

  // If scene didn't add lights, create random lights
  if (lights.length === 0) {
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
  }

  // Build Forward+ material and assign to meshes
  const demo = new ForwardPlusDemo(renderer, camera);
  demo.setLights(lights);
  demo.build();
  const { material } = demo.buildMaterial();
  scene.traverse(obj => {
    if ((obj as THREE.Mesh).isMesh) {
      (obj as THREE.Mesh).material = material;
    }
  });

  // Resize handling
  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();
}

