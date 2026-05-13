"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
/**
 * MINIMAL PANEL - Based on VS Code's official webview panel example
 * This is the SIMPLEST possible panel that should work
 */
function activate(context) {
    console.log('AIMOS Simple Panel extension activated');
    // Register command to open panel
    const disposable = vscode.commands.registerCommand('aimosSimple.openPanel', () => {
        // Create panel - using VS Code's standard pattern
        const panel = vscode.window.createWebviewPanel('aimosSimplePanel', // Panel ID
        'AIMOS Simple Panel', // Panel title
        vscode.ViewColumn.One, // Show in editor area
        {
            enableScripts: true, // Allow JavaScript
            retainContextWhenHidden: true
        });
        // Set HTML - SIMPLEST possible
        panel.webview.html = getWebviewContent();
        // Handle panel disposal
        panel.onDidDispose(() => {
            console.log('Panel disposed');
        }, null, context.subscriptions);
    });
    context.subscriptions.push(disposable);
}
/**
 * Get webview HTML content
 * SIMPLEST possible HTML - no dependencies, no external files
 */
function getWebviewContent() {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIMOS Simple Panel</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
        }
        h1 {
            color: var(--vscode-textLink-foreground);
            border-bottom: 2px solid var(--vscode-textLink-foreground);
            padding-bottom: 10px;
        }
        .success {
            color: var(--vscode-textLink-foreground);
            font-weight: bold;
            font-size: 18px;
            margin: 20px 0;
            padding: 15px;
            background-color: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textLink-foreground);
        }
        .info {
            margin: 15px 0;
            padding: 10px;
            background-color: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
        }
    </style>
</head>
<body>
    <h1>AIMOS Simple Panel</h1>
    
    <div class="success">
        ✅ PANEL IS WORKING!
    </div>
    
    <div class="info">
        <p><strong>If you see this, the panel works!</strong></p>
        <p>Time: ${new Date().toLocaleString()}</p>
        <p>This is the simplest possible panel structure.</p>
    </div>
    
    <div class="info">
        <h3>Next Steps:</h3>
        <ul>
            <li>✅ Panel opens</li>
            <li>✅ HTML renders</li>
            <li>✅ CSS works</li>
            <li>⏭️ Add chat functionality</li>
        </ul>
    </div>

    <script>
        console.log('Simple panel script loaded');
        
        // Test: Change background color to verify JavaScript works
        setTimeout(() => {
            document.body.style.border = '3px solid var(--vscode-textLink-foreground)';
            console.log('Border added - JavaScript is working!');
        }, 500);
    </script>
</body>
</html>`;
}
function deactivate() {
    console.log('AIMOS Simple Panel extension deactivated');
}
//# sourceMappingURL=extension.js.map