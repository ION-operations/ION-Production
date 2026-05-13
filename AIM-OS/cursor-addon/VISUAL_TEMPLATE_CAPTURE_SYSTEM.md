# Visual Template Capture System - Complete Design

**Date:** 2025-11-02  
**Status:** 📋 **DESIGN COMPLETE - AWAITING IMPLEMENTATION**  
**Protocol:** A-H Protocol - Full documentation before code  
**Priority:** High - Enables user-friendly macro automation

---

## 🎯 **CORE REQUIREMENT**

**User draws rectangle over ANY window (like Snipping Tool) → System captures template → Used for pixel search detection**

This is a **SYSTEM-WIDE OVERLAY** - not a component inside the Electron app. It works like Windows Snipping Tool or macOS screenshot tool:
- Transparent full-screen overlay window
- Works over ANY window (Cursor, browser, etc.)
- Rectangle drawing tool
- Captures selected area from underlying window
- Saves as template for pixel matching

---

## 🏗️ **ARCHITECTURE OVERVIEW**

```
[User clicks "Capture Template" in Electron App]
    ↓
[Electron Main Process creates overlay window]
    ↓ (Transparent, full-screen, always-on-top)
    ↓
[User draws rectangle over Cursor window]
    ↓ (Rectangle visible on overlay)
    ↓
[User clicks Accept/confirms selection]
    ↓
[Overlay window closes/hides]
    ↓
[System captures screenshot of full screen]
    ↓
[System crops selected region from screenshot]
    ↓
[Template saved with metadata]
    ↓
[Template available for vision detection]

---

## 📐 **COMPONENT DESIGN**

### **1. Overlay Window (Electron Main Process)**

**Location:** `packages/ide_chat_app/electron/overlayWindow.js`

**Purpose:** Create system-wide transparent overlay for rectangle drawing

**Window Management Flow:**
1. User clicks "Capture Template" in Electron app
2. System checks if Cursor window is open
3. If Cursor not open → Open Cursor window
4. If Cursor minimized → Restore Cursor window
5. Bring Cursor window to front (but overlay will be on top)
6. Create transparent overlay window
7. Overlay appears on top of everything

**Key Properties:**
- **Frameless:** No window borders/chrome
- **Transparent:** See through to underlying windows
- **Always-on-top:** Above all other windows (including Cursor)
- **Full-screen:** Covers all displays
- **Click-through:** Can interact with underlying windows (optional)
- **Non-resizable:** Fixed size matching screen dimensions

**Electron BrowserWindow Configuration:**
```javascript
const overlayWindow = new BrowserWindow({
    width: screenSize.width,
    height: screenSize.height,
    x: 0,
    y: 0,
    frame: false,                    // Frameless
    transparent: true,               // Transparent background
    alwaysOnTop: true,               // Always on top
    skipTaskbar: true,               // Don't show in taskbar
    resizable: false,                // Fixed size
    movable: false,                  // Fixed position
    focusable: true,                 // Can receive focus
    hasShadow: false,                // No shadow
    opacity: 0.3,                    // Semi-transparent overlay (dimmed)
    webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'overlayPreload.js')
    }
});

// Set to be above all windows
overlayWindow.setAlwaysOnTop(true, 'screen-saver');
overlayWindow.setIgnoreMouseEvents(false); // Allow mouse events for drawing
```

**Window Lifecycle:**
1. User clicks "Capture Template" in Electron app
2. System manages Cursor window (open/restore if needed)
3. Main process creates overlay window
4. Overlay window loads HTML/React component
5. User draws rectangle over target window/element
6. User clicks Accept/confirms selection
7. Rectangle coordinates sent to main process
8. Overlay window closes/hides
9. Main process captures screenshot (full screen)
10. Main process crops selected region from screenshot
11. System minimizes Cursor window
12. Electron app window shows again (brought to front)
13. Electron app displays thumbnail + coordinates
14. User enters template metadata and saves
15. Template saved

---

### **2. Overlay React Component**

**Location:** `packages/ide_chat_app/src/components/OverlayCapture.tsx`

**Purpose:** Rectangle drawing UI on transparent overlay

**Features:**
- Semi-transparent dimmed background (shows underlying windows)
- Rectangle drawing tool (click + drag)
- Live preview of selected region
- Magnifier/zoom for precise selection
- Coordinates display
- Cancel button (ESC key)
- Instructions overlay

**Component Structure:**
```typescript
interface OverlayCaptureProps {
    onCapture: (rectangle: Rectangle) => void;
    onCancel: () => void;
}

