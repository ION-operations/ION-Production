#!/usr/bin/env python3
"""NGINX, Kubernetes ingress-nginx, and ARM CCA for ATLAS (2026-04-08)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-08"

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
        "slug": "nginx",
        "title": "NGINX",
        "display_name": "NGINX (web server / reverse proxy)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** High-performance HTTP(S) server, reverse proxy, and load balancer (`DOCUMENTED`, nginx.org documentation).

## Boundaries

- Not the Kubernetes `ingress-nginx` controller project — see `ingress-nginx` package.
- Not Envoy — different codebase and configuration model.""",
        "sources": [
            {
                "id": "src-nginx-docs",
                "title": "NGINX Documentation",
                "kind": "primary",
                "url": "https://nginx.org/en/docs/",
                "access_date": DATE,
                "notes": "Official open-source NGINX documentation.",
            }
        ],
        "ledger_rows": [("ngx-001", "NGINX documents HTTP proxy and server core", "DOCUMENTED", "src-nginx-docs")],
        "relations": {
            "system_slug": "nginx",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Typical deployments on Linux server hosts.",
                },
                {
                    "type": "competes_with",
                    "target": "haproxy",
                    "evidence_tier": "INFERRED",
                    "notes": "Overlapping reverse-proxy and LB deployments.",
                },
                {
                    "type": "competes_with",
                    "target": "envoy",
                    "evidence_tier": "INFERRED",
                    "notes": "Overlapping L7 edge patterns in cloud-native stacks.",
                },
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "HTTP/3 support depends on NGINX edition and build; verify per product line.",
                },
            ],
        },
    },
    {
        "slug": "ingress-nginx",
        "title": "ingress-nginx",
        "display_name": "ingress-nginx (Kubernetes Ingress controller)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Kubernetes Ingress controller implementation using NGINX as datapath (`DOCUMENTED`, Kubernetes ingress-nginx project docs).

## Boundaries

- Not the NGINX Inc. commercial Kubernetes Ingress product unless explicitly conflated in a given deployment — this package tracks the **kubernetes.github.io/ingress-nginx** lineage.
- Not a service mesh — ingress scope.""",
        "sources": [
            {
                "id": "src-ingress-nginx-docs",
                "title": "ingress-nginx documentation",
                "kind": "primary",
                "url": "https://kubernetes.github.io/ingress-nginx/",
                "access_date": DATE,
                "notes": "Official ingress-nginx documentation.",
            }
        ],
        "ledger_rows": [("ing-001", "ingress-nginx documents Kubernetes Ingress integration", "DOCUMENTED", "src-ingress-nginx-docs")],
        "relations": {
            "system_slug": "ingress-nginx",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "depends_on",
                    "target": "nginx",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Controller embeds NGINX as the proxy engine per upstream project architecture.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Ingress controller for Kubernetes API resources.",
                },
                {
                    "type": "competes_with",
                    "target": "traefik",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable ingress controller class.",
                },
                {
                    "type": "competes_with",
                    "target": "emissary-ingress",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable ingress controller class.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "gRPC ingress patterns are common where documented for NGINX/Ingress annotations.",
                },
            ],
        },
    },
    {
        "slug": "arm-cca",
        "title": "ARM Confidential Compute Architecture (CCA)",
        "display_name": "ARM CCA",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** ARM architecture security feature set for confidential computing (Realms, Realm Management Monitor) (`DOCUMENTED` at high level via Arm publications; microarch claims per CPU generation).

## Boundaries

- Not `intel-tdx` or `amd-sev` — different ISA and firmware trust model.
- Not `confidential-computing` alone — use survey plus this package for Arm-specific claims.""",
        "sources": [
            {
                "id": "src-arm-cca",
                "title": "Arm Confidential Compute Architecture",
                "kind": "primary",
                "url": "https://www.arm.com/architecture/security-features/arm-confidential-compute-architecture",
                "access_date": DATE,
                "notes": "Arm marketing/architecture overview; follow Arm Architecture Reference Manual for normative detail.",
            }
        ],
        "ledger_rows": [("cca-001", "Arm publishes CCA overview and security feature positioning", "DOCUMENTED", "src-arm-cca")],
        "relations": {
            "system_slug": "arm-cca",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "OS/hypervisor support for CCA is kernel and firmware dependent (pin version).",
                },
                {
                    "type": "competes_with",
                    "target": "intel-tdx",
                    "evidence_tier": "INFERRED",
                    "notes": "Alternative confidential computing architecture (different CPU vendor).",
                },
                {
                    "type": "competes_with",
                    "target": "amd-sev",
                    "evidence_tier": "INFERRED",
                    "notes": "Alternative confidential computing architecture (different CPU vendor).",
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
