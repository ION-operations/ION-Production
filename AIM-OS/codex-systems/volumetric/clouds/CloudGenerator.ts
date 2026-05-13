export interface NoiseParams {
  baseFrequency: number;
  lacunarity: number;
  gain: number;
  octaves: number;
  worleyBlend: number; // 0=FBM only, 1=Worley only
}

export interface DensityParams {
  baseDensity: number;
  heightFalloff: number;
  anvilStrength: number;
}

export interface LightingParams {
  hgG: number; // Henyey-Greenstein anisotropy
  lightAbsorption: number;
  ambient: number;
}

export interface CloudSettings {
  noise: NoiseParams;
  density: DensityParams;
  lighting: LightingParams;
}

export const DEFAULT_CLOUD_SETTINGS: CloudSettings = {
  noise: { baseFrequency: 0.8, lacunarity: 2.0, gain: 0.5, octaves: 5, worleyBlend: 0.35 },
  density: { baseDensity: 0.6, heightFalloff: 0.8, anvilStrength: 0.15 },
  lighting: { hgG: 0.65, lightAbsorption: 1.2, ambient: 0.15 }
};

