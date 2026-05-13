---
atlas_package: system
system_slug: anthropic-claude-code-agent-sdk
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Components

| Component | Role | Evidence |
|-----------|------|----------|
| Messages API (conceptual) | Core LLM call surface | DOCUMENTED |
| Tool use blocks | Model-requested tool invocations | DOCUMENTED |
| Claude Code CLI | Local agent workflow | DOCUMENTED (URL pinned in sources) |
| MCP client/host interaction | Tool/context providers | DOCUMENTED (MCP spec + vendor docs) |
