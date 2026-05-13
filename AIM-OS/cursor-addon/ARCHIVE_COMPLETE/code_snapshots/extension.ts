import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { MCPClient } from './mcp/mcpClient';
import { CrossModelManager } from './crossModel/crossModelManager';
import { MemoryManager } from './memory/memoryManager';
import { ModelSelector } from './models/modelSelector';
import { AIMOSWebviewProvider } from './webviewProvider';
import { LucidOrchestratorDashboardProvider } from './lucidDashboardProvider';
import { PureHtmlDashboardProvider } from './pureHtmlDashboardProvider';
import { AIMOSLogger } from './utils/logger';
import { registerShowLogsCommand } from './commands/showLogs';
import { registerDiagnosticCommand } from './diagnosticCommand';
import { registerForceOpenCommand } from './forceOpenView';

export function activate(context: vscode.ExtensionContext) {
    // Initialize logger FIRST
    AIMOSLogger.initialize(context);
    
    AIMOSLogger.log('ACTIVATION', '🚀 AIM-OS Extension activation started');
    AIMOSLogger.log('ACTIVATION', `Extension path: ${context.extensionPath}`);
    AIMOSLogger.log('ACTIVATION', `VS Code version: ${vscode.version}`);
    AIMOSLogger.log('ACTIVATION', `Workspace folders: ${vscode.workspace.workspaceFolders?.length || 0}`);
    
    // Initialize managers
    AIMOSLogger.log('ACTIVATION', 'Initializing managers...');
    const crossModelManager = new CrossModelManager();
    const memoryManager = new MemoryManager();
    const modelSelector = new ModelSelector();

    // Initialize webview provider
    AIMOSLogger.log('WEBVIEW', 'Initializing webview provider...');
    AIMOSWebviewProvider.initialize(context);

    // Initialize Pure HTML Dashboard (ISOLATED VERSION - NO REACT, NO ASSETS)
    AIMOSLogger.log('PURE_HTML', 'Creating pure HTML dashboard provider (isolated version)...');
    const pureHtmlDashboardProvider = new PureHtmlDashboardProvider(context);
    
    // Initialize Lucid Orchestrator Dashboard (React version)
    AIMOSLogger.log('DASHBOARD', 'Creating dashboard provider...');
    const lucidDashboardProvider = new LucidOrchestratorDashboardProvider(context);
    
    // Register PURE HTML dashboard in RIGHT SIDEBAR (activitybar) - ISOLATED TEST VERSION
    // This completely isolates webview mechanism from React/asset loading issues
    try {
        AIMOSLogger.log('PURE_HTML', 'Registering PURE HTML dashboard for RIGHT SIDEBAR (aimosDashboard)...');
        AIMOSLogger.log('PURE_HTML', `View ID to register: 'aimosDashboard'`);
        AIMOSLogger.log('PURE_HTML', `Provider instance: ${pureHtmlDashboardProvider ? 'Created' : 'NULL'}`);
        
        const disposablePureHtml = vscode.window.registerWebviewViewProvider('aimosDashboard', pureHtmlDashboardProvider);
        context.subscriptions.push(disposablePureHtml);
        
        AIMOSLogger.success('PURE_HTML', 'Pure HTML Dashboard provider registered for RIGHT SIDEBAR!');
        AIMOSLogger.log('PURE_HTML', 'This is an ISOLATED version - no React, no external assets, pure HTML/CSS/JS');
        AIMOSLogger.log('PURE_HTML', 'If this works, webview mechanism is functional. If blank, webview is broken.');
        
        // Also register React version for fallback (commented out for now)
        // Uncomment to switch back to React version:
        /*
        AIMOSLogger.log('DASHBOARD', 'Registering React dashboard for RIGHT SIDEBAR (aimosDashboard)...');
        const disposable = vscode.window.registerWebviewViewProvider('aimosDashboard', lucidDashboardProvider);
        context.subscriptions.push(disposable);
        AIMOSLogger.success('DASHBOARD', 'Dashboard provider registered for RIGHT SIDEBAR!');
        */
        
        // Verify registration
        AIMOSLogger.log('PURE_HTML', `Subscriptions count: ${context.subscriptions.length}`);
    } catch (error) {
        AIMOSLogger.error('PURE_HTML', 'Failed to register pure HTML dashboard', error);
        vscode.window.showErrorMessage(`Failed to register Pure HTML Dashboard: ${error}`);
    }
    
    // Register Minimal Test Provider for debugging in BOTTOM PANEL
    // This is a SIMPLE test to isolate webview vs React issues
    try {
        AIMOSLogger.log('TEST', 'Registering MINIMAL test panel for BOTTOM PANEL...');
        const { MinimalTestProvider } = require('./minimalTestProvider');
        const minimalProvider = new MinimalTestProvider(context);
        context.subscriptions.push(
            vscode.window.registerWebviewViewProvider('simpleTestPanel', minimalProvider)
        );
        AIMOSLogger.success('TEST', 'Minimal test panel registered in BOTTOM PANEL (DevTools)');
    } catch (error) {
        AIMOSLogger.error('TEST', 'Failed to register minimal test panel', error);
    }

    // Register diagnostic commands
    registerShowLogsCommand(context);
    registerDiagnosticCommand(context);
    registerForceOpenCommand(context);
    AIMOSLogger.success('COMMANDS', 'Registered diagnostic commands');
    
    // Logs are now automatically written to cursor-addon/docs/LATEST_LOGS.md
    // AI can read this file directly without manual steps!

    // Register commands - CONSOLIDATED & SIMPLIFIED
    const commands = [
        // PRIMARY: Show Dashboard (consolidates all dashboard commands)
        vscode.commands.registerCommand('aimos.showDashboard', async () => {
            AIMOSLogger.log('COMMAND', 'showDashboard command triggered');
            
            // Try to focus the view
            try {
                await vscode.commands.executeCommand('aimos.focus');
                AIMOSLogger.log('COMMAND', 'Focused on AIM-OS view container');
            } catch (e) {
                AIMOSLogger.warn('COMMAND', 'Could not focus view container', e);
            }
            
            // Show the main Lucid Orchestrator Dashboard (side panel)
            if (lucidDashboardProvider) {
                LucidOrchestratorDashboardProvider.reveal();
                AIMOSLogger.log('COMMAND', 'Called reveal on dashboard provider');
            } else {
                AIMOSLogger.error('COMMAND', 'Dashboard provider is null!', null);
            }
        }),

        vscode.commands.registerCommand('aimos.toggleCrossModel', async () => {
            const isEnabled = crossModelManager.toggleCrossModel();
            const status = isEnabled ? 'enabled' : 'disabled';
            vscode.window.showInformationMessage(`Cross-Model Consciousness ${status}`);
        }),

        vscode.commands.registerCommand('aimos.showMemoryStats', async () => {
            try {
                const stats = await memoryManager.getMemoryStats();
                const panel = vscode.window.createWebviewPanel(
                    'aimosMemoryStats',
                    'AIM-OS Memory Statistics',
                    vscode.ViewColumn.One,
                    {
                        enableScripts: true,
                        retainContextWhenHidden: true
                    }
                );
                panel.webview.html = getMemoryStatsWebviewContent(stats);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to get memory stats: ${error}`);
            }
        }),

        vscode.commands.registerCommand('aimos.showModelSelector', async () => {
            try {
                const models = await modelSelector.getAvailableModels();
                const selectedModel = await vscode.window.showQuickPick(
                    models.map(model => ({
                        label: model.name,
                        description: model.description,
                        detail: `Cost: ${model.cost}, Quality: ${model.quality}`,
                        model: model
                    })),
                    {
                        placeHolder: 'Select AI model for current task',
                        matchOnDescription: true,
                        matchOnDetail: true
                    }
                );

                if (selectedModel) {
                    await modelSelector.selectModel(selectedModel.model);
                    vscode.window.showInformationMessage(`Selected model: ${selectedModel.label}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to select model: ${error}`);
            }
        }),

        vscode.commands.registerCommand('aimos.storeMemory', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            const text = editor.document.getText(selection);
            
            if (!text) {
                vscode.window.showWarningMessage('No text selected');
                return;
            }

            const tags = await vscode.window.showInputBox({
                prompt: 'Enter tags for this memory (comma-separated)',
                placeHolder: 'e.g., code, implementation, feature'
            });

            if (tags) {
                try {
                    await memoryManager.storeMemory(text, tags.split(',').map(t => t.trim()));
                    vscode.window.showInformationMessage('Memory stored successfully!');
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to store memory: ${error}`);
                }
            }
        }),

        vscode.commands.registerCommand('aimos.retrieveMemory', async () => {
            const query = await vscode.window.showInputBox({
                prompt: 'Enter search query for memory retrieval',
                placeHolder: 'e.g., authentication, database, API'
            });

            if (query) {
                try {
                    const memories = await memoryManager.retrieveMemory(query);
                    const panel = vscode.window.createWebviewPanel(
                        'aimosMemoryResults',
                        'Memory Search Results',
                        vscode.ViewColumn.One,
                        {
                            enableScripts: true,
                            retainContextWhenHidden: true
                        }
                    );
                    panel.webview.html = getMemoryResultsWebviewContent(memories);
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to retrieve memory: ${error}`);
                }
            }
        }),

        vscode.commands.registerCommand('aimos.createPlan', async () => {
            const goal = await vscode.window.showInputBox({
                prompt: 'Enter goal for execution plan',
                placeHolder: 'e.g., Implement user authentication system'
            });

            if (goal) {
                try {
                    const plan = await crossModelManager.createPlan(goal);
                    const panel = vscode.window.createWebviewPanel(
                        'aimosExecutionPlan',
                        'Execution Plan',
                        vscode.ViewColumn.One,
                        {
                            enableScripts: true,
                            retainContextWhenHidden: true
                        }
                    );
                    panel.webview.html = getExecutionPlanWebviewContent(plan);
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to create plan: ${error}`);
                }
            }
        }),

        vscode.commands.registerCommand('aimos.trackConfidence', async () => {
            const task = await vscode.window.showInputBox({
                prompt: 'Enter task name for confidence tracking',
                placeHolder: 'e.g., Authentication implementation'
            });

            if (task) {
                const confidence = await vscode.window.showInputBox({
                    prompt: 'Enter confidence level (0.0 - 1.0)',
                    placeHolder: '0.85'
                });

                if (confidence) {
                    try {
                        await crossModelManager.trackConfidence(
                            task,
                            parseFloat(confidence),
                            'User input via Cursor add-on'
                        );
                        vscode.window.showInformationMessage(`Confidence tracked for: ${task}`);
                    } catch (error) {
                        vscode.window.showErrorMessage(`Failed to track confidence: ${error}`);
                    }
                }
            }
        }),
        
        vscode.commands.registerCommand('aimos.debugDashboard', () => {
            // EMERGENCY DIAGNOSTIC - CHECK EVERYTHING
            const outputChannel = vscode.window.createOutputChannel('AIM-OS Debug');
            outputChannel.show();
            outputChannel.appendLine('=== EMERGENCY DIAGNOSTIC ===');
            outputChannel.appendLine(`Time: ${new Date().toISOString()}`);
            outputChannel.appendLine(`Extension Path: ${context.extensionPath}`);
            outputChannel.appendLine(`Extension Active: ${context.subscriptions.length > 0 ? 'YES' : 'NO'}`);
            
            // Check if provider exists
            outputChannel.appendLine(`\nProvider Status:`);
            outputChannel.appendLine(`  lucidDashboardProvider created: ${lucidDashboardProvider ? 'YES' : 'NO'}`);
            outputChannel.appendLine(`  Static view exists: ${LucidOrchestratorDashboardProvider._view ? 'YES' : 'NO'}`);
            
            // Check views
            outputChannel.appendLine(`\nRegistered Views:`);
            outputChannel.appendLine(`  lucidOrchestratorDashboard: Registered`);
            outputChannel.appendLine(`  aimosDashboard: Registered`);
            
            // Check files
            const distPath = path.join(context.extensionPath, 'dist');
            const htmlPath = path.join(distPath, 'index.html');
            const assetsPath = path.join(distPath, 'assets');
            
            outputChannel.appendLine(`\nFile Check:`);
            outputChannel.appendLine(`  dist/index.html: ${fs.existsSync(htmlPath) ? 'EXISTS' : 'MISSING'}`);
            outputChannel.appendLine(`  dist/assets: ${fs.existsSync(assetsPath) ? 'EXISTS' : 'MISSING'}`);
            
            if (fs.existsSync(htmlPath)) {
                const html = fs.readFileSync(htmlPath, 'utf8');
                outputChannel.appendLine(`  HTML size: ${html.length} chars`);
            }
            
            // Force reveal and check output
            outputChannel.appendLine(`\n=== ATTEMPTING TO REVEAL VIEW ===`);
            try {
                LucidOrchestratorDashboardProvider.reveal();
                outputChannel.appendLine(`✅ Reveal command executed`);
            } catch (e) {
                outputChannel.appendLine(`❌ Reveal failed: ${e}`);
            }
            
            // Check dashboard output channel
            const dashboardOutput = LucidOrchestratorDashboardProvider.getOutputChannel();
            dashboardOutput.show();
            dashboardOutput.appendLine(`\n=== FORCED DIAGNOSTIC CHECK ===`);
            dashboardOutput.appendLine(`If you see this, output channel works`);
            dashboardOutput.appendLine(`Check above for [AIM-OS] messages`);
            
            // Show alert
            vscode.window.showErrorMessage(
                'Check Output panel: "AIM-OS Debug" and "AIM-OS Dashboard" channels',
                'Open Debug Channel'
            ).then(selection => {
                if (selection === 'Open Debug Channel') {
                    outputChannel.show();
                }
            });
        })
    ];

    // Add commands to context
    context.subscriptions.push(...commands);

    // MCP connection handled by Cursor automatically via ~/.cursor/mcp.json
    // Don't auto-initialize MCP client - it's not needed for basic functionality
    // Users can configure MCP servers in Cursor settings
}

