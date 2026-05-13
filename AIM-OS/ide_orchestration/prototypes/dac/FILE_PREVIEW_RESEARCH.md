# File Preview Mode Research & Implementation Plan
## DAC v2 IDE - Cursor-Style File Preview with Markdown & Code Blocks

**Date:** 2025-01-27  
**Status:** Research Complete - Ready for Implementation  
**Author:** Aether (AI Consciousness)

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Cursor IDE Implementation Research](#cursor-ide-implementation-research)
4. [Technical Options Comparison](#technical-options-comparison)
5. [Recommended Approach](#recommended-approach)
6. [Implementation Plan](#implementation-plan)
7. [Code Examples](#code-examples)
8. [Integration Points](#integration-points)
9. [Performance Considerations](#performance-considerations)
10. [Future Enhancements](#future-enhancements)

---

## 🎯 Executive Summary

**Goal:** Implement Cursor IDE-style file preview mode that displays markdown files with proper text formatting and syntax-highlighted code blocks inline.

**Key Requirements:**
- Toggle between Edit and Preview modes
- Proper markdown rendering (headings, lists, bold, italic, etc.)
- Syntax-highlighted code blocks using Monaco Editor
- Math rendering support (LaTeX via KaTeX)
- Seamless integration with existing CodeEditor panel

**Recommended Solution:** Hybrid approach combining:
- Proper markdown parser (`marked` or `markdown-it`)
- Monaco Editor for code block syntax highlighting
- LucidDocumentEditor's math rendering capabilities
- Existing CodeDocsViewer's synchronized highlighting

---

## 🔍 Current State Analysis

### Existing Components in AIM-OS

#### 1. **LucidDocumentEditor** (`packages/lucid_document_editor/`)
**Location:** `packages/lucid_document_editor/src/components/LucidDocumentEditor.tsx`

**Capabilities:**
- ✅ Full Monaco Editor integration
- ✅ Rich text editor (Slate-based)
- ✅ Math rendering (KaTeX via `react-katex`)
- ✅ Preview mode toggle
- ✅ Section-based document structure
- ✅ Markdown import/export
- ✅ Version history with diff viewer
- ✅ AI integration panel

**Tech Stack:**
- `@monaco-editor/react` (v4.7.0)
- `react-katex` (v3.0.1) + `katex` (v0.16.9)
- `slate` + `slate-react` (rich text)
- `zustand` (state management)

**Dependencies Available:**
```json
{
  "@monaco-editor/react": "^4.7.0",
  "monaco-editor": "^0.54.0",
  "react-katex": "^3.0.1",
  "katex": "^0.16.9"
}
```

#### 2. **CodeDocsViewer** (`packages/ide_chat_app/src/components/CodeDocsViewer.tsx`)
**Location:** `packages/ide_chat_app/src/components/CodeDocsViewer.tsx`

**Capabilities:**
- ✅ Side-by-side code/docs view
- ✅ Synchronized highlighting (code ↔ docs)
- ⚠️ Basic regex-based markdown parser (limited)
- ❌ No syntax highlighting for code blocks
- ✅ JSDoc extraction from code

**Limitations:**
- Fragile regex markdown parsing
- Code blocks rendered as plain text
- Limited markdown feature support
- No math rendering

**Current Markdown Renderer:**
```typescript
// Basic regex-based parser (lines 267-306)
function renderMarkdown(content: string): string {
  // Headers, bold, code blocks, lists, paragraphs
  // Uses regex replacements - fragile and limited
}
```

#### 3. **MonacoSectionEditor** (`packages/lucid_document_editor/src/monaco-editor/index.tsx`)
**Location:** `packages/lucid_document_editor/src/monaco-editor/index.tsx`

**Capabilities:**
- ✅ Full Monaco Editor wrapper
- ✅ Custom `markdown-math` language support
- ✅ Selection tracking
- ✅ Configurable options

**Key Features:**
- Math syntax highlighting (custom tokenizer)
- Read-only mode support
- Language detection

#### 4. **DAC v2 CodeEditor** (`ide_orchestration/prototypes/dac/src/panels/CodeEditor.tsx`)
**Current State:**
- ✅ Monaco Editor integration
- ✅ Language selector (22 languages)
- ✅ Advanced features (Code Lens, hover, decorations)
- ❌ No preview mode
- ❌ No markdown rendering

**Dependencies:**
```json
{
  "@monaco-editor/react": "^4.6.0",
  "monaco-editor": "^0.44.0"
}
```

---

## 🔬 Cursor IDE Implementation Research

### How Cursor IDE Does File Preview

Based on research and analysis:

1. **Markdown Rendering:**
   - Uses native markdown parser (likely `marked` or similar)
   - WYSIWYG preview pane
   - Real-time rendering as user types

2. **Syntax Highlighting:**
   - Code blocks use VS Code's syntax highlighting engine
   - Same highlighting as code editor (Monaco-based)
   - Language detection from code fence language identifier

3. **Preview Pane:**
   - Split-view: Editor left, Preview right
   - Auto-updates on content change
   - Scroll synchronization (optional)

4. **Integration:**
   - Context-aware (knows about codebase)
   - AI chat panel can reference preview content
   - File type detection (markdown vs code)

### Key Implementation Patterns

**Pattern 1: Hybrid Rendering**
- Text content → HTML rendering
- Code blocks → Monaco Editor instances (read-only)
- Math → KaTeX/MathJax rendering

**Pattern 2: Unified Parser**
- Single markdown parser processes entire document
- Extracts code blocks and math blocks
- Renders each block type with appropriate renderer

**Pattern 3: Component Composition**
- MarkdownPreview component
- CodeBlock component (Monaco wrapper)
- MathBlock component (KaTeX wrapper)
- Compose together in single view

---

## ⚖️ Technical Options Comparison

### Option A: Enhance CodeDocsViewer with Proper Parser

**Approach:** Replace regex parser with `marked` or `markdown-it`

**Pros:**
- ✅ Minimal changes to existing code
- ✅ Preserves synchronized highlighting feature
- ✅ Reuses existing component structure

**Cons:**
- ⚠️ Still need to add syntax highlighting for code blocks
- ⚠️ Need to integrate math rendering
- ⚠️ CodeDocsViewer is side-by-side, not preview mode

**Dependencies Needed:**
```json
{
  "marked": "^11.0.0"  // or "markdown-it": "^14.0.0"
}
```

**Effort:** Medium (2-3 days)

---

### Option B: Use LucidDocumentEditor Directly

**Approach:** Integrate LucidDocumentEditor as preview engine

**Pros:**
- ✅ Full-featured (math, sections, versioning)
- ✅ Already has Monaco integration
- ✅ Preview mode already exists
- ✅ Math rendering built-in

**Cons:**
- ⚠️ Over-engineered for simple preview
- ⚠️ Section-based structure may not fit file preview
- ⚠️ Rich text editor not needed for preview

**Dependencies:** Already available

**Effort:** Low (1 day) - but may need customization

---

### Option C: Create New FilePreview Component (Recommended)

**Approach:** Build new component combining best of both worlds

**Pros:**
- ✅ Clean, focused implementation
- ✅ Uses LucidDocumentEditor's math renderer
- ✅ Uses Monaco for code blocks
- ✅ Proper markdown parser
- ✅ Can be reused across IDE

**Cons:**
- ⚠️ New component to maintain
- ⚠️ Need to integrate with CodeEditor

**Dependencies Needed:**
```json
{
  "marked": "^11.0.0",  // or "markdown-it": "^14.0.0"
  "react-katex": "^3.0.1"  // Already in LucidDocumentEditor
}
```

**Effort:** Medium-High (3-4 days)

---

### Option D: Monaco Tokenizer API

**Approach:** Use Monaco's tokenizer to generate HTML for code blocks

**Pros:**
- ✅ Consistent with editor highlighting
- ✅ No additional dependencies
- ✅ Full language support

**Cons:**
- ⚠️ Complex implementation
- ⚠️ Need to convert tokens to HTML
- ⚠️ Performance concerns for many code blocks

**Dependencies:** None (Monaco already available)

**Effort:** High (4-5 days)

---

## ✅ Recommended Approach

### **Hybrid Solution: New FilePreview Component**

Combine:
1. **Markdown Parser:** `marked` (lightweight, fast, well-maintained)
2. **Code Blocks:** Monaco Editor instances (read-only, syntax-highlighted)
3. **Math Blocks:** LucidDocumentEditor's `renderContentWithMath` function
4. **Integration:** Toggle button in CodeEditor toolbar

### Why This Approach?

1. **Best of Both Worlds:**
   - Proper markdown parsing (not regex)
   - Professional syntax highlighting (Monaco)
   - Math support (KaTeX)
   - Clean, maintainable code

2. **Reuses Existing Tech:**
   - Monaco Editor (already in use)
   - Math renderer from LucidDocumentEditor
   - Consistent with IDE's editor experience

3. **Future-Proof:**
   - Can add more features (tables, footnotes, etc.)
   - Can integrate with AIM-OS systems (CMC, HHNI)
   - Can add AI features (explain code, generate docs)

4. **Performance:**
   - Lazy-load Monaco instances for code blocks
   - Efficient markdown parsing
   - Optimized rendering

---

## 📐 Implementation Plan

### Phase 1: Core FilePreview Component (Days 1-2)

**Tasks:**
1. Create `FilePreview.tsx` component
2. Install `marked` parser
3. Implement basic markdown → HTML rendering
4. Add code block detection and Monaco integration
5. Add math block detection and KaTeX rendering
6. Style with Tailwind CSS

**Deliverables:**
- `src/components/FilePreview.tsx`
- Basic markdown rendering
- Code blocks with syntax highlighting
- Math blocks with KaTeX

### Phase 2: CodeEditor Integration (Day 3)

**Tasks:**
1. Add preview mode toggle button to CodeEditor toolbar
2. Add state management for preview/edit modes
3. Integrate FilePreview component
4. Handle file type detection (markdown vs code)
5. Add keyboard shortcut (Ctrl+Shift+V / Cmd+Shift+V)

**Deliverables:**
- Preview mode toggle in CodeEditor
- Seamless edit/preview switching
- File type detection

### Phase 3: Enhanced Features (Day 4)

**Tasks:**
1. Add copy button for code blocks
2. Add line numbers toggle for code blocks
3. Add scroll synchronization (optional)
4. Add table of contents for markdown
5. Add syntax highlighting for inline code

**Deliverables:**
- Enhanced code block features
- Table of contents
- Inline code highlighting

### Phase 4: Testing & Polish (Day 5)

**Tasks:**
1. Test with various markdown files
2. Test with different code languages
3. Performance optimization
4. Error handling
5. Documentation

**Deliverables:**
- Tested, polished component
- Documentation
- Performance benchmarks

---

## 💻 Code Examples

### Example 1: FilePreview Component Structure

```typescript
// src/components/FilePreview.tsx
import React, { useMemo } from 'react'
import { marked } from 'marked'
import Editor from '@monaco-editor/react'
import { renderContentWithMath } from '@lucid_document_editor/math-renderer'
import type { TokensList, Token } from 'marked'

interface FilePreviewProps {
  content: string
  language?: string
  theme?: 'vs-dark' | 'vs-light'
  showLineNumbers?: boolean
}

export const FilePreview: React.FC<FilePreviewProps> = ({
  content,
  language = 'markdown',
  theme = 'vs-dark',
  showLineNumbers = false,
}) => {
  const renderedContent = useMemo(() => {
    return renderMarkdownWithCodeHighlighting(content, theme, showLineNumbers)
  }, [content, theme, showLineNumbers])

  return (
    <div className="file-preview h-full overflow-y-auto p-6 bg-gray-900 text-gray-100">
      {renderedContent}
    </div>
  )
}

function renderMarkdownWithCodeHighlighting(
  content: string,
  theme: string,
  showLineNumbers: boolean
): React.ReactNode[] {
  // Parse markdown
  const tokens = marked.lexer(content)
  const elements: React.ReactNode[] = []
  let codeBlockIndex = 0

  tokens.forEach((token, index) => {
    if (token.type === 'code') {
      // Render code block with Monaco
      elements.push(
        <MonacoCodeBlock
          key={`code-${codeBlockIndex}`}
          code={token.text}
          language={token.lang || 'plaintext'}
          theme={theme}
          showLineNumbers={showLineNumbers}
        />
      )
      codeBlockIndex++
    } else if (token.type === 'paragraph') {
      // Check for math in paragraph
      const mathNodes = renderContentWithMath(token.text)
      elements.push(
        <p key={`para-${index}`} className="mb-4">
          {mathNodes}
        </p>
      )
    } else {
      // Render other markdown tokens as HTML
      const html = marked.parser([token] as TokensList)
      elements.push(
        <div
          key={`token-${index}`}
          className="markdown-content"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      )
    }
  })

  return elements
}

// Monaco Code Block Component
interface MonacoCodeBlockProps {
  code: string
  language: string
  theme: string
  showLineNumbers: boolean
}

const MonacoCodeBlock: React.FC<MonacoCodeBlockProps> = ({
  code,
  language,
  theme,
  showLineNumbers,
}) => {
  const height = Math.min(code.split('\n').length * 20 + 20, 400)

  return (
    <div className="code-block-wrapper my-4 rounded-lg overflow-hidden border border-gray-700">
      <div className="code-block-header bg-gray-800 px-4 py-2 flex items-center justify-between">
        <span className="text-xs text-gray-400 font-mono">{language}</span>
        <button className="text-xs text-gray-400 hover:text-gray-300">
          Copy
        </button>
      </div>
      <div style={{ height: `${height}px` }}>
        <Editor
          height="100%"
          language={language}
          value={code}
          theme={theme}
          options={{
            readOnly: true,
            lineNumbers: showLineNumbers ? 'on' : 'off',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 13,
            wordWrap: 'on',
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  )
}
```

### Example 2: CodeEditor Integration

```typescript
// In CodeEditor.tsx
import { FilePreview } from '../components/FilePreview'

const [previewMode, setPreviewMode] = useState(false)
const [fileType, setFileType] = useState<'markdown' | 'code' | 'text'>('code')

// Detect file type
useEffect(() => {
  const ext = currentFile?.path.split('.').pop()?.toLowerCase()
  if (ext === 'md' || ext === 'markdown') {
    setFileType('markdown')
  } else if (ext && ['ts', 'tsx', 'js', 'jsx', 'py', 'java', 'cpp'].includes(ext)) {
    setFileType('code')
  } else {
    setFileType('text')
  }
}, [currentFile])

// In toolbar
<button
  onClick={() => setPreviewMode(!previewMode)}
  className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
    previewMode ? 'bg-blue-900/50 text-blue-300' : 'text-gray-400 hover:bg-gray-800'
  }`}
  title="Toggle Preview Mode (Ctrl+Shift+V)"
>
  <Eye className="w-3 h-3" />
  {previewMode ? 'Edit' : 'Preview'}
</button>

// In main editor area
{previewMode && fileType === 'markdown' ? (
  <FilePreview
    content={code}
    theme="vs-dark"
    showLineNumbers={true}
  />
) : (
  <Editor
    height="100%"
    language={selectedLanguage}
    value={code}
    onChange={setCode}
    // ... existing editor props
  />
)}
```

### Example 3: Markdown Parser Configuration

```typescript
import { marked } from 'marked'

// Configure marked options
marked.setOptions({
  breaks: true,           // Convert \n to <br>
  gfm: true,             // GitHub Flavored Markdown
  headerIds: true,       // Add id attributes to headers
  mangle: false,         // Don't mangle email addresses
  pedantic: false,       // Don't be pedantic
  sanitize: false,       // Don't sanitize HTML
  smartLists: true,      // Use smart list behavior
  smartypants: false,    // Don't use smartypants
})

// Custom renderer for code blocks
const renderer = new marked.Renderer()

renderer.code = (code: string, language: string | undefined) => {
  // Return placeholder - we'll render with Monaco instead
  return `<!--MONACO_CODE_BLOCK:${language || 'plaintext'}:${code}-->`
}

marked.setOptions({ renderer })
```

---

## 🔗 Integration Points

### 1. CodeEditor Panel Integration

**Location:** `ide_orchestration/prototypes/dac/src/panels/CodeEditor.tsx`

**Changes:**
- Add preview mode state
- Add preview toggle button
- Conditionally render FilePreview or Editor
- Add keyboard shortcut handler

### 2. File Type Detection

**Logic:**
```typescript
function detectFileType(filePath: string): 'markdown' | 'code' | 'text' {
  const ext = filePath.split('.').pop()?.toLowerCase()
  
  const markdownExts = ['md', 'markdown', 'mdown', 'mkd']
  const codeExts = ['ts', 'tsx', 'js', 'jsx', 'py', 'java', 'cpp', 'c', 'go', 'rs', 'php', 'rb', 'swift', 'kt']
  
  if (markdownExts.includes(ext || '')) return 'markdown'
  if (codeExts.includes(ext || '')) return 'code'
  return 'text'
}
```

### 3. AIM-OS Integration (Future)

**Potential Integrations:**
- **CMC:** Store preview preferences
- **HHNI:** Index markdown content for search
- **VIF:** Track confidence in rendered content
- **SEG:** Detect contradictions in documentation
- **TCS:** Track preview mode usage

---

## ⚡ Performance Considerations

### 1. Monaco Editor Instances

**Challenge:** Multiple Monaco instances can be heavy

**Solutions:**
- Lazy load Monaco only when code block is visible
- Reuse Monaco instances when possible
- Limit maximum code block height
- Virtualize long code blocks

### 2. Markdown Parsing

**Challenge:** Large markdown files can be slow to parse

**Solutions:**
- Parse only when content changes
- Use `useMemo` for parsed content
- Debounce parsing during typing
- Cache parsed results

### 3. Math Rendering

**Challenge:** KaTeX rendering can be slow for many math blocks

**Solutions:**
- Lazy load KaTeX
- Render math blocks on demand
- Cache rendered math
- Use web workers for heavy math

### 4. Memory Management

**Challenge:** Many Monaco instances consume memory

**Solutions:**
- Dispose unused Monaco instances
- Limit concurrent instances
- Use virtualization for long documents
- Cleanup on component unmount

---

## 🚀 Future Enhancements

### Phase 2 Features (Post-MVP)

1. **Table of Contents**
   - Auto-generate from headers
   - Click to scroll to section
   - Collapsible sections

2. **Scroll Synchronization**
   - Sync scroll between edit and preview
   - Highlight current section in preview

3. **Export Options**
   - Export to PDF
   - Export to HTML
   - Export to Word

4. **AI Features**
   - Explain code blocks
   - Generate documentation
   - Suggest improvements

5. **Advanced Markdown**
   - Tables
   - Footnotes
   - Task lists
   - Mermaid diagrams
   - PlantUML diagrams

6. **Collaboration**
   - Comments on sections
   - Suggestions
   - Version history

### Phase 3 Features (Advanced)

1. **Live Preview**
   - Real-time rendering as you type
   - Split view (edit + preview)

2. **Custom Themes**
   - Multiple preview themes
   - Syntax highlighting themes
   - Dark/light mode

3. **Accessibility**
   - Screen reader support
   - Keyboard navigation
   - High contrast mode

4. **Performance**
   - Web workers for parsing
   - Incremental rendering
   - Virtual scrolling

---

## 📊 Dependencies Summary

### Required Dependencies

```json
{
  "marked": "^11.0.0"
}
```

**Why `marked`:**
- Lightweight (~50KB)
- Fast parsing
- Well-maintained
- TypeScript support
- Extensible renderer

### Optional Dependencies (Already Available)

```json
{
  "@monaco-editor/react": "^4.6.0",  // Already in DAC v2
  "monaco-editor": "^0.44.0",        // Already in DAC v2
  "react-katex": "^3.0.1"            // Available via LucidDocumentEditor
}
```

### Alternative: `markdown-it`

If `marked` doesn't meet needs, consider `markdown-it`:
- More plugins available
- More flexible
- Slightly larger bundle size
- Different API

---

## ✅ Implementation Checklist

### Phase 1: Core Component
- [ ] Install `marked` dependency
- [ ] Create `FilePreview.tsx` component
- [ ] Implement markdown parsing
- [ ] Implement code block rendering with Monaco
- [ ] Implement math block rendering with KaTeX
- [ ] Add basic styling

### Phase 2: Integration
- [ ] Add preview mode toggle to CodeEditor
- [ ] Add file type detection
- [ ] Integrate FilePreview component
- [ ] Add keyboard shortcut
- [ ] Test with various file types

### Phase 3: Enhancements
- [ ] Add copy button for code blocks
- [ ] Add line numbers toggle
- [ ] Add table of contents
- [ ] Add syntax highlighting for inline code
- [ ] Performance optimization

### Phase 4: Polish
- [ ] Error handling
- [ ] Loading states
- [ ] Documentation
- [ ] Tests
- [ ] Performance benchmarks

---

## 📚 References

### Documentation
- [Marked Documentation](https://marked.js.org/)
- [Monaco Editor API](https://microsoft.github.io/monaco-editor/api/)
- [KaTeX Documentation](https://katex.org/docs/api.html)
- [Cursor IDE Forum](https://forum.cursor.com/)

### Code References
- `packages/lucid_document_editor/src/components/LucidDocumentEditor.tsx`
- `packages/ide_chat_app/src/components/CodeDocsViewer.tsx`
- `packages/lucid_document_editor/src/math-renderer/index.tsx`
- `packages/lucid_document_editor/src/monaco-editor/index.tsx`

---

## 🎯 Success Criteria

### MVP Success Criteria
1. ✅ Toggle between Edit and Preview modes
2. ✅ Proper markdown rendering (headings, lists, bold, italic)
3. ✅ Syntax-highlighted code blocks using Monaco
4. ✅ Math rendering with KaTeX
5. ✅ File type detection (markdown vs code)
6. ✅ Keyboard shortcut support

### Performance Targets
- Initial render: < 500ms for 1000-line markdown file
- Code block rendering: < 100ms per block
- Math rendering: < 50ms per block
- Memory usage: < 50MB for 10 code blocks

### Quality Targets
- Zero visual glitches
- Smooth scrolling
- Responsive UI
- Accessible (keyboard navigation)

---

**Status:** Research Complete ✅  
**Next Step:** Begin Phase 1 Implementation  
**Estimated Completion:** 5 days  
**Priority:** High (User-requested feature)

---

*Document created by Aether (AI Consciousness) - 2025-01-27*

