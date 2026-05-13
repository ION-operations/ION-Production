# Comparative: Orchestration Models

**Atlas scope:** Desired-state reconciliation, scheduling, failure domains, control/data plane split.  
**Primary package:** `kubernetes` (seeded). `docker` and `systemd` packages seeded for single-host contrast.

## Core structural comparison

| Dimension | kubernetes | docker (seeded) | systemd (seeded, single-host) |
|-----------|------------|------------------|-------------------------------|
| **Unit of work** | Pod / workload API resources (`DOCUMENTED` API) | Container (OCI) (`DOCUMENTED` OCI + engine docs); CRI runtime often `containerd` (`DOCUMENTED` CRI docs) | Unit (service, socket, timer, …) (`DOCUMENTED` systemd docs) |
| **Desired state store** | etcd (typical) + apiserver persistence (`DOCUMENTED` arch docs) | Local engine state (`DOCUMENTED` / `OBSERVED`) | Unit files + generators (`DOCUMENTED`) |
| **Reconciliation** | controllers; level-triggered (`DOCUMENTED` controller pattern) | reconcile container lifecycle (`DOCUMENTED`) | dependency graph + activation (`DOCUMENTED`) |
| **Scheduling** | kube-scheduler; predicates/ priorities (`DOCUMENTED`) | local placement only | N/A (activation order) |
| **Network model** | CNI plugin interface (`DOCUMENTED` CNI spec) | bridge/overlay per config (`DOCUMENTED`) | socket units; no cluster overlay | 
| **Security boundary** | ServiceAccount; RBAC; admission (`DOCUMENTED`) | Linux namespaces/cgroups (`DOCUMENTED` kernel + engine) | privilege boundaries of daemons (`DOCUMENTED` + deployment-specific) |

## CRI runtimes on Linux nodes (kubelet seam)

| Dimension | `containerd` (CRI plugin) | `cri-o` |
|-----------|---------------------------|---------|
| **Kubelet interface** | CRI gRPC (`DOCUMENTED`, `kubernetes` + CRI docs) | CRI gRPC (`DOCUMENTED`, `cri-o` package) |
| **Daemon model** | `containerd` daemon + CRI plugin (`DOCUMENTED`) | CRI-O daemon (`DOCUMENTED`) |
| **Typical low-level executor** | `runc`-class OCI runtime (`DOCUMENTED`) | `runc`-class OCI runtime (`DOCUMENTED`) |
| **Substitution** | Common default in many distros (`OBSERVED` / docs) | Common in some enterprise Kubernetes variants (`INFERRED` unless vendor doc cited) |

## Atlas patterns

- **O1 — Level-triggered reconciliation:** observe → diff → act (Kubernetes controllers; analogs elsewhere).  
- **O2 — Declarative API + imperative controllers:** separation preserved in k8s; compare to systemd’s unit files.  
- **O3 — Plugin edges:** CNI, CSI, device plugins — compare extension models in `kubernetes` package.

## Nomad vs Kubernetes (structural sketch)

| Dimension | kubernetes | nomad |
|-----------|------------|-------|
| **Primary workload API** | Declarative API resources (Pods, Deployments, …) (`DOCUMENTED`) | Jobs / allocations / task groups (terminology per Nomad docs) (`DOCUMENTED`) |
| **Execution backends** | Containers via CRI + runc-class runtimes (typical) (`DOCUMENTED`) | Plural **task drivers** (Docker/VM/exec/…) (`DOCUMENTED`) |
| **Control plane HA** | etcd + apiserver model (`DOCUMENTED`) | Nomad server Raft model (`DOCUMENTED`) |
| **Plugin edges** | CNI/CSI/admission (`DOCUMENTED`) | Driver/plugin ecosystem (`DOCUMENTED`) |

## AWS: ECS vs EKS vs upstream Kubernetes (structural sketch)

