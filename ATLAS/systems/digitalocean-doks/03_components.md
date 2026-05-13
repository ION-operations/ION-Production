---
atlas_package: system
system_slug: digitalocean-doks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Components

| Area | Role | Evidence |
|------|------|----------|
| Managed control plane | Kubernetes control plane operated by DigitalOcean | DOCUMENTED |
| Workers | Droplet-backed node pools (typical reading of product docs) | DOCUMENTED / INFERRED |
| Tooling | `kubectl`, DO API, `doctl`, Terraform docs linked | DOCUMENTED |
