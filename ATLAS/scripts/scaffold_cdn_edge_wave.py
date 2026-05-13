#!/usr/bin/env python3
"""Global CDN and edge-compute surfaces for ATLAS (2026-04-10)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-10"

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
        "slug": "azure-front-door",
        "title": "Azure Front Door",
        "display_name": "Azure Front Door",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Azure global application delivery and protection network (CDN, WAF, routing per Microsoft Learn).

## Boundaries

- Not `azure-application-gateway` — regional Application Gateway vs global Front Door (different products).
- Not self-hosted `nginx` or `envoy`.""",
        "sources": [
            {
                "id": "src-azure-fd",
                "title": "What is Azure Front Door?",
                "kind": "primary",
                "url": "https://learn.microsoft.com/en-us/azure/frontdoor/front-door-overview",
                "access_date": DATE,
                "notes": "Microsoft Learn overview.",
            }
        ],
        "ledger_rows": [("afd-001", "Microsoft documents Azure Front Door global edge and routing", "DOCUMENTED", "src-azure-fd")],
        "relations": {
            "system_slug": "azure-front-door",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "azure-aks",
                    "evidence_tier": "INFERRED",
                    "notes": "Common to front AKS-hosted APIs with Front Door.",
                },
                {
                    "type": "integrates_with",
                    "target": "azure-application-gateway",
                    "evidence_tier": "INFERRED",
                    "notes": "Layered Azure edge patterns (global + regional) in some architectures.",
                },
                {
                    "type": "competes_with",
                    "target": "amazon-cloudfront",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable global CDN / edge delivery class.",
                },
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "HTTP/3 and QUIC features depend on Azure Front Door SKU and docs.",
                },
            ],
        },
    },
    {
        "slug": "amazon-cloudfront",
        "title": "Amazon CloudFront",
        "display_name": "Amazon CloudFront",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** AWS content delivery network (CDN) with edge caching and request routing (`DOCUMENTED`, AWS developer guide).

## Boundaries

- Not `amazon-s3` — S3 is often an origin, not the CDN control plane.
- Not `aws-elastic-load-balancing` — different edge product (though architectures combine).""",
        "sources": [
            {
                "id": "src-cloudfront",
                "title": "What is Amazon CloudFront?",
                "kind": "primary",
                "url": "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html",
                "access_date": DATE,
                "notes": "CloudFront developer guide introduction.",
            }
        ],
        "ledger_rows": [("cfr-001", "AWS documents CloudFront CDN and origin integration", "DOCUMENTED", "src-cloudfront")],
        "relations": {
            "system_slug": "amazon-cloudfront",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "amazon-s3",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "S3 bucket origins are a standard CloudFront pattern in AWS documentation.",
                },
                {
                    "type": "integrates_with",
                    "target": "aws-elastic-load-balancing",
                    "evidence_tier": "INFERRED",
                    "notes": "ALB/NLB as custom origins in common AWS architectures.",
                },
                {
                    "type": "integrates_with",
                    "target": "amazon-api-gateway",
                    "evidence_tier": "INFERRED",
                    "notes": "API Gateway behind CloudFront in documented edge patterns.",
                },
                {
                    "type": "competes_with",
                    "target": "azure-front-door",
                    "evidence_tier": "INFERRED",
                    "notes": "Cross-cloud CDN class.",
                },
                {
                    "type": "competes_with",
                    "target": "cloudflare-workers",
                    "evidence_tier": "INFERRED",
                    "notes": "Overlapping global edge delivery (different execution models).",
                },
            ],
        },
    },
    {
        "slug": "cloudflare-workers",
        "title": "Cloudflare Workers",
        "display_name": "Cloudflare Workers",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Serverless JavaScript/WebAssembly execution at Cloudflare edge PoPs (`DOCUMENTED`, Cloudflare Workers docs).

## Boundaries

- Not a full Linux VM — V8/isolates model per product docs.
- Not the `webassembly` spec itself — may host Wasm modules where documented for the Workers runtime.""",
        "sources": [
            {
                "id": "src-cf-workers",
                "title": "Cloudflare Workers documentation",
                "kind": "primary",
                "url": "https://developers.cloudflare.com/workers/",
                "access_date": DATE,
                "notes": "Official Workers developer documentation.",
            }
        ],
        "ledger_rows": [("cfw-001", "Cloudflare documents Workers runtime and deployment model", "DOCUMENTED", "src-cf-workers")],
        "relations": {
            "system_slug": "cloudflare-workers",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "Cloudflare edge stack is QUIC/HTTP3 heavy in public documentation culture.",
                },
                {
                    "type": "integrates_with",
                    "target": "webassembly",
                    "evidence_tier": "INFERRED",
                    "notes": "Workers support Wasm modules in documented runtime paths (verify product edition).",
                },
                {
                    "type": "competes_with",
                    "target": "amazon-cloudfront",
                    "evidence_tier": "INFERRED",
                    "notes": "Global edge; different programming model (compute at edge vs CDN-only).",
                },
                {
                    "type": "competes_with",
                    "target": "azure-front-door",
                    "evidence_tier": "INFERRED",
                    "notes": "Global edge delivery class.",
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
