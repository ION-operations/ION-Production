# COMMAND DEBUGGING - Why Output Panels Are Empty

**Issue:** Commands show empty Output panels

**Root Cause Analysis:**

## 1. Show Extension Logs (`aimos.showLogs`)
- **What it does:** Shows a QuickPick (dropdown picker) to select log file
- **NOT an Output panel command** - It opens log file in editor
- **If you see empty Output:** Wrong command or command not executing
- **Expected behavior:** QuickPick appears at top of screen

## 2. Debug Dashboard (`aimos.debugDashboard`)
- **What it does:** Creates Output channel named "AIM-OS Debug"
- **Output location:** Output panel → **Dropdown → Select "AIM-OS Debug"**
- **If empty:** Either command not executing OR wrong channel selected
- **Check:** Look at Output panel dropdown - is "AIM-OS Debug" in the list?

## 3. Run Full Diagnostic (`aimos.runFullDiagnostic`)
- **What it does:** Uses AIMOSLogger which writes to "AIM-OS Extension" channel
- **Output location:** Output panel → **Dropdown → Select "AIM-OS Extension"**
- **If empty:** Either command not executing OR wrong channel selected
- **Check:** Look at Output panel dropdown - is "AIM-OS Extension" in the list?

---

## 🔍 DEBUGGING STEPS:

### Step 1: Verify Commands Are Executing
Add console.log to verify commands are called:

```typescript
// In showLogs.ts
export function registerShowLogsCommand(context: vscode.ExtensionContext) {
    const showLogsCommand = vscode.commands.registerCommand('aimos.showLogs', async () => {
        console.log('🔵 SHOW LOGS COMMAND CALLED'); // Add this
        vscode.window.showInformationMessage('Show Logs command executed!'); // Add this
        
        // ... rest of code
```

### Step 2: Check Output Channel Dropdown
1. Open Output panel (View → Output)
2. Click dropdown in top-right of Output panel
3. Look for:
   - "AIM-OS Extension" (for Run Full Diagnostic)
   - "AIM-OS Debug" (for Debug Dashboard)
4. Select the correct channel

### Step 3: Verify Commands Are Registered
Check Developer Tools console:
1. Help → Toggle Developer Tools
2. Console tab
3. Type: `vscode.commands.getCommands().then(cmds => console.log(cmds.filter(c => c.includes('aimos'))))`
4. Should see: `['aimos.showLogs', 'aimos.debugDashboard', 'aimos.runFullDiagnostic', ...]`

---

## 🚨 POSSIBLE ISSUES:

### Issue 1: Commands Not Executing
- **Symptom:** Nothing happens when command clicked
- **Cause:** Command not registered or activation failed
- **Fix:** Check extension activation logs

### Issue 2: Wrong Output Channel Selected
- **Symptom:** Output panel empty but logs exist
- **Cause:** Looking at wrong channel in dropdown
- **Fix:** Check Output panel dropdown

### Issue 3: Output Channel Not Created
- **Symptom:** Channel doesn't exist in dropdown
- **Cause:** Command not executing or error in command
- **Fix:** Check Developer Tools console for errors

---

## ✅ QUICK TEST:

Run this in Developer Tools console:
```javascript
vscode.commands.executeCommand('aimos.showLogs').then(() => console.log('Show Logs executed'));
```

If you see "Show Logs executed" but no QuickPick appears, command is executing but QuickPick failing.

If you see error, command not registered or activation issue.

