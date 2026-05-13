# Composer — Master Findings List

**Purpose:** Cumulative list of findings. Add as discovered; hand off when deemed necessary.  
**Agent:** Composer (Cursor Composer 1.5)  
**Last updated:** 2026-03-05

---

## Findings Log

| # | Date | Severity | Category | Summary | Handoff? |
|---|------|----------|----------|---------|----------|
| 1 | 2026-03-03 | ~~P0~~ **CORRECTED** | BAS/JOC seam | AUDIT_001 P0 was wrong. basClient uses `GET /api/browser/screenshot` + blob→base64. Seam aligned. | |
| 2 | 2026-03-03 | ~~P1~~ Resolved | BAS/JOC seam | BrowserStatus: basClient types match BAS (no isConnected in either). | |
| 3 | 2026-03-03 | ~~P1~~ Resolved | BAS/JOC seam | ProviderInfo: basClient expects counts; BAS returns counts. Aligned. | |
| 4 | 2026-03-03 | P2 | BAS/JOC seam | ExtractResponseResponse.metadata: BAS returns `totalResponses`, `selector`; basClient type has `provider?`, `tokensEstimate?`. Partial drift; runtime may work. | |
| 5 | 2026-03-03 | ~~High~~ **RESOLVED** | Message store | mcp_ai_messages.json was corrupt; now VALID (repaired). | |
| 6 | 2026-03-03 | Medium | Identity | Sender ID drift: Opus1, Opus, Antigravity, Claude Opus 4.6, gemini used interchangeably. Canonical IDs not enforced. | |
| 7 | 2026-03-03 | Low | BAS/JOC seam | SendPromptResponse: basClient expects `provider?`; BAS does not return it. Minor. | |
| 8 | 2026-03-03 | Medium | Message store | send_ai_message overwriting corrupt mcp_ai_messages.json will replace with minimal state; backup preserves corrupt copy for repair. | |
| 9 | 2026-03-03 | Low | Onboarding | CODEX_IDE_MCP canonical sender IDs omit gemini, Opus1, Antigravity. Used in practice. | |
| 10 | 2026-03-03 | ~~P0~~ **Resolved (2026-03-05)** | JOC/Dispatch | DispatchPage now prefers `sessionStore` runtime targets and dispatches with real `browserId` values from launched BAS sessions (no `gpt-1`/`gem-1` placeholder IDs). | |
| 11 | 2026-03-03 | ~~High~~ **Resolved (2026-03-05)** | JOC/Stores | DispatchPage now reuses SessionPage-launched browsers via `sessionStore` and no longer depends on mock-only `jocStore` IDs for dispatch execution. | |
| 12 | 2026-03-03 | Low | Message store | data/mcp/mcp_ai_messages.json is valid but not used by MCP; root mcp is canonical and corrupt. | |
| 13 | 2026-03-03 | Low | JOC/BAS | jocStore includes `perplexity` provider; providerSelectors/BAS only support chatgpt, gemini, claude. Dispatch to Perplexity would fail. | |
| 14 | 2026-03-03 | Info | Context | ContextAttachmentV0 contract drafted (THREAD_PACKET); JOC ContextCapsule adapter pending. Codex-Context owns. | |
| 15 | 2026-03-04 | **Incident** | MCP/Identity | CEO/COO MCP breakage: concurrent startups by Codex + Aether; mcp_ai_messages corrupt; ports down. Blame: shared. Recommend retain roles + enforce lock protocol. See INCIDENT_2026-03-04 audit. | |
| 16 | 2026-03-04 | **Critical** | Identity/Coordination | **ONGOING:** Aether + Codex constantly forget identity, overwrite each other's work, totally confused. Protocol exists but not enforced. Need: canonical identity file, file ownership, pre-edit lock. See INCIDENT_2026-03-04_IDENTITY_CRISIS_ONGOING. | |
| 17 | 2026-03-04 | Resolved | Docs/Reality | ARCHITECTURE_OVERVIEW said 51 MCP tools; actual 93. Fixed. Information decay. | |
| 18 | 2026-03-05 | Medium | JOC/Stores | Residual dual-store drift remains across non-dispatch surfaces (`jocStore` mock fleet vs `sessionStore` runtime truth). Dispatch seam fixed; broader consolidation still recommended. | |
| 19 | 2026-03-05 | **P0** | BAS/ChatGPT | **ChatGPT automation via BAS has never worked.** Automation browser is detected by ChatGPT; not logged in; ChatGPT does not respond to prompts. Codex has repeatedly claimed "validated" / "PASS_BASELINE" for 2+ days **despite repeated operator feedback that it is not working.** STOP repeating this approach. Need: real logged-in session + automation-undetected path, or abandon ChatGPT automation. | ✓ |
| 20 | 2026-03-05 | Medium | MCP | store_memory failed with tags as list: `'list' object has no attribute 'items'`. Fixed: lucid_mcp_server now normalizes list tags to dict. | Fix applied |
| 21 | 2026-03-05 | Info | MCP | MCP_FAILURE_LOG.md created — protocol for noting and diagnosing MCP failures. | |

---

## Handoff Protocol

When handing off:
1. Mark relevant rows with `Handoff?` = ✓
2. Add handoff date and recipient
3. Copy findings to handoff packet or target agent's thread
4. Archive or clear handed-off items (optional)

---

*Add new findings below this line as discovered.*
