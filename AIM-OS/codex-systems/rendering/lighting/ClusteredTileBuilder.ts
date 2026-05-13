/**
 * Clustered Lighting Tile Texture Builder
 * Similar layout to Forward+ tile texture, extended to 3D clusters.
 *
 * Texture layout (RGBA32F):
 * - width = clustersX * maxLightsPerCluster
 * - height = clustersY * clustersZ
 * - For cluster (x,y,z):
 *   texel (x*maxLightsPerCluster + 0, y + z*clustersY): r = count
 *   texel (x*maxLightsPerCluster + i, y + z*clustersY): r = light index
 */

import * as THREE from 'three';
import { ClusterLightList } from './ClusteredLighting';

export function buildClusterTexture(
  clusters: ClusterLightList[],
  clustersX: number,
  clustersY: number,
  clustersZ: number,
  maxLightsPerCluster: number,
  maxLights: number
): THREE.DataTexture {
  const texWidth = clustersX * maxLightsPerCluster;
  const texHeight = clustersY * clustersZ;
  const data = new Float32Array(texWidth * texHeight * 4);

  for (let z = 0; z < clustersZ; z++) {
    for (let y = 0; y < clustersY; y++) {
      for (let x = 0; x < clustersX; x++) {
        const clusterIdx = z * clustersX * clustersY + y * clustersX + x;
        const list = clusters[clusterIdx];
        const count = Math.min(list.indices.length, maxLightsPerCluster - 1);

        // Header
        let base = ((y + z * clustersY) * texWidth + x * maxLightsPerCluster + 0) * 4;
        data[base + 0] = count;

        for (let i = 0; i < count; i++) {
          base = ((y + z * clustersY) * texWidth + x * maxLightsPerCluster + (i + 1)) * 4;
          data[base + 0] = list.indices[i] < maxLights ? list.indices[i] : -1;
        }
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

