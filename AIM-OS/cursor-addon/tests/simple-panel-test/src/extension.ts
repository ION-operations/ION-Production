import * as vscode from 'vscode';

/**
 * SIMPLEST POSSIBLE PANEL
 * Based on VS Code's official examples
 * Completely separate from AIMOS
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Simple Panel Test extension activated');

    const disposable = vscode.commands.registerCommand('simplePanel.open', () => {
        const panel = vscode.window.createWebviewPanel(
            'simplePanel',
            'Simple Panel Test',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 40px;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
        }
        h1 {
            color: var(--vscode-textLink-foreground);
            border: 3px solid var(--vscode-textLink-foreground);
            padding: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>✅ SIMPLE PANEL WORKS!</h1>
    <p>Time: ${new Date().toLocaleString()}</p>
    <script>
        console.log('Panel loaded!');
        document.body.style.border = '5px solid var(--vscode-textLink-foreground)';
    </script>
</body>
</html>`;

        vscode.window.showInformationMessage('Simple panel opened!');
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
