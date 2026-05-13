/**
 * Particle Life WebGPU Renderer
 *
 * End-to-end WebGPU path: compute + render from the same storage buffer.
 * - Positions/species are stored in a storage buffer (vec4: xyz, species).
 * - Compute step updates positions/velocities (see ParticleLifeWebGPU for logic).
 * - Render step binds the particle buffer as a vertex buffer and draws points.
 *
 * Notes:
 * - This is a minimal scaffold and does not integrate with Three.js renderers.
 * - It targets pure WebGPU to keep the data on GPU without readback.
 */

export interface ParticleLifeWebGPURenderConfig {
  width: number;
  height: number;
  worldSize: number; // half-extent used to map to clip space
  background?: GPUColor;
}

export class ParticleLifeWebGPURenderer {
  private device: GPUDevice;
  private queue: GPUQueue;
  private format: GPUTextureFormat;
  private context: GPUCanvasContext;
  private pipeline: GPURenderPipeline;

  constructor(
    device: GPUDevice,
    queue: GPUQueue,
    canvas: HTMLCanvasElement,
    format: GPUTextureFormat,
    worldSize: number,
    background: GPUColor = { r: 0, g: 0, b: 0, a: 1 }
  ) {
    this.device = device;
    this.queue = queue;
    this.context = canvas.getContext('webgpu') as GPUCanvasContext;
    this.format = format;
    this.context.configure({
      device: this.device,
      format: this.format,
      alphaMode: 'premultiplied',
    });

    const code = `
      struct VSOut {
        @builtin(position) position : vec4<f32>,
        @location(0) color : vec3<f32>
      };

      @group(0) @binding(0) var<storage, read> particles : array<vec4<f32>>;
      @group(0) @binding(1) var<storage, read> velocities : array<vec4<f32>>; // unused in rendering

      @vertex
      fn vs(@builtin(vertex_index) vid : u32) -> VSOut {
        let p = particles[vid];
        // Map from world to clip space using worldSize
        let ws = ${worldSize}.0;
        let pos = vec3(p.x, p.y, p.z) / ws;
        var out : VSOut;
        out.position = vec4(pos, 1.0);
        // Simple palette from species
        let h = fract(p.w * 0.13);
        out.color = vec3(h, 0.6, 1.0 - h);
        return out;
      }

      @fragment
      fn fs(in: VSOut) -> @location(0) vec4<f32> {
        return vec4(in.color, 1.0);
      }
    `;

    this.pipeline = this.device.createRenderPipeline({
      layout: 'auto',
      vertex: {
        module: this.device.createShaderModule({ code }),
        entryPoint: 'vs',
      },
      fragment: {
        module: this.device.createShaderModule({ code }),
        entryPoint: 'fs',
        targets: [{ format: this.format }],
      },
      primitive: { topology: 'point-list' },
    });
  }

  /**
   * Render the particle buffer (count points).
   */
  public render(
    particleBuffer: GPUBuffer,
    velocityBuffer: GPUBuffer,
    count: number,
    clearColor: GPUColor = { r: 0, g: 0, b: 0, a: 1 }
  ): void {
    const encoder = this.device.createCommandEncoder();
    const view = this.context.getCurrentTexture().createView();
    const pass = encoder.beginRenderPass({
      colorAttachments: [
        {
          view,
          loadOp: 'clear',
          storeOp: 'store',
          clearValue: clearColor,
        },
      ],
    });
    const bg = this.device.createBindGroup({
      layout: this.pipeline.getBindGroupLayout(0),
      entries: [
        { binding: 0, resource: { buffer: particleBuffer } },
        { binding: 1, resource: { buffer: velocityBuffer } },
      ],
    });
    pass.setPipeline(this.pipeline);
    pass.setBindGroup(0, bg);
    pass.draw(count, 1, 0, 0);
    pass.end();
    this.queue.submit([encoder.finish()]);
  }
}

