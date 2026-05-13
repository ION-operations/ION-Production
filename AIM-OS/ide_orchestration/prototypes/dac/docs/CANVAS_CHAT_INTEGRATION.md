# Canvas Mode Integration with Existing Chat System
## Enhancing AIChatManagement with Living Document Capabilities

**Current State:** We have a sophisticated chat system with:
- ✅ Channel-based organization (Discord-style)
- ✅ AIM-OS integration (confidence, evidence, work references)
- ✅ Multi-agent support
- ✅ Context management
- ✅ Message threading

**Enhancement:** Add Canvas Mode as a living document system that integrates seamlessly with chat.

---

## 🔄 **Integration Points**

### **1. Canvas Creation from Chat**

#### **From Message Actions**
```typescript
// Add to ChatMessage interface
interface ChatMessage {
  // ... existing fields ...
  canvasActions?: {
    addToCanvas?: string  // Canvas ID to add to
    createCanvas?: boolean  // Create new canvas from this message
    canvasReference?: string  // Reference to existing canvas
  }
}
```

#### **UI Components**
```typescript
// In message renderer
<MessageActions>
  <button onClick={() => addToCanvas(message.id)}>
    Add to Canvas
  </button>
  <button onClick={() => createCanvasFromMessage(message.id)}>
    Create Canvas
  </button>
  {canvasReference && (
    <button onClick={() => openCanvas(canvasReference)}>
      View Canvas
    </button>
  )}
</MessageActions>
```

---

### **2. Canvas Document Structure**

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
    createdFrom?: string  // Chat message ID that created this
    relatedMessages?: string[]  // Chat messages related to this canvas
    collaborators: string[]
  }
  history: CanvasVersion[]
  branches: CanvasBranch[]
  aimos: {
    confidence: number
    evidence: Evidence[]
    memory: MemoryReference[]
    knowledgeGraph: KnowledgeNode[]
    workReferences?: WorkReference  // From chat system
    evidenceTrail?: EvidenceTrail  // From chat system
    goalAlignment?: GoalAlignment  // From chat system
  }
  chatIntegration: {
    relatedChannel?: string
    relatedMessages: string[]
    lastSyncedAt: Date
  }
}
```

---

### **3. Canvas Section Types**

```typescript
interface CanvasSection {
  id: string
  type: 'text' | 'code' | 'image' | 'table' | 'math' | 'component' | 'chat-reference'
  content: any
  metadata: {
    createdBy: 'user' | 'ai' | 'chat'
    createdFrom?: string  // Chat message ID
    editedBy: string[]
    confidence?: number
    evidence?: Evidence[]
    timestamp: Date
  }
  editable: boolean
  aiSuggestions?: AISuggestion[]
  chatReferences?: string[]  // Related chat messages
}
```

---

### **4. Chat → Canvas Flow**

#### **Scenario 1: Create Canvas from Message**
```
1. User receives AI response in chat
2. User clicks "Create Canvas"
3. Canvas created with:
   - Title: Auto-generated from message content
   - Initial content: Message content formatted
   - Metadata: Links to original message
   - AIM-OS: Inherits confidence, evidence, work references
4. Canvas opens in Canvas Mode
5. User can now edit and enhance
```

#### **Scenario 2: Add Message to Existing Canvas**
```
1. User selects message in chat
2. User clicks "Add to Canvas"
3. Canvas selector appears
4. User selects canvas
5. Message content added as new section
6. Section metadata links to original message
7. Canvas updated with new content
```

#### **Scenario 3: AI Enhances Canvas from Chat**
```
1. User asks question in chat about Canvas content
2. AI responds with enhancement
3. User clicks "Apply to Canvas"
4. AI enhancement applied to Canvas
5. Canvas section updated
6. Change tracked in version history
```

---

### **5. Canvas → Chat Flow**

#### **Scenario 1: Reference Canvas in Chat**
```
1. User mentions Canvas in chat message
2. Canvas preview appears in chat
3. User can click to open Canvas
4. Chat context includes Canvas content
5. AI responses aware of Canvas context
```

#### **Scenario 2: Ask About Canvas Section**
```
1. User highlights section in Canvas
2. User asks question in chat
3. Chat context includes:
   - Selected section
   - Full Canvas content
   - Canvas history
