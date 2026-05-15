# ION Custom GPT Project Hash Identity and Helixion Handshake

## Status

Candidate contract. `ion_project_hash` is a public project identity and routing
locator. It is not a credential and must not be treated as authorization by
itself.

## Core Rule

The hash is the project identity. Helixion is the authorization authority.

The Custom GPT may carry or send:

- `ion_project_hash`
- branch hashes
- package hashes
- challenge nonce
- carrier instance id

Helixion must decide access server-side from account/OAuth/session approval,
subject-project ACL, claim status, package proof, receipt scope, and expiry.

## Public Folder Files

Recommended project files:

```text
ION_PROJECT_IDENTITY.yaml
ION_HASH_BRANCHES.yaml
ION_VALIDATION_POINTERS.yaml
ION_CONTEXT_CAPSULE.yaml
.ionignore
```

These are intentionally exportable and must not contain bearer tokens, private
keys, credentials, session cookies, vault values, or ChatGPT account identity.

## Key Branches

Folder key branches are non-secret validation pointers, hashes, signatures, or
Helixion request pointers. They prove what the project claims; they do not grant
access.

Examples:

- `root_identity`
- `context_mesh`
- `continuity_package`
- `receipt_chain`
- `action_capability`
- `git_preview`
- `folder_capsule`
- `public_signature`

## Multi-User Isolation

One Custom GPT can serve many users only when Helixion enforces subject plus
project access control. A shared Action API key authenticates the gateway only;
it does not identify the human user. OAuth or an explicit Helixion claim flow is
required for private project context.

If an unauthorized user presents another project hash, Helixion must return a
blind response:

```yaml
status: requires_claim_or_forbidden
private_metadata_returned: false
```

Do not reveal project title, files, package list, owner, receipts, preview URLs,
or private metadata before authorization.

## Capability Grants

Capability grants are short-lived, scoped, revocable, receipt-required, and
bound to subject, project hash, carrier instance, and allowed actions. They are
not written to project folders and are never exported in continuity packages.

## Non-Exportable Boundary

Never export private signing keys, bearer tokens, OAuth tokens, session cookies,
vault contents, credentials, capability tokens, raw account identifiers unless
explicitly approved, or hidden chain-of-thought.
