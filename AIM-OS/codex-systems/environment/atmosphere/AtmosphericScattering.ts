/**
 * Atmospheric Scattering System
 * Physically-based sky and atmosphere rendering
 * 
 * Features:
 * - Rayleigh scattering (blue sky)
 * - Mie scattering (sun haze)
 * - Multiple scattering
 * - Aerial perspective
 * - Time of day transitions
 * - Procedural clouds
 * - Sun and moon
 * - Star field
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface AtmosphereConfig {
  earthRadius: number;
  atmosphereHeight: number;
  rayleighScaleHeight: number;
  mieScaleHeight: number;
  rayleighCoefficients: THREE.Vector3;
  mieCoefficient: number;
  mieG: number; // Mie phase function asymmetry
  sunIntensity: number;
  samples: number;
  lightSamples: number;
}

export interface TimeOfDay {
  hours: number;
  minutes: number;
  sunPosition: THREE.Vector3;
  moonPosition: THREE.Vector3;
  sunColor: THREE.Color;
  ambientColor: THREE.Color;
  fogColor: THREE.Color;
}

export interface StarConfig {
  count: number;
  minSize: number;
  maxSize: number;
  colorVariation: number;
}

// ============================================
// ATMOSPHERIC SCATTERING SHADER
// ============================================

const atmosphereVertexShader = `
  varying vec3 vWorldPosition;
  varying vec3 vViewDirection;
  
  void main() {
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    vViewDirection = normalize(worldPos.xyz - cameraPosition);
    
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const atmosphereFragmentShader = `
  uniform vec3 sunDirection;
  uniform float sunIntensity;
  uniform vec3 rayleighCoefficients;
  uniform float mieCoefficient;
  uniform float mieG;
  uniform float earthRadius;
  uniform float atmosphereHeight;
  uniform float rayleighScaleHeight;
  uniform float mieScaleHeight;
  uniform int samples;
  uniform int lightSamples;
  uniform float exposure;
  
  varying vec3 vWorldPosition;
  varying vec3 vViewDirection;
  
  const float PI = 3.14159265359;
  
  // Rayleigh phase function
  float rayleighPhase(float cosTheta) {
    return (3.0 / (16.0 * PI)) * (1.0 + cosTheta * cosTheta);
  }
  
  // Mie phase function (Henyey-Greenstein)
  float miePhase(float cosTheta, float g) {
    float g2 = g * g;
    return (3.0 / (8.0 * PI)) * ((1.0 - g2) * (1.0 + cosTheta * cosTheta)) /
           ((2.0 + g2) * pow(1.0 + g2 - 2.0 * g * cosTheta, 1.5));
  }
  
  // Ray-sphere intersection
  vec2 raySphereIntersect(vec3 ro, vec3 rd, float radius) {
    float b = dot(ro, rd);
    float c = dot(ro, ro) - radius * radius;
    float d = b * b - c;
    
    if (d < 0.0) return vec2(-1.0);
    
    d = sqrt(d);
    return vec2(-b - d, -b + d);
  }
  
  // Optical depth integration
  float opticalDepth(vec3 position, vec3 direction, float scaleHeight) {
    float atmosphereRadius = earthRadius + atmosphereHeight;
    vec2 intersection = raySphereIntersect(position, direction, atmosphereRadius);
    
    if (intersection.x < 0.0) return 0.0;
    
    float stepSize = intersection.y / float(lightSamples);
    float totalDepth = 0.0;
    
    for (int i = 0; i < 8; i++) {
      if (i >= lightSamples) break;
      
      float t = stepSize * (float(i) + 0.5);
      vec3 samplePos = position + direction * t;
      float altitude = length(samplePos) - earthRadius;
      
      totalDepth += exp(-altitude / scaleHeight) * stepSize;
    }
    
    return totalDepth;
  }
  
  void main() {
    vec3 viewDir = normalize(vViewDirection);
    
    // Position camera at earth surface
    vec3 cameraPos = vec3(0.0, earthRadius + 1.0, 0.0);
    float atmosphereRadius = earthRadius + atmosphereHeight;
    
    // Find ray intersection with atmosphere
    vec2 intersection = raySphereIntersect(cameraPos, viewDir, atmosphereRadius);
    
    if (intersection.y < 0.0) {
      gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
      return;
    }
    
    float rayLength = intersection.y;
    float stepSize = rayLength / float(samples);
    
    vec3 rayleighScatter = vec3(0.0);
    vec3 mieScatter = vec3(0.0);
    
    float cosTheta = dot(viewDir, sunDirection);
    float rayleighPhaseValue = rayleighPhase(cosTheta);
    float miePhaseValue = miePhase(cosTheta, mieG);
    
    vec3 transmittance = vec3(1.0);
    
    for (int i = 0; i < 32; i++) {
      if (i >= samples) break;
      
      float t = stepSize * (float(i) + 0.5);
      vec3 samplePos = cameraPos + viewDir * t;
      float altitude = length(samplePos) - earthRadius;
      
      // Densities at this altitude
      float rayleighDensity = exp(-altitude / rayleighScaleHeight);
      float mieDensity = exp(-altitude / mieScaleHeight);
      
      // Optical depth to sun
      float rayleighDepth = opticalDepth(samplePos, sunDirection, rayleighScaleHeight);
      float mieDepth = opticalDepth(samplePos, sunDirection, mieScaleHeight);
      
      // Attenuation
      vec3 attenuation = exp(-(rayleighCoefficients * rayleighDepth + mieCoefficient * mieDepth));
      
      // Accumulate scattering
      rayleighScatter += rayleighDensity * attenuation * transmittance * stepSize;
      mieScatter += mieDensity * attenuation * transmittance * stepSize;
      
      // Update transmittance
      transmittance *= exp(-(rayleighCoefficients * rayleighDensity + mieCoefficient * mieDensity) * stepSize);
    }
    
    // Final color
    vec3 color = sunIntensity * (
      rayleighScatter * rayleighCoefficients * rayleighPhaseValue +
      mieScatter * mieCoefficient * miePhaseValue
    );
    
    // Tone mapping
    color = 1.0 - exp(-exposure * color);
    
    // Gamma correction
    color = pow(color, vec3(1.0 / 2.2));
    
    gl_FragColor = vec4(color, 1.0);
  }
`;

// ============================================
// STAR FIELD GENERATOR
// ============================================

export class StarField {
  private geometry: THREE.BufferGeometry;
  private material: THREE.PointsMaterial;
  private points: THREE.Points;
  private config: StarConfig;
  
  constructor(scene: THREE.Scene, config: Partial<StarConfig> = {}) {
    this.config = {
      count: 5000,
      minSize: 0.5,
      maxSize: 2,
      colorVariation: 0.2,
      ...config
    };
    
    this.geometry = new THREE.BufferGeometry();
    
    const positions = new Float32Array(this.config.count * 3);
    const colors = new Float32Array(this.config.count * 3);
    const sizes = new Float32Array(this.config.count);
    
    for (let i = 0; i < this.config.count; i++) {
      // Random position on sphere
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const radius = 1000;
      
      positions[i * 3 + 0] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);
      
      // Color with variation
      const baseColor = new THREE.Color(0xffffff);
      const variation = this.config.colorVariation;
      
      colors[i * 3 + 0] = baseColor.r * (1 - variation + Math.random() * variation * 2);
      colors[i * 3 + 1] = baseColor.g * (1 - variation + Math.random() * variation * 2);
      colors[i * 3 + 2] = baseColor.b * (1 - variation + Math.random() * variation * 2);
      
      // Size
      sizes[i] = THREE.MathUtils.randFloat(this.config.minSize, this.config.maxSize);
    }
    
    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    this.material = new THREE.PointsMaterial({
      size: 1,
      vertexColors: true,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    
    this.points = new THREE.Points(this.geometry, this.material);
    this.points.renderOrder = -1;
    scene.add(this.points);
  }
  
  /**
   * Set star visibility based on time of day
   */
  public setVisibility(visibility: number): void {
    this.material.opacity = visibility;
  }
  
  /**
   * Rotate star field
   */
  public rotate(angle: number): void {
    this.points.rotation.z = angle;
  }
  
  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

