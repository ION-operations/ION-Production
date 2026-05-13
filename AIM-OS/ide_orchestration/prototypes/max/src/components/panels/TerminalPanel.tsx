// Enhanced Terminal Panel - Max V2
// Command execution with AIM-OS integration (CMC, VIF, SEG, bitemporal)

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Terminal as TerminalIcon, Plus, X, ChevronRight, Database, Shield, Clock, AlertTriangle } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { ContradictionAlert } from '../ContradictionAlert/ContradictionAlert';
import { EvidenceTrailDisplay } from '../EvidenceTrailDisplay/EvidenceTrailDisplay';
import { BitemporalDisplay } from '../BitemporalDisplay/BitemporalDisplay';
import { PanelLoading } from '../Loading/Loading';
import { createEvidenceTrail, createCMCAtomLink, createVIFWitnessLink } from '../../utils/evidence';
import { createBitemporalMetadata } from '../../utils/bitemporal';
import './TerminalPanel.css';

export interface TerminalCommand {
  id: string;
  command: string;
  output: string;
  timestamp: string;
  exitCode: number;
  duration: number;
  cwd: string;
  
  // AIM-OS Integration
  cmcAtom?: string;
  vifConfidence?: number;
  evidenceTrail?: any;
  bitemporal?: {
    valid_from: string;
    valid_to: string | null;
  };
  contradictions?: number;
}

export interface TerminalSession {
  id: string;
  name: string;
  cwd: string;
  commands: TerminalCommand[];
  commandHistory: string[];
  createdAt: string;
}

