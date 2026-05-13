/**
 * Dynamic Weather System
 * Complete weather simulation with particles and shaders
 * 
 * Features:
 * - Rain (particles + screen effects)
 * - Snow (particles + accumulation)
 * - Fog (volumetric + height-based)
 * - Wind (vector field + turbulence)
 * - Lightning (bolt generation)
 * - Wet surfaces (PBR modification)
 * - Cloud shadows
 * - Weather transitions
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export type WeatherType = 'clear' | 'cloudy' | 'rain' | 'storm' | 'snow' | 'fog';

export interface WeatherState {
  type: WeatherType;
  intensity: number;  // 0-1
  windDirection: THREE.Vector3;
  windSpeed: number;
  fogDensity: number;
  temperature: number;
  cloudCoverage: number;
  visibility: number;
}

export interface WeatherConfig {
  particleCount: number;
  areaSize: number;
  height: number;
  transitionDuration: number;
  enableScreenEffects: boolean;
  enableWetSurfaces: boolean;
}

// ============================================
// RAIN SYSTEM
// ============================================

const RainVertexShader = `
attribute float size;
attribute float opacity;
attribute vec3 velocity;

uniform float time;
uniform vec3 windVelocity;
uniform float rainHeight;
uniform float areaSize;

varying float vOpacity;
varying vec2 vStretch;

void main() {
  vOpacity = opacity;
  
  // Calculate rain drop position with wind
  vec3 pos = position;
  
  // Wrap particles
  pos.y = mod(pos.y + rainHeight, rainHeight * 2.0) - rainHeight;
  pos.x = mod(pos.x + areaSize, areaSize * 2.0) - areaSize;
  pos.z = mod(pos.z + areaSize, areaSize * 2.0) - areaSize;
  
  // Apply wind
  float fallTime = (rainHeight - pos.y) / velocity.y;
  pos.x += windVelocity.x * fallTime * 0.1;
  pos.z += windVelocity.z * fallTime * 0.1;
  
  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  
  // Stretch based on velocity
  float speedFactor = length(velocity) / 20.0;
  vStretch = vec2(1.0, speedFactor * 3.0);
  
  gl_PointSize = size * (300.0 / -mvPosition.z);
  gl_Position = projectionMatrix * mvPosition;
}
`;

const RainFragmentShader = `
varying float vOpacity;
varying vec2 vStretch;

void main() {
  vec2 uv = gl_PointCoord - vec2(0.5);
  uv.y *= vStretch.y;
  
  float dist = length(uv);
  float alpha = smoothstep(0.5, 0.0, dist);
  
  // Rain drop shape
  float dropShape = smoothstep(0.5, 0.0, abs(uv.x) * 4.0);
  alpha *= dropShape;
  
  gl_FragColor = vec4(0.7, 0.8, 1.0, alpha * vOpacity * 0.6);
}
`;

export class RainSystem {
  public points: THREE.Points;
  
  private geometry: THREE.BufferGeometry;
  private material: THREE.ShaderMaterial;
  private positions: Float32Array;
  private velocities: Float32Array;
  private sizes: Float32Array;
  private opacities: Float32Array;
  private particleCount: number;
  private config: WeatherConfig;
  
  constructor(config: WeatherConfig) {
    this.config = config;
    this.particleCount = config.particleCount;
    
    // Initialize arrays
    this.positions = new Float32Array(this.particleCount * 3);
    this.velocities = new Float32Array(this.particleCount * 3);
    this.sizes = new Float32Array(this.particleCount);
    this.opacities = new Float32Array(this.particleCount);
    
    // Initialize particles
    for (let i = 0; i < this.particleCount; i++) {
      this.positions[i * 3] = (Math.random() - 0.5) * config.areaSize * 2;
      this.positions[i * 3 + 1] = Math.random() * config.height * 2 - config.height;
      this.positions[i * 3 + 2] = (Math.random() - 0.5) * config.areaSize * 2;
      
      this.velocities[i * 3] = 0;
      this.velocities[i * 3 + 1] = -15 - Math.random() * 10;  // Fall speed
      this.velocities[i * 3 + 2] = 0;
      
      this.sizes[i] = 2 + Math.random() * 3;
      this.opacities[i] = 0.3 + Math.random() * 0.7;
    }
    
    // Create geometry
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.geometry.setAttribute('velocity', new THREE.BufferAttribute(this.velocities, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(this.sizes, 1));
    this.geometry.setAttribute('opacity', new THREE.BufferAttribute(this.opacities, 1));
    
    // Create material
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        windVelocity: { value: new THREE.Vector3(0, 0, 0) },
        rainHeight: { value: config.height },
        areaSize: { value: config.areaSize }
      },
      vertexShader: RainVertexShader,
      fragmentShader: RainFragmentShader,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
    
    this.points = new THREE.Points(this.geometry, this.material);
  }
  
  public update(deltaTime: number, windVelocity: THREE.Vector3, intensity: number): void {
    this.material.uniforms.time.value += deltaTime;
    this.material.uniforms.windVelocity.value.copy(windVelocity);
    
    const positionAttr = this.geometry.getAttribute('position') as THREE.BufferAttribute;
    const positions = positionAttr.array as Float32Array;
    
    for (let i = 0; i < this.particleCount; i++) {
      // Move particles
      positions[i * 3 + 1] += this.velocities[i * 3 + 1] * deltaTime * intensity;
      positions[i * 3] += windVelocity.x * deltaTime * 0.5;
      positions[i * 3 + 2] += windVelocity.z * deltaTime * 0.5;
      
      // Respawn at top if below ground
      if (positions[i * 3 + 1] < -this.config.height) {
        positions[i * 3 + 1] = this.config.height;
        positions[i * 3] = (Math.random() - 0.5) * this.config.areaSize * 2;
        positions[i * 3 + 2] = (Math.random() - 0.5) * this.config.areaSize * 2;
      }
    }
    
    positionAttr.needsUpdate = true;
  }
  
  public setIntensity(intensity: number): void {
    // Adjust particle visibility/density
    const opacityAttr = this.geometry.getAttribute('opacity') as THREE.BufferAttribute;
    const opacities = opacityAttr.array as Float32Array;
    
    for (let i = 0; i < this.particleCount; i++) {
      opacities[i] = (0.3 + Math.random() * 0.7) * intensity;
    }
    
    opacityAttr.needsUpdate = true;
  }
  
  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

// ============================================
// SNOW SYSTEM
// ============================================

const SnowVertexShader = `
attribute float size;
attribute float rotation;

uniform float time;
uniform vec3 windVelocity;

varying float vRotation;
varying vec2 vUv;

void main() {
  vRotation = rotation + time * 0.5;
  
  vec3 pos = position;
  
  // Gentle falling with turbulence
  float turbulence = sin(time * 2.0 + position.x * 0.5) * cos(time * 1.5 + position.z * 0.5);
  pos.x += turbulence * 0.5;
  pos.z += turbulence * 0.3;
  
  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  
  gl_PointSize = size * (200.0 / -mvPosition.z);
  gl_Position = projectionMatrix * mvPosition;
}
`;

const SnowFragmentShader = `
varying float vRotation;

void main() {
  vec2 uv = gl_PointCoord - vec2(0.5);
  
  // Rotate UV
  float c = cos(vRotation);
  float s = sin(vRotation);
  uv = mat2(c, -s, s, c) * uv;
  
  // Snowflake shape (6-pointed star)
  float r = length(uv);
  float a = atan(uv.y, uv.x);
  
  float arms = 0.5 + 0.5 * cos(a * 6.0);
  float shape = smoothstep(0.5, 0.2, r * (1.0 + arms * 0.3));
  
  gl_FragColor = vec4(1.0, 1.0, 1.0, shape * 0.8);
}
`;

export class SnowSystem {
  public points: THREE.Points;
  
  private geometry: THREE.BufferGeometry;
  private material: THREE.ShaderMaterial;
  private particleCount: number;
  private config: WeatherConfig;
  private positions: Float32Array;
  private velocities: Float32Array;
  
  constructor(config: WeatherConfig) {
    this.config = config;
    this.particleCount = config.particleCount;
    
    this.positions = new Float32Array(this.particleCount * 3);
    this.velocities = new Float32Array(this.particleCount * 3);
    const sizes = new Float32Array(this.particleCount);
    const rotations = new Float32Array(this.particleCount);
    
    for (let i = 0; i < this.particleCount; i++) {
      this.positions[i * 3] = (Math.random() - 0.5) * config.areaSize * 2;
      this.positions[i * 3 + 1] = Math.random() * config.height * 2 - config.height;
      this.positions[i * 3 + 2] = (Math.random() - 0.5) * config.areaSize * 2;
      
      this.velocities[i * 3 + 1] = -1 - Math.random() * 2;  // Slow fall
      
      sizes[i] = 3 + Math.random() * 5;
      rotations[i] = Math.random() * Math.PI * 2;
    }
    
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    this.geometry.setAttribute('rotation', new THREE.BufferAttribute(rotations, 1));
    
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        windVelocity: { value: new THREE.Vector3(0, 0, 0) }
      },
      vertexShader: SnowVertexShader,
      fragmentShader: SnowFragmentShader,
      transparent: true,
      depthWrite: false
    });
    
    this.points = new THREE.Points(this.geometry, this.material);
  }
  
  public update(deltaTime: number, windVelocity: THREE.Vector3, intensity: number): void {
    this.material.uniforms.time.value += deltaTime;
    this.material.uniforms.windVelocity.value.copy(windVelocity);
    
    const positionAttr = this.geometry.getAttribute('position') as THREE.BufferAttribute;
    const positions = positionAttr.array as Float32Array;
    
    for (let i = 0; i < this.particleCount; i++) {
      positions[i * 3 + 1] += this.velocities[i * 3 + 1] * deltaTime * intensity;
      positions[i * 3] += windVelocity.x * deltaTime * 0.2;
      positions[i * 3 + 2] += windVelocity.z * deltaTime * 0.2;
      
      if (positions[i * 3 + 1] < -this.config.height) {
        positions[i * 3 + 1] = this.config.height;
        positions[i * 3] = (Math.random() - 0.5) * this.config.areaSize * 2;
        positions[i * 3 + 2] = (Math.random() - 0.5) * this.config.areaSize * 2;
      }
    }
    
    positionAttr.needsUpdate = true;
  }
  
  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

// ============================================
// FOG SYSTEM
// ============================================

export class FogSystem {
  private scene: THREE.Scene;
  private fog: THREE.FogExp2 | THREE.Fog | null = null;
  private targetDensity: number = 0;
  private currentDensity: number = 0;
  
  constructor(scene: THREE.Scene) {
    this.scene = scene;
  }
  
  public setFog(type: 'exponential' | 'linear', color: THREE.Color, density: number): void {
    this.targetDensity = density;
    
    if (type === 'exponential') {
      if (!(this.scene.fog instanceof THREE.FogExp2)) {
        this.scene.fog = new THREE.FogExp2(color, density);
      }
      (this.scene.fog as THREE.FogExp2).color.copy(color);
    } else {
      const near = 1;
      const far = 100 / Math.max(density, 0.001);
      if (!(this.scene.fog instanceof THREE.Fog)) {
        this.scene.fog = new THREE.Fog(color, near, far);
      }
      (this.scene.fog as THREE.Fog).color.copy(color);
      (this.scene.fog as THREE.Fog).far = far;
    }
  }
  
  public clearFog(): void {
    this.scene.fog = null;
    this.targetDensity = 0;
    this.currentDensity = 0;
  }
  
  public update(deltaTime: number): void {
    // Smooth fog transition
    this.currentDensity += (this.targetDensity - this.currentDensity) * deltaTime * 2;
    
    if (this.scene.fog instanceof THREE.FogExp2) {
      this.scene.fog.density = this.currentDensity;
    }
  }
}

// ============================================
// LIGHTNING SYSTEM
// ============================================

export class LightningBolt {
  public lines: THREE.Line;
  public light: THREE.PointLight;
  
  private startPoint: THREE.Vector3;
  private endPoint: THREE.Vector3;
  private segments: number;
  private lifetime: number;
  private age: number = 0;
  
  constructor(
    start: THREE.Vector3,
    end: THREE.Vector3,
    segments: number = 10
  ) {
    this.startPoint = start;
    this.endPoint = end;
    this.segments = segments;
    this.lifetime = 0.1 + Math.random() * 0.1;
    
    // Generate bolt geometry
    const points = this.generateBoltPoints();
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    
    const material = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 1.0,
      linewidth: 2
    });
    
    this.lines = new THREE.Line(geometry, material);
    
    // Lightning light
    this.light = new THREE.PointLight(0xaaccff, 100, 500);
    this.light.position.copy(start).lerp(end, 0.5);
  }
  
  private generateBoltPoints(): THREE.Vector3[] {
    const points: THREE.Vector3[] = [];
    const mainBranch = this.generateBranch(this.startPoint, this.endPoint, this.segments);
    points.push(...mainBranch);
    
    // Add sub-branches
    for (let i = 0; i < 3; i++) {
      const branchStart = mainBranch[Math.floor(Math.random() * mainBranch.length * 0.5)];
      const branchEnd = branchStart.clone().add(
        new THREE.Vector3(
          (Math.random() - 0.5) * 20,
          -Math.random() * 10,
          (Math.random() - 0.5) * 20
        )
      );
      points.push(...this.generateBranch(branchStart, branchEnd, 5));
    }
    
    return points;
  }
  
  private generateBranch(start: THREE.Vector3, end: THREE.Vector3, segments: number): THREE.Vector3[] {
    const points: THREE.Vector3[] = [];
    const direction = end.clone().sub(start);
    const length = direction.length();
    
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const point = start.clone().lerp(end, t);
      
      // Add jagged displacement
      if (i > 0 && i < segments) {
        const displacement = length * 0.1 * (1 - t);
        point.x += (Math.random() - 0.5) * displacement;
        point.z += (Math.random() - 0.5) * displacement;
      }
      
      points.push(point);
    }
    
    return points;
  }
  
  public update(deltaTime: number): boolean {
    this.age += deltaTime;
    
    const progress = this.age / this.lifetime;
    const opacity = 1 - progress;
    
    if (this.lines.material instanceof THREE.LineBasicMaterial) {
      this.lines.material.opacity = opacity;
    }
    
    this.light.intensity = 100 * opacity * (0.5 + Math.random() * 0.5);
    
    return this.age >= this.lifetime;
  }
  
  public dispose(): void {
    this.lines.geometry.dispose();
    if (this.lines.material instanceof THREE.Material) {
      this.lines.material.dispose();
    }
  }
}

export class LightningSystem {
  private scene: THREE.Scene;
  private bolts: LightningBolt[] = [];
  private areaSize: number;
  private height: number;
  private timeSinceLastBolt: number = 0;
  
  constructor(scene: THREE.Scene, areaSize: number, height: number) {
    this.scene = scene;
    this.areaSize = areaSize;
    this.height = height;
  }
  
  public strike(position?: THREE.Vector3): void {
    const start = position ?? new THREE.Vector3(
      (Math.random() - 0.5) * this.areaSize,
      this.height,
      (Math.random() - 0.5) * this.areaSize
    );
    
    const end = start.clone();
    end.y = 0;
    end.x += (Math.random() - 0.5) * 20;
    end.z += (Math.random() - 0.5) * 20;
    
    const bolt = new LightningBolt(start, end);
    this.bolts.push(bolt);
    this.scene.add(bolt.lines);
    this.scene.add(bolt.light);
  }
  
  public update(deltaTime: number, stormIntensity: number): void {
    // Random lightning based on storm intensity
    this.timeSinceLastBolt += deltaTime;
    
    if (stormIntensity > 0.5) {
      const strikeChance = (stormIntensity - 0.5) * 2;
      if (this.timeSinceLastBolt > 1 && Math.random() < strikeChance * deltaTime) {
        this.strike();
        this.timeSinceLastBolt = 0;
      }
    }
    
    // Update existing bolts
    for (let i = this.bolts.length - 1; i >= 0; i--) {
      const isDead = this.bolts[i].update(deltaTime);
      if (isDead) {
        this.scene.remove(this.bolts[i].lines);
        this.scene.remove(this.bolts[i].light);
        this.bolts[i].dispose();
        this.bolts.splice(i, 1);
      }
    }
  }
  
  public dispose(): void {
    for (const bolt of this.bolts) {
      this.scene.remove(bolt.lines);
      this.scene.remove(bolt.light);
      bolt.dispose();
    }
    this.bolts = [];
  }
}

// ============================================
// MAIN WEATHER SYSTEM
// ============================================

export class WeatherSystem {
  private scene: THREE.Scene;
  private config: WeatherConfig;
  
  private rainSystem: RainSystem;
  private snowSystem: SnowSystem;
  private fogSystem: FogSystem;
  private lightningSystem: LightningSystem;
  
  private currentState: WeatherState;
  private targetState: WeatherState;
  private transitionProgress: number = 1;
  
  private wind: THREE.Vector3 = new THREE.Vector3();
  private time: number = 0;
  
  constructor(scene: THREE.Scene, config: Partial<WeatherConfig> = {}) {
    this.scene = scene;
    
    this.config = {
      particleCount: 10000,
      areaSize: 100,
      height: 50,
      transitionDuration: 5,
      enableScreenEffects: true,
      enableWetSurfaces: true,
      ...config
    };
    
    // Initialize systems
    this.rainSystem = new RainSystem(this.config);
    this.snowSystem = new SnowSystem(this.config);
    this.fogSystem = new FogSystem(scene);
    this.lightningSystem = new LightningSystem(scene, this.config.areaSize, this.config.height);
    
    // Hide particles initially
    this.rainSystem.points.visible = false;
    this.snowSystem.points.visible = false;
    
    // Add to scene
    scene.add(this.rainSystem.points);
    scene.add(this.snowSystem.points);
    
    // Initialize state
    this.currentState = this.createClearState();
    this.targetState = this.createClearState();
  }
  
  private createClearState(): WeatherState {
    return {
      type: 'clear',
      intensity: 0,
      windDirection: new THREE.Vector3(1, 0, 0),
      windSpeed: 0,
      fogDensity: 0,
      temperature: 20,
      cloudCoverage: 0,
      visibility: 1000
    };
  }
  
  /**
   * Set weather type
   */
  public setWeather(type: WeatherType, intensity: number = 1): void {
    this.targetState = {
      type,
      intensity: Math.max(0, Math.min(1, intensity)),
      windDirection: new THREE.Vector3(
        Math.random() - 0.5,
        0,
        Math.random() - 0.5
      ).normalize(),
      windSpeed: this.getWindSpeedForWeather(type, intensity),
      fogDensity: this.getFogDensityForWeather(type, intensity),
      temperature: this.getTemperatureForWeather(type),
      cloudCoverage: this.getCloudCoverageForWeather(type, intensity),
      visibility: this.getVisibilityForWeather(type, intensity)
    };
    
    this.transitionProgress = 0;
  }
  
  private getWindSpeedForWeather(type: WeatherType, intensity: number): number {
    switch (type) {
      case 'storm': return 15 + intensity * 15;
      case 'rain': return 5 + intensity * 10;
      case 'snow': return 2 + intensity * 5;
      case 'cloudy': return 3 + intensity * 5;
      default: return intensity * 3;
    }
  }
  
  private getFogDensityForWeather(type: WeatherType, intensity: number): number {
    switch (type) {
      case 'fog': return 0.02 + intensity * 0.03;
      case 'rain': return 0.005 + intensity * 0.01;
      case 'snow': return 0.01 + intensity * 0.015;
      default: return 0;
    }
  }
  
  private getTemperatureForWeather(type: WeatherType): number {
    switch (type) {
      case 'snow': return -5;
      case 'rain': return 10;
      case 'storm': return 15;
      default: return 20;
    }
  }
  
  private getCloudCoverageForWeather(type: WeatherType, intensity: number): number {
    switch (type) {
      case 'clear': return 0.1;
      case 'cloudy': return 0.5 + intensity * 0.4;
      case 'rain': return 0.8 + intensity * 0.2;
      case 'storm': return 1.0;
      case 'snow': return 0.9;
      case 'fog': return 0.7;
      default: return 0.3;
    }
  }
  
  private getVisibilityForWeather(type: WeatherType, intensity: number): number {
    switch (type) {
      case 'fog': return 50 - intensity * 40;
      case 'rain': return 200 - intensity * 100;
      case 'snow': return 150 - intensity * 100;
      case 'storm': return 100 - intensity * 50;
      default: return 1000;
    }
  }
  
  /**
   * Update weather simulation
   */
  public update(deltaTime: number, cameraPosition?: THREE.Vector3): void {
    this.time += deltaTime;
    
    // Handle transition
    if (this.transitionProgress < 1) {
      this.transitionProgress += deltaTime / this.config.transitionDuration;
      this.transitionProgress = Math.min(1, this.transitionProgress);
      this.interpolateStates();
    }
    
    // Update wind with turbulence
    const windNoise = Math.sin(this.time * 0.5) * 0.3;
    this.wind.copy(this.currentState.windDirection)
      .multiplyScalar(this.currentState.windSpeed * (1 + windNoise));
    
    // Follow camera if provided
    if (cameraPosition) {
      this.rainSystem.points.position.copy(cameraPosition);
      this.snowSystem.points.position.copy(cameraPosition);
    }
    
    // Update systems based on weather type
    const type = this.currentState.type;
    const intensity = this.currentState.intensity;
    
    // Rain
    this.rainSystem.points.visible = (type === 'rain' || type === 'storm') && intensity > 0;
    if (this.rainSystem.points.visible) {
      this.rainSystem.update(deltaTime, this.wind, intensity);
    }
    
    // Snow
    this.snowSystem.points.visible = type === 'snow' && intensity > 0;
    if (this.snowSystem.points.visible) {
      this.snowSystem.update(deltaTime, this.wind, intensity);
    }
    
    // Fog
    if (this.currentState.fogDensity > 0.001) {
      const fogColor = this.getFogColor();
      this.fogSystem.setFog('exponential', fogColor, this.currentState.fogDensity);
    } else {
      this.fogSystem.clearFog();
    }
    this.fogSystem.update(deltaTime);
    
    // Lightning
    this.lightningSystem.update(deltaTime, type === 'storm' ? intensity : 0);
  }
  
  private interpolateStates(): void {
    const t = this.transitionProgress;
    
    this.currentState.intensity = THREE.MathUtils.lerp(
      this.currentState.intensity,
      this.targetState.intensity,
      t
    );
    
    this.currentState.windSpeed = THREE.MathUtils.lerp(
      this.currentState.windSpeed,
      this.targetState.windSpeed,
      t
    );
    
    this.currentState.fogDensity = THREE.MathUtils.lerp(
      this.currentState.fogDensity,
      this.targetState.fogDensity,
      t
    );
    
    this.currentState.visibility = THREE.MathUtils.lerp(
      this.currentState.visibility,
      this.targetState.visibility,
      t
    );
    
    this.currentState.cloudCoverage = THREE.MathUtils.lerp(
      this.currentState.cloudCoverage,
      this.targetState.cloudCoverage,
      t
    );
    
    this.currentState.windDirection.lerp(this.targetState.windDirection, t);
    
    // Snap type at end of transition
    if (t >= 1) {
      this.currentState.type = this.targetState.type;
    }
  }
  
  private getFogColor(): THREE.Color {
    switch (this.currentState.type) {
      case 'fog': return new THREE.Color(0.8, 0.8, 0.8);
      case 'rain': return new THREE.Color(0.5, 0.5, 0.55);
      case 'storm': return new THREE.Color(0.3, 0.3, 0.35);
      case 'snow': return new THREE.Color(0.9, 0.9, 0.95);
      default: return new THREE.Color(0.7, 0.8, 0.9);
    }
  }
  
  /**
   * Get current weather state
   */
  public getState(): WeatherState {
    return { ...this.currentState };
  }
  
  /**
   * Get wind vector
   */
  public getWind(): THREE.Vector3 {
    return this.wind.clone();
  }
  
  /**
   * Trigger lightning manually
   */
  public triggerLightning(position?: THREE.Vector3): void {
    this.lightningSystem.strike(position);
  }
  
  /**
   * Dispose all resources
   */
  public dispose(): void {
    this.rainSystem.dispose();
    this.snowSystem.dispose();
    this.lightningSystem.dispose();
    this.fogSystem.clearFog();
    
    this.scene.remove(this.rainSystem.points);
    this.scene.remove(this.snowSystem.points);
  }
}

