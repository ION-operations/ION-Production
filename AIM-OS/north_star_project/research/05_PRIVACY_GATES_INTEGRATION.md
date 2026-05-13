# Integration Analysis: Privacy & PII Policy Gates

**Phase:** 5 of 8  
**Priority:** Medium  
**Status:** Analysis Complete  
**Date:** 2025-11-07

---

## 🎯 **Integration Objective**

**Goal:** Integrate privacy gates (PII classification, retention policies, consent flows) into SDF-CVF gate system with auditable outcomes.

**Key Integration Points:**
1. PII Classification → Privacy Gate
2. Retention Policies → Retention Gate
3. Consent Flows → Consent Gate
4. Privacy Gates → SDF-CVF Integration
5. Privacy Outcomes → Auditable Evidence

---

## 🔗 **System Integration Map**

### **Privacy Gate Flow**

**Current Flow:**
```
Content → Store → Retrieve
```

**Enhanced Privacy-Aware Flow:**
```
Content → PII Classification ← NEW
           ↓
         Privacy Gate Check ← NEW
           ↓
         Retention Policy Check ← NEW
           ↓
         Consent Check ← NEW
           ↓
         Redact or Permissioned Enclave ← NEW
           ↓
         Store → Auditable Outcome ← NEW
```

---

## 🏗️ **Technical Integration**

### **1. PII Classification Gate**

**PII Classifier:**
```python
class PIIClassifier:
    """Classify PII in content"""
    
    def classify(self, content: str) -> PIIDetection:
        """Classify PII in content"""
        
        # Detect PII types
        pii_types = []
        
        # Email detection
        if self._detect_email(content):
            pii_types.append("email")
        
        # Phone detection
        if self._detect_phone(content):
            pii_types.append("phone")
        
        # SSN detection
        if self._detect_ssn(content):
            pii_types.append("ssn")
        
        # Credit card detection
        if self._detect_credit_card(content):
            pii_types.append("credit_card")
        
        # Name detection
        if self._detect_name(content):
            pii_types.append("name")
        
        return PIIDetection(
            has_pii=len(pii_types) > 0,
            pii_types=pii_types,
            confidence=self._calculate_confidence(pii_types)
        )
```

**PII Gate:**
```python
class PIIGate(Gate):
    """Gate that checks for PII and enforces redaction or permission"""
    gate_type: str = "pii"
    
    def __init__(self):
        self.pii_classifier = PIIClassifier()
    
    def evaluate(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Tuple[GateOutcome, str]:
        """Evaluate PII gate"""
        
        # Classify PII
        pii_detection = self.pii_classifier.classify(content)
        
        if not pii_detection.has_pii:
            return GateOutcome.PASS, "No PII detected"
        
        # Check if permissioned enclave
        if metadata.get("permissioned_enclave"):
            return GateOutcome.PASS, f"PII in permissioned enclave: {pii_detection.pii_types}"
        
        # Check if redacted
        if metadata.get("redacted"):
            return GateOutcome.PASS, f"PII redacted: {pii_detection.pii_types}"
        
        # PII present without redaction or permission
        return GateOutcome.FAIL, (
            f"PII detected: {pii_detection.pii_types}. "
            "Redact or use permissioned enclave."
        )
```

---

### **2. Retention Policy Gate**

**Retention Policy Gate:**
```python
class RetentionPolicyGate(Gate):
    """Gate that enforces retention policies"""
    gate_type: str = "retention_policy"
    
    def evaluate(self, artifact: Artifact) -> Tuple[GateOutcome, str]:
        """Evaluate retention policy gate"""
        
        # Get retention policy
        policy = self._get_retention_policy(artifact)
        
        # Check TTL
        if policy.ttl_days is not None:
            age_days = (datetime.now() - artifact.created_at).days
            
            if age_days > policy.ttl_days:
                # Check if legal hold
                if artifact.metadata.get("legal_hold"):
                    return GateOutcome.PASS, "Legal hold prevents deletion"
                
                # Check if exception applies
                if self._check_exceptions(artifact, policy):
                    return GateOutcome.PASS, "Exception applies"
                
                # TTL exceeded
                return GateOutcome.FAIL, (
                    f"TTL exceeded: {age_days} days > {policy.ttl_days} days"
                )
        
        return GateOutcome.PASS, "Retention policy satisfied"
```

---

### **3. Consent Gate**

