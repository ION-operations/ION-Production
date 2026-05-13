# 🌐 Standalone Browser vs Cursor Extension Testing

**Date:** 2025-01-27  
**Purpose:** Clarify testing options for React UI panel

---

## ✅ **YES - Same React UI Panel!**

The standalone browser panel shows **the exact same React UI** as the Cursor extension panel:
- Same `MainDashboard` component
- Same tabs (Agents, Chat, Chains, Tools, Timeline, NL Tags)
- Same chat interface
- Same agent management

---

## 🔌 **BUT - Different Connection Methods**

### **Standalone Browser Panel:**
```
React UI → HTTP API (http://localhost:8000/mcp/tools/call)
  ↓
MCP Server (if HTTP endpoints exist)
```

**Limitations:**
- ⚠️ Requires MCP server to expose HTTP API endpoints
- ⚠️ Currently, `AIMOSService.ts` tries HTTP API first, but endpoint may not exist
- ✅ Can test UI layout, navigation, components
- ✅ Can test if HTTP API works

### **Cursor Extension Panel:**
```
React UI → Extension Bridge (vscode.postMessage)
  ↓
Extension → MCP Client → MCP Server
```

**Advantages:**
- ✅ Full extension bridge implementation
- ✅ Uses Cursor's MCP integration
- ✅ Complete round-trip functionality

---

## 🧪 **What You Can Test Where**

### **Standalone Browser (`start-standalone.ps1`):**
✅ **CAN TEST:**
- UI layout and design
- Component rendering
- Navigation between tabs
- Form inputs and interactions
- Visual appearance
- If HTTP API endpoints exist and work

❌ **CANNOT TEST:**
- Extension bridge (`vscode.postMessage` won't exist)
- Cursor-specific features
- Extension → MCP connection

### **Cursor Extension Panel:**
✅ **CAN TEST:**
- Everything from standalone browser
- Extension bridge functionality
- Full MCP tool calls via extension
- Complete user → agent chat
- Agent communications visibility
- Round-trip conversations

---

## 🔧 **Current Connection Flow**

### **In `AIMOSService.ts`:**

```typescript
// 1. Try HTTP API first
try {
  const response = await fetch(`${this.baseUrl}/mcp/tools/call`, {
    method: 'POST',
    body: JSON.stringify({ name: 'mcp_lucid-mcp_send_ai_message', ... })
  })
  // Use response if successful
} catch (httpError) {
  // HTTP API failed, try extension bridge
}

// 2. Fallback: Extension bridge (only works in Cursor)
if (typeof window !== 'undefined' && (window as any).vscode) {
  vscode.postMessage({ command: 'mcpCall', ... })
  // Extension forwards to MCP server
}
```

---

## 📋 **Testing Strategy**

### **Option 1: Test UI in Standalone Browser**
1. Run `start-standalone.ps1`
2. Test UI layout, navigation, visual appearance
3. Check if HTTP API endpoints work (if MCP server exposes them)
4. **Good for:** UI/UX testing, visual debugging

### **Option 2: Test Full Functionality in Cursor**
1. Install extension (`aimos-cursor-addon.vsix`)
2. Open React UI panel in Cursor
3. Test complete functionality:
   - User → Agent chat
   - Agent communications
   - Extension bridge
   - MCP tool calls
4. **Good for:** End-to-end testing, extension bridge verification

---

## ⚠️ **Current Limitation**

**MCP Server HTTP API:**
- `AIMOSService.ts` tries to call `http://localhost:8000/mcp/tools/call`
- This endpoint may not exist on the MCP server
- **Need to verify:** Does `lucid_mcp_server.py` expose HTTP endpoints?

**If HTTP API doesn't exist:**
- Standalone browser will fall back to mock/error
- Cursor extension will use extension bridge (works!)

---

## 💡 **Recommendation**

**For Testing Extension Bridge:**
- ✅ Use Cursor extension panel (full functionality)
- ✅ Install extension and test in Cursor

**For Testing UI:**
- ✅ Use standalone browser (faster, no extension needed)
- ✅ Test layout, navigation, visual appearance
- ⚠️ MCP functionality may not work without HTTP API

---

## 🎯 **Bottom Line**

**YES - Same React UI panel!** But:
- **Standalone browser:** Tests UI, may not test MCP (depends on HTTP API)
- **Cursor extension:** Tests everything including extension bridge

**Best approach:** Test UI in browser, test functionality in Cursor! 💙