const OverlayCapture: React.FC<OverlayCaptureProps> = ({ onCapture, onCancel }) => {
    const [isDrawing, setIsDrawing] = useState(false);
    const [startPoint, setStartPoint] = useState<Point | null>(null);
    const [currentRect, setCurrentRect] = useState<Rectangle | null>(null);
    const [magnifierVisible, setMagnifierVisible] = useState(false);
    
    // Full-screen overlay styling
    const overlayStyle: React.CSSProperties = {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0, 0, 0, 0.5)', // Dimmed background
        zIndex: 999999,
        cursor: 'crosshair',
        userSelect: 'none'
    };
    
    // ... rectangle drawing logic ...
};
```

**Rectangle Drawing:**
```typescript
const handleMouseDown = (e: React.MouseEvent) => {
    setStartPoint({ x: e.clientX, y: e.clientY });
    setIsDrawing(true);
};

const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing || !startPoint) return;
    
    const currentRect: Rectangle = {
        x: Math.min(startPoint.x, e.clientX),
        y: Math.min(startPoint.y, e.clientY),
        width: Math.abs(e.clientX - startPoint.x),
        height: Math.abs(e.clientY - startPoint.y)
    };
    
    setCurrentRect(currentRect);
    drawRectangle(currentRect);
};

const handleMouseUp = () => {
    if (currentRect) {
        onCapture(currentRect);
    }
    setIsDrawing(false);
};
```

**Visual Feedback:**
- Rectangle border (bright color, e.g., cyan)
- Rectangle fill (semi-transparent)
- Selected region highlighted (brighter)
- Rest of screen dimmed
- Coordinates shown in corner
- Magnifier follows mouse cursor

---

### **3. Screenshot Capture Service**

**Location:** `packages/ide_chat_app/electron/screenshotService.js`

**Purpose:** Capture screenshot AFTER user confirms selection, then crop selected region

**Flow:** Overlay shows → User draws rectangle → User accepts → Overlay closes → Capture screenshot → Crop region

**Implementation:**
```javascript
const { desktopCapturer, screen } = require('electron');
const sharp = require('sharp');

class ScreenshotService {
    /**
     * Capture full screen AFTER overlay closes
     * User has already selected the region they want
     */
    async captureScreen() {
        const primaryDisplay = screen.getPrimaryDisplay();
        
        const sources = await desktopCapturer.getSources({
            types: ['screen'],
            thumbnailSize: {
                width: primaryDisplay.size.width,
                height: primaryDisplay.size.height
            }
        });
        
        if (sources.length === 0) {
            throw new Error('No screen sources available');
        }
        
        // Return full screen screenshot
        return sources[0].thumbnail.toPNG();
    }
    
    /**
     * Crop selected region from full screenshot
     */
    async extractRegion(fullScreenshot, rectangle) {
        return await sharp(fullScreenshot)
            .extract({
                left: rectangle.x,
                top: rectangle.y,
                width: rectangle.width,
                height: rectangle.height
            })
            .png()
            .toBuffer();
    }
    
    /**
     * Complete flow: Capture screen and crop region
     */
    async captureAndCrop(rectangle) {
        // Step 1: Capture full screen
        const fullScreenshot = await this.captureScreen();
        
        // Step 2: Crop selected region
        const croppedRegion = await this.extractRegion(fullScreenshot, rectangle);
        
        return {
            fullScreenshot,
            croppedRegion,
            rectangle
        };
    }
}
```

**Critical Timing:** Overlay must close/hide BEFORE capturing screenshot. Small delay ensures overlay is fully closed.

---

### **4. Window Management Service**

**Location:** `packages/ide_chat_app/electron/windowManager.js`

**Purpose:** Manage Cursor window (open, restore, minimize, bring to front)

**Implementation:**
```javascript
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

class WindowManager {
    /**
     * Find Cursor window process
     */
    async findCursorWindow() {
        // Windows: Use tasklist to find Cursor.exe
        // macOS: Use pgrep to find Cursor
        // Linux: Use pgrep to find cursor
        
        const platform = process.platform;
        if (platform === 'win32') {
            const { stdout } = await execAsync('tasklist /FI "IMAGENAME eq Cursor.exe"');
            return stdout.includes('Cursor.exe');
        } else if (platform === 'darwin') {
            const { stdout } = await execAsync('pgrep -f Cursor');
            return stdout.trim().length > 0;
        } else {
            const { stdout } = await execAsync('pgrep -f cursor');
            return stdout.trim().length > 0;
        }
    }
    
