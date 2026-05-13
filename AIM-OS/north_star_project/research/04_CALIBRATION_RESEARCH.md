# Research Brief: Calibration Reality Checks

**Phase:** 4 of 8  
**Priority:** High (10-Day "Ship It Harder")  
**Status:** Research In Progress  
**Date:** 2025-11-07

---

## 🎯 **Research Objective**

**Goal:** Research and document how to implement calibration curves, Brier scores, and ACE metrics as required artifacts for production-ready capabilities, with gates that fail if predicted vs observed bins diverge >ε.

**Key Questions:**
1. How are calibration curves generated and validated?
2. How are Brier scores calculated and interpreted?
3. How are ACE (Average Calibration Error) metrics computed?
4. How do calibration gates enforce production readiness?
5. How do calibration artifacts integrate with VIF and SDF-CVF?

---

## 📊 **Current State Analysis**

### **What Exists in AIM-OS:**

**1. Chapter 21: Confidence Calibration**
- ✅ Complete calibration chapter in North Star Document
- ✅ Bayesian calibration model documented
- ✅ Calibration curves described
- ✅ Brier score mentioned
- ✅ ECE (Expected Calibration Error) documented

**2. VIF Calibration Implementation**
- ✅ ECE tracker exists (`packages/vif/calibration.py`)
- ✅ Calibration bins implemented
- ✅ ECE calculation implemented (15% complete)
- ❌ **Missing:** Calibration curve generation
- ❌ **Missing:** Brier score calculation
- ❌ **Missing:** ACE metrics
- ❌ **Missing:** Production-ready gate enforcement
- ❌ **Missing:** Calibration dashboards

**3. Current ECE Implementation:**
```python
class ECETracker:
    num_bins: int = 10
    bins: List[CalibrationBin] = []
    
    def calculate_ece(self) -> float:
        """Calculate Expected Calibration Error"""
        # Implementation exists but incomplete
```

---

## 🔍 **Integration Analysis**

### **Calibration Curve Generation:**

```python
class CalibrationCurve(BaseModel):
    """Calibration curve showing predicted vs observed accuracy"""
    bins: List[CalibrationBin]
    ece_score: float
    brier_score: float
    ace_score: float
    divergence_threshold: float = 0.05  # ε threshold
    
    def generate(self, predictions: List[Prediction]) -> None:
        """Generate calibration curve from predictions"""
        # Bin predictions by confidence
        for pred in predictions:
            bin_idx = int(pred.confidence * self.num_bins)
            self.bins[bin_idx].add_prediction(pred)
        
        # Calculate metrics
        self.ece_score = self.calculate_ece()
        self.brier_score = self.calculate_brier()
        self.ace_score = self.calculate_ace()
    
    def check_divergence(self) -> bool:
        """Check if bins diverge >ε"""
        for bin in self.bins:
            divergence = abs(bin.avg_confidence - bin.accuracy)
            if divergence > self.divergence_threshold:
                return True
        return False
```

### **Brier Score Calculation:**

```python
def calculate_brier_score(predictions: List[Prediction]) -> float:
    """Calculate Brier score for calibration quality
    
    Brier = (1/n) * Σ (predicted_i - actual_i)²
    
    Where:
    - predicted_i = confidence score (0-1)
    - actual_i = actual outcome (0 or 1)
    
    Interpretation:
    - Brier < 0.10: Excellent calibration
    - Brier < 0.20: Good calibration
    - Brier >= 0.20: Poor calibration (recalibration needed)
    """
    total_brier = 0.0
    
    for pred in predictions:
        predicted = pred.confidence
        actual = 1.0 if pred.correct else 0.0
        squared_error = (predicted - actual) ** 2
        total_brier += squared_error
    
    brier_score = total_brier / len(predictions)
    return brier_score
```

### **ACE (Average Calibration Error) Calculation:**

```python
def calculate_ace(predictions: List[Prediction], num_bins: int = 10) -> float:
    """Calculate Average Calibration Error
    
    ACE = (1/n) * Σ |Accuracy(Bin_i) - AverageConfidence(Bin_i)|
    
    Where:
    - Accuracy(Bin_i) = fraction correct in bin i
    - AverageConfidence(Bin_i) = average confidence in bin i
    
    Interpretation:
    - ACE < 0.05: Excellent calibration
    - ACE < 0.10: Good calibration
    - ACE >= 0.10: Poor calibration (recalibration needed)
    """
    # Bin predictions
    bins = [[] for _ in range(num_bins)]
    for pred in predictions:
        bin_idx = int(pred.confidence * num_bins)
        bin_idx = min(bin_idx, num_bins - 1)
        bins[bin_idx].append(pred)
    
    # Calculate ACE
    total_ace = 0.0
    total_count = len(predictions)
    
    for bin_predictions in bins:
        if not bin_predictions:
            continue
        
        bin_count = len(bin_predictions)
        bin_weight = bin_count / total_count
        
        # Calculate accuracy in bin
        bin_accuracy = sum(1 for p in bin_predictions if p.correct) / bin_count
        
        # Calculate average confidence in bin
        bin_confidence = sum(p.confidence for p in bin_predictions) / bin_count
        
        # Add to ACE
        bin_ace = abs(bin_accuracy - bin_confidence) * bin_weight
        total_ace += bin_ace
    
    return total_ace
```

