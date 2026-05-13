---
atlas_package: system
system_slug: libbpf
schema_version: "1.0"
last_reviewed: "2026-04-16"
evidence_grade: B
---

# Scope

## In scope

- **libbpf** **as** **the** **documented** **reference** **userspace** **library** **for** **BPF** **program** **loading,** **maps,** **and** **links** **on** **Linux** (`DOCUMENTED`).  
- **Syscall** **and** **uAPI** **adjacency** **to** **the** **kernel** **BPF** **subsystem** (`DOCUMENTED`).

## Out of scope

- **Alternative** **BPF** **loader** **ecosystems** **(Go**/**Rust**/**other)** **—** **not** **this** **package** **unless** **promoted** **as** **separate** **slugs**.  
- **Non-Linux** **BPF** **stories** **—** **out** **of** **package** **identity**.

## Versioning note

**Upstream** **tags** **and** **kernel** **tree** **bundling** **drive** **visible** **revisions** (`OBSERVED`).
