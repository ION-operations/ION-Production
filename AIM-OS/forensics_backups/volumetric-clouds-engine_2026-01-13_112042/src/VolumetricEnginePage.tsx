import React, { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
  Play, Pause, Maximize, Minimize, Sun, Cloud, Save, Zap, Camera, Palette, Mountain, Sparkles, Wind, Eye, Droplets, Building, Trash2
} from 'lucide-react';

// ============================================================================
// VOLUMETRIC CLOUD ENGINE v4.0
// Mountains, City, Water with Gerstner Waves, Enhanced Clouds
// ============================================================================

const vertexShaderSource = `#version 300 es
in vec4 aPosition;
out vec2 vUv;
void main() {
    vUv = aPosition.xy * 0.5 + 0.5;
    gl_Position = aPosition;
}`;

const presentFragmentShaderSource = `#version 300 es
precision highp float;
in vec2 vUv;
out vec4 fragColor;
uniform sampler2D uTex;
void main() {
    fragColor = texture(uTex, vUv);
}
`;

const fragmentShaderSource = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform float iTime;
uniform vec2 iResolution;
uniform int iFrame;

// Camera
uniform vec3 uCameraPos;
uniform float uCameraYaw;
uniform float uCameraPitch;
uniform float uCameraZoom;

// Cloud params
uniform float uCloudDensity;
uniform float uCloudCoverage;
uniform float uCloudScale;
uniform float uDetailScale;
uniform float uShapeSpeed;
uniform float uDetailSpeed;
uniform float uCloudHeight;
uniform float uCloudThickness;
uniform float uCloudBrightness;
uniform float uCloudContrast;
uniform float uCloudShadowDarkness;
uniform float uCloudShadowSoftness;

// Lighting
uniform float uLightIntensity;
uniform float uAmbientIntensity;
uniform vec3 uLightDir;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform float uSilverLiningIntensity;
uniform float uSilverLiningSpread;
uniform float uMultiScatter;
uniform float uPowderStrength;

// Sun/Sky
uniform float uSunSize;
uniform float uSunBloom;
uniform float uSunHaloSize;
uniform float uSunHaloStrength;
uniform vec3 uSkyColorZenith;
uniform vec3 uSkyColorHorizon;
uniform float uRayleighStrength;
uniform float uMieStrength;
uniform float uMieG;

// Stars
uniform bool uShowStars;
uniform float uStarDensity;
uniform float uStarBrightness;
uniform float uStarTwinkleSpeed;

// God Rays
uniform bool uEnableGodRays;
uniform float uGodRayDensity;
uniform float uGodRayIntensity;
uniform float uGodRayDecay;
uniform int uGodRaySteps;
uniform vec3 uGodRayColor;

// Fog
uniform float uFogDensity;
uniform float uFogHeight;
uniform float uFogFalloff;
uniform vec3 uFogColor;
uniform bool uVolumetricFog;

// Terrain
uniform float uTerrainHeight;
uniform float uMountainHeight;
uniform float uMountainScale;
uniform float uMountainSharpness;
uniform vec3 uGrassColor;
uniform vec3 uDirtColor;
uniform vec3 uRockColor;
uniform vec3 uSnowColor;
uniform float uSnowLine;
uniform bool uShowTerrain;

// City
uniform bool uShowCity;
uniform float uCityDistance;
uniform float uCityDensity;
uniform float uBuildingHeight;
uniform vec3 uBuildingColor;
uniform float uWindowGlow;

// Water
uniform bool uShowWater;
uniform float uWaterLevel;
uniform vec3 uWaterColor;
uniform vec3 uWaterDeepColor;
uniform float uWaveHeight;
uniform float uWaveFrequency;
uniform float uWaveSpeed;
uniform float uWaterReflectivity;
uniform float uWaterRoughness;
uniform float uWaterFresnel;
uniform bool uShowCaustics;
uniform float uCausticsStrength;

// Quality
uniform int uPrimarySteps;
uniform int uLightSteps;

// Temporal
uniform sampler2D uPrevFrame;
uniform float uTemporalBlend;
uniform bool uEnableTemporal;

#define PI 3.14159265359

// ============================================================================
// NOISE FUNCTIONS
// ============================================================================

float hash(float n) { return fract(sin(n) * 43758.5453123); }
float hash2(vec2 p) { return fract(1e4 * sin(17.0 * p.x + p.y * 0.1) * (0.1 + abs(sin(p.y * 13.0 + p.x)))); }
float hash3(vec3 p) { return hash(dot(p, vec3(127.1, 311.7, 74.7))); }

float noise(vec3 x) {
    vec3 i = floor(x);
    vec3 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(hash3(i), hash3(i + vec3(1,0,0)), f.x),
                   mix(hash3(i + vec3(0,1,0)), hash3(i + vec3(1,1,0)), f.x), f.y),
               mix(mix(hash3(i + vec3(0,0,1)), hash3(i + vec3(1,0,1)), f.x),
                   mix(hash3(i + vec3(0,1,1)), hash3(i + vec3(1,1,1)), f.x), f.y), f.z);
}

float noise2D(vec2 x) {
    vec2 i = floor(x);
    vec2 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash2(i), hash2(i + vec2(1,0)), f.x),
               mix(hash2(i + vec2(0,1)), hash2(i + vec2(1,1)), f.x), f.y);
}

float fbm(vec3 p, int octaves) {
    float v = 0.0, a = 0.5;
    for(int i = 0; i < 6; i++) {
        if(i >= octaves) break;
        v += a * noise(p);
        p *= 2.0;
        a *= 0.5;
    }
    return v;
}

float fbm2D(vec2 p, int octaves) {
    float v = 0.0, a = 0.5;
    for(int i = 0; i < 6; i++) {
        if(i >= octaves) break;
        v += a * noise2D(p);
        p *= 2.0;
        a *= 0.5;
    }
    return v;
}

float blueNoise(vec2 uv, int frame) {
    vec3 magic = vec3(0.06711056, 0.00583715, 52.9829189);
    return fract(magic.z * fract(dot(uv + float(frame % 64) * 5.588238, magic.xy)));
}

// Ridge noise for sharp mountains
float ridgeNoise(vec2 p) {
    return 1.0 - abs(noise2D(p) * 2.0 - 1.0);
}

float ridgeFbm(vec2 p, int octaves) {
    float v = 0.0, a = 0.5;
    for(int i = 0; i < 6; i++) {
        if(i >= octaves) break;
        float r = ridgeNoise(p);
        v += a * r * r;
        p *= 2.0;
        a *= 0.5;
    }
    return v;
}

// ============================================================================
// ATMOSPHERIC SCATTERING
// ============================================================================

float rayleighPhase(float cosTheta) {
    return (3.0 / (16.0 * PI)) * (1.0 + cosTheta * cosTheta);
}

float miePhase(float cosTheta, float g) {
    float g2 = g * g;
    return (3.0 / (8.0 * PI)) * ((1.0 - g2) * (1.0 + cosTheta * cosTheta)) / 
           ((2.0 + g2) * pow(1.0 + g2 - 2.0 * g * cosTheta, 1.5));
}

vec3 atmosphericScattering(vec3 rd, vec3 lightDir, float sunHeight) {
    float cosTheta = dot(rd, lightDir);
    vec3 rayleighCoeff = vec3(5.8e-6, 13.5e-6, 33.1e-6);
    vec3 mieCoeff = vec3(21e-6);
    
    float zenithAngle = max(0.0, rd.y);
    float rayleighDepth = exp(-zenithAngle * 4.0) * uRayleighStrength;
    float mieDepth = exp(-zenithAngle * 1.2) * uMieStrength;
    
    vec3 rayleigh = rayleighCoeff * rayleighPhase(cosTheta) * rayleighDepth * 40.0;
    vec3 mie = mieCoeff * miePhase(cosTheta, uMieG) * mieDepth * 20.0;
    
    float sunInfluence = max(0.0, sunHeight);
    vec3 sunColor = mix(vec3(1.0, 0.3, 0.1), vec3(1.0, 0.95, 0.9), sunInfluence);
    
    float horizonBlend = pow(1.0 - max(0.0, rd.y), 3.0);
    vec3 skyGradient = mix(uSkyColorZenith, uSkyColorHorizon, horizonBlend);
    
    vec3 scatter = (rayleigh + mie) * sunColor * uLightIntensity;
    return skyGradient + scatter;
}

// ============================================================================
// STARS
// ============================================================================

float starField(vec3 rd) {
    if(!uShowStars) return 0.0;
    float nightFactor = 1.0 - smoothstep(-0.1, 0.3, normalize(uLightDir).y);
    if(nightFactor < 0.01 || rd.y < 0.0) return 0.0;
    
    vec2 starUV = vec2(atan(rd.z, rd.x), asin(rd.y)) * vec2(1.0 / PI, 2.0 / PI);
    starUV *= uStarDensity * 100.0;
    
    vec2 starCell = floor(starUV);
    vec2 starPos = fract(starUV);
    
    float star = 0.0;
    for(int x = -1; x <= 1; x++) {
        for(int y = -1; y <= 1; y++) {
            vec2 cell = starCell + vec2(x, y);
            vec2 cellHash = vec2(hash2(cell), hash2(cell + 100.0));
            vec2 starCenter = cellHash;
            float dist = length(starPos - starCenter - vec2(x, y));
            float brightness = hash2(cell + 200.0);
            if(brightness > 0.97) {
                float twinkle = sin(iTime * uStarTwinkleSpeed * (1.0 + hash2(cell) * 2.0) + hash2(cell) * 6.28) * 0.5 + 0.5;
                twinkle = mix(0.5, 1.0, twinkle);
                float core = 1.0 - smoothstep(0.0, 0.02, dist);
                float starBright = core * brightness * twinkle;
                star = max(star, starBright);
            }
        }
    }
    return star * uStarBrightness * nightFactor;
}

// ============================================================================
// SUN RENDERING
// ============================================================================

vec3 renderSun(vec3 rd, vec3 lightDir) {
    float sunDot = dot(rd, lightDir);
    float sunDisk = smoothstep(1.0 - uSunSize * 0.0001, 1.0 - uSunSize * 0.00005, sunDot);
    float bloom = pow(max(0.0, sunDot), 256.0 / uSunBloom) * uSunBloom;
    float halo = pow(max(0.0, sunDot), 8.0 / uSunHaloSize) * uSunHaloStrength;
    vec3 sunColor = uLightColor * uLightIntensity;
    return sunColor * (sunDisk * 10.0 + bloom * 2.0 + halo);
}

