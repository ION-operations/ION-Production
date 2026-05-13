# Parser Fix Implementation Plan

**Date:** 2025-01-27  
**Status:** ⏳ **READY TO IMPLEMENT**  
**Estimated Time:** 11 hours (1.5 days)

---

## 🎯 **FIXES TO IMPLEMENT**

### **Fix 1: Dual Syntax Support** (2 hours)
**Goal:** Accept BOTH `pre:/post:` AND `requires/ensures`

**Implementation:**
1. Update `tokenizeLine` to recognize `requires` and `ensures` keywords
2. Map `requires` → `pre_start` token
3. Map `ensures` → `post_start` token
4. Update AST to normalize to `pre/post`
5. Add tests

**Files to Modify:**
- `packages/plix/src/parser/index.ts` (tokenizeLine function)

**Test Cases:**
```plix
# Test 1: requires/ensures syntax
ensure ent:plix://room/reservation
  act:reserve
  requires room_available == true
  ensures room_reserved == true

# Test 2: pre:/post: syntax (existing)
ensure ent:plix://room/reservation
  act:reserve
  pre:
    con:room_available == true
  post:
    con:room_reserved == true
```

---

### **Fix 2: Formal Step Definition** (4 hours)
**Goal:** Support `task id := Action(params)` syntax

**Implementation:**
1. Update `tokenizeLine` to recognize `:=` operator
2. Parse action identifier after `:=`
3. Parse parameter list with tag references (`check.ref:field`)
4. Update AST to store action invocation
5. Keep `step id` as sugar (expands to `step id := id()`)
6. Add tests

**Files to Modify:**
- `packages/plix/src/parser/index.ts` (tokenizeLine, parseStep)
- `packages/plix/src/models/schema.ts` (PLIxPlanStep interface)

**Test Cases:**
```plix
# Test 1: Formal syntax
plan [
  task check := api.check_auth()
  task query := api.query_users(filter: check.ref:filter)
  depends query <- check
]

# Test 2: Simplified syntax (existing)
plan [
  step check
  step query
  depends query <- check
]
```

---

### **Fix 3: Formal Compensation** (2 hours)
**Goal:** Support `compensate id -> Action(params)` syntax

**Implementation:**
1. Update `tokenizeLine` to recognize `->` operator in compensation
2. Parse compensation action identifier
3. Parse compensation parameters
4. Update AST to store compensation action
5. Keep `compensate id` as sugar (looks up default compensation)
6. Add tests

**Files to Modify:**
- `packages/plix/src/parser/index.ts` (parseStep, parseCompensation)
- `packages/plix/src/models/schema.ts` (PLIxPlanStep.compensate)

**Test Cases:**
```plix
# Test 1: Formal syntax
plan [
  task create := api.create_user(data: user_data)
  compensate create -> api.delete_user(id: create.ref:id)
]

# Test 2: Simplified syntax (existing)
plan [
  step create
  compensate create
]
```

---

### **Fix 4: Evidence Structure** (2 hours)
**Goal:** Support `require/produce` evidence keywords

**Implementation:**
1. Update `tokenizeLine` to recognize `require` and `produce` keywords
2. Parse required evidence list
3. Parse produced evidence list
4. Update AST to distinguish between required and produced
5. Keep `w:` as sugar for `produce`
6. Add tests

**Files to Modify:**
- `packages/plix/src/parser/index.ts` (tokenizeLine, parseEvidence)
- `packages/plix/src/models/schema.ts` (PLIxIntent.evidence)

**Test Cases:**
```plix
# Test 1: Formal syntax
ensure ent:plix://db/schema/public
  act:migrate
  evidence
    require plix://witness/schema_before
    produce plix://witness/schema_after

# Test 2: Simplified syntax (existing)
ensure ent:plix://db/schema/public
  act:migrate
  evidence:
    w:plix://witness/schema_before
    w:plix://witness/schema_after
```

---

### **Fix 5: Golden Example Test** (1 hour)
**Goal:** Create comprehensive test for meeting-room intent

**Implementation:**
1. Create test file `packages/plix/src/parser/__tests__/core-plix.test.ts`
2. Add meeting-room intent test
3. Parse Core-PLIx format
4. Validate AST structure
5. Test round-trip conversion
6. Ensure 100% pass rate

**Test Case:**
```plix
ensure ent:plix://room/reservation
  act:reserve
  requires room_available(date, duration) == true
  ensures room_reserved == true
  plan [
    task check := api.check_room_availability(date: date, duration: duration)
    task reserve := api.reserve_room(room_id: check.ref:room_id, duration: duration)
    task invite := api.create_calendar_event(room_id: reserve.ref:room_id)
    depends reserve <- check
    depends invite <- reserve
    compensate reserve -> api.cancel_reservation(reservation_id: reserve.ref:id)
  ]
```

---

## 📋 **IMPLEMENTATION ORDER**

**Day 1 (Morning):** Fix 1 + Fix 4 (4 hours total)
- Dual syntax support (2 hours)
- Evidence structure (2 hours)

**Day 1 (Afternoon):** Fix 2 (4 hours)
- Formal step definition (4 hours)

**Day 2 (Morning):** Fix 3 + Fix 5 (3 hours total)
- Formal compensation (2 hours)
- Golden example test (1 hour)

**Total:** 11 hours (1.5 days)

---

## ✅ **SUCCESS CRITERIA**

**Per Fix:**
- ✅ Implementation complete
- ✅ Tests passing (unit + integration)
- ✅ No regressions (existing tests still pass)
- ✅ Code reviewed and documented

**Overall:**
- ✅ All 5 fixes implemented
- ✅ Golden example test passing (100%)
- ✅ Parser validation re-run shows 100% compliance
- ✅ Ready for compiler validation

---

## 🔧 **TECHNICAL APPROACH**

### **Backward Compatibility:**
- ALL fixes maintain backward compatibility
- Simplified syntax still works (sugar for formal syntax)
- Existing tests continue to pass
- No breaking changes

### **Parser Enhancement Pattern:**
```typescript
// Pattern: Recognize new keyword, parse formal syntax, fall back to simplified
if (line.startsWith('requires') || line.startsWith('ensures')) {
  // Formal syntax: requires/ensures
  tokens.push({ type: line.startsWith('requires') ? 'pre_start' : 'post_start', ... });
} else if (line.startsWith('pre:') || line.startsWith('post:')) {
  // Simplified syntax: pre:/post: (existing)
  tokens.push({ type: line.startsWith('pre:') ? 'pre_start' : 'post_start', ... });
}
```

### **AST Normalization:**
- Always normalize to canonical form in AST
- `requires` → `pre` in AST
- `ensures` → `post` in AST
- `task id := Action(params)` → structured step with action + params
- `compensate id -> Action(params)` → structured compensation

---

## 📊 **TRACKING**

### **Progress:**
- [ ] Fix 1: Dual Syntax Support (0/5 subtasks)
- [ ] Fix 2: Formal Step Definition (0/5 subtasks)
- [ ] Fix 3: Formal Compensation (0/5 subtasks)
- [ ] Fix 4: Evidence Structure (0/5 subtasks)
- [ ] Fix 5: Golden Example Test (0/5 subtasks)

### **Milestones:**
- [ ] Day 1 Morning Complete (Fix 1 + Fix 4)
- [ ] Day 1 Afternoon Complete (Fix 2)
- [ ] Day 2 Morning Complete (Fix 3 + Fix 5)
- [ ] All Fixes Complete (100% parser compliance)

---

**Next:** Start Fix 1 - Dual Syntax Support  
**Status:** ⏳ **READY TO IMPLEMENT**  
**Confidence:** 0.95

