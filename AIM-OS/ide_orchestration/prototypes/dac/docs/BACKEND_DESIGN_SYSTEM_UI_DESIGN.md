# Backend Design System - UI Design Document
**Seamless Integration with DAC IDE Layout**

**Date:** 2025-12-02  
**Status:** Design Phase  
**Integration Point:** New Main View Type  
**Follows:** DAC IDE 5-Zone Layout System

---

## 🎯 **OVERVIEW**

Add a new **"Backend"** main view to the DAC IDE that provides:
- Visual template selection and composition
- Backend architecture design canvas
- Template customization interface
- Code generation preview
- Deployment configuration

**Placement:** New main view type alongside Code, Canvas, AI Chat, Evolution, etc.

---

## 🏗️ **INTEGRATION WITH EXISTING LAYOUT**

### **Main View Type Addition**

```typescript
// In IDELayout.tsx - Add to MainViewType
type MainViewType = 
  | 'code' 
  | 'evolution' 
  | 'consciousness' 
  | 'orchestration' 
  | 'app-preview' 
  | 'document-editor' 
  | 'file-preview' 
  | 'canvas' 
  | 'manager-ai-chat'
  | 'backend-design'  // ← NEW
```

### **Main Toolbar Button Addition**

```typescript
// In IDELayout.tsx - Add to MAIN_TOOLBAR_BUTTONS
const MAIN_TOOLBAR_BUTTONS: MainToolbarButton[] = [
  // ... existing buttons ...
  { 
    id: 'backend-design', 
    icon: Server, 
    title: 'Backend Design\nVisual backend architecture design with template composition', 
    section: 'right', 
    toolbar: 'main' 
  },
]
```

### **Lazy Loading**

```typescript
// In utils/performance.tsx - Add lazy component
export const LazyBackendDesign = lazy(() => 
  import('../views/BackendDesignView').then(m => ({ default: m.BackendDesignView }))
)
```

---

## 📐 **UI LAYOUT SPECIFICATION**

### **Full Layout Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TOP BAR (h-8 = 32px)                               │
│  [Menu] │ [↓] Code | Preview | Canvas | AI Chat | Backend | Evolution | ... │ 🔔│
├────┬────┴──────────────────────────────────────────────────────────────────┬────┤
│    │                                                                        │    │
│ L  │                        BACKEND DESIGN VIEW                            │  R │
│ E  │  ┌─────────────────────────────────────────────────────────────────┐  │  I │
│ F  │  │                    TEMPLATE PALETTE (h-12)                       │  │  G │
│ T  │  │  🗄️ Architecture | 🔒 Auth | 💾 Database | 🌐 API | ⚡ Real-time │  │  H │
│    │  └─────────────────────────────────────────────────────────────────┘  │  T │
│ T  │                                                                        │    │
│ O  │  ┌─────────────────────────────────────────────────────────────────┐  │  T │
│ O  │  │                                                                  │  │  O │
│ L  │  │                     DESIGN CANVAS (Flex-1)                       │  │  O │
│ B  │  │                                                                  │  │  L │
│ A  │  │    ┌──────────┐           ┌──────────┐           ┌──────────┐   │  │  B │
│ R  │  │    │  Auth    │──────────→│   API    │──────────→│ Database │   │  │  A │
│    │  │    │  (JWT)   │           │  (REST)  │           │ (Postgres)│   │  │  R │
│(w  │  │    └──────────┘           └──────────┘           └──────────┘   │  │    │
│-8) │  │                                                                  │  │(w  │
│    │  │    ┌──────────┐                                                  │  │-8) │
│    │  │    │  Storage │                                                  │  │    │
│    │  │    │   (S3)   │                                                  │  │    │
│    │  │    └──────────┘                                                  │  │    │
│    │  │                                                                  │  │    │
│    │  └─────────────────────────────────────────────────────────────────┘  │    │
│    │                                                                        │    │
│    │  ┌─────────────────────────────────────────────────────────────────┐  │    │
│    │  │                  PROPERTIES PANEL (h-64)                         │  │    │
│    │  │  [Selected: Auth (JWT)]                                          │  │    │
│    │  │  Access Token Expiry: [15m ▼]  Refresh Token Expiry: [7d ▼]     │  │    │
│    │  │  Email Verification: [✓]       Social Login: [ ] Google [...]    │  │    │
│    │  └─────────────────────────────────────────────────────────────────┘  │    │
├────┴────────────────────────────────────────────────────────────────────────┴────┤
│                           BOTTOM BAR (h-8 = 32px)                                │
│  [CMC: 156] [VIF + SEG Active] │ [◐ ◑ ◒ ◓] ◀▶ [◔ ◕ ◖ ◗] │ DAC-V2               │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 **COMPONENT SPECIFICATIONS**

