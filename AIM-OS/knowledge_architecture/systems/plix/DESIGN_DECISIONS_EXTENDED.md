# PLIx Extended Design Decisions - Perplexity Considerations

**Date:** 2025-11-09  
**Source:** Perplexity Technical Considerations  
**Status:** 🔴 **NEW DECISIONS NEEDED**  
**Priority:** High - Address before implementation

---

## 🔴 5 New Design Decisions

### **Decision 11: Execution Ambiguity**

**Question:** How do you guarantee postcondition achievement when multiple execution paths exist?

**Decision:** **Formal Verification + Path Enumeration**

**Approach:**
1. **Enumerate all execution paths** (via topological ordering + parallel branches)
2. **Formally verify each path** (Alloy/TLA+ model checking)
3. **Verify postconditions** for each path
4. **Fallback strategy:** If primary path fails, try verified alternative

**Implementation:**
```typescript
interface ExecutionPath {
  steps: string[];
  postconditions: string[];
  verified: boolean;
  verification_proof?: string;  // Alloy/TLA+ proof
}

function verifyAllPaths(ir: IRPlan): ExecutionPath[] {
  const paths = enumeratePaths(ir);
  return paths.map(path => {
    const verified = verifyWithAlloy(path, ir.contract.post);
    return {
      ...path,
      verified,
      verification_proof: verified ? generateProof(path) : undefined
    };
  });
}
```

**Status:** 🔒 **LOCKED**

---

### **Decision 12: Temporal Constraints**

**Question:** Does intent change validity over time? Can postconditions be time-bounded?

**Decision:** **Time-Bounded Contracts + Intent Expiration**

**Approach:**
1. **Time-bounded postconditions:** `valid_until` field
2. **Intent expiration:** `intent_valid_until` field
3. **Temporal constraints:** Time-based preconditions
4. **TCS integration:** Track intent evolution over time

**Schema:**
```typescript
interface TemporalPostcondition {
  condition: string;
  valid_until?: datetime;  // Optional expiration
  valid_from?: datetime;    // Optional start time
}

interface PLIxContract {
  intent: {
    text: string;
    valid_until?: datetime;  // Intent expiration
  };
  contract: {
    pre: Array<string | TemporalConstraint>;
    post: Array<string | TemporalPostcondition>;
    temporal_constraints?: TemporalConstraint[];
  };
}
```

**Example:**
```yaml
intent:
  text: "Book a meeting room"
  valid_until: datetime("2025-12-01T12:00:00Z")  # Expires at noon

contract:
  pre:
    - user_authenticated == true
    - current_time >= datetime("2025-12-01T09:00:00Z")  # Temporal constraint
  post:
    - condition: room_reserved == true
      valid_until: datetime("2025-12-01T18:00:00Z")  # Time-bounded
```

**Status:** 🔒 **LOCKED**

---

### **Decision 13: Partial Achievement**

**Question:** What happens when intent is 70% achieved?

**Decision:** **Weighted Postconditions + Achievement Scoring**

**Approach:**
1. **Weighted postconditions:** Each postcondition has a weight (0.0-1.0)
2. **Achievement score:** `sum(weight * achieved)` for all postconditions
3. **Success threshold:** Default 0.8 (80% achievement required)
4. **Partial compensation:** Compensate only achieved postconditions

**Schema:**
```typescript
interface WeightedPostcondition {
  condition: string;
  weight: number;  // 0.0 to 1.0, must sum to 1.0
  achieved?: boolean;
}

interface AchievementResult {
  score: number;  // 0.0 to 1.0
  threshold: number;  // Default: 0.8
  success: boolean;  // score >= threshold
  postconditions: WeightedPostcondition[];
}
```

**Example:**
```yaml
contract:
  post:
    - condition: room_reserved == true
      weight: 0.6  # 60% of success
    - condition: calendar_event_created == true
      weight: 0.4  # 40% of success

telemetry:
  achievement:
    success_threshold: 0.8  # 80% required for success
```

**Implementation:**
```typescript
function calculateAchievement(
  postconditions: WeightedPostcondition[],
  threshold: number = 0.8
): AchievementResult {
  const score = postconditions.reduce(
    (sum, pc) => sum + (pc.weight * (pc.achieved ? 1 : 0)),
    0
  );
  
  return {
    score,
    threshold,
    success: score >= threshold,
    postconditions
  };
}
```

**Status:** 🔒 **LOCKED**

---

### **Decision 14: Intent Conflict Resolution**

**Question:** How does the system resolve conflicts when multiple contracts have interdependent goals?

**Decision:** **Priority-Based Resolution + Conflict Detection**

**Approach:**
1. **Conflict detection:** Detect conflicting postconditions
2. **Priority system:** Assign priorities to contracts
3. **Resolution strategies:** Priority, time, negotiation, escalation
4. **Pre-execution check:** Detect conflicts before execution

**Schema:**
```typescript
interface ConflictResolution {
  strategy: "priority" | "time" | "negotiation" | "escalation";
  priority_weights?: Record<string, number>;
  negotiation_rules?: string[];
}

interface Conflict {
  contracts: string[];  // Contract IDs in conflict
  type: "postcondition" | "resource" | "temporal";
  description: string;
  resolution?: ConflictResolution;
}
```

**Example:**
```yaml
# Contract 1
intent: "Book room A"
post: [room_A_reserved == true]

# Contract 2
intent: "Book room A"  # Same room!
post: [room_A_reserved == true]

# Conflict detected: Both want same room
conflict_resolution:
  strategy: priority
  priority_weights:
    contract_1: 0.7
    contract_2: 0.3
  # Contract 1 wins (higher priority)
```

