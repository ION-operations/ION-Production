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
 * SIMPLEST POSSIBLE PANEL
 * Based on VS Code's official examples
 * Completely separate from AIMOS
 */
function activate(context) {
    console.log('Simple Panel Test extension activated');
    const disposable = vscode.commands.registerCommand('simplePanel.open', () => {
        const panel = vscode.window.createWebviewPanel('simplePanel', 'Simple Panel Test', vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true
        });
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
function deactivate() { }
//# sourceMappingURL=extension.js.map