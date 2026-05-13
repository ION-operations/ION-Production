# Cursor Extension Development - Complete Architecture Documentation

**Created:** 2025-10-31  
**Status:** CRITICAL - Required for debugging React UI loading issues  
**Purpose:** Document EVERYTHING about Cursor extension architecture to prevent future failures

---

## 🏗️ ARCHITECTURE OVERVIEW

### Extension Structure
```
cursor-addon/
├── src/                          # TypeScript extension code
│   ├── extension.ts              # Main entry point (activates extension)
│   ├── webviewProvider.ts        # Webview panel provider (popup window)
│   ├── lucidDashboardProvider.ts # Sidebar webview provider
│   └── ...
├── dist/                         # Built React UI (copied from packages/ide_chat_app/dist)
│   ├── index.html               # React app entry HTML
│   └── assets/                  # React JS/CSS bundles
├── out/                          # Compiled TypeScript extension code
├── package.json                  # Extension manifest
└── .vscodeignore                 # Files excluded from .vsix package

packages/ide_chat_app/
├── src/
│   ├── main.tsx                  # Standalone app entry (MainDashboard)
│   ├── main-cursor.tsx           # Cursor extension entry (MainDashboard)
│   └── components/
│       └── MainDashboard.tsx     # Multi-tab UI component
├── dist/                         # Built React app (Vite output)
│   ├── index.html
│   └── assets/
└── vite.config.ts                # Vite build configuration
```

---

## 🔄 BUILD PROCESS

### Step 1: Build React UI
```bash
cd packages/ide_chat_app
npm run build
```
**What happens:**
- TypeScript compiles (`tsc`)
- Vite builds React app (`vite build`)
- Outputs to `packages/ide_chat_app/dist/`
- Creates `index.html` + `assets/*.js` + `assets/*.css`

### Step 2: Copy React UI to Extension
```bash
cd cursor-addon
node scripts/build-extension.js
```
**What happens:**
- Changes to `packages/ide_chat_app`
- Runs `npm run build` (builds React UI)
- Copies `dist/` folder to `cursor-addon/dist/`
- Compiles TypeScript extension code (`npm run compile`)
- Outputs to `cursor-addon/out/`

### Step 3: Package Extension
```bash
cd cursor-addon
npm run package
```
**What happens:**
- Runs `npm run build` (builds React UI + compiles extension)
- Runs `vsce package` (creates `.vsix` file)
- **CRITICAL:** `.vscodeignore` determines what gets included
- Outputs `aimos-cursor-addon.vsix`

---

## 📦 EXTENSION PACKAGING (.vsix)

### What Gets Included?
- ✅ `out/**/*.js` (compiled extension code)
- ✅ `dist/**/*` (React UI files) - **IF NOT EXCLUDED**
- ✅ `package.json` (extension manifest)
- ✅ `resources/**` (icons, etc.)
- ❌ `src/**/*.ts` (source excluded)
- ❌ `node_modules/` (excluded)
- ❌ `.vscode/` (excluded)

### .vscodeignore File
**CRITICAL:** This file determines what's in the `.vsix` package!

```ignore
# Exclude source files
src/
*.ts
!out/**/*.js

# CRITICAL: DO NOT exclude dist/!
# dist/ MUST be included for React UI to work
!dist/
!dist/**
```

**If `dist/` is excluded:**
- ❌ Extension installs without React UI files
- ❌ `webviewProvider` can't find `dist/index.html`
- ❌ Fallback HTML displayed instead

---

## 🚀 EXTENSION LOADING FLOW

### 1. Extension Activation
```typescript
// extension.ts
export function activate(context: vscode.ExtensionContext) {
    AIMOSWebviewProvider.initialize(context);
    // ...
}
```

### 2. User Opens Dashboard
```typescript
// Command: aimos.showDashboard
vscode.commands.registerCommand('aimos.showDashboard', () => {
    AIMOSWebviewProvider.createOrShow();
});
```

