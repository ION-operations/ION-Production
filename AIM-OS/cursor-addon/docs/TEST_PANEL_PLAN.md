# Test Panel Implementation Plan
## Progressive Testing Strategy for UI Panel Issue

---

## 🎯 OBJECTIVE

Isolate the root cause of the blank dashboard through systematic, progressive testing.

---

## 📋 TEST PROGRESSION

### Test 1: Simple HTML (simpleTestProvider.ts) ✅ CREATED
**Purpose:** Verify basic webview mechanism works
**What it tests:**
- Can webview display HTML?
- Can inline styles work?
- Can inline JavaScript execute?
- Can buttons trigger events?

**Expected Result:**
- Shows "✅ WEBVIEW IS WORKING!" heading
- Green border appears (JavaScript executed)
- Button click shows alert

**Files:**
- `src/simpleTestProvider.ts` - Simple HTML provider
- Modified `src/extension.ts` - Registered provider
- Modified `package.json` - Added view definition

### Test 2: External Script Loading (Next)
**Purpose:** Verify external scripts can load
**What to test:**
- Can load script from webview URI?
- Do asset paths resolve correctly?
- Does CSP allow execution?

### Test 3: React Mounting (After Test 2)
**Purpose:** Verify React can mount
**What to test:**
- Does React mount to #root?
- Do React components render?
- Can state updates work?

---

## 🔧 HOW TO TEST

### Build & Install
```bash
cd cursor-addon
npm run build
npm run package
code --install-extension aimos-cursor-addon.vsix --force
```

### Reload Cursor
```
Ctrl+Shift+P → Developer: Reload Window
```

### Find Test Panel
1. Look at bottom panel (where Terminal is)
2. Should see tabs: Terminal | Output | Lucid Orchestrator
3. Should now also see: **Test Panel** tab
4. Click "Test Panel"

### What to Check
1. **Does it show HTML?** → If yes, webview works
2. **Is border green?** → If yes, JavaScript works
3. **Does button work?** → If yes, events work
4. **Any console errors?** → Check Developer Tools

---

## 🐛 DEBUGGING

### If Test Panel Tab Missing
- Check activation: Extension installed?
- Check package.json: View defined?
- Check extension.ts: Provider registered?

### If Test Panel Blank
- Check Extension Host console for errors
- Check simpleTestProvider.ts loaded
- Try simpler HTML (just text)

### If JavaScript Not Working
- CSP issue - check meta tags
- TrustedTypes blocking - check console
- Script syntax error - validate JavaScript

---

## 📊 RESULTS TRACKING

| Test | Expected | Actual | Root Cause | Fix |
|------|----------|--------|------------|-----|
| Simple HTML | Shows heading | ? | ? | ? |
| Inline JS | Green border | ? | ? | ? |
| Button Click | Alert shown | ? | ? | ? |
| External Script | Loads & runs | ? | ? | ? |
| React Mount | Components render | ? | ? | ? |

---

## 💡 INSIGHTS SO FAR

### Confirmed Working
- Extension installs ✅
- Files present in package ✅
- Fallback HTML displays ✅

### Confirmed Broken
- React app not mounting ❌
- Scripts might not be loading ❌
- Unknown if JavaScript executes ❌

### Hypotheses
1. **Most Likely:** CSP/TrustedTypes blocking scripts
2. **Possible:** Asset URIs not resolving
3. **Less Likely:** React-specific issue

---

## 🎯 NEXT IMMEDIATE STEP

1. Build extension with test panel
2. Install and reload
3. Click "Test Panel" tab
4. Document what happens
5. Proceed based on results

**Time Estimate:** 10 minutes to first result

---
