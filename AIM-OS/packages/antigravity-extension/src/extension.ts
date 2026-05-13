import * as vscode from 'vscode';
import { ConsoleViewProvider } from './providers/consoleView';

let pollInterval: NodeJS.Timeout | undefined;

export function activate(context: vscode.ExtensionContext): void {
    const provider = new ConsoleViewProvider(context.extensionUri, context);

    // Register the webview view provider
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('antigravity.consoleView', provider, {
            webviewOptions: { retainContextWhenHidden: true }
        })
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('antigravity.refresh', () => provider.refresh()),
        vscode.commands.registerCommand('antigravity.sendMessage', () => provider.promptSendMessage()),
        vscode.commands.registerCommand('antigravity.storeMemory', () => provider.promptStoreMemory()),
        vscode.commands.registerCommand('antigravity.checkGhost', () => provider.checkGhost())
    );

    // Start periodic polling
    const config = vscode.workspace.getConfiguration('antigravity');
    const intervalSec = config.get<number>('pollIntervalSeconds', 30);
    pollInterval = setInterval(() => provider.refresh(), intervalSec * 1000);
    context.subscriptions.push({ dispose: () => { if (pollInterval) { clearInterval(pollInterval); } } });

    console.log('[Antigravity] Console extension activated');
}

export function deactivate(): void {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    console.log('[Antigravity] Console extension deactivated');
}
