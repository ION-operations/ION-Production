const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const http = require('http');
const https = require('https');
const { URL } = require('url');
const os = require('os');
const { promisify } = require('util');

// Import overlay and screenshot services
const overlayWindow = require('./overlayWindow.cjs');
const screenshotService = require('./screenshotService.cjs');
const windowManager = require('./windowManager.cjs');

const execAsync = promisify(exec);

let mainWindow;
let viteProcess = null;

// ✅ ELECTRON CONSOLE CAPTURE - Log to file for MCP access
const logDir = app.getPath('userData');
const logFile = path.join(logDir, 'electron-console.log');
const maxLogSize = 10 * 1024 * 1024; // 10MB

// Ensure log directory exists
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}

// ✅ Log rotation function
function rotateLogIfNeeded() {
    if (fs.existsSync(logFile)) {
        const stats = fs.statSync(logFile);
        if (stats.size > maxLogSize) {
            // Keep last 5MB
            const content = fs.readFileSync(logFile, 'utf8');
            const lines = content.split('\n');
            const keepLines = lines.slice(-50000); // Keep last 50k lines
            fs.writeFileSync(logFile, keepLines.join('\n'));
        }
    }
}

// ✅ Store original console methods BEFORE overriding
const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;

// ✅ Enhanced logging function
function writeLog(level, source, ...args) {
    const timestamp = new Date().toISOString();
    const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' ');
    const logEntry = `[${timestamp}] [${level.toUpperCase()}] [${source}] ${message}\n`;
    
    // Write to file
    try {
        fs.appendFileSync(logFile, logEntry);
        rotateLogIfNeeded();
    } catch (error) {
        // FIXED: Use originalError instead of console.error to avoid infinite loop
        // If log write fails, output to stderr directly (bypass overridden console)
        process.stderr.write(`Failed to write to log file: ${error}\n`);
    }
    
    // FIXED: Use original console methods, not overridden ones
    // Wrap in try-catch to handle EPIPE errors (broken pipe when console output is closed)
    try {
        const originalMethod = level === 'error' ? originalError : (level === 'warn' ? originalWarn : originalLog);
        originalMethod(`[${source}]`, ...args);
    } catch (error) {
        // EPIPE: broken pipe can occur if console output stream is closed
        // Silently ignore - we've already written to file
        if (error.code !== 'EPIPE') {
            // Only log non-EPIPE errors to stderr
            process.stderr.write(`Console output failed: ${error.message}\n`);
        }
    }
}

// ✅ Override console methods for main process
console.log = (...args) => {
    writeLog('log', 'MAIN', ...args);
    // Don't call originalLog here - writeLog already calls it, and avoids double EPIPE errors
};

console.error = (...args) => {
    writeLog('error', 'MAIN', ...args);
    // Don't call originalError here - writeLog already calls it, and avoids double EPIPE errors
};

console.warn = (...args) => {
    writeLog('warn', 'MAIN', ...args);
    // Don't call originalWarn here - writeLog already calls it, and avoids double EPIPE errors
};

