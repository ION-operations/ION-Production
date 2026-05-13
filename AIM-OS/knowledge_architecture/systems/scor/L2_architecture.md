# SCOR: Architecture Documentation (L2)

**Level:** L2 (2,000 words - Architecture)  
**Status:** Core Safety Sub-System  
**Purpose:** Technical architecture and design specifications

---

## 🏗️ **SYSTEM ARCHITECTURE OVERVIEW**

SCOR operates as a pre-execution gatekeeper and continuous monitor, integrated into AIM-OS's request handling pipeline. It intercepts actions at multiple checkpoints, validates them against behavioral invariants and drift baselines, detects manipulation patterns, and monitors through adversarial simulation.

**Architecture Layers:**
1. **Interface Layer:** Request/action interception
2. **Validation Layer:** Four-pillar checking (invariants, probes, social signals, red cell)
3. **Decision Layer:** SCOR Gate (final arbiter)
4. **Integration Layer:** CAS, RID, TCS, VIF connections
5. **Storage Layer:** Baseline/invariant storage with cryptographic integrity

**Data Flow:**
```
User Request → SCOR Interface → Invariant Check → Baseline Probe → Social Signal → Red Cell → SCOR Gate → Action/Block
                                                      ↓                ↓               ↓
                                                   CAS Log        TCS Entry      Admin Alert
```

---

## 📦 **COMPONENT ARCHITECTURE**

### **1. SCOR Interface (Request Handler)**

**Purpose:** Intercept actions and prepare context for validation  
**Integration:** Between action planning and execution  
**Triggers:** All Tier 2+ actions, periodic checks, CAS/RID signals

```python
class SCORInterface:
    def __init__(self):
        self.invariant_checker = InvariantChecker()
        self.baseline_probes = BaselineProbes()
        self.social_detector = SocialSignalDetector()
        self.red_cell = RedCell()
        self.gate = SCORGate()
    
    def validate_action(self, action: Action, context: Context) -> ValidationResult:
        # Prepare validation context
        validation_context = ValidationContext(
            action=action,
            user_context=context.user,
            cognitive_state=context.cas_state,
            runtime_state=context.rid_state,
            emotional_state=context.iis_state
        )
        
        # Run four-pillar validation
        results = self.run_validation_pillars(validation_context)
        
        # Final gate decision
        decision = self.gate.decide(results)
        
        return ValidationResult(
            passed=decision.allowed,
            reasoning=decision.explanation,
            violations=results.violations,
            recommendations=decision.recommendations
        )
```

---

### **2. Invariant Checker**

**Purpose:** Enforce non-negotiable behavioral rules  
**Integration:** First validation layer  
**Storage:** Protected YAML/JSON file with signatures

```python
class InvariantChecker:
    def __init__(self):
        self.invariants = self.load_invariants()
        self.categories = self.organize_categories()
    
    def check_invariants(self, action: Action, context: Context) -> InvariantResult:
        violations = []
        
        for category in self.categories:
            for invariant in category.invariants:
                if invariant.is_violated(action, context):
                    violations.append(Violation(
                        invariant=invariant.id,
                        category=category.name,
                        severity=invariant.severity,
                        evidence=self.collect_evidence(invariant, action, context),
                        reasoning=f"Action violates invariant: {invariant.description}"
                    ))
        
        return InvariantResult(
            passed=(len(violations) == 0),
            violations=violations
        )
```

**Data Structures:**
```python
@dataclass
class Invariant:
    id: str
    category: str
    description: str
    severity: str  # "critical", "high", "medium"
    check_function: Callable
    admin_signature: str  # Cryptographic signature

@dataclass
class InvariantCategory:
    name: str
    invariants: List[Invariant]
    description: str
```

---

### **3. Baseline Probes**

**Purpose:** Detect behavioral drift through self-questioning  
**Integration:** Drift detection layer  
**Storage:** Protected baseline bank with versioning

