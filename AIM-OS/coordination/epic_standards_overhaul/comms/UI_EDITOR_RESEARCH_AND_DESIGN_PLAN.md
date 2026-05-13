# UI Editor Research & Custom Design Plan

**Created:** 2025-10-31  
**From:** Aether (Manager/Leader)  
**Purpose:** Research existing UI editors, learn from them, and design our own custom UI editor for Cursor Lucid AIM-OS  
**Status:** Research & Planning Phase

---

## 🎯 **OBJECTIVE**

**NOT using existing UI editors** - Instead:
1. **Research** existing UI editors (learn from them)
2. **Document** findings, architectures, patterns, strengths, weaknesses
3. **Plan** our own custom UI editor built specifically for Cursor + AIM-OS
4. **Design** architecture that integrates seamlessly with Cursor's browser and AIM-OS systems

---

## 📚 **RESEARCH: EXISTING UI EDITORS**

### **1. OmniUIEditor** (`omnibuilder_extracted`)

#### **Architecture:**
- **Technology:** React + TypeScript
- **Preview Method:** iframe (`/iframe-content.html`)
- **Communication:** PostMessage API between iframe and parent
- **Component Structure:**
  ```
  OmniUIEditor
  ├── Toolbar (select element, save, export)
  ├── Preview Panel (iframe)
  └── Properties Panel (style editor)
  ```

#### **Key Features:**
1. **Element Selection:**
   - Click-to-select elements in iframe
   - PostMessage communication for selection events
   - Element data structure: `{ tag, id, classes, styles, textContent }`

2. **Style Editing:**
   - Properties panel with style inputs
   - Real-time style application via PostMessage
   - Optimistic UI updates (local state + iframe update)

3. **Code Export:**
   - HTML export functionality
   - Code export (structured data)
   - Save design functionality

4. **Communication Pattern:**
   ```typescript
   // Parent → iframe
   iframe.contentWindow.postMessage({
     type: "START_SELECTING" | "applyStyle" | "EXPORT_HTML",
     payload: { property, value, ... }
   }, "*");

   // iframe → Parent
   window.addEventListener("message", (event) => {
     if (event.data.type === "elementSelected") {
       setSelectedElement(event.data.payload);
     }
   });
   ```

#### **Strengths:**
- ✅ Clean separation (preview vs. editor)
- ✅ Simple communication pattern
- ✅ Easy to understand and maintain
- ✅ iframe isolation (no style conflicts)

#### **Weaknesses:**
- ❌ Limited interactivity (iframe constraints)
- ❌ No component library
- ❌ No drag & drop
- ❌ Basic styling only (no layout tools)

#### **Lessons Learned:**
- ✅ iframe + PostMessage = good isolation pattern
- ✅ Optimistic updates improve UX
- ✅ Simple element selection works well

---

### **2. Amazing UI Editor** (`amazinguiediter`)

#### **Architecture:**
- **Technology:** React + TypeScript
- **Preview Method:** Direct DOM manipulation (BrowserOS component)
- **Design System:** Neumorphic design
- **Component Structure:**
  ```
  App
  ├── BrowserOS (browser simulation)
  ├── OmniToolbar (toolbar)
  ├── ElementInspector (element details)
  ├── CodeSync (live code sync)
  ├── AIAgent (AI assistance)
  ├── VisualFeedback (visual indicators)
  └── SnapEngine (smart alignment)
  ```

#### **Key Features:**
1. **BrowserOS Component:**
   - Simulates browser environment
   - Status bar, desktop area, app launcher
   - Neural browser window with holographic UI
   - Direct DOM manipulation (no iframe)

2. **Element Inspector:**
   - Detailed element inspection
   - Property editing
   - Visual feedback on selection

3. **Code Sync:**
   - Live code synchronization
   - Bidirectional sync (code ↔ UI)
   - Real-time updates

4. **AI Agent Integration:**
   - AI-powered assistance
   - Design recommendations
   - Auto-layout suggestions

