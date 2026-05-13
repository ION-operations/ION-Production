// Code Preview Modal - Shows generated code with syntax highlighting
// File tree, code viewer, and download options

import React, { useState, useMemo } from 'react'
import { 
  X, Download, Copy, Check, FileText, Folder, FolderOpen, 
  ChevronRight, ChevronDown, Code, Terminal, Search,
  FileCode, FileJson, FileType, Braces, Loader2
} from 'lucide-react'
import { GeneratedCode, GeneratedFile, FileTreeNode } from './types'

interface CodePreviewModalProps {
  isOpen: boolean
  onClose: () => void
  generatedCode: GeneratedCode | null
  isGenerating?: boolean
}

export const CodePreviewModal: React.FC<CodePreviewModalProps> = ({
  isOpen,
  onClose,
  generatedCode,
  isGenerating = false,
}) => {
  const [selectedFile, setSelectedFile] = useState<GeneratedFile | null>(null)
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['/']))
  const [searchQuery, setSearchQuery] = useState('')
  const [copied, setCopied] = useState(false)

  // Auto-select first file
  React.useEffect(() => {
    if (generatedCode?.files?.length && !selectedFile) {
      setSelectedFile(generatedCode.files[0])
    }
  }, [generatedCode])

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  const handleCopy = async () => {
    if (selectedFile) {
      await navigator.clipboard.writeText(selectedFile.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownloadAll = () => {
    // Create a zip file (in real implementation)
    console.log('Download all files')
  }

  const getFileIcon = (language: string) => {
    switch (language) {
      case 'typescript':
      case 'javascript':
        return <FileCode className="w-4 h-4 text-blue-400" />
      case 'json':
        return <FileJson className="w-4 h-4 text-yellow-400" />
      case 'yaml':
        return <Braces className="w-4 h-4 text-orange-400" />
      case 'dockerfile':
        return <Terminal className="w-4 h-4 text-cyan-400" />
      default:
        return <FileText className="w-4 h-4 text-gray-400" />
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-6xl h-[85vh] bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-6 border-b border-gray-800 bg-gray-950/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Code className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-100">Generated Code</h2>
              {generatedCode && (
                <p className="text-xs text-gray-500">
                  {generatedCode.stats.totalFiles} files • {generatedCode.stats.totalLines.toLocaleString()} lines • {generatedCode.stats.testCoverage}% coverage
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadAll}
              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download All
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {isGenerating ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
              <p className="text-lg text-gray-300">Generating code...</p>
              <p className="text-sm text-gray-500 mt-2">This may take a few seconds</p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex overflow-hidden">
            {/* File Tree */}
            <div className="w-72 border-r border-gray-800 flex flex-col bg-gray-950/30">
              {/* Search */}
              <div className="p-3 border-b border-gray-800">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Search files..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-8 pl-9 pr-3 rounded-lg bg-gray-800 border border-gray-700 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Tree */}
              <div className="flex-1 overflow-y-auto p-2">
                {generatedCode?.structure && (
                  <FileTree
                    nodes={generatedCode.structure}
                    files={generatedCode.files}
                    selectedPath={selectedFile?.path}
                    expandedFolders={expandedFolders}
                    searchQuery={searchQuery}
                    onToggleFolder={toggleFolder}
                    onSelectFile={setSelectedFile}
                    getFileIcon={getFileIcon}
                  />
                )}
              </div>

              {/* Stats */}
              {generatedCode && (
                <div className="p-3 border-t border-gray-800 space-y-2">
                  <div className="grid grid-cols-2 gap-2 text-[10px]">
                    <div className="p-2 rounded-lg bg-gray-800/50">
                      <div className="text-gray-500">TypeScript</div>
                      <div className="text-gray-200 font-medium">{generatedCode.stats.languages['typescript'] || 0} lines</div>
                    </div>
                    <div className="p-2 rounded-lg bg-gray-800/50">
                      <div className="text-gray-500">Test Files</div>
                      <div className="text-gray-200 font-medium">{generatedCode.stats.testFiles}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Code Viewer */}
            <div className="flex-1 flex flex-col bg-gray-950">
              {selectedFile ? (
                <>
                  {/* File Header */}
                  <div className="h-10 flex items-center justify-between px-4 border-b border-gray-800 bg-gray-900/50">
                    <div className="flex items-center gap-2">
                      {getFileIcon(selectedFile.language)}
                      <span className="text-sm text-gray-300">{selectedFile.path}</span>
                      <span className="text-xs text-gray-600">({selectedFile.content.split('\n').length} lines)</span>
                    </div>
                    <button
                      onClick={handleCopy}
                      className="p-1.5 hover:bg-gray-800 rounded text-gray-400 hover:text-gray-200 transition-colors"
                    >
                      {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Code Content */}
                  <div className="flex-1 overflow-auto">
                    <pre className="p-4 text-xs font-mono leading-relaxed">
                      <code className="text-gray-300">
                        {selectedFile.content.split('\n').map((line, i) => (
                          <div key={i} className="flex hover:bg-gray-800/50">
                            <span className="w-10 text-right pr-4 text-gray-600 select-none">{i + 1}</span>
                            <span className="flex-1">{highlightCode(line, selectedFile.language)}</span>
                          </div>
                        ))}
                      </code>
                    </pre>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <FileText className="w-12 h-12 text-gray-700 mx-auto mb-4" />
                    <p className="text-gray-500">Select a file to view its contents</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// File Tree Component
interface FileTreeProps {
  nodes: FileTreeNode[]
  files: GeneratedFile[]
  selectedPath?: string
  expandedFolders: Set<string>
  searchQuery: string
  onToggleFolder: (path: string) => void
  onSelectFile: (file: GeneratedFile) => void
  getFileIcon: (language: string) => React.ReactNode
  level?: number
}

const FileTree: React.FC<FileTreeProps> = ({
  nodes,
  files,
  selectedPath,
  expandedFolders,
  searchQuery,
  onToggleFolder,
  onSelectFile,
  getFileIcon,
  level = 0,
}) => {
  return (
    <div className="space-y-0.5">
      {nodes.map(node => {
        const isExpanded = expandedFolders.has(node.path)
        const matchesSearch = !searchQuery || node.name.toLowerCase().includes(searchQuery.toLowerCase())
        
        if (!matchesSearch && node.type === 'file') return null

        if (node.type === 'directory') {
          return (
            <div key={node.path}>
              <button
                onClick={() => onToggleFolder(node.path)}
                className="w-full flex items-center gap-1.5 px-2 py-1 rounded hover:bg-gray-800/50 text-left"
                style={{ paddingLeft: `${8 + level * 12}px` }}
              >
                {isExpanded ? (
                  <ChevronDown className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                ) : (
                  <ChevronRight className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                )}
                {isExpanded ? (
                  <FolderOpen className="w-4 h-4 text-blue-400 flex-shrink-0" />
                ) : (
                  <Folder className="w-4 h-4 text-blue-400 flex-shrink-0" />
                )}
                <span className="text-xs text-gray-300 truncate">{node.name}</span>
              </button>
              {isExpanded && node.children && (
                <FileTree
                  nodes={node.children}
                  files={files}
                  selectedPath={selectedPath}
                  expandedFolders={expandedFolders}
                  searchQuery={searchQuery}
                  onToggleFolder={onToggleFolder}
                  onSelectFile={onSelectFile}
                  getFileIcon={getFileIcon}
                  level={level + 1}
                />
              )}
            </div>
          )
        }

        const file = files.find(f => f.path === node.path)
        if (!file) return null

        return (
          <button
            key={node.path}
            onClick={() => onSelectFile(file)}
            className={`w-full flex items-center gap-1.5 px-2 py-1 rounded text-left transition-colors ${
              selectedPath === node.path
                ? 'bg-blue-600/20 text-blue-300'
                : 'hover:bg-gray-800/50 text-gray-400'
            }`}
            style={{ paddingLeft: `${20 + level * 12}px` }}
          >
            {getFileIcon(file.language)}
            <span className="text-xs truncate">{node.name}</span>
            {node.lines && (
              <span className="text-[10px] text-gray-600 ml-auto">{node.lines}</span>
            )}
          </button>
        )
      })}
    </div>
  )
}

// Simple syntax highlighting (in production, use a proper library like Prism)
function highlightCode(line: string, language: string): React.ReactNode {
  // Keywords
  const keywords = ['const', 'let', 'var', 'function', 'class', 'interface', 'type', 'export', 'import', 'from', 'async', 'await', 'return', 'if', 'else', 'for', 'while', 'try', 'catch', 'throw', 'new', 'this', 'extends', 'implements']
  
  // Very basic highlighting
  let result = line
  
  // Highlight strings
  result = result.replace(/(["'`])(.*?)\1/g, '<span class="text-green-400">$&</span>')
  
  // Highlight keywords
  keywords.forEach(kw => {
    const regex = new RegExp(`\\b${kw}\\b`, 'g')
    result = result.replace(regex, `<span class="text-purple-400">${kw}</span>`)
  })
  
  // Highlight comments
  if (result.includes('//')) {
    const idx = result.indexOf('//')
    result = result.slice(0, idx) + `<span class="text-gray-600">${result.slice(idx)}</span>`
  }
  
  return <span dangerouslySetInnerHTML={{ __html: result }} />
}

export default CodePreviewModal

