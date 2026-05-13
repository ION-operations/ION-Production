// Document Editor Panel - LUCID Document Editor Integration
// Wraps the LUCID Document Editor component for IDE integration

import React from 'react'
import { LucidDocumentEditor } from '../../../../../packages/lucid_document_editor/src/index'
// Import CSS for the editor
import '../../../../../packages/lucid_document_editor/src/components/LucidDocumentEditor.css'

export const DocumentEditor: React.FC = () => {
  return (
    <div className="h-full w-full">
      <LucidDocumentEditor
        documentId="ide-document-editor"
        autoSave={true}
        autoSaveInterval={30000}
        aiEnabled={true}
        hhniEndpoint="http://localhost:8000"
        onSave={(document) => {
          // Save to CMC via MCP tools (TODO: implement CMC integration)
          console.log('Document saved:', document)
          // TODO: Use MCP tools to save to CMC
          // mcp_lucid-mcp_store_memory({ content: JSON.stringify(document), tags: { type: 'document', id: document.id } })
        }}
        onLoad={() => {
          // Load from CMC via MCP tools (TODO: implement CMC integration)
          // TODO: Use MCP tools to load from CMC
          // const memory = await mcp_lucid-mcp_retrieve_memory({ query: 'document ide-document-editor' })
          // return memory ? JSON.parse(memory.content) : null
          return null
        }}
      />
    </div>
  )
}

