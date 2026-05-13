# ION Custom GPT Expansion Plan

Source: ION custom GPT architecture note received on 2026-05-09.

This document captures the new product modules added after the first dAimon orchestration layer. The earlier plan already covered the first principle, product layers, domains, templates, receipts, settlement, generative governance, capability routing, Gemini, MongoDB MCP, enterprise trust, demo video, contest slice, narrative, and non-claims.

The new material expands dAimon beyond the contest proof into the larger ION product boundary: dynamic technology fabric, portable continuation, voice-to-local work, security lanes, voice safety, project-bound identity, and collaboration.

## Product Boundary: ION And dAimon

ION remains the deep continuity organism: the operating law, domain graph, carrier discipline, packet discipline, receipt discipline, settlement discipline, and long-horizon work substrate.

dAimon is the productized trust surface built from that law. It should be explainable to judges, customers, collaborators, and enterprise buyers without requiring them to understand the full ION organism on first contact.

The boundary is:

```text
ION is the law and deep engine.
dAimon is the product surface and trust layer built from that law.
```

The build posture is not to copy all of ION into dAimon immediately. The correct path is:

1. Productize the parts of ION that create visible trust.
2. Prove the smallest coherent vertical slice.
3. Reintroduce deeper ION modules as product capabilities.

Near-term modules:

- Domain graph.
- Capability routing.
- Generative governance.
- Agent spawning.
- Parallel branch settlement.
- Context package export.
- Enterprise audit ledger.
- Self-demonstrating demo agent.

## Lead Development Posture

The development posture is disciplined ambition:

```text
full product architecture
+ narrow proof slice
+ honest evidence boundaries
```

Two failures must be avoided:

- Overbuilding the entire organism before the demo works.
- Shrinking the product story until it looks like a small memory app.

The project should run on three synchronized tracks:

- Track A: ship the judge-visible vertical slice.
- Track B: preserve the full Layer 3 product architecture.
- Track C: keep ION continuity and proof discipline underneath everything.

Immediate expansion priorities:

1. Public repo hardening.
2. README and Devpost narrative lock.
3. Dashboard evidence capture.
4. Self-demonstrating video agent package.
5. Gemini or Agent Builder handoff surface.
6. Live or bounded MongoDB MCP trace path.
7. Receipt ledger and inheritance bundle polish.

## Dynamic Technology Fabric

dAimon should not be MongoDB-only. MongoDB is a contest and product wedge because it can carry document-shaped state, trace artifacts, metadata, and search-adjacent workloads. The larger claim is:

```text
dAimon can govern inheritance across any connected context substrate.
```

The adapter pattern is:

```text
external system
-> adapter manifest
-> capability declaration
-> object normalization
-> authority classification
-> proof requirements
-> settlement policy
-> receipt
-> inheritable context object
```

Every connector must answer:

- What objects can you read?
- What objects can you write?
- What authority is required?
- What proof can you return?
- What is stale, candidate, accepted, rejected, or secret-bearing?
- What should future agents be allowed to inherit?

Adapter classes:

- Document stores: MongoDB, Firestore, Couchbase, DynamoDB, Cosmos DB.
- Relational stores: PostgreSQL, MySQL, Cloud SQL, AlloyDB, Spanner.
- Warehouse stores: BigQuery, Snowflake, Databricks.
- Vector stores: MongoDB Atlas Vector Search, Vertex AI Vector Search, Pinecone, Weaviate, Qdrant, Milvus, pgvector, OpenSearch.
- Graph stores: Neo4j, Neptune, ArangoDB, Memgraph.
- Search stores: Elasticsearch, OpenSearch, Solr.
- Object and file stores: Google Cloud Storage, S3, Drive, local filesystem.
- Source control: GitHub, GitLab, Bitbucket.
- Work systems: Jira, Linear, ServiceNow, Confluence, Notion, Slack, Teams.
- Agent surfaces: Gemini Agent Builder, ADK, MCP servers, Codex CLI, browser extensions.

The product claim is stronger than broad integration:

```text
We can connect to many tools and still know what future AI work is allowed to trust.
```

## Overlap And Path Settlement

