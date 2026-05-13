# AIM-OS Package Manifest
# Generated: 2026-03-10 by Opus (COO)
# This file documents the AIM-OS package structure for autonomous operations.

## Core Runtime Packages (ESSENTIAL)
| Package | Type | Description |
|---------|------|-------------|
| agent | Python | Agent workforce system — genome loader, swarm contracts |
| ai_collaboration | Python | Multi-agent collaboration framework |
| aimos-sdk | TypeScript | AIM-OS software development kit |
| apoe | Python | Autonomous Protocol Orchestration Engine |
| apoe_runner | Python | APOE execution runtime |
| autonomous_protocol | Python | Autonomous operation protocol |
| browser-automation-service | TypeScript | Browser control, credential vault, automation |
| cas | Python | Consciousness Awareness System |
| cmc_service | Python | Context Memory Core — bitemporal memory |
| context_bootloader | Python | Session context initialization |
| deepsearch | Python | Deep research and investigation |
| hhni | Python | Holographic Hierarchical Neural Index — semantic search |
| integration_tests | Python | Cross-package integration tests |

## AI Engine Packages
| Package | Type | Description |
|---------|------|-------------|
| consciousness_analyzer | Python | Consciousness pattern analysis |
| consciousness_creativity_engine | Python | Creative reasoning engine |
| consciousness_error_learning | Python | Error analysis and learning |
| consciousness_learning_engine | Python | Learning pattern optimization |
| consciousness_optimization_detector | Python | System optimization detection |

## IDE & UI Packages
| Package | Type | Description |
|---------|------|-------------|
| advanced_monaco_editor | TypeScript | Enhanced Monaco code editor |
| ide_chat_app | TypeScript | IDE chat interface |

## Infrastructure
| Package | Type | Description |
|---------|------|-------------|
| api_service_registry | Python | Service discovery and registration |
| capability_awareness | Python | Agent capability detection |
| igodn | Python | Inter-agent graph discovery network |
| icip_search | Python | Indexed content pattern search |

## Key Files (Root Level)
| File | Purpose |
|------|---------|
| lucid_mcp_server.py | Main MCP server — 92+ tools |
| server.py | Bridge server — port 9090, ghost comms |
| scripts/vault.py | Credential vault (encrypted) |
| scripts/mcp_http_fallback_server.py | HTTP MCP bridge — port 5001 |
| scripts/mcp_bridge.py | MCP transport bridge |
| scripts/agent_comms/comms_cli.py | Agent filesystem comms CLI |

## Git Rules
- NO binary files (.docx, .pdf, .pptx, media, model weights)
- NO node_modules
- NO build artifacts
- NO credentials/secrets
- Documentation kept as markdown only
- Large reference docs stored locally, not tracked