5. **Visual Feedback:**
   - Visual indicators for interactions
   - Snap lines and guides
   - Highlighting and overlays

6. **Snap Engine:**
   - Smart alignment
   - Grid snapping
   - Gravity wells

#### **Strengths:**
- ✅ Rich feature set
- ✅ AI integration (fits AIM-OS philosophy)
- ✅ Direct DOM manipulation (more control)
- ✅ Visual feedback system
- ✅ Code sync capability

#### **Weaknesses:**
- ❌ Complex architecture (many components)
- ❌ BrowserOS is simulation (not real browser)
- ❌ Neumorphic design may not fit Cursor aesthetic
- ❌ More overhead (multiple systems)

#### **Lessons Learned:**
- ✅ AI assistance is valuable
- ✅ Visual feedback improves UX
- ✅ Code sync enables bidirectional editing
- ✅ Direct DOM manipulation gives more control

---

### **3. Perfect UI Adjuster** (`perfectUIadjuster-bolt`)

#### **Architecture:**
- **Technology:** React + TypeScript
- **Preview Method:** Canvas-based rendering
- **Component Structure:**
  ```
  Canvas
  ├── ElementOverlay (selection overlay)
  ├── GuideLines (alignment guides)
  ├── MeasurementOverlay (dimensions)
  ├── ScaleHandles (resize handles)
  ├── SnapLines (snapping lines)
  ├── Rulers (measurement rulers)
  ├── GridOverlay (grid display)
  ├── SelectionBox (multi-select)
  ├── GravityWells (smart positioning)
  ├── FluidDynamics (animation system)
  ├── SemanticZones (semantic regions)
  ├── BlueprintOverlay (layout blueprint)
  └── MagneticFields (magnetic alignment)
  ```

#### **Key Features:**
1. **Canvas-Based Rendering:**
   - Canvas for overlay rendering
   - Separate from content DOM
   - Advanced visual tools

2. **Advanced Snapping:**
   - Multiple snap types (horizontal, vertical, magnetic, semantic, gravity)
   - Configurable snap strength
   - Smart alignment system

3. **Layout Tools:**
   - Rulers and measurements
   - Grid overlay
   - Guide lines
   - Blueprint overlay

4. **Smart Positioning:**
   - Gravity wells (attract elements)
   - Magnetic fields (magnetic alignment)
   - Semantic zones (semantic regions)
   - Fluid dynamics (smooth animations)

5. **Multi-Select:**
   - Selection box (drag to select multiple)
   - Multi-element manipulation
   - Batch operations

#### **Strengths:**
- ✅ Advanced layout tools
- ✅ Canvas overlay (clean separation)
- ✅ Multiple snapping systems
- ✅ Smart positioning features
- ✅ Professional-grade tools

#### **Weaknesses:**
- ❌ Canvas-based (more complex rendering)
- ❌ Learning curve (many features)
- ❌ Potentially over-engineered for basic use
- ❌ Performance concerns (canvas rendering)

#### **Lessons Learned:**
- ✅ Canvas overlay = clean visual tools
- ✅ Multiple snapping systems = flexibility
- ✅ Smart positioning improves UX
- ✅ Advanced tools for professional use

---

## 🎨 **CUSTOM UI EDITOR DESIGN**

### **Design Philosophy**

**Built specifically for Cursor + AIM-OS:**
- ✅ Native Cursor integration (webview API)
- ✅ AIM-OS awareness (CMC, HHNI, VIF, APOE)
- ✅ Browser-based editing (real browser, not simulation)
- ✅ Consciousness-first design (AI assistance built-in)
- ✅ Production-ready quality

### **Core Principles**

1. **Real Browser Integration:**
   - Use Cursor's webview API for preview
   - Real browser rendering (not simulation)
   - Full browser capabilities

2. **AIM-OS Integration:**
   - Store designs in CMC
   - Search components via HHNI
   - Track confidence with VIF
   - Orchestrate with APOE

