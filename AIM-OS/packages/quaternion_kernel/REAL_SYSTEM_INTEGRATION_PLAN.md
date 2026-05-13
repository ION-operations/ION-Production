# Phase 2 Real System Integration Plan

**Status:** 📋 **PLANNING**  
**Date:** 2025-01-27  
**Phase:** Phase 2 - Real System Integrations  
**Purpose:** Comprehensive plan for integrating PLIX Quaternion Extension with real AIM-OS systems

---

## 🎯 Overview

This document provides a detailed plan for integrating the PLIX Quaternion Extension with four critical AIM-OS systems:

1. **Real Rust Kernel Bridge** (FFI or HTTP)
2. **Real GPU Field Solver** (κ/λ/ρ field updates)
3. **Real CMC Storage Client** (Bitemporal entity storage)
4. **Real HHNI/SEG/CMC Clients** (Tag resolution and provenance)

---

## 1. Real Rust Kernel Bridge

### 1.1 Architecture Decision: FFI vs HTTP

**Decision Matrix:**

| Factor | FFI (Foreign Function Interface) | HTTP (REST API) |
|--------|----------------------------------|-----------------|
| **Performance** | ⭐⭐⭐⭐⭐ Lowest latency (< 1ms) | ⭐⭐⭐ Higher latency (5-50ms) |
| **Complexity** | ⭐⭐ Higher (native bindings) | ⭐⭐⭐⭐ Lower (standard HTTP) |
| **Deployment** | ⭐⭐ Requires native compilation | ⭐⭐⭐⭐⭐ Easy (separate service) |
| **Debugging** | ⭐⭐⭐ More complex | ⭐⭐⭐⭐⭐ Easier (standard tools) |
| **Scalability** | ⭐⭐⭐ Single process | ⭐⭐⭐⭐⭐ Multi-process/distributed |
| **Language** | ⭐⭐⭐ Requires Rust/Node.js FFI | ⭐⭐⭐⭐⭐ Language-agnostic |

**Recommendation:** **Start with HTTP, optimize to FFI if needed**

**Rationale:**
- HTTP is easier to implement and debug
- Allows kernel to run as separate service
- Can optimize to FFI later if performance is critical
- Better for distributed deployments

### 1.2 HTTP API Design

**Base URL:** `http://localhost:8080/api/kernel/v1`

**Endpoints:**

#### `POST /syscall/place`
```json
{
  "actor_qaddr": {
    "n": 1,
    "l": "io",
    "m": 1234,
    "s": "act",
    "morton_key": 1234567890,
    "s3_bin": 5678
  },
  "entity_id": "uuid-string",
  "entity_state": {
    "qaddr": {...},
    "pose": {
      "rotation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
      "translation": {"w": 0.0, "x": 0.1, "y": 0.0, "z": 0.0}
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "entity_id": "uuid-string",
  "qaddr": {...},
  "selection_rules": {
    "delta_n": 0,
    "delta_l": true,
    "delta_m": true,
    "delta_s": true,
    "ok": true
  }
}
```

#### `POST /syscall/move`
```json
{
  "actor_qaddr": {...},
  "entity_id": "uuid-string",
  "delta_pose": {
    "rotation": {...},
    "translation": {...}
  },
  "current_time": 1234567890.0
}
```

#### `POST /syscall/sense`
```json
{
  "actor_qaddr": {...},
  "region": {
    "center": {"x": 0.0, "y": 0.0, "z": 0.0, "tau": 1234567890.0},
    "radius": 5.0
  },
  "filters": {
    "orbital_class": "io",
    "min_n": 1,
    "max_n": 3
  }
}
```

**Response:**
```json
{
  "success": true,
  "entities": [
    {
      "entity_id": "uuid-string",
      "qaddr": {...},
      "pose": {...},
      "distance": 2.5
    }
  ]
}
```

