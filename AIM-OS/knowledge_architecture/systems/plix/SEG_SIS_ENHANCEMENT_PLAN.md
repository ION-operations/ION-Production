# PLIx Enhancement: SEG & SIS Deep Research & Implementation Plan

**Date:** 2025-11-09  
**Status:** 🔬 **DEEP RESEARCH COMPLETE** → 📋 **READY FOR IMPLEMENTATION**  
**Priority:** Critical - Enables PLIx → AIM-OS integration

---

## 🌟 Executive Summary

**SEG Enhancement:** Add PLIx-specific contradiction detection (intent vs outcome, postcondition failure)  
**SIS Enhancement:** Extend dream generation with PLIx intent failure pattern extraction

**Key Finding:** Both systems exist with solid foundations. Enhancements are **additive**, not rewrites.

---

## 📊 System Analysis: SEG (Shared Evidence Graph)

### **Current State Assessment**

**Status:** ~10% complete, but foundation is solid

**What Exists:**
- ✅ **Graph Structure:** NetworkX MultiDiGraph with entities, relations, evidence
- ✅ **Bitemporal Support:** Transaction time (TT) + Valid time (VT) tracking
- ✅ **Basic Contradiction Detection:** `detect_contradictions()` method
- ✅ **Models:** Entity, Relation, Evidence, Contradiction models
- ✅ **Tests:** `test_contradiction_detection.py` with 7 tests

**What Works:**
```python
# Current contradiction detection
def detect_contradictions(self) -> List[Contradiction]:
    """Detect potential contradictions in the graph."""
    # Only detects explicit CONTRADICTS relations
    contradicting_relations = self.get_relations(
        relation_type=RelationType.CONTRADICTS
    )
    # Creates Contradiction objects from relations
```

**What's Missing for PLIx:**
- ❌ **Intent vs Outcome Comparison:** Compare PLIx intent postconditions with actual outcomes
- ❌ **Postcondition Failure Detection:** Detect when postconditions are not achieved
- ❌ **Semantic Contradiction Detection:** Find contradictions without explicit CONTRADICTS edges
- ❌ **PLIx-Specific Entity Types:** Intent entities, Outcome entities, Postcondition entities

---

### **PLIx Requirements Analysis**

**From Perplexity's Feedback:**
> "PLIx intent vs actual outcome anchored in SEG. Detect: Intent violated? Postcondition failed?"

**Required Capabilities:**

1. **Intent Entity Storage**
   - Store PLIx intent as SEG Entity
   - Link to contract, postconditions, preconditions
   - Tag with `plix_intent` type

2. **Outcome Entity Storage**
   - Store execution outcome as SEG Entity
   - Link to intent entity
   - Store actual results vs expected postconditions

3. **Postcondition Verification**
   - Compare expected postconditions with actual outcomes
   - Detect failures (postcondition not achieved)
   - Create contradiction when intent violated

4. **Contradiction Detection Enhancement**
   - Semantic comparison (not just explicit CONTRADICTS edges)
   - Postcondition failure detection
   - Intent violation detection

---

### **SEG Enhancement Design**

#### **1. New Entity Types for PLIx**

```python
class PLIxIntentEntity(Entity):
    """PLIx intent stored as SEG entity"""
    type: str = "plix_intent"
    intent_id: str
    contract: Dict[str, Any]  # PLIx contract JSON
    postconditions: List[str]  # Expected postconditions
    preconditions: List[str]   # Required preconditions
    created_at: datetime
    valid_until: Optional[datetime]  # Intent expiration
    
class PLIxOutcomeEntity(Entity):
    """PLIx execution outcome stored as SEG entity"""
    type: str = "plix_outcome"
    outcome_id: str
    intent_id: str  # Links to PLIxIntentEntity
    achieved_postconditions: List[str]  # Which postconditions were achieved
    failed_postconditions: List[str]    # Which postconditions failed
    actual_results: Dict[str, Any]      # Actual execution results
    execution_time: datetime
    success: bool
    
class PLIxPostconditionEntity(Entity):
    """Individual postcondition stored as SEG entity"""
    type: str = "plix_postcondition"
    postcondition_id: str
    intent_id: str  # Links to PLIxIntentEntity
    condition: str  # Postcondition expression
    weight: float   # Weight for achievement scoring
    achieved: bool # Whether this postcondition was achieved
```

#### **2. Enhanced Contradiction Detection**

