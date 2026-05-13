const canvas = document.getElementById("canvas");
const tabBarEl = document.getElementById("tabBar");
const tabPanelsEl = document.getElementById("tabPanels");
const collapseBtn = document.getElementById("collapseBtn");
const overlayBodyEl = document.getElementById("overlayBody");
let settingsEl = null;
let errorEl = null;
let statusPanelBody = null;

const urlParams = new URLSearchParams(window.location.search);

// ============================================================================
// WEBGL INITIALIZATION (RECONSTRUCTED)
// ============================================================================

let gl = null;
let vao = null;
let rtWidth = 0;
let rtHeight = 0;

let passA = null;
let passB = null;
let passImage = null;
let passImageFast = null;
let passAccum = null;
let passBlit = null;
let passGodrays = null;

let bufferA = { readFbo: null, writeFbo: null, readTex: null, writeTex: null };
let bufferB = { readFbo: null, writeFbo: null, readTex: null, writeTex: null };
let history = { readFbo: null, writeFbo: null, readTex: null, writeTex: null };
let currentColorTex = null;
let currentColorFbo = null;

let blueNoise = null;
let needsHistoryReset = false;
let needsBufferBRebuild = true;

function createTab(id, label, shortcut, { active = false } = {}) {
  const btn = document.createElement("button");
  btn.className = "tabButton" + (active ? " active" : "");
  btn.textContent = shortcut;
  btn.title = label;
  btn.addEventListener("click", () => setActiveTab(id));
  tabBarEl.append(btn);
  const panel = document.createElement("div");
  panel.className = "tabPanel" + (active ? " active" : "");
  panel.id = `panel-${id}`;
  tabPanelsEl.append(panel);
  tabs[id] = { btn, panel };
  if (active) activeTabId = id;
  return panel;
}

function setActiveTab(id) {
  if (activeTabId === id) return;
  if (activeTabId && tabs[activeTabId]) {
    tabs[activeTabId].btn.classList.remove("active");
    tabs[activeTabId].panel.classList.remove("active");
  }
  activeTabId = id;
  if (tabs[id]) {
    tabs[id].btn.classList.add("active");
    tabs[id].panel.classList.add("active");
  }
}

