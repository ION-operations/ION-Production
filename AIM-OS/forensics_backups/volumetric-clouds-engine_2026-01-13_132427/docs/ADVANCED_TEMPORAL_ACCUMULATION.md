# Advanced Temporal Accumulation for Volumetric Clouds
## The 4-Frame Loop with Structured Dithering (Bayer Matrix)

**Status:** Research & Documentation  
**Target Engines:** Horizon: Zero Dawn, Microsoft Flight Simulator  
**Current Implementation:** Simple temporal blend (needs enhancement)

---

## 📋 Table of Contents

1. [Problem Statement](#problem-statement)
2. [Current Implementation Analysis](#current-implementation-analysis)
3. [The 4-Frame Loop Strategy](#the-4-frame-loop-strategy)
4. [Structured Dithering with Bayer Matrix](#structured-dithering-with-bayer-matrix)
5. [Implementation Guide](#implementation-guide)
6. [Moving Clouds & Velocity Correction](#moving-clouds--velocity-correction)
7. [Comparison: Current vs. Advanced](#comparison-current-vs-advanced)
8. [Integration Considerations](#integration-considerations)
9. [Performance Analysis](#performance-analysis)
10. [References & Further Reading](#references--further-reading)

---

## Problem Statement

### Current Issues

1. **Dithering Bands**: Random noise/jitter creates visible banding artifacts
2. **Insufficient Samples**: Can't afford 100+ samples per pixel per frame
3. **Moving Clouds Artifacts**: Temporal accumulation fails during camera/cloud movement
4. **Ghosting & Trails**: Clouds leave trails when moving behind mountains
5. **Dependency on Main Scene TAA**: Relies on external temporal anti-aliasing

### The Core Challenge

> "You can't afford 100 samples per pixel. But you can afford 25 samples per pixel. So, you split the work."

**Solution**: Distribute sampling across 4 frames using structured dithering, then accumulate internally before the clouds touch the main scene.

---

## Current Implementation Analysis

### Current Temporal System

**Location**: `VolumetricEnginePage.tsx` - Fragment Shader (lines ~845-849)

```glsl
// Temporal blend
if(uEnableTemporal && iFrame > 0) {
    vec3 prevColor = texture(uPrevFrame, vUv).rgb;
    color = mix(color, prevColor, uTemporalBlend);
}
```

**Characteristics**:
- ✅ Simple pixel-space temporal blend
- ❌ Uses random blue noise jitter (`blueNoise(gl_FragCoord.xy, iFrame)`)
- ❌ No velocity correction for moving clouds
- ❌ No structured sampling pattern
- ❌ Dependent on main scene's TAA
- ❌ Blend factor is constant (typically 0.85 = 85% old, 15% new)

**Current Jitter** (line ~218):
```glsl
float jitter = blueNoise(gl_FragCoord.xy, iFrame);
```

**Problems**:
1. Random jitter creates uneven sampling distribution
2. No guarantee of complete coverage after N frames
3. Moving clouds break temporal coherence
4. Artifacts visible during camera movement

---

## The 4-Frame Loop Strategy

### Concept

Instead of randomly distributing samples, use a **structured 2x2 Bayer matrix** that guarantees perfect coverage over exactly 4 frames.

### The Strategy

```
Frame 1: Calculate top-left corner of every pixel block
Frame 2: Calculate top-right corner
Frame 3: Calculate bottom-left corner
Frame 4: Calculate bottom-right corner

By Frame 4: Perfect image stored in internal history buffer
Time Cost: 60ms at 60fps (4 frames)
Quality: Equivalent to 4x the samples per pixel
```

### Mathematical Guarantee

- **2x2 Bayer Matrix**: 4 unique positions (0, 1, 2, 3)
- **4-Frame Cycle**: Ensures every pixel samples all 4 positions
- **Perfect Coverage**: No gaps, no overlaps, no randomness
- **Deterministic**: Same pattern every time, predictable and smooth

### Visual Representation

```
Bayer Matrix Pattern (2x2):
┌─────┬─────┐
│  0  │  1  │  ← Frame 1: Sample position 0
├─────┼─────┤  ← Frame 2: Sample position 1
│  2  │  3  │  ← Frame 3: Sample position 2
└─────┴─────┘  ← Frame 4: Sample position 3
```

**After 4 frames**, every pixel has sampled all 4 positions = complete coverage.

---

## Structured Dithering with Bayer Matrix

### Step A: Calculate Bayer Offset

```glsl
// Inside Cloud Shader (Ray Marching Section)

// 1. Calculate pixel position in 2x2 grid
int x = int(gl_FragCoord.x) % 2;
int y = int(gl_FragCoord.y) % 2;
int index = x + y * 2;  // Returns 0, 1, 2, or 3 based on pixel position

// 2. Shift pattern based on frame counter (4-frame loop)
int loopPhase = (iFrame % 4);
int bayerIndex = (index + loopPhase) % 4;

// 3. Convert to offset value (0.0, 0.25, 0.50, 0.75)
float rayOffset = float(bayerIndex) / 4.0;

// 4. Apply to ray marching
float t = tStart + rayOffset * stepSize;
```

### Why This Works

1. **Structured Pattern**: Bayer matrix ensures even distribution
2. **Deterministic**: Same pattern repeats every 4 frames
3. **Complete Coverage**: After 4 frames, all positions sampled
4. **No Randomness**: Predictable, smooth accumulation
5. **Checkerboard Pattern**: Easier for accumulator to smooth than random noise

### Comparison: Random vs. Structured

| Aspect | Random Jitter (Current) | Bayer Matrix (Advanced) |
|--------|------------------------|------------------------|
| Distribution | Uneven, clustered | Perfectly even |
| Coverage | Probabilistic | Guaranteed after 4 frames |
| Visual Artifact | Noise/static | Clean checkerboard |
| Predictability | Random | Deterministic |
| Smoothness | Varies | Consistent |

---

## Implementation Guide

### Phase 1: Replace Jitter in Ray Marching

**Current Code** (line ~218):
```glsl
float jitter = blueNoise(gl_FragCoord.xy, iFrame);
```

**New Code**:
```glsl
// Structured dithering with 2x2 Bayer matrix
int x = int(gl_FragCoord.x) % 2;
int y = int(gl_FragCoord.y) % 2;
int bayerIndex = (x + y * 2 + (iFrame % 4)) % 4;
float rayOffset = float(bayerIndex) * 0.25;  // 0.0, 0.25, 0.50, 0.75
```

**In ray marching** (where `jitter` was used):
```glsl
float stepSize = (t.y - t.x) / float(uPrimarySteps);
float dist = t.x + stepSize * rayOffset;  // Instead of: t.x + stepSize * jitter
```

### Phase 2: Internal Accumulation Shader

**Current**: Temporal blend happens in main shader (pixel-space)

**Advanced**: Separate accumulation pass with velocity correction

```glsl
// Accumulation Shader (Separate Pass)
// Runs AFTER cloud rendering, BEFORE compositing to main scene

uniform sampler2D currentFrame;      // Raw dithered output (checkerboard pattern)
uniform sampler2D historyFrame;      // Accumulated result from previous frame
uniform vec2 cloudVelocity;          // Wind + camera motion (in UV space)
uniform vec2 resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    
    // 1. Rewind time: Find where cloud particle was LAST frame
    vec2 previousUV = uv - cloudVelocity;
    
    // 2. Clamp to valid range (prevent sampling outside texture)
    previousUV = clamp(previousUV, vec2(0.0), vec2(1.0));
    
    // 3. Fetch history and current
    vec4 oldCloud = texture(historyFrame, previousUV);
    vec4 newCloud = texture(currentFrame, uv);
    
    // 4. Neighborhood clamping (anti-ghosting)
    // If new pixel differs drastically from neighbors, trust it more
    vec4 neighborMin = texture(currentFrame, uv + vec2(-1.0, -1.0) / resolution);
    vec4 neighborMax = texture(currentFrame, uv + vec2(1.0, 1.0) / resolution);
    vec4 clampedOld = clamp(oldCloud, neighborMin, neighborMax);
    
    // 5. Blend with velocity-aware history
    float blendFactor = 0.15;  // 15% new, 85% old (for 4-frame pattern)
    vec4 blended = mix(clampedOld, newCloud, blendFactor);
    
    fragColor = blended;
}
```

### Phase 3: Velocity Calculation

**Cloud Velocity = Wind Velocity + Camera Motion**

```glsl
// In main cloud shader or separate calculation
vec2 cloudVelocity = vec2(
    uShapeSpeed * 0.005,  // Wind X component
    uShapeSpeed * 0.003   // Wind Z component (or use camera motion)
);

// If camera moves, add camera velocity:
// cloudVelocity += cameraMotionUV;
```

**Camera Motion** (if needed):
```glsl
// Calculate camera motion in UV space
vec2 cameraMotion = (currentCameraPos.xz - previousCameraPos.xz) / cloudDistance;
```

### Phase 4: Off-Screen Rendering Pipeline

**Current Pipeline**:
```
Cloud Shader → Temporal Blend → Main Scene
```

**Advanced Pipeline**:
```
Cloud Shader (Dithered) → Off-Screen Buffer → 
Accumulation Shader (Velocity-Corrected) → 
Accumulated Buffer → Main Scene
```

**Benefits**:
1. Checkerboard pattern never shown to user
2. Internal accumulation isolated from main scene
3. Independent of main scene TAA
4. Can use different blend factors for clouds vs. scene

---

## Moving Clouds & Velocity Correction

### The Problem

When clouds move (wind) or camera moves, temporal accumulation fails because:
- **History lookup** uses same UV coordinate
- **Cloud has moved** to different position
- **Averaging pixel with sky** instead of cloud with cloud
- **Result**: Ghosting, trails, smearing

### The Solution: Velocity Correction

**Key Insight**: "You must offset the history lookup by the wind."

```glsl
// Instead of:
vec4 oldCloud = texture(historyFrame, uv);  // ❌ Wrong: cloud moved!

// Use:
vec2 previousUV = uv - cloudVelocity;        // ✅ Correct: rewind time
vec4 oldCloud = texture(historyFrame, previousUV);
```

### Why This Works

1. **Rewinds Time**: Subtracts velocity to find previous position
2. **Tracks Clouds**: History follows the cloud, not the pixel
3. **Correct Averaging**: Cloud averaged with itself, not with sky
4. **Eliminates Ghosting**: No trails, no smearing

### Implementation Details

**Velocity Components**:
- **Wind Speed**: Cloud movement due to wind (`uShapeSpeed`)
- **Camera Motion**: Camera movement in world space
- **Combined**: Total velocity in UV space

**Clamping**:
```glsl
previousUV = clamp(previousUV, vec2(0.0), vec2(1.0));
```
Prevents sampling outside texture bounds.

**Neighborhood Clamping** (Advanced Anti-Ghosting):
```glsl
// If new pixel is drastically different from neighbors, trust it more
// This fixes "trails" when clouds move behind mountains
vec4 clampedOld = clamp(oldCloud, neighborMin, neighborMax);
```

---

## Comparison: Current vs. Advanced

### Current Implementation

| Aspect | Implementation |
|--------|---------------|
| **Jitter** | Random blue noise |
| **Coverage** | Probabilistic, uneven |
| **Temporal Blend** | Simple pixel-space mix |
| **Velocity** | Not accounted for |
| **Ghosting** | Present during movement |
| **Dependency** | Relies on main scene TAA |
| **Quality** | Good for static scenes |

### Advanced Implementation

| Aspect | Implementation |
|--------|---------------|
| **Jitter** | Structured Bayer matrix |
| **Coverage** | Guaranteed after 4 frames |
| **Temporal Blend** | Velocity-corrected accumulation |
| **Velocity** | Wind + camera motion corrected |
| **Ghosting** | Eliminated via velocity correction |
| **Dependency** | Independent, internal accumulation |
| **Quality** | Professional (Horizon, Flight Sim) |

### Quality Comparison

| Scenario | Current | Advanced |
|----------|---------|----------|
| **Static Clouds** | ✅ Good | ✅ Excellent |
| **Moving Clouds** | ❌ Ghosting | ✅ Smooth |
| **Camera Movement** | ❌ Artifacts | ✅ Clean |
| **Fast Movement** | ❌ Trails | ✅ Correct |
| **Banding** | ⚠️ Visible | ✅ Eliminated |

---

## Integration Considerations

### Current Architecture

**Files to Modify**:
1. `VolumetricEnginePage.tsx` - Fragment shader (main rendering)
2. `VolumetricEnginePage.tsx` - JavaScript (framebuffer management)

**Current Framebuffer Setup**:
- `fbRef.current.current` - Current frame
- `fbRef.current.prev` - Previous frame (for temporal)
- Simple ping-pong between two buffers

### Required Changes

1. **Additional Framebuffer**:
   - Add `accumulated` buffer for internal accumulation
   - Or reuse existing buffers with different pass

2. **Two-Pass Rendering**:
   - **Pass 1**: Cloud shader with Bayer jitter → `currentFrame` buffer
   - **Pass 2**: Accumulation shader → `accumulated` buffer
   - **Pass 3**: Composite `accumulated` to main scene

3. **New Uniforms**:
   ```glsl
   uniform vec2 uCloudVelocity;      // Wind + camera motion
   uniform sampler2D uCurrentFrame;  // Raw dithered output
   uniform sampler2D uHistoryFrame;  // Previous accumulation
   ```

4. **JavaScript Changes**:
   - Calculate cloud velocity (wind + camera motion)
   - Manage additional framebuffer/texture
   - Run accumulation pass after cloud pass

### Performance Impact

**Current**:
- 1 pass: Cloud rendering with temporal blend
- ~64 ray steps per pixel per frame
- Temporal blend: Simple texture lookup + mix

**Advanced**:
- 2 passes: Cloud rendering + accumulation
- ~16 ray steps per pixel per frame (4x reduction per frame)
- Over 4 frames: Same total samples (16 × 4 = 64)
- Accumulation: Texture lookup + velocity calculation + blend

**Net Result**:
- ✅ **Lower per-frame cost** (fewer samples per frame)
- ✅ **Better quality** (structured sampling)
- ⚠️ **Slightly higher complexity** (two passes)
- ✅ **Better for moving scenes** (velocity correction)

### Migration Path

**Phase 1: Add Bayer Jitter** (Low Risk)
- Replace `blueNoise` with Bayer matrix calculation
- Keep current temporal blend
- Test for quality improvement

**Phase 2: Add Velocity Calculation** (Medium Risk)
- Calculate cloud velocity in JavaScript
- Pass to shader as uniform
- Update temporal blend to use velocity

**Phase 3: Separate Accumulation Pass** (Higher Risk)
- Add accumulation shader
- Add additional framebuffer
- Implement two-pass pipeline

**Recommended**: Start with Phase 1, validate, then proceed.

---

## Performance Analysis

### Sampling Cost

**Current System** (per frame):
```
64 ray steps × 1 frame = 64 samples per pixel
Cost: 64 operations per pixel per frame
```

**4-Frame Loop** (per frame):
```
16 ray steps × 1 frame = 16 samples per pixel
Cost: 16 operations per pixel per frame
Over 4 frames: 16 × 4 = 64 samples (same total)
```

**Performance Gain**: 4x fewer samples per frame = 4x faster cloud rendering per frame

### Memory Cost

**Current**:
- 2 framebuffers (ping-pong)
- 2 textures (current, previous)

**Advanced**:
- 3 framebuffers (current, history, accumulated)
- 3 textures (or reuse with proper management)

**Additional Cost**: 1 additional framebuffer/texture (minimal)

### CPU Cost

**Additional Calculations**:
- Cloud velocity calculation (wind + camera)
- Framebuffer management (one extra buffer)

**Cost**: Negligible (simple vector math)

### Overall Performance

| Metric | Current | Advanced | Change |
|--------|---------|----------|--------|
| **Samples/Frame** | 64 | 16 | ✅ 4x reduction |
| **Samples/4 Frames** | 256 | 64 | ✅ 4x reduction |
| **Framebuffers** | 2 | 3 | ⚠️ +1 buffer |
| **Shader Passes** | 1 | 2 | ⚠️ +1 pass |
| **Quality** | Good | Excellent | ✅ Better |
| **Moving Scenes** | Poor | Excellent | ✅ Much better |

**Conclusion**: Per-frame performance significantly improved, with better quality and fewer artifacts.

---

## References & Further Reading

### Professional Implementations

1. **Horizon: Zero Dawn** (Guerrilla Games)
   - Internal temporal accumulation for clouds
   - Structured sampling patterns
   - Velocity-corrected accumulation

2. **Microsoft Flight Simulator** (Asobo Studio)
   - Advanced cloud rendering system
   - Temporal accumulation independent of main scene
   - High-quality results at 60fps

### Technical Papers

1. **"Real-Time Volumetric Cloudscapes"** (Guerrilla Games, SIGGRAPH 2015)
   - Original technique for volumetric clouds
   - Temporal accumulation strategies

2. **"Temporal Reprojection Anti-Aliasing"** (Various)
   - General temporal anti-aliasing techniques
   - Velocity correction methods

### WebGL/GLSL Resources

1. **Bayer Matrix Dithering**
   - Structured dithering patterns
   - 2x2, 4x4, 8x8 matrices

2. **Temporal Accumulation**
   - History buffer management
   - Velocity correction techniques

### Implementation Notes

- **Bayer Matrix**: Standard 2x2 pattern: `[0, 1; 2, 3]`
- **Frame Counter**: Must cycle 0→1→2→3→0 (modulo 4)
- **Velocity Units**: Must be in UV space (0.0 to 1.0)
- **Blend Factor**: 0.15 (15% new) works well for 4-frame pattern

---

## Summary

The **4-Frame Loop with Structured Dithering** represents a significant upgrade over simple temporal blending:

1. ✅ **Structured Sampling**: Bayer matrix ensures perfect coverage
2. ✅ **Performance**: 4x fewer samples per frame
3. ✅ **Quality**: Better than random jitter
4. ✅ **Moving Scenes**: Velocity correction eliminates ghosting
5. ✅ **Independence**: Works without main scene TAA
6. ✅ **Professional Quality**: Used in Horizon, Flight Simulator

**Recommended Next Steps**:
1. Implement Phase 1 (Bayer jitter) for immediate quality improvement
2. Test and validate results
3. Proceed to Phase 2 (velocity correction) if needed
4. Consider Phase 3 (separate accumulation) for maximum quality

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Research Complete, Ready for Implementation
