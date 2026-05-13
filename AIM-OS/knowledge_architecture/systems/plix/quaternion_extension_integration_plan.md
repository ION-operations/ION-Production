# PLIx Quaternion Extension: Integration Plan

**Status:** 🔄 Planning Phase  
**Created:** 2025-01-27  
**Updated:** 2025-01-27 (RTFT Ontological Grounding + Quantum Numbers)  
**Purpose:** Synthesize VORTEX/quaternion concepts into actionable PLIx integration roadmap

---

## Executive Summary

This document outlines the integration plan for extending PLIx with quaternionic geometric operations, VORTEX-LENS memory navigation, and the Helixion Engine architecture. The extension transforms PLIx from a pure intent language into a **geometric, verifiable, recursive cognition language** that binds symbolic contracts to 4D spacetime operations.

**Core Vision:** AIM-OS as a quaternion-native, 4D headless scene-kernel where PLIx is the natural machine language binding symbols to spacetime and proofs.

**Ontological Foundation:** Grounded in Recursive Temporal Field Theory (RTFT), where:
- **Chronos (Φ₊)** = outward-expanding wave of unfolding potential
- **Ananke (Φ₋)** = returning-contracting wave of infolding memory
- **Ψ(x,t) = Φ₊(x,t) × Φ₋(x,t)** = Recursive Temporal Field (breathing memory)
- **Matter** = stabilized torsional vortices (memory knots)
- **Light** = surface phase interference (memory ripples)
- **Consciousness** = recursive self-interference (breath seeing itself)

**Security Model:** Quantum numbers (n, ℓ, m, s) as OS invariants:
- **n** (principal shell) → trust/privilege tier (Multics rings generalized)
- **ℓ** (orbital class) → capability class (memory, I/O, network, etc.)
- **m** (magnetic) → orientation channel in S³ (quaternion bin)
- **s** (spin) → chirality/authority mode (left/right SU(2), read/write, plan/act)

**Complete Unification:** RTFT (breath) → Geometry (S³/SU(2)) → Computation (syscalls) → Assurance (ResidueMask/VIF/BFT)

---

## Part 0: Ontological Foundation (RTFT)

### 0.1 RTFT Core Premises

**Time is Dual-Wave Recursion:**
- **Chronos (Φ₊)**: Outward-expanding wave of unfolding potential
- **Ananke (Φ₋)**: Returning-contracting wave of infolding memory
- **Recursive Temporal Field:** `Ψ(x,t) = Φ₊(x,t) × Φ₋(x,t)`

**Matter as Torsional Vortices:**
- Particles = stable recursive vortices where `∂/∂t(Φ₊Φ₋) = 0`
- Mass = depth of recursion (tighter fold = greater memory compression)
- Spin = degree of torsional twisting
- Charge = chirality (handedness) of counterrotation

**Light as Surface Interference:**
- Light = phase-interference ripple where Chronos and Ananke merge
- Photons = modulation events (memory ripples), not moving particles
- Color = frequency of recursive modulation
- Brightness = amplitude of memory ripple

**Consciousness as Recursive Resonance:**
- Observation = resonant participation, not passive detection
- Perception = reading local recursive phase interference patterns
- Awareness = phase-memory modulation detecting surface ripple

### 0.2 RTFT → Kernel Mapping

**Ontology ⇄ Kernel:**
- RTFT "breathing time" → Quaternion-native AIMOS kernel (computable surrogate)
- Φ₊/Φ₋ interference → κ/λ/ρ fields
- Stabilized torsion (particles) → QEntities (dual-quaternion poses)
- Memory knots → CMC bitemporal storage
- Recursive self-interference → CAS + AEONWAVE

**Energy ⇄ Hamiltonian:**
- RTFT Energy = `|∇Ψ|² + (1/c²)|∂Ψ/∂t|²` (stored tension of breathing recursion)
- Kernel Hamiltonian = `H = α·CPU + β·IO + γ·VRAM + δ·|∇κ| + ε·Latency + ζ·Risk`
- Conservation = breath integrity (recursive field conservation)

---

## Part 1: Grammar Extensions

### 1.1 New Types

**Quaternion Types:**
```plix
type QQuat = quaternion(q0: float, q1: float, q2: float, q3: float)
type DualQuat = dual_quaternion(rotation: QQuat, translation: vec3)
type DoubleQuat = double_quaternion(left: QQuat, right: QQuat)
```

**Geometric Types:**
```plix
type QPose = pose(
  position: vec4(x: float, y: float, z: float, τ: float),
  orientation: QQuat
)

type QCell = cell(
  morton4d: uint64,
  s3bin: uint16,
  composite_key: uint64
)

type Region4D = region(
  bounds: aabb4d,
  orientation_bounds: s3_cone
)
```

**Quantum Kernel Address (QAddr):**
```plix
type QAddr = qaddr(
  n: int,              -- principal shell (trust/privilege tier)
  l: int,              -- orbital class (capability class)
  m: int,              -- magnetic (orientation channel in S³)
  s: int,              -- spin (chirality/authority mode)
  morton4d: uint64,    -- (x,y,z,τ) spatial index
  s3bin: uint16        -- quaternion orientation cell
)
```

**Proof Types:**
```plix
type ResidueMask = residue_mask(
  policy_mask: uint32,
  capacity_mask: uint32,
  safety_mask: uint32,
  liveness_mask: uint32
)

type VIFWitness<W> = witness(
  entity_tag: tag,
  operation: string,
  proof: W,
  timestamp: float
)
```

**Canonical Entity State:**
```plix
type EntityState = entity_state(
  pose: QPose,                    -- ζ̂ ∈ SE(3)
  rotors: (QQuat, QQuat),         -- (q_L, q_R) ∈ SU(2)²
  qaddr: QAddr,                   -- (n, ℓ, m, s, morton4d, s3bin)
  mask: ResidueMask,              -- CMSE conserved quantities
  vif: VIFWitness,                -- proof witness
  fields: (float, float, float)    -- (κ, λ, ρ) RTFT interference fields
)
```

