# Evidence Schema: DAG Structure and Verifier Algorithm

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Define Evidence DAG schema, PROV/OpenLineage mapping, and verifier algorithm

---

## 🎯 **OBJECTIVE**

Define:
1. **Evidence DAG** structure (nodes = claims, edges = supports/derived-from)
2. **W3C PROV** mapping
3. **OpenLineage** mapping
4. **JSON Schema** for Evidence
5. **Verifier algorithm** (deterministic replay)

---

## 📊 **EVIDENCE DAG STRUCTURE**

### **Graph Definition**

**Evidence DAG G = (V, E, τ, σ, ε) where:**

- **V** = Set of nodes (claims, sources, derivations, agents)
- **E** = Set of directed edges (supports, derives, witnesses, contradicts)
- **τ** = Temporal function (tx_time, valid_time)
- **σ** = Strength function (confidence, authority)
- **ε** = Embedding function (for similarity)

### **Node Types**

**1. Claim Node:**
```json
{
  "id": "claim:uuid",
  "type": "claim",
  "content": "room_reserved == true",
  "confidence": 0.95,
  "authority_tier": "A",
  "tx_time": "2025-01-27T12:00:00Z",
  "valid_time": {
    "from": "2025-01-27T12:00:00Z",
    "to": null
  },
  "embedding": [0.1, 0.2, ...]
}
```

**2. Source Node:**
```json
{
  "id": "source:uuid",
  "type": "source",
  "uri": "plix://witness/schema_before",
  "content_hash": "sha256:...",
  "authority_tier": "S",
  "tx_time": "2025-01-27T12:00:00Z",
  "valid_time": {
    "from": "2025-01-27T12:00:00Z",
    "to": null
  }
}
```

**3. Derivation Node:**
```json
{
  "id": "derivation:uuid",
  "type": "derivation",
  "method": "api.reserve_room",
  "inputs": ["claim:check_availability"],
  "outputs": ["claim:room_reserved"],
  "confidence": 0.90,
  "tx_time": "2025-01-27T12:00:00Z"
}
```

**4. Agent Node:**
```json
{
  "id": "agent:uuid",
  "type": "agent",
  "name": "APOE Executor",
  "capability": "execution",
  "trust_score": 0.85,
  "tx_time": "2025-01-27T12:00:00Z"
}
```

### **Edge Types**

**1. Supports Edge:**
```json
{
  "id": "edge:uuid",
  "type": "supports",
  "from": "source:uuid",
  "to": "claim:uuid",
  "strength": 0.95,
  "tx_time": "2025-01-27T12:00:00Z"
}
```

**2. Derives Edge:**
```json
{
  "id": "edge:uuid",
  "type": "derives",
  "from": "claim:input",
  "to": "claim:output",
  "via": "derivation:uuid",
  "strength": 0.90,
  "tx_time": "2025-01-27T12:00:00Z"
}
```

**3. Witnesses Edge:**
```json
{
  "id": "edge:uuid",
  "type": "witnesses",
  "from": "source:vif_witness",
  "to": "claim:uuid",
  "vif_hash": "sha256:...",
  "tx_time": "2025-01-27T12:00:00Z"
}
```

**4. Contradicts Edge:**
```json
{
  "id": "edge:uuid",
  "type": "contradicts",
  "from": "claim:claim1",
  "to": "claim:claim2",
  "strength": 0.80,
  "tx_time": "2025-01-27T12:00:00Z"
}
```

---

## 🌐 **W3C PROV MAPPING**

### **PROV Entities**

**Claim → prov:Entity:**
```json
{
  "@context": "http://www.w3.org/ns/prov#",
  "@id": "prov:claim:uuid",
  "@type": "prov:Entity",
  "prov:value": "room_reserved == true",
  "prov:wasAttributedTo": "prov:agent:uuid",
  "prov:wasGeneratedBy": "prov:activity:uuid",
  "prov:generatedAtTime": "2025-01-27T12:00:00Z"
}
```

**Source → prov:Entity:**
```json
{
  "@context": "http://www.w3.org/ns/prov#",
  "@id": "prov:source:uuid",
  "@type": "prov:Entity",
  "prov:value": "plix://witness/schema_before",
  "prov:wasDerivedFrom": "prov:source:original",
  "prov:specializationOf": "prov:source:parent"
}
```

