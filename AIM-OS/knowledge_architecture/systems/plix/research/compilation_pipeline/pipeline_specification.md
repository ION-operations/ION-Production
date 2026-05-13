# Compilation Pipeline: CNL → Core-PLIx → TLA+/Alloy/OPA/IRPlan

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Define complete compilation pipeline from CNL to all target formats

---

## 🎯 **OBJECTIVE**

Define compilation pipeline:
1. **CNL → AST** (parser transformation)
2. **AST → Core-PLIx** (lowering)
3. **Core-PLIx → TLA+** (formal verification)
4. **Core-PLIx → Alloy** (structural constraints)
5. **Core-PLIx → OPA/Cedar** (runtime policy)
6. **Core-PLIx → IRPlan** (APOE execution)

---

## 📐 **PIPELINE ARCHITECTURE**

### **Pipeline Stages**

```
CNL Source
    ↓
[1] Parser (CNL → AST)
    ↓
AST
    ↓
[2] Lowerer (AST → Core-PLIx)
    ↓
Core-PLIx
    ↓
[3] Compilers (Core-PLIx → Targets)
    ├─→ TLA+ Module
    ├─→ Alloy Model
    ├─→ OPA Policy
    └─→ IRPlan JSON
```

---

## 🔄 **STAGE 1: CNL → AST**

### **Parser Transformation**

**Input:** CNL source text  
**Output:** AST (Abstract Syntax Tree)

**Transformation Rules:**

**Intent:**
```
CNL: "ask ent:plix://db/table/users act:query ..."
AST: {
  speechAct: "ask",
  entity: {tag: "plix://db/table/users"},
  action: {id: "query"},
  ...
}
```

**Contract:**
```
CNL: "pre: user_authenticated == true post: results_returned == true"
AST: {
  preconditions: [
    {expr: {left: "user_authenticated", op: "==", right: true}}
  ],
  postconditions: [
    {expr: {left: "results_returned", op: "==", right: true}}
  ]
}
```

**Plan:**
```
CNL: "plan [step check := api.check_auth() ...]"
AST: {
  steps: [
    {id: "check", action: "api.check_auth", params: {}}
  ]
}
```

---

## 🔄 **STAGE 2: AST → CORE-PLIX**

### **Lowering Transformation**

**Input:** AST  
**Output:** Core-PLIx

**Transformation Rules:**

**Intent Lowering:**
```
AST.intent(sa, ent, act, contract, plan)
→ Core-PLIx: intent(sa, ent, act, contract, plan)
```

**Contract Lowering:**
```
AST.contract(pre, post)
→ Core-PLIx: contract(requires pre, ensures post)
```

**Plan Lowering:**
```
AST.plan(steps)
→ Core-PLIx: plan([task id := action(params), ...])
```

**Parameter Lowering:**
```
AST.with: {key: value}
→ Core-PLIx: params inlined in plan steps
```

**Evidence Lowering:**
```
AST.evidence: {w: tag, ...}
→ Core-PLIx: evidence require tag produce ...
```

---

## 🔄 **STAGE 3: CORE-PLIX → TLA+**

### **TLA+ Compilation**

**Input:** Core-PLIx intent  
**Output:** TLA+ module

**Transformation Rules:**

**Contract → TLA+ Invariant:**
```
Core-PLIx: contract(requires pre, ensures post)
TLA+: 
  Precondition == pre
  Postcondition == post
  Invariant == Precondition => [Next]_vars => Postcondition
```

**Plan → TLA+ Action:**
```
Core-PLIx: plan([task id := action(params), ...])
TLA+:
  Action ==
    /\ Precondition
    /\ task_id' = Execute(action, params)
    /\ ...
    /\ Postcondition
```

**Intent → TLA+ Specification:**
```
Core-PLIx: intent(sa, ent, act, contract, plan)
TLA+:
  SPEC == Init /\ [][Action]_vars /\ WF_vars(Action)
```

### **Example: Room Reservation**

