// ═══════════════════════════════════════════════════════════════
// JOC — Electron Main Process
// ═══════════════════════════════════════════════════════════════

const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');

// ─── Configuration ───

const IS_DEV = process.env.NODE_ENV !== 'production';
const DEV_SERVER_URL = 'http://localhost:5011';
const WINDOW_CONFIG = {
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'JOC — Joint Operations Center',
};

// ─── Window Management ───

let mainWindow = null;

function createMainWindow() {
    mainWindow = new BrowserWindow({
        ...WINDOW_CONFIG,
        frame: false,                    // Custom title bar for full canon control
        titleBarStyle: 'hidden',
        titleBarOverlay: {
            color: '#0a0a1a',             // --bg-deep
            symbolColor: '#8a8a9a',       // --text-secondary
            height: 32,
        },
        backgroundColor: '#0a0a1a',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            webviewTag: true,              // Enable <webview> for AI session embedding
            sandbox: false,                // Needed for preload to access Node APIs
        },
    });

    // Load the app
    if (IS_DEV) {
        mainWindow.loadURL(DEV_SERVER_URL);
        // Open DevTools in development
        mainWindow.webContents.openDevTools({ mode: 'detach' });
    } else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // ─── Webview Session Partitioning ───
    // Each AI provider gets its own session partition so cookies/auth don't clash
    setupSessionPartitions();
}

// ─── Session Partitions ───
// Separate cookie jars per AI provider — ChatGPT cookies won't interfere with Gemini

function setupSessionPartitions() {
    const providers = ['chatgpt', 'gemini', 'claude', 'perplexity'];

    providers.forEach(provider => {
        const partition = `persist:joc-${provider}`;
        const ses = session.fromPartition(partition);

        // Set a reasonable user agent
        ses.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        );

        // Allow all permissions the AI sites need (media, notifications, etc.)
        ses.setPermissionRequestHandler((_webContents, permission, callback) => {
            const allowed = ['clipboard-read', 'clipboard-write', 'notifications', 'media'];
            callback(allowed.includes(permission));
        });
    });
}

// ─── IPC Handlers ───

// Get session cookies for a provider (for health checks)
ipcMain.handle('session:get-cookies', async (_event, provider) => {
    const partition = `persist:joc-${provider}`;
    const ses = session.fromPartition(partition);
    try {
        const cookies = await ses.cookies.get({});
        return { success: true, cookies: cookies.map(c => ({ name: c.name, domain: c.domain, expirationDate: c.expirationDate })) };
    } catch (err) {
        return { success: false, error: err.message };
    }
});

// Clear session for a provider (logout/reset)
ipcMain.handle('session:clear', async (_event, provider) => {
    const partition = `persist:joc-${provider}`;
    const ses = session.fromPartition(partition);
    try {
        await ses.clearStorageData();
        return { success: true };
    } catch (err) {
        return { success: false, error: err.message };
    }
});

// Execute JavaScript in a webview (for injection/extraction)
ipcMain.handle('webview:execute-js', async (_event, { webviewId, code }) => {
    // The renderer process handles this via webview.executeJavaScript
    // This is a fallback channel for cases where we need main-process coordination
    return { success: true, channel: 'webview:execute-js', webviewId };
});

// Get webview DOM info (bounding rects for overlay calibration)
ipcMain.handle('webview:get-element-rect', async (_event, { webviewId, selector }) => {
    // Forwarded to renderer — the webview's executeJavaScript does the actual work
    return { success: true, channel: 'webview:get-element-rect', webviewId, selector };
});

// Window control (for frameless window)
ipcMain.on('window:minimize', () => mainWindow?.minimize());
ipcMain.on('window:maximize', () => {
    if (mainWindow?.isMaximized()) {
        mainWindow.unmaximize();
    } else {
        mainWindow?.maximize();
    }
});
ipcMain.on('window:close', () => mainWindow?.close());

// ─── App Lifecycle ───

app.whenReady().then(() => {
    createMainWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createMainWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// ─── Security: Restrict navigation ───

app.on('web-contents-created', (_event, contents) => {
    // Prevent the main window from navigating away
    contents.on('will-navigate', (event, url) => {
        if (contents === mainWindow?.webContents) {
            const allowed = [DEV_SERVER_URL, 'file://'];
            if (!allowed.some(a => url.startsWith(a))) {
                event.preventDefault();
            }
        }
    });

    // Prevent new windows (popups) — force everything into webviews
    contents.setWindowOpenHandler(({ url }) => {
        // Could route to a new JOC tab instead
        console.log('[JOC] Blocked popup:', url);
        return { action: 'deny' };
    });
});
