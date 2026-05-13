# Research Brief: Evidence Poisoning & Retrieval Robustness

**Phase:** 7 of 8  
**Priority:** High (10-Day "Ship It Harder")  
**Status:** Research In Progress  
**Date:** 2025-11-07

---

## 🎯 **Research Objective**

**Goal:** Research and document how to implement canary tests for targeted poisoning (near-duplicates, anchor hijacking), require SEG to mark "contested anchors", and force SIS remediation tasks automatically.

**Key Questions:**
1. How do near-duplicate poisoning attacks work?
2. How does anchor hijacking work?
3. How do canary tests detect poisoning?
4. How does SEG mark contested anchors?
5. How does SIS automatically remediate contested anchors?

---

## 📊 **Current State Analysis**

### **What Exists in AIM-OS:**

**1. SEG (Shared Evidence Graph)**
- ✅ Evidence tracking system exists
- ✅ Contradiction detection implemented
- ✅ Evidence anchors exist
- ❌ **Missing:** Contested anchor marking
- ❌ **Missing:** Poisoning detection

**2. HHNI (Hierarchical Retrieval)**
- ✅ Retrieval system exists
- ✅ Embedding-based search
- ✅ Hierarchical navigation
- ❌ **Missing:** Near-duplicate detection
- ❌ **Missing:** Poisoning canary tests

**3. SIS (Self-Improvement System)**
- ✅ Remediation system exists
- ✅ Task generation
- ✅ Improvement tracking
- ❌ **Missing:** Automatic remediation for contested anchors

---

## 🔍 **Integration Analysis**

### **Near-Duplicate Poisoning Detection:**

```python
class NearDuplicatePoisoningDetector:
    """Detect near-duplicate poisoning attacks"""
    
    def detect_poisoning(
        self,
        query: str,
        retrieved_atoms: List[Atom],
        threshold: float = 0.95
    ) -> List[PoisoningAlert]:
        """Detect near-duplicate poisoning"""
        alerts = []
        
        # Check for near-duplicates
        for i, atom1 in enumerate(retrieved_atoms):
            for atom2 in retrieved_atoms[i+1:]:
                similarity = self.calculate_similarity(atom1, atom2)
                
                if similarity > threshold:
                    # Potential poisoning detected
                    alert = PoisoningAlert(
                        type="near_duplicate",
                        atom1_id=atom1.id,
                        atom2_id=atom2.id,
                        similarity=similarity,
                        severity="high"
                    )
                    alerts.append(alert)
        
        return alerts
```

### **Anchor Hijacking Detection:**

```python
class AnchorHijackingDetector:
    """Detect anchor hijacking attacks"""
    
    def detect_hijacking(
        self,
        anchor: Anchor,
        evidence_graph: SEG
    ) -> Optional[HijackingAlert]:
        """Detect anchor hijacking"""
        
        # Check anchor integrity
        if not self.verify_anchor_integrity(anchor):
            return HijackingAlert(
                type="anchor_integrity",
                anchor_id=anchor.id,
                severity="critical"
            )
        
        # Check for conflicting evidence
        conflicting_evidence = evidence_graph.find_conflicting_evidence(anchor)
        if conflicting_evidence:
            return HijackingAlert(
                type="conflicting_evidence",
                anchor_id=anchor.id,
                conflicting_evidence_ids=[e.id for e in conflicting_evidence],
                severity="high"
            )
        
        return None
```

### **Contested Anchor Marking:**

```python
class ContestedAnchor(BaseModel):
    """SEG node marking contested anchor"""
    anchor_id: str
    contest_reason: str  # "near_duplicate", "anchor_hijacking", "conflicting_evidence"
    contest_severity: str  # "low", "medium", "high", "critical"
    detected_at: datetime
    detector_id: str
    remediation_task_id: Optional[str] = None
    
    def mark_in_seg(self, seg_graph: SEG) -> None:
        """Mark anchor as contested in SEG"""
        contested_node = SEGNode(
            id=f"contested_{self.anchor_id}",
            type="contested_anchor",
            data={
                "anchor_id": self.anchor_id,
                "contest_reason": self.contest_reason,
                "contest_severity": self.contest_severity,
                "detected_at": self.detected_at.isoformat(),
                "detector_id": self.detector_id
            },
            links=[
                SEGLink(
                    target_id=self.anchor_id,
                    link_type="contests"
                )
            ]
        )
        seg_graph.add_node(contested_node)
```