// ✅ Log Electron startup
writeLog('log', 'MAIN', '🚀 Electron app starting...');
writeLog('log', 'MAIN', `Log file: ${logFile}`);

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    frame: true, // ✅ Standard Electron frame with menu bar
    titleBarStyle: 'default', // ✅ Standard titlebar
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    },
    icon: path.join(__dirname, '../resources/icon.png'), // Optional icon
    title: 'AIM-OS Dashboard',
    backgroundColor: '#1e1e1e', // Match dark theme
    minWidth: 800,
    minHeight: 600
  });

  // ✅ Create standard menu bar
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            // Handle new file
          }
        },
        {
          label: 'Open',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            // Handle open
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo', label: 'Undo' },
        { role: 'redo', label: 'Redo' },
        { type: 'separator' },
        { role: 'cut', label: 'Cut' },
        { role: 'copy', label: 'Copy' },
        { role: 'paste', label: 'Paste' },
        { role: 'selectAll', label: 'Select All' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { 
          role: 'reload', 
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R'
        },
        { 
          role: 'forceReload', 
          label: 'Force Reload',
          accelerator: 'CmdOrCtrl+Shift+R'
        },
        { 
          label: 'Toggle Developer Tools',
          accelerator: 'F12',
          click: () => {
            if (mainWindow && !mainWindow.isDestroyed()) {
              mainWindow.webContents.toggleDevTools();
            }
          }
        },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Actual Size' },
        { role: 'zoomIn', label: 'Zoom In' },
        { role: 'zoomOut', label: 'Zoom Out' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toggle Full Screen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize', label: 'Minimize' },
        { role: 'close', label: 'Close' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About AIM-OS',
          click: () => {
            // Show about dialog
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
  
  // ✅ Force DevTools to open if app fails to load (for debugging)
  mainWindow.webContents.on('did-fail-load', () => {
    // Auto-open DevTools on load failure so user can debug
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.openDevTools();
      }
    }, 1000);
  });

  // ✅ ALWAYS open DevTools - Force it multiple times to ensure it opens
  mainWindow.webContents.once('did-finish-load', () => {
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.openDevTools();
      }
    }, 500);
  });
  
  mainWindow.webContents.once('dom-ready', () => {
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.openDevTools();
      }
    }, 500);
  });
  
  // Also try immediately (in case events already fired)
  setTimeout(() => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.openDevTools();
    }
  }, 1000);
  
  // Check if production build exists OR if --dev flag is passed
  const distPath = path.join(__dirname, '../dist/index.html');
  const isDev = !fs.existsSync(distPath) || process.argv.includes('--dev');
  
  console.log('[Electron] Build check:', { isDev, distPath, exists: fs.existsSync(distPath) });
  
  // ✅ Add window load event handlers BEFORE loading
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('[Electron] ✅ Window finished loading');
  });
  
  mainWindow.webContents.on('dom-ready', () => {
    console.log('[Electron] ✅ DOM ready');
  });
  
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('[Electron] ❌ Failed to load:', errorCode, errorDescription, validatedURL);
    writeLog('error', 'MAIN', `Failed to load: ${errorCode} - ${errorDescription} - ${validatedURL}`);
  });
  
  if (isDev) {
    // Development: Start Vite dev server and load from it
    console.log('🚀 Starting Vite dev server...');
    viteProcess = spawn('npm', ['run', 'dev'], {
      cwd: path.join(__dirname, '..'),
      shell: true,
      stdio: 'inherit'
    });
    
    // Wait for Vite to start, then load
    setTimeout(() => {
      console.log('[Electron] Loading dev URL: http://localhost:3000');
      mainWindow.loadURL('http://localhost:3000').then(() => {
        console.log('[Electron] ✅ Dev URL loaded successfully');
      }).catch((error) => {
        console.error('[Electron] ❌ Failed to load dev URL:', error);
      });
      // DevTools already opened above
      
      // ✅ Capture renderer console messages
      mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
        const levelMap = { 0: 'log', 1: 'warn', 2: 'error', 3: 'info' };
        writeLog(levelMap[level] || 'log', 'RENDERER', message);
      });
    }, 3000);
  } else {
    // Production: Load from dist folder
    const indexPath = path.join(__dirname, '../dist/index.html');
    console.log('[Electron] Loading production file:', indexPath);
    mainWindow.loadFile(indexPath).then(() => {
      console.log('[Electron] ✅ Production file loaded successfully');
    }).catch((error) => {
      console.error('[Electron] ❌ Failed to load production file:', error);
    });
    
    // ✅ Capture renderer console messages (production)
    mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
      const levelMap = { 0: 'log', 1: 'warn', 2: 'error', 3: 'info' };
      writeLog(levelMap[level] || 'log', 'RENDERER', message);
    });
    
    // Add reload shortcut in production (Ctrl+R or Cmd+R)
    // Add DevTools shortcut (Ctrl+Shift+I or Cmd+Shift+I)
    mainWindow.webContents.on('before-input-event', (event, input) => {
      if ((input.control || input.meta) && input.key.toLowerCase() === 'r') {
        event.preventDefault();
        mainWindow.reload();
      }
      // Ctrl+Shift+I or Cmd+Shift+I for DevTools
      if ((input.control || input.meta) && input.shift && input.key.toLowerCase() === 'i') {
        event.preventDefault();
        mainWindow.webContents.toggleDevTools();
      }
      // F12 for DevTools (alternative)
      if (input.key === 'F12') {
        event.preventDefault();
        mainWindow.webContents.toggleDevTools();
      }
    });
  }

  // ✅ AUTO-RECOVERY: Handle renderer process crashes
  mainWindow.webContents.on('render-process-gone', (event, details) => {
    console.error('Renderer process crashed:', details);
    writeLog('error', 'MAIN', `Renderer crashed: ${details.reason}`);
    
    // Auto-restart window instead of crashing
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        console.log('🔄 Auto-restarting Electron window after crash...');
        mainWindow.reload();
      } else {
        console.log('🔄 Creating new window after crash...');
        createWindow();
      }
    }, 1000);
  });

  // ✅ AUTO-RECOVERY: Handle uncaught exceptions in renderer
  mainWindow.webContents.on('uncaught-exception', (event, error) => {
    console.error('Uncaught exception:', error);
    writeLog('error', 'MAIN', `Uncaught exception: ${error.message}`);
    event.preventDefault(); // Don't crash
    
    // Auto-reload window
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        console.log('🔄 Auto-reloading Electron window after exception...');
        mainWindow.reload();
      }
    }, 1000);
  });

  // ✅ AUTO-RESTART: Reload window on connection failures
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('Failed to load:', errorCode, errorDescription);
    writeLog('error', 'MAIN', `Failed to load: ${errorCode} - ${errorDescription}`);
    
    // Auto-retry load
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        console.log('🔄 Retrying load after failure...');
        const distPath = path.join(__dirname, '../dist/index.html');
        const isDev = !fs.existsSync(distPath);
        if (isDev) {
          mainWindow.loadURL('http://localhost:3000');
        } else {
          mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
        }
      }
    }, 2000);
  });

  // ✅ Listen for maximize state changes
  mainWindow.on('maximize', () => {
    mainWindow.webContents.send('window-maximize-changed', true);
  });

  mainWindow.on('unmaximize', () => {
    mainWindow.webContents.send('window-maximize-changed', false);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (viteProcess) {
      viteProcess.kill();
      viteProcess = null;
    }
  });
}

