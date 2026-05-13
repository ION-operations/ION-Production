import * as vscode from 'vscode';

export interface CodeSymbol {
    name: string;
    kind: string;
    range: vscode.Range;
    nodeId: string;
}

export class LucidOrchestratorProvider {
    
    async provideDecorations(document: vscode.TextDocument): Promise<vscode.DecorationOptions[]> {
        const decorations: vscode.DecorationOptions[] = [];
        
        // Only process TypeScript/JavaScript files
        if (!this.isSupportedLanguage(document.languageId)) {
            return decorations;
        }

        const symbols = await this.extractSymbols(document);
        
        for (const symbol of symbols) {
            // Create decoration for each symbol
            const decoration: vscode.DecorationOptions = {
                range: symbol.range,
                renderOptions: {
                    after: {
                        contentText: this.createGutterContent(symbol),
                        margin: '0 0 0 1em',
                        color: new vscode.ThemeColor('editorLineNumber.foreground')
                    }
                },
                hoverMessage: this.createHoverMessage(symbol)
            };
            
            decorations.push(decoration);
        }
        
        return decorations;
    }

    private isSupportedLanguage(languageId: string): boolean {
        return ['typescript', 'javascript', 'typescriptreact', 'javascriptreact'].includes(languageId);
    }

    private async extractSymbols(document: vscode.TextDocument): Promise<CodeSymbol[]> {
        const symbols: CodeSymbol[] = [];
        const text = document.getText();
        const lines = text.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmedLine = line.trim();
            
            // Detect function declarations
            const functionMatch = trimmedLine.match(/^(export\s+)?(async\s+)?function\s+(\w+)/);
            if (functionMatch) {
                const name = functionMatch[3];
                const range = new vscode.Range(i, 0, i, line.length);
                const nodeId = this.generateNodeId(document.fileName, name, 'function');
                
                symbols.push({
                    name,
                    kind: 'function',
                    range,
                    nodeId
                });
            }
            
            // Detect arrow functions
            const arrowFunctionMatch = trimmedLine.match(/^(export\s+)?const\s+(\w+)\s*=\s*(async\s+)?\(/);
            if (arrowFunctionMatch) {
                const name = arrowFunctionMatch[2];
                const range = new vscode.Range(i, 0, i, line.length);
                const nodeId = this.generateNodeId(document.fileName, name, 'function');
                
                symbols.push({
                    name,
                    kind: 'function',
                    range,
                    nodeId
                });
            }
            
            // Detect React components
            const componentMatch = trimmedLine.match(/^(export\s+)?(const|function)\s+(\w+)\s*[=\(]/);
            if (componentMatch && this.isReactComponent(componentMatch[3])) {
                const name = componentMatch[3];
                const range = new vscode.Range(i, 0, i, line.length);
                const nodeId = this.generateNodeId(document.fileName, name, 'reactComponent');
                
                symbols.push({
                    name,
                    kind: 'reactComponent',
                    range,
                    nodeId
                });
            }
            
            // Detect class declarations
            const classMatch = trimmedLine.match(/^(export\s+)?class\s+(\w+)/);
            if (classMatch) {
                const name = classMatch[2];
                const range = new vscode.Range(i, 0, i, line.length);
                const nodeId = this.generateNodeId(document.fileName, name, 'class');
                
                symbols.push({
                    name,
                    kind: 'class',
                    range,
                    nodeId
                });
            }
            
            // Detect interface declarations
            const interfaceMatch = trimmedLine.match(/^(export\s+)?interface\s+(\w+)/);
            if (interfaceMatch) {
                const name = interfaceMatch[2];
                const range = new vscode.Range(i, 0, i, line.length);
                const nodeId = this.generateNodeId(document.fileName, name, 'interface');
                
                symbols.push({
                    name,
                    kind: 'interface',
                    range,
                    nodeId
                });
            }
        }
        
        return symbols;
    }

    private isReactComponent(name: string): boolean {
        // Simple heuristic: PascalCase names are likely React components
        return /^[A-Z][a-zA-Z0-9]*$/.test(name);
    }

    private generateNodeId(fileName: string, name: string, kind: string): string {
        // Extract file path relative to workspace
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(fileName));
        if (workspaceFolder) {
            const relativePath = vscode.workspace.asRelativePath(fileName);
            const pathParts = relativePath.split('/');
            const module = pathParts[pathParts.length - 1].replace(/\.(ts|tsx|js|jsx)$/, '');
            return `${module}:${name}`;
        }
        return `${name}`;
    }

    private createGutterContent(symbol: CodeSymbol): string {
        return `[SPEC] [BLUEPRINT] [TIMELINE]`;
    }

    private createHoverMessage(symbol: CodeSymbol): vscode.MarkdownString {
        const message = new vscode.MarkdownString();
        message.appendMarkdown(`**${symbol.name}** (${symbol.kind})\n\n`);
        message.appendMarkdown(`Node ID: \`${symbol.nodeId}\`\n\n`);
        message.appendMarkdown(`Click on [SPEC], [BLUEPRINT], or [TIMELINE] to view details.`);
        return message;
    }
}
