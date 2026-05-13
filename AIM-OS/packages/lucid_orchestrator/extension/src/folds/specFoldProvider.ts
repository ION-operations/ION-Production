import * as vscode from 'vscode';
import { DaemonClient, SpecBlock } from '../daemonClient';

export class SpecFoldProvider {
    private daemonClient: DaemonClient;
    private activeFolds: Map<string, vscode.TextEditorDecorationType> = new Map();

    constructor(daemonClient: DaemonClient) {
        this.daemonClient = daemonClient;
    }

    async showSpec(nodeId: string) {
        try {
            const specBlock = await this.daemonClient.getSpecBlock(nodeId);
            await this.renderSpecFold(nodeId, specBlock);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load spec for ${nodeId}: ${error}`);
        }
    }

    private async renderSpecFold(nodeId: string, specBlock: SpecBlock) {
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

        // Create the spec fold content
        const foldContent = this.createSpecFoldContent(specBlock);
        
        // Insert the fold after the symbol definition
        const insertPosition = new vscode.Position(symbolLine + 1, 0);
        const edit = new vscode.WorkspaceEdit();
        edit.insert(editor.document.uri, insertPosition, foldContent);
        
        await vscode.workspace.applyEdit(edit);
        
        // Create decoration for the fold
        const decorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: this.getStatusColor(specBlock.status),
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

    private async findSymbolLine(document: vscode.TextDocument, nodeId: string): Promise<number> {
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

    private createSpecFoldContent(specBlock: SpecBlock): string {
        const statusIcon = this.getStatusIcon(specBlock.status);
        const statusColor = this.getStatusColor(specBlock.status);
        
        return `
// 🔍 SPEC FOLD - ${specBlock.node_id} ${statusIcon}
// ================================================
// 
// 📋 RESPONSIBILITY:
// ${specBlock.responsibility}
// 
// 🚫 MUST NEVER:
${specBlock.must_never.map(item => `//   • ${item}`).join('\n')}
// 
// 📥 INPUTS: ${specBlock.inputs.join(', ')}
// 📤 OUTPUTS: ${specBlock.outputs.join(', ')}
// ⚡ SIDE EFFECTS: ${specBlock.side_effects.join(', ')}
// 
// 🔒 SECURITY LEVEL: ${specBlock.security_level.toUpperCase()}
// ⏱️  PERF BUDGET: ${specBlock.perf_budget_ms}ms
// 📊 STATUS: ${specBlock.status.toUpperCase()}
${specBlock.drift_reason ? `// ⚠️  DRIFT REASON: ${specBlock.drift_reason}` : ''}
// 
${specBlock.governance ? `// 👤 GOVERNANCE:
//   Last Change: ${specBlock.governance.lastChange?.by} at ${specBlock.governance.lastChange?.at}
//   Reason: ${specBlock.governance.lastChange?.reason}` : ''}
// 
// [PROPOSE CHANGE] - Click to propose changes to this spec
// ================================================
`;
    }

    private getStatusIcon(status: string): string {
        switch (status) {
            case 'clean': return '✅';
            case 'drift': return '⚠️';
            case 'violation': return '❌';
            case 'proposed': return '📝';
            default: return '❓';
        }
    }

    private getStatusColor(status: string): string {
        switch (status) {
            case 'clean': return 'rgba(0, 255, 0, 0.1)';
            case 'drift': return 'rgba(255, 165, 0, 0.1)';
            case 'violation': return 'rgba(255, 0, 0, 0.1)';
            case 'proposed': return 'rgba(0, 0, 255, 0.1)';
            default: return 'rgba(128, 128, 128, 0.1)';
        }
    }

    public dispose() {
        // Clean up active decorations
        for (const decoration of this.activeFolds.values()) {
            decoration.dispose();
        }
        this.activeFolds.clear();
    }
}
