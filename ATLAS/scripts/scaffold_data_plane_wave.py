#!/usr/bin/env python3
"""Data-plane / mesh / boot wave for ATLAS (2026-04-04)."""
from __future__ import annotations

import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-04"

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
        "slug": "postgresql",
        "title": "PostgreSQL",
        "display_name": "PostgreSQL (database)",
        "primary_kind": "protocol",
        "tags": ["protocol", "distributed-system"],
        "identity_md": """**Kind:** **Open**-**source** **relational** **database** **with** **documented** **wire** **protocol** **(frontend/backend)** **and** **SQL** **dialect** (`DOCUMENTED`, PostgreSQL docs).

## Boundaries

- **Not** **pure** **SQL** **standard** **—** **implementation** **with** **extensions.**  
- **Not** **a** **message** **broker** — **see** **`apache-kafka`**.""",
        "sources": [
            {
                "id": "src-pg-docs",
                "title": "PostgreSQL Documentation",
                "kind": "primary",
                "url": "https://www.postgresql.org/docs/",
                "access_date": DATE,
                "notes": "Official docs including protocol overview.",
            }
        ],
        "ledger_rows": [("pq-001", "PostgreSQL documents client/server protocol", "DOCUMENTED", "src-pg-docs")],
        "relations": {
            "system_slug": "postgresql",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Typical server deployments on Linux hosts.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "StatefulSets and operators commonly run PostgreSQL on Kubernetes.",
                },
                {
                    "type": "integrates_with",
                    "target": "openid-connect",
                    "evidence_tier": "INFERRED",
                    "notes": "Application-level auth often uses OIDC upstream of app DB access.",
                },
            ],
        },
    },
    {
        "slug": "sqlite",
        "title": "SQLite",
        "display_name": "SQLite (embedded database)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **Embedded** **SQL** **database** **engine** **(library)** **with** **file** **format** **and** **C** **API** (`DOCUMENTED`, SQLite docs).

## Boundaries

- **Not** **a** **network** **server** **by** **default** — **embedding** **model.**  
- **Not** **PostgreSQL** **compatibility** **guarantee** — **different** **SQL** **surface.**""",
        "sources": [
            {
                "id": "src-sqlite-docs",
                "title": "SQLite Documentation",
                "kind": "primary",
                "url": "https://www.sqlite.org/docs.html",
                "access_date": DATE,
                "notes": "Official SQLite documentation.",
            }
        ],
        "ledger_rows": [("sql-001", "SQLite documents C API and file format", "DOCUMENTED", "src-sqlite-docs")],
        "relations": {
            "system_slug": "sqlite",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Common embedding target on Linux and other POSIX hosts.",
                },
                {
                    "type": "integrates_with",
                    "target": "webassembly",
                    "evidence_tier": "INFERRED",
                    "notes": "SQLite is embedded in Wasm runtimes and browsers in some stacks (implementation-dependent).",
                },
            ],
        },
    },
    {
        "slug": "redis",
        "title": "Redis",
        "display_name": "Redis (in-memory data store)",
        "primary_kind": "protocol",
        "tags": ["protocol", "distributed-system"],
        "identity_md": """**Kind:** **In**-**memory** **data** **structure** **store** **with** **RESP** **wire** **protocol** **and** **rich** **command** **set** (`DOCUMENTED`, Redis docs).

## Boundaries

- **Not** **durable** **SQL** **OLTP** **—** **different** **consistency** **and** **persistence** **model.**  
- **Not** **Kafka** **—** **see** **`apache-kafka`**.""",
        "sources": [
            {
                "id": "src-redis-docs",
                "title": "Redis Documentation",
                "kind": "primary",
                "url": "https://redis.io/docs/",
                "access_date": DATE,
                "notes": "Official Redis documentation.",
            }
        ],
        "ledger_rows": [("rds-001", "Redis documents RESP and command reference", "DOCUMENTED", "src-redis-docs")],
        "relations": {
            "system_slug": "redis",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Redis is commonly deployed as cache/session store on Kubernetes.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Typical deployments on Linux server hosts.",
                },
            ],
        },
    },
    {
        "slug": "apache-kafka",
        "title": "Apache Kafka",
        "display_name": "Apache Kafka (distributed event streaming)",
        "primary_kind": "protocol",
        "tags": ["protocol", "distributed-system"],
        "identity_md": """**Kind:** **Distributed** **event** **streaming** **platform** **(topics,** **partitions,** **brokers,** **producer/consumer** **protocols)** (`DOCUMENTED`, Kafka docs).

## Boundaries

- **Not** **a** **relational** **database** — **log**-**oriented** **streaming.**  
- **Not** **Redis** **pub/sub** **semantics** **—** **different** **durability** **model.**""",
        "sources": [
            {
                "id": "src-kafka-docs",
                "title": "Apache Kafka Documentation",
                "kind": "primary",
                "url": "https://kafka.apache.org/documentation/",
                "access_date": DATE,
                "notes": "Official Kafka documentation.",
            }
        ],
        "ledger_rows": [("kfk-001", "Kafka documents broker and client protocols at docs site", "DOCUMENTED", "src-kafka-docs")],
        "relations": {
            "system_slug": "apache-kafka",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Kafka operators and Helm charts are common on Kubernetes.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "Some ecosystem components use gRPC alongside Kafka deployments.",
                },
            ],
        },
    },
    {
        "slug": "envoy",
        "title": "Envoy Proxy",
        "display_name": "Envoy (L7 proxy / data plane)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** **High**-**performance** **edge/middle** **proxy** **(HTTP/gRPC/TCP)** **with** **xDS** **dynamic** **configuration** **culture** (`DOCUMENTED`, Envoy docs).

## Boundaries

- **Not** **a** **service** **mesh** **control** **plane** **alone** — **see** **`istio`.**  
- **Not** **Kubernetes** **—** **often** **deployed** **as** **DaemonSet** **/** **sidecar.**""",
        "sources": [
            {
                "id": "src-envoy-docs",
                "title": "Envoy Proxy Documentation",
                "kind": "primary",
                "url": "https://www.envoyproxy.io/docs",
                "access_date": DATE,
                "notes": "Official Envoy documentation.",
            }
        ],
        "ledger_rows": [("env-001", "Envoy documents listeners, clusters, xDS configuration", "DOCUMENTED", "src-envoy-docs")],
        "relations": {
            "system_slug": "envoy",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Common as ingress or mesh data plane on Kubernetes.",
                },
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "Envoy supports gRPC routing and observability features.",
                },
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "HTTP/3 support depends on build and deployment (check Envoy release notes).",
                },
            ],
        },
    },
    {
        "slug": "istio",
        "title": "Istio",
        "display_name": "Istio (service mesh)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** **Service** **mesh** **control** **plane** **(traffic** **management,** **security,** **observability)** **with** **sidecar** **data** **plane** **culture** **(Envoy)** (`DOCUMENTED`, Istio docs).

## Boundaries

- **Not** **Kubernetes** **itself** — **add**-**on** **on** **top** **of** **K8s** **typically.**  
- **Not** **Envoy** **—** **Istio** **configures** **and** **operates** **proxies.**""",
        "sources": [
            {
                "id": "src-istio-docs",
                "title": "Istio Documentation",
                "kind": "primary",
                "url": "https://istio.io/latest/docs/",
                "access_date": DATE,
                "notes": "Official Istio documentation.",
            }
        ],
        "ledger_rows": [("ist-001", "Istio documents mesh architecture and APIs", "DOCUMENTED", "src-istio-docs")],
        "relations": {
            "system_slug": "istio",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Istio targets Kubernetes as its primary deployment environment in upstream documentation.",
                },
                {
                    "type": "integrates_with",
                    "target": "envoy",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Istio uses Envoy as the data plane proxy in standard architectures.",
                },
                {
                    "type": "integrates_with",
                    "target": "opentelemetry",
                    "evidence_tier": "INFERRED",
                    "notes": "Mesh telemetry often integrates with OpenTelemetry-class pipelines.",
                },
            ],
        },
    },
    {
        "slug": "grub",
        "title": "GRUB",
        "display_name": "GRUB (boot loader)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **GNU** **GRUB** **boot** **loader** **—** **multiboot,** **menu,** **kernel** **/** **initrd** **loading** **on** **BIOS** **/** **UEFI** **systems** (`DOCUMENTED`, GNU GRUB manual).

## Boundaries

- **Not** **Linux** **kernel** — **pre-kernel** **stage.**  
- **Not** **systemd** — **different** **lifecycle** **(PID** **1** **comes** **after** **kernel** **handoff).**""",
        "sources": [
            {
                "id": "src-grub-manual",
                "title": "GNU GRUB Manual",
                "kind": "primary",
                "url": "https://www.gnu.org/software/grub/manual/grub/html_node/",
                "access_date": DATE,
                "notes": "GRUB documentation.",
            }
        ],
        "ledger_rows": [("grb-001", "GRUB manual documents boot process and configuration", "DOCUMENTED", "src-grub-manual")],
        "relations": {
            "system_slug": "grub",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "uefi",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "GRUB supports UEFI boot paths alongside legacy BIOS in documented configurations.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "GRUB commonly loads Linux kernels and initrds on Linux distributions.",
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