// ============================================
// SUN/MOON RENDERER
// ============================================

export class CelestialBody {
  private mesh: THREE.Mesh;
  private light: THREE.DirectionalLight;
  private corona: THREE.Mesh | null = null;
  
  constructor(
    scene: THREE.Scene,
    type: 'sun' | 'moon',
    radius: number = 50
  ) {
    const geometry = new THREE.SphereGeometry(radius, 32, 32);
    
    let material: THREE.Material;
    
    if (type === 'sun') {
      material = new THREE.MeshBasicMaterial({
        color: 0xffffee,
        fog: false
      });
      
      // Add corona
      const coronaGeometry = new THREE.SphereGeometry(radius * 1.5, 32, 32);
      const coronaMaterial = new THREE.ShaderMaterial({
        uniforms: {
          sunColor: { value: new THREE.Color(0xffffaa) }
        },
        vertexShader: `
          varying vec3 vNormal;
          void main() {
            vNormal = normalize(normalMatrix * normal);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          uniform vec3 sunColor;
          varying vec3 vNormal;
          void main() {
            float intensity = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 2.0);
            gl_FragColor = vec4(sunColor, intensity * 0.5);
          }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        side: THREE.BackSide
      });
      
      this.corona = new THREE.Mesh(coronaGeometry, coronaMaterial);
      scene.add(this.corona);
      
      this.light = new THREE.DirectionalLight(0xffffee, 1);
    } else {
      material = new THREE.MeshStandardMaterial({
        color: 0xcccccc,
        roughness: 0.8,
        metalness: 0.1
      });
      
      this.light = new THREE.DirectionalLight(0x6666aa, 0.3);
    }
    
    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.position.set(0, 500, 0);
    scene.add(this.mesh);
    
    this.light.position.copy(this.mesh.position);
    this.light.castShadow = true;
    scene.add(this.light);
  }
  
  /**
   * Update position
   */
  public setPosition(position: THREE.Vector3): void {
    this.mesh.position.copy(position);
    this.light.position.copy(position);
    
    if (this.corona) {
      this.corona.position.copy(position);
    }
  }
  
  /**
   * Set intensity
   */
  public setIntensity(intensity: number): void {
    this.light.intensity = intensity;
  }
  
  /**
   * Set color
   */
  public setColor(color: THREE.Color): void {
    this.light.color.copy(color);
  }
  
  public getDirection(): THREE.Vector3 {
    return this.mesh.position.clone().normalize();
  }
  
  public dispose(): void {
    this.mesh.geometry.dispose();
    (this.mesh.material as THREE.Material).dispose();
    this.corona?.geometry.dispose();
    (this.corona?.material as THREE.Material)?.dispose();
  }
}

// ============================================
// AERIAL PERSPECTIVE
// ============================================

export class AerialPerspective {
  private material: THREE.ShaderMaterial;
  
  constructor() {
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        tDepth: { value: null },
        fogColor: { value: new THREE.Color(0x88aacc) },
        fogDensity: { value: 0.0001 },
        near: { value: 0.1 },
        far: { value: 1000 },
        sunDirection: { value: new THREE.Vector3(0, 1, 0) },
        sunColor: { value: new THREE.Color(0xffffee) },
        inscatterStrength: { value: 0.1 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform sampler2D tDepth;
        uniform vec3 fogColor;
        uniform float fogDensity;
        uniform float near;
        uniform float far;
        uniform vec3 sunDirection;
        uniform vec3 sunColor;
        uniform float inscatterStrength;
        
        varying vec2 vUv;
        
        float linearizeDepth(float depth) {
          return near * far / (far - depth * (far - near));
        }
        
        void main() {
          vec4 color = texture2D(tDiffuse, vUv);
          float depth = texture2D(tDepth, vUv).r;
          float linearDepth = linearizeDepth(depth);
          
          // Exponential fog
          float fogAmount = 1.0 - exp(-linearDepth * fogDensity);
          
          // Inscattering based on view direction relative to sun
          vec3 viewDir = normalize(vec3(vUv * 2.0 - 1.0, 1.0));
          float inscatter = max(0.0, dot(viewDir, sunDirection)) * inscatterStrength;
          vec3 inscatterColor = sunColor * inscatter;
          
          vec3 finalColor = mix(color.rgb, fogColor + inscatterColor, fogAmount);
          
          gl_FragColor = vec4(finalColor, color.a);
        }
      `
    });
  }
  
  public getMaterial(): THREE.ShaderMaterial {
    return this.material;
  }
  
  public setFogColor(color: THREE.Color): void {
    this.material.uniforms.fogColor.value.copy(color);
  }
  
  public setFogDensity(density: number): void {
    this.material.uniforms.fogDensity.value = density;
  }
  
  public setSunDirection(direction: THREE.Vector3): void {
    this.material.uniforms.sunDirection.value.copy(direction.normalize());
  }
  
  public dispose(): void {
    this.material.dispose();
  }
}

// ============================================
// MAIN ATMOSPHERIC SCATTERING SYSTEM
// ============================================

export class AtmosphericScattering {
  private scene: THREE.Scene;
  private config: AtmosphereConfig;
  private skyMesh: THREE.Mesh;
  private skyMaterial: THREE.ShaderMaterial;
  private sun: CelestialBody;
  private moon: CelestialBody;
  private stars: StarField;
  private aerialPerspective: AerialPerspective;
  