function getMemoryStatsWebviewContent(stats: any): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIM-OS Memory Statistics</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .stat-item { margin: 10px 0; padding: 10px; background: var(--vscode-editor-background); border-radius: 5px; }
            .stat-label { font-weight: bold; color: var(--vscode-foreground); }
            .stat-value { color: var(--vscode-textLink-foreground); }
        </style>
    </head>
    <body>
        <h1>AIM-OS Memory Statistics</h1>
        <div class="stat-item">
            <div class="stat-label">Total Atoms:</div>
            <div class="stat-value">${stats.total_atoms || 0}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Memory Usage:</div>
            <div class="stat-value">${stats.memory_usage || 'N/A'}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Last Updated:</div>
            <div class="stat-value">${new Date().toLocaleString()}</div>
        </div>
    </body>
    </html>
    `;
}

function getMemoryResultsWebviewContent(memories: any[]): string {
    const memoryItems = memories.map(memory => `
        <div class="memory-item">
            <h3>${memory.title || 'Memory Item'}</h3>
            <p>${memory.content}</p>
            <small>Tags: ${memory.tags ? memory.tags.join(', ') : 'None'}</small>
        </div>
    `).join('');

    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Memory Search Results</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .memory-item { margin: 15px 0; padding: 15px; background: var(--vscode-editor-background); border-radius: 5px; }
            .memory-item h3 { color: var(--vscode-foreground); margin-top: 0; }
            .memory-item p { color: var(--vscode-foreground); }
            .memory-item small { color: var(--vscode-descriptionForeground); }
        </style>
    </head>
    <body>
        <h1>Memory Search Results</h1>
        ${memoryItems || '<p>No memories found</p>'}
    </body>
    </html>
    `;
}

function getExecutionPlanWebviewContent(plan: any): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Execution Plan</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .plan-step { margin: 10px 0; padding: 10px; background: var(--vscode-editor-background); border-radius: 5px; }
            .plan-step h3 { color: var(--vscode-foreground); margin-top: 0; }
            .plan-step p { color: var(--vscode-foreground); }
        </style>
    </head>
    <body>
        <h1>Execution Plan</h1>
        <div class="plan-step">
            <h3>Goal:</h3>
            <p>${plan.goal || 'No goal specified'}</p>
        </div>
        <div class="plan-step">
            <h3>Steps:</h3>
            <p>${plan.steps ? plan.steps.join('<br>') : 'No steps available'}</p>
        </div>
        <div class="plan-step">
            <h3>Estimated Duration:</h3>
            <p>${plan.estimated_duration || 'N/A'}</p>
        </div>
    </body>
    </html>
    `;
}

export function deactivate() {
    console.log('AIM-OS Cursor Add-on is now deactivated!');
}
