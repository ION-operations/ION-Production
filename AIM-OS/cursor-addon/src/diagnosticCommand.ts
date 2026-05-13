import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { AIMOSLogger } from './utils/logger';

export function registerDiagnosticCommand(context: vscode.ExtensionContext) {
    const diagnosticCommand = vscode.commands.registerCommand('aimos.runFullDiagnostic', async () => {
        console.log('🔵 RUN FULL DIAGNOSTIC COMMAND CALLED');
        console.log('🔵 TESTING DIRECT OUTPUT CHANNEL');
        vscode.window.showInformationMessage('Run Full Diagnostic command executed!').catch(err => console.error('Show message failed:', err));
        
        // Create direct output channel for testing
        try {
            const testChannel = vscode.window.createOutputChannel('AIM-OS Diagnostic Test');
            testChannel.show();
            
            // Test write immediately
            testChannel.appendLine('=== DIRECT OUTPUT CHANNEL TEST ===');
            testChannel.appendLine(`Time: ${new Date().toISOString()}`);
            testChannel.appendLine('If you see this, output channels work!');
            testChannel.appendLine('TEST LINE 1');
            testChannel.appendLine('TEST LINE 2');
            testChannel.appendLine('TEST LINE 3');
            
            // Force flush/show
            testChannel.show(true); // true = preserve focus
            vscode.window.showInformationMessage('Test channel written - check Output panel!');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create test channel: ${error}`);
        }
        
        AIMOSLogger.log('DIAGNOSTIC', '═══════════════════════════════════════════');
        AIMOSLogger.log('DIAGNOSTIC', '🔍 FULL DIAGNOSTIC STARTED');
        AIMOSLogger.log('DIAGNOSTIC', '═══════════════════════════════════════════');
        
        // Check 1: Extension Info
        AIMOSLogger.log('DIAGNOSTIC', '📦 Extension Information:');
        AIMOSLogger.log('DIAGNOSTIC', `  Extension ID: ${context.extension.id}`);
        AIMOSLogger.log('DIAGNOSTIC', `  Extension path: ${context.extensionPath}`);
        AIMOSLogger.log('DIAGNOSTIC', `  Active: ${context.extension.isActive}`);
        AIMOSLogger.log('DIAGNOSTIC', `  Subscriptions: ${context.subscriptions.length}`);
        
        // Check 2: Workspace Info
        AIMOSLogger.log('DIAGNOSTIC', '📁 Workspace Information:');
        AIMOSLogger.log('DIAGNOSTIC', `  Workspace folders: ${vscode.workspace.workspaceFolders?.length || 0}`);
        if (vscode.workspace.workspaceFolders) {
            vscode.workspace.workspaceFolders.forEach((folder, i) => {
                AIMOSLogger.log('DIAGNOSTIC', `    Folder ${i + 1}: ${folder.uri.fsPath}`);
            });
        }
        
        // Check 3: View Containers
        AIMOSLogger.log('DIAGNOSTIC', '🎨 Checking View Containers:');
        try {
            // Try to get all views
            const allCommands = await vscode.commands.getCommands();
            const viewCommands = allCommands.filter(cmd => 
                cmd.includes('aimos') || cmd.includes('lucid')
            );
            AIMOSLogger.log('DIAGNOSTIC', `  AIM-OS related commands: ${viewCommands.length}`);
            viewCommands.forEach(cmd => {
                AIMOSLogger.log('DIAGNOSTIC', `    - ${cmd}`);
            });
        } catch (error) {
            AIMOSLogger.error('DIAGNOSTIC', 'Failed to get commands', error);
        }
        
        // Check 4: Files in Extension
        AIMOSLogger.log('DIAGNOSTIC', '📂 Checking Extension Files:');
        const distPath = path.join(context.extensionPath, 'dist');
        const outPath = path.join(context.extensionPath, 'out');
        
        AIMOSLogger.log('DIAGNOSTIC', `  dist/ exists: ${fs.existsSync(distPath)}`);
        AIMOSLogger.log('DIAGNOSTIC', `  out/ exists: ${fs.existsSync(outPath)}`);
        
        if (fs.existsSync(distPath)) {
            const distFiles = fs.readdirSync(distPath);
            AIMOSLogger.log('DIAGNOSTIC', `  dist/ contents (${distFiles.length} items):`);
            distFiles.forEach(file => {
                const filePath = path.join(distPath, file);
                const stats = fs.statSync(filePath);
                const type = stats.isDirectory() ? 'DIR' : 'FILE';
                const size = stats.isDirectory() ? '-' : `${(stats.size / 1024).toFixed(1)}KB`;
                AIMOSLogger.log('DIAGNOSTIC', `    [${type}] ${file} (${size})`);
            });
            
            // Check assets
            const assetsPath = path.join(distPath, 'assets');
            if (fs.existsSync(assetsPath)) {
                const assetFiles = fs.readdirSync(assetsPath);
                AIMOSLogger.log('DIAGNOSTIC', `  dist/assets/ contents (${assetFiles.length} items):`);
                assetFiles.forEach(file => {
                    const filePath = path.join(assetsPath, file);
                    const stats = fs.statSync(filePath);
                    const size = `${(stats.size / 1024).toFixed(1)}KB`;
                    AIMOSLogger.log('DIAGNOSTIC', `    ${file} (${size})`);
                });
            }
        }
        
        // Check 5: Try to Focus Views
        AIMOSLogger.log('DIAGNOSTIC', '🎯 Attempting to focus views:');
        
        try {
            await vscode.commands.executeCommand('aimos.focus');
            AIMOSLogger.log('DIAGNOSTIC', '  ✅ Focused aimos container');
        } catch (error) {
            AIMOSLogger.log('DIAGNOSTIC', `  ❌ Failed to focus aimos: ${error}`);
        }
        
        try {
            await vscode.commands.executeCommand('lucidOrchestratorDashboard.focus');
            AIMOSLogger.log('DIAGNOSTIC', '  ✅ Focused lucidOrchestratorDashboard view');
        } catch (error) {
            AIMOSLogger.log('DIAGNOSTIC', `  ❌ Failed to focus dashboard view: ${error}`);
        }
        
        // Check 6: Read package.json to verify configuration
        AIMOSLogger.log('DIAGNOSTIC', '📋 Package.json Configuration:');
        try {
            const packagePath = path.join(context.extensionPath, 'package.json');
            if (!fs.existsSync(packagePath)) {
                AIMOSLogger.log('DIAGNOSTIC', `  ❌ package.json not found at: ${packagePath}`);
                throw new Error(`package.json not found at: ${packagePath}`);
            }
            const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf-8'));
            
            AIMOSLogger.log('DIAGNOSTIC', `  Activation Events: ${JSON.stringify(packageJson.activationEvents)}`);
            AIMOSLogger.log('DIAGNOSTIC', `  Views defined: ${Object.keys(packageJson.contributes?.views || {}).join(', ')}`);
            AIMOSLogger.log('DIAGNOSTIC', `  View containers: ${Object.keys(packageJson.contributes?.viewsContainers || {}).join(', ')}`);
            
            // Check each view
            for (const [container, views] of Object.entries(packageJson.contributes?.views || {})) {
                AIMOSLogger.log('DIAGNOSTIC', `  Container "${container}":`);
                (views as any[]).forEach((view: any) => {
                    AIMOSLogger.log('DIAGNOSTIC', `    View ID: "${view.id}"`);
                    AIMOSLogger.log('DIAGNOSTIC', `      Name: "${view.name}"`);
                    AIMOSLogger.log('DIAGNOSTIC', `      When: ${view.when || 'ALWAYS'}`);
                });
            }
        } catch (error) {
            AIMOSLogger.error('DIAGNOSTIC', 'Failed to read package.json', error);
        }
        
        // Show summary message
        vscode.window.showInformationMessage(
            'Full diagnostic complete! Check Output panel (AIM-OS Extension)',
            'Show Output'
        ).then(selection => {
            if (selection === 'Show Output') {
                AIMOSLogger.showOutput();
            }
        });
        
        AIMOSLogger.log('DIAGNOSTIC', '═══════════════════════════════════════════');
        AIMOSLogger.log('DIAGNOSTIC', '✅ FULL DIAGNOSTIC COMPLETE');
        AIMOSLogger.log('DIAGNOSTIC', '═══════════════════════════════════════════');
    });

    context.subscriptions.push(diagnosticCommand);
}
