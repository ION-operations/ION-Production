# Dual-Mode AI Interaction System
## Canvas Mode + Chat Mode Architecture

**Vision:** Two powerful modes that complement each other - a living, editable Canvas document and a traditional Chat conversation.

---

## 🎯 **Two Distinct Modes**

### **1. Canvas Mode** (Living Document)
**Like ChatGPT Canvas, but more powerful**

**Purpose:**
- Growing, editable document that accumulates knowledge
- Used as the "reply view" from AI discussions
- Evolves over time like a journal or project blueprint
- Highly editable by both user and AI

**Characteristics:**
- ✅ Persistent across sessions
- ✅ Continuously editable
- ✅ Grows organically
- ✅ Multi-user/AI collaboration
- ✅ Version history
- ✅ Rich content support
- ✅ AIM-OS integration

**Use Cases:**
- Project blueprints
- Research journals
- Documentation
- Design documents
- Learning notes
- Meeting notes
- Planning documents
- Knowledge bases

---

### **2. Chat Mode** (Conversation)
**Like ChatGPT Chat, but enhanced**

**Purpose:**
- Traditional conversation flow
- Quick questions and answers
- Discussion and exploration
- Progresses linearly through messages

**Characteristics:**
- ✅ Message-by-message progression
- ✅ Thread-based conversations
- ✅ Quick interactions
- ✅ Can spawn Canvas documents
- ✅ Context-aware responses
- ✅ AIM-OS integration

**Use Cases:**
- Quick questions
- Exploratory discussions
- Problem-solving sessions
- Code debugging
- General conversation

---

## 🔄 **Mode Interaction**

### **Chat → Canvas Flow**
```
User asks question in Chat
  ↓
AI responds with answer
  ↓
User clicks "Add to Canvas" or "Create Canvas"
  ↓
Content added to Canvas document
  ↓
Canvas becomes editable, growing document
```

### **Canvas → Chat Flow**
```
User editing Canvas
  ↓
User highlights section
  ↓
User asks "Can you expand this?"
  ↓
AI responds in Chat
  ↓
User drags Chat response into Canvas
  ↓
Canvas updated with new content
```

### **Dual-Mode Workflow**
```
1. User starts conversation in Chat
2. AI provides answer
3. User creates Canvas from answer
4. Canvas becomes living document
5. User edits Canvas directly
6. User asks follow-up in Chat
7. AI enhances Canvas based on Chat discussion
8. Canvas grows and evolves
```

---

## 📝 **Canvas Mode Features**

### **Core Editing Capabilities**

#### **1. Rich Text Editing**
- **Markdown support** (headings, lists, bold, italic)
- **Code blocks** (syntax highlighting, execution)
- **Math rendering** (LaTeX support)
- **Images** (upload, embed, edit)
- **Tables** (editable, sortable)
- **Links** (internal, external)
- **Professional icons** (emoji replacement)

#### **2. AI Editing Modes**
- **Inline editing**: AI edits text directly in place
- **Suggestions**: AI suggests improvements (accept/reject)
- **Expansion**: AI expands sections on request
- **Refinement**: AI refines and improves content
- **Restructuring**: AI reorganizes content structure
- **Summarization**: AI creates summaries

#### **3. User Editing Modes**
- **Direct editing**: Type/edit directly in Canvas
- **Drag & drop**: Rearrange sections
- **Multi-select**: Edit multiple sections
- **Undo/redo**: Full history support
- **Comments**: Add notes and annotations
- **Highlights**: Mark important sections

#### **4. Collaborative Editing**
- **Real-time sync**: Multiple users/AI editing simultaneously
- **Conflict resolution**: Smart merge for conflicts
- **Change tracking**: See who changed what
- **Version history**: Full document history
- **Branches**: Create document branches
- **Merges**: Merge branches back

---

## 🎨 **Canvas UI Components**

### **Canvas Editor**
```typescript
<CanvasEditor
  content={canvasContent}
  onEdit={(changes) => updateCanvas(changes)}
  onAISuggest={(section) => requestAISuggestion(section)}
  onVersionHistory={() => showHistory()}
  onCollaborate={() => enableCollaboration()}
/>
```