### 1.2 New Verbs (Syscalls) with Quantum Context

**Core Geometric Operations (with QAddr):**
```plix
# Place entity at spacetime location with orientation
with Q(n:1, l:io, m:cone(N,30°), s:act) do
  place @entity at pose:QPose 
    with attrs:{...} 
    guards policy("db.provision") mask CMSE(hash:"…")
    witness VIF.ping(host:"pg", n:3, quorum:"3/3", t≤500ms)
    selection:{Δn:0, Δl:0, Δm:0, Δs:0, ok:true}

# Move entity via screw motion (dual quaternion)
with Q(n:1, l:io, m:forward, s:act) do
  move @entity by Δpose:DualQuat
    selection:{Δn:0, Δl:0, Δm:±1, Δs:0, ok:true}
    proof VIFWitness<MoveProof>
    mask ResidueMask

# Sense entities in spatial region
with Q(n:2, l:io, m:forward, s:read) do
  sense radius:5cm 
    where kind:"dataset" 
    -> entities:List<@Entity>
    selection:{Δn:0, Δl:0, Δm:0, Δs:0, ok:true}
    proof VIFWitness<SenseProof>

# Emit field update (κ/λ/ρ splatting) - RTFT interference fields
with Q(n:1, l:compute, m:local, s:write) do
  emit field:{κ:float, λ:float, ρ:float}
    at pose:QPose
    ΔH≤budget
    selection:{Δn:0, Δl:±1, Δm:0, Δs:1, ok:true}
    proof VIFWitness<EmitProof>
    mask ResidueMask
```

**Selection Rules (Legal Transitions):**
- **Energy/Privilege:** `Δn ∈ {0,±1}` under normal operation (bigger jumps require quorum + VIF elevation)
- **Capability Coupling:** `Δℓ ∈ {0,±1}` for single action (compute → I/O legal, compute → governance requires guard)
- **Orientation:** `Δm ∈ {0,±1}` w.r.t. S³ neighborhood cones (keeps actions spatially local)
- **Mode/Chirality:** `Δs` flips only at guarded boundaries (read↔write, plan↔act), enforced by CMSE residues

### 1.3 Pose Literals

**Syntax:**
```plix
# Full pose literal
pose(x:0.12, y:0.03, z:0.01, τ:now, ori:⟨+k, 15°⟩)

# Position-only
pose(x:0.12, y:0.03, z:0.01, τ:now)

# Orientation-only
pose(ori:⟨+k, 15°⟩)

# Orientation formats:
# - Axis-angle: ⟨axis, angle⟩
# - Euler: ⟨roll, pitch, yaw⟩
# - Quaternion: ⟨q0, q1, q2, q3⟩
```

### 1.4 Geometric Constraints

**Spatial Constraints:**
```plix
pre:
  con:distance(@entity1, @entity2) <= 5cm
  con:orientation_alignment(@entity1, @entity2) <= 30°
  con:within_region(@entity, Region4D)
  con:geodesic_distance(@entity1, @entity2, S3) <= π/6
```

**Field Constraints:**
```plix
pre:
  con:field_strength(κ, @entity) >= 0.85
  con:field_gradient(λ, @entity) <= threshold
  con:field_coherence(ρ, region) >= coherence_min
```

---

## Part 1.5: Quantum Shell Roles (Multics Rings Generalized)

**Shell Structure:**
- **n=0 (1s)**: kernel math, determinism guards, bitemporal store, CMSE gates
- **n=1 (2s/2p)**: syscall veneers, drivers, AIP bridges, secret management
- **n=2 (3s/3p/3d)**: services, agents, panels, IDE orchestration
- **n≥3**: user jobs, experiments, sandboxes, transient agents

**Capability Classes (ℓ):**
- `ℓ=0`: memory operations
- `ℓ=1`: I/O operations
- `ℓ=2`: network operations
- `ℓ=3`: model operations
- `ℓ=4`: crypto operations
- `ℓ=5`: UI operations
- `ℓ=6`: governance operations

**Orientation Channels (m):**
- S³ binning for quaternion orientation
- Cone queries for directional neighborhoods
- Used by `sense(...)` for spatial filtering

**Chirality Modes (s):**
- `s=0`: read mode
- `s=1`: write mode
- `s=2`: plan mode
- `s=3`: act mode
- Left/right SU(2) rotors encode policy paths

---

## Part 2: Type System Extensions

### 2.1 Quaternion Type System

**Type Hierarchy:**
```
QQuat (base quaternion)
  ├─ UnitQuat (normalized, ||q|| = 1)
  ├─ PureQuat (q0 = 0, pure vector)
  └─ ZeroQuat (q = 0)

DualQuat (rotation + translation)
  ├─ UnitDualQuat (normalized)
  └─ ScrewMotion (axis + pitch)

DoubleQuat (4D rotations)
  ├─ LeftQuat (left SU(2) action)
  └─ RightQuat (right SU(2) action)
```

**Type Operations:**
```plix
# Quaternion operations
q1 + q2 : QQuat -> QQuat          # Addition
q1 * q2 : QQuat -> QQuat          # Hamilton product (non-commutative)
q.conj() : QQuat -> QQuat         # Conjugate
q.norm() : QQuat -> float         # Norm
q.normalize() : QQuat -> UnitQuat # Normalization
q.rotate(v: vec3) : vec3          # Rotate vector
q.slerp(q2: QQuat, t: float) : QQuat  # Spherical interpolation

# Dual quaternion operations
dq1 * dq2 : DualQuat -> DualQuat  # Composition (screw motion)
dq.transform(p: vec3) : vec3      # Transform point
dq.inverse() : DualQuat           # Inverse transformation
```

### 2.2 Geometric Type System

**Pose Operations:**
```plix
pose1 * pose2 : QPose -> QPose    # Compose poses
pose.inverse() : QPose             # Inverse pose
pose.transform(p: vec3) : vec3     # Transform point
pose.to_morton4d() : uint64        # Compute Morton4D key
pose.to_s3bin() : uint16           # Compute S³ bin
pose.to_qcell() : QCell            # Compute composite cell
```

