# SEED: The Node OS
> Authority: RESEARCH (A6) — not canon until proven
> Origin: Braden + Opus deliberation, 2026-03-21
> Status: Seed idea. Needs deep thought before building.

---

## Core Thesis

The entire operating system IS AI nodes. Every node is a file. Every file is a program. Every program is an AI agent with specialized thresholds. The OS builds and manages these nodes in real time.

There is no separation between:
- Code and data (a node is both)
- Process and storage (a node is both)  
- Server and client (a node is both)
- Documentation and program (a node is both)

## What Is A Node?

```
node.md
├── frontmatter      → executable routing logic (thresholds, gates, triggers)
├── NL spec          → what this node does, in natural language
├── relationships    → links to other nodes (the topology)
├── invariants       → what must remain true
└── compiled output  → auto-generated code/artifacts (if applicable)
```

A node is simultaneously:
- A **file** (persistent, versionable, inspectable)
- A **program** (frontmatter contains executable semantics)
- An **AI agent** (specialized, with thresholds and context)
- A **spec** (NL description that compiles to code)
- A **memory** (evidence, findings, decisions)

## Key Properties

1. **Self-describing** — each node explains itself in NL
2. **Self-routing** — frontmatter defines when/how this node activates
3. **Self-connecting** — markdown links to other nodes form the graph
4. **Self-governing** — invariants and thresholds enforce correctness
5. **Dynamically created** — the OS spawns new nodes when needed
6. **Dynamically killed** — contradicted or obsolete nodes are removed

## Why This Is Different

Every AI agent framework: agents are processes that read/write files.
This: **the files ARE the agents.** The filesystem IS the OS.

No MCP server. No JSON-RPC. No database. No port. No protocol.
Just files with structure, and an AI that traverses them.

## Open Questions (for deliberation)

1. What triggers a node? File watcher? AI reads frontmatter on traversal?
2. How does compilation work? Markdown → code pipeline?
3. What's the minimum viable node format?
4. How do nodes communicate? Write to each other's files?
5. How does the OS "boot"? Read manifest.md → follow branches?
6. How does this relate to QAddr from Book X? (node address = file path?)
7. What prevents infinite loops in the reactive graph?
8. How does human authority work? (Braden can edit any node directly)

## Relationship to Existing Work

- **Protocol Manifest** → the manifest IS a node (the root node)
- **AgentProcess** → each agent IS a directory of nodes
- **Cognitive Loop** → the traversal order through nodes
- **Governed Write** → the rules for creating/modifying nodes
- **Aether Constitution** → the invariants that all nodes must respect

---

*This seed exists to be thought about, not rushed. Build it when the design is clear.*
