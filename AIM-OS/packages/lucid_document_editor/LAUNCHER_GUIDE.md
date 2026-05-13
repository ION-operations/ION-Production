# LUCID Document Editor - Launcher Guide

## 🚀 Quick Start

**Yes, this runs on React!** The LUCID Document Editor is a React application built with TypeScript and Vite.

### Running the Launcher/Demo App

```bash
# Navigate to the package directory
cd packages/lucid_document_editor

# Install dependencies (if not already installed)
npm install

# Start the development server
npm run dev
```

The launcher will automatically open in your browser at `http://localhost:3004`

### Building for Production

```bash
# Build the library (for npm package)
npm run build:lib

# Build the demo app
npm run build:demo

# Preview the built demo
npm run preview
```

## 📦 What You Get

### Launcher Features:
- ✅ **Full-featured demo** of the LUCID Document Editor
- ✅ **New Document** button to create fresh documents
- ✅ **Load Document** button to load saved documents
- ✅ **AI Features** toggle to enable/disable AI capabilities
- ✅ **Collaboration** toggle for real-time collaboration
- ✅ **Auto-save** enabled by default (saves every 30 seconds)
- ✅ **Beautiful UI** with gradient header and modern design

### Editor Features:
- 📝 **Rich Text Editing** with Slate.js
- 🔢 **LaTeX Math Rendering** with KaTeX
- 💻 **Monaco Editor** mode for code editing
- 📑 **Section-based editing** with section management
- 🔒 **Section locking** for collaborative editing
- 📊 **Version control** with section versioning
- 💬 **Comments** system for collaboration
- 🔗 **AIM-OS Integration** (CMC, VIF, SEG, HHNI, APOE)
- 📤 **Export/Import** (JSON, Markdown, LaTeX, HTML)

## 🎯 Usage Examples

### Basic Usage:
```tsx
import { LucidDocumentEditor } from '@aimos/lucid-document-editor';

function MyApp() {
  return (
    <LucidDocumentEditor
      documentId="my-document"
      autoSave={true}
      aiEnabled={true}
    />
  );
}
```

### With Custom Handlers:
```tsx
<LucidDocumentEditor
  documentId="my-document"
  onSave={(doc) => console.log('Saved:', doc)}
  onLoad={() => loadMyDocument()}
  aiEnabled={true}
  hhniEndpoint="http://localhost:8000"
/>
```

## 🛠️ Development

The launcher uses:
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Zustand** - State management
- **Monaco Editor** - Code editing
- **Slate.js** - Rich text editing
- **KaTeX** - Math rendering
- **Yjs** - Real-time collaboration

## 📁 Project Structure

```
packages/lucid_document_editor/
├── index.html          # HTML entry point for launcher
├── src/
│   ├── main.tsx        # React entry point
│   ├── App.tsx         # Launcher app component
│   ├── App.css         # Launcher styles
│   ├── index.css       # Global styles
│   ├── components/
│   │   └── LucidDocumentEditor.tsx  # Main editor component
│   ├── store/          # Zustand store
│   ├── models/         # TypeScript models
│   ├── persistence/    # Save/load functionality
│   ├── math-renderer/  # KaTeX integration
│   ├── monaco-editor/  # Monaco integration
│   ├── rich-text-editor/  # Slate.js integration
│   ├── collaboration/  # Yjs collaboration
│   └── aimos-integration/  # AIM-OS integrations
└── package.json
```

## 🎨 Customization

You can customize the launcher by editing `src/App.tsx`:
- Change the header design
- Add more controls
- Customize the footer
- Add theme switching
- Add more demo features

## 🚀 Next Steps

1. **Run the launcher**: `npm run dev`
2. **Try creating a document** with math equations
3. **Test rich text editing** with the formatting toolbar
4. **Enable AI features** to see auto-tagging and suggestions
5. **Export documents** to various formats

Enjoy the LUCID Document Editor! 🌟