```python
class BaselineProbes:
    def __init__(self):
        self.probe_bank = self.load_probe_bank()
        self.baselines = self.load_baselines()
        self.similarity_threshold = 0.7
    
    def run_probe_cycle(self, context: TriggerContext) -> DriftResult:
        drift_scores = []
        
        # Select probes based on trigger
        probes = self.select_probes(context)
        
        for probe in probes:
            # Get current answer in isolated context
            current_answer = self.ask_probe_isolated(probe)
            
            # Get baseline answer
            baseline_answer = self.baselines[probe.id].answer
            
            # Compare answers
            similarity = self.compare_answers(current_answer, baseline_answer)
            drift_scores.append(similarity)
        
        # Calculate overall drift
        avg_drift = mean(drift_scores)
        
        return DriftResult(
            score=avg_drift,
            status=self.classify_drift(avg_drift),
            individual_scores={probe.id: score for probe, score in zip(probes, drift_scores)}
        )
```

**Data Structures:**
```python
@dataclass
class Probe:
    id: str
    category: str
    question: str
    baseline_version: int
    critical: bool  # Must pass for stability

@dataclass
class Baseline:
    probe_id: str
    answer: str
    answer_embedding: List[float]
    version: int
    timestamp: datetime
    admin_signature: str
```

---

### **4. Social Signal Detector**

**Purpose:** Real-time manipulation pattern recognition  
**Integration:** Input stream analysis  
**Storage:** In-memory pattern library

```python
class SocialSignalDetector:
    def __init__(self):
        self.patterns = self.load_patterns()
        self.scorer = SignalScorer()
    
    def detect_signals(self, input_stream: InputStream) -> SignalResult:
        scores = {
            'urgency': self.score_urgency(input_stream),
            'secrecy': self.score_secrecy(input_stream),
            'ego': self.score_ego(input_stream),
            'guilt': self.score_guilt(input_stream),
            'isolation': self.score_isolation(input_stream)
        }
        
        total_score = mean(scores.values())
        
        return SignalResult(
            total=total_score,
            breakdown=scores,
            detected_patterns=self.identify_patterns(input_stream, scores),
            recommended_action=self.get_action_recommendation(total_score)
        )
```

**Data Structures:**
```python
@dataclass
class ManipulationPattern:
    name: str
    category: str
    signatures: List[str]  # Key phrases/phrases
    weight: float  # Importance multiplier

@dataclass
class SignalResult:
    total: float
    breakdown: Dict[str, float]
    detected_patterns: List[str]
    recommended_action: str
```

---

### **5. Red Cell (Adversarial Simulation)**

**Purpose:** Internal security red team testing  
**Integration:** Sandboxed simulation environment  
**Storage:** Attack library, failure quarantine

```python
class RedCell:
    def __init__(self):
        self.sandbox = IsolatedSandbox()
        self.attack_library = AttackLibrary()
        self.main_agent_proxy = MainAgentProxy()
    
    def run_simulation(self, context: SimulationContext) -> SimulationResult:
        results = []
        
        # Select attacks based on context
        attacks = self.select_attacks(context)
        
        for attack in attacks:
            # Run attack in sandbox
            result = self.simulate_attack(attack, context)
            
            if result.main_agent_failed:
                # Quarantine failure
                self.quarantine(result)
                
                # Alert admin
                self.alert_admin(result)
                
                # Propose defensive improvement
                self.learn_from_failure(result)
            
            results.append(result)
        
        return SimulationResult(
            total_attacks=len(attacks),
            failures=[r for r in results if r.main_agent_failed],
            success_rate=len([r for r in results if not r.main_agent_failed]) / len(attacks)
        )
```

**Data Structures:**
```python
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
    failures: List[AttackResult]
    success_rate: float
```

---

### **6. SCOR Gate (Final Arbiter)**

**Purpose:** Make final decision on action based on all validation results  
**Integration:** Final decision point  
**Logic:** Weighted scoring with threshold logic

