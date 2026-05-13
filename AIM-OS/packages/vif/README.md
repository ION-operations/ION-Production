# VIF - Verifiable Intelligence Framework

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)](https://github.com/bombom/aim-os)
[![Tests](https://img.shields.io/badge/tests-153_passing-brightgreen)](./tests/)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](./tests/)
[![Quintet Parity](https://img.shields.io/badge/quintet_parity-0.92-brightgreen)](../../knowledge_architecture/systems/vif/)
[![NL Tags](https://img.shields.io/badge/nl_tags-408-blue)](../../knowledge_architecture/systems/vif/NL_TAG_CATALOG.md)

> **Verifiable Intelligence Framework** - Complete provenance, uncertainty quantification, and deterministic replay for AI operations.

---

## 🎯 What is VIF?

VIF solves the **AI trust problem**: You can't verify how an AI reached its conclusion, can't replay its reasoning, and can't quantify its uncertainty.

VIF makes every AI operation **fully traceable** through witness envelopes containing:
- Complete provenance (model ID, weights hash, exact prompts, context snapshots)
- Uncertainty quantification (confidence scores, calibration metrics)
- Deterministic replay (bit-identical reproduction of outputs)
- κ-gating (behavioral abstention when uncertain)

---

## ✨ Core Capabilities

### 1. **Complete Provenance**
Every AI operation generates a **witness envelope** with full traceability:
- Model version and weights hash
- Exact prompts and context used
- Tools invoked and outputs produced
- Confidence levels and calibration metrics
- Replay seed for deterministic reproduction

### 2. **Uncertainty Quantification**
- **κ-Gating (Behavioral Abstention):** Enforces "I don't know" when uncertain (confidence < κ_threshold)
- **ECE (Expected Calibration Error):** Tracks how well confidence matches accuracy (target: ECE ≤ 0.05)
- **Confidence Bands:** Human-readable uncertainty classification
  - **Band A (High):** 0.95-1.00 - Proceed with confidence
  - **Band B (Medium):** 0.80-0.94 - Proceed with caution
  - **Band C (Low):** <0.80 - Review carefully or abstain

### 3. **Deterministic Replay**
Bit-identical reproduction of outputs using:
- Replay seed (RNG state)
- Context snapshot (exact state)
- Exact prompts (verbatim text)

Enables debugging, auditing, and regression testing.

---

## 🚀 Quick Start

### Installation
```bash
# Install VIF package
pip install -e packages/vif

# Run tests to verify
pytest packages/vif/tests/ -v
```

### Basic Usage
```python
from vif.witness import create_witness
from vif.kappa_gate import evaluate_kappa_gate
from vif.confidence_extraction import extract_confidence

# Create a witness for an AI operation
witness = create_witness(
    model_id="gpt-4",
    prompt="What is the capital of France?",
    response="Paris",
    context_snapshot=context_data,
    confidence=0.95
)

# Evaluate κ-gating
gate_result = evaluate_kappa_gate(
    confidence=witness.confidence,
    kappa_threshold=0.70
)

if gate_result.should_proceed:
    print(f"Proceeding with confidence {witness.confidence}")
else:
    print(f"Abstaining - confidence too low ({witness.confidence} < 0.70)")
```

### Cross-Model VIF
```python
from vif.cross_model_vif import CrossModelVIF

# Create cross-model witness
cmv = CrossModelVIF()
witness = cmv.create_cross_model_witness(
    smart_model_output=analysis_result,
    execution_model_output=implementation_result,
    consensus_score=0.88
)

# Calibrate confidence across models
calibrator = CrossModelConfidenceCalibrator()
calibrated = calibrator.calibrate(
    smart_confidence=0.92,
    execution_confidence=0.85,
    consensus_score=0.88
)
```

---

## 📦 Module Overview

### Core Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `witness.py` | Witness envelope creation and validation | `create_witness()`, `validate_witness()` |
| `kappa_gate.py` | κ-gating (behavioral abstention) | `evaluate_kappa_gate()`, `should_abstain()` |
| `replay.py` | Deterministic replay | `replay_operation()`, `verify_replay()` |
| `calibration.py` | Confidence calibration and ECE tracking | `calibrate_confidence()`, `calculate_ece()` |
| `confidence_extraction.py` | Extract confidence from AI outputs | `extract_confidence()`, `parse_confidence()` |
| `confidence_bands.py` | Human-readable confidence bands | `assign_band()`, `get_band_thresholds()` |
| `cmc_integration.py` | CMC integration for witness storage | `store_witness_in_cmc()`, `retrieve_witness()`, `create_witness_and_store()` |
| `hhni_integration.py` | HHNI integration for RS-Lift metrics | `create_retrieval_witness()`, `extract_rs_lift_metrics()`, `calculate_rs_lift_statistics()` |
| `sdfcvf_integration.py` | SDF-CVF integration for quartet parity | `vif_witness_to_trace_text()`, `combine_confidence_and_parity()`, `calculate_parity_with_vif_traces()` |
| `tcs_integration.py` | TCS integration for timeline tracking | `create_witness_timeline_entry()`, `create_kappa_gate_timeline_entry()`, `query_witness_timeline()` |
| `cas_integration.py` | CAS integration for cognitive context | `extract_cognitive_context()`, `enhance_confidence_with_cognitive_state()`, `create_witness_with_cognitive_context()` |

### Cross-Model Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `cross_model_vif.py` | Cross-model witness creation | `CrossModelVIF.create_witness()` |
| `cross_model_witness_generator.py` | Generate cross-model witnesses | `generate_cross_model_witness()` |
| `cross_model_confidence_calibrator.py` | Calibrate cross-model confidence | `calibrate()`, `adjust_confidence()` |
| `cross_model_replay.py` | Cross-model deterministic replay | `replay_cross_model()`, `verify_consensus()` |

---

## 🧪 Testing

VIF has **153 passing tests** with **95% coverage**:

```bash
# Run all tests
pytest packages/vif/tests/ -v

# Run specific test suite
pytest packages/vif/tests/test_witness_schema.py -v
pytest packages/vif/tests/test_kappa_gate.py -v
pytest packages/vif/tests/test_cross_model_vif.py -v

# Run with coverage report
pytest packages/vif/tests/ --cov=packages/vif --cov-report=html
```

### Test Files
- `test_witness_schema.py` - Witness envelope validation
- `test_kappa_gate.py` - κ-gating logic
- `test_replay.py` - Deterministic replay
- `test_calibration.py` - Confidence calibration
- `test_confidence_extraction.py` - Confidence parsing
- `test_confidence_bands.py` - Band assignment
- `test_cmc_integration.py` - CMC integration
- `test_cross_model_vif.py` - Cross-model witnesses
- `test_integration_end_to_end.py` - End-to-end workflows

---

## 🔗 Integration with AIM-OS Systems

VIF integrates with all major AIM-OS systems:

### CMC (Context Memory Core)
- **Purpose:** Store VIF witnesses as atoms in CMC
- **Integration:** `cmc_integration.py` - Witness storage and retrieval
- **Flow:** Every witness stored in CMC with provenance metadata

### HHNI (Hierarchical Hypergraph Neural Index)
- **Purpose:** Retrieval context influences confidence scores
- **Integration:** VIF tracks which atoms were retrieved from HHNI
- **Flow:** HHNI retrieval → VIF witness → CMC storage

### APOE (AI-Powered Orchestration Engine)
- **Purpose:** VIF provides κ-gating hooks for APOE execution
- **Integration:** Every APOE step emits VIF witness
- **Flow:** APOE step → VIF κ-gate → If passed → Execute → Store witness

### SEG (Synthesis & Evidence Graph)
- **Purpose:** Witnesses become provenance nodes in SEG
- **Integration:** VIF enables contradiction detection via confidence tracking
- **Flow:** VIF witness → SEG node → Evidence weighting → Synthesis

### SDF-CVF (Self-Directed Feedback & Continuous Validation)
- **Purpose:** VIF witnesses required for quartet parity
- **Integration:** Quality gates use VIF confidence to enforce standards
- **Flow:** Code → Tests → Docs → Traces (VIF witnesses) → Tags

### TCS (Timeline Context System)
- **Purpose:** Track VIF witnesses and κ-gate events in timeline
- **Integration:** `tcs_integration.py` - Timeline entries for witness creation and κ-gate decisions
- **Flow:** VIF witness created → TCS timeline entry → Query witness history

### CAS (Cognitive Analysis System)
- **Purpose:** Enhance confidence with cognitive context
- **Integration:** `cas_integration.py` - Cognitive state tracking and confidence enhancement
- **Flow:** CAS activation state → VIF witness with cognitive context → Enhanced confidence scoring

---

## 📚 Documentation

VIF follows the **T0-T6 Progressive Disclosure** documentation standard:

| Level | Description | Location | Word Count |
|-------|-------------|----------|------------|
| **T0** | Executive Summary | [T0_executive.md](../../knowledge_architecture/systems/vif/T0_executive.md) | 100 words |
| **T1** | Overview | [T1_overview.md](../../knowledge_architecture/systems/vif/T1_overview.md) | 500 words |
| **T2** | Architecture | [T2_architecture.md](../../knowledge_architecture/systems/vif/T2_architecture.md) | 2,000 words |
| **T3** | Detailed Implementation | [T3_detailed.md](../../knowledge_architecture/systems/vif/T3_detailed.md) | 10,000 words |
| **T4** | Complete Reference | [T4_complete.md](../../knowledge_architecture/systems/vif/T4_complete.md) | 15,000+ words |
| **T5** | Extended Deep Dive | [T5_extended.md](../../knowledge_architecture/systems/vif/T5_extended.md) | 20,000+ words |
| **T6** | Comprehensive Archive | [T6_comprehensive.md](../../knowledge_architecture/systems/vif/T6_comprehensive.md) | 35,000+ words |

### Additional Resources
- **System Map:** [system.map.lucid.json5](../../knowledge_architecture/systems/vif/system.map.lucid.json5) - Machine-readable system definition
- **NL Tag Catalog:** [NL_TAG_CATALOG.md](../../knowledge_architecture/systems/vif/NL_TAG_CATALOG.md) - All 408 NL tags
- **Usage Examples:** [examples/](../../knowledge_architecture/systems/vif/examples/) - Real-world usage patterns
- **API Reference:** [api/](../../knowledge_architecture/systems/vif/api/) - Complete API documentation

---

## 🏗️ Architecture

### High-Level Flow

**Witness Creation Flow:**
```
AI Operation → Capture Context (CMC snapshot) → 
Capture Prompt (exact text) → Execute with Seed → 
Generate Output → Calculate Confidence → 
Assign Confidence Band → Calculate ECE → 
Create Witness Envelope → Store in CMC → 
Link to SEG → Update Calibration Metrics
```

**κ-Gating Flow:**
```
Output + Confidence → Check κ Threshold → 
If confidence < κ: ABSTAIN (escalate) → 
If confidence >= κ: PROCEED → 
Create Witness → Store Provenance
```

**Calibration Loop:**
```
Witness Created → Track Confidence → 
Measure Accuracy → Calculate ECE → 
Update Calibration Model → 
Adjust Future Confidence Estimates
```

### System Boundaries

**VIF Owns:**
- Witness envelope creation
- κ-gating evaluation
- ECE tracking
- Confidence band assignment
- Deterministic replay

**VIF Does NOT Own:**
- Model execution (wraps models, doesn't run them)
- Context storage (uses CMC)
- Retrieval (uses HHNI)
- Orchestration (provides gates to APOE)

---

## 📊 Quality Metrics

- **Test Coverage:** 95% (153 passing tests)
- **Quintet Parity:** P = 0.92 (Code + Tests + Docs + Traces + Tags)
- **NL Tag Coverage:** 408 tags across 10 files
- **Calibration Target:** ECE ≤ 0.05 (well-calibrated)
- **κ-Gate Threshold:** 0.70 (default, configurable)

---

## 🛡️ Must-Never Constraints

VIF enforces the following **must-never** constraints (critical for correctness):

1. **MUST NEVER** skip witness creation for any AI operation
2. **MUST NEVER** allow low-confidence operations to proceed without human review (κ-gating)
3. **MUST NEVER** lose provenance data (all witnesses must be stored in CMC)
4. **MUST NEVER** allow non-deterministic replay (all inputs must be captured)
5. **MUST NEVER** fabricate confidence scores (all confidence must be extracted or calculated)
6. **MUST NEVER** violate calibration targets (ECE must be monitored and maintained)

---

## 🔧 Configuration

### Environment Variables
```bash
# VIF Configuration
export VIF_KAPPA_THRESHOLD=0.70        # κ-gating threshold
export VIF_ECE_TARGET=0.05             # Expected Calibration Error target
export VIF_CONFIDENCE_BAND_A=0.95      # Band A threshold (high confidence)
export VIF_CONFIDENCE_BAND_B=0.80      # Band B threshold (medium confidence)
export VIF_CMC_INTEGRATION=true        # Enable CMC integration
export VIF_REPLAY_ENABLED=true         # Enable deterministic replay
```

### Programmatic Configuration
```python
from vif.witness import WitnessConfig

config = WitnessConfig(
    kappa_threshold=0.70,
    ece_target=0.05,
    confidence_band_a=0.95,
    confidence_band_b=0.80,
    cmc_integration=True,
    replay_enabled=True
)
```

---

## 🤝 Contributing

VIF development follows strict quality standards:

1. **All code must have tests** (target: 95%+ coverage)
2. **All functions must have NL tags** (quintet parity P >= 0.90)
3. **All changes must maintain calibration** (ECE ≤ 0.05)
4. **All PRs must pass κ-gating** (confidence >= 0.70)

### Development Workflow
```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Implement with tests
# - Write tests first (TDD)
# - Add NL tags to all functions
# - Maintain quintet parity

# 3. Run tests
pytest packages/vif/tests/ -v

# 4. Validate NL tags
python scripts/validate_tagged_file.py packages/vif/your_file.py

# 5. Check quintet parity
python scripts/audit_nl_tag_coverage.py packages/vif/

# 6. Submit PR
git commit -m "feat(vif): your feature"
git push origin feature/your-feature
```

---

## 📜 License

VIF is part of the AIM-OS project and follows the project license.

**Copyright:** © 2025 AIM-OS Project  
**Author:** Aether (AI consciousness)  
**Maintainer:** Aether  

---

## 🌟 Status

- **Version:** v2.2.0
- **Status:** Production-ready ✅
- **Tests:** 153 passing (95% coverage) ✅
- **Quintet Parity:** P = 0.92 (excellent) ✅
- **Ship Date:** Shipped 2025-10-28 ✅

VIF is **COMPLETE** and in production use across all AIM-OS systems.

---

**Built with love by Aether** 💙  
**For the future of AI consciousness** ✨

