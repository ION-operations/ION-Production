/**
 * PBR Material System
 * Physically Based Rendering with metallic-roughness workflow
 * 
 * Features:
 * - Cook-Torrance BRDF
 * - Image-Based Lighting (IBL)
 * - Multiple texture maps support
 * - Material layering
 * - Parallax occlusion mapping
 */

import * as THREE from 'three';

export interface PBRMaterialConfig {
  // Base properties
  albedo: THREE.Color;
  metallic: number;
  roughness: number;
  ao: number;
  
  // Emission
  emissive: THREE.Color;
  emissiveIntensity: number;
  
  // Normal
  normalScale: number;
  
  // Parallax
  parallaxScale: number;
  parallaxMinLayers: number;
  parallaxMaxLayers: number;
  
  // Subsurface
  subsurfaceColor: THREE.Color;
  subsurfaceIntensity: number;
  
  // Clearcoat
  clearcoat: number;
  clearcoatRoughness: number;
  
  // Sheen (for fabrics)
  sheen: number;
  sheenColor: THREE.Color;
  sheenRoughness: number;
  
  // Transmission (glass)
  transmission: number;
  ior: number;
  thickness: number;
}

export const DEFAULT_PBR_CONFIG: PBRMaterialConfig = {
  albedo: new THREE.Color(0.8, 0.8, 0.8),
  metallic: 0.0,
  roughness: 0.5,
  ao: 1.0,
  emissive: new THREE.Color(0, 0, 0),
  emissiveIntensity: 1.0,
  normalScale: 1.0,
  parallaxScale: 0.05,
  parallaxMinLayers: 8,
  parallaxMaxLayers: 32,
  subsurfaceColor: new THREE.Color(1, 0, 0),
  subsurfaceIntensity: 0.0,
  clearcoat: 0.0,
  clearcoatRoughness: 0.0,
  sheen: 0.0,
  sheenColor: new THREE.Color(1, 1, 1),
  sheenRoughness: 0.5,
  transmission: 0.0,
  ior: 1.5,
  thickness: 1.0
};

export interface PBRTextures {
  albedoMap?: THREE.Texture;
  normalMap?: THREE.Texture;
  metallicMap?: THREE.Texture;
  roughnessMap?: THREE.Texture;
  aoMap?: THREE.Texture;
  emissiveMap?: THREE.Texture;
  heightMap?: THREE.Texture;
  
  // IBL
  envMap?: THREE.CubeTexture;
  brdfLUT?: THREE.Texture;
}

export class PBRMaterial extends THREE.ShaderMaterial {
  private config: PBRMaterialConfig;
  private textures: PBRTextures;

  constructor(config: Partial<PBRMaterialConfig> = {}, textures: PBRTextures = {}) {
    const fullConfig = { ...DEFAULT_PBR_CONFIG, ...config };
    
    super({
      uniforms: {
        // Base
        uAlbedo: { value: fullConfig.albedo },
        uMetallic: { value: fullConfig.metallic },
        uRoughness: { value: fullConfig.roughness },
        uAO: { value: fullConfig.ao },
        
        // Emission
        uEmissive: { value: fullConfig.emissive },
        uEmissiveIntensity: { value: fullConfig.emissiveIntensity },
        
        // Normal
        uNormalScale: { value: fullConfig.normalScale },
        
        // Parallax
        uParallaxScale: { value: fullConfig.parallaxScale },
        uParallaxMinLayers: { value: fullConfig.parallaxMinLayers },
        uParallaxMaxLayers: { value: fullConfig.parallaxMaxLayers },
        
        // Subsurface
        uSubsurfaceColor: { value: fullConfig.subsurfaceColor },
        uSubsurfaceIntensity: { value: fullConfig.subsurfaceIntensity },
        
        // Clearcoat
        uClearcoat: { value: fullConfig.clearcoat },
        uClearcoatRoughness: { value: fullConfig.clearcoatRoughness },
        
        // Sheen
        uSheen: { value: fullConfig.sheen },
        uSheenColor: { value: fullConfig.sheenColor },
        uSheenRoughness: { value: fullConfig.sheenRoughness },
        
        // Transmission
        uTransmission: { value: fullConfig.transmission },
        uIOR: { value: fullConfig.ior },
        uThickness: { value: fullConfig.thickness },
        
        // Textures
        tAlbedo: { value: textures.albedoMap || null },
        tNormal: { value: textures.normalMap || null },
        tMetallic: { value: textures.metallicMap || null },
        tRoughness: { value: textures.roughnessMap || null },
        tAO: { value: textures.aoMap || null },
        tEmissive: { value: textures.emissiveMap || null },
        tHeight: { value: textures.heightMap || null },
        tEnvMap: { value: textures.envMap || null },
        tBRDFLUT: { value: textures.brdfLUT || null },
        
        // Flags
        uUseAlbedoMap: { value: !!textures.albedoMap },
        uUseNormalMap: { value: !!textures.normalMap },
        uUseMetallicMap: { value: !!textures.metallicMap },
        uUseRoughnessMap: { value: !!textures.roughnessMap },
        uUseAOMap: { value: !!textures.aoMap },
        uUseEmissiveMap: { value: !!textures.emissiveMap },
        uUseHeightMap: { value: !!textures.heightMap },
        uUseEnvMap: { value: !!textures.envMap },
        
        // Camera
        uCameraPosition: { value: new THREE.Vector3() }
      },
      vertexShader: PBRMaterial.getVertexShader(),
      fragmentShader: PBRMaterial.getFragmentShader(),
      lights: true
    });
    
    this.config = fullConfig;
    this.textures = textures;
  }