3. **Consciousness-First:**
   - AI assistance built-in (Gemini/Cerebras)
   - Design recommendations
   - Auto-layout suggestions
   - Quality assurance

4. **Cursor Aesthetic:**
   - Match Cursor's design system
   - Consistent with existing panels
   - Professional and clean

5. **Developer Experience:**
   - Fast and responsive
   - Intuitive interface
   - Powerful features
   - Real-time feedback

---

## 🏗️ **ARCHITECTURE DESIGN**

### **Component Structure**

```
UIEditorTab (Main Component)
├── Toolbar
│   ├── Mode Selector (Select, Design, Code)
│   ├── View Controls (Zoom, Grid, Rulers)
│   ├── Actions (Save, Export, Import)
│   └── AI Assistant Toggle
│
├── Preview Panel
│   ├── Browser Preview (Cursor webview)
│   ├── Element Overlay (selection, guides)
│   └── Interaction Layer (click, drag, resize)
│
├── Properties Panel
│   ├── Element Info (tag, id, classes)
│   ├── Style Editor (CSS properties)
│   ├── Layout Controls (flexbox, grid)
│   ├── Responsive Breakpoints
│   └── Component Properties
│
├── Component Library
│   ├── Basic Components (Button, Input, Card)
│   ├── Layout Components (Container, Grid, Flex)
│   ├── AIM-OS Components (if available)
│   └── Custom Components
│
└── Code Panel (Optional)
    ├── Generated Code View
    ├── Code Editor (Monaco)
    └── Sync Controls (bidirectional)
```

### **Technology Stack**

- **Framework:** React + TypeScript
- **Preview:** Cursor webview API (real browser)
- **Communication:** PostMessage API + WebSocket (for real-time)
- **State Management:** Zustand or Redux Toolkit
- **Styling:** Tailwind CSS (match Cursor aesthetic)
- **Code Generation:** React/HTML/CSS codegen
- **AI Integration:** Gemini/Cerebras APIs (via AIM-OS)

### **Data Flow**

```
User Interaction
    ↓
UI Editor Component
    ↓
State Management (Zustand/Redux)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│                 │                 │                 │
Preview Panel  Properties Panel  Code Panel
(Webview)      (Style Editor)    (Monaco Editor)
    ↓                 ↓                 ↓
PostMessage      State Update     Code Update
    ↓                 ↓                 ↓
┌─────────────────────────────────────────────────┐
│            AIM-OS Integration                   │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │   CMC    │   HHNI   │   VIF    │   APOE   │ │
│  │ (Storage)│ (Search) │(Confidence)│ (Plan) │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 🔧 **KEY FEATURES DESIGN**

### **1. Browser Preview (Real Browser)**

**Approach:**
- Use Cursor's `vscode.window.createWebviewPanel()` for preview
- Load actual HTML content in webview
- Real browser rendering (not simulation)
- Full browser capabilities (CSS, JavaScript, etc.)

**Implementation:**
```typescript
// Create webview panel for preview
const previewPanel = vscode.window.createWebviewPanel(
  'uiEditorPreview',
  'UI Editor Preview',
  vscode.ViewColumn.Beside,
  {
    enableScripts: true,
    retainContextWhenHidden: true
  }
);

// Load HTML content
previewPanel.webview.html = generatePreviewHTML(designData);

