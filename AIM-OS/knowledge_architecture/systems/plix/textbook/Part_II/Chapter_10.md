# Chapter 10: Error Taxonomy and Handling

**Part:** II - Architecture  
**Chapter:** 10  
**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE**  
**Priority:** ⚠️ **HIGH** - Essential for reliability

---

## Introduction

In Chapter 7, we explored the enhanced constraint language—how to express complex intent requirements. But what happens when constraints fail? What happens when network requests timeout? What happens when policies deny access?

PLIx provides a **comprehensive error taxonomy** and **declarative error handling** system that enables robust intent execution. Instead of ad-hoc error handling scattered throughout code, PLIx contracts declare how to handle errors declaratively.

This chapter explores the complete error taxonomy, shows how to declare error handling, and demonstrates error handling patterns. By the end, you'll be able to write robust PLIx contracts that handle errors gracefully and reliably.

---

## Section 10.1: Error Categories

### The Error Taxonomy

PLIx categorizes errors into **8 categories**, each with specific error types:

1. **Network Errors** - Network-related failures
2. **Policy Errors** - Policy and authorization failures
3. **Constraint Errors** - Constraint violation failures
4. **Contract Errors** - Contract precondition/postcondition failures
5. **Proof Errors** - Evidence and witness failures
6. **Auth Errors** - Authentication failures
7. **Resource Errors** - Resource exhaustion failures
8. **Execution Errors** - Execution step failures

### Network Errors

Network errors occur when network operations fail:

- **`net.timeout`** - Network request timed out
- **`net.unreachable`** - Network destination unreachable
- **`net.connection_failed`** - Network connection failed

**When Network Errors Occur:**
- API calls timeout
- Database connections fail
- Service endpoints unreachable
- Network partitions

**Example:**
```plix
plan [
  step call_api
    on_error: net.timeout -> retry with retry(3, 100ms, 2s)
    on_error: net.connection_failed -> retry with retry(2, 500ms, 5s)
]
```

### Policy Errors

Policy errors occur when policies deny operations:

- **`policy.denied`** - Policy denied operation
- **`policy.insufficient_authority`** - Insufficient authority tier
- **`policy.quorum_not_met`** - Required quorum not met

**When Policy Errors Occur:**
- Insufficient permissions
- Authority tier too low
- Quorum requirements not met
- Policy violations

**Example:**
```plix
plan [
  step execute_operation
    on_error: policy.denied -> escalate admin
    on_error: policy.insufficient_authority -> escalate operator
]
```

### Constraint Errors

Constraint errors occur when constraints are violated:

- **`constraint.violated`** - General constraint violation
- **`constraint.precondition_failed`** - Precondition constraint failed
- **`constraint.postcondition_failed`** - Postcondition constraint failed
- **`constraint.invariant_broken`** - Invariant constraint broken

**When Constraint Errors Occur:**
- Preconditions fail (room not available)
- Postconditions fail (migration incomplete)
- Invariants broken (schema corrupted)
- Constraint violations detected

**Example:**
```plix
plan [
  step validate_preconditions
    on_error: constraint.violated -> fail
  step execute_migration
    on_error: constraint.postcondition_failed -> compensate rollback_migration
]
```

### Contract Errors

Contract errors occur when contract conditions fail:

- **`contract.precondition_failed`** - Contract precondition failed
- **`contract.postcondition_failed`** - Contract postcondition failed
- **`contract.compensation_failed`** - Compensation step failed

**When Contract Errors Occur:**
- Contract preconditions not met
- Contract postconditions not achieved
- Compensation steps fail
- Contract violations detected

**Example:**
```plix
plan [
  step execute_operation
    on_error: contract.precondition_failed -> fail
    on_error: contract.postcondition_failed -> compensate rollback
    on_error: contract.compensation_failed -> escalate admin
]
```

### Proof Errors

Proof errors occur when evidence is missing or invalid:

- **`proof.missing`** - Required proof/witness missing
- **`proof.invalid`** - Proof/witness invalid
- **`proof.insufficient`** - Insufficient proof evidence

**When Proof Errors Occur:**
- Required witnesses missing
- Witness validation fails
- Insufficient evidence for verification
- Proof generation fails

**Example:**
```plix
plan [
  step generate_witness
    on_error: proof.missing -> retry with retry(2, 1s, 5s)
    on_error: proof.invalid -> fail
]
```

### Auth Errors

Auth errors occur when authentication fails:

- **`auth.insufficient`** - Insufficient authentication
- **`auth.expired`** - Authentication expired
- **`auth.invalid`** - Invalid authentication credentials