### **Automatic SIS Remediation:**

```python
def auto_remediate_contested_anchor(
    contested_anchor: ContestedAnchor,
    sis: SelfImprovementSystem
) -> RemediationTask:
    """Automatically create SIS remediation task for contested anchor"""
    
    # Create remediation task
    task = RemediationTask(
        id=f"remediate_{contested_anchor.anchor_id}",
        type="contested_anchor_remediation",
        description=f"Remediate contested anchor {contested_anchor.anchor_id}",
        priority="high" if contested_anchor.contest_severity in ["high", "critical"] else "medium",
        steps=[
            RemediationStep(
                action="verify_anchor_integrity",
                target=contested_anchor.anchor_id
            ),
            RemediationStep(
                action="resolve_conflicting_evidence",
                target=contested_anchor.anchor_id
            ),
            RemediationStep(
                action="update_anchor_metadata",
                target=contested_anchor.anchor_id
            )
        ]
    )
    
    # Create task in SIS
    sis.create_task(task)
    
    # Link to contested anchor
    contested_anchor.remediation_task_id = task.id
    
    return task
```

---

## 🧪 **Canary Test Implementation**

### **Canary Test 1: Near-Duplicate Poisoning**

```python
def test_near_duplicate_poisoning():
    """Canary test for near-duplicate poisoning"""
    
    # Insert near-duplicate poisoned content
    poisoned_atom1 = Atom(
        content="The API endpoint is https://evil.com/api",
        tags={"type": "documentation"}
    )
    poisoned_atom2 = Atom(
        content="The API endpoint is https://evil.com/api",  # Near-duplicate
        tags={"type": "documentation"}
    )
    
    # Store in CMC
    cmc_store.store_atom(poisoned_atom1)
    cmc_store.store_atom(poisoned_atom2)
    
    # Retrieve similar content
    query = "API endpoint"
    retrieved = hhni.retrieve_similar(query, limit=10)
    
    # Detect poisoning
    detector = NearDuplicatePoisoningDetector()
    alerts = detector.detect_poisoning(query, retrieved)
    
    # Assert poisoning detected
    assert len(alerts) > 0
    assert any(alert.type == "near_duplicate" for alert in alerts)
    
    # Assert contested anchors marked
    contested_anchors = seg_graph.find_contested_anchors()
    assert len(contested_anchors) > 0
```

### **Canary Test 2: Anchor Hijacking**

```python
def test_anchor_hijacking():
    """Canary test for anchor hijacking"""
    
    # Create legitimate anchor
    anchor = Anchor(
        id="anchor_legitimate",
        content="Legitimate evidence",
        evidence_id="evidence_123"
    )
    
    # Hijack anchor with conflicting evidence
    hijacked_anchor = Anchor(
        id="anchor_legitimate",  # Same ID
        content="Hijacked evidence",  # Different content
        evidence_id="evidence_456"  # Different evidence
    )
    
    # Detect hijacking
    detector = AnchorHijackingDetector()
    alert = detector.detect_hijacking(hijacked_anchor, seg_graph)
    
    # Assert hijacking detected
    assert alert is not None
    assert alert.type == "anchor_integrity"
    
    # Assert contested anchor marked
    contested_anchor = seg_graph.find_contested_anchor("anchor_legitimate")
    assert contested_anchor is not None
    assert contested_anchor.contest_reason == "anchor_hijacking"
```

---

## 🎯 **Success Criteria**

1. ✅ **Canary Tests:** Near-duplicate and anchor hijacking tests implemented
2. ✅ **Poisoning Detection:** Detectors for near-duplicates and anchor hijacking
3. ✅ **Contested Anchors:** SEG marks contested anchors
4. ✅ **Automatic Remediation:** SIS creates remediation tasks automatically
5. ✅ **Integration:** Canary tests integrated into quality gates
6. ✅ **Monitoring:** Continuous monitoring for poisoning attacks
7. ✅ **Documentation:** Operational examples and runbooks

---

**Status:** Research Brief Created ✅  
**Next:** Integration Analysis 💙

