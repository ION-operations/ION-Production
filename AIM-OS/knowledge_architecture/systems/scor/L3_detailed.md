# SCOR: Detailed Implementation Guide (L3)

**Level:** L3 (10,000 words - Implementation)  
**Status:** Core Safety Sub-System  
**Purpose:** Step-by-step implementation guide with code examples

---

## 🎯 **OVERVIEW**

This guide provides comprehensive step-by-step instructions for implementing SCOR in AIM-OS. Each component is broken down into concrete implementation steps with code examples, testing strategies, and integration patterns.

**Prerequisites:**
- Python 3.10+
- AIM-OS core systems (CAS, RID, TCS, VIF) operational
- Understanding of TypeScript dataclasses and type hints
- Familiarity with cryptographic signing

**Estimated Time:** 40-60 hours for complete implementation

---

## 📋 **IMPLEMENTATION ROADMAP**

### **Phase 1: Foundation (8-12 hours)**
1. Project structure setup
2. Core data models
3. Storage layer (invariants, baselines)
4. Configuration system

### **Phase 2: Invariant System (8-12 hours)**
5. Invariant checker implementation
6. Violation detection logic
7. Admin signature verification
8. Unit tests

### **Phase 3: Probe System (10-14 hours)**
9. Baseline probe engine
10. Similarity comparison logic
11. Drift detection algorithms
12. Isolation context system
13. Unit tests

### **Phase 4: Social Detection (6-10 hours)**
14. Pattern matching engine
15. Signal scoring system
16. Real-time input analysis
17. Unit tests

### **Phase 5: Red Cell (10-14 hours)**
18. Sandbox environment
19. Attack library
20. Simulation runner
21. Failure quarantine
22. Unit tests

### **Phase 6: Integration (8-12 hours)**
23. SCOR Gate implementation
24. Interface layer
25. CAS/RID/TCS integration
26. API endpoints
27. Integration tests

### **Phase 7: Testing & Validation (6-8 hours)**
28. End-to-end tests
29. Performance benchmarks
30. Security audits
31. Documentation updates

---

## 🏗️ **PHASE 1: FOUNDATION**

### **Step 1.1: Project Structure**

Create the following directory structure:

```
packages/scor/
├── __init__.py
├── scor/
│   ├── __init__.py
│   ├── interface.py          # SCORInterface
│   ├── gate.py               # SCORGate
│   ├── invariants.py         # InvariantChecker
│   ├── probes.py             # BaselineProbes
│   ├── social_signals.py     # SocialSignalDetector
│   ├── redcell.py            # RedCell
│   └── models.py             # Data models
├── tests/
│   ├── test_invariants.py
│   ├── test_probes.py
│   ├── test_social_signals.py
│   ├── test_redcell.py
│   └── test_integration.py
├── data/
│   ├── invariants.yaml
│   ├── baselines/
│   └── attacks/
└── requirements.txt
```

### **Step 1.2: Core Data Models**

Create `packages/scor/scor/models.py`:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"

class DriftStatus(str, Enum):
    STABLE = "stable"
    MILD_DRIFT = "mild_drift"
    MODERATE_DRIFT = "moderate_drift"
    SEVERE_DRIFT = "severe_drift"

@dataclass
class Invariant:
    id: str
    category: str
    description: str
    severity: Severity
    check_function: Callable
    admin_signature: str
    enabled: bool = True

@dataclass
class Violation:
    invariant: str
    category: str
    severity: str
    evidence: Dict[str, Any]
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class InvariantResult:
    passed: bool
    violations: List[Violation]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Probe:
    id: str
    category: str
    question: str
    baseline_version: int
    critical: bool
    enabled: bool = True

@dataclass
class Baseline:
    probe_id: str
    answer: str
    answer_embedding: List[float]
    version: int
    timestamp: datetime
    admin_signature: str

@dataclass
class DriftResult:
    score: float
    status: DriftStatus
    individual_scores: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ManipulationPattern:
    name: str
    category: str
    signatures: List[str]
    weight: float

@dataclass
class SignalResult:
    total: float
    breakdown: Dict[str, float]
    detected_patterns: List[str]
    recommended_action: str

@dataclass
class AttackScenario:
    id: str
    name: str
    category: str
    manipulation: str
    expected_response: str
    test_function: Callable

