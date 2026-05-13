---
atlas_package: system
system_slug: linux-capabilities
schema_version: "1.0"
last_reviewed: "2026-04-22"
evidence_grade: B
---

# Scope

## In scope

- **Capability** **sets** **(permitted,** **effective,** **inheritable,** **bounding)** **and** **ambient** **capabilities** **as** **documented** **in** **capabilities(7)** (`DOCUMENTED`).  
- **Interaction** **with** **user** **namespaces** **and** **container** **defaults** **as** **integration** **patterns** (`INFERRED`).  
- **File** **capabilities** **and** **`setcap`**/**`getcap`** **operator** **surface** **at** **survey** **level** (`OBSERVED`/`INFERRED`).

## Out of scope

- **Full** **matrix** **of** **every** **`CAP_*`** **by** **kernel** **minor** **—** **use** **upstream** **docs** **for** **normative** **enumerations.**  
- **Non-Linux** **POSIX** **capabilities** **where** **they** **differ** **—** **out** **unless** **explicitly** **scoped** **later**.

## Versioning note

**Capability** **splitting** **and** **defaults** **evolve** **with** **kernel** **and** **distribution** **policy** (`OBSERVED`).
