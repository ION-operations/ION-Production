const canvas = document.getElementById("canvas");
const tabBarEl = document.getElementById("tabBar");
const tabPanelsEl = document.getElementById("tabPanels");
const collapseBtn = document.getElementById("collapseBtn");
const overlayBodyEl = document.getElementById("overlayBody");
let settingsEl = null;
let errorEl = null;
let statusPanelBody = null;

const urlParams = new URLSearchParams(window.location.search);

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
  cameraMode: "orbit", // orbit | fly
  flightSpeed: 60,
  flightBoost: 2.5,
  flightDamping: 1.5,
  flightBank: true,
  flightBankStrength: 0.6,
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

let cameraMode = getEnumParam("cam", effectiveDefaults.cameraMode, ["orbit", "fly"]);
let flightSpeed = getFloatParam("flySpeed", effectiveDefaults.flightSpeed, 1, 500);
let flightBoost = getFloatParam("flyBoost", effectiveDefaults.flightBoost, 1, 10);
let flightDamping = getFloatParam("flyDamp", effectiveDefaults.flightDamping, 0, 10);
let flightBank = getBoolParam("flyBank", effectiveDefaults.flightBank);
let flightBankStrength = getFloatParam("flyBankStrength", effectiveDefaults.flightBankStrength, 0, 2);

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

const fovDeg = 55.0;
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

const flightState = {
  pos: [-CLOUD_EXTENT_JS * 0.4, 0.7 * CLOUD_EXTENT_JS, CLOUD_EXTENT_JS * 0.4],
  vel: [0, 0, 0],
};

let prevMouseDownForQualitySwitch = false;

function getDpr() {
  return Math.max(1, Math.min(2, window.devicePixelRatio || 1));
}

