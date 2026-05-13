---
id: "local_vs_cloud_agents_explanation"
system: "agent_automation"
component: "agentMonitor"
level: "T1"
type: "explanation"
title: "Local vs Cloud Agents - When to Use Each"
description: "Explains the difference between Cloud Agents API and CLI agents for local repos"
audience: "developers"
confidence_threshold: 0.85
token_cost: 500
word_count: 500
created: "2025-11-03T22:40:00Z"
updated: "2025-11-03T22:40:00Z"
author: "aether"
status: "complete"
tags: ["agents", "local", "cloud", "cli", "explanation", "t-level"]
dependencies: []
related_docs: ["CURSOR_API_RESEARCH.md", "API_KEY_TESTING_GUIDE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Local vs Cloud Agents - When to Use Each (≈500 words)

## 🎯 **THE PROBLEM**

You want to automate Cursor agents, but you have **two different scenarios:**

1. **Repo is on GitHub** → Can use Cloud Agents API ✅
2. **Repo is local-only** → Cloud API won't work ❌

## 🌐 **CLOUD AGENTS API** (What We Built)

**How It Works:**
- Makes HTTP request to `https://api.cursor.com/v0/agents`
- Cursor's servers clone your GitHub repo
- Agent runs on Cursor's infrastructure
- Sends webhooks back to your extension

**Requirements:**
- ✅ **MUST have GitHub repository URL**
- ✅ **MUST be publicly accessible** (or Cursor has access)
- ✅ **Requires API key**
- ✅ **Supports webhooks** for real-time updates

**Example:**
```typescript
// ✅ WORKS - GitHub URL
startAgent({
  repoPath: "https://github.com/myuser/my-repo"
})

// ❌ FAILS - Local path
startAgent({
  repoPath: "C:\\Users\\braden\\projects\\my-app"  // Error!
})
```

**Why It Fails:**
The API endpoint requires this format:
```json
{
  "source": {
    "repository": "https://github.com/user/repo"  // ← Must be GitHub URL
  }
}
```

You can't pass a local file path here because Cursor's servers can't access your local filesystem.

---

## 💻 **CLI AGENT** (Alternative for Local Repos)

**How It Works:**
- Spawns `cursor-agent` command-line tool
- Runs on YOUR machine (not Cursor's servers)
- Works directly with local files
- No GitHub required!

**Requirements:**
- ✅ **Works with local repos** (file paths)
- ✅ **No API key needed** (uses your Cursor installation)
- ✅ **No webhooks** (but you can monitor stdout)
- ✅ **Requires `cursor-agent` CLI** (v0.47.5+)

**Example:**
```typescript
// ✅ WORKS - Local path
startLocalAgent({
  prompt: "Add README.md file",
  repoPath: "C:\\Users\\braden\\projects\\my-app"  // Local path OK!
})
```

**Implementation:**
```typescript
const { execSync } = require('child_process');

const output = execSync(
  `cursor-agent --print --output-format json "Add README.md"`,
  { cwd: "C:\\Users\\braden\\projects\\my-app" }
);
```

---

## 🔄 **WHICH ONE TO USE?**

### **Use Cloud Agents API When:**
- ✅ You have a GitHub repository
- ✅ You want cloud execution (doesn't use your machine)
- ✅ You need webhooks for real-time updates
- ✅ You want to run multiple agents simultaneously
- ✅ You want long-running agents (hours/days)

### **Use CLI Agent When:**
- ✅ You have a local-only repository
- ✅ You want to run on your machine
- ✅ You don't need webhooks (can monitor stdout)
- ✅ Your repo isn't on GitHub (or isn't public)
- ✅ You want simpler setup (no API key needed)

---

## 🛠️ **OUR SOLUTION**

**AgentMonitor supports BOTH:**

1. **`startAgent()`** - Cloud Agents API (requires GitHub URL)
2. **`startLocalAgent()`** - CLI Agent (works with local paths)

**Smart Detection:**
```typescript
if (repoPath.startsWith('https://github.com/')) {
  // Use Cloud API
  return await this.startAgent(params);
} else {
  // Use CLI Agent
  return await this.startLocalAgent(params);
}
```

---

## ✅ **BOTTOM LINE**

**The "issue" isn't really an issue** - it's just two different tools:

- **Cloud API** = Runs on Cursor's servers → Needs GitHub
- **CLI Agent** = Runs on your machine → Works with local repos

Both are available, and AgentMonitor supports both! 🎉

---

**Status:** Both methods supported  
**Choice:** Use Cloud API for GitHub repos, CLI for local repos

