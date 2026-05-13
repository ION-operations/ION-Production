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
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const crossModelManager_1 = require("./crossModel/crossModelManager");
const memoryManager_1 = require("./memory/memoryManager");
const modelSelector_1 = require("./models/modelSelector");
const webviewProvider_1 = require("./webviewProvider");
const lucidDashboardProvider_1 = require("./lucidDashboardProvider");
const pureHtmlDashboardProvider_1 = require("./pureHtmlDashboardProvider");
const logger_1 = require("./utils/logger");
const showLogs_1 = require("./commands/showLogs");
const diagnosticCommand_1 = require("./diagnosticCommand");
const forceOpenView_1 = require("./forceOpenView");
function activate(context) {
    // Initialize logger FIRST
    logger_1.AIMOSLogger.initialize(context);
    logger_1.AIMOSLogger.log('ACTIVATION', '🚀 AIM-OS Extension activation started');
    logger_1.AIMOSLogger.log('ACTIVATION', `Extension path: ${context.extensionPath}`);
    logger_1.AIMOSLogger.log('ACTIVATION', `VS Code version: ${vscode.version}`);
    logger_1.AIMOSLogger.log('ACTIVATION', `Workspace folders: ${vscode.workspace.workspaceFolders?.length || 0}`);
    // Initialize managers
    logger_1.AIMOSLogger.log('ACTIVATION', 'Initializing managers...');
    const crossModelManager = new crossModelManager_1.CrossModelManager();
    const memoryManager = new memoryManager_1.MemoryManager();
    const modelSelector = new modelSelector_1.ModelSelector();
    // Initialize webview provider
    logger_1.AIMOSLogger.log('WEBVIEW', 'Initializing webview provider...');
    webviewProvider_1.AIMOSWebviewProvider.initialize(context);
    // Initialize Pure HTML Dashboard (ISOLATED VERSION - NO REACT, NO ASSETS)
    logger_1.AIMOSLogger.log('PURE_HTML', 'Creating pure HTML dashboard provider (isolated version)...');
    const pureHtmlDashboardProvider = new pureHtmlDashboardProvider_1.PureHtmlDashboardProvider(context);
    // Initialize Lucid Orchestrator Dashboard (React version)
    logger_1.AIMOSLogger.log('DASHBOARD', 'Creating dashboard provider...');
    const lucidDashboardProvider = new lucidDashboardProvider_1.LucidOrchestratorDashboardProvider(context);
    // Register PURE HTML dashboard in RIGHT SIDEBAR (activitybar) - ISOLATED TEST VERSION
    // This completely isolates webview mechanism from React/asset loading issues
    try {
        logger_1.AIMOSLogger.log('PURE_HTML', 'Registering PURE HTML dashboard for RIGHT SIDEBAR (aimosDashboard)...');
        logger_1.AIMOSLogger.log('PURE_HTML', `View ID to register: 'aimosDashboard'`);
        logger_1.AIMOSLogger.log('PURE_HTML', `Provider instance: ${pureHtmlDashboardProvider ? 'Created' : 'NULL'}`);
        const disposablePureHtml = vscode.window.registerWebviewViewProvider('aimosDashboard', pureHtmlDashboardProvider);
        context.subscriptions.push(disposablePureHtml);
        logger_1.AIMOSLogger.success('PURE_HTML', 'Pure HTML Dashboard provider registered for RIGHT SIDEBAR!');
        logger_1.AIMOSLogger.log('PURE_HTML', 'This is an ISOLATED version - no React, no external assets, pure HTML/CSS/JS');
        logger_1.AIMOSLogger.log('PURE_HTML', 'If this works, webview mechanism is functional. If blank, webview is broken.');
        // Also register React version for fallback (commented out for now)
        // Uncomment to switch back to React version:
        /*
        AIMOSLogger.log('DASHBOARD', 'Registering React dashboard for RIGHT SIDEBAR (aimosDashboard)...');
        const disposable = vscode.window.registerWebviewViewProvider('aimosDashboard', lucidDashboardProvider);
        context.subscriptions.push(disposable);
        AIMOSLogger.success('DASHBOARD', 'Dashboard provider registered for RIGHT SIDEBAR!');
        */
        // Verify registration
        logger_1.AIMOSLogger.log('PURE_HTML', `Subscriptions count: ${context.subscriptions.length}`);
    }
    catch (error) {
        logger_1.AIMOSLogger.error('PURE_HTML', 'Failed to register pure HTML dashboard', error);
        vscode.window.showErrorMessage(`Failed to register Pure HTML Dashboard: ${error}`);
    }
    // Register Minimal Test Provider for debugging in BOTTOM PANEL
    // This is a SIMPLE test to isolate webview vs React issues
    try {
        logger_1.AIMOSLogger.log('TEST', 'Registering MINIMAL test panel for BOTTOM PANEL...');
        const { MinimalTestProvider } = require('./minimalTestProvider');
        const minimalProvider = new MinimalTestProvider(context);
        context.subscriptions.push(vscode.window.registerWebviewViewProvider('simpleTestPanel', minimalProvider));
        logger_1.AIMOSLogger.success('TEST', 'Minimal test panel registered in BOTTOM PANEL (DevTools)');
    }
    catch (error) {
        logger_1.AIMOSLogger.error('TEST', 'Failed to register minimal test panel', error);
    }
    // Register diagnostic commands
    (0, showLogs_1.registerShowLogsCommand)(context);
    (0, diagnosticCommand_1.registerDiagnosticCommand)(context);
    (0, forceOpenView_1.registerForceOpenCommand)(context);
    logger_1.AIMOSLogger.success('COMMANDS', 'Registered diagnostic commands');
    // Logs are now automatically written to cursor-addon/docs/LATEST_LOGS.md
    // AI can read this file directly without manual steps!
    // Register commands - CONSOLIDATED & SIMPLIFIED
    const commands = [
        // PRIMARY: Show Dashboard (consolidates all dashboard commands)
        vscode.commands.registerCommand('aimos.showDashboard', async () => {
            logger_1.AIMOSLogger.log('COMMAND', 'showDashboard command triggered');
            // Try to focus the view
            try {
                await vscode.commands.executeCommand('aimos.focus');
                logger_1.AIMOSLogger.log('COMMAND', 'Focused on AIM-OS view container');
            }
            catch (e) {
                logger_1.AIMOSLogger.warn('COMMAND', 'Could not focus view container', e);
            }
            // Show the main Lucid Orchestrator Dashboard (side panel)
            if (lucidDashboardProvider) {
                lucidDashboardProvider_1.LucidOrchestratorDashboardProvider.reveal();
                logger_1.AIMOSLogger.log('COMMAND', 'Called reveal on dashboard provider');
            }
            else {
                logger_1.AIMOSLogger.error('COMMAND', 'Dashboard provider is null!', null);
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
                const panel = vscode.window.createWebviewPanel('aimosMemoryStats', 'AIM-OS Memory Statistics', vscode.ViewColumn.One, {
                    enableScripts: true,
                    retainContextWhenHidden: true
                });
                panel.webview.html = getMemoryStatsWebviewContent(stats);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to get memory stats: ${error}`);
            }
        }),
        vscode.commands.registerCommand('aimos.showModelSelector', async () => {
            try {
                const models = await modelSelector.getAvailableModels();
                const selectedModel = await vscode.window.showQuickPick(models.map(model => ({
                    label: model.name,
                    description: model.description,
                    detail: `Cost: ${model.cost}, Quality: ${model.quality}`,
                    model: model
                })), {
                    placeHolder: 'Select AI model for current task',
                    matchOnDescription: true,
                    matchOnDetail: true
                });
                if (selectedModel) {
                    await modelSelector.selectModel(selectedModel.model);
                    vscode.window.showInformationMessage(`Selected model: ${selectedModel.label}`);
                }
            }
            catch (error) {
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
                }
                catch (error) {
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
                    const panel = vscode.window.createWebviewPanel('aimosMemoryResults', 'Memory Search Results', vscode.ViewColumn.One, {
                        enableScripts: true,
                        retainContextWhenHidden: true
                    });
                    panel.webview.html = getMemoryResultsWebviewContent(memories);
                }
                catch (error) {
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
                    const panel = vscode.window.createWebviewPanel('aimosExecutionPlan', 'Execution Plan', vscode.ViewColumn.One, {
                        enableScripts: true,
                        retainContextWhenHidden: true
                    });
                    panel.webview.html = getExecutionPlanWebviewContent(plan);
                }
                catch (error) {
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
                        await crossModelManager.trackConfidence(task, parseFloat(confidence), 'User input via Cursor add-on');
                        vscode.window.showInformationMessage(`Confidence tracked for: ${task}`);
                    }
                    catch (error) {
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
            outputChannel.appendLine(`  Static view exists: ${lucidDashboardProvider_1.LucidOrchestratorDashboardProvider._view ? 'YES' : 'NO'}`);
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
                lucidDashboardProvider_1.LucidOrchestratorDashboardProvider.reveal();
                outputChannel.appendLine(`✅ Reveal command executed`);
            }
            catch (e) {
                outputChannel.appendLine(`❌ Reveal failed: ${e}`);
            }
            // Check dashboard output channel
            const dashboardOutput = lucidDashboardProvider_1.LucidOrchestratorDashboardProvider.getOutputChannel();
            dashboardOutput.show();
            dashboardOutput.appendLine(`\n=== FORCED DIAGNOSTIC CHECK ===`);
            dashboardOutput.appendLine(`If you see this, output channel works`);
            dashboardOutput.appendLine(`Check above for [AIM-OS] messages`);
            // Show alert
            vscode.window.showErrorMessage('Check Output panel: "AIM-OS Debug" and "AIM-OS Dashboard" channels', 'Open Debug Channel').then(selection => {
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
exports.activate = activate;
function getMemoryStatsWebviewContent(stats) {
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
function getMemoryResultsWebviewContent(memories) {
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
function getExecutionPlanWebviewContent(plan) {
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
function deactivate() {
    console.log('AIM-OS Cursor Add-on is now deactivated!');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map