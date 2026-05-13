# Chapter 51: Policy Emission: OPA/Rego Integration

**Part:** V - Implementation  
**Chapter:** 51  
**Target Word Count:** 2,500-3,000 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)

---

## Section 51.1: OPA Integration

OPA (Open Policy Agent) integration provides policy evaluation for PLIx constraints, enabling fail-fast policy enforcement before execution.

**OPA Overview**

OPA provides:

- **Policy Engine:** Decoupled policy evaluation engine
- **Rego Language:** Declarative policy language
- **Sidecar Pattern:** OPA runs as sidecar service
- **Policy Evaluation:** Fast policy evaluation via HTTP API

OPA enables decoupled policy enforcement, supporting policy-as-code practices.

**OPA Sidecar Integration**

OPA sidecar integration:

```typescript
interface OPAClient {
  evaluate(policy: string, input: any): Promise<boolean>;
}

class OPASidecarClient implements OPAClient {
  private baseUrl: string;
  
  constructor(baseUrl: string = "http://localhost:8181") {
    this.baseUrl = baseUrl;
  }
  
  async evaluate(policy: string, input: any): Promise<boolean> {
    const response = await fetch(`${this.baseUrl}/v1/data/plix/policy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        input: input
      })
    });
    
    if (!response.ok) {
      throw new Error(`OPA evaluation failed: ${response.statusText}`);
    }
    
    const result = await response.json();
    return result.result?.allow === true;
  }
}
```

OPA sidecar integration enables policy evaluation via HTTP API, supporting decoupled policy enforcement.

**Policy Gate Implementation**

Policy gate implementation:

```typescript
async function evaluatePolicyGate(
  constraints: string[],
  nodeParams: Record<string, any>,
  entity_tag: string | undefined,
  opaClient: OPAClient
): Promise<boolean> {
  // Compile constraints to Rego (includes entity tag context)
  const regoPolicy = compileConstraintsToRego(constraints, entity_tag);
  
  // Add entity tag to input for policy evaluation
  const policyInput = {
    ...nodeParams,
    entity_tag: entity_tag  // Include entity tag in policy input
  };
  
  // Evaluate policy
  const allowed = await opaClient.evaluate(regoPolicy, policyInput);
  
  if (!allowed) {
    throw new PolicyDeniedError(
      `Policy denied for constraints: ${constraints.join(', ')}` +
      (entity_tag ? ` (entity: ${entity_tag})` : '')
    );
  }
  
  return true;
}

async function executeWithPolicyGate(
  ir: IRPlan,
  executor: NodeExecutor,
  opaClient: OPAClient
): Promise<ExecutionResult> {
  const results: Record<string, any> = {};
  const entity_tag = ir.entityTag;  // Get entity tag from IR
  
  for (const node of ir.nodes) {
    // Evaluate policy gate before execution (includes entity tag)
    const policyPassed = await evaluatePolicyGate(
      ir.constraints,
      node.params,
      node.entityTag || entity_tag,  // Use node entity tag or IR entity tag
      opaClient
    );
    
    if (!policyPassed) {
      throw new PolicyDeniedError(`Policy denied for node: ${node.id}`);
    }
    
    // Execute node
    const output = await executor.exec(node.id, node.action, node.params);
    results[node.id] = output;
  }
  
  return { results };
}
```

Policy gate implementation enforces constraints before execution, ensuring policy compliance.

**OPA Integration Benefits**

OPA integration provides:

- **Decoupled Policy:** Policy evaluation decoupled from execution
- **Fail-Fast:** Policy enforcement before execution
- **Policy-as-Code:** Policies defined as code (Rego)
- **Scalability:** OPA sidecar scales independently

These benefits enable reliable policy enforcement with decoupled architecture.

---

## Section 51.2: Rego Generation

Rego generation transforms PLIx constraints into Rego policy language, enabling automatic policy generation from intent contracts.

**Rego Language Overview**

Rego provides:

- **Declarative Syntax:** Declarative policy language
- **Package Structure:** Package-based organization
- **Rules:** Rule-based policy definition
- **Expressions:** Boolean expressions for conditions

Rego enables declarative policy definition, supporting policy-as-code practices.

**Constraint → Rego Translation**

Constraint to Rego translation:

```typescript
function compileConstraintsToRego(
  constraints: string[],
  entity_tag: string | undefined = undefined,
  packageName: string = "plix.policy"
): string {
  const regoRules = constraints.map((constraint, index) => {
    const regoExpr = translateConstraintToRego(constraint);
    return `    ${regoExpr}  # c${index}`;
  }).join('\n');
  
  // Add entity tag check if provided
  const entityTagRule = entity_tag 
    ? `    input.entity_tag = "${entity_tag}"  # Entity tag check\n`
    : '';
  
  return `package ${packageName}

default allow = false

allow {
${entityTagRule}${regoRules}
}
`;
}

