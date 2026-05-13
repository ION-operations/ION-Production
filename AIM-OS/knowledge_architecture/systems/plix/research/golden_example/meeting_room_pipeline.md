# Golden Example: Meeting-Room Pipeline (End-to-End)

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Create complete end-to-end example with all artifacts

---

## 🎯 **OBJECTIVE**

Create golden example demonstrating:
1. **CNL source** (human-readable)
2. **Core-PLIx** (kernel representation)
3. **TLA+ module** (formal verification)
4. **Alloy model** (structural constraints)
5. **OPA policy** (runtime policy)
6. **IRPlan JSON** (APOE execution)
7. **Evidence DAG** (provenance)
8. **Verifier output** (verification result)

---

## 📝 **CNL SOURCE**

### **Meeting-Room Reservation Intent**

```plix
ensure ent:plix://room/reservation
  act:reserve
  with:
    date: "2025-12-01"
    duration: "2h"
    user_id: "user123"
  
  pre:
    room_available(date, duration) == true
    user_authenticated == true
  
  post:
    room_reserved == true
    calendar_event_created == true
  
  evidence:
    require w:plix://witness/room_availability
    produce w:plix://witness/reservation_confirmed
  
  plan [
    step check := api.check_room_availability(date: ${date}, duration: ${duration})
    step reserve := api.reserve_room(room_id: ${check.room_id}, duration: ${duration})
    step invite := api.create_calendar_event(room_id: ${reserve.room_id}, user_id: ${user_id})
    
    depends reserve <- check
    depends invite <- reserve
    
    retry check 3 exponential(100ms, 1s) jitter
    fallback check api.fallback_check_availability(date: ${date}, duration: ${duration})
    
    compensate reserve -> api.cancel_reservation(reservation_id: ${reserve.id})
  ]
  
  policy:
    duration_hours <= 4
    calendar_conflicts == "none"
  
  safety:
    min_confidence = 0.82
    effects = [external_io, compensable]
```

---

## 🔧 **CORE-PLIX REPRESENTATION**

### **Core-PLIx Kernel**

```
ensure ent:plix://room/reservation
  act:reserve
  requires 
    room_available(date, duration) == true
    user_authenticated == true
  ensures 
    room_reserved == true
    calendar_event_created == true
  evidence
    require plix://witness/room_availability
    produce plix://witness/reservation_confirmed
  plan [
    task check := api.check_room_availability(date: date, duration: duration)
    task reserve := api.reserve_room(room_id: check.ref:room_id, duration: duration)
    task invite := api.create_calendar_event(room_id: reserve.ref:room_id, user_id: user_id)
    depends reserve <- check
    depends invite <- reserve
    retry check 3 exponential(100ms, 1s)
    fallback check api.fallback_check_availability(date: date, duration: duration)
    compensate reserve -> api.cancel_reservation(reservation_id: reserve.ref:id)
  ]
```

---

## 🔍 **TLA+ MODULE**

### **TLA+ Specification**

```tla
EXTENDS Naturals, Sequences

VARIABLES room_available, room_reserved, calendar_event_created, reservation_id, user_authenticated

Precondition == 
  /\ room_available = TRUE
  /\ user_authenticated = TRUE

Postcondition == 
  /\ room_reserved = TRUE
  /\ calendar_event_created = TRUE

CheckAvailability ==
  /\ Precondition
  /\ room_id' = GetAvailableRoom()
  /\ UNCHANGED <<room_reserved, calendar_event_created, reservation_id, user_authenticated>>

ReserveRoom ==
  /\ room_id ≠ NULL
  /\ reservation_id' = ReserveRoom(room_id, duration)
  /\ room_reserved' = TRUE
  /\ room_available' = FALSE
  /\ UNCHANGED <<calendar_event_created, user_authenticated>>

CreateCalendarEvent ==
  /\ room_reserved = TRUE
  /\ calendar_event_created' = TRUE
  /\ UNCHANGED <<room_available, room_reserved, reservation_id, user_authenticated>>

Next == CheckAvailability \/ ReserveRoom \/ CreateCalendarEvent

Init == 
  /\ room_available = TRUE
  /\ room_reserved = FALSE
  /\ calendar_event_created = FALSE
  /\ reservation_id = NULL
  /\ user_authenticated = TRUE

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

THEOREM Spec => []Postcondition
```

---

## 🔷 **ALLOY MODEL**

### **Alloy Specification**

