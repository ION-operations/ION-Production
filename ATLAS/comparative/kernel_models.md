# Comparative: Kernel Models

**Atlas scope:** Privileged execution substrate, resource mediation, protection domains.  
**Evidence:** Per-cell tiers refer to packages: `multics`, `windows-nt`, `linux-kernel`, `xnu-macos`, `freebsd` (seeded).

## Dimension matrix

| Dimension | multics | windows-nt | linux-kernel | xnu-macos | freebsd |
|-----------|---------|------------|--------------|-----------|---------|
| **Primary abstraction** | Single-level store + generalized segments; rich supervisor (`HISTORICAL` / primary literature) | Executive / kernel / HAL layering; user/kernel mode (`DOCUMENTED` MS kernel docs + observable ABI) | Monolithic kernel with loadable modules; POSIX-ish API (`DOCUMENTED` kernel source + man-pages LDP) | Mach + BSD hybrid; I/O Kit drivers (`DOCUMENTED` Apple OSS/docs) | Monolithic BSD kernel + cohesive base system (`DOCUMENTED` handbook) |
| **Process / address model** | Segment + ring protection; shared memory emphasis (`HISTORICAL`) | EPROCESS / KTHREAD; virtual address spaces per process (`DOCUMENTED` internals books / WDK where cited in package) | `mm_struct`; VMAs; copy-on-write fork (`DOCUMENTED` kernel) | Mach tasks/threads + BSD process mapping (`DOCUMENTED`) | Traditional Unix processes; UVM VM (`DOCUMENTED` handbook) |
| **Scheduling claim** | Multiplexed CPU via supervisor (`HISTORICAL`) | Priority classes; scheduler revisions across releases (`DOCUMENTED` release-relative) | CFS default; pluggable classes (`DOCUMENTED`) | Documented scheduler classes at Apple doc granularity (`DOCUMENTED` / `UNKNOWN` micro-detail) | SMP scheduling (`DOCUMENTED` handbook overview) |
| **IPC primitive class** | Shared memory + supervisor-mediated IPC (`HISTORICAL`) | LPC/ALPC, objects, handles (`DOCUMENTED` externally) | pipes, sockets, futex, signals, mmap (`DOCUMENTED`) | Mach ports + BSD sockets/pipes (`DOCUMENTED`) | Sockets, pipes; Unix IPC (`DOCUMENTED`) |
| **File / naming integration** | Unified memory-file via segments (`HISTORICAL`) | NT namespace + object manager (`DOCUMENTED`) | VFS unified over many FS types (`DOCUMENTED`) | BSD VFS + APFS stack (`DOCUMENTED` FS docs) | UFS/ZFS and others; unified namespace (`DOCUMENTED`) |
| **Extensibility** | Dynamic linking; reconfiguration in research deployments (`HISTORICAL`) | Filter drivers, FS mini-filters, callbacks (`DOCUMENTED` driver model) | Loadable modules; eBPF attach points (`DOCUMENTED` / evolving) | kext legacy → System Extensions/DriverKit (`DOCUMENTED` version-dependent) | `kld` modules; kernel options (`DOCUMENTED`) |

## Atlas patterns (structural)

- **K1 — Ring / mode separation:** Hardware privilege levels + syscall gate (variants across systems).  
- **K2 — Object handles:** NT-style handle tables vs FD tables — compare `windows-nt` vs `linux-kernel` packages.  
- **K3 — Single-level store vs separate FS namespace:** Multics pattern vs mainstream “file descriptor” OS (`multics` vs `linux-kernel`).  
- **K4 — Module extensibility:** In-tree vs out-of-tree policy differs by governance, not diagram shape.

## Unknown / do-not-merge-without-sources

- Micro-architectural details of unreleased NT branches.  
- Vendor-specific secure enclave layout unless DOCUMENTED in package ledger.