// ============================================================================
// TERRAIN WITH MOUNTAINS
// ============================================================================

float mountainHeight(vec2 p) {
    float base = fbm2D(p * 0.00005 * uMountainScale, 4) * uTerrainHeight;
    float ridges = ridgeFbm(p * 0.0001 * uMountainScale, 5);
    float mountains = pow(ridges, uMountainSharpness) * uMountainHeight;
    float detail = fbm2D(p * 0.001, 3) * uTerrainHeight * 0.1;
    return base + mountains + detail;
}

vec3 terrainNormal(vec2 p) {
    float eps = 10.0;
    float h = mountainHeight(p);
    return normalize(vec3(h - mountainHeight(p + vec2(eps, 0)), eps, h - mountainHeight(p + vec2(0, eps))));
}

// ============================================================================
// CITY SKYLINE
// ============================================================================

float buildingHeight(vec2 p) {
    vec2 cellId = floor(p / 50.0);
    float h = hash2(cellId);
    if(h < uCityDensity) {
        float variation = hash2(cellId + 100.0);
        return variation * uBuildingHeight;
    }
    return 0.0;
}

// ============================================================================
// GERSTNER WAVES
// ============================================================================

vec3 gerstnerWave(vec2 p, float time, vec2 dir, float steepness, float wavelength) {
    float k = 2.0 * PI / wavelength;
    float c = sqrt(9.8 / k);
    float a = steepness / k;
    
    dir = normalize(dir);
    float f = k * (dot(dir, p) - c * time);
    
    return vec3(
        dir.x * a * cos(f),
        a * sin(f),
        dir.y * a * cos(f)
    );
}

vec3 getWaterDisplacement(vec2 p) {
    float t = iTime * uWaveSpeed;
    vec3 disp = vec3(0.0);
    
    // Multiple wave layers
    disp += gerstnerWave(p, t, vec2(1.0, 0.3), 0.25 * uWaveHeight, 60.0 / uWaveFrequency);
    disp += gerstnerWave(p, t, vec2(0.5, 0.8), 0.15 * uWaveHeight, 31.0 / uWaveFrequency);
    disp += gerstnerWave(p, t, vec2(-0.3, 0.6), 0.1 * uWaveHeight, 18.0 / uWaveFrequency);
    disp += gerstnerWave(p, t, vec2(0.8, -0.2), 0.08 * uWaveHeight, 10.0 / uWaveFrequency);
    disp += gerstnerWave(p, t * 1.5, vec2(-0.5, -0.5), 0.05 * uWaveHeight, 5.0 / uWaveFrequency);
    
    return disp;
}

vec3 getWaterNormal(vec2 p) {
    float eps = 0.5;
    vec3 d0 = getWaterDisplacement(p);
    vec3 dxDisp = getWaterDisplacement(p + vec2(eps, 0.0)) - d0;
    vec3 dzDisp = getWaterDisplacement(p + vec2(0.0, eps)) - d0;
    
    // Gerstner wave returns (dx, height, dz) displacement
    // Build tangent vectors for normal calculation
    vec3 tangent = vec3(eps, dxDisp.y, 0.0);
    vec3 bitangent = vec3(0.0, dzDisp.y, eps);
    
    return normalize(cross(bitangent, tangent));
}

float waterHeight(vec2 p) {
    return uWaterLevel + getWaterDisplacement(p).y;
}

// ============================================================================
// RIVER/LAKE DETECTION
// ============================================================================

float riverMask(vec2 p) {
    float river = 0.0;
    
    float riverPath = sin(p.x * 0.0001 + fbm2D(p * 0.00005, 3) * 3.0) * 500.0;
    float dMain = abs(p.y - riverPath);
    river = max(river, 1.0 - smoothstep(0.0, 200.0, dMain));
    
    float trib = sin(p.x * 0.00015 + 2.0) * 300.0 + 1000.0;
    float dTrib = abs(p.y - trib);
    river = max(river, (1.0 - smoothstep(0.0, 100.0, dTrib)) * step(p.x, 5000.0));
    
    return river;
}

float lakeMask(vec2 p) {
    float valley = 1.0 - fbm2D(p * 0.0001, 3);
    
    float a = smoothstep(0.3, 0.4, valley);
    float b = 1.0 - smoothstep(0.5, 0.6, valley);
    float lake = a * b;
    
    float d1 = length(p - vec2(3000.0, -2000.0)) / 1500.0;
    float d2 = length(p - vec2(-5000.0, 4000.0)) / 2000.0;
    lake = max(lake, 1.0 - smoothstep(0.8, 1.0, d1));
    lake = max(lake, 1.0 - smoothstep(0.8, 1.0, d2));
    
    return lake;
}

bool isWater(vec2 p, float terrainH) {
    if(!uShowWater) return false;
    float water = max(riverMask(p), lakeMask(p));
    return water > 0.5 || terrainH < uWaterLevel;
}

// ============================================================================
// WATER CAUSTICS
// ============================================================================

float caustics(vec2 p, float time) {
    if(!uShowCaustics) return 1.0;
    vec2 uv = p * 0.01;
    float c = 0.0;
    for(int i = 0; i < 3; i++) {
        float t = time * (0.5 + float(i) * 0.2);
        c += sin(uv.x * 10.0 + t) * sin(uv.y * 10.0 + t * 0.7);
        c += sin((uv.x + uv.y) * 8.0 - t * 1.3) * 0.5;
        uv *= 1.5;
    }
    return 1.0 + c * uCausticsStrength * 0.1;
}

// ============================================================================
// VOLUMETRIC FOG
// ============================================================================

float fogDensityAt(vec3 p) {
    if(!uVolumetricFog) return 0.0;
    float heightFactor = exp(-(p.y / uFogHeight) * uFogFalloff);
    float noiseFactor = fbm(p * 0.0001 + vec3(iTime * 0.01, 0.0, 0.0), 3) * 0.5 + 0.5;
    return uFogDensity * heightFactor * noiseFactor;
}

// ============================================================================
// CLOUD DENSITY - FIXED
// ============================================================================

float cloudDensity(vec3 p, float lod, float dist) {
    float heightFraction = clamp((p.y - uCloudHeight) / uCloudThickness, 0.0, 1.0);
    float heightGradient = pow(4.0 * heightFraction * (1.0 - heightFraction), 0.35);
    
    vec3 shapePos = p * uCloudScale * 0.00006;
    shapePos.x += iTime * uShapeSpeed * 0.005;
    shapePos.z += iTime * uShapeSpeed * 0.003;
    
    float distFactor = clamp(dist / 60000.0, 0.0, 1.0);
    int shapeOctaves = int(mix(5.0, 2.0, distFactor));
    
    float baseShape = fbm(shapePos, shapeOctaves);
    
    // Better coverage mapping
    float coverage = uCloudCoverage;
    baseShape = smoothstep(0.5 - coverage * 0.5, 0.5 + coverage * 0.3, baseShape);
    
    float detail = 1.0;
    if(lod < 0.6 && distFactor < 0.7) {
        vec3 detailPos = p * uDetailScale * 0.0003 + vec3(iTime * uDetailSpeed * 0.008, 0.0, 0.0);
        int detailOctaves = int(mix(3.0, 1.0, distFactor));
        detail = 1.0 - fbm(detailPos, detailOctaves) * 0.3 * (1.0 - lod) * (1.0 - distFactor);
    }
    
    return max(0.0, baseShape * heightGradient * detail) * uCloudDensity;
}

// ============================================================================
// CLOUD SHADOW
// ============================================================================

float getCloudShadow(vec3 pos, vec3 lightDir) {
    vec3 p = pos;
    float shadow = 1.0;
    float stepSize = uCloudThickness * 0.12 * uCloudShadowSoftness;
    int steps = int(10.0 / uCloudShadowSoftness);
    
    for(int i = 0; i < 20; i++) {
        if(i >= steps) break;
        p += lightDir * stepSize;
        if(p.y > uCloudHeight && p.y < uCloudHeight + uCloudThickness) {
            float d = cloudDensity(p, 0.8, 30000.0);
            shadow *= exp(-d * stepSize * uCloudShadowDarkness * 0.5);
        }
    }
    return shadow;
}

// ============================================================================
// GOD RAYS
// ============================================================================

float godRayMarch(vec3 ro, vec3 rd, vec3 lightDir, float maxDist) {
    if(!uEnableGodRays) return 0.0;
    
    float stepSize = min(maxDist, 25000.0) / float(uGodRaySteps);
    float accumLight = 0.0;
    float transmittance = 1.0;
    
    for(int i = 0; i < 64; i++) {
        if(i >= uGodRaySteps) break;
        
        float t = stepSize * (float(i) + 0.5);
        vec3 p = ro + rd * t;
        
        float cloudOcclusion = 1.0;
        if(p.y > uCloudHeight && p.y < uCloudHeight + uCloudThickness) {
            cloudOcclusion = 1.0 - cloudDensity(p, 0.9, t) * 0.3;
        }
        
        float shadow = getCloudShadow(p, lightDir);
        float fogD = fogDensityAt(p);
        float scatter = (fogD + uGodRayDensity * 0.0008) * shadow * cloudOcclusion;
        
        float cosTheta = dot(rd, lightDir);
        float phase = miePhase(cosTheta, 0.76);
        
        accumLight += scatter * phase * transmittance * stepSize;
        transmittance *= exp(-scatter * stepSize * uGodRayDecay);
        
        if(transmittance < 0.01) break;
    }
    
    return accumLight * uGodRayIntensity;
}

// ============================================================================
// RAY MARCHING
// ============================================================================

vec2 rayBoxIntersection(vec3 ro, vec3 rd, vec3 boxMin, vec3 boxMax) {
    vec3 t1 = (boxMin - ro) / rd;
    vec3 t2 = (boxMax - ro) / rd;
    vec3 tmin = min(t1, t2);
    vec3 tmax = max(t1, t2);
    return vec2(max(max(tmin.x, tmin.y), tmin.z), min(min(tmax.x, tmax.y), tmax.z));
}

float HenyeyGreenstein(float g, float cosTheta) {
    float g2 = g * g;
    return (1.0 - g2) / (4.0 * PI * pow(1.0 + g2 - 2.0 * g * cosTheta, 1.5));
}

float lightMarch(vec3 p, vec3 lightDir, float dist) {
    float density = 0.0;
    float stepSize = uCloudThickness / float(uLightSteps);
    for(int i = 0; i < 10; i++) {
        if(i >= uLightSteps) break;
        p += lightDir * stepSize;
        density += cloudDensity(p, 0.8, dist) * stepSize;
    }
    return exp(-density * 0.3);
}