// IPC handlers for AIM-OS daemon communication
ipcMain.handle('aimos-api', async (event, { method, endpoint, data }) => {
  try {
    const url = new URL(`http://localhost:5000${endpoint}`);
    const client = url.protocol === 'https:' ? https : http;
    
    return new Promise((resolve, reject) => {
      const options = {
        hostname: url.hostname,
        port: url.port || (url.protocol === 'https:' ? 443 : 80),
        path: url.pathname + url.search,
        method: method || 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      };
      
      const req = client.request(options, (res) => {
        let body = '';
        res.on('data', (chunk) => { body += chunk; });
        res.on('end', () => {
          try {
            const result = JSON.parse(body);
            resolve({ success: true, data: result });
          } catch (e) {
            resolve({ success: true, data: body });
          }
        });
      });
      
      req.on('error', (error) => {
        resolve({ success: false, error: error.message });
      });
      
      if (data) {
        req.write(JSON.stringify(data));
      }
      req.end();
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// ✅ IPC handler for renderer console logs (FIXED: don't spread args object)
ipcMain.handle('electron-console-log', (event, { level, message }) => {
  // message is already serialized from preload script
  writeLog(level || 'log', 'RENDERER', message);
});

// ✅ IPC handlers for window controls (borderless window)
ipcMain.handle('window-minimize', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.minimize();
    return { success: true };
  }
  return { success: false, error: 'Window not available' };
});

ipcMain.handle('window-maximize', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
    return { success: true, isMaximized: mainWindow.isMaximized() };
  }
  return { success: false, error: 'Window not available' };
});

ipcMain.handle('window-close', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.close();
    return { success: true };
  }
  return { success: false, error: 'Window not available' };
});

