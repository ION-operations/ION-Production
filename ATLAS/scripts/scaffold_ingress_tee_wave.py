#!/usr/bin/env python3
"""Ingress breadth (Emissary, HAProxy) and vendor TEE grains for ATLAS (2026-04-07)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-07"

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
        "slug": "emissary-ingress",
        "title": "Emissary-Ingress",
        "display_name": "Emissary-Ingress (Envoy-based ingress)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Kubernetes ingress controller and API gateway built on Envoy (`DOCUMENTED`, upstream repository and CNCF project materials).

## Boundaries

- Not raw Envoy — control plane and CRDs around Envoy data plane.
- Not Traefik — different configuration model; see `competes_with` where substitutable.""",
        "sources": [
            {
                "id": "src-emissary-cncf",
                "title": "Emissary-Ingress (CNCF project)",
                "kind": "primary",
                "url": "https://www.cncf.io/projects/emissary-ingress/",
                "access_date": DATE,
                "notes": "CNCF project page; links to code and documentation.",
            },
            {
                "id": "src-emissary-github",
                "title": "Emissary-Ingress (source repository)",
                "kind": "primary",
                "url": "https://github.com/emissary-ingress/emissary",
                "access_date": DATE,
                "notes": "Upstream GitHub repository; README points to docs.",
            },
        ],
        "ledger_rows": [
            ("emi-001", "CNCF lists Emissary-Ingress as graduated ingress project", "DOCUMENTED", "src-emissary-cncf"),
            ("emi-002", "Upstream repository documents Envoy-based architecture", "DOCUMENTED", "src-emissary-github"),
        ],
        "relations": {
            "system_slug": "emissary-ingress",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Ingress controller role documented for Kubernetes.",
                },
                {
                    "type": "integrates_with",
                    "target": "envoy",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Architecture centers on Envoy as data plane in upstream documentation.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "gRPC routing is a common ingress use case on Envoy-based stacks.",
                },
                {
                    "type": "competes_with",
                    "target": "traefik",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable ingress class on Kubernetes in many orgs.",
                },
            ],
        },
    },
    {
        "slug": "haproxy",
        "title": "HAProxy",
        "display_name": "HAProxy (load balancer / reverse proxy)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** High-performance TCP/HTTP load balancer and proxy (`DOCUMENTED`, HAProxy documentation).

## Boundaries

- Not Kubernetes — though HAProxy Ingress Controller and similar patterns exist (INFERRED deployment).
- Not Envoy — different implementation; overlapping edge/L7 deployment class.""",
        "sources": [
            {
                "id": "src-haproxy-docs",
                "title": "HAProxy Documentation",
                "kind": "primary",
                "url": "https://docs.haproxy.org/",
                "access_date": DATE,
                "notes": "Official HAProxy documentation.",
            }
        ],
        "ledger_rows": [("hap-001", "HAProxy documents proxy, balancing, and TLS configuration", "DOCUMENTED", "src-haproxy-docs")],
        "relations": {
            "system_slug": "haproxy",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "HAProxy is used as ingress / external LB in many Kubernetes deployments.",
                },
                {
                    "type": "competes_with",
                    "target": "envoy",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable L7/L4 edge in data centers and clouds.",
                },
                {
                    "type": "competes_with",
                    "target": "traefik",
                    "evidence_tier": "INFERRED",
                    "notes": "Overlapping ingress and reverse-proxy deployments.",
                },
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "HTTP/3 support depends on HAProxy version and build; verify per release.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Typical production deployments on Linux.",
                },
            ],
        },
    },
    {
        "slug": "intel-tdx",
        "title": "Intel Trust Domain Extensions (TDX)",
        "display_name": "Intel TDX",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** Intel hardware trust domain extensions for confidential VMs and guest memory isolation (`DOCUMENTED` where Intel publishes spec/whitepapers; silicon availability is deployment-specific).

## Boundaries

- Not the `confidential-computing` survey umbrella alone — vendor-specific grain; pair with survey for cross-vendor context.
- Not a substitute for full application attestation design — TEE is one layer.""",
        "sources": [
            {
                "id": "src-intel-tdx",
                "title": "Intel Trust Domain Extensions (overview)",
                "kind": "primary",
                "url": "https://www.intel.com/content/www/us/en/developer/tools/trust-domain-extensions/overview.html",
                "access_date": DATE,
                "notes": "Intel developer-facing TDX overview; pin architecture manuals for normative microarch claims.",
            }
        ],
        "ledger_rows": [("tdx-001", "Intel publishes TDX overview and programming documentation (verify edition)", "DOCUMENTED", "src-intel-tdx")],
        "relations": {
            "system_slug": "intel-tdx",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Linux KVM/QEMU stacks integrate TDX paths where enabled (pin kernel version).",
                },
                {
                    "type": "integrates_with",
                    "target": "tpm2",
                    "evidence_tier": "INFERRED",
                    "notes": "Attestation ecosystems may combine TDX evidence with TPM-style roots (deployment-specific).",
                },
                {
                    "type": "competes_with",
                    "target": "amd-sev",
                    "evidence_tier": "INFERRED",
                    "notes": "Alternative x86 confidential VM vendor technology class.",
                },
            ],
        },
    },
    {
        "slug": "amd-sev",
        "title": "AMD Secure Encrypted Virtualization (SEV)",
        "display_name": "AMD SEV / SEV-SNP",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** AMD memory encryption and guest isolation for virtual machines (SEV, SEV-ES, SEV-SNP per generation) (`DOCUMENTED` where AMD publishes PSP/SEV docs; claim granularity per CPU generation).

## Boundaries

- Not `intel-tdx` — different vendor ISA and firmware contract.
- Not `confidential-computing` alone — use both survey and vendor package for honest tiers.""",
        "sources": [
            {
                "id": "src-amd-sev",
                "title": "AMD Secure Encrypted Virtualization",
                "kind": "primary",
                "url": "https://www.amd.com/en/developer/sev.html",
                "access_date": DATE,
                "notes": "AMD developer SEV landing page; follow links to programming manuals for normative detail.",
            }
        ],
        "ledger_rows": [("sev-001", "AMD publishes SEV / SEV-SNP developer documentation", "DOCUMENTED", "src-amd-sev")],
        "relations": {
            "system_slug": "amd-sev",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "KVM and hypervisor stacks enable SEV/SNP guests where configured.",
                },
                {
                    "type": "competes_with",
                    "target": "intel-tdx",
                    "evidence_tier": "INFERRED",
                    "notes": "Alternative x86 confidential VM vendor technology class.",
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
