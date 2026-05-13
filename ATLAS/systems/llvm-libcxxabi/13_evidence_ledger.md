---
atlas_package: system
system_slug: llvm-libcxxabi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| lcxa-001 | LLVM libc++abi implements Itanium C++ ABI support routines used with libc++ | DOCUMENTED | `src-llvm-libcxxabi-docs` | |
| lcxa-002 | Typical libc++ on LLVM links libc++abi for exceptions and RTTI machinery | DOCUMENTED | `src-llvm-libcxxabi-docs`; `llvm-libcxx` | |
| lcxa-003 | libc++abi builds on platform C library services on hosted Unix targets | DOCUMENTED | `src-llvm-libcxxabi-docs`; `glibc` / `musl` | |
