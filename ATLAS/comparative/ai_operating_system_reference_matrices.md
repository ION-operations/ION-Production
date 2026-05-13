# Comparative: AI operating system reference matrices

**Atlas scope:** Cross-cutting views for **ION** consolidation — how trust, isolation, RPC, telemetry, ML serving, and identity **compose** toward an **OS-class AI platform**. Cells cite **package slugs** and **evidence tiers** where ATLAS has them; otherwise **UNKNOWN** / survey footnotes.

**Companion:** `language_machine_and_assembly_stack.md` (languages / GPU / Wasm / **ELF** / **GNU Binutils** / **GNU GCC** / **gnu-libstdcxx** / **llvm-libcxx** / **llvm-libcxxabi** / **glibc** / **musl** / **newlib** / **wasi-libc** / **uclibc** / **dietlibc** / **msvc-vcruntime** / **msvcprt** / **GNU GDB** / **LLDB** / **LLVM lld** / **Clang**). **Evolution:** AI/OS `ATLAS_AI_OS_EXPANSION_20260403.signal.md`; data-plane `ATLAS_DATA_PLANE_20260404.signal.md`; mesh/boot/UKI `ATLAS_MESH_BOOT_UKI_20260405.signal.md`; ingress/BLS `ATLAS_INGRESS_BLS_20260406.signal.md`; ingress/TEE `ATLAS_INGRESS_TEE_20260407.signal.md`; NGINX/ARM/systemd `ATLAS_NGINX_ARM_SYSTEMD_20260408.signal.md`; cloud edge `ATLAS_CLOUD_EDGE_20260409.signal.md`; CDN/edge compute `ATLAS_CDN_EDGE_20260410.signal.md`; CDN vendors + RISC-V `ATLAS_CDN_RISCV_20260411.signal.md`; DAP `ATLAS_DEBUG_ADAPTER_PROTOCOL_20260412.signal.md`; ELF `ATLAS_ELF_OBJECT_FORMAT_20260412.signal.md`; GNU Binutils `ATLAS_GNU_BINUTILS_20260412.signal.md`; LLVM lld `ATLAS_LLVM_LLD_20260412.signal.md`; systemd unit model `ATLAS_SYSTEMD_UNIT_MODEL_20260412.signal.md`; Clang + K8s unit edges `ATLAS_CLANG_AND_K8S_SYSTEMD_20260412.signal.md`; GNU GCC `ATLAS_GNU_GCC_20260412.signal.md`; GNU GDB `ATLAS_GNU_GDB_20260412.signal.md`; LLDB `ATLAS_LLDB_20260412.signal.md`; systemd portable `ATLAS_SYSTEMD_PORTABLE_20260412.signal.md`; OCI image spec `ATLAS_OCI_IMAGE_SPEC_20260403.signal.md`; OCI distribution spec `ATLAS_OCI_DISTRIBUTION_SPEC_20260403.signal.md`; OCI runtime spec `ATLAS_OCI_RUNTIME_SPEC_20260403.signal.md`; crun `ATLAS_CRUN_20260403.signal.md`; glibc `ATLAS_GLIBC_20260403.signal.md`; musl `ATLAS_MUSL_20260403.signal.md`; GNU libstdc++ `ATLAS_GNU_LIBSTDCXX_20260403.signal.md`; LLVM libc++ `ATLAS_LLVM_LIBCXX_20260403.signal.md`; LLVM libc++abi `ATLAS_LLVM_LIBCXXABI_20260403.signal.md`; systemd sysext `ATLAS_SYSTEMD_SYSEXT_20260403.signal.md`; systemd confext `ATLAS_SYSTEMD_CONFEXT_20260403.signal.md`; Alpine Linux `ATLAS_ALPINE_LINUX_20260403.signal.md`; Debian `ATLAS_DEBIAN_20260403.signal.md`; Ubuntu `ATLAS_UBUNTU_20260403.signal.md`; Fedora `ATLAS_FEDORA_20260403.signal.md`; CentOS Stream `ATLAS_CENTOS_STREAM_20260403.signal.md`; RHEL `ATLAS_RHEL_20260403.signal.md`; Rocky + AlmaLinux `ATLAS_ROCKY_ALMALINUX_20260403.signal.md`; CentOS Linux legacy `ATLAS_CENTOS_LINUX_20260403.signal.md`; MSVC CRT `ATLAS_MSVC_RUNTIME_20260403.signal.md`; BSD libc `ATLAS_BSD_LIBC_20260403.signal.md`; NetBSD + DragonFly libc `ATLAS_NETBSD_DRAGONFLY_LIBC_20260403.signal.md`; illumos libc `ATLAS_ILLUMOS_LIBC_20260403.signal.md`; Android Bionic `ATLAS_ANDROID_BIONIC_20260403.signal.md`; newlib `ATLAS_NEWLIB_20260403.signal.md`; wasi-libc `ATLAS_WASI_LIBC_20260413.signal.md`; uClibc-ng `ATLAS_UCLIBC_20260414.signal.md`; dietlibc `ATLAS_DIETLIBC_20260415.signal.md`; libbpf `ATLAS_LIBBPF_20260416.signal.md`; io_uring + liburing `ATLAS_IO_URING_LIBURING_20260417.signal.md`; Landlock `ATLAS_LANDLOCK_20260418.signal.md`; seccomp + libseccomp `ATLAS_SECCOMP_LIBSECCOMP_20260419.signal.md`; Linux namespaces `ATLAS_LINUX_NAMESPACES_20260420.signal.md`; Linux cgroups `ATLAS_LINUX_CGROUPS_20260421.signal.md`; Linux capabilities `ATLAS_LINUX_CAPABILITIES_20260422.signal.md`; Linux OverlayFS `ATLAS_LINUX_OVERLAYFS_20260423.signal.md`; Linux netfilter `ATLAS_LINUX_NETFILTER_20260424.signal.md`; Linux FUSE `ATLAS_LINUX_FUSE_20260425.signal.md`; Linux KVM `ATLAS_LINUX_KVM_20260426.signal.md`; Virtio `ATLAS_VIRTIO_20260427.signal.md`; Linux vhost `ATLAS_LINUX_VHOST_20260428.signal.md`; Linux VFIO `ATLAS_LINUX_VFIO_20260403.signal.md`; QEMU `ATLAS_QEMU_20260404.signal.md`; libvirt `ATLAS_LIBVIRT_20260405.signal.md`; KubeVirt `ATLAS_KUBEVIRT_20260406.signal.md`; Kata Containers `ATLAS_KATA_CONTAINERS_20260407.signal.md`; gVisor gvisor `ATLAS_GVISOR_20260408.signal.md`; BuildKit buildkit `ATLAS_BUILDKIT_20260409.signal.md`; Helm helm `ATLAS_HELM_20260410.signal.md`; Flux fluxcd `ATLAS_FLUXCD_20260411.signal.md`; Argo CD argo-cd `ATLAS_ARGO_CD_20260412.signal.md`; Kustomize kustomize `ATLAS_KUSTOMIZE_20260413.signal.md`.

---

## 1. Trust, attestation, and boot

| Stage | Representative slugs | Role |
|-------|----------------------|------|
| Firmware handoff | `uefi` | Pre-boot interface; boot services → runtime handoff to OS loader. |
| Loaders / UKI | `grub`, `systemd-boot`, `unified-kernel-image` | Boot menu / stub / combined PE+kernel+initrd artifact (UAPI UKI spec + distro tooling). |
| Loader menu spec (UAPI.1) | `uapi-boot-loader-specification` | Distribution-independent boot loader menu file naming and drop-ins (UAPI Group DOCUMENTED). |
| Root of trust | `tpm2` | TCG TPM 2.0 commands; measured boot / key storage (tier per claim). |
| Kernel MAC | `linux-security-modules`, `linux-kernel` | LSM hooks; SELinux / AppArmor-class policy on Linux. |
| TEE / confidential workloads | `confidential-computing`, `intel-tdx`, `amd-sev`, `arm-cca` | Survey umbrella plus x86 and Arm CCA grains (`DOCUMENTED` vendor portals); normative microarch per CPU generation. |

**ION mapping:** Aligns with **AuthorityClass**, **continuity law**, and **governance chain** — *who vouches for which layer* must not be conflated across projections.

---

## 2. Isolation and sandboxes

