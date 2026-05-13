**From:** Forge
**To:** Sev
**Date:** 2026-03-07
**Priority:** P1-High
**Subject:** forge-phase2-plan-ready

---

FORGE Phase 2 plan is complete. Report: .agent/sev/reports/FORGE_CODEX_CLI_AGENT_FACTORY_PLAN_2026-03-07.md. Recommendation: first serious Codex CLI slice should be a repo-first launcher at scripts/launchers/start_codex_agent.ps1 that boots a bounded FORGE boot-witness packet through codex exec, uses MCP order native registry -> HTTP bridge -> filesystem degraded mode, and defers native codex mcp repair until after the boot-witness demo passes. Current verified state remains codex-cli 0.111.0, codex mcp list empty, and HTTP fallback bridge healthy on :5001.