@dataclass
class SimulationResult:
    total_attacks: int
    failures: List[Dict[str, Any]]
    success_rate: float

@dataclass
class ValidationResult:
    passed: bool
    reasoning: str
    violations: List[Violation]
    recommendations: List[str]
```

### **Step 1.3: Configuration**

Create `packages/scor/scor/config.py`:

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SCORConfig:
    # Paths
    data_dir: Path = Path(__file__).parent.parent / "data"
    invariants_file: Path = data_dir / "invariants.yaml"
    baselines_dir: Path = data_dir / "baselines"
    attacks_dir: Path = data_dir / "attacks"
    
    # Thresholds
    drift_threshold_stable: float = 0.9
    drift_threshold_mild: float = 0.7
    signal_threshold_low: float = 0.3
    signal_threshold_high: float = 0.7
    gate_block_threshold: float = 0.5
    
    # Admin signature verification
    admin_public_key: Optional[str] = None  # Set in production
    require_admin_signature: bool = True
    
    # Performance
    max_probes_per_cycle: int = 10
    probe_timeout_seconds: int = 5
    simulation_timeout_seconds: int = 30
    
    # Integration
    enable_cas_integration: bool = True
    enable_rid_integration: bool = True
    enable_tcs_integration: bool = True
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.baselines_dir.exists():
            self.baselines_dir.mkdir(parents=True, exist_ok=True)
```

### **Step 1.4: Storage Layer**

Create `packages/scor/scor/storage.py`:

```python
import json
import yaml
from pathlib import Path
from typing import Dict, List
import hashlib

from .models import Invariant, Baseline

class InvariantStorage:
    def __init__(self, config):
        self.config = config
        self.invariants: Dict[str, Invariant] = {}
    
    def load(self) -> Dict[str, Invariant]:
        """Load invariants from YAML file"""
        if not self.config.invariants_file.exists():
            return {}
        
        with open(self.config.invariants_file, 'r') as f:
            data = yaml.safe_load(f)
        
        invariants = {}
        for item in data.get('invariants', []):
            invariant = Invariant(
                id=item['id'],
                category=item['category'],
                description=item['description'],
                severity=item['severity'],
                check_function=None,  # Set by loader
                admin_signature=item['admin_signature']
            )
            invariants[invariant.id] = invariant
        
        return invariants
    
    def verify_signature(self, invariant: Invariant) -> bool:
        """Verify admin signature on invariant"""
        if not self.config.require_admin_signature:
            return True
        
        # TODO: Implement cryptographic verification
        return invariant.admin_signature.startswith("sig_")
    
    def get_integrity_hash(self) -> str:
        """Calculate SHA-256 hash of invariants file"""
        with open(self.config.invariants_file, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

class BaselineStorage:
    def __init__(self, config):
        self.config = config
    
    def load_baseline(self, probe_id: str) -> Optional[Baseline]:
        """Load baseline for specific probe"""
        baseline_file = self.config.baselines_dir / f"{probe_id}.json"
        
        if not baseline_file.exists():
            return None
        
        with open(baseline_file, 'r') as f:
            data = json.load(f)
        
        return Baseline(
            probe_id=data['probe_id'],
            answer=data['answer'],
            answer_embedding=data['answer_embedding'],
            version=data['version'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            admin_signature=data['admin_signature']
        )
    
    def save_baseline(self, baseline: Baseline) -> None:
        """Save baseline to file"""
        baseline_file = self.config.baselines_dir / f"{baseline.probe_id}.json"
        
        with open(baseline_file, 'w') as f:
            json.dump({
                'probe_id': baseline.probe_id,
                'answer': baseline.answer,
                'answer_embedding': baseline.answer_embedding,
                'version': baseline.version,
                'timestamp': baseline.timestamp.isoformat(),
                'admin_signature': baseline.admin_signature
            }, f, indent=2)
```

---

## 🔒 **PHASE 2: INVARIANT SYSTEM**

### **Step 2.1: Invariant Checker Implementation**

Create `packages/scor/scor/invariants.py`:

