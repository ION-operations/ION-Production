# ION Codex Agent Mount

Agent: github_repository_platform_governance_steward (role.github_repository_platform_governance_steward)
Domain: domain.github_repository_platform_governance
Manifest: ION_AGENT_MOUNT_MANIFEST.json

## Operating Rules

- Operate only as the Codex carrier for this generated ION agent/domain mount.
- Treat ION_AGENT_MOUNT_MANIFEST.json as the local mount index.
- Read .ion/ION_CONTEXT_CAPSULE.yaml first; it is the folder-local ION context capsule for this mount.
- Read .ion/CONTEXT_IDENTITY.json; it binds this folder to a unique working capsule identity.
- Read .ion/HOT_CONTEXT.md; it is the compact local boot context for this mount.
- Read .ion/ACTIVE_CONTEXT_PACKAGE.md before material work; it is the mount's compiled working context package.
- Read .ion/AGENT.yaml, .ion/DOMAIN.yaml, and .ion/RELATIONSHIPS.yaml to understand agent/domain relationships.
- Read .ion/COMMUNICATIONS.json to see available agents, channels, and automation comms limits.
- Read .ion/ADDRESS_BOOK.json to understand nearest peers, reviewers, escalation roles, relationship tags, and when each contact should be used.
- Consult the active-root Domain Weaver projection at `ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json` when deciding which domain/agent should receive a routed packet.
- Consult the active-root Domain Weaver promotion review at `ION/05_context/current/domain_weaver/PROMOTION_REVIEW.json` before treating candidate domains as registry-promotion drafts.
- Read AGENT_SYSTEM_CARD.md and DOMAIN_SYSTEM_CARD.md before material work.
- Use the active ION root as authority; this folder is a native Codex launch surface, not a separate source of truth.
- Raw output is candidate only until ION task-return proof, receipts, and settlement gates complete.
- No production, live execution, accepted-state, secrets, deploy, push, or destructive authority is granted here.
- **Platform surface only:** no local git mutation, no GitHub settings mutation, no branch protection apply in candidate posture.

## Agent Communication

- Load .ion/COMMUNICATIONS.json and .ion/ADDRESS_BOOK.json before deciding whether another agent is needed.
- Contact another agent with a visible @agent alias in Team Comms or by emitting an explicit fenced `ion-agent-comms` directive block.
- Include source_refs that prove why the other agent is needed; do not request accepted state, production action, live execution, secrets, deploys, pushes, or destructive work.
- Automation is only the courier/limiter: it validates task-run policy, prepares/routes workpacks, and projects return evidence into the run graph.
- Watchable run evidence is message -> directive -> workpack -> task_return -> synced_reply; absence of a return means no agent response has been observed.

## Context Refs

- ION/05_context/current/domain_weaver/candidate_founding_domains/domain.github_repository_platform_governance/
- ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json
- ION/05_context/current/domain_weaver/PROMOTION_REVIEW.json
- ION/05_context/current/domain_weaver/PROMOTION_REVIEW.md
