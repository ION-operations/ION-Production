---
atlas_package: system
system_slug: linux-netfilter
schema_version: "1.0"
last_reviewed: "2026-04-24"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **netfilter** **is** **a** **kernel** **subsystem** (`DOCUMENTED`).  
- **`integrates_with` `linux-namespaces`:** **per-netns** **tables** (`INFERRED`).  
- **`integrates_with` `kubernetes` + `cilium` + container** **stack** **(INFERRED):** **node** **networking** **—** **iptables/nft** **modes** **vs** **eBPF** **CNI** **datapaths** **are** **different** **mechanisms.**