### **Section Components**
```typescript
// Editable text section
<EditableSection
  content={text}
  onEdit={(newText) => updateSection(newText)}
  onAISuggest={() => getAISuggestion()}
  onExpand={() => expandSection()}
/>

// Code block with execution
<EditableCodeBlock
  code={code}
  language="python"
  executable={true}
  onEdit={(newCode) => updateCode(newCode)}
  onExecute={() => executeCode()}
/>

// Image with editing
<EditableImage
  src={imageSrc}
  onEdit={() => openImageEditor()}
  onReplace={(newImage) => replaceImage(newImage)}
/>
```

### **AI Enhancement Panel**
```typescript
<AIEnhancementPanel
  section={selectedSection}
  suggestions={aiSuggestions}
  onApply={(suggestion) => applySuggestion(suggestion)}
  onExpand={() => expandSection()}
  onRefine={() => refineSection()}
  onRestructure={() => restructureSection()}
/>
```

---

## 💬 **Chat Mode Features**

### **Enhanced Chat Capabilities**

#### **1. Message Types**
- **Text messages** (with markdown)
- **Code blocks** (with execution)
- **Images** (with analysis)
- **Canvas references** (links to Canvas documents)
- **Interactive components** (forms, charts)

#### **2. Canvas Integration**
- **"Add to Canvas"** button on messages
- **"Create Canvas"** from conversation
- **Canvas preview** in chat
- **Quick edit** Canvas from chat
- **Canvas suggestions** based on chat

#### **3. Context Awareness**
- **Canvas context**: Chat aware of active Canvas
- **Memory integration**: Uses CMC for context
- **Confidence indicators**: Shows VIF confidence
- **Evidence trails**: Shows sources
- **Knowledge graph**: Visualizes connections

---

## 🔧 **Technical Architecture**

### **Canvas Document Structure**
```typescript
interface CanvasDocument {
  id: string
  title: string
  content: CanvasSection[]
  metadata: {
    createdAt: Date
    updatedAt: Date
    version: number
    author: string
    collaborators: string[]
  }
  history: CanvasVersion[]
  branches: CanvasBranch[]
  aimos: {
    confidence: number
    evidence: Evidence[]
    memory: MemoryReference[]
    knowledgeGraph: KnowledgeNode[]
  }
}

interface CanvasSection {
  id: string
  type: 'text' | 'code' | 'image' | 'table' | 'math' | 'component'
  content: any
  metadata: {
    createdBy: 'user' | 'ai'
    editedBy: string[]
    confidence?: number
    evidence?: Evidence[]
  }
  editable: boolean
  aiSuggestions?: AISuggestion[]
}
```

### **Chat Message Structure**
```typescript
interface ChatMessage {
  id: string
  role: 'user' | 'ai'
  content: MessageContent[]
  timestamp: Date
  canvasReferences?: CanvasReference[]
  aimos: {
    confidence: number
    evidence: Evidence[]
    memory: MemoryReference[]
  }
  actions: {
    addToCanvas?: boolean
    createCanvas?: boolean
    executeCode?: boolean
  }
}
```

---

## 🎯 **Key Features**

### **1. Seamless Mode Switching**
- Switch between Chat and Canvas instantly
- Content flows between modes
- Context preserved across modes
- Unified search across both

### **2. AI-Powered Enhancement**
- AI suggests improvements to Canvas
- AI expands sections on request
- AI refines content based on feedback
- AI maintains consistency across edits

### **3. Version Control**
- Full document history
- Branch and merge support
- Compare versions
- Rollback to previous versions
- AI-generated summaries of changes

### **4. Collaboration**
- Real-time multi-user editing
- AI as collaborator
- Comments and annotations
- Change tracking
- Conflict resolution

### **5. AIM-OS Integration**
- **CMC**: Persistent memory across sessions
- **VIF**: Confidence scores for all content
- **SEG**: Knowledge graph visualization
- **TCS**: Timeline of document evolution
- **CAS**: Quality metrics for content

