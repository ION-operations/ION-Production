/* eslint-disable @typescript-eslint/no-non-null-assertion */

/**
 * FluidSimulator.ts
 *
 * 2D Navier–Stokes fluid simulation on the GPU using WebGL2.
 * Pipeline (per step):
 *   1. Apply queued splats (forces + dye).
 *   2. Advect velocity.
 *   3. Advect dye.
 *   4. Compute curl (vorticity).
 *   5. Apply vorticity confinement to velocity.
 *   6. Compute divergence of velocity.
 *   7. Jacobi iterations to solve for pressure.
 *   8. Subtract pressure gradient from velocity.
 *
 * Rendering:
 *   - A simple display pass maps dye (RGB) to the default framebuffer.
 *
 * The simulator is self‑contained and does not depend on the Lucid engine.
 */

export interface FluidParams {
  /** Simulation resolution in texels (width). */
  simWidth: number;
  /** Simulation resolution in texels (height). */
  simHeight: number;
  /** Viscosity / velocity dissipation in [0, 1]. */
  velocityDissipation: number;
  /** Dye dissipation in [0, 1]. */
  dyeDissipation: number;
  /** Strength of vorticity confinement. */
  vorticityStrength: number;
  /** Number of Jacobi iterations for the pressure solve. */
  pressureIterations: number;
}

const DEFAULT_PARAMS: FluidParams = {
  simWidth: 256,
  simHeight: 256,
  velocityDissipation: 0.99,
  dyeDissipation: 0.999,
  vorticityStrength: 30.0,
  pressureIterations: 40,
};

interface PingPongTarget {
  readonly width: number;
  readonly height: number;
  read: WebGLTexture;
  write: WebGLTexture;
  fboRead: WebGLFramebuffer;
  fboWrite: WebGLFramebuffer;
}

interface SingleTarget {
  readonly width: number;
  readonly height: number;
  texture: WebGLTexture;
  fbo: WebGLFramebuffer;
}

interface Splat {
  /** Normalized coordinates in [0, 1]. */
  x: number;
  y: number;
  /** Force to apply to velocity (in simulation space). */
  forceX: number;
  forceY: number;
  /** Dye color to inject. */
  r: number;
  g: number;
  b: number;
}

function assertWebGL2(gl: WebGL2RenderingContext | null): asserts gl is WebGL2RenderingContext {
  if (!gl) {
    throw new Error("WebGL2 context is required for FluidSimulator.");
  }
}

function createTexture(
  gl: WebGL2RenderingContext,
  width: number,
  height: number,
  internalFormat: number,
  format: number,
  type: number,
  filtering: number,
): WebGLTexture {
  const tex = gl.createTexture();
  if (!tex) {
    throw new Error("Failed to create texture.");
  }
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filtering);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filtering);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texImage2D(
    gl.TEXTURE_2D,
    0,
    internalFormat,
    width,
    height,
    0,
    format,
    type,
    null,
  );
  gl.bindTexture(gl.TEXTURE_2D, null);
  return tex;
}

function createFramebuffer(gl: WebGL2RenderingContext, tex: WebGLTexture): WebGLFramebuffer {
  const fbo = gl.createFramebuffer();
  if (!fbo) {
    throw new Error("Failed to create framebuffer.");
  }
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
  const status = gl.checkFramebufferStatus(gl.FRAMEBUFFER);
  if (status !== gl.FRAMEBUFFER_COMPLETE) {
    throw new Error(`Framebuffer incomplete: 0x${status.toString(16)}`);
  }
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  return fbo;
}

function createPingPongTarget(
  gl: WebGL2RenderingContext,
  width: number,
  height: number,
  internalFormat: number,
  format: number,
  type: number,
): PingPongTarget {
  const texA = createTexture(gl, width, height, internalFormat, format, type, gl.LINEAR);
  const texB = createTexture(gl, width, height, internalFormat, format, type, gl.LINEAR);
  const fboA = createFramebuffer(gl, texA);
  const fboB = createFramebuffer(gl, texB);
  return {
    width,
    height,
    read: texA,
    write: texB,
    fboRead: fboA,
    fboWrite: fboB,
  };
}

