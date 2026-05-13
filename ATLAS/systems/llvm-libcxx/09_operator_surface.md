---
atlas_package: system
system_slug: llvm-libcxx
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Operator surface

**Packagers** **and** **toolchain** **maintainers** **expose** **libc++** **via** **packages** **and** **SDK** **layouts**; **application** **operators** **see** **it** **as** **link** **flags** **and** **runtime** **`.so`** **dependencies** (`INFERRED`).
