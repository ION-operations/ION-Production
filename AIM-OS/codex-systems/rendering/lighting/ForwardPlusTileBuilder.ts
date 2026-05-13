/**
 * Forward+ Tile Texture Builder
 *
 * Builds a float32 RGBA texture encoding per-tile light lists:
 * - Texture size: width = tilesX * maxLightsPerTile, height = tilesY
 * - For each tile (x,y):
 *   texel (x*maxLightsPerTile + 0, y): r = lightCount, g/b/a unused
 *   texel (x*maxLightsPerTile + i, y): r = lightIndex for i=1..lightCount
 *
 * This is a WebGL-friendly layout (no SSBOs). Shaders can sample tTile
 * to fetch indices; see ForwardPlusShader for a consumer.
 */

import * as THREE from 'three';
import { TileLightList } from './ForwardPlusLighting';

export function buildTileTexture(
  tileLists: TileLightList[],
  tilesX: number,
  tilesY: number,
  maxLightsPerTile: number,
  maxLights: number
): THREE.DataTexture {
  const texWidth = tilesX * maxLightsPerTile;
  const texHeight = tilesY;
  const data = new Float32Array(texWidth * texHeight * 4);

  for (let ty = 0; ty < tilesY; ty++) {
    for (let tx = 0; tx < tilesX; tx++) {
      const tileIndex = ty * tilesX + tx;
      const list = tileLists[tileIndex];
      const count = Math.min(list.indices.length, maxLightsPerTile - 1);

      // Header texel
      let base = (ty * texWidth + tx * maxLightsPerTile + 0) * 4;
      data[base + 0] = count;

      for (let i = 0; i < count; i++) {
        base = (ty * texWidth + tx * maxLightsPerTile + (i + 1)) * 4;
        data[base + 0] = list.indices[i] < maxLights ? list.indices[i] : -1;
      }
    }
  }

  const texture = new THREE.DataTexture(
    data,
    texWidth,
    texHeight,
    THREE.RGBAFormat,
    THREE.FloatType
  );
  texture.needsUpdate = true;
  texture.minFilter = THREE.NearestFilter;
  texture.magFilter = THREE.NearestFilter;
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;

  return texture;
}

