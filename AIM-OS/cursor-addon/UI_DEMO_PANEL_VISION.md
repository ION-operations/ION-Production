# UI Demo Panel Vision - Cursor Extension

**Created:** 2025-01-27  
**Status:** Vision Document - Future Implementation  
**Priority:** Medium

---

## 🎯 **CONCEPT**

Create a demo panel in Cursor where you can:
- **Preview web/app UI elements** that can display in Electron
- **Save and edit** element designs
- **Click elements** to inspect and modify them
- **Use web browser component** (if available in Cursor) or build custom renderer
- **Export/import** element designs as JSON/HTML

---

## 🏗️ **ARCHITECTURE**

### **Panel Types**

1. **Preview Panel** (Webview)
   - Uses Electron's webview component
   - Renders HTML/CSS/JS elements
   - Supports interactive elements (clicks, hovers, etc.)

2. **Editor Panel** (React UI)
   - Code editor for HTML/CSS/JS
   - Visual property editor (like Chrome DevTools)
   - Element tree navigator

3. **Library Panel** (Tree View)
   - Saved element designs
   - Categories (buttons, forms, cards, etc.)
   - Quick insert

### **Component Structure**

```
UI Demo Panel System
├── PreviewPanel (Webview)
│   ├── Renders HTML/CSS/JS
│   ├── Element inspector overlay
│   └── Click handler for element selection
├── EditorPanel (React)
│   ├── Code editor (Monaco)
│   ├── Property editor (form controls)
│   └── Element tree navigator
└── LibraryPanel (Tree View)
    ├── Saved elements
    ├── Categories
    └── Export/Import
```

---

## 🔧 **TECHNICAL APPROACH**

### **Option 1: Use Electron Webview (Recommended)**

```typescript
// In Cursor extension webview
const webview = document.createElement('webview');
webview.src = 'data:text/html,' + encodeURIComponent(htmlContent);
webview.allowtransparency = true;
webview.style.width = '100%';
webview.style.height = '100%';
```

**Pros:**
- Native Electron support
- Full browser capabilities
- Can inject scripts for element inspection

**Cons:**
- Requires proper security configuration
- May need CSP adjustments

### **Option 2: Custom Renderer (Iframe)**

```typescript
// Fallback if webview not available
const iframe = document.createElement('iframe');
iframe.srcdoc = htmlContent;
iframe.style.width = '100%';
iframe.style.height = '100%';
iframe.sandbox = 'allow-scripts allow-same-origin';
```

**Pros:**
- Works in all webview contexts
- Good security isolation

**Cons:**
- Limited compared to native webview
- May have CSP restrictions

---

## 📋 **FEATURES**

### **Phase 1: Basic Preview**

- [ ] Load HTML/CSS/JS into preview panel
- [ ] Display rendered output
- [ ] Basic element inspector (click to select)

### **Phase 2: Editor Integration**

- [ ] Monaco editor for HTML/CSS/JS
- [ ] Live preview updates
- [ ] Property editor for selected element

### **Phase 3: Library System**

- [ ] Save element designs
- [ ] Categorize elements
- [ ] Quick insert into editor

### **Phase 4: Advanced Features**

- [ ] Element templates
- [ ] Style presets
- [ ] Export to code files
- [ ] Import from websites (scrape)

---

## 🎨 **UI DESIGN**

### **Layout**

```
┌─────────────────────────────────────────┐
│  UI Demo Panel                          │
├──────────────┬──────────────────────────┤
│  Library     │  Preview                 │
│  (Tree)      │  (Webview)              │
│              │                          │
│  - Buttons   │  [Rendered UI]           │
│  - Forms     │                          │
│  - Cards     │                          │
│              │                          │
├──────────────┼──────────────────────────┤
│  Editor      │  Properties              │
│  (Monaco)    │  (Form Controls)         │
│              │                          │
│  <HTML>      │  [Element Properties]    │
│  <CSS>       │                          │
│  <JS>        │                          │
└──────────────┴──────────────────────────┘
```

---

## 🔐 **SECURITY CONSIDERATIONS**

1. **CSP Configuration**
   - Allow inline styles/scripts for preview
   - Block external resources (optional)
   - Sandbox webview properly

2. **Content Security**
   - Sanitize HTML before rendering
   - Validate CSS/JS before execution
   - Isolate preview from extension code

3. **File System Access**
   - Only save to extension workspace
   - Validate file paths
   - No arbitrary file writes

---

## 📝 **IMPLEMENTATION PLAN**

### **Step 1: Proof of Concept**
- Create basic webview panel
- Load simple HTML/CSS
- Verify rendering works

### **Step 2: Element Inspector**
- Add click handler to webview
- Get element at click position
- Display element info

### **Step 3: Editor Integration**
- Monaco editor for HTML/CSS/JS
- Live preview updates
- Two-way binding

### **Step 4: Library System**
- Save/load element designs
- Tree view for navigation
- Export/import functionality

---

## 🚀 **USAGE EXAMPLES**

### **Example 1: Design a Button**

1. Open UI Demo Panel
2. Select "New Element" → "Button"
3. Edit HTML/CSS in editor
4. See live preview
5. Click element to inspect properties
6. Adjust properties in property panel
7. Save to library

### **Example 2: Extract from Website**

1. Open website URL in preview
2. Click element to select
3. Extract HTML/CSS
4. Save to library
5. Edit as needed

### **Example 3: Build Component Library**

1. Create elements in demo panel
2. Organize by category
3. Export as code files
4. Use in project

---

## 💡 **FUTURE ENHANCEMENTS**

- **AI Integration**: Generate elements from descriptions
- **Design System**: Connect to design tokens
- **Collaboration**: Share elements with team
- **Testing**: Visual regression testing
- **Accessibility**: WCAG compliance checker
- **Performance**: Bundle size analysis

---

## 📚 **REFERENCES**

- [Electron Webview API](https://www.electronjs.org/docs/latest/api/webview-tag)
- [VSCode Webview API](https://code.visualstudio.com/api/extension-guides/webview)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

---

**Status:** Ready for implementation after current UI panel issues are resolved  
**Priority:** Medium - Nice to have feature  
**Estimated Effort:** 2-3 days for basic version