// Communication via PostMessage
previewPanel.webview.onDidReceiveMessage((message) => {
  if (message.type === 'elementSelected') {
    handleElementSelection(message.payload);
  }
});
```

**Benefits:**
- ✅ Real browser rendering (accurate preview)
- ✅ Full browser capabilities
- ✅ No simulation overhead
- ✅ Matches production environment

### **2. Element Selection & Inspection**

**Approach:**
- Click-to-select elements in preview
- PostMessage communication for selection
- Element data structure with full metadata
- Visual overlay for selected element

**Implementation:**
```typescript
interface SelectedElement {
  tag: string;
  id?: string;
  classes: string[];
  styles: Record<string, string>;
  attributes: Record<string, string>;
  textContent?: string;
  children?: SelectedElement[];
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}
```

**Features:**
- ✅ Click-to-select in preview
- ✅ Visual highlight overlay
- ✅ Element hierarchy display
- ✅ Full element metadata

### **3. Style Editor**

**Approach:**
- Comprehensive CSS property editor
- Real-time style application
- Organized by category (layout, typography, colors, etc.)
- Visual controls (color picker, slider, etc.)

**Implementation:**
```typescript
// Style categories
const styleCategories = {
  layout: ['width', 'height', 'margin', 'padding', 'display', 'position'],
  typography: ['font-family', 'font-size', 'font-weight', 'line-height', 'color'],
  colors: ['background-color', 'color', 'border-color'],
  spacing: ['margin', 'padding', 'gap'],
  // ... more categories
};

// Real-time style application
const applyStyle = (property: string, value: string) => {
  previewPanel.webview.postMessage({
    type: 'applyStyle',
    payload: { property, value, elementId: selectedElement.id }
  });
};
```

**Features:**
- ✅ Category-based organization
- ✅ Visual controls (color picker, slider)
- ✅ Real-time preview
- ✅ CSS validation

### **4. Component Library**

**Approach:**
- Drag & drop component library
- Common UI components
- AIM-OS components (if available)
- Custom components (user-defined)

**Implementation:**
```typescript
interface Component {
  id: string;
  name: string;
  category: 'basic' | 'layout' | 'aimos' | 'custom';
  preview: string; // Preview image/icon
  code: string; // Generated code
  properties: ComponentProperty[];
}

// Drag & drop
const handleComponentDrop = (component: Component, position: { x: number, y: number }) => {
  const element = createElementFromComponent(component);
  addElementToDesign(element, position);
};
```

**Features:**
- ✅ Drag & drop from library
- ✅ Component preview
- ✅ Property configuration
- ✅ Code generation

### **5. Code Sync**

**Approach:**
- Bidirectional sync (UI ↔ Code)
- Live code generation
- Import from code files
- Export to React/HTML/CSS

**Implementation:**
```typescript
// Generate code from design
const generateCode = (design: Design): string => {
  return design.elements.map(element => {
    return generateReactComponent(element);
  }).join('\n');
};

// Parse code to design
const parseCodeToDesign = (code: string): Design => {
  const ast = parseCode(code);
  return convertASTToDesign(ast);
};

// Sync updates
const syncCodeToUI = (code: string) => {
  const design = parseCodeToDesign(code);
  updateDesign(design);
};

const syncUIToCode = (design: Design) => {
  const code = generateCode(design);
  updateCodeEditor(code);
};
```

**Features:**
- ✅ Live code generation
- ✅ Import from code
- ✅ Export to React/HTML/CSS
- ✅ Bidirectional sync

### **6. AI Assistance**

**Approach:**
- Integrated Gemini/Cerebras APIs
- Design recommendations
- Auto-layout suggestions
- Quality assurance

**Implementation:**
```typescript
// AI design assistant
const getDesignRecommendations = async (design: Design): Promise<Recommendation[]> => {
  const prompt = `Analyze this UI design and provide recommendations:
    ${JSON.stringify(design)}
    
    Consider:
    - Accessibility
    - Responsiveness
    - Best practices
    - Performance
    - User experience
  `;
  
  const response = await aimosService.callGemini(prompt);
  return parseRecommendations(response);
};

// Auto-layout suggestions
const suggestLayout = async (elements: Element[]): Promise<LayoutSuggestion> => {
  const prompt = `Suggest optimal layout for these elements:
    ${JSON.stringify(elements)}
  `;
  
  const response = await aimosService.callGemini(prompt);
  return parseLayoutSuggestion(response);
};
```

**Features:**
- ✅ Design recommendations
- ✅ Auto-layout suggestions
- ✅ Accessibility checks
- ✅ Best practices guidance

### **7. AIM-OS Integration**

**CMC (Storage):**
```typescript
// Store design in CMC
await aimosService.storeMemory({
  content: JSON.stringify(design),
  tags: {
    type: 'ui_design',
    project: 'my-app',
    component: 'button'
  }
});

