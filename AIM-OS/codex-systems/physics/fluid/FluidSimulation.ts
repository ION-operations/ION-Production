/**
 * GPU-Accelerated Fluid Simulation
 * Based on Navier-Stokes equations
 * 
 * 7-Pass Pipeline:
 * 1. Advection - Move velocity field along itself
 * 2. Curl - Calculate vorticity
 * 3. Vorticity Confinement - Add rotational forces
 * 4. Divergence - Calculate velocity divergence
 * 5. Pressure - Solve pressure field (Jacobi iteration)
 * 6. Gradient Subtract - Make velocity divergence-free
 * 7. Dye Advection - Move dye/density field
 */

import {
  FluidConfig,
  FluidState,
  FluidPrograms,
  DoubleFBO,
  SingleFBO,
  Pointer,
  DEFAULT_FLUID_CONFIG
} from './FluidTypes';

export class FluidSimulation {
  private gl: WebGLRenderingContext;
  private config: FluidConfig;
  private state!: FluidState;
  private programs!: FluidPrograms;
  private quadVAO!: WebGLBuffer;
  private pointers: Pointer[] = [];
  private lastTime: number = 0;

  constructor(canvas: HTMLCanvasElement, config: Partial<FluidConfig> = {}) {
    const gl = canvas.getContext('webgl', {
      alpha: true,
      depth: false,
      stencil: false,
      antialias: false,
      preserveDrawingBuffer: false
    });

    if (!gl) {
      throw new Error('WebGL not supported');
    }

    this.gl = gl;
    this.config = { ...DEFAULT_FLUID_CONFIG, ...config };

    this.initExtensions();
    this.initShaders();
    this.initFramebuffers();
    this.initQuad();
    this.initPointers();
  }

  private initExtensions(): void {
    const gl = this.gl;
    
    // Required extensions for float textures
    const halfFloat = gl.getExtension('OES_texture_half_float');
    const halfFloatLinear = gl.getExtension('OES_texture_half_float_linear');
    
    if (!halfFloat) {
      console.warn('OES_texture_half_float not supported, falling back to UNSIGNED_BYTE');
    }
  }

  private initShaders(): void {
    // Shader source would be loaded from files in production
    // For now, inline the essential parts
    
    const baseVertexShader = `
      precision highp float;
      attribute vec2 aPosition;
      varying vec2 vUv;
      uniform vec2 texelSize;
      
      void main() {
        vUv = aPosition * 0.5 + 0.5;
        gl_Position = vec4(aPosition, 0.0, 1.0);
      }
    `;

    this.programs = {
      advection: this.createProgram(baseVertexShader, this.getAdvectionShader()),
      divergence: this.createProgram(baseVertexShader, this.getDivergenceShader()),
      curl: this.createProgram(baseVertexShader, this.getCurlShader()),
      vorticity: this.createProgram(baseVertexShader, this.getVorticityShader()),
      pressure: this.createProgram(baseVertexShader, this.getPressureShader()),
      gradientSubtract: this.createProgram(baseVertexShader, this.getGradientSubtractShader()),
      splat: this.createProgram(baseVertexShader, this.getSplatShader()),
      display: this.createProgram(baseVertexShader, this.getDisplayShader()),
      clear: this.createProgram(baseVertexShader, this.getClearShader())
    };
  }

  private createProgram(vertexSource: string, fragmentSource: string): WebGLProgram {
    const gl = this.gl;
    
    const vertexShader = this.compileShader(gl.VERTEX_SHADER, vertexSource);
    const fragmentShader = this.compileShader(gl.FRAGMENT_SHADER, fragmentSource);
    
    const program = gl.createProgram()!;
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error('Program link failed: ' + gl.getProgramInfoLog(program));
    }
    