    /**
     * Open Cursor window if not already open
     */
    async ensureCursorOpen() {
        const isOpen = await this.findCursorWindow();
        
        if (!isOpen) {
            // Open Cursor
            const platform = process.platform;
            if (platform === 'win32') {
                await execAsync('start "" "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\cursor\\Cursor.exe"');
            } else if (platform === 'darwin') {
                await execAsync('open -a Cursor');
            } else {
                await execAsync('cursor');
            }
            
            // Wait for Cursor to open
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
        
        // Bring Cursor to front (but overlay will be on top)
        await this.bringCursorToFront();
    }
    
    /**
     * Bring Cursor window to front
     */
    async bringCursorToFront() {
        const platform = process.platform;
        
        if (platform === 'win32') {
            // Use PowerShell to bring window to front
            await execAsync(`powershell -Command "[Microsoft.VisualBasic.Interaction]::AppActivate((Get-Process | Where-Object {$_.MainWindowTitle -like '*Cursor*'}).Id)"`);
        } else if (platform === 'darwin') {
            await execAsync('osascript -e \'tell application "Cursor" to activate\'');
        } else {
            // Linux: Use wmctrl
            await execAsync('wmctrl -a Cursor');
        }
    }
    
    /**
     * Minimize Cursor window
     */
    async minimizeCursor() {
        const platform = process.platform;
        
        if (platform === 'win32') {
            // Use PowerShell to minimize window
            await execAsync(`powershell -Command "$proc = Get-Process | Where-Object {$_.MainWindowTitle -like '*Cursor*'}; if ($proc) { $proc | ForEach-Object { $hwnd = $_.MainWindowHandle; [void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.SendKeys]::SendWait('{F11}'); } }"`);
        } else if (platform === 'darwin') {
            await execAsync('osascript -e \'tell application "Cursor" to set miniaturized of every window to true\'');
        } else {
            // Linux: Use wmctrl
            await execAsync('wmctrl -r Cursor -b add,hidden');
        }
    }
}
```

**Location:** `packages/ide_chat_app/electron/ipcHandlers.js`

**Purpose:** Communication between overlay and main process

**IPC Events:**
```javascript
// Main process → Overlay
ipcMain.handle('overlay:show', async () => {
    // Step 1: Ensure Cursor window is open
    await windowManager.ensureCursorOpen();
    
    // Step 2: Create overlay window (no screenshot yet)
    const overlay = createOverlayWindow();
    
    return { success: true };
});

// Overlay → Main process (rectangle selected, user clicked Accept)
ipcMain.handle('overlay:capture', async (event, rectangle) => {
    // Step 1: Close/hide overlay window immediately
    overlayWindow.hide(); // Hide first (faster than close)
    
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
    mainWindow.show();
    mainWindow.focus();
    
    // Step 7: Close overlay window completely
    overlayWindow.close();
    
    // Step 8: Send result to renderer (thumbnail + coordinates)
    mainWindow.webContents.send('capture:result', {
        thumbnail: template.toString('base64'),
        rectangle,
        fullScreenshot: fullScreenshot.toString('base64')
    });
    
    return { success: true };
});

// Overlay → Main process (cancel)
ipcMain.handle('overlay:cancel', async () => {
    // Close overlay without capturing
    overlayWindow.close();
    
    // Bring Electron app back to front
    mainWindow.show();
    mainWindow.focus();
    
    return { success: true };
});
```

---

### **5. IPC Communication**

**Location:** `packages/ide_chat_app/src/services/templateCaptureService.ts`

**Purpose:** Save captured templates with metadata

**Complete Flow:**
1. User clicks "Capture Template" in Electron app UI
2. Renderer sends IPC message to main process (`overlay:show`)
3. Main process ensures Cursor window is open (opens/restores if needed)
4. Main process creates overlay window (transparent, full-screen)
5. Overlay window shows rectangle drawing tool
6. User draws rectangle over target window/element (Cursor, etc.)
7. User clicks Accept/confirms selection
8. Overlay sends rectangle coordinates to main process (`overlay:capture`)
9. Overlay window closes/hides
10. Main process waits briefly (100ms) for overlay to fully close
11. Main process captures full screen screenshot
12. Main process crops selected region from screenshot
13. Main process minimizes Cursor window
14. Main process brings Electron app window to front
15. Main process sends result to renderer (thumbnail + coordinates)
16. Electron app UI displays `CaptureResult` component
17. User enters template metadata (name, theme)
18. User clicks Save
19. Template saved with metadata
20. Success notification shown

**API:**
```typescript
class TemplateCaptureService {
    /**
     * Start template capture flow
     */
    async startCapture(): Promise<void> {
        // IPC call to main process
        await window.electron.ipcRenderer.invoke('overlay:show');
    }
    