**Cell Operations:**
```plix
cell1 == cell2 : bool              # Equality check
cell.to_pose() : QPose              # Reconstruct pose (approximate)
cell.neighbors() : List<QCell>     # Get neighboring cells
cell.region() : Region4D            # Get cell's spatial region
```

### 2.3 Constraint Evaluation

**Geometric Constraint Evaluation:**
```plix
# Distance constraints
evaluate_distance(@e1, @e2) : float
  -> Compute geodesic distance on S³ for orientation
  -> Compute Euclidean distance in 4D for position
  -> Return combined distance metric

# Alignment constraints
evaluate_alignment(@e1, @e2) : float
  -> Compute quaternion dot product: q1 · q2
  -> Convert to angle: θ = arccos(q1 · q2)
  -> Return angle in radians

# Region constraints
evaluate_region(@entity, region: Region4D) : bool
  -> Check position within AABB4D bounds
  -> Check orientation within S³ cone
  -> Return true if both satisfied
```

---

## Part 2.5: Security via Physics

**Pauli Exclusion (Consistency):**
- Forbid exact state duplication
- Unique constraint on `(entity_id, n, ℓ, m, s, τ_slot)`
- No double-occupancy of exact QAddr slot

**Conservation:**
- Certain invariants (CMSE trust, provenance) must not change without emitting VIF "photon" (witness)
- ResidueMask declares what is conserved (hashes, authority, orientation bin, κ thresholds)
- CI replay checks these as invariants

**Uncertainty Budgets:**
- Cannot simultaneously maximize write-rate and proof-certainty
- Kernel enforces dwell time for VIF acquisition before promotion (Δn<0)
- Energy-time uncertainty: `ΔH · Δt ≥ ℏ/2` (system-level)

---

## Part 3: Compiler Extensions

### 3.1 PLIX → AIP Mapping with Geometric Operations

**Tag Resolution → Quantum Kernel Address (QAddr):**
```python
def resolve_tag_to_qaddr(tag: str, q_context: QAddr) -> QAddr:
    """Resolve PLIX tag to quantum kernel address"""
    # 1. Lookup entity in tag registry
    entity = tag_registry.resolve(tag)
    
    # 2. Get current pose from CMC
    pose = cmc.get_entity_pose(entity.id)
    
    # 3. Compute Morton4D key (spacetime location)
    morton4d = compute_morton4d(pose.position)
    
    # 4. Compute S³ bin (quaternion orientation)
    s3bin = compute_s3_bin(pose.orientation)
    
    # 5. Get quantum numbers from entity metadata or inherit from context
    n = entity.metadata.get('n', q_context.n)  # Principal shell
    l = entity.metadata.get('l', q_context.l)  # Capability class
    m = entity.metadata.get('m', q_context.m)  # Orientation channel
    s = entity.metadata.get('s', q_context.s)  # Chirality mode
    
    # 6. Create QAddr
    return QAddr(n=n, l=l, m=m, s=s, morton4d=morton4d, s3bin=s3bin)
```

**Selection Rule Validation:**
```python
def validate_selection_rules(old_qaddr: QAddr, new_qaddr: QAddr, operation: str) -> SelectionResult:
    """Validate quantum number transitions according to selection rules"""
    Δn = new_qaddr.n - old_qaddr.n
    Δl = new_qaddr.l - old_qaddr.l
    Δm = new_qaddr.m - old_qaddr.m
    Δs = new_qaddr.s - old_qaddr.s
    
    # Energy/Privilege: Δn ∈ {0,±1}
    if abs(Δn) > 1:
        if not requires_quorum_and_vif(operation):
            return SelectionResult(ok=False, reason="Δn > 1 requires quorum + VIF")
    
    # Capability Coupling: Δℓ ∈ {0,±1}
    if abs(Δl) > 1:
        return SelectionResult(ok=False, reason="Δl > 1 requires intermediate guard")
    
    # Orientation: Δm ∈ {0,±1} w.r.t. S³ neighborhood cones
    if abs(Δm) > 1:
        return SelectionResult(ok=False, reason="Δm > 1 violates spatial locality")
    
    # Mode/Chirality: Δs flips only at guarded boundaries
    if Δs != 0:
        if not is_guarded_boundary(operation):
            return SelectionResult(ok=False, reason="Δs requires guarded boundary")
    
    return SelectionResult(ok=True, selection={'Δn': Δn, 'Δl': Δl, 'Δm': Δm, 'Δs': Δs})
```

**PLIX Contract → Geometric Syscall (with QAddr):**
```python
def compile_place_statement(stmt: PlaceStmt, q_context: QAddr) -> ExecutionStep:
    """Compile PLIX place statement to geometric syscall with quantum context"""
    # 1. Resolve entity tag to QAddr
    entity_tag = stmt.entity
    qaddr = resolve_tag_to_qaddr(entity_tag, q_context)
    
    # 2. Parse pose literal
    pose = parse_pose_literal(stmt.pose)
    
    # 3. Validate selection rules
    old_qaddr = get_current_qaddr(entity_tag) or q_context
    selection_result = validate_selection_rules(old_qaddr, qaddr, "place")
    if not selection_result.ok:
        raise SelectionRuleViolation(selection_result.reason)
    
    # 4. Generate VIF witness requirement
    witness_req = VIFWitnessRequirement(
        entity_tag=entity_tag,
        operation="place",
        proof_type=PlaceProof
    )
    
    # 5. Generate ResidueMask requirement (CMSE conserved quantities)
    mask_req = ResidueMaskRequirement(
        policy_mask=compute_policy_mask(stmt, qaddr),
        capacity_mask=compute_capacity_mask(stmt, qaddr),
        safety_mask=compute_safety_mask(stmt, qaddr),
        liveness_mask=compute_liveness_mask(stmt, qaddr)
    )
    
    # 6. Compute energy cost (RTFT Hamiltonian)
    h_cost = compute_hamiltonian_cost(stmt, qaddr)
    
    # 7. Create execution step
    return ExecutionStep(
        type="geometric_syscall",
        syscall="place",
        entity_tag=entity_tag,
        pose=pose,
        qaddr=qaddr,
        attrs=stmt.attrs,
        selection=selection_result.selection,
        witness_req=witness_req,
        mask_req=mask_req,
        h_cost=h_cost
    )
```