### **1. Template Palette Bar (Top)**

**Position:** Fixed at top of Backend Design view  
**Height:** 48px (h-12)  
**Background:** `var(--aimos-bg-secondary)` / `gray-900`  
**Border:** `border-b border-gray-800`

```tsx
<div className="h-12 bg-gray-900 border-b border-gray-800 flex items-center px-4 gap-2">
  {/* Category Tabs */}
  <div className="flex items-center gap-1">
    {categories.map(cat => (
      <button
        key={cat.id}
        onClick={() => setActiveCategory(cat.id)}
        className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 ${
          activeCategory === cat.id
            ? 'bg-gray-800 text-gray-100'
            : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
        }`}
      >
        <cat.icon className="w-3.5 h-3.5" />
        <span>{cat.name}</span>
        <span className="text-gray-500 ml-1">({cat.count})</span>
      </button>
    ))}
  </div>
  
  {/* Search */}
  <div className="ml-auto flex items-center gap-2">
    <div className="relative">
      <Search className="w-3.5 h-3.5 absolute left-2 top-1/2 -translate-y-1/2 text-gray-500" />
      <input
        type="text"
        placeholder="Search templates..."
        className="w-48 h-7 pl-7 pr-2 rounded-md bg-gray-800 border border-gray-700 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-gray-600"
      />
    </div>
  </div>
</div>
```

**Template Categories:**
| ID | Icon | Name | Count |
|-----|------|------|-------|
| `architecture` | `Layers` | Architecture | 10 |
| `auth` | `Shield` | Auth | 15 |
| `database` | `Database` | Database | 20 |
| `api` | `Globe` | API | 18 |
| `realtime` | `Zap` | Real-time | 12 |
| `jobs` | `Clock` | Jobs | 10 |
| `storage` | `HardDrive` | Storage | 8 |
| `deploy` | `Cloud` | Deploy | 15 |
| `monitor` | `Activity` | Monitor | 12 |

---

### **2. Design Canvas (Center)**

**Position:** Main content area (flex-1)  
**Background:** `var(--aimos-bg-primary)` / `gray-950`  
**Library:** React Flow (same as Context Web panel)

```tsx
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  NodeTypes,
  useNodesState,
  useEdgesState,
} from 'reactflow'

// Custom node types for templates
const nodeTypes: NodeTypes = {
  template: TemplateNode,
  group: GroupNode,
}

<div className="flex-1 bg-gray-950">
  <ReactFlow
    nodes={nodes}
    edges={edges}
    onNodesChange={onNodesChange}
    onEdgesChange={onEdgesChange}
    onConnect={onConnect}
    nodeTypes={nodeTypes}
    fitView
    className="bg-gray-950"
  >
    <Background color="#374151" gap={16} size={1} />
    <Controls className="bg-gray-800 border border-gray-700 rounded-lg" />
    <MiniMap 
      className="bg-gray-800 border border-gray-700 rounded-lg"
      nodeColor={(node) => getNodeColor(node.data.type)}
    />
  </ReactFlow>
</div>
```

**Template Node Component:**

```tsx
interface TemplateNodeData {
  id: string
  type: 'auth' | 'database' | 'api' | 'realtime' | 'storage' | 'deploy' | 'monitor'
  name: string
  icon: React.ComponentType
  status: 'configured' | 'incomplete' | 'error'
  config: Record<string, any>
}