function translateConstraintToRego(constraint: string): string {
  // Translate PLIx constraint to Rego expression
  let regoExpr = constraint;
  
  // Replace operators
  regoExpr = regoExpr.replace(/==/g, '=');
  regoExpr = regoExpr.replace(/<=/g, '<=');
  regoExpr = regoExpr.replace(/>=/g, '>=');
  regoExpr = regoExpr.replace(/&&/g, 'and');
  regoExpr = regoExpr.replace(/\|\|/g, 'or');
  regoExpr = regoExpr.replace(/!/g, 'not ');
  
  // Handle variable references
  regoExpr = regoExpr.replace(/(\w+)/g, (match) => {
    // Check if it's a variable reference
    if (match.includes('.')) {
      return `input.${match}`;
    }
    return `input.${match}`;
  });
  
  return regoExpr;
}
```

Constraint to Rego translation generates Rego policies from PLIx constraints, enabling automatic policy generation.

**Rego Policy Examples**

Rego policy examples:

```rego
# Example 1: Duration constraint with entity tag
package plix.booking

default allow = false

allow {
    input.entity_tag = "plix://room/meeting_room"  # Entity tag check
    input.duration <= 4
}

# Example 2: Multiple constraints with entity tag
package plix.booking

default allow = false

allow {
    input.entity_tag = "plix://room/meeting_room"  # Entity tag check
    input.duration <= 4
    input.calendar_conflicts == "none"
    input.user_age >= 18
}

# Example 3: Complex constraint with entity tag
package plix.booking

default allow = false

allow {
    input.entity_tag = "plix://room/meeting_room"  # Entity tag check
    input.duration <= 4
    input.room_available == true
    not input.blacklisted_user
}
```

Rego policy examples demonstrate constraint translation, showing how PLIx constraints become Rego policies.

**Rego Generation Benefits**

Rego generation provides:

- **Automatic Generation:** Constraints automatically become policies
- **Declarative Syntax:** Declarative policy definition
- **Standard Format:** Standard Rego format enables tool integration
- **Maintainability:** Policies defined as code, version-controlled

These benefits enable automatic policy generation from intent contracts.

---

## Section 51.3: Policy Evaluation

Policy evaluation provides runtime policy enforcement, ensuring constraints are satisfied before execution.

**Policy Evaluation Flow**

Policy evaluation flow:

```typescript
async function evaluatePolicy(
  regoPolicy: string,
  input: Record<string, any>,
  opaClient: OPAClient
): Promise<PolicyResult> {
  try {
    // Load policy into OPA
    await opaClient.loadPolicy(regoPolicy);
    
    // Evaluate policy
    const allowed = await opaClient.evaluate(regoPolicy, input);
    
    return {
      allowed,
      reason: allowed ? "Policy passed" : "Policy denied",
      constraints: extractConstraints(regoPolicy)
    };
  } catch (error) {
    return {
      allowed: false,
      reason: `Policy evaluation error: ${error.message}`,
      constraints: []
    };
  }
}

interface PolicyResult {
  allowed: boolean;
  reason: string;
  constraints: string[];
}
```

Policy evaluation flow provides runtime policy enforcement, ensuring constraints are satisfied.

**Policy Gate Integration**

Policy gate integration with PLIx execution:

```typescript
async function executeWithPolicyGates(
  ir: IRPlan,
  executor: NodeExecutor,
  opaClient: OPAClient
): Promise<ExecutionResult> {
  // Compile constraints to Rego (includes entity tag)
  const entity_tag = ir.entityTag;
  const regoPolicy = compileConstraintsToRego(ir.constraints, entity_tag);
  
  const results: Record<string, any> = {};
  
  for (const node of ir.nodes) {
    // Add entity tag to input for policy evaluation
    const policyInput = {
      ...node.params,
      entity_tag: node.entityTag || entity_tag  // Include entity tag
    };
    
    // Evaluate policy gate
    const policyResult = await evaluatePolicy(regoPolicy, policyInput, opaClient);
    
    if (!policyResult.allowed) {
      // Policy denied: fail fast
      throw new PolicyDeniedError(
        `Policy denied for node ${node.id} (entity: ${policyInput.entity_tag}): ${policyResult.reason}`
      );
    }
    
    // Execute node
    const output = await executor.exec(node.id, node.action, node.params);
    results[node.id] = output;
  }
  
  return { results };
}
```

Policy gate integration enforces policies before execution, ensuring constraint compliance.

**Policy Evaluation Benefits**

Policy evaluation provides:

- **Fail-Fast:** Policy enforcement before execution
- **Constraint Compliance:** Ensures constraints are satisfied
- **Error Reporting:** Clear policy denial reasons
- **Runtime Enforcement:** Runtime policy enforcement

These benefits enable reliable constraint enforcement through policy evaluation.

---

## Section 51.4: Policy Testing

Policy testing ensures Rego policies are correct, enabling policy validation and verification.

**Policy Unit Tests**

Policy unit tests:

```typescript
describe('Rego Policy Generation', () => {
  it('generates Rego for duration constraint', () => {
    const constraints = ['duration <= 4h'];
    const entity_tag = 'plix://room/meeting_room';
    const rego = compileConstraintsToRego(constraints, entity_tag);
    
    expect(rego).toContain('package plix.policy');
    expect(rego).toContain('default allow = false');
    expect(rego).toContain('input.duration <= 4');
    expect(rego).toContain(`input.entity_tag = "${entity_tag}"`);
  });
  
  it('generates Rego for multiple constraints', () => {
    const constraints = [
      'duration <= 4h',
      'calendar_conflicts == none'
    ];
    const entity_tag = 'plix://room/meeting_room';
    const rego = compileConstraintsToRego(constraints, entity_tag);
    
    expect(rego).toContain('input.duration <= 4');
    expect(rego).toContain('input.calendar_conflicts = "none"');
    expect(rego).toContain(`input.entity_tag = "${entity_tag}"`);
  });
});

