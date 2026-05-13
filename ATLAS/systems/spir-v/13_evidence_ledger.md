---
atlas_package: system
system_slug: spir-v
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Evidence ledger

| claim_id | claim | tier | locator | notes |
|----------|-------|------|---------|-------|
| sp-001 | Khronos SPIR-V registry/spec | DOCUMENTED | `src-khronos-spirv` | |
| sp-002 | LLVM SPIR-V usage documentation | DOCUMENTED | `src-llvm-spirv` | |
| sp-003 | Vulkan/OpenCL consumption (ecosystem) | DOCUMENTED | `src-wiki-spirv` | survey |
| sp-004 | OpenCL 2.1+ SPIR-V IL track | DOCUMENTED | `opencl` package `src-khronos-opencl` | cross-pkg |
| sp-005 | Vulkan shader modules consume SPIR-V | DOCUMENTED | `vulkan` package `src-vulkan-registry` | cross-pkg |
| sp-006 | OpenGL SPIR-V ingest (4.6-era extension track) | DOCUMENTED | `opengl` package `src-opengl-registry` | cross-pkg |
| sp-007 | SYCL / LLVM paths may consume SPIR-V on some GPU targets | INFERRED | `sycl` package `src-sycl-registry` | impl-dependent |
| sp-008 | Level Zero SPIR-V programming guide (kernels/modules) | DOCUMENTED | `level-zero` package `src-lz-spirv-guide` | cross-pkg |
| sp-009 | WebGPU WGSL → SPIR-V lowering on Vulkan backends (ecosystem) | INFERRED | `webgpu` package `src-w3c-wgsl` | impl-dependent |
