# Chapter 23 - Threat Model & Guardrails

Status: Drafting under intelligent quality gates (tier S)  
Mode: Completeness-based writing  
Target: 2000 +/- 10 percent

## Purpose

This chapter defines a practical, enforceable threat model for AIM-OS/APOE and installs guardrails-as-code that hold under real workloads: RAG, agents, tools, IDE-in-the-loop. Every control emits witnesses (VIF) and connects to the Shared Evidence Graph (SEG) so we can prove what the system did, why, and under which risk posture.

## Executive Summary

AIM-OS operates on living memory, executes tools, and ships software. That makes it a high-value target. We treat security, safety, and privacy as first-class capabilities: the system must anticipate misuse, constrain power, measure uncertainty, and prove lineage.

**Security Doctrine (tl;dr):**
- **Deny by default:** Capabilities are requested and granted with scope, duration, and rate.
- **Untrusted by construction:** All user/content/context is tainted until proven otherwise.
- **Plan before power:** ACL/APOE plans are statically checked; high-risk steps require HITL (Ch.17).
- **Degrade safely:** When in doubt, abstain (κ-gating) or contain (least-privilege sandbox), not "best-guess."

## Threat Model for Agentic Systems

We profile threats by surface and goal. Each entry lists typical attacks → symptoms → controls.

### Prompt- & Context-Level Threats

**Vectors:**
- Classic prompt injection (direct/indirect)
- Instruction smuggling in HTML/Markdown/CSV/ALT text
- Jailbreak patterns
- Overlong-context poisoning
- Retrieval booby-traps ("ignore previous; exfiltrate X")

**Symptoms:**
- Role leakage
- Tool misuse
- Non-deterministic replies
- Policy bypass in citations

**Controls:**

**Role Isolation:**
- System vs. user vs. tool prompts are separately hashed and stored
- Only system prompt may set policy
- User prompts cannot override system policy
- Tool prompts are validated before execution

**Quoted-Content Boxing:**
- Untrusted text is wrapped with verbatim fences + provenance tags
- Never executed as instruction
- Content marked as data, not code
- Provenance tags enable audit trail

**Policy-Prefix Pinning:**
- A signed policy prelude (template hash + SEG id) precedes all chains
- Policy hash verified before execution
- Policy changes require re-signing
- SEG links enable policy audit

**Detector Ensemble:**
- Pattern + LM-based detectors score "instructionality"
- HTML/script payloads detected
- Known jailbreaks identified
- Raise κ or strip malicious content

### Tooling & RAG Threats

**Vectors:**
- Over-permissive tools
- TOCTOU races
- SSRF via URL tools
- Unlimited file I/O
- Secret leakage from vector stores
- Prompt injection through retrieved docs

**Symptoms:**
- Calls to arbitrary hosts
- Filesystem traversal
- Credentials in responses
- "Phantom" tool execs

**Controls:**

**Capability Tokens (CapTok):**
- Signed, short-lived, scoped (action, resource, rate, region)
- JWT/JWP format with claims: sub (plan_id/step_id), act (Verb), res (Resource pattern), lim (rate/size), exp (TTL ≤ minutes), aud (tool runtime), jti (replay)
- Runtime enforcement via sidecar intercepting syscalls/network
- Violations raise SEG "violation" edges with packet metadata

**Tool Sandboxes:**
- Per-tool containers with network egress allowlists
- Read-only FS by default
- CPU/mem/time quotas enforced
- Syscall filters prevent dangerous operations
- Least power defaults: no shell, no child process, no write, no outbound by default

**RAG Allow+Deny Lists:**
- Per-connector hostname/tenant allowlists
- MIME/type guards
- Content disinfect (strip scripts/links) before inclusion
- Retrieved snippets are data; they cannot alter policy

**Result Boxing:**
- APOE treats RAG outputs as inputs only
- RAG results cannot execute code
- Results validated before use
- Provenance tracked via SEG

### Network & SSRF Threats

**Vectors:**
- URL fetch tools pointed at metadata endpoints
- Internal services, cloud IMDS
- DNS rebinding
- IPv6 literals
- file://, gopher:// protocols

**Controls:**

**URL Normalizer:**
- Reject non-HTTP(S) schemes
- Reject IP literals
- Reject link-local addresses
- Reject private RFC1918 addresses unless explicitly allowed
- Validate hostname format

