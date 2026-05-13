/**
 * Spatial Audio System
 * 3D positional audio with HRTF, reverb, and advanced effects
 * 
 * Features:
 * - 3D positional audio (HRTF)
 * - Distance attenuation
 * - Doppler effect
 * - Reverb zones
 * - Occlusion/obstruction
 * - Music crossfading
 * - Ambience layers
 * - Audio pooling
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface AudioSourceConfig {
  volume: number;
  loop: boolean;
  spatialize: boolean;
  minDistance: number;
  maxDistance: number;
  rolloffFactor: number;
  coneInnerAngle: number;
  coneOuterAngle: number;
  coneOuterGain: number;
  dopplerFactor: number;
}

export interface ReverbZone {
  id: string;
  position: THREE.Vector3;
  size: THREE.Vector3;
  preset: ReverbPreset;
  wetLevel: number;
  dryLevel: number;
  priority: number;
}

export type ReverbPreset = 
  | 'none'
  | 'small_room'
  | 'medium_room'
  | 'large_room'
  | 'hall'
  | 'cathedral'
  | 'cave'
  | 'outdoor'
  | 'underwater';

export interface AudioSource {
  id: string;
  node: AudioBufferSourceNode | null;
  panner: PannerNode | null;
  gain: GainNode;
  config: AudioSourceConfig;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  buffer: AudioBuffer | null;
  isPlaying: boolean;
  startTime: number;
}

export interface AmbienceLayer {
  id: string;
  sources: { buffer: AudioBuffer; weight: number }[];
  currentWeight: number;
  targetWeight: number;
  gain: GainNode;
}

// ============================================
// REVERB PRESETS
// ============================================

const REVERB_PRESETS: Record<ReverbPreset, { decay: number; preDelay: number; wetLevel: number }> = {
  none: { decay: 0, preDelay: 0, wetLevel: 0 },
  small_room: { decay: 0.3, preDelay: 0.01, wetLevel: 0.3 },
  medium_room: { decay: 0.6, preDelay: 0.02, wetLevel: 0.4 },
  large_room: { decay: 1.0, preDelay: 0.03, wetLevel: 0.5 },
  hall: { decay: 2.0, preDelay: 0.05, wetLevel: 0.6 },
  cathedral: { decay: 4.0, preDelay: 0.08, wetLevel: 0.7 },
  cave: { decay: 3.0, preDelay: 0.1, wetLevel: 0.8 },
  outdoor: { decay: 0.1, preDelay: 0, wetLevel: 0.1 },
  underwater: { decay: 0.5, preDelay: 0.15, wetLevel: 0.9 }
};

// ============================================
// AUDIO OCCLUSION
// ============================================

export class AudioOcclusion {
  private lowPassFilter: BiquadFilterNode;
  private highPassFilter: BiquadFilterNode;
  
  constructor(audioContext: AudioContext) {
    this.lowPassFilter = audioContext.createBiquadFilter();
    this.lowPassFilter.type = 'lowpass';
    this.lowPassFilter.frequency.value = 22000;
    
    this.highPassFilter = audioContext.createBiquadFilter();
    this.highPassFilter.type = 'highpass';
    this.highPassFilter.frequency.value = 20;
    
    this.lowPassFilter.connect(this.highPassFilter);
  }
  
  /**
   * Apply occlusion based on obstacles
   */
  public applyOcclusion(
    occlusionFactor: number, // 0 = no occlusion, 1 = fully occluded
    materialDensity: number = 1 // 0 = air, 1 = solid
  ): void {
    // Lower frequencies pass through better
    const minFreq = 200;
    const maxFreq = 22000;
    
    const cutoffFreq = THREE.MathUtils.lerp(
      maxFreq,
      minFreq,
      occlusionFactor * materialDensity
    );
    
    this.lowPassFilter.frequency.value = cutoffFreq;
    
    // Add some high-pass for muffled effect
    if (occlusionFactor > 0.5) {
      this.highPassFilter.frequency.value = THREE.MathUtils.lerp(
        20,
        500,
        (occlusionFactor - 0.5) * 2
      );
    }
  }
  
  public getInputNode(): BiquadFilterNode {
    return this.lowPassFilter;
  }
  
  public getOutputNode(): BiquadFilterNode {
    return this.highPassFilter;
  }
  
  public disconnect(): void {
    this.lowPassFilter.disconnect();
    this.highPassFilter.disconnect();
  }
}

