---
atlas_package: system
system_slug: llvm-libcxxabi
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Operator surface

**Packagers** **expose** **libc++abi** **as** **a** **separate** **runtime** **package** **or** **bundled** **with** **LLVM** **SDKs**; **operators** **see** **it** **via** **missing** **`libc++abi`** **link** **errors** (`INFERRED`).