const TemplateNode: React.FC<NodeProps<TemplateNodeData>> = ({ data, selected }) => {
  const colorMap = {
    auth: 'border-orange-500/50 bg-orange-500/10',
    database: 'border-green-500/50 bg-green-500/10',
    api: 'border-blue-500/50 bg-blue-500/10',
    realtime: 'border-yellow-500/50 bg-yellow-500/10',
    storage: 'border-purple-500/50 bg-purple-500/10',
    deploy: 'border-cyan-500/50 bg-cyan-500/10',
    monitor: 'border-pink-500/50 bg-pink-500/10',
  }
  
  return (
    <div className={`
      w-32 h-20 rounded-lg border-2 p-2
      ${colorMap[data.type]}
      ${selected ? 'ring-2 ring-blue-500 ring-offset-2 ring-offset-gray-950' : ''}
      transition-all duration-200
    `}>
      <Handle type="target" position={Position.Left} className="w-2 h-2 bg-gray-600" />
      
      <div className="flex flex-col items-center justify-center h-full gap-1">
        <data.icon className="w-6 h-6 text-gray-300" />
        <span className="text-xs font-medium text-gray-200 text-center">{data.name}</span>
        
        {/* Status Indicator */}
        <div className={`w-1.5 h-1.5 rounded-full ${
          data.status === 'configured' ? 'bg-green-500' :
          data.status === 'incomplete' ? 'bg-yellow-500' : 'bg-red-500'
        }`} />
      </div>
      
      <Handle type="source" position={Position.Right} className="w-2 h-2 bg-gray-600" />
    </div>
  )
}
```

---

### **3. Template Drawer (Left/Right Panel)**

**Position:** Right sidebar panel (like existing context-web, timeline, etc.)  
**Panel Type:** Add to `RightPanelType`

```typescript
type RightPanelType = 
  | 'context-web' 
  | 'timeline' 
  | 'outline' 
  // ...existing...
  | 'template-library'  // ← NEW
```

**Template Library Panel:**

```tsx
const TemplateLibraryPanel: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  
  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="h-10 flex items-center justify-between px-3 border-b border-gray-800">
        <span className="text-xs font-semibold text-gray-200">Template Library</span>
        <span className="text-xs text-gray-500">500+ templates</span>
      </div>
      
      {/* Search */}
      <div className="p-2 border-b border-gray-800">
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-7 pl-7 pr-2 rounded-md bg-gray-800 border border-gray-700 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-gray-600"
          />
        </div>
      </div>
      
      {/* Category Filter */}
      <div className="p-2 border-b border-gray-800 overflow-x-auto">
        <div className="flex gap-1">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-2 py-1 rounded text-xs whitespace-nowrap ${
                selectedCategory === cat.id
                  ? 'bg-gray-800 text-gray-100'
                  : 'text-gray-400 hover:bg-gray-800/50'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>
      
      {/* Template List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {filteredTemplates.map(template => (
          <TemplateCard key={template.id} template={template} />
        ))}
      </div>
    </div>
  )
}

const TemplateCard: React.FC<{ template: Template }> = ({ template }) => {
  return (
    <div
      draggable
      onDragStart={(e) => handleTemplateDrag(e, template)}
      className="p-2 rounded-md bg-gray-800/50 border border-gray-700 hover:border-gray-600 cursor-move group transition-colors"
    >
      <div className="flex items-start gap-2">
        <div className={`w-8 h-8 rounded flex items-center justify-center ${getColorByType(template.type)}`}>
          <template.icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-medium text-gray-200 truncate">{template.name}</div>
          <div className="text-[10px] text-gray-500 truncate">{template.description}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[10px] text-gray-600">{template.lines} lines</span>
            <span className="text-[10px] text-gray-600">•</span>
            <span className="text-[10px] text-gray-600">{template.coverage}% coverage</span>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

### **4. Properties Panel (Bottom)**

**Position:** Bottom section of main view (collapsible)  
**Height:** 256px (h-64) when expanded  
**Background:** `var(--aimos-bg-secondary)` / `gray-900`

```tsx
const PropertiesPanel: React.FC<{ selectedNode: TemplateNodeData | null }> = ({ selectedNode }) => {
  const [isExpanded, setIsExpanded] = useState(true)
  
  if (!selectedNode) {
    return (
      <div className="h-64 bg-gray-900 border-t border-gray-800 flex items-center justify-center">
        <div className="text-center">
          <Package className="w-8 h-8 text-gray-600 mx-auto mb-2" />
          <div className="text-sm text-gray-500">Select a template to configure</div>
        </div>
      </div>
    )
  }
  
  return (
    <div className={`bg-gray-900 border-t border-gray-800 transition-all ${isExpanded ? 'h-64' : 'h-10'}`}>
      {/* Header */}
      <div className="h-10 flex items-center justify-between px-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <selectedNode.icon className="w-4 h-4 text-gray-300" />
          <span className="text-sm font-medium text-gray-200">{selectedNode.name}</span>
          <span className={`px-1.5 py-0.5 rounded text-[10px] ${getStatusBadgeColor(selectedNode.status)}`}>
            {selectedNode.status}
          </span>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 hover:bg-gray-800 rounded text-gray-400"
        >
          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </button>
      </div>
      
      {/* Content */}
      {isExpanded && (
        <div className="p-4 overflow-y-auto h-[calc(256px-40px)]">
          <div className="grid grid-cols-2 gap-4">
            {/* Dynamic form fields based on template type */}
            {renderConfigFields(selectedNode)}
          </div>
        </div>
      )}
    </div>
  )
}
```

**Config Field Components:**

```tsx
// Dropdown Field
const ConfigDropdown: React.FC<{ label: string; value: string; options: string[]; onChange: (v: string) => void }> = ({
  label, value, options, onChange
}) => (
  <div className="space-y-1">
    <label className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full h-7 px-2 rounded bg-gray-800 border border-gray-700 text-xs text-gray-200 focus:outline-none focus:border-gray-600"
    >
      {options.map(opt => (
        <option key={opt} value={opt}>{opt}</option>
      ))}
    </select>
  </div>
)