async function loadShader(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to load shader: ${url}`);
  return await response.text();
}

function wrapShadertoyFragment(source, { defineFast = false } = {}) {
  const fastDefine = defineFast ? "\n#define FAST\n" : "\n";
  return `#version 300 es
precision highp float;
precision highp int;

uniform vec3 iResolution;
uniform float iTime;
uniform float iTimeDelta;
uniform float iFrameRate;
uniform int iFrame;
uniform vec4 iMouse;
uniform vec4 iDate;
uniform float iSampleRate;

uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform sampler2D iChannel2;
uniform sampler2D iChannel3;
uniform vec3 iChannelResolution[4];

// Harness-driven camera override (used by the Image shader; safe to ignore elsewhere).
uniform vec3 uHarnessCameraPos;
uniform vec3 uHarnessTargetDir;
uniform vec3 uHarnessCameraUp;
uniform float uHarnessFovDeg;
${fastDefine}
out vec4 outColor;

${source}

void main() {
  vec4 color = vec4(0.0);
  mainImage(color, gl_FragCoord.xy);
  outColor = color;
}
`;
}

function patchAlroImageShaderForHarnessCamera(source) {
  // Minimal, explicit patching (keeps the shader file itself unchanged).
  // We drive camera parameters from JS so rendering and reprojection share the same source of truth.
  return source
    .replace(
      "vec3 rayDir = rayDirection(55.0, fragCoord);",
      "vec3 rayDir = rayDirection(uHarnessFovDeg, fragCoord);",
    )
    .replace(
      "vec3 cameraPos = vec3(-CLOUD_EXTENT * 0.4, cloudEnd * 0.7, CLOUD_EXTENT * 0.4);",
      "vec3 cameraPos = uHarnessCameraPos;",
    )
    .replace(
      "vec3 targetDir = texelFetch(iChannel0, ivec2(0.5, 1.5), 0).xyz;",
      "vec3 targetDir = uHarnessTargetDir;",
    )
    .replace("vec3 up = vec3(0.0, 1.0, 0.0);", "vec3 up = uHarnessCameraUp;");
}

function getShadertoyUniformLocations(gl, program) {
  return {
    iResolution: gl.getUniformLocation(program, "iResolution"),
    iTime: gl.getUniformLocation(program, "iTime"),
    iTimeDelta: gl.getUniformLocation(program, "iTimeDelta"),
    iFrameRate: gl.getUniformLocation(program, "iFrameRate"),
    iFrame: gl.getUniformLocation(program, "iFrame"),
    iMouse: gl.getUniformLocation(program, "iMouse"),
    iDate: gl.getUniformLocation(program, "iDate"),
    iSampleRate: gl.getUniformLocation(program, "iSampleRate"),
    iChannel0: gl.getUniformLocation(program, "iChannel0"),
    iChannel1: gl.getUniformLocation(program, "iChannel1"),
    iChannel2: gl.getUniformLocation(program, "iChannel2"),
    iChannel3: gl.getUniformLocation(program, "iChannel3"),
    // WebGL uniform arrays are addressed via "[0]" for the base location.
    iChannelResolution0: gl.getUniformLocation(program, "iChannelResolution[0]"),
  };
}

function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const info = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error(`Shader compilation error: ${info}`);
  }
  return shader;
}

function createProgram(gl, vertexSource, fragmentSource) {
  const vs = createShader(gl, gl.VERTEX_SHADER, vertexSource);
  const fs = createShader(gl, gl.FRAGMENT_SHADER, fragmentSource);
  const program = gl.createProgram();
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const info = gl.getProgramInfoLog(program);
    gl.deleteProgram(program);
    gl.deleteShader(vs);
    gl.deleteShader(fs);
    throw new Error(`Program link error: ${info}`);
  }
  gl.deleteShader(vs);
  gl.deleteShader(fs);
  return program;
}

function getUniformLocations(gl, program, names) {
  const uniforms = {};
  for (const name of names) {
    const loc = gl.getUniformLocation(program, name);
    if (loc !== null) uniforms[name] = loc;
  }
  return uniforms;
}

function createFramebuffer(gl, tex) {
  const fb = gl.createFramebuffer();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
  const status = gl.checkFramebufferStatus(gl.FRAMEBUFFER);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  if (status !== gl.FRAMEBUFFER_COMPLETE) {
    throw new Error(`Framebuffer incomplete: ${status}`);
  }
  return fb;
}

function createTexture(gl, width, height, internalFormat, format, type, data = null) {
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, width, height, 0, format, type, data);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.bindTexture(gl.TEXTURE_2D, null);
  return tex;
}

function createDoubleBufferedTexture(gl, width, height, internalFormat, format, type) {
  const buffer = {
    readTex: createTexture(gl, width, height, internalFormat, format, type),
    writeTex: createTexture(gl, width, height, internalFormat, format, type),
    swap() {
      const tempTex = this.readTex;
      this.readTex = this.writeTex;
      this.writeTex = tempTex;
      const tempFbo = this.readFbo;
      this.readFbo = this.writeFbo;
      this.writeFbo = tempFbo;
    }
  };
  buffer.readFbo = createFramebuffer(gl, buffer.readTex);
  buffer.writeFbo = createFramebuffer(gl, buffer.writeTex);
  return buffer;
}

function createBlueNoise(gl) {
  const size = 1024;
  const data = new Uint8Array(size * size);
  for (let i = 0; i < size * size; i++) data[i] = Math.floor(Math.random() * 256);

  // Single-channel is sufficient (shader reads `.r`). Using R8 avoids invalid-sized RGBA uploads.
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.R8, size, size, 0, gl.RED, gl.UNSIGNED_BYTE, data);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
  gl.bindTexture(gl.TEXTURE_2D, null);
  return tex;
}

const vertexShaderSource = `#version 300 es
layout(location = 0) in vec2 aPosition;
void main() {
  gl_Position = vec4(aPosition, 0.0, 1.0);
}`;

async function initWebGL() {
  gl = canvas.getContext("webgl2");
  if (!gl) {
    setError("WebGL2 not supported");
    return;
  }

  const extCBF = gl.getExtension("EXT_color_buffer_float");
  if (!extCBF) {
    setError("EXT_color_buffer_float not supported");
    return;
  }

  // Create VAO
  vao = gl.createVertexArray();
  gl.bindVertexArray(vao);
  const quadBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const posLoc = 0;
  gl.enableVertexAttribArray(posLoc);
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
  gl.bindVertexArray(null);

  // Load shaders
  const [bufferARaw, bufferBRaw, imageRaw, accumSource, godraysSource] = await Promise.all([
    loadShader("./shaders/bufferA.glsl"),
    loadShader("./shaders/bufferB.glsl"),
    loadShader("./shaders/image.glsl"),
    loadShader("./shaders/accum.glsl"),
    loadShader("./shaders/godrays.glsl"),
  ]);

  const bufferASource = wrapShadertoyFragment(bufferARaw);
  const bufferBSource = wrapShadertoyFragment(bufferBRaw);
  const imagePatched = patchAlroImageShaderForHarnessCamera(imageRaw);
  const imageSource = wrapShadertoyFragment(imagePatched);
  const imageFastSource = wrapShadertoyFragment(imagePatched, { defineFast: true });

  // Create programs
  const passAProgram = createProgram(gl, vertexShaderSource, bufferASource);
  passA = {
    program: passAProgram,
    uniforms: getShadertoyUniformLocations(gl, passAProgram),
  };

  const passBProgram = createProgram(gl, vertexShaderSource, bufferBSource);
  passB = {
    program: passBProgram,
    uniforms: getShadertoyUniformLocations(gl, passBProgram),
  };

  const passImageProgram = createProgram(gl, vertexShaderSource, imageSource);
  const imageUniformNames = [
    "uLightingMode",
    "uLightAzimuth",
    "uLightHeight",
    "uLightColor",
    "uLightPower",
    "uExposure",
    "uStars",
    "uNightSkyColor",
    "uDaySkyZenithColor",
    "uDaySkyHorizonColor",
    "uSunDiskIntensity",
    "uSunGlowIntensity",
    "uCelestialDistance",
    "uCelestialSize",
    "uHarnessCameraPos",
    "uHarnessTargetDir",
    "uHarnessCameraUp",
    "uHarnessFovDeg",
  ];
  passImage = {
    program: passImageProgram,
    uniforms: getShadertoyUniformLocations(gl, passImageProgram),
    imageUniforms: getUniformLocations(gl, passImageProgram, imageUniformNames),
  };

  const passImageFastProgram = createProgram(gl, vertexShaderSource, imageFastSource);
  passImageFast = {
    program: passImageFastProgram,
    uniforms: getShadertoyUniformLocations(gl, passImageFastProgram),
    imageUniforms: getUniformLocations(gl, passImageFastProgram, imageUniformNames),
  };

  const passAccumProgram = createProgram(gl, vertexShaderSource, accumSource);
  passAccum = {
    program: passAccumProgram,
    uniforms: getUniformLocations(gl, passAccumProgram, ["uResolution", "uAlpha", "uReset", "uUseReprojection", "uTargetDirCur", "uTargetDirPrev", "uFovDeg", "uCurrent", "uHistory"]),
  };

  const blitSource = `#version 300 es
precision highp float;
uniform vec2 uResolution;
uniform sampler2D uTex;
out vec4 outColor;
void main() {
  outColor = texture(uTex, gl_FragCoord.xy / uResolution);
}`;

  const passBlitProgram = createProgram(gl, vertexShaderSource, blitSource);
  passBlit = {
    program: passBlitProgram,
    uniforms: getUniformLocations(gl, passBlitProgram, ["uResolution", "uTex"]),
  };

  const passGodraysProgram = createProgram(gl, vertexShaderSource, godraysSource);
  passGodrays = {
    program: passGodraysProgram,
    uniforms: getUniformLocations(gl, passGodraysProgram, ["uResolution", "uLightUv", "uLightColor", "uIntensity", "uDensity", "uDecay", "uWeight", "uSamples", "uSourceRadius", "uScene"]),
  };

  // Create blue noise
  blueNoise = createBlueNoise(gl);

  // Initialize render targets
  resizeRenderTargets();

  // Setup input handlers (pointer + keyboard)
  // Notes:
  // - Shadertoy expects iMouse coordinates in the same pixel space as iResolution (rtWidth/rtHeight), origin bottom-left.
  // - Keyboard listeners are attached to window so flight controls work without requiring canvas focus.
  canvas.tabIndex = 0;
  canvas.style.outline = "none";
  canvas.style.touchAction = "none";

  canvas.addEventListener("contextmenu", (e) => e.preventDefault());

  canvas.addEventListener("pointerdown", (e) => {
    updateMouseFromPointerEvent(e);
    canvas.focus();

    if (cameraMode === "orbit") {
      state.mouseDown = true;
      try {
        canvas.setPointerCapture(e.pointerId);
      } catch {}
      return;
    }

    // Fly mode uses pointer-lock for continuous look (Esc to release).
    if (document.pointerLockElement !== canvas) {
      try {
        canvas.requestPointerLock();
      } catch {}
    }
  });

  canvas.addEventListener("pointermove", (e) => {
    updateMouseFromPointerEvent(e);
    if (isPointerLocked) {
      flyLookDx += e.movementX || 0;
      flyLookDy += e.movementY || 0;
    }
  });

  const onPointerUp = (e) => {
    updateMouseFromPointerEvent(e);
    if (cameraMode === "orbit") state.mouseDown = false;
    try {
      canvas.releasePointerCapture(e.pointerId);
    } catch {}
  };
  canvas.addEventListener("pointerup", onPointerUp);
  canvas.addEventListener("pointercancel", onPointerUp);

  document.addEventListener("pointerlockchange", () => {
    isPointerLocked = document.pointerLockElement === canvas;
    flyLookDx = 0;
    flyLookDy = 0;
  });

  canvas.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();

      // Jet mode: wheel adjusts throttle while pointer-locked (Ctrl/Cmd/Alt+wheel keeps FOV zoom).
      if (cameraMode === "jet" && isPointerLocked && !(e.ctrlKey || e.metaKey || e.altKey)) {
        const delta = e.deltaY || 0;
        const step = clamp(-delta * 0.001, -0.2, 0.2);
        applyConfigPatch({ jetThrottle: clamp(jetThrottle + step, 0, 1) });
        return;
      }

      const zoom = Math.exp((e.deltaY || 0) * 0.001);
      const nextFov = clamp(fovDeg * zoom, 20, 110);
      applyConfigPatch({ fovDeg: nextFov });
    },
    { passive: false },
  );

  window.addEventListener("keydown", (e) => {
    const key = e.key.toLowerCase();
    state.keys[key] = true;

    // Avoid scrolling the page while flying.
    if (isPointerLocked && key.startsWith("arrow")) e.preventDefault();

    // One-shot toggles (ignore repeats + don't trigger while editing inputs).
    if (e.repeat) return;
    const tag = (e.target && e.target.tagName ? String(e.target.tagName).toLowerCase() : "");
    if (tag === "input" || tag === "textarea") return;

    if (key === "m" && cameraMode === "jet") {
      applyConfigPatch({ jetMouseAim: !jetMouseAim });
    }
    if (key === "c" && cameraMode === "jet") {
      jetCursor.x = 0;
      jetCursor.y = 0;
      jetRates.yaw = 0;
      jetRates.pitch = 0;
      jetRates.roll = 0;
      jetAngles.roll = 0;
    }
  });
  window.addEventListener("keyup", (e) => {
    state.keys[e.key.toLowerCase()] = false;
  });
  window.addEventListener("blur", () => {
    for (const key of Object.keys(state.keys)) delete state.keys[key];
    state.mouseDown = false;
  });

  window.addEventListener("resize", () => {
    resizeRenderTargets();
  });

  // Initialize UI
  initControls();

  // Start render loop
  setError("");
  requestAnimationFrame(tick);
}

// Start initialization
initWebGL().catch(err => {
  setError(`Initialization failed: ${err.message}`);
  console.error(err);
});

function resizeRenderTargets() {
  const dpr = getDpr();
  rtWidth = Math.floor(canvas.clientWidth * renderScale * dpr);
  rtHeight = Math.floor(canvas.clientHeight * renderScale * dpr);
  canvas.width = rtWidth;
  canvas.height = rtHeight;

  const useFloat = !!gl.getExtension("EXT_color_buffer_float");
  const internalFormat = useFloat ? gl.RGBA16F : gl.RGBA8;
  const format = gl.RGBA;
  const type = useFloat ? (gl.HALF_FLOAT || 0x140B) : gl.UNSIGNED_BYTE;

  // BufferA: 1x4
  bufferA = createDoubleBufferedTexture(gl, 1, 4, internalFormat, format, type);

  // BufferB: full resolution
  bufferB = createDoubleBufferedTexture(gl, rtWidth, rtHeight, internalFormat, format, type);
  needsBufferBRebuild = true;

  // History: full resolution
  history = createDoubleBufferedTexture(gl, rtWidth, rtHeight, internalFormat, format, type);

  // Current color: full resolution
  currentColorTex = createTexture(gl, rtWidth, rtHeight, internalFormat, format, type);
  currentColorFbo = createFramebuffer(gl, currentColorTex);
}

function selectImagePass() {
  // This would rebuild passImage/passImageFast if needed
  // For now, we assume they're already created
}

function setError(message) {
  if (!errorEl) return;
  const text = message ?? "";
  errorEl.textContent = text;
  if (text) setActiveTab("status");
}

function normalizePresetKey(value) {
  return (value ?? "")
    .trim()
    .toLowerCase()
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-");
}

const BASE_DEFAULTS = {
  scale: 1,
  timeScale: 1,
  fast: false,
  fastWhileDrag: true,
  taa: true,
  reproject: true,
  // If disabled, we reset history while dragging (responsive, but grain returns).
  // If enabled, we keep accumulating (smoother, but needs a higher alpha while moving).
  taaDuringDrag: true,
  taaAlpha: 0.12,
  // Motion-aware blend: use a higher alpha while dragging to reduce "laggy" history.
  taaUseDragAlpha: true,
  taaAlphaDrag: 0.28,

  lighting: "night", // "night" | "day"
  lightAzimuthDeg: (4.5 * 180) / Math.PI,
  lightHeight: 0.25,
  lightColor: "#a5ccff",
  lightPower: 100,
  exposure: 0.5,
  stars: 1,
  nightSkyColor: "#08111a",
  daySkyZenithColor: "#3a7bd5",
  daySkyHorizonColor: "#d8f0ff",
  sunDiskIntensity: 1.6,
  sunGlowIntensity: 1.0,
  celestialDistance: 100,
  celestialSize: 8,

  godrays: false,
  godraysDuringDrag: false,
  godraysSamples: 48,
  godraysDensity: 0.95,
  godraysDecay: 0.965,
  godraysWeight: 0.02,
  godraysIntensity: 1.0,
  godraysRadiusScale: 1.0,

  // Clouds
  shapeSpeed: -5,
  detailSpeed: -10,
  densityMultiplier: 0.075,
  shapeStrength: 0.7,
  detailStrength: 0.2,
  noiseSeed: 0.0,

  // Camera / flight
  cameraMode: "orbit", // orbit | fly | jet
  fovDeg: 55,
  flightSpeed: 60,
  flightBoost: 2.5,
  flightDamping: 1.5,
  flightBank: true,
  flightBankStrength: 0.6,

  // Jet flight (Warthunder-style mouse aim + throttle)
  jetThrottle: 0.45,
  jetMinSpeed: 20,
  jetMaxSpeed: 260,
  // Higher = faster speed response to throttle changes.
  jetThrottleResponse: 2.5,
  // Max angular rates (rad/s). Higher = more agile.
  jetYawRate: 2.0,
  jetPitchRate: 1.6,
  jetRollRate: 3.6,
  jetMouseAim: true,
  jetAutoBank: true,
  jetAutoBankStrength: 0.9,
  // Virtual cursor sensitivity + clamp range for mouse-aim.
  jetCursorSensitivity: 1.0,
  jetCursorMax: 0.85,
};

const PRESETS = {
  "fast-crisp": {
    label: "fast-crisp",
    defaults: {
      scale: 0.6,
      fast: true,
      fastWhileDrag: true,
      taa: true,
      reproject: true,
      taaDuringDrag: true,
      taaAlpha: 0.22,
      taaUseDragAlpha: true,
      taaAlphaDrag: 0.35,
    },
  },
  smooth: {
    label: "smooth",
    defaults: {
      scale: 1,
      fast: false,
      fastWhileDrag: true,
      taa: true,
      reproject: true,
      taaDuringDrag: true,
      taaAlpha: 0.07,
      taaUseDragAlpha: true,
      taaAlphaDrag: 0.25,
    },
  },
};

const PRESET_ALIASES = {
  fast: "fast-crisp",
  crisp: "fast-crisp",
  quality: "smooth",
};

const LIGHTING_PRESETS = {
  night: {
    lighting: "night",
    stars: 1,
    lightColor: "#a5ccff",
    lightPower: 100,
    exposure: 0.5,
    nightSkyColor: "#08111a",
    daySkyZenithColor: "#3a7bd5",
    daySkyHorizonColor: "#d8f0ff",
    sunDiskIntensity: 1.6,
    sunGlowIntensity: 1.0,
    celestialDistance: 100,
    celestialSize: 8,
  },
  day: {
    lighting: "day",
    stars: 0,
    lightColor: "#fff2d0",
    lightPower: 160,
    exposure: 0.85,
    nightSkyColor: "#08111a",
    daySkyZenithColor: "#3a7bd5",
    daySkyHorizonColor: "#d8f0ff",
    sunDiskIntensity: 3.0,
    sunGlowIntensity: 2.0,
    celestialDistance: 300,
    celestialSize: 2,
  },
};

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function getBoolParam(name, defaultValue) {
  const raw = urlParams.get(name);
  if (raw == null) return defaultValue;
  if (raw === "") return true;
  const v = raw.toLowerCase();
  if (v === "1" || v === "true" || v === "yes" || v === "on") return true;
  if (v === "0" || v === "false" || v === "no" || v === "off") return false;
  return defaultValue;
}

function getFloatParam(name, defaultValue, min, max) {
  const raw = urlParams.get(name);
  if (raw == null) return defaultValue;
  const value = Number.parseFloat(raw);
  if (!Number.isFinite(value)) return defaultValue;
  return Math.min(max, Math.max(min, value));
}

function getIntParam(name, defaultValue, min, max) {
  const raw = urlParams.get(name);
  if (raw == null) return defaultValue;
  const value = Number.parseInt(raw, 10);
  if (!Number.isFinite(value)) return defaultValue;
  return Math.min(max, Math.max(min, value));
}

function getEnumParam(name, defaultValue, allowedValues) {
  const raw = urlParams.get(name);
  if (raw == null) return defaultValue;
  const normalized = normalizePresetKey(raw);
  return allowedValues.includes(normalized) ? normalized : defaultValue;
}

function normalizeHexColor(value, fallback) {
  if (value == null) return fallback;
  const raw = String(value).trim();
  if (!raw) return fallback;
  const withHash = raw.startsWith("#") ? raw : `#${raw}`;
  const match = withHash.match(/^#[0-9a-fA-F]{6}$/);
  return match ? withHash.toLowerCase() : fallback;
}

function hexToRgb01(hex) {
  const h = hex.startsWith("#") ? hex.slice(1) : hex;
  const r = Number.parseInt(h.slice(0, 2), 16) / 255;
  const g = Number.parseInt(h.slice(2, 4), 16) / 255;
  const b = Number.parseInt(h.slice(4, 6), 16) / 255;
  return [r, g, b];
}

const presetKeyRaw = normalizePresetKey(urlParams.get("preset"));
const presetKeyResolved = (() => {
  if (!presetKeyRaw) return "";
  if (PRESETS[presetKeyRaw]) return presetKeyRaw;
  if (PRESET_ALIASES[presetKeyRaw]) return PRESET_ALIASES[presetKeyRaw];
  return "";
})();
const presetConfig = presetKeyResolved ? PRESETS[presetKeyResolved] : null;
const effectiveDefaults = { ...BASE_DEFAULTS, ...(presetConfig?.defaults ?? {}) };

let activePresetKey = presetKeyResolved;
let activePresetLabel = presetKeyRaw
  ? presetConfig
    ? presetConfig.label
    : `${presetKeyRaw} (unknown)`
  : "(none)";

let renderScale = getFloatParam("scale", effectiveDefaults.scale, 0.2, 1);
let timeScale = getFloatParam("timeScale", effectiveDefaults.timeScale, 0.01, 5);
let fastMode = getBoolParam("fast", effectiveDefaults.fast);
let fastWhileDrag = getBoolParam("fastWhileDrag", effectiveDefaults.fastWhileDrag);
let taaEnabled = getBoolParam("taa", effectiveDefaults.taa);
let taaReproject = getBoolParam("reproject", effectiveDefaults.reproject);
let taaDuringDrag = getBoolParam("taaDuringDrag", effectiveDefaults.taaDuringDrag);
let taaAlpha = getFloatParam("taaAlpha", effectiveDefaults.taaAlpha, 0.02, 0.5);
let taaUseDragAlpha = getBoolParam("taaUseDragAlpha", effectiveDefaults.taaUseDragAlpha);
let taaAlphaDrag = getFloatParam("taaAlphaDrag", effectiveDefaults.taaAlphaDrag, 0.02, 0.5);

let lightingMode = getEnumParam("lighting", effectiveDefaults.lighting, ["night", "day"]);
let lightAzimuthDeg = getFloatParam("lightAz", effectiveDefaults.lightAzimuthDeg, 0, 360);
let lightHeight = getFloatParam("lightH", effectiveDefaults.lightHeight, -1, 1);
let lightPower = getFloatParam("lightPower", effectiveDefaults.lightPower, 0, 400);
let exposure = getFloatParam("exposure", effectiveDefaults.exposure, 0, 2);
let stars = getFloatParam("stars", effectiveDefaults.stars, 0, 1);

let lightColorHex = normalizeHexColor(urlParams.get("lightColor"), effectiveDefaults.lightColor);
let nightSkyColorHex = normalizeHexColor(urlParams.get("nightSky"), effectiveDefaults.nightSkyColor);
let daySkyZenithColorHex = normalizeHexColor(urlParams.get("dayZenith"), effectiveDefaults.daySkyZenithColor);
let daySkyHorizonColorHex = normalizeHexColor(urlParams.get("dayHorizon"), effectiveDefaults.daySkyHorizonColor);

let lightColorRgb = hexToRgb01(lightColorHex);
let nightSkyColorRgb = hexToRgb01(nightSkyColorHex);
let daySkyZenithColorRgb = hexToRgb01(daySkyZenithColorHex);
let daySkyHorizonColorRgb = hexToRgb01(daySkyHorizonColorHex);

let sunDiskIntensity = getFloatParam("sunDisk", effectiveDefaults.sunDiskIntensity, 0, 5);
let sunGlowIntensity = getFloatParam("sunGlow", effectiveDefaults.sunGlowIntensity, 0, 5);
let celestialDistance = getFloatParam("celestialDist", effectiveDefaults.celestialDistance, 10, 500);
let celestialSize = getFloatParam("celestialSize", effectiveDefaults.celestialSize, 0.1, 50);

let godraysEnabled = getBoolParam("godrays", effectiveDefaults.godrays);
let godraysDuringDrag = getBoolParam("godraysDuringDrag", effectiveDefaults.godraysDuringDrag);
let godraysSamples = getIntParam("godraysSamples", effectiveDefaults.godraysSamples, 4, 128);
let godraysDensity = getFloatParam("godraysDensity", effectiveDefaults.godraysDensity, 0, 2);
let godraysDecay = getFloatParam("godraysDecay", effectiveDefaults.godraysDecay, 0.8, 1);
let godraysWeight = getFloatParam("godraysWeight", effectiveDefaults.godraysWeight, 0, 1);
let godraysIntensity = getFloatParam("godraysIntensity", effectiveDefaults.godraysIntensity, 0, 5);
let godraysRadiusScale = getFloatParam("godraysRadius", effectiveDefaults.godraysRadiusScale, 0.25, 4);

let shapeSpeed = getFloatParam("shapeSpeed", effectiveDefaults.shapeSpeed, -50, 50);
let detailSpeed = getFloatParam("detailSpeed", effectiveDefaults.detailSpeed, -50, 50);
let densityMultiplier = getFloatParam("densityMul", effectiveDefaults.densityMultiplier, 0, 1);
let shapeStrength = getFloatParam("shapeStrength", effectiveDefaults.shapeStrength, 0, 2);
let detailStrength = getFloatParam("detailStrength", effectiveDefaults.detailStrength, 0, 2);
let noiseSeed = getFloatParam("noiseSeed", effectiveDefaults.noiseSeed, -1000, 1000);

let cameraMode = getEnumParam("cam", effectiveDefaults.cameraMode, ["orbit", "fly", "jet"]);
let fovDeg = getFloatParam("fov", effectiveDefaults.fovDeg, 20, 110);
let flightSpeed = getFloatParam("flySpeed", effectiveDefaults.flightSpeed, 1, 500);
let flightBoost = getFloatParam("flyBoost", effectiveDefaults.flightBoost, 1, 10);
let flightDamping = getFloatParam("flyDamp", effectiveDefaults.flightDamping, 0, 10);
let flightBank = getBoolParam("flyBank", effectiveDefaults.flightBank);
let flightBankStrength = getFloatParam("flyBankStrength", effectiveDefaults.flightBankStrength, 0, 2);

let jetThrottle = getFloatParam("jetThrottle", effectiveDefaults.jetThrottle, 0, 1);
let jetMinSpeed = getFloatParam("jetMinSpeed", effectiveDefaults.jetMinSpeed, 0, 500);
let jetMaxSpeed = getFloatParam("jetMaxSpeed", effectiveDefaults.jetMaxSpeed, 1, 2000);
let jetThrottleResponse = getFloatParam("jetThrottleResponse", effectiveDefaults.jetThrottleResponse, 0, 20);
let jetYawRate = getFloatParam("jetYawRate", effectiveDefaults.jetYawRate, 0, 20);
let jetPitchRate = getFloatParam("jetPitchRate", effectiveDefaults.jetPitchRate, 0, 20);
let jetRollRate = getFloatParam("jetRollRate", effectiveDefaults.jetRollRate, 0, 50);
let jetMouseAim = getBoolParam("jetMouseAim", effectiveDefaults.jetMouseAim);
let jetAutoBank = getBoolParam("jetAutoBank", effectiveDefaults.jetAutoBank);
let jetAutoBankStrength = getFloatParam("jetAutoBankStrength", effectiveDefaults.jetAutoBankStrength, 0, 3);
let jetCursorSensitivity = getFloatParam("jetCursorSensitivity", effectiveDefaults.jetCursorSensitivity, 0.05, 10);
let jetCursorMax = getFloatParam("jetCursorMax", effectiveDefaults.jetCursorMax, 0, 1);

// If the user requests day lighting but doesn't specify the full set of knobs,
// seed missing values from the day lighting preset so "lighting=day" looks good immediately.
if (lightingMode === "day") {
  const preset = LIGHTING_PRESETS.day;

  if (!urlParams.has("stars")) stars = preset.stars;
  if (!urlParams.has("lightColor")) {
    lightColorHex = preset.lightColor;
    lightColorRgb = hexToRgb01(lightColorHex);
  }
  if (!urlParams.has("lightPower")) lightPower = preset.lightPower;
  if (!urlParams.has("exposure")) exposure = preset.exposure;
  if (!urlParams.has("dayZenith")) {
    daySkyZenithColorHex = preset.daySkyZenithColor;
    daySkyZenithColorRgb = hexToRgb01(daySkyZenithColorHex);
  }
  if (!urlParams.has("dayHorizon")) {
    daySkyHorizonColorHex = preset.daySkyHorizonColor;
    daySkyHorizonColorRgb = hexToRgb01(daySkyHorizonColorHex);
  }
  if (!urlParams.has("sunDisk")) sunDiskIntensity = preset.sunDiskIntensity;
  if (!urlParams.has("sunGlow")) sunGlowIntensity = preset.sunGlowIntensity;
  if (!urlParams.has("celestialDist")) celestialDistance = preset.celestialDistance;
  if (!urlParams.has("celestialSize")) celestialSize = preset.celestialSize;
}

const CLOUD_EXTENT_JS = 1000.0;

const state = {
  mouseX: 0,
  mouseY: 0,
  mouseDown: false,
  keys: {},
};

const cameraAngles = {
  x: 0.1,
  y: 0.07,
  prevMouseNormX: 0,
  prevMouseNormY: 0,
  prevDown: false,
};

const orbitCameraPos = [-CLOUD_EXTENT_JS * 0.4, 0.7 * CLOUD_EXTENT_JS, CLOUD_EXTENT_JS * 0.4];

const flightState = {
  pos: [-CLOUD_EXTENT_JS * 0.4, 0.7 * CLOUD_EXTENT_JS, CLOUD_EXTENT_JS * 0.4],
  vel: [0, 0, 0],
};

const flightAngles = {
  x: 0.1, // yaw (same convention as BufferA)
  y: 0.07, // "elevation" stored as y component (same convention as BufferA)
  roll: 0,
};

// Jet mode state (separate from "fly" so we can keep both modes stable).
const jetState = {
  pos: [-CLOUD_EXTENT_JS * 0.4, 0.7 * CLOUD_EXTENT_JS, CLOUD_EXTENT_JS * 0.4],
  speed: 0,
};

const jetAngles = {
  x: 0.1,
  y: 0.07,
  roll: 0,
};

const jetRates = {
  yaw: 0,
  pitch: 0,
  roll: 0,
};

// Virtual cursor for mouse-aim (screen-space offsets around the center).
const jetCursor = { x: 0, y: 0 };

let isPointerLocked = false;
let flyLookDx = 0;
let flyLookDy = 0;

let cameraPosThisFrame = [...orbitCameraPos];
let cameraTargetDirThisFrame = [Math.sin(0.1), 0.07, -Math.cos(0.1)];
let cameraUpThisFrame = [0, 1, 0];

let prevMouseDownForQualitySwitch = false;

function getDpr() {
  return Math.max(1, Math.min(2, window.devicePixelRatio || 1));
}

function updateMouseFromPointerEvent(e) {
  const rect = canvas.getBoundingClientRect();
  const width = rect.width || canvas.clientWidth || 1;
  const height = rect.height || canvas.clientHeight || 1;

  const xCss = e.clientX - rect.left;
  const yCss = e.clientY - rect.top;

  const x01 = clamp(xCss / width, 0, 1);
  const y01 = clamp(yCss / height, 0, 1);

  // Shadertoy convention: iMouse is in the same pixel space as iResolution, with origin at bottom-left.
  state.mouseX = x01 * rtWidth;
  state.mouseY = (1 - y01) * rtHeight;
}

function renderSettingsOverlay() {
  if (!settingsEl) return;

  const lines = [
    ["preset:", activePresetLabel],
    ["scale:", renderScale.toFixed(2)],
    ["timeScale:", timeScale.toFixed(2)],
    ["fast:", fastMode ? "on" : "off"],
    ["fastWhileDrag:", fastWhileDrag ? "on" : "off"],
    ["taa:", taaEnabled ? "on" : "off"],
    ["lighting:", lightingMode],
    ["godrays:", godraysEnabled ? "on" : "off"],
    ["cam:", cameraMode],
    ["fov:", fovDeg.toFixed(0)],
    ["fps:", simFrameRate.toFixed(1)],
  ];

  if (taaEnabled) {
    lines.push(["taaAlpha:", taaAlpha.toFixed(3)]);
    if (taaUseDragAlpha) lines.push(["taaAlphaDrag:", taaAlphaDrag.toFixed(3)]);
    lines.push(["reproject:", taaReproject ? "on" : "off"]);
    lines.push(["accumWhileDrag:", taaDuringDrag ? "on" : "off"]);
  }

  lines.push(["stars:", stars.toFixed(2)]);

  settingsEl.textContent = "";
  for (const [label, value] of lines) {
    const row = document.createElement("div");
    row.append(document.createTextNode(`${label} `));
    const code = document.createElement("code");
    code.textContent = value;
    row.append(code);
    settingsEl.append(row);
  }

  const presetsRow = document.createElement("div");
  presetsRow.style.marginTop = "4px";
  presetsRow.append(document.createTextNode("presets: "));
  const presetsCode = document.createElement("code");
  presetsCode.textContent = "?preset=fast-crisp  |  ?preset=smooth";
  presetsRow.append(presetsCode);
  settingsEl.append(presetsRow);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function markCustomPreset() {
  activePresetKey = "";
  activePresetLabel = "(custom)";
}

function buildShareUrl() {
  const base = `${window.location.origin}${window.location.pathname}`;
  const params = new URLSearchParams();

  if (activePresetKey) params.set("preset", activePresetKey);
  params.set("scale", String(renderScale));
  params.set("fast", fastMode ? "1" : "0");
  params.set("fastWhileDrag", fastWhileDrag ? "1" : "0");
  params.set("taa", taaEnabled ? "1" : "0");
  params.set("reproject", taaReproject ? "1" : "0");
  params.set("taaDuringDrag", taaDuringDrag ? "1" : "0");
  params.set("taaAlpha", String(taaAlpha));
  params.set("taaUseDragAlpha", taaUseDragAlpha ? "1" : "0");
  params.set("taaAlphaDrag", String(taaAlphaDrag));
  params.set("timeScale", String(timeScale));

  params.set("lighting", lightingMode);
  params.set("lightAz", String(lightAzimuthDeg));
  params.set("lightH", String(lightHeight));
  params.set("lightColor", lightColorHex);
  params.set("lightPower", String(lightPower));
  params.set("exposure", String(exposure));
  params.set("stars", String(stars));
  params.set("nightSky", nightSkyColorHex);
  params.set("dayZenith", daySkyZenithColorHex);
  params.set("dayHorizon", daySkyHorizonColorHex);
  params.set("sunDisk", String(sunDiskIntensity));
  params.set("sunGlow", String(sunGlowIntensity));
  params.set("celestialDist", String(celestialDistance));
  params.set("celestialSize", String(celestialSize));

  params.set("godrays", godraysEnabled ? "1" : "0");
  params.set("godraysDuringDrag", godraysDuringDrag ? "1" : "0");
  params.set("godraysSamples", String(godraysSamples));
  params.set("godraysDensity", String(godraysDensity));
  params.set("godraysDecay", String(godraysDecay));
  params.set("godraysWeight", String(godraysWeight));
  params.set("godraysIntensity", String(godraysIntensity));
  params.set("godraysRadius", String(godraysRadiusScale));

  params.set("shapeSpeed", String(shapeSpeed));
  params.set("detailSpeed", String(detailSpeed));
  params.set("densityMul", String(densityMultiplier));
  params.set("shapeStrength", String(shapeStrength));
  params.set("detailStrength", String(detailStrength));
  params.set("noiseSeed", String(noiseSeed));

  params.set("cam", cameraMode);
  params.set("fov", String(fovDeg));
  params.set("flySpeed", String(flightSpeed));
  params.set("flyBoost", String(flightBoost));
  params.set("flyDamp", String(flightDamping));
  params.set("flyBank", flightBank ? "1" : "0");
  params.set("flyBankStrength", String(flightBankStrength));

  params.set("jetThrottle", String(jetThrottle));
  params.set("jetMinSpeed", String(jetMinSpeed));
  params.set("jetMaxSpeed", String(jetMaxSpeed));
  params.set("jetThrottleResponse", String(jetThrottleResponse));
  params.set("jetYawRate", String(jetYawRate));
  params.set("jetPitchRate", String(jetPitchRate));
  params.set("jetRollRate", String(jetRollRate));
  params.set("jetMouseAim", jetMouseAim ? "1" : "0");
  params.set("jetAutoBank", jetAutoBank ? "1" : "0");
  params.set("jetAutoBankStrength", String(jetAutoBankStrength));
  params.set("jetCursorSensitivity", String(jetCursorSensitivity));
  params.set("jetCursorMax", String(jetCursorMax));

  return `${base}?${params.toString()}`;
}

const ui = {
  presetSelect: null,
  scaleRange: null,
  scaleValue: null,
  timeScaleRange: null,
  timeScaleValue: null,
  fastCheckbox: null,
  fastWhileDragCheckbox: null,
  taaCheckbox: null,
  reprojectCheckbox: null,
  accumWhileDragCheckbox: null,
  alphaRange: null,
  alphaValue: null,
  useDragAlphaCheckbox: null,
  alphaDragRange: null,
  alphaDragValue: null,
  lightingSelect: null,
  lightAzRange: null,
  lightAzValue: null,
  lightHeightRange: null,
  lightHeightValue: null,
  lightColorInput: null,
  lightPowerRange: null,
  lightPowerValue: null,
  exposureRange: null,
  exposureValue: null,
  starsRange: null,
  starsValue: null,
  nightSkyColorInput: null,
  daySkyZenithColorInput: null,
  daySkyHorizonColorInput: null,
  sunDiskRange: null,
  sunDiskValue: null,
  sunGlowRange: null,
  sunGlowValue: null,
  celestialDistRange: null,
  celestialDistValue: null,
  celestialSizeRange: null,
  celestialSizeValue: null,
  shapeSpeedRange: null,
  shapeSpeedValue: null,
  detailSpeedRange: null,
  detailSpeedValue: null,
  densityMulRange: null,
  densityMulValue: null,
  shapeStrengthRange: null,
  shapeStrengthValue: null,
  detailStrengthRange: null,
  detailStrengthValue: null,
  noiseSeedRange: null,
  noiseSeedValue: null,
  cameraModeSelect: null,
  fovRange: null,
  fovValue: null,
  flightSpeedRange: null,
  flightSpeedValue: null,
  flightBoostRange: null,
  flightBoostValue: null,
  flightDampingRange: null,
  flightDampingValue: null,
  flightBankCheckbox: null,
  flightBankStrengthRange: null,
  flightBankStrengthValue: null,
  jetThrottleRange: null,
  jetThrottleValue: null,
  jetMinSpeedRange: null,
  jetMinSpeedValue: null,
  jetMaxSpeedRange: null,
  jetMaxSpeedValue: null,
  jetThrottleResponseRange: null,
  jetThrottleResponseValue: null,
  jetYawRateRange: null,
  jetYawRateValue: null,
  jetPitchRateRange: null,
  jetPitchRateValue: null,
  jetRollRateRange: null,
  jetRollRateValue: null,
  jetMouseAimCheckbox: null,
  jetAutoBankCheckbox: null,
  jetAutoBankStrengthRange: null,
  jetAutoBankStrengthValue: null,
  jetCursorSensitivityRange: null,
  jetCursorSensitivityValue: null,
  jetCursorMaxRange: null,
  jetCursorMaxValue: null,
  godraysCheckbox: null,
  godraysDuringDragCheckbox: null,
  godraysSamplesRange: null,
  godraysSamplesValue: null,
  godraysDensityRange: null,
  godraysDensityValue: null,
  godraysDecayRange: null,
  godraysDecayValue: null,
  godraysWeightRange: null,
  godraysWeightValue: null,
  godraysIntensityRange: null,
  godraysIntensityValue: null,
  godraysRadiusRange: null,
  godraysRadiusValue: null,
  resetHistoryBtn: null,
  shareUrlInput: null,
  copyUrlBtn: null,
};

let isSyncingUi = false;

const tabs = {};
let activeTabId = null;

function createControlRow(labelText, controlEl, valueEl = null) {
  const row = document.createElement('div');
  row.className = 'controlRow';
  const label = document.createElement('label');
  label.textContent = labelText;
  row.append(label);
  const right = document.createElement('div');
  right.style.display = 'flex';
  right.style.alignItems = 'center';
  right.style.gap = '8px';
  right.append(controlEl);
  if (valueEl) right.append(valueEl);
  row.append(right);
  return row;
}

function createSection(panel, title, hint, { open = true } = {}) {
  const details = document.createElement('details');
  details.className = 'drawer';
  details.open = open;

  const summary = document.createElement('summary');
  summary.textContent = title;
  details.append(summary);

  const wrapper = document.createElement('div');
  wrapper.style.display = 'flex';
  wrapper.style.flexDirection = 'column';
  wrapper.style.gap = '10px';
  wrapper.style.paddingTop = '8px';

  if (hint) {
    const hintEl = document.createElement('div');
    hintEl.className = 'controlHint';
    hintEl.textContent = hint;
    wrapper.append(hintEl);
  }

  details.append(wrapper);
  panel.append(details);
  return wrapper;
}

function addCheckbox(panel, label, key, onChange) {
  const input = document.createElement('input');
  input.type = 'checkbox';
  input.addEventListener('change', () => {
    if (isSyncingUi) return;
    if (onChange) onChange(input.checked);
    applyConfigPatch({ [key]: input.checked });
  });
  panel.append(createControlRow(label, input));
  return input;
}

function addSelect(panel, label, options, key, onChange) {
  const select = document.createElement('select');
  options.forEach((opt) => select.append(new Option(opt.label, opt.value)));
  select.addEventListener('change', () => {
    if (isSyncingUi) return;
    if (onChange) onChange(select.value);
    applyConfigPatch({ [key]: select.value });
  });
  panel.append(createControlRow(label, select));
  return select;
}

function addSlider(panel, label, key, { min, max, step, format = (v) => v.toFixed(2), onInput, onCommit } = {}) {
  const input = document.createElement('input');
  input.type = 'range';
  input.min = String(min);
  input.max = String(max);
  input.step = String(step);
  const valueEl = document.createElement('code');
  const updateValue = () => {
    const v = Number(input.value);
    valueEl.textContent = format(v);
    if (onInput) onInput(v);
  };
  input.addEventListener('input', () => {
    if (isSyncingUi) return;
    updateValue();
  });
  input.addEventListener('change', () => {
    if (isSyncingUi) return;
    const v = Number(input.value);
    if (onCommit) onCommit(v);
    applyConfigPatch({ [key]: v });
  });
  updateValue();
  panel.append(createControlRow(label, input, valueEl));
  return { input, valueEl, updateValue };
}

function addColor(panel, label, key) {
  const input = document.createElement('input');
  input.type = 'color';
  input.addEventListener('change', () => {
    if (isSyncingUi) return;
    applyConfigPatch({ [key]: input.value });
  });
  panel.append(createControlRow(label, input));
  return input;
}

function applyPreset(key) {
  const preset = PRESETS[key];
  if (!preset) return;
  activePresetKey = key;
  activePresetLabel = preset.label || key;
  const defaults = { ...BASE_DEFAULTS, ...(preset.defaults ?? {}) };
  applyConfigPatch(
    {
      ...defaults,
      lighting: defaults.lighting,
    },
    { markCustom: false },
  );
}

function applyLightingPreset(mode) {
  const preset = LIGHTING_PRESETS[mode];
  if (!preset) return;
  applyConfigPatch(preset);
}

function applyConfigPatch(patch, { markCustom = true } = {}) {
  const prevCameraMode = cameraMode;
  const prevScale = renderScale;
  const prevFast = fastMode;
  const prevFastWhileDrag = fastWhileDrag;
  const prevTaa = taaEnabled;
  const prevReproject = taaReproject;
  const prevFovDeg = fovDeg;
  const prevLightingMode = lightingMode;
  const prevLightAzimuthDeg = lightAzimuthDeg;
  const prevLightHeight = lightHeight;
  const prevLightColorHex = lightColorHex;
  const prevLightPower = lightPower;
  const prevExposure = exposure;
  const prevStars = stars;
  const prevNightSkyHex = nightSkyColorHex;
  const prevDayZenithHex = daySkyZenithColorHex;
  const prevDayHorizonHex = daySkyHorizonColorHex;
  const prevSunDisk = sunDiskIntensity;
  const prevSunGlow = sunGlowIntensity;
  const prevCelestialDist = celestialDistance;
  const prevCelestialSize = celestialSize;
  const prevGodraysEnabled = godraysEnabled;

  if (Object.prototype.hasOwnProperty.call(patch, 'scale')) {
    renderScale = clamp(Number(patch.scale) || renderScale, 0.2, 1);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'timeScale')) {
    timeScale = clamp(Number(patch.timeScale) || timeScale, 0.01, 5);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'fast')) fastMode = Boolean(patch.fast);
  if (Object.prototype.hasOwnProperty.call(patch, 'fastWhileDrag')) {
    fastWhileDrag = Boolean(patch.fastWhileDrag);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'taa')) taaEnabled = Boolean(patch.taa);
  if (Object.prototype.hasOwnProperty.call(patch, 'reproject')) taaReproject = Boolean(patch.reproject);
  if (Object.prototype.hasOwnProperty.call(patch, 'taaDuringDrag')) taaDuringDrag = Boolean(patch.taaDuringDrag);
  if (Object.prototype.hasOwnProperty.call(patch, 'taaAlpha')) {
    taaAlpha = clamp(Number(patch.taaAlpha) || taaAlpha, 0.02, 0.5);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'taaUseDragAlpha')) {
    taaUseDragAlpha = Boolean(patch.taaUseDragAlpha);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'taaAlphaDrag')) {
    taaAlphaDrag = clamp(Number(patch.taaAlphaDrag) || taaAlphaDrag, 0.02, 0.5);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'fovDeg')) {
    fovDeg = clamp(Number(patch.fovDeg) || fovDeg, 20, 110);
  }

  if (Object.prototype.hasOwnProperty.call(patch, 'lighting')) {
    lightingMode = patch.lighting === 'day' ? 'day' : 'night';
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'lightAzimuthDeg')) {
    lightAzimuthDeg = clamp(Number(patch.lightAzimuthDeg) || lightAzimuthDeg, 0, 360);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'lightHeight')) {
    lightHeight = clamp(Number(patch.lightHeight) || lightHeight, -1, 1);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'lightPower')) {
    lightPower = clamp(Number(patch.lightPower) || lightPower, 0, 400);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'exposure')) {
    exposure = clamp(Number(patch.exposure) || exposure, 0, 2);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'stars')) {
    stars = clamp(Number(patch.stars) || stars, 0, 1);
  }

  if (Object.prototype.hasOwnProperty.call(patch, 'lightColor')) {
    lightColorHex = normalizeHexColor(patch.lightColor, lightColorHex);
    lightColorRgb = hexToRgb01(lightColorHex);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'nightSkyColor')) {
    nightSkyColorHex = normalizeHexColor(patch.nightSkyColor, nightSkyColorHex);
    nightSkyColorRgb = hexToRgb01(nightSkyColorHex);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'daySkyZenithColor')) {
    daySkyZenithColorHex = normalizeHexColor(patch.daySkyZenithColor, daySkyZenithColorHex);
    daySkyZenithColorRgb = hexToRgb01(daySkyZenithColorHex);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'daySkyHorizonColor')) {
    daySkyHorizonColorHex = normalizeHexColor(patch.daySkyHorizonColor, daySkyHorizonColorHex);
    daySkyHorizonColorRgb = hexToRgb01(daySkyHorizonColorHex);
  }

  if (Object.prototype.hasOwnProperty.call(patch, 'sunDiskIntensity')) {
    sunDiskIntensity = clamp(Number(patch.sunDiskIntensity) || sunDiskIntensity, 0, 5);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'sunGlowIntensity')) {
    sunGlowIntensity = clamp(Number(patch.sunGlowIntensity) || sunGlowIntensity, 0, 5);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'celestialDistance')) {
    celestialDistance = clamp(Number(patch.celestialDistance) || celestialDistance, 10, 500);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'celestialSize')) {
    celestialSize = clamp(Number(patch.celestialSize) || celestialSize, 0.1, 50);
  }

  if (Object.prototype.hasOwnProperty.call(patch, 'godrays')) godraysEnabled = Boolean(patch.godrays);
  if (Object.prototype.hasOwnProperty.call(patch, 'godraysDuringDrag')) {
    godraysDuringDrag = Boolean(patch.godraysDuringDrag);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'godraysSamples')) {
    godraysSamples = clamp(Math.round(Number(patch.godraysSamples) || godraysSamples), 4, 128);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'godraysDensity')) {
    godraysDensity = clamp(Number(patch.godraysDensity) || godraysDensity, 0, 2);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'godraysDecay')) {
    godraysDecay = clamp(Number(patch.godraysDecay) || godraysDecay, 0.8, 1);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'godraysWeight')) {
    godraysWeight = clamp(Number(patch.godraysWeight) || godraysWeight, 0, 1);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'godraysIntensity')) {
    godraysIntensity = clamp(Number(patch.godraysIntensity) || godraysIntensity, 0, 5);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'godraysRadiusScale')) {
    godraysRadiusScale = clamp(Number(patch.godraysRadiusScale) || godraysRadiusScale, 0.25, 4);
  }

  if (Object.prototype.hasOwnProperty.call(patch, 'shapeSpeed')) {
    shapeSpeed = clamp(Number(patch.shapeSpeed) || shapeSpeed, -50, 50);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'detailSpeed')) {
    detailSpeed = clamp(Number(patch.detailSpeed) || detailSpeed, -50, 50);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'densityMultiplier')) {
    densityMultiplier = clamp(Number(patch.densityMultiplier) || densityMultiplier, 0, 1);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'shapeStrength')) {
    shapeStrength = clamp(Number(patch.shapeStrength) || shapeStrength, 0, 2);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'detailStrength')) {
    detailStrength = clamp(Number(patch.detailStrength) || detailStrength, 0, 2);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'noiseSeed')) {
    noiseSeed = clamp(Number(patch.noiseSeed) || noiseSeed, -1000, 1000);
  }

  if (Object.prototype.hasOwnProperty.call(patch, 'cameraMode')) {
    const nextMode = patch.cameraMode === 'jet' ? 'jet' : patch.cameraMode === 'fly' ? 'fly' : 'orbit';
    cameraMode = nextMode;

    const startYaw = Math.atan2(cameraTargetDirThisFrame[0], -cameraTargetDirThisFrame[2]);
    const startAy = clamp(cameraTargetDirThisFrame[1], -0.999, 0.999);
    if (cameraMode === "orbit") {
      state.mouseDown = false;
      if (document.pointerLockElement === canvas) {
        try {
          document.exitPointerLock();
        } catch {}
      }
      // Preserve the last view direction when switching back to orbit/look mode.
      if (prevCameraMode === "jet") {
        cameraAngles.x = jetAngles.x;
        cameraAngles.y = jetAngles.y;
      } else {
        cameraAngles.x = flightAngles.x;
        cameraAngles.y = flightAngles.y;
      }
      cameraAngles.prevDown = false;
    }
    if (cameraMode === "fly") {
      // Start free-flight from the current orbit camera placement/orientation.
      flightState.pos = [...cameraPosThisFrame];
      flightState.vel = [0, 0, 0];
      flightAngles.x = startYaw;
      flightAngles.y = startAy;
      flightAngles.roll = 0;
    }
    if (cameraMode === "jet") {
      jetState.pos = [...cameraPosThisFrame];
      jetState.speed = clamp(Math.max(jetMinSpeed, jetState.speed || jetMinSpeed), jetMinSpeed, jetMaxSpeed);
      jetAngles.x = startYaw;
      jetAngles.y = startAy;
      jetAngles.roll = 0;
      jetRates.yaw = 0;
      jetRates.pitch = 0;
      jetRates.roll = 0;
      jetCursor.x = 0;
      jetCursor.y = 0;
    }

    // Camera mode switches should reset history to avoid smearing/ghosting.
    if (prevCameraMode !== cameraMode) needsHistoryReset = true;
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'flightSpeed')) {
    flightSpeed = clamp(Number(patch.flightSpeed) || flightSpeed, 1, 500);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'flightBoost')) {
    flightBoost = clamp(Number(patch.flightBoost) || flightBoost, 1, 10);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'flightDamping')) {
    flightDamping = clamp(Number(patch.flightDamping) || flightDamping, 0, 10);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'flightBank')) {
    flightBank = Boolean(patch.flightBank);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'flightBankStrength')) {
    flightBankStrength = clamp(Number(patch.flightBankStrength) || flightBankStrength, 0, 2);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetThrottle')) {
    const v = Number(patch.jetThrottle);
    if (Number.isFinite(v)) jetThrottle = clamp(v, 0, 1);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetMinSpeed')) {
    const v = Number(patch.jetMinSpeed);
    if (Number.isFinite(v)) jetMinSpeed = clamp(v, 0, 500);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetMaxSpeed')) {
    const v = Number(patch.jetMaxSpeed);
    if (Number.isFinite(v)) jetMaxSpeed = clamp(v, 1, 2000);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetThrottleResponse')) {
    const v = Number(patch.jetThrottleResponse);
    if (Number.isFinite(v)) jetThrottleResponse = clamp(v, 0, 20);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetYawRate')) {
    const v = Number(patch.jetYawRate);
    if (Number.isFinite(v)) jetYawRate = clamp(v, 0, 20);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetPitchRate')) {
    const v = Number(patch.jetPitchRate);
    if (Number.isFinite(v)) jetPitchRate = clamp(v, 0, 20);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetRollRate')) {
    const v = Number(patch.jetRollRate);
    if (Number.isFinite(v)) jetRollRate = clamp(v, 0, 50);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetMouseAim')) {
    jetMouseAim = Boolean(patch.jetMouseAim);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetAutoBank')) {
    jetAutoBank = Boolean(patch.jetAutoBank);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetAutoBankStrength')) {
    const v = Number(patch.jetAutoBankStrength);
    if (Number.isFinite(v)) jetAutoBankStrength = clamp(v, 0, 3);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetCursorSensitivity')) {
    const v = Number(patch.jetCursorSensitivity);
    if (Number.isFinite(v)) jetCursorSensitivity = clamp(v, 0.05, 10);
  }
  if (Object.prototype.hasOwnProperty.call(patch, 'jetCursorMax')) {
    const v = Number(patch.jetCursorMax);
    if (Number.isFinite(v)) jetCursorMax = clamp(v, 0, 1);
  }

  if (markCustom && activePresetKey) markCustomPreset();

  const needResize = prevScale != renderScale || prevTaa != taaEnabled || prevGodraysEnabled !== godraysEnabled;
  const needRebuildImage = prevFast != fastMode || prevFastWhileDrag != fastWhileDrag;
  const needHistoryResetForParams =
    prevLightingMode !== lightingMode ||
    prevLightAzimuthDeg !== lightAzimuthDeg ||
    prevLightHeight !== lightHeight ||
    prevLightColorHex !== lightColorHex ||
    prevLightPower !== lightPower ||
    prevExposure !== exposure ||
    prevStars !== stars ||
    prevNightSkyHex !== nightSkyColorHex ||
    prevDayZenithHex !== daySkyZenithColorHex ||
    prevDayHorizonHex !== daySkyHorizonColorHex ||
    prevSunDisk !== sunDiskIntensity ||
    prevSunGlow !== sunGlowIntensity ||
    prevCelestialDist !== celestialDistance ||
    prevCelestialSize !== celestialSize;

  if (needResize) resizeRenderTargets();
  if (needRebuildImage) selectImagePass();
  if (prevTaa !== taaEnabled) needsHistoryReset = true;
  if (prevReproject !== taaReproject) needsHistoryReset = true;
  if (prevFovDeg !== fovDeg) needsHistoryReset = true;
  if (needHistoryResetForParams) needsHistoryReset = true;

  renderSettingsOverlay();
  syncControlsFromConfig();
}

