---
atlas_package: system
system_slug: linux-capabilities
schema_version: "1.0"
last_reviewed: "2026-04-22"
evidence_grade: B
---

# Architecture (conceptual)

**Per-thread** **credential** **bags** **carry** **capability** **bitsets;** **the** **kernel** **checks** **them** **when** **privileged** **operations** **are** **attempted** **(per** **documented** **model** **in** **capabilities(7)** **and** **kernel** **security** **docs)** (`DOCUMENTED`).
