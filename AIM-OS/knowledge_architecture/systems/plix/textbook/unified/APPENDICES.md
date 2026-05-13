# Unified Textbook Appendices

**Appendix A:** Glossary  
**Appendix B:** Bibliography  
**Appendix C:** Index  
**Appendix D:** Notation Reference  
**Appendix E:** Implementation Resources

---

## Appendix A: Glossary

### A

**APOE (Autonomous Plan Orchestration Engine):** Execution engine for PLIx plans  
**AST (Abstract Syntax Tree):** Parsed representation of PLIx intent  
**Authority Tier:** Security level in evidence system (S, A, B, C, D)

### C

**CMC (Context Memory Core):** Bitemporal storage system  
**CMSE (Capability-Mode-State-Effect):** Security enforcement framework  
**Composite Key:** Combined Morton4D + S³ bin (80-bit entity address)  
**Core-PLIx:** Minimal kernel language (formal semantics)

### D

**Dual Quaternion:** 8-number representation of rigid 3D transformation (SE(3))  
**Double Quaternion:** Pair of quaternions for 4D rotations (SO(4))

### E

**Evidence DAG:** Directed acyclic graph of provenance evidence  
**Effect Rows:** Row-polymorphic type for tracking operation effects

### H

**Hamiltonian (H):** System energy for pricing kernel operations  
**HHNI (Hierarchical Hypergraph Neural Index):** Semantic indexing system  
**Hopf Fibration:** Mathematical structure S³ → S² × S¹ for orientation indexing

### I

**IRPlan:** Intermediate representation for execution plans

### M

**Morton4D Key:** 64-bit spatiotemporal index from (x,y,z,τ)

### P

**Pauli Exclusion:** No two entities in exact same quantum state  
**PLIx:** Programmatic-Linguistic Interface (pure intent language)

### Q

**QAddr:** Quantum kernel address with (n,ℓ,m,s) + spatial indices  
**QEntity:** Entity with QPose + QAddr  
**QPose:** Position + orientation (quaternion) + time  
**Quaternion:** 4-number complex extension for representing 3D rotations

### R

**RTFT (Recursive Temporal Field Theory):** Ontological substrate theory

### S

**S³ Binning:** Orientation indexing using unit quaternion sphere  
**ScLERP:** Screw Linear Interpolation for dual quaternions  
**SEG (Shared Evidence Graph):** Provenance tracking system  
**Selection Rules:** Hydrogen-like transition constraints (Δn, Δℓ, Δm, Δs)  
**SLERP:** Spherical Linear Interpolation for quaternions

### V

**VIF (Verifiable Integrity Framework):** Cryptographic witness system  
**VORTEX-LENS:** Geometric-symbolic memory navigation framework

---

## Appendix B: Bibliography

### Foundational Papers

1. Hamilton, W. R. (1843). "On Quaternions" *Proceedings of the Royal Irish Academy*

2. Hopf, H. (1931). "Über die Abbildungen der dreidimensionalen Sphäre auf die Kugelfläche" *Mathematische Annalen*

3. Organick, E. I. (1972). *The Multics System: An Examination of Its Structure* MIT Press

### Quaternion Mathematics

4. Kuipers, J. B. (1999). *Quaternions and Rotation Sequences* Princeton University Press

5. Hanson, A. J. (2006). *Visualizing Quaternions* Morgan Kaufmann

6. Kenwright, B. (2012). "A Beginners Guide to Dual-Quaternions" *WSCG Conference*

### Spatial Indexing

7. Morton, G. M. (1966). "A Computer Oriented Geodetic Data Base and a New Technique in File Sequencing" IBM Technical Report

8. Samet, H. (2006). *Foundations of Multidimensional and Metric Data Structures* Morgan Kaufmann

### Formal Verification

9. Lamport, L. (2002). *Specifying Systems: The TLA+ Language and Tools* Addison-Wesley

10. Jackson, D. (2012). *Software Abstractions: Logic, Language, and Analysis* MIT Press

### Provenance and Evidence

11. Moreau, L., et al. (2013). "PROV-DM: The PROV Data Model" W3C Recommendation

12. OpenLineage Project (2021). "OpenLineage Specification" https://openlineage.io

### AIM-OS Related

13. [Internal] CMC L0-L4 Documentation (`knowledge_architecture/systems/cmc/`)

14. [Internal] VIF L0-L4 Documentation (`knowledge_architecture/systems/vif/`)

15. [Internal] APOE L0-L4 Documentation (`knowledge_architecture/systems/apoe/`)

---

## Appendix C: Index

### A

- Abstract Syntax Tree → Ch 5, 17, 26
- Action resolution → Ch 7, 25, 26.4
- Authority tiers → Ch 9, 14, 24.2

### B

- Backoff strategies → Ch 12, 25
- Bandit objective → Research/router_math
- BVH (Bounding Volume Hierarchy) → Ch 23.6
- Bitemporal storage → Ch 14, 24.4, 27.3

### C

- Cache coherence → Ch 23.7
- Capability class (ℓ) → Ch 24.2.2
- Compensation → Ch 13, 25.3, 26
- Composite keys → Ch 23.4, 24.7
- Confidence aggregation → Ch 11, 24.5, 26.3
- Constraint replay → Ch 16, Research/verifier
- Core-PLIx → Research/formal_semantics

### D

- Denotational semantics → Research/formal_semantics
- Deterministic replay → Ch 21.5, 25.9
- Dual quaternions → Ch 22.2, 25.3