```python
class PLIxContradictionDetector:
    """Detect PLIx-specific contradictions"""
    
    def __init__(self, seg_graph: SEGraph):
        self.graph = seg_graph
    
    def detect_intent_violations(self) -> List[Contradiction]:
        """Detect when PLIx intents are violated"""
        violations = []
        
        # Get all PLIx intent entities
        intents = self.graph.list_entities(entity_type="plix_intent")
        
        for intent in intents:
            # Find linked outcome entities
            outcomes = self.graph.get_relations(
                source_id=intent.id,
                relation_type=RelationType.DERIVES_FROM
            )
            
            for outcome_rel in outcomes:
                outcome = self.graph.get_entity(outcome_rel.target_id)
                
                if outcome and outcome.type == "plix_outcome":
                    # Compare postconditions with actual results
                    violations.extend(
                        self._compare_postconditions(intent, outcome)
                    )
        
        return violations
    
    def _compare_postconditions(
        self,
        intent: PLIxIntentEntity,
        outcome: PLIxOutcomeEntity
    ) -> List[Contradiction]:
        """Compare expected postconditions with actual outcomes"""
        contradictions = []
        
        # Check each postcondition
        for postcondition in intent.postconditions:
            # Check if postcondition was achieved
            if postcondition not in outcome.achieved_postconditions:
                # Postcondition failed - create contradiction
                contradiction = Contradiction(
                    entity1_id=intent.id,
                    entity2_id=outcome.id,
                    contradiction_type="postcondition_failure",
                    similarity=0.0,  # Explicit failure
                    confidence=1.0,  # High confidence (explicit check)
                    explanation=f"Postcondition '{postcondition}' not achieved for intent '{intent.intent_id}'"
                )
                contradictions.append(contradiction)
        
        return contradictions
    
    def detect_postcondition_failures(
        self,
        intent_id: str
    ) -> List[Contradiction]:
        """Detect postcondition failures for a specific intent"""
        intent = self.graph.get_entity(intent_id)
        
        if not intent or intent.type != "plix_intent":
            return []
        
        # Find outcome
        outcome_relations = self.graph.get_relations(
            source_id=intent_id,
            relation_type=RelationType.DERIVES_FROM
        )
        
        failures = []
        for rel in outcome_relations:
            outcome = self.graph.get_entity(rel.target_id)
            if outcome and outcome.type == "plix_outcome":
                failures.extend(
                    self._compare_postconditions(intent, outcome)
                )
        
        return failures
```

#### **3. Integration Points**

**PLIx → SEG Integration:**
```python
# In packages/plix/src/integration/seg-contradiction-detector.ts

class PLIxSEGIntegration:
    """Integrate PLIx with SEG for contradiction detection"""
    
    def store_intent(self, intent: PLIxContract) -> str:
        """Store PLIx intent as SEG entity"""
        intent_entity = PLIxIntentEntity(
            intent_id=intent.id,
            contract=intent.to_dict(),
            postconditions=intent.contract.post,
            preconditions=intent.contract.pre,
            created_at=datetime.now(),
            valid_until=intent.intent.valid_until
        )
        
        return self.seg_graph.add_entity(intent_entity).id
    
    def store_outcome(
        self,
        intent_id: str,
        outcome: ExecutionOutcome
    ) -> str:
        """Store PLIx execution outcome as SEG entity"""
        outcome_entity = PLIxOutcomeEntity(
            outcome_id=f"outcome_{uuid.uuid4()}",
            intent_id=intent_id,
            achieved_postconditions=outcome.achieved_postconditions,
            failed_postconditions=outcome.failed_postconditions,
            actual_results=outcome.results,
            execution_time=outcome.timestamp,
            success=outcome.success
        )
        
        outcome_id = self.seg_graph.add_entity(outcome_entity).id
        
        # Create relation: intent → outcome
        relation = Relation(
            source_id=intent_id,
            target_id=outcome_id,
            relation_type=RelationType.DERIVES_FROM,
            confidence=1.0
        )
        self.seg_graph.add_relation(relation)
        
        return outcome_id
    
    def detect_violations(self) -> List[Contradiction]:
        """Detect PLIx intent violations"""
        detector = PLIxContradictionDetector(self.seg_graph)
        return detector.detect_intent_violations()
```

---

## 📊 System Analysis: SIS (Self-Improvement System)

### **Current State Assessment**

**Status:** ✅ **EXISTS** - Full implementation with 6 components

