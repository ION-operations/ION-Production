# Comparative: Namespace Models

**Atlas scope:** How names resolve to objects; mount namespaces; distributed naming.

## Framework (populate as packages mature)

| Namespace class | Example systems | Ledger pointers |
|-----------------|-----------------|-----------------|
| **Filesystem path** | linux-kernel, windows-nt | VFS vs NT object namespace |
| **Network** | linux-kernel (network ns), kubernetes (Services/DNS) | CNI + kube-dns/CoreDNS |
| **Process / PID** | linux-kernel, container runtimes | PID namespaces |
| **Object / handle** | windows-nt | Object Manager paths |
| **Cluster logical** | kubernetes | Namespaces API resource |

## Status

**INFERRED scaffold:** Dimensions above are atlas-internal structuring; per-system DOCUMENTED claims must live in respective `04_process_memory_namespace.md` and `05_storage_network_ipc.md` files.

## Next packages to unlock rows

`docker`, `nixos`, `android-aosp` — each introduces distinct naming layers (store paths, package namespaces).