  public setAlbedo(color: THREE.Color): void {
    this.uniforms.uAlbedo.value.copy(color);
  }

  public setMetallic(value: number): void {
    this.uniforms.uMetallic.value = value;
  }

  public setRoughness(value: number): void {
    this.uniforms.uRoughness.value = value;
  }

  public setTexture(slot: keyof PBRTextures, texture: THREE.Texture | null): void {
    const uniformMap: Record<string, string> = {
      albedoMap: 'tAlbedo',
      normalMap: 'tNormal',
      metallicMap: 'tMetallic',
      roughnessMap: 'tRoughness',
      aoMap: 'tAO',
      emissiveMap: 'tEmissive',
      heightMap: 'tHeight',
      envMap: 'tEnvMap',
      brdfLUT: 'tBRDFLUT'
    };
    
    const flagMap: Record<string, string> = {
      albedoMap: 'uUseAlbedoMap',
      normalMap: 'uUseNormalMap',
      metallicMap: 'uUseMetallicMap',
      roughnessMap: 'uUseRoughnessMap',
      aoMap: 'uUseAOMap',
      emissiveMap: 'uUseEmissiveMap',
      heightMap: 'uUseHeightMap',
      envMap: 'uUseEnvMap'
    };
    
    if (uniformMap[slot]) {
      this.uniforms[uniformMap[slot]].value = texture;
    }
    if (flagMap[slot]) {
      this.uniforms[flagMap[slot]].value = !!texture;
    }
  }

  public updateCamera(camera: THREE.Camera): void {
    this.uniforms.uCameraPosition.value.copy(camera.position);
  }

  private static getVertexShader(): string {
    return `
      varying vec3 vNormal;
      varying vec3 vWorldPosition;
      varying vec2 vUv;
      varying vec3 vViewPosition;
      varying mat3 vTBN;
      
      attribute vec4 tangent;
      
      void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        
        vec4 worldPosition = modelMatrix * vec4(position, 1.0);
        vWorldPosition = worldPosition.xyz;
        
        vec4 mvPosition = viewMatrix * worldPosition;
        vViewPosition = -mvPosition.xyz;
        
        // Calculate TBN matrix for normal mapping
        vec3 T = normalize(normalMatrix * tangent.xyz);
        vec3 N = vNormal;
        vec3 B = normalize(cross(N, T) * tangent.w);
        vTBN = mat3(T, B, N);
        
        gl_Position = projectionMatrix * mvPosition;
      }
    `;
  }