**What Exists:**
- ✅ **SISCore:** Main orchestrator with monitoring loop
- ✅ **MetaCognitiveAnalyzer:** Decision pattern analysis
- ✅ **SystemUsageAuditor:** System usage monitoring
- ✅ **PerformanceMonitor:** Performance tracking
- ✅ **GapIdentifier:** Gap identification
- ✅ **ImprovementImplementer:** Improvement implementation
- ✅ **ContinuousLearner:** Learning from improvements
- ✅ **AutonomousResearchDream:** Dream generation system

**What Works:**
```python
# Current SIS structure
class SISCore:
    def __init__(self):
        self.meta_cognitive_analyzer = MetaCognitiveAnalyzer()
        self.system_usage_auditor = SystemUsageAuditor()
        self.performance_monitor = PerformanceMonitor()
        self.gap_identifier = GapIdentifier()
        self.improvement_implementer = ImprovementImplementer()
        self.continuous_learner = ContinuousLearner()
```

**Dream Generation (AutonomousResearchDream):**
- ✅ **Dream Types:** Performance, Feature, Architecture, Consciousness, Integration, Documentation
- ✅ **Dream Patterns:** Predefined patterns for each type
- ✅ **Dream Prioritization:** Impact-based ranking
- ✅ **Dream Storage:** Stores in CMC

**What's Missing for PLIx:**
- ❌ **PLIx Intent Failure Pattern Extraction:** Extract patterns from failed PLIx intents
- ❌ **PLIx-Specific Dream Generation:** Generate dreams based on intent failures
- ❌ **Intent-Outcome Learning:** Learn from intent-outcome relationships
- ❌ **Postcondition Improvement Hypotheses:** Suggest better postconditions

---

### **PLIx Requirements Analysis**

**From Perplexity's Feedback:**
> "Observe: Failed PLIx intents → common failure patterns. Generate: Improvement hypotheses (new postconditions, guards, tactics). Validate: Run SDF-CVF gates on improvements."

**Required Capabilities:**

1. **Pattern Extraction from Failures**
   - Extract common failure patterns from CMC failure atoms
   - Identify failure modes (postcondition failures, timeout, errors)
   - Build failure pattern database

2. **Improvement Hypothesis Generation**
   - Propose new postconditions based on failures
   - Suggest additional guards
   - Recommend tactics

3. **SDF-CVF Validation**
   - Validate improvement hypotheses
   - Check for contradictions
   - Verify feasibility

4. **Intent-Outcome Learning**
   - Learn from intent-outcome relationships
   - Store patterns in CMC
   - Use for future intent improvement

---

### **SIS Enhancement Design**

#### **1. PLIx-Specific Dream Generator**

