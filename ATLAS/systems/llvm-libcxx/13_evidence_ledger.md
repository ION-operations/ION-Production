---
atlas_package: system
system_slug: llvm-libcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| lcxx-001 | LLVM libc++ is the C++ standard library implementation documented on libcxx.llvm.org | DOCUMENTED | `src-llvm-libcxx-docs` | |
| lcxx-002 | libc++ depends on a C library (glibc or musl) for hosted POSIX/C services | DOCUMENTED | `src-llvm-libcxx-docs`; `glibc` / `musl` | |
| lcxx-003 | Clang -stdlib=libc++ links libc++ in LLVM-oriented C++ builds | DOCUMENTED | Clang driver docs; `clang` | |
| lcxx-004 | Typical libc++ deployments link libc++abi for Itanium C++ ABI facilities | DOCUMENTED | `src-llvm-libcxx-docs`; `llvm-libcxxabi` | |