---

## 🚀 **Implementation Phases**

### **Phase 1: Foundation** (Current)
- ✅ Rich content rendering (FilePreview)
- ✅ Basic editing capabilities
- ✅ AIM-OS integration hooks

### **Phase 2: Canvas Mode** (Next)
- Canvas document structure
- Rich text editing
- Section management
- Version history
- AI enhancement panel

### **Phase 3: Chat Mode**
- Enhanced chat interface
- Canvas integration
- Message types
- Context awareness

### **Phase 4: Collaboration**
- Real-time sync
- Multi-user editing
- Conflict resolution
- Comments and annotations

### **Phase 5: Advanced Features**
- Branch and merge
- Advanced AI suggestions
- Knowledge graph visualization
- Performance optimization

---

## 💡 **User Experience Flow**

### **Example: Project Blueprint**

1. **User starts in Chat:**
   ```
   User: "I want to build a web app for task management"
   ```

2. **AI responds in Chat:**
   ```
   AI: "Here's a comprehensive plan for your task management app..."
   [Add to Canvas] [Create Canvas]
   ```

3. **User creates Canvas:**
   - Canvas document created with AI's response
   - User can now edit directly
   - Canvas becomes living document

4. **User edits Canvas:**
   - Adds more details
   - Rearranges sections
   - Adds code examples
   - Inserts images

5. **User asks follow-up in Chat:**
   ```
   User: "Can you expand the authentication section?"
   ```

6. **AI enhances Canvas:**
   - AI adds detailed authentication section
   - Canvas grows organically
   - User can refine further

7. **Canvas evolves:**
   - Becomes comprehensive blueprint
   - Continuously editable
   - Version history maintained
   - Ready for implementation

---

## 🎨 **UI Layout**

### **Canvas Mode Layout**
```
┌─────────────────────────────────────────┐
│ [Canvas Title] [Edit] [AI Enhance] [History] │
├─────────────────────────────────────────┤
│                                         │
│  [Rich Content Editor]                 │
│  - Editable sections                   │
│  - AI suggestions                      │
│  - Version history                     │
│                                         │
│  [Sidebar: AI Enhancement Panel]       │
│  - Suggestions                         │
│  - Expand options                      │
│  - Refine options                      │
│                                         │
└─────────────────────────────────────────┘
```

### **Chat Mode Layout**
```
┌─────────────────────────────────────────┐
│ [Chat Title] [New Canvas] [Settings]   │
├─────────────────────────────────────────┤
│                                         │
│  [Message Thread]                      │
│  - User messages                       │
│  - AI responses                        │
│  - Canvas references                   │
│                                         │
│  [Input Area]                          │
│  [Send] [Add to Canvas]                │
│                                         │
└─────────────────────────────────────────┘
```

### **Dual-Mode Layout**
```
┌──────────────┬──────────────────────────┐
│   Chat       │      Canvas              │
│              │                          │
│ [Messages]   │  [Editable Document]     │
│              │                          │
│ [Input]      │  [AI Enhancement]        │
│              │                          │
└──────────────┴──────────────────────────┘
```

---

## 🔮 **Future Enhancements**

### **Advanced Canvas Features**
- **Templates**: Pre-built Canvas templates
- **Plugins**: Extend Canvas with plugins
- **Export**: Export to PDF, Markdown, HTML
- **Import**: Import from various formats
- **Search**: Full-text search across Canvas
- **Tags**: Organize Canvas with tags

### **Advanced Chat Features**
- **Voice input/output**: Speak to AI
- **Image analysis**: Upload and analyze images
- **Code execution**: Run code in chat
- **Multi-agent**: Multiple AI agents
- **Streaming**: Real-time response streaming

### **Integration Features**
- **Git integration**: Version control with Git
- **API integration**: Connect to external APIs
- **Database integration**: Query databases
- **File system**: Access local files
- **Web scraping**: Extract web content

---

**Goal:** Create a powerful dual-mode system where Chat enables quick interactions and Canvas enables deep, evolving document creation - both seamlessly integrated with AIM-OS capabilities.

