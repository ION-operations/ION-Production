# Systems ATLAS — AI / OS evolution roadmap (ION-aligned)

**Status:** Living document. **Authority:** Curatorial (Atlas); **not** ION doctrine.

**Purpose:** Map ATLAS growth to **ION** horizons in `ION/PLAN.md` (unified kernel → MCP → products → IDE → OS) while keeping ATLAS as **field reference** only.

**Planning spine:** For domain-by-domain directions, comparative map, wave checklist, gaps, and sequencing, see [`MASTER_SYSTEMS_EXPANSION_PLAN.md`](MASTER_SYSTEMS_EXPANSION_PLAN.md). This file keeps the **chronological wave log** and **Next waves** table; the master plan holds the **full** expansion taxonomy.

---

## Executed wave (2026-04-03)

- **14** new `systems/<slug>/` packages (see `ION/05_context/signals/ATLAS_AI_OS_EXPANSION_20260403.signal.md`).
- **Comparative:** `comparative/ai_operating_system_reference_matrices.md`.
- **Validation:** `scripts/validate_relations.py` (edge targets must exist).
- **MCP:** transport source + ledger rows; `grpc` / `http3` adjacency (semantic distinction, not equivalence).

**Already present before wave (not duplicated):** `kubernetes`, `systemd`, full GPU/Web language stack, `model-context-protocol`, etc.

---

## Executed wave (2026-04-04) — data plane / mesh / boot

- **7** new packages: `postgresql`, `sqlite`, `redis`, `apache-kafka`, `envoy`, `istio`, `grub` (signal `ATLAS_DATA_PLANE_20260404.signal.md`).
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 (data stores, streaming, mesh, boot).
- **Generator:** `scripts/scaffold_data_plane_wave.py`.

---

## Executed wave (2026-04-05) — mesh alternatives, eBPF dataplane, boot / UKI

- **4** new packages: `linkerd`, `cilium`, `systemd-boot`, `unified-kernel-image` (signal `ATLAS_MESH_BOOT_UKI_20260405.signal.md`).
- **Comparative:** trust/boot table + §8 rows; open gaps updated.
- **Generator:** `scripts/scaffold_mesh_boot_wave.py`.

---

## Executed wave (2026-04-06) — ingress, Consul, UAPI BLS

- **3** new packages: `traefik`, `consul`, `uapi-boot-loader-specification` (signal `ATLAS_INGRESS_BLS_20260406.signal.md`).
- **Comparative:** §4 ingress row, §1 BLS row, §8 Consul row, §9 gaps.
- **Generator:** `scripts/scaffold_ingress_bootspec_wave.py`.

---

## Executed wave (2026-04-07) — ingress breadth, x86 TEE vendors

- **4** new packages: `emissary-ingress`, `haproxy`, `intel-tdx`, `amd-sev` (signal `ATLAS_INGRESS_TEE_20260407.signal.md`).
- **Comparative:** §1 TEE row, §4 ingress row, §9 gaps.
- **Generator:** `scripts/scaffold_ingress_tee_wave.py`.

---

## Executed wave (2026-04-08) — NGINX, ingress-nginx, ARM CCA, systemd edges

- **3** new packages: `nginx`, `ingress-nginx`, `arm-cca` (signal `ATLAS_NGINX_ARM_SYSTEMD_20260408.signal.md`).
- **`systemd` deepen:** `relations.json` → `systemd-boot`, `unified-kernel-image`; `sources.yaml` + ledger **sd-005** / **sd-006** (`ukify`, `portablectl`).
- **Comparative:** §1 TEE, §4 ingress, §8 `systemd` row, §9 gaps.
- **Generator:** `scripts/scaffold_nginx_arm_wave.py`.

---

## Executed wave (2026-04-09) — managed cloud load balancing / API gateway

- **4** new packages: `aws-elastic-load-balancing`, `amazon-api-gateway`, `azure-application-gateway`, `gcp-load-balancing` (signal `ATLAS_CLOUD_EDGE_20260409.signal.md`).
- **Comparative:** §4 managed cloud row, §9 gaps.
- **Generator:** `scripts/scaffold_cloud_edge_wave.py`.

---

## Executed wave (2026-04-10) — global CDN / edge compute

- **3** new packages: `azure-front-door`, `amazon-cloudfront`, `cloudflare-workers` (signal `ATLAS_CDN_EDGE_20260410.signal.md`).
- **Comparative:** §4 CDN/edge row, §9 gaps; `tag_index` `distributed-system` aligned with managed-edge slugs.
- **Generator:** `scripts/scaffold_cdn_edge_wave.py`.

---

## Executed wave (2026-04-11) — CDN vendor breadth + RISC-V ISA

- **4** new packages: `fastly`, `akamai`, `edgio`, `riscv-isa` (signal `ATLAS_CDN_RISCV_20260411.signal.md`).
- **Comparative:** `ai_operating_system_reference_matrices.md` §4/§9; `language_machine_and_assembly_stack.md` §1 RISC-V row.
- **Generator:** `scripts/scaffold_cdn_riscv_wave.py`.

---

## Executed wave (2026-04-12) — Debug Adapter Protocol (IDE triad)

- **1** new package: `debug-adapter-protocol` (signal `ATLAS_DEBUG_ADAPTER_PROTOCOL_20260412.signal.md`).  
- **Relations:** `vscode` / `cursor` / `language-server-protocol` / `model-context-protocol` edges updated for **LSP / DAP / MCP** separation.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §4 + forbidden-merge line; `context_systems_landscape.md` §2 + companion.

---

## Executed wave (2026-04-12) — ELF object format (toolchain law)

- **1** new package: `elf` (TIS ELF + System V gABI refspec locators; signal `ATLAS_ELF_OBJECT_FORMAT_20260412.signal.md`).  
- **Relations:** `dwarf`, `llvm-ir`, `linux-kernel`, `unified-kernel-image`, `c-language`, `riscv-isa`, `debug-adapter-protocol` (plus reciprocal edges where comparative).  
- **Comparative:** `language_machine_and_assembly_stack.md` §5 row; `ai_operating_system_reference_matrices.md` new §9 + forbidden merge + evolution line.

---

## Executed wave (2026-04-12) — GNU Binutils (toolchain utilities)

- **1** new package: `gnu-binutils` (GNU + Sourceware doc locators; signal `ATLAS_GNU_BINUTILS_20260412.signal.md`).  
- **Taxonomy:** `tag_taxonomy.yaml` adds **`toolchain`**; `tag_index.yaml` lists `gnu-binutils`.  
- **Relations:** reciprocal edges with `elf`, `dwarf`, `c-language`, `linux-kernel`, `llvm-ir`, `riscv-isa`; `elf` §07 tooling paragraph points at package.  
- **Comparative:** `language_machine_and_assembly_stack.md`, `ai_operating_system_reference_matrices.md` §9, **Forbidden merges**, `context_systems_landscape.md` companion.

---

## Executed wave (2026-04-12) — LLVM lld (linker)