**Consent Gate:**
```python
class ConsentGate(Gate):
    """Gate that checks consent for PII processing"""
    gate_type: str = "consent"
    
    def evaluate(self, artifact: Artifact) -> Tuple[GateOutcome, str]:
        """Evaluate consent gate"""
        
        # Check if PII present
        pii_gate = PIIGate()
        pii_detection = pii_gate.pii_classifier.classify(artifact.content)
        
        if not pii_detection.has_pii:
            return GateOutcome.PASS, "No PII, consent not required"
        
        # Check consent ledger in SEG
        consent_node = self._get_consent_node(artifact.user_id)
        
        if consent_node is None:
            return GateOutcome.FAIL, "Consent not found in ledger"
        
        # Check consent validity
        if not self._is_consent_valid(consent_node):
            return GateOutcome.FAIL, "Consent expired or revoked"
        
        # Check consent scope
        if not self._is_consent_scope_valid(consent_node, artifact):
            return GateOutcome.FAIL, "Consent scope insufficient"
        
        return GateOutcome.PASS, "Consent valid"
```

---

### **4. SDF-CVF Privacy Gate Integration**

**SDF-CVF Privacy Gate:**
```python
class SDFCVFPrivacyGate(Gate):
    """Privacy gate integrated with SDF-CVF"""
    gate_type: str = "sdf_cvf_privacy"
    
    def __init__(self):
        self.pii_gate = PIIGate()
        self.retention_gate = RetentionPolicyGate()
        self.consent_gate = ConsentGate()
    
    def evaluate(self, artifact: Artifact) -> Tuple[GateOutcome, str, PrivacyGateResult]:
        """Evaluate privacy gate for artifact"""
        
        # Check PII
        pii_outcome, pii_message = self.pii_gate.evaluate(
            artifact.content,
            artifact.metadata
        )
        
        if pii_outcome == GateOutcome.FAIL:
            return self._create_failure_result(
                artifact,
                pii_outcome,
                pii_message,
                "pii_check"
            )
        
        # Check retention policy
        retention_outcome, retention_message = self.retention_gate.evaluate(artifact)
        
        if retention_outcome == GateOutcome.FAIL:
            return self._create_failure_result(
                artifact,
                retention_outcome,
                retention_message,
                "retention_check"
            )
        
        # Check consent (if PII present)
        if pii_outcome == GateOutcome.PASS and "PII" in pii_message:
            consent_outcome, consent_message = self.consent_gate.evaluate(artifact)
            
            if consent_outcome == GateOutcome.FAIL:
                return self._create_failure_result(
                    artifact,
                    consent_outcome,
                    consent_message,
                    "consent_check"
                )
        
        # All privacy checks passed
        return self._create_success_result(artifact)
    
    def _create_success_result(self, artifact: Artifact) -> Tuple[GateOutcome, str, PrivacyGateResult]:
        """Create success result with auditable outcome"""
        
        # Create VIF witness
        vif_witness = VIF.create_with_privacy_check(
            artifact_id=artifact.id,
            pii_detected=False,
            retention_satisfied=True,
            consent_valid=True
        )
        
        # Create auditable outcome
        outcome = PrivacyGateResult(
            artifact_id=artifact.id,
            gate_outcome=GateOutcome.PASS,
            pii_check="PASS",
            retention_check="PASS",
            consent_check="PASS",
            vif_witness_id=vif_witness.id,
            timestamp=datetime.now()
        )
        
        # Store in CMC
        self._store_privacy_outcome(outcome)
        
        # Link to SEG
        self._link_privacy_to_seg(outcome, artifact)
        
        return GateOutcome.PASS, "All privacy checks passed", outcome
    
    def _create_failure_result(
        self,
        artifact: Artifact,
        outcome: GateOutcome,
        message: str,
        failed_check: str
    ) -> Tuple[GateOutcome, str, PrivacyGateResult]:
        """Create failure result with auditable outcome"""
        
        # Create VIF witness
        vif_witness = VIF.create_with_privacy_check(
            artifact_id=artifact.id,
            pii_detected=(failed_check == "pii_check"),
            retention_satisfied=(failed_check != "retention_check"),
            consent_valid=(failed_check != "consent_check")
        )
        
        # Create auditable outcome
        privacy_outcome = PrivacyGateResult(
            artifact_id=artifact.id,
            gate_outcome=outcome,
            pii_check="PASS" if failed_check != "pii_check" else "FAIL",
            retention_check="PASS" if failed_check != "retention_check" else "FAIL",
            consent_check="PASS" if failed_check != "consent_check" else "FAIL",
            vif_witness_id=vif_witness.id,
            timestamp=datetime.now(),
            failure_reason=message
        )
        
        # Store in CMC
        self._store_privacy_outcome(privacy_outcome)
        
        # Link to SEG
        self._link_privacy_to_seg(privacy_outcome, artifact)
        
        return outcome, message, privacy_outcome
```