vec4 rayMarchClouds(vec3 ro, vec3 rd, vec3 lightDir, float maxDist, float jitter) {
    vec3 boxMin = vec3(-100000.0, uCloudHeight, -100000.0);
    vec3 boxMax = vec3(100000.0, uCloudHeight + uCloudThickness, 100000.0);
    
    vec2 t = rayBoxIntersection(ro, rd, boxMin, boxMax);
    if(t.x > t.y || t.y < 0.0) return vec4(0.0);
    
    t.x = max(t.x, 0.0);
    t.y = min(t.y, maxDist);
    
    float stepSize = (t.y - t.x) / float(uPrimarySteps);
    float dist = t.x + stepSize * jitter;
    
    vec3 lightEnergy = vec3(0.0);
    float transmittance = 1.0;
    
    float cosTheta = dot(rd, lightDir);
    float phase = mix(HenyeyGreenstein(0.4, cosTheta), HenyeyGreenstein(-0.2, cosTheta), 0.35);
    
    for(int i = 0; i < 128; i++) {
        if(i >= uPrimarySteps || transmittance < 0.01) break;
        
        vec3 p = ro + rd * dist;
        float lod = float(i) / float(uPrimarySteps);
        float density = cloudDensity(p, lod, dist);
        
        if(density > 0.0001) {
            float lightTransmittance = lightMarch(p, lightDir, dist);
            float heightFrac = clamp((p.y - uCloudHeight) / uCloudThickness, 0.0, 1.0);
            
            float powder = 1.0 - exp(-density * 2.5 * uPowderStrength);
            float depthProbability = mix(0.15, 1.0, powder);
            
            vec3 ambient = uAmbientColor * uAmbientIntensity * (0.5 + 0.5 * heightFrac);
            ambient += vec3(0.1, 0.12, 0.18) * (1.0 - heightFrac);
            
            vec3 direct = uLightColor * uLightIntensity * lightTransmittance * phase * depthProbability;
            direct *= uCloudBrightness;
            
            float ms = uMultiScatter * powder * (1.0 - lightTransmittance * 0.4);
            float silver = pow(max(0.0, cosTheta), uSilverLiningSpread) * uSilverLiningIntensity * lightTransmittance;
            
            vec3 luminance = (ambient + direct + uLightColor * ms + uLightColor * silver) * density;
            luminance = pow(luminance, vec3(uCloudContrast));
            
            float sampleTransmittance = exp(-density * stepSize * 0.6);
            lightEnergy += luminance * transmittance * (1.0 - sampleTransmittance);
            transmittance *= sampleTransmittance;
        }
        dist += stepSize;
    }
    return vec4(lightEnergy, 1.0 - transmittance);
}

// ============================================================================
// WATER RENDERING
// ============================================================================

vec3 renderWater(vec3 ro, vec3 rd, vec3 lightDir, vec3 hitPos, vec3 skyColor) {
    vec3 normal = getWaterNormal(hitPos.xz);
    
    // Mix with roughness
    normal = normalize(mix(vec3(0.0, 1.0, 0.0), normal, 1.0 - uWaterRoughness * 0.5));
    
    // Fresnel
    float fresnel = pow(1.0 - max(0.0, dot(-rd, normal)), uWaterFresnel);
    fresnel = mix(0.04, 1.0, fresnel) * uWaterReflectivity;
    
    // Reflection
    vec3 reflectDir = reflect(rd, normal);
    vec3 reflectColor = atmosphericScattering(reflectDir, lightDir, lightDir.y);
    reflectColor += renderSun(reflectDir, lightDir);
    
    // Cloud reflection
    vec4 cloudRefl = rayMarchClouds(hitPos + vec3(0.0, 1.0, 0.0), reflectDir, lightDir, 80000.0, 0.5);
    reflectColor = mix(reflectColor, cloudRefl.rgb, cloudRefl.a * 0.7);
    
    // Refraction / water color
    float depth = max(0.0, hitPos.y - uWaterLevel) * 0.1;
    vec3 waterCol = mix(uWaterColor, uWaterDeepColor, smoothstep(0.0, 50.0, depth));
    
    // Caustics on underwater terrain
    float caust = caustics(hitPos.xz, iTime);
    waterCol *= caust;
    
    // Specular highlight
    vec3 halfVec = normalize(lightDir - rd);
    float spec = pow(max(0.0, dot(normal, halfVec)), 256.0) * uLightIntensity;
    
    // Cloud shadow on water
    float cloudShadow = getCloudShadow(hitPos, lightDir);
    
    // Combine
    vec3 color = mix(waterCol, reflectColor, fresnel);
    color += uLightColor * spec * cloudShadow;
    color *= cloudShadow * 0.7 + 0.3;
    
    return color;
}

// ============================================================================
// TERRAIN RENDERING
// ============================================================================

vec4 rayMarchTerrain(vec3 ro, vec3 rd, vec3 lightDir, out float terrainDist) {
    terrainDist = 1e10;
    if(!uShowTerrain || rd.y >= 0.1) return vec4(0.0);
    
    float t = 0.0;
    for(int i = 0; i < 150; i++) {
        vec3 p = ro + rd * t;
        float h = mountainHeight(p.xz);
        float wh = uShowWater ? waterHeight(p.xz) : -1e10;
        
        // Check water first
        if(uShowWater && p.y < wh && isWater(p.xz, h)) {
            // Refine water hit
            float tLo = t - 100.0, tHi = t;
            for(int j = 0; j < 6; j++) {
                float tMid = (tLo + tHi) * 0.5;
                vec3 pm = ro + rd * tMid;
                if(pm.y < waterHeight(pm.xz)) tHi = tMid;
                else tLo = tMid;
            }
            terrainDist = tHi;
            vec3 hitPos = ro + rd * tHi;
            vec3 skyCol = atmosphericScattering(rd, lightDir, lightDir.y);
            vec3 waterColor = renderWater(ro, rd, lightDir, hitPos, skyCol);
            
            float fogAmount = 1.0 - exp(-terrainDist * fogDensityAt(hitPos) * 0.00005);
            waterColor = mix(waterColor, uFogColor, fogAmount);
            
            return vec4(waterColor, 1.0);
        }
        
        // Check terrain
        if(p.y < h) {
            float tLo = t - 150.0, tHi = t;
            for(int j = 0; j < 8; j++) {
                float tMid = (tLo + tHi) * 0.5;
                if((ro + rd * tMid).y < mountainHeight((ro + rd * tMid).xz)) tHi = tMid;
                else tLo = tMid;
            }
            terrainDist = tHi;
            
            vec3 hitPos = ro + rd * tHi;
            vec3 normal = terrainNormal(hitPos.xz);
            float ndotl = max(0.0, dot(normal, lightDir));
            float cloudShadow = getCloudShadow(hitPos, lightDir);
            
            // Material based on height and slope
            float height = hitPos.y;
            float slope = 1.0 - normal.y;
            
            // Color layers
            vec3 grass = uGrassColor * (0.8 + 0.2 * fbm2D(hitPos.xz * 0.005, 2));
            vec3 rock = uRockColor * (0.8 + 0.2 * fbm2D(hitPos.xz * 0.01, 2));
            vec3 snow = uSnowColor;
            
            // Blend based on slope and height
            vec3 surface = mix(grass, rock, smoothstep(0.4, 0.7, slope));
            surface = mix(surface, snow, smoothstep(uSnowLine - 200.0, uSnowLine + 200.0, height) * (1.0 - slope));
            
            // Lighting
            vec3 color = surface * uAmbientColor * 0.25 + surface * uLightColor * ndotl * cloudShadow;
            
            // Fog
            float fogAmount = 1.0 - exp(-terrainDist * fogDensityAt(hitPos) * 0.00004);
            color = mix(color, uFogColor, fogAmount);
            
            return vec4(color, 1.0);
        }
        
        float stepMult = max(100.0, (ro.y + rd.y * t - h) * 0.4);
        t += stepMult;
        if(t > 80000.0) break;
    }
    return vec4(0.0);
}

// ============================================================================
// CITY RENDERING (Silhouette)
// ============================================================================

vec4 renderCitySilhouette(vec3 ro, vec3 rd, vec3 lightDir, float maxDist) {
    if(!uShowCity) return vec4(0.0);
    
    // Simple plane intersection at city distance
    if(abs(rd.z) < 0.001) return vec4(0.0);
    float t = (-uCityDistance - ro.z) / rd.z;
    if(t < 0.0 || t > maxDist) return vec4(0.0);
    
    vec3 hitPos = ro + rd * t;
    
    // Building height at this position
    float bh = buildingHeight(hitPos.xz);
    if(bh <= 0.0 || hitPos.y > bh) return vec4(0.0);
    
    // Silhouette color
    float backlight = max(0.0, dot(normalize(vec3(lightDir.x, 0.0, lightDir.z)), vec3(0.0, 0.0, 1.0)));
    vec3 silhouette = uBuildingColor * 0.1 + uBuildingColor * backlight * 0.3;
    
    // Window lights
    vec2 windowUV = hitPos.xz * 0.1;
    float windowNoise = step(0.7, hash2(floor(windowUV)));
    float windowGlow = windowNoise * uWindowGlow * (1.0 - smoothstep(-0.1, 0.3, lightDir.y));
    silhouette += vec3(1.0, 0.9, 0.6) * windowGlow;
    
    // Fog
    float fogAmount = 1.0 - exp(-t * uFogDensity * 0.0001);
    silhouette = mix(silhouette, uFogColor, fogAmount);
    
    return vec4(silhouette, 1.0);
}

// ============================================================================
// MAIN
// ============================================================================

vec3 getSkyColor(vec3 rd, vec3 lightDir) {
    vec3 sky = atmosphericScattering(rd, lightDir, lightDir.y);
    sky += vec3(starField(rd));
    sky += renderSun(rd, lightDir);
    return sky;
}

mat3 rotationMatrix(float yaw, float pitch) {
    float cy = cos(yaw), sy = sin(yaw), cp = cos(pitch), sp = sin(pitch);
    return mat3(cy, 0.0, -sy, sy * sp, cp, cy * sp, sy * cp, -sp, cy * cp);
}

