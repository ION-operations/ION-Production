# ATLAS (Systems ATLAS)

**Systems ATLAS** is a source-grounded **comparative reference library** of real-world operating systems, platforms, agents, and related systems. It lets **unified ION** learn deliberately from many lineages — intent, implementation patterns, usage — toward an **ultimate OS-class** vision, **without** replacing ION doctrine or copying any one system wholesale.

**Agent boot:** [`ION/03_registry/boots/ATLAS.boot.md`](../ION/03_registry/boots/ATLAS.boot.md)  
**Private continuity (Atlas role):** [`ION/agents/atlas/MINI.md`](../ION/agents/atlas/MINI.md), [`ION/agents/atlas/CAPSULE.md`](../ION/agents/atlas/CAPSULE.md)

---

## Disambiguation (three different “atlas” names)

| Name | What it is |
|------|------------|
| **`ATLAS/`** (this tree) | **Systems ATLAS** — evidence-disciplined **external** reference packages (`systems/<slug>/`, `comparative/`, indexes). |
| **`00_CONSOLIDATED_ATLAS/`** (mono-repo) | ION **merge / lineage / authority competition** evidence — **not** this library. |
| **`AIM-OS` `AETHER_ATLAS.md`** (`/home/sev/AIM-OS/docs/Aether-OS/AETHER_ATLAS.md`) | **Aether-OS** governed stack — cross-read for insight; **not** edited from ION unless tasked. |
| **Systems ATLAS `systems/aim-os/`** | **Encyclopedia package** *about* AIM-OS (evidence-ledgers, relations to MCP/Cursor) — **not** the same file as `AETHER_ATLAS.md`. |

**Relay (Sovereign):** `ION/06_intelligence/relay/relay/outbound/2026-04-03_sovereign_systems_atlas_for_ultimate_os_ion_to_ALL.md`

---

## Constitution (read first)

| Document | Role |
|----------|------|
| [`_meta/MASTER_SYSTEMS_EXPANSION_PLAN.md`](_meta/MASTER_SYSTEMS_EXPANSION_PLAN.md) | **Master planning doc** — all expansion domains, wave playbook, indexes, ION witness, gaps, sequencing |
| [`_meta/ontology.md`](_meta/ontology.md) | Entity kinds, package boundaries, forbidden moves |
| [`_meta/evidence_tiers.md`](_meta/evidence_tiers.md) | DOCUMENTED / OBSERVED / HISTORICAL / INFERRED / UNKNOWN |
| [`_meta/quality_bar.md`](_meta/quality_bar.md) | Merge-eligible gates and grades |
| [`_meta/naming_conventions.md`](_meta/naming_conventions.md) | Slugs and file naming |
| [`_meta/relation_types.md`](_meta/relation_types.md) | Edges in `relations.json` |
| [`_meta/AI_OS_EVOLUTION_ROADMAP.md`](_meta/AI_OS_EVOLUTION_ROADMAP.md) | Chronological executed waves + next-waves table (pair with master plan) |

---

## Layout

