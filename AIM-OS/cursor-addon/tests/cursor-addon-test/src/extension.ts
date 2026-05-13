import * as vscode from 'vscode';

export class TestPanelProvider implements vscode.WebviewViewProvider {
    private static _view?: vscode.WebviewView;

    constructor(private readonly _context: vscode.ExtensionContext) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        console.log('═══════════════════════════════════════════');
        console.log('🎯 TEST PANEL resolveWebviewView CALLED!!!');
        console.log('═══════════════════════════════════════════');

        TestPanelProvider._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: []
        };

        webviewView.webview.html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TEST PANEL</title>
    <style>
        body {
            background: #1e1e1e;
            color: #51cf66;
            font-family: sans-serif;
            padding: 20px;
        }
        h1 { color: #51cf66; font-size: 24px; }
        p { color: white; }
    </style>
</head>
<body>
    <h1>✅ TEST PANEL WORKS!</h1>
    <p>If you see this, webview is working!</p>
    <p>This is a COMPLETELY SEPARATE extension.</p>
</body>
</html>`;

        console.log('✅ HTML set successfully');
    }

    public static reveal() {
        if (TestPanelProvider._view) {
            TestPanelProvider._view.show(true);
        }
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('TEST EXTENSION ACTIVATED');
    
    const provider = new TestPanelProvider(context);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('testPanel', provider)
    );
    
    console.log('✅ Test panel provider registered');
}

export function deactivate() {}
