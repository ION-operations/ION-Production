import * as vscode from 'vscode';
import { DaemonClient } from './daemonClient';
import { TimelineLogger } from './timelineLogger';

export interface FileMutationRequest {
    id: string;
    filePath: string;
    operation: 'create' | 'modify' | 'delete' | 'rename';
    description: string;
    confidence: number;
    blastRadius: string;
    requiresApproval: boolean;
    timestamp: number;
}

export class FileHooks {
    private _daemonClient: DaemonClient;
    private _timelineLogger: TimelineLogger;
    private _disposables: vscode.Disposable[] = [];
    private _pendingMutations: Map<string, FileMutationRequest> = new Map();

    constructor(daemonClient: DaemonClient, timelineLogger: TimelineLogger) {
        this._daemonClient = daemonClient;
        this._timelineLogger = timelineLogger;
    }

    public registerHooks() {
        // Hook into file system events
        this._disposables.push(
            vscode.workspace.onDidCreateFiles(this._onFileCreated.bind(this)),
            vscode.workspace.onDidDeleteFiles(this._onFileDeleted.bind(this)),
            vscode.workspace.onDidRenameFiles(this._onFileRenamed.bind(this)),
            vscode.workspace.onDidSaveTextDocument(this._onFileSaved.bind(this))
        );

        // Hook into editor events
        this._disposables.push(
            vscode.workspace.onDidChangeTextDocument(this._onTextChanged.bind(this))
        );

        this._timelineLogger.log('file_hooks_registered', {
            timestamp: Date.now()
        });
    }

    private _onFileCreated(event: vscode.FileCreateEvent) {
        event.files.forEach(file => {
            this._handleFileMutation({
                id: this._generateMutationId(),
                filePath: file.fsPath,
                operation: 'create',
                description: `File created: ${file.fsPath}`,
                confidence: 0.8, // Default confidence for file creation
                blastRadius: 'local',
                requiresApproval: this._requiresApproval('create', file.fsPath),
                timestamp: Date.now()
            });
        });
    }

    private _onFileDeleted(event: vscode.FileDeleteEvent) {
        event.files.forEach(file => {
            this._handleFileMutation({
                id: this._generateMutationId(),
                filePath: file.fsPath,
                operation: 'delete',
                description: `File deleted: ${file.fsPath}`,
                confidence: 0.9, // High confidence for deletion
                blastRadius: 'local',
                requiresApproval: this._requiresApproval('delete', file.fsPath),
                timestamp: Date.now()
            });
        });
    }

    private _onFileRenamed(event: vscode.FileRenameEvent) {
        event.files.forEach(file => {
            this._handleFileMutation({
                id: this._generateMutationId(),
                filePath: file.newUri.fsPath,
                operation: 'rename',
                description: `File renamed: ${file.oldUri.fsPath} → ${file.newUri.fsPath}`,
                confidence: 0.8,
                blastRadius: 'local',
                requiresApproval: this._requiresApproval('rename', file.newUri.fsPath),
                timestamp: Date.now()
            });
        });
    }

    private _onFileSaved(document: vscode.TextDocument) {
        this._handleFileMutation({
            id: this._generateMutationId(),
            filePath: document.uri.fsPath,
            operation: 'modify',
            description: `File saved: ${document.uri.fsPath}`,
            confidence: 0.7, // Medium confidence for modifications
            blastRadius: this._calculateBlastRadius(document.uri.fsPath),
            requiresApproval: this._requiresApproval('modify', document.uri.fsPath),
            timestamp: Date.now()
        });
    }

    private _onTextChanged(event: vscode.TextDocumentChangeEvent) {
        // Only track significant changes (not every keystroke)
        if (event.contentChanges.length > 0) {
            const change = event.contentChanges[0];
            if (change.text.length > 10 || change.rangeLength > 10) {
                this._handleFileMutation({
                    id: this._generateMutationId(),
                    filePath: event.document.uri.fsPath,
                    operation: 'modify',
                    description: `Text changed: ${event.document.uri.fsPath}`,
                    confidence: 0.6, // Lower confidence for text changes
                    blastRadius: this._calculateBlastRadius(event.document.uri.fsPath),
                    requiresApproval: this._requiresApproval('modify', event.document.uri.fsPath),
                    timestamp: Date.now()
                });
            }
        }
    }