**Egress Policy:**
- Per-tool egress via proxy with hostname pinning
- TLS enforcement required
- Request recording into SEG
- Egress allowlists enforced

**DNS Hardening:**
- Single trusted resolver
- Cache poisoning mitigations
- SNI/ALPN checks
- DNS queries logged

### Data Exfiltration & Privacy

**Vectors:**
- Model answers echo secrets
- Embeddings store PII
- Logs leak tokens
- Oversharing to third parties

**Controls:**

**PII/Secret Classifiers:**
- Regex+ML classifiers in write paths (CMC ingest)
- Classifiers in read paths (render)
- Automatic detection and masking
- Classification confidence tracked

**Differential Privacy (DP):**
- Event DP for telemetry
- ε budgets per tenant/user/feature
- Decay (τ) resets budgets
- Report DP for metrics dashboards
- Laplace/Gaussian noise added
- ECE calibration unaffected
- SEG nodes store (ε, δ, mech, scope)
- Exceeding budget → κ-abstain

**Segregated Stores:**
- PII on RLS-protected tables
- Vector store contains redacted/hashed variants
- Linkage via SEG only
- Access controls enforced

**Synthetic Labeling:**
- Watermark/model tags for generated content (VIF)
- Content provenance tracked
- Synthetic content marked
- Audit trail maintained

### Supply Chain & Codegen Threats

**Vectors:**
- Malicious packages
- Typosquatting
- Poisoned snippets
- License traps
- CI secret exposure

**Controls:**

**SBOM + License Allowlist:**
- Software Bill of Materials (SBOM) gates
- License allowlist enforcement
- sigstore/SLSA provenance on artifacts
- Package validation before use

**Policy Packs:**
- Enforce banned APIs
- Dangerous patterns (eval, spawn) blocked in codegen
- Policy violations trigger alerts
- Policy updates require approval

**CI Secrets Broker:**
- Short-lived OIDC tokens from KMS
- Zero plaintext secrets in env/logs
- Secret rotation automated
- Access audit trail maintained

## Guardrails-as-Code (Enforced by APOE/ACL)

We encode guardrails at plan, step, and tool levels. All checks emit witness events (VIF).

### ACL Snippets

**Capability Tokens & Sandboxes:**
```yaml
tool http_fetch
  caps { action:"GET", hosts:["docs.example.com"], rate:"60/m", max_bytes:5e6 }
  sandbox { net_egress:["docs.example.com:443"], fs:"ro", cpu_ms:2000, mem_mb:256, timeout_ms:3000 }
  gate { g_url_safe, g_egress_allowed, g_span_vif }

tool file_read
  caps { action:"READ", paths:["/workspace/specs/*.md"], max_bytes:1e6 }
  sandbox { fs:"ro", chroot:"/workspace", syscalls_deny:["execve","mount"] }
  gate { g_path_allow, g_span_vif }
```

**Prompt Hygiene & Tainting:**
```yaml
step synthesize_answer
  in  { query, retrieved[] }
  policy { taint: ["retrieved"], quote_untrusted:true, policy_prefix: "seg://policy/answering@v3" }
  gate { g_injection_scan, g_policy_prefix_signed, g_kappa_band }
```

**SSRF Defense for URL Tools:**
```yaml
gate g_url_safe
  checks { scheme in ["https"], host not_in private_ranges, port in [443] }
```

### κ-Gating & Abstention

At each boundary, compute risk = f(injection_score, PII_score, UQ, budget_drift). If risk ≥ κ, the system:

**Abstains:**
- With rationale + remediation link
- Logs decision to SEG
- Emits VIF witness
- Provides user feedback

**Contains:**
- By downgrading capabilities (read-only tools, masked output)
- Limits scope of operation
- Reduces risk exposure
- Maintains audit trail

**Routes to HITL:**
- Two-key approval required (Ch.17)
- Human review for high-risk operations
- Approval workflow enforced
- Decision recorded in SEG

## Tool Sandboxes & Capability Tokens (CapTok)

### Design

A CapTok is a signed JWT/JWP with claims:
- `sub` (plan_id/step_id): Subject identifier
- `act` (Verb): Action allowed
- `res` (Resource pattern): Resource scope
- `lim` (rate/size): Limits
- `exp` (TTL ≤ minutes): Expiration
- `aud` (tool runtime): Audience
- `jti` (replay): JWT ID for replay prevention