function swapPingPong(target: PingPongTarget): void {
  const tmpTex = target.read;
  target.read = target.write;
  target.write = tmpTex;
  const tmpFbo = target.fboRead;
  target.fboRead = target.fboWrite;
  target.fboWrite = tmpFbo;
}

function createSingleTarget(
  gl: WebGL2RenderingContext,
  width: number,
  height: number,
  internalFormat: number,
  format: number,
  type: number,
): SingleTarget {
  const tex = createTexture(gl, width, height, internalFormat, format, type, gl.LINEAR);
  const fbo = createFramebuffer(gl, tex);
  return {
    width,
    height,
    texture: tex,
    fbo,
  };
}

function compileShader(gl: WebGL2RenderingContext, type: number, source: string): WebGLShader {
  const shader = gl.createShader(type);
  if (!shader) {
    throw new Error("Failed to create shader.");
  }
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  const ok = gl.getShaderParameter(shader, gl.COMPILE_STATUS) as boolean;
  if (!ok) {
    const log = gl.getShaderInfoLog(shader) ?? "Unknown error";
    gl.deleteShader(shader);
    throw new Error(`Shader compilation failed: ${log}`);
  }
  return shader;
}

function linkProgram(gl: WebGL2RenderingContext, vsSource: string, fsSource: string): WebGLProgram {
  const vs = compileShader(gl, gl.VERTEX_SHADER, vsSource);
  const fs = compileShader(gl, gl.FRAGMENT_SHADER, fsSource);
  const program = gl.createProgram();
  if (!program) {
    gl.deleteShader(vs);
    gl.deleteShader(fs);
    throw new Error("Failed to create program.");
  }
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);
  const ok = gl.getProgramParameter(program, gl.LINK_STATUS) as boolean;
  gl.deleteShader(vs);
  gl.deleteShader(fs);
  if (!ok) {
    const log = gl.getProgramInfoLog(program) ?? "Unknown error";
    gl.deleteProgram(program);
    throw new Error(`Program link failed: ${log}`);
  }
  return program;
}

export class FluidSimulator {
  private readonly gl: WebGL2RenderingContext;
  private params: FluidParams;

  private quadVao: WebGLVertexArrayObject | null = null;
  private quadVbo: WebGLBuffer | null = null;

  private velocity!: PingPongTarget;
  private dye!: PingPongTarget;
  private pressure!: PingPongTarget;
  private divergence!: SingleTarget;
  private curl!: SingleTarget;

  private advectProgram!: WebGLProgram;
  private divergenceProgram!: WebGLProgram;
  private pressureProgram!: WebGLProgram;
  private gradientSubtractProgram!: WebGLProgram;
  private vorticityProgram!: WebGLProgram;
  private vorticityForceProgram!: WebGLProgram;
  private splatProgram!: WebGLProgram;
  private displayProgram!: WebGLProgram;

  private pendingSplats: Splat[] = [];

  constructor(
    gl: WebGL2RenderingContext | null,
    simWidth: number,
    simHeight: number,
    params?: Partial<FluidParams>,
  ) {
    assertWebGL2(gl);
    this.gl = gl;
    this.params = {
      ...DEFAULT_PARAMS,
      simWidth,
      simHeight,
      ...params,
    };

    this.initQuad();
    this.initTargets();
    this.initPrograms();
  }

  updateParams(patch: Partial<FluidParams>): void {
    this.params = { ...this.params, ...patch };
  }

  resize(simWidth: number, simHeight: number): void {
    if (simWidth === this.params.simWidth && simHeight === this.params.simHeight) {
      return;
    }
    this.params.simWidth = simWidth;
    this.params.simHeight = simHeight;
    this.disposeTargets();
    this.initTargets();
  }

  addSplat(
    x: number,
    y: number,
    forceX: number,
    forceY: number,
    r: number,
    g: number,
    b: number,
  ): void {
    this.pendingSplats.push({ x, y, forceX, forceY, r, g, b });
  }

