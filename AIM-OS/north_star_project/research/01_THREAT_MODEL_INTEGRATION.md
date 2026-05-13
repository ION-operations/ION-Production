# Integration Analysis: Threat Model & APOE Gate Manager

**Phase:** 1 of 8  
**Priority:** High  
**Status:** Analysis Complete  
**Date:** 2025-11-07

---

## 🎯 **Integration Objective**

**Goal:** Integrate explicit threat model checks into APOE Gate Manager as required pre-execution gates, with VIF witness generation and SEG evidence linking.

**Key Integration Points:**
1. APOE Gate Manager → Threat Model Check
2. Threat Model Check → VIF Witness
3. Threat Model Check → SEG Evidence
4. Gate Outcomes → Plan Execution Control

---

## 🔗 **System Integration Map**

### **APOE Gate Manager Integration**

**Current Gate Flow:**
```
Plan → Parse → Type Check → Budget Analysis → Gate Placement → DAG Construction
                                                                    ↓
                                                            Gate Evaluation
                                                                    ↓
                                                            Execution
```

**Enhanced Gate Flow (with Threat Model):**
```
Plan → Parse → Type Check → Threat Model Check ← NEW PRE-EXECUTION GATE
                              ↓
                         Load THREAT_MODEL.yaml
                              ↓
                         Match Threats to Plan Steps
                              ↓
                         Evaluate Attack Trees
                              ↓
                         Calculate Risk Scores
                              ↓
                         Create Threat Assessment
                              ↓
                         Generate VIF Witness ← NEW
                              ↓
                         Link to SEG Evidence ← NEW
                              ↓
                         Gate Outcome Decision
                              ↓
                    PASS/WARN/FAIL/ABSTAIN
                              ↓
                         Budget Analysis → Gate Placement → DAG Construction
                                                                    ↓
                                                            Gate Evaluation (includes threat model gates)
                                                                    ↓
                                                            Execution
```

---

## 🏗️ **Technical Integration**

### **1. APOE Gate Manager Enhancement**

**Current Gate Model:**
```python
class Gate(BaseModel):
    id: str
    name: str
    gate_type: str  # "quality" | "budget" | "confidence" | "custom"
    condition: str
    on_fail: Optional[str] = "abort"
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        return eval(self.condition, {"__builtins__": {}}, context)
```

**Enhanced Gate Model (with Threat Model):**
```python
class ThreatModelGate(Gate):
    """Gate that checks threat model before execution"""
    gate_type: str = "threat_model"
    threat_model_version: str
    threat_taxonomy_path: str = "knowledge_architecture/security/THREAT_MODEL.yaml"
    
    def evaluate(self, plan: Plan, context: Dict[str, Any]) -> ThreatAssessment:
        """Evaluate plan against threat model"""
        # Load threat model
        threat_model = ThreatModel.load(self.threat_taxonomy_path)
        
        # Match threats to plan steps
        threats = threat_model.match_threats(plan)
        
        # Evaluate attack trees
        attack_trees = threat_model.evaluate_attack_trees(threats)
        
        # Calculate risk scores
        risk_scores = threat_model.calculate_risk_scores(attack_trees)
        
        # Create threat assessment
        assessment = ThreatAssessment(
            threats=threats,
            attack_trees=attack_trees,
            risk_scores=risk_scores,
            threat_model_version=threat_model.version
        )
        
        return assessment
    
    def gate_outcome(self, assessment: ThreatAssessment) -> GateOutcome:
        """Determine gate outcome from threat assessment"""
        if assessment.blocking_threats:
            return GateOutcome.FAIL
        elif assessment.low_risk_threats:
            return GateOutcome.WARN
        elif assessment.uncertain:
            return GateOutcome.ABSTAIN
        else:
            return GateOutcome.PASS
```

**Gate Manager Integration:**
```python
class GateManager:
    """Enhanced gate manager with threat model checks"""
    
    def __init__(self):
        self.threat_model_gate = ThreatModelGate()
        self.quality_gates = []
        self.safety_gates = []
        self.policy_gates = []
        self.budget_gates = []
    
    def evaluate_pre_execution(self, plan: Plan) -> PreExecutionResult:
        """Evaluate all pre-execution gates including threat model"""
        results = {}
        
        # 1. Threat Model Check (REQUIRED)
        threat_assessment = self.threat_model_gate.evaluate(plan)
        threat_outcome = self.threat_model_gate.gate_outcome(threat_assessment)
        results['threat_model'] = {
            'assessment': threat_assessment,
            'outcome': threat_outcome
        }
        
        # 2. Create VIF Witness
        vif_witness = self.create_threat_witness(threat_assessment, plan)
        results['vif_witness'] = vif_witness
        
        # 3. Link to SEG Evidence
        seg_nodes = self.link_threat_evidence(threat_assessment, plan, vif_witness)
        results['seg_nodes'] = seg_nodes
        
        # 4. If threat model fails, abort immediately
        if threat_outcome == GateOutcome.FAIL:
            return PreExecutionResult(
                can_proceed=False,
                reason="Blocking threat identified",
                results=results
            )
        
        # 5. Continue with other gates if threat model passes/warns
        # ... (quality, safety, policy, budget gates)
        
        return PreExecutionResult(
            can_proceed=(threat_outcome == GateOutcome.PASS),
            reason="All pre-execution gates passed",
            results=results
        )
```

