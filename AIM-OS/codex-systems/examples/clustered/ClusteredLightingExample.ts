import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { createClusteredLightingScene } from '../../demos/clustered/ClusteredLightingScene';
import { ClusteredLightingDemo } from '../../rendering/lighting/ClusteredLightingDemo';
import { ClusteredLight } from '../../rendering/lighting/ClusteredLighting';
import { buildClusterTexture } from '../../rendering/lighting/ClusteredTileBuilder';
import { createClusteredMaterial } from '../../rendering/lighting/ClusteredLightingShader';

/**
 * Full Three.js example for Clustered Lighting.
 */
export async function initClusteredLightingExample(canvas: HTMLCanvasElement) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x080810);

  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 2, 8);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1, -5);

  // Build scene geometry and lights
  createClusteredLightingScene(camera, scene);

  // Collect lights (or create random)
  const lights: ClusteredLight[] = [];
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

  // Build clustered data and material
  const demo = new ClusteredLightingDemo(camera);
  demo.setLights(lights);
  const clusterData = demo.build();
  const clusterTex = buildClusterTexture(
    clusterData.clusters,
    clusterData.slicesX,
    clusterData.slicesY,
    clusterData.slicesZ,
    64,
    lights.length
  );

  const lp = new Float32Array(lights.length * 3);
  const lc = new Float32Array(lights.length * 3);
  const lr = new Float32Array(lights.length);
  const li = new Float32Array(lights.length);
  for (let i = 0; i < lights.length; i++) {
    lp[i * 3 + 0] = lights[i].position.x;
    lp[i * 3 + 1] = lights[i].position.y;
    lp[i * 3 + 2] = lights[i].position.z;
    lc[i * 3 + 0] = lights[i].color.r;
    lc[i * 3 + 1] = lights[i].color.g;
    lc[i * 3 + 2] = lights[i].color.b;
    lr[i] = lights[i].range;
    li[i] = lights[i].intensity;
  }

  const material = createClusteredMaterial({
    clustersX: clusterData.slicesX,
    clustersY: clusterData.slicesY,
    clustersZ: clusterData.slicesZ,
    maxLightsPerCluster: 64,
    clusterTexture: clusterTex,
    maxLights: lights.length,
    lightPositions: lp,
    lightColors: lc,
    lightRanges: lr,
    lightIntensity: li,
  });

  scene.traverse(obj => {
    if ((obj as THREE.Mesh).isMesh) {
      (obj as THREE.Mesh).material = material;
    }
  });

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

