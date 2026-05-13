import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function registerShowLogsCommand(context: vscode.ExtensionContext) {
    const showLogsCommand = vscode.commands.registerCommand('aimos.showLogs', async () => {
        console.log('🔵 SHOW LOGS COMMAND CALLED');
        vscode.window.showInformationMessage('Show Logs command executed!').catch(err => console.error('Show message failed:', err));
        
        try {
            const logsDir = path.join(context.extensionPath, 'logs');
            console.log('🔵 Logs directory:', logsDir);
            
            if (!fs.existsSync(logsDir)) {
                vscode.window.showWarningMessage('No logs found yet. Try reloading the window after extension activation.');
                return;
            }

            // Get all log files
            const logFiles = fs.readdirSync(logsDir)
                .filter(f => f.endsWith('.log'))
                .sort((a, b) => b.localeCompare(a)); // Most recent first

            if (logFiles.length === 0) {
                vscode.window.showWarningMessage('No log files found.');
                return;
            }

            // Show quick pick to select log file
            const selected = await vscode.window.showQuickPick(logFiles, {
                placeHolder: 'Select a log file to view',
                title: 'AIM-OS Extension Logs'
            });

            if (selected) {
                const logPath = path.join(logsDir, selected);
                const logContent = fs.readFileSync(logPath, 'utf-8');
                
                // Create a new document with the log content
                const doc = await vscode.workspace.openTextDocument({
                    content: logContent,
                    language: 'log'
                });
                
                await vscode.window.showTextDocument(doc, {
                    viewColumn: vscode.ViewColumn.Beside,
                    preserveFocus: false
                });
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to show logs: ${error}`);
        }
    });

    context.subscriptions.push(showLogsCommand);
}