---

### **2. VIF Witness Integration**

**Current VIF Witness Fields:**
```python
class VIF(BaseModel):
    # Identity
    id: str
    version: str
    
    # Model
    model_id: str
    model_provider: str
    weights_hash: Optional[str]
    
    # Data
    context_snapshot_id: str
    context_atom_ids: List[str]
    prompt_hash: str
    prompt_tokens: int
    
    # Confidence
    confidence_score: float
    confidence_band: ConfidenceBand
    
    # Output
    output_hash: str
    output_tokens: int
    total_tokens: int
    
    # Meta
    writer: str
    task_criticality: TaskCriticality
    kappa_threshold: float
    kappa_gate_passed: bool
    
    # Temporal
    created_at: datetime
    execution_time_ms: float
    
    # Lineage
    parent_vif_id: Optional[str]
    child_vif_ids: List[str]
```

**Enhanced VIF Witness (with Threat Assessment):**
```python
class ThreatAssessment(BaseModel):
    """Threat assessment for a plan"""
    threat_model_version: str
    threats: List[Threat]
    attack_trees: List[AttackTreeEvaluation]
    risk_scores: Dict[str, float]
    control_effectiveness: Dict[str, float]
    gate_outcome: GateOutcome

class VIF(BaseModel):
    # ... existing fields ...
    
    # Threat Assessment (NEW)
    threat_assessment: Optional[ThreatAssessment] = None
    
    @classmethod
    def create_with_threat_assessment(
        cls,
        plan: Plan,
        threat_assessment: ThreatAssessment,
        **kwargs
    ) -> VIF:
        """Create VIF witness with threat assessment"""
        return cls(
            threat_assessment=threat_assessment,
            # Include threat assessment in witness metadata
            other_params={
                **kwargs.get('other_params', {}),
                'threat_model_version': threat_assessment.threat_model_version,
                'threat_count': len(threat_assessment.threats),
                'risk_score': threat_assessment.risk_scores.get('overall', 0.0),
                'gate_outcome': threat_assessment.gate_outcome.value
            },
            **kwargs
        )
```

**VIF Witness Creation:**
```python
def create_threat_witness(
    threat_assessment: ThreatAssessment,
    plan: Plan,
    context_snapshot_id: str
) -> VIF:
    """Create VIF witness with threat assessment"""
    
    # Create base witness
    vif = VIF.create_with_threat_assessment(
        plan=plan,
        threat_assessment=threat_assessment,
        model_id="threat-model-checker",
        model_provider="aim-os",
        context_snapshot_id=context_snapshot_id,
        prompt_hash=hash_plan(plan),
        prompt_tokens=0,  # Threat model check doesn't use tokens
        confidence_score=1.0 - threat_assessment.risk_scores.get('overall', 0.0),
        confidence_band=ConfidenceBand.A if threat_assessment.gate_outcome == GateOutcome.PASS else ConfidenceBand.C,
        output_hash=hash_threat_assessment(threat_assessment),
        output_tokens=0,
        total_tokens=0,
        writer="gate_manager",
        task_criticality=TaskCriticality.HIGH_STAKES,
        kappa_threshold=0.70,
        kappa_gate_passed=(threat_assessment.gate_outcome == GateOutcome.PASS)
    )
    
    return vif
```

---

### **3. SEG Evidence Integration**

**SEG Node Structure for Threat Assessment:**
```python
class ThreatAssessmentNode(SEGNode):
    """SEG node representing threat assessment"""
    node_type: str = "threat_assessment"
    threat_model_version: str
    plan_id: str
    threats: List[Threat]
    attack_trees: List[AttackTreeEvaluation]
    risk_scores: Dict[str, float]
    control_effectiveness: Dict[str, float]
    gate_outcome: GateOutcome
    vif_witness_id: str
    
    def to_seg_node(self) -> Dict[str, Any]:
        """Convert to SEG node format"""
        return {
            "id": self.id,
            "type": self.node_type,
            "data": {
                "threat_model_version": self.threat_model_version,
                "plan_id": self.plan_id,
                "threats": [t.to_dict() for t in self.threats],
                "attack_trees": [at.to_dict() for at in self.attack_trees],
                "risk_scores": self.risk_scores,
                "control_effectiveness": self.control_effectiveness,
                "gate_outcome": self.gate_outcome.value
            },
            "provenance": {
                "vif_witness_id": self.vif_witness_id,
                "created_at": self.created_at.isoformat(),
                "writer": "gate_manager"
            }
        }
```