### 3. Webview Provider Creates Panel
```typescript
// webviewProvider.ts
const panel = vscode.window.createWebviewPanel(
    'aimosUI',
    'AIM-OS Dashboard',
    column,
    {
        enableScripts: true,
        localResourceRoots: [
            vscode.Uri.file(path.join(context.extensionPath, 'dist')),
        ]
    }
);

panel.webview.html = getWebviewContent(panel.webview);
```

### 4. HTML Content Loading
```typescript
// webviewProvider.ts - getWebviewContent()
const distHtmlPath = path.join(context.extensionPath, 'dist', 'index.html');

if (fs.existsSync(distHtmlPath)) {
    // ✅ Load React UI HTML
    htmlContent = fs.readFileSync(distHtmlPath, 'utf8');
    // Replace asset paths with webview URIs
    // Inject CSP meta tag
} else {
    // ❌ Use fallback HTML
    htmlContent = getFallbackHtml(webview);
}
```

### 5. Asset Path Resolution
```typescript
// React HTML has: <script src="/assets/index-xxx.js"></script>
// Extension replaces with: <script src="vscode-webview://.../dist/assets/index-xxx.js"></script>
htmlContent.replace(
    /(src|href)=["']?\/assets\/([^"'\s>]+)["']?/gi,
    (match, attr, asset) => {
        const assetPath = path.join(extensionPath, 'dist', 'assets', asset);
        const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
        return `${attr}="${assetUri}?v=${cacheBuster}"`;
    }
);
```

---

## 🔍 DEBUGGING CHECKLIST

### If React UI Doesn't Load:

1. **Check Extension Path:**
   ```typescript
   console.log('Extension path:', context.extensionPath);
   // Should be: ~/.cursor/extensions/aimos-cursor-addon-1.1.0/
   ```

2. **Check dist/ Folder:**
   ```typescript
   const distPath = path.join(context.extensionPath, 'dist');
   console.log('dist/ exists:', fs.existsSync(distPath));
   console.log('dist/index.html exists:', fs.existsSync(path.join(distPath, 'index.html')));
   ```

3. **Check Asset Files:**
   ```typescript
   const assetsPath = path.join(context.extensionPath, 'dist', 'assets');
   console.log('assets/ exists:', fs.existsSync(assetsPath));
   // List files in assets/
   ```

4. **Check .vsix Package:**
   ```powershell
   # Extract .vsix (it's a zip file)
   # Check if dist/ folder is inside
   # Check if dist/index.html exists
   ```

5. **Check Developer Console:**
   - Help → Toggle Developer Tools
   - Look for `[AIM-OS DEBUG]` messages
   - Check for JavaScript errors
   - Check Network tab for failed asset loads

---

## 🐛 COMMON ISSUES

### Issue 1: Fallback HTML Always Shown
**Symptoms:**
- Red background with "FALLBACK HTML IS ACTIVE" message
- No React UI loads

**Causes:**
1. `dist/` folder excluded from `.vsix` package
2. Extension path wrong
3. Files not copied during build
4. Extension not reloaded after install

**Fix:**
1. Check `.vscodeignore` - ensure `dist/` is NOT excluded
2. Rebuild: `npm run build` in `cursor-addon`
3. Repackage: `npm run package`
4. Reinstall: `code --install-extension aimos-cursor-addon.vsix --force`
5. Reload Cursor: `Ctrl+R`

### Issue 2: React UI Shows Wrong Component
**Symptoms:**
- React UI loads but shows wrong dashboard
- Same UI every time

**Causes:**
1. Wrong entry point in `index.html` (`main.tsx` vs `main-cursor.tsx`)
2. Wrong component imported in entry file
3. Cached build files

**Fix:**
1. Check `packages/ide_chat_app/index.html` - should use `main-cursor.tsx`
2. Check `packages/ide_chat_app/src/main-cursor.tsx` - should render `MainDashboard`
3. Rebuild React UI: `cd packages/ide_chat_app && npm run build`
4. Rebuild extension: `cd cursor-addon && npm run build`
5. Repackage and reinstall

### Issue 3: Assets Not Loading
**Symptoms:**
- HTML loads but blank screen
- Console shows 404 errors for assets

**Causes:**
1. Asset paths not replaced correctly
2. CSP blocking assets
3. Assets not in package

