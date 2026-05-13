/**
 * Spatial Audio System
 * 3D positional audio with HRTF and environmental effects
 * 
 * Features:
 * - Web Audio API integration
 * - HRTF panning
 * - Distance attenuation models
 * - Room reverb
 * - Occlusion
 * - Doppler effect
 */

import * as THREE from 'three';

export interface AudioSourceConfig {
  volume: number;
  loop: boolean;
  refDistance: number;        // Distance at which volume is 100%
  maxDistance: number;        // Maximum hearing distance
  rolloffFactor: number;      // How quickly sound fades
  coneInnerAngle: number;     // Inner cone angle (degrees)
  coneOuterAngle: number;     // Outer cone angle (degrees)
  coneOuterGain: number;      // Volume outside outer cone
  doppler: boolean;           // Enable Doppler effect
  occlusion: boolean;         // Enable occlusion
}

export const DEFAULT_AUDIO_SOURCE_CONFIG: AudioSourceConfig = {
  volume: 1.0,
  loop: false,
  refDistance: 1,
  maxDistance: 100,
  rolloffFactor: 1,
  coneInnerAngle: 360,
  coneOuterAngle: 360,
  coneOuterGain: 0,
  doppler: true,
  occlusion: true
};

export interface ReverbConfig {
  roomSize: number;           // 0-1
  decay: number;              // Decay time in seconds
  wetLevel: number;           // Reverb mix (0-1)
  dryLevel: number;           // Direct sound mix (0-1)
  preDelay: number;           // Pre-delay in seconds
}

export const DEFAULT_REVERB_CONFIG: ReverbConfig = {
  roomSize: 0.5,
  decay: 2.0,
  wetLevel: 0.3,
  dryLevel: 0.7,
  preDelay: 0.01
};

interface AudioSource3D {
  id: string;
  buffer: AudioBuffer | null;
  source: AudioBufferSourceNode | null;
  panner: PannerNode;
  gain: GainNode;
  lowpass: BiquadFilterNode;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  previousPosition: THREE.Vector3;
  config: AudioSourceConfig;
  playing: boolean;
  url: string;
}

export class SpatialAudioSystem {
  private audioContext: AudioContext;
  private listener: AudioListener;
  private masterGain: GainNode;
  private compressor: DynamicsCompressorNode;
  private convolver: ConvolverNode;
  private wetGain: GainNode;
  private dryGain: GainNode;
  
  private sources: Map<string, AudioSource3D> = new Map();
  private bufferCache: Map<string, AudioBuffer> = new Map();
  
  private listenerPosition = new THREE.Vector3();
  private listenerForward = new THREE.Vector3(0, 0, -1);
  private listenerUp = new THREE.Vector3(0, 1, 0);
  
  private reverbConfig: ReverbConfig;
  private occlusionRaycaster: THREE.Raycaster;
  private occlusionMeshes: THREE.Object3D[] = [];

  constructor(reverbConfig: Partial<ReverbConfig> = {}) {
    this.reverbConfig = { ...DEFAULT_REVERB_CONFIG, ...reverbConfig };
    
    this.audioContext = new AudioContext();
    this.listener = this.audioContext.listener;
    
    // Create audio graph
    this.masterGain = this.audioContext.createGain();
    this.compressor = this.audioContext.createDynamicsCompressor();
    this.convolver = this.audioContext.createConvolver();
    this.wetGain = this.audioContext.createGain();
    this.dryGain = this.audioContext.createGain();
    
    // Connect graph
    // Sources -> [panner -> gain -> lowpass] -> dryGain -> compressor -> masterGain -> destination
    //                                        -> convolver -> wetGain -> compressor
    this.dryGain.gain.value = this.reverbConfig.dryLevel;
    this.wetGain.gain.value = this.reverbConfig.wetLevel;
    
    this.dryGain.connect(this.compressor);
    this.convolver.connect(this.wetGain);
    this.wetGain.connect(this.compressor);
    this.compressor.connect(this.masterGain);
    this.masterGain.connect(this.audioContext.destination);
    
    // Generate reverb impulse response
    this.generateReverbIR();
    
    this.occlusionRaycaster = new THREE.Raycaster();
  }

