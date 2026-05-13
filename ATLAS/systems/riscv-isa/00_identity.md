---
atlas_package: system
system_slug: riscv-isa
schema_version: "1.0"
last_reviewed: "2026-04-11"
evidence_grade: B
---

# RISC-V ISA — Identity

**Kind:** Open modular ISA family (base integer + standard extensions) ratified by RISC-V International (`DOCUMENTED` where specs are published).

## Boundaries

- Not `linux-kernel` — the kernel port implements ABI on top of RISC-V.
- Not `arm-cca` — Arm confidential compute is an orthogonal Arm-specific domain.