describe('Policy Evaluation', () => {
  it('evaluates policy correctly', async () => {
    const rego = `package plix.policy
default allow = false
allow {
    input.entity_tag = "plix://room/meeting_room"
    input.duration <= 4
}`;
    
    const opaClient = new OPASidecarClient();
    const result = await evaluatePolicy(rego, { 
      duration: 2,
      entity_tag: 'plix://room/meeting_room'
    }, opaClient);
    
    expect(result.allowed).toBe(true);
  });
  
  it('denies policy violation', async () => {
    const rego = `package plix.policy
default allow = false
allow {
    input.entity_tag = "plix://room/meeting_room"
    input.duration <= 4
}`;
    
    const opaClient = new OPASidecarClient();
    const result = await evaluatePolicy(rego, { 
      duration: 5,
      entity_tag: 'plix://room/meeting_room'
    }, opaClient);
    
    expect(result.allowed).toBe(false);
  });
  
  it('denies wrong entity tag', async () => {
    const rego = `package plix.policy
default allow = false
allow {
    input.entity_tag = "plix://room/meeting_room"
    input.duration <= 4
}`;
    
    const opaClient = new OPASidecarClient();
    const result = await evaluatePolicy(rego, { 
      duration: 2,
      entity_tag: 'plix://room/other_room'  # Wrong entity tag
    }, opaClient);
    
    expect(result.allowed).toBe(false);
  });
});
```

Policy unit tests ensure Rego policies are correct, enabling policy validation.

**Policy Integration Tests**

Policy integration tests:

```typescript
describe('Policy Gate Integration', () => {
  it('enforces policy before execution', async () => {
    const ir: IRPlan = {
      intent: "Book a room",
      entityTag: "plix://room/meeting_room",  # Entity tag
      nodes: [{
        id: "reserve",
        action: "api.reserve_room",
        entityTag: "plix://room/meeting_room",  # Entity tag
        params: { duration: 2 },
        deps: []
      }],
      constraints: ['duration <= 4h']
    };
    
    const opaClient = new OPASidecarClient();
    const executor = new MockExecutor();
    
    const result = await executeWithPolicyGates(ir, executor, opaClient);
    
    expect(result.results).toBeDefined();
    expect(executor.executed).toBe(true);
  });
  
  it('fails fast on policy violation', async () => {
    const ir: IRPlan = {
      intent: "Book a room",
      entityTag: "plix://room/meeting_room",  # Entity tag
      nodes: [{
        id: "reserve",
        action: "api.reserve_room",
        entityTag: "plix://room/meeting_room",  # Entity tag
        params: { duration: 5 },
        deps: []
      }],
      constraints: ['duration <= 4h']
    };
    
    const opaClient = new OPASidecarClient();
    const executor = new MockExecutor();
    
    await expect(
      executeWithPolicyGates(ir, executor, opaClient)
    ).rejects.toThrow(PolicyDeniedError);
    
    expect(executor.executed).toBe(false);
  });
});
```

Policy integration tests ensure policy gates work correctly with execution, enabling end-to-end validation.

**Policy Testing Benefits**

Policy testing provides:

- **Correctness:** Ensures policies are correct
- **Validation:** Policy validation before deployment
- **Integration:** End-to-end policy integration testing
- **Reliability:** Reliable policy enforcement

These benefits enable reliable policy enforcement through comprehensive testing.

---

## Chapter 51 Summary

Policy emission provides OPA integration, Rego generation, policy evaluation, and policy testing **with tag-based entity references**. OPA integration enables decoupled policy evaluation via sidecar **with tag-based entity filtering**. Rego generation transforms PLIx constraints into Rego policies **with entity tag checks**. Policy evaluation provides runtime policy enforcement **for specific entities via tags**. Policy testing ensures policies are correct and reliable **including tag-based policy validation**.

**Tags enable canonical identity** throughout policy emission: Rego policies include entity tag checks (`input.entity_tag = "plix://room/meeting_room"`), policy evaluation filters by entity tags, policy gates enforce constraints for specific entities via tags, and policy testing validates tag-based policies. Tags enable unambiguous entity references that survive technology changes, enabling intent-aware policy enforcement with canonical identity.

**Next:** Part V Implementation complete. The unified textbook now provides comprehensive coverage of PLIx language design, implementation, and integration with AIM-OS systems.

---

**Word Count:** ~2,700 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)  
**Cross-References:**
- Chapter 5: Tag System (tag format and components)
- Chapter 7: Enhanced Constraints (constraint language with tags)
- Chapter 15: Tag Registry (tag resolution process)

