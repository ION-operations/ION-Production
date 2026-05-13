# AIM-OS IDE Launcher - Quick Start

## One-Click Launch

Simply run the appropriate launcher for your platform:

### Windows
```bash
LAUNCH.bat
```
or
```powershell
.\LAUNCH.ps1
```

### Linux/Mac
```bash
./LAUNCH.sh
```

### Cross-Platform (Node.js)
```bash
node LAUNCH.js
```

## Features

✅ **Automatic Port Detection** - Finds an open port starting from 5173  
✅ **Dependency Check** - Installs npm packages if needed  
✅ **Auto-Open Browser** - Opens IDE automatically when ready  
✅ **Cross-Platform** - Works on Windows, Linux, and Mac  

## How It Works

1. Checks if dependencies are installed (installs if needed)
2. Finds the first available port starting from 5173
3. Launches Vite dev server on that port
4. Opens browser automatically

## Port Range

The launcher checks ports **5173-6000** for availability. If all ports are in use, it will show an error.

## Stopping the Server

Press **Ctrl+C** in the terminal to stop the dev server.

---

**Created:** 2025-11-08  
**Status:** ✅ Ready to use

