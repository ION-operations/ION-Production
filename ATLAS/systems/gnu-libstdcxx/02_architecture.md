---
atlas_package: system
system_slug: gnu-libstdcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **C++** **standard** **facilities** **implemented** **using** **C** **library** **and** **compiler** **support** **routines** (`DOCUMENTED`).

## Link shape

- **`libstdc++.so`** (or **static** **archive**) **linked** **after** **object** **files** on **typical** **g++** **links** (`DOCUMENTED`).