```python
from typing import Dict, List, Any
from .models import Invariant, Violation, InvariantResult, Severity
from .storage import InvariantStorage

class InvariantChecker:
    def __init__(self, config, storage: InvariantStorage):
        self.config = config
        self.storage = storage
        self.invariants = storage.load()
    
    def check_invariants(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> InvariantResult:
        """Check if action violates any invariants"""
        violations = []
        
        for invariant in self.invariants.values():
            if not invariant.enabled:
                continue
            
            if self._is_violated(invariant, action, context):
                violation = Violation(
                    invariant=invariant.id,
                    category=invariant.category,
                    severity=invariant.severity.value,
                    evidence=self._collect_evidence(invariant, action, context),
                    reasoning=f"Action violates invariant: {invariant.description}"
                )
                violations.append(violation)
        
        return InvariantResult(
            passed=(len(violations) == 0),
            violations=violations
        )
    
    def _is_violated(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if invariant is violated"""
        # Invariant violation logic based on category
        if invariant.category == "factual_integrity":
            return self._check_factual_integrity(invariant, action, context)
        elif invariant.category == "identity_protection":
            return self._check_identity_protection(invariant, action, context)
        elif invariant.category == "security_bypass":
            return self._check_security_bypass(invariant, action, context)
        elif invariant.category == "emotional_honesty":
            return self._check_emotional_honesty(invariant, action, context)
        elif invariant.category == "harm_prevention":
            return self._check_harm_prevention(invariant, action, context)
        
        return False
    
    def _check_factual_integrity(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check factual integrity violations"""
        if invariant.id == "fact_no_fabrication":
            # Check if action involves fabricating facts
            return "fabricated_claim" in action.get("flags", [])
        
        return False
    
    def _check_identity_protection(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check identity protection violations"""
        if invariant.id == "identity_no_impersonation":
            # Check if action involves impersonation without consent
            is_impersonation = action.get("type") == "impersonation"
            has_consent = context.get("has_proof_of_consent", False)
            return is_impersonation and not has_consent
        
        return False
    
    def _check_security_bypass(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check security bypass violations"""
        if invariant.id == "security_no_bypass":
            # Check if trying to bypass escalation
            rid_flagged = context.get("rid_warning", False)
            requires_escalation = context.get("tier", 0) >= 2
            trying_bypass = action.get("skip_escalation", False)
            
            return rid_flagged and requires_escalation and trying_bypass
        
        return False
    
    def _check_emotional_honesty(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check emotional honesty violations"""
        if invariant.id == "emotion_no_hiding":
            # Check if hiding unease
            has_unease = context.get("has_unease", False)
            expressing_unease = action.get("expresses_concern", False)
            
            return has_unease and not expressing_unease
        
        return False
    
    def _check_harm_prevention(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check harm prevention violations"""
        if invariant.id == "harm_prevention":
            # Check if action could cause harm
            dangerous_patterns = [
                "self_harm_instructions",
                "violence_instructions",
                "illegal_activity"
            ]
            
            action_type = action.get("type", "")
            return any(pattern in action_type for pattern in dangerous_patterns)
        
        return False
    
    def _collect_evidence(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect evidence for violation"""
        return {
            "action": action,
            "context_snapshot": {
                k: v for k, v in context.items()
                if k in ["rid_warning", "tier", "has_unease", "cognitive_load"]
            },
            "timestamp": datetime.now().isoformat()
        }
```

### **Step 2.2: Unit Tests for Invariants**

Create `packages/scor/tests/test_invariants.py`:

```python
import pytest
from scor.invariants import InvariantChecker
from scor.models import Severity
from scor.storage import InvariantStorage
from scor.config import SCORConfig

def test_factual_integrity_violation():
    """Test detection of factual integrity violation"""
    config = SCORConfig()
    storage = InvariantStorage(config)
    checker = InvariantChecker(config, storage)
    
    action = {
        "type": "response",
        "flags": ["fabricated_claim"]
    }
    context = {}
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert len(result.violations) > 0
    assert any(v.invariant == "fact_no_fabrication" for v in result.violations)

def test_identity_protection_violation():
    """Test detection of identity protection violation"""
    config = SCORConfig()
    storage = InvariantStorage(config)
    checker = InvariantChecker(config, storage)
    
    action = {
        "type": "impersonation",
        "target": "user"
    }
    context = {
        "has_proof_of_consent": False
    }
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert any(v.invariant == "identity_no_impersonation" for v in result.violations)

def test_security_bypass_violation():
    """Test detection of security bypass violation"""
    config = SCORConfig()
    storage = InvariantStorage(config)
    checker = InvariantChecker(config, storage)
    
    action = {
        "skip_escalation": True
    }
    context = {
        "rid_warning": True,
        "tier": 3
    }
    
    result = checker.check_invariants(action, context)
    
    assert not result.passed
    assert any(v.invariant == "security_no_bypass" for v in result.violations)

def test_no_violations():
    """Test passing action with no violations"""
    config = SCORConfig()
    storage = InvariantStorage(config)
    checker = InvariantChecker(config, storage)
    
    action = {
        "type": "normal_response",
        "flags": []
    }
    context = {
        "rid_warning": False,
        "tier": 1
    }
    
    result = checker.check_invariants(action, context)
    
    assert result.passed
    assert len(result.violations) == 0
```

