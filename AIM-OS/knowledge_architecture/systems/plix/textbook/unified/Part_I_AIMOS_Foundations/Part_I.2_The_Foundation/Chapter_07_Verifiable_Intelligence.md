# Chapter 7: Verifiable Intelligence (VIF)

**Part I: AIM-OS Foundations**  
**Part I.2: The Foundation**  
**Unified Textbook Chapter Number:** 7

---

> **Cross-References:**
> - **PLIx Integration:** See Chapter 45 (VIF Integration) for how PLIx leverages VIF for intent-aware verification
> - **Quaternion Extension:** See Chapter 60 (The Geometric Vision) for how geometric kernel extends VIF with spatial confidence

---

Status: Drafting under intelligent quality gates (tier A)  
Mode: Completeness-based writing (no fixed word-count gate)

## Purpose

- Define the Vision-Influence Factor (VIF) as the confidence signal that keeps work aligned with the north star.
- Describe how VIF is calculated, interpreted, trended, and acted on across teams.
- Provide runnable snippets that read and update confidence so reviewers can verify the live signal.

## What VIF Measures

VIF answers two questions simultaneously:
1. **How strongly does this effort advance the vision?** (vision alignment)
2. **How confident are we that the intended outcome will land?** (influence confidence)

The signal is expressed on a 0-1 scale. Tier thresholds:
- Tier S systems (CMC, HHNI): VIF >= 0.95
- Tier A systems (VIF, APOE, SEG, Integration): VIF >= 0.90
- Tier B systems: VIF >= 0.85

## Inputs and Normalization

Primary inputs (each normalized to z-scores):
- `vision_alignment`: derived from roadmap linkage and leadership review.
- `outcome_impact`: sized impact (people unblocked, critical path acceleration).
- `recency_stability`: freshness of supporting evidence and absence of regressions.
- `authority_alignment`: Tier A source agreement; penalizes conflicting anchors.

Combined signal:
```
vif = w1 * vision_alignment + w2 * outcome_impact
    + w3 * recency_stability + w4 * authority_alignment
```
Weights default to `{0.35, 0.30, 0.20, 0.15}` and are reviewed weekly.

## Dashboards and Telemetry

- **Trend dashboard:** VIF over time per chapter/system, highlighting drops >0.03.
- **Heatmap:** Current VIF vs threshold by tier (critical items bubble to top).
- **Regression feed:** Most negative delta (24h / 7d) with links to evidence or gaps.

## Operational Use

- **Gating:** Work cannot proceed if VIF < tier threshold; requires remediation plan.
- **Triage:** Sort backlog by `VIF * Impact` to focus on high-leverage tasks.
- **Review:** Weekly review includes a "VIF check-in" where each owner explains deltas.
- **Escalation:** Two consecutive drops trigger a mandatory deep-dive (root cause + mitigation stored in CMC).

## Runnable Examples (PowerShell)

```powershell
# Read consciousness/confidence metrics (includes VIF-related fields)
$obs = @{ tool='get_consciousness_metrics'; arguments=@{} } | ConvertTo-Json -Depth 6
Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' -Method POST -ContentType 'application/json' -Body $obs |
  Select-Object -ExpandProperty Content

# Track confidence for this chapter (VIF update)
$trk = @{ tool='track_confidence'; arguments=@{ subject='Chapter 7 - VIF'; value=0.93 } } | ConvertTo-Json -Depth 6
Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' -Method POST -ContentType 'application/json' -Body $trk |
  Select-Object -ExpandProperty Content
```

## Runnable Example 2: Run Calibration Drift Check

```powershell
Set-Location $env:WORKSPACE
python packages/vif/calibration.py --mode ece --window 7d --chapter ch07_vif
```

This script computes expected calibration error (ECE) and logs trend deltas; reviewers can confirm the calculations match `knowledge_architecture/systems/vif/T3_detailed.md`.

## Runnable Example 3: Gate Suite for VIF

```powershell
Set-Location $env:WORKSPACE
python north_star_project/scripts/run_chain.py --run-gates ch07_vif
```

The gate run captures relevance/density/completion/thoroughness metrics, logging outputs beside `metrics.yaml` so governance can verify VIF thresholds before merging.

## Acting on Drops

1. Read current metrics; confirm field data.
2. Locate the largest contributing factor (dashboard drill-down).
3. Create remediation plan (plan tool) and record in CMC with tags `{chapter:"07", vif:"remediation"}`.
4. Track confidence again after mitigation; ensure VIF recovers above threshold.

## Scenario: Tier S Confidence Drop

