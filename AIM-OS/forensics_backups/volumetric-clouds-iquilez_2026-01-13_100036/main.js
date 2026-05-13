const canvas = document.getElementById("canvas");
const errorEl = document.getElementById("error");
const infoEl = document.getElementById("info");

function setError(message) {
  errorEl.textContent = message ?? "";
}

// Resize canvas to match display size
function resizeCanvas() {
  const dpr = window.devicePixelRatio || 1;
  const width = window.innerWidth;
  const height = window.innerHeight;
  
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = width + "px";
  canvas.style.height = height + "px";
}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);

// Get WebGL2 context
const gl = canvas.getContext("webgl2");
if (!gl) {
  setError("WebGL2 not supported. Please use a modern browser.");
  throw new Error("WebGL2 not supported");
}

// Check for required extensions
const extFloat = gl.getExtension("EXT_color_buffer_float");
if (!extFloat) {
  setError("Warning: EXT_color_buffer_float not available. Some features may not work correctly.");
}

// Compile shader
function compileShader(source, type) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const error = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error(`Shader compilation error: ${error}`);
  }
  
  return shader;
}

// Create shader program
async function createProgram() {
  // Load shader source
  const response = await fetch("./shaders/clouds.glsl");
  if (!response.ok) {
    throw new Error(`Failed to load shader: ${response.statusText}`);
  }
  const fragmentSource = await response.text();
  
  // Vertex shader (fullscreen triangle - covers entire screen)
  const vertexSource = `#version 300 es
layout(location = 0) in vec2 aPosition;
void main() {
  gl_Position = vec4(aPosition, 0.0, 1.0);
}
`;

  // Fragment shader wrapper - use gl_FragCoord directly like Shadertoy
  const fullFragmentSource = `#version 300 es
precision highp float;

uniform vec3 iResolution;
uniform float iTime;
uniform vec2 iMouse;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;
uniform sampler2D iChannel2;
uniform vec3 iChannelResolution[4];

out vec4 fragColor;

${fragmentSource.replace(/void mainImage\(/g, "void mainImage_original(")}

void main() {
  vec4 color = vec4(0.0);
  mainImage_original(color, gl_FragCoord.xy);
  fragColor = color;
}
`;

  const vs = compileShader(vertexSource, gl.VERTEX_SHADER);
  const fs = compileShader(fullFragmentSource, gl.FRAGMENT_SHADER);
  
  const program = gl.createProgram();
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);
  
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const error = gl.getProgramInfoLog(program);
    gl.deleteProgram(program);
    throw new Error(`Program link error: ${error}`);
  }
  
  return program;
}

// Create noise texture (2D noise for iChannel0)
// This texture is used as 3D noise by encoding Z into XY using vec2(37.0,239.0)*p.z
// The shader samples with: textureLod(iChannel0,(uv+0.5)/256.0,0.0).yx
// So R and G channels are swapped (.yx) and mixed based on f.z
// Both R and G must have independent, pattern-free noise
function createNoiseTexture(size) {
  const data = new Uint8Array(size * size * 4);
  
  // Use crypto random for truly pattern-free noise, with deterministic fallback
  const cryptoObj = globalThis.crypto;
  const useCrypto = cryptoObj?.getRandomValues;
  
  // Generate noise - R and G channels need to be completely independent
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (y * size + x) * 4;
      
      if (useCrypto) {
        // Use crypto random for true randomness (no patterns)
        const randomBytes = new Uint8Array(4);
        cryptoObj.getRandomValues(randomBytes);
        data[idx + 0] = randomBytes[0]; // R
        data[idx + 1] = randomBytes[1]; // G
        data[idx + 2] = randomBytes[2]; // B
        data[idx + 3] = 255;
      } else {
        // Fallback: use different hash functions for each channel
        // This ensures independence and reduces patterns
        function hash(n) {
          n = (n << 13) ^ n;
          return ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483648.0;
        }
        
        const h1 = hash(x * 73 + y * 137);
        const h2 = hash(x * 179 + y * 251);
        const h3 = hash(x * 293 + y * 367);
        
        data[idx + 0] = Math.floor((h1 * 0.5 + 0.5) * 255); // R
        data[idx + 1] = Math.floor((h2 * 0.5 + 0.5) * 255); // G
        data[idx + 2] = Math.floor((h3 * 0.5 + 0.5) * 255); // B
        data[idx + 3] = 255;
      }
    }
  }
  
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, size, size, 0, gl.RGBA, gl.UNSIGNED_BYTE, data);
  // LINEAR filtering for smooth interpolation (textureLod with lod=0 uses linear)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  // REPEAT for seamless tiling (critical for 3D noise encoding with vec2(37.0,239.0)*p.z)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
  
  return texture;
}

// Create blue noise/dither texture (iChannel1)
// CRITICAL: This texture is used with texelFetch, which requires NEAREST filtering
// The shader uses: texelFetch(iChannel1, px&1023, 0).x for dithering
function createBlueNoiseTexture(size) {
  const data = new Uint8Array(size * size * 4);
  
  // Use crypto.getRandomValues if available, otherwise Math.random
  const cryptoObj = globalThis.crypto;
  if (cryptoObj?.getRandomValues) {
    // Fill in chunks (some browsers limit to 65536 bytes)
    const maxChunk = 65536;
    for (let offset = 0; offset < data.length; offset += maxChunk) {
      cryptoObj.getRandomValues(data.subarray(offset, Math.min(data.length, offset + maxChunk)));
    }
  } else {
    // Fallback to Math.random
    for (let i = 0; i < data.length; i++) {
      data[i] = Math.floor(Math.random() * 256);
    }
  }
  
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, size, size, 0, gl.RGBA, gl.UNSIGNED_BYTE, data);
  // CRITICAL: texelFetch requires NEAREST filtering (no interpolation)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  // REPEAT for tiling (px&1023 wraps around)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
  
  return texture;
}

