import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class AIMOSLogger {
    private static outputChannel: vscode.OutputChannel;
    private static logFile: string;
    private static startTime: number = Date.now();
    private static workspaceLogPath: string | null = null;

    static initialize(context: vscode.ExtensionContext) {
        // Create output channel for VS Code
        this.outputChannel = vscode.window.createOutputChannel('AIM-OS Extension', { log: true });
        
        // Create log file
        const logsDir = path.join(context.extensionPath, 'logs');
        if (!fs.existsSync(logsDir)) {
            fs.mkdirSync(logsDir, { recursive: true });
        }
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        this.logFile = path.join(logsDir, `aimos-${timestamp}.log`);
        
        // ALSO write to workspace file so AI can read it automatically
        this.writeToWorkspaceFile(context);
        
        this.log('SYSTEM', '🚀 AIM-OS Extension Logger Initialized');
        this.log('SYSTEM', `Extension Path: ${context.extensionPath}`);
        this.log('SYSTEM', `Log File: ${this.logFile}`);
        this.log('SYSTEM', `VS Code Version: ${vscode.version}`);
        
        // Show output channel immediately
        this.outputChannel.show(true);
    }

    private static writeToWorkspaceFile(context: vscode.ExtensionContext) {
        try {
            // Try to find workspace root
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (workspaceFolder) {
                this.workspaceLogPath = path.join(workspaceFolder.uri.fsPath, 'cursor-addon', 'docs', 'LATEST_LOGS.md');
                const workspaceLogDir = path.dirname(this.workspaceLogPath);
                
                if (!fs.existsSync(workspaceLogDir)) {
                    fs.mkdirSync(workspaceLogDir, { recursive: true });
                }
                
                // Write initial header
                const header = `# Latest Extension Logs (Auto-Generated)

**Last Updated:** ${new Date().toISOString()}
**Extension Path:** ${context.extensionPath}

> **Note:** This file is automatically updated with extension logs. AI assistants can read this file directly!

---

## Log Entries

`;
                fs.writeFileSync(this.workspaceLogPath, header, 'utf8');
            }
        } catch (error) {
            // Silently fail - workspace file is optional
            console.error('Failed to create workspace log file:', error);
        }
    }

    static log(category: string, message: string, data?: any) {
        const timestamp = new Date().toISOString();
        const elapsed = ((Date.now() - this.startTime) / 1000).toFixed(3);
        
        // Format message
        const prefix = `[${elapsed}s] [${category}]`;
        const fullMessage = `${prefix} ${message}`;
        
        // Log to output channel
        this.outputChannel.appendLine(fullMessage);
        if (data) {
            this.outputChannel.appendLine(`  DATA: ${JSON.stringify(data, null, 2)}`);
        }
        
        // Log to file
        if (this.logFile) {
            const logEntry = `${timestamp} ${fullMessage}\n`;
            fs.appendFileSync(this.logFile, logEntry);
            if (data) {
                fs.appendFileSync(this.logFile, `  DATA: ${JSON.stringify(data, null, 2)}\n`);
            }
        }
        
        // ALSO append to workspace file so AI can read it
        this.appendToWorkspaceFile(fullMessage, data);
        
        // Also log to console for debugging
        console.log(fullMessage, data || '');
    }

    private static appendToWorkspaceFile(message: string, data?: any) {
        try {
            if (this.workspaceLogPath && fs.existsSync(this.workspaceLogPath)) {
                const logEntry = `${message}\n`;
                fs.appendFileSync(this.workspaceLogPath, logEntry, 'utf8');
                if (data) {
                    fs.appendFileSync(this.workspaceLogPath, `  DATA: ${JSON.stringify(data, null, 2)}\n`, 'utf8');
                }
                
                // Update last updated timestamp in header (every 10 logs to avoid too much I/O)
                if (Math.random() < 0.1) {
                    const content = fs.readFileSync(this.workspaceLogPath, 'utf8');
                    const updated = content.replace(
                        /\*\*Last Updated:\*\* .*/,
                        `**Last Updated:** ${new Date().toISOString()}`
                    );
                    fs.writeFileSync(this.workspaceLogPath, updated, 'utf8');
                }
            }
        } catch (error) {
            // Silently fail - workspace file is optional
        }
    }

    static error(category: string, message: string, error: any) {
        const errorDetails = {
            message: error?.message || String(error),
            stack: error?.stack,
            name: error?.name
        };
        
        this.log(`${category}:ERROR`, `❌ ${message}`, errorDetails);
        
        // Also show error message to user
        vscode.window.showErrorMessage(`AIM-OS: ${message}`);
    }

    static success(category: string, message: string, data?: any) {
        this.log(`${category}:SUCCESS`, `✅ ${message}`, data);
    }

    static warn(category: string, message: string, data?: any) {
        this.log(`${category}:WARN`, `⚠️ ${message}`, data);
    }

    static debug(category: string, message: string, data?: any) {
        this.log(`${category}:DEBUG`, `🔍 ${message}`, data);
    }

    static getLogFile(): string {
        return this.logFile;
    }

    static showOutput() {
        this.outputChannel.show();
    }
}