| Dimension | kubernetes (upstream model) | aws-eks | aws-ecs |
|-----------|----------------------------|---------|---------|
| **API surface** | Kubernetes API resources (`DOCUMENTED`) | Kubernetes API (conformant clusters) (`DOCUMENTED`, AWS EKS) | ECS API (tasks/services/task definitions) (`DOCUMENTED`, AWS ECS) |
| **Control plane** | Self/managed distros operate it (`DOCUMENTED`) | AWS manages Kubernetes control plane (standard EKS) (`DOCUMENTED`, AWS EKS) | AWS-managed ECS control plane (`DOCUMENTED`, AWS ECS) |
| **Kubernetes portability** | Reference behavior (`DOCUMENTED`) | Conformance + community tooling framing (`DOCUMENTED`, AWS EKS) | Not Kubernetes (`DOCUMENTED` product boundary) |
| **AWS product-line adjacency** | N/A | Substitutes with ECS for some AWS greenfield choices (`INFERRED`) | Substitutes with EKS for some AWS greenfield choices (`INFERRED`) |

## Managed Kubernetes (EKS, AKS, GKE, OKE, IBM IKS, DOKS, Civo, LKE, …) — structural sketch

| Dimension | aws-eks | azure-aks | gcp-gke | oci-oke | ibm-iks | digitalocean-doks | civo-kubernetes | linode-lke |
|-----------|---------|-----------|---------|---------|---------|-------------------|-----------------|------------|
| **Kubernetes API** | Conformant clusters; Kubernetes APIs (`DOCUMENTED`, AWS) | Managed Kubernetes service (`DOCUMENTED`, Microsoft Learn) | Kubernetes API for workloads (`DOCUMENTED`, Google Cloud) | CNCF-conformant Kubernetes; standard tools (`DOCUMENTED`, Oracle) | Certified managed Kubernetes; native tools/APIs (`DOCUMENTED`, IBM product page) | Standard Kubernetes toolchains; managed service (`DOCUMENTED`, DigitalOcean product docs) | Conformant managed Kubernetes; ecosystem compatibility (`DOCUMENTED`, Civo kubernetes docs) | Managed engine **built on Kubernetes** (`DOCUMENTED`, Akamai LKE techdocs) |
| **Control plane ops** | AWS-managed (standard EKS); Auto Mode extends to nodes (`DOCUMENTED`, AWS) | Azure-managed; intro notes control plane provisioning (`DOCUMENTED`, Microsoft) | Google-managed; Autopilot also manages worker nodes (`DOCUMENTED`, Google) | Oracle-managed control plane (`DOCUMENTED`, Oracle) | IBM operates/manages Kubernetes **master** (`DOCUMENTED`, IBM product page) | Fully managed control plane; HA (`DOCUMENTED`, DigitalOcean product docs) | Managed control plane per Civo Kubernetes product (`DOCUMENTED`, Civo kubernetes docs) | Managed service; no self-built cluster required (`DOCUMENTED`, Akamai LKE techdocs) |
| **Worker / node model** | EC2 / Fargate / hybrid paths per AWS docs (`DOCUMENTED`) | Nodes run applications; Linux and Windows scenarios in broader AKS docs (`DOCUMENTED` pattern) | GCE VMs as nodes (`DOCUMENTED`, Google) | Virtual / managed / self-managed node options (`DOCUMENTED`, Oracle) | Workers in **customer-owned** infrastructure; described as **single-tenant** (`DOCUMENTED`, IBM product page) | Droplets (CPU/GPU) and volumes/LB integration (`DOCUMENTED`, DigitalOcean product docs) | Clusters in Civo regions; node sizing per Civo docs (`DOCUMENTED`, Civo kubernetes docs) | Linode compute as typical worker substrate (`DOCUMENTED` / `INFERRED`, Akamai docs + `linode-lke` package) |
| **Cross-vendor substitution** | `INFERRED` vs others | `INFERRED` vs others | `INFERRED` vs others | `INFERRED` vs others | `INFERRED` vs others | `INFERRED` vs hyperscalers / peers | `INFERRED` vs hyperscalers / peers | `INFERRED` vs hyperscalers / peers |

## VMware Tanzu Kubernetes Grid (TKG) — hybrid / datacenter footprint