---

### **5. Auditable Outcome Storage**

**Privacy Outcome Storage:**
```python
def store_privacy_outcome(outcome: PrivacyGateResult) -> Atom:
    """Store privacy gate outcome in CMC"""
    
    atom = cmc_store.store_atom(
        content=outcome.to_dict(),
        tags={
            "type": "privacy_gate_outcome",
            "artifact_id": outcome.artifact_id,
            "gate_outcome": outcome.gate_outcome.value
        },
        metadata={
            "outcome_id": outcome.id,
            "pii_check": outcome.pii_check,
            "retention_check": outcome.retention_check,
            "consent_check": outcome.consent_check,
            "vif_witness_id": outcome.vif_witness_id,
            "timestamp": outcome.timestamp.isoformat()
        }
    )
    
    return atom
```

**SEG Linking:**
```python
def link_privacy_to_seg(outcome: PrivacyGateResult, artifact: Artifact) -> SEGNode:
    """Link privacy gate outcome to SEG"""
    
    node = SEGNode(
        id=f"privacy_gate_{outcome.id}",
        type="privacy_gate_outcome",
        data={
            "outcome_id": outcome.id,
            "artifact_id": artifact.id,
            "gate_outcome": outcome.gate_outcome.value,
            "pii_check": outcome.pii_check,
            "retention_check": outcome.retention_check,
            "consent_check": outcome.consent_check,
            "timestamp": outcome.timestamp.isoformat()
        },
        links=[
            SEGLink(target_id=artifact.id, link_type="validates"),
            SEGLink(target_id=outcome.vif_witness_id, link_type="witnessed_by")
        ]
    )
    
    seg_graph.add_node(node)
    return node
```

---

## 🔄 **Execution Flow Integration**

### **Privacy-Aware Artifact Processing:**

```python
def process_artifact_with_privacy(artifact: Artifact) -> ProcessingResult:
    """Process artifact with privacy gates"""
    
    # Run privacy gate
    privacy_gate = SDFCVFPrivacyGate()
    outcome, message, privacy_result = privacy_gate.evaluate(artifact)
    
    if outcome == GateOutcome.FAIL:
        return ProcessingResult(
            success=False,
            reason=message,
            privacy_result=privacy_result
        )
    
    # Process artifact
    processed = process_artifact(artifact)
    
    return ProcessingResult(
        success=True,
        artifact=processed,
        privacy_result=privacy_result
    )
```

---

## 🧪 **Testing Integration**

### **Test 1: PII Gate**

```python
def test_pii_gate():
    """Test PII gate"""
    
    # Test with PII
    artifact = Artifact(
        content="Contact john.doe@example.com at 555-1234",
        metadata={}
    )
    
    gate = PIIGate()
    outcome, message = gate.evaluate(artifact.content, artifact.metadata)
    
    assert outcome == GateOutcome.FAIL
    assert "PII detected" in message
```

### **Test 2: Privacy Gate Integration**

```python
def test_privacy_gate_integration():
    """Test privacy gate integration"""
    
    artifact = Artifact(
        content="Contact john.doe@example.com",
        metadata={"permissioned_enclave": True}
    )
    
    gate = SDFCVFPrivacyGate()
    outcome, message, result = gate.evaluate(artifact)
    
    assert outcome == GateOutcome.PASS
    assert result.pii_check == "PASS"
```

---

## 📋 **Implementation Checklist**

- [ ] Create PIIClassifier class
- [ ] Implement PII detection methods
- [ ] Create PIIGate class
- [ ] Create RetentionPolicyGate class
- [ ] Create ConsentGate class
- [ ] Create SDFCVFPrivacyGate class
- [ ] Create PrivacyGateResult model
- [ ] Implement auditable outcome storage
- [ ] Implement SEG linking
- [ ] Create integration tests
- [ ] Create operational examples
- [ ] Document in SDF-CVF gates reference

---

**Status:** Integration Analysis Complete ✅  
**Next:** Implementation Planning 💙

