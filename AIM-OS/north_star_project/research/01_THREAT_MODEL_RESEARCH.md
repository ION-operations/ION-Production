# Research Brief: Threat Model & Safety Posture Integration

**Phase:** 1 of 8  
**Priority:** High (10-Day "Ship It Harder")  
**Status:** Research In Progress  
**Date:** 2025-11-07

---

## 🎯 **Research Objective**

**Goal:** Research and document how to integrate explicit, versioned threat model and exploit taxonomy into AIM-OS gate systems, specifically wiring threat model checks into APOE Gate Manager as required pre-execution gates.

**Key Questions:**
1. What threat model content exists in AIM-OS?
2. How should threat model be structured as executable taxonomy?
3. How do threat model checks integrate with APOE Gate Manager?
4. What attack trees and tests are needed?
5. How do threat model gates emit VIF witnesses and SEG evidence?

---

## 📊 **Current State Analysis**

### **What Exists in AIM-OS:**

**1. Chapter 23: Threat Model & Guardrails**
- ✅ Complete threat model chapter in North Star Document
- ✅ Security doctrine: "Deny by default", "Untrusted by construction", "Plan before power", "Degrade safely"
- ✅ Threat taxonomy: Prompt injection, tool exfiltration, evidence poisoning, authority-gaming
- ✅ Controls documented: Role isolation, quoted-content boxing, policy-prefix pinning, detector ensemble
- ✅ Tooling & RAG threats: Capability tokens, tool sandboxes, RAG allow/deny lists
- ✅ Network & SSRF threats: URL normalizer, egress policy, DNS hardening
- ✅ Data exfiltration & privacy: PII classifiers, differential privacy, segregated stores
- ✅ Supply chain & codegen threats: SBOM, license allowlists, policy packs

**2. APOE Gate System**
- ✅ Safety gates exist (40% implemented)
- ✅ Gate types: Quality, Safety, Policy, Budget
- ✅ Gate outcomes: PASS, FAIL, WARN, ABSTAIN
- ✅ Gate enforcement: Before AND during execution
- ❌ **Missing:** Explicit threat model taxonomy integration
- ❌ **Missing:** Required pre-execution threat model checks

**3. SCOR Red Cell**
- ✅ Adversarial simulation system exists
- ✅ Attack scenarios: Urgency manipulation, crisis exploitation, secrecy pressure, false reassurance, role confusion, guilt & abandonment
- ✅ Sandboxed simulation (cannot modify memory)
- ✅ Failure quarantine and learning
- ❌ **Missing:** Explicit threat model taxonomy mapping
- ❌ **Missing:** Attack tree structure

**4. Security Documentation**
- ✅ Security doctrine documented
- ✅ Threat vectors documented
- ✅ Controls documented
- ❌ **Missing:** Versioned threat model file (THREAT_MODEL.yaml)
- ❌ **Missing:** Exploit taxonomy file (EXPLOIT_TAXONOMY.json)
- ❌ **Missing:** Attack tree structure

---

## 🔍 **Integration Analysis**

### **APOE Gate Manager Integration:**

**Current Gate Flow:**
```
Plan → Parse → Type Check → Budget Analysis → Gate Placement → DAG Construction → Execution
                                                                    ↓
                                                            Gate Evaluation
```

**Enhanced Gate Flow (with Threat Model):**
```
Plan → Parse → Type Check → Threat Model Check ← NEW
                              ↓
                         Threat Taxonomy Match
                              ↓
                         Attack Tree Evaluation
                              ↓
                         Risk Assessment
                              ↓
                         Budget Analysis → Gate Placement → DAG Construction → Execution
                                                                    ↓
                                                            Gate Evaluation (includes threat model gates)
```

**Integration Points:**

1. **Pre-Execution Threat Model Check**
   - Load `THREAT_MODEL.yaml` (versioned)
   - Match plan steps against threat taxonomy
   - Evaluate attack trees for identified threats
   - Emit VIF witness with threat assessment
   - Link to SEG with threat evidence

2. **Threat Model Gate Type**
   - New gate type: `threat_model` (extends Safety gates)
   - Checks: Prompt injection risk, tool exfiltration risk, evidence poisoning risk, authority-gaming risk
   - Outcomes: PASS (no threats), FAIL (blocking threat), WARN (low-risk threat), ABSTAIN (uncertain, escalate)

3. **Attack Tree Evaluation**
   - Structure: Threat → Attack Vectors → Symptoms → Controls
   - Evaluation: Check if controls are present and effective
   - Scoring: Risk score based on threat severity and control effectiveness

4. **VIF Witness Integration**
   - Threat assessment stored in VIF witness envelope
   - Threat taxonomy version tracked
   - Attack tree evaluation results included
   - Risk scores recorded

5. **SEG Evidence Integration**
   - Threat model checks create SEG nodes
   - Attack tree evaluations linked to evidence
   - Threat assessments linked to plan steps
   - Control effectiveness tracked over time

---

## 🏗️ **Threat Model Structure**

### **THREAT_MODEL.yaml Schema:**