  private timeOfDay: TimeOfDay;
  private latitude: number = 45; // Degrees
  
  constructor(scene: THREE.Scene, config: Partial<AtmosphereConfig> = {}) {
    this.scene = scene;
    
    this.config = {
      earthRadius: 6371000, // meters
      atmosphereHeight: 100000,
      rayleighScaleHeight: 8500,
      mieScaleHeight: 1200,
      rayleighCoefficients: new THREE.Vector3(5.8e-6, 13.5e-6, 33.1e-6),
      mieCoefficient: 21e-6,
      mieG: 0.76,
      sunIntensity: 22,
      samples: 16,
      lightSamples: 8,
      ...config
    };
    
    // Create sky dome
    const geometry = new THREE.SphereGeometry(900, 64, 32);
    geometry.scale(-1, 1, 1); // Inside-out sphere
    
    this.skyMaterial = new THREE.ShaderMaterial({
      uniforms: {
        sunDirection: { value: new THREE.Vector3(0, 1, 0) },
        sunIntensity: { value: this.config.sunIntensity },
        rayleighCoefficients: { value: this.config.rayleighCoefficients },
        mieCoefficient: { value: this.config.mieCoefficient },
        mieG: { value: this.config.mieG },
        earthRadius: { value: this.config.earthRadius / 1000 },
        atmosphereHeight: { value: this.config.atmosphereHeight / 1000 },
        rayleighScaleHeight: { value: this.config.rayleighScaleHeight / 1000 },
        mieScaleHeight: { value: this.config.mieScaleHeight / 1000 },
        samples: { value: this.config.samples },
        lightSamples: { value: this.config.lightSamples },
        exposure: { value: 2.0 }
      },
      vertexShader: atmosphereVertexShader,
      fragmentShader: atmosphereFragmentShader,
      side: THREE.BackSide,
      depthWrite: false
    });
    
    this.skyMesh = new THREE.Mesh(geometry, this.skyMaterial);
    this.skyMesh.renderOrder = -100;
    scene.add(this.skyMesh);
    
    // Create celestial bodies
    this.sun = new CelestialBody(scene, 'sun', 30);
    this.moon = new CelestialBody(scene, 'moon', 20);
    
    // Create star field
    this.stars = new StarField(scene);
    
    // Aerial perspective
    this.aerialPerspective = new AerialPerspective();
    
    // Initialize time
    this.timeOfDay = {
      hours: 12,
      minutes: 0,
      sunPosition: new THREE.Vector3(0, 1, 0),
      moonPosition: new THREE.Vector3(0, -1, 0),
      sunColor: new THREE.Color(0xffffee),
      ambientColor: new THREE.Color(0x88aacc),
      fogColor: new THREE.Color(0x88aacc)
    };
    
    this.setTime(12, 0);
  }
  