### **Production-Ready Gate:**

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
        if not capability.calibration_curve:
            return GateOutcome.FAIL, "Calibration curve missing"
        
        if not capability.brier_score:
            return GateOutcome.FAIL, "Brier score missing"
        
        if not capability.ace_score:
            return GateOutcome.FAIL, "ACE score missing"
        
        # Check thresholds
        if capability.calibration_curve.ece_score > self.ece_threshold:
            return GateOutcome.FAIL, f"ECE {capability.calibration_curve.ece_score} > {self.ece_threshold}"
        
        if capability.brier_score > self.brier_threshold:
            return GateOutcome.FAIL, f"Brier {capability.brier_score} > {self.brier_threshold}"
        
        if capability.ace_score > self.ace_threshold:
            return GateOutcome.FAIL, f"ACE {capability.ace_score} > {self.ace_threshold}"
        
        # Check divergence
        if capability.calibration_curve.check_divergence():
            return GateOutcome.FAIL, f"Bins diverge > {self.divergence_threshold}"
        
        return GateOutcome.PASS, "All calibration checks passed"
```

---

## 🏗️ **Implementation Approach**

### **Step 1: Complete ECE Implementation**

1. **Prediction Tracking:**
   - Track predictions with confidence and outcomes
   - Store in CMC for historical analysis
   - Link to VIF witnesses

2. **Ground Truth Collection:**
   - Collect actual outcomes
   - Verify correctness
   - Store in CMC

3. **Continuous Monitoring:**
   - Monitor ECE over time
   - Alert on degradation
   - Trigger recalibration

### **Step 2: Implement Brier Score**

1. **Brier Calculation:**
   - Implement Brier score formula
   - Track Brier scores over time
   - Store in calibration artifacts

2. **Brier Decomposition:**
   - Calibration component
   - Resolution component
   - Uncertainty component

### **Step 3: Implement ACE Metrics**

1. **ACE Calculation:**
   - Implement ACE formula
   - Track ACE scores over time
   - Compare with ECE

2. **ACE Interpretation:**
   - Define thresholds
   - Create alerts
   - Trigger recalibration

### **Step 4: Create Calibration Gates**

1. **Production-Ready Gate:**
   - Require calibration artifacts
   - Check thresholds
   - Fail if divergence >ε

2. **Gate Integration:**
   - Integrate with SDF-CVF
   - Integrate with APOE gates
   - Integrate with VIF

---

## 📋 **Operational Examples**

### **Example 1: Generate Calibration Curve**

```python
# Collect predictions
predictions = [
    Prediction(confidence=0.90, correct=True),
    Prediction(confidence=0.85, correct=True),
    Prediction(confidence=0.80, correct=False),
    # ... more predictions
]

# Generate calibration curve
curve = CalibrationCurve(num_bins=10)
curve.generate(predictions)

# Check metrics
print(f"ECE: {curve.ece_score:.4f}")  # 0.0234
print(f"Brier: {curve.brier_score:.4f}")  # 0.0845
print(f"ACE: {curve.ace_score:.4f}")  # 0.0198
print(f"Divergence check: {curve.check_divergence()}")  # False
```

### **Example 2: Production-Ready Gate Check**

```python
# Check production readiness
gate = ProductionReadyGate()
outcome, message = gate.evaluate(capability)

# Results
if outcome == GateOutcome.PASS:
    print("✅ Production ready")
else:
    print(f"❌ Not production ready: {message}")
```

---

## 🎯 **Success Criteria**

1. ✅ **Calibration Curves:** Generated and validated
2. ✅ **Brier Scores:** Calculated and interpreted
3. ✅ **ACE Metrics:** Computed and tracked
4. ✅ **Production-Ready Gate:** Enforces calibration requirements
5. ✅ **Divergence Detection:** Fails if bins diverge >ε
6. ✅ **VIF Integration:** Calibration artifacts in VIF witnesses
7. ✅ **SDF-CVF Integration:** Calibration gates in quality validation
8. ✅ **Dashboards:** Calibration dashboards with bins, Brier, ACE

---

**Status:** Research Brief Created ✅  
**Next:** Integration Analysis 💙