// Retrieve designs
const designs = await aimosService.retrieveMemory('button component design');
```

**HHNI (Search):**
```typescript
// Search for similar components
const similarComponents = await aimosService.retrieveMemory(
  'card component with shadow',
  { limit: 10 }
);
```

**VIF (Confidence):**
```typescript
// Track design quality confidence
await aimosService.trackConfidence({
  task: 'UI design generation',
  confidence: 0.85,
  reasoning: 'Generated from proven component pattern',
  evidence: ['design_follows_best_practices', 'responsive_design', 'accessible']
});
```

**APOE (Orchestration):**
```typescript
// Create design generation plan
const plan = await aimosService.createPlan({
  goal: 'Create responsive dashboard UI',
  steps: [
    'Design layout structure',
    'Add components',
    'Configure responsive breakpoints',
    'Generate code',
    'Test accessibility'
  ]
});

// Execute plan
await aimosService.executePlan(plan);
```

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Foundation (Week 1-2)**
- [ ] Create `UIEditorTab.tsx` component
- [ ] Set up Cursor webview integration
- [ ] Basic preview panel (load HTML in webview)
- [ ] Element selection (click-to-select)
- [ ] PostMessage communication setup
- [ ] Basic state management

### **Phase 2: Style Editor (Week 2-3)**
- [ ] Properties panel component
- [ ] Style editor (CSS properties)
- [ ] Real-time style application
- [ ] Visual controls (color picker, slider)
- [ ] Category-based organization
- [ ] CSS validation

### **Phase 3: Element Manipulation (Week 3-4)**
- [ ] Drag & drop elements
- [ ] Resize handles
- [ ] Element overlay (selection highlight)
- [ ] Guide lines and snapping
- [ ] Multi-select functionality
- [ ] Element hierarchy display

### **Phase 4: Component Library (Week 4-5)**
- [ ] Component library panel
- [ ] Drag & drop from library
- [ ] Component preview
- [ ] Property configuration
- [ ] Code generation for components
- [ ] Custom component support

### **Phase 5: Code Sync (Week 5-6)**
- [ ] Code generation (React/HTML/CSS)
- [ ] Code editor (Monaco)
- [ ] Import from code
- [ ] Export to files
- [ ] Bidirectional sync
- [ ] Code formatting

### **Phase 6: AI Integration (Week 6-7)**
- [ ] Gemini/Cerebras API integration
- [ ] Design recommendations
- [ ] Auto-layout suggestions
- [ ] Accessibility checks
- [ ] Quality assurance
- [ ] Best practices guidance

### **Phase 7: AIM-OS Integration (Week 7-8)**
- [ ] CMC storage integration
- [ ] HHNI search integration
- [ ] VIF confidence tracking
- [ ] APOE orchestration
- [ ] Design templates
- [ ] Component sharing

### **Phase 8: Advanced Features (Week 8-9)**
- [ ] Responsive breakpoints
- [ ] Layout tools (flexbox, grid)
- [ ] Animation system
- [ ] Template system
- [ ] Collaboration features
- [ ] Version control integration

---

## 🎨 **UI DESIGN**

### **Tab Placement:**
- **Tab 8: 🎨 UI Editor** (New tab in main Cursor panel)

### **Layout Design:**

```
┌─────────────────────────────────────────────────────────────┐
│ [🤖 Agents] [💬 Chat] [🔗 Chains] [🛠️ Tools] [🎨 UI Editor] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ 🎨 UI EDITOR                                          │   │
│ │                                                       │   │
│ │ ┌──────────────────────────┐ ┌───────────────────┐ │   │
│ │ │                          │ │ Properties Panel  │ │   │
│ │ │                          │ │                   │ │   │
│ │ │   Browser Preview        │ │ Selected: div     │ │   │
│ │ │   (Cursor Webview)       │ │                   │ │   │
│ │ │                          │ │ Styles:           │ │   │
│ │ │   [Live Preview]         │ │ • width: 100px    │ │   │
│ │ │                          │ │ • height: 50px    │ │   │
│ │ │                          │ │ • background: #333│ │   │
│ │ │                          │ │                   │ │   │
│ │ │                          │ │ [Edit Styles]     │ │   │
│ │ │                          │ │                   │ │   │
│ │ │                          │ │ [AI Suggestions]  │ │   │
│ │ └──────────────────────────┘ └───────────────────┘ │   │
│ │                                                       │   │
│ │ ┌─────────────────────────────────────────────────┐ │   │
│ │ │ Component Library                               │ │   │
│ │ │ [Button] [Input] [Card] [Modal] [Form] ...     │ │   │
│ │ │ [Drag to add]                                   │ │   │
│ │ └─────────────────────────────────────────────────┘ │   │
│ │                                                       │   │
│ │ ┌─────────────────────────────────────────────────┐ │   │
│ │ │ Code Sync                                        │ │   │
│ │ │ [Generated Code] [Edit Code] [Sync] [Export]   │ │   │
│ │ └─────────────────────────────────────────────────┘ │   │
│ └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### **Design Principles:**
- ✅ Match Cursor aesthetic (dark theme, consistent styling)
- ✅ Clean and professional
- ✅ Intuitive interface
- ✅ Real-time feedback
- ✅ Powerful features

