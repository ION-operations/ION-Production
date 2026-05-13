import * as vscode from 'vscode';
import { LucidOrchestratorProvider } from './lucidOrchestratorProvider';
import { DaemonClient } from './daemonClient';
import { SpecFoldProvider } from './folds/specFoldProvider';
import { BlueprintFoldProvider } from './folds/blueprintFoldProvider';
import { TimelineFoldProvider } from './folds/timelineFoldProvider';
import { ChangeProposalProvider } from './changeProposalProvider';

let daemonClient: DaemonClient;
let specFoldProvider: SpecFoldProvider;
let blueprintFoldProvider: BlueprintFoldProvider;
let timelineFoldProvider: TimelineFoldProvider;
let changeProposalProvider: ChangeProposalProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('Lucid Orchestrator extension is now active!');

    // Initialize daemon client
    const config = vscode.workspace.getConfiguration('lucid');
    const daemonUrl = config.get<string>('daemonUrl', 'ws://localhost:8765');
    
    daemonClient = new DaemonClient(daemonUrl);
    
    // Initialize fold providers
    specFoldProvider = new SpecFoldProvider(daemonClient);
    blueprintFoldProvider = new BlueprintFoldProvider(daemonClient);
    timelineFoldProvider = new TimelineFoldProvider(daemonClient);
    changeProposalProvider = new ChangeProposalProvider(daemonClient);

    // Register commands
    const showSpecCommand = vscode.commands.registerCommand('lucid.showSpec', async (nodeId: string) => {
        await specFoldProvider.showSpec(nodeId);
    });

    const showBlueprintCommand = vscode.commands.registerCommand('lucid.showBlueprint', async (nodeId: string) => {
        await blueprintFoldProvider.showBlueprint(nodeId);
    });

    const showTimelineCommand = vscode.commands.registerCommand('lucid.showTimeline', async (nodeId: string) => {
        await timelineFoldProvider.showTimeline(nodeId);
    });

    const proposeChangeCommand = vscode.commands.registerCommand('lucid.proposeChange', async (nodeId: string) => {
        await changeProposalProvider.showProposal(nodeId);
    });

    // Register gutter decorations
    const gutterProvider = new LucidOrchestratorProvider();
    const gutterDecorationType = vscode.window.createTextEditorDecorationType({
        gutterIconPath: context.asAbsolutePath('resources/gutter-icon.svg'),
        gutterIconSize: 'contain'
    });

    // Register text editor change handler
    const onDidChangeActiveTextEditor = vscode.window.onDidChangeActiveTextEditor(async (editor) => {
        if (editor) {
            await updateGutterDecorations(editor, gutterProvider, gutterDecorationType);
        }
    });

    // Register document change handler
    const onDidChangeTextDocument = vscode.workspace.onDidChangeTextDocument(async (event) => {
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document === event.document) {
            await updateGutterDecorations(editor, gutterProvider, gutterDecorationType);
        }
    });

    // Add to subscriptions
    context.subscriptions.push(
        showSpecCommand,
        showBlueprintCommand,
        showTimelineCommand,
        proposeChangeCommand,
        gutterDecorationType,
        onDidChangeActiveTextEditor,
        onDidChangeTextDocument
    );

    // Initialize with current editor
    if (vscode.window.activeTextEditor) {
        updateGutterDecorations(vscode.window.activeTextEditor, gutterProvider, gutterDecorationType);
    }
}

async function updateGutterDecorations(
    editor: vscode.TextEditor,
    gutterProvider: LucidOrchestratorProvider,
    decorationType: vscode.TextEditorDecorationType
) {
    const decorations = await gutterProvider.provideDecorations(editor.document);
    editor.setDecorations(decorationType, decorations);
}

export function deactivate() {
    if (daemonClient) {
        daemonClient.disconnect();
    }
}