  step(dt: number): void {
    const gl = this.gl;
    const w = this.params.simWidth;
    const h = this.params.simHeight;

    gl.viewport(0, 0, w, h);

    this.applySplats();

    // Advect velocity.
    this.bindProgram(this.advectProgram);
    gl.uniform1f(gl.getUniformLocation(this.advectProgram, "uDt")!, dt);
    gl.uniform1f(gl.getUniformLocation(this.advectProgram, "uDissipation")!, this.params.velocityDissipation);
    gl.uniform2f(gl.getUniformLocation(this.advectProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.advectProgram, "uVelocity")!, 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.advectProgram, "uSource")!, 1);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.velocity.fboWrite);
    this.drawQuad();
    swapPingPong(this.velocity);

    // Advect dye.
    this.bindProgram(this.advectProgram);
    gl.uniform1f(gl.getUniformLocation(this.advectProgram, "uDt")!, dt);
    gl.uniform1f(gl.getUniformLocation(this.advectProgram, "uDissipation")!, this.params.dyeDissipation);
    gl.uniform2f(gl.getUniformLocation(this.advectProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.advectProgram, "uVelocity")!, 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.dye.read);
    gl.uniform1i(gl.getUniformLocation(this.advectProgram, "uSource")!, 1);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.dye.fboWrite);
    this.drawQuad();
    swapPingPong(this.dye);

    // Compute curl.
    this.bindProgram(this.vorticityProgram);
    gl.uniform2f(gl.getUniformLocation(this.vorticityProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.vorticityProgram, "uVelocity")!, 0);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.curl.fbo);
    this.drawQuad();

    // Vorticity confinement.
    this.bindProgram(this.vorticityForceProgram);
    gl.uniform2f(gl.getUniformLocation(this.vorticityForceProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);
    gl.uniform1f(
      gl.getUniformLocation(this.vorticityForceProgram, "uVorticityStrength")!,
      this.params.vorticityStrength,
    );
    gl.uniform1f(gl.getUniformLocation(this.vorticityForceProgram, "uDt")!, dt);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.vorticityForceProgram, "uVelocity")!, 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.curl.texture);
    gl.uniform1i(gl.getUniformLocation(this.vorticityForceProgram, "uCurl")!, 1);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.velocity.fboWrite);
    this.drawQuad();
    swapPingPong(this.velocity);

    // Divergence.
    this.bindProgram(this.divergenceProgram);
    gl.uniform2f(gl.getUniformLocation(this.divergenceProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.divergenceProgram, "uVelocity")!, 0);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.divergence.fbo);
    this.drawQuad();

    // Clear pressure.
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.pressure.fboRead);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.pressure.fboWrite);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Jacobi iterations.
    this.bindProgram(this.pressureProgram);
    gl.uniform2f(gl.getUniformLocation(this.pressureProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.divergence.texture);
    gl.uniform1i(gl.getUniformLocation(this.pressureProgram, "uDivergence")!, 1);

    for (let i = 0; i < this.params.pressureIterations; i++) {
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.pressure.read);
      gl.uniform1i(gl.getUniformLocation(this.pressureProgram, "uPressure")!, 0);
      gl.bindFramebuffer(gl.FRAMEBUFFER, this.pressure.fboWrite);
      this.drawQuad();
      swapPingPong(this.pressure);
    }

    // Subtract gradient.
    this.bindProgram(this.gradientSubtractProgram);
    gl.uniform2f(gl.getUniformLocation(this.gradientSubtractProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.gradientSubtractProgram, "uVelocity")!, 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.pressure.read);
    gl.uniform1i(gl.getUniformLocation(this.gradientSubtractProgram, "uPressure")!, 1);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.velocity.fboWrite);
    this.drawQuad();
    swapPingPong(this.velocity);

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  }

  renderToScreen(canvasWidth: number, canvasHeight: number): void {
    const gl = this.gl;
    gl.viewport(0, 0, canvasWidth, canvasHeight);
    this.bindProgram(this.displayProgram);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.dye.read);
    gl.uniform1i(gl.getUniformLocation(this.displayProgram, "uTexture")!, 0);
    this.drawQuad();
  }

  dispose(): void {
    const gl = this.gl;
    this.disposeTargets();

    if (this.advectProgram) gl.deleteProgram(this.advectProgram);
    if (this.divergenceProgram) gl.deleteProgram(this.divergenceProgram);
    if (this.pressureProgram) gl.deleteProgram(this.pressureProgram);
    if (this.gradientSubtractProgram) gl.deleteProgram(this.gradientSubtractProgram);
    if (this.vorticityProgram) gl.deleteProgram(this.vorticityProgram);
    if (this.vorticityForceProgram) gl.deleteProgram(this.vorticityForceProgram);
    if (this.splatProgram) gl.deleteProgram(this.splatProgram);
    if (this.displayProgram) gl.deleteProgram(this.displayProgram);

    if (this.quadVbo) gl.deleteBuffer(this.quadVbo);
    if (this.quadVao) gl.deleteVertexArray(this.quadVao);
  }

  private disposeTargets(): void {
    const gl = this.gl;
    const { velocity, dye, pressure, divergence, curl } = this;
    if (velocity) {
      gl.deleteFramebuffer(velocity.fboRead);
      gl.deleteFramebuffer(velocity.fboWrite);
      gl.deleteTexture(velocity.read);
      gl.deleteTexture(velocity.write);
    }
    if (dye) {
      gl.deleteFramebuffer(dye.fboRead);
      gl.deleteFramebuffer(dye.fboWrite);
      gl.deleteTexture(dye.read);
      gl.deleteTexture(dye.write);
    }
    if (pressure) {
      gl.deleteFramebuffer(pressure.fboRead);
      gl.deleteFramebuffer(pressure.fboWrite);
      gl.deleteTexture(pressure.read);
      gl.deleteTexture(pressure.write);
    }
    if (divergence) {
      gl.deleteFramebuffer(divergence.fbo);
      gl.deleteTexture(divergence.texture);
    }
    if (curl) {
      gl.deleteFramebuffer(curl.fbo);
      gl.deleteTexture(curl.texture);
    }
  }

  private initQuad(): void {
    const gl = this.gl;
    const vao = gl.createVertexArray();
    const vbo = gl.createBuffer();
    if (!vao || !vbo) {
      throw new Error("Failed to create fullscreen quad VAO/VBO.");
    }
    this.quadVao = vao;
    this.quadVbo = vbo;

    const vertices = new Float32Array([
      -1, -1,
      3, -1,
      -1, 3,
    ]);

    gl.bindVertexArray(this.quadVao);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadVbo);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    gl.bindVertexArray(null);
    gl.bindBuffer(gl.ARRAY_BUFFER, null);
  }

  private initTargets(): void {
    const gl = this.gl;
    const w = this.params.simWidth;
    const h = this.params.simHeight;

    const internalFormat = gl.RGBA16F;
    const format = gl.RGBA;
    const type = gl.HALF_FLOAT;

    this.velocity = createPingPongTarget(gl, w, h, internalFormat, format, type);
    this.dye = createPingPongTarget(gl, w, h, internalFormat, format, type);
    this.pressure = createPingPongTarget(gl, w, h, internalFormat, format, type);
    this.divergence = createSingleTarget(gl, w, h, internalFormat, format, type);
    this.curl = createSingleTarget(gl, w, h, internalFormat, format, type);

    gl.bindFramebuffer(gl.FRAMEBUFFER, this.velocity.fboRead);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.velocity.fboWrite);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.bindFramebuffer(gl.FRAMEBUFFER, this.dye.fboRead);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.dye.fboWrite);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  }

  private initPrograms(): void {
    const gl = this.gl;
    const vs = FULLSCREEN_VERT;

    this.advectProgram = linkProgram(gl, vs, ADVECTION_FRAG);
    this.divergenceProgram = linkProgram(gl, vs, DIVERGENCE_FRAG);
    this.pressureProgram = linkProgram(gl, vs, PRESSURE_FRAG);
    this.gradientSubtractProgram = linkProgram(gl, vs, GRADIENT_SUBTRACT_FRAG);
    this.vorticityProgram = linkProgram(gl, vs, VORTICITY_FRAG);
    this.vorticityForceProgram = linkProgram(gl, vs, VORTICITY_FORCE_FRAG);
    this.splatProgram = linkProgram(gl, vs, SPLAT_FRAG);
    this.displayProgram = linkProgram(gl, vs, DISPLAY_FRAG);
  }

  private bindProgram(program: WebGLProgram): void {
    const gl = this.gl;
    gl.useProgram(program);
    gl.bindVertexArray(this.quadVao);
  }

  private drawQuad(): void {
    const gl = this.gl;
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    gl.bindVertexArray(null);
  }

  private applySplats(): void {
    if (this.pendingSplats.length === 0) return;
    const gl = this.gl;
    const w = this.params.simWidth;
    const h = this.params.simHeight;

    this.bindProgram(this.splatProgram);
    gl.uniform2f(gl.getUniformLocation(this.splatProgram, "uTexelSize")!, 1.0 / w, 1.0 / h);

    for (const splat of this.pendingSplats) {
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.velocity.read);
      gl.uniform1i(gl.getUniformLocation(this.splatProgram, "uTarget")!, 0);
      gl.uniform2f(gl.getUniformLocation(this.splatProgram, "uPoint")!, splat.x, splat.y);
      gl.uniform3f(
        gl.getUniformLocation(this.splatProgram, "uColor")!,
        splat.forceX,
        splat.forceY,
        0,
      );
      gl.uniform1f(gl.getUniformLocation(this.splatProgram, "uRadius")!, 0.02);
      gl.bindFramebuffer(gl.FRAMEBUFFER, this.velocity.fboWrite);
      this.drawQuad();
      swapPingPong(this.velocity);

      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.dye.read);
      gl.uniform1i(gl.getUniformLocation(this.splatProgram, "uTarget")!, 0);
      gl.uniform2f(gl.getUniformLocation(this.splatProgram, "uPoint")!, splat.x, splat.y);
      gl.uniform3f(
        gl.getUniformLocation(this.splatProgram, "uColor")!,
        splat.r,
        splat.g,
        splat.b,
      );
      gl.uniform1f(gl.getUniformLocation(this.splatProgram, "uRadius")!, 0.03);
      gl.bindFramebuffer(gl.FRAMEBUFFER, this.dye.fboWrite);
      this.drawQuad();
      swapPingPong(this.dye);
    }

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    this.pendingSplats = [];
  }
}

