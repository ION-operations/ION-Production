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
exports.TestPanelProvider = void 0;
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
class TestPanelProvider {
    constructor(_context) {
        this._context = _context;
    }
    resolveWebviewView(webviewView, _context, _token) {
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
    static reveal() {
        if (TestPanelProvider._view) {
            TestPanelProvider._view.show(true);
        }
    }
}
exports.TestPanelProvider = TestPanelProvider;
function activate(context) {
    console.log('TEST EXTENSION ACTIVATED');
    const provider = new TestPanelProvider(context);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider('testPanel', provider));
    console.log('✅ Test panel provider registered');
}
function deactivate() { }
//# sourceMappingURL=extension.js.map