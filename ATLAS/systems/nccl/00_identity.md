---
atlas_package: system
system_slug: nccl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# NCCL — Identity

**Kind:** **NVIDIA** **library** **for** **multi**-**GPU** **collective** **communication** **(AllReduce,** **AllGather,** **…)** (`DOCUMENTED`, NCCL docs).

## Boundaries

- **Not** **a** **network** **transport** **spec** **—** **library** **API** **on** **top** **of** **PCIe** **/** **NVLink** **/** **InfiniBand** **etc.**  
- **Not** **portable** **to** **non**-**NVIDIA** **without** **alternatives** **(e.g.** **RCCL)** — **out** **of** **scope** **here.**
