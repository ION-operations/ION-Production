#!/usr/bin/env python3
"""CDN vendor breadth (Fastly, Akamai, Edgio) and RISC-V ISA survey for ATLAS (2026-04-11)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-11"

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
        "slug": "fastly",
        "title": "Fastly",
        "display_name": "Fastly (CDN / Compute@Edge)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Global edge cloud — CDN caching, **Compute@Edge** (V8 isolates / Wasm-class workloads per Fastly docs), and security features.

## Boundaries

- Not `cloudflare-workers` — different runtime and product surface.
- Not `amazon-cloudfront` — substitute CDN class, not identical APIs.""",
        "sources": [
            {
                "id": "src-fastly-docs",
                "title": "Fastly Developer Hub",
                "kind": "primary",
                "url": "https://www.fastly.com/documentation/guides/",
                "access_date": DATE,
                "notes": "Official Fastly documentation.",
            }
        ],
        "ledger_rows": [("fst-001", "Fastly documents CDN and Compute@Edge deployment", "DOCUMENTED", "src-fastly-docs")],
        "relations": {
            "system_slug": "fastly",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "competes_with",
                    "target": "amazon-cloudfront",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable global CDN / edge delivery class.",
                },
                {
                    "type": "competes_with",
                    "target": "azure-front-door",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable global edge delivery class.",
                },
                {
                    "type": "competes_with",
                    "target": "cloudflare-workers",
                    "evidence_tier": "INFERRED",
                    "notes": "Edge compute + CDN overlap.",
                },
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "HTTP/3 and QUIC support depends on Fastly product and configuration.",
                },
                {
                    "type": "integrates_with",
                    "target": "webassembly",
                    "evidence_tier": "INFERRED",
                    "notes": "Compute@Edge Wasm module paths where documented.",
                },
            ],
        },
    },
    {
        "slug": "akamai",
        "title": "Akamai",
        "display_name": "Akamai (CDN / edge security)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Global content delivery, DNS, application and API security, and edge services (`DOCUMENTED`, Akamai TechDocs).

## Boundaries

- Not a single open-source repo — commercial edge platform with many product lines.
- Not `fastly` / `cloudflare-workers` — competitor class.""",
        "sources": [
            {
                "id": "src-akamai-techdocs",
                "title": "Akamai TechDocs",
                "kind": "primary",
                "url": "https://techdocs.akamai.com/",
                "access_date": DATE,
                "notes": "Akamai technical documentation portal.",
            }
        ],
        "ledger_rows": [("akm-001", "Akamai publishes TechDocs for CDN and edge products", "DOCUMENTED", "src-akamai-techdocs")],
        "relations": {
            "system_slug": "akamai",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "competes_with",
                    "target": "amazon-cloudfront",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable enterprise CDN class.",
                },
                {
                    "type": "competes_with",
                    "target": "fastly",
                    "evidence_tier": "INFERRED",
                    "notes": "CDN / edge vendor competition.",
                },
                {
                    "type": "competes_with",
                    "target": "cloudflare-workers",
                    "evidence_tier": "INFERRED",
                    "notes": "Overlapping edge security and delivery.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Ingress and origin patterns with K8s in customer architectures.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "API and microservice edge patterns where documented.",
                },
            ],
        },
    },
    {
        "slug": "edgio",
        "title": "Edgio",
        "display_name": "Edgio (CDN / edge applications)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Edge platform combining CDN, **Applications** (routing, caching, serverless), and related services (`DOCUMENTED`, Edgio developer docs).

## Boundaries

- Corporate/product line history includes Limelight heritage — **pin** **claims** **to** **current** **Edgio** **docs.**  
- Not `akamai` or `fastly` — substitute CDN class.""",
        "sources": [
            {
                "id": "src-edgio-docs",
                "title": "Edgio Documentation",
                "kind": "primary",
                "url": "https://docs.edg.io/",
                "access_date": DATE,
                "notes": "Edgio (edg.io) documentation.",
            }
        ],
        "ledger_rows": [("edg-001", "Edgio documents Applications and CDN edge products", "DOCUMENTED", "src-edgio-docs")],
        "relations": {
            "system_slug": "edgio",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "competes_with",
                    "target": "amazon-cloudfront",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable CDN / edge delivery class.",
                },
                {
                    "type": "competes_with",
                    "target": "fastly",
                    "evidence_tier": "INFERRED",
                    "notes": "CDN vendor competition.",
                },
                {
                    "type": "competes_with",
                    "target": "akamai",
                    "evidence_tier": "INFERRED",
                    "notes": "CDN vendor competition.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Customer deployments fronting K8s origins.",
                },
            ],
        },
    },
    {
        "slug": "riscv-isa",
        "title": "RISC-V ISA",
        "display_name": "RISC-V (instruction set architecture)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** Open modular ISA family (base integer + standard extensions) ratified by RISC-V International (`DOCUMENTED` where specs are published).

## Boundaries

- Not `linux-kernel` — the kernel port implements ABI on top of RISC-V.
- Not `arm-cca` — Arm confidential compute is an orthogonal Arm-specific domain.""",
        "sources": [
            {
                "id": "src-riscv-specs",
                "title": "RISC-V Technical Specifications",
                "kind": "primary",
                "url": "https://riscv.org/technical/specifications/",
                "access_date": DATE,
                "notes": "RISC-V International specification catalog.",
            }
        ],
        "ledger_rows": [("rv-001", "RISC-V International publishes ratified ISA specifications", "DOCUMENTED", "src-riscv-specs")],
        "relations": {
            "system_slug": "riscv-isa",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Linux documents and maintains a RISC-V architecture port.",
                },
                {
                    "type": "integrates_with",
                    "target": "llvm-ir",
                    "evidence_tier": "INFERRED",
                    "notes": "LLVM targets RISC-V in mainstream backends.",
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