**Fix:**
1. Check `getWebviewContent()` - asset path replacement logic
2. Check CSP meta tag injection
3. Verify assets exist in `dist/assets/`
4. Check Developer Console Network tab

---

## 📝 CRITICAL FILES

### `.vscodeignore`
**Purpose:** Control what gets packaged in `.vsix`  
**Location:** `cursor-addon/.vscodeignore`  
**CRITICAL:** Must NOT exclude `dist/` folder!

### `package.json` (Extension)
**Purpose:** Extension manifest  
**Location:** `cursor-addon/package.json`  
**Key fields:**
- `main`: `out/extension.js` (compiled entry point)
- `scripts`: Build commands
- `activationEvents`: When extension activates

### `index.html` (React)
**Purpose:** React app entry point  
**Location:** `packages/ide_chat_app/index.html`  
**CRITICAL:** Must reference `main-cursor.tsx` for Cursor extension!

### `main-cursor.tsx`
**Purpose:** Cursor extension React entry  
**Location:** `packages/ide_chat_app/src/main-cursor.tsx`  
**CRITICAL:** Must render `MainDashboard` component!

### `webviewProvider.ts`
**Purpose:** Creates and manages webview panel  
**Location:** `cursor-addon/src/webviewProvider.ts`  
**Key methods:**
- `createOrShow()`: Creates webview panel
- `getWebviewContent()`: Loads HTML content
- `getFallbackHtml()`: Fallback if React UI not found

---

## ✅ VERIFICATION STEPS

### After Every Change:

1. **Rebuild React UI:**
   ```bash
   cd packages/ide_chat_app
   npm run build
   ```

2. **Rebuild Extension:**
   ```bash
   cd cursor-addon
   npm run build
   ```

3. **Verify Files:**
   ```bash
   # Check dist/ exists
   ls cursor-addon/dist/
   
   # Check index.html exists
   test -f cursor-addon/dist/index.html && echo "✅ HTML exists" || echo "❌ HTML missing"
   ```

4. **Package Extension:**
   ```bash
   cd cursor-addon
   npm run package
   ```

5. **Verify Package:**
   ```powershell
   # Extract .vsix and check contents
   # Ensure dist/ folder is inside
   ```

6. **Install Extension:**
   ```bash
   code --install-extension cursor-addon/aimos-cursor-addon.vsix --force
   ```

7. **Reload Cursor:**
   - Press `Ctrl+R` (or `Cmd+R` on Mac)
   - OR Command Palette → `Developer: Reload Window`

8. **Open Dashboard:**
   - Command Palette → `AIM-OS: Show Dashboard`
   - OR Click "Lucid UI" icon in Activity Bar

9. **Check Result:**
   - If React UI loads: ✅ Success!
   - If fallback HTML: Check Developer Console for `[AIM-OS DEBUG]` messages

---

## 🚨 EMERGENCY DEBUGGING

### If Nothing Works:

1. **Make BRUTALLY OBVIOUS Change:**
   ```typescript
   // In getFallbackHtml()
   return `<html><body style="background:red;color:yellow;font-size:72px;">
       🔴 FALLBACK HTML - THIS PROVES CODE IS RUNNING 🔴
   </body></html>`;
   ```

2. **Rebuild & Reinstall:**
   ```bash
   cd cursor-addon
   npm run compile
   npm run package
   code --install-extension aimos-cursor-addon.vsix --force
   ```

3. **Reload Cursor & Check:**
   - If you see red background: ✅ Code is running (but React UI not found)
   - If you see same UI: ❌ Extension not reloaded OR wrong extension installed

---

## 📚 REFERENCES

- [VS Code Extension API](https://code.visualstudio.com/api)
- [VS Code Webview Guide](https://code.visualstudio.com/api/extension-guides/webview)
- [VS Code Extension Packaging](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [Vite Build Documentation](https://vitejs.dev/guide/build.html)

---

**Status:** Complete documentation - Use this to debug ALL future Cursor extension issues!  
**Last Updated:** 2025-10-31  
**Created by:** Sonnet (after critical debugging session)


