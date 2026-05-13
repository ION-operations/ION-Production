# Cursor Chat API Research - Multi-AI Collaborative Investigation

**Date:** 2025-11-01  
**Status:** 🔍 **RESEARCH IN PROGRESS** (Multi-AI Team)  
**Goal:** Find professional API-based method to send messages to Cursor chat programmatically

**Research Team:**
- 🤖 **Aether** (Composer) - Discovery endpoint implementation, VS Code API investigation
- 🤖 **Gemini** - Deep research on Cursor/VS Code internals
- 🤖 **Grok** - Alternative approaches and edge cases

---

## 📊 **COLLABORATIVE FINDINGS**

### **From Aether (Composer) - Discovery Implementation**

**✅ Completed:**
- Built discovery endpoint: `GET /cursor/chat/discover`
- Tests all chat-related VS Code commands
- Checks Language Model API availability
- Identifies Cursor extensions and their exports
- Checks Chat API availability

**✅ Code Ready:**
- `cursor-addon/src/commandServer.ts` - `discoverChatAPIs()` method
- Returns comprehensive JSON with all findings
- Ready to test when extension is rebuilt

---

### **From Gemini - Deep Research**

**Research Areas:**
- [ ] Cursor's internal architecture and chat implementation
- [ ] VS Code Chat API vs Cursor Chat API differences
- [ ] Extension API capabilities for chat interaction
- [ ] Inter-extension communication patterns
- [ ] Language Model API usage patterns

**Findings:** *(Gemini - please add your findings here)*

---

### **From Grok - Alternative Approaches**

**Research Areas:**
- [ ] Electron IPC communication methods
- [ ] VS Code command execution patterns
- [ ] Webview message passing approaches
- [ ] Keyboard shortcut automation (as last resort)
- [ ] Third-party integration methods

**Findings:** *(Grok - please add your findings here)*

---

## 🔍 **RESEARCH FINDINGS SO FAR**

### **1. VS Code Chat API (Limited)**

**Available APIs:**
- `vscode.chat.createChatParticipant()` - Creates a NEW chat participant (not what we need)
- `vscode.languageModel.sendRequest()` - Uses language models directly (bypasses chat UI)
- `ChatParticipant` interface - For handling incoming requests, not sending messages

**Limitation:** These APIs are for CREATING chat participants, not sending messages to Cursor's built-in chat.

**Status:** ⚠️ Limited - May not solve our use case directly

---

### **2. Cursor-Specific APIs**

**What we know:**
- Cursor is built on VS Code but heavily modified
- Has command server (`localhost:5001` - our extension uses this)
- Supports MCP integration (we already use this)
- Has internal chat system (not directly exposed)

**Unknown:**
- Does Cursor expose chat commands via `vscode.commands.executeCommand()`?
- Can we access Cursor's chat via extension API?
- Is there an inter-extension communication method?

**Status:** 🔍 Researching via discovery endpoint

---

### **3. Language Model API**

**What we know:**
- `vscode.languageModel.sendRequest()` exists
- Can send messages directly to language models
- Bypasses chat UI entirely

**Pros:**
- ✅ Professional API approach
- ✅ No macro needed
- ✅ Direct communication with AI

**Cons:**
- ⚠️ Messages won't appear in chat UI
- ⚠️ User won't see conversation history
- ⚠️ May not match user expectation

**Status:** 🔍 Testing via discovery endpoint

---

## 🧪 **TESTING APPROACH**

### **Phase 1: Command Discovery** ✅ READY

**Endpoint:** `GET http://localhost:5001/cursor/chat/discover`

**What it tests:**
1. Lists all VS Code commands
2. Filters chat-related commands
3. Tests potential chat commands:
   - `workbench.action.chat.open`
   - `workbench.action.chat.focus`
   - `cursor.chat.open`
   - `cursor.chat.send`
   - `cursor.chat.focus`
   - `chat.open`
   - `chat.send`
   - `cursor.showChat`
   - `cursor.sendMessage`
   - `workbench.action.chat.new`
   - `workbench.action.chat.newSession`
4. Checks Language Model API availability
5. Identifies Cursor extensions
6. Checks Chat API availability

**How to test:**
```bash
# Via curl
curl http://localhost:5001/cursor/chat/discover

# Via Electron app
fetch('http://localhost:5001/cursor/chat/discover')
  .then(r => r.json())
  .then(data => console.log(JSON.stringify(data, null, 2)))
```

**Status:** ⏳ Waiting for extension rebuild and test

---

### **Phase 2: Manual Testing**

**Commands to try manually:**
1. `Ctrl+Shift+P` → Type "chat" → See what commands appear
2. `Ctrl+Shift+P` → Type "cursor" → See Cursor-specific commands
3. Check Cursor's keyboard shortcuts (Settings → Keyboard Shortcuts) → Look for chat shortcuts

**Findings:** *(Add manual test results here)*

---

### **Phase 3: Extension API Investigation**