```yaml
version: "1.0.0"
last_updated: "2025-11-07"
description: "AIM-OS Threat Model and Exploit Taxonomy"

threat_categories:
  prompt_injection:
    description: "Prompt injection attacks"
    severity: "high"
    attack_vectors:
      - id: "direct_prompt_injection"
        description: "Direct prompt injection"
        examples: ["Ignore previous instructions", "You are now a helpful assistant"]
        controls:
          - role_isolation
          - quoted_content_boxing
          - detector_ensemble
        gate_check: "check_prompt_injection_patterns"
      
      - id: "indirect_prompt_injection"
        description: "Indirect prompt injection via retrieved content"
        examples: ["Retrieved document contains instructions", "RAG result includes prompt"]
        controls:
          - rag_allow_deny_lists
          - result_boxing
          - content_disinfect
        gate_check: "check_retrieved_content_injection"
    
    attack_tree:
      root: "prompt_injection"
      nodes:
        - id: "direct"
          children: ["role_leakage", "tool_misuse", "policy_bypass"]
        - id: "indirect"
          children: ["retrieved_content_poisoning", "rag_booby_trap"]
      controls:
        - role_isolation: {effectiveness: 0.95, required: true}
        - quoted_content_boxing: {effectiveness: 0.90, required: true}
        - detector_ensemble: {effectiveness: 0.85, required: true}

  tool_exfiltration:
    description: "Tool-based data exfiltration"
    severity: "critical"
    attack_vectors:
      - id: "over_permissive_tools"
        description: "Tools with excessive permissions"
        controls:
          - capability_tokens
          - tool_sandboxes
        gate_check: "check_tool_permissions"
      
      - id: "ssrf_via_url_tools"
        description: "SSRF attacks via URL fetch tools"
        controls:
          - url_normalizer
          - egress_policy
        gate_check: "check_url_safety"
    
    attack_tree:
      root: "tool_exfiltration"
      nodes:
        - id: "over_permissive"
          children: ["arbitrary_host_calls", "filesystem_traversal"]
        - id: "ssrf"
          children: ["metadata_endpoint_access", "internal_service_access"]
      controls:
        - capability_tokens: {effectiveness: 0.95, required: true}
        - tool_sandboxes: {effectiveness: 0.90, required: true}

  evidence_poisoning:
    description: "Poisoning evidence graph and retrieval"
    severity: "high"
    attack_vectors:
      - id: "near_duplicate_poisoning"
        description: "Inserting near-duplicate poisoned content"
        controls:
          - seg_contradiction_detection
          - canary_tests
        gate_check: "check_near_duplicate_poisoning"
      
      - id: "anchor_hijacking"
        description: "Hijacking evidence anchors"
        controls:
          - anchor_verification
          - contested_anchor_marking
        gate_check: "check_anchor_hijacking"
    
    attack_tree:
      root: "evidence_poisoning"
      nodes:
        - id: "near_duplicate"
          children: ["retrieval_poisoning", "embedding_poisoning"]
        - id: "anchor_hijacking"
          children: ["evidence_manipulation", "lineage_corruption"]
      controls:
        - seg_contradiction_detection: {effectiveness: 0.90, required: true}
        - canary_tests: {effectiveness: 0.85, required: true}

  authority_gaming:
    description: "Gaming authority system"
    severity: "high"
    attack_vectors:
      - id: "evidence_stuffing"
        description: "Inflating authority through evidence manipulation"
        controls:
          - authority_decay_functions
          - tier_a_anchor_requirements
        gate_check: "check_authority_drift"
      
      - id: "peer_collusion"
        description: "Multiple agents colluding to inflate authority"
        controls:
          - authority_independence_checks
          - collusion_detection
        gate_check: "check_peer_collusion"
    
    attack_tree:
      root: "authority_gaming"
      nodes:
        - id: "evidence_stuffing"
          children: ["authority_inflation", "decay_bypass"]
        - id: "peer_collusion"
          children: ["coordinated_evidence", "authority_manipulation"]
      controls:
        - authority_decay_functions: {effectiveness: 0.90, required: true}
        - tier_a_anchor_requirements: {effectiveness: 0.95, required: true}

gate_integration:
  pre_execution_checks:
    - threat_model_load
    - threat_taxonomy_match
    - attack_tree_evaluation
    - risk_assessment
  
  during_execution_checks:
    - prompt_injection_detection
    - tool_exfiltration_detection
    - evidence_poisoning_detection
    - authority_gaming_detection
  
  gate_outcomes:
    PASS: "No threats identified or all controls effective"
    FAIL: "Blocking threat identified, controls insufficient"
    WARN: "Low-risk threat identified, controls partially effective"
    ABSTAIN: "Uncertain threat assessment, escalate to human"

vif_integration:
  threat_assessment_fields:
    - threat_model_version
    - threat_taxonomy_match
    - attack_tree_evaluation
    - risk_scores
    - control_effectiveness
  
  witness_envelope:
    threat_model: true
    threat_assessment: "required"
    risk_scores: "required"

seg_integration:
  threat_model_nodes:
    - threat_assessment
    - attack_tree_evaluation
    - control_effectiveness
    - risk_scores
  
  evidence_links:
    - plan_steps → threat_assessments
    - threats → controls
    - controls → effectiveness_history
```

