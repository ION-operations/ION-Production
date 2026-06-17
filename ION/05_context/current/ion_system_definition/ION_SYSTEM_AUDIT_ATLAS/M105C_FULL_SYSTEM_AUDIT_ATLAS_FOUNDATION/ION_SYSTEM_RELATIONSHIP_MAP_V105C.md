# ION System Relationship Map v105C

Status: sandbox candidate relationship map  
Posture: `LOCAL_SANDBOX_PARTIAL_MOUNT`

## Top-Level Flow

```text
Operator / Braden
  -> Persona / Browser GPT carrier
  -> Relay / grounding + route selection
  -> Steward / acceptance + settlement + risk
  -> JOC/Cockpit / visible control plane
  -> Domain Weave / domain graph + steward routing + impact checks
  -> Agent domains / role-specific context + local config
  -> Codex queue / bounded worker
  -> Runtime proof / receipts / hashes / touched paths
  -> Steward settlement
  -> Living Encyclopedia currentness update
```

## Control Plane Edges

```text
Living Encyclopedia
  governs -> Design Quality Gates
  route-deeper -> Context Packages
  currentness input -> JOC/Cockpit

Action Branching
  exposes -> bounded route capsules
  owns -> branch_context, gateway_core, latest_context, project_workbench,
          runtime_services, codex_queue, agent_swarm, browser_queue,
          supabase_cockpit, context_graph, worker_shift, receipts

JOC/Cockpit
  displays -> queue status, agents, service health, receipts, current packets
  must call -> broker/runner for starts
  must not -> raw shell launch
```

## Domain Weave Edges

```text
Domain Weave
  maps -> domains, stewards, ownership, edges
  checks -> impact and required contacts
  emits -> dry-run activation plans, settlement receipts
  cannot by itself -> claim accepted state or authorize real mutation
```

## Proof Edges

```text
Runtime
  emits -> REQUIRED_READ_EVIDENCE.json, TOUCHED_PATHS.json, RUN_POSTURE.json,
           RETURN_CONTRACT_STATUS.json

AI output
  explains -> findings and reasoning
  cannot -> become proof or state by itself
```

## Known Broken Edge

```text
ion_context_proof_gate.py / ion_template_action_gate.py
  currently parse -> worker markdown
  should validate -> machine proof artifacts
  status -> CONFIRMED_DEFECT / QUARANTINE
```