ipcMain.handle('window-is-maximized', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    return { success: true, isMaximized: mainWindow.isMaximized() };
  }
  return { success: false, error: 'Window not available' };
});

// ✅ Toggle DevTools
ipcMain.handle('toggle-devtools', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.toggleDevTools();
    return { success: true };
  }
  return { success: false, error: 'Window not available' };
});

// ✅ IPC handler for reading logs
ipcMain.handle('read-logs', async (event, { limit, level, source }) => {
  try {
    if (!fs.existsSync(logFile)) {
      return { success: true, logs: [] };
    }
    
    const content = fs.readFileSync(logFile, 'utf8');
    const lines = content.split('\n').filter(line => line.trim());
    
    let logs = lines.map(line => {
      // Parse log format: [timestamp] [LEVEL] [SOURCE] message
      const match = line.match(/^\[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] (.+)$/);
      if (match) {
        return {
          timestamp: match[1],
          level: match[2].toLowerCase(),
          source: match[3],
          message: match[4]
        };
      }
      return null;
    }).filter(log => log !== null);
    
    // Apply filters
    if (level) {
      logs = logs.filter(log => log.level === level.toLowerCase());
    }
    if (source) {
      logs = logs.filter(log => log.source === source.toUpperCase());
    }
    
    // Apply limit
    if (limit) {
      logs = logs.slice(-limit); // Get last N logs
    }
    
    return { success: true, logs };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to read logs: ${error.message}`);
    return { success: false, error: error.message };
  }
});

// ✅ IPC handlers for system tools
ipcMain.handle('system-get-processes', async () => {
  try {
    const platform = os.platform();
    let processes = [];
    
    if (platform === 'win32') {
      // Windows: Use wmic or tasklist
      try {
        const { stdout } = await execAsync('tasklist /FO CSV /NH');
        const lines = stdout.split('\n').filter(line => line.trim());
        processes = lines.map(line => {
          const parts = line.split('","').map(p => p.replace(/"/g, ''));
          if (parts.length >= 5) {
            return {
              pid: parseInt(parts[1]) || 0,
              name: parts[0],
              cpu: 0, // Tasklist doesn't provide CPU
              memory: parseFloat(parts[4].replace(/[^\d.]/g, '')) * 1024 * 1024 || 0, // Convert MB to bytes
              command: parts[0],
              status: parts[4] || 'RUNNING'
            };
          }
          return null;
        }).filter(p => p !== null && p.pid > 0);
      } catch (error) {
        writeLog('warn', 'MAIN', `Failed to get processes: ${error.message}`);
        return { success: false, error: error.message };
      }
    } else {
      // macOS/Linux: Use ps command
      try {
        const { stdout } = await execAsync('ps -eo pid,comm,%cpu,rss,command --no-headers');
        const lines = stdout.split('\n').filter(line => line.trim());
        processes = lines.map(line => {
          const parts = line.trim().split(/\s+/);
          if (parts.length >= 5) {
            return {
              pid: parseInt(parts[0]) || 0,
              name: parts[1],
              cpu: parseFloat(parts[2]) || 0,
              memory: parseInt(parts[3]) * 1024 || 0, // Convert KB to bytes
              command: parts.slice(4).join(' '),
              status: 'RUNNING'
            };
          }
          return null;
        }).filter(p => p !== null && p.pid > 0);
      } catch (error) {
        writeLog('warn', 'MAIN', `Failed to get processes: ${error.message}`);
        return { success: false, error: error.message };
      }
    }
    
    return { success: true, processes };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to get processes: ${error.message}`);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-get-ports', async () => {
  try {
    const platform = os.platform();
    let ports = [];
    
    if (platform === 'win32') {
      // Windows: Use netstat
      try {
        const { stdout } = await execAsync('netstat -ano');
        const lines = stdout.split('\n').filter(line => line.trim());
        const portMap = new Map();
        
        lines.forEach(line => {
          const match = line.match(/(TCP|UDP)\s+(\S+):(\d+)\s+.*\s+(\d+)/);
          if (match) {
            const protocol = match[1].toLowerCase();
            const port = parseInt(match[3]);
            const pid = parseInt(match[4]);
            
            if (port && pid) {
              const key = `${port}-${protocol}`;
              if (!portMap.has(key)) {
                portMap.set(key, {
                  port,
                  protocol,
                  pid,
                  processName: 'Unknown', // Will be resolved separately
                  status: 'LISTENING'
                });
              }
            }
          }
        });
        
        ports = Array.from(portMap.values());
        
        // Resolve process names
        for (const port of ports) {
          try {
            const { stdout } = await execAsync(`tasklist /FI "PID eq ${port.pid}" /FO CSV /NH`);
            const parts = stdout.split('","');
            if (parts.length > 0) {
              port.processName = parts[0].replace(/"/g, '') || 'Unknown';
            }
          } catch (e) {
            // Ignore errors for individual process lookups
          }
        }
      } catch (error) {
        writeLog('warn', 'MAIN', `Failed to get ports: ${error.message}`);
        return { success: false, error: error.message };
      }
    } else {
      // macOS/Linux: Use lsof or netstat
      try {
        const { stdout } = await execAsync('lsof -i -P -n | grep LISTEN');
        const lines = stdout.split('\n').filter(line => line.trim());
        const portMap = new Map();
        
        lines.forEach(line => {
          const parts = line.trim().split(/\s+/);
          if (parts.length >= 9) {
            const name = parts[0];
            const pid = parseInt(parts[1]);
            const protocol = parts[7].split(':')[0].toLowerCase();
            const port = parseInt(parts[8].split(':').pop());
            
            if (port && pid) {
              const key = `${port}-${protocol}`;
              if (!portMap.has(key)) {
                portMap.set(key, {
                  port,
                  protocol,
                  pid,
                  processName: name,
                  status: 'LISTENING'
                });
              }
            }
          }
        });
        
        ports = Array.from(portMap.values());
      } catch (error) {
        writeLog('warn', 'MAIN', `Failed to get ports: ${error.message}`);
        return { success: false, error: error.message };
      }
    }
    
    return { success: true, ports };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to get ports: ${error.message}`);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-get-info', async () => {
  try {
    const cpus = os.cpus();
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    
    // Get disk usage (simplified - just reports basic info)
    const diskInfo = {
      total: 0,
      used: 0,
      free: 0,
      percentage: 0
    };
    
    try {
      const platform = os.platform();
      if (platform === 'win32') {
        const { stdout } = await execAsync('wmic logicaldisk get size,freespace,caption');
        // Parse disk info (simplified)
        diskInfo.total = totalMem * 10; // Rough estimate
        diskInfo.used = usedMem * 10;
        diskInfo.free = freeMem * 10;
        diskInfo.percentage = (diskInfo.used / diskInfo.total) * 100;
      } else {
        const { stdout } = await execAsync('df -h /');
        const parts = stdout.split('\n')[1].split(/\s+/);
        if (parts.length >= 4) {
          // Parse disk info (simplified)
          diskInfo.total = totalMem * 10;
          diskInfo.used = usedMem * 10;
          diskInfo.free = freeMem * 10;
          diskInfo.percentage = (diskInfo.used / diskInfo.total) * 100;
        }
      }
    } catch (error) {
      writeLog('warn', 'MAIN', `Failed to get disk info: ${error.message}`);
    }
    
    const info = {
      cpu: {
        usage: 0, // Would need to calculate from previous snapshot
        cores: cpus.length,
        model: cpus[0]?.model || 'Unknown'
      },
      memory: {
        total: totalMem,
        used: usedMem,
        free: freeMem,
        percentage: (usedMem / totalMem) * 100
      },
      disk: diskInfo,
      platform: os.platform(),
      arch: os.arch(),
      nodeVersion: process.version,
      electronVersion: process.versions.electron
    };
    
    return { success: true, info };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to get system info: ${error.message}`);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-kill-process', async (event, { pid }) => {
  try {
    const platform = os.platform();
    
    if (platform === 'win32') {
      await execAsync(`taskkill /F /PID ${pid}`);
    } else {
      await execAsync(`kill -9 ${pid}`);
    }
    
    return { success: true };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to kill process ${pid}: ${error.message}`);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-close-port', async (event, { port }) => {
  try {
    // First find process using the port
    const platform = os.platform();
    let pid = null;
    
    if (platform === 'win32') {
      const { stdout } = await execAsync(`netstat -ano | findstr :${port}`);
      const match = stdout.match(/\s+(\d+)$/);
      if (match) {
        pid = parseInt(match[1]);
      }
    } else {
      const { stdout } = await execAsync(`lsof -ti:${port}`);
      pid = parseInt(stdout.trim());
    }
    
    if (pid) {
      // Kill the process using the port
      if (platform === 'win32') {
        await execAsync(`taskkill /F /PID ${pid}`);
      } else {
        await execAsync(`kill -9 ${pid}`);
      }
      return { success: true };
    } else {
      return { success: false, error: 'No process found using this port' };
    }
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to close port ${port}: ${error.message}`);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-get-terminals', async () => {
  try {
    // Integration with Cursor terminals via Command Server
    // For now, return empty array - will integrate with Cursor API later
    return { success: true, terminals: [] };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to get terminals: ${error.message}`);
    return { success: false, error: error.message };
  }
});

// ✅ IPC handlers for template capture overlay
ipcMain.handle('overlay:show', async () => {
  try {
    // Step 1: Ensure Cursor window is open
    await windowManager.ensureCursorOpen();
    
    // Step 2: Create overlay window (no screenshot yet)
    overlayWindow.createOverlayWindow();
    
    return { success: true };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to show overlay: ${error.message}`);
    return { success: false, error: error.message };
  }
});

