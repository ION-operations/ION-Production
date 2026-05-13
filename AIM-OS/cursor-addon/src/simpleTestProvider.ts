import * as vscode from 'vscode';
import { AIMOSLogger } from './utils/logger';

export class SimpleTestProvider implements vscode.WebviewViewProvider {
    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        AIMOSLogger.log('TEST_RESOLVE', '═══════════════════════════════════════════');
        AIMOSLogger.log('TEST_RESOLVE', '🧪 TEST PANEL resolveWebviewView TRIGGERED!!!');
        AIMOSLogger.log('TEST_RESOLVE', '═══════════════════════════════════════════');
        AIMOSLogger.log('TEST_RESOLVE', `View ID: ${webviewView.viewId}`);
        
        // Set options FIRST (critical!)
        webviewView.webview.options = {
            enableScripts: true
        };

        // Then set the SIMPLEST possible HTML
        webviewView.webview.html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test</title>
    <style>
        body {
            background: #1e1e1e;
            color: white;
            font-family: sans-serif;
            padding: 20px;
        }
        h1 { color: #4ec9b0; }
        button { 
            padding: 10px 20px;
            background: #4ec9b0;
            color: black;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>✅ WEBVIEW IS WORKING!</h1>
    <p>If you can see this, the webview mechanism itself works.</p>
    <p>Current time: ${new Date().toLocaleTimeString()}</p>
    <button onclick="alert('Button clicked!')">Test JavaScript</button>
    <script>
        console.log('JavaScript is executing!');
        document.body.style.border = '2px solid #4ec9b0';
    </script>
</body>
</html>`;
    }
}
