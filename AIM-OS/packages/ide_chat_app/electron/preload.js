const { contextBridge, ipcRenderer } = require('electron');

// Expose AIM-OS API bridge to renderer process
contextBridge.exposeInMainWorld('aimosAPI', {
  // Proxy requests to AIM-OS daemon (localhost:5000)
  request: async (method, endpoint, data) => {
    return await ipcRenderer.invoke('aimos-api', { method, endpoint, data });
  },
  
  // Helper methods
  get: async (endpoint) => {
    return await ipcRenderer.invoke('aimos-api', { method: 'GET', endpoint });
  },
  
  post: async (endpoint, data) => {
    return await ipcRenderer.invoke('aimos-api', { method: 'POST', endpoint, data });
  }
});

// ✅ CAPTURE RENDERER CONSOLE - Send to main process for logging
const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;
const originalInfo = console.info;

// ✅ FIXED: Properly serialize args to avoid spread syntax errors
const serializeArgs = (...args) => {
  try {
    return args.map(arg => {
      if (typeof arg === 'object' && arg !== null) {
        try {
          return JSON.stringify(arg);
        } catch {
          return String(arg);
        }
      }
      return String(arg);
    }).join(' ');
  } catch (error) {
    return String(args);
  }
};

console.log = (...args) => {
  const message = serializeArgs(...args);
  ipcRenderer.invoke('electron-console-log', { level: 'log', message }).catch(() => {
    // Silently fail if IPC not available
  });
  originalLog(...args);
};

console.error = (...args) => {
  const message = serializeArgs(...args);
  ipcRenderer.invoke('electron-console-log', { level: 'error', message }).catch(() => {
    // Silently fail if IPC not available
  });
  originalError(...args);
};

console.warn = (...args) => {
  const message = serializeArgs(...args);
  ipcRenderer.invoke('electron-console-log', { level: 'warn', message }).catch(() => {
    // Silently fail if IPC not available
  });
  originalWarn(...args);
};

console.info = (...args) => {
  const message = serializeArgs(...args);
  ipcRenderer.invoke('electron-console-log', { level: 'info', message }).catch(() => {
    // Silently fail if IPC not available
  });
  originalInfo(...args);
};

// ✅ Window controls API (for borderless window)
contextBridge.exposeInMainWorld('windowControls', {
  minimize: () => ipcRenderer.invoke('window-minimize'),
  maximize: () => ipcRenderer.invoke('window-maximize'),
  close: () => ipcRenderer.invoke('window-close'),
  isMaximized: () => ipcRenderer.invoke('window-is-maximized'),
  onMaximizeChange: (callback) => {
    ipcRenderer.on('window-maximize-changed', (event, isMaximized) => {
      callback(isMaximized);
    });
  }
});

// ✅ Log reading API (for dev tools)
contextBridge.exposeInMainWorld('logAPI', {
  readLogs: (options) => ipcRenderer.invoke('read-logs', options)
});

// ✅ System tools API (for system monitoring)
contextBridge.exposeInMainWorld('systemAPI', {
  getProcesses: () => ipcRenderer.invoke('system-get-processes'),
  getPorts: () => ipcRenderer.invoke('system-get-ports'),
  getSystemInfo: () => ipcRenderer.invoke('system-get-info'),
  killProcess: (pid) => ipcRenderer.invoke('system-kill-process', { pid }),
  closePort: (port) => ipcRenderer.invoke('system-close-port', { port }),
  getTerminals: () => ipcRenderer.invoke('system-get-terminals')
});

// Log that preload is loaded
// ✅ Template capture API
contextBridge.exposeInMainWorld('electronAPI', {
  invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
  on: (channel, callback) => {
    ipcRenderer.on(channel, callback)
  },
  removeListener: (channel, callback) => {
    ipcRenderer.removeListener(channel, callback)
  }
});

// ✅ Listen for capture result and forward to renderer
ipcRenderer.on('capture:result', (event, data) => {
  // Dispatch custom event to renderer
  window.dispatchEvent(new CustomEvent('capture-result', { detail: data }))
});

console.log('✅ AIM-OS Electron preload script loaded');

