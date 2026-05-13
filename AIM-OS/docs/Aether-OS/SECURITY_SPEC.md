---
ion_id: docs/aether-os/security-spec
type: spec
authority: A2_PROTOCOL
confidence: 0.80
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T18:30:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/governance-spec
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
tags: [security, sentinel, scor, safety, track-l, hardening]
---

# Security Specification — ION Hardening and Protection

> **Purpose:** Define how existing security systems (Sentinel suite ~5,846 lines, SCOR 2,005 lines, Safety Systems 4,681 lines — total 12,532 lines) integrate with ION Track L (Security & Hardening). Maps authentication, encryption, sandboxing, audit hardening, and rate limiting.

---

## §1. Existing Security Systems

| System | Lines | Purpose | ION Track |
|--------|------:|---------|-----------|
| **Sentinel (11 files)** | ~5,846 | Security monitoring, telemetry, governance | L.01-L.05 |
| **SCOR** | 2,005 | Sanity core, invariant probes, manipulation detection | L.04 |
| **Safety Systems** | 4,681 | Manager AI, line removal detection, protocol | L.03 |
| **SDF-CVF** blast radius | 8,170 | Mutation safety, parity enforcement | L.05 |
| Vault (scripts) | ~200 | Secret management | L.02 |
| Security (scripts) | ~400 | Security operations | L.01 |
| **Total** | **~21,302** | | |

### Sentinel File Breakdown

| File | Lines (est) | Purpose |
|------|-------------|---------|
| sentinel.py | ~2,000 | Core security monitoring |
| sentinel_telemetry.py | ~1,200 | System telemetry |
| sentinel_nexus.py | ~1,300 | Central coordination |
| sentinel_chronicle.py | ~1,200 | Event logging |
| sentinel_phantom.py | ~1,300 | Stealth monitoring |
| sentinel_mcp_governance.py | ~850 | MCP-specific governance |
| sentinel_host_baselines.py | ~1,200 | Host baseline profiling |
| sentinel_policy_engine.py | ~600 | Policy evaluation |
| sentinel_recon.py | ~800 | Reconnaissance |
| sentinel_sessions.py | ~600 | Session monitoring |
| sentinel_wraith.py | ~1,300 | Advanced threat detection |

---

## §2. ION Security Architecture (Track L)

### L.01 — Authentication

**What exists:** Security scripts, some API key handling.
**What ION needs:**

| Auth Method | Use Case | Implementation |
|-------------|----------|---------------|
| Agent identity | Each agent has cryptographic identity | Agent manifest ion + key pair |
| API key | Programmatic MCP/API access | Key stored in vault, validated per request |
| JWT | Web UI sessions (JOC) | Standard JWT with authority class claim |
| Role mapping | Authority class enforcement | Agent manifest → authority class |

### L.02 — Ion Encryption

**What exists:** Vault.py for secret management.
**What ION needs:**

- Selective encryption: only ions marked `encrypted: true`
- Header-only mode: encrypt body, keep frontmatter readable for indexing
- Key management: master key + per-agent keys
- Transparent: governed write encrypts, ion read decrypts

### L.03 — Sandboxing

**What exists:** Safety Systems (4,681 lines) with line removal detection, protocol enforcement.
**What ION needs:**

| Isolation Type | What It Prevents | Enforcement |
|---------------|-----------------|-------------|
| Filesystem | Agent reads/writes only its own dirs + shared | Authority + directory mapping |
| Network | Automation ions can't call external APIs without approval | Allowlist per authority class |
| Resource | CPU/memory bounds per automation | cgroup-like limits |
| Scope | Agent can't modify ions outside its authority | Governed write W5 |

### L.04 — Audit Hardening

**What exists:** SCOR (2,005 lines) with baseline probes and manipulation detection.
**What ION needs:**

- Hash chaining: each audit ion includes hash of previous
- Merkle tree: periodic root hash for integrity verification
- No audit ion deletable without A0 authority
- SCOR probes run at audit write time

### L.05 — Rate Limiting

**What exists:** SDF-CVF blast radius analysis (8,170 lines).
**What ION needs:**

| Limit Type | What It Prevents | Threshold |
|-----------|-----------------|-----------|
| Ion creation rate | Runaway automation | Max 100 ions/minute per agent |
| Propagation depth | Cascade explosion | Max 10 hops per propagation |
| Events per second | Event bus flood | Max 50 events/second |
| LLM calls per minute | Token budget burn | Configurable per agent |

---

## §3. Sentinel ↔ ION Integration

The Sentinel suite becomes ION's continuous security monitor:

```
Sentinel Monitoring Loop:
  1. sentinel.py    → monitors ion filesystem for unauthorized changes
  2. sentinel_telemetry.py → collects ION health metrics
  3. sentinel_nexus.py → coordinates security alerts
  4. sentinel_phantom.py → stealth monitoring of agent behavior
  5. sentinel_policy_engine.py → evaluates ION writes against security policies

Alerts → automation ions in .ion/automation/security/
Violations → evidence ions in .ion/evidence/security/
Recovery → trigger governed write to quarantine affected ions
```

---

## §4. Implementation Priority

| Component | Lines (est) | Priority |
|-----------|-------------|----------|
| Agent authentication (manifest + keys) | ~300 | HIGH |
| Authority-based filesystem isolation | ~200 | HIGH |
| Rate limiter for governed write | ~200 | HIGH |
| Sentinel ION adapter | ~400 | MEDIUM |
| Ion encryption (selective) | ~300 | MEDIUM |
| Audit hash chaining | ~200 | MEDIUM |
| SCOR ION integration | ~200 | MEDIUM |
| **Total** | **~1,800** | |

---

## §5. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All security systems inventoried | ✅ | §1 — 21,302 lines across 6 systems |
| All Track L modules mapped | ✅ | §2 — L.01 through L.05 |
| Sentinel integration defined | ✅ | §3 |
| Implementation estimate | ✅ | §4 — ~1,800 lines |

---

*Security is not a feature to add later — it's the enforcement layer that makes governance real. Without it, constitutional law is aspirational.*

*Governed by: AETHER_CONSTITUTION.md*
*— Opus, 2026-03-23*