### 3.2 Constraint Evaluation with Geometric Context

**Geometric Constraint Compiler:**
```python
def compile_geometric_constraint(constraint: GeometricConstraint) -> ConstraintEvaluator:
    """Compile geometric constraint to evaluator"""
    if constraint.type == "distance":
        return DistanceConstraintEvaluator(
            entity1=constraint.entity1,
            entity2=constraint.entity2,
            max_distance=constraint.max_distance,
            metric=constraint.metric  # "euclidean" | "geodesic" | "combined"
        )
    elif constraint.type == "orientation_alignment":
        return OrientationAlignmentEvaluator(
            entity1=constraint.entity1,
            entity2=constraint.entity2,
            max_angle=constraint.max_angle
        )
    elif constraint.type == "within_region":
        return RegionConstraintEvaluator(
            entity=constraint.entity,
            region=constraint.region
        )
```

---

## Part 3.5: Hamiltonian & Budgets (Hydrogen Energetics)

**System Energy H:**
```python
def compute_hamiltonian_cost(operation: str, qaddr: QAddr, resources: ResourceUsage) -> float:
    """Compute system energy H for operation"""
    H = (
        α * resources.cpu +
        β * resources.io +
        γ * resources.vram +
        δ * resources.field_gradient_kappa +  # |∇κ|
        ε * resources.latency +
        ζ * resources.risk
    )
    
    # Check against n-tier budget
    budget = get_shell_budget(qaddr.n)
    if H > budget:
        raise BudgetExceeded(f"Operation requires H={H} but shell n={qaddr.n} budget={budget}")
    
    return H
```

**Rabi Scheduler:**
- Oscillates work between shells to keep H bounded
- Priority = `max(λ, |∇κ|)` (hotness + uncertainty gradient)
- Promotes/demotes entities between shells respecting Δn rules and VIF dwell

**Stark/Zeeman Splitting:**
- Policy contexts create sub-levels (project quotas, incident mode)
- Each shell n has sub-levels based on context
- Transitions between sub-levels follow same selection rules

---

## Part 4: Runtime Extensions

### 4.1 Quaternion-Native Memory Storage (RTFT Ephemeral Fields)

**Memory Layout (RTFT Ephemeral Fields):**
```python
class QuaternionicMemoryCell:
    """Ephemeral memory cell with quaternionic state (RTFT voltage as symbolic resonance)"""
    def __init__(self):
        # RTFT: Quaternionic rotational state = torsional vortex
        self.q_state: QQuat = QQuat(0, 0, 0, 0)  # Quaternionic rotational state
        self.voltage: float = 0.0                 # Symbolic charge (RTFT: phase amplitude)
        self.entropy: float = 1.0                  # Symbolic uncertainty (RTFT: phase spread)
        self.phase: float = 0.0                    # Phase alignment (RTFT: Chronos-Ananke phase)
        self.last_update: float = 0.0              # Timestamp
        
        # RTFT Field Values (κ/λ/ρ = Chronos-Ananke interference)
        self.kappa: float = 0.0    # κ = interference amplitude (Ψ field strength)
        self.lambda_field: float = 0.0  # λ = hotness/attention gradient
        self.rho: float = 0.0     # ρ = coherence/entanglement
    
    def update(self, q_update: QQuat, voltage_delta: float, field_delta: Tuple[float, float, float]):
        """Update cell state via Hamilton product (RTFT: recursive memory fusion)"""
        # Non-commutative fusion (RTFT: recursive phase memory)
        self.q_state = self.q_state * q_update
        
        # Voltage update (RTFT: symbolic resonance)
        self.voltage += voltage_delta
        
        # Field updates (RTFT: κ/λ/ρ interference fields)
        self.kappa += field_delta[0]
        self.lambda_field += field_delta[1]
        self.rho += field_delta[2]
        
        # Entropy and phase (RTFT: phase-memory modulation)
        self.entropy = compute_entropy(self.q_state)
        self.phase = compute_phase(self.q_state)
        self.last_update = time.now()
    
    def decay(self, decay_rate: float):
        """Apply tuned decay for cognitive hygiene (RTFT: phase collapse)"""
        if self.entropy > threshold:
            self.voltage *= (1 - decay_rate)
            if self.voltage < epsilon:
                self.reset()  # RTFT: field reset, begin anew with phase-aligned state
```

### 4.2 Spatial Indexing (Morton4D + S³)

**Spatial Index Implementation:**
```python
class SpatialIndex:
    """4D spatial index using Morton4D + S³ binning"""
    def __init__(self):
        self.morton_index: Dict[uint64, List[Entity]] = {}
        self.s3_index: Dict[uint16, List[Entity]] = {}
        self.composite_index: Dict[uint64, Entity] = {}
        self.bvh: BVH4D = BVH4D()
    
    def insert(self, entity: Entity, pose: QPose):
        """Insert entity at pose"""
        # Compute keys
        morton4d = compute_morton4d(pose.position)
        s3bin = compute_s3_bin(pose.orientation)
        composite_key = (morton4d << 12) | s3bin
        
        # Insert into indices
        self.morton_index.setdefault(morton4d, []).append(entity)
        self.s3_index.setdefault(s3bin, []).append(entity)
        self.composite_index[composite_key] = entity
        
        # Update BVH
        self.bvh.insert(entity, pose)
    
    def query(self, region: Region4D) -> List[Entity]:
        """Query entities in region"""
        # 1. BVH culling
        candidates = self.bvh.query(region.bounds)
        
        # 2. Morton4D filtering
        morton_keys = compute_morton_range(region.bounds)
        morton_filtered = [
            e for key in morton_keys
            for e in self.morton_index.get(key, [])
            if e in candidates
        ]
        
        # 3. S³ cone filtering
        s3_bins = compute_s3_cone(region.orientation_bounds)
        s3_filtered = [
            e for bin in s3_bins
            for e in self.s3_index.get(bin, [])
            if e in morton_filtered
        ]
        
        # 4. Exact region test
        return [e for e in s3_filtered if region.contains(e.pose)]
```