function syncControlsFromConfig() {
  isSyncingUi = true;
  try {
    if (ui.presetSelect) ui.presetSelect.value = activePresetKey || '';
    if (ui.scaleRange) ui.scaleRange.value = String(renderScale);
    if (ui.scaleValue) ui.scaleValue.textContent = renderScale.toFixed(2);
    if (ui.timeScaleRange) ui.timeScaleRange.value = String(timeScale);
    if (ui.timeScaleValue) ui.timeScaleValue.textContent = timeScale.toFixed(2);
    if (ui.fastCheckbox) ui.fastCheckbox.checked = fastMode;
    if (ui.fastWhileDragCheckbox) ui.fastWhileDragCheckbox.checked = fastWhileDrag;

    if (ui.taaCheckbox) ui.taaCheckbox.checked = taaEnabled;
    if (ui.reprojectCheckbox) ui.reprojectCheckbox.checked = taaReproject;
    if (ui.accumWhileDragCheckbox) ui.accumWhileDragCheckbox.checked = taaDuringDrag;
    if (ui.alphaRange) ui.alphaRange.value = String(taaAlpha);
    if (ui.alphaValue) ui.alphaValue.textContent = taaAlpha.toFixed(3);
    if (ui.useDragAlphaCheckbox) ui.useDragAlphaCheckbox.checked = taaUseDragAlpha;
    if (ui.alphaDragRange) ui.alphaDragRange.value = String(taaAlphaDrag);
    if (ui.alphaDragValue) ui.alphaDragValue.textContent = taaAlphaDrag.toFixed(3);

    if (ui.lightingSelect) ui.lightingSelect.value = lightingMode;
    if (ui.lightAzRange) ui.lightAzRange.value = String(lightAzimuthDeg);
    if (ui.lightAzValue) ui.lightAzValue.textContent = lightAzimuthDeg.toFixed(0) + '°';
    if (ui.lightHeightRange) ui.lightHeightRange.value = String(lightHeight);
    if (ui.lightHeightValue) ui.lightHeightValue.textContent = lightHeight.toFixed(2);
    if (ui.lightColorInput) ui.lightColorInput.value = lightColorHex;
    if (ui.lightPowerRange) ui.lightPowerRange.value = String(lightPower);
    if (ui.lightPowerValue) ui.lightPowerValue.textContent = lightPower.toFixed(0);
    if (ui.exposureRange) ui.exposureRange.value = String(exposure);
    if (ui.exposureValue) ui.exposureValue.textContent = exposure.toFixed(2);
    if (ui.starsRange) ui.starsRange.value = String(stars);
    if (ui.starsValue) ui.starsValue.textContent = stars.toFixed(2);
    if (ui.nightSkyColorInput) ui.nightSkyColorInput.value = nightSkyColorHex;
    if (ui.daySkyZenithColorInput) ui.daySkyZenithColorInput.value = daySkyZenithColorHex;
    if (ui.daySkyHorizonColorInput) ui.daySkyHorizonColorInput.value = daySkyHorizonColorHex;
    if (ui.sunDiskRange) ui.sunDiskRange.value = String(sunDiskIntensity);
    if (ui.sunDiskValue) ui.sunDiskValue.textContent = sunDiskIntensity.toFixed(2);
    if (ui.sunGlowRange) ui.sunGlowRange.value = String(sunGlowIntensity);
    if (ui.sunGlowValue) ui.sunGlowValue.textContent = sunGlowIntensity.toFixed(2);
    if (ui.celestialDistRange) ui.celestialDistRange.value = String(celestialDistance);
    if (ui.celestialDistValue) ui.celestialDistValue.textContent = celestialDistance.toFixed(0);
    if (ui.celestialSizeRange) ui.celestialSizeRange.value = String(celestialSize);
    if (ui.celestialSizeValue) ui.celestialSizeValue.textContent = celestialSize.toFixed(2);

    if (ui.shapeSpeedRange) ui.shapeSpeedRange.value = String(shapeSpeed);
    if (ui.shapeSpeedValue) ui.shapeSpeedValue.textContent = shapeSpeed.toFixed(2);
    if (ui.detailSpeedRange) ui.detailSpeedRange.value = String(detailSpeed);
    if (ui.detailSpeedValue) ui.detailSpeedValue.textContent = detailSpeed.toFixed(2);
    if (ui.densityMulRange) ui.densityMulRange.value = String(densityMultiplier);
    if (ui.densityMulValue) ui.densityMulValue.textContent = densityMultiplier.toFixed(3);
    if (ui.shapeStrengthRange) ui.shapeStrengthRange.value = String(shapeStrength);
    if (ui.shapeStrengthValue) ui.shapeStrengthValue.textContent = shapeStrength.toFixed(3);
    if (ui.detailStrengthRange) ui.detailStrengthRange.value = String(detailStrength);
    if (ui.detailStrengthValue) ui.detailStrengthValue.textContent = detailStrength.toFixed(3);
    if (ui.noiseSeedRange) ui.noiseSeedRange.value = String(noiseSeed);
    if (ui.noiseSeedValue) ui.noiseSeedValue.textContent = noiseSeed.toFixed(1);

    if (ui.cameraModeSelect) ui.cameraModeSelect.value = cameraMode;
    if (ui.fovRange) ui.fovRange.value = String(fovDeg);
    if (ui.fovValue) ui.fovValue.textContent = fovDeg.toFixed(0);
    if (ui.flightSpeedRange) ui.flightSpeedRange.value = String(flightSpeed);
    if (ui.flightSpeedValue) ui.flightSpeedValue.textContent = flightSpeed.toFixed(1);
    if (ui.flightBoostRange) ui.flightBoostRange.value = String(flightBoost);
    if (ui.flightBoostValue) ui.flightBoostValue.textContent = flightBoost.toFixed(2);
    if (ui.flightDampingRange) ui.flightDampingRange.value = String(flightDamping);
    if (ui.flightDampingValue) ui.flightDampingValue.textContent = flightDamping.toFixed(2);
    if (ui.flightBankCheckbox) ui.flightBankCheckbox.checked = flightBank;
    if (ui.flightBankStrengthRange) ui.flightBankStrengthRange.value = String(flightBankStrength);
    if (ui.flightBankStrengthValue) ui.flightBankStrengthValue.textContent = flightBankStrength.toFixed(2);

    if (ui.jetThrottleRange) ui.jetThrottleRange.value = String(jetThrottle);
    if (ui.jetThrottleValue) ui.jetThrottleValue.textContent = jetThrottle.toFixed(2);
    if (ui.jetMinSpeedRange) ui.jetMinSpeedRange.value = String(jetMinSpeed);
    if (ui.jetMinSpeedValue) ui.jetMinSpeedValue.textContent = jetMinSpeed.toFixed(0);
    if (ui.jetMaxSpeedRange) ui.jetMaxSpeedRange.value = String(jetMaxSpeed);
    if (ui.jetMaxSpeedValue) ui.jetMaxSpeedValue.textContent = jetMaxSpeed.toFixed(0);
    if (ui.jetThrottleResponseRange) ui.jetThrottleResponseRange.value = String(jetThrottleResponse);
    if (ui.jetThrottleResponseValue) ui.jetThrottleResponseValue.textContent = jetThrottleResponse.toFixed(2);
    if (ui.jetYawRateRange) ui.jetYawRateRange.value = String(jetYawRate);
    if (ui.jetYawRateValue) ui.jetYawRateValue.textContent = jetYawRate.toFixed(2);
    if (ui.jetPitchRateRange) ui.jetPitchRateRange.value = String(jetPitchRate);
    if (ui.jetPitchRateValue) ui.jetPitchRateValue.textContent = jetPitchRate.toFixed(2);
    if (ui.jetRollRateRange) ui.jetRollRateRange.value = String(jetRollRate);
    if (ui.jetRollRateValue) ui.jetRollRateValue.textContent = jetRollRate.toFixed(2);
    if (ui.jetMouseAimCheckbox) ui.jetMouseAimCheckbox.checked = jetMouseAim;
    if (ui.jetAutoBankCheckbox) ui.jetAutoBankCheckbox.checked = jetAutoBank;
    if (ui.jetAutoBankStrengthRange) ui.jetAutoBankStrengthRange.value = String(jetAutoBankStrength);
    if (ui.jetAutoBankStrengthValue) ui.jetAutoBankStrengthValue.textContent = jetAutoBankStrength.toFixed(2);
    if (ui.jetCursorSensitivityRange) ui.jetCursorSensitivityRange.value = String(jetCursorSensitivity);
    if (ui.jetCursorSensitivityValue) ui.jetCursorSensitivityValue.textContent = jetCursorSensitivity.toFixed(2);
    if (ui.jetCursorMaxRange) ui.jetCursorMaxRange.value = String(jetCursorMax);
    if (ui.jetCursorMaxValue) ui.jetCursorMaxValue.textContent = jetCursorMax.toFixed(2);

    if (ui.godraysCheckbox) ui.godraysCheckbox.checked = godraysEnabled;
    if (ui.godraysDuringDragCheckbox) ui.godraysDuringDragCheckbox.checked = godraysDuringDrag;
    if (ui.godraysSamplesRange) ui.godraysSamplesRange.value = String(godraysSamples);
    if (ui.godraysSamplesValue) ui.godraysSamplesValue.textContent = godraysSamples.toFixed(0);
    if (ui.godraysDensityRange) ui.godraysDensityRange.value = String(godraysDensity);
    if (ui.godraysDensityValue) ui.godraysDensityValue.textContent = godraysDensity.toFixed(3);
    if (ui.godraysDecayRange) ui.godraysDecayRange.value = String(godraysDecay);
    if (ui.godraysDecayValue) ui.godraysDecayValue.textContent = godraysDecay.toFixed(3);
    if (ui.godraysWeightRange) ui.godraysWeightRange.value = String(godraysWeight);
    if (ui.godraysWeightValue) ui.godraysWeightValue.textContent = godraysWeight.toFixed(3);
    if (ui.godraysIntensityRange) ui.godraysIntensityRange.value = String(godraysIntensity);
    if (ui.godraysIntensityValue) ui.godraysIntensityValue.textContent = godraysIntensity.toFixed(3);
    if (ui.godraysRadiusRange) ui.godraysRadiusRange.value = String(godraysRadiusScale);
    if (ui.godraysRadiusValue) ui.godraysRadiusValue.textContent = godraysRadiusScale.toFixed(3);

    if (ui.shareUrlInput) ui.shareUrlInput.value = buildShareUrl();
  } finally {
    isSyncingUi = false;
  }
}