function renderSettingsOverlay() {
  if (!settingsEl) return;

  const lines = [
    ["preset:", activePresetLabel],
    ["scale:", renderScale.toFixed(2)],
    ["fast:", fastMode ? "on" : "off"],
    ["fastWhileDrag:", fastWhileDrag ? "on" : "off"],
    ["taa:", taaEnabled ? "on" : "off"],
    ["lighting:", lightingMode],
    ["godrays:", godraysEnabled ? "on" : "off"],
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
  params.set("flySpeed", String(flightSpeed));
  params.set("flyBoost", String(flightBoost));
  params.set("flyDamp", String(flightDamping));
  params.set("flyBank", flightBank ? "1" : "0");
  params.set("flyBankStrength", String(flightBankStrength));

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
  flightSpeedRange: null,
  flightSpeedValue: null,
  flightBoostRange: null,
  flightBoostValue: null,
  flightDampingRange: null,
  flightDampingValue: null,
  flightBankCheckbox: null,
  flightBankStrengthRange: null,
  flightBankStrengthValue: null,
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

function createSection(panel, title, hint) {
  const wrapper = document.createElement('div');
  wrapper.style.display = 'flex';
  wrapper.style.flexDirection = 'column';
  wrapper.style.gap = '10px';
  const heading = document.createElement('h3');
  heading.textContent = title;
  heading.style.margin = '0 0 6px 0';
  wrapper.append(heading);
  if (hint) {
    const hintEl = document.createElement('div');
    hintEl.className = 'controlHint';
    hintEl.textContent = hint;
    wrapper.append(hintEl);
  }
  panel.append(wrapper);
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
  const prevScale = renderScale;
  const prevFast = fastMode;
  const prevFastWhileDrag = fastWhileDrag;
  const prevTaa = taaEnabled;
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
    cameraMode = patch.cameraMode === 'fly' ? 'fly' : 'orbit';
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
    if (ui.flightSpeedRange) ui.flightSpeedRange.value = String(flightSpeed);
    if (ui.flightSpeedValue) ui.flightSpeedValue.textContent = flightSpeed.toFixed(1);
    if (ui.flightBoostRange) ui.flightBoostRange.value = String(flightBoost);
    if (ui.flightBoostValue) ui.flightBoostValue.textContent = flightBoost.toFixed(2);
    if (ui.flightDampingRange) ui.flightDampingRange.value = String(flightDamping);
    if (ui.flightDampingValue) ui.flightDampingValue.textContent = flightDamping.toFixed(2);
    if (ui.flightBankCheckbox) ui.flightBankCheckbox.checked = flightBank;
    if (ui.flightBankStrengthRange) ui.flightBankStrengthRange.value = String(flightBankStrength);
    if (ui.flightBankStrengthValue) ui.flightBankStrengthValue.textContent = flightBankStrength.toFixed(2);

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
    statusPanelBody = document.createElement('div');
    statusPanelBody.style.display = 'flex';
    statusPanelBody.style.flexDirection = 'column';
    statusPanelBody.style.gap = '8px';
    settingsEl = document.createElement('div');
    settingsEl.id = 'settings';
    errorEl = document.createElement('div');
    errorEl.id = 'error';
    statusPanelBody.append(settingsEl, errorEl);
    statusPanel.append(statusPanelBody);
  }

  if (renderPanel) {
    const section = createSection(renderPanel, 'Render', 'Quality vs performance controls.');
    ui.presetSelect = addSelect(section, 'Preset', [
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
    const scaleCtrl = addSlider(section, 'Render scale', 'scale', { min: 0.2, max: 1, step: 0.01, format: (v) => v.toFixed(2) });
    ui.scaleRange = scaleCtrl.input;
    ui.scaleValue = scaleCtrl.valueEl;
    const timeCtrl = addSlider(section, 'Time scale', 'timeScale', { min: 0.05, max: 5, step: 0.01, format: (v) => v.toFixed(2) });
    ui.timeScaleRange = timeCtrl.input;
    ui.timeScaleValue = timeCtrl.valueEl;
    ui.fastCheckbox = addCheckbox(section, 'Fast shader mode', 'fast');
    ui.fastWhileDragCheckbox = addCheckbox(section, 'Use fast mode while dragging', 'fastWhileDrag');
  }

  if (temporalPanel) {
    const section = createSection(temporalPanel, 'Temporal accumulation', 'Reduce grain with reprojection + alpha blend.');
    ui.taaCheckbox = addCheckbox(section, 'Enable TAA', 'taa');
    ui.accumWhileDragCheckbox = addCheckbox(section, 'Accumulate while dragging', 'taaDuringDrag');
    ui.reprojectCheckbox = addCheckbox(section, 'Use reprojection', 'reproject');
    const alphaCtrl = addSlider(section, 'TAA alpha (still)', 'taaAlpha', { min: 0.02, max: 0.5, step: 0.005, format: (v) => v.toFixed(3) });
    ui.alphaRange = alphaCtrl.input;
    ui.alphaValue = alphaCtrl.valueEl;
    ui.useDragAlphaCheckbox = addCheckbox(section, 'Use higher alpha while dragging', 'taaUseDragAlpha');
    const alphaDragCtrl = addSlider(section, 'TAA alpha (drag)', 'taaAlphaDrag', { min: 0.02, max: 0.5, step: 0.005, format: (v) => v.toFixed(3) });
    ui.alphaDragRange = alphaDragCtrl.input;
    ui.alphaDragValue = alphaDragCtrl.valueEl;
    ui.resetHistoryBtn = document.createElement('button');
    ui.resetHistoryBtn.type = 'button';
    ui.resetHistoryBtn.textContent = 'Reset history';
    ui.resetHistoryBtn.addEventListener('click', () => {
      needsHistoryReset = true;
    });
    section.append(createControlRow('History', ui.resetHistoryBtn));
  }

  if (lightingPanel) {
    const section = createSection(lightingPanel, 'Lighting & sky', 'Switch day/night and tweak colors.');
    ui.lightingSelect = addSelect(section, 'Mode', [
      { label: 'Night (moon)', value: 'night' },
      { label: 'Day (sun)', value: 'day' },
    ], 'lighting', (val) => applyLightingPreset(val));
    const azCtrl = addSlider(section, 'Azimuth', 'lightAzimuthDeg', { min: 0, max: 360, step: 1, format: (v) => v.toFixed(0) + '?' });
    ui.lightAzRange = azCtrl.input;
    ui.lightAzValue = azCtrl.valueEl;
    const elCtrl = addSlider(section, 'Elevation', 'lightHeight', { min: -1, max: 1, step: 0.01 });
    ui.lightHeightRange = elCtrl.input;
    ui.lightHeightValue = elCtrl.valueEl;
    ui.lightColorInput = addColor(section, 'Light color', 'lightColor');
    const powerCtrl = addSlider(section, 'Light power', 'lightPower', { min: 0, max: 400, step: 1, format: (v) => v.toFixed(0) });
    ui.lightPowerRange = powerCtrl.input;
    ui.lightPowerValue = powerCtrl.valueEl;
    const exposureCtrl = addSlider(section, 'Exposure', 'exposure', { min: 0, max: 2, step: 0.01 });
    ui.exposureRange = exposureCtrl.input;
    ui.exposureValue = exposureCtrl.valueEl;
    const starCtrl = addSlider(section, 'Stars', 'stars', { min: 0, max: 1, step: 0.01 });
    ui.starsRange = starCtrl.input;
    ui.starsValue = starCtrl.valueEl;
    ui.nightSkyColorInput = addColor(section, 'Night sky base', 'nightSkyColor');
    ui.daySkyZenithColorInput = addColor(section, 'Day sky zenith', 'daySkyZenithColor');
    ui.daySkyHorizonColorInput = addColor(section, 'Day sky horizon', 'daySkyHorizonColor');
    const sunDiskCtrl = addSlider(section, 'Sun/moon disk', 'sunDiskIntensity', { min: 0, max: 5, step: 0.01 });
    ui.sunDiskRange = sunDiskCtrl.input;
    ui.sunDiskValue = sunDiskCtrl.valueEl;
    const sunGlowCtrl = addSlider(section, 'Sun/moon glow', 'sunGlowIntensity', { min: 0, max: 5, step: 0.01 });
    ui.sunGlowRange = sunGlowCtrl.input;
    ui.sunGlowValue = sunGlowCtrl.valueEl;
    const celDistCtrl = addSlider(section, 'Celestial distance', 'celestialDistance', { min: 10, max: 500, step: 1, format: (v) => v.toFixed(0) });
    ui.celestialDistRange = celDistCtrl.input;
    ui.celestialDistValue = celDistCtrl.valueEl;
    const celSizeCtrl = addSlider(section, 'Celestial size', 'celestialSize', { min: 0.1, max: 50, step: 0.1 });
    ui.celestialSizeRange = celSizeCtrl.input;
    ui.celestialSizeValue = celSizeCtrl.valueEl;
  }

  if (cloudsPanel) {
    const section = createSection(cloudsPanel, 'Cloud field', 'Main noise + detail carving and seeds.');
    const shapeCtrl = addSlider(section, 'Shape scroll speed', 'shapeSpeed', { min: -50, max: 50, step: 0.1 });
    ui.shapeSpeedRange = shapeCtrl.input;
    ui.shapeSpeedValue = shapeCtrl.valueEl;
    const detailCtrl = addSlider(section, 'Detail scroll speed', 'detailSpeed', { min: -50, max: 50, step: 0.1 });
    ui.detailSpeedRange = detailCtrl.input;
    ui.detailSpeedValue = detailCtrl.valueEl;
    const densityCtrl = addSlider(section, 'Density multiplier', 'densityMultiplier', { min: 0, max: 1, step: 0.001, format: (v) => v.toFixed(3) });
    ui.densityMulRange = densityCtrl.input;
    ui.densityMulValue = densityCtrl.valueEl;
    const shapeStrengthCtrl = addSlider(section, 'Shape strength', 'shapeStrength', { min: 0, max: 2, step: 0.01, format: (v) => v.toFixed(3) });
    ui.shapeStrengthRange = shapeStrengthCtrl.input;
    ui.shapeStrengthValue = shapeStrengthCtrl.valueEl;
    const detailStrengthCtrl = addSlider(section, 'Detail strength', 'detailStrength', { min: 0, max: 2, step: 0.01, format: (v) => v.toFixed(3) });
    ui.detailStrengthRange = detailStrengthCtrl.input;
    ui.detailStrengthValue = detailStrengthCtrl.valueEl;
    const seedCtrl = addSlider(section, 'Noise seed', 'noiseSeed', { min: -1000, max: 1000, step: 1, format: (v) => v.toFixed(0) });
    ui.noiseSeedRange = seedCtrl.input;
    ui.noiseSeedValue = seedCtrl.valueEl;
  }

  if (flightPanel) {
    const section = createSection(flightPanel, 'Camera & flight', 'Orbit vs free-flight controls.');
    ui.cameraModeSelect = addSelect(section, 'Mode', [
      { label: 'Orbit', value: 'orbit' },
      { label: 'Free flight', value: 'fly' },
    ], 'cameraMode');
    const speedCtrl = addSlider(section, 'Cruise speed', 'flightSpeed', { min: 1, max: 500, step: 1, format: (v) => v.toFixed(0) });
    ui.flightSpeedRange = speedCtrl.input;
    ui.flightSpeedValue = speedCtrl.valueEl;
    const boostCtrl = addSlider(section, 'Boost multiplier', 'flightBoost', { min: 1, max: 10, step: 0.05 });
    ui.flightBoostRange = boostCtrl.input;
    ui.flightBoostValue = boostCtrl.valueEl;
    const dampCtrl = addSlider(section, 'Damping', 'flightDamping', { min: 0, max: 10, step: 0.05 });
    ui.flightDampingRange = dampCtrl.input;
    ui.flightDampingValue = dampCtrl.valueEl;
    ui.flightBankCheckbox = addCheckbox(section, 'Bank while turning', 'flightBank');
    const bankCtrl = addSlider(section, 'Bank strength', 'flightBankStrength', { min: 0, max: 2, step: 0.05 });
    ui.flightBankStrengthRange = bankCtrl.input;
    ui.flightBankStrengthValue = bankCtrl.valueEl;
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
  gl.uniform1i(pass.uniforms.iFrame, frame);

  const mx = state.mouseX;
  const my = state.mouseY;
  const mz = state.mouseDown ? mx : 0;
  const mw = state.mouseDown ? my : 0;
  gl.uniform4f(pass.uniforms.iMouse, mx, my, mz, mw);
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

function computeLightUv(targetDir) {
  if (rtWidth <= 0 || rtHeight <= 0) return null;

  const up = [0, 1, 0];
  const zaxis = normalize3(targetDir);
  const xaxis = normalize3(cross3(zaxis, up));
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

function renderAccum(targetDirCur, targetDirPrev, resetHistory, alpha) {
  gl.useProgram(passAccum.program);
  gl.bindVertexArray(vao);
  gl.bindFramebuffer(gl.FRAMEBUFFER, history.writeFbo);
  gl.viewport(0, 0, rtWidth, rtHeight);

  gl.uniform2f(passAccum.uniforms.uResolution, rtWidth, rtHeight);
  gl.uniform1f(passAccum.uniforms.uAlpha, alpha);
  gl.uniform1i(passAccum.uniforms.uReset, resetHistory ? 1 : 0);
  gl.uniform1i(passAccum.uniforms.uUseReprojection, taaReproject ? 1 : 0);
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

let start = performance.now();
let frame = 0;

function tick() {
  const now = performance.now();
  const time = (now - start) / 1000;

  const { curTargetDir, prevTargetDir } = updateAnglesForFrame(frame);
  const lightUv = computeLightUv(curTargetDir);
  const didRebuildB = needsBufferBRebuild;

  // If we're switching between quality (mouse up) and FAST (mouse down), reset history to avoid "chunky" lag/bands.
  const dragToggled = prevMouseDownForQualitySwitch !== state.mouseDown;
  prevMouseDownForQualitySwitch = state.mouseDown;
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
    const imagePassThisFrame = state.mouseDown && fastWhileDrag ? passImageFast : passImage;
    renderPass(imagePassThisFrame, currentColorFbo, rtWidth, rtHeight, time, frame);

    const resetHistory = needsHistoryReset || didRebuildB || (state.mouseDown && !taaDuringDrag);
    const alphaThisFrame = state.mouseDown && taaUseDragAlpha ? taaAlphaDrag : taaAlpha;
    renderAccum(curTargetDir, resetHistory ? curTargetDir : prevTargetDir, resetHistory, alphaThisFrame);

    const finalTex = history.readTex;
    const applyRays = godraysEnabled && (godraysDuringDrag || !state.mouseDown);
    if (applyRays) renderGodrays(finalTex, lightUv);
    else renderBlit(finalTex);

    if (resetHistory) needsHistoryReset = false;
  } else {
    const imagePassThisFrame = state.mouseDown && fastWhileDrag ? passImageFast : passImage;

    if (godraysEnabled) {
      // Render to an intermediate texture so the post-pass can sample it.
      renderPass(imagePassThisFrame, currentColorFbo, rtWidth, rtHeight, time, frame);
      const applyRays = godraysDuringDrag || !state.mouseDown;
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

setError("");
requestAnimationFrame(tick);