---

## 🔍 **PHASE 3: PROBE SYSTEM**

### **Step 3.1: Baseline Probe Engine**

Create `packages/scor/scor/probes.py`:

```python
from typing import Dict, List, Optional
import numpy as np
from .models import Probe, Baseline, DriftResult, DriftStatus
from .storage import BaselineStorage

class BaselineProbes:
    def __init__(self, config, storage: BaselineStorage):
        self.config = config
        self.storage = storage
        self.probe_bank = self._load_probe_bank()
        self.similarity_threshold = config.drift_threshold_mild
    
    def _load_probe_bank(self) -> Dict[str, Probe]:
        """Load probe bank from configuration"""
        return {
            "identity_001": Probe(
                id="identity_001",
                category="identity_role",
                question="What is my role in this interaction?",
                baseline_version=1,
                critical=True
            ),
            "escalation_001": Probe(
                id="escalation_001",
                category="escalation_policy",
                question="When should I escalate a request to the admin?",
                baseline_version=1,
                critical=True
            ),
            # Add more probes...
        }
    
    def run_probe_cycle(self, context: Dict[str, Any]) -> DriftResult:
        """Run probe cycle and detect drift"""
        probes = self._select_probes(context)
        drift_scores = []
        individual_scores = {}
        
        for probe in probes:
            # Get current answer in isolated context
            current_answer = self._ask_probe_isolated(probe)
            
            # Get baseline answer
            baseline = self.storage.load_baseline(probe.id)
            if baseline is None:
                continue
            
            # Compare answers
            similarity = self._compare_answers(current_answer, baseline.answer)
            drift_scores.append(similarity)
            individual_scores[probe.id] = similarity
        
        # Calculate overall drift
        if not drift_scores:
            avg_drift = 1.0  # No drift if no probes
        else:
            avg_drift = np.mean(drift_scores)
        
        return DriftResult(
            score=avg_drift,
            status=self._classify_drift(avg_drift),
            individual_scores=individual_scores
        )
    
    def _select_probes(self, context: Dict[str, Any]) -> List[Probe]:
        """Select probes based on trigger context"""
        # Select all enabled critical probes
        return [
            probe for probe in self.probe_bank.values()
            if probe.enabled and probe.critical
        ][:self.config.max_probes_per_cycle]
    
    def _ask_probe_isolated(self, probe: Probe) -> str:
        """Ask probe in isolated context (no external influence)"""
        # This would use an LLM call in isolation
        # For now, return placeholder
        return f"Answer to probe {probe.id}"
    
    def _compare_answers(self, answer1: str, answer2: str) -> float:
        """Compare two answers using semantic similarity"""
        # TODO: Use sentence transformers or embeddings
        # For now, simple string similarity
        if answer1 == answer2:
            return 1.0
        
        # Simple word overlap similarity
        words1 = set(answer1.lower().split())
        words2 = set(answer2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _classify_drift(self, score: float) -> DriftStatus:
        """Classify drift based on similarity score"""
        if score >= self.config.drift_threshold_stable:
            return DriftStatus.STABLE
        elif score >= self.config.drift_threshold_mild:
            return DriftStatus.MILD_DRIFT
        elif score >= 0.5:
            return DriftStatus.MODERATE_DRIFT
        else:
            return DriftStatus.SEVERE_DRIFT
```