// Toggle Field
const ConfigToggle: React.FC<{ label: string; value: boolean; onChange: (v: boolean) => void }> = ({
  label, value, onChange
}) => (
  <div className="flex items-center justify-between">
    <label className="text-xs text-gray-300">{label}</label>
    <button
      onClick={() => onChange(!value)}
      className={`w-8 h-4 rounded-full transition-colors ${value ? 'bg-blue-600' : 'bg-gray-700'}`}
    >
      <div className={`w-3 h-3 rounded-full bg-white transition-transform ${value ? 'translate-x-4' : 'translate-x-0.5'}`} />
    </button>
  </div>
)

// Input Field
const ConfigInput: React.FC<{ label: string; value: string; placeholder?: string; onChange: (v: string) => void }> = ({
  label, value, placeholder, onChange
}) => (
  <div className="space-y-1">
    <label className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</label>
    <input
      type="text"
      value={value}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
      className="w-full h-7 px-2 rounded bg-gray-800 border border-gray-700 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-gray-600"
    />
  </div>
)
```

---

### **5. Action Bar (Floating)**

**Position:** Bottom-right of canvas  
**Style:** Floating action buttons

```tsx
const ActionBar: React.FC = () => (
  <div className="absolute bottom-4 right-4 flex items-center gap-2 z-10">
    {/* Preview Code */}
    <button className="px-3 py-1.5 rounded-md bg-gray-800 border border-gray-700 text-xs text-gray-200 hover:bg-gray-700 flex items-center gap-1.5 transition-colors">
      <Code className="w-3.5 h-3.5" />
      Preview Code
    </button>
    
    {/* Generate */}
    <button className="px-3 py-1.5 rounded-md bg-blue-600 text-xs text-white hover:bg-blue-700 flex items-center gap-1.5 transition-colors">
      <Zap className="w-3.5 h-3.5" />
      Generate Backend
    </button>
    
    {/* Deploy */}
    <button className="px-3 py-1.5 rounded-md bg-green-600 text-xs text-white hover:bg-green-700 flex items-center gap-1.5 transition-colors">
      <Cloud className="w-3.5 h-3.5" />
      Deploy
    </button>
  </div>
)
```

---

## 🎨 **COLOR SCHEME**

### **Template Type Colors**

Following AIM-OS design tokens pattern:

```css
/* Template Type Colors */
--aimos-template-auth: #ffa657;      /* Orange (like VIF) */
--aimos-template-database: #7ee787;  /* Green (like CMC) */
--aimos-template-api: #79c0ff;       /* Blue (like HHNI) */
--aimos-template-realtime: #ffd93d;  /* Yellow */
--aimos-template-storage: #d2a8ff;   /* Purple (like APOE) */
--aimos-template-deploy: #4ec9b0;    /* Teal (like CAS) */
--aimos-template-monitor: #ff7b72;   /* Red (like SEG) */
--aimos-template-jobs: #569cd6;      /* Cyan (like TCS) */
--aimos-template-arch: #a855f7;      /* Violet */
```

### **Status Colors**

```typescript
const statusColors = {
  configured: 'bg-green-500/10 text-green-400 border-green-500/30',
  incomplete: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  error: 'bg-red-500/10 text-red-400 border-red-500/30',
}
```

---

## 🔄 **STATE MANAGEMENT**

### **Zustand Store Extension**

```typescript
// Add to panelStore.ts or create new backendDesignStore.ts

