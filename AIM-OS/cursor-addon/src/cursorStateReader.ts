import * as vscode from 'vscode';

/**
 * Cursor State Reader - Reads VS Code/Cursor state for MCP tools
 * Provides access to terminals, output channels, editor state, workspace state
 */

export interface TerminalInfo {
    index: number;
    name: string;
    shellPath?: string;
    shellType: string; // PowerShell, Bash, CMD, Unknown
    processId?: number;
    isActive: boolean;
    exitStatus?: number;
    state: 'running' | 'finished' | 'unknown';
}

export interface TerminalCloseOption {
    terminal_name: string;
    terminal_index: number;
    reason: string;
    shell_type: string;
}

export interface TerminalManagementResult {
    total_terminals: number;
    powershell_count: number;
    bash_count: number;
    cmd_count: number;
    recommendations: string[];
    close_options: TerminalCloseOption[];
    terminals: TerminalInfo[];
}

export interface EditorState {
    active: boolean;
    file?: string;
    language?: string;
    selection?: {
        start: { line: number; character: number };
        end: { line: number; character: number };
        text: string;
    };
    cursor?: { line: number; character: number };
    lineCount?: number;
}

export interface WorkspaceState {
    folders: Array<{ name: string; path: string }>;
    openFiles: Array<{ file: string; language: string }>;
    activeFile?: string;
}

export interface ProblemInfo {
    file: string;
    severity: 'error' | 'warning' | 'info' | 'hint';
    message: string;
    line: number;
    column: number;
    source?: string;
    code?: string | number;
}

export interface ProblemSummary {
    total: number;
    errors: number;
    warnings: number;
    info: number;
    hints: number;
}

export class CursorStateReader {
    /**
     * Detect shell type from terminal
     */
    private static detectShellType(terminal: vscode.Terminal): string {
        const shellPath = terminal.creationOptions?.shellPath?.toLowerCase() || '';
        const name = terminal.name.toLowerCase();
        
        if (shellPath.includes('powershell') || name.includes('powershell') || shellPath.includes('pwsh')) {
            return 'PowerShell';
        }
        if (shellPath.includes('bash') || name.includes('bash')) {
            return 'Bash';
        }
        if (shellPath.includes('cmd') || name.includes('cmd') || shellPath.includes('cmd.exe')) {
            return 'CMD';
        }
        if (shellPath.includes('zsh') || name.includes('zsh')) {
            return 'Zsh';
        }
        return 'Unknown';
    }

    /**
     * Get terminal state
     */
    private static getTerminalState(terminal: vscode.Terminal): 'running' | 'finished' | 'unknown' {
        if (terminal.exitStatus) {
            return 'finished';
        }
        // Terminal is still running if no exit status
        return 'running';
    }

    /**
     * List all open terminals with details
     */
    static async listTerminals(): Promise<TerminalInfo[]> {
        const terminals = vscode.window.terminals;
        const activeTerminal = vscode.window.activeTerminal;
        
        return terminals.map((terminal, index) => ({
            index,
            name: terminal.name,
            shellPath: terminal.creationOptions?.shellPath,
            shellType: this.detectShellType(terminal),
            processId: terminal.exitStatus?.code,
            isActive: terminal === activeTerminal,
            exitStatus: terminal.exitStatus?.code,
            state: this.getTerminalState(terminal)
        }));
    }

