/**
 * Audio Visualization System
 * Real-time audio analysis and 3D visualization
 * 
 * Features:
 * - FFT frequency analysis
 * - Beat detection
 * - Waveform display
 * - 3D visualizers (bars, rings, particles)
 * - Audio-reactive materials
 */

import * as THREE from 'three';

export interface AudioConfig {
  fftSize: number;            // FFT size (power of 2: 32-32768)
  smoothingTimeConstant: number; // Smoothing (0-1)
  minDecibels: number;        // Min dB for visualization
  maxDecibels: number;        // Max dB for visualization
  beatThreshold: number;      // Threshold for beat detection
  beatDecay: number;          // Beat energy decay rate
}

export const DEFAULT_AUDIO_CONFIG: AudioConfig = {
  fftSize: 256,
  smoothingTimeConstant: 0.8,
  minDecibels: -90,
  maxDecibels: -10,
  beatThreshold: 1.5,
  beatDecay: 0.98
};

export class AudioAnalyzer {
  private config: AudioConfig;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private source: MediaElementAudioSourceNode | MediaStreamAudioSourceNode | null = null;
  
  // Frequency data
  private frequencyData: Uint8Array = new Uint8Array(0);
  private timeDomainData: Uint8Array = new Uint8Array(0);
  
  // Processed data
  private normalizedFrequency: Float32Array = new Float32Array(0);
  private bass: number = 0;
  private mid: number = 0;
  private treble: number = 0;
  private average: number = 0;
  
  // Beat detection
  private beatEnergy: number = 0;
  private beatHistory: number[] = [];
  private isBeat: boolean = false;
  private beatCount: number = 0;

  constructor(config: Partial<AudioConfig> = {}) {
    this.config = { ...DEFAULT_AUDIO_CONFIG, ...config };
  }

  /**
   * Initialize with audio element
   */
  public initWithAudioElement(audioElement: HTMLAudioElement): void {
    this.audioContext = new AudioContext();
    this.source = this.audioContext.createMediaElementSource(audioElement);
    this.setupAnalyser();
    this.source.connect(this.analyser!);
    this.analyser!.connect(this.audioContext.destination);
  }

  /**
   * Initialize with microphone
   */
  public async initWithMicrophone(): Promise<void> {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.audioContext = new AudioContext();
    this.source = this.audioContext.createMediaStreamSource(stream);
    this.setupAnalyser();
    this.source.connect(this.analyser!);
  }

  private setupAnalyser(): void {
    if (!this.audioContext) return;
    
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = this.config.fftSize;
    this.analyser.smoothingTimeConstant = this.config.smoothingTimeConstant;
    this.analyser.minDecibels = this.config.minDecibels;
    this.analyser.maxDecibels = this.config.maxDecibels;
    
    const bufferLength = this.analyser.frequencyBinCount;
    this.frequencyData = new Uint8Array(bufferLength);
    this.timeDomainData = new Uint8Array(bufferLength);
    this.normalizedFrequency = new Float32Array(bufferLength);
    this.beatHistory = new Array(60).fill(0);
  }

  /**
   * Update audio analysis
   */
  public update(): void {
    if (!this.analyser) return;

    // Get frequency data
    this.analyser.getByteFrequencyData(this.frequencyData);
    this.analyser.getByteTimeDomainData(this.timeDomainData);

    const binCount = this.analyser.frequencyBinCount;

    // Normalize frequency data
    let sum = 0;
    for (let i = 0; i < binCount; i++) {
      this.normalizedFrequency[i] = this.frequencyData[i] / 255;
      sum += this.normalizedFrequency[i];
    }
    this.average = sum / binCount;

    // Calculate bass, mid, treble
    const bassEnd = Math.floor(binCount * 0.1);
    const midEnd = Math.floor(binCount * 0.5);

    let bassSum = 0, midSum = 0, trebleSum = 0;
    for (let i = 0; i < binCount; i++) {
      if (i < bassEnd) {
        bassSum += this.normalizedFrequency[i];
      } else if (i < midEnd) {
        midSum += this.normalizedFrequency[i];
      } else {
        trebleSum += this.normalizedFrequency[i];
      }
    }

    this.bass = bassSum / bassEnd;
    this.mid = midSum / (midEnd - bassEnd);
    this.treble = trebleSum / (binCount - midEnd);

    // Beat detection
    this.detectBeat();
  }

