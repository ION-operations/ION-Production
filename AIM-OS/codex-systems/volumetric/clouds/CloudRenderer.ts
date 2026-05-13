import { CloudSettings, DEFAULT_CLOUD_SETTINGS } from './CloudGenerator';

export interface CloudRendererOptions {
  resolution?: number;
}

/**
 * Placeholder interface for a volumetric cloud renderer.
 * TODO: wire raymarch uniforms, 3D noise textures, and lighting params.
 */
export class CloudRenderer {
  private settings: CloudSettings;
  private resolution: number;

  constructor(settings: Partial<CloudSettings> = {}, options: CloudRendererOptions = {}) {
    this.settings = { ...DEFAULT_CLOUD_SETTINGS, ...settings };
    this.resolution = options.resolution ?? 512;
  }

  updateSettings(settings: Partial<CloudSettings>) {
    this.settings = { ...this.settings, ...settings };
  }

  getSettings(): CloudSettings {
    return this.settings;
  }

  getResolution(): number {
    return this.resolution;
  }
}

