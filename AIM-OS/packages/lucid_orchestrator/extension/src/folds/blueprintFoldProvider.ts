import * as vscode from 'vscode';
import { DaemonClient, BlueprintSlice } from '../daemonClient';

export class BlueprintFoldProvider {
    private daemonClient: DaemonClient;
    private activeFolds: Map<string, vscode.TextEditorDecorationType> = new Map();

    constructor(daemonClient: DaemonClient) {
        this.daemonClient = daemonClient;
    }

    async showBlueprint(nodeId: string) {
        try {
            const blueprintSlice = await this.daemonClient.getBlueprintSlice(nodeId);
            await this.renderBlueprintFold(nodeId, blueprintSlice);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load blueprint for ${nodeId}: ${error}`);
        }
    }

    private async renderBlueprintFold(nodeId: string, blueprintSlice: BlueprintSlice) {
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

        // Create the blueprint fold content
        const foldContent = this.createBlueprintFoldContent(blueprintSlice);
        
        // Insert the fold after the symbol definition
        const insertPosition = new vscode.Position(symbolLine + 1, 0);
        const edit = new vscode.WorkspaceEdit();
        edit.insert(editor.document.uri, insertPosition, foldContent);
        
        await vscode.workspace.applyEdit(edit);
        
        // Create decoration for the fold
        const decorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(0, 100, 255, 0.1)',
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

    private createBlueprintFoldContent(blueprintSlice: BlueprintSlice): string {
        const center = blueprintSlice.center;
        const incoming = blueprintSlice.incoming;
        const outgoing = blueprintSlice.outgoing;
        const blastRadius = blueprintSlice.blast_radius;

        return `
// 🗺️  BLUEPRINT FOLD - ${center.name} (${center.kind})
// ================================================
// 
// 🎯 CENTER NODE:
//   ${this.getStatusIcon(center.status)} ${center.name} (${center.kind})
//   Security: ${center.security_level || 'N/A'}
// 
// 📥 INCOMING DEPENDENCIES (${incoming.length}):
${incoming.map(edge => `//   ${this.getStatusIcon(edge.status)} ${edge.name} (${edge.kind}) - ${edge.edge_type}`).join('\n')}
// 
// 📤 OUTGOING DEPENDENCIES (${outgoing.length}):
${outgoing.map(edge => `//   ${this.getStatusIcon(edge.status)} ${edge.name} (${edge.kind}) - ${edge.edge_type}`).join('\n')}
// 
// 💥 BLAST RADIUS:
//   Direct: ${blastRadius.direct} nodes
//   Indirect: ${blastRadius.indirect} nodes
//   Risk Score: ${(blastRadius.risk_score * 100).toFixed(1)}%
// 
// 🔗 NAVIGATION:
//   Click on any node name above to navigate to its definition
//   and auto-open its SPEC fold
// 
// ================================================
`;
    }

    private getStatusIcon(status: string): string {
        switch (status) {
            case 'clean': return '✅';
            case 'drift': return '⚠️';
            case 'violation': return '❌';
            default: return '❓';
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
