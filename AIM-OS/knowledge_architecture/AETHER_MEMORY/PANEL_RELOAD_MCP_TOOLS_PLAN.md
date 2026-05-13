# Panel/Webview Reload MCP Tools - Research & Implementation Plan

**Date:** 2025-01-27  
**Status:** ✅ **IMPLEMENTATION PLAN**

---

## 🎯 **GOAL**

Create MCP tools that allow reloading individual panels/webviews without reloading the entire Cursor window.

**Benefits:**
- ⚡ **Much faster iteration** (no full reload)
- 🔄 **Instant feedback** when testing changes
- 🎯 **Targeted reloads** (only what changed)
- 🛠️ **Better debugging** workflow

---

## 📚 **VS CODE API CAPABILITIES**

### **1. WebviewView Refresh Methods:**

**Option A: Update HTML Directly**
```typescript
// Store reference to webview in provider
private _view?: vscode.WebviewView;

// Update HTML without reload
public refresh(): void {
    if (this._view) {
        this._view.webview.html = this.getWebviewContent(this._view.webview);
    }
}
```

**Option B: Force View Refresh**
```typescript
// VS Code command to refresh view
await vscode.commands.executeCommand('workbench.action.webview.reloadWebviewAction');
// OR trigger resolveWebviewView again
await vscode.commands.executeCommand('workbench.view.extension.aimos');
```

**Option C: Dispose and Recreate**
```typescript
// Dispose current view
this._view?.dispose();
// Trigger view to resolve again
await vscode.commands.executeCommand('workbench.view.extension.aimos');
```

### **2. VS Code Commands Available:**

```typescript
// Reload entire window (too heavy)
'workbench.action.reloadWindow'

// Focus/show view (might trigger resolve)
'workbench.view.extension.aimos'

// Webview-specific commands
'workbench.action.webview.reloadWebviewAction'  // Reloads active webview
```

---

## 🛠️ **IMPLEMENTATION PLAN**

### **Phase 1: Provider Refresh Method**

**File:** `cursor-addon/src/superBasicDashboardProvider.ts`

```typescript
export class SuperBasicDashboardProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;
    
    // ✅ ADD: Refresh method
    public refresh(): void {
        if (this._view) {
            AIMOSLogger.log('SUPER_BASIC', '🔄 Refreshing webview...');
            this._outputChannel.appendLine('🔄 Refreshing webview...');
            
            // Update HTML with new content
            this._view.webview.html = this.getWebviewContent(this._view.webview);
            
            AIMOSLogger.log('SUPER_BASIC', '✅ Webview refreshed');
            this._outputChannel.appendLine('✅ Webview refreshed');
        } else {
            AIMOSLogger.log('SUPER_BASIC', '⚠️ Webview not yet initialized');
        }
    }
    
    // ✅ ADD: Get current HTML
    public getCurrentHtml(): string {
        return this._view?.webview.html || '';
    }
}
```

### **Phase 2: VS Code Command**

**File:** `cursor-addon/src/extension.ts`

```typescript
// Store provider reference globally
let superBasicDashboardProvider: SuperBasicDashboardProvider;

// Register refresh command
vscode.commands.registerCommand('aimos.refreshDashboard', () => {
    if (superBasicDashboardProvider) {
        superBasicDashboardProvider.refresh();
        vscode.window.showInformationMessage('Dashboard refreshed!');
    } else {
        vscode.window.showErrorMessage('Dashboard provider not initialized');
    }
});
```

### **Phase 3: Command Server Endpoint**

**File:** `cursor-addon/src/commandServer.ts`

```typescript
// POST /cursor/webview/refresh
private async handleRefreshWebview(request: {
    viewId: string;
}): Promise<any> {
    try {
        const viewId = request.viewId || 'aimosDashboard';
        
        // Execute VS Code command
        await vscode.commands.executeCommand('aimos.refreshDashboard');
        
        return {
            success: true,
            message: `Webview ${viewId} refreshed`,
            timestamp: new Date().toISOString()
        };
    } catch (error: any) {
        return {
            success: false,
            error: error.message
        };
    }
}
```

### **Phase 4: MCP Tool**

**File:** `lucid_mcp_server.py`

```python
{
    "name": "refresh_webview",
    "description": "Refresh/reload a specific webview panel without reloading the entire Cursor window. Faster than full reload.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "view_id": {
                "type": "string",
                "description": "The view ID to refresh (e.g., 'aimosDashboard', 'simpleTestPanel')",
                "default": "aimosDashboard"
            }
        },
        "required": []
    }
}
```

---

## 📋 **PROPOSED MCP TOOLS**

### **1. refresh_webview**
**Purpose:** Reload a specific webview panel  
**Parameters:**
- `view_id` (string, optional): View ID to refresh (default: 'aimosDashboard')

**Returns:**
- Success status
- Timestamp of refresh
- Current HTML length

### **2. get_webview_html**
**Purpose:** Get current HTML content of a webview  
**Parameters:**
- `view_id` (string, optional): View ID to get HTML from

**Returns:**
- Current HTML content
- HTML length
- Last updated timestamp

### **3. update_webview_html**
**Purpose:** Update webview HTML directly (for testing)  
**Parameters:**
- `view_id` (string, optional): View ID to update
- `html` (string, required): New HTML content

**Returns:**
- Success status
- New HTML length

### **4. reload_extension**
**Purpose:** Reload the extension (heavier, but sometimes needed)  
**Parameters:**
- None

**Returns:**
- Success status
- Note: This will reload the entire extension

---

## 🎯 **USE CASES**

### **1. Testing UI Changes:**
```python
# Make change to superBasicDashboardProvider.ts
# Compile
# Refresh webview - NO FULL RELOAD NEEDED!
refresh_webview(view_id="aimosDashboard")
```

### **2. Debugging:**
```python
# Check current HTML
get_webview_html(view_id="aimosDashboard")

# Update HTML to test
update_webview_html(view_id="aimosDashboard", html="<html>...test...</html>")
```

### **3. Quick Iteration:**
```python
# No more waiting for full reload!
# Just refresh the panel
refresh_webview(view_id="aimosDashboard")
```

---

## ✅ **IMPLEMENTATION CHECKLIST**

- [ ] Add `refresh()` method to `SuperBasicDashboardProvider`
- [ ] Register `aimos.refreshDashboard` VS Code command
- [ ] Add Command Server endpoint `/cursor/webview/refresh`
- [ ] Add MCP tool `refresh_webview`
- [ ] Test refresh functionality
- [ ] Document usage

---

## 📊 **EXPECTED BENEFITS**

**Before:**
- Full Cursor reload: ~5-10 seconds
- Lose context/state
- Slow iteration

**After:**
- Webview refresh: <1 second
- Keep context/state
- Fast iteration

---

**Status:** ✅ **Ready to implement**  
**Priority:** HIGH (Major developer experience improvement)  
**Confidence:** 0.85 (VS Code API supports this)

---

*Research & Implementation Plan by Aether*  
*2025-01-27*