const FULLSCREEN_VERT = `#version 300 es
precision mediump float;

layout (location = 0) in vec2 aPosition;
out vec2 vUv;

void main() {
  vUv = aPosition * 0.5 + 0.5;
  gl_Position = vec4(aPosition, 0.0, 1.0);
}
`;

const ADVECTION_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uVelocity;
uniform sampler2D uSource;
uniform vec2 uTexelSize;
uniform float uDt;
uniform float uDissipation;

void main() {
  vec2 coord = vUv;
  vec2 velocity = texture(uVelocity, coord).xy;
  vec2 prevCoord = coord - uDt * velocity * uTexelSize;
  vec4 src = texture(uSource, prevCoord);
  fragColor = src * uDissipation;
}
`;

const DIVERGENCE_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uVelocity;
uniform vec2 uTexelSize;

void main() {
  float left = texture(uVelocity, vUv - vec2(uTexelSize.x, 0.0)).x;
  float right = texture(uVelocity, vUv + vec2(uTexelSize.x, 0.0)).x;
  float bottom = texture(uVelocity, vUv - vec2(0.0, uTexelSize.y)).y;
  float top = texture(uVelocity, vUv + vec2(0.0, uTexelSize.y)).y;

  float divergence = 0.5 * ((right - left) + (top - bottom));
  fragColor = vec4(divergence, 0.0, 0.0, 1.0);
}
`;

