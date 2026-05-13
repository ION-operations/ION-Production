import React, { useRef } from 'react'
import Editor from '@monaco-editor/react'
import { Code, FileText } from 'lucide-react'

interface MonacoEditorProps {
  value: string
  language?: string
  onChange?: (value: string | undefined) => void
  fileName?: string
  readOnly?: boolean
  theme?: string
}

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  language = 'typescript',
  onChange,
  fileName,
  readOnly = false,
  theme = 'vs-dark'
}) => {
  const editorRef = useRef<any>(null)

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor

    // Configure editor options
    editor.updateOptions({
      minimap: { enabled: true },
      fontSize: 14,
      lineNumbers: 'on',
      roundedSelection: false,
      scrollBeyondLastLine: false,
      readOnly,
      wordWrap: 'on',
      automaticLayout: true,
    })

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      console.log('Save triggered')
      // Handle save
    })

    // Configure TypeScript/JavaScript language
    if (language === 'typescript' || language === 'javascript') {
      monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
        target: monaco.languages.typescript.ScriptTarget.ES2020,
        allowNonTsExtensions: true,
        moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
        module: monaco.languages.typescript.ModuleKind.CommonJS,
        noEmit: true,
        esModuleInterop: true,
        jsx: monaco.languages.typescript.JsxEmit.React,
        reactNamespace: 'React',
        allowJs: true,
        typeRoots: ['node_modules/@types']
      })
    }
  }

  // Determine language from file name if not provided
  const detectedLanguage = language || (() => {
    if (!fileName) return 'typescript'
    const ext = fileName.split('.').pop()?.toLowerCase()
    const languageMap: Record<string, string> = {
      'ts': 'typescript',
      'tsx': 'typescript',
      'js': 'javascript',
      'jsx': 'javascript',
      'py': 'python',
      'json': 'json',
      'css': 'css',
      'html': 'html',
      'md': 'markdown',
      'yaml': 'yaml',
      'yml': 'yaml',
      'xml': 'xml',
      'sql': 'sql',
      'sh': 'shell',
      'bash': 'shell',
      'go': 'go',
      'rs': 'rust',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
    }
    return languageMap[ext || ''] || 'typescript'
  })()

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 border-b border-gray-700">
        {fileName ? (
          <>
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-gray-200">{fileName}</span>
          </>
        ) : (
          <>
            <Code className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-gray-200">Editor</span>
          </>
        )}
        <span className="ml-auto text-xs text-gray-500">{detectedLanguage}</span>
      </div>

      {/* Editor */}
      <div className="flex-1">
        <Editor
          height="100%"
          defaultLanguage={detectedLanguage}
          value={value}
          onChange={onChange}
          onMount={handleEditorDidMount}
          theme={theme}
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            readOnly,
            wordWrap: 'on',
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
            formatOnPaste: true,
            formatOnType: true,
            suggestSelection: 'first',
            quickSuggestions: true,
            suggestOnTriggerCharacters: true,
            acceptSuggestionOnEnter: 'on',
            snippetSuggestions: 'top',
            parameterHints: { enabled: true },
            hover: { enabled: true },
            colorDecorators: true,
            bracketPairColorization: { enabled: true },
            guides: {
              bracketPairs: true,
              indentation: true,
              highlightActiveIndentation: true,
            },
          }}
        />
      </div>
    </div>
  )
}
