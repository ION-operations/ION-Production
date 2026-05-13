/**
 * Complete Weather System
 * Rain, snow, wind, lightning, fog, wet surfaces
 * 
 * Based on research from:
 * - Red Dead Redemption 2
 * - Horizon Forbidden West
 * - Microsoft Flight Simulator
 */

import * as THREE from 'three';

// ============================================
// TYPES & CONFIG
// ============================================

export type WeatherType = 'clear' | 'cloudy' | 'rain' | 'storm' | 'snow' | 'blizzard' | 'fog';

export interface WeatherState {
  type: WeatherType;
  intensity: number;       // 0-1
  windSpeed: number;       // m/s
  windDirection: THREE.Vector3;
  temperature: number;     // Celsius
  visibility: number;      // meters
  cloudCoverage: number;   // 0-1
  precipitationRate: number;
}

export interface WeatherConfig {
  maxRaindrops: number;
  maxSnowflakes: number;
  windFieldResolution: number;
  lightningFrequency: number;  // per minute during storms
  fogDensity: number;
  transitionDuration: number;  // seconds
}

export const DEFAULT_WEATHER_CONFIG: WeatherConfig = {
  maxRaindrops: 50000,
  maxSnowflakes: 30000,
  windFieldResolution: 32,
  lightningFrequency: 3,
  fogDensity: 0.01,
  transitionDuration: 60
};

export const WEATHER_PRESETS: Record<WeatherType, Partial<WeatherState>> = {
  clear: {
    intensity: 0,
    windSpeed: 2,
    visibility: 10000,
    cloudCoverage: 0.1,
    precipitationRate: 0
  },
  cloudy: {
    intensity: 0,
    windSpeed: 5,
    visibility: 8000,
    cloudCoverage: 0.7,
    precipitationRate: 0
  },
  rain: {
    intensity: 0.5,
    windSpeed: 8,
    visibility: 3000,
    cloudCoverage: 0.9,
    precipitationRate: 10
  },
  storm: {
    intensity: 1.0,
    windSpeed: 20,
    visibility: 1000,
    cloudCoverage: 1.0,
    precipitationRate: 30
  },
  snow: {
    intensity: 0.5,
    windSpeed: 5,
    visibility: 2000,
    cloudCoverage: 0.8,
    precipitationRate: 5,
    temperature: -5
  },
  blizzard: {
    intensity: 1.0,
    windSpeed: 25,
    visibility: 200,
    cloudCoverage: 1.0,
    precipitationRate: 20,
    temperature: -15
  },
  fog: {
    intensity: 0.8,
    windSpeed: 1,
    visibility: 100,
    cloudCoverage: 0.3,
    precipitationRate: 0
  }
};

// ============================================
// RAIN SYSTEM
// ============================================

export class RainSystem {
  private geometry: THREE.BufferGeometry;
  private material: THREE.ShaderMaterial;
  public points: THREE.Points;
  
  private positions: Float32Array;
  private velocities: Float32Array;
  private ages: Float32Array;
  private count: number;
  
  private bounds: THREE.Box3;
  private active: boolean = false;

