# Deep Think Response: Project Leviathan — Master Architecture Blueprint

**Date saved:** 2026-02-22  
**Source:** Gemini 3 Deep Think  
**Topic:** Master architecture for planetary-scale ocean/globe rendering and hybrid hydrodynamics engine.  
**Pack:** Standalone (not from a numbered handoff pack).

---

## Full response (verbatim)

---

🌍 **PROJECT LEVIATHAN: Master Architecture Blueprint**

### MODULE 1: The Engine Core & Infinite Precision

You cannot render a 1:1 Earth globe (R=6,371 km) and a 1-millimeter water droplet in the same coordinate space using standard 32-bit floats. The engine will suffer from catastrophic floating-point jitter.

- **The WebGPU Compute Foundation:** Move all wave evaluations, particle physics, and foam advection off the CPU. The CPU should only handle UI state and camera matrices. WebGPU Compute Shaders will allow us to simulate millions of fluid particles instead of a 15k CPU limit.

- **Camera-Relative Rendering (RTE - Relative To Eye):** Store planetary geometry in double-precision (Float64) on the CPU. Send the Camera Position and Vertex Positions to the GPU as High and Low 32-bit float pairs. Calculate the difference in the shader. This guarantees millimeter precision at planetary distances.

- **Spherical Quadtree (CDLOD):** Replace the flat PlaneGeometry with a Continuous Distance-Dependent Level of Detail Cube-Sphere. As the camera descends from space, the sphere dynamically subdivides exactly where the camera is looking, providing limitless geometry density right at the wave crests while culling the rest of the planet.

- **Reversed-Z / Logarithmic Depth Buffer:** Crucial for eliminating z-fighting when transitioning from 10,000 km in space down to 0.1 meters above the water.

---

### MODULE 2: The 5-Tier Hybrid Hydrodynamics Engine

Gerstner waves are fantastic for steep crests, but they are limited to a handful of octaves. Real oceans consist of millions of overlapping wave spectra. We must use a nested, multi-scale architecture:

- **Tier 1: Planetary Macro-Scale (Cascaded FFT):** 4 to 6 cascades of Fast Fourier Transform (FFT) grids using JONSWAP or TMA spectral models, evaluated on WebGPU Compute Shaders. This provides chaotic, non-repeating, infinitely tiling deep-water displacement that drives the ocean's massive swells.

- **Tier 2: Hero Breakers (Spectral Gerstner Injector):** Extract the highest amplitude peaks from the FFT and locally inject explicit Gerstner functions aligned with the wind direction. We use these to shape the sharp, curling crests and explicitly calculate the exact moment of breaking (Jacobian folding).

- **Tier 3: Interaction Scale (Shallow Water Equations - SWE):** A moving 2.5D heightfield grid centered around the camera. This mathematically calculates boat wakes (Kelvin wakes), shoreline diffraction, and object buoyancy.

- **Tier 4: High-Frequency Micro-facets:** Dual-layered Fractional Brownian Motion (fBm) evaluated per-pixel in the fragment shader to perturb normals, giving the water that glassy, wind-sheared capillary look.

- **Tier 5: 3D Breaching (MLS-MPM / SPH):** When the Jacobian determinant of the surface hits < 0, the mesh tears. The wave energy seamlessly spawns GPU Compute Particles that follow true fluid dynamics.

---

### MODULE 3: Multi-Phase Fluid Breach & Foam System

When a wave breaks, water transitions from a connected mathematical surface into a chaotic multi-phase fluid.

- **Airborne Spray (SPH/MPM):** Particles spawned at the crest inherit the wave's orbital velocity. They simulate aerodynamic drag, gravity, and particle-particle collisions (Smoothed Particle Hydrodynamics) so the spray clumps together realistically into droplets rather than passing through each other.

- **Sub-Surface Bubbles:** When spray hits the surface, it transfers momentum and pushes bubble particles beneath the ocean mesh. These drift upward based on buoyancy and advect along the underwater currents, catching subsurface scattered light.

- **Eulerian Surface Foam (Optical Flow):** Foam must not be a static texture. It is injected into an Eulerian grid texture by the splashing particles. A compute shader then advects (smears and stretches) this texture using the horizontal velocity vectors of the FFT waves. This creates the beautiful, thread-like marbling of sea foam (Langmuir circulation) that persists and decays realistically.

---

### MODULE 4: Hyper-Realistic Optics & Atmosphere

Lighting water correctly requires simulating exactly what happens to photons entering a dense medium.

- **Planetary Atmosphere (Bruneton/Hillaire Model):** Upgrade from Nishita to a scalable multiple-scattering atmospheric model. This handles light bouncing off air molecules multiple times, giving true Earth-orbit realism, blood-red sunsets, Earth's shadow (the Terminator line), and accurate twilight ozone absorption.

- **Volumetric Raymarched Clouds:** Driven by 3D Worley-Perlin noise, casting physically accurate god-rays and soft shadows onto and into the ocean volume.

- **Jerlov Water Types (Spectral Absorption):** Water isn't a blue surface; it's a volume. Implement Beer-Lambert law integration with specific spectral extinction coefficients. Deep water absorbs red/green completely; shallow water allows light to hit the sea floor and scatter back.

- **Subsurface Scattering (SSS):** Calculate the "optical thickness" of the wave crest using the dot product of the View vector and Inverse Light vector. Sunlight penetrating the back of a wave crest scatters via a Henyey-Greenstein phase function, creating a glowing jade/teal translucency.

