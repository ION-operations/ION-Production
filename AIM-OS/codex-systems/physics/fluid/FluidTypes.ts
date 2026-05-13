/**
 * Fluid Simulation Types
 * Navier-Stokes GPU-based fluid dynamics
 */

export interface FluidConfig {
  // Grid dimensions
  width: number;
  height: number;
  
  // Simulation parameters
  viscosity: number;          // Fluid viscosity (0.0001 - 0.1)
  diffusion: number;          // Dye diffusion rate
  pressureIterations: number; // Jacobi iterations for pressure solve (20-50)
  curlStrength: number;       // Vorticity confinement strength
  
  // Rendering
  dyeResolution: number;      // Dye texture resolution multiplier
  velocityDissipation: number; // Velocity decay (0.98 - 1.0)
  densityDissipation: number;  // Density/dye decay (0.97 - 1.0)
  
  // Interaction
  splatRadius: number;        // Splat size on interaction
  splatForce: number;         // Force applied on splat
}

export const DEFAULT_FLUID_CONFIG: FluidConfig = {
  width: 512,
  height: 512,
  viscosity: 0.0001,
  diffusion: 0.0,
  pressureIterations: 20,
  curlStrength: 30,
  dyeResolution: 1.0,
  velocityDissipation: 0.98,
  densityDissipation: 0.97,
  splatRadius: 0.25,
  splatForce: 6000
};

export interface FluidState {
  // Double-buffered textures for ping-pong rendering
  velocity: DoubleFBO;
  pressure: DoubleFBO;
  divergence: SingleFBO;
  curl: SingleFBO;
  dye: DoubleFBO;
}

export interface DoubleFBO {
  read: WebGLTexture;
  write: WebGLTexture;
  readFBO: WebGLFramebuffer;
  writeFBO: WebGLFramebuffer;
  width: number;
  height: number;
  texelSizeX: number;
  texelSizeY: number;
}

export interface SingleFBO {
  texture: WebGLTexture;
  fbo: WebGLFramebuffer;
  width: number;
  height: number;
}

export interface Pointer {
  id: number;
  x: number;
  y: number;
  deltaX: number;
  deltaY: number;
  down: boolean;
  moved: boolean;
  color: [number, number, number];
}

/**
 * Shader program references
 */
export interface FluidPrograms {
  advection: WebGLProgram;
  divergence: WebGLProgram;
  curl: WebGLProgram;
  vorticity: WebGLProgram;
  pressure: WebGLProgram;
  gradientSubtract: WebGLProgram;
  splat: WebGLProgram;
  display: WebGLProgram;
  clear: WebGLProgram;
}

/**
 * Uniform locations cache
 */
export interface UniformLocations {
  [programName: string]: {
    [uniformName: string]: WebGLUniformLocation | null;
  };
}

