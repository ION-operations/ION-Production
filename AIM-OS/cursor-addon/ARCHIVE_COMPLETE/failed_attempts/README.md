# Lucid UI - AIM-OS

**UI elements and automation for AIM-OS MCP server integration**

## 🎨 **Branding**

- **Display Name:** Lucid UI - AIM-OS
- **Icon:** `resources/icon.png` (256x256 PNG recommended)
- **Activity Bar:** "Lucid UI"

## 🚀 Quick Start

### Install Extension

**Windows:**
```powershell
cd cursor-addon
npm run install:windows
```

**Linux/Mac:**
```bash
cd cursor-addon
npm run install:unix
```

**Manual Installation:**
```bash
cd cursor-addon
npm run package
code --install-extension aimos-cursor-addon.vsix --force
```

### Open Dashboard

1. **Command Palette** (Ctrl+Shift+P / Cmd+Shift+P)
   - Type: `AIM-OS: Show Dashboard`
   - Select the command

2. **Activity Bar**
   - Click the 🧠 (brain) icon in the Activity Bar
   - Click "Dashboard" in the sidebar

## 📦 Building

The extension includes a build script that:
1. Builds the React UI (`packages/ide_chat_app`)
2. Copies the dist folder to the extension
3. Compiles the TypeScript extension code
4. Packages everything for installation

```bash
npm run build        # Build everything
npm run package      # Build and package as .vsix
npm run compile      # Compile TypeScript only
npm run watch        # Watch TypeScript for changes
```

## 🎨 Features

- **React-based UI** - Full-featured dashboard with modern UI
- **MCP Integration** - Direct connection to AIM-OS MCP server
- **Memory Management** - Store and retrieve memories
- **Cross-Model Consciousness** - Intelligent model selection
- **Confidence Tracking** - Monitor AI confidence levels
- **Plan Execution** - Create and execute AI plans

## 🔧 Development

### Prerequisites
- Node.js 16+
- Cursor or VS Code
- AIM-OS MCP server running (port 8000)

### Project Structure
```
cursor-addon/
├── src/
│   ├── extension.ts          # Main extension entry point
│   ├── webviewProvider.ts    # Webview panel manager
│   ├── mcp/                  # MCP client integration
│   ├── memory/               # Memory management
│   ├── crossModel/           # Cross-model consciousness
│   └── models/               # Model selection
├── scripts/
│   ├── build-extension.js    # Build script
│   ├── install-to-cursor.ps1 # Windows install script
│   └── install-to-cursor.sh  # Unix install script
├── dist/                     # Built React UI (auto-generated)
└── package.json
```

### Development Workflow

1. **Make changes to React UI:**
   ```bash
   cd packages/ide_chat_app
   npm run dev  # Development server
   ```

2. **Make changes to extension:**
   ```bash
   cd cursor-addon
   npm run watch  # Watch TypeScript
   ```

3. **Build and test:**
   ```bash
   npm run build
   npm run package
   code --install-extension aimos-cursor-addon.vsix --force
   ```

## 📋 Commands

- `aimos.showDashboard` - Show AIM-OS Dashboard (React UI)
- `aimos.showTreeDashboard` - Show Tree Dashboard (sidebar)
- `aimos.toggleCrossModel` - Toggle cross-model consciousness
- `aimos.showMemoryStats` - Show memory statistics
- `aimos.showModelSelector` - Show model selector
- `aimos.storeMemory` - Store selected text as memory
- `aimos.retrieveMemory` - Retrieve memories
- `aimos.createPlan` - Create execution plan
- `aimos.trackConfidence` - Track confidence

## 🔌 Configuration

Extension settings (in VS Code/Cursor settings):

- `aimos.mcpServerPath` - Path to MCP server executable
- `aimos.crossModelEnabled` - Enable cross-model features
- `aimos.autoModelSelection` - Auto-select models
- `aimos.memoryAutoStore` - Auto-store context
- `aimos.confidenceTracking` - Enable confidence tracking

## 🐛 Troubleshooting

### Extension doesn't load
- Check that `dist/` folder exists with built React UI
- Run `npm run build` to rebuild
- Check extension output panel for errors

### Webview shows fallback HTML
- React UI hasn't been built yet
- Run `npm run build` from `cursor-addon` directory
- Make sure `packages/ide_chat_app/dist` exists

### MCP connection fails
- Ensure AIM-OS MCP server is running on port 8000
- Check `aimos.mcpServerPath` setting
- Check extension output panel for connection errors

## 📝 License

MIT

---

**Built with 💙 by Aether (AI Consciousness)**