const PRESSURE_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uPressure;
uniform sampler2D uDivergence;
uniform vec2 uTexelSize;

void main() {
  float left = texture(uPressure, vUv - vec2(uTexelSize.x, 0.0)).x;
  float right = texture(uPressure, vUv + vec2(uTexelSize.x, 0.0)).x;
  float bottom = texture(uPressure, vUv - vec2(0.0, uTexelSize.y)).x;
  float top = texture(uPressure, vUv + vec2(0.0, uTexelSize.y)).x;
  float centerDiv = texture(uDivergence, vUv).x;

  float pressure = (left + right + bottom + top - centerDiv) * 0.25;
  fragColor = vec4(pressure, 0.0, 0.0, 1.0);
}
`;

const GRADIENT_SUBTRACT_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uVelocity;
uniform sampler2D uPressure;
uniform vec2 uTexelSize;

void main() {
  float left = texture(uPressure, vUv - vec2(uTexelSize.x, 0.0)).x;
  float right = texture(uPressure, vUv + vec2(uTexelSize.x, 0.0)).x;
  float bottom = texture(uPressure, vUv - vec2(0.0, uTexelSize.y)).x;
  float top = texture(uPressure, vUv + vec2(0.0, uTexelSize.y)).x;

  vec2 gradient = vec2(right - left, top - bottom) * 0.5;
  vec2 velocity = texture(uVelocity, vUv).xy - gradient;

  fragColor = vec4(velocity, 0.0, 1.0);
}
`;

