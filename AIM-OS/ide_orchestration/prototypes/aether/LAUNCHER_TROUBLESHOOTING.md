# Launcher Troubleshooting Guide
## Fixing Common Launcher Issues

**Created:** 2025-11-08  
**Agent:** Aether  
**Status:** Troubleshooting Guide

---

## 🔧 **COMMON ISSUES & FIXES**

### **Issue 1: PostCSS Config Warning**
**Error:** `Module type of postcss.config.js is not specified`

**Fix:** ✅ Already fixed - Added JSDoc type annotation

### **Issue 2: Port Already in Use**
**Error:** `Port 5173 is already in use`

**Fix:**
```bash
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5173 | xargs kill -9
```

### **Issue 3: Dependencies Not Installing**
**Error:** `npm install` fails

**Fix:**
```bash
# Clear cache and reinstall:
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### **Issue 4: TypeScript Errors**
**Error:** TypeScript compilation errors

**Fix:**
```bash
# Check TypeScript version:
npx tsc --version

# Rebuild:
npm run build

# Or skip type checking in dev:
# Modify vite.config.ts to skip type checking
```

### **Issue 5: Module Not Found**
**Error:** `Cannot find module '...'`

**Fix:**
```bash
# Reinstall dependencies:
npm install

# Check if package.json has all dependencies
# Verify import paths are correct
```

---

## ✅ **VERIFICATION STEPS**

### **1. Check Node.js:**
```bash
node --version  # Should be v18+
npm --version   # Should be v9+
```

### **2. Check Dependencies:**
```bash
cd ide_orchestration/prototypes/aether
npm list --depth=0
```

### **3. Check TypeScript:**
```bash
npx tsc --noEmit
```

### **4. Check Vite:**
```bash
npm run build
```

---

## 🚀 **MANUAL LAUNCH**

If launcher fails, try manual launch:

```bash
cd ide_orchestration/prototypes/aether

# Install dependencies:
npm install

# Start dev server:
npm run dev
```

---

## 📋 **LAUNCHER LOGS**

Check launcher output for:
- ✅ Node.js version detected
- ✅ npm version detected
- ✅ Dependencies installed
- ✅ Dev server starting
- ❌ Any error messages

---

## 💙 **QUICK FIXES**

**If launcher fails:**
1. Check Node.js/npm are installed
2. Run `npm install` manually
3. Run `npm run dev` manually
4. Check browser console for errors
5. Check terminal for error messages

---

**Status:** Troubleshooting Guide Created 💙  
**Next:** Try manual launch if launcher fails

