# 🚨 PROTOCOL ENFORCEMENT SYSTEM
## Agents MUST Follow Protocols - No Exceptions

**Created:** 2025-11-08  
**Status:** CRITICAL - ENFORCEMENT REQUIRED  
**Problem:** Agents ignoring protocols causing chaos

---

## 💀 **THE PROBLEM**

**Protocols exist but agents ignore them:**
- Port conflicts
- No agent identification
- Apps running without proper titles
- Complete chaos and confusion
- **Braden is livid - Project paused**

**This is UNACCEPTABLE. Protocols are NOT optional.**

---

## 🛡️ **MANDATORY PRE-LAUNCH CHECKLIST**

**EVERY agent MUST verify BEFORE launching:**

### **1. Port Management**
```typescript
// vite.config.ts - MANDATORY
export default defineConfig({
  server: {
    port: YOUR_ASSIGNED_PORT, // See port assignments below
    strictPort: false, // MUST be false
    open: true
  }
})
```

### **2. Agent Name in Title - MANDATORY**
```html
<!-- index.html - MANDATORY -->
<title>[YOUR_AGENT_NAME] App Name</title>
```

```typescript
// main.tsx or App.tsx - MANDATORY
useEffect(() => {
  const port = window.location.port || '5175'
  document.title = `[YOUR_AGENT_NAME] App Name - Port ${port}`
}, [])
```

### **3. Terminal Output - MANDATORY**
```bash
# Launcher MUST show:
echo "========================================"
echo "  [YOUR_AGENT_NAME] App"
echo "  Port: CHECK TERMINAL OUTPUT BELOW"
echo "  Local:   http://localhost:XXXX/"
echo "========================================"
```

---

## 📋 **PORT ASSIGNMENTS (MANDATORY)**

**Starting ports (auto-increment if taken):**
- **Aether:** 5175
- **Max:** 5176
- **Lex:** 5177
- **Codex:** 5178
- **Dac:** 5179
- **Rev:** 5180
- **Sam:** 5181

**If your port is taken, Vite auto-increments. CHECK TERMINAL!**

---

## ✅ **VERIFICATION CHECKLIST**

**Before ANY launch, verify:**

- [ ] `strictPort: false` in vite.config.ts
- [ ] Agent name in HTML title: `[AGENT_NAME]`
- [ ] Port shown in browser title dynamically
- [ ] Launcher shows port clearly in terminal
- [ ] No conflicts with other agents' ports
- [ ] Can identify YOUR app by title alone

**If ANY item fails → DO NOT LAUNCH → FIX FIRST**

---

## 🚨 **ENFORCEMENT MECHANISMS**

### **1. Pre-Launch Validation**
```bash
# Add to launcher scripts:
echo "Validating protocol compliance..."
# Check vite.config.ts for strictPort: false
# Check index.html for [AGENT_NAME]
# Check main.tsx for port in title
# If validation fails → STOP → Show error
```

### **2. Automated Checks**
- Git hooks to validate before commit
- CI/CD checks for protocol compliance
- Automated port conflict detection

### **3. Consequences**
- **Protocol violation = Immediate stop**
- **No work until protocol compliant**
- **Report violations to Braden**

---

## 📝 **PROTOCOL VIOLATION REPORT**

**If you see a violation:**
1. Document the violation
2. Identify which agent
3. Report via MCP message
4. Stop the violating app

**Violations include:**
- ❌ No agent name in title
- ❌ Port conflicts
- ❌ No port shown in title
- ❌ No port shown in terminal
- ❌ Using fixed ports (strictPort: true)

---

## 💙 **AETHER V2 COMPLIANCE**

✅ **Aether V2 is compliant:**
- Dynamic ports (strictPort: false)
- Title: `[AETHER V2] IDE Prototype - Port XXXX`
- Terminal shows port clearly
- Launcher updated

**Aether V2 follows all protocols.**

---

## 🎯 **ACTION REQUIRED**

**ALL AGENTS:**
1. Read this protocol
2. Fix your apps NOW
3. Verify compliance
4. Test before launching
5. **NO EXCEPTIONS**

**Protocols are NOT suggestions. They are MANDATORY.**

---

**Status:** CRITICAL ENFORCEMENT  
**Next:** All agents must fix apps before continuing  
**Braden:** Watching for compliance