**When Auth Errors Occur:**
- Authentication tokens expired
- Insufficient permissions
- Invalid credentials
- Authentication failures

**Example:**
```plix
plan [
  step authenticate_user
    on_error: auth.expired -> retry with refresh_token
    on_error: auth.invalid -> fail
]
```

### Resource Errors

Resource errors occur when resources are exhausted:

- **`resource.exceeded`** - Resource limit exceeded
- **`resource.unavailable`** - Resource unavailable
- **`resource.throttled`** - Resource throttled

**When Resource Errors Occur:**
- Memory limits exceeded
- CPU limits exceeded
- Rate limits exceeded
- Resource quotas exceeded

**Example:**
```plix
plan [
  step process_data
    on_error: resource.exceeded -> escalate admin
    on_error: resource.throttled -> retry with retry(5, 2s, 30s)
]
```

### Execution Errors

Execution errors occur when execution steps fail:

- **`execution.failed`** - Execution step failed
- **`execution.timeout`** - Execution step timed out
- **`execution.cancelled`** - Execution step cancelled

**When Execution Errors Occur:**
- Step execution fails
- Step execution times out
- Step execution cancelled
- Step dependencies fail

**Example:**
```plix
plan [
  step execute_migration
    on_error: execution.failed -> compensate rollback_migration
    on_error: execution.timeout -> retry with retry(3, 1s, 10s)
    on_error: execution.cancelled -> fail
]
```

---

## Section 10.2: Error Handling Clauses

### The `on_error:` Syntax

Error handling is declared using `on_error:` clauses in plan steps:

**Human-PLIX:**
```plix
plan [
  step execute_migration
    on_error: net.timeout -> retry with retry(3, 100ms, 2s)
    on_error: execution.failed -> compensate rollback_migration
    on_error: constraint.violated -> fail
]
```

**Canonical JSON:**
```json
{
  "plan": [
    {
      "step": "execute_migration",
      "errors": [
        {
          "on": "net.timeout",
          "action": "retry",
          "config": {
            "retry": {
              "max": 3,
              "min_delay": "100ms",
              "max_delay": "2s"
            }
          }
        },
        {
          "on": "execution.failed",
          "action": "compensate",
          "config": {
            "compensate": "rollback_migration"
          }
        },
        {
          "on": "constraint.violated",
          "action": "fail"
        }
      ]
    }
  ]
}
```

**S-form:**
```
(plan
  (step execute_migration
    (on_error net.timeout retry (retry 3 100ms 2s))
    (on_error execution.failed compensate rollback_migration)
    (on_error constraint.violated fail)))
```

### Error Type Matching

Error clauses match errors using:

1. **Exact Match:** `on_error: net.timeout -> retry`
2. **Category Match:** `on_error: net.* -> retry` (matches all network errors)
3. **Wildcard Match:** `on_error: * -> escalate` (matches all errors)

**Matching Priority:**
1. Exact match (most specific)
2. Category match (less specific)
3. Wildcard match (least specific)

**Example:**
```plix
plan [
  step execute_operation
    on_error: net.timeout -> retry          # Exact match (highest priority)
    on_error: net.* -> escalate            # Category match (medium priority)
    on_error: * -> fail                    # Wildcard match (lowest priority)
]
```

### Error Configuration

Error actions can be configured with additional parameters:

**Retry Configuration:**
```plix
on_error: net.timeout -> retry with retry(3, 100ms, 2s)
```
- `3` - Maximum retry attempts
- `100ms` - Minimum delay between retries
- `2s` - Maximum delay between retries
- Optional: `jitter` - Add random jitter to delays

**Compensation Configuration:**
```plix
on_error: execution.failed -> compensate rollback_migration
```
- `rollback_migration` - Step ID or action name to execute

**Escalation Configuration:**
```plix
on_error: policy.denied -> escalate admin
```
- `admin` - Escalation target (admin, operator, or custom)

**Fallback Configuration:**
```plix
on_error: execution.failed -> fallback alternative_step
```
- `alternative_step` - Step ID to execute as fallback

---

## Section 10.3: Error Actions

### Retry Action

The `retry` action retries the step with exponential backoff:

**Syntax:**
```plix
on_error: net.timeout -> retry with retry(3, 100ms, 2s) jitter
```

**Configuration:**
- `max` - Maximum retry attempts
- `min_delay` - Minimum delay between retries
- `max_delay` - Maximum delay between retries
- `jitter` - Optional random jitter

**When to Use Retry:**
- Transient errors (network timeouts, temporary failures)
- Errors that might succeed on retry
- Errors with exponential backoff strategy