    /**
     * Save template (called by main process after capture)
     */
    async saveTemplate(template: TemplateData): Promise<string> {
        // ... save logic ...
    }
}
```

---

### **6. Template Capture Service**

**Challenge:** Overlay must work across multiple displays

**Solution:**
```javascript
const { screen } = require('electron');

function createOverlayWindow() {
    // Get all displays
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
    
    // Create overlay covering all displays
    const overlayWindow = new BrowserWindow({
        width: maxX - minX,
        height: maxY - minY,
        x: minX,
        y: minY,
        // ... other options ...
    });
}
```

---

### **7. Multi-Display Support**

**Challenge:** Rectangle coordinates from overlay need to map to screenshot coordinates

**Solution:** Store display information with screenshot

```javascript
async captureScreenForSelection() {
    const displays = screen.getAllDisplays();
    const primaryDisplay = screen.getPrimaryDisplay();
    
    const sources = await desktopCapturer.getSources({
        types: ['screen'],
        thumbnailSize: {
            width: primaryDisplay.size.width,
            height: primaryDisplay.size.height
        }
    });
    
    // Store display info for coordinate mapping
    return {
        screenshot: sources[0].thumbnail.toPNG(),
        displayInfo: {
            primaryDisplay: primaryDisplay.bounds,
            allDisplays: displays.map(d => d.bounds)
        }
    };
}
```

---

### **8. Coordinate Mapping**

**Complete User Flow:**

1. **User clicks "Capture Template"** in Electron app
   - Button in Macro Automation settings
   - Or keyboard shortcut (e.g., Ctrl+Shift+T)

2. **System manages Cursor window**
   - Checks if Cursor is open
   - Opens Cursor if not open
   - Restores Cursor if minimized
   - Brings Cursor to front

3. **Overlay window appears**
   - Transparent, dimmed background
   - Covers all displays
   - Instructions shown: "Click and drag to select area"
   - NO screenshot taken yet

4. **User draws rectangle**
   - Click and drag over Cursor window/element
   - Rectangle visible in real-time
   - Coordinates shown
   - Magnifier follows cursor (optional)

5. **User releases mouse**
   - Rectangle finalized
   - Preview shown (optional)
   - "Press Enter to capture, ESC to cancel"

6. **User presses Enter/clicks Accept**
   - Rectangle coordinates sent to main process
   - Overlay window closes/hides immediately

7. **System captures screenshot**
   - Small delay (100ms) for overlay to fully close
   - Full screen screenshot captured
   - Selected region cropped from screenshot

8. **System minimizes Cursor**
   - Cursor window minimized
   - Electron app window brought to front

9. **Electron app shows result**
   - `CaptureResult` component displayed
   - Thumbnail preview shown
   - Coordinates displayed (x, y, width, height)
   - Template name input field
   - Theme selection dropdown

10. **User enters template metadata**
    - Template name (e.g., "Stop Button")
    - Theme selection (Light/Dark/Hover)
    - Clicks Save button

11. **Template saved**
    - File saved to `templates/` directory
    - Metadata saved
    - Success notification shown

---

### **9. Result Display Component**

**Location:** `packages/ide_chat_app/src/components/CaptureResult.tsx`

**Purpose:** Display thumbnail and coordinates after capture

**Features:**
- Thumbnail preview of captured region
- Coordinate display (x, y, width, height)
- Template name input
- Theme selection (Light/Dark/Hover)
- Save/Cancel buttons

**Props:**
```typescript
interface CaptureResultProps {
    thumbnail: Buffer | string;  // Base64 or Buffer
    rectangle: Rectangle;
    onSave: (metadata: TemplateMetadata) => void;
    onCancel: () => void;
}
```

**Component:**
```typescript
const CaptureResult: React.FC<CaptureResultProps> = ({ 
    thumbnail, 
    rectangle, 
    onSave, 
    onCancel 
}) => {
    const [templateName, setTemplateName] = useState('');
    const [theme, setTheme] = useState<'light' | 'dark' | 'hover'>('light');
    
    return (
        <div className="capture-result">
            <h2>Template Captured</h2>
            
            <div className="thumbnail-preview">
                <img src={`data:image/png;base64,${thumbnail}`} alt="Template preview" />
            </div>
            
            <div className="coordinates">
                <p>X: {rectangle.x}</p>
                <p>Y: {rectangle.y}</p>
                <p>Width: {rectangle.width}</p>
                <p>Height: {rectangle.height}</p>
            </div>
            
            <div className="metadata-form">
                <input
                    type="text"
                    placeholder="Template name"
                    value={templateName}
                    onChange={(e) => setTemplateName(e.target.value)}
                />
                
                <select value={theme} onChange={(e) => setTheme(e.target.value as any)}>
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="hover">Hover</option>
                </select>
                
                <div className="actions">
                    <button onClick={onCancel}>Cancel</button>
                    <button onClick={() => onSave({ templateName, theme, rectangle })}>
                        Save Template
                    </button>
                </div>
            </div>
        </div>
    );
};
```

---

### **10. User Experience Flow**

**During Overlay:**
- **ESC:** Cancel capture
- **Enter:** Confirm selection
- **Arrow keys:** Fine-tune rectangle (if implemented)
- **Space:** Toggle magnifier

**Global:**
- **Ctrl+Shift+T:** Start template capture (from anywhere)

---

### **12. Visual Design**

**Overlay Appearance:**
- **Background:** Semi-transparent black (`rgba(0, 0, 0, 0.5)`)
- **Selected region:** Brightened (less dimmed)
- **Rectangle border:** Bright cyan (`#00ffff`) or green (`#00ff00`)
- **Rectangle fill:** Semi-transparent (`rgba(0, 255, 255, 0.2)`)
- **Instructions:** Top-left corner, white text
- **Coordinates:** Bottom-right corner, small font

**Example:**
```
┌─────────────────────────────────────────────────┐
│ Instructions: Click and drag to select area     │
│                                                 │
│    [Dimmed background]                         │
│                                                 │
│        ┌─────────────────┐                    │
│        │                 │                    │
│        │  [Brightened]  │                    │
│        │  [Rectangle]   │                    │
│        │                 │                    │
│        └─────────────────┘                    │
│                                                 │
│                           Coordinates: 1250x850 │
└─────────────────────────────────────────────────┘
```

---

---

### **2. Template Capture Service**

**Location:** `packages/ide_chat_app/src/services/templateCaptureService.ts`

**Purpose:** Core logic for capturing and managing templates

**Responsibilities:**
- Capture screenshots of selected regions
- Save templates with metadata
- Load templates for matching
- Validate template quality
- Manage template storage

**API:**
```typescript
class TemplateCaptureService {
    /**
     * Capture template from rectangle selection
     */
    async captureTemplate(
        rectangle: Rectangle,
        metadata: TemplateMetadata
    ): Promise<TemplateData>;
    
    /**
     * Save template to disk
     */
    async saveTemplate(template: TemplateData): Promise<string>;
    
    /**
     * Load template from disk
     */
    async loadTemplate(templateId: string): Promise<TemplateData>;
    
    /**
     * List all templates
     */
    async listTemplates(): Promise<TemplateMetadata[]>;
    
    /**
     * Delete template
     */
    async deleteTemplate(templateId: string): Promise<void>;
    
    /**
     * Validate template quality (check dimensions, contrast, etc.)
     */
    async validateTemplate(template: TemplateData): Promise<ValidationResult>;
}
```

**Template Data Structure:**
```typescript
interface TemplateData {
    id: string;                    // Unique identifier
    name: string;                  // User-friendly name
    description?: string;          // Optional description
    theme: 'light' | 'dark' | 'hover';
    rectangle: Rectangle;         // Original selection coordinates
    imageData: Buffer;             // PNG image buffer
    screenshotBounds: Rectangle;   // Full screenshot bounds
    createdAt: Date;
    updatedAt: Date;
    metadata: {
        cursorVersion?: string;    // Cursor version when captured
        os?: string;               // Operating system
        dpi?: number;              // Screen DPI
        windowTitle?: string;      // Window title
    };
}
```

**Template Storage:**
```
templates/
├── stop-button/
│   ├── light.png
│   ├── dark.png
│   ├── hover.png
│   └── metadata.json
├── send-button/
│   ├── light.png
│   ├── dark.png
│   └── metadata.json
└── templates-index.json  // Master index
```

**Metadata JSON:**
```json
{
  "id": "stop-button-light",
  "name": "Stop Button - Light Theme",
  "theme": "light",
  "rectangle": {
    "x": 1250,
    "y": 850,
    "width": 60,
    "height": 30
  },
  "screenshotBounds": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  },
  "metadata": {
    "cursorVersion": "0.40.0",
    "os": "win32",
    "dpi": 96,
    "windowTitle": "Cursor"
  },
  "createdAt": "2025-11-02T13:00:00Z"
}
```

---

### **3. Screenshot Capture**

**Location:** `packages/ide_chat_app/src/services/screenshotService.ts`

**Purpose:** Capture screenshots using Electron's desktopCapturer API

**API:**
```typescript
class ScreenshotService {
    /**
     * Capture full screen
     */
    async captureScreen(): Promise<Buffer>;
    
    /**
     * Capture specific window by name
     */
    async captureWindow(windowName: string): Promise<Buffer>;
    
    /**
     * Capture region from existing screenshot
     */
    async captureRegion(
        screenshot: Buffer,
        rectangle: Rectangle
    ): Promise<Buffer>;
    
    /**
     * List available windows
     */
    async listWindows(): Promise<WindowInfo[]>;
}
```

**Window Detection:**
```typescript
interface WindowInfo {
    id: string;
    name: string;
    thumbnail: Buffer;
    bounds: Rectangle;
}
```

**Implementation:**
```typescript
import { desktopCapturer } from 'electron';

class ScreenshotService {
    async captureScreen(): Promise<Buffer> {
        const sources = await desktopCapturer.getSources({
            types: ['screen'],
            thumbnailSize: { width: 1920, height: 1080 }
        });
        
        if (sources.length === 0) {
            throw new Error('No screen sources available');
        }
        
        // Return primary screen
        return sources[0].thumbnail.toPNG();
    }
    
    async captureWindow(windowName: string): Promise<Buffer> {
        const sources = await desktopCapturer.getSources({
            types: ['window'],
            thumbnailSize: { width: 1920, height: 1080 }
        });
        
        const targetWindow = sources.find(s => 
            s.name.toLowerCase().includes(windowName.toLowerCase())
        );
        
        if (!targetWindow) {
            throw new Error(`Window "${windowName}" not found`);
        }
        
        return targetWindow.thumbnail.toPNG();
    }
    
    async captureRegion(
        screenshot: Buffer,
        rectangle: Rectangle
    ): Promise<Buffer> {
        // Use sharp or jimp for image processing
        const sharp = require('sharp');
        
        return await sharp(screenshot)
            .extract({
                left: rectangle.x,
                top: rectangle.y,
                width: rectangle.width,
                height: rectangle.height
            })
            .png()
            .toBuffer();
    }
}
```

---

### **4. Rectangle Drawing Component**

**Location:** `packages/ide_chat_app/src/components/RectangleSelector.tsx`

**Purpose:** Canvas-based rectangle drawing tool

**Features:**
- Click and drag to draw rectangle
- Visual feedback (border, fill, resize handles)
- Snap-to-grid option
- Zoom/pan controls
- Min/max size validation

**Props:**
```typescript
interface RectangleSelectorProps {
    screenshot: Buffer;
    onSelect: (rectangle: Rectangle) => void;
    onCancel: () => void;
    minSize?: { width: number; height: number };
    maxSize?: { width: number; height: number };
    snapToGrid?: boolean;
    gridSize?: number;
}
```

**State:**
```typescript
interface RectangleSelectorState {
    isDrawing: boolean;
    startPoint: { x: number; y: number } | null;
    currentRectangle: Rectangle | null;
    zoomLevel: number;
    panOffset: { x: number; y: number };
}
```

**Drawing Logic:**
```typescript
const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = (e.clientX - rect.left) / zoomLevel - panOffset.x;
    const y = (e.clientY - rect.top) / zoomLevel - panOffset.y;
    
    setStartPoint({ x, y });
    setIsDrawing(true);
};

const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !startPoint) return;
    
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const currentX = (e.clientX - rect.left) / zoomLevel - panOffset.x;
    const currentY = (e.clientY - rect.top) / zoomLevel - panOffset.y;
    
    const rectangle: Rectangle = {
        x: Math.min(startPoint.x, currentX),
        y: Math.min(startPoint.y, currentY),
        width: Math.abs(currentX - startPoint.x),
        height: Math.abs(currentY - startPoint.y)
    };
    
    setCurrentRectangle(rectangle);
    drawRectangle(rectangle);
};

const handleMouseUp = () => {
    if (currentRectangle) {
        onSelect(currentRectangle);
    }
    setIsDrawing(false);
    setStartPoint(null);
};
```

---

### **5. Template Management UI**

**Location:** `packages/ide_chat_app/src/components/TemplateManager.tsx`

**Purpose:** UI for managing templates (view, edit, delete)

**Features:**
- List all templates
- Preview templates
- Edit template metadata
- Delete templates
- Test template matching

**UI Components:**
- Template list with thumbnails
- Template preview modal
- Edit template dialog
- Delete confirmation dialog

---

### **6. Integration with Vision Detection**

**Location:** `packages/ide_chat_app/src/services/visionService.ts`

**Purpose:** Use captured templates for pixel matching

**Updated API:**
```typescript
class VisionService {
    private templates: Map<string, TemplateData> = new Map();
    
    /**
     * Initialize - load all templates
     */
    async initialize(): Promise<void> {
        const templateService = new TemplateCaptureService();
        const templates = await templateService.listTemplates();
        
        for (const metadata of templates) {
            const template = await templateService.loadTemplate(metadata.id);
            this.templates.set(template.id, template);
        }
    }
    
    /**
     * Check if button is visible using templates
     */
    async isButtonVisible(buttonName: string): Promise<boolean> {
        const screenshot = await this.captureScreen();
        
        // Try all theme variants
        const variants = ['light', 'dark', 'hover'];
        for (const theme of variants) {
            const templateId = `${buttonName}-${theme}`;
            const template = this.templates.get(templateId);
            
            if (!template) continue;
            
            const match = await this.templateMatch(
                screenshot,
                template.imageData,
                template.rectangle
            );
            
            if (match.confidence > 0.85) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Template matching algorithm
     */
    private async templateMatch(
        screenshot: Buffer,
        template: Buffer,
        expectedRegion: Rectangle
    ): Promise<{ confidence: number; location?: Rectangle }> {
        // Use opencv4nodejs or sharp for template matching
        // Simplified for documentation
        return { confidence: 0.0 };
    }
}
```

---

## 🔄 **COMPLETE USER FLOW**

### **Step 1: Capture Template**

1. User opens Electron app
2. Navigates to "Macro Automation" → "Template Capture"
3. Clicks "Capture New Template"
4. Screen overlay appears (dimmed)
5. User sees Cursor window in background
6. User clicks and drags rectangle over "Stop" button
7. Rectangle preview appears
8. User releases mouse
9. Preview shows selected region (zoomed)
10. User enters template name: "Stop Button"
11. User selects theme: "Dark"
12. User clicks "Save Template"
13. Template saved to `templates/stop-button/dark.png`
14. Metadata saved to `templates/stop-button/metadata.json`
15. Overlay disappears

### **Step 2: Use Template**

1. Vision detection service loads templates on startup
2. Supervisor calls `visionService.isButtonVisible('stop-button')`
3. Service captures screenshot
4. Service tries matching against all theme variants
5. If match found (confidence > 0.85) → returns `true`
6. Supervisor uses result to decide if Cursor is busy

---

## 🎨 **UI/UX DESIGN**

### **Template Capture Modal**

```
┌─────────────────────────────────────────────────┐
│  Capture Template                        [×]   │
├─────────────────────────────────────────────────┤
│                                                 │
│  [Screenshot Preview - Dimmed]                 │
│                                                 │
│  ┌─────────────────────────────┐              │
│  │                             │              │
│  │    [Selected Rectangle]     │              │
│  │                             │              │
│  └─────────────────────────────┘              │
│                                                 │
│  Template Name: [Stop Button        ]          │
│  Theme:        [Dark ▼]                       │
│                                                 │
│  [Cancel]              [Save Template]        │
└─────────────────────────────────────────────────┘
```

### **Template Manager**

```
┌─────────────────────────────────────────────────┐
│  Template Manager                        [+ New]│
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────────┐  ┌────────────┐               │
│  │ [Preview] │  │ [Preview] │               │
│  │            │  │            │               │
│  │ Stop Light │  │ Stop Dark  │               │
│  │ [Edit][×]  │  │ [Edit][×]  │               │
│  └────────────┘  └────────────┘               │
│                                                 │
│  ┌────────────┐                                │
│  │ [Preview] │                                │
│  │            │                                │
│  │ Send Light │                                │
│  │ [Edit][×]  │                                │
│  └────────────┘                                │
└─────────────────────────────────────────────────┘
```

---

## 🔧 **TECHNICAL IMPLEMENTATION DETAILS**

### **Dependencies**

```json
{
  "dependencies": {
    "sharp": "^0.33.0",           // Image processing
    "opencv4nodejs": "^5.6.0",   // Template matching (optional)
    "electron": "^28.0.0"         // Desktop capture
  }
}
```

### **File Structure**

```
packages/ide_chat_app/
├── src/
│   ├── components/
│   │   ├── TemplateCapture.tsx
│   │   ├── RectangleSelector.tsx
│   │   └── TemplateManager.tsx
│   ├── services/
│   │   ├── templateCaptureService.ts
│   │   ├── screenshotService.ts
│   │   └── visionService.ts (updated)
│   └── types/
│       └── template.ts
├── templates/
│   ├── stop-button/
│   │   ├── light.png
│   │   ├── dark.png
│   │   ├── hover.png
│   │   └── metadata.json
│   └── templates-index.json
└── electron/
    └── main.js (desktopCapturer API)
```

### **Electron Main Process**

```typescript
// electron/main.js
import { desktopCapturer, app } from 'electron';

// Expose screenshot capture to renderer
ipcMain.handle('capture-screen', async () => {
    const sources = await desktopCapturer.getSources({
        types: ['screen'],
        thumbnailSize: { width: 1920, height: 1080 }
    });
    
    return sources[0].thumbnail.toPNG();
});

ipcMain.handle('capture-window', async (event, windowName: string) => {
    const sources = await desktopCapturer.getSources({
        types: ['window'],
        thumbnailSize: { width: 1920, height: 1080 }
    });
    
    const target = sources.find(s => 
        s.name.toLowerCase().includes(windowName.toLowerCase())
    );
    
    return target?.thumbnail.toPNG() || null;
});
```

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests**

1. **TemplateCaptureService**
   - Test template save/load
   - Test metadata persistence
   - Test template validation

2. **ScreenshotService**
   - Test screen capture
   - Test window detection
   - Test region extraction

3. **RectangleSelector**
   - Test rectangle drawing
   - Test coordinate calculation
   - Test zoom/pan

### **Integration Tests**

1. **End-to-End Capture Flow**
   - Capture template → Save → Load → Match

2. **Vision Detection Integration**
   - Load templates → Capture screenshot → Match → Result

### **Manual Testing**

1. **User Flow**
   - Open capture UI
   - Draw rectangle
   - Save template
   - Verify file creation
   - Test template matching

---

## 📊 **ERROR HANDLING**

### **Capture Errors**

- **No screen access:** Prompt user for permissions
- **Window not found:** Show available windows list
- **Invalid rectangle:** Validate min/max size
- **Save failure:** Show error, retry option

### **Matching Errors**

- **Template not found:** Log warning, skip variant
- **Low confidence:** Log warning, try next variant
- **Screenshot failure:** Return `false` (assume not visible)

---

## 🚀 **IMPLEMENTATION PHASES**

### **Phase 1: Core Capture**
- [ ] ScreenshotService (screen/window capture)
- [ ] RectangleSelector component
- [ ] TemplateCaptureService (save/load)

### **Phase 2: UI Components**
- [ ] TemplateCapture modal
- [ ] TemplateManager component
- [ ] Integration with Electron app

### **Phase 3: Vision Integration**
- [ ] Update VisionService to use templates
- [ ] Template matching algorithm
- [ ] Multi-variant matching

### **Phase 4: Polish**
- [ ] Error handling
- [ ] Validation
- [ ] Testing
- [ ] Documentation

---

## 📝 **DOCUMENTATION REQUIREMENTS**

### **User Documentation**
- How to capture templates
- How to manage templates
- How templates are used
- Troubleshooting guide

### **Developer Documentation**
- API reference
- Component props
- Service interfaces
- Extension points

---

## ✅ **ACCEPTANCE CRITERIA**

1. ✅ User can draw rectangle over UI button
2. ✅ Template is captured and saved
3. ✅ Template metadata is stored
4. ✅ Templates can be loaded and used for matching
5. ✅ Multi-theme variants are supported
6. ✅ UI is intuitive and responsive
7. ✅ Error handling is comprehensive
8. ✅ Tests are written and passing

---

**Status:** Design complete - Ready for implementation  
**Confidence:** 0.90 (high - well-defined requirements)  
**Next:** Implementation Phase 1 - Core Capture