void main() {
    vec2 uv = (vUv * 2.0 - 1.0) * vec2(iResolution.x / iResolution.y, 1.0);
    
    vec3 ro = uCameraPos;
    mat3 camRot = rotationMatrix(uCameraYaw, uCameraPitch);
    vec3 rd = normalize(camRot * vec3(uv * uCameraZoom, -1.0));
    vec3 lightDir = normalize(uLightDir);
    
    float jitter = blueNoise(gl_FragCoord.xy, iFrame);
    
    // Sky
    vec3 color = getSkyColor(rd, lightDir);
    
    // Terrain/Water
    float terrainDist;
    vec4 terrain = rayMarchTerrain(ro, rd, lightDir, terrainDist);
    if(terrain.a > 0.0) color = terrain.rgb;
    
    // City silhouette
    vec4 city = renderCitySilhouette(ro, rd, lightDir, terrain.a > 0.0 ? terrainDist : 100000.0);
    if(city.a > 0.0) color = mix(color, city.rgb, city.a);
    
    // Clouds
    float cloudMaxDist = terrain.a > 0.0 ? terrainDist : 150000.0;
    vec4 clouds = rayMarchClouds(ro, rd, lightDir, cloudMaxDist, jitter);
    color = mix(color, clouds.rgb, clouds.a);
    
    // God rays
    float godRays = godRayMarch(ro, rd, lightDir, min(cloudMaxDist, 30000.0));
    color += uGodRayColor * godRays;
    
    // Volumetric fog
    if(uVolumetricFog) {
        float fogMarch = 0.0;
        float fogSteps = 16.0;
        float fogStep = min(terrainDist, 20000.0) / fogSteps;
        for(float i = 0.0; i < fogSteps; i++) {
            vec3 fogPos = ro + rd * fogStep * (i + 0.5);
            fogMarch += fogDensityAt(fogPos) * fogStep;
        }
        float fogAmount = 1.0 - exp(-fogMarch * 0.00008);
        color = mix(color, uFogColor * (0.5 + 0.5 * uLightIntensity), fogAmount);
    }
    
    // Tone mapping
    color = color / (color + vec3(1.0));
    
    // Temporal blend
    if(uEnableTemporal && iFrame > 0) {
        vec3 prevColor = texture(uPrevFrame, vUv).rgb;
        color = mix(color, prevColor, uTemporalBlend);
    }
    
    // Gamma
    color = pow(color, vec3(1.0 / 2.2));
    
    fragColor = vec4(color, 1.0);
}
`;

const defaultPresets = {
  'Mountain Lake': {
    cloudDensity: 1.2, cloudCoverage: 0.45, cloudScale: 10.0, detailScale: 30.0,
    shapeSpeed: 0.3, detailSpeed: 0.6, cloudHeight: 3000, cloudThickness: 3500,
    cloudBrightness: 2.2, cloudContrast: 0.95, cloudShadowDarkness: 0.35, cloudShadowSoftness: 1.0,
    lightIntensity: 2.5, ambientIntensity: 0.45, lightDir: [0.5, 0.7, 0.3],
    lightColor: [1.0, 0.98, 0.95], ambientColor: [0.6, 0.7, 0.9],
    silverLiningIntensity: 0.8, silverLiningSpread: 5.0, multiScatter: 0.4, powderStrength: 1.0,
    sunSize: 5.0, sunBloom: 3.0, sunHaloSize: 2.0, sunHaloStrength: 0.3,
    skyColorZenith: [0.2, 0.4, 0.85], skyColorHorizon: [0.6, 0.75, 0.95],
    rayleighStrength: 1.0, mieStrength: 0.5, mieG: 0.76,
    showStars: false, starDensity: 1.0, starBrightness: 1.0, starTwinkleSpeed: 2.0,
    enableGodRays: true, godRayDensity: 0.5, godRayIntensity: 0.8, godRayDecay: 1.0, godRaySteps: 32, godRayColor: [1.0, 0.95, 0.8],
    fogDensity: 0.08, fogHeight: 600.0, fogFalloff: 1.5, fogColor: [0.7, 0.8, 0.9], volumetricFog: true,
    terrainHeight: 300, mountainHeight: 2500, mountainScale: 1.0, mountainSharpness: 2.0,
    grassColor: [0.15, 0.35, 0.1], dirtColor: [0.35, 0.25, 0.15], rockColor: [0.4, 0.38, 0.35], snowColor: [0.95, 0.97, 1.0], snowLine: 1800.0, showTerrain: true,
    showCity: false, cityDistance: 15000, cityDensity: 0.6, buildingHeight: 500, buildingColor: [0.2, 0.22, 0.25], windowGlow: 0.5,
    showWater: true, waterLevel: 200, waterColor: [0.1, 0.3, 0.5], waterDeepColor: [0.02, 0.08, 0.15],
    waveHeight: 1.0, waveFrequency: 1.0, waveSpeed: 0.5, waterReflectivity: 0.8, waterRoughness: 0.2, waterFresnel: 3.0,
    showCaustics: true, causticsStrength: 0.5,
    primarySteps: 64, lightSteps: 6, temporalBlend: 0.85, enableTemporal: true,
  },
  'City Sunset': {
    cloudDensity: 1.5, cloudCoverage: 0.5, cloudScale: 8.0, detailScale: 25.0,
    shapeSpeed: 0.2, detailSpeed: 0.5, cloudHeight: 2000, cloudThickness: 4000,
    cloudBrightness: 2.8, cloudContrast: 0.85, cloudShadowDarkness: 0.45, cloudShadowSoftness: 1.0,
    lightIntensity: 3.0, ambientIntensity: 0.3, lightDir: [0.8, 0.15, 0.3],
    lightColor: [1.0, 0.55, 0.25], ambientColor: [0.5, 0.35, 0.5],
    silverLiningIntensity: 1.8, silverLiningSpread: 5.5, multiScatter: 0.5, powderStrength: 1.5,
    sunSize: 10.0, sunBloom: 6.0, sunHaloSize: 3.5, sunHaloStrength: 0.6,
    skyColorZenith: [0.18, 0.22, 0.45], skyColorHorizon: [0.95, 0.55, 0.35],
    rayleighStrength: 0.7, mieStrength: 1.3, mieG: 0.82,
    showStars: false, starDensity: 1.0, starBrightness: 1.0, starTwinkleSpeed: 2.0,
    enableGodRays: true, godRayDensity: 1.0, godRayIntensity: 1.8, godRayDecay: 0.7, godRaySteps: 48, godRayColor: [1.0, 0.7, 0.4],
    fogDensity: 0.2, fogHeight: 400.0, fogFalloff: 1.2, fogColor: [0.85, 0.6, 0.4], volumetricFog: true,
    terrainHeight: 100, mountainHeight: 500, mountainScale: 1.5, mountainSharpness: 1.5,
    grassColor: [0.2, 0.35, 0.1], dirtColor: [0.35, 0.25, 0.15], rockColor: [0.35, 0.32, 0.3], snowColor: [0.95, 0.97, 1.0], snowLine: 3000.0, showTerrain: true,
    showCity: true, cityDistance: 8000, cityDensity: 0.7, buildingHeight: 800, buildingColor: [0.15, 0.15, 0.2], windowGlow: 0.8,
    showWater: false, waterLevel: 0, waterColor: [0.1, 0.3, 0.5], waterDeepColor: [0.02, 0.08, 0.15],
    waveHeight: 1.0, waveFrequency: 1.0, waveSpeed: 0.5, waterReflectivity: 0.8, waterRoughness: 0.2, waterFresnel: 3.0,
    showCaustics: true, causticsStrength: 0.5,
    primarySteps: 64, lightSteps: 6, temporalBlend: 0.85, enableTemporal: true,
  },
  'Ocean Storm': {
    cloudDensity: 2.5, cloudCoverage: 0.75, cloudScale: 5.0, detailScale: 18.0,
    shapeSpeed: 1.8, detailSpeed: 2.5, cloudHeight: 1000, cloudThickness: 6000,
    cloudBrightness: 1.5, cloudContrast: 1.05, cloudShadowDarkness: 0.6, cloudShadowSoftness: 0.8,
    lightIntensity: 0.7, ambientIntensity: 0.2, lightDir: [0.4, 0.25, 0.5],
    lightColor: [0.75, 0.78, 0.85], ambientColor: [0.3, 0.33, 0.4],
    silverLiningIntensity: 0.4, silverLiningSpread: 3.0, multiScatter: 0.35, powderStrength: 1.0,
    sunSize: 4.0, sunBloom: 1.0, sunHaloSize: 1.0, sunHaloStrength: 0.1,
    skyColorZenith: [0.08, 0.1, 0.15], skyColorHorizon: [0.25, 0.28, 0.32],
    rayleighStrength: 0.3, mieStrength: 0.4, mieG: 0.7,
    showStars: false, starDensity: 1.0, starBrightness: 1.0, starTwinkleSpeed: 2.0,
    enableGodRays: true, godRayDensity: 0.4, godRayIntensity: 0.6, godRayDecay: 1.3, godRaySteps: 32, godRayColor: [0.6, 0.65, 0.7],
    fogDensity: 0.5, fogHeight: 1000.0, fogFalloff: 0.8, fogColor: [0.3, 0.33, 0.38], volumetricFog: true,
    terrainHeight: 50, mountainHeight: 100, mountainScale: 2.0, mountainSharpness: 1.0,
    grassColor: [0.1, 0.2, 0.08], dirtColor: [0.25, 0.2, 0.15], rockColor: [0.3, 0.28, 0.25], snowColor: [0.9, 0.92, 0.95], snowLine: 5000.0, showTerrain: false,
    showCity: false, cityDistance: 15000, cityDensity: 0.5, buildingHeight: 400, buildingColor: [0.15, 0.15, 0.2], windowGlow: 0.5,
    showWater: true, waterLevel: 100, waterColor: [0.08, 0.18, 0.3], waterDeepColor: [0.02, 0.05, 0.1],
    waveHeight: 4.0, waveFrequency: 2.0, waveSpeed: 1.5, waterReflectivity: 0.6, waterRoughness: 0.5, waterFresnel: 2.5,
    showCaustics: false, causticsStrength: 0.3,
    primarySteps: 48, lightSteps: 5, temporalBlend: 0.88, enableTemporal: true,
  },
  'Alpine Dawn': {
    cloudDensity: 0.8, cloudCoverage: 0.3, cloudScale: 12.0, detailScale: 35.0,
    shapeSpeed: 0.2, detailSpeed: 0.4, cloudHeight: 4000, cloudThickness: 2500,
    cloudBrightness: 2.5, cloudContrast: 0.9, cloudShadowDarkness: 0.3, cloudShadowSoftness: 1.2,
    lightIntensity: 2.0, ambientIntensity: 0.4, lightDir: [0.9, 0.15, 0.2],
    lightColor: [1.0, 0.7, 0.45], ambientColor: [0.5, 0.45, 0.55],
    silverLiningIntensity: 1.2, silverLiningSpread: 5.0, multiScatter: 0.45, powderStrength: 1.2,
    sunSize: 8.0, sunBloom: 5.0, sunHaloSize: 3.0, sunHaloStrength: 0.5,
    skyColorZenith: [0.25, 0.35, 0.65], skyColorHorizon: [0.9, 0.6, 0.45],
    rayleighStrength: 0.8, mieStrength: 1.0, mieG: 0.78,
    showStars: false, starDensity: 1.0, starBrightness: 1.0, starTwinkleSpeed: 2.0,
    enableGodRays: true, godRayDensity: 0.7, godRayIntensity: 1.2, godRayDecay: 0.85, godRaySteps: 40, godRayColor: [1.0, 0.75, 0.5],
    fogDensity: 0.15, fogHeight: 800.0, fogFalloff: 1.8, fogColor: [0.85, 0.7, 0.6], volumetricFog: true,
    terrainHeight: 200, mountainHeight: 3500, mountainScale: 0.8, mountainSharpness: 2.5,
    grassColor: [0.12, 0.3, 0.08], dirtColor: [0.3, 0.22, 0.12], rockColor: [0.45, 0.42, 0.38], snowColor: [1.0, 0.98, 0.95], snowLine: 1500.0, showTerrain: true,
    showCity: false, cityDistance: 15000, cityDensity: 0.5, buildingHeight: 400, buildingColor: [0.15, 0.15, 0.2], windowGlow: 0.5,
    showWater: true, waterLevel: 300, waterColor: [0.08, 0.25, 0.4], waterDeepColor: [0.02, 0.06, 0.12],
    waveHeight: 0.3, waveFrequency: 0.8, waveSpeed: 0.3, waterReflectivity: 0.9, waterRoughness: 0.1, waterFresnel: 4.0,
    showCaustics: true, causticsStrength: 0.6,
    primarySteps: 64, lightSteps: 6, temporalBlend: 0.85, enableTemporal: true,
  },
  'Night City': {
    cloudDensity: 0.6, cloudCoverage: 0.25, cloudScale: 14.0, detailScale: 40.0,
    shapeSpeed: 0.15, detailSpeed: 0.3, cloudHeight: 3500, cloudThickness: 2000,
    cloudBrightness: 1.2, cloudContrast: 1.1, cloudShadowDarkness: 0.2, cloudShadowSoftness: 1.5,
    lightIntensity: 0.3, ambientIntensity: 0.12, lightDir: [0.3, -0.25, 0.4],
    lightColor: [0.6, 0.65, 0.9], ambientColor: [0.08, 0.1, 0.18],
    silverLiningIntensity: 0.6, silverLiningSpread: 4.0, multiScatter: 0.2, powderStrength: 0.7,
    sunSize: 3.0, sunBloom: 2.0, sunHaloSize: 1.5, sunHaloStrength: 0.4,
    skyColorZenith: [0.02, 0.025, 0.06], skyColorHorizon: [0.06, 0.07, 0.12],
    rayleighStrength: 0.15, mieStrength: 0.1, mieG: 0.7,
    showStars: true, starDensity: 1.8, starBrightness: 2.5, starTwinkleSpeed: 3.0,
    enableGodRays: false, godRayDensity: 0.2, godRayIntensity: 0.2, godRayDecay: 1.0, godRaySteps: 24, godRayColor: [0.4, 0.5, 0.7],
    fogDensity: 0.08, fogHeight: 300.0, fogFalloff: 2.5, fogColor: [0.08, 0.1, 0.15], volumetricFog: true,
    terrainHeight: 50, mountainHeight: 200, mountainScale: 1.5, mountainSharpness: 1.5,
    grassColor: [0.03, 0.06, 0.03], dirtColor: [0.12, 0.1, 0.08], rockColor: [0.2, 0.18, 0.16], snowColor: [0.8, 0.82, 0.85], snowLine: 5000.0, showTerrain: true,
    showCity: true, cityDistance: 5000, cityDensity: 0.8, buildingHeight: 1000, buildingColor: [0.05, 0.05, 0.08], windowGlow: 1.5,
    showWater: false, waterLevel: 0, waterColor: [0.05, 0.1, 0.2], waterDeepColor: [0.01, 0.03, 0.06],
    waveHeight: 0.5, waveFrequency: 1.0, waveSpeed: 0.3, waterReflectivity: 0.7, waterRoughness: 0.3, waterFresnel: 3.0,
    showCaustics: false, causticsStrength: 0.3,
    primarySteps: 48, lightSteps: 5, temporalBlend: 0.88, enableTemporal: true,
  },
};

const settingsPanels = [
  { id: 'clouds', icon: Cloud, label: 'Clouds' },
  { id: 'shadows', icon: Eye, label: 'Shadows' },
  { id: 'lighting', icon: Sun, label: 'Sun/Light' },
  { id: 'atmosphere', icon: Palette, label: 'Sky' },
  { id: 'stars', icon: Sparkles, label: 'Stars' },
  { id: 'godrays', icon: Sun, label: 'God Rays' },
  { id: 'fog', icon: Wind, label: 'Fog' },
  { id: 'terrain', icon: Mountain, label: 'Terrain' },
  { id: 'water', icon: Droplets, label: 'Water' },
  { id: 'city', icon: Building, label: 'City' },
  { id: 'quality', icon: Zap, label: 'Quality' },
];

const STORAGE_KEY = 'volumetric-clouds-saved-presets';

export default function VolumetricEnginePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const glRef = useRef<WebGL2RenderingContext | null>(null);
  const programRef = useRef<WebGLProgram | null>(null);
  const presentProgramRef = useRef<WebGLProgram | null>(null);
  const presentTexLocRef = useRef<WebGLUniformLocation | null>(null);
  const frameRef = useRef(0);
  const startTimeRef = useRef(Date.now());
  const animationRef = useRef<number | null>(null);
  const fbRef = useRef<{ current: WebGLFramebuffer | null, prev: WebGLFramebuffer | null, texCurrent: WebGLTexture | null, texPrev: WebGLTexture | null, useHDR?: boolean }>({ current: null, prev: null, texCurrent: null, texPrev: null });

  const [cameraPos, setCameraPos] = useState<[number, number, number]>([0, 800, 3000]);
  const [cameraYaw, setCameraYaw] = useState(0);
  const [cameraPitch, setCameraPitch] = useState(-0.05);
  const [cameraZoom, setCameraZoom] = useState(1.0);
  const isDraggingRef = useRef(false);
  const lastMouseRef = useRef({ x: 0, y: 0 });

  const [isPlaying, setIsPlaying] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activePanel, setActivePanel] = useState('clouds');
  const [showPresetDialog, setShowPresetDialog] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [savedPresets, setSavedPresets] = useState<Record<string, any>>({});

  const [params, setParams] = useState({ ...defaultPresets['Mountain Lake'] });
  const [renderScale, setRenderScale] = useState(1.0);

  // Load saved presets from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setSavedPresets(parsed);
      }
    } catch (error) {
      console.error('Failed to load saved presets from localStorage:', error);
    }
  }, []);

  // Save presets to localStorage whenever savedPresets changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(savedPresets));
    } catch (error) {
      console.error('Failed to save presets to localStorage:', error);
    }
  }, [savedPresets]);

  const updateParam = (key: string, value: any) => setParams(prev => ({ ...prev, [key]: value }));

  const applyPreset = (name: string) => {
    const preset = (defaultPresets as any)[name] || savedPresets[name];
    if (preset) setParams({ ...preset });
  };

  const savePreset = () => {
    const trimmedName = presetName.trim();
    if (trimmedName) {
      setSavedPresets(prev => ({ ...prev, [trimmedName]: { ...params } }));
      setPresetName('');
      setShowPresetDialog(false);
    }
  };

  const deletePreset = (name: string) => {
    setSavedPresets(prev => {
      const updated = { ...prev };
      delete updated[name];
      return updated;
    });
  };

  const resetCamera = () => {
    setCameraPos([0, 800, 3000]);
    setCameraYaw(0);
    setCameraPitch(-0.05);
    setCameraZoom(1.0);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl2', { antialias: false, preserveDrawingBuffer: true });
    if (!gl) {
      console.error('WebGL2 not supported');
      return;
    }
    glRef.current = gl;

    // ✅ Check for WebGL extensions (framebuffer fix)
    const extCBF = gl.getExtension('EXT_color_buffer_float');
    const extFloatLinear =
      gl.getExtension('OES_texture_float_linear') ||
      gl.getExtension('OES_texture_half_float_linear');

    const vs = gl.createShader(gl.VERTEX_SHADER);
    if (!vs) return;
    gl.shaderSource(vs, vertexShaderSource);
    gl.compileShader(vs);

    // ✅ Add vertex shader error checking
    if (!gl.getShaderParameter(vs, gl.COMPILE_STATUS)) {
      console.error('Vertex shader error:', gl.getShaderInfoLog(vs));
      return;
    }

    const fs = gl.createShader(gl.FRAGMENT_SHADER);
    if (!fs) return;
    gl.shaderSource(fs, fragmentShaderSource);
    gl.compileShader(fs);
    
    // ✅ Add fragment shader error checking
    if (!gl.getShaderParameter(fs, gl.COMPILE_STATUS)) {
      console.error('Fragment shader error:', gl.getShaderInfoLog(fs));
      return;
    }

    const program = gl.createProgram();
    if (!program) return;
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    programRef.current = program;

    // ✅ Add program link error checking
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program link error:', gl.getProgramInfoLog(program));
      return;
    }

    // Present program (cheap blit)
    const pfs = gl.createShader(gl.FRAGMENT_SHADER);
    if (!pfs) return;
    gl.shaderSource(pfs, presentFragmentShaderSource);
    gl.compileShader(pfs);
    if (!gl.getShaderParameter(pfs, gl.COMPILE_STATUS)) {
      console.error('Present fragment shader error:', gl.getShaderInfoLog(pfs));
      return;
    }

    const presentProgram = gl.createProgram();
    if (!presentProgram) return;
    gl.attachShader(presentProgram, vs);   // reuse same vertex shader
    gl.attachShader(presentProgram, pfs);
    gl.linkProgram(presentProgram);
    if (!gl.getProgramParameter(presentProgram, gl.LINK_STATUS)) {
      console.error('Present program link error:', gl.getProgramInfoLog(presentProgram));
      return;
    }

    presentProgramRef.current = presentProgram;
    presentTexLocRef.current = gl.getUniformLocation(presentProgram, 'uTex');

    const vertices = new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    const posLoc = gl.getAttribLocation(program, 'aPosition');
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    // ✅ Fixed framebuffer creation
    const createFB = (w: number, h: number) => {
      const tex = gl.createTexture();
      if (!tex) return null;
      gl.bindTexture(gl.TEXTURE_2D, tex);

      const useHDR = !!extCBF;
      const internalFormat = useHDR ? gl.RGBA16F : gl.RGBA8;
      const type = useHDR ? (gl.HALF_FLOAT || 0x140B) : gl.UNSIGNED_BYTE;

      gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, w, h, 0, gl.RGBA, type, null);

      const filter = (useHDR && extFloatLinear) ? gl.LINEAR : gl.NEAREST;
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filter);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filter);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

      const fb = gl.createFramebuffer();
      if (!fb) return null;
      gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
      gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);

      const status = gl.checkFramebufferStatus(gl.FRAMEBUFFER);
      if (status !== gl.FRAMEBUFFER_COMPLETE) {
        console.error('Framebuffer incomplete:', status, { useHDR, internalFormat, type });
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        return null;
      }

      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      return { fb, tex, useHDR };
    };

    const w = canvas.clientWidth || 800;
    const h = canvas.clientHeight || 600;
    const fb1 = createFB(w, h);
    const fb2 = createFB(w, h);
    if (!fb1 || !fb2) {
      console.error('Failed to create framebuffers');
      return;
    }
    fbRef.current = { current: fb1.fb, prev: fb2.fb, texCurrent: fb1.tex, texPrev: fb2.tex, useHDR: fb1.useHDR };

    startTimeRef.current = Date.now();

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, []);

  useEffect(() => {
    const gl = glRef.current;
    const program = programRef.current;
    const canvas = canvasRef.current;
    if (!gl || !program || !canvas) return;

    const render = () => {
      if (!isPlaying) {
        animationRef.current = requestAnimationFrame(render);
        return;
      }

      const dw = canvas.clientWidth;
      const dh = canvas.clientHeight;
      
      const useTAA = !!params.enableTemporal;
      
      // Calculate render dimensions with render scale
      const rw = Math.max(1, Math.floor(dw * renderScale));
      const rh = Math.max(1, Math.floor(dh * renderScale));
      
      if (canvas.width !== dw || canvas.height !== dh) {
        canvas.width = dw;
        canvas.height = dh;
        const resizeTex = (tex: WebGLTexture | null, w: number, h: number) => {
          if (!tex) return;
          const useHDR = fbRef.current.useHDR;
          const internalFormat = useHDR ? gl.RGBA16F : gl.RGBA8;
          const type = useHDR ? (gl.HALF_FLOAT || 0x140B) : gl.UNSIGNED_BYTE;
          gl.bindTexture(gl.TEXTURE_2D, tex);
          gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, w, h, 0, gl.RGBA, type, null);
        };
        if (useTAA) {
          resizeTex(fbRef.current.texCurrent, rw, rh);
          resizeTex(fbRef.current.texPrev, rw, rh);
        }
      } else if (useTAA) {
        // Resize textures if render scale changed
        const resizeTex = (tex: WebGLTexture | null, w: number, h: number) => {
          if (!tex) return;
          const useHDR = fbRef.current.useHDR;
          const internalFormat = useHDR ? gl.RGBA16F : gl.RGBA8;
          const type = useHDR ? (gl.HALF_FLOAT || 0x140B) : gl.UNSIGNED_BYTE;
          gl.bindTexture(gl.TEXTURE_2D, tex);
          const currentW = gl.getTexParameter(gl.TEXTURE_2D, gl.TEXTURE_WIDTH) as number;
          const currentH = gl.getTexParameter(gl.TEXTURE_2D, gl.TEXTURE_HEIGHT) as number;
          if (currentW !== w || currentH !== h) {
            gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, w, h, 0, gl.RGBA, type, null);
          }
        };
        resizeTex(fbRef.current.texCurrent, rw, rh);
        resizeTex(fbRef.current.texPrev, rw, rh);
      }

      // Fast path: render directly to screen when TAA is off
      if (!useTAA) {
        gl.viewport(0, 0, dw, dh);
        gl.useProgram(program);
        
        const time = (Date.now() - startTimeRef.current) / 1000;
        
        const INT_UNIFORMS = new Set(['iFrame', 'uPrimarySteps', 'uLightSteps', 'uGodRaySteps']);

        const setU = (name: string, ...args: any[]) => {
          const loc = gl.getUniformLocation(program, name);
          if (loc === null) return;

          if (args.length === 1) {
            const v = args[0];
            if (typeof v === 'boolean') {
              gl.uniform1i(loc, v ? 1 : 0);
            } else if (INT_UNIFORMS.has(name)) {
              gl.uniform1i(loc, (v as number) | 0);
            } else {
              gl.uniform1f(loc, +v);
            }
          } else if (args.length === 2) {
            gl.uniform2f(loc, +args[0], +args[1]);
          } else if (args.length === 3) {
            gl.uniform3f(loc, +args[0], +args[1], +args[2]);
          }
        };

        setU('iTime', time);
        setU('iResolution', dw, dh);
        setU('iFrame', frameRef.current);
        setU('uCameraPos', cameraPos[0], cameraPos[1], cameraPos[2]);
        setU('uCameraYaw', cameraYaw);
        setU('uCameraPitch', cameraPitch);
        setU('uCameraZoom', cameraZoom);

        // Set all params (abbreviated for brevity - same as below)
        // ... (copy all setU calls from the TAA path)
        
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        frameRef.current++;
        animationRef.current = requestAnimationFrame(render);
        return;
      }

      // TAA path: render to FBO, then present
      gl.viewport(0, 0, rw, rh);
      gl.useProgram(program);

      const time = (Date.now() - startTimeRef.current) / 1000;
      
      const INT_UNIFORMS = new Set(['iFrame', 'uPrimarySteps', 'uLightSteps', 'uGodRaySteps']);

      // Don't infer GLSL type from JS number "integer-ness".
      // Many float uniforms receive integer-valued numbers (e.g. 3000, 5.0).
      const setU = (name: string, ...args: any[]) => {
        const loc = gl.getUniformLocation(program, name);
        if (loc === null) return;

        if (args.length === 1) {
          const v = args[0];
          if (typeof v === 'boolean') {
            gl.uniform1i(loc, v ? 1 : 0);
          } else if (INT_UNIFORMS.has(name)) {
            gl.uniform1i(loc, (v as number) | 0);
          } else {
            gl.uniform1f(loc, +v);
          }
        } else if (args.length === 2) {
          gl.uniform2f(loc, +args[0], +args[1]);
        } else if (args.length === 3) {
          gl.uniform3f(loc, +args[0], +args[1], +args[2]);
        }
      };

      setU('iTime', time);
      setU('iResolution', dw, dh);
      setU('iFrame', frameRef.current);
      setU('uCameraPos', cameraPos[0], cameraPos[1], cameraPos[2]);
      setU('uCameraYaw', cameraYaw);
      setU('uCameraPitch', cameraPitch);
      setU('uCameraZoom', cameraZoom);

      // All params
      setU('uCloudDensity', params.cloudDensity);
      setU('uCloudCoverage', params.cloudCoverage);
      setU('uCloudScale', params.cloudScale);
      setU('uDetailScale', params.detailScale);
      setU('uShapeSpeed', params.shapeSpeed);
      setU('uDetailSpeed', params.detailSpeed);
      setU('uCloudHeight', params.cloudHeight);
      setU('uCloudThickness', params.cloudThickness);
      setU('uCloudBrightness', params.cloudBrightness);
      setU('uCloudContrast', params.cloudContrast);
      setU('uCloudShadowDarkness', params.cloudShadowDarkness);
      setU('uCloudShadowSoftness', params.cloudShadowSoftness);

      setU('uLightIntensity', params.lightIntensity);
      setU('uAmbientIntensity', params.ambientIntensity);
      setU('uLightDir', ...params.lightDir);
      setU('uLightColor', ...params.lightColor);
      setU('uAmbientColor', ...params.ambientColor);
      setU('uSilverLiningIntensity', params.silverLiningIntensity);
      setU('uSilverLiningSpread', params.silverLiningSpread);
      setU('uMultiScatter', params.multiScatter);
      setU('uPowderStrength', params.powderStrength);

      setU('uSunSize', params.sunSize);
      setU('uSunBloom', params.sunBloom);
      setU('uSunHaloSize', params.sunHaloSize);
      setU('uSunHaloStrength', params.sunHaloStrength);
      setU('uSkyColorZenith', ...params.skyColorZenith);
      setU('uSkyColorHorizon', ...params.skyColorHorizon);
      setU('uRayleighStrength', params.rayleighStrength);
      setU('uMieStrength', params.mieStrength);
      setU('uMieG', params.mieG);

      setU('uShowStars', params.showStars);
      setU('uStarDensity', params.starDensity);
      setU('uStarBrightness', params.starBrightness);
      setU('uStarTwinkleSpeed', params.starTwinkleSpeed);

      setU('uEnableGodRays', params.enableGodRays);
      setU('uGodRayDensity', params.godRayDensity);
      setU('uGodRayIntensity', params.godRayIntensity);
      setU('uGodRayDecay', params.godRayDecay);
      setU('uGodRaySteps', params.godRaySteps);
      setU('uGodRayColor', ...params.godRayColor);

      setU('uFogDensity', params.fogDensity);
      setU('uFogHeight', params.fogHeight);
      setU('uFogFalloff', params.fogFalloff);
      setU('uFogColor', ...params.fogColor);
      setU('uVolumetricFog', params.volumetricFog);

      setU('uTerrainHeight', params.terrainHeight);
      setU('uMountainHeight', params.mountainHeight);
      setU('uMountainScale', params.mountainScale);
      setU('uMountainSharpness', params.mountainSharpness);
      setU('uGrassColor', ...params.grassColor);
      setU('uDirtColor', ...params.dirtColor);
      setU('uRockColor', ...params.rockColor);
      setU('uSnowColor', ...params.snowColor);
      setU('uSnowLine', params.snowLine);
      setU('uShowTerrain', params.showTerrain);

      setU('uShowCity', params.showCity);
      setU('uCityDistance', params.cityDistance);
      setU('uCityDensity', params.cityDensity);
      setU('uBuildingHeight', params.buildingHeight);
      setU('uBuildingColor', ...params.buildingColor);
      setU('uWindowGlow', params.windowGlow);

      setU('uShowWater', params.showWater);
      setU('uWaterLevel', params.waterLevel);
      setU('uWaterColor', ...params.waterColor);
      setU('uWaterDeepColor', ...params.waterDeepColor);
      setU('uWaveHeight', params.waveHeight);
      setU('uWaveFrequency', params.waveFrequency);
      setU('uWaveSpeed', params.waveSpeed);
      setU('uWaterReflectivity', params.waterReflectivity);
      setU('uWaterRoughness', params.waterRoughness);
      setU('uWaterFresnel', params.waterFresnel);
      setU('uShowCaustics', params.showCaustics);
      setU('uCausticsStrength', params.causticsStrength);

      setU('uPrimarySteps', params.primarySteps);
      setU('uLightSteps', params.lightSteps);
      setU('uTemporalBlend', params.temporalBlend);
      setU('uEnableTemporal', params.enableTemporal);

      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, fbRef.current.texPrev);
      gl.uniform1i(gl.getUniformLocation(program, 'uPrevFrame'), 0);

      gl.bindFramebuffer(gl.FRAMEBUFFER, fbRef.current.current);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

      const temp = fbRef.current.current;
      fbRef.current.current = fbRef.current.prev;
      fbRef.current.prev = temp;
      const tempTex = fbRef.current.texCurrent;
      fbRef.current.texCurrent = fbRef.current.texPrev;
      fbRef.current.texPrev = tempTex;

      frameRef.current++;
      animationRef.current = requestAnimationFrame(render);
    };

    render();
    return () => { if (animationRef.current) cancelAnimationFrame(animationRef.current); };
  }, [isPlaying, params, cameraPos, cameraYaw, cameraPitch, cameraZoom]);

  const handleMouseDown = (e: React.MouseEvent) => {
    isDraggingRef.current = true;
    lastMouseRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => { isDraggingRef.current = false; };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    const dx = e.clientX - lastMouseRef.current.x;
    const dy = e.clientY - lastMouseRef.current.y;
    
    if (e.shiftKey) {
      setCameraPos(prev => [prev[0] - dx * 8, prev[1] + dy * 8, prev[2]]);
    } else {
      setCameraYaw(prev => prev + dx * 0.004);
      setCameraPitch(prev => Math.max(-Math.PI/2 + 0.1, Math.min(Math.PI/2 - 0.1, prev - dy * 0.004)));
    }
    lastMouseRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    setCameraZoom(prev => Math.max(0.5, Math.min(2.0, prev + e.deltaY * 0.001)));
  };

  const SliderControl = ({ label, value, min, max, step, onChange, format }: any) => (
    <div className="space-y-1" onClick={(e) => e.stopPropagation()}>
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-300 font-mono text-[10px]">{format ? format(value) : value.toFixed(2)}</span>
      </div>
      <Slider value={[value]} min={min} max={max} step={step} onValueChange={([v]) => onChange(v)} className="cursor-pointer" />
    </div>
  );

  const SectionHeader = ({ children }: { children: React.ReactNode }) => (
    <div className="text-[10px] uppercase tracking-wider text-gray-500 font-semibold mt-4 mb-2 first:mt-0">{children}</div>
  );

  const renderPanelContent = () => {
    switch(activePanel) {
      case 'clouds':
        return (
          <div className="space-y-3">
            <SectionHeader>Shape</SectionHeader>
            <SliderControl label="Density" value={params.cloudDensity} min={0.1} max={5} step={0.1} onChange={(v: number) => updateParam('cloudDensity', v)} />
            <SliderControl label="Coverage" value={params.cloudCoverage} min={0} max={1} step={0.01} onChange={(v: number) => updateParam('cloudCoverage', v)} format={(v: number) => `${(v*100).toFixed(0)}%`} />
            <SliderControl label="Scale" value={params.cloudScale} min={1} max={20} step={0.5} onChange={(v: number) => updateParam('cloudScale', v)} />
            <SliderControl label="Detail" value={params.detailScale} min={5} max={50} step={1} onChange={(v: number) => updateParam('detailScale', v)} />
            <SectionHeader>Position</SectionHeader>
            <SliderControl label="Height" value={params.cloudHeight} min={500} max={6000} step={100} onChange={(v: number) => updateParam('cloudHeight', v)} format={(v: number) => `${v.toFixed(0)}m`} />
            <SliderControl label="Thickness" value={params.cloudThickness} min={500} max={8000} step={100} onChange={(v: number) => updateParam('cloudThickness', v)} format={(v: number) => `${v.toFixed(0)}m`} />
            <SectionHeader>Animation</SectionHeader>
            <SliderControl label="Shape Speed" value={params.shapeSpeed} min={0} max={3} step={0.1} onChange={(v: number) => updateParam('shapeSpeed', v)} />
            <SliderControl label="Detail Speed" value={params.detailSpeed} min={0} max={5} step={0.1} onChange={(v: number) => updateParam('detailSpeed', v)} />
            <SectionHeader>Appearance</SectionHeader>
            <SliderControl label="Brightness" value={params.cloudBrightness} min={0.5} max={5} step={0.1} onChange={(v: number) => updateParam('cloudBrightness', v)} />
            <SliderControl label="Contrast" value={params.cloudContrast} min={0.5} max={2} step={0.05} onChange={(v: number) => updateParam('cloudContrast', v)} />
          </div>
        );
      case 'shadows':
        return (
          <div className="space-y-3">
            <SectionHeader>Cloud Shadows</SectionHeader>
            <SliderControl label="Darkness" value={params.cloudShadowDarkness} min={0.1} max={1} step={0.05} onChange={(v: number) => updateParam('cloudShadowDarkness', v)} />
            <SliderControl label="Softness" value={params.cloudShadowSoftness} min={0.5} max={2} step={0.1} onChange={(v: number) => updateParam('cloudShadowSoftness', v)} />
            <SectionHeader>Scattering</SectionHeader>
            <SliderControl label="Multi-Scatter" value={params.multiScatter} min={0} max={1} step={0.05} onChange={(v: number) => updateParam('multiScatter', v)} />
            <SliderControl label="Powder Effect" value={params.powderStrength} min={0} max={3} step={0.1} onChange={(v: number) => updateParam('powderStrength', v)} />
            <SliderControl label="Silver Lining" value={params.silverLiningIntensity} min={0} max={3} step={0.1} onChange={(v: number) => updateParam('silverLiningIntensity', v)} />
            <SliderControl label="Silver Spread" value={params.silverLiningSpread} min={1} max={10} step={0.5} onChange={(v: number) => updateParam('silverLiningSpread', v)} />
          </div>
        );
      case 'lighting':
        return (
          <div className="space-y-3">
            <SectionHeader>Sun</SectionHeader>
            <SliderControl label="Intensity" value={params.lightIntensity} min={0} max={5} step={0.1} onChange={(v: number) => updateParam('lightIntensity', v)} />
            <SliderControl label="Height" value={params.lightDir[1]} min={-0.5} max={1} step={0.01} onChange={(v: number) => updateParam('lightDir', [params.lightDir[0], v, params.lightDir[2]])} />
            <SliderControl label="Azimuth" value={params.lightDir[0]} min={-1} max={1} step={0.01} onChange={(v: number) => updateParam('lightDir', [v, params.lightDir[1], params.lightDir[2]])} />
            <SectionHeader>Sun Appearance</SectionHeader>
            <SliderControl label="Size" value={params.sunSize} min={1} max={20} step={0.5} onChange={(v: number) => updateParam('sunSize', v)} />
            <SliderControl label="Bloom" value={params.sunBloom} min={0} max={10} step={0.5} onChange={(v: number) => updateParam('sunBloom', v)} />
            <SliderControl label="Halo Size" value={params.sunHaloSize} min={0.5} max={5} step={0.25} onChange={(v: number) => updateParam('sunHaloSize', v)} />
            <SliderControl label="Halo Strength" value={params.sunHaloStrength} min={0} max={2} step={0.1} onChange={(v: number) => updateParam('sunHaloStrength', v)} />
            <SectionHeader>Ambient</SectionHeader>
            <SliderControl label="Ambient" value={params.ambientIntensity} min={0} max={1} step={0.05} onChange={(v: number) => updateParam('ambientIntensity', v)} />
          </div>
        );
      case 'atmosphere':
        return (
          <div className="space-y-3">
            <SectionHeader>Scattering</SectionHeader>
            <SliderControl label="Rayleigh" value={params.rayleighStrength} min={0} max={2} step={0.1} onChange={(v: number) => updateParam('rayleighStrength', v)} />
            <SliderControl label="Mie" value={params.mieStrength} min={0} max={2} step={0.1} onChange={(v: number) => updateParam('mieStrength', v)} />
            <SliderControl label="Mie Anisotropy" value={params.mieG} min={0.5} max={0.99} step={0.01} onChange={(v: number) => updateParam('mieG', v)} />
          </div>
        );
      case 'stars':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-xs text-gray-400">Show Stars</span>
              <Switch checked={params.showStars} onCheckedChange={(v) => updateParam('showStars', v)} />
            </div>
            {params.showStars && (
              <>
                <SliderControl label="Density" value={params.starDensity} min={0.5} max={3} step={0.1} onChange={(v: number) => updateParam('starDensity', v)} />
                <SliderControl label="Brightness" value={params.starBrightness} min={0.5} max={5} step={0.1} onChange={(v: number) => updateParam('starBrightness', v)} />
                <SliderControl label="Twinkle Speed" value={params.starTwinkleSpeed} min={0} max={5} step={0.25} onChange={(v: number) => updateParam('starTwinkleSpeed', v)} />
              </>
            )}
          </div>
        );
      case 'godrays':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-xs text-gray-400">Enable God Rays</span>
              <Switch checked={params.enableGodRays} onCheckedChange={(v) => updateParam('enableGodRays', v)} />
            </div>
            {params.enableGodRays && (
              <>
                <SliderControl label="Density" value={params.godRayDensity} min={0.1} max={2} step={0.1} onChange={(v: number) => updateParam('godRayDensity', v)} />
                <SliderControl label="Intensity" value={params.godRayIntensity} min={0} max={5} step={0.1} onChange={(v: number) => updateParam('godRayIntensity', v)} />
                <SliderControl label="Decay" value={params.godRayDecay} min={0.5} max={2} step={0.1} onChange={(v: number) => updateParam('godRayDecay', v)} />
                <SliderControl label="Steps" value={params.godRaySteps} min={16} max={64} step={8} onChange={(v: number) => updateParam('godRaySteps', v)} format={(v: number) => v.toFixed(0)} />
              </>
            )}
          </div>
        );
      case 'fog':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-xs text-gray-400">Volumetric Fog</span>
              <Switch checked={params.volumetricFog} onCheckedChange={(v) => updateParam('volumetricFog', v)} />
            </div>
            <SliderControl label="Density" value={params.fogDensity} min={0} max={1} step={0.01} onChange={(v: number) => updateParam('fogDensity', v)} />
            <SliderControl label="Height" value={params.fogHeight} min={100} max={2000} step={50} onChange={(v: number) => updateParam('fogHeight', v)} format={(v: number) => `${v.toFixed(0)}m`} />
            <SliderControl label="Falloff" value={params.fogFalloff} min={0.5} max={5} step={0.25} onChange={(v: number) => updateParam('fogFalloff', v)} />
          </div>
        );
      case 'terrain':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-xs text-gray-400">Show Terrain</span>
              <Switch checked={params.showTerrain} onCheckedChange={(v) => updateParam('showTerrain', v)} />
            </div>
            <SectionHeader>Mountains</SectionHeader>
            <SliderControl label="Height" value={params.mountainHeight} min={0} max={5000} step={100} onChange={(v: number) => updateParam('mountainHeight', v)} format={(v: number) => `${v.toFixed(0)}m`} />
            <SliderControl label="Scale" value={params.mountainScale} min={0.5} max={3} step={0.1} onChange={(v: number) => updateParam('mountainScale', v)} />
            <SliderControl label="Sharpness" value={params.mountainSharpness} min={1} max={4} step={0.25} onChange={(v: number) => updateParam('mountainSharpness', v)} />
            <SectionHeader>Snow</SectionHeader>
            <SliderControl label="Snow Line" value={params.snowLine} min={500} max={4000} step={100} onChange={(v: number) => updateParam('snowLine', v)} format={(v: number) => `${v.toFixed(0)}m`} />
          </div>
        );
      case 'water':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-xs text-gray-400">Show Water</span>
              <Switch checked={params.showWater} onCheckedChange={(v) => updateParam('showWater', v)} />
            </div>
            {params.showWater && (
              <>
                <SliderControl label="Water Level" value={params.waterLevel} min={0} max={1000} step={25} onChange={(v: number) => updateParam('waterLevel', v)} format={(v: number) => `${v.toFixed(0)}m`} />
                <SectionHeader>Waves (Gerstner)</SectionHeader>
                <SliderControl label="Wave Height" value={params.waveHeight} min={0} max={5} step={0.1} onChange={(v: number) => updateParam('waveHeight', v)} />
                <SliderControl label="Frequency" value={params.waveFrequency} min={0.5} max={3} step={0.1} onChange={(v: number) => updateParam('waveFrequency', v)} />
                <SliderControl label="Speed" value={params.waveSpeed} min={0} max={3} step={0.1} onChange={(v: number) => updateParam('waveSpeed', v)} />
                <SectionHeader>Surface</SectionHeader>
                <SliderControl label="Reflectivity" value={params.waterReflectivity} min={0} max={1} step={0.05} onChange={(v: number) => updateParam('waterReflectivity', v)} />
                <SliderControl label="Roughness" value={params.waterRoughness} min={0} max={1} step={0.05} onChange={(v: number) => updateParam('waterRoughness', v)} />
                <SliderControl label="Fresnel" value={params.waterFresnel} min={1} max={5} step={0.25} onChange={(v: number) => updateParam('waterFresnel', v)} />
                <div className="flex items-center justify-between mt-2" onClick={(e) => e.stopPropagation()}>
                  <span className="text-xs text-gray-400">Caustics</span>
                  <Switch checked={params.showCaustics} onCheckedChange={(v) => updateParam('showCaustics', v)} />
                </div>
                {params.showCaustics && (
                  <SliderControl label="Caustics Strength" value={params.causticsStrength} min={0} max={2} step={0.1} onChange={(v: number) => updateParam('causticsStrength', v)} />
                )}
              </>
            )}
          </div>
        );
      case 'city':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-xs text-gray-400">Show City</span>
              <Switch checked={params.showCity} onCheckedChange={(v) => updateParam('showCity', v)} />
            </div>
            {params.showCity && (
              <>
                <SliderControl label="Distance" value={params.cityDistance} min={2000} max={30000} step={500} onChange={(v: number) => updateParam('cityDistance', v)} format={(v: number) => `${(v/1000).toFixed(1)}km`} />
                <SliderControl label="Density" value={params.cityDensity} min={0.3} max={1} step={0.05} onChange={(v: number) => updateParam('cityDensity', v)} />
                <SliderControl label="Building Height" value={params.buildingHeight} min={100} max={1500} step={50} onChange={(v: number) => updateParam('buildingHeight', v)} format={(v: number) => `${v.toFixed(0)}m`} />
                <SliderControl label="Window Glow" value={params.windowGlow} min={0} max={2} step={0.1} onChange={(v: number) => updateParam('windowGlow', v)} />
              </>
            )}
          </div>
        );
      case 'quality':
        return (
          <div className="space-y-3">
            <SliderControl label="Ray Steps" value={params.primarySteps} min={24} max={96} step={8} onChange={(v: number) => updateParam('primarySteps', v)} format={(v: number) => v.toFixed(0)} />
            <SliderControl label="Light Steps" value={params.lightSteps} min={3} max={10} step={1} onChange={(v: number) => updateParam('lightSteps', v)} format={(v: number) => v.toFixed(0)} />
            <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
              <span className="text-xs text-gray-400">Temporal AA</span>
              <Switch checked={params.enableTemporal} onCheckedChange={(v) => updateParam('enableTemporal', v)} />
            </div>
            {params.enableTemporal && (
              <SliderControl label="Blend Factor" value={params.temporalBlend} min={0.5} max={0.95} step={0.01} onChange={(v: number) => updateParam('temporalBlend', v)} format={(v: number) => `${(v*100).toFixed(0)}%`} />
            )}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black flex">
      <div className={`flex-1 relative ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing"
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onMouseMove={handleMouseMove}
          onWheel={handleWheel}
        />
        
        <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-b from-black/70 to-transparent flex items-center px-4 gap-3">
          <Cloud className="w-5 h-5 text-cyan-400" />
          <span className="text-white font-medium">Volumetric Engine</span>
          <Badge variant="outline" className="text-[10px] border-gray-600">v4.0</Badge>
          
          <div className="flex-1" />
          
          <span className="text-[10px] text-gray-400 hidden md:block">Drag: Rotate | Shift+Drag: Pan | Scroll: Zoom</span>
          
          <Select onValueChange={applyPreset}>
            <SelectTrigger className="w-36 h-8 bg-black/50 border-gray-700 text-xs">
              <SelectValue placeholder="Presets..." />
            </SelectTrigger>
            <SelectContent className="max-h-[400px]">
              <div className="px-2 py-1.5 text-[10px] font-semibold text-gray-400 uppercase">Default Presets</div>
              {Object.keys(defaultPresets).map(name => (
                <SelectItem key={name} value={name} className="text-xs">{name}</SelectItem>
              ))}
              {Object.keys(savedPresets).length > 0 && (
                <>
                  <div className="px-2 py-1.5 text-[10px] font-semibold text-gray-400 uppercase mt-2 border-t border-gray-700">Saved Presets</div>
                  {Object.keys(savedPresets).map(name => (
                    <SelectItem key={name} value={name} className="text-xs">{name}</SelectItem>
                  ))}
                </>
              )}
            </SelectContent>
          </Select>
          
          <Button variant="ghost" size="icon" onClick={() => setShowPresetDialog(true)} className="w-8 h-8 text-gray-400 hover:text-white">
            <Save className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setIsPlaying(!isPlaying)} className="w-8 h-8 text-gray-400 hover:text-white">
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <Button variant="ghost" size="icon" onClick={resetCamera} className="w-8 h-8 text-gray-400 hover:text-white">
            <Camera className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setIsFullscreen(!isFullscreen)} className="w-8 h-8 text-gray-400 hover:text-white">
            {isFullscreen ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
          </Button>
        </div>

        <div className="absolute bottom-4 left-4 text-xs text-white/40 font-mono">
          Frame: {frameRef.current} | TAA: {params.enableTemporal ? 'ON' : 'OFF'}
        </div>
      </div>

      {!isFullscreen && (
        <div className="w-72 bg-gray-950 border-l border-gray-800 flex">
          <div className="w-12 bg-gray-900 flex flex-col items-center py-2 gap-0.5 overflow-y-auto">
            {settingsPanels.map(panel => (
              <Button
                key={panel.id}
                variant="ghost"
                size="icon"
                onClick={() => setActivePanel(panel.id)}
                className={`w-10 h-10 flex-shrink-0 ${activePanel === panel.id ? 'bg-cyan-600 text-white' : 'text-gray-500 hover:text-white hover:bg-gray-800'}`}
                title={panel.label}
              >
                <panel.icon className="w-4 h-4" />
              </Button>
            ))}
          </div>
          
          <div className="flex-1 flex flex-col">
            <div className="h-10 border-b border-gray-800 flex items-center px-4">
              <span className="text-sm font-medium text-white">{settingsPanels.find(p => p.id === activePanel)?.label}</span>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-3">
                {renderPanelContent()}
              </div>
            </ScrollArea>
          </div>
        </div>
      )}

      <Dialog open={showPresetDialog} onOpenChange={setShowPresetDialog}>
        <DialogContent className="bg-gray-900 border-gray-800 max-w-md">
          <DialogHeader>
            <DialogTitle className="text-white">Save & Manage Presets</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm text-gray-300">Save Current Settings</label>
              <div className="flex gap-2">
                <Input 
                  value={presetName} 
                  onChange={(e) => setPresetName(e.target.value)} 
                  placeholder="Preset name..." 
                  className="bg-gray-800 border-gray-700 flex-1"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') savePreset();
                  }}
                />
                <Button onClick={savePreset} disabled={!presetName.trim()}>Save</Button>
              </div>
            </div>
            
            {Object.keys(savedPresets).length > 0 && (
              <div className="space-y-2">
                <label className="text-sm text-gray-300">Saved Presets</label>
                <ScrollArea className="h-48 border border-gray-700 rounded-md bg-gray-800/50">
                  <div className="p-2 space-y-1">
                    {Object.keys(savedPresets).map(name => (
                      <div key={name} className="flex items-center justify-between p-2 hover:bg-gray-700/50 rounded">
                        <span className="text-sm text-gray-200">{name}</span>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              applyPreset(name);
                              setShowPresetDialog(false);
                            }}
                            className="h-7 px-2 text-xs"
                          >
                            Load
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deletePreset(name)}
                            className="h-7 px-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-900/20"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}