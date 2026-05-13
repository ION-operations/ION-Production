# 🔍 Research Findings - Blank Dashboard Issue

**Date:** 2025-11-01  
**Key Finding:** Vite builds module scripts (`type="module"`) which may not work in VS Code webviews

---

## ✅ **CONFIRMED: Webviews DO Work in Cursor**

**User Report:** "HTML worked before so webview seems to work"

This means:
- ✅ Webview mechanism works
- ✅ Extension registration works  
- ✅ Something changed in HOW we're loading scripts

---

## 🎯 **ROOT CAUSE HYPOTHESIS**

### **Vite Build Output = Module Scripts**

**Finding:** Vite builds output:
```html
<script type="module" crossorigin src="./assets/main-5fYGI1t7.js"></script>
```

**Problem:** VS Code/Cursor webviews have known issues with:
- `type="module"` scripts
- `crossorigin` attribute
- TrustedTypes enforcement
- CSP blocking module scripts

**Evidence:**
- Web search: Multiple reports of module scripts not loading in webviews
- User errors: "TrustedScript assignment" errors
- Our code: Vite config uses default module build

---

## 📋 **WHAT CHANGED?**

If HTML worked before, what changed?

**Possible Changes:**
1. **Vite version update** → Different build output?
2. **React build configuration** → Started using modules?
3. **Cursor update** → Stricter CSP/TrustedTypes?
4. **Extension API changes** → Different webview behavior?

**What We Know:**
- `vite.config.ts` uses `base: './'` (correct for webviews)
- Build outputs `type="module"` scripts (problematic)
- We have `crossorigin` attribute (may cause issues)

---

## 🔧 **SOLUTIONS TO RESEARCH**

### **Option 1: Non-Module Build**
- Configure Vite to build without `type="module"`
- Use regular script tags instead
- May require build config changes

### **Option 2: Bundle Everything**
- Build single JS file (no modules)
- Inline or bundle all dependencies
- Simpler but larger file

### **Option 3: TrustedTypes Bypass**
- Sonnet's fix (already in code)
- Create TrustedTypes policy
- Allow module scripts

### **Option 4: Different Build Target**
- Build for "webview" instead of "module"
- Use Vite's library mode?
- Custom rollup config?

---

## 🐛 **DEBUG COMMAND FIX**

**Issue:** Debug command not showing in Command Palette  
**Fix:** Added to `commandPalette` menu with `"when": "true"`  
**Status:** Fixed (needs rebuild)

---

## 📚 **ONLINE FINDINGS**

### **1. Cursor Webview Issues:**
- Some webview panels don't work (but user says HTML worked before)
- Webview developer tools no longer accessible
- Performance issues in Cursor v1.2

### **2. VS Code Module Script Issues:**
- Module scripts (`type="module"`) have CSP restrictions
- TrustedTypes blocks module scripts without policy
- `crossorigin` attribute can cause issues

### **3. Common Solutions:**
- Remove `type="module"` from build
- Use non-module build target
- Create TrustedTypes policy (Sonnet's approach)

---

## ✅ **NEXT STEPS**

1. **Fix Debug Command** (rebuild extension)
2. **Research Vite Non-Module Build** - How to build without modules?
3. **Test Sonnet's TrustedTypes Fix** - Does it work?
4. **Check Build Output** - What does dist/index.html actually contain?
5. **Compare Old vs New** - What changed in build?

---

**Status:** Researching Vite module build configuration  
**Priority:** Understand if we can build without `type="module"`

