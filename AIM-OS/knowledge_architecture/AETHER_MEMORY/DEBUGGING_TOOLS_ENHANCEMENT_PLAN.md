# Additional Cursor State Access Tools - Debugging Enhancement Plan

**Date:** 2025-01-27  
**Purpose:** Identify additional Cursor IDE state access tools to aid AI debugging  
**Current:** Terminal management tools implemented and working  
**Next:** Expand to console, output channels, diagnostics, and editor state

---

## 🎯 **HIGH PRIORITY - DEBUGGING ESSENTIALS**

### **1. Output Channels Access** ⭐⭐⭐
**Why:** Critical for debugging - see extension logs, errors, warnings  
**VS Code API:** `vscode.window.activeTextEditor`, `vscode.workspace.createOutputChannel()`

**Tools to Create:**
- `get_output_channel(channelName)` - Get specific output channel content
- `list_output_channels()` - List all available output channels
- `get_output_channel_logs(channelName, limit)` - Get recent logs from channel

**Use Cases:**
- See extension logs without manual steps
- Debug MCP server errors
- Check Command Server logs
- View diagnostic output

**Implementation:**
```typescript
// Already partially implemented in cursorStateReader.ts
static async getOutputChannel(channelName: string): Promise<string> {
    const channel = vscode.window.createOutputChannel(channelName);
    // VS Code doesn't expose reading output channels directly
    // Alternative: Read from log files or use extension API
}
```

### **2. Developer Console Access** ⭐⭐⭐
**Why:** F12 console shows runtime errors, extension host logs  
**VS Code API:** Limited - console logs go to Developer Tools (not directly accessible)

**Tools to Create:**
- `get_console_errors()` - Get recent console errors from Extension Host
- `get_extension_host_logs()` - Get Extension Host output logs
- `get_webview_console_logs()` - Get webview console logs (if accessible)

**Use Cases:**
- See JavaScript errors immediately
- Debug extension activation issues
- Check webview console errors
- Find runtime exceptions

**Implementation:**
```typescript
// VS Code doesn't expose Developer Tools console directly
// Alternative approaches:
// 1. Read Extension Host log files
// 2. Use Output Channel for extension logs
// 3. Create custom logging that writes to accessible location
```

### **3. Problems Panel / Diagnostics** ⭐⭐⭐
**Why:** See linter errors, TypeScript errors, diagnostic issues  
**VS Code API:** `vscode.languages.getDiagnostics()`

**Tools to Create:**
- `get_problems()` - Get all diagnostics (errors, warnings, info)
- `get_file_problems(filePath)` - Get diagnostics for specific file
- `get_workspace_problems()` - Get all workspace diagnostics
- `get_problem_summary()` - Summary of error/warning counts

**Use Cases:**
- See TypeScript compilation errors
- Check linter warnings
- Debug file issues
- Track code quality

**Implementation:**
```typescript
static async getProblems(): Promise<Diagnostic[]> {
    const diagnostics = vscode.languages.getDiagnostics();
    return diagnostics.flatMap(([uri, diags]) => 
        diags.map(d => ({
            file: uri.fsPath,
            severity: d.severity,
            message: d.message,
            range: d.range,
            source: d.source
        }))
    );
}
```

### **4. Editor State (Enhanced)** ⭐⭐
**Why:** Current implementation exists but could be enhanced  
**Already Implemented:** `get_active_editor()`, `get_workspace_state()`

**Enhancements Needed:**
- `get_editor_selection()` - Get current selection details
- `get_open_editors()` - List all open editor tabs
- `get_cursor_position()` - Get cursor line/column
- `get_file_content(uri)` - Get file content (for debugging)
- `get_editor_history()` - Recent files opened

**Use Cases:**
- See what file user is editing
- Check cursor position for context
- See all open files
- Read file content for debugging

---

## 🔍 **MEDIUM PRIORITY - USEFUL DEBUGGING**

### **5. Debug Console Access** ⭐⭐
**Why:** See debug output, breakpoint info, variable values  
**VS Code API:** `vscode.debug.activeDebugConsole`

**Tools to Create:**
- `get_debug_console_output()` - Get debug console content
- `get_active_debug_session()` - Get current debug session info
- `get_breakpoints()` - List all breakpoints

**Use Cases:**
- See debug output
- Check debug session status
- Debug breakpoint issues

### **6. Status Bar Information** ⭐
**Why:** See current status, branch, errors count  
**VS Code API:** Limited - status bar items are extensions

**Tools to Create:**
- `get_status_bar_info()` - Get status bar text (if accessible)
- `get_notifications()` - Get recent notifications
- `get_error_count()` - Get error count from status bar

