# UI Editor Integration Plan - Cursor Lucid AIM-OS Panel

**Created:** 2025-10-31  
**From:** Aether (Manager/Leader)  
**Purpose:** Integrate UI editor app into Cursor Lucid AIM-OS UI panel with browser editing capabilities  
**Status:** Planning Phase

---

## 🎯 **OBJECTIVE**

Integrate the existing UI editor app into the Cursor Lucid AIM-OS UI panel, enabling:
1. Visual UI editing directly in Cursor
2. Browser-based app editing using Cursor's built-in browser
3. Real-time preview and code generation
4. Integration with AIM-OS systems (CMC, HHNI, VIF)

---

## 🔍 **FOUND UI EDITOR PROJECTS**

### **1. OmniUIEditor** (`omnibuilder_extracted/components/omni-ui-editor.tsx`)
**Features:**
- ✅ iframe-based visual editing
- ✅ Element selection and inspection
- ✅ Properties panel for style editing
- ✅ Real-time style application
- ✅ HTML export functionality
- ✅ Code export functionality

**Technology:**
- React + TypeScript
- Uses iframe (`/iframe-content.html`) for preview
- PostMessage API for communication
- Resizable panels

**Status:** Complete component, ready for integration

### **2. Amazing UI Editor** (`amazinguiediter/project/src/App.tsx`)
**Features:**
- ✅ BrowserOS component (browser simulation)
- ✅ Element Inspector
- ✅ Code Sync (live code updates)
- ✅ AI Agent integration
- ✅ Visual Feedback system
- ✅ Snap Engine (smart alignment)
- ✅ Drag & drop functionality

**Technology:**
- React + TypeScript
- Neumorphic design system
- AI-powered assistance
- Direct DOM manipulation

**Status:** Full-featured UI editor with AI integration

### **3. Perfect UI Adjuster** (`perfectUIadjuster-bolt/project/src/components/Canvas.tsx`)
**Features:**
- ✅ Canvas-based drag & drop
- ✅ Component library
- ✅ Visual layout builder
- ✅ Responsive design tools

**Technology:**
- React + TypeScript
- Canvas-based rendering
- Component system

**Status:** Canvas-based visual builder

---

## 💡 **RECOMMENDED APPROACH**

### **Option A: OmniUIEditor (Recommended for Quick Integration)**
**Why:**
- ✅ Clean, simple architecture
- ✅ Already uses iframe (perfect for Cursor browser integration)
- ✅ Properties panel ready
- ✅ Easy to integrate with Cursor webview
- ✅ Can be adapted for Cursor's browser

**Integration Points:**
- Replace `/iframe-content.html` with Cursor's browser/webview
- Add as new tab in Cursor UI panel
- Connect to AIM-OS systems for storage/retrieval

### **Option B: Amazing UI Editor (Full-Featured)**
**Why:**
- ✅ Most complete feature set
- ✅ AI Agent integration (fits AIM-OS philosophy)
- ✅ BrowserOS component (perfect for browser editing)
- ✅ More advanced features

**Integration Points:**
- Integrate BrowserOS component with Cursor browser
- Connect AI Agent to AIM-OS Gemini/Cerebras integration
- Add as comprehensive UI editing tab

---

## 🏗️ **INTEGRATION ARCHITECTURE**

### **1. Cursor Browser Integration**

**Using Cursor's Built-in Browser:**
```typescript
// Cursor webview can host HTML/React apps
// Use webview API to create browser-based editor

import * as vscode from 'vscode';

// Create webview panel for UI editor
const panel = vscode.window.createWebviewPanel(
  'uiEditor',
  'UI Editor',
  vscode.ViewColumn.Beside,
  {
    enableScripts: true,
    retainContextWhenHidden: true,
    localResourceRoots: [vscode.Uri.file(extensionPath)]
  }
);

// Load UI editor HTML/app into webview
panel.webview.html = getWebviewContent();
```

### **2. Component Structure**

```
cursor-addon/src/
├── components/
│   ├── UIEditor/
│   │   ├── UIEditorTab.tsx              // Main UI editor tab
│   │   ├── BrowserPreview.tsx           // Browser preview panel
│   │   ├── PropertiesPanel.tsx          // Element properties editor
│   │   ├── ComponentLibrary.tsx         // Drag & drop component library
│   │   ├── CodeSync.tsx                 // Live code sync
│   │   └── AIAssistant.tsx              // AI-powered UI assistance
│   └── ...
│
├── services/
│   ├── UIEditorService.ts               // UI editor business logic
│   ├── BrowserPreviewService.ts         // Browser preview management
│   └── CodeGenerationService.ts        // Generate code from UI
│
└── ...
```