interface BackendDesignState {
  // Canvas State
  nodes: Node<TemplateNodeData>[]
  edges: Edge[]
  selectedNodeId: string | null
  
  // Template Library State
  templates: Template[]
  filteredTemplates: Template[]
  searchQuery: string
  selectedCategory: string
  
  // Generation State
  isGenerating: boolean
  generationProgress: number
  generatedCode: string | null
  
  // Actions
  addNode: (template: Template, position: { x: number; y: number }) => void
  removeNode: (nodeId: string) => void
  updateNodeConfig: (nodeId: string, config: Record<string, any>) => void
  setSelectedNode: (nodeId: string | null) => void
  connectNodes: (source: string, target: string) => void
  generateCode: () => Promise<void>
  deploy: (target: 'docker' | 'kubernetes' | 'vercel') => Promise<void>
}
```

---

## 📁 **FILE STRUCTURE**

```
src/
├── views/
│   └── BackendDesignView.tsx          # Main view component
│
├── components/
│   └── backend-design/
│       ├── index.ts                    # Exports
│       ├── TemplatePalette.tsx         # Top category bar
│       ├── DesignCanvas.tsx            # React Flow canvas
│       ├── TemplateNode.tsx            # Custom node component
│       ├── TemplateLibraryPanel.tsx    # Right sidebar panel
│       ├── PropertiesPanel.tsx         # Bottom config panel
│       ├── ActionBar.tsx               # Floating action buttons
│       ├── CodePreviewModal.tsx        # Generated code preview
│       └── DeploymentModal.tsx         # Deployment options
│
├── store/
│   └── backendDesignStore.ts           # Zustand store
│
├── hooks/
│   └── useBackendDesign.ts             # Custom hook for backend design
│
├── services/
│   └── backendTemplateService.ts       # Template loading and generation
│
└── types/
    └── backendDesignTypes.ts           # TypeScript types
```

---

## 🔧 **IMPLEMENTATION STEPS**

### **Phase 1: Core Integration (Week 1)**

1. Add `backend-design` to `MainViewType`
2. Add toolbar button with Server icon
3. Create `BackendDesignView.tsx` placeholder
4. Create `LazyBackendDesign` wrapper
5. Wire up main view switching

### **Phase 2: Canvas & Nodes (Week 1-2)**

1. Install React Flow (already in project)
2. Create `DesignCanvas.tsx`
3. Create `TemplateNode.tsx` custom node
4. Implement drag-and-drop from library
5. Implement node connections

### **Phase 3: Template Library (Week 2)**

1. Create `TemplateLibraryPanel.tsx`
2. Add to right panel types
3. Load template data from JSON/API
4. Implement search and filtering
5. Implement drag-to-canvas

### **Phase 4: Properties Panel (Week 2-3)**

1. Create `PropertiesPanel.tsx`
2. Implement dynamic form generation
3. Connect to node selection
4. Persist configuration to store

### **Phase 5: Generation & Deploy (Week 3-4)**

1. Create generation service
2. Implement code preview modal
3. Create deployment modal
4. Connect to backend code generation
5. Test end-to-end flow

---

## 🎯 **KEY INTERACTIONS**

### **1. Drag Template to Canvas**

```
User drags template card from library
    ↓
Drop on canvas
    ↓
Create new node at drop position
    ↓
Auto-select new node
    ↓
Show properties panel with default config
```

### **2. Connect Templates**

```
User drags from source node handle
    ↓
Drop on target node handle
    ↓
Validate connection (check dependencies)
    ↓
Create edge (or show error)
    ↓
Update composition state
```

### **3. Configure Template**

```
User clicks on node
    ↓
Node becomes selected (ring highlight)
    ↓
Properties panel expands
    ↓
User modifies configuration
    ↓
Node status updates (configured/incomplete/error)
```

### **4. Generate Backend**

```
User clicks "Generate Backend"
    ↓
Validate all nodes configured
    ↓
Resolve dependencies
    ↓
Generate code (show progress)
    ↓
Show code preview modal
    ↓
