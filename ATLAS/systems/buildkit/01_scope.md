---
atlas_package: system
system_slug: buildkit
schema_version: "1.0"
last_reviewed: "2026-04-09"
evidence_grade: B
---

# Scope

## In scope

- **`buildkitd`** **daemon** **/** **worker** **model,** **LLB** **DAG,** **and** **export** **modes** **toward** **OCI** **images** (`DOCUMENTED`).  
- **Docker** **Engine** **integration** **as** **default** **`docker`** **build** **backend** **where** **documented** (`DOCUMENTED`).  
- **Registry** **push** **and** **cache** **semantics** **at** **survey** **grain** (`INFERRED` **where** **marked**).

## Out of scope

- **Vendor-specific** **CI** **pricing** **and** **quota** **policies.**  
- **Per-language** **base** **image** **curation** **unless** **ledgered.**

## Versioning note

**BuildKit** **tracks** **Moby/Docker** **release** **cadence** **and** **Go** **runtime** **requirements** **in** **upstream** **documentation** (`DOCUMENTED`).
