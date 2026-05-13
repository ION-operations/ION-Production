/**
 * Forward+ Shader Helper (CPU → GPU bridge)
 *
 * Simplified reference material that consumes:
 * - Light arrays (positions/colors/range/intensity) limited to MAX_LIGHTS
 * - Tile data as a float texture (tileCount, then indices)
 *
 * Tile texture layout (RGBA32F):
 * - Each texel represents one light index and a count header:
 *   texel 0 of each tile row: r = count (number of lights), g,b,a unused
 *   texel 1..N: r = light index, g,b,a unused
 *
 * The texture is arranged as a 2D atlas of tiles:
 *   width = tilesX * maxLightsPerTile
 *   height = tilesY
 *
 * For efficiency this should be a SSBO/texture buffer in WebGPU; this is a WebGL-friendly scaffold.
 */

import * as THREE from 'three';

export interface ForwardPlusShaderParams {
  tilesX: number;
  tilesY: number;
  maxLightsPerTile: number;
  tileTexture: THREE.DataTexture; // RGBA32F
  maxLights: number;
  lightPositions: Float32Array; // length = maxLights * 3
  lightColors: Float32Array;    // length = maxLights * 3
  lightRanges: Float32Array;    // length = maxLights
  lightIntensity: Float32Array; // length = maxLights
}

export function createForwardPlusMaterial(params: ForwardPlusShaderParams): THREE.ShaderMaterial {
  const material = new THREE.ShaderMaterial({
    uniforms: {
      tTile: { value: params.tileTexture },
      tilesX: { value: params.tilesX },
      tilesY: { value: params.tilesY },
      maxLightsPerTile: { value: params.maxLightsPerTile },
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
      uniform sampler2D tTile;
      uniform int tilesX;
      uniform int tilesY;
      uniform int maxLightsPerTile;
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
        // Determine tile from gl_FragCoord
        ivec2 tile = ivec2(int(gl_FragCoord.x) / maxLightsPerTile, int(gl_FragCoord.y));
        // Convert to UV in tile texture
        vec2 baseUV = vec2(float(tile.x * maxLightsPerTile) + 0.5, float(tile.y) + 0.5);
        vec2 texSize = vec2(float(tilesX * maxLightsPerTile), float(tilesY));
        // Read count (r channel)
        float count = texture2D(tTile, baseUV / texSize).r;
        int lightCount = int(count + 0.5);

        vec3 N = normalize(vNormal);
        vec3 V = normalize(cameraPosition - vWorldPos);
        vec3 color = ambient;

        for (int i = 0; i < ${params.maxLightsPerTile}; i++) {
          if (i >= lightCount) break;
          vec2 uv = baseUV + vec2(float(i + 1), 0.0);
          float idxF = texture2D(tTile, uv / texSize).r;
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

  material.defines = {
    MAX_LIGHTS_PER_TILE: params.maxLightsPerTile,
    MAX_LIGHTS: params.maxLights,
  };

  return material;
}

