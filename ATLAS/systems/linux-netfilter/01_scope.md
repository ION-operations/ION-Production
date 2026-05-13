---
atlas_package: system
system_slug: linux-netfilter
schema_version: "1.0"
last_reviewed: "2026-04-24"
evidence_grade: B
---

# Scope

## In scope

- **Netfilter** **hook** **points** **and** **documented** **kernel** **architecture** **overview** (`DOCUMENTED`).  
- **Common** **userspace** **rule** **frontends** **(nftables** **vs** **iptables** **legacy)** **as** **naming** **and** **migration** **context** (`OBSERVED`/`INFERRED`).  
- **Interaction** **with** **network** **namespaces** **and** **Kubernetes/Docker** **networking** **patterns** (`INFERRED`).

## Out of scope

- **Vendor-specific** **cloud** **VPC** **implementations** **—** **out** **unless** **added** **as** **separate** **packages.**  
- **Full** **rule** **syntax** **reference** **for** **every** **nft** **statement** **—** **use** **upstream** **nftables** **documentation** **for** **normative** **details.**

## Versioning note

**Rule** **backends** **and** **defaults** **(iptables** **vs** **nft** **backends)** **vary** **by** **distribution** **and** **release** (`OBSERVED`).