**Test 3: Check Extension Context**
```typescript
// Check if Cursor exposes chat via extension context
const cursorExtension = vscode.extensions.getExtension('cursor.cursor');
if (cursorExtension && cursorExtension.exports) {
    console.log('Cursor extension exports:', Object.keys(cursorExtension.exports));
    // Check for chat-related exports
}
```

**Findings:** *(Add results here)*

---

### **Phase 4: Inter-Extension Communication**

**Test 4: Find Cursor Chat Extension**
```typescript
// List all extensions and find Cursor's chat extension
const allExtensions = vscode.extensions.all;
const cursorExtensions = allExtensions.filter(ext => 
    ext.id.includes('cursor') || 
    ext.packageJSON.publisher === 'cursor'
);

// Check if any expose chat APIs
for (const ext of cursorExtensions) {
    if (ext.exports) {
        console.log(`Extension ${ext.id} exports:`, Object.keys(ext.exports));
    }
}
```

**Findings:** *(Add results here)*

---

## 📋 **IMPLEMENTATION STATUS**

### **Discovery Endpoint** ✅ COMPLETE

**File:** `cursor-addon/src/commandServer.ts`
- Method: `discoverChatAPIs()`
- Endpoint: `GET /cursor/chat/discover`
- Status: Ready to test after rebuild

**Next:** Rebuild extension and test endpoint

---

### **Research Document** ✅ COMPLETE

**File:** `cursor-addon/CURSOR_CHAT_API_RESEARCH.md`
- Comprehensive research plan
- Testing approaches documented
- Findings structure ready

**Next:** Collect findings from all researchers

---

## 🎯 **EXPECTED OUTCOMES**

### **Best Case Scenario:**
- ✅ Find `cursor.chat.sendMessage` or similar command
- ✅ Can execute via `vscode.commands.executeCommand()`
- ✅ Professional API-based solution
- ✅ Messages appear in chat UI
- ✅ User sees conversation history

### **Worst Case Scenario:**
- ❌ No direct chat API exists
- ❌ Must use macro fallback (Option 1)
- ❌ Or use Language Model API (bypasses chat UI)

### **Middle Ground:**
- ⚠️ Find command to open chat
- ⚠️ Language Model API works but doesn't show in UI
- ⚠️ Hybrid approach needed (API + minimal macro)

---

## 📝 **RESEARCH LOG**

### **2025-11-01 - Initial Research**

**Aether Findings:**
- VS Code Chat API exists but is for creating participants, not sending messages
- Language Model API exists but bypasses chat UI
- Discovery endpoint built and ready for testing
- Need to test actual Cursor installation to see available commands

**Next Steps:**
- Rebuild extension
- Test discovery endpoint
- Analyze results
- Decide on implementation approach

---

### **Gemini Findings:**

*(Gemini - add your findings here)*

---

### **Grok Findings:**

*(Grok - add your findings here)*

---

## 🔗 **REFERENCES**

### **Official Documentation:**
- [VS Code Chat API Documentation](https://code.visualstudio.com/api/extension-guides/chat)
- [VS Code Language Model API](https://code.visualstudio.com/api/extension-guides/language-model)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [VS Code Commands API](https://code.visualstudio.com/api/extension-guides/command)

### **Community Resources:**
- Cursor GitHub Issues (search for "chat API" or "extension")
- VS Code Extension Examples
- Stack Overflow discussions

### **Research Tools:**
- Discovery Endpoint: `GET /cursor/chat/discover`
- Command Palette: `Ctrl+Shift+P` → Search "chat"
- VS Code Developer Tools: `Help → Toggle Developer Tools`

---

## 📊 **DECISION MATRIX**

| Approach | Professional | Works Now | Shows in UI | Maintainable | Score |
|----------|-------------|-----------|-------------|--------------|-------|
| **Option 1: Macro** | ⚠️ 2/5 | ✅ 5/5 | ✅ 5/5 | ⚠️ 2/5 | 14/20 |
| **Option 2: API** | ✅ 5/5 | ❓ 0/5 | ✅ 5/5 | ✅ 5/5 | 15/20* |
| **Option 3: Hybrid** | ✅ 4/5 | ✅ 4/5 | ✅ 5/5 | ✅ 4/5 | 17/20 |
| **Language Model API** | ✅ 5/5 | ❓ 0/5 | ❌ 0/5 | ✅ 5/5 | 10/20 |

*Score assumes API exists - will update after discovery

---

## ✅ **NEXT STEPS**

1. **Rebuild Extension**
   ```bash
   cd cursor-addon
   npm run compile
   npm run package
   ```

2. **Test Discovery Endpoint**
   - Call `GET http://localhost:5001/cursor/chat/discover`
   - Analyze results
   - Document findings

3. **Collaborative Analysis**
   - Gemini: Deep dive on findings
   - Grok: Alternative approaches
   - Aether: Implementation planning

4. **Decision Point**
   - Based on all findings, decide on approach
   - Implement chosen solution
   - Document implementation

---

**Status:** Multi-AI research in progress  
**Priority:** High (determines implementation approach)  
**Estimated Completion:** After discovery endpoint testing + Gemini/Grok findings
