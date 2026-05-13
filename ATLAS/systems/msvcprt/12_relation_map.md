---
atlas_package: system
system_slug: msvcprt
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `windows-nt`:** **user**-**mode** **DLLs** **on** **Windows** (`DOCUMENTED`).  
- **`integrates_with` `msvc-vcruntime`:** **C++** **stdlib** **DLLs** **depend** **on** **CRT** **/`VCRUNTIME`** **support** (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** **C++** **interop** **via** **`extern` "C"** **still** **anchors** **to** **C** **ABI** **themes** (`DOCUMENTED`).  
- **`competes_with` `gnu-libstdcxx` / `llvm-libcxx`:** **substitutable** **C++** **stdlib** **implementations** **across** **platforms** **(not** **ABI**-**interchangeable** **in** **process)** (`INFERRED`).
