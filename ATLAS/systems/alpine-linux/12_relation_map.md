---
atlas_package: system
system_slug: alpine-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **ships** **kernel** **packages** **for** **supported** **architectures** (`DOCUMENTED`).  
- **`integrates_with` `musl`:** **default** **libc** **on** **mainline** **Alpine** (`DOCUMENTED`).  
- **`integrates_with` `docker` / `oci-image-spec`:** **pervasive** **Alpine** **base** **layers** (`OBSERVED` **+** **`INFERRED`**).  
- **`integrates_with` `gnu-gcc` / `gnu-binutils`:** **native** **and** **cross** **build** **toolchains** **in** **repos** (`DOCUMENTED`).
