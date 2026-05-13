import * as vscode from 'vscode';
import { ConsoleProvider } from './consoleProvider';
import { DaemonClient } from './daemonClient';
import { FileHooks } from './fileHooks';
import { TimelineLogger } from './timelineLogger';

export function activate(context: vscode.ExtensionContext) {
    console.log('Lucid Core Console extension is now active!');

    // Initialize timeline logger
    const timelineLogger = new TimelineLogger();
    
    // Initialize daemon client
    const daemonClient = new DaemonClient(timelineLogger);
    
    // Initialize file hooks for mutation control
    const fileHooks = new FileHooks(daemonClient, timelineLogger);
    
    // Register console provider
    const consoleProvider = new ConsoleProvider(context.extensionUri, daemonClient, timelineLogger);
    vscode.window.registerWebviewViewProvider('lucidCoreConsoleView', consoleProvider);
    
    // Register file mutation hooks
    fileHooks.registerHooks();
    
    // Register commands
    const voiceInputCommand = vscode.commands.registerCommand('lucidCore.voiceInput', () => {
        consoleProvider.startVoiceInput();
    });
    
    const phonePairingCommand = vscode.commands.registerCommand('lucidCore.phonePairing', () => {
        consoleProvider.startPhonePairing();
    });
    
    const forceEditCommand = vscode.commands.registerCommand('lucidCore.forceEdit', () => {
        consoleProvider.forceEdit();
    });
    
    const approveChangeCommand = vscode.commands.registerCommand('lucidCore.approveChange', () => {
        consoleProvider.approveChange();
    });
    
    // Add to subscriptions
    context.subscriptions.push(
        voiceInputCommand,
        phonePairingCommand,
        forceEditCommand,
        approveChangeCommand,
        daemonClient,
        fileHooks
    );
    
    // Log activation
    timelineLogger.log('extension_activated', {
        timestamp: Date.now(),
        version: context.extension.packageJSON.version
    });
}

export function deactivate() {
    console.log('Lucid Core Console extension is now deactivated');
}
