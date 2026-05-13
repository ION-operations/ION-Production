// ═══════════════════════════════════════════════════════════════
// JOC — Electron Preload Script
// IPC bridge between renderer (React) and main process
// ═══════════════════════════════════════════════════════════════

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('jocBridge', {

    // ─── Platform Detection ───
    isElectron: true,
    platform: process.platform,

    // ─── Window Controls (frameless window) ───
    window: {
        minimize: () => ipcRenderer.send('window:minimize'),
        maximize: () => ipcRenderer.send('window:maximize'),
        close: () => ipcRenderer.send('window:close'),
    },

    // ─── Session Management ───
    session: {
        getCookies: (provider) => ipcRenderer.invoke('session:get-cookies', provider),
        clear: (provider) => ipcRenderer.invoke('session:clear', provider),
    },

    // ─── Webview Control ───
    // These are convenience wrappers — most webview control happens directly
    // in the renderer via the <webview> DOM element's API.
    webview: {
        executeJS: (webviewId, code) =>
            ipcRenderer.invoke('webview:execute-js', { webviewId, code }),
        getElementRect: (webviewId, selector) =>
            ipcRenderer.invoke('webview:get-element-rect', { webviewId, selector }),
    },

    // ─── Event Subscriptions ───
    on: (channel, callback) => {
        const validChannels = [
            'session:cookie-changed',
            'webview:dom-ready',
            'webview:navigation',
            'webview:console',
        ];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (_event, ...args) => callback(...args));
        }
    },

    removeAllListeners: (channel) => {
        ipcRenderer.removeAllListeners(channel);
    },
});
