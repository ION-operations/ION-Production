import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface TimelineEntry {
    id: string;
    type: string;
    data: any;
    timestamp: number;
    sessionId: string;
}

export class TimelineLogger {
    private _sessionId: string;
    private _logFile: string;
    private _entries: TimelineEntry[] = [];
    private _maxEntries: number = 1000;

    constructor() {
        this._sessionId = this._generateSessionId();
        this._logFile = this._getLogFilePath();
        this._initializeLogFile();
    }

    private _generateSessionId(): string {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    private _getLogFilePath(): string {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            return path.join(workspaceFolder.uri.fsPath, '.lucid', 'timeline.json');
        } else {
            // Fallback to user's home directory
            const homeDir = require('os').homedir();
            return path.join(homeDir, '.lucid', 'timeline.json');
        }
    }

    private _initializeLogFile() {
        const logDir = path.dirname(this._logFile);
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }

        if (!fs.existsSync(this._logFile)) {
            fs.writeFileSync(this._logFile, JSON.stringify([], null, 2));
        } else {
            // Load existing entries
            try {
                const data = fs.readFileSync(this._logFile, 'utf8');
                this._entries = JSON.parse(data);
            } catch (error) {
                console.error('Failed to load timeline log:', error);
                this._entries = [];
            }
        }
    }

    public log(type: string, data: any): void {
        const entry: TimelineEntry = {
            id: this._generateEntryId(),
            type: type,
            data: data,
            timestamp: Date.now(),
            sessionId: this._sessionId
        };

        this._entries.push(entry);

        // Keep only the last maxEntries
        if (this._entries.length > this._maxEntries) {
            this._entries = this._entries.slice(-this._maxEntries);
        }

        // Write to file asynchronously
        this._writeToFile();

        // Also log to VS Code output channel
        this._logToOutputChannel(entry);
    }

    private _generateEntryId(): string {
        return `entry_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    private _writeToFile() {
        try {
            fs.writeFileSync(this._logFile, JSON.stringify(this._entries, null, 2));
        } catch (error) {
            console.error('Failed to write timeline log:', error);
        }
    }

    private _logToOutputChannel(entry: TimelineEntry) {
        const outputChannel = vscode.window.createOutputChannel('Lucid Core Console Timeline');
        const timestamp = new Date(entry.timestamp).toISOString();
        const message = `[${timestamp}] ${entry.type}: ${JSON.stringify(entry.data)}`;
        outputChannel.appendLine(message);
    }

    public getEntries(type?: string): TimelineEntry[] {
        if (type) {
            return this._entries.filter(entry => entry.type === type);
        }
        return [...this._entries];
    }

    public getSessionEntries(): TimelineEntry[] {
        return this._entries.filter(entry => entry.sessionId === this._sessionId);
    }

    public getRecentEntries(count: number = 10): TimelineEntry[] {
        return this._entries.slice(-count);
    }

    public clear(): void {
        this._entries = [];
        this._writeToFile();
    }

    public exportToFile(filePath: string): void {
        try {
            fs.writeFileSync(filePath, JSON.stringify(this._entries, null, 2));
        } catch (error) {
            console.error('Failed to export timeline log:', error);
        }
    }

    public getStats(): { totalEntries: number; sessionEntries: number; types: { [key: string]: number } } {
        const types: { [key: string]: number } = {};
        this._entries.forEach(entry => {
            types[entry.type] = (types[entry.type] || 0) + 1;
        });

        return {
            totalEntries: this._entries.length,
            sessionEntries: this.getSessionEntries().length,
            types: types
        };
    }
}
