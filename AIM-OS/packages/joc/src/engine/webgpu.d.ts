// WebGPU Type Declarations
// ═══════════════════════════════════════════════════════════════════
// Minimal WebGPU type stubs for the Surface Engine.
// These provide TypeScript awareness without requiring @webgpu/types.
// The actual WebGPU API is available in supported browsers natively.
// ═══════════════════════════════════════════════════════════════════

/* eslint-disable @typescript-eslint/no-explicit-any */

interface GPURequestAdapterOptions {
    powerPreference?: 'low-power' | 'high-performance';
}

interface GPUDeviceDescriptor {
    requiredFeatures?: string[];
    requiredLimits?: Record<string, number>;
}

interface GPUTextureDescriptor {
    size: [number, number] | { width: number; height: number };
    format: GPUTextureFormat;
    usage: number;
}

interface GPUBufferDescriptor {
    size: number;
    usage: number;
    mappedAtCreation?: boolean;
}

interface GPUShaderModuleDescriptor {
    code: string;
    label?: string;
}

interface GPURenderPipelineDescriptor {
    layout: 'auto' | any;
    vertex: {
        module: GPUShaderModule;
        entryPoint: string;
        buffers?: any[];
    };
    fragment?: {
        module: GPUShaderModule;
        entryPoint: string;
        targets: Array<{ format: GPUTextureFormat }>;
    };
    primitive?: {
        topology?: string;
        stripIndexFormat?: string;
        frontFace?: string;
        cullMode?: string;
    };
    depthStencil?: any;
    multisample?: any;
}

interface GPUBindGroupDescriptor {
    layout: GPUBindGroupLayout;
    entries: Array<{
        binding: number;
        resource: { buffer: GPUBuffer } | any;
    }>;
}

interface GPURenderPassDescriptor {
    colorAttachments: Array<{
        view: GPUTextureView;
        clearValue?: { r: number; g: number; b: number; a: number };
        loadOp: 'clear' | 'load';
        storeOp: 'store' | 'discard';
    }>;
    depthStencilAttachment?: any;
}

interface GPU {
    requestAdapter(options?: GPURequestAdapterOptions): Promise<GPUAdapter | null>;
    getPreferredCanvasFormat(): GPUTextureFormat;
}

interface GPUAdapter {
    requestDevice(descriptor?: GPUDeviceDescriptor): Promise<GPUDevice>;
    features: Set<string>;
    limits: Record<string, number>;
}

interface GPUDevice {
    createBuffer(descriptor: GPUBufferDescriptor): GPUBuffer;
    createShaderModule(descriptor: GPUShaderModuleDescriptor): GPUShaderModule;
    createRenderPipeline(descriptor: GPURenderPipelineDescriptor): GPURenderPipeline;
    createBindGroup(descriptor: GPUBindGroupDescriptor): GPUBindGroup;
    createCommandEncoder(): GPUCommandEncoder;
    queue: GPUQueue;
    destroy(): void;
}

interface GPUBuffer {
    destroy(): void;
    mapAsync(mode: number): Promise<void>;
    getMappedRange(): ArrayBuffer;
    unmap(): void;
}

interface GPUShaderModule { }

interface GPURenderPipeline {
    getBindGroupLayout(index: number): GPUBindGroupLayout;
}

interface GPUBindGroupLayout { }
interface GPUBindGroup { }

interface GPUCommandEncoder {
    beginRenderPass(descriptor: GPURenderPassDescriptor): GPURenderPassEncoder;
    finish(): GPUCommandBuffer;
}

interface GPURenderPassEncoder {
    setPipeline(pipeline: GPURenderPipeline): void;
    setBindGroup(index: number, bindGroup: GPUBindGroup): void;
    draw(vertexCount: number, instanceCount?: number, firstVertex?: number, firstInstance?: number): void;
    end(): void;
}

interface GPUQueue {
    submit(commandBuffers: GPUCommandBuffer[]): void;
    writeBuffer(buffer: GPUBuffer, offset: number, data: ArrayBuffer | ArrayBufferView): void;
}

interface GPUCommandBuffer { }
interface GPUTextureView { }

interface GPUTexture {
    createView(): GPUTextureView;
}

type GPUTextureFormat = string;

interface GPUCanvasContext {
    configure(config: {
        device: GPUDevice;
        format: GPUTextureFormat;
        alphaMode?: 'opaque' | 'premultiplied';
    }): void;
    getCurrentTexture(): GPUTexture;
}

// Buffer usage flags
declare const GPUBufferUsage: {
    MAP_READ: number;
    MAP_WRITE: number;
    COPY_SRC: number;
    COPY_DST: number;
    INDEX: number;
    VERTEX: number;
    UNIFORM: number;
    STORAGE: number;
    INDIRECT: number;
    QUERY_RESOLVE: number;
};

// Extend Navigator
interface Navigator {
    gpu?: GPU;
}

// Extend HTMLCanvasElement
interface HTMLCanvasElement {
    getContext(contextId: 'webgpu'): GPUCanvasContext | null;
}
