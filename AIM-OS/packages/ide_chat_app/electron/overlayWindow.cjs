/**
 * Overlay Window for Template Capture
 * System-wide transparent overlay for rectangle drawing
 */

const { BrowserWindow, screen } = require('electron');
const path = require('path');

let overlayWindow = null;

/**
 * Create overlay window (transparent, full-screen, always-on-top)
 */
function createOverlayWindow() {
  if (overlayWindow) {
    overlayWindow.show();
    overlayWindow.focus();
    return overlayWindow;
  }

  // Get all displays for multi-monitor support
  const displays = screen.getAllDisplays();
  
  // Find bounding box of all displays
  let minX = Infinity, minY = Infinity;
  let maxX = -Infinity, maxY = -Infinity;
  
  displays.forEach(display => {
    minX = Math.min(minX, display.bounds.x);
    minY = Math.min(minY, display.bounds.y);
    maxX = Math.max(maxX, display.bounds.x + display.bounds.width);
    maxY = Math.max(maxY, display.bounds.y + display.bounds.height);
  });

  const width = maxX - minX;
  const height = maxY - minY;

  overlayWindow = new BrowserWindow({
    width: width,
    height: height,
    x: minX,
    y: minY,
    frame: false,                    // Frameless
    transparent: true,               // Transparent background
    alwaysOnTop: true,               // Always on top
    skipTaskbar: true,               // Don't show in taskbar
    resizable: false,                // Fixed size
    movable: false,                   // Fixed position
    focusable: true,                 // Can receive focus
    hasShadow: false,                // No shadow
    opacity: 0.3,                    // Semi-transparent overlay (dimmed)
    webPreferences: {
      nodeIntegration: true,         // Enable for IPC access
      contextIsolation: false,        // Disable for direct IPC access
      preload: path.join(__dirname, 'overlayPreload.cjs')
    }
  });

  // Set to be above all windows
  overlayWindow.setAlwaysOnTop(true, 'screen-saver');
  overlayWindow.setIgnoreMouseEvents(false); // Allow mouse events for drawing

  // Load overlay HTML
  overlayWindow.loadFile(path.join(__dirname, '..', 'public', 'overlay.html'));

  // Handle window close
  overlayWindow.on('closed', () => {
    overlayWindow = null;
  });

  return overlayWindow;
}

/**
 * Close overlay window
 */
function closeOverlayWindow() {
  if (overlayWindow) {
    overlayWindow.close();
    overlayWindow = null;
  }
}

/**
 * Hide overlay window (faster than close)
 */
function hideOverlayWindow() {
  if (overlayWindow) {
    overlayWindow.hide();
  }
}

module.exports = {
  createOverlayWindow,
  closeOverlayWindow,
  hideOverlayWindow,
  getOverlayWindow: () => overlayWindow
};

