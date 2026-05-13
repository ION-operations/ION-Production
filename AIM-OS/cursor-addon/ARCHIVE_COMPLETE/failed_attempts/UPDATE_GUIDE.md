# Extension Update & Reload Guide

## 🔄 **Auto-Updates During Development**

### **Short Answer:**
**You need to reload/reinstall when you make changes**, but there are shortcuts:

### **Quick Reload (Fastest)**
1. **Press `Ctrl+R` (Windows/Linux) or `Cmd+R` (Mac)** in Cursor
   - This reloads the extension without full restart
   - Works for most code changes (TypeScript, webview HTML)

2. **Command Palette Method:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
   - Type: `Developer: Reload Window`
   - Press Enter

### **Full Reinstall (For Major Changes)**
If reload doesn't work, rebuild and reinstall:
```bash
cd cursor-addon
npm run install
```

### **Development Mode (Hot Reload)**
For the React UI components, you can run the dev server separately:
```bash
cd packages/ide_chat_app
npm run dev
```

Then configure the webview to load from `http://localhost:5173` instead of bundled files. This gives you hot-reload for UI changes!

## 📦 **What Updates Automatically?**

### **✅ Hot Reloads (No Restart Needed):**
- TypeScript changes in `src/` (if using watch mode)
- Webview content (if loading from dev server)
- Configuration changes

### **🔄 Requires Reload:**
- Extension manifest (`package.json` changes)
- New commands registered
- New views/panels added
- Initial activation logic

### **🔧 Requires Reinstall:**
- New dependencies added
- Build process changes
- Extension ID changes

## 🚀 **Best Development Workflow**

1. **Run TypeScript in watch mode:**
   ```bash
   cd cursor-addon
   npm run watch
   ```

2. **Run React dev server (optional):**
   ```bash
   cd packages/ide_chat_app
   npm run dev
   ```

3. **Make changes** → Press `Ctrl+R` in Cursor → See updates!

4. **For major changes:** Run `npm run install` in `cursor-addon/`

## 📝 **Note About Published Extensions**

When published to VS Code Marketplace:
- ✅ **Auto-updates automatically** when new version published
- ✅ Users don't need to reinstall
- ✅ VS Code handles updates in background

For local development, use the reload/reinstall methods above! 💙

