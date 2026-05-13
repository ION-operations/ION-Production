import * as vscode from 'vscode';
import { DaemonClient, TimelineSummary } from '../daemonClient';

export class TimelineFoldProvider {
    private daemonClient: DaemonClient;
    private activeFolds: Map<string, vscode.TextEditorDecorationType> = new Map();

    constructor(daemonClient: DaemonClient) {
        this.daemonClient = daemonClient;
    }

    async showTimeline(nodeId: string) {
        try {
            const timelineSummary = await this.daemonClient.getTimelineSummary(nodeId);
            await this.renderTimelineFold(nodeId, timelineSummary);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load timeline for ${nodeId}: ${error}`);
        }
    }

    private async renderTimelineFold(nodeId: string, timelineSummary: TimelineSummary) {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        // Find the line where this symbol is defined
        const symbolLine = await this.findSymbolLine(editor.document, nodeId);
        if (symbolLine === -1) {
            vscode.window.showErrorMessage(`Could not find symbol for ${nodeId}`);
            return;
        }

        // Create the timeline fold content
        const foldContent = this.createTimelineFoldContent(timelineSummary);
        
        // Insert the fold after the symbol definition
        const insertPosition = new vscode.Position(symbolLine + 1, 0);
        const edit = new vscode.WorkspaceEdit();
        edit.insert(editor.document.uri, insertPosition, foldContent);
        
        await vscode.workspace.applyEdit(edit);
        
        // Create decoration for the fold
        const decorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(255, 165, 0, 0.1)',
            borderRadius: '4px',
            margin: '0 0 0 1em'
        });

        // Calculate the range for the fold
        const foldStartLine = symbolLine + 1;
        const foldEndLine = symbolLine + 1 + foldContent.split('\n').length;
        const foldRange = new vscode.Range(foldStartLine, 0, foldEndLine, 0);

        editor.setDecorations(decorationType, [{
            range: foldRange,
            renderOptions: {
                after: {
                    contentText: ' ',
                    margin: '0 0 0 1em'
                }
            }
        }]);

        // Store the decoration for cleanup
        this.activeFolds.set(nodeId, decorationType);
    }

    private async findSymbolLine(document: vscode.Document, nodeId: string): Promise<number> {
        const symbolName = nodeId.split(':')[1];
        const text = document.getText();
        const lines = text.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line.includes(symbolName) && (
                line.includes('function') ||
                line.includes('const') ||
                line.includes('class') ||
                line.includes('interface')
            )) {
                return i;
            }
        }
        
        return -1;
    }

    private createTimelineFoldContent(timelineSummary: TimelineSummary): string {
        const recentRuns = timelineSummary.recent_runs;
        const worstCascade = timelineSummary.worst_run_cascade;

        return `
// ⏰ TIMELINE FOLD - ${timelineSummary.node_id}
// ================================================
// 
// 📊 RECENT EXECUTIONS (${recentRuns.length}):
${recentRuns.map(run => {
    const timestamp = new Date(run.timestamp).toLocaleString();
    const statusIcon = this.getStatusIcon(run.status);
    const violations = run.violations.length > 0 ? ` | Violations: ${run.violations.join(', ')}` : '';
    return `//   ${statusIcon} ${timestamp} | ${run.duration_ms}ms | ${run.thread}${violations}`;
}).join('\n')}
// 
// 🔥 WORST EXECUTION CASCADE:
${worstCascade.map((step, index) => {
    const indent = '  '.repeat(index);
    const thread = step.thread ? ` (${step.thread})` : '';
    return `//   ${indent}${step.symbol} - ${step.action} - ${step.duration_ms}ms${thread}`;
}).join('\n')}
// 
// 📈 PERFORMANCE ANALYSIS:
//   Average Duration: ${this.calculateAverageDuration(recentRuns).toFixed(1)}ms
//   Slow Executions: ${recentRuns.filter(run => run.status === 'slow').length}
//   Violations: ${recentRuns.filter(run => run.violations.length > 0).length}
// 
// ================================================
`;
    }

    private getStatusIcon(status: string): string {
        switch (status) {
            case 'normal': return '✅';
            case 'ok': return '✅';
            case 'slow': return '⚠️';
            case 'threw': return '❌';
            case 'security_event': return '🔒';
            default: return '❓';
        }
    }

    private calculateAverageDuration(runs: any[]): number {
        if (runs.length === 0) return 0;
        const totalDuration = runs.reduce((sum, run) => sum + run.duration_ms, 0);
        return totalDuration / runs.length;
    }

    public dispose() {
        // Clean up active decorations
        for (const decoration of this.activeFolds.values()) {
            decoration.dispose();
        }
        this.activeFolds.clear();
    }
}
