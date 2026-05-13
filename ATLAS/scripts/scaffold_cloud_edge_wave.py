#!/usr/bin/env python3
"""Managed cloud load balancing and API gateway products for ATLAS (2026-04-09)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-09"

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
        "slug": "aws-elastic-load-balancing",
        "title": "AWS Elastic Load Balancing",
        "display_name": "AWS Elastic Load Balancing (ALB / NLB / GWLB)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** AWS managed load balancing (Application, Network, Gateway, Classic families per AWS documentation).

## Boundaries

- Not self-hosted `envoy` or `nginx` — managed control/data plane by AWS.
- Not the Kubernetes Service `type: LoadBalancer` implementation itself — often backs that pattern on EKS (INFERRED integration).""",
        "sources": [
            {
                "id": "src-aws-elb",
                "title": "What is Elastic Load Balancing?",
                "kind": "primary",
                "url": "https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/introduction.html",
                "access_date": DATE,
                "notes": "AWS ELB user guide introduction.",
            }
        ],
        "ledger_rows": [("elb-001", "AWS documents ELB product families and use cases", "DOCUMENTED", "src-aws-elb")],
        "relations": {
            "system_slug": "aws-elastic-load-balancing",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "aws-eks",
                    "evidence_tier": "INFERRED",
                    "notes": "EKS workloads commonly fronted by AWS load balancers.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Ingress and Service integration patterns on cloud Kubernetes.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "ALB can front gRPC targets where documented for load balancer type/version.",
                },
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "HTTP/3 availability is product/version dependent; verify AWS release notes.",
                },
                {
                    "type": "competes_with",
                    "target": "envoy",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable edge tier vs customer-managed proxies.",
                },
            ],
        },
    },
    {
        "slug": "amazon-api-gateway",
        "title": "Amazon API Gateway",
        "display_name": "Amazon API Gateway",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** AWS managed HTTP/REST/WebSocket API front door with auth, throttling, and integration targets (`DOCUMENTED`, AWS docs).

## Boundaries

- Not a generic gRPC gateway — REST/HTTP focus in common use; verify gRPC features per AWS product line.
- Not `amazon-s3` — different API surface.""",
        "sources": [
            {
                "id": "src-aws-apigw",
                "title": "What is Amazon API Gateway?",
                "kind": "primary",
                "url": "https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html",
                "access_date": DATE,
                "notes": "API Gateway developer guide.",
            }
        ],
        "ledger_rows": [("apg-001", "AWS documents API Gateway types and integration models", "DOCUMENTED", "src-aws-apigw")],
        "relations": {
            "system_slug": "amazon-api-gateway",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "amazon-s3",
                    "evidence_tier": "INFERRED",
                    "notes": "API Gateway can integrate with S3 as backend in documented patterns.",
                },
                {
                    "type": "integrates_with",
                    "target": "openid-connect",
                    "evidence_tier": "INFERRED",
                    "notes": "JWT/OIDC authorizers are common API Gateway patterns.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "Check AWS API Gateway v2 / HTTP API gRPC support per region and docs.",
                },
                {
                    "type": "competes_with",
                    "target": "envoy",
                    "evidence_tier": "INFERRED",
                    "notes": "Managed API edge vs self-managed gateway mesh.",
                },
            ],
        },
    },
    {
        "slug": "azure-application-gateway",
        "title": "Azure Application Gateway",
        "display_name": "Azure Application Gateway",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Azure layer-7 load balancer with optional WAF and ingress patterns for AKS (`DOCUMENTED`, Microsoft Learn).

## Boundaries

- Not Azure Front Door (separate global CDN/edge product) — this package is Application Gateway grain only unless expanded later.
- Not self-hosted `nginx`.""",
        "sources": [
            {
                "id": "src-azure-appgw",
                "title": "What is Azure Application Gateway?",
                "kind": "primary",
                "url": "https://learn.microsoft.com/en-us/azure/application-gateway/overview",
                "access_date": DATE,
                "notes": "Microsoft Learn overview.",
            }
        ],
        "ledger_rows": [("apw-001", "Microsoft documents Application Gateway features and AKS ingress", "DOCUMENTED", "src-azure-appgw")],
        "relations": {
            "system_slug": "azure-application-gateway",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "azure-aks",
                    "evidence_tier": "INFERRED",
                    "notes": "Application Gateway Ingress Controller patterns on AKS.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Kubernetes ingress integration via AGIC where deployed.",
                },
                {
                    "type": "competes_with",
                    "target": "aws-elastic-load-balancing",
                    "evidence_tier": "INFERRED",
                    "notes": "Cross-cloud managed L7 load balancing class.",
                },
                {
                    "type": "competes_with",
                    "target": "haproxy",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable edge tier vs self-managed HAProxy.",
                },
            ],
        },
    },
    {
        "slug": "gcp-load-balancing",
        "title": "Google Cloud Load Balancing",
        "display_name": "Google Cloud Load Balancing",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Google Cloud managed load balancing (global/regional, L4/L7 families per GCP docs).

## Boundaries

- Not GKE Ingress controller implementation detail — this package is the GCP LB product surface.
- Not `envoy` unless the customer runs Envoy separately.""",
        "sources": [
            {
                "id": "src-gcp-lb",
                "title": "Cloud Load Balancing overview",
                "kind": "primary",
                "url": "https://cloud.google.com/load-balancing/docs/load-balancing-overview",
                "access_date": DATE,
                "notes": "Google Cloud load balancing documentation.",
            }
        ],
        "ledger_rows": [("gcl-001", "Google documents Cloud Load Balancing product families", "DOCUMENTED", "src-gcp-lb")],
        "relations": {
            "system_slug": "gcp-load-balancing",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "gcp-gke",
                    "evidence_tier": "INFERRED",
                    "notes": "GKE Services and Ingress commonly use GCP load balancers.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Cloud LB integration for Kubernetes on GCP.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "gRPC-friendly backends depend on LB type and configuration.",
                },
                {
                    "type": "competes_with",
                    "target": "aws-elastic-load-balancing",
                    "evidence_tier": "INFERRED",
                    "notes": "Cross-cloud managed load balancing class.",
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
