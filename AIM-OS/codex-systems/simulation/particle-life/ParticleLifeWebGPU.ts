/**
 * Particle Life WebGPU Scaffold
 * Placeholder for a compute-driven implementation.
 *
 * Notes:
 * - Checks for WebGPU support and sets up device/queue.
 * - Pipeline definitions are TODO; this is a wiring scaffold to avoid blocking.
 */

export class ParticleLifeWebGPU {
  private device: GPUDevice | null = null;
  private queue: GPUQueue | null = null;
  private supported = false;

  // Buffers
  private particleBuffer: GPUBuffer | null = null; // vec4: xyz, species
  private velocityBuffer: GPUBuffer | null = null; // vec4: vx,vy,vz,pad
  private paramsBuffer: GPUBuffer | null = null;   // timestep, damping, maxDist, count
  private interactionBuffer: GPUBuffer | null = null; // flattened matrix
  private bindGroupLayout: GPUBindGroupLayout | null = null;
  private bindGroup: GPUBindGroup | null = null;
  private pipeline: GPUComputePipeline | null = null;
  private count = 0;
  private speciesCount = 0;

  public async init(): Promise<boolean> {
    if (!('gpu' in navigator)) return false;
    const adapter = await (navigator as any).gpu.requestAdapter();
    if (!adapter) return false;
    this.device = await adapter.requestDevice();
    this.queue = this.device.queue;
    this.supported = true;
    return true;
  }

  public isSupported(): boolean {
    return this.supported;
  }

  /**
   * Allocate buffers for N particles (pos xyz + species).
   */
  public allocate(count: number, speciesCount: number, interactionMatrix: number[][]): void {
    if (!this.device) return;
    this.count = count;
    this.speciesCount = speciesCount;
    const stride = 4 * 4; // x,y,z,species (float)
    const size = count * stride;
    this.particleBuffer = this.device.createBuffer({
      size,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST | GPUBufferUsage.COPY_SRC,
    });

    this.velocityBuffer = this.device.createBuffer({
      size,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST | GPUBufferUsage.COPY_SRC,
    });

    this.paramsBuffer = this.device.createBuffer({
      size: 4 * 4, // timestep, damping, maxDist, falloff (placeholder)
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });

    // Flatten interaction matrix (speciesCount x speciesCount)
    const flat = new Float32Array(speciesCount * speciesCount);
    for (let a = 0; a < speciesCount; a++) {
      for (let b = 0; b < speciesCount; b++) {
        flat[a * speciesCount + b] = interactionMatrix[a][b];
      }
    }
    this.interactionBuffer = this.device.createBuffer({
      size: flat.byteLength,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
    });
    this.queue!.writeBuffer(this.interactionBuffer, 0, flat);

    this.bindGroupLayout = this.device.createBindGroupLayout({
      entries: [
        { binding: 0, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
        { binding: 1, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
        { binding: 2, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'uniform' } },
        { binding: 3, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
      ],
    });

    this.bindGroup = this.device.createBindGroup({
      layout: this.bindGroupLayout,
      entries: [
        { binding: 0, resource: { buffer: this.particleBuffer } },
        { binding: 1, resource: { buffer: this.velocityBuffer } },
        { binding: 2, resource: { buffer: this.paramsBuffer } },
        { binding: 3, resource: { buffer: this.interactionBuffer } },
      ],
    });

    // Compute shader with simple O(n) attraction/repulsion using interaction matrix.
    const code = `
      struct Params { dt:f32; damping:f32; maxDist:f32; speciesCount:f32; };
      @group(0) @binding(0) var<storage, read_write> particles : array<vec4<f32>>; // xyz, species
      @group(0) @binding(1) var<storage, read_write> velocities : array<vec4<f32>>; // vx,vy,vz,pad
      @group(0) @binding(2) var<uniform> params : Params;
      @group(0) @binding(3) var<storage> interactions : array<f32>; // speciesCount x speciesCount

      @compute @workgroup_size(64)
      fn main(@builtin(global_invocation_id) gid : vec3<u32>) {
        let idx = gid.x;
        if (idx >= arrayLength(&particles)) { return; }

        var p = particles[idx];
        var v = velocities[idx];
        let count = arrayLength(&particles);

        let maxDist = params.maxDist;
        let maxDist2 = maxDist * maxDist;

        var fx = 0.0;
        var fy = 0.0;
        var fz = 0.0;

        // O(N) loop – fine for small demos
        for (var j:u32 = 0u; j < count; j = j + 1u) {
          if (j == idx) { continue; }
          let op = particles[j];
          let dx = op.x - p.x;
          let dy = op.y - p.y;
          let dz = op.z - p.z;
          let d2 = dx*dx + dy*dy + dz*dz;
          if (d2 < 1e-6 || d2 > maxDist2) { continue; }
          let dist = sqrt(d2);
          let sA = i32(p.w);
          let sB = i32(op.w);
          let matIndex = sA * i32(params.speciesCount) + sB;
          let force = interactions[matIndex];
          let fall = 1.0 - dist / maxDist;
          let f = force * fall / (dist + 1e-4);
          fx += dx * f;
          fy += dy * f;
          fz += dz * f;
        }

        v.x = (v.x + fx * params.dt) * params.damping;
        v.y = (v.y + fy * params.dt) * params.damping;
        v.z = (v.z + fz * params.dt) * params.damping;
        p.x = p.x + v.x * params.dt;
        p.y = p.y + v.y * params.dt;
        p.z = p.z + v.z * params.dt;

        particles[idx] = p;
        velocities[idx] = v;
      }
    `;

    this.pipeline = this.device.createComputePipeline({
      layout: this.device.createPipelineLayout({ bindGroupLayouts: [this.bindGroupLayout] }),
      compute: { module: this.device.createShaderModule({ code }), entryPoint: 'main' },
    });
  }

  public uploadParams(dt: number, damping: number, maxDist: number): void {
    if (!this.device || !this.paramsBuffer) return;
    const arr = new Float32Array([dt, damping, maxDist, this.speciesCount]);
    this.queue!.writeBuffer(this.paramsBuffer, 0, arr.buffer);
  }

  public uploadParticles(data: Float32Array): void {
    if (!this.queue || !this.particleBuffer) return;
    this.queue.writeBuffer(this.particleBuffer, 0, data);
  }

  public step(): void {
    if (!this.device || !this.pipeline || !this.bindGroup) return;
    const encoder = this.device.createCommandEncoder();
    const pass = encoder.beginComputePass();
    pass.setPipeline(this.pipeline);
    pass.setBindGroup(0, this.bindGroup);
    const workgroups = Math.ceil(this.count / 64);
    pass.dispatchWorkgroups(workgroups);
    pass.end();
    this.queue!.submit([encoder.finish()]);
  }
}

