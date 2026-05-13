# Verifier: Evidence Replayer Implementation Plan

**Date:** 2025-01-27  
**Status:** 📋 **PLANNING**  
**Goal:** Create verifier that re-executes pure constraints and checks hash equality and signatures

---

## 🎯 **OBJECTIVE**

Implement verifier with:
1. **Hash chain verification** (DAG structure, parent hash validation)
2. **Signature verification** (cryptographic signature validation)
3. **Pure constraint replay** (deterministic constraint re-evaluation)
4. **Evidence completeness** (all postconditions supported by evidence)

---

## 📐 **ARCHITECTURE**

### **Core Components**

```
verifier/
├── src/
│   ├── lib.rs                    # Main library
│   ├── hash_chain.rs             # Hash chain verification
│   ├── signature.rs              # Signature verification
│   ├── constraint_replay.rs     # Pure constraint replay
│   ├── evidence_completeness.rs  # Evidence completeness check
│   └── verifier.rs              # Main verifier
├── tests/
│   ├── test_hash_chain.rs
│   ├── test_signature.rs
│   ├── test_constraint_replay.rs
│   └── test_evidence_completeness.rs
└── examples/
    └── room_verification.rs      # Meeting-room verification
```

---

## 🔧 **IMPLEMENTATION SPECIFICATIONS**

### **1. Hash Chain Verification**

**Hash Chain Check:**
```rust
pub fn verify_hash_chain(
    evidence_dag: &EvidenceDAG
) -> Result<(), VerificationError> {
    let mut seen_ids = HashSet::new();
    
    for node in &evidence_dag.nodes {
        // Check ID uniqueness
        if seen_ids.contains(&node.id) {
            return Err(VerificationError::DuplicateId(node.id.clone()));
        }
        seen_ids.insert(node.id.clone());
        
        // Check parent hash chain
        if !node.parents.is_empty() {
            for parent_id in &node.parents {
                if !seen_ids.contains(parent_id) {
                    return Err(VerificationError::ParentNotFound {
                        node: node.id.clone(),
                        parent: parent_id.clone(),
                    });
                }
                
                let parent = evidence_dag.get_node(parent_id)?;
                let expected_hash = compute_hash(parent);
                
                if node.previous_hash != expected_hash {
                    return Err(VerificationError::HashMismatch {
                        node: node.id.clone(),
                        expected: expected_hash,
                        actual: node.previous_hash.clone(),
                    });
                }
            }
        }
        
        // Check node hash
        let computed_hash = compute_hash(node);
        if node.hash != computed_hash {
            return Err(VerificationError::NodeHashMismatch {
                node: node.id.clone(),
                expected: computed_hash,
                actual: node.hash.clone(),
            });
        }
    }
    
    Ok(())
}
```

**Hash Computation:**
```rust
pub fn compute_hash(node: &EvidenceNode) -> String {
    let content = format!(
        "{}{}{}{}{}{}",
        node.id,
        node.time,
        node.tool,
        node.input_hash,
        node.output_hash,
        node.previous_hash
    );
    sha256(&content)
}
```

### **2. Signature Verification**

**Signature Check:**
```rust
pub fn verify_signature(
    node: &EvidenceNode,
    public_key: &PublicKey
) -> Result<(), VerificationError> {
    let message = format!(
        "{}{}{}{}",
        node.id,
        node.time,
        node.input_hash,
        node.output_hash
    );
    
    match verify(&message, &node.sig, public_key) {
        Ok(true) => Ok(()),
        Ok(false) => Err(VerificationError::InvalidSignature {
            node: node.id.clone(),
        }),
        Err(e) => Err(VerificationError::SignatureError(e)),
    }
}
```

**Quorum Signature Check:**
```rust
pub fn verify_quorum_signature(
    node: &EvidenceNode,
    quorum: &QuorumSignature,
    trusted_keys: &HashMap<String, PublicKey>
) -> Result<(), VerificationError> {
    let message = format!(
        "{}{}{}{}",
        node.id,
        node.time,
        node.input_hash,
        node.output_hash
    );
    
    let mut valid_signatures = 0;
    
    for signer in &quorum.signers {
        if let Some(public_key) = trusted_keys.get(&signer.id) {
            if verify(&message, &signer.sig, public_key).is_ok() {
                valid_signatures += 1;
            }
        }
    }
    
    if valid_signatures >= quorum.threshold {
        Ok(())
    } else {
        Err(VerificationError::QuorumNotMet {
            required: quorum.threshold,
            actual: valid_signatures,
        })
    }
}
```

### **3. Pure Constraint Replay**

**Constraint Replay:**
```rust
pub fn replay_constraint(
    constraint: &Constraint,
    evidence_dag: &EvidenceDAG,
    resolver: &Resolver
) -> Result<bool, VerificationError> {
    // Extract constraint expression
    let expr = constraint.expr.clone();
    
    // Build state from evidence
    let state = build_state_from_evidence(expr.variables(), evidence_dag)?;
    
    // Re-evaluate constraint
    let result = eval_constraint(&expr, &state, resolver)?;
    
    // Check against evidence claim
    if let Some(claim_node) = find_claim_node(constraint, evidence_dag)? {
        if claim_node.content == format!("{} == true", expr) {
            if result != claim_node.result {
                return Err(VerificationError::ConstraintMismatch {
                    constraint: expr,
                    expected: claim_node.result,
                    actual: result,
                });
            }
        }
    }
    
    Ok(result)
}
```