**Derivation → prov:Activity:**
```json
{
  "@context": "http://www.w3.org/ns/prov#",
  "@id": "prov:derivation:uuid",
  "@type": "prov:Activity",
  "prov:used": ["prov:claim:input"],
  "prov:generated": ["prov:claim:output"],
  "prov:startedAtTime": "2025-01-27T12:00:00Z",
  "prov:endedAtTime": "2025-01-27T12:00:05Z"
}
```

**Agent → prov:Agent:**
```json
{
  "@context": "http://www.w3.org/ns/prov#",
  "@id": "prov:agent:uuid",
  "@type": "prov:Agent",
  "prov:name": "APOE Executor",
  "prov:type": "SoftwareAgent"
}
```

### **PROV Relationships**

**Supports → prov:wasInfluencedBy:**
```json
{
  "@context": "http://www.w3.org/ns/prov#",
  "@id": "prov:influence:uuid",
  "@type": "prov:Influence",
  "prov:influencer": "prov:source:uuid",
  "prov:influencee": "prov:claim:uuid"
}
```

**Derives → prov:wasDerivedFrom:**
```json
{
  "@context": "http://www.w3.org/ns/prov#",
  "@id": "prov:derivation:uuid",
  "@type": "prov:Derivation",
  "prov:entity": "prov:claim:output",
  "prov:hadPrimarySource": "prov:claim:input",
  "prov:activity": "prov:derivation:activity"
}
```

**Witnesses → prov:wasQuotedFrom:**
```json
{
  "@context": "http://www.w3.org/ns/prov#",
  "@id": "prov:quotation:uuid",
  "@type": "prov:Quotation",
  "prov:entity": "prov:claim:uuid",
  "prov:hadPrimarySource": "prov:source:vif_witness"
}
```

---

## 📈 **OPENLINEAGE MAPPING**

### **OpenLineage Run**

**Intent Execution → Run:**
```json
{
  "run": {
    "runId": "intent:uuid",
    "facets": {
      "intent": {
        "speechAct": "ensure",
        "entity": "plix://room/reservation",
        "action": "reserve"
      },
      "contract": {
        "preconditions": ["room_available == true"],
        "postconditions": ["room_reserved == true"]
      }
    }
  },
  "job": {
    "namespace": "plix",
    "name": "room_reservation"
  },
  "inputs": [
    {
      "namespace": "plix",
      "name": "room_availability_check",
      "facets": {
        "dataQuality": {
          "confidence": 0.95
        }
      }
    }
  ],
  "outputs": [
    {
      "namespace": "plix",
      "name": "room_reservation",
      "facets": {
        "dataQuality": {
          "confidence": 0.90
        }
      }
    }
  ]
}
```

### **OpenLineage Job**

**Plan Step → Job:**
```json
{
  "job": {
    "namespace": "plix",
    "name": "api.reserve_room",
    "facets": {
      "sourceCode": {
        "language": "PLIx",
        "source": "task reserve := api.reserve_room(...)"
      }
    }
  },
  "inputs": [
    {
      "namespace": "plix",
      "name": "room_availability"
    }
  ],
  "outputs": [
    {
      "namespace": "plix",
      "name": "reservation_id"
    }
  ]
}
```

---

## 📋 **JSON SCHEMA**

