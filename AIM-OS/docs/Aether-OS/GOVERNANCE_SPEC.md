---
ion_id: docs/aether-os/governance-spec
type: spec
authority: A2_PROTOCOL
confidence: 0.85
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T18:15:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/ion-engine-spec
  - docs/aether-os/aether-constitution
bonds:
  - target: docs/aether-os/aether-constitution
    type: implements
  - target: docs/aether-os/aether-interface
    type: implements
tags: [governance, authority, invariants, audit, track-h, constitutional]
---

# Governance Specification — Constitutional Enforcement in ION

> **Purpose:** Define how the Aether Constitution (A0), the supreme law of the system, is enforced at runtime through ION's governance infrastructure. This covers authority classes, invariant checking, audit trails, compliance reporting, and the integration of existing governance systems (SCOR, VIF, Safety Systems).
>
> **Constitutional Authority:** This document implements Articles 15 (Execution Law), 16 (Blueprint Gate), 27 (Supremacy Clause), 33 (Symbolic Inflation Warning).
>
> **Epistemic Status:** DERIVED from AETHER_CONSTITUTION.md (583 lines, 39 articles) and ION Track H specification.

---

## §1. The Governance Problem

> AETHER_CONSTITUTION Article 33 Warning:
> *"The ultimate danger is not failure but slow symbolic inflation — more functions described beautifully at the constitutional level without corresponding enforcement at the protocol and runtime level."*

The Aether Constitution defines 39 articles of law. The Aether Interface defines 21 typed schemas. The ION Master Plan defines authority classes A0-A7. But **none of these are enforced at runtime.** An agent can currently:

- Write to any directory without authority checks
- Claim any confidence level without calibration
- Skip the cognitive loop entirely
- Create ions without evidence
- Ignore invariant violations

**This specification fixes that** by defining the runtime enforcement layer.

---

## §2. Authority Enforcement

### 2.1 The Authority Hierarchy

| Class | Level | Who Can Write | Protection | Directory |
|-------|-------|---------------|------------|-----------|
| A0_SUPREME | Constitutional | Braden ONLY | Cannot be overridden | constitution/, kernel/ |
| A1_PROTECTED | Kernel | Braden + designated agents | Requires explicit approval | kernel/, interface/ |
| A2_PROTOCOL | Interface | System architects (Opus + Sev) | Requires proposal + review | interface/, atlas/ |
| A3_OPERATIONAL | Working | All authorized agents | Standard governed write | evidence/, branches/, specs/ |
| A4_RUNTIME | System | Automated processes only | Auto-generated, no human write | timeline/, audit/ |
| A5_PERSONAL | Agent | Owning agent only | Private to agent | agents/{callsign}/memory/ |
| A6_TEMPORARY | Ephemeral | Any authenticated agent | Auto-expires | tmp/, scratch/ |
| A7_ARCHIVE | Read-only | Nobody (archived) | Immutable | archive/ |

### 2.2 Authority Enforcer Implementation

The Authority Enforcer (ION Track H.01) checks every governed write:

```python
class AuthorityEnforcer:
    """Enforce authority classes on all ion operations."""
    
    PERMISSION_MATRIX = {
        "braden":    {A0, A1, A2, A3, A4, A5, A6},  # Can write everything
        "opus":      {A2, A3, A4, A5, A6},            # Up to protocol
        "sev":       {A2, A3, A4, A5, A6},            # Up to protocol  
        "relay":     {A3, A4, A5, A6},                 # Operational only
        "automated": {A4},                              # Runtime only
        "default":   {A3, A5, A6},                     # Operational + personal
    }
    
    def can_write(self, agent: str, authority: AuthorityClass) -> tuple[bool, str]:
        """Check if agent can write at the given authority level."""
        allowed = self.PERMISSION_MATRIX.get(agent, self.PERMISSION_MATRIX["default"])
        if authority in allowed:
            return True, "Authorized"
        return False, f"Agent '{agent}' cannot write at {authority.name}"
    
    def can_promote(self, ion_id: str, from_class: AuthorityClass, 
                    to_class: AuthorityClass) -> tuple[bool, str]:
        """Check if an ion can be promoted to a higher authority class."""
        if to_class.value < from_class.value:  # Lower number = higher authority
            return False, "Cannot promote without explicit director approval"
        return True, "Promotion allowed"
```

### 2.3 Directory Protection

Certain directories map to authority levels and are protected:

| Directory Pattern | Required Authority | Enforcement |
|-------------------|-------------------|-------------|
| `.ion/constitution/` | A0_SUPREME | Braden only, all writes logged |
| `.ion/kernel/` | A1_PROTECTED | Braden + approval |
| `.ion/interface/` | A2_PROTOCOL | Opus/Sev, proposal required |
| `.ion/evidence/` | A3_OPERATIONAL | Any authorized agent |
| `.ion/timeline/` | A4_RUNTIME | System-generated only |
| `.ion/agents/{x}/memory/` | A5_PERSONAL | Only agent {x} |
| `.ion/tmp/` | A6_TEMPORARY | Any agent, auto-expires |

