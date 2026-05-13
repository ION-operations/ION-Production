import * as THREE from 'three';
import { ClusteredLightingDemo } from '../../rendering/lighting/ClusteredLightingDemo';
import { ClusteredLight } from '../../rendering/lighting/ClusteredLighting';
import { buildClusterTexture } from '../../rendering/lighting/ClusteredTileBuilder';
import { createClusteredMaterial } from '../../rendering/lighting/ClusteredLightingShader';

/**
 * Minimal Clustered lighting demo:
 * - Builds cluster lists and cluster texture
 * - Applies clustered material to a set of meshes
 */
export function createClusteredLightingScene(
  camera: THREE.PerspectiveCamera,
  scene: THREE.Scene
): void {
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const meshes: THREE.Mesh[] = [];
  for (let i = 0; i < 8; i++) {
    const m = new THREE.Mesh(geo);
    m.position.set((i - 4) * 2, Math.random() * 2, -5 - i * 1.5);
    scene.add(m);
    meshes.push(m);
  }

  const lights: ClusteredLight[] = [];
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

  meshes.forEach(m => (m.material = material));
}