### **Evidence DAG Schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Evidence DAG",
  "type": "object",
  "properties": {
    "nodes": {
      "type": "array",
      "items": {
        "oneOf": [
          {"$ref": "#/definitions/ClaimNode"},
          {"$ref": "#/definitions/SourceNode"},
          {"$ref": "#/definitions/DerivationNode"},
          {"$ref": "#/definitions/AgentNode"}
        ]
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "oneOf": [
          {"$ref": "#/definitions/SupportsEdge"},
          {"$ref": "#/definitions/DerivesEdge"},
          {"$ref": "#/definitions/WitnessesEdge"},
          {"$ref": "#/definitions/ContradictsEdge"}
        ]
      }
    }
  },
  "definitions": {
    "ClaimNode": {
      "type": "object",
      "required": ["id", "type", "content", "tx_time"],
      "properties": {
        "id": {"type": "string", "pattern": "^claim:"},
        "type": {"const": "claim"},
        "content": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "authority_tier": {"type": "string", "enum": ["S", "A", "B", "C"]},
        "tx_time": {"type": "string", "format": "date-time"},
        "valid_time": {"$ref": "#/definitions/TimeInterval"},
        "embedding": {"type": "array", "items": {"type": "number"}}
      }
    },
    "SourceNode": {
      "type": "object",
      "required": ["id", "type", "uri", "content_hash", "tx_time"],
      "properties": {
        "id": {"type": "string", "pattern": "^source:"},
        "type": {"const": "source"},
        "uri": {"type": "string"},
        "content_hash": {"type": "string", "pattern": "^sha256:"},
        "authority_tier": {"type": "string", "enum": ["S", "A", "B", "C"]},
        "tx_time": {"type": "string", "format": "date-time"},
        "valid_time": {"$ref": "#/definitions/TimeInterval"}
      }
    },
    "TimeInterval": {
      "type": "object",
      "required": ["from"],
      "properties": {
        "from": {"type": "string", "format": "date-time"},
        "to": {"type": ["string", "null"], "format": "date-time"}
      }
    }
  }
}
```

---

## ✅ **VERIFIER ALGORITHM**

### **Verifier Specification**

**Algorithm: `verify(evidence_dag, contract)`**

```
function verify(evidence_dag, contract):
  // Step 1: Extract claims from evidence DAG
  claims = extract_claims(evidence_dag)
  
  // Step 2: Check preconditions
  for precondition in contract.preconditions:
    claim = find_claim(claims, precondition)
    if not claim:
      return FAIL("Precondition not found: " + precondition)
    if not verify_claim(claim, evidence_dag):
      return FAIL("Precondition not verified: " + precondition)
  
  // Step 3: Check postconditions
  for postcondition in contract.postconditions:
    claim = find_claim(claims, postcondition)
    if not claim:
      return FAIL("Postcondition not found: " + postcondition)
    if not verify_claim(claim, evidence_dag):
      return FAIL("Postcondition not verified: " + postcondition)
  
  // Step 4: Check evidence chain completeness
  for claim in claims:
    if not has_source_path(claim, evidence_dag):
      return FAIL("Claim has no source path: " + claim.id)
  
  return PASS("All conditions verified")
```

### **Claim Verification**

**Algorithm: `verify_claim(claim, evidence_dag)`**

```
function verify_claim(claim, evidence_dag):
  // Step 1: Find all sources supporting this claim
  sources = find_sources(claim, evidence_dag)
  
  if sources.empty():
    return FAIL("No sources found for claim: " + claim.id)
  
  // Step 2: Verify source authenticity
  for source in sources:
    if not verify_source_hash(source):
      return FAIL("Source hash mismatch: " + source.id)
  
  // Step 3: Check authority tier
  max_authority = max([s.authority_tier for s in sources])
  if max_authority < required_authority(claim):
    return FAIL("Insufficient authority: " + max_authority)
  
  // Step 4: Check confidence
  if claim.confidence < required_confidence(claim):
    return FAIL("Insufficient confidence: " + claim.confidence)
  
  return PASS("Claim verified")
```

### **Source Path Verification**

**Algorithm: `has_source_path(claim, evidence_dag)`**

```
function has_source_path(claim, evidence_dag):
  // BFS from claim to sources
  queue = [claim]
  visited = set()
  
  while queue:
    node = queue.pop()
    if node.type == "source":
      return true
    
    visited.add(node.id)
    
    // Follow supports/derives edges backwards
    for edge in evidence_dag.edges:
      if edge.to == node.id and edge.type in ["supports", "derives"]:
        if edge.from not in visited:
          queue.append(find_node(evidence_dag, edge.from))
  
  return false
```

---

## 🔗 **HASH-ANCHORING**

### **Content Hash**

**Format:** `sha256:<hex>`

**Computation:**
```
content_hash = sha256(
  claim.content +
  claim.tx_time +
  claim.authority_tier +
  claim.confidence
)
```

### **Evidence Hash**

**Format:** `sha256:<hex>`

**Computation:**
```
evidence_hash = sha256(
  node.id +
  node.content_hash +
  node.tx_time +
  serialize(edges_from_node)
)
```

### **Verification**

**Algorithm: `verify_hash(node, expected_hash)`**

```
function verify_hash(node, expected_hash):
  computed_hash = compute_content_hash(node)
  return computed_hash == expected_hash
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Evidence DAG Structure** - Complete
2. ✅ **PROV Mapping** - Complete
3. ✅ **OpenLineage Mapping** - Complete
4. ✅ **JSON Schema** - Complete
5. ✅ **Verifier Algorithm** - Complete
6. ⏳ **Implementation** - Link to SEG/VIF systems

---

**Status:** 📋 **EVIDENCE SCHEMA SPECIFICATION COMPLETE**  
**Next:** Link to SEG/VIF implementations

