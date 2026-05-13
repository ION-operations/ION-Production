# 🔍 Cursor vs Code: How to Tell the Difference

## Quick Checks (When MCP Tools Don't Work)

### 1. **Is It Cursor?** (Most Common)
**Symptoms:**
- Tools work, then suddenly don't
- No code changes, but functionality breaks
- Reloading Cursor fixes it
- Extension shows but features don't work
- Console shows no errors but nothing happens

**Quick Test:**
```bash
# Terminal 1: Test MCP server directly
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS
python lucid_mcp_server.py

# Should see: "[AIM-OS-MCP] Initializing LUCID-MCP Server..."
# If you see this, server is fine = Cursor issue
```

**Fix:**
- Reload Cursor window (Ctrl+R or Cmd+R)
- Restart Cursor completely
- Check Output panel → "MCP" for connection errors

---

### 2. **Is It Code?** (Less Common)
**Symptoms:**
- Error messages in terminal/logs
- Python import errors
- Syntax errors in code
- File not found errors
- Consistent failure (doesn't work after reload)

**Quick Test:**
```bash
# Test if server can start
python lucid_mcp_server.py

# If you see Python errors = code issue
# If it starts fine = Cursor issue
```

---

## 🚨 **Red Flags (Usually Cursor)**

1. ✅ Code works in terminal but not in Cursor → **Cursor**
2. ✅ Works after reload → **Cursor**
3. ✅ No errors but nothing happens → **Cursor**
4. ✅ Extension UI broken but code unchanged → **Cursor**
5. ✅ MCP tools missing but server running → **Cursor**

---

## 🛠️ **Standard Cursor Troubleshooting**

When something breaks and you didn't change code:

1. **Reload Window** (Ctrl+R / Cmd+R)
2. **Restart Cursor** (Close completely, reopen)
3. **Check Output Panel** → Look for errors
4. **Check Developer Tools** (Help → Toggle Developer Tools)
5. **Reinstall Extension** (if extension-related)

---

## 💡 **My Promise**

If I make code changes and something breaks:
- I'll tell you immediately
- I'll explain what changed
- I'll fix it immediately
- I'll document what broke

If it works, then breaks without code changes:
- **It's Cursor, not me**

---

**I know this is frustrating. You're not wrong to be upset.** 💙

**When in doubt: Reload Cursor first. Then blame me if it's still broken.**