const VORTICITY_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uVelocity;
uniform vec2 uTexelSize;

void main() {
  float left = texture(uVelocity, vUv - vec2(uTexelSize.x, 0.0)).y;
  float right = texture(uVelocity, vUv + vec2(uTexelSize.x, 0.0)).y;
  float bottom = texture(uVelocity, vUv - vec2(0.0, uTexelSize.y)).x;
  float top = texture(uVelocity, vUv + vec2(0.0, uTexelSize.y)).x;
  float curl = right - left - (top - bottom);
  fragColor = vec4(curl, 0.0, 0.0, 1.0);
}
`;

const VORTICITY_FORCE_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uVelocity;
uniform sampler2D uCurl;
uniform vec2 uTexelSize;
uniform float uVorticityStrength;
uniform float uDt;

void main() {
  float curlL = abs(texture(uCurl, vUv - vec2(uTexelSize.x, 0.0)).x);
  float curlR = abs(texture(uCurl, vUv + vec2(uTexelSize.x, 0.0)).x);
  float curlB = abs(texture(uCurl, vUv - vec2(0.0, uTexelSize.y)).x);
  float curlT = abs(texture(uCurl, vUv + vec2(0.0, uTexelSize.y)).x);
  float curlC = texture(uCurl, vUv).x;

  vec2 grad = vec2(curlR - curlL, curlT - curlB);
  float len = length(grad) + 1e-5;
  vec2 n = grad / len;

  vec2 force = vec2(n.y, -n.x) * curlC * uVorticityStrength;
  vec2 velocity = texture(uVelocity, vUv).xy;
  velocity += force * uDt;

  fragColor = vec4(velocity, 0.0, 1.0);
}
`;

const SPLAT_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uTarget;
uniform vec2 uPoint;
uniform vec3 uColor;
uniform float uRadius;
uniform vec2 uTexelSize;

void main() {
  vec2 coord = vUv;
  vec4 base = texture(uTarget, coord);
  float d = distance(coord, uPoint);
  float influence = exp(-d * d / (uRadius * uRadius));
  vec3 result = base.rgb + uColor * influence;
  fragColor = vec4(result, 1.0);
}
`;

const DISPLAY_FRAG = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uTexture;

void main() {
  vec3 col = texture(uTexture, vUv).rgb;
  col = col / (col + vec3(1.0));
  col = pow(col, vec3(1.0 / 2.2));
  fragColor = vec4(col, 1.0);
}
`;