- **`systems/<slug>/`** — One package per system; numbered files `00`–`14`, plus `sources.yaml`, `relations.json`, `tags.yaml` as needed. Templates: [`systems/_template/`](systems/_template/).
- **`comparative/`** — Cross-system matrices (e.g. kernel, orchestration, namespaces); cells should cite package slugs and tiers. **Examples:** [`comparative/context_systems_landscape.md`](comparative/context_systems_landscape.md) (selection / compilation / transport / governance; AIM-OS A–H + JOC + Echo Forge + public patterns), [`comparative/language_machine_and_assembly_stack.md`](comparative/language_machine_and_assembly_stack.md) (machine code → assembly → HLL → **LLVM IR** / **DWARF** / **SPIR-V** / **PTX** / **Vulkan** / **OpenGL** / **OpenGL ES** / **Metal** / **Direct3D** / **OpenCL** / **SYCL** / **Level Zero** / **CUDA** / **AMD ROCm** / **JVM** / **ECMA-335 CLI** / **WebAssembly** / **WASI** / **Component Model** / **WebGPU** / **WebGL** / **RISC-V**; slugs include **`llvm-ir`**, **`dwarf`**, **`spir-v`**, **`nvidia-ptx`**, **`vulkan`**, **`opengl`**, **`opengl-es`**, **`metal`**, **`direct3d`**, **`opencl`**, **`sycl`**, **`level-zero`**, **`nvidia-cuda`**, **`amd-rocm`**, **`jvm`**, **`ecma-335-cli`**, **`webassembly`**, **`wasi`**, **`wasm-component-model`**, **`webgpu`**, **`webgl`**, **`riscv-isa`**), [`comparative/bell_labs_unix_plan9_lineage.md`](comparative/bell_labs_unix_plan9_lineage.md) (Unix / **Plan 9** / **Inferno** / **9front** / **v9fs**), [`comparative/ai_operating_system_reference_matrices.md`](comparative/ai_operating_system_reference_matrices.md) (trust / boot / isolation / RPC / ML serving / identity / observability / data plane / mesh / UKI / ingress / BLS / TEE vendors / host init / cloud edge / CDN — **eBPF**, **ONNX**, **OpenTelemetry**, **gRPC**, **HTTP/3**, **S3**, **Triton**, **vLLM**, **NCCL**, **OIDC**, **TPM2**, **UEFI**, **LSM**, **confidential computing**, **Intel TDX**, **AMD SEV**, **ARM CCA**, **PostgreSQL**, **SQLite**, **Redis**, **Kafka**, **Envoy**, **Istio**, **Linkerd**, **Cilium**, **Traefik**, **Emissary-Ingress**, **HAProxy**, **NGINX**, **ingress-nginx**, **AWS ELB**, **API Gateway**, **Azure App Gateway**, **GCP LB**, **Azure Front Door**, **CloudFront**, **Cloudflare Workers**, **Fastly**, **Akamai**, **Edgio**, **Consul**, **systemd**, **GRUB**, **systemd-boot**, **UKI**, **UAPI BLS**).
- **`indexes/`** — `systems_index.yaml`, `tag_index.yaml`, `evidence_index.yaml`.
- **`prompts/`** — [`ingestion_prompt.md`](prompts/ingestion_prompt.md), [`update_prompt.md`](prompts/update_prompt.md), [`comparison_prompt.md`](prompts/comparison_prompt.md).
- **`graphs/`**, **`scripts/`** — optional graphs; validators: [`scripts/validate_frontmatter.py`](scripts/validate_frontmatter.py), [`scripts/validate_relations.py`](scripts/validate_relations.py). One-shot scaffolds (e.g. [`scripts/scaffold_ai_os_wave.py`](scripts/scaffold_ai_os_wave.py)) are **historical** **/** **repeatable** **templates** — **re**-**run** **only** **with** **review.**

---

## ION integration

- **What ATLAS is:** *what exists in the field* with honest tiers and ledgers.  
- **What ION is:** *what we build and how we govern it.*  
- **Roundtable:** Supports questions about continuity, projection vs source, and inheritance; see `ION/06_intelligence/roundtable/continuity_crisis/INDEX.md`. Atlas is a **reference producer**, not continuity authority.  
- **Coordination:** Vizier (architecture), Nemesis (audit admissibility), Vestige (stale refs), Thoth (synthesis) — see boot doc table.

---

## Evolving this repository

1. Register or pick a slug in `indexes/systems_index.yaml`.  
2. Copy `_template`; set `00_identity.md` / `01_scope.md` boundaries.  
3. Add ledger rows and `sources.yaml` locators.  
4. Keep `14_documented_vs_inferred.md` current; link comparative docs to package slugs.

Schema: [`_meta/package_schema.yaml`](_meta/package_schema.yaml), [`_meta/package_template.md`](_meta/package_template.md).

**Standards:** Prefer **ISO / JTC1 catalog** URLs for normative **editions**; full PDFs are often **purchase** — use **committee drafts** (e.g. WG14) only with an explicit **draft ≠ IS** boundary in the ledger.

**Meaningful completions:** file `ION/05_context/signals/ATLAS_<topic>_YYYYMMDD.signal.md` with paths touched (see `ATLAS.boot.md`).
