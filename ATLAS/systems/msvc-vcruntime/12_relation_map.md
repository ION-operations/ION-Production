---
atlas_package: system
system_slug: msvc-vcruntime
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `windows-nt`:** **user**-**mode** **DLLs** **on** **the** **NT** **+** **Win32** **stack** (`DOCUMENTED`).  
- **`integrates_with` `c-language`:** **hosted** **C** **entry** **points** **for** **MSVC** **ABI** (`DOCUMENTED`).  
- **`integrates_with` `clang`:** **Clang** **can** **target** **MSVC** **CRT** **layouts** **on** **Windows** (`INFERRED`).  
- **`integrates_with` `msvcprt`:** **C++** **stdlib** **DLLs** **layer** **above** **the** **CRT** (`DOCUMENTED`).