function initControls() {
  if (!tabBarEl || !tabPanelsEl) return;
  tabBarEl.textContent = '';
  tabPanelsEl.textContent = '';

  const renderPanel = createTab('render', 'Render', 'R', { active: true });
  const temporalPanel = createTab('temporal', 'Temporal', 'T');
  const lightingPanel = createTab('lighting', 'Lighting', 'L');
  const cloudsPanel = createTab('clouds', 'Clouds', 'C');
  const flightPanel = createTab('flight', 'Flight', 'F');
  const godraysPanel = createTab('godrays', 'Godrays', 'G');
  const sharePanel = createTab('share', 'Share', 'S');
  const statusPanel = createTab('status', 'Status', 'I');

  if (statusPanel) {
    settingsEl = document.createElement('div');
    settingsEl.id = 'settings';
    errorEl = document.createElement('div');
    errorEl.id = 'error';

    const summary = createSection(statusPanel, 'Summary', 'Live state (fps, preset, toggles).', { open: true });
    summary.append(settingsEl);
    const errors = createSection(statusPanel, 'Errors', 'Shader compilation / runtime errors.', { open: false });
    errors.append(errorEl);
  }

  if (renderPanel) {
    const presetSection = createSection(renderPanel, 'Presets', 'Quick starting points.', { open: true });
    ui.presetSelect = addSelect(presetSection, 'Preset', [
      { label: '(custom)', value: '' },
      { label: 'fast-crisp', value: 'fast-crisp' },
      { label: 'smooth', value: 'smooth' },
    ], 'preset', (val) => {
      if (!val) {
        markCustomPreset();
        renderSettingsOverlay();
        syncControlsFromConfig();
      } else {
        applyPreset(val);
      }
    });

    const scaleSection = createSection(renderPanel, 'Resolution & time', 'Controls that most affect performance.', { open: true });
    const scaleCtrl = addSlider(scaleSection, 'Render scale', 'scale', { min: 0.2, max: 1, step: 0.01, format: (v) => v.toFixed(2) });
    ui.scaleRange = scaleCtrl.input;
    ui.scaleValue = scaleCtrl.valueEl;
    const timeCtrl = addSlider(scaleSection, 'Time scale', 'timeScale', { min: 0.05, max: 5, step: 0.01, format: (v) => v.toFixed(2) });
    ui.timeScaleRange = timeCtrl.input;
    ui.timeScaleValue = timeCtrl.valueEl;

    const perfSection = createSection(renderPanel, 'Performance', 'Optional quality cuts while interacting.', { open: false });
    ui.fastCheckbox = addCheckbox(perfSection, 'Fast shader mode', 'fast');
    ui.fastWhileDragCheckbox = addCheckbox(perfSection, 'Use fast mode while dragging/moving', 'fastWhileDrag');
  }

  if (temporalPanel) {
    const toggles = createSection(temporalPanel, 'TAA', 'Temporal accumulation reduces dithering grain.', { open: true });
    ui.taaCheckbox = addCheckbox(toggles, 'Enable TAA', 'taa');
    ui.accumWhileDragCheckbox = addCheckbox(toggles, 'Accumulate while dragging/moving (requires reprojection)', 'taaDuringDrag');
    ui.reprojectCheckbox = addCheckbox(toggles, 'Use reprojection (orbit only)', 'reproject');

    const blend = createSection(temporalPanel, 'Blend', 'Higher alpha = more responsive; lower alpha = smoother.', { open: true });
    const alphaCtrl = addSlider(blend, 'TAA alpha (still)', 'taaAlpha', { min: 0.02, max: 0.5, step: 0.005, format: (v) => v.toFixed(3) });
    ui.alphaRange = alphaCtrl.input;
    ui.alphaValue = alphaCtrl.valueEl;
    ui.useDragAlphaCheckbox = addCheckbox(blend, 'Use higher alpha while dragging/moving', 'taaUseDragAlpha');
    const alphaDragCtrl = addSlider(blend, 'TAA alpha (move)', 'taaAlphaDrag', { min: 0.02, max: 0.5, step: 0.005, format: (v) => v.toFixed(3) });
    ui.alphaDragRange = alphaDragCtrl.input;
    ui.alphaDragValue = alphaDragCtrl.valueEl;

    const tools = createSection(temporalPanel, 'Tools', null, { open: false });
    ui.resetHistoryBtn = document.createElement('button');
    ui.resetHistoryBtn.type = 'button';
    ui.resetHistoryBtn.textContent = 'Reset history';
    ui.resetHistoryBtn.addEventListener('click', () => {
      needsHistoryReset = true;
    });
    tools.append(createControlRow('History', ui.resetHistoryBtn));
  }

  if (lightingPanel) {
    const modeSection = createSection(lightingPanel, 'Mode & light', 'Day/night and sun/moon direction.', { open: true });
    ui.lightingSelect = addSelect(modeSection, 'Mode', [
      { label: 'Night (moon)', value: 'night' },
      { label: 'Day (sun)', value: 'day' },
    ], 'lighting', (val) => applyLightingPreset(val));
    const azCtrl = addSlider(modeSection, 'Azimuth', 'lightAzimuthDeg', { min: 0, max: 360, step: 1, format: (v) => v.toFixed(0) + '?' });
    ui.lightAzRange = azCtrl.input;
    ui.lightAzValue = azCtrl.valueEl;
    const elCtrl = addSlider(modeSection, 'Elevation', 'lightHeight', { min: -1, max: 1, step: 0.01 });
    ui.lightHeightRange = elCtrl.input;
    ui.lightHeightValue = elCtrl.valueEl;
    ui.lightColorInput = addColor(modeSection, 'Light color', 'lightColor');
    const powerCtrl = addSlider(modeSection, 'Light power', 'lightPower', { min: 0, max: 400, step: 1, format: (v) => v.toFixed(0) });
    ui.lightPowerRange = powerCtrl.input;
    ui.lightPowerValue = powerCtrl.valueEl;

    const skySection = createSection(lightingPanel, 'Sky', 'Exposure + starfield and sky gradients.', { open: true });
    const exposureCtrl = addSlider(skySection, 'Exposure', 'exposure', { min: 0, max: 2, step: 0.01 });
    ui.exposureRange = exposureCtrl.input;
    ui.exposureValue = exposureCtrl.valueEl;
    const starCtrl = addSlider(skySection, 'Stars', 'stars', { min: 0, max: 1, step: 0.01 });
    ui.starsRange = starCtrl.input;
    ui.starsValue = starCtrl.valueEl;
    ui.nightSkyColorInput = addColor(skySection, 'Night sky base', 'nightSkyColor');
    ui.daySkyZenithColorInput = addColor(skySection, 'Day sky zenith', 'daySkyZenithColor');
    ui.daySkyHorizonColorInput = addColor(skySection, 'Day sky horizon', 'daySkyHorizonColor');

    const celSection = createSection(lightingPanel, 'Celestial', 'Sun/moon disk/glow and apparent size.', { open: false });
    const sunDiskCtrl = addSlider(celSection, 'Sun/moon disk', 'sunDiskIntensity', { min: 0, max: 5, step: 0.01 });
    ui.sunDiskRange = sunDiskCtrl.input;
    ui.sunDiskValue = sunDiskCtrl.valueEl;
    const sunGlowCtrl = addSlider(celSection, 'Sun/moon glow', 'sunGlowIntensity', { min: 0, max: 5, step: 0.01 });
    ui.sunGlowRange = sunGlowCtrl.input;
    ui.sunGlowValue = sunGlowCtrl.valueEl;
    const celDistCtrl = addSlider(celSection, 'Celestial distance', 'celestialDistance', { min: 10, max: 500, step: 1, format: (v) => v.toFixed(0) });
    ui.celestialDistRange = celDistCtrl.input;
    ui.celestialDistValue = celDistCtrl.valueEl;
    const celSizeCtrl = addSlider(celSection, 'Celestial size', 'celestialSize', { min: 0.1, max: 50, step: 0.1 });
    ui.celestialSizeRange = celSizeCtrl.input;
    ui.celestialSizeValue = celSizeCtrl.valueEl;
  }

  if (cloudsPanel) {
    const animSection = createSection(cloudsPanel, 'Animation', 'Scroll speeds for the shape/detail fields.', { open: true });
    const shapeCtrl = addSlider(animSection, 'Shape scroll speed', 'shapeSpeed', { min: -50, max: 50, step: 0.1 });
    ui.shapeSpeedRange = shapeCtrl.input;
    ui.shapeSpeedValue = shapeCtrl.valueEl;
    const detailCtrl = addSlider(animSection, 'Detail scroll speed', 'detailSpeed', { min: -50, max: 50, step: 0.1 });
    ui.detailSpeedRange = detailCtrl.input;
    ui.detailSpeedValue = detailCtrl.valueEl;

    const carveSection = createSection(cloudsPanel, 'Density & carving', 'Overall density and how aggressively noise cuts the volume.', { open: true });
    const densityCtrl = addSlider(carveSection, 'Density multiplier', 'densityMultiplier', { min: 0, max: 1, step: 0.001, format: (v) => v.toFixed(3) });
    ui.densityMulRange = densityCtrl.input;
    ui.densityMulValue = densityCtrl.valueEl;
    const shapeStrengthCtrl = addSlider(carveSection, 'Shape strength', 'shapeStrength', { min: 0, max: 2, step: 0.01, format: (v) => v.toFixed(3) });
    ui.shapeStrengthRange = shapeStrengthCtrl.input;
    ui.shapeStrengthValue = shapeStrengthCtrl.valueEl;
    const detailStrengthCtrl = addSlider(carveSection, 'Detail strength', 'detailStrength', { min: 0, max: 2, step: 0.01, format: (v) => v.toFixed(3) });
    ui.detailStrengthRange = detailStrengthCtrl.input;
    ui.detailStrengthValue = detailStrengthCtrl.valueEl;

    const seedSection = createSection(cloudsPanel, 'Seed', 'Offsets noise sampling (useful for testing variety).', { open: false });
    const seedCtrl = addSlider(seedSection, 'Noise seed', 'noiseSeed', { min: -1000, max: 1000, step: 1, format: (v) => v.toFixed(0) });
    ui.noiseSeedRange = seedCtrl.input;
    ui.noiseSeedValue = seedCtrl.valueEl;
  }

  if (flightPanel) {
    const modeSection = createSection(flightPanel, 'Camera', 'Orbit vs free-flight.', { open: true });
    ui.cameraModeSelect = addSelect(modeSection, 'Mode', [
      { label: 'Orbit', value: 'orbit' },
      { label: 'Free flight', value: 'fly' },
      { label: 'Jet', value: 'jet' },
    ], 'cameraMode');
    const fovCtrl = addSlider(modeSection, 'FOV (deg)', 'fovDeg', { min: 20, max: 110, step: 1, format: (v) => v.toFixed(0) });
    ui.fovRange = fovCtrl.input;
    ui.fovValue = fovCtrl.valueEl;

    const flightSection = createSection(flightPanel, 'Flight physics', 'Velocity smoothing + optional banking.', { open: true });
    const speedCtrl = addSlider(flightSection, 'Cruise speed', 'flightSpeed', { min: 1, max: 500, step: 1, format: (v) => v.toFixed(0) });
    ui.flightSpeedRange = speedCtrl.input;
    ui.flightSpeedValue = speedCtrl.valueEl;
    const boostCtrl = addSlider(flightSection, 'Boost multiplier', 'flightBoost', { min: 1, max: 10, step: 0.05 });
    ui.flightBoostRange = boostCtrl.input;
    ui.flightBoostValue = boostCtrl.valueEl;
    const dampCtrl = addSlider(flightSection, 'Damping', 'flightDamping', { min: 0, max: 10, step: 0.05 });
    ui.flightDampingRange = dampCtrl.input;
    ui.flightDampingValue = dampCtrl.valueEl;
    ui.flightBankCheckbox = addCheckbox(flightSection, 'Bank while turning', 'flightBank');
    const bankCtrl = addSlider(flightSection, 'Bank strength', 'flightBankStrength', { min: 0, max: 2, step: 0.05 });
    ui.flightBankStrengthRange = bankCtrl.input;
    ui.flightBankStrengthValue = bankCtrl.valueEl;

    const jetSection = createSection(flightPanel, 'Jet flight', 'Mouse-aim + throttle (Warthunder-style).', { open: true });
    const jetThrottleCtrl = addSlider(jetSection, 'Throttle', 'jetThrottle', { min: 0, max: 1, step: 0.01, format: (v) => v.toFixed(2) });
    ui.jetThrottleRange = jetThrottleCtrl.input;
    ui.jetThrottleValue = jetThrottleCtrl.valueEl;
    const jetMinCtrl = addSlider(jetSection, 'Min speed', 'jetMinSpeed', { min: 0, max: 500, step: 1, format: (v) => v.toFixed(0) });
    ui.jetMinSpeedRange = jetMinCtrl.input;
    ui.jetMinSpeedValue = jetMinCtrl.valueEl;
    const jetMaxCtrl = addSlider(jetSection, 'Max speed', 'jetMaxSpeed', { min: 1, max: 2000, step: 1, format: (v) => v.toFixed(0) });
    ui.jetMaxSpeedRange = jetMaxCtrl.input;
    ui.jetMaxSpeedValue = jetMaxCtrl.valueEl;
    const jetRespCtrl = addSlider(jetSection, 'Throttle response', 'jetThrottleResponse', { min: 0, max: 20, step: 0.05, format: (v) => v.toFixed(2) });
    ui.jetThrottleResponseRange = jetRespCtrl.input;
    ui.jetThrottleResponseValue = jetRespCtrl.valueEl;
    const jetYawCtrl = addSlider(jetSection, 'Yaw rate', 'jetYawRate', { min: 0, max: 20, step: 0.05, format: (v) => v.toFixed(2) });
    ui.jetYawRateRange = jetYawCtrl.input;
    ui.jetYawRateValue = jetYawCtrl.valueEl;
    const jetPitchCtrl = addSlider(jetSection, 'Pitch rate', 'jetPitchRate', { min: 0, max: 20, step: 0.05, format: (v) => v.toFixed(2) });
    ui.jetPitchRateRange = jetPitchCtrl.input;
    ui.jetPitchRateValue = jetPitchCtrl.valueEl;
    const jetRollCtrl = addSlider(jetSection, 'Roll rate', 'jetRollRate', { min: 0, max: 50, step: 0.05, format: (v) => v.toFixed(2) });
    ui.jetRollRateRange = jetRollCtrl.input;
    ui.jetRollRateValue = jetRollCtrl.valueEl;
    ui.jetMouseAimCheckbox = addCheckbox(jetSection, 'Mouse aim (M toggles)', 'jetMouseAim');
    ui.jetAutoBankCheckbox = addCheckbox(jetSection, 'Auto bank', 'jetAutoBank');
    const jetBankCtrl = addSlider(jetSection, 'Auto bank strength', 'jetAutoBankStrength', { min: 0, max: 3, step: 0.05, format: (v) => v.toFixed(2) });
    ui.jetAutoBankStrengthRange = jetBankCtrl.input;
    ui.jetAutoBankStrengthValue = jetBankCtrl.valueEl;
    const jetCursorSensCtrl = addSlider(jetSection, 'Cursor sensitivity', 'jetCursorSensitivity', { min: 0.05, max: 10, step: 0.05, format: (v) => v.toFixed(2) });
    ui.jetCursorSensitivityRange = jetCursorSensCtrl.input;
    ui.jetCursorSensitivityValue = jetCursorSensCtrl.valueEl;
    const jetCursorMaxCtrl = addSlider(jetSection, 'Cursor max', 'jetCursorMax', { min: 0, max: 1, step: 0.01, format: (v) => v.toFixed(2) });
    ui.jetCursorMaxRange = jetCursorMaxCtrl.input;
    ui.jetCursorMaxValue = jetCursorMaxCtrl.valueEl;

    const controlsSection = createSection(flightPanel, 'Controls', null, { open: true });
    const controlsHint = document.createElement('div');
    controlsHint.className = 'controlHint';
    controlsHint.style.whiteSpace = 'pre-wrap';
    controlsHint.textContent =
      'Controls (Orbit):\\n' +
      '- Click-drag canvas: rotate\\n' +
      '- Mouse wheel: FOV zoom\\n\\n' +
      'Controls (Free flight):\\n' +
      '- Click canvas: lock mouse (Esc to unlock)\\n' +
      '- Mouse: look\\n' +
      '- Mouse wheel: FOV zoom\\n' +
      '- W/S: forward/back\\n' +
      '- A/D: strafe left/right\\n' +
      '- Q/E: down/up\\n' +
      '- Shift: boost\\n\\n' +
      'Controls (Jet):\\n' +
      '- Click canvas: lock mouse (Esc to unlock)\\n' +
      '- Mouse: aim (virtual cursor)\\n' +
      '- Wheel (locked): throttle\\n' +
      '- W/S: throttle\\n' +
      '- A/D: roll\\n' +
      '- Q/E: rudder\\n' +
      '- ArrowUp/ArrowDown: pitch\\n' +
      '- M: toggle mouse aim\\n' +
      '- C: recenter aim + level wings\\n' +
      '- Shift: afterburner (uses Boost multiplier)';
    controlsSection.append(controlsHint);
  }

  if (godraysPanel) {
    const section = createSection(godraysPanel, 'God rays', 'Screen-space radial blur from light source.');
    ui.godraysCheckbox = addCheckbox(section, 'Enable god rays', 'godrays');
    ui.godraysDuringDragCheckbox = addCheckbox(section, 'Keep while dragging', 'godraysDuringDrag');
    const samplesCtrl = addSlider(section, 'Samples', 'godraysSamples', { min: 4, max: 128, step: 1, format: (v) => v.toFixed(0) });
    ui.godraysSamplesRange = samplesCtrl.input;
    ui.godraysSamplesValue = samplesCtrl.valueEl;
    const densityCtrl = addSlider(section, 'Density', 'godraysDensity', { min: 0, max: 2, step: 0.001, format: (v) => v.toFixed(3) });
    ui.godraysDensityRange = densityCtrl.input;
    ui.godraysDensityValue = densityCtrl.valueEl;
    const decayCtrl = addSlider(section, 'Decay', 'godraysDecay', { min: 0.8, max: 1, step: 0.001, format: (v) => v.toFixed(3) });
    ui.godraysDecayRange = decayCtrl.input;
    ui.godraysDecayValue = decayCtrl.valueEl;
    const weightCtrl = addSlider(section, 'Weight', 'godraysWeight', { min: 0, max: 1, step: 0.001, format: (v) => v.toFixed(3) });
    ui.godraysWeightRange = weightCtrl.input;
    ui.godraysWeightValue = weightCtrl.valueEl;
    const intensityCtrl = addSlider(section, 'Intensity', 'godraysIntensity', { min: 0, max: 5, step: 0.01, format: (v) => v.toFixed(2) });
    ui.godraysIntensityRange = intensityCtrl.input;
    ui.godraysIntensityValue = intensityCtrl.valueEl;
    const radiusCtrl = addSlider(section, 'Source radius scale', 'godraysRadiusScale', { min: 0.25, max: 4, step: 0.01, format: (v) => v.toFixed(2) });
    ui.godraysRadiusRange = radiusCtrl.input;
    ui.godraysRadiusValue = radiusCtrl.valueEl;
  }

  if (sharePanel) {
    const section = createSection(sharePanel, 'Share URL', 'Copyable link with current settings.');
    ui.shareUrlInput = document.createElement('input');
    ui.shareUrlInput.type = 'text';
    ui.shareUrlInput.readOnly = true;
    ui.shareUrlInput.style.width = '100%';
    ui.copyUrlBtn = document.createElement('button');
    ui.copyUrlBtn.type = 'button';
    ui.copyUrlBtn.textContent = 'Copy';
    ui.copyUrlBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(ui.shareUrlInput.value);
        ui.copyUrlBtn.textContent = 'Copied!';
        setTimeout(() => (ui.copyUrlBtn.textContent = 'Copy'), 1200);
      } catch (err) {
        console.error('Clipboard copy failed', err);
      }
    });
    section.append(createControlRow('URL', ui.shareUrlInput, ui.copyUrlBtn));
  }

  if (collapseBtn && overlayBodyEl) {
    collapseBtn.addEventListener('click', () => {
      const isHidden = overlayBodyEl.style.display === 'none';
      overlayBodyEl.style.display = isHidden ? 'grid' : 'none';
      collapseBtn.textContent = isHidden ? '[]' : 'x';
    });
  }

  renderSettingsOverlay();
  syncControlsFromConfig();
}

