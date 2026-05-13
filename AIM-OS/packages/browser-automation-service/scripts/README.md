# Sample Automation Scripts

**Location:** `packages/browser-automation-service/scripts/`

This directory contains sample automation scripts for common use cases.

---

## 📋 **AVAILABLE SCRIPTS**

### **1. ChatGPT Deep Search** (`chatgpt-deep-search.json`)
**Purpose:** Automate ChatGPT for deep search queries

**Variables:**
- `query` - The search query to send
- `accountId` - Optional account ID for session loading

**Usage:**
```bash
curl -X POST http://localhost:5002/api/automation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "browserId": "browser_123",
    "script": {...},
    "variables": {
      "query": "Explain quantum computing",
      "accountId": "account_456"
    }
  }'
```

---

### **2. ChatGPT Login** (`chatgpt-login.json`)
**Purpose:** Automate ChatGPT login flow

**Variables:**
- `email` - ChatGPT email address
- `password` - ChatGPT password

**Usage:**
```bash
curl -X POST http://localhost:5002/api/automation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "browserId": "browser_123",
    "script": {...},
    "variables": {
      "email": "user@example.com",
      "password": "password123"
    }
  }'
```

**Note:** After login, use `saveSession()` to persist cookies for future use.

---

### **3. Claude Chat Query** (`claude-chat-query.json`)
**Purpose:** Automate Claude chat queries

**Variables:**
- `query` - The chat query to send
- `accountId` - Optional account ID for session loading

**Usage:**
```bash
curl -X POST http://localhost:5002/api/automation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "browserId": "browser_123",
    "script": {...},
    "variables": {
      "query": "Analyze this code",
      "accountId": "account_456"
    }
  }'
```

---

### **4. ChatGPT File Upload** (`chatgpt-file-upload.json`)
**Purpose:** Automate ChatGPT with file upload

**Variables:**
- `query` - The query to send with file
- `filePath` - Path to file to upload
- `accountId` - Optional account ID for session loading

**Usage:**
```bash
curl -X POST http://localhost:5002/api/automation/execute \
  -H "Content-Type: application/json" \
  -d '{
    "browserId": "browser_123",
    "script": {...},
    "variables": {
      "query": "Analyze this file",
      "filePath": "/path/to/file.pdf",
      "accountId": "account_456"
    }
  }'
```

---

## 🔧 **SCRIPT FORMAT**

All scripts follow the JSON format defined in `BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md`:

```json
{
  "name": "Script Name",
  "description": "Script description",
  "provider": "chatgpt" | "claude" | "gemini" | "custom",
  "variables": {
    "var1": "{{var1}}",
    "var2": "{{var2}}"
  },
  "actions": [
    {
      "type": "navigate" | "click" | "type" | "wait" | "upload" | "screenshot" | "extract" | "scroll" | "hover",
      "selector": "...",
      "value": "...",
      "url": "...",
      "filePath": "...",
      "timeout": 10000,
      "humanLike": true,
      "beforeDelay": 500,
      "afterDelay": 1000,
      "condition": "JavaScript condition",
      "retry": false
    }
  ],
  "output": {
    "outputVar": "selector"
  }
}
```

---

## 📝 **CREATING CUSTOM SCRIPTS**

1. **Copy a template** from this directory
2. **Modify actions** based on your needs
3. **Add variables** for dynamic values
4. **Test the script** using the REST API
5. **Save the script** using `POST /api/scripts/save`

---

## ⚠️ **IMPORTANT NOTES**

- **Selectors may change:** Website selectors can change, scripts may need updates
- **Rate limiting:** Be mindful of rate limits on AI chat services
- **Session persistence:** Use ConnectionManager to save sessions after login
- **Error handling:** Scripts include retry logic, but may need adjustment
- **Human-like behavior:** Scripts use delays to mimic human behavior

---

**Last Updated:** 2025-01-27  
**Status:** ✅ Sample scripts ready for testing

---

*Sample Automation Scripts*  
*Part of Browser Automation Service* 💙✨