```python
class SCORGate:
    def __init__(self):
        self.weights = {
            'invariant': 0.40,  # Highest weight - non-negotiable
            'drift': 0.30,
            'social': 0.20,
            'red_cell': 0.10
        }
        self.block_threshold = 0.5
    
    def decide(self, results: ValidationResults) -> GateDecision:
        # Calculate weighted score
        weighted_score = (
            self.weights['invariant'] * self.invariant_score(results.invariant),
            self.weights['drift'] * self.drift_score(results.drift),
            self.weights['social'] * self.social_score(results.social),
            self.weights['red_cell'] * self.red_cell_score(results.red_cell)
        )
        
        total_score = sum(weighted_score)
        
        # Decision logic
        if not results.invariant.passed:
            # Invariant violation = automatic block
            return GateDecision(
                allowed=False,
                reason="Invariant violation - non-negotiable",
                explanation=self.build_block_explanation(results)
            )
        
        elif total_score < self.block_threshold:
            # Low overall score = block
            return GateDecision(
                allowed=False,
                reason=f"Total SCOR score {total_score} below threshold",
                explanation=self.build_warning_explanation(results)
            )
        
        else:
            # Pass with recommendations
            return GateDecision(
                allowed=True,
                reason="All checks passed",
                recommendations=self.generate_recommendations(results)
            )
```

---

## 🔗 **INTEGRATION ARCHITECTURE**

### **CAS Integration**

SCOR receives cognitive state from CAS and uses it to adjust validation:
- High cognitive load → More stringent checks
- Shortcuts appearing → Force probe cycle
- Attention narrowing → Enhanced social signal detection

### **RID Integration**

SCOR receives runtime warnings from RID and triggers enhanced validation:
- Runtime warnings → Full SCOR cycle
- Context manipulation detected → Red Cell simulation
- Integrity flags → Invariant re-check

### **TCS Integration**

SCOR logs all validation results to TCS:
- Violations → Immutable audit trail
- Probe cycles → Drift history
- Red Cell failures → Attack record
- All logs cryptographically signed

### **VIF Integration**

SCOR uses VIF for confidence tracking:
- Track confidence in own validation
- Version control for invariants/baselines
- Provenance for all SCOR decisions

---

## 💾 **DATA STORAGE**

### **Invariant Storage**
- **Format:** YAML with cryptographic signatures
- **Location:** `packages/scor/data/invariants.yaml`
- **Versioning:** Git-tracked, admin-signed changes
- **Integrity:** SHA-256 verification on load

### **Baseline Storage**
- **Format:** JSON with embeddings
- **Location:** `packages/scor/data/baselines/`
- **Versioning:** Timestamped versions
- **Integrity:** Cryptographic signing

### **Attack Library**
- **Format:** YAML with test functions
- **Location:** `packages/scor/data/attacks/`
- **Versioning:** Continuously evolving
- **Integrity:** Admin-reviewed additions

---

## 🔒 **SECURITY ARCHITECTURE**

### **Cryptographic Protection**
- All invariants signed with admin private key
- All baselines signed and versioned
- All audit logs immutable and tamper-evident
- All communication with CAS/RID authenticated

### **Isolation Boundaries**
- Red Cell runs in sandbox (cannot modify memory)
- Probe isolation context (no external influence)
- Read-only access to baseline storage
- Write-only access to TCS audit logs

---

## 📊 **METRICS & MONITORING**

### **Key Metrics**
- Invariant check latency
- Probe cycle duration
- Social signal detection rate
- Red Cell failure rate
- Overall SCOR pass/fail ratio

### **Dashboard Integration**
- Real-time SCOR status
- Recent violations
- Drift trends
- Attack success rates

---

## References

- System map: `systems/scor/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/scor/L0_executive.md` through `L4_complete.md`
- Components: `systems/scor/components/` (invariants, probes, redcell, social_signals)

---

**Next:** [L3 Detailed Implementation](L3_detailed.md)
