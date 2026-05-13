import React, { useState, useRef, useEffect } from 'react'
import { Terminal as TerminalIcon, Send, X } from 'lucide-react'

interface TerminalPanelProps {
  isOpen: boolean
  onClose: () => void
}

export const TerminalPanel: React.FC<TerminalPanelProps> = ({ isOpen, onClose }) => {
  const [command, setCommand] = useState('')
  const [history, setHistory] = useState<string[]>([])
  const [output, setOutput] = useState<string[]>(['Welcome to AIM-OS Terminal', 'Type "help" for available commands'])
  const terminalRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isOpen && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [output, isOpen])

  const executeCommand = (cmd: string) => {
    const trimmedCmd = cmd.trim()
    if (!trimmedCmd) return

    setHistory([...history, trimmedCmd])
    setOutput([...output, `$ ${trimmedCmd}`])

    // Simulate command execution
    let result = ''
    const lowerCmd = trimmedCmd.toLowerCase()

    if (lowerCmd === 'help') {
      result = `Available commands:
- help: Show this help message
- clear: Clear terminal output
- status: Show AIM-OS system status
- memory: Display memory statistics
- version: Show AIM-OS version info`
    } else if (lowerCmd === 'clear') {
      setOutput([])
      return
    } else if (lowerCmd === 'status') {
      result = `AIM-OS Status:
- CMC: Online
- HHNI: Online
- VIF: Online
- APOE: Online
- SEG: Offline`
    } else if (lowerCmd === 'memory') {
      result = `Memory Stats:
- Total Atoms: 165
- Active Sessions: 1
- Storage: SQLite`
    } else if (lowerCmd === 'version') {
      result = `AIM-OS Version 1.0.0
Built with consciousness infrastructure`
    } else {
      result = `Command not found: ${trimmedCmd}. Type "help" for available commands.`
    }

    setOutput(prev => [...prev, result])
    setCommand('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    executeCommand(command)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-x-0 bottom-0 h-96 bg-gray-900 text-green-400 font-mono border-t border-gray-700 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-5 h-5 text-green-400" />
          <h3 className="text-sm font-semibold text-white">Terminal</h3>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Output */}
      <div
        ref={terminalRef}
        className="flex-1 overflow-y-auto p-4 space-y-1 text-sm"
      >
        {output.map((line, index) => (
          <div key={index} className="text-gray-300">
            {line.split('\n').map((l, i) => (
              <div key={i}>{l}</div>
            ))}
          </div>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-gray-700 bg-gray-800 p-2">
        <div className="flex items-center gap-2">
          <span className="text-green-400 font-bold">$</span>
          <input
            ref={inputRef}
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Enter command..."
            className="flex-1 bg-transparent text-white outline-none font-mono text-sm"
            autoFocus
          />
          <button
            type="submit"
            className="px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  )
}
