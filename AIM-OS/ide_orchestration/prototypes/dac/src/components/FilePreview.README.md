# FilePreview Component

A Cursor IDE-style file preview component that displays markdown files with proper text formatting and syntax-highlighted code blocks.

## Features

- ✅ **Markdown Rendering** - Full markdown support (headings, lists, bold, italic, links, etc.)
- ✅ **Syntax-Highlighted Code Blocks** - Uses Monaco Editor for professional code highlighting
- ✅ **Math Rendering** - LaTeX math support via KaTeX (inline and block)
- ✅ **Inline Code** - Styled inline code snippets
- ✅ **Copy Buttons** - One-click copy for code blocks
- ✅ **Line Numbers** - Optional line numbers for code blocks
- ✅ **Dark Theme** - Beautiful dark theme matching IDE aesthetic

## Installation

The component uses the following dependencies (already installed):

```json
{
  "marked": "^11.0.0",
  "react-katex": "^3.0.1",
  "katex": "^0.16.9",
  "@monaco-editor/react": "^4.6.0",
  "monaco-editor": "^0.44.0"
}
```

## Usage

### Basic Usage

```tsx
import { FilePreview } from './components/FilePreview'

function MyComponent() {
  const markdownContent = `# Hello World

This is **markdown** content.

\`\`\`typescript
const greeting = "Hello, World!"
console.log(greeting)
\`\`\`
`

  return (
    <FilePreview
      content={markdownContent}
      theme="vs-dark"
      showLineNumbers={true}
    />
  )
}
```

### With Toggle (Edit/Preview Mode)

```tsx
import { useState } from 'react'
import { FilePreview } from './components/FilePreview'
import Editor from '@monaco-editor/react'

function EditorWithPreview() {
  const [previewMode, setPreviewMode] = useState(false)
  const [content, setContent] = useState('# My Document\n\nContent here...')

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="toolbar">
        <button onClick={() => setPreviewMode(!previewMode)}>
          {previewMode ? 'Edit' : 'Preview'}
        </button>
      </div>

      {/* Content */}
      {previewMode ? (
        <FilePreview content={content} />
      ) : (
        <Editor
          language="markdown"
          value={content}
          onChange={(value) => setContent(value || '')}
        />
      )}
    </div>
  )
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `content` | `string` | **required** | Markdown content to render |
| `language` | `string` | `'markdown'` | Language for code blocks (not used currently) |
| `theme` | `'vs-dark' \| 'vs-light'` | `'vs-dark'` | Monaco Editor theme |
| `showLineNumbers` | `boolean` | `false` | Show line numbers in code blocks |
| `className` | `string` | `''` | Additional CSS classes |

## Supported Markdown Features

- Headings (H1-H6)
- Paragraphs
- **Bold** and *italic* text
- Inline `code`
- Code blocks with syntax highlighting
- Lists (ordered and unordered)
- Blockquotes
- Horizontal rules
- Links
- Math (LaTeX via KaTeX)
  - Inline: `$E = mc^2$`
  - Block: `$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$`

## Code Block Languages

All Monaco Editor supported languages work, including:
- TypeScript/JavaScript
- Python
- Java
- C/C++
- Go
- Rust
- And 100+ more...

## Math Support

The component supports LaTeX math via KaTeX:

- **Inline math**: `$E = mc^2$` or `\(E = mc^2\)`
- **Block math**: `$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$` or `\[\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}\]`

## Styling

The component uses Tailwind CSS classes and includes custom prose styling. The preview area has:
- Dark background (`bg-gray-900`)
- Light text (`text-gray-100`)
- Proper spacing and typography
- Code blocks with Monaco Editor styling
- Responsive design

## Performance

- Markdown parsing is memoized (only re-parses when content changes)
- Monaco Editor instances are created on-demand for code blocks
- Math rendering is optimized with KaTeX
- Large files are handled efficiently

## Integration with CodeEditor

To integrate with the CodeEditor panel:

```tsx
// In CodeEditor.tsx
import { FilePreview } from '../components/FilePreview'

const [previewMode, setPreviewMode] = useState(false)
const fileType = detectFileType(currentFile?.path || '')

{previewMode && fileType === 'markdown' ? (
  <FilePreview
    content={code}
    theme="vs-dark"
    showLineNumbers={true}
  />
) : (
  <Editor ... />
)}
```

## Examples

See `FilePreview.example.tsx` for a complete usage example with edit/preview toggle.

## Future Enhancements

- [ ] Table of contents generation
- [ ] Scroll synchronization
- [ ] Export to PDF/HTML
- [ ] Mermaid diagram support
- [ ] PlantUML diagram support
- [ ] Custom themes
- [ ] Accessibility improvements

## License

MIT

