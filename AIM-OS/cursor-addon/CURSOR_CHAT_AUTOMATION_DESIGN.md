# Cursor Chat Automation Design

**Date:** 2025-11-01  
**Status:** Design Phase  
**Goal:** Enable Electron app/daemon to programmatically send messages to Cursor chat

---

## 🎯 **THE PROBLEM**

You want to automate sending messages to Cursor chat from:
- Electron app
- Daemon (Python service)
- Macros/scripts

**Challenge:** Cursor doesn't expose a direct API for sending chat messages programmatically.

---

## 🔍 **THREE APPROACHES**

### **Option 1: Keyboard/Mouse Macro (RECOMMENDED FOR NOW)**

**How it works:**
- Electron app/daemon calls Extension Command Server (`localhost:5001`)
- Extension executes macro script (AutoHotkey on Windows, AppleScript on Mac)
- Macro simulates keyboard/mouse to:
  1. Focus Cursor chat input
  2. Type the message
  3. Send it (Enter key or click send button)

**Pros:**
- ✅ Works immediately (no Cursor API needed)
- ✅ Reliable (you've done complex macros before)
- ✅ Can be triggered from Electron app/daemon
- ✅ Works with any Cursor version

**Cons:**
- ⚠️ Requires macro script (AutoHotkey/AppleScript)
- ⚠️ Window focus dependent (Cursor must be visible)
- ⚠️ Less elegant than API approach

**Implementation:**
```typescript
// Extension Command Server adds new endpoint:
POST /cursor/chat/send
{
  "message": "Hello from Electron app!",
  "waitForResponse": false  // Optional: wait for AI response
}
```

**Macro Script (AutoHotkey example):**
```autohotkey
; Send message to Cursor chat
SendCursorChat(message) {
    ; Focus Cursor window (if not focused)
    WinActivate, ahk_class Chrome_WidgetWin_1
    
    ; Open chat (Ctrl+L or whatever shortcut Cursor uses)
    Send, ^l
    
    ; Wait for chat input to be ready
    Sleep, 200
    
    ; Type the message
    SendRaw, %message%
    
    ; Send (Enter)
    Send, {Enter}
}
```

---

### **Option 2: Extension Command Enhancement**

**How it works:**
- Add new VS Code command: `cursor.chat.sendMessage`
- Extension uses VS Code API to interact with chat
- Electron app calls this via Command Server

**Pros:**
- ✅ More elegant than macros
- ✅ Doesn't require window focus
- ✅ Can work in background

**Cons:**
- ❌ Requires Cursor to expose chat API (may not exist)
- ❌ May require reverse engineering Cursor's internal APIs
- ❌ Could break with Cursor updates

**Implementation:**
```typescript
// Extension adds command:
vscode.commands.registerCommand('cursor.chat.sendMessage', async (message: string) => {
  // Try to find Cursor's chat API
  // This would require investigating Cursor's internals
  // May not be possible without Cursor's cooperation
});
```

---

### **Option 3: Hybrid - Extension + Macro Bridge**

**How it works:**
- Extension Command Server receives request
- Extension checks if Cursor chat API exists
- If API exists → Use API (Option 2)
- If API doesn't exist → Fall back to macro (Option 1)

**Pros:**
- ✅ Best of both worlds
- ✅ Future-proof (switches to API if available)
- ✅ Works now with macro fallback

**Cons:**
- ⚠️ More complex implementation
- ⚠️ Requires macro script maintenance

---

## 🚀 **RECOMMENDED APPROACH**

**Start with Option 1 (Macro)**, then evolve to Option 3 (Hybrid):

### **Phase 1: Macro System (Now)**
1. Add `/cursor/chat/send` endpoint to Extension Command Server
2. Create AutoHotkey script wrapper
3. Extension calls macro script when endpoint is hit
4. Electron app can call: `POST http://localhost:5001/cursor/chat/send`

### **Phase 2: API Detection (Later)**
1. Research Cursor's internal chat APIs
2. If API found → Use it
3. If not → Continue using macro

---

## 📋 **IMPLEMENTATION PLAN**

### **Step 1: Extension Command Server Enhancement**

**File:** `cursor-addon/src/commandServer.ts`

**Add endpoint:**
```typescript
// POST /cursor/chat/send
private async handleSendChatMessage(request: {
    message: string;
    waitForResponse?: boolean;
}): Promise<any> {
    // Validate message
    if (!request.message || typeof request.message !== 'string') {
        return {
            success: false,
            error: 'Message is required'
        };
    }

    // Execute macro script
    const result = await this.executeChatMacro(request.message);
    
    return {
        success: true,
        message: request.message,
        sent: true
    };
}

private async executeChatMacro(message: string): Promise<void> {
    // Platform-specific macro execution
    const platform = process.platform;
    
    if (platform === 'win32') {
        // Windows: Use AutoHotkey or PowerShell
        return this.executeWindowsMacro(message);
    } else if (platform === 'darwin') {
        // macOS: Use AppleScript
        return this.executeMacMacro(message);
    } else {
        // Linux: Use xdotool or similar
        return this.executeLinuxMacro(message);
    }
}
```

### **Step 2: Windows Macro Script**

**File:** `cursor-addon/scripts/send-cursor-chat.ahk` (AutoHotkey)

```autohotkey
; Send message to Cursor chat
; Usage: AutoHotkey.exe send-cursor-chat.ahk "Your message here"

message := A_Args[1]

if (message = "") {
    ExitApp, 1
}

; Focus Cursor window
WinActivate, ahk_class Chrome_WidgetWin_1
Sleep, 300

; Open chat (Ctrl+L is Cursor's default chat shortcut)
Send, ^l
Sleep, 500

; Type message
SendRaw, %message%

; Send (Enter)
Sleep, 100
Send, {Enter}

ExitApp, 0
```

**PowerShell Alternative (no AutoHotkey needed):**
```powershell
# send-cursor-chat.ps1
param([string]$message)

Add-Type -AssemblyName System.Windows.Forms

# Focus Cursor window
$cursor = Get-Process | Where-Object {$_.MainWindowTitle -like "*Cursor*"}
if ($cursor) {
    [System.Windows.Forms.SendKeys]::SendWait("^l")  # Ctrl+L
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait($message)
    Start-Sleep -Milliseconds 100
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
}
```

### **Step 3: Electron App Integration**

**File:** `packages/ide_chat_app/src/services/cursorApi.ts`

**Add method:**
```typescript
async sendChatMessage(message: string): Promise<boolean> {
    const response = await fetch(`${this.baseUrl}/cursor/chat/send`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    });
    
    const result = await response.json();
    return result.success === true;
}
```

### **Step 4: Daemon Integration**

**File:** Python daemon can call Extension Command Server:

```python
import requests

def send_cursor_chat(message: str):
    """Send message to Cursor chat via Extension Command Server"""
    response = requests.post(
        'http://localhost:5001/cursor/chat/send',
        json={'message': message}
    )
    return response.json().get('success', False)
```

---

## 🎮 **MACRO ADVANTAGES (Your Experience)**

Since you've built complex macros before (RuneScape boss automation), you know:

1. **Reliability** - Macros can be very reliable with proper error handling
2. **Timing** - Sleep/wait commands ensure UI is ready
3. **Robustness** - Can handle edge cases (window not focused, etc.)
4. **Debugging** - Easy to test and debug macro scripts

**Your macro expertise makes Option 1 very viable!**

---

## 🔧 **MACRO REFINEMENTS**

### **Better Window Detection:**
```autohotkey
; More robust window finding
WinGet, cursorWindow, ID, ahk_exe Cursor.exe
if (!cursorWindow) {
    ExitApp, 1  ; Cursor not running
}
WinActivate, ahk_id %cursorWindow%
```

### **Error Handling:**
```autohotkey
; Check if chat input is actually focused
ControlGetFocus, focusedControl, ahk_class Chrome_WidgetWin_1
if (focusedControl != "ChatInput") {
    ; Retry focus
    Send, ^l
    Sleep, 500
}
```

### **Wait for Response (Optional):**
```autohotkey
; After sending, wait for AI response indicator
; Look for "thinking" indicator or message count increase
; This requires parsing Cursor's UI structure
```

---

## 📊 **ARCHITECTURE DIAGRAM**

```
Electron App
    ↓ HTTP POST
Extension Command Server (localhost:5001)
    ↓ /cursor/chat/send
Extension executes macro script
    ↓ AutoHotkey/PowerShell/AppleScript
Keyboard/Mouse simulation
    ↓ Focus + Type + Send
Cursor Chat Input
    ↓ Message sent
Cursor AI processes message
```

---

## ✅ **NEXT STEPS**

1. **Would you like me to implement Option 1 (Macro) now?**
   - Add endpoint to Command Server
   - Create macro script wrapper
   - Test with Electron app

2. **Or research Option 2 (API) first?**
   - Investigate Cursor's internal APIs
   - See if chat API exists
   - Then decide which approach

3. **Or start with Option 3 (Hybrid)?**
   - Build macro system
   - Add API detection
   - Fallback gracefully

**What's your preference?** Given your macro experience, Option 1 seems most practical for immediate implementation! 🚀

