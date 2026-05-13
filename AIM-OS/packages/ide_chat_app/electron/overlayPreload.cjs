/**
 * Overlay Preload Script
 * Exposes IPC access to overlay renderer
 */

const { ipcRenderer } = require('electron');

// Expose IPC to overlay window
window.ipcRenderer = ipcRenderer;
window.electronAPI = {
  invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
  send: (channel, ...args) => ipcRenderer.send(channel, ...args)
};