    /**
     * Close a terminal by name or index
     */
    static async closeTerminal(terminalName?: string, terminalIndex?: number): Promise<{ success: boolean; closed: string; error?: string }> {
        const terminals = vscode.window.terminals;
        
        let terminalToClose: vscode.Terminal | undefined;
        
        if (terminalIndex !== undefined) {
            if (terminalIndex < 0 || terminalIndex >= terminals.length) {
                return {
                    success: false,
                    closed: '',
                    error: `Terminal index ${terminalIndex} out of range (0-${terminals.length - 1})`
                };
            }
            terminalToClose = terminals[terminalIndex];
        } else if (terminalName) {
            terminalToClose = terminals.find(t => t.name === terminalName);
            if (!terminalToClose) {
                return {
                    success: false,
                    closed: '',
                    error: `Terminal "${terminalName}" not found`
                };
            }
        } else {
            // Close active terminal
            terminalToClose = vscode.window.activeTerminal;
            if (!terminalToClose) {
                return {
                    success: false,
                    closed: '',
                    error: 'No active terminal to close'
                };
            }
        }
        
        const name = terminalToClose.name;
        try {
            terminalToClose.dispose(); // ✅ ONE-CLICK CLOSE!
            return { success: true, closed: name };
        } catch (error: any) {
            return {
                success: false,
                closed: '',
                error: error.message || String(error)
            };
        }
    }

    /**
     * Manage terminals - analyze and provide recommendations
     */
    static async manageTerminals(threshold: number = 5): Promise<TerminalManagementResult> {
        const terminals = vscode.window.terminals;
        const terminalList = await this.listTerminals();
        
        // Count by shell type
        const powershellCount = terminalList.filter(t => t.shellType === 'PowerShell').length;
        const bashCount = terminalList.filter(t => t.shellType === 'Bash').length;
        const cmdCount = terminalList.filter(t => t.shellType === 'CMD').length;
        const totalCount = terminals.length;
        
        // Build recommendations
        const recommendations: string[] = [];
        const closeOptions: TerminalCloseOption[] = [];
        
        if (totalCount > threshold) {
            recommendations.push(`You have ${totalCount} terminals open (recommended: ≤${threshold})`);
            
            // Identify finished/inactive terminals
            terminals.forEach((terminal, index) => {
                if (terminal.exitStatus) {
                    recommendations.push(`Terminal "${terminal.name}" appears finished (exit code: ${terminal.exitStatus.code})`);
                    closeOptions.push({
                        terminal_name: terminal.name,
                        terminal_index: index,
                        reason: 'Finished process',
                        shell_type: terminalList[index].shellType
                    });
                }
            });
            
            // If multiple PowerShell instances
            if (powershellCount > 2) {
                recommendations.push(`You have ${powershellCount} PowerShell terminals open (consider closing unused ones)`);
                
                // List PowerShell terminals for easy closing
                terminalList.forEach((term, index) => {
                    if (term.shellType === 'PowerShell') {
                        closeOptions.push({
                            terminal_name: term.name,
                            terminal_index: index,
                            reason: 'Multiple PowerShell instances',
                            shell_type: 'PowerShell'
                        });
                    }
                });
            }
        } else {
            recommendations.push(`Terminal count is reasonable (${totalCount} terminals, threshold: ${threshold})`);
        }
        
        return {
            total_terminals: totalCount,
            powershell_count: powershellCount,
            bash_count: bashCount,
            cmd_count: cmdCount,
            recommendations,
            close_options: closeOptions, // One-click close options!
            terminals: terminalList
        };
    }

    /**
     * Get active editor state
     */
    static async getActiveEditorState(): Promise<EditorState> {
        const editor = vscode.window.activeTextEditor;
        
        if (!editor) {
            return { active: false };
        }
        
        return {
            active: true,
            file: editor.document.uri.fsPath,
            language: editor.document.languageId,
            selection: {
                start: {
                    line: editor.selection.start.line,
                    character: editor.selection.start.character
                },
                end: {
                    line: editor.selection.end.line,
                    character: editor.selection.end.character
                },
                text: editor.document.getText(editor.selection)
            },
            cursor: {
                line: editor.selection.active.line,
                character: editor.selection.active.character
            },
            lineCount: editor.document.lineCount
        };
    }

