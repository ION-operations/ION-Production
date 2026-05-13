# Integration Analysis: Calibration Reality Checks

**Phase:** 4 of 8  
**Priority:** High  
**Status:** Analysis Complete  
**Date:** 2025-11-07

---

## 🎯 **Integration Objective**

**Goal:** Integrate calibration curves, Brier scores, and ACE metrics as required artifacts for production-ready capabilities, with gates that fail if predicted vs observed bins diverge >ε.

**Key Integration Points:**
1. VIF Calibration → Calibration Curve Generation
2. Calibration Artifacts → Production-Ready Gate
3. Calibration Gates → SDF-CVF Quality Validation
4. Calibration Dashboards → CCS Monitoring

---

## 🔗 **System Integration Map**

### **VIF Calibration Enhancement**

**Current Calibration Flow:**
```
Predictions → ECE Tracker → ECE Score
```

**Enhanced Calibration Flow:**
```
Predictions → ECE Tracker → ECE Score
           → Brier Calculator → Brier Score ← NEW
           → ACE Calculator → ACE Score ← NEW
           → Calibration Curve Generator → Curve Artifact ← NEW
           → Production-Ready Gate Check ← NEW
           → SDF-CVF Quality Validation ← NEW
```

---

## 🏗️ **Technical Integration**

### **1. VIF Calibration Enhancement**

**Current ECE Tracker:**
```python
class ECETracker:
    num_bins: int = 10
    bins: List[CalibrationBin] = []
    
    def calculate_ece(self) -> float:
        """Calculate Expected Calibration Error"""
        # Implementation exists but incomplete
```

**Enhanced Calibration System:**
```python
class CalibrationSystem:
    """Complete calibration system with ECE, Brier, ACE"""
    
    def __init__(self):
        self.ece_tracker = ECETracker()
        self.brier_calculator = BrierCalculator()
        self.ace_calculator = ACECalculator()
        self.curve_generator = CalibrationCurveGenerator()
    
    def generate_calibration_artifacts(
        self,
        predictions: List[Prediction]
    ) -> CalibrationArtifacts:
        """Generate complete calibration artifacts"""
        
        # Calculate ECE
        ece_score = self.ece_tracker.calculate_ece(predictions)
        
        # Calculate Brier
        brier_score = self.brier_calculator.calculate_brier(predictions)
        
        # Calculate ACE
        ace_score = self.ace_calculator.calculate_ace(predictions)
        
        # Generate calibration curve
        calibration_curve = self.curve_generator.generate(predictions)
        
        return CalibrationArtifacts(
            ece_score=ece_score,
            brier_score=brier_score,
            ace_score=ace_score,
            calibration_curve=calibration_curve,
            predictions=predictions
        )
```

**Calibration Curve Generator:**
```python
class CalibrationCurveGenerator:
    """Generate calibration curves from predictions"""
    
    def generate(
        self,
        predictions: List[Prediction],
        num_bins: int = 10
    ) -> CalibrationCurve:
        """Generate calibration curve"""
        
        # Bin predictions
        bins = self._bin_predictions(predictions, num_bins)
        
        # Calculate curve data
        curve_data = []
        for bin in bins:
            curve_data.append({
                "confidence_range": bin.confidence_range,
                "avg_confidence": bin.avg_confidence,
                "accuracy": bin.accuracy,
                "count": bin.count,
                "divergence": bin.calibration_gap
            })
        
        # Check divergence
        max_divergence = max(bin.calibration_gap for bin in bins)
        divergence_threshold = 0.05  # ε
        
        return CalibrationCurve(
            bins=curve_data,
            ece_score=self._calculate_ece(bins),
            brier_score=self._calculate_brier(predictions),
            ace_score=self._calculate_ace(bins),
            max_divergence=max_divergence,
            divergence_threshold=divergence_threshold,
            bins_diverge=(max_divergence > divergence_threshold)
        )
```

---

### **2. Production-Ready Gate Integration**