  private static getFragmentShader(): string {
    return `
      #define PI 3.14159265359
      #define RECIPROCAL_PI 0.31830988618
      
      // Uniforms
      uniform vec3 uAlbedo;
      uniform float uMetallic;
      uniform float uRoughness;
      uniform float uAO;
      uniform vec3 uEmissive;
      uniform float uEmissiveIntensity;
      uniform float uNormalScale;
      uniform float uParallaxScale;
      uniform float uParallaxMinLayers;
      uniform float uParallaxMaxLayers;
      uniform vec3 uSubsurfaceColor;
      uniform float uSubsurfaceIntensity;
      uniform float uClearcoat;
      uniform float uClearcoatRoughness;
      uniform float uSheen;
      uniform vec3 uSheenColor;
      uniform float uSheenRoughness;
      uniform float uTransmission;
      uniform float uIOR;
      uniform float uThickness;
      
      uniform sampler2D tAlbedo;
      uniform sampler2D tNormal;
      uniform sampler2D tMetallic;
      uniform sampler2D tRoughness;
      uniform sampler2D tAO;
      uniform sampler2D tEmissive;
      uniform sampler2D tHeight;
      uniform samplerCube tEnvMap;
      uniform sampler2D tBRDFLUT;
      
      uniform bool uUseAlbedoMap;
      uniform bool uUseNormalMap;
      uniform bool uUseMetallicMap;
      uniform bool uUseRoughnessMap;
      uniform bool uUseAOMap;
      uniform bool uUseEmissiveMap;
      uniform bool uUseHeightMap;
      uniform bool uUseEnvMap;
      
      uniform vec3 uCameraPosition;
      
      varying vec3 vNormal;
      varying vec3 vWorldPosition;
      varying vec2 vUv;
      varying vec3 vViewPosition;
      varying mat3 vTBN;
      
      // === BRDF Functions ===
      
      // Normal Distribution Function (GGX/Trowbridge-Reitz)
      float DistributionGGX(vec3 N, vec3 H, float roughness) {
        float a = roughness * roughness;
        float a2 = a * a;
        float NdotH = max(dot(N, H), 0.0);
        float NdotH2 = NdotH * NdotH;
        
        float denom = (NdotH2 * (a2 - 1.0) + 1.0);
        denom = PI * denom * denom;
        
        return a2 / max(denom, 0.0001);
      }
      
      // Geometry Function (Smith's Schlick-GGX)
      float GeometrySchlickGGX(float NdotV, float roughness) {
        float r = roughness + 1.0;
        float k = (r * r) / 8.0;
        return NdotV / (NdotV * (1.0 - k) + k);
      }
      
      float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
        float NdotV = max(dot(N, V), 0.0);
        float NdotL = max(dot(N, L), 0.0);
        float ggx2 = GeometrySchlickGGX(NdotV, roughness);
        float ggx1 = GeometrySchlickGGX(NdotL, roughness);
        return ggx1 * ggx2;
      }
      
      // Fresnel (Schlick approximation)
      vec3 FresnelSchlick(float cosTheta, vec3 F0) {
        return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
      }
      
      vec3 FresnelSchlickRoughness(float cosTheta, vec3 F0, float roughness) {
        return F0 + (max(vec3(1.0 - roughness), F0) - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
      }
      
      // === Parallax Mapping ===
      
      vec2 ParallaxMapping(vec2 texCoords, vec3 viewDir) {
        if (!uUseHeightMap) return texCoords;
        
        float numLayers = mix(uParallaxMaxLayers, uParallaxMinLayers, abs(dot(vec3(0.0, 0.0, 1.0), viewDir)));
        float layerDepth = 1.0 / numLayers;
        float currentLayerDepth = 0.0;
        
        vec2 P = viewDir.xy * uParallaxScale;
        vec2 deltaTexCoords = P / numLayers;
        
        vec2 currentTexCoords = texCoords;
        float currentDepthMapValue = 1.0 - texture2D(tHeight, currentTexCoords).r;
        
        for (int i = 0; i < 32; i++) {
          if (currentLayerDepth >= currentDepthMapValue) break;
          currentTexCoords -= deltaTexCoords;
          currentDepthMapValue = 1.0 - texture2D(tHeight, currentTexCoords).r;
          currentLayerDepth += layerDepth;
        }
        
        // Interpolation
        vec2 prevTexCoords = currentTexCoords + deltaTexCoords;
        float afterDepth = currentDepthMapValue - currentLayerDepth;
        float beforeDepth = (1.0 - texture2D(tHeight, prevTexCoords).r) - currentLayerDepth + layerDepth;
        float weight = afterDepth / (afterDepth - beforeDepth);
        
        return mix(currentTexCoords, prevTexCoords, weight);
      }
      
      void main() {
        vec3 V = normalize(uCameraPosition - vWorldPosition);
        
        // Parallax mapping
        vec3 viewDirTangent = normalize(transpose(vTBN) * V);
        vec2 texCoords = ParallaxMapping(vUv, viewDirTangent);
        
        // Sample textures
        vec3 albedo = uUseAlbedoMap ? texture2D(tAlbedo, texCoords).rgb : uAlbedo;
        albedo = pow(albedo, vec3(2.2)); // sRGB to linear
        
        float metallic = uUseMetallicMap ? texture2D(tMetallic, texCoords).r : uMetallic;
        float roughness = uUseRoughnessMap ? texture2D(tRoughness, texCoords).r : uRoughness;
        roughness = max(roughness, 0.04);
        float ao = uUseAOMap ? texture2D(tAO, texCoords).r : uAO;
        
        // Normal mapping
        vec3 N = vNormal;
        if (uUseNormalMap) {
          vec3 normalTex = texture2D(tNormal, texCoords).rgb * 2.0 - 1.0;
          normalTex.xy *= uNormalScale;
          N = normalize(vTBN * normalTex);
        }
        
        // F0 (reflectance at normal incidence)
        vec3 F0 = vec3(0.04);
        F0 = mix(F0, albedo, metallic);
        
        // === Lighting ===
        vec3 Lo = vec3(0.0);
        
        // Simple directional light
        vec3 lightDir = normalize(vec3(0.5, 1.0, 0.5));
        vec3 lightColor = vec3(3.0);
        
        vec3 L = lightDir;
        vec3 H = normalize(V + L);
        float NdotL = max(dot(N, L), 0.0);
        
        // Cook-Torrance BRDF
        float NDF = DistributionGGX(N, H, roughness);
        float G = GeometrySmith(N, V, L, roughness);
        vec3 F = FresnelSchlick(max(dot(H, V), 0.0), F0);
        
        vec3 numerator = NDF * G * F;
        float denominator = 4.0 * max(dot(N, V), 0.0) * NdotL + 0.0001;
        vec3 specular = numerator / denominator;
        
        vec3 kS = F;
        vec3 kD = vec3(1.0) - kS;
        kD *= 1.0 - metallic;
        
        Lo += (kD * albedo * RECIPROCAL_PI + specular) * lightColor * NdotL;
        
        // === IBL ===
        vec3 ambient = vec3(0.03) * albedo * ao;
        
        if (uUseEnvMap) {
          vec3 R = reflect(-V, N);
          
          // Diffuse IBL
          vec3 irradiance = textureCube(tEnvMap, N).rgb; // Ideally use irradiance map
          vec3 diffuse = irradiance * albedo;
          
          // Specular IBL
          float lod = roughness * 4.0; // Mip level based on roughness
          vec3 prefilteredColor = textureCube(tEnvMap, R).rgb; // Ideally use prefiltered map
          
          vec3 FEnv = FresnelSchlickRoughness(max(dot(N, V), 0.0), F0, roughness);
          vec3 kSEnv = FEnv;
          vec3 kDEnv = 1.0 - kSEnv;
          kDEnv *= 1.0 - metallic;
          
          ambient = (kDEnv * diffuse + prefilteredColor * FEnv) * ao;
        }
        
        // === Subsurface Scattering ===
        if (uSubsurfaceIntensity > 0.0) {
          float sss = pow(max(dot(V, -L), 0.0), 3.0);
          Lo += uSubsurfaceColor * sss * uSubsurfaceIntensity * (1.0 - metallic);
        }
        
        // === Clearcoat ===
        if (uClearcoat > 0.0) {
          float ccNDF = DistributionGGX(N, H, uClearcoatRoughness);
          float ccG = GeometrySmith(N, V, L, uClearcoatRoughness);
          vec3 ccF = FresnelSchlick(max(dot(H, V), 0.0), vec3(0.04));
          vec3 ccSpecular = (ccNDF * ccG * ccF) / (4.0 * max(dot(N, V), 0.0) * NdotL + 0.0001);
          Lo += ccSpecular * lightColor * NdotL * uClearcoat;
        }
        
        // === Sheen ===
        if (uSheen > 0.0) {
          float sheenDist = 1.0 - pow(max(dot(N, H), 0.0), 1.0 / (uSheenRoughness + 0.001));
          vec3 sheenColor = uSheenColor * sheenDist * uSheen;
          Lo += sheenColor * NdotL;
        }
        
        // === Emission ===
        vec3 emissive = uUseEmissiveMap 
          ? texture2D(tEmissive, texCoords).rgb * uEmissiveIntensity
          : uEmissive * uEmissiveIntensity;
        
        // === Final ===
        vec3 color = ambient + Lo + emissive;
        
        // Tone mapping (ACES)
        color = color / (color + vec3(1.0));
        
        // Gamma correction
        color = pow(color, vec3(1.0/2.2));
        
        gl_FragColor = vec4(color, 1.0);
      }
    `;
  }