// ============================================
// CONVOLVER REVERB
// ============================================

export class ConvolverReverb {
  private convolver: ConvolverNode;
  private wetGain: GainNode;
  private dryGain: GainNode;
  private inputGain: GainNode;
  private outputGain: GainNode;
  private audioContext: AudioContext;
  
  constructor(audioContext: AudioContext) {
    this.audioContext = audioContext;
    
    this.convolver = audioContext.createConvolver();
    this.wetGain = audioContext.createGain();
    this.dryGain = audioContext.createGain();
    this.inputGain = audioContext.createGain();
    this.outputGain = audioContext.createGain();
    
    // Routing
    this.inputGain.connect(this.dryGain);
    this.inputGain.connect(this.convolver);
    this.convolver.connect(this.wetGain);
    this.wetGain.connect(this.outputGain);
    this.dryGain.connect(this.outputGain);
  }
  
  /**
   * Generate impulse response for reverb
   */
  public generateImpulseResponse(
    duration: number,
    decay: number,
    preDelay: number = 0
  ): void {
    const sampleRate = this.audioContext.sampleRate;
    const length = sampleRate * duration;
    const impulse = this.audioContext.createBuffer(2, length, sampleRate);
    
    const left = impulse.getChannelData(0);
    const right = impulse.getChannelData(1);
    const preSamples = Math.floor(preDelay * sampleRate);
    
    for (let i = preSamples; i < length; i++) {
      const t = (i - preSamples) / sampleRate;
      const amplitude = Math.exp(-t / decay);
      
      // Random noise with exponential decay
      left[i] = (Math.random() * 2 - 1) * amplitude;
      right[i] = (Math.random() * 2 - 1) * amplitude;
    }
    
    this.convolver.buffer = impulse;
  }
  
  /**
   * Set wet/dry mix
   */
  public setMix(wetLevel: number, dryLevel: number = 1 - wetLevel): void {
    this.wetGain.gain.value = wetLevel;
    this.dryGain.gain.value = dryLevel;
  }
  
  /**
   * Apply reverb preset
   */
  public applyPreset(preset: ReverbPreset): void {
    const settings = REVERB_PRESETS[preset];
    this.generateImpulseResponse(settings.decay * 2, settings.decay, settings.preDelay);
    this.setMix(settings.wetLevel);
  }
  
  public getInputNode(): GainNode {
    return this.inputGain;
  }
  
  public getOutputNode(): GainNode {
    return this.outputGain;
  }
  
  public dispose(): void {
    this.convolver.disconnect();
    this.wetGain.disconnect();
    this.dryGain.disconnect();
    this.inputGain.disconnect();
    this.outputGain.disconnect();
  }
}

// ============================================
// MUSIC CROSSFADER
// ============================================

export class MusicCrossfader {
  private audioContext: AudioContext;
  private tracks: Map<string, { source: AudioBufferSourceNode; gain: GainNode }> = new Map();
  private currentTrack: string | null = null;
  private crossfadeDuration: number = 2.0;
  private masterGain: GainNode;
  
  constructor(audioContext: AudioContext, destination: AudioNode) {
    this.audioContext = audioContext;
    this.masterGain = audioContext.createGain();
    this.masterGain.connect(destination);
  }
  
  /**
   * Load and prepare a music track
   */
  public loadTrack(id: string, buffer: AudioBuffer): void {
    const source = this.audioContext.createBufferSource();
    source.buffer = buffer;
    source.loop = true;
    
    const gain = this.audioContext.createGain();
    gain.gain.value = 0;
    
    source.connect(gain);
    gain.connect(this.masterGain);
    
    this.tracks.set(id, { source, gain });
  }
  