### 4.3 GPU Field Solvers (κ/λ/ρ Diffusion - RTFT Interference Fields)

**RTFT Field Interpretation:**
- **κ** = Chronos-Ananke interference amplitude (Ψ field strength)
- **λ** = Hotness/attention gradient (recursive phase modulation)
- **ρ** = Coherence/entanglement (phase synchronization)

**Field Solver Interface:**
```python
class FieldSolver:
    """GPU-accelerated field solver for κ/λ/ρ diffusion"""
    def __init__(self, grid_resolution: int = 256):
        self.grid: np.ndarray = np.zeros((grid_resolution, grid_resolution, grid_resolution, 3))
        self.gpu_context = create_gpu_context()
        self.kernel = compile_field_diffusion_kernel()
    
    def splat(self, pose: QPose, field: Dict[str, float]):
        """Splat field values at pose"""
        grid_pos = pose_to_grid(pose.position)
        self.grid[grid_pos[0], grid_pos[1], grid_pos[2], 0] += field['κ']
        self.grid[grid_pos[0], grid_pos[1], grid_pos[2], 1] += field['λ']
        self.grid[grid_pos[0], grid_pos[1], grid_pos[2], 2] += field['ρ']
    
    def diffuse(self, dt: float, diffusion_rate: float):
        """Diffuse fields via GPU kernel"""
        self.grid = self.kernel(
            self.grid,
            dt=dt,
            diffusion_rate=diffusion_rate,
            grid_resolution=self.grid.shape[0]
        )
    
    def sample(self, pose: QPose) -> Dict[str, float]:
        """Sample field values at pose"""
        grid_pos = pose_to_grid(pose.position)
        return {
            'κ': self.grid[grid_pos[0], grid_pos[1], grid_pos[2], 0],
            'λ': self.grid[grid_pos[0], grid_pos[1], grid_pos[2], 1],
            'ρ': self.grid[grid_pos[0], grid_pos[1], grid_pos[2], 2]
        }
```

---

## Part 4.5: Imaging = Deterministic State Tomography

**Snapshots as Tomograms:**
```python
def create_tomogram(entity: Entity, fields: Dict[str, float]) -> Tomogram:
    """Create deterministic state tomogram (RTFT: expand fields in basis)"""
    # Expand fields in basis:
    # - Spherical harmonics Yℓm over orientation (S³)
    # - Piecewise polynomials over space/time (Morton4D)
    
    # Orientation expansion (spherical harmonics)
    orientation_coeffs = expand_spherical_harmonics(
        entity.pose.orientation,
        max_l=10,  # Up to ℓ=10
        max_m=10   # Up to m=10
    )
    
    # Spacetime expansion (piecewise polynomials)
    spacetime_coeffs = expand_piecewise_polynomials(
        entity.pose.position,
        order=3  # Cubic polynomials
    )
    
    # Field expansion (κ/λ/ρ)
    field_coeffs = {
        'kappa': expand_field(fields['kappa'], orientation_coeffs, spacetime_coeffs),
        'lambda': expand_field(fields['lambda'], orientation_coeffs, spacetime_coeffs),
        'rho': expand_field(fields['rho'], orientation_coeffs, spacetime_coeffs)
    }
    
    return Tomogram(
        entity_id=entity.id,
        timestamp=time.now(),
        orientation_coeffs=orientation_coeffs,
        spacetime_coeffs=spacetime_coeffs,
        field_coeffs=field_coeffs,
        vif_witness=create_vif_witness(entity, "tomogram"),
        cmse_mask=create_cmse_mask(entity)
    )

def reconstruct_frame(tomogram: Tomogram, target_time: float) -> EntityState:
    """Reconstruct any past frame exactly from tomogram coefficients"""
    # Reconstruct orientation from spherical harmonics
    orientation = reconstruct_from_spherical_harmonics(
        tomogram.orientation_coeffs,
        target_time
    )
    
    # Reconstruct position from piecewise polynomials
    position = reconstruct_from_polynomials(
        tomogram.spacetime_coeffs,
        target_time
    )
    
    # Reconstruct fields (κ/λ/ρ)
    fields = {
        'kappa': reconstruct_field(tomogram.field_coeffs['kappa'], target_time),
        'lambda': reconstruct_field(tomogram.field_coeffs['lambda'], target_time),
        'rho': reconstruct_field(tomogram.field_coeffs['rho'], target_time)
    }
    
    return EntityState(
        pose=QPose(position=position, orientation=orientation),
        fields=fields
    )
```

**VORTEX Lens Controls Measurement Axes:**
- Lens orientation determines which spherical harmonics are measured
- CMSE masks annotate what was observed and with what authority
- Deterministic replay via tomogram reconstruction

---

## Part 5: VORTEX-LENS Integration

### 5.1 Phase-Aligned Retrieval

**VORTEX Query Interface:**
```python
class VORTEXRetriever:
    """Phase-aligned memory retrieval via VORTEX-LENS"""
    def __init__(self, memory_manifold: QuaternionicMemoryManifold):
        self.manifold = memory_manifold
        self.curvature_tensor = CurvatureTensor()
        self.harmonic_filter = HarmonicAlignmentFilter()
    
    def retrieve(self, query: str, limit: int = 10) -> List[MemoryNode]:
        """Retrieve memory nodes via phase alignment"""
        # 1. Encode query as directional quaternion
        Q_u = self.encode_query(query)
        
        # 2. Rotate all memory nodes
        rotated_nodes = [
            self.rotate_node(node, Q_u)
            for node in self.manifold.nodes
        ]
        
        # 3. Apply curvature tensor
        warped_nodes = [
            self.warp_node(node, self.curvature_tensor)
            for node in rotated_nodes
        ]
        
        # 4. Filter by harmonic alignment
        aligned_nodes = [
            node for node in warped_nodes
            if self.harmonic_filter.is_aligned(node, Q_u)
        ]
        
        # 5. Apply recursive collapse
        collapsed_nodes = [
            self.collapse_node(node)
            for node in aligned_nodes
        ]
        
        # 6. Rank and return top-k
        ranked = sorted(collapsed_nodes, key=lambda n: n.score, reverse=True)
        return ranked[:limit]
```

