/**
 * Cursor API Client for Electron App
 * Communicates with Cursor extension via HTTP API to execute VS Code commands
 */

export interface CursorCommandRequest {
    command: string;
    args?: any[];
}

export interface CursorCommandResponse {
    success: boolean;
    command?: string;
    result?: any;
    error?: string;
}

export class CursorAPI {
    private baseUrl: string;
    private isAvailable: boolean = false;

    constructor(baseUrl: string = 'http://localhost:5001') {
        this.baseUrl = baseUrl;
        // Don't check availability in constructor - do it lazily when needed
        // this.checkAvailability();
    }

    /**
     * Check if command server is available
     */
    async checkAvailability(): Promise<boolean> {
        try {
            // Try to ping the server
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(1000)
            });
            this.isAvailable = response.ok;
            return this.isAvailable;
        } catch (error) {
            this.isAvailable = false;
            return false;
        }
    }

    /**
     * Execute a VS Code command via the extension
     */
    async executeCommand(command: string, ...args: any[]): Promise<CursorCommandResponse> {
        if (!this.isAvailable) {
            const available = await this.checkAvailability();
            if (!available) {
                return {
                    success: false,
                    error: 'Command server not available. Is the extension running?'
                };
            }
        }

        try {
            const response = await fetch(`${this.baseUrl}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command,
                    args
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result: CursorCommandResponse = await response.json();
            return result;
        } catch (error: any) {
            return {
                success: false,
                error: error.message || 'Failed to execute command'
            };
        }
    }

    /**
     * Execute VS Code command (convenience method)
     */
    async cmd(command: string, ...args: any[]): Promise<any> {
        const response = await this.executeCommand(command, ...args);
        if (!response.success) {
            throw new Error(response.error || 'Command failed');
        }
        return response.result;
    }

    // ========================================
    // Cursor Automation Convenience Methods
    // ========================================

    /**
     * Show dashboard (focus on AIM-OS view)
     */
    async showDashboard(): Promise<boolean> {
        const response = await this.executeCommand('aimos.showDashboard');
        return response.success;
    }

    /**
     * Store memory from selected text
     */
    async storeMemory(content: string, tags: string[]): Promise<boolean> {
        // Note: This would need to be implemented in extension
        // For now, we'll use the existing command structure
        const response = await this.executeCommand('aimos.storeMemory', content, tags);
        return response.success;
    }

    /**
     * Retrieve memory by query
     */
    async retrieveMemory(query: string): Promise<any> {
        const response = await this.executeCommand('aimos.retrieveMemory', query);
        return response.result;
    }

    /**
     * Create execution plan
     */
    async createPlan(goal: string): Promise<any> {
        const response = await this.executeCommand('aimos.createPlan', goal);
        return response.result;
    }

    /**
     * Track confidence for a task
     */
    async trackConfidence(task: string, confidence: number): Promise<boolean> {
        const response = await this.executeCommand('aimos.trackConfidence', task, confidence);
        return response.success;
    }

    /**
     * Get workspace files
     */
    async getWorkspaceFiles(): Promise<string[]> {
        // This would need a custom command in extension
        // For now, placeholder
        return [];
    }

    /**
     * Open file in editor
     */
    async openFile(filePath: string): Promise<boolean> {
        // This would need a custom command in extension
        // For now, placeholder
        return false;
    }

    /**
     * Send message to Cursor chat programmatically
     * Uses macro automation to simulate keyboard input
     */
    async sendChatMessage(message: string, waitForResponse?: boolean): Promise<boolean> {
        if (!this.isAvailable) {
            const available = await this.checkAvailability();
            if (!available) {
                throw new Error('Command server not available. Is the extension running?');
            }
        }

        try {
            const response = await fetch(`${this.baseUrl}/cursor/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message, waitForResponse })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result.success === true;
        } catch (error: any) {
            throw new Error(`Failed to send chat message: ${error.message}`);
        }
    }

    /**
     * Get active editor content
     */
    async getActiveEditorContent(): Promise<string | null> {
        // This would need a custom command in extension
        // For now, placeholder
        return null;
    }
}

// Singleton instance
let cursorApiInstance: CursorAPI | null = null;

export function getCursorAPI(): CursorAPI {
    if (!cursorApiInstance) {
        cursorApiInstance = new CursorAPI();
    }
    return cursorApiInstance;
}