**State Building:**
```rust
pub fn build_state_from_evidence(
    variables: Vec<String>,
    evidence_dag: &EvidenceDAG
) -> Result<State, VerificationError> {
    let mut state = HashMap::new();
    
    for var in variables {
        // Find evidence node that provides this variable
        if let Some(node) = find_evidence_for_variable(&var, evidence_dag)? {
            // Extract value from evidence
            let value = extract_value_from_evidence(&var, node)?;
            state.insert(var, value);
        } else {
            return Err(VerificationError::MissingEvidence {
                variable: var,
            });
        }
    }
    
    Ok(state)
}
```

### **4. Evidence Completeness**

**Completeness Check:**
```rust
pub fn verify_evidence_completeness(
    contract: &Contract,
    evidence_dag: &EvidenceDAG
) -> Result<(), VerificationError> {
    // Check preconditions
    for precondition in &contract.preconditions {
        if !has_evidence_support(precondition, evidence_dag)? {
            return Err(VerificationError::MissingPreconditionEvidence {
                precondition: precondition.clone(),
            });
        }
    }
    
    // Check postconditions
    for postcondition in &contract.postconditions {
        if !has_evidence_support(postcondition, evidence_dag)? {
            return Err(VerificationError::MissingPostconditionEvidence {
                postcondition: postcondition.clone(),
            });
        }
    }
    
    Ok(())
}
```

**Evidence Support Check:**
```rust
pub fn has_evidence_support(
    constraint: &Constraint,
    evidence_dag: &EvidenceDAG
) -> Result<bool, VerificationError> {
    // Find claim node for this constraint
    let claim_nodes: Vec<&EvidenceNode> = evidence_dag.nodes
        .iter()
        .filter(|n| n.type == "claim")
        .filter(|n| n.content.contains(&constraint.to_string()))
        .collect();
    
    if claim_nodes.is_empty() {
        return Ok(false);
    }
    
    // Check each claim has source path
    for claim in claim_nodes {
        if !has_source_path(claim, evidence_dag)? {
            return Ok(false);
        }
    }
    
    Ok(true)
}
```

**Source Path Check:**
```rust
pub fn has_source_path(
    claim: &EvidenceNode,
    evidence_dag: &EvidenceDAG
) -> Result<bool, VerificationError> {
    // BFS from claim to sources
    let mut queue = vec![claim.id.clone()];
    let mut visited = HashSet::new();
    
    while let Some(node_id) = queue.pop() {
        if visited.contains(&node_id) {
            continue;
        }
        visited.insert(node_id.clone());
        
        let node = evidence_dag.get_node(&node_id)?;
        
        if node.type == "source" {
            return Ok(true);
        }
        
        // Follow supports/derives edges backwards
        for edge in &evidence_dag.edges {
            if edge.to == node_id && 
               (edge.type == "supports" || edge.type == "derives") {
                queue.push(edge.from.clone());
            }
        }
    }
    
    Ok(false)
}
```

### **5. Main Verifier**

**Verification Algorithm:**
```rust
pub fn verify(
    intent: &Intent,
    evidence_dag: &EvidenceDAG,
    resolver: &Resolver,
    trusted_keys: &HashMap<String, PublicKey>
) -> Result<VerificationResult, VerificationError> {
    // Step 1: Verify hash chain
    verify_hash_chain(evidence_dag)?;
    
    // Step 2: Verify signatures
    for node in &evidence_dag.nodes {
        if let Some(signer_id) = &node.signer {
            if let Some(public_key) = trusted_keys.get(signer_id) {
                verify_signature(node, public_key)?;
            }
        }
    }
    
    // Step 3: Replay constraints
    for precondition in &intent.contract.preconditions {
        let result = replay_constraint(precondition, evidence_dag, resolver)?;
        if !result {
            return Err(VerificationError::PreconditionFailed {
                precondition: precondition.clone(),
            });
        }
    }
    
    for postcondition in &intent.contract.postconditions {
        let result = replay_constraint(postcondition, evidence_dag, resolver)?;
        if !result {
            return Err(VerificationError::PostconditionFailed {
                postcondition: postcondition.clone(),
            });
        }
    }
    
    // Step 4: Verify evidence completeness
    verify_evidence_completeness(&intent.contract, evidence_dag)?;
    
    Ok(VerificationResult::Pass {
        preconditions: intent.contract.preconditions.len(),
        postconditions: intent.contract.postconditions.len(),
        evidence_nodes: evidence_dag.nodes.len(),
        evidence_edges: evidence_dag.edges.len(),
    })
}
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Implementation Plan** - Complete
2. ⏳ **Rust Implementation** - Create verifier
3. ⏳ **Tests** - Create test suite
4. ⏳ **Examples** - Verify meeting-room example

---

**Status:** 📋 **VERIFIER IMPLEMENTATION PLAN COMPLETE**  
**Next:** Create Rust implementation

