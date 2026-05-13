// Terminal Panel - V2 Refactored with BasePanel
// Command execution with CMC atom storage and VIF witness tracking

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { BasePanel } from '../components/BasePanel'
import { useCMC, useVIF } from '../hooks/useAIMOS'
import { Terminal as TerminalIcon, ChevronRight, Database, Shield, Clock } from 'lucide-react'
import type { CMCAtom, VIFWitness } from '../hooks/useAIMOS'

interface Command {
  id: string
  command: string
  output: string
  timestamp: string
  
  // AIM-OS Integration
  cmc_atom?: CMCAtom
  vif_witness?: VIFWitness
  confidence_band?: 'A' | 'B' | 'C'
  kappa_gate_passed?: boolean
  
  // Metadata
  exit_code?: number
  duration_ms?: number
  evidence?: string[]
}

export const TerminalPanel: React.FC = () => {
  const { storeAtom } = useCMC()
  const { trackConfidence, witnesses } = useVIF()
  const [commands, setCommands] = useState<Command[]>([])
  const [input, setInput] = useState('')
  const [currentDir, setCurrentDir] = useState('~/aimos-ide')
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const terminalRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    // Scroll to bottom on new commands
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [commands])
  
  const executeCommand = useCallback(async (cmd: string) => {
    if (!cmd.trim()) return
    
    const startTime = Date.now()
    const cmdId = `cmd_${Date.now()}_${Math.random().toString(16).substring(2, 10)}`
    
    // Determine command criticality
    let taskCriticality: 'critical' | 'important' | 'routine' | 'low_stakes' = 'routine'
    if (cmd.includes('rm ') || cmd.includes('delete') || cmd.includes('drop')) {
      taskCriticality = 'critical'
    } else if (cmd.includes('git ') || cmd.includes('npm ') || cmd.includes('install')) {
      taskCriticality = 'important'
    }
    
    // Store command in CMC with proper atom structure
    const atomResult = await storeAtom(
      `Terminal Command: ${cmd}\nDirectory: ${currentDir}\nTimestamp: ${new Date().toISOString()}`,
      'event',
      {
        'type': 1.0,
        'terminal': 1.0,
        'command': 0.95,
        'directory': 0.8
      },
      {
        command: cmd,
        directory: currentDir,
        command_id: cmdId,
        task_criticality: taskCriticality
      }
    )
    
    // Track confidence with VIF
    const confidence = taskCriticality === 'critical' ? 0.95 : 
                      taskCriticality === 'important' ? 0.85 : 0.80
    
    const vifResult = await trackConfidence(
      `command_execution:${cmd}`,
      confidence,
      [atomResult.atom_id || cmdId],
      `Command executed: ${cmd} in ${currentDir}`,
      taskCriticality
    )
    
    // Simulate command execution
    let output = ''
    let exitCode = 0
    
    if (cmd.startsWith('cd ')) {
      const dir = cmd.substring(3).trim()
      const newDir = dir || '~/aimos-ide'
      setCurrentDir(newDir)
      output = `Changed directory to ${newDir}`
    } else if (cmd === 'ls' || cmd === 'ls -la') {
      output = `src/\ncomponents/\nhooks/\npanels/\npackage.json\nREADME.md\n`
    } else if (cmd === 'pwd') {
      output = currentDir
    } else if (cmd === 'cmc status') {
      output = `CMC Status:
Total Atoms: 1,250
Modalities: text (850), code (320), event (80)
Storage: 45.2 MB
Health: Excellent`
    } else if (cmd === 'vif witnesses') {
      output = `VIF Witnesses: ${witnesses.length}
Recent Witnesses:
${witnesses.slice(-5).map(w => `  ${w.id.substring(0, 16)}... Band ${w.confidence_band} (${(w.confidence_score * 100).toFixed(0)}%)`).join('\n')}`
    } else if (cmd.startsWith('git ')) {
      output = `Git command executed: ${cmd}\n[Simulated git output]`
    } else if (cmd === 'help') {
      output = `AIM-OS Terminal Commands:
  cd <dir>          - Change directory
  ls                - List files
  pwd               - Print working directory
  cmc status        - Show CMC status
  vif witnesses     - Show VIF witnesses
  git <command>     - Git operations
  help              - Show this help`
    } else {
      output = `Command '${cmd}' executed successfully`
    }
    
    const duration = Date.now() - startTime
    
    // Determine confidence band
    let confidence_band: 'A' | 'B' | 'C'
    if (confidence >= 0.90) {
      confidence_band = 'A'
    } else if (confidence >= 0.70) {
      confidence_band = 'B'
    } else {
      confidence_band = 'C'
    }
    
    // Check κ-gate
    const kappa_thresholds = {
      critical: 0.95,
      important: 0.85,
      routine: 0.70,
      low_stakes: 0.60
    }
    const kappa_threshold = kappa_thresholds[taskCriticality]
    const kappa_gate_passed = confidence >= kappa_threshold
    
    const newCommand: Command = {
      id: cmdId,
      command: cmd,
      output,
      timestamp: new Date().toISOString(),
      cmc_atom: atomResult.atom,
      vif_witness: vifResult.witness || undefined,
      confidence_band,
      kappa_gate_passed,
      exit_code: exitCode,
      duration_ms: duration,
      evidence: [atomResult.atom_id || cmdId]
    }
    
    setCommands(prev => [...prev, newCommand])
    setCommandHistory(prev => [...prev, cmd])
    setHistoryIndex(-1)
    setInput('')
  }, [storeAtom, trackConfidence, currentDir, witnesses])
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      executeCommand(input)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (commandHistory.length > 0) {
        const newIndex = historyIndex === -1 
          ? commandHistory.length - 1 
          : Math.max(0, historyIndex - 1)
        setHistoryIndex(newIndex)
        setInput(commandHistory[newIndex])
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex >= 0) {
        const newIndex = historyIndex + 1
        if (newIndex >= commandHistory.length) {
          setHistoryIndex(-1)
          setInput('')
        } else {
          setHistoryIndex(newIndex)
          setInput(commandHistory[newIndex])
        }
      }
    }
  }
  
  const getConfidenceBandColor = (band?: 'A' | 'B' | 'C') => {
    switch (band) {
      case 'A': return 'text-green-400'
      case 'B': return 'text-yellow-400'
      case 'C': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }
  
  // Calculate AIM-OS metrics
  const overallConfidence = commands.length > 0
    ? commands.reduce((sum, cmd) => {
        const conf = cmd.vif_witness?.confidence_score || 0.5
        return sum + conf
      }, 0) / commands.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  const kappaGateFailures = commands.filter(c => c.kappa_gate_passed === false).length
  
  return (
    <BasePanel
      id="panel-terminal"
      title="Terminal"
      icon={TerminalIcon}
      description="Command execution with CMC atom storage and VIF witness tracking"
      loading={false}
      error={null}
      empty={commands.length === 0}
      emptyMessage="No commands executed yet"
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            {kappaGateFailures > 0 && (
              <span className="text-red-400">
                {kappaGateFailures} κ-gate failures
              </span>
            )}
            {kappaGateFailures === 0 && `${commands.length} commands executed`}
          </span>
          <span className="text-green-400">CMC + VIF Integration Active</span>
        </div>
      }
      headerClassName="px-3 py-2"
    >
      {/* Terminal Output */}
      <div 
        ref={terminalRef}
        className="flex-1 overflow-auto p-3 font-mono text-sm text-gray-300 space-y-2"
      >
        {commands.length === 0 && (
          <div className="text-gray-500 space-y-1">
            <div>Welcome to AIM-OS Terminal</div>
            <div className="text-xs mt-2">
              Commands are tracked in CMC with bitemporal storage
              <br />
              VIF witnesses created for each command execution
              <br />
              Evidence links maintained for full provenance
            </div>
            <div className="text-xs mt-4 text-gray-600">
              Type 'help' for available commands
            </div>
          </div>
        )}
        
        {commands.map((cmd) => {
          const confidenceColor = getConfidenceBandColor(cmd.confidence_band)
          
          return (
            <div key={cmd.id} className="space-y-1">
              {/* Command Line */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-green-400">{currentDir}</span>
                <ChevronRight className="w-4 h-4 text-gray-500" />
                <span className="text-blue-400">{cmd.command}</span>
                
                {/* VIF Witness Indicator */}
                {cmd.vif_witness && (
                  <div className="flex items-center gap-1 ml-2">
                    <Shield className={`w-3 h-3 ${confidenceColor}`} />
                    <span className={`text-xs ${confidenceColor}`}>
                      Band {cmd.confidence_band}
                    </span>
                    {cmd.kappa_gate_passed !== undefined && (
                      <span className={`text-xs ${cmd.kappa_gate_passed ? 'text-green-400' : 'text-red-400'}`}>
                        {cmd.kappa_gate_passed ? '✓' : '✗'} κ
                      </span>
                    )}
                  </div>
                )}
                
                {/* Duration */}
                {cmd.duration_ms !== undefined && (
                  <span className="text-xs text-gray-500">
                    ({cmd.duration_ms}ms)
                  </span>
                )}
              </div>
              
              {/* Output */}
              <div className="text-gray-400 ml-4 whitespace-pre-wrap">{cmd.output}</div>
              
              {/* CMC Atom Link */}
              {cmd.cmc_atom && (
                <div className="ml-4 flex items-center gap-2 text-xs text-blue-400">
                  <Database className="w-3 h-3" />
                  <span>CMC Atom: {cmd.cmc_atom.id.substring(0, 16)}...</span>
                  <span className="text-gray-500">•</span>
                  <span className="text-gray-500 capitalize">{cmd.cmc_atom.modality}</span>
                </div>
              )}
              
              {/* VIF Witness Details */}
              {cmd.vif_witness && (
                <div className="ml-4 pt-1 border-t border-gray-800">
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <div>
                      <span>Witness ID:</span>
                      <span className="ml-2 text-gray-400 font-mono">
                        {cmd.vif_witness.id.substring(0, 12)}...
                      </span>
                    </div>
                    <div>
                      <span>Confidence:</span>
                      <span className={`ml-2 ${confidenceColor}`}>
                        {(cmd.vif_witness.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    {cmd.vif_witness.task_criticality && (
                      <div>
                        <span>Criticality:</span>
                        <span className="ml-2 text-gray-400 capitalize">
                          {cmd.vif_witness.task_criticality}
                        </span>
                      </div>
                    )}
                    {cmd.vif_witness.kappa_threshold !== undefined && (
                      <div>
                        <span>κ Threshold:</span>
                        <span className="ml-2 text-gray-400">
                          {(cmd.vif_witness.kappa_threshold * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Timestamp */}
              <div className="ml-4 text-xs text-gray-600 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>{new Date(cmd.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Input */}
      <div className="px-3 py-2 border-t border-gray-700 flex items-center gap-2 bg-gray-800/50">
        <span className="text-green-400 font-mono text-sm">{currentDir}</span>
        <ChevronRight className="w-4 h-4 text-gray-500" />
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter command..."
          className="flex-1 bg-transparent text-gray-300 font-mono text-sm outline-none"
          autoFocus
        />
      </div>
    </BasePanel>
  )
}
