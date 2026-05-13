# Cursor 2.0 Project/User Commands - Research Notes

**Date:** 2025-11-03  
**Status:** ⚠️ **RESEARCH NEEDED**  
**Purpose:** Understand Cursor 2.0 project/user commands API

---

## 🔍 **WHAT ARE CURSOR 2.0 PROJECT/USER COMMANDS?**

**Cursor 2.0** introduces new command types:
- **Project Commands** - Commands scoped to a specific project/workspace
- **User Commands** - Commands scoped to a user account (persist across projects)

**Potential Use Cases:**
- Project-specific automation scripts
- User-level preferences and shortcuts
- Custom workflows per project
- Shared commands across workspaces

---

## 📋 **RESEARCH FINDINGS**

### **1. VS Code API (Baseline)**

**Standard VS Code Commands:**
- `vscode.commands.executeCommand()` - Execute any command
- Commands registered in `package.json` or programmatically
- Commands can be project-scoped or global

**Limitations:**
- No built-in "project commands" vs "user commands" distinction
- All commands are either extension-scoped or global

---

### **2. Cursor-Specific Extensions**

**Cursor may have:**
- Custom API extensions for project/user commands
- Configuration files (`.cursor/commands.json`?)
- Workspace settings for project commands
- User settings for user commands

**Status:** ⚠️ **NEEDS VERIFICATION**

---

### **3. Integration Approach**

**Option A: Configuration Files**
```
.cursor/commands.json (project-level)
~/.cursor/commands.json (user-level)
```

**Option B: VS Code Settings**
```
.vscode/settings.json (project-level)
User Settings (user-level)
```

**Option C: Extension API**
```
cursor.commands.registerProjectCommand()
cursor.commands.registerUserCommand()
```

**Status:** ⚠️ **NEEDS VERIFICATION**

---

## 🔧 **INTEGRATION PLAN**

### **If Project/User Commands Exist:**

**1. Wrap in Envelope Protocol:**
```typescript
{
  v: 1,
  id: "cmd-123",
  kind: "request",
  topic: "cursor.projectCommand",
  payload: {
    command: "custom-build",
    args: [...]
  }
}
```

**2. Route via Message Router:**
- Register handler for `cursor.projectCommand`
- Register handler for `cursor.userCommand`
- Ensure idempotency
- Dead letter queue for failures

**3. Execute via VS Code API:**
```typescript
// If available
await vscode.commands.executeCommand('cursor.projectCommand', command, args);
// Or custom implementation
```

---

## 📝 **NEXT STEPS**

1. **Research Cursor 2.0 Documentation**
   - Check Cursor release notes
   - Look for API documentation
   - Search for project/user command examples

2. **Test in Cursor IDE**
   - Try executing custom commands
   - Check if project/user distinction exists
   - Verify API availability

3. **Implement Integration**
   - If available: Wrap in envelope protocol
   - If not: Document limitation
   - Create handlers for future support

---

## 🎯 **CURRENT STATUS**

**Known:**
- ✅ VS Code commands work via `vscode.commands.executeCommand()`
- ✅ Commands can be registered programmatically
- ✅ Commands can be project-scoped via workspace settings

**Unknown:**
- ❓ Does Cursor 2.0 have project/user command distinction?
- ❓ Is there a Cursor-specific API for this?
- ❓ How are project/user commands stored/configured?

**Recommendation:**
- ⚠️ **Research first** before implementing
- Document findings
- Create integration plan based on actual API

---

*Created: 2025-11-03*  
*Status: Research Needed*  
*Next: Investigate Cursor 2.0 API documentation*

