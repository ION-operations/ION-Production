import * as vscode from 'vscode';
import { AIMOSLogger } from './utils/logger';

export function registerForceOpenCommand(context: vscode.ExtensionContext) {
    const forceOpenDashboard = vscode.commands.registerCommand('aimos.forceOpenDashboard', async () => {
        AIMOSLogger.log('FORCE_OPEN', '🚀 Force opening dashboard...');
        
        try {
            // Method 1: Execute workbench command to show the view
            await vscode.commands.executeCommand('workbench.view.extension.aimos');
            AIMOSLogger.log('FORCE_OPEN', '✅ Executed workbench.view.extension.aimos');
        } catch (error) {
            AIMOSLogger.error('FORCE_OPEN', 'Method 1 failed', error);
        }
        
        try {
            // Method 2: Focus the specific view
            await vscode.commands.executeCommand('lucidOrchestratorDashboard.focus');
            AIMOSLogger.log('FORCE_OPEN', '✅ Executed lucidOrchestratorDashboard.focus');
        } catch (error) {
            AIMOSLogger.error('FORCE_OPEN', 'Method 2 failed', error);
        }
        
        try {
            // Method 3: Toggle visibility
            await vscode.commands.executeCommand('lucidOrchestratorDashboard.toggleVisibility');
            AIMOSLogger.log('FORCE_OPEN', '✅ Toggled visibility');
        } catch (error) {
            AIMOSLogger.error('FORCE_OPEN', 'Method 3 failed', error);
        }
        
        // Check if resolveWebviewView was called
        setTimeout(() => {
            AIMOSLogger.log('FORCE_OPEN', '⏰ Checking if resolveWebviewView was triggered...');
            AIMOSLogger.log('FORCE_OPEN', 'Look above for: "🎯 resolveWebviewView TRIGGERED!!!"');
        }, 1000);
    });

    context.subscriptions.push(forceOpenDashboard);
    
    const forceOpenTest = vscode.commands.registerCommand('aimos.forceOpenTest', async () => {
        AIMOSLogger.log('FORCE_OPEN', '🧪 Force opening test panel...');
        
        try {
            await vscode.commands.executeCommand('workbench.view.extension.aimosDevTools');
            AIMOSLogger.log('FORCE_OPEN', '✅ Opened DevTools container');
        } catch (error) {
            AIMOSLogger.error('FORCE_OPEN', 'Failed to open DevTools', error);
        }
        
        try {
            await vscode.commands.executeCommand('simpleTestPanel.focus');
            AIMOSLogger.log('FORCE_OPEN', '✅ Focused test panel');
        } catch (error) {
            AIMOSLogger.error('FORCE_OPEN', 'Failed to focus test panel', error);
        }
    });

    context.subscriptions.push(forceOpenTest);
}