#### `POST /syscall/emit`
```json
{
  "actor_qaddr": {...},
  "event": "@event.index_sync",
  "field_deltas": {
    "kappa": 0.1,
    "lambda": 0.2,
    "rho": 0.05
  },
  "fact": {
    "entity_id": "uuid-string",
    "op": "emit",
    "valid_from": "2025-01-27T00:00:00Z",
    "valid_to": null
  }
}
```

### 1.3 Rust HTTP Server Implementation

**File:** `packages/quaternion_kernel/src/http_server.rs`

**Dependencies:**
```toml
[dependencies]
axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

**Implementation:**
```rust
use axum::{Router, routing::post, Json};
use crate::kernel::{Kernel, EntityId, EntityState};
use crate::{QAddr, DualQuat};

pub struct KernelServer {
    kernel: Kernel,
}

impl KernelServer {
    pub fn new() -> Self {
        Self {
            kernel: Kernel::new(),
        }
    }
    
    pub async fn handle_place(
        &mut self,
        Json(request): Json<PlaceRequest>,
    ) -> Result<Json<PlaceResponse>, String> {
        // Convert request to kernel types
        let actor_qaddr = request.actor_qaddr.into();
        let entity_state = request.entity_state.into();
        
        // Call kernel syscall
        self.kernel.place(
            &actor_qaddr,
            request.entity_id,
            entity_state,
        )?;
        
        Ok(Json(PlaceResponse {
            success: true,
            entity_id: request.entity_id,
            qaddr: entity_state.addr.into(),
            selection_rules: SelectionRulesResponse {
                delta_n: 0,
                delta_l: true,
                delta_m: true,
                delta_s: true,
                ok: true,
            },
        }))
    }
    
    // Similar handlers for move, sense, emit
}

