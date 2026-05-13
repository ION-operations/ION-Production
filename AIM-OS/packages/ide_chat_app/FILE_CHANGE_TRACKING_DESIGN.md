# File Change Tracking System - Design Document

**Date:** 2025-11-02  
**Status:** 📋 **DESIGN COMPLETE - IMPLEMENTATION IN PROGRESS**  
**Purpose:** Track file changes via MCP messages and display in Monaco diff viewer

---

## 🎯 **OVERVIEW**

**Goal:** Show latest file changes in Electron app using Monaco editor diff view, similar to Cursor's file change tracking.

**Approach:** Use MCP messages with specific tags to notify of file changes, then display in organized Monaco diff viewer.

---

## 🔧 **HOW IT WORKS**

### **1. Agent Notification Protocol**

**When agents make file changes, they MUST send MCP messages with these tags:**

```typescript
// Example: Agent modifies a file
await send_ai_message({
  from_ai: "Aether",
  to_ai: "electron-app",
  content: "Modified packages/ide_chat_app/src/App.tsx",
  message_type: "status_update",
  tags: {
    type: "file_change",
    file_path: "packages/ide_chat_app/src/App.tsx",
    operation: "modified", // "created" | "modified" | "deleted"
    old_content: "...", // Optional: previous file content
    new_content: "...", // Optional: new file content
    diff: "...", // Optional: unified diff format
    agent: "aether",
    timestamp: new Date().toISOString()
  }
})
```

**Required Tags:**
- `type: "file_change"` - Identifies this as a file change notification
- `file_path` - Full path to the file
- `operation` - Type of change (created/modified/deleted)

**Optional Tags:**
- `old_content` - Previous file content (for diff view)
- `new_content` - New file content (for diff view)
- `diff` - Unified diff format (alternative to old/new content)
- `agent` - Agent name who made the change
- `timestamp` - When change occurred

---

### **2. File Changes Viewer Component**

**Features:**
- **List View:** Shows all recent file changes grouped by file
- **Filtering:** Filter by operation type, agent, time period
- **Diff View:** Monaco diff editor showing old vs new content
- **Auto-refresh:** Polls for new changes every 5 seconds
- **Expandable Groups:** Group changes by file, expand to see all changes

**UI Layout:**
```
┌─────────────────────────────────────────┐
│ File Changes Viewer                     │
├──────────────┬──────────────────────────┤
│ File List    │ Diff Viewer              │
│              │                          │
│ • App.tsx    │ [Monaco Diff Editor]    │
│   - modified │                          │
│   - modified │                          │
│ • Main.tsx   │                          │
│   - created  │                          │
└──────────────┴──────────────────────────┘
```

---

### **3. Cursor Extension Integration (Future)**

**Option A: VS Code File Watcher API**
```typescript
// In Cursor extension
const watcher = vscode.workspace.createFileSystemWatcher('**/*');
watcher.onDidChange(async (uri) => {
  // Get file content
  const doc = await vscode.workspace.openTextDocument(uri);
  const content = doc.getText();
  
  // Send MCP message with file change
  await sendFileChangeNotification({
    file_path: uri.fsPath,
    operation: 'modified',
    new_content: content
  });
});
```

**Option B: Command Server Endpoint**
```typescript
// Add to CommandServer
POST /cursor/file-changes
{
  "file_path": "...",
  "operation": "modified",
  "content": "..."
}
```

---

### **4. Agent Protocol Enhancement**

**Update Cursor Rules to require file change notifications:**

```markdown
## FILE CHANGE NOTIFICATION PROTOCOL

**When modifying files:**
1. Make file changes
2. Send MCP message with file_change tags
3. Include file path, operation type, and content (if available)

**Example:**
```typescript
// After modifying a file
await mcp_lucid-mcp_send_ai_message({
  from_ai: "Aether",
  to_ai: "electron-app",
  content: `Modified ${filePath}`,
  message_type: "status_update",
  tags: {
    type: "file_change",
    file_path: filePath,
    operation: "modified",
    new_content: newContent, // If available
    agent: "aether"
  }
})
```
```

---

## 📊 **IMPLEMENTATION STATUS**

### **✅ Completed:**
- FileChangesViewer component created
- MCP message polling for file_change tags
- Monaco diff editor integration
- Grouped file list view
- Expandable groups

### **⏳ Pending:**
- Cursor extension file watcher integration
- Automatic content reading for diff view
- Agent protocol updates in Cursor rules
- File content caching for diff comparison

---

## 🚀 **NEXT STEPS**

1. **Update Cursor Rules** - Add file change notification protocol
2. **Add Cursor Extension Endpoint** - File watcher → MCP message bridge
3. **Enhance Agent Tools** - Auto-notify on file changes
4. **Add File Content Reading** - Read files for diff view when content not in message

---

**Status:** Core component ready, needs agent protocol updates and Cursor integration