Many systems will overlap. A document may live in GitHub, be indexed in MongoDB, embedded in a vector store, summarized in BigQuery, and linked in a graph database.

dAimon should not flatten those objects into one vague memory. It should settle their paths and relationships.

Required relationship edges:

```text
same_as
copied_from
indexed_from
embedded_from
summarized_from
supersedes
conflicts_with
source_of_truth
```

The core question is:

```text
How does work move lawfully from one surface to another?
```

Every transition should be typed:

```text
witness -> candidate -> settled -> receipted -> inherited
```

## ION As A Governed Virtual Computer

Distributed AI work surfaces resemble parts of a larger virtual computer:

- Filesystems store artifacts.
- Databases store structured state.
- Warehouses store analytic state.
- Vector stores provide associative recall.
- Graph stores preserve relationships.
- Search engines provide indexed retrieval.
- GitHub preserves versioned change history.
- SaaS tools preserve organizational work state.
- Agent frameworks provide execution surfaces.
- Models provide inference.
- MCP provides tool and data connection protocol.

ION does not erase the differences between these surfaces. It governs transitions between them. A normal virtual machine abstracts hardware into one coherent machine. ION abstracts distributed AI and tool surfaces into one coherent state-transition environment while preserving provenance.

The goal is not:

```text
make all tools look the same
```

The goal is:

```text
make all tool transitions governable
```

## Portable Continuation

dAimon should prove that work survives the carrier.

The operator should be able to:

- Start on a desktop.
- Continue from a phone.
- Open a new ChatGPT conversation.
- Spawn a new local Codex or ION agent.
- Re-enter the project folder.
- Load the current context package.
- Continue without rebuilding the project from memory.

This is portable continuation, not ordinary chat history.

User-facing promise:

```text
Your AI work can move across conversations, devices, models, and local machines without losing the proof trail.
```

The distinction:

```text
Generic continuity: the assistant remembers or resumes.
Governed continuity: the system knows what may be inherited and why.
```

Portable continuation should be built from packets, receipts, context packages, routes, queues, validation artifacts, and accepted-state boundaries.

## The Re-Explanation Tax

Normal AI workflows make the user rebuild the project world repeatedly:

```text
new chat
-> upload files
-> explain project
-> correct misunderstandings
-> model produces work
-> context drifts
-> repeat
```

ION changes the loop:

```text
project state
-> context package
-> packet
-> domain route
-> proof
-> receipt
-> next lawful move
```

The product argument is not that every packet is cheaper than a casual prompt. The argument is that structured packets reduce the total cost of finishing real work.

```text
ION increases the cost of a single AI action so it can reduce the cost of finishing real AI work.
```

## Voice-To-Local Work

Voice-to-local work is a major proof surface:

```text
voice intent
-> ChatGPT interpretation
-> ION packet
-> local PC connector
-> Codex CLI / local agent
-> proof return
-> settlement
-> next packet
```

The phone becomes a command surface for serious local AI work, but the key is governed continuation, not remote control.

Voice input is an intent source. It is not authority by itself.

## Voice Misrecognition Safety Gate

Speech-to-text can turn a harmless phrase into a dangerous-looking instruction. High-risk voice-derived instructions require explicit confirmation before execution.

High-risk phrase classes:

- attack
- exploit
- bypass
- delete
- exfiltrate
- credentials
- secrets
- wipe
- push
- deploy
- production
- red team
- break into

Required behavior:

```text
pause
classify as possible transcription ambiguity
ask for confirmation or restatement
create a blocker/clarification receipt
perform no high-risk action until confirmed
```

This is a product feature, not friction. It protects governed human-AI work.

## Security, Red-Team, And High-Risk Testing

dAimon's product claim is trust, so it must eventually be tested against trust-breaking scenarios:

- Prompt injection.
- Malicious tool output.
- Stale context inheritance.
- Secret leakage.
- Unsafe file access.
- Confused authority.
- False receipts.
- Agent impersonation.
- Unbounded local execution.
- Cloud permission drift.
- Database mutation accidents.
- Cross-agent instruction poisoning.

High-risk tests belong in high-containment lanes:

