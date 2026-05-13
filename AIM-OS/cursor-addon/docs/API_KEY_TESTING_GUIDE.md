---
id: "api_key_testing_guide"
system: "agent_automation"
component: "agentMonitor"
level: "T1"
type: "test_guide"
title: "API Key Testing Guide"
description: "How to test Cursor API key and AgentMonitor integration"
audience: "developers"
confidence_threshold: 0.80
token_cost: 500
word_count: 500
created: "2025-11-03T22:35:00Z"
updated: "2025-11-03T22:35:00Z"
author: "aether"
status: "complete"
tags: ["api", "testing", "cursor", "authentication", "t-level"]
dependencies: []
related_docs: ["CURSOR_API_RESEARCH.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# API Key Testing Guide (≈500 words)

## 🎯 **API KEY RECEIVED**

**Status:** ✅ **OBTAINED**
- Key: `key_a8076b1d34580605160a239acd6540ee2f69bb04da86ed8a00b085efd32a7558`
- **SECURITY:** Never commit to git, store securely

## 🧪 **TESTING STEPS**

### **Step 1: Test API Key Authentication**

```bash
# Test API key works
curl --request GET \
  --url https://api.cursor.com/v0/me \
  --header 'Authorization: Bearer key_a8076b1d34580605160a239acd6540ee2f69bb04da86ed8a00b085efd32a7558'
```

**Expected Response:**
```json
{
  "apiKeyName": "Automation Integration",
  "createdAt": "2025-11-03T22:30:00Z",
  "userEmail": "your-email@example.com"
}
```

### **Step 2: Test List Agents**

```bash
curl --request GET \
  --url 'https://api.cursor.com/v0/agents?limit=10' \
  --header 'Authorization: Bearer key_a8076b1d34580605160a239acd6540ee2f69bb04da86ed8a00b085efd32a7558'
```

### **Step 3: Test Launch Agent (Requires GitHub Repo)**

```bash
curl --request POST \
  --url https://api.cursor.com/v0/agents \
  --header 'Authorization: Bearer key_a8076b1d34580605160a239acd6540ee2f69bb04da86ed8a00b085efd32a7558' \
  --header 'Content-Type: application/json' \
  --data '{
    "prompt": {
      "text": "Add README.md file"
    },
    "source": {
      "repository": "https://github.com/your-org/your-repo",
      "ref": "main"
    },
    "target": {
      "branchName": "agent/test-run",
      "autoCreatePr": false
    }
  }'
```

## 🔧 **AGENTMONITOR UPDATES**

**Fixed:**
- ✅ API URL: Changed from `/v1` to `/v0`
- ✅ Endpoints: Fixed to match official API:
  - `POST /v0/agents` (was `/agents/runs`)
  - `GET /v0/agents/{id}` (was `/agents/runs/{id}`)
  - `DELETE /v0/agents/{id}` (was `/agents/runs/{id}/cancel`)
- ✅ Request format: Updated to match API spec (`prompt.text`, `source.repository`, etc.)
- ✅ Response parsing: Maps API response to internal format
- ✅ Status mapping: Maps API statuses (CREATING, RUNNING, FINISHED) to internal statuses

**Added:**
- ✅ `getGitHubUrl()` helper: Converts local repo path to GitHub URL
- ✅ `mapStatus()` helper: Maps API statuses to internal format

## ⚠️ **IMPORTANT LIMITATIONS**

**GitHub Repository Required:**
- API **requires** GitHub repository URLs
- Won't work with local-only repositories
- Use `cursor-agent` CLI for local repos instead

**How to Handle:**
- Provide full GitHub URL: `https://github.com/user/repo`
- Or repo path must have git remote configured
- Helper method tries to get git remote URL automatically

## 📝 **NEXT STEPS**

1. **Test API Key:** Run curl commands above
2. **Configure Extension:** Add API key to extension settings
3. **Test Agent Launch:** Try launching agent with real GitHub repo
4. **Set Up Webhook:** Configure webhook URL for agent events

---

**Status:** Ready for testing  
**API Key:** Obtained and configured  
**AgentMonitor:** Updated with correct endpoints