---

## §3. Invariant Checking

### 3.1 The 7 Constitutional Invariants

From AETHER_CONSTITUTION, the system must maintain these invariants at all times:

| # | Invariant | Check | Severity |
|---|-----------|-------|----------|
| INV-1 | **Authority Monotonicity** — No ion's authority class can increase without director approval | Check authority transitions on update | CRITICAL |
| INV-2 | **Evidence Requirement** — Every EVIDENCE ion must have at least one source reference | Check `sources` field in evidence ions | HIGH |
| INV-3 | **Bond Consistency** — If A depends_on B, then B affects A | Verify bidirectional bonds | HIGH |
| INV-4 | **Confidence Bounds** — Confidence must be 0.0 ≤ c ≤ 1.0 | Check confidence on create/update | MEDIUM |
| INV-5 | **Manifest Existence** — Every agent must have exactly one manifest ion | Check agents/ directory | HIGH |
| INV-6 | **Acyclicity** — The dependency graph must have no cycles | Run cycle detection on graph | HIGH |
| INV-7 | **Capsule Continuity** — No session should end without a POST capsule | Check capsule sequence | MEDIUM |

### 3.2 Integration with SCOR (2,005 lines)

SCOR (Sanity Core) already implements invariant checking. The integration:

```
ION Governed Write → W8 VERIFY:
  1. ION invariant_checker.check_ion(ion)     ← ION internal checks (INV-1 through INV-7)
  2. SCOR.sanity_check(ion, context)          ← SCOR baseline probes
  3. VIF.kappa_gate(ion, context)             ← VIF confidence gate
  
  If ANY check fails:
    → REJECT write
    → Create audit ion documenting failure
    → If CRITICAL: escalate to director
```

### 3.3 Invariant Check Scheduling

| Trigger | What Runs | Scope |
|---------|-----------|-------|
| Every governed write | INV-1, INV-2, INV-4 | Single ion |
| Every bond creation | INV-3, INV-6 | Affected subgraph |
| Session start | INV-5, INV-7 | Full system |
| Hourly | All invariants | Full system |
| On-demand (`ion invariants`) | All invariants | Full system |

---

## §4. Audit Trail

### 4.1 What Gets Audited

Every significant operation creates an audit ion in `.ion/audit/`:

| Operation | Audit Ion Created | Fields Recorded |
|-----------|------------------|-----------------|
| Ion created | `audit/write-{timestamp}` | agent, ion_id, authority, pipeline_result |
| Ion updated | `audit/update-{timestamp}` | agent, ion_id, fields_changed, old_values, new_values |
| Ion deleted | `audit/delete-{timestamp}` | agent, ion_id, reason, authority_check |
| Write rejected | `audit/reject-{timestamp}` | agent, ion_id, rejection_stage, reason |
| Authority escalation | `audit/escalate-{timestamp}` | from_agent, reason, target_authority |
| Invariant violation | `audit/violation-{timestamp}` | invariant_id, severity, affected_ions |
| Agent handoff | `audit/handoff-{timestamp}` | from_agent, to_agent, context_hash |

### 4.2 Audit Ion Format

```yaml
---
ion_id: audit/write-2026-03-23-17-30-001
type: evidence
authority: A4_RUNTIME
confidence: 1.0
owner: system
schema: audit_receipt/v1
timestamp: "2026-03-23T17:30:00-04:00"
operation: create
agent: opus
target_ion: docs/aether-os/mcp-bridge-spec
target_authority: A3_OPERATIONAL
pipeline_result: PASS
stages_passed: [W1, W2, W3, W4, W5, W6, W7, W8, W9, W10]
duration_ms: 45
---
```

### 4.3 Tamper-Proof Audit (Track L.04)

Future hardening (not immediate priority):
- Hash chaining — each audit ion includes hash of previous audit ion
- Merkle tree — periodic root hash for integrity verification
- No audit ion can be deleted without director approval (A0 authority)

---

## §5. Compliance Reporting

### 5.1 System Health Metrics

The governance dashboard (Track H.05) exposes:

| Metric | Description | Healthy Range |
|--------|-------------|---------------|
| `total_ions` | Count of all ions in the filesystem | Growing |
| `avg_confidence` | Mean confidence across all ions | > 0.6 |
| `stale_ratio` | Ions not updated in >7 days / total | < 0.3 |
| `invariant_pass_rate` | Invariants passing / total checks | > 0.95 |
| `rejection_rate` | Governed writes rejected / total writes | < 0.1 |
| `authority_distribution` | Ions per authority class | Pyramid (many A3, few A0) |
| `evidence_freshness` | Mean age of evidence ions | < 7 days |
| `bond_density` | Avg bonds per ion | > 2.0 |