**Core-PLIx:**
```
ensure ent:plix://room/reservation
  act:reserve
  requires room_available(date, duration) == true
  ensures room_reserved == true
  plan [
    task check := api.check_room_availability(date: date, duration: duration)
    task reserve := api.reserve_room(room_id: check.ref:room_id, duration: duration)
    depends reserve <- check
  ]
```

**TLA+ Module:**
```tla
EXTENDS Naturals, Sequences

VARIABLES room_available, room_reserved, reservation_id

Precondition == room_available = TRUE

Postcondition == room_reserved = TRUE

ReserveAction ==
  /\ Precondition
  /\ reservation_id' = ReserveRoom(GetAvailableRoom())
  /\ room_reserved' = TRUE
  /\ room_available' = FALSE
  /\ UNCHANGED <<other_vars>>
  /\ Postcondition'

Init == 
  /\ room_available = TRUE
  /\ room_reserved = FALSE
  /\ reservation_id = ""

Next == ReserveAction

Spec == Init /\ [][Next]_vars /\ WF_vars(ReserveAction)

THEOREM Spec => []Postcondition
```

---

## 🔄 **STAGE 4: CORE-PLIX → ALLOY**

### **Alloy Compilation**

**Input:** Core-PLIx intent  
**Output:** Alloy model

**Transformation Rules:**

**Entity → Alloy Signature:**
```
Core-PLIx: ent:plix://db/table/users
Alloy: sig User { ... }
```

**Contract → Alloy Fact:**
```
Core-PLIx: contract(requires pre, ensures post)
Alloy:
  fact Contract {
    all s: State | pre[s] => post[Next[s]]
  }
```

**Plan → Alloy Predicate:**
```
Core-PLIx: plan([task id := action(params), ...])
Alloy:
  pred ExecutePlan[s, s': State] {
    ExecuteTask1[s, s'] and
    ExecuteTask2[s', s''] and
    ...
  }
```

### **Example: Room Reservation**

**Alloy Model:**
```alloy
sig Room {
  id: Int,
  available: Bool
}

sig Reservation {
  room: Room,
  date: Int,
  duration: Int
}

fact NoDoubleBooking {
  all r1, r2: Reservation | 
    r1 != r2 => 
      (r1.date + r1.duration <= r2.date) or 
      (r2.date + r2.duration <= r1.date)
}

pred ReserveRoom[r: Room, d: Int, dur: Int] {
  r.available = True
  some res: Reservation |
    res.room = r and
    res.date = d and
    res.duration = dur
}

assert NoConflict {
  all r: Room, d: Int, dur: Int |
    ReserveRoom[r, d, dur] => 
      no res: Reservation |
        res.room = r and
        (res.date < d + dur) and
        (res.date + res.duration > d)
}
```

---

## 🔄 **STAGE 5: CORE-PLIX → OPA**

### **OPA Compilation**

**Input:** Core-PLIx intent  
**Output:** OPA Rego policy

**Transformation Rules:**

**Contract → OPA Rule:**
```
Core-PLIx: contract(requires pre, ensures post)
OPA:
  allow {
    preconditions_satisfied
    postconditions_satisfied
  }
```

**Plan → OPA Rules:**
```
Core-PLIx: plan([task id := action(params), ...])
OPA:
  can_execute_task_id {
    preconditions_for_task_id
  }
  
  execute_task_id {
    action_executed
    postconditions_for_task_id
  }
```

### **Example: Room Reservation**

**OPA Policy:**
```rego
package plix.room_reservation

import rego.v1

# Precondition check
allow {
  input.room_available == true
  input.user_authenticated == true
}

# Postcondition check
postcondition_satisfied {
  output.room_reserved == true
  output.calendar_event_created == true
}

# Task execution rules
can_execute_check {
  input.room_available == true
}

can_execute_reserve {
  check_result.room_id != null
}

can_execute_invite {
  reserve_result.reservation_id != null
}

# Main execution
execute {
  can_execute_check
  check_result := check_room_availability(input.date, input.duration)
  
  can_execute_reserve
  reserve_result := reserve_room(check_result.room_id, input.duration)
  
  can_execute_invite
  invite_result := create_calendar_event(reserve_result.reservation_id)
  
  postcondition_satisfied
}
```