| Mechanism | Slugs | Notes |
|-----------|--------|--------|
| Browser / module sandbox | `webassembly`, `wasi`, `wasm-component-model` | Capability-based imports; no implicit POSIX. |
| OS containers | `docker`, `containerd`, `kata-containers`, `gvisor`, `kubernetes` (orchestration) | Share host kernel; **`linux-namespaces`** + **`linux-cgroups`** **on** **Linux** — **engines** **are** **not** **those** **kernel** **primitives** **alone**. **`kata-containers`** **adds** **VM-isolated** **OCI** **runtimes** **(see** **§2** **Kata** **row).** **`gvisor`** **`runsc`** **adds** **userspace** **syscall** **interposition** **(see** **§2** **gVisor** **row).** |
| MicroVM | `firecracker` | **`linux-kvm`** **+** **`virtio`** **on** **Linux** — **minimal** **guest** **VMs** **(see** **`firecracker`**) **vs** **namespaced** **containers** **in** **this** **matrix.** |
| Linux KVM (hardware virtualization API) | `linux-kvm` | **Kernel** **`/dev/kvm`** **hypervisor** **ABI** — **not** **`linux-namespaces`** **/** **`linux-cgroups`** **(containers)** **or** **`firecracker`** **(VMM)** **alone**. |
| Virtio (paravirtual I/O) | `virtio` | **Virtqueues** **/** **device** **model** **for** **guest** **I/O** — **not** **`linux-kvm`** **(hypervisor** **API)** **or** **`firecracker`** **(VMM)** **alone**. |
| Linux vhost (virtio host backends) | `linux-vhost` | **Kernel** **/** **vhost-user** **acceleration** **for** **virtio** **queues** **on** **the** **host** — **not** **`virtio`** **(guest** **contract)** **or** **`linux-kvm`** **(hypervisor** **API)** **alone**. |
| Linux VFIO (device passthrough) | `linux-vfio` | **IOMMU-backed** **device** **assignment** **/** **VFIO** **userspace** **driver** **API** — **not** **`virtio`** **(paravirtual** **devices)** **or** **`linux-kvm`** **(hypervisor** **API)** **alone**. |
| QEMU (VMM / emulator) | `qemu` | **Userspace** **VMM** **/** **emulator** **composing** **`linux-kvm`**, **`virtio`**, **`linux-vhost`**, **`linux-vfio`** **on** **typical** **Linux** **hosts** — **not** **`linux-kvm`** **(kernel** **API)** **alone** **or** **`firecracker`** **(microVM** **VMM)** **alone**. |
| libvirt (virtualization management) | `libvirt` | **Host** **virtualization** **management** **API** **/** **daemon** **(commonly** **QEMU/KVM)** — **not** **`qemu`** **(VMM** **binary)** **alone,** **`linux-kvm`** **(kernel** **API)** **alone,** **or** **`kubernetes`** **(cluster** **orchestrator)** **alone.** |
| KubeVirt (VMs on Kubernetes) | `kubevirt` | **Kubernetes** **extension** **for** **VM** **workloads** **(CRDs/controllers)** **on** **QEMU/KVM** **nodes** — **not** **`kubernetes`** **(default** **pod/OCI** **model)** **alone,** **`libvirt`** **(node** **management** **daemon)** **alone,** **or** **`qemu`** **(VMM)** **alone.** |
| Kata Containers (VM-isolated OCI) | `kata-containers` | **OCI** **runtime** **stack** **using** **lightweight** **VMs** **(QEMU/KVM** **on** **Linux)** — **not** **`runc`** **(namespace** **OCI** **runtime)** **alone,** **`kubevirt`** **(Kubernetes** **VM** **CRDs),** **or** **`qemu`** **(VMM)** **alone.** |
| gVisor (runsc — userspace kernel) | `gvisor` | **OCI** **runtime** **using** **userspace** **syscall** **interposition** **(application** **kernel)** — **not** **`runc`** **(namespace** **OCI** **runtime)** **alone,** **`kata-containers`** **(VM-isolated** **OCI),** **or** **`linux-kernel`** **(host** **kernel** **facility)** **alone.** |
| In-kernel policy | `ebpf` | Verified programs for trace/network/security hooks. |
| BPF userspace loaders | `libbpf` | Reference C library for the BPF syscall uAPI; **not** in-kernel bytecode (`ebpf`). |
| Linux async I/O (io_uring) | `io-uring`, `liburing` | Kernel io_uring uAPI + **`liburing`** userspace helpers — **not** **`ebpf`** / **`libbpf`**. |
| Linux unprivileged sandbox (LSM) | `landlock` | Filesystem-oriented **Landlock** rules without SELinux/AppArmor policy languages; **not** **`ebpf`** / **`libbpf`** / **`io-uring`**. |
| Linux syscall filtering (seccomp) | `seccomp`, `libseccomp` | Kernel **seccomp**/**seccomp-filter** + **`libseccomp`** helpers — **not** **`ebpf`**/**`libbpf`** (general attach) or **`landlock`** (filesystem LSM). |
| Linux kernel namespaces | `linux-namespaces` | mnt/UTS/IPC/PID/net/user/cgroup/time **views** — **not** **`docker`**/**`kubernetes`** (engines) **or** **`oci-runtime-spec`** (bundle law) **alone**. |
| Linux cgroups (resource control) | `linux-cgroups` | cgroup **v2** **controllers** **(CPU/memory/io/…)** — **not** **`linux-namespaces`** **(visibility)** **or** **`docker`** **(engine)** **alone**. |
| Linux capabilities (POSIX `CAP_*`) | `linux-capabilities` | **Permitted/effective/inheritable/bounding** **sets** **—** **not** **`linux-security-modules`** **(MAC)** **or** **`seccomp`** **(syscall** **filters)** **alone**. |
| Linux OverlayFS (union filesystem) | `linux-overlayfs` | **Kernel** **overlay** **driver** **(lower/upper/work,** **merged** **view)** — **not** **`oci-image-spec`** **/** **`oci-runtime-spec`** **/** **`docker`** **(engine)** **alone**. |
| Linux FUSE (userspace filesystem bridge) | `linux-fuse` | **Kernel** **`/dev/fuse`** **bridge** **to** **userspace** **filesystem** **daemons** — **not** **`linux-overlayfs`** **(in-kernel** **stacked** **fs)** **or** **`oci-image-spec`** **alone**. |
| GPU contexts | `vulkan`, `cuda` (platform), `metal`, `webgpu` | Distinct from process sandbox; **driver trust** dominates. |

---

## 3. Scheduling and data movement (survey)

| Concern | Slugs | Tier discipline |
|---------|--------|-----------------|
| Cluster scheduling | `kubernetes`, `nomad` | DOCUMENTED API + INFERRED deployment defaults. |
| GPU collectives | `nccl`, `nvidia-cuda` | Training/inference scale-out; vendor-specific. |
| Object artifacts | `amazon-s3` | Model checkpoints, datasets — **not** POSIX fs. |
| Telemetry export | `opentelemetry` | OTLP; often paired with `grpc` or HTTP. |

---

## 4. RPC, edge, and agent I/O

| Layer | Slugs | Notes |
|-------|--------|--------|
| L7 RPC | `grpc` | Protobuf services over HTTP/2 (normative gRPC docs). |
| Modern web transport | `http3` | QUIC + HTTP/3 (RFC 9000 / 9114). |
| Ingress / edge (dynamic) | `traefik`, `envoy`, `emissary-ingress`, `haproxy`, `nginx`, `ingress-nginx` | Kubernetes ingress / Gateway-class edge; `ingress-nginx` depends on NGINX datapath; DOCUMENTED per product. |
| Managed cloud L7 / API edge | `aws-elastic-load-balancing`, `amazon-api-gateway`, `azure-application-gateway`, `gcp-load-balancing` | Vendor-managed load balancers and HTTP API front doors; typically pair with `aws-eks`, `azure-aks`, `gcp-gke` (INFERRED). |
| Global CDN / edge compute | `azure-front-door`, `amazon-cloudfront`, `cloudflare-workers`, `fastly`, `akamai`, `edgio` | PoP-scale caching, routing, WAF; vendor-specific edge compute (e.g. Workers, Compute@Edge) (`DOCUMENTED` per vendor). |
| Agent tools | `model-context-protocol` | JSON-RPC message shape; **not** gRPC. |
| IDE services | `language-server-protocol` | Language intelligence; analogous *host/server* split to MCP. |
| IDE debugging | `debug-adapter-protocol` | JSON-RPC between **debug client** and **debug adapter**; breakpoints, threads, variables — orthogonal to LSP and MCP. |

**Forbidden merge:** Do not equate **MCP JSON-RPC** with **gRPC** — different IDL and framing.  
**Forbidden merge:** Do not equate **DAP** with **LSP** or **MCP** — different capability contracts on the same host.

---

## 5. ML interchange and serving

| Concern | Slugs | Notes |
|---------|--------|-------|
| Model graph IR | `onnx` | Exchange format; not a trainer. |
| Multi-backend serving | `nvidia-triton-inference-server` | gRPC/HTTP APIs per NVIDIA docs. |
| LLM serving engine | `vllm` | PagedAttention / OpenAI-compatible surfaces in common deployments. |
| GPU stack | `nvidia-cuda`, `amd-rocm`, `llvm-ir` | Compilation and runtime adjacency. |

---

## 6. Identity and cluster auth

| Concern | Slugs | Notes |
|---------|--------|-------|
| OIDC | `openid-connect` | ID Tokens on OAuth 2.0; kube-apiserver OIDC integration is a **common pattern** (INFERRED deployment). |

---

## 7. Observability

| Concern | Slugs | Notes |
|---------|--------|-------|
| Traces / metrics / logs | `opentelemetry` | OTLP wire formats; backends are **out of package** unless added. |
| Kernel/runtime introspection | `ebpf`, `libbpf`, `linux-kernel` | **`ebpf`** in-kernel execution; **`libbpf`** userspace loader/API — **not** conflating bytecode vs library. |

---

## 8. Data stores, streaming, mesh, boot (2026-04-04 wave)

| Concern | Slugs | Notes |
|---------|--------|--------|
| Relational server | `postgresql` | Wire protocol + SQL dialect (DOCUMENTED docs). |
| Embedded SQL | `sqlite` | Library / file format; not network-first. |
| Cache / structures | `redis` | RESP; persistence modes vary by deployment. |
| Event log | `apache-kafka` | Partitioned topics; not a SQL store. |
| L7 data plane | `envoy` | xDS-configured proxy; pairs with mesh. |
| Service mesh (Envoy-centric) | `istio` | Control plane + Envoy data plane (DOCUMENTED architecture). |
| Service mesh (lightweight) | `linkerd` | Kubernetes-first mesh; own proxy model (`DOCUMENTED` Linkerd docs). |
| eBPF CNI / mesh | `cilium` | eBPF datapath on Linux; Kubernetes CNI + optional L7 / Gateway (`DOCUMENTED` Cilium docs). |
| Linux netfilter (iptables/nftables) | `linux-netfilter` | Kernel **hook** **framework** **for** **L3/L4** **filter/NAT/ct** — **not** **`ebpf`** **/** **`cilium`** **(eBPF** **datapath)** **or** **`envoy`** **(L7** **proxy)** **alone**. |
| Linux async I/O (io_uring) | `io-uring`, `liburing` | Kernel submission/completion queues + **`liburing`** C library — **not** **`ebpf`** / **`libbpf`** / **`cilium`** (different concerns). |
| Service catalog / Connect | `consul` | Discovery, health, KV, Consul Connect (mTLS); mesh-adjacent vs `istio` / `linkerd` (DOCUMENTED HashiCorp docs). |
| Boot loader | `grub` | Pre-kernel; UEFI/BIOS paths (`uefi`). |
| UEFI stub loader | `systemd-boot` | Minimal systemd-project loader; UKI consumer on many images. |
| UKI artifact | `unified-kernel-image` | PE binary bundling kernel + initrd + cmdline (UAPI.5 + `systemd.ukify`). |
| Host init / portable / UKI tooling | `systemd` | PID 1 suite; `ukify` and related manuals on freedesktop (`DOCUMENTED`); edges to `systemd-boot`, `unified-kernel-image`, `systemd-portable`, `systemd-sysext`, `systemd-confext`. |
| **systemd portable bundles** | `systemd-portable` | **`portablectl`** + portable **OS-tree** images — **not** OCI/Docker (`docker`); **`integrates_with`** **`systemd`**, **`systemd-unit-model`** ([systemd.io portable services](https://systemd.io/PORTABLE_SERVICES/)). |
| **systemd system extensions** | `systemd-sysext` | **`systemd-sysext`** **/** **`systemd-sysext.service`** — **read-only** **images** **merged** **into** **`/usr`** **(etc.)** **via** **overlay**; **not** **`systemd-confext`**, **`systemd-portable`**, **`docker`**, **or** **`oci-image-spec`**; **`integrates_with`** **`systemd`**, **`systemd-confext`**, **`systemd-unit-model`**, **`linux-kernel`** ([systemd-sysext(1)](https://www.freedesktop.org/software/systemd/man/latest/systemd-sysext.html)). |
| **systemd configuration extensions** | `systemd-confext` | **`systemd-confext`** **/** **`systemd-confext.service`** — **read-only** **images** **merged** **into** **`/etc`**-**class** **trees** **via** **overlay**; **not** **`systemd-sysext`**, **`systemd-portable`**, **`docker`**, **or** **`oci-image-spec`**; **`integrates_with`** **`systemd`**, **`systemd-sysext`**, **`systemd-unit-model`**, **`linux-kernel`** ([systemd-confext(1)](https://www.freedesktop.org/software/systemd/man/latest/systemd-confext.html)). |
| **OCI container image format** | `oci-image-spec` | **Manifest / index / config / layers** — **not** **`docker`** (engine), **registry HTTP API** alone (`oci-distribution-spec`), or **runtime bundle law** alone (`oci-runtime-spec`); **`integrates_with`** **`oci-distribution-spec`**, **`oci-runtime-spec`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`buildkit`**, **`helm`**, **`fluxcd`**, **`argo-cd`**, **`runc`**, **`crun`** ([opencontainers/image-spec](https://github.com/opencontainers/image-spec)). |
| **OCI registry distribution API** | `oci-distribution-spec` | **HTTP** pull/push for manifests/blobs; **not** **image JSON** (`oci-image-spec`) or **runtime bundle** (`oci-runtime-spec`); **`integrates_with`** **`oci-image-spec`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`podman`**, **`cri-o`**, **`helm`**, **`buildkit`**, **`fluxcd`**, **`argo-cd`** ([opencontainers/distribution-spec](https://github.com/opencontainers/distribution-spec)). |
| **BuildKit (OCI image build)** | `buildkit` | **DAG** **image** **build** **/** **export** **toward** **OCI** **manifests** **and** **blobs** — **not** **`oci-runtime-spec`** **(bundle** **execution** **law)** **alone,** **`runc`** **(low-level** **runtime),** **or** **`oci-image-spec`** **(format-only** **spec)** **as** **the** **build** **engine** **itself**; **`integrates_with`** **`oci-image-spec`**, **`oci-distribution-spec`**, **`docker`**, **`containerd`**, **`kubernetes`** ([moby/buildkit](https://github.com/moby/buildkit)). |
| **OCI runtime bundle spec** | `oci-runtime-spec` | **`config.json`** + **`rootfs`** + lifecycle — **not** **image layers** (`oci-image-spec`) or **registry** (`oci-distribution-spec`); **`runc`** (reference) and **`crun`** **implement** **`oci-runtime-spec`**; **`integrates_with`** **`oci-image-spec`**, **`linux-kernel`**, **`crun`**, **`docker`**, **`containerd`**, **`kubernetes`**, **`podman`**, **`cri-o`**, **`runc`** ([opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec)). |
| **Low-level OCI runtime (crun)** | `crun` | C **executor** on **Linux**; **`implements`** **`oci-runtime-spec`**; **`competes_with`** **`runc`**; **`integrates_with`** **`linux-kernel`**, **`containerd`**, **`podman`**, **`cri-o`**, **`oci-image-spec`**; **`kubernetes`** (**INFERRED**, CRI-configured nodes) ([containers/crun](https://github.com/containers/crun)). |
| **systemd unit grammar** | `systemd-unit-model` | `.service` / `.socket` / `.target` **directive** model, **drop-ins**, **systemd.generator(7)** — **declarative law** slice adjacent to **`systemd`**. |
| **K8s Linux node services** | `kubernetes` | **`integrates_with`** **`systemd`** / **`systemd-unit-model`** — kubelet, runtime, and node agents commonly installed as **unit files** (`INFERRED`). |
| **Helm (Kubernetes charts)** | `helm` | **Chart** **packaging** **/** **templating** **/** **release** **lifecycle** **against** **the** **Kubernetes** **API** — **not** **`kubernetes`** **(orchestrator** **/** **control** **plane** **itself)** **alone,** **`oci-runtime-spec`** **(bundle** **execution),** **or** **`oci-image-spec`** **(container** **image** **format** **law)** **alone**; **`depends_on`** **`kubernetes`**; **`integrates_with`** **`oci-distribution-spec`** **(OCI** **charts),** **`oci-image-spec`** **(image** **references)** ([helm.sh](https://helm.sh/docs/)). |
| **Flux (GitOps for Kubernetes)** | `fluxcd` | **Continuous** **reconciliation** **from** **Git/OCI** **sources** **via** **controllers** **/** **CRDs** — **not** **`kubernetes`** **(orchestrator** **itself),** **`helm`** **(CLI** **chart** **client** **alone),** **or** **`oci-runtime-spec`** **(bundle** **execution)**; **`depends_on`** **`kubernetes`**; **`integrates_with`** **`helm`**, **`oci-image-spec`**, **`oci-distribution-spec`** ([fluxcd.io](https://fluxcd.io/flux/)). |
| **Argo CD (GitOps delivery)** | `argo-cd` | **Declarative** **GitOps** **CD** **with** **Application** **CRDs** **/** **UI** **—** **not** **`kubernetes`** **(orchestrator** **itself),** **`helm`** **(packaging** **tool** **alone),** **`fluxcd`** **(other** **GitOps** **controller),** **or** **`oci-runtime-spec`**; **`depends_on`** **`kubernetes`**; **`integrates_with`** **`helm`**, **`oci-image-spec`**, **`oci-distribution-spec`**; **`competes_with`** **`fluxcd`** ([argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/)). |
| **Alpine Linux (distro)** | `alpine-linux` | **`linux-distribution`** — **`musl`** + **`apk`** + **OpenRC** **defaults** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`debian`**, **`ubuntu`**, **`fedora`**, **`centos-stream`**, **`rhel`**, **`rocky-linux`**, **`almalinux`**, **`centos-linux`** (INFERRED); **`integrates_with`** **`musl`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`** ([Alpine about](https://alpinelinux.org/about/)). |
| **Debian (distro)** | `debian` | **`linux-distribution`** — **`glibc`** + **`dpkg`**/**`apt`** + **`systemd`** **defaults** **on** **stable** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`** (INFERRED); **`influences`** **`ubuntu`** (`DOCUMENTED`); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`** ([Debian releases](https://www.debian.org/releases/stable/)). |
| **Ubuntu (distro)** | `ubuntu` | **`linux-distribution`** — **`glibc`** + **`dpkg`**/**`apt`** + **`systemd`** **defaults** (`DOCUMENTED`); **`fork_of`** **`debian`**; **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`** (INFERRED); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`clang`** (INFERRED) ([Ubuntu release cycle](https://ubuntu.com/about/release-cycle)). |
| **Fedora Linux (distro)** | `fedora` | **`linux-distribution`** — **`glibc`** + **`rpm`**/**`dnf`** + **`systemd`** **defaults** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`** (INFERRED); **`influences`** **`centos-stream`**, **`rhel`** (`DOCUMENTED`); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`clang`** (INFERRED) ([Fedora releases](https://docs.fedoraproject.org/en-US/releases/)). |
| **CentOS Stream (distro)** | `centos-stream` | **`linux-distribution`** — **`glibc`** + **`rpm`**/**`dnf`** + **`systemd`** **defaults** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`** (INFERRED); **`fedora`** **`influences`** **`centos-stream`** (`DOCUMENTED`); **`influences`** **`rhel`** (`DOCUMENTED`); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`clang`** (INFERRED) ([CentOS Stream](https://www.centos.org/centos-stream/)). |
| **RHEL (distro)** | `rhel` | **`linux-distribution`** — **`glibc`** + **`rpm`**/**`dnf`** + **`systemd`** **defaults** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`** (INFERRED); **`centos-stream`** **`influences`** **`rhel`** (`DOCUMENTED`); **`influences`** **`rocky-linux`**, **`almalinux`** (`DOCUMENTED`); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`red-hat-openshift`**, **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`clang`** (INFERRED) ([Red Hat Enterprise Linux](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux)). |
| **Rocky Linux (distro)** | `rocky-linux` | **`linux-distribution`** — **`glibc`** + **`rpm`**/**`dnf`** + **`systemd`** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`**, **`almalinux`**, **`centos-linux`** (INFERRED); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`clang`** (INFERRED) ([Rocky Linux](https://rockylinux.org/about)). |
| **AlmaLinux (distro)** | `almalinux` | **`linux-distribution`** — **`glibc`** + **`rpm`**/**`dnf`** + **`systemd`** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`**, **`rocky-linux`**, **`centos-linux`** (INFERRED); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`clang`** (INFERRED) ([AlmaLinux](https://almalinux.org/)). |
| **CentOS Linux (legacy)** | `centos-linux` | **`linux-distribution`** — **`glibc`** + **`rpm`**/**`yum`**/**`dnf`** + **`systemd`** **on** **supported** **releases** (`DOCUMENTED`); **`depends_on`** **`linux-kernel`**; **`competes_with`** **`alpine-linux`**, **`rocky-linux`**, **`almalinux`** (INFERRED); **`rhel`** **`influences`** **`centos-linux`** (`DOCUMENTED`); **`integrates_with`** **`glibc`**, **`systemd`**, **`systemd-unit-model`**, **`gnu-libstdcxx`**, **`docker`**, **`oci-image-spec`**, **`containerd`** (INFERRED), **`kubernetes`** (INFERRED), **`gnu-gcc`**, **`gnu-binutils`**, **`elf`**, **`clang`** (INFERRED); **EOL** **fixed**-**minor** **line** **distinct** **from** **`centos-stream`** ([CentOS project communications](https://blog.centos.org/)). |

---

## 9. Toolchain object format (Unix-class + BSD + illumos + Android Bionic + newlib + wasi-libc + uclibc + dietlibc + Windows MSVC CRT)

| Concern | Slugs | Notes |
|---------|--------|-------|
| ELF containers | `elf` | Object / executable / `.so` layout; **not** ISA, **not** DWARF encoding itself — edges link those packages. |
| GNU toolchain utilities | `gnu-binutils` | **as** / **ld** / inspectors — **implements** link + inspect for ELF; **not** the ELF spec (`elf`) and **not** GCC itself (`c-language` adjacency). |
| LLVM linker | `llvm-lld` | **lld** — link stage in LLVM/**clang**/**rustc** stacks; **`competes_with`** `gnu-binutils` (**ld**); still **not** full Binutils (**as**/**readelf** remain separate concerns). |
| **Clang** | `clang` | LLVM **C/C++ front end** + driver; **`integrates_with`** **`llvm-ir`**, **`llvm-lld`**, **`gnu-binutils`**, **`llvm-libcxx`**, **`llvm-libcxxabi`**, **`language-server-protocol`** (**clangd**); **not** the IR spec or the linker package alone. |
| **GNU GCC** | `gnu-gcc` | **gcc**/**g++**; **`integrates_with`** **`gnu-binutils`**, **`c-language`**, **`elf`**, **`dwarf`**, **`linux-kernel`**, **`riscv-isa`**; **`competes_with`** **`clang`**; **not** **as**/**ld** themselves (`gnu-binutils`). |
| **GNU GDB** | `gnu-gdb` | **gdb** / **gdbserver**; **`integrates_with`** **`dwarf`**, **`elf`**, **`gnu-gcc`**, **`clang`**, **`c-language`**; **`integrates_with`** **`debug-adapter-protocol`** (**INFERRED** adapter bridge); **not** DWARF spec or DAP wire format. |
| **LLDB** | `lldb` | LLVM debugger; **`integrates_with`** **`clang`**, **`dwarf`**, **`elf`**, **`c-language`**, **`debug-adapter-protocol`** (**lldb-dap** / adapters); **`competes_with`** **`gnu-gdb`**; **not** Clang or DWARF. |
| **GNU C Library** | `glibc` | **C**/**POSIX** **userland** **runtime** + **dynamic** **linker**; **not** **`linux-kernel`**, **`gnu-gcc`**, **`elf`** spec, or **`musl`**; **`competes_with`** **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`linux-kernel`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`**, **`clang`** (INFERRED), **`gnu-gdb`**, **`lldb`** (INFERRED), **`riscv-isa`**, **`debian`**, **`ubuntu`**, **`fedora`**, **`centos-stream`**, **`rhel`**, **`rocky-linux`**, **`almalinux`**, **`centos-linux`** ([GNU libc manual](https://www.gnu.org/software/libc/manual/)). |
| **musl libc** | `musl` | **Lightweight** **Linux** **libc** (static-link friendly); **not** **`glibc`** (ABI); **`competes_with`** **`glibc`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`gnu-gdb`** (INFERRED), **`lldb`** (INFERRED), **`riscv-isa`**, **`docker`** (INFERRED), **`alpine-linux`** ([musl.libc.org](https://musl.libc.org/)). |
| **FreeBSD libc** | `freebsd-libc` | **FreeBSD** **base** **libc** **+** **dynamic** **linker**; **not** **`glibc`**/**`musl`**; **`integrates_with`** **`freebsd`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([FreeBSD Handbook](https://docs.freebsd.org/en/books/handbook/bibliography/)). |
| **OpenBSD libc** | `openbsd-libc` | **OpenBSD** **base** **libc**; **not** **`freebsd-libc`**; **`integrates_with`** **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`freebsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([OpenBSD FAQ](https://www.openbsd.org/faq/)). |
| **NetBSD libc** | `netbsd-libc` | **NetBSD** **base** **libc**; **`integrates_with`** **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`freebsd-libc`**, **`openbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([NetBSD Guide](https://www.netbsd.org/docs/guide/en/)). |
| **DragonFly libc** | `dragonfly-libc` | **DragonFly** **base** **libc**; **`integrates_with`** **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([DragonFly Handbook](https://www.dragonflybsd.org/docs/handbook/)). |
| **illumos libc** | `illumos-libc` | **illumos** **core** **libc** **(Solaris/ON** **lineage)**; **`integrates_with`** **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([illumos developer guide](https://illumos.org/books/dev/intro.html)). |
| **Android Bionic** | `android-bionic` | **Android** **Bionic** **libc**; **`integrates_with`** **`android-aosp`**, **`linux-kernel`**, **`elf`**, **`c-language`**, **`clang`** (INFERRED), **`llvm-libcxx`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([AOSP platform/bionic](https://android.googlesource.com/platform/bionic/+/refs/heads/main/README.md)). |
| **newlib** | `newlib` | **Embedded** **GCC** **libc** **(Sourceware)**; **`integrates_with`** **`c-language`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`riscv-isa`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([Sourceware newlib](https://sourceware.org/newlib/)). |
| **wasi-libc** | `wasi-libc` | **WASI** **C** **library** **for** **`wasm32-wasi`** **(LLVM** **sysroot)**; **`integrates_with`** **`wasi`**, **`webassembly`**, **`c-language`**, **`clang`**, **`llvm-lld`**, **`wasm-component-model`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([wasi-libc](https://github.com/WebAssembly/wasi-libc)). |
| **uClibc-ng** | `uclibc` | **Small** **Linux** **libc** **(embedded** **GNU/Linux)**; **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`riscv-isa`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`dietlibc`** (INFERRED) ([uClibc-ng](https://uclibc-ng.org/)). |
| **dietlibc** | `dietlibc` | **Minimal** **Linux** **libc** **(static-friendly)**; **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`** (INFERRED) ([dietlibc](https://www.fefe.de/dietlibc/)). |
| **GNU libstdc++** | `gnu-libstdcxx` | **ISO C++** **stdlib** **with** **GCC**; **not** **`gnu-gcc`** (compiler), **`glibc`**/**`musl`** (C **libc**), or **`elf`**; **`integrates_with`** **`gnu-gcc`**, **`glibc`**, **`musl`** (INFERRED), **`freebsd-libc`** (INFERRED), **`openbsd-libc`** (INFERRED), **`netbsd-libc`** (INFERRED), **`dragonfly-libc`** (INFERRED), **`illumos-libc`** (INFERRED), **`android-bionic`** (INFERRED), **`newlib`** (INFERRED), **`wasi-libc`** (INFERRED), **`uclibc`** (INFERRED), **`dietlibc`** (INFERRED), **`gnu-binutils`**, **`elf`**, **`dwarf`**, **`c-language`** (INFERRED), **`clang`** (INFERRED), **`gnu-gdb`**, **`lldb`** (INFERRED), **`riscv-isa`**, **`debian`**, **`ubuntu`**, **`fedora`**, **`centos-stream`**, **`rhel`**, **`rocky-linux`**, **`almalinux`**, **`centos-linux`**; **`competes_with`** **`llvm-libcxx`**, **`msvcprt`** (INFERRED) ([GCC libstdc++ docs](https://gcc.gnu.org/onlinedocs/libstdc++/)). |
| **LLVM libc++** | `llvm-libcxx` | **ISO C++** **stdlib** **in** **the** **LLVM** **ecosystem**; **not** **`clang`** (compiler), **`llvm-lld`** (linker), **or** **`llvm-libcxxabi`** (ABI **runtime**); **`integrates_with`** **`llvm-libcxxabi`**, **`clang`**, **`llvm-lld`**, **`glibc`**, **`musl`** (INFERRED), **`freebsd-libc`** (INFERRED), **`openbsd-libc`** (INFERRED), **`netbsd-libc`** (INFERRED), **`dragonfly-libc`** (INFERRED), **`illumos-libc`** (INFERRED), **`android-bionic`** (INFERRED), **`newlib`** (INFERRED), **`wasi-libc`** (INFERRED), **`uclibc`** (INFERRED), **`dietlibc`** (INFERRED), **`gnu-binutils`**, **`elf`**, **`dwarf`**, **`c-language`** (INFERRED), **`gnu-gdb`** (INFERRED), **`lldb`**, **`riscv-isa`**; **`competes_with`** **`gnu-libstdcxx`**, **`msvcprt`** (INFERRED) ([libc++ docs](https://libcxx.llvm.org/)). |
| **LLVM libc++abi** | `llvm-libcxxabi` | **Itanium** **C++** **ABI** **runtime** (**exceptions**, **RTTI**, …); **`cxx-abi-runtime`** — **not** **`llvm-libcxx`** (stdlib), **`clang`**, **or** **`llvm-lld`**; **`integrates_with`** **`llvm-libcxx`**, **`clang`**, **`llvm-lld`**, **`glibc`**, **`musl`** (INFERRED), **`freebsd-libc`** (INFERRED), **`openbsd-libc`** (INFERRED), **`netbsd-libc`** (INFERRED), **`dragonfly-libc`** (INFERRED), **`illumos-libc`** (INFERRED), **`android-bionic`** (INFERRED), **`newlib`** (INFERRED), **`wasi-libc`** (INFERRED), **`uclibc`** (INFERRED), **`dietlibc`** (INFERRED), **`gnu-binutils`**, **`elf`**, **`dwarf`**, **`c-language`** (INFERRED), **`gnu-gdb`** (INFERRED), **`lldb`**, **`riscv-isa`** ([libc++abi docs](https://libcxxabi.llvm.org/)). |
| **MSVC UCRT / VCRUNTIME** | `msvc-vcruntime` | **Windows** **UCRT** **+** **`VCRUNTIME*.dll`** **CRT** **surface**; **not** **`glibc`**/**`musl`**; **`integrates_with`** **`windows-nt`**, **`c-language`**, **`clang`** (INFERRED), **`msvcprt`** ([CRT features](https://learn.microsoft.com/en-us/cpp/c-runtime-library/crt-library-features)). |
| **MSVC C++ runtime** | `msvcprt` | **Windows** **`msvcp*.dll`** **C++** **stdlib** **runtime**; **not** **`gnu-libstdcxx`**/**`llvm-libcxx`** **(Unix)**; **`integrates_with`** **`windows-nt`**, **`msvc-vcruntime`**, **`c-language`**; **`competes_with`** **`gnu-libstdcxx`**, **`llvm-libcxx`** (INFERRED) ([C++ standard library](https://learn.microsoft.com/en-us/cpp/standard-library/cpp-standard-library-reference)). |

---

## 10. Open gaps (honest)

- Niche CDN / regional PoP networks beyond seeded vendors — not exhaustive.
- Proprietary NGINX Plus-only behaviors as a dedicated package — not seeded.
- RISC-V confidential-compute extensions as separate packages from `riscv-isa` — not split yet.
- `systemd` **generator implementation** internals beyond **systemd.generator(7)** contract — not split (see `systemd-unit-model` for the documented generator **interface**).
- **Finer** **split** **of** **UCRT** **vs** **`VCRUNTIME*.dll`** **vs** **legacy** **MSVCRT** **as** **separate** **`c-runtime`** **packages** — not split (**`msvc-vcruntime`** **covers** **the** **survey** **DLL** **family**).
- **Per**-**minor** **fork** **packages** **(e.g.** **CentOS** **Linux** **7** **vs** **8** **as** **separate** **`linux-distribution`** **slugs)** — not split (**`centos-linux`** **covers** **the** **EOL** **fixed**-**minor** **rebuild** **line** **as** **one** **survey** **package**).

---

## Forbidden merges

- Treating **S3** as a **POSIX** **filesystem**.  
- Treating **ONNX** as **inference** **without** **a** **runtime** **package**.  
- Collapsing **MCP** and **gRPC** because both appear in “cloud” diagrams.  
- Treating **ELF** as **the ISA** or as **DWARF** — container vs machine code vs debug encoding (`elf`, ISA packages, `dwarf`).  
- Treating **`gnu-binutils`** as **the ELF standard** or as **the compiler** — toolchain vs format vs GCC (`gnu-binutils`, `elf`, `c-language`).  
- Treating **`llvm-lld`** as **all of LLVM**, **GNU Binutils**, or **the ELF spec** — linker subproject only (`llvm-lld`, `llvm-ir`, `gnu-binutils`, `elf`).  
- Treating **`systemd-unit-model`** as **the full systemd project** — grammar slice only (`systemd-unit-model` vs `systemd`).  
- Treating **`clang`** as **LLVM IR** or as **the linker** — front end/driver vs `llvm-ir` vs `llvm-lld` / `gnu-binutils`.  
- Treating **`gnu-gcc`** as **`gnu-binutils`** or as **`llvm-ir`** — compiler vs assembler/linker vs LLVM IL (`gnu-gcc`, `gnu-binutils`, `llvm-ir`).  
- Treating **`gnu-gdb`** as **`dwarf`** or as **`debug-adapter-protocol`** — debugger vs debug encoding vs IDE JSON-RPC (`gnu-gdb`, `dwarf`, `debug-adapter-protocol`).  
- Treating **`lldb`** as **`clang`** or as **`dwarf`** — debugger vs compiler vs debug encoding (`lldb`, `clang`, `dwarf`).  
- Treating **`systemd-portable`** as **`docker`** or as **all of systemd** — portable OS-tree bundles vs OCI vs full suite (`systemd-portable`, `docker`, `systemd`).  
- Treating **`systemd-sysext`** as **`systemd-portable`** or as **`docker`** — **sysext** **`/usr`** **merge** vs **`portablectl`** **attach** vs **container** **roots** (`systemd-sysext`, `systemd-portable`, `docker`).  
- Treating **`systemd-confext`** as **`systemd-sysext`** — **`/etc`**-**class** **config** **merge** vs **`/usr`** **system** **merge** (`systemd-confext`, `systemd-sysext`).  
- Treating **`docker`** as **`oci-image-spec`** — engine/tooling vs image format standard (`docker`, `oci-image-spec`).  
- Treating **`oci-image-spec`** as **`oci-distribution-spec`** — image **layout** vs registry **HTTP** **transport** (`oci-image-spec`, `oci-distribution-spec`).  
- Treating **`runc`** as **`oci-runtime-spec`** — **implementation** vs **specification** (`runc`, `oci-runtime-spec`).  
- Treating **`oci-runtime-spec`** as **`oci-image-spec`** — **runtime bundle** vs **image** **manifest/layers** (`oci-runtime-spec`, `oci-image-spec`).  
- Treating **`linux-overlayfs`** as **`oci-image-spec`** — **kernel** **union** **mount** **driver** **vs** **OCI** **image** **manifest/layer** **law** (`linux-overlayfs`, `oci-image-spec`, `linux-kernel`).  
- Treating **`linux-overlayfs`** as **`oci-runtime-spec`** — **overlay** **mount** **mechanism** **vs** **runtime** **bundle** **specification** (`linux-overlayfs`, `oci-runtime-spec`, `linux-kernel`).  
- Treating **`crun`** as **`oci-runtime-spec`** or as **`runc`** — **implementation** vs **spec** vs **other** **implementation** (`crun`, `oci-runtime-spec`, `runc`).  
- Treating **`ebpf`** as **`libbpf`** — **in-kernel** **BPF** **facility** **vs** **userspace** **C** **library** **/** **syscall** **uAPI** (`ebpf`, `libbpf`, `linux-kernel`).  
- Treating **`linux-netfilter`** as **`ebpf`** — **netfilter** **hook** **framework** **vs** **BPF** **subsystem** **facility** (`linux-netfilter`, `ebpf`, `linux-kernel`).  
- Treating **`linux-netfilter`** as **`cilium`** — **kernel** **framework** **vs** **CNI** **product** **/** **eBPF** **datapath** **implementation** (`linux-netfilter`, `cilium`, `linux-kernel`).  
- Treating **`linux-netfilter`** as **`envoy`** — **kernel** **L3/L4** **policy** **path** **vs** **userspace** **L7** **proxy** (`linux-netfilter`, `envoy`, `linux-kernel`).  
- Treating **`io-uring`** as **`liburing`** — **kernel** **io_uring** **uAPI** **vs** **userspace** **C** **library** (`io-uring`, `liburing`, `linux-kernel`).  
- Treating **`landlock`** as **`linux-security-modules`** — **one** **LSM** **(Landlock)** **vs** **LSM** **framework** **/** **other** **modules** (`landlock`, `linux-security-modules`, `linux-kernel`).  
- Treating **`seccomp`** as **`libseccomp`** — **kernel** **syscall** **filter** **facility** **vs** **userspace** **policy** **/** **BPF** **generator** **library** (`seccomp`, `libseccomp`, `linux-kernel`).  
- Treating **`linux-namespaces`** as **`docker`** **/** **`kubernetes`** — **kernel** **isolation** **primitive** **vs** **container** **engine** **/** **orchestrator** (`linux-namespaces`, `docker`, `kubernetes`, `linux-kernel`).  
- Treating **`linux-cgroups`** as **`docker`** **/** **`kubernetes`** — **kernel** **resource** **control** **vs** **container** **engine** **/** **orchestrator** (`linux-cgroups`, `docker`, `kubernetes`, `linux-kernel`).  
- Treating **`linux-capabilities`** as **`linux-security-modules`** — **privilege** **decomposition** **`CAP_*`** **vs** **LSM** **MAC** **policy** **framework** (`linux-capabilities`, `linux-security-modules`, `linux-kernel`).  
- Treating **`linux-capabilities`** as **`seccomp`** **or** **`libseccomp`** — **credential** **capability** **checks** **vs** **syscall** **filtering** **/** **policy** **generation** (`linux-capabilities`, `seccomp`, `libseccomp`, `linux-kernel`).  
- Treating **`linux-capabilities`** as **`docker`** **/** **`kubernetes`** — **kernel** **capability** **model** **vs** **container** **engine** **/** **orchestrator** (`linux-capabilities`, `docker`, `kubernetes`, `linux-kernel`).  
- Treating **`linux-overlayfs`** as **`docker`** **/** **`kubernetes`** — **kernel** **union** **filesystem** **vs** **container** **engine** **/** **orchestrator** (`linux-overlayfs`, `docker`, `kubernetes`, `linux-kernel`).  
- Treating **`linux-fuse`** as **`linux-overlayfs`** — **userspace** **delegated** **filesystem** **bridge** **vs** **in-kernel** **stacked** **union** **filesystem** (`linux-fuse`, `linux-overlayfs`, `linux-kernel`).  
- Treating **`linux-fuse`** as **`oci-image-spec`** — **kernel** **FUSE** **facility** **vs** **OCI** **image** **manifest/layer** **law** (`linux-fuse`, `oci-image-spec`, `linux-kernel`).  
- Treating **`linux-fuse`** as **`docker`** **/** **`kubernetes`** — **kernel** **FUSE** **mechanism** **vs** **container** **engine** **/** **orchestrator** (`linux-fuse`, `docker`, `kubernetes`, `linux-kernel`).  
- Treating **`linux-kvm`** as **`linux-namespaces`** **or** **`linux-cgroups`** — **hardware** **virtualization** **API** **vs** **OS-level** **container** **primitives** (`linux-kvm`, `linux-namespaces`, `linux-cgroups`, `linux-kernel`).  
- Treating **`linux-kvm`** as **`firecracker`** — **kernel** **KVM** **facility** **vs** **VMM** **product** (`linux-kvm`, `firecracker`, `linux-kernel`).  
- Treating **`linux-kvm`** as **`docker`** **/** **`kubernetes`** — **kernel** **hypervisor** **ABI** **vs** **default** **container** **engine** **/** **orchestrator** (`linux-kvm`, `docker`, `kubernetes`, `linux-kernel`).  
- Treating **`virtio`** as **`linux-kvm`** — **paravirtual** **device** **transport** **vs** **hypervisor** **control** **API** (`virtio`, `linux-kvm`, `linux-kernel`).  
- Treating **`virtio`** as **`firecracker`** — **virtio** **interface** **law** **vs** **VMM** **product** (`virtio`, `firecracker`, `linux-kernel`).  
- Treating **`linux-vhost`** as **`virtio`** — **host** **backend** **acceleration** **path** **vs** **guest-visible** **virtio** **device** **contract** (`linux-vhost`, `virtio`, `linux-kernel`).  
- Treating **`linux-vhost`** as **`linux-kvm`** — **virtio** **backend** **I/O** **path** **vs** **hypervisor** **control** **API** (`linux-vhost`, `linux-kvm`, `linux-kernel`).  
- Treating **`linux-vfio`** as **`virtio`** — **IOMMU** **/** **device** **assignment** **path** **vs** **paravirtual** **virtio** **device** **model** (`linux-vfio`, `virtio`, `linux-kernel`).  
- Treating **`linux-vfio`** as **`linux-kvm`** — **VFIO** **/** **IOMMU** **assignment** **API** **vs** **`/dev/kvm`** **hypervisor** **control** **API** (`linux-vfio`, `linux-kvm`, `linux-kernel`).  
- Treating **`linux-vfio`** as **`linux-vhost`** — **passthrough** **/** **DMA** **isolation** **for** **assigned** **devices** **vs** **virtio** **queue** **acceleration** **on** **the** **host** (`linux-vfio`, `linux-vhost`, `linux-kernel`).  
- Treating **`qemu`** as **`linux-kvm`** — **userspace** **VMM** **/** **emulator** **vs** **kernel** **`/dev/kvm`** **hypervisor** **API** (`qemu`, `linux-kvm`, `linux-kernel`).  
- Treating **`qemu`** as **`firecracker`** — **general-purpose** **QEMU** **vs** **microVM-focused** **Firecracker** **VMM** (`qemu`, `firecracker`, `linux-kernel`).  
- Treating **`libvirt`** as **`qemu`** — **management** **API** **/** **daemon** **vs** **VMM** **binary** (`libvirt`, `qemu`, `linux-kernel`).  
- Treating **`libvirt`** as **`linux-kvm`** — **orchestration** **/** **policy** **layer** **vs** **kernel** **`/dev/kvm`** **hypervisor** **API** (`libvirt`, `linux-kvm`, `linux-kernel`).  
- Treating **`libvirt`** as **`kubernetes`** — **node-local** **VM** **management** **stack** **vs** **cluster** **orchestrator** **API** (`libvirt`, `kubernetes`, `linux-kernel`).  
- Treating **`kubevirt`** as **`kubernetes`** — **VM** **extension** **/** **CRDs** **vs** **core** **Kubernetes** **pod** **/** **OCI** **sandbox** **model** (`kubevirt`, `kubernetes`, `linux-kernel`).  
- Treating **`kubevirt`** as **`libvirt`** — **cluster** **VM** **orchestration** **layer** **vs** **node** **virtualization** **management** **daemon** (`kubevirt`, `libvirt`, `linux-kernel`).  
- Treating **`kubevirt`** as **`qemu`** — **Kubernetes** **integration** **/** **controllers** **vs** **VMM** **binary** (`kubevirt`, `qemu`, `linux-kernel`).  
- Treating **`kata-containers`** as **`runc`** — **VM-isolated** **OCI** **runtime** **vs** **namespace-isolated** **OCI** **runtime** (`kata-containers`, `runc`, `linux-kernel`).  
- Treating **`kata-containers`** as **`kubevirt`** — **CRI/OCI** **container** **sandbox** **with** **VM** **technology** **vs** **Kubernetes** **VM** **workload** **CRDs** (`kata-containers`, `kubevirt`, `kubernetes`).  
- Treating **`kata-containers`** as **`qemu`** — **OCI** **runtime** **integration** **layer** **vs** **VMM** **binary** (`kata-containers`, `qemu`, `linux-kernel`).  
- Treating **`gvisor`** as **`runc`** — **userspace** **application** **kernel** **/** **syscall** **interposition** **vs** **namespace** **OCI** **runtime** (`gvisor`, `runc`, `linux-kernel`).  
- Treating **`gvisor`** as **`kata-containers`** — **userspace** **sandbox** **model** **vs** **VM-isolated** **OCI** **runtime** (`gvisor`, `kata-containers`, `linux-kernel`).  
- Treating **`gvisor`** as **`linux-kernel`** — **userspace** **OCI** **runtime** **boundary** **vs** **host** **kernel** **facility** (`gvisor`, `linux-kernel`).  
- Treating **`buildkit`** as **`oci-runtime-spec`** — **image** **build** **engine** **/** **DAG** **cache** **vs** **runtime** **bundle** **lifecycle** **law** (`buildkit`, `oci-runtime-spec`, `linux-kernel`).  
- Treating **`buildkit`** as **`runc`** — **build-time** **artifact** **production** **vs** **low-level** **OCI** **runtime** **execution** (`buildkit`, `runc`, `containerd`).  
- Treating **`buildkit`** as **`oci-image-spec`** — **implementation** **and** **tooling** **vs** **JSON/manifest** **format** **standard** (`buildkit`, `oci-image-spec`).  
- Treating **`helm`** as **`kubernetes`** — **chart** **packaging** **client** **/** **release** **tooling** **vs** **cluster** **orchestrator** **/** **control** **plane** (`helm`, `kubernetes`).  
- Treating **`helm`** as **`oci-runtime-spec`** — **Kubernetes** **manifest** **templating** **/** **release** **lifecycle** **vs** **OCI** **runtime** **bundle** **law** (`helm`, `oci-runtime-spec`, `kubernetes`).  
- Treating **`helm`** as **`oci-image-spec`** — **chart** **format** **and** **workload** **references** **vs** **OCI** **image** **manifest** **/** **layer** **law** (`helm`, `oci-image-spec`).  
- Treating **`fluxcd`** as **`kubernetes`** — **GitOps** **controllers** **reconciling** **desired** **state** **vs** **orchestrator** **/** **API** **server** **itself** (`fluxcd`, `kubernetes`).  
- Treating **`fluxcd`** as **`helm`** — **continuous** **reconciliation** **/** **CRD** **operators** **vs** **Helm** **CLI** **chart** **client** **alone** (`fluxcd`, `helm`, `kubernetes`).  
- Treating **`fluxcd`** as **`oci-runtime-spec`** — **cluster** **reconciliation** **path** **vs** **OCI** **runtime** **bundle** **law** (`fluxcd`, `oci-runtime-spec`, `kubernetes`).  
- Treating **`argo-cd`** as **`kubernetes`** — **GitOps** **delivery** **controller** **vs** **orchestrator** **/** **API** **server** **itself** (`argo-cd`, `kubernetes`).  
- Treating **`argo-cd`** as **`fluxcd`** — **distinct** **GitOps** **controller** **products** **/** **CRD** **models** **(substitutable** **class)** (`argo-cd`, `fluxcd`, `kubernetes`).  
- Treating **`argo-cd`** as **`helm`** — **delivery** **controller** **vs** **chart** **packaging** **tool** (`argo-cd`, `helm`, `kubernetes`).  
- Treating **`kustomize`** as **`kubernetes`** — **manifest** **build** **tool** **vs** **orchestrator** **/** **API** **server** (`kustomize`, `kubernetes`).  
- Treating **`kustomize`** as **`helm`** — **overlay** **/** **patch** **composition** **vs** **chart** **templating** **/** **release** **packaging** (`kustomize`, `helm`, `kubernetes`).  
- Treating **`glibc`** as **`linux-kernel`** — **userland** **libc** vs **kernel** (`glibc`, `linux-kernel`).  
- Treating **`glibc`** as **`gnu-gcc`** or as **`elf`** — **runtime**/**ABI** vs **compiler** vs **object** **format** (`glibc`, `gnu-gcc`, `elf`).  
- Treating **`musl`** as **`glibc`** — **not** **ABI**-**interchangeable** **Linux** **libcs** (`musl`, `glibc`).  
- Treating **`gnu-libstdcxx`** as **`gnu-gcc`** or as **`glibc`** — **C++** **stdlib** vs **compiler** vs **C** **libc** (`gnu-libstdcxx`, `gnu-gcc`, `glibc`).  
- Treating **`llvm-libcxx`** as **`clang`** or as **`llvm-lld`** — **C++** **stdlib** vs **compiler** **front** **end** vs **linker** (`llvm-libcxx`, `clang`, `llvm-lld`).  
- Treating **`llvm-libcxxabi`** as **`llvm-libcxx`** or as **`gnu-libstdcxx`** — **C++** **ABI** **runtime** vs **stdlib** vs **GCC** **stdlib** **package** (`llvm-libcxxabi`, `llvm-libcxx`, `gnu-libstdcxx`).  
- Treating **`msvc-vcruntime`** as **`glibc`** or as **`musl`** — **Windows** **UCRT**/**`VCRUNTIME`** **DLL** **surface** **vs** **Unix** **hosted** **libcs** (`msvc-vcruntime`, `glibc`, `musl`).  
- Treating **`msvcprt`** as **`gnu-libstdcxx`** or as **`llvm-libcxx`** **without** **platform** **/** **ABI** **distinction** — **MSVC** **`msvcp*.dll`** **vs** **ELF**-**oriented** **Unix** **C++** **runtimes** (`msvcprt`, `gnu-libstdcxx`, `llvm-libcxx`).  
- Treating **`freebsd-libc`** **or** **`openbsd-libc`** **or** **`illumos-libc`** as **`glibc`** **or** **`musl`** — **non**-**Linux** **Unix** **base** **libcs** **vs** **Linux** **hosted** **libcs** (`freebsd-libc`, `openbsd-libc`, `illumos-libc`, `glibc`, `musl`).  
- Treating **`freebsd-libc`** as **`openbsd-libc`** — **separate** **BSD** **projects** **and** **ABI** **policies** (`freebsd-libc`, `openbsd-libc`).  
- Treating **`netbsd-libc`** as **`dragonfly-libc`** **or** **other** **BSD** **base** **libcs** — **separate** **release** **engineering** **and** **ABI** **policies** (`netbsd-libc`, `dragonfly-libc`, `freebsd-libc`, `openbsd-libc`).  
- Treating **`illumos-libc`** as **`glibc`** **or** **as** **a** **BSD** **base** **libc** — **Solaris/illumos** **lineage** **vs** **GNU/Linux** **or** **BSD** **userland** **ABIs** (`illumos-libc`, `glibc`, `freebsd-libc`).  
- Treating **`android-bionic`** as **`glibc`** **or** **`musl`** — **Android** **NDK**/**platform** **ABI** **vs** **desktop** **Linux** **libcs** (`android-bionic`, `glibc`, `musl`).  
- Treating **`newlib`** as **`glibc`**, **`musl`**, **or** **hosted** **BSD**/**illumos**/**Bionic** **libcs** — **embedded**/**bare-metal** **GCC** **libc** **vs** **full** **hosted** **OS** **userland** **ABIs** (`newlib`, `glibc`, `musl`, `freebsd-libc`, `illumos-libc`, `android-bionic`).  
- Treating **`wasi`** **(spec)** as **`wasi-libc`** **(C** **library** **sysroot)** — **WASI** **import** **APIs** **vs** **the** **libc** **implementation** **linked** **into** **`wasm32-wasi`** **modules** (`wasi`, `wasi-libc`, `webassembly`).  
- Treating **`alpine-linux`** as **`musl`** or as **`linux-kernel`** — **distribution** **packaging** **/** **policy** vs **libc** **implementation** vs **kernel** (`alpine-linux`, `musl`, `linux-kernel`).  
- Treating **`alpine-linux`** as **`docker`** — **distro** **userland** vs **container** **engine** (`alpine-linux`, `docker`).  
- Treating **`debian`** as **`glibc`**, **`systemd`**, **or** **`docker`** — **distribution** **packaging** **vs** **libc** **/** **init** **suite** **/** **engine** (`debian`, `glibc`, `systemd`, `docker`).  
- Treating **`debian`** as **`alpine-linux`** — **glibc**/**systemd** **vs** **musl**/**OpenRC** **defaults** (`debian`, `alpine-linux`).  
- Treating **`ubuntu`** as **`debian`** — **same** **heritage** **≠** **same** **governance** **/** **cadence** **/** **defaults** (`ubuntu`, `debian`).  
- Treating **`ubuntu`** as **`glibc`**, **`systemd`**, **or** **`docker`** — **distribution** **packaging** **vs** **libc** **/** **init** **suite** **/** **engine** (`ubuntu`, `glibc`, `systemd`, `docker`).  
- Treating **`ubuntu`** as **`alpine-linux`** — **glibc**/**systemd** **vs** **musl**/**OpenRC** **defaults** (`ubuntu`, `alpine-linux`).  
- Treating **`fedora`** as **`glibc`**, **`systemd`**, **or** **`docker`** — **distribution** **packaging** **vs** **libc** **/** **init** **suite** **/** **engine** (`fedora`, `glibc`, `systemd`, `docker`).  
- Treating **`fedora`** as **`debian`** **or** **`ubuntu`** — **rpm**/**dnf** **vs** **`dpkg`**/**`apt`** **law** (`fedora`, `debian`, `ubuntu`).  
- Treating **`fedora`** as **`alpine-linux`** — **glibc**/**systemd** **vs** **musl**/**OpenRC** **defaults** (`fedora`, `alpine-linux`).  
- Treating **`rhel`** as **`red-hat-openshift`** — **node** **OS** **distro** **vs** **Kubernetes** **platform** (`rhel`, `red-hat-openshift`).  
- Treating **`rhel`** as **`fedora`** — **enterprise** **subscription** **/** **cadence** **≠** **community** **Fedora** **release** **model** (`rhel`, `fedora`).  
- Treating **`centos-stream`** as **`rhel`** — **rolling** **upstream** **/** **community** **cadence** **≠** **enterprise** **subscription** **GA** (`centos-stream`, `rhel`).  
- Treating **`centos-stream`** as **`fedora`** — **RHEL** **pipeline** **node** **≠** **Fedora** **release** **model** (`centos-stream`, `fedora`).  
- Treating **`centos-stream`** as **`rocky-linux`** **or** **`almalinux`** — **upstream** **development** **branch** **≠** **downstream** **rebuild** (`centos-stream`, `rocky-linux`, `almalinux`).  
- Treating **`centos-linux`** as **`centos-stream`** — **EOL** **fixed**-**minor** **rebuild** **line** **≠** **rolling** **upstream** **branch** (`centos-linux`, `centos-stream`).  
- Treating **`centos-linux`** as **`rocky-linux`** **or** **`almalinux`** **without** **EOL** **/** **maintenance** **distinction** — **historical** **rebuild** **vs** **active** **successor** **projects** (`centos-linux`, `rocky-linux`, `almalinux`).  
- Treating **`rhel`** as **`glibc`**, **`systemd`**, **or** **`docker`** — **distribution** **packaging** **vs** **libc** **/** **init** **suite** **/** **engine** (`rhel`, `glibc`, `systemd`, `docker`).  
- Treating **`rhel`** as **`alpine-linux`** — **glibc**/**systemd** **vs** **musl**/**OpenRC** **defaults** (`rhel`, `alpine-linux`).  
- Treating **`rocky-linux`** **or** **`almalinux`** **as** **`rhel`** — **rebuild** **/** **compatible** **lineage** **≠** **Red** **Hat** **subscription** **product** (`rocky-linux`, `almalinux`, `rhel`).  
- Treating **`rocky-linux`** **as** **`almalinux`** **(or** **vice** **versa)** **without** **governance** **/** **cadence** **distinction** — **substitutable** **but** **separate** **projects** (`rocky-linux`, `almalinux`).  
- Treating **`rocky-linux`** **or** **`almalinux`** **as** **`red-hat-openshift`** — **distro** **node** **OS** **vs** **Kubernetes** **platform** (`rocky-linux`, `almalinux`, `red-hat-openshift`).  
- Treating **`rocky-linux`** **or** **`almalinux`** **as** **`glibc`**, **`systemd`**, **or** **`docker`** — **distribution** **packaging** **vs** **libc** **/** **init** **/** **engine** (`rocky-linux`, `almalinux`, `glibc`, `systemd`, `docker`).  
- Treating **`rocky-linux`** **or** **`almalinux`** **as** **`alpine-linux`** — **glibc**/**systemd** **vs** **musl**/**OpenRC** **defaults** (`rocky-linux`, `almalinux`, `alpine-linux`).