**Production-Ready Gate:**
```python
class ProductionReadyGate(Gate):
    """Gate that requires calibration artifacts for production readiness"""
    gate_type: str = "production_ready"
    ece_threshold: float = 0.05
    brier_threshold: float = 0.10
    ace_threshold: float = 0.05
    divergence_threshold: float = 0.05  # ε
    
    def evaluate(self, capability: Capability) -> GateOutcome:
        """Evaluate if capability is production-ready"""
        
        # Check if calibration artifacts exist
        if not capability.calibration_artifacts:
            return GateOutcome.FAIL, "Calibration artifacts missing"
        
        artifacts = capability.calibration_artifacts
        
        # Check ECE threshold
        if artifacts.ece_score > self.ece_threshold:
            return GateOutcome.FAIL, f"ECE {artifacts.ece_score:.4f} > {self.ece_threshold}"
        
        # Check Brier threshold
        if artifacts.brier_score > self.brier_threshold:
            return GateOutcome.FAIL, f"Brier {artifacts.brier_score:.4f} > {self.brier_threshold}"
        
        # Check ACE threshold
        if artifacts.ace_score > self.ace_threshold:
            return GateOutcome.FAIL, f"ACE {artifacts.ace_score:.4f} > {self.ace_threshold}"
        
        # Check divergence
        if artifacts.calibration_curve.bins_diverge:
            return GateOutcome.FAIL, f"Bins diverge > {self.divergence_threshold}"
        
        return GateOutcome.PASS, "All calibration checks passed"
```

**SDF-CVF Integration:**
```python
class SDFCVFCalibrationGate(Gate):
    """Calibration gate integrated with SDF-CVF"""
    gate_type: str = "sdf_cvf_calibration"
    
    def evaluate(self, artifact: Artifact) -> GateOutcome:
        """Evaluate calibration gate for artifact"""
        
        # Check if artifact has calibration data
        if not hasattr(artifact, 'calibration_artifacts'):
            return GateOutcome.FAIL, "Calibration artifacts missing"
        
        # Run production-ready gate
        production_gate = ProductionReadyGate()
        outcome, message = production_gate.evaluate(artifact)
        
        # Create VIF witness for calibration check
        vif_witness = VIF.create_with_calibration(
            calibration_artifacts=artifact.calibration_artifacts,
            gate_outcome=outcome
        )
        
        # Link to SEG
        seg_node = SEGNode(
            id=f"calibration_check_{artifact.id}",
            type="calibration_check",
            data={
                "artifact_id": artifact.id,
                "ece_score": artifact.calibration_artifacts.ece_score,
                "brier_score": artifact.calibration_artifacts.brier_score,
                "ace_score": artifact.calibration_artifacts.ace_score,
                "gate_outcome": outcome.value
            },
            links=[
                SEGLink(target_id=vif_witness.id, link_type="witnessed_by")
            ]
        )
        seg_graph.add_node(seg_node)
        
        return outcome, message
```

---

### **3. VIF Witness Integration**

**VIF Witness Enhancement (with Calibration):**
```python
class VIF(BaseModel):
    # ... existing fields ...
    
    # Calibration Artifacts (NEW)
    calibration_artifacts: Optional[CalibrationArtifacts] = None
    ece_score: Optional[float] = None
    brier_score: Optional[float] = None
    ace_score: Optional[float] = None
    
    @classmethod
    def create_with_calibration(
        cls,
        calibration_artifacts: CalibrationArtifacts,
        **kwargs
    ) -> VIF:
        """Create VIF witness with calibration artifacts"""
        return cls(
            calibration_artifacts=calibration_artifacts,
            ece_score=calibration_artifacts.ece_score,
            brier_score=calibration_artifacts.brier_score,
            ace_score=calibration_artifacts.ace_score,
            # Adjust confidence based on calibration quality
            confidence_score=cls._adjust_confidence_for_calibration(
                kwargs.get('confidence_score', 0.0),
                calibration_artifacts
            ),
            **kwargs
        )
    
    @staticmethod
    def _adjust_confidence_for_calibration(
        base_confidence: float,
        artifacts: CalibrationArtifacts
    ) -> float:
        """Adjust confidence based on calibration quality"""
        # Poor calibration reduces confidence
        if artifacts.ece_score > 0.10:
            return base_confidence * 0.90
        elif artifacts.brier_score > 0.20:
            return base_confidence * 0.85
        else:
            return base_confidence
```

---

### **4. Calibration Dashboard Integration**