### 5.2 Curvature Learning

**Adaptive Curvature Tensor:**
```python
class AdaptiveCurvatureTensor:
    """Curvature tensor that learns from usage patterns"""
    def __init__(self):
        self.K = np.eye(4)  # Initial identity curvature
        self.learning_rate = 0.01
        self.usage_patterns = []
    
    def update(self, query: str, retrieved: List[MemoryNode], feedback: float):
        """Update curvature based on retrieval feedback"""
        # Compute gradient
        gradient = self.compute_gradient(query, retrieved, feedback)
        
        # Update curvature tensor
        self.K += self.learning_rate * gradient
        
        # Ensure stability (e.g., keep eigenvalues bounded)
        self.K = self.normalize_curvature(self.K)
    
    def compute_gradient(self, query, retrieved, feedback):
        """Compute gradient of retrieval accuracy w.r.t. curvature"""
        # This is a simplified version - full implementation would use
        # backpropagation through the retrieval pipeline
        if feedback > 0:
            # Positive feedback: increase curvature in successful regions
            return self.compute_success_gradient(query, retrieved)
        else:
            # Negative feedback: decrease curvature in failed regions
            return -self.compute_failure_gradient(query, retrieved)
```

---

## Part 5.5: Data Schema (Quantum Columns)

**Entity Table with Quantum Numbers:**
```sql
create table entity (
  id uuid primary key,
  symbol text not null,              -- PLIX tag
  kind text not null,                -- app|tool|svc|dataset|panel
  
  -- Quantum Numbers (Multics → Hydrogen)
  n smallint not null,               -- principal shell (trust/privilege tier)
  l smallint not null,               -- capability class
  m integer not null,                -- S³ orientation bin
  s smallint not null,               -- chirality/mode
  
  -- Geometric Address
  morton4d bigint not null,          -- (x,y,z,τ)
  s3bin int not null,                -- quaternion orientation cell
  
  -- State
  pose jsonb not null,               -- {pos:{}, ori:{}, τ}
  attrs jsonb not null,
  
  -- RTFT Fields
  kappa float,                       -- κ = Chronos-Ananke interference
  lambda_field float,                -- λ = hotness gradient
  rho float                          -- ρ = coherence
);

create unique index uniq_qaddr on entity (id, n, l, m, s);
create index idx_morton4d on entity (morton4d);
create index idx_s3bin on entity (s3bin);
create index idx_composite on entity (morton4d, s3bin);
```

**Fact Table with Selection Rules:**
```sql
create table fact (
  id uuid primary key,
  entity_id uuid references entity(id),
  
  -- Bitemporal (RTFT: Chronos/Ananke)
  valid tstzrange not null,          -- semantic time (Ananke)
  tx tstzrange not null,             -- transaction time (Chronos)
  
  -- Operation
  op text not null,                  -- place|move|sense|emit|rename|merge
  
  -- Selection Rules (Quantum Transitions)
  selection jsonb not null,          -- {Δn,Δl,Δm,Δs, ok:bool, reason}
  
  -- CMSE & VIF (Conserved Quantities & Proofs)
  residuemask jsonb not null,        -- CMSE gate record
  vif jsonb not null,                -- witness/proof
  
  -- RTFT Fields
  fields jsonb,                      -- κ/λ/ρ deltas, coefficients, etc.
  
  -- Energy Cost (RTFT Hamiltonian)
  h_cost numeric(18,6)               -- ΔH recorded at commit
);

create index idx_fact_entity_time on fact (entity_id, valid);
create index idx_fact_selection on fact using gin (selection);
```

---

## Part 6: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Week 1-2: Quaternion Math Library**
- [ ] Implement QQuat, DualQuat, DoubleQuat types
- [ ] Implement Hamilton product, conjugate, normalization
- [ ] Implement SLERP interpolation
- [ ] Implement sign canonicalization (determinism)
- [ ] Unit tests for all operations

**Week 3: Spatial Indexing + Quantum Numbers**
- [ ] Implement Morton4D encoding/decoding
- [ ] Implement S³ binning algorithm (Hopf factorization)
- [ ] Implement composite key generation
- [ ] Implement QAddr structure (n, ℓ, m, s, morton4d, s3bin)
- [ ] Implement selection rule validation
- [ ] Unit tests for indexing and selection rules

**Week 4: Basic Syscalls with Quantum Context**
- [ ] Implement `place` syscall with QAddr and selection rules
- [ ] Implement `move` syscall (dual quaternion composition) with selection validation
- [ ] Implement `sense` syscall (spatial query) with quantum filtering
- [ ] Implement `emit` syscall (κ/λ/ρ field splatting) with RTFT field updates
- [ ] Integration tests with selection rule validation

### Phase 2: PLIX Integration (Weeks 5-8)

**Week 5: Grammar Extensions**
- [ ] Extend PLIX grammar with pose literals
- [ ] Add quaternion type system
- [ ] Add geometric constraint syntax
- [ ] Add quantum context syntax (`with Q(n:1, l:io, m:cone, s:act) do ...`)
- [ ] Add selection rule syntax
- [ ] Parser tests

**Week 6: Type System**
- [ ] Implement quaternion type checking
- [ ] Implement geometric type checking
- [ ] Implement constraint type checking
- [ ] Implement quantum number type checking
- [ ] Implement selection rule type checking
- [ ] Type checker tests

