// Volumetric cloud raymarch (placeholder stub)
precision highp float;
varying vec2 vUv;
uniform vec3 cameraPos;
uniform vec3 lightDir;
uniform float time;

void main() {
  // Placeholder: simple gradient; actual implementation will raymarch 3D noise
  float sky = smoothstep(0.0, 1.0, vUv.y);
  gl_FragColor = vec4(mix(vec3(0.9, 0.95, 1.0), vec3(0.6, 0.7, 0.8), sky), 1.0);
}

