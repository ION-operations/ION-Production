# ION True Name and Context Binding Protocol v0.1

Status: candidate local protocol
Packet: CODEX_B2_TRUE_NAME_BINDING
Production authority: false
Live execution authority: false
Accepted state claim: false
Secrets authority: false

## Core Law

A worker true name is an action-bound identity, not a persona.

The true name describes one bounded movement by one carrier lane. It may help
route context, leases, receipts, and handoffs, but it does not create a
permanent identity and it does not grant authority.

Example:

```text
codex_a2_vault_move
```

This parses as:

```yaml
carrier: codex
lane: A
sequence: 2
mission_movement: vault_move
inferred_domain: security.vault
```

## Binding Requirements

A true-name binding must declare:

- one or more folder domains;
- one or more context package IDs;
- one or more allowed path scopes;
- expected receipts for sign-on, lease, sign-off, validation, or settlement.

If the context package IDs are missing, the binding is incomplete and not ready.
An incomplete binding may be observed or repaired, but it may not approve path
or lease access.

## Path and Lease Law

A worker may only touch a path when both are true:

- the path is covered by the true-name binding allowed path scopes;
- the path domain is compatible with the binding folder domains.

The active Worker Shift lease must also cover the path. Binding approval alone
does not replace Worker Shift lease conflict detection.

Parent scopes cover child paths. A child file scope does not automatically grant
the parent directory.

## Authority Boundary

A true name cannot grant:

- production authority;
- live execution authority;
- accepted-state authority;
- secret read authority;
- deployment authority;
- GitHub push authority.

Vault or environment paths are path scopes only. A binding may coordinate lease
claims for those paths when explicitly assigned, but secret values remain
contained by vault and security boundary law.

## Lifecycle

A true name expires, settles, or is superseded. It does not become a permanent
persona or role.

Signed-off, expired, settled, released, failed, or superseded true names cannot
claim new leases without a new sign-on and an active binding.

## Candidate Helper

Implementation:

```text
ION/04_packages/kernel/ion_true_name_binding.py
```

Current context holder:

```text
ION/05_context/current/worker_shift/true_name_bindings/
```

Template:

```text
ION/07_templates/worker_shift/TRUE_NAME_BINDING_TEMPLATE.md
```