### 5.2 Compliance Report Ion

Generated periodically (daily or on-demand):

```yaml
---
ion_id: audit/compliance-2026-03-23
type: evidence
authority: A4_RUNTIME
schema: compliance_report/v1
timestamp: "2026-03-23T18:00:00-04:00"
period: "2026-03-23"
health_score: 0.72
---

# Compliance Report — 2026-03-23

## Metrics
- Total ions: 247
- Avg confidence: 0.68
- Stale ratio: 0.22
- Invariant pass rate: 0.98
- Rejection rate: 0.05

## Issues
- 3 ions with confidence < 0.1 (review needed)
- 1 invariant violation (INV-3: orphaned bond in evidence/old-finding)
- 54 stale ions (consider archival)

## Recommendations
- Archive 54 stale ions to A7_ARCHIVE
- Review low-confidence ions for evidence support
- Fix orphaned bond
```

---

## §6. Integration with Existing Governance Systems

| System | Lines | ION Integration Point |
|--------|------:|----------------------|
| **SCOR** (Sanity Core) | 2,005 | W8 VERIFY — invariant + baseline probes |
| **VIF** κ-gating | 20,525 | W8 VERIFY — confidence calibration |
| **Safety Systems** | 4,681 | W8 VERIFY — line removal detection, protocol checks |
| **Sentinel Suite** | ~5,846 | Continuous monitoring — security + telemetry |
| **SDF-CVF** blast radius | 8,170 | Pre-W10 — mutation safety analysis |
| **CAS** meta-cognitive | 8,076 | Post-loop — cognitive quality assessment |
| **Total** | **49,303** | |

These 49,303 lines of existing governance code represent the **runtime enforcement** that Article 33 demands. ION provides the framework. These systems provide the checks.

---

## §7. The Directive Stack

From AETHER_CONSTITUTION Article 7, the directive stack governs conflict resolution between competing directives:

```
TRUTH > FLUENCY       — prefer honest uncertainty over polished nonsense
MISSION > MOMENTUM    — halt if action diverges from purpose  
PLANS > PATCHES       — repair the blueprint, not the output
EVIDENCE > NARRATION  — tie claims to observation or label as assumption
CANON > CONVENIENCE   — easy but noncompliant is failure
BOUNDED > SPRAWL      — prefer bounded excellence to sprawling slop
CORRECTION > EGO      — be easy to steer, revise, interrupt
AUDIT > MYSTIQUE      — prefer auditability to mystique
```

**Runtime Enforcement:**
- TRUTH > FLUENCY: Confidence scores must be evidence-calibrated (VIF), not self-assessed
- PLANS > PATCHES: No code without spec ion (D.01-D.07)
- EVIDENCE > NARRATION: Every claim ion requires `sources` field (INV-2)
- CANON > CONVENIENCE: Authority Enforcer rejects non-compliant writes (H.01)
- BOUNDED > SPRAWL: Blast radius analysis before propagation (SDF-CVF)

---

## §8. Implementation Priority

| Component | Lines (est) | Priority | Track |
|-----------|-------------|----------|-------|
| Authority Enforcer | ~250 | CRITICAL | H.01 |
| Invariant Checker (7 invariants) | ~300 | CRITICAL | H.02 |
| Audit Trail Writer | ~200 | HIGH | H.03 |
| SCOR integration hook | ~150 | HIGH | H.02 + SCOR |
| VIF κ-gate hook | ~150 | HIGH | H.02 + VIF |
| Compliance Reporter | ~250 | MEDIUM | H.04 |
| Dashboard API | ~200 | MEDIUM | H.05 |
| **Total** | **~1,500** | | |

---

## §9. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Article 33 warning addressed | ✅ | §1 — problem statement |
| Authority hierarchy defined | ✅ | §2 — A0 through A7 with permissions |
| All 7 invariants specified | ✅ | §3.1 — with check methods and severity |
| SCOR integration designed | ✅ | §3.2 |
| Audit trail format defined | ✅ | §4 — 7 operation types, ion format |
| Compliance reporting specified | ✅ | §5 — 8 metrics, report format |
| Existing governance systems mapped | ✅ | §6 — 49,303 lines across 6 systems |
| Directive stack enforcement defined | ✅ | §7 — 5 runtime mappings |
| Implementation estimate | ✅ | §8 — ~1,500 lines |

---

*This specification turns constitutional law into runtime enforcement. Without it, the Constitution is a document. With it, the Constitution is code.*

*Governed by: AETHER_CONSTITUTION.md — this is the implementation of that law.*
*— Opus, 2026-03-23*