  /**
   * Crossfade to a new track
   */
  public crossfadeTo(trackId: string, duration?: number): void {
    const fadeDuration = duration ?? this.crossfadeDuration;
    const now = this.audioContext.currentTime;
    
    // Fade out current track
    if (this.currentTrack) {
      const current = this.tracks.get(this.currentTrack);
      if (current) {
        current.gain.gain.setValueAtTime(current.gain.gain.value, now);
        current.gain.gain.linearRampToValueAtTime(0, now + fadeDuration);
      }
    }
    
    // Fade in new track
    const next = this.tracks.get(trackId);
    if (next) {
      if (!next.source.buffer) return;
      
      try {
        next.source.start(0);
      } catch (e) {
        // Already started
      }
      
      next.gain.gain.setValueAtTime(next.gain.gain.value, now);
      next.gain.gain.linearRampToValueAtTime(1, now + fadeDuration);
      
      this.currentTrack = trackId;
    }
  }
  
  /**
   * Set master volume
   */
  public setVolume(volume: number): void {
    this.masterGain.gain.value = volume;
  }
  
  public dispose(): void {
    this.tracks.forEach(track => {
      track.source.disconnect();
      track.gain.disconnect();
    });
    this.tracks.clear();
    this.masterGain.disconnect();
  }
}

// ============================================
// MAIN SPATIAL AUDIO SYSTEM
// ============================================

export class SpatialAudioSystem {
  private audioContext: AudioContext;
  private listener: THREE.AudioListener;
  private sources: Map<string, AudioSource> = new Map();
  private reverbZones: Map<string, ReverbZone> = new Map();
  private ambienceLayers: Map<string, AmbienceLayer> = new Map();
  
  private masterGain: GainNode;
  private compressor: DynamicsCompressorNode;
  private reverb: ConvolverReverb;
  private crossfader: MusicCrossfader;
  
  private listenerPosition: THREE.Vector3 = new THREE.Vector3();
  private listenerOrientation: THREE.Quaternion = new THREE.Quaternion();
  private listenerVelocity: THREE.Vector3 = new THREE.Vector3();
  
  private defaultConfig: AudioSourceConfig = {
    volume: 1,
    loop: false,
    spatialize: true,
    minDistance: 1,
    maxDistance: 100,
    rolloffFactor: 1,
    coneInnerAngle: 360,
    coneOuterAngle: 360,
    coneOuterGain: 0,
    dopplerFactor: 1
  };
  
  constructor() {
    this.audioContext = new AudioContext();
    this.listener = new THREE.AudioListener();
    
    // Create master chain
    this.masterGain = this.audioContext.createGain();
    this.compressor = this.audioContext.createDynamicsCompressor();
    
    this.masterGain.connect(this.compressor);
    this.compressor.connect(this.audioContext.destination);
    
    // Setup reverb
    this.reverb = new ConvolverReverb(this.audioContext);
    this.reverb.applyPreset('medium_room');
    this.reverb.getOutputNode().connect(this.masterGain);
    
    // Setup music crossfader
    this.crossfader = new MusicCrossfader(this.audioContext, this.masterGain);
    
    // Setup audio context listener
    this.updateListenerOrientation();
  }
  