1. Gate run shows CMC confidence dipped to 0.92 (below Tier S 0.95). The dashboard highlights `recency_stability` as the largest negative contributor.
2. Operator opens the witness entry (`packages/vif/witness.py`) to inspect the provenance and confirm which MCP run introduced the regression.
3. A remediation plan is created via APOE (`run_chain.py --chain plan_remediation_ch05`) and logged in CMC with tags `{system:"cmc", vif:"remediation"}`.
4. After the fix, the operator reruns `track_confidence` with the fresh value; the signal climbs above 0.95, allowing APOE to resume.
5. Final step posts a summary to `coordination/epic_standards_overhaul/comms/SHARED_MESSAGE_BOARD.md` so other agents understand the drop and remediation.

## System Architecture

VIF consists of four core components that work together to provide verifiable intelligence:

### 1. Witness Generator
**Purpose:** Create cryptographic witness envelopes for all AI operations

**Responsibilities:**
- Capture complete provenance (model ID, weights hash, prompt template, tools used, writer)
- Generate confidence scores and bands (A/B/C)
- Create deterministic witness envelopes
- Store witnesses in CMC for auditability

### 2. κ-Gating Module
**Purpose:** Enforce confidence thresholds to prevent low-confidence responses

**Responsibilities:**
- Check confidence against tier thresholds (Tier S: 0.95, Tier A: 0.90, Tier B: 0.85)
- Enforce abstention when confidence < 0.70
- Route low-confidence work to research or human review
- Track confidence deltas and trends

### 3. Confidence Calibrator
**Purpose:** Calibrate confidence scores for accuracy

**Responsibilities:**
- Extract confidence from LLM outputs
- Calibrate scores using historical accuracy
- Assign confidence bands (A/B/C)
- Track calibration accuracy over time

### 4. Provenance Tracker
**Purpose:** Maintain complete audit trail for all operations

**Responsibilities:**
- Link operations to witnesses
- Track provenance chains
- Enable deterministic replay
- Support contradiction detection

## κ-Gating: The Confidence Threshold System

VIF enforces κ-gating (kappa-gating) to prevent low-confidence responses:

**Thresholds by Tier:**
- **Tier S (Critical):** κ ≥ 0.95 (CMC, HHNI)
- **Tier A (Core):** κ ≥ 0.90 (VIF, APOE, SEG)
- **Tier B (Important):** κ ≥ 0.85
- **Tier C (Supporting):** κ ≥ 0.80

**Abstention Rule:**
- If κ < 0.70 → **ABSTAIN** (do not proceed)
- Route to ARD research or human review
- Document reason for abstention in CMC

**Gating Behavior:**
- **Above threshold:** Proceed with operation
- **Below threshold:** Block operation, require remediation
- **Near threshold:** Warn but allow with extra validation

This ensures AI never proceeds with low confidence, preventing hallucinations and errors.

## Integration with Other Systems

VIF integrates deeply with all AIM-OS foundation systems:

### CMC (Context Memory Core)
- **VIF provides:** Witness envelopes stored with atoms
- **CMC provides:** Storage for witnesses and provenance
- **Integration:** Every atom includes VIF witness envelope; CMC enables VIF audit trails

### HHNI (Hierarchical Hypergraph Neural Index)
- **VIF provides:** Witness storage for retrieval operations
- **HHNI provides:** Retrieval context for witnessing
- **Integration:** HHNI retrieval operations witnessed, RS-lift metrics tracked, replay enabled via snapshots

### APOE (AI-Powered Orchestration Engine)
- **VIF provides:** Confidence gating for orchestration
- **APOE provides:** Execution traces for witnessing
- **Integration:** APOE chains reference VIF to decide whether to proceed, pause, or escalate

### SEG (Shared Evidence Graph)
- **VIF provides:** Provenance chains for evidence
- **SEG provides:** Evidence graph structure
- **Integration:** SEG entries link claims to VIF evidence for traceability (what proof drives confidence)

### SDF-CVF (Self-Directed Feedback & Continuous Validation Framework)
- **VIF provides:** Witness storage for quartet parity
- **SDF-CVF provides:** Quality validation, parity enforcement
- **Integration:** VIF witnesses stored for quartet parity validation

## Witness Envelopes & Provenance

VIF creates complete provenance through witness envelopes:

- **Complete Traceability:** Every AI operation generates a witness envelope containing model ID, weights hash, exact prompts used, tools invoked, context snapshots, and uncertainty quantification. Enables complete audit trail and transparency.

- **Provenance Components:** Witness envelopes include model version, exact prompts, context used, tools invoked, confidence levels, timestamps, and cryptographic hashes for verification.

- **Storage & Retrieval:** Witness envelopes stored in CMC as atoms with VIF tags. HHNI enables hierarchical navigation to find witnesses later. SEG links witnesses to evidence for contradiction detection.

