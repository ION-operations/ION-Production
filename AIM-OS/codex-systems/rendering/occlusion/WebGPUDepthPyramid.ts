/**
 * WebGPU Depth Pyramid (Hi-Z) Builder
 *
 * Builds mipmapped depth pyramid using a compute shader. Requires WebGPU.
 * Inputs:
 *  - depthTexture: depth rendered to a texture (R32Float recommended)
 * Outputs:
 *  - Array of GPUTextures, one per mip level (level 0 is copy of input or downsampled)
 */

export interface WebGPUDepthPyramidConfig {
  width: number;
  height: number;
  levels?: number;
}

export class WebGPUDepthPyramid {
  private device: GPUDevice;
  private config: WebGPUDepthPyramidConfig;
  private pipeline: GPUComputePipeline;

  constructor(device: GPUDevice, config: WebGPUDepthPyramidConfig) {
    this.device = device;
    this.config = config;
    const maxDim = Math.max(config.width, config.height);
    const levels = config.levels ?? Math.floor(Math.log2(maxDim)) + 1;

    const code = `
      struct Params { srcWidth:u32; srcHeight:u32; };
      @group(0) @binding(0) var samp : sampler;
      @group(0) @binding(1) var tSrc : texture_2d<f32>;
      @group(0) @binding(2) var tDst : texture_storage_2d<r32float, write>;
      @group(0) @binding(3) var<uniform> params : Params;

      @compute @workgroup_size(8,8)
      fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
        if (gid.x >= params.srcWidth || gid.y >= params.srcHeight) { return; }
        let uv = (vec2<f32>(gid.xy) + vec2<f32>(0.5)) / vec2<f32>(params.srcWidth, params.srcHeight);
        let texSize = vec2<f32>(params.srcWidth, params.srcHeight);
        let texel = vec2<f32>(1.0) / texSize;
        let d0 = textureSampleLevel(tSrc, samp, uv + vec2<f32>( 0.0, 0.0) * texel, 0.0).r;
        let d1 = textureSampleLevel(tSrc, samp, uv + vec2<f32>( texel.x, 0.0), 0.0).r;
        let d2 = textureSampleLevel(tSrc, samp, uv + vec2<f32>( 0.0, texel.y), 0.0).r;
        let d3 = textureSampleLevel(tSrc, samp, uv + vec2<f32>( texel.x, texel.y), 0.0).r;
        let m = min(d0, min(d1, min(d2, d3)));
        textureStore(tDst, vec2<i32>(gid.xy), vec4<f32>(m, 0.0, 0.0, 0.0));
      }
    `;

    this.pipeline = device.createComputePipeline({
      layout: 'auto',
      compute: { module: device.createShaderModule({ code }), entryPoint: 'main' },
    });
  }

  /**
   * Build pyramid. Returns GPUTexture array of length levels.
   */
  public build(depthTexture: GPUTexture): GPUTexture[] {
    const maxDim = Math.max(this.config.width, this.config.height);
    const levels = this.config.levels ?? Math.floor(Math.log2(maxDim)) + 1;
    const textures: GPUTexture[] = [];

    // level 0: copy from input
    let srcTex = depthTexture;
    let srcWidth = this.config.width;
    let srcHeight = this.config.height;

    for (let level = 0; level < levels; level++) {
      const dstWidth = Math.max(1, srcWidth >> 1);
      const dstHeight = Math.max(1, srcHeight >> 1);
      const dst = this.device.createTexture({
        size: [dstWidth, dstHeight],
        format: 'r32float',
        usage: GPUTextureUsage.STORAGE_BINDING | GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_SRC,
      });

      const sampler = this.device.createSampler({
        magFilter: 'nearest',
        minFilter: 'nearest',
      });

      const bindGroup = this.device.createBindGroup({
        layout: this.pipeline.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: sampler },
          { binding: 1, resource: srcTex.createView() },
          { binding: 2, resource: dst.createView() },
          {
            binding: 3,
            resource: {
              buffer: this.device.createBuffer({
                size: 8,
                usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
              }),
            },
          },
        ],
      });

      const encoder = this.device.createCommandEncoder();
      const pass = encoder.beginComputePass();
      pass.setPipeline(this.pipeline);

      // Upload params
      const paramsBuf = (bindGroup.getBindGroupEntry(3)?.resource as GPUBufferBinding).buffer;
      const paramsArray = new Uint32Array([dstWidth, dstHeight]);
      this.device.queue.writeBuffer(paramsBuf, 0, paramsArray.buffer);

      pass.setBindGroup(0, bindGroup);
      const wgX = Math.ceil(dstWidth / 8);
      const wgY = Math.ceil(dstHeight / 8);
      pass.dispatchWorkgroups(wgX, wgY);
      pass.end();
      this.device.queue.submit([encoder.finish()]);

      textures.push(dst);

      // Next level uses this level as source
      srcTex = dst;
      srcWidth = dstWidth;
      srcHeight = dstHeight;
    }

    return textures;
  }
}