  private detectBeat(): void {
    // Calculate current energy (weighted toward bass)
    const energy = this.bass * 2 + this.mid * 0.5;
    
    // Update history
    this.beatHistory.push(energy);
    if (this.beatHistory.length > 60) {
      this.beatHistory.shift();
    }

    // Calculate average energy
    const avgEnergy = this.beatHistory.reduce((a, b) => a + b, 0) / this.beatHistory.length;

    // Detect beat
    const prevBeat = this.isBeat;
    this.isBeat = energy > avgEnergy * this.config.beatThreshold;
    
    if (this.isBeat && !prevBeat) {
      this.beatCount++;
      this.beatEnergy = 1;
    }

    // Decay beat energy
    this.beatEnergy *= this.config.beatDecay;
  }

  // Getters
  public getFrequencyData(): Uint8Array { return this.frequencyData; }
  public getTimeDomainData(): Uint8Array { return this.timeDomainData; }
  public getNormalizedFrequency(): Float32Array { return this.normalizedFrequency; }
  public getBass(): number { return this.bass; }
  public getMid(): number { return this.mid; }
  public getTreble(): number { return this.treble; }
  public getAverage(): number { return this.average; }
  public getIsBeat(): boolean { return this.isBeat; }
  public getBeatEnergy(): number { return this.beatEnergy; }
  public getBeatCount(): number { return this.beatCount; }

  public dispose(): void {
    if (this.audioContext) {
      this.audioContext.close();
    }
  }
}

// ============================================
// VISUALIZERS
// ============================================

/**
 * Bar visualizer (frequency bars in a line or circle)
 */
export class BarVisualizer {
  public group: THREE.Group;
  private bars: THREE.Mesh[] = [];
  private config: {
    count: number;
    width: number;
    maxHeight: number;
    spacing: number;
    circular: boolean;
    radius: number;
  };

  constructor(config: Partial<{
    count: number;
    width: number;
    maxHeight: number;
    spacing: number;
    circular: boolean;
    radius: number;
  }> = {}) {
    this.config = {
      count: 64,
      width: 0.1,
      maxHeight: 5,
      spacing: 0.05,
      circular: false,
      radius: 3,
      ...config
    };

    this.group = new THREE.Group();
    this.createBars();
  }

  private createBars(): void {
    const geometry = new THREE.BoxGeometry(this.config.width, 1, this.config.width);
    
    for (let i = 0; i < this.config.count; i++) {
      const hue = i / this.config.count;
      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(hue, 0.8, 0.5),
        emissive: new THREE.Color().setHSL(hue, 0.8, 0.2),
        emissiveIntensity: 0.5
      });

      const bar = new THREE.Mesh(geometry, material);
      bar.geometry = geometry.clone(); // Each bar needs its own geometry for scaling

      if (this.config.circular) {
        const angle = (i / this.config.count) * Math.PI * 2;
        bar.position.x = Math.cos(angle) * this.config.radius;
        bar.position.z = Math.sin(angle) * this.config.radius;
        bar.rotation.y = -angle;
      } else {
        const totalWidth = this.config.count * (this.config.width + this.config.spacing);
        bar.position.x = (i / this.config.count) * totalWidth - totalWidth / 2;
      }

      this.bars.push(bar);
      this.group.add(bar);
    }
  }

  public update(frequencyData: Float32Array): void {
    const step = Math.floor(frequencyData.length / this.config.count);

    for (let i = 0; i < this.bars.length; i++) {
      const dataIndex = i * step;
      const value = frequencyData[dataIndex] || 0;
      const height = value * this.config.maxHeight + 0.01;

      this.bars[i].scale.y = height;
      this.bars[i].position.y = height / 2;

      // Update emissive based on intensity
      const material = this.bars[i].material as THREE.MeshStandardMaterial;
      material.emissiveIntensity = value * 2;
    }
  }

  public dispose(): void {
    for (const bar of this.bars) {
      bar.geometry.dispose();
      (bar.material as THREE.Material).dispose();
    }
  }
}