```python
class PLIxDreamGenerator:
    """Generate improvement dreams from PLIx intent failures"""
    
    def __init__(
        self,
        cmc_client,
        seg_client,
        vif_client,
        sdfcvf_client
    ):
        self.cmc = cmc_client
        self.seg = seg_client
        self.vif = vif_client
        self.sdfcvf = sdfcvf_client
        
        # Failure pattern database
        self.failure_patterns: Dict[str, FailurePattern] = {}
    
    def extract_failure_patterns(
        self,
        failed_intents: List[PLIxIntent]
    ) -> List[FailurePattern]:
        """Extract common failure patterns from failed PLIx intents"""
        patterns = []
        
        # Group failures by type
        failure_types = {}
        for intent in failed_intents:
            failure_type = self._classify_failure(intent)
            if failure_type not in failure_types:
                failure_types[failure_type] = []
            failure_types[failure_type].append(intent)
        
        # Extract patterns for each failure type
        for failure_type, intents in failure_types.items():
            pattern = self._extract_pattern(failure_type, intents)
            patterns.append(pattern)
            self.failure_patterns[pattern.id] = pattern
        
        return patterns
    
    def _classify_failure(self, intent: PLIxIntent) -> str:
        """Classify failure type"""
        outcome = self.seg.get_outcome_for_intent(intent.id)
        
        if not outcome:
            return "unknown"
        
        if outcome.failed_postconditions:
            return "postcondition_failure"
        elif outcome.timeout:
            return "timeout"
        elif outcome.error:
            return "execution_error"
        else:
            return "partial_achievement"
    
    def _extract_pattern(
        self,
        failure_type: str,
        intents: List[PLIxIntent]
    ) -> FailurePattern:
        """Extract pattern from failures"""
        # Find common postconditions that failed
        failed_postconditions = []
        for intent in intents:
            outcome = self.seg.get_outcome_for_intent(intent.id)
            if outcome:
                failed_postconditions.extend(outcome.failed_postconditions)
        
        # Count frequency
        postcondition_counts = {}
        for pc in failed_postconditions:
            postcondition_counts[pc] = postcondition_counts.get(pc, 0) + 1
        
        # Find most common failures
        common_failures = sorted(
            postcondition_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5
        
        return FailurePattern(
            id=f"pattern_{uuid.uuid4()}",
            failure_type=failure_type,
            frequency=len(intents),
            common_failures=[pc for pc, _ in common_failures],
            confidence=len(intents) / 100.0,  # Normalize
            examples=intents[:3]  # Sample intents
        )
    
    def generate_improvement_hypotheses(
        self,
        pattern: FailurePattern
    ) -> List[ImprovementHypothesis]:
        """Generate improvement hypotheses from failure pattern"""
        hypotheses = []
        
        # Hypothesis 1: Add missing postconditions
        if pattern.failure_type == "postcondition_failure":
            hypotheses.append(
                ImprovementHypothesis(
                    type="add_postcondition",
                    description=f"Add postcondition to prevent '{pattern.common_failures[0]}' failures",
                    proposed_postcondition=self._suggest_postcondition(pattern),
                    confidence=0.7
                )
            )
        
        # Hypothesis 2: Add guards
        hypotheses.append(
            ImprovementHypothesis(
                type="add_guard",
                description=f"Add guard to prevent {pattern.failure_type}",
                proposed_guard=self._suggest_guard(pattern),
                confidence=0.6
            )
        )
        
        # Hypothesis 3: Improve tactics
        hypotheses.append(
            ImprovementHypothesis(
                type="improve_tactic",
                description=f"Improve execution tactic for {pattern.failure_type}",
                proposed_tactic=self._suggest_tactic(pattern),
                confidence=0.5
            )
        )
        
        return hypotheses
    
    def validate_hypothesis(
        self,
        hypothesis: ImprovementHypothesis
    ) -> ValidationResult:
        """Validate improvement hypothesis using SDF-CVF"""
        # Run SDF-CVF gates
        validation = self.sdfcvf.validate_change(
            change=hypothesis.to_change(),
            context=self._get_context(hypothesis)
        )
        
        return ValidationResult(
            valid=validation.passes,
            confidence=validation.confidence,
            issues=validation.issues,
            recommendations=validation.recommendations
        )
    
    def _suggest_postcondition(
        self,
        pattern: FailurePattern
    ) -> str:
        """Suggest new postcondition based on pattern"""
        # Analyze common failures and suggest prevention
        common_failure = pattern.common_failures[0]
        
        # Generate postcondition that would prevent this failure
        # This is a placeholder - actual implementation would use LLM
        return f"prevent_{common_failure}_failure == true"
    
    def _suggest_guard(self, pattern: FailurePattern) -> str:
        """Suggest guard based on pattern"""
        return f"check_{pattern.failure_type}_prevention == true"
    
    def _suggest_tactic(self, pattern: FailurePattern) -> str:
        """Suggest tactic based on pattern"""
        return f"use_{pattern.failure_type}_resilient_strategy"
```

#### **2. Integration with SIS**

```python
# Extend SISCore with PLIx-specific capabilities

class PLIxSISExtension:
    """PLIx-specific extension for SIS"""
    
    def __init__(self, sis_core: SISCore):
        self.sis = sis_core
        self.plix_dream_generator = PLIxDreamGenerator(
            cmc_client=self.sis.cmc_client,
            seg_client=self.sis.seg_client,
            vif_client=self.sis.vif_client,
            sdfcvf_client=self.sis.sdfcvf_client
        )
    
    def learn_from_plix_failures(self):
        """Learn from PLIx intent failures"""
        # Get failed intents from CMC
        failed_intents = self._get_failed_intents()
        
        # Extract patterns
        patterns = self.plix_dream_generator.extract_failure_patterns(
            failed_intents
        )
        
        # Generate improvement hypotheses
        for pattern in patterns:
            hypotheses = self.plix_dream_generator.generate_improvement_hypotheses(
                pattern
            )
            
            # Validate hypotheses
            for hypothesis in hypotheses:
                validation = self.plix_dream_generator.validate_hypothesis(
                    hypothesis
                )
                
                if validation.valid:
                    # Store in SIS for implementation
                    self.sis.improvement_implementer.plan_improvements().append(
                        hypothesis.to_improvement()
                    )
    
    def _get_failed_intents(self) -> List[PLIxIntent]:
        """Get failed PLIx intents from CMC"""
        # Query CMC for failed intent atoms
        failed_atoms = self.sis.cmc_client.query(
            tags=["plix_intent", "status:failed"]
        )
        
        return [PLIxIntent.from_atom(atom) for atom in failed_atoms]
```