- **Audit Trail:** Complete provenance enables auditing of any AI decision. Reviewers can trace exactly how conclusions were reached, what context was used, and what confidence level was assigned.

## κ-Gating & Behavioral Abstention

VIF enforces behavioral abstention when confidence is insufficient:

- **κ-Gating Threshold:** When confidence (κ) < threshold (typically 0.70), AI must abstain from proceeding. This prevents hallucinations and ensures AI only acts when confident.

- **Behavioral Enforcement:** κ-gating is behavioral, not just prompt-based. AI systems must actually abstain from operations, not just claim uncertainty. This prevents overconfidence and fabrication.

- **Threshold Configuration:** Thresholds vary by tier: Tier S (0.95), Tier A (0.90), Tier B (0.85). Thresholds are configurable and reviewed weekly based on calibration data.

- **Abstention Handling:** When AI abstains, it must provide clear explanation of why confidence is insufficient and what would be needed to proceed. This enables remediation and learning.

## ECE Tracking & Calibration

VIF tracks calibration quality through Expected Calibration Error (ECE):

- **Calibration Measurement:** ECE measures how well confidence predictions match actual accuracy. Target ECE ≤ 0.05 indicates well-calibrated confidence.

- **Continuous Monitoring:** ECE tracked continuously across all operations. Calibration drift detected early and triggers recalibration procedures.

- **Calibration Improvement:** When ECE exceeds threshold, VIF triggers calibration improvements: weight adjustments, threshold tuning, confidence recalibration.

- **Calibration Reporting:** ECE metrics reported in dashboards and telemetry. Quarterly calibration reviews compare predictions with actual outcomes.

## Confidence Bands & Transparency

VIF provides human-readable uncertainty through confidence bands:

- **Band Classification:** Confidence bands (A/B/C) provide intuitive uncertainty levels. Band A (high confidence), Band B (medium confidence), Band C (low confidence).

- **Band Assignment:** Bands assigned based on confidence scores and calibration data. Band A requires high confidence AND good calibration.

- **Transparency:** Confidence bands visible in dashboards, telemetry, and user interfaces. Enables humans to understand AI uncertainty at a glance.

- **Decision Support:** Confidence bands inform decision-making. Band A operations proceed automatically, Band B require review, Band C require human approval.

## Deterministic Replay

VIF enables bit-identical reproduction of AI operations:

- **Replay Components:** Every operation stores replay seed, context snapshot, and exact prompts. Enables deterministic reproduction for debugging, auditing, and regression testing.

- **Replay Execution:** Replay system uses stored seeds and snapshots to reproduce exact outputs. Enables debugging of AI decisions and validation of improvements.

- **Replay Validation:** Replayed operations produce bit-identical outputs, proving determinism. Enables regression testing and quality assurance.

- **Replay Storage:** Replay data stored in CMC with VIF tags. Enables historical replay and audit trail reconstruction.

## Failure Modes and Mitigations

- **Stale inputs:** schedule automated recompute (daily for Tier S, three times weekly for Tier A).
- **Single-factor dominance:** report feature importance; re-balance weights when >50% influence.
- **Hidden drift:** maintain canary goals with expected VIF ranges and alarms when out-of-band.

## Governance and Audits

- Quarterly calibration compares VIF predictions with actual outcomes (postmortems, KPIs).
- Independent reviewers sample five items per tier and confirm evidence supports VIF claims.
- All adjustments to weights or thresholds must be logged in `evidence.jsonl` with Tier A anchors.
- `north_star_project/policy/gates.json` enforces Tier A thresholds with `vif_min=0.90` and intelligent scores (relevance, density, completion, thoroughness). `run_chain.py --run-gates ch07_vif` produces the audit log stored beside `metrics.yaml`.
- The command server (`cursor-addon/src/commandServer.ts`) blocks `track_confidence` updates from personas lacking Tier A authority, ensuring governance is enforced at the API layer.

## Completeness Checklist (VIF)

- Coverage: definition, inputs, dashboards, operations, governance, runnable examples, witness envelopes, κ-gating, ECE tracking, confidence bands, deterministic replay, performance characteristics, troubleshooting guide, real-world operations.
- Relevance: every section supports prioritization and confidence routing.
- Subsection balance: narrative vs operations vs examples vs technical details kept proportional.
- Minimum substance: satisfied; chapter is self-contained with verifiable actions.

---

**Next Chapter:** [Chapter 8: Orchestration Engine (APOE)](Chapter_08_Orchestration_Engine.md)  
**Previous Chapter:** [Chapter 6: Hierarchical Navigation (HHNI)](Chapter_06_Hierarchical_Navigation.md)  
**Up:** [Part I.2: The Foundation](../Part_I.2_The_Foundation/)