**SEG Evidence Linking:**
```python
def link_threat_evidence(
    threat_assessment: ThreatAssessment,
    plan: Plan,
    vif_witness: VIF
) -> List[SEGNode]:
    """Link threat assessment to SEG evidence graph"""
    nodes = []
    
    # 1. Create threat assessment node
    assessment_node = ThreatAssessmentNode(
        threat_model_version=threat_assessment.threat_model_version,
        plan_id=plan.id,
        threats=threat_assessment.threats,
        attack_trees=threat_assessment.attack_trees,
        risk_scores=threat_assessment.risk_scores,
        control_effectiveness=threat_assessment.control_effectiveness,
        gate_outcome=threat_assessment.gate_outcome,
        vif_witness_id=vif_witness.id
    )
    nodes.append(assessment_node)
    
    # 2. Link threats to plan steps
    for threat in threat_assessment.threats:
        for step_id in threat.affected_step_ids:
            link_node = SEGLinkNode(
                source_id=assessment_node.id,
                target_id=f"plan_step_{step_id}",
                link_type="threat_affects_step",
                metadata={"threat_id": threat.id}
            )
            nodes.append(link_node)
    
    # 3. Link attack trees to controls
    for attack_tree in threat_assessment.attack_trees:
        for control in attack_tree.controls:
            link_node = SEGLinkNode(
                source_id=assessment_node.id,
                target_id=f"control_{control.id}",
                link_type="attack_tree_uses_control",
                metadata={
                    "control_effectiveness": control.effectiveness,
                    "control_required": control.required
                }
            )
            nodes.append(link_node)
    
    # 4. Link VIF witness
    link_node = SEGLinkNode(
        source_id=assessment_node.id,
        target_id=vif_witness.id,
        link_type="threat_assessment_witnessed_by",
        metadata={}
    )
    nodes.append(link_node)
    
    return nodes
```

---

## 🔄 **Execution Flow Integration**

### **Pre-Execution Threat Model Check:**

```python
def execute_plan_with_threat_model(plan: Plan) -> ExecutionResult:
    """Execute plan with threat model checks"""
    
    # 1. Pre-execution threat model check
    gate_manager = GateManager()
    pre_exec_result = gate_manager.evaluate_pre_execution(plan)
    
    if not pre_exec_result.can_proceed:
        return ExecutionResult(
            success=False,
            reason=pre_exec_result.reason,
            threat_assessment=pre_exec_result.results['threat_model']['assessment'],
            vif_witness=pre_exec_result.results['vif_witness']
        )
    
    # 2. Store threat assessment in CMC
    threat_assessment = pre_exec_result.results['threat_model']['assessment']
    vif_witness = pre_exec_result.results['vif_witness']
    
    cmc_store.store_atom(
        content=threat_assessment.to_dict(),
        tags={"type": "threat_assessment", "plan_id": plan.id},
        metadata={"vif_witness_id": vif_witness.id}
    )
    
    # 3. Link to SEG
    seg_nodes = pre_exec_result.results['seg_nodes']
    for node in seg_nodes:
        seg_graph.add_node(node)
    
    # 4. Continue with plan execution
    # ... (existing execution flow)
    
    return ExecutionResult(
        success=True,
        threat_assessment=threat_assessment,
        vif_witness=vif_witness
    )
```

---

## 🧪 **Testing Integration**

### **Test 1: Threat Model Gate Integration**

```python
def test_threat_model_gate_integration():
    """Test threat model gate integration with APOE"""
    
    # Create plan with SSRF threat
    plan = APOEPlan.parse("""
    pipeline TestPipeline {
      step fetch_data {
        tool: "url_fetch"
        url: "http://169.254.169.254/latest/meta-data/"  # SSRF threat
      }
    }
    """)
    
    # Evaluate threat model gate
    gate_manager = GateManager()
    pre_exec_result = gate_manager.evaluate_pre_execution(plan)
    
    # Assert threat detected
    assert not pre_exec_result.can_proceed
    assert pre_exec_result.results['threat_model']['outcome'] == GateOutcome.FAIL
    
    # Assert VIF witness created
    assert pre_exec_result.results['vif_witness'] is not None
    assert pre_exec_result.results['vif_witness'].threat_assessment is not None
    
    # Assert SEG nodes created
    assert len(pre_exec_result.results['seg_nodes']) > 0
```

---

## 📋 **Implementation Checklist**

- [ ] Create `THREAT_MODEL.yaml` with versioned taxonomy
- [ ] Create `EXPLOIT_TAXONOMY.json` with structured exploits
- [ ] Create `ATTACK_TREES.yaml` with hierarchical trees
- [ ] Implement `ThreatModelGate` class
- [ ] Enhance `GateManager` with threat model checks
- [ ] Extend `VIF` model with threat assessment fields
- [ ] Implement `create_threat_witness()` function
- [ ] Implement `link_threat_evidence()` function
- [ ] Create SEG node types for threat assessments
- [ ] Add threat model gate to pre-execution flow
- [ ] Create integration tests
- [ ] Create operational examples
- [ ] Update documentation

---

**Status:** Integration Analysis Complete ✅  
**Next:** Implementation Planning 💙