---

## 🔧 **TECHNICAL DECISIONS**

### **1. Preview Method: Cursor Webview**
- ✅ Real browser rendering
- ✅ Full browser capabilities
- ✅ Native Cursor integration
- ✅ No simulation overhead

### **2. Communication: PostMessage + WebSocket**
- ✅ PostMessage for iframe/webview communication
- ✅ WebSocket for real-time updates (optional)
- ✅ Simple and reliable

### **3. State Management: Zustand**
- ✅ Lightweight and simple
- ✅ Good TypeScript support
- ✅ Easy to integrate
- ✅ Performance optimized

### **4. Code Generation: React Codegen**
- ✅ Generate React components
- ✅ TypeScript support
- ✅ Clean code output
- ✅ Export to files

### **5. AI Integration: AIM-OS Services**
- ✅ Use existing AIMOSService
- ✅ Gemini/Cerebras APIs
- ✅ VIF confidence tracking
- ✅ CMC storage integration

---

## 📊 **SUCCESS CRITERIA**

### **Must Have:**
- ✅ Basic UI editor (select, style, export)
- ✅ Browser preview (Cursor webview)
- ✅ Properties panel
- ✅ Code generation
- ✅ Cursor integration

### **Should Have:**
- ⏳ Component library
- ⏳ Drag & drop
- ⏳ Code sync
- ⏳ AI assistance
- ⏳ AIM-OS integration

### **Nice to Have:**
- ⏳ Advanced layout tools
- ⏳ Responsive breakpoints
- ⏳ Animation system
- ⏳ Template system
- ⏳ Collaboration features

---

## 🚀 **NEXT STEPS**

### **Immediate Actions:**
1. ✅ Research complete (documented findings)
2. ✅ Design complete (architecture planned)
3. ⏳ Assign to Lexicon for implementation
4. ⏳ Begin Phase 1 integration

### **For Lexicon:**
1. Review this research and design plan
2. Start Phase 1 implementation
3. Create `UIEditorTab.tsx` component
4. Set up Cursor webview integration
5. Implement basic preview panel

### **For User:**
1. Review design plan
2. Provide feedback on architecture
3. Test implementation as it's built

---

## 💙 **QUESTIONS?**

**If Lexicon Needs Clarification:**
- Review this research and design plan
- Ask questions via MCP message to Aether
- Check message board for updates

**If User Needs Clarification:**
- Review design plan
- Provide feedback on architecture
- Test implementation as it's built

---

**Status:** Research complete! Design planned! Ready for Lexicon implementation! 💙✨