**Use Cases:**
- Quick status check
- See notifications
- Check error counts

### **7. Extension State** ⭐⭐
**Why:** See which extensions are active, errors, activation status  
**VS Code API:** `vscode.extensions.all`

**Tools to Create:**
- `get_extension_status(extensionId)` - Get extension activation status
- `get_extensions_list()` - List all installed extensions
- `get_extension_errors()` - Get extension errors

**Use Cases:**
- Debug extension issues
- Check if extension is active
- See extension errors

### **8. Git State** ⭐
**Why:** See current branch, changes, git status  
**VS Code API:** Git extension API (if available)

**Tools to Create:**
- `get_git_status()` - Get git status
- `get_current_branch()` - Get current branch
- `get_git_changes()` - Get uncommitted changes

**Use Cases:**
- Context for debugging
- See what changed
- Check git state

---

## 📋 **IMPLEMENTATION PRIORITY**

### **Phase 1: Essential Debugging (Highest Priority)**
1. ✅ **Problems Panel** - `get_problems()`, `get_file_problems()`
2. ✅ **Output Channels** - `list_output_channels()`, `get_output_channel()`
3. ✅ **Console Errors** - `get_console_errors()` (via log files)

**Why:** These give immediate insight into what's broken

### **Phase 2: Enhanced Editor State**
4. ✅ **Editor Enhancements** - `get_open_editors()`, `get_selection()`, `get_file_content()`
5. ✅ **Debug Console** - `get_debug_console_output()`

**Why:** More context about current state

### **Phase 3: Additional Context**
6. ✅ **Extension State** - `get_extension_status()`, `get_extensions_list()`
7. ✅ **Notifications** - `get_notifications()`
8. ✅ **Git State** - `get_git_status()`

**Why:** Additional debugging context

---

## 🛠️ **IMPLEMENTATION PLAN**

### **Step 1: Problems Panel Access**
```typescript
// cursorStateReader.ts
static async getProblems(): Promise<ProblemInfo[]> {
    const diagnostics = vscode.languages.getDiagnostics();
    const problems: ProblemInfo[] = [];
    
    for (const [uri, diags] of diagnostics) {
        for (const diag of diags) {
            problems.push({
                file: uri.fsPath,
                severity: this.getSeverityLabel(diag.severity),
                message: diag.message,
                line: diag.range.start.line + 1,
                column: diag.range.start.character + 1,
                source: diag.source || 'unknown'
            });
        }
    }
    
    return problems;
}

static async getProblemSummary(): Promise<ProblemSummary> {
    const problems = await this.getProblems();
    return {
        total: problems.length,
        errors: problems.filter(p => p.severity === 'error').length,
        warnings: problems.filter(p => p.severity === 'warning').length,
        info: problems.filter(p => p.severity === 'info').length
    };
}
```

### **Step 2: Output Channels**
```typescript
// VS Code limitation: Can't read output channels directly
// Alternative: Read from extension log files
static async getOutputChannels(): Promise<string[]> {
    // Return list of known output channels
    return ['AIM-OS Dashboard', 'AIM-OS Extension', 'Extension Host'];
}

static async getExtensionLogs(): Promise<string> {
    // Read from extension log file
    const logPath = path.join(context.extensionPath, 'logs', '*.log');
    // Read latest log file
    return logContent;
}
```

### **Step 3: Console Errors**
```typescript
// Read Extension Host console from log files
static async getConsoleErrors(): Promise<ConsoleError[]> {
    // Read from Extension Host log
    // Parse for errors
    return errors;
}
```

---

## 🎯 **RECOMMENDED NEXT IMPLEMENTATION**

### **Priority Order:**
1. **Problems Panel** (Highest) - Immediate error visibility
2. **Output Channels** - Extension logs access
3. **Enhanced Editor State** - Better context
4. **Console Errors** - Runtime error visibility

### **Quick Wins:**
- Problems Panel: Easy to implement, high value
- Output Channels: Medium complexity, high value
- Editor Enhancements: Easy, medium value

---

## 📊 **EXPECTED IMPACT**

### **Before (Current State):**
- ❌ Can't see TypeScript errors
- ❌ Can't see extension logs
- ❌ Can't see console errors
- ❌ Limited editor context

### **After (With New Tools):**
- ✅ See all problems immediately
- ✅ Access extension logs
- ✅ See console errors
- ✅ Full editor context
- ✅ Better debugging capability

---

**Status:** Planning complete  
**Next Step:** Implement Problems Panel access first (highest priority)  
**Confidence:** 0.90 (high - VS Code APIs well documented)

---

*Debugging enhancement plan created by Aether*  
*2025-01-27*