### E

- Effect rows → Ch 19, Research/type_system
- Energy levels (Hamiltonian) → Ch 24.5
- Entity creation (place) → Ch 25.1
- Evidence DAG → Ch 14, 16, Research/evidence_schema

### F

- Field solver (κ/λ/ρ) → Ch 27.6
- Frustum culling → Ch 23.10.2

### G

- Geometric operations → Ch 21.3, 25, 26.2
- Governance operations → Ch 24.10

### H

- Hamiltonian cost → Ch 24.5
- Hash chain verification → Ch 16, Research/verifier
- HHNI integration → Ch 27.4
- Hopf fibration → Ch 22.6, 23.3

### I

- Idempotence → Ch 12, Research/durable_execution
- IRPlan → Ch 17, 18, Research/compilation_pipeline

### K

- Kernel syscalls → Ch 21.3, 25

### M

- Magnetic number (m) → Ch 24.2.2
- Morton4D keys → Ch 23.2
- Move operation → Ch 25.3

### O

- OPA backend → Ch 17, Research/compilation_pipeline
- Operational semantics → Research/formal_semantics
- Orbital class (ℓ) → Ch 24.2.2

### P

- Pauli exclusion → Ch 24.4.1, 25.1
- Place operation → Ch 25.1
- Principal shell (n) → Ch 24.2.2
- PROV mapping → Ch 14, 27.5

### Q

- QAddr structure → Ch 24.2.3
- QEntity → Ch 22.7.3
- QPose → Ch 22.7.1
- Quantum context → Ch 21.4.1, 26.2
- Quantum numbers → Ch 24
- Quaternions → Ch 22

### R

- Rabi scheduler → Ch 24.6.1
- Range queries → Ch 23.5.2
- Retry strategies → Ch 12, 25
- RTFT ontology → Ch 21.8, 24

### S

- S³ binning → Ch 22.6, 23.3
- Saga compensation → Ch 13, Research/durable_execution
- ScLERP → Ch 22.2.4
- Selection rules → Ch 24.3
- Sense operation → Ch 25.4
- Sign canonicalization → Ch 22.4
- SLERP → Ch 22.5.1
- Soundness theorems → Research/formal_semantics
- Spatial indexing → Ch 23
- Spin (s) → Ch 24.2.2
- Subdistribution monad → Research/formal_semantics

### T

- Tag resolution → Ch 15, 26.4, 27.4
- TLA+ backend → Ch 17, Research/compilation_pipeline
- Type checker → Ch 19, 26.3

### V

- VIF witnesses → Ch 14, 21.5.4, 25.7
- VORTEX integration → Ch 21.8

---

## Appendix D: Notation Reference

### Mathematical Notation

- **ℍ:** Quaternions (Hamilton's notation)
- **S³:** Unit quaternion sphere (3-sphere)
- **S²:** Unit vector sphere (2-sphere)
- **S¹:** Circle (1-sphere)
- **SE(3):** Special Euclidean group (rigid 3D transformations)
- **SO(3):** Special Orthogonal group (3D rotations)
- **SO(4):** Special Orthogonal group (4D rotations)
- **SU(2):** Special Unitary group (quaternions)

### PLIx Notation

- **@entity:** Entity reference
- **ent:tag:** Entity tag
- **act:action:** Action tag
- **cap:capability:** Capability tag
- **w:witness:** Witness tag
- **${variable}:** Variable interpolation

### Kernel Notation

- **QAddr:** Quantum kernel address
- **QPose:** Position + orientation + time
- **ΔH:** Hamiltonian cost delta
- **Δn, Δℓ, Δm, Δs:** Quantum number transitions
- **κ, λ, ρ:** Confidence/hotness/density fields

---

## Appendix E: Implementation Resources

### Source Code Locations

**PLIx Language:**
- `packages/plix/` — TypeScript implementation
- `knowledge_architecture/systems/plix/` — Documentation

**Geometric Kernel:**
- `packages/quaternion_kernel/` — Rust implementation
- Tests, benchmarks, HTTP server

**Core-PLIx Reference:**
- `knowledge_architecture/systems/plix/research/implementation/ref-interpreter/` — Reference interpreter
- `knowledge_architecture/systems/plix/research/implementation/verifier/` — Verifier

**Examples:**
- `knowledge_architecture/systems/plix/research/implementation/examples/meeting_room/` — Complete example

### Key Documentation Files

1. `QUATERNION_EXTENSION_RESEARCH_PAPER.md` — Research paper
2. `core_semantics_v01_final.md` — Formal semantics
3. `GRAMMAR_SPECIFICATION_V2.md` — Complete grammar
4. `COMPLETE_TODO_LIST.md` — Implementation roadmap

### Test Suites

**Unit Tests:** 200+ tests across all packages  
**Integration Tests:** 30+ end-to-end tests  
**Benchmarks:** Performance regression suite  
**Property Tests:** Invariant validation

### Build Commands

```bash
# Build everything
cargo build --workspace --release

# Run all tests
cargo test --workspace

# Run benchmarks
cargo bench --workspace

# Generate documentation
cargo doc --workspace --no-deps --open
```

---

**Status:** ✅ **APPENDICES COMPLETE**  
**Total Glossary Terms:** 50+  
**Bibliography Entries:** 15+  
**Index Entries:** 100+  
**Implementation References:** Complete

