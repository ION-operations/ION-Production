# Systems ATLAS — Master expansion & documentation plan

**Status:** Living (curatorial).  
**Authority:** Atlas role; **not** ION constitutional law.  
**Audience:** Future-you, Atlas sessions, Vizier/Nemesis reviewers, and any contributor extending **`ATLAS/`** as the field-reference library for OS-class and platform design.  
**Companion docs:** [`ontology.md`](ontology.md), [`evidence_tiers.md`](evidence_tiers.md), [`quality_bar.md`](quality_bar.md), [`naming_conventions.md`](naming_conventions.md), [`relation_types.md`](relation_types.md), [`AI_OS_EVOLUTION_ROADMAP.md`](AI_OS_EVOLUTION_ROADMAP.md), [`../README.md`](../README.md).

---

## Table of contents

1. [Purpose and scope](#1-purpose-and-scope)  
2. [Disambiguation and boundaries](#2-disambiguation-and-boundaries)  
3. [Alignment with ION (read-only)](#3-alignment-with-ion-read-only)  
4. [Repository topology](#4-repository-topology)  
5. [Constitutional rules (operational summary)](#5-constitutional-rules-operational-summary)  
6. [Comparative documentation map](#6-comparative-documentation-map)  
7. [Expansion domains — full detail](#7-expansion-domains--full-detail)  
8. [Per-wave execution playbook](#8-per-wave-execution-playbook)  
9. [Indexes, tags, and taxonomy](#9-indexes-tags-and-taxonomy)  
10. [Relations graph discipline](#10-relations-graph-discipline)  
11. [ION witness protocol](#11-ion-witness-protocol)  
12. [Validation and automation](#12-validation-and-automation)  
13. [Open gaps catalog (rolling)](#13-open-gaps-catalog-rolling)  
14. [Suggested sequencing](#14-suggested-sequencing)  
15. [Risk register and anti-patterns](#15-risk-register-and-anti-patterns)  
16. [Appendices](#16-appendices)

---

## 1. Purpose and scope

### 1.1 What Systems ATLAS is

**Systems ATLAS** (`ATLAS/`) is a **source-grounded comparative library** of real operating systems, platforms, runtimes, protocols, and adjacent systems. Its job is to let unified ION **learn deliberately from many lineages** — intent, implementation patterns, failure modes, and operator surfaces — **without** replacing ION doctrine or copying any one system wholesale.

### 1.2 What this master plan is for

This document is the **single planning spine** for continuing “vast” ATLAS growth: it names **every major direction** worth covering, **how** to add packages consistently, **where** comparative text must be updated, and **how** work is witnessed inside ION. Use it when:

- Scoping a new **wave** (one or many packages + comparative + indexes).  
- Deciding whether a candidate belongs as a **new slug** vs an **extension** of an existing package.  
- Avoiding **forbidden merges** (conceptual collisions documented in comparative files).  
- Handing work to another session without losing the **quality bar** and **evidence tier** discipline.

### 1.3 Non-goals

- **Not** merging `00_CONSOLIDATED_ATLAS/` merge-evidence into this tree (different purpose).  
- **Not** silently equating marketing names with architectural kinds.  
- **Not** inventing closed-system internals without DOCUMENTED operator sources.  
- **Not** using ATLAS as the authority for **private agent continuity** (that remains `ION/agents/*/MINI.md` / `CAPSULE.md` per `CONTINUITY_ARCHITECTURE`).

---

## 2. Disambiguation and boundaries

| Name | Role |
|------|------|
| **`ATLAS/`** | External field reference — **this library**. |
| **`00_CONSOLIDATED_ATLAS/`** | ION lineage / authority competition evidence across project roots. |
| **AIM-OS `AETHER_ATLAS.md`** (external repo) | Aether-OS governed stack — **cross-read**; not edited from ION unless tasked. |
| **`systems/aim-os/`** | ATLAS **package about** AIM-OS — not the same artifact as `AETHER_ATLAS.md`. |

**Relay:** `ION/06_intelligence/relay/relay/outbound/2026-04-03_sovereign_systems_atlas_for_ultimate_os_ion_to_ALL.md`

---

## 3. Alignment with ION (read-only)

`ION/PLAN.md` describes horizons: unified ION → **ION-over-MCP** → Chat/Builder → IDE → OS. ATLAS supports this **only as reference**:

| ION horizon | How ATLAS helps |
|-------------|-----------------|
| **Kernel / transactional cognition** | Packages for kernels, LSM, eBPF, schedulers, memory models — **compare**, don’t prescribe ION kernel law. |
| **MCP access layer** | `model-context-protocol`, IDE stacks (`vscode`, `cursor`), **LSP/DAP** separation — wire-level and product-level slugs. |
| **Daemon / runtime** | Orchestrators, init systems, OCI — **field patterns** for dispatch, signals, lifecycle. |
| **Ultimate OS vision** | Broad coverage: libc, linker, boot, TEE, mesh, data plane — **survey** for design options. |

ATLAS **does not** implement ION; it **informs** Vizier/Mason/Nemesis with **merge-eligible**, tier-tagged claims.

---

## 4. Repository topology

```
ATLAS/
├── README.md                 # Entry; constitution table; layout
├── _meta/                    # Ontology, evidence, naming, relations, roadmaps, THIS FILE
├── systems/<slug>/           # One package per system (00–14, sources, relations, tags)
├── systems/_template/        # Scaffold for new packages
├── comparative/              # Cross-system matrices (not per-slug only)
├── indexes/                  # systems_index, tag_index, evidence_index
├── prompts/                  # Ingestion / update / comparison prompts
├── graphs/                   # Optional visual artifacts
└── scripts/                  # Validators; historical scaffold scripts (review before re-run)
```

**Package interior (canonical):** `00_identity.md` … `14_documented_vs_inferred.md`, plus `sources.yaml`, `relations.json`, `tags.yaml` as required by validators and [`package_schema.yaml`](package_schema.yaml).

---

## 5. Constitutional rules (operational summary)

### 5.1 Evidence tiers

Every substantive claim should be recoverable to a **ledger row** or an explicit **UNKNOWN / INFERRED** boundary. Full definitions: [`evidence_tiers.md`](evidence_tiers.md).

### 5.2 Entity kinds and packages

**System** packages are the **unit of curatorial integrity**. Subsystems that are **independently named products** with distinct ABIs often deserve **separate slugs** (e.g. `systemd` vs `systemd-unit-model`). When in doubt: **split identity**, **link with relations**.

### 5.3 Merge-eligible quality

See [`quality_bar.md`](quality_bar.md): structure, identity, ledger coverage, `14_*` honesty, relations, sources, no fabrication. Grades **A–D**; **B** is acceptable for new waves until ledgers are deepened.

### 5.4 Forbidden moves (ontology)

From [`ontology.md`](ontology.md): do not collapse DOCUMENTED and INFERRED without marking; do not treat marketing names as kinds; do not import unverified third-party diagrams as architecture without relabeling.

---

## 6. Comparative documentation map

These files are the **public cross-system** layer. New packages should **touch the comparative set that matches their domain** — not necessarily every file every time.

| File | Primary coverage |
|------|------------------|
| [`comparative/ai_operating_system_reference_matrices.md`](../comparative/ai_operating_system_reference_matrices.md) | Trust, boot, isolation, RPC, ML serving, identity, observability, data plane, mesh, UKI, ingress, BLS, TEE vendors, host init, cloud edge, CDN; **§9** toolchain / libc / MSVC; **§10** open gaps; **Forbidden merges** |
| [`comparative/language_machine_and_assembly_stack.md`](../comparative/language_machine_and_assembly_stack.md) | Machine code → languages → LLVM IR, DWARF, GPU IR, JVM, WASM, **ELF**, **GNU Binutils**, **GCC**, **libcs**, etc. |
| [`comparative/context_systems_landscape.md`](../comparative/context_systems_landscape.md) | Context selection / compilation / transport / governance; AIM-OS A–H; **§8** memory reconciliation; **forbidden merges** vs MCP/RAG |
| [`comparative/bell_labs_unix_plan9_lineage.md`](../comparative/bell_labs_unix_plan9_lineage.md) | Unix / Plan 9 / Inferno / 9front / v9fs lineage |

**Evolution line (matrices §0 companion):** When adding a significant package, append the **signal filename** to the long **Evolution** sentence in `ai_operating_system_reference_matrices.md` so chronological witness stays grep-friendly.

---

## 7. Expansion domains — full detail

Each subsection lists **what to cover**, **typical package types**, **relation patterns**, and **where to reflect** in comparative docs.

### 7.1 Kernels and core OS

**Intent:** ABI boundaries, security models, scheduling, memory, drivers — comparative ground for any “ION OS” thinking.

| Direction | Examples / seeds | Notes |
|-----------|------------------|--------|
| Monolithic vs microkernel patterns | `linux-kernel`, `xnu-macos`, `freebsd` | Add **components** depth in ledgers before new kernel slugs. |
| Research / capability lineage | `multics` (historical) | Preserve **HISTORICAL** tier discipline. |
| Mobile / OEM stacks | `android-aosp` | Relations to `android-bionic`, `linux-kernel`. |
| Hardening interfaces | `linux-security-modules`, `linux-namespaces`, `linux-cgroups`, `linux-capabilities`, `ebpf`, `libbpf`, `landlock`, `seccomp`, `libseccomp` | **`linux-namespaces`** kernel views; **`linux-cgroups`** resource control; **`linux-capabilities`** `CAP_*` privilege sets; **`ebpf`** in-kernel; **`libbpf`** userspace; **`landlock`** unprivileged LSM; **`seccomp`** kernel filters; **`libseccomp`** userspace; tie to observability and policy packages. |

**Comparative:** matrices §1–3 as relevant; `language_machine` only if syscall/toolchain touch.

### 7.2 Init, service management, portable OS trees

**Intent:** How userland bootstraps and long-runs — essential for distro and appliance design.

| Direction | Examples | Open depth |
|-----------|----------|------------|
| systemd grain | `systemd`, `systemd-unit-model`, `systemd-portable`, `systemd-sysext`, `systemd-confext` | Deeper **generator internals** optional (see roadmap). |
| Boot chain | `grub`, `systemd-boot`, `unified-kernel-image`, `uapi-boot-loader-specification` | UKI + BLS law. |
| Declarative OS | `nixos` | `integrates_with` nix-style tooling where seeded. |

**Comparative:** matrices §1 boot rows, §8 host init; roadmap “systemd law grain”.

### 7.3 Containers, images, and orchestration

**Intent:** OCI triad, runtimes, Kubernetes ecosystem — control plane vs data plane.

| Direction | Examples | Relation vocabulary |
|-----------|----------|---------------------|
| OCI | `oci-image-spec`, `oci-distribution-spec`, `oci-runtime-spec` | **Never merge** image vs registry HTTP vs runtime bundle. |
| Union filesystem (Linux layers) | `linux-overlayfs` | **Kernel** **overlay** **driver** **for** **merged** **views** — **not** **`oci-image-spec`** **(manifest/layer** **law)** **alone**. |
| Runtimes | `runc`, `crun`, `containerd`, `docker`, `podman`, `cri-o` | `implements` / `integrates_with` per ontology. |
| Orchestration | `kubernetes`, `nomad`, `apache-mesos`, cloud-managed K8s slugs | **`competes_with`** and **`integrates_with`** cloud control planes. |
| VM workloads on Kubernetes | `kubevirt` | **VM** **CRDs/controllers** **on** **Kubernetes** **with** **QEMU/KVM** **nodes** — **not** **`kubernetes`** **(default** **pod** **model)** **alone,** **`libvirt`** **(node** **daemon)** **alone,** **or** **`qemu`** **(VMM)** **alone.** |
| VM-isolated OCI runtimes | `kata-containers` | **OCI** **runtime** **using** **lightweight** **VMs** **(QEMU/KVM)** — **not** **`runc`** **(namespace** **OCI** **runtime)** **alone,** **`kubevirt`** **(Kubernetes** **VM** **CRDs),** **or** **`qemu`** **(VMM)** **alone.** |
| Userspace-kernel OCI runtime (runsc) | `gvisor` | **OCI** **runtime** **using** **userspace** **syscall** **interposition** — **not** **`runc`** **(namespace** **OCI** **runtime)** **alone,** **`kata-containers`** **(VM-isolated** **OCI),** **or** **`linux-kernel`** **(host** **kernel** **facility)** **alone.** |
| OCI image build (DAG / cache / export) | `buildkit` | **Image** **build** **engine** **emitting** **OCI** **artifacts** — **not** **`oci-runtime-spec`** **(bundle** **execution),** **`runc`** **(low-level** **runtime),** **or** **`oci-image-spec`** **(format** **law)** **alone.** |
| Kubernetes chart packaging | `helm` | **Charts** **and** **releases** **against** **the** **Kubernetes** **API** — **not** **`kubernetes`** **(orchestrator** **itself),** **`oci-runtime-spec`**, **or** **`oci-image-spec`** **alone.** |
| GitOps (continuous reconcile) | `fluxcd` | **Controllers** **reconciling** **Git/OCI** **sources** **into** **Kubernetes** — **not** **`kubernetes`** **(orchestrator** **itself),** **`helm`** **(CLI** **alone),** **or** **`oci-runtime-spec`.** |
| GitOps (Argo CD) | `argo-cd` | **Declarative** **CD** **controller** **with** **Application** **model** — **not** **`kubernetes`** **(orchestrator** **itself),** **`helm`** **(packaging** **alone),** **`fluxcd`** **(other** **GitOps** **controller),** **or** **`oci-runtime-spec`.** |
| Manifest customization (overlays) | `kustomize` | **Base/overlay** **YAML** **composition** — **not** **`kubernetes`** **(orchestrator** **itself),** **`helm`** **(chart** **model** **alone),** **or** **`oci-runtime-spec`.**

**Comparative:** matrices §8; forbidden merges for OCI conflation.

### 7.4 Toolchain, languages, and runtimes

**Intent:** Link/load, debug info, libc, C++ ABI — “law” for anything that compiles.

| Direction | Examples | Ongoing |
|-----------|----------|---------|
| Object / debug formats | `elf`, `dwarf`, `llvm-ir` | Per-ISA **ELF** ABI splits optional (roadmap “toolchain law”). |
| Linkers / compilers | `gnu-binutils`, `llvm-lld`, `gnu-gcc`, `clang` | **`competes_with`** GNU vs LLVM linkers. |
| Linux BPF | `ebpf`, `libbpf` | **`ebpf`** in-kernel bytecode/verifier; **`libbpf`** userspace C loader — not interchangeable. |
| Linux io_uring | `io-uring`, `liburing` | **`io-uring`** kernel async I/O uAPI; **`liburing`** userspace C library — not interchangeable. |
| Linux Landlock | `landlock` | Unprivileged **LSM** **sandbox** **(filesystem** **rules)** — **not** **the** **full** **`linux-security-modules`** **umbrella** **alone**. |
| Linux seccomp | `seccomp`, `libseccomp` | **`seccomp`** kernel **/** **seccomp-filter**; **`libseccomp`** userspace — **not** **interchangeable** **with** **`ebpf`**/**`libbpf`**. |
| Linux namespaces | `linux-namespaces` | **Kernel** **namespace** **types** **(mnt,** **UTS,** **IPC,** **PID,** **net,** **user,** **cgroup,** **time)** — **not** **a** **container** **engine** **or** **OCI** **spec** **by** **itself**. |
| Linux cgroups | `linux-cgroups` | **cgroup** **v2** **resource** **controllers** — **not** **interchangeable** **with** **`linux-namespaces`** **(visibility)** **or** **engines** **alone**. |
| Linux capabilities | `linux-capabilities` | **POSIX** **`CAP_*`** **sets** **on** **credentials** — **not** **interchangeable** **with** **`linux-security-modules`** **(MAC)** **or** **`seccomp`** **alone**. |
| Linux OverlayFS | `linux-overlayfs` | **Kernel** **union** **filesystem** **(lower/upper/work)** — **not** **`oci-image-spec`** **/** **`oci-runtime-spec`** **/** **engines** **alone**. |
| Linux netfilter | `linux-netfilter` | **Kernel** **packet** **filtering** **hooks** **(iptables/nftables)** — **not** **`ebpf`** **bytecode** **facility** **alone** **or** **L7** **reverse** **proxies** **alone**. |
| Linux FUSE | `linux-fuse` | **Kernel** **/** **`/dev/fuse`** **bridge** **to** **userspace** **filesystem** **daemons** — **not** **`linux-overlayfs`** **(in-kernel** **stacked** **fs)** **or** **`oci-image-spec`** **alone**. |
| Linux KVM | `linux-kvm` | **Kernel** **hardware** **virtualization** **API** (`/dev/kvm`) — **not** **`linux-namespaces`**/**`linux-cgroups`** **(containers)** **or** **`firecracker`** **(VMM)** **alone**. |
| Virtio | `virtio` | **Paravirtual** **I/O** **transport** **/** **device** **model** — **not** **`linux-kvm`** **(hypervisor** **API)** **or** **`firecracker`** **(VMM)** **alone**. |
| Linux vhost | `linux-vhost` | **Kernel** **vhost** **framework** **for** **virtio** **backends** — **not** **`virtio`** **(guest** **contract)** **or** **`linux-kvm`** **(hypervisor** **API)** **alone**. |
| Linux VFIO | `linux-vfio` | **Kernel** **VFIO** **/** **IOMMU** **device** **assignment** **to** **userspace** **/** **guests** — **not** **`virtio`** **(paravirtual** **I/O)** **or** **`linux-kvm`** **(hypervisor** **API)** **alone**. |
| QEMU | `qemu` | **Userspace** **VMM** **/** **system** **emulator** **(e.g.** **KVM** **on** **Linux)** — **not** **`linux-kvm`** **(kernel** **API)** **alone,** **`firecracker`** **(microVM** **product)** **alone,** **or** **kernel** **facilities** **such** **as** **`virtio`** **/** **`linux-vhost`** **/** **`linux-vfio`** **without** **the** **VMM** **that** **wires** **them.** |
| libvirt | `libvirt` | **Virtualization** **management** **API** **/** **daemon** **(commonly** **QEMU/KVM)** — **not** **`qemu`** **(VMM),** **`linux-kvm`** **(kernel** **API),** **or** **`kubernetes`** **(cluster** **orchestrator)** **alone.** |
| C libcs | `glibc`, `musl`, BSD libcs, `illumos-libc`, `android-bionic`, `newlib`, `wasi-libc`, `uclibc`, `dietlibc`, `msvc-vcruntime` | **`wasi`** **spec** vs **`wasi-libc`** **implementation** are distinct packages; other niche embedded Linux libcs optional. |
| C++ | `gnu-libstdcxx`, `llvm-libcxx`, `llvm-libcxxabi`, `msvcprt` | **`cxx-runtime`** / **`cxx-abi-runtime`** tags. |
| GPU / parallel | `spir-v`, `nvidia-ptx`, `vulkan`, `cuda`, `rocm`, `opencl`, `sycl`, `level-zero` | Shader/IR packages vs API packages. |
| Managed runtimes | `jvm`, `ecma-335-cli` | Distinct from **C** runtime packages. |
| Web | `webassembly`, `wasi`, `wasm-component-model`, `webgpu`, `webgl` | WASM **stack** vs **browser API** slugs. |

**Comparative:** `language_machine_and_assembly_stack.md` §5–6; matrices §9–10; **Forbidden merges** for MSVC vs Unix, newlib vs hosted libcs, etc.

### 7.5 Networking — service mesh, ingress, load balancing, CDN

**Intent:** North-south and east-west patterns for distributed systems and AI serving.

| Direction | Examples |
|-----------|----------|
| Mesh | `envoy`, `istio`, `linkerd`, `cilium` |
| Kernel L3/L4 filtering (Linux) | `linux-netfilter` — hooks + iptables/nftables frontends; **not** **`ebpf`** **alone** **or** **L7** **proxies** **alone**. |
| Ingress | `traefik`, `nginx`, `ingress-nginx`, `emissary-ingress`, `haproxy` |
| Managed cloud L4/L7 | `aws-elastic-load-balancing`, `amazon-api-gateway`, `azure-application-gateway`, `gcp-load-balancing`, `azure-front-door` |
| CDN / edge | `amazon-cloudfront`, `cloudflare-workers`, `fastly`, `akamai`, `edgio` |
| Discovery | `consul` |

**Comparative:** matrices §4, §8; open gaps for niche vendors.

### 7.6 Data plane — stores, queues, streaming

**Intent:** Persistence and movement of state — training pipelines, inference, and control telemetry.

| Direction | Examples |
|-----------|----------|
| RDBMS / embedded | `postgresql`, `sqlite` |
| Memory / streams | `redis`, `apache-kafka` |

**Comparative:** matrices §8; `integrates_with` orchestration and observability slugs.

### 7.7 Observability and RPC

**Intent:** How systems witness themselves and talk — aligns with ION signals and MCP-adjacent design.

| Direction | Examples |
|-----------|----------|
| Telemetry | `opentelemetry` |
| RPC / transport | `grpc`, `http3` |
| Object storage API patterns | `amazon-s3` |

**Comparative:** matrices; distinguish **gRPC** vs **MCP** vs **HTTP** (forbidden merges).

### 7.8 Security, identity, trust, confidential computing

**Intent:** Boot trust, tenant isolation, attestation — for any “secure AI OS” narrative.

| Direction | Examples |
|-----------|----------|
| Identity | `openid-connect`, `tpm2`, `uefi` |
| TEE / CC | `confidential-computing`, `intel-tdx`, `amd-sev`, `arm-cca` |
| Future | RISC-V confidential extensions as **separate** packages when normative |

**Comparative:** matrices §1 TEE rows; §9 gaps.

### 7.9 AI / ML serving and GPU collectives

**Intent:** Inference servers and collective comms — **field** reference for “AI runtime” stacks.

| Direction | Examples |
|-----------|----------|
| Serving | `nvidia-triton-inference-server`, `vllm` |
| Collectives | `nccl` |
| ML interchange | `onnx` |

**Comparative:** matrices ML rows; avoid **ONNX** as “inference without runtime” (forbidden merge).

### 7.10 IDE, agents, and developer protocols

**Intent:** How tools attach to editors and agents — direct ION/MCP relevance.

| Direction | Examples |
|-----------|----------|
| IDEs / assistants | `vscode`, `cursor`, `anthropic-claude-code-agent-sdk`, `openhands` |
| Protocols | `language-server-protocol`, `debug-adapter-protocol`, `model-context-protocol` |
| Public API runtimes | `openai-agents-chatgpt-public-runtime`, `gemini-api`, `deepseek-api`, `microsoft-agent-framework` |

**Comparative:** `context_systems_landscape.md` §2; matrices §4; **LSP/DAP/MCP** separation.

### 7.11 Linux distributions and packaging law

**Intent:** glibc vs musl bases, systemd defaults, lineage Fedora → CentOS Stream → RHEL → rebuilds.

| Direction | Examples |
|-----------|----------|
| Families | `alpine-linux`, `debian`, `ubuntu`, `fedora`, `centos-stream`, `rhel`, `rocky-linux`, `almalinux`, `centos-linux` |

**Comparative:** matrices; **forbidden merges** for “Ubuntu = Debian” etc.

### 7.12 Historical and research OS lineages

**Intent:** Intellectual history — Plan 9, Inferno, Multics — without conflating with production Linux.

| Direction | Examples |
|-----------|----------|
| Plan 9 line | `plan-9`, `inferno-os`, `9front`, `v9fs` |
| Historical languages | `pl-i`, `fortran`, `cobol`, `algol`, `pascal-language`, `ada-language` |

**Comparative:** `bell_labs_unix_plan9_lineage.md`; matrices where cross-references matter.

### 7.13 ISAs and hardware law

**Intent:** CPU architecture as **package** where it affects toolchain and OS (e.g. RISC-V).

| Direction | Examples |
|-----------|----------|
| Open ISA survey | `riscv-isa` | Confidential-compute **extensions** as future slugs when ratified. |

**Comparative:** `language_machine` §1; matrices evolution line.

---

## 8. Per-wave execution playbook

Use this checklist for **every** coordinated expansion (single package or batch).

### 8.1 Pre-flight

1. **Choose slug(s)** per [`naming_conventions.md`](naming_conventions.md) — kebab-case, stable product or spec names.  
2. **Search** `indexes/systems_index.yaml` and `systems/` for collisions.  
3. **Identify comparative files** affected (§6 above).  
4. **Sketch relations** to existing packages — plan **reciprocal** updates for `competes_with` / strong `integrates_with`.

### 8.2 Scaffold

1. Copy `systems/_template/` → `systems/<slug>/`.  
2. Fill `00_identity.md`, `01_scope.md` first — **what it is / is not**.  
3. Add `sources.yaml` with **primary** URLs or repos; note draft-vs-IS for standards.  
4. Write ledger rows in `13_evidence_ledger.md` / section ledgers as claims solidify.  
5. Complete `14_documented_vs_inferred.md` with **open questions**.  
6. Set `tags.yaml` and add **`relations.json`** edges.

### 8.3 Indexes

1. **`indexes/systems_index.yaml`** — entry with `primary_kind` and display name.  
2. **`indexes/tag_index.yaml`** — add slug under each tag it belongs to.  
3. If new **tag kind** is needed, update [`tag_taxonomy.yaml`](tag_taxonomy.yaml) (if present) and tag_index consistently.

### 8.4 Comparative updates

1. **`ai_operating_system_reference_matrices.md`** — relevant § rows; **§10** open gaps (remove covered items, add new honest gaps); **Forbidden merges** if new confusion class appears; **Evolution** line + companion line if significant.  
2. **`language_machine_and_assembly_stack.md`** — if toolchain/language/ISA.  
3. **`context_systems_landscape.md`** — if context/MCP/IDE/RAG boundary.  
4. **`bell_labs_unix_plan9_lineage.md`** — only for Bell/Plan9/Inferno lineage work.

### 8.5 Roadmap and meta

1. **`_meta/AI_OS_EVOLUTION_ROADMAP.md`** — **Executed wave** subsection + adjust **Next waves** table rows.  
2. This **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** — update §13 open gaps if you add a **new recurring theme**.

### 8.6 ION witness

1. `ION/05_context/signals/ATLAS_<TOPIC>_YYYYMMDD.signal.md` — paths touched, packages, comparative files.  
2. `ION/CAPSULE.md` — **ION-*** row (next free ID).  
3. `ION/agents/atlas/CAPSULE.md` — **A-*** row.  
4. Optionally bump **`ION/agents/atlas/MINI.md`** routing notes.

### 8.7 Validation gate

```bash
python3 ATLAS/scripts/validate_structure.py ATLAS
python3 ATLAS/scripts/validate_relations.py ATLAS
python3 ATLAS/scripts/validate_frontmatter.py ATLAS
```

All must pass before calling a wave **complete**.

---

## 9. Indexes, tags, and taxonomy

- **`systems_index.yaml`** — canonical registry of slugs; keep **sorted** or follow existing convention for discoverability.  
- **`tag_index.yaml`** — reverse index; **every** tag on a package should appear here.  
- **Primary kind** — helps humans and scripts; align with `systems_index` metadata.  
- When adding tags like **`c-runtime`**, **`toolchain`**, **`protocol`**, ensure **cross-package consistency** (e.g. all libcs under `c-runtime` that participate in the same comparative table).

---

## 10. Relations graph discipline

- Use only types defined in [`relation_types.md`](relation_types.md).  
- **`competes_with`** should be **reciprocal** when the relationship is symmetric in the comparative docs.  
- **`integrates_with`** reciprocals: if A integrates B, often B integrates A **when** the doc language supports it (curator judgment).  
- **Do not** create edges to **non-existent** slugs (validators enforce).  
- Prefer **fewer, accurate** edges over dense but vague graphs.

---

## 11. ION witness protocol

**Boot:** [`ION/03_registry/boots/ATLAS.boot.md`](../../ION/03_registry/boots/ATLAS.boot.md)

**Rules:**

- Signals are **machine-addressable** breadcrumbs for Nemesis/Vizier — not a substitute for package ledgers.  
- Root `ION/CAPSULE.md` entries are **projections**; Atlas private log is `ION/agents/atlas/CAPSULE.md`.  
- Naming: `ATLAS_<SHORT_TOPIC>_YYYYMMDD.signal.md` — topic uppercase snake for grep.

---

## 12. Validation and automation

| Script | Role |
|--------|------|
| `scripts/validate_structure.py` | Directory layout and required files |
| `scripts/validate_relations.py` | Edge endpoints exist |
| `scripts/validate_frontmatter.py` | YAML frontmatter on system packages |

**Scaffold scripts** (`scaffold_*.py`): treat as **templates** — re-run only with human review (`README.md` warning).

---

## 13. Open gaps catalog (rolling)

**Source of truth for “not yet seeded”** lives in **`ai_operating_system_reference_matrices.md` §10** and **`AI_OS_EVOLUTION_ROADMAP.md` Next waves**. Typical recurring items:

- Niche CDN / regional PoPs — not exhaustive.  
- Proprietary NGINX Plus-only behaviors as a **dedicated** package — not seeded.  
- RISC-V confidential extensions — separate from base `riscv-isa` when ready.  
- systemd **generator implementation** internals beyond **systemd-unit-model** contract.  
- Finer **MSVC** CRT splits (UCRT vs `VCRUNTIME*` vs legacy MSVCRT) — optional.  
- Per-minor **CentOS** forks as separate distros — optional.

**Maintenance:** When you seed a gap, **edit §10** and this section’s mirror list in the same PR/wave.

---

## 14. Suggested sequencing

**Principle:** Alternate **deep single-package** improvements (grades A/B) with **thematic waves** that keep comparative matrices coherent.

| Theme | Rationale | Typical outputs |
|-------|-----------|-----------------|
| **Residual libc / embedded** | Roadmap explicitly open | **`wasi`** (spec-first) vs **`wasi-libc`**; other niche embedded Linux libcs — **one slug per wave** unless tightly coupled. |
| **Toolchain law depth** | ELF ABI per ISA, relocation models | New packages or **ledger depth** in `elf` + ISA slugs. |
| **TEE / CC** | Hardware trust | New CPU/vendor packages when specs stable. |
| **MCP / IDE adjacency** | ION Horizon 2 | Deeper **`model-context-protocol`** ledgers; **not** merging with gRPC. |
| **Service mesh / ingress** | Operations reality | Fill remaining niche ingress controllers only when operator demand exists. |
| **Distro lineage** | Packaging law | Finer CentOS minors **only** if consolidation work needs them. |

**Anti-pattern:** Seeding ten unrelated slugs without updating **§9 matrices** — creates orphan packages.

---

## 15. Risk register and anti-patterns

| Risk | Mitigation |
|------|------------|
| **Tier inflation** (INFERRED sold as DOCUMENTED) | Ledger + `14_*` explicit boundaries; Nemesis audit. |
| **Slug explosion** | Prefer **extends existing** via relations + ledgers before new package. |
| **Comparative drift** | Mandatory comparative pass in wave playbook (§8). |
| **Broken reciprocals** | `validate_relations.py` + grep for peer slugs. |
| **Marketing architecture** | Ontology forbidden moves; scrub superlatives in `02_architecture.md`. |

**Forbidden merges** are duplicated in comparative docs — when adding a package that could be confused with an existing one, add a **bullet** to the relevant matrix’s **Forbidden merges** section.

---

## 16. Appendices

### 16.1 Slug and file naming

- Slugs: **kebab-case**, ASCII; see [`naming_conventions.md`](naming_conventions.md).  
- Files: `NN_topic.md` under each package; **do not** rename without index grep.

### 16.2 Ledger IDs

- Use **stable prefixes** per package (e.g. `newlib-001`) — continuity for future diffs.

### 16.3 Standards citations

- Prefer **ISO / JTC1** catalog links for normative editions; PDFs often purchase-only — **WG drafts** require **draft ≠ IS** notes (`README.md` standards note).

### 16.4 Quick link roll — constitution

| Doc | Purpose |
|-----|---------|
| [`ontology.md`](ontology.md) | Kinds, forbidden moves |
| [`evidence_tiers.md`](evidence_tiers.md) | Tier definitions |
| [`quality_bar.md`](quality_bar.md) | Merge gates |
| [`naming_conventions.md`](naming_conventions.md) | Slugs |
| [`relation_types.md`](relation_types.md) | Edge vocabulary |
| [`package_schema.yaml`](package_schema.yaml) | Structural schema |
| [`AI_OS_EVOLUTION_ROADMAP.md`](AI_OS_EVOLUTION_ROADMAP.md) | Chronological executed waves + next waves table |

---

**End of master plan.** Revise this file when **cross-cutting rules** change; revise **`AI_OS_EVOLUTION_ROADMAP.md`** for **wave-by-wave** history. Together they form the **full** planning surface for continuing **Systems ATLAS** OS/systems documentation.