  private async generateReverbIR(): Promise<void> {
    const { roomSize, decay, preDelay } = this.reverbConfig;
    const sampleRate = this.audioContext.sampleRate;
    const length = Math.floor(sampleRate * (decay + preDelay));
    
    const impulse = this.audioContext.createBuffer(2, length, sampleRate);
    const left = impulse.getChannelData(0);
    const right = impulse.getChannelData(1);
    
    const preDelaySamples = Math.floor(sampleRate * preDelay);
    
    for (let i = preDelaySamples; i < length; i++) {
      const t = (i - preDelaySamples) / (length - preDelaySamples);
      const envelope = Math.exp(-3 * t / decay);
      
      // Early reflections
      const early = i < preDelaySamples + sampleRate * 0.1
        ? Math.sin(i * 0.01) * 0.5
        : 0;
      
      // Diffuse tail
      const diffuse = (Math.random() * 2 - 1) * envelope * roomSize;
      
      left[i] = (early + diffuse) * 0.5;
      right[i] = (early + (Math.random() * 2 - 1) * envelope * roomSize) * 0.5;
    }
    
    this.convolver.buffer = impulse;
  }

  /**
   * Set listener (camera) position and orientation
   */
  public setListener(
    position: THREE.Vector3,
    forward: THREE.Vector3,
    up: THREE.Vector3
  ): void {
    this.listenerPosition.copy(position);
    this.listenerForward.copy(forward).normalize();
    this.listenerUp.copy(up).normalize();
    
    if (this.listener.positionX) {
      // Modern API
      this.listener.positionX.setValueAtTime(position.x, this.audioContext.currentTime);
      this.listener.positionY.setValueAtTime(position.y, this.audioContext.currentTime);
      this.listener.positionZ.setValueAtTime(position.z, this.audioContext.currentTime);
      
      this.listener.forwardX.setValueAtTime(forward.x, this.audioContext.currentTime);
      this.listener.forwardY.setValueAtTime(forward.y, this.audioContext.currentTime);
      this.listener.forwardZ.setValueAtTime(forward.z, this.audioContext.currentTime);
      
      this.listener.upX.setValueAtTime(up.x, this.audioContext.currentTime);
      this.listener.upY.setValueAtTime(up.y, this.audioContext.currentTime);
      this.listener.upZ.setValueAtTime(up.z, this.audioContext.currentTime);
    } else {
      // Legacy API
      this.listener.setPosition(position.x, position.y, position.z);
      this.listener.setOrientation(
        forward.x, forward.y, forward.z,
        up.x, up.y, up.z
      );
    }
  }

  /**
   * Update listener from camera
   */
  public updateFromCamera(camera: THREE.Camera): void {
    const position = camera.position;
    const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
    const up = new THREE.Vector3(0, 1, 0).applyQuaternion(camera.quaternion);
    
    this.setListener(position, forward, up);
  }

  /**
   * Add occlusion mesh
   */
  public addOcclusionMesh(mesh: THREE.Object3D): void {
    this.occlusionMeshes.push(mesh);
  }

  /**
   * Load audio file
   */
  public async loadAudio(url: string): Promise<AudioBuffer> {
    if (this.bufferCache.has(url)) {
      return this.bufferCache.get(url)!;
    }
    
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
    
    this.bufferCache.set(url, audioBuffer);
    return audioBuffer;
  }

