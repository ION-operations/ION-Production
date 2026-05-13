import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import fs from 'fs';
import http from 'http';
import https from 'https';
import { URL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
        // If log write fails, at least output to console
        console.error('Failed to write to log file:', error);
    }
    
    // Also output to console (original behavior)
    const originalMethod = console[level] || console.log;
    originalMethod(`[${source}]`, ...args);
}

// ✅ Override console methods for main process
const originalLog = console.log;
console.log = (...args) => {
    writeLog('log', 'MAIN', ...args);
    originalLog(...args);
};

const originalError = console.error;
console.error = (...args) => {
    writeLog('error', 'MAIN', ...args);
    originalError(...args);
};

const originalWarn = console.warn;
console.warn = (...args) => {
    writeLog('warn', 'MAIN', ...args);
    originalWarn(...args);
};

// ✅ Log Electron startup
writeLog('log', 'MAIN', '🚀 Electron app starting...');
writeLog('log', 'MAIN', `Log file: ${logFile}`);

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    },
    icon: path.join(__dirname, '../resources/icon.png'), // Optional icon
    title: 'AIM-OS Dashboard'
  });

  // Check if production build exists
  const distPath = path.join(__dirname, '../dist/index.html');
  const isDev = !fs.existsSync(distPath);
  
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
      mainWindow.loadURL('http://localhost:3000');
      mainWindow.webContents.openDevTools(); // Auto-open dev tools in dev mode
      
      // ✅ Capture renderer console messages
      mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
        const levelMap = { 0: 'log', 1: 'warn', 2: 'error', 3: 'info' };
        writeLog(levelMap[level] || 'log', 'RENDERER', message);
      });
    }, 3000);
  } else {
    // Production: Load from dist folder
    const indexPath = path.join(__dirname, '../dist/index.html');
    mainWindow.loadFile(indexPath);
    
    // ✅ Capture renderer console messages (production)
    mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
      const levelMap = { 0: 'log', 1: 'warn', 2: 'error', 3: 'info' };
      writeLog(levelMap[level] || 'log', 'RENDERER', message);
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

// ✅ IPC handler for renderer console logs (explicit logging)
ipcMain.handle('electron-console-log', (event, { level, message, ...args }) => {
  writeLog(level || 'log', 'RENDERER', message, ...args);
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