    private _handleFileMutation(mutation: FileMutationRequest) {
        this._pendingMutations.set(mutation.id, mutation);

        this._timelineLogger.log('file_mutation_detected', {
            mutationId: mutation.id,
            filePath: mutation.filePath,
            operation: mutation.operation,
            confidence: mutation.confidence,
            blastRadius: mutation.blastRadius,
            requiresApproval: mutation.requiresApproval,
            timestamp: mutation.timestamp
        });

        // Send to daemon for processing
        this._daemonClient.onMessage({
            type: 'fileMutationRequest',
            change: mutation
        });

        // If approval is required, show notification
        if (mutation.requiresApproval) {
            this._showApprovalNotification(mutation);
        }
    }

    private _requiresApproval(operation: string, filePath: string): boolean {
        // Check if file is in a critical directory
        const criticalDirs = [
            'packages/',
            'knowledge_architecture/',
            'goals/',
            '.cursorrules'
        ];

        const isCriticalFile = criticalDirs.some(dir => filePath.includes(dir));
        
        // Check if operation is high-risk
        const highRiskOperations = ['delete', 'rename'];
        const isHighRisk = highRiskOperations.includes(operation);

        return isCriticalFile || isHighRisk;
    }

    private _calculateBlastRadius(filePath: string): string {
        // Calculate blast radius based on file location and type
        if (filePath.includes('packages/')) {
            return 'package';
        } else if (filePath.includes('knowledge_architecture/')) {
            return 'system';
        } else if (filePath.includes('goals/')) {
            return 'project';
        } else if (filePath.endsWith('.cursorrules')) {
            return 'global';
        } else {
            return 'local';
        }
    }

    private _showApprovalNotification(mutation: FileMutationRequest) {
        const message = `File mutation requires approval: ${mutation.description}`;
        const actions = ['Approve', 'Force Edit', 'Cancel'];
        
        vscode.window.showWarningMessage(message, ...actions).then(selection => {
            switch (selection) {
                case 'Approve':
                    this._approveMutation(mutation.id);
                    break;
                case 'Force Edit':
                    this._forceMutation(mutation.id);
                    break;
                case 'Cancel':
                    this._cancelMutation(mutation.id);
                    break;
            }
        });
    }

    private _approveMutation(mutationId: string) {
        const mutation = this._pendingMutations.get(mutationId);
        if (mutation) {
            this._daemonClient.approveChange(mutationId);
            this._pendingMutations.delete(mutationId);
            
            this._timelineLogger.log('mutation_approved', {
                mutationId: mutationId,
                timestamp: Date.now()
            });
        }
    }

    private _forceMutation(mutationId: string) {
        const mutation = this._pendingMutations.get(mutationId);
        if (mutation) {
            this._daemonClient.forceEdit(mutationId);
            this._pendingMutations.delete(mutationId);
            
            this._timelineLogger.log('mutation_forced', {
                mutationId: mutationId,
                timestamp: Date.now()
            });
        }
    }

    private _cancelMutation(mutationId: string) {
        const mutation = this._pendingMutations.get(mutationId);
        if (mutation) {
            this._pendingMutations.delete(mutationId);
            
            this._timelineLogger.log('mutation_cancelled', {
                mutationId: mutationId,
                timestamp: Date.now()
            });
        }
    }

    private _generateMutationId(): string {
        return `mutation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    public getPendingMutations(): FileMutationRequest[] {
        return Array.from(this._pendingMutations.values());
    }

    public dispose() {
        this._disposables.forEach(disposable => disposable.dispose());
        this._disposables = [];
        this._pendingMutations.clear();
    }
}