  constructor(count: number, bounds: THREE.Box3) {
    this.count = count;
    this.bounds = bounds;
    
    this.positions = new Float32Array(count * 3);
    this.velocities = new Float32Array(count * 3);
    this.ages = new Float32Array(count);
    
    this.initializeDrops();
    
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.geometry.setAttribute('age', new THREE.BufferAttribute(this.ages, 1));
    
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uIntensity: { value: 0 },
        uWindOffset: { value: new THREE.Vector2() },
        uColor: { value: new THREE.Color(0.7, 0.8, 0.9) }
      },
      vertexShader: `
        attribute float age;
        varying float vAge;
        varying float vStreak;
        uniform float uTime;
        uniform vec2 uWindOffset;
        
        void main() {
          vAge = age;
          
          vec3 pos = position;
          
          // Streak based on fall speed
          vStreak = 0.5 + age * 0.5;
          
          vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
          gl_Position = projectionMatrix * mvPosition;
          
          // Size based on distance
          gl_PointSize = 2.0 * (300.0 / -mvPosition.z);
        }
      `,
      fragmentShader: `
        uniform vec3 uColor;
        uniform float uIntensity;
        varying float vAge;
        varying float vStreak;
        
        void main() {
          // Elongated raindrop shape
          vec2 uv = gl_PointCoord * 2.0 - 1.0;
          float streak = 1.0 - smoothstep(0.0, 0.3, abs(uv.x));
          streak *= 1.0 - smoothstep(0.0, 1.0, abs(uv.y));
          
          if (streak < 0.1) discard;
          
          gl_FragColor = vec4(uColor, streak * uIntensity * 0.6);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
    
    this.points = new THREE.Points(this.geometry, this.material);
    this.points.frustumCulled = false;
  }

  private initializeDrops(): void {
    const size = this.bounds.getSize(new THREE.Vector3());
    const center = this.bounds.getCenter(new THREE.Vector3());
    
    for (let i = 0; i < this.count; i++) {
      const i3 = i * 3;
      
      this.positions[i3] = center.x + (Math.random() - 0.5) * size.x;
      this.positions[i3 + 1] = center.y + Math.random() * size.y;
      this.positions[i3 + 2] = center.z + (Math.random() - 0.5) * size.z;
      
      // Fall velocity (8-12 m/s)
      this.velocities[i3] = 0;
      this.velocities[i3 + 1] = -(8 + Math.random() * 4);
      this.velocities[i3 + 2] = 0;
      
      this.ages[i] = Math.random();
    }
  }

  public update(dt: number, wind: THREE.Vector3, intensity: number): void {
    if (intensity <= 0) {
      this.points.visible = false;
      return;
    }
    
    this.points.visible = true;
    this.material.uniforms.uIntensity.value = intensity;
    this.material.uniforms.uWindOffset.value.set(wind.x * 0.1, wind.z * 0.1);
    
    const size = this.bounds.getSize(new THREE.Vector3());
    const center = this.bounds.getCenter(new THREE.Vector3());
    
    for (let i = 0; i < this.count; i++) {
      const i3 = i * 3;
      
      // Apply wind
      this.velocities[i3] = wind.x * 0.5;
      this.velocities[i3 + 2] = wind.z * 0.5;
      
      // Update position
      this.positions[i3] += this.velocities[i3] * dt;
      this.positions[i3 + 1] += this.velocities[i3 + 1] * dt;
      this.positions[i3 + 2] += this.velocities[i3 + 2] * dt;
      
      // Respawn if below ground or out of bounds
      if (this.positions[i3 + 1] < this.bounds.min.y) {
        this.positions[i3] = center.x + (Math.random() - 0.5) * size.x;
        this.positions[i3 + 1] = this.bounds.max.y;
        this.positions[i3 + 2] = center.z + (Math.random() - 0.5) * size.z;
        this.ages[i] = Math.random();
      }
    }
    
    this.geometry.attributes.position.needsUpdate = true;
    this.geometry.attributes.age.needsUpdate = true;
  }

  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

// ============================================
// SNOW SYSTEM
// ============================================

export class SnowSystem {
  private geometry: THREE.BufferGeometry;
  private material: THREE.ShaderMaterial;
  public points: THREE.Points;
  
  private positions: Float32Array;
  private velocities: Float32Array;
  private sizes: Float32Array;
  private count: number;
  
  private bounds: THREE.Box3;
  private time: number = 0;

  constructor(count: number, bounds: THREE.Box3) {
    this.count = count;
    this.bounds = bounds;
    
    this.positions = new Float32Array(count * 3);
    this.velocities = new Float32Array(count * 3);
    this.sizes = new Float32Array(count);
    
    this.initializeFlakes();
    
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(this.sizes, 1));
    
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uIntensity: { value: 0 },
        uTexture: { value: this.createSnowflakeTexture() }
      },
      vertexShader: `
        attribute float size;
        varying float vSize;
        uniform float uTime;
        
        void main() {
          vSize = size;
          
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          gl_Position = projectionMatrix * mvPosition;
          gl_PointSize = size * (200.0 / -mvPosition.z);
        }
      `,
      fragmentShader: `
        uniform sampler2D uTexture;
        uniform float uIntensity;
        varying float vSize;
        
