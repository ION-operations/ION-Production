---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Documented vs inferred

## Firmly DOCUMENTED (in cited AIM-OS files)

- **Governance quartet** and **authority class** system (A0–A7).  
- **Major subsystem roles** (CMC, HHNI, VIF, SEG, APOE, SDF-CVF) and **module paths** as stated in `AIMOS_MAJOR_SYSTEMS.md`.  
- **CAPSULE** as sole continuity carrier in **AETHER_INTERFACE**.  
- **MCP** exposure and **JSON-RPC** framing.  
- **Project ION** as **A3** lineage in **AETHER_ATLAS**.

## INFERRED (needs stronger citation for upgrade)

- **Production** deployment SLOs on a **specific** host class.

## UNKNOWN (do not state without evidence)

- Internal **cloud** control plane for any hosted SKU (if one exists) — not covered in cited quartet.  
- **Formal verification** of full stack safety properties.

## Open questions

1. Map **AIM-OS ontology** (A0–A7, ontology classes) to **Systems ATLAS** evidence tiers in a comparative note (optional).  
2. Add **ION** as separate Systems ATLAS package when ION architecture stabilizes enough for a scoped `00_identity` — or keep **one-way** lineage here only.

## Resolved (2026-04-03)

- **MCP tool count:** **103** tools in `lucid_mcp_server.py` `handle_tools_list` (**OBSERVED**, ledger `aim-028`). `ARCHITECTURE_OVERVIEW.md` **93** figure is **superseded** by source for current surface; refresh that doc separately if desired.
