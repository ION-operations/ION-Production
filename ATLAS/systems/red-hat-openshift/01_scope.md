---
atlas_package: system
system_slug: red-hat-openshift
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Scope

## In scope

- **Getting started — Kubernetes overview** claims: OCP + Kubernetes relationship, API parity statement, `oc` vs `kubectl`, enterprise platform additions (`DOCUMENTED`, `src-redhat-ocp-kubernetes-overview`).  
- **Conformance artifacts** for **`openshift`** product family under CNCF **`k8s-conformance`** (`DOCUMENTED`, `src-cncf-k8s-conformance`).

## Out of scope

- Full **installation topology** per cloud/bare metal — follow Red Hat **installing** guides (`DOCUMENTED` pattern).  
- **OperatorHub** / every bundled operator — record per operator when needed.

## Versioning note

- OCP **4.x** stream is time-bounded; re-pin doc URLs when upgrading the package baseline (`DOCUMENTED` discipline).
