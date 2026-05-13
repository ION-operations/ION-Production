# Research Brief: Privacy & PII Policy Gates

**Phase:** 5 of 8  
**Priority:** Medium (Next Sprint)  
**Status:** Research In Progress  
**Date:** 2025-11-07

---

## 🎯 **Research Objective**

**Goal:** Research and document how to integrate privacy gates into SDF-CVF, specifically PII classification/retention/consent flows as gates (e.g., "PII present → redact or permissioned enclave"), with auditable outcomes.

**Key Questions:**
1. How does PII classification work in AIM-OS?
2. How are retention policies enforced?
3. How are consent flows managed?
4. How do privacy gates integrate with SDF-CVF?
5. How do privacy gates emit auditable outcomes?

---

## 📊 **Current State Analysis**

### **What Exists in AIM-OS:**

**1. Privacy Infrastructure (Chapter 21.4-21.6)**
- ✅ Retention policies exist (policy model)
- ✅ DSAR/DSE flows documented
- ✅ Consent ledger in SEG
- ✅ PII tagging in CMC ingest
- ✅ Cryptographic tombstone strategy
- ❌ **Missing:** Privacy gates in SDF-CVF
- ❌ **Missing:** PII gate enforcement
- ❌ **Missing:** Auditable outcomes for privacy gates

**2. Retention Policies:**
```yaml
policy_id: rp-default-highrisk-v3
scope:
  seg_types: ["vif:event", "tool:egress", "decision", "claim", "snapshot"]
defaults:
  ttl_days: 190
  storage_class: WORM
exceptions:
  - condition: { legal_hold: true }
    override: { ttl_days: null }
  - condition: { contains_pii: true, purpose: "analytics" }
    override: { ttl_days: 30, dp: { epsilon: 1.0, delta: 1e-6 } }
```

---

## 🔍 **Integration Analysis**

### **PII Classification Gate:**

```python
class PIIGate(Gate):
    """Gate that checks for PII and enforces redaction or permission"""
    gate_type: str = "pii"
    
    def evaluate(self, content: str, metadata: Dict[str, Any]) -> GateOutcome:
        """Evaluate PII gate"""
        
        # Classify PII
        pii_classifier = PIIClassifier()
        pii_detected = pii_classifier.classify(content)
        
        if not pii_detected.has_pii:
            return GateOutcome.PASS, "No PII detected"
        
        # Check if permissioned enclave
        if metadata.get("permissioned_enclave"):
            return GateOutcome.PASS, "PII in permissioned enclave"
        
        # Check if redacted
        if metadata.get("redacted"):
            return GateOutcome.PASS, "PII redacted"
        
        # PII present without redaction or permission
        return GateOutcome.FAIL, f"PII detected: {pii_detected.pii_types}. Redact or use permissioned enclave."
```

### **SDF-CVF Privacy Gate Integration:**

```python
class SDFCVFPrivacyGate(Gate):
    """Privacy gate integrated with SDF-CVF"""
    gate_type: str = "sdf_cvf_privacy"
    
    def evaluate(self, artifact: Artifact) -> GateOutcome:
        """Evaluate privacy gate for artifact"""
        
        # Check PII
        pii_gate = PIIGate()
        pii_outcome, pii_message = pii_gate.evaluate(artifact.content, artifact.metadata)
        
        if pii_outcome == GateOutcome.FAIL:
            return GateOutcome.FAIL, pii_message
        
        # Check retention policy
        retention_gate = RetentionPolicyGate()
        retention_outcome, retention_message = retention_gate.evaluate(artifact)
        
        if retention_outcome == GateOutcome.FAIL:
            return GateOutcome.FAIL, retention_message
        
        # Check consent
        consent_gate = ConsentGate()
        consent_outcome, consent_message = consent_gate.evaluate(artifact)
        
        if consent_outcome == GateOutcome.FAIL:
            return GateOutcome.FAIL, consent_message
        
        # All privacy checks passed
        return GateOutcome.PASS, "All privacy checks passed"
```

---

**Status:** Research Brief Created ✅  
**Next:** Integration Analysis 💙

