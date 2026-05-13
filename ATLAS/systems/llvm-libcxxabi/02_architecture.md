---
atlas_package: system
system_slug: llvm-libcxxabi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Sits** **below** **`llvm-libcxx`** **and** **above** **the** **C** **library** **/** **dynamic** **loader** **for** **language** **ABI** **machinery** (`DOCUMENTED`).

## Link shape

- **`libc++abi.so`** **(or** **static)** **pulled** **into** **the** **same** **link** **line** **as** **`libc++`** **on** **many** **deployments** (`DOCUMENTED`).