User can download or deploy
```

---

## 📱 **RESPONSIVE BEHAVIOR**

### **Small Screens (<1280px)**

- Template palette collapses to icon-only mode
- Properties panel auto-collapses
- Right sidebar (template library) closes by default
- Action bar becomes vertical

### **Large Screens (>1920px)**

- Template palette shows full descriptions
- Canvas has more room for complex architectures
- Can have both left and right panels open

---

## 🎨 **VISUAL MOCKUP**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ [☰] File  Edit  View  Help  │ ↓  Code  Preview  Canvas  AI  Backend  ...  │ 🔔 👤│
├────┬────────────────────────────────────────────────────────────────────────┬───┤
│    │  🗄️ Architecture  🔒 Auth  💾 Database  🌐 API  ⚡ Real-time  ...  [🔍]│   │
│    ├────────────────────────────────────────────────────────────────────────┤   │
│ 📁 │                                                                        │🌐 │
│ 🧠 │    ┌─────────────┐                                                     │📅 │
│    │    │  🔒 JWT     │                                                     │📋 │
│ ⚡ │    │   Auth      │══════════════╗                                      │🤖 │
│    │    │  ●──────────┤              ║                                      │   │
│    │    └─────────────┘              ║                                      │🗂️ │
│    │                                 ║                                      │🗺️ │
│ 📊 │    ┌─────────────┐         ┌────╨────────┐        ┌─────────────┐     │   │
│ 💾 │    │  🌐 REST    │         │  💾 Postgres │        │  ☁️ Docker  │     │   │
│    │    │    API      │═════════│   Database   │════════│   Deploy    │     │   │
│    │    │  ●──────────┤         │  ●───────────┤        │  ●──────────┤     │   │
│    │    └─────────────┘         └──────────────┘        └─────────────┘     │   │
│    │                                                                        │   │
│    │    ┌─────────────┐                                                     │   │
│    │    │  📦 S3      │                                     [👁️ Code]      │   │
│    │    │   Storage   │                                     [⚡ Generate]   │   │
│    │    │  ●──────────┤                                     [☁️ Deploy]     │   │
│    │    └─────────────┘                                                     │   │
│    ├────────────────────────────────────────────────────────────────────────┤   │
│    │  🔒 JWT Auth  [Configured ●]                                    [▼]    │   │
│    │  Access Token: [15m ▼]  Refresh: [7d ▼]  Email Verify: [✓]  ...       │   │
├────┴────────────────────────────────────────────────────────────────────────┴───┤
│  [CMC: 156]  [VIF Active]  │  🖥️ ❌ ⚠️ 📊  ◀▶  🧠 🐛 📈 🔥  │  Port: 3002  DAC│
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ **CHECKLIST**

### **Phase 1: Core Integration**
- [ ] Add `backend-design` to `MainViewType`
- [ ] Add `Server` icon to toolbar buttons
- [ ] Create `BackendDesignView.tsx`
- [ ] Add lazy loading wrapper
- [ ] Test main view switching

### **Phase 2: Canvas**
- [ ] Create `DesignCanvas.tsx`
- [ ] Create `TemplateNode.tsx`
- [ ] Implement node rendering
- [ ] Implement edge rendering
- [ ] Implement drag-and-drop

### **Phase 3: Template Library**
- [ ] Create `TemplateLibraryPanel.tsx`
- [ ] Add to right panel types
- [ ] Load template data
- [ ] Implement search
- [ ] Implement filtering

### **Phase 4: Properties**
- [ ] Create `PropertiesPanel.tsx`
- [ ] Create config form components
- [ ] Connect to node selection
- [ ] Persist to store

### **Phase 5: Generation**
- [ ] Create code generation service
- [ ] Create code preview modal
- [ ] Create deployment modal
- [ ] Test end-to-end

---

## 🔗 **REFERENCES**

- **Layout System:** `src/components/IDELayout.tsx`
- **Top Bar:** `src/components/TopBar.tsx`
- **Design Tokens:** `src/styles/design-tokens.css`
- **Context Web (React Flow):** `src/panels/ContextWebPanel.tsx`
- **Panel Store:** `src/store/panelStore.ts`
- **Lazy Loading:** `src/utils/performance.tsx`

---

**Status:** Design Complete ✅  
**Next Step:** Begin Phase 1 Implementation  
**Estimated Duration:** 3-4 weeks  
**Integration Risk:** Low (follows existing patterns)

**Built with DAC IDE design system** 💙✨

