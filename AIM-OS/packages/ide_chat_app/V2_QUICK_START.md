# V2 Quick Start Guide
## AIM-OS IDE - One-Click Launch

**Last Updated:** 2025-11-08  
**Status:** ✅ Ready to Use  
**Version:** V2 Development Complete

---

## 🚀 **Quick Start**

### **One-Click Launch**

Simply run the launcher for your platform:

**Windows:**
```bash
cd packages/ide_chat_app
LAUNCH.bat
```

**Linux/Mac:**
```bash
cd packages/ide_chat_app
./LAUNCH.sh
```

**PowerShell:**
```powershell
cd packages/ide_chat_app
.\LAUNCH.ps1
```

**Cross-Platform (Node.js):**
```bash
cd packages/ide_chat_app
node LAUNCH.js
```

---

## ✨ **Features**

### **Automatic Port Detection**
- Finds first available port starting from 5173
- Checks ports 5173-6000
- No manual port configuration needed

### **Dependency Management**
- Automatically installs npm packages if needed
- Checks for node_modules before starting
- Handles installation errors gracefully

### **Auto-Open Browser**
- Opens IDE automatically when ready
- Shows connection URL in console
- Ready to use immediately

---

## 📋 **What Gets Launched**

The launcher starts the Vite dev server with:
- **Hot Module Replacement (HMR)** - Instant updates
- **TypeScript compilation** - Full type checking
- **React Fast Refresh** - Component state preservation
- **Source maps** - Easy debugging

---

## 🎯 **V2 Features Available**

### **Foundation (Week 1)**
- ✅ Panel Registry System
- ✅ Panel State Management
- ✅ MCP Tools Service (59 tools)
- ✅ Debug Console
- ✅ Comprehensive AIM-OS Hooks
- ✅ Real-Time Updates

### **Customization (Week 2)**
- ✅ Drag-Drop Panels
- ✅ Panel Resizing
- ✅ Panel Grouping (tabs, accordion, stack)
- ✅ Layout Persistence

### **Integration (Week 3)**
- ✅ Performance Monitoring
- ✅ Error Tracking
- ✅ Consciousness Awareness
- ✅ Advanced Visualizations

### **Revolutionary UX (Week 4 Preview)**
- ✅ Context Web Visualization
- ✅ Evolution Explorer
- ✅ Enhanced Evidence Trails
- ✅ Multi-Agent Coordination

---

## 🔧 **Troubleshooting**

### **Port Already in Use**
If you see "port already in use" errors:
- The launcher will automatically try the next port
- Or manually stop the process using that port
- Or specify a port: `npm run dev -- --port 3000`

### **Dependencies Not Installing**
If npm install fails:
- Check Node.js version (requires Node 18+)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and package-lock.json, then retry

### **Browser Not Opening**
- Check firewall settings
- Manually navigate to the URL shown in console
- Default: `http://localhost:5173` (or next available port)

---

## 📊 **System Requirements**

- **Node.js:** 18.0.0 or higher
- **npm:** 9.0.0 or higher
- **OS:** Windows 10+, macOS 10.15+, or Linux
- **Browser:** Chrome, Firefox, Edge, or Safari (latest)

---

## 🎉 **Status**

**V2 Development:** ✅ 96% Complete  
**All Weeks:** ✅ 100% Complete  
**Ready for:** ✅ Testing & Refinement

---

## 📚 **Documentation**

- `LAUNCH_README.md` - Detailed launcher documentation
- `V2_PROGRESS_COMPREHENSIVE.md` - Complete progress tracking
- `V2_FINAL_SUMMARY.md` - Final development summary
- `WEEK4_PREVIEW_SUMMARY.md` - Week 4 preview details

---

**Happy Coding!** 💙✨

