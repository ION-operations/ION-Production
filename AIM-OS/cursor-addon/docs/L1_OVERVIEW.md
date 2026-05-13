# Cursor Extension Dashboard - L1 Overview

**System:** Cursor Extension Dashboard (AIM-OS Integration)  
**Level:** L1 - Overview (500 words)  
**Status:** Documentation in Progress  
**Date:** 2025-11-01

---

## System Purpose

The Cursor Extension Dashboard provides AIM-OS UI integration within Cursor IDE, displaying the MainDashboard React component (6 tabs: Agents, Chat, Chains, Tools, Timeline, NL Tags) in a VS Code webview panel. The extension bridges Cursor IDE and AIM-OS backend systems, enabling visualization and interaction with consciousness infrastructure.

## Architecture Overview

**Components:**
- **Extension Host** (`extension.ts`): Registers providers, commands, activation events
- **Webview Provider** (`lucidDashboardProvider.ts`): Creates and manages webview panels
- **React UI** (`packages/ide_chat_app/`): MainDashboard component with 6 tabs
- **Build System** (`scripts/build-extension.js`): Builds React UI and packages extension
- **MCP Integration** (`src/mcp/mcpClient.ts`): Connects to AIM-OS MCP server

**Data Flow:**
1. User opens dashboard panel → Extension activates
2. Provider creates webview → Loads React HTML
3. HTML rewrites URIs → Converts file paths to `vscode-webview://` URIs
4. Scripts load → React mounts → UI displays

## Current Issues

**Critical Problems:**
1. **Packaging:** `.vscodeignore` excluded `dist/` folder (fixed ✅)
2. **Activation:** Missing `onView` activation events (partially fixed)
3. **Options Order:** Webview options set after HTML (fixed ✅)
4. **URI Rewriting:** Complex regex matching for asset paths (unknown status)
5. **Security Layers:** TrustedTypes, CSP, webview isolation (fixed ✅)
6. **React Mounting:** May fail silently if scripts don't load (unknown)
7. **Extension Context:** `acquireVsCodeApi()` timing issues (unknown)

**Why So Hard:**
VS Code webviews have 10+ security layers browsers don't have. Each layer can fail silently, causing blank screen. No clear error messages. Requires perfect configuration across packaging, activation, options, URIs, security policies, and React initialization.

## Documentation Status

**Current State:** 100+ fragmented documentation files in `cursor-addon/`  
**New Approach:** Systematic L0-L4 documentation per standards  
**This Document:** L1 Overview - High-level understanding  
**Related:** L0 Executive (summary), L2 Architecture (detailed structure), L3 Implementation (code guide), L4 Complete (reference)

## Next Steps

Complete L2-L4 documentation, create issue log, enable systematic debugging.