```text
lab environment
-> synthetic secrets
-> synthetic repos/databases
-> bounded attack scenarios
-> detector/guardrail evaluation
-> receipt-bearing incident reports
-> patches
-> re-test
```

Mature security stack:

1. Threat model registry.
2. Prompt-injection test harness.
3. Secret-leak detector.
4. Tool-output trust classifier.
5. Capability and authority policy tests.
6. Cloud/database permission probes in sandbox accounts.
7. Local filesystem boundary tests.
8. Receipt integrity tests.
9. Agent impersonation and carrier spoofing tests.
10. Emergency stop and containment receipts.

## AI Is Not The Work Layer

AI should not be the unmanaged workspace, memory, planner, authority, and executor all at once.

Fragile pattern:

```text
user
-> AI conversation
-> direct work output
-> implicit trust
```

Better pattern:

```text
user
-> AI generation
-> governed work layer
-> visible classification
-> settlement
-> receipt
-> auditable continuation
```

The user should be able to see:

- What the AI proposed.
- What was accepted.
- What was rejected.
- What is still candidate.
- What proof exists.
- What future agents may inherit.
- What remains blocked.

## First Contact Package

A public custom GPT may be shared by many users. Each user's work must become separate immediately.

The early identity primitive should be project-bound, not necessarily human-bound.

A first contact package contains:

```text
project_id
project_secret_or_pairing_code
created_at
created_by_carrier_class
first_contact_receipt
public_project_hash
private_project_key_reference
initial_context_package
allowed_action_scope
```

Recommended flow:

1. User opens the custom GPT.
2. GPT calls `create_first_contact_package`.
3. ION hub returns project ID and pairing instructions.
4. User saves or mounts the project continuity package locally.
5. Future actions include project ID, packet nonce, and receipt reference.
6. Hub routes actions only to that project's queue/state.
7. Higher-risk actions require local hub confirmation or stronger auth.

Authority tiers:

- `project_id only`: read public/basic project metadata.
- `project_id + pairing secret`: queue bounded packets.
- `project_id + local hub proof`: interact with local machine/project files.
- `project_id + human approval`: perform higher-risk mutations.
- `oauth/admin identity`: enterprise or team account management.

## Project Tags And Collaboration

The project, not the chat, should be the shared object.

User-facing idea:

```text
Share the project tag.
Join the same continuity lane.
Work from the same receipts, packets, context, and accepted state.
```

Distinction:

```text
project_id = stable public-ish project lane identifier
invite_token = private scoped capability to participate
```

Collaboration roles:

- `viewer`: read project status, receipts, and context summaries.
- `contributor`: submit candidate packets and artifacts.
- `builder`: queue bounded local/cloud work packets.
- `reviewer`: comment on settlement decisions.
- `authorizer`: approve higher-risk state transitions.
- `owner`: rotate tokens, revoke access, bind stronger identity.

Safety rule:

```text
project_id routes the request
capability token scopes the request
receipt records the request
settlement decides what becomes state
```

## New Build Modules

The custom GPT expansion adds these orchestration domains:

- `ion_product_boundary`
- `technology_fabric`
- `portable_continuation`
- `voice_local_work`
- `security_red_team`
- `project_identity_collaboration`

It adds these roadmap tracks:

- P7: Portable continuation and custom GPT connector.
- P8: Dynamic technology fabric adapters.
- P9: Security and red-team containment lane.

It adds these proof gates:

- Adapter manifest validation.
- Portable continuation replay.
- Voice safety confirmation.
- Project identity pairing.
- Collaboration capability scope.
- Red-team lab containment.

## Current Non-Claims

These expansion modules are product architecture until proof artifacts exist. Do not claim:

- Full custom GPT to local PC connector.
- Production identity or collaboration system.
- Complete red-team certification.
- Complete cross-database technology fabric.
- Safe execution of high-risk tests outside a containment lab.
- Voice command execution without confirmation gates.

Claim instead:

```text
dAimon has repo-owned architecture and validation contracts for portable continuation, project-bound identity, technology fabric adapters, voice-to-local governance, and security containment.
```
