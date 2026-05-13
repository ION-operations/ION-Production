# Cursor UI Panel Fix Plan - TrustedTypes & Module Scripts

**Created:** 2025-11-01  
**Agents:** Sonnet + Aether  
**Priority:** URGENT - 30+ failed attempts

---

## 🔍 **ROOT CAUSE ANALYSIS**

### **Critical Issues Identified:**

1. **TrustedScript/TrustedTypes Errors:**
   - VS Code 2.0/Cursor enforces strict TrustedTypes policy
   - Module scripts (`type="module"`) require special handling
   - CSP `'unsafe-inline' 'unsafe-eval'` may not be enough for module scripts

2. **Script Tag Regex May Not Match:**
   - `dist/index.html` has: `<script type="module" crossorigin src="./assets/main-5fYGI1t7.js"></script>`
   - Current regex: `/(src|href)=["']([^"']*assets\/[^"']+)["']/gi`
   - May not be matching because of `type="module"` and `crossorigin` attributes

3. **Module Scripts in Webviews:**
   - VS Code webviews require `webview.asWebviewUri()` for ALL script sources
   - Module scripts need explicit TrustedTypes policy bypass
   - May need to convert module scripts to regular scripts or use different approach

---

## ✅ **FIX STRATEGY**

### **Step 1: Fix Script Tag Regex (CRITICAL)**

**Problem:** Regex may not be matching module script tags correctly.

**Solution:** Update regex to handle:
- `type="module"` attribute
- `crossorigin` attribute
- `defer` and `async` attributes
- Both relative (`./assets/`) and absolute (`/assets/`) paths

**New Regex:**
```typescript
// Match script tags with src attribute (handles type="module", crossorigin, etc.)
htmlContent = htmlContent.replace(
    /<script([^>]*)\ssrc=["']([^"']*assets\/[^"']+)["']([^>]*)>/gi,
    (match, beforeSrc, assetPathRel, afterSrc) => {
        // Extract filename
        const assetFileName = assetPathRel.split('/').pop() || assetPathRel.split('\\').pop() || assetPathRel;
        const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', assetFileName);
        
        if (fs.existsSync(assetPath)) {
            const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
            // Reconstruct script tag with webview URI
            return `<script${beforeSrc} src="${assetUri}?v=${cacheBuster}"${afterSrc}>`;
        }
        return match;
    }
);
```

### **Step 2: Add TrustedTypes Policy Bypass**

**Problem:** VS Code/Cursor TrustedTypes blocking module script execution.

**Solution:** Add TrustedTypes policy to CSP and inject policy creation script:

```typescript
// Add TrustedTypes policy bypass BEFORE CSP meta tag
const trustedTypesScript = `
<script>
if (window.trustedTypes && window.trustedTypes.createPolicy) {
    window.trustedTypes.createPolicy('default', {
        createHTML: (string) => string,
        createScript: (string) => string,
        createScriptURL: (string) => string
    });
}
</script>
`;

// Insert TrustedTypes script BEFORE <head> tag
htmlContent = htmlContent.replace(/<head>/i, `<head>\n    ${trustedTypesScript}`);
```

### **Step 3: Update CSP for Module Scripts**

**Problem:** CSP may not allow module scripts even with `'unsafe-inline'`.

**Solution:** Add explicit `'module'` to script-src directive:

```typescript
const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src ${webview.cspSource} https:; script-src ${webview.cspSource} 'unsafe-inline' 'unsafe-eval' 'module' https:; style-src ${webview.cspSource} 'unsafe-inline' https:; img-src ${webview.cspSource} https: data:; font-src ${webview.cspSource} https: data:; connect-src ${webview.cspSource} https: ws: wss:;">`;
```

### **Step 4: Verify Asset Path Conversion**

**Problem:** Need to ensure ALL asset paths are converted correctly.

**Solution:** Add comprehensive logging and verification:

```typescript
// After all replacements, verify scripts are converted
const finalScriptTags = htmlContent.match(/<script[^>]*src=["']([^"']+)["'][^>]*>/gi);
if (finalScriptTags) {
    finalScriptTags.forEach((script, idx) => {
        const srcMatch = script.match(/src=["']([^"']+)["']/);
        if (srcMatch) {
            const src = srcMatch[1];
            if (!src.startsWith('vscode-webview://')) {
                console.error(`[AIM-OS DEBUG] ❌ Script ${idx + 1} NOT converted to webview URI: ${src}`);
            } else {
                console.log(`[AIM-OS DEBUG] ✅ Script ${idx + 1} converted: ${src.substring(0, 80)}...`);
            }
        }
    });
}
```

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Fix Script Tag Replacement (IMMEDIATE)**
1. Update regex to handle module scripts
2. Test regex matching against actual `dist/index.html`
3. Verify asset paths are converted to webview URIs

### **Phase 2: Add TrustedTypes Bypass (IMMEDIATE)**
1. Inject TrustedTypes policy creation script
2. Add to CSP meta tag
3. Test if TrustedScript errors disappear

### **Phase 3: Verify Module Script Loading (IMMEDIATE)**
1. Check browser console for module loading errors
2. Verify React mounts correctly
3. Test full UI functionality

### **Phase 4: Comprehensive Testing**
1. Test without restart (reload webview)
2. Test with extension reload
3. Test with full Cursor restart
4. Verify all tabs work (Agents, Chat, Chains, Tools, Timeline, NL Tags)

---

## 📋 **DEBUGGING CHECKLIST**

Before claiming fix:
- [ ] Script tags have `vscode-webview://` URIs
- [ ] No TrustedScript errors in console
- [ ] No TrustedTypes errors in console
- [ ] React root element mounts (`<div id="root">`)
- [ ] React components render (MainDashboard visible)
- [ ] All tabs functional
- [ ] No CSP violations in console
- [ ] Assets load correctly (CSS, fonts, images)

---

## 🎯 **SUCCESS CRITERIA**

**The fix is successful when:**
1. ✅ Dashboard panel shows React UI (not blank, not fallback HTML)
2. ✅ All tabs visible and functional (Agents, Chat, Chains, Tools, Timeline, NL Tags)
3. ✅ No console errors related to TrustedScript/TrustedTypes
4. ✅ Works WITHOUT requiring Cursor restart (webview reload sufficient)
5. ✅ Works consistently across multiple reloads

---

## 💡 **ALTERNATIVE APPROACHES**

If TrustedTypes continues to block:

1. **Convert Module Scripts to Regular Scripts:**
   - Remove `type="module"` from script tags
   - May require React build configuration changes

2. **Use Inline Scripts (Last Resort):**
   - Bundle React app into single inline script
   - Not ideal but would bypass TrustedTypes issues

3. **Webview API Updates:**
   - Check if newer VS Code API has TrustedTypes support
   - May need to update extension manifest

---

**Status:** Ready for implementation  
**Next:** Apply fixes to `lucidDashboardProvider.ts`  
**Agent:** Sonnet + Aether collaboration

