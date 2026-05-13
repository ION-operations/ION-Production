# Standalone AIM-OS Dashboard Panel Guide

**Purpose:** Test the AIM-OS Dashboard outside of Cursor in any browser to debug issues and verify functionality.

---

## 🚀 Quick Start

### Option 1: Quick Start Script (Easiest!)

**Windows:**
```powershell
cd packages/ide_chat_app
.\start-standalone.ps1
```

**Mac/Linux:**
```bash
cd packages/ide_chat_app
./start-standalone.sh
```

The script will:
- ✅ Auto-detect if you have a production build
- ✅ Start dev server (port 3000) if no build exists
- ✅ Start preview server (port 4173) if build exists
- ✅ Open dashboard automatically

### Option 2: Using Vite Dev Server (Development)

1. **Start the dev server:**
   ```bash
   cd packages/ide_chat_app
   npm run dev
   ```

2. **Open in browser:**
   - Navigate to: `http://localhost:3000`
   - The React UI will load automatically

3. **Test in different browsers:**
   - Chrome: `http://localhost:3000`
   - Firefox: `http://localhost:3000`
   - Edge: `http://localhost:3000`
   - Safari: `http://localhost:3000`

### Option 3: Using Vite Preview Server (Production Build)

1. **Build the React UI:**
   ```bash
   cd packages/ide_chat_app
   npm run build
   ```

2. **Start preview server:**
   ```bash
   npm run preview
   ```

3. **Open in browser:**
   - Navigate to: `http://localhost:4173`
   - The React UI will load automatically

### Option 4: Using Standalone HTTP Server (Alternative)

1. **Build the React UI:**
   ```bash
   cd packages/ide_chat_app
   npm run build
   ```

2. **Start the standalone server:**
   ```bash
   python standalone-server.py
   ```
   Or with custom port:
   ```bash
   python standalone-server.py --port 3002
   ```

3. **Open in browser:**
   - Navigate to: `http://localhost:3001/standalone.html`
   - Or: `http://localhost:3001` (will redirect to standalone.html)

---

## 🔧 Requirements

### For Vite Dev Server:
- Node.js installed
- Dependencies installed: `npm install`

### For Standalone Server:
- Python 3.6+ installed
- React UI built: `npm run build`

---

## 📋 Features Available

The standalone panel includes all dashboard features:

- ✅ **Agent Management Dashboard** - Manage Cursor AI agents
- ✅ **Chat Interface** - Multi-model chat (Gemini/Cerebras)
- ✅ **Prompt Chains** - Visualize prompt chains
- ✅ **MCP Tools** - View MCP tool call history
- ✅ **Timeline** - View timeline entries
- ✅ **NL Tags** - Natural language tag management

---

## 🐛 Debugging

### Check Browser Console

1. **Open Developer Tools:**
   - Chrome/Edge: `F12` or `Ctrl+Shift+I`
   - Firefox: `F12` or `Ctrl+Shift+I`
   - Safari: `Cmd+Option+I`

2. **Check Console Tab:**
   - Look for errors or warnings
   - Check if assets are loading correctly
   - Verify API connections

### Check Network Tab

1. **Open Network Tab in DevTools**
2. **Reload the page** (`F5` or `Ctrl+R`)
3. **Check asset loading:**
   - Look for failed requests (red)
   - Verify JavaScript/CSS files load
   - Check API endpoint responses

### Common Issues

**Issue: "Failed to load module"**
- **Solution:** Make sure you're accessing via HTTP (not file://)
- Use `http://localhost:3000` or `http://localhost:3001`

**Issue: "CORS error"**
- **Solution:** The standalone server includes CORS headers
- If using Vite dev server, CORS is handled automatically

**Issue: "Assets not loading"**
- **Solution:** Check that build completed successfully
- Verify `dist/assets/` directory exists with JS/CSS files

**Issue: "API not connecting"**
- **Solution:** Check that AIM-OS backend services are running
- MCP server should be on port 8000
- Daemon should be on port 5000

---

## 🔄 Comparing Cursor vs Standalone

### Cursor Extension
- Uses VS Code webview API
- Requires extension installation
- Loads via `lucidDashboardProvider.ts`
- May have webview-specific issues

### Standalone Panel
- Standard browser environment
- No extension required
- Direct HTTP access
- Better for debugging

### Differences to Watch For:
- **Asset loading:** Cursor uses `webview.asWebviewUri()`, standalone uses direct paths
- **API connections:** Both should work the same
- **Styling:** Should be identical in both

---

## 📝 Notes

- The standalone panel uses the same React components as the Cursor extension
- All service layer code (`AIMOSService.ts`) works the same way
- API endpoints are identical in both environments
- This is perfect for testing if issues are Cursor-specific or general React UI issues

---

## 🚀 Next Steps

1. **Test in different browsers** to find compatibility issues
2. **Compare behavior** between Cursor and standalone
3. **Debug issues** using browser DevTools
4. **Report findings** back to team

---

**Created:** 2025-01-27  
**Purpose:** Debug Cursor extension UI issues by testing in standard browser

