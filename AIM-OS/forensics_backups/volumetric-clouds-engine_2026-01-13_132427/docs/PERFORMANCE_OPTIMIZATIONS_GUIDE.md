# Performance Optimizations Implementation Guide

**Status**: Implementation Plan  
**Priority**: High - Critical Performance Improvements  
**Estimated Impact**: 2-4x performance improvement

---

## 📋 Table of Contents

1. [Problem Analysis](#problem-analysis)
2. [Optimization 1: Present/Blit Pass (Critical)](#optimization-1-presentblit-pass-critical)
3. [Optimization 2: Fast Path When TAA is Off](#optimization-2-fast-path-when-taa-is-off)
4. [Optimization 3: Render Scale Slider](#optimization-3-render-scale-slider)
5. [Optimization 4: Profiling Toggles](#optimization-4-profiling-toggles)
6. [Implementation Steps](#implementation-steps)
7. [Testing & Validation](#testing--validation)
8. [Expected Performance Gains](#expected-performance-gains)

---

## Problem Analysis

### Current Performance Issues

**Issue 1: Double Rendering (CRITICAL)**
- **Problem**: The render loop currently executes the expensive ray marching shader **twice per frame**
  1. Once to render to FBO (framebuffer object) for temporal accumulation
  2. Once again to render to screen
- **Impact**: This effectively doubles the rendering cost
- **Location**: `VolumetricEnginePage.tsx` lines ~1439-1442
- **Code**:
  ```typescript
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbRef.current.current);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);  // Expensive ray marching
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);  // Same expensive ray marching again!
  ```

**Issue 2: TAA Always Active**
- **Problem**: Even when TAA is disabled, the code still renders to FBO and performs ping-pong buffer swaps
- **Impact**: Unnecessary overhead when TAA is off
- **Solution**: Fast path that renders directly to screen when `enableTemporal === false`

**Issue 3: No Render Scale Control**
- **Problem**: Always renders at full resolution
- **Impact**: No way to trade quality for performance
- **Solution**: Render scale slider (0.5-1.0) to reduce pixel count

**Issue 4: No Profiling Tools**
- **Problem**: Difficult to identify performance hotspots
- **Impact**: Can't optimize specific features
- **Solution**: Toggles to disable expensive features for profiling

---

## Optimization 1: Present/Blit Pass (Critical)

### Overview

Replace the double render with a two-pass approach:
1. **Heavy Pass**: Render expensive ray marching shader **once** to FBO
2. **Present Pass**: Use a cheap texture blit shader to copy FBO to screen

### Expected Impact

- **Performance Gain**: ~2x faster (cuts expensive work in half)
- **Quality**: No change (same visual result)
- **Complexity**: Low-Medium

### Implementation Details

#### Step 1: Add Present Shader

**Location**: Near other shader sources (after `vertexShaderSource`, before `fragmentShaderSource`)

**Code**:
```typescript
const presentFragmentShaderSource = `#version 300 es
precision highp float;
in vec2 vUv;
out vec4 fragColor;
uniform sampler2D uTex;
void main() {
    fragColor = texture(uTex, vUv);
}
`;
```

**Purpose**: Simple texture sampler - just copies texture to screen (very cheap)

#### Step 2: Add Program Refs

**Location**: With other refs (around line 984-990)

**Code**:
```typescript
const presentProgramRef = useRef<WebGLProgram | null>(null);
const presentTexLocRef = useRef<WebGLUniformLocation | null>(null);
```

#### Step 3: Compile Present Program

**Location**: In the `useEffect` init block, after main program compilation (around line 1118)

**Code**:
```typescript
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
```

**Note**: Present program uses the same vertex shader as main program (reuse `vs`)

#### Step 4: Replace Double Render

**Location**: In render loop, replace lines ~1439-1442

**Current Code** (WRONG - renders twice):
```typescript
gl.bindFramebuffer(gl.FRAMEBUFFER, fbRef.current.current);
gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);  // Heavy render to FBO
gl.bindFramebuffer(gl.FRAMEBUFFER, null);
gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);  // Heavy render to screen (BAD!)
```

**New Code** (CORRECT - render once, blit once):
```typescript
// 1) Heavy render ONCE into current FBO
gl.bindFramebuffer(gl.FRAMEBUFFER, fbRef.current.current);
gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);  // Heavy render to FBO (ONCE)

// 2) Cheap present pass to screen
gl.bindFramebuffer(gl.FRAMEBUFFER, null);
gl.useProgram(presentProgramRef.current);

gl.activeTexture(gl.TEXTURE0);
gl.bindTexture(gl.TEXTURE_2D, fbRef.current.texCurrent);
if (presentTexLocRef.current) {
  gl.uniform1i(presentTexLocRef.current, 0);
}

gl.viewport(0, 0, dw, dh);  // Full screen viewport
gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);  // Cheap blit

// Restore main program for next frame uniforms
gl.useProgram(program);
```

**Important Notes**:
- Set viewport to screen size (`dw, dh`) for present pass
- Bind the current texture (`texCurrent`) before present pass
- Restore main program after present pass
- Present pass uses same vertex buffer (no additional setup needed)

---

## Optimization 2: Fast Path When TAA is Off

### Overview

When TAA is disabled, skip FBO rendering entirely and render directly to screen.

### Expected Impact

- **Performance Gain**: Eliminates FBO overhead when TAA is off
- **Quality**: No change (same visual result)
- **Complexity**: Low

### Implementation Details

#### Step 1: Add Fast Path Check

**Location**: At start of render function, before FBO setup

**Code**:
```typescript
const render = () => {
  if (!isPlaying) {
    animationRef.current = requestAnimationFrame(render);
    return;
  }

  const dw = canvas.clientWidth;
  const dh = canvas.clientHeight;
  
  const useTAA = !!params.enableTemporal;

  // Fast path: render directly to screen when TAA is off
  if (!useTAA) {
    gl.viewport(0, 0, dw, dh);
    gl.useProgram(program);
    
    const time = (Date.now() - startTimeRef.current) / 1000;
    
    // ... (setU function definition - same as TAA path)
    // ... (all setU calls - copy from TAA path)
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    frameRef.current++;
    animationRef.current = requestAnimationFrame(render);
    return;  // Exit early - skip FBO path
  }

  // TAA path: continue with FBO rendering...
  // ... (rest of existing code)
};
```

**Important**: Must copy ALL `setU` calls from TAA path to fast path (all parameter setup)

#### Step 2: Skip FBO Setup When TAA is Off

**Location**: In texture resizing code

**Code**:
```typescript
if (canvas.width !== dw || canvas.height !== dh) {
  canvas.width = dw;
  canvas.height = dh;
  const resizeTex = (tex: WebGLTexture | null, w: number, h: number) => {
    // ... resize logic
  };
  if (useTAA) {  // Only resize FBO textures if TAA is enabled
    resizeTex(fbRef.current.texCurrent, rw, rh);
    resizeTex(fbRef.current.texPrev, rw, rh);
  }
}
```

---

## Optimization 3: Render Scale Slider

### Overview

Add a render scale parameter (0.5-1.0) to render at lower resolution and upscale to screen.

### Expected Impact

- **Performance Gain**: 0.75 scale = 44% fewer pixels = significant speedup
- **Quality**: Slight quality reduction (trade-off)
- **Complexity**: Medium

### Implementation Details

#### Step 1: Add State Variable

**Location**: With other state variables (around line 1017)

**Code**:
```typescript
const [renderScale, setRenderScale] = useState(1.0);  // 0.5 to 1.0
```

#### Step 2: Calculate Render Dimensions

**Location**: In render function, after getting canvas dimensions

**Code**:
```typescript
const dw = canvas.clientWidth;
const dh = canvas.clientHeight;

const useTAA = !!params.enableTemporal;

// Calculate render dimensions with render scale
const rw = Math.max(1, Math.floor(dw * renderScale));
const rh = Math.max(1, Math.floor(dh * renderScale));
```

#### Step 3: Use Render Dimensions for FBO

**Location**: When creating/resizing FBO textures

**Code**:
```typescript
if (useTAA) {
  resizeTex(fbRef.current.texCurrent, rw, rh);  // Use rw, rh instead of dw, dh
  resizeTex(fbRef.current.texPrev, rw, rh);
}
```

#### Step 4: Set Viewport and Resolution for FBO Render

**Location**: Before FBO render

**Code**:
```typescript
// TAA path
gl.viewport(0, 0, rw, rh);  // Render at scaled resolution
gl.useProgram(program);

// ... setU calls ...

setU('iResolution', rw, rh);  // Shader resolution matches render buffer
```

#### Step 5: Set Viewport for Present Pass

**Location**: In present pass

**Code**:
```typescript
// Present pass
gl.bindFramebuffer(gl.FRAMEBUFFER, null);
gl.viewport(0, 0, dw, dh);  // Full screen viewport for upscale
gl.useProgram(presentProgramRef.current);
// ... present pass code ...
```

#### Step 6: Add UI Slider

**Location**: In Quality panel (around line 1595)

**Code**:
```typescript
case 'quality':
  return (
    <div className="space-y-3">
      <SliderControl 
        label="Render Scale" 
        value={renderScale} 
        min={0.5} 
        max={1.0} 
        step={0.05} 
        onChange={(v: number) => setRenderScale(v)} 
        format={(v: number) => `${(v*100).toFixed(0)}%`} 
      />
      <SliderControl label="Ray Steps" value={params.primarySteps} min={24} max={96} step={8} onChange={(v: number) => updateParam('primarySteps', v)} format={(v: number) => v.toFixed(0)} />
      // ... rest of quality controls
    </div>
  );
```

---

## Optimization 4: Profiling Toggles

### Overview

Add toggles to disable expensive features for performance profiling.

### Expected Impact

- **Performance Gain**: Varies by feature (can identify bottlenecks)
- **Quality**: Features disabled (for profiling only)
- **Complexity**: Low-Medium

### Features to Toggle

1. **Cloud Shadows**: Early return in `getCloudShadow()`
2. **Water Cloud Reflection**: Skip `rayMarchClouds()` in `renderWater()`
3. **Clouds On/Off**: Skip `rayMarchClouds()` entirely

### Implementation Details

#### Step 1: Add Uniforms to Shader

**Location**: In shader uniform declarations (around line 140)

**Code**:
```glsl
// Profiling toggles
uniform bool uDisableCloudShadows;
uniform bool uDisableWaterCloudReflection;
uniform bool uDisableClouds;
```

#### Step 2: Add State Variables

**Location**: With other state (around line 1017)

**Code**:
```typescript
const [disableCloudShadows, setDisableCloudShadows] = useState(false);
const [disableWaterCloudReflection, setDisableWaterCloudReflection] = useState(false);
const [disableClouds, setDisableClouds] = useState(false);
```

#### Step 3: Pass Uniforms to Shader

**Location**: In render function, with other setU calls

**Code**:
```typescript
setU('uDisableCloudShadows', disableCloudShadows);
setU('uDisableWaterCloudReflection', disableWaterCloudReflection);
setU('uDisableClouds', disableClouds);
```

#### Step 4: Implement Early Returns in Shader

**Location A**: In `getCloudShadow()` function (around line 494)

**Code**:
```glsl
float getCloudShadow(vec3 pos, vec3 lightDir) {
    if(uDisableCloudShadows) return 1.0;  // Early return - no shadows
    
    // ... existing shadow code ...
}
```

**Location B**: In `renderWater()` function (around line 625)

**Code**:
```glsl
vec3 renderWater(vec3 ro, vec3 rd, vec3 lightDir, vec3 hitPos, vec3 skyColor) {
    // ... existing code ...
    
    // Cloud reflection
    if(!uDisableWaterCloudReflection) {
        vec4 cloudRefl = rayMarchClouds(hitPos + vec3(0.0, 1.0, 0.0), reflectDir, lightDir, 80000.0, 0.5);
        reflectColor = mix(reflectColor, cloudRefl.rgb, cloudRefl.a * 0.7);
    }
    
    // ... rest of function ...
}
```

**Location C**: In `main()` function (around line 820)

**Code**:
```glsl
void main() {
    // ... existing code ...
    
    // Clouds
    if(!uDisableClouds) {
        float cloudMaxDist = terrain.a > 0.0 ? terrainDist : 150000.0;
        vec4 clouds = rayMarchClouds(ro, rd, lightDir, cloudMaxDist, jitter);
        color = mix(color, clouds.rgb, clouds.a);
    }
    
    // ... rest of main function ...
}
```

#### Step 5: Add UI Toggles

**Location**: In Quality panel (around line 1595)

**Code**:
```typescript
case 'quality':
  return (
    <div className="space-y-3">
      <SectionHeader>Profiling (Debug)</SectionHeader>
      <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
        <span className="text-xs text-gray-400">Disable Cloud Shadows</span>
        <Switch checked={disableCloudShadows} onCheckedChange={setDisableCloudShadows} />
      </div>
      <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
        <span className="text-xs text-gray-400">Disable Water Cloud Reflection</span>
        <Switch checked={disableWaterCloudReflection} onCheckedChange={setDisableWaterCloudReflection} />
      </div>
      <div className="flex items-center justify-between" onClick={(e) => e.stopPropagation()}>
        <span className="text-xs text-gray-400">Disable Clouds</span>
        <Switch checked={disableClouds} onCheckedChange={setDisableClouds} />
      </div>
      
      <SectionHeader>Performance</SectionHeader>
      <SliderControl label="Render Scale" value={renderScale} min={0.5} max={1.0} step={0.05} onChange={(v: number) => setRenderScale(v)} format={(v: number) => `${(v*100).toFixed(0)}%`} />
      // ... rest of quality controls
    </div>
  );
```

---

## Implementation Steps

### Recommended Order

1. **Optimization 1 (Present Pass)** - Highest impact, fixes critical double-render issue
2. **Optimization 2 (Fast Path)** - Quick win, low complexity
3. **Optimization 3 (Render Scale)** - Good performance control
4. **Optimization 4 (Profiling Toggles)** - Useful for debugging

### Step-by-Step Process

#### Phase 1: Present Pass (Critical Fix)

1. Add present shader source
2. Add present program refs
3. Compile present program in init
4. Replace double render with FBO + present
5. Test: Verify no visual changes, check performance improvement

#### Phase 2: Fast Path

1. Add `useTAA` check at start of render
2. Copy all parameter setup to fast path
3. Add early return when TAA is off
4. Skip FBO setup when TAA is off
5. Test: Toggle TAA off, verify direct render works

#### Phase 3: Render Scale

1. Add render scale state
2. Calculate render dimensions
3. Update FBO texture sizing
4. Update viewport and resolution uniforms
5. Add UI slider
6. Test: Adjust scale, verify performance/quality trade-off

#### Phase 4: Profiling Toggles

1. Add shader uniforms
2. Add state variables
3. Pass uniforms to shader
4. Implement early returns in shader
5. Add UI toggles
6. Test: Toggle features, verify performance impact

---

## Testing & Validation

### Performance Testing

1. **Before Optimization**: Measure FPS with current code
2. **After Each Optimization**: Measure FPS again
3. **Compare**: Calculate performance improvement

### Visual Testing

1. **Present Pass**: Verify no visual changes (should be identical)
2. **Fast Path**: Toggle TAA off/on, verify identical rendering
3. **Render Scale**: Adjust scale, verify quality trade-off is acceptable
4. **Profiling Toggles**: Toggle features, verify they disable correctly

### Validation Checklist

- [ ] Present pass: No visual artifacts
- [ ] Present pass: Performance improved (~2x)
- [ ] Fast path: TAA off works correctly
- [ ] Fast path: No FBO overhead when TAA off
- [ ] Render scale: UI slider works
- [ ] Render scale: Lower scale = better performance
- [ ] Render scale: Quality degrades gracefully
- [ ] Profiling toggles: All toggles work
- [ ] Profiling toggles: Performance impact measurable
- [ ] No console errors
- [ ] No visual glitches

---

## Expected Performance Gains

### Combined Impact

| Optimization | Performance Gain | Cumulative |
|-------------|------------------|------------|
| **Base (Current)** | 1.0x | 1.0x |
| **Present Pass** | 2.0x | 2.0x |
| **Fast Path (TAA off)** | +10-20% | 2.2-2.4x |
| **Render Scale 0.75** | +1.8x | 4.0-4.3x |
| **Render Scale 0.5** | +4.0x | 8.8-9.6x |

### Individual Impact

- **Present Pass**: ~2x (critical fix)
- **Fast Path**: Eliminates FBO overhead when TAA off
- **Render Scale 0.75**: ~1.8x (44% fewer pixels)
- **Render Scale 0.5**: ~4x (75% fewer pixels)
- **Profiling Toggles**: Varies by feature (identifies bottlenecks)

### Real-World Expectations

- **Low-end GPU**: 2-4x improvement with all optimizations
- **Mid-range GPU**: 1.5-3x improvement
- **High-end GPU**: 1.2-2x improvement (less impact, already fast)

---

## Code Locations Reference

### Key Files

- **Main Component**: `src/VolumetricEnginePage.tsx`
- **Shader Source**: Embedded in component (lines ~19-854)

### Key Line Numbers (Approximate)

- Shader uniforms: ~33-141
- `getCloudShadow()`: ~494
- `renderWater()`: ~625
- `main()` cloud rendering: ~820
- State variables: ~1017
- Init useEffect: ~1060
- Render useEffect: ~1208
- Double render (to fix): ~1439-1442
- Quality panel UI: ~1595

**Note**: Line numbers may vary after edits. Use grep/search to find exact locations.

---

## Troubleshooting

### Present Pass Issues

**Problem**: Black screen or no output
- **Check**: Present program compiled successfully
- **Check**: Texture bound correctly (`texCurrent`)
- **Check**: Viewport set correctly (`dw, dh`)

**Problem**: Visual artifacts
- **Check**: Viewport matches screen size
- **Check**: Texture filtering (should be LINEAR)

### Fast Path Issues

**Problem**: TAA off doesn't work
- **Check**: All `setU` calls copied to fast path
- **Check**: Early return executes correctly
- **Check**: No FBO operations when TAA off

### Render Scale Issues

**Problem**: Quality too low
- **Solution**: Increase render scale (0.75-0.9 recommended)
- **Check**: Viewport set correctly for present pass

**Problem**: Performance not improving
- **Check**: Render dimensions calculated correctly
- **Check**: FBO textures resized correctly
- **Check**: Resolution uniform matches render size

### Profiling Toggle Issues

**Problem**: Toggles don't work
- **Check**: Uniforms passed to shader
- **Check**: Early returns in correct locations
- **Check**: Boolean uniforms set correctly

---

## Summary

These optimizations provide significant performance improvements with minimal complexity:

1. **Present Pass** (Critical): 2x performance - fixes double-render bug
2. **Fast Path**: Eliminates overhead when TAA disabled
3. **Render Scale**: Flexible quality/performance trade-off
4. **Profiling Toggles**: Tools for performance analysis

**Recommended Priority**: Implement in order (1 → 2 → 3 → 4) for maximum impact with minimal risk.

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation
