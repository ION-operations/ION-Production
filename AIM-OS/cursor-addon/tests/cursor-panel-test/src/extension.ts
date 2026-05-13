import * as vscode from 'vscode';

/**
 * SIMPLEST POSSIBLE PANEL TEST
 * Uses createWebviewPanel (editor panel) - NOT WebviewViewProvider
 * Based on VS Code's official examples
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Cursor Panel Test extension activated');

    const disposable = vscode.commands.registerCommand('panelTest.open', () => {
        // Create panel in editor area (NOT sidebar)
        const panel = vscode.window.createWebviewPanel(
            'panelTest',              // Panel ID
            'Panel Test',              // Panel title
            vscode.ViewColumn.One,     // Show in editor area
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        // Simplest possible HTML
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
    <h1>✅ PANEL WORKS!</h1>
    <p>Time: ${new Date().toLocaleString()}</p>
    <p>If you see this, createWebviewPanel works in Cursor.</p>
    <script>
        console.log('Panel script loaded');
        document.body.style.border = '5px solid var(--vscode-textLink-foreground)';
    </script>
</body>
</html>`;

        vscode.window.showInformationMessage('Panel opened!');
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