---

## 🎯 Implementation Plan

### **Phase 1: SEG Enhancement (Week 3)**

**Goal:** Add PLIx-specific contradiction detection

**Tasks:**
1. **Add PLIx Entity Types** (Day 1-2)
   - Create `PLIxIntentEntity`, `PLIxOutcomeEntity`, `PLIxPostconditionEntity`
   - Add to SEG models
   - Update graph schema

2. **Implement PLIx Contradiction Detector** (Day 3-4)
   - Create `PLIxContradictionDetector` class
   - Implement `detect_intent_violations()`
   - Implement `detect_postcondition_failures()`
   - Add `_compare_postconditions()` method

3. **PLIx → SEG Integration** (Day 5)
   - Create `PLIxSEGIntegration` class
   - Implement `store_intent()` and `store_outcome()`
   - Create intent → outcome relations
   - Test end-to-end flow

4. **Tests** (Day 6-7)
   - Test intent violation detection
   - Test postcondition failure detection
   - Test contradiction creation
   - Integration tests

**Deliverables:**
- `packages/seg/models.py` (updated with PLIx entities)
- `packages/seg/plix_contradiction_detector.py` (new)
- `packages/plix/src/integration/seg-contradiction-detector.ts` (new)
- `packages/seg/tests/test_plix_contradiction.py` (new)

---

### **Phase 2: SIS Enhancement (Week 4)**

**Goal:** Extend SIS with PLIx-specific dream generation

**Tasks:**
1. **Create PLIx Dream Generator** (Day 1-3)
   - Create `PLIxDreamGenerator` class
   - Implement `extract_failure_patterns()`
   - Implement `generate_improvement_hypotheses()`
   - Implement `validate_hypothesis()`

2. **Integrate with SIS** (Day 4-5)
   - Create `PLIxSISExtension` class
   - Integrate with `SISCore`
   - Add `learn_from_plix_failures()` method
   - Connect to improvement implementer

3. **Pattern Database** (Day 6)
   - Build failure pattern database
   - Store patterns in CMC
   - Enable pattern retrieval

4. **Tests** (Day 7)
   - Test pattern extraction
   - Test hypothesis generation
   - Test validation
   - Integration tests

**Deliverables:**
- `packages/sis/plix_dream_generator.py` (new)
- `packages/sis/plix_sis_extension.py` (new)
- `packages/plix/src/integration/sis-dream-generator.ts` (new)
- `packages/sis/tests/test_plix_dream_generator.py` (new)

---

## 📋 Success Criteria

### **SEG Enhancement:**
- ✅ Can store PLIx intents as SEG entities
- ✅ Can store PLIx outcomes as SEG entities
- ✅ Can detect intent violations
- ✅ Can detect postcondition failures
- ✅ Creates contradictions when violations detected
- ✅ All tests passing

### **SIS Enhancement:**
- ✅ Can extract failure patterns from failed intents
- ✅ Can generate improvement hypotheses
- ✅ Can validate hypotheses with SDF-CVF
- ✅ Can learn from intent-outcome relationships
- ✅ Stores patterns in CMC
- ✅ All tests passing

---

## 🔗 Integration Points

### **SEG ↔ PLIx Integration:**
```
PLIx Intent → SEG Intent Entity
PLIx Outcome → SEG Outcome Entity
SEG Contradiction → PLIx Violation Detection
```

### **SIS ↔ PLIx Integration:**
```
PLIx Failures → SIS Pattern Extraction
SIS Patterns → PLIx Improvement Hypotheses
SIS Validation → PLIx Hypothesis Validation
```

---

## 💡 Key Insights

1. **SEG Foundation is Solid:** Basic contradiction detection exists, just needs PLIx-specific enhancement
2. **SIS Already Has Dream Generation:** Just needs PLIx-specific pattern extraction
3. **Additive Changes:** Both enhancements are additive, not rewrites
4. **Integration via Adapters:** PLIx integrates via adapter layers, not direct system modifications

---

**Status:** ✅ **RESEARCH COMPLETE - READY FOR IMPLEMENTATION**  
**Next:** Begin Phase 1 (SEG Enhancement) implementation