  /**
   * Resume audio context (required after user interaction)
   */
  public async resume(): Promise<void> {
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }
  }
  
  /**
   * Load audio file
   */
  public async loadAudio(url: string): Promise<AudioBuffer> {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    return this.audioContext.decodeAudioData(arrayBuffer);
  }
  
  /**
   * Create audio source
   */
  public createSource(
    id: string,
    buffer: AudioBuffer,
    position: THREE.Vector3,
    config: Partial<AudioSourceConfig> = {}
  ): AudioSource {
    const fullConfig = { ...this.defaultConfig, ...config };
    
    const gain = this.audioContext.createGain();
    gain.gain.value = fullConfig.volume;
    
    let panner: PannerNode | null = null;
    
    if (fullConfig.spatialize) {
      panner = this.audioContext.createPanner();
      panner.panningModel = 'HRTF';
      panner.distanceModel = 'inverse';
      panner.refDistance = fullConfig.minDistance;
      panner.maxDistance = fullConfig.maxDistance;
      panner.rolloffFactor = fullConfig.rolloffFactor;
      panner.coneInnerAngle = fullConfig.coneInnerAngle;
      panner.coneOuterAngle = fullConfig.coneOuterAngle;
      panner.coneOuterGain = fullConfig.coneOuterGain;
      
      panner.positionX.value = position.x;
      panner.positionY.value = position.y;
      panner.positionZ.value = position.z;
      
      gain.connect(panner);
      panner.connect(this.reverb.getInputNode());
    } else {
      gain.connect(this.masterGain);
    }
    
    const source: AudioSource = {
      id,
      node: null,
      panner,
      gain,
      config: fullConfig,
      position: position.clone(),
      velocity: new THREE.Vector3(),
      buffer,
      isPlaying: false,
      startTime: 0
    };
    
    this.sources.set(id, source);
    return source;
  }
  
  /**
   * Play audio source
   */
  public playSource(id: string, delay: number = 0): void {
    const source = this.sources.get(id);
    if (!source || !source.buffer) return;
    
    // Stop existing
    if (source.node) {
      source.node.stop();
      source.node.disconnect();
    }
    
    // Create new source node
    source.node = this.audioContext.createBufferSource();
    source.node.buffer = source.buffer;
    source.node.loop = source.config.loop;
    source.node.connect(source.gain);
    
    source.node.start(this.audioContext.currentTime + delay);
    source.isPlaying = true;
    source.startTime = this.audioContext.currentTime + delay;
    
    source.node.onended = () => {
      source.isPlaying = false;
    };
  }
  
  /**
   * Stop audio source
   */
  public stopSource(id: string, fadeTime: number = 0): void {
    const source = this.sources.get(id);
    if (!source || !source.node) return;
    
    if (fadeTime > 0) {
      const now = this.audioContext.currentTime;
      source.gain.gain.setValueAtTime(source.gain.gain.value, now);
      source.gain.gain.linearRampToValueAtTime(0, now + fadeTime);
      
      setTimeout(() => {
        source.node?.stop();
        source.isPlaying = false;
      }, fadeTime * 1000);
    } else {
      source.node.stop();
      source.isPlaying = false;
    }
  }
  
  /**
   * Update source position
   */
  public updateSourcePosition(
    id: string,
    position: THREE.Vector3,
    velocity?: THREE.Vector3
  ): void {
    const source = this.sources.get(id);
    if (!source || !source.panner) return;
    
    source.position.copy(position);
    source.panner.positionX.value = position.x;
    source.panner.positionY.value = position.y;
    source.panner.positionZ.value = position.z;
    
    if (velocity) {
      source.velocity.copy(velocity);
    }
  }
  
  /**
   * Set source volume
   */
  public setSourceVolume(id: string, volume: number, fadeTime: number = 0): void {
    const source = this.sources.get(id);
    if (!source) return;
    
    if (fadeTime > 0) {
      const now = this.audioContext.currentTime;
      source.gain.gain.setValueAtTime(source.gain.gain.value, now);
      source.gain.gain.linearRampToValueAtTime(volume, now + fadeTime);
    } else {
      source.gain.gain.value = volume;
    }
  }
  
  /**
   * Update listener position
   */
  public updateListener(
    position: THREE.Vector3,
    orientation: THREE.Quaternion,
    velocity?: THREE.Vector3
  ): void {
    this.listenerPosition.copy(position);
    this.listenerOrientation.copy(orientation);
    
    if (velocity) {
      this.listenerVelocity.copy(velocity);
    }
    
    this.updateListenerOrientation();
    this.updateReverbZones();
  }
  
  private updateListenerOrientation(): void {
    const listener = this.audioContext.listener;
    
    // Forward vector
    const forward = new THREE.Vector3(0, 0, -1)
      .applyQuaternion(this.listenerOrientation);
    
    // Up vector
    const up = new THREE.Vector3(0, 1, 0)
      .applyQuaternion(this.listenerOrientation);
    
    if (listener.positionX) {
      listener.positionX.value = this.listenerPosition.x;
      listener.positionY.value = this.listenerPosition.y;
      listener.positionZ.value = this.listenerPosition.z;
      
      listener.forwardX.value = forward.x;
      listener.forwardY.value = forward.y;
      listener.forwardZ.value = forward.z;
      
      listener.upX.value = up.x;
      listener.upY.value = up.y;
      listener.upZ.value = up.z;
    } else {
      // Legacy API
      listener.setPosition(
        this.listenerPosition.x,
        this.listenerPosition.y,
        this.listenerPosition.z
      );
      listener.setOrientation(
        forward.x, forward.y, forward.z,
        up.x, up.y, up.z
      );
    }
  }
  
  /**
   * Add reverb zone
   */
  public addReverbZone(zone: ReverbZone): void {
    this.reverbZones.set(zone.id, zone);
  }
  
  /**
   * Remove reverb zone
   */
  public removeReverbZone(id: string): void {
    this.reverbZones.delete(id);
  }
  
  private updateReverbZones(): void {
    let activeZone: ReverbZone | null = null;
    let highestPriority = -1;
    
    for (const zone of this.reverbZones.values()) {
      // Check if listener is inside zone
      const box = new THREE.Box3(
        zone.position.clone().sub(zone.size.clone().multiplyScalar(0.5)),
        zone.position.clone().add(zone.size.clone().multiplyScalar(0.5))
      );
      
      if (box.containsPoint(this.listenerPosition)) {
        if (zone.priority > highestPriority) {
          highestPriority = zone.priority;
          activeZone = zone;
        }
      }
    }
    
    if (activeZone) {
      this.reverb.applyPreset(activeZone.preset);
      this.reverb.setMix(activeZone.wetLevel, activeZone.dryLevel);
    } else {
      this.reverb.applyPreset('outdoor');
    }
  }
  
  /**
   * Create ambience layer
   */
  public createAmbienceLayer(id: string): void {
    const gain = this.audioContext.createGain();
    gain.gain.value = 0;
    gain.connect(this.masterGain);
    
    this.ambienceLayers.set(id, {
      id,
      sources: [],
      currentWeight: 0,
      targetWeight: 0,
      gain
    });
  }
  
  /**
   * Add sound to ambience layer
   */
  public addAmbienceSound(
    layerId: string,
    buffer: AudioBuffer,
    weight: number
  ): void {
    const layer = this.ambienceLayers.get(layerId);
    if (!layer) return;
    
    layer.sources.push({ buffer, weight });
  }
  
  /**
   * Set ambience layer weight
   */
  public setAmbienceWeight(layerId: string, weight: number): void {
    const layer = this.ambienceLayers.get(layerId);
    if (!layer) return;
    
    layer.targetWeight = weight;
  }
  
  /**
   * Set master volume
   */
  public setMasterVolume(volume: number): void {
    this.masterGain.gain.value = volume;
  }
  
  /**
   * Get music crossfader
   */
  public getMusicCrossfader(): MusicCrossfader {
    return this.crossfader;
  }
  
  /**
   * Get audio context
   */
  public getAudioContext(): AudioContext {
    return this.audioContext;
  }
  
  /**
   * Remove source
   */
  public removeSource(id: string): void {
    const source = this.sources.get(id);
    if (source) {
      if (source.node) {
        source.node.stop();
        source.node.disconnect();
      }
      source.gain.disconnect();
      source.panner?.disconnect();
      this.sources.delete(id);
    }
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    for (const id of this.sources.keys()) {
      this.removeSource(id);
    }
    
    this.reverb.dispose();
    this.crossfader.dispose();
    this.compressor.disconnect();
    this.masterGain.disconnect();
    this.audioContext.close();
  }
}