```alloy
sig Room {
  id: Int,
  available: Bool
}

sig Reservation {
  room: Room,
  date: Int,
  duration: Int,
  user_id: Int
}

sig CalendarEvent {
  reservation: Reservation,
  user_id: Int
}

fact NoDoubleBooking {
  all r1, r2: Reservation | 
    r1 != r2 => 
      (r1.date + r1.duration <= r2.date) or 
      (r2.date + r2.duration <= r1.date)
}

fact ReservationRequiresAvailability {
  all r: Reservation | r.room.available = True
}

fact CalendarEventRequiresReservation {
  all e: CalendarEvent | e.reservation != none
}

pred ReserveRoom[r: Room, d: Int, dur: Int, u: Int] {
  r.available = True
  some res: Reservation |
    res.room = r and
    res.date = d and
    res.duration = dur and
    res.user_id = u
  some ev: CalendarEvent |
    ev.reservation = res and
    ev.user_id = u
}

assert NoConflict {
  all r: Room, d: Int, dur: Int, u: Int |
    ReserveRoom[r, d, dur, u] => 
      no res: Reservation |
        res.room = r and
        (res.date < d + dur) and
        (res.date + res.duration > d) and
        res != the_reservation
}
```

---

## 🔒 **OPA POLICY**

### **OPA Rego Policy**

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

# Policy constraints
duration_policy {
  input.duration_hours <= 4
}

calendar_conflict_policy {
  input.calendar_conflicts == "none"
}

# Task execution rules
can_execute_check {
  input.room_available == true
  input.user_authenticated == true
}

can_execute_reserve {
  check_result.room_id != null
  duration_policy
}

can_execute_invite {
  reserve_result.reservation_id != null
  calendar_conflict_policy
}

# Main execution
execute {
  can_execute_check
  check_result := check_room_availability(input.date, input.duration)
  
  can_execute_reserve
  reserve_result := reserve_room(check_result.room_id, input.duration)
  
  can_execute_invite
  invite_result := create_calendar_event(reserve_result.reservation_id, input.user_id)
  
  postcondition_satisfied
}
```

---

## 📋 **IRPLAN JSON**

### **APOE Execution Plan**

```json
{
  "intent_id": "intent:room_reservation_2025-12-01",
  "speech_act": "ensure",
  "entity": "plix://room/reservation",
  "action": "reserve",
  "contract": {
    "preconditions": [
      "room_available(date, duration) == true",
      "user_authenticated == true"
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
      "dependencies": [],
      "retry": {
        "max_attempts": 3,
        "backoff": {
          "type": "exponential",
          "initial": "100ms",
          "max": "1s",
          "jitter": true
        }
      },
      "fallback": {
        "action": "api.fallback_check_availability",
        "params": {
          "date": "${date}",
          "duration": "${duration}"
        }
      }
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
        "room_id": "${reserve.room_id}",
        "user_id": "${user_id}"
      },
      "dependencies": ["reserve"]
    }
  ],
  "evidence": {
    "require": ["plix://witness/room_availability"],
    "produce": ["plix://witness/reservation_confirmed"]
  },
  "policy": {
    "duration_hours": {"max": 4},
    "calendar_conflicts": {"allowed": "none"}
  },
  "safety": {
    "min_confidence": 0.82,
    "effects": ["external_io", "compensable"]
  }
}
```

---

## 📊 **EVIDENCE DAG**

### **Evidence Graph JSON**

```json
{
  "nodes": [
    {
      "id": "claim:room_available",
      "type": "claim",
      "content": "room_available(date, duration) == true",
      "confidence": 0.95,
      "authority_tier": "A",
      "tx_time": "2025-12-01T10:00:00Z",
      "valid_time": {
        "from": "2025-12-01T10:00:00Z",
        "to": null
      }
    },
    {
      "id": "source:room_availability_witness",
      "type": "source",
      "uri": "plix://witness/room_availability",
      "content_hash": "sha256:abc123...",
      "authority_tier": "S",
      "tx_time": "2025-12-01T10:00:00Z"
    },
    {
      "id": "claim:room_reserved",
      "type": "claim",
      "content": "room_reserved == true",
      "confidence": 0.90,
      "authority_tier": "A",
      "tx_time": "2025-12-01T10:00:05Z"
    },
    {
      "id": "derivation:reserve_room",
      "type": "derivation",
      "method": "api.reserve_room",
      "inputs": ["claim:room_available"],
      "outputs": ["claim:room_reserved"],
      "confidence": 0.90,
      "tx_time": "2025-12-01T10:00:05Z"
    },
    {
      "id": "claim:calendar_event_created",
      "type": "claim",
      "content": "calendar_event_created == true",
      "confidence": 0.88,
      "authority_tier": "A",
      "tx_time": "2025-12-01T10:00:10Z"
    },
    {
      "id": "source:reservation_confirmed_witness",
      "type": "source",
      "uri": "plix://witness/reservation_confirmed",
      "content_hash": "sha256:def456...",
      "authority_tier": "S",
      "tx_time": "2025-12-01T10:00:10Z"
    }
  ],
  "edges": [
    {
      "id": "edge:support_availability",
      "type": "supports",
      "from": "source:room_availability_witness",
      "to": "claim:room_available",
      "strength": 0.95,
      "tx_time": "2025-12-01T10:00:00Z"
    },
    {
      "id": "edge:derives_reservation",
      "type": "derives",
      "from": "claim:room_available",
      "to": "claim:room_reserved",
      "via": "derivation:reserve_room",
      "strength": 0.90,
      "tx_time": "2025-12-01T10:00:05Z"
    },
    {
      "id": "edge:derives_calendar",
      "type": "derives",
      "from": "claim:room_reserved",
      "to": "claim:calendar_event_created",
      "via": "derivation:create_calendar_event",
      "strength": 0.88,
      "tx_time": "2025-12-01T10:00:10Z"
    },
    {
      "id": "edge:witnesses_confirmation",
      "type": "witnesses",
      "from": "source:reservation_confirmed_witness",
      "to": "claim:calendar_event_created",
      "vif_hash": "sha256:ghi789...",
      "tx_time": "2025-12-01T10:00:10Z"
    }
  ]
}
```

---

## ✅ **VERIFIER OUTPUT**

### **Verification Result**

```
PLIx Verifier v0.1
==================