4. AI responds with section-specific answer
5. User can apply answer to Canvas
```

#### **Scenario 3: Canvas Triggers Chat Discussion**
```
1. User edits Canvas section
2. AI detects potential issues
3. AI suggests improvement in chat
4. User discusses in chat
5. User applies changes to Canvas
```

---

## 🎨 **UI Integration**

### **Chat Panel with Canvas Actions**
```typescript
// Enhanced message renderer
<ChatMessageComponent message={message}>
  <MessageContent content={message.content} />
  <MessageActions>
    <button onClick={() => addToCanvas(message.id)}>
      <FileText /> Add to Canvas
    </button>
    <button onClick={() => createCanvas(message.id)}>
      <Plus /> Create Canvas
    </button>
    {message.canvasReference && (
      <button onClick={() => openCanvas(message.canvasReference)}>
        <ExternalLink /> View Canvas
      </button>
    )}
  </MessageActions>
  <AIMOSMetadata 
    confidence={message.confidence}
    evidence={message.evidence_trail}
    workReferences={message.work_references}
  />
</ChatMessageComponent>
```

### **Canvas Panel with Chat Integration**
```typescript
// Canvas editor with chat sidebar
<CanvasEditor canvas={canvas}>
  <CanvasToolbar>
    <button onClick={() => askAIAboutSection(selectedSection)}>
      <MessageSquare /> Ask AI
    </button>
    <button onClick={() => enhanceWithAI(selectedSection)}>
      <Sparkles /> Enhance
    </button>
    <button onClick={() => showRelatedChat()}>
      <Hash /> Related Chat
    </button>
  </CanvasToolbar>
  <CanvasContent sections={canvas.content} />
  <ChatSidebar 
    relatedMessages={canvas.chatIntegration.relatedMessages}
    onMessageSelect={(msgId) => highlightSection(msgId)}
  />
</CanvasEditor>
```

---

## 🔧 **Technical Implementation**

### **Canvas Store**
```typescript
// New Zustand store for Canvas documents
interface CanvasStore {
  canvases: Record<string, CanvasDocument>
  activeCanvas: string | null
  createCanvas: (fromMessageId?: string) => string
  updateCanvas: (id: string, updates: Partial<CanvasDocument>) => void
  addSection: (canvasId: string, section: CanvasSection) => void
  updateSection: (canvasId: string, sectionId: string, updates: Partial<CanvasSection>) => void
  deleteSection: (canvasId: string, sectionId: string) => void
  addMessageToCanvas: (canvasId: string, messageId: string) => void
  linkCanvasToMessage: (canvasId: string, messageId: string) => void
  getCanvasHistory: (canvasId: string) => CanvasVersion[]
  createBranch: (canvasId: string, branchName: string) => string
  mergeBranch: (canvasId: string, branchId: string) => void
}
```

### **Canvas Service**
```typescript
// Service for Canvas operations
class CanvasService {
  // Create canvas from chat message
  async createFromMessage(messageId: string): Promise<CanvasDocument> {
    const message = await getMessage(messageId)
    return {
      id: generateId(),
      title: extractTitle(message.content),
      content: [{
        id: generateId(),
        type: 'text',
        content: formatMessageContent(message.content),
        metadata: {
          createdBy: 'chat',
          createdFrom: messageId,
          timestamp: new Date()
        },
        editable: true
      }],
      metadata: {
        createdAt: new Date(),
        updatedAt: new Date(),
        version: 1,
        author: message.role === 'user' ? 'user' : message.agent || 'ai',
        createdFrom: messageId,
        relatedMessages: [messageId],
        collaborators: []
      },
      aimos: {
        confidence: message.confidence || 0.8,
        evidence: message.evidence_trail?.evidence || [],
        memory: [],
        knowledgeGraph: [],
        workReferences: message.work_references,
        evidenceTrail: message.evidence_trail,
        goalAlignment: message.goal_alignment
      },
      chatIntegration: {
        relatedChannel: message.connected_channel,
        relatedMessages: [messageId],
        lastSyncedAt: new Date()
      }
    }
  }