---

## 🔄 **STAGE 6: CORE-PLIX → IRPLAN**

### **IRPlan Compilation**

**Input:** Core-PLIx intent  
**Output:** IRPlan JSON (APOE format)

**Transformation Rules:**

**Plan → IRPlan Steps:**
```
Core-PLIx: plan([task id := action(params), ...])
IRPlan: {
  steps: [
    {id: "id", action: "action", params: {...}, dependencies: [...]}
  ]
}
```

**Dependencies → IRPlan Dependencies:**
```
Core-PLIx: depends id1 <- id2
IRPlan: {
  steps: [
    {id: "id1", dependencies: ["id2"]}
  ]
}
```

**Retry → IRPlan Retry:**
```
Core-PLIx: retry id 3 exponential(100ms, 1s)
IRPlan: {
  steps: [
    {
      id: "id",
      retry: {
        max_attempts: 3,
        backoff: {type: "exponential", initial: "100ms", max: "1s"}
      }
    }
  ]
}
```

**Fallback → IRPlan Fallback:**
```
Core-PLIx: fallback id1 id2
IRPlan: {
  steps: [
    {
      id: "id1",
      fallback: "id2"
    }
  ]
}
```

**Compensation → IRPlan Compensation:**
```
Core-PLIx: compensate id -> action(params)
IRPlan: {
  steps: [
    {
      id: "id",
      compensation: {
        action: "action",
        params: {...}
      }
    }
  ]
}
```

### **Example: Room Reservation**

**IRPlan JSON:**
```json
{
  "intent_id": "intent:room_reservation",
  "speech_act": "ensure",
  "entity": "plix://room/reservation",
  "action": "reserve",
  "contract": {
    "preconditions": [
      "room_available(date, duration) == true"
    ],
    "postconditions": [
      "room_reserved == true",
      "calendar_event_created == true"
    ]
  },
  "steps": [
    {
      "id": "check",
      "action": "api.check_room_availability",
      "params": {
        "date": "${date}",
        "duration": "${duration}"
      },
      "dependencies": []
    },
    {
      "id": "reserve",
      "action": "api.reserve_room",
      "params": {
        "room_id": "${check.room_id}",
        "duration": "${duration}"
      },
      "dependencies": ["check"],
      "compensation": {
        "action": "api.cancel_reservation",
        "params": {
          "reservation_id": "${reserve.id}"
        }
      }
    },
    {
      "id": "invite",
      "action": "api.create_calendar_event",
      "params": {
        "room_id": "${reserve.room_id}"
      },
      "dependencies": ["reserve"]
    }
  ]
}
```

---

## 🎯 **COMPILATION VALIDATION**

### **Validation Rules**

**1. Semantic Preservation:**
```
∀intent: semantics(compile(intent)) = semantics(intent)
```

**2. Type Preservation:**
```
∀intent: types(compile(intent)) = types(intent)
```

**3. Effect Preservation:**
```
∀intent: effects(compile(intent)) = effects(intent)
```

---

## 🎯 **NEXT STEPS**

1. ✅ **Pipeline Architecture** - Complete
2. ✅ **CNL → AST** - Complete
3. ✅ **AST → Core-PLIx** - Complete
4. ✅ **Core-PLIx → TLA+** - Complete
5. ✅ **Core-PLIx → Alloy** - Complete
6. ✅ **Core-PLIx → OPA** - Complete
7. ✅ **Core-PLIx → IRPlan** - Complete
8. ⏳ **Implementation** - Link to compiler

---

**Status:** 📋 **COMPILATION PIPELINE SPECIFICATION COMPLETE**  
**Next:** Implementation integration

