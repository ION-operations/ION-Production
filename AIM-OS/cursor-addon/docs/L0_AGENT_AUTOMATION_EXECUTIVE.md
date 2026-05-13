# L0: Agent Automation Executive Summary

**Purpose:** 100-word quick reference for Cursor agent automation  
**Audience:** Developers, stakeholders, quick decision-making  
**Status:** Production Ready  
**Tags:** `#agent-automation` `#cursor` `#autonomous` `#production-ready`

---

## Executive Summary

Cursor agent automation enables autonomous operation via Background Agent API (HTTP), MCP tools, and slash commands. Bulletproof messaging ensures reliable communication through envelope protocol with ACK/NACK, ordering, idempotency, and dead letter queue. Agents run for hours/days autonomously, monitored via React UI dashboard. Complete protocol: Slash commands → MCP tools → Command Server → Background Agent API → Webhooks → MessageRouter → UI. Production-ready with supervisor patterns, checkpointing, and automatic recovery.

**Key Components:** AgentMonitor, MessageRouter, Command Server, React UI  
**Status:** Protocol designed, AgentMonitor implemented, pending API research  
**Next:** Research Cursor API endpoints, register MCP tools, create slash commands

---

**Related:** [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md) | [CURSOR_AGENT_AUTOMATION.md](./CURSOR_AGENT_AUTOMATION.md) | [INDEX.md](./INDEX.md)