// Create 3D noise texture (iChannel2) - simple approximation
function create3DNoiseTexture(size) {
  const data = new Uint8Array(size * size * size * 4);
  for (let z = 0; z < size; z++) {
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const i = (z * size * size + y * size + x) * 4;
        const hash = ((x * 12.9898 + y * 78.233 + z * 37.7193) % 1.0) * 255;
        data[i + 0] = hash;
        data[i + 1] = hash;
        data[i + 2] = hash;
        data[i + 3] = 255;
      }
    }
  }
  
  // Note: WebGL2 doesn't support 3D textures directly in this context
  // We'll create a 2D texture as a fallback
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  // Flatten to 2D (size x size^2)
  const flatData = new Uint8Array(size * size * size * 4);
  for (let i = 0; i < size * size * size; i++) {
    const z = Math.floor(i / (size * size));
    const y = Math.floor((i % (size * size)) / size);
    const x = i % size;
    const idx = (z * size * size + y * size + x) * 4;
    flatData[i * 4 + 0] = data[idx + 0];
    flatData[i * 4 + 1] = data[idx + 1];
    flatData[i * 4 + 2] = data[idx + 2];
    flatData[i * 4 + 3] = data[idx + 3];
  }
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, size, size * size, 0, gl.RGBA, gl.UNSIGNED_BYTE, flatData);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
  
  return texture;
}

// Fullscreen triangle vertices (covers entire screen with 2 triangles)
// Using triangle strip: [-1,-1], [3,-1], [-1,3] creates 2 triangles covering full screen
const quadVertices = new Float32Array([
  -1, -1,
   3, -1,
  -1,  3,
]);

// Mouse state
let mouseX = 0.5;
let mouseY = 0.5;
let isDragging = false;

canvas.addEventListener("mousedown", (e) => {
  isDragging = true;
  updateMouse(e);
});

canvas.addEventListener("mousemove", (e) => {
  if (isDragging) {
    updateMouse(e);
  }
});

canvas.addEventListener("mouseup", () => {
  isDragging = false;
});

canvas.addEventListener("mouseleave", () => {
  isDragging = false;
});

function updateMouse(e) {
  const rect = canvas.getBoundingClientRect();
  mouseX = (e.clientX - rect.left) / rect.width;
  mouseY = (e.clientY - rect.top) / rect.height;
}

// Main render loop
async function init() {
  try {
    const program = await createProgram();
    
    // Create textures
    const noiseTex = createNoiseTexture(256);
    const blueNoiseTex = createBlueNoiseTexture(1024);
    const noise3DTex = create3DNoiseTexture(32);
    
    // Create vertex buffer
    const vbo = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
    gl.bufferData(gl.ARRAY_BUFFER, quadVertices, gl.STATIC_DRAW);
    
    // Get attribute and uniform locations
    const positionLoc = gl.getAttribLocation(program, "a_position");
    const resolutionLoc = gl.getUniformLocation(program, "iResolution");
    const timeLoc = gl.getUniformLocation(program, "iTime");
    const mouseLoc = gl.getUniformLocation(program, "iMouse");
    const channel0Loc = gl.getUniformLocation(program, "iChannel0");
    const channel1Loc = gl.getUniformLocation(program, "iChannel1");
    const channel2Loc = gl.getUniformLocation(program, "iChannel2");
    const channelResLoc = gl.getUniformLocation(program, "iChannelResolution");
    
    let startTime = Date.now();
    
    function render() {
      const currentTime = (Date.now() - startTime) / 1000.0;
      
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.clearColor(0, 0, 0, 1);
      gl.clear(gl.COLOR_BUFFER_BIT);
      
      gl.useProgram(program);
      
      // Set up vertex buffer
      gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
      gl.enableVertexAttribArray(positionLoc);
      gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0);
      
      // Set uniforms
      gl.uniform3f(resolutionLoc, canvas.width, canvas.height, 1.0);
      gl.uniform1f(timeLoc, currentTime);
      // iMouse: pixel coordinates (x, y) - Shadertoy format
      // gl_FragCoord.y increases upward (0 at bottom), so mouse Y needs to be from bottom
      gl.uniform2f(mouseLoc, mouseX * canvas.width, (1.0 - mouseY) * canvas.height);
      
      // Bind textures
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, noiseTex);
      gl.uniform1i(channel0Loc, 0);
      
      gl.activeTexture(gl.TEXTURE1);
      gl.bindTexture(gl.TEXTURE_2D, blueNoiseTex);
      gl.uniform1i(channel1Loc, 1);
      
      gl.activeTexture(gl.TEXTURE2);
      gl.bindTexture(gl.TEXTURE_2D, noise3DTex);
      gl.uniform1i(channel2Loc, 2);
      
      // Channel resolutions
      gl.uniform3fv(channelResLoc, new Float32Array([
        256, 256, 1,
        1024, 1024, 1,
        32, 32, 32,
        0, 0, 0
      ]));
      
      // Draw fullscreen triangle (2 triangles covering full screen)
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      
      requestAnimationFrame(render);
    }
    
    infoEl.textContent = "Drag mouse to rotate camera. WebGL2 required.";
    render();
    
  } catch (error) {
    setError(error.message);
    console.error(error);
  }
}

init();