- **Dual-Lobe BRDF & SSR:** Water needs two specular reflections: one perfectly smooth (for sharp sun reflections/SSR) and one micro-faceted (driven by capillary waves) to create the wide "sun glint". Screen Space Local Reflections (SSLR) allow waves to reflect the clouds, ships, and other waves.

---

### 🎛️ THE "GOD MODE" OMNI-UI SETTINGS SCHEMA

To expose every parameter of this engine, a simple list of sliders will fail. The UI must be a Node-based or Matrix-layered GUI (similar to advanced DAWs or Blender).

**Master schema for UI tree:**

1. **🌍 Planetary & Celestial Matrix**  
   Orbital Mechanics: Time of Day, Julian Date, Latitude/Longitude, Earth Axial Tilt, Moon Phase (drives tides/lighting).  
   Atmospheric Optics: Rayleigh Scattering Vector (RGB), Mie Coefficient, Mie Phase Anisotropy (g-factor), Ozone Absorption, Multi-scattering Multiplier.  
   Lighting: Sun Illuminance (Lux), Star Field Exposure, Earthshine.

2. **🌊 Macro Wave Engine (FFT & Swell)**  
   Spectrum Type: Phillips, JONSWAP, TMA, Pierson-Moskowitz.  
   JONSWAP Params: Fetch Length, Wind Speed at 10m (U10), Phillips Constant (α), Peak Enhancement Factor (γ).  
   FFT Settings: Grid Resolution (1024 to 4096), Physical Domain Size, Choppiness Factor (λ).  
   Global Wind: Primary Heading, Wind Variance, Gust Frequency.

3. **🏄 Meso Wave Engine (Gerstner Shape Overrides)**  
   Gerstner Layers [1-16]: Amplitude, Wavelength, Speed, Steepness (Q), Directional Variance.  
   Non-Linearity: Skewness (horizontal wave leaning), Asymmetry (vertical wave pitching).

4. **💥 Multi-Phase Breach & Particle Dynamics**  
   Jacobian Triggers: Folding Threshold (J<x), Crest Height Threshold, Steepness Threshold.  
   MPM Spray (Airborne): Gravity Vector, Aerodynamic Drag, Particle Mass, Droplet Cohesion (Surface Tension).  
   Sub-Surface Bubbles: Buoyancy Force, Dissolve Rate, Max Depth Advection.  
   Surface Foam (Eulerian): Generation Rate, Marbling/Advection Strength, Decay/Popping Rate, Micro-texture scale (fBm noise overlay).

5. **🎨 Oceanic Optics & Shading**  
   Jerlov Water Type: (Dropdown: Coastal, Oceanic I, Oceanic II, Muddy, etc.).  
   Absorption Spectrum: Extinction coefficients for R, G, B at 1m depth.  
   Volume Scattering: Particulate Density (plankton/silt), Backscatter Intensity.  
   Surface Shading: Index of Refraction (IOR), Roughness (Microfacet GGX), Specular Broadness.  
   Subsurface Scattering (SSS): Crest Translucency Multiplier, Phase Function.

---

### 📚 DEEP RESEARCH NETWORK (The "Secret Sauce" Index)

- **"Simulating Ocean Water"** (Jerry Tessendorf, 2001): The absolute bible for FFT ocean rendering. Implement this for the base layer to move beyond Gerstner.

- **"A Scalable and Production Ready Sky and Atmosphere Rendering Technique"** (Sébastien Hillaire, 2020): Modern standard for real-time planetary atmospheres (Unreal Engine 5). Far superior to basic Nishita.

- **"Material Point Method (MPM) for Snow and Water"** (Stomakhin et al. / Disney Animation, 2013): Math behind hyper-realistic splash physics. Adapt to WebGPU compute for true fluid splashes.

- **"Real-Time Fluid Dynamics for Games"** (Jos Stam): Eulerian grid for shallow water/wake simulation and foam advection.

- **"Screen Space Fluid Rendering"** (van der Laan et al., 2009): Render spray as spheres to depth buffer, blur (curvature flow), generate normals — cohesive liquid splash look.

- **"Precision in Earth-Scale Rendering"** (Cozzi / Cesium, 2011): Mandatory for fixing 32-bit floating-point precision at planetary scale.

---

### 🚀 PROJECT EXECUTION ROADMAP

Proceed in this strict order (do not build monolithically):

- **PHASE 1: The Engine Rebuild** — Modern repo: Vite + TypeScript + Three.js (WebGPU backend / WebGPURenderer) or raw WGSL.

- **PHASE 2: The Infinite Globe** — Cube-Sphere CDLOD Quadtree geometry. Relative-to-Eye (RTE) rendering for zero jitter from 1 mm to 100,000 km.

- **PHASE 3: The Math Offload (FFT)** — Compute shaders for Cascaded FFT ocean. Analytical normals and Jacobian determinant per vertex on GPU. Layer explicit Gerstner for "Hero" waves.

- **PHASE 4: Shading & Subsurface** — Hillaire atmospheric multiple-scattering, 3-color Beer-Lambert absorption, Subsurface Scattering (inverted Normal dot Light).

- **PHASE 5: Particle & Foam Compute** — WebGPU compute particle system. SPH compute for spray. Eulerian grid compute for foam advection and reaction-diffusion.

- **PHASE 6: The Ultimate UI** — State manager (e.g. Zustand) + UI library (Leva, Tweakpane, or custom React overlay). Hook 200+ parameters to WebGPU uniform buffers.

---

*End of Deep Think response.*