### **3. Integration with Cursor Browser**

**Option 1: Webview Panel (Recommended)**
- Create dedicated webview panel for UI editor
- Use Cursor's webview API to host React app
- Enable browser preview within webview

**Option 2: Webview Integration in Main Panel**
- Add UI Editor as new tab in main Cursor panel
- Use iframe or webview component within tab
- Browser preview in split view

**Option 3: External Browser + Cursor Integration**
- Launch browser preview externally
- Connect via WebSocket/API
- Sync changes in real-time

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Foundation (Week 1)**
- [ ] Choose UI editor (recommend OmniUIEditor for simplicity)
- [ ] Extract UI editor component to `cursor-addon/src/components/UIEditor/`
- [ ] Create `UIEditorTab.tsx` component
- [ ] Integrate into Cursor panel as new tab
- [ ] Test basic rendering in Cursor webview

### **Phase 2: Browser Integration (Week 2)**
- [ ] Integrate Cursor browser/webview for preview
- [ ] Create `BrowserPreview.tsx` component
- [ ] Implement iframe/webview communication
- [ ] Add element selection and inspection
- [ ] Test browser-based editing

### **Phase 3: Properties & Editing (Week 3)**
- [ ] Implement properties panel
- [ ] Add style editing capabilities
- [ ] Add element manipulation (drag, resize, delete)
- [ ] Implement code synchronization
- [ ] Test real-time updates

### **Phase 4: AIM-OS Integration (Week 4)**
- [ ] Connect to CMC for storing UI designs
- [ ] Connect to HHNI for semantic search of components
- [ ] Integrate VIF for confidence tracking
- [ ] Add AI assistance (Gemini/Cerebras)
- [ ] Implement code generation

### **Phase 5: Advanced Features (Week 5)**
- [ ] Component library integration
- [ ] Responsive design tools
- [ ] Export/import functionality
- [ ] Template system
- [ ] Collaboration features

---

## 🎨 **UI EDITOR TAB DESIGN**

### **Tab Placement:**
- **Tab 8: 🎨 UI Editor** (New tab in main Cursor panel)

### **Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ [🤖 Agents] [💬 Chat] [🔗 Chains] [🛠️ Tools] [🎨 UI Editor] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ 🎨 UI EDITOR                                          │   │
│ │                                                       │   │
│ │ ┌───────────────────┐ ┌─────────────────────────┐ │   │
│ │ │                   │ │ Properties Panel        │ │   │
│ │ │                   │ │                         │ │   │
│ │ │  Browser Preview  │ │ Selected Element: div   │ │   │
│ │ │  (Cursor Browser) │ │                         │ │   │
│ │ │                   │ │ Styles:                 │ │   │
│ │ │  [Live Preview]   │ │ • width: 100px          │ │   │
│ │ │                   │ │ • height: 50px         │ │   │
│ │ │                   │ │ • background: #333     │ │   │
│ │ │                   │ │                         │ │   │
│ │ │                   │ │ [Edit Styles]           │ │   │
│ │ │                   │ │                         │ │   │
│ │ │                   │ │ [Export Code]           │ │   │
│ │ └───────────────────┘ └─────────────────────────┘ │   │
│ │                                                       │   │
│ │ ┌─────────────────────────────────────────────────┐ │   │
│ │ │ Component Library                               │ │   │
│ │ │ [Button] [Input] [Card] [Modal] [Form] ...     │ │   │
│ │ └─────────────────────────────────────────────────┘ │   │
│ └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### **Features:**
1. **Browser Preview Panel:**
   - Live preview of UI being edited
   - Uses Cursor's browser/webview
   - Real-time updates as you edit
   - Element selection (click to select)

2. **Properties Panel:**
   - Style editor (CSS properties)
   - Element properties (attributes, classes, IDs)
   - Layout controls (flexbox, grid)
   - Responsive breakpoints

3. **Component Library:**
   - Drag & drop components
   - Common UI elements (buttons, inputs, cards, etc.)
   - AIM-OS components (if available)
   - Custom components