    return program;
  }

  private compileShader(type: number, source: string): WebGLShader {
    const gl = this.gl;
    const shader = gl.createShader(type)!;
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      throw new Error('Shader compile failed: ' + gl.getShaderInfoLog(shader));
    }
    
    return shader;
  }

  private initFramebuffers(): void {
    const { width, height } = this.config;
    const dyeWidth = Math.floor(width * this.config.dyeResolution);
    const dyeHeight = Math.floor(height * this.config.dyeResolution);

    this.state = {
      velocity: this.createDoubleFBO(width, height),
      pressure: this.createDoubleFBO(width, height),
      divergence: this.createSingleFBO(width, height),
      curl: this.createSingleFBO(width, height),
      dye: this.createDoubleFBO(dyeWidth, dyeHeight)
    };
  }

  private createDoubleFBO(width: number, height: number): DoubleFBO {
    const fbo1 = this.createSingleFBO(width, height);
    const fbo2 = this.createSingleFBO(width, height);
    
    return {
      read: fbo1.texture,
      write: fbo2.texture,
      readFBO: fbo1.fbo,
      writeFBO: fbo2.fbo,
      width,
      height,
      texelSizeX: 1.0 / width,
      texelSizeY: 1.0 / height
    };
  }

  private createSingleFBO(width: number, height: number): SingleFBO {
    const gl = this.gl;
    
    const texture = gl.createTexture()!;
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    
    const fbo = gl.createFramebuffer()!;
    gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
    
    return { texture, fbo, width, height };
  }

  private swapFBO(fbo: DoubleFBO): void {
    const temp = fbo.read;
    fbo.read = fbo.write;
    fbo.write = temp;
    
    const tempFBO = fbo.readFBO;
    fbo.readFBO = fbo.writeFBO;
    fbo.writeFBO = tempFBO;
  }

  private initQuad(): void {
    const gl = this.gl;
    
    this.quadVAO = gl.createBuffer()!;
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadVAO);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
       1,  1
    ]), gl.STATIC_DRAW);
  }

  private initPointers(): void {
    this.pointers.push({
      id: -1,
      x: 0,
      y: 0,
      deltaX: 0,
      deltaY: 0,
      down: false,
      moved: false,
      color: [0.3, 0.0, 0.8]
    });
  }

  /**
   * Main simulation step
   */
  public step(dt: number): void {
    const gl = this.gl;
    
    gl.disable(gl.BLEND);
    
    // 1. Curl calculation
    this.curl();
    
    // 2. Vorticity confinement
    this.vorticity(dt);
    
    // 3. Divergence calculation
    this.divergence();
    
    // 4. Pressure solve (Jacobi iteration)
    this.pressure();
    
    // 5. Gradient subtraction (make velocity divergence-free)
    this.gradientSubtract();
    
    // 6. Advect velocity
    this.advect(this.state.velocity, this.state.velocity, this.config.velocityDissipation, dt);
    
    // 7. Advect dye
    this.advect(this.state.dye, this.state.velocity, this.config.densityDissipation, dt);
  }

  private curl(): void {
    const gl = this.gl;
    gl.useProgram(this.programs.curl);
    
    gl.uniform2f(
      gl.getUniformLocation(this.programs.curl, 'texelSize'),
      this.state.velocity.texelSizeX,
      this.state.velocity.texelSizeY
    );
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.state.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.curl, 'uVelocity'), 0);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.curl.fbo);
    gl.viewport(0, 0, this.state.curl.width, this.state.curl.height);
    this.blit();
  }

  private vorticity(dt: number): void {
    const gl = this.gl;
    gl.useProgram(this.programs.vorticity);
    
    gl.uniform2f(
      gl.getUniformLocation(this.programs.vorticity, 'texelSize'),
      this.state.velocity.texelSizeX,
      this.state.velocity.texelSizeY
    );
    gl.uniform1f(gl.getUniformLocation(this.programs.vorticity, 'curl'), this.config.curlStrength);
    gl.uniform1f(gl.getUniformLocation(this.programs.vorticity, 'dt'), dt);
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.state.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.vorticity, 'uVelocity'), 0);
    
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.state.curl.texture);
    gl.uniform1i(gl.getUniformLocation(this.programs.vorticity, 'uCurl'), 1);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.velocity.writeFBO);
    gl.viewport(0, 0, this.state.velocity.width, this.state.velocity.height);
    this.blit();
    this.swapFBO(this.state.velocity);
  }

  private divergence(): void {
    const gl = this.gl;
    gl.useProgram(this.programs.divergence);
    
    gl.uniform2f(
      gl.getUniformLocation(this.programs.divergence, 'texelSize'),
      this.state.velocity.texelSizeX,
      this.state.velocity.texelSizeY
    );
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.state.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.divergence, 'uVelocity'), 0);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.divergence.fbo);
    gl.viewport(0, 0, this.state.divergence.width, this.state.divergence.height);
    this.blit();
  }

  private pressure(): void {
    const gl = this.gl;
    gl.useProgram(this.programs.pressure);
    
    gl.uniform2f(
      gl.getUniformLocation(this.programs.pressure, 'texelSize'),
      this.state.velocity.texelSizeX,
      this.state.velocity.texelSizeY
    );
    
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.state.divergence.texture);
    gl.uniform1i(gl.getUniformLocation(this.programs.pressure, 'uDivergence'), 1);
    
    // Clear pressure
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.pressure.readFBO);
    gl.clearColor(0, 0, 0, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    
    // Jacobi iterations
    for (let i = 0; i < this.config.pressureIterations; i++) {
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, this.state.pressure.read);
      gl.uniform1i(gl.getUniformLocation(this.programs.pressure, 'uPressure'), 0);
      
      gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.pressure.writeFBO);
      gl.viewport(0, 0, this.state.pressure.width, this.state.pressure.height);
      this.blit();
      this.swapFBO(this.state.pressure);
    }
  }

  private gradientSubtract(): void {
    const gl = this.gl;
    gl.useProgram(this.programs.gradientSubtract);
    
    gl.uniform2f(
      gl.getUniformLocation(this.programs.gradientSubtract, 'texelSize'),
      this.state.velocity.texelSizeX,
      this.state.velocity.texelSizeY
    );
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.state.pressure.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.gradientSubtract, 'uPressure'), 0);
    
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.state.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.gradientSubtract, 'uVelocity'), 1);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.velocity.writeFBO);
    gl.viewport(0, 0, this.state.velocity.width, this.state.velocity.height);
    this.blit();
    this.swapFBO(this.state.velocity);
  }

  private advect(target: DoubleFBO, velocity: DoubleFBO, dissipation: number, dt: number): void {
    const gl = this.gl;
    gl.useProgram(this.programs.advection);
    
    gl.uniform2f(
      gl.getUniformLocation(this.programs.advection, 'texelSize'),
      velocity.texelSizeX,
      velocity.texelSizeY
    );
    gl.uniform1f(gl.getUniformLocation(this.programs.advection, 'dt'), dt);
    gl.uniform1f(gl.getUniformLocation(this.programs.advection, 'dissipation'), dissipation);
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.advection, 'uVelocity'), 0);
    
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, target.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.advection, 'uSource'), 1);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, target.writeFBO);
    gl.viewport(0, 0, target.width, target.height);
    this.blit();
    this.swapFBO(target);
  }

  /**
   * Add force/dye at position
   */
  public splat(x: number, y: number, dx: number, dy: number, color: [number, number, number]): void {
    const gl = this.gl;
    gl.useProgram(this.programs.splat);
    
    const aspectRatio = this.config.width / this.config.height;
    
    // Splat velocity
    gl.uniform1f(gl.getUniformLocation(this.programs.splat, 'aspectRatio'), aspectRatio);
    gl.uniform2f(gl.getUniformLocation(this.programs.splat, 'point'), x, y);
    gl.uniform1f(gl.getUniformLocation(this.programs.splat, 'radius'), this.config.splatRadius / 100.0);
    gl.uniform3f(gl.getUniformLocation(this.programs.splat, 'color'), dx * this.config.splatForce, dy * this.config.splatForce, 0);
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.state.velocity.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.splat, 'uTarget'), 0);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.velocity.writeFBO);
    gl.viewport(0, 0, this.state.velocity.width, this.state.velocity.height);
    this.blit();
    this.swapFBO(this.state.velocity);
    
    // Splat dye
    gl.uniform3f(gl.getUniformLocation(this.programs.splat, 'color'), color[0], color[1], color[2]);
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.state.dye.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.splat, 'uTarget'), 0);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.state.dye.writeFBO);
    gl.viewport(0, 0, this.state.dye.width, this.state.dye.height);
    this.blit();
    this.swapFBO(this.state.dye);
  }

  /**
   * Render to screen
   */
  public render(): void {
    const gl = this.gl;
    
    gl.useProgram(this.programs.display);
    gl.uniform1f(gl.getUniformLocation(this.programs.display, 'brightness'), 1.0);
    
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.state.dye.read);
    gl.uniform1i(gl.getUniformLocation(this.programs.display, 'uTexture'), 0);
    
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
    this.blit();
  }

  private blit(): void {
    const gl = this.gl;
    
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadVAO);
    const posLocation = gl.getAttribLocation(gl.getParameter(gl.CURRENT_PROGRAM), 'aPosition');
    gl.enableVertexAttribArray(posLocation);
    gl.vertexAttribPointer(posLocation, 2, gl.FLOAT, false, 0, 0);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  // ============================================
  // INLINE SHADER SOURCES
  // ============================================

  private getAdvectionShader(): string {
    return `
      precision highp float;
      uniform sampler2D uVelocity;
      uniform sampler2D uSource;
      uniform vec2 texelSize;
      uniform float dt;
      uniform float dissipation;
      varying vec2 vUv;
      
      void main() {
        vec2 coord = vUv - dt * texture2D(uVelocity, vUv).xy * texelSize;
        gl_FragColor = dissipation * texture2D(uSource, coord);
      }
    `;
  }

  private getDivergenceShader(): string {
    return `
      precision highp float;
      uniform sampler2D uVelocity;
      uniform vec2 texelSize;
      varying vec2 vUv;
      
      void main() {
        float L = texture2D(uVelocity, vUv - vec2(texelSize.x, 0.0)).x;
        float R = texture2D(uVelocity, vUv + vec2(texelSize.x, 0.0)).x;
        float T = texture2D(uVelocity, vUv + vec2(0.0, texelSize.y)).y;
        float B = texture2D(uVelocity, vUv - vec2(0.0, texelSize.y)).y;
        float div = 0.5 * (R - L + T - B);
        gl_FragColor = vec4(div, 0.0, 0.0, 1.0);
      }
    `;
  }

  private getCurlShader(): string {
    return `
      precision highp float;
      uniform sampler2D uVelocity;
      uniform vec2 texelSize;
      varying vec2 vUv;
      
      void main() {
        float L = texture2D(uVelocity, vUv - vec2(texelSize.x, 0.0)).y;
        float R = texture2D(uVelocity, vUv + vec2(texelSize.x, 0.0)).y;
        float T = texture2D(uVelocity, vUv + vec2(0.0, texelSize.y)).x;
        float B = texture2D(uVelocity, vUv - vec2(0.0, texelSize.y)).x;
        float vorticity = R - L - T + B;
        gl_FragColor = vec4(0.5 * vorticity, 0.0, 0.0, 1.0);
      }
    `;
  }

  private getVorticityShader(): string {
    return `
      precision highp float;
      uniform sampler2D uVelocity;
      uniform sampler2D uCurl;
      uniform float curl;
      uniform float dt;
      uniform vec2 texelSize;
      varying vec2 vUv;
      
      void main() {
        float L = texture2D(uCurl, vUv - vec2(texelSize.x, 0.0)).x;
        float R = texture2D(uCurl, vUv + vec2(texelSize.x, 0.0)).x;
        float T = texture2D(uCurl, vUv + vec2(0.0, texelSize.y)).x;
        float B = texture2D(uCurl, vUv - vec2(0.0, texelSize.y)).x;
        float C = texture2D(uCurl, vUv).x;
        
        vec2 force = 0.5 * vec2(abs(T) - abs(B), abs(R) - abs(L));
        force /= length(force) + 0.0001;
        force *= curl * C;
        force.y *= -1.0;
        
        vec2 velocity = texture2D(uVelocity, vUv).xy;
        velocity += force * dt;
        gl_FragColor = vec4(velocity, 0.0, 1.0);
      }
    `;
  }

  private getPressureShader(): string {
    return `
      precision highp float;
      uniform sampler2D uPressure;
      uniform sampler2D uDivergence;
      uniform vec2 texelSize;
      varying vec2 vUv;
      
      void main() {
        float L = texture2D(uPressure, vUv - vec2(texelSize.x, 0.0)).x;
        float R = texture2D(uPressure, vUv + vec2(texelSize.x, 0.0)).x;
        float T = texture2D(uPressure, vUv + vec2(0.0, texelSize.y)).x;
        float B = texture2D(uPressure, vUv - vec2(0.0, texelSize.y)).x;
        float C = texture2D(uDivergence, vUv).x;
        float pressure = (L + R + B + T - C) * 0.25;
        gl_FragColor = vec4(pressure, 0.0, 0.0, 1.0);
      }
    `;
  }

  private getGradientSubtractShader(): string {
    return `
      precision highp float;
      uniform sampler2D uPressure;
      uniform sampler2D uVelocity;
      uniform vec2 texelSize;
      varying vec2 vUv;
      
      void main() {
        float L = texture2D(uPressure, vUv - vec2(texelSize.x, 0.0)).x;
        float R = texture2D(uPressure, vUv + vec2(texelSize.x, 0.0)).x;
        float T = texture2D(uPressure, vUv + vec2(0.0, texelSize.y)).x;
        float B = texture2D(uPressure, vUv - vec2(0.0, texelSize.y)).x;
        vec2 velocity = texture2D(uVelocity, vUv).xy;
        velocity.xy -= vec2(R - L, T - B);
        gl_FragColor = vec4(velocity, 0.0, 1.0);
      }
    `;
  }

  private getSplatShader(): string {
    return `
      precision highp float;
      uniform sampler2D uTarget;
      uniform float aspectRatio;
      uniform vec3 color;
      uniform vec2 point;
      uniform float radius;
      varying vec2 vUv;
      
      void main() {
        vec2 p = vUv - point.xy;
        p.x *= aspectRatio;
        vec3 splat = exp(-dot(p, p) / radius) * color;
        vec3 base = texture2D(uTarget, vUv).xyz;
        gl_FragColor = vec4(base + splat, 1.0);
      }
    `;
  }

  private getDisplayShader(): string {
    return `
      precision highp float;
      uniform sampler2D uTexture;
      uniform float brightness;
      varying vec2 vUv;
      
      void main() {
        vec3 color = texture2D(uTexture, vUv).rgb;
        color *= brightness;
        color = color / (1.0 + color);
        gl_FragColor = vec4(color, 1.0);
      }
    `;
  }

  private getClearShader(): string {
    return `
      precision highp float;
      uniform sampler2D uTexture;
      uniform float value;
      varying vec2 vUv;
      
      void main() {
        gl_FragColor = value * texture2D(uTexture, vUv);
      }
    `;
  }

  /**
   * Cleanup resources
   */
  public dispose(): void {
    const gl = this.gl;
    
    // Delete framebuffers and textures
    gl.deleteFramebuffer(this.state.velocity.readFBO);
    gl.deleteFramebuffer(this.state.velocity.writeFBO);
    gl.deleteTexture(this.state.velocity.read);
    gl.deleteTexture(this.state.velocity.write);
    
    gl.deleteFramebuffer(this.state.pressure.readFBO);
    gl.deleteFramebuffer(this.state.pressure.writeFBO);
    gl.deleteTexture(this.state.pressure.read);
    gl.deleteTexture(this.state.pressure.write);
    
    gl.deleteFramebuffer(this.state.divergence.fbo);
    gl.deleteTexture(this.state.divergence.texture);
    
    gl.deleteFramebuffer(this.state.curl.fbo);
    gl.deleteTexture(this.state.curl.texture);
    
    gl.deleteFramebuffer(this.state.dye.readFBO);
    gl.deleteFramebuffer(this.state.dye.writeFBO);
    gl.deleteTexture(this.state.dye.read);
    gl.deleteTexture(this.state.dye.write);
    
    // Delete programs
    Object.values(this.programs).forEach(program => {
      gl.deleteProgram(program);
    });
    
    gl.deleteBuffer(this.quadVAO);
  }
}

