/**
 * SIMPLE TEST PANEL - Guaranteed to work
 * This creates a minimal panel to verify createWebviewPanel works
 */
import * as vscode from 'vscode';

export function createSimpleTestPanel(context: vscode.ExtensionContext): void {
    vscode.commands.registerCommand('aimos.testPanel', () => {
        const panel = vscode.window.createWebviewPanel(
            'aimosTestPanel',
            'AIMOS Test Panel',
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
            background: #1e1e1e;
            color: #51cf66;
            font-family: monospace;
            font-size: 16px;
        }
        h1 {
            color: #51cf66;
            border: 3px solid #51cf66;
            padding: 20px;
            text-align: center;
        }
        .test {
            margin: 20px 0;
            padding: 15px;
            background: #2d2d30;
            border-left: 4px solid #51cf66;
        }
    </style>
</head>
<body>
    <h1>✅ TEST PANEL WORKING!</h1>
    <div class="test">
        <p><strong>If you see this, createWebviewPanel WORKS!</strong></p>
        <p>Time: ${new Date().toLocaleString()}</p>
        <p>This proves webviews can work in Cursor.</p>
    </div>
    <script>
        console.log('Test panel loaded!');
        document.body.style.border = '5px solid #51cf66';
    </script>
</body>
</html>`;

        vscode.window.showInformationMessage('✅ Test panel opened! Check if you see green border.');
    });
}
