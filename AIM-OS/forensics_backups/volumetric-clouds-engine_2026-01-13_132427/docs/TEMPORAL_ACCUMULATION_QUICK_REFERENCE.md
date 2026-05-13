# Temporal Accumulation Quick Reference

**See**: `ADVANCED_TEMPORAL_ACCUMULATION.md` for full documentation

## Key Concepts

### The 4-Frame Loop Strategy

**Problem**: Can't afford 100 samples/pixel, but can afford 25 samples/pixel.

**Solution**: Split work across 4 frames using structured dithering (Bayer matrix).

```
Frame 1: Sample top-left  (25 samples)
Frame 2: Sample top-right (25 samples)
Frame 3: Sample bottom-left (25 samples)
Frame 4: Sample bottom-right (25 samples)
Result: 100 samples over 4 frames = 60ms at 60fps
```

### Bayer Matrix Implementation

**Replace random jitter with structured pattern:**

```glsl
// Replace: float jitter = blueNoise(gl_FragCoord.xy, iFrame);

// With:
int x = int(gl_FragCoord.x) % 2;
int y = int(gl_FragCoord.y) % 2;
int bayerIndex = (x + y * 2 + (iFrame % 4)) % 4;
float rayOffset = float(bayerIndex) * 0.25;  // 0.0, 0.25, 0.50, 0.75
```

### Velocity Correction

**Problem**: Moving clouds cause ghosting because history lookup uses same UV.

**Solution**: Rewind time by subtracting velocity:

```glsl
vec2 previousUV = uv - cloudVelocity;  // Rewind time
vec4 oldCloud = texture(historyFrame, previousUV);
```

## Current vs. Advanced

| Aspect | Current | Advanced |
|--------|---------|----------|
| **Jitter** | Random blue noise | Bayer matrix (structured) |
| **Samples/Frame** | 64 | 16 (4x reduction) |
| **Velocity** | Not corrected | Wind + camera corrected |
| **Ghosting** | Present | Eliminated |
| **Quality** | Good (static) | Excellent (moving) |

## Implementation Phases

1. **Phase 1**: Replace `blueNoise` with Bayer matrix (low risk, immediate improvement)
2. **Phase 2**: Add velocity correction to temporal blend (medium risk)
3. **Phase 3**: Separate accumulation pass (higher risk, maximum quality)

**Recommended**: Start with Phase 1.