**Implementation:**
```typescript
function detectConflicts(contracts: PLIxContract[]): Conflict[] {
  const conflicts: Conflict[] = [];
  
  // Detect postcondition conflicts
  for (let i = 0; i < contracts.length; i++) {
    for (let j = i + 1; j < contracts.length; j++) {
      const conflict = checkPostconditionConflict(
        contracts[i],
        contracts[j]
      );
      if (conflict) {
        conflicts.push(conflict);
      }
    }
  }
  
  return conflicts;
}

function resolveConflict(
  conflict: Conflict,
  resolution: ConflictResolution
): PLIxContract {
  switch (resolution.strategy) {
    case "priority":
      const sorted = conflict.contracts.sort((a, b) => 
        (resolution.priority_weights?.[b] || 0) - 
        (resolution.priority_weights?.[a] || 0)
      );
      return getContract(sorted[0]);
      
    case "time":
      return getContract(
        conflict.contracts.sort((a, b) => 
          getContract(a).created_at.localeCompare(getContract(b).created_at)
        )[0]
      );
      
    case "negotiation":
      return negotiateContracts(conflict.contracts, resolution.negotiation_rules);
      
    case "escalation":
      return escalateToHuman(conflict);
  }
}
```

**Status:** 🔒 **LOCKED**

---

### **Decision 15: Evidence Scalability**

**Question:** Compression/archival strategies for massive provenance graphs?

**Decision:** **Roll-Up + Hash Commitments + Retention Policies**

**Approach:**
1. **Retention policies:** Define retention periods per evidence type
2. **Roll-up strategy:** Aggregate old events into summaries
3. **Hash commitments:** Store hashes instead of full data for old evidence
4. **Archival:** Move old evidence to cold storage
5. **Query optimization:** Index evidence chains for fast queries

**Schema:**
```typescript
interface EvidenceRetentionPolicy {
  retention_period: duration;  // e.g., "90d"
  archival_strategy: "rollup" | "hash" | "archive" | "keep";
  rollup_aggregation?: "daily" | "weekly" | "monthly";
  hash_commitment?: boolean;  // Store hash instead of full data
}

interface ArchivedEvidence {
  hash: string;  // SHA-256 hash of original evidence
  count: number;  // Number of events aggregated
  date_range: { start: datetime; end: datetime };
  summary: string;  // Human-readable summary
}
```

**Example:**
```yaml
evidence:
  retention:
    default_period: duration("90d")
    archival_strategy: rollup
    rollup_aggregation: weekly
    hash_commitment: true  # Store hash after archival
    
  policies:
    - type: intent_lineage
      retention_period: duration("365d")  # Keep for 1 year
      archival_strategy: rollup
    - type: execution_events
      retention_period: duration("30d")  # Keep for 30 days
      archival_strategy: hash
    - type: provenance_chains
      retention_period: duration("forever")  # Never archive
      archival_strategy: keep
```

**Implementation:**
```typescript
function archiveEvidence(
  evidence: Evidence[],
  policy: EvidenceRetentionPolicy
): ArchivedEvidence | Evidence[] {
  const age = calculateAge(evidence);
  
  if (age > policy.retention_period) {
    switch (policy.archival_strategy) {
      case "rollup":
        return {
          hash: sha256(JSON.stringify(evidence)),
          count: evidence.length,
          date_range: {
            start: evidence[0].timestamp,
            end: evidence[evidence.length - 1].timestamp
          },
          summary: generateSummary(evidence, policy.rollup_aggregation)
        };
        
      case "hash":
        return {
          hash: sha256(JSON.stringify(evidence)),
          count: evidence.length,
          date_range: {
            start: evidence[0].timestamp,
            end: evidence[evidence.length - 1].timestamp
          },
          summary: "Archived evidence (hash commitment)"
        };
        
      case "archive":
        return moveToColdStorage(evidence);
        
      case "keep":
        return evidence;  // Keep as-is
    }
  }
  
  return evidence;  // Not old enough to archive
}
```

**Status:** 🔒 **LOCKED**

---

## 📋 Updated Design Decisions Summary

**Total Decisions:** 15 (10 original + 5 new)

| # | Decision | Status |
|---|----------|--------|
| 1-10 | Original decisions | 🔒 Locked |
| 11 | Execution ambiguity | 🔒 Locked |
| 12 | Temporal constraints | 🔒 Locked |
| 13 | Partial achievement | 🔒 Locked |
| 14 | Conflict resolution | 🔒 Locked |
| 15 | Evidence scalability | 🔒 Locked |

---

## 🚀 Implementation Impact

### **Schema Updates Needed**

1. **Add temporal fields:**
   - `intent.valid_until`
   - `postcondition.valid_until`
   - `temporal_constraints`

2. **Add weighted postconditions:**
   - `postcondition.weight`
   - `achievement.threshold`

3. **Add conflict resolution:**
   - `conflict_resolution` field
   - `priority_weights` field

4. **Add evidence retention:**
   - `evidence.retention_policy`
   - `archived_evidence` type

### **New Components Needed**

1. **Path Enumeration** - Generate all execution paths
2. **Formal Verification** - Alloy/TLA+ integration
3. **Achievement Scoring** - Calculate partial achievement
4. **Conflict Detection** - Detect conflicting contracts
5. **Evidence Archival** - Roll-up/hash/archive strategies
6. **Intent Learner** - Pattern extraction from lineage

---

## 📊 Updated MVP Scope

**Original MVP:** 6 components  
**Updated MVP:** 6 components + 6 new considerations

**New Tasks:**
- Week 1: Add temporal constraints to schema
- Week 2: Add achievement scoring to guards
- Week 3: Add conflict detection to execution
- Week 4: Add evidence archival to emitters

---

**Status:** 🔒 **ALL 15 DECISIONS LOCKED**  
**Next:** Update schema and implementation roadmap

