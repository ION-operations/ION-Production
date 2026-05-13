/**
 * Clustered Lighting Shader (CPU → GPU bridge)
 *
 * Simplified shader that consumes:
 * - A texture buffer of cluster light indices (same layout as Forward+ tile texture)
 * - Cluster grid dims
 *
 * This is a reference; a full implementation would use 3D cluster addressing from depth and screen coords.
 */

import * as THREE from 'three';

export interface ClusteredShaderParams {
  clustersX: number;
  clustersY: number;
  clustersZ: number;
  maxLightsPerCluster: number;
  clusterTexture: THREE.DataTexture;
  maxLights: number;
  lightPositions: Float32Array;
  lightColors: Float32Array;
  lightRanges: Float32Array;
  lightIntensity: Float32Array;
}

export function createClusteredMaterial(params: ClusteredShaderParams): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      tCluster: { value: params.clusterTexture },
      clustersX: { value: params.clustersX },
      clustersY: { value: params.clustersY },
      clustersZ: { value: params.clustersZ },
      maxLightsPerCluster: { value: params.maxLightsPerCluster },
      maxLights: { value: params.maxLights },
      lightPositions: { value: params.lightPositions },
      lightColors: { value: params.lightColors },
      lightRanges: { value: params.lightRanges },
      lightIntensity: { value: params.lightIntensity },
      ambient: { value: new THREE.Color(0x222222) },
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vWorldPos;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vWorldPos = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: `
      precision highp float;
      uniform sampler2D tCluster;
      uniform int clustersX;
      uniform int clustersY;
      uniform int clustersZ;
      uniform int maxLightsPerCluster;
      uniform int maxLights;
      uniform float lightPositions[${params.maxLights * 3}];
      uniform float lightColors[${params.maxLights * 3}];
      uniform float lightRanges[${params.maxLights}];
      uniform float lightIntensity[${params.maxLights}];
      uniform vec3 ambient;
      varying vec3 vNormal;
      varying vec3 vWorldPos;

      vec3 getLightPos(int idx) {
        int i = idx * 3;
        return vec3(lightPositions[i], lightPositions[i+1], lightPositions[i+2]);
      }
      vec3 getLightColor(int idx) {
        int i = idx * 3;
        return vec3(lightColors[i], lightColors[i+1], lightColors[i+2]);
      }

      void main() {
        // Approximate cluster selection: use screen xy and a simple depth bucket.
        // Real implementation would use depth buffer. Here, assume mid-depth slice.
        ivec2 frag = ivec2(int(gl_FragCoord.x), int(gl_FragCoord.y));
        ivec3 cluster = ivec3(
          frag.x % clustersX,
          frag.y % clustersY,
          clustersZ / 2
        );

        // Compute cluster index
        int clusterIndex = cluster.z * clustersX * clustersY + cluster.y * clustersX + cluster.x;
        int texWidth = clustersX * maxLightsPerCluster;
        int texHeight = clustersY * clustersZ;

        // Header texel
        vec2 baseUV = vec2(float(cluster.x * maxLightsPerCluster) + 0.5, float(cluster.y + cluster.z * clustersY) + 0.5);
        vec2 texSize = vec2(float(texWidth), float(texHeight));
        float count = texture2D(tCluster, baseUV / texSize).r;
        int lightCount = int(count + 0.5);

        vec3 N = normalize(vNormal);
        vec3 color = ambient;

        for (int i = 0; i < ${params.maxLightsPerCluster}; i++) {
          if (i >= lightCount) break;
          vec2 uv = baseUV + vec2(float(i + 1), 0.0);
          float idxF = texture2D(tCluster, uv / texSize).r;
          int idx = int(idxF + 0.5);
          if (idx < 0 || idx >= maxLights) continue;

          vec3 Lpos = getLightPos(idx);
          vec3 L = Lpos - vWorldPos;
          float dist2 = dot(L, L);
          float range = lightRanges[idx];
          if (dist2 > range * range) continue;
          float dist = sqrt(dist2);
          L /= dist;
          float atten = max(0.0, 1.0 - dist / range);
          float ndotl = max(dot(N, L), 0.0);
          vec3 lc = getLightColor(idx) * lightIntensity[idx];
          color += lc * ndotl * atten;
        }

        gl_FragColor = vec4(color, 1.0);
      }
    `,
    lights: false,
  });
}