- **1** new package: `llvm-lld` (lld.llvm.org + LLVM CommandGuide; signal `ATLAS_LLVM_LLD_20260412.signal.md`).  
- **Tag:** `toolchain` (`tag_index` with `gnu-binutils`).  
- **Relations:** `llvm-ir`, `elf`, `c-language`, `rust-language`, `riscv-isa`, `linux-kernel`; **`competes_with`** / reciprocal with `gnu-binutils`.  
- **Comparative:** language stack, matrices §9, forbidden merge, landscape companion.

---

## Executed wave (2026-04-12) — systemd unit model (law grain)

- **1** new package: `systemd-unit-model` (freedesktop **systemd.unit(5)**, **systemd.service(5)**, **systemd.generator(7)**; signal `ATLAS_SYSTEMD_UNIT_MODEL_20260412.signal.md`).  
- **Tag:** `service-manager` alongside `systemd`.  
- **Relations:** `systemd`, `linux-kernel`, `systemd-boot`, `unified-kernel-image`, `docker`; reciprocal on `systemd` + boot/UKI/docker as noted.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 row, §10 gap text, **Forbidden merges**; `systemd/00_identity.md` boundary bullet.

---

## Executed wave (2026-04-12) — Clang + Kubernetes↔systemd units

- **1** new package: `clang` (clang.llvm.org + Users Manual; signal `ATLAS_CLANG_AND_K8S_SYSTEMD_20260412.signal.md`).  
- **Tag:** `toolchain` with `gnu-binutils`, `llvm-lld`.  
- **Relations:** `llvm-ir`, `llvm-lld`, `gnu-binutils`, `c-language`, `dwarf`, `elf`, `language-server-protocol` (clangd); reciprocal edges on those packages.  
- **Kubernetes:** `integrates_with` **`systemd-unit-model`**; reciprocal edge; matrices §8 row for **K8s Linux node services**.  
- **Comparative:** `language_machine_and_assembly_stack.md` §5; `ai_operating_system_reference_matrices.md` §8–§9 + **Forbidden merges** + evolution line.

---

## Executed wave (2026-04-12) — GNU GCC (compiler collection)

- **1** new package: `gnu-gcc` (gcc.gnu.org + GCC manual; signal `ATLAS_GNU_GCC_20260412.signal.md`).  
- **Tag:** `toolchain` with Binutils/Clang/lld.  
- **Relations:** `gnu-binutils`, `c-language`, `elf`, `dwarf`, `linux-kernel`, `riscv-isa`; **`competes_with`** **`clang`** (reciprocal).  
- **Comparative:** `language_machine_and_assembly_stack.md` §5; `ai_operating_system_reference_matrices.md` §9 + **Forbidden merges** + evolution line.

---

## Executed wave (2026-04-12) — GNU GDB (debugger)

- **1** new package: `gnu-gdb` (GNU + Sourceware docs; signal `ATLAS_GNU_GDB_20260412.signal.md`).  
- **Tag:** `toolchain`.  
- **Relations:** `dwarf`, `elf`, `gnu-gcc`, `clang`, `c-language`, `gnu-binutils`, `debug-adapter-protocol` (INFERRED); reciprocals added.  
- **Comparative:** `language_machine_and_assembly_stack.md` §5; `ai_operating_system_reference_matrices.md` §9 + **Forbidden merges**; `gnu-gcc/01_scope.md` points here.

---

## Executed wave (2026-04-12) — LLDB (LLVM debugger)

- **1** new package: `lldb` (lldb.llvm.org; signal `ATLAS_LLDB_20260412.signal.md`).  
- **Tag:** `toolchain`.  
- **Relations:** `clang`, `llvm-ir`, `dwarf`, `elf`, `c-language`, `debug-adapter-protocol`; **`competes_with`** **`gnu-gdb`** (reciprocal).  
- **Comparative:** language stack §5; matrices §9 + **Forbidden merges**; `context_systems_landscape.md`; `gnu-gdb/01_scope.md` pointer.

---

## Executed wave (2026-04-12) — systemd portable services

- **1** new package: `systemd-portable` (systemd.io PORTABLE_SERVICES + portablectl man; signal `ATLAS_SYSTEMD_PORTABLE_20260412.signal.md`).  
- **Tag:** `service-manager`.  
- **Relations:** `systemd`, `systemd-unit-model`, `linux-kernel`; **`competes_with`** **`docker`** (reciprocal `competes_with`).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 row; **Forbidden merges**; `systemd/00_identity.md` boundary; systemd host-init row wording (portablectl → `systemd-portable`).

---

## Executed wave (2026-04-03) — OCI Image Format

