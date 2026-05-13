# Meeting-Room Example: README

**Example:** Meeting-Room Reservation using Core-PLIx  
**Status:** ✅ **COMPLETE**  
**Demonstrates:** Full PLIx pipeline from intent to verification

---

## 📋 **OVERVIEW**

This example demonstrates a complete PLIx workflow:
1. **Intent creation** — Reserve a meeting room
2. **Plan execution** — Check availability → Reserve → Create calendar event
3. **Evidence generation** — Track execution with hash-chaining
4. **Verification** — Verify evidence DAG cryptographically

---

## 🚀 **RUNNING THE EXAMPLE**

### **Passing Scenario:**

```bash
cargo run --bin run-meeting-room-passing
```

**Output:**
- `meeting_room_passing_trace.json` — Evidence log

### **Compensated Scenario:**

```bash
cargo run --bin run-meeting-room-compensated
```

**Output:**
- `meeting_room_compensated_trace.json` — Evidence log with compensation

### **Generate Evidence DAG:**

```bash
cargo run --bin generate-evidence-dag
```

**Output:**
- `meeting_room_evidence_dag.json` — Evidence DAG structure

### **Verify Evidence DAG:**

```bash
cargo run --bin verify-evidence-dag
```

**Output:**
- Verification result (PASS/FAIL)

### **Visualize Evidence DAG:**

```bash
cargo run --bin visualize-evidence-dag
dot -Tpng meeting_room_evidence_dag.dot -o meeting_room_evidence_dag.png
```

**Output:**
- `meeting_room_evidence_dag.dot` — GraphViz DOT file
- `meeting_room_evidence_dag.png` — Visual diagram

---

## 📐 **INTENT STRUCTURE**

### **Speech Act:** `ensure`

### **Entity:** `plix://room/reservation`

### **Action:** `reserve`

### **Contract:**

**Preconditions:**
- `room_available == true`
- `user_authenticated == true`

**Postconditions:**
- `room_reserved == true`
- `calendar_event_created == true`

### **Plan:**

**Steps:**
1. **check** — `api.check_room_availability(date, duration)`
2. **reserve** — `api.reserve_room(room_id, duration)` [compensable]
3. **invite** — `api.create_calendar_event(room_id, user_id)`

**Dependencies:**
- `reserve` depends on `check`
- `invite` depends on `reserve`

**Compensation:**
- `reserve` → `api.cancel_reservation(reservation_id)`

---

## 🎯 **WHAT THIS DEMONSTRATES**

### **1. Intent Execution:**
- ✅ DAG-based plan execution
- ✅ Topological ordering
- ✅ Step execution with evidence

### **2. Evidence Tracking:**
- ✅ Hash-chaining
- ✅ Parent relationships
- ✅ Tool tracking

### **3. Compensation:**
- ✅ Reverse topological order
- ✅ Automatic compensation on failure
- ✅ Evidence of compensation

### **4. Verification:**
- ✅ Hash chain verification
- ✅ Signature verification
- ✅ Constraint replay
- ✅ Evidence completeness

---

**Status:** ✅ **EXAMPLE COMPLETE**  
**Files Generated:** 5 executables, 4 output files