        void main() {
          vec4 texColor = texture2D(uTexture, gl_PointCoord);
          if (texColor.a < 0.1) discard;
          
          gl_FragColor = vec4(1.0, 1.0, 1.0, texColor.a * uIntensity * 0.8);
        }
      `,
      transparent: true,
      depthWrite: false
    });
    
    this.points = new THREE.Points(this.geometry, this.material);
    this.points.frustumCulled = false;
  }

  private createSnowflakeTexture(): THREE.Texture {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d')!;
    
    // Radial gradient for soft snowflake
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    gradient.addColorStop(0.3, 'rgba(255, 255, 255, 0.8)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 64, 64);
    
    const texture = new THREE.CanvasTexture(canvas);
    return texture;
  }

  private initializeFlakes(): void {
    const size = this.bounds.getSize(new THREE.Vector3());
    const center = this.bounds.getCenter(new THREE.Vector3());
    
    for (let i = 0; i < this.count; i++) {
      const i3 = i * 3;
      
      this.positions[i3] = center.x + (Math.random() - 0.5) * size.x;
      this.positions[i3 + 1] = center.y + Math.random() * size.y;
      this.positions[i3 + 2] = center.z + (Math.random() - 0.5) * size.z;
      
      // Slow fall velocity
      this.velocities[i3] = 0;
      this.velocities[i3 + 1] = -(0.5 + Math.random() * 1);
      this.velocities[i3 + 2] = 0;
      
      this.sizes[i] = 2 + Math.random() * 4;
    }
  }

  public update(dt: number, wind: THREE.Vector3, intensity: number): void {
    if (intensity <= 0) {
      this.points.visible = false;
      return;
    }
    
    this.points.visible = true;
    this.time += dt;
    this.material.uniforms.uTime.value = this.time;
    this.material.uniforms.uIntensity.value = intensity;
    
    const size = this.bounds.getSize(new THREE.Vector3());
    const center = this.bounds.getCenter(new THREE.Vector3());
    
    for (let i = 0; i < this.count; i++) {
      const i3 = i * 3;
      
      // Swirling motion (curl noise approximation)
      const swirl = Math.sin(this.time * 2 + this.positions[i3] * 0.1) * 0.5;
      const sway = Math.cos(this.time * 1.5 + this.positions[i3 + 2] * 0.1) * 0.3;
      
      // Apply wind + swirl
      this.velocities[i3] = wind.x * 0.3 + swirl;
      this.velocities[i3 + 2] = wind.z * 0.3 + sway;
      
      // Update position
      this.positions[i3] += this.velocities[i3] * dt;
      this.positions[i3 + 1] += this.velocities[i3 + 1] * dt;
      this.positions[i3 + 2] += this.velocities[i3 + 2] * dt;
      
      // Respawn
      if (this.positions[i3 + 1] < this.bounds.min.y) {
        this.positions[i3] = center.x + (Math.random() - 0.5) * size.x;
        this.positions[i3 + 1] = this.bounds.max.y;
        this.positions[i3 + 2] = center.z + (Math.random() - 0.5) * size.z;
      }
    }
    
    this.geometry.attributes.position.needsUpdate = true;
  }

  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

// ============================================
// LIGHTNING SYSTEM
// ============================================

export class LightningSystem {
  public group: THREE.Group;
  private bolts: THREE.Line[] = [];
  private ambientLight: THREE.AmbientLight;
  private flashLight: THREE.PointLight;
  
  private lastStrikeTime: number = 0;
  private flashIntensity: number = 0;

  constructor() {
    this.group = new THREE.Group();
    
    this.ambientLight = new THREE.AmbientLight(0xffffff, 0);
    this.group.add(this.ambientLight);
    
    this.flashLight = new THREE.PointLight(0xaaccff, 0, 5000);
    this.flashLight.position.set(0, 500, 0);
    this.group.add(this.flashLight);
  }

  private generateBolt(start: THREE.Vector3, end: THREE.Vector3, depth: number = 0): THREE.Vector3[] {
    if (depth >= 5) {
      return [start, end];
    }
    
    const mid = new THREE.Vector3().lerpVectors(start, end, 0.5);
    const length = start.distanceTo(end);
    
    // Random offset perpendicular to bolt
    const dir = new THREE.Vector3().subVectors(end, start).normalize();
    const perp = new THREE.Vector3(-dir.z, 0, dir.x);
    const offset = (Math.random() - 0.5) * length * 0.3;
    mid.addScaledVector(perp, offset);
    mid.y += (Math.random() - 0.5) * length * 0.1;
    
    const left = this.generateBolt(start, mid, depth + 1);
    const right = this.generateBolt(mid, end, depth + 1);
    
    return [...left.slice(0, -1), ...right];
  }

  public strike(position: THREE.Vector3): void {
    // Generate bolt from sky to ground
    const start = new THREE.Vector3(
      position.x + (Math.random() - 0.5) * 100,
      500,
      position.z + (Math.random() - 0.5) * 100
    );
    const end = position.clone();
    
    const points = this.generateBolt(start, end);
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    
    const material = new THREE.LineBasicMaterial({
      color: 0xaaddff,
      linewidth: 2,
      transparent: true,
      opacity: 1
    });
    
    const bolt = new THREE.Line(geometry, material);
    this.bolts.push(bolt);
    this.group.add(bolt);
    
    // Create branches
    for (let i = 0; i < 3; i++) {
      if (Math.random() > 0.5) {
        const branchStart = points[Math.floor(Math.random() * points.length * 0.5)];
        const branchEnd = branchStart.clone().add(
          new THREE.Vector3(
            (Math.random() - 0.5) * 100,
            -50 - Math.random() * 100,
            (Math.random() - 0.5) * 100
          )
        );
        
        const branchPoints = this.generateBolt(branchStart, branchEnd, 2);
        const branchGeometry = new THREE.BufferGeometry().setFromPoints(branchPoints);
        const branchMaterial = new THREE.LineBasicMaterial({
          color: 0xaaddff,
          linewidth: 1,
          transparent: true,
          opacity: 0.7
        });
        
        const branch = new THREE.Line(branchGeometry, branchMaterial);
        this.bolts.push(branch);
        this.group.add(branch);
      }
    }
    
    // Flash
    this.flashIntensity = 3;
    this.flashLight.position.copy(start);
    this.lastStrikeTime = performance.now();
  }

  public update(dt: number): void {
    // Fade flash
    this.flashIntensity *= 0.9;
    this.flashLight.intensity = this.flashIntensity;
    this.ambientLight.intensity = this.flashIntensity * 0.3;
    
    // Fade and remove bolts
    for (let i = this.bolts.length - 1; i >= 0; i--) {
      const bolt = this.bolts[i];
      const material = bolt.material as THREE.LineBasicMaterial;
      material.opacity *= 0.85;
      
      if (material.opacity < 0.01) {
        this.group.remove(bolt);
        bolt.geometry.dispose();
        material.dispose();
        this.bolts.splice(i, 1);
      }
    }
  }

  public dispose(): void {
    for (const bolt of this.bolts) {
      bolt.geometry.dispose();
      (bolt.material as THREE.Material).dispose();
    }
  }
}

// ============================================
// FOG SYSTEM
// ============================================

export class FogSystem {
  private scene: THREE.Scene;
  private fog: THREE.FogExp2 | null = null;

  constructor(scene: THREE.Scene) {
    this.scene = scene;
  }

  public update(visibility: number, color: THREE.Color): void {
    const density = 1 / Math.max(visibility, 10);
    
    if (!this.fog) {
      this.fog = new THREE.FogExp2(color, density);
      this.scene.fog = this.fog;
    } else {
      this.fog.density = density;
      this.fog.color.copy(color);
    }
  }

  public disable(): void {
    this.scene.fog = null;
  }
}

// ============================================
// MAIN WEATHER SYSTEM
// ============================================

export class WeatherSystem {
  private config: WeatherConfig;
  private currentState: WeatherState;
  private targetState: WeatherState;
  private transitionProgress: number = 1;
  
  // Subsystems
  private rain: RainSystem;
  private snow: SnowSystem;
  private lightning: LightningSystem;
  private fog: FogSystem;
  
  // Wind
  private windDirection = new THREE.Vector3(1, 0, 0);
  private windSpeed: number = 0;
  
  // Time
  private time: number = 0;
  private lastLightningTime: number = 0;
  
  public group: THREE.Group;

  constructor(
    scene: THREE.Scene,
    bounds: THREE.Box3,
    config: Partial<WeatherConfig> = {}
  ) {
    this.config = { ...DEFAULT_WEATHER_CONFIG, ...config };
    
    this.currentState = {
      type: 'clear',
      intensity: 0,
      windSpeed: 2,
      windDirection: new THREE.Vector3(1, 0, 0),
      temperature: 20,
      visibility: 10000,
      cloudCoverage: 0.1,
      precipitationRate: 0
    };
    this.targetState = { ...this.currentState };
    
    this.group = new THREE.Group();
    
    // Initialize subsystems
    this.rain = new RainSystem(this.config.maxRaindrops, bounds);
    this.group.add(this.rain.points);
    
    this.snow = new SnowSystem(this.config.maxSnowflakes, bounds);
    this.group.add(this.snow.points);
    
    this.lightning = new LightningSystem();
    this.group.add(this.lightning.group);
    
    this.fog = new FogSystem(scene);
  }

  /**
   * Transition to new weather
   */
  public setWeather(type: WeatherType, duration?: number): void {
    const preset = WEATHER_PRESETS[type];
    
    this.targetState = {
      type,
      intensity: preset.intensity ?? 0,
      windSpeed: preset.windSpeed ?? 5,
      windDirection: this.currentState.windDirection.clone(),
      temperature: preset.temperature ?? 15,
      visibility: preset.visibility ?? 5000,
      cloudCoverage: preset.cloudCoverage ?? 0.5,
      precipitationRate: preset.precipitationRate ?? 0
    };
    
    this.config.transitionDuration = duration ?? this.config.transitionDuration;
    this.transitionProgress = 0;
  }

  /**
   * Update weather system
   */
  public update(dt: number, cameraPosition?: THREE.Vector3): void {
    this.time += dt;
    
    // Interpolate state transition
    if (this.transitionProgress < 1) {
      this.transitionProgress += dt / this.config.transitionDuration;
      this.transitionProgress = Math.min(1, this.transitionProgress);
      
      this.currentState.intensity = THREE.MathUtils.lerp(
        this.currentState.intensity,
        this.targetState.intensity,
        this.transitionProgress
      );
      this.currentState.windSpeed = THREE.MathUtils.lerp(
        this.currentState.windSpeed,
        this.targetState.windSpeed,
        this.transitionProgress
      );
      this.currentState.visibility = THREE.MathUtils.lerp(
        this.currentState.visibility,
        this.targetState.visibility,
        this.transitionProgress
      );
      
      if (this.transitionProgress >= 1) {
        this.currentState.type = this.targetState.type;
      }
    }
    
    // Update wind with turbulence
    const turbulence = Math.sin(this.time * 0.5) * 0.3;
    const wind = this.currentState.windDirection.clone()
      .multiplyScalar(this.currentState.windSpeed * (1 + turbulence));
    
    // Update subsystems based on weather type
    const isRaining = this.currentState.type === 'rain' || this.currentState.type === 'storm';
    const isSnowing = this.currentState.type === 'snow' || this.currentState.type === 'blizzard';
    
    this.rain.update(dt, wind, isRaining ? this.currentState.intensity : 0);
    this.snow.update(dt, wind, isSnowing ? this.currentState.intensity : 0);
    
    // Lightning during storms
    if (this.currentState.type === 'storm') {
      const lightningInterval = 60 / this.config.lightningFrequency;
      if (this.time - this.lastLightningTime > lightningInterval + Math.random() * lightningInterval) {
        const strikePos = cameraPosition 
          ? cameraPosition.clone().add(new THREE.Vector3(
              (Math.random() - 0.5) * 500,
              0,
              (Math.random() - 0.5) * 500
            ))
          : new THREE.Vector3();
        
        this.lightning.strike(strikePos);
        this.lastLightningTime = this.time;
      }
    }
    this.lightning.update(dt);
    
    // Fog
    const fogColor = new THREE.Color(0.7, 0.7, 0.75);
    this.fog.update(this.currentState.visibility, fogColor);
    
    // Center particles around camera
    if (cameraPosition) {
      this.group.position.copy(cameraPosition);
    }
  }

  public getCurrentState(): WeatherState {
    return { ...this.currentState };
  }

  public dispose(): void {
    this.rain.dispose();
    this.snow.dispose();
    this.lightning.dispose();
    this.fog.disable();
  }
}