- **1** new package: `oci-image-spec` ([opencontainers/image-spec](https://github.com/opencontainers/image-spec); signal `ATLAS_OCI_IMAGE_SPEC_20260403.signal.md`).  
- **Tag:** `protocol` (`systems_index` **primary_kind** `protocol`).  
- **Relations:** **`integrates_with`** **`docker`**, **`containerd`**, **`runc`**, **`kubernetes`**; **`competes_with`** **`systemd-portable`** (reciprocal); reciprocals on those packages.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 row + **Forbidden merges**; `docker/00_identity.md` boundary; `context_systems_landscape.md` companion.

---

## Executed wave (2026-04-03) — OCI Distribution Specification

- **1** new package: `oci-distribution-spec` ([opencontainers/distribution-spec](https://github.com/opencontainers/distribution-spec); signal `ATLAS_OCI_DISTRIBUTION_SPEC_20260403.signal.md`).  
- **Tag:** `protocol`.  
- **Relations:** **`integrates_with`** **`oci-image-spec`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`podman`**, **`cri-o`** (reciprocals); **`oci-image-spec`** **`integrates_with`** **`oci-distribution-spec`**.  
- **Comparative:** matrices §8 + **Forbidden merges**; `docker` / `oci-image-spec` cross-refs; `context_systems_landscape.md`.

---

## Executed wave (2026-04-03) — OCI Runtime Specification

- **1** new package: `oci-runtime-spec` ([opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec); signal `ATLAS_OCI_RUNTIME_SPEC_20260403.signal.md`).  
- **Tag:** `protocol`.  
- **Relations:** **`integrates_with`** **`oci-image-spec`**, **`linux-kernel`**, **`runc`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`podman`**, **`cri-o`**; **`runc`** **`implements`** **`oci-runtime-spec`**; reciprocals on stack packages; **`oci-image-spec`** **`integrates_with`** **`oci-runtime-spec`**.  
- **Comparative:** matrices §8 (image + distribution + runtime rows) + **Forbidden merges**; `docker` / `runc` / `oci-distribution-spec` scope touch-ups; `context_systems_landscape.md`.

---

## Executed wave (2026-04-03) — crun (OCI low-level runtime)

- **1** new package: `crun` ([containers/crun](https://github.com/containers/crun); signal `ATLAS_CRUN_20260403.signal.md`).  
- **Tag:** `container-runtime`.  
- **Relations:** **`implements`** **`oci-runtime-spec`**; **`depends_on`** **`linux-kernel`**; **`integrates_with`** **`containerd`**, **`podman`**, **`cri-o`**, **`oci-image-spec`**, **`kubernetes`** (INFERRED); **`competes_with`** **`runc`** (reciprocal). **`oci-runtime-spec`** **`integrates_with`** **`crun`**; reciprocals on **`containerd`**, **`podman`**, **`cri-o`**, **`kubernetes`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 row + **Forbidden merges**; `runc` / `oci-runtime-spec` touch-ups; `context_systems_landscape.md`.

---

## Executed wave (2026-04-03) — GNU C Library (glibc)

- **1** new package: `glibc` ([GNU libc manual](https://www.gnu.org/software/libc/manual/), [sourceware](https://www.sourceware.org/glibc/); signal `ATLAS_GLIBC_20260403.signal.md`).  
- **Taxonomy:** **`c-runtime`** tag (`tag_taxonomy.yaml` + `tag_index.yaml`); `systems_index` **primary_kind** **`c-runtime`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`**, **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`c-language`**, **`riscv-isa`**, **`clang`** (INFERRED), **`gnu-gdb`**, **`lldb`** (INFERRED); reciprocals on those packages.  
- **Comparative:** `language_machine_and_assembly_stack.md` §5 row; `ai_operating_system_reference_matrices.md` §9 + **Forbidden merges** + §10 gap; `context_systems_landscape.md` companion.

---

## Executed wave (2026-04-03) — musl libc

- **1** new package: `musl` ([musl.libc.org](https://musl.libc.org/), [wiki](https://wiki.musl-libc.org/); signal `ATLAS_MUSL_20260403.signal.md`).  
- **Tag:** `c-runtime` (`glibc`, `musl`).  
- **Relations:** **`competes_with`** **`glibc`** (reciprocal); **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`**, **`gnu-gdb`**, **`lldb`** (INFERRED where noted), **`riscv-isa`**, **`docker`** (INFERRED); reciprocals.  
- **Comparative:** `language_machine_and_assembly_stack.md` §5; `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `context_systems_landscape.md`; **`glibc`** scope/relation map touch-up.

---

## Executed wave (2026-04-03) — GNU libstdc++

- **1** new package: `gnu-libstdcxx` ([GCC libstdc++ manual](https://gcc.gnu.org/onlinedocs/libstdc++/); signal `ATLAS_GNU_LIBSTDCXX_20260403.signal.md`).  
- **Taxonomy:** **`cxx-runtime`** (`tag_taxonomy.yaml` + `tag_index.yaml`); `systems_index` **primary_kind** **`cxx-runtime`**.  
- **Relations:** **`integrates_with`** **`gnu-gcc`**, **`glibc`**, **`musl`** (INFERRED), **`gnu-binutils`**, **`elf`**, **`dwarf`**, **`c-language`** (INFERRED), **`clang`** (INFERRED), **`gnu-gdb`**, **`lldb`** (INFERRED), **`riscv-isa`**; reciprocals.  
- **Comparative:** `language_machine_and_assembly_stack.md` §5; `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `context_systems_landscape.md`; **`gnu-gcc`** `01_scope.md`.

---

## Executed wave (2026-04-03) — LLVM libc++

- **1** new package: `llvm-libcxx` ([libc++ docs](https://libcxx.llvm.org/); signal `ATLAS_LLVM_LIBCXX_20260403.signal.md`).  
- **Taxonomy:** **`cxx-runtime`** already present; **`tag_index`** lists **`llvm-libcxx`** alongside **`gnu-libstdcxx`**.  
- **Relations:** **`integrates_with`** **`clang`**, **`llvm-lld`**, **`glibc`**, **`musl`** (INFERRED), **`gnu-binutils`**, **`elf`**, **`dwarf`**, **`c-language`** (INFERRED), **`gnu-gdb`** (INFERRED), **`lldb`**, **`riscv-isa`**; **`competes_with`** **`gnu-libstdcxx`** (reciprocal); reciprocals on neighbors.  
- **Comparative:** `language_machine_and_assembly_stack.md` §5; `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `context_systems_landscape.md`; **`gnu-libstdcxx`** identity boundary.

---

## Executed wave (2026-04-03) — LLVM libc++abi

- **1** new package: `llvm-libcxxabi` ([libc++abi docs](https://libcxxabi.llvm.org/); signal `ATLAS_LLVM_LIBCXXABI_20260403.signal.md`).  
- **Taxonomy:** **`cxx-abi-runtime`** in `tag_taxonomy.yaml` + `tag_index.yaml`; `systems_index` **primary_kind** **`cxx-abi-runtime`**.  
- **Relations:** **`integrates_with`** **`llvm-libcxx`**, **`clang`**, **`llvm-lld`**, **`glibc`**, **`musl`** (INFERRED), **`gnu-binutils`**, **`elf`**, **`dwarf`**, **`c-language`** (INFERRED), **`gnu-gdb`** (INFERRED), **`lldb`**, **`riscv-isa`**; **`llvm-libcxx`** **`integrates_with`** **`llvm-libcxxabi`**; reciprocals on toolchain neighbors.  
- **Comparative:** `language_machine_and_assembly_stack.md` §5; `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `context_systems_landscape.md`; **`llvm-libcxx`** scope/identity touch-up.

---

## Executed wave (2026-04-03) — systemd sysext

- **1** new package: `systemd-sysext` ([systemd-sysext(1)](https://www.freedesktop.org/software/systemd/man/latest/systemd-sysext.html); signal `ATLAS_SYSTEMD_SYSEXT_20260403.signal.md`).  
- **Tag:** **`service-manager`** (`tag_index` lists **`systemd-sysext`** alongside **`systemd`**, **`systemd-unit-model`**, **`systemd-portable`**).  
- **Relations:** **`integrates_with`** **`systemd`**, **`systemd-unit-model`**, **`systemd-portable`** (INFERRED), **`linux-kernel`**, **`unified-kernel-image`** (INFERRED); **`competes_with`** **`docker`**, **`oci-image-spec`** (INFERRED); reciprocals on **`systemd`**, **`systemd-portable`**, **`systemd-unit-model`**, **`linux-kernel`**, **`docker`**, **`oci-image-spec`**, **`unified-kernel-image`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 + **Forbidden merges**; `context_systems_landscape.md`; **`systemd`** **/** **`systemd-portable`** identity touch-ups.

---

## Executed wave (2026-04-03) — systemd confext

- **1** new package: `systemd-confext` ([systemd-confext(1)](https://www.freedesktop.org/software/systemd/man/latest/systemd-confext.html); signal `ATLAS_SYSTEMD_CONFEXT_20260403.signal.md`).  
- **Tag:** **`service-manager`** (`tag_index` includes **`systemd-confext`**).  
- **Relations:** **`integrates_with`** **`systemd`**, **`systemd-unit-model`**, **`systemd-sysext`**, **`systemd-portable`** (INFERRED), **`linux-kernel`**, **`unified-kernel-image`** (INFERRED); **`competes_with`** **`docker`**, **`oci-image-spec`** (INFERRED); reciprocals; **`systemd-sysext`** **`integrates_with`** **`systemd-confext`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 + **Forbidden merges**; `context_systems_landscape.md`; **`systemd`** **/** **`systemd-sysext`** scope touch-ups.

---

## Executed wave (2026-04-03) — Alpine Linux

- **1** new package: `alpine-linux` ([Alpine about](https://alpinelinux.org/about/); signal `ATLAS_ALPINE_LINUX_20260403.signal.md`).  
- **Taxonomy:** **`linux-distribution`** in `tag_taxonomy.yaml` + `tag_index.yaml`; `systems_index` **primary_kind** **`linux-distribution`**.  
- **Relations:** **`depends_on`** **`linux-kernel`**; **`integrates_with`** **`musl`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`docker`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`oci-image-spec`** (INFERRED); reciprocals on **`musl`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`oci-image-spec`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 **Open gaps** + **Forbidden merges**; `context_systems_landscape.md`.

---

## Executed wave (2026-04-03) — Debian

- **1** new package: `debian` ([Debian releases](https://www.debian.org/releases/stable/); signal `ATLAS_DEBIAN_20260403.signal.md`).  
- **Tag:** **`linux-distribution`** (`tag_index` lists **`debian`** alongside **`alpine-linux`**).  
- **Relations:** **`depends_on`** **`linux-kernel`**; **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`docker`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`oci-image-spec`** (INFERRED); **`competes_with`** **`alpine-linux`** (reciprocal); reciprocals on **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`oci-image-spec`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 + **Forbidden merges**; `context_systems_landscape.md`; **`alpine-linux`** **`competes_with`** **`debian`**.

---

## Executed wave (2026-04-03) — Ubuntu

- **1** new package: `ubuntu` ([Ubuntu release cycle](https://ubuntu.com/about/release-cycle); signal `ATLAS_UBUNTU_20260403.signal.md`).  
- **Tag:** **`linux-distribution`** (`tag_index` lists **`ubuntu`** alongside **`alpine-linux`**, **`debian`**).  
- **Relations:** **`depends_on`** **`linux-kernel`**; **`fork_of`** **`debian`**; **`debian`** **`influences`** **`ubuntu`**; **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`docker`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`oci-image-spec`** (INFERRED); **`competes_with`** **`alpine-linux`** (reciprocal); reciprocals on the same toolchain/container targets as **`debian`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 + **Forbidden merges**; **`alpine-linux`** **`competes_with`** **`ubuntu`**.

---

## Executed wave (2026-04-03) — Fedora

- **1** new package: `fedora` ([Fedora releases](https://docs.fedoraproject.org/en-US/releases/); signal `ATLAS_FEDORA_20260403.signal.md`).  
- **Tag:** **`linux-distribution`** (`tag_index` lists **`fedora`** alongside **`alpine-linux`**, **`debian`**, **`ubuntu`**).  
- **Relations:** **`depends_on`** **`linux-kernel`**; **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`docker`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`oci-image-spec`** (INFERRED); **`competes_with`** **`alpine-linux`** (reciprocal); reciprocals on the same toolchain/container targets as **`debian`**/**`ubuntu`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 + **Forbidden merges**; **`alpine-linux`** **`competes_with`** **`fedora`**.

---

## Executed wave (2026-04-03) — RHEL

- **1** new package: `rhel` ([Red Hat Enterprise Linux](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux); signal `ATLAS_RHEL_20260403.signal.md`).  
- **Tag:** **`linux-distribution`** (`tag_index` lists **`rhel`** alongside **`alpine-linux`**, **`debian`**, **`ubuntu`**, **`fedora`**).  
- **Relations:** **`depends_on`** **`linux-kernel`**; **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`docker`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`oci-image-spec`** (INFERRED), **`red-hat-openshift`**; **`competes_with`** **`alpine-linux`** (reciprocal); **`fedora`** **`influences`** **`rhel`**; **`red-hat-openshift`** **`integrates_with`** **`rhel`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 + **Forbidden merges**; **`alpine-linux`** **`competes_with`** **`rhel`**.

---

## Executed wave (2026-04-03) — Rocky Linux + AlmaLinux

- **2** new packages: `rocky-linux` ([Rocky Linux about](https://rockylinux.org/about)), `almalinux` ([AlmaLinux](https://almalinux.org/)); signal `ATLAS_ROCKY_ALMALINUX_20260403.signal.md`.  
- **Tag:** **`linux-distribution`** (`tag_index` adds **`rocky-linux`**, **`almalinux`**).  
- **Relations:** same toolchain/container **`integrates_with`** pattern as **`fedora`**/**`rhel`**; **`competes_with`** **`alpine-linux`** (reciprocal); **`rocky-linux`** **`competes_with`** **`almalinux`** (reciprocal); **`rhel`** **`influences`** **`rocky-linux`** **and** **`almalinux`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 + **Forbidden merges**.

---

## Executed wave (2026-04-03) — CentOS Stream

- **1** new package: `centos-stream` ([CentOS Stream](https://www.centos.org/centos-stream/)); signal `ATLAS_CENTOS_STREAM_20260403.signal.md`.  
- **Tag:** **`linux-distribution`** (`tag_index` adds **`centos-stream`**).  
- **Relations:** **`fedora`** **`influences`** **`centos-stream`**; **`centos-stream`** **`influences`** **`rhel`**; toolchain/container **`integrates_with`** mirror **`fedora`**/**`rhel`** **minus** **`red-hat-openshift`**; **`competes_with`** **`alpine-linux`** (reciprocal); reciprocals on **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`oci-image-spec`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 + **Forbidden merges**.

---

## Executed wave (2026-04-03) — CentOS Linux (legacy)

- **1** new package: `centos-linux` ([CentOS project communications](https://blog.centos.org/)); signal `ATLAS_CENTOS_LINUX_20260403.signal.md`.  
- **Tag:** **`linux-distribution`** (`tag_index` adds **`centos-linux`**).  
- **Relations:** **`rhel`** **`influences`** **`centos-linux`**; **`competes_with`** **`alpine-linux`**, **`rocky-linux`**, **`almalinux`** (reciprocal); toolchain/container **`integrates_with`** mirror **`rocky-linux`**/**`almalinux`**; reciprocals on **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`oci-image-spec`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8–§9 + §10 + **Forbidden merges**.

---

## Executed wave (2026-04-03) — MSVC Windows CRT + C++ runtime

- **2** new packages: `msvc-vcruntime` ([CRT library features](https://learn.microsoft.com/en-us/cpp/c-runtime-library/crt-library-features)), `msvcprt` ([C++ standard library](https://learn.microsoft.com/en-us/cpp/standard-library/cpp-standard-library-reference)); signal `ATLAS_MSVC_RUNTIME_20260403.signal.md`.  
- **Tags:** **`c-runtime`** (`msvc-vcruntime`), **`cxx-runtime`** (`msvcprt`).  
- **Relations:** **`integrates_with`** **`windows-nt`**, **`c-language`**; **`msvc-vcruntime`** **`integrates_with`** **`msvcprt`** **/** **`clang`**; **`msvcprt`** **`competes_with`** **`gnu-libstdcxx`**, **`llvm-libcxx`** (reciprocal); **`windows-nt`** **`integrates_with`** both; comparative **`language_machine_and_assembly_stack.md`** §5.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**.

---

## Executed wave (2026-04-03) — FreeBSD + OpenBSD libc

- **2** new packages: `freebsd-libc` ([FreeBSD Handbook](https://docs.freebsd.org/en/books/handbook/bibliography/)), `openbsd-libc` ([OpenBSD FAQ](https://www.openbsd.org/faq/)); signal `ATLAS_BSD_LIBC_20260403.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`freebsd-libc`**, **`openbsd-libc`**).  
- **Relations:** **`integrates_with`** **`c-language`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`freebsd-libc`** **`integrates_with`** **`freebsd`**; **`competes_with`** **`glibc`**, **`musl`**, **cross**-**BSD** (reciprocal); **`gnu-libstdcxx`**/**`llvm-libcxx`**/**`llvm-libcxxabi`** reciprocals; **`freebsd`** **`integrates_with`** **`freebsd-libc`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-03) — NetBSD + DragonFly libc

- **2** new packages: `netbsd-libc` ([NetBSD Guide](https://www.netbsd.org/docs/guide/en/)), `dragonfly-libc` ([DragonFly Handbook](https://www.dragonflybsd.org/docs/handbook/)); signal `ATLAS_NETBSD_DRAGONFLY_LIBC_20260403.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`netbsd-libc`**, **`dragonfly-libc`**).  
- **Relations:** **`integrates_with`** **`c-language`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **cross**-**BSD** **with** **`freebsd-libc`**/**`openbsd-libc`** (reciprocal); **`gnu-libstdcxx`**/**`llvm-libcxx`**/**`llvm-libcxxabi`** reciprocals.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-03) — illumos libc

- **1** new package: `illumos-libc` ([illumos developer guide](https://illumos.org/books/dev/intro.html)); signal `ATLAS_ILLUMOS_LIBC_20260403.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`illumos-libc`**).  
- **Relations:** **`integrates_with`** **`c-language`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`** (reciprocal); **`gnu-libstdcxx`**/**`llvm-libcxx`**/**`llvm-libcxxabi`** reciprocals.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-03) — Android Bionic

- **1** new package: `android-bionic` ([AOSP platform/bionic README](https://android.googlesource.com/platform/bionic/+/refs/heads/main/README.md)); signal `ATLAS_ANDROID_BIONIC_20260403.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`android-bionic`**).  
- **Relations:** **`integrates_with`** **`android-aosp`**, **`linux-kernel`**, **`c-language`**, **`elf`**, **`clang`**, **`llvm-libcxx`**, **`llvm-libcxxabi`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`** (reciprocal); **`gnu-libstdcxx`**/**`llvm-libcxx`**/**`llvm-libcxxabi`** reciprocals.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-03) — newlib

- **1** new package: `newlib` ([Sourceware newlib](https://sourceware.org/newlib/), [GitWeb](https://sourceware.org/git/?p=newlib-cygwin.git)); signal `ATLAS_NEWLIB_20260403.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`newlib`**).  
- **Relations:** **`integrates_with`** **`c-language`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`riscv-isa`** (INFERRED), **`gnu-libstdcxx`**, **`llvm-libcxx`**, **`llvm-libcxxabi`** (reciprocal); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`** (reciprocal).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-13) — wasi-libc

- **1** new package: `wasi-libc` ([GitHub wasi-libc](https://github.com/WebAssembly/wasi-libc)); signal `ATLAS_WASI_LIBC_20260413.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`wasi-libc`**).  
- **Relations:** **`integrates_with`** **`wasi`**, **`webassembly`**, **`c-language`**, **`clang`**, **`llvm-lld`**, **`wasm-component-model`** (INFERRED), **`gnu-libstdcxx`**, **`llvm-libcxx`**, **`llvm-libcxxabi`** (reciprocal); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`** (reciprocal); **`wasi`**/**`webassembly`**/**`clang`**/**`llvm-lld`** updated.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10 + **Forbidden merges**; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-14) — uClibc-ng (uclibc)

- **1** new package: `uclibc` ([uClibc-ng](https://uclibc-ng.org/), [Git](https://cgit.uclibc-ng.org/cgi/cgit/uclibc-ng.git/)); signal `ATLAS_UCLIBC_20260414.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`uclibc`**).  
- **Relations:** **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`riscv-isa`** (INFERRED), **`gnu-libstdcxx`**, **`llvm-libcxx`**, **`llvm-libcxxabi`** (reciprocal); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`** (reciprocal).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-15) — dietlibc

- **1** new package: `dietlibc` ([dietlibc](https://www.fefe.de/dietlibc/)); signal `ATLAS_DIETLIBC_20260415.signal.md`.  
- **Tag:** **`c-runtime`** (`tag_index` adds **`dietlibc`**).  
- **Relations:** **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`gnu-libstdcxx`**, **`llvm-libcxx`**, **`llvm-libcxxabi`** (reciprocal); **`competes_with`** peer **`c-runtime`** libcs including **`uclibc`** (reciprocal).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §9–§10; `language_machine_and_assembly_stack.md` §5.

---

## Executed wave (2026-04-16) — libbpf

- **1** new package: `libbpf` ([libbpf/libbpf](https://github.com/libbpf/libbpf), [kernel docs](https://www.kernel.org/doc/html/latest/bpf/libbpf/index.html)); signal `ATLAS_LIBBPF_20260416.signal.md`.  
- **Tag:** **`toolchain`** (`tag_index` adds **`libbpf`**).  
- **Relations:** **`integrates_with`** **`ebpf`**, **`linux-kernel`**, **`c-language`**, **`glibc`** (INFERRED), **`musl`** (INFERRED), **`clang`** (INFERRED), **`llvm-ir`** (INFERRED), **`gnu-gcc`** (INFERRED); **`ebpf`** **`integrates_with`** **`libbpf`** (reciprocal).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2, §7, §10, **Forbidden merges**; evolution line.

---

## Executed wave (2026-04-17) — io_uring + liburing

- **2** new packages: `io-uring` ([kernel io_uring docs](https://www.kernel.org/doc/html/latest/io_uring/index.html)), `liburing` ([axboe/liburing](https://github.com/axboe/liburing)); signal `ATLAS_IO_URING_LIBURING_20260417.signal.md`.  
- **Tags:** **`io-uring`** — **`protocol`** + **`kernel`**; **`liburing`** — **`toolchain`**.  
- **Relations:** reciprocal **`integrates_with`** **`io-uring`** ↔ **`liburing`**; **`linux-kernel`**; **`liburing`** **`integrates_with`** **`c-language`**, **`glibc`** (INFERRED), **`musl`** (INFERRED), **`clang`** (INFERRED), **`gnu-gcc`** (INFERRED).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2, §8, **Forbidden merges**; evolution line.

---

## Executed wave (2026-04-18) — Landlock

- **1** new package: `landlock` ([kernel Landlock uAPI](https://docs.kernel.org/userspace-api/landlock.html), [landlock.io](https://landlock.io/)); signal `ATLAS_LANDLOCK_20260418.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`**, **`linux-security-modules`**, **`c-language`**, **`glibc`** (INFERRED), **`musl`** (INFERRED), **`kubernetes`** (INFERRED); **`linux-security-modules`** **`integrates_with`** **`landlock`** (reciprocal).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2, **Forbidden merges**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** hardening row.

---

## Executed wave (2026-04-19) — seccomp + libseccomp

- **2** new packages: `seccomp` ([Seccomp BPF](https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html)), `libseccomp` ([seccomp/libseccomp](https://github.com/seccomp/libseccomp)); signal `ATLAS_SECCOMP_LIBSECCOMP_20260419.signal.md`.  
- **Tags:** **`seccomp`** — **`protocol`** + **`kernel`**; **`libseccomp`** — **`toolchain`**.  
- **Relations:** reciprocal **`integrates_with`** **`seccomp`** ↔ **`libseccomp`**; **`linux-kernel`**; **`libseccomp`** **`integrates_with`** **`c-language`**, **`glibc`** (INFERRED), **`musl`** (INFERRED), **`clang`** (INFERRED), **`gnu-gcc`** (INFERRED), **`kubernetes`** (INFERRED).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2, **Forbidden merges**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** hardening + §7.4.

---

## Executed wave (2026-04-20) — Linux namespaces

- **1** new package: `linux-namespaces` ([namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)); signal `ATLAS_LINUX_NAMESPACES_20260420.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`**, **`docker`** (INFERRED), **`kubernetes`** (INFERRED), **`containerd`** (INFERRED), **`runc`** (INFERRED), **`podman`** (INFERRED), **`cri-o`** (INFERRED), **`systemd`** (INFERRED).  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (containers row + new row), **Forbidden merges**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** hardening + §7.4.

---

## Executed wave (2026-04-21) — Linux cgroups

- **1** new package: `linux-cgroups` ([cgroup v2 admin guide](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)); signal `ATLAS_LINUX_CGROUPS_20260421.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`linux-namespaces`**, **`docker`**/**`kubernetes`**/**`containerd`**/**`runc`**/**`podman`**/**`cri-o`**/**`systemd`** (INFERRED where marked). Reciprocal **`linux-namespaces`** → **`linux-cgroups`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (OS containers + **Linux cgroups** row), **Forbidden merges** **`linux-cgroups`** vs **`docker`**/**`kubernetes`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** hardening + §7.4.

---

## Executed wave (2026-04-22) — Linux capabilities

- **1** new package: `linux-capabilities` ([capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)); signal `ATLAS_LINUX_CAPABILITIES_20260422.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`linux-namespaces`**, **`linux-cgroups`**, **`linux-security-modules`**, **`seccomp`**, **`docker`**/**`kubernetes`**/**`containerd`**/**`runc`**/**`podman`**/**`cri-o`**/**`systemd`** (INFERRED where marked). Reciprocal edges from **`linux-namespaces`**, **`linux-cgroups`**, **`seccomp`**, **`linux-security-modules`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (OS containers row + **Linux capabilities** row), **Forbidden merges** **`linux-capabilities`** vs **`linux-security-modules`**/**`seccomp`**/**`docker`**/**`kubernetes`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** hardening + §7.4.

---

## Executed wave (2026-04-23) — Linux OverlayFS

- **1** new package: `linux-overlayfs` ([Overlay Filesystem](https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html)); signal `ATLAS_LINUX_OVERLAYFS_20260423.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`linux-namespaces`**, **`oci-image-spec`**, **`oci-runtime-spec`**, **`docker`**/**`containerd`**/**`runc`**/**`podman`**/**`cri-o`**/**`kubernetes`** (INFERRED where marked). Reciprocal **`linux-namespaces`** → **`linux-overlayfs`**; **`oci-image-spec`**/**`oci-runtime-spec`** → **`linux-overlayfs`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (OS containers row + **Linux OverlayFS** row), **Forbidden merges** **`linux-overlayfs`** vs **`oci-image-spec`**/**`oci-runtime-spec`**/**`docker`**/**`kubernetes`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3 + §7.4.

---

## Executed wave (2026-04-24) — Linux netfilter

- **1** new package: `linux-netfilter` ([kernel netfilter documentation](https://www.kernel.org/doc/html/latest/networking/netfilter.html)); signal `ATLAS_LINUX_NETFILTER_20260424.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`linux-namespaces`**, **`linux-capabilities`**, **`ebpf`**, **`kubernetes`**, **`docker`**, **`cilium`**, **`envoy`** (INFERRED where marked). Reciprocal **`linux-namespaces`**, **`linux-capabilities`**, **`ebpf`**, **`kubernetes`**, **`docker`**, **`cilium`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §8 (**Linux netfilter** row), **Forbidden merges** **`linux-netfilter`** vs **`ebpf`**/**`cilium`**/**`envoy`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.5 + §7.4.

---

## Executed wave (2026-04-25) — Linux FUSE

- **1** new package: `linux-fuse` ([kernel FUSE documentation](https://www.kernel.org/doc/html/latest/filesystems/fuse.html)); signal `ATLAS_LINUX_FUSE_20260425.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`linux-namespaces`**, **`linux-overlayfs`**, **`oci-image-spec`**, **`docker`**, **`containerd`**, **`kubernetes`** (INFERRED where marked). Reciprocal **`linux-namespaces`**, **`linux-overlayfs`**, **`oci-image-spec`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (**Linux FUSE** row), **Forbidden merges** **`linux-fuse`** vs **`linux-overlayfs`**/**`oci-image-spec`**/**`docker`**/**`kubernetes`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.4.

---

## Executed wave (2026-04-26) — Linux KVM

- **1** new package: `linux-kvm` ([kernel KVM documentation](https://www.kernel.org/doc/html/latest/virt/kvm/index.html)); signal `ATLAS_LINUX_KVM_20260426.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`firecracker`** (DOCUMENTED), **`linux-namespaces`**, **`linux-cgroups`**, **`docker`**, **`kubernetes`**, **`confidential-computing`** (INFERRED where marked). Reciprocal **`firecracker`**, **`linux-namespaces`**, **`linux-cgroups`**, **`docker`**, **`kubernetes`**, **`confidential-computing`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (MicroVM row + **Linux KVM** row), **Forbidden merges** **`linux-kvm`** vs **`linux-namespaces`**/**`linux-cgroups`**/**`firecracker`**/**`docker`**/**`kubernetes`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.4.

---

## Executed wave (2026-04-27) — Virtio

- **1** new package: `virtio` ([kernel Virtio documentation](https://www.kernel.org/doc/html/latest/driver-api/virtio/virtio.html)); signal `ATLAS_VIRTIO_20260427.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`linux-kvm`**, **`firecracker`** (INFERRED). Reciprocal **`linux-kvm`**, **`firecracker`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (MicroVM row + **Virtio** row), **Forbidden merges** **`virtio`** vs **`linux-kvm`**/**`firecracker`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.4.

---

## Executed wave (2026-04-28) — Linux vhost

- **1** new package: `linux-vhost` ([kernel vhost core](https://raw.githubusercontent.com/torvalds/linux/master/drivers/vhost/vhost.c)); signal `ATLAS_LINUX_VHOST_20260428.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`virtio`**, **`linux-kvm`**, **`firecracker`** (INFERRED). Reciprocal **`virtio`**, **`linux-kvm`**, **`firecracker`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (**Linux vhost** row), **Forbidden merges** **`linux-vhost`** vs **`virtio`**/**`linux-kvm`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.4.

---

## Executed wave (2026-04-03) — Linux VFIO

- **1** new package: `linux-vfio` ([kernel VFIO documentation](https://www.kernel.org/doc/html/latest/driver-api/vfio.html)); signal `ATLAS_LINUX_VFIO_20260403.signal.md`.  
- **Tags:** **`protocol`** + **`kernel`**.  
- **Relations:** **`integrates_with`** **`linux-kernel`** (DOCUMENTED), **`linux-kvm`**, **`firecracker`** (INFERRED). Reciprocal **`linux-kvm`**, **`firecracker`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (**Linux VFIO** row), **Forbidden merges** **`linux-vfio`** vs **`virtio`**/**`linux-kvm`**/**`linux-vhost`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.4.

---

## Executed wave (2026-04-04) — QEMU

- **1** new package: `qemu` ([QEMU documentation](https://www.qemu.org/docs/master/)); signal `ATLAS_QEMU_20260404.signal.md`.  
- **Tags:** **`vmm`** + **`distributed-system`** (`tag_taxonomy` / `tag_index`); `systems_index` **primary_kind** **`vmm`**.  
- **Relations:** **`depends_on`** **`linux-kernel`** (DOCUMENTED); **`integrates_with`** **`linux-kvm`** (DOCUMENTED), **`virtio`**, **`linux-vhost`**, **`linux-vfio`** (INFERRED); **`competes_with`** **`firecracker`** (INFERRED). Reciprocal **`linux-kvm`**, **`virtio`**, **`linux-vhost`**, **`linux-vfio`**, **`firecracker`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (**QEMU** row), **Forbidden merges** **`qemu`** vs **`linux-kvm`**/**`firecracker`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.4.

---

## Executed wave (2026-04-05) — libvirt

- **1** new package: `libvirt` ([libvirt documentation](https://libvirt.org/docs.html)); signal `ATLAS_LIBVIRT_20260405.signal.md`.  
- **Tags:** **`control-plane`** + **`distributed-system`**; `systems_index` **primary_kind** **`control-plane`**.  
- **Relations:** **`depends_on`** **`linux-kernel`** (DOCUMENTED); **`integrates_with`** **`qemu`** (DOCUMENTED), **`linux-kvm`**, **`kubernetes`** (INFERRED). Reciprocal **`qemu`**, **`linux-kvm`**, **`kubernetes`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (**libvirt** row), **Forbidden merges** **`libvirt`** vs **`qemu`**/**`linux-kvm`**/**`kubernetes`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.4.

---

## Executed wave (2026-04-06) — KubeVirt

- **1** new package: `kubevirt` ([KubeVirt user guide](https://kubevirt.io/user-guide/)); signal `ATLAS_KUBEVIRT_20260406.signal.md`.  
- **Tags:** **`cluster-orchestrator`** + **`distributed-system`** + **`control-plane`**; `systems_index` **primary_kind** **`cluster-orchestrator`**.  
- **Relations:** **`depends_on`** **`linux-kernel`** (DOCUMENTED); **`integrates_with`** **`kubernetes`** (DOCUMENTED), **`libvirt`**, **`qemu`**, **`linux-kvm`** (INFERRED). Reciprocal **`kubernetes`**, **`libvirt`**, **`qemu`**, **`linux-kvm`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §2 (**KubeVirt** row), **Forbidden merges** **`kubevirt`** vs **`kubernetes`**/**`libvirt`**/**`qemu`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Executed wave (2026-04-07) — Kata Containers

- **1** new package: `kata-containers` ([Kata Containers documentation](https://katacontainers.io/docs/)); signal `ATLAS_KATA_CONTAINERS_20260407.signal.md`.  
- **Tags:** **`container-runtime`** + **`distributed-system`** + **`microvm`**; `systems_index` **primary_kind** **`container-runtime`**.  
- **Relations:** **`depends_on`** **`linux-kernel`** (DOCUMENTED); **`implements`** **`oci-runtime-spec`** (DOCUMENTED); **`integrates_with`** **`kubernetes`** (DOCUMENTED), **`containerd`** (DOCUMENTED), **`qemu`**, **`linux-kvm`** (INFERRED); **`competes_with`** **`runc`** (INFERRED). Reciprocal **`kubernetes`**, **`containerd`**, **`qemu`**, **`linux-kvm`**, **`runc`**, **`oci-runtime-spec`**.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §1–§2 (**Kata** row + OS containers note), **Forbidden merges** **`kata-containers`** vs **`runc`**/**`kubevirt`**/**`qemu`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Executed wave (2026-04-08) — gVisor (runsc)

- **1** new package: `gvisor` ([gVisor documentation](https://gvisor.dev/docs/)); signal `ATLAS_GVISOR_20260408.signal.md`.  
- **Tags:** **`container-runtime`** + **`distributed-system`**; `systems_index` **primary_kind** **`container-runtime`**.  
- **Relations:** **`depends_on`** **`linux-kernel`** (DOCUMENTED); **`implements`** **`oci-runtime-spec`** (INFERRED); **`integrates_with`** **`kubernetes`**, **`containerd`**, **`docker`** (INFERRED); **`competes_with`** **`runc`**, **`kata-containers`** (INFERRED). Reciprocal edges from peers updated.  
- **Comparative:** `ai_operating_system_reference_matrices.md` §1–§2 (**gVisor** row + OS containers note), **Forbidden merges** **`gvisor`** vs **`runc`**/**`kata-containers`**/**`linux-kernel`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Executed wave (2026-04-09) — BuildKit

- **1** new package: `buildkit` ([moby/buildkit](https://github.com/moby/buildkit)); signal `ATLAS_BUILDKIT_20260409.signal.md`.  
- **Tags:** **`container-runtime`** + **`distributed-system`**; `systems_index` **primary_kind** **`container-runtime`**.  
- **Relations:** **`depends_on`** **`linux-kernel`** (DOCUMENTED); **`integrates_with`** **`oci-image-spec`**, **`oci-distribution-spec`**, **`docker`**, **`containerd`** (DOCUMENTED), **`kubernetes`** (INFERRED). Reciprocal edges from peers updated.  
- **Comparative:** `ai_operating_system_reference_matrices.md` survey (**BuildKit** row + **`oci-image-spec`** integrators), **Forbidden merges** **`buildkit`** vs **`oci-runtime-spec`**/**`runc`**/**`oci-image-spec`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Executed wave (2026-04-10) — Helm

- **1** new package: `helm` ([Helm documentation](https://helm.sh/docs/)); signal `ATLAS_HELM_20260410.signal.md`.  
- **Tags:** **`cluster-orchestrator`** + **`distributed-system`** + **`control-plane`**; `systems_index` **primary_kind** **`cluster-orchestrator`**.  
- **Relations:** **`depends_on`** **`kubernetes`** (DOCUMENTED); **`integrates_with`** **`oci-distribution-spec`**, **`oci-image-spec`** (INFERRED), **`docker`** (INFERRED). Reciprocal edges from peers updated.  
- **Comparative:** `ai_operating_system_reference_matrices.md` (**Helm** row; **`oci-image-spec`**/**`oci-distribution-spec`** integrators), **Forbidden merges** **`helm`** vs **`kubernetes`**/**`oci-runtime-spec`**/**`oci-image-spec`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Executed wave (2026-04-11) — Flux (fluxcd)

- **1** new package: `fluxcd` ([Flux documentation](https://fluxcd.io/flux/)); signal `ATLAS_FLUXCD_20260411.signal.md`.  
- **Tags:** **`cluster-orchestrator`** + **`distributed-system`** + **`control-plane`**; `systems_index` **primary_kind** **`cluster-orchestrator`**.  
- **Relations:** **`depends_on`** **`kubernetes`** (DOCUMENTED); **`integrates_with`** **`helm`** (DOCUMENTED), **`oci-image-spec`**, **`oci-distribution-spec`** (INFERRED). Reciprocal edges from peers updated.  
- **Comparative:** `ai_operating_system_reference_matrices.md` (**Flux** row), **Forbidden merges** **`fluxcd`** vs **`kubernetes`**/**`helm`**/**`oci-runtime-spec`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Executed wave (2026-04-12) — Argo CD

- **1** new package: `argo-cd` ([Argo CD documentation](https://argo-cd.readthedocs.io/)); signal `ATLAS_ARGO_CD_20260412.signal.md`.  
- **Tags:** **`cluster-orchestrator`** + **`distributed-system`** + **`control-plane`**; `systems_index` **primary_kind** **`cluster-orchestrator`**.  
- **Relations:** **`depends_on`** **`kubernetes`** (DOCUMENTED); **`integrates_with`** **`helm`** (DOCUMENTED), **`oci-image-spec`**, **`oci-distribution-spec`** (INFERRED); **`competes_with`** **`fluxcd`** (INFERRED). Reciprocal edges from peers updated.  
- **Comparative:** `ai_operating_system_reference_matrices.md` (**Argo** **CD** row; **`oci-image-spec`**/**`oci-distribution-spec`** integrators), **Forbidden merges** **`argo-cd`** vs **`kubernetes`**/**`fluxcd`**/**`helm`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Executed wave (2026-04-13) — Kustomize

- **1** new package: `kustomize` ([Kustomize kustomization reference](https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/)); signal `ATLAS_KUSTOMIZE_20260413.signal.md`.  
- **Tags:** **`cluster-orchestrator`** + **`distributed-system`** + **`control-plane`**; `systems_index` **primary_kind** **`cluster-orchestrator`**.  
- **Relations:** **`depends_on`** **`kubernetes`** (DOCUMENTED); **`integrates_with`** **`helm`**, **`fluxcd`**, **`argo-cd`** (DOCUMENTED). Reciprocal edges from peers updated.  
- **Comparative:** `ai_operating_system_reference_matrices.md` (**Kustomize** row), **Forbidden merges** **`kustomize`** vs **`kubernetes`**/**`helm`**; evolution line; **`MASTER_SYSTEMS_EXPANSION_PLAN.md`** §7.3.

---

## Next waves (suggested)

| Phase | Targets | Rationale |
|-------|---------|-----------|
| **systemd law grain** | ~~Unit grammar~~ **Done** (`systemd-unit-model`); ~~portable **image**~~ **Done** (`systemd-portable`); ~~**sysext**~~ **Done** (`systemd-sysext`); ~~**confext**~~ **Done** (`systemd-confext`); deeper **generator implementation** internals still optional | Init-system parity |
| **TEE breadth** | RISC-V confidential extensions when ratified / packaged separately | Finer TEE grain |
| **Linux kernel uAPI pairs** | ~~**ebpf**~~ + ~~**libbpf**~~ **Done**; ~~**io-uring**~~ + ~~**liburing**~~ **Done**; ~~**seccomp**~~ + ~~**libseccomp**~~ **Done** | Kernel facility vs userspace helper library — **not** libc/C++ survey |
| **Toolchain / userland** | ~~**glibc**~~ **Done**; ~~**musl**~~ **Done** (`c-runtime`); ~~**FreeBSD** **libc**~~ **Done** (`freebsd-libc`); ~~**OpenBSD** **libc**~~ **Done** (`openbsd-libc`); ~~**NetBSD** **libc**~~ **Done** (`netbsd-libc`); ~~**DragonFly** **libc**~~ **Done** (`dragonfly-libc`); ~~**illumos** **libc**~~ **Done** (`illumos-libc`); ~~**Android** **Bionic**~~ **Done** (`android-bionic`); ~~**newlib**~~ **Done** (`newlib`); ~~**wasi-libc**~~ **Done** (`wasi-libc`); ~~**uClibc-ng**~~ **Done** (`uclibc`); ~~**dietlibc**~~ **Done** (`dietlibc`); ~~**MSVC** **UCRT**/**`VCRUNTIME`**~~ **Done** (`msvc-vcruntime`); ~~**GNU libstdc++**~~ **Done** (`cxx-runtime`); ~~**LLVM libc++**~~ **Done** (`llvm-libcxx`); ~~**LLVM libc++abi**~~ **Done** (`llvm-libcxxabi`, **`cxx-abi-runtime`**) ; ~~**MSVC** **`msvcp*.dll`**~~ **Done** (`msvcprt`) | Libc / C++ runtime + ABI grain; **finer** **UCRT**/**`VCRUNTIME`**/**legacy** **MSVCRT** **splits** **still** **optional** |
| **Toolchain law** | Binutils/ELF ABI packages per ISA | Link/load discipline |
| **OCI triad** | ~~**`oci-image-spec`** + **`oci-distribution-spec`** + **`oci-runtime-spec`**~~ **Done** | Split **image layout**, **registry HTTP**, **runtime bundle** |
| **Linux distributions** | ~~**Alpine**~~ **Done** (`alpine-linux`); ~~**Debian**~~ **Done** (`debian`); ~~**Ubuntu**~~ **Done** (`ubuntu`); ~~**Fedora**~~ **Done** (`fedora`); ~~**CentOS** **Stream**~~ **Done** (`centos-stream`); ~~**RHEL**~~ **Done** (`rhel`); ~~**Rocky**~~ **Done** (`rocky-linux`); ~~**AlmaLinux**~~ **Done** (`almalinux`); ~~**CentOS** **Linux** **(legacy)**~~ **Done** (`centos-linux`); **finer** **per**-**minor** **CentOS** **forks** **still** **optional** | Distro grain for **glibc** vs **musl** **bases** + **packaging** **law** + **Fedora→CentOS Stream→RHEL→rebuilds** **lineage** |

---

## Quality bar

- New scaffolds are **B-grade survey** until ledgers and `sources.yaml` are pinned per environment.
- Run: `python3 ATLAS/scripts/validate_frontmatter.py ATLAS` and `python3 ATLAS/scripts/validate_relations.py ATLAS` before merge-style handoff.

---

## Disambiguation

- **`00_CONSOLIDATED_ATLAS/`** — ION merge evidence; **not** this library.
- **`ATLAS/`** — external systems reference only.