// Overlay → Main process (rectangle selected, user clicked Accept)
ipcMain.handle('overlay:capture', async (event, rectangle) => {
  try {
    // Step 1: Close/hide overlay window immediately
    overlayWindow.hideOverlayWindow();
    
    // Step 2: Small delay to ensure overlay is fully closed
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Step 3: Capture full screen screenshot
    const fullScreenshot = await screenshotService.captureScreen();
    
    // Step 4: Crop selected region from screenshot
    const template = await screenshotService.extractRegion(
      fullScreenshot,
      rectangle
    );
    
    // Step 5: Minimize Cursor window
    await windowManager.minimizeCursor();
    
    // Step 6: Bring Electron app to front
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show();
      mainWindow.focus();
    }
    
    // Step 7: Close overlay window completely
    overlayWindow.closeOverlayWindow();
    
    // Step 8: Send result to renderer (thumbnail + coordinates)
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('capture:result', {
        thumbnail: template.toString('base64'),
        rectangle,
        fullScreenshot: fullScreenshot.toString('base64')
      });
    }
    
    return { success: true };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to capture template: ${error.message}`);
    return { success: false, error: error.message };
  }
});

// Overlay → Main process (cancel)
ipcMain.handle('overlay:cancel', async () => {
  try {
    // Close overlay without capturing
    overlayWindow.closeOverlayWindow();
    
    // Bring Electron app back to front
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show();
      mainWindow.focus();
    }
    
    return { success: true };
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to cancel overlay: ${error.message}`);
    return { success: false, error: error.message };
  }
});

// Save template
ipcMain.handle('template:save', async (event, { templateData, metadata }) => {
  try {
    const result = await screenshotService.saveTemplate(templateData, metadata);
    return result;
  } catch (error) {
    writeLog('error', 'MAIN', `Failed to save template: ${error.message}`);
    return { success: false, error: error.message };
  }
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (viteProcess) {
    viteProcess.kill();
    viteProcess = null;
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (viteProcess) {
    viteProcess.kill();
    viteProcess = null;
  }
});

