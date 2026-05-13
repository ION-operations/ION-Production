---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| Syscall layer | User/kernel boundary | DOCUMENTED |
| Process management | fork/exec, tasks, `task_struct` | DOCUMENTED |
| Memory management | VMAs, page tables, reclaim | DOCUMENTED |
| VFS | Path resolution, inodes, dentries | DOCUMENTED |
| Block layer | I/O scheduling, stacking | DOCUMENTED |
| Net stack | sockets, protocols, drivers | DOCUMENTED |
| LSM / BPF | Security & extensibility hooks | DOCUMENTED (feature-dependent) |