Intent: intent:room_reservation_2025-12-01
Entity: plix://room/reservation
Action: reserve

[1/8] Resolve Tags
  ✓ Resolved ent:plix://room/reservation → Entity
  ✓ Resolved act:reserve → Action

[2/8] Authorize
  ✓ Authority tier A sufficient for reserve action

[3/8] Check Preconditions
  ✓ room_available(date, duration) == true
    - Supported by: source:room_availability_witness
    - Confidence: 0.95
    - Authority: S
  ✓ user_authenticated == true
    - Supported by: system authentication
    - Confidence: 1.0
    - Authority: S

[4/8] Execute Plan
  ✓ Step check: api.check_room_availability
    - Result: room_id = "room-101"
    - Evidence: check_evidence_001
  ✓ Step reserve: api.reserve_room
    - Result: reservation_id = "res-12345"
    - Evidence: reserve_evidence_002
  ✓ Step invite: api.create_calendar_event
    - Result: event_id = "event-67890"
    - Evidence: invite_evidence_003

[5/8] Run Tests
  ✓ All test specifications passed

[6/8] Collect Evidence
  ✓ Collected evidence for all steps
  ✓ Evidence DAG constructed
  ✓ Hash chain verified

[7/8] Verify Postconditions
  ✓ room_reserved == true
    - Supported by: derivation:reserve_room
    - Confidence: 0.90
    - Authority: A
  ✓ calendar_event_created == true
    - Supported by: derivation:create_calendar_event
    - Confidence: 0.88
    - Authority: A

[8/8] Emit Provenance
  ✓ SEG events emitted
  ✓ Intent lineage tracked
  ✓ Evidence graph updated

==================
VERIFICATION RESULT: PASS
==================

Preconditions: ✓ All satisfied
Postconditions: ✓ All satisfied
Evidence Chain: ✓ Complete and verified
Confidence: 0.88 (meets minimum 0.82)
Authority: A (sufficient)

Evidence DAG:
  - Nodes: 6
  - Edges: 4
  - Sources: 2
  - Claims: 3
  - Derivations: 2

Hash Chain:
  - All hashes verified ✓
  - No tampering detected ✓
  - Signatures valid ✓

Compensation Plan:
  - Available: ✓
  - Tested: ✓
  - Ready: ✓

Status: INTENT EXECUTED SUCCESSFULLY
```

---

## 🎯 **NEXT STEPS**

1. ✅ **CNL Source** - Complete
2. ✅ **Core-PLIx** - Complete
3. ✅ **TLA+ Module** - Complete
4. ✅ **Alloy Model** - Complete
5. ✅ **OPA Policy** - Complete
6. ✅ **IRPlan JSON** - Complete
7. ✅ **Evidence DAG** - Complete
8. ✅ **Verifier Output** - Complete
9. ⏳ **Implementation** - Create reference interpreter and verifier

---

**Status:** 📋 **GOLDEN EXAMPLE COMPLETE**  
**Next:** Create reference interpreter and verifier