pub fn create_router() -> Router {
    Router::new()
        .route("/syscall/place", post(handle_place))
        .route("/syscall/move", post(handle_move))
        .route("/syscall/sense", post(handle_sense))
        .route("/syscall/emit", post(handle_emit))
}
```

### 1.4 TypeScript Client Implementation

**File:** `packages/plix/src/runtime/rust-kernel-bridge.ts`

```typescript
export class RustKernelBridge implements KernelBridge {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:8080/api/kernel/v1') {
    this.baseUrl = baseUrl;
  }
  
  async placeSyscall(
    actorQAddr: QAddrLiteral,
    entityId: string,
    entityState: EntityState
  ): Promise<SyscallResult> {
    const response = await fetch(`${this.baseUrl}/syscall/place`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        actor_qaddr: actorQAddr,
        entity_id: entityId,
        entity_state: entityState,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Kernel syscall failed: ${response.statusText}`);
    }
    
    return await response.json();
  }
  
  // Similar methods for move, sense, emit
}
```

### 1.5 FFI Alternative (Future Optimization)

**If HTTP latency becomes an issue:**

**File:** `packages/quaternion_kernel/src/ffi_bridge.rs`

```rust
use std::os::raw::{c_char, c_void};

#[no_mangle]
pub extern "C" fn kernel_place(
    actor_qaddr_json: *const c_char,
    entity_id: u128,
    entity_state_json: *const c_char,
    result_json: *mut c_char,
    result_len: usize,
) -> i32 {
    // Parse JSON, call kernel, serialize result
    // Return 0 on success, -1 on error
}
```

**Node.js FFI Binding:**
```typescript
import ffi from 'ffi-napi';

const kernelLib = ffi.Library('./quaternion_kernel', {
  kernel_place: ['int', ['string', 'uint64', 'string', 'string', 'int']],
});
```

---

## 2. Real GPU Field Solver

### 2.1 Architecture Overview

**Purpose:** Update κ/λ/ρ fields on GPU for efficient field diffusion

**Technology Stack:**
- **WebGPU** (for browser/Node.js)
- **CUDA/OpenCL** (for native GPU compute)
- **Compute Shaders** (for field updates)

### 2.2 Field Representation

**GPU Texture Layout:**
- **κ (kappa) field:** RGBA32F texture (4 channels for 4D spacetime)
- **λ (lambda) field:** RGBA32F texture (attention/energy)
- **ρ (rho) field:** RGBA32F texture (density/mass)

**Texture Dimensions:**
- **Width × Height:** 1024 × 1024 (1M cells)
- **Depth:** 64 slices (for 4D spacetime)
- **Format:** RGBA32F (128 bits per cell)

### 2.3 Field Update Pipeline

**Compute Shader (GLSL/WGSL):**

```wgsl
// Field update compute shader
@group(0) @binding(0) var<storage, read_write> kappa_field: array<vec4<f32>>;
@group(0) @binding(1) var<storage, read_write> lambda_field: array<vec4<f32>>;
@group(0) @binding(2) var<storage, read_write> rho_field: array<vec4<f32>>;
@group(0) @binding(3) var<uniform> field_params: FieldParams;

struct FieldParams {
    delta_tau: f32,
    diffusion_rate: f32,
    decay_rate: f32,
}

@compute @workgroup_size(64)
fn update_fields(@builtin(global_invocation_id) id: vec3<u32>) {
    let index = id.x + id.y * 1024u + id.z * 1024u * 1024u;
    
    // Gaussian diffusion (4 passes)
    let kappa = kappa_field[index];
    let lambda = lambda_field[index];
    let rho = rho_field[index];
    
    // Apply diffusion
    let kappa_new = diffuse_gaussian(kappa, field_params.diffusion_rate);
    let lambda_new = diffuse_gaussian(lambda, field_params.diffusion_rate);
    let rho_new = diffuse_gaussian(rho, field_params.diffusion_rate);
    
    // Apply decay
    kappa_field[index] = kappa_new * (1.0 - field_params.decay_rate);
    lambda_field[index] = lambda_new * (1.0 - field_params.decay_rate);
    rho_field[index] = rho_new * (1.0 - field_params.decay_rate);
}

fn diffuse_gaussian(value: vec4<f32>, rate: f32) -> vec4<f32> {
    // Gaussian blur kernel (simplified)
    return value * rate;
}
```

### 2.4 Field Solver Service

**File:** `packages/quaternion_kernel/src/field_solver.rs`

```rust
pub struct FieldSolver {
    device: wgpu::Device,
    queue: wgpu::Queue,
    kappa_texture: wgpu::Texture,
    lambda_texture: wgpu::Texture,
    rho_texture: wgpu::Texture,
    compute_pipeline: wgpu::ComputePipeline,
}

impl FieldSolver {
    pub fn new(device: wgpu::Device, queue: wgpu::Queue) -> Self {
        // Create textures
        // Create compute pipeline
        // Initialize fields
    }
    
    pub fn splat_field(
        &mut self,
        position: Vec4,
        kappa_delta: f32,
        lambda_delta: f32,
        rho_delta: f32,
    ) {
        // Convert position to texture coordinates
        // Update field textures
        // Dispatch compute shader
    }
    
    pub fn update_fields(&mut self, delta_tau: f32) {
        // Dispatch compute shader for field diffusion
        // Apply Gaussian blur (4 passes)
        // Apply decay
    }
    
    pub fn get_field_value(&self, position: Vec4) -> (f32, f32, f32) {
        // Sample textures at position
        // Return (kappa, lambda, rho)
    }
}
```

### 2.5 TypeScript Integration

**File:** `packages/plix/src/runtime/gpu-field-solver.ts`

```typescript
export class GPUFieldSolver implements FieldSolver {
  private device: GPUDevice;
  private computePipeline: GPUComputePipeline;
  private kappaTexture: GPUTexture;
  private lambdaTexture: GPUTexture;
  private rhoTexture: GPUTexture;
  
  async initialize(): Promise<void> {
    // Initialize WebGPU device
    // Create textures
    // Create compute pipeline
  }
  
  async splatField(
    position: Vec4,
    kappaDelta: number,
    lambdaDelta: number,
    rhoDelta: number
  ): Promise<void> {
    // Convert position to texture coordinates
    // Update field textures
    // Dispatch compute shader
  }
  
  async updateFields(deltaTau: number): Promise<void> {
    // Dispatch compute shader for field diffusion
  }
  
  async getFieldValue(position: Vec4): Promise<[number, number, number]> {
    // Sample textures at position
    // Return [kappa, lambda, rho]
  }
}
```

---

## 3. Real CMC Storage Client

### 3.1 CMC API Overview

**Base URL:** `http://localhost:5000/api/cmc/v1`

**Key Operations:**
- `POST /atoms` - Create atom
- `GET /atoms/:id` - Retrieve atom
- `PUT /atoms/:id` - Update atom
- `POST /atoms/query` - Query atoms

### 3.2 Entity Storage Schema

**CMC Atom Structure:**
```json
{
  "modality": "quaternion_entity",
  "content": {
    "inline": {
      "entity_id": "uuid-string",
      "qaddr": {
        "n": 1,
        "l": "io",
        "m": 1234,
        "s": "act",
        "morton_key": 1234567890,
        "s3_bin": 5678
      },
      "pose": {
        "rotation": {...},
        "translation": {...}
      },
      "fields": {
        "kappa": 0.1,
        "lambda": 0.2,
        "rho": 0.05
      }
    }
  },
  "tags": {
    "entity_id": "uuid-string",
    "qaddr_n": "1",
    "qaddr_l": "io",
    "morton_key": "1234567890"
  },
  "metadata": {
    "created_at": "2025-01-27T00:00:00Z",
    "valid_from": "2025-01-27T00:00:00Z",
    "valid_to": null
  }
}
```

### 3.3 CMC Client Implementation

**File:** `packages/plix/src/runtime/cmc-storage-client.ts`

```typescript
import { MemoryStore } from '@aimos/cmc-service';

export class CMCStorageClient implements CMCStorage {
  private client: MemoryStore;
  
  constructor(basePath: string) {
    this.client = new MemoryStore(basePath);
  }
  
  async storeEntity(
    entityId: string,
    qaddr: QAddrLiteral,
    state: EntityState
  ): Promise<void> {
    const atomCreate = {
      modality: 'quaternion_entity',
      content: {
        inline: {
          entity_id: entityId,
          qaddr: qaddr,
          pose: state.pose,
          fields: state.fields,
        },
      },
      tags: {
        entity_id: entityId,
        qaddr_n: qaddr.n.toString(),
        qaddr_l: qaddr.l,
        morton_key: qaddr.morton_key.toString(),
      },
      metadata: {
        created_at: new Date().toISOString(),
        valid_from: new Date().toISOString(),
        valid_to: null,
      },
    };
    
    await this.client.create_atom(atomCreate);
  }
  
  async retrieveEntity(entityId: string): Promise<EntityState | null> {
    const atom = await this.client.get_atom(entityId);
    
    if (!atom || atom.modality !== 'quaternion_entity') {
      return null;
    }
    
    const content = atom.content.inline;
    return {
      qaddr: content.qaddr,
      pose: content.pose,
      fields: content.fields,
    };
  }
  
  async queryByQAddr(qaddr: QAddrLiteral): Promise<string[]> {
    const results = await this.client.query_atoms({
      tags: {
        qaddr_n: qaddr.n.toString(),
        qaddr_l: qaddr.l,
        morton_key: qaddr.morton_key.toString(),
      },
    });
    
    return results.map(atom => atom.content.inline.entity_id);
  }
  
  async queryByRegion(region: Region): Promise<string[]> {
    // Query CMC for entities in region
    // Use morton_key range queries
    const minMorton = morton4d_encode(region.min);
    const maxMorton = morton4d_encode(region.max);
    
    const results = await this.client.query_atoms({
      tags: {
        morton_key_min: minMorton.toString(),
        morton_key_max: maxMorton.toString(),
      },
    });
    
    return results.map(atom => atom.content.inline.entity_id);
  }
}
```

---

## 4. Real HHNI/SEG/CMC Clients

### 4.1 HHNI Client (Tag Resolution)

**Purpose:** Resolve PLIX tags to QAddr using HHNI hierarchical index

**File:** `packages/plix/src/compiler/hhni-client.ts`

```typescript
import { HHNIIndexer } from '@aimos/hhni';

export class HHNIClient {
  private indexer: HHNIIndexer;
  
  constructor() {
    this.indexer = new HHNIIndexer();
  }
  
  async resolveTagToQAddr(tag: string): Promise<QAddrLiteral | null> {
    // Query HHNI for tag
    const results = await this.indexer.retrieve({
      query: tag,
      k: 1,
      filters: {
        modality: 'quaternion_entity',
      },
    });
    
    if (results.length === 0) {
      return null;
    }
    
    // Extract QAddr from top result
    const atom = results[0].atom;
    if (atom.modality === 'quaternion_entity') {
      return atom.content.inline.qaddr;
    }
    
    return null;
  }
}
```

### 4.2 SEG Client (Provenance Tracking)

**Purpose:** Track entity lineage and relationships

**File:** `packages/plix/src/runtime/seg-client.ts`

```typescript
import { SEGraph } from '@aimos/seg';

export class SEGClient {
  private graph: SEGraph;
  
  constructor() {
    this.graph = new SEGraph();
  }
  
  async trackEntityCreation(
    entityId: string,
    qaddr: QAddrLiteral,
    sourceTag: string
  ): Promise<void> {
    // Create entity node
    const entity = {
      type: 'quaternion_entity',
      name: entityId,
      attributes: {
        qaddr: qaddr,
        source_tag: sourceTag,
      },
    };
    
    await this.graph.add_entity(entity);
    
    // Create relation to source
    if (sourceTag) {
      const relation = {
        source_id: sourceTag,
        target_id: entityId,
        relation_type: 'derives_from',
        confidence: 1.0,
      };
      
      await this.graph.add_relation(relation);
    }
  }
  
  async trackSyscall(
    entityId: string,
    syscallType: 'place' | 'move' | 'sense' | 'emit',
    result: SyscallResult
  ): Promise<void> {
    // Create evidence node
    const evidence = {
      content: `${syscallType} syscall on ${entityId}`,
      source: 'quaternion_kernel',
      confidence: result.success ? 1.0 : 0.0,
    };
    
    await this.graph.add_evidence(evidence);
  }
}
```

### 4.3 CMC Client (Bitemporal Storage)

**Already covered in Section 3** - CMC client handles bitemporal storage

---

## 5. Integration Architecture

### 5.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PLIX Quaternion Runtime                   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Parser     │→ │   Compiler   │→ │   Runtime    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Real System Integrations                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Rust Kernel  │  │ GPU Field    │  │ CMC Storage  │      │
│  │   Bridge     │  │   Solver     │  │   Client     │      │
│  │  (HTTP/FFI)  │  │  (WebGPU)    │  │  (Python)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ HHNI Client  │  │ SEG Client   │  │ CMC Client   │      │
│  │  (Tag Res.)  │  │ (Provenance) │  │ (Bitemporal) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

**Place Syscall Flow:**
1. PLIX text → Parser → AST
2. AST → Compiler → Geometric syscall
3. Compiler → HHNI Client → Resolve tag to QAddr
4. Runtime → Rust Kernel Bridge → Execute `place` syscall
5. Runtime → CMC Storage Client → Store entity
6. Runtime → SEG Client → Track provenance
7. Runtime → GPU Field Solver → Update κ/λ/ρ fields

**Move Syscall Flow:**
1. PLIX text → Parser → AST
2. AST → Compiler → Geometric syscall
3. Runtime → Rust Kernel Bridge → Execute `move` syscall
4. Runtime → CMC Storage Client → Update entity
5. Runtime → SEG Client → Track movement

**Sense Syscall Flow:**
1. PLIX text → Parser → AST
2. AST → Compiler → Geometric syscall
3. Runtime → Rust Kernel Bridge → Execute `sense` syscall
4. Runtime → CMC Storage Client → Query entities by region

**Emit Syscall Flow:**
1. PLIX text → Parser → AST
2. AST → Compiler → Geometric syscall
3. Runtime → Rust Kernel Bridge → Execute `emit` syscall
4. Runtime → GPU Field Solver → Splat κ/λ/ρ fields
5. Runtime → CMC Storage Client → Store bitemporal fact
6. Runtime → SEG Client → Track event

---

## 6. Implementation Roadmap

### Phase 1: Rust Kernel Bridge (Week 1-2)
- [ ] Implement HTTP server (axum)
- [ ] Create API endpoints (place, move, sense, emit)
- [ ] Implement TypeScript client
- [ ] Add error handling and validation
- [ ] Write integration tests

### Phase 2: CMC Storage Client (Week 3)
- [ ] Implement CMC client wrapper
- [ ] Create entity storage schema
- [ ] Implement query methods
- [ ] Add bitemporal support
- [ ] Write integration tests

### Phase 3: HHNI/SEG Clients (Week 4)
- [ ] Implement HHNI client for tag resolution
- [ ] Implement SEG client for provenance tracking
- [ ] Integrate with compiler
- [ ] Write integration tests

### Phase 4: GPU Field Solver (Week 5-6)
- [ ] Implement WebGPU field solver
- [ ] Create compute shaders
- [ ] Implement field splatting
- [ ] Implement field diffusion
- [ ] Write integration tests

### Phase 5: End-to-End Integration (Week 7)
- [ ] Integrate all components
- [ ] End-to-end tests
- [ ] Performance optimization
- [ ] Documentation

---

## 7. Testing Strategy

### 7.1 Unit Tests
- Test each client independently
- Mock external dependencies
- Test error handling

### 7.2 Integration Tests
- Test client → service communication
- Test data serialization/deserialization
- Test error propagation

### 7.3 End-to-End Tests
- Test full PLIX → Kernel → Storage pipeline
- Test field solver integration
- Test provenance tracking

### 7.4 Performance Tests
- Measure HTTP latency
- Measure GPU compute throughput
- Measure storage query performance

---

## 8. Error Handling

### 8.1 Kernel Bridge Errors
- **Network errors:** Retry with exponential backoff
- **Validation errors:** Return detailed error messages
- **Kernel errors:** Propagate selection rule violations

### 8.2 Storage Errors
- **Storage failures:** Retry with exponential backoff
- **Query failures:** Return empty results with error log
- **Bitemporal conflicts:** Resolve using VIF witnesses

### 8.3 GPU Errors
- **Device errors:** Fallback to CPU computation
- **Shader errors:** Log and skip field update
- **Memory errors:** Reduce texture resolution

---

## 9. Performance Considerations

### 9.1 Kernel Bridge
- **HTTP latency:** ~5-50ms per syscall
- **FFI latency:** <1ms per syscall (if optimized)
- **Batch operations:** Reduce round-trips

### 9.2 GPU Field Solver
- **Field update:** ~16ms per frame (60 FPS target)
- **Field splatting:** ~1ms per splat
- **Memory usage:** ~512MB for 1024×1024×64 textures

### 9.3 Storage
- **Storage latency:** ~1-10ms per operation
- **Query latency:** ~5-50ms per query
- **Bitemporal overhead:** ~10% storage increase

---

## 10. Security Considerations

### 10.1 Kernel Bridge
- **Authentication:** JWT tokens for API access
- **Authorization:** QAddr-based privilege checks
- **Rate limiting:** Prevent DoS attacks

### 10.2 Storage
- **Data encryption:** Encrypt sensitive entity data
- **Access control:** Tag-based access policies
- **Audit logging:** Log all storage operations

### 10.3 GPU
- **Shader validation:** Validate compute shaders
- **Memory limits:** Prevent GPU memory exhaustion
- **Sandboxing:** Isolate GPU compute from host

---

**Status:** 📋 **PLANNING COMPLETE**  
**Next:** Begin Phase 1 implementation (Rust Kernel Bridge) 🚀