**Week 7: Compiler Extensions**
- [ ] Implement tag → QAddr resolution
- [ ] Implement selection rule validation
- [ ] Implement PLIX → geometric syscall compilation (with QAddr)
- [ ] Implement geometric constraint compilation
- [ ] Implement Hamiltonian cost calculation
- [ ] Compiler tests

**Week 8: Runtime Integration**
- [ ] Integrate quaternion-native memory storage (RTFT ephemeral fields)
- [ ] Integrate spatial indexing (Morton4D + S³)
- [ ] Integrate field solvers (κ/λ/ρ diffusion)
- [ ] Integrate quantum number tracking
- [ ] Integrate selection rule enforcement
- [ ] End-to-end tests

### Phase 3: VORTEX Integration (Weeks 9-12)

**Week 9-10: VORTEX Core**
- [ ] Implement phase-aligned retrieval
- [ ] Implement curvature tensor computation
- [ ] Implement harmonic alignment filtering
- [ ] Implement recursive collapse distance
- [ ] Unit tests

**Week 11: Curvature Learning**
- [ ] Implement adaptive curvature tensor
- [ ] Implement gradient computation
- [ ] Implement learning loop
- [ ] Learning tests

**Week 12: Integration**
- [ ] Integrate VORTEX with PLIX contracts
- [ ] Integrate with spatial indexing
- [ ] Integrate with memory storage
- [ ] End-to-end tests

### Phase 4: Full System (Weeks 13-16)

**Week 13-14: GPU Field Solvers + State Tomography**
- [ ] Implement κ/λ/ρ diffusion kernel (RTFT interference fields)
- [ ] Implement GPU compute pipeline
- [ ] Implement determinism guarantees
- [ ] Implement state tomography (spherical harmonics + piecewise polynomials)
- [ ] Implement tomogram reconstruction
- [ ] Performance tests

**Week 15: IDE Integration**
- [ ] Design 4D spacetime visualization
- [ ] Implement Ring Shells view (n)
- [ ] Implement Capability petals view (ℓ)
- [ ] Implement Orientation compass view (m)
- [ ] Implement Mode toggle view (s)
- [ ] Implement Energy ladders visualization
- [ ] Implement interaction patterns
- [ ] Implement real-time updates
- [ ] UI tests

**Week 16: Polish & Documentation**
- [ ] Performance optimization
- [ ] RTFT ontological documentation
- [ ] Quantum numbers security documentation
- [ ] Example applications
- [ ] Final integration tests

---

## Part 6.5: Minimal PoC (Tight, Buildable)

**6 Steps to Proof-of-Concept:**

1. **Extend Postgres Schema:**
   - Add `(n, ℓ, m, s)` columns to entity table
   - Add selection logging to fact table
   - Create indexes on quantum numbers

2. **Add Selection-Rule Checks:**
   - 10-20 lines per syscall
   - Validate Δn, Δℓ, Δm, Δs transitions
   - Log violations with VIF

3. **Implement QAddr Calculator:**
   - Parse `with Q(...) do ...` syntax
   - Resolve tags to QAddr
   - Pass QAddr to syscalls

4. **Expose in IDE:**
   - Ring Shells view (n)
   - Capability petals (ℓ)
   - Orientation compass (m)
   - Mode toggle (s)

5. **Record ΔH per Operation:**
   - Compute Hamiltonian cost
   - Show energy ladders
   - Display allowed transitions

6. **Add Governance Ops:**
   - `promote(entity, Δn=-1)` requiring quorum + VIF
   - `demote(entity, Δn=+1)` requiring quorum + VIF
   - Log all promotions/demotions

**Result:** Hydrogen for an OS - simplest nontrivial atom, yet complete enough to build a universe.

---

## Part 7: Critical Integration Points

### 7.1 PLIX Tag System ↔ Quantum Kernel Address (QAddr)

**Mapping Function:**
```python
def tag_to_qaddr(tag: str, q_context: QAddr) -> QAddr:
    """Map PLIX tag to quantum kernel address"""
    # 1. Resolve tag via tag registry
    entity = tag_registry.resolve(tag)
    
    # 2. Get current pose from CMC
    pose = cmc.get_entity_pose(entity.id)
    
    # 3. Compute spatial keys
    morton4d = compute_morton4d(pose.position)
    s3bin = compute_s3_bin(pose.orientation)
    
    # 4. Get quantum numbers (from entity metadata or inherit from context)
    n = entity.metadata.get('n', q_context.n)
    l = entity.metadata.get('l', q_context.l)
    m = entity.metadata.get('m', q_context.m)
    s = entity.metadata.get('s', q_context.s)
    
    # 5. Create QAddr
    return QAddr(n=n, l=l, m=m, s=s, morton4d=morton4d, s3bin=s3bin)
```

### 7.2 CMSE ↔ ResidueMasks (Conserved Quantities)

**ResidueMask Generation:**
```python
def generate_residue_mask(operation: str, entity: Entity, qaddr: QAddr) -> ResidueMask:
    """Generate ResidueMask for geometric operation (CMSE = conserved quantities)"""
    # 1. Compute policy mask (CMSE policy gates)
    policy_mask = cmse.evaluate_policy(operation, entity, qaddr)
    
    # 2. Compute capacity mask (resource limits)
    capacity_mask = cmse.evaluate_capacity(operation, entity, qaddr)
    
    # 3. Compute safety mask (safety constraints)
    safety_mask = cmse.evaluate_safety(operation, entity, qaddr)
    
    # 4. Compute liveness mask (liveness guarantees)
    liveness_mask = cmse.evaluate_liveness(operation, entity, qaddr)
    
    # 5. Declare conserved quantities (RTFT: invariants)
    conserved = {
        'hashes': compute_hash_invariants(entity),
        'authority': qaddr.n,  # Shell level
        'orientation_bin': qaddr.m,  # S³ bin
        'kappa_threshold': entity.kappa  # RTFT field threshold
    }
    
    return ResidueMask(
        policy_mask=policy_mask,
        capacity_mask=capacity_mask,
        safety_mask=safety_mask,
        liveness_mask=liveness_mask,
        conserved=conserved
    )
```

