---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Process, memory, and namespace model

- **Processes / tasks:** Represented by `task_struct`; creation via `fork`/`clone` (`DOCUMENTED`).  
- **Memory:** Virtual address space per process (`mm_struct`, VMAs); demand paging; COW on fork (`DOCUMENTED`).  
- **Namespaces:** Mount, UTS, IPC, PID, network, user, cgroup, time namespaces enable container isolation (`DOCUMENTED`).  
- **Capabilities / credentials:** POSIX-like UIDs with Linux extensions (`DOCUMENTED`).
