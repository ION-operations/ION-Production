# Performance Optimizations Implementation Plan

## Issues Identified

1. **Double Rendering**: Currently rendering heavy ray marching shader twice per frame (once to FBO, once to screen)
2. **TAA Always Active**: Rendering to FBO even when TAA is disabled
3. **No Render Scale**: Can't reduce resolution for performance
4. **Missing Profiling Tools**: No way to isolate performance hotspots

## Solutions

### 1. Add Present/Blit Pass (Critical Performance Fix)
- Add cheap present shader (simple texture sampler)
- Replace double render with: FBO render → present pass
- **Expected improvement**: ~2x faster (cuts expensive work in half)

### 2. Fast Path When TAA is Off
- When `enableTemporal === false`: render directly to screen, skip FBO
- **Expected improvement**: Eliminates unnecessary FBO overhead when TAA disabled

### 3. Render Scale Slider
- Add render scale parameter (0.5-1.0)
- Render at lower resolution, upscale to screen
- **Expected improvement**: 0.75 scale = 44% fewer pixels = significant speedup

### 4. Profiling Toggles
- Cloud Shadows: Early return in `getCloudShadow()`
- Water Cloud Reflection: Skip `rayMarchClouds()` in `renderWater()`
- Clouds On/Off: Skip `rayMarchClouds()` entirely
- **Expected improvement**: Isolate performance hotspots quickly

## Implementation Status

- [x] Present shader added
- [x] Present program refs added
- [ ] Present program compilation (in init)
- [ ] Replace double render with present pass
- [ ] Fast path when TAA off
- [ ] Render scale implementation
- [ ] Render scale slider in UI
- [ ] Profiling toggles in shader
- [ ] Profiling toggles in UI