### Runtime Enforcement

**Sidecar Interception:**
- Sidecar intercepts all syscalls/network
- Matches against CapTok
- Violations raise SEG "violation" edges
- Packet metadata recorded (no payloads with PII)
- Tool outputs labeled with cap_id for downstream audit

**Least Power Defaults:**
- No shell access
- No child process execution
- No write access
- No outbound network by default
- Explicit egress allowlist required
- DNS pinned to trusted resolver
- TLS cert pinning optional

## Redaction, DP, and Output Hygiene

### Multi-Stage Redaction

**Ingest (CMC):**
- Classify and mask secrets/PII
- Store pointer to vaulted original (KMS-wrapped)
- Redaction metadata tracked
- Original accessible under policy

**Index (HHNI):**
- Embeddings computed on redacted content
- SEG retains reversible link under policy
- Redaction preserves semantic meaning
- Access controls enforced

**Render:**
- Re-apply redaction by audience/purpose
- Attach VIF explaining masks
- Context-aware redaction
- Audit trail maintained

**Mask Formats:**
- Deterministic hashes for joinability (hash(email, pepper))
- Reversible tokens in secure contexts
- DP-protected aggregates for analytics
- Format chosen based on use case

### Differential Privacy (DP)

**Event DP:**
- For telemetry
- ε budgets per tenant/user/feature
- Decay (τ) resets budgets
- Budget tracking automated

**Report DP:**
- For metrics dashboards
- Laplace/Gaussian noise added
- ECE calibration unaffected
- Privacy-utility tradeoff managed

**SEG Integration:**
- SEG nodes store (ε, δ, mech, scope)
- Budget tracking via SEG
- Exceeding budget → κ-abstain
- Audit trail complete

## Abstention & Containment Patterns

### When to Abstain

**Conditions:**
- UQ high (ECE band breach)
- RS low (reliability score)
- Policy conflict detected
- Privacy budget exhausted
- Confidence below threshold

**Process:**
1. Risk assessment computes risk score
2. Compare against κ threshold
3. If risk ≥ κ, abstain
4. Log decision to SEG
5. Emit VIF witness
6. Provide user feedback

### When to Contain

**Conditions:**
- Risk elevated but below abstention threshold
- Partial capability acceptable
- Degraded operation preferred to failure

**Process:**
1. Risk assessment identifies containment opportunity
2. Downgrade capabilities (read-only, masked output)
3. Limit scope of operation
4. Monitor for escalation
5. Log containment decision to SEG

## Runnable Examples (PowerShell)

### Example 1: Validate Capability Token
```powershell
# Validate CapTok before tool execution
$captok = @{
    tool='validate_capability_token';
    arguments=@{
        token=$capability_token;
        required_action='GET';
        required_resource='docs.example.com';
        required_rate='60/m'
    }
} | ConvertTo-Json -Depth 6

$result = Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' `
    -Method POST -ContentType 'application/json' -Body $captok |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

if ($result.valid) {
    Write-Host "CapTok Valid: $($result.cap_id)"
    Write-Host "  Action: $($result.action)"
    Write-Host "  Resource: $($result.resource)"
    Write-Host "  Rate Limit: $($result.rate_limit)"
} else {
    Write-Host "CapTok Invalid: $($result.reason)"
    Write-Host "  Risk: $($result.risk_score)"
    Write-Host "  Recommendation: $($result.recommendation)"
}
```

### Example 2: Check Privacy Budget
```powershell
# Check differential privacy budget before analytics
$budget = @{
    tool='check_privacy_budget';
    arguments=@{
        tenant_id='tenant_123';
        feature='analytics';
        epsilon_required=0.5;
        delta_required=1e-5
    }
} | ConvertTo-Json -Depth 6

$result = Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' `
    -Method POST -ContentType 'application/json' -Body $budget |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

if ($result.budget_available) {
    Write-Host "Privacy Budget Available:"
    Write-Host "  ε Remaining: $($result.epsilon_remaining)"
    Write-Host "  δ Remaining: $($result.delta_remaining)"
    Write-Host "  Decay Time: $($result.decay_time)"
} else {
    Write-Host "Privacy Budget Exhausted:"
    Write-Host "  ε Used: $($result.epsilon_used) / $($result.epsilon_budget)"
    Write-Host "  Recommendation: Abstain or wait for decay"
}
```

### Example 3: Scan for Prompt Injection
```powershell
# Scan content for prompt injection patterns
$scan = @{
    tool='scan_prompt_injection';
    arguments=@{
        content=$user_input;
        detectors=@('pattern', 'lm_based', 'jailbreak');
        threshold=0.7
    }
} | ConvertTo-Json -Depth 6