  // Add message to canvas
  async addMessageToCanvas(canvasId: string, messageId: string): Promise<void> {
    const canvas = await getCanvas(canvasId)
    const message = await getMessage(messageId)
    
    const newSection: CanvasSection = {
      id: generateId(),
      type: 'chat-reference',
      content: {
        messageId,
        content: message.content,
        timestamp: message.timestamp
      },
      metadata: {
        createdBy: 'chat',
        createdFrom: messageId,
        timestamp: new Date()
      },
      editable: true,
      chatReferences: [messageId]
    }
    
    canvas.content.push(newSection)
    canvas.metadata.relatedMessages.push(messageId)
    canvas.chatIntegration.relatedMessages.push(messageId)
    canvas.metadata.updatedAt = new Date()
    
    await saveCanvas(canvas)
  }

  // AI enhancement
  async enhanceSection(canvasId: string, sectionId: string, enhancement: string): Promise<void> {
    const canvas = await getCanvas(canvasId)
    const section = canvas.content.find(s => s.id === sectionId)
    
    if (!section) return
    
    // Apply AI enhancement
    section.content = mergeContent(section.content, enhancement)
    section.metadata.editedBy.push('ai')
    section.metadata.timestamp = new Date()
    
    // Create version snapshot
    await createVersion(canvasId, canvas)
    
    await saveCanvas(canvas)
  }
}
```

---

## 🎯 **User Experience Flow**

### **Example: Project Blueprint Creation**

1. **User starts conversation in Chat:**
   ```
   Channel: #ui-building
   User: "I want to build a task management app"
   ```

2. **AI responds:**
   ```
   AI: "Here's a comprehensive plan..."
   [Add to Canvas] [Create Canvas]
   ```

3. **User creates Canvas:**
   - Canvas created: "Task Management App Blueprint"
   - Content: AI's response formatted as sections
   - Linked to chat message
   - Inherits AIM-OS metadata

4. **User edits Canvas:**
   - Adds more details
   - Rearranges sections
   - Adds code examples
   - Inserts images

5. **User asks follow-up in Chat:**
   ```
   User: "Can you expand the authentication section?"
   ```

6. **AI responds:**
   ```
   AI: "Here's a detailed authentication flow..."
   [Apply to Canvas] [Add to Canvas]
   ```

7. **User applies to Canvas:**
   - Authentication section expanded
   - Canvas updated
   - Version history created
   - Change linked to chat message

8. **Canvas evolves:**
   - Grows organically
   - Continuously editable
   - Version history maintained
   - Linked to chat discussions
   - Ready for implementation

---

## 🚀 **Implementation Plan**

### **Phase 1: Canvas Foundation**
- [ ] Canvas document structure
- [ ] Canvas store (Zustand)
- [ ] Canvas service
- [ ] Basic Canvas editor UI

### **Phase 2: Chat Integration**
- [ ] "Create Canvas" from message
- [ ] "Add to Canvas" from message
- [ ] Canvas references in chat
- [ ] Chat sidebar in Canvas

### **Phase 3: Editing Capabilities**
- [ ] Rich text editing
- [ ] Section management
- [ ] AI enhancement panel
- [ ] Version history

### **Phase 4: Advanced Features**
- [ ] Real-time collaboration
- [ ] Branch and merge
- [ ] Advanced AI suggestions
- [ ] Performance optimization

---

**Goal:** Seamlessly integrate Canvas Mode with existing chat system, creating a powerful dual-mode experience where chat enables quick interactions and Canvas enables deep, evolving document creation.

