import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { createVisibilityBufferScene } from '../../demos/visibility/VisibilityBufferScene';
import { VisibilityBufferDemo } from '../../rendering/visibility/VisibilityBufferDemo';

/**
 * Full Three.js example for Visibility Buffer.
 */
export async function initVisibilityBufferExample(canvas: HTMLCanvasElement) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0f0f12);

  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 2, 8);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1, -5);

  const vb = createVisibilityBufferScene(
    renderer,
    camera,
    scene,
    window.innerWidth,
    window.innerHeight
  );

  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    vb.setSize(w, h);
  });

  function animate() {
    requestAnimationFrame(animate);
    vb.render();
  }
  animate();
}