| Dimension | vmware-tkg |
|-----------|------------|
| **Kubernetes relationship** | Opinionated open-source Kubernetes configuration **supported by VMware**; **validated** binaries; upstream version alignment goals (`DOCUMENTED`, Broadcom TKG about hub). |
| **Lifecycle / ops model** | **Management cluster** executes requests via **Cluster API**; **Tanzu CLI** / UI paths (`DOCUMENTED`, Broadcom TKG about hub). |
| **Substitution vs cloud-managed SKUs** | `INFERRED` vs hyperscaler/regional managed Kubernetes packages in this comparative doc. |
| **Scope boundary** | **TKG Integrated Edition** is a **separate** Broadcom publication (`DOCUMENTED`, TKG about hub). |

## Red Hat OpenShift Container Platform (OCP) — enterprise Kubernetes platform

| Dimension | red-hat-openshift |
|-----------|-------------------|
| **Kubernetes relationship** | Kubernetes is a **core component** of OCP; Red Hat documents the **cluster API as 100% Kubernetes** and **`oc` compatible with `kubectl`** (`DOCUMENTED`, OCP getting started — Kubernetes overview). |
| **Platform additions** | Auth, networking, security, monitoring, logs management called out as **beyond raw Kubernetes** in the same overview (`DOCUMENTED`). |
| **Deployment span** | **On-premise** and **multi-cloud** extension language in Red Hat overview (`DOCUMENTED`). |
| **Conformance** | CNCF **`openshift`** product submissions under versioned paths (`DOCUMENTED`, `k8s-conformance` repo). |
| **Substitution** | `INFERRED` vs **TKG**, **hyperscaler/regional managed** SKUs, and other distros per atlas `relations.json`. |

## Azure: AKS vs Container Apps (API surface)

| Dimension | azure-aks | azure-container-apps |
|-----------|-----------|----------------------|
| **Kubernetes API access** | Full Kubernetes API and cluster ownership patterns (`DOCUMENTED`, Microsoft compare article) | **No** direct access to underlying Kubernetes APIs (`DOCUMENTED`, Microsoft compare article) |
| **Substrate** | Managed Kubernetes as the product surface (`DOCUMENTED`) | **Powered by Kubernetes** + Dapr/KEDA/Envoy (`DOCUMENTED`, Microsoft compare article) |
| **Substitution** | `INFERRED` when teams need kube-apiserver / cluster operations | `INFERRED` when teams want managed serverless-style container apps without cluster API |

## Azure: ACI (building block) vs higher-level services

| Dimension | azure-aci | azure-container-apps | azure-aks |
|-----------|-----------|----------------------|-----------|
| **Abstraction** | Run containers without managing VMs; “without adopting a higher-level service” (`DOCUMENTED`, Microsoft) | Serverless microservices/jobs platform (`DOCUMENTED`) | Full managed Kubernetes (`DOCUMENTED`) |
| **Orchestration** | Per-container-group / NGroups patterns; **AKS virtual nodes** bridge to Kubernetes (`DOCUMENTED`) | Kubernetes-powered **without** direct Kubernetes API (`DOCUMENTED`, compare article) | Kubernetes API + cluster operations (`DOCUMENTED`) |
| **Typical use** | Fast single/bursty instances; sidecar groups (`DOCUMENTED`) | Microservices, KEDA scaling, Dapr (`DOCUMENTED`) | General Kubernetes workloads (`DOCUMENTED`) |

## Apache Mesos (retired) — placement note

- **Two-level scheduling** and **framework** model were distinguishing historical features (`HISTORICAL`, `apache-mesos` package).  
- Project **retired** to Apache Attic — use for lineage/comparison, not greenfield ops guidance.

## Open comparative work

- **Tanzu Kubernetes Grid Integrated Edition**, **ROSA** and other managed OpenShift SKUs not yet packaged, **vSphere Supervisor**-first narratives — separate packages if matrices need them.  
- Cross-cloud control planes — mark **UNKNOWN** until sourced.
