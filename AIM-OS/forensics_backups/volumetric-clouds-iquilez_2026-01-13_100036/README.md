# Inigo Quilez Volumetric Clouds

A WebGL2 harness for running Inigo Quilez's volumetric cloud shader locally.

## Overview

This is a standalone WebGL2 harness that runs the volumetric cloud shader by Inigo Quilez. The shader implements volumetric raymarching with fBM noise to create realistic-looking clouds.

## Features

- **Volumetric Raymarching**: Real-time volumetric cloud rendering
- **Interactive Camera**: Drag mouse to rotate camera view
- **Two Look Modes**: Sunset look (LOOK=0) and bright look (LOOK=1)
- **LOD Support**: Optional level-of-detail for performance
- **Multiple Noise Methods**: Hardware and software interpolation options

## Requirements

- Modern browser with WebGL2 support
- Python 3.x (for local development server)

## Quick Start

### Option 1: Using the Launcher Script (Windows)

**Batch file:**
```bash
launch.bat
```

**PowerShell:**
```powershell
.\launch.ps1
```

### Option 2: Manual Setup

1. Serve this folder using any HTTP server (required for module loading):
   ```bash
   # Python 3
   python -m http.server 5174
   
   # Or Node.js
   npx http-server -p 5174
   ```

2. Open `http://localhost:5174` in a modern browser

3. Drag mouse to rotate the camera view

## Controls

- **Mouse Drag**: Rotate camera around the cloud scene
- The camera automatically orbits based on mouse position

## Shader Configuration

The shader supports several compile-time defines:

- `LOOK`: 0 = sunset look, 1 = bright look (default: 1)
- `NOISE_METHOD`: 0 = 3D texture, 1 = 2D textures with hardware interpolation (default: 1), 2 = 2D textures with software interpolation
- `USE_LOD`: 0 = no LOD, 1 = yes LOD (default: 1)

Edit `shaders/clouds.glsl` to change these values.

## Technical Details

### Shadertoy Uniforms

The harness implements standard Shadertoy uniforms:
- `iResolution`: Canvas resolution (vec3)
- `iTime`: Time in seconds (float)
- `iMouse`: Mouse position (vec2)
- `iChannel0`: 2D noise texture (256x256)
- `iChannel1`: Blue noise/dither texture (1024x1024)
- `iChannel2`: 3D noise texture (32x32x32, flattened to 2D)

### Noise Textures

The harness generates simple procedural noise textures:
- **iChannel0**: 2D noise for fBM sampling (used with NOISE_METHOD=1)
- **iChannel1**: Blue noise for dithering raymarch steps
- **iChannel2**: 3D noise (used with NOISE_METHOD=0, currently flattened to 2D)

For production use, you may want to replace these with proper noise textures.

## Performance

- The shader uses adaptive raymarching with LOD for performance
- Performance depends on:
  - Number of raymarch steps (controlled by `kDiv` constant)
  - LOD level (controlled by `USE_LOD` define)
  - Canvas resolution

## License

**Important**: This shader is copyright Inigo Quilez, 2013. See the license header in `shaders/clouds.glsl` for full terms.

This work is shared for educational purposes only. You cannot:
- Host, display, distribute or share this work (as-is or altered)
- Use in commercial or non-commercial products
- Sell this work or mint NFTs
- Use to train AI models

For commercial use, please contact Inigo Quilez directly.

## Credits

- **Shader**: Inigo Quilez (https://iquilezles.org/)
- **Harness**: WebGL2 implementation for local development

## Notes

- The shader is not physically correct (as noted in the comments)
- It works in sRGB instead of linear RGB
- No shadows or proper scattering are computed
- It's designed to look good, not be physically accurate
