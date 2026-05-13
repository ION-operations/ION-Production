#!/usr/bin/env python3
"""One-shot scaffold for ION ATLAS AI-OS expansion wave (2026-04-03)."""
from __future__ import annotations

import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ROOT / "systems"
DATE = "2026-04-03"

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

    id_body = meta["identity_md"]
    (d / "00_identity.md").write_text(
        FM.format(slug=slug, date=DATE, title=f"{title} — Identity", body=id_body), encoding="utf-8"
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

    led = meta.get("ledger_rows", [("001", "Primary sources in `sources.yaml`", "DOCUMENTED", "sources")])
    rows = "\n".join(
        f"| {slug[:3]}-{rid} | {claim} | {tier} | `{loc}` | |" for rid, claim, tier, loc in led
    )
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
        "slug": "ebpf",
        "title": "eBPF",
        "display_name": "eBPF (Linux kernel bytecode)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **Linux** **kernel** **bytecode** **VM** **and** **verifier** **for** **safe** **extensibility** **(tracing,** **networking,** **security)** (`DOCUMENTED`, Linux kernel docs + BPF docs).

## Boundaries

- **Not** **the** **whole** **Linux** **kernel** — **see** **`linux-kernel`**.  
- **Not** **a** **userspace** **language** **runtime** — **clang** **/** **libbpf** **are** **tooling.**

## Why this matters for ION

- **Primary** **pattern** **for** **in-kernel** **observability** **and** **policy** **hooks** **without** **custom** **kernel** **forks.**""",
        "sources": [
            {
                "id": "src-linux-bpf",
                "title": "Linux BPF documentation",
                "kind": "primary",
                "url": "https://docs.kernel.org/bpf/",
                "access_date": DATE,
                "notes": "Kernel eBPF subsystem documentation.",
            },
            {
                "id": "src-bpf-io",
                "title": "BPF and XDP reference (bpf.io / kernel links)",
                "kind": "secondary",
                "url": "https://ebpf.io/",
                "access_date": DATE,
                "notes": "Community hub with links to specs and projects.",
            },
        ],
        "ledger_rows": [
            ("001", "Kernel BPF documentation describes verifier and program types", "DOCUMENTED", "src-linux-bpf"),
        ],
        "relations": {
            "system_slug": "ebpf",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "eBPF programs are verified and executed by the Linux kernel BPF subsystem.",
                }
            ],
        },
    },
    {
        "slug": "onnx",
        "title": "ONNX",
        "display_name": "ONNX (Open Neural Network Exchange)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **Open** **neural** **network** **exchange** **format** **(graph** **+** **operators)** **for** **interoperable** **ML** **models** (`DOCUMENTED`, ONNX spec).

## Boundaries

- **Not** **a** **training** **framework** — **export** **/** **import** **surface.**  
- **Not** **inference** **serving** **—** **see** **`nvidia-triton-inference-server`**, **`vllm`**.""",
        "sources": [
            {
                "id": "src-onnx-spec",
                "title": "ONNX — Open Neural Network Exchange",
                "kind": "primary",
                "url": "https://onnx.ai/onnx/",
                "access_date": DATE,
                "notes": "Specification and operator reference.",
            }
        ],
        "ledger_rows": [
            ("001", "ONNX defines portable model graph and operator set", "DOCUMENTED", "src-onnx-spec"),
        ],
        "relations": {
            "system_slug": "onnx",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "llvm-ir",
                    "evidence_tier": "INFERRED",
                    "notes": "Many runtimes lower graphs through LLVM-class codegen paths (implementation-dependent).",
                },
                {
                    "type": "integrates_with",
                    "target": "nvidia-cuda",
                    "evidence_tier": "INFERRED",
                    "notes": "GPU inference stacks often consume ONNX or ONNX-derived artifacts.",
                },
            ],
        },
    },
    {
        "slug": "opentelemetry",
        "title": "OpenTelemetry",
        "display_name": "OpenTelemetry",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **CNCF** **observability** **framework** **(traces,** **metrics,** **logs)** **with** **OTLP** **wire** **formats** (`DOCUMENTED`, OpenTelemetry spec).

## Boundaries

- **Not** **a** **storage** **backend** — **exporters** **/** **collectors** **bridge** **to** **vendors.**  
- **Not** **application** **metrics** **without** **instrumentation** **—** **SDK** **layer** **is** **separate.**""",
        "sources": [
            {
                "id": "src-otel-spec",
                "title": "OpenTelemetry Specification",
                "kind": "primary",
                "url": "https://opentelemetry.io/docs/specs/otel/",
                "access_date": DATE,
                "notes": "Normative OTel specification index.",
            }
        ],
        "ledger_rows": [
            ("001", "OTLP protocol for telemetry export", "DOCUMENTED", "src-otel-spec"),
        ],
        "relations": {
            "system_slug": "opentelemetry",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "INFERRED",
                    "notes": "OTLP commonly carried over gRPC in deployments (see OTLP mapping docs).",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Kubernetes clusters commonly deploy OpenTelemetry collectors and instrumented workloads.",
                },
            ],
        },
    },
    {
        "slug": "grpc",
        "title": "gRPC",
        "display_name": "gRPC",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **RPC** **framework** **using** **HTTP/2** **framing** **and** **Protobuf** **IDL** **(service** **contracts)** (`DOCUMENTED`, gRPC docs).

## Boundaries

- **Not** **REST** **/** **OpenAPI** **—** **different** **IDL** **and** **streaming** **model.**  
- **Not** **JSON-RPC** **—** **see** **`model-context-protocol`** **for** **MCP** **message** **shape.**""",
        "sources": [
            {
                "id": "src-grpc-io",
                "title": "gRPC — A high performance RPC framework",
                "kind": "primary",
                "url": "https://grpc.io/docs/",
                "access_date": DATE,
                "notes": "Official documentation.",
            }
        ],
        "ledger_rows": [
            ("001", "gRPC uses HTTP/2 and Protobuf service definitions", "DOCUMENTED", "src-grpc-io"),
        ],
        "relations": {
            "system_slug": "grpc",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Kubernetes APIs and many cloud services expose gRPC interfaces.",
                }
            ],
        },
    },
    {
        "slug": "http3",
        "title": "HTTP/3 and QUIC",
        "display_name": "HTTP/3 (QUIC transport)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **IETF** **HTTP/3** **(RFC** **9114)** **over** **QUIC** **(RFC** **9000)** — **UDP-based** **multiplexed** **transport** **with** **TLS** **1.3** **integration** (`DOCUMENTED`, RFCs).

## Boundaries

- **Not** **HTTP/1.1** **or** **HTTP/2** **over** **TCP** — **different** **loss** **recovery** **and** **handshake** **model.**  
- **Not** **gRPC** **—** **though** **deployments** **may** **coexist** **at** **edge** **load** **balancers.**""",
        "sources": [
            {
                "id": "src-rfc9114",
                "title": "RFC 9114 — HTTP/3",
                "kind": "primary",
                "url": "https://www.rfc-editor.org/rfc/rfc9114.html",
                "access_date": DATE,
                "notes": "Normative HTTP/3.",
            },
            {
                "id": "src-rfc9000",
                "title": "RFC 9000 — QUIC",
                "kind": "primary",
                "url": "https://www.rfc-editor.org/rfc/rfc9000.html",
                "access_date": DATE,
                "notes": "QUIC transport protocol.",
            },
        ],
        "ledger_rows": [
            ("001", "HTTP/3 maps HTTP semantics to QUIC streams", "DOCUMENTED", "src-rfc9114"),
            ("002", "QUIC provides encrypted transport with connection migration", "DOCUMENTED", "src-rfc9000"),
        ],
        "relations": {
            "system_slug": "http3",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "QUIC stacks run on general-purpose OS networking; Linux hosts common in servers.",
                }
            ],
        },
    },
    {
        "slug": "amazon-s3",
        "title": "Amazon S3 API",
        "display_name": "Amazon S3 (object storage API)",
        "primary_kind": "protocol",
        "tags": ["protocol", "control-plane"],
        "identity_md": """**Kind:** **Object** **storage** **control** **plane** **/** **data** **API** **(REST,** **SigV4,** **buckets** **/** **objects)** — **de** **facto** **cloud** **reference** **for** **immutable** **blob** **stores** (`DOCUMENTED`, AWS docs).

## Boundaries

- **Not** **a** **POSIX** **filesystem** — **different** **consistency** **and** **mutation** **model.**  
- **Not** **vendor**-**neutral** **—** **S3** **is** **AWS** **product** **name;** **API** **shape** **is** **widely** **emulated.**""",
        "sources": [
            {
                "id": "src-aws-s3-api",
                "title": "Amazon S3 — API Reference",
                "kind": "primary",
                "url": "https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html",
                "access_date": DATE,
                "notes": "AWS S3 REST API reference.",
            }
        ],
        "ledger_rows": [
            ("001", "S3 exposes REST API for buckets and objects", "DOCUMENTED", "src-aws-s3-api"),
        ],
        "relations": {
            "system_slug": "amazon-s3",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Kubernetes workloads commonly use S3-compatible object stores for artifacts and models.",
                }
            ],
        },
    },
    {
        "slug": "nvidia-triton-inference-server",
        "title": "NVIDIA Triton Inference Server",
        "display_name": "NVIDIA Triton Inference Server",
        "primary_kind": "ai-runtime",
        "tags": ["protocol", "ai-runtime"],
        "identity_md": """**Kind:** **Inference** **serving** **platform** **for** **multiple** **framework** **backends** **with** **HTTP** **/** **gRPC** **APIs** (`DOCUMENTED`, NVIDIA docs).

## Boundaries

- **Not** **model** **training** — **serving** **and** **scheduling** **of** **inference** **requests.**  
- **Not** **CUDA** **toolkit** **—** **see** **`nvidia-cuda`**.""",
        "sources": [
            {
                "id": "src-triton-docs",
                "title": "NVIDIA Triton Inference Server — Documentation",
                "kind": "primary",
                "url": "https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/index.html",
                "access_date": DATE,
                "notes": "Product documentation.",
            }
        ],
        "ledger_rows": [
            ("001", "Triton documents HTTP/gRPC inference APIs", "DOCUMENTED", "src-triton-docs"),
        ],
        "relations": {
            "system_slug": "nvidia-triton-inference-server",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "grpc",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "Triton exposes gRPC inference protocol per NVIDIA documentation.",
                },
                {
                    "type": "integrates_with",
                    "target": "onnx",
                    "evidence_tier": "INFERRED",
                    "notes": "Triton commonly serves ONNX and other backend formats.",
                },
                {
                    "type": "integrates_with",
                    "target": "nvidia-cuda",
                    "evidence_tier": "INFERRED",
                    "notes": "GPU backends typically require NVIDIA CUDA stack on GPU deployments.",
                },
            ],
        },
    },
    {
        "slug": "vllm",
        "title": "vLLM",
        "display_name": "vLLM (LLM inference engine)",
        "primary_kind": "ai-runtime",
        "tags": ["ai-runtime", "protocol"],
        "identity_md": """**Kind:** **Open** **LLM** **inference** **and** **serving** **engine** **(PagedAttention,** **OpenAI**-**compatible** **API** **surface** **in** **common** **deployments)** (`DOCUMENTED`, vLLM docs).

## Boundaries

- **Not** **a** **foundation** **model** **—** **runtime** **for** **weights** **you** **provide.**  
- **Not** **vendor**-**neutral** **GPU** **stack** — **CUDA** **common** **in** **upstream** **docs.**""",
        "sources": [
            {
                "id": "src-vllm-readthedocs",
                "title": "vLLM — documentation",
                "kind": "primary",
                "url": "https://docs.vllm.ai/",
                "access_date": DATE,
                "notes": "Project documentation.",
            }
        ],
        "ledger_rows": [
            ("001", "vLLM documents inference server and Python API", "DOCUMENTED", "src-vllm-readthedocs"),
        ],
        "relations": {
            "system_slug": "vllm",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "nvidia-cuda",
                    "evidence_tier": "INFERRED",
                    "notes": "Common deployments target NVIDIA GPUs via CUDA-class stacks.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Helm/K8s deployment patterns common for serving at scale.",
                },
            ],
        },
    },
    {
        "slug": "nccl",
        "title": "NCCL",
        "display_name": "NVIDIA NCCL (collective communications)",
        "primary_kind": "gpu-compute-stack",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **NVIDIA** **library** **for** **multi**-**GPU** **collective** **communication** **(AllReduce,** **AllGather,** **…)** (`DOCUMENTED`, NCCL docs).

## Boundaries

- **Not** **a** **network** **transport** **spec** **—** **library** **API** **on** **top** **of** **PCIe** **/** **NVLink** **/** **InfiniBand** **etc.**  
- **Not** **portable** **to** **non**-**NVIDIA** **without** **alternatives** **(e.g.** **RCCL)** — **out** **of** **scope** **here.**""",
        "sources": [
            {
                "id": "src-nccl-docs",
                "title": "NVIDIA NCCL Documentation",
                "kind": "primary",
                "url": "https://docs.nvidia.com/deeplearning/nccl/",
                "access_date": DATE,
                "notes": "NCCL user guide.",
            }
        ],
        "ledger_rows": [
            ("001", "NCCL provides multi-GPU collective primitives", "DOCUMENTED", "src-nccl-docs"),
        ],
        "relations": {
            "system_slug": "nccl",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "nvidia-cuda",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "NCCL is part of NVIDIA deep learning software stack documentation.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Typical training clusters run Linux hosts with NCCL-accelerated frameworks.",
                },
            ],
        },
    },
    {
        "slug": "openid-connect",
        "title": "OpenID Connect",
        "display_name": "OpenID Connect",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **Identity** **layer** **on** **OAuth** **2.0** **—** **ID** **Tokens,** **UserInfo,** **and** **RP** **/** **OP** **roles** (`DOCUMENTED`, OpenID Connect specifications).

## Boundaries

- **Not** **OAuth** **2.0** **alone** — **OIDC** **adds** **authentication** **semantics.**  
- **Not** **Kerberos** **/** **SAML** — **different** **token** **and** **binding** **models** **(may** **coexist).**""",
        "sources": [
            {
                "id": "src-oidc-core",
                "title": "OpenID Connect Core 1.0",
                "kind": "primary",
                "url": "https://openid.net/specs/openid-connect-core-1_0.html",
                "access_date": DATE,
                "notes": "Core OIDC specification.",
            }
        ],
        "ledger_rows": [
            ("001", "OIDC Core defines ID Token and authentication flows", "DOCUMENTED", "src-oidc-core"),
        ],
        "relations": {
            "system_slug": "openid-connect",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "http3",
                    "evidence_tier": "INFERRED",
                    "notes": "Deployments may terminate OIDC/OAuth HTTP at HTTP/3-capable edges (implementation-dependent).",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Cluster auth integrations (OIDC with kube-apiserver) are common patterns.",
                },
            ],
        },
    },
    {
        "slug": "tpm2",
        "title": "TPM 2.0",
        "display_name": "TPM 2.0 (Trusted Platform Module)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **TCG** **TPM** **2.0** **—** **hardware** **/** **firmware** **rooted** **crypto** **and** **attestation** **commands** (`DOCUMENTED`, TCG library).

## Boundaries

- **Not** **a** **full** **TEE** **execution** **environment** — **see** **`confidential-computing`** **for** **broader** **survey.**  
- **Not** **UEFI** **—** **often** **composed** **with** **firmware** **boot** **(`uefi`).**""",
        "sources": [
            {
                "id": "src-tcg-tpm2",
                "title": "Trusted Computing Group — TPM 2.0 Library",
                "kind": "primary",
                "url": "https://trustedcomputinggroup.org/resource/tpm-library-specification/",
                "access_date": DATE,
                "notes": "TPM 2.0 library specification (TCG).",
            }
        ],
        "ledger_rows": [
            ("001", "TCG publishes TPM 2.0 library specification", "DOCUMENTED", "src-tcg-tpm2"),
        ],
        "relations": {
            "system_slug": "tpm2",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "uefi",
                    "evidence_tier": "INFERRED",
                    "notes": "Measured boot and firmware trust chains commonly involve TPM + UEFI-class firmware.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Linux TPM driver stack exposes TPM 2.0 to userspace (kernel-dependent).",
                },
            ],
        },
    },
    {
        "slug": "uefi",
        "title": "UEFI",
        "display_name": "UEFI (firmware interface)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **UEFI** **Forum** **firmware** **/** **boot** **interface** **specification** **successor** **to** **classic** **BIOS** **boot** **culture** (`DOCUMENTED`, UEFI spec).

## Boundaries

- **Not** **an** **OS** **kernel** — **pre-boot** **/** **firmware** **environment.**  
- **Not** **Secure** **Boot** **policy** **alone** — **often** **policy** **layered** **on** **UEFI** **+** **keys.**""",
        "sources": [
            {
                "id": "src-uefi-spec",
                "title": "UEFI Specification",
                "kind": "primary",
                "url": "https://uefi.org/specifications",
                "access_date": DATE,
                "notes": "UEFI Forum specifications index.",
            }
        ],
        "ledger_rows": [
            ("001", "UEFI Forum publishes firmware interface specifications", "DOCUMENTED", "src-uefi-spec"),
        ],
        "relations": {
            "system_slug": "uefi",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Linux boot loaders hand off from UEFI to kernel on UEFI-class machines.",
                },
                {
                    "type": "integrates_with",
                    "target": "windows-nt",
                    "evidence_tier": "INFERRED",
                    "notes": "Windows boots via UEFI on modern PCs.",
                },
            ],
        },
    },
    {
        "slug": "linux-security-modules",
        "title": "Linux Security Modules",
        "display_name": "Linux Security Modules (LSM / SELinux / AppArmor)",
        "primary_kind": "protocol",
        "tags": ["protocol", "kernel"],
        "identity_md": """**Kind:** **Linux** **kernel** **LSM** **framework** **and** **major** **implementations** **(SELinux,** **AppArmor)** **for** **mandatory** **/** **path-based** **access** **control** (`DOCUMENTED`, kernel docs + LSM).

## Boundaries

- **Not** **discretionary** **ACLs** **alone** — **MAC** **/** **policy** **languages.**  
- **Not** **containers** **—** **see** **`docker`**, **`kubernetes`** **for** **orchestration** **grain.**""",
        "sources": [
            {
                "id": "src-kernel-lsm",
                "title": "Linux Kernel — Linux Security Modules",
                "kind": "primary",
                "url": "https://docs.kernel.org/security/lsm.html",
                "access_date": DATE,
                "notes": "Kernel LSM documentation.",
            },
            {
                "id": "src-selinux-docs",
                "title": "SELinux documentation",
                "kind": "secondary",
                "url": "https://selinuxproject.org/",
                "access_date": DATE,
                "notes": "SELinux project hub.",
            },
        ],
        "ledger_rows": [
            ("001", "Kernel documents LSM hooks and stacking", "DOCUMENTED", "src-kernel-lsm"),
        ],
        "relations": {
            "system_slug": "linux-security-modules",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "DOCUMENTED",
                    "notes": "LSM is a kernel subsystem for security policy enforcement.",
                },
                {
                    "type": "integrates_with",
                    "target": "kubernetes",
                    "evidence_tier": "INFERRED",
                    "notes": "Pod security contexts and host policies interact with LSM on Linux nodes.",
                },
            ],
        },
    },
    {
        "slug": "confidential-computing",
        "title": "Confidential computing (survey)",
        "display_name": "Confidential computing (TEE survey)",
        "primary_kind": "protocol",
        "tags": ["protocol"],
        "identity_md": """**Kind:** **Survey** **grain** **for** **hardware** **/** **firmware** **assisted** **workload** **isolation** **(TEEs,** **memory** **encryption,** **attestation** **ecosystems)** — **vendor** **splits** **are** **large;** **claims** **must** **be** **tiered** (`DOCUMENTED` **where** **public** **spec** **exists,** **`UNKNOWN`** **for** **opaque** **silicon).

## Boundaries

- **Not** **a** **single** **standard** **ISA** — **Intel** **/** **AMD** **/** **ARM** **families** **differ.**  
- **Not** **cryptographic** **proof** **of** **application** **correctness** — **primarily** **isolation** **/** **attestation** **surfaces.**""",
        "sources": [
            {
                "id": "src-ccc",
                "title": "Confidential Computing Consortium",
                "kind": "secondary",
                "url": "https://confidentialcomputing.io/",
                "access_date": DATE,
                "notes": "Industry consortium overview and pointers.",
            }
        ],
        "ledger_rows": [
            ("001", "TEE ecosystems are multi-vendor; pin vendor spec per claim", "INFERRED", "src-ccc"),
        ],
        "relations": {
            "system_slug": "confidential-computing",
            "schema_version": "1.0",
            "last_reviewed": DATE,
            "edges": [
                {
                    "type": "integrates_with",
                    "target": "tpm2",
                    "evidence_tier": "INFERRED",
                    "notes": "Attestation and key storage workflows often involve TPM-class roots of trust.",
                },
                {
                    "type": "integrates_with",
                    "target": "linux-kernel",
                    "evidence_tier": "INFERRED",
                    "notes": "Linux hosts integrate confidential VM and TEE drivers on supported hardware.",
                },
            ],
        },
    },
]


def main() -> None:
    index_entries = []
    for p in PACKAGES:
        if (SYSTEMS / p["slug"]).exists():
            print("skip existing", p["slug"])
            continue
        write_pkg(p)
        index_entries.append(
            {
                "slug": p["slug"],
                "display_name": p["display_name"],
                "package_status": "seeded",
                "primary_kind": p["primary_kind"],
            }
        )
        print("wrote", p["slug"])

    if index_entries:
        print("\n--- Append to systems_index.yaml ---")
        for e in index_entries:
            print(f"  - slug: {e['slug']}")
            print(f"    display_name: \"{e['display_name']}\"")
            print(f"    package_status: seeded")
            print(f"    primary_kind: {e['primary_kind']}")


if __name__ == "__main__":
    main()