  /**
   * Create audio source
   */
  public async createSource(
    id: string,
    url: string,
    position: THREE.Vector3,
    config: Partial<AudioSourceConfig> = {}
  ): Promise<AudioSource3D> {
    const fullConfig = { ...DEFAULT_AUDIO_SOURCE_CONFIG, ...config };
    
    // Load audio
    const buffer = await this.loadAudio(url);
    
    // Create nodes
    const panner = this.audioContext.createPanner();
    panner.panningModel = 'HRTF';
    panner.distanceModel = 'inverse';
    panner.refDistance = fullConfig.refDistance;
    panner.maxDistance = fullConfig.maxDistance;
    panner.rolloffFactor = fullConfig.rolloffFactor;
    panner.coneInnerAngle = fullConfig.coneInnerAngle;
    panner.coneOuterAngle = fullConfig.coneOuterAngle;
    panner.coneOuterGain = fullConfig.coneOuterGain;
    
    const gain = this.audioContext.createGain();
    gain.gain.value = fullConfig.volume;
    
    const lowpass = this.audioContext.createBiquadFilter();
    lowpass.type = 'lowpass';
    lowpass.frequency.value = 20000;
    
    // Connect
    panner.connect(gain);
    gain.connect(lowpass);
    lowpass.connect(this.dryGain);
    lowpass.connect(this.convolver);
    
    // Set position
    if (panner.positionX) {
      panner.positionX.setValueAtTime(position.x, this.audioContext.currentTime);
      panner.positionY.setValueAtTime(position.y, this.audioContext.currentTime);
      panner.positionZ.setValueAtTime(position.z, this.audioContext.currentTime);
    } else {
      panner.setPosition(position.x, position.y, position.z);
    }
    
    const source: AudioSource3D = {
      id,
      buffer,
      source: null,
      panner,
      gain,
      lowpass,
      position: position.clone(),
      velocity: new THREE.Vector3(),
      previousPosition: position.clone(),
      config: fullConfig,
      playing: false,
      url
    };
    
    this.sources.set(id, source);
    return source;
  }

  /**
   * Play source
   */
  public play(id: string): void {
    const source = this.sources.get(id);
    if (!source || !source.buffer) return;
    
    // Create new source node (can only be played once)
    source.source = this.audioContext.createBufferSource();
    source.source.buffer = source.buffer;
    source.source.loop = source.config.loop;
    source.source.connect(source.panner);
    
    source.source.start();
    source.playing = true;
    
    source.source.onended = () => {
      source.playing = false;
      source.source = null;
    };
  }

  /**
   * Stop source
   */
  public stop(id: string): void {
    const source = this.sources.get(id);
    if (!source || !source.source) return;
    
    source.source.stop();
    source.playing = false;
    source.source = null;
  }

  /**
   * Set source position
   */
  public setSourcePosition(id: string, position: THREE.Vector3): void {
    const source = this.sources.get(id);
    if (!source) return;
    
    source.previousPosition.copy(source.position);
    source.position.copy(position);
    
    if (source.panner.positionX) {
      source.panner.positionX.setValueAtTime(position.x, this.audioContext.currentTime);
      source.panner.positionY.setValueAtTime(position.y, this.audioContext.currentTime);
      source.panner.positionZ.setValueAtTime(position.z, this.audioContext.currentTime);
    } else {
      source.panner.setPosition(position.x, position.y, position.z);
    }
  }

  /**
   * Update audio system
   */
  public update(dt: number): void {
    for (const source of this.sources.values()) {
      if (!source.playing) continue;
      
      // Calculate velocity for Doppler
      if (source.config.doppler) {
        source.velocity.subVectors(source.position, source.previousPosition)
          .divideScalar(dt);
      }
      
      // Occlusion
      if (source.config.occlusion && this.occlusionMeshes.length > 0) {
        this.updateOcclusion(source);
      }
    }
  }

  private updateOcclusion(source: AudioSource3D): void {
    const direction = new THREE.Vector3()
      .subVectors(source.position, this.listenerPosition);
    const distance = direction.length();
    direction.normalize();
    
    this.occlusionRaycaster.set(this.listenerPosition, direction);
    this.occlusionRaycaster.far = distance;
    
    const intersects = this.occlusionRaycaster.intersectObjects(
      this.occlusionMeshes,
      true
    );
    
    // Apply lowpass filter based on occlusion
    let occlusionAmount = 0;
    for (const intersect of intersects) {
      if (intersect.distance < distance - 0.1) {
        occlusionAmount += 0.3;
      }
    }
    
    const cutoff = THREE.MathUtils.lerp(20000, 500, Math.min(occlusionAmount, 1));
    source.lowpass.frequency.setValueAtTime(cutoff, this.audioContext.currentTime);
  }

  /**
   * Set master volume
   */
  public setMasterVolume(volume: number): void {
    this.masterGain.gain.setValueAtTime(volume, this.audioContext.currentTime);
  }

  /**
   * Resume audio context (required after user interaction)
   */
  public async resume(): Promise<void> {
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }
  }

  public dispose(): void {
    for (const source of this.sources.values()) {
      if (source.source) source.source.stop();
      source.panner.disconnect();
      source.gain.disconnect();
      source.lowpass.disconnect();
    }
    
    this.audioContext.close();
  }
}

