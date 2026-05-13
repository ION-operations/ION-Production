# Volumetric Clouds Engine

A real-time volumetric cloud rendering engine with terrain, water, and atmospheric effects.

**Current Version**: 4.1 - Performance optimized with coherent shadows/god rays

## Features

- Real-time volumetric cloud rendering
- Procedural terrain with mountains
- Gerstner wave water simulation
- City skyline rendering
- Atmospheric scattering
- God rays
- Star field
- Temporal anti-aliasing

## Documentation

### Advanced Rendering Techniques

- **[Advanced Temporal Accumulation](docs/ADVANCED_TEMPORAL_ACCUMULATION.md)** - Deep dive into 4-frame loop with structured dithering (Bayer matrix), velocity correction, and professional-grade temporal accumulation techniques used in Horizon: Zero Dawn and Microsoft Flight Simulator.
- **[Quick Reference](docs/TEMPORAL_ACCUMULATION_QUICK_REFERENCE.md)** - Quick reference guide for temporal accumulation techniques.

### Performance Optimization

- **[Performance Optimizations Guide](docs/PERFORMANCE_OPTIMIZATIONS_GUIDE.md)** - Comprehensive guide to performance optimizations including present pass, fast path, render scale, and profiling toggles. Expected 2-4x performance improvement.

### Version History

- **[Version 4.1 Changelog](docs/VERSION_4.1_CHANGELOG.md)** - Complete changelog for v4.1 including coherent shadows, performance optimizations, and enhanced water rendering
- **[Version 4.1 Technical Notes](docs/VERSION_4.1_TECHNICAL_NOTES.md)** - Technical details and implementation notes for v4.1

## Getting Started

### Installation

\`\`\`bash
npm install
\`\`\`

### Development

\`\`\`bash
npm run dev
\`\`\`

### Build

\`\`\`bash
npm run build
\`\`\`

## Controls

- **Drag**: Rotate camera
- **Shift + Drag**: Pan camera
- **Scroll**: Zoom
- **Presets**: Select from dropdown menu
- **Settings**: Adjust parameters in the side panel
