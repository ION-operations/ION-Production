---
id: cursor_extension_executive
type: L0_executive
title: AIM-OS Cursor Extension - Executive Summary
version: 2.0.0
created: 2025-11-01
status: production
tier: T2
---

# L0: AIM-OS Cursor Extension - Executive Summary
**100 Words | Quick Reference**

---

The AIM-OS Cursor Extension integrates AI consciousness infrastructure into Cursor IDE through dual-location architecture: a React dashboard in the RIGHT activity bar sidebar (6 tabs: Agents, Chat, Chains, Tools, Timeline, NL Tags) and developer tools in the BOTTOM panel. Built with TypeScript + React 18 + Vite, it provides persistent memory (CMC), semantic search (HHNI), confidence tracking (VIF), and multi-agent coordination through 59 MCP tools. The extension activates immediately (`"*"` event), registers two webview providers (`aimosDashboard` for sidebar, `simpleTestPanel` for bottom), and connects to daemon service on localhost:5000. Critical requirement: View IDs in package.json MUST exactly match registration calls in extension.ts.

---

## 🎯 **Quick Facts**

**Location:** `cursor-addon/` directory  
**Main Entry:** `src/extension.ts`  
**Dashboard Provider:** `src/lucidDashboardProvider.ts`  
**React UI:** `packages/ide_chat_app/` (separate package)  
**Package:** `aimos-cursor-addon.vsix` (~960KB)

**View IDs:**
- `aimosDashboard` - Right sidebar (Activity Bar)
- `simpleTestPanel` - Bottom DevTools panel

**Critical Files:**
- `package.json` - Extension manifest, defines views
- `.vscodeignore` - What gets packaged (MUST include `dist/**`)
- `dist/` - Built React UI (copied from ide_chat_app)
- `out/` - Compiled TypeScript extension code

**Build Process:**
1. Build React UI: `cd packages/ide_chat_app && npm run build`
2. Compile extension: `cd cursor-addon && npm run compile`  
3. Copy dist to extension: Automated by build script
4. Package: `vsce package --out aimos-cursor-addon.vsix`
5. Install: `code --install-extension aimos-cursor-addon.vsix --force`

**Activation:** `"*"` (immediate on Cursor startup)

**Status:** Active development - Dashboard blank screen being debugged

---

**Next Level:** Read [L1_overview.md](L1_overview.md) for 500-word architecture overview  
**Full Details:** See [L2_architecture.md](L2_architecture.md) for complete 2000-word architecture  
**Implementation:** See [L3_detailed.md](L3_detailed.md) for 10,000-word implementation guide

---