---
schema_id: ion.architecture_signal_journal.v1
status: candidate_signal
created_at: 2026-05-15T00:18:00Z
created_by: ChatGPT Browser / ION front-door carrier
source_thread: live operator discussion during Project Workbench Context Capsule v0 implementation
related_objective: V120_CHATGPT_BROWSER_MCP_CONNECTOR_AND_CORRECT_CARRIER_ONBOARDING
related_packets:
  - PCKT-ION-PROJECT-WORKBENCH-CONTEXT-CAPSULE-V0-IMPLEMENT-AND-TEST-20260514
  - PCKT-ION-PROJECT-WORKBENCH-CONTEXT-CAPSULE-V0-PROOF-REPAIR-AND-QUEUE-LANE-SMOKE-20260515
accepted_state_claim: false
production_authority: false
live_execution_authority: false
---

# Carrier-Portable Working Intelligence Journal

## Summary

This journal captures an operator/ION design discussion about why ION works and what must be preserved as the project evolves.

The key point is that ION is not merely a prompt chain, workflow runner, or audit wrapper. ION is intended to externalize the project-relevant working intelligence that capable humans and high-inference AI carriers normally hold tacitly: context loaded, evidence used, situation classification, template chosen, action boundary, validation result, blocker, and next packet.

This is not about exposing hidden model chain-of-thought. It is about preserving the operational context that makes work intelligible, portable, and reusable across carriers.

## Core thesis

ION makes intelligence carrier-portable.

A normal AI workflow depends heavily on the hidden qualities of the current model/session: current chat context, model intuition, implicit memory, and unrecorded reasoning around why an output was produced.

ION shifts the dependency to durable project structure:

```text
context loaded
+ template selected
+ evidence used
+ action taken
+ proof emitted
+ blocker recorded
+ next packet compiled
+ domain context updated
```

A later carrier does not need the prior carrier's private hidden state. It inherits the externalized working intelligence through context proofs, template-action proofs, receipts, deltas, domain memory, and settlement records.

## Template-bound inference economy

Templates are not only audit forms. They are inference compression.

High-inference carriers are used when a situation is new, a domain is unbound, context is unclear, or the existing template fails. Once the situation is understood, ION binds it into a reusable template/protocol/packet contract so future workers can operate without rediscovering the workflow.

Pattern:

```text
new situation
→ high-inference reasoning
→ template/protocol created or amended
→ future workers follow the bound shape
→ failures become documented deltas
→ domain context improves
```

Lower-inference or cheaper carriers can safely operate inside known domains because the template tells them what context to load, what proof is required, what actions are allowed, what output is valid, and how to report blockers.

## Working context externalization

ION should preserve the decision-relevant context that competent human operators often carry implicitly but do not fully document.

This includes:

```text
why this route was chosen
what was already tried
which evidence was loaded
which assumption is stale
what was not done
what risk is being avoided
what action boundary was respected
what would need review later
```

This is human-grade tacit workflow context made durable for AI carriers.

## Anti-drift mechanism

Drift and hallucination are reduced when carriers are forced to reattach each serious move to:

```text
source context
domain state
template law
receipt trail
validation result
accepted deltas
```

Instead of reverse-engineering why an output happened from the output alone, future carriers inspect the context/action proof and the surrounding domain history.

This turns worker failure into useful signal. A template-invalid return is not just failure; it can reveal unclear proof requirements, missing context, stale service state, or a domain boundary that needs a new subtype.

## Sequential swarm bootstrap mode

ION's current bootstrap mode can be single-carrier and sequential while still being swarm-shaped.

A single carrier can walk the domain graph one branch at a time:

```text
situation
→ choose first domain
→ load that domain context
→ reason / inspect / produce baton
→ carry baton into next domain
→ compare / reconcile
→ settle back into whole-project state
```

Parallelism is an optimization, not the essence of swarm. The essence is relational domain sequencing, context rehydration, branch batons, and fan-in settlement.

## Prompt-to-swarm routing

A user prompt should not be answered from the visible chat window by default. It should be treated as a routing event.

ION should resolve:

```text
What situation is this?
Which domains does it touch?
Which agents have the best context?
Which branch context must be rehydrated?
What can be answered directly?
What requires worker execution?
What requires settlement before becoming project state?
```

Then ION compiles the smallest sufficient context/tool/template packet for the next carrier.

## Proceed requires rehydration

A continuation signal such as "proceed" should not mean "continue from whatever remains in the model context." It should mean:

```text
rehydrate the active work object and continue from durable project state
```

Required resolution before acting:

```text
active objective
active work packet
current queue/worker status
relevant domain capsules
latest receipts
known blockers
next lawful move
```

The current chat context guides the lookup, but it is not the authority.

## Relation to current implementation work

During this discussion, the Project Workbench Context Capsule v0 implementation was accepted by Codex with proof:

```text
implemented:
- ion_project_context_capsule
- ion_project_file_slice_read
- connector routing for both tools
- policy allowlist updates
- Action Gateway validation approval metadata

tests:
- 60 passed in 8.17s
```

A follow-up smoke worker found the repo/source contract and tests are current at 65 tools, but the live MCP listener at 127.0.0.1:8765 remains stale at 63 tools. The blocker is live-listener reload, not implementation failure.

## Proposed laws / names to preserve

```text
CARRIER_AGNOSTIC_WORKING_INTELLIGENCE
ION externalizes project-relevant intelligence so future carriers can continue from structured reality rather than hidden session state.

TEMPLATE_BOUND_INFERENCE_ECONOMY
High-inference carriers bind new situations into templates; lower-inference carriers execute known situations through those templates.

WORKING_CONTEXT_EXTERNALIZATION
ION captures the operational context that makes decisions intelligible without requiring hidden chain-of-thought.

PROMPT_TO_SWARM_ROUTING_LAW
A prompt is a routing event into domains/agents, not merely a request answered from current chat memory.

PROCEED_REQUIRES_REHYDRATION
Continuation requires resolving active packets, receipts, domains, queue state, and blockers from durable project state.

SEQUENTIAL_SWARM_BOOTSTRAP_MODE
ION can execute a multi-domain swarm through one carrier sequentially while preserving branch identity and batons.
```

## Next consideration

Promote these signals into the context-system / scheduler / template doctrine if accepted. In particular, connect them to:

```text
ION/02_architecture/LAWFUL_ORCHESTRATION_SCHEDULER_PROTOCOL.md
ION/02_architecture/ION_AGENT_CONTEXT_DYNAMICS_AND_CONTEXT_WINDOW_PROTOCOL.md
ION/02_architecture/ION_AGENT_CONTEXT_CONTINUITY_TIMELINE_AND_ROUTE_MAP_PROTOCOL.md
ION/02_architecture/ION_CONTEXT_AUTHORITY_TEAM_PROTOCOL.md
ION/02_architecture/BOUNDED_PARALLELISM_AND_SETTLEMENT_PROTOCOL.md
```

The product implication is that ION should be framed as a carrier-portable project intelligence runtime, not just a toolchain or automation queue.