function setCommonUniforms(pass, time, frame) {
  gl.uniform3f(pass.uniforms.iResolution, rtWidth, rtHeight, 1);
  gl.uniform1f(pass.uniforms.iTime, time);
  if (pass.uniforms.iTimeDelta) gl.uniform1f(pass.uniforms.iTimeDelta, simTimeDelta);
  if (pass.uniforms.iFrameRate) gl.uniform1f(pass.uniforms.iFrameRate, simFrameRate);
  gl.uniform1i(pass.uniforms.iFrame, frame);

  const mx = state.mouseX;
  const my = state.mouseY;
  // This shader only needs a stable "mouse is down" boolean (`iMouse.z > 0`), not click coordinates.
  const down = state.mouseDown ? 1 : 0;
  gl.uniform4f(pass.uniforms.iMouse, mx, my, down, down);
}

function setChannels(pass) {
  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, bufferA.readTex);
  gl.uniform1i(pass.uniforms.iChannel0, 0);

  gl.activeTexture(gl.TEXTURE1);
  gl.bindTexture(gl.TEXTURE_2D, bufferB.readTex);
  gl.uniform1i(pass.uniforms.iChannel1, 1);

  gl.activeTexture(gl.TEXTURE2);
  gl.bindTexture(gl.TEXTURE_2D, blueNoise);
  gl.uniform1i(pass.uniforms.iChannel2, 2);

  gl.activeTexture(gl.TEXTURE3);
  gl.bindTexture(gl.TEXTURE_2D, null);
  gl.uniform1i(pass.uniforms.iChannel3, 3);

  // iChannelResolution[0..3]
  gl.uniform3fv(
    pass.uniforms.iChannelResolution0,
    new Float32Array([
      1,
      4,
      1, // channel0 (BufferA)
      rtWidth,
      rtHeight,
      1, // channel1 (BufferB)
      1024,
      1024,
      1, // channel2 (blue noise)
      0,
      0,
      1, // channel3 (unused)
    ]),
  );
}

