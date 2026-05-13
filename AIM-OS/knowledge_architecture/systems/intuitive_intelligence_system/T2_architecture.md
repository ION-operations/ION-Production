---
id: "intuitive_intelligence_system_T2_architecture"
system: "intuitive_intelligence_system"
component: null
level: "T2"
type: "architecture"
title: "IIS Architecture"
description: "2,000-word architecture document for Intuitive Intelligence System"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:50:00Z"
author: "aether"
status: "complete"
tags: ["iis", "core", "intuition", "learning", "t0-t6", "transitional"]
dependencies: ["intuitive_intelligence_system_T1_overview"]
related_docs: ["intuitive_intelligence_system_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# IIS – T2 Architecture (≈2000 words)

## System Overview

IIS provides an operational definition and learning loop for AI intuition. It computes an IntuitionScore for candidate actions/ideas using calibrated confidence (VIF), retrieval quality (HHNI), meta-pattern similarity (CAS/timeline), emotional salience (TCS/EST), and 4D evolution alignment (predicted vs observed). It logs features and outcomes as IntuitionTrace, learns online from labels, and is audited by CAS.

## Core Signals and Features

- **C′ (Calibrated Confidence):** VIF confidence adjusted by ECE; entropy-aware
- **RS (Retrieval Strength):** HHNI Retrieval Score or RS-lift vs baseline
- **M (Meta-Pattern Similarity):** similarity to past successful decision patterns (CAS/timeline signatures)
- **E (Emotional Salience):** AI+user resonance, breakthrough markers (from EST)
- **F (4D Evolution Alignment):** agreement between predicted vs observed state change over horizon h
- **U (Miscalibration Penalty):** |confidence − actual| or volatility over last N decisions

**Feature vector:** x = [C′, RS, M, E, F, U, bias]

## Intuition Score and Learning

- **IntuitionScore:** I(x) = w·x (linear baseline) or logistic σ(w·x)
- **Online learning:** update w by SGD on labeled outcomes (success=1, failure=0)
- **Calibration:** maintain AUC, ECE; recalibrate via Platt/Isotonic if drift
- **Drift detection:** trigger CAS alert if AUC↓ > threshold or ECE↑ > threshold

**Algorithm:**
```python
# compute features
x = features(Cprime, RS, M, E, F, U)
# score
z = np.dot(w, x)
I = 1/(1+np.exp(-z))
# decision log
trace = IntuitionTrace(x=x, I=I, decision_id=did, horizon=h)
# on label arrival (y∈{0,1})
loss = -(y*np.log(I) + (1-y)*np.log(1-I))
w = w - lr * (I - y) * x
# track auc/ece
```

**Safety:** κ-gating (VIF) always precedes; intuition never overrides abstention.

## Data Model: IntuitionTrace

```yaml
IntuitionTrace:
  version: "1.0"
  computed_at: ISO-8601
  horizon: "short|medium|long"  # 1-3 prompts, 1 day, 1 week
  decision_id: string
  action_ref: { type, id }
  features:
    Cprime: float
    RS: float
    M: float
    E: float
    F: float
    U: float
    extra: { … }
  score: float  # IntuitionScore
  feature_hash: sha256
  predicted_outcome: float
  label: { value: 0|1|null, observed_at: ISO-8601 }
  calibration_snapshot: { auc: float, ece: float, n: int }
  provenance:
    vif_witness_id: string
    context_snapshot_id: string
```

**Storage:** attach to CMC atom `ccs_metadata.intuition_trace` and include `intuition_score` + `intuition_features_hash` in VIF witness.

## 4D Evolution Predictor (v0)

**State vectors:**
- S_ai(t): capability, calibration, load, focus
- S_user(t): satisfaction, engagement, trust
- S_collab(t): velocity, alignment, cohesion

**v0 predictor:** EWMA trend + simple Bayesian update; F = cosine(predictedΔ, observedΔ). Upgrade path: ESN/RNN-lite.

## Integration Points

- **CMC:** extend CCSMetadata with IntuitionTrace
- **VIF:** add `intuition_score`, `intuition_features_hash` to witness
- **HHNI:** optional re-rank hook using I for tie-breaking; no semantic override
- **TCS/EST:** supply E via emotional salience/resonance + breakthrough detection
- **CAS:** audit AUC/ECE drift, failure modes, trigger recalibration
- **SEG:** record relations `intuitively_predicted`, `matched_prediction`, `missed_prediction`

## APIs (Internal)

- `compute_intuition(features) -> score, trace`
- `update_intuition(decision_id, label) -> updated metrics`
- `get_intuition_metrics() -> { auc, ece, drift }`

## MVP Plan

- Day 1-2: schema + logging; attach IntuitionTrace
- Day 3-4: baseline I (C′, RS, E, basic M)
- Day 5-6: labels + online logistic + AUC/ECE
- Day 7-8: 4D predictor v0 → F added
- Day 9: HHNI re-rank hook (optional)
- Day 10: CAS dashboard + alerts

## Validation

- Unit: monotonicity, serialization, hashing
- Backtest: AUC lift vs confidence-only baseline
- E2E: vague idea + high resonance elevates priority; κ respected
- Drift: synthetic shift triggers alert + re-calibration

## Risks & Mitigations

- **Overfitting:** regularization, replay splits
- **Feedback loops:** cap weight on E and tie-break only in HHNI
- **Misuse:** κ precedence; human review for critical domains
- **Latency:** compute features asynchronously; cache traces

## References

- System map: `systems/intuitive_intelligence_system/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/intuitive_intelligence_system/L0_executive.md` through `L4_complete.md`



---

## 🔗 RELATED SYSTEMS

### **Systems We Depend On**

#### **CAS**
**Relationship:** bidirectional
**Integration Point:** casIntegration
**Data Exchanged:** meta_pattern_data, cognitive_metrics, intuition_traces (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/cas/T0_executive.md`

#### **CMC**
**Relationship:** bidirectional
**Integration Point:** cmcIntegration
**Data Exchanged:** intuition_traces, learning_data, calibration_snapshots (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/cmc/T0_executive.md`

#### **HHNI**
**Relationship:** bidirectional
**Integration Point:** hhniIntegration
**Data Exchanged:** retrieval_strength, retrieval_scores, context_quality (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/hhni/T0_executive.md`

#### **TCS**
**Relationship:** bidirectional
**Integration Point:** tcsIntegration
**Data Exchanged:** emotional_salience, timeline_patterns, consciousness_data (+ 1 more)
**Security Level:** medium
**Docs:** `knowledge_architecture/systems/tcs/T0_executive.md`

#### **VIF**
**Relationship:** bidirectional
**Integration Point:** vifIntegration
**Data Exchanged:** calibrated_confidence, confidence_scores, provenance_data (+ 1 more)
**Security Level:** critical
**Docs:** `knowledge_architecture/systems/vif/T0_executive.md`


### **Systems That Depend On Us**

**Other Systems:** autonomous_research_dream, dynamic_onboarding

**Layer 1:** cmc, seg

**Layer 2:** hhni, vif

**Total Dependent Systems:** 6

**Integration Details:** See system map (`system.map.lucid.json5`) for complete integration topology.