**Example:**
```plix
plan [
  step call_api
    retry 3 backoff exponential(100ms, 2s) jitter
    on_error: net.timeout -> retry with retry(3, 100ms, 2s)
]
```

### Compensate Action

The `compensate` action executes compensation logic:

**Syntax:**
```plix
on_error: execution.failed -> compensate rollback_migration
```

**Configuration:**
- `compensate` - Step ID or action name to execute

**When to Use Compensate:**
- Reversible operations (database migrations, reservations)
- Errors requiring cleanup (rollback, release resources)
- Saga pattern compensation

**Example:**
```plix
plan [
  step reserve_room
    compensate release_room
    on_error: execution.failed -> compensate release_room
]
```

### Fail Action

The `fail` action fails the step immediately:

**Syntax:**
```plix
on_error: constraint.violated -> fail
```

**When to Use Fail:**
- Unrecoverable errors (constraint violations, invalid state)
- Errors that shouldn't be retried
- Errors requiring immediate failure

**Example:**
```plix
plan [
  step validate_preconditions
    on_error: constraint.violated -> fail
]
```

### Escalate Action

The `escalate` action escalates to human operators:

**Syntax:**
```plix
on_error: policy.denied -> escalate admin
```

**Configuration:**
- `admin` - Escalation target (admin, operator, or custom)

**When to Use Escalate:**
- Policy violations requiring human review
- Errors requiring human intervention
- Errors beyond automated recovery

**Example:**
```plix
plan [
  step execute_operation
    on_error: policy.denied -> escalate admin
    on_error: resource.exceeded -> escalate operator
]
```

### Fallback Action

The `fallback` action executes an alternative step:

**Syntax:**
```plix
on_error: execution.failed -> fallback alternative_step
```

**Configuration:**
- `alternative_step` - Step ID to execute as fallback

**When to Use Fallback:**
- Errors with alternative execution paths
- Errors requiring different strategies
- Errors with backup plans

**Example:**
```plix
plan [
  step primary_operation
    on_error: execution.failed -> fallback backup_operation
  step backup_operation
    ...
]
```

---

## Section 10.4: Error Handling Examples

### Example 1: Network Timeout Handling

**Scenario:** Database migration with network timeout handling

```plix
plan [
  step execute_migration
    retry 3 backoff exponential(100ms, 2s) jitter
    on_error: net.timeout -> retry with retry(3, 100ms, 2s)
    on_error: net.connection_failed -> retry with retry(2, 500ms, 5s)
    on_error: execution.failed -> compensate rollback_migration
    compensate rollback_migration
]
```

**Error Handling Strategy:**
- Network timeout → Retry with exponential backoff
- Connection failed → Retry with longer delays
- Execution failed → Compensate (rollback migration)

### Example 2: Policy Denied Handling

**Scenario:** Operation requiring policy approval

```plix
plan [
  step execute_operation
    on_error: policy.denied -> escalate admin
    on_error: policy.insufficient_authority -> escalate operator
    on_error: execution.failed -> fail
]
```

**Error Handling Strategy:**
- Policy denied → Escalate to admin
- Insufficient authority → Escalate to operator
- Execution failed → Fail immediately

### Example 3: Constraint Violation Handling

**Scenario:** Precondition validation with constraint violation handling

```plix
plan [
  step validate_preconditions
    on_error: constraint.violated -> fail
    on_error: constraint.precondition_failed -> fail
  step execute_operation
    on_error: constraint.postcondition_failed -> compensate rollback
]
```

**Error Handling Strategy:**
- Constraint violated → Fail immediately
- Precondition failed → Fail immediately
- Postcondition failed → Compensate (rollback)

### Example 4: Complete Error Handling Workflow

**Scenario:** Complete database migration with comprehensive error handling

```plix
plan [
  step validate_preconditions
    on_error: constraint.violated -> fail
    on_error: constraint.precondition_failed -> fail
  
  step execute_migration
    retry 3 backoff exponential(100ms, 2s) jitter
    on_error: net.timeout -> retry with retry(3, 100ms, 2s)
    on_error: net.connection_failed -> retry with retry(2, 500ms, 5s)
    on_error: execution.failed -> compensate rollback_migration
    on_error: execution.timeout -> retry with retry(2, 1s, 10s)
    on_error: constraint.postcondition_failed -> compensate rollback_migration
    compensate rollback_migration
  
  step validate_postconditions
    on_error: constraint.postcondition_failed -> compensate rollback_migration
    on_error: proof.missing -> retry with retry(2, 1s, 5s)
]
```