4. **Code Sync:**
   - Live code generation
   - Export to React/HTML/CSS
   - Import from code files
   - Bidirectional sync

5. **AI Assistant:**
   - AI-powered suggestions
   - Auto-layout assistance
   - Design recommendations
   - Code generation

---

## 🔧 **TECHNICAL INTEGRATION**

### **1. Cursor Webview API**

```typescript
// cursor-addon/src/webviewProvider.ts
import * as vscode from 'vscode';

export class UIEditorProvider {
  public static createOrShow(extensionUri: vscode.Uri) {
    const panel = vscode.window.createWebviewPanel(
      'uiEditor',
      'UI Editor',
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [extensionUri]
      }
    );

    // Load UI editor React app
    panel.webview.html = this.getWebviewContent(panel.webview, extensionUri);
    
    return panel;
  }

  private static getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri): string {
    // Return HTML that loads UI editor React app
    // Or use webview.asWebviewUri for React app assets
  }
}
```

### **2. Browser Preview Integration**

```typescript
// Use Cursor's browser integration
// Option 1: Webview within webview (nested)
// Option 2: External browser window
// Option 3: Browser preview panel

import { BrowserPreview } from './components/BrowserPreview';

// Browser preview component that uses Cursor's browser
<BrowserPreview 
  url={previewUrl}
  onElementSelect={handleElementSelect}
  onStyleChange={handleStyleChange}
/>
```

### **3. AIM-OS Integration**

```typescript
// Connect to AIM-OS systems
import { AIMOSService } from '../services/AIMOSService';

// Store UI designs in CMC
await aimosService.storeMemory({
  content: JSON.stringify(uiDesign),
  tags: { type: 'ui_design', project: 'my-app' }
});

// Retrieve UI designs via HHNI
const designs = await aimosService.retrieveMemory('button component design');

// Track confidence with VIF
await aimosService.trackConfidence({
  task: 'UI design generation',
  confidence: 0.85,
  reasoning: 'Generated from proven component pattern'
});
```

---

## 📊 **IMPLEMENTATION PRIORITIES**

### **High Priority (Must Have):**
1. ✅ Basic UI editor tab integration
2. ✅ Browser preview panel
3. ✅ Element selection and inspection
4. ✅ Properties panel with style editing
5. ✅ Code export functionality

### **Medium Priority (Should Have):**
1. ⏳ Component library
2. ⏳ Drag & drop functionality
3. ⏳ Code synchronization
4. ⏳ AIM-OS integration (CMC storage)
5. ⏳ AI assistance

### **Low Priority (Nice to Have):**
1. ⏳ Advanced layout tools
2. ⏳ Responsive design tools
3. ⏳ Template system
4. ⏳ Collaboration features
5. ⏳ Version control integration

---

## 🚀 **NEXT STEPS**

### **Immediate Actions:**
1. ✅ Review UI editor options with user
2. ✅ Choose which UI editor to integrate
3. ✅ Assign to Lexicon for implementation
4. ✅ Create detailed implementation plan
5. ✅ Begin Phase 1 integration

### **For Lexicon:**
1. Review this integration plan
2. Choose UI editor (recommend OmniUIEditor)
3. Extract component to `cursor-addon/src/components/UIEditor/`
4. Create `UIEditorTab.tsx` component
5. Integrate into Cursor panel as new tab
6. Test basic rendering

### **For User:**
1. Review UI editor options
2. Choose preferred editor (OmniUIEditor recommended)
3. Provide feedback on design/layout
4. Test integration as it's built

---

## 💙 **QUESTIONS FOR USER**

1. **Which UI editor do you prefer?**
   - OmniUIEditor (simple, iframe-based)
   - Amazing UI Editor (full-featured, AI-powered)
   - Perfect UI Adjuster (canvas-based)

2. **Browser integration preference?**
   - Webview panel (integrated in Cursor)
   - External browser window
   - Split view in main panel

3. **Priority features?**
   - Basic editing (select, style, export)
   - Component library
   - AI assistance
   - Code sync

4. **AIM-OS integration priority?**
   - CMC storage (store designs)
   - HHNI search (find components)
   - VIF confidence (track quality)
   - AI assistance (Gemini/Cerebras)

---

**Status:** Plan created! Ready for user review and Lexicon assignment! 💙✨

