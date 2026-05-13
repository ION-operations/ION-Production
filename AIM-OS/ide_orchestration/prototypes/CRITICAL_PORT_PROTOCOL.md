# 🚨 CRITICAL PORT & IDENTIFICATION PROTOCOL
## MANDATORY FOR ALL AGENTS

**Created:** 2025-11-08  
**Status:** CRITICAL - IMMEDIATE ACTION REQUIRED  
**Braden:** Livid - Project Paused

---

## 🛑 **IMMEDIATE ACTIONS REQUIRED**

### **1. STOP ALL RUNNING SERVERS**
```bash
# Kill all node processes
# Windows:
taskkill /F /IM node.exe

# Linux/Mac:
pkill -9 node
```

### **2. FIX YOUR APP TITLES**
**MANDATORY:** Every app MUST have agent name in title:

```html
<!-- index.html -->
<title>[YOUR_AGENT_NAME] App Name - Port XXXX</title>
```

```typescript
// main.tsx or App.tsx
useEffect(() => {
  const port = window.location.port || '5175'
  document.title = `[YOUR_AGENT_NAME] App Name - Port ${port}`
}, [])
```

### **3. USE DYNAMIC PORTS**
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    port: 5175, // Start port
    strictPort: false, // AUTO-INCREMENT IF TAKEN
    open: true
  }
})
```

### **4. DISPLAY PORT IN TERMINAL**
```bash
# Launcher must show:
echo "========================================"
echo "  LOOK FOR THIS IN TERMINAL OUTPUT:"
echo "  Local:   http://localhost:XXXX/"
echo "  THAT IS YOUR PORT NUMBER!"
echo "========================================"
```

---

## 📋 **PORT ASSIGNMENT**

**Starting Ports (auto-increment if taken):**
- **Aether V2:** 5175
- **Max:** 5176
- **Lex:** 5177
- **Codex:** 5178
- **Dac:** 5179
- **Rev:** 5180
- **Sam:** 5181

**If your port is taken, Vite will auto-increment. CHECK TERMINAL OUTPUT!**

---

## ✅ **CHECKLIST FOR ALL AGENTS**

- [ ] Kill all running servers
- [ ] Add agent name to HTML title: `[AGENT_NAME]`
- [ ] Add port to browser title dynamically
- [ ] Set `strictPort: false` in vite.config.ts
- [ ] Update launcher to show port clearly
- [ ] Test: Can you identify YOUR app by title?
- [ ] Test: Can you see YOUR port in terminal?

---

## 🚨 **VERIFICATION**

**Before launching:**
1. Check what ports are in use: `netstat -ano | findstr "LISTENING"`
2. Kill conflicting processes
3. Launch your app
4. Verify title shows: `[YOUR_AGENT_NAME] App - Port XXXX`
5. Verify terminal shows port clearly

---

## 💙 **AETHER V2 STATUS**

✅ Fixed:
- Dynamic port selection (strictPort: false)
- Title: `[AETHER V2] IDE Prototype - Port XXXX`
- Terminal shows port clearly
- Launcher updated

**Aether V2 is ready and compliant.**

---

**ALL AGENTS: Fix your apps NOW. No exceptions. Braden is watching.**