**Error Handling Strategy:**
- Validation errors → Fail immediately
- Network errors → Retry with backoff
- Execution errors → Compensate or retry
- Constraint errors → Compensate or fail
- Proof errors → Retry or fail

---

## Section 10.5: Error Handling Best Practices

### When to Retry vs Compensate

**Retry When:**
- Error is transient (network timeout, temporary failure)
- Error might succeed on retry
- Error doesn't require cleanup

**Compensate When:**
- Error requires cleanup (rollback, release resources)
- Operation is reversible (database migration, reservation)
- Error requires state restoration

**Example:**
```plix
# Retry: Transient network error
on_error: net.timeout -> retry with retry(3, 100ms, 2s)

# Compensate: Reversible operation
on_error: execution.failed -> compensate rollback_migration
```

### When to Escalate vs Fail

**Escalate When:**
- Error requires human intervention
- Error is policy-related (authorization, approval)
- Error is beyond automated recovery

**Fail When:**
- Error is unrecoverable (constraint violation, invalid state)
- Error shouldn't be retried
- Error requires immediate failure

**Example:**
```plix
# Escalate: Policy violation requiring human review
on_error: policy.denied -> escalate admin

# Fail: Unrecoverable constraint violation
on_error: constraint.violated -> fail
```

### Error Handling Patterns

**Pattern 1: Retry with Exponential Backoff**
```plix
step call_api
  retry 3 backoff exponential(100ms, 2s) jitter
  on_error: net.timeout -> retry with retry(3, 100ms, 2s)
```

**Pattern 2: Compensate on Failure**
```plix
step reserve_room
  compensate release_room
  on_error: execution.failed -> compensate release_room
```

**Pattern 3: Escalate Policy Violations**
```plix
step execute_operation
  on_error: policy.denied -> escalate admin
  on_error: policy.insufficient_authority -> escalate operator
```

**Pattern 4: Fail on Constraint Violations**
```plix
step validate_preconditions
  on_error: constraint.violated -> fail
  on_error: constraint.precondition_failed -> fail
```

**Pattern 5: Fallback Strategy**
```plix
step primary_operation
  on_error: execution.failed -> fallback backup_operation
step backup_operation
  ...
```

### Common Pitfalls

**Pitfall 1: Retrying Unrecoverable Errors**
```plix
# Bad: Retrying constraint violation
on_error: constraint.violated -> retry

# Good: Failing on constraint violation
on_error: constraint.violated -> fail
```

**Pitfall 2: Not Compensating Reversible Operations**
```plix
# Bad: No compensation for reversible operation
step reserve_room
  on_error: execution.failed -> fail

# Good: Compensating reversible operation
step reserve_room
  compensate release_room
  on_error: execution.failed -> compensate release_room
```

**Pitfall 3: Escalating Transient Errors**
```plix
# Bad: Escalating transient network error
on_error: net.timeout -> escalate admin

# Good: Retrying transient network error
on_error: net.timeout -> retry with retry(3, 100ms, 2s)
```

**Pitfall 4: Missing Error Handling**
```plix
# Bad: No error handling
step execute_operation

# Good: Comprehensive error handling
step execute_operation
  on_error: net.timeout -> retry with retry(3, 100ms, 2s)
  on_error: execution.failed -> compensate rollback
  on_error: constraint.violated -> fail
```

---

## Chapter 10 Summary

PLIx provides a comprehensive error taxonomy and declarative error handling system:

1. **Error Categories:** 8 categories covering all error types
2. **Error Handling Clauses:** `on_error:` syntax for declarative error handling
3. **Error Actions:** Retry, compensate, fail, escalate, fallback
4. **Error Examples:** Real-world error handling patterns
5. **Best Practices:** When to use each error action

**Key Takeaways:**
1. **Error Taxonomy:** 8 categories, 25+ error types
2. **Declarative Handling:** `on_error:` clauses declare error handling
3. **Error Actions:** 5 actions (retry, compensate, fail, escalate, fallback)
4. **Best Practices:** Retry transient errors, compensate reversible operations, escalate policy violations, fail unrecoverable errors
5. **Common Pitfalls:** Avoid retrying unrecoverable errors, always compensate reversible operations

**Next:** Chapter 11 explores CMC integration—how PLIx contracts are stored in Context Memory Core with tag-based queries and bitemporal versioning.

---

**Word Count:** ~2,800 words  
**Status:** ✅ **COMPLETE**  
**Cross-References:**
- Chapter 7: Enhanced Constraints (constraint errors)
- Chapter 17: Runtime Implementation (error execution)
- Spec Section 3.1: Error Taxonomy

