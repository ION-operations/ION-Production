#!/usr/bin/env python3
"""Mesh depth, eBPF dataplane, and boot/UKI grain for ATLAS (2026-04-05)."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-05"

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
        "slug": "linkerd",
        "title": "Linkerd",
        "display_name": "Linkerd (service mesh)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** Lightweight Kubernetes-native **service mesh** with its own **data-plane proxy** (not Envoy-centric in Linkerd2 architecture) (`DOCUMENTED`, Linkerd docs).

## Boundaries

- Not Kubernetes itself — cluster add-on.
- Not Istio — different control plane and proxy; see `competes_with` edge to `istio`.""",
        "sources": [
            {
                "id": "src-linkerd-docs",
                "title": "Linkerd Documentation",
                "kind": "primary",
                "url": "https://linkerd.io/2-edge/overview/",
                "access_date": DATE,
                "notes": "Official Linkerd overview and architecture.",
            }
        ],
        "ledger_rows": [("lnk-001", "Linkerd documents mesh architecture for Kubernetes", "DOCUMENTED", "src-linkerd-docs")],
        "relations": {
            "system_slug": "linkerd",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Linkerd targets Kubernetes as primary deployment in upstream documentation.",
                },
                {
                    "type": "competes_with",
                    "target": "istio",
                    "evidence_tier": "INFERRED",
                    "notes": "Substitutable service-mesh class on Kubernetes in many deployments.",
                },
                {
                    "type": "integrates_with",
                    "target": "opentelemetry",
                    "evidence_tier": "INFERRED",
                    "notes": "Mesh telemetry often feeds OTel-class pipelines.",
                },
            ],
        },
    },
    {
        "slug": "cilium",
        "title": "Cilium",
        "display_name": "Cilium (eBPF networking / mesh)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane", "distributed-system"],
        "identity_md": """**Kind:** **Linux** networking and security using **eBPF**, commonly as **Kubernetes CNI** with optional **Gateway** / **mesh** features (`DOCUMENTED`, Cilium docs).

## Boundaries

- Not a pure L7-only sidecar mesh clone of Istio — different dataplane (eBPF + optional Envoy where documented).
- Not the Linux kernel — builds on `linux-kernel` and `ebpf`.""",
        "sources": [
            {
                "id": "src-cilium-docs",
                "title": "Cilium Documentation",
                "kind": "primary",
                "url": "https://docs.cilium.io/",
                "access_date": DATE,
                "notes": "Official Cilium documentation.",
            }
        ],
        "ledger_rows": [("cil-001", "Cilium documents eBPF-based networking and Kubernetes integration", "DOCUMENTED", "src-cilium-docs")],
        "relations": {
            "system_slug": "cilium",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Cilium is widely documented as a Kubernetes CNI and platform component.",
                },
                {
                    "type": "integrates_with",
                    "target": "ebpf",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Cilium's design centers on eBPF programs for datapath.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "eBPF execution requires a capable Linux kernel.",
                },
                {
                    "type": "integrates_with",
                    "target": "envoy",
                    "evidence_tier": "INFERRED",
                    "notes": "Some Cilium features integrate Envoy where documented for L7 policy / ingress.",
                },
                {
                    "type": "competes_with",
                    "target": "istio",
                    "evidence_tier": "INFERRED",
                    "notes": "Overlapping service connectivity / mesh problem space; not identical architectures.",
                },
            ],
        },
    },
    {
        "slug": "systemd-boot",
        "title": "systemd-boot",
        "display_name": "systemd-boot (UEFI boot loader)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **Minimal UEFI boot loader** from the systemd project — **stub** loading kernels and UKI images where configured (`DOCUMENTED`, systemd-boot docs).

## Boundaries

- Not GRUB — simpler menu/stub model; see `competes_with` to `grub`.
- Not the Linux kernel — runs in firmware context before kernel handoff.""",
        "sources": [
            {
                "id": "src-systemd-boot",
                "title": "systemd-boot documentation",
                "kind": "primary",
                "url": "https://www.freedesktop.org/software/systemd/man/systemd-boot.html",
                "access_date": DATE,
                "notes": "systemd-boot manual (freedesktop).",
            }
        ],
        "ledger_rows": [("sdb-001", "systemd-boot documented as UEFI boot loader", "DOCUMENTED", "src-systemd-boot")],
        "relations": {
            "system_slug": "systemd-boot",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "uefi",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "systemd-boot is a UEFI boot loader.",
                },
                {
                    "type": "competes_with",
                    "target": "grub",
                    "evidence_tier": "INFERRED",
                    "notes": "Alternative boot loader on many Linux distributions.",
                },
                {
                    "type": "integrates_with",
                    "target": "systemd",
                    "evidence_tier": "INFERRED",
                    "notes": "Same project family; init system typically follows loader on systemd-based OS images.",
                },
            ],
        },
    },
    {
        "slug": "unified-kernel-image",
        "title": "Unified Kernel Image (UKI)",
        "display_name": "Unified Kernel Image (UKI)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **Combined boot artifact** — **PE**/**EFI** **stub** packaging **kernel**, **initrd**, and **cmdline** for **measured**/**direct** UEFI boot (`DOCUMENTED`, systemd ukify / UKI docs).

## Boundaries

- Not generic GRUB configuration syntax — artifact format and tooling (e.g. `ukify`) per systemd docs.
- Not TPM2 logic alone — may interact with `tpm2` / firmware for measured boot (pin per deployment).""",
        "sources": [
            {
                "id": "src-systemd-ukify",
                "title": "systemd ukify and UKI",
                "kind": "primary",
                "url": "https://www.freedesktop.org/software/systemd/man/systemd.ukify.html",
                "access_date": DATE,
                "notes": "ukify — UKI construction tool.",
            },
            {
                "id": "src-systemd-uki",
                "title": "Unified Kernel Images (systemd docs)",
                "kind": "primary",
                "url": "https://uapi-group.org/specifications/specs/unified_kernel_image/",
                "access_date": DATE,
                "notes": "UAPI Group UKI specification (cross-check with distro tooling).",
            },
        ],
        "ledger_rows": [
            ("uki-001", "systemd documents ukify for building UKIs", "DOCUMENTED", "src-systemd-ukify"),
            ("uki-002", "UAPI Group publishes UKI specification", "DOCUMENTED", "src-systemd-uki"),
        ],
        "relations": {
            "system_slug": "unified-kernel-image",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "uefi",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "UKI is consumed by UEFI firmware as a bootable PE/EFI artifact.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "UKI bundles the Linux kernel image in standard UKI constructions.",
                },
                {
                    "type": "integrates_with",
                    "target": "systemd",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "ukify and UKI workflow are documented in the systemd project.",
                },
                {
                    "type": "integrates_with",
                    "target": "systemd-boot",
                    "evidence_tier": "INFERRED",
                    "notes": "systemd-boot commonly loads UKIs on systemd-centric distributions.",
                },
                {
                    "type": "integrates_with",
                    "target": "tpm2",
                    "evidence_tier": "INFERRED",
                    "notes": "Measured boot / PCR policies may use UKI with TPM2 (deployment-specific).",
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
