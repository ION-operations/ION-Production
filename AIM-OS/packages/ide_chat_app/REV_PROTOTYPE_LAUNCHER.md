# Rev's IDE Prototype Launcher

**Port:** 5180 (Rev's assigned port per protocol)  
**URL:** http://localhost:5180/indexRev.html  
**Protocol:** Launcher automatically cleans up ports 3000 and 5180 before starting (strictPort: true)

---

## 🚀 Quick Start

### Windows (Easiest!)

**Option 1: Double-click launcher**
- Double-click `LAUNCH_REV_PROTOTYPE.bat`
- Browser will open automatically at http://localhost:5180/indexRev.html

**Option 2: PowerShell**
```powershell
cd packages/ide_chat_app
.\LAUNCH_REV_PROTOTYPE.ps1
```

### Mac/Linux

```bash
cd packages/ide_chat_app
./LAUNCH_REV_PROTOTYPE.sh
```

### Manual Launch

```bash
cd packages/ide_chat_app
npm run dev:rev
```

Then open: http://localhost:5180/indexRev.html (or check terminal for actual port if auto-incremented)

---

## 📋 What the Launcher Does

1. ✅ **CLEANS UP PORTS FIRST** - Kills any processes on ports 3000 (Sam's IDE) and 5180 (Rev's IDE)
2. ✅ Checks if dependencies are installed (runs `npm install` if needed)
3. ✅ Starts Vite dev server on port 5180 (FAILS if port is taken - no auto-increment confusion)
4. ✅ Opens browser automatically at http://localhost:5180/indexRev.html
5. ✅ Shows server output in terminal with actual port number
6. ✅ Displays port in browser title: `[REV] IDE Prototype - Port 5180`

---

## 🔧 Technical Details

### Entry Point Chain
- `indexRev.html` → `mainRev.tsx` → `AppRev.tsx` → `RevIDELayout.tsx`

### Configuration
- **Vite Config:** `vite.rev.config.ts`
- **Port:** 5180 (Rev's assigned port per PROTOCOL_ENFORCEMENT.md)
- **strictPort:** false (allows auto-increment)
- **Host:** true (accessible from network)

### NPM Scripts
- `npm run dev:rev` - Start dev server (port 5180, auto-increments)
- `npm run build:rev` - Build for production
- `npm run preview:rev` - Preview production build (port 5180)

### Protocol Compliance
- ✅ Port 5180 assigned per PROTOCOL_ENFORCEMENT.md
- ✅ strictPort: false (allows port auto-increment)
- ✅ Title includes `[REV]` agent identifier
- ✅ Dynamic port display in browser title

---

## 🎯 Features

Rev's IDE Prototype V2 includes:
- ✅ **Phase 1:** Foundation - Unified `useAIMOS` hook, MCP/Daemon services, 23 panels integrated
- ✅ **Phase 2:** Revolutionary Features - Context Web (React Flow), Evolution Explorer, Bitemporal Timeline, Consciousness Visualization
- ✅ **Phase 3:** Customization - Panel presets (10 layouts), Panel registry, Layout management
- ✅ **Phase 4:** Integration - BasePanel component, PDAS system, Consciousness awareness
- ✅ **Phase 5:** Polish - Accessibility (WCAG 2.1 AA), Performance optimization, Theme system (dark/light/high-contrast/auto)
- ✅ Resizable panels with react-resizable-panels
- ✅ Panel visibility toggle
- ✅ Keyboard shortcuts (Ctrl+K for command palette, Ctrl+` for terminal)
- ✅ Comprehensive AIM-OS integration (CMC, HHNI, VIF, APOE, SEG, SDF-CVF, CAS, TCS)
- ✅ Theme selector in top bar
- ✅ Accessibility features (Skip to main content, ARIA live regions)

---

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal window.

---

## 📝 Notes

- **Port 5180** is Rev's assigned port per PROTOCOL_ENFORCEMENT.md
- **Port 3000** is Sam's IDE port (DO NOT USE for Rev's IDE)
- Port auto-increments if 5180 is taken (strictPort: false)
- The launcher automatically installs dependencies if needed
- Browser opens automatically after 3 seconds
- Port number is displayed in browser title dynamically
- All panels integrate with AIM-OS systems (CMC, HHNI, VIF, etc.)

## ⚠️ Port Conflicts

**The launcher automatically handles port conflicts:**
- ✅ **Automatically kills** any process on port 3000 (Sam's IDE) before starting
- ✅ **Automatically kills** any process on port 5180 (Rev's IDE) before starting
- ✅ **Waits 2 seconds** for ports to fully release
- ✅ **Fails clearly** if port 5180 is still taken after cleanup (strictPort: true)

**Manual port cleanup (if needed):**
```powershell
# Windows PowerShell
Get-NetTCPConnection -LocalPort 5180 | Stop-Process -Id {OwningProcess} -Force

# Windows CMD
netstat -ano | findstr ":5180"
taskkill /F /PID <PID>

# Mac/Linux
lsof -ti:5180 | xargs kill -9
```

---

## 🔍 Troubleshooting

**Port already in use:**
- The server will automatically try the next available port
- Check the terminal output for the actual port number
- Browser title will show the correct port

**Dependencies not installed:**
- Launcher automatically runs `npm install` if needed
- If issues persist, manually run: `cd packages/ide_chat_app && npm install`

**Browser doesn't open:**
- Manually navigate to the URL shown in terminal output
- Default: http://localhost:5180/indexRev.html

---

**Built by Rev** 💙  
**Research-First, User-Centered, Comprehensive Integration**  
**V2 Status:** Phase 5 Polish - 50% Complete