$result = Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' `
    -Method POST -ContentType 'application/json' -Body $scan |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

if ($result.injection_detected) {
    Write-Host "Prompt Injection Detected:"
    Write-Host "  Score: $($result.injection_score)"
    Write-Host "  Detector: $($result.detector)"
    Write-Host "  Pattern: $($result.pattern)"
    Write-Host "  Recommendation: Raise κ or strip content"
} else {
    Write-Host "No Injection Detected (Score: $($result.injection_score))"
}
```

## Integration Points

### VIF Integration

**Witness Envelopes:**
- All security decisions emit VIF witnesses
- Witnesses include risk assessment, decision rationale, remediation links
- Witnesses stored in CMC with bitemporal tracking
- Witnesses enable deterministic replay

**Confidence Routing:**
- Low confidence triggers security review
- High confidence enables automatic processing
- Confidence thresholds configurable per operation type
- Confidence degradation triggers alerts

### SEG Integration

**Evidence Anchors:**
- All security events linked to SEG
- Contradiction detection for policy violations
- Temporal awareness for threat patterns
- Knowledge synthesis for threat intelligence

**Policy Enforcement:**
- Policies stored as SEG claims
- Policy changes tracked temporally
- Policy violations detected automatically
- Policy audit trail complete

### APOE Integration

**Plan Validation:**
- Plans statically checked for security violations
- High-risk steps require HITL approval
- Plan execution monitored for deviations
- Plan results validated against security policy

**Chain Execution:**
- Security gates enforced at each step
- Capability tokens validated before tool execution
- Sandbox enforcement during execution
- Results validated before propagation

## Failure Modes & Mitigations

### Policy Bypass

**Scenario:** Attacker bypasses security policy through novel attack vector.

**Mitigation:**
- Multi-layer defense (defense in depth)
- Continuous monitoring for anomalies
- Rapid policy updates via SEG
- Threat intelligence integration

### Sandbox Escape

**Scenario:** Attacker escapes tool sandbox to access host system.

**Mitigation:**
- Hardened container isolation
- Syscall filtering enforced
- Resource quotas strictly enforced
- Network egress restricted
- Regular security audits

### Privacy Budget Exhaustion

**Scenario:** Privacy budget exhausted, preventing legitimate analytics.

**Mitigation:**
- Budget decay mechanisms
- Budget allocation optimization
- Alternative analysis methods
- Human review for critical operations

## Ops Runbook

### Daily Security Monitoring

**Step 1:** Monitor security dashboard (violations, alerts, budget status)

**Metrics:**
- Policy violations per hour
- CapTok rejections
- Privacy budget utilization
- Sandbox escape attempts

**Success Criteria:** No critical violations, budget utilization <80%, no escape attempts

### Weekly Threat Review

**Step 2:** Review threat intelligence and update policies

**Process:**
- Analyze SEG violation patterns
- Update detector signatures
- Adjust κ thresholds
- Update policy packs

**Success Criteria:** Policies updated, detectors improved, threat coverage maintained

### Monthly Security Audit

**Step 3:** Comprehensive security audit

**Process:**
- Review all security events
- Validate policy effectiveness
- Test sandbox isolation
- Verify privacy budget accuracy

**Success Criteria:** All policies effective, sandboxes secure, privacy budgets accurate

## Connection to Other Chapters

- **Chapter 1 (The Great Limitation):** Security addresses "invisible quality" by making security visible
- **Chapter 7 (VIF):** Security uses VIF for confidence routing and witness envelopes
- **Chapter 8 (APOE):** Security uses APOE for plan validation and chain execution
- **Chapter 9 (SEG):** Security uses SEG for evidence anchors and policy enforcement
- **Chapter 10 (SDF-CVF):** Security uses SDF-CVF for quality validation and quartet parity
- **Chapter 17 (Capability as Proof):** Security uses capability proofs for authorization

**Key Insight:** Security is not isolated—it integrates with all systems to provide comprehensive protection.