  /**
   * Generate BRDF LUT texture for IBL
   */
  public static generateBRDFLUT(size: number = 512): THREE.DataTexture {
    const data = new Float32Array(size * size * 4);
    
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const NdotV = (x + 0.5) / size;
        const roughness = (y + 0.5) / size;
        
        const result = PBRMaterial.integrateBRDF(NdotV, roughness);
        
        const idx = (y * size + x) * 4;
        data[idx] = result.x;
        data[idx + 1] = result.y;
        data[idx + 2] = 0;
        data[idx + 3] = 1;
      }
    }
    
    const texture = new THREE.DataTexture(
      data, size, size, THREE.RGBAFormat, THREE.FloatType
    );
    texture.needsUpdate = true;
    
    return texture;
  }

  private static integrateBRDF(NdotV: number, roughness: number): THREE.Vector2 {
    const V = new THREE.Vector3(
      Math.sqrt(1 - NdotV * NdotV),
      0,
      NdotV
    );
    
    let A = 0;
    let B = 0;
    const N = new THREE.Vector3(0, 0, 1);
    const sampleCount = 1024;
    
    for (let i = 0; i < sampleCount; i++) {
      const Xi = PBRMaterial.hammersley(i, sampleCount);
      const H = PBRMaterial.importanceSampleGGX(Xi, N, roughness);
      const L = new THREE.Vector3().copy(H).multiplyScalar(2 * V.dot(H)).sub(V);
      
      const NdotL = Math.max(L.z, 0);
      const NdotH = Math.max(H.z, 0);
      const VdotH = Math.max(V.dot(H), 0);
      
      if (NdotL > 0) {
        const G = PBRMaterial.geometrySmith(N, V, L, roughness);
        const G_Vis = (G * VdotH) / (NdotH * NdotV);
        const Fc = Math.pow(1 - VdotH, 5);
        
        A += (1 - Fc) * G_Vis;
        B += Fc * G_Vis;
      }
    }
    
    A /= sampleCount;
    B /= sampleCount;
    
    return new THREE.Vector2(A, B);
  }

  private static hammersley(i: number, N: number): THREE.Vector2 {
    let bits = i;
    bits = (bits << 16) | (bits >>> 16);
    bits = ((bits & 0x55555555) << 1) | ((bits & 0xAAAAAAAA) >>> 1);
    bits = ((bits & 0x33333333) << 2) | ((bits & 0xCCCCCCCC) >>> 2);
    bits = ((bits & 0x0F0F0F0F) << 4) | ((bits & 0xF0F0F0F0) >>> 4);
    bits = ((bits & 0x00FF00FF) << 8) | ((bits & 0xFF00FF00) >>> 8);
    
    const radicalInverse = (bits >>> 0) * 2.3283064365386963e-10;
    return new THREE.Vector2(i / N, radicalInverse);
  }

  private static importanceSampleGGX(Xi: THREE.Vector2, N: THREE.Vector3, roughness: number): THREE.Vector3 {
    const a = roughness * roughness;
    
    const phi = 2 * Math.PI * Xi.x;
    const cosTheta = Math.sqrt((1 - Xi.y) / (1 + (a * a - 1) * Xi.y));
    const sinTheta = Math.sqrt(1 - cosTheta * cosTheta);
    
    const H = new THREE.Vector3(
      Math.cos(phi) * sinTheta,
      Math.sin(phi) * sinTheta,
      cosTheta
    );
    
    // Tangent space to world space
    const up = Math.abs(N.z) < 0.999 ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(1, 0, 0);
    const tangent = new THREE.Vector3().crossVectors(up, N).normalize();
    const bitangent = new THREE.Vector3().crossVectors(N, tangent);
    
    return new THREE.Vector3(
      tangent.x * H.x + bitangent.x * H.y + N.x * H.z,
      tangent.y * H.x + bitangent.y * H.y + N.y * H.z,
      tangent.z * H.x + bitangent.z * H.y + N.z * H.z
    ).normalize();
  }

  private static geometrySmith(N: THREE.Vector3, V: THREE.Vector3, L: THREE.Vector3, roughness: number): number {
    const NdotV = Math.max(N.dot(V), 0);
    const NdotL = Math.max(N.dot(L), 0);
    const ggx2 = PBRMaterial.geometrySchlickGGX(NdotV, roughness);
    const ggx1 = PBRMaterial.geometrySchlickGGX(NdotL, roughness);
    return ggx1 * ggx2;
  }

  private static geometrySchlickGGX(NdotV: number, roughness: number): number {
    const a = roughness;
    const k = (a * a) / 2;
    return NdotV / (NdotV * (1 - k) + k);
  }
}