**CCS Dashboard Integration:**
```python
class CalibrationDashboard:
    """Calibration dashboard for CCS"""
    
    def generate_dashboard_data(
        self,
        capability_id: str,
        time_range: str = "30d"
    ) -> DashboardData:
        """Generate calibration dashboard data"""
        
        # Get calibration artifacts
        artifacts = self.get_calibration_artifacts(capability_id, time_range)
        
        # Generate dashboard data
        return DashboardData(
            ece_trend=self._calculate_ece_trend(artifacts),
            brier_trend=self._calculate_brier_trend(artifacts),
            ace_trend=self._calculate_ace_trend(artifacts),
            calibration_curves=self._generate_curves(artifacts),
            bin_data=self._generate_bin_data(artifacts),
            alerts=self._generate_alerts(artifacts)
        )
```

---

## 🔄 **Execution Flow Integration**

### **Calibration-Aware Capability Validation:**

```python
def validate_capability_production_ready(capability: Capability) -> ValidationResult:
    """Validate capability is production-ready with calibration"""
    
    # 1. Generate calibration artifacts
    calibration_system = CalibrationSystem()
    predictions = capability.get_predictions()
    artifacts = calibration_system.generate_calibration_artifacts(predictions)
    
    # 2. Store artifacts in capability
    capability.calibration_artifacts = artifacts
    
    # 3. Run production-ready gate
    gate = ProductionReadyGate()
    outcome, message = gate.evaluate(capability)
    
    # 4. Create VIF witness
    vif_witness = VIF.create_with_calibration(
        calibration_artifacts=artifacts,
        capability_id=capability.id,
        gate_outcome=outcome
    )
    
    # 5. Store in CMC
    cmc_store.store_atom(
        content=artifacts.to_dict(),
        tags={"type": "calibration_artifacts", "capability_id": capability.id},
        metadata={"vif_witness_id": vif_witness.id}
    )
    
    # 6. Link to SEG
    seg_node = create_calibration_seg_node(artifacts, capability.id, vif_witness.id)
    seg_graph.add_node(seg_node)
    
    return ValidationResult(
        production_ready=(outcome == GateOutcome.PASS),
        gate_outcome=outcome,
        message=message,
        calibration_artifacts=artifacts,
        vif_witness=vif_witness
    )
```

---

## 🧪 **Testing Integration**

### **Test 1: Calibration Artifact Generation**

```python
def test_calibration_artifact_generation():
    """Test calibration artifact generation"""
    
    # Create predictions
    predictions = [
        Prediction(confidence=0.90, correct=True),
        Prediction(confidence=0.85, correct=True),
        Prediction(confidence=0.80, correct=False),
        # ... more predictions
    ]
    
    # Generate artifacts
    calibration_system = CalibrationSystem()
    artifacts = calibration_system.generate_calibration_artifacts(predictions)
    
    # Assert artifacts exist
    assert artifacts.ece_score is not None
    assert artifacts.brier_score is not None
    assert artifacts.ace_score is not None
    assert artifacts.calibration_curve is not None
```

### **Test 2: Production-Ready Gate**

```python
def test_production_ready_gate():
    """Test production-ready gate"""
    
    # Create capability with calibration artifacts
    capability = Capability(
        id="test_capability",
        calibration_artifacts=CalibrationArtifacts(
            ece_score=0.03,  # Below threshold
            brier_score=0.08,  # Below threshold
            ace_score=0.04,  # Below threshold
            calibration_curve=CalibrationCurve(bins_diverge=False)
        )
    )
    
    # Run gate
    gate = ProductionReadyGate()
    outcome, message = gate.evaluate(capability)
    
    # Assert PASS
    assert outcome == GateOutcome.PASS
```

---

## 📋 **Implementation Checklist**

- [ ] Complete ECE implementation (currently 15%)
- [ ] Implement Brier score calculation
- [ ] Implement ACE metrics calculation
- [ ] Create CalibrationCurveGenerator class
- [ ] Create CalibrationArtifacts model
- [ ] Implement ProductionReadyGate class
- [ ] Integrate with SDF-CVF gates
- [ ] Enhance VIF witness with calibration fields
- [ ] Create calibration dashboard for CCS
- [ ] Store calibration artifacts in CMC
- [ ] Link calibration checks to SEG
- [ ] Create integration tests
- [ ] Create operational examples

---

**Status:** Integration Analysis Complete ✅  
**Next:** Implementation Planning 💙