    /**
     * Get workspace state
     */
    static async getWorkspaceState(): Promise<WorkspaceState> {
        return {
            folders: vscode.workspace.workspaceFolders?.map(f => ({
                name: f.name,
                path: f.uri.fsPath
            })) || [],
            openFiles: vscode.window.visibleTextEditors.map(e => ({
                file: e.document.uri.fsPath,
                language: e.document.languageId
            })),
            activeFile: vscode.window.activeTextEditor?.document.uri.fsPath
        };
    }

    /**
     * Get output channel content
     */
    static async getOutputChannel(channelName: string): Promise<string> {
        const channel = vscode.window.createOutputChannel(channelName);
        return channel.value; // ✅ CAN READ!
    }

    /**
     * List known output channels
     * Note: VS Code doesn't expose a list of all channels, so we return known channels
     */
    static async listOutputChannels(): Promise<string[]> {
        return [
            'AIM-OS Extension',
            'AIM-OS Dashboard',
            'AIM-OS Debug',
            'Extension Host',
            'Tasks',
            'Git',
            'Output'
        ];
    }

    /**
     * Get output channel content with line limit
     */
    static async getOutputChannelLogs(channelName: string, limit: number = 100): Promise<string> {
        const channel = vscode.window.createOutputChannel(channelName);
        const content = channel.value || '';
        
        // If limit specified, return last N lines
        if (limit > 0 && content) {
            const lines = content.split('\n');
            return lines.slice(-limit).join('\n');
        }
        
        return content;
    }

    /**
     * Get severity label from DiagnosticSeverity
     */
    private static getSeverityLabel(severity: vscode.DiagnosticSeverity): 'error' | 'warning' | 'info' | 'hint' {
        switch (severity) {
            case vscode.DiagnosticSeverity.Error:
                return 'error';
            case vscode.DiagnosticSeverity.Warning:
                return 'warning';
            case vscode.DiagnosticSeverity.Information:
                return 'info';
            case vscode.DiagnosticSeverity.Hint:
                return 'hint';
            default:
                return 'info';
        }
    }

    /**
     * Get all diagnostics/problems from VS Code
     */
    static async getProblems(): Promise<ProblemInfo[]> {
        const diagnostics = vscode.languages.getDiagnostics();
        const problems: ProblemInfo[] = [];
        
        for (const [uri, diags] of diagnostics) {
            for (const diag of diags) {
                problems.push({
                    file: uri.fsPath,
                    severity: this.getSeverityLabel(diag.severity),
                    message: diag.message,
                    line: diag.range.start.line + 1, // 1-based for user-friendly display
                    column: diag.range.start.character + 1, // 1-based for user-friendly display
                    source: diag.source || undefined,
                    code: diag.code ? (typeof diag.code === 'string' ? diag.code : diag.code.value) : undefined
                });
            }
        }
        
        return problems;
    }

    /**
     * Get problems summary (counts by severity)
     */
    static async getProblemSummary(): Promise<ProblemSummary> {
        const problems = await this.getProblems();
        
        return {
            total: problems.length,
            errors: problems.filter(p => p.severity === 'error').length,
            warnings: problems.filter(p => p.severity === 'warning').length,
            info: problems.filter(p => p.severity === 'info').length,
            hints: problems.filter(p => p.severity === 'hint').length
        };
    }

    /**
     * Get problems for a specific file
     */
    static async getFileProblems(filePath: string): Promise<ProblemInfo[]> {
        const uri = vscode.Uri.file(filePath);
        const diagnostics = vscode.languages.getDiagnostics(uri);
        const problems: ProblemInfo[] = [];
        
        for (const diag of diagnostics) {
            problems.push({
                file: uri.fsPath,
                severity: this.getSeverityLabel(diag.severity),
                message: diag.message,
                line: diag.range.start.line + 1,
                column: diag.range.start.character + 1,
                source: diag.source || undefined,
                code: diag.code ? (typeof diag.code === 'string' ? diag.code : diag.code.value) : undefined
            });
        }
        
        return problems;
    }
}