function setImageUniforms(pass) {
  const u = pass.imageUniforms;
  if (!u) return;

  const lightingModeInt = lightingMode === "day" ? 1 : 0;
  const lightAzimuthRad = (lightAzimuthDeg * Math.PI) / 180;

  if (u.uLightingMode) gl.uniform1i(u.uLightingMode, lightingModeInt);
  if (u.uLightAzimuth) gl.uniform1f(u.uLightAzimuth, lightAzimuthRad);
  if (u.uLightHeight) gl.uniform1f(u.uLightHeight, lightHeight);
  if (u.uLightColor) gl.uniform3f(u.uLightColor, lightColorRgb[0], lightColorRgb[1], lightColorRgb[2]);
  if (u.uLightPower) gl.uniform1f(u.uLightPower, lightPower);
  if (u.uExposure) gl.uniform1f(u.uExposure, exposure);
  if (u.uStars) gl.uniform1f(u.uStars, stars);

  if (u.uNightSkyColor) gl.uniform3f(u.uNightSkyColor, nightSkyColorRgb[0], nightSkyColorRgb[1], nightSkyColorRgb[2]);
  if (u.uDaySkyZenithColor) {
    gl.uniform3f(u.uDaySkyZenithColor, daySkyZenithColorRgb[0], daySkyZenithColorRgb[1], daySkyZenithColorRgb[2]);
  }
  if (u.uDaySkyHorizonColor) {
    gl.uniform3f(u.uDaySkyHorizonColor, daySkyHorizonColorRgb[0], daySkyHorizonColorRgb[1], daySkyHorizonColorRgb[2]);
  }

  if (u.uSunDiskIntensity) gl.uniform1f(u.uSunDiskIntensity, sunDiskIntensity);
  if (u.uSunGlowIntensity) gl.uniform1f(u.uSunGlowIntensity, sunGlowIntensity);
  if (u.uCelestialDistance) gl.uniform1f(u.uCelestialDistance, celestialDistance);
  if (u.uCelestialSize) gl.uniform1f(u.uCelestialSize, celestialSize);

  if (u.uHarnessCameraPos) gl.uniform3f(u.uHarnessCameraPos, cameraPosThisFrame[0], cameraPosThisFrame[1], cameraPosThisFrame[2]);
  if (u.uHarnessTargetDir) {
    gl.uniform3f(u.uHarnessTargetDir, cameraTargetDirThisFrame[0], cameraTargetDirThisFrame[1], cameraTargetDirThisFrame[2]);
  }
  if (u.uHarnessCameraUp) gl.uniform3f(u.uHarnessCameraUp, cameraUpThisFrame[0], cameraUpThisFrame[1], cameraUpThisFrame[2]);
  if (u.uHarnessFovDeg) gl.uniform1f(u.uHarnessFovDeg, fovDeg);
}

