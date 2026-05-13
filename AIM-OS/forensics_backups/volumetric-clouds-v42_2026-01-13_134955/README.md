# Volumetric Clouds Engine v4.2

Real-time volumetric cloud rendering engine with terrain, water, and atmospheric effects.

## Features

- **Volumetric Cloud Rendering**: Real-time ray-marched clouds with advanced lighting
- **Terrain System**: Procedural mountains with snow lines and varied materials
- **Water Rendering**: Realistic water with reflections, caustics, and Gerstner waves
- **Atmospheric Scattering**: Physically-based sky rendering with Rayleigh and Mie scattering
- **God Rays**: Volumetric light shafts from clouds
- **City Skyline**: Procedural city silhouette with window glow
- **Stars**: Twinkling starfield for night scenes
- **Volumetric Fog**: Height-based fog with noise variation
- **Temporal Anti-Aliasing**: Smooth rendering with frame blending
- **Preset System**: Save and load custom configurations

## Quick Start

### Launch the App

Double-click `launch.bat` or run:

```bash
npm install
npm run dev
```

The app will open automatically in your browser at `http://localhost:3003`

### Controls

- **Drag**: Rotate camera
- **Shift + Drag**: Pan camera
- **Scroll**: Zoom in/out
- **Presets**: Select from dropdown menu
- **Settings**: Adjust parameters in the side panel

## Presets

The app includes several built-in presets:

- **Mountain Lake**: Serene mountain scene with water
- **City Sunset**: Urban sunset with dramatic lighting
- **Ocean Storm**: Stormy ocean scene with heavy clouds
- **Alpine Dawn**: Mountain sunrise with clear skies
- **Night City**: Nighttime cityscape with stars

## Settings Panels

- **Clouds**: Shape, position, animation, and appearance
- **Shadows**: Cloud shadow darkness, softness, and scattering
- **Sun/Light**: Sun position, intensity, and appearance
- **Sky**: Atmospheric scattering parameters
- **Stars**: Starfield density, brightness, and twinkle
- **God Rays**: Volumetric light shaft settings
- **Fog**: Volumetric fog density and height
- **Terrain**: Mountain height, scale, and snow line
- **Water**: Wave parameters, reflectivity, and caustics
- **City**: Building density, height, and window glow
- **Quality**: Ray marching steps and temporal AA

## Technical Details

- **WebGL 2.0**: Uses WebGL2 for advanced rendering features
- **Ray Marching**: Volumetric rendering with adaptive step sizes
- **Temporal AA**: Frame blending for smooth anti-aliasing
- **Performance**: Optimized with LOD and distance-based quality

## Requirements

- Modern browser with WebGL 2.0 support
- Node.js 18+ and npm
- GPU recommended for best performance

## Version

v4.2 - Performance optimized with coherent shadows/god rays