/**
 * Waveform visualizer (oscilloscope-style)
 */
export class WaveformVisualizer {
  public line: THREE.Line;
  private geometry: THREE.BufferGeometry;
  private positions: Float32Array;
  private width: number;
  private height: number;

  constructor(width: number = 10, height: number = 2, segments: number = 128) {
    this.width = width;
    this.height = height;

    this.positions = new Float32Array(segments * 3);
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));

    const material = new THREE.LineBasicMaterial({ 
      color: 0x00ff88,
      linewidth: 2
    });
    this.line = new THREE.Line(this.geometry, material);
  }

  public update(timeDomainData: Uint8Array): void {
    const segments = this.positions.length / 3;

    for (let i = 0; i < segments; i++) {
      const dataIndex = Math.floor((i / segments) * timeDomainData.length);
      const value = (timeDomainData[dataIndex] - 128) / 128;

      this.positions[i * 3] = (i / segments) * this.width - this.width / 2;
      this.positions[i * 3 + 1] = value * this.height;
      this.positions[i * 3 + 2] = 0;
    }

    this.geometry.attributes.position.needsUpdate = true;
  }

  public dispose(): void {
    this.geometry.dispose();
    (this.line.material as THREE.Material).dispose();
  }
}

/**
 * Particle visualizer (audio-reactive particles)
 */
export class ParticleVisualizer {
  public points: THREE.Points;
  private geometry: THREE.BufferGeometry;
  private positions: Float32Array;
  private velocities: Float32Array;
  private particleCount: number;
  private radius: number;

  constructor(particleCount: number = 1000, radius: number = 5) {
    this.particleCount = particleCount;
    this.radius = radius;

    this.positions = new Float32Array(particleCount * 3);
    this.velocities = new Float32Array(particleCount * 3);

    // Initialize particles in sphere
    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = Math.random() * radius;

      this.positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      this.positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      this.positions[i * 3 + 2] = r * Math.cos(phi);

      this.velocities[i * 3] = (Math.random() - 0.5) * 0.02;
      this.velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
      this.velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
    }

    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));

    const material = new THREE.PointsMaterial({
      size: 0.05,
      color: 0x00ffff,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    this.points = new THREE.Points(this.geometry, material);
  }

  public update(bass: number, beatEnergy: number): void {
    const expansionForce = bass * 0.1 + beatEnergy * 0.3;

    for (let i = 0; i < this.particleCount; i++) {
      const x = this.positions[i * 3];
      const y = this.positions[i * 3 + 1];
      const z = this.positions[i * 3 + 2];

      // Expand outward on beat
      const dist = Math.sqrt(x * x + y * y + z * z);
      if (dist > 0) {
        const nx = x / dist;
        const ny = y / dist;
        const nz = z / dist;

        this.velocities[i * 3] += nx * expansionForce * 0.1;
        this.velocities[i * 3 + 1] += ny * expansionForce * 0.1;
        this.velocities[i * 3 + 2] += nz * expansionForce * 0.1;
      }

      // Apply velocity
      this.positions[i * 3] += this.velocities[i * 3];
      this.positions[i * 3 + 1] += this.velocities[i * 3 + 1];
      this.positions[i * 3 + 2] += this.velocities[i * 3 + 2];

      // Pull back to center
      this.velocities[i * 3] -= x * 0.001;
      this.velocities[i * 3 + 1] -= y * 0.001;
      this.velocities[i * 3 + 2] -= z * 0.001;

      // Damping
      this.velocities[i * 3] *= 0.99;
      this.velocities[i * 3 + 1] *= 0.99;
      this.velocities[i * 3 + 2] *= 0.99;
    }

    this.geometry.attributes.position.needsUpdate = true;

    // Update material
    const material = this.points.material as THREE.PointsMaterial;
    material.size = 0.05 + beatEnergy * 0.1;
    material.color.setHSL(0.5 + bass * 0.2, 0.8, 0.5 + beatEnergy * 0.3);
  }

  public dispose(): void {
    this.geometry.dispose();
    (this.points.material as THREE.Material).dispose();
  }
}