function renderPass(pass, targetFbo, viewportW, viewportH, time, frame) {
  gl.useProgram(pass.program);
  gl.bindVertexArray(vao);
  gl.bindFramebuffer(gl.FRAMEBUFFER, targetFbo);
  gl.viewport(0, 0, viewportW, viewportH);
  setCommonUniforms(pass, time, frame);
  setChannels(pass);
  setImageUniforms(pass);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.bindVertexArray(null);
}

function computeTargetDirFromAngles(ax, ay) {
  return [Math.sin(ax), ay, -Math.cos(ax)];
}

function dot3(a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function cross3(a, b) {
  return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
}

function normalize3(v) {
  const len = Math.hypot(v[0], v[1], v[2]);
  if (len <= 1e-8) return [0, 0, 0];
  return [v[0] / len, v[1] / len, v[2] / len];
}

function add3(a, b) {
  return [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
}

function scale3(v, s) {
  return [v[0] * s, v[1] * s, v[2] * s];
}

function rotateAroundAxis(v, axis, angleRad) {
  // Rodrigues' rotation formula
  const k = normalize3(axis);
  const cosA = Math.cos(angleRad);
  const sinA = Math.sin(angleRad);
  const vCos = scale3(v, cosA);
  const kxv = cross3(k, v);
  const kxvSin = scale3(kxv, sinA);
  const kDotV = dot3(k, v);
  const kTerm = scale3(k, kDotV * (1 - cosA));
  return add3(add3(vCos, kxvSin), kTerm);
}

function computeLightUv(targetDir, up) {
  if (rtWidth <= 0 || rtHeight <= 0) return null;

  const upN = normalize3(up);
  const zaxis = normalize3(targetDir);
  const xaxis = normalize3(cross3(zaxis, upN));
  const yaxis = cross3(xaxis, zaxis);

  const azimuthRad = (lightAzimuthDeg * Math.PI) / 180;
  const lightDirWorld = normalize3([Math.cos(azimuthRad), lightHeight, Math.sin(azimuthRad)]);

  // GLSL view matrix columns: xaxis, yaxis, -zaxis. Inverse is transpose.
  const camX = dot3(lightDirWorld, xaxis);
  const camY = dot3(lightDirWorld, yaxis);
  const camZ = dot3(lightDirWorld, [-zaxis[0], -zaxis[1], -zaxis[2]]);

  // In this convention, forward rays have negative z.
  if (camZ >= -1e-4) return null;

  const z = (0.5 * rtHeight) / Math.tan(((fovDeg * Math.PI) / 180) * 0.5);
  const k = (-z) / camZ;
  const px = camX * k + rtWidth / 2;
  const py = camY * k + rtHeight / 2;
  return [px / rtWidth, py / rtHeight];
}

function updateAnglesForFrame(frameIdx) {
  const prevAngles = { x: cameraAngles.x, y: cameraAngles.y };

  if (frameIdx < 5) {
    cameraAngles.x = 0.1;
    cameraAngles.y = 0.07;
    cameraAngles.prevMouseNormX = 0;
    cameraAngles.prevMouseNormY = 0;
  } else {
    const mx = rtWidth > 0 ? state.mouseX / rtWidth : 0;
    const my = rtHeight > 0 ? state.mouseY / rtHeight : 0;

    if (state.mouseDown && cameraAngles.prevDown) {
      const dx = mx - cameraAngles.prevMouseNormX;
      const dy = my - cameraAngles.prevMouseNormY;
      cameraAngles.x += 3.5 * dx;
      cameraAngles.y += 2.5 * dy;
    }

    cameraAngles.prevMouseNormX = mx;
    cameraAngles.prevMouseNormY = my;
  }

  cameraAngles.prevDown = state.mouseDown;
  cameraAngles.x = ((cameraAngles.x % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  cameraAngles.y = Math.max(-0.999, Math.min(0.999, cameraAngles.y));

  return {
    prevTargetDir: computeTargetDirFromAngles(prevAngles.x, prevAngles.y),
    curTargetDir: computeTargetDirFromAngles(cameraAngles.x, cameraAngles.y),
  };
}

function renderAccum(targetDirCur, targetDirPrev, resetHistory, alpha, useReprojection) {
  gl.useProgram(passAccum.program);
  gl.bindVertexArray(vao);
  gl.bindFramebuffer(gl.FRAMEBUFFER, history.writeFbo);
  gl.viewport(0, 0, rtWidth, rtHeight);

  gl.uniform2f(passAccum.uniforms.uResolution, rtWidth, rtHeight);
  gl.uniform1f(passAccum.uniforms.uAlpha, alpha);
  gl.uniform1i(passAccum.uniforms.uReset, resetHistory ? 1 : 0);
  gl.uniform1i(passAccum.uniforms.uUseReprojection, useReprojection ? 1 : 0);
  gl.uniform3f(passAccum.uniforms.uTargetDirCur, targetDirCur[0], targetDirCur[1], targetDirCur[2]);
  gl.uniform3f(passAccum.uniforms.uTargetDirPrev, targetDirPrev[0], targetDirPrev[1], targetDirPrev[2]);
  gl.uniform1f(passAccum.uniforms.uFovDeg, fovDeg);

  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, currentColorTex);
  gl.uniform1i(passAccum.uniforms.uCurrent, 0);

  gl.activeTexture(gl.TEXTURE1);
  gl.bindTexture(gl.TEXTURE_2D, history.readTex);
  gl.uniform1i(passAccum.uniforms.uHistory, 1);

  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.bindVertexArray(null);

  history.swap();
}

function renderBlit(tex) {
  gl.useProgram(passBlit.program);
  gl.bindVertexArray(vao);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.viewport(0, 0, rtWidth, rtHeight);
  gl.uniform2f(passBlit.uniforms.uResolution, rtWidth, rtHeight);
  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.uniform1i(passBlit.uniforms.uTex, 0);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.bindVertexArray(null);
}

function renderGodrays(sceneTex, lightUv) {
  if (!passGodrays) {
    renderBlit(sceneTex);
    return;
  }

  if (!lightUv) {
    renderBlit(sceneTex);
    return;
  }

  gl.useProgram(passGodrays.program);
  gl.bindVertexArray(vao);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.viewport(0, 0, rtWidth, rtHeight);

  gl.uniform2f(passGodrays.uniforms.uResolution, rtWidth, rtHeight);
  gl.uniform2f(passGodrays.uniforms.uLightUv, lightUv[0], lightUv[1]);
  gl.uniform3f(passGodrays.uniforms.uLightColor, lightColorRgb[0], lightColorRgb[1], lightColorRgb[2]);
  gl.uniform1f(passGodrays.uniforms.uIntensity, godraysIntensity);
  gl.uniform1f(passGodrays.uniforms.uDensity, godraysDensity);
  gl.uniform1f(passGodrays.uniforms.uDecay, godraysDecay);
  gl.uniform1f(passGodrays.uniforms.uWeight, godraysWeight);
  gl.uniform1i(passGodrays.uniforms.uSamples, godraysSamples);

  const theta = Math.atan(celestialSize / celestialDistance);
  const radiusUv = 0.5 * (Math.tan(theta) / Math.tan(((fovDeg * Math.PI) / 180) * 0.5));
  const sourceRadiusUv = Math.max(0.0005, radiusUv * godraysRadiusScale);
  gl.uniform1f(passGodrays.uniforms.uSourceRadius, sourceRadiusUv);

  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, sceneTex);
  gl.uniform1i(passGodrays.uniforms.uScene, 0);

  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.bindVertexArray(null);
}

let lastNow = performance.now();
let simTime = 0;
let simTimeDelta = 1 / 60;
let simFrameRate = 60;
let frame = 0;

function tick() {
  const now = performance.now();
  const rawDt = (now - lastNow) / 1000;
  lastNow = now;
  // Clamp to avoid huge jumps when the tab is backgrounded (stabilizes motion + reprojection).
  simTimeDelta = Math.max(0, Math.min(0.1, rawDt || 0));
  simFrameRate = simTimeDelta > 1e-6 ? 1 / simTimeDelta : simFrameRate;
  simTime += simTimeDelta * timeScale;
  const time = simTime;

  let curTargetDir;
  let prevTargetDir;
  let isInteracting = false;
  let useReprojectionThisFrame = false;

  if (cameraMode === "orbit") {
    ({ curTargetDir, prevTargetDir } = updateAnglesForFrame(frame));
    cameraPosThisFrame = [...orbitCameraPos];
    cameraTargetDirThisFrame = curTargetDir;
    cameraUpThisFrame = [0, 1, 0];
    isInteracting = state.mouseDown;
    useReprojectionThisFrame = taaReproject;
  } else {
    const dt = simTimeDelta;
    const lookDx = flyLookDx;
    const lookDy = flyLookDy;
    flyLookDx = 0;
    flyLookDy = 0;

    // Pointer-lock movement deltas are in CSS pixel space; normalizing by rtWidth/rtHeight makes
    // look sensitivity depend on renderScale/devicePixelRatio (unintuitive and can feel "crazy").
    const clientW = canvas.clientWidth || rtWidth || 1;
    const clientH = canvas.clientHeight || rtHeight || 1;
    const dxNorm = lookDx / clientW;
    const dyNorm = lookDy / clientH;

    const key = (k) => !!state.keys[k];

    if (cameraMode === "fly") {
      const yawDelta = 3.5 * dxNorm;
      const pitchDelta = 2.5 * (-dyNorm);

      if (isPointerLocked) {
        flightAngles.x += yawDelta;
        flightAngles.y += pitchDelta;
      }

      flightAngles.x = ((flightAngles.x % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
      flightAngles.y = Math.max(-0.999, Math.min(0.999, flightAngles.y));

      const forward = normalize3(computeTargetDirFromAngles(flightAngles.x, flightAngles.y));
      const worldUp = [0, 1, 0];

      let up = worldUp;
      let right = normalize3(cross3(forward, worldUp));
      if (Math.hypot(right[0], right[1], right[2]) < 1e-6) right = [1, 0, 0];
      let upNoRoll = normalize3(cross3(right, forward));

      // Bank (roll) while turning.
      if (flightBank) {
        const maxRoll = 0.9;
        const rollTarget = clamp(-yawDelta * 8.0 * flightBankStrength, -maxRoll, maxRoll);
        const k = 1 - Math.exp(-8.0 * dt);
        flightAngles.roll = flightAngles.roll + (rollTarget - flightAngles.roll) * k;
      } else {
        const k = 1 - Math.exp(-8.0 * dt);
        flightAngles.roll = flightAngles.roll + (0 - flightAngles.roll) * k;
      }

      if (Math.abs(flightAngles.roll) > 1e-4) {
        up = normalize3(rotateAroundAxis(upNoRoll, forward, flightAngles.roll));
      } else {
        up = upNoRoll;
      }
      right = normalize3(cross3(forward, up));
      up = normalize3(cross3(right, forward));

      const forwardInput = (key("w") ? 1 : 0) - (key("s") ? 1 : 0);
      const rightInput = (key("d") ? 1 : 0) - (key("a") ? 1 : 0);
      const upInput = (key("e") ? 1 : 0) - (key("q") ? 1 : 0);

      let moveDir = [0, 0, 0];
      if (forwardInput) moveDir = add3(moveDir, scale3(forward, forwardInput));
      if (rightInput) moveDir = add3(moveDir, scale3(right, rightInput));
      if (upInput) moveDir = add3(moveDir, scale3(worldUp, upInput));

      const moveMag = Math.hypot(moveDir[0], moveDir[1], moveDir[2]);
      if (moveMag > 1e-6) moveDir = scale3(moveDir, 1 / moveMag);

      const boost = key("shift") ? flightBoost : 1.0;
      const desiredVel = scale3(moveDir, flightSpeed * boost);

      const response = Math.max(0, flightDamping);
      const t = response > 0 ? 1 - Math.exp(-response * dt) : 0;
      flightState.vel = add3(scale3(flightState.vel, 1 - t), scale3(desiredVel, t));
      flightState.pos = add3(flightState.pos, scale3(flightState.vel, dt));

      cameraPosThisFrame = [...flightState.pos];
      cameraTargetDirThisFrame = forward;
      cameraUpThisFrame = up;

      curTargetDir = forward;
      prevTargetDir = forward;

      const speedNow = Math.hypot(flightState.vel[0], flightState.vel[1], flightState.vel[2]);
      const hasLookInput = isPointerLocked && (Math.abs(lookDx) + Math.abs(lookDy) > 0);
      const hasMoveInput = Math.abs(forwardInput) + Math.abs(rightInput) + Math.abs(upInput) > 0;
      isInteracting = hasLookInput || hasMoveInput || speedNow > 0.05;
      useReprojectionThisFrame = false;
    } else {
      // --------------------------------------------------------------------
      // Jet mode: throttle-driven forward flight + mouse-aim (virtual cursor)
      // --------------------------------------------------------------------

      if (isPointerLocked && jetMouseAim) {
        jetCursor.x = clamp(jetCursor.x + dxNorm * jetCursorSensitivity, -jetCursorMax, jetCursorMax);
        jetCursor.y = clamp(jetCursor.y + (-dyNorm) * jetCursorSensitivity, -jetCursorMax, jetCursorMax);
      }

      // Throttle: W/S trims continuously (wheel while locked also works).
      const throttleInput = (key("w") ? 1 : 0) - (key("s") ? 1 : 0);
      if (throttleInput) {
        jetThrottle = clamp(jetThrottle + throttleInput * dt * 0.6, 0, 1);
        if (!isSyncingUi && ui.jetThrottleRange) {
          ui.jetThrottleRange.value = String(jetThrottle);
          if (ui.jetThrottleValue) ui.jetThrottleValue.textContent = jetThrottle.toFixed(2);
        }
      }

      // Manual controls: A/D roll, Q/E rudder, ArrowUp/ArrowDown pitch.
      const manualRoll = (key("d") ? 1 : 0) - (key("a") ? 1 : 0);
      const manualYaw = (key("e") ? 1 : 0) - (key("q") ? 1 : 0);
      const manualPitch = (key("arrowdown") ? 1 : 0) - (key("arrowup") ? 1 : 0);

      // If mouse-aim is disabled, fall back to direct look (like free-flight, but without strafing).
      if (isPointerLocked && !jetMouseAim) {
        jetAngles.x += 3.5 * dxNorm;
        jetAngles.y += 2.5 * (-dyNorm);
      }

      // Keep yaw in [0, 2pi), and clamp the shadertoy "elevation" channel.
      jetAngles.x = ((jetAngles.x % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
      jetAngles.y = Math.max(-0.999, Math.min(0.999, jetAngles.y));

      const forward = normalize3(computeTargetDirFromAngles(jetAngles.x, jetAngles.y));
      const worldUp = [0, 1, 0];
      let right = normalize3(cross3(forward, worldUp));
      if (Math.hypot(right[0], right[1], right[2]) < 1e-6) right = [1, 0, 0];
      const upNoRoll = normalize3(cross3(right, forward));

      // Convert cursor offsets to a desired direction in world space (camera-space ray).
      let targetYaw = jetAngles.x;
      let targetAy = jetAngles.y;
      if (jetMouseAim) {
        const aspect = clientW / clientH;
        const halfTan = Math.tan(((fovDeg * Math.PI) / 180) * 0.5);
        const desired = normalize3(
          add3(
            forward,
            add3(scale3(right, jetCursor.x * halfTan * aspect), scale3(upNoRoll, jetCursor.y * halfTan)),
          ),
        );
        targetYaw = Math.atan2(desired[0], -desired[2]);
        targetAy = clamp(desired[1], -0.999, 0.999);
      }

      // Shortest yaw delta in [-pi, pi].
      const yawError = ((targetYaw - jetAngles.x + Math.PI) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) - Math.PI;
      const pitchError = targetAy - jetAngles.y;

      // Desired angular rates (rad/s), clamped to max rates.
      const aimKp = 4.0;
      const yawCmd = clamp(yawError * aimKp + manualYaw * jetYawRate, -jetYawRate, jetYawRate);
      const pitchCmd = clamp(pitchError * aimKp + manualPitch * jetPitchRate, -jetPitchRate, jetPitchRate);

      // Auto-bank towards turns (unless player is actively rolling).
      const maxAutoBank = 1.2;
      const bankTarget = jetAutoBank ? clamp(-yawError * jetAutoBankStrength, -maxAutoBank, maxAutoBank) : 0;
      const bankError = ((bankTarget - jetAngles.roll + Math.PI) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) - Math.PI;
      const rollAuto = jetAutoBank && Math.abs(manualRoll) < 0.05 ? clamp(bankError * 2.0, -jetRollRate, jetRollRate) : 0;
      const rollCmd = clamp(manualRoll * jetRollRate + rollAuto, -jetRollRate, jetRollRate);

      // Smooth rates for inertia (critically-damped-ish).
      const rateT = 1 - Math.exp(-10.0 * dt);
      jetRates.yaw = jetRates.yaw + (yawCmd - jetRates.yaw) * rateT;
      jetRates.pitch = jetRates.pitch + (pitchCmd - jetRates.pitch) * rateT;
      jetRates.roll = jetRates.roll + (rollCmd - jetRates.roll) * rateT;

      jetAngles.x += jetRates.yaw * dt;
      jetAngles.y = Math.max(-0.999, Math.min(0.999, jetAngles.y + jetRates.pitch * dt));
      jetAngles.roll += jetRates.roll * dt;

      // Wrap yaw/roll so they don't grow unbounded (roll can still barrel-roll).
      jetAngles.x = ((jetAngles.x % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
      jetAngles.roll = ((jetAngles.roll + Math.PI) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) - Math.PI;

      const forward2 = normalize3(computeTargetDirFromAngles(jetAngles.x, jetAngles.y));
      let right2 = normalize3(cross3(forward2, worldUp));
      if (Math.hypot(right2[0], right2[1], right2[2]) < 1e-6) right2 = [1, 0, 0];
      const upNoRoll2 = normalize3(cross3(right2, forward2));
      const up2 = normalize3(rotateAroundAxis(upNoRoll2, forward2, jetAngles.roll));
      right2 = normalize3(cross3(forward2, up2));
      const upFinal = normalize3(cross3(right2, forward2));

      // Throttle-driven speed along forward direction (Shift = afterburner).
      const targetSpeed = jetMinSpeed + jetThrottle * (jetMaxSpeed - jetMinSpeed);
      const boost = key("shift") ? flightBoost : 1.0;
      const desiredSpeed = targetSpeed * boost;
      const speedT = jetThrottleResponse > 0 ? 1 - Math.exp(-jetThrottleResponse * dt) : 1;
      jetState.speed = jetState.speed + (desiredSpeed - jetState.speed) * speedT;
      jetState.speed = clamp(jetState.speed, 0, Math.max(jetMaxSpeed * flightBoost, jetMaxSpeed));
      jetState.pos = add3(jetState.pos, scale3(forward2, jetState.speed * dt));

      cameraPosThisFrame = [...jetState.pos];
      cameraTargetDirThisFrame = forward2;
      cameraUpThisFrame = upFinal;

      curTargetDir = forward2;
      prevTargetDir = forward2;

      const hasLookInput = isPointerLocked && (Math.abs(lookDx) + Math.abs(lookDy) > 0);
      const hasJetInput = throttleInput || manualRoll || manualYaw || manualPitch;
      isInteracting = hasLookInput || hasJetInput || jetState.speed > 0.05;
      useReprojectionThisFrame = false;
    }
  }

  const lightUv = computeLightUv(curTargetDir, cameraUpThisFrame);
  const didRebuildB = needsBufferBRebuild;

  // If we're switching between quality (mouse up) and FAST (mouse down), reset history to avoid "chunky" lag/bands.
  const dragToggled = prevMouseDownForQualitySwitch !== isInteracting;
  prevMouseDownForQualitySwitch = isInteracting;
  if (dragToggled && fastWhileDrag && !fastMode && taaEnabled) {
    needsHistoryReset = true;
  }

  // BufferA: 1x4 state texture
  renderPass(passA, bufferA.writeFbo, 1, 4, time, frame);
  bufferA.swap();

  // BufferB: generate once (or on resize)
  if (didRebuildB) {
    renderPass(passB, bufferB.writeFbo, rtWidth, rtHeight, time, 0);
    bufferB.swap();
    needsBufferBRebuild = false;
  }

  if (taaEnabled) {
    // Image: render to an intermediate buffer, then temporally accumulate to reduce dithering grain.
    const imagePassThisFrame = isInteracting && fastWhileDrag ? passImageFast : passImage;
    renderPass(imagePassThisFrame, currentColorFbo, rtWidth, rtHeight, time, frame);

    // When reprojection is disabled (e.g. free-flight translation), accumulating during motion smears/darkens.
    // Only allow accumulation during motion if both `taaDuringDrag` and reprojection are enabled.
    const resetHistory =
      needsHistoryReset || didRebuildB || (isInteracting && (!taaDuringDrag || !useReprojectionThisFrame));
    const alphaThisFrame = isInteracting && taaUseDragAlpha ? taaAlphaDrag : taaAlpha;
    renderAccum(curTargetDir, resetHistory ? curTargetDir : prevTargetDir, resetHistory, alphaThisFrame, useReprojectionThisFrame);

    const finalTex = history.readTex;
    const applyRays = godraysEnabled && (godraysDuringDrag || !isInteracting);
    if (applyRays) renderGodrays(finalTex, lightUv);
    else renderBlit(finalTex);

    if (resetHistory) needsHistoryReset = false;
  } else {
    const imagePassThisFrame = isInteracting && fastWhileDrag ? passImageFast : passImage;

    if (godraysEnabled) {
      // Render to an intermediate texture so the post-pass can sample it.
      renderPass(imagePassThisFrame, currentColorFbo, rtWidth, rtHeight, time, frame);
      const applyRays = godraysDuringDrag || !isInteracting;
      if (applyRays) renderGodrays(currentColorTex, lightUv);
      else renderBlit(currentColorTex);
    } else {
      // Image: render directly to screen (original behavior, includes dithering grain).
      renderPass(imagePassThisFrame, null, rtWidth, rtHeight, time, frame);
    }
  }

  frame += 1;
  requestAnimationFrame(tick);
}

// Initialization will start the render loop
