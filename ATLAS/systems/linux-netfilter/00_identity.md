---
atlas_package: system
system_slug: linux-netfilter
schema_version: "1.0"
last_reviewed: "2026-04-24"
evidence_grade: B
---

# Linux netfilter — Identity

**Kind:** **Linux** **kernel** **framework** **for** **packet** **filtering,** **NAT,** **and** **connection** **tracking** **via** **registered** **hooks** **in** **the** **network** **stack** (`DOCUMENTED`, `src-linux-netfilter-kernel-docs`). **Userspace** **frontends** **include** **nftables** **(nft)** **and** **the** **legacy** **iptables** **CLI** **family** **(survey,** **INFERRED).**

## Boundaries

- **Not** **`ebpf`** **—** **eBPF** **attaches** **via** **BPF** **syscalls** **and** **distinct** **subsystems** **(tc/XDP,** **kprobes,** **…);** **netfilter** **is** **the** **older** **hook** **framework** **for** **L3/L4** **packet** **path** **policy** (`DOCUMENTED` **boundary** **at** **high** **level).**  
- **Not** **`cilium`** **or** **`envoy`** **—** **those** **are** **products** **with** **their** **own** **datapaths** **and** **control** **planes.**  
- **Not** **`linux-namespaces`** **—** **network** **namespaces** **scope** **interfaces** **and** **routing;** **netfilter** **rules** **execute** **inside** **a** **given** **namespace’s** **stack.**

## Why this system matters

- **Explains** **kube-proxy** **iptables/nftables** **modes,** **host** **firewalling,** **and** **NAT** **without** **conflating** **the** **kernel** **hook** **framework** **with** **eBPF** **service** **mesh** **datapaths.**

## What this system teaches the atlas

**Separate** **netfilter** **hook** **semantics** **from** **eBPF** **bytecode** **facilities** **and** **from** **L7** **proxies.**