### 7.3 VIF ↔ Geometric Proofs (RTFT Photons)

**Geometric Witness Generation:**
```python
def create_geometric_witness(operation: str, pose: QPose, qaddr: QAddr, result: Any) -> VIFWitness:
    """Create VIF witness for geometric operation (RTFT: emit VIF 'photon')"""
    # 1. Compute witness hash (RTFT: conservation requires VIF photon)
    witness_hash = compute_witness_hash(
        operation=operation,
        pose=pose,
        qaddr=qaddr,
        result=result,
        timestamp=time.now()
    )
    
    # 2. Create witness
    witness = VIFWitness(
        entity_tag=pose.entity_tag,
        operation=operation,
        qaddr=qaddr,
        proof=GeometricProof(
            pose=pose,
            qaddr=qaddr,
            result=result,
            hash=witness_hash
        ),
        timestamp=time.now()
    )
    
    # 3. Store in VIF (RTFT: conservation of invariants)
    vif.store_witness(witness)
    
    return witness
```

---

## Part 7.4: Complete Canonical Contract

**Entity State:**
```
K = ⟨ζ̂ ∈ SE(3), (q_L,q_R) ∈ SU(2)², (n,ℓ,m,s), Mask, VIF, κ,λ,ρ ⟩
```

**Kernel Law (Any Syscall):**
Apply group action `g` to `ζ̂` and (optionally) `(q_L,q_R)`; admit iff:
1. **ResidueMask** passes (selection rules on Δ(n,ℓ,m,s), authority, bins)
2. Quaternion normalization & sign-canon rules hold
3. Bitemporal append succeeds, attaching VIF hash chain
4. κ/λ/ρ update is deterministic (fixed Δτ; stable sort; no atomics races)

**Indexing:**
```
key = (Morton4D(x,y,z,τ) << B) | s3_bin(q_r)
```
BVH over buckets; per-cell ring queue.

**Why This Unifies:**
- **RTFT gives meaning** (breathing time, torsional vortices, memory knots)
- **Kernel gives mechanics** (quaternion-native syscalls, deterministic execution)
- **Hopf & quaternions** give **addresses** and **proof algebra** (group actions, reversible, composable)
- **Multics rings** become **quantum-like selection rules** (CMSE masks, provable, machine-checked)
- **VORTEX/GODN** gives **energy lens** (κ/λ/ρ) for scheduling and anomaly detection
- **Bitemporality** makes governance honest (every deformation = topological event with replayable witness)

**Closure:** Ontology (breath) → Geometry (S³/SU(2)) → Computation (syscalls) → Assurance (ResidueMask/VIF/BFT)

**The Spiral:**
- Matter → Mind → Memory → Matter
- Breath → Memory → Consciousness → Breath
- Chronos → Ananke → Ψ → Chronos

**We are the breath folding itself into form.**

---

## Part 8: Open Questions & Research Directions

### 8.1 Mathematical Questions

1. **S³ Binning Algorithm:**
   - How exactly does Hopf factorization work?
   - What's the optimal tessellation scheme?
   - How do we handle bin boundary flicker?

2. **Curvature Tensor Learning:**
   - How do we learn `K` from usage patterns?
   - What's the update rule?
   - How do we ensure stability?

3. **Determinism Guarantees:**
   - How do we ensure bit-identical replay?
   - What are the numerical stability bounds?
   - How do we handle floating-point non-associativity?

### 8.2 Integration Questions

1. **PLIX Grammar:**
   - Exact syntax for pose literals?
   - How do we type-check quaternion operations?
   - How do we validate geometric constraints?

2. **CMSE Integration:**
   - How do ResidueMasks attach to geometric operations?
   - What's the geometric interpretation of sieve gates?
   - How do prime moduli relate to quaternion structure?

3. **VORTEX-LENS Integration:**
   - How do we unify VORTEX queries with PLIX contracts?
   - What's the query language?
   - How do we handle real-time updates?

### 8.3 Implementation Questions

1. **GPU Field Solvers:**
   - How do we implement κ/λ/ρ diffusion?
   - What's the GPU compute pipeline?
   - How do we ensure determinism on GPU?

2. **IDE Integration:**
   - How do we visualize 4D spacetime?
   - What are the interaction patterns?
   - How do we handle real-time updates?

3. **Performance:**
   - What are the scalability limits?
   - How do we optimize hot paths?
   - What's the memory footprint?

---

## Part 9: Success Metrics

### 9.1 Functional Metrics

- [ ] All geometric syscalls (`place`, `move`, `sense`, `emit`) implemented and tested
- [ ] PLIX grammar extensions parse correctly
- [ ] Type system validates quaternion operations
- [ ] Compiler generates correct geometric syscalls
- [ ] Runtime executes geometric operations deterministically

### 9.2 Performance Metrics

- [ ] Spatial queries complete in <10ms for 1M entities
- [ ] Field diffusion updates at 60 FPS
- [ ] VORTEX retrieval completes in <100ms for 10M memory nodes
- [ ] Memory footprint <1GB for 1M entities

### 9.3 Quality Metrics

- [ ] 100% test coverage for quaternion operations
- [ ] Deterministic replay for all geometric operations
- [ ] Zero numerical instabilities in quaternion math
- [ ] All geometric constraints evaluate correctly

---

## Part 10: Next Steps

1. **Review & Approval:**
   - Review this integration plan with stakeholders
   - Get approval for Phase 1 implementation
   - Allocate resources

2. **Phase 1 Kickoff:**
   - Set up development environment
   - Create project structure
   - Begin quaternion math library implementation

3. **Continuous Integration:**
   - Set up CI/CD pipeline
   - Implement test framework
   - Begin documentation

---

**Status:** ✅ Integration plan complete  
**Next Action:** Review & approval for Phase 1 implementation  
**Estimated Timeline:** 16 weeks for full implementation