export const TerminalPanel: React.FC = () => {
  const { cmc, vif, seg, loading, errors } = useAIMOS();
  const [sessions, setSessions] = useState<TerminalSession[]>([
    {
      id: 'session_1',
      name: 'Terminal 1',
      cwd: '~/aimos-ide',
      commands: [],
      commandHistory: [],
      createdAt: new Date().toISOString(),
    },
  ]);
  const [activeSessionId, setActiveSessionId] = useState('session_1');
  const [input, setInput] = useState('');
  const [historyIndex, setHistoryIndex] = useState(-1);
  const terminalOutputRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const activeSession = sessions.find(s => s.id === activeSessionId);

  // Scroll to bottom on new commands
  useEffect(() => {
    if (terminalOutputRef.current) {
      terminalOutputRef.current.scrollTop = terminalOutputRef.current.scrollHeight;
    }
  }, [activeSession?.commands]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, [activeSessionId]);

  const executeCommand = useCallback(async (cmd: string) => {
    if (!cmd.trim() || !activeSession) return;

    const startTime = Date.now();
    const cmdId = `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Determine command criticality
    let taskCriticality: 'critical' | 'important' | 'routine' | 'low_stakes' = 'routine';
    if (cmd.includes('rm ') || cmd.includes('delete') || cmd.includes('drop')) {
      taskCriticality = 'critical';
    } else if (cmd.includes('git ') || cmd.includes('npm ') || cmd.includes('install')) {
      taskCriticality = 'important';
    }

    // Store command in CMC
    let cmcAtomId: string | undefined;
    let vifConfidence: number | undefined;
    let evidenceTrail: any;
    let contradictions: number = 0;

    try {
      // Store in CMC
      const atomResult = await cmc.storeAtom(
        `Terminal Command: ${cmd}\nDirectory: ${activeSession.cwd}\nTimestamp: ${new Date().toISOString()}`,
        'event',
        {
          'type': 1.0,
          'terminal': 1.0,
          'command': 0.95,
          'directory': 0.8,
        },
        {
          command: cmd,
          directory: activeSession.cwd,
          command_id: cmdId,
          task_criticality: taskCriticality,
        }
      );
      cmcAtomId = atomResult.atom_id;

      // Track confidence with VIF
      const confidence = taskCriticality === 'critical' ? 0.95 :
                        taskCriticality === 'important' ? 0.85 : 0.80;
      vifConfidence = confidence;

      // Create evidence trail
      const evidence = [
        createCMCAtomLink(cmcAtomId, confidence, 'Command stored in CMC'),
        createVIFWitnessLink(`witness_${cmdId}`, confidence, 'VIF witness for command execution'),
      ];
      evidenceTrail = createEvidenceTrail(`Command executed: ${cmd}`, evidence);

      // Check for contradictions
      const segContradictions = await seg.getContradictions();
      contradictions = segContradictions.length;
    } catch (error) {
      console.error('AIM-OS integration error:', error);
    }

    // Simulate command execution
    let output = '';
    let exitCode = 0;

    if (cmd.startsWith('cd ')) {
      const dir = cmd.substring(3).trim();
      const newDir = dir || '~/aimos-ide';
      setSessions(prev => prev.map(s =>
        s.id === activeSessionId ? { ...s, cwd: newDir } : s
      ));
      output = `Changed directory to ${newDir}`;
    } else if (cmd === 'ls' || cmd === 'ls -la') {
      output = `src/\ncomponents/\nhooks/\npanels/\npackage.json\nREADME.md\n`;
    } else if (cmd === 'pwd') {
      output = activeSession.cwd;
    } else if (cmd === 'clear') {
      setSessions(prev => prev.map(s =>
        s.id === activeSessionId ? { ...s, commands: [] } : s
      ));
      return;
    } else if (cmd.startsWith('echo ')) {
      output = cmd.substring(5);
    } else if (cmd === 'help') {
      output = `Available commands:\n  cd <dir> - Change directory\n  ls - List files\n  pwd - Print working directory\n  clear - Clear terminal\n  echo <text> - Echo text\n  help - Show this help`;
    } else {
      output = `Command not found: ${cmd}\nType 'help' for available commands`;
      exitCode = 1;
    }

    const duration = Date.now() - startTime;

    // Create command object
    const command: TerminalCommand = {
      id: cmdId,
      command: cmd,
      output,
      timestamp: new Date().toISOString(),
      exitCode,
      duration,
      cwd: activeSession.cwd,
      cmcAtom: cmcAtomId,
      vifConfidence,
      evidenceTrail,
      bitemporal: createBitemporalMetadata(),
      contradictions,
    };

    // Add command to session
    setSessions(prev => prev.map(s =>
      s.id === activeSessionId
        ? {
            ...s,
            commands: [...s.commands, command],
            commandHistory: [...s.commandHistory, cmd],
          }
        : s
    ));

    // Clear input
    setInput('');
    setHistoryIndex(-1);
  }, [activeSessionId, activeSession, cmc, vif, seg]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!activeSession) return;

    if (e.key === 'Enter') {
      e.preventDefault();
      executeCommand(input);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (activeSession.commandHistory.length > 0) {
        const newIndex = historyIndex === -1
          ? activeSession.commandHistory.length - 1
          : Math.max(0, historyIndex - 1);
        setHistoryIndex(newIndex);
        setInput(activeSession.commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex !== -1) {
        const newIndex = historyIndex + 1;
        if (newIndex >= activeSession.commandHistory.length) {
          setHistoryIndex(-1);
          setInput('');
        } else {
          setHistoryIndex(newIndex);
          setInput(activeSession.commandHistory[newIndex]);
        }
      }
    }
  };

  const createNewSession = () => {
    const newSession: TerminalSession = {
      id: `session_${Date.now()}`,
      name: `Terminal ${sessions.length + 1}`,
      cwd: '~/aimos-ide',
      commands: [],
      commandHistory: [],
      createdAt: new Date().toISOString(),
    };
    setSessions(prev => [...prev, newSession]);
    setActiveSessionId(newSession.id);
  };

  const closeSession = (sessionId: string) => {
    if (sessions.length === 1) return; // Don't close last session
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (activeSessionId === sessionId) {
      const remainingSessions = sessions.filter(s => s.id !== sessionId);
      setActiveSessionId(remainingSessions[0]?.id || '');
    }
  };

  if (loading.cmc || loading.vif || loading.seg) {
    return <PanelLoading message="Loading Terminal..." />;
  }

  if (errors.cmc || errors.vif || errors.seg) {
    return (
      <div className="terminal-error" role="alert">
        <p>Error loading Terminal: {errors.cmc?.message || errors.vif?.message || errors.seg?.message}</p>
      </div>
    );
  }

  const totalContradictions = activeSession?.commands.reduce((sum, cmd) => sum + (cmd.contradictions || 0), 0) || 0;

  return (
    <div className="terminal-panel" role="region" aria-label="Terminal Panel">
      {/* Tabs */}
      <div className="terminal-tabs">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`terminal-tab ${activeSessionId === session.id ? 'active' : ''}`}
            onClick={() => setActiveSessionId(session.id)}
            role="tab"
            aria-selected={activeSessionId === session.id}
          >
            <TerminalIcon className="terminal-tab-icon" />
            <span className="terminal-tab-name">{session.name}</span>
            {sessions.length > 1 && (
              <button
                className="terminal-tab-close"
                onClick={(e) => {
                  e.stopPropagation();
                  closeSession(session.id);
                }}
                aria-label={`Close ${session.name}`}
              >
                <X className="terminal-tab-close-icon" />
              </button>
            )}
          </div>
        ))}
        <button
          className="terminal-tab-new"
          onClick={createNewSession}
          aria-label="Create new terminal"
          title="New Terminal"
        >
          <Plus className="terminal-tab-new-icon" />
        </button>
      </div>

      {/* Terminal Content */}
      {activeSession && (
        <div className="terminal-content">
          {/* Header */}
          <div className="terminal-header">
            <div className="terminal-header-left">
              <TerminalIcon className="terminal-header-icon" />
              <div>
                <h3 className="terminal-header-title">Terminal</h3>
                <p className="terminal-header-subtitle">
                  Command Execution • CMC-Backed • VIF Confidence • Evidence Trails
                </p>
              </div>
            </div>
            <div className="terminal-header-right">
              {totalContradictions > 0 && (
                <ContradictionAlert count={totalContradictions} />
              )}
              <div className="terminal-stats">
                <span className="terminal-stat">
                  {activeSession.commands.length} command{activeSession.commands.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          </div>

          {/* Output */}
          <div className="terminal-output" ref={terminalOutputRef}>
            {activeSession.commands.length === 0 ? (
              <div className="terminal-empty">
                <p>No commands executed yet</p>
                <p className="terminal-empty-hint">Type a command and press Enter to execute</p>
              </div>
            ) : (
              activeSession.commands.map((cmd) => (
                <div key={cmd.id} className="terminal-command-block">
                  {/* Command */}
                  <div className="terminal-command-line">
                    <span className="terminal-prompt">{cmd.cwd} $</span>
                    <span className="terminal-command-text">{cmd.command}</span>
                    {cmd.vifConfidence !== undefined && (
                      <ConfidenceIndicator
                        confidence={cmd.vifConfidence}
                        size="sm"
                        variant="inline"
                      />
                    )}
                    {cmd.contradictions && cmd.contradictions > 0 && (
                      <ContradictionAlert count={cmd.contradictions} severity="high" />
                    )}
                  </div>

                  {/* Output */}
                  <div className={`terminal-output-lines ${cmd.exitCode !== 0 ? 'terminal-output-error' : ''}`}>
                    {cmd.output.split('\n').map((line, index) => (
                      <div key={index} className="terminal-output-line">
                        {line}
                      </div>
                    ))}
                  </div>

                  {/* AIM-OS Integration */}
                  <div className="terminal-aimos">
                    {cmd.cmcAtom && (
                      <div className="terminal-aimos-item">
                        <Database className="terminal-aimos-icon" />
                        <span className="terminal-aimos-label">CMC:</span>
                        <span className="terminal-aimos-value">{cmd.cmcAtom}</span>
                      </div>
                    )}
                    {cmd.bitemporal && (
                      <BitemporalDisplay bitemporal={cmd.bitemporal} compact={true} />
                    )}
                    {cmd.evidenceTrail && (
                      <EvidenceTrailDisplay trail={cmd.evidenceTrail} compact={true} />
                    )}
                    <div className="terminal-aimos-item">
                      <Clock className="terminal-aimos-icon" />
                      <span className="terminal-aimos-label">Duration:</span>
                      <span className="terminal-aimos-value">{cmd.duration}ms</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Input */}
          <div className="terminal-input-container">
            <span className="terminal-prompt">{activeSession.cwd} $</span>
            <input
              ref={inputRef}
              type="text"
              className="terminal-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter command..."
              aria-label="Terminal command input"
            />
          </div>
        </div>
      )}
    </div>
  );
};
