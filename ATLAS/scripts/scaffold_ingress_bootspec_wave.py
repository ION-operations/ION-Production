#!/usr/bin/env python3
"""Ingress / edge, Consul, and UAPI Boot Loader Specification for ATLAS (2026-04-06)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-06"

FM = """---
atlas_package: system
system_slug: {slug}
schema_version: "1.0"
last_reviewed: "{date}"
evidence_grade: B
---

# {title}

{body}
"""

FILES = [
    ("01_scope.md", "# Scope\n\n## In scope\n\nSurvey-grade; cite `sources.yaml` for normative claims.\n\n## Out of scope\n\nVendor marketing without spec locators.\n"),
    ("02_architecture.md", "# Architecture\n\nSee specification sources in `sources.yaml`.\n"),
    ("03_components.md", "# Components (survey)\n\nSee spec / product docs — not exhaustive in ATLAS.\n"),
    ("04_process_memory_namespace.md", "# Process, memory, namespace\n\nHost and trust boundaries per `sources.yaml`.\n"),
    ("05_storage_network_ipc.md", "# Storage, network, IPC\n\nSee specification for data-plane vs control-plane.\n"),
    ("06_security_permissions.md", "# Security and permissions\n\nSee security sections of primary sources.\n"),
    ("07_extension_tooling.md", "# Extension and tooling\n\nSDKs, CLIs, and reference implementations (survey).\n"),
    ("08_build_deploy_update.md", "# Build, deploy, update\n\nVersioning and compatibility per primary sources.\n"),
    ("09_operator_surface.md", "# Operator surface\n\nAPIs, CLIs, and configuration surfaces (survey).\n"),
    ("10_observability.md", "# Observability\n\nMetrics, logs, traces where specified.\n"),
    ("11_lineage.md", "# Lineage\n\nSee `relations.json` and comparative matrices.\n"),
]


def write_pkg(meta: dict) -> None:
    slug = meta["slug"]
    title = meta["title"]
    d = SYSTEMS / slug
    d.mkdir(parents=True, exist_ok=True)

    (d / "00_identity.md").write_text(
        FM.format(slug=slug, date=DATE, title=f"{title} — Identity", body=meta["identity_md"]),
        encoding="utf-8",
    )
    for name, body in FILES:
        (d / name).write_text(
            FM.format(slug=slug, date=DATE, title=name.replace(".md", "").replace("_", " ").title(), body=body),
            encoding="utf-8",
        )

    (d / "12_relation_map.md").write_text(
        FM.format(
            slug=slug,
            date=DATE,
            title="Relation map",
            body="See `relations.json`. **Comparative:** `comparative/ai_operating_system_reference_matrices.md`.",
        ),
        encoding="utf-8",
    )

    led = meta.get("ledger_rows", [("x-001", "Primary sources in `sources.yaml`", "DOCUMENTED", "sources")])
    rows = "\n".join(f"| {cid} | {claim} | {tier} | `{loc}` | |" for cid, claim, tier, loc in led)
    (d / "13_evidence_ledger.md").write_text(
        FM.format(
            slug=slug,
            date=DATE,
            title="Evidence ledger",
            body=f"| claim_id | claim | tier | locator | notes |\n|----------|-------|------|---------|-------|\n{rows}\n",
        ),
        encoding="utf-8",
    )

    (d / "14_documented_vs_inferred.md").write_text(
        FM.format(
            slug=slug,
            date=DATE,
            title="Documented vs inferred",
            body="## DOCUMENTED\n\nPrimary specifications in `sources.yaml`.\n\n## INFERRED\n\nDeployment topology and vendor defaults — pin environment when load-bearing.\n",
        ),
        encoding="utf-8",
    )

    (d / "sources.yaml").write_text(
        yaml.dump({"schema_version": "1.0", "last_reviewed": DATE, "sources": meta["sources"]}, sort_keys=False),
        encoding="utf-8",
    )
    (d / "relations.json").write_text(json.dumps(meta["relations"], indent=2) + "\n", encoding="utf-8")
    (d / "tags.yaml").write_text(
        yaml.dump({"schema_version": "1.0", "last_reviewed": DATE, "tags": meta["tags"]}, sort_keys=False),
        encoding="utf-8",
    )


PACKAGES = [
    {
        "slug": "traefik",
        "title": "Traefik",
        "display_name": "Traefik (ingress / reverse proxy)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Cloud-native HTTP reverse proxy and ingress controller with dynamic configuration (`DOCUMENTED`, Traefik docs).

## Boundaries

- Not a full service mesh control plane like `istio` — ingress / edge routing focus (though ecosystem extends).
- Not Envoy — different implementation; see `competes_with` where deployments substitute.""",
        "sources": [
            {
                "id": "src-traefik-docs",
                "title": "Traefik Documentation",
                "kind": "primary",
                "url": "https://doc.traefik.io/traefik/",
                "access_date": DATE,
                "notes": "Official Traefik documentation.",
            }
        ],
        "ledger_rows": [("trf-001", "Traefik documents routers, middleware, providers (Kubernetes, etc.)", "DOCUMENTED", "src-traefik-docs")],
        "relations": {
            "system_slug": "traefik",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Traefik documents Kubernetes Ingress / Gateway API style integration.",
                },
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "HTTP stack features depend on version and entrypoints; verify per release.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "gRPC routing is a common edge use case where documented for Traefik version.",
                },
                {
                    "type": "competes_with",
                    "target": "envoy",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable L7 edge / ingress in many Kubernetes deployments.",
                },
                {
                    "type": "integrates_with",
                    "target": "opentelemetry",
                    "evidence_tier": "INFERRED",
                    "notes": "Tracing integration is common in production stacks (check Traefik OTel docs per version).",
                },
            ],
        },
    },
    {
        "slug": "consul",
        "title": "HashiCorp Consul",
        "display_name": "Consul (service discovery / Connect)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Distributed service identity and networking — service catalog, health checks, KV, and Consul Connect (mTLS service-to-service) (`DOCUMENTED`, HashiCorp Consul docs).

## Boundaries

- Not Kubernetes — often runs on VMs or K8s as a workload.
- Not identical to `istio` — different control/data model; overlaps in *service mesh* problem space.""",
        "sources": [
            {
                "id": "src-consul-docs",
                "title": "HashiCorp Consul Documentation",
                "kind": "primary",
                "url": "https://developer.hashicorp.com/consul/docs",
                "access_date": DATE,
                "notes": "Official Consul documentation.",
            }
        ],
        "ledger_rows": [("cns-001", "Consul documents agents, service catalog, and Connect", "DOCUMENTED", "src-consul-docs")],
        "relations": {
            "system_slug": "consul",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Consul on Kubernetes is a common deployment pattern (Helm / operators).",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "Consul uses gRPC in internal RPC paths per HashiCorp documentation.",
                },
                {
                    "type": "competes_with",
                    "target": "istio",
                    "evidence_tier": "INFERRED",
                    "notes": "Overlapping service connectivity / mesh-class concerns; not drop-in equivalent.",
                },
                {
                    "type": "competes_with",
                    "target": "linkerd",
                    "evidence_tier": "INFERRED",
                    "notes": "Kubernetes-native mesh alternatives in some orgs.",
                },
                {
                    "type": "integrates_with",
                    "target": "envoy",
                    "evidence_tier": "INFERRED",
                    "notes": "Consul service mesh dataplane options have included Envoy-class integration in documented architectures.",
                },
            ],
        },
    },
    {
        "slug": "uapi-boot-loader-specification",
        "title": "UAPI Boot Loader Specification",
        "display_name": "UAPI Boot Loader Specification (BLS)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** UAPI Group UAPI.1 — file formats and naming for distribution-independent boot loader menus shared across multiple bootloaders (`DOCUMENTED`, UAPI spec).

## Boundaries

- Not a bootloader implementation — spec only; see `grub`, `systemd-boot`.
- Not UKI — see `unified-kernel-image` for PE bundle semantics.""",
        "sources": [
            {
                "id": "src-uapi-bls",
                "title": "UAPI.1 Boot Loader Specification",
                "kind": "primary",
                "url": "https://uapi-group.org/specifications/specs/boot_loader_specification/",
                "access_date": DATE,
                "notes": "Canonical UAPI Group BLS.",
            }
        ],
        "ledger_rows": [("bls-001", "UAPI.1 defines boot loader menu file layout and naming", "DOCUMENTED", "src-uapi-bls")],
        "relations": {
            "system_slug": "uapi-boot-loader-specification",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "uefi",
                    "evidence_tier": "INFERRED",
                    "notes": "BLS complements UEFI boot paths on Linux distributions.",
                },
                {
                    "type": "integrates_with",
                    "target": "grub",
                    "evidence_tier": "INFERRED",
                    "notes": "Distributions may align GRUB entries with BLS drop-in conventions.",
                },
                {
                    "type": "integrates_with",
                    "target": "systemd-boot",
                    "evidence_tier": "INFERRED",
                    "notes": "systemd-boot and BLS are commonly discussed together in Linux boot documentation.",
                },
                {
                    "type": "integrates_with",
                    "target": "unified-kernel-image",
                    "evidence_tier": "INFERRED",
                    "notes": "Boot menu entries may reference UKI paths where distros adopt both.",
                },
            ],
        },
    },
]


def main() -> None:
    for p in PACKAGES:
        if (SYSTEMS / p["slug"]).exists():
            print("skip existing", p["slug"])
            continue
        write_pkg(p)
        print("wrote", p["slug"])


if __name__ == "__main__":
    main()
