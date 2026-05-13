# PLIx User Guide

**Version:** 1.0.0  
**Date:** 2025-01-27  
**Audience:** Developers using PLIx for intent specification

---

## 🌟 **Welcome to PLIx!**

PLIx (Programmatic-Linguistic Interface) is a pure language for expressing intent with mathematical rigor and verifiable execution. This guide will help you write, test, and deploy PLIx contracts.

---

## 📖 **Table of Contents**

1. [Getting Started](#getting-started)
2. [Writing Your First Intent](#writing-your-first-intent)
3. [Understanding Contracts](#understanding-contracts)
4. [Plans and Compensation](#plans-and-compensation)
5. [Evidence and Verification](#evidence-and-verification)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 **Getting Started**

### **Installation**

```bash
npm install @aimos/plix
# or
yarn add @aimos/plix
```

### **Quick Start**

```typescript
import { PLIXParser, Pipeline } from '@aimos/plix';

// Parse PLIx text
const parser = new PLIXParser();
const result = parser.parse(plixText);

// Or use convenience function
const { aipGraph, errors } = await Pipeline.parseAndCompile(plixText);
```

---

## ✍️ **Writing Your First Intent**

### **Basic Structure**

Every PLIx intent has 4 parts:

1. **Speech Act** - What you want to do (`ask`, `ensure`, `plan`)
2. **Entity** - What you're acting on (`ent:plix://...`)
3. **Contract** - Preconditions and postconditions
4. **Plan** - How to achieve the intent

### **Example: Simple Query**

```plix
ask ent:plix://db/users
  act:query
  requires
    con:authenticated == true
  ensures
    con:results_returned == true
  plan [
    task query := api.query_users(filter: "active")
  ]
```

**Explanation:**
- `ask` - We're requesting information
- `ent:plix://db/users` - Acting on users table
- `requires` - Must be authenticated first
- `ensures` - Must return results
- `plan` - Single step to query users

---

## 📋 **Understanding Contracts**

### **Preconditions (`requires`)**

Preconditions define what MUST be true before execution:

```plix
requires
  con:user_authenticated == true
  con:account_active == true
  con:balance >= 100
```

**Types of Constraints:**

**Simple:**
```plix
con:x == 1
con:y <= 100
con:z != "invalid"
```

**Logical:**
```plix
con:(x == 1) AND (y == 2)
con:(a == true) OR (b == true)
con:NOT (error_count > 0)
```

**Quantified:**
```plix
con:forall_rows unique_email
con:exists_room (capacity >= 10)
```

**Temporal:**
```plix
con:eventually_true(completed, within_ms=5000)
con:always(authenticated == true)
```

### **Postconditions (`ensures`)**

Postconditions define what MUST be true after execution:

```plix
ensures
  con:operation_complete == true
  con:result_valid == true
  con:no_errors == true
```

---

## 🔄 **Plans and Compensation**

### **Writing Plans**

Plans define HOW to achieve your intent:

```plix
plan [
  task check := api.check_availability()
  task reserve := api.reserve(room_id: check.ref:room_id)
  task notify := api.send_notification(event_id: reserve.ref:event_id)
  depends reserve <- check
  depends notify <- reserve
]
```

**Key Concepts:**

**Tasks:**
```plix
task stepName := api.action(param1: value1, param2: value2)
```

**Dependencies:**
```plix
depends step2 <- step1  # step2 runs after step1
```

**Tag References:**
```plix
param: step1.ref:field  # Reference output from previous step
```

### **Compensation (Saga Pattern)**

Define how to undo actions if something fails:

```plix
plan [
  task create_user := api.create(data: user_data)
  task send_email := api.email(to: create_user.ref:email)
  
  # If send_email fails, delete the user
  compensate create_user -> api.delete_user(id: create_user.ref:id)
  compensate send_email -> api.cancel_email(id: send_email.ref:id)
]
```

**Compensation executes in REVERSE order:**
1. If `send_email` fails → cancel email, then delete user
2. If `create_user` fails → no compensation needed

---

## 🔍 **Evidence and Verification**

### **Evidence Requirements**

Specify what evidence must exist before/after execution:

```plix
evidence
  require plix://witness/schema_before
  produce plix://witness/schema_after
  produce plix://witness/migration_log
```

**Evidence Types:**
- `require` - Must exist before execution
- `produce` - Will be created during execution

### **Verification**

PLIx uses cryptographic verification:
- **Hash chains** - Ensure evidence integrity
- **Signatures** - Prove authenticity
- **Constraint replay** - Verify claims deterministically

```typescript
// Verify evidence
import { verifyEvidence } from '@aimos/plix/verifier';

const result = await verifyEvidence(intent, evidenceDAG);
if (result.passed) {
  console.log('Evidence valid!');
}
```

---

## 🚨 **Error Handling**

### **Retry Logic**

Handle transient failures with retry:

```plix
plan [
  task api_call := api.fetch_data()
    retry 3 backoff exponential(100ms, 2s) jitter
]
```

**Parameters:**
- `3` - Maximum attempts
- `exponential(100ms, 2s)` - Backoff from 100ms to 2s
- `jitter` - Add randomness to prevent thundering herd

### **Fallback Strategies**

Provide alternative actions if primary fails:

```plix
plan [
  task primary := api.primary_endpoint()
  task backup := api.backup_endpoint()
  
  fallback primary backup
]
```

### **Error Clauses**

Handle specific error types:

```plix
plan [
  task connect := api.connect()
    on_error: net.timeout -> retry
    on_error: net.unreachable -> fallback use_cache
    on_error: auth.denied -> fail
]
```

---

## 💡 **Best Practices**

### **1. Keep Constraints Pure**

✅ **Good:**
```plix
con:balance >= 100
con:user_authenticated == true
```

❌ **Bad:**
```plix
con:update_database() == true  # Side effects in constraint!
```

### **2. Use Meaningful Names**

✅ **Good:**
```plix
task check_inventory := api.check_stock(product_id: product)
```

❌ **Bad:**
```plix
task step1 := api.a(x: y)
```

### **3. Specify Dependencies Explicitly**

✅ **Good:**
```plix
depends charge_card <- verify_inventory
depends send_confirmation <- charge_card
```

❌ **Bad:**
```plix
# No dependencies specified - execution order unclear
```

### **4. Always Add Compensation for Mutations**

✅ **Good:**
```plix
task create_order := api.create(data: order)
compensate create_order -> api.cancel_order(id: create_order.ref:id)
```

❌ **Bad:**
```plix
task create_order := api.create(data: order)
# No compensation - can't rollback!
```

### **5. Use Confidence Thresholds**

```plix
telemetry:
  confidenceThresholds:
    minimum: 0.80   # Fail if confidence < 80%
    warning: 0.90   # Warn if confidence < 90%
```

---

## 🔧 **Troubleshooting**

### **Problem: Parse Errors**

**Error:** "Invalid tag format"

**Solution:** Ensure tags follow format:
```plix
ent:plix://namespace/path#rev@hash
```

---

### **Problem: Circular Dependencies**

**Error:** "Circular dependency detected"

**Solution:** Check your `depends` clauses:
```plix
# BAD:
depends step1 <- step2
depends step2 <- step1  # Circular!

# GOOD:
depends step2 <- step1
depends step3 <- step2
```

---

### **Problem: Type Errors**

**Error:** "Effect check failed: net not allowed"

**Solution:** Check context capabilities:
```typescript
effectChecker.registerContext('myContext', {
  io: true,
  net: true  // Add required effects
});
```

---

### **Problem: Low Confidence**

**Error:** "Confidence below minimum threshold"

**Solution:**
1. Add retry logic
2. Use fallback strategies
3. Increase confidence threshold if acceptable
4. Improve action reliability

---

## 📚 **Examples**

### **Example 1: Database Migration**

```plix
ensure ent:plix://db/schema
  act:migrate
  requires
    con:schema_intact == true
    con:backup_complete == true
  ensures
    con:migration_success == true
    con:no_data_loss == true
  evidence
    require plix://witness/schema_before
    require plix://witness/backup_complete
    produce plix://witness/schema_after
    produce plix://witness/migration_log
  plan [
    task backup := api.backup_database()
    task migrate := api.run_migration(version: "v2.0")
    task validate := api.validate_schema()
    depends migrate <- backup
    depends validate <- migrate
    compensate migrate -> api.rollback_migration()
  ]
```

### **Example 2: Distributed Workflow**

```plix
ensure ent:plix://workflow/order_processing
  act:process_order
  requires
    con:inventory_available == true
    con:payment_valid == true
  ensures
    con:order_complete == true
  plan [
    task verify_inventory := inventory.check(product_id: order.product)
    task charge_card := payment.charge(amount: order.total)
    task ship_order := shipping.create_shipment(order_id: order.id)
    task send_confirmation := email.send(to: order.customer)
    
    depends charge_card <- verify_inventory
    depends ship_order <- charge_card
    depends send_confirmation <- ship_order
    
    compensate charge_card -> payment.refund(transaction_id: charge_card.ref:id)
    compensate ship_order -> shipping.cancel(shipment_id: ship_order.ref:id)
  ]
    retry 2 backoff exponential(500ms, 5s)
```

---

## 🎯 **Next Steps**

1. **Read the [Developer Guide](./DEVELOPER_GUIDE.md)** for advanced topics
2. **Try the [Tutorials](./TUTORIALS.md)** for hands-on learning
3. **Explore [Examples](../examples/)** for real-world use cases
4. **Join the Community** for support and discussions

---

**Happy PLIx coding!** 🚀✨

