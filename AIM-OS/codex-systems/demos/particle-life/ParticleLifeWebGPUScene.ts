import * as THREE from 'three';
import { ParticleLifeWebGPU } from '../../simulation/particle-life/ParticleLifeWebGPU';
import { ParticleLifeDemo } from '../../simulation/particle-life/ParticleLifeDemo';
import { ParticleLifeWebGPURenderer } from '../../simulation/particle-life/ParticleLifeWebGPURenderer';

/**
 * Particle Life WebGPU Scene
 * - Tries WebGPU compute; falls back to CPU demo if unsupported.
 */
export async function createParticleLifeWebGPUScene(
  scene: THREE.Scene,
  renderer: THREE.WebGLRenderer,
  useWebGPU: boolean = true
): Promise<{ update: () => void }> {
  const gpu = new ParticleLifeWebGPU();
  const supported = useWebGPU && (await gpu.init());

  if (!supported) {
    // Fallback to CPU demo
    const demo = new ParticleLifeDemo(scene, { particleCount: 2000, speciesCount: 5 });
    return {
      update: () => demo.update(),
    };
  }

  // WebGPU path
  const speciesCount = 5;
  const interaction: number[][] = [];
  for (let a = 0; a < speciesCount; a++) {
    interaction[a] = [];
    for (let b = 0; b < speciesCount; b++) {
      interaction[a][b] = THREE.MathUtils.lerp(-1, 1, Math.random()) * 3;
    }
  }

  const count = 4096;
  await gpu.allocate(count, speciesCount, interaction);
  gpu.uploadParams(0.016, 0.99, 2.5);

  // Initialize particles on CPU and upload
  const data = new Float32Array(count * 4);
  for (let i = 0; i < count; i++) {
    data[i * 4 + 0] = THREE.MathUtils.randFloatSpread(10);
    data[i * 4 + 1] = THREE.MathUtils.randFloatSpread(10);
    data[i * 4 + 2] = THREE.MathUtils.randFloatSpread(10);
    data[i * 4 + 3] = Math.floor(Math.random() * speciesCount);
  }
  gpu.uploadParticles(data);

  // WebGPU render path using ParticleLifeWebGPURenderer
  const canvas = renderer.domElement as HTMLCanvasElement;
  const format = (renderer as any).getContext()?.getCurrentTexture()?.format ?? 'bgra8unorm';
  const renderVis = new ParticleLifeWebGPURenderer(
    (gpu as any)['device'],
    (gpu as any)['queue'],
    canvas,
    format,
    10
  );

  return {
    update: () => {
      gpu.step();
      const particleBuffer = (gpu as any)['particleBuffer'];
      const velocityBuffer = (gpu as any)['velocityBuffer'];
      if (particleBuffer && velocityBuffer) {
        renderVis.render(particleBuffer, velocityBuffer, count);
      }
    },
  };
}

