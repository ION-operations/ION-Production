# ⚠️ UI PANEL WORK - READ THIS FIRST

**CRITICAL:** Before working on ANY extension UI panels, read this.

## 🚨 **THE RULES (NEVER VIOLATE)**

1. **NO Sidebar Views** - Use `createWebviewPanel` ONLY
2. **Single Command** - ONE dashboard command only
3. **ViewColumn.Beside** - Force editor area explicitly
4. **Dispose Old Panels** - Don't reuse wrong location panels
5. **Document Failures** - Use MCP tools before fixing

## ✅ **WORKING PATTERN:**

```typescript
// ✅ THIS WORKS - Copy this pattern
vscode.commands.registerCommand('aimos.openDashboard', () => {
    // Dispose old panel
    if (currentPanel) {
        currentPanel.dispose();
        currentPanel = undefined;
    }
    
    // Create NEW panel in editor area
    const panel = vscode.window.createWebviewPanel(
        'aimosUI',
        'AIM-OS Dashboard',
        vscode.ViewColumn.Beside,  // ✅ Editor area
        {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [...]
        }
    );
    panel.webview.html = getContent();
    currentPanel = panel;
});
```

## ❌ **NEVER DO THIS:**

```typescript
// ❌ DON'T USE - Sidebar view
vscode.window.registerWebviewViewProvider('aimosDashboard', provider);

// ❌ DON'T USE - Reuse wrong location
if (currentPanel) {
    currentPanel.reveal(column);  // Keeps wrong location!
}

// ❌ DON'T USE - Multiple commands
"aimos.showDashboard", "aimos.openDashboard", "aimos.forceOpenDashboard"

// ❌ DON'T USE - Sidebar registration
"views": { "explorer": [...] }
```

## 📋 **CHECKLIST:**

- [ ] No `views.explorer` in package.json
- [ ] No `viewsContainers.activitybar` in package.json  
- [ ] Only ONE dashboard command
- [ ] Uses `createWebviewPanel` (not `registerWebviewViewProvider`)
- [ ] Uses `ViewColumn.Beside` explicitly
- [ ] Disposes old panels before creating new
- [ ] Tested that panel opens in EDITOR AREA (not sidebar)

## 📚 **Full Documentation:**

See `CRITICAL_UI_PANEL_FAILURE_DOCUMENTATION.md` for complete details.

---

**Remember:** Sidebar views = NIGHTMARE. Editor panels = WORKS.

