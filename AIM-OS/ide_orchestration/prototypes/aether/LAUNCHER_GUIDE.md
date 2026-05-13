# Aether IDE Prototype - Launcher Guide

**Created:** 2025-11-07  
**Purpose:** One-click launcher for Aether IDE Prototype  
**Status:** ✅ Ready  

---

## 🚀 **QUICK START**

### **Windows (Command Prompt):**
1. Double-click `launch.bat`
2. Browser opens automatically at `http://localhost:5173`

### **Windows (PowerShell):**
1. Right-click `launch.ps1` → "Run with PowerShell"
2. Browser opens automatically at `http://localhost:5173`

### **Mac/Linux:**
1. Make executable: `chmod +x launch.sh`
2. Run: `./launch.sh`
3. Browser opens automatically at `http://localhost:5173`

---

## 📋 **WHAT THE LAUNCHER DOES**

1. **Checks Dependencies** - Verifies `node_modules` exists
2. **Installs if Needed** - Runs `npm install` if dependencies missing
3. **Starts Dev Server** - Runs `npm run dev`
4. **Opens Browser** - Automatically opens at `http://localhost:5173`

---

## 🛠️ **MANUAL LAUNCH**

If launcher doesn't work, run manually:

```bash
# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

---

## 🌐 **ACCESS**

- **Local:** `http://localhost:5173`
- **Network:** `http://[your-ip]:5173` (for screenshots/sharing)

---

## ⚙️ **CONFIGURATION**

The launcher uses Vite configuration (`vite.config.ts`):
- Port: `5173`
- Auto-open: `true`
- Host: `true` (allows external access)

---

## 🐛 **TROUBLESHOOTING**

### **Port Already in Use:**
- Change port in `vite.config.ts`
- Or kill process using port 5173

### **Dependencies Fail:**
- Delete `node_modules` folder
- Delete `package-lock.json`
- Run `npm install` again

### **Browser Doesn't Open:**
- Manually navigate to `http://localhost:5173`

---

**Status:** ✅ Ready  
**One-Click Launch:** Yes! 🚀💙