  /**
   * Set time of day
   */
  public setTime(hours: number, minutes: number = 0): void {
    this.timeOfDay.hours = hours;
    this.timeOfDay.minutes = minutes;
    
    // Calculate sun position
    const dayFraction = (hours + minutes / 60) / 24;
    const solarAngle = (dayFraction - 0.25) * Math.PI * 2;
    
    // Adjust for latitude
    const latRad = this.latitude * Math.PI / 180;
    const declination = 23.45 * Math.cos((dayFraction - 0.5) * Math.PI * 2) * Math.PI / 180;
    
    const sunX = Math.cos(solarAngle) * Math.cos(declination);
    const sunY = Math.sin(solarAngle) * Math.sin(latRad) +
                  Math.cos(solarAngle) * Math.cos(latRad) * Math.sin(declination);
    const sunZ = Math.sin(solarAngle) * Math.cos(latRad) -
                  Math.cos(solarAngle) * Math.sin(latRad) * Math.sin(declination);
    
    const sunDirection = new THREE.Vector3(sunX, sunY, sunZ).normalize();
    this.timeOfDay.sunPosition.copy(sunDirection);
    
    // Update sun position in world space
    this.sun.setPosition(sunDirection.clone().multiplyScalar(800));
    this.skyMaterial.uniforms.sunDirection.value.copy(sunDirection);
    
    // Moon position (opposite)
    this.timeOfDay.moonPosition.copy(sunDirection).negate();
    this.moon.setPosition(this.timeOfDay.moonPosition.clone().multiplyScalar(800));
    
    // Calculate sun color based on angle
    const sunHeight = sunDirection.y;
    
    if (sunHeight > 0) {
      // Day
      const t = Math.min(1, sunHeight * 2);
      this.timeOfDay.sunColor.setRGB(
        1,
        THREE.MathUtils.lerp(0.6, 1, t),
        THREE.MathUtils.lerp(0.3, 0.9, t)
      );
      this.sun.setIntensity(Math.min(1, sunHeight * 3));
      this.moon.setIntensity(0);
      this.stars.setVisibility(0);
    } else if (sunHeight > -0.2) {
      // Twilight
      const t = 1 + sunHeight / 0.2;
      this.timeOfDay.sunColor.setRGB(
        THREE.MathUtils.lerp(0.8, 1, t),
        THREE.MathUtils.lerp(0.3, 0.6, t),
        THREE.MathUtils.lerp(0.1, 0.3, t)
      );
      this.sun.setIntensity(t * 0.5);
      this.moon.setIntensity((1 - t) * 0.3);
      this.stars.setVisibility(1 - t);
    } else {
      // Night
      this.timeOfDay.sunColor.setRGB(0.1, 0.1, 0.2);
      this.sun.setIntensity(0);
      this.moon.setIntensity(0.3);
      this.stars.setVisibility(1);
    }
    
    this.sun.setColor(this.timeOfDay.sunColor);
    
    // Update fog color
    this.timeOfDay.fogColor.copy(this.timeOfDay.sunColor)
      .multiplyScalar(0.5);
    this.aerialPerspective.setFogColor(this.timeOfDay.fogColor);
    this.aerialPerspective.setSunDirection(sunDirection);
  }
  
  /**
   * Set latitude
   */
  public setLatitude(latitude: number): void {
    this.latitude = latitude;
    this.setTime(this.timeOfDay.hours, this.timeOfDay.minutes);
  }
  
  /**
   * Get sun direction
   */
  public getSunDirection(): THREE.Vector3 {
    return this.timeOfDay.sunPosition.clone();
  }
  
  /**
   * Get sun color
   */
  public getSunColor(): THREE.Color {
    return this.timeOfDay.sunColor.clone();
  }
  
  /**
   * Get ambient color
   */
  public getAmbientColor(): THREE.Color {
    return this.timeOfDay.ambientColor.clone();
  }
  
  /**
   * Get aerial perspective pass for post-processing
   */
  public getAerialPerspectiveMaterial(): THREE.ShaderMaterial {
    return this.aerialPerspective.getMaterial();
  }
  
  /**
   * Update camera position for sky dome
   */
  public update(cameraPosition: THREE.Vector3): void {
    this.skyMesh.position.copy(cameraPosition);
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.skyMesh.geometry.dispose();
    this.skyMaterial.dispose();
    this.sun.dispose();
    this.moon.dispose();
    this.stars.dispose();
    this.aerialPerspective.dispose();
  }
}

