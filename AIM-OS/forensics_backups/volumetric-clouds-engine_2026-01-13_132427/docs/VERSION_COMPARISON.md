# Version Comparison Guide

**Purpose**: Compare different versions of the Volumetric Cloud Engine  
**Last Updated**: 2025-01-27

---

## Version Overview

| Version | Release Date | Key Features | Status |
|---------|--------------|--------------|--------|
| **v4.0** | Original | Mountains, City, Water, Gerstner Waves, Enhanced Clouds | Base version |
| **v4.1** | 2025-01-27 | Coherent shadows, performance optimizations, enhanced water | Documented |
| **v4.2** | 2025-01-27 | Enhanced atmospheric scattering, optimized god ray shadows | Documented |

---

## Feature Comparison

### Atmospheric Scattering

| Feature | v4.0 | v4.1 | v4.2 |
|---------|------|------|------|
| **Basic Scattering** | ✅ | ✅ | ✅ |
| **Horizon Glow** | ❌ | ❌ | ✅ NEW |
| **Atmospheric Haze** | ❌ | ❌ | ✅ NEW |
| **Enhanced Coefficients** | ❌ | ❌ | ✅ NEW |
| **Smooth Sun Color** | ❌ | ❌ | ✅ NEW |

### Shadow System

| Feature | v4.0 | v4.1 | v4.2 |
|---------|------|------|------|
| **Cloud Shadows** | ✅ | ✅ | ✅ |
| **Coherent Shadows** | ❌ | ✅ NEW | ✅ |
| **Fast Shadow (God Rays)** | ❌ | ❌ | ✅ NEW |
| **Dual Shadow System** | ❌ | ❌ | ✅ NEW |

### Performance Optimizations

| Feature | v4.0 | v4.1 | v4.2 |
|---------|------|------|------|
| **Uniform Caching** | ❌ | ✅ NEW | ✅ |
| **Blit Framebuffer** | ❌ | ✅ NEW | ✅ |
| **Fast Shadow for God Rays** | ❌ | ❌ | ✅ NEW |
| **Optimized God Rays** | ❌ | ❌ | ✅ NEW |

### Water Rendering

| Feature | v4.0 | v4.1 | v4.2 |
|---------|------|------|------|
| **Basic Water** | ✅ | ✅ | ✅ |
| **Terrain Reflections** | ❌ | ✅ NEW | ✅ |
| **Enhanced Depth** | ❌ | ✅ NEW | ✅ |

---

## Performance Comparison

### Relative Performance (v4.0 = 1.0x)

| Version | Overall | God Rays | Shadows | Atmospheric |
|---------|---------|----------|---------|-------------|
| **v4.0** | 1.0x | 1.0x | 1.0x | 1.0x |
| **v4.1** | 1.2-1.3x | 1.0x | 1.0x | 1.0x |
| **v4.2** | 1.2-1.3x | 1.3x | 1.0x | 1.0x |

### God Ray Performance

- **v4.0-v4.1**: Same performance (coherent shadows)
- **v4.2**: ~30% faster (fast shadow function)

---

## Visual Quality Comparison

### Sky Rendering

- **v4.0-v4.1**: Good quality
- **v4.2**: Excellent quality (horizon glow, haze, better transitions)

### God Rays

- **v4.0-v4.1**: High quality
- **v4.2**: High quality (maintained, with better performance)

### Shadows

- **v4.0**: Good quality
- **v4.1-v4.2**: Excellent quality (coherent shadows)

---

## Migration Path

### Recommended Upgrade Path

1. **v4.0 → v4.1**: Significant performance improvements, coherent shadows
2. **v4.1 → v4.2**: Enhanced atmospheric effects, optimized god rays

### Breaking Changes

- **None**: All versions are backward compatible
- **Visual**: Each version improves visual quality (no regressions)

---

## Documentation References

- **[Version 4.1 Changelog](VERSION_4.1_CHANGELOG.md)** - v4.1 details
- **[Version 4.1 Technical Notes](VERSION_4.1_TECHNICAL_NOTES.md)** - v4.1 technical details
- **[Version 4.2 Changelog](VERSION_4.2_CHANGELOG.md)** - v4.2 details
- **[Version 4.2 Technical Notes](VERSION_4.2_TECHNICAL_NOTES.md)** - v4.2 technical details

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Complete
