# Code + Documentation Side-by-Side Viewer

## Vision

A revolutionary IDE feature that displays code alongside its matching documentation in a synchronized, side-by-side view. When you select code elements (functions, classes, variables), the corresponding documentation sentences/paragraphs are automatically highlighted, showing perfect alignment between implementation and documentation.

## Key Features

### 1. **Side-by-Side Layout**
- **Left Panel:** Code editor (Monaco Editor)
- **Right Panel:** Documentation viewer (with syntax highlighting for markdown/docs)
- **Resizable:** Drag to adjust panel sizes
- **Synchronized Scrolling:** Optional - scroll both panels in sync

### 2. **Synchronized Highlighting**
- **Code Selection → Doc Highlight:**
  - When user selects/hovers a function/class in code
  - Automatic highlight of corresponding doc sentences
  - Visual connection indicator (arrow/line between panels)

- **Doc Selection → Code Highlight:**
  - When user selects/hovers documentation section
  - Automatic highlight of corresponding code implementation
  - Visual connection indicator

### 3. **Element Mapping**
**Supported Code Elements:**
- Functions/Methods
- Classes/Interfaces
- Variables/Constants
- Types/Interfaces
- Props/Parameters

**Doc Matching:**
- Function documentation
- Class documentation
- Parameter descriptions
- Type descriptions
- Usage examples

### 4. **Doc Sources**
- **Inline Comments:** Extract JSDoc/docstrings
- **Separate Docs:** Link to markdown/doc files
- **AIM-OS Docs:** Integrate with L0-L4 documentation system
- **External Docs:** Link to external documentation

## Technical Implementation

### Component Structure

```
CodeDocsViewer.tsx (Main Component)
├── CodePanel.tsx (Monaco Editor)
├── DocsPanel.tsx (Documentation Viewer)
├── SynchronizationEngine.ts (Mapping Logic)
└── HighlightingManager.ts (Visual Feedback)
```

### Architecture

**1. Code Parser & Mapping**
- Parse code to extract elements (AST parsing)
- Generate element signatures (function name, params, etc.)
- Store position ranges (start/end line/column)

**2. Documentation Parser & Mapping**
- Parse documentation (JSDoc, markdown, etc.)
- Extract doc sections (descriptions, params, examples)
- Map to code elements

**3. Synchronization Engine**
- Maintain mapping between code elements and doc sections
- Handle selection events from both panels
- Trigger highlighting in opposite panel

**4. Highlighting System**
- Code highlights: Monaco Editor decorations
- Doc highlights: Custom markdown rendering with CSS
- Connection indicators: SVG lines/arrows between panels

### Data Structure

```typescript
interface ElementMapping {
  codeElement: {
    type: 'function' | 'class' | 'variable' | 'type'
    name: string
    signature: string
    range: {
      start: { line: number, column: number }
      end: { line: number, column: number }
    }
  }
  docElement: {
    type: 'description' | 'param' | 'return' | 'example'
    content: string
    range: {
      start: { line: number, column: number }
      end: { line: number, column: number }
    }
  }
  source: 'inline' | 'jsdoc' | 'separate_doc' | 'aimos'
}
```

## UI/UX Design

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Top Bar: [Code Only] [Code+Doc Split] [Doc Only]      │
├─────────────────────────┬───────────────────────────────┤
│                         │                               │
│   CODE PANEL            │    DOCUMENTATION PANEL        │
│   (Monaco Editor)       │    (Markdown Renderer)        │
│                         │                               │
│   function myFunc() {   │    ## myFunc()                │
│     // highlighted      │    → highlighted              │
│   }                     │                               │
│                         │    Does something useful      │
│   const x = 5;          │                               │
│                         │    - highlighted element      │
│                         │                               │
│                         │    **Parameters:**            │
│                         │    - `arg1`: description      │
│                         │                               │
│   Visual Connector →    │                               │
│                         │                               │
└─────────────────────────┴───────────────────────────────┘
```

### Interaction Patterns

**1. Hover to Preview:**
- Hover code element → Highlight matching doc
- Hover doc section → Highlight matching code
- Non-intrusive, quick reference

**2. Click to Lock:**
- Click element → Lock both panels to that element
- Disable scrolling until unlocked
- Show "locked" indicator
- Click again to unlock

**3. Navigate & Sync:**
- Arrow keys move through linked elements
- Both panels scroll together
- Visual indicator shows connection

**4. Highlight Colors:**
- Code selection: Blue background
- Doc highlight: Yellow/green background
- Connection line: Animated pulse effect

## Integration with IDELayout

### New Main Tab Option

Add to `mainPage` type:
```typescript
'mainPage' → 'code' | 'preview' | 'ui' | 'backend' | 'orchestration' | 'code-docs'
```

### Implementation in IDELayout

```typescript
else if (mainPage === 'code-docs') {
  return (
    <CodeDocsViewer
      codeFile={activeTab?.fileName}
      docFile={getAssociatedDoc(activeTab?.fileName)}
      onHighlight={(element) => syncPanels(element)}
    />
  )
}
```

## Future Enhancements

### Phase 2: Advanced Features
- **Live Documentation:** Generate docs from code patterns
- **Doc Validation:** Check if code matches documented behavior
- **Cross-Reference:** Link to related elements in both panels
- **Search & Jump:** Search in code, jump to doc (and vice versa)

### Phase 3: AI Integration
- **Auto-Generate Docs:** AI generates docs from code
- **Sync Check:** AI validates code-doc alignment
- **Suggest Edits:** AI suggests doc updates when code changes

## Success Metrics

1. **Alignment Accuracy:** Code ↔ Doc matching precision
2. **User Engagement:** Time spent in Code+Doc mode
3. **Documentation Quality:** Improvement in doc completeness
4. **Development Speed:** Faster coding with better doc reference

## Implementation Priority

**Priority:** HIGH (Immediate Value)
**Complexity:** Medium
**Estimated Time:** 2-3 days

**Steps:**
1. Create `CodeDocsViewer.tsx` component
2. Implement basic side-by-side layout
3. Add code parsing and doc mapping
4. Implement synchronized highlighting
5. Add visual connection indicators
6. Integrate with IDELayout
7. Test with real codebase examples

## Next Steps

1. ✅ Document architecture (this file)
2. Update `IDELayout.tsx` to add 'code-docs' tab
3. Create `CodeDocsViewer.tsx` component
4. Implement code parsing (AST)
5. Implement doc parsing (markdown/JSDoc)
6. Implement synchronization engine
7. Add highlighting system
8. Test with real code examples
9. Integrate with AIM-OS docs system

---

**Status:** Architecture Documented
**Next:** Implement basic component structure
