# How to Use @aimos Chat Participant

**Quick Guide:** How to use `@aimos` in Cursor chat

---

## 🎯 **STEP-BY-STEP INSTRUCTIONS**

### **Step 1: Open Cursor Chat**

**Method 1: Keyboard Shortcut**
- Press `Ctrl+L` (Windows) or `Cmd+L` (Mac)
- This opens Cursor's chat panel

**Method 2: Command Palette**
- Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
- Type "Chat" and select "Chat: Open Chat"

**Method 3: UI Button**
- Look for the chat icon in the top-right corner of Cursor
- Click it to open chat

---

### **Step 2: Type @aimos**

Once the chat is open:

1. **Type `@aimos`** in the chat input box
2. **Wait for autocomplete** - You should see "AIMOS" appear as an option
3. **Select "AIMOS"** from the dropdown (or just press Enter/Tab)
4. **Type your message** after `@aimos`

---

### **Step 3: Example Usage**

**Example 1: Store Memory**
```
@aimos store this in memory
```
(Select some code first, then send this message)

**Example 2: Search Memory**
```
@aimos search memory for authentication patterns
```

**Example 3: Create Plan**
```
@aimos create a plan to implement OAuth2
```

**Example 4: Memory Stats**
```
@aimos show memory statistics
```

**Example 5: Direct MCP Tool**
```
@aimos mcp:mcp_lucid-mcp_get_memory_stats
```

---

## 🔍 **TROUBLESHOOTING**

### **Problem: Dropdown shows files instead of chat participant**

**This means:** Cursor is trying to autocomplete file names instead of recognizing the chat participant.

**Solutions:**

1. **Make sure you're in Cursor Chat** (not just typing in the editor)
   - Use `Ctrl+L` to open chat first
   - The chat input should say "Ask Cursor..." or similar

2. **Type `@aimos` in the chat input box specifically**
   - Not in the editor
   - Not in the command palette
   - In the CHAT input box

3. **Check if extension is loaded:**
   - Look for "✅ AIMOS chat participant registered!" message when Cursor starts
   - Or check Output panel → "AIM-OS Extension" channel

4. **Reload Extension:**
   - `Ctrl+Shift+P` → "Developer: Reload Window"
   - Wait for reload, then try `@aimos` again

---

### **Problem: @aimos doesn't appear in autocomplete**

**Possible causes:**

1. **Extension not activated**
   - Check: Output panel → "AIM-OS Extension" → Look for "AIMOS chat participant registered"
   - If not there, extension may not be loaded

2. **Chat API not available**
   - Cursor may not support Chat Participant API in your version
   - Check: Output panel → "AIM-OS Extension" → Look for "Chat API not available" warning

3. **Extension needs rebuild**
   ```bash
   cd cursor-addon
   npm run compile
   ```
   Then reload Cursor

---

## 📋 **WHAT @aimos CAN DO**

### **Auto-Detected Commands** (just type naturally):

- **"store memory"** → Stores selected text in AIMOS memory
- **"search memory"** → Searches AIMOS memory
- **"create plan"** → Creates execution plan via APOE
- **"track confidence"** → Tracks confidence for a task
- **"memory stats"** → Shows memory statistics

### **Direct MCP Tool Calls:**

```
@aimos mcp:mcp_lucid-mcp_store_memory {"content": "Important info"}
```

---

## 🎬 **VISUAL GUIDE**

```
1. Press Ctrl+L to open chat
   ↓
2. Chat panel opens at bottom/side
   ↓
3. Type: @aimos
   ↓
4. See "AIMOS" in dropdown
   ↓
5. Select it or press Enter
   ↓
6. Type your message: "store this in memory"
   ↓
7. Press Enter to send
   ↓
8. AIMOS processes via Command Server
   ↓
9. Response appears in chat
```

---

## ✅ **QUICK TEST**

**Try this right now:**

1. Press `Ctrl+L` (opens chat)
2. Type: `@aimos show memory statistics`
3. Press Enter
4. You should see memory stats appear!

---

## 🆘 **STILL NOT WORKING?**

**Check these:**

1. **Extension is installed** - Check Extensions panel
2. **Extension is enabled** - Should show "Enabled"
3. **Command Server is running** - Check Output → "AIM-OS Extension" logs
4. **No errors** - Check Output → "AIM-OS Extension" for errors

**If still not working:**
- Check `cursor-addon/docs/LATEST_LOGS.md` for error messages
- Reload Cursor (`Ctrl+Shift+P` → "Developer: Reload Window")
- Try rebuilding extension (`npm run compile` in cursor-addon folder)

---

**Remember:** `@aimos` only works in Cursor's **CHAT** interface, not in the editor or command palette!