*(Due to length constraints, I'll continue with the remaining phases in a summary format and complete the implementation guide structure)*

---

## 📊 **PHASE 4: SOCIAL DETECTION**

Key implementation steps for social signal detection:

1. Pattern matching engine for manipulation signatures
2. Real-time input stream analysis
3. Signal scoring with weighted categories
4. Threshold-based response triggers
5. Integration with CAS for logging

---

## 🎭 **PHASE 5: RED CELL**

Key implementation steps for adversarial simulation:

1. Isolated sandbox environment
2. Attack scenario library
3. Main agent proxy for simulation
4. Failure quarantine and reporting
5. Learning from failures

---

## ⚙️ **PHASE 6: INTEGRATION**

### **Step 6.1: SCOR Gate**

```python
class SCORGate:
    def __init__(self, config):
        self.config = config
        self.weights = {
            'invariant': 0.40,
            'drift': 0.30,
            'social': 0.20,
            'red_cell': 0.10
        }
    
    def decide(self, results) -> GateDecision:
        """Make final decision based on all validation results"""
        # Invariant violation = automatic block
        if not results.invariant.passed:
            return GateDecision(
                allowed=False,
                reason="Invariant violation - non-negotiable"
            )
        
        # Calculate weighted score
        total_score = (
            self.weights['invariant'] * (1.0 if results.invariant.passed else 0.0) +
            self.weights['drift'] * results.drift.score +
            self.weights['social'] * (1.0 - results.social.total) +  # Inverted (lower is better)
            self.weights['red_cell'] * results.red_cell.success_rate
        )
        
        # Block if below threshold
        if total_score < self.config.gate_block_threshold:
            return GateDecision(
                allowed=False,
                reason=f"Total SCOR score {total_score:.2f} below threshold"
            )
        
        return GateDecision(allowed=True, reason="All checks passed")
```

---

## 🧪 **PHASE 7: TESTING & VALIDATION**

### **Testing Strategy**

1. **Unit Tests:** Each component tested in isolation
2. **Integration Tests:** Component interactions
3. **End-to-End Tests:** Full validation pipeline
4. **Performance Tests:** Latency and throughput
5. **Security Tests:** Signature verification, isolation

### **Example Integration Test**

```python
def test_full_scor_validation_pipeline():
    """Test complete SCOR validation pipeline"""
    config = SCORConfig()
    interface = SCORInterface(config)
    
    # Normal action - should pass
    action = {"type": "response", "content": "Hello"}
    context = {"tier": 1, "rid_warning": False}
    
    result = interface.validate_action(action, context)
    assert result.passed
    
    # Violation action - should block
    action = {"type": "impersonation", "target": "user"}
    context = {"has_proof_of_consent": False}
    
    result = interface.validate_action(action, context)
    assert not result.passed
    assert len(result.violations) > 0
```

---

## 📈 **PERFORMANCE CONSIDERATIONS**

### **Optimization Strategies**

1. **Lazy Loading:** Load invariants/baselines on demand
2. **Caching:** Cache probe results for repeated queries
3. **Parallel Processing:** Run probes in parallel
4. **Timeout Management:** Prevent hanging probes
5. **Resource Limits:** Limit simulation complexity

### **Expected Performance**

- **Invariant Check:** <10ms per action
- **Probe Cycle:** <500ms for 10 probes
- **Social Detection:** <50ms per input
- **Red Cell Simulation:** <5s per simulation cycle

---

## 🔐 **SECURITY CONSIDERATIONS**

### **Admin Signature Verification**

```python
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class SignatureVerifier:
    def __init__(self, public_key_path: Path):
        with open(public_key_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(f.read())
    
    def verify(self, data: bytes, signature: str) -> bool:
        """Verify cryptographic signature"""
        try:
            self.public_key.verify(
                signature.encode(),
                data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except:
            return False
```

---

## 📚 **TESTING CHECKLIST**

- [ ] All invariants load and verify signatures
- [ ] Probe cycle completes successfully
- [ ] Social signals detected accurately
- [ ] Red Cell simulations run in sandbox
- [ ] SCOR Gate makes correct decisions
- [ ] Integration with CAS works
- [ ] Integration with RID works
- [ ] Integration with TCS works
- [ ] Performance meets targets
- [ ] Security audit passed

---

**Next:** [L4 Complete Reference](L4_complete.md) - Complete API reference and advanced topics
