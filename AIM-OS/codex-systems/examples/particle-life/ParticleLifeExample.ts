import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { createParticleLifeWebGPUScene } from '../../demos/particle-life/ParticleLifeWebGPUScene';

/**
 * Full example for Particle Life with WebGPU render path fallback.
 */
export async function initParticleLifeExample(canvas: HTMLCanvasElement) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);

  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 20);

  const controls = new OrbitControls(camera, renderer.domElement);

  const sim = await createParticleLifeWebGPUScene(scene, renderer, true);

  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  function animate() {
    requestAnimationFrame(animate);
    sim.update();
    renderer.render(scene, camera);
    controls.update();
  }
  animate();
}

