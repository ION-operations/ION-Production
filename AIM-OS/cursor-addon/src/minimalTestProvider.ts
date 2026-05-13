import * as vscode from 'vscode';

/**
 * MINIMAL TEST PROVIDER
 * 
 * This is a SIMPLE test to verify webview mechanism works.
 * If this shows "HELLO WORLD" - webview works, issue is with React/asset loading
 * If this is blank - webview mechanism itself is broken
 */
export class MinimalTestProvider implements vscode.WebviewViewProvider {
    private static _view?: vscode.WebviewView;

    constructor(private readonly _context: vscode.ExtensionContext) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        MinimalTestProvider._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.file(this._context.extensionPath)]
        };

        // ABSOLUTELY MINIMAL HTML - no external dependencies
        webviewView.webview.html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src ${webviewView.webview.cspSource} 'unsafe-inline' 'unsafe-eval'; script-src ${webviewView.webview.cspSource} 'unsafe-inline' 'unsafe-eval'; style-src ${webviewView.webview.cspSource} 'unsafe-inline';">
    <title>Minimal Test</title>
    <style>
        body {
            background: #1e1e1e;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            margin: 0;
        }
        h1 { color: #4ec9b0; }
        .success { color: #51cf66; }
        .error { color: #ff6b6b; }
        pre { background: #2d2d2d; padding: 10px; border-radius: 4px; overflow: auto; }
    </style>
</head>
<body>
    <h1>🎯 MINIMAL WEBVIEW TEST</h1>
    <p class="success">✅ If you see this, webview HTML loading works!</p>
    
    <h2>Test Results:</h2>
    <div id="results"></div>
    
    <script>
        const results = document.getElementById('results');
        const tests = [];
        
        // Test 1: DOM loaded
        tests.push({ name: 'DOM loaded', passed: true });
        
        // Test 2: Scripts execute
        tests.push({ name: 'Scripts execute', passed: true });
        
        // Test 3: Check for root element
        const rootExists = document.querySelector('#root') !== null;
        tests.push({ name: 'Root element exists', passed: rootExists });
        
        // Display results
        tests.forEach(test => {
            const div = document.createElement('div');
            div.innerHTML = test.passed 
                ? '<span class="success">✅</span> ' + test.name
                : '<span class="error">❌</span> ' + test.name;
            results.appendChild(div);
        });
        
        // Log to console
        console.log('[MINIMAL TEST] Webview loaded successfully');
        console.log('[MINIMAL TEST] Tests:', tests);
        
        // Send message to extension
        const vscode = acquireVsCodeApi();
        vscode.postMessage({ command: 'testComplete', results: tests });
    </script>
</body>
</html>`;
    }

    public static reveal() {
        if (MinimalTestProvider._view) {
            MinimalTestProvider._view.show(true);
        }
    }
}