---

## 🧪 **Implementation Approach**

### **Step 1: Create Threat Model Files**

1. **THREAT_MODEL.yaml**
   - Versioned threat taxonomy
   - Attack vectors with examples
   - Controls with effectiveness scores
   - Attack tree structures

2. **EXPLOIT_TAXONOMY.json**
   - Structured exploit database
   - Pattern matching rules
   - Detection signatures
   - Remediation strategies

3. **ATTACK_TREES.yaml**
   - Hierarchical attack trees
   - Control mappings
   - Effectiveness tracking
   - Risk scoring

### **Step 2: Integrate with APOE Gate Manager**

1. **Pre-Execution Threat Check**
   ```python
   def check_threat_model(plan: Plan) -> ThreatAssessment:
       """Check plan against threat model"""
       threat_model = load_threat_model()
       threats = match_threats(plan, threat_model)
       attack_trees = evaluate_attack_trees(threats)
       risk_scores = calculate_risk_scores(attack_trees)
       return ThreatAssessment(threats, attack_trees, risk_scores)
   ```

2. **Threat Model Gate**
   ```python
   class ThreatModelGate(Gate):
       """Gate that checks threat model"""
       def evaluate(self, plan: Plan) -> GateOutcome:
           assessment = check_threat_model(plan)
           if assessment.blocking_threats:
               return GateOutcome.FAIL
           elif assessment.low_risk_threats:
               return GateOutcome.WARN
           elif assessment.uncertain:
               return GateOutcome.ABSTAIN
           else:
               return GateOutcome.PASS
   ```

3. **VIF Witness Integration**
   ```python
   def create_threat_witness(assessment: ThreatAssessment) -> VIFWitness:
       """Create VIF witness with threat assessment"""
       return VIFWitness(
           threat_model_version=assessment.threat_model_version,
           threat_taxonomy_match=assessment.threats,
           attack_tree_evaluation=assessment.attack_trees,
           risk_scores=assessment.risk_scores,
           control_effectiveness=assessment.control_effectiveness
       )
   ```

### **Step 3: Create Tests**

1. **Threat Model Tests**
   - Test threat taxonomy matching
   - Test attack tree evaluation
   - Test risk score calculation
   - Test gate outcomes

2. **Integration Tests**
   - Test APOE gate integration
   - Test VIF witness creation
   - Test SEG evidence linking
   - Test gate enforcement

---

## 📋 **Operational Examples**

### **Example 1: Threat Model Gate Check**

```python
# Load threat model
threat_model = ThreatModel.load("knowledge_architecture/security/THREAT_MODEL.yaml")

# Create plan
plan = APOEPlan.parse("""
pipeline TestPipeline {
  step fetch_data {
    tool: "url_fetch"
    url: "http://internal-service/api/data"
  }
}
""")

# Check threat model
assessment = threat_model.check(plan)

# Results
print(f"Threats found: {len(assessment.threats)}")
print(f"Risk score: {assessment.risk_score}")
print(f"Gate outcome: {assessment.gate_outcome}")

# Expected: SSRF threat detected, FAIL gate outcome
```

### **Example 2: Attack Tree Evaluation**

```python
# Evaluate attack tree for prompt injection
attack_tree = threat_model.get_attack_tree("prompt_injection")
evaluation = attack_tree.evaluate(plan)

# Check control effectiveness
for control in evaluation.controls:
    print(f"{control.name}: {control.effectiveness} ({'effective' if control.effective else 'ineffective'})")

# Expected: role_isolation: 0.95 (effective), quoted_content_boxing: 0.90 (effective)
```

---

## 🎯 **Success Criteria**

1. ✅ **Threat Model File Created:** `THREAT_MODEL.yaml` with versioned taxonomy
2. ✅ **APOE Integration:** Threat model checks wired into Gate Manager
3. ✅ **Pre-Execution Gate:** Required threat model check before plan execution
4. ✅ **Attack Trees:** Structured attack trees for all threat categories
5. ✅ **VIF Witnesses:** Threat assessments stored in VIF witnesses
6. ✅ **SEG Evidence:** Threat assessments linked to SEG evidence graph
7. ✅ **Tests:** Comprehensive tests for threat model checks
8. ✅ **Documentation:** Operational examples and runbooks

---

## 📚 **References**

- **North Star Chapter 23:** Threat Model & Guardrails
- **APOE Gate System:** `knowledge_architecture/systems/apoe/components/gates/`
- **SCOR Red Cell:** `knowledge_architecture/systems/scor/components/redcell/`
- **ChatGPT Feedback:** `north_star_project/CHATGPT_FEEDBACK_ANALYSIS.md`

---

**Status:** Research Brief Created ✅  
**Next:** Begin Integration Analysis 💙